import ctypes
import tkinter as tk
import tkinter.font as tkFont
from copy import deepcopy
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import numpy as np

from opennars.NAL.Functions import Stamp_merge, Budget_merge, Truth_induction, Truth_deduction
from opennars.NARS.DataStructures import Memory
from opennars.NARS.DataStructures.MC.AnticipationMC import AnticipationMC
from opennars.NARS.DataStructures.MC.SlotMC import SlotMC
from opennars.Narsese import Compound, Task, Judgement, Interval, Statement, Copula


# the priority value of predictions (predictive implications)
def p_value(t: Task):
    return t.budget.summary * t.truth.e / t.term.complexity ** 2


def UI_better_content(task: Task):
    """
    A function to help generate UI output.
    Make it not just plain texts.
    Since each buffer (event buffer, internal buffer, global buffer) will have an independent UI page.
    """
    budget = "$" + str(task.budget.priority)[:4] + ";" + str(task.budget.durability)[:4] + ";" + str(
        task.budget.quality)[:4] + "$ | "
    word = "".join(task.sentence.word.split(" ")) + "\n"
    end = "=" * 41 + "\n"
    word.replace("-->", "->")
    word.replace("==>", "=>")
    if task.truth is not None:
        truth = "% " + str(task.truth.f)[:4] + ";" + str(task.truth.c)[:4] + "%\n"
        return [budget + truth, word, end]
    else:
        return [budget + "\n", word, end]


class InputBufferMC(object):
    """
    The super class of all input buffers (event buffer, internal buffer, global buffer).
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_operation, num_prediction, memory: Memory, root_UI,
                 UI_name):
        self.num_slot = num_slot * 2 + 1
        self.present = num_slot

        self.num_event = num_event
        self.num_anticipation = num_anticipation
        self.num_operation = num_operation
        self.num_prediction = num_prediction

        self.memory = memory
        self.prediction_table = []
        self.slots = [SlotMC(num_event, num_anticipation, num_operation) for _ in range(self.num_slot)]

        # GUI
        # ==============================================================================================================
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # auto-resolution rate
        SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)

        self.top = tk.Toplevel(root_UI, width=160, height=50)  # top canvas created
        self.top.title(UI_name)
        self.top.tk.call("tk", "scaling", SF / 75)

        self.notebook = ttk.Notebook(self.top)  # notebook created
        self.notebook.pack(pady=10, padx=10, expand=True)
        # each time slot has one page on the notebook
        self.P = {}  # reference of all notebook pages
        self.contents_UI = []  # reference of the content of each notebook page
        for i in range(self.num_slot):
            P_i = ttk.Frame(self.notebook, width=160, height=50)  # notebook page created
            self.contents_UI.append({"historical_compound": [],
                                     "concurrent_compound": [],
                                     "anticipation": [],
                                     "prediction": []})
            P_i.pack(fill="both", expand=True)
            self.notebook.add(P_i, text="Slot [" + str(i - self.present) + "]     ")

            # frames of each part on the page
            F_1 = tk.LabelFrame(P_i, width=41, height=50, text="Historical Compound")  # frame created on the page
            F_2 = tk.LabelFrame(P_i, width=41, height=50, text="Concurrent Compound")
            F_3 = tk.LabelFrame(P_i, width=41, height=50, text="Anticipation")
            F_4 = tk.LabelFrame(P_i, width=41, height=50, text="Prediction")
            F_1.pack(side=tk.LEFT)
            F_2.pack(side=tk.LEFT)
            F_3.pack(side=tk.LEFT)
            F_4.pack(side=tk.LEFT)
            Font = tkFont.Font(family="monaco", size=8)
            T_1 = ScrolledText(F_1, width=41, height=50, font=Font)  # scrolled text created on the frame
            T_2 = ScrolledText(F_2, width=41, height=50, font=Font)
            T_3 = ScrolledText(F_3, width=41, height=50, font=Font)
            T_4 = ScrolledText(F_4, width=41, height=50, font=Font)
            T_1.pack(side=tk.RIGHT)
            T_2.pack(side=tk.RIGHT)
            T_3.pack(side=tk.RIGHT)
            T_4.pack(side=tk.RIGHT)
            T_1.insert(tk.END, "=" * 18 + "READY" + "=" * 18)  # initialization reminder
            T_2.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_3.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_4.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_1.configure(state="disabled")  # disable user input (just for display)
            T_2.configure(state="disabled")
            T_3.configure(state="disabled")
            T_4.configure(state="disabled")
            self.P.update({P_i: [T_1, T_2, T_3, T_4]})
        # ==============================================================================================================

    def update_prediction(self, p: Task):
        for i in range(len(self.prediction_table)):  # delete if existed
            if self.prediction_table[i].term == p.term:
                del self.prediction_table[i]
                break
        P = p_value(p)
        added = False
        # large to small
        for i in range(len(self.prediction_table)):
            if P > p_value(self.prediction_table[i]):
                self.prediction_table = self.prediction_table[:i] + [p] + self.prediction_table[i:]
                added = True
                break
        if not added:  # smallest
            self.prediction_table = self.prediction_table + [p]
        if len(self.prediction_table) > self.num_prediction:
            self.prediction_table = self.prediction_table[:-1]

    def combination(self, lst, start, num, tmp, cpds):
        """
        Compound utility function.
        """
        if num == 0:
            cpds.append(deepcopy(tmp))
            return
        elif len(lst) - start < num:
            return
        else:
            tmp.append(lst[start])
            self.combination(lst, start + 1, num - 1, tmp, cpds)
            self.combination(lst[:-1], start + 1, num, tmp, cpds)

    def concurrent_compound_generation(self, new_contents, origin = ""):
        """
        Each buffer will have a compound generation process, and this process is exactly the same. Though in some
        buffers, a part of the process is skipped due to blank inputs.

        For example, in event buffers, usually this step will be skipped since there are only one event at each time.
        """
        if new_contents is None:
            return
        for new_content in new_contents:
            self.slots[self.present].update_events(new_content)
        # check atomic anticipations
        self.slots[self.present].check_anticipation(self)

        # concurrent compounds generation
        compounds = []
        for i in range(len(self.slots[self.present].events)):
            self.combination(self.slots[self.present].events[:, 1], 0, i + 1, [], compounds)
        for each_compound in compounds:
            if len(each_compound) > 1:
                # term generation
                each_compound_term = [each.term for each in each_compound]
                term = Compound.ParallelEvents(*each_compound_term)
                # truth, using truth-induction function (TODO, may subject to change)
                truth = each_compound[0].truth
                for each in each_compound[1:]:
                    truth = Truth_induction(truth, each.truth)
                # stamp, using stamp-merge function (TODO, may subject to change)
                stamp = each_compound[0].stamp
                for each in each_compound[1:]:
                    stamp = Stamp_merge(stamp, each.stamp)
                # budget, using budget-merge function (TODO, may subject to change)
                budget = each_compound[0].budget
                for each in each_compound[1:]:
                    budget = Budget_merge(budget, each.budget)
                # sentence composition
                sentence = Judgement(term, stamp, truth)
                # task generation
                task = Task(sentence, budget)
                self.slots[self.present].update_events(task)
            else:
                self.slots[self.present].update_events(each_compound[0])
        # check concurrent compound anticipations
        self.slots[self.present].check_anticipation(self)

    def historical_compound_generation(self, origin = ""):
        """
        Previously, this is achieved by a DP-like process, but currently it is achieved by exhaustion.

        It happens among all the present concurrent compound and all "previous candidates", like finding a sub-string.
        Note that one current event may not be included.
        """
        if self.slots[self.present].events is None:
            return
        for i in range(len(self.slots[self.present].events)):
            # there might be "None" in tmp_list
            tmp_list = [self.slots[i].candidate for i in range(self.present)] + [self.slots[self.present].events[i][1]]
            for j in range(1, 2 ** (self.present + 1)):  # enumeration, actually this is a process finding sub-strings
                # a binary coding is used to find the sub-string
                j_binary_str = list(("{:0" + str(self.present + 1) + "b}").format(j))
                j_binary_boolean = [False if each == "0" else True for each in j_binary_str]
                cpd = []
                for k, each in enumerate(j_binary_boolean):
                    if not each:
                        cpd.append(1)
                    elif tmp_list[k] is not None:
                        cpd.append(tmp_list[k])
                    else:
                        cpd.append(1)
                # for example
                # tmp_list: [None, None, A, None, None, B, C]
                # i_binary_boolean: [False, False, True, True, True, True, False]
                # cpd: [1, 1, A, 1, 1, B, 1], remove the 1's at the beginning and ending
                while True:
                    if len(cpd) != 0 and cpd[0] == 1:
                        cpd = cpd[1:]
                    else:
                        break
                # cpd: [A, 1, 1, B, 1], or []
                if len(cpd) != 0:
                    while True:
                        if cpd[-1] == 1:
                            cpd = cpd[:-1]
                        else:
                            break
                # cpd: [A, 1, 1, B], cpd is a list of tasks, merge adjacent intervals next
                cpd_term = []
                if len(cpd) != 0:
                    interval = 0
                    for k, each in enumerate(cpd):
                        if each != 1:
                            if interval != 0:
                                cpd_term.append(Interval(interval))
                                interval = 0
                            cpd_term.append(each.term)  # each isType Task
                        else:
                            interval += 1
                # cpd_term: [A.term, Interval(2), B.term] or [] TODO: ugly, but work :\

                if len(cpd_term) != 0:
                    term = Compound.SequentialEvents(*cpd_term)
                    truth = cpd[0].truth
                    stamp = cpd[0].stamp
                    budget = cpd[0].budget
                    for each in cpd[1:]:
                        if each != 1:
                            # truth, using truth-induction function (TODO, may subject to change)
                            truth = Truth_induction(truth, each.truth)
                            # stamp, using stamp-merge function (TODO, may subject to change)
                            stamp = Stamp_merge(stamp, each.stamp)
                            # budget, using budget-merge function (TODO, may subject to change)
                            budget = Budget_merge(budget, each.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    self.slots[self.present].update_events(task)

            # checking historical events is moved to the end of local_evaluation

    def local_evaluation(self):
        # generate anticipation
        for each_prediction in self.prediction_table:

            # predictions may be like "(&/, A, +1) =/> B", the content of the subject will just be A
            # if it is "(&/, A, +1, B) =/> C", no need to change the subject
            interval = 0
            if isinstance(each_prediction.term.subject.terms[-1], Interval):
                subject = Compound.SequentialEvents(*each_prediction.term.subject.terms[:-1])  # condition
                interval = int(each_prediction.term.subject.terms[-1])
            else:
                subject = each_prediction.term.subject

            for each_event in self.slots[self.present].events:
                if subject.equal(each_event[1].term):
                    # term generation
                    term = each_prediction.term.predicate
                    # truth, using truth-deduction function (TODO, may subject to change)
                    truth = Truth_deduction(each_prediction.truth, each_event[1].truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(each_prediction.stamp, each_event[1].stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(each_prediction.budget, each_event[1].budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    # anticipation generation
                    anticipation = AnticipationMC(task, each_prediction)
                    if interval <= self.present:
                        self.slots[self.present + interval].update_anticipations(anticipation)

        # check anticipations with un-expectation handling (non-anticipation events)
        self.slots[self.present].check_anticipation(self, mode_unexpected=True)

        # unsatisfied anticipation handling
        for each_anticipation in self.slots[self.present].anticipations:
            if not self.slots[self.present].anticipations[each_anticipation].solved:
                self.slots[self.present].anticipations[each_anticipation].unsatisfied(self)

    def memory_based_evaluations(self):
        """
        Find whether a concept is already in the main memory. If so, merger the budget.
        """
        events_updates = []

        for each_event in self.slots[self.present].events:
            tmp = self.memory.concepts.take_by_key(each_event[1].term, remove=False)
            if tmp is not None:
                budget = Budget_merge(each_event[1].budget, tmp.budget)
                task = Task(each_event[1].sentence, budget)
                events_updates.append(task)
        for each_event in events_updates:
            self.slots[self.present].update_events(each_event)

        # find the highest concurrent compound, namely the candidate
        # sorting first
        if len(self.slots[self.present].events) != 0:
            self.slots[self.present].events = self.slots[self.present].events[
                np.argsort(self.slots[self.present].events[:, 2])]
            self.slots[self.present].candidate = self.slots[self.present].events[-1][1]

    def prediction_generation(self):
        # =/>
        if self.slots[self.present].candidate is not None:
            predicate = self.slots[self.present].candidate.term
            for i in range(self.present):
                if self.slots[i].candidate:
                    # e.g., (E, +1) as the subject
                    subject = Compound.SequentialEvents(self.slots[i].candidate.term, Interval(abs(self.present - i)))
                    copula = Copula.PredictiveImplication  # =/>
                    term = Statement(subject, copula, predicate)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth,
                                            self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp,
                                        self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget,
                                          self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        return self.slots[self.present].candidate

    def reset(self):
        self.slots = [SlotMC(self.num_event, self.num_anticipation, self.num_operation) for _ in range(self.num_slot)]
        self.prediction_table = []
        self.contents_UI = []
        for i in range(self.num_slot):
            self.contents_UI.append({"historical_compound": [],
                                     "concurrent_compound": [],
                                     "anticipation": [],
                                     "prediction": []})
        for each in self.P:
            T_1, T_2, T_3, T_4 = self.P[each]
            T_1.configure(state="normal")
            T_2.configure(state="normal")
            T_3.configure(state="normal")
            T_4.configure(state="normal")
            T_1.delete("1.0", "end")
            T_2.delete("1.0", "end")
            T_3.delete("1.0", "end")
            T_4.delete("1.0", "end")
            T_1.insert(tk.END, "=" * 18 + "READY" + "=" * 18)  # initialization reminder
            T_2.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_3.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_4.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
            T_1.configure(state="disabled")  # disable user input
            T_2.configure(state="disabled")
            T_3.configure(state="disabled")
            T_4.configure(state="disabled")

    def UI_roll(self):
        self.contents_UI = self.contents_UI[1:]
        self.contents_UI.append({"historical_compound": [],
                                 "concurrent_compound": [],
                                 "anticipation": [],
                                 "prediction": []})

    def UI_show_single_page(self, P_i, content_UI):
        T_1, T_2, T_3, T_4 = self.P[P_i][0], self.P[P_i][1], self.P[P_i][2], self.P[P_i][3]

        # add tags
        Font = tkFont.Font(family="monaco", size=8, weight="bold")
        T_1.tag_config("tag_1", font=Font)  # for the word of each task
        T_1.tag_config("tag_2", foreground="red")  # for the budget and truth-value
        T_2.tag_config("tag_1", font=Font)
        T_2.tag_config("tag_2", foreground="red")
        T_3.tag_config("tag_1", font=Font)
        T_3.tag_config("tag_2", foreground="red")
        T_4.tag_config("tag_1", font=Font)
        T_4.tag_config("tag_2", foreground="red")

        T_1.configure(state="normal")  # enable inputting
        T_2.configure(state="normal")
        T_3.configure(state="normal")
        T_4.configure(state="normal")
        T_1.delete("1.0", "end")  # delete old contents
        T_2.delete("1.0", "end")
        T_3.delete("1.0", "end")
        T_4.delete("1.0", "end")

        for each in content_UI["historical_compound"]:
            if each is not None and len(each) != 0:
                BT, word, end = each[0], each[1], each[2]
                T_1.insert(tk.END, BT, "tag_2")
                T_1.insert(tk.END, word, "tag_1")
                T_1.insert(tk.END, end)

        for each in content_UI["concurrent_compound"]:
            if each is not None and len(each) != 0:
                BT, word, end = each[0], each[1], each[2]
                T_2.insert(tk.END, BT, "tag_2")
                T_2.insert(tk.END, word, "tag_1")
                T_2.insert(tk.END, end)

        for each in content_UI["anticipation"]:
            if each is not None and len(each) != 0:
                BT, word, end = each[0], each[1], each[2]
                T_3.insert(tk.END, BT, "tag_2")
                T_3.insert(tk.END, word, "tag_1")
                T_3.insert(tk.END, end)

        for each in content_UI["prediction"]:
            if each is not None and len(each) != 0:
                BT, word, end = each[0], each[1], each[2]
                T_4.insert(tk.END, BT, "tag_2")
                T_4.insert(tk.END, word, "tag_1")
                T_4.insert(tk.END, end)

        T_1.configure(state="disabled")  # disable user input
        T_2.configure(state="disabled")
        T_3.configure(state="disabled")
        T_4.configure(state="disabled")

    def UI_content_update(self):
        for i in range(self.num_slot):
            self.contents_UI[i].update({"historical_compound": [],
                                        "concurrent_compound": [UI_better_content(each[1]) for each in
                                                                self.slots[i].events],
                                        "anticipation": [UI_better_content(self.slots[i].anticipations[each].t) for each
                                                         in self.slots[i].anticipations],
                                        "prediction": [UI_better_content(each) for each in
                                                       self.prediction_table]})

    def UI_show(self):
        for i, each in enumerate(self.P):
            self.UI_show_single_page(each, self.contents_UI[i])
