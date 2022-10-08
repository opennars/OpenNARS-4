from pynars.NAL.Functions import Truth_induction, Stamp_merge, Budget_merge
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from pynars.Narsese import Judgement, Task, Term


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
                    # TODO, this is ugly
                    word = "<(&/," \
                           + self.slots[i].candidate.sentence.word \
                           + ",+" \
                           + str(abs(self.present - i)) \
                           + ") =/> " \
                           + self.slots[self.present].candidate.sentence.word \
                           + ">."
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(Term(word), stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        # =|>
        if self.slots[self.present].candidate:
            # from concurrent events
            for i in range(len(self.slots[self.present].events)):
                if self.slots[i].candidate and not self.slots[self.present].events[i].term.equal(
                        self.slots[self.present].candidate.term):
                    # TODO, this is ugly
                    word = "<(&/," \
                           + self.slots[i].candidate.sentence.word \
                           + ",+" \
                           + str(abs(self.present - i)) \
                           + ") =|> " \
                           + self.slots[self.present].candidate.sentence.word \
                           + ">."
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(Term(word), stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
            # from historical events
            for i in range(len(self.slots[self.present].events_historical)):
                if not self.slots[self.present].events_historical[i].term.equal(
                        self.slots[self.present].candidate.term):
                    # TODO, this is ugly
                    word = "<(&/," \
                           + self.slots[i].candidate.sentence.word \
                           + ",+" \
                           + str(abs(self.present - i)) \
                           + ") =|> " \
                           + self.slots[self.present].candidate.sentence.word \
                           + ">."
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(Term(word), stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        return self.slots[self.present].candidate
