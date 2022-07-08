# Event buffer

import re
import heapq
# from queue import PriorityQueue
from typing import List

from pynars.Narsese import Task
from pynars.NAL.Inference import local__revision, compositional__conjunstion_composition, \
    temporal__induction_implication, temporal__induction_composition
from pynars.Narsese import parser, Term, Statement, Compound, Interval, Budget, Sentence
from pynars.NARS.DataStructures import Memory, Judgement
from pynars.NAL.Functions import Stamp_merge, Truth_intersection, Truth_deduction, Budget_merge
from pynars.NARS import Reasoner
from pynars import Global


def priority(t: Task):
    return t.budget.summary * t.truth.e / t.sentence.term.complexity


class PriorityQueue(object):
    """
    Maybe this is not a good name, since it not only supports to get the maximum, it also needs to get the minimum,
    and it needs to change the priority value of existed instance and maintain the order.
    """

    def __init__(self, capacity = 5):
        super(PriorityQueue, self).__init__()
        self.capacity = capacity
        self.data = []
        """
        a sorted list of lists, [priority_value, prediction], sorted from large to small by a task's priority 
        value, which is NOT its truth-value.
        It is used for "observations in slot", "anticipations in slot", "predictive implications".
        For "operations in slot", they will be processed specially.
        """

    def update(self, priority_value, t: Task):
        """
        If there is a task with the same statement in self.data, replace the old one with the new one.
        After adding a task, if self.data is maxing out, drop the one with the lowest priority value.
        """
        for j in range(len(self.data)):
            if t.sentence.term.equal(self.data[j][1].sentence.term):
                self.data = self.data[:j] + self.data[j + 1:]  # possible data leak
                break
        for j in range(len(self.data)):
            if priority_value > self.data[j][0]:
                self.data = self.data[:j] + [[priority_value, t]] + self.data[j:]
                if len(self.data) > self.capacity:
                    self.data = self.data[:self.capacity]
                return
        self.data += [[priority_value, t]]
        if len(self.data) > self.capacity:
            self.data = self.data[:self.capacity]
        return

    def get_highest(self, rmv = False):
        """
        Return the [priority-task pair] with the highest priority value, used for compound/prediction generation,
        when rmv = True, it will pop the task with the highest truth-value.
        """
        if len(self.data) == 0:
            return None
        if not rmv:
            return self.data[0]
        else:
            tmp = self.data[0]
            self.data = self.data[1:]
            return tmp

    def get_others(self):
        if len(self.data) <= 1:
            return None
        else:
            return [each for each in self.data[1:]]

    def is_empty(self):
        return len(self.data) == 0


class Anticipation(object):
    """
    Anticipations have two parts, its parent prediction (where this anticipation is from), and its expected
    observation: Task. The expected observation's truth-value is generated from a known observation and its
    parent prediction using the deductive rule.

    When an anticipation really appears, its parent prediction's truth-value and priority value will be both increased,
    (or the truth-value will be increased and the priority value will just be maintained.) and the observation will be
    revised with the corresponding anticipation.

    When an anticipation does not appear, its parent prediction's truth-value and priority value will be both decreased.
    """

    def __init__(self, parent_prediction: Task, expected_observation: Task):
        super(Anticipation, self).__init__()
        self.parent_prediction = parent_prediction
        self.expected_observation = expected_observation

    def satisfied(self, predictions: PriorityQueue):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %1.0;0.9% \n")
        for each in predictions.data:
            if each[1].sentence.term.equal(self.parent_prediction.sentence.term):
                t = local__revision(task=self.parent_prediction, belief=t,
                                    budget_tasklink=self.parent_prediction.budget,
                                    budget_termlink=Budget(
                                        min(1.0, self.parent_prediction.budget.priority * 1.2),
                                        min(1.0, self.parent_prediction.budget.durability * 1.2),
                                        min(1.0, self.parent_prediction.budget.quality * 1.2)))
                predictions.update(priority(t), t)  # replacement

    def unsatisfied(self, predictions: PriorityQueue):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %0.0;0.9% \n")
        for each in predictions.data:
            if each[1].sentence.term.equal(self.parent_prediction.sentence.term):
                t = local__revision(task=self.parent_prediction, belief=t,
                                    budget_tasklink=self.parent_prediction.budget,
                                    budget_termlink=Budget(
                                        self.parent_prediction.budget.priority * 0.8,
                                        self.parent_prediction.budget.durability * 0.8,
                                        self.parent_prediction.budget.quality * 0.8))
                predictions.update(priority(t), self.parent_prediction)  # replacement


class PriorityQueueAnticipations(PriorityQueue):
    """
    A PriorityQueue for anticipations, since anticipations need another (slightly different) way for updating.
    """

    def __init__(self, capacity = 5):
        super(PriorityQueueAnticipations, self).__init__(capacity)
        self.capacity = capacity
        self.data = []

    def update(self, priority_value, a: Anticipation):
        for j in range(len(self.data)):
            if a.expected_observation.sentence.term.equal(self.data[j][1].expected_observation.sentence.term):
                self.data = self.data[:j] + self.data[j + 1:]  # possible data leak
                break
        for j in range(len(self.data)):
            if priority_value > self.data[j][0]:
                self.data = self.data[:j] + [[priority_value, a]] + self.data[j:]
                if len(self.data) > self.capacity:
                    self.data = self.data[:self.capacity]
                    return
        self.data += [[priority_value, a]]
        if len(self.data) > self.capacity:
            self.data = self.data[:self.capacity]
            return


class Slot(object):
    """
    For each time slot in one buffer.
    It has three parts,
        1: One is for the input observations.
        2: One is for the expected observations (also called anticipations).
        3: One is for the operations just carried out.
    Here is the compound generation logic,
        1: For all input observations, keep using PriorityQueue.get_highest(rmv=True) till the priority values have a
        relatively large difference. Then generate a concurrent compound (&|). Keep doing till all observations are
        scanned.
        2: After step 1 above, we still need to process the past observations and operations. For operations, they are
        used to generate a big compound operations and this compound operation is further combined with the observation
        with the largest priority value. Note that this will not eliminate both, after this generation, we will have 3,
        compounds, "a compound for observations", "a compound for operations" and "a compound for observations and
        operations".
        3: After the above step, we can process the past observations. Though in each past slot, the above three types
        of compounds will also be generated, but only one will be of the highest priority. Therefore, we need to further
        generate 3*n compounds (n is the number of the past slots). This is a relative big number, but it is linear.
    All have capacities.
        1: If the one for observations is max out, the observation with the lowest priority (expectation here) will be
        dropped.
        2: If the one for anticipations is max out, the oldest anticipation will be dropped.
        3: If the one for operations is max out, the remaining operations will find the nearest available slot in the
        future.
    """

    def __init__(self, observation_capacity = 5, anticipation_capacity = 5, operation_capacity = 5):
        super(Slot, self).__init__()
        self.observation_capacity = observation_capacity  # num of observations
        self.anticipation_capacity = anticipation_capacity  # num of anticipations
        self.operation_capacity = operation_capacity  # num of operations
        self.concurrent_observations = PriorityQueue(observation_capacity)
        self.historical_observations = PriorityQueue(observation_capacity)
        self.anticipations = PriorityQueueAnticipations(anticipation_capacity)
        self.operations = []  # to-do list
        self.highest_concurrent_compound = None
        # compound generated from concurrent events (&|) with the highest priority
        self.highest_historical_compound = None
        """compound generated from concurrent compounds and past concurrent compounds with the highest priority"""
        self.highest_compound = None  # report compound

    def put_concurrent_observation(self, t: Task):
        """
        Put an observation to self.observations. Observations need a priority value, which is the summary of its budget.
        """
        self.concurrent_observations.update(priority(t), t)

    def put_historical_observation(self, t: Task):
        """
        Put an observation to self.observations. Observations need a priority value, which is the summary of its budget.
        """
        self.historical_observations.update(priority(t), t)

    def put_anticipation(self, a: Anticipation):
        """
        self.anticipations is also a PriorityQueue, with each anticipation's budget's summary as its priority value,
        except for that, each anticipation's expected observation is a task, generated using inference rules, so it can
        have the correct budget and truth-value.
        """
        self.anticipations.update(priority(a.expected_observation), a)

    def put_operation(self, o: Task):
        """
        Since self.operations is just a list, all inside operations will have a default truth-value and priority value.
        """
        self.operations.append(o)

    def check_anticipations(self, predictions: PriorityQueue):  # check whether some anticipations are satisfied
        """
        Check all observations on all anticipations:
            1: An observation may match one anticipation, this will *.satisfied() the anticipation.
            2: An observation may match no anticipations, this is called one "unexpected" observation.
            3: In the end, some anticipations are not satisfied, this will *.unsatisfied() these anticipations.
        """
        observation_updating_list = []
        unexpected_observations = []
        satisfied_anticipations = []
        for j, each_observation in enumerate(self.concurrent_observations.data):
            matched = False
            for k, each_anticipation in enumerate(self.anticipations.data):
                if k in satisfied_anticipations:  # already satisfied, cannot be satisfied again, pass
                    continue
                if each_anticipation[1].expected_observation.sentence.term.equal(each_observation[1].sentence.term):
                    """
                    A satisfied anticipation.
                    Corresponding observations will be revised.
                    Corresponding anticipation will be revised (truth_value and priority), which is by *.satisfied()
                    """
                    revised_observation = local__revision(each_observation[1],
                                                          each_anticipation[1].expected_observation)
                    observation_updating_list.append(revised_observation)
                    each_anticipation[1].satisfied(predictions)
                    matched = True
                    satisfied_anticipations.append(k)
                    break
            if not matched:
                unexpected_observations.append(each_observation[1])
                # unexpected observations' priority will also be increased
        for j in range(len(self.anticipations.data)):
            if j not in satisfied_anticipations:
                self.anticipations.data[j][1].unsatisfied(predictions)
        """
        Unsatisfied anticipations will be removed, their corresponding parent predictions' priority will be decreased,
        which is by *.unsatisfied()
        """
        for each in observation_updating_list:
            self.put_concurrent_observation(each)
        for each in unexpected_observations:
            each.budget = Budget(min(1.0, each.budget.priority * 1.2),
                                 min(1.0, each.budget.durability * 1.2),
                                 min(1.0, each.budget.quality * 1.2))
            self.put_concurrent_observation(each)
        # do the same thing for self.historical_observations
        observation_updating_list = []
        unexpected_observations = []
        for j, each_observation in enumerate(self.historical_observations.data):
            matched = False
            for k, each_anticipation in enumerate(self.anticipations.data):
                if k in satisfied_anticipations:  # already satisfied, cannot be satisfied again, pass
                    continue
                if each_anticipation[1].expected_observation.sentence.term.equal(each_observation[1].sentence.term):
                    """
                    A satisfied anticipation.
                    Corresponding observations will be revised.
                    Corresponding anticipation will be revised (truth_value and priority), which is by *.satisfied()
                    """
                    revised_observation = local__revision(each_observation[1],
                                                          each_anticipation[1].expected_observation)
                    observation_updating_list.append(revised_observation)
                    each_anticipation[1].satisfied(predictions)
                    matched = True
                    satisfied_anticipations.append(k)
                    break
            if not matched:
                unexpected_observations.append(each_observation[1])
                # unexpected observations' priority will also be increased
        for j in range(len(self.anticipations.data)):
            if j not in satisfied_anticipations:
                self.anticipations.data[j][1].unsatisfied(predictions)
        """
        Unsatisfied anticipations will be removed, their corresponding parent predictions' priority will be decreased,
        which is by *.unsatisfied()
        """
        for each in observation_updating_list:
            self.put_historical_observation(each)
        for each in unexpected_observations:
            each.budget = Budget(min(1.0, each.budget.priority * 1.2),
                                 min(1.0, each.budget.durability * 1.2),
                                 min(1.0, each.budget.quality * 1.2))
            self.put_historical_observation(each)


class EventBuffer(object):
    """
    A class for the event buffer in one channel. It has multiple slots and a set of predictive implications
    (also called predictions).
    """

    def __init__(self, num_slots = 2, observation_capacity = 5, anticipation_capacity = 5, operation_capacity = 5,
                 prediction_capacity = 5, memory: Memory = None):
        super(EventBuffer, self).__init__()
        self.memory = memory
        self.observation_capacity = observation_capacity
        self.anticipation_capacity = anticipation_capacity
        self.operation_capacity = operation_capacity
        # num_slots is for the number of slots on one side
        self.num_slots_one_side = num_slots
        # self.num_slots is for the number of slots on both sides and the middle
        self.num_slots = 2 * num_slots + 1
        self.data = [Slot(observation_capacity, anticipation_capacity, operation_capacity) for _ in
                     range(self.num_slots)]
        self.curr = num_slots  # the index of the slot in the middle (also called the "current" slot)
        self.predictions = PriorityQueue(prediction_capacity)

    def compound_generation(self):
        # the first step
        """
        Chronologically,
            1: Commanded operations will be carried out first, and this will affect the observations to get.
            2: Initial (atomic) observations will be gathered.
            3: Compounds will be generated among atomic observations and observations.

            *** This function will only cover the third step.

        Two kinds of compounds will be generated (&|, &/), but no matter what, only two terms will be used to generate
        one compound. But it is possible to generate ((A, B), C) which is a triplet, or larger compound.
        """
        obs_with_close_priority: List[List] = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
        if len(obs_with_close_priority) == 0:
            print("1st step: compound generation FINISHED, no observations")
            return
        while not self.data[self.curr].concurrent_observations.is_empty():
            tmp_event = self.data[self.curr].concurrent_observations.get_highest(rmv=True)
            if abs(tmp_event[0] - obs_with_close_priority[0][0]) <= 0.05:
                obs_with_close_priority.append(tmp_event)
            else:
                tmp = obs_with_close_priority[0][1]
                obs_with_close_priority = obs_with_close_priority[1:]
                for each in obs_with_close_priority:
                    tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
                self.data[self.curr].put_concurrent_observation(tmp)
                obs_with_close_priority = [tmp_event]
        tmp = obs_with_close_priority[0]
        obs_with_close_priority = obs_with_close_priority[1:]
        for each in obs_with_close_priority:
            tmp = temporal__induction_composition(tmp[1], each[1], time_diff=0)
        self.data[self.curr].put_concurrent_observation(tmp)
        self.data[self.curr].highest_concurrent_compound = self.data[self.curr].concurrent_observations.get_highest()

        """
        Concurrent compounds generation finished, which are restored in self.data[self.curr].concurrent_observations.
        The one with the highest compound is copied to self.data[self.curr].highest_concurrent_compound
        """

        for j in range(self.num_slots_one_side):
            if self.data[j].highest_concurrent_compound is not None:
                tmp = temporal__induction_composition(self.data[j].highest_concurrent_compound[1],
                                                      self.data[self.curr].highest_concurrent_compound[1],
                                                      time_diff=self.curr - j)
                self.data[self.curr].put_historical_observation(tmp)
            if self.data[j].highest_historical_compound is not None:
                tmp = temporal__induction_composition(self.data[j].highest_historical_compound[1],
                                                      self.data[self.curr].highest_concurrent_compound[1],
                                                      time_diff=self.curr - j)
                self.data[self.curr].put_historical_observation(tmp)
        self.data[self.curr].highest_historical_compound = self.data[self.curr].historical_observations.get_highest()

        print("1st step: compound generation FINISHED")

    def local_evaluation(self):
        # the second step
        """
        Predictions will be checked first and satisfied predictions will fire.
        These predictions are Tasks, but initialized with Statement, not simply Term.
        """
        # Prediction checking
        for each_prediction in self.predictions.data:
            if isinstance(each_prediction[1].sentence.term.subject.components[-1], Interval):
                """
                When a term is like (&/, A, +3), which is allowed in pynars but not in new version opennars, 
                since this Interval cannot be automatically generated, we need to convert it to A and +3.
                When A is observed, its consequence will be expected after 3 time slots.
                """
                other_components = each_prediction[1].sentence.term.subject.components[:-1]
                if len(other_components) == 1:
                    subject = other_components[0]
                else:
                    subject = Term("(&/, " + " ,".join([each.word for each in other_components]) + ")")
            else:
                subject: Term = each_prediction[1].sentence.term.subject
            predicate: Term = each_prediction[1].sentence.term.predicate
            for each_observation in self.data[self.curr].concurrent_observations.data:
                if each_observation[1].sentence.term.equal(subject):
                    """
                    each_observation[1]: Task, e.g., A, <f,c>
                    each_prediction[1]: Task, e.g., A =/> B <f,c>
                    """
                    predicated_observation_truth_value = Truth_deduction(each_prediction[1].truth,
                                                                         each_observation[1].truth)
                    predicated_observation_budget = Budget_merge(each_prediction[1].budget,
                                                                 each_observation[1].budget)
                    predicted_observation = parser.parse("$" + str(predicated_observation_budget.priority) + ";" + str(
                        predicated_observation_budget.durability) + ";" + str(
                        predicated_observation_budget.quality) + "$ " + predicate.word + ". %" + str(
                        predicated_observation_truth_value.f) + ";" + str(
                        predicated_observation_truth_value.c) + "% \n")
                    self.data[self.curr].put_anticipation(Anticipation(each_prediction[1], predicted_observation))
            # do the same thing for self.[data][self.curr].historical_observations
            for each_observation in self.data[self.curr].historical_observations.data:
                if each_observation[1].sentence.term.equal(subject):
                    """
                    each_observation[1]: Task, e.g., A, <f,c>
                    each_prediction[1]: Task, e.g., A =/> B <f,c>
                    """
                    predicated_observation_truth_value = Truth_deduction(each_prediction[1].truth,
                                                                         each_observation[1].truth)
                    predicated_observation_budget = Budget_merge(each_prediction[1].budget,
                                                                 each_observation[1].budget)
                    predicted_observation = parser.parse("$" + str(predicated_observation_budget.priority) + ";" + str(
                        predicated_observation_budget.durability) + ";" + str(
                        predicated_observation_budget.quality) + "$ " + predicate.word + ". %" + str(
                        predicated_observation_truth_value.f) + ";" + str(
                        predicated_observation_truth_value.c) + "% \n")
                    self.data[self.curr].put_anticipation(Anticipation(each_prediction[1], predicted_observation))
        # Anticipation checking
        self.data[self.curr].check_anticipations(self.predictions)
        print("2nd step: local evaluation FINISHED")

    def memory_based_evaluation(self):
        # the third step
        """
        Check observations and update their priority values (expectation used here) for prediction generation.
        Update the priority value (expectation used here) for all predictions.

        This updating will also apply to memory.
        """

        # 这不debug一定是会有问题的

        concurrent_observation_updating_list = []
        for j in range(len(self.data[self.curr].concurrent_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].concurrent_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].concurrent_observations.data[j][1]
                    tmp.budget = Budget(min(1.0, tmp.budget.priority*1.2), min(1.0, tmp.budget.durability*1.2), min(1.0, tmp.budget.quality*1.2))
                    concurrent_observation_updating_list.append(tmp)
        historical_observation_updating_list = []
        for j in range(len(self.data[self.curr].historical_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].historical_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].historical_observations.data[j][1]
                    tmp.budget = Budget(min(1.0, tmp.budget.priority * 1.2), min(1.0, tmp.budget.durability * 1.2),
                                        min(1.0, tmp.budget.quality * 1.2))
                    historical_observation_updating_list.append(tmp)
        for each in concurrent_observation_updating_list:
            self.data[self.curr].put_concurrent_observation(each)
        for each in historical_observation_updating_list:
            self.data[self.curr].put_historical_observation(each)

        print("3nd step: memory-based evaluation FINISHED")

    def prediction_generation(self):
        # the fourth step
        # figure out the highest compound
        if self.data[self.curr].highest_concurrent_compound is not None \
                and self.data[self.curr].highest_historical_compound is not None:
            if priority(self.data[self.curr].highest_concurrent_compound[1]) > priority(
                    self.data[self.curr].highest_historical_compound[1]):
                self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
            else:
                self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
        elif self.data[self.curr].highest_concurrent_compound is not None:
            self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
        elif self.data[self.curr].highest_historical_compound is not None:
            self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
        # generate predictions
        for j in range(self.num_slots_one_side):
            if self.data[j].highest_concurrent_compound is not None:
                tmp = temporal__induction_implication(self.data[j].highest_concurrent_compound[1],
                                                      self.data[self.curr].highest_compound[1],
                                                      time_diff=self.curr - j)
                self.predictions.update(priority(tmp), tmp)
            if self.data[j].highest_historical_compound is not None:
                tmp = temporal__induction_implication(self.data[j].highest_historical_compound[1],
                                                      self.data[self.curr].highest_compound[1],
                                                      time_diff=self.curr - j)
                self.predictions.update(priority(tmp), tmp)
        print("4th step: prediction generation FINISHED")

    def step(self, new_contents):  # list of tasks
        """
        The new contents are resulted from the operations carried out
        """
        for each in new_contents:
            self.data[self.curr].put_concurrent_observation(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        print(">" + "=" * 73)
        tmp = self.data[self.curr].highest_compound[1]
        if tmp is not None:
            print("Task forwarded " + tmp.sentence.word)
            print("-" * 74)
        return tmp  # for the next buffer (overall exp buffer)


"""
operation def
"""


class Operation1(object):

    def __init__(self):
        super(Operation1, self).__init__()
        self.name = "^opt1"

    def execute(self):
        print("---Operation 1 executed---")


opt1 = Operation1()


class Operation2(object):

    def __init__(self):
        super(Operation2, self).__init__()
        self.name = "^opt2"

    def execute(self):
        print("---Operation 2 executed---")


opt2 = Operation2()
"""
operation def end
"""


class SensoryMotorChannel(object):
    """
    A channel contains:
        1: Atomic operations.
        2: An operation agenda, which is an agenda to carry out operations. This agenda gets commends from memory (from
        operation goals).
        3: An event buffer.
        4: A mechanism to convert information from sensors into Narsese.
    """

    def __init__(self, event_buffer):
        super(SensoryMotorChannel, self).__init__()
        self.event_buffer = event_buffer
        """
        This specification is just one example.
        """
        self.atomic_operation_reference = {"^opt1": opt1, "^opt2": opt2}
        self.operation_agenda = {}
        self.operation_capacity = 100  # usually this will be the number of threads

    def generate_narsese_input(self, t):
        """
        This function will retrieve the new contents in the "container" at each cycle, which is automatic,
        so it is unnecessary to have this parameter "t". Here "t" is used for simulation, return tasks at pre-defined
        time point "t".
        """
        pass

    def load_operation(self, operation: Task, time_pointer):
        """
        Since operations are not necessarily (or even practically) be executed when they arrive at this channel.
        They need to be loaded into the buffer.
        """
        local_pointer = time_pointer
        if not operation.sentence.term.is_compound:  # atomic operation
            self.operation_agenda.update({operation.sentence.term: local_pointer})
        else:
            for each in operation.sentence.term.decomposition:
                if isinstance(each[0], int):
                    local_pointer += each[0]
                else:
                    self.load_operation(each[0], local_pointer)

    def exe(self, operations):  # maybe many operations will be forwarded to one channel
        """
        :param operations: a list of tasks (operation goals specifically)
        """
        for each in self.operation_agenda:  # update the agenda first
            self.operation_agenda[each] -= 1
        for operation in operations:  # load new operations second
            self.load_operation(operation, 0)
        """
        Operations just to be carried out is in this list, since we need to consider whether the number of such 
        operations is larger than the capacity, we do not execute them instantly.
        Those operations max out will be forwarded to the nearest available future slot.
        """
        rmv_list = []
        for each in self.operation_agenda:
            if self.operation_agenda[each] == 0:
                rmv_list.append(each)
        if len(rmv_list) > self.operation_capacity:
            for _ in range(len(rmv_list) - self.operation_capacity):
                self.operation_agenda.update({rmv_list.pop(): 1})
        # drop the oldest slot
        self.event_buffer.data = self.event_buffer.data[1:]
        # create a new slot
        self.event_buffer.data.append(
            Slot(self.event_buffer.observation_capacity, self.event_buffer.anticipation_capacity,
                 self.event_buffer.operation_capacity))
        for each in rmv_list:
            self.atomic_operation_reference[each].execute()
            self.event_buffer.data[self.event_buffer.curr].put_operation(parser.parse("^" + each.word + "."))
            self.operation_agenda.pop(each)

    def step(self, t, operations = []):
        """
        Always execute operations first
        """
        self.exe(operations)
        self.event_buffer.step(self.generate_narsese_input(t))
        tsk = self.event_buffer.data[self.event_buffer.curr].highest_compound[1]
        self.event_buffer.memory.accept(tsk)
        for j, each in enumerate(self.event_buffer.predictions.data):
            print("Prediction  " + str(j) + " | ", each[1].sentence.word, " | ", each[1].truth)
        print("-" * 74)


class Channel1(SensoryMotorChannel):

    def __init__(self, event_buffer):
        super(Channel1, self).__init__(event_buffer)

    def generate_narsese_input(self, t):
        if t % 2 == 1:
            return [parser.parse("A. \n"), parser.parse("a. \n")]
        else:
            return [parser.parse("B. \n"), parser.parse("b. \n")]


class Channel2(SensoryMotorChannel):

    def __init__(self, event_buffer):
        super(Channel2, self).__init__(event_buffer)

    def generate_narsese_input(self, t):
        if t % 2 == 1:
            return [parser.parse("a. \n")]
        else:
            return [parser.parse("b. \n")]


nars = Reasoner(100, 100)
e1 = EventBuffer(num_slots=2, memory=nars.memory)
e2 = EventBuffer(num_slots=2, memory=nars.memory)
c1 = Channel1(e1)
c2 = Channel2(e2)

for i in range(50):
    c1.step(i)
    # c2.step(i)

print(1)
