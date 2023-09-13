from kanren import run, eq, var
from cons import cons, car, cdr

from pynars import Narsese
from pynars.Narsese import Term, Copula, Connector, Statement, Compound


#################################################
### Conversion between Narsese and miniKanren ###
#################################################

prefix = '_rule_'

def logic(term: Term, rule=False):
    if term.is_atom:
        name = prefix+term.word if rule else term.word
        return var(name)
    if term.is_statement:
        return cons(term.copula, *[logic(t, rule) for t in term.terms])
    if term.is_compound:
        return cons(term.connector, *[logic(t, rule) for t in term.terms])

def term(logic):
    if type(logic) is var:
        word = logic.token.replace(prefix, '')
        return Term(word)
    if type(logic) is cons:
        if type(car(logic)) is Copula:
            sub = car(cdr(logic))
            cop = car(logic)
            pre = cdr(cdr(logic))
            return Statement(term(sub), cop, term(pre))
        if type(car(logic)) is Connector:
            con = car(logic)
            terms = to_list(cdr(logic))
            return Compound(con, *terms)
    return logic # atom or cons

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

#################################################


# rule = '''{<(&&, C, S) ==> P>. S} |- <C ==> P>'''
rule = '''{<(&&, C, S) ==> P>. M} |- <((&&, C, S) - M) ==> P>'''

rules = [rule, '{<M-->P>. <S-->M>} |- <S-->P>']


def convert(rule):
    # convert to logical form
    premises, conclusion = rule.split(" |- ")

    p1, p2 = premises.strip("{}").split(". ")

    # TODO: can we parse statements instead?
    p1 = Narsese.parser.parse(p1+'.').term
    p2 = Narsese.parser.parse(p2+'.').term
    c = Narsese.parser.parse(conclusion+'.').term

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

    # apply rule
    result = run(1, c, eq(p1, logic(t1)), eq(p2, logic(t2)))
    # print(result)

    if result:
        conclusion = term(result[0])
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

t1 = Narsese.parser.parse('<(&&, A, B, C, D) ==> Z>.').term

t2 = Narsese.parser.parse('B.').term # positive example
for rule in rules:
    apply(rule, t1, t2)

t2 = Narsese.parser.parse('U.').term # negative example
for rule in rules:
    apply(rule, t1, t2)

t2 = Narsese.parser.parse('(&&, B, C).').term # complex example
for rule in rules:
    apply(rule, t1, t2)

# DEDUCTION

t1 = Narsese.parser.parse('<bird --> animal>.').term
t2 = Narsese.parser.parse('<robin --> bird>.').term
for rule in rules:
    apply(rule, t1, t2)
