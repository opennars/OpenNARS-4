import numpy as np

from pynars.Config import Config
from pynars.NAL.Inference.LocalRules import revision
from pynars.Narsese import Task, Budget, Term, Judgement
from pynars.NARS.DataStructures import Anticipation, Buffer, Event


class Slot:
    """
    Each slot shall contain 4 parts:
    1) events, including input events, in event buffers, there are only one input events, but in other buffers,
    there might be more than one event;
    2) working space, if there are compounds need to be generated, they will be here. IT is separated from self.events
    to avoid some impossible cases. (e.g., from (a, b, c), generate (a, ab, c)).
    3) anticipations, events (including compounds) expected;
    4) to-do operations, these operations will be executed AT THE END of each cycle.
    """

    def __init__(self, num_event, num_anticipation, num_operation):

        self.num_event = num_event
        self.num_working_space = 10 * num_event
        self.num_anticipation = num_anticipation
        self.num_operation = num_operation

        """
        self.events are the MOST original events, untouched by MY personal understanding. As a reference can be 
        inferred in the future. So, a working space (combination of the FACT and MY understanding) will be used.
        """
        self.events = {}
        self.events_archived = {}
        self.working_space = {}

        self.anticipations = {}
        self.operations = []

        self.candidate = None

    def input_events(self, t: Task):
        """
        The very beginning events input. Say, turn the outside Task in Event.

        When overwhelmed, these tasks will be dropped.
        """
        word = t.term.word
        if word in self.events:
            # revision
            # even it is input, it is also possible for duplicate tasks
            self.events[word] = Event(revision(self.events[word].t, t))
        elif len(self.events) < self.num_event:
            self.events.update({word: Event(t)})

    def update_working_space(self, t: Task):
        """
        Update a single event in the working space.

        When overwhelmed, the following tasks will be dropped.
        """
        word = t.term.word
        if word in self.working_space:
            # revision
            self.working_space[word] = Event(revision(self.working_space[word].t, t))
        elif len(self.working_space) < self.num_working_space:
            self.working_space.update({word: Event(t)})

    def update_anticipations(self, a: Anticipation):
        """
        There might be duplicate anticipations. Only the strongest one (the one with the highest frequency) will be
        kept.
        """
        word = a.t.term.word
        if word in self.anticipations:
            # keep the strongest one
            if a.t.truth.f > self.anticipations[word].t.truth.f:
                self.anticipations[word] = a
        elif len(self.anticipations) < self.num_anticipation:
            self.anticipations.update({word: a})

    def update_operations(self, term: Term):
        """
        Remember that operations are executed at the end of each time slot.
        """
        if len(self.operations) < self.num_operation:
            self.operations.append(Task(Judgement(term)))  # default budget

    def check_anticipation(self, buffer: Buffer):
        """
        Unexpected event:= not an anticipation

        If an anticipation matches with an event, then the task in the event will be revised.

        If there is an event with no anticipation matched, it will be considered "unexpected", and therefore draw
        more attention. Note that this "more attention" is inside the buffer.
        """
        events_updates = []  # satisfied anticipations will be used for revision

        for each_event in self.working_space:
            if each_event.word in self.anticipations:
                # a satisfied anticipation
                # revision for the event and the prediction
                # the prediction revision is finished in .satisfied(self)
                events_updates.append(self.anticipations[each_event.word].satisfied(buffer))
            else:
                each_event.priority_multiplier *= 1.1

        for each_task in events_updates:  # pay attention to the name
            self.update_working_space(each_task)

        # unsatisfied anticipations will be handled in the buffer
