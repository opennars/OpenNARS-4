from opennars.Narsese._py.Connector import Connector
from .Copula import Copula
from opennars.Config import Enable, Config
from typing import Iterable, List, Set, Type
from enum import Enum
from opennars.utils.IndexVar import IndexVar
from ordered_set import OrderedSet
from copy import copy, deepcopy
from bidict import bidict
from typing import Tuple
from .Tense import TemporalOrder

class TermType(Enum):
    ATOM = 0
    STATEMENT = 1
    COMPOUND = 2

class Term:
    type = TermType.ATOM
    copula: Copula = None
    connector: Connector = None
    _complexity: int = 1 # The complexity of the term. Read only.
    has_var: bool = False # Whether the term contains variable(s).
    has_ivar: bool = False # Whether the term contains independent variable(s).
    has_dvar: bool = False # Whether the term contains dependent variable(s).
    has_qvar: bool = False # Whether the term contains query variable(s).
    is_var: bool = False
    is_ivar: bool = False
    is_dvar: bool = False
    is_qvar: bool = False
    is_closed: bool = True # Whether the term is closed or open in terms of variable.

    is_interval: bool = False

    is_operation = False

    components: set['Term'] = None

    normalized: bool = True # used for variable normalization

    
    def __init__(self, word, do_hashing=False) -> None:
        self.word = word

        # id initialization
        if do_hashing: self.do_hashing()
        else: self._hash_value = None
    
    @property
    def recursive_terms(self) -> Iterable['Term']:
        return (self, )

    @property
    def simplicity(self):
        return self._complexity ** -Config.r_term_complexity_unit

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
    def is_mental_operation(self):
        return False
    
    @property
    def is_constant(self):
        return not self.has_var
    
    @property
    def temporal_order(self):
        return TemporalOrder.NONE

    def contains_term(self, term: 'Term') -> bool:
        return self == term
    
    def contains_term_recursively(self, term: 'Term') -> bool:
        return self == term

    def do_hashing(self):        
        self._hash_value = hash(self.word)
        return self._hash_value
    
    def contain_term(self, target: 'Term') -> bool:
        '''
        Recursively check if a compound contains a term
        
        Args:
            target: The term to be searched
        Returns:
            Whether the two have the same content
        '''
        return self == target

    def __hash__(self) -> int:
        return self._hash_value if self._hash_value is not None else self.do_hashing()
    
    def __eq__(self, o: 'Term') -> bool:
        return hash(self) == hash(o)

    def __contains__(self, term: 'Term') -> bool:
        return self == term

    def __str__(self) -> str:
        return self.word
    
    def __repr__(self) -> str:
        return f'<Term: {str(self)}>'
    
    def __len__(self):
        return 1

    def __getitem__(self, index: List[int]) -> Type['Term']:
        return None

    def repr(self, is_input=False):
        return str(self) # if not self.has_var else self.repr_with_var(self._vars_independent, [])

    def clone(self):
        term = copy(self)
        return term
    
    def deep_clone(self):
        return self.clone()


place_holder = Term('_', True)