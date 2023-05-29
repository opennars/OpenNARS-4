import numpy as np
from depq import DEPQ
from pynars.Narsese import Task
from ..Memory import Memory
from typing import Tuple, Iterable
from ..Table import Table
from collections import deque

class Slots:
    ''''''
    def __init__(self, N: int, M) -> None:
        self.past = np.array([None for _ in range(N)])
        self.past[:] = [Table(M) for _ in range(N)]
        self.future = np.array([None for _ in range(N)])
        self.future[:] = [Table(M) for _ in range(N)]
        self.now = Table(M)
        self.events = np.full((N+1), None, object)

        pass

    def roll(self):
        self.past[:-1] = self.past[1:]
        self.past[-1] = self.now
        self.now = self.future[0]
        self.future[:-1] = self.future[1:]
        future: DEPQ = self.future[-1]
        self.events[:-1] = self.events[1:]
        future.clear()
    
    def add(self, i: int, tasks: Iterable[Task]):
        '''
        add the task into the `i`th slot
        Args:
            i (int): index of the slot. 0<=i<=N
            task (Task): the task to be added to the slot
        '''
        slot: Table
        if i==0:
            slot = self.now
        elif i<0:
            slot = self.past[abs(i)-1]
        else: # i>0
            slot = self.future[abs(i)-1]
        
        for task in tasks:
            slot.add(task, task.budget.priority)
    
    def append(self, tasks: Iterable[Task]):
        if len(tasks) > 1:
            raise NotImplementedError("TODO: handle the case where len(tasks)>1")
        tasks = tuple(tasks)
        self.roll()
        self.add(0, tasks)
        self.events[-1] = tasks
