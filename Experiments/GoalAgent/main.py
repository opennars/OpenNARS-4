import threading
import queue
import subprocess
import random
import signal
from pynars.NARS.Control.Reasoner import Reasoner
from time import time
import sty
from pynars.Config import Config
from pynars import Narsese
from pynars.utils.Print import print_out, PrintType
import numpy as np
import random

seed = 2
random.seed(seed)
np.random.seed(seed)

def main():
    Config.projection_decay = 1e-4
    nars = Reasoner(100, 100)
    nars.register_operator("say_hello", say_hello)

    # task1 = Narsese.parse("<{SELF}-->[good]>! :|:")
    # task2 = Narsese.parse("<{SELF}-->[good]>! :|:")
    # nars.internal_experience.put(task1)
    # nars.internal_experience.put(task1)
    # nars.internal_experience.put(task2)
    # nars.internal_experience.take()

    # _, task, _ = nars.input_narsese("< A =/> B >. :|:")
    # print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)
    # _, task, _ = nars.input_narsese("B! :|:")
    # print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)
    # for _ in range(50):
    #     tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
    #         task_operation_return, task_executed) = nars.cycle()
    #     if task_executed is not None:
    #         print_out(PrintType.EXE, f"{task_executed.sentence.repr()} {str(task_executed.stamp)}", *task.budget)
    #     for task in tasks_derived:
    #         print_out(PrintType.OUT, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)


    _, task, _ = nars.input_narsese("<<(*,{SELF}) --> ^say_hello> =/> <{SELF}-->[good]>>. :|:")
    print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)
    _, task, _ = nars.input_narsese("<{SELF}-->[good]>! :|:")
    print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)
    for _ in range(50):
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = nars.cycle()
        if task_executed is not None:
            print_out(PrintType.EXE, f"{task_executed.sentence.repr()} {str(task_executed.stamp)}", *task.budget)
        for task in tasks_derived:
            print_out(PrintType.OUT, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)

    print("============")
    _, task, _ = nars.input_narsese("<<(*,{SELF}) --> ^say_hello> =/> <{SELF}-->[good]>>. :|:")
    print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)
    _, task, _ = nars.input_narsese("<{SELF}-->[good]>! :|:")
    print_out(PrintType.IN, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)

    for _ in range(50):
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = nars.cycle()
        if task_executed is not None:
            print_out(PrintType.EXE, f"{task_executed.sentence.repr()} {str(task_executed.stamp)}", *task.budget)
        for task in tasks_derived:
            print_out(PrintType.OUT, f"{task.sentence.repr()} {str(task.stamp)}", *task.budget)



def say_hello(*args):
    
    print(f'{sty.fg.green}hello{sty.rs.fg}')


if __name__ == '__main__':
    main()
