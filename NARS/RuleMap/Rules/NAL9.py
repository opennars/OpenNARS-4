from collections import OrderedDict
from NARS.DataStructures import LinkType, TaskLink, TermLink
from utils.SparseLUT import SparseLUT
import Global
from .add_rule import *
from NARS.MentalOperation import *

def add_rules__NAL9(sparse_lut: SparseLUT=None, structure: OrderedDict=None):
    ''''''
    register(Believe,    execute__believe)
    register(Doubt,      execute__doubt)
    register(Evaluate,   execute__evaluate)
    register(Hesitate,   execute__hesitate)
    register(Want,       execute__want)
    register(Wonder,     execute__wonder)
    # register(Anticipate, execute__anticipate)
