from kanren import run, eq, var

rule = '''{<M --> P>, <S --> M>} |- <S --> P>'''

premises, conclusion = rule.split(" |- ")

p1, p2 = premises.strip("{}").split(", ")

p1 = p1.strip("<>").split()
p2 = p2.strip("<>").split()
c = conclusion.strip("<>").split()

# print(p1, p2, c) # ['M', '-->', 'P'] ['S', '-->', 'M'] ['S', '-->', 'P']

_vars = {} # mappings of terms to vars

def replace_terms(t: str):
    if t.isalpha():
        if not t in _vars:
            _vars[t] = var()
        return _vars[t]
    else:
        return t

p1 = list(map(replace_terms, p1))
p2 = list(map(replace_terms, p2))
c = list(map(replace_terms, c))

# print(p1, p2, c) # [~_1, '-->', ~_2] [~_3, '-->', ~_1] [~_3, '-->', ~_2]

t1, t2 = "bird --> animal", "robin --> bird"
t1, t2 = t1.split(), t2.split() # ["bird", "-->", "animal"], ["robin", "-->", "bird"]

# apply rule

result = run(1, c, eq(p1, t1), eq(p2, t2))
# print(res)

if result:
    print("Positive example:")
    print(' '.join(result[0])) # robin --> animal


t3, t4 = ["bird", "-->", "animal"], ["bird", "-->", "[flying]"]

result = run(1, c, eq(p1, t3), eq(p2, t4))

if not result:
    print("\nNegative example:")
    print("Failed to match rule pattern to premises")

