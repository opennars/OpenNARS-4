'''
**Variable substitution.** All occurrences of an independent variable term in a statement can be substituted by another term (constant or variable); all occurrences of a term (constant or variable) in a statement can be substituted by a dependent variable term. The reverse cases of these substitution are limited to the cases discussed in NAL-6. A query variable in a question can be substituted by a constant term in a judgment.
'''

from copy import deepcopy
from typing import Callable, Dict, List, Tuple, Union

from bidict import bidict
from pynars.Narsese import Term
from pynars.Narsese import Statement, Compound
from pynars.utils.IndexVar import IndexVar, IntVar
from pynars.utils.tools import find_pos_with_pos, find_var_with_pos

from .Substitution import Substitution
from .Elimination import Elimination
from .Introduction import Introduction

# find_var_with_pos: Callable = lambda pos_search, variables, positions: [var for var, pos in zip(variables, positions) if pos[:len(pos_search)] == pos_search] # find those variables with a common head of position. e.g. pos_search=[0], variables=[1, 1, 2, 2], and positions=[[0, 2, 0, 0], [0, 2, 1, 0], [0, 3, 0], [1, 0]], then return [1, 1, 2]
# find_pos_with_pos: Callable = lambda pos_search, positions: [pos for pos in positions if pos[:len(pos_search)] == pos_search]
def unification__var_var(term1: Term, term2: Term, pos_common1: List[IntVar], pos_common2: List[IntVar]) -> Substitution:
    '''
    It should be ensured that `term1[pos_common1].equal(term2[pos_common2]) == True`.
    '''
    # 1. find the variables in the first common position
    ivar1 = find_var_with_pos(pos_common1, term1._index_var.var_independent, term1._index_var.positions_ivar)
    dvar1 = find_var_with_pos(pos_common1, term1._index_var.var_dependent, term1._index_var.positions_dvar)
    qvar1 = find_var_with_pos(pos_common1, term1._index_var.var_query, term1._index_var.positions_qvar)

    # 2. find the variables in the second common position
    ivar2 = find_var_with_pos(pos_common2, term2._index_var.var_independent, term2._index_var.positions_ivar)
    dvar2 = find_var_with_pos(pos_common2, term2._index_var.var_dependent, term2._index_var.positions_dvar)
    qvar2 = find_var_with_pos(pos_common2, term2._index_var.var_query, term2._index_var.positions_qvar)

    return Substitution(term1, term2, ivar1, ivar2, dvar1, dvar2, qvar1, qvar2)


def unification__const_var(term1: Term, term2: Term, pos_common1: List[IntVar], pos_common2: List[IntVar]) -> Introduction:
    ''''''

    return Introduction(...)


def unification__var_const(term1: Term, term2: Term, pos_common1: List[IntVar], pos_common2: List[IntVar]) -> Elimination:
    '''
    It should be ensured that `term1[pos_common1].equal(term2[pos_common2]) == True`.
    e.g. 
    term1: <<$0-->A>==><$0-->B>>>
    term2: <<C-->B>==><C-->D>>>
    pos_common1: [1]
    pos_common1: [0]
    '''
    ivar = find_var_with_pos(pos_common1, term1.index_var.var_independent, term1.index_var.positions_ivar)
    dvar = find_var_with_pos(pos_common1, term1.index_var.var_dependent, term1.index_var.positions_dvar)
    qvar = find_var_with_pos(pos_common1, term1.index_var.var_query, term1.index_var.positions_qvar)

    iconst = [term2[pos_common2][pos[len(pos_common2):]] for pos in find_pos_with_pos(pos_common1, term1.index_var.positions_ivar)]
    dconst = [term2[pos_common2][pos[len(pos_common2):]] for pos in find_pos_with_pos(pos_common1, term1.index_var.positions_dvar)]
    qconst = [term2[pos_common2][pos[len(pos_common2):]] for pos in find_pos_with_pos(pos_common1, term1.index_var.positions_qvar)]

    # 1. To find an option: there might be multiple options, and choose one of them randomly, e.g., [$x, $y] might be [A, B] or [B, A].
    
    # 2. Check conflicts: there should be no conflicts, e.g., $x cannot be A and B simultaneously.

    # BUG: 
    # when the compound is commutative, the positions of const-terms and variables are not in correspondance.
    # testcase: 
    #   (&&, <a-->b>, <c-->d>).
    #   (&&, <?x-->b>, <c-->d>)?
    #   1
    #   ''outputMustContain('(&&, <a-->b>, <c-->d>).')
    return Elimination(term1, term2, ivar, iconst, dvar, dconst, qvar, qconst)


def unification() -> Substitution:
    ''''''