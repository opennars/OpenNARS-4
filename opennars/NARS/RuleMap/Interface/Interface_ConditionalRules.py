from opennars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from opennars.Narsese import Belief
from opennars.NAL.Inference import *
from opennars.NAL.Theorems import *
from opennars import Global

'''deduction'''
def _conditional__deduction__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<S ==> P>. S.} |- P.'''
    return conditional__deduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _conditional__deduction__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{S. <S ==> P>.} |- P.'''
    return conditional__deduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _conditional__deduction_compound_eliminate__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- P.'''
    return conditional__deduction_compound_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _conditional__deduction_compound_eliminate__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<C ==> P>. <(&&, C, S, ...) ==> P>.} |- P.'''
    return conditional__deduction_compound_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _conditional__deduction_compound_replace__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- P.'''
    return conditional__deduction_compound_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _conditional__deduction_compound_replace__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<C ==> P>. <(&&, C, S, ...) ==> P>.} |- P.'''
    return conditional__deduction_compound_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''abduction'''
def _conditional__abduction__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return conditional__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _conditional__abduction__1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return conditional__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

def _conditional__abduction_compound_eliminate__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- (&&, S, ...).'''
    return conditional__abduction_compound_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _conditional__abduction_compound_eliminate__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- (&&, S, ...).'''
    return conditional__abduction_compound_eliminate(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _conditional__abduction_compound_eliminate2__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- (&&, S, ...).'''
    return conditional__abduction_compound_eliminate2(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _conditional__abduction_compound_eliminate2__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, S, ...) ==> P>. <C ==> P>.} |- (&&, S, ...).'''
    return conditional__abduction_compound_eliminate2(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''induction'''
def _conditional__induction_compound_replace__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<(&&, C, M, ...) ==> P>. <M ==> S>.} |- <(&&, C, S, ...)  ==> P>.%'''
    return conditional__induction_compound_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _conditional__induction_compound_replace__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<M ==> S>. <(&&, C, M, ...) ==> P>.} |- <(&&, C, S, ...)  ==> P>.%'''
    return conditional__induction_compound_replace(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''analogy'''
def _conditional__analogy__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{S. <S<=>P>.} |- P.'''
    return conditional__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=False)


def _conditional__analogy__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<S<=>P>. S.} |- P.'''
    return conditional__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)

def _conditional__analogy__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{S. <P<=>S>.} |- P.'''
    return conditional__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=True)


def _conditional__analogy__1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<P<=>S>. S.} |- P.'''
    return conditional__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=True)

# def _syllogistic__analogy__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=True if belief.term.is_commutative else False)


# def _syllogistic__analogy__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=False)


# def _syllogistic__analogy__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=True)


# '''resemblance'''
# def _syllogistic__resemblance__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=inverse_premise)


# def _syllogistic__resemblance__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=(not inverse_premise))


# def _syllogistic__resemblance__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=False)


# def _syllogistic__resemblance__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=True)


# def _syllogistic__resemblance__0_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=inverse_premise)


# def _syllogistic__resemblance__1_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=(not inverse_premise))


# def _syllogistic__resemblance__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=False)


# def _syllogistic__resemblance__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
#     return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=True)

# '''reversion'''
# def _syllogistic__reversion(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return syllogistic__reversion(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None))