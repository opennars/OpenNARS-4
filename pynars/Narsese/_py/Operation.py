from .Term import Term

class Operation(Term):
    
    is_operation = True

    def __init__(self, word, do_hashing=False, is_mental_operation=False) -> None:
        super().__init__(word, do_hashing=do_hashing)
        self._is_mental_operation = is_mental_operation

    @property
    def is_mental_operation(self):
        return self._is_mental_operation
    
    def __str__(self) -> str:
        return "^" + str(self.word)
    
    def __repr__(self) -> str:
        return f'<Operation: {str(self)}>'

    def do_hashing(self):
        self._hash_value = hash(str(self))
        return self._hash_value


Anticipate = Operation('anticipate', True, is_mental_operation=True)
Believe    = Operation('believe',    True, is_mental_operation=True)
Doubt      = Operation('doubt',      True, is_mental_operation=True)
Evaluate   = Operation('evaluate',   True, is_mental_operation=True)
Hesitate   = Operation('hesitate',   True, is_mental_operation=True)
Want       = Operation('want',       True, is_mental_operation=True)
Wonder     = Operation('wonder',     True, is_mental_operation=True)