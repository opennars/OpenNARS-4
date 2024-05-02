from operator import imod
import os 
from pathlib import Path
from inspect import getmembers, isfunction
import importlib
import re
from typing import Any, List, Tuple, Union
from typing_extensions import Protocol
from collections import OrderedDict

from pynars.Config import Enable
from pynars.NARS.RuleMap.Interface import Interface_CompositionalRules, Interface_SyllogisticRules, Interface_DecompositionalRules, Interface_TransformRules, Interface_ConditionalRules, Interface_TemporalRules, Interface_VariableRules
from pynars.Narsese import Copula, Task
from pynars.Narsese._py.Connector import Connector
from pynars.Narsese._py.Sentence import Goal, Judgement, Quest, Question
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Term import Term
from pynars.Narsese import Belief, Term, Truth, Compound, Budget
from ..DataStructures import LinkType, TaskLink, TermLink
from pynars.NAL.Inference import *
from sparse_lut import SparseLUT
from pynars.utils.tools import get_size

from pynars.utils.Print import print_out, PrintType

import time
from datetime import datetime
import pickle
import sty
# from ._extract_feature import extract_feature, _compound_has_common, _compound_at
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
    
    @staticmethod
    def get(first, second):
        return None if first is None and second is None else int(CommonId(first, second))


def _compound_has_common(term1: Union[Term, Compound, Statement], term2: Union[Term, Compound, Statement]):
    if term1.is_compound:
        return (term2 in term1.terms) or term1.has_common(term2)
    elif term2.is_compound:
        return (term1 in term2.terms) or term1.has_common(term2)
    else: return False

def _compound_at(term1: Union[Term, Compound, Statement], term2: Compound, compound_has_common: bool=None):
    if term2.is_compound:
        if not term1.is_compound: 
            if term2.connector is Connector.SequentialEvents: 
                return term2.terms[0] == term1
            else: 
                return term2.contains(term1)
        else: 
            empty = True if len(term2.terms - term1.terms) == 0 else False
            if term2.connector is Connector.SequentialEvents: 
                return (not empty) and term2.terms[:len(term1.terms)] == term1.terms
            else: 
                return (not empty) and (compound_has_common if compound_has_common is not None else _compound_has_common(term1, term2))
    else: return False
    
def _at(compound: Union[Compound, Statement], term: Term):
    '''
    To judge whether the `component` is in the `compound`.

    e.g. A@(&&,A,B), then return (True, 0); 
        B@(&&,A,B), then return (True, 1); 
        C@(&&,A,B), then return (False, None)
    '''
    if compound.is_atom:
        return (False, None)
    else:
        if compound.is_compound:
            terms = compound
        elif compound.is_statement:
            terms = (compound.subject, compound.predicate)
        else: raise "Invalid case."

        for i, component in enumerate(terms):
            if component == term:
                return (True, i)
        else:
            return (False, None)
    

def _common(premise1: Statement, premise2: Statement):
    '''
    To judge whether the `premise1` and the `premise2` have common term.

    e.g. <S-->M>, <M-->P>, then return (True, 1, 0);
        <M-->P>, <S-->M>, then return (True, 0, 1);
        <M-->P>, <M-->S>, then return (True, 0, 0);
        <P-->M>, <S-->M>, then return (True, 1, 1);
        <A==>B>, A, then return (True, 0, 0)
        <A==>B>, B, then return (True, 1, 0)

        <A==><B-->C>>, <B-->C>
        <A==>(&, B, C)>, (&, B, C)
        <A==>(&, B, C, D)>, (&, B, C)
        <A-->(|, B, C), <A-->C> |- <A-->B>
        <(&, A, B)-->(|, C, D), <(&, A, B)-->D> |- <(&, A, B)-->C>

    Return:
        has_common_id (bool), common_id_task (int), common_id_belief (int), match_reverse (bool)
    '''
    if premise1.is_statement and premise2.is_statement:
        if premise1.subject == premise2.predicate and premise1.predicate == premise2.subject:
            return True, None, None, True
        if premise1.subject == premise2.subject:
            return True, 0, 0, False
        elif premise1.subject == premise2.predicate:
            return True, 0, 1, False
        elif premise1.predicate == premise2.subject:
            return True, 1, 0, False
        elif premise1.predicate == premise2.predicate:
            return True, 1, 1, False
        else:
            return False, None, None, False
    elif premise1.is_statement and premise2.is_atom:
        if premise1.subject == premise2:
            return True, 0, 0, False
        elif premise1.predicate == premise2:
            return True, 1, 0, False
        else:
            return False, None, None, False
    elif premise2.is_statement and premise1.is_atom:
        if premise2.subject == premise1:
            return True, 0, 0, False
        elif premise2.predicate == premise1:
            return True, 0, 1, False
        else:
            return False, None, None, False
    else:
        return False, None, None, False




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