import random
from pynars.NARS.DataStructures._py.Channel import Channel

from pynars.Narsese._py.Budget import Budget
from pynars.Narsese import Term, Copula, Item
from ..DataStructures import Bag, Memory, NarseseChannel, Buffer, Task, Concept, EventBuffer
from pynars import Config
from pynars.Config import Enable
from typing import Callable, List, Tuple, Union
import pynars.NARS.Operation as Operation
from pynars import Global
from time import time
from ..GlobalEval import GlobalEval
from pynars.NARS.InferenceEngineInterface.KanrenInterface import InferenceEngine

class Reasoner:
    avg_inference = 0
    num_runs = 0

    def __init__(self, n_memory, capacity, config='./config.json', 
                 nal_rules={1, 2, 3, 4, 5, 6, 7, 8, 9}, inference: str = 'kanren') -> None:
        Config.load(config)

        self.global_eval = GlobalEval()

        self.inference_engine = InferenceEngine()

        self.memory = Memory(n_memory, global_eval=self.global_eval)
        self.overall_experience = Buffer(capacity)
        self.internal_experience = Buffer(capacity)
        self.event_buffer = EventBuffer(3)
        self.narsese_channel = NarseseChannel(capacity)
        self.channels: List[Channel] = [
            self.narsese_channel,
        ]  # append other channels here

        self.sequence_buffer = Buffer(capacity)
        self.operations_buffer = Buffer(capacity)

        self.u_top_level_attention = 0.5

        # metrics
        self.cycles_count = 0
        self.last_cycle_duration = 0
        self.avg_cycle_duration = 0

    def reset(self):
        self.memory.reset()
        self.overall_experience.reset()
        self.internal_experience.reset()
        self.narsese_channel.reset()
        for channel in self.channels:
            channel.reset()

        self.sequence_buffer.reset()
        self.operations_buffer.reset()
        self.inference_engine.reset()

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
        start_cycle_time_in_seconds = time()
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

        """done with cycle"""
        self.do_cycle_metrics(start_cycle_time_in_seconds)

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
            tasks_inference_derived = self.inference_engine.step(concept)
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
    
    # METRICS
    def do_cycle_metrics(self, start_cycle_time_in_seconds: float):
        #  record some metrics
        total_cycle_duration_in_seconds = time() - start_cycle_time_in_seconds
        self.last_cycle_duration = total_cycle_duration_in_seconds # store the cycle duration
        # calculate average
        self.cycles_count += 1
        self.avg_cycle_duration += (self.last_cycle_duration - self.avg_cycle_duration) / self.cycles_count
