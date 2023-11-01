'''PyNARS-Explore-Experiment
This program is used to experiment on some projects of PyNARS and import local NARS for detailed study
! using backslash `\` to run experimental commands
'''

# Interface
from pynars.ConsolePlus import *
# need to report errors to ** timely detection of ** "invalid statement input" caused by the bug
from pynars.Narsese import parser as NarseseParser

# PyNARS: Import internal modules
from pynars.NARS.DataStructures._py.Channel import *
from pynars.NARS.DataStructures import *
from pynars.Narsese import *

# other native modules
from random import randint

# compatible type annotation
from typing import List, Dict, Tuple, Iterable

# information


def show_bag(bag: Bag, sep: str = ',', indent_count: int = 1) -> str:
    '''Relation of extension: Channel -> Buffer -> Bag'''
    not_none_levels: List[list] = [
        level_list for level_list in bag.levels if level_list]
    if not_none_levels:
        sep = sep + '\n' + "\t"*indent_count
        return f'{repr(bag)} :\n' + "\t"*indent_count + sep.join(
            ','.join(
                repr(value)
                for value in level)
            for level in not_none_levels)
    return repr(bag)


def show_buffer(buffer: Buffer) -> str:
    item: Item = buffer.take_max(remove=False)
    return repr(buffer) + show_bag(Bag(buffer)) + f' ->  {item}'


def show_channel(channel: Channel) -> str:
    b = Buffer(channel)
    return repr(channel) + f'@{repr(show_buffer(buffer=b))}'


def show_memory(memory: Memory, indent_count: int = 1) -> str:
    return repr(memory) + f'@{show_bag(memory.concepts,indent_count=indent_count)}'


def show_reasoner(reasoner: Reasoner):
    return '\n\t'+"\n\t".join(f"{name}: {inf}" for name, inf in [
        ('Memory', show_memory(reasoner.memory, indent_count=2)),
        ('Channels', '\r\n\t\t'.join(
            show_channel(channel)
            for channel in reasoner.channels)),
        # this section is a "temporary repository" of the knowledge NARS has acquired from the "channel".
        ('Overall Experience', show_buffer(reasoner.overall_experience)),
        ('Internal Experience', show_buffer(reasoner.internal_experience)),
        ('Sequence Buffer', show_buffer(reasoner.sequence_buffer)),
        ('Operations Buffer', show_buffer(reasoner.operations_buffer)),
    ])


def show_information():
    print(
        f'''<{current_nar_name()}>: {show_reasoner(current_NARS_interface.reasoner)}''')

## Main program ##


EXPERIMENTAL_CMDS: Dict[Tuple[str], Tuple[any, Tuple[str]]] = {}


def exp_register(*cmd_names: Tuple[str]):
    '''Mimic from `cmd_register` in "Interface.py"
    It's no need of parameters because the experimental functions can utilize all of global variable'''
    def decorator(func):
        # register
        global EXPERIMENTAL_CMDS
        EXPERIMENTAL_CMDS[cmd_names] = (func, )
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


@exp_register('l')
def list_details_reasoner() -> None:
    return reasoner_list()


@exp_register('t')
def test_simple_output() -> None:
    execute_input('<A --> B>.')


@exp_register('r')
def test_random_input_sentence() -> None:
    execute_input(f'<A{randint(1,9)} --> A{randint(1,9)}>.')


@exp_register('c')
def list_all_concepts() -> None:
    print(show_bag((current_NARS_interface.reasoner.memory.concepts)))


@exp_register('exec')
def exec_multiline_python_code() -> None:
    while (inp := input('Please input Python code (empty to cancel)')):
        try:
            exec(inp)  # separated by a space, followed by a statement
        except BaseException as e:
            print(f'Error! {e}')


@exp_register('v')
def list_variables() -> None:
    print('locals\n\t'+'\n\t'.join(f'{k} : {v}'for k, v in locals().items()),
          'globals\n\t' +
          '\n\t'.join(f'{k} : {v}'for k, v in globals().items()),
          sep='\n')


@exp_register('r')
def list_histories() -> None:
    print_history_in('')
    print_history_in('1')


@exp_register('help')
def help_of_experiments() -> None:
    print('''The backslash commands is used for feature experiments.\nto see the supported certain commands, may you should view `Experiments\ExConsole\main.py\_cmdExperiment`.''')
    help('', search_in=EXPERIMENTAL_CMDS)


@exp_register('ch')
def channel_addition_test() -> None:
    # add new channel
    channel: Channel = Channel(capacity=5, n_buckets=5, max_duration=10000)
    # [2023-09-21 23:51:23] PyNARS does not currently have a built-in "add channel" method
    current_NARS_interface.reasoner.channels.append(channel)
    print(show_channel(channel=channel))
    # test new channel
    [channel.put(NarseseParser.parse(test_sentence_C))  # auto parse
        for test_sentence_C in [
            '<cpt_channel_1 --> cpt_channel_2>.',
            '<cpt_channel_2 --> cpt_channel_3>.',
            '<cpt_channel_1 --> cpt_channel_3>?',
    ]
    ]  # ? multiple input at once
    show_information()
    execute_input('/waitans')
    show_information()


@exp_register('cha')
def shared_channel_test() -> None:
    channel: Channel = NarseseChannel(
        capacity=500, n_buckets=100, max_duration=1000)
    # new reasoner
    r_name1: str = '1'
    r_name2: str = '2'
    r1: Reasoner = reasoner_new(name=r_name1).reasoner
    r2: Reasoner = reasoner_new(name=r_name2).reasoner
    r1.narsese_channel = r2.narsese_channel = r1.channels[0] = r2.channels[0] = channel
    execute_input('<A --> B>.')  # enter the NARS statement in r2
    reasoner_goto(r_name1)  # r1 also has channels in it
    execute_input('10')  # enter the NARS statement in r2
    reasoner_list()


@exp_register('me')
def shared_memory_test() -> None:
    memory: Memory = Memory(
        capacity=1000,
        n_buckets=50)  # This `n_buckets` determines the levels of the concepts in it.
    # new reasoner
    rName1: str = '1'
    rName2: str = '2'
    r1: Reasoner = reasoner_new(name=rName1)._NARS
    r2: Reasoner = reasoner_new(name=rName2)._NARS
    r1.memory = r2.memory = memory
    # enter the NARS statement in r2
    execute_input('A --> B.', 'B --> C.', 'A --> C?')
    reasoner_goto(rName1)  # r1 also has channels in it
    execute_input('1')  # enter the NARS statement in r2
    print(r1.memory is r2.memory, r1.memory is memory)
    show_information()


@exp_register('op')
def operations_test() -> None:
    # register operation, the register of mental operations can be seen in pynars\NARS\InferenceEngine\GeneralEngine\Rules\NAL9.py
    from pynars.NARS import Operation
    def exeF(arguments: Iterable[Term], task: Task=None, memory: Memory=None) -> Union[Task,None]:
        '''
        The execution should accepts arguments (terms), task(current) and current memory(to deal mental operations)
        @return a task(is used to represent the new task generated) or None(no task is processed)
        '''
        print(f'executed: arguments={arguments}, task={task}, memory={memory}. the "task" will be returned')
        return task
    Operation.register(Operation.Operator('f'), exeF)
    # build task
    # task1: Task = NarseseParser.parse('f(x).')  # the same as <(*, x) --> ^f>.
    # task1: Task = NarseseParser.parse('f(x).')  # the same as <(*, x) --> ^f>.
    # * Force the term involved in the task to be set to "action", if is_executable = True
    # print(f'Is operation? {task1.is_executable}')
    # placing tasks directly into perceptual channels (Narsese channels can only pass text)
    # current_NARS_interface.reasoner.perception_channel.put(task1)
    '''concept Concept: Concept = concept. _conceptualize(  # Generate concept
        current_NARS_interface.reasoner.memory,
        term=statement Operation statement,
        Budget=budget(0.9, 0.9, 0.5)
        )
        current_NARS_interface.reasoner.memory.concepts.put(concept)
    '''
    # into the concept, but it does not seem to be associated with the task, the reasoner will not use it.
    # run other cmds
    execute_input('5')
    execute_input('<A ==> G>.')
    execute_input('<(^f, x) ==> A>.')
    execute_input('5')
    current_NARS_interface.input_narsese('G!')  # avoid to be <G>!
    # Automatic reasoning five steps, let NAS put "antecedent" and "result" into the memory area
    execute_input('/waitans ACHIEVED')
    # * it should be contained with two outputs:
      # * `EXE   :<(*, x)-->^f> = $0.022;0.225;0.644$ <(*, x)-->^f>! %1.000;0.287% {None: 2, 1, 0}`
      # * `ACHIEVED:<(*, x)-->^f>. :\: %1.000;0.900%`
    # print concept list
    print(show_bag(current_NARS_interface.reasoner.memory.concepts))


@exp_register('far', 'chain', 'chain_inference')
def chain_inference_test() -> None:
    n: int = int(input('Please enter the length of chain:'))
    [execute_input(f'<chain_{i} --> chain_{i+1}>.')
        for i in range(n)
     ]
    show_information()
    execute_input(f'<chain_0 --> chain_{n}>?')
    execute_input('/waitans')


@exp_register('json')
def JSON_test() -> None:
    '''Input a series of numbers and construct a set, allowing NARS to determine ownership'''
    from Experiments.ExConsole.data2narsese import auto2Narsese, SIGN_RELATION_BELONG
    n: int = int(input('Please enter the number: '))
    f: set = {x for x in range(n)}
    sN: str = f'Num0to{n}'
    s2: set = {sN, 'element2'}
    sN2: str = 'big_set'
    execute_input(*auto2Narsese(f, sN), *auto2Narsese(f, sN2),
                  f'<(*,{1},{sN2}) --> {SIGN_RELATION_BELONG}>?')
    show_information()
    execute_input('/waitans')
    show_information()


@exp_register('json2')
def JSON_test2() -> None:
    '''Enter a custom dictionary and ask for relationships one by one'''
    from Experiments.ExConsole.data2narsese import auto2Narsese
    print('JSON Test Part II:')
    dic: dict = {
        'smallest_positive_integer': 1,
        'even_number_LT_10': [
            2, 4, 6, 8
        ],
        'is0not_neg': True,
        1: {
            'dict_name': 'a_name_of_dict'
        }
    }
    execute_input(*auto2Narsese(dic, 'my_dict'))
    show_information()
    execute_input(*auto2Narsese(dic, 'my_dict', punct=Punctuation.Question))
    show_information()
    execute_input('/waitans')


@exp_register('eval', 'py_object')
def py_object_load_in() -> None:
    '''Load any Python object into NARS'''
    from Experiments.ExConsole.data2narsese import auto2Narsese
    obj: any = None
    while not obj:
        try:
            obj: any = eval(input('Please input your Python object: '))
        except BaseException as e:
            print(
                f'parsing failed! Error: {e.with_traceback(None) if e else e}')
    name: str = input(
        'Please enter a name for this object (leave blank for automatic generation): ')
    punct: str = input(
        'Please enter your modality for the object (./?/!) (Leave blank default.): ')
    nals: List[str] = auto2Narsese(
        obj, punct=punct if punct else '.', name=name if name else None)
    print(f'Input object: {repr(obj)}\nNarsese: \n' + "\n".join(nals))
    execute_input(*nals)


@exp_register('mcopyJ')
def memory_copy_JSON() -> None:
    '''Experiment: Memory copy & Localization retention'''
    nars = current_NARS_interface.reasoner
    import jsonpickle as jp  # Use the JSON serialization library jsonpickle
    copied_mem: Memory = deepcopy(nars.memory)
    execute_input('A-->B.', 'B-->C.', 'A-->C?', '/waitans')
    print(id(nars.memory), show_memory(nars.memory),
          'copied:\n', id(copied_mem), show_memory(copied_mem))
    jp_emem = jp.encode(nars.memory)
    jp_ecopied = jp.encode(copied_mem)
    print('pickle#Encode:\n', repr(jp_emem), 'copied:\n', repr(jp_ecopied))
    decoded_mem: Memory = jp.decode(jp_ecopied)
    print(id(copied_mem), show_memory(copied_mem), 'decoded:\n',
          id(decoded_mem), show_memory(decoded_mem))


@exp_register('rcopyJ')
def reasoner_copy_JSON() -> None:
    '''Make a deep copy of the entire reasoner'''
    nars = current_NARS_interface.reasoner
    import jsonpickle as jp  # Use the JSON serialization library jsonpickle
    import json
    copied_nar: Reasoner = deepcopy(nars)  # deep copy
    jp_enar: str = jp.encode(copied_nar)  # serialize to JSON string
    encoded_nar: dict = json.loads(jp_enar)  # JSON string to dict
    rStr_dict: str = repr(encoded_nar)  # dict to str
    decoded_nar: Reasoner = jp.decode(
        json.dumps(encoded_nar))  # str to Reasoner
    print(
        f'Copied:\n{show_reasoner(copied_nar)}\nEncoded:\n{rStr_dict}\nDecoded:\n{show_reasoner(decoded_nar)}')


@exp_register('copyJ')
def copy_JSON() -> None:
    '''Copy the reasoner data to the clipboard'''
    nars = current_NARS_interface.reasoner
    # import module
    from pyperclip import copy
    import jsonpickle as jp
    try:
        jp_enar: str = jp.encode(nars)  # serialize to JSON string
        print(
            f'Source reasoner:\n{show_reasoner(nars)}\n Serialized JSON string:\n{jp_enar}')
        copy(jp_enar)  # copy to clipboard
        print('JSON data copied!')
    except BaseException as e:
        print(f'Save Failed! Error: {e.with_traceback(None) if e else e}')


@exp_register('loadJ')
def load_JSON() -> None:
    '''load the clipboard reasoner data into the interface'''
    # import module
    import jsonpickle as jp
    try:
        json_path: str = input(
            'Please enter your saved reasoner JSON path:')  # get JSON path
        from pathlib import Path
        json_path: Path = Path(json_path)
        with open(json_path, mode='r', encoding='utf-8') as json_file:
            json_str: str = json_file.read()
        try:
            decoded_NAR: Reasoner = jp.decode(
                json_str)  # deserialize from JSON string
            try:
                interface_name: str = input(
                    'Please enter a new interface name:')  # accept the reasoner with a new interface
                interface: NARSInterface = NARSInterface(
                    NARS=decoded_NAR)  # create interface
                interfaces[interface_name] = interface  # directly add
                reasoner_goto(interface_name)  # goto
                print(
                    f"Import a reasoner named {interface_name}, silent {'on' if interface.silent_output else 'off'}.")
                print(
                    f'Pre-deserialized JSON string:\n{json_str}\nNew reasoner:\n{show_reasoner(decoded_NAR)}')
            except BaseException as e:
                print(
                    f'Import failed! \nError: {e.with_traceback(None) if e else e}')
        except BaseException as e:
            print(
                f'Deserialization failed! \nError: {e.with_traceback(None) if e else e}')
    except BaseException as e:
        print(f'Read failed! \nError: {e.with_traceback(None) if e else e}')


@exp_register('copy', 'pickle')
def copy_pickle() -> None:
    '''Save the reasoner data to a file'''
    nars = current_NARS_interface.reasoner
    # import module
    import pickle as p
    # start to save
    file_name: str = input(
        'Please enter the file name to save reasoner (default is "[current reasoner name].pickle):')
    try:
        with open(f'{file_name if file_name else current_nar_name()}.pickle', 'wb') as file:
            print(
                f'Trying to save the reasoner "{current_nar_name()}" to file "{file_name}.pickle"...')
            # pickle reasoner to file
            p.dump(nars, file)
            print(f'Reasoner data saved as "{file_name}.pickle"!')
    except BaseException as e:
        print(f'Save Failed! Error: {e.with_traceback(None) if e else e}')
        # TODO: Failed with error "Can't pickle local object 'Bag.__init__.<locals>.map_priority'"


@exp_register('load', 'unpickle')
def load_pickle() -> None:
    '''load the reasoner data into the interface'''
    # import module
    import pickle as p
    try:
        from pathlib import Path
        file_path: str = input(
            'Please enter the file path of your saved reasoner (e.g. "reasoner.pickle"): ')  # get .pickle path
        file_path: Path = Path(file_path)
        with open(file_path, mode='rb') as file:
            try:
                print(
                    f'Trying to load reasoner from "{file_path}"...')
                # deserialize from pickle file
                decoded_NAR: Reasoner = p.load(file)
                try:
                    # accept the reasoner with a new interface
                    interface_name: str = input(
                        'Please enter a new interface name: ')
                    # create interface
                    interface: NARSInterface = NARSInterface(NARS=decoded_NAR)
                    interfaces[interface_name] = interface  # directly add
                    reasoner_goto(interface_name)  # goto
                    print(
                        f"Import a reasoner named {interface_name}, silent {'on' if interface.silent_output else 'off'}.")
                    print(
                        f'New reasoner:\n{show_reasoner(decoded_NAR)}')
                except BaseException as e:
                    print(
                        f'Import failed! \nError: {e.with_traceback(None) if e else e}')
            except BaseException as e:
                print(
                    f'Deserialization failed! \nError: {e.with_traceback(None) if e else e}')
    except BaseException as e:
        print(f'Read failed! \nError: {e.with_traceback(None) if e else e}')


def _cmd_experiment(cmd: str):
    '''Cmd experiment entry'''
    nars = current_NARS_interface.reasoner  # current NARS reasoner
    # [2023-09-22 16:34:55] Now reuse the multi-patch to run cmd respectfully
    auto_execute_cmd_by_name(cmd, [], EXPERIMENTAL_CMDS)


# Main
if __name__ == '__main__':
    while 1:
        # enter preset format prompt "IN"
        print_output(PrintType.COMMENT, '',
                     comment_title='Input', end='')  # force hint

        # get input
        inp: str = input()

        # deal input

        if not inp:
            pass
        elif inp[0] == '\\':  # Gives the current interface library information
            cmd: str = inp[1:]
            if not cmd:
                show_information()
            else:
                _cmd_experiment(cmd=cmd)
                continue

        # execute input
        if 1:
            pass
            execute_input(inp=inp)
        try:
            pass
        except BaseException as e:
            print('Input execute failed: ', e.with_traceback(None) if e else e)
