from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC


class EventBufferMC(InputBufferMC):
    """
    The same as InputBufferMC without further specification.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory, root_UI, UI_name):
        super(EventBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI,
                                            UI_name)
