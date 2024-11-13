from enum import Enum


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

    def __int__(self):
        return self.value
