"""
Note: The code is translated from TemporalRules.java in OpenNARS 3.0.4
"""

from opennars.Narsese import Sentence, Task
from opennars.Narsese import TemporalOrder
from opennars.Narsese import Truth
from opennars.Narsese import Term, Statement, Compound, Interval
from .util import invalid_statement
from Config import Config
from opennars.NAL.Functions import project, eternalize
from opennars import Global
from opennars.NAL.Functions.TruthValueFunctions import *
from opennars.NAL.Functions.BudgetFunctions import *

def reverse_order(order: TemporalOrder) -> TemporalOrder:
    return -order

def matching_order(order1: TemporalOrder, order2: TemporalOrder) -> bool:
    return (order1 is order2) or (order1 is TemporalOrder.NONE) or (order2 is TemporalOrder.NONE)


def ded_exe_order(order1: TemporalOrder, order2: TemporalOrder) -> TemporalOrder:
    order = TemporalOrder.INVALID

    if (order1 == order2) or (order2 == TemporalOrder.NONE):
        order = order1
    elif (order1 == TemporalOrder.NONE) or (order1 == TemporalOrder.CONCURRENT):
        order = order2
    elif order2 == TemporalOrder.CONCURRENT:
        order = order1

    return order


def abd_ind_com_order(order1: TemporalOrder, order2: TemporalOrder) -> TemporalOrder:
    order = TemporalOrder.INVALID
    if (order2 is TemporalOrder.NONE):
        order = order1
    elif (order1 is TemporalOrder.NONE) or (order1 is TemporalOrder.CONCURRENT):
        order = -order2
    elif (order2 is TemporalOrder.CONCURRENT) or (order1 is -order2):
        order = order1
    return order

def analogy_order(order1: TemporalOrder, order2: TemporalOrder, figure: int) -> TemporalOrder:
    order = TemporalOrder.INVALID
    if (order2 is TemporalOrder.NONE) or (order2 is TemporalOrder.CONCURRENT):
        order = order1
    elif (order1 is TemporalOrder.NONE) or (order1 is TemporalOrder.CONCURRENT):
        order = order2 if figure < 20 else -order2
    elif order1 is order2:
        if (figure == 12) or (figure == 21):
            order = order1
    elif order1 is -order2:
        if (figure == 11) or (figure == 22):
            order = order1
    return order

def resemblance_order(order1: TemporalOrder, order2: TemporalOrder, figure: int) -> TemporalOrder:
    order = TemporalOrder.INVALID
    if order2 is TemporalOrder.NONE:
        order = order1 if (figure > 20) else -order1    # switch when 11 or 12
    elif (order1 is TemporalOrder.NONE) or (order1 is  TemporalOrder.CONCURRENT):
        order = order2 if (figure % 10 == 1) else -order2       # switch when 12 or 22
    elif order2 is TemporalOrder.CONCURRENT:
        order = order1 if (figure > 20) else -order1            # switch when 11 or 12
    elif order1 is order2:
        order = order1 if (figure == 21) else -order1
    return order

def compose_order(order1: TemporalOrder, order2: TemporalOrder) -> TemporalOrder:
    order = TemporalOrder.INVALID
    if order2 is TemporalOrder.NONE:
        order = order1
    elif order1 is TemporalOrder.NONE:
        order = order2
    elif order1 is order2:
        order = order1
    return order




def too_much_temporal_statements(t: Term) -> bool: 
    ''' 
    whether temporal induction can generate a task by avoiding producing wrong terms; only one temporal operator is allowed
    '''
    return (t is None) or (t.contained_temporal_relations > 1)



# //TODO maybe split &/ case into own function
def temporal_induction(s1: Sentence, s2: Sentence, SucceedingEventsInduction: bool, addToMemory: bool, allowSequence: bool, currentTime: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]:
    
    if (s1.truth is None) or (s2.truth is None) or \
        (not s1.is_judgement) or (not s2.is_judgement) or \
        s1.is_eternal or s2.is_eternal:
        return []
    
    if invalid_statement(t1, t2, False):
        return []
    
    t1 = s1.term
    t2 = s2.term
            
    deriveSequenceOnly: bool = (not addToMemory) or invalid_statement(t1, t2, True)
    
    durationCycles = int(Config.temporal_duration)
    time1 = s1.occurence_time
    time2 = s2.occurence_time
    timeDiff = time2 - time1
    interval: Interval = None
    
    if not is_concurrent(s1, s2, durationCycles):
        interval = Interval(abs(timeDiff))
        if (timeDiff > 0):
            t1 = Compound.SequentialEvents(t1, interval)
        else:
            t2 = Compound.SequentialEvents(t2, interval)

    order = get_order(timeDiff, durationCycles)
    givenTruth1 = s1.truth
    givenTruth2 = s2.truth
    
    # This code adds a penalty for large time distance (TODO probably revise)
    s3: Sentence = projection(s2, s1, currentTime)
    givenTruth2 = s3.truth 
    
    # Truth and priority calculations
    truth1 = Truth_induction(givenTruth1, givenTruth2)
    truth2 = Truth_induction(givenTruth2, givenTruth1)
    truth3 = Truth_comparison(givenTruth1, givenTruth2)
    truth4 = Truth_intersection(givenTruth1, givenTruth2)
    budget1 = Budget_forward(truth1, budget_tasklink, budget_termlink)
    budget2 = Budget_forward(truth2, budget_tasklink, budget_termlink)
    budget3 = Budget_forward(truth3, budget_tasklink, budget_termlink)
    budget4 = Budget_forward(truth4, budget_tasklink, budget_termlink) # this one is sequence in sequenceBag, no need to reduce here
    
    statement1 = Statement.Implication(t1, t2, order)
    statement2 = Statement.Implication(t2, t1, -order)
    statement3 = Statement.Equivalence(t1, t2, order)
    statement4: Term = None
    match order:
        case TemporalOrder.FORWARD:
            statement4 = Compound.Conjunction(t1, interval, s2.term, order)
        case TemporalOrder.BACKWARD:
            statement4 = Compound.Conjunction(s2.term, interval, t1, -order)
        case _:
            statement4 = Compound.Conjunction(t1, s2.term, order)
    
    
    # t11s = list[Term]()
    # t22s = list[Term]()
    # penalties = list[float]()
    # # "Perception Variable Introduction Rule" - https://groups.google.com/forum/#!topic/open-nars/uoJBa8j7ryE
    # if (not deriveSequenceOnly) and statement2 is not None:
    #     for subjectIntro in (True, False):
    #         Set<Pair<Term,Float>> ress = CompositionalRules.introduceVariables(nal, statement2, subjectIntro)
    #         for(Pair<Term,Float> content_penalty : ress)  //ok we applied it, all we have to do now is to use it
    #             t11s.add(((Statement)content_penalty.getLeft()).getPredicate())
    #             t22s.add(((Statement)content_penalty.getLeft()).getSubject())
    #             penalties.add(content_penalty.getRight())
            
        
    
#     final List<Task> derivations= new ArrayList<>()
#     if (!deriveSequenceOnly ) 
#         for(int i=0 i<t11s.size() i++) 
#             Term t11 = t11s.get(i)
#             Term t22 = t22s.get(i)
#             Float penalty = penalties.get(i)
#             statement11 = Implication.make(t11, t22, order)
#             statement22 = Implication.make(t22, t11, reverseOrder(order))
#             statement33 = Equivalence.make(t11, t22, order)
#             appendConclusion(nal, truth1.clone().mulConfidence(penalty), budget1.clone(), statement11, derivations)
#             appendConclusion(nal, truth2.clone().mulConfidence(penalty), budget2.clone(), statement22, derivations)
#             appendConclusion(nal, truth3.clone().mulConfidence(penalty), budget3.clone(), statement33, derivations)
#         

#         appendConclusion(nal, truth1, budget1, statement1, derivations)
#         appendConclusion(nal, truth2, budget2, statement2, derivations)
#         appendConclusion(nal, truth3, budget3, statement3, derivations)
#     

#     if(!tooMuchTemporalStatements(statement4)) 
#         if(!allowSequence) 
#             return derivations
#         
#         final List<Task> tl=nal.doublePremiseTask(statement4, truth4, budget4,true, false, addToMemory)
#         if(tl!=null) 
#             for(final Task t : tl) 
#                 //fill sequenceTask buffer due to the new derived sequence
#                 if(addToMemory &&
#                         t.sentence.isJudgment() &&
#                         !t.sentence.isEternal() && 
#                         t.sentence.term instanceof Conjunction && 
#                         t.sentence.term.getTemporalOrder() != TemporalRules.TemporalOrder.NONE &&
#                         t.sentence.term.getTemporalOrder() != TemporalRules.TemporalOrder.INVALID) 
#                     TemporalInferenceControl.addToSequenceTasks(nal, t)
#                 

#                 derivations.add(t)
#             
#         
#     

#     return derivations
# 

# private static void appendConclusion(DerivationContext nal, TruthValue truth1, BudgetValue budget1, Statement statement1, List<Task> success) 
#     if(!tooMuchTemporalStatements(statement1)) 
#         final List<Task> t=nal.doublePremiseTask(statement1, truth1, budget1, true, false)
#         if(t!=null) 
#             success.addAll(t)
#         
#     
# 


def is_concurrent(a: Sentence, b: Sentence, durationCycles: int) -> bool:
    '''
    a: (stationary) event A
    b: (relative) event A
    '''
    
    if a.is_eternal:
        # if both are eternal, consider concurrent.  this is consistent with the original
        # method of calculation which compared equivalent integer values only
        return b.is_eternal
    elif b.is_eternal:
        return False # a==b was compared above.
    else:
        return get_order(b.occurence_time - a.occurence_time, durationCycles) is TemporalOrder.CONCURRENT


def get_order(time_diff: int, duration_cycles: int) -> TemporalOrder:
    '''
    if (relative) event B after  (stationary) event A then, order=forward;
    if (relative) event B before (stationary) event A then, order=backward
    if event B and event A occur at the same time (relative to duration), then order=concurrent
    '''
    half_duration = duration_cycles/2
    if time_diff > half_duration:
        return TemporalOrder.FORWARD
    elif time_diff < -half_duration:
        return TemporalOrder.BACKWARD
    else:
        return TemporalOrder.CONCURRENT
    

""" ------------------ Helper functions ------------------ """

def projection(sentence: Sentence, target_sentence: Sentence, currentTime: int) -> Sentence:
    '''
    [Stems from `Sentence.projection`]

    project a judgment to a difference occurrence time

    Args:
        targetTime: The time to be projected into
        currentTime: The current time as a reference
    Returns:
        The projected belief
    '''
    truth_old = sentence.truth
    newTruth = projection_truth(truth_old, target_sentence, currentTime)
    eternalizing = newTruth.eternalizing
            
    newStamp = sentence.stamp.clone()
    if eternalizing:
        newStamp.eternalize()
    else:
        newStamp.t_occurrence = target_sentence.occurence_time
    
    return Sentence.make(sentence.term, sentence.punct, newStamp, newTruth, False)


def projection_truth(sentence: Sentence, target_sentence: Sentence, currentTime: int):
    '''
    [Stems from `Sentence.projectionTruth`]
    '''
    newTruth: Truth = None
    if not sentence.is_eternal:
        newTruth = eternalize(sentence.truth)
        newTruth.eternalizing = True
        if not target_sentence.is_eternal:
            newTruth2 = project(sentence.truth, sentence.occurence_time, currentTime, target_sentence.occurence_time)
            if newTruth2.c > newTruth.c:
                newTruth = newTruth2
                newTruth.eternalizing = False
    
    if newTruth is None: 
        newTruth = sentence.truth.clone()
        newTruth.eternalizing = False

    return newTruth