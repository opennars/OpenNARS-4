from copy import deepcopy
from typing import List

from bidict import bidict
from Narsese import Term
from utils.IndexVar import IntVar


class Substitution:
    '''
    the substitutions between the terms of the same type, that is, ivar-to-ivar, dvar-to-dvar, qvar-to-qvar, const-to-const
    '''
    def __init__(self, term_src: Term, term_tgt: Term, ivar_src: List[IntVar]=None, ivar_tgt: List[IntVar]=None, dvar_src: List[IntVar]=None, dvar_tgt: List[IntVar]=None, qvar_src: List[IntVar]=None, qvar_tgt: List[IntVar]=None, const_src: List[Term]=None, const_tgt: List[Term]=None) -> None:
        '''
        len(src) == len(tgt)
        '''
        self.term_src = term_src
        self.term_tgt = term_tgt
        self.mapping_ivar = None
        self.mapping_dvar = None
        self.mapping_qvar = None
        self.mapping_const = None

        if (ivar_src is not None and ivar_tgt is not None):
            self.mapping_ivar = self._build_mapping(term_src._index_var.var_independent, term_tgt._index_var.var_independent, ivar_src, ivar_tgt)
        if (dvar_src is not None and dvar_tgt is not None):
            self.mapping_dvar = self._build_mapping(term_src._index_var.var_dependent, term_tgt._index_var.var_dependent, dvar_src, dvar_tgt)
        if (qvar_src is not None and qvar_tgt is not None):
            self.mapping_qvar = self._build_mapping(term_src._index_var.var_query, term_tgt._index_var.var_query, qvar_src, qvar_tgt)
        if (const_src is not None and const_tgt is not None):
            self.mapping_const = bidict(zip(const_src, const_tgt))

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


    def apply(self, term_src: Term=None, term_tgt: Term=None, inverse=False):
        ''''''
        term_src = term_src if term_src is not None else self.term_src
        term_tgt = term_tgt if term_tgt is not None else self.term_tgt
        mapping_ivar = self.mapping_ivar
        mapping_dvar = self.mapping_dvar
        mapping_qvar = self.mapping_qvar
        mapping_const = self.mapping_const
        if inverse:
            term_src, term_tgt = term_tgt, term_src            
            mapping_ivar = mapping_ivar.inverse if mapping_ivar is not None else None
            mapping_dvar = mapping_dvar.inverse if mapping_dvar is not None else None
            mapping_qvar = mapping_qvar.inverse  if mapping_qvar is not None else None
            mapping_const = self.mapping_const.inverse  if mapping_const is not None else None


        ivar = [int(var) for var in term_src.index_var.var_independent]
        dvar = [int(var) for var in term_src.index_var.var_dependent]
        qvar = [int(var) for var in term_src.index_var.var_query]

        # TODO: replace var with var
        term = deepcopy(term_src)
        term.index_var.var_independent = [var(mapping_ivar.get(var_int, None)) for var, var_int in zip(term._index_var.var_independent, ivar)]
        term.index_var.var_dependent = [var(mapping_dvar.get(var_int, None)) for var, var_int in zip(term._index_var.var_dependent, dvar)]
        term.index_var.var_query = [var(mapping_qvar.get(var_int, None)) for var, var_int in zip(term._index_var.var_query, qvar)]

        return term
    
    @staticmethod
    def _build_mapping(variables1, variables2, var_common1, var_common2):
        if len(variables1) > 0 and len(variables2) > 0:
            var_diff1 = sorted(list(set(variables1)-set(var_common1)))
            var_diff2 = sorted(list(set(variables2)-set(var_common2)))
            var_bias1 = max(variables1) + 1
            var_bias2 = max(variables2) + 1
            var_diff_new1 = [ivar+var_bias2 for ivar in var_diff1]
            var_diff_new2 = [ivar+var_bias1 for ivar in var_diff2]
            # mapping the second to the first
            mapping = bidict({int(key): int(value) for key, value in (*zip(var_common1, var_common2), *zip( var_diff_new2, var_diff2), *zip(var_diff1, var_diff_new1))}) 
        else:
            mapping = bidict()
        return mapping