from operator import imod
import os 
from pathlib import Path
from inspect import getmembers, isfunction
import importlib
import re
from typing import Any, List, Tuple, Union
from typing_extensions import Protocol
from collections import OrderedDict

from numpy import product

from pynars.Config import Enable
from pynars.NARS.RuleMap.Interface import Interface_CompositionalRules, Interface_SyllogisticRules, Interface_DecompositionalRules, Interface_TransformRules, Interface_ConditionalRules, Interface_TemporalRules
from pynars.Narsese import Copula, Task
from pynars.Narsese._py.Connector import Connector
from pynars.Narsese._py.Sentence import Goal, Judgement, Quest, Question
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Term import Term
from pynars.Narsese import Belief, Term, Truth, Compound, Budget
# from .RuleMap_v1 import RuleMap as RuleMap_v1, RuleCallable
from ...DataStructures import LinkType, TaskLink, TermLink
from pynars.NAL.Inference import *
from pynars.utils.SparseLUT import SparseLUT
from pynars.utils.tools import get_size

from pynars.utils.Print import out_print, PrintType

import time
from datetime import datetime
import pickle
import sty
from .._extract_feature import extract_feature, _compound_has_common, _compound_at
from pynars import Global

class RuleCallable(Protocol):
    def __call__(self, 
        task: Task, 
        belief: Belief, 
        budget_tasklink: Budget=None, 
        budget_termlink: Budget=None
    ) -> Tuple[Task, Tuple[Budget, float, float]]: ...

class RuleMapCallable(Protocol):
    def __call__(self, 
        task: Task, 
        term_belief: Union[Statement, Term],
        truth_belief: Union[Truth, None], 
        task_link: TaskLink, 
        term_link: TermLink
    ) -> List[RuleCallable]: ...


def task_type_id(task: Task):
    if task.is_judgement: return 0
    elif task.is_goal: return 1
    elif task.is_question: return 2
    elif task.is_quest: return 3
    else: raise "Invalid case."

_class_convert = {
    Judgement: 0,
    Goal: 1,
    Question: 2,
    Quest: 3
}
def class_sentence_to_list(*types):
    if isinstance(types, list): types = [types]
    return [_class_convert[t] for t in types]
    
    
class CommonId:
    def __init__(self, first, second=None) -> None:
        self.first = first
        self.second = second

    def __int__(self):
        return self.first*2 + self.second if self.second is not None else self.first


def add_rule(sparse_lut: SparseLUT, structure: OrderedDict, rules: List[RuleCallable],**kwargs):
        ''''''
        indices = [kwargs.get(key, None) for key in structure.keys()]

        # convert the indices into a normalized form.
        indices_norm = []
        values = iter(structure.values())
        for index in indices:
            _type, _cnt_type = next(values)
            # if index is Ellipsis or index is None: index = None
            if index is Any: pass
            elif index is None: pass
            elif isinstance(index, tuple): 
                assert 0 < len(index) <= 3, "It shouldn't be bigger than 3, and shouldn't be 0."
                _index = index
                index = []
                for i, idx in enumerate(_index):
                    if i < 2: assert isinstance(idx, _type), "It should be the type identified in `self.structure_map`"
                    idx = int(idx)
                    if i < 2: assert idx < _cnt_type, "It shouldn't be bigger than the maximum index of the type."
                    index.append(index)
                index = slice(*index)
            elif isinstance(index, slice): pass
            elif isinstance(index, list): 
                _index = index
                index = []
                for idx in _index:
                    assert idx is None or isinstance(idx, _type), "It should be the type identified in `self.structure_map`"
                    idx = int(idx) if idx is not None else idx
                    assert (idx if idx is not None else 0) < _cnt_type , "It shouldn't be bigger than the maximum index of the type."
                    index.append(idx)
            else: 
                assert isinstance(index, _type), f"The `{index}` should be the type identified in `self.structure_map`"
                index = int(index)
                assert index < _cnt_type, "It shouldn't be bigger than the maximum index of the type."
            indices_norm.append(index)
        indices = tuple(indices_norm)
        
        # add the rule to the map
        if not(isinstance(rules, tuple) or isinstance(rules, list)):
            rules = (rules,)
        for rule in rules:            
            sparse_lut.add(list(indices), rule)
        return indices