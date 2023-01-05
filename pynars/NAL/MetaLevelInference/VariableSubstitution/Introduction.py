from typing import List
from pynars.Narsese import Term, Statement, Compound, VarPrefix, Variable
from pynars.utils.IndexVar import IntVar

from .Substitution import Substitution
from pynars.utils.tools import find_pos_with_pos, find_var_with_pos


class Introduction(Substitution):
    '''
    the substitution of const-to-var
    '''
    def __init__(self, term_src: Term, term_tgt: Term, term_common: Term) -> None:
        self.term_common = term_common
        self.term_src = term_src
        self.term_tgt = term_tgt


    def apply(self, term_src: Term=None, term_tgt: Term=None, type_var=VarPrefix.Independent):
        '''
        e.g.
        Input:
            term_src: <robin --> bird>
            term_tgt: <robin --> animal>
            term_common: robin
        Ouput:
            <$x --> bird>
            <$x --> animal>
        '''
        term_src = term_src if term_src is not None else self.term_src
        term_tgt = term_tgt if term_tgt is not None else self.term_tgt

        if type_var is VarPrefix.Independent:
            variables1 = term_src._vars_independent.indices
            variables2 = term_tgt._vars_independent.indices
        elif type_var is VarPrefix.Dependent:
            variables1 = term_src._vars_dependent.indices
            variables2 = term_tgt._vars_dependent.indices
        elif type_var is VarPrefix.Query:
            variables1 = term_src._vars_query.indices
            variables2 = term_tgt._vars_query.indices
        else: raise TypeError("Inalid type")
        id_var = max((*variables1, *variables2, -1)) + 1
        var = Variable(type_var, str(id_var), id_var)

        # replace const with var
        def replace(term: 'Term|Statement|Compound', term_r: Term) -> Term:
            '''
            replace constant term with variable
            
            term_r should be a constant
            '''
            nonlocal var
            if term.identical(term_r):
                ''''''
                return var, True
            
            if term.is_statement:
                if term_r not in term.components: # term.components is not None
                    return term, False
                stat: Statement = term
                predicate, flag1 = replace(stat.predicate, term_r)
                subject, flag2 = replace(stat.subject, term_r)
                flag = max(flag1, flag2)
                if flag:
                    stat = Statement(subject, term.copula, predicate)
                return stat, flag
            elif term.is_compound:
                if term_r not in term.components: # term.components is not None
                    return term, False
                cpmd: Compound = term
                terms, flags = zip(*(replace(component, term_r) for component in cpmd.terms))
                flag = max(flags)
                if flag:
                    cpmd = Compound(cpmd.connector, *terms)
                return cpmd, flag
            elif term.is_atom:
                return term, False

        term1, _ = replace(term_src, self.term_common)
        term2, _ = replace(term_tgt, self.term_common)
        return term1, term2
        


def get_introduction__const_var(term1: Term, term2: Term, term_common: Term) -> Introduction:
    ''''''
    return Introduction(term1, term2, term_common)

