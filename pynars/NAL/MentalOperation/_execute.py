from typing import List
from pynars.Config import Config
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Operation import *
from pynars.Narsese._py.Sentence import Goal, Judgement, Quest, Question, Sentence, Stamp
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Task import Belief, Desire, Task
from pynars.Narsese._py.Truth import Truth
from ._register import registered_operations
from pynars.Narsese import Term
from ..Functions.Tools import truth_from_term, truth_to_quality
from pynars.Narsese import Base
from pynars import Global

def execute(task: Task):
    ''''''
    stat: Statement = task.term
    if stat.is_executable:
        operation: Operation = stat.predicate
        args = stat.terms
        return registered_operations[operation](task, *args)
    else:
        return None

def anticipate(task: Task, *args: Term):
    ''''''

def believe(statement: Term, term_truth: Term):
    ''''''
    truth = truth_from_term(term_truth)
    budget = Budget(Config.p_judgement, Config.d_judgement, truth_to_quality(truth))
    stamp = Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_external=False)
    sentence = Judgement(statement, stamp=stamp, truth=truth)
    return Task(sentence, budget)


def doubt(beliefs: List[Belief]):
    ''''''
    for belief in beliefs:
        # discount the confidence of the beleif
        belief.truth.c = belief.truth.c * Config.rate_discount_c
    return None


def evaluate(statement: Term):
    ''''''
    budget = Budget(Config.p_quest, Config.d_quest, 1.0)
    stamp = Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_eternal=False)
    sentence = Quest(statement, stamp=stamp)
    return Task(sentence, budget)


def hesitate(desires: List[Desire]):
    ''''''
    for desire in desires:
        # discount the confidence of the desire
        desire.truth.c = desire.truth.c * Config.rate_discount_c
    return None


def want(statement: Term):
    ''''''
    truth = Truth(1.0, Config.c_judgement, Config.k)
    budget = Budget(Config.p_judgement, Config.d_judgement, truth_to_quality(truth))
    stamp = Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_eternal=False)
    sentence = Goal(statement, stamp, truth)
    return Task(sentence, budget)


def wonder(statement: Term):
    ''''''
    budget = Budget(Config.p_question, Config.d_question, 1)
    stamp = Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_eternal=False)
    sentence = Question(statement, stamp=stamp)
    return Task(sentence, budget)

