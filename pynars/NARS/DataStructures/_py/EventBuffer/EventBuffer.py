import numpy as np
from depq import DEPQ
from pynars.Narsese import Task, Compound, Term, Statement, Judgement
from ..Memory import Memory
from .Slot import Slots
from .PredictionTable import PredictionTable
from typing import Iterable, Tuple, List

class EventBuffer:
    ''''''

    def __init__(self, N=5, capacity_pred=1000, memory: Memory=None) -> None:

        self.slots = Slots(N, N)
        self.N = N
        self.predictions = PredictionTable(capacity_pred)

        self.memory: Memory = memory
        
        pass

    def append(self, events: Iterable[Task]):
        '''
        add events to the event-buffer
        '''
        self.slots.append(events)
        
    def combination(self, bias: int=0) -> List[Compound]:
        '''
        bias >= 0
        '''
        # assert bias >= 0
        compounds = []
        for i in range(1+bias, self.N+1):
            if self.slots.events[-i] is None:
                break
            events = self.slots.events[-i:None if bias==0 else -bias]
            terms: Iterable[Term] = (event[0].term for event in events)
            cpnd = Compound.SequentialEvents(*terms)
            compounds.append(cpnd)
        return compounds
    

    def generate_predictions(self):
        ''''''
        compounds = self.combination()
        event: Task = self.slots.events[-1][0]
        term = event.term   
        predictions = []
        for compound in compounds:
            prediction = Task(Judgement(Statement.PredictiveImplication(compound, term)))
            predictions.append(prediction)
        return predictions