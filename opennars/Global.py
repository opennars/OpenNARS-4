import inspect

time = 0
_input_id = 0
def get_input_id():
    global _input_id
    input_id = _input_id
    _input_id += 1
    return input_id

class States:
    task = None
    belief = None
    term_belief = None
    concept = None
    rules = None
    tasks_derived = None

    @classmethod
    def reset(cls):
        ''''''
        for name in vars(cls):
            attr = getattr(cls, name)
            if inspect.ismethod(attr): continue
            if name.startswith('_'): continue
            if isinstance(attr, property): continue
            # if isinstance(attr, classmethod): continue
            setattr(cls, name, None)

    @classmethod
    def record_premises(cls, task=None, belief=None, term_belief=None):
        cls.task = task
        cls.belief = belief
        cls.term_belief = term_belief
    
    @classmethod
    def record_concept(cls, concept=None):
        cls.concept = concept

    @classmethod
    def record_rules(cls, rules=None):
        cls.rules = rules
    
    @property
    def time(self):
        return time
    
    @classmethod
    def __repr__(cls):
        return f'<States: time={time}\n\tconcept: {cls.concept}\n\ttask: {cls.task}\n\tbelief: {cls.belief}\n\trules: {cls.rules}\n>.'