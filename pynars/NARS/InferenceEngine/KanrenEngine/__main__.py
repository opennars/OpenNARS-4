from .KanrenEngine import KanrenEngine
from .util import *

engine = KanrenEngine()

rule = convert('{<(&&, S, C) ==> P>. <_C ==> P>} |- ((&&, S, C) - _C) .abd')

t1 = parse('<(&&,<#1 --> lock>,<#1 --> (/,open,$2,_)>) ==> <$2 --> key>>.')
t2 = parse('<<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>.')


t1e, t2e = variable_elimination(t1.term, t2.term, None)

# TODO: what about other possibilities?
t1t = t1e[0] if len(t1e) else t1.term
t2t = t2e[0] if len(t2e) else t2.term

l1 = logic(t1t)
l2 = logic(t2t)

res = engine.apply(rule, l1, l2)

print(res)
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