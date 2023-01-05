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
        self.shown_content = False
        # ==============================================================================================================

    def register_channel(self, channel):  # register channels' operations
        tmp = set()
        for each_operation in channel.operations:
            tmp.add(each_operation)
            self.operation_of_channel.update({each_operation: channel})
        self.channel_of_operation.update({channel: tmp})

    def decompose(self, term: Term, agenda_pointer):
        # decompose complicated compound operations, including intervals
        ap = agenda_pointer
        if isinstance(term, Compound):
            for each_component in term.terms:
                if isinstance(each_component, Interval):
                    ap += each_component.interval
                elif isinstance(each_component, Compound):
                    self.decompose(each_component, ap)
                else:
                    for each_operation in self.operation_of_channel:
                        if each_component.equal(each_operation) and ap < self.agenda_length:  # only store operations
                            self.agenda[ap].append(each_component)
                            break
        else:
            self.agenda[ap].append(term)

    def distribute_execute(self):  # distribute the decomposed operations into corresponding channels
        for each_operation in self.agenda[0]:
            corresponding_channel = self.operation_of_channel[Term("^" + each_operation.word)]
            corresponding_channel.execute(Term("^" + each_operation.word))  # operation execution
            corresponding_channel.event_buffer.slots[corresponding_channel.event_buffer.present].update_operations(
                Term("^" + each_operation.word))  # operation execution record added
        self.agenda = {i: self.agenda[i + 1] for i in range(self.agenda_length - 1)}
        self.agenda.update({self.agenda_length - 1: []})

    def UI_show(self):
        self.T.configure(state="normal")  # enable inputting

        # show active questions
        for each in self.active_questions:
            BT, word, _ = UI_better_content(each[0])
            if each[1] == "updated":
                self.T.insert(tk.END, "[Question updated]: " + BT)
                self.T.insert(tk.END, word, "tag_2_updated")
                self.shown_content = True
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Question found]: " + BT)
                self.T.insert(tk.END, word, "tag_2")
                self.shown_content = True
            elif each[1] == "derived":
                self.T.insert(tk.END, "[Question derived]: " + BT)
                self.T.insert(tk.END, word, "tag_2_updated")
                self.shown_content = True
            each[1] = ""

        # show active goals
        for each in self.active_goals:
            BT, word, _ = UI_better_content(each[0])
            AL = str(each[0].achieving_level())[:4] + "\n"
            if each[1] == "updated":
                self.T.insert(tk.END, "[Goal updated]: " + BT)
                self.T.insert(tk.END, "Achieving level: " + AL)
                self.T.insert(tk.END, word, "tag_2_updated")
                self.shown_content = True
            elif each[1] == "initialized":
                self.T.insert(tk.END, "[Goal found]: " + BT)
                self.T.insert(tk.END, "Achieving level: " + AL)
                self.T.insert(tk.END, word, "tag_2")
                self.shown_content = True
            elif each[1] == "derived":
                self.T.insert(tk.END, "[Goal derived]: " + BT)
                self.T.insert(tk.END, "Achieving level: " + AL)
                self.T.insert(tk.END, word, "tag_2_updated")
                self.shown_content = True
            each[1] = ""

        if self.shown_content:
            self.T.insert(tk.END, "=" * 79 + "\n")
            self.shown_content = False
        self.T.configure(state="disabled")  # disable user input

    def step(self, task: Task):
        """
        This function is used to distribute "operations" from the internal buffer to the event buffer.
        One operation goal is firstly generated in the inference engine. After that, it will be forwarded to the
        internal buffer, and if this task is further forwarded to the global buffer, this task will be viewed as
        "executed". And it is also really executed, which might be reflected in the information gathered by the
        corresponding event buffer. And it is possible for the global buffer to generate "procedural knowledge".

        Since such operation is executed by the event buffer, it also needs to be "percepted" by the event buffer.
        And so in event buffers, it is also possible to generate such "procedural knowledge".

        In short, this function will execute the operation goal selected from the internal buffer and let the
        corresponding event buffer know.
        """
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
