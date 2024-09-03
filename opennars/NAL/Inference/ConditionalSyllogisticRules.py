'''
Conditional syllogism

@ Author:   Bowen XU
@ Contact:  bowen.xu@pku.edu.cn
@ Update:   2021.11.7
@ Comment:
    The general form:
        def syllogistic_rule(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False): ...
    The param `inverse_premise` means whether to inverse the order of term in the task and term in the belief as the two premises, for example, if the terms in the task and the belief are {<S-->M>, <M-->P>}, and the `inverse_premise` equals `True`, then the premises are {<M-->P>, <S-->M>}.
    The param `inverse_copula` means whether to inverse the order of the subject and predicate in the task, for example, if the term in the task is <S-->M>, and the `inverse_copula` equals `True`, then the premise1 is <M-->S>.
    The param `inverse_copula` means whether to inverse the order of the subject and predicate in the task, for example, if the term in the task is <S-->M>, and the `inverse_copula` equals `True`, then the premise1 is <M-->S>.
    
'''
from opennars.Narsese import Copula, Statement, Compound, Connector, Task, Belief, Budget, Stamp, Truth

from ..Functions import F_deduction, F_analogy, F_comparison, F_abduction, F_induction, \
    fc_to_w_minus, fc_to_w_plus
from ..Functions import *
from opennars.Narsese import Judgement, Goal, Quest, Question

'''
The Conditional Syllogistic Rules (Table B.2)

    J1                  J2                  J                   F       function-name
------------------------------------------------------------------------------
1   S                   S <=> P             P                   F_ana   analogy
2   S                   P                   S <=> P             F_com   comparison
3   S ==> P             S                   P                   F_ded   deduction
4   P ==> S             S                   P                   F_abd   abduction
5   P                   S                   S ==> P             F_ind   induction
6   (&&, C, S) ==> P    S                   C ==> P             F_ded   deduction_compound_eliminate
7   (&&, C, S) ==> P    C ==> P             S                   F_abd   abduction_compound_eliminate
8   C ==> P             S                   (&&, C, S) ==> P    F_ind   induction_compound_compose
9   (&&, C, S) ==> P    M ==> S             (&&, C, M) ==> P    F_ded   deduction_compound_replace
10  (&&, C, S) ==> P    (&&, C, M) ==> P    M ==> S             F_abd   abduction_compound_eliminate2
11  (&&, C, M) ==> P    M ==> S             (&&, C, S) ==> P    F_ind   induction_compound_replace

Additional Rules, Ref: OpenNARS 3.0.4 SyllogysticRules.java

    J1                  J2                  J                   F
------------------------------------------------------------------------------
12  (&&, C, S) <=> P    S                   C <=> P             F_ana   analogy_compound_replace

'''

'''Compound irrelevant rules'''

def deduction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <S ==> P>. %f1;c1%
    j2: S. %f2;c2%
    |-
    j3: P. %F_ded%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief, stat1.copula)
    
    statement = stat1.predicate

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
    j1: <P ==> S>. %f1;c1%
    j2: S. %f2;c2%
    |-
    j3: P. %F_abd%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief, stat1.copula, reverse_order=True)

    statement = stat1.subject

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


def induction(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: P. %f1;c1%
    j2: S. %f2;c2%
    |-
    j3: <S ==> P>. %F_ind%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    statement = Statement(stat2, Copula.Implication, stat1)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
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
    j1: S. %f1;c1%
    j2: <S <=> P>. %f2;c2%
    |-
    j3: P. %F_ana%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    statement = stat2.predicate if not inverse_copula else stat2.subject

    if task.is_judgement:
        truth = Truth_analogy(premise1.truth, premise2.truth)
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


def comparison(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: S. %f1;c1%
    j2: P. %f2;c2%
    |-
    j3: <S <=> P>. %F_com%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    statement = Statement(stat1, Copula.Equivalence, stat2)

    if task.is_judgement:
        truth = Truth_comparison(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal:
        truth = Desire_weak(task.truth, belief.truth)
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


'''Compound relevant rules'''

def deduction_compound_eliminate(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <(&&, C, S, ...) ==> P>. %f1;c1%
    j2: S. %f2;c2%
    |-
    j3: <C ==> P>. %F_ded%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = stat1.subject
    compound = compound - stat2
    statement = Statement(compound, Copula.Implication, stat1.predicate)

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


def deduction_compound_replace(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <(&&, C, S, ...) ==> P>. %f1;c1%
    j2: <M ==> S>. %f2;c2%
    |-
    j3: <(&&, C, M, ...) ==> P>. %F_ded%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = stat1.subject
    compound = compound.replace(stat2.predicate, stat2.subject)
    statement = Statement(compound, Copula.Implication, stat1.predicate)

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


def abduction_compound_eliminate(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <(&&, C, S, ...) ==> P>. %f1;c1%
    j2: <C ==> P>. %f2;c2%
    |-
    j3: (&&, S, ...). %F_abd%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound: Compound = stat1.subject
    statement = compound - stat2.subject

    if task.is_judgement:
        truth = Truth_abduction(premise1.truth, premise2.truth)
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


def abduction_compound_eliminate2(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <(&&, C, S, ...) ==> P>. %f1;c1%
    j2: <(&&, C, M, ...) ==> P>. %f2;c2%
    |-
    j3: <M ==> S>. %F_abd%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)

    compound1: Compound = stat1.subject
    compound2: Compound = stat2.subject
    statement = Statement(compound2-compound1, Copula.Implication, compound1-compound2)

    if task.is_judgement:
        truth = Truth_abduction(premise1.truth, premise2.truth)
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


def induction_compound_compose(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <C ==> P>. %f1;c1%
    j2: S. %f2;c2%
    |-
    j3: <(&&, C, S) ==> P>. %F_ind%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    compound: Compound = Compound.Conjunction(stat1.subject, stat2)
    statement = Statement(compound, Copula.Implication, stat1.predicate)

    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
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


def induction_compound_replace(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    j1: <(&&, C, M, ...) ==> P>. %f1;c1%
    j2: <M ==> S>. %f2;c2%
    |-
    j3: <(&&, C, S, ...)  ==> P>. %F_ind%
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    compound: Compound = stat1.subject
    compound = compound.replace(stat2.subject, stat2.predicate)
    statement = Statement(compound, Copula.Implication, stat1.predicate)

    
    if task.is_judgement:
        truth = Truth_induction(premise1.truth, premise2.truth)
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


def analogy_compound_eliminate(task: Task, belief: Belief, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    S
    (&&, C, S, ...) <=> P    
    |-
    (&&, C, ...) <=> P
    '''
    premise1, premise2 = (task.sentence, belief.sentence) if not inverse_premise else (belief.sentence, task.sentence)

    stamp_task: Stamp = task.stamp
    stamp_belief: Stamp = belief.stamp
    
    stat1: Statement = premise1.term
    stat2: Statement = premise2.term
    stamp = Stamp_merge(stamp_task, stamp_belief)
    
    compound: Compound = stat2.subject
    compound = compound - stat1
    statement = Statement(compound, stat2.copula, stat2.predicate)

    if task.is_judgement:
        truth = Truth_analogy(premise1.truth, premise2.truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
        sentence_derived = Judgement(statement, stamp, truth)
    elif task.is_goal: 
        raise # TODO: if inverse the premises, the Desire function may diverse.
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