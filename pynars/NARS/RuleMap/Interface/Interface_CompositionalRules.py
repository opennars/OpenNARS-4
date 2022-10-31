from pynars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from pynars.Narsese import Belief
from pynars.NAL.Inference import *
from pynars.NAL.Theorems import *
from pynars import Global


'''first-order With common subject'''

def _compositional__intersection_extension__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__intersection_extension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _compositional__union_extension__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__union_extension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


'''First-order with common predicate'''

def _compositional__intersection_intension__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__intersection_intension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _compositional__union_intension__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__union_intension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


'''higher-order With common subject'''

def _compositional__conjunction_extension__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__conjunction_extension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _compositional__disjunction_extension__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__disjunction_extension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


'''higher-order With common predicate'''
def _compositional__conjunction_intension__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__conjunction_intension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _compositional__disjunction_intension__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return compositional__disjunction_intension(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


'''Theorems'''

'''structural rules'''
def _structural__bi_composition__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__bi_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _structural__bi_composition__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__bi_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)

def _structural__bi_composition__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__bi_composition_prime(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _structural__bi_composition__1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__bi_composition_prime(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)

def _structural__uni_composition__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _structural__uni_composition__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_composition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)

def _structural__uni_composition__0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_composition_prime(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _structural__uni_composition__1_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_composition_prime(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)


def _structural__uni_decomposition__0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_decomposition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _structural__uni_decomposition__1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__uni_decomposition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)


'''implication theorems'''
def _structural__implication_theorem3(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__implication_theorem3(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)


def _structural__implication_theorem4(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return structural__implication_theorem4(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)
