from copy import copy
import enum
from pynars.Config import Enable
from pynars.utils.IndexVar import IndexVar
from .Term import Term, TermType
from .Copula import Copula
from typing import List, Type
# from .Compound import *f
from ordered_set import OrderedSet

class Statement(Term):
    type = TermType.STATEMENT
    
    def __init__(self, subject: Term, copula: Copula, predicate: Term, is_input: bool=False) -> None:
        self._is_commutative = copula.is_commutative
        word = "<"+str(subject)+str(copula.value)+str(predicate)+">"
        if self.is_commutative:
            subject_word, predicate_word = sorted((subject, predicate), key=hash)
            word_sorted = "<"+subject_word.word_sorted+str(copula.value)+predicate_word.word_sorted+">"
        else: word_sorted = "<"+subject.word_sorted+str(copula.value)+predicate.word_sorted+">"
        super().__init__(word, word_sorted=word_sorted)

        self.subject = subject
        self.copula = copula
        self.predicate = predicate

        self._components = OrderedSet((*self.subject.sub_terms, *self.predicate.sub_terms))
        self._complexity += (subject.complexity + predicate.complexity)
        self._is_higher_order = copula.is_higher_order

        self.is_operation = self.predicate.is_operation

        if Enable.variable:
            terms = (self.subject, self.predicate)
            self.handle_variables(terms)
            self._index_var = self.handle_index_var(terms, is_input, self._index_var)

        pass
        
    def __getitem__(self, index: List[int]) -> Term:
        if isinstance(index, int): index = (index,)
        if len(index) == 0: return self
        
        idx = index[0]
        if idx > 1: raise "Out of bounds."

        index = index[1:]
        term = self.subject if idx == 0 else self.predicate
        return term.__getitem__(index)

    @property
    def is_commutative(self):
        return self._is_commutative
    
    @property
    def is_higher_order(self):
        return self._is_higher_order

    @property
    def terms(self):
        return (self.subject, self.predicate)

    def equal(self, o: Type['Statement']) -> bool:
        '''
        Return:
            is_equal (bool), is_replacable(bool)
        '''

        if o.is_statement:
            if not self.copula is o.copula: return False

            if self.subject.equal(o.subject) and self.predicate.equal(o.predicate): return True
            elif not o.is_commutative: return False
            else: return self.subject.equal(o.predicate) and self.predicate.equal(o.subject)

        elif o.is_atom and o.is_var:
            return True
        else: return False
            

    def has_common(self, statement: Type['Statement'], same_copula: bool=True) -> bool:
        if not statement.is_statement: return False
        return ((statement.copula is self.copula) if same_copula else True) and (not {self.subject, self.predicate}.isdisjoint({statement.subject, statement.predicate}))


    def __repr__(self) -> str:
        return  f'<Statement: {self.repr()}>'
    
    def repr_with_var(self, index_var: IndexVar, pos: list):
        '''
        index_var (IndexVar): the `index_var` of the root/topmost term.
        pos (list): the position of the current term within the root/topmost term.
        '''
        word_subject = str(self.subject) if not self.subject.has_var else self.subject.repr_with_var(index_var, pos+[0])
        word_predicate = str(self.predicate) if not self.predicate.has_var else self.predicate.repr_with_var(index_var, pos+[1])
        
        return f'<{word_subject+str(self.copula.value)+word_predicate}>'

    @classmethod
    def Inheritance(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.Inheritance, predicate, is_input)
    
    
    @classmethod
    def Implication(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.Implication, predicate, is_input)


    @classmethod
    def Similarity(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.Similarity, predicate, is_input)

    
    @classmethod
    def Equivalence(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.Equivalence, predicate, is_input)


    @classmethod
    def PredictiveImplication(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.PredictiveImplication, predicate, is_input)


    @classmethod
    def ConcurrentImplication(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.ConcurrentImplication, predicate, is_input)


    @classmethod
    def RetrospectiveImplication(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.RetrospectiveImplication, predicate, is_input)


    @classmethod
    def PredictiveEquivalence(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.PredictiveEquivalence, predicate, is_input)


    @classmethod
    def ConcurrentEquivalence(cls, subject: Term, predicate: Term, is_input: bool=False):
        return cls(subject, Copula.ConcurrentEquivalence, predicate, is_input)

    def clone(self):
        if not self.has_var: return self
        # now, not self.has_var
        clone = copy(self)
        clone.subject = self.subject.clone()
        clone.predicate = self.predicate.clone()
        clone._index_var = self._index_var.clone()
        
        return clone
