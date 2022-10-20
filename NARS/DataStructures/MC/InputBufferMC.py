from copy import deepcopy

from pynars.NAL.Functions import Stamp_merge, Budget_merge, Truth_induction, Truth_deduction
from pynars.NAL.Inference import LocalRules
from pynars.NARS.DataStructures import Memory
from pynars.NARS.DataStructures.MC.AnticipationMC import AnticipationMC
from pynars.NARS.DataStructures.MC.SlotMC import SlotMC
from pynars.Narsese import Compound, Punctuation, Sentence, Task, Judgement, Interval, Term, Statement


# the priority value of predictions
def p_value(t: Task):
    return t.budget.summary * t.truth.e / t.term.complexity ** 2


class InputBufferMC(object):

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory: Memory):
        self.num_slot = num_slot * 2 + 1
        self.present = num_slot
        self.num_event = num_event
        self.num_anticipation = num_anticipation
        self.num_prediction = num_prediction
        self.memory = memory
        self.prediction_table = []
        self.slots = [SlotMC(num_event, num_anticipation) for _ in range(self.num_slot)]

    def update_prediction(self, p: Task):
        for i in range(len(self.prediction_table)):
            if self.prediction_table[i].term == p.term:
                del self.prediction_table[i]
                break
        P = p_value(p)
        for i in range(len(self.prediction_table)):
            if P > p_value(self.prediction_table[i]):
                self.prediction_table = self.prediction_table[:i] + [p] + self.prediction_table[i:]
                break
        self.prediction_table = [p] + self.prediction_table
        if len(self.prediction_table) > self.num_prediction:
            self.prediction_table = self.prediction_table[1:]

    def combination(self, lst, start, num, tmp, cpds):
        if num == 0:
            cpds.append(deepcopy(tmp))
            return
        elif len(lst) - start < num:
            return
        else:
            tmp.append(lst[start])
            self.combination(lst, start + 1, num - 1, tmp, cpds)
            self.combination(lst[:-1], start + 1, num, tmp, cpds)

    def compound_generation(self, new_contents):
        for new_content in new_contents:
            self.slots[self.present].update_events(new_content)
        # check atomic anticipations
        self.slots[self.present].check_anticipation(self.prediction_table)
        compounds = []
        for i in range(len(self.slots[self.present].events)):
            self.combination(self.slots[self.present].events, 0, i + 1, [], compounds)
        for each_compound in compounds:
            if len(each_compound) > 1:
                # term generation
                each_compound_term = [each.term for each in each_compound]
                term = Compound.ParallelEvents(*each_compound_term)
                existed = False
                existed_p = 0
                for each_existed_event in self.slots[self.present].events:
                    if each_existed_event.term.equal(term):
                        existed = True
                        existed_p = p_value(each_existed_event)
                        break
                # judgment punctuation
                punctuation = Punctuation.Judgement
                # truth, using truth-induction function (TODO, may subject to change)
                truth = each_compound[0].truth
                for each in each_compound[1:]:
                    truth = Truth_induction(truth, each.truth)
                # stamp, using stamp-merge function (TODO, may subject to change)
                stamp = each_compound[0].stamp
                for each in each_compound[1:]:
                    stamp = Stamp_merge(stamp, each.stamp)
                # budget, using budget-merge function (TODO, may subject to change)
                budget = each_compound[0].budget
                for each in each_compound[1:]:
                    budget = Budget_merge(budget, each.budget)
                # sentence composition
                sentence = Judgement(term, stamp, truth)
                # task generation
                task = Task(sentence, budget)
                if not existed:
                    self.slots[self.present].update_events(task)
                elif p_value(task) > existed_p:
                    self.slots[self.present].update_events(task)
            else:
                self.slots[self.present].update_events(each_compound[0])
        # check concurrent compound anticipations
        self.slots[self.present].check_anticipation(self.prediction_table)
        # generate historical compounds
        for i in range(self.present):
            previous_event_concurrent = self.slots[i].highest_compound
            if previous_event_concurrent:
                for each_event in self.slots[self.present].events:
                    # term generation
                    term = Compound.SequentialEvents(previous_event_concurrent.term, Interval(abs(self.present - i)),
                                                     each_event.term)
                    # judgment punctuation
                    punctuation = Punctuation.Judgement
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = each_compound[0].truth
                    for each in each_compound[1:]:
                        truth = Truth_induction(truth, each.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = each_compound[0].stamp
                    for each in each_compound[1:]:
                        stamp = Stamp_merge(stamp, each.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = each_compound[0].budget
                    for each in each_compound[1:]:
                        budget = Budget_merge(budget, each.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    self.slots[self.present].update_events_historical(task)
            previous_compound_historical = self.slots[i].highest_compound_historical
            if previous_compound_historical:
                for each_event in self.slots[self.present].events:
                    # term generation
                    term = Compound.SequentialEvents(previous_compound_historical, Interval(abs(self.present - i)),
                                                     each_event)
                    # judgment punctuation
                    punctuation = Punctuation.Judgement
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = each_compound[0].truth
                    for each in compounds[1:]:
                        truth = Truth_induction(truth, each.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = each_compound[0].stamp
                    for each in compounds[1:]:
                        stamp = Stamp_merge(stamp, each.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = each_compound[0].budget
                    for each in compounds[1:]:
                        budget = Budget_merge(budget, each.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    self.slots[self.present].update_events_historical(task)
        # check historical compound anticipations
        self.slots[self.present].check_anticipation(self.prediction_table)

    def local_evaluation(self):
        # generate anticipation
        for each_prediction in self.prediction_table:
            for each_event in self.slots[self.present].events:
                if each_prediction.term.subject.equal(each_event.term):
                    # term generation
                    term = each_prediction.term.predicate
                    # judgment punctuation
                    punctuation = Punctuation.Judgement
                    # truth, using truth-deduction function (TODO, may subject to change)
                    truth = Truth_deduction(each_prediction.truth, each_event.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(each_prediction.stamp, each_event.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(each_prediction.budget, each_event.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    # anticipation generation
                    anticipation = AnticipationMC(task, each_prediction)
                    self.slots[self.present].update_anticipation(anticipation)
            for each_event_historical in self.slots[self.present].events_historical:
                if each_prediction.term.subject.equal(each_event_historical.term):
                    # term generation
                    term = each_prediction.term.predicate
                    # judgment punctuation
                    punctuation = Punctuation.Judgement
                    # truth, using truth-deduction function (TODO, may subject to change)
                    truth = Truth_deduction(each_prediction.truth, each_event_historical.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(each_prediction.stamp, each_event_historical.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(each_prediction.budget, each_event_historical.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    task = Task(sentence, budget)
                    # anticipation generation
                    anticipation = AnticipationMC(task, each_prediction)
                    self.slots[self.present].update_anticipation(anticipation)
        # check anticipations with un-expectation handling
        self.slots[self.present].check_anticipation(self.prediction_table, mode_unexpected=True)

    def memory_based_evaluations(self):
        events_updates = []
        events_historical_updates = []
        for each_event in self.slots[self.present].events:
            tmp = self.memory.concepts.take_by_key(each_event.term, remove=False)
            if tmp:
                budget = Budget_merge(each_event.budget, tmp.budget)
                task = Task(each_event.sentence, budget)
                events_updates.append(task)
        for each_event_historical in self.slots[self.present].events_historical:
            tmp = self.memory.concepts.take_by_key(each_event_historical.term, remove=False)
            if tmp:
                budget = Budget_merge(each_event_historical.budget, tmp.budget)
                task = Task(each_event_historical.sentence, budget)
                events_historical_updates.append(task)
        for each_event in events_updates:
            self.slots[self.present].update_events(each_event)
        for each_event_historical in events_historical_updates:
            self.slots[self.present].update_events_historical(each_event_historical)
        if len(self.slots[self.present].events) != 0:
            self.slots[self.present].highest_compound = self.slots[self.present].events[-1]
        if len(self.slots[self.present].events_historical) != 0:
            self.slots[self.present].highest_compound_historical = self.slots[self.present].events_historical[-1]
        if len(self.slots[self.present].events) != 0 and len(self.slots[self.present].events_historical) != 0:
            if self.slots[0].p_value(self.slots[self.present].highest_compound) > self.slots[0].p_value(
                    self.slots[self.present].highest_compound_historical):
                self.slots[self.present].candidate = self.slots[self.present].highest_compound
            else:
                self.slots[self.present].candidate = self.slots[self.present].highest_compound_historical
        elif len(self.slots[self.present].events) != 0:
            self.slots[self.present].candidate = self.slots[self.present].highest_compound
        elif len(self.slots[self.present].events_historical) != 0:
            self.slots[self.present].candidate = self.slots[self.present].highest_compound_historical

    def prediction_generation(self):
        if self.slots[self.present].candidate:
            for i in range(self.present):
                if self.slots[i].candidate:
                    # TODO, this is ugly
                    term1 = Compound.SequentialEvents(self.slots[i].candidate.term, Interval(abs(self.present - i)))
                    term2 = self.slots[self.present].candidate.term
                    term = Statement.PredictiveImplication(term1, term2)
                    # <term1 =/> term2>
                    # truth, using truth-induction function (TODO, may subject to change)
                    truth = Truth_induction(self.slots[i].candidate.truth, self.slots[self.present].candidate.truth)
                    # stamp, using stamp-merge function (TODO, may subject to change)
                    stamp = Stamp_merge(self.slots[i].candidate.stamp, self.slots[self.present].candidate.stamp)
                    # budget, using budget-merge function (TODO, may subject to change)
                    budget = Budget_merge(self.slots[i].candidate.budget, self.slots[self.present].candidate.budget)
                    # sentence composition
                    sentence = Judgement(term, stamp, truth)
                    # task generation
                    prediction = Task(sentence, budget)
                    self.update_prediction(prediction)
        return self.slots[self.present].candidate

    def step(self, new_contents):
        # remove the oldest slot and create a new slot
        self.slots = self.slots[1:]
        self.slots.append(SlotMC(self.num_event, self.num_anticipation))
        self.compound_generation(new_contents)
        self.local_evaluation()
        self.memory_based_evaluations()
        task_forward = self.prediction_generation()
        return task_forward
