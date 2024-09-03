import tkinter
from abc import abstractmethod
from opennars.Narsese import Term
from opennars.NARS.DataStructures.MC.EventBufferMC import EventBufferMC


class ChannelMC:

    def __init__(self, num_slot, num_event, num_anticipation, num_operation, num_prediction, memory,
                 root_UI: tkinter.Tk, UI_name: str):
        self.ID = UI_name
        self.operations = []
        self.event_buffer = EventBufferMC(num_slot, num_event, num_anticipation, num_operation, num_prediction, memory,
                                          root_UI, UI_name)

    @abstractmethod
    def execute(self, term: Term):
        pass

    @abstractmethod
    def information_gathering(self):
        return None

    def step(self):
        new_contents = self.information_gathering()
        task_forward = self.event_buffer.step(new_contents, "SC2")
        return task_forward
