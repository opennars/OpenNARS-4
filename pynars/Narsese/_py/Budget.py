from math import sqrt
from pynars.Config import Config
from typing import Type
from .Truth import Truth

class Budget:
    priority: float = 0.9
    durability: float = 0.9
    quality: float = 0.5
    
    def __init__(self, priority: float, durability: float, quality: float):
        self.priority = priority if priority is not None else Budget.priority
        self.durability = durability if durability is not None else  Budget.durability
        self.quality = quality if quality is not None else  Budget.quality

    @property
    def summary(self) -> float:
        return self.durability*(self.priority+self.quality)/2.0

    @property
    def is_above_thresh(self) -> bool:
        return self.summary > Config.budget_thresh


    def __str__(self) -> str:
        return f'${float(self.priority):.3f};{float(self.durability):.3f};{float(self.quality):.3f}$'
        
    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        '''return (p, d, q)'''
        return iter((self.priority, self.durability, self.quality))


    @classmethod
    def quality_from_truth(cls, t: Truth):
        exp: float = t.e
        return max(exp, (1 - exp)*0.75)

    def reduce_by_achieving_level(self, h: float):
        self.priority = self.priority * (1 - h)
        # self.quality = self.quality * (1 - h)
    
    def distribute(self, n: int):
        '''
        distribute the budget into n parts.
        Ref. OpenNARS 3.1.0 BudgetFunctions.java line 144~146:
            ```
            final float priority = (float) (b.getPriority() / sqrt(n));
            return new BudgetValue(priority, b.getDurability(), b.getQuality(), narParameters);
            ```
        '''
        return Budget(self.priority/sqrt((n if n > 0 else 1)), self.durability, self.quality)