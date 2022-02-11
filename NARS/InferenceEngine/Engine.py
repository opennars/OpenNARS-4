from copy import copy
from NAL.Functions.Tools import project_truth, revisible
from Narsese._py.Budget import Budget
from Narsese._py.Term import Term
from ..DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ..RuleMap import RuleCallable, RuleMap_v2
from NAL.Inference import local__revision
import Global


class Engine:
    
    rule_map = RuleMap_v2()

    def __init__(self):
        pass


    @classmethod
    def match(cls, *args, **kwargs):
        pass


    def step(self, *args, **kwargs):
        pass