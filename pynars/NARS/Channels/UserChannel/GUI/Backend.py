from copy import deepcopy
from typing import Tuple, Union
from pathlib import Path
from multiprocessing import Process
import random
from pynars.NARS import Reasoner as Reasoner
from pynars.utils.Print import print_out, PrintType
from pynars.Narsese import Task
from typing import List
from pynars.utils.tools import rand_seed
import asyncio
from as_rpc import AioRpcServer, AioRpcClient, rpc
from functools import partial



def run_line(nars: Reasoner, line: str):
    ''''''

    ret = []
    satisfaction = []
    busyness = []
    alertness = []
    wellness = []

    def handle_line(tasks_line: Tuple[List[Task], Task, Task, List[Task], Task, Tuple[Task, Task]]):
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = tasks_line

        for task in tasks_derived:
            ret.append(repr(task))

        if judgement_revised is not None:
            ret.append(repr(judgement_revised))
        if goal_revised is not None:
            ret.append(repr(goal_revised))
        if answers_question is not None:
            for answer in answers_question:
                ret.append(repr(answer))
        if answers_quest is not None:
            for answer in answers_quest:
                ret.append(repr(answer))
        if task_executed is not None:
            ret.append(f'{task_executed.term.repr()} = {str(task_operation_return) if task_operation_return is not None else None}')

    line = line.strip(' \n')
    if line.startswith("'"):
        return None
    elif line.isdigit():
        n_cycle = int(line)
        for _ in range(n_cycle):
            tasks_all = nars.cycle()
            satisfaction.append(nars.global_eval.S)
            busyness.append(nars.global_eval.B)
            alertness.append(nars.global_eval.A)
            wellness.append(nars.global_eval.W)
            handle_line(tasks_all)
    else:
        line = line.rstrip(' \n')
        if len(line) == 0:
            return ret
        try:
            success, task, _ = nars.input_narsese(line, go_cycle=False)
            if success:
                ret.append(repr(task))
            else:
                ret.append(f':Invalid input! Failed to parse: {line}')

            tasks_all = nars.cycle()
            satisfaction.append(nars.global_eval.S)
            busyness.append(nars.global_eval.B)
            alertness.append(nars.global_eval.A)
            wellness.append(nars.global_eval.W)
            handle_line(tasks_all)
        except Exception as e:
            ret.append(f':Unknown error: {line}. \n{e}')
    return ret, (satisfaction, busyness, alertness, wellness)


def handle_lines(nars: Reasoner, lines: str):
    ret = []
    satisfaction = []
    busyness = []
    alertness = []
    wellness = []
    for line in lines.split('\n'):
        if len(line) == 0:
            continue

        ret_line, (satisfaction_line, busynesse_line, alertness_line, wellbeing_line) = run_line(nars, line)
        ret.extend(ret_line)
        satisfaction.extend(satisfaction_line)
        busyness.extend(busynesse_line)
        alertness.extend(alertness_line)
        wellness.extend(wellbeing_line)
    return '\n'.join(ret), (satisfaction, busyness, alertness, wellness)


def run_nars(capacity_mem=1000, capacity_buff=1000):
    seed = 137
    rand_seed(seed)
    nars = Reasoner(capacity_mem, capacity_buff)
    print_out(PrintType.COMMENT, 'Running with GUI.', comment_title='NARS')
    server = AioRpcServer(buff=6553500)
    rpc(server, "run_line")(run_line)

    def _handle_lines(content):
        return handle_lines(nars, content)
    rpc(server, "handle_lines")(_handle_lines)
    server.init()
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(run_nars())
    loop.run_forever()
