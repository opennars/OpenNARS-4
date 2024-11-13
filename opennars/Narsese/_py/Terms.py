from copy import copy, deepcopy
from typing import Iterable, List, Set, Type
from opennars.utils.IndexVar import IndexVar
from ordered_set import OrderedSet
from opennars.utils.tools import find_pos_with_pos, find_var_with_pos
from .Term import Term
from opennars import Global
from typing import Tuple

class Terms:
    ''''''
    def __init__(self, terms: Iterable[Term], is_commutative: bool, **kwargs) -> None:
        self._is_commutative = is_commutative
        terms = tuple(term.clone() for term in terms)
        self._terms = terms

    @property
    def is_commutative(self):
        return self._is_commutative
    
    @property
    def terms(self) -> Iterable[Term]:
        return self._terms

    def __repr__(self) -> str:
        word_terms = (str(component) if not component.has_var else component.repr() for i, component in enumerate(self.terms))
        if self.is_commutative:
            return f"<Terms: {{{', '.join(word_terms)}}}>"
        else:
            return f"<Terms: ({', '.join(word_terms)})>"

    def __iter__(self):
        return iter(self._terms)

    def __len__(self):
        return len(self._terms)

    def __getitem__(self, index):
        return self._terms.__getitem__(index)

    
    def __sub__(self, o: Type['Terms']):
        ''''''
        return self.difference(o)
    
    @property
    def variables(self) -> Tuple[IndexVar, IndexVar, IndexVar]:
        return (self._vars_independent, self._vars_dependent, self._vars_query)

            
    # @staticmethod
    # def init_variables(terms: List['Term'], is_input: bool):
    #     index_var = IndexVar()
    #     # Term.init_variables(terms, is_input, index_var) # TODO
    #     return index_var


    def clone(self):
        ''''''
        clone = deepcopy(self)
        # clone = copy(self)
        # clone._vars_independent = IndexVar() # self._vars_independent.clone()
        # clone._vars_dependent = IndexVar() # self._vars_dependent.clone()
        # clone._vars_query = IndexVar() # self._vars_query.clone()
        # for term in clone.terms: clone._vars_independent.connect(term._vars_independent, True)
        # for term in clone.terms: clone._vars_dependent.connect(term._vars_dependent, True)
        # for term in clone.terms: clone._vars_query.connect(term._vars_query, True) 
        return clone


    def intersection(self, *tuple_terms: Type['Terms'], is_input: bool=False):
        '''
        it make sense only when self.is_commutative is True
        '''
        if self.is_commutative:
            # if is_input: Terms.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)
            terms_const = OrderedSet.intersection(self._terms_const, *(terms._terms_const for terms in tuple_terms))
            terms_var = OrderedSet.intersection(self._terms_var, *(terms._terms_var for terms in tuple_terms))
            terms = tuple((*terms_const, *(term[0] for term in terms_var)))
            terms_intersection = Terms(terms, is_commutative=True, is_input=False)
            # Term._init_variables(terms_intersection.variables, terms)
            # terms_intersection._build_vars()
        else: terms_intersection = None
        return terms_intersection


    def union(self, *tuple_terms: Type['Terms'], is_input: bool=False):
        '''
        it make sense only when self.is_commutative is True
        '''
        if self.is_commutative:
            # if is_input: self.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)
            terms_const = OrderedSet.union(self._terms_const, *(terms._terms_const for terms in tuple_terms))
            terms_var = OrderedSet.union(self._terms_var, *(terms._terms_var for terms in tuple_terms))
            terms = tuple((*terms_const, *(term[0] for term in terms_var)))
            terms_union = Terms(terms, is_commutative=True, is_input=False)
        else: terms_union = None
        return terms_union


    def difference(self, *tuple_terms: Type['Terms'], is_input: bool=False):
        '''
        it make sense only when self.is_commutative is True
        '''
        # if self.is_commutative:
        # if is_input: self.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)
        terms_const = OrderedSet.difference(self._terms_const, *(terms._terms_const for terms in tuple_terms))
        terms_var = OrderedSet.difference(self._terms_var, *(terms._terms_var for terms in tuple_terms))
        terms = tuple((*terms_const, *(term[0] for term in terms_var)))
        terms_difference = Terms(terms, is_commutative=True, is_input=False)
        # else: 
        #     # TODO
        #     raise
        #     terms_difference = None
        return terms_difference

    def issuperset(self, terms_other: Type['Terms']):
        ''''''
        if self.is_commutative:
            issuperset_const = self._terms_const.issuperset(terms_other._terms_const)
            issuperset_var = self._terms_var.issuperset(terms_other._terms_var)
        else:
            issuperset_const = set(self._terms_const).issuperset(terms_other._terms_const)
            issuperset_var = set(self._terms_var).issuperset(terms_other._terms_var)
        issuperset = issuperset_const and issuperset_var
        return issuperset

    def isdisjoint(self, terms_other: Type['Terms']):
        if self.is_commutative:
            isdisjoint_const = self._terms_const.isdisjoint(terms_other._terms_const)
            isdisjoint_var = self._terms_var.isdisjoint(terms_other._terms_var)
        else:
            isdisjoint_const = set(self._terms_const).isdisjoint(terms_other._terms_const)
            isdisjoint_var = set(self._terms_var).isdisjoint(terms_other._terms_var)
        isdisjoint = isdisjoint_const and isdisjoint_var
        return isdisjoint

    def index(self, term: Term):
        ''''''
        return self._terms.index(term)
