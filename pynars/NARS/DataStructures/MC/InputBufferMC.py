import time
import ctypes
import tkinter as tk
from tkinter import ttk
from copy import deepcopy
import tkinter.font as tkFont
from tkinter.scrolledtext import ScrolledText

import numpy as np

from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
from pynars.NARS.DataStructures.MC.AnticipationMC import AnticipationMC
from pynars.NARS.DataStructures.MC.SlotMC import p_value as p_value_events
from pynars.Narsese import Compound, Task, Judgement, Interval, Statement, Copula
from pynars.NAL.Functions import Stamp_merge, Budget_merge, Truth_induction, Truth_deduction


# the priority value of predictions
def p_value(t: Task):
    return t.budget.priority * t.truth.f / t.term.complexity + np.random.rand() / 20


def UI_better_content(task: Task):
    budget = "$" + str(task.budget.priority)[:4] + ";" + str(task.budget.durability)[:4] + ";" + str(
        task.budget.quality)[:4] + "$ | "
    word = "".join(task.sentence.word.split(" ")) + "\n"
    end = "=" * 41 + "\n"
    word.replace("-->", "->")
    word.replace("==>", "=>")
    if task.truth is not None:
        truth = "% " + str(task.truth.f)[:4] + ";" + str(task.truth.c)[:4] + "%"
        P = p_value(task)
        return [budget + truth + " | " + str(P)[:4] + "\n", word, end]
    else:
        return [budget + "\n", word, end]


class InputBufferMC(object):
    """
    The super class of all input buffers (event buffer, internal buffer, global buffer).
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory, root_UI, UI_name):
        self.num_slot = num_slot * 2 + 1
        self.present = num_slot
        self.num_event = num_event
        self.num_anticipation = num_anticipation
        self.num_prediction = num_prediction

        self.memory = memory
        self.prediction_table = []
        self.slots = [SlotMC(num_event, num_anticipation) for _ in range(self.num_slot)]

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
            self.contents_UI[i].update({"historical_compound": [UI_better_content(each[1]) for each in
                                                                self.slots[i].events_historical],
                                        "concurrent_compound": [UI_better_content(each[1]) for each in
                                                                self.slots[i].events],
                                        "anticipation": [UI_better_content(self.slots[i].anticipations[each].t) for each
                                                         in self.slots[i].anticipations],
                                        "prediction": [UI_better_content(each) for each in
                                                       self.prediction_table]})

    def UI_show(self):
        for i, each in enumerate(self.P):
            self.UI_show_single_page(each, self.contents_UI[i])

    def update_prediction(self, p: Task):
        for i in range(len(self.prediction_table)):
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

    """
    Compound utility function.
    """

    def combination(self, lst, start, num, tmp, cpds):
        if num == 0:
            cpds.append(deepcopy(tmp))
            return
        elif len(lst) - start < num:
            return
        else:
            tmp.append(lst[start])
            self.combination(lst, start + 1, num - 1, tmp, cpds)
            self.combination(lst[:-1], start + 1, num, tmp, cpds)

    def compound_generation(self, new_contents, origin = ""):
        if new_contents is None:
            return
        for new_content in new_contents:
            self.slots[self.present].update_events(new_content)
        # check atomic anticipations
        A = time.time()
        self.slots[self.present].check_anticipation(self)
        B = time.time()

        # concurrent compounds generation
        compounds = []
        for i in range(len(self.slots[self.present].events)):
            self.combination(self.slots[self.present].events[:, 1], 0, i + 1, [], compounds)
        C = time.time()
        for each_compound in compounds:
            if len(each_compound) > 1:
                # term generation
                each_compound_term = [each.term for each in each_compound]
                term = Compound.ParallelEvents(*each_compound_term)

                # avoid duplicate compounds, when there are duplicates, only save the highest one
                # temporally disabled to save some time
                # existed = False
                # existed_p = 0
                # for each_existed_event in self.slots[self.present].events:
                #     if each_existed_event.term.equal(term):
                #         existed = True
                #         existed_p = p_value(each_existed_event)
                #         break

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

                # temporally disabled to save some time
                # if not existed:
                #     self.slots[self.present].update_events(task)
                # elif p_value(task) > existed_p:
                #     self.slots[self.present].update_events(task)

            else:
                self.slots[self.present].update_events(each_compound[0])
        D = time.time()
        # check concurrent compound anticipations
        self.slots[self.present].check_anticipation(self)

        # historical compounds generation
        E = time.time()
        for i in range(self.present):

            previous_event_concurrent = self.slots[i].highest_compound
            if previous_event_concurrent:
                for each_event in self.slots[self.present].events:
                    # term generation
                    term = Compound.SequentialEvents(previous_event_concurrent.term, Interval(abs(self.present - i)),
                                                     each_event[1].term)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(previous_event_concurrent.truth, each_event[1].truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(previous_event_concurrent.stamp, each_event[1].stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(previous_event_concurrent.budget, each_event[1].budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    self.slots[self.present].update_events_historical(task)

            previous_compound_historical = self.slots[i].highest_compound_historical
            if previous_compound_historical:
                for each_event in self.slots[self.present].events:
                    # term generation
                    term = Compound.SequentialEvents(previous_compound_historical.term, Interval(abs(self.present - i)),
                                                     each_event[1].term)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(previous_compound_historical.truth, each_event[1].truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(previous_compound_historical.stamp, each_event[1].stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(previous_compound_historical.budget, each_event[1].budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    self.slots[self.present].update_events_historical(task)

        # check historical compound anticipations
        F = time.time()
        # if origin == "X":
        #     print(origin + "1: {:.2f} second".format(B - A))
        #     print(origin + "2: {:.2f} second".format(C - B))
        #     print(origin + "3: {:.2f} second".format(D - C))
        #     print(origin + "4: {:.2f} second".format(E - D))
        #     print(origin + "5: {:.2f} second".format(F - E))
        #     print("==")

        self.slots[self.present].check_anticipation(self)

    def local_evaluation(self):
        # generate anticipation
        for each_prediction in self.prediction_table:
            # predictions may be like "(&/, A, +1) =/> B", the content of the subject will just be A
            interval = 0
            if isinstance(each_prediction.term.subject.terms[-1], Interval):
                subject = Compound.SequentialEvents(*each_prediction.term.subject.terms[:-1])
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
                    if interval <= self.present:  # avoid time slots overflow
                        self.slots[self.present + interval].update_anticipation(anticipation)

            for each_event_historical in self.slots[self.present].events_historical:
                if subject.equal(each_event_historical[1].term):
                    # term generation
                    term = each_prediction.term.predicate
                    # truth, using truth-deduction function (TODO, may subject to change)
                    truth = Truth_deduction(each_prediction.truth, each_event_historical[1].truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(each_prediction.stamp, each_event_historical[1].stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(each_prediction.budget, each_event_historical[1].budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    # anticipation generation
                    anticipation = AnticipationMC(task, each_prediction)
                    if interval <= self.present:
                        self.slots[self.present + interval].update_anticipation(anticipation)

        # check anticipations with un-expectation handling (non-anticipation events)
        self.slots[self.present].check_anticipation(self, mode_unexpected=True)

        # unsatisfied anticipation handling
        for each_anticipation in self.slots[self.present].anticipations:
            if not self.slots[self.present].anticipations[each_anticipation].solved:
                self.slots[self.present].anticipations[each_anticipation].unsatisfied(self)
            # if not each_anticipation.solved:
            #     each_anticipation.unsatisfied(self)

    """
    Find whether a concept is already in the main memory. If so, merger the budget.
    """

    def memory_based_evaluations(self):
        events_updates = []
        events_historical_updates = []

        for each_event in self.slots[self.present].events:
            tmp = self.memory.concepts.take_by_key(each_event[1].term, remove=False)
            if tmp is not None:
                budget = Budget_merge(each_event[1].budget, tmp.budget)
                task = Task(each_event[1].sentence, budget)
                events_updates.append(task)
        for each_event_historical in self.slots[self.present].events_historical:
            tmp = self.memory.concepts.take_by_key(each_event_historical[1].term, remove=False)
            if tmp is not None:
                budget = Budget_merge(each_event_historical[1].budget, tmp.budget)
                task = Task(each_event_historical[1].sentence, budget)
                events_historical_updates.append(task)
        for each_event in events_updates:
            self.slots[self.present].update_events(each_event)
        for each_event_historical in events_historical_updates:
            self.slots[self.present].update_events_historical(each_event_historical)

        # find the highest concurrent/historical compound
        if len(self.slots[self.present].events) != 0:
            self.slots[self.present].events = self.slots[self.present].events[
                np.argsort(self.slots[self.present].events[:, 2])]
            self.slots[self.present].highest_compound = self.slots[self.present].events[-1][1]
        if len(self.slots[self.present].events_historical) != 0:
            self.slots[self.present].events_historical = self.slots[self.present].events_historical[
                np.argsort(self.slots[self.present].events_historical[:, 2])]
            self.slots[self.present].highest_compound_historical = self.slots[self.present].events_historical[-1][1]
        if len(self.slots[self.present].events) != 0 and len(self.slots[self.present].events_historical) != 0:
            if p_value_events(self.slots[self.present].highest_compound) > \
                    p_value_events(self.slots[self.present].highest_compound_historical):
                self.slots[self.present].candidate = self.slots[self.present].highest_compound
            else:
                self.slots[self.present].candidate = self.slots[self.present].highest_compound_historical
        elif len(self.slots[self.present].events) != 0:
            self.slots[self.present].candidate = self.slots[self.present].highest_compound
        elif len(self.slots[self.present].events_historical) != 0:
            self.slots[self.present].candidate = self.slots[self.present].highest_compound_historical

    def prediction_generation(self):
        # =/>
        if self.slots[self.present].candidate:
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

    def step(self, new_contents, origin = ""):
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation))

        A = time.time()
        self.compound_generation(new_contents, origin)  # 1st step
        B = time.time()
        self.local_evaluation()  # 2nd step
        C = time.time()
        self.memory_based_evaluations()  # 3rd step
        D = time.time()
        task_forward = self.prediction_generation()  # 4th step
        E = time.time()

        # GUI
        # ==============================================================================================================
        self.UI_roll()
        self.UI_content_update()
        self.UI_show()
        F = time.time()
        # ==============================================================================================================

        # if origin == "internal":
        #     print(origin + "1: {:.2f} second".format(B - A))
        #     print(origin + "2: {:.2f} second".format(C - B))
        #     print(origin + "3: {:.2f} second".format(D - C))
        #     print(origin + "4: {:.2f} second".format(E - D))
        #     print(origin + "5: {:.2f} second".format(F - E))
        #     print("==")

        return task_forward

    def reset(self):
        self.slots = [SlotMC(self.num_event, self.num_anticipation) for _ in range(self.num_slot)]
        self.contents_UI = []
        for i in range(self.num_slot):
            self.contents_UI.append({"historical_compound": [],
                                     "concurrent_compound": [],
                                     "anticipation": [],
                                     "prediction": []})
        self.UI_content_update()
        self.UI_show()
        # for each in self.P:
        #     T_1, T_2, T_3, T_4 = self.P[each]
        #     T_1.configure(state="normal")
        #     T_2.configure(state="normal")
        #     T_3.configure(state="normal")
        #     T_4.configure(state="normal")
        #     T_1.delete("1.0", "end")
        #     T_2.delete("1.0", "end")
        #     T_3.delete("1.0", "end")
        #     T_4.delete("1.0", "end")
        #     T_1.insert(tk.END, "=" * 18 + "READY" + "=" * 18)  # initialization reminder
        #     T_2.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
        #     T_3.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
        #     T_4.insert(tk.END, "=" * 18 + "READY" + "=" * 18)
        #     T_1.configure(state="disabled")  # disable user input
        #     T_2.configure(state="disabled")
        #     T_3.configure(state="disabled")
        #     T_4.configure(state="disabled")
