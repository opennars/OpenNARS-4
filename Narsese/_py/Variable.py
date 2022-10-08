from copy import copy, deepcopy
from enum import Enum
from typing import Type
from pynars.Config import Config

from pynars.utils.IndexVar import IndexVar
from .Term import Term

class VarPrefix(Enum):
    Independent = "$"
    Dependent = "#"
    Query = "?"


class Variable(Term):
    is_var: bool = True
    has_var: bool = True
    
    def __init__(self, prefix: VarPrefix, word: str, do_hashing=False, is_input=False) -> None:
        self.prefix = prefix
        self.name = str(word)
        word = prefix.value
        super().__init__(word, do_hashing=do_hashing)
        self.dependents = [] # only for dependent variable. TODO: implement son classes of Variable, including DependentVar, IndependentVar, QueryVar.
        # self.has_variable: bool = True

        self.is_ivar = self.has_ivar = self.prefix == VarPrefix.Independent
        self.is_dvar = self.has_dvar = self.prefix == VarPrefix.Dependent
        self.is_qvar = self.has_qvar = self.prefix == VarPrefix.Query
    

    def __repr__(self) -> str:
        # return f'<Variable: {self.repr}>'
        return self.word + self.name


    # @property
    # def repr(self):
    #     return self.word + self.name

    def repr_with_var(self, index_var: IndexVar, pos: list):
        ''''''
        if not self.is_var: raise "Invalide case."
        if self.is_ivar:
            try: idx = index_var.positions_ivar.index(pos)
            except: raise "Invalid case: The `pos` is not in `index_var.positions_ivar`"
            var = index_var.postions_normalized[0][idx] if Config.variable_repr_normalized else index_var.var_independent[idx]
        elif self.is_dvar:
            try: idx = index_var.positions_dvar.index(pos)
            except: raise "Invalid case: The `pos` is not in `index_var.positions_dvar`"
            var = index_var.postions_normalized[1][idx] if Config.variable_repr_normalized else index_var.var_dependent[idx]
        elif self.is_qvar:
            try: idx = index_var.positions_qvar.index(pos)
            except: raise "Invalid case: The `pos` is not in `index_var.positions_qvar`"
            var = index_var.postions_normalized[2][idx] if Config.variable_repr_normalized else index_var.var_query[idx]
        else: raise "Invalide case."
        prefix = self.prefix.value
            
        return prefix + str(var)


    @classmethod
    def Independent(cls, word: str, do_hashing=False, is_input=False):
        return Variable(VarPrefix.Independent, word, do_hashing, is_input)


    @classmethod
    def Dependent(cls, word: str, do_hashing=False, is_input=False):
        return Variable(VarPrefix.Dependent, word, do_hashing, is_input)


    @classmethod
    def Query(cls, word: str, do_hashing=False, is_input=False):
        return Variable(VarPrefix.Query, word, do_hashing, is_input)

    
    def clone(self) -> Type['Variable']:
        clone = copy(self)
        clone._index_var = deepcopy(self._index_var)
        return clone