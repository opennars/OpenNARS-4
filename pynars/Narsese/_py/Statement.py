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
    
    def __init__(self, subject: Term, copula: Copula, predicate: Term, is_input: bool=False, is_subterm=True) -> None:
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

        # self._height = max((self.subject._height, self.predicate._height))+1

        ''' Variables related initialization '''
        terms = (self.subject, self.predicate)
        self._handle_variables(terms)
        self._init_variables(self.variables, terms)
        self._build_vars()

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
    def is_predictive(self):
        return self.copula.is_predictive
    
    @property
    def is_concurrent(self):
        return self.copula.is_concurrent
    
    @property
    def is_retrospective(self):
        return self.copula.is_retrospective

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
    
    def repr(self, *args):
        '''
        index_var (IndexVar): the `index_var` of the root/topmost term.
        pos (list): the position of the current term within the root/topmost term.
        '''
        word_subject = str(self.subject) if not self.subject.has_var else self.subject.repr()
        word_predicate = str(self.predicate) if not self.predicate.has_var else self.predicate.repr()
        
        return f'<{word_subject+" "+str(self.copula.value)+" "+word_predicate}>'

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

    def concurrent(self):
        return Statement(self.subject, self.copula.get_concurent, self.predicate)

    def predictive(self):
        return Statement(self.subject, self.copula.get_predictive, self.predicate)

    def retrospective(self):
        return Statement(self.subject, self.copula.get_retrospective, self.predicate)

    def temporal_swapped(self):
        if self.copula is Copula.PredictiveEquivalence:
            return self # TODO: could be handled by introducing <\> copula
        return Statement(self.predicate, self.copula.get_temporal_swapped, self.subject)
    
    def clone(self):
        if not self.has_var: return self
        # now, not self.has_var
        clone = copy(self)
        clone.subject = self.subject.clone()
        clone.predicate = self.predicate.clone()

        clone._vars_independent = IndexVar() # self._vars_independent.clone()
        clone._vars_dependent = IndexVar() # self._vars_dependent.clone()
        clone._vars_query = IndexVar() # self._vars_query.clone()
        for idx in (clone.subject._vars_independent, clone.predicate._vars_independent): clone._vars_independent.connect(idx, True)
        for idx in (clone.subject._vars_dependent, clone.predicate._vars_dependent): clone._vars_dependent.connect(idx, True)
        for idx in (clone.subject._vars_query, clone.predicate._vars_query): clone._vars_query.connect(idx, True)
        
        
        return clone
