from pynars.Narsese._codon.Term import Term as cTerm
from pynars.Narsese._py.Term import Term as Term
import time
if __name__ == '__main__':
    t = Term('bird')
    print(t)
    exit()
    t1 = time.time()
    terms = []
    for i in range(10000):
        t = Term(f"{i}")
        terms.append(t)
    t2 = time.time()
    print('py', t2 - t1)

    t1 = time.time()
    terms = []
    for i in range(10000):
        t = cTerm(f"{i}")
        terms.append(t)
    t2 = time.time()
    print('codon jit', t2 - t1)