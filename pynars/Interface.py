'''Mimic from the pynars.Console module and mount an NARS
Based on the original interface, an NARS terminal is internally called that can be copied by constructing objects, and the underlying interface is exposed to other programs
Principle: Not responsible for "advanced command processing" other than basic command line operations
'''

from typing import Tuple, List, Union
from pathlib import Path
import argparse  # for cmdline

# pynars
from pynars.utils.Print import print_out as printOut
from pynars.NARS import Reasoner
from pynars.Narsese import Task
from pynars.utils.Print import PrintType
from pynars import Config
from pynars.Narsese import parser as NarseseParser
from copy import deepcopy

# utils #


def NAL_Parse(narsese: str) -> None | Task:
    '''
    Responsible for calling the NAL parser to parse statements
    ! It might raise errors
    '''
    return NarseseParser.parse(narsese)


def NAL_GrammarParse(narsese: str) -> None | Task:
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
        return NAL_Parse(narsese=narsese)
    except:  # if errors, return `None` that can be identify
        return None

# outpost interfaces #


class NARSOutput:
    type: PrintType
    content: any
    p: float
    q: float
    commentTitle: str
    end: str

    def __init__(self, type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        self.type = type
        self.content = content
        self.p = p
        self.d = d
        self.q = q
        self.comment_title = comment_title
        self.end = end


## default config ##

DEFAULT_CONFIG: dict = {
    "PROGRAM": {
        "VERSION": "0.0.1",
        "DRIVER": "py"
    },
    "HYPER-PARAMS": {
        "DEFAULT": {
            "BUDGET": {
                "PRIORITY_JUDGEMENT": 0.8,
                "DURABILITY_JUDGEMENT": 0.5,
                "PRIORITY_QUESTION": 0.9,
                "DURABILITY_QUESTION": 0.9,
                "PRIORITY_QUEST": 0.9,
                "DURABILITY_QUEST": 0.9,
                "PRIORITY_GOAL": 0.9,
                "DURABILITY_GOAL": 0.9,
                "THRESHOLD": 0.01
            },
            "NUM_BUCKETS": 100,
            "TRUTH": {
                "FREQUENCY": 1.0,
                "CONFIDENCE": 0.9,
                "CONFIDENCE_JUDGEMENT": 0.9,
                "CONFIDENCE_GOAL": 0.9,
                "K": 1
            },
            "MAX_DURATION": 1000,
            "CONCEPT": {
                "NUM_LEVELS_TASKLINK_BAG": 1000,
                "CAPACITY_TASKLINK_BAG": 10000,
                "NUM_LEVELS_TERMLINK_BAG": 1000,
                "CAPACITY_TERMLINK_BAG": 10000,
                "CAPACITY_TABLE": 100
            },
            "COMPLEXITY_UNIT": 1.0,  # 1.0 - oo
            "QUALITY_MIN": 0.3,
            "CYCLES_PER_DURATION": 5,
            "NUM_FORGET_DURATIONS": 2,
            "REVISION_MAX_OCCURRENCE_DISTANCE": 10,
            # The rate of confidence decrease in mental operations Doubt and Hesitate
            "RATE_DISCOUNT_CONFIDENCE": 0.5,
            "RATE_DISCOUNT_PRIORITY_INTERNAL_EXPERIENCE": 0.1,
            "RATE_DISCOUNT_DURABILITY_INTERNAL_EXPERIENCE": 0.1,
            "TEMPORAL_DURATION": 5,
            "NUM_SEQUENCE_ATTEMPTS": 10,
            "NUM_OP_CONDITION_ATTEMPTS": 10
        },
        "TRUTH_EPSILON": 0.01,
        "BUDGET_EPSILON": 0.0001,
        "COMPLEXITY_UNIT": 1.0
    }
}

## NARS Interface Main ##


class NARSInterface:
    '''The main part of NARS Interface
    '''

    # Print out interface static methods & class variables #

    _showColor: bool = True
    # Try importing, prompt if no package is available and go to a more compatible path (less program dependency)
    try:
        from sty import bg as _strBackGround, fg as _strForeGround  # Import background class
    except:
        # No color mode
        _showColor = None
        print('Unable to import color pack! Automatically switched to `No color mode` and locked!')

    @property
    def showColor(self):
        return NARSInterface.showColor

    @showColor.setter
    def showColor(self, value: bool) -> bool | None:
        # strictly identify None rather than implicit bool(None) == False
        if NARSInterface._showColor == None:
            return None  # the color display cannot be enabled
        NARSInterface._showColor = value
        return NARSInterface._showColor

    def floatRestrictStr(x):
        '''0 to 1 floating point constraint'''
        return (f'{round(x, 2):.2f}'
                if isinstance(x, float) and 0 <= x <= 1
                else '    ')

    def outMessageNoColor(type: PrintType, content,
                          pStr: float = None, dStr: float = None, qStr: float = None,
                          comment_title: str = None):
        ''''from pynars.utils.Print import out_print'''
        # show_budget = True
        # if isinstance(p, float) and isinstance(d, float) and isinstance(q, float):
        #     if p<0 or p>1 or q<0 or q>1 or d<0 or d>1:
        #         show_budget = False
        # else:
        #     show_budget = False
        pStr: str = NARSInterface.floatRestrictStr(pStr)
        qStr: str = NARSInterface.floatRestrictStr(qStr)
        dStr: str = NARSInterface.floatRestrictStr(dStr)
        if type:
            # ! ↓ The value of this enumeration class comes with a foreground color
            value: str = type.value[5:-1]
            if type is PrintType.COMMENT and comment_title is not None:
                return f'{comment_title}: {str(content)}'
            elif type is PrintType.INFO:
                return f'|{pStr}|{dStr}|{qStr}| {value}「{str(content)}」'
            else:
                return f'|{pStr}|{dStr}|{qStr}| {value} | {str(content)}'

    # modified colored output of Print.py
    @staticmethod
    def outPrintNoColor(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        print(
            NARSInterface.outMessageNoColor(
                type=type, content=content,
                p=p, d=d, q=q,
                comment_title=comment_title,
                end=end))

    def _is0to1Float(x): return isinstance(x, float) and 0 <= x <= 1

    def _bgEmbrace(
        str, bg): return f'{bg}{str}{NARSInterface._strBackGround.rs}'

    def _fgEmbrace(
        str, fg): return f'{fg}{str}{NARSInterface._strForeGround.rs}'

    @staticmethod
    def outMessageWithColor(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None):
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

        bg, fg = NARSInterface._strBackGround, NARSInterface._strForeGround
        bge, fge = NARSInterface._bgEmbrace, NARSInterface._fgEmbrace

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
    def printOutWithColor(type: PrintType, content, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None):
        print(NARSInterface.outMessageWithColor(
            type=type, content=content, p=p, d=d, q=q, comment_title=comment_title), end=end)

    @staticmethod
    def changeRandomSeed(seed: int) -> None:
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
        printOut(PrintType.COMMENT,
                 f'Changing random seed={seed}...', comment_title='Setup')

    @staticmethod
    def loadConfig(content: str) -> None:
        Config.loadFromStr(content=content)

    silentOutput: bool = False

    # reasoner
    _NARS: Reasoner = None  # ! internal

    @property  # read only
    def reasoner(self) -> Reasoner:
        return self._NARS

    # NARS constructor & initialization #

    @staticmethod
    def constructInterface(seed=-1, memory=100, capacity=100, silent: bool = False):
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
            NARSInterface.changeRandomSeed(seed)

        # config
        self.silentOutput: bool = silent

        # reasoner
        self.printOutput(
            PrintType.COMMENT, f'{"Importing" if NARS else "Creating"} Reasoner...', comment_title='NARS')
        self._NARS = NARS if NARS else Reasoner(100, 100)
        self.printOutput(
            PrintType.COMMENT, 'Run...', comment_title='NARS')
        ''' TODO?
        Use a Python dictionary instead of "external file address" to input configuration to the reasoner
        so that the reasoner's construction does not depend on external files
        '''

    # Interface to the outer interface of the PyNARS part #

    @staticmethod
    def directPrint(type: PrintType, content: any, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None) -> None:
        '''Direct print information by parameters'''
        (
            NARSInterface.printOutWithColor
            if NARSInterface.showColor
            else NARSInterface.outPrintNoColor
        )(type=type, content=content, p=p, d=d, q=q, comment_title=comment_title, end=end)

    def printOutput(self, type: PrintType, content: any, p: float = None, d: float = None, q: float = None, comment_title: str = None, end: str = None) -> None:
        # able to be silent
        if not self.silentOutput:
            NARSInterface.directPrint(
                type=type, content=content,
                p=p, d=d, q=q,
                comment_title=comment_title,
                end=end)

    # _eventHandlers: list[function] = [] # ! error: name 'function' is not defined
    _eventHandlers: list = []

    @property  # read only
    def eventHandlers(self):
        '''Registry of event handlers
            Standard format:
            ```
            def handler(out: NARSOutput):
                # your code
            ```
        '''
        return self._eventHandlers

    def _handleNARSOutput(self, out: NARSOutput):
        '''Internally traverses the event handler registry table, running its internal functions one by one'''
        for handler in self._eventHandlers:
            try:
                handler(out)
            except BaseException as e:
                print(
                    f'Handler "{handler.__name__}" errors when deal NARS output "{out}": {e}')

    def inputNAL(self, lines: str) -> list[NARSOutput]:
        '''Interfacing with NARS: Injects input provided by an external program into NARS'''
        return self._handleLines(lines=lines)

    def executeFile(self, path: str | Path) -> None:
        '''Handle files'''
        # it's copied directly from Console.py
        if path is not None:
            path: Path = Path(path)
            file_name = path.name
            self.printOutput(
                PrintType.COMMENT, f'Run file <{file_name}>.', comment_title='NARS')
            with open(path, 'r') as f:
                lines = f.read()
                self._handleLines(lines)
            self.printOutput(
                PrintType.COMMENT, 'Console.', comment_title='NARS')

    # History & Memories #

    _inputHistory: list[str] = []

    @property  # readonly
    def inputHistory(self):
        '''Records texts (statements) entered into the interface'''
        return self._inputHistory

    '''
    # TODO: The `silent` cannot prevent printing the following lines
                    INFO  : Loading RuleMap <LUT.pkl>...
                    INFO  : Done. Time-cost: 0.3810005187988281s.
                    INFO  : Loading RuleMap <LUT_Tense.pkl>...
                    INFO  : Done. Time-cost: 0.0009992122650146484s.
    '''

    def _handleLines(self, lines: str) -> list[NARSOutput]:
        '''
        Process the input stream of statements, decompose it into multiple statements, and pass each statement to NARS for processing, and finally return the result list of NARS output.

        Types of parameters and outputs and their effects:
        - Statement flow: str indicates the input NAL statement flow, which contains multiple NAL statements separated by newlines.
        - Returned value: list[NARSOutput], a list of output results after NARS processing, each element is an NARS output object.

        Internal variable types, meanings and mutual relations:
        - Task List: List[Tuple], which stores information about tasks processed by NARS. Each element is a task row and contains information about multiple tasks.
        - Task line: Tuple, which contains information about multiple tasks, such as the exported task, modified target, and modified target.
        - out Output list: list[NARSOutput], stores NARS output results, each element is an NARS output object.

        Main operation process:
        1. Decompose the input statement flow into multiple statements.
        2. Go through each statement, call "processing statement" to pass the statement to NARS for processing, and add the processing result to the task list.
        3. Traverse the task list, convert the task-related information into NARS output objects, and add them to the out output list.
        4. Traverse the out output list, call `self.printOutput` to print the output, and call `self._handleNARSOutput` to broadcast the output.
        5. Return to the out output list.

        Possible exceptions:
        - Incorrect format of the input NAL statement: If the input statement does not comply with the NAL syntax rules, the NARS processing exception may occur.
        - NARS internal error or exception: When processing input statements, an error or exception may occur inside NARS, causing the processing to fail.
        '''

        # NARS undefined -> auto initialize

        if not self._NARS:
            self.__init__()

        # start to handle

        taskList = []
        for line in lines.split('\n'):
            if len(line) == 0:
                continue

            taskLine = self.run_line(reasoner=self._NARS, line=line)
            self._inputHistory.append(line)
            if taskLine is not None:
                taskList.extend(taskLine)

        outs: list[NARSOutput] = []

        taskList: List[
            Tuple[
                List[Task], Task, Task,
                List[Task], Task,
                Tuple[Task, Task]
            ]
        ]
        for taskLine in taskList:
            (
                tasksDerived,
                judgementRevised,
                goalRevised,
                answersQuestion,
                answersQuest,
                (taskOperationReturn, taskExecuted)
            ) = taskLine
            for derivedTask in tasksDerived:
                outs.append(
                    NARSOutput(
                        PrintType.OUT, derivedTask.sentence.repr(), *derivedTask.budget)
                )

            if judgementRevised is not None:
                outs.append(NARSOutput(PrintType.OUT, judgementRevised.sentence.repr(
                ), *judgementRevised.budget))
            if goalRevised is not None:
                outs.append(NARSOutput(
                    PrintType.OUT, goalRevised.sentence.repr(), *goalRevised.budget))
            if answersQuestion is not None:
                for answer in answersQuestion:
                    outs.append(
                        NARSOutput(PrintType.ANSWER, answer.sentence.repr(), *answer.budget))
            if answersQuest is not None:
                for answer in answersQuest:
                    outs.append(NARSOutput(
                        PrintType.ANSWER, answersQuest.sentence.repr(), *answersQuest.budget))
            if taskExecuted is not None:
                outs.append(NARSOutput(
                    PrintType.EXE, f'{taskExecuted.term.repr()} = {str(taskOperationReturn) if taskOperationReturn is not None else None}'))

            # * print & event patch
            for out in outs:
                if out:
                    self.printOutput(type=out.type, content=out.content, p=out.p,
                                     d=out.d, q=out.q, comment_title=out.comment_title, end=out.end)
                # broadcast outputs before return
                self._handleNARSOutput(out=out)

        # return outputs
        return outs

    # run line
    def run_line(self, reasoner: reasoner, line: str):
        '''Run one line of input'''
        line = line.strip(' \r\n\t')  # ignore spaces
        # special notations
        if line.startswith("''"):  #
            if line.startswith("''outputMustContain('"):
                line = line[len("''outputMustContain('"):].rstrip("')\n")  #
                if len(line) == 0:  # no any content
                    return
                if (check := NAL_GrammarParse(line)):  # verify the input
                    self.printOutput(
                        PrintType.INFO, f'OutputContains({check.sentence.repr()})')
                else:
                    self.printOutput(
                        PrintType.ERROR, f'parse "{line}" failed!'
                    )
            return
        # empty or comments
        elif len(line) == 0 or line.startswith("//") or line.startswith("'"):
            return None
        # digit -> run cycle
        elif line.isdigit():
            nCycles = int(line)
            self.printOutput(PrintType.INFO, f'Run {nCycles} cycles.')
            tasksInCycles: list[Task] = []
            # Get all export statements run during this period, deep copy for backup
            for _ in range(nCycles):
                tasksCaught = reasoner.cycle()
                tasksInCycles.append(deepcopy(tasksCaught))
            return tasksInCycles
        # narsese
        else:
            line = line.rstrip(' \n')  # ignore spaces and newline
            if 1:
                success, task, _ = reasoner.input_narsese(line, go_cycle=False)
                if success:  # input success
                    self.printOutput(
                        PrintType.IN, task.sentence.repr(), *task.budget)
                else:  # input failed
                    self.printOutput(
                        PrintType.ERROR, f'Input "{line}" failed.')
                tasksCaught = reasoner.cycle()  # run cycles
                return [deepcopy(tasksCaught)]  # Returns a inferred statement


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
    interface: NARSInterface = NARSInterface.constructInterface()
    # enter console loop
    while True:
        interface.printOutput(
            PrintType.COMMENT, '', comment_title='Input', end='')
        lines = input()
        try:
            interface._handleLines(lines)
        except Exception as e:
            interface.printOutput(
                PrintType.ERROR, f'Errors when input {lines}\n{e}')


if __name__ == '__main__':
    Config.loadFromDict(DEFAULT_CONFIG)
    __main__()
