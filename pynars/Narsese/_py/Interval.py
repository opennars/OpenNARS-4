from typing import Type
from .Term import Term


class Interval(Term):
    is_interval: bool = True
    def __init__(self, interval, do_hashing=False, word_sorted=None, is_input=False) -> None:
        super().__init__("+"+str(interval), do_hashing=do_hashing, word_sorted=word_sorted, is_input=is_input)
        self.interval = int(interval)

    def __repr__(self) -> str:
        return f'<Interval: {str(self)}>'
    
    def __int__(self) -> int:
        return self.interval
    
    def __add__(self, o: Type['Interval']):
        return Interval(int(self)+int(o))