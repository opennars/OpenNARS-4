from typing import Tuple, Type, List, Union

from pynars.NAL.Functions import Or
from pynars.NAL.Functions.Tools import calculate_solution_quality, distribute_budget_among_links
from pynars.NAL.Functions.BudgetFunctions import Budget_merge
from pynars.Narsese import Belief, Task, Item, Budget, Sentence, Term, Task, Judgement, Goal
from pynars.Narsese._py.Sentence import Quest, Question
# from .Link import Link, TermLink, TaskLink, LinkType
from .Link import *
from .Table import Table
from .Bag import Bag
from pynars.Config import Config, Enable
from pynars.Narsese import place_holder

class Concept(Item):
    '''Ref: OpenNARS 3.0.4 Concept.java'''

    # seq_before: Bag # Recent events that happened before the operation the concept represents was executed. 
    task_links: Bag
    term_links: Bag
    
    # *Note*: since this is iterated frequently, an array should be used. To avoid iterator allocation, use .get(n) in a for-loop
    question_table: Table # Pending Question directly asked about the term
    quest_table: Table # Pending Question directly asked about the term
    executable_preconditions: Table
    belief_table: Table # Judgments directly made about the term Use List because of access and insertion in the middle
    general_executable_preconditions: Table
    
    desire_table: Table # Desire values on the term, similar to the above one

    termLinkTemplates: List[TermLink] # Link templates of TermLink, only in concepts with CompoundTerm Templates are used to improve the efficiency of TermLink building

    _subterms: List[Term]


    def __init__(self, term: Term, budget: Budget, capacity_table: int=None) -> None:
        super().__init__(hash(term), budget)
        self._term = term

        capacity_table = Config.capacity_table if capacity_table is None else capacity_table
        nlevels_term_link_bag = Config.nlevels_term_link
        capacity_term_link_bag = Config.capacity_term_link
        nlevels_task_link_bag = Config.nlevels_task_link
        capacity_task_link_bag = Config.capacity_task_link

        self._term = term
        self.belief_table = Table(capacity_table) 
        self.desire_table = Table(capacity_table) 
        self.question_table = Table(capacity_table)
        self.quest_table = Table(capacity_table)
        self.term_links = Bag(capacity_term_link_bag, nlevels_term_link_bag)
        self.task_links = Bag(capacity_task_link_bag, nlevels_task_link_bag)

        self.executable_preconditions = Table(capacity_table)
        self.general_executable_preconditions = Table(capacity_table)

        self.task_links = Bag(Config.capacity_task_link, Config.nlevels_task_link)
        self.term_links = Bag(Config.capacity_term_link, Config.nlevels_term_link)

        # self._cache_subterms()
        # self.accept(task)

    @property
    def term(self) -> Term:
        return self._term

    def get_belief(self) -> Belief:
        ''''''
        if Enable.temporal_reasoning:
            #  final Sentence belief = beliefT.sentence;
            # nal.emit(BeliefSelect.class, belief);
            # nal.setTheNewStamp(taskStamp, belief.stamp, currentTime);
            
            # final Sentence projectedBelief = belief.projection(taskStamp.getOccurrenceTime(), nal.time.time(), nal.memory);
            # /*if (projectedBelief.getOccurenceTime() != belief.getOccurenceTime()) {
            #    nal.singlePremiseTask(projectedBelief, task.budget);
            # }*/
            
            # return projectedBelief;     // return the first satisfying belief
            raise
        # if self.belief_table.empty:
        #     for term_link in self.term_links:
        #         if not term_link.target.belief_table.empty:
        #             return term_link.target.belief_table.first()
        return self.belief_table.first()

    # def match_candidate(self, sentence: Sentence) -> Task | Belief:
    #     if sentence.is_judgement:
    #         return self.match_belief(sentence)
    #     elif sentence.is_goal:
    #         return self.match_desire(sentence)
    #     else:
    #         raise "Invalid type." # TODO: What about question and quest?

    def match_belief(self, sentence: Union[Judgement, Question, Goal]) -> Belief:
        '''
        Select a belief with highest quality, within the belief_table, according to the task
        '''
        belief_table: List[Task] = self.belief_table
        if len(belief_table) == 0: return None
        qualities = [(calculate_solution_quality(sentence, task.sentence), task) for task in belief_table]
        _, item_max = max(qualities, key=lambda quality: quality[0])
        return item_max
        
    def add_belief(self, task: Task) -> Union[Judgement, None]:
        ''''''
        self.belief_table.add(task, task.truth.c)
    
    def get_desire(self, task: Task) -> Union[Judgement, None]:
        ''''''
        self.desire_table.first(task, task.truth.c)

    def match_desire(self, goal: Goal) -> Task:
        '''
        Select a desire with highest quality, within the desire_table, according to the task
        '''
        desire_table: List[Task] = self.desire_table
        if len(desire_table) == 0: return None
        qualities = [(calculate_solution_quality(goal, task.sentence), task) for task in desire_table]
        _, item_max = max(qualities, key=lambda quality: quality[0])
        return item_max

    def add_desire(self, task: Task) -> Union[Task, None]:
        ''''''
        # goal: Goal = task.sentence
        self.desire_table.add(task, task.truth.c)

    def accept(self, task: Task, concepts: Bag=None, conceptualize: bool=True):
        '''
        Ref: The Conceptual Design of OpenNARS 3.1.0
            **accept task-link:** Pre-process the task using the information local to the con-
            cept, then add the link into the task-link bag so as to process it repeatedly
            in the future.
        '''
        # if task.is_judgement:
        #     self.belief_table.add(task, task.sentence.truth.c)
        if concepts is None: return

        budget = task.budget
        if budget.is_above_thresh:
            if conceptualize:
                concept = Concept._conceptualize(concepts, self.term, budget)
                if concept is None: return # The memroy is full, and the concept fails to get into the memory.
            self._build_task_links(concepts, task)
            self._build_term_links(concepts, task, budget)

    def update_priority(self, p, concepts: Bag):
        concepts.take_by_key(key=self,remove=True)
        self.budget.priority = Or(self.budget.priority, p)
        concepts.put(item=self)

    def update_durability(self, d, concepts: Bag):
        concepts.take_by_key(key=self, remove=True)
        self.budget.durability = (Config.concept_update_durability_weight * d
                                + (1-Config.concept_update_durability_weight)*self.budget.durability)
        concepts.put(item=self)

    def update_quality(self, q, concepts: Bag):
        concepts.take_by_key(key=self, remove=True)
        self.budget.quality = (Config.concept_update_quality_weight * q
                                + (1-Config.concept_update_quality_weight)*self.budget.quality)
        concepts.put(item=self)
    
    def _build_task_links(self, concepts: Bag, task: Task):
        ''''''
        budget = task.budget
        task_link = TaskLink(self, task, budget, True, index=[])
        self._insert_task_link(task_link, concepts)
        if self.term.is_atom: return
        sub_budget = budget.distribute(self.term.count()-1) # TODO: It seems that the budget is not the same with that in OpenNARS 3.0.4/3.1.0. Check here.
        for term in self.term.components:
            if term == place_holder: continue # should it skip the `place_holder?`
            concept = Concept._conceptualize(concepts, term, sub_budget)
            if concept is None: continue
            
            indices = Link.get_index(self.term, term)
            for index in indices:
                task_link = TaskLink(concept, task, sub_budget, index=index)
                concept._insert_task_link(task_link, concepts)

    def _build_term_links(self, concepts: Bag, task: Task, budget: Budget):
        '''
        Get component-terms to be concepualized and build links by DFS (Depth-Fist-Search).
        '''
        if self.term.count() == 1: return # atomic term

        sub_budget = budget.distribute(self.term.count()-1) # TODO: in the case that there are some terms not being used to build term-links, the count here is not valid, which should be modified.
        if sub_budget.is_above_thresh:
            if self.term.is_atom: return
            
            for term in self.term.components:
                if term == place_holder: continue # should it skip the `place_holder?`
                
                # Option 1
                # # in _build_task_links(...), the terms all have been conceptualized.
                # # therefore, here if a concept is not in memory, it should not be used for term-links construction.
                # sub_concept: Concept = concepts.take_by_key(term, False) 

                # Option 2
                # again, conceptualize
                sub_concept: Concept = Concept._conceptualize(concepts, term, task.budget)
                if sub_concept is None: continue

                indices = Link.get_index(self.term, term)
                for index in indices:
                    self._insert_term_link(TermLink(self, sub_concept, sub_budget, False, index=index), concepts)
                    sub_concept._insert_term_link(TermLink(sub_concept, self, sub_budget, True, index=index), concepts)

                    sub_concept._build_term_links(concepts, task, sub_budget)
        

    def _insert_task_link(self, task_link: TaskLink, concepts: Bag):
        self.task_links.put(task_link)
        # update the concept's budget using the link's budget
        self.update_priority(task_link.budget.priority, concepts)
        self.update_durability(task_link.budget.durability, concepts)
        # TODO: more handling. see OpenNARS 3.1.0 Concept.java line 318~366.
    
    def _insert_term_link(self, term_link: TermLink, concepts: Bag):
        self.term_links.put(term_link)
        # update the concept's budget using the link's budget
        self.update_priority(term_link.budget.priority, concepts)
        self.update_durability(term_link.budget.durability, concepts)
        # TODO: more handling. see OpenNARS 3.1.0 Concept.java line 318~366.

    @classmethod
    def _conceptualize(cls, concepts: Bag, term: Term, budget: Budget):
        '''
        Conceptualize a task. 
        If the concept of the task is already in the memory, then merge the concept into the existed one.
        Otherwise, make up a new concept and add it into the memory.
        '''
        if Enable.temporal_reasoning:
            # if(term instanceof Interval) {
            #     return null;
            # }
            # term = CompoundTerm.replaceIntervals(term);
            raise # TODO

        if term.is_var: return None
        
        concept = concepts.take_by_key(term, True) # take the concept from the bag

        if concept is not None:
            Budget_merge(concept.budget, budget) # Merge the term into the concept if the concept has existed
            # Note: The budget handling here is sort of different from that in OpenNARS 3.1.0, see `Memory.java line 207` and `BudgetFunction.java line 167~170` in OpenNARS 3.1.0.
        else:
            concept = Concept(term, budget) # build the current concept if there has not been the concept in the bag

        concept_popped = concepts.put_back(concept) # TODO: Check here. `put` or `put_back`?
        if concept_popped is not None and concept == concept_popped:
            concept = None
        return concept

    def __eq__(self, concept: Type['Concept']):
        return concept.term == self.term
        
    def __hash__(self):
        return hash(self.term)

    def __str__(self):
        return f'{self.budget} {self.term}'

    def __repr__(self):
        return f'<Concept: {self.term.repr()}>'
