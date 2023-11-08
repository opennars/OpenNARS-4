'''Mimic from the pynars.Console module and mount an NARS
Based on the original interface, an NARS terminal is internally called that can be copied by constructing objects, and the underlying interface is exposed to other programs
Principle: Not responsible for "advanced command processing" other than basic command line operations
'''

from pathlib import Path
import argparse  # for cmdline

# compatible type annotation
from typing import List, Dict, Tuple, Union

# pynars
from pynars.utils.Print import print_out as print_out_origin
from pynars.NARS import Reasoner
from pynars.Narsese import Task
from pynars.utils.Print import PrintType
from pynars.Narsese import parser as NarseseParser
from copy import deepcopy

# utils #


def narsese_parse_safe(narsese: str) -> Union[None, Task]:
    '''
    Responsible for calling the NAL parser to parse statements

    Key features:
    - No error is reported, but checks for an error (returns a null value)
    - Integrate "analysis" and "test" into one

    Process:
    1. If it can be resolved, return the statement
    2. Can not parse (error), return a null value (can be used to judge)
    '''
    try:
        return NarseseParser.parse(narsese=narsese)
    except:  # if errors, return `None` that can be identify
        return None

# outpost interfaces #


class NARSOutput:
    type: PrintType
    content: str
    p: float
    d: float
    q: float
    comment_title: str
    end: str

    def __init__(self, type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        self.type = type
        self.content = content
        self.p = p
        self.d = d
        self.q = q
        self.comment_title = comment_title
        self.end = end

## NARS Interface Main ##


class NARSInterface:
    '''The main part of NARS Interface
    '''

    # Print out interface static methods & class variables #

    _show_color: bool = True
    # Try importing, prompt if no package is available and go to a more compatible path (less program dependency)
    try:
        # Import background class
        from sty import bg as _str_back_ground, fg as _str_fore_ground
    except:
        # No color mode
        _show_color = None
        print('Unable to import color pack! Automatically switched to `No color mode` and locked!')

    @property
    def show_color(self):
        return NARSInterface.show_color

    @show_color.setter
    def show_color(self, value: bool) -> Union[str, bool]:
        # strictly identify None rather than implicit bool(None) == False
        if NARSInterface._show_color == None:
            return None  # the color display cannot be enabled
        NARSInterface._show_color = value
        return NARSInterface._show_color

    def float_restrict_str(x):
        '''0 to 1 floating point constraint'''
        return (f'{round(x, 2):.2f}'
                if isinstance(x, float) and 0 <= x <= 1
                else '    ')

    def out_message_no_color(type: PrintType, content,
                             p: float = None, d: float = None, q: float = None,
                             comment_title: str = None):
        ''''from pynars.utils.Print import out_print'''
        # show_budget = True
        # if isinstance(p, float) and isinstance(d, float) and isinstance(q, float):
        #     if p<0 or p>1 or q<0 or q>1 or d<0 or d>1:
        #         show_budget = False
        # else:
        #     show_budget = False
        p_str: str = NARSInterface.float_restrict_str(p)
        q_str: str = NARSInterface.float_restrict_str(q)
        d_str: str = NARSInterface.float_restrict_str(d)
        if type:
            # ! ↓ The value of this enumeration class comes with a foreground color
            value: str = type.value[5:-1]
            if type is PrintType.COMMENT and comment_title is not None:
                return f'{comment_title}: {str(content)}'
            elif type is PrintType.INFO:
                return f'|{p_str}|{d_str}|{q_str}| {value}「{str(content)}」'
            else:
                return f'|{p_str}|{d_str}|{q_str}| {value} | {str(content)}'

    # modified colored output of Print.py
    @staticmethod
    def out_print_no_color(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        print(
            NARSInterface.out_message_no_color(
                type=type, content=content,
                p=p, d=d, q=q,
                comment_title=comment_title),
            end=end)

    def _is0to1Float(x): return isinstance(x, float) and 0 <= x <= 1

    def _bg_embrace(
        str, bg): return f'{bg}{str}{NARSInterface._str_back_ground.rs}'

    def _fg_embrace(
        str, fg): return f'{fg}{str}{NARSInterface._str_fore_ground.rs}'

    @staticmethod
    def out_message_with_color(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None):
        # show_budget = True
        # if isinstance(p, float) and isinstance(d, float) and isinstance(q, float):
        #     if p<0 or p>1 or q<0 or q>1 or d<0 or d>1:
        #         show_budget = False
        # else:
        #     show_budget = False
        '''
        TODO The conflict between simplicity and efficiency
        Although the code has become simpler, the actual call has gone through more functions and calculations, but it has become less concise
        '''

        bg, fg = NARSInterface._str_back_ground, NARSInterface._str_fore_ground
        bge, fge = NARSInterface._bg_embrace, NARSInterface._fg_embrace

        if NARSInterface._is0to1Float(p):
            bg1 = bg(min(255, int(255*p/2+10)), 10, 10)
            p = f' {round(p, 2):.2f} '
        else:
            p = '    '
            bg1 = ''
        if NARSInterface._is0to1Float(d):
            bg2 = bg(10, min(255, int(255*d/2+10)), 10)
            d = f' {round(d, 2):.2f} '
        else:
            d = '    '
            bg2 = ''
        if NARSInterface._is0to1Float(q):
            bg3 = bg(10, 10, min(255, int(255*q/2+10)))
            q = f' {round(q, 2):.2f} '
        else:
            q = '    '
            bg3 = ''

        # print(F'{bg(int(256*p),0,0)} {p} {bg(0,int(256*q),0)} {q} {bg(0,0,int(256*d))} {d} {bg.rs}{type.value} {str(content)}')

        if type is PrintType.COMMENT and comment_title is not None:
            return fge(comment_title + ': ' + str(content), fg.da_grey)
        else:
            return bge(p, bg1)+bge(d, bg2)+bge(q, bg3) + type.value + (
                fge(str(content), fg.grey)
                if type is PrintType.INFO
                else str(content)
            )

    @staticmethod
    def print_out_with_color(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        print(NARSInterface.out_message_with_color(
            type=type, content=content, p=p, d=d, q=q, comment_title=comment_title), end=end)

    @staticmethod
    def change_random_seed(seed: int) -> None:
        '''[Taken from Console.py and improved] Set random and numpy.random random seeds (global)'''
        # Set random seeds from random and numpy
        '''from importlib import import_module # ! Temporary not use
        [import_module(x) for x in ('random','numpy') if not x in globals()]'''
        if not 'random' in globals():
            import random
        random.seed(seed)

        if not 'numpy' in globals():
            import numpy as np
        np.random.seed(seed=seed)
        print_out_origin(PrintType.COMMENT,
                         f'Changing random seed={seed}...', comment_title='Setup')

    silent_output: bool = False
    'determines whether the output is hidden or not'
    
    volume_threshold: float = 0.5
    'determines the level (min threshold of total budget) of output (NARSOutput) generate, only affects the narsese output'

    # reasoner
    _NARS: Reasoner = None  # ! internal

    @property  # read only
    def reasoner(self) -> Reasoner:
        return self._NARS

    # NARS constructor & initialization #

    @staticmethod
    def construct_interface(seed:int=-1, memory:int=100, capacity:int=100, silent: bool = False):
        '''Construct the reasoner using specific construction parameters instead of having to construct the reasoner itself in each constructor'''
        return NARSInterface(seed=seed,
                             NARS=Reasoner(
                                 n_memory=memory, capacity=capacity),
                             silent=silent
                             )

    def __init__(self, seed=-1, NARS: reasoner = None, silent: bool = False) -> None:
        '''init the interface'''
        # random seed
        if seed > 0:
            NARSInterface.change_random_seed(seed)

        # config
        self.silent_output: bool = silent
        self.volume_threshold = 0

        # reasoner
        self.print_output(
            PrintType.COMMENT, f'{"Importing" if NARS else "Creating"} Reasoner...', comment_title='NARS')
        self._NARS = NARS if NARS else Reasoner(100, 100)
        self.print_output(
            PrintType.COMMENT, 'Run...', comment_title='NARS')
        ''' TODO?
        Use a Python dictionary instead of "external file address" to input configuration to the reasoner
        so that the reasoner's construction does not depend on external files
        '''

    # Interface to the outer interface of the PyNARS part #

    @staticmethod
    def direct_print(type: PrintType, content: any, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None) -> None:
        '''Direct print information by parameters'''
        (
            NARSInterface.print_out_with_color
            if NARSInterface.show_color
            else NARSInterface.out_print_no_color
        )(type=type, content=content, p=p, d=d, q=q, comment_title=comment_title, end=end)

    def print_output(self, type: PrintType, content: any, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None) -> None:
        # able to be silent
        if not self.silent_output:
            NARSInterface.direct_print(
                type=type, content=content,
                p=p, d=d, q=q,
                comment_title=comment_title,
                end=end)

    # _event_handlers: List[function] = [] # ! error: name 'function' is not defined
    _output_handlers: list = []

    @property  # read only
    def output_handlers(self):
        '''Registry of event handlers
            Standard format:
            ```
            def handler(out: NARSOutput):
                # your code
            ```
        '''
        return self._output_handlers

    def _handle_NARS_output(self, out: NARSOutput) -> None:
        '''Internally traverses the event handler registry table, running its internal functions one by one'''
        for handler in self._output_handlers:
            try:
                handler(out)
            except BaseException as e:
                print(
                    f'Handler "{handler.__name__}" errors when deal NARS output "{out}": {e}')

    def input_narsese(self, lines: str) -> List[NARSOutput]:
        '''Interfacing with NARS: Injects input provided by an external program into NARS'''
        return self._handle_lines(lines=lines)

    def execute_file(self, path: Union[Path, str]) -> None:
        '''Handle files'''
        # it's copied directly from Console.py
        if path is not None:
            path: Path = Path(path)
            file_name = path.name
            self.print_output(
                PrintType.COMMENT, f'Run file <{file_name}>.', comment_title='NARS')
            with open(path, 'r') as f:
                lines = f.read()
                self._handle_lines(lines)
            self.print_output(
                PrintType.COMMENT, 'Console.', comment_title='NARS')

    # History & Memories #

    _input_history: List[str] = []

    @property  # readonly
    def input_history(self) -> List[str]:
        '''Records texts (statements) entered into the interface'''
        return self._input_history

    '''
    # TODO: The `silent` cannot prevent printing the following lines
                    INFO  : Loading RuleMap <LUT.pkl>...
                    INFO  : Done. Time-cost: 0.3810005187988281s.
                    INFO  : Loading RuleMap <LUT_Tense.pkl>...
                    INFO  : Done. Time-cost: 0.0009992122650146484s.
    '''

    def _handle_lines(self, lines: str) -> List[NARSOutput]:
        '''
        Process the input stream of statements, decompose it into multiple statements, and pass each statement to NARS for processing, and finally return the result list of NARS output.

        Types of parameters and outputs and their effects:
        - Statement flow: str indicates the input NAL statement flow, which contains multiple NAL statements separated by newlines.
        - Returned value: List[NARSOutput], a list of output results after NARS processing, each element is an NARS output object.

        Internal variable types, meanings and mutual relations:
        - Task List: List[Tuple], which stores information about tasks processed by NARS. Each element is a task row and contains information about multiple tasks.
        - Task line: Tuple, which contains information about multiple tasks, such as the exported task, modified target, and modified target.
        - out Output list: List[NARSOutput], stores NARS output results, each element is an NARS output object.

        Main operation process:
        1. Decompose the input statement flow into multiple statements.
        2. Go through each statement, call "processing statement" to pass the statement to NARS for processing, and add the processing result to the task list.
        3. Traverse the task list, convert the task-related information into NARS output objects, and add them to the out output list.
        4. Traverse the out output list, call `self.print_output` to print the output, and call `self._handle_NARS_output` to broadcast the output.
        5. Return to the out output list.

        Possible exceptions:
        - Incorrect format of the input NAL statement: If the input statement does not comply with the NAL syntax rules, the NARS processing exception may occur.
        - NARS internal error or exception: When processing input statements, an error or exception may occur inside NARS, causing the processing to fail.
        '''

        # NARS undefined -> auto initialize

        if not self._NARS:
            self.__init__()

        # start to handle

        task_list = []
        for line in lines.split('\n'):
            if len(line) == 0:
                continue

            task_line = self.run_line(reasoner=self._NARS, line=line)
            self._input_history.append(line)
            if task_line is not None:
                task_list.extend(task_line)

        outs: List[NARSOutput] = []

        task_list: List[
            Tuple[
                List[Task], Task, Task,
                List[Task], Task,
                Tuple[Task, Task]
            ]
        ]
        for task_line in task_list:
            tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest,\
                (task_operation_return, task_executed) = task_line
            # * only the 'OUT' will be affected by silence level
            for derived_task in tasks_derived:
                '''
                Ref. OpenNARS 3.1.0 Memory.java line 344~352
                    ```
                    final float budget = t.budget.summary();
                    final float noiseLevel = 1.0f - (narParameters.VOLUME / 100.0f);
                    
                    if (budget >= noiseLevel) {  // only report significant derived Tasks
                        emit(OUT.class, t);
                        if (Debug.PARENTS) {
                            emit(DEBUG.class, "Parent Belief\t" + t.parentBelief);
                            emit(DEBUG.class, "Parent Task\t" + t.parentTask + "\n\n");
                        }
                    }
                    ```
                '''
                if derived_task.budget.summary > self.volume_threshold:
                    outs.append(
                        NARSOutput(
                            PrintType.OUT, derived_task.sentence.repr(), *derived_task.budget)
                    )

            if judgement_revised is not None:
                if judgement_revised.budget.summary > self.volume_threshold:
                    outs.append(NARSOutput(
                        PrintType.OUT, judgement_revised.sentence.repr(), *judgement_revised.budget))
            if goal_revised is not None:
                if judgement_revised.budget.summary > self.volume_threshold:
                    outs.append(NARSOutput(
                        PrintType.OUT, goal_revised.sentence.repr(), *goal_revised.budget))
            if answers_question is not None:
                for answer in answers_question:
                    outs.append(
                        NARSOutput(PrintType.ANSWER, answer.sentence.repr(), *answer.budget))
            if answers_quest is not None:
                for answer in answers_quest:
                    outs.append(NARSOutput(
                        PrintType.ACHIEVED, answer.sentence.repr(), *answer.budget))
            if task_executed is not None:
                outs.append(NARSOutput(
                    PrintType.EXE, f'{task_executed.term.repr()} = {str(task_operation_return) if task_operation_return is not None else None}'))

            # * print & event patch
            for out in outs:
                if out:
                    self.print_output(type=out.type, content=out.content, p=out.p,
                                      d=out.d, q=out.q, comment_title=out.comment_title, end=out.end)
                # broadcast outputs before return
                self._handle_NARS_output(out=out)

        # return outputs
        return outs

    # run line
    def run_line(self, reasoner: reasoner, line: str) -> Union[None, List[Task]]:
        '''Run one line of input'''
        line = line.strip(' \r\n\t')  # ignore spaces
        # special notations
        if line.startswith("''"):  #
            if line.startswith("''outputMustContain('"):
                line = line[len("''outputMustContain('"):].rstrip("')\n")  #
                if len(line) == 0:  # no any content
                    return
                if (check := narsese_parse_safe(line)):  # verify the input
                    self.print_output(
                        PrintType.INFO, f'OutputContains({check.sentence.repr()})')
                else:
                    self.print_output(
                        PrintType.ERROR, f'parse "{line}" failed!'
                    )
            return None
        # empty or comments
        elif len(line) == 0 or line.startswith("//") or line.startswith("'"):
            return None
        # digit -> run cycle
        elif line.isdigit():
            n_cycles = int(line)
            self.print_output(PrintType.INFO, f'Run {n_cycles} cycles.')
            tasks_in_cycles: List[Task] = []
            # Get all export statements run during this period, deep copy for backup
            for _ in range(n_cycles):
                tasks_caught = reasoner.cycle()
                tasks_in_cycles.append(deepcopy(tasks_caught))
            return tasks_in_cycles
        # narsese
        else:
            line = line.rstrip(' \n')  # ignore spaces and newline
            if 1:
                success, task, _ = reasoner.input_narsese(line, go_cycle=False)
                if success:  # input success
                    self.print_output(
                        PrintType.IN, task.sentence.repr(), *task.budget)
                else:  # input failed
                    self.print_output(
                        PrintType.ERROR, f'Input "{line}" failed.')
                tasks_caught = reasoner.cycle()  # run cycles
                return [deepcopy(tasks_caught)]  # Returns a inferred statement


def __main__():
    '''Main process'''
    # parse arguments
    parser = argparse.ArgumentParser(description='Parse NAL files.')
    parser.add_argument('filepath', metavar='Path',
                        type=str, nargs='*', help='file path of an *.nal file.')
    args = parser.parse_args()
    filepath: Union[list, None] = args.filepath
    filepath = filepath[0] if filepath else None
    # setup NARS interface
    interface: NARSInterface = NARSInterface.construct_interface()
    # enter console loop
    while True:
        interface.print_output(
            PrintType.COMMENT, '', comment_title='Input', end='')
        lines = input()
        try:
            interface._handle_lines(lines)
        except Exception as e:
            interface.print_output(
                PrintType.ERROR, f'Errors when input {lines}\n{e}')


if __name__ == '__main__':
    __main__()
