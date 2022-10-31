from typing import Union
from collections import namedtuple

from pynars.Narsese._py.Connector import Connector
from pynars.NAL.Inference import *
from pynars.Narsese import Statement, Term, Compound
from pynars.Narsese._py.Copula import Copula

Feature = namedtuple(
    'Feature', 
    [
        'is_temporal_copula1',
        'is_temporal_copula2',
        'is_temporal_connector1',
        'is_temporal_connector2'
    ],
    defaults=[None, None, None, None]
)

def _mirorr_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]):
    feature = extract_feature(premise2, premise1)
    return Feature(
        feature.is_temporal_copula2,
        feature.is_temporal_copula1,
        feature.is_temporal_connector2,
        feature.is_temporal_connector1
    )


def extract_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]) -> Feature:
    '''
    It should be ensured that premise1 and premise2 aren't identical.    
    '''
    is_temporal_copula1 = premise1.is_statement and premise1.copula.is_temporal
    is_temporal_copula2 = premise2.is_statement and premise2.copula.is_temporal
    is_temporal_connector1 = premise1.is_compound and premise1.connector.is_temporal
    is_temporal_connector2 = premise2.is_compound and premise2.connector.is_temporal
    return Feature(
        is_temporal_copula1=is_temporal_copula1,
        is_temporal_copula2=is_temporal_copula2,
        is_temporal_connector1=is_temporal_connector1,
        is_temporal_connector2=is_temporal_connector2,

    )

