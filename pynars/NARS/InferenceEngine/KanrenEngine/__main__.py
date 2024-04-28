from .KanrenEngine import KanrenEngine
from .util import *

engine = KanrenEngine()

rule = convert("{<S ==> P>. S} |- P .ded")

t1 = parse('(&/, <(*, SELF, {t002})-->reachable>, <(*, SELF, {t002})-->^pick>).')
t2 = parse('<(&&, S1, S2) ==> S1>.')


t1e, t2e = variable_elimination(t1.term, t2.term, None)

# TODO: what about other possibilities?
t1t = t1.term#t1e[0] if len(t1e) else t1.term
t2t = t2.term#t2e[0] if len(t2e) else t2.term

l1 = logic(t1t, structural=True)
l2 = convert_theorems('<(&&, S1, S2) ==> S1>')[0]

res = engine.apply(rule, l2, l1)

conclusion = res[0]
# common = set(t1.term.sub_terms).intersection(t2.term.sub_terms)

# # variable introduction
# prefix = '$' if conclusion.is_statement else '#'
# substitution = {logic(c, True, var_intro=True): var(prefix=prefix) for c in common}
# reified = reify(logic(conclusion, True, var_intro=True), substitution)

# conclusion = term(reified)

print(conclusion)
exit()

memory = {}


def accept_task(task):
    for term in get_terms(task):
        add_task(task, term)

    for concept in memory.items():
        print(concept, len(concept[1]['tasks']))
    print('---')

def add_task(task, term):
    if term not in memory:
        memory[term] = {'tasks': set(), 'beliefs': set()}
    memory[term]['tasks'].add(task)
    memory[term]['beliefs'].add(task)

def get_term(task):
    return task[:-1]

def get_terms(task):
    return get_term(task).split()


accept_task('A.')
accept_task('B.')
accept_task('C.')
accept_task('A B.')
accept_task('B C.')
accept_task('A C.')



exit()



engine = KanrenEngine()
print('--')

x = parse('<A=\>B>.')
y = parse('<B=\>C>.')
rule = convert("{<P ==> M>. <M ==> S>} |- <P ==> S> .ded'")
z = parse('<A=\>C>.')

conclusion = engine.apply(rule, logic(x.term), logic(y.term))[0]

conclusion = conclusion.retrospective()
# conclusion.copula = conclusion.copula.retrospective
# conclusion = Statement(conclusion.subject, conclusion.copula.retrospective, conclusion.predicate)

print('Output:', conclusion)
print('Target:', z.term)
print('')
print('EQUAL?    ', conclusion.equal(z.term))
# True
print('IDENTICAL?', conclusion.identical(z.term))
# False