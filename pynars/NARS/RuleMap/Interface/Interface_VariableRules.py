from pynars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from pynars.Narsese import Belief
from pynars.NAL.Inference import *
from pynars.NAL.Theorems import *
from pynars import Global


"""
Introduction Rules
"""

'''induction'''
def _variable__independent_variable_introduction__induction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _variable__independent_variable_introduction__induction_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

def _variable__independent_variable_introduction__implication__induction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__implication__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _variable__independent_variable_introduction__conjunction__induction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__conjunction__induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

'''comparison'''
def _variable__independent_variable_introduction__comparison__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _variable__independent_variable_introduction__comparison__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__comparison(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)


'''abduction'''
def _variable__independent_variable_introduction__abduction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _variable__independent_variable_introduction__abduction_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__abduction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


'''intersection'''
def _variable__dependent_variable_introduction__intersection__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_introduction__intersection(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _variable__dependent_variable_introduction__intersection__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_introduction__intersection(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=True)

def _variable__dependent_variable_introduction__conjunction__intersection(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_introduction__conjunction__intersection(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _variable__independent_variable_introduction__implication0__intersection__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__implication0__intersection(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _variable__independent_variable_introduction__implication1__intersection__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__independent_variable_introduction__implication1__intersection(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

"""
Elimination Rules
"""

def _variable__dependent_variable_elimination__conjunction__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_elimination__conjunction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)

def _variable__dependent_variable_elimination__implication1__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_elimination__implication1(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)


def _variable__dependent_variable_elimination__implication0__inheritance__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_elimination__implication0__inheritance(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)


def _variable__dependent_variable_elimination__implication0__implication__1_1(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return variable__dependent_variable_elimination__implication0__implication(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_copula=False)