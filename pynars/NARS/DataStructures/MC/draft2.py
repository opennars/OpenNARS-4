"""
draft2.py uses wordnet as an example
"""


from multiprocessing import Process

from BufferMC import Buffer
from SampleChannels.WordNetChannel import WordNetChannel
from pynars.NARS import Reasoner
from pynars.Narsese import Task
from pynars.NARS.DataStructures.MC.util.word2narsese_exAll import words2narsese


def nars_core():
    """
    It will try to read from the nars_inputs list, and write the results in nars_outputs (just write for recording).
    And it will also append some results to wcn_inputs for further processing. (hand the task to the channel)
    """
    global nars_input
    global nars_output
    global wch_input
    global wch_output
    for _ in range(300):
        # here it runs for 300 cycles, but it is designed to run forever, if so, please use while(True)
        if len(nars_input) == 0:
            ret = nars.cycle()
        else:
            tmp = nars_input.pop(0)

            print("narsese input:", tmp)

            if isinstance(tmp, Task):
                success, task, _, ret = nars.input_narsese(text=str(tmp), go_cycle=True)
            else:
                success, task, _, ret = nars.input_narsese(text=tmp, go_cycle=True)
        nars_output.append(ret)
        if len(ret[0]) != 0:
            for each in ret[0]:
                wch_input.append(each)


def wcn_core():
    global nars_input
    global nars_output
    global wch_input
    global wch_output
    for _ in range(300):
        # here it runs for 300 cycles, but it is designed to run forever, if so, please use while(True)
        if len(wch_input) == 0:
            ret = wcn.WordNetQuery()
        else:
            tmp = wch_input.pop(0)
            print("channel input:", tmp)
            ret = wcn.WordNetQuery(tmp)
        wch_output.append(ret)
        if ret is not None:
            nars_input.append(each)


if __name__ == "__main__":

    apriori_knowledge = ["<Query(WordNet, $x) ==> <$x --> [KNOWN]>>.",
                         "<<$label --> X> ==> <$label --> [pos]>>. %0.6;0.99%",
                         "<explosion --> X>.",
                         "<car --> X>.",
                         "<accident --> X>."]  # note this X is for one single case

    nars = Reasoner(1000, 1000)
    for each in apriori_knowledge:
        nars.input_narsese(each, True)

    buff = Buffer(100, nars.memory)
    wcn = WordNetChannel("WCN", buff)

    # global data
    nars_input = ["<X --> [KNOWN]>!", "<?1 --> [pos]>?"]
    nars_output = []
    wch_input = []
    wch_output = []

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
    print(wch_output)
