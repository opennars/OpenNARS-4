from pynars.Narsese import Task


class Event:
    """
    Event is an auxiliary class for buffers. It contains one task, and corresponding parameters for the situation in the
    buffer.

    ONLY used inside buffer
    """

    def __init__(self, t: Task):
        self.t = t
        self.word = t.term.word
        self.complexity = t.term.complexity
        self.priority_multiplier = 1

    @property
    def priority(self):
        # just an example
        # say the priority of an event in a buffer is decided by its truth, priority, and its complexity
        # but if such event exists in the main memory already, its complexity will be set to 1
        return self.t.budget.priority * self.priority_multiplier * self.t.truth.e / (self.complexity ** 0.5)
