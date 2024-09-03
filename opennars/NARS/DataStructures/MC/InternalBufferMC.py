import numpy as np

from opennars.NARS.DataStructures import Memory
from opennars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from opennars.NARS.DataStructures.MC.SlotMC import SlotMC


class InternalBufferMC(InputBufferMC):

    def __init__(self, num_slot, num_event, num_anticipation, num_operation, num_prediction,
                 memory: Memory, root_UI, UI_name):
        super(InternalBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_operation, num_prediction,
                                               memory, root_UI, UI_name)

    def operation_processing_default(self):
        """
        A default processing of operations. "By default" means that an operation is used as an event, and they are
        combined used in compound generation.

        And the operation is not used specially in prediction generation as "procedural knowledge".

        Note that, in internal buffers, this "operation" means "mental operations" specifically.
        """
        self.slots[self.present].events = np.append(self.slots[self.present].events,
                                                    self.slots[self.present - 1].operations)

    def step(self, new_contents, origin = ""):
        """
        Internal buffer and global buffer can have multiple inputs at the same time. And so they have contemporary and
        historical compound generations successively. But the input of the historical compound generation will be the
        highest concurrent input.
        """
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation, self.num_operation))

        self.operation_processing_default()  # default operation processing
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
