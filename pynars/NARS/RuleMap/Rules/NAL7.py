from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from pynars.utils.SparseLUT import SparseLUT
from pynars import Global
from .add_rule import *


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
        common_id = CommonId(0, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(1, 0)
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
        common_id = CommonId(0, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__1_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(1, 0)
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
        common_id = CommonId(0, 0)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,
        Copula2 = Copula.RetrospectiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,
        Copula2 = Copula.PredictiveImplication,
        match_reverse = False,
        common_id = CommonId(0, 0)
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
        common_id = CommonId(1, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(1, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1)
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
        common_id = CommonId(0, 0)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(0, 0)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.PredictiveImplication,     # =/>
        Copula2 = Copula.RetrospectiveImplication,  # =\>
        match_reverse = False,
        common_id = CommonId(1, 1)
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.RetrospectiveImplication,  # =\>
        Copula2 = Copula.PredictiveImplication,     # =/>
        match_reverse = False,
        common_id = CommonId(1, 1)
    )

    '''reversion?'''

    '''---------------'''


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
        p2_at_p1=True
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
        p1_at_p2=True
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

    '''abduction'''
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
        p2_at_p1=True
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
        p1_at_p2=True
    )

    # '''abudction (compound eliminate)'''
    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__abduction_compound_eliminate__1_1, 
    #     LinkType1 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ], 
    #     LinkType2 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ],
    #     has_common_id = True,
    #     Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     common_id = CommonId(1, 1),
    #     the_other_compound_has_common = True,
    #     the_other_compound_p1_at_p2 = False,
    #     the_other_compound_p2_at_p1 = True,
    #     Connector1 = Connector.Conjunction,
    #     Connector2 = None
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__abduction_compound_eliminate__1_1_prime, 
    #     LinkType1 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ], 
    #     LinkType2 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ],
    #     has_common_id = True,
    #     Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     common_id = CommonId(1, 1),
    #     the_other_compound_has_common = True,
    #     the_other_compound_p1_at_p2 = True,
    #     the_other_compound_p2_at_p1 = False,
    #     Connector1 = None,
    #     Connector2 = Connector.Conjunction
    # )

    # add_rule(sparse_lut, structure,
    #     [
    #         Interface_ConditionalRules._conditional__abduction_compound_eliminate2__1_1,
    #         Interface_ConditionalRules._conditional__abduction_compound_eliminate2__1_1_prime
    #     ], 
    #     LinkType1 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ], 
    #     LinkType2 = [
    #         LinkType.COMPOUND_CONDITION,
    #         LinkType.COMPOUND_STATEMENT
    #     ],
    #     has_common_id = True,
    #     Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     common_id = CommonId(1, 1),
    #     the_other_compound_has_common = True,
    #     the_other_compound_p1_at_p2 = True,
    #     the_other_compound_p2_at_p1 = True,
    #     Connector1 = Connector.Conjunction,
    #     Connector2 = Connector.Conjunction
    # )

    # '''induction (compound replace)'''
    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__induction_compound_replace__0_0, 
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
    #     compound_common_id = CommonId(0, 0),
    #     Connector1 = Connector.Conjunction
    # )


    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__induction_compound_replace__0_0_prime, 
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
    #     compound_common_id = CommonId(0, 0),
    #     Connector2 = Connector.Conjunction
    # )

    # '''analogy'''
    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__analogy__0, 
    #     # LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     LinkType2 = LinkType.COMPOUND_CONDITION, 
    #     has_common_id = True,
    #     # Copula1 = Copula.Implication,
    #     Copula2 = Copula.Equivalence,
    #     match_reverse = False,
    #     common_id = CommonId(0),
    #     has_at = True,
    #     p1_at_p2=True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__analogy__0_prime, 
    #     LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     # LinkType2 = LinkType.COMPOUND_CONDITION, 
    #     has_common_id = True,
    #     Copula1 = Copula.Equivalence,
    #     # Copula2 = Copula.Equivalence,
    #     match_reverse = False,
    #     common_id = CommonId(0),
    #     has_at = True,
    #     p2_at_p1=True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__analogy__1, 
    #     # LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     LinkType2 = LinkType.COMPOUND_CONDITION, 
    #     has_common_id = True,
    #     # Copula1 = Copula.Implication,
    #     Copula2 = Copula.Equivalence,
    #     match_reverse = False,
    #     common_id = CommonId(1),
    #     has_at = True,
    #     p1_at_p2=True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__analogy__1_prime, 
    #     LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     # LinkType2 = LinkType.COMPOUND_CONDITION, 
    #     has_common_id = True,
    #     Copula1 = Copula.Equivalence,
    #     # Copula2 = Copula.Equivalence,
    #     match_reverse = False,
    #     common_id = CommonId(1),
    #     has_at = True,
    #     p2_at_p1=True
    # )

    # '''
    # Decompositional Theorems
    # '''

    # '''decompositional theorem 9'''
    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem9, 
    #     LinkType1 = LinkType.COMPOUND, 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     Connector1 = Connector.Conjunction,
    #     p2_at_p1 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem9, 
    #     LinkType1 = LinkType.SELF, 
    #     LinkType2 = LinkType.COMPONENT, 
    #     Connector1 = Connector.Conjunction,
    #     p2_at_p1 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem9_prime, 
    #     LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Conjunction,
    #     p1_at_p2 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem9_prime, 
    #     LinkType1 = LinkType.SELF, 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Conjunction,
    #     p1_at_p2 = True,
    #     is_belief_valid = True
    # )

    # '''decompositional theorem 10'''
    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem10, 
    #     LinkType1 = LinkType.COMPOUND, 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     Connector1 = Connector.Disjunction,
    #     p2_at_p1 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem10, 
    #     LinkType1 = LinkType.SELF, 
    #     LinkType2 = LinkType.COMPONENT, 
    #     Connector1 = Connector.Disjunction,
    #     p2_at_p1 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem10_prime, 
    #     LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Disjunction,
    #     p1_at_p2 = True,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_DecompositionalRules._decompositional__decomposition_theorem10_prime, 
    #     LinkType1 = LinkType.SELF, 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Disjunction,
    #     p1_at_p2 = True,
    #     is_belief_valid = True
    # )


    # '''
    # Implication Theorems
    # '''
    # add_rule(sparse_lut, structure,
    #     Interface_CompositionalRules._structural__implication_theorem3, 
    #     LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
    #     # LinkType2 = LinkType.COMPOUND, 
    #     Connector1 = Connector.Conjunction,
    #     p2_at_p1 = True,
    #     is_belief_valid = False
    # )
    
    # add_rule(sparse_lut, structure,
    #     Interface_CompositionalRules._structural__implication_theorem4, 
    #     # LinkType1 = LinkType.COMPOUND, 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Disjunction,
    #     p1_at_p2 = True,
    #     is_belief_valid = False
    # )

    # '''transform negation'''
    # add_rule(sparse_lut, structure,
    #     Interface_TransformRules._transform__negation, 
    #     LinkType1 = LinkType.SELF, 
    #     LinkType2 = LinkType.COMPONENT, 
    #     Connector1 = Connector.Negation,
    #     # p2_at_p1 = True,
    #     is_belief_valid = False
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_TransformRules._transform__negation, 
    #     LinkType1 = LinkType.COMPOUND, 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     Connector1 = Connector.Negation,
    #     # p2_at_p1 = True,
    #     is_belief_valid = False
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_TransformRules._transform__negation, 
    #     LinkType1 = [LinkType.SELF, LinkType.COMPOUND_STATEMENT], 
    #     LinkType2 = LinkType.COMPOUND, 
    #     Connector2 = Connector.Negation,
    #     # p2_at_p1 = True,
    #     is_belief_valid = False
    # )

    # '''contraposition'''
    # add_rule(sparse_lut, structure,
    #     Interface_TransformRules._transform__contraposition, 
    #     LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     LinkType2 = LinkType.COMPONENT, 
    #     Connector1 = Connector.Negation,
    #     has_compound_at = True,
    #     c2_at_c1 = True,
    #     is_belief_valid = False
    # )
    # # TODO: other cases should be considered.
    # # add_rule(sparse_lut, structure,
    # #     Interface_TransformRules._transform__contraposition, 
    # #     LinkType1 = LinkType.COMPOUND_CONDITION, 
    # #     LinkType2 = LinkType.COMPONENT, 
    # #     Connector1 = Connector.Negation,
    # #     has_compound_common_id = True,
    # #     c2_at_c1 = True,
    # #     is_belief_valid = False
    # # )

    '''---------NAL 7---------'''
    '''sequential conditional deduction (compound eliminate)'''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__deduction_sequence_eliminate__0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
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
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
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

