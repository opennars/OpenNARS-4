# from pynars.Narsese._py.Task import Task
from .Truth import Truth
from .Term import Term
from .Statement import Statement
from enum import Enum
from .Tense import Tense
from typing import Tuple, Type, Set, List, Union

from ordered_set import OrderedSet
# from .Evidence import Base
# from .Task import *

from pynars.Config import Config, Enable
from pynars import Global 

# class Evidence:
#     def __init__(self, task) -> None:
#         self._hash_task = hash(task)
#         self._input_id = task.input_id
    
#     def __eq__(self, evidence: Type['Evidence']):
#         return (self._hash_task==evidence._hash_task) and (self._input_id==evidence._input_id)

class Base:
    '''Evidential Base'''
    def __init__(self, terms: Tuple[int]=tuple()) -> None:
        # TODO: DOUBT --
        # IF `<A-->B>.`, `<B-->C>.`, `<C--D>.`, THEN it can be derived in a single that `<A-->C>.`, `<B-->D>.`.
        # In the second step, it can be derived that `{<A-->B>. <B-->D>.} |- (1) <A-->D>.`, and `{<A-->C>. <C-->D>.} |- (2) <A-->D>.`
        # Is it reasonable theoretically to apply revision rules between (1) and (2)?

        self._set: Set[int] = OrderedSet(terms)
        self._hash = None
    
    @classmethod
    def interleave(self, base1, base2) -> Type['Base']:
        '''interleave two bases'''
        # TODO: DOUBT --
        # What if some evidence is lost (because of forgetting)?

        # TODO: DOUBT --
        # Is the base ordered? What kind of evidence should overflow?
        

        # TODO: Ref: OpenNARS 3.1.0 Stamp.java line 178~187.
        # TODO: Optimize this loop with cython.
        b1 = len(base1)
        b2 = len(base2)
        base_length = min(b1 + b2, Config.maximum_evidental_base_length)
        evidential_base: Set[int] = OrderedSet()

        i1 = i2 = j = 0

        while j < base_length:
            if i2 < b2:
                evidential_base.add(base2[i2])
                j += 1
                i2 += 1
            if i1 < b1:
                evidential_base.add(base1[i1])
                j += 1
                i1 += 1

        return evidential_base

    def add(self, id_evidence: int):
        self._hash = None
        self._set.add(id_evidence)
        return self
    
    def extend(self, base: Union[Type['Base'] , None]):
        self._hash = None
        self._set = self.interleave(self._set, base)
        return self

    def is_overlaped(self, base: Union[Type['Base'], None]) -> bool:
        ''' Check whether another `Base` object is overlapped with `self`.
        Complexity: O(N) N=min(len(self), len(o))
        '''
        return not self._set.isdisjoint(base._set) if base is not None else False
    
    def do_hashing(self):
        self._hash = hash(frozenset(self._set))
        return self._hash

    def __eq__(self, o: Type['Base']) -> bool:
        # TODO: Ref: OpenNARS 3.1.0 Stamp.Java line 334~335, 346~349, 461~516
        if id(o) == id(self):
            return True
        elif hash(self) != hash(o):
            return False
        return self._set == o._set
    
    def __or__(self, base: Type['Base']) -> Type['Base']:
        return Base(self._set | base._set)

    def __ior__(self, base: Type['Base']) -> Type['Base']:
        self._hash = None
        self._set |= base._set
        return self

    def __hash__(self) -> int:
        return self._hash if self._hash is not None else self.do_hashing()

    def __len__(self) -> int:
        return len(self._set)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{set(self._set)}"

    def contains(self, base: 'Base'):
        return len(self._set - base._set) == 0
    
    def __contains__(self, evidence) -> bool:
        return self._set.__contains__(evidence)