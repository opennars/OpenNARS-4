from matplotlib import pyplot as plt
from tqdm import tqdm

from Tests.test_EventBuffer.dataset import generate_dataset
from pynars import Config
from pynars.NARS.DataStructures import EventBuffer
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Term, parser, Goal

Config.Config.task_show_evidence = False

seq1 = ['A', 'B', 'C', 'D']
seq2 = ['X', 'B', 'C', 'Y']
# seq3 = ['M', 'B', 'C', 'N']
seqs = [seq1, seq2]

D_train, _ = generate_dataset(seqs, 100, 100, n_rand=2)
D_train_raw = D_train
D_train = [parser.parse(each + ".") for each in D_train]

num_slot = 5
num_anticipation = 10
num_operation = 10
num_prediction = 1000
num_goal = 10

memory = Memory(100, 100)

EB = EventBuffer(num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory)
# EB.update_goal(Goal(Compound.SequentialEvents(*[Term("X"), Term("B"), Term("C"), Term("Y")])))
EB.update_goal(Goal(Term("Y")))

for i, each in enumerate(tqdm(D_train)):
    EB.step([each])
    if (i + 1) % 100 == 0:
        predictions = sorted(EB.predictions, key=lambda x: x[1].truth.c)
        # for each_p in predictions:
        #     print(each_p[1])

plt.figure()
plt.grid()
plt.plot(EB.plot)
plt.show()
