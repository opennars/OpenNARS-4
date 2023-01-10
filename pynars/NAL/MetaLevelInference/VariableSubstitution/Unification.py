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
from .Substitution import get_substitution__var_var
from .Introduction import get_introduction__const_var
from .Elimination import get_elimination__var_const

'''
"The procedure of finding a possible substitution is called “unification”, which has been specified in the study of reasoning systems [Russell and Norvig (2010)]. "[Ref: NAL Book, Page 133]
'''


def unify__substitution(term1: Term, term2: Term, pos1_common1: list, pos2_common: list) -> Substitution:
    '''
    Fir example:
        term1: <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> (&&, <$z-->F>, <#p-->G>, <#p-->H>)>.
        term2: <<(&&, <$x-->F>, <#p-->G>, <#p-->H>)==><$x-->H>>.
        term_common: 
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
    '''
    return get_substitution__var_var(term1, term2, pos1_common1, pos2_common)

def unify__elimination(term1: Term, term2: Term, pos1_common1: list, pos2_common: list) -> Elimination:
    ''''''
    return get_elimination__var_const(term1, term2, pos1_common1, pos2_common)

def unify__introduction(term1: Term, term2: Term, term_common: Term) -> Introduction:
    ''''''
