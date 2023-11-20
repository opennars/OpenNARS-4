from pynars.Narsese._py.Sentence import Sentence
from ..Functions.TruthValueFunctions import *
from pynars.Narsese import Copula, Statement, Compound, Connector, Term, Task, Budget, Stamp
from ..Functions.BudgetFunctions import *

from ..Functions import F_negation, F_conversion, F_contraposition, \
    fc_to_w_minus, fc_to_w_plus, w_to_f, w_to_c
from pynars.Narsese import Judgement, Truth, Goal, Quest, Question

# TODO: <S --> P> |- <S <-> P> OpenNARS 3.0.4 LocalRules.java line 424~441

def negation(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    S |- (--, S). %F_neg%
    '''
    stamp_task: Stamp = task.stamp
    premise: Sentence = task.sentence

    term_task = task.term
    term_neg = Compound.Negation(term_task)

    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_negation(premise.truth)
        sentence_derived = Judgement(term_neg, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_goal:
        truth = Truth_negation(premise.truth)
        sentence_derived = Goal(term_neg, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_question:
        sentence_derived = Question(term_neg, stamp)
        budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
    elif premise.is_quest:
        sentence_derived = Quest(term_neg, stamp)
        budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
    else: raise 'Invalid case.'

    return Task(sentence_derived, budget)


def conversion(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <S --> P> |- <P --> S>
    <S ==> P> |- <P ==> S>
    '''
    stamp_task: Stamp = task.stamp
    premise: Sentence = task.sentence
    stat: Statement = premise.term

    subject = stat.predicate
    predicate = stat.subject
    statement = Statement(subject, stat.copula.reverse, predicate)

    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_conversion(premise.truth)
        sentence_derived = Judgement(statement, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    # elif premise.is_goal:
    #     truth = Truth_negation(premise.truth)
    #     sentence_derived = Goal(term_concept, stamp, truth)
    #     budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    # elif premise.is_question:
    #     sentence_derived = Question(term_concept, stamp)
    #     budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
    # elif premise.is_quest:
    #     sentence_derived = Quest(term_concept, stamp)
    #     budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
    else: raise 'Invalid case.'

    return Task(sentence_derived, budget)


def contraposition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S ==> P> |- <(--, P) ==> (--, S)>>. %F_cnt%
    '''
    stamp_task: Stamp = task.stamp
    premise: Sentence = task.sentence
    stat: Statement = premise.term

    subject = Compound.Negation(stat.predicate)
    predicate = Compound.Negation(stat.subject)
    statement = Statement(subject, stat.copula, predicate)

    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_contraposition(premise.truth)
        sentence_derived = Judgement(statement, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_goal:
        truth = Truth_negation(premise.truth)
        sentence_derived = Goal(term_concept, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_question or premise.is_quest:
        sentence_derived = Question(term_concept, stamp)
        budget = Budget_backward_weak_compound(statement, budget_tasklink, budget_termlink)
    else: raise 'Invalid case.'

    return Task(sentence_derived, budget)
