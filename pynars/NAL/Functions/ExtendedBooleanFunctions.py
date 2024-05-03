from functools import reduce
from statistics import mean
from operator import mul

Not = lambda x: (1-x)

And = lambda *x: reduce(mul, x, 1)
Or  = lambda *x: 1 - reduce(mul, (1 - xi for xi in x), 1)
Average = lambda *x: mean(x)

def Scalar(x): 
    x = 0.5 + 4*(x-0.5)**3 
    x = 0.001 if x < 0.001 else 0.999 if x > 0.999 else x
    return x