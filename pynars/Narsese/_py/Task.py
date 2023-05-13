from copy import copy
from typing import Type, Union
from .Sentence import Sentence, Judgement, Goal, Quest, Question, Stamp
from .Item import Item
from .Budget import Budget
from .Term import Term
from .Truth import Truth

class Task(Item):
    input_id = -1
    best_solution: 'Task' = None
    
    def __init__(self, sentence: Sentence, budget: Budget=None, input_id: int=None) -> None:
        super().__init__(hash(sentence), budget)
        self.sentence: Sentence = sentence
        self.input_id = self.input_id if input_id is None else input_id

    def achieving_level(self, truth_belief: Truth=None):
        if self.is_judgement:
            e_belief = truth_belief.e if truth_belief is not None else 0.5
            judgement: Judgement=self.sentence
            return 1-abs(judgement.truth.e-e_belief)
        elif self.is_goal:
            e_belief = truth_belief.e if truth_belief is not None else 0.5
            goal: Goal=self.sentence
            return 1-abs(goal.truth.e-e_belief)
        elif self.is_question:
            question: Question = self.sentence
            return truth_belief.e if question.is_query else truth_belief.c
        elif self.is_quest:
            quest: Quest = self.sentence
            return truth_belief.e if quest.is_query else truth_belief.c
        else:
            raise f'Invalid type! {type(self.sentence)}'

    def reduce_budget_by_achieving_level(self, belief_selected: Union[Type['Belief'], None]):
        truth = belief_selected.truth if belief_selected is not None else None
        self.budget.reduce_by_achieving_level(self.achieving_level(truth))

    @property
    def stamp(self) -> Stamp:
        return self.sentence.stamp
    
    @property
    def evidential_base(self):
        return self.sentence.evidential_base

    @property
    def term(self) -> Term:
        return self.sentence.term
    
    @property
    def truth(self) -> Truth:
        return self.sentence.truth
    
    @property
    def is_judgement(self) -> bool:
        return self.sentence.is_judgement
    
    @property
    def is_goal(self) -> bool:
        return self.sentence.is_goal
    
    @property
    def is_question(self) -> bool:
        return self.sentence.is_question

    @property 
    def is_quest(self) -> bool:
        return self.sentence.is_quest


    @property
    def is_query(self) -> bool:
        return self.term.has_qvar and (self.is_question or self.is_quest)

    @property
    def is_eternal(self) -> bool:
        return self.sentence.is_eternal
    
    @property
    def is_event(self) -> bool:
        return self.sentence.is_event

    @property
    def is_external_event(self) -> bool:
        return self.sentence.is_external_event

    @property
    def is_operation(self) -> bool:
        return self.term.is_operation
    
    @property
    def is_mental_operation(self) -> bool:
        return self.term.is_mental_operation

    @property
    def is_executable(self):
        return self.is_goal and self.term.is_executable
    
    def eternalize(self, truth: Truth=None):
        task = copy(self)
        task.sentence = task.sentence.eternalize(truth)
        return task

    def __str__(self) -> str:
        '''$p;d;q$ sentence %f;c%'''
        return f'{(str(self.budget) if self.budget is not None else "$-;-;-$") + " "}{self.sentence.repr(False)} {str(self.stamp)}'

    def __repr__(self) -> str:
        return str(self)

Belief = Task
Desire = Task
