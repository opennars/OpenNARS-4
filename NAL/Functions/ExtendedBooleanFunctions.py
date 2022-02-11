import numpy as np

Not = lambda x: (1-x)
And = lambda *x: np.prod(x)
Or  = lambda *x: 1 - np.prod(1-np.array(x))
Average = lambda *x: np.mean(x)