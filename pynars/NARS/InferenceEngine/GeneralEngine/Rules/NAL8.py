from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from pynars.Narsese._py import SELF
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL8(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''
    (&/,A, B, C)!
    A
    |-
    A!
    '''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__sequence_immediate, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        LinkType2 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.TRANSFORM],
        has_common_id = True,
        p2_at_p1 = True,
        sentence_type = class_sentence_to_list(Goal),
        Connector1 = Connector.SequentialEvents,
        match_reverse = False,
        is_belief_valid = False
    )

    '''
    (&/,A, B, C)!
    A.
    |-
    (&/, B, C)!
    '''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__sequence, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        LinkType2 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.TRANSFORM],
        has_common_id = True,
        p2_at_p1 = True,
        sentence_type = class_sentence_to_list(Goal),
        Connector1 = Connector.SequentialEvents,
        match_reverse = False,
        is_belief_valid = True
    )

    '''
    C!
    (&/,A, B, C).
    |-
    (&/, A, B)!
    '''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__sequence_prime, 
        LinkType1 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.SELF, LinkType.TRANSFORM], 
        LinkType2 = [LinkType.COMPOUND, LinkType.COMPOUND_STATEMENT],
        has_common_id = True,
        p1_at_p2 = True,
        sentence_type = class_sentence_to_list(Goal),
        Connector2 = Connector.SequentialEvents,
        match_reverse = False,
        is_belief_valid = True
    )

    '''
    (&/, A, B, C).
    A.
    |- 
    (&/, B, C).
    '''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__sequence, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        LinkType2 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.TRANSFORM],
        has_common_id = True,
        p2_at_p1 = True,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = Connector.SequentialEvents,
        match_reverse = False,
        is_belief_valid = True
    )
    # add_rule(sparse_lut, structure,
    #     Interface_TemporalRules._temporal__sequence_prime, 
    #     LinkType1 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
    #     LinkType2 = [LinkType.COMPOUND, LinkType.COMPOUND_STATEMENT],
    #     has_common_id = True,
    #     p1_at_p2 = True,
    #     sentence_type = class_sentence_to_list(Judgement),
    #     Connector2 = Connector.SequentialEvents,
    #     match_reverse = False,
    #     is_belief_valid = True
    # )

    '''
    (&|,A, B, C)!
    B.
    |-
    (&|,A, C)!
    '''
    add_rule(sparse_lut, structure,
        Interface_TemporalRules._temporal__parallel, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        LinkType2 = [LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.TRANSFORM],
        has_common_id = True,
        p2_at_p1 = True,
        sentence_type = class_sentence_to_list(Goal),
        Connector1 = Connector.ParallelEvents,
        match_reverse = False,
        is_belief_valid = True
    )
    # add_rule(sparse_lut, structure,
    #     Interface_TemporalRules._temporal__parallel_prime, 
    #     LinkType1 = [LinkType.SELF, LinkType.COMPONENT, LinkType.COMPOUND_STATEMENT, LinkType.COMPONENT_STATEMENT],
    #     LinkType2 = [LinkType.COMPOUND], 
    #     has_common_id = True,
    #     p1_at_p2 = True,
    #     sentence_type = class_sentence_to_list(Goal),
    #     Connector2 = Connector.ParallelEvents,
    #     match_reverse = False,
    #     is_belief_valid = True
    # )
    
    '''
    (&|, A, B)!
    A
    |-
    A!
    '''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__implication_theorem3, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        # LinkType2 = LinkType.COMPOUND, 
        Connector1 = Connector.ParallelEvents,
        Copula1 = [None],
        p2_at_p1 = True,
        is_belief_valid = False,
    )