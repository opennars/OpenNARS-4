"""
    Author: Christian Hahm
    Created: March 8, 2021
    Purpose: Given premises, performs proper inference and returns the resultant sentences as Tasks.
"""
from opennars import NAL
from opennars.NAL import Inference
from opennars.NARS.DataStructures import Concept, TermLink
from opennars.Narsese import Task, Sentence, Question, Compound, Statement, Goal, Judgement, Copula, Connector, Budget


def do_semantic_inference_two_premise(j1, j2):
    #if not NALGrammar.Sentences.may_interact(j1, j2): return []

    try:
        if isinstance(j1, Goal) and isinstance(j2, Judgement):
            results = do_semantic_inference_goal_judgment(j1, j2)
        else:
            results = do_semantic_inference_two_judgment(j1, j2)
    except Exception as error:
        assert False, "ERROR: Inference error " + str(error) + " between " + str(j1) + " and " + str(j2)

    return results


def do_semantic_inference_two_judgment(j1_task: Task, j2: Sentence,
                                       budget_tasklink: Budget = None, budget_termlink: Budget = None) -> [Task]:
    """
        Derives a new task by performing the appropriate inference rules on the given semantically related sentences.
        The resultant sentence's evidential base is merged from its parents.

        :param j1: Sentence (Question or Judgment)
        :param j2: Semantically related belief (Judgment)

        :assume j1 and j2 have distinct evidential bases B1 and B2: B1 ⋂ B2 = Ø
                (no evidential overlap)

        :returns An array of the derived Tasks, or an empty array if the inputs have evidential overlap
    """

    j1: Sentence = j1_task.sentence

    budget_args = [budget_tasklink, budget_termlink]

    """
    ===============================================
    ===============================================
        Pre-Processing
    ===============================================
    ===============================================
    """

    if j1.truth.c == 0 or j2.truth.c == 0:
        return []  # can't do inference with 0 confidence

    all_derived_sentences = []

    j1_statement = j1.term
    j2_statement = j2.term

    # same statement
    if j1_statement == j2_statement:
        assert False,"Error: use Revision function"

    if j1.truth.f == 0 or j2.truth.f == 0:
        return []  # can't do inference with a negative premise

    """
    ===============================================
    ===============================================
        First-order and Higher-Order Syllogistic Rules
    ===============================================
    ===============================================
    """
    if isinstance(j1.term, Compound):
        if isinstance(j2.term, Statement) \
                and not j2.term.copula.is_first_order():
            if j2.term.copula == Copula.Implication \
                    or j2.term.copula == Copula.PredictiveImplication:
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalJudgmentDeduction(j2, j1)  # S-->P
                # #if j2.term.copula == Copula.PredictiveImplication: derived_sentence.stamp.occurrence_time = Global.Global.get_current_cycle_number()
                # add_to_derived_sentences(derived_sentence, all_derived_sentences, j2, j1)
                return all_derived_sentences

    if isinstance(j2.term, Compound):
        if isinstance(j1.term, Statement) \
                and not j1.term.copula.is_first_order():
            if j1.term.copula == Copula.Implication \
                    or j1.term.copula == Copula.PredictiveImplication:
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalJudgmentDeduction(j1, j2)  # S-->P
                # #if j1.term.copula == Copula.PredictiveImplication: derived_sentence.stamp.occurrence_time = Global.Global.get_current_cycle_number()
                # add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                return all_derived_sentences

    swapped = False

    if isinstance(j1.term, Statement) and isinstance(j2.term,Statement) and \
            j1.term.copula.is_first_order() == j2.term.copula.is_first_order():
        """
            Both sentences are first-order or higher-order
        """
        j1_subject_term = j1.term.subject
        j2_subject_term = j2.term.subject
        j1_predicate_term = j1.term.predicate
        j2_predicate_term = j2.term.predicate
        j1_copula = j1.term.copula
        j2_copula = j2.term.copula

        # check if the result will lead to tautology
        tautology = (j1_subject_term == j2_predicate_term and j1_predicate_term == j2_subject_term) or \
                    (j1_subject_term == j2_subject_term and j1_predicate_term == j2_predicate_term
                     and
                     ((not j1_copula.is_symmetric() and j2_copula.is_symmetric())  # S-->P and P<->S
                      or
                      (j1_copula.is_symmetric() and not j2_copula.is_symmetric())))  # S<->P and S-->P

        if tautology:
            return all_derived_sentences  # can't do inference, it will result in tautology

        if j1.term.copula.is_temporal or (isinstance(j1, Judgement) and j1.is_event) or (isinstance(j2, Judgement) and j2.is_event):
            # dont do semantic inference with temporal
            # todo .. don't do inference with events, it isn't handled gracefully right now
            return all_derived_sentences
        elif not j1.term.copula.is_symmetric() and not j2.term.copula.is_symmetric():
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

                """
                # Deduction
                """

                derived_sentence = Inference.SyllogisticRules.deduction(j1, j2, *budget_args)  # S-->P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Exemplification
                """
                derived_sentence = Inference.SyllogisticRules.exemplification(j2, j1, *budget_args)  # P-->S
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

            elif j1.term.subject == j2.term.subject:
                """
                    j1=M-->P
                    j2=M-->S
                """
            
                """
                # Induction
                """
                derived_sentence = Inference.SyllogisticRules.induction(j1, j2, *budget_args)  # S-->P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Induction
                """
                derived_sentence = Inference.SyllogisticRules.induction(j2, j1, *budget_args)  # P-->S
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Comparison
                """
                derived_sentence = Inference.SyllogisticRules.comparison(j1, j2, *budget_args)  # S<->P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Intensional Intersection or Disjunction
                """
                derived_sentence = Inference.CompositionalRules.intersection_extension(j1,j2, *budget_args)  # M --> (S | P)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Extensional Intersection or Conjunction
                """
                derived_sentence = Inference.CompositionalRules.intersection_extension(j1,j2, *budget_args)  # M --> (S & P)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Extensional Difference
                """
                derived_sentence = Inference.CompositionalRules.difference_extension(j1, j2, *budget_args)  # M --> (S - P)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Extensional Difference
                """
                derived_sentence = Inference.CompositionalRules.difference_extension(j2, j1, *budget_args)  # M --> (P - S)
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
            elif j1.term.predicate == j2.term.predicate:
                """
                    j1 = P-->M
                    j2 = S-->M
                """

                """
                # Abduction
                """
                derived_sentence = Inference.SyllogisticRules.abduction(j1, j2, *budget_args)  # S-->P or S==>P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Abduction
                """
                derived_sentence = Inference.SyllogisticRules.abduction(j2, j1, *budget_args)  # P-->S or P==>S
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                if not j1_copula.is_first_order():
                    # two implication statements
                    if j1_subject_term.connector.is_conjunction() or \
                            j2_subject_term.connector.is_conjunction():
                        j1_subject_statement_terms = j1_subject_term.subterms if j1_subject_term.connector.is_conjunction() else [j1_subject_term]

                        j2_subject_statement_terms = j2_subject_term.subterms if j2_subject_term.connector.is_conjunction() else [j2_subject_term]

                        difference_of_subterms = list(
                            set(j1_subject_statement_terms) - set(j2_subject_statement_terms)) + list(
                            set(j2_subject_statement_terms) - set(j1_subject_statement_terms))

                        if len(difference_of_subterms) == 1:
                            """
                               At least one of the statement's subjects is conjunctive and differs from the
                               other statement's subject by 1 term
                            """
                            if len(j1_subject_statement_terms) > len(j2_subject_statement_terms):
                                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalConjunctionalAbduction(j1,j2)  # S
                                pass
                            else:
                                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalConjunctionalAbduction(j2,j1)  # S
                                pass
                            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Intensional Intersection Disjunction
                """
                derived_sentence = Inference.CompositionalRules.intersection_intension(j1,j2,*budget_args)  # (P | S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Extensional Intersection Conjunction
                """
                derived_sentence = Inference.CompositionalRules.intersection_extension(j1,j2,*budget_args)  # (P & S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Intensional Difference
                """
                derived_sentence = Inference.CompositionalRules.difference_intension(j1, j2,*budget_args)  # (P ~ S) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)

                """
                # Swapped Intensional Difference
                """
                derived_sentence = Inference.CompositionalRules.difference_intension(j2, j1,*budget_args)  # (S ~ P) --> M
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                """
                # Comparison
                """
                derived_sentence = Inference.SyllogisticRules.comparison(j1, j2,*budget_args)  # S<->P or S<=>P
                add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
        elif not j1.term.copula.is_symmetric() and j2.term.copula.is_symmetric():
            """
            # j1 = M-->P or P-->M
            # j2 = S<->M or M<->S
            # Analogy
            """
            derived_sentence = Inference.SyllogisticRules.analogy(j1, j2,*budget_args)  # S-->P or P-->S
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2,)
        elif j1.term.copula.is_symmetric() and not j2.term.copula.is_symmetric():
            """
            # j1 = M<->S or S<->M
            # j2 = P-->M or M-->P
            # Swapped Analogy
            """
            derived_sentence = Inference.SyllogisticRules.analogy(j2, j1,*budget_args)  # S-->P or P-->S
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2,)
        elif j1.term.copula.is_symmetric() and j2.term.copula.is_symmetric():
            """
            # j1 = M<->P or P<->M
            # j2 = S<->M or M<->S
            # Resemblance
            """
            derived_sentence = Inference.SyllogisticRules.resemblance(j1, j2)  # S<->P
            add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
    elif (isinstance(j1.term, Statement) and not j1.term.copula.is_first_order()) \
            or (isinstance(j2.term, Statement) and not j2.term.copula.is_first_order()):
        # One premise is a higher-order statement
        """
                j1 = S==>P or S<=>P
                j2 = A-->B or A<->B
            OR
                j1 = A-->B or A<->B
                j2 = S==>P or S<=>P
        """
        if isinstance(j2.term, Statement) and not j2.term.copula.is_first_order():
            """
                j1 = A-->B or A<->B 
                j2 = S==>P or S<=>P
            """
            # swap sentences so j1 is higher order
            j1, j2 = j2, j1
            swapped = True

        assert (isinstance(j1.term, Statement) and not j1.term.is_first_order()), "ERROR"

        """
            j1 = S==>P or S<=>P
        """
        if j1.term.copula.is_symmetric() and (j2.term == j1.term.subject or j2.term == j1.term.predicate):
            """
                j1 = S<=>P
                j2 = S (e.g A-->B)
            """
            pass
            # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalAnalogy(j2, j1)  # P
            # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
        else:
            """
                j1 = S==>P
                j2 = S or P (e.g A-->B)
            """
            if j2.term == j1.term.subject:
                """
                    j2 = S
                """
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalDeduction(j1, j2)  # P
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
                pass
            elif j2.term == j1.term.predicate:
                """
                    j2 = P
                """
                # j2 = P. or (E ==> P)
                pass
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalJudgmentAbduction(j1, j2)  # S.
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)
            elif j1.term.subject.connector.is_conjunction() and not j1.term.copula.is_symmetric():
                """
                    j1 = (C1 && C2 && ..CN && S) ==> P
                    j2 = S
                """
                pass
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalConjunctionalDeduction(j1,j2)  # (C1 && C2 && ..CN) ==> P
                # add_to_derived_sentences(derived_sentence,all_derived_sentences,j1,j2)

    elif (isinstance(j1.term, Compound) and
          isinstance(j2.term, Statement) and
          j1.term.connector.is_conjunction()) \
            or (isinstance(j2.term, Compound) and
                isinstance(j1.term, Statement) and
                j2.term.connector.is_conjunction()):
        """
                j1 = (A &/ B)
                j2 = A
            OR
                j1 = A
                j2 = (A &/ B)
        """
        if isinstance(j2.term, Compound):
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


    return all_derived_sentences

def Revision(j1_task: Task, j2: Sentence, budget_tasklink: Budget = None, budget_termlink: Budget = None) -> Task:
    """
            # Revision
            # j1 = j2
            """
    j1: Sentence = j1_task.sentence
    assert not (isinstance(j1, Question) or isinstance(j2, Question)),"Can't do revision with Questions, they don't have a truth value"

    derived_sentence = Inference.LocalRules.revision(j1_task, j2, budget_tasklink, budget_termlink)  # S-->P
    return derived_sentence

def do_semantic_inference_goal_judgment(j1: Sentence, j2: Sentence) -> [
    Task]:
    """
        Derives a new task by performing the appropriate inference rules on the given semantically related sentences.
        The resultant sentence's evidential base is merged from its parents.

        :param j1: Sentence (Goal)
        :param j2: Semantically related belief (Judgment)

        :assume j1 and j2 have distinct evidential bases B1 and B2: B1 ⋂ B2 = Ø
                (no evidential overlap)

        :returns An array of the derived Tasks, or an empty array if the inputs have evidential overlap
    """

    """
    ===============================================
    ===============================================
        Pre-Processing
    ===============================================
    ===============================================
    """

    if j1.truth.c == 0 or j2.truth.c == 0:
        return []  # can't do inference with 2 entirely negative premises

    all_derived_sentences = []

    j1_statement = j1.term  # goal statement
    j2_statement = j2.term

    if not j2_statement.copula.is_first_order():
        if not j2_statement.copula.is_symmetric():
            if j2_statement.predicate == j1_statement:
                # j1 = P!, j2 = S=>P!
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalGoalDeduction(j1, j2)  #:- S! i.e. (P ==> D)
                # add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                pass
            elif j2_statement.subject == j1_statement:
                # j1 = S!, j2 = (S=>P).
                # derived_sentence = Inference.ConditionalSyllogisticRules.ConditionalGoalInduction(j1, j2)  #:- P! i.e. (P ==> D)
                # add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                pass
    elif j2_statement.copula.is_first_order():
        if j1_statement.connector.is_conjunction():
            # j1 = (C &/ S)!, j2 = C. )
            # derived_sentence = Inference.ConditionalSyllogisticRules.SimplifyConjunctiveGoal(j1, j2)  # S!
            # add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
            pass

        elif j1_statement.connector == Connector.Negation:
            # j1 = (--,G)!, j2 = C. )
            if j1_statement.subterms[0].connector.is_conjunction():
                # j1 = (--,(A &/ B))!, j2 = A. )
                # derived_sentence = Inference.ConditionalSyllogisticRules.SimplifyNegatedConjunctiveGoal(j1, j2)  # B!
                # add_to_derived_sentences(derived_sentence, all_derived_sentences, j1, j2)
                pass

    else:
        assert False, "ERROR"

    """
    ===============================================
    ===============================================
        Post-Processing
    ===============================================
    ===============================================
    """

    return all_derived_sentences


def do_temporal_inference_two_premise(A: Sentence, B: Sentence) -> [Task]:
    derived_sentences = []

    # derived_sentence = Inference.TemporalRules.TemporalIntersection(A, B)  # A &/ B or  A &/ B or B &/ A
    # add_to_derived_sentences(derived_sentence, derived_sentences, A, B)
    #
    # derived_sentence = Inference.TemporalRules.TemporalInduction(A, B)  # A =|> B or A =/> B or B =/> A
    # add_to_derived_sentences(derived_sentence, derived_sentences, A, B)

    """
    ===============================================
    ===============================================
        Post-Processing
    ===============================================
    ===============================================
    """

    return derived_sentences


def do_inference_one_premise(j_task: Task):
    """
        Immediate Inference Rules
        Generates beliefs that are equivalent to j but in a different form.

        :param j: Sentence

        :returns An array of the derived Tasks
    """
    j: Sentence = j_task.sentence

    derived_sentences = []
    if j.term.is_first_order(): return derived_sentences  # only higher order
    if j.term.connector is not None or j.stamp.from_one_premise_inference: return derived_sentences  # connectors are too complicated
    if j.term.subject.connector == Connector.Negation \
            or j.term.predicate.connector == Connector.Negation:
        return derived_sentences

    if isinstance(j, Judgement):
        # Negation (--,(S-->P))
        # derived_sentence = Inference.ImmediateRules.Negation(j)
        # add_to_derived_sentences(derived_sentence,derived_sentences,j)

        # Conversion (P --> S) or (P ==> S)
        # if not j.stamp.from_one_premise_inference \
        #         and not sym(j.term.copula) \
        #         and j.truth.f > 0:
        #     derived_sentence = Inference.ImmediateRules.Conversion(j)
        #     add_to_derived_sentences(derived_sentence,derived_sentences,j)

        # Contraposition  ((--,P) ==> (--,S))
        if j.term.copula.is_implication() and \
                isinstance(j.term.subject,
                           Compound) and j.term.subject.connector.is_conjunction():
            contrapositive = Inference.ImmediateRules.contraposition(j)
            add_to_derived_sentences(contrapositive, derived_sentences, j)

            # contrapositive_with_conversion = Inference.ImmediateRules.Conversion(contrapositive)
            # add_to_derived_sentences(contrapositive_with_conversion, derived_sentences, j)

        # Image
        # if isinstance(j.term.subject, Compound) \
        #     and j.term.subject.connector == NALSyntax.TermConnector.Product\
        #         and j.term.copula == Copula.Inheritance:
        #     derived_sentence_list = Inference.ImmediateRules.ExtensionalImage(j)
        #     for derived_sentence in derived_sentence_list:
        #         add_to_derived_sentences(derived_sentence,derived_sentences,j)
        # elif isinstance(j.term.predicate, Compound) \
        #     and j.term.predicate.connector == NALSyntax.TermConnector.Product:
        #     derived_sentence_list = Inference.ImmediateRules.IntensionalImage(j)
        #     for derived_sentence in derived_sentence_list:
        #         add_to_derived_sentences(derived_sentence,derived_sentences,j)

    return derived_sentences


def add_to_derived_sentences(derived_sentence: Sentence, derived_sentence_array, j1, j2=None):
    """
        Add derived sentence to array if it meets certain conditions
    :param derived_sentence:
    :param derived_sentence_array:
    :return:
    """
    if derived_sentence is None: return  # no inference result
    if not isinstance(derived_sentence, Question) and derived_sentence.truth.c == 0.0: return  # zero confidence is useless
    derived_sentence_array.append(derived_sentence)
