from pynars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from pynars.Narsese import Belief
from pynars.NAL.Inference import *
from pynars.NAL.Theorems import *
from pynars import Global
from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Term import Term


def _temporal__deduction_sequence_eliminate__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&/, C, +100, S, ...) =/> P>. C. :|:} |- <S=/>P>. :!105:'''
    return temporal__deduction_sequence_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__deduction_sequence_eliminate__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{C. :|: <(&/, C, +100, S, ...) =/> P>.} |- <S=/>P>. :!105:'''
    return temporal__deduction_sequence_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _temporal__abduction__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&/, C, +100, S, ...) =/> P>. C. :|:} |- <S=/>P>. :!105:'''
    return temporal__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__abduction__1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{C. :|: <(&/, C, +100, S, ...) =/> P>.} |- <S=/>P>. :!105:'''
    return temporal__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

def _temporal__deduction_sequence_replace__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- P.'''
    return temporal__deduction_sequence_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _temporal__deduction_sequence_replace__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<C ==> P>. <(&&, C, S, ...) ==> P>.} |- P.'''
    return temporal__deduction_sequence_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _temporal__sequence_immediate(task: Task, term_belief: Term, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{(&/, A, B, C)! A} |- A!.'''
    return temporal__sequence_immediate(task, term_belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _temporal__sequence(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{(&/, A, B, C)! A} |- A!.'''
    return temporal__sequence(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _temporal__sequence_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{C! (&/, A, B, C).} |- (&/, A, B)!'''
    return temporal__sequence(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=True)

    
def _temporal__parallel_immediate(task: Task, term_belief: Term, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{(&/, A, B, C)! A} |- A!.'''
    return temporal__parallel_immediate(task, term_belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _temporal__parallel(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{(&/, A, B, C)! A} |- A!.'''
    return temporal__parallel(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

# def _temporal__parallel_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     '''{(&/, A, B, C)! A} |- A!.'''
#     return temporal__parallel(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

'''analogy'''
def _temporal__analogy__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    is_equivalence = belief.term.copula in (Copula.ConcurrentEquivalence, Copula.PredictiveEquivalence)
    return temporal__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if is_equivalence else True, inverse_copula=False if is_equivalence else True)


def _temporal__analogy__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    is_equivalence = belief.term.copula in (Copula.ConcurrentEquivalence, Copula.PredictiveEquivalence)
    return temporal__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if is_equivalence else True, inverse_copula=True if is_equivalence else False)


def _temporal__analogy__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    is_equivalence = belief.term.copula in (Copula.ConcurrentEquivalence, Copula.PredictiveEquivalence)
    return temporal__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if is_equivalence else True, inverse_copula=False)


def _temporal__analogy__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    is_equivalence = belief.term.copula in (Copula.ConcurrentEquivalence, Copula.PredictiveEquivalence)
    return temporal__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if is_equivalence else True, inverse_copula=True)

'''Sequential induction'''
# TODO: the name of each rule may need to be modifed.
def _temporal__induction_implication(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_implication(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__induction_implication_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_implication(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _temporal__induction_equivalence(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_equivalence(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__induction_composition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

''''''
def _temporal__induction_predictieve_implication_composition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=False)


def _temporal__induction_predictive_implication_composition_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)


def _temporal__induction_predictive_implication_composition_inverse(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=True)


def _temporal__induction_predictive_implication_composition_inverse_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=True)


''''''
def _temporal__induction_retrospective_implication_composition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=False)


def _temporal__induction_retrospective_implication_composition_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)


def _temporal__induction_retrospective_implication_composition_inverse(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=True)


def _temporal__induction_retrospective_implication_composition_inverse_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_implication_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=True)


def _temporal__induction_predictive_equivalance_composition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_equivalance_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=False)

def _temporal__induction_predictive_equivalance_composition_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_predictive_equivalance_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)

def _temporal__induction_retrospective_equivalance_composition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_equivalance_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=False)

def _temporal__induction_retrospective_equivalance_composition_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__induction_retrospective_equivalance_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)
