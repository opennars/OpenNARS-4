from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
from pynars.Narsese import Compound, Interval, Judgement, Task
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC
from pynars.NAL.Functions import Stamp_merge, Budget_merge, Truth_induction


class EventBufferMC(InputBufferMC):
    """
    The same as InputBufferMC without further specification.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory, root_UI, UI_name):
        super(EventBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI,
                                            UI_name)

    """
    Event buffer now only receive one event (this event might be matrix) at each time. Therefore, there are no
    "contemporary candidates" at all.
    But global buffers or internal buffers may still have multiple inputs as well.
    """

    def step(self, new_content, origin = ""):
        """
        Event buffer can get at most one new content each time, and so there are no "concurrent compound generations".
        But it still has historical compound generations.
        """
        # remove the oldest slot and create a new one
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation))

        self.historical_compound_generation(new_content, origin)  # 1st step
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
