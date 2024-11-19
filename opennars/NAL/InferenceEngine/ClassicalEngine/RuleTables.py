
"""
Reference:
RuleTables.java in OpenNARS 1.5.6
It is transated into python.
@author: Bowen Xu
@date: Nov 12, 2024
"""

from opennars.Narsese import Task, Sentence, Term, Copula, LinkType, Statement, Term, Compound, VarPrefix, Budget
from . import VariableTools
from . import CompositionalRules, SyllogisticRules
from copy import copy, deepcopy
#Entry point of the inference engine
#     *
#     tLink The selected TaskLink, which will provide a task
#     bLink The selected TermLink, which may provide a belief
#     memory Reference to the memory
#     */
def reason(task: Task, belief_term: Term, belief: Sentence|None, tlink_type: LinkType, blink_type: LinkType, tlink_indices: tuple[int, int], blink_indices: tuple[int, int]):
    '''
    Args:
        tlink_indices: A tuple of the level 0 index and the level 1 index of the TaskLink
        blink_indices: A tuple of the level 0 index and the level 1 index of the TermLink
    '''
    taskSentence: Sentence = task.sentence
    taskTerm: Term  = deepcopy(taskSentence.term)       # cloning for substitution
    beliefTerm: Term = deepcopy(belief_term)            # cloning for substitution

    if(taskTerm.is_statement and (taskTerm.copula is Copula.Implication) and taskSentence.is_judgement):
        n: float = taskTerm.complexity  # don't let this rule apply every time, make it dependent on complexity
        w: float = 1.0/((n*(n-1))/2.0)  # let's assume hierachical tuple (triangle numbers) amount for this
        # if(CompositionalRules.rand.nextDouble()<w) { //so that NARS memory will not be spammed with contrapositions
        #     StructuralRules.contraposition((Statement) taskTerm, taskSentence, memory); //before it was the linkage which did that
        # } //now we some sort "emulate" it.

#     if(CompoundTerm.EqualSubTermsInRespectToImageAndProduct(taskTerm,beliefTerm)) {
#         return;
#     }

#     Concept beliefConcept = memory.termToConcept(beliefTerm);
#     Sentence belief = null;
#     if (beliefConcept != null) {
#         belief = beliefConcept.getBelief(task);
#     }
#     memory.currentBelief = belief;  // may be null
#     if (belief != null) {
#         LocalRules.match(task, belief, memory);
#     }
#     Sentence buf1=memory.currentBelief;
#     Task buf2=memory.currentTask;
#     CompositionalRules.dedSecondLayerVariableUnification(task,memory);
#     memory.currentBelief=buf1;
#     memory.currentTask=buf2;
#     if (!memory.noResult() && task.getSentence().isJudgment()) {
#         return;
#     }
#     /*if(CompositionalRules.dedProductByQuestion(task,memory)) {
#         return;
#     }*/
#     CompositionalRules.dedConjunctionByQuestion(taskSentence, belief, memory);
    tIndex = tlink_indices[0]
    bIndex = blink_indices[0]
    match tlink_type:  # dispatch first by TaskLink type
        case LinkType.SELF:
            match (blink_type): 
                case LinkType.COMPONENT:
#                     compoundAndSelf((CompoundTerm) taskTerm, beliefTerm, true, memory);
#                     break;
#                 case TermLink.COMPOUND:
#                     compoundAndSelf((CompoundTerm) beliefTerm, taskTerm, false, memory);
#                     break;
#                 case TermLink.COMPONENT_STATEMENT:
#                     if (belief != null) {
#                         SyllogisticRules.detachment(task.getSentence(), belief, bIndex, memory);
#                     }
#                     break;
#                 case TermLink.COMPOUND_STATEMENT:
#                     if (belief != null) {
#                         SyllogisticRules.detachment(belief, task.getSentence(), bIndex, memory);
#                     }
#                     break;
#                 case TermLink.COMPONENT_CONDITION:
#                     if (belief != null) {
#                         bIndex = bLink.getIndex(1);
#                         SyllogisticRules.conditionalDedInd((Implication) taskTerm, bIndex, beliefTerm, tIndex, memory);
#                     }
#                     break;
#                 case TermLink.COMPOUND_CONDITION:
#                     if (belief != null) {
#                         bIndex = bLink.getIndex(1);
#                         SyllogisticRules.conditionalDedInd((Implication) beliefTerm, bIndex, taskTerm, tIndex, memory);
#                     }
#                     break;
                    pass
            pass
        case LinkType.COMPOUND:
            match blink_type:
                case LinkType.COMPOUND:
#                     compoundAndCompound((CompoundTerm) taskTerm, (CompoundTerm) beliefTerm, memory);
#                     break;
#                 case TermLink.COMPOUND_STATEMENT:
#                     compoundAndStatement((CompoundTerm) taskTerm, tIndex, (Statement) beliefTerm, bIndex, beliefTerm, memory);
#                     break;
#                 case TermLink.COMPOUND_CONDITION:
#                     if (belief != null) {
#                         if (beliefTerm instanceof Implication) {
#                             if (Variable.unify(Symbols.VAR_INDEPENDENT, ((Implication) beliefTerm).getSubject(), taskTerm, beliefTerm, taskTerm)) {
#                                 detachmentWithVar(belief, taskSentence, bIndex, memory);
#                             } else {
#                                 SyllogisticRules.conditionalDedInd((Implication) beliefTerm, bIndex, taskTerm, -1, memory);
#                             }
#                         } else if (beliefTerm instanceof Equivalence) {
#                             SyllogisticRules.conditionalAna((Equivalence) beliefTerm, bIndex, taskTerm, -1, memory);
#                         }
#                     }
#                     break;
                    pass
#             }
#             break;
            pass
        case LinkType.COMPOUND_STATEMENT:
            match blink_type:
                case LinkType.COMPONENT:
#                     componentAndStatement((CompoundTerm) memory.currentTerm, bIndex, (Statement) taskTerm, tIndex, memory);
#                     break;
                    pass
                case LinkType.COMPOUND:
#                     compoundAndStatement((CompoundTerm) beliefTerm, bIndex, (Statement) taskTerm, tIndex, beliefTerm, memory);
#                     break;
                    pass
                case LinkType.COMPOUND_STATEMENT:
                    if belief is not None:
                        pass # TODO: CONTINUE HERE
                        # syllogisms(tLink, bLink, taskTerm, beliefTerm, memory);
                    pass
                case LinkType.COMPOUND_CONDITION:
#                     if (belief != null) {
#                         bIndex = bLink.getIndex(1);
#                         if (beliefTerm instanceof Implication) {
#                             conditionalDedIndWithVar((Implication) beliefTerm, bIndex, (Statement) taskTerm, tIndex, memory);
#                         }
#                     }
#                     break;
                    pass
            pass
        case LinkType.COMPOUND_CONDITION:
            match blink_type:
                case LinkType.COMPOUND:
#                     if (belief != null) {
#                         detachmentWithVar(taskSentence, belief, tIndex, memory);
#                     }
#                     break;
                    pass
                case LinkType.COMPOUND_STATEMENT:
#                     if (belief != null) {
#                         if (taskTerm instanceof Implication) // TODO maybe put instanceof test within conditionalDedIndWithVar()
#                         {
#                             Term subj = ((Implication) taskTerm).getSubject();
#                             if (subj instanceof Negation) {
#                                 if (task.getSentence().isJudgment()) {
#                                     componentAndStatement((CompoundTerm) subj, bIndex, (Statement) taskTerm, tIndex, memory);
#                                 } else {
#                                     componentAndStatement((CompoundTerm) subj, tIndex, (Statement) beliefTerm, bIndex, memory);
#                                 }
#                             } else {
#                                 conditionalDedIndWithVar((Implication) taskTerm, tIndex, (Statement) beliefTerm, bIndex, memory);
#                             }
#                         }
#                         break;
#                     }
#                     break;
                    pass
            pass
#     }
# }




''' ----- syllogistic inferences ----- '''
def syllogisms(task: Task, belief_term: Term, belief: Sentence|None, tlink_type: LinkType, blink_type: LinkType, tlink_indices: tuple[int, int], blink_indices: tuple[int, int]):
    '''
    Meta-table of syllogistic rules, indexed by the content classes of the taskSentence and the belief
    Args:
        [to be added]
        tlink_indices: A tuple of the level 0 index and the level 1 index of the TaskLink
        blink_indices: A tuple of the level 0 index and the level 1 index of the TermLink
    '''

    taskSentence = task.sentence
    taskTerm = task.term
    
    figure: int
    if taskTerm.is_statement and taskTerm.copula is Copula.Inheritance:
        if belief_term.is_statement and belief_term.copula is Copula.Inheritance:
            figure = indexToFigure(tlink_indices, blink_indices)
        #     asymmetricAsymmetric(taskSentence, belief, figure, memory);
        # } else if (beliefTerm instanceof Similarity) {
        #     figure = indexToFigure(tLink, bLink);
        #     asymmetricSymmetric(taskSentence, belief, figure, memory);
        # } else {
        #     detachmentWithVar(belief, taskSentence, bLink.getIndex(0), memory);
        # }
#     } else if (taskTerm instanceof Similarity) {
#         if (beliefTerm instanceof Inheritance) {
#             figure = indexToFigure(bLink, tLink);
#             asymmetricSymmetric(belief, taskSentence, figure, memory);
#         } else if (beliefTerm instanceof Similarity) {
#             figure = indexToFigure(bLink, tLink);
#             symmetricSymmetric(belief, taskSentence, figure, memory);
#         }
#     } else if (taskTerm instanceof Implication) {
#         if (beliefTerm instanceof Implication) {
#             figure = indexToFigure(tLink, bLink);
#             asymmetricAsymmetric(taskSentence, belief, figure, memory);
#         } else if (beliefTerm instanceof Equivalence) {
#             figure = indexToFigure(tLink, bLink);
#             asymmetricSymmetric(taskSentence, belief, figure, memory);
#         } else if (beliefTerm instanceof Inheritance) {
#             detachmentWithVar(taskSentence, belief, tLink.getIndex(0), memory);
#         }
#     } else if (taskTerm instanceof Equivalence) {
#         if (beliefTerm instanceof Implication) {
#             figure = indexToFigure(bLink, tLink);
#             asymmetricSymmetric(belief, taskSentence, figure, memory);
#         } else if (beliefTerm instanceof Equivalence) {
#             figure = indexToFigure(bLink, tLink);
#             symmetricSymmetric(belief, taskSentence, figure, memory);
#         } else if (beliefTerm instanceof Inheritance) {
#             detachmentWithVar(taskSentence, belief, tLink.getIndex(0), memory);
#         }
#     }
# }


def indexToFigure(link1_indices: tuple[int, int], link2_indices: tuple[int, int]) -> int:
    '''
    Decide the figure of syllogism according to the locations of the common
    term in the premises
    Args:
        link1_indices: The indices of the link to the first premise
        link2: The indices of the link to the second premise
    @return The figure of the syllogism, one of the four: 11, 12, 21, or 22
    '''
    return (link1_indices[0] + 1) * 10 + (link2_indices[0] + 1)

def asymmetricAsymmetric(task: Task, belief: Sentence, figure: int, budget_tasklink: Budget, budget_termlink: Budget=None):
    '''
    Syllogistic rules whose both premises are on the same asymmetric relation
    Args:
        task: The current task
        sentence: The taskSentence in the task
        belief: The judgment in the belief
        figure: The location of the shared term

    '''
    sentence: Sentence = task.sentence
    s1: Statement = deepcopy(sentence.term)
    s2: Statement = deepcopy(belief.term)
    t1: Term
    t2: Term
    match (figure):
        case 11:    # induction
            if (VariableTools.unify(VarPrefix.Independent, s1.subject, s2.subject, s1, s2))
                if s1 == s2:
                    return

                t1 = s2.predicate
                t2 = s1.predicate
                CompositionalRules.composeCompound(task, belief, s1, s2, 0, budget_tasklink, budget_termlink)
                SyllogisticRules.abdIndCom(task, belief, t1, t2, figure, budget_tasklink, budget_termlink)
                # CompositionalRules.EliminateVariableOfConditionAbductive(figure,sentence,belief,memory);

#             break;
#         case 12:    // deduction
#             if (Variable.unify(Symbols.VAR_INDEPENDENT, s1.getSubject(), s2.getPredicate(), s1, s2)) {
#                 if (s1.equals(s2)) {
#                     return;
#                 }
#                 t1 = s2.getSubject();
#                 t2 = s1.getPredicate();
#                 if (Variable.unify(Symbols.VAR_QUERY, t1, t2, s1, s2)) {
#                     LocalRules.matchReverse(memory);
#                 } else {
#                     SyllogisticRules.dedExe(t1, t2, sentence, belief, memory);
#                 }
#             }
#             break;
#         case 21:    // exemplification
#             if (Variable.unify(Symbols.VAR_INDEPENDENT, s1.getPredicate(), s2.getSubject(), s1, s2)) {
#                 if (s1.equals(s2)) {
#                     return;
#                 }
#                 t1 = s1.getSubject();
#                 t2 = s2.getPredicate();
#                 if (Variable.unify(Symbols.VAR_QUERY, t1, t2, s1, s2)) {
#                     LocalRules.matchReverse(memory);
#                 } else {
#                     SyllogisticRules.dedExe(t1, t2, sentence, belief, memory);
#                 }
#             }
#             break;
#         case 22:    // abduction
#             if (Variable.unify(Symbols.VAR_INDEPENDENT, s1.getPredicate(), s2.getPredicate(), s1, s2)) {
#                 if (s1.equals(s2)) {
#                     return;
#                 }
#                 t1 = s1.getSubject();
#                 t2 = s2.getSubject();
#                 if (!SyllogisticRules.conditionalAbd(t1, t2, s1, s2, memory)) {         // if conditional abduction, skip the following
#                     CompositionalRules.composeCompound(s1, s2, 1, memory);
#                     SyllogisticRules.abdIndCom(t1, t2, sentence, belief, figure, memory);
#                 }
#                 CompositionalRules.EliminateVariableOfConditionAbductive(figure,sentence,belief,memory);
#             }
#             break;
#         default:
#     }
# }