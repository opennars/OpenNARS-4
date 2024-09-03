from collections import OrderedDict
from opennars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from opennars import Global
from ....RuleMap.add_rule import *
from opennars.NARS.Operation import *

def add_rules__NAL9(sparse_lut: SparseLUT=None, structure: OrderedDict=None):
    ''''''
    register(Believe,    execute__believe)
    register(Doubt,      execute__doubt)
    register(Evaluate,   execute__evaluate)
    register(Hesitate,   execute__hesitate)
    register(Want,       execute__want)
    register(Wonder,     execute__wonder)
    # register(Anticipate, execute__anticipate)
