import re
import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from modules import FirstModule, SecondModule, ThirdModule, Final, Observer
from pynars.Console import run_line
from pynars.utils.tools import rand_seed
from pynars.utils.Print import out_print, PrintType
from pynars.NARS import Reasoner as Reasoner
import matplotlib.pyplot as plt


'''
0.92655255
0.21196429
'''


device = torch.device('cuda' if torch.cuda.is_available else 'cpu')
print(device)

transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Resize([56, 56])])

data_train = datasets.MNIST(root="./data/",
                            transform=transform,
                            train=True,
                            download=True)

data_test = datasets.MNIST(root="./data/",
                           transform=transform,
                           train=False)

data_loader_train = torch.utils.data.DataLoader(dataset=data_train,
                                                batch_size=64,
                                                shuffle=True)

data_loader_test = torch.utils.data.DataLoader(dataset=data_test,
                                               batch_size=64,
                                               shuffle=True)

# NN spec

epoch = 100
m1, m2, m3, fc, ob = FirstModule().to(device), SecondModule().to(device), ThirdModule().to(device), Final().to(
    device), Observer().to(device)
op1, op2, op3, op4 = torch.optim.SGD(m1.parameters(), lr=1e-3), torch.optim.SGD(m2.parameters(), lr=1e-3), \
                     torch.optim.SGD(m3.parameters(), lr=1e-3), torch.optim.SGD(fc.parameters(), lr=1e-3)
loss_function = nn.CrossEntropyLoss()

testing_acc = []


def small_scale_test(n):
    count = 0
    acc = 0
    with torch.no_grad():
        for x, y in data_loader_test:
            if count == n:
                return acc / (n * 64)
            tmp = m3(m2(m1(x.to(device))))
            yp = fc(tmp)
            acc += (y == torch.argmax(yp, 1)).sum().item()
            count += 1


def active_symbols(yob):
    return "(&&," + ",".join(["s" + str(each) for each in np.argwhere(yob > 0.5).squeeze().tolist()]) + ")"


# NARS spec

NARS_ON = True
if NARS_ON:
    steps = 100
    seed = 137
    rand_seed(137)
    out_print(PrintType.COMMENT, f'rand_seed={seed}', comment_title='Setup')
    out_print(PrintType.COMMENT, 'Init...', comment_title='NARS')
    nars = Reasoner(1000, 1000)
    op_container = []


def handle_lines(container: list, nars: Reasoner, lines: str, show = False):
    tasks_lines = []
    for line in lines.split('\n'):
        if len(line) == 0: continue

        tasks_line = run_line(nars, line)
        if tasks_line is not None:
            tasks_lines.extend(tasks_line)

    for tasks_line in tasks_lines:
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = tasks_line

        for task in tasks_derived:
            if task.is_operation and task.sentence.word[0] == "^":  # atomic executable operations
                container.append(task)
            else:  # compound executable operation
                pattern = "[(]&&(, *\^[a-zA-Z]+)+[)]."
                if re.match(pattern, task.sentence.word) is not None:
                    container.append(task)

        if show:
            for task in tasks_derived: out_print(PrintType.OUT, task.sentence.repr(), *task.budget)

            if judgement_revised is not None: out_print(PrintType.OUT, judgement_revised.sentence.repr(),
                                                        *judgement_revised.budget)
            if goal_revised is not None: out_print(PrintType.OUT, goal_revised.sentence.repr(), *goal_revised.budget)
            if answers_question is not None:
                for answer in answers_question: out_print(PrintType.ANSWER, answer.sentence.repr(), *answer.budget)
            if answers_quest is not None:
                for answer in answers_quest: out_print(PrintType.ANSWER, answers_quest.sentence.repr(),
                                                       *answers_quest.budget)
            if task_executed is not None:
                out_print(PrintType.EXE,
                          f'{task_executed.term.repr()} = '
                          f'{str(task_operation_return) if task_operation_return is not None else None}')


num_training = 1000
num_testing = 700

for _ in range(epoch):
    # get pre/post
    if NARS_ON:
        yob = 0
        train_count = 0
        for x, y in data_loader_train:
            if train_count == num_training:
                break
            train_count += 1
            tmp = m3(m2(m1(x.to(device))))
            # yp = fc(tmp)
            yob += np.array(torch.sum(ob(tmp), 0).to("cpu").detach())
            # pre = active_symbols(yob)
            # if len(pre) == 0:
            #     continue
            # op_container = []
            # handle_lines(op_container, nars, pre + ".\n 50 \n")
            # if len(op_container) != 0:
            #     print("have something reasoned")
            # for _ in range(5):
            #     op_container.append("(&&,^" + ",^".join(
            #         np.random.choice(["op1", "op2", "op3", "op4"], np.random.randint(2,4), replace=False).tolist()) + ")")
            # post = np.random.choice(op_container, 1)[0]
            # freq = small_scale_test(n=1)
            # conf = 0.3  # by default
            # judgment = "<" + pre + "=/>" + post + ">. %" + str(freq) + ";" + str(conf) + "%\n"
            # handle_lines([], nars, judgment + "\n 200 \n")
            # loss = loss_function(yp, y)
            # op1.zero_grad(), op2.zero_grad(), op3.zero_grad(), op4.zero_grad()
            # loss.backward()
            # if "op1" in post:
            #     op1.step()
            # if "op2" in post:
            #     op2.step()
            # if "op3" in post:
            #     op3.step()
            # if "op4" in post:
            #     op4.step()

        pre = active_symbols(yob / (64 * len(data_loader_train)))

        if len(pre) == 5:
            continue
        op_container = []
        handle_lines(op_container, nars, pre + ". :|: \n 5000 \n")
        if len(op_container) != 0:
            print("have something reasoned")
        for _ in range(5):
            op_container.append("(&&,^" + ",^".join(
                np.random.choice(["op1", "op2", "op3", "op4"], np.random.randint(2, 4), replace=False).tolist()) + ")")
        post = np.random.choice(op_container, 1)[0]

    # training

    train_count = 0
    for x, y in data_loader_train:
        if train_count == num_training:
            break
        train_count += 1
        tmp = m3(m2(m1(x.to(device))))
        yp = fc(tmp)
        loss = loss_function(yp, y.to(device))
        op1.zero_grad(), op2.zero_grad(), op3.zero_grad(), op4.zero_grad()
        loss.backward()
        if NARS_ON:
            if "op1" in post:
                op1.step()
            if "op2" in post:
                op2.step()
            if "op3" in post:
                op3.step()
            if "op4" in post:
                op4.step()
        else:
            op1.step(), op2.step(), op3.step(), op4.step()

    # testing

    with torch.no_grad():
        acc = 0
        test_count = 0
        for x, y in data_loader_test:
            if test_count == num_testing:
                break
            test_count += 1
            tmp = m3(m2(m1(x.to(device))))
            yp = fc(tmp)
            acc += (y == torch.argmax(yp.to("cpu"), 1)).sum().item()
        freq = acc / (64 * len(data_loader_test))
        testing_acc.append(freq)
        print(freq)
    if NARS_ON:
        conf = 0.9  # by default
        judgment = "<" + pre + "=/>" + post + ">. %" + str(freq) + ";" + str(conf) + "%\n"
        handle_lines([], nars, judgment + "\n 10000 \n")

# handle_lines(op_container, nars, "(&&,^A,^B,^C).\n(&&,^A,^B,^C)?\n10")
# print(op_container)

plt.plot(testing_acc)
