from pynars.Narsese import Task, Compound, Interval, Term


class OutputBufferMC:

    def __init__(self):
        self.agenda_length = 20
        self.operation_of_channel = {}
        self.channel_of_operation = {}
        self.agenda = {i: [] for i in range(self.agenda_length)}

    def register_channel(self, channel):
        tmp = set()
        for each_operation in channel.operations:
            tmp.add(each_operation)
            self.operation_of_channel.update({each_operation: channel})
        self.channel_of_operation.update({channel: tmp})

    def decompose(self, term: Term, agenda_pointer):
        ap = agenda_pointer
        if isinstance(term, Compound):
            for each_component in term.components:
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
            corresponding_channel = self.operation_of_channel[each_operation]
            corresponding_channel.execute(each_operation)
        self.agenda = {i: self.agenda[i+1] for i in range(self.agenda_length-1)}
        self.agenda.update({self.agenda_length - 1: []})

    def step(self, task: Task):
        # operation goal TODO
        if task and task.is_goal:
            self.decompose(task.term, 0)
            self.distribute_execute()
