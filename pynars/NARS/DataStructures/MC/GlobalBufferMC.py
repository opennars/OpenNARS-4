from pynars.NAL.Functions import Truth_induction, Stamp_merge, Budget_merge
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
from pynars.Narsese import Judgement, Task, Copula, Statement, Compound, Interval


class GlobalBufferMC(InputBufferMC):
    """
    The global buffer is able to generate concurrent implications (=|>).
    Currently, this is the only difference.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_operation, num_prediction,
                 memory: Memory, root_UI, UI_name):
        """
        Though the global buffer has an input variable "num_operation", but a global buffer will never process any
        operations, so this variable should always be 0.
        """
        super(GlobalBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_operation, num_prediction,
                                             memory, root_UI, UI_name)

    def prediction_generation(self):
        """
        In the global buffer, not only =/> implications are generated. But also =|> implications are generated.
        """
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
        # =|>
        if self.slots[self.present].candidate:
            # from concurrent events
            predicate = self.slots[self.present].candidate.term
            for i in range(len(self.slots[self.present].events)):
                if self.slots[self.present].events[-1][1].term.equal(self.slots[self.present].candidate.term):
                    continue
                subject = self.slots[self.present].events[i][1].term
                copula = Copula.ConcurrentImplication  # =|>
                term = Statement(subject, copula, predicate)
                # truth, using truth-induction function (TODO, may subject to change)
                truth = Truth_induction(self.slots[self.present].events[i][1].truth,
                                        self.slots[self.present].candidate.truth)
                # stamp, using stamp-merge function (TODO, may subject to change)
                stamp = Stamp_merge(self.slots[self.present].events[i][1].stamp,
                                    self.slots[self.present].candidate.stamp)
                # budget, using budget-merge function (TODO, may subject to change)
                budget = Budget_merge(self.slots[self.present].events[i][1].budget,
                                      self.slots[self.present].candidate.budget)
                # sentence composition
                sentence = Judgement(term, stamp, truth)
                # task generation
                prediction = Task(sentence, budget)
                self.update_prediction(prediction)

        return self.slots[self.present].candidate

    def step(self, new_contents, origin = ""):
        """
        Internal buffer and global buffer can have multiple inputs at the same time. And so they have contemporary and
        historical compound generations successively. But the input of the historical compound generation will be the
        highest concurrent input.
        """
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation, self.num_operation))

        self.concurrent_compound_generation(new_contents, origin)  # 1st step
        self.historical_compound_generation(origin)  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluations()  # 3rd step
        task_forward = self.prediction_generation()  # 4th step

        # GUI
        # ==============================================================================================================
        self.UI_roll()
        self.UI_content_update()
        self.UI_show()
        # ==============================================================================================================

        return task_forward
