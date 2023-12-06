# from ...Narsese import Compound

# def compound_remove_components

from typing import Union
from pynars import Global
from pynars.Config import Config, Enable
from pynars.NAL.Functions.TemporalFunctions import eternalize, project
from pynars.Narsese import Budget
from pynars.Narsese import Sentence, Judgement, Truth, Task
from copy import deepcopy
# import Config, Global
from math import sqrt
from pynars.Narsese import Sentence, Stamp, Term
from pynars.Narsese import TRUE, FALSE, UNSURE
from pynars.Narsese import Goal, Quest, Question

def truth_to_quality(truth: Truth) -> float:
    return max(truth.e, (1 - truth.e)*0.75);
    
def distribute_budget_among_links(budget: Budget, n_links: int) -> Budget:
    return Budget(budget.priority/sqrt(n_links), budget.durability, budget.quality)

def project_truth(premise1: Union[Judgement, Goal, Question, Quest], premise2: Union[Judgement, Goal]):
    '''
    project the truth of the belief to that of the task.
    Ref:
        [1] OpenNARS 3.0.4 Sentence.java line 362~380
        ```
        public TruthValue projectionTruth(final long targetTime, final long currentTime, Memory mem) {
            TruthValue newTruth = null;
            if (!stamp.isEternal()) {
                newTruth = TruthFunctions.eternalize(truth, mem.narParameters);
                if (targetTime != Stamp.ETERNAL) {
                    final long occurrenceTime = stamp.getOccurrenceTime();
                    final float factor = TruthFunctions.temporalProjection(occurrenceTime, targetTime, currentTime, mem.narParameters);
                    final double projectedConfidence = factor * truth.getConfidence();
                    if (projectedConfidence > newTruth.getConfidence()) {
                        newTruth = new TruthValue(truth.getFrequency(), projectedConfidence, mem.narParameters);
                    }
                }
            }
            if (newTruth == null) newTruth = truth.clone();
            return newTruth;
        }
        ```
    [2] Hammer, Patrick, Tony Lofthouse, and Pei Wang. "The OpenNARS implementation of the non-axiomatic reasoning system." International conference on artificial general intelligence. Springer, Cham, 2016.

    The two methods seem different. I adopt the second one.
    '''
    truth = premise2.truth
    if not premise2.is_eternal:
        if not premise1.is_eternal:
            t_target = premise1.stamp.t_occurrence
            t_source = premise2.stamp.t_occurrence
            truth = project(truth, t_source, Global.time, t_target)
        truth = eternalize(truth)
    return truth

    

def calculate_solution_quality(s_in: Sentence, s_solution: Sentence, rate_by_confidence: bool=True):
    '''
    Evaluate the quality of the judgment as a solution to a problem

    Ref: OpenNARS 3.1.0 line 262~286; Source Code:
        ```
            public static float solutionQuality(final boolean rateByConfidence, final Task probT, final Sentence solution, final Memory memory, final Timable time) {
                final Sentence problem = probT.sentence;
                
                if ((probT.sentence.punctuation != solution.punctuation && solution.term.hasVarQuery()) || !matchingOrder(problem.getTemporalOrder(), solution.getTemporalOrder())) {
                    return 0.0F;
                }
                
                TruthValue truth = solution.truth;
                if (problem.getOccurenceTime()!=solution.getOccurenceTime()) {
                    truth = solution.projectionTruth(problem.getOccurenceTime(), time.time(), memory);
                }
                
                //when the solutions are comparable, we have to use confidence!! else truth expectation.
                //this way negative evidence can update the solution instead of getting ignored due to lower truth expectation.
                //so the previous handling to let whether the problem has query vars decide was wrong.
                if (!rateByConfidence) {
                    /*
                    * just some function that decreases quality of solution if it is complex, and increases if it has a high truth expecation
                    */
                    
                    return (float) (truth.getExpectation() / Math.sqrt(Math.sqrt(Math.sqrt(solution.term.getComplexity()*memory.narParameters.COMPLEXITY_UNIT))));
                } else {
                    return (float)truth.getConfidence();
                }
            }
        ```
    Args: 
        s_in (Sentence): the sentence in an input task.
        s_solution (Sentence): the sentence in the memory for solving the task.
    Returns:
        quality (float): the quality of the solution.
    '''

    if (
        (s_in.punct != s_solution.punct and s_solution.term.has_qvar) #or not temporal_matching_order(s_in, s_solution)
    ):
        return 0.0
    
    truth = s_solution.truth

    t_occur_in = s_in.stamp.t_occurrence
    t_occur_solution = s_solution.stamp.t_occurrence
    if t_occur_solution != t_occur_in:
        truth = project_truth(s_in, s_solution)

    # When the solutions are comparable, we have to use confidence!! else truth expectation. This way negative evidence can update the solution instead of getting ignored due to lower truth expectation. So the previous handling to let whether the problem has query vars decide was wrong.
    if not rate_by_confidence:
        # Just some function that decreases quality of solution if it is complex, and increases if it has a high truth expecation        
        # raise "what does `Config.complexity_unit` mean?"
        return truth.e / sqrt(sqrt(sqrt(s_solution.term.complexity * Config.r_term_complexity_unit)))
    else:
        return truth.c


# def temporal_matching_order(s1: Sentence, s2: Sentence):
#     if Enable.temporal_rasoning:
#         # raise 'Eliminate this line.'
#         order1 = s1.temporal_order
#         order2 = s2.temporal_order
#         return (order1 == order2) or (order1 == TemporalOrder.NONE) or (order2 == TemporalOrder.NONE)
#     else:
#         return True

'''
The rules out of the book *Non-Axiomatic-Logic*
'''
def revisible(task: Task, belief: Task):
    ''' Check whether two sentences can be used in revision
    Ref: OpenNARS 3.1.0 LocalRules.java line 91~106; Source Code:
        ```
        public static boolean revisible(final Sentence s1, final Sentence s2, Parameters narParameters) {
            if(!s1.isEternal() && !s2.isEternal() && Math.abs(s1.getOccurenceTime() - s2.getOccurenceTime()) > narParameters.REVISION_MAX_OCCURRENCE_DISTANCE) {
                return false;
            }
            if(s1.term.term_indices != null && s2.term.term_indices != null) {
                for(int i=0;i<s1.term.term_indices.length;i++) {
                    if(s1.term.term_indices[i] != s2.term.term_indices[i]) {
                        return false;
                    }
                }
            }
            return (s1.getRevisible() && 
                    matchingOrder(s1.getTemporalOrder(), s2.getTemporalOrder()) &&
                    CompoundTerm.replaceIntervals(s1.term).equals(CompoundTerm.replaceIntervals(s2.term)) &&
                    !Stamp.baseOverlap(s1.stamp, s2.stamp));
        }
        ```
    '''
    s1: Sentence = task.sentence
    s2: Sentence = belief.sentence
    if not (s1.is_goal or s1.is_judgement):
        return False
    if s1.evidential_base == s2.evidential_base:
        return False
    if s1.evidential_base.is_overlaped(s2.evidential_base):
        return False
    if not s1.is_eternal and not s2.is_eternal and abs(s1.stamp.t_occurrence - belief.stamp.t_occurrence) > Config.revision_max_occurence_distance:
        return False
    
    # if(s1.term.term_indices != null and s2.term.term_indices != null):
    #     for(int i=0;i<s1.term.term_indices.length;i++):
    #         if(s1.term.term_indices[i] != s2.term.term_indices[i]):
    #             return False
    
    # return (s1.getRevisible() and
    #     matchingOrder(s1.getTemporalOrder(), s2.getTemporalOrder()) and
    #     CompoundTerm.replaceIntervals(s1.term).equals(CompoundTerm.replaceIntervals(s2.term)) and
    #     not s1.stamp.evidential_base.is_overlaped(s2.stamp))
    
    return True # TODO

'''Operation relative'''
def truth_from_term(term: Term):
    ''''''
    if term == TRUE: return Truth(1.0, Config.c, Config.k)
    elif term == FALSE: return Truth(0.0, Config.c, Config.k)
    elif term == UNSURE: return Truth(0.5, Config.c/2, Config.k)
    else: return None

def truth_to_term(truth: Truth):
    f = truth.f
    if f > 0.66: return TRUE
    elif f < 0.33: return FALSE
    else: return UNSURE
