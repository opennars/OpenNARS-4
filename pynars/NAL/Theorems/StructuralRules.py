from typing import List
from pynars.Narsese import Copula, Statement, Compound, Connector, Term, Judgement, Truth, Task, Belief, Budget, Stamp, Goal, Quest, Question
from pynars.Narsese import place_holder, truth_analytic

from ..Functions.TruthValueFunctions import *
from ..Functions.DesireValueFunctions import *
from ..Functions.StampFunctions import *
from ..Functions.BudgetFunctions import *


'''uni-composition (unilateral composition)'''
def uni_composition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <P --> S>.          (inverse_copula: <S --> P>.)
    (|, P, Q)           (inverse_copula: (&, P, Q))
    |- 
    <(|, P, Q) --> S>.  (inverse_copula: <S --> (&, P, Q)>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    
    subject = term_concept if not inverse_copula else stat.subject
    predicate = stat.predicate if not inverse_copula else term_concept

    truth = Truth_deduction(premise.truth, truth_analytic)
    statement = Statement(subject, stat.copula, predicate)
    budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

def uni_composition_prime(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <P --> S>.          (inverse_copula: <S --> P>.)
    (~, Q, P)           (inverse_copula: (-, Q, P))
    |- 
    <(~, Q, P) --> S>.  (inverse_copula: <S --> (-, Q, P)>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    
    subject = term_concept if not inverse_copula else stat.subject
    predicate = stat.predicate if not inverse_copula else term_concept

    truth = Truth_negation(Truth_deduction(premise.truth, truth_analytic))
    statement = Statement(subject, stat.copula, predicate)
    budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

'''uni-decomposition (unilateral composition)'''
# def uni_decomposition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
#     '''
#     e.g.
#     <(S|T) --> P>.          (inverse_copula: <P --> (S&T)>.)
#     S                       (inverse_copula: S)
#     |- 
#     <S --> P>.              (inverse_copula: <P --> S>.)
#     '''
#     stamp_task: Stamp = task.stamp
#     premise: Judgement = task.sentence
#     stat: Statement = premise.term
    
#     subject: Compound | Term = stat.subject - set(term_concept) if not inverse_copula else stat.subject
#     predicate: Compound | Term = stat.predicate if not inverse_copula else stat.predicate - set(term_concept)

#     truth = Truth_deduction(premise.truth, truth_analytic)
#     statement = Statement(subject, stat.copula, predicate)
#     budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
#     stamp = stamp_task
#     sentence_derived = Judgement(statement, stamp, truth)

#     return Task(sentence_derived, budget)


def uni_decomposition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <(S|T) --> P>.          (inverse_copula: <P --> (S&T)>.)
    S                       (inverse_copula: S)
    |- 
    <S --> P>.              (inverse_copula: <P --> S>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    
    subject: Union[Compound, Term] = stat.subject if not inverse_copula else term_concept
    predicate: Union[Compound, Term] = term_concept if not inverse_copula else stat.predicate

    truth = Truth_deduction(premise.truth, truth_analytic)
    statement = Statement(subject, stat.copula, predicate)
    budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

'''bi-composition (bilateral compose)'''
def bi_composition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <S --> P>. (inverse_copula: <P --> S>.)
    (|, S, M)  (inverse_copula: (|, S, M))
    |- 
    <(|, S, M) --> (|, P, M)>. (inverse_copula: <(|, P, M) --> (|, S, M)>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    compound: Compound = term_concept
        
    subject = compound if not inverse_copula else compound.replace(stat.predicate, stat.subject)
    predicate = compound.replace(stat.subject, stat.predicate) if not inverse_copula else compound

    statement = Statement(subject, stat.copula, predicate)
    truth = Truth_deduction(premise.truth, truth_analytic)
    budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

def bi_composition_prime(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <S --> P>. (inverse_copula: <P --> S>.)
    (-, M, S)  (inverse_copula: (-, M, S))
    |- 
    <(-, M, P) --> (-, M, S)>. (inverse_copula: <(-, M, S) --> (-, M, P)>.)

    <S --> P>. (inverse_copula: <P --> S>.)
    (/, M1, M2, _ S)  (inverse_copula: (/, M1, M2, _ S))
    |- 
    <(/, M1, M2, _ P) --> (/, M1, M2, _ S)>. (inverse_copula: <(/, M1, M2, _ S) --> (/, M1, M2, _ P)>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    compound: Compound = term_concept
        
    subject = compound if not inverse_copula else compound.replace(stat.predicate, stat.subject)
    predicate = compound.replace(stat.subject, stat.predicate) if not inverse_copula else compound

    statement = Statement(predicate, stat.copula, subject)
    truth = Truth_deduction(premise.truth, truth_analytic)
    budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


'''bi-decomposition (bilateral decompose)'''
def bi_decomposition(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g.
    <(S*T) --> (P*T)>.  (inverse_copula: <(P*T) --> (S*T)>.)
    S                   (inverse_copula: S)
    |- 
    <S --> P>.          (inverse_copula: <P --> S>.)
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    compound_subject: Compound = stat.subject
    compound_predicate: Compound = stat.predicate

    subject = compound_subject - compound_predicate
    predicate = compound_predicate - compound_subject
    statement = Statement(subject, stat.copula, predicate)

    truth = Truth_deduction(premise.truth, truth_analytic)
    if premise.is_judgement or premise.is_goal:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


'''transform product to image'''
def transform_product_to_image(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    inverse_copula=False:
        <(*, T1, T2) --> R> |- <T1 --> (/, R, _, T2)>
        <(*, T1, T2) --> R> |- <T2 --> (/, R, T1, _)>
    inverse_copula=True:
        <R --> (*, T1, T2)> |- <(\, R, _, T2) --> T1>
        <R --> (*, T1, T2)> |- <(\, R, T1, _) --> T2>
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    
    subject = term_concept if not inverse_copula else Compound.IntensionalImage(term_concept, stat.subject, compound_product=stat.predicate)
    predicate = Compound.ExtensionalImage(term_concept, stat.predicate, compound_product=stat.subject) if not inverse_copula else term_concept
    statement = Statement(subject, stat.copula, predicate)

    truth = premise.truth
    if premise.is_judgement or premise.is_goal:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

# TODO: The higher-order case of product-image transformation.
# Ref: OpenNARS 3.0.4 StructuralRules.java line 375~474
def transform_product_to_image_higher_order(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    e.g. 
        <(&&,<(*,a,b) --> R>,...) ==> C>. |- <(&&,<a --> (/,R,_,b)>,...) ==> C>
        <(&&,<(*,a,b) --> R>,...) <=> C>. |- <(&&,<a --> (/,R,_,b)>,...) <=> C>
    '''


'''transform image to product'''
def transform_image_to_product(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    inverse_copula=False:
        <T1 --> (/, R, _, T2)> |- <(*, T1, T2) --> R>                 
        <T2 --> (/, R, T1, _)> |- <(*, T1, T2) --> R>                 
    inverse_copula=True:
        <(\, R, _, T2) --> T1> |- <R --> (*, T1, T2)>                 
        <(\, R, T1, _) --> T2> |- <R --> (*, T1, T2)>                 
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    
    compound_subject: Compound = stat.subject
    compound_predicate: Compound = stat.predicate
    subject = Compound.Product(stat.subject, compound_product=compound_predicate) if not inverse_copula else compound_predicate[0]
    predicate = compound_subject[0] if not inverse_copula else Compound.Product(stat.predicate, compound_product=compound_subject)

    statement = Statement(subject, stat.copula, predicate)
    truth = premise.truth
    if premise.is_judgement or premise.is_goal:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


'''
Inheritence Theorems

term1           --> term2
----------------------------------------
ok 1 (&, T1, T2)         T1
ok 2 T1                  (|, T1, T2)
ok 3 (-, T1, T2)         T1         
ok 4 T1                  (~, T1, T2)
5 (*, (/, R, _, T), T)   R
6 R                   (*, (\, R, _, T), T)

'''

# uni-composition, uni-decomposition--------------------

def inheritance_theorem1(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <(&, T1, T2) --> T1>.
    unicompsition (inverse_premise=False):
        <P-->S>.
        <(&, P, Q) --> P>. (analytic truth)
        |-
        <(&, P, Q) --> S>.
    unidecomposition (inverse_premise=True):
        <(&, P, Q) --> P>. (analytic truth)
        <S --> (&, P, Q)>.
        |-
        <S --> P>.
    '''
    return uni_composition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True) if not inverse_premise else uni_decomposition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True)


def inheritance_theorem2(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <T1 --> (|, T1, T2)>.
    unicompsition (inverse_premise=False):
        <P --> (|, P, Q)>. (analytic truth)
        <S-->P>.
        |-
        <S --> (|, P, Q)>.
    unidecomposition (inverse_premise=True):
        <(|, P, Q)-->S>.
        <P --> (|, P, Q)>. (analytic truth)
        |-
        <P --> S>.
    '''
    return uni_composition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False) if not inverse_premise else uni_decomposition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False)


def inheritance_theorem3(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <(-, T1, T2) --> T1>.
    unicompsition (inverse_premise=False):
        <P-->S>.
        <(-, P, Q) --> P>. (analytic truth)
        |-
        <(-, P, Q) --> S>.
    unidecomposition (inverse_premise=True):
        <(-, P, Q) --> P>. (analytic truth)
        <S --> (&, P, Q)>.
        |-
        <S --> P>.
    '''
    return uni_composition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True) if not inverse_premise else uni_decomposition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True)


def inheritance_theorem4(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <T1 --> (~, T1, T2)>.
    unicompsition (inverse_premise=False):
        <P --> (~, P, Q)>. (analytic truth)
        <S-->P>.
        |-
        <S --> (~, P, Q)>.
    unidecomposition (inverse_premise=True):
        (~, P, Q)-->S>.
        <P --> (~, P, Q)>. (analytic truth)
        |-
        <P --> S>.
    '''
    return uni_composition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False) if not inverse_premise else uni_decomposition(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False)

# ------------------------------------------------------


def inheritance_theorem5(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <(*, (/, R, _, T), T) --> R>.
    '''
    return Judgement(
        Statement(
            Compound(
                Connector.Product, 
                Compound(
                    Connector.ExtensionalImage, R, place_holder, T
                ),
                T
            ),
            Copula.Inheritance,
            R            
        ),
        Truth(1, 1, 0)
    )


def inheritance_theorem6(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=None):
    '''
    <R --> (*, (\, R, _, T), T)>.
    '''
    return Judgement(
        Statement(
            R,
            Copula.Inheritance,
            Compound(
                Connector.Product, 
                Compound(
                    Connector.IntensionalImage, R, place_holder, T
                ),
                T
            )         
        ),
        Truth(1, 1, 0)
    )


'''
Similarity Theorems

term1                           <-> term2
---------------------------------------
1 (--, (--, T))                       T
2 (|, ({, T1), ..., ({, Tn))          ({, T1, ..., Tn)
3 (&, ([, T1), ..., ([, Tn))          ([, T1, ..., Tn)
4 (-, ({, T1, ..., Tn), ({, Tn))      ({, T1, ..., Tn-1)
5 (~, ([, T1, ..., Tn), ([, Tn))      ([, T1, ..., Tn-1)
6 (/, (*, T1, T2), _, T2)             T1
7 (\, (*, T1, T2), _, T2)             T1
'''

def similarity_theorem1(R: Term, T: Term):
    '''
    <(--, (--, T)) <-> T>.
    '''
    return Judgement(
        Statement(
            Compound(Connector.Negation, Compound(Connector.Negation, T)),
            Copula.Inheritance,
            T
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem2_1(T1: Term, T2: Term, *Ts: Term):
    '''
    <(|, ({, T1), ..., ({, Tn)) <-> ({, T1, ..., Tn)>.
    '''
    Ts: List[Compound] = (T1, T2, *Ts)
    for T in Ts:
        T: Compound
        assert isinstance(T, Compound) and T.connector == Connector.ExtensionalSet
    
    term1 = Compound(Connector.IntensionalIntersection, *Ts)
    term2 = Compound(Connector.ExtensionalSet, *(T[0] for T in Ts))

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem2_2(T1: Term, T2: Term, *Ts: Term):
    '''
    <({, T1, ..., Tn) <-> (|, ({, T1), ..., ({, Tn))>.
    '''
    Ts: List[Compound] = (T1, T2, *Ts)
    
    term1 = Compound(Connector.IntensionalIntersection,  *(Compound(Connector.ExtensionalSet, T) for T in Ts))
    term2 = Compound(Connector.ExtensionalSet, *Ts)

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem3_1(T1: Term, T2: Term, *Ts: Term):
    '''(&, ([, T1), ..., ([, Tn))          ([, T1, ..., Tn)'''
    Ts: List[Compound] = (T1, T2, *Ts)
    for T in Ts:
        T: Compound
        assert isinstance(T, Compound) and T.connector == Connector.ExtensionalSet
    
    term1 = Compound(Connector.ExtensionalIntersection, *Ts)
    term2 = Compound(Connector.IntensionalSet, *(T[0] for T in Ts))

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem3_2(T1: Term, T2: Term, *Ts: Term):
    '''(&, ([, T1), ..., ([, Tn))          ([, T1, ..., Tn)'''
    Ts: List[Compound] = (T1, T2, *Ts)
    
    term1 = Compound(Connector.ExtensionalIntersection,  *(Compound(Connector.IntensionalSet, T) for T in Ts))
    term2 = Compound(Connector.IntensionalSet, *Ts)

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem4(T1: Term, T2: Term, *Ts: Term):
    '''
    (-, ({, T1, ..., Tn), ({, Tn)) <-> ({, T1, ..., Tn-1)
    '''
    Ts: List[Compound] = (T1, T2, *Ts)
    Ts = Ts[:-1]
    Tn = Ts[-1]
    term1 = Compound(Connector.ExtensionalDifference, Compound(Connector.ExtensionalSet, *Ts), Compound(Connector.ExtensionalSet, Tn))
    term2 = Compound(Connector.ExtensionalSet, *Ts)

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem5(T1: Term, T2: Term, *Ts: Term):
    '''
    (~, ([, T1, ..., Tn), ([, Tn)) <-> ([, T1, ..., Tn-1)
    '''
    Ts: List[Compound] = (T1, T2, *Ts)
    Ts = Ts[:-1]
    Tn = Ts[-1]
    term1 = Compound(Connector.IntensionalDifference, Compound(Connector.IntensionalSet, *Ts), Compound(Connector.IntensionalSet, Tn))
    term2 = Compound(Connector.IntensionalSet, *Ts)

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem6(T1: Term, T2: Term):
    '''
    (/, (*, T1, T2), _, T2) <-> T1
    '''
    term1 = Compound(Connector.ExtensionalImage, Compound(Connector.Product, T1, T2), place_holder, T2)
    term2 = T1

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

def similarity_theorem7(T1: Term, T2: Term):
    '''
    (\, (*, T1, T2), _, T2) <-> T1
    '''
    term1 = Compound(Connector.IntensionalImage, Compound(Connector.Product, T1, T2), place_holder, T2)
    term2 = T1

    return Judgement(
        Statement(
            term1,
            Copula.Similarity,
            term2
        ),
        Truth(1, 1, 0)
    )

'''
The Implication Theorems

statement1 ==> statement2
---------------------------------------

ok 1 <S <-> P>       <S --> P>
ok 2 <S <=> P>       <S ==> P>
ok 3 (&&, S1, S2)    S1
4 S1              (||, S1, S2)
ok 5 <S --> P>       <(|, S, M) --> (|, P, M)>
ok 6 <S --> P>       <(&, S, M) --> (&, P, M)>
ok 7 <S <-> P>       <(|, S, M) <-> (|, P, M)>
ok 8 <S <-> P>       <(&, S, M) <-> (&, P, M)>
ok 9 <S ==> P>       <(||, S, M) ==> (||, P, M)>
ok 10 <S ==> P>       <(&&, S, M) ==> (&&, P, M)>
ok 11 <S <=> P>       <(||, S, M) <=> (||, P, M)>
ok 12 <S <=> P>       <(&&, S, M) <=> (&&, P, M)>
ok 13 <S --> P>       <(-, S, M) --> (-, P, M)>
ok 14 <S --> P>       <(-, M, P) --> (-, M, S)>
ok 15 <S --> P>       <(~, S, M) --> (~, P, M)>
ok 16 <S --> P>       <(~, M, P) --> (~, M, S)>
ok 17 <S <-> P>       <(-, S, M) <-> (-, P, M)>
ok 18 <S <-> P>       <(-, M, P) <-> (-, M, S)>
ok 19 <S <-> P>       <(~, S, M) <-> (~, P, M)>
ok 20 <S <-> P>       <(~, M, P) <-> (~, M, S)>
21 <M --> (-, T1, T2)>     (--, <M --> T2>)
22 <(~, T1, T2) --> M>     (--, <T2 --> M>)
23 <S --> P>               <(/, S, M) --> (/, P, M)>
24 <S --> P>               <(\, S, M) --> (\, P, M)>
25 <S --> P>               <(/, M, P) --> (/, M, S)>
26 <S --> P>               <(\, M, P) --> (\, M, S)>
'''

def implication_theorem1(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <S --> P>>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term

    subject = stat.subject if not inverse_copula else stat.predicate
    predicate = stat.predicate if not inverse_copula else stat.subject
    statement = Statement(subject, stat.copula, predicate)
    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_deduction(premise.truth, truth_analytic)
        sentence_derived = Judgement(statement, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    # elif premise.is_goal:
    #     truth = Truth_deduction(premise.truth, truth_analytic)
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


def implication_theorem2(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <=> P> ==> <S ==> P>>.
    '''
    return implication_theorem1(task, term_concept, budget_tasklink, budget_termlink, inverse_premise, inverse_copula)


def implication_theorem3(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <(&&, S1, S2) ==> S1>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence

    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_deduction(premise.truth, truth_analytic)
        sentence_derived = Judgement(term_concept, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_goal:
        truth = Truth_deduction(premise.truth, truth_analytic)
        sentence_derived = Goal(term_concept, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_question:
        sentence_derived = Question(term_concept, stamp)
        budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
        # budget = Budget_backward_compound(sentence_derived.term, budget_tasklink, budget_termlink)
        
    elif premise.is_quest:
        sentence_derived = Quest(term_concept, stamp)
        budget = Budget_backward_compound(premise.term, budget_tasklink, budget_termlink)
        # budget = Budget_backward_compound(sentence_derived.term, budget_tasklink, budget_termlink) 
    else: raise 'Invalid case.' 
    
    return Task(sentence_derived, budget)


def implication_theorem4(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <S1 ==> (||, S1, S2)>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence

    stamp = stamp_task
    if premise.is_judgement:
        truth = Truth_deduction(premise.truth, truth_analytic)
        sentence_derived = Judgement(term_concept, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_goal:
        truth = Truth_deduction(premise.truth, truth_analytic)
        sentence_derived = Goal(term_concept, stamp, truth)
        budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    elif premise.is_question:
        sentence_derived = Question(term_concept, stamp)
        budget = Budget_backward_compound(term_concept, budget_tasklink, budget_termlink)
    elif premise.is_quest:
        sentence_derived = Quest(term_concept, stamp)
        budget = Budget_backward_compound(term_concept, budget_tasklink, budget_termlink)
    else: raise 'Invalid case.'
    
    return Task(sentence_derived, budget)


# bi-composition----------------------------------------

def implication_theorem5(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(|, S, M) --> (|, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem6(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(&, S, M) --> (&, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem7(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(|, S, M) <-> (|, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem8(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(&, S, M) <-> (&, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem9(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S ==> P> ==> <(||, S, M) ==> (||, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem10(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S ==> P> ==> <(&&, S, M) ==> (&&, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem11(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <=> P> ==> <(||, S, M) <=> (||, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem12(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <=> P> ==> <(&&, S, M) <=> (&&, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem13(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(-, S, M) --> (-, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem14(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(-, M, P) --> (-, M, S)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem15(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(~, S, M) --> (-, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem16(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(~, M, P) --> (~, M, S)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem17(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(-, S, M) <-> (-, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem18(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(-, M, P) <-> (-, M, S)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem19(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(~, S, M) <-> (~, P, M)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)


def implication_theorem20(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> ==> <(~, M, P) <-> (~, M, S)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink)

# ------------------------------------------------------


def implication_theorem21(M: Term, T1: Term, T2: Term):
    '''
    <<M --> (-, T1, T2)> ==> (--, <M --> T2>)>.
    '''
    return Judgement(
        Statement(
            Statement(M, Copula.Inheritance, Compound(Connector.ExtensionalDifference, T1, T2)),
            Copula.Implication,
            Compound(Connector.Negation, Statement(M, Copula.Inheritance, T2))
        ),
        Truth(1, 1, 0)
    )

def implication_theorem22(M: Term, T1: Term, T2: Term):
    '''
    <<(~, T1, T2) --> M> ==> (--, <T2 --> M>)>.
    '''
    return Judgement(
        Statement(
            Statement(Compound(Connector.IntensionalDifference, T1, T2), Copula.Inheritance, M),
            Copula.Implication,
            Compound(Connector.Negation, Statement(T2, Copula.Inheritance, M))
        ),
        Truth(1, 1, 0)
    )


def implication_theorem23(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(/, S, M) --> (/, P, M)>>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Inheritance, P),
            Copula.Implication,
            Statement(Compound(Connector.ExtensionalImage, S, M), Copula.Inheritance,Compound(Connector.ExtensionalImage, P, M))
        ),
        Truth(1, 1, 0)
    )


def implication_theorem24(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(\, S, M) --> (\, P, M)>>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Inheritance, P),
            Copula.Implication,
            Statement(Compound(Connector.IntensionalImage, S, M), Copula.Inheritance,Compound(Connector.IntensionalImage, P, M))
        ),
        Truth(1, 1, 0)
    )


def implication_theorem25(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(/, M, P) --> (/, M, S)>>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Inheritance, P),
            Copula.Implication,
            Statement(Compound(Connector.ExtensionalImage, M, P), Copula.Inheritance,Compound(Connector.ExtensionalImage, M, S))
        ),
        Truth(1, 1, 0)
    )


def implication_theorem26(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> ==> <(\, M, P) --> (\, M, S)>>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Inheritance, P),
            Copula.Implication,
            Statement(Compound(Connector.IntensionalImage, M, P), Copula.Inheritance,Compound(Connector.IntensionalImage, M, S))
        ),
        Truth(1, 1, 0)
    )


'''
The Equivalence Theorems (Table B.9)

statement1                      <=> statement2
------------------------------------------------------------------------------
1 <S <-> P>                           (&&, <S --> P>, <P --> S>)
2 <S <=> P>                           (&&, <S ==> P>, <P ==> S>)
ok 3 <S <-> P>                           <({, S) <-> ({, P)>
ok 4 <S <-> P>                           <([, S) <-> ([, P)>
ok 5 <S --> ({, P)>                      <S <-> ([, P)>
ok 6 <([, S) --> P>                      <([, S) <-> P>
7 <(*, S1, S2) --> (*, P1, P2)>       (&&, <S1 --> P1>, <S2 --> P2>)
8 <(*, S1, S2) <-> (*, P1, P2)>       (&&, <S1 <-> P1>, <S2 <-> P2>)
ok 9 <S --> P>                           <(*, M, S) --> (*, M, P)>
ok 10 <S --> P>                           <(*, S, M) --> (*, P, M)>
ok 11 <S <-> P>                           <(*, M, S) <-> (*, M, P)>
ok 12 <S <-> P>                           <(*, S, M) <-> (*, P, M)>
ok <(*, T1, T2) --> R>                 <T1 --> (/, R, _, T2)>
ok <(*, T1, T2) --> R>                 <T2 --> (/, R, T1, _)>
ok <R --> (*, T1, T2)>                 <(\, R, _, T2) --> T1>
ok <R --> (*, T1, T2)>                 <(\, R, T1, _) --> T2>
17 <S1 ==> <S2 ==> S3>>                 <(&&, S1, S2) ==> S3>
18 (--, (&&, S1, S2))                  (||, (--, S1), (--, S2))
19 (--, (||, S1, S2))                  (&&, (--, S1), (--, S2))
20 <S1 <=> S2>                         <(--, S1) <=> (--, S2)>

'''

def equivalence_theorem1(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> <=> (&&, <S --> P>, <P --> S>)>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Similarity, P),
            Copula.Equivalence,
            Compound(Connector.Conjunction, Statement(S, Copula.Inheritance, P), Statement(P, Copula.Inheritance, S))
        ),
        Truth(1, 1, 0)
    )

def equivalence_theorem2(S: Term, P: Term):
    '''
    <<S <=> P> <=> (&&, <S ==> P>, <P ==> S>)>.
    '''
    return Judgement(
        Statement(
            Statement(S, Copula.Equivalence, P),
            Copula.Equivalence,
            Compound(Connector.Conjunction, Statement(S, Copula.Implication, P), Statement(P, Copula.Implication, S))
        ),
        Truth(1, 1, 0)
    )


# ok ---------------------------------------------------

def equivalence_theorem3(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> <=> <({, S) <-> ({, P)>>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    truth = premise.truth
    copula = stat.copula

    if not inverse_copula:
        subject = Compound.Instance(stat.subject)
        predicate = Compound.Instance(stat.predicate)
    else:
        compound_subject: Compound = stat.subject
        compound_predicate: Compound = stat.predicate
        subject = compound_subject[0]
        predicate = compound_predicate[0]

    statement = Statement(subject, copula, predicate)
    
    if premise.is_judgement:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_goal or premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


def equivalence_theorem4(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> <=> <({, S) <-> ({, P)>>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    truth = premise.truth
    copula = stat.copula

    
    if not inverse_copula:
        subject = Compound.Property(stat.subject)
        predicate = Compound.Property(stat.predicate)
    else:
        compound_subject: Compound = stat.subject
        compound_predicate: Compound = stat.predicate
        subject = compound_subject[0]
        predicate = compound_predicate[0]

    statement = Statement(subject, copula, predicate)
    if premise.is_judgement:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_goal or premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


def equivalence_theorem5(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> {P}> <=> <S <-> {P}>>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    truth = premise.truth
    if not inverse_copula:
        copula = Copula.Similarity 
        subject = stat.subject
        predicate = stat.predicate
    else:
        copula = Copula.Inheritance
        compound_subject: Compound = stat.subject
        compound_predicate: Compound = stat.predicate
        if compound_subject.is_compound and compound_subject.connector == Connector.ExtensionalSet:
            subject = stat.subject
            predicate = stat.predicate
        elif compound_predicate.is_compound and compound_predicate.connector == Connector.ExtensionalSet:
            subject = stat.predicate
            predicate = stat.subject

    statement = Statement(subject, copula, predicate)

    if premise.is_judgement:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_goal or premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    statement = Statement(subject, copula, predicate)
    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)


def equivalence_theorem6(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<[S] --> P> <=> <[S] <-> P>>.
    '''
    stamp_task: Stamp = task.stamp
    premise: Judgement = task.sentence
    stat: Statement = premise.term
    truth = premise.truth
    if not inverse_copula:
        copula = Copula.Similarity 
        subject = stat.subject
        predicate = stat.predicate
    else:
        copula = Copula.Inheritance
        compound_subject: Compound = stat.subject
        compound_predicate: Compound = stat.predicate
        if compound_subject.is_compound and compound_subject.connector == Connector.IntensionalSet:
            subject = stat.subject
            predicate = stat.predicate
        elif compound_predicate.is_compound and compound_predicate.connector == Connector.IntensionalSet:
            subject = stat.predicate
            predicate = stat.subject

    statement = Statement(subject, copula, predicate)

    if premise.is_judgement:
        budget = Budget_forward_compound(statement, truth, budget_tasklink, budget_termlink)
    elif premise.is_goal or premise.is_question or premise.is_quest:
        budget = Budget_backward_compound(truth, budget_tasklink, budget_termlink)

    stamp = stamp_task
    sentence_derived = Judgement(statement, stamp, truth)

    return Task(sentence_derived, budget)

# ------------------------------------------------------


def equivalence_theorem7(S1: Term, S2: Term, P1: Term, P2: Term):
    '''
    <<(*, S1, S2) --> (*, P1, P2)> <=> (&&, <S1 --> P1>, <S2 --> P2>)>.
    '''
    return Judgement(
        Statement(
            Statement(Compound(Connector.Product, S1, S2), Copula.Inheritance, Compound(Connector.Product, P1, P2)),
            Copula.Equivalence,
            Compound(Connector.Conjunction, Statement(S1, Copula.Inheritance, P1), Statement(S2, Copula.Inheritance, P2))
        ),
        Truth(1, 1, 0)
    )

def equivalence_theorem8(S1: Term, S2: Term, P1: Term, P2: Term):
    '''
    <<(*, S1, S2) <-> (*, P1, P2)> <=>(&&, <S1 <-> P1>, <S2 <-> P2>)>.
    '''
    return Judgement(
        Statement(
            Statement(Compound(Connector.Product, S1, S2), Copula.Similarity, Compound(Connector.Product, P1, P2)),
            Copula.Equivalence,
            Compound(Connector.Conjunction, Statement(S1, Copula.Similarity, P1), Statement(S2, Copula.Similarity, P2))
        ),
        Truth(1, 1, 0)
    )


# bi-composition, bi-decomposition----------------------

def equivalence_theorem9(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> <=> <(*, M, S) --> (*, M, P)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink) if not inverse_copula else bi_decomposition(task, term_concept, budget_tasklink, budget_termlink)


def equivalence_theorem10(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S --> P> <=> <(*, S, M) --> (*, P, M)>>.
    '''
    return equivalence_theorem9(task, term_concept, budget_tasklink, budget_termlink, inverse_premise, inverse_copula)


def equivalence_theorem11(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> <=> <(*, M, S) <-> (*, M, P)>>.
    '''
    return bi_composition(task, term_concept, budget_tasklink, budget_termlink) if not inverse_copula else bi_decomposition(task, term_concept, budget_tasklink, budget_termlink)


def equivalence_theorem12(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<S <-> P> <=> <(*, S, M) <-> (*, P, M)>>.
    '''
    return equivalence_theorem11(task, term_concept, budget_tasklink, budget_termlink, inverse_premise, inverse_copula)

# ------------------------------------------------------


def equivalence_theorem13(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<(*, T1, T2) --> R> <=> <T1 --> (/, R, _, T2)>>.
    '''
    return transform_product_to_image(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False) if not inverse_copula else transform_image_to_product(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=False)


def equivalence_theorem14(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<(*, T1, T2) --> R> <=> <T2 --> (/, R, T1, _)>>.
    '''
    return equivalence_theorem13(task, term_concept, budget_tasklink, budget_termlink, inverse_premise, inverse_copula)


def equivalence_theorem15(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<R --> (*, T1, T2)> <=> <(\, R, _, T2) --> T1>>.
    '''
    return transform_product_to_image(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True) if not inverse_copula else transform_image_to_product(task, term_concept, budget_tasklink, budget_termlink, inverse_copula=True)


def equivalence_theorem16(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False):
    '''
    <<R --> (*, T1, T2)> <=> <(\, R, T1, _) --> T2>>.
    '''
    return equivalence_theorem15(task, term_concept, budget_tasklink, budget_termlink, inverse_premise, inverse_copula)


def equivalence_theorem17(S1: Term, S2: Term, S3: Term):
    '''
    <<S1 ==> <S2 ==> S3>> <=> <(&&, S1, S2) ==> S3>>.
    '''
    assert isinstance(S1, Statement) and isinstance(S2, Statement) and isinstance(S3, Statement)
    return Judgement(
        Statement(
            Statement(S1, Copula.Implication, Statement(S2, Copula.Implication, S3)),
            Copula.Equivalence,
            Statement(Compound(Connector.Conjunction, S1, S2), Copula.Implication, S3)
        ),
        Truth(1, 1, 0)
    )

def equivalence_theorem18(S1: Term, S2: Term):
    '''
    <(--, (&&, S1, S2)) <=> (||, (--, S1), (--, S2))>.
    '''
    assert isinstance(S1, Statement) and isinstance(S2, Statement)
    return Judgement(
        Statement(
            Compound(Connector.Negation, Compound(Connector.Conjunction, S1, S2)),
            Copula.Equivalence,
            Compound(Connector.Disjunction, Compound(Connector.Negation, S1), Compound(Connector.Negation, S2))
        ),
        Truth(1, 1, 0)
    )

def equivalence_theorem19(S1: Term, S2: Term):
    '''
    <(--, (||, S1, S2)) <=> (&&, (--, S1), (--, S2))>.
    '''
    assert isinstance(S1, Statement) and isinstance(S2, Statement)
    return Judgement(
        Statement(
            Compound(Connector.Negation, Compound(Connector.Disjunction, S1, S2)),
            Copula.Equivalence,
            Compound(Connector.Conjunction, Compound(Connector.Negation, S1), Compound(Connector.Negation, S2))
        ),
        Truth(1, 1, 0)
    )

def equivalence_theorem20(S1: Term, S2: Term):
    '''
    <<S1 <=> S2> <=> <(--, S1) <=> (--, S2)>>.
    '''
    assert isinstance(S1, Statement) and isinstance(S2, Statement)
    return Judgement(
        Statement(
            Statement(S1, Copula.Equivalence, S2),
            Copula.Equivalence,
            Statement(Compound(Connector.Negation, S1), Copula.Equivalence, Compound(Connector.Negation, S2))
        ),
        Truth(1, 1, 0)
    )
