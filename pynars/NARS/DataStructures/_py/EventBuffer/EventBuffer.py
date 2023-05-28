from pynars.NAL.Functions import Truth_induction
from pynars.NARS.DataStructures._py.Buffer import Buffer
from pynars.Narsese import Compound, Interval, Judgement, Task


class EventBuffer(Buffer):
    """
    Different from Buffer, EventBuffer equips the ability of temporal compounding, though there is still ONLY one input
    in each buffer cycle.
    """

    def __init__(self, num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory):
        super(EventBuffer, self).__init__(num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory)

    def temporal_compounding(self):
        """
        Must include the current time slot (if it is not empty), and don't allow skipping, say if there is a sequence
        (A, B, C), we cannot have a compound (A, C).

        An example, say if we have a sequence (A, B, C, D). We will have the following compounds (A, B, C, D),
        (B, C, D), (C, D) and (D).

        If there are None's in the middle, say (A, None, None, D), it will be first transformed to (A, +2, D), and then
        we will have 2 compounds, (A, +2, D), (D).

        Remember that in EventBuffers, only one
        """
        # if there are no inputs at all, return
        if len(self.slots[self.present].events) == 0:
            return

        # a list of candidates, it may be like (None, A, None, B), since the buffer CAN have nothing input
        # these None's are used for decide the interval
        previous_events = []  # a list of Terms (Intervals) AND Tasks

        interval = 0
        skip = True

        for i in range(self.present):
            if len(self.slots[i].events) != 0:
                skip = False
                if interval != 0:
                    previous_events.append(Interval(interval))
                    interval = 0
                # here, though list(dict.keys()) is not am array, but we ASSUME in each time slot, there is only one
                # event
                previous_events.append(self.slots[i].events[list(self.slots[i].events.keys())[0]].t)
            elif not skip:
                interval += 1

        for i in range(len(previous_events)):
            if not isinstance(previous_events[i], Interval):  # then it must be a Task
                # term
                term = Compound.SequentialEvents(
                    *[each.term if not isinstance(each, Interval) else each for each in previous_events[i:]])
                # truth, using truth-induction function
                truth = previous_events[i].truth
                for each in previous_events[i + 1:]:
                    if not isinstance(each, Interval):
                        truth = Truth_induction(truth, each.truth)
                # stamp, using the current stamp
                stamp = previous_events[i].stamp
                # budget, using the current budget
                budget = previous_events[i].budget
                # sentence composition
                sentence = Judgement(term, stamp, truth)
                # task generation
                task = Task(sentence, budget)
                self.slots[self.present].update_working_space(task)

        # if there are no previous events at all, then just put the only event into the working space
        self.slots[self.present].update_working_space(
            self.slots[self.present].events[list(self.slots[self.present].events.keys())[0]].t)

    def compound_generation(self):
        # every event is loaded to the working space by temporal compounding
        # we have these compounds and themselves (atoms)
        self.temporal_compounding()
