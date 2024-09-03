from collections import OrderedDict
from opennars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from opennars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL7(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True
    )

    '''exemplification'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True
    )

    '''induction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    '''comparison'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True
    )

    '''analogy'''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.RetrospectiveImplication,
            Copula.ConcurrentImplication
        ],   # =\>, =|>
        Copula2 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication, # =/>
        Copula2 = Copula.ConcurrentEquivalence, # <|>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ],   # =/>, =|>
        Copula2 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication, # =\>
        Copula2 = Copula.ConcurrentEquivalence, # <|>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ],   # =/>, =|>
        Copula2 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.RetrospectiveImplication,
        ],   # =\>
        Copula2 = Copula.ConcurrentEquivalence,   # <|>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.RetrospectiveImplication,
            Copula.ConcurrentImplication
        ],   # =\>, =|>
        Copula2 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,  # =/>
        Copula2 = Copula.ConcurrentEquivalence,  # <|>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )


    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        Copula2 = [
            Copula.RetrospectiveImplication,
            Copula.ConcurrentImplication
        ],   # =\>, =|>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence, # <|>
        Copula2 = Copula.PredictiveImplication, # =/>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        Copula2 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ],   # =/>, =|>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence, # <|>
        Copula2 = Copula.RetrospectiveImplication, # =\>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        Copula2 = [
            Copula.PredictiveImplication,
            Copula.ConcurrentImplication
        ],   # =/>, =|>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,   # <|>
        Copula2 = Copula.RetrospectiveImplication,   # =\>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveEquivalence,
            Copula.ConcurrentEquivalence
        ],   # </>, <|>
        Copula2 = [
            Copula.RetrospectiveImplication,
            Copula.ConcurrentImplication
        ],   # =\>, =|>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,  # <|>
        Copula2 = Copula.PredictiveImplication,  # =/>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )



    '''reversion?'''

    '''---------------'''

    '''---------NAL 2---------'''
    '''resemblance'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,   # <|>
        Copula2 = Copula.ConcurrentEquivalence,   # <|>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,   # <|>
        Copula2 = Copula.ConcurrentEquivalence,   # <|>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,   # <|>
        Copula2 = Copula.ConcurrentEquivalence,   # <|>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentEquivalence,   # <|>
        Copula2 = Copula.ConcurrentEquivalence,   # <|>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    '''---------NAL 5---------'''

    '''conditianal rules'''

    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction__0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        # LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        # Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction__0_prime, 
        # LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        # Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True
    )
    # '''deduction (compound eliminate)'''
    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_eliminate__0, 
    #     LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     has_common_id = True,
    #     has_compound_at = True,
    #     Copula1 = Copula.PredictiveImplication,
    #     # Copula2 = Copula.PredictiveImplication,
    #     match_reverse = False,
    #     common_id = CommonId(0),
    #     Connector1 = Connector.Conjunction
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_eliminate__0_prime, 
    #     LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     has_common_id = True,
    #     has_compound_at = True,
    #     # Copula1 = Copula.PredictiveImplication,
    #     Copula2 = Copula.PredictiveImplication,
    #     match_reverse = False,
    #     common_id = CommonId(0),
    #     Connector2 = Connector.Conjunction
    # )

    # '''deduction (compound replace)'''
    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_replace__0_1, 
    #     LinkType1 = [
    #         LinkType.COMPOUND_STATEMENT,
    #         LinkType.COMPOUND_CONDITION
    #     ], 
    #     LinkType2 = [
    #         LinkType.COMPOUND_STATEMENT,
    #         LinkType.COMPOUND_CONDITION
    #     ], 
    #     has_common_id = True,
    #     has_compound_common_id = True,
    #     Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     compound_common_id = CommonId(0, 1),
    #     Connector1 = Connector.Conjunction
    # )


    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_replace__1_0, 
    #     LinkType1 = [
    #         LinkType.COMPOUND_STATEMENT,
    #         LinkType.COMPOUND_CONDITION
    #     ], 
    #     LinkType2 = [
    #         LinkType.COMPOUND_STATEMENT,
    #         LinkType.COMPOUND_CONDITION
    #     ], 
    #     has_common_id = True,
    #     has_compound_common_id = True,
    #     Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     compound_common_id = CommonId(1, 0),
    #     Connector2 = Connector.Conjunction
    # )

    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__0_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    '''induction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.ConcurrentImplication,
        Copula2 = Copula.ConcurrentImplication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    '''temporal contitional abduction'''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__abduction__1, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION, 
            LinkType.COMPOUND_STATEMENT
        ],
        # LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = [
            Copula.PredictiveImplication, 
            Copula.ConcurrentImplication, 
            Copula.RetrospectiveImplication
        ],
        # Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__abduction__1_prime, 
        # LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        has_common_id = True,
        # Copula1 = Copula.PredictiveImplication,
        Copula2 = [
            Copula.PredictiveImplication, 
            Copula.ConcurrentImplication, 
            Copula.RetrospectiveImplication
        ],
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True
    )


    '''---------NAL 5---------'''

    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction__0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        # LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = [
            Copula.ConcurrentImplication,
            Copula.PredictiveImplication,
        ],
        # Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction__0_prime, 
        # LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT],
        has_common_id = True,
        # Copula1 = Copula.Implication,
        Copula2 = [
            Copula.ConcurrentImplication,
            Copula.PredictiveImplication,
        ],
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True,
    )

    
    '''---------NAL 7---------'''
    '''sequential conditional deduction (compound eliminate)'''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__deduction_sequence_eliminate__0, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        has_compound_at = True,
        Copula1 = Copula.PredictiveImplication,
        # Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0),
        Connector1 = Connector.SequentialEvents,
        is_belief_valid=True
    )

    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__deduction_sequence_eliminate__0_prime, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        has_compound_at = True,
        # Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0),
        Connector2 = Connector.SequentialEvents,
        is_belief_valid=True
    )

    '''deduction (sequence replace)'''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__deduction_sequence_replace__0_1, 
        LinkType1 = [
            LinkType.COMPOUND_STATEMENT,
            LinkType.COMPOUND_CONDITION
        ], 
        LinkType2 = [
            LinkType.COMPOUND_STATEMENT,
            LinkType.COMPOUND_CONDITION
        ], 
        has_common_id = True,
        has_compound_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        compound_common_id = CommonId(0, 1),
        Connector1 = Connector.SequentialEvents,
        is_belief_valid = True,
    )


    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__deduction_sequence_replace__1_0, 
        LinkType1 = [
            LinkType.COMPOUND_STATEMENT,
            LinkType.COMPOUND_CONDITION
        ], 
        LinkType2 = [
            LinkType.COMPOUND_STATEMENT,
            LinkType.COMPOUND_CONDITION
        ], 
        has_common_id = True,
        has_compound_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        compound_common_id = CommonId(1, 0),
        Connector2 = Connector.SequentialEvents,
        is_belief_valid = True,
    )


