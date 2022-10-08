from pynars.NAL.Inference.LocalRules import revision
# from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from pynars.NARS.DataStructures.MC import InputBufferMC
from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
from pynars.Narsese import Task, parser


class AnticipationMC:

    def __init__(self, t: Task, parent_prediction: Task):
        self.t = t
        self.parent_prediction = parent_prediction
        self.solved = False

    # the priority value of predictions
    def p_value(self, t: Task):
        return InputBufferMC.p_value(t)

    def satisfied(self, prediction_table: list, event: Task):
        revised_t = revision(self.t, event)
        tmp_prediction = parser.parse(self.parent_prediction.sentence.word + "%1.0; 0.5%")
        revised_prediction = revision(self.parent_prediction, tmp_prediction)
        for i in range(len(prediction_table)):
            if prediction_table[i].sentence.word == revised_prediction.sentence.word:
                del prediction_table[i]
                break
        P = self.p_value(revised_prediction)
        for i in range(len(prediction_table)):
            if P > self.p_value(prediction_table[i]):
                prediction_table = prediction_table[:i] + [revised_prediction] + prediction_table[i:]
                break
        return revised_t

    def unsatisfied(self, prediction_table: list):
        tmp_prediction = parser.parse(self.parent_prediction.sentence.word + "%0.0; 0.5%")
        revised_prediction = revision(self.parent_prediction, tmp_prediction)
        for i in range(len(prediction_table)):
            if prediction_table[i].sentence.word == revised_prediction.sentence.word:
                del prediction_table[i]
                break
        P = self.p_value(revised_prediction)
        for i in range(len(prediction_table)):
            if P > self.p_value(prediction_table[i]):
                prediction_table = prediction_table[:i] + [revised_prediction] + prediction_table[i:]
                break
