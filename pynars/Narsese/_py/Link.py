from enum import Enum
from .Item import Item
from .Budget import Budget
from .Task import Task 
from typing import List, Type
# from .Concept import *
from .import Concept

class LinkType(Enum):
    SELF = 0 # At C, point to C; TaskLink only 
    COMPONENT = 1 # At (&&, A, C), point to C
    COMPOUND = 2 # At C, point to (&&, A, C)
    COMPONENT_STATEMENT = 3 # At <C --> A>, point to C
    COMPOUND_STATEMENT = 4 # At C, point to <C --> A>
    COMPONENT_CONDITION = 5 # At <(&&, C, B) ==> A>, point to C
    COMPOUND_CONDITION = 6 # At C, point to <(&&, C, B) ==> A>
    TRANSFORM = 7 # At C, point to <(*, C, B) --> A>; TaskLink only
    TEMPORAL = 8 # At C, point to B, potentially without common subterm term



class Link(Item):
    link_id = 0
    type: LinkType
    component_index: List[int] # TODO: refer to OpenNARS 3.0.4, TermLink.java line 75 and TaskLink.java line 85. But why use it?
    def __init__(self, source: Item, target: Task, budget: Budget) -> None:
        self.link_id = Link.link_id
        hash_value = hash((source, target, self.link_id))
        super().__init__(hash_value, budget=budget)
        Link.link_id += 1
        
        self.source = source
        self.target = target
    
    def __str__(self) -> str:
        return f'{self.budget} {self.source.term} --- {self.target.term}'


class TermLink(Link):
    def __init__(self, source: Type['Concept'], target: Task, budget: Budget) -> None:
        super().__init__(source, target, budget)

class TaskLink(Link):
    def __init__(self, source: Type['Concept'], target: Type['Concept'], budget: Budget) -> None:
        super().__init__(source, target, budget)