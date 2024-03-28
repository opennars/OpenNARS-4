import random
from os import remove
from pynars.NAL.Functions.BudgetFunctions import Budget_forward, Budget_backward
from pynars.NAL.Functions.StampFunctions import Stamp_merge
from pynars.NAL.Functions.Tools import truth_to_quality
from pynars.NARS.DataStructures._py.Channel import Channel

from pynars.NARS.DataStructures._py.Link import TaskLink, TermLink
from pynars.NARS.InferenceEngine import TemporalEngine
# from pynars.NARS.Operation import Interface_Awareness
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Sentence import Judgement, Stamp, Tense, Question, Goal
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Compound import Compound
from pynars.Narsese._py.Connector import Connector
from pynars.Narsese._py.Task import Belief
from pynars.Narsese._py.Evidence import Base
from pynars.Narsese import Copula, Item
from ..DataStructures import Bag, Memory, NarseseChannel, Buffer, Task, Concept, EventBuffer
from ..InferenceEngine import GeneralEngine, TemporalEngine, VariableEngine, KanrenEngine
from pynars import Config
from pynars.Config import Enable
from typing import Callable, List, Tuple, Union
import pynars.NARS.Operation as Operation
from pynars import Global
from time import time
from pynars.NAL.Functions.Tools import project_truth, project
from ..GlobalEval import GlobalEval
from ..InferenceEngine.KanrenEngine import util

class Reasoner:
    avg_inference = 0
    num_runs = 0
    
    all_theorems = Bag(100, 100, take_in_order=False)
    theorems_per_cycle = 1

    class TheoremItem(Item):
        def __init__(self, theorem, budget: Budget) -> None:
            super().__init__(hash(theorem), budget)
            self._theorem = theorem

    def __init__(self, n_memory, capacity, config='./config.json', nal_rules={1, 2, 3, 4, 5, 6, 7, 8, 9}) -> None:
        # print('''Init...''')
        Config.load(config)

        self.global_eval = GlobalEval()

        self.inference = KanrenEngine()
        
        # a = util.parse('(*,a,b,(*,c,d),e,(*,f,g)).')
        # b = util.logic(a.term)

        # c = util.term(b)

        for theorem in self.inference.theorems:
            priority = random.randint(0,9) * 0.01
            item = self.TheoremItem(theorem, Budget(0.5 + priority, 0.8, 0.5))
            self.all_theorems.put(item)

        # self.inference = GeneralEngine(add_rules=nal_rules)
        self.variable_inference = VariableEngine(add_rules=nal_rules)
        self.temporal_inference = TemporalEngine(
            add_rules=nal_rules)  # for temporal causal reasoning

        self.memory = Memory(n_memory, global_eval=self.global_eval)
        self.overall_experience = Buffer(capacity)
        self.internal_experience = Buffer(capacity)
        self.event_buffer = EventBuffer(3)
        self.narsese_channel = NarseseChannel(capacity)
        self.perception_channel = Channel(capacity)
        self.channels: List[Channel] = [
            self.narsese_channel,
            self.perception_channel
        ]  # TODO: other channels

        self.sequence_buffer = Buffer(capacity)
        self.operations_buffer = Buffer(capacity)

        self.u_top_level_attention = 0.5

    def reset(self):
        self.memory.reset()
        self.overall_experience.reset()
        self.internal_experience.reset()
        self.narsese_channel.reset()
        self.perception_channel.reset()
        for channel in self.channels:
            channel.reset()

        self.sequence_buffer.reset()
        self.operations_buffer.reset()

        # reset theorems priority
        self.all_theorems.reset()
        for theorem in self.inference.theorems:
            priority = random.randint(0,9) * 0.01
            item = self.TheoremItem(theorem, Budget(0.5 + priority, 0.8, 0.5))
            self.all_theorems.put(item)

        # reset metrics
        self.avg_inference = 0
        self.num_runs = 0

    def cycles(self, n_cycle: int):
        tasks_all_cycles = []
        for _ in range(n_cycle):
            tasks_all_cycles.append(self.cycle())
        return tasks_all_cycles

    def input_narsese(self, text, go_cycle: bool = False) -> Tuple[bool, Union[Task, None], Union[Task, None]]:
        success, task, task_overflow = self.narsese_channel.put(text)
        if go_cycle:
            tasks = self.cycle()
            return success, task, task_overflow, tasks
        return success, task, task_overflow

    def cycle(self):
        """Everything to do by NARS in a single working cycle"""
        Global.States.reset()
        tasks_derived: List[Task] = []

        judgement_revised, goal_revised, answers_question, answers_quest = None, None, None, None
        task_operation_return, task_executed = None, None

        random_number: float = random.random()

        data_structure_accessed_busyness = None
        if random_number < self.u_top_level_attention:
            judgement_revised, goal_revised, answers_question, answers_quest = self.observe(
                tasks_derived)
            data_structure_accessed_busyness = self.overall_experience.busyness
        else:
            self.consider(tasks_derived)
            data_structure_accessed_busyness = self.memory.busyness

        self.u_top_level_attention = Config.Config.r_top_level_attention_adjust * data_structure_accessed_busyness \
            + (1 - Config.Config.r_top_level_attention_adjust) * \
            self.u_top_level_attention

        #   put the derived tasks into the internal-experience.
        for task_derived in tasks_derived:
            self.internal_experience.put(task_derived)

        # handle the sense of time
        Global.time += 1
        thresh_complexity = 20
        tasks_derived = [
            task for task in tasks_derived if task.term.complexity <= thresh_complexity]
        return tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed)

    def consider(self, tasks_derived: List[Task]):
        """
            Consider a Concept in the Memory
        """
        # step 4. Apply inference step
        #   general inference step
        concept: Concept = self.memory.take(remove=True)
        if concept is not None:
            # self.num_runs += 1
            # t0 = time()
            tasks_inference_derived = self.inference_step(concept)
            tasks_derived.extend(tasks_inference_derived)
            # t1 = time() - t0 + 1e-6 # add epsilon to avoid division by 0
            # self.avg_inference += (t1 - self.avg_inference) / self.num_runs
            # print("inference:", 1 // self.avg_inference, "per second", f"({1//t1})")
            
            is_concept_valid = True  # TODO
            if is_concept_valid:
                self.memory.put_back(concept)

    def observe(self, tasks_derived: List[Task]):
        """
            OBSERVE
            Process Channels/Buffers
        """
        judgement_revised, goal_revised, answers_question, answers_quest = None, None, None, None
        # step 1. Take out an Item from `Channels`, and then put it into the `Overall Experience` and Event Buffers
        for channel in self.channels:
            task_in: Task = channel.take()
            if task_in is not None:
                self.overall_experience.put(task_in)
                if self.event_buffer.can_task_enter(task_in):
                    self.event_buffer.put(task_in)
                    # when there's a new event, run the temporal chaining
                    temporal_results = self.event_buffer.generate_temporal_sentences()
                    for result in temporal_results:
                        self.overall_experience.put(result)

        # step 2. Take out an Item from the `Internal Experience`, with putting it back afterwards, and then put it
        # into the `Overall Experience`
        task: Task = self.internal_experience.take(remove=True)
        if task is not None:
            self.overall_experience.put(task)
            self.internal_experience.put_back(task)

        # step 3. Process a task in the global experience buffer
        task: Task = self.overall_experience.take()
        if task is not None and not task.processed:
            task.processed = True
            # if task.is_goal:
            #     print(task)

            # concept = self.memory.take_by_key(task.term, remove=False)
            # if task.is_goal:
            # goal_revised = self.process_goal(task, concept)
            judgement_revised, goal_revised, answers_question, answers_quest, (
                task_operation_return, task_executed), _tasks_derived = self.memory.accept(task)
            if task_operation_return is not None:
                tasks_derived.append(task_operation_return)
            # if task_executed is not None: tasks_derived.append(task_executed)
            tasks_derived.extend(_tasks_derived)
            # self.sequence_buffer.put_back(task) # globalBuffer.putBack(task,
            # narParameters.GLOBAL_BUFFER_FORGET_DURATIONS, this)

            if Enable.temporal_reasoning:
                # TODO: Temporal Inference
                # Ref: OpenNARS 3.1.0 line 409~411
                # if (!task.sentence.isEternal() && !(task.sentence.term instanceof Operation)) {
                #     globalBuffer.eventInference(task, cont, false); //can be triggered by Buffer itself in the future
                # }
                raise

            if judgement_revised is not None:
                self.internal_experience.put(judgement_revised)
            if goal_revised is not None:
                self.internal_experience.put(goal_revised)
            if answers_question is not None:
                for answer in answers_question:
                    self.internal_experience.put(answer)
            if answers_quest is not None:
                for answer in answers_quest:
                    self.internal_experience.put(answer)
            # update busyness
            self.global_eval.update_busyness(task.budget.priority)

        """ update alertness
        Note: 
            according to [Wang, P., Talanov, M., & Hammer, P. (2016). The emotional mechanisms in NARS. In Artificial General Intelligence: 9th International Conference, AGI 2016, New York, NY, USA, July 16-19, 2016, Proceedings 9 (pp. 150-159). Springer International Publishing.](https://cis.temple.edu/~pwang/Publication/emotion.pdf)
                > summarizes the average difference between recently processed input and the corresponding anticipations, so as to roughly indicate the extent to which the current environment is familiar.
            The current code hasn't implemented `EventBuffer` yet.
            The intuitive meaning of `alertness` is 
                > the extent to which the system’s knowledge is insufficient
                (see [The Conceptual Design of OpenNARS 3.1.0](https://cis.temple.edu/tagit/publications/PAGI-TR-11.pdf))
            We tentatively exploit the truth of a revised task to indicate alertness
        """
        if judgement_revised is not None:
            self.global_eval.update_alertness(
                judgement_revised.truth.c - task.truth.c)
        else:
            self.global_eval.update_alertness(0.0)
            # TODO: handling temporal induction and mental operation
            #       Is it implemented correctly?

            #   temporal induction in NAL-7
            if Enable.temporal_reasoning and task is not None and task.is_judgement and task.is_external_event:
                concept_task: Concept = self.memory.take_by_key(
                    task.term, remove=False)
                # t1 = time()
                tasks_derived.extend(
                    self.temporal_inference.step(
                        task, concept_task,
                        self.sequence_buffer,
                        self.operations_buffer
                    )
                )
                # t2 = time()
                # print(f"time: {t2-t1}")
            else:
                pass  # TODO: select a task from `self.sequence_buffer`?

            #   mental operation of NAL-9
            if Enable.operation:  # it should be `Enable.mental_operation`?
                # self.memory.
                concept_task: Concept = self.memory.take_by_key(
                    task.term, remove=False)
                task_operation_return, task_executed, belief_awared = self.mental_operation(
                    task, concept_task, answers_question, answers_quest)
                if task_operation_return is not None:
                    tasks_derived.append(task_operation_return)
                if task_executed is not None:
                    tasks_derived.append(task_executed)
                if belief_awared is not None:
                    tasks_derived.append(belief_awared)

        return judgement_revised, goal_revised, answers_question, answers_quest,

    def mental_operation(self, task: Task, concept: Concept, answers_question: Task, answers_quest: Task):
        # handle the mental operations in NAL-9
        task_operation_return, task_executed, belief_awared = None, None, None

        # belief-awareness
        for answers in (answers_question, answers_quest):
            if answers is None:
                continue
            for answer in answers:
                belief_awared = Operation.aware__believe(answer)

        if task is not None:
            # question-awareness
            if task.is_question:
                belief_awared = Operation.aware__wonder(task)
            # quest-awareness
            elif task.is_quest:
                belief_awared = Operation.aware__evaluate(task)

                # execute mental operation
        if task is not None and task.is_executable:
            task_operation_return, task_executed = Operation.execute(
                task, concept, self.memory)

            # update well-being
            self.global_eval.update_wellbeing(task_executed.truth.e)

        return task_operation_return, task_executed, belief_awared

    def register_operator(self, name_operator: str, callback: Callable):
        '''register an operator and return the operator if successful (otherwise, return None)'''
        if not Operation.is_registered_by_name(name_operator):
            from pynars.Narsese import Operator as Op
            op = Op(name_operator)
            Operation.register(op, callback)
            return op
        return None

#################################################

    # INFERENCE STEP 

    def inference_step(self, concept: Concept):
        '''One step inference.'''
        tasks_derived = []

        Global.States.record_concept(concept)
        
        # Based on the selected concept, take out a task and a belief for further inference.
        task_link: TaskLink = concept.task_links.take(remove=True)
        
        if task_link is None: 
            return tasks_derived
        
        concept.task_links.put_back(task_link)

        task: Task = task_link.target

        # print('')
        # print(task.sentence)

        # _t0 = time()
        # t0 = time()

        # inference for single-premise rules
        if not task.immediate_rules_applied: # TODO: handle other cases
            Global.States.record_premises(task)

            results = []

            backward = task.is_question or task.is_goal
            res, cached = self.inference.inference_immediate(task.sentence, backward=backward)

            if not cached:
                results.extend(res)

            for term, truth in results:
                # TODO: how to properly handle stamp for immediate rules?
                # base = Base((Global.get_input_id(),))
                # stamp_task: Stamp = Stamp(Global.time, None, None, base)
                stamp_task = task.stamp

                if task.is_question and term[1] == 'cnv':
                    question_derived = Question(term[0], stamp_task)
                    task_derived = Task(question_derived)
                    # set flag to prevent repeated processing
                    task_derived.immediate_rules_applied = True
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)
                
                if task.is_goal and term[1] == 'cnv':
                    goal_derived = Goal(term[0], stamp_task, truth)
                    task_derived = Task(goal_derived)
                    # set flag to prevent repeated processing
                    task_derived.immediate_rules_applied = True
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

                if task.is_judgement: # TODO: hadle other cases
                    # TODO: calculate budget
                    budget = Budget_forward(truth, task_link.budget, None)
                    budget.priority = budget.priority * 1/term[0].complexity
                    sentence_derived = Judgement(term[0], stamp_task, truth)
                    task_derived = Task(sentence_derived, budget)
                    # set flag to prevent repeated processing
                    task_derived.immediate_rules_applied = True
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

            # record immediate rule application for task
            task.immediate_rules_applied = True

        # _t1 = time() - t0 + 1e-6 # add epsilon to avoid division by 0
        # print('single premise', 1//_t1)
        # t0 = _t1
        # self._run_count += 1


        ### STRUCTURAL

        if task.is_judgement or task.is_goal or task.is_question: #and not task.structural_rules_applied: # TODO: handle other cases
            Global.States.record_premises(task)

            results = []

            # t0 = time()
            theorems = []
            for _ in range(min(self.theorems_per_cycle, len(self.all_theorems))):
                theorem = self.all_theorems.take(remove=True)
                theorems.append(theorem)
            
            for theorem in theorems:
                # print(term(theorem._theorem))
                # results.extend(self.inference_structural(task.sentence))
                res, cached = self.inference.inference_structural(task.sentence, tuple([theorem._theorem]))
                # print(res)
                # print("")
                if not cached:
                    if res:
                        new_priority = theorem.budget.priority + 0.1
                        theorem.budget.priority = min(0.99, new_priority)
                    else:
                        new_priority = theorem.budget.priority - 0.1
                        theorem.budget.priority = max(0.1, new_priority)

                self.all_theorems.put(theorem)

                results.extend(res)
            # t1 = time() - t0
            # self._structural_time_avg += (t1 - self._structural_time_avg) / self._run_count
            # print("structural: ", 1 // self._structural_time_avg, "per second")
            # for r in results:
            #     print(r, r[0][0].complexity)
            # print(task.budget.priority)
            # print(task_link.budget.priority)
            for term, truth in results:
                # TODO: how to properly handle stamp for structural rules?
                stamp_task: Stamp = task.stamp

                if task.is_question:
                    pass

                if task.is_goal:
                    goal_derived = Goal(term[0], stamp_task, truth)
                    task_derived = Task(goal_derived)
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

                if task.is_judgement: # TODO: hadle other cases
                    # TODO: calculate budget
                    budget = Budget_forward(truth, task_link.budget, None)
                    budget.priority = budget.priority * 1/term[0].complexity
                    sentence_derived = Judgement(term[0], stamp_task, truth)
                    task_derived = Task(sentence_derived, budget)
                    # task_derived.structural_rules_applied = True
                    
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

            # record structural rule application for task
            # task.structural_rules_applied = True

        # _t1 = time() - t0 + 1e-6 # add epsilon to avoid division by 0
        # print('structural', 1//_t1)
        # t0 = _t1

        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False
        # n = len(concept.term_links)
        # t0 = time()
        # iter = 0
        for _ in range(len(concept.term_links)): # TODO: should limit max number of links to process
            # iter += 1
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            # _t = time()
            term_link: TermLink = concept.term_links.take(remove=True)
            # print(round((time() - _t)*1000, 2))
            term_links.append(term_link)

            if not task_link.novel(term_link, Global.time):
                continue
            
            concept_target: Concept = term_link.target
            belief = concept_target.get_belief() # TODO: consider all beliefs.
            
            if belief is None: 
                continue

            if task == belief:
                # if task.sentence.punct == belief.sentence.punct:
                #     is_revision = revisible(task, belief)
                continue
            # TODO: currently causes infinite recursion with variables
            # elif task.term.equal(belief.term): 
            #     # TODO: here
            #     continue
            elif not belief.evidential_base.is_overlaped(task.evidential_base):
                term_link_valid = term_link
                is_valid = True
                break

        # t1 = time() - t0
        # loop_time = round(t1 * 1000, 2)
        # if loop_time > 20:
        #     print("hello")
        # print(iter, '/', n, "- loop time", loop_time, is_valid)
        # print(is_valid, "Concept", concept.term)
        if is_valid \
            and task.is_judgement: # TODO: handle other cases
            
            Global.States.record_premises(task, belief)

            # t0 = time()
                    
            results = []

            # COMPOSITIONAL
            if task.is_eternal and belief.is_eternal:
                # events are handled in the event buffer
                res, cached = self.inference.inference_compositional(task.sentence, belief.sentence)
                
                if not cached: 
                    results.extend(res)
            
            # Temporal Projection and Eternalization
            if belief is not None:
                # TODO: Handle the backward inference.
                if not belief.is_eternal and (belief.is_judgement or belief.is_goal):
                    truth_belief = project_truth(task.sentence, belief.sentence)
                    belief = belief.eternalize(truth_belief)
                    # beleif_eternalized = belief # TODO: should it be added into the `tasks_derived`?

            # SYLLOGISTIC
            res, cached = self.inference.inference(task.sentence, belief.sentence, concept.term)

            # t1 = time() - t0 + 1e-6 # add epsilon to avoid division by 0
            # print('syllogistic', 1//t1)
            # t0 = t1
            # t1 = time() - t0

            # print("inf:", 1 // t1, "per second")

            # self._inference_time_avg += (t1 - self._inference_time_avg) / self._run_count

            # print("avg:", 1 // self._inference_time_avg, "per second")
            
            # t0 = time()

            
            # t1 = time() - t0
            # print("inf comp:", 1 // t1, "per second")
            # t1 = time() - t0 + 1e-6 # add epsilon to avoid division by 0
            # print('compositional', 1//t1)
            # t0 = t1

            if not cached:
                results.extend(res)

            # print(">>>", results)

            for term, truth in results:

                budget = Budget_forward(truth, task_link.budget, term_link_valid.budget)

                # Add temporal dimension

                conclusion = term[0]

                t1 = task.sentence.term
                t2 = belief.sentence.term

                if type(conclusion) is Compound \
                and conclusion.connector == Connector.Conjunction:
                    # TODO: finish this
                    if type(belief.term) is Compound or type(belief.term) is Statement:
                        if belief.term.is_predictive:
                            conclusion = conclusion.predictive()
                        if belief.term.is_concurrent:
                            conclusion = conclusion.concurrent()

                if type(conclusion) is Statement \
                and (conclusion.copula == Copula.Equivalence \
                or conclusion.copula == Copula.Implication):

                    if type(t1) is Statement \
                    and type(t2) is Statement:
                        
                        if t1.copula.is_concurrent and t2.copula.is_concurrent:
                            # both concurrent
                            conclusion = conclusion.concurrent()

                        if t1.copula.is_predictive and t2.copula.is_predictive:
                            # both predictive
                            conclusion = conclusion.predictive()

                        if t1.copula.is_retrospective and t2.copula.is_retrospective:
                            # both retrospective
                            conclusion = conclusion.retrospective()

                        if (t1.copula.is_concurrent and t2.copula.is_predictive) \
                        or (t2.copula.is_concurrent and t1.copula.is_predictive):
                            # one concurrent, one predictive
                            conclusion = conclusion.predictive()
                        
                        if (t1.copula.is_concurrent and t2.copula.is_retrospective) \
                        or (t2.copula.is_concurrent and t1.copula.is_retrospective):
                            # one concurrent, one retrospective
                            conclusion = conclusion.retrospective()

                        terms = [] # more complex combinations require extra work

                        if t1.copula.is_predictive and t2.copula.is_retrospective:
                            terms = [t1.subject, t1.predicate]
                            if t2.subject in terms:
                                idx = terms.index(t2.subject)
                                terms.insert(idx, t2.predicate)
                            if t2.predicate in terms:
                                idx = terms.index(t2.predicate)
                                terms.insert(idx + 1, t2.subject)
                        elif t2.copula.is_predictive and t1.copula.is_retrospective:
                            terms = [t2.subject, t2.predicate]
                            if t1.subject in terms:
                                idx = terms.index(t1.subject)
                                terms.insert(idx, t1.predicate)
                            if t1.predicate in terms:
                                idx = terms.index(t1.predicate)
                                terms.insert(idx + 1, t1.subject)

                        if conclusion.predicate in terms and conclusion.subject in terms:
                            cpi = terms.index(conclusion.predicate)
                            csi = terms.index(conclusion.subject)
                            if cpi > csi:
                                # predicate after subject
                                conclusion = conclusion.predictive()
                            else:
                                # predicate before subject
                                conclusion = conclusion.retrospective()


                # calculate new stamp
                stamp_task: Stamp = task.stamp
                stamp_belief: Stamp = belief.stamp

                # TODO: how to correctly determine order?
                order_mark = None
                whole = part = None

                if task.sentence.term.copula and task.sentence.term.copula == Copula.PredictiveImplication:
                    whole = task
                    part = belief
                if belief.sentence.term.copula and belief.sentence.term.copula == Copula.PredictiveImplication:
                    whole = belief
                    part = task

                if part and whole:
                    if part.term == whole.sentence.term.subject:
                        order_mark = Copula.PredictiveImplication
                    if part.term == whole.sentence.term.predicate:
                        order_mark = Copula.RetrospectiveImplication

                stamp = Stamp_merge(stamp_task, stamp_belief, order_mark)

                sentence_derived = Judgement(conclusion, stamp, truth)
                # print(stamp.tense == sentence_derived.stamp.tense)
                task_derived = Task(sentence_derived, budget)
                # print(task_derived.sentence.tense, task_derived)
                # normalize the variable indices
                task_derived.term._normalize_variables()
                tasks_derived.append(task_derived)

            if term_link is not None:
                for derived_task in tasks_derived: 
                    reward: float = max(derived_task.budget.priority, task.achieving_level())
                    term_link.reward_budget(reward)

        # BACKWARD
        if is_valid \
            and task.is_question: # TODO: handle other cases

            results = []

            res, cached = self.inference.backward(task.sentence, belief.sentence)
            # print('\nBackward:', res)
            if not cached:
                results.extend(res)

            for term, _ in results:
                # budget = Budget_backward(truth, task_link.budget, term_link_valid.budget)

                question_derived = Question(term[0], task.stamp)
                task_derived = Task(question_derived) #, budget)
                tasks_derived.append(task_derived)

        if is_valid \
            and task.is_goal: # TODO: handle other cases

            results = []

            res, cached = self.inference.backward(task.sentence, belief.sentence)
            # print('\nBackward:', res)
            if not cached:
                results.extend(res)

            for term, truth in results:
                # budget = Budget_backward(truth, task_link.budget, term_link_valid.budget)
                conclusion = term[0]

                if type(conclusion) is Compound \
                and conclusion.connector == Connector.Conjunction:
                    # TODO: finish this
                    if type(belief.term) is Compound or type(belief.term) is Statement:
                        if belief.term.is_predictive:
                            conclusion = conclusion.predictive()
                        if belief.term.is_concurrent:
                            conclusion = conclusion.concurrent()

                goal_derived = Goal(conclusion, task.stamp, truth)
                task_derived = Task(goal_derived) #, budget)
                tasks_derived.append(task_derived)


        for term_link in term_links: 
            concept.term_links.put_back(term_link)
        
        return list(filter(lambda t: t.is_question or t.truth.c > 0, tasks_derived))
    
