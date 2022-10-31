from typing import Dict, List, Tuple

from bidict import bidict
from pynars.Narsese import Term
from pynars.utils.IndexVar import IntVar

from .Substitution import Substitution


class Elimination(Substitution):
    '''
    the substitution of var-to-const
    '''
    def __init__(self, term_src: Term, term_tgt: Term, ivar_src: List[IntVar]=None, iconst_tgt: List[Term]=None, dvar_src: List[IntVar]=None, dconst_tgt: List[Term]=None, qvar_src: List[IntVar]=None, qconst_tgt: List[Term]=None) -> None:
        super().__init__(term_src, term_tgt) #, ivar_src, iconst_tgt, dvar_src, dconst_tgt, qvar_src, qconst_tgt)

        # is_conflict_ivar = is_conflict_dvar = is_conflict_qvar = False
        if (ivar_src is not None and iconst_tgt is not None):
            self.is_conflict_ivar, self.mapping_ivar = self.check_conflict(ivar_src, iconst_tgt)
        if (dvar_src is not None and dconst_tgt is not None):
            self.is_conflict_dvar, self.mapping_dvar = self.check_conflict(dvar_src, dconst_tgt)
        if (qvar_src is not None and qconst_tgt is not None):
            self.is_conflict_qvar, self.mapping_qvar = self.check_conflict(qvar_src, qconst_tgt)

        # self._is_conflict = is_conflict_ivar or is_conflict_dvar or is_conflict_qvar

    @property
    def is_valid(self):
        return self.is_qvar_valid or self.is_dvar_valid or self.is_ivar_valid

    @property
    def is_qvar_valid(self):
        return not self.is_conflict_qvar and len(self.mapping_qvar) > 0
    
    @property
    def is_dvar_valid(self):
        return not self.is_conflict_dvar and len(self.mapping_dvar) > 0

    @property
    def is_ivar_valid(self):
        return not self.is_conflict_ivar and len(self.mapping_ivar) > 0

    @staticmethod
    def check_conflict(vars: List[IntVar], consts: List[Term]) -> Tuple[bool, Dict[IntVar, Term]]:
        '''
        no conflict:
            (&&, <$x-->A>, <$y-->A>)
            (&&, <B-->A>, <C-->A>)
            [0, 1], [B, C]
            [0, 1], [C, B]
        conflict:
            (&&, <$x-->A>, <$x-->B>)
            (&&, <C-->A>, <D-->B>)
            [0, 0], [C, D]
        '''
        mapping_ret = bidict()
        if len(vars) != len(consts): return True, mapping_ret
        mapping = {key: set() for key in set(vars)}
        is_conflict = False
        for var, const in zip(vars, consts):
            var_list = mapping[var]
            var_list.add(const)
            if len(var_list) > 1: 
                is_conflict = True
                break
        
        if not is_conflict:
            mapping_ret = bidict({key: list(value)[0] for key, value in mapping.items()})
        return is_conflict, mapping_ret


    def apply(self, term_src: Term=None, term_tgt: Term=None):
        ''''''
        term_src = term_src if term_src is not None else self.term_src
        term_tgt = term_tgt if term_tgt is not None else self.term_tgt
        mapping_ivar = self.mapping_ivar
        mapping_dvar = self.mapping_dvar
        mapping_qvar = self.mapping_qvar
        mapping_const = self.mapping_const

        # TODO: replace var with const

        pass