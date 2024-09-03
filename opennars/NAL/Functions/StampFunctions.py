from typing import Union
from opennars.Config import Config
from opennars.Narsese import Stamp
from copy import deepcopy
from opennars.Narsese import Connector, Copula


_temporal_interval = {
    Connector.SequentialEvents: Config.temporal_duration,
    Copula.PredictiveImplication: Config.temporal_duration,
    Copula.PredictiveEquivalence: Config.temporal_duration,
    Copula.RetrospectiveImplication: -Config.temporal_duration,
}

def Stamp_merge(stamp1: Stamp, stamp2: Stamp, order_mark: Union[Copula, Connector]=None, reverse_order=False, t_bias=0):
    stamp: Stamp = deepcopy(stamp1)
    # stamp.is_external = stamp1.is_external
    if stamp is not None:
        stamp.extend_evidenital_base(stamp2.evidential_base)
        if not stamp1.is_eternal and not stamp2.is_eternal:
            stamp.t_occurrence = max(stamp1.t_occurrence, stamp2.t_occurrence)
        if not stamp1.is_eternal:
            # occurrence time interval
            interval = _temporal_interval.get(order_mark, 0)
            if reverse_order: interval = -interval
            stamp.t_occurrence += interval + t_bias
    return stamp