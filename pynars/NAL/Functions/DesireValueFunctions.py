from typing import Callable
from pynars.Narsese import Truth
from .ExtendedBooleanFunctions import *
from .UncertaintyMappingFunctions import w_to_c

DesireFuncion = Callable[[Truth, Truth], Truth]


Desire_strong: DesireFuncion = lambda desire1, desire2: Truth(And(desire1.f, desire2.f), And(desire1.c, desire2.c, desire2.f), desire1.k)

Desire_weak: DesireFuncion = lambda desire1, desire2: Truth(And(desire1.f, desire2.f), And(desire1.c, desire2.c, desire2.f, w_to_c(1.0, desire1.k)), desire1.k)

Desire_deduction: DesireFuncion = lambda desire1, desire2: Truth(And(desire1.f, desire2.f), And(desire1.c, desire2.c), desire1.k)

Desire_induction: DesireFuncion = lambda desire1, desire2: Truth(desire1.f, w_to_c(And(desire2.f, desire1.c, desire2.c), desire1.k), desire1.k)
