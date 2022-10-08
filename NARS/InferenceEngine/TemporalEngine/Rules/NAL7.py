from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL7(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    ''''''
    add_rule(sparse_lut, structure,
        [
            Interface_TemporalRules._temporal__induction_composition,
            Interface_TemporalRules._temporal__induction_implication,
            Interface_TemporalRules._temporal__induction_implication_prime,
            Interface_TemporalRules._temporal__induction_equivalence,
        ],
        is_temporal_copula1 = False,
        is_temporal_copula2 = False
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__induction_composition,
        is_temporal_copula1 = False,
        is_temporal_copula2 = True
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__induction_composition,
        is_temporal_copula1 = True,
        is_temporal_copula2 = False
    )

    ''''''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__induction_implication,
        is_temporal_copula1 = False,
        is_temporal_copula2 = False
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__induction_implication_prime,
        is_temporal_copula1 = False,
        is_temporal_copula2 = False
    )

    ''''''
    add_rule(sparse_lut, structure,
        [
            Interface_TemporalRules._temporal__induction_predictieve_implication_composition,
            Interface_TemporalRules._temporal__induction_predictive_implication_composition_inverse,
            Interface_TemporalRules._temporal__induction_predictive_equivalance_composition
        ],
        is_temporal_copula1 = False,
        is_temporal_copula2 = True,
        copula2 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ]
    )
    add_rule(sparse_lut, structure,
        [
            Interface_TemporalRules._temporal__induction_predictive_implication_composition_prime,
            Interface_TemporalRules._temporal__induction_predictive_implication_composition_inverse_prime,
            Interface_TemporalRules._temporal__induction_predictive_equivalance_composition_prime
        ],
        is_temporal_copula1 = True,
        is_temporal_copula2 = False,
        copula1 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ]
    )

    ''''''
    add_rule(sparse_lut, structure,
        [
            Interface_TemporalRules._temporal__induction_retrospective_implication_composition,
            Interface_TemporalRules._temporal__induction_retrospective_implication_composition_inverse,
            Interface_TemporalRules._temporal__induction_retrospective_equivalance_composition

        ],
        is_temporal_copula1 = False,
        is_temporal_copula2 = True,
        copula2 = Copula.RetrospectiveImplication
    )
    add_rule(sparse_lut, structure,
        [
            Interface_TemporalRules._temporal__induction_retrospective_implication_composition_prime,
            Interface_TemporalRules._temporal__induction_retrospective_implication_composition_inverse_prime,
            Interface_TemporalRules._temporal__induction_retrospective_equivalance_composition_prime
        ],
        is_temporal_copula1 = True,
        is_temporal_copula2 = False,
        copula1 = Copula.RetrospectiveImplication
    )

    # add_rule(sparse_lut, structure,
    #     Interface_TemporalRules._temporal__induction_predictive_implication_composition_inverse,
    #     is_temporal_copula1 = False,
    #     is_temporal_copula2 = True,
    #     coupla2 = [Copula.RetrospectiveImplication]
    # )
    # add_rule(sparse_lut, structure,
    #     Interface_TemporalRules._temporal__induction_predictive_implication_composition_inverse_prime,
    #     is_temporal_copula1 = True,
    #     is_temporal_copula2 = False,
    #     coupla1 = [Copula.RetrospectiveImplication]
    # )


    # add_rule(sparse_lut, structure,
    #     Interface_TemporalRules._temporal__induction_implication_composition,
    #     connector1 = [None, Connector.SequentialEvents, Connector.ParallelEvents],
    #     copula2 = Copula.PredictiveImplication
    # )

    # add_rule(sparse_lut, structure,
    #     [
    #         Interface_TemporalRules._temporal__induction_implication,
    #         Interface_TemporalRules._temporal__induction_implication_prime
    #     ], 
    #     is_temporal_copula1 = False,
    #     is_temporal_copula2 = False
    # )
    # add_rule(sparse_lut, structure,
    #     [
    #         Interface_TemporalRules._temporal__induction_implication,
    #         Interface_TemporalRules._temporal__induction_implication_prime,
    #         Interface_TemporalRules._temporal__induction_composition,
    #     ], 
    #     is_temporal_copula1 = False,
    #     is_temporal_copula2 = False,
    #     is_temporal_connector1 = False,
    #     is_temporal_connector2 = False
    # )