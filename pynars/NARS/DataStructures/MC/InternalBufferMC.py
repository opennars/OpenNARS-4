from pynars.Narsese import Task
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC


class InternalBufferMC(InputBufferMC):
    """
    TODO, The internal buffer takes mental operations and evaluations into consideration.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory, root_UI, UI_name):
        super(InternalBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI,
                                               UI_name)
        self.previous_inference_result = []

    def update_inference_result(self, t: Task):
        self.previous_inference_result.append(t)
