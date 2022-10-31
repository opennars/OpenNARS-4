import tkinter
from abc import abstractmethod
from pynars.Narsese import Term
from pynars.NARS.DataStructures.MC.EventBufferMC import EventBufferMC


class ChannelMC:

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory, root_UI: tkinter.Tk,
                 UI_name: str):
        self.ID = UI_name
        self.operations = []
        self.event_buffer = EventBufferMC(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI,
                                          UI_name)

    @abstractmethod
    def execute(self, term: Term):
        pass

    @abstractmethod
    def information_gathering(self):
        return None

    def step(self):
        new_contents = self.information_gathering()
        task_forward = self.event_buffer.step(new_contents)
        return task_forward
