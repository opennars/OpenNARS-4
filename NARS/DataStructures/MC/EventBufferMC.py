from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.InputBufferMC import InputBufferMC


class EventBufferMC(InputBufferMC):

    """
    Event buffers may subject to change to specific channels.
    """

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory):
        super(EventBufferMC, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory)
