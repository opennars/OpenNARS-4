from collections import OrderedDict
from opennars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from opennars import Global
from ....RuleMap.add_rule import *

def add_rules__NAL1(sparse_lut: SparseLUT, structure: OrderedDict):

    '''deduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__0_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__deduction__1_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 0),
        has_compound_at = False
    )

    '''exemplification'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__0_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__exemplification__1_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 0),
        has_compound_at = False
    )

    '''induction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__induction__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__abduction__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )

    '''reversion'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__reversion, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,
        Copula2 = Copula.Inheritance,
        match_reverse = True
    )