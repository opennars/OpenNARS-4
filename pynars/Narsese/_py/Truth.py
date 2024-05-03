from pynars.Config import Config
from typing import Type

class Truth:
    # analytic: Type['Truth']
    def __init__(self, f, c, k) -> None:
        self.f = f 
        self.c = c
        self.k = k
    
    @property
    def e(self):
        return (self.c * (self.f - 0.5) + 0.5)

    # @classmethod
    # def from_w(cls, w_plus, w, k):
    #     f, c = w_to_f(w_plus, w), w_to_c(w_plus, w)        
    #     return Truth(f, c, k)
    def __iter__(self):
        '''return (f, c, k)'''
        return iter((self.f, self.c, self.k))

    def __hash__(self) -> int:
        return hash((self.f, self.c, self.k))

    def __str__(self) -> str:
        return f'%{self.f:.3f};{self.c:.3f}%'
    
    def __repr__(self) -> str:
        return str(self)

truth_analytic = Truth(1.0, 1.0, Config.k)
    