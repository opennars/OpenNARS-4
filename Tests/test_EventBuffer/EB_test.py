import random

import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

from Tests.test_EventBuffer.dataset import generate_dataset
from pynars import Config
from pynars.NARS.DataStructures import EventBuffer
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Term, parser, Goal, Judgement, Task

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
num_prediction = 10000
num_goal = 10

memory = Memory(10000, 100)

EB = EventBuffer(num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory)
# EB.update_goal(Goal(Compound.SequentialEvents(*[Term("X"), Term("B"), Term("C"), Term("Y")])))
EB.update_goal(Goal(Term("Y")))

samples = [chr(i) for i in range(65, 91)]

for i, each in enumerate(tqdm(D_train)):
    EB.step([each, Task(Judgement(Term(np.random.choice(samples, 1).item())))])
    # if random.random() > 0.5:
    #     EB.step([Task(Judgement(Term(np.random.choice(samples, 1).item()))), each])
    # else:
    #     EB.step([each, Task(Judgement(Term(np.random.choice(samples, 1).item())))])
    if (i + 1) % 100 == 0:
        predictions = sorted(EB.predictions, key=lambda x: x[1].truth.c)

for each_p in predictions:
    if (each_p[1].truth.f > 0.8 and each_p[1].truth.c > 0.5) or "(&/, X, B, C)=/>" in each_p[0]:
        print(each_p[1])

plt.figure()
plt.grid()
plt.plot(EB.plot)
plt.ylabel("Accuracy")
plt.xlabel("Steps")
plt.title("Prediction Accuracy of Event Buffer ")
plt.axhline(0.5, color="r")
plt.show()
