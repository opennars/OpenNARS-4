from typing import Callable
from pynars.Narsese import Truth, truth_analytic
from .ExtendedBooleanFunctions import *
# from .Tools import *
from .UncertaintyMappingFunctions import *

TruthFunction = Callable[[Truth, Truth], Truth]
TruthImmedFunction = Callable[[Truth], Truth]

'''local inference'''
# F_rev
F_rev = F_revision = lambda w_p_1, w_p_2, w_m_1, w_m_2: (w_p_1 + w_p_2, w_m_1 + w_m_2)  # return: w+, w-


def Truth_revision(truth1: Truth, truth2: Truth):
    w_p_1 = fc_to_w_plus(truth1.f, truth1.c, truth1.k)
    w_p_2 = fc_to_w_plus(truth2.f, truth2.c, truth2.k)
    w_m_1 = fc_to_w_minus(truth1.f, truth1.c, truth1.k)
    w_m_2 = fc_to_w_minus(truth2.f, truth2.c, truth2.k)
    w_p, w_m = F_revision(w_p_1, w_p_2, w_m_1, w_m_2)
    truth = truth_from_w(w_p, w_m + w_p, truth1.k)
    return truth


# F_exp
F_exp = F_expectation = lambda f, c: (c * (f - 0.5) + 0.5)  # return: e

# F_dec
F_dec = F_decision = lambda p, d: p * (d - 0.5)  # return: g

'''immediate inference'''
# F_neg
F_neg = F_negation = lambda w_plus, w_minus: (w_minus, w_plus)  # return: w+, w-


def Truth_negation(truth: Truth) -> Truth:
    k = truth.k
    w_plus, w_minus = F_negation(*w_from_truth(truth))
    w = w_plus + w_minus
    return Truth(w_to_f(w_plus, w), w_to_c(w, k), k)


# F_cnv
F_cnv = F_conversion = lambda f, c: (And(f, c), 0)  # return: w+, w-


def Truth_conversion(truth: Truth) -> Truth:
    w_plus, w_minus = F_conversion(truth.f, truth.c)
    return truth_from_w(w_plus, w_plus + w_minus, truth.k)


# F_cnt
F_cnt = F_contraposition = lambda f, c: (0, And(Not(f), c))  # return: w+, w-


def Truth_contraposition(truth: Truth) -> Truth:
    w_plus, w_minus = F_contraposition(truth.f, truth.c)
    return truth_from_w(w_plus, w_plus + w_minus, truth.k)


'''strong syllogism'''
# F_ded
F_ded = F_deduction = lambda f1, c1, f2, c2: (And(f1, f2), And(f1, f2, c1, c2))  # return: f, c
Truth_deduction: TruthFunction = lambda truth1, truth2: Truth(*F_deduction(truth1.f, truth1.c, truth2.f, truth2.c),
                                                              truth1.k)

# F_ana
F_ana = F_analogy = lambda f1, c1, f2, c2: (And(f1, f2), And(f2, c1, c2))  # return: f, c
Truth_analogy: TruthFunction = lambda truth1, truth2: Truth(*F_analogy(truth1.f, truth1.c, truth2.f, truth2.c),
                                                            truth1.k)

# F_res
F_res = F_resemblance = lambda f1, c1, f2, c2: (And(f1, f2), And(Or(f1, f2), c1, c2))  # return: f, c
Truth_resemblance: TruthFunction = lambda truth1, truth2: Truth(*F_resemblance(truth1.f, truth1.c, truth2.f, truth2.c),
                                                                truth1.k)

'''weak syllogism'''
# F_abd
F_abd = F_abduction = lambda f1, c1, f2, c2: (And(f1, f2, c1, c2), And(f1, c1, c2))  # return: w+, w
Truth_abduction: TruthFunction = lambda truth1, truth2: truth_from_w(
    *F_abduction(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

# F_ind
F_ind = F_induction = lambda f1, c1, f2, c2: (And(f1, f2, c1, c2), And(f2, c1, c2))  # return: w+, w
Truth_induction: TruthFunction = lambda truth1, truth2: truth_from_w(
    *F_induction(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

# F_exe
F_ind = F_exemplification = lambda f1, c1, f2, c2: (And(f1, f2, c1, c2), And(f1, f2, c1, c2))  # return: w+, w
Truth_exemplification: TruthFunction = lambda truth1, truth2: truth_from_w(
    *F_exemplification(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)
# def Truth_exemplification(truth1: Truth, truth2: Truth) -> Truth: 
#     return truth_from_w(*F_exemplification(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

# F_com
F_com = F_comparison = lambda f1, c1, f2, c2: (And(f1, f2, c1, c2), And(Or(f1, f2), c1, c2))  # return: w+, w
Truth_comparison: TruthFunction = lambda truth1, truth2: truth_from_w(
    *F_comparison(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

'''term composition'''
# F_int
F_int = F_intersection = lambda f1, c1, f2, c2: (And(f1, f2), And(c1, c2))  # return: f, c
Truth_intersection: TruthFunction = lambda truth1, truth2: Truth(
    *F_intersection(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

# F_uni
F_uni = F_union = lambda f1, c1, f2, c2: (Or(f1, f2), And(c1, c2))  # return: f, c
Truth_union: TruthFunction = lambda truth1, truth2: Truth(*F_union(truth1.f, truth1.c, truth2.f, truth2.c), truth1.k)

# F_dif
F_dif = F_difference = lambda f1, c1, f2, c2: (And(f1, Not(f2)), And(c1, c2))  # return: f, c
Truth_difference: TruthFunction = lambda truth1, truth2: Truth(*F_difference(truth1.f, truth1.c, truth2.f, truth2.c),
                                                               truth1.k)

# F_dcj     {(&&, A, B).; B.} |- A.
Truth_deconjuntion: TruthFunction = lambda truth1, truth2: Truth_negation(
    Truth_deduction(Truth_intersection(Truth_negation(truth1), truth2), truth_analytic))

# F_ddj     {(||, A, B).; B.} |- A.
Truth_dedisjunction: TruthFunction = lambda truth1, truth2: Truth_deduction(
    Truth_intersection(truth1, Truth_negation(truth2)), truth_analytic)
