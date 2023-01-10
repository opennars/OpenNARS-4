from collections import OrderedDict
from pynars.NARS.DataStructures import LinkType, TaskLink, TermLink
from sparse_lut import SparseLUT
from pynars import Global
from ....RuleMap.add_rule import *


def add_rules__NAL6(sparse_lut: SparseLUT, structure: OrderedDict):
    ''''''
    ''' 
    variable introduction
    '''

    '''induction'''
    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__induction, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__induction_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__implication__induction, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 0,
        L2_Copula1 = Copula.Inheritance,
        L2_common1 = 0,        
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__conjunction__induction, 
        LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Connector1 = Connector.Conjunction,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = [None],
        L1_common2 = 0,
        L2_Copula1 = Copula.Inheritance,
        L2_common1 = 0,
        sentence_type = class_sentence_to_list(Judgement),
    )

    '''abduction'''
    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__abduction, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 1,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__abduction_prime, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 1,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )


    '''comparison'''
    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__comparison__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__comparison__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 1,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    '''intersection'''
    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_introduction__intersection__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT,
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_introduction__intersection__1_1, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Inheritance,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 1,
        L2_common1 = [None],
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__implication0__intersection__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_Copula1 = Copula.Inheritance,
        L2_common1 = 0,        
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__independent_variable_introduction__implication1__intersection__0_0, 
        LinkType1 = LinkType.COMPOUND_STATEMENT, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 0,
        L2_Copula1 = Copula.Inheritance,
        L2_common1 = 0,        
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_introduction__conjunction__intersection, 
        LinkType1 = LinkType.COMPOUND, 
        LinkType2 = LinkType.COMPOUND_STATEMENT, 
        L1_Connector1 = Connector.Conjunction,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = [None],
        L1_common2 = 0,
        L2_Copula1 = Copula.Inheritance,
        L2_common1 = 0,
        sentence_type = class_sentence_to_list(Judgement),
    )

    ''' 
    dependent variable elimination
    '''

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_elimination__conjunction__1_1, 
        LinkType1 = [LinkType.COMPOUND, LinkType.SELF], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        L1_Connector1 = Connector.Conjunction,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = [None],
        L1_common2 = 1,
        L2_common1 = 1,
        L2_eliminable = True,
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_elimination__implication1__1_1, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF, LinkType.COMPOUND_CONDITION], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 1,
        L1_common2 = 1,
        L2_Connector1 = Connector.Conjunction,
        L2_has_common = True,
        L2_common1 = [None],
        L3_Copula = Copula.Inheritance,
        L3_common1 = 1,
        L3_eliminable = True,
        sentence_type = class_sentence_to_list(Judgement),
    )


    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_elimination__implication0__inheritance__1_1, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF, LinkType.COMPOUND_CONDITION], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Inheritance,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 1,
        L2_Connector1 = Connector.Conjunction,
        L2_has_common = True,
        L2_common1 = [None],
        L3_Copula = Copula.Inheritance,
        L3_common1 = 1,
        L3_eliminable = True,
        sentence_type = class_sentence_to_list(Judgement),
    )

    add_rule(sparse_lut, structure,
        Interface_VariableRules._variable__dependent_variable_elimination__implication0__implication__1_1, 
        LinkType1 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF, LinkType.COMPOUND_CONDITION], 
        LinkType2 = [LinkType.COMPOUND_STATEMENT, LinkType.SELF], 
        L1_Copula1 = Copula.Implication,
        L1_Copula2 = Copula.Implication,
        match_reverse = False,
        L1_common1 = 0,
        L1_common2 = 0,
        L2_Connector1 = Connector.Conjunction,
        L2_Copula2 = Copula.Inheritance,
        L2_has_common = True,
        L2_common1 = [None],
        L2_common2 = 1,
        L3_Copula = Copula.Inheritance,
        L3_common1 = 1,
        L3_eliminable = True,
        sentence_type = class_sentence_to_list(Judgement),
    )
