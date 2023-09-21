'''PyNARS-Explore-Experiment
This program is used to experiment on some projects of PyNARS and import local NARS for detailed study
! using backslash `\` to run experimental commands
'''

# Interface
from pynars.ConsolePlus import *
# need to report errors to ** timely detection of ** "invalid statement input" caused by the bug
from pynars.Interface import NAL_Parse

# PyNARS: Import internal modules
from pynars.NARS.DataStructures._py.Channel import *
from pynars.NARS.DataStructures import *
from pynars.Narsese import *

# other native modules
from random import randint


# information

def infBag(bag: Bag, sep: str = ',', indentCount: int = 1) -> str:
    '''Relation of extension: Channel -> Buffer -> Bag'''
    notNoneLevels: list[list] = [
        levelList for levelList in bag.levels if levelList]
    if notNoneLevels:
        sep = sep + '\n' + "\t"*indentCount
        return f'{repr(bag)} :\n' + "\t"*indentCount + sep.join(
            ','.join(
                repr(value)
                for value in level)
            for level in notNoneLevels)
    return repr(bag)


def infBuffer(buffer: Buffer) -> str:
    item: Item = buffer.take_max(remove=False)
    return repr(buffer) + infBag(Bag(buffer)) + f' ->  {item}'


def infChannel(channel: Channel) -> str:
    b = Buffer(channel)
    return repr(channel) + f'@{repr(infBuffer(buffer=b))}'


def infMemory(memory: Memory, indentCount: int = 1) -> str:
    return repr(memory) + f'@{infBag(memory.concepts,indentCount=indentCount)}'


def infReasoner(reasoner: Reasoner):
    return '\n\t'+"\n\t".join(f"{name}: {inf}" for name, inf in [
        ('Memory', infMemory(reasoner.memory, indentCount=2)),
        ('Channels', '\r\n\t\t'.join(
            infChannel(channel)
            for channel in reasoner.channels)),
        # this section is a "temporary repository" of the knowledge NARS has acquired from the "channel".
        ('Overall Experience', infBuffer(reasoner.overall_experience)),
        ('Internal Experience', infBuffer(reasoner.internal_experience)),
        ('Sequence Buffer', infBuffer(reasoner.sequence_buffer)),
        ('Operations Buffer', infBuffer(reasoner.operations_buffer)),
    ])


def printInf():
    print(
        f'''<{getCurrentReasonerName()}>: {infReasoner(currentNARSInterface.reasoner)}''')

## Main program ##


def _cmdExperiment(cmd: str):
    '''Cmd experiment entry'''
    nars = currentNARSInterface.reasoner  # current NARS reasoner
    if cmd == 'l':  # list the details of the current reasoner
        reasonerList()
    elif cmd == 't':  # test an input sentence
        execInput('<A --> B>.')
    elif cmd == 'r':  # test an random input sentence
        execInput(f'<A{randint(1,9)} --> A{randint(1,9)}>.')
    elif cmd == 'c':  # list all concepts
        print(infBag(nars.memory.concepts))
    elif cmd == 'exec':  # execute code
        while (inp := input('Please input Python code (empty to cancel)')):
            try:
                exec(inp)  # separated by a space, followed by a statement
            except BaseException as e:
                print(f'Error! {e}')
    elif cmd == 'v':  # list variables
        print('locals\n\t'+'\n\t'.join(f'{k} : {v}' for k, v in locals().items()),
              'globals\n\t' +
              '\n\t'.join(f'{k} : {v}' for k, v in globals().items()),
              sep='\n')
    elif cmd == 'h':  # history
        printHistory('')
        printHistory('1')
    elif cmd == 'help':  # help
        print('''The backslash commands is used for feature experiments.
              to see the supported certain commands, may you should view `Experiments\ExConsole\main.py\_cmdExperiment`.''')
    elif cmd == 'ch':  # New channel addition test
        # add new channel
        channel: Channel = Channel(capacity=5, n_buckets=5, max_duration=10000)
        # [2023-09-21 23:51:23] PyNARS does not currently have a built-in "add channel" method
        nars.channels.append(channel)
        print(infChannel(channel=channel))
        # test new channel
        [channel.put(NAL_Parse(testSentence_C))  # auto parse
            for testSentence_C in [
                '<cpt_channel_1 --> cpt_channel_2>.',
                '<cpt_channel_2 --> cpt_channel_3>.',
                '<cpt_channel_1 --> cpt_channel_3>?',
        ]
        ]  # ? multiple input at once
        printInf()
        execInput('/waitans')
        printInf()
    elif cmd == 'cha':  # Shared channel test
        channel: Channel = NarseseChannel(
            capacity=500, n_buckets=100, max_duration=1000)
        # new reasoner
        rName1: str = '1'
        rName2: str = '2'
        r1: Reasoner = reasonerNew(name=rName1).reasoner
        r2: Reasoner = reasonerNew(name=rName2).reasoner
        r1.narsese_channel = r2.narsese_channel = r1.channels[0] = r2.channels[0] = channel
        execInput('<A --> B>.')  # enter the NARS statement in r2
        reasonerGoto(rName1)  # r1 also has channels in it
        execInput('10')  # enter the NARS statement in r2
        reasonerList()
    elif cmd == 'me':  # Shared memory test
        memory: Memory = Memory(
            capacity=1000,
            n_buckets=50)  # This `n_buckets` determines the levels of the concepts in it.
        # new reasoner
        rName1: str = '1'
        rName2: str = '2'
        r1: Reasoner = reasonerNew(name=rName1)._NARS
        r2: Reasoner = reasonerNew(name=rName2)._NARS
        r1.memory = r2.memory = memory
        # enter the NARS statement in r2
        execInput('A --> B.', 'B --> C.', 'A --> C?')
        reasonerGoto(rName1)  # r1 also has channels in it
        execInput('1')  # enter the NARS statement in r2
        print(r1.memory is r2.memory, r1.memory is memory)
        printInf()
    elif cmd == 'op':
        taskOp: Task = NAL_Parse('<antecedent --> result>.')  # auto parse
        # term.type = TermType.STATEMENT # ! Only statements can be actions, not mandatory
        statementOp = taskOp.term  # term of the task
        # * Force the term involved in the task to be set to "action", if is_executable = True
        statementOp.is_operation = True
        print(f'Is operation? {statementOp.is_executable}')
        '''concept Concept: Concept = concept. _conceptualize(  # Generate concept
        nars.memory,
        term=statement Operation statement,
        Budget=budget(0.9, 0.9, 0.5)
        )
        nars.memory.concepts.put(concept)
        # into the concept, but it does not seem to be associated with the task, the reasoner will not use it.
        # '''
        # placing tasks directly into perceptual channels (Narsese channels can only pass text)
        nars.perception_channel.put(taskOp)
        # Automatic reasoning five steps, let NAS put "antecedent" and "result" into the memory area
        execInput('5')
        print(infBag(nars.memory.concepts))  # print concept list
    elif cmd == 'far':  # remote inference test
        n: int = int(input('Please enter the length of chain:'))
        [execInput(f'chainNo{i} --> chainNo{i+1}.')
            for i in range(n)
         ]
        printInf()
        execInput(f'chainNo0 --> chainNo{n}?')
        execInput('/waitans')
    elif cmd == 'js':  # JSON test: Input a series of numbers and construct a set, allowing NARS to determine ownership
        from data2nal import auto2NAL, SIGN_RELATION_BELONG
        n: int = int(input('Please enter the number: '))
        f: set = {x for x in range(n)}
        sN: str = f'Num0to{n}'
        s2: set = {sN, 'element2'}
        sN2: str = 'bigSet'
        execInput(*auto2NAL(f, sN), *auto2NAL(f, sN2),
                  f'<(*,{1},{sN2}) --> {SIGN_RELATION_BELONG}>?')
        printInf()
        execInput('/waitans')
        printInf()
    elif cmd == 'js2':  # JSON Test 2: Enter a custom dictionary and ask for relationships one by one
        from data2nal import auto2NAL
        print('Part II:')
        dic: dict = {
            'smallestPositiveInteger': 1,
            'evenNumberLT10': [
                2, 4, 6, 8
            ],
            'is0notNeg': True,
            1: {
                'dictName': 'aNameOfDict'
            }
        }
        execInput(*auto2NAL(dic, 'myDict'))
        printInf()
        execInput(*auto2NAL(dic, 'myDict', punct=Punctuation.Question))
        printInf()
        execInput('/waitans')
    elif cmd == 'js3':  # JSON Test 3: Enter a Config.json object that acts as its own "system parameter"
        print('Part III')
        from pynars.Interface import DEFAULT_CONFIG
        from data2nal import auto2NAL
        printInf()
        execInput(*auto2NAL(DEFAULT_CONFIG, 'systemConfig',
                            punct=Punctuation.Judgement))
        printInf()
        execInput(*auto2NAL(DEFAULT_CONFIG, 'systemConfig',
                            punct=Punctuation.Question))
        printInf()
        execInput('/waitans')
    elif cmd == 'eval':  # Load any Python object into NARS
        from data2nal import auto2NAL
        obj: any = None
        while not obj:
            try:
                obj: any = eval(input(' Please input your Python object: '))
            except BaseException as e:
                print(
                    f' parsing failed! Error: {e.With_traceback(None) if e else e}')
        name: str = input(
            'Please enter a name for this object (leave blank for automatic generation): ')
        punct: str = input(
            'Please enter your modality for the object (./?/!) (Leave blank default.): ')
        nals: list[str] = auto2NAL(
            obj, punct=punct if punct else '.', name=name if name else None)
        print(f'Input object: {repr(obj)}\nNAL text: \n' + "\n".join(nals))
        execInput(*nals)
    elif cmd == 'mcopy':  # Experiment: Memory copy & Localization retention
        import jsonpickle as jp  # Use the JSON serialization library jsonpickle
        copiedMem: Memory = deepcopy(nars.memory)
        execInput('A-->B.', 'B-->C.', 'A-->C?', '/waitans')
        print(id(nars.memory), infMemory(nars.memory),
              'copied:\n', id(copiedMem), infMemory(copiedMem))
        jpEmem = jp.encode(nars.memory)
        jpEcopied = jp.encode(copiedMem)
        print('pickle#Encode:\n', repr(jpEmem), 'copied:\n', repr(jpEcopied))
        decodedMem: Memory = jp.decode(jpEcopied)
        print(id(copiedMem), infMemory(copiedMem), 'decoded:\n',
              id(decodedMem), infMemory(decodedMem))
    elif cmd == 'rcopy':  # Make a deep copy of the entire reasoner
        import jsonpickle as jp  # Use the JSON serialization library jsonpickle
        import json
        copiedNar: Reasoner = deepcopy(nars)  # deep copy
        jpEnar: str = jp.encode(copiedNar)  # serialize to JSON string
        encodedNar: dict = json.loads(jpEnar)  # JSON string to dict
        rStrDict: str = repr(encodedNar)  # dict to str
        decodedNar: Reasoner = jp.decode(
            json.dumps(encodedNar))  # str to Reasoner
        print(
            f'Copied:\n{infReasoner(copiedNar)}\nEncoded:\n{rStrDict}\nDecoded:\n{infReasoner(decodedNar)}')
    elif cmd == 'copyJ':  # Copy the reasoner data to the clipboard
        # import module
        from pyperclip import copy
        import jsonpickle as jp
        try:
            jpEnar: str = jp.encode(nars)  # serialize to JSON string
            print(
                f'Source reasoner:\n{infReasoner(nars)}\n Serialized JSON string:\n{jpEnar}')
            copy(jpEnar)  # copy to clipboard
            print('JSON data copied!')
        except BaseException as e:
            print(f'Save Failed!\nError:{e.with_traceback(None) if e else e}')
    elif cmd == 'loadJ':  # load the clipboard reasoner data into the interface
        # import module
        import jsonpickle as jp
        try:
            jsonPath: str = input(
                'Please enter your saved reasoner JSON path:')  # get JSON path
            from pathlib import Path
            jsonPath: Path = Path(jsonPath)
            with open(jsonPath, mode='r', encoding='utf-8') as jsonFile:
                jsonStr: str = jsonFile.read()
            try:
                decodedNAR: Reasoner = jp.decode(
                    jsonStr)  # deserialize from JSON string
                try:
                    interfaceName: str = input(
                        'Please enter a new interface name:')  # accept the reasoner with a new interface
                    interface: NARSInterface = NARSInterface(
                        NARS=decodedNAR)  # create interface
                    reasoners[interfaceName] = interface  # directly add
                    reasonerGoto(interfaceName)  # goto
                    print(
                        f"Import a reasoner named {interfaceName}, silent {'on' if interface.silentOutput else 'off'}.")
                    print(
                        f'Pre-deserialized JSON string:\n{jsonStr}\nNew reasoner:\n{infReasoner(decodedNAR)}')
                except BaseException as e:
                    print(
                        f'Import failed! \nError:{e.with_traceback(None) if e else e}')
            except BaseException as e:
                print(
                    f'Deserialization failed! \nError:{e.with_traceback(None) if e else e}')
        except BaseException as e:
            print(f'Read failed! \nError:{e.with_traceback(None) if e else e}')
    return


# Main
if __name__ == '__main__':
    while 1:
        # enter preset format prompt "IN"
        printOutput(PrintType.COMMENT, '',
                    comment_title='Input', end='')  # force hint

        # get input
        inp: str = input()

        # deal input

        if not inp:
            pass
        elif inp[0] == '\\':  # Gives the current interface library information
            cmd: str = inp[1:]
            if not cmd:
                printInf()
            else:
                _cmdExperiment(cmd=cmd)
                continue

        # execute input
        if 1:
            pass
            execInput(inp=inp)
        try:
            pass
        except BaseException as e:
            print('Input execute failed: ', e.with_traceback(None) if e else e)
