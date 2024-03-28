# from enum import Enum
from pynars.utils.IdEnum import IdEnum
# from .Term import Term

class Connector(IdEnum):
    Conjunction = "&&"
    Disjunction = "||"
    Product = "*"
    ParallelEvents = "&|"
    SequentialEvents = "&/"
    IntensionalIntersection = "|"
    ExtensionalIntersection = "&"
    ExtensionalDifference = "-"
    IntensionalDifference = "~"
    Negation = "--"
    IntensionalSet = "["
    ExtensionalSet = "{"
    IntensionalImage = "\\"
    ExtensionalImage = "/"
    List = "#"

    @property
    def is_commutative(self):
        return self in (
            Connector.Conjunction, 
            Connector.Disjunction, 
            Connector.ParallelEvents,
            Connector.IntensionalIntersection,
            Connector.ExtensionalIntersection,
            Connector.IntensionalSet,
            Connector.ExtensionalSet
        )
    @property
    def is_single_only(self):
        return self in (
            Connector.Negation,
        )
    
    @property
    def is_double_only(self):
        return self in (
            Connector.ExtensionalDifference, 
            Connector.IntensionalDifference
        )
    
    @property
    def is_multiple_only(self):
        return self in (
            Connector.Conjunction, 
            Connector.Disjunction, 
            # Connector.Product, 
            Connector.ParallelEvents,
            Connector.SequentialEvents,
            Connector.IntensionalIntersection,
            Connector.ExtensionalIntersection,
            Connector.ExtensionalDifference,
            Connector.IntensionalDifference,
            Connector.IntensionalImage,
            Connector.ExtensionalImage
        )

    @property
    def is_temporal(self):
        return self in (Connector.SequentialEvents, Connector.ParallelEvents)

    @property
    def is_predictive(self):
        return self is Connector.SequentialEvents
    
    @property
    def is_concurrent(self):
        return self is Connector.ParallelEvents

    @property
    def get_atemporal(self):
        if self is Connector.SequentialEvents \
        or self is Connector.ParallelEvents:
            return Connector.Conjunction
        return self
    
    @property
    def get_concurent(self):
        if self is Connector.Conjunction:
            return Connector.ParallelEvents
        return self

    @property
    def get_predictive(self):
        if self is Connector.Conjunction:
            return Connector.SequentialEvents
        return self
    
    def check_valid(self, len_terms: int):
        if self.is_single_only: return len_terms == 1
        elif self.is_double_only: return len_terms == 2
        elif self.is_multiple_only: return len_terms > 1
        else: return len_terms > 0
    
    # @property
    # def is_higher_order(self):
    #     return self in (
    #         Connector.Conjunction, 
    #         Connector.Disjunction, 
    #         Connector.ParallelEvents,
    #         Connector.IntensionalIntersection,
    #         Connector.ExtensionalIntersection,
    #         Connector.IntensionalSet,
    #         Connector.ExtensionalSet
    #     )

# place_holder = Term('_', True)