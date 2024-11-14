"""
    Author: Christian Hahm
    Created: March 8, 2021
    Purpose: Given premises, performs proper inference and returns the resultant sentences as Tasks.
"""
import timeit as time

import Asserts
import Config
import Global
import NALGrammar
import NALInferenceRules.Immediate
import NALInferenceRules.Syllogistic
import NALInferenceRules.Composition
import NALInferenceRules.Local
import NALInferenceRules.Conditional
import NALInferenceRules.Temporal
import NALInferenceRules.HelperFunctions
import NARSDataStructures.Other

import NALSyntax


def do_semantic_inference_two_premise(j1, j2):
    if not NALGrammar.Sentences.may_interact(j1, j2): return []

    try:
        if isinstance(j1, NALGrammar.Sentences.Goal) and isinstance(j2, NALGrammar.Sentences.Judgment):
            results = do_semantic_inference_goal_judgment(j1, j2)
        else:
            results = do_semantic_inference_two_judgment(j1, j2)
    except Exception as error:
        assert False, "ERROR: Inference error " + str(error) + " between " + str(j1) + " and " + str(j2)

    return results


def do_semantic_inference_two_judgment(j1: NALGrammar.Sentences, j2: NALGrammar.Sentences) -> [
    NARSDataStructures.Other.Task]:
    """
        Derives a new task by performing the appropriate inference rules on the given semantically related sentences.
        The resultant sentence's evidential base is merged from its parents.

        :param j1: Sentence (Question or Judgment)
        :param j2: Semantically related belief (Judgment)

        :assume j1 and j2 have distinct evidential bases B1 and B2: B1 ⋂ B2 = Ø
                (no evidential overlap)

        :returns An array of the derived Tasks, or an empty array if the inputs have evidential overlap
    """

    Asserts.assert_sentence(j1)
    Asserts.assert_sentence(j2)

    if Config.DEBUG: Global.Global.debug_print(
        "Trying inference between: " + j1.get_formatted_string() + " and " + j2.get_formatted_string())

    """
    ===============================================
    ===============================================
        Pre-Processing
    ===============================================
    ===============================================
    """

    if j1.value.confidence == 0 or j2.value.confidence == 0:
        if Config.DEBUG: Global.Global.debug_print("Can't do inference between negative premises")
        return []  # can't do inference with 2 entirely negative premises

    all_derived_sentences = []

    j1_statement = j1.statement
    j2_statement = j2.statement

    # same statement
    if j1_statement == j2_statement:
        """
        # Revision
        # j1 = j2
        """
        if isinstance(j1,
                      NALGrammar.Sentences.Question): return all_derived_sentences  # can't do revision with questions

        derived_sentence = NALInferenceRules.Local.Revision(j1, j2)  # S-->P
        add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        return all_derived_sentences

    if j1.value.frequency == 0 or j2.value.frequency == 0:
        if Config.DEBUG: Global.Global.debug_print("Can't do inference between negative premises")
        return []  # can't do inference with 2 entirely negative premises

    """
    ===============================================
    ===============================================
        First-order and Higher-Order Syllogistic Rules
    ===============================================
    ===============================================
    """
    if isinstance(j1.statement, NALGrammar.Terms.CompoundTerm):
        if isinstance(j2.statement, NALGrammar.Terms.StatementTerm) \
                and not j2.statement.is_first_order():
            if j2.statement.get_copula() == NALSyntax.Copula.Implication \
                    or j2.statement.get_copula() == NALSyntax.Copula.PredictiveImplication:
                derived_sentence = NALInferenceRules.Conditional.ConditionalJudgmentDeduction(j2, j1)  # S-->P
                if j2.statement.get_copula() == NALSyntax.Copula.PredictiveImplication: derived_sentence.stamp.occurrence_time = Global.Global.get_current_cycle_number()
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j2, j1)
                return all_derived_sentences

    if isinstance(j2.statement, NALGrammar.Terms.CompoundTerm):
        if isinstance(j1.statement, NALGrammar.Terms.StatementTerm) \
                and not j1.statement.is_first_order():
            if j1.statement.get_copula() == NALSyntax.Copula.Implication \
                    or j1.statement.get_copula() == NALSyntax.Copula.PredictiveImplication:
                derived_sentence = NALInferenceRules.Conditional.ConditionalJudgmentDeduction(j1, j2)  # S-->P
                if j1.statement.get_copula() == NALSyntax.Copula.PredictiveImplication: derived_sentence.stamp.occurrence_time = Global.Global.get_current_cycle_number()
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                return all_derived_sentences

    swapped = False

    if isinstance(j1.statement, NALGrammar.Terms.StatementTerm) and isinstance(j2.statement,
                                                                               NALGrammar.Terms.StatementTerm) and \
            NALSyntax.Copula.is_first_order(j1.statement.get_copula()) == NALSyntax.Copula.is_first_order(
        j2.statement.get_copula()):
        j1_subject_term = j1.statement.get_subject_term()
        j2_subject_term = j2.statement.get_subject_term()
        j1_predicate_term = j1.statement.get_predicate_term()
        j2_predicate_term = j2.statement.get_predicate_term()
        j1_copula = j1.statement.get_copula()
        j2_copula = j2.statement.get_copula()

        # check if the result will lead to tautology
        tautology = (j1_subject_term == j2_predicate_term and j1_predicate_term == j2_subject_term) or \
                    (j1_subject_term == j2_subject_term and j1_predicate_term == j2_predicate_term
                     and
                     ((not NALSyntax.Copula.is_symmetric(j1_copula) and NALSyntax.Copula.is_symmetric(
                         j2_copula))  # S-->P and P<->S
                      or
                      (NALSyntax.Copula.is_symmetric(j1_copula) and not NALSyntax.Copula.is_symmetric(
                          j2_copula))))  # S<->P and S-->P

        if tautology:
            if Config.DEBUG: Global.Global.debug_print("tautology")
            return all_derived_sentences  # can't do inference, it will result in tautology

        if NALSyntax.Copula.is_temporal(j1.statement.get_copula()) \
                or (isinstance(j1, NALGrammar.Sentences.Judgment)
                    and j1.is_event()) or (isinstance(j2, NALGrammar.Sentences.Judgment) and j2.is_event()):
            # dont do semantic inference with temporal
            # todo .. don't do inference with events, it isn't handled gracefully right now
            return all_derived_sentences
        elif not NALSyntax.Copula.is_symmetric(j1.statement.get_copula()) and not NALSyntax.Copula.is_symmetric(
                j2.statement.get_copula()):
            if j1_subject_term == j2_predicate_term or j1_predicate_term == j2_subject_term:
                """
                    j1 = M-->P, j2 = S-->M
                OR swapped premises
                    j1 = S-->M, j2 = M-->P
                """
                if j1_subject_term != j2_predicate_term:
                    """
                        j1=S-->M, j2=M-->P

                        Swap these premises
                    """

                    j1, j2 = j2, j1

                """
                    j1 = M-->P, j2 = S-->M
                """
                if not j1.is_array and not j2.is_array:
                    """
                    # Deduction
                    """

                    derived_sentence = NALInferenceRules.Syllogistic.Deduction(j1, j2)  # S-->P
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Swapped Exemplification
                    """
                    derived_sentence = NALInferenceRules.Syllogistic.Exemplification(j2, j1)  # P-->S
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

            elif j1.statement.get_subject_term() == j2.statement.get_subject_term():
                """
                    j1=M-->P
                    j2=M-->S
                """
                if not j1.is_array and not j2.is_array:
                    """
                    # Induction
                    """
                    derived_sentence = NALInferenceRules.Syllogistic.Induction(j1, j2)  # S-->P
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Swapped Induction
                    """
                    derived_sentence = NALInferenceRules.Syllogistic.Induction(j2, j1)  # P-->S
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Comparison
                    """
                    derived_sentence = NALInferenceRules.Syllogistic.Comparison(j1, j2)  # S<->P
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Intensional Intersection or Disjunction
                    """
                    derived_sentence = NALInferenceRules.Composition.DisjunctionOrIntensionalIntersection(j1,
                                                                                                          j2)  # M --> (S | P)
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Extensional Intersection or Conjunction
                    """
                    derived_sentence = NALInferenceRules.Composition.ConjunctionOrExtensionalIntersection(j1,
                                                                                                          j2)  # M --> (S & P)
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Extensional Difference
                    """
                    derived_sentence = NALInferenceRules.Composition.ExtensionalDifference(j1, j2)  # M --> (S - P)
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                    """
                    # Swapped Extensional Difference
                    """
                    derived_sentence = NALInferenceRules.Composition.ExtensionalDifference(j2, j1)  # M --> (P - S)
                    add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
            elif j1.statement.get_predicate_term() == j2.statement.get_predicate_term():
                """
                    j1 = P-->M
                    j2 = S-->M
                """

                """
                # Abduction
                """
                derived_sentence = NALInferenceRules.Syllogistic.Abduction(j1, j2)  # S-->P or S==>P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Abduction
                """
                derived_sentence = NALInferenceRules.Syllogistic.Abduction(j2, j1)  # P-->S or P==>S
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                if not NALSyntax.Copula.is_first_order(j1_copula):
                    # two implication statements
                    if NALSyntax.TermConnector.is_conjunction(j1_subject_term.connector) or \
                            NALSyntax.TermConnector.is_conjunction(j2_subject_term.connector):
                        j1_subject_statement_terms = j1_subject_term.subterms if NALSyntax.TermConnector.is_conjunction(
                            j1_subject_term.connector) else [j1_subject_term]

                        j2_subject_statement_terms = j2_subject_term.subterms if NALSyntax.TermConnector.is_conjunction(
                            j2_subject_term.connector) else [j2_subject_term]

                        difference_of_subterms = list(
                            set(j1_subject_statement_terms) - set(j2_subject_statement_terms)) + list(
                            set(j2_subject_statement_terms) - set(j1_subject_statement_terms))

                        if len(difference_of_subterms) == 1:
                            """
                               At least one of the statement's subjects is conjunctive and differs from the
                               other statement's subject by 1 term
                            """
                            if len(j1_subject_statement_terms) > len(j2_subject_statement_terms):
                                derived_sentence = NALInferenceRules.Conditional.ConditionalConjunctionalAbduction(j1,
                                                                                                                   j2)  # S
                            else:
                                derived_sentence = NALInferenceRules.Conditional.ConditionalConjunctionalAbduction(j2,
                                                                                                                   j1)  # S
                            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Intensional Intersection Disjunction
                """
                derived_sentence = NALInferenceRules.Composition.DisjunctionOrIntensionalIntersection(j1,
                                                                                                      j2)  # (P | S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Extensional Intersection Conjunction
                """
                derived_sentence = NALInferenceRules.Composition.ConjunctionOrExtensionalIntersection(j1,
                                                                                                      j2)  # (P & S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Intensional Difference
                """
                derived_sentence = NALInferenceRules.Composition.IntensionalDifference(j1, j2)  # (P ~ S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Intensional Difference
                """
                derived_sentence = NALInferenceRules.Composition.IntensionalDifference(j2, j1)  # (S ~ P) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                """
                # Comparison
                """
                derived_sentence = NALInferenceRules.Syllogistic.Comparison(j1, j2)  # S<->P or S<=>P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        elif not NALSyntax.Copula.is_symmetric(j1.statement.get_copula()) and NALSyntax.Copula.is_symmetric(
                j2.statement.get_copula()):
            """
            # j1 = M-->P or P-->M
            # j2 = S<->M or M<->S
            # Analogy
            """
            derived_sentence = NALInferenceRules.Syllogistic.Analogy(j1, j2)  # S-->P or P-->S
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        elif NALSyntax.Copula.is_symmetric(j1.statement.get_copula()) and not NALSyntax.Copula.is_symmetric(
                j2.statement.get_copula()):
            """
            # j1 = M<->S or S<->M
            # j2 = P-->M or M-->P
            # Swapped Analogy
            """
            derived_sentence = NALInferenceRules.Syllogistic.Analogy(j2, j1)  # S-->P or P-->S
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        elif NALSyntax.Copula.is_symmetric(j1.statement.get_copula()) and NALSyntax.Copula.is_symmetric(
                j2.statement.get_copula()):
            """
            # j1 = M<->P or P<->M
            # j2 = S<->M or M<->S
            # Resemblance
            """
            derived_sentence = NALInferenceRules.Syllogistic.Resemblance(j1, j2)  # S<->P
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
    elif (isinstance(j1.statement, NALGrammar.Terms.StatementTerm) and not j1.statement.is_first_order()) \
            or (isinstance(j2.statement, NALGrammar.Terms.StatementTerm) and not j2.statement.is_first_order()):
        # One premise is a higher-order statement
        """
                j1 = S==>P or S<=>P
                j2 = A-->B or A<->B
            OR
                j1 = A-->B or A<->B
                j2 = S==>P or S<=>P
        """
        if isinstance(j2.statement, NALGrammar.Terms.StatementTerm) and not j2.statement.is_first_order():
            """
                j1 = A-->B or A<->B 
                j2 = S==>P or S<=>P
            """
            # swap sentences so j1 is higher order
            j1, j2 = j2, j1
            swapped = True

        assert (isinstance(j1.statement, NALGrammar.Terms.StatementTerm) and not j1.statement.is_first_order()), "ERROR"

        """
            j1 = S==>P or S<=>P
        """
        if NALSyntax.Copula.is_symmetric(j1.statement.get_copula()) and (
                j2.statement == j1.statement.get_subject_term() or j2.statement == j1.statement.get_predicate_term()):
            """
                j1 = S<=>P
                j2 = S (e.g A-->B)
            """
            pass
            # derived_sentence = NALInferenceRules.Conditional.ConditionalAnalogy(j2, j1)  # P
            # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
        else:
            """
                j1 = S==>P
                j2 = S or P (e.g A-->B)
            """
            if j2.statement == j1.statement.get_subject_term():
                """
                    j2 = S
                """
                # derived_sentence = NALInferenceRules.Conditional.ConditionalDeduction(j1, j2)  # P
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
                pass
            elif j2.statement == j1.statement.get_predicate_term():
                """
                    j2 = P
                """
                # j2 = P. or (E ==> P)
                pass
                # derived_sentence = NALInferenceRules.Conditional.ConditionalJudgmentAbduction(j1, j2)  # S.
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
            elif NALSyntax.TermConnector.is_conjunction(
                    j1.statement.get_subject_term().connector) and not NALSyntax.Copula.is_symmetric(
                    j1.statement.get_copula()):
                """
                    j1 = (C1 && C2 && ..CN && S) ==> P
                    j2 = S
                """
                pass
                # derived_sentence = NALInferenceRules.Conditional.ConditionalConjunctionalDeduction(j1,j2)  # (C1 && C2 && ..CN) ==> P
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)

    elif (isinstance(j1.statement, NALGrammar.Terms.CompoundTerm) and
          isinstance(j2.statement, NALGrammar.Terms.StatementTerm) and
          NALSyntax.TermConnector.is_conjunction(j1.statement.connector)) \
            or (isinstance(j2.statement, NALGrammar.Terms.CompoundTerm) and
                isinstance(j1.statement, NALGrammar.Terms.StatementTerm) and
                NALSyntax.TermConnector.is_conjunction(j2.statement.connector)):
        """
                j1 = (A &/ B)
                j2 = A
            OR
                j1 = A
                j2 = (A &/ B)
        """
        if isinstance(j2.statement, NALGrammar.Terms.CompoundTerm):
            """
                j1 = A
                j2 = (A &/ B)
            """
            # swap sentences so j1 is the compound
            j1, j2 = j2, j1
            swapped = True

        """
            j1 = (A &/ B)
            j2 = A
        """
        pass

    if swapped:
        # restore sentences
        j1, j2 = j2, j1
        swapped = False
    """
    ===============================================
    ===============================================
        Post-Processing
    ===============================================
    ===============================================
    """
    # mark sentences as interacted with each other
    # j1.mutually_add_to_interacted_sentences(j2)

    if Config.DEBUG: Global.Global.debug_print("Derived " + str(len(all_derived_sentences)) + " inference results.")

    return all_derived_sentences


def do_semantic_inference_goal_judgment(j1: NALGrammar.Sentences, j2: NALGrammar.Sentences) -> [
    NARSDataStructures.Other.Task]:
    """
        Derives a new task by performing the appropriate inference rules on the given semantically related sentences.
        The resultant sentence's evidential base is merged from its parents.

        :param j1: Sentence (Goal)
        :param j2: Semantically related belief (Judgment)

        :assume j1 and j2 have distinct evidential bases B1 and B2: B1 ⋂ B2 = Ø
                (no evidential overlap)

        :returns An array of the derived Tasks, or an empty array if the inputs have evidential overlap
    """
    Asserts.assert_sentence(j1)
    Asserts.assert_sentence(j2)

    if Config.DEBUG: Global.Global.debug_print(
        "Trying inference between: " + j1.get_formatted_string() + " and " + j2.get_formatted_string())

    """
    ===============================================
    ===============================================
        Pre-Processing
    ===============================================
    ===============================================
    """

    if j1.value.confidence == 0 or j2.value.confidence == 0:
        if Config.DEBUG: Global.Global.debug_print("Can't do inference between negative premises")
        return []  # can't do inference with 2 entirely negative premises

    all_derived_sentences = []

    j1_statement = j1.statement  # goal statement
    j2_statement = j2.statement

    if not NALSyntax.Copula.is_first_order(j2_statement.get_copula()):
        if not NALSyntax.Copula.is_symmetric(j2_statement.get_copula()):
            if j2_statement.get_predicate_term() == j1_statement:
                # j1 = P!, j2 = S=>P!
                derived_sentence = NALInferenceRules.Conditional.ConditionalGoalDeduction(j1, j2)  #:- S! i.e. (P ==> D)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
            elif j2_statement.get_subject_term() == j1_statement:
                # j1 = S!, j2 = (S=>P).
                derived_sentence = NALInferenceRules.Conditional.ConditionalGoalInduction(j1, j2)  #:- P! i.e. (P ==> D)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
    elif NALSyntax.Copula.is_first_order(j2_statement.get_copula()):
        if NALSyntax.TermConnector.is_conjunction(j1_statement.connector):
            # j1 = (C &/ S)!, j2 = C. )
            derived_sentence = NALInferenceRules.Conditional.SimplifyConjunctiveGoal(j1, j2)  # S!
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        elif j1_statement.connector == NALSyntax.TermConnector.Negation:
            # j1 = (--,G)!, j2 = C. )
            if NALSyntax.TermConnector.is_conjunction(j1_statement.subterms[0].connector):
                # j1 = (--,(A &/ B))!, j2 = A. )
                derived_sentence = NALInferenceRules.Conditional.SimplifyNegatedConjunctiveGoal(j1, j2)  # B!
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

    else:
        assert False, "ERROR"

    """
    ===============================================
    ===============================================
        Post-Processing
    ===============================================
    ===============================================
    """

    if Config.DEBUG: Global.Global.debug_print("Derived " + str(len(all_derived_sentences)) + " inference results.")

    return all_derived_sentences


def do_temporal_inference_two_premise(A: NALGrammar.Sentences, B: NALGrammar.Sentences) -> [
    NARSDataStructures.Other.Task]:
    derived_sentences = []

    derived_sentence = NALInferenceRules.Temporal.TemporalIntersection(A, B)  # A &/ B or  A &/ B or B &/ A
    add_to_derived_sentences(derived_sentence, derived_sentences, A, B)

    derived_sentence = NALInferenceRules.Temporal.TemporalInduction(A, B)  # A =|> B or A =/> B or B =/> A
    add_to_derived_sentences(derived_sentence, derived_sentences, A, B)

    """
    ===============================================
    ===============================================
        Post-Processing
    ===============================================
    ===============================================
    """

    return derived_sentences


def do_inference_one_premise(j):
    """
        Immediate Inference Rules
        Generates beliefs that are equivalent to j but in a different form.

        :param j: Sentence

        :returns An array of the derived Tasks
    """

    derived_sentences = []
    if j.statement.is_first_order(): return derived_sentences  # only higher order
    if j.statement.connector is not None or j.stamp.from_one_premise_inference: return derived_sentences  # connectors are too complicated
    if j.statement.get_subject_term().connector == NALSyntax.TermConnector.Negation \
            or j.statement.get_predicate_term().connector == NALSyntax.TermConnector.Negation:
        return derived_sentences

    if isinstance(j, NALGrammar.Sentences.Judgment):
        # Negation (--,(S-->P))
        # derived_sentence = NALInferenceRules.Immediate.Negation(j)
        # add_to_derived_sentences(derived_sentence,derived_sentences,j)

        # Conversion (P --> S) or (P ==> S)
        # if not j.stamp.from_one_premise_inference \
        #         and not NALSyntax.Copula.is_symmetric(j.statement.get_copula()) \
        #         and j.value.frequency > 0:
        #     derived_sentence = NALInferenceRules.Immediate.Conversion(j)
        #     add_to_derived_sentences(derived_sentence,derived_sentences,j)

        # Contraposition  ((--,P) ==> (--,S))
        if NALSyntax.Copula.is_implication(j.statement.get_copula()) and \
                isinstance(j.statement.get_subject_term(),
                           NALGrammar.Terms.CompoundTerm) and NALSyntax.TermConnector.is_conjunction(
            j.statement.get_subject_term().connector):
            contrapositive = NALInferenceRules.Immediate.Contraposition(j)
            add_to_derived_sentences(contrapositive, derived_sentences, j)

            # contrapositive_with_conversion = NALInferenceRules.Immediate.Conversion(contrapositive)
            # add_to_derived_sentences(contrapositive_with_conversion, derived_sentences, j)

        # Image
        # if isinstance(j.statement.get_subject_term(), NALGrammar.Terms.CompoundTerm) \
        #     and j.statement.get_subject_term().connector == NALSyntax.TermConnector.Product\
        #         and j.statement.get_copula() == NALSyntax.Copula.Inheritance:
        #     derived_sentence_list = NALInferenceRules.Immediate.ExtensionalImage(j)
        #     for derived_sentence in derived_sentence_list:
        #         add_to_derived_sentences(derived_sentence,derived_sentences,j)
        # elif isinstance(j.statement.get_predicate_term(), NALGrammar.Terms.CompoundTerm) \
        #     and j.statement.get_predicate_term().connector == NALSyntax.TermConnector.Product:
        #     derived_sentence_list = NALInferenceRules.Immediate.IntensionalImage(j)
        #     for derived_sentence in derived_sentence_list:
        #         add_to_derived_sentences(derived_sentence,derived_sentences,j)

    return derived_sentences


def add_to_derived_sentences(derived_sentence, derived_sentence_array, j1, j2=None):
    """
        Add derived sentence to array if it meets certain conditions
    :param derived_sentence:
    :param derived_sentence_array:
    :return:
    """
    if derived_sentence is None: return  # inference result was not useful
    if not isinstance(derived_sentence,
                      NALGrammar.Sentences.Question) and derived_sentence.value.confidence == 0.0: return  # zero confidence is useless
    derived_sentence_array.append(derived_sentence)