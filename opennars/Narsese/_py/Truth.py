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

    @property
    def is_negative(self) -> bool:
        return self.f < 0.5
    
    @staticmethod
    def from_w( w_plus, w, k) -> 'Truth':
        if w>0:
            f, c = w_plus/w, w/(w+k)        
            return Truth(f, c, k)
        else:
            return Truth(0.5, 0, k)
    
    def __iter__(self):
        '''return (f, c, k)'''
        return iter((self.f, self.c, self.k))

    def __hash__(self) -> int:
        return hash((self.f, self.c, self.k))

    def __str__(self) -> str:
        return f'%{self.f:.3f};{self.c:.3f}%'
    
    def __repr__(self) -> str:
        return str(self)
    
    def clone(self) -> 'Truth':
        return Truth(self.f, self.c, self.k)

truth_analytic = Truth(Config.f, Config.c, Config.k)
    