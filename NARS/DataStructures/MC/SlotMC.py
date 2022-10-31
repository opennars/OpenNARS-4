from pynars.Narsese import Task, Budget
from pynars.NARS.DataStructures.MC import AnticipationMC, InputBufferMC


# the priority value of events
def p_value(t: Task):
    return t.budget.summary * t.truth.e / t.term.complexity ** 2


class SlotMC:

    def __init__(self, num_event, num_anticipation):
        self.num_event = num_event
        self.num_anticipation = num_anticipation

        self.events = []
        self.events_historical = []
        self.anticipations = []

        self.highest_compound = None
        self.highest_compound_historical = None
        self.candidate = None

    def update_events(self, t: Task):
        for i in range(len(self.events)):
            if self.events[i].term.equal(t.term):
                del self.events[i]
                break
        P = p_value(t)
        added = False
        # large to small
        for i in range(len(self.events)):
            if P > p_value(self.events[i]):
                self.events = self.events[:i] + [t] + self.events[i:]
                added = True
                break
        if not added:  # smallest
            self.events = self.events + [t]
        if len(self.events) > self.num_event:
            self.events = self.events[:-1]

    def update_events_historical(self, t: Task):
        for i in range(len(self.events_historical)):
            if self.events_historical[i].term.equal(t.term):
                del self.events_historical[i]
                break
        P = p_value(t)
        added = False
        # large to small
        for i in range(len(self.events_historical)):
            if P > p_value(self.events_historical[i]):
                self.events_historical = self.events_historical[:i] + [t] + self.events_historical[i:]
                added = True
                break
        if not added:  # smallest
            self.events_historical = self.events_historical + [t]
        if len(self.events_historical) > self.num_event:
            self.events_historical = self.events_historical[:-1]

    """
    There might be duplicate anticipations. All are used for revision.
    """
    def update_anticipation(self, a: AnticipationMC):
        self.anticipations.append(a)
        if len(self.anticipations) > self.num_anticipation:
            self.anticipations = self.anticipations[1:]

    """
    Unexpected event:= not an anticipation
    """
    def check_anticipation(self, buffer: InputBufferMC, mode_unexpected = False):
        events_updates = []
        events_historical_updates = []

        events_updates_unexpected = []
        events_historical_updates_unexpected = []

        for each_event in self.events:
            event_used = False  # whether it is used to fit an anticipation
            for each_anticipation in self.anticipations:
                if not each_anticipation.solved and each_anticipation.t.term.equal(each_event.term):
                    events_updates.append(each_anticipation.satisfied(buffer, each_event))
                    each_anticipation.solved = True
                    event_used = True
                    break
            if not event_used and mode_unexpected:  # unexpected event, budget.priority *= 1.1
                task = Task(each_event.sentence,
                            Budget(min(0.99, each_event.budget.priority * 1.1), each_event.budget.durability,
                                   each_event.budget.quality))
                events_updates_unexpected.append(task)

        for each_event_historical in self.events_historical:
            event_used = False
            for each_anticipation in self.anticipations:
                if not each_anticipation.solved and each_anticipation.t.term.equal(each_event_historical.term):
                    events_updates.append(each_anticipation.satisfied(buffer, each_event_historical))
                    each_anticipation.solved = True
                    event_used = True
                    break
            if not event_used and mode_unexpected:
                task = Task(each_event_historical.sentence,
                            Budget(min(0.99, each_event_historical.budget.priority * 1.1),
                                   each_event_historical.budget.durability,
                                   each_event_historical.budget.quality))
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
