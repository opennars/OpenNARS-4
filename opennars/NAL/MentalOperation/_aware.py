from copy import copy
from typing import List
from opennars.Config import Config
from opennars.Narsese._py import SELF
from opennars.Narsese._py.Budget import Budget
from opennars.Narsese._py.Compound import Compound
from opennars.Narsese._py.Connector import Connector
from opennars.Narsese._py.Operation import *
from opennars.Narsese._py.Sentence import Goal, Judgement, Quest, Question, Sentence, Stamp
from opennars.Narsese._py.Statement import Statement
from opennars.Narsese._py.Task import Belief, Desire, Task
from opennars.Narsese._py.Truth import Truth
from ._register import registered_operators
from opennars.Narsese import Term
from ..Functions.Tools import truth_from_term, truth_to_quality, truth_to_term
from opennars.Narsese import Base
from opennars import Global


def _aware(statement: Statement, stamp: Stamp, budget_task: Budget=None):
    ''''''
    stamp = copy(stamp)
    stamp.t_occurrence = Global.time
    truth_aware = Truth(1.0, Config.c_judgement, Config.k)
    if budget_task is None:
        budget = Budget(Config.p_judgement*Config.rate_discount_p_internal_exp, Config.d_judgement*Config.rate_discount_d_internal_exp, truth_to_quality(truth_aware))
    else:
        budget = Budget(budget_task.priority*Config.rate_discount_p_internal_exp, budget_task.durability*Config.rate_discount_d_internal_exp, truth_to_quality(truth_aware))

    sentence = Judgement(statement, stamp, truth_aware)
    return Task(sentence, budget)


def believe(judgement: Judgement, truth: Truth, budget_task: Budget=None):
    ''''''
    stat_aware = Statement.Inheritance(Compound(Connector.Product, SELF, judgement.term, truth_to_term(truth)), Believe)
    return _aware(stat_aware, judgement.stamp, budget_task)


def want(goal: Goal, truth: Truth, budget_task: Budget=None):
    ''''''
    stat_aware = Statement.Inheritance(Compound(Connector.Product, SELF, goal.term, truth_to_term(truth)), Believe)
    return _aware(stat_aware, goal.stamp, budget_task)


def evaluate(quest: Quest, budget_task: Budget=None):
    ''''''
    stat_aware = Statement.Inheritance(Compound(Connector.Product, SELF, quest.term), Evaluate)
    return _aware(stat_aware, quest.stamp, budget_task)



def wonder(question: Question, budget_task: Budget=None):
    ''''''
    stat_aware = Statement.Inheritance(Compound(Connector.Product, SELF, question.term), Wonder)
    return _aware(stat_aware, question.stamp, budget_task)

