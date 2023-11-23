from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL2(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    '''comparison'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__0_0_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__comparison__1_1_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )
    '''analogy'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Similarity,   # <->
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Similarity,    # <->
        match_reverse = False,
        common_id = CommonId(0, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Similarity,    # <->
        match_reverse = False,
        common_id = CommonId(1, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Inheritance,   # -->
        Copula2 = Copula.Similarity,    # <->
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,   # <->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__0_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,    # <->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(0, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,    # <->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(1, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__analogy__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,    # <->
        Copula2 = Copula.Inheritance,   # -->
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )
    '''resemblance'''
    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,   # <->
        Copula2 = Copula.Similarity,   # <->
        match_reverse = False,
        common_id = CommonId(0, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__0_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,   # <->
        Copula2 = Copula.Similarity,   # <->
        match_reverse = False,
        common_id = CommonId(0, 1),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,   # <->
        Copula2 = Copula.Similarity,   # <->
        match_reverse = False,
        common_id = CommonId(1, 0),
        has_compound_at = False
    )

    add_rule(sparse_lut, structure,
        Interface_SyllogisticRules._syllogistic__resemblance__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        has_common_id = True,
        Copula1 = Copula.Similarity,   # <->
        Copula2 = Copula.Similarity,   # <->
        match_reverse = False,
        common_id = CommonId(1, 1),
        has_compound_at = False
    )

    '''
    {<S <-> P>., [S]} |- <[S] <-> [P]>.
    {<S <-> P>., {S}} |- <{S} <-> {P}>.

    {<S <-> P>., [P]} |- <[S] <-> [P]>.
    {<S <-> P>., {P}} |- <{S} <-> {P}>.
    '''
    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__0,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Similarity,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [Connector.IntensionalSet, Connector.ExtensionalSet],
        has_compound_common_id = True,
        compound_common_id = CommonId(0),
        is_belief_valid = False,
    )

    add_rule(sparse_lut, structure,
        Interface_CompositionalRules._structural__bi_composition__1,
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND, 
        has_common_id = True,
        Copula1 = Copula.Similarity,
        Copula2 = None,
        match_reverse = False,
        sentence_type = class_sentence_to_list(Judgement),
        Connector1 = None,
        Connector2 = [Connector.IntensionalSet, Connector.ExtensionalSet],
        has_compound_common_id = True,
        compound_common_id = CommonId(1),
        is_belief_valid = False,
    )