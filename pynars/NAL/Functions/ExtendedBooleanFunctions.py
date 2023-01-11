import numpy as np

Not = lambda x: (1-x)

And = lambda *x: np.prod(x)
Or  = lambda *x: 1 - np.prod(1-np.array(x))
Average = lambda *x: np.mean(x)

def Scalar(x): 
    x = 0.5 + 4*(x-0.5)**3 
    x = 0.001 if x < 0.001 else 0.999 if x > 0.999 else x
    return x