import numpy as np
from depq import DEPQ
from pynars.Narsese import Task
from .Memory import Memory

class Slots:
    ''''''
    def __init__(self, N: int, M) -> None:
        self.past = np.array([DEPQ(M) for _ in range(N)])
        self.future = np.array([DEPQ(M) for _ in range(N)])
        self.now = DEPQ(M)
        self.events = np.full((N+1), None, DEPQ)

        pass

    def roll(self):
        self.past[:-1] = self.past[1:]
        self.past[-1] = self.now
        self.now = self.future[0]
        self.future[:-1] = self.future[1:]
        future: DEPQ = self.future[-1]
        future.clear()
    
    def add(self, i: int, task: Task):
        '''
        add the task into the `i`th slot
        Args:
            i (int): index of the slot. 0<=i<=N
            task (Task): the task to be added to the slot
        '''
        slot: DEPQ
        if i==0:
            slot = self.now
        elif i<0:
            slot = self.past[abs(i)-1]
        else: # i>0
            slot = self.future[abs(i)-1]
        slot.insert(task, task.budget.priority)

class PredictionTable:
    ''''''
    def __init__(self, capacity) -> None:
        pass

class EventBuffer:
    ''''''

    def __init__(self, N=5, capacity_pred=1000, memory: Memory=None) -> None:

        self.working_space = Slots(N, N)
        self.predictions = PredictionTable(capacity_pred)

        self.memory: Memory = memory
        pass

    def add(self, event: Task):
        '''
        add the event to the event-buffer
        '''
        