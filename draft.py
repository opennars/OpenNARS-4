import numpy as np
from pynars.Narsese import parser

A = np.array(("<A --> B>.", parser.parse("<A --> B>."), 0.8))
B = np.array(("<C --> D>.", parser.parse("<C --> D>."), 0.5))

C = np.array([A, B])
print(1)