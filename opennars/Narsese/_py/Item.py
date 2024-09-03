from .Budget import Budget
from typing import Type
from opennars.Config import Config
from copy import deepcopy
class Item:
    def __init__(self, hash_value, budget: Budget=None, copy_budget=True) -> None:
        budget = (deepcopy(budget) if copy_budget else budget) if budget is not None else Budget(Config.priority, Config.durability, Config.quality)
        self._hash_value = hash_value
        self.set_budget(budget)

    def set_budget(self, budget: Budget):
        self.budget: Budget = budget
    
    def __hash__(self) -> int:
        return self._hash_value
    
    def __eq__(self, o: object) -> bool:
        return hash(o) == hash(self)

    def __str__(self) -> str:
        return f'{self.budget} (Item)'

    def __repr__(self) -> str:
        return str(self)
    