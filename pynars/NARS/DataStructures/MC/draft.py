from multiprocessing import Process

from BufferMC import Buffer
from SampleChannels.WordNetChannel import WordNetChannel
from pynars.NARS import Reasoner
from pynars.Narsese import Task


def nars_core():
    """
    It will try to read from the nars_inputs list, and write the results in nars_outputs (just write for recording).
    And it will also append some results to wcn_inputs for further processing. (hand the task to the channel)
    """
    global nars_input
    global nars_output
    global wcn_input
    global wcn_output
    for _ in range(300):
        # here it runs for 300 cycles, but it is designed to run forever, if so, please use while(True)
        if len(nars_input) == 0:
            ret = nars.cycle()
        else:
            tmp = nars_input.pop(0)
            if isinstance(tmp, Task):
                success, task, _, ret = nars.input_narsese(text=str(tmp), go_cycle=True)
            else:
                success, task, _, ret = nars.input_narsese(text=tmp, go_cycle=True)
        nars_output.append(ret)
        if len(ret[0]) != 0:
            for each in ret[0]:
                wcn_input.append(each)


def wcn_core():
    global nars_input
    global nars_output
    global wcn_input
    global wcn_output
    for _ in range(300):
        # here it runs for 300 cycles, but it is designed to run forever, if so, please use while(True)
        if len(wcn_input) == 0:
            ret = wcn.WordNetQuery()
        else:
            ret = wcn.WordNetQuery(wcn_input.pop(0))
        wcn_output.append(ret)
        if ret is not None:
            nars_input.append(each)


if __name__ == "__main__":

    apriori_knowledge = ["<<cat --> #y> ==> <cat --> [KNOWN]>>.",
                         "<<#y --> cat> ==> <cat --> [KNOWN]>>.",
                         "<Query(WordNet, cat) ==> <cat --> [KNOWN]>>."]
    # including product as images

    nars = Reasoner(100, 100)
    for each in apriori_knowledge:
        nars.input_narsese(each, True)

    buff = Buffer(100, nars.memory)
    wcn = WordNetChannel("WCN", buff)

    # global data
    nars_input = ["<cat --> [KNOWN]>!", "<?x --> cat>?"]  # though there is a question here, the answer is not used
    nars_output = []
    wcn_input = []
    wcn_output = []

    process_list = []

    p = Process(target=nars_core(), args=('Python',))
    p.start()
    process_list.append(p)

    p = Process(target=wcn_core(), args=('Python',))
    p.start()
    process_list.append(p)

    for i in range(len(process_list)):
        process_list[i].join()

    print(nars_output)
    print(wcn_output)
