from pynars.Narsese._py.Connector import Connector
from .Copula import Copula
from pynars.Config import Enable
from typing import Iterable, List, Set, Type
from enum import Enum
from pynars.utils._codon.IndexVar import IndexVar

from numpy import prod
from ordered_set import OrderedSet
# from pynars.utils.tools import find_pos_with_pos, find_var_with_pos
from copy import copy, deepcopy
from bidict import bidict
from pynars.utils.IndexVar import IntVar
from typing import Callable
from typing import Tuple
import codon


class TermType(Enum):
    ATOM = 0
    STATEMENT = 1
    COMPOUND = 2

@codon.convert
class Term:

    __slots__ = (
        'type', 'copula', 'connector', '_complexity', 'has_var', 'has_ivar', 'has_dvar', 'has_qvar', 'is_var', 'is_ivar', 'is_dvar', 'is_qvar',
        'is_closed', 'is_interval', 'is_operation', '_height',
        'word', 'word_sorted', '_components', '_hash_value', '_vars_independent', '_vars_dependent', '_vars_query',
    )
    # copula: Copula = None

    # @codon.jit
    def __init__(self, word, do_hashing=False, word_sorted=None, is_input=False) -> None:

        self.type = TermType.ATOM
        self.copula: Copula = None
        self.connector: Connector = None
        self._complexity: float = 1.0 # The complexity of the term. Read only.
        self.has_var: bool = False # Whether the term contains variable(s).
        self.has_ivar: bool = False # Whether the term contains independent variable(s).
        self.has_dvar: bool = False # Whether the term contains dependent variable(s).
        self.has_qvar: bool = False # Whether the term contains query variable(s).
        self.is_var: bool = False
        self.is_ivar: bool = False
        self.is_dvar: bool = False
        self.is_qvar: bool = False
        self.is_closed: bool = True # Whether the term is closed or open in terms of variable.
        self.is_interval: bool = False
        self.is_operation = False 
        self._height = 0

        self.word = word
        self.word_sorted = word_sorted if word_sorted is not None else word
        self._components = None

        # Variables related initialization
        self._vars_independent = IndexVar()
        self._vars_dependent = IndexVar()
        self._vars_query = IndexVar()

        # id initialization
        if do_hashing: self.do_hashing()
        else: self._hash_value = None
    
    @property
    def vars_independent(self):
        return self._vars_independent
    
    @property
    def vars_dependent(self):
        return self._vars_dependent

    @property
    def vars_query(self):
        return self._vars_query

    @property
    def sub_terms(self) -> Set[Type['Term']]:
        return (self, *self._components) if self._components is not None else set((self, ))

    @property
    def components(self) ->Set[Type['Term']]:
        return self._components
    

    @codon.jit
    def count(self):
        '''the number of sub-terms (including this term itself)'''
        return len(self._components)+1 if self._components is not None else 1


    @property
    def complexity(self):
        return self._complexity

    @property
    def is_statement(self):
        return self.type == TermType.STATEMENT
    
    @property
    def is_compound(self):
        return self.type == TermType.COMPOUND
    
    @property
    def is_atom(self):
        return self.type == TermType.ATOM

    @property
    def is_commutative(self):
        '''whether the components of the term is commutative'''
        return False
    
    @property
    def is_higher_order(self):
        '''whether the term is higher-ordered'''
        return False

    @property
    def is_executable(self):
        return self.is_statement and self.is_operation

    @property
    def terms(self):
        return (self, )

    @property
    def variables(self) -> Tuple[IndexVar, IndexVar, IndexVar]:
        return (self.vars_independent, self.vars_dependent, self.vars_query)
    
    @property
    def is_mental_operation(self):
        return False

    @codon.jit
    def identical(self, o) -> bool:
        return hash(o) == hash(self) # and hash(o.index_var) == hash(self.index_var)

    @codon.jit
    def equal(self, o) -> bool:
        '''
        Return:
            is_equal (bool), is_replacable(bool)
        '''
        # o:  Type['Term']
        if o.is_atom:
            if self.is_var ^ o.is_var: # one of them is variable, while the other is not
                return True
            elif self.is_var and o.is_var: # the two are both variables
                if (self.is_ivar and o.is_ivar) or (self.is_dvar and o.is_dvar) or (self.is_qvar and o.is_qvar): # the two, to be equal, should be the same type of variable 
                    return True
                else: 
                    return False
            elif not self.is_var and not o.is_var: # the two are neither variables:
                return self.identical(o)
        elif (o.is_compound or o.is_statement) and self.is_var:
            return True
        else: return False

    @codon.jit
    def has_common(self, term, same_term: bool=True) -> bool:
        # term: Type['Term']
        if not term.is_atom: return False
        return self == term

    # @codon.jit
    def do_hashing(self):        
        self._hash_value = hash(self.word_sorted+str(tuple(vars.indices_normalized for vars in self.variables)))
        return self._hash_value

    @codon.jit
    def __hash__(self) -> int:
        return self._hash_value if self._hash_value is not None else self.do_hashing()
    
    @codon.jit
    def __eq__(self, o) -> bool:
        # o: Type['Term']
        return self.identical(o) and self.vars_independent.indices == o.vars_independent.indices and self.vars_dependent.indices == o.vars_dependent.indices and self.vars_query.indices == o.vars_query.indices

    @codon.jit
    def __contains__(self, term) -> bool:
        # for sub_term in self.sub_terms:
        #     if term.identical()
        return term in self.sub_terms

    @codon.jit
    def __str__(self) -> str:
        return self.word
    
    # @codon.jit
    def __repr__(self) -> str:
        return f'<Term: {str(self)}>'
    
    @codon.jit
    def __len__(self):
        return len(self._components)

    @codon.jit
    def __getitem__(self, index: List[int]):
        if len(index) > 0 or not (len(index)==0 or index[0]== 0 or index[0] == -1): raise Exception("Out of bounds.")
        return self

    @codon.jit
    def repr(self, is_input=False):
        return str(self) # if not self.has_var else self.repr_with_var(self._vars_independent, [])

    # def repr_with_var(self, index_var: IndexVar, pos: list):
    #     ''''''
    #     # raise "Invalid case."
    #     return str(self)

    # @codon.jit
    def _handle_variables(self, terms: Iterable['Term']):
        ''''''
        self.has_var = bool(sum(tuple(term.has_var for term in terms)))
        self.has_ivar = bool(sum(tuple(term.has_ivar for term in terms)))
        self.has_dvar = bool(sum(tuple(term.has_dvar for term in terms)))
        self.has_qvar = bool(sum(tuple(term.has_qvar for term in terms)))
    
    @staticmethod
    def _init_variables(variables: Tuple[IndexVar, IndexVar, IndexVar], terms: Iterable['Term']):
        ''''''
        for term in terms:
            for idxvar1, idxvar2 in zip(variables, term.variables):
                idxvar1.connect(idxvar2)


    def _rebuild_vars(self):
        ''''''
        if self.has_ivar: self.vars_independent.rebuild()
        else: self.vars_independent._is_built = True
        if self.has_dvar: self.vars_dependent.rebuild()
        else: self.vars_dependent._is_built = True
        if self.has_qvar: self.vars_query.rebuild()
        else: self.vars_query._is_built = True

    def _build_vars(self):
        ''''''
        if self.has_ivar: self.vars_independent.build(); 
        else: self.vars_independent._is_built = True
        if self.has_dvar: self.vars_dependent.build()
        else: self.vars_dependent._is_built = True
        if self.has_qvar: self.vars_query.build()
        else: self.vars_query._is_built = True



    def clone(self):
        # clone = copy(self)
        return self

    def _normalize_variables(self):
        ''''''
        if self.has_var:
            if self.has_ivar:
                for idx, idx_norm in zip(self.vars_independent.indices, self.vars_independent.indices_normalized):
                    idx(int(idx_norm))
            if self.has_dvar:
                for idx, idx_norm in zip(self.vars_dependent.indices, self.vars_dependent.indices_normalized):
                    idx(int(idx_norm))
            if self.has_qvar:
                for idx, idx_norm in zip(self.vars_query.indices, self.vars_query.indices_normalized):
                    idx(int(idx_norm))


place_holder = Term('_', True)
