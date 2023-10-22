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
Evaluate   = Operation('evaluate',   True, is_mental_operation=True)

# With reference to book NAL(2012)
Observe   = Operation('observe',     True, is_mental_operation=True)
'''get an active task from the task buffer'''

Expect    = Operation('expect',      True, is_mental_operation=True)
'''check the input for a given statement'''

Know      = Operation('know',        True, is_mental_operation=True)
'''find the truth-value of a statement'''

Assess    = Operation('assess',      True, is_mental_operation=True)
'''find the desire-value of a statement'''

Believe   = Operation('believe',     True, is_mental_operation=True)
'''turn a statement into a task containing a judgment'''

Want      = Operation('want',        True, is_mental_operation=True)
'''turn a statement into a task containing a goal'''

Wonder    = Operation('wonder',      True, is_mental_operation=True)
'''turn a statement into a task containing a question'''

Remember  = Operation('remember',    True, is_mental_operation=True)
'''turn a statement into a belief'''

Consider  = Operation('consider',    True, is_mental_operation=True)
'''do inference on a concept'''

Remind    = Operation('remind',      True, is_mental_operation=True)
'''activate a concept'''

Doubt     = Operation('doubt',       True, is_mental_operation=True)
'''decrease the confidence of a belief'''

Hesitate  = Operation('hesitate',    True, is_mental_operation=True)
'''decrease the confidence of a goal'''

Assume    = Operation('assume',      True, is_mental_operation=True)
'''temporarily take a statement as a belief'''

Name      = Operation('name',        True, is_mental_operation=True)
'''create a simple internal ID to a useful compound term'''

Wait      = Operation('wait',        True, is_mental_operation=True)
'''pause the system’s action for a given number of working cycles'''

Repeat    = Operation('repeat',      True, is_mental_operation=True)
'''execute an action repeatedly under a given condition'''

Tell      = Operation('tell',        True, is_mental_operation=True)
'''produce an outgoing task containing a judgment'''

Demand    = Operation('demand',      True, is_mental_operation=True)
'''produce an outgoing task containing a goal'''

Ask       = Operation('ask',         True, is_mental_operation=True)
'''produce an outgoing task containing a question'''

Check     = Operation('check',       True, is_mental_operation=True)
'''produce an outgoing task containing a query'''

Register  = Operation('register',    True, is_mental_operation=True)
'''let a term be used as an operator'''
