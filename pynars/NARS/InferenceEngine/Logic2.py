from kanren import run, eq, var, membero

# rule = '''{<( && C S ) ==> P>, <S>} |- <C ==> P>'''
rule = '''{<( && C S ) ==> P>, <M>} |- <( - ( && C S ) M ) ==> P>'''

premises, conclusion = rule.split(" |- ")

p1, p2 = premises.strip("{}").split(", ")

p1 = p1.strip("<>").split()
p2 = p2.strip("<>").split()
c = conclusion.strip("<>").split()

# print(p1, p2, c)

def replace_terms(t: str):
    if t.isalpha():
        return var(t)
    else:
        return t

p1 = list(map(replace_terms, p1))
p2 = list(map(replace_terms, p2))
c = list(map(replace_terms, c))

# print(p1, p2, c)

t1, t2 = "( && A B ) ==> Z", "B"
t1, t2 = t1.split(), t2.split()

# print(t1, t2)

# apply rule

result = run(1, c, eq(p1, t1), eq(p2, t2), membero(t2[0], t1[:-2]))
# print(result)

if result:
    print("Positive example:")
    print(' '.join(result[0]))

# multi-component set
from cons import cons, car, cdr

t1, t2 = "( && A B C ) ==> Z", "( && B C )"
t1, t2 = t1.split(), t2.split()

p1 = cons("==>", cons(*p1[1:-3]), p1[-1])
t1 = cons("==>", cons(*t1[1:-3]), t1[-1])
p2 = cons("&&", *p2)
t2 = cons(*t2[1:-1])

print(p1)
print(t1)
print(p2)
print(t2)

print(t1, t2)

# apply rule

result = run(1, c, eq(p1, t1), eq(p2, t2))#, membero(t2, car(cdr(t1))))
print(result)

if result:
    print("Positive example:")
    print(' '.join(result[0]))

