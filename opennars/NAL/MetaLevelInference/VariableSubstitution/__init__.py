'''
**Variable substitution.** All occurrences of an independent variable term in a statement can be substituted by another term (constant or variable); all occurrences of a term (constant or variable) in a statement can be substituted by a dependent variable term. The reverse cases of these substitution are limited to the cases discussed in NAL-6. A query variable in a question can be substituted by a constant term in a judgment.
'''

from .Substitution import Substitution
from .Elimination import Elimination
from .Introduction import Introduction
from .Unification import *