from typing import Union
from collections import namedtuple

from pynars.Narsese._py.Connector import Connector
from pynars.NAL.Inference import *
from pynars.Narsese import Statement, Term, Compound
from pynars.Narsese._py.Copula import Copula

Feature = namedtuple(
    'Feature', 
    [
        # feature names
    ],
    defaults=[None, None, None, None]
)

def _mirorr_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]):
    feature = extract_feature(premise2, premise1)
    return Feature(
        # features
    )


def extract_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]) -> Feature:
    ''''''