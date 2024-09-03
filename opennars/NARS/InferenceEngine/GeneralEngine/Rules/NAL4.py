from collections import OrderedDict
from opennars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from opennars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL4(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''transform'''
    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__product_to_image, 
        LinkType1 = LinkType.TRANSFORM, 
        LinkType2 = None,
        has_common_id = True,
        Connector1 = Connector.Product
    )

    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__image_to_product, 
        LinkType1 = LinkType.TRANSFORM, 
        LinkType2 = None,
        has_common_id = True,
        Connector1 = [
            Connector.IntensionalImage, 
            Connector.ExtensionalImage
        ]
    )

    add_rule(sparse_lut, structure,
        Interface_TransformRules._transform__image_to_image, 
        LinkType1 = LinkType.TRANSFORM, 
        LinkType2 = [None],
        has_common_id = True,
        Connector1 = [
            Connector.IntensionalImage, 
            Connector.ExtensionalImage
        ]
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
        Connector2 = Connector.Product,
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        # at_compound_pos = 0
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
        Connector2 = Connector.Product,
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        # at_compound_pos = 0
    )

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
            # Connector.Product,
            Connector.ExtensionalImage,
            Connector.IntensionalImage
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
        at_compound_pos = 0
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
            # Connector.Product,
            Connector.ExtensionalImage,
            Connector.IntensionalImage
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = 0
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
            Connector.ExtensionalImage,
            Connector.IntensionalImage
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
            Connector.ExtensionalImage,
            Connector.IntensionalImage
        ],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
        at_compound_pos = 1
    )