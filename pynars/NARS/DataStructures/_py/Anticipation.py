from pynars.Config import Config
from pynars.NAL.Functions import truth_to_quality
from pynars.Narsese import Task, parser, Judgement, Truth, Budget
from pynars.NAL.Inference.LocalRules import revision
from pynars.NARS.DataStructures import Buffer


class Anticipation:
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

    def satisfied(self, buffer: Buffer):
        # one positive case
        tmp_prediction = Task(Judgement(self.parent_prediction.term, truth=Truth(1, Config.c, Config.k)))
        buffer.update_prediction(tmp_prediction)

        return self.t

    def unsatisfied(self, buffer: Buffer):
        # one negative case
        tmp_prediction = Task(Judgement(self.parent_prediction.term, truth=Truth(0, Config.c, Config.k)))
        buffer.update_prediction(tmp_prediction)
