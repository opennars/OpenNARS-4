from typing import List, Dict, Tuple, Union, Iterable
import functools
import re
from pynars.Interface import narsese_parse_safe
from pynars.Narsese import Term,Task
from pynars.NARS.DataStructures import Memory

from pynars.Interface import NARSInterface,NARSOutput,PrintType,Reasoner,print_out_origin
print_output = print_out_origin

# compatible type annotation


## Cmd system ##

# Preset cmd functions & decorators #


def check_except(handler=None, formatted_message=None):  # -> function
    '''Returns a decorator that handles the error/alarm in case of an error and returns a custom message'''
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except BaseException as e:
                if handler:
                    # Return handled error (only one parameter e)
                    return handler(e)
                print((formatted_message if formatted_message else '%s') %
                      str(e.with_traceback(None) if e else repr(e))
                      )
        return wrapper
    return decorator


def prefix_browse(to_browse: List[str], *keywords: List[str]) -> List[str]:
    '''Matches the content against the string prefix'''
    return [string  # returns cmd names
            # find matching cmds by: do not repeat
            for string in to_browse
            # match the list of all cmds, as long as they match the search results - not necessarily in order
            if any(
                string.startswith(prefix)
                for prefix in keywords)]


def prefix_cmd_browse(cmd_dict: Dict[tuple, tuple], *keywords: List[str]) -> List[Tuple[str]]:
    '''Matches the content against the string prefix'''
    return [alias_indices  # returns cmd names
            # find matching cmds by: do not repeat
            for alias_indices in cmd_dict
            if any(
                any(
                    alias_index.startswith(keyword)
                    for alias_index in alias_indices)
                for keyword in keywords)]  # match the list of all cmds, as long as they match the search results - not necessarily in order


def quick_convert_cmd_types(inp: List[str], type_N_default: List[Tuple[type, any]]) -> List[str]:
    '''Constructs the parameter set of the final input cmd handler by specifying the type-default parameter list, combined with the input parameter list (using positional parameters)'''
    if type_N_default:
        result: List[any] = []
        lp = len(inp)
        for index in range(len(type_N_default)):  # if has default values
            param_type, default_value = type_N_default[index]
            # if input not provided, uses default values
            if index >= lp:
                result.append(default_value)
                continue
            # If the type is None, return itself and all subsequent arguments (compatible with any long arguments).
            if not param_type:
                result.extend(inp[index:])
                continue
            arg: str = inp[index]
            try:  # Use the types defined here to convert the string parameters
                result.append(param_type(arg))
            except:  # error -> use default value
                result.append(default_value)
                print(
                    f'Parsing error! Default values "{default_value}" have been used.')
        return result
    else:  # If not required (may be a "no input/only str array" case)
        return inp


# Common Cmds #
'''
Main functions of common cmd block:
1. Provide a set of preset cmds to simplify user interaction with the NARS system
2. Provide macro command function, allowing users to customize a set of commands and package them as macros, easy to repeat execution

The main functions of each function, and their respective types and roles of parameters and outputs:
1. wait_ans try to get the result: try to capture the output of the specified type, and stop when it appears
- Parameter: paras (List[str]), which contains the output type, maximum tolerance, and interval cmd
- Output: List[NARSOutput], captured output of the specified type
2. toggle_silent switches silent mode: Switches the silent mode of the cmd, generally blocking NARSOutput information
- Parameter: args (List[str]). No parameter is required
- The output is None
3. readfile Read files: Call API to read files
- Parameter: args (List[str]), which contains the file path
- The output is None
4. print_history Output history: Output user input history
- Parameter: args (List[str]), placeholder
- The output is None
5. exec execution command: Directly invoke Python's built-in exec command to execute a single line of code
- Parameter: args (List[str]), which contains the code to be executed
- The output is None
6. parse switch shorthand escape: Switch command "automatic shorthand parsing" function
- Parameter: args (List[str]). No parameter is required
- The output is None
7. help: Display the help document
- Parameter: args (List[str]), which contains specific commands
- The output is None

# Externally defined variable types, meanings and relationships:
1. PRE_CMD_ dict command index (dict) : Stores dictionaries of preset command functions. The key is the command name and the value is the corresponding function

# Main dependencies between functions:
1. wait_ans attempt to obtain results relying on the NAL_GrammarParse.NARS statement input
2. toggle_silent switching silent mode depends on NAL_GrammarParse. Silent output and out_print direct output
3. readfile reads files dependent on NAL_GrammarParse.exec to run files
4. print_history output history depends on input_history input history and NAL_GrammarParse.cmdHistory cmd history
5. The exec command depends on Python's built-in exec command
6. parse toggle shorthand escape depends on parse_needSlash escape requires slash and out_print output directly
7. The help help depends on the PRE_CMD_PRESET cmd index and the helpDoc single cmd
'''
PRESET_CMDS: Dict[tuple, tuple] = {}


def cmd_register(cmd_name: Union[str, Tuple[str]], *type_N_default: List[Tuple[type, any]]):
    '''Decorator: Used to encapsulate cmds
    Automatically register cmds at function definition time through the specified Type - Default parameter list
    ! Encapsulated function becomes a "callable object"

    TODO Maybe can generalize cmd matching: return a function that can determine whether the "cmd name" matches; If it is a string, it is automatically encapsulated
    if isinstance(cmd_name,str):
        cmd_name = lambda cmd_name: cmd_name == cmd_name
    '''
    # the cmd name can be multiple aliases, and only one time bracket can be left unwritten
    if isinstance(cmd_name, str):
        cmd_name = (cmd_name,)  # automatically converts to tuples

    def decorator(func):
        # register
        global PRESET_CMDS
        PRESET_CMDS[cmd_name] = (func, type_N_default, cmd_name)
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


@cmd_register(('waitans', 'wait-answer', 'w-answer'), (str, 'ANSWER'), (int, 100), (None, '1'))
def wait_answer(out_type: str, max_listens: int, *cmd_in_interval: str) -> List[NARSOutput]:
    '''Format: waitans [Output type = ANSWER] [Maximum tolerance = 100] [Interval cmd = '1']
    Attempts to capture output of a specified type and stops when it appears'''
    # Parameter preprocessing: Concatenates cmds separated by Spaces
    cmd_in_interval: str = ' '.join(cmd_in_interval)
    out_type = PrintType.__getattribute__(PrintType, out_type)
    outs: List[NARSOutput]
    while max_listens < 0 or (max_listens := max_listens-1):
        # Loop execute interval cmd (default is wait statement)
        outs = current_NARS_interface.input_narsese(cmd_in_interval)
        for out in outs:
            if out and out.type == out_type:
                current_NARS_interface.print_output(
                    PrintType.INFO, f'Answer "{out.content}" is caught!')
                return out  # catch once


@cmd_register(('waitres', 'wait-result', 'w-result'), (int, 100), (str, '1'), (None, ''))
def wait_result(max_listens: int, cmd_in_interval: str, *target_sentences: List[str]) -> List[NARSOutput]:
    '''Format: waitres [Maximum tolerance = 100] [Interval cmd = '1'] [*sentences]
    Attempts to intercept output that matches the specified sentences (same NAL format) and stops when it appears'''
    from pynars.Narsese import parser
    # Parameter preprocessing ' '.join(str target statement)
    # handles subsequent cases where whitespace is split
    # (the change in the number of whitespace does not affect parsing for the time being)
    target_sentences: str = special_narsese_parse(' '.join(target_sentences))
    # Using special syntax +NAL parser, reconvert to NAL standard format
    target_sentences: str = parser.parse(target_sentences).sentence.repr()
    # starting wait
    outs: List[NARSOutput]
    while max_listens < 0 or (max_listens := max_listens-1):
        # Loop execute interval cmd (default is wait statement)
        outs = current_NARS_interface.input_narsese(cmd_in_interval)
        for out in outs:
            # compare with the statement's repr, 'task.sentence.repr()'
            if out and out.content == target_sentences:
                current_NARS_interface.print_output(
                    PrintType.INFO, f'Target sentence "{target_sentences}" is caught!')
                return out  # caught once
    current_NARS_interface.print_output(
        PrintType.INFO, f'Target sentence "{target_sentences}" is not caught!')


@cmd_register(('toggle-silent', 'silent'))
def toggle_silent() -> None:
    '''Switching the silent mode of the cmd generally prevents NARSOutput messages'''
    current_NARS_interface.silent_output = not current_NARS_interface.silent_output
    current_NARS_interface.print_output(
        type=PrintType.INFO, content=f'''Silent output {
            "opened"
            if current_NARS_interface.silent_output
            else "closed"
        }.''')


@cmd_register(('volume'), (int, 100))
def volume(vol:int) -> None:
    '''Format: volume [volume:int 0~100]
    Set the Output Volume of the console to control its output (same as OpenNARS)'''
    if 0 <= vol <= 100:
        current_NARS_interface.volume_threshold = 1 - vol * 0.01 # same as `(100-vol)/100`
        current_NARS_interface.print_output(
            type=PrintType.INFO, content=f'''Volume is set to "*volume={vol}".''')
    else:
        current_NARS_interface.print_output(
            type=PrintType.INFO, content=f'''Volume {vol} is out of range 0~100!''')


@cmd_register(('toggle-color', 'color'))
def toggle_color() -> None:
    '''Toggle the color display of cmds (for terminals that do not support custom foreground/background colors)'''
    NARSInterface.show_color = not current_NARS_interface.show_color
    current_NARS_interface.print_output(
        type=PrintType.INFO, content=f'''Color showing {
            "opened"
            if current_NARS_interface.show_color
            else "closed"
        }.''')


@cmd_register('readfile', 'read-file')
def read_file(*args: List[str]) -> None:
    '''Format: readfile [*file_paths]
    Call API to read file'''
    for path in args:
        current_NARS_interface.execute_file(path)


@cmd_register(('history', 'history-input'))
def print_history_in(*args: List[str]) -> None:
    '''Format: history [*placeholder]
    Output the user's input history
    Default: The Narsese seen at the bottom of the system, not the actual input
    User actual input cmd: input any parameters can be obtained'''
    global input_history
    print('\n'.join(input_history if args else current_NARS_interface.input_history))


@cmd_register('history-output')
def print_history_out(*args: List[str]) -> None:
    '''Format: history-output [*placeholder]
    Output the console's output history
    Default: The Narsese seen at the bottom of the system, not the actual input
    User actual input cmd: input any parameters can be obtained'''
    global output_history
    for (interface_name, output_type, content) in output_history:
        print(f'{interface_name}: [{output_type}]\t{content}')


@cmd_register(('execute', 'exec'))
def exec_code(*args: List[str]) -> None:
    '''Format: exec <Python code >
    Directly invoke Python's built-in exec cmd to execute a single line of code'''
    code = " ".join(args)
    print(f'[exec]{code}')
    try:
        exec(code)
    except BaseException as e:
        print(f'exec failed: {e}')


@cmd_register(('evaluate', 'eval'))
def eval_code(*args: List[str]) -> None:
    '''Format: eval <Python code >
    Directly invoke Python's built-in eval cmd to evaluate a single line of code'''
    code = " ".join(args)
    print(f'[eval]{code}')
    try:
        print(f'eval result: {eval(code)}')
    except BaseException as e:
        print(f'eval failed: {e}')


@cmd_register(('operator', 'operator-list', 'o-list'))
def operator_list(*keywords: List[str]) -> None:
    '''Format: operator-list [*keywords]
    Enumerate existing operators; It can be retrieved with parameters'''
    keywords = keywords if keywords else ['']
    # Search for a matching interface name
    from pynars.NARS.Operation.Register import registered_operators, get_registered_operator_by_name, registered_operator_names
    operator_names: List[str] = prefix_browse(registered_operator_names(), *keywords)
    # Displays information about "matched interface"
    if operator_names:
        for name in operator_names:  # match the list of all cmds, as long as they match the search results - not necessarily in order
            op = get_registered_operator_by_name(name)
            f = registered_operators[op]
            print(f'''<Operator {str(op)}>: {
                'No function' if f == None else
                'No description' if f.__doc__.strip() == '' else
                f.__doc__}''')
        return
    print(f'No Operator is browsed by "{", ".join(keywords)}"')


@cmd_register(('register-operator', 'operator-register', 'o-register', 'register'))
def operator_register(*args: List[str]) -> None:
    '''Format: register-operator <Operator(Term) Name> [<'eval'/'exec'> <Python Code>]
    Register an operator to NARS interface.
    
    function signature:
        execution_F(arguments: Iterable[Term], task: Task=None, memory: Memory=None) -> Union[Task,None]
    
    default fallback of execution_F when only 1 argument is provided:
        print(f'executed: arguments={arguments}, task={task}, memory={memory}. the "task" will be returned')
    
    ! Unsupported: register mental operators
    '''
    name = args[0]
    "The operator's name without `^` as prefix"
    if len(args) == 1:
        def execution_F(arguments: Iterable[Term], task: Task=None, memory: Memory=None) -> Union[Task,None]:
            print(f'executed: arguments={arguments}, task={task}, memory={memory}. the "task" will be returned')
            return task
        execution_F.__doc__ = f'''
            The execution is auto generated from operator with name={name} without code
            '''.strip()
    else:
        eType = args[1]
        code = " ".join(args[2:])
        if eType =='exec':
            def execution_F(arguments: Iterable[Term], task: Task=None, memory: Memory=None) -> Union[Task,None]:
                return exec(code)
        else:
            def execution_F(arguments: Iterable[Term], task: Task=None, memory: Memory=None) -> Union[Task,None]:
                return eval(code)
        execution_F.__doc__ = f'''
            The execution is auto generated from operator with name={name} in {eType} mode with code={code}
            '''.strip()
    if (op:=current_NARS_interface.reasoner.register_operator(name, execution_F)) is not None:
        print(f'Operator {str(op)} was successfully registered ' + (
            'without code'
            if len(args) == 1
            else f'in mode "{eType}" with code={code}'))
    else:
        print(f'The operator with name="{name}" was already registered!')


@cmd_register(('simplify-parse', 'parse'))
def toggle_simplify_parse() -> None:
    '''Toggle the "automatic shorthand parsing" function of the cmd (enabled by default),
    If so, the Narsese input are automatically parsed in a simplified format'''
    global _parse_simplification
    _parse_simplification = not _parse_simplification
    print(
        f'Narsese automatic analytic simplification {"closed" if _parse_simplification else "opened"}.')


@cmd_register('help')
def help(*keywords: List[str], search_in: Dict[tuple, tuple] = PRESET_CMDS) -> None:
    '''Format: help [*keywords]
    Display this help document, or assist in retrieving help for additional cmds'''
    # Core idea: Empty prefix = all cmds
    keywords = keywords if keywords else ['']
    # find a matching cmd name
    cmd_name_aliases: List[tuple(str)] = prefix_cmd_browse(
        search_in, *keywords)
    # display "matching cmds" as follows
    if cmd_name_aliases:
        # match the list of all cmds, as long as they match the search results - not necessarily in order
        for cmd_name_alias in cmd_name_aliases:
            # Structure: {Name: (handler, ordinal and default list)}
            cmd_function = search_in[cmd_name_alias][0]
            print(
                f'''<{"/".join(cmd_name_alias)}>: {cmd_function.__name__}\n{
                    cmd_function.__doc__ 
                    if cmd_function.__doc__ 
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
# 1. macro_def Define macros: Define a macro that contains a set of predefined cmds
# - Parameter: args (List[str]), which contains the macro name and the number of cmds
# - Output: None
# 2. macro_query Query macros: Query defined macros and display their internal commands
# - Argument: args (List[str]), which contains the macro name
# - Output: None
# 3. macro_exec executes macros by name: Executes macros by name
# - Argument: args (List[str]), which contains the macro name
# - Output: None
# 4. macro_repeat: Repeat the execution of macros by name and number
# - Parameter: args (List[str]), which contains the macro name and the number of executions
# - Output: None

# Externally defined variable types, meanings and relationships:
# 1.stored_macros Stored macros (dict) : Stores defined macros. The key is the name of the macro, and the value is the corresponding cmd list

# Main dependencies between functions:
# 1. macro_def defines macros that rely on exec_input to execute input
# 2. macro_query query macros rely on show to display individual macros
# 3. macro_exec executes macros on a per-macro basis depending on exec_macro_sin
# 4. macro_repeat execution of macros depends on exec_macro_sin to execute a single macro
# 5.help The help depends on a single help_doc cmd
# 6. readfile reads files dependent on NAL_GrammarParse.executeFile
# 7. Toggle_silent switch silent mode depends on the NAL_GrammarParse. Silent_output
# 8.print_history output history depends on input_history input history and NAL_GrammarParse.cmdHistory cmd history
# 9.exec exec relies on Python's built-in exec directive
parse toggle shorthand escape depends on parse_need_slash escape requires slash
# 11. The help_doc individual cmd depends on the index of PRESET_CMDS
'''

stored_macros: Dict[str, List[str]] = {}


@cmd_register(('macro-def', 'm-def'))
def macro_def(name: str, num_cmds: int) -> None:
    '''Format: macro-def < macro name > < Number of cmds >
    According to the number of subsequent input cmds, 
    input a specified line of cmds, you can define an "cmd series" i.e. macro'''
    # input
    cmd_list: List[str]
    if num_cmds:  # limited cmd count
        cmd_list = [
            input(f'Please input cmd #{i+1}: ')
            for i in range(num_cmds)]
    else:  # unlimited cmd count
        cmd_list = []
        while (cmd := input(f'Please input cmd #{len(cmd_list)+1}: ')):
            cmd_list.append(cmd)
    stored_macros[name] = cmd_list
    # notify
    print(f'Macro {name} with {len(cmd_list)}cmds input completed!')
    print("The following is cmds in it:\n"+'\n'.join(cmd_list))


def macro_show(name: str): return f'Macro {name}: \n' + \
    '\n'.join(stored_macros[name])


@cmd_register(('macro-query', 'm-query'))
def macro_query(*args: List[str]) -> None:
    '''Format: macro-query [*keywords]
    With parameters: Find macros by name and display their internal commands (the number can be stacked indefinitely)
    No arguments: Lists all defined macros and displays their internal commands'''
    if args:  # find by names
        for name in args:
            if name in stored_macros:
                macro_show(name=name)
            else:
                print(f'Unknown macro name "{name}"')
    else:  # lists all defined macros
        for name in stored_macros:
            macro_show(name=name)


def macro_exec1(name: str) -> None:
    '''Execute 1 macro'''
    cmds: List[str] = stored_macros[name]
    for cmd in cmds:
        execute_input(cmd)


@cmd_register(('macro-exec', 'm-exec'))
def macro_exec(*args: List[str]) -> None:
    '''Format: macro-exec [*keywords]
    Execute macros by name (unlimited number can be stacked)
    If empty, execute macro "" (empty string)'''
    args = args if args else ['']
    for name in args:
        macro_exec1(name=name)


@cmd_register(('macro-repeat', 'm-repeat'))
def macro_repeat(name: str, num_executes: int) -> None:
    '''Format: macro-repeat < macro name > < execution times >
    Execute macros as "name + number" (number can be stacked indefinitely)'''
    for _ in range(num_executes):
        macro_exec1(name=name)


interfaces: Dict[str, Reasoner] = {}
'The dictionary contains all registered NARS interfaces.'

# Reasoner management #


def register_interface(name: str, seed: int = -1, memory: int = 100, capacity: int = 100, silent: bool = False) -> NARSInterface:
    '''
    Wrapped from NARSInterface.construct_interface.
    - It will auto register the new interface to `reasoners`
    - It will add a output handler(uses lambda) to catch its output into output_history
    '''
    # create interface
    interface = NARSInterface.construct_interface(
        seed=seed,
        memory=memory,
        capacity=capacity,
        silent=silent)
    # add handler to catch outputs
    global output_history
    interface.output_handlers.append(
        lambda out: output_history.append(
            (name,  # Name of interface e.g. 'initial'
             out.type.name,  # Type of output e.g. 'ANSWER'
             out.content)  # Content of output e.g. '<A --> B>.'
        ))
    # register in dictionary
    interfaces[name] = interface
    # return the interface
    return interface


current_NARS_interface: NARSInterface = register_interface(
    'initial',
    137,
    500, 500,
    silent=False)


def current_nar_name() -> str:
    global current_NARS_interface
    for name in interfaces:
        if interfaces[name] is current_NARS_interface:
            return name
    return None


@cmd_register(('reasoner-current', 'r-current', 'info'))
def reasoner_current() -> None:
    '''Gets the name and info of the current reasoner'''
    name = current_nar_name()
    if name != None:
        print('Current NARS interface:')
        print(get_interface_info(name, interfaces[name]))


@cmd_register(('reasoner-list', 'r-list', 'list'))
def reasoner_list(*keywords: List[str]) -> None:
    '''Format: reasoner-list [*keywords]
    Enumerate existing reasoners; It can be retrieved with parameters'''
    keywords = keywords if keywords else ['']
    # Search for a matching interface name
    reasoner_names: List[str] = prefix_browse(interfaces, *keywords)
    # Displays information about "matched interface"
    if reasoner_names:
        for name in reasoner_names:  # match the list of all cmds, as long as they match the search results - not necessarily in order
            print(get_interface_info(name, interfaces[name]))
        return
    print(f'No reasoner is browsed by "{", ".join(keywords)}"')


def get_interface_info(name:str, interface: NARSInterface) -> str:
    '''print the information of an NARS interface'''
    information: str = '\n\t'+"\n\t".join(f"{name}: {repr(inf)}" for name, inf in [
        ('Memory', interface.reasoner.memory),
        ('Channels', interface.reasoner.channels),
        ('Overall Experience', interface.reasoner.overall_experience),
        ('Internal Experience', interface.reasoner.internal_experience),
        ('Sequence Buffer', interface.reasoner.sequence_buffer),
        ('Operations Buffer', interface.reasoner.operations_buffer),
    ])
    return f'<{name}>: {information}'


@cmd_register(('reasoner-new', 'r-new'),
              (str, 'unnamed'),
              (int, 100),
              (int, 100),
              (bool, False),)
def reasoner_new(name: str, n_memory: int = 100, capacity: int = 100, silent: bool = False) -> NARSInterface:
    '''Format: reasoner-new < Name > [Memory capacity] [buffer size] [Silent output]
    Create a new reasoner and go to the existing reasoner if it exists
    If an empty name is encountered, the default name is "unnamed"'''
    global current_NARS_interface
    if name in interfaces:
        print(
            f'The reasoner exists! Now automatically go to the reasoner "{name}"!')
        return (current_NARS_interface := interfaces[name])

    current_NARS_interface = register_interface(
        name=name,
        seed=-1,  # use '-1' to keep the seed until directly change
        memory=n_memory,
        capacity=capacity,
        silent=silent)
    print(
        f'A reasoner named "{name}" with memory capacity {n_memory}, buffer capacity {capacity}, silent output {" on " if silent else" off "} has been created!')
    return current_NARS_interface


@cmd_register(('reasoner-goto', 'r-goto'), (str, 'initial'))
def reasoner_goto(name: str) -> NARSInterface:
    '''Format: reasoner-goto < name >
    Transfers the current reasoner of the program to the specified reasoner'''
    global current_NARS_interface
    if name in interfaces:
        print(f"Gone to reasoner named '{name}'!")
        return (current_NARS_interface := interfaces[name])
    print(f"There is no reasoner named '{name}'!")


@cmd_register(('reasoner-delete', 'r-delete'))
def reasoner_delete(name: str) -> None:
    '''Format: reasoner-select < name >
    Deletes the reasoner with the specified name, but cannot delete the current reasoner'''
    global current_NARS_interface
    if name in interfaces:
        if interfaces[name] is current_NARS_interface:
            print(
                f'Unable to delete reasoner "{name}", it is the current reasoner!')
            return
        del interfaces[name]
        print(f'the reasoner named "{name}" has been deleted!')
        return
    print(f'There is no reasoner named "{name}"!')


@cmd_register(('seed-set', 'seed'), (int, 137))
def random_seed(seed: int) -> None:
    '''Format: seed [seed: integer]
    Set the random seed of the random number generator random and numpy.random'''
    NARSInterface.change_random_seed(seed=seed)


@cmd_register(('server', 'server-ws', 'server-websocket'), (str, 'localhost'), (int, 8765))
def server_websocket(host: str = 'localhost', port: int = 8765) -> None:
    '''Format: server [host: str = 'localhost'] [port: integer = 8765]
    Launch a websocket server uses certain host(ip) and port, enables the console to receive input from WS messages.
    - format of receiving: same as user input
    - format of sending [{"interface_name": XXX, "output_type": XXX, "content": XXX}, ...]
    
    The default address is ws://localhost:8765.
    ! The server blocks the main process, and the service can only be stopped using Ctrl+C.'''
    import websockets
    from json import dumps

    async def handler(websocket, path):
        print(f"Connected with path={path}!")
        messages2send:List[str] = []
        len_outputs:int = 0
        last_output_json_objs:list = []
        last_output_json_obj:dict = {}
        async for message in websocket:
            try:
                messages2send.clear()
                # execute
                execute_input(message)
                # handle output using json
                if len_outputs < len(output_history):
                    # clear last sent
                    last_output_json_objs.clear()
                    # traverse newer outputs
                    for i in range(len_outputs, len(output_history)):
                        # data: (interface_name, output_type, content)
                        # format: [{"interface_name": XXX, "output_type": XXX, "content": XXX}, ...]
                        (last_output_json_obj['interface_name'],
                         last_output_json_obj['output_type'],
                         last_output_json_obj['content']) = output_history[i]
                        # append
                        last_output_json_objs.append(last_output_json_obj.copy())
                    # to be sent
                    messages2send.append(dumps(last_output_json_objs))
                # send result if have
                for message2send in messages2send:
                    print(f"send: {message} -> {message2send}")
                    await websocket.send(message2send)
                # refresh output length
                len_outputs = len(output_history)
            # when keyboard interrupt
            except KeyboardInterrupt as e:
                raise e
            # it cannot be interrupted by internal exceptions
            except BaseException as e:
                print(f"Error: {e}")

    # Launch
    import asyncio
    try:
        async def main():
            async with websockets.serve(handler, host, port):
                print(f'WS server launched on ws://{host}:{port}.')
                await asyncio.Future()
        asyncio.run(main())
    except BaseException as e:
        print(f'WS server error: {e}')


# Total index and other variables #

_parse_simplification: bool = False
'Determines whether the "Narsese automatic analytic simplification" enabled'

input_history: List[str] = []
'History of inputs'

output_history: List[Tuple[str, str, str]] = []
'History of outputs. The inner part is (Reasoner Name, PRINT_TYPE, Content)'

# Special grammar parser #

# regular expressions: predefined as constants
PUNCT_INDEX: re.Pattern = re.compile(r'([^0-9%]\.)|[\?\!\@]')


def special_narsese_parse(inp: str) -> str:
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
    if narsese_parse_safe(inp):
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


def execute_input(inp: str, *other_input: List[str]) -> None:
    '''
    Main functions:
    This code is mainly used to process the user input cmds and NAS statements, and perform the corresponding operations according to the input content.

    The types, meanings and relationships of each variable:
    - in "input" (str): A string entered by the user, which may be an cmd or a Nax statement.
    - cmdHistory "Cmd history" (List[str]): Stores the cmd history entered by the user.
    - parse_need_slash "Escape requires slash" (bool): Indicates whether slashes are required for short escape.
    - PRESET_CMDS (dict): Index list of preset cmds, used to execute functions based on cmd names.

    Main operation process:
    1. Wait for user input.
    2. Check whether the input is an cmd. If yes, execute the corresponding preset cmd function.
    3. If the input is not a command, determine whether special parsing is required according to the slash required for parse_need_slash escape.
    4. Inject parsed NAS statements into the NARS interface.

    Possible exceptions:
    - Input execution failure: An exception may occur when an cmd or NAS statement entered by the user is executed. The exception is caught and the exception information is output。
    '''

    # multiline cmd disassembly

    if len(other_input) > 0:
        execute_input(inp=inp)
        for i in other_input:
            execute_input(i)
        return

    # add to history

    input_history.append(inp)

    # pre-jump cmd
    if inp.startswith('/'):
        # the first word is the cmd name, and the following are parameters
        words: List[str] = inp[1:].split()
        if words:  # if not empty
            cmd_name: str = words[0].lower()  # case insensitive
            auto_execute_cmd_by_name(cmd_name, words[1:])
        return  # If it's executed as a command, it won't execute as Narsese input

    # Narsese parsing
    has_slash = False  # usage of backslashes: Enforce/disable "parse simplification"
    if _parse_simplification or (has_slash := inp.startswith('\\')):
        if has_slash:  # Remove the slash if there is a backslash
            inp = inp[1:]
        inp = special_narsese_parse(inp=inp)

    # input NAL
    current_NARS_interface.input_narsese(inp)


def auto_execute_cmd_by_name(cmd_name: str, params: List[str], cmd_dict: Dict[tuple, tuple] = PRESET_CMDS) -> bool:
    '''Execute cmd by name with autocompletion
    returns: whether a cmd is chosen and executed successfully'''
    # auto browse & complete
    name_alias_hints: List[Tuple[str]] = prefix_cmd_browse(cmd_dict, cmd_name)
    # if it have a precise match, directly use it
    for i in range(len(name_alias_hints)):
        name_aliases = name_alias_hints[i]
        if any(name_alias == cmd_name for name_alias in name_aliases):
            name_alias_hints = [name_aliases]
            break
    # Only option: Full match or auto complete
    if len(name_alias_hints) == 1:
        # auto complete
        if not cmd_name in name_alias_hints[0]:
            print(
                f'Autocompleted cmd to "{"/".join(name_alias_hints[0])}".')
        name_alias_index = name_alias_hints[0]
        # Cmd execution: Automatically adjust the "parameter requirements" of specific cmds and intercept parameters
        cmd_data = cmd_dict[name_alias_index]
        cmd_handler = cmd_data[0]
        type_N_default: List[Tuple[type, any]] = (
            cmd_data[1]
            if len(cmd_data) > 1 else None)
        params: list = quick_convert_cmd_types(params, type_N_default)
        try:
            # in the form of positional arguments, to the appropriate handler. Structure: {Name: (handler, ordinal and default list)}
            cmd_handler(*params)
            return True
        except BaseException as e:
            print('Cmd execute failed: ',
                  e.with_traceback(None) if e else e)
            return False
    else:
        hint = 'Are you looking for "' + \
            "\" | \"".join('/'.join(alias) for alias in name_alias_hints) + \
            '"?' if name_alias_hints else ''
        print(f'Unknown cmd {cmd_name}. {hint}')
        return False

# @checkExcept error alarm (message formatted message =' Input execution failed: %s')
# TODO fix "TypeError: checkExcept error alarm..decorator decorator () missing 1 required positional argument: 'func'"


def __main__():
    # enter preset format prompt "IN", not regards `silent`
    print_output(PrintType.COMMENT, '', comment_title='Input', end='')

    # get & execute
    inp: str = input()
    execute_input(inp=inp)


## main program ##
if __name__ == '__main__':
    while 1:
        __main__()
