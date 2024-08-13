from pynars.Narsese import Sentence
from pynars.NARS.DataStructures._py.Channel import Channel, NarseseChannel
from pynars.NARS.DataStructures._py.Buffer import Buffer
from queue import Queue
from pynars.Narsese import Task
from pynars.Narsese import parser
from pynars.utils.Print import print_out, PrintType
from pynars.utils.tools import rand_seed
from typing import List, Tuple
from copy import deepcopy
from pynars import Narsese
from pynars.Narsese import Task
from pathlib import Path


class ConsoleChannel(NarseseChannel):
    ''''''

    def __init__(self, reasoner, capacity: int, seed=137, n_buckets: int = None, take_in_order: bool = False, max_duration: int = None) -> None:
        import threading
        from time import sleep
        from readchar import key
        from pynars.NARS import Reasoner
        self.nars: Reasoner = reasoner

        super().__init__(capacity, n_buckets, take_in_order, max_duration)

        rand_seed(seed)
        print_out(PrintType.COMMENT,
                  f'rand_seed={seed}', comment_title='Setup')
        print_out(PrintType.COMMENT, 'Console.', comment_title='NARS')

        self.terminated = False

        def console_input():
            while not self.terminated:
                if self.nars.paused:
                    while self.nars.paused:
                        print_out(PrintType.COMMENT, '',
                                  comment_title='Input', end='')
                        try:
                            lines = input()
                        except Exception as e:
                            print("KeyboardInterrupt")
                        lines = lines.split(key.CTRL_P)[-1]
                        self.handle_lines(lines)
                else:
                    sleep(0.1)

        self.thread_console = threading.Thread(target=console_input)
        # set as daemon thread, so that it exits when the main thread exits
        self.thread_console.setDaemon(True)
        self.thread_console.start()

    def on_cycle_finished(self):
        tasks = self.nars.get_derived_tasks()
        self.print_tasks(tasks)

    def run_line(self, line: str):
        nars = self.nars
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
            elif line == "''reset":
                nars.reset()
            elif line == "''run":
                nars.paused = False
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
                success, task, task_overflow = self.put(line)
                tasks = self.nars.cycle()
                # success, task, _ = nars.input_narsese(line, go_cycle=False)
                if success:
                    print_out(
                        PrintType.IN,
                        (f"[{task.channel_id}] " if task.channel_id > -1 else '') +
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

    def handle_lines(self, lines: str):
        nars = self.nars
        '''Handle inputs with NARS reasoner'''
        tasks_lines = []
        # run input line by line #
        for line in lines.split('\n'):
            # skip empty lines
            if len(line) == 0:
                continue
            # run non-empty lines
            tasks_line = self.run_line(line)
            if tasks_line is not None:
                tasks_lines.extend(tasks_line)
        # print the output #
        for tasks_line in tasks_lines:
            self.print_tasks(tasks_line)

    def run_file(self, filepath: str = None):
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
                self.handle_lines(lines)

    @staticmethod
    def print_tasks(tasks_packed: Tuple[
            List[Task],
            Task,
            Task,
            List[Task],
            List[Task],
            Tuple[Task, Task]]):
        # unpack one of lines of tasks, and then print out
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, \
            (task_operation_return, task_executed) = tasks_packed

        # while derived task(s)
        for task in tasks_derived:
            channel_id = f"[{task.channel_id}] " if task.channel_id > -1 else ''
            print_out(PrintType.OUT, channel_id +
                      task.sentence.repr(), *task.budget)

        # while revising a judgement
        if judgement_revised is not None:
            print_out(PrintType.OUT, channel_id + judgement_revised.sentence.repr(),
                      *judgement_revised.budget)

        # while revising a goal
        if goal_revised is not None:
            print_out(PrintType.OUT, channel_id + goal_revised.sentence.repr(),
                      *goal_revised.budget)

        # while answering a question for truth value
        if answers_question is not None:
            for answer in answers_question:
                print_out(
                    PrintType.ANSWER,
                    channel_id +
                    answer.sentence.repr(),
                    *answer.budget)
        # while answering a quest for desire value
        if answers_quest is not None:
            for answer in answers_quest:
                print_out(PrintType.ACHIEVED, channel_id +
                          answer.sentence.repr(), *answer.budget)
        # while executing an operation
        if task_executed is not None:
            print_out(
                PrintType.EXE, channel_id +
                f'''{task_executed.term.repr()} = {
                    str(task_operation_return) 
                    if task_operation_return is not None
                    else None}''')
