# Event buffer

import re
from queue import PriorityQueue
from pynars.Narsese import Task
from pynars.NAL.Inference import local__revision, compositional__conjunstion_composition, \
    temporal__induction_implication, temporal__induction_composition
from pynars.Narsese import parser, Term
from pynars.NARS import Reasoner


class PredictiveImplications(object):
    """
    Each predictive implication is a Narsese sentence like:
        <(&/, A, +3, B) =/> C>. <f,c>
    If more predictions are added when it is full, the prediction with [the lowest expectation] (or other priority
    measurement) will be dropped.
    Add a brand-new prediction is possible.
    Add an already-existed prediction is also possible. This will call a revision.
    """

    def __init__(self, prediction_capacity = 5):
        super(PredictiveImplications, self).__init__()
        self.prediction_capacity = prediction_capacity
        self.reference = {}  # uid to sentence
        self.reverse_reference = {}  # sentence to uid
        self.data = []
        self.uid = 0

    def revise_one_prediction(self, prediction: Task):  # for prediction revision
        if prediction.sentence.word not in self.reverse_reference:
            return
        for i in range(len(self.data)):
            if self.data[i][1].sentence.word == prediction.sentence.word:
                self.data[i][1] = local__revision(self.data[i][1], prediction)
                self.data[i][0] = self.data[i][1].truth.e
                break
        self.data = self.data[self.data[:, 0].argsort()]

    def update(self, prediction: Task):  # add a new prediction
        if prediction.sentence.word not in self.reverse_reference:
            self.uid += 1
            self.reference.update({self.uid: prediction.sentence})
            self.reverse_reference.update({prediction.sentence: self.uid})
            if len(self.data) > self.prediction_capacity:
                tmp = self.data[-1]
                self.data = self.data[:-1]  # sorted from large to small
                tmp_id = self.reverse_reference[tmp.sentence.word]
                self.reference.pop(tmp_id)
                self.reverse_reference.pop(tmp.sentence.word)
            for i in range(len(self.data)):
                if prediction.truth.e > self.data[i][0]:
                    self.data = self.data[:i] + [[prediction.truth.e, prediction]] + self.data[i:]
        else:
            self.revise_one_prediction(prediction)


class EPQ(object):  # expectation priority queue
    """
    A class for candidate compounds. It is an abbreviation of "expectation priority queue".
    This is a priority queue for these candidate compounds based on their expectations.
    It does not have a capacity, but usually the compounds needed are limited, so the "capacity" will be
    applied outside this function.
    """

    def __init__(self):
        super(EPQ, self).__init__()
        self.PQ = PriorityQueue()
        self.size = 0

    def put(self, t: Task):
        self.PQ.put((t.sentence.truth.e, t))
        self.size += 1

    def get(self) -> Task:  # get the compound with the highest priority
        tmp = self.PQ.get()
        if tmp is not None:
            self.size -= 1
            return tmp[1]
        else:
            return

    def empty(self):
        return self.PQ.empty()

    def to_list(self):
        ret = []
        while not self.PQ.empty():
            ret.append(self.get())
        return ret

    def __len__(self):
        return self.size


class Anticipation(object):  # since anticipations are only used for local evaluation, non-necessary to be a "question"

    def __init__(self, parent_prediction: Task, expected_observation: str):
        super(Anticipation, self).__init__()
        self.parent_prediction = parent_prediction
        self.expected_observation = expected_observation

    def satisfied(self):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %1.0;0.9%")
        try:
            self.parent_prediction = local__revision(self.parent_prediction, t)
        except:
            return  # its parent prediction is expired

    def unsatisfied(self):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %0.0;0.9%")
        try:
            self.parent_prediction = local__revision(self.parent_prediction, t)
        except:
            return  # its parent prediction is expired


class Slot(object):
    """
    A class for each time slot in one event buffer.
    It has two parts,
        1: One is for the input observations.
        2: Another is for the expected observations (also called anticipations).
    Both have capacities. If the one for observations is max out, the observation with the lowest priority will be
    dropped. If another is max out, the oldest expectation will be dropped.
    """

    def __init__(self, slot_capacity, index):
        super(Slot, self).__init__()
        self.slot_capacity = slot_capacity
        self.data = []
        self.anticipations = []  # 还是先不要当作问题
        self.anticipations_capacity = self.slot_capacity  # by default
        self.operations = []
        self.operation_capacity = self.slot_capacity  # by default
        self.index = index

    def put(self, t: Task):
        if len(self.data) == self.slot_capacity:
            self.data = self.data[:-1]  # drop the oldest
        for i in range(len(self.data)):
            if t.sentence.truth.e > self.data[i][0]:
                self.data = self.data[:i] + [[t.truth.e, t]] + self.data[i:]
                return
        self.data += [[t.truth.e, t]]
        # pass

    def put_anticipation(self, expected_observation: Anticipation):  # this expected observation is just a string
        self.anticipations.append(expected_observation)
        if len(self.anticipations) > self.anticipations_capacity:
            self.anticipations = self.anticipations[1:]  # drop the oldest

    def put_operation(self, t: Task):
        """
        Since the input task is simply an operation goal, and it is possibly achieved from decomposition. So, its
        truth-value is undefined (or by default).
        """
        if len(self.operations) == self.operation_capacity:
            self.operations = self.operation[:-1]  # drop the oldest
        self.operations.append(t)

    def get(self, rmv = False) -> Task:  # get the one with the highest priority
        if len(self.data) == 0:
            return
        if not rmv:
            return self.data[0][1]
        else:
            tmp = self.data[0][1]
            self.data = self.data[1:]
            return tmp

    def get_other(self):  # get other observations, mainly used for compound generation
        return [self.data[i][1] for i in range(1, len(self.data))]

    def include(self, expected_observation: str) -> bool:  # check whether an anticipation is satisfied
        for each in self.anticipations:
            if each.expected_observation == expected_observation:
                return True
        return False


class EventBuffer(object):
    """
    A class for the event buffer in one channel. It has multiple slots and one array of predictive implications.
    """

    def __init__(self, num_slots = 1, slot_capacity = 5, prediction_capacity = 5, nars: Reasoner = None):
        super(EventBuffer, self).__init__()
        self.reasoner = nars
        # hyper parameters
        self.num_slots = 2 * num_slots + 1
        self.slot_capacity = slot_capacity
        # data initialization
        self.data = [Slot(self.slot_capacity, i) for i in range(-num_slots, 0, 1)] + [Slot(self.slot_capacity, 0)] + [
            Slot(self.slot_capacity, i) for i in range(1, num_slots + 1, 1)]
        self.curr = num_slots
        self.predictions = PredictiveImplications(prediction_capacity)
        # self.compound_operation_reference = {}

    def compound_generation(self, num_limit = 1):
        # the first step
        """include current operations"""
        current_highest, current_other = self.data[self.curr].get(), self.data[self.curr].get_other() + self.data[
            self.curr].operations
        # pass
        previous_highest = [self.data[i].get() for i in range(int((self.num_slots - 1) / 2))]
        # pass
        candidate_compounds = EPQ()
        for each in current_other:  # &&
            cpd = compositional__conjunstion_composition(current_highest, each)
            candidate_compounds.put(cpd)
            # if cpd.term.is_operation:  # restore all compound operations
            #     self.compound_operation_reference.update({cpd.term: (current_highest.term, each.term)})
        for each, tdf in zip(previous_highest, list(range(-int((self.num_slots - 1) / 2)))):  # &/
            cpd = temporal__induction_composition(each, current_highest, time_diff=-tdf)
            candidate_compounds.put(cpd)
            # if cpd.term.is_operation:  # restore all compound operations
            #     self.compound_operation_reference.update({cpd.term: (each.term, -tdf, current_highest.term)})
        if num_limit:
            candidate_compounds = [candidate_compounds.get() for _ in range(min(num_limit, len(candidate_compounds)))]
        else:
            candidate_compounds = candidate_compounds.to_list()
        for each in candidate_compounds:
            self.data[self.curr].put(each)
        # pass
        print("1st step: compound generation FINISHED")

    def local_evaluation(self):
        # the second step
        # check predictions first
        for each in self.predictions:
            tmp = each.sentence.term
            sub = re.search("<\(&\/((, [a-zA-Z])|(, [+][0-9]))+\) =\/>", tmp)  # subject
            if sub is not None:
                sub = sub[0][1:-4]
            obj = re.search(" =\/> .*>.", tmp)  # object
            if obj is not None:
                obj = obj[0][4:-1]
            if sub[1:2] == "&/" and re.match("\+[1-" + str(int((self.num_slots - 1) / 2)) + "]+",
                                             sub.split(", ")[-1][:-1]) is not None:
                # Subject starts with "&/", and ends with "+num", therefore, the anticipation should be allocated to
                # the corresponding time slot.
                pre_term = Term(sub.split(", +")[0] + ')')
                for i in range(len(self.data[self.curr])):
                    if self.data[self.curr][i].sentence.term.equal(pre_term):
                        target_time = int(sub.split(", ")[-1][1:-1])
                        self.data[self.curr + target_time].anticipations.append(obj)
                        self.data[self.curr + target_time].anticipations = list(
                            set(self.data[self.curr + target_time].anticipations))
                        break
            elif sub[1:2] == "&/" or sub[1:2] == "&&":
                # Subject starts with "&/" (or "&&"), but does not end with "+num", therefore,
                # the whole is considered as one whole term
                for i in range(len(self.data[self.curr])):
                    if self.data[self.curr][i].sentence.term.equal(Term(sub)):
                        self.data[self.curr].anticipations.append(obj)
                        self.data[self.curr].anticipations = list(set(self.data[self.curr].anticipations))
        # check anticipations secondly
        rmv_list = []
        for each in self.data[self.curr].anticipations:
            if self.data[self.curr].include(each.expected_observation):
                each.satisfied()
                rmv_list.append(each)
        for each in rmv_list:
            self.data[self.curr].anticipations.remove(each)

    def memory_based_evaluation(self):
        # the third step
        for i in range(len(self.data[self.curr])):
            self.data[self.curr][i] = self.reasoner.memory.accept(self.data[self.curr][i])
        for i in range(len(self.predictions.data)):
            tmp = self.reasoner.memory.accept(self.predictions.data[i])
            self.predictions.data[i] = [[tmp.truth.e, tmp]]

    def prediction_generation(self):
        # the fourth step
        current_highest = self.data[self.curr].get()
        previous_highest = [self.data[i].get() for i in range(-int((self.num_slots - 1) / 2), 0, 1)]
        for i in range(len(previous_highest)):
            self.predictions.update(temporal__induction_implication(current_highest, previous_highest[i]))

    def step(self, new_contents):  # list of tasks
        # un-satisfy the anticipations in the slot to be dropped
        for each in self.data[0].anticipations:
            each.unsatisfied()
        # drop the oldest slot
        self.data = self.data[1:]
        # update the index [may be unnecessary]
        for each in self.data:
            each.index -= 1
        # create a new slot, here we just do the creation, we do not need to any inputs
        self.data.append(Slot(self.slot_capacity, int((self.num_slots - 1) / 2)))
        # input the new contents to the current slot
        for each in new_contents:
            self.data[self.curr].put(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        return self.data[self.curr].get(rmv=True)


class Operation(object):

    def __init__(self):
        super(Operation, self).__init__()

    def execute(self):
        pass


class Operation1(Operation):

    def __init__(self):
        super(Operation1, self).__init__()
        self.name = "^opt1"

    def execute(self):
        print(1)


opt1 = Operation1()


class Operation2(Operation):

    def __init__(self):
        super(Operation2, self).__init__()
        self.name = "^opt2"

    def execute(self):
        print(2)


opt2 = Operation2()


class SensoryMotorChannel(object):

    def __init__(self, num_slots = 1):
        super(SensoryMotorChannel, self).__init__()
        self.event_buffer = EventBuffer(num_slots=num_slots)
        # self.atomic_operation_reference = {}  # should be specified for each specific channel {Term: Operation}
        '''One specification'''
        self.atomic_operation_reference = {Term("^opt1"): opt1, Term("^opt2"): opt2}
        self.operation_agenda = {}
        self.operation_capacity = 100  # usually this will be the number of threads

    def generate_narsese_input(self, t):
        """
        This function will retrieve the new contents in the container at each cycle, so it is unnecessary to have
        this parameter "t".
        :param t: this parameter should not even exist, here this "t" is only used for debugging
        :return: list of Tasks
        """
        if t == 0:
            return [parser.parse("A. \n"), parser.parse("Z. \n")]
            # return [parser.parse("A. \n")]
        elif t == 1:
            return [parser.parse("B. \n")]
        elif t == 2:
            return [parser.parse("C. \n")]
        elif t == 3:
            return []
        elif t == 4:
            return [parser.parse("D. \n")]
        else:
            return []

    def load_operation(self, operation: Task, time_pointer):
        local_pointer = time_pointer
        if not operation.sentence.term.is_compound:  # atomic operation
            self.operation_agenda.update({operation.sentence.term: local_pointer})
        else:
            for each in operation.sentence.term.decomposition:
                if isinstance(each[0], int):
                    local_pointer += each
                else:
                    self.load_operation(each[0], local_pointer)
        '''The operation capacity is for parallel operations. It is not for the operation agenda.'''
        # # TODO: this will be slow, better implementation is to be done
        # if len(self.operation_agenda) > self.operation_capacity:
        #     # after loading all operations, sort them with the time pointer, remove the farthest operation when it is
        #     # overwhelmed
        #     lst = [(self.operation_agenda[each], each) for each in self.operation_agenda]
        #     lst.sort()
        #     lst = lst[:self.operation_capacity]
        #     self.operation_agenda = {each[1]: each[0] for each in lst}

    def exe(self, operations):  # a list of tasks (operation goals specifically)
        # maybe many operations will be forwarded to one channel
        for each in self.operation_agenda:  # update the agenda first
            self.operation_agenda[each] -= 1
        for operation in operations:  # load new operations second
            self.load_operation(operation, 0)
        rmv_list = []
        for each in self.operation_agenda:
            if self.operation_agenda[each] == 0:
                rmv_list.append(each)
        if len(rmv_list) > self.operation_capacity:
            """
            since operations are decomposed, it is hard to say the decomposed tasks' truth-value
            what we can do is to put these tasks to the nearest available time slot
            """
            for _ in range(len(rmv_list) - self.operation_capacity):
                self.operation_agenda.update({rmv_list.pop(): 1})
        for each in rmv_list:
            self.atomic_operation_reference[each].execute()
            self.event_buffer.data[self.event_buffer.curr].put_operation(parser.parse(each.word))
            self.operation_agenda.pop(each)

    def step(self, new_contents, operations):
        self.event_buffer.step(new_contents)
        self.exe(operations)

    # a function JUST for debugging
    def simulator(self):
        for i in range(10):
            self.step(self.generate_narsese_input(i), operation_commands_simulator(i))


def operation_commands_simulator(t):  # it could be replaced with some other functions
    # :return: list of operation goals
    tmp1 = parser.parse("^opt1! \n")
    tmp2 = parser.parse("^opt2! \n")
    if t == 0:
        return [tmp1]
    elif t == 1:
        return []
    elif t == 2:
        return []
    elif t == 3:
        return [tmp2]
    elif t == 7:
        tmp3 = parser.parse("(&&, ^opt1, ^opt2)! \n")
        tmp3.sentence.term.decomposition = [[tmp1], [tmp2]]
        return
    else:
        return []

EXP = SensoryMotorChannel()
EXP.simulator()