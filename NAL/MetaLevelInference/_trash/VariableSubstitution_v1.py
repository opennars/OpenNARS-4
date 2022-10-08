'''
**Variable substitution.** All occurrences of an independent variable term in a statement can be substituted by another term (constant or variable); all occurrences of a term (constant or variable) in a statement can be substituted by a dependent variable term. The reverse cases of these substitution are limited to the cases discussed in NAL-6. A query variable in a question can be substituted by a constant term in a judgment.
'''

from typing import Callable, List, Union

from bidict import bidict
from pynars.Narsese import Term
from pynars.Narsese import Statement, Compound
from pynars.utils.IndexVar import IndexVar


class SubstituteVar:
    ''''''
    def __init__(self, mapping_ivar: bidict, mapping_dvar: bidict, mapping_qvar: bidict) -> None:
        self.mapping_ivar = mapping_ivar
        self.mapping_dvar = mapping_dvar
        self.mapping_qvar = mapping_qvar
    
    @property
    def is_valid(self):
        return len(self.mapping_dvar) > 0 or len(self.mapping_ivar) > 0 or len(self.mapping_qvar) > 0

    @property
    def is_qvar_valid(self):
        return len(self.mapping_qvar) > 0
    
    @property
    def is_dvar_valid(self):
        return len(self.mapping_dvar) > 0

    @property
    def is_ivar_valid(self):
        return len(self.mapping_ivar) > 0
    
    def apply(self, term1: Term, term2: Term, inverse=False):
        mapping_ivar = self.mapping_ivar
        mapping_dvar = self.mapping_dvar
        mapping_qvar = self.mapping_qvar
        if inverse:
            term1, term2 = term2, term1            
            mapping_ivar = mapping_ivar.inverse
            mapping_dvar = mapping_dvar.inverse
            mapping_qvar = mapping_qvar.inverse
        ivar = [int(var) for var in term2._index_var.var_independent]
        dvar = [int(var) for var in term2._index_var.var_dependent]
        qvar = [int(var) for var in term2._index_var.var_query]

        term2._index_var.var_independent = [var(mapping_ivar[var_int]) for var, var_int in zip(term2._index_var.var_independent, ivar)]
        term2._index_var.var_dependent = [var(mapping_dvar[var_int]) for var, var_int in zip(term2._index_var.var_dependent, dvar)]
        term2._index_var.var_query = [var(mapping_qvar[var_int]) for var, var_int in zip(term2._index_var.var_query, qvar)]
        # TODO: to recursively apply the variable-mapping to the terms.


def substitution(R: Union[Term, Statement, Compound], S: Term, T: Term) -> Term:
    '''
    Refer to the definition in NAL:
        Definition 10.6. For given terms R, S, T, a substitution R{S/T} produces a new term by replacing all occurrences of S by T in R, under the condition that S does not occur in T.
    Args:
        R (Term): the original term.
        S (Term): the term to be substituted in R.
        T (Term): the term to substitute S.
    Returns:
        R_new (Term): the new term after substitution.
    '''
    if R.is_atom:
        R_new = T if R == S else R
    elif R.is_statement:
        subject = substitution(R.subject, S, T)
        predicate = substitution(R.predicate, S, T)
        R_new = Statement(subject, R.copula, predicate)
    elif R.is_compound:
        components = (substitution(component, S, T) for component in R)
        R_new = Compound(R.connector, *components)
    else: raise "Invalid case."
    return R_new


_find_var_with_pos: Callable = lambda pos_search, variables, positions: [var for var, pos in zip(variables, positions) if pos[:len(pos_search)] == pos_search]

def _build_mapping(variables1, variables2, var_common1, var_common2):
    if len(variables1) == 0 and len(variables2) == 0:
        mapping = bidict()
    elif len(variables1) > 0 and len(variables2) > 0:
        var_diff1 = sorted(list(set(variables1)-set(var_common1)))
        var_diff2 = sorted(list(set(variables2)-set(var_common2)))
        var_bias1 = max(variables1) + 1
        var_bias2 = max(variables2) + 1
        var_diff_new1 = [ivar+var_bias2 for ivar in var_diff1]
        var_diff_new2 = [ivar+var_bias1 for ivar in var_diff2]
        # mapping the second to the first
        mapping = bidict({int(key): int(value) for key, value in (*zip(var_common2, var_common1), *zip(var_diff2, var_diff_new2), *zip(var_diff_new1, var_diff1))})
    else: # (len(variables1) > 0) ^ (len(variables2) > 0)
        
        mapping = bidict()
        pass
    return mapping

def unification_variable(term1: Term, term2: Term, pos_common1: List[int], pos_common2: List[int]):
    ''''''
    # 1. find the variables in the first common position
    ivar1 = _find_var_with_pos(pos_common1, term1._index_var.var_independent, term1._index_var.positions_ivar)
    dvar1 = _find_var_with_pos(pos_common1, term1._index_var.var_dependent, term1._index_var.positions_dvar)
    qvar1 = _find_var_with_pos(pos_common1, term1._index_var.var_query, term1._index_var.positions_qvar)

    # 2. find the variables in the second common position
    ivar2 = _find_var_with_pos(pos_common2, term2._index_var.var_independent, term2._index_var.positions_ivar)
    dvar2 = _find_var_with_pos(pos_common2, term2._index_var.var_dependent, term2._index_var.positions_dvar)
    qvar2 = _find_var_with_pos(pos_common2, term2._index_var.var_query, term2._index_var.positions_qvar)

    # 3. build the mapping
    mapping_ivar = _build_mapping(term1._index_var.var_independent, term2._index_var.var_independent, ivar1, ivar2)
    mapping_dvar = _build_mapping(term1._index_var.var_dependent, term2._index_var.var_dependent, dvar1, dvar2)
    mapping_qvar = _build_mapping(term1._index_var.var_query, term2._index_var.var_query, qvar1, qvar2)

    return SubstituteVar(mapping_ivar, mapping_dvar, mapping_qvar)


def unification_var_to_const(term_var: Term, term_const: Term, pos_common_var: List[int], pos_common_const: List[int]):
    ''''''
    # 1. find the variables in the first common position
    ivar = _find_var_with_pos(pos_common_var, term_var._index_var.var_independent, term_var._index_var.positions_ivar)
    dvar = _find_var_with_pos(pos_common_var, term_var._index_var.var_dependent, term_var._index_var.positions_dvar)
    qvar = _find_var_with_pos(pos_common_var, term_var._index_var.var_query, term_var._index_var.positions_qvar)

    # 2. find the variables in the second common position
    iconst = _find_var_with_pos(pos_common_const, term_const._index_var.var_independent, term_const._index_var.positions_ivar)
    dconst = _find_var_with_pos(pos_common_const, term_const._index_var.var_dependent, term_const._index_var.positions_dvar)
    qconst = _find_var_with_pos(pos_common_const, term_const._index_var.var_query, term_const._index_var.positions_qvar)

    # 3. build the mapping
    mapping_ivar = _build_mapping(term_var._index_var.var_independent, term_const._index_var.var_independent, ivar, iconst)
    mapping_dvar = _build_mapping(term_var._index_var.var_dependent, term_const._index_var.var_dependent, dvar, dconst)
    mapping_qvar = _build_mapping(term_var._index_var.var_query, term_const._index_var.var_query, qvar, qconst)

    return SubstituteVar(mapping_ivar, mapping_dvar, mapping_qvar)

def unification(term1: Term, term2: Term, term_common1: Term, term_common2: Term):
    '''
    According to the variable-indexes of `term_common1` and `term_common2`, get a map and apply it to `term2`. The variable-index of the `term2` will be unified to that of `term1`.
    '''
    # 1. variable substitution

    # 2. variable introduction

    # 3. variable elimination
    term_unified: Term = None
    return term_unified


def introduction(term: Term):
    ''''''


def elimination(term: Term):
    ''''''