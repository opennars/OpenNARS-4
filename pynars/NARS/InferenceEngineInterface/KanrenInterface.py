from pynars.NARS.DataStructures import Bag, Memory, NarseseChannel, Buffer, Task, Concept
from pynars.NARS.DataStructures._py.Link import TaskLink, TermLink
from pynars import Global
from pynars.Narsese._py.Sentence import Judgement, Stamp, Question, Goal
from pynars.NAL.Functions.BudgetFunctions import Budget_forward, Budget_backward
from pynars.NAL.Functions.StampFunctions import Stamp_merge
from pynars.NAL.Functions.Tools import project_truth, project
from pynars.NARS.DataStructures._py.Link import TaskLink, TermLink
from pynars.Narsese import Term, Copula, Statement, Compound, Connector, Item, Budget
from pynars.NAL.InferenceEngine.KanrenEngine import KanrenEngine
import random


class InferenceEngine:
    structural_enabled = True
    immediate_enabled = True
    compositional_enabled = True
    theorems_per_cycle = 1

    class TheoremItem(Item):
        def __init__(self, theorem, budget: Budget) -> None:
            super().__init__(hash(theorem), budget)
            self._theorem = theorem

    def __init__(self):
        self.inference = KanrenEngine()
        self.all_theorems = Bag(100, 100, take_in_order=False)

        if self.structural_enabled:
            for theorem in self.inference.theorems:
                priority = random.randint(0,9) * 0.01
                item = self.TheoremItem(theorem, Budget(0.5 + priority, 0.8, 0.5))
                self.all_theorems.put(item)

    def reset(self):
        if self.structural_enabled:
            # reset theorems priority
            self.all_theorems.reset()
            for theorem in self.inference.theorems:
                priority = random.randint(0,9) * 0.01
                item = self.TheoremItem(theorem, Budget(0.5 + priority, 0.8, 0.5))
                self.all_theorems.put(item)


    def step(self, concept: Concept):
        '''One step inference.'''
        tasks_derived = []

        Global.States.record_concept(concept)
        
        # Based on the selected concept, take out a task and a belief for further inference.
        task_link: TaskLink = concept.task_links.take(remove=True)
        
        if task_link is None: 
            return tasks_derived
        
        concept.task_links.put_back(task_link)

        task: Task = task_link.target

        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False

        for _ in range(len(concept.term_links)): # TODO: should limit max number of links to process
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            term_link: TermLink = concept.term_links.take(remove=True)
            term_links.append(term_link)

            if not task_link.novel(term_link, Global.time):
                continue
            
            concept_target: Concept = term_link.target
            belief = concept_target.get_belief() # TODO: consider all beliefs.
            
            if belief is None: 
                continue

            if task == belief:
                # TODO: here
                # if task.sentence.punct == belief.sentence.punct:
                #     is_revision = revisible(task, belief)
                continue
            # TODO: currently causes infinite recursion in some cases
            # elif task.term.equal(belief.term): 
            #     continue
            elif not belief.evidential_base.is_overlaped(task.evidential_base):
                term_link_valid = term_link
                is_valid = True
                break

        
        ### IMMEDIATE

        if self.immediate_enabled:
            if not task.immediate_rules_applied: # TODO: handle other cases
                Global.States.record_premises(task)

                results = []

                backward = task.is_question or task.is_goal
                res, cached = self.inference.inference_immediate(task.sentence, backward=backward)

                if not cached:
                    results.extend(res)

                for term, truth in results:
                    # TODO: how to properly handle stamp for immediate rules?
                    # base = Base((Global.get_input_id(),))
                    # stamp_task: Stamp = Stamp(Global.time, None, None, base)
                    stamp_task = task.stamp

                    if task.is_question and term[1] == 'cnv':
                        question_derived = Question(term[0], stamp_task)
                        task_derived = Task(question_derived)
                        # set flag to prevent repeated processing
                        task_derived.immediate_rules_applied = True
                        task_derived.term._normalize_variables()
                        tasks_derived.append(task_derived)
                    
                    if task.is_goal and term[1] == 'cnv':
                        goal_derived = Goal(term[0], stamp_task, truth)
                        task_derived = Task(goal_derived)
                        # set flag to prevent repeated processing
                        task_derived.immediate_rules_applied = True
                        task_derived.term._normalize_variables()
                        tasks_derived.append(task_derived)

                    if task.is_judgement: # TODO: hadle other cases
                        budget = Budget_forward(truth, task_link.budget, None)
                        budget.priority = budget.priority * 1/term[0].complexity
                        sentence_derived = Judgement(term[0], stamp_task, truth)
                        task_derived = Task(sentence_derived, budget)
                        # set flag to prevent repeated processing
                        task_derived.immediate_rules_applied = True
                        # normalize the variable indices
                        task_derived.term._normalize_variables()
                        tasks_derived.append(task_derived)

                # record immediate rule application for task
                task.immediate_rules_applied = True


        ### STRUCTURAL
        
        if self.structural_enabled:
            if task.is_judgement or task.is_goal or task.is_question: # TODO: handle other cases
                Global.States.record_premises(task)

                results = []

                theorems = []
                for _ in range(min(self.theorems_per_cycle, len(self.all_theorems))):
                    theorem = self.all_theorems.take(remove=False)
                    theorems.append(theorem)
                
                for theorem in theorems:
                    res, cached = self.inference.inference_structural(task.sentence, theorem._theorem)

                    if not cached:
                        if res:
                            new_priority = theorem.budget.priority + 0.1
                            theorem.budget.priority = min(0.99, new_priority)
                        else:
                            new_priority = theorem.budget.priority - 0.1
                            theorem.budget.priority = max(0.1, new_priority)
                        self.all_theorems.put(theorem)

                    results.extend(res)
                    
                    for term, truth in results:
                        # TODO: how to properly handle stamp for structural rules?
                        stamp_task: Stamp = task.stamp

                        if task.is_question:
                            pass

                        if task.is_goal:
                            goal_derived = Goal(term[0], stamp_task, truth)
                            task_derived = Task(goal_derived)
                            task_derived.term._normalize_variables()
                            tasks_derived.append(task_derived)

                        if task.is_judgement: # TODO: hadle other cases
                            budget = Budget_forward(truth, task_link.budget, None)
                            budget.priority = budget.priority * 1/term[0].complexity
                            sentence_derived = Judgement(term[0], stamp_task, truth)
                            task_derived = Task(sentence_derived, budget)
                            
                            # normalize the variable indices
                            task_derived.term._normalize_variables()
                            tasks_derived.append(task_derived)
        

        if is_valid \
            and task.is_judgement: # TODO: handle other cases
            
            Global.States.record_premises(task, belief)
                    
            results = []

            # COMPOSITIONAL
            if self.compositional_enabled:
                if task.is_eternal and belief.is_eternal:
                    # events are handled in the event buffer
                    res, cached = self.inference.inference_compositional(task.sentence, belief.sentence)
                    
                    if not cached: 
                        results.extend(res)
            
            # Temporal Projection and Eternalization
            if belief is not None:
                # TODO: Handle the backward inference.
                if not belief.is_eternal and (belief.is_judgement or belief.is_goal):
                    truth_belief = project_truth(task.sentence, belief.sentence)
                    belief = belief.eternalize(truth_belief)
                    # beleif_eternalized = belief # TODO: should it be added into the `tasks_derived`?

            # SYLLOGISTIC
            res, cached = self.inference.inference(task.sentence, belief.sentence)

            if not cached:
                results.extend(res)

            for term, truth in results:

                budget = Budget_forward(truth, task_link.budget, term_link_valid.budget)

                conclusion: Term = term[0]

                # calculate new stamp
                stamp_task: Stamp = task.stamp
                stamp_belief: Stamp = belief.stamp

                # TODO: how to correctly determine order?
                order_mark = None
                whole = part = None

                if task.sentence.term.copula and task.sentence.term.copula == Copula.PredictiveImplication:
                    whole = task
                    part = belief
                if belief.sentence.term.copula and belief.sentence.term.copula == Copula.PredictiveImplication:
                    whole = belief
                    part = task

                if part and whole:
                    if part.term == whole.sentence.term.subject:
                        order_mark = Copula.PredictiveImplication
                    if part.term == whole.sentence.term.predicate:
                        order_mark = Copula.RetrospectiveImplication

                stamp = Stamp_merge(stamp_task, stamp_belief, order_mark)
                
                def add_task(term):
                    sentence_derived = Judgement(term, stamp, truth)
                    task_derived = Task(sentence_derived, budget)
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

                add_task(conclusion)

                if  conclusion.is_statement:
                    if conclusion.is_predictive or conclusion.is_retrospective:
                        add_task(conclusion.temporal_swapped())

            if term_link is not None:
                for derived_task in tasks_derived: 
                    reward: float = max(derived_task.budget.priority, task.achieving_level())
                    term_link.reward_budget(reward)

        # BACKWARD
        if is_valid \
            and task.is_question: # TODO: handle other cases

            results = []

            res, cached = self.inference.backward(task.sentence, belief.sentence)

            if not cached:
                results.extend(res)

            for term, _ in results:
                # budget = Budget_backward(truth, task_link.budget, term_link_valid.budget)

                question_derived = Question(term[0], task.stamp)
                task_derived = Task(question_derived) #, budget)
                tasks_derived.append(task_derived)

        if is_valid \
            and task.is_goal: # TODO: handle other cases

            results = []

            res, cached = self.inference.backward(task.sentence, belief.sentence)

            if not cached:
                results.extend(res)

            for term, truth in results:
                # budget = Budget_backward(truth, task_link.budget, term_link_valid.budget)
                conclusion = term[0]

                if type(conclusion) is Compound \
                and conclusion.connector == Connector.Conjunction:
                    # TODO: finish this
                    if type(belief.term) is Compound or type(belief.term) is Statement:
                        if belief.term.is_predictive:
                            conclusion = conclusion.predictive()
                        if belief.term.is_concurrent:
                            conclusion = conclusion.concurrent()

                goal_derived = Goal(conclusion, task.stamp, truth)
                task_derived = Task(goal_derived) #, budget)
                tasks_derived.append(task_derived)


        for term_link in term_links: 
            concept.term_links.put_back(term_link)
        
        return list(filter(lambda t: t.is_question or t.truth.c > 0, tasks_derived))