# from enum import Enum
from pynars.utils.IdEnum import IdEnum

class Copula(IdEnum):
    Inheritance = "-->"
    Similarity = "<->"
    Instance = "{--"
    Property = "--]"
    InstanceProperty = "{-]"
    Implication = "==>"
    PredictiveImplication = "=/>"
    ConcurrentImplication = "=|>"
    RetrospectiveImplication = "=\>"
    Equivalence = "<=>"
    PredictiveEquivalence = "</>"
    ConcurrentEquivalence = "<|>"

    @property
    def is_commutative(self):
        return self in (Copula.Similarity, Copula.Equivalence, Copula.ConcurrentEquivalence)

    @property
    def is_higher_order(self):
        return self in (
            Copula.Implication,
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication,
            Copula.RetrospectiveImplication,
            Copula.Equivalence,
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        )
    
    @property
    def is_temporal(self):
        return self in (Copula.ConcurrentEquivalence, Copula.PredictiveEquivalence, Copula.ConcurrentImplication, Copula.PredictiveImplication, Copula.RetrospectiveImplication)
    
    @property
    def get_atemporal(self):
        if self is Copula.PredictiveImplication \
        or self is Copula.ConcurrentImplication \
        or self is Copula.RetrospectiveImplication:
            return Copula.Implication
        if self is Copula.PredictiveEquivalence \
        or self is Copula.ConcurrentEquivalence:
            return Copula.Equivalence
        return self
    
    @property
    def is_predictive(self):
        return self == Copula.PredictiveEquivalence or self == Copula.PredictiveImplication
    
    @property
    def is_concurrent(self):
        return self == Copula.ConcurrentEquivalence or self == Copula.ConcurrentImplication
    
    @property
    def is_retrospective(self):
        return self == Copula.RetrospectiveImplication
    
    @property
    def get_concurent(self):
        if self == Copula.Implication:
            return Copula.ConcurrentImplication
        if self == Copula.Equivalence:
            return Copula.ConcurrentEquivalence
        else:
            return self
    
    @property
    def get_predictive(self):
        if self == Copula.Implication:
            return Copula.PredictiveImplication
        if self == Copula.Equivalence:
            return Copula.PredictiveEquivalence
        else:
            return self

    @property
    def get_retrospective(self):
        if self == Copula.Implication:
            return Copula.RetrospectiveImplication
        # if self == Copula.Equivalence:
        #     return Copula.ConcurrentEquivalence
        else:
            return self
        
    @property
    def get_temporal_swapped(self):
        if self == Copula.PredictiveImplication:
            return Copula.RetrospectiveImplication
        if self == Copula.RetrospectiveImplication:
            return Copula.PredictiveImplication
        return self
        
    def symmetrize(self):
        if self is Copula.Inheritance:
            return Copula.Similarity
        elif self is Copula.Implication:
            return Copula.Equivalence
        elif self is Copula.ConcurrentImplication:
            return Copula.ConcurrentEquivalence
        elif self is Copula.PredictiveImplication:
            return Copula.PredictiveEquivalence
        else:
            raise "Invalid case."

    # def inverse(self):
    #     if self is Copula.PredictiveImplication:
    #         return Copula.RetrospectiveImplication
    #     elif self is Copula.RetrospectiveImplication:
    #         return Copula.PredictiveImplication
    #     else: 
    #         return self
                
    
    @property
    def reverse(self):
        if self is Copula.PredictiveImplication:
            return Copula.RetrospectiveImplication
        elif self is Copula.RetrospectiveImplication:
            return Copula.PredictiveImplication
        else:
            return self