from copy import copy
from .Truth import Truth
from .Term import Term
from .Statement import Statement
from enum import Enum
from .Tense import Tense
from typing import Type, Set

from ordered_set import OrderedSet
from .Evidence import *

from pynars.Config import Config, Enable
from pynars import Global


class Punctuation(Enum):
    Judgement = r"."
    Question = r"?"
    Goal = r"!"
    Quest = r"@"

    @property
    def is_judgement(self):
        return self == Punctuation.Judgement

    @property
    def is_question(self):
        return self == Punctuation.Question

    @property
    def is_goal(self):
        return self == Punctuation.Goal

    @property
    def is_quest(self):
        return self == Punctuation.Quest


class Stamp:

    def __init__(self, t_creation: int, t_occurrence: int, t_put: int, evidential_base: Type['Base']) -> None:
        '''
        Args:
            t_creation(int): creation time of the stamp
            t_occurrence(int): estimated occurrence time of the event
            t_put(int): the time when it was put into buffer
        '''
        self.t_creation = t_creation
        self.t_occurrence = t_occurrence
        self.t_put = t_put
        self.evidential_base: Type['Base'] = evidential_base

    @property
    def tense(self):
        return Tense.Eternal if self.t_occurrence is None else Tense.Future if self.t_occurrence >= Global.time + Config.temporal_duration else Tense.Past if self.t_occurrence <= Global.time - Config.temporal_duration else Tense.Present

    @property
    def is_eternal(self):
        # whether a sentence is from the external world or the internal world. Only those sentences derived from Mental Operations are internal.
        return self.t_occurrence is None

    def eternalize(self):
        self.t_occurrence = None

    def extend_evidenital_base(self, base: Type['Base']):
        if self.evidential_base is None:
            if base is None:
                return
            elif self.evidential_base is None:
                self.evidential_base = Base(())
        self.evidential_base.extend(base)

    def __str__(self):
        return f'{{{self.t_occurrence}: {", ".join(str(b) for b in self.evidential_base._set)}}}'

    def __repr__(self):
        return f'<Stamp: {str(self)}>'


'''
Doubt that are Question and Quest have got a tense?
'''


class Sentence:
    truth: Truth = None

    def __init__(self, term: Term, punct: Punctuation, stamp: Stamp, do_hashing: bool = False) -> None:
        ''''''
        self.term = term
        self.word = term.word + str(punct.value)
        self.punct = punct
        self.stamp: Stamp = stamp

    @property
    def evidential_base(self):
        return self.stamp.evidential_base

    @property
    def tense(self):
        return self.stamp.tense

    @property
    def directness(self):
        return len(self.stamp.evidential_base) ** -Config.t_sentence_directness_unit

    @property
    def sharpness(self):
        if self.truth is None: return None
        else: return 2 * abs(self.truth.e - 0.5)

    # @property
    # def temporal_order(self):
    #     return self.term.temporal_order

    def eternalize(self, truth: Truth = None):
        sentence = copy(self)
        if truth is not None:
            sentence.truth = truth
        stamp = copy(sentence.stamp)
        stamp.eternalize()
        sentence.stamp = stamp
        return sentence

    def __hash__(self) -> int:
        return hash((self.term, self.punct, self.truth))

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return f'<{"Sentence" if self.is_eternal else "Event"}: {self.term.repr()}{self.punct.value}>'

    # @property
    def repr(self, is_input=True):
        return self.term.repr()
    
    @property
    def is_judgement(self) -> bool:
        return self.punct == Punctuation.Judgement

    @property
    def is_goal(self) -> bool:
        return self.punct == Punctuation.Goal

    @property
    def is_question(self) -> bool:
        return self.punct == Punctuation.Question

    @property
    def is_quest(self) -> bool:
        return self.punct == Punctuation.Quest

    @property
    def is_eternal(self) -> bool:
        return self.stamp.is_eternal

    @property
    def is_event(self) -> bool:
        return not self.stamp.is_eternal

    @property
    def is_external_event(self) -> bool: # TODO: ???
        return not self.is_eternal and self.stamp.is_external


class Judgement(Sentence):
    def __init__(self, term: Term, stamp: Stamp = None, truth: Truth = None) -> None:
        ''''''
        stamp = stamp if stamp is not None else Stamp(Global.time, None, None, None)
        Sentence.__init__(self, term, Punctuation.Judgement, stamp)
        self.truth = truth if truth is not None else Truth(Config.f, Config.c, Config.k)

    def __str__(self) -> str:
        return f'{self.word}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""} {self.truth}'


    def repr(self,is_input=False):
        return f'{self.term.repr()}{self.punct.value}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""} {self.truth}'


class Goal(Sentence):
    best_solution: 'Judgement' = None

    def __init__(self, term: Term, stamp: Stamp = None, desire: Truth = None) -> None:
        ''''''
        stamp = stamp if stamp is not None else Stamp(Global.time, None, None, None, None)
        Sentence.__init__(self, term, Punctuation.Goal, stamp)
        self.truth = desire if desire is not None else Truth(Config.f, Config.c, Config.k)

    def __str__(self) -> str:
        return f'{self.word}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""} {str(self.truth)}'

    def repr(self, is_input = False):
        return f'{self.term.repr() + self.punct.value}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""} {str(self.truth)}'


class Question(Sentence):
    best_answer: 'Judgement' = None

    def __init__(self, term: Term, stamp: Stamp = None, curiosiry: Truth = None) -> None:
        ''''''
        stamp = stamp if stamp is not None else Stamp(Global.time, None, None, None, None)
        # stamp.set_eternal()
        Sentence.__init__(self, term, Punctuation.Question, stamp)
        self.is_query = False  # TODO: if there is a query variable in the sentence, then `self.is_query=True`

    def __str__(self) -> str:
        return f'{self.word}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""}'
        # return self.word + (str(self.tense.value) if self.tense != Tense.Eternal else "")

    def repr(self, is_input = False):
        return f'{self.term.repr() + self.punct.value}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""}'


class Quest(Sentence):
    best_answer: 'Goal' = None
    def __init__(self, term: Term, stamp: Stamp = None, curiosiry: Truth = None) -> None:
        ''''''
        stamp = stamp if stamp is not None else Stamp(Global.time, None, None, None, None)
        # stamp.set_eternal()
        Sentence.__init__(self, term, Punctuation.Quest, stamp)
        self.is_query = False  # TODO: if there is a query variable in the sentence, then `self.is_query=True`

    def __str__(self) -> str:
        return f'{self.word}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""}'
        # return self.word + (str(self.tense.value) if self.tense != Tense.Eternal else "")

    def repr(self, is_input = False):
        return f'{self.term.repr() + self.punct.value}{(" " + str(self.tense.value)) if self.tense != Tense.Eternal else ""}'
