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
from ..DataStructures.MC.ChannelMC import ChannelMC
from ..DataStructures.MC.GlobalBufferMC import GlobalBufferMC
from ..DataStructures.MC.InternalBufferMC import InternalBufferMC
from ..DataStructures.MC.OutputBufferMC import OutputBufferMC
from ..DataStructures.MC.SampleChannels.SampleChannel1 import SampleChannel1
from ..InferenceEngine import GeneralEngine
from pynars import Config
from pynars.Config import Enable
from typing import Callable, List, Tuple, Union
import pynars.NARS.Operation as Operation
from pynars import Global


class ReasonerMC:

    def __init__(self, n_memory, config = './config.json') -> None:
        # print('''Init...''')
        Config.load(config)
        self.inference = GeneralEngine()
        # self.temporal_inference = TemporalEngine()  # for temporal causal reasoning
        self.memory = Memory(n_memory)
        self.channels: List[ChannelMC] = [
            SampleChannel1("SC1", 3, 10, 10, 10, self.memory)
        ]
        # TODO, these parameters could come from config.json
        self.internal_buffer = InternalBufferMC(3, 10, 10, 10, self.memory)
        self.global_buffer = GlobalBufferMC(3, 10, 10, 10, self.memory)
        self.output_buffer = OutputBufferMC()
        for each_channel in self.channels:
            self.output_buffer.register_channel(each_channel)

    def reset(self):
        """
        Everything in the buffers should be cleared.
        """
        # TODO

    def cycles(self, n_cycle: int):
        for _ in range(n_cycle):
            self.cycle()

    def cycle(self):
        """Everything to do by NARS in a single working cycle"""

        # step 1, take out a task from the internal buffer, and put it into the global buffer
        task_from_internal_buffer = self.internal_buffer.step(self.internal_buffer.previous_inference_result)

        # step1.5, execute the task if executable
        self.output_buffer.step(task_from_internal_buffer)

        # step 2, Take out a task from each channel, and put it into the global buffer
        tasks_from_channels = []
        for each_channel in self.channels:
            tasks_from_channels.append(each_channel.step())

        # step 2.5, merge the task from the internal buffer and the tasks from channels
        tasks_for_global_buffer = tasks_from_channels + [task_from_internal_buffer]
        tasks_for_global_buffer = list(filter(None, tasks_for_global_buffer))

        # step 3, feed these tasks to the global buffer and send the one from the global buffer to the main memory
        task_from_global_buffer = self.global_buffer.step(tasks_for_global_buffer)
        if task_from_global_buffer:
            judgement_revised, goal_revised, answers_question, answers_quest = self.memory.accept(
                task_from_global_buffer)
            # if Enable.temporal_rasoning:
            #     # TODO: Temporal Inference
            #     raise
            # TODO, what does this mean
            # if judgement_revised is not None:
            #     self.internal_buffer.update_inference_result(judgement_revised)
            # if goal_revised is not None:
            #     self.internal_buffer.update_inference_result(goal_revised)
            # if answers_question is not None:
            #     for answer in answers_question:
            #         self.internal_buffer.update_inference_result(answer)
            # if answers_quest is not None:
            #     for answer in answers_quest:
            #         self.internal_buffer.update_inference_result(answer)
        else:
            judgement_revised, goal_revised, answers_question, answers_quest = None, None, None, None

        # step 4, apply general inference step
        concept: Concept = self.memory.take(remove=True)
        tasks_derived: List[Task] = []
        if concept is not None:
            tasks_inference_derived = self.inference.step(concept)
            tasks_derived.extend(tasks_inference_derived)
            # TODO: relevant process
            is_concept_valid = True
            if is_concept_valid:
                self.memory.put_back(concept)
        self.internal_buffer.previous_inference_result = tasks_derived

        #   temporal induction in NAL-7
        # if False and task_from_global_buffer is not None and task_from_global_buffer.is_judgement and
        # task_from_global_buffer.is_external_event:
        #     concept_task: Concept = self.memory.take_by_key(task_from_global_buffer.term, remove=False)
        #     tasks_derived.extend(
        #         self.temporal_inference.step(
        #             task_from_global_buffer, concept_task,
        #             self.sequence_buffer,
        #             self.operations_buffer
        #         )
        #     )
        # else:
        #     pass  # TODO: select a task from `self.sequence_buffer`?

        #   mental operation of NAL-9
        # TODO, what does it mean
        # task_operation_return, task_executed = None, None
        # if False:
        #     task_operation_return, task_executed, belief_awared = self.mental_operation(task,
        #     concept, answers_question, answers_quest)
        #     if task_operation_return is not None: tasks_derived.append(task_operation_return)
        #     if task_executed is not None: tasks_derived.append(task_executed)
        #     if belief_awared is not None: tasks_derived.append(belief_awared)

        #   execute registered operations
        # if task is not None and task.is_executable:
        #     from pynars.NARS import Operation
        #     stat: Statement = task.term
        #     op = stat.predicate
        #     if op in Operation.registered_operations and not task.is_mental_operation:
        #         # to judge whether the goal is satisfied
        #         task_operation_return, task_executed = Operation.execute(task, concept, self.memory)
        #         concept_task = self.memory.take_by_key(task, remove=False)
        #         if concept_task is not None:
        #             belief: Belief = concept_task.match_belief(task.sentence)
        #         if belief is not None:
        #             task.budget.reduce_by_achieving_level(belief.truth.e)
        #         if task_operation_return is not None: tasks_derived.append(task_operation_return)
        #         if task_executed is not None: tasks_derived.append(task_executed)

        #   put the tasks-derived into the internal-experience.
        # for task_derived in tasks_derived:
        #     self.internal_experience.put(task_derived)

        # handle the sense of time
        Global.time += 1

        return tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (None, None)

    # def mental_operation(self, task: Task, concept: Concept, answers_question: Task, answers_quest: Task):
    #     # handle the mental operations in NAL-9
    #     task_operation_return, task_executed, belief_awared = None, None, None
    #
    #     # belief-awareness
    #     for answers in (answers_question, answers_quest):
    #         if answers is None: continue
    #         for answer in answers:
    #             belief_awared = Operation.aware__believe(answer)
    #
    #     if task is not None:
    #         # question-awareness
    #         if task.is_question:
    #             belief_awared = Operation.aware__wonder(task)
    #         # quest-awareness
    #         elif task.is_quest:
    #             belief_awared = Operation.aware__evaluate(task)
    #
    #             # execute mental operation
    #     if task is not None and task.is_executable:
    #         task_operation_return, task_executed = Operation.execute(task, concept, self.memory)
    #
    #     return task_operation_return, task_executed, belief_awared

    # def register_operation(self, name_operation: str, callback: Callable):
    #     """"""
    #     from pynars.Narsese import Operation as Op
    #     op = Op(name_operation)
    #     Operation.register(op, callback)
