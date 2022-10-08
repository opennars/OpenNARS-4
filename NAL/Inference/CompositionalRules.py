'''
Composition rules
'''
from pynars.Narsese import Copula, Statement, Compound, Connector, Task, Belief, Budget, Truth

from ..Functions import *
from pynars.Narsese import Judgement, Goal, Quest, Question

'''first-order With common subject'''
def intersection_extension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <M --> T1>. %f1;c1%
    j2: <M --> T2>. %f2;c2%
    |-
    j3: <M --> (&, T1, T2)>. %F_int%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.ExtensionalIntersection(stat1.predicate, stat2.predicate)
    statement = Statement(stat1.subject, Copula.Inheritance, compound)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def union_extension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <M --> T1>. %f1;c1%
    j2: <M --> T2>. %f2;c2%
    |-
    j3: <M --> (|, T1, T2)>. %F_uni%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.IntensionalIntersection(stat1.predicate, stat2.predicate)
    statement = Statement(stat1.subject, Copula.Inheritance, compound)

    if task.is_judgement:
        truth = Truth_union(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def difference_extension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <M --> T1>. %f1;c1%
    j2: <M --> T2>. %f2;c2%
    |-
    j3: <M --> (-, T1, T2)>. %F_dif%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.ExtensionalIntersection(stat1.predicate, stat2.predicate)
    statement = Statement(stat1.subject, Copula.Inheritance, compound)

    if task.is_judgement:
        truth = Truth_difference(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

# def difference_extension2(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
#     '''
#     j1: <M --> T1>. %f1;c1%
#     j2: <M --> T2>. %f2;c2%
#     |-
#     j3: <M --> (-, T2, T1)>. %F_dif'%
#     '''
#     difference_extension(task, belief, budget_tasklink, budget_termlink, inverse_premise=True)


'''First-order with common predicate'''
def intersection_intension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <T1 --> M>. %f1;c1%
    j2: <T2 --> M>. %f2;c2%
    |-
    j3: <(|, T1, T2) --> M>. %F_int%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.IntensionalIntersection(stat1.subject, stat2.subject)
    statement = Statement(compound, Copula.Inheritance, stat1.predicate)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def union_intension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <T1 --> M>. %f1;c1%
    j2: <T2 --> M>. %f2;c2%
    |-
    j3: <(&, T1, T2) --> M>. %F_uni%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.ExtensionalIntersection(stat1.subject, stat2.subject)
    statement = Statement(compound, Copula.Inheritance, stat1.predicate)

    if task.is_judgement:
        truth = Truth_union(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def difference_intension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <T1 --> M>. %f1;c1%
    j2: <T2 --> M>. %f2;c2%
    |-
    j3: <(~, T1, T2) --> M>. %F_dif%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.IntensionalDifference(stat1.subject, stat2.subject)
    statement = Statement(compound, Copula.Inheritance, stat1.predicate)

    if task.is_judgement:
        truth = Truth_difference(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

# def difference_intension2(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
#     '''
#     j1: <T1 --> M>. %f1;c1%
#     j2: <T2 --> M>. %f2;c2%
#     |-
#     j3: <(~, T2, T1) --> M>. %F_dif'%
#     '''
#     difference_intension(task, belief, budget_tasklink, budget_termlink, inverse_premise=True)
    


'''Higher-order with common subject'''
def conjunction_extension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <M ==> T1>. %f1;c1%
    j2: <M ==> T2>. %f2;c2%
    |-
    j3: <M ==> (&&, T1, T2)>. %F_int%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.Conjunction(stat1.predicate, stat2.predicate)
    statement = Statement(stat1.subject, Copula.Implication, compound)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def disjunction_extension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <M ==> T1>. %f1;c1%
    j2: <M ==> T2>. %f2;c2%
    |-
    j3: <M ==> (||, T1, T2)>. %F_uni%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.Disjunction(stat1.predicate, stat2.predicate)
    statement = Statement(stat1.subject, Copula.Implication, compound)

    if task.is_judgement:
        truth = Truth_union(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

'''Higher-order with common predicate'''
def disjunction_intension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <T1 ==> M>. %f1;c1%
    j2: <T2 ==> M>. %f2;c2%
    |-
    j3: <(||, T1, T2) ==> M>. %F_int%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.Disjunction(stat1.subject, stat2.subject)
    statement = Statement(compound, Copula.Implication, stat1.predicate)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def conjunction_intension(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <T1 ==> M>. %f1;c1%
    j2: <T2 ==> M>. %f2;c2%
    |-
    j3: <(&&, T1, T2) ==> M>. %F_uni%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = Compound.Conjunction(stat1.subject, stat2.subject)
    statement = Statement(compound, Copula.Implication, stat1.predicate)

    if task.is_judgement:
        truth = Truth_union(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

'''Higher-order composition'''
def conjunstion_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: T1. %f1;c1%
    j2: T2. %f2;c2%
    |-
    j3: (&&, T1, T2). %F_int%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    statement = Compound.Conjunction(stat1.subject, stat2.subject)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

def disjunction_composition(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: T1. %f1;c1%
    j2: T2. %f2;c2%
    |-
    j3: (||, T1, T2). %F_uni%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    statement = Compound.Disjunction(stat1, stat2)

    if task.is_judgement:
        truth = Truth_union(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)

