from typing import List
from Narsese import Term
from utils.IndexVar import IntVar

from .Substitution import Substitution

class Introduction(Substitution):
    '''
    the substitution of const-to-var
    '''
    def __init__(self, term_src: Term, term_tgt: Term, iconst_src: List[Term]=None, ivar_tgt: List[IntVar]=None, dconst_src: List[Term]=None, dvar_tgt: List[IntVar]=None, qconst_src: List[Term]=None, qvar_tgt: List[IntVar]=None) -> None:
        super().__init__(term_src, term_tgt, iconst_src, ivar_tgt, dconst_src, dvar_tgt, qconst_src, qvar_tgt)


    def apply(self, term_src: Term=None, term_tgt: Term=None):
        ''''''
        term_src = term_src if term_src is not None else self.term_src
        term_tgt = term_tgt if term_tgt is not None else self.term_tgt
        mapping_ivar = self.mapping_ivar
        mapping_dvar = self.mapping_dvar
        mapping_qvar = self.mapping_qvar
        mapping_const = self.mapping_const

        # TODO: replace const with var

        pass
