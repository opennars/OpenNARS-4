from .Term import Term

class Operator(Term):
    
    is_operation = True # ? If it changed the type of statements also need to change, but if rename it, two properties with different names will occur. Same as 'is_mental_operation'

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

Anticipate = Operator('anticipate', True, is_mental_operation=True)
Evaluate   = Operator('evaluate',   True, is_mental_operation=True)

# With reference to book NAL(2012)
Observe   = Operator('observe',     True, is_mental_operation=True)
'''get an active task from the task buffer'''

Expect    = Operator('expect',      True, is_mental_operation=True)
'''check the input for a given statement'''

Know      = Operator('know',        True, is_mental_operation=True)
'''find the truth-value of a statement'''

Assess    = Operator('assess',      True, is_mental_operation=True)
'''find the desire-value of a statement'''

Believe   = Operator('believe',     True, is_mental_operation=True)
'''turn a statement into a task containing a judgment'''

Want      = Operator('want',        True, is_mental_operation=True)
'''turn a statement into a task containing a goal'''

Wonder    = Operator('wonder',      True, is_mental_operation=True)
'''turn a statement into a task containing a question'''

Remember  = Operator('remember',    True, is_mental_operation=True)
'''turn a statement into a belief'''

Consider  = Operator('consider',    True, is_mental_operation=True)
'''do inference on a concept'''

Remind    = Operator('remind',      True, is_mental_operation=True)
'''activate a concept'''

Doubt     = Operator('doubt',       True, is_mental_operation=True)
'''decrease the confidence of a belief'''

Hesitate  = Operator('hesitate',    True, is_mental_operation=True)
'''decrease the confidence of a goal'''

Assume    = Operator('assume',      True, is_mental_operation=True)
'''temporarily take a statement as a belief'''

Name      = Operator('name',        True, is_mental_operation=True)
'''create a simple internal ID to a useful compound term'''

Wait      = Operator('wait',        True, is_mental_operation=True)
'''pause the system’s action for a given number of working cycles'''

Repeat    = Operator('repeat',      True, is_mental_operation=True)
'''execute an action repeatedly under a given condition'''

Tell      = Operator('tell',        True, is_mental_operation=True)
'''produce an outgoing task containing a judgment'''

Demand    = Operator('demand',      True, is_mental_operation=True)
'''produce an outgoing task containing a goal'''

Ask       = Operator('ask',         True, is_mental_operation=True)
'''produce an outgoing task containing a question'''

Check     = Operator('check',       True, is_mental_operation=True)
'''produce an outgoing task containing a query'''

Register  = Operator('register',    True, is_mental_operation=True)
'''let a term be used as an operator'''
