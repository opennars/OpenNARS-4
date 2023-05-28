import copy
import math

from pynars.NAL.Functions import Stamp_merge, Budget_merge, Truth_induction, Truth_deduction, Budget_forward, \
    Budget_decay
from pynars.NAL.Inference.LocalRules import revision
from pynars.NARS.DataStructures._py.Anticipation import Anticipation
from pynars.NARS.DataStructures._py.Slot import Slot
from pynars.Narsese import Compound, Task, Judgement, Interval, Statement, Copula, Goal, Term, Connector


def predictions_p_value(p: Task):
    """
    the priority value of predictions (predictive implications)

    In some cases, the priority value used for sorting might be different from the priority value (budget.priority)
    of these tasks.

    Here this value is effected by 1) its own priority, and 2) its frequency. Since we don't want some "negative
    predictions", e.g. "B will NOT follow A".
    """
    return p.budget.priority * p.truth.f


def short_term_memory_sorting_policy(t: Task):
    return t.budget.priority


class Buffer:
    """
    The class for all (input) buffers, say event buffer, internal buffer and global buffer.
    For THIS buffer, it will not have the temporal compounding capability, and it is ASSUMED that there are NO multiple
    inputs (each time there will be only one input event), so there are no spatial compounding capability as well.
    """

    def __init__(self, num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory):

        # parameters
        self.num_slot = num_slot * 2 + 1  # symmetric
        self.present = num_slot
        self.num_anticipation = num_anticipation
        self.num_operation = num_operation
        self.num_prediction = num_prediction
        self.num_goal = num_goal
        self.num_short_term_memory = 2 * self.num_prediction

        # data structures
        self.memory = memory

        self.predictions = []  # a list of lists, e.g., [prediction.word, prediction, prediction's priority value]
        # sorted from large to small
        self.goals = {}
        self.slots = [Slot(1, num_anticipation, num_operation) for _ in range(self.num_slot)]
        self.short_term_memory = []

    def update_prediction(self, p: Task):
        """
        Duplicate predictions will be revised.

        Predictions will be sorted in descending order, by insertion sort.
        """
        word = p.term.word

        words = [each[0] for each in self.predictions]
        if word in words:
            idx = words.index(word)
            # revision
            self.predictions[idx][1] = revision(self.predictions[idx][1], p)
            self.predictions[idx][2] = predictions_p_value(self.predictions[idx][1])
        else:
            priority = predictions_p_value(p)
            added = False
            for i in range(len(self.predictions)):
                if priority > self.predictions[i][2]:
                    self.predictions = self.predictions[:i] + [[word, p, priority]] + self.predictions[i:]
                    added = True
                    break
            if not added:
                self.predictions += [[word, p, priority]]

        if len(self.predictions) > self.num_prediction:
            self.predictions = self.predictions[:self.num_prediction]

    def update_goal(self, g: Goal):
        """
        Duplicate goals will be ignored.

        If self.goals is already overwhelmed, no following goals will be input.
        """
        word = g.term.word
        if word not in self.goals and len(self.goals) < self.num_goal:
            self.goals.update({word: g})

    def update_short_term_memory(self, tasks):
        """
        short-term memory is s place remembering "recent events (including compounds)".

        Copied from Slot.working_space, but the durability will be changed. The shorter the term, the less the
        durability it has. Currently, a linear function 2 / (1 + exp(-0.2 * (complexity - 1))) - 1 is used.

        This is used to check whether recently some terms are paid attention. If not, they will have a "great" priority
        punishment.

        In each buffer cycle, the short-term memory will decay automatically.
        """

        # decay
        for each in self.short_term_memory:
            each.budget = Budget_decay(each.budget)

        # update
        for each in tasks:
            added = False

            tmp_task = copy.deepcopy(tasks[each].t)
            tmp_task.budget.durability = 2 / (1 + math.exp(- 0.2 * (tmp_task.term.complexity - 0.9))) - 1

            for i in range(len(self.short_term_memory)):
                # revision
                if hash(tasks[each].t.term) == hash(self.short_term_memory[i].term):
                    self.short_term_memory[i] = revision(tmp_task, self.short_term_memory[i])
                    added = True
                    break
            if not added:
                self.short_term_memory.append(tmp_task)

        # sorting
        self.short_term_memory.sort(key=short_term_memory_sorting_policy, reverse=True)

        # overflow handling
        if len(self.short_term_memory) > self.num_short_term_memory:
            self.short_term_memory = self.short_term_memory[:self.num_short_term_memory]

    def in_short_term_memory(self, t: Task):
        t = hash(t.term)
        for i in range(len(self.short_term_memory)):
            if t == hash(self.short_term_memory[i].term):
                return i
        return -1

    def input_filtering(self):
        """
        It is possible that there are multiple inputs (more than one). This function is to find just one of them.

        The chosen one is left in slot.events, and the original inputs are moved to slot.events_archived.
        """
        event = None
        p = -1
        for each in self.slots[self.present].events:
            new_p = self.slots[self.present].events[each].priority
            if new_p > p:
                event = self.slots[self.present].events[each]
                p = new_p

        if event is not None:  # else, there are no inputs at all in this time slot
            self.slots[self.present].events_archived[event.word] = event
            self.slots[self.present].events, self.slots[self.present].events_archived = \
                self.slots[self.present].events_archived, self.slots[self.present].events

    def compound_generation(self):
        # the start of a buffer cycle, so every event is loaded to the working space
        self.slots[self.present].working_space = self.slots[self.present].events.copy()
        # buffers have no temporal/spatial compounding capability, so then pass

    def local_evaluation(self):
        """
        For buffers, only one event is input in each buffer cycle, so the local evaluation function is only to adjust
        its priority and truth-value (is applicable).
        """
        # check whether some predictions can be applied (fire)
        for i in range(len(self.predictions)):

            # subject =/> predict

            # a subject is found first and then a search on all events
            # if a prediction can fire, it is good, but if it cannot often, it will be dropped

            # predictions may be like "(&/, A, +1) =/> B", the content of the subject will just be A in this version
            # but if it is "(&/, A, +1, B) =/> C", no need to change the subject

            interval = 0
            if isinstance(self.predictions[i][1].term.subject.terms[-1], Interval):
                subject = Compound.SequentialEvents(
                    *self.predictions[i][1].term.subject.terms[:-1])  # precondition
                interval = int(self.predictions[i][1].term.subject.terms[-1])
            else:
                subject = self.predictions[i][1].term.subject

            # since there might be some little differences in Narsese, e.g., (&/, A, +1) and simply A
            # deduction functions cannot be applied here, though the same process will follow
            for each_event in self.slots[self.present].working_space:
                if subject.equal(self.slots[self.present].working_space[each_event].t.term):
                    # term generation
                    term = self.predictions[i][1].term.predicate
                    # truth, using truth-deduction function
                    truth = Truth_deduction(self.predictions[i][1].truth,
                                            self.slots[self.present].working_space[each_event].t.truth)
                    # stamp, using stamp-merge function
                    stamp = Stamp_merge(self.predictions[i][1].stamp,
                                        self.slots[self.present].working_space[each_event].t.stamp)
                    # budget, using budget-forward function
                    budget = Budget_forward(truth,
                                            self.predictions[i][1].budget,
                                            self.slots[self.present].working_space[each_event].t.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    # anticipation generation
                    anticipation = Anticipation(task, self.predictions[i][1])
                    # if interval is too large, a far anticipation will be created
                    if interval <= self.present:
                        self.slots[self.present + interval].update_anticipations(anticipation)
                    break

        # check anticipations with exception handling (non-anticipation events)
        # unexpected event will have 10% more priorities
        self.slots[self.present].check_anticipation(self)

        # unsatisfied anticipation (failed prediction) handling
        for each_anticipation in self.slots[self.present].anticipations:
            if not self.slots[self.present].anticipations[each_anticipation].solved:
                # punish the predictions
                self.slots[self.present].anticipations[each_anticipation].unsatisfied(self)

    def goal_filtering(self):
        for each in self.slots[self.present].working_space:
            if each in self.goals:
                # for these events fit self.goals, there priority multiplier will be 1.5 times larger. TODO
                self.slots[self.present].working_space[each].priority_multiplier *= 1.5

    def memory_based_evaluations(self):
        """
        Find whether a concept is already in the main memory. If so, the priority should be changed, but it is reflected
        on the priority multiplier, not a direct change. Since if it is really accepted by the memory, this change must
        be applied, so, no need to do it here.

        And its complexity is set to 1.
        e.g., hotdog as a compound, but it is also an atom
        """
        for each_event in self.slots[self.present].working_space:
            tmp = self.memory.concepts.take_by_key(self.slots[self.present].working_space[each_event].t.term,
                                                   remove=False)
            if tmp is not None:
                budget = Budget_merge(each_event[1].budget, tmp.budget)
                each_event.priority_multiplier *= budget.priority / each_event.t.budget.priority
                each_event.complexity = 1

        # print("-------------------------")
        # print("without short-term memory")
        # for each in self.slots[self.present].working_space:
        #     print(self.slots[self.present].working_space[each].t)

        for each in self.slots[self.present].working_space:
            idx = self.in_short_term_memory(self.slots[self.present].working_space[each].t)
            if idx != -1:
                self.slots[self.present].working_space[each].t.budget = self.short_term_memory[idx].budget
            else:
                self.slots[self.present].working_space[each].t.budget.priority = 0.1

        # short-term memory handling
        self.update_short_term_memory(self.slots[self.present].working_space)

        # sorting (finding the max)
        # after the above process, every event in the working space will not be further changed, so it is the time
        # to find the one with the highest priority and send it to the next level
        candidate = None
        priority = -1
        for each_event in self.slots[self.present].working_space:
            if self.slots[self.present].working_space[each_event].priority > priority:
                candidate = self.slots[self.present].working_space[each_event].t
                priority = self.slots[self.present].working_space[each_event].priority

        self.slots[self.present].candidate = candidate

    def prediction_generation(self):

        # subject =/> predict
        # using induction rules (TODO, maybe another)

        if self.slots[self.present].candidate is not None:
            predicate = self.slots[self.present].candidate.term
            for i in range(self.present):
                if self.slots[i].candidate:
                    # e.g., (E, +1) as the subject
                    subject = Compound.SequentialEvents(self.slots[i].candidate.term,
                                                        Interval(abs(self.present - i)))
                    copula = Copula.PredictiveImplication  # =/>
                    # term
                    term = Statement(subject, copula, predicate)
                    # truth, using truth-induction function
                    truth = Truth_induction(self.slots[self.present].candidate.truth,
                                            self.slots[i].candidate.truth)
                    # stamp, using stamp-merge function
                    stamp = Stamp_merge(self.slots[self.present].candidate.stamp,
                                        self.slots[i].candidate.stamp, )
                    # budget, using budget-forward function
                    budget = Budget_forward(truth,
                                            self.slots[self.present].candidate.budget,
                                            self.slots[i].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)

        return self.slots[self.present].candidate

    def goal_achieved(self):
        """
        Check whether some goals have been achieved. This function is called at the end of each buffer cycle, after
        self.prediction_generation.
        """
        for each in self.slots[self.present].working_space:
            if each in self.goals:
                # TODO, now achieved goals are just popped, might be weakened instread of removing
                self.goals.pop(each)

    def rule_1(self):
        """
        For predictions like "A =/> B", when B is a goal, then make A is a goal as well.

        This function is called after self.goal_achieved.
        """
        goal_updates = []

        for i in range(len(self.predictions)):
            statement: Statement = self.predictions[i][1].term
            if statement.predicate.word in self.goals:
                goal_updates.append(Goal(statement.predicate))

        for each in goal_updates:
            self.update_goal(each)

    def rule_2(self):
        """
        When a sequential compound is a goal, say (A, B, C)! Then make the first one a goal.

        This function runs after self.rule_1.
        """
        goal_updates = []

        for each in self.goals:
            term: Term = self.goals[each].term
            if term.is_compound:
                cpd: Compound = term
                if cpd.connector is Connector.SequentialEvents:
                    goal_updates.append(Goal(cpd.terms[0]))

        for each in goal_updates:
            self.update_goal(each)

    def rule_3(self):
        """
        When a sequential compound is a goal, and the first atomic of it is finished, say in slot.working_space,
        then the remaining part will be created as a new goal.

        Say when we have (A, B, C)!, and A., then we have (B, C)!

        TODO, this could be expanded to "a part of it is finished, not just the first one".
        """
        goal_updates = []

        for each in self.goals:
            term: Term = self.goals[each].term
            if term.is_compound:
                cpd: Compound = term
                if cpd.connector is Connector.SequentialEvents:
                    first_atom = cpd.terms[0]
                    if first_atom.word in self.slots[self.present].working_space:
                        if len(cpd.terms) > 1:
                            if cpd.terms[1].is_interval:
                                remaining_part = cpd.terms[2:]
                            else:
                                remaining_part = cpd.terms[1:]
                            goal_updates.append(Goal(Compound.SequentialEvents(*remaining_part)))

        for each in goal_updates:
            self.update_goal(each)

    def goal_reasoning(self):
        self.goal_achieved()
        self.rule_1()
        self.rule_2()
        self.rule_3()

    def step(self, new_content):
        """
        Event buffer can get at most one new content each time, and so there are no "concurrent compound generations"
        in definition. But this will change if "default operation processing" is considered.
        """
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(Slot(1, self.num_anticipation, self.num_operation))

        for each in new_content:  # new_content is a list of tasks
            self.slots[self.present].input_events(each)

        self.input_filtering()
        self.compound_generation()
        self.local_evaluation()
        self.memory_based_evaluations()
        task_forward = self.prediction_generation()
        self.goal_reasoning()

        # print("-------------------------")
        # print("with short-term memory")
        # for each in self.slots[self.present].working_space:
        #     print(self.slots[self.present].working_space[each].t)

        print("-------------------------")
        print("short-term memory")
        for each in self.short_term_memory:
            print(each)
        print("-------------------------")

        return task_forward
