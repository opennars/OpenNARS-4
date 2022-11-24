from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL5(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''syllogystic rules'''

    '''---------NAL 1---------'''
    
    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__0_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__1_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    '''exemplification'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__0_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__1_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    '''induction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    '''reversion'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__reversion, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = True,
        is_belief_valid = True,
    )


    '''---------NAL 2---------'''
    '''comparison'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )
    '''analogy'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Equivalence,   # <=>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Equivalence,    # <=>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Equivalence,    # <=>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Implication,   # ==>
        Copula2 = Copula.Equivalence,    # <=>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,   # <=>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,    # <=>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,    # <=>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,    # <=>
        Copula2 = Copula.Implication,   # ==>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )
    '''resemblance'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,   # <=>
        Copula2 = Copula.Equivalence,   # <=>
        match_reverse = False,
        common_id = CommonId(0, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,   # <=>
        Copula2 = Copula.Equivalence,   # <=>
        match_reverse = False,
        common_id = CommonId(0, 1),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,   # <=>
        Copula2 = Copula.Equivalence,   # <=>
        match_reverse = False,
        common_id = CommonId(1, 0),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        Copula1 = Copula.Equivalence,   # <=>
        Copula2 = Copula.Equivalence,   # <=>
        match_reverse = False,
        common_id = CommonId(1, 1),
        is_belief_valid = True,
    )

    '''---------NAL 3---------'''

    '''
    Compositional Rules
    '''

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__conjunction_extension__0_0, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__conjunction_intension__1_1, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        sentence_type = class_sentence_to_list(Judgement),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__disjunction_extension__0_0, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__disjunction_intension__1_1, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        sentence_type = class_sentence_to_list(Judgement),
        is_belief_valid = True,
    )

    '''
    Decompositional Rules
    '''
    '''conjunction'''
    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND_CONDITION], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND_CONDITION], 
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = False,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.Conjunction,
        Connector2 = Any,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0_prime, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND_CONDITION], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND_CONDITION],  
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = False,
        Connector1 = Any,
        Connector2 = Connector.Conjunction,
        is_belief_valid = True,
    )
    

    

    '''---------NAL 5---------'''

    '''conditianal rules'''

    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction__0, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        # LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Implication,
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
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        # Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True,
    )
    '''deduction (compound eliminate)'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction_compound_eliminate__0, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND], 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        has_compound_at = True,
        Copula1 = Copula.Implication,
        # Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0),
        Connector1 = Connector.Conjunction,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction_compound_eliminate__0_prime, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND], 
        has_common_id = True,
        has_compound_at = True,
        # Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(0),
        Connector2 = Connector.Conjunction,
        is_belief_valid = True
    )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_eliminate__0, 
    #     LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND], 
    #     LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #     has_common_id = True,
    #     has_compound_common_id = True,
    #     Copula1 = Copula.Implication,
    #     # Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     compound_common_id = CommonId(0),
    #     Connector2 = Connector.Conjunction,
    #     is_belief_valid = True
    # )

    # add_rule(sparse_lut, structure,
    #     Interface_ConditionalRules._conditional__deduction_compound_eliminate__0_prime, 
    #     LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND, LinkType.SELF], 
    #     LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.COMPOUND], 
    #     has_common_id = True,
    #     has_compound_common_id = True,
    #     # Copula1 = Copula.Implication,
    #     Copula2 = Copula.Implication,
    #     match_reverse = False,
    #     compound_common_id = CommonId(0),
    #     Connector1 = Connector.Conjunction,
    #     is_belief_valid = True
    # )

    '''deduction (compound replace)'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction_compound_replace__0_1, 
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
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        compound_common_id = CommonId(0, 1),
        Connector1 = Connector.Conjunction,
        is_belief_valid = True,
    )


    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__deduction_compound_replace__1_0, 
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
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        compound_common_id = CommonId(1, 0),
        Connector2 = Connector.Conjunction,
        is_belief_valid = True,
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__abduction__1, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        # LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Implication,
        # Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__abduction__1_prime, 
        # LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        # Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True,
    )

    '''abudction (compound eliminate)'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__abduction_compound_eliminate__1_1, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = False,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.Conjunction,
        Connector2 = None,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__abduction_compound_eliminate__1_1_prime, 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = False,
        Connector1 = None,
        Connector2 = Connector.Conjunction,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        [
            Interface_ConditionalRules._conditional__abduction_compound_eliminate2__1_1,
            Interface_ConditionalRules._conditional__abduction_compound_eliminate2__1_1_prime
        ], 
        LinkType1 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ], 
        LinkType2 = [
            LinkType.COMPOUND_CONDITION,
            LinkType.COMPOUND_STATEMENT
        ],
        has_common_id = True,
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        common_id = CommonId(1, 1),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.Conjunction,
        Connector2 = Connector.Conjunction,
        is_belief_valid = True,
    )

    '''induction (compound replace)'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__induction_compound_replace__0_0, 
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
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        compound_common_id = CommonId(0, 0),
        Connector1 = Connector.Conjunction,
        is_belief_valid = True,
    )


    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__induction_compound_replace__0_0_prime, 
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
        Copula1 = Copula.Implication,
        Copula2 = Copula.Implication,
        match_reverse = False,
        compound_common_id = CommonId(0, 0),
        Connector2 = Connector.Conjunction,
        is_belief_valid = True,
    )

    '''analogy'''
    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__analogy__0, 
        # LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        # Copula1 = Copula.Implication,
        Copula2 = Copula.Equivalence,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__analogy__0_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        # LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.Equivalence,
        # Copula2 = Copula.Equivalence,
        match_reverse = False,
        common_id = CommonId(0),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__analogy__1, 
        # LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        has_common_id = True,
        # Copula1 = Copula.Implication,
        Copula2 = Copula.Equivalence,
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p1_at_p2=True,
        is_belief_valid = True,
    )

    add_rule(sparse_lut, structure,
        Interface_ConditionalRules._conditional__analogy__1_prime, 
        LinkType1 = [LinkType.COMPOUND_CONDITION, LinkType.COMPOUND_STATEMENT], 
        # LinkType2 = LinkType.COMPOUND_CONDITION, 
        has_common_id = True,
        Copula1 = Copula.Equivalence,
        # Copula2 = Copula.Equivalence,
        match_reverse = False,
        common_id = CommonId(1),
        has_at = True,
        p2_at_p1=True,
        is_belief_valid = True,
    )

    '''
    Decompositional Theorems
    '''

    '''decompositional theorem 9'''
    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem9, 
        LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        Connector1 = Connector.Conjunction,
        p2_at_p1 = True,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem9, 
        LinkType1 = LinkType.SELF, 
        LinkType2 = LinkType.COMPONENT, 
        Connector1 = Connector.Conjunction,
        p2_at_p1 = True,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem9_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Conjunction,
        p1_at_p2 = True,
        is_belief_valid = True
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem9_prime, 
        LinkType1 = LinkType.SELF, 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Conjunction,
        p1_at_p2 = True,
        is_belief_valid = True
    )

    '''decompositional theorem 10'''
    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem10, 
        LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        Connector1 = Connector.Disjunction,
        p2_at_p1 = True,
        is_belief_valid = True,
        sentence_type = class_sentence_to_list(Judgement)
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem10, 
        LinkType1 = LinkType.SELF, 
        LinkType2 = LinkType.COMPONENT, 
        Connector1 = Connector.Disjunction,
        p2_at_p1 = True,
        is_belief_valid = True,
        sentence_type = class_sentence_to_list(Judgement)
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem10_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Disjunction,
        p1_at_p2 = True,
        is_belief_valid = True,
        sentence_type = class_sentence_to_list(Judgement)
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem10_prime, 
        LinkType1 = LinkType.SELF, 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Disjunction,
        p1_at_p2 = True,
        is_belief_valid = True,
        sentence_type = class_sentence_to_list(Judgement)
    )


    '''
    Implication Theorems
    '''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__implication_theorem3, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        # LinkType2 = LinkType.COMPOUND, 
        Connector1 = Connector.Conjunction,
        Copula1 = [None],
        p2_at_p1 = True,
        is_belief_valid = False,
    )
    
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__implication_theorem4, 
        # LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Disjunction,
        p1_at_p2 = True,
        is_belief_valid = False
    )

    '''transform negation'''
    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__negation, 
        LinkType1 = LinkType.SELF, 
        LinkType2 = LinkType.COMPONENT, 
        Connector1 = Connector.Negation,
        # p2_at_p1 = True,
        is_belief_valid = False
    )

    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__negation, 
        LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        Connector1 = Connector.Negation,
        # p2_at_p1 = True,
        is_belief_valid = False
    )

    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__negation, 
        LinkType1 = [LinkType.SELF, LinkType.COMPOUND_STATEMENT], 
        LinkType2 = LinkType.COMPOUND, 
        Connector2 = Connector.Negation,
        # p2_at_p1 = True,
        is_belief_valid = False
    )

    '''contraposition'''
    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__contraposition, 
        LinkType1 = LinkType.COMPOUND_CONDITION, 
        LinkType2 = LinkType.COMPONENT, 
        Connector1 = Connector.Negation,
        has_compound_at = True,
        c2_at_c1 = True,
        is_belief_valid = False
    )
    # TODO: other cases should be considered.
    # add_rule(sparse_lut, structure,
    #     Interface_TransformRules._transform__contraposition, 
    #     LinkType1 = LinkType.COMPOUND_CONDITION, 
    #     LinkType2 = LinkType.COMPONENT, 
    #     Connector1 = Connector.Negation,
    #     has_compound_common_id = True,
    #     c2_at_c1 = True,
    #     is_belief_valid = False
    # )