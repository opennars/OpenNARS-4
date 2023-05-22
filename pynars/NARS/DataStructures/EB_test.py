from pynars.NARS.DataStructures._py.EventBuffer import EventBuffer
from pynars.NARS.DataStructures._py.Memory import Memory
from dataset import generate_dataset
from pynars.Narsese import Task, Judgement, Term, parser, Goal, Compound

seq1 = ['A', 'B', 'C', 'D']
seq2 = ['X', 'B', 'C', 'Y']
seq3 = ['M', 'B', 'C', 'N']
seqs = [seq1, seq2, seq3]

D_train, _ = generate_dataset(seqs, 10, 10)
D_train = [parser.parse(each + ".") for each in D_train]

num_slot = 5
num_anticipation = 10
num_operation = 10
num_prediction = 20
num_goal = 10

memory = Memory(100, 100)

EB = EventBuffer(num_slot, num_anticipation, num_operation, num_prediction, num_goal, memory)
EB.update_goal(Goal(Compound.SequentialEvents(*[Term("X"), Term("B"), Term("C"), Term("Y")])))

for each in D_train:
    EB.step([each])
    for each in EB.predictions:
        print(EB.predictions[each])
    print("----------------------")
    # for each in EB.goals:
    #     print(EB.goals[each])
    print("======================")
