from pynars.NARS.DataStructures import Link, TaskLink, TermLink, LinkType, Task
from pynars.Narsese import Belief
from pynars.NAL.Inference import *
from pynars.NAL.Theorems import *
from pynars import Global

'''negation'''
def _transform__negation(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return immediate__negation(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None))


'''contraposition'''
def _transform__contraposition(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return immediate__contraposition(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None))

'''product and image'''
def _transform__product_to_image(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return transform__product_to_image(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), index=tasklink.component_index)


def _transform__image_to_product(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return transform__image_to_product(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), index=tasklink.component_index)


def _transform__image_to_image(task: Task, belief: Belief, tasklink: TaskLink=None, termlink: TermLink=None):
    return transform__image_to_image(task, belief, (tasklink.budget if tasklink is not None else None), (termlink.budget if termlink is not None else None), index=tasklink.component_index)