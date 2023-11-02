from os import remove
from pynars.NAL.Functions.Tools import truth_to_quality
from pynars.NARS.DataStructures._py.Channel import Channel

from pynars.NARS.DataStructures._py.Link import TaskLink
from pynars.NARS.InferenceEngine import TemporalEngine
# from pynars.NARS.Operation import Interface_Awareness
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Task import Belief
from ..DataStructures import Bag, Memory, NarseseChannel, Buffer, Task, Concept
from ..InferenceEngine import GeneralEngine, TemporalEngine, VariableEngine
from pynars import Config
from pynars.Config import Enable
from typing import Callable, List, Tuple, Union
import pynars.NARS.Operation as Operation
from pynars import Global
from time import time
from pynars.NAL.Functions.Tools import project_truth, project

class Reasoner:

    def __init__(self, n_memory, capacity, config = './config.json', nal_rules={1,2,3,4,5,6,7,8,9}) -> None:
        # print('''Init...''')
        Config.load(config)

        self.inference = GeneralEngine(add_rules=nal_rules)
        self.variable_inference = VariableEngine(add_rules=nal_rules)
        self.temporal_inference = TemporalEngine(add_rules=nal_rules) # for temporal causal reasoning 

        self.memory = Memory(n_memory)
        self.overall_experience = Buffer(capacity)
        self.internal_experience = Buffer(capacity)
        self.narsese_channel = NarseseChannel(capacity)
        self.perception_channel = Channel(capacity)
        self.channels: List[Channel] = [
            self.narsese_channel,
            self.perception_channel
        ]  # TODO: other channels

        self.sequence_buffer = Buffer(capacity)
        self.operations_buffer = Buffer(capacity)

    def reset(self):
        ''''''
        # TODO

    def cycles(self, n_cycle: int):
        for _ in range(n_cycle):
            self.cycle()

    def input_narsese(self, text, go_cycle: bool = False) -> Tuple[bool, Union[Task, None], Union[Task, None]]:
        success, task, task_overflow = self.narsese_channel.put(text)
        if go_cycle: 
            tasks = self.cycle()
            return success, task, task_overflow, tasks
        return success, task, task_overflow

    def cycle(self):
        '''Everything to do by NARS in a single working cycle'''
        Global.States.reset()
        tasks_derived: List[Task] = []
        task_operation_return, task_executed = None, None
        # step 1. Take out an Item from `Channels`, and then put it into the `Overall Experience`
        for channel in self.channels:
            task_in: Task = channel.take()
            if task_in is not None:
                self.overall_experience.put(task_in)

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
            judgement_revised, goal_revised, answers_question, answers_quest, (task_operation_return, task_executed), _tasks_derived = self.memory.accept(task)
            if task_operation_return is not None: tasks_derived.append(task_operation_return)
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
        else:
            judgement_revised, goal_revised, answers_question, answers_quest = None, None, None, None

        # step 4. Apply inference step
        #   general inference step
        concept: Concept = self.memory.take(remove=True)
        if concept is not None:
            tasks_inference_derived = self.inference.step(concept)
            tasks_derived.extend(tasks_inference_derived)
            
            is_concept_valid = True # TODO
            if is_concept_valid:
                self.memory.put_back(concept)

        #   temporal induction in NAL-7
        if Enable.temporal_reasoning and task is not None and task.is_judgement and task.is_external_event:
            concept_task: Concept = self.memory.take_by_key(task.term, remove=False)
            t1 = time()
            tasks_derived.extend(
                self.temporal_inference.step(
                    task, concept_task,
                    self.sequence_buffer,
                    self.operations_buffer
                )
            )
            t2 = time()
            print(f"time: {t2-t1}")
        else:
            pass  # TODO: select a task from `self.sequence_buffer`?

        #   mental operation of NAL-9
        if Enable.operation: # it should be `Enable.mental_operation`?
            task_operation_return, task_executed, belief_awared = self.mental_operation(task, concept, answers_question,
                                                                                        answers_quest)
            if task_operation_return is not None: tasks_derived.append(task_operation_return)
            if task_executed is not None: tasks_derived.append(task_executed)
            if belief_awared is not None: tasks_derived.append(belief_awared)

        #   put the derived tasks into the internal-experience.
        for task_derived in tasks_derived:
            self.internal_experience.put(task_derived)

        # handle the sense of time
        Global.time += 1
        thresh_complexity = 20
        tasks_derived = [task for task in tasks_derived if task.term.complexity <= thresh_complexity]
        return tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed)

    def mental_operation(self, task: Task, concept: Concept, answers_question: Task, answers_quest: Task):
        # handle the mental operations in NAL-9
        task_operation_return, task_executed, belief_awared = None, None, None

        # belief-awareness
        for answers in (answers_question, answers_quest):
            if answers is None: continue
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
            task_operation_return, task_executed = Operation.execute(task, concept, self.memory)

        return task_operation_return, task_executed, belief_awared

    def register_operator(self, name_operator: str, callback: Callable):
        '''register an operator and return the operator if successful (otherwise, return None)'''
        if not Operation.is_registered_by_name(name_operator):
            from pynars.Narsese import Operator as Op
            op = Op(name_operator)
            Operation.register(op, callback)
            return op
        return None

