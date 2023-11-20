import math
from pynars.NAL.Functions.DesireValueFunctions import Desire_strong, Desire_weak, Desire_deduction, Desire_induction
from pynars.NAL.Functions.TruthValueFunctions import *
from pynars.NAL.Functions.BudgetFunctions import Budget_backward_weak, Budget_forward, Budget_inference, Budget_backward, Budget_forward_compound
from pynars.Narsese import Term, Copula, Statement, Truth, Task, Belief, Budget, Stamp, VarPrefix, Compound
from pynars.Narsese import Punctuation, Sentence, Judgement, Goal, Question, Quest
from ..Functions import F_deduction, fc_to_w_minus, fc_to_w_plus
from copy import deepcopy
from ..Functions.StampFunctions import *
from pynars.NAL.MetaLevelInference.VariableSubstitution.Introduction import Introduction, get_introduction__const_var
from pynars.NAL.MetaLevelInference.VariableSubstitution.Elimination import Elimination, get_elimination__var_const
'''
Introducton Rules:

induction       {<M --> P>, <M --> S>} |- <<$x-->S>==><$x-->P>>
abduction       {<P --> M>, <S --> M>} |- <<S --> $x> ==> <P --> $x>>

comparison      {<M --> P>, <M --> S>} |- <<$x-->S><=><$x-->P>>
                {<P --> M>, <S --> M>} |- <<S --> $x> <=> <P --> $x>>
intersection    {<M --> P>, <M --> S>} |- (&&, <#x-->S>, <#x-->P>)
                {<P --> M>, <S --> M>} |- (&&, <S --> #x>, <P --> #x>)


{<A ==> <M --> B>>, <M --> C>} |- <(&&, A, <$x --> C>) ==> <$x-->B>>
{<A ==> <M --> B>>, <M --> C>} |- (&&, <#x --> C>, <A ==> <#x --> B>>)

{(&&, A, <M --> B>), <M --> C>} |- <<$x --> C> ==> (&&, A, <$x --> B>)>
{(&&, A, <M --> B>), <M --> C>} |- (&&, <#x --> C>, A, <#x --> B>)

{<<M --> B> ==> A>, <M --> C>} |- <(&&, <#x --> B>, <#x --> C>) ==> A>
{<<M --> B> ==> A>, <M --> C>} |- <(&&, <$x --> B>, <$x --> C>) ==> A>

Elimination Rules:
{(&&, <#x-->A>, <#x-->B>), <M-->A>} |- <M-->B>
{(&&, <A-->#x>, <B-->#x>), <A-->M>} |- <B-->M>

'''

def independent_variable_introduction__induction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <M --> P>
    premise2: <M --> S>
    |-
    conclusion: <<$x-->S>==><$x-->P>>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    term_common = stat1.subject

    intro = Introduction(stat1, stat2, term_common)
    stat1, stat2 = intro.apply(type_var=VarPrefix.Independent)

    statement = Statement.Implication(stat2, stat1)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def independent_variable_introduction__implication__induction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <C ==> <M --> P>>
    premise2: <M --> S>
    |-
    conclusion: <(&&, C, <$x-->S>) ==> <$x-->P>>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stat1_predicate: Statement = stat1.predicate
    term_common = stat1_predicate.subject

    intro = Introduction(stat1_predicate, stat2, term_common)
    stat1_predicate, stat2 = intro.apply(type_var=VarPrefix.Independent)
    cpnd = Compound.Conjunction(stat1.subject, stat2)

    statement = Statement.Implication(cpnd, stat1_predicate)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def independent_variable_introduction__conjunction__induction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: (&&, C, <M-->A>)
    premise2: <M-->B>.
    |-
    conclusion: <<$x-->B> ==> (&&, C, <#x-->A>)>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    cpnd1: Compound = premise1.term
    stat2: Statement = premise2.term
    for cpnt in cpnd1:
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            stat1: Statement = cpnt
            if stat1.subject == stat2.subject and not inverse_copula:
                term_common = stat1.subject
                break
            elif stat1.predicate == stat2.predicate and inverse_copula:
                term_common = stat1.predicate
                break
    else:
        raise Exception("The common term cannot be found.")

    intro = Introduction(cpnd1, stat2, term_common)
    cpnd1, stat2 = intro.apply(type_var=VarPrefix.Independent)

    statement = Statement.Implication(stat2, cpnd1) if not inverse_premise else Statement.Implication(cpnd1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def independent_variable_introduction__abduction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <P --> M>
    premise2: <S --> M>
    |-
    conclusion: <<S-->$x>==><P-->$x>>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    term_common = stat1.predicate

    intro = Introduction(stat1, stat2, term_common)
    stat1, stat2 = intro.apply(type_var=VarPrefix.Independent)

    statement = Statement.Implication(stat1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_abduction(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)



def independent_variable_introduction__comparison(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <M --> P>
    premise2: <M --> S>
    |-
    conclusion: <<$x-->S><=><$x-->P>>

    premise1: <P --> M>
    premise2: <S --> M>
    |-
    conclusion: <<S-->$x><=><P-->$x>>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    term_common = stat1.subject if not inverse_copula else stat1.predicate

    intro = Introduction(stat1, stat2, term_common)
    stat1, stat2 = intro.apply(type_var=VarPrefix.Independent)

    statement = Statement.Equivalence(stat1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_comparison(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def dependent_variable_introduction__intersection(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <M --> P>
    premise2: <M --> S>
    |-
    conclusion: (&&, <#x-->S>, <#x-->P>)

    premise1: <P --> M>
    premise2: <S --> M>
    |-
    conclusion: (&&, <S-->#x>, <P-->#x>)
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    term_common = stat1.subject if not inverse_copula else stat1.predicate

    intro = Introduction(stat1, stat2, term_common)
    stat1, stat2 = intro.apply(type_var=VarPrefix.Dependent)

    statement = Compound.Conjunction(stat1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def independent_variable_introduction__implication0__intersection(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <<M --> A> ==> C>
    premise2: <M --> B>
    |-
    conclusion: <(&&, <#x-->A>, <#x-->B>) ==> C>.
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stat1_subject: Statement = stat1.subject
    term_common = stat1_subject.subject if not inverse_copula else stat1.predicate

    intro = Introduction(stat1_subject, stat2, term_common)
    stat1_subject, stat2 = intro.apply(type_var=VarPrefix.Dependent)
    cpnd = Compound.Conjunction(stat1_subject, stat2)

    statement = Statement.Implication(cpnd, stat1.predicate)

    stamp = Stamp_merge(stamp_task, stamp_belief)

    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def independent_variable_introduction__implication1__intersection(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <C ==> <M --> A>>
    premise2: <M --> B>
    |-
    conclusion: (&&, <C ==> <#x-->A>>, <#x-->B>)
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stat1_predicate: Statement = stat1.predicate
    term_common = stat1_predicate.subject if not inverse_copula else stat1.predicate

    intro = Introduction(stat1, stat2, term_common)
    stat1, stat2 = intro.apply(type_var=VarPrefix.Dependent)
    compound = Compound.Conjunction(stat1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(compound, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(compound, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def dependent_variable_introduction__conjunction__intersection(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: (&&, C, <M-->A>)
    premise2: <M-->B>
    |-
    conclusion: (&&, C, <#x-->A>, <#x-->B>)
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    cpnd1: Compound = premise1.term
    stat2: Statement = premise2.term
    for cpnt in cpnd1:
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            stat1: Statement = cpnt
            if stat1.subject == stat2.subject and not inverse_copula:
                term_common = stat1.subject
                break
            elif stat1.predicate == stat2.predicate and inverse_copula:
                term_common = stat1.predicate
                break
    else:
        raise Exception("The common term cannot be found.")

    intro = Introduction(cpnd1, stat2, term_common)
    cpnd1, stat2 = intro.apply(type_var=VarPrefix.Dependent)

    compound = Compound.Conjunction(cpnd1, stat2)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_intersection(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(compound, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(compound, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


'''
Elimination Rules
'''

def dependent_variable_elimination__conjunction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: (&&, <#x-->A>, B)
    premise2: <M-->A>
    |-
    conclusion: B.
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    cpnd1: Compound = premise1.term
    stat2: Statement = premise2.term

    for i, cpnt in enumerate(cpnd1):
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            stat1: Statement = cpnt
            if stat1.subject == stat2.subject and inverse_copula:
                pos_common1 = [i]
                break
            elif stat1.predicate == stat2.predicate and not inverse_copula:
                pos_common1 = [i]
                break
    else:
        raise Exception("The common term cannot be found.")

    pos_common2 = []

    elimn: Elimination = get_elimination__var_const(cpnd1, stat2, pos_common1, pos_common2)
    cpnd1 = elimn.apply(type_var=VarPrefix.Dependent)
    
    compound = cpnd1 - stat2

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_anonymous_analogy(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(compound, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(compound, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def dependent_variable_elimination__implication1(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <A ==> (&&, <#x-->B>, C)>
    premise2: <M-->B>
    |-
    conclusion: <A ==> C>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    cpnd1: Compound = stat1.predicate

    for i, cpnt in enumerate(cpnd1):
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            cpnt_stat1: Statement = cpnt
            if cpnt_stat1.subject == stat2.subject and inverse_copula:
                pos_common1 = [1, i]
                break
            elif cpnt_stat1.predicate == stat2.predicate and not inverse_copula:
                pos_common1 = [1, i]
                break
    else:
        raise Exception("The common term cannot be found.")

    pos_common2 = []

    elimn: Elimination = get_elimination__var_const(stat1, stat2, pos_common1, pos_common2)
    stat1 = elimn.apply(type_var=VarPrefix.Dependent)
    
    cpnd1: Compound = stat1.predicate
    cpnd1 -= stat2
    statement = Statement.Implication(stat1.subject, cpnd1)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_anonymous_analogy(premise1.truth, premise2.truth)
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def dependent_variable_elimination__implication0__inheritance(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <(&&, <#x-->A>, B) ==> C>
    premise2: <M --> A>
    |-
    conclusion: <B ==> C>
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    cpnd1: Compound = stat1.subject

    for i, cpnt in enumerate(cpnd1):
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            cpnt_stat1: Statement = cpnt
            if cpnt_stat1.subject == stat2.subject and inverse_copula:
                pos_common1 = [0, i]
                break
            elif cpnt_stat1.predicate == stat2.predicate and not inverse_copula:
                pos_common1 = [0, i]
                break
    else:
        raise Exception("The common term cannot be found.")

    pos_common2 = []

    elimn: Elimination = get_elimination__var_const(stat1, stat2, pos_common1, pos_common2)
    stat1 = elimn.apply(type_var=VarPrefix.Dependent)
    
    cpnd1: Compound = stat1.subject
    cpnd1 -= stat2
    statement = Statement.Implication(cpnd1, stat1.predicate)

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_deduction(premise1.truth, premise2.truth) # why?
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)


def dependent_variable_elimination__implication0__implication(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    premise1: <(&&, <#x-->A>, B) ==> C>
    premise2: <<M-->A>==>C>
    |-
    conclusion: B
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    cpnd1: Compound = stat1.subject
    stat2_subject: Statement = stat2.subject

    for i, cpnt in enumerate(cpnd1):
        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
            cpnt_stat1: Statement = cpnt
            if cpnt_stat1.subject == stat2_subject.subject and inverse_copula:
                pos_common1 = [0, i]
                break
            elif cpnt_stat1.predicate == stat2_subject.predicate and not inverse_copula:
                pos_common1 = [0, i]
                break
    else:
        raise Exception("The common term cannot be found.")

    pos_common2 = [0]

    elimn: Elimination = get_elimination__var_const(stat1, stat2, pos_common1, pos_common2)
    stat1 = elimn.apply(type_var=VarPrefix.Dependent)
    
    cpnd1: Compound = stat1.subject
    statement = cpnd1 - stat2_subject

    stamp = Stamp_merge(stamp_task, stamp_belief)
    if task.is_judgement:
        truth = Truth_abduction(premise1.truth, premise2.truth) # why?
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    else: raise "Invalid case."

    return Task(sentence_derived, budget)