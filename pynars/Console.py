from copy import deepcopy
from typing import Tuple, Union
from pathlib import Path
from pynars import Narsese, NAL, NARS
from time import sleep
from multiprocessing import Process
import os
from pynars.Narsese.Parser.parser import TreeToNarsese
from pynars.Narsese import Sentence
import random
from pynars.NARS import Reasoner as Reasoner
from pynars.utils.Print import print_out, PrintType
from pynars.Narsese import Task
from typing import List
from pynars.utils.tools import rand_seed
import argparse


def info(title):
    '''Print the info of module and process'''
    print(f'''
============= {title} =============
module name: {__name__}
parent process: {os.getppid()}
process id: {os.getpid()}
============={'=' * (len(title) + 2)}=============
    ''')


def run_line(nars: Reasoner, line: str):
    '''Run one line of input'''
    line = line.strip(' \n')
    # `//` comment
    if line.startswith("//"):
        return None
    # special notations
    elif line.startswith("''"):
        if line.startswith("''outputMustContain('"):
            line = line[len("''outputMustContain('"):].rstrip("')\n")
            if len(line) == 0:
                return
            try:
                content_check = Narsese.parser.parse(line)
                print_out(
                    PrintType.INFO,
                    f'OutputContains({content_check.sentence.repr()})')
            except:
                print_out(
                    PrintType.ERROR,
                    f'Invalid input! Failed to parse: {line}')
                # print_out(PrintType.ERROR, f'{file}, line {i}, {line}')
        return
    # `'` comment
    elif line.startswith("'"):
        return None
    # digit -> run cycle
    elif line.isdigit():
        n_cycle = int(line)
        print_out(PrintType.INFO, f'Run {n_cycle} cycles.')
        tasks_all_cycles = []
        for _ in range(n_cycle):
            tasks_all = nars.cycle()
            tasks_all_cycles.append(deepcopy(tasks_all))
        return tasks_all_cycles
    # narsese
    else:
        line = line.rstrip(' \n')
        if len(line) == 0:
            return None
        try:
            success, task, _ = nars.input_narsese(line, go_cycle=False)
            if success:
                print_out(
                    PrintType.IN,
                    task.sentence.repr(),
                    *task.budget)
            else:
                print_out(
                    PrintType.ERROR,
                    f'Invalid input! Failed to parse: {line}')

            tasks_all = nars.cycle()
            return [deepcopy(tasks_all)]
        except Exception as e:
            print_out(PrintType.ERROR, f'Unknown error: {line}. \n{e}')


def handle_lines(nars: Reasoner, lines: str):
    '''Handle inputs with NARS reasoner'''
    tasks_lines = []
    # run input line by line #
    for line in lines.split('\n'):
        # skip empty lines
        if len(line) == 0:
            continue
        # run non-empty lines
        tasks_line = run_line(nars, line)
        if tasks_line is not None:
            tasks_lines.extend(tasks_line)
    # print the output #
    tasks_lines: List[Tuple[
        List[Task],
        Task,
        Task,
        List[Task],
        Task,
        Tuple[Task, Task]]]
    for tasks_line in tasks_lines:
        # unpack one of lines of tasks, and then print out
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, \
        (task_operation_return, task_executed) = tasks_line
    
        # while derived task(s)
        for task in tasks_derived: print_out(PrintType.OUT, task.sentence.repr(), *task.budget)

        # while revising a judgement
        if judgement_revised is not None: print_out(PrintType.OUT, judgement_revised.sentence.repr(),*judgement_revised.budget)
                   
        # while revising a goal                                 
        if goal_revised is not None: print_out(PrintType.OUT, goal_revised.sentence.repr(), *goal_revised.budget)

        # while answering a question for truth value
        if answers_question is not None:
            for answer in answers_question:
                print_out(
                    PrintType.ANSWER,
                    answer.sentence.repr(),
                    *answer.budget)
        # while answering a quest for desire value
        if answers_quest is not None:
            for answer in answers_quest: print_out(PrintType.ACHIEVED, answer.sentence.repr(), *answer.budget)
        # while executing an operation
        if task_executed is not None:
            print_out(
                PrintType.EXE,
                f'''{task_executed.term.repr()} = {
                    str(task_operation_return) 
                    if task_operation_return is not None
                    else None}''')


def run_file(nars: Reasoner, filepath: str = None):
    '''Run the content of file'''
    # handle the file
    if filepath is not None:
        filepath: Path = Path(filepath)
        filename = filepath.name
        # notify
        print_out(
            PrintType.COMMENT,
            f'Run file <{filename}>.',
            comment_title='NARS')
        # open and run
        with open(filepath, 'r') as f:
            lines = f.read()
            handle_lines(nars, lines)


def run_nars(filepath: str, seed: int = 137, n_memory: int = 100, capacity: int = 100):
    '''Load the datas and launch the NARS reasoner'''
    # info('Console')
    # init status #
    rand_seed(seed)
    print_out(PrintType.COMMENT, f'rand_seed={seed}', comment_title='Setup')
    nars = Reasoner(n_memory, capacity)
    nars.register_operator('left', lambda *args: print('execute left.'))
    # try to run file if exists
    print_out(PrintType.COMMENT, 'Init...', comment_title='NARS')
    print_out(PrintType.COMMENT, 'Run...', comment_title='NARS')
    run_file(nars, filepath)
    # console #
    print_out(PrintType.COMMENT, 'Console.', comment_title='NARS')
    while True:
        print_out(PrintType.COMMENT, '', comment_title='Input', end='')
        lines = input()
        handle_lines(nars, lines)


if __name__ == '__main__':
    '''Main process'''
    # parse arguments
    parser = argparse.ArgumentParser(description='Parse NAL files.')
    parser.add_argument('filepath',
                        metavar='Path',
                        type=str,
                        nargs='*',
                        help='file path of an *.nal file.')
    args = parser.parse_args()
    # try to load files
    filepath: Union[list, None] = args.filepath
    filepath = (
        filepath[0]
        if filepath is not None and len(filepath) > 0
        else None)
    # launch NARS
    try:
        run_nars(filepath)
    # when stop
    except KeyboardInterrupt:
        print_out(PrintType.COMMENT, 'Stop...', comment_title='\n\nNARS')
    # main process finish
    print('Done.')

# if __name__ == '__main__':
#     # Process
#     info('main')
#     try:
#         p_console = Process(target=run_console, args=())
#         p_nars = Process(target=run_nars, args=())
#         p_console.start()
#         p_nars.start()
#         p_nars.join()
#         p_console.close()
#     except KeyboardInterrupt:
#         print('\n\nStop NARS...')

#     print('Done.')
