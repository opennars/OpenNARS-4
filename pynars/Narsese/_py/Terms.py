from copy import copy
from typing import Iterable, List, Set, Type
from pynars.utils.IndexVar import IndexVar
from ordered_set import OrderedSet
from pynars.utils.tools import find_pos_with_pos, find_var_with_pos
from .Term import Term
from pynars import Global

class Terms:
    ''''''
    # index_var: IndexVar = None
    def __init__(self, terms: Iterable[Term], is_commutative: bool, is_input: bool=False) -> None:
        self._is_commutative = is_commutative

        terms = tuple(term.clone() for term in terms)
        terms_const: Iterable[Term] = tuple(term for term in terms if not term.has_var)
        terms_var: Iterable[Term] = tuple(term for term in terms if term.has_var)

        # convert terms's form <Term> into (<Terms>, (ivars), (dvars), (qvars)), so that the terms, which have variables, with the same hash-value can be distinguished.
        index_var = self.handle_index_var(terms_var, is_input=is_input)
        ivars = tuple(tuple(find_var_with_pos([i], index_var.var_independent, index_var.positions_ivar)) for i in range(len(terms_var)))
        dvars = tuple(tuple(find_var_with_pos([i], index_var.var_dependent, index_var.positions_dvar)) for i in range(len(terms_var)))
        qvars = tuple(tuple(find_var_with_pos([i], index_var.var_query, index_var.positions_qvar)) for i in range(len(terms_var)))
        terms_var = tuple(term for term in zip(terms_var, ivars, dvars, qvars))

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
        self._index_var = self.handle_index_var(self._terms, is_input=False)
        pass

    @property
    def is_commutative(self):
        return self._is_commutative
    
    
    @property
    def terms(self) -> Iterable[Term]:
        return self._terms

    def __repr__(self) -> str:
        word_terms = (str(component) if not component.has_var else component.repr_with_var(self._index_var, [i]) for i, component in enumerate(self.terms))
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

    # def convert(self):
    #     if self._is_commutative:
    #         terms = tuple((*(term for term in self._terms_const), *(term for term in self._terms_var)))
    #     else:
    #         bias = len(self._terms_const)
    #         order = ((bias + i if term.has_var else i) for i, term in enumerate(self._terms))
    #         terms = (self._terms_var[i-bias] if term.has_var else self._terms_const[i] for term, i in zip(self._terms, order))
            
    #     return terms
            
    @staticmethod
    def handle_index_var(terms: List['Term'], is_input: bool):
        index_var = IndexVar()
        
        indices_var_to_merge = []
        for i, term in enumerate(terms):
            if term.is_atom and term.is_var: 
                if term.is_ivar: index_var.add_ivar([i], name=repr(term))
                elif term.is_dvar: index_var.add_dvar([i], name=repr(term))
                elif term.is_qvar: index_var.add_qvar([i], name=repr(term))
            elif term.has_var: # but component itself is not variable
                if term.has_ivar:
                    for index in term.index_var.positions_ivar:
                        index_var.add_ivar([i]+index)
                if term.has_dvar:
                    for index in term.index_var.positions_dvar:
                        index_var.add_dvar([i]+index)
                if term.has_qvar:
                    for index in term.index_var.positions_qvar:
                        index_var.add_qvar([i]+index)
                indices_var_to_merge.append(term.index_var)
        index_var.merge(*indices_var_to_merge, is_input=is_input)
        index_var.normalize()
        return index_var


    def clone(self):
        ''''''
        clone = copy(self)
        clone._index_var = clone._index_var.clone()
        return clone


    def intersection(self, *tuple_terms: Type['Terms'], is_input: bool=False):
        '''
        it make sense only when self.is_commutative is True
        '''
        if self.is_commutative:
            if is_input: Terms.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)


            terms_const = OrderedSet.intersection(self._terms_const, *(terms._terms_const for terms in tuple_terms))
            terms_var = OrderedSet.intersection(self._terms_var, *(terms._terms_var for terms in tuple_terms))
            terms = tuple((*terms_const, *(term[0] for term in terms_var)))
            terms_intersection = Terms(terms, is_commutative=True, is_input=False)
        else: terms_intersection = None
        return terms_intersection


    def union(self, *tuple_terms: Type['Terms'], is_input: bool=False):
        '''
        it make sense only when self.is_commutative is True
        '''
        if self.is_commutative:
            if is_input: self.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)
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
        if is_input: self.handle_index_var((*(self), *(term for terms in tuple_terms for term in terms)), True)
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