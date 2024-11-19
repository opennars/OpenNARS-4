from opennars.Narsese import Term, Variable, VarPrefix, Compound, Statement
from copy import deepcopy


def unify(type: VarPrefix, t1: Term, t2: Term, compound1: Term=None, compound2: Term=None) -> bool:
    '''
    To unify two terms
    Args:
        type: The type of variable that can be substituted
        t1: The first term to be unified
        t2: The second term to be unified
        compound1: The compound contermaining the first term
        compound2: The compound contermaining the second term
    Returns:
        Whether the unification is possible
    */
    '''
    compound1 = compound1 if compound1 is not None else t1
    compound2 = compound2 if compound2 is not None else t2

    map1 = dict[Term, Term]()
    map2 = dict[Term, Term]()
    hasSubs: bool = findSubstitute(type, t1, t2, map1, map2); # find substitution
    if hasSubs:
        if len(map1)>0:
            applySubstitute(compound1, map1)
        if len(map2)>0:
            applySubstitute(compound2, map2)
    return hasSubs

def findSubstitute(type: VarPrefix, term1: Term|Variable, term2: Term|Variable, map1: dict[Term, Term], map2: dict[Term, Term]) -> bool:
    '''
    To recursively find a substitution that can unify two Terms without changing them
    Args:
        type: The type of Variable to be substituted
        term1: The first Term to be unified
        term2: The second Term to be unified
        subs: The substitution formed so far
    Returns:
        The substitution that unifies the two Terms
#     */
    '''
    t: Term
    if (term1.is_atom and term1.is_var) and (term1.prefix == type):
        t = map1.get(term1, None)
        if t is not None:
            return t == term2
        else:
            map1[term1] = term2
            return True
    if (term2.is_atom and term2.is_var) and (term2.prefix == type):
        t = map2.get(term2, None)
        if t is None:
            return t == term1
        else:
            map2[term2] = term1
            return True
        
    if term1.is_compound and term1.connector == term2.connector:
        cTerm1: Compound = term1
        cTerm2: Compound = term2
        if (cTerm1.count_components() != cTerm2.count_components()):
            return False

        for i in range(cTerm1.count_components()):
            t1: Term = cTerm1[i]
            t2: Term = cTerm2[i]
            haveSub: bool = findSubstitute(type, t1, t2, map1, map2);
            if not haveSub:
                return False
            
        return True
    if not (term1.is_atom and term1.is_var) and not (term2.is_atom and term2.is_var) and term1 == term2: # for constant, also shortcut for variable and compound
        return True
    return False

def hasSubstitute(type: VarPrefix, term1: Term, term2: Term) -> bool:
    '''
    Check if two terms can be unified
    Args:
        type: The type of variable that can be substituted
        term1: The first term to be unified
        term2: The second term to be unified
    Returns:
        Whether there is a substitution
    '''
    return findSubstitute(type, term1, term2, dict[Term, Term](), dict[Term, Term]());


def applySubstitute(compound: Compound|Statement, subs: dict[Term, Term]):
    '''
    Recursively apply a substitute to the current CompoundTerm
    Args:
        compound
        subs
    '''
    t1: Term
    t2: Term
    components = list(compound.terms)
    for i in range(len(components)):
        t1 = compound[i]
        if t1 in subs:
            t2 = subs[t1]
            while t2 in subs:
                t2 = subs[t2]

            components[i] = deepcopy(t2)
        elif t1.is_compound:
            applySubstitute(t1, subs)
    
    compound.reset(compound.connector, *components)

def contain_var_indep(n: str) -> bool:
    '''
    Check whether a string represent a name of a term that contains an independent variable

    Args:
        n: The string name to be checked
    Returns:
        Whether the name contains an independent variable
    '''
    return n.find(VarPrefix.Independent.value) >= 0



def contain_var_dep(n: str) -> bool:
    '''
    Check whether a string represent a name of a term that contains a dependent variable

    Args:
        n: The string name to be checked
    Returns:
        Whether the name contains a dependent variable
    '''
    return n.find(VarPrefix.Dependent.value) >= 0

def contain_var_query(n: str):
    '''
    Check whether a string represent a name of a term that contains a query variable

    Args:
        n: The string name to be checked
    Returns:
        Whether the name contains a query variable
    '''
    return n.find(VarPrefix.Query.value) >= 0


def contain_var(n: str):
    '''
    Check whether a string represent a name of a term that contains a variable

    Args:
        n: The string name to be checked
    Returns:
        Whether the name contains a variable
    '''
    return contain_var_indep(n) or contain_var_dep(n) or contain_var_query(n)