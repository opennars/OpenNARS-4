import functools
import re
from pynars.Interface import NAL_GrammarParse

from pynars.Interface import NARSInterface
from pynars.Interface import NARSOutput
from pynars.Interface import PrintType
from pynars.Interface import Reasoner
from pynars.Interface import printOut
printOutput = printOut


## Cmd system ##

# Preset cmd functions & decorators #

def checkExcept(handleFunc=None, formattedMessage=None):  # -> function
    '''Returns a decorator that handles the error/alarm in case of an error and returns a custom message'''
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except BaseException as e:
                if handleFunc:
                    # Return handled error (only one parameter e)
                    return handleFunc(e)
                print((formattedMessage if formattedMessage else '%s') %
                      str(e.with_traceback(None) if e else repr(e))
                      )
        return wrapper
    return decorator


def prefixBrowse(toBrowse: list[str], *keywords: list[str]) -> list[str]:
    '''Matches the content against the string prefix'''
    return [string  # returns cmd names
            # find matching cmds by: do not repeat
            for string in toBrowse
            # match the list of all cmds, as long as they match the search results - not necessarily in order
            if any(
                string.startswith(prefix)
                for prefix in keywords)]


def prefixCmdBrowse(cmdDict: dict[tuple:tuple], *keywords: list[str]) -> list[tuple[str]]:
    '''Matches the content against the string prefix'''
    return [aliasIndices  # returns cmd names
            # find matching cmds by: do not repeat
            for aliasIndices in cmdDict
            if any(
                any(
                    aliasIndex.startswith(keyword)
                    for aliasIndex in aliasIndices)
                for keyword in keywords)]  # match the list of all cmds, as long as they match the search results - not necessarily in order


def quickConvertCmdTypes(inp: list[str], type_N_default: list[tuple[type, any]]) -> list[str]:
    '''Constructs the parameter set of the final input cmd handler by specifying the type-default parameter list, combined with the input parameter list (using positional parameters)'''
    if type_N_default:
        result: list[any] = []
        lp = len(inp)
        for index in range(len(type_N_default)):  # if has default values
            paramType, defaultValue = type_N_default[index]
            # if input not provided, uses default values
            if index >= lp:
                result.append(defaultValue)
                continue
            # If the type is None, return itself and all subsequent arguments (compatible with any long arguments).
            if not paramType:
                result.extend(inp[index:])
                continue
            arg: str = inp[index]
            try:  # Use the types defined here to convert the string parameters
                result.append(paramType(arg))
            except:  # error -> use default value
                result.append(defaultValue)
                print(
                    f'Parsing error! Default values "{defaultValue}" have been used.')
        return result
    else:  # If not required (may be a "no input/only str array" case)
        return inp


# Common Cmds #
'''
Main functions of common cmd block:
1. Provide a set of preset cmds to simplify user interaction with the NARS system
2. Provide macro command function, allowing users to customize a set of commands and package them as macros, easy to repeat execution

The main functions of each function, and their respective types and roles of parameters and outputs:
1. waitAns try to get the result: try to capture the output of the specified type, and stop when it appears
- Parameter: paras (list[str]), which contains the output type, maximum tolerance, and interval cmd
- Output: list[NARSOutput], captured output of the specified type
2. toggleSilent switches silent mode: Switches the silent mode of the cmd, generally blocking NARSOutput information
- Parameter: args (list[str]). No parameter is required
- The output is None
3. readfile Read files: Call API to read files
- Parameter: args (list[str]), which contains the file path
- The output is None
4. printHistory Output history: Output user input history
- Parameter: args (list[str]), placeholder
- The output is None
5. exec execution command: Directly invoke Python's built-in exec command to execute a single line of code
- Parameter: args (list[str]), which contains the code to be executed
- The output is None
6. parse switch shorthand escape: Switch command "automatic shorthand parsing" function
- Parameter: args (list[str]). No parameter is required
- The output is None
7. help: Display the help document
- Parameter: args (list[str]), which contains specific commands
- The output is None

# Externally defined variable types, meanings and relationships:
1. PRE_CMD_ dict command index (dict) : Stores dictionaries of preset command functions. The key is the command name and the value is the corresponding function

# Main dependencies between functions:
1. waitAns attempt to obtain results relying on the NAL_GrammarParse.NARS statement input
2. toggleSilent switching silent mode depends on NAL_GrammarParse. Silent output and outPrint direct output
3. readfile reads files dependent on NAL_GrammarParse.exec to run files
4. printHistory output history depends on inputHistory input history and NAL_GrammarParse.cmdHistory cmd history
5. The exec command depends on Python's built-in exec command
6. parse toggle shorthand escape depends on parseNeedSlash escape requires slash and outPrint output directly
7. The help help depends on the PRE_CMD_ preset cmd index and the helpDoc single cmd
'''
PRESET_CMDS: dict[tuple:tuple] = {}


def cmdRegister(cmdName: str | tuple[str], *type_N_default: list[tuple[type, any]]):
    '''Decorator: Used to encapsulate cmds
    Automatically register cmds at function definition time through the specified Type - Default parameter list
    ! Encapsulated function becomes a "callable object"

    TODO Maybe can generalize cmd matching: return a function that can determine whether the "cmd name" matches; If it is a string, it is automatically encapsulated
    if isinstance(cmdName,str):
        cmdName = lambda cmdName: cmdName == cmdName
    '''
    # the cmd name can be multiple aliases, and only one time bracket can be left unwritten
    if isinstance(cmdName, str):
        cmdName = (cmdName,)  # automatically converts to tuples

    def decorator(func):
        # register
        global PRESET_CMDS
        PRESET_CMDS[cmdName] = (func, type_N_default, cmdName)
        '''
        Core format & Structure: {Name: (handler function, ordinal and default list)}
        ! Tuples can be used as indexes: fixed type
        '''

        # decorator: pass metadata (docstrings) to the decorated function
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            return func(*args, **kwargs)

        # manual synchronization name and documents: Directly modify
        decorated.__name__ = func.__name__
        decorated.__doc__ = func.__doc__

        # finish
        return decorated

    return decorator


@cmdRegister(('waitans', 'wait-answer', 'w-answer'), (str, 'ANSWER'), (int, 100), (None, '1'))
def waitAnswer(outType: str, maxListens: int, *cmdInInterval: str) -> list[NARSOutput]:
    '''Format: waitans [Output type = ANSWER] [Maximum tolerance = 100] [Interval cmd = '1']
    Attempts to capture output of a specified type and stops when it appears'''
    # Parameter preprocessing: Concatenates cmds separated by Spaces
    cmdInInterval: str = ' '.join(cmdInInterval)
    outType = PrintType.__getattribute__(PrintType, outType)
    outs: list[NARSOutput]
    while maxListens < 0 or (maxListens := maxListens-1):
        # Loop execute interval cmd (default is wait statement)
        outs = currentNARSInterface.inputNAL(cmdInInterval)
        for out in outs:
            if out and out.type == outType:
                currentNARSInterface.printOutput(
                    PrintType.INFO, f'Answer "{out.content}" is caught!')
                return out  # catch once


@cmdRegister(('waitres', 'wait-result', 'w-result'), (int, 100), (str, '1'), (None, ''))
def waitResult(maxListens: int, cmdInInterval: str, *targetSentence: list[str]) -> list[NARSOutput]:
    '''Format: waitres [Maximum tolerance = 100] [Interval cmd = '1'] [sentences...]
    Attempts to intercept output that matches the specified sentences (same NAL format) and stops when it appears'''
    from pynars.Narsese import parser
    # Parameter preprocessing ' '.join(str target statement)
    # handles subsequent cases where whitespace is split
    # (the change in the number of whitespace does not affect parsing for the time being)
    targetSentence: str = specialGrammarParse(' '.join(targetSentence))
    # Using special syntax +NAL parser, reconvert to NAL standard format
    targetSentence: str = parser.parse(targetSentence).sentence.repr()
    # starting wait
    outs: list[NARSOutput]
    while maxListens < 0 or (maxListens := maxListens-1):
        # Loop execute interval cmd (default is wait statement)
        outs = currentNARSInterface.inputNAL(cmdInInterval)
        for out in outs:
            # compare with the statement's repr, 'task.sentence.repr()'
            if out and out.content == targetSentence:
                currentNARSInterface.printOutput(
                    PrintType.INFO, f'Target sentence "{targetSentence}" is caught!')
                return out  # caught once
    currentNARSInterface.printOutput(
        PrintType.INFO, f'Target sentence "{targetSentence}" is not caught!')


@cmdRegister(('toggle-silent', 'silent'))
def toggleSilent() -> None:
    '''Switching the silent mode of the cmd generally prevents NARSOutput messages'''
    currentNARSInterface.silentOutput = not currentNARSInterface.silentOutput
    currentNARSInterface.printOutput(
        type=PrintType.INFO, content=f'''Silent output {
            "opened"
            if currentNARSInterface.silentOutput
            else "closed"
        }.''')


@cmdRegister(('toggle-color', 'color'))
def toggleColor() -> None:
    '''Toggle the color display of cmds (for terminals that do not support custom foreground/background colors)'''
    NARSInterface.showColor = not currentNARSInterface.showColor
    currentNARSInterface.printOutput(
        type=PrintType.INFO, content=f'''Color showing {
            "opened"
            if currentNARSInterface.showColor
            else "closed"
        }.''')


@cmdRegister('readfile', 'read-file')
def readfile(*args: list[str]) -> None:
    '''Format: readfile [... file path]
    Call API to read file'''
    for path in args:
        currentNARSInterface.executeFile(path)


@cmdRegister('history')
def printHistory(*args: list[str]) -> None:
    '''Format: history [... placeholder]
    Output the user's input history
    Default: The Narsese seen at the bottom of the system, not the actual input
    User actual input cmd: input any parameters can be obtained'''
    global _inputHistory
    print('\n'.join(_inputHistory if args else currentNARSInterface.inputHistory))


@cmdRegister(('execute', 'exec'))
def execCode(*args: list[str]) -> None:
    '''Format: exec <Python code >
    Directly invoke Python's built-in exec cmd to execute a single line of code'''
    exec(' '.join(args))


@cmdRegister(('execute', 'exec'))
def execCode(*args: list[str]) -> None:
    '''Format: eval <Python code >
    Directly invoke Python's built-in eval cmd to evaluate a single line of code'''
    print(f'eval result: {eval(" ".join(args))}')


@cmdRegister(('simplify-parse', 'parse'))
def toggleSimplifyParse() -> None:
    '''Toggle the "automatic shorthand parsing" function of the cmd (enabled by default),
    If so, the Narsese input are automatically parsed in a simplified format'''
    global _parseNeedSlash
    _parseNeedSlash = not _parseNeedSlash
    print(
        f'Narsese automatic analytic simplification {"closed" if _parseNeedSlash else "opened"}.')


@cmdRegister('help')
def help(*keywords: list[str], searchIn: dict[tuple:tuple] = PRESET_CMDS) -> None:
    '''Format: help [... specific cmd]
    Display this help document, or assist in retrieving help for additional cmds'''
    # Core idea: Empty prefix = all cmds
    keywords = keywords if keywords else ['']
    # find a matching cmd name
    cmdNameAliases: list[tuple(str)] = prefixCmdBrowse(searchIn, *keywords)
    # display "matching cmds" as follows
    if cmdNameAliases:
        # match the list of all cmds, as long as they match the search results - not necessarily in order
        for cmdNameAlias in cmdNameAliases:
            # Structure: {Name: (handler, ordinal and default list)}
            cmdFunction = searchIn[cmdNameAlias][0]
            print(
                f'''<{"/".join(cmdNameAlias)}>: {cmdFunction.__name__}\n{
                    cmdFunction.__doc__ 
                    if cmdFunction.__doc__ 
                    else "!!! This cmd don't have any description !!!"
                    }\n''')
        return
    print(f'No commends is browsed by "{", ".join(keywords)}"!')


# Macro functions #
'''Macro cmd function module

# Main functions:
# 1. Define, query, execute, and repeat macros
A macro is a pre-defined set of cmds that can be executed with a simple macro name

# The main functions of each function, and their respective types and roles of parameters and outputs:
# 1. macroDef Define macrodef: Define a macro that contains a set of predefined cmds
# - Parameter: args (list[str]), which contains the macro name and the number of cmds
# - Output: None
# 2. macroQuery Query macros: Query defined macros and display their internal commands
# - Argument: args (list[str]), which contains the macro name
# - Output: None
# 3. macroExec executes macros by name: Executes macros by name
# - Argument: args (list[str]), which contains the macro name
# - Output: None
# 4. macroRepeat: Repeat the execution of macros by name and number
# - Parameter: args (list[str]), which contains the macro name and the number of executions
# - Output: None

# Externally defined variable types, meanings and relationships:
# 1.storedMacros Stored macros (dict) : Stores defined macros. The key is the name of the macro, and the value is the corresponding cmd list

# Main dependencies between functions:
# 1. macroDef defines macros that rely on execInput to execute input
# 2. macroQuery query macros rely on show to display individual macros
# 3. macroExec executes macros on a per-macro basis depending on execMacroSin
# 4. macroRepeat execution of macros depends on execMacroSin to execute a single macro
# 5.help The help depends on a single helpDoc cmd
# 6. readfile reads files dependent on NAL_GrammarParse.executeFile
# 7. ToggleSilent switch silent mode depends on the NAL_GrammarParse. SilentOutput
# 8.printHistory output history depends on inputHistory input history and NAL_GrammarParse.cmdHistory cmd history
# 9.exec exec relies on Python's built-in exec directive
parse toggle shorthand escape depends on parseNeedSlash escape requires slash
# 11. The helpDoc individual cmd depends on the index of PRESET_CMDS
'''

storedMacros: dict[str:list[str]] = {}


@cmdRegister(('macro-def', 'm-def'))
def macroDef(name: str, numCmds: int) -> None:
    '''Format: macro-def < macro name > < Number of cmds >
    According to the number of subsequent input cmds, 
    input a specified line of cmds, you can define an "cmd series" i.e. macro'''
    # input
    cmdList: list[str]
    if numCmds:  # limited cmd count
        cmdList = [
            input(f'Please input cmd #{i+1}: ')
            for i in range(numCmds)]
    else:  # unlimited cmd count
        cmdList = []
        while (cmd := input(f'Please input cmd #{len(cmdList)+1}: ')):
            cmdList.append(cmd)
    storedMacros[name] = cmdList
    # notify
    print(f'Macro {name} with {len(cmdList)}cmds input completed!')
    print("The following is cmds in it:\n"+'\n'.join(cmdList))


def showMacro(name: str): return f'Macro {name}: \n' + \
    '\n'.join(storedMacros[name])


@cmdRegister(('macro-query', 'm-query'))
def macroQuery(*args: list[str]) -> None:
    '''Format: macro-query [... macro name]
    With parameters: Find macros by name and display their internal commands (the number can be stacked indefinitely)
    No arguments: Lists all defined macros and displays their internal commands'''
    if args:  # find by names
        for name in args:
            if name in storedMacros:
                showMacro(name=name)
            else:
                print(f'Unknown macro name "{name}"')
    else:  # lists all defined macros
        for name in storedMacros:
            showMacro(name=name)


def macroExec1(name: str) -> None:
    '''Execute 1 macro'''
    cmds: list[str] = storedMacros[name]
    for cmd in cmds:
        execInput(cmd)


@cmdRegister(('macro-exec', 'm-exec'))
def macroExec(*args: list[str]) -> None:
    '''Format: macro-exec [... macro name]
    Execute macros by name (unlimited number can be stacked)
    If empty, execute macro "" (empty string)'''
    args = args if args else ['']
    for name in args:
        macroExec1(name=name)


@cmdRegister(('macro-repeat', 'm-repeat'))
def macroRepeat(name: str, numExecutes: int) -> None:
    '''Format: macro-repeat < macro name > < execution times >
    Execute macros as "name + number" (number can be stacked indefinitely)'''
    for _ in range(numExecutes):
        macroExec1(name=name)

# Reasoner management #


currentNARSInterface: NARSInterface = NARSInterface.constructInterface(
    137,
    500, 500,
    silent=False)

reasoners: dict[str:Reasoner] = {'initial': currentNARSInterface}


def getCurrentReasonerName() -> str:
    global currentNARSInterface
    for name in reasoners:
        if reasoners[name] is currentNARSInterface:
            return name
    return None


@cmdRegister(('reasoner-current', 'r-current'))
def reasonerCurrent() -> None:
    '''Gets the name of the current reasoner'''
    name = getCurrentReasonerName()
    if name != None:
        print(f'The name of the current reasoner is "{name}".')


@cmdRegister(('reasoner-list', 'r-list'))
def reasonerList(*keywords: list[str]) -> None:
    '''Format: reasoner-list [... specific cmd]
    Enumerate existing reasoners; It can be retrieved with parameters'''
    keywords = keywords if keywords else ['']
    # Search for a matching interface name
    reasonerNames: list[str] = prefixBrowse(reasoners, *keywords)
    # Displays information about "matched interface"
    if reasonerNames:
        for name in reasonerNames:  # match the list of all cmds, as long as they match the search results - not necessarily in order
            interface: NARSInterface = reasoners[name]
            information: str = '\n\t'+"\n\t".join(f"{name}: {repr(inf)}" for name, inf in [
                ('Memory', interface.reasoner.memory),
                ('Channels', interface.reasoner.channels),
                ('Overall Experience', interface.reasoner.overall_experience),
                ('Internal Experience', interface.reasoner.internal_experience),
                ('Sequence Buffer', interface.reasoner.sequence_buffer),
                ('Operations Buffer', interface.reasoner.operations_buffer),
            ])
            print(f'<{name}>: {information}')
        return
    print(f'No reasoner is browsed by "{", ".join(keywords)}"')


@cmdRegister(('reasoner-new', 'r-new'),
             (str, 'unnamed'),
             (int, 100),
             (int, 100),
             (bool, False),)
def reasonerNew(name: str, n_memory: int = 100, capacity: int = 100, silent: bool = False) -> NARSInterface:
    '''Format: reasoner-new < Name > [Memory capacity] [buffer size] [Silent output]
    Create a new reasoner and go to the existing reasoner if it exists
    If an empty name is encountered, the default name is "unnamed"'''
    global currentNARSInterface
    if name in reasoners:
        print(
            f'The reasoner exists! Now automatically go to the reasoner "{name}"!')
        return (currentNARSInterface := reasoners[name])

    reasoners[name] = (currentNARSInterface := NARSInterface.constructInterface(
        memory=n_memory,
        capacity=capacity,
        silent=silent
    ))
    print(
        f'A reasoner named "{name}" with memory capacity {n_memory}, buffer capacity {capacity}, silent output {" on " if silent else" off "} has been created!')
    return currentNARSInterface


@cmdRegister(('reasoner-goto', 'r-goto'), (str, 'initial'))
def reasonerGoto(name: str) -> NARSInterface:
    '''Format: reasoner-goto < name >
    Transfers the current reasoner of the program to the specified reasoner'''
    global currentNARSInterface
    if name in reasoners:
        print(f"Gone to reasoner named '{name}'!")
        return (currentNARSInterface := reasoners[name])
    print(f"There is no reasoner named '{name}'!")


@cmdRegister(('reasoner-delete', 'r-delete'))
def reasonerDelete(name: str) -> None:
    '''Format: reasoner-select < name >
    Deletes the reasoner with the specified name, but cannot delete the current reasoner'''
    global currentNARSInterface
    if name in reasoners:
        if reasoners[name] is currentNARSInterface:
            print(
                f'Unable to delete reasoner "{name}", it is the current reasoner!')
            return
        del reasoners[name]
        print(f'the reasoner named "{name}" has been deleted!')
        return
    print(f'There is no reasoner named "{name}"!')


@cmdRegister(('seed-set', 'seed'), (int, 137))
def randomSeed(seed: int) -> None:
    '''Format: seed [seed: integer]
    Set the random seed of the random number generator random and numpy.random'''
    NARSInterface.changeRandomSeed(seed=seed)


# Total index and other variables #

_parseNeedSlash: bool = False

_inputHistory: list[str] = []

# Special grammar parser #

# regular expressions: predefined as constants
PUNCT_INDEX: re.Pattern = re.compile(r'([^0-9%]\.)|[\?\!\@]')


def specialGrammarParse(inp: str) -> str:
    '''
    Additional syntax parsing for non-cmd input
    Main functions:
    This function is mainly used for special syntax parsing of non-cmd input, and converts the simplified input format into standard NAS statements.

    Types of parameters and outputs and their effects:
    - input (str): indicates the input string. It is a NAS statement that requires special syntax parsing.
    - Output (str): parsed standard NAS statement.

    Internal variable types, meanings and mutual relations:
    - l "Punctuation index" (str): A regular expression used to find punctuation marks in the input string.
    - ml "Punctuation search sequence" (list): Stores the position information of the matched punctuation marks in the input string.
    - ind "Last punctuation" (int): The position of the last punctuation in the input string.

    Main operation process:
    1. Check whether the input string is empty or starts with single quotation marks. If yes, the input string is directly returned.
    2. Use regular expressions to find punctuation marks in the input string and obtain the position of the last punctuation mark.
    3. Determine whether there are Angle brackets before the last punctuation mark. If not, add Angle brackets before the last punctuation mark.
    4. Return the parsed standard NAS statement.

    Possible exceptions:
    - Regular expression matching failure: When searching for punctuation marks in the input string, a regular expression matching failure may occur.
    TODO known BUG: incorrect parsing of "correct NARS syntax"
    When you enter "A-->E.%1.000;0.810%", the following truth value is removed
    For example, the statement "(--,<{left_wall} --> [on]>). :|:" is "automatically misunderstood".
    '''
    # handle comments/empty cmds

    if not inp or inp[0] == "'":
        return inp

    # First "normal parsing NAL", then do special syntax parsing, special language → Standard Naz
    # If can't "normal parsing", enter the following "special syntax"
    if NAL_GrammarParse(inp):
        return inp

    # complete the outermost parenthesis of the statement
    global PUNCT_INDEX
    ml: list = list(PUNCT_INDEX.finditer(inp))
    if ml:
        ind = ml[-1].span()[1]-1
        if inp[ind-1] != '>':  # TODO: There is an identification error
            # < incomplete sentence > Punctuate other parts
            inp = f'<{inp[:ind]}>{inp[ind]}{inp[ind+1:]}'
    return inp


def execInput(inp: str, *otherInput: list[str]) -> None:
    '''
    Main functions:
    This code is mainly used to process the user input cmds and NAS statements, and perform the corresponding operations according to the input content.

    The types, meanings and relationships of each variable:
    - in "input" (str): A string entered by the user, which may be an cmd or a Nax statement.
    - cmdHistory "Cmd history" (list[str]): Stores the cmd history entered by the user.
    - parseNeedSlash "Escape requires slash" (bool): Indicates whether slashes are required for short escape.
    - PRESET_CMDS (dict): Index list of preset cmds, used to execute functions based on cmd names.

    Main operation process:
    1. Wait for user input.
    2. Check whether the input is an cmd. If yes, execute the corresponding preset cmd function.
    3. If the input is not a command, determine whether special parsing is required according to the slash required for parseNeedSlash escape.
    4. Inject parsed NAS statements into the NARS interface.

    Possible exceptions:
    - Input execution failure: An exception may occur when an cmd or NAS statement entered by the user is executed. The exception is caught and the exception information is output。
    '''

    # multiline cmd disassembly

    if len(otherInput) > 0:
        execInput(inp=inp)
        for i in otherInput:
            execInput(i)
        return

    # add to history

    _inputHistory.append(inp)

    # pre-jump cmd
    if inp.startswith('/'):
        # the first word is the cmd name, and the following are parameters
        words: list[str] = inp[1:].split()
        if words:  # if not empty
            cmdName: str = words[0].lower()  # case insensitive
            autoExecuteCmdByName(cmdName, words[1:])
        return  # If it's executed as a command, it won't execute as Narsese input

    # Narsese parsing
    hasSlash = False  # usage of backslashes: Enforce/disable "parse simplification"
    if not _parseNeedSlash or (hasSlash := inp.startswith('\\')):
        if hasSlash:  # Remove the slash if there is a backslash
            inp = inp[1:]
        inp = specialGrammarParse(inp=inp)

    # input NAL
    currentNARSInterface.inputNAL(inp)


def autoExecuteCmdByName(cmdName: str, words: list[str], cmdDict: dict[tuple:tuple] = PRESET_CMDS) -> bool:
    '''Execute cmd by name with autocompletion
    returns: whether a cmd is chosen and executed successfully'''
    # auto browse & complete
    nameAliasHints: list[tuple[str]] = prefixCmdBrowse(cmdDict, cmdName)
    # if it have a precise match, directly use it
    for i in range(len(nameAliasHints)):
        nameAliases = nameAliasHints[i]
        if any(nameAlias == cmdName for nameAlias in nameAliases):
            nameAliasHints = [nameAliases]
            break
    # Only option: Full match or auto complete
    if len(nameAliasHints) == 1:
        # auto complete
        if not cmdName in nameAliasHints[0]:
            print(
                f'Autocompleted cmd to "{"/".join(nameAliasHints[0])}".')
        nameAliasIndex = nameAliasHints[0]
        # Cmd execution: Automatically adjust the "parameter requirements" of specific cmds and intercept parameters
        cmdData = cmdDict[nameAliasIndex]
        cmdHandler = cmdData[0]
        type_N_default: list[tuple[type, any]] = (
            cmdData[1]
            if len(cmdData) > 1 else None)
        params: list = quickConvertCmdTypes(words[1:], type_N_default)
        try:
            # in the form of positional arguments, to the appropriate handler. Structure: {Name: (handler, ordinal and default list)}
            cmdHandler(*params)
            return True
        except BaseException as e:
            print('Cmd execute failed: ',
                  e.with_traceback(None) if e else e)
            return False
    else:
        hint = 'Are you looking for "' + \
            "\"|\"".join('/'.join(alias) for alias in nameAliasHints) + \
            '"?' if nameAliasHints else ''
        print(f'Unknown cmd {cmdName}. {hint}')
        return False

# @checkExcept error alarm (message formatted message =' Input execution failed: %s')
# TODO fix "TypeError: checkExcept error alarm..decorator decorator () missing 1 required positional argument: 'func'"


def __main__():
    # enter preset format prompt "IN", not regards `silent`
    printOutput(PrintType.COMMENT, '', comment_title='Input', end='')

    # get & execute
    inp: str = input()
    execInput(inp=inp)


## main program ##
if __name__ == '__main__':
    while 1:
        __main__()
