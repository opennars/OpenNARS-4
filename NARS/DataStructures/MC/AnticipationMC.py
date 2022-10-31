from pynars.Narsese import Task, parser
from pynars.NAL.Inference.LocalRules import revision
from pynars.NARS.DataStructures.MC import InputBufferMC


class AnticipationMC:
    """
    Anticipation is the anticipation made by some predictions, e.g., (A, A=/>B |- B)
    It contains two parts:
        1) the body of the anticipation, which is a task,
        2) the prediction makes this anticipation, which is used for updating when the first part is satisfied/unsatisfied
    """

    def __init__(self, t: Task, parent_prediction: Task):
        self.t = t
        self.parent_prediction = parent_prediction
        # check whether an anticipation is examined
        self.solved = False

    def satisfied(self, buffer: InputBufferMC, event: Task):
        revised_t = revision(self.t, event)  # revision if satisfied

        tmp_prediction = parser.parse(self.parent_prediction.sentence.word + "%1.0; 0.5%")  # one positive case
        revised_prediction = revision(self.parent_prediction, tmp_prediction)

        buffer.update_prediction(revised_prediction)

        return revised_t

    def unsatisfied(self, buffer: InputBufferMC):
        tmp_prediction = parser.parse(self.parent_prediction.sentence.word + "%0.0; 0.5%")
        revised_prediction = revision(self.parent_prediction, tmp_prediction)
        buffer.update_prediction(revised_prediction)
