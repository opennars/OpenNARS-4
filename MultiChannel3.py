# Event buffer

import re
import heapq
# from queue import PriorityQueue
from pynars.Narsese import Task
from pynars.NAL.Inference import local__revision, compositional__conjunstion_composition, \
    temporal__induction_implication, temporal__induction_composition
from pynars.Narsese import parser, Term, Statement, Compound, Interval, Budget, Sentence
from pynars.NARS.DataStructures import Memory, Judgement
from pynars.NAL.Functions import Stamp_merge, Truth_intersection, Truth_deduction, Budget_merge
from pynars.NARS import Reasoner


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
        a sorted list of lists, [priority_value, prediction], sorted from large to small by a prediction's priority 
        value, which is not its truth-value.
        It is used for "observations in slot", "anticipations in slot", "predictive implications".
        For "operations in slot", since they have the same default truth-value, they have the same priority value.
        """

    def update(self, priority_value, t: Task):
        for i in range(len(self.data)):
            if t.sentence.term.equal(self.data[i][1].sentence.term):
                self.data = self.data[:i] + self.data[i + 1:]  # possible data leak
                break
        for i in range(len(self.data)):
            if priority_value > self.data[i][0]:
                self.data = self.data[:i] + [[priority_value, t]] + self.data[i:]
                if len(self.data) > self.capacity:
                    self.data = self.data[:self.capacity]
                return
        self.data += [[priority_value, t]]
        if len(self.data) > self.capacity:
            self.data = self.data[:self.capacity]
        return

    def get_highest(self, rmv = False):
        if len(self.data) == 0:
            return None
        if not rmv:
            return self.data[0][1]
        else:
            tmp = self.data[0][1]
            self.data = self.data[1:]
            return tmp

    def get_others(self):
        if len(self.data) <= 1:
            return None
        else:
            return [each[1] for each in self.data[1:]]


class Anticipation(object):
    """
    Anticipations have two parts, its parent prediction (where this anticipation is from), and its expected
    observation. This expected observation has a truth-value, which is generated from a known observation and its
    parent prediction using the deductive rule.

    When an anticipation really appears, its parent prediction's truth-value and priority value will be both increased,
    and the observation will be revised with the anticipation.

    When an anticipation does not appear, its parent prediction's truth-value and priority value will be both decreased.
    """

    def __init__(self, parent_prediction: Task, expected_observation: Task):
        super(Anticipation, self).__init__()
        self.parent_prediction = parent_prediction
        self.expected_observation = expected_observation

    def satisfied(self, predictions: PriorityQueue):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %1.0;0.9% \n")
        try:
            self.parent_prediction = local__revision(task=self.parent_prediction, belief=t,
                                                     budget_tasklink=self.parent_prediction.budget,
                                                     budget_termlink=Budget(0.9, 0.9, 0.5))
            predictions.update(self.parent_prediction.budget.summary, self.parent_prediction)
        except:
            return  # the parent prediction is expired

    def unsatisfied(self, predictions: PriorityQueue):  # revision for its parent prediction
        t = parser.parse(self.parent_prediction.sentence.word + " %0.0;0.9% \n")
        try:
            self.parent_prediction = local__revision(task=self.parent_prediction, belief=t,
                                                     budget_tasklink=self.parent_prediction.budget,
                                                     budget_termlink=Budget(0.1, 0.9, 0.5))
            predictions.update(self.parent_prediction.budget.summary, self.parent_prediction)
        except:
            return  # the parent prediction is expired


class PriorityQueueAnticipations(PriorityQueue):

    def __init__(self, capacity = 5):
        super(PriorityQueueAnticipations, self).__init__(capacity)
        self.capacity = capacity
        self.data = []

    def update(self, priority_value, a: Anticipation):
        for i in range(len(self.data)):
            if a.expected_observation.sentence.term.equal(self.data[i][1].sentence.term):
                self.data = self.data[:i] + self.data[i + 1:]  # possible data leak
                break
        for i in range(len(self.data)):
            if priority_value > self.data[i][0]:
                self.data = self.data[:i] + [[priority_value, a]] + self.data[i:]
                if len(self.data) > self.capacity:
                    self.data = self.data[:self.capacity]
                    return
        self.data += [[priority_value, a]]
        if len(self.data) > self.capacity:
            self.data = self.data[:self.capacity]
            return


class PriorityQueueOperations(PriorityQueue):
    """
    Not necessary to make "operations" a PriorityQueue, just to make it consistent.
    """

    def __init__(self, capacity = 5):
        super(PriorityQueueOperations, self).__init__(capacity)
        self.capacity = capacity
        self.data = []

    def update(self, o: Task):
        for i in range(len(self.data)):
            if o.sentence.term.equal(self.data[i][1].sentence.term):
                self.data = self.data[:i] + self.data[i + 1:]  # possible data leak
                break
        for i in range(len(self.data)):
            if o.budget.summary > self.data[i][0]:
                self.data = self.data[:i] + [[o.budget.summary, o]] + self.data[i:]
                if len(self.data) > self.capacity:
                    self.data = self.data[:self.capacity]
                    return
        self.data += [[o.budget.summary, o]]
        if len(self.data) > self.capacity:
            self.data = self.data[:self.capacity]
            return


def pq_merge(pq1: PriorityQueue, pq2: PriorityQueue):
    """
    Merge two PriorityQueue's, generate a new PQ whose capacity is the addition of two inputs.
    """
    new_pq = PriorityQueue(pq1.capacity + pq2.capacity)
    for i in range(len(pq1.data)):
        new_pq.update(pq1.data[i][0], pq1.data[i][1])
    for i in range(len(pq2.data)):
        new_pq.update(pq2.data[i][0], pq2.data[i][1])
    return new_pq


"""
It is commented since we can use the above PriorityQueue class for it.
"""
# class PredictiveImplications(object):
#     """
#     Each predictive implication is a Narsese sentence like:
#         <(&/, A, +3, B) =/> C>. <f,c>
#     If more predictions are added when it is full, the prediction with [the lowest expectation] (or other priority
#     measurement) will be dropped.
#     Add a brand-new prediction is possible.
#     Add an already-existed prediction is also possible. This will call a revision.
#     """
#
#     def __init__(self, prediction_capacity = 5):
#         super(PredictiveImplications, self).__init__()
#         self.prediction_capacity = prediction_capacity
#         self.data = []
#         """
#         a sorted list of lists, [priority_value, prediction], sorted from large to small by a prediction's priority
#         value, which is not its truth-value.
#         """
#
#     def update(self, prediction: Task, priority_value):
#         for i in range(len(self.data)):
#             if prediction.sentence.term.equal(self.data[i][1].sentence.term):
#                 self.data = self.data[:i] + self.data[i+1:]  # possible data leak
#                 break
#         for i in range(len(self.data)):
#             if priority_value > self.data[i][0]:
#                 self.data = self.data[:i] + [[priority_value, prediction]] + self.data[i:]
#                 if len(self.data) > self.prediction_capacity:
#                     self.data = self.data[:self.prediction_capacity]
#                     return
#         self.data += [[priority_value, prediction]]
#         if len(self.data) > self.prediction_capacity:
#             self.data = self.data[:self.prediction_capacity]
#             return


"""
It is commented since for newly generated candidate compounds, we just need a container, possible with a maximum
capacity, but no need for sorting. Since these compounds will enter "observations" in a slot, and the "observations" is
a PriorityQueue.
"""


# class CandidateCompounds(object):
#     """
#     For candidate compounds based on their expectations (the priority measurement).
#     It does not have a capacity, but usually the compounds needed are limited, so the "capacity" will be
#     applied outside.
#     """
#
#     def __init__(self):
#         super(CandidateCompounds, self).__init__()
#         self.PQ = PriorityQueue()
#         self.size = 0
#
#     def put(self, t: Task):
#         self.PQ.put((t.truth.e, t))
#         self.size += 1
#
#     def get(self) -> Task:  # get the compound with the highest expectation (the priority measurement)
#         tmp = self.PQ.get()
#         if tmp is not None:
#             self.size -= 1
#             return tmp[1]
#         else:
#             return None
#
#     def empty(self):
#         return self.PQ.empty()
#
#     def to_list(self) -> list:
#         ret = []
#         while not self.PQ.empty():
#             ret.append(self.get())
#         return ret  # [(compound's expectation: the priority measurement, compound: Task), ...]
#
#     def __len__(self):
#         return self.size


class Slot(object):
    """
    For each time slot in one buffer.
    It has three parts,
        1: One is for the input observations.
        2: One is for the expected observations (also called anticipations).
        3: One is for the operations just carried out.
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
        self.observations = PriorityQueue(observation_capacity)
        self.anticipations = PriorityQueueAnticipations(anticipation_capacity)
        self.operations = PriorityQueueOperations(operation_capacity)

    def put_observation(self, t: Task):
        """
        Put an observation to self.observations. Observations need a priority value, which is the summary of its budget.
        """
        self.observations.update(t.budget.summary, t)
        """
        The following is commented since previously,we treat self.observations as a python list.
        """
        # if len(self.observations) == self.observation_capacity:
        #     self.observations = self.observations[:-1]
        #     # drop the one with the lowest priority value (expectation here)
        # for i in range(len(self.observations)):  # insertion sort
        #     if t.truth.e > self.observations[i][0]:
        #         self.observations = self.observations[:i] + [[t.truth.e, t]] + self.observations[i:]
        #         return
        # self.observations += [[t.truth.e, t]]

    def put_anticipation(self, a: Anticipation):
        """
        self.anticipations is also a PriorityQueue, with each anticipation's budget's summary as its priority value,
        except for that, each anticipation's expected observation is a task, generated using inference rules, so it can
        have the correct budget and truth-value.
        """
        self.anticipations.update(a.expected_observation.budget.summary, a)
        """
        The following is commented since previously,we treat self.observations as a python list.
        """
        # if len(self.anticipations) == self.anticipation_capacity:
        #     self.anticipations = self.anticipations[:-1]
        #     """
        #     drop the one with the lowest truth-value, note that in other cases, the one with the lowest "priority"
        #     value is usually dropped, but anticipations can only have truth-values.
        #     """
        # for i in range(len(self.anticipations)):
        #     if a.expected_observation.truth.e > self.anticipations[i].expected_observation.truth.e:
        #         self.anticipations = self.anticipations[:i] + [a] + self.anticipations[i:]
        #         return
        # self.anticipations += [a]

    def put_operation(self, o: Task):
        """
        like above
        """
        self.operations.update(o)
        # """
        # Here "operations" are "observed executions of observation", so they are just judgments, with a default truth-
        # value <1, 0.9> and a default budget <0.9, 0.9, 0.5>.
        # """
        #
        # """
        # The following two lines are commented intentionally. Since here we don't need to worry it will max out.
        # The "operations" in one slot is filled by the buffer, maxing out will never happen.
        # """
        # # if len(self.operations) == self.operation_capacity:
        # #     pass
        # self.operations.append(t)

    """
    The following function is commented, since we can call self.operations.get_highest() to get the observation with
    the highest priority.
    Unexpected observations will get a special priority boost (or expected observations will have a special priority
    decay), so we don't need to point them out here.
    """
    # def get_highest(self, rmv = False, unexpected_observations = None):  # get the one with the highest priority
    #     if len(self.observations) == 0:  # it is possible to have no observations at all
    #         return None
    #     if not rmv:
    #         if unexpected_observations is not None and len(unexpected_observations) != 0:
    #             for each_observation in self.observations:
    #                 for each_unexpected_observation in unexpected_observations:
    #                     if each_observation[1].sentence.term.equal(each_unexpected_observation):
    #                         return each_observation[1]
    #         if self.observations[0] is not None:
    #             return self.observations[0][1]
    #     else:
    #         if unexpected_observations is not None and len(unexpected_observations) != 0:
    #             for each_observation in self.observations:
    #                 for each_unexpected_observation in unexpected_observations:
    #                     if each_observation[1].sentence.term.equal(each_unexpected_observation):
    #                         tmp = each_observation
    #                         self.observations.remove(tmp)
    #                         return tmp[1]
    #         if self.observations[0] is not None:
    #             tmp = self.observations[0][1]
    #             self.observations = self.observations[1:]
    #             return tmp

    """
    The following function is commented, since we can call self.operations.get_others().
    """

    # def get_others(self):  # get other observations, used for compound generation
    #     return [self.observations[i][1] for i in range(1, len(self.observations))]

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
        for i, each_observation in enumerate(self.observations.data):
            matched = False
            for j, each_anticipation in enumerate(self.anticipations.data):
                if j in satisfied_anticipations:  # already satisfied, cannot be satisfied again, pass
                    continue
                if each_anticipation.expected_observation.sentence.term.equal(each_observation[1].sentence.term):
                    """
                    A satisfied anticipation, self.observations.update(revised observation)
                    """
                    revised_observation = local__revision(each_observation, each_anticipation.expected_observation)
                    observation_updating_list.append(revised_observation)
                    each_anticipation.satisfied()
                    matched = True
                    break
            if not matched:
                unexpected_observations.append(each_observation[1])
        for i in range(len(self.anticipations.data)):
            if i not in satisfied_anticipations:
                self.anticipations.data[i][1].unsatisfied()
        """
        self.observations' updating after all anticipations are checked.
        """
        for each in observation_updating_list:
            self.observations.update(each.budget.summary, each)
        """
        increase the priority of the unexpected observations
        """
        for each in unexpected_observations:
            self.observations.update(Budget_merge(each.budget, Budget(0.9, 0.9, 0.5)).summary, each)


class EventBuffer(object):
    """
    A class for the event buffer in one channel. It has multiple slots and a set of predictive implications
    (also called predictions).
    """

    def __init__(self, num_slots = 2, observation_capacity = 5, anticipation_capacity = 5, operation_capacity = 5,
                 prediction_capacity = 5, memory: Memory = None):
        super(EventBuffer, self).__init__()
        self.observation_capacity = observation_capacity
        self.anticipation_capacity = anticipation_capacity
        self.operation_capacity = operation_capacity
        self.memory = memory
        # num_slots is for the number of slots on one side
        self.num_slots_one_side = num_slots
        # self.num_slots is for the number of slots on both sides and the middle
        self.num_slots = 2 * num_slots + 1
        self.data = [Slot(observation_capacity, anticipation_capacity, operation_capacity) for i in
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

        Two kinds of compounds will be generated (&&, &/), but no matter what, only two terms will be used to generate
        one compound. Though it is possible to have ((A,B),C).
        """

        current_highest = self.data[self.curr].observations.get_highest()
        if current_highest is None:
            print("1st step: compound generation FINISHED, no current highest")
            return
        current_others = self.data[self.curr].observations.get_others()
        previous_highest = [self.data[i].observations.get_highest() for i in range(self.num_slots_one_side)]
        if current_others is None and all(each is None for each in previous_highest):
            print("1st step: compound generation FINISHED, no current other and previous highest")
            return
        candidate_compounds = []
        if current_others is not None:
            for each in current_others:  # &|
                cpd = temporal__induction_composition(current_highest, each, time_diff=0)
                candidate_compounds.append(cpd)
        if all(each is None for each in previous_highest) is not True:
            tdf = 0
            for each in previous_highest[::-1]:  # &/
                tdf += 1
                if each is not None:
                    cpd = temporal__induction_composition(each, current_highest, time_diff=tdf)
                    candidate_compounds.append(cpd)
        for each in candidate_compounds:
            self.data[self.curr].observations.update(each.budget.summary, each)

        # current_highest = self.data[self.curr].get_highest()
        # if current_highest is None:
        #     print("1st step: compound generation FINISHED")
        #     return
        # current_others = self.data[self.curr].get_others() + self.data[self.curr].operations
        # previous_highest = [self.data[i].get_highest() for i in range(self.num_slots_one_side)]
        # candidate_compounds = CandidateCompounds()
        # """
        # I have changed the source code for both compound-generating functions used to make "compound-operations"'
        # "is_operation" True. And if it is a compound operation, its "decomposition" will not be empty.
        # """
        # for each in current_others:  # &&
        #     if each is not None:
        #         cpd = compositional__conjunstion_composition(current_highest, each)
        #         candidate_compounds.put(cpd)
        # tdf = 0
        # for each in previous_highest[::-1]:  # &/
        #     tdf += 1
        #     if each is not None:
        #         cpd = temporal__induction_composition(each, current_highest, time_diff=tdf)
        #         candidate_compounds.put(cpd)
        # candidate_compounds = candidate_compounds.to_list()
        # """
        # Here, there might be many compounds, but they will be pushed to the current slot and compete due to their
        # priorities (expectation used here)
        # """
        # for each in candidate_compounds:
        #     self.data[self.curr].put_observation(each)
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
            for each_observation in self.data[self.curr].observations.data:
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
        for i in range(len(self.data[self.curr].observations.data)):
            tmp, _, _, _ = self.memory.accept(self.data[self.curr].observations.data[i][1])
            if tmp is not None:
                self.data[self.curr].observations.data[i] = [tmp.budget.summary, tmp]
        for i in range(len(self.predictions.data)):
            tmp, _, _, _ = self.memory.accept(self.predictions.data[i][1])
            if tmp is not None:
                self.predictions.data[i] = [[tmp.budget.summary, tmp]]
        print("3nd step: memory-based evaluation FINISHED")
        for i, each in enumerate(self.data[self.curr].observations.data):
            print("Compounds  " + str(i) + " | ", each[1].sentence.word, " | ", each[1].truth)
        print("-" * 74)

    def prediction_generation(self):
        # the fourth step
        current_highest = self.data[self.curr].observations.get_highest()
        if current_highest is None:
            print("4th step: prediction generation FINISHED, no current highest")
            return
        previous_highest = [self.data[i].observations.get_highest() for i in range(self.num_slots_one_side)]
        if all(each is None for each in previous_highest):
            print("4th step: prediction generation FINISHED, no previous highest")
            return
        tdf = 0
        for each in previous_highest[::-1]:
            tdf += 1
            """
            Note that this task is generated using Statement, not purly Term, therefore, this task's sentence.term has
            attribute *.subject and *.predicate.
            """
            if each is not None:
                tmp = temporal__induction_implication(each, current_highest, time_diff=tdf)
                self.predictions.update(tmp.budget.summary, tmp)
        print("4th step: prediction generation FINISHED")

    def step(self, new_contents):  # list of tasks
        """
        The new contents are resulted from the operations carried out
        """
        for each in new_contents:
            self.data[self.curr].put_observation(each)
        self.compound_generation()  # 1st step
        self.local_evaluation()  # 2nd step
        self.memory_based_evaluation()  # 3rd step
        self.prediction_generation()  # 4th step
        print(">" + "=" * 73)
        tmp = self.data[self.curr].observations.get_highest(rmv=True)
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

    def __init__(self, num_slots = 2, memory = None):
        super(SensoryMotorChannel, self).__init__()
        self.event_buffer = EventBuffer(num_slots=num_slots, memory=memory)
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
        if t == 0:
            print("Observations [<A-->B>. <C-->D>.] found at time [" + str(t) + "].")
            print("-" * 74)
            return [parser.parse("<A-->B>. \n"), parser.parse("<C-->D>. \n")]
            # return [parser.parse("A. \n")]
        elif t == 1:
            print("Observations [B.] found at time [" + str(t) + "].")
            print("-" * 74)
            return [parser.parse("B. \n")]
        elif t == 2:
            print("Observations [C.] found at time [" + str(t) + "].")
            print("-" * 74)
            return [parser.parse("C. \n"), parser.parse("B. \n")]
        elif t == 3:
            print("Observations [] found at time [" + str(t) + "].")
            print("-" * 74)
            return []
        elif t == 4:
            print("Observations [D.] found at time [" + str(t) + "].")
            print("-" * 74)
            return [parser.parse("D. \n")]
        else:
            print("Observations [] found at time [" + str(t) + "].")
            print("-" * 74)
            return []

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

    def step(self, new_contents, operations):
        """
        Always execute operations first
        """
        self.exe(operations)
        self.event_buffer.step(new_contents)
        for i, each in enumerate(self.event_buffer.predictions.data):
            print("Prediction  " + str(i) + " | ", each[1].sentence.word, " | ", each[1].truth)
        print("-" * 74)

    # a function JUST for debugging
    def simulator(self):
        for i in range(10):
            print("<<< Time", i, ">>>")
            print("-" * 74)
            self.step(self.generate_narsese_input(i), operation_commands_simulator(i))
        print("FINISHED")


def operation_commands_simulator(t):  # it could be replaced with some other functions
    """
    :return: list of operation goals
    """
    tmp1 = parser.parse("^opt1! \n")
    tmp2 = parser.parse("^opt2! \n")
    if t == 0:
        print("Commands [^opt1!] given at time [" + str(t) + "].")
        print("-" * 74)
        return [tmp1]
    elif t == 1:
        print("Commands [] given at time [" + str(t) + "].")
        print("-" * 74)
        return []
    elif t == 2:
        print("Commands [^opt2!] given at time [" + str(t) + "].")
        print("-" * 74)
        return [tmp2]
    elif t == 3:
        print("Commands [(&&, ^opt1, ^opt2)!] given at time [" + str(t) + "].")
        print("-" * 74)
        tmp3 = parser.parse("(&&, ^opt1, ^opt2)! \n")
        tmp3.sentence.term.decomposition = [[tmp1], [tmp2]]
        return [tmp3]
    elif t == 5:
        print("Commands [(&/, ^opt1, +2, ^opt2)!] given at time [" + str(t) + "].")
        print("-" * 74)
        tmp4 = parser.parse("(&/, ^opt1, +2, ^opt2)! \n")
        tmp4.sentence.term.decomposition = [[tmp1], [2], [tmp2]]
        return [tmp4]
    else:
        print("Commands [] given at time [" + str(t) + "].")
        print("-" * 74)
        return []


nars = Reasoner(100, 100)
EXP = SensoryMotorChannel(memory=nars.memory)
EXP.simulator()
