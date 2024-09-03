import random
from os import remove
from opennars.NAL.Functions.Tools import truth_to_quality
from opennars.NARS.DataStructures._py.Channel import Channel

from opennars.NARS.DataStructures._py.Link import TaskLink
from opennars.NARS.InferenceEngine import TemporalEngine
# from opennars.NARS.Operation import Interface_Awareness
from opennars.Narsese._py.Budget import Budget
from opennars.Narsese._py.Statement import Statement
from opennars.Narsese._py.Task import Belief
from ..DataStructures import Bag, Memory, NarseseChannel, Buffer, Task, Concept, EventBuffer
from ..InferenceEngine import GeneralEngine, TemporalEngine, VariableEngine
from opennars import Config
from opennars.Config import Enable
from typing import Callable, List, Tuple, Union, Dict
import opennars.NARS.Operation as Operation
from opennars import Global
from time import time
from opennars.NAL.Functions.Tools import project_truth, project
from ..GlobalEval import GlobalEval
from loguru import logger
from opennars.utils.Print import print_out, PrintType
from opennars.NARS.Channels.ConsoleChannel import ConsoleChannel
import threading


class Reasoner:

    def __init__(self, n_memory, capacity, config='./config.json', nal_rules={1, 2, 3, 4, 5, 6, 7, 8, 9}, record=False) -> None:
        # print('''Init...''')
        Config.load(config)

        self.global_eval = GlobalEval()

        self.inference = GeneralEngine(add_rules=nal_rules)
        self.variable_inference = VariableEngine(add_rules=nal_rules)
        self.temporal_inference = TemporalEngine(
            add_rules=nal_rules)  # for temporal causal reasoning

        self.memory = Memory(n_memory, global_eval=self.global_eval)
        self.overall_experience = Buffer(capacity)
        self.internal_experience = Buffer(capacity)
        self.event_buffer = EventBuffer(3)

        self.record = record
        if self.record:
            logger.remove()
            logger.add("experience_{time}.log", rotation="1 MB")  # 文件达到1 MB时轮转

        self.narsese_channel = NarseseChannel(capacity) # TODO: this line will be deprecated soon. All channels
        # self.channels: Dict[Channel, int] = {}
        self.channels: List[Channel] = []

        self.sequence_buffer = Buffer(capacity)
        self.operations_buffer = Buffer(capacity)

        self.u_top_level_attention = 0.5

        # metrics
        self.cycles_count = 0
        self.last_cycle_duration = 0
        self.avg_cycle_duration = 0

        # running
        self.paused = False


        # TODO: channel capacity as a parameter
        console_channel = ConsoleChannel(self, 1000)
        self.add_channel(console_channel)
        self.console_channel = console_channel


    def reset(self):
        self.memory.reset()
        self.overall_experience.reset()
        self.internal_experience.reset()
        # self.narsese_channel.reset()
        # self.perception_channel.reset()
        for channel in self.channels:
            channel.reset()

        self.sequence_buffer.reset()
        self.operations_buffer.reset()

    def cycles(self, n_cycle: int):
        tasks_all_cycles = []
        for _ in range(n_cycle):
            tasks_all_cycles.append(self.cycle())
        return tasks_all_cycles

    def run(self, paused=False):
        from time import sleep
        from pynput import keyboard
        from opennars.utils.Print import print_out, PrintType


        def on_ctrl_p():
            print_out(PrintType.COMMENT, 'Paused.', comment_title='\n\nNARS')
            print_out(PrintType.COMMENT, '', comment_title='Input', end='')
            self.paused = True

        def on_ctrl_r():
            if self.paused:
                print_out(PrintType.COMMENT, 'Running...', comment_title='\n\nNARS')
            self.paused = False

        self.paused = paused
        def run_console():
            try:
                with keyboard.GlobalHotKeys({'<ctrl>+r': on_ctrl_r}):
                    while True:
                        if not self.paused:
                            with keyboard.GlobalHotKeys({'<ctrl>+p': on_ctrl_p}) as listener:
                                while not self.paused:
                                    tasks = self.cycle()
                        sleep(0.1)
            except KeyboardInterrupt:
                print_out(PrintType.COMMENT, 'Stop...', comment_title='\n\nNARS')
                self.console_channel.terminated = True            
                exit()
                # console_channel.thread_console.join()
        thread_console = threading.Thread(target=run_console)
        thread_console.start()
        thread_console.join()

    def input_narsese(self, text, go_cycle: bool = False) -> Tuple[bool, Union[Task, None], Union[Task, None]]:
        success, task, task_overflow = self.narsese_channel.put(text)
        if go_cycle:
            tasks = self.cycle()
            return success, task, task_overflow, tasks
        return success, task, task_overflow

    def add_channel(self, channel: Channel):
        channel_id = len(self.channels)
        # self.channels[channel] = channel_id
        self.channels.append(channel)
        channel.channel_id = channel_id

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

        if self.record:
            if len(tasks_derived) > 0:
                logger.debug(
                    f"{{{Global.States.task}, {Global.States.belief}, {Global.States.term_belief}}} |- {tasks_derived}")

        ret =  tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed)
        Global.States.tasks_derived = ret

        for channel in self.channels:
            channel.on_cycle_finished()
        return ret
    
    @staticmethod
    def get_derived_tasks() -> Union[None, Tuple[
            List[Task],
            Task,
            Task,
            List[Task],
            List[Task],
            Tuple[Task, Task]]]:
        tasks = Global.States.tasks_derived
        return tasks
    

    def get_global_evaluations(self) -> Tuple[float, float, float, float]:
        return self.global_eval.S, self.global_eval.B, self.global_eval.A, self.global_eval.W

    def consider(self, tasks_derived: List[Task]):
        """
            Consider a Concept in the Memory
        """
        # step 4. Apply inference step
        #   general inference step
        concept: Concept = self.memory.take(remove=True)
        if concept is not None:
            tasks_inference_derived = self.inference.step(concept)
            tasks_derived.extend(tasks_inference_derived)

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
        '''register an operator and return the operator if successful (otherwise, return None)
        Args:
            name_operator: for example, `"left"`. Don't add `^` to the begining of the string.
            callback: for example, `my_callback`, where
                def my_callback(*args):
                    pass
        '''
        if not Operation.is_registered_by_name(name_operator):
            from opennars.Narsese import Operator as Op
            op = Op(name_operator)
            Operation.register(op, callback)
            return op
        return None

    def do_cycle_metrics(self, start_cycle_time_in_seconds: float):
        #  record some metrics
        total_cycle_duration_in_seconds = time() - start_cycle_time_in_seconds
        self.last_cycle_duration = total_cycle_duration_in_seconds  # store the cycle duration
        # calculate average
        self.cycles_count += 1
        self.avg_cycle_duration += (self.last_cycle_duration -
                                    self.avg_cycle_duration) / self.cycles_count
