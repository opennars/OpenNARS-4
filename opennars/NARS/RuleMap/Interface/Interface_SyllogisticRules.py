from opennars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from opennars.Narsese import Belief
from opennars.NAL.Inference import *
from opennars.NAL.Theorems import *
from opennars import Global

'''deduction'''
def _syllogistic__deduction__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<M-->P>, <S-->M>} |- <S-->P>'''
    return syllogistic__deduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _syllogistic__deduction__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<S-->M>, <M-->P>} |- <S-->P>'''
    return syllogistic__deduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''exemplification'''
def _syllogistic__exemplification__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<M-->S>, <P-->M>} |- <S-->P>'''
    return syllogistic__exemplification(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _syllogistic__exemplification__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    '''{<P-->M>, <M-->S>} |- <S-->P>'''
    return syllogistic__exemplification(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


'''induction'''
def _syllogistic__induction__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _syllogistic__induction__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''abduction'''
def _syllogistic__abduction__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _syllogistic__abduction__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _syllogistic__comparison__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False,inverse_copula=False)

def _syllogistic__comparison__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=False)

def _syllogistic__comparison__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False, inverse_copula=True)

def _syllogistic__comparison__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True, inverse_copula=True)


'''analogy'''
def _syllogistic__analogy__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=False if belief.term.is_commutative else True)


def _syllogistic__analogy__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=True if belief.term.is_commutative else False)


def _syllogistic__analogy__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=False)


def _syllogistic__analogy__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__analogy(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False if belief.term.is_commutative else True, inverse_copula=True)


'''resemblance'''
def _syllogistic__resemblance__0_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=inverse_premise)


def _syllogistic__resemblance__1_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=(not inverse_premise))


def _syllogistic__resemblance__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=False)


def _syllogistic__resemblance__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if (task.term.is_higher_order and (not belief.term.is_higher_order)) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=True)


def _syllogistic__resemblance__0_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=inverse_premise)


def _syllogistic__resemblance__1_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=(not inverse_premise))


def _syllogistic__resemblance__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=False)


def _syllogistic__resemblance__1_1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    inverse_premise = True if ((not task.term.is_higher_order) and belief.term.is_higher_order) else False
    return syllogistic__resemblance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=inverse_premise, inverse_copula=True)

'''reversion'''
def _syllogistic__reversion(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return syllogistic__reversion(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None))