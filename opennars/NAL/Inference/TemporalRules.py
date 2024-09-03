from typing import Dict, Tuple
from opennars.Narsese import Task, Belief, Sentence, Judgement, Goal, Question, Quest
from opennars.Narsese import Statement, Term, Compound
from opennars.Narsese import Budget, Stamp
from opennars.Narsese import truth_analytic
from opennars.Config import Enable
from opennars.Narsese._py.Interval import Interval
from opennars.Narsese._py.Terms import Terms
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

    if compound is not None: 
        statement = Statement(compound, stat1.copula, stat1.predicate)
        stamp = Stamp_merge(stamp_task, stamp_belief, None, t_bias=t_bias)
    else: 
        statement = stat1.predicate
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


def deduction_sequence_replace(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''

    premise1: <(&/, C, ..., +100) =/> P>.
    premise2: (&/, S, ..., +100)=/>C. :|:
    |-
    conclusion: <(&/, S, ..., +100, ..., +100)=/>P>.
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    compound1: Compound = stat1.subject
    compound1 = compound1 - stat2.predicate
    interval1: Interval = compound1.terms[0]
    compound2: Compound = stat2.subject
    interval2: Interval = compound2.terms[-1]
    if interval1.is_interval and interval2.is_interval:
        interval = interval1 + interval2
        compound = Compound(compound2.connector, *compound2.terms[:-1], interval)
    else:
        compound = Compound(compound2.connector, *compound2.terms, *compound1.terms)

    statement = Statement(compound, stat1.copula, stat1.predicate)

    stamp = Stamp_merge(stamp_task, stamp_belief)
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


def analogy(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
        premise1: <M =/> P> (inverse: <P =/> M>)
        premise2: <S </> M> (inverse: <S </> M>)
        |-
        conclusion: <S =/> P> (inverse: <P =/> S>)

        premise1: <M =/> P> (inverse: <P =/> M>)
        premise2: <M </> S> (inverse: <M </> S>)
        |-
        conclusion: <S =/> P> (inverse: <P =/> S>)
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    truth_belief: Truth = belief.truth
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stat1_subject = stat1.subject
    stat1_predicate = stat1.predicate

    copula_dict: Dict[Tuple[Copula, Copula], Copula]= analogy.copula_dict
    copula1 = stat1.copula
    copula2 = stat2.copula    
    if copula1 is Copula.RetrospectiveImplication:
        copula1 = copula1.PredictiveImplication
        inverse_copula = not inverse_copula
        stat1_subject, stat1_predicate = stat1_predicate, stat1_subject
        
    copula = copula_dict[(copula1, copula2)]

    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    # TODO
    if not inverse_copula:
        if stat2.predicate == stat1_subject:
            statement = Statement(stat2.subject, copula, stat1_predicate)
        elif stat2.subject == stat1_subject:
            if copula1 is Copula.ConcurrentImplication and copula2 is Copula.PredictiveEquivalence:
                # {A=|>B>. <A</>C>.} |- <A=\>C>.
                copula = copula.reverse
            statement = Statement(stat2.predicate, copula, stat1_predicate)
        else: raise "Invalid case."
    else:
        if stat2.predicate == stat1_predicate:
            if copula1 is Copula.ConcurrentImplication and copula2 is Copula.PredictiveEquivalence:
                # {A=|>B>. <C</>B>.} |- <A=\>C>.
                copula = copula.reverse
            statement = Statement(stat1_subject, copula, stat2.subject)
        elif stat2.subject == stat1_predicate:
            statement = Statement(stat1_subject, copula, stat2.predicate)
        else: raise "Invalid case."
            

    if task.is_judgement:
        truth = Truth_analogy(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        Desire_function = Desire_weak if task.term.is_commutative else Desire_strong
        truth = Desire_function(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    elif task.is_question:
        curiosity = None # TODO
        budget = Budget_backward_weak(truth_belief, budget_tasklink, budget_termlink)
        sentence_derived = Question(statement, stamp, curiosity)
    elif task.is_quest:
        curiosity = None # TODO
        budget = Budget_backward(truth_belief, budget_tasklink, budget_termlink)
        sentence_derived = Quest(statement, stamp, curiosity)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

analogy.copula_dict = {
    (Copula.PredictiveImplication, Copula.PredictiveEquivalence): Copula.PredictiveImplication,
    (Copula.ConcurrentImplication, Copula.PredictiveEquivalence): Copula.PredictiveImplication,
    (Copula.PredictiveImplication, Copula.ConcurrentEquivalence): Copula.PredictiveImplication,
    (Copula.ConcurrentImplication, Copula.ConcurrentEquivalence): Copula.ConcurrentImplication,
}


def sequence(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&/, A, B, C).
    A.
    |- 
    (&/, B, C).

    (&/, A, B, C).
    C!
    |- 
    (&/, A, B)!

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
        compound_terms = compound.terms[1:] if not inverse_copula else compound.terms[:-1]
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


def parallel(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&|, A, B, C)!
    A.
    |- 
    (&|, B, C)!

    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    statement = stat1 - stat2

    stamp = Stamp_merge(stamp_task, stamp_belief)

    if task.is_goal:
        truth = Desire_deduction(task.truth, belief.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)



def sequence_immediate(task: Task, term_belief: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&/, A, B, C)!
    A
    |- 
    A!
    '''

    stamp: Stamp = copy(task.stamp)

    if task.is_goal:
        truth = Desire_deduction(task.truth, truth_analytic)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(term_belief, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def parallel_immediate(task: Task, term_belief: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    (&|, A, B, C)!
    A
    |- 
    A!
    '''

    stamp: Stamp = copy(task.stamp)

    if task.is_goal:
        truth = Desire_deduction(task.truth, truth_analytic)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Goal(term_belief, stamp, truth)
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
'''
{A. :\:; B. :|:} |- <A=/>B>. :|:
{A. :\:; B. :|:} |- (&/, A, +5, B). :|:
{A. :\:; <B=/>C>. :|:} |- <(&/, A, +5, B)=/>C>. :|:
'''

# TODO: each rule-function should be renamed.

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


def induction_equivalence(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   B. :|:
    conclusion: <A</>B>. :|:


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
        statement = Statement(stat1, Copula.ConcurrentEquivalence, stat2)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        statement = Statement(Compound.SequentialEvents(stat1, interval), Copula.PredictiveEquivalence, stat2)
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        statement = Statement(Compound.SequentialEvents(stat2, interval), Copula.PredictiveEquivalence, stat1)
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
    premise2:   B. :|:
    conclusion: (&/, A, +5, B). :|:


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
        # parallel
        statement = Compound.ParallelEvents(stat1, stat2)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # sequential
        statement = Compound.SequentialEvents(stat1, interval, stat2)
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # sequential
        statement = Compound.SequentialEvents(stat2, interval, stat1)
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)



def induction_predictive_implication_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
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

    # stat2_subject, stat2_predicate, stat2_copula = (stat2.subject, stat2.predicate, stat2.copula) if not inverse_copula else (stat2.predicate, stat2.subject, stat2.copula.reverse)

    time_diff = premise2.stamp.t_occurrence - premise1.stamp.t_occurrence
    interval = Interval(abs(time_diff))
    if abs(time_diff) < Config.temporal_duration:
        # concurrent
        # TODO: I doubt this rule below. So I modified it into a new one, but it should be further justified.
        # # subject = Compound.ParallelEvents(stat1, stat2.subject)
        # # copula = Copula.ConcurrentImplication  # stat2.copula
        # # predicate = stat2.predicate

        subject = stat2.subject
        copula = stat2.copula
        predicate =  Compound.ParallelEvents(stat1, stat2.predicate)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        subject = Compound.SequentialEvents(stat1, interval, stat2.subject)
        copula = stat2.copula
        predicate = stat2.predicate
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        subject = stat2.subject
        copula = stat2.copula
        predicate = Compound.SequentialEvents(stat2.predicate, interval, stat1)
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)
    if inverse_copula:
        subject, copula, predicate = predicate, copula.reverse, subject
    statement = Statement(subject, copula, predicate)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def induction_retrospective_implication_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   <B=\>C>. :|:
    conclusion: <(&/, A, +5, C)=/>B>. :|:


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
        # TODO: I doubt this rule below. So I modified it into a new one, but it should be further justified.
        # # subject = Compound.ParallelEvents(stat1, stat2.subject)
        # # copula = Copula.ConcurrentImplication  # stat2.copula
        # # predicate = stat2.predicate

        subject = stat2.predicate
        copula = stat2.copula.reverse
        predicate =  Compound.ParallelEvents(stat1, stat2.subject)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        subject = Compound.SequentialEvents(stat1, interval, stat2.predicate)
        copula = stat2.copula.reverse
        predicate = stat2.subject
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        subject = stat2.predicate
        copula = stat2.copula.reverse
        predicate = Compound.SequentialEvents(stat2.subject, interval, stat1)
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)
    if inverse_copula:
        subject, copula, predicate = predicate, copula.reverse, subject
    statement = Statement(subject, copula, predicate)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def induction_predictive_equivalance_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   <B=/>C>. :|:
    conclusion: <(&/, A, +5, B)</>C>. :|:


    Reference:
    [1] OpenNARS 3.0.4 TemporalRules.java line 147~263 temporalInduction(...)

    Testcase: nal7.7.nal
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term

    # stat2_subject, stat2_predicate, stat2_copula = (stat2.subject, stat2.predicate, stat2.copula) if not inverse_copula else (stat2.predicate, stat2.subject, stat2.copula.reverse)

    time_diff = premise2.stamp.t_occurrence - premise1.stamp.t_occurrence
    interval = Interval(abs(time_diff))
    if abs(time_diff) < Config.temporal_duration:
        # concurrent
        # TODO: I doubt this rule below. So I modified it into a new one, but it should be further justified.
        # # subject = Compound.ParallelEvents(stat1, stat2.subject)
        # # copula = Copula.ConcurrentImplication  # stat2.copula
        # # predicate = stat2.predicate

        subject = stat2.subject
        copula = Copula.PredictiveEquivalence
        predicate =  Compound.ParallelEvents(stat1, stat2.predicate)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        subject = Compound.SequentialEvents(stat1, interval, stat2.subject)
        copula = Copula.PredictiveEquivalence
        predicate = stat2.predicate
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        subject = stat2.subject
        copula = Copula.PredictiveEquivalence
        predicate = Compound.SequentialEvents(stat2.predicate, interval, stat1)
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)
    if inverse_copula:
        subject, copula, predicate = predicate, copula.reverse, subject
    statement = Statement(subject, copula, predicate)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def induction_retrospective_equivalance_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    judgements of both of task and belief should be events.

    premise1:   A. :\:
    premise2:   <B=\>C>. :|:
    conclusion: <(&/, A, +5, C)</>B>. :|:


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
        # TODO: I doubt this rule below. So I modified it into a new one, but it should be further justified.
        # # subject = Compound.ParallelEvents(stat1, stat2.subject)
        # # copula = Copula.ConcurrentImplication  # stat2.copula
        # # predicate = stat2.predicate

        subject = stat2.predicate
        copula = Copula.PredictiveEquivalence
        predicate =  Compound.ParallelEvents(stat1, stat2.subject)
        stamp = Stamp_merge(stamp_task, stamp_belief)
    elif time_diff > 0:
        # predictive
        subject = Compound.SequentialEvents(stat1, interval, stat2.predicate)
        copula = Copula.PredictiveEquivalence
        predicate = stat2.subject
        stamp = Stamp_merge(premise2.stamp, premise1.stamp)
    else: # time_diff < 0
        # retrospective
        subject = stat2.predicate
        copula = Copula.PredictiveEquivalence
        predicate = Compound.SequentialEvents(stat2.subject, interval, stat1)
        stamp = Stamp_merge(premise1.stamp, premise2.stamp)
    if inverse_copula:
        subject, copula, predicate = predicate, copula.reverse, subject
    statement = Statement(subject, copula, predicate)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink if budget_tasklink is not None else task.budget, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)