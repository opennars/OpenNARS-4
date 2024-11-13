from copy import copy
import enum
from opennars.Config import Enable
from opennars.utils.IndexVar import IndexVar
from .Term import Term, TermType
from .Copula import Copula
from typing import List, Type
# from .Compound import *f
from ordered_set import OrderedSet
from collections import Counter

class Statement(Term):
    type = TermType.STATEMENT
    
    def __init__(self, subject: Term, copula: Copula, predicate: Term, is_input: bool=False, is_subterm=True) -> None:
        self._is_commutative = copula.is_commutative
        if self.is_commutative:
            subject, predicate = sorted((subject, predicate), key=hash)
        word = f"<{str(subject)}{str(copula.value)}{str(predicate)}>"
        super().__init__(word)

        self.subject = subject
        self.copula = copula
        self.predicate = predicate

        self._complexity += (subject.complexity + predicate.complexity)
        self._is_higher_order = copula.is_higher_order

        self.is_operation = self.predicate.is_operation

    def __getitem__(self, index: List[int]) -> Term:
        if isinstance(index, int): index = (index,)
        if len(index) == 0: return self
        
        idx = index[0]
        if idx > 1: raise "Out of bounds."

        index = index[1:]
        term = self.subject if idx == 0 else self.predicate
        return term.__getitem__(index)

    @property
    def recursive_terms(self):
        return (*self.subject.recursive_terms, *self.predicate.recursive_terms)
    
    @property
    def is_commutative(self):
        return self._is_commutative
    
    @property
    def is_higher_order(self):
        return self._is_higher_order


    def contains_component(self, t: Term) -> bool:
        '''
        Check whether the compound contains a certain component

        Args:
            t: The component to be checked
        Returns:
            Whether the component is in the compound
        '''
        return t == self.subject or t == self.predicate
    
    def contains_term(self, target: Term, count_self: bool=False) -> bool:
        '''
        Recursively check if a compound contains a term
        Args:
            target: The term to be searched
            count_self: Whether to count the compound itself
        Returns:
            Whether the target is in the current term
        '''
        if count_self:
            if Term.contains_term(self, target):
                return True
        for term in (self.subject, self.predicate):
            if term.contains_term(target):
                return True
        return False
    

    def count_term_recursively(self, count_self: bool=False) -> dict[Term, int]:
        '''
        Recursively count how often the terms are contained

        Args:
            count_self: Whether to count the compound itself
        Returns:
            The counts of the terms
        '''
        map: dict[Term, int] = dict(Counter(self.recursive_terms))
        if count_self:
            map[self] = 1
        return map

    def contains_all_components(self, t: 'Term|Statement') -> bool:
        '''
        Check whether the compound contains all components of another term, or that term as a whole
        Args:
            t: The other term
        Returns:
            Whether the components are all in the compound
        
        '''
        if t.is_statement and (t.copula is self.copula):
            components1 = set(t.subject, t.predicate)
            components2 = set(self.subject, self.predicate)
            return components1 <= components2
        else:
            return t in self.components

    # def equal(self, o: Type['Statement']) -> bool:
    #     '''
    #     Return:
    #         is_equal (bool), is_replacable(bool)
    #     '''

    #     if o.is_statement:
    #         if not self.copula is o.copula: return False

    #         if self.subject.equal(o.subject) and self.predicate.equal(o.predicate): return True
    #         elif not o.is_commutative: return False
    #         else: return self.subject.equal(o.predicate) and self.predicate.equal(o.subject)

    #     elif o.is_atom and o.is_var:
    #         return True
    #     else: return False
            

    # def has_common(self, statement: Type['Statement'], same_copula: bool=True) -> bool:
    #     if not statement.is_statement: return False
    #     return ((statement.copula is self.copula) if same_copula else True) and (not {self.subject, self.predicate}.isdisjoint({statement.subject, statement.predicate}))

    def contain_term(self, target: Term) -> bool:
        '''
        Recursively check if a compound contains a term
        
        Args:
            target: The term to be searched
        Returns:
            Whether the two have the same content
        '''
        for term in (self.subject, self.predicate):
            if term.contain_term(target):
                return True
        return False
    
    def __repr__(self) -> str:
        return  f'<Statement: {self.repr()}>'
    
    # def repr(self, *args):
    #     '''
    #     index_var (IndexVar): the `index_var` of the root/topmost term.
    #     pos (list): the position of the current term within the root/topmost term.
    #     '''
    #     word_subject = str(self.subject) if not self.subject.has_var else self.subject.repr()
    #     word_predicate = str(self.predicate) if not self.predicate.has_var else self.predicate.repr()
        
    #     return f'<{word_subject+str(self.copula.value)+word_predicate}>'

    @classmethod
    def Inheritance(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.Inheritance, predicate, is_input, is_subterm)
    
    
    @classmethod
    def Implication(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.Implication, predicate, is_input, is_subterm)


    @classmethod
    def Similarity(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.Similarity, predicate, is_input, is_subterm)

    
    @classmethod
    def Equivalence(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.Equivalence, predicate, is_input, is_subterm)


    @classmethod
    def PredictiveImplication(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.PredictiveImplication, predicate, is_input, is_subterm)


    @classmethod
    def ConcurrentImplication(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.ConcurrentImplication, predicate, is_input, is_subterm)


    @classmethod
    def RetrospectiveImplication(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.RetrospectiveImplication, predicate, is_input, is_subterm)


    @classmethod
    def PredictiveEquivalence(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.PredictiveEquivalence, predicate, is_input, is_subterm)


    @classmethod
    def ConcurrentEquivalence(cls, subject: Term, predicate: Term, is_input: bool=False, is_subterm=True):
        return cls(subject, Copula.ConcurrentEquivalence, predicate, is_input, is_subterm)

    def clone(self):
        if not self.has_var: return self
        # now, self.has_var is False
        clone = copy(self)
        clone.subject = self.subject.clone()
        clone.predicate = self.predicate.clone()
        
        return clone
