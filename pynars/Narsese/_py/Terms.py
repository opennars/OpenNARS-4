from copy import copy, deepcopy
from typing import Iterable, List, Set, Type
from pynars.utils.IndexVar import IndexVar
from ordered_set import OrderedSet
from pynars.utils.tools import find_pos_with_pos, find_var_with_pos
from .Term import Term
from pynars import Global
from typing import Tuple

class Terms:
    ''''''
    # index_var: IndexVar = None
    _vars_independent: IndexVar = None
    _vars_dependent: IndexVar = None
    _vars_query: IndexVar = None
    def __init__(self, terms: Iterable[Term], is_commutative: bool, **kwargs) -> None:
        self._is_commutative = is_commutative

        terms = tuple(term.clone() for term in terms)
        terms_const: Iterable[Term] = tuple(term for term in terms if not term.has_var)
        # terms_var: Iterable[Term] = tuple(term for term in terms if term.has_var)

        if self._vars_independent is None: self._vars_independent = IndexVar()
        if self._vars_dependent is None: self._vars_dependent = IndexVar()
        if self._vars_query is None: self._vars_query = IndexVar()

        # convert terms's form <Term> into (<Term>, (ivars), (dvars), (qvars)), so that the terms, which have variables, with the same hash-value can be distinguished.
        Term._init_variables(self.variables, terms) # self.handle_index_var(terms_var, is_input=is_input)
        self._build_vars()
        # ivars = tuple(tuple(find_var_with_pos([i], self._vars_independent.indices, self._vars_independent.positions)) for i in range(len(terms_var)))
        # dvars = tuple(tuple(find_var_with_pos([i], self._vars_dependent.indices, self._vars_independent.positions)) for i in range(len(terms_var)))
        # qvars = tuple(tuple(find_var_with_pos([i], self._vars_query.indices, self._vars_query.positions)) for i in range(len(terms_var)))
        ivars = tuple(tuple(idxvar.indices) for idxvar in self._vars_independent.successors)
        dvars = tuple(tuple(idxvar.indices) for idxvar in self._vars_dependent.successors)
        qvars = tuple(tuple(idxvar.indices) for idxvar in self._vars_query.successors)
        terms_var = tuple((term, ivar, dvar, qvar) for term, ivar, dvar, qvar in zip(terms, ivars, dvars, qvars) if term.has_var)

        # store the terms
        if is_commutative: 
            self._terms_const = OrderedSet(terms_const)
            self._terms_var = OrderedSet(terms_var)
            self._terms = tuple((*self._terms_const, *(term[0] for term in self._terms_var)))
        else:
            self._terms_const = terms_const
            self._terms_var = terms_var
            self._terms = terms

        # set index_var
        # TODO
        # self._index_var = self.handle_index_var(self._terms, is_input=False)
        pass

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

    
    def _rebuild_vars(self):
        ''''''
        self._vars_independent.rebuild()
        self._vars_dependent.rebuild()
        self._vars_query.rebuild()

    def _build_vars(self):
        ''''''
        self._vars_independent.build()
        self._vars_dependent.build()
        self._vars_query.build()