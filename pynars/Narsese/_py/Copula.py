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