from pynars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from pynars.Narsese import Belief
from pynars.NAL.Inference import *
from pynars.NAL.Theorems import *
from pynars import Global


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


def _temporal__implication_induction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__implication_induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__implication_induction_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__implication_induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)


def _temporal__composition_induction(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__composition_induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=False)


def _temporal__composition_induction_prime(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    ''''''
    return temporal__composition_induction(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), inverse_premise=True)

