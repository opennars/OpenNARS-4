from pynars.Narsese import Task, Compound, Interval, Term
import tkinter as tk


def UI_better_content(task: Task):
    budget = "%" + str(task.budget.priority)[:4] + ";" + str(task.budget.durability)[:4] + ";" + str(
        task.budget.quality)[:4] + "% | "
    word = "".join(task.sentence.word.split(" ")) + "\n"
    word.replace("-->", "->")
    word.replace("==>", "=>")
    if not task.is_goal:
        truth = str(task.truth.f)[:4] + ";" + str(task.truth.c)[:4] + "%\n"
    else:
        truth = None
    end = "=" * 79 + "\n"
    if not task.is_goal:
        return [budget + truth, word, end]
    else:
        return [budget + "\n", word, end]


class OutputBufferMC:

    def __init__(self, T):
        self.agenda_length = 20
        self.operation_of_channel = {}
        self.channel_of_operation = {}
        self.agenda = {i: [] for i in range(self.agenda_length)}
        # self.content_to_show = {"judgment revised": [],
        #                         "goal revised": [],
        #                         "answers questions": [],
        #                         "answers quest": []}

        # GUI
        self.active_questions = []
        self.active_goals = []
        # self.active_quests = []
        self.T = T

    def register_channel(self, channel):
        tmp = set()
        for each_operation in channel.operations:
            tmp.add(each_operation)
            self.operation_of_channel.update({each_operation: channel})
        self.channel_of_operation.update({channel: tmp})

    def decompose(self, term: Term, agenda_pointer):
        ap = agenda_pointer
        if isinstance(term, Compound):
            for each_component in term.terms:
                if isinstance(each_component, Interval):
                    ap += each_component.interval
                elif isinstance(each_component, Compound):
                    self.decompose(each_component, ap)
                else:
                    if ap < self.agenda_length:
                        self.agenda[ap].append(each_component)
        else:
            self.agenda[ap].append(term)

    def distribute_execute(self):
        for each_operation in self.agenda[0]:
            corresponding_channel = self.operation_of_channel[Term("^" + each_operation.word)]
            corresponding_channel.execute(Term("^" + each_operation.word))
        self.agenda = {i: self.agenda[i + 1] for i in range(self.agenda_length - 1)}
        self.agenda.update({self.agenda_length - 1: []})

    # def update_content_to_show(self, task: Task, tag: str):
    #     self.content_to_show.append(UI_better_content(task))

    def UI_show(self):
        self.T.configure(state="normal")
        for each in self.active_questions:
            BT, word, end = UI_better_content(each[0])
            if each[1] == "updated":
                self.T.insert(tk.END, "[Answer updated]: " + BT)
                self.T.insert(tk.END, word, "tag_2_updated")
                self.T.insert(tk.END, end)
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Answer found]: " + BT)
                self.T.insert(tk.END, word, "tag_2")
                self.T.insert(tk.END, end)
            each[1] = "X"
        for each in self.active_goals:
            BT, word, end = UI_better_content(each[0])
            if each[1] == "updated":
                self.T.insert(tk.END, "[Goal updated]: " + BT)
                self.T.insert(tk.END, word, "tag_2_updated")
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Goal found]: " + BT)
                self.T.insert(tk.END, word, "tag_2")
            each[1] = "X"
        self.T.configure(state="disabled")

    """
    This function mainly has two functions, 1) handling the operation goals, 2) showing these goals and questions.
    """

    def step(self, task: Task):
        # operation goal TODO, may need to change the source code of "Compound"
        if task and task.is_goal:
            self.decompose(task.term, 0)
            self.distribute_execute()
