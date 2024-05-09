from kanren import run, eq, var, lall, lany
from kanren.constraints import neq, ConstrainedVar
from unification import unify, reify
from cons import cons, car, cdr

from itertools import combinations, product, chain, permutations

from pynars import Narsese, Global
from pynars.Narsese import Term, Copula, Connector, Statement, Compound, Variable, VarPrefix, Sentence, Punctuation, Stamp, place_holder, Tense

from pynars.NAL.Functions import *
from pynars.NARS.DataStructures import Concept, Task, TaskLink, TermLink, Judgement, Question
from pynars.NAL.Functions.Tools import project_truth, revisible
from collections import defaultdict
from typing import List

from functools import cache

from time import time
import yaml
from pathlib import Path


truth_functions = {
    'ded': Truth_deduction,
    'ana': Truth_analogy,
    'res': Truth_resemblance,
    'abd': Truth_abduction,
    'ind': Truth_induction,
    'exe': Truth_exemplification,
    'com': Truth_comparison,
    'int': Truth_intersection,
    'uni': Truth_union,
    'dif': Truth_difference,

    'neg': Truth_negation,
    'cnv': Truth_conversion,
    'cnt': Truth_contraposition
}


def split_rules(rules: str) -> List[str]:
    lines = []
    for line in rules.splitlines():
        if len(line) and not (line.startswith("'") or line.startswith("#")):
            lines.append(line)
    return lines

def parse(narsese: str, rule=False):
    task = Narsese.parser.parse(narsese)
    return task.term if rule else task.sentence


#################################################
### Conversion between Narsese and miniKanren ###
#################################################

# used in converting from logic to Narsese
vars_all = defaultdict(lambda: len(vars_all))
vars = set() # used as scratchpad

rules_strong = [] # populated by `convert` below for use in structural inference

def convert(rule, conditional_compositional=False):
    # convert to logical form
    premises, conclusion = rule.split(" |- ")

    p1, p2 = premises.strip("{}").split(". ")
    conclusion = conclusion.split(" .")
    c = conclusion[0]
    r = conclusion[1]

    # TODO: can we parse statements instead?
    p1 = parse(p1+'.', True)
    p2 = parse(p2+'.', True)
    c = parse(c+'.', True)

    vars.clear() # clear scratchpad

    p1 = logic(p1, True)
    p2 = logic(p2, True)
    c = logic(c, True)

    var_combinations = list(combinations(vars, 2))
    # filter out combinations like (_C, C) allowing them to be the same
    cond = lambda x, y: x.token.replace('_', '') != y.token.replace('_', '')
    constraints = [neq(c[0], c[1]) for c in var_combinations if cond(c[0], c[1])]

    if not conditional_compositional: # conditional compositional rules require special treatment
        if r.replace("'", '') in ['ded', 'ana', 'res', 'int', 'uni', 'dif']:
            rules_strong.append(((p1, p2, c), (r, constraints)))

    return ((p1, p2, c), (r, constraints))

def convert_immediate(rule):
    # convert to logical form
    premise, conclusion = rule.split(" |- ")
    conclusion = conclusion.split(" .")
    c = conclusion[0]
    r = conclusion[1]

    # TODO: can we parse statements instead?
    p = parse(premise+'.', True)
    c = parse(c+'.', True)

    vars.clear() # clear scratchpad

    p = logic(p, True)
    c = logic(c, True)
    
    var_combinations = list(combinations(vars, 2))
    # filter out combinations like (_C, C) allowing them to be the same
    cond = lambda x, y: x.token.replace('_', '') != y.token.replace('_', '')
    constraints = [neq(c[0], c[1]) for c in var_combinations if cond(c[0], c[1])]

    return ((p, c), (r, constraints))

def convert_theorems(theorem):
    # TODO: can we parse statements instead?
    t = parse(theorem+'.', True)
    l = logic(t, True, True, prefix='_theorem_')

    matching_rules = []
    for i, rule in enumerate(rules_strong):
        (p1, p2, c) = rule[0]
        res = run(1, (p2, c), eq(p1, l))
        if res:
            matching_rules.append(i)

    sub_terms = frozenset(filter(lambda x: x != place_holder, t.sub_terms))
    return (l, sub_terms, tuple(matching_rules))


#################
# TERM TO LOGIC #
#################
def logic(term: Term, rule=False, substitution=False, var_intro=False, structural=False, prefix='_rule_'):
    if term.is_atom:
        name = prefix+term.word if rule else term.word
        if type(term) is Variable:
            vname = term.word + term.name
            name = prefix+vname if rule else vname 
            if rule and not substitution: # collect rule variable names
                vars.add(var(name))
            return var(name) if not structural else term
        if rule and not substitution: # collect rule variable names
            vars.add(var(name))
        return var(name) if rule else term
    if term.is_statement:
        copula = term.copula if rule else term.copula.get_atemporal
        return cons(copula, *[logic(t, rule, substitution, var_intro, structural, prefix) for t in term.terms])
    if term.is_compound:
        # when used in variable introduction, treat single component compounds as atoms
        if rule and var_intro and len(term.terms) == 1 \
            and (term.connector is Connector.ExtensionalSet \
            or term.connector is Connector.IntensionalSet):
                name = prefix+term.word
                return var(name)
        
        # extensional and intensional images are not composable
        if term.connector is Connector.ExtensionalImage \
            or term.connector is Connector.IntensionalImage:
            return cons(term.connector, *[logic(t, rule, substitution, var_intro, structural, prefix) for t in term.terms])

        connector = term.connector if rule else term.connector.get_atemporal
        terms = list(term.terms)
        multi = []
        while len(terms) > 2:
            t = terms.pop(0)
            multi.append(logic(t, rule, substitution, var_intro, structural, prefix))
            multi.append(connector)
        multi.extend(logic(t, rule, substitution, var_intro, structural, prefix) for t in terms)
        
        return cons(connector, *multi)

#################
# LOGIC TO TERM #
#################
@cache
def term(logic, root=True):
    # additional variable handling
    if root: vars_all.clear()
    def create_var(name, prefix: VarPrefix):
        vars_all[name]
        var = Variable(prefix, name)
        idx = vars_all[name]
        if prefix is VarPrefix.Independent:
            var._vars_independent.add(idx, [])
        if prefix is VarPrefix.Dependent:
            var._vars_dependent.add(idx, [])
        if prefix is VarPrefix.Query:
            var._vars_query.add(idx, [])
        return var

    if type(logic) is Term:
        return logic
    if type(logic) is Variable:
        return logic
    if type(logic) is var or type(logic) is ConstrainedVar:
        name = logic.token.replace('_rule_', '').replace('_theorem_', '')
        if name[0] == '$':
            return create_var(name[1:], VarPrefix.Independent)
        if name[0] == '#':
            return create_var(name[1:], VarPrefix.Dependent)
        if name[0] == '?':
            return create_var(name[1:], VarPrefix.Query)
        else:
            return Term(name)
    if type(logic) is cons or type(logic) is tuple:
        if type(car(logic)) is Copula:
            sub = car(cdr(logic))
            cop = car(logic)
            pre = cdr(cdr(logic))
            if type(term(sub, False)) is cons or type(term(pre, False)) is cons:
                return logic
            return Statement(term(sub, False), cop, term(pre, False))
        if type(car(logic)) is Connector:
            con = car(logic)
            t = cdr(logic)
            is_list = type(t) is (cons or tuple) \
                and not (type(car(t)) is Copula or type(car(t)) is Connector)
            terms = to_list(cdr(logic), con) if is_list else [term(t, False)]
            return Compound(con, *terms)
        # else:
        #     return term(car(logic))
    return logic # cons

def to_list(pair, con) -> list:
    l = [term(car(pair), False)]
    if type(cdr(pair)) is list and cdr(pair) == [] \
        or type(cdr(pair)) is tuple and cdr(pair) == ():
        () # empty TODO: there's gotta be a better way to check
    elif type(cdr(pair)) is cons or type(cdr(pair)) is tuple:
        # if len(cdr(pair)) == 1:
        #     l.append(term(car(cdr(pair))))
        #     return l
        t = term(cdr(pair), False)
        if type(t) is cons or type(t) is tuple:
            l.extend(to_list(t, con)) # recurse
        # elif type(t) is Compound and t.connector == con:
        #     l.extend(t.terms)
        else:
            l.append(t)
    else:
        l.append(term(cdr(pair), False)) # atom
    return l

###############
# UNIFICATION #
###############

def variable_elimination(t1: Term, t2: Term) -> list:
    terms = [
        t1, t2, \
        *t1.terms, *t2.terms, \
        *chain(*map(lambda t: t.terms if len(t.terms) > 1 else [], t1.terms)), \
        *chain(*map(lambda t: t.terms if len(t.terms) > 1 else [], t2.terms))
    ]

    unified = []
    for pair in permutations(set(terms), 2):
        unified.append(unify(logic(pair[0]), logic(pair[1], True, True)))

    unified = list(filter(None, unified))

    def valid(k, v):
        kname = vname = '.'
        if type(k) is var:
            kname = k.token.replace('_rule_', '')
        if type(k) is Term:
            kname = k.word
        if type(v) is var:
            vname = v.token.replace('_rule_', '')
        if type(v) is Term:
            vname = v.word
        if kname[0] in ['#', '$', '?'] or kname == vname:
            return True
        return False

    substitution = []
    for u in unified:
        if len(u) > 1 and all(valid(k, v) for k, v in u.items()):
            substitution.append(u)
            
    t1s = []
    t2s = []

    for s in substitution:
        t1r = term(reify(logic(t1, True, True), s))
        if not t1r.identical(t1):
            t1s.append(t1r)

        t2r = term(reify(logic(t2, True, True), s))
        if not t2r.identical(t2):
            t2s.append(t2r)
    
    if not t1s: t1s.append(t1)
    if not t2s: t2s.append(t2)
    
    return (t1s, t2s)


#################################################
### quick and dirty example of applying diff ####
#################################################

def diff(c):
    # TODO: room for improvement
    difference = -1 # result of applying diff

    def calculate_difference(l: Term, r: Term):
        l._normalize_variables()
        r._normalize_variables()
        return (l - r) if not l.sub_terms.isdisjoint(r.sub_terms) and not l.equal(r) else None
        
    def do_diff(t: Term):
        nonlocal difference
        if len(t.terms.terms) == 2:
            components = t.terms.terms
            difference = calculate_difference(*components)


    # COMPOUND
    if type(c) is Compound and c.connector is Connector.ExtensionalDifference:
        if len(c.terms.terms) == 2:
            return calculate_difference(*c.terms.terms)

    # STATEMENT
    elif type(c) is Statement and \
        (c.copula is Copula.Implication \
        or c.copula is Copula.Inheritance):
        # check subject
        subject = c.subject
        if subject.is_compound:
            if subject.connector is Connector.ExtensionalDifference:
                do_diff(c.subject)
                if difference is not None and difference != -1:
                    subject = difference

            # check for nested difference
            elif subject.connector is Connector.Conjunction:
                if len(subject.terms.terms) == 2:
                    components = subject.terms.terms
                    if components[0].is_compound:
                        if components[0].connector is Connector.ExtensionalDifference:
                            components[0]._normalize_variables()
                            do_diff(components[0])
                            # if components[0].terms.terms[0] == components[1]:
                            #     difference = None
                            if difference is not None:
                                components[1]._normalize_variables()
                                subject = Compound(subject.connector, difference, components[1])

        # check predicate
        predicate = c.predicate
        if predicate.is_compound:
            if predicate.connector is Connector.ExtensionalDifference:
                do_diff(predicate)
                if difference is not None:
                    predicate = difference

        # check for success
        if difference == None or difference == -1:
            return difference
        else:
            return Statement(subject, c.copula, predicate)

    return -1 # no difference was applied



########################################################################

# UTILITY METHODS

########################################################################

def cache_notify(func):
    func = cache(func)
    def notify_wrapper(*args, **kwargs):
        stats = func.cache_info()
        hits = stats.hits
        results = func(*args, **kwargs)
        stats = func.cache_info()
        cached = False
        if stats.hits > hits:
            cached = True
            # print(f"NOTE: {func.__name__}() results were cached")
        return (results, cached)
    return notify_wrapper