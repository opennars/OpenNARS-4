from typing import Dict, List, Tuple

from bidict import bidict
from pynars.Narsese import Term, Statement, Compound, VarPrefix, Variable
from pynars.utils.IndexVar import IntVar

from .Substitution import Substitution
from pynars.utils.tools import find_pos_with_pos, find_var_with_pos, find_pos_with_var
from typing import Set

class Elimination(Substitution):
    '''
    the substitution of var-to-const
    '''
    def __init__(self, term_var: Term, term_con: Term, ivar_src: List[IntVar]=None, iconst_tgt: List[Term]=None, dvar_src: List[IntVar]=None, dconst_tgt: List[Term]=None, qvar_src: List[IntVar]=None, qconst_tgt: List[Term]=None) -> None:
        # super().__init__(term_src, term_tgt) #, ivar_src, iconst_tgt, dvar_src, dconst_tgt, qvar_src, qconst_tgt)
        self.term_var = term_var
        self.term_con = term_con

        # is_conflict_ivar = is_conflict_dvar = is_conflict_qvar = False
        if (ivar_src is not None and iconst_tgt is not None):
            self.is_conflict_ivar, self.mapping_ivar = self.check_conflict(ivar_src, iconst_tgt)
        else:
            self.mapping_ivar = bidict()
        if (dvar_src is not None and dconst_tgt is not None):
            self.is_conflict_dvar, self.mapping_dvar = self.check_conflict(dvar_src, dconst_tgt)
        else:
            self.mapping_dvar = bidict()
        if (qvar_src is not None and qconst_tgt is not None):
            self.is_conflict_qvar, self.mapping_qvar = self.check_conflict(qvar_src, qconst_tgt)
        else:
            self.mapping_qvar = bidict()

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
        mapping = {int(key): set() for key in set(vars)}
        is_conflict = False
        for var, const in zip(vars, consts):
            var_list = mapping[int(var)]
            var_list.add(const)
            if len(var_list) > 1: 
                is_conflict = True
                break
        
        if not is_conflict:
            mapping_ret = bidict({key: list(value)[0] for key, value in mapping.items()})
        return is_conflict, mapping_ret


    # def apply(self, term_var: Term=None, term_con: Term=None):
    #     ''''''
    #     term_var = term_var if term_var is not None else self.term_var
    #     term_con = term_con if term_con is not None else self.term_con
    #     mapping_ivar = self.mapping_ivar
    #     mapping_dvar = self.mapping_dvar
    #     mapping_qvar = self.mapping_qvar
        
    #     # replace const with var
    #     def replace(term: 'Term|Statement|Compound',  pos_tree: dict, current_node: dict, var_type: VarPrefix) -> Term:
    #         '''
    #         replace a variable term with a constant term
            
    #         term_r should be a constant
    #         '''
    #         if not term.has_var: 
    #             return
    #         elif var_type is VarPrefix.Independent and not term.has_ivar:
    #             return
    #         elif var_type is VarPrefix.Dependent and not term.has_dvar:
    #             return
    #         elif var_type is VarPrefix.Query and not term.has_dvar:
    #             return
            
    #         if term.is_statement:
    #             stat: Statement = term
    #             subject = stat.subject
    #             predicate = stat.predicate
    #             for is_leaf, content in current_node.values():
    #                 if not is_leaf:
    #                     if content == 0:
    #                         subject = replace(stat.predicate, pos_tree, )

    #             predicate = replace(stat.predicate, term_r)
    #             subject = replace(stat.subject, term_r)
    #             return Statement(subject, term.copula, predicate, is_input=True)
    #         elif term.is_compound:
    #             if term_r not in term.components: # term.components is not None
    #                 return term
    #             cpmd: Compound = term
    #             terms = (component for component in cpmd.terms)
    #             return Compound(cpmd.connector, *terms, is_input=True)
    #         elif term.is_atom:
    #             return term

        

    #     # TODO: replace var with const
    #     if not self.is_conflict_ivar:
    #         ''''''
            
    #         mapping_pos = {}
    #         for var, const in mapping_ivar.items():
    #             pos = tuple(tuple(p) for p in find_pos_with_var(var, term_var._vars_independent.indices, term_var._vars_independent.positions))
    #             mapping_pos[pos] = const
            
    #         tree = {}
    #         for pos, const in mapping_pos.items():
    #             p1=None
    #             node = tree
    #             for p2 in pos[:-1]:
    #                 if p1 not in node:
    #                     node[p1] = (False, {p2: {}})
    #                 p1 = p2
    #             tree[pos[-1]] = (True, const)

    #         if len(mapping_pos) > 0:
    #             term_result = replace(term_var, tree, tree[None], VarPrefix.Independent)

    #     pass

    def apply(self, term_var: Term=None, term_con: Term=None, type_var: Set[VarPrefix]={VarPrefix.Independent, VarPrefix.Dependent, VarPrefix.Query}):
        ''''''
        if isinstance(type_var, VarPrefix):
            type_var = {type_var}
        term_var = term_var if term_var is not None else self.term_var
        term_con = term_con if term_con is not None else self.term_con
        mapping_ivar = self.mapping_ivar
        mapping_dvar = self.mapping_dvar
        mapping_qvar = self.mapping_qvar

        # replace var with const
        def replace(term: 'Term|Statement|Compound', mapping: dict, var_type: VarPrefix) -> Term:
            '''
            replace a variable term with a constant term
            
            term_r should be a constant
            '''
            if not term.has_var: 
                return term, False
            elif var_type is VarPrefix.Independent and not term.has_ivar:
                return term, False
            elif var_type is VarPrefix.Dependent and not term.has_dvar:
                return term, False
            elif var_type is VarPrefix.Query and not term.has_dvar:
                return term, False
            
            if term.is_atom and term.is_var:
                if var_type is VarPrefix.Independent:
                    idx = term._vars_independent.indices[0]
                elif var_type is VarPrefix.Dependent:
                    idx = term._vars_dependent.indices[0]
                elif var_type is VarPrefix.Query:
                    idx = term._vars_query.indices[0]
                else: raise TypeError("Invalide case")
                idx = int(idx)
                if idx in mapping:
                    const = mapping[idx]
                    return const, True
                else:
                    return term, False

            if term.is_statement:
                stat: Statement = term
                predicate, flag1 = replace(stat.predicate, mapping, var_type)
                subject, flag2 = replace(stat.subject, mapping, var_type)
                flag = max(flag1, flag2)
                if flag:
                    stat = Statement(subject, term.copula, predicate)
                return stat, flag
            elif term.is_compound:
                cpmd: Compound = term
                terms, flags = zip(*(replace(component, mapping, var_type) for component in cpmd.terms))
                flag = max(flags)
                if flag:
                    cpmd = Compound(cpmd.connector, *terms)
                return cpmd, flag
            elif term.is_atom:
                return term, False

        term_result = term_var
        if VarPrefix.Independent in type_var and not self.is_conflict_ivar and len(mapping_ivar) > 0:
            term_result, _ = replace(term_result, mapping_ivar, VarPrefix.Independent)
        if VarPrefix.Dependent in type_var and not self.is_conflict_dvar and len(mapping_dvar) > 0:
            term_result, _ = replace(term_result, mapping_dvar, VarPrefix.Dependent)
        if VarPrefix.Query in type_var and not self.is_conflict_qvar and len(mapping_qvar) > 0:
            term_result, _ = replace(term_result, mapping_qvar, VarPrefix.Query)
        return term_result

    def __repr__(self):
        mappings = []
        if not self.is_conflict_ivar: mappings.append({f'${int(key)}': val for key, val in self.mapping_ivar.items()})
        if not self.is_conflict_dvar: mappings.append({f'#{int(key)}': val for key, val in self.mapping_dvar.items()})
        if not self.is_conflict_qvar: mappings.append({f'?{int(key)}': val for key, val in self.mapping_qvar.items()})
        mappings = [str(m) for m in mappings if len(m) > 0]
        if len(mappings) == 0:
            mappings = 'None'
        else:
            mappings = ', '.join(mappings)
        return f'<Elimination: {mappings}>'

def get_elimination__var_const(term1: Term, term2: Term, pos_common1: List[IntVar], pos_common2: List[IntVar]) -> Elimination:
    '''
    It should be ensured that `term1[pos_common1].equal(term2[pos_common2]) == True`.
    e.g. 
    term1: <<$0-->A>==><$0-->B>>>
    term2: <<C-->B>==><C-->D>>>
    pos_common1: [1]
    pos_common2: [0]
    '''
    if not term1[pos_common1].equal(term2[pos_common2]):
        return None
        
    # ivar = find_var_with_pos(pos_common1, term1._vars_independent.indices, term1._vars_independent.positions)
    dvar = find_var_with_pos(pos_common1, term1._vars_dependent.indices, term1._vars_dependent.positions)
    qvar = find_var_with_pos(pos_common1, term1._vars_query.indices, term1._vars_query.positions)

    # iconst = [term2[pos_common2][pos[len(pos_common1):]] for pos in find_pos_with_pos(pos_common1, term1._vars_independent.positions)]
    iconst = []
    ivar = []
    for pos, var in zip(find_pos_with_pos(pos_common1, term1._vars_independent.positions), find_var_with_pos(pos_common1, term1._vars_independent.indices, term1._vars_independent.positions)):
        pos = pos[len(pos_common1):]
        term = term2[pos_common2]
        if len(pos) <= term._height:
            const = term[pos]
            iconst.append(const)
            ivar.append(var)
    dconst = [term2[pos_common2][pos[len(pos_common1):]] for pos in find_pos_with_pos(pos_common1, term1._vars_dependent.positions)]
    qconst = [term2[pos_common2][pos[len(pos_common1):]] for pos in find_pos_with_pos(pos_common1, term1._vars_query.positions)]

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


    