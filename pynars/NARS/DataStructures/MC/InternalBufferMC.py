import numpy as np

from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
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

    def step(self, new_contents, origin = ""):
        """
        Internal buffer and global buffer can have multiple inputs at the same time. And so they have contemporary and
        historical compound generations successively. But the input of the historical compound generation will be the
        highest concurrent input.
        """
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation))

        self.contemporary_compound_generation(new_contents, origin)  # 1st step
        # find the highest concurrent compound first
        if len(self.slots[self.present].events) != 0:
            # when this happens, the same process in memory_based_evaluations() will be skipped
            self.slots[self.present].events = self.slots[self.present].events[
                np.argsort(self.slots[self.present].events[:, 2])]
            self.slots[self.present].highest_compound = self.slots[self.present].events[-1][1]
            if self.slots[self.present].highest_compound is not None:
                self.historical_compound_generation(self.slots[self.present].highest_compound, origin)  # 1st step
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
