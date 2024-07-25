from pynars.NAL.Functions import Stamp_merge, Budget_merge, Truth_deduction
from pynars.NAL.Inference.LocalRules import revision
from pynars.NARS import Reasoner
from pynars.NARS.DataStructures.MC import Utils
from pynars.NARS.DataStructures.MC.OutputBuffer import Reaction
from pynars.NARS.DataStructures.MC.Utils import PriorityQueue, BufferTask, satisfaction_level, preprocessing
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Compound, Judgement, Task, Interval, parser, Term, Truth, Copula, Statement
from typing import Iterable, List, Optional, Tuple


class Anticipation:

    matched: bool
    task: Task
    prediction: 'PredictiveImplication'

    def __init__(self, task: Task, prediction: 'PredictiveImplication') -> None:
        self.matched = False
        self.task = task
        self.prediction = prediction


class PredictiveImplication:

    condition: Term
    interval: Interval
    conclusion: Term
    to_memory_cooldown: int
    expiration: int
    task: Task

    def __init__(self, condition: Term, interval: Interval, conclusion: Term, task: Task) -> None:
        self.condition = condition
        """
        As explained the conceptual design, "+1, +2" cannot be used in buffers, thus the interval is only kept in the
        prediction. Which might cause a trouble, but you may use +1, +2 as terms if you want.
        I will let you know how to do it the referred function.
        """
        self.interval = interval
        self.conclusion = conclusion
        self.to_memory_cooldown = 0
        """
        The expiration of predictions are different from expirations in buffers. It is a non-negative integer.
        It means how many cycles this prediction has not been used.
        """
        self.expiration = 0
        self.task = task

    def get_conclusion(self, condition_task: 'BufferTask') -> Tuple[Optional[Interval], Optional[Task]]:
        # when "A" is matched with "A =/> B", return B with truth deduction
        truth = Truth_deduction(self.task.truth, condition_task.task.truth)
        if truth.c < 0.3:
            return None, None

        task = parser.parse(self.conclusion.word + ". " + str(truth))

        return self.interval, task


class Slot:
    """
    It contains 3 parts: 1) events observed, 2) anticipations made, 3) operations to do.
    """

    events: PriorityQueue[BufferTask]
    anticipations: List[Anticipation]
    num_anticipations: int
    operations: list # TODO: operation types
    num_operations: int

    def __init__(self, num_events: int, num_anticipations: int, num_operations: int) -> None:
        self.events = PriorityQueue(num_events)
        self.anticipations = []
        self.num_anticipations = num_anticipations
        self.operations = []
        self.num_operations = num_operations

    def push(self, item: BufferTask, value: float):
        self.events.push(item, value)

    def pop(self) -> Tuple[BufferTask, float]:
        return self.events.pop()

    def random_pop(self) -> Optional[BufferTask]:
        return self.events.random_pop()


class EventBuffer:

    num_events: int
    num_anticipations: int
    num_operations: int
    slots: List[Slot]
    curr: int
    predictive_implications: PriorityQueue[PredictiveImplication]
    reactions: PriorityQueue[Reaction]
    N: int

    def __init__(self, num_slot: int, num_events: int, num_anticipations: int, num_operations: int, num_predictive_implications: int, N=1) -> None:
        # num slot is the number of slots on one side. If num_slot is 2, there are 1 (in the middle) + 2*2=5 slots
        self.num_events = num_events
        self.num_anticipations = num_anticipations
        self.num_operations = num_operations
        self.slots = [Slot(num_events, num_anticipations, num_operations) for _ in range(1 + 2 * num_slot)]
        self.curr = num_slot
        self.predictive_implications = PriorityQueue(num_predictive_implications)
        self.reactions = PriorityQueue(num_predictive_implications * 5)
        self.N = N

    def push(self, tasks: Iterable[Task], memory: Memory) -> None:
        for task in tasks:
            buffer_task = BufferTask(task)
            buffer_task.preprocess_effect = Utils.preprocessing(task, memory)
            self.slots[self.curr].push(buffer_task, buffer_task.priority)

    def pop(self) -> List[Task]:
        ret = []
        for _ in range(self.N):
            if len(self.slots[self.curr].events) != 0:
                buffer_task, _ = self.slots[self.curr].pop()
                ret.append(buffer_task.task)
        return ret

    @staticmethod
    def contemporary_composition(events: List[Task]) -> Task:
        # according to the conceptual design, currently only 2-compounds are allowed,
        # though in the future, we may have compounds with many components,

        # term
        each_compound_term = [each.term for each in events]
        term = Compound.ParallelEvents(*each_compound_term)

        # truth, using the truth with the lowest expectation
        truth = events[0].truth
        for each in events[1:]:
            if each.truth.e < truth.e:
                truth = each.truth

        # stamp, using stamp-merge function
        stamp = events[0].stamp
        for each in events[1:]:
            stamp = Stamp_merge(stamp, each.stamp)

        # budget, using budget-merge function
        budget = events[0].budget
        for each in events[1:]:
            budget = Budget_merge(budget, each.budget)

        # sentence
        sentence = Judgement(term, stamp, truth) # ! Argument 1 to "Judgement" has incompatible type "Type[Compound]"; expected "Term" (Mypy arg-type)

        # task
        return Task(sentence, budget)

    @staticmethod
    def sequential_composition(event_1: Task, interval: Interval, event_2: Task) -> Task:
        # according to the conceptual design, we currently only have "event_1, interval, event_2" schema,
        # though in the future this may also change, but it is too early to decide here

        term = Compound.SequentialEvents(*[event_1.term, interval, event_2.term])
        # in some cases, the interval needs not to be displayer in Narsese
        # term = Compound.SequentialEvents(*[event_1.term, event_2.term])
        truth = event_2.truth
        # decrease the confidence of a compound based on the length of the interval
        # truth.c *= 1 / int(interval)
        # truth.c *= 0.7 + 0.3 * (0.9 - (0.9 / (self.curr * 5)) * int(interval))
        stamp = Stamp_merge(event_2.stamp, event_1.stamp)
        budget = Budget_merge(event_2.budget, event_1.budget)
        # sentence
        sentence = Judgement(term, stamp, truth)
        # task
        return Task(sentence, budget)

    @staticmethod
    def generate_prediction_util(event_1: Task, interval: Interval, event_2: Task) -> PredictiveImplication:
        if interval != 0:
            copula = Copula.PredictiveImplication  # =/>
        else:
            # currently, this is only allowed in the global buffer,
            # but only for events from different resources
            copula = Copula.ConcurrentImplication  # ==>
        """
        If you want to include "interval" as a term, you just need to change "term" on the next line.
        """
        term = Statement(event_1.term, copula, event_2.term)
        # truth, a default truth, with only one positive example
        truth = Truth(1, 0.9, 1)
        # stamp, using event_2's stamp
        stamp = event_2.stamp
        # budget, using budget-merge function
        budget = Budget_merge(event_1.budget, event_2.budget)
        # sentence
        sentence = Judgement(term, stamp, truth)
        # task
        task = Task(sentence, budget)
        # predictive implication
        return PredictiveImplication(event_1.term, interval, event_2.term, task)

    def compound_composition(self, memory: Memory) -> None:
        """
        After the initial composition, pick the one with the highest priority in the current slot.
        Compose it with all other events in the current slot and the previous max events.
        """
        if len(self.slots[self.curr].events) != 0:
            curr_max, _ = self.slots[self.curr].pop()
            curr_remaining = []
            curr_composition = []
            while len(self.slots[self.curr].events) != 0:
                curr_remaining.append(self.slots[self.curr].pop()[0])
                curr_remaining[-1].is_component = 1
                curr_max.is_component = 1
                curr_composition.append(self.contemporary_composition([curr_max.task, curr_remaining[-1].task]))

            previous_max: List[Optional[BufferTask]] = []
            previous_composition = []
            for i in range(self.curr):
                if len(self.slots[i].events) != 0:
                    tmp, _ = self.slots[i].pop()
                    previous_max.append(tmp)
                    # don't change previous max's "is_component"
                    curr_max.is_component = 1
                    previous_composition.append(self.sequential_composition(previous_max[-1].task, # ? should change this `previous_max[-1]` to `tmp` to assume the non-none type?
                                                                            Interval(self.curr - i), curr_max.task))
                else:
                    previous_max.append(None)

            # after get all compositions, put everything back
            for i in range(self.curr):
                if previous_max[i] is not None:
                    self.slots[i].push(previous_max[i], previous_max[i].priority)
            self.slots[self.curr].push(curr_max, curr_max.priority)
            for each in curr_remaining:
                self.slots[self.curr].push(each, each.priority)

            # add all compositions to the current slot
            self.push(curr_composition + previous_composition, memory)

    def check_anticipation(self, memory: Memory) -> None:
        """
        Check all anticipations, award or punish the corresponding predictive implications.
        If an anticipation does not even exist, apply the lowest satisfaction.
        """
        prediction_award_penalty: List[Tuple[PredictiveImplication, float]] = []
        checked_buffer_tasks = []
        while len(self.slots[self.curr].events) != 0:
            buffer_task, _ = self.slots[self.curr].pop()
            for each_anticipation in self.slots[self.curr].anticipations:
                # it is possible for an event satisfying multiple anticipations,
                # e.g., A, +1 =/> B, A =/> B
                if each_anticipation.task.term.word == buffer_task.task.term.word:
                    each_anticipation.matched = True
                    buffer_task.task = revision(each_anticipation.task, buffer_task.task)
                    satisfaction = 1 - satisfaction_level(each_anticipation.task.truth, buffer_task.task.truth)
                    prediction_award_penalty.append((each_anticipation.prediction, satisfaction))
            checked_buffer_tasks.append(buffer_task)

        # if there are some unmatched anticipations, apply the lowest satisfaction
        for each_anticipation in self.slots[self.curr].anticipations:
            if not each_anticipation.matched:
                prediction_award_penalty.append((each_anticipation.prediction, 0))

        print("prediction_award_penalty", prediction_award_penalty)

        # put all buffer tasks back, some evaluations may change
        for each_task in checked_buffer_tasks: # ! have to use different variable names to avoid type conflicts
            self.slots[self.curr].push(each_task, each_task.priority)

        # update the predictive implications
        for each in prediction_award_penalty:
            each[0].task = revision(each[0].task, parser.parse(each[0].task.term.word + ". %" + str(each[1]) + ";0.9%"))
            self.predictive_implications.edit(each[0], each[0].task.truth.e * preprocessing(each[0].task, memory),
                                              lambda x: x.task.term)

    def predictive_implication_application(self, memory: Memory) -> None:
        """
        Check all predictive implications, whether some of them can fire.
        If so, calculate the corresponding task of the conclusion and create it as an anticipation in the corresponding
        slot in the future.
        If some implications cannot fire, increase the expiration of them.
        """
        implications = []
        while len(self.predictive_implications) != 0:
            implication, _ = self.predictive_implications.pop()
            applied = False
            for each_event in self.slots[self.curr].events.pq:
                if implication.condition == each_event[1].task.term: # ! Unsupported operand types for == ("Term" and "Term") (Mypy operator)
                    interval, conclusion = implication.get_conclusion(each_event[1])
                    if interval is None or conclusion is None: # ! if the interval isn't `None`, same to the conclusion
                        break
                    applied = True
                    implication.expiration = max(0, implication.expiration - 1)
                    anticipation = Anticipation(conclusion, implication)
                    self.slots[self.curr + int(interval)].anticipations.append(anticipation)
                    implications.append(implication)
            if not applied:
                implication.expiration += 1
                implications.append(implication)

        for each in implications:
            self.predictive_implications.push(each, each.task.truth.e * preprocessing(each.task, memory) *
                                              (1 / (1 + each.expiration)))

    def to_memory_predictive_implication(self, memory: Memory, threshold_f: float=0.9, threshold_c: float=0.8, default_cooldown: int=100) -> List[Reaction]:
        # when a predictive implication reaches a relatively high truth value, it will be forwarded to the memory
        #   (not the next level)
        # this does not mean it is removed from the predictive implication pq

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        reactions = []
        # ==============================================================================================================

        for each in self.predictive_implications.pq:
            if each[1].task.truth.f >= threshold_f and each[1].task.truth.c >= threshold_c:
                if each[1].to_memory_cooldown <= 0:
                    memory.accept(each[1].task)
                    # print("accepted task", each[1].task.sentence)

                    # cheating
                    # since something is wrong the reasoner, such that it cannot generate sub-goals correctly,
                    # I have to cheat.
                    # ==================================================================================================

                    # ? for `each[1].task.term.predicate`, should assume the `each[1]`'s term is a statement?
                    if each[1].task.term.predicate.word == "<{SELF}-->[good]>":

                        if (each[1].task.term.subject.is_compound and each[1].task.term.subject.components[-1].word[0]
                                == "^"):
                            condition = None
                            operation = None

                            if each[1].task.term.subject.connector == "Connector.ParallelEvents":
                                condition = Compound.ParallelEvents(*each[1].task.term.subject.components[:-1])
                                operation = each[1].task.term.subject.components[-1]
                            elif each[1].task.term.subject.connector == "Connector.ParallelEvents":
                                condition = Compound.SequentialEvents(*each[1].task.term.subject.components[:-1])
                                operation = each[1].task.term.subject.components[-1]

                            if condition is not None and operation is not None:
                                reaction = Reaction(condition, operation, None)
                                reactions.append(reaction)

                    # ==================================================================================================

                    each[1].to_memory_cooldown = default_cooldown
                else:
                    each[1].to_memory_cooldown -= 1

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        return reactions
        # ==============================================================================================================

    def local_evaluation(self, memory: Memory, threshold_f: float=0.8, threshold_c: float=0.9, default_cooldown: int=100) -> List[Reaction]:
        self.check_anticipation(memory)
        self.predictive_implication_application(memory)
        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        reactions = self.to_memory_predictive_implication(memory, threshold_f, threshold_c, default_cooldown)
        return reactions
        # ==============================================================================================================
        # original
        # self.to_memory_predictive_implication(memory, threshold_f, threshold_c, default_cooldown)

    def memory_based_evaluation(self, memory: Memory) -> None:
        evaluated_buffer_tasks = []
        while len(self.slots[self.curr].events) != 0:
            buffer_task, _ = self.slots[self.curr].pop()
            buffer_task.preprocess_effect = preprocessing(buffer_task.task, memory)
            evaluated_buffer_tasks.append(buffer_task)
        # put all buffer tasks back
        for each in evaluated_buffer_tasks:
            self.slots[self.curr].push(each, each.priority)

    @staticmethod
    def prediction_revision(existed_prediction: PredictiveImplication, new_prediction: PredictiveImplication) -> PredictiveImplication:
        existed_prediction.task = revision(existed_prediction.task, new_prediction.task)
        existed_prediction.expiration = max(0, existed_prediction.expiration - 1)
        return existed_prediction

    def prediction_generation(self, max_events_per_slot: int, memory: Memory) -> None:
        """
        For each slot, randomly pop "max events per slot" buffer tasks to generate predictions.
        Currently, concurrent predictive implications (==>) are not supported.
        """
        # get all events needed for prediction generation
        selected_buffer_tasks = []
        for i in range(self.curr + 1):
            tmp = []
            for _ in range(max_events_per_slot):
                tmp.append(self.slots[i].random_pop())
            selected_buffer_tasks.append(tmp)

        for i, each_selected_buffer_tasks in enumerate(selected_buffer_tasks):
            print("selected_buffer_tasks", i,
                  [each_event.task if each_event is not None else "None" for each_event in each_selected_buffer_tasks])
        print("===")

        # generate predictions based on intervals (=/>)
        for i in range(self.curr):
            for each_curr_event in selected_buffer_tasks[-1]:
                for each_previous_event in selected_buffer_tasks[i]:
                    if each_curr_event is not None and each_previous_event is not None:
                        tmp2 = self.generate_prediction_util(each_previous_event.task, Interval(self.curr - i), # ! for type stability, it may need to be renamed to `tmp2`
                                                            each_curr_event.task)
                        # if tmp2.task.truth.e * preprocessing(tmp2.task, memory) <= 0.05:
                        #     continue
                        existed = None
                        for j in range(len(self.predictive_implications)):
                            if self.predictive_implications.pq[j][1].task.term == tmp2.task.term:
                                existed = self.predictive_implications.pq.pop(j)
                                break
                        if existed is not None:
                            tmp2 = self.prediction_revision(existed[1], tmp2)

                        self.predictive_implications.push(tmp2, tmp2.task.truth.e * preprocessing(tmp2.task, memory))

        # after the prediction generation, put the randomly selected buffer tasks back
        for i in range(self.curr + 1):
            for each in selected_buffer_tasks[i]:
                if each is not None:
                    self.slots[i].push(each, each.priority)

    def slots_cycle(self) -> None:
        self.slots = self.slots[1:] + [Slot(self.num_events, self.num_anticipations, self.num_operations)]

    def buffer_cycle(self, tasks: Iterable[Task], memory: Memory,
                     max_events_per_slot: int=5, threshold_f: float=0.8, threshold_c: float=0.9,
                     default_cooldown: int=10) -> Tuple[List[Reaction], List[Task]]:
        # put all tasks to the current slot
        self.push(tasks, memory)
        self.compound_composition(memory)
        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        reactions = self.local_evaluation(memory, threshold_f, threshold_c, default_cooldown)
        # ==============================================================================================================
        # original
        # self.local_evaluation(memory, threshold_f, threshold_c, default_cooldown)
        # ==============================================================================================================
        self.memory_based_evaluation(memory)
        self.prediction_generation(max_events_per_slot, memory)
        ret = self.pop()
        self.slots_cycle()
        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        return reactions, ret
        # ==============================================================================================================
        # original
        # return ret
