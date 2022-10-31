import tkinter as tk
from pynars.Narsese import Task, Compound, Interval, Term


def UI_better_content(task: Task):
    budget = "$" + str(task.budget.priority)[:4] + ";" + str(task.budget.durability)[:4] + ";" + str(
        task.budget.quality)[:4] + "$ | "
    word = "".join(task.sentence.word.split(" ")) + "\n"
    end = "=" * 79 + "\n"
    word.replace("-->", "->")
    word.replace("==>", "=>")
    if task.truth is not None:
        truth = "% " + str(task.truth.f)[:4] + ";" + str(task.truth.c)[:4] + "%\n"
        return [budget + truth, word, end]
    else:
        return [budget + "\n", word, end]


class OutputBufferMC:

    def __init__(self, T):
        self.agenda_length = 20
        self.operation_of_channel = {}
        self.channel_of_operation = {}
        self.agenda = {i: [] for i in range(self.agenda_length)}

        # GUI
        # ==============================================================================================================
        self.active_questions = []
        self.active_goals = []
        # self.active_quests = []
        self.T = T  # T is the text box in the main UI
        # ==============================================================================================================

    def register_channel(self, channel):  # register operations
        tmp = set()
        for each_operation in channel.operations:
            tmp.add(each_operation)
            self.operation_of_channel.update({each_operation: channel})
        self.channel_of_operation.update({channel: tmp})

    def decompose(self, term: Term, agenda_pointer):  # decompose complicated compound operations, including intervals
        ap = agenda_pointer
        if isinstance(term, Compound):
            for each_component in term.terms:
                if isinstance(each_component, Interval):
                    ap += each_component.interval
                elif isinstance(each_component, Compound):
                    self.decompose(each_component, ap)
                else:
                    for each_operation in self.operation_of_channel:
                        if each_component.equal(each_operation) and ap < self.agenda_length:  # only append operations
                            self.agenda[ap].append(each_component)
                            break
        else:
            self.agenda[ap].append(term)

    def distribute_execute(self):  # distribute the decomposed operations into corresponding channels
        for each_operation in self.agenda[0]:
            corresponding_channel = self.operation_of_channel[Term("^" + each_operation.word)]
            corresponding_channel.execute(Term("^" + each_operation.word))
        self.agenda = {i: self.agenda[i + 1] for i in range(self.agenda_length - 1)}
        self.agenda.update({self.agenda_length - 1: []})

    def UI_show(self):
        self.T.configure(state="normal")  # enable inputting

        # show active questions
        for each in self.active_questions:
            BT, word, _ = UI_better_content(each[0])
            if each[1] == "updated":
                self.T.insert(tk.END, "[Answer updated]: " + BT)
                self.T.insert(tk.END, word, "tag_2_updated")
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Answer found]: " + BT)
                self.T.insert(tk.END, word, "tag_2")
            each[1] = ""

        # show active goals
        for each in self.active_goals:
            BT, word, _ = UI_better_content(each[0])
            AL = str(each[0].achieving_level())[:4] + "\n"
            if each[1] == "updated":
                self.T.insert(tk.END, "[Goal updated]: " + BT)
                self.T.insert(tk.END, "Achieving level: " + AL)
                self.T.insert(tk.END, word, "tag_2_updated")
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Goal found]: " + BT)
                self.T.insert(tk.END, "Achieving level: " + AL)
                self.T.insert(tk.END, word, "tag_2")
            each[1] = ""

        self.T.configure(state="disabled")  # disable user input

    """
    This function mainly has two functions, 1) handling the operation goals, 2) showing these goals and questions.
    """
    def step(self, task: Task):
        # operation goal
        if task and task.is_goal:
            self.decompose(task.term, 0)
            self.distribute_execute()

    def reset(self):
        self.agenda = {i: [] for i in range(self.agenda_length)}
        self.T.configure(state="normal")
        self.T.delete("1.0", "end")  # clear window
        self.T.configure(state="disabled")
        self.active_questions = []
        self.active_goals = []
