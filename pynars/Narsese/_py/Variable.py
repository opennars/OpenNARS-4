from copy import copy, deepcopy
from enum import Enum
from typing import Type
from pynars.Config import Config

from pynars.utils.IndexVar import IndexVar, IntVar
from .Term import Term

class VarPrefix(Enum):
    Independent = "$"
    Dependent = "#"
    Query = "?"


class Variable(Term):
    is_var: bool = True
    has_var: bool = True
    
    def __init__(self, prefix: VarPrefix, word: str, idx: int=0, do_hashing=False) -> None:
        self.prefix = prefix
        self.name = str(word)
        word = prefix.value
        super().__init__(word, do_hashing=do_hashing)
        self.dependents = [] # only for dependent variable. TODO: implement son classes of Variable, including DependentVar, IndependentVar, QueryVar.
        # self.has_variable: bool = True

        self.is_ivar = self.has_ivar = self.prefix == VarPrefix.Independent
        self.is_dvar = self.has_dvar = self.prefix == VarPrefix.Dependent
        self.is_qvar = self.has_qvar = self.prefix == VarPrefix.Query

        # if idx is not None:
        if self.is_ivar: self._vars_independent.add(IntVar(int(idx)), [])
        if self.is_dvar: self._vars_dependent.add(IntVar(int(idx)), [])
        if self.is_qvar: self._vars_query.add(IntVar(int(idx)), [])
    

    def __repr__(self) -> str:
        # return f'<Variable: {self.repr}>'
        # return self.word + self.name
        return f'<Variable: {self.repr()}>'


    def repr(self):
        ''''''
        if not self.is_var: raise "Invalide case."
        if self.is_ivar:
            var = self._vars_independent.indices[0]
        elif self.is_dvar:
            var = self._vars_dependent.indices[0]
        elif self.is_qvar:
            var = self._vars_query.indices[0]
        else: raise "Invalide case."
        
        # if self.is_ivar:
        #     try: idx = index_var.positions.index(pos)
        #     except: raise "Invalid case: The `pos` is not in `index_var.positions_ivar`"
        #     var = index_var.postions_normalized[0][idx] if Config.variable_repr_normalized else index_var.var_independent[idx]
        # elif self.is_dvar:
        #     try: idx = index_var.positions.index(pos)
        #     except: raise "Invalid case: The `pos` is not in `index_var.positions_dvar`"
        #     var = index_var.postions_normalized[1][idx] if Config.variable_repr_normalized else index_var.var_dependent[idx]
        # elif self.is_qvar:
        #     try: idx = index_var.positions.index(pos)
        #     except: raise "Invalid case: The `pos` is not in `index_var.positions_qvar`"
        #     var = index_var.postions_normalized[2][idx] if Config.variable_repr_normalized else index_var.var_query[idx]
        # else: raise "Invalide case."
        prefix = self.prefix.value
            
        return prefix + str(int(var)+1)


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
        clone._vars_independent = clone._vars_independent.clone()
        clone._vars_dependent = clone._vars_dependent.clone()
        clone._vars_query = clone._vars_query.clone()
        return clone