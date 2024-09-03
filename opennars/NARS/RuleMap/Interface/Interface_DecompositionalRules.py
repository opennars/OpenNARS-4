from opennars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from opennars.Narsese import Belief
from opennars.NAL.Inference import *
from opennars.NAL.Theorems import *
from opennars import Global

def _decompositional__decomposition_theorem2__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem2(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _decompositional__decomposition_theorem2__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem2(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

def _decompositional__decomposition_theorem3__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem3(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _decompositional__decomposition_theorem3__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem3(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

# def _decompositional__decomposition_theorem4__0_0(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return decomposition_theorem4(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

# def _decompositional__decomposition_theorem4__0_0_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
#     return decomposition_theorem4(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _decompositional__decomposition_theorem9(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem9(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _decompositional__decomposition_theorem9_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem9(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _decompositional__decomposition_theorem10(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem10(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)

def _decompositional__decomposition_theorem10_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return decompositional__decomposition_theorem10(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)
