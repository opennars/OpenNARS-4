import ctypes
import tkinter as tk
from typing import List

from ..DataStructures.MC.SampleChannels.SampleChannel3 import SampleChannel3
from ...Narsese import parser
import tkinter.font as tkFont
from pynars import Config, Global
import pynars.NARS.Operation as Operation
from ..InferenceEngine import GeneralEngine
from tkinter.scrolledtext import ScrolledText
from ..DataStructures import Memory, Task, Concept
from ..DataStructures.MC.ChannelMC import ChannelMC
from ..DataStructures.MC.GlobalBufferMC import GlobalBufferMC
from ..DataStructures.MC.OutputBufferMC import OutputBufferMC
from ..DataStructures.MC.InternalBufferMC import InternalBufferMC
from ..DataStructures.MC.SampleChannels.SampleChannel2 import SampleChannel2
from ..DataStructures.MC.SampleChannels.SampleEnvironment1 import SampleEnvironment1


class ReasonerMC:

    def __init__(self, n_memory, config = './config.json') -> None:
        Config.load(config)
        self.inference = GeneralEngine()

        # GUI
        # ==============================================================================================================
        self.root = tk.Tk()
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # scaling for any resolution rates
        SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.root.tk.call("tk", "scaling", SF / 75)

        # the frame for the output box
        self.F_1 = tk.LabelFrame(self.root, width=79, height=30, text="Output")
        # the frane for the interacting box, has two parts, 1) user input, 2) buttons
        self.F_2 = tk.LabelFrame(self.root, width=69, height=10, text="Input")
        # sub-frame for the user input
        self.F_21 = tk.Frame(self.F_2, width=75, height=10)
        # sub-frame for buttons
        self.F_22 = tk.Frame(self.F_2, width=4, height=10)

        self.F_1.pack(side=tk.TOP)
        self.F_2.pack(side=tk.TOP)
        self.F_21.pack(side=tk.LEFT)
        self.F_22.pack(side=tk.LEFT)

        Font = tkFont.Font(family="monaco", size=8)
        self.T = ScrolledText(self.F_1, width=79, height=30, font=Font)
        self.T.tag_config("tag_1", background="#D5D5D5")  # gray background, used for immediate user input responses
        # tag_2's are for immediate responses from inference, i.e., responses for questions/goals
        # plain background for the first update, yellow background for continue updates
        self.T.tag_config("tag_2", font=tkFont.Font(family="monaco", size=8, weight="bold"))
        self.T.tag_config("tag_2_updated", font=tkFont.Font(family="monaco", size=8, weight="bold"),
                          background="yellow")
        self.T.configure(state="disabled")  # disable user input

        self.E = tk.Text(self.F_21, width=75, height=10, font=Font)
        self.B_1 = tk.Button(self.F_22, text="Step", height=1, width=5, command=self.cycle, font=Font)
        self.B_2 = tk.Button(self.F_22, text="Enter", height=1, width=5, command=self.input_lines, font=Font)
        self.B_3 = tk.Button(self.F_22, text="Reset", height=1, width=5, command=self.reset, font=Font)
        self.B_4 = tk.Button(self.F_22, text="Clear", height=1, width=5, command=self.clear, font=Font)

        self.T.pack(side=tk.BOTTOM)
        self.E.pack(side=tk.LEFT, padx=1)
        self.B_1.pack(side=tk.TOP)
        self.B_2.pack(side=tk.TOP)
        self.B_3.pack(side=tk.TOP)
        self.B_4.pack(side=tk.TOP)

        self.root.title("PyNARS 0.0.2.MC Console")
        # ==============================================================================================================

        self.output_buffer = OutputBufferMC(self.T)
        self.memory = Memory(n_memory, output_buffer=self.output_buffer)
        env = SampleEnvironment1()
        self.channels: List[ChannelMC] = [
            # SampleChannel1("SC1", 3, 10, 10, 10, self.memory)
            SampleChannel2(3, 10, 10, 10, self.memory, env, self.root, "SC2"),
            SampleChannel3(3, 10, 10, 10, self.memory, env, self.root, "SC3")
        ]
        self.internal_buffer = InternalBufferMC(3, 10, 10, 10, self.memory, self.root, "Internal Buffer")
        self.global_buffer = GlobalBufferMC(3, 10, 10, 10, self.memory, self.root, "Global Buffer")
        for each_channel in self.channels:
            self.output_buffer.register_channel(each_channel)

    """
    collect the content in the input window; parse them into Narsese and process
    a task will be directly accept() by the main memory
    """

    def input_lines(self):
        t = self.E.get("1.0", "end")  # get content
        sentences = t.split("\n")
        sentences = list(filter(None, sentences))
        self.E.delete("1.0", "end")  # clear window
        have_content = False
        for each in sentences:
            if len(each) == 0:
                continue
            elif each.isdigit():  # digit input, run n cycles
                have_content = True
                self.T.configure(state="normal")  # enable inputting
                self.T.insert(tk.END, "Running " + each + " cycles. \n", "tag_1")
                self.T.configure(state="disabled")  # disable user input
                self.cycles(int(each))
            else:
                try:
                    task = parser.parse(each)
                except:
                    self.T.insert(tk.END, each + "PARSE ERROR! \n", "tag_1")
                    continue
                have_content = True
                self.T.configure(state="normal")
                self.T.insert(tk.END, "Task accepted: " + each + "\n", "tag_1")
                self.T.configure(state="disabled")
                self.memory.accept(task)

        self.T.configure(state="normal")
        if have_content:
            self.T.insert(tk.END, "=" * 79 + "\n")
        self.T.configure(state="disabled")

    """
    Everything in the buffers should be cleared: 1) slots, 2) prediction table, 3) operation agenda.
    """

    def reset(self):
        self.output_buffer.reset()
        self.internal_buffer.reset()
        self.global_buffer.reset()
        for each in self.channels:
            each.event_buffer.reset()

    def clear(self):
        self.T.configure(state="normal")
        self.T.delete("1.0", "end")  # clear window
        self.T.configure(state="disabled")

    def cycles(self, n_cycle: int):
        for _ in range(n_cycle):
            self.cycle()

    """
    Copied from Reasoner.py, all returns should be forwarded to InternalBufferMC.previous_inference_result
    """

    def mental_operation(self, task: Task, concept: Concept, answers_question: Task, answers_quest: Task):
        # handle the mental operations in NAL-9
        task_operation_return, task_executed, belief_aware = None, None, None

        # belief-awareness
        for answers in (answers_question, answers_quest):
            if answers is None:
                continue
            for answer in answers:
                belief_aware = Operation.aware__believe(answer)

        if task is not None:
            # question-awareness
            if task.is_question:
                belief_aware = Operation.aware__wonder(task)
            # quest-awareness
            elif task.is_quest:
                belief_aware = Operation.aware__evaluate(task)

        # execute mental operation
        if task is not None and task.is_executable:
            task_operation_return, task_executed = Operation.execute(task, concept, self.memory)

        return task_operation_return, task_executed, belief_aware

    """
    Everything to do by NARS in a single working cycle
    """

    def cycle(self):

        # step 1, take out a task from the internal buffer, and put it into the global buffer
        task_from_internal_buffer = self.internal_buffer.step(self.internal_buffer.previous_inference_result)

        # step 1.5, execute the task if executable
        self.output_buffer.step(task_from_internal_buffer)

        # step 2, Take out a task from each channel, and put it into the global buffer
        tasks_from_channels = []
        for each_channel in self.channels:
            tasks_from_channels.append(each_channel.step())

        # debugging information
        print(tasks_from_channels)
        print("==>")

        # step 2.5, merge the task from the internal buffer and the tasks from channels
        tasks_for_global_buffer = tasks_from_channels + [task_from_internal_buffer]
        tasks_for_global_buffer = list(filter(None, tasks_for_global_buffer))

        # step 3, feed these tasks to the global buffer and send the one from the global buffer to the main memory
        task_from_global_buffer = self.global_buffer.step(tasks_for_global_buffer)
        if task_from_global_buffer is not None:
            judgement_revised, goal_revised, answers_question, answers_quest = \
                self.memory.accept(task_from_global_buffer)

            if goal_revised is not None:
                exist = False
                for i in range(len(self.output_buffer.active_goals)):
                    if self.output_buffer.active_goals[i][0].term.equal(goal_revised.term):
                        self.output_buffer.active_goals = self.output_buffer.active_goals[:i] + [
                            [goal_revised, "updated"]] + self.output_buffer.active_goals[i:]
                        exist = True
                        break
                if not exist:
                    self.output_buffer.active_goals.append([goal_revised, "initialized"])
            if answers_question is not None and len(answers_question) != 0:
                for each in answers_question:
                    exist = False
                    for i in range(len(self.output_buffer.active_questions)):
                        if self.output_buffer.active_questions[i][0].term.equal(each.term):
                            self.output_buffer.active_questions = self.output_buffer.active_questions[:i] + [
                                [each, "updated"]] + self.output_buffer.active_questions[i:]
                            exist = True
                            break
                    if not exist:
                        self.output_buffer.active_questions.append([each, "initialized"])
            # temporally disabled
            # if answers_quest is not None:
            #     for i in range(len(self.output_buffer.active_quests)):
            #         if self.output_buffer.active_quests[i][0].term.equal(answers_quest.term):
            #             self.output_buffer.active_quests = self.output_buffer.active_quests[:i] + [
            #                 [answers_quest, "updated"]] + self.output_buffer.active_quests[i:]
            #             break

            # update inference results (by accepting one task into the main memory)
            if judgement_revised is not None:
                self.internal_buffer.update_inference_result(judgement_revised)
            if goal_revised is not None:
                self.internal_buffer.update_inference_result(goal_revised)
            if answers_question is not None:
                for answer in answers_question:
                    self.internal_buffer.update_inference_result(answer)
            # temporally disabled
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
            is_concept_valid = True
            if is_concept_valid:
                self.memory.put_back(concept)

        # mental operation
        task_operation_return, task_executed = None, None
        task_operation_return, task_executed, belief_aware = self.mental_operation(task_from_global_buffer,
                                                                                   concept,
                                                                                   answers_question,
                                                                                   answers_quest)
        if task_operation_return is not None:
            self.internal_buffer.update_inference_result(task_operation_return)
        if task_executed is not None:
            self.internal_buffer.update_inference_result(task_executed)
        if belief_aware is not None:
            self.internal_buffer.update_inference_result(belief_aware)

        self.output_buffer.UI_show()

        # handle the sense of time
        Global.time += 1

        return tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed)
