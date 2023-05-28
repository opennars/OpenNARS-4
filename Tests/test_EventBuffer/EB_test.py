from tqdm import tqdm

from dataset import generate_dataset
from pynars import Config
from pynars.NARS.DataStructures import EventBuffer
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Term, parser, Goal, Compound

Config.Config.task_show_evidence = False

seq1 = ['A', 'B', 'C', 'D']
seq2 = ['X', 'B', 'C', 'Y']
seq3 = ['M', 'B', 'C', 'N']
seqs = [seq1, seq2, seq3]

D_train, _ = generate_dataset(seqs, 100, 100, n_rand=2)
D_train = [parser.parse(each + ".") for each in D_train]

num_slot = 5
num_anticipation = 10
num_operation = 10
num_prediction = 200
num_goal = 10

memory = Memory(100, 100)

EB = EventBuffer(num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory)
EB.update_goal(Goal(Compound.SequentialEvents(*[Term("X"), Term("B"), Term("C"), Term("Y")])))

for i, each in enumerate(tqdm(D_train)):
    EB.step([each])
    if (i + 1) % 100 == 0:
        for i in range(len(EB.predictions)):
            print(EB.predictions[i][1])
        print("----------------------")
        for each in EB.goals:
            print(EB.goals[each])
        print("======================")