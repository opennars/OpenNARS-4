from Narsese import Task, Belief, Sentence, Judgement, Goal, Question, Quest
from Narsese import Statement, Term, Compound
from Narsese import Budget, Stamp
from Narsese import truth_analytic
from Config import Enable
from Narsese._py.Interval import Interval
from ..Functions import *
from copy import copy, deepcopy

# TODO: Implement temporal rules here.
#       Ref: OpenNARS 3.1.0 TemporalRules.java; OpenNARS 3.0.4 TemporalRules.java.

def deduction_sequence_eliminate(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    Testcase: nal7.18.nal
    judgements of both of task and belief should be events.


    premise1: <(&/, C, +100, S, ...) =/> P>.
    premise2: C. :|:
    |-
    conclusion: <S=/>P>. :!105:
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    compound: Compound = stat1.subject
    compound = compound - stat2


    interval: Interval = compound.terms[0]
    t_bias = 0
    if (compound.is_compound and interval.is_interval):
        t_bias = int(interval)
        if len(compound) == 1: compound = None
        else: compound = Compound(compound.connector, compound.terms[1:])
    elif compound.is_interval:
        t_bias = int(interval)
        compound = None

    if compound is not None: statement = Statement(compound, stat1.copula, stat1.predicate)
    else: statement = stat1.predicate

    stamp = Stamp_merge(stamp_task, stamp_belief, stat1.copula, t_bias=t_bias)

    if task.is_judgement:
        truth = Truth_deduction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        truth = Desire_induction(task.truth, belief.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    elif task.is_question:
        curiosity = None # TODO
        budget = Budget_backward_weak(belief.truth, budget_tasklink, budget_termlink)
        sentence_derived = Question(statement, stamp, curiosity)
    elif task.is_quest:
        curiosity = None # TODO
        budget = Budget_backward_weak(belief.truth, budget_tasklink, budget_termlink)
        sentence_derived = Quest(statement, stamp, curiosity)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def abduction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    Testcase: nal7.18.nal
    judgements of both of task and belief should be events.


    premise1: <(&/, C, S, ... +100) =/> P>.
    premise2: P. :|:
    |-
    conclusion: (&/, C, S, ...). :!-105:
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    compound: Compound = stat1.subject
    t_bias = 0
    if compound.is_compound and compound.connector is Connector.SequentialEvents:
        interval: Interval = compound.terms[-1]
        if  interval.is_interval:
            t_bias = -int(interval)
            compound_terms = compound.terms[:-1]
            if compound.is_multiple_only and len(compound_terms)==1:
                compound = compound_terms[0]
            else:
                compound = Compound(compound.connector, *compound_terms)

    statement = compound

    stamp = Stamp_merge(stamp_task, stamp_belief, stat1.copula, reverse_order=True, t_bias=t_bias)

    if task.is_judgement:
        truth = Truth_abduction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        truth = Desire_deduction(task.truth, belief.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    elif task.is_question:
        curiosity = None # TODO
        budget = Budget_backward_weak(belief.truth, budget_tasklink, budget_termlink)
        sentence_derived = Question(statement, stamp, curiosity)
    elif task.is_quest:
        curiosity = None # TODO
        budget = Budget_backward_weak(belief.truth, budget_tasklink, budget_termlink)
        sentence_derived = Quest(statement, stamp, curiosity)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def sequence(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&/, A, B, C)!
    A.
    |- 
    (&/, B, C)!

    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    compound: Compound = stat1
    if compound.connector is Connector.SequentialEvents:
        compound_terms = compound.terms[1:]
        if compound.is_multiple_only and len(compound_terms)==1:
            compound = compound_terms[0]
        else:
            compound = Compound(compound.connector, *compound_terms)

    statement = compound

    stamp = Stamp_merge(stamp_task, stamp_belief)

    if task.is_judgement:
        truth = Truth_deduction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        truth = Desire_deduction(task.truth, belief.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def sequence_predictive_implication(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&/, A, B, C) =/> D!
    A.
    |- 
    (&/, B, C) =/> D!

    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    compound: Compound = stat1.subject
    if compound.connector is Connector.SequentialEvents:
        compound_terms = compound.terms[1:]
        if compound.is_multiple_only and len(compound_terms)==1:
            compound = compound_terms[0]
        else:
            compound = Compound(compound.connector, *compound_terms)

    statement = Statement(compound, stat1.copula, stat1.predicate)

    stamp = Stamp_merge(stamp_task, stamp_belief)

    if task.is_judgement:
        truth = Truth_deduction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        truth = Desire_deduction(task.truth, belief.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


'''Immediate Rules'''

def immediate_goal_deriviation(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&/, A, B, C)!
    '''
    # belief is None.
    premise = task.sentence
    stat: Statement = premise.term

    statement = stat[0]
    stamp = copy(premise.stamp)

    if task.is_goal:
        truth = Truth_deduction(premise.truth, truth_analytic)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


'''Temporal Induction Rules'''
def induction_implication(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   B. :|:
    conclusion: <A=/>B>. :|:


    Reference:
    [1] OpenNARS 3.0.4 TemporalRules.java line 147~263 temporalInduction(...)

    Testcase: nal7.6.nal
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    time_diff = premise2.stamp.t_occurrence - premise1.stamp.t_occurrence
    interval = Interval(abs(time_diff))
    if abs(time_diff) < Config.temporal_duration:
        # concurrent
        statement = Statement(stat1, Copula.ConcurrentImplication, stat2)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        statement = Statement(Compound.SequentialEvents(stat1, interval), Copula.PredictiveImplication, stat2)
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        statement = Statement(stat1, Copula.RetrospectiveImplication, Compound.SequentialEvents(stat2, interval))
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def induction_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   <B=/>C>. :|:
    conclusion: <(&/, A, +5, B)=/>C>. :|:


    Reference:
    [1] OpenNARS 3.0.4 TemporalRules.java line 147~263 temporalInduction(...)

    Testcase: nal7.7.nal
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    time_diff = premise2.stamp.t_occurrence - premise1.stamp.t_occurrence
    interval = Interval(abs(time_diff))
    if abs(time_diff) < Config.temporal_duration:
        # concurrent
        statement = Statement(Compound.ParallelEvents(stat1, stat2.subject), Copula.ConcurrentImplication, stat2.predicate)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        statement = Statement(Compound.SequentialEvents(stat1, interval, stat2.subject), Copula.PredictiveImplication, stat2.predicate)
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        statement = Statement(stat2.subject, Copula.RetrospectiveImplication, Compound.SequentialEvents(stat2.predicate, interval, stat1))
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)
