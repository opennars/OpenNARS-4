from enum import Enum

class IdEnum(Enum):
    def __new__(cls, value):
        if not hasattr(cls, '_copula_id'): cls._copula_id = 0
        member = object.__new__(cls)
        member._value_ = value
        member._copula_id = cls._copula_id
        cls._copula_id += 1
        return member

    def __int__(self):
        return self._copula_id