from opennars.Config import Config
from typing import Type

class Truth:
    def __init__(self, f, c, k) -> None:
        self.f = f 
        self.c = c
        self.k = k
    
    @property
    def e(self):
        return (self.c * (self.f - 0.5) + 0.5)

    def __iter__(self):
        '''return (f, c, k)'''
        return iter((self.f, self.c, self.k))

    def __hash__(self) -> int:
        return hash((self.f, self.c, self.k))

    def __str__(self) -> str:
        return f'%{self.f:.3f};{self.c:.3f}%'
    
    def __repr__(self) -> str:
        return str(self)

truth_analytic = Truth(Config.f, Config.c, Config.k)
    