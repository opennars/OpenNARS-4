from kanren import run, eq, var
from cons import cons, car, cdr

from pynars import Narsese
from pynars.Narsese import Term, Copula, Connector, Statement, Compound, Variable, VarPrefix


#################################################
### Conversion between Narsese and miniKanren ###
#################################################

prefix = '_rule_'

def logic(term: Term, rule=False):
    if term.is_atom:
        name = prefix+term.word if rule else term.word
        if type(term) is Variable:
            vname = term.word + term.name
            name = prefix+vname if rule else vname 
            return var(name)
        return var(name) if rule else term
    if term.is_statement:
        return cons(term.copula, *[logic(t, rule) for t in term.terms])
    if term.is_compound:
        return cons(term.connector, *[logic(t, rule) for t in term.terms])

def term(logic):
    if type(logic) is Term:
        return logic
    if type(logic) is var:
        name = logic.token.replace(prefix, '')
        if name[0] == '$':
            return Variable(VarPrefix.Independent, name[1:])
        if name[0] == '#':
            return Variable(VarPrefix.Dependent, name[1:])
        if name[0] == '?':
            return Variable(VarPrefix.Query, name[1:])
        else:
            return Term(name)
    if type(logic) is cons:
        if type(car(logic)) is Copula:
            sub = car(cdr(logic))
            cop = car(logic)
            pre = cdr(cdr(logic))
            return Statement(term(sub), cop, term(pre))
        if type(car(logic)) is Connector:
            con = car(logic)
            t = cdr(logic)
            terms = to_list(cdr(logic)) if type(t) is cons else [term(t)]
            return Compound(con, *terms)
    return logic # cons

def to_list(pair) -> list:
    l = [term(car(pair))]
    if type(cdr(pair)) is list and cdr(pair) == []:
        () # empty TODO: there's gotta be a better way to check
    elif type(cdr(pair)) is cons:
        t = term(cdr(pair))
        if type(t) is cons:
            l.extend(to_list(t)) # recurse
        else:
            l.append(t)
    else:
        l.append(term(cdr(pair))) # atom
    return l

#################################################

    # WARNING: terrible code below :)

### quick and dirty example of applying diff ####

def diff(c):
    difference = -1 # result of applying diff

    if type(c) is Statement:
        if c.subject.is_compound and c.copula is Copula.Implication:
            if c.subject.connector is Connector.ExtensionalDifference:
                if len(c.subject.terms.terms) == 2:
                    components = c.subject.terms.terms
                    l = components[0]
                    r = components[1]
                    if l.contains(r) and not l.equal(r):
                        difference = l - r
                    else:
                        difference = None

    if difference == None or difference == -1:
        return difference
    else:
        return Statement(difference, c.copula, c.predicate)

# UNIFICATION

from unification import unify, reify

def variable_elimination(t1: Term, t2: Term) -> list:
    unified = filter(None, (unify(logic(t), logic(t2, True)) for t in t1.terms))
    substitution = []
    for u in unified:
        d = {k: v for k, v in u.items() if type(term(k)) is Variable}
        if len(d):
            substitution.append(d)
    result = []
    for s in substitution:
        reified = reify(logic(t1), s)
        result.append(term(reified))

    return result

#################################################


# rule = '''{<(&&, C, S) ==> P>. S} |- <C ==> P>'''
rule = '''{<(&&, C, S) ==> P>. M} |- <((&&, C, S) - M) ==> P>'''

rules = [rule, '{<M-->P>. <S-->M>} |- <S-->P>']


def parse(narsese: str) -> Term:
    return Narsese.parser.parse(narsese).term

def convert(rule):
    # convert to logical form
    premises, conclusion = rule.split(" |- ")

    p1, p2 = premises.strip("{}").split(". ")

    # TODO: can we parse statements instead?
    p1 = parse(p1+'.')
    p2 = parse(p2+'.')
    c = parse(conclusion+'.')

    p1 = logic(p1, True)
    p2 = logic(p2, True)
    c = logic(c, True)
    return (p1, p2, c)

def apply(rule, *args):
    print("\nRULE:", rule)
    p1, p2, c = convert(rule)

    # test statements
    t1, t2 = args
    print("Test:", t1, t2)

    # TODO: what about other possibilities?
    t1e = variable_elimination(t1, t2)
    t2e = variable_elimination(t2, t1)

    t1 = t1e[0] if len(t1e) else t1
    t2 = t2e[0] if len(t2e) else t2

    if len(t1e) or len(t2e):
        print("Substituted:", t1, t2)

    # apply rule
    result = run(1, c, eq((p1, p2), (logic(t1), logic(t2))))
    # print(result)

    if result:
        conclusion = term(result[0])
        # print(conclusion)
        # apply diff connector
        difference = diff(conclusion)
        if difference == None:
            print("Rule application failed.")
        elif difference == -1:
            print(conclusion) # no diff application
        else:
            print(difference) # diff applied successfully
    else:
        print("Rule application failed.")

    print("-------------------")

# CONDITIONAL

t1 = parse('<(&&, A, B, C, D) ==> Z>.')

t2 = parse('B.') # positive example
for rule in rules:
    apply(rule, t1, t2)

t2 = parse('U.') # negative example
for rule in rules:
    apply(rule, t1, t2)

t2 = parse('(&&, B, C).') # complex example
for rule in rules:
    apply(rule, t1, t2)

# DEDUCTION

t1 = parse('<bird --> animal>.')
t2 = parse('<robin --> bird>.')
for rule in rules:
    apply(rule, t1, t2)

print("\n\n----VARIABLE SUBSTITUTION")

# CONDITIONAL SYLLOGISTIC

rules = [
    '{<S ==> P>. S} |- P', # deduction
    '{<P ==> S>. S} |- P', #abduction
    '{<(&&, C, S) ==> P>. M} |- <((&&, C, S) - M) ==> P>', # conditional ded
    ]

print('\n--nal6.7')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<robin --> bird>.')

for rule in rules:
    apply(rule, t1, t2)

print('\n--nal6.8')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<tiger --> animal>.')

for rule in rules:
    apply(rule, t1, t2)

print('\n--nal6.12')
t1 = parse('<(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>.')
t2 = parse('<{Tweety} --> flyer>.')

for rule in rules:
    apply(rule, t1, t2)
