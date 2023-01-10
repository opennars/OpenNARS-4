from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *
from pynars.NARS.Operation import *

def add_rules__NAL9(sparse_lut: SparseLUT=None, structure: OrderedDict=None):
    ''''''
    register(Believe,    execute__believe)
    register(Doubt,      execute__doubt)
    register(Evaluate,   execute__evaluate)
    register(Hesitate,   execute__hesitate)
    register(Want,       execute__want)
    register(Wonder,     execute__wonder)
    # register(Anticipate, execute__anticipate)
