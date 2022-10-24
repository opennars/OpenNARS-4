from pynars.NARS.DataStructures.MC.EventBufferMC import EventBufferMC
from pynars.Narsese import Term


class ChannelMC:

    def __init__(self, ID: str, num_slot, num_event, num_anticipation, num_prediction, memory, root_UI):
        self.ID = ID
        self.operations = []
        self.event_buffer = EventBufferMC(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI, ID)

    def execute(self, term: Term):
        # TODO, you need to do it
        pass

    def information_gathering(self):
        # TODO, you need to do it
        return None

    def step(self):
        new_contents = self.information_gathering()
        task_forward = self.event_buffer.step(new_contents)
        return task_forward

