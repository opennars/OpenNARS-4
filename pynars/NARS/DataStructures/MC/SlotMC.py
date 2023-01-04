import numpy as np
from pynars.Narsese import Task, Budget
from pynars.NARS.DataStructures.MC import AnticipationMC, InputBufferMC


# the priority value of events
def p_value(t: Task):
    return t.budget.summary * t.truth.e / t.term.complexity ** 2


class SlotMC:
    """
    Each slot shall contain 3 parts:
    1) events, including input events and generated compounds;
    2) anticipations, events (including compounds) expected;
    3) to-do operations, these operations will be executed AT THE END of each cycle.
    """

    def __init__(self, num_event, num_anticipation):
        self.num_event = num_event
        self.num_anticipation = num_anticipation

        self.events = np.array([])
        self.events_historical = np.array([])
        self.anticipations = {}

        self.highest_compound = None
        self.highest_compound_historical = None
        self.candidate = None

    def update_events(self, t: Task):
        word = t.term.word
        if len(self.events) != 0:
            self.events = np.delete(self.events, np.where(self.events[:, 0] == word), axis=0).reshape((-1, 3))
        if len(self.events) == 0:
            self.events = np.array([(word, t, p_value(t))])
        else:
            self.events = np.append(self.events, [(word, t, p_value(t))], 0)
        if len(self.events_historical) > self.num_event:
            self.events = np.delete(self.events, np.where(self.events[:, 2] == self.events[:, 2].min()),
                                    axis=0).reshape((-1, 3))

    # def update_events(self, t: Task):
    #     for i in range(len(self.events)):
    #         if self.events[i].term.equal(t.term):
    #             del self.events[i]
    #             break
    #     P = p_value(t)
    #     added = False
    #     # large to small
    #     for i in range(len(self.events)):
    #         if P > p_value(self.events[i]):
    #             self.events = self.events[:i] + [t] + self.events[i:]
    #             added = True
    #             break
    #     if not added:  # smallest
    #         self.events = self.events + [t]
    #     if len(self.events) > self.num_event:
    #         self.events = self.events[:-1]

    def update_events_historical(self, t: Task):
        word = t.term.word
        if len(self.events_historical) != 0:
            self.events_historical = np.delete(self.events_historical,
                                               np.where(self.events_historical[:, 0] == word),
                                               axis=0).reshape((-1, 3))
        if len(self.events_historical) == 0:
            self.events_historical = np.array([(word, t, p_value(t))])
        else:
            self.events_historical = np.append(self.events_historical, [(word, t, p_value(t))], 0)
        if len(self.events_historical) > self.num_event:
            self.events_historical = np.delete(self.events_historical, np.where(
                self.events_historical[:, 2] == self.events_historical[:, 2].min()), axis=0).reshape((-1, 3))

    # def update_events_historical(self, t: Task):
    #     for i in range(len(self.events_historical)):
    #         if self.events_historical[i].term.equal(t.term):
    #             del self.events_historical[i]
    #             break
    #     P = p_value(t)
    #     added = False
    #     # large to small
    #     for i in range(len(self.events_historical)):
    #         if P > p_value(self.events_historical[i]):
    #             self.events_historical = self.events_historical[:i] + [t] + self.events_historical[i:]
    #             added = True
    #             break
    #     if not added:  # smallest
    #         self.events_historical = self.events_historical + [t]
    #     if len(self.events_historical) > self.num_event:
    #         self.events_historical = self.events_historical[:-1]

    """
    There might be duplicate anticipations. All are used for revision.
    """

    def update_anticipation(self, a: AnticipationMC):
        if len(self.anticipations) < self.num_anticipation:
            word = a.t.term.word
            if word in self.anticipations and p_value(a.t) > p_value(self.anticipations[word].t):
                self.anticipations.update({word: a})
            else:
                self.anticipations.update({word: a})

    """
    Unexpected event:= not an anticipation
    """

    def check_anticipation(self, buffer: InputBufferMC, mode_unexpected = False):
        events_updates = []
        events_historical_updates = []

        events_updates_unexpected = []
        events_historical_updates_unexpected = []

        for each_event in self.events:
            if each_event[0] in self.anticipations:
                events_updates.append(self.anticipations[each_event[0]].satisfied(buffer, each_event[1]))
            elif mode_unexpected:
                task = Task(each_event[1].sentence,
                            Budget(min(0.99, each_event[1].budget.priority * 1.1), each_event[1].budget.durability,
                                   each_event[1].budget.quality))
                events_updates_unexpected.append(task)

        for each_event_historical in self.events_historical:
            if each_event_historical[0] in self.anticipations:
                events_historical_updates.append(
                    self.anticipations[each_event_historical[0]].satisfied(buffer, each_event_historical[1]))
            elif mode_unexpected:
                task = Task(each_event_historical[1].sentence,
                            Budget(min(0.99, each_event_historical[1].budget.priority * 1.1),
                                   each_event_historical[1].budget.durability,
                                   each_event_historical[1].budget.quality))
                events_historical_updates_unexpected.append(task)

        for each_event in events_updates:
            self.update_events(each_event)
        for each_event_historical in events_historical_updates:
            self.update_events_historical(each_event_historical)
        for each_event_unexpected in events_updates_unexpected:
            self.update_events(each_event_unexpected)
        for each_event_historical_unexpected in events_historical_updates_unexpected:
            self.update_events_historical(each_event_historical_unexpected)

        # unsatisfied anticipations are handled in InputBufferMC.py
