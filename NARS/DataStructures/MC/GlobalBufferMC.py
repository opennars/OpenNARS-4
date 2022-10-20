from pynars.NAL.Functions import Truth_induction, Stamp_merge, Budget_merge
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from pynars.Narsese import Judgement, Task, Term, Copula, Statement, Compound, Interval


class GlobalBufferMC(InputBufferMC):
    """
    The internal buffer may take the mental operation carried out in consideration, but it is not here yet.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory):
        super(GlobalBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory)

    def prediction_generation(self):
        """
        In the global buffer, not only =/> implications are generated. But also =|> implications are generated.
        """
        # =/>
        if self.slots[self.present].candidate:
            for i in range(self.present):
                if self.slots[i].candidate:
                    subject = Compound.SequentialEvents(self.slots[i].candidate.term, Interval(abs(self.present - i)))
                    copula = Copula.PredictiveImplication  # =/>
                    predicate = self.slots[self.present].candidate.term
                    term = Statement(subject, copula, predicate)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        # =|>
        if self.slots[self.present].candidate:
            # from concurrent events
            for i in range(len(self.slots[self.present].events)):
                if self.slots[self.present].candidate and \
                        not self.slots[self.present].events[i].term.equal(self.slots[self.present].candidate.term):
                    subject = self.slots[self.present].events[i].term
                    copula = Copula.ConcurrentImplication  # =|>
                    predicate = self.slots[self.present].candidate.term
                    term = Statement(subject, copula, predicate)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[self.present].events[i].truth,
                                            self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[self.present].events[i].stamp,
                                        self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[self.present].events[i].budget,
                                          self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
            # from historical events
            for i in range(len(self.slots[self.present].events_historical)):
                if not self.slots[self.present].events_historical[i].term.equal(
                        self.slots[self.present].candidate.term):
                    subject = self.slots[self.present].events_historical[i].term
                    copula = Copula.ConcurrentImplication  # =|>
                    predicate = self.slots[self.present].candidate.term
                    term = Statement(subject, copula, predicate)
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        return self.slots[self.present].candidate
