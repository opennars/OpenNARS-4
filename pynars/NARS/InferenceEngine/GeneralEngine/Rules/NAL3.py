from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *

def add_rules__NAL3(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''
    Compositinal Rules
    '''
    '''First-order with common subject'''

    '''intersection_extension'''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__intersection_extension__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement)
    )

    '''union_extension'''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__union_extension__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement)
    )


    '''First-order with common predicate'''

    '''intersection_intension'''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__intersection_intension__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 1),
        sentence_type = class_sentence_to_list(Judgement)
    )

    '''union_intension'''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._compositional__union_intension__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 1),
        sentence_type = class_sentence_to_list(Judgement)
    )
    

    '''
    Decompositinal Rules
    '''

    '''intensional intersection'''
    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = False,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.IntensionalIntersection,
        Connector2 = Any
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = False,
        Connector1 = Any,
        Connector2 = Connector.IntensionalIntersection
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.ExtensionalSet,
        Connector2 = Connector.ExtensionalSet
    )

    add_rule(sparse_lut, structure,
        Interface_DecompositionalRules._decompositional__decomposition_theorem2__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.ExtensionalSet,
        Connector2 = Connector.ExtensionalSet
    )

    '''extensional difference'''
    add_rule(sparse_lut, structure,
        #[
        Interface_DecompositionalRules._decompositional__decomposition_theorem3__0_0,
        # Interface_DecompositionalRules._decompositional__decomposition_theorem4__0_0,
        # ], 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = False,
        the_other_compound_p2_at_p1 = True,
        Connector1 = Connector.ExtensionalDifference,
        Connector2 = Any
    )

    add_rule(sparse_lut, structure,
        # [
        Interface_DecompositionalRules._decompositional__decomposition_theorem3__0_0_prime,
        # Interface_DecompositionalRules._decompositional__decomposition_theorem4__0_0_prime,
        # ], 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        sentence_type = class_sentence_to_list(Judgement),
        the_other_compound_has_common = True,
        the_other_compound_p1_at_p2 = True,
        the_other_compound_p2_at_p1 = False,
        Connector1 = Any,
        Connector2 = Connector.ExtensionalDifference
    )

    '''Theorems'''

    '''bi-composition'''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__0,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.ExtensionalIntersection,
            Connector.IntensionalIntersection,
            Connector.ExtensionalDifference,
            Connector.IntensionalDifference
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__1,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.ExtensionalIntersection,
            Connector.IntensionalIntersection,
            Connector.ExtensionalDifference,
            Connector.IntensionalDifference
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__0_prime,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.ExtensionalDifference,
            Connector.IntensionalDifference            
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        at_compound_pos = 1
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__1_prime,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.ExtensionalDifference,
            Connector.IntensionalDifference            
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = 1
    )


    '''uni-composition'''
    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_composition__0,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.ExtensionalIntersection,
            Connector.ExtensionalDifference,
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )

    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_composition__1,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [
            Connector.IntensionalIntersection,
            Connector.IntensionalDifference
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )


    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_composition__0_prime,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = Connector.IntensionalDifference,
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        at_compound_pos = 1
    )

    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_composition__1_prime,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = Connector.ExtensionalDifference,
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = 1
    )

    '''uni-decomposition'''
    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_decomposition__0,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPONENT, 
        has_common_id = True,
        has_compound_at = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Any,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = [
            Connector.ExtensionalIntersection,
            Connector.ExtensionalDifference
        ],
        Connector2 = None,
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )

    add_rule(sparse_lut, structure,
        
        Interface_CompositionalRules._structural__uni_decomposition__1,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPONENT, 
        has_common_id = True,
        has_compound_at = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Any,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = [
            Connector.IntensionalIntersection,
            Connector.IntensionalDifference
        ],
        Connector2 = None,
        is_belief_valid = False,
        at_compound_pos = [0, None]
    )