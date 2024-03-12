from .KanrenEngine import KanrenEngine
from .util import *

engine = KanrenEngine()
print('--')

x = parse('<A-->B>. %0.90;0.90%')
y = parse('<B-->A>. %0.90;0.90%')
rule = convert("{<S --> P>. <P --> S>} |- <S <-> P> .int")
conclusion = engine.apply(rule, logic(x.term), logic(y.term))[0]
print(truth_functions['int'](x.truth, y.truth))
print('')

exit()

engine = KanrenEngine()
print('--')

# t0 = time()
x = parse('<(-, (&&, <$1-->[chirping]>, <$1-->[with_wings]>), <(&&, <$1-->flyer>, <$1-->[chirping]>, <(*, $1, worms)-->food>)==><$1-->bird>>)==><$1-->bird>>.')
# x = parse('<(-, (&&, <x-->[chirping]>, <x-->[with_wings]>), <(&&, <x-->flyer>, <x-->[chirping]>, <(*, x, worms)-->food>)==><x-->bird>>)==><x-->bird>>.')
# print(time()-t0)
# t0 = time()

logic = logic(x.term)
# print(time()-t0)
t0 = time()

term = term(logic)
print(time()-t0)
t0 = time()


exit()

# rule = convert('{<M --> P>. <S --> M>} |- <S --> P> .ded')
rule = convert('{<(&&, C, S) ==> P>. _S} |- <((&&, C, S) - _S) ==> P> .ded')

x = parse('<(&&, <$1-->[chirping]>, <$1-->[with_wings]>)==><$1-->bird>>.')
y = parse('<(&&, <$1-->flyer>, <$1-->[chirping]>, <(*, $1, worms)-->food>)==><$1-->bird>>.')
c = parse('bird.').term
t0 = time()
# z = engine.inference(x,y,c)

l1 = logic(x.term)
l2 = logic(y.term)

res = engine.apply(rule, l1, l2)

t1 = time() - t0
print(res, t1)
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