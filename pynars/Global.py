import inspect
from pynars.Narsese import Global as _Global

class StatesCls:
    task = None
    belief = None
    concept = None
    rules = None

    @classmethod
    def reset(cls):
        ''''''
        for name in vars(cls):
            attr = getattr(cls, name)
            if inspect.ismethod(attr):
                continue
            if name.startswith('_'):
                continue
            if isinstance(attr, property):
                continue
            # if isinstance(attr, classmethod): continue
            setattr(cls, name, None)

    @classmethod
    def record_premises(cls, task=None, belief=None):
        cls.task = task
        cls.belief = belief

    @classmethod
    def record_concept(cls, concept=None):
        cls.concept = concept

    @classmethod
    def record_rules(cls, rules=None):
        cls.rules = rules

    @property
    def time(self):
        return _Global.time

    @time.setter
    def time(self, value):
        _Global.time = value

    @staticmethod
    def get_input_id():
        return _Global.get_input_id()

    @classmethod
    def __repr__(cls):
        return f'<States: time={cls.time}\n\tconcept: {cls.concept}\n\ttask: {cls.task}\n\tbelief: {cls.belief}\n\trules: {cls.rules}\n>.'


Global = StatesCls()
