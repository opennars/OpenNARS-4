from copy import copy
from pynars.NAL.Functions.Tools import project_truth, revisible
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Term import Term
from ..DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ..RuleMap import RuleCallable, RuleMap
from pynars.NAL.Inference import local__revision
from pynars import Global


class Engine:
    rule_map: RuleMap
    def __init__(self):
        pass


    @classmethod
    def match(cls, *args, **kwargs):
        pass


    def step(self, *args, **kwargs):
        pass

    def build(self):
        self.rule_map.build()