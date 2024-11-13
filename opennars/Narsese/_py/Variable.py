from copy import copy
from enum import Enum
from typing import Type
from opennars.Config import Config

from opennars.utils.IndexVar import IndexVar, IntVar
from .Term import Term

class VarPrefix(Enum):
    Independent = "$"
    Dependent = "#"
    Query = "?"


class Variable(Term):
    is_var: bool = True
    has_var: bool = True
    
    normalized: bool = False # used for variable normalization
    
    def __init__(self, prefix: VarPrefix, word: str, idx: int=0, do_hashing=False) -> None:
        self.prefix = prefix
        self.name = str(word)
        word = prefix.value
        super().__init__(word, do_hashing=do_hashing)
        self.dependents = [] # only for dependent variable. TODO: implement son classes of Variable, including DependentVar, IndependentVar, QueryVar.

        match prefix:
            case VarPrefix.Independent:
                self.is_ivar = True
                self.has_ivar = True
            case VarPrefix.Dependent:
                self.is_dvar = True
                self.has_dvar = True
            case VarPrefix.Query:
                self.is_qvar = True
                self.has_qvar = True

    def __repr__(self) -> str:
        return f'<Variable: {self.repr()}>'

    def repr(self):
        prefix = self.prefix.value
        return prefix + str(self.name)

    @classmethod
    def Independent(cls, word: str, idx=0, do_hashing=False):
        return Variable(VarPrefix.Independent, word, idx=idx, do_hashing=do_hashing)


    @classmethod
    def Dependent(cls, word: str, idx=0, do_hashing=False):
        return Variable(VarPrefix.Dependent, word, idx=idx, do_hashing=do_hashing)


    @classmethod
    def Query(cls, word: str, idx=0, do_hashing=False):
        return Variable(VarPrefix.Query, word, idx=idx, do_hashing=do_hashing)
    
    def clone(self) -> Type['Variable']:
        clone = copy(self)
        return clone