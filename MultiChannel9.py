import random
import re
import heapq
# from queue import PriorityQueue
from typing import List
from pynars.Narsese import Task
from pynars.NAL.Inference import local__revision, compositional__conjunstion_composition, \
    temporal__induction_implication, temporal__induction_composition
from pynars.Narsese import parser, Term, Statement, Compound, Interval, Budget, Sentence
from pynars.NARS.DataStructures import Memory, Judgement, Concept
from pynars.NAL.Functions import Stamp_merge, Truth_intersection, Truth_deduction, Budget_merge
from pynars import Global
from pynars.utils.tools import rand_seed
from pynars.utils.Print import out_print, PrintType
from pynars import Config
from pynars.NARS.InferenceEngine import GeneralEngine, TemporalEngine
import pynars.NARS.MentalOperation as MentalOperation
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from pynars.NARS import Reasoner as ReasonerSC
from typing import Tuple

compound_generation_threshold = 0.01
show_predictions = False
show_inference_result = True
show_task_forwarded = False
prediction_as_observation = False
show_concept_selected = False
visualize_concepts = False

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
                                        min(0.99, self.parent_prediction.budget.priority * 1.2),
                                        min(0.99, self.parent_prediction.budget.durability * 1.2),
                                        min(0.99, self.parent_prediction.budget.quality * 1.2)))
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
        # self.concurrent_implications = PriorityQueue(observation_capacity)
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

    # def put_concurrent_implication(self, t: Task):
    #     """
    #     Put an observation to self.observations. Observations need a priority value, which is the summary of its budget.
    #     """
    #     self.concurrent_implications.update(priority(t), t)

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
            each.budget = Budget(min(0.99, each.budget.priority * 1.2),
                                 min(0.99, each.budget.durability * 1.2),
                                 min(0.99, each.budget.quality * 1.2))
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
            each.budget = Budget(min(0.99, each.budget.priority * 1.2),
                                 min(0.99, each.budget.durability * 1.2),
                                 min(0.99, each.budget.quality * 1.2))
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
        cpd = []
        obs_with_close_priority: List[List] = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
        if len(obs_with_close_priority) == 1 and obs_with_close_priority[0] is None:
            # print("1st step: compound generation FINISHED, no observations")
            return
        while not self.data[self.curr].concurrent_observations.is_empty():
            tmp_event = self.data[self.curr].concurrent_observations.get_highest(rmv=True)
            # it cannot be None
            if abs(tmp_event[0] - obs_with_close_priority[0][0]) <= compound_generation_threshold:
                obs_with_close_priority.append(tmp_event)
            else:
                tmp = obs_with_close_priority[0][1]
                obs_with_close_priority = obs_with_close_priority[1:]
                for each in obs_with_close_priority:
                    tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
                cpd.append(tmp)
                if not self.data[self.curr].concurrent_observations.is_empty():
                    obs_with_close_priority = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
                else:
                    obs_with_close_priority = []
        if len(obs_with_close_priority) != 0:
            tmp = obs_with_close_priority[0]
            obs_with_close_priority = obs_with_close_priority[1:]
            for each in obs_with_close_priority:
                tmp = temporal__induction_composition(tmp[1], each[1], time_diff=0)
            cpd.append(tmp)
        for each in cpd:
            self.data[self.curr].put_concurrent_observation(each[1])
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

        # print("1st step: compound generation FINISHED")

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
        # print("2nd step: local evaluation FINISHED")

    def memory_based_evaluation(self):
        # the third step
        """
        Check observations and update their priority values (expectation used here) for prediction generation.
        Update the priority value (expectation used here) for all predictions.

        This updating will also apply to memory.
        """

        concurrent_observation_updating_list = []
        for j in range(len(self.data[self.curr].concurrent_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].concurrent_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].concurrent_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    concurrent_observation_updating_list.append(tmp)
        historical_observation_updating_list = []
        for j in range(len(self.data[self.curr].historical_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].historical_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].historical_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    historical_observation_updating_list.append(tmp)
        for each in concurrent_observation_updating_list:
            self.data[self.curr].put_concurrent_observation(each)
        for each in historical_observation_updating_list:
            self.data[self.curr].put_historical_observation(each)

        # print("3nd step: memory-based evaluation FINISHED")

    def prediction_generation(self):
        # the fourth step
        # figure out the highest compound
        # if self.data[self.curr].highest_concurrent_compound is not None \
        #         and self.data[self.curr].highest_historical_compound is not None:
        #     if priority(self.data[self.curr].highest_concurrent_compound[1]) > priority(
        #             self.data[self.curr].highest_historical_compound[1]):
        #         self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
        #     else:
        #         self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
        # elif self.data[self.curr].highest_concurrent_compound is not None:
        #     self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
        # elif self.data[self.curr].highest_historical_compound is not None:
        #     self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
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
        else:
            # there are no inputs at all, so there are no concurrent_highest, and so there are no predictions
            return
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
        # print("4th step: prediction generation FINISHED")
        if show_predictions:
            print("-" * 74)
            for i, each in enumerate(self.predictions.data):
                print("Event", i + 1, "th prediction", each[1].sentence.word)

    def step(self, new_contents):  # list of tasks
        """
        The new contents are resulted from the operations carried out
        """
        if new_contents is not None:
            for each in new_contents:
                self.data[self.curr].put_concurrent_observation(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        # print(">" + "=" * 73)
        tmp = self.data[self.curr].highest_compound
        # if tmp[1] is not None:
        #     print("Task forwarded " + tmp[1].sentence.word)
        #     print("-" * 74)


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
            # this step is actually unnecessary
            self.operation_agenda.pop(each)

    def step(self, t, operations = []):
        """
        Always execute operations first
        """
        self.exe(operations)
        self.event_buffer.step(self.generate_narsese_input(t))
        if not prediction_as_observation:
            tsk = self.event_buffer.data[self.event_buffer.curr].highest_compound
            if tsk is not None:
                return tsk[1]
            else:
                return None
        else:
            tsk = self.event_buffer.data[self.event_buffer.curr].highest_compound
            pre = self.event_buffer.predictions.get_highest()
            if tsk is not None and pre is not None:
                if priority(tsk[1]) > priority(pre[1]):
                    return tsk[1]
                else:
                    return pre[1]
            elif tsk is not None:
                return tsk[1]
            elif pre is not None:
                return pre[1]
            else:
                return None
        # for j, each in enumerate(self.event_buffer.predictions.data):
        #     print("Prediction  " + str(j) + " | ", each[1].sentence.word, " | ", each[1].truth)
        # print("-" * 74)


class Channel1(SensoryMotorChannel):

    def __init__(self, event_buffer):
        super(Channel1, self).__init__(event_buffer)

    def generate_narsese_input(self, t):
        if t <= 400:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_1}, sting) --> ^see>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        else:
            return []


class Channel2(SensoryMotorChannel):

    def __init__(self, event_buffer):
        super(Channel2, self).__init__(event_buffer)

    def generate_narsese_input(self, t):
        if t <= 100:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_2}, pain) --> ^feel>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        elif 100 < t <= 300:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_2}, nothing) --> ^feel>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        elif 300 < t <= 400:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_2}, pain) --> ^feel>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        else:
            return []


class Channel3(SensoryMotorChannel):

    def __init__(self, event_buffer):
        super(Channel3, self).__init__(event_buffer)

    def generate_narsese_input(self, t):
        if 100 < t <= 300:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_3}, medicine) --> ^see>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        elif t <= 100:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_3}, nothing) --> ^see>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        elif 300 < t <= 400:
            return [parser.parse("$" + str(0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "$ " + "<(*,{Channel_3}, nothing) --> ^see>" + ". :|: %" + str(
                0.5 + random.random() * 0.4) + ";" + str(
                0.5 + random.random() * 0.4) + "% \n")]
        else:
            return []


class OverallExperienceBuffer(object):
    """
    A class for the overall experience buffer. Literally, it is identical to the event buffer, but it can generate
    concurrent implication (=|>) additionally. But these implications are as "predictions".
    """

    def __init__(self, num_slots = 2, observation_capacity = 5, anticipation_capacity = 5, operation_capacity = 5,
                 prediction_capacity = 5, memory: Memory = None):
        super(OverallExperienceBuffer, self).__init__()
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
        self.highest_from = None

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
        cpd = []
        obs_with_close_priority: List[List] = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
        if len(obs_with_close_priority) == 1 and obs_with_close_priority[0] is None:
            # print("1st step: compound generation FINISHED, no observations")
            return
        while not self.data[self.curr].concurrent_observations.is_empty():
            tmp_event = self.data[self.curr].concurrent_observations.get_highest(rmv=True)
            # it cannot be None
            if abs(tmp_event[0] - obs_with_close_priority[0][0]) <= compound_generation_threshold:
                obs_with_close_priority.append(tmp_event)
            else:
                tmp = obs_with_close_priority[0][1]
                obs_with_close_priority = obs_with_close_priority[1:]
                for each in obs_with_close_priority:
                    tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
                cpd.append(tmp)
                if not self.data[self.curr].concurrent_observations.is_empty():
                    obs_with_close_priority = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
                else:
                    obs_with_close_priority = []
        if len(obs_with_close_priority) != 0:
            tmp = obs_with_close_priority[0][1]
            obs_with_close_priority = obs_with_close_priority[1:]
            for each in obs_with_close_priority:
                tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
            cpd.append(tmp)
        for each in cpd:
            self.data[self.curr].put_concurrent_observation(each)
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

        # print("1st step: compound generation FINISHED")

    def local_evaluation(self):
        # the second step
        """
        Predictions will be checked first and satisfied predictions will fire.
        These predictions are Tasks, but initialized with Statement, not simply Term.
        """
        # Prediction checking
        for each_prediction in self.predictions.data:
            if each_prediction[1].sentence.term.subject.components is not None:
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
        # print("2nd step: local evaluation FINISHED")

    def memory_based_evaluation(self):
        # the third step
        """
        Check observations and update their priority values (expectation used here) for prediction generation.
        Update the priority value (expectation used here) for all predictions.

        This updating will also apply to memory.
        """

        concurrent_observation_updating_list = []
        for j in range(len(self.data[self.curr].concurrent_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].concurrent_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].concurrent_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    concurrent_observation_updating_list.append(tmp)
        historical_observation_updating_list = []
        for j in range(len(self.data[self.curr].historical_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].historical_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].historical_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    historical_observation_updating_list.append(tmp)
        for each in concurrent_observation_updating_list:
            self.data[self.curr].put_concurrent_observation(each)
        for each in historical_observation_updating_list:
            self.data[self.curr].put_historical_observation(each)

        # print("3nd step: memory-based evaluation FINISHED")

    def prediction_generation(self):
        # the fourth step
        # figure out the highest compound
        # if self.data[self.curr].highest_concurrent_compound is not None \
        #         and self.data[self.curr].highest_historical_compound is not None:
        #     if priority(self.data[self.curr].highest_concurrent_compound[1]) > priority(
        #             self.data[self.curr].highest_historical_compound[1]):
        #         self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
        #         self.highest_from = "concurrent"
        #     else:
        #         self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
        #         self.highest_from = "historical"
        # elif self.data[self.curr].highest_concurrent_compound is not None:
        #     self.data[self.curr].highest_compound = self.data[self.curr].highest_concurrent_compound
        #     self.highest_from = "concurrent"
        # elif self.data[self.curr].highest_historical_compound is not None:
        #     self.data[self.curr].highest_compound = self.data[self.curr].highest_historical_compound
        #     self.highest_from = "historical"
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
        else:
            # there are no inputs at all, so there are no concurrent_highest, and so there are no predictions
            return
        # generate predictions (=/>)
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
        # generate concurrent predictions (=|>)
        for j in range(len(self.data[self.curr].concurrent_observations.data)):
            if j == 0:
                continue
            tmp = temporal__induction_implication(self.data[self.curr].concurrent_observations.data[j][1],
                                                  self.data[self.curr].highest_compound[1],
                                                  time_diff=0)
            self.predictions.update(priority(tmp), tmp)
        # print("4th step: prediction generation FINISHED")
        if show_predictions:
            print("-" * 74)
            for i, each in enumerate(self.predictions.data):
                print("Overall", i + 1, "th prediction", each[1].sentence.word)
            print("-" * 74)

    def step(self, new_contents):  # list of tasks
        """
        The new contents are resulted from the operations carried out
        """
        # drop the oldest slot
        self.data = self.data[1:]
        # create a new slot
        self.data.append(
            Slot(self.observation_capacity, self.anticipation_capacity, self.operation_capacity))
        for each in new_contents:
            if each is not None:
                self.data[self.curr].put_concurrent_observation(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        # print(">" + "=" * 73)
        # tmp = self.data[self.curr].highest_compound
        # if tmp is not None:
        #     if show_task_forwarded:
        #         print("Task forwarded " + tmp[1].sentence.word)
        #     print("=" * 74)
        #     return tmp[1]
        # else:
        #     return None
        if not prediction_as_observation:
            tsk = self.data[self.curr].highest_compound
            if tsk is not None:
                if show_task_forwarded:
                    print("Task forwarded " + tsk[1].sentence.word)
                return tsk[1]
            else:
                return None
        else:
            tsk = self.data[self.curr].highest_compound
            pre = self.predictions.get_highest()
            if tsk is not None and pre is not None:
                if priority(tsk[1]) > priority(pre[1]):
                    if show_task_forwarded:
                        print("Task forwarded " + tsk[1].sentence.word)
                    return tsk[1]
                else:
                    if show_task_forwarded:
                        print("Task forwarded " + pre[1].sentence.word)
                    return pre[1]
            elif tsk is not None:
                if show_task_forwarded:
                    print("Task forwarded " + tsk[1].sentence.word)
                return tsk[1]
            elif pre is not None:
                if show_task_forwarded:
                    print("Task forwarded " + pre[1].sentence.word)
                return pre[1]
            else:
                return None


class InternalExperienceBuffer(object):
    """
    A class for the overall experience buffer. Literally, it is identical to the event buffer, but it will take these
    mental operations into consideration (as events).
    """

    def __init__(self, num_slots = 2, observation_capacity = 5, anticipation_capacity = 5, operation_capacity = 5,
                 prediction_capacity = 5, memory: Memory = None):
        super(InternalExperienceBuffer, self).__init__()
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
        cpd = []
        obs_with_close_priority: List[List] = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
        if len(obs_with_close_priority) == 1 and obs_with_close_priority[0] is None:
            # print("1st step: compound generation FINISHED, no observations")
            return
        while not self.data[self.curr].concurrent_observations.is_empty():
            tmp_event = self.data[self.curr].concurrent_observations.get_highest(rmv=True)
            # it cannot be None
            if abs(tmp_event[0] - obs_with_close_priority[0][0]) <= compound_generation_threshold:
                obs_with_close_priority.append(tmp_event)
            else:
                tmp = obs_with_close_priority[0][1]
                obs_with_close_priority = obs_with_close_priority[1:]
                for each in obs_with_close_priority:
                    tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
                cpd.append(tmp)
                if not self.data[self.curr].concurrent_observations.is_empty():
                    obs_with_close_priority = [self.data[self.curr].concurrent_observations.get_highest(rmv=True)]
                else:
                    obs_with_close_priority = []
        if len(obs_with_close_priority) != 0:
            tmp = obs_with_close_priority[0][1]
            obs_with_close_priority = obs_with_close_priority[1:]
            for each in obs_with_close_priority:
                tmp = temporal__induction_composition(tmp, each[1], time_diff=0)
            cpd.append(tmp)
        for each in cpd:
            self.data[self.curr].put_concurrent_observation(each)
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

        # print("1st step: compound generation FINISHED")

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
        # print("2nd step: local evaluation FINISHED")

    def memory_based_evaluation(self):
        # the third step
        """
        Check observations and update their priority values (expectation used here) for prediction generation.
        Update the priority value (expectation used here) for all predictions.

        This updating will also apply to memory.
        """

        concurrent_observation_updating_list = []
        for j in range(len(self.data[self.curr].concurrent_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].concurrent_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].concurrent_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    concurrent_observation_updating_list.append(tmp)
        historical_observation_updating_list = []
        for j in range(len(self.data[self.curr].historical_observations.data)):
            for each in self.memory.concepts:
                if self.data[self.curr].historical_observations.data[j][1].sentence.term.equal(each.term):
                    tmp = self.data[self.curr].historical_observations.data[j][1]
                    tmp.budget = Budget(min(0.99, tmp.budget.priority * 1.2), min(0.99, tmp.budget.durability * 1.2),
                                        min(0.99, tmp.budget.quality * 1.2))
                    historical_observation_updating_list.append(tmp)
        for each in concurrent_observation_updating_list:
            self.data[self.curr].put_concurrent_observation(each)
        for each in historical_observation_updating_list:
            self.data[self.curr].put_historical_observation(each)

        # print("3nd step: memory-based evaluation FINISHED")

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
        else:
            # there are no inputs at all, so there are no concurrent_highest, and so there are no predictions
            return
        # generate predictions (=/>)
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
        # print("4th step: prediction generation FINISHED")
        if show_predictions:
            print("-" * 74)
            for i, each in enumerate(self.predictions.data):
                print("Internal", i + 1, "th prediction", each[1].sentence.word)

    def step(self, new_contents):  # list of tasks
        """
        The new contents are resulted from the operations carried out
        """
        # drop the oldest slot
        self.data = self.data[1:]
        # create a new slot
        self.data.append(
            Slot(self.observation_capacity, self.anticipation_capacity, self.operation_capacity))
        for each in new_contents:
            self.data[self.curr].put_concurrent_observation(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        # print(">" + "=" * 73)
        # tmp = self.data[self.curr].highest_compound
        # if tmp is not None:
        #     # print("Task forwarded " + tmp[1].sentence.word)
        #     # print("-" * 74)
        #     return tmp[1]
        # else:
        #     return None
        if not prediction_as_observation:
            tsk = self.data[self.curr].highest_compound
            if tsk is not None:
                return tsk[1]
            else:
                return None
        else:
            tsk = self.data[self.curr].highest_compound
            pre = self.predictions.get_highest()
            if tsk is not None and pre is not None:
                if priority(tsk[1]) > priority(pre[1]):
                    return tsk[1]
                else:
                    return pre[1]
            elif tsk is not None:
                return tsk[1]
            elif pre is not None:
                return pre[1]
            else:
                return None


class Reasoner:

    def __init__(self, n_memory, capacity, config = './config.json') -> None:
        # print('''Init...''')
        Config.load(config)

        self.inference = GeneralEngine()
        self.temporal_inference = TemporalEngine()  # for temporal causal reasoning

        self.memory = Memory(n_memory)
        self.overall_experience = OverallExperienceBuffer(num_slots=4, observation_capacity=5, anticipation_capacity=5,
                                                          operation_capacity=5,
                                                          prediction_capacity=5, memory=self.memory)
        self.internal_experience = InternalExperienceBuffer(num_slots=2, observation_capacity=5,
                                                            anticipation_capacity=5,
                                                            operation_capacity=5,
                                                            prediction_capacity=5, memory=self.memory)
        self.channels = [Channel1(EventBuffer(num_slots=2, memory=self.memory)),
                         Channel2(EventBuffer(num_slots=2, memory=self.memory)),
                         Channel3(EventBuffer(num_slots=2, memory=self.memory))]
        self.uid = 0
        self.d = {}

    def concept_attention_visualization(self, t):
        for each in self.memory.concepts:
            if each.term.word in self.d:
                self.d.update({each.term.word: [self.d[each.term.word][0], each.budget.priority]})
            else:
                self.d.update({each.term.word: [self.uid, each.budget.priority]})
                self.uid += 1
        img = np.zeros([10, 10])
        for each in self.d:
            x = self.d[each][0] // 10
            y = self.d[each][0] % 10
            img[x, y] = self.d[each][1]
        plt.figure()
        plt.imshow(img)
        plt.savefig(
            "C:\\Users\\TORY\\OneDrive - Temple University\\AGI research\\NARS_Optimizer\\img\\" + str(t) + ".jpg")

    def cycle(self, t, operation_goals_for_channels, previous_inference_results, previous_carried_out_mental_opts):
        """Everything to do by NARS in a single working cycle"""

        # step 1. Take out an Items (Tasks) from self.channels, and then put it into the self.overall_experience
        # step 1. Take out an Items (Tasks) from self.channels, and then put it into the self.overall_experience
        tasks_from_channels = [each_channel.step(t, operation_goals_for_channels) for each_channel in self.channels]

        # step 2. Take out an Item from the self.internal_experience, and then put it into self.overall_experience`
        task_from_InternalExpBuffer = self.internal_experience.step(
            previous_inference_results + previous_carried_out_mental_opts)

        tasks_for_OverallExpBuffer = tasks_from_channels + [task_from_InternalExpBuffer]

        # step 3. Process a task of global experience buffer
        task = self.overall_experience.step(tasks_for_OverallExpBuffer)

        previous_inference_results = []
        if task is not None:
            judgement_revised, goal_revised, answers_question, answers_quest = self.memory.accept(task)

            if judgement_revised is not None:
                previous_inference_results.append(judgement_revised)
            if goal_revised is not None:
                previous_inference_results.append(goal_revised)
            if answers_question is not None:
                for answer in answers_question:
                    previous_inference_results.append(answer)
            if answers_quest is not None:
                for answer in answers_quest:
                    previous_inference_results.append(answer)
        else:
            judgement_revised, goal_revised, answers_question, answers_quest = None, None, None, None

        if visualize_concepts:
            self.concept_attention_visualization(t)

        # step 4. Apply general inference step
        concept: Concept = self.memory.take(remove=True)
        if show_concept_selected:
            print(concept.term.word)
        operation_goals_for_channels = []
        tasks_derived: List[Task] = []
        if concept is not None:
            tasks_inference_derived = self.inference.step(concept)
            tasks_derived.extend(tasks_inference_derived)
            self.memory.put_back(concept)
            previous_inference_results.extend(tasks_inference_derived)
            for each in previous_inference_results:
                if each.is_goal and each.is_operation:
                    operation_goals_for_channels.append(each)
            for each in operation_goals_for_channels:
                previous_inference_results.remove(each)

        else:
            pass  # TODO: select a task from `self.sequence_buffer`?

        #   mental operation of NAL-9
        mental_operations_carried_out = []
        task_operation_return, task_executed, belief_awared = self.mental_operation(task, concept, answers_question,
                                                                                    answers_quest,
                                                                                    mental_operations_carried_out)
        if task_operation_return is not None: tasks_derived.append(task_operation_return)
        if task_executed is not None: tasks_derived.append(task_executed)
        if belief_awared is not None: tasks_derived.append(belief_awared)

        #   put the tasks-derived into the internal-experience.
        for task_derived in tasks_derived:
            self.internal_experience.data[self.internal_experience.curr].put_concurrent_observation(task_derived)

        # handle the sense of time
        Global.time += 1

        return operation_goals_for_channels, previous_inference_results, mental_operations_carried_out

    def mental_operation(self, task: Task, concept: Concept, answers_question: Task, answers_quest: Task,
                         mental_operations_carried_out):
        """
        This function will handle a task, and call some mental_operations. An array of operations will be collected,
        and forwarded to the internal exp buffer.
        """

        # handle the mental operations in NAL-9
        task_operation_return, task_executed, belief_awared = None, None, None

        # belief-awareness
        for answers in (answers_question, answers_quest):
            if answers is None: continue
            for answer in answers:
                belief_awared = MentalOperation.aware__believe(answer)
                mental_operations_carried_out.append(belief_awared)

        if task is not None:
            # question-awareness
            if task.is_question:
                belief_awared = MentalOperation.aware__wonder(task)
                mental_operations_carried_out.append(belief_awared)
            # quest-awareness
            elif task.is_quest:
                belief_awared = MentalOperation.aware__evaluate(task)
                mental_operations_carried_out.append(belief_awared)

                # execute mental operation
        if task is not None and task.is_executable:
            task_operation_return, task_executed = MentalOperation.execute(task, concept, self.memory)

        return task_operation_return, task_executed, belief_awared


seed = 523
rand_seed(137)
out_print(PrintType.COMMENT, f'rand_seed={seed}', comment_title='Setup')
out_print(PrintType.COMMENT, 'Init...', comment_title='NARS')
nars = Reasoner(n_memory=100, capacity=100)
out_print(PrintType.COMMENT, 'Run...', comment_title='NARS')
operation_goals_for_channels = []
previous_inference_results = []
previous_carried_out_mental_opts = []
for t in range(400):
    print("Cycle [", t, "]")
    operation_goals_for_channels, previous_inference_results, previous_carried_out_mental_opts = \
        nars.cycle(t,
                   operation_goals_for_channels,
                   previous_inference_results,
                   previous_carried_out_mental_opts)
    if show_inference_result:
        for i, each in enumerate(previous_inference_results):
            print("Task Derived", i + 1, "|", each.sentence.word)


def run_line(nars: ReasonerSC, line: str):
    ''''''
    line = line.strip(' \n')
    if line.startswith("//"):
        return None
    elif line.startswith("''"):
        if line.startswith("''outputMustContain('"):
            line = line[len("''outputMustContain('"):].rstrip("')\n")
            if len(line) == 0: return
            try:
                content_check = parser.parse(line)
                out_print(PrintType.INFO, f'OutputContains({content_check.sentence.repr()})')
            except:
                out_print(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')
                # out_print(PrintType.ERROR, f'{file}, line {i}, {line}')
        return
    elif line.startswith("'"):
        return None
    elif line.isdigit():
        n_cycle = int(line)
        out_print(PrintType.INFO, f'Run {n_cycle} cycles.')
        tasks_all_cycles = []
        for _ in range(n_cycle):
            tasks_all = nars.cycle()
            tasks_all_cycles.append(deepcopy(tasks_all))
        return tasks_all_cycles
    else:
        line = line.rstrip(' \n')
        if len(line) == 0:
            return None
        try:
            success, task, _ = nars.input_narsese(line, go_cycle=False)
            if success:
                out_print(PrintType.IN, task.sentence.repr(), *task.budget)
            else:
                out_print(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')

            tasks_all = nars.cycle()
            return [deepcopy(tasks_all)]
        except:
            out_print(PrintType.ERROR, f'Unknown error: {line}')


def handle_lines(lines: str):
    tasks_lines = []
    for line in lines.split('\n'):
        if len(line) == 0: continue

        tasks_line = run_line(nars_SC, line)
        if tasks_line is not None:
            tasks_lines.extend(tasks_line)

    tasks_lines: List[Tuple[List[Task], Task, Task, List[Task], Task, Tuple[Task, Task]]]
    for tasks_line in tasks_lines:
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = tasks_line

        # operation goal detection
        for task in tasks_derived:
            print("task derived", task.sentence.word)

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


nars_SC = ReasonerSC(100, 100)
nars_SC.memory = nars.memory
while True:
    out_print(PrintType.COMMENT, '', comment_title='Input', end='')
    lines = input()
    handle_lines(lines)
