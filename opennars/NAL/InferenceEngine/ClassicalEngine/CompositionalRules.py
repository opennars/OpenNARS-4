from opennars.Narsese import Term, Statement, Compound, Task, Sentence, Variable, VarPrefix
from opennars.Narsese import Truth, Budget
from opennars.Narsese import Connector, Copula
from opennars.NAL.Functions.BudgetFunctions import *
from opennars.NAL.Functions.TruthValueFunctions import *
from opennars.NAL.Functions.StampFunctions import *
from . import VariableTools
import util


def EliminateVariableOfConditionAbductive(task: Task, belief: Sentence, figure: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]|None:
    tasks_derived = []

    sentence = task.sentence
    T1: Statement = sentence.term.clone()
    T2: Statement = belief.term.clone()
    S1: Term = T2.subject
    P1: Term = T2.predicate
    S2: Term = T1.subject
    P2: Term = T1.predicate
    
    if figure == 21:
        res1 = dict[Term, Term]()
        res2 = dict[Term, Term]()
        VariableTools.findSubstitute(VarPrefix.Independent, P1, S2, res1, res2) # //this part is 
        VariableTools.applySubstitute(T1, res2)  # independent, the rule works if it unifies
        VariableTools.applySubstitute(T2, res1)
        if S1.connector is Connector.Conjunction:
            # try to unify P2 with a component
            for s1 in deepcopy(S1.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]()  # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, P2, res3, res4):
                    for s2 in deepcopy(S1.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))

        if P2.connector is Connector.Conjunction:
            # try to unify S1 with a component
            for s1 in deepcopy(P2.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]() # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, S1, res3, res4):
                    for s2 in deepcopy(P2.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))
    
    if figure == 12:
        res1 = dict[Term, Term]()
        res2 = dict[Term, Term]()
        VariableTools.findSubstitute(VarPrefix.Independent, S1, P2, res1, res2)  # this part is 
        VariableTools.applySubstitute(T1, res2) # independent, the rule works if it unifies
        VariableTools.applySubstitute(T2, res1)
        if S2.connector is Connector.Conjunction:
            # try to unify P1 with a component
            for s1 in deepcopy(S2.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]()  # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, P1, res3, res4):
                    for s2 in deepcopy(S2.terms):
                        VariableTools.applySubstitute(s2, res3);
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))

        if(P1.connector is Connector.Conjunction):
            # try to unify S2 with a component
            for s1 in deepcopy(P1.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]() # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, S2, res3, res4):
                    for s2 in deepcopy(P1.terms):
                        VariableTools.applySubstitute(s2, res3);
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))
    
    if figure == 11:
        res1 = dict[Term, Term]()
        res2 = dict[Term, Term]()
        VariableTools.findSubstitute(VarPrefix.Independent, S1, S2, res1, res2)     # this part is 
        VariableTools.applySubstitute(T1, res2)  # independent, the rule works if it unifies
        VariableTools.applySubstitute(T2, res1)
        if P1.connector is Connector.Conjunction:
            # try to unify P2 with a component
            for s1 in deepcopy(P1.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]() # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, P2, res3, res4):
                    for s2 in deepcopy(P1.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))

        if P2.connector is Connector.Conjunction:
            # try to unify P1 with a component
            for s1 in deepcopy(P2.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]() # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, P1, res3, res4):
                    for s2 in deepcopy(P2.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))
    
    if figure == 22:
        res1 = dict[Term, Term]()
        res2 = dict[Term, Term]()
        VariableTools.findSubstitute(VarPrefix.Independent, P1, P2, res1, res2) # this part is 
        VariableTools.applySubstitute(T1, res2) # independent, the rule works if it unifies
        VariableTools.applySubstitute(T2, res1)
        if(S1.connector is Connector.Conjunction):
            # try to unify S2 with a component
            for s1 in deepcopy(S1.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]() # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, S2, res3, res4):
                    for s2 in deepcopy(S1.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))

        if(S2.connector is Connector.Conjunction):
            # try to unify S1 with a component
            for  s1 in deepcopy(S2.terms):
                res3 = dict[Term, Term]()
                res4 = dict[Term, Term]()  # here the dependent part matters, see example of Issue40
                if VariableTools.findSubstitute(VarPrefix.Dependent, s1, S1, res3, res4):
                    for s2 in deepcopy(S2.terms):
                        VariableTools.applySubstitute(s2, res3)
                        if not (s2 == s1):
                            truth = Truth_abduction(sentence.truth, belief.truth)
                            budget = Budget_forward_compound(s2, truth, budget_tasklink, budget_termlink)
                            tasks_derived.append(util.double_premise_task(task, belief, s2, truth, budget))
    
    return tasks_derived

def IntroVarSameSubjectOrPredicate(task: Task, belief: Sentence, originalMainSentence: Sentence, subSentence: Sentence, component: Term|Statement, content: Term|Statement, index: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]|None:
    tasks_derived = []
    cloned: Sentence = deepcopy(originalMainSentence)
    T1: Term = cloned.term
    if (not T1.is_compound) or (not content.is_compound)
        return

    T: Compound = T1
    T2: Compound = content.clone()

    # component: Statement = component
    # content: Statement = content
    if (component.copula is Copula.Inheritance and content.copula is Copula.Inheritance) or \
        (component.copula is Copula.Similarity and content.copula is Copula.Similarity):
        result: Compound = T
        if component == content:
            return # wouldn't make sense to create a conjunction here, would contain a statement twice
        if (component.predicate == content.predicate) and not (component.predicate.is_atom and component.predicate.is_var):
            V = Variable.Dependent("depIndVar1")
            zw: Compound = T[index]
            zw = util.set_component(zw, 1, V)
            T2 = util.set_component(T2, 1, V)
            res = Compound.Conjunction(zw, T2)
            T = util.set_component(T, index, res)
        elif (component.subject == content.subject) and not (component.subject.is_atom and  component.subject.is_var):
            V = Variable.Dependent("depIndVar2")
            zw = T[index]
            zw = util.set_component(zw, 0, V)
            T2 = util.set_component(T2, 0, V)
            res = Compound.Conjunction(zw, T2)
            T = util.set_component(T, index, res)

        truth = Truth_induction(originalMainSentence.truth, subSentence.truth)
        budget = Budget_forward_compound(T, truth, budget_tasklink, budget_termlink)
        tasks_derived.append(util.double_premise_task(task, belief, T, truth, budget))
    return tasks_derived



''' -------------------- intersections and differences -------------------- '''

def composeCompound(task: Task, belief: Sentence, taskContent: Statement, beliefContent: Statement, index: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]|None:
    '''
    {<S ==> M>, <P ==> M>} |- {<(S|P) ==> M>, <(S&P) ==> M>, <(S-P) ==> M>, <(P-S) ==> M>}
    *
    Args:
        [to be added]
        task: Current task
        belief: The belief
        taskSentence: The first premise
        belief: The second premise
        index: The location of the shared term
    '''
    tasks_derived = []

    if ((task.is_judgement) or (taskContent.is_statement and beliefContent.is_statement and taskContent.copula not = beliefContent.copula)):
        return

    componentT: Compound = taskContent[1 - index]
    componentB: Compound = beliefContent[1 - index]
    componentCommon: Term = taskContent[index]
    
    if componentT.is_compound and componentT.contains(componentB):
        decomposeCompound(componentT, componentB, componentCommon, index, True, budget_tasklink, budget_termlink)
        return
    elif componentB.is_compound and componentB.contains(componentT):
        decomposeCompound(componentB, componentT, componentCommon, index, True, budget_tasklink, budget_termlink)
        return
    
    truthT: Truth = task.truth
    truthB: Truth = belief.truth
    truthOr: Truth = Truth_union(truthT, truthB)
    truthAnd: Truth = Truth_intersection(truthT, truthB)
    truthDif: Truth = None
    termOr: Term = None
    termAnd: Term = None
    termDif: Term = None
    if index == 0:
        if taskContent.copula is Copula.Inheritance: 
            termOr = Compound.IntensionalIntersection(componentT, componentB)
            termAnd = Compound.ExtensionalIntersection(componentT, componentB)
            if truthB.is_negative:
                if not truthT.is_negative:
                    termDif = Compound.ExtensionalDifference(componentT, componentB)
                    truthDif = Truth_intersection(truthT, Truth_negation(truthB))
            elif truthT.is_negative:
                termDif = Compound.ExtensionalDifference(componentB, componentT)
                truthDif = Truth_intersection(truthB, Truth_negation(truthT))
        elif taskContent.copula is Copula.Implication:
            termOr = Compound.Disjunction(componentT, componentB)
            termAnd = Compound.Conjunction(componentT, componentB)

        tasks_derived.append(processComposed(task, belief, taskContent, componentCommon.clone(), termOr, truthOr, budget_tasklink, budget_termlink))
        tasks_derived.append(processComposed(task, belief, taskContent, componentCommon.clone(), termAnd, truthAnd, budget_tasklink, budget_termlink))
        tasks_derived.append(processComposed(task, belief, taskContent, componentCommon.clone(), termDif, truthDif, budget_tasklink, budget_termlink))
    else:    # index == 1
        if taskContent.copula is Copula.Inheritance:
            termOr = Compound.ExtensionalIntersection(componentT, componentB)
            termAnd = Compound.IntensionalIntersection(componentT, componentB)
            if truthB.is_negative:
                if not truthT.is_negative:
                    termDif = Compound.IntensionalDifference(componentT, componentB)
                    truthDif = Truth_intersection(truthT, Truth_negation(truthB))
            elif truthT.is_negative:
                termDif = Compound.IntensionalDifference(componentB, componentT)
                truthDif = Truth_intersection(truthB, Truth_negation(truthT))
        elif taskContent.copula is Copula.Implication:
            termOr = Compound.Conjunction(componentT, componentB)
            termAnd = Compound.Disjunction(componentT, componentB)

        tasks_derived.append(processComposed(task, belief, taskContent, termOr, componentCommon.clone(), truthOr, budget_tasklink, budget_termlink))
        tasks_derived.append(processComposed(task, belief, taskContent, termAnd, componentCommon.clone(), truthAnd, budget_tasklink, budget_termlink))
        tasks_derived.append(processComposed(task, belief, taskContent, termDif, componentCommon.clone(), truthDif, budget_tasklink, budget_termlink))

    if taskContent.copula is Copula.Inheritance:
        introVarOuter(taskContent, beliefContent, index); #            introVarImage(taskContent, beliefContent, index, memory);

def processComposed(currentTask: Task, currentBelief: Sentence, statement: Statement, subject: Term, predicate: Term, truth: Truth, budget_tasklink: Budget, budget_termlink: Budget=None):
    '''
    Finish composing implication term

    Args:
        premise1: Type of the contentInd
        subject: Subject of contentInd
        predicate: Predicate of contentInd
        truth: TruthValue of the contentInd
    '''
    if (subject is None) or (predicate is None):
        return
    
    content = Statement(statement.copula, subject, predicate) if statement.is_statement else None

    if (content is None) or (content == statement) or (content == currentBelief.term):
        return
    
    budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
    return util.double_premise_task(currentTask, currentBelief, content, truth, budget)


def decomposeCompound(task: Task, belief: Sentence, compound: Compound, component: Term, term1: Term, index: int, compoundTask: bool, budget_tasklink: Budget, budget_termlink: Budget=None) -> Task|None:
    '''
    {<(S|P) ==> M>, <P ==> M>} |- <S ==> M>

    Args:
        task: Current task
        implication: The implication term to be decomposed
        componentCommon: The part of the implication to be removed
        term1: The other term in the contentInd
        index: The location of the shared term: 0 for subject, 1 for predicate
        compoundTask: Whether the implication comes from the task
    '''
    if compound.is_statement or (compound.is_compound and (compound.connector is Connector.ExtensionalImage or compound.connector is Connector.IntensionalImage)):
        return

    term2: Term = Compound.reduce_components(compound, component)

    if term2 is None:
        return

    sentence: Sentence = task.sentence
    oldContent: Statement = sentence.term
    v1: Truth
    v2: Truth
    if compoundTask:
        v1 = sentence.truth
        v2 = belief.truth
    else:
        v1 = belief.truth
        v2 = sentence.truth
    
    truth: Truth = None
    content: Term
    if index == 0:
        content = Statement(oldContent.copula, term1, term2) if oldContent.is_statement else None
        if content is None:
            return
        
        if oldContent.copula is Copula.Inheritance:
            if compound.connector is Connector.ExtensionalIntersection:
                truth = Truth_deconjuntion(v1, v2)
            elif compound.connector is Connector.IntensionalIntersection:
                truth = Truth_dedisjunction(v1, v2)
            elif (compound.connector is Connector.IntensionalSet) and (component.connector is Connector.IntensionalSet):
                truth = Truth_deconjuntion(v1, v2)
            elif (compound.connector is Connector.ExtensionalSet) and (compound.connector is Connector.ExtensionalSet):
                truth = Truth_dedisjunction(v1, v2)
            elif compound.connector is Connector.ExtensionalDifference:
                if compound[0] == component:
                    truth = Truth_dedisjunction(v2, v1)
                else:
                    truth = Truth_deconjuntion(v1, v2)
        elif oldContent.copula is Copula.Implication:
            if compound.connector is Connector.Conjunction:
                truth = Truth_deconjuntion(v1, v2)
            elif compound.connector is Connector.Disjunction:
                truth = Truth_dedisjunction(v1, v2)
    else:
        content = Statement(oldContent.copula, term2, term1)
        if content is None:
            return

        if oldContent.copula is Copula.Inheritance:
            if compound.connector is Connector.IntensionalIntersection:
                truth = Truth_deconjuntion(v1, v2)
            elif compound.connector is Connector.ExtensionalIntersection:
                truth = Truth_dedisjunction(v1, v2)
            elif (compound.connector is Connector.ExtensionalSet) and (component.connector is Connector.ExtensionalSet):
                truth = Truth_deconjuntion(v1, v2)
            elif (compound.connector is Connector.IntensionalSet) and (component.connector is Connector.IntensionalSet):
                truth = Truth_dedisjunction(v1, v2)
            elif compound.connector is Connector.IntensionalDifference:
                if compound[1] == component:
                    truth = Truth_dedisjunction(v2, v1)
                else:
                    truth = Truth_deconjuntion(v1, Truth_negation(v2))
        elif oldContent.copula is Copula.Implication:
            if compound.connector is Connector.Disjunction:
                truth = Truth_deconjuntion(v1, v2)
            elif compound.connector is Connector.Conjunction:
                truth = Truth_dedisjunction(v1, v2)
    if truth is not None:
        budget: Budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
        task_derived: Task = util.double_premise_task(task, belief, content, truth, budget)
        return task_derived


''' --------------- rules used for variable introduction --------------- '''

def introVarOuter(task: Task, belief: Sentence, taskContent: Statement, beliefContent: Statement, index: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> Task|None:
    '''
    Introduce a dependent variable in an outer-layer conjunction
    
    Args:
        taskContent The first premise <M --> S>
        beliefContent The second premise <M --> P>
        index The location of the shared term: 0 for subject, 1 for predicate
    '''
    tasks_derived = []

    truthT = task.truth
    truthB = belief.truth
    varInd = Variable.Independent("varInd1")
    varInd2 = Variable.Independent("varInd2")

    term11: Term; term12: Term; term21: Term; term22: Term; commonTerm: Term

    subs = dict[Term, Term]()
    if index == 0:
        term11 = varInd
        term21 = varInd
        term12: Compound = taskContent.predicate.clone()
        term22: Compound = beliefContent.predicate.clone()
        if (term12.is_compound and term12.connector is Connector.ExtensionalImage) and (term22.is_compound and term22.connector is Connector.ExtensionalImage):
            commonTerm = term12.get_the_other_component()
            if (commonTerm is None) or (not term22.contain_term(commonTerm)):
                commonTerm = term22.get_the_other_component()
                if (commonTerm is None) or (not term12.contain_term(commonTerm)):
                    commonTerm = None

            if commonTerm is not None:
                subs[commonTerm] = varInd2
                VariableTools.applySubstitute(term12, subs)
                VariableTools.applySubstitute(term22, subs)
    else:
        term11: Compound = taskContent.subject.clone()
        term21: Compound = beliefContent.subject.clone()
        term12 = varInd
        term22 = varInd
        if (term11.connector is Connector.IntensionalImage) and (term21.connector is Connector.IntensionalImage):
            commonTerm = term11.get_the_other_component()
            if (commonTerm is None) or not term21.contain_term(commonTerm):
                commonTerm = term21.get_the_other_component()
                if (commonTerm is None) or (not term11.contain_term(commonTerm)):
                    commonTerm = None
            if commonTerm is not None:
                subs[commonTerm] = varInd2
                VariableTools.applySubstitute(term11, subs)
                VariableTools.applySubstitute(term21, subs)

    state1: Statement = Statement.Inheritance(term11, term12)
    state2: Statement = Statement.Inheritance(term21, term22)
    content: Term = Statement.Implication(state1, state2)
    if content is None:
        return

    truth = Truth_induction(truthT, truthB)
    budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget))

    content = Statement.Implication(state2, state1)
    truth = Truth_induction(truthB, truthT)
    budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget))
    content = Statement.Equivalence(state1, state2)
    truth = Truth_comparison(truthT, truthB)
    budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget))
    varDep = Variable.Dependent("varDep")
    if index == 0:
        state1 = Statement.Inheritance(varDep, taskContent.predicate)
        state2 = Statement.Inheritance(varDep, beliefContent.predicate)
    else:
        state1 = Statement.Inheritance(taskContent.subject, varDep)
        state2 = Statement.Inheritance(beliefContent.subject, varDep)
    
    content = Compound.Conjunction(state1, state2)
    truth = Truth_intersection(truthT, truthB)
    budget = Budget_forward_compound(content, truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget, False))

    return tasks_derived



def introVarInner(task: Task, belief: Sentence, premise1: Statement, premise2: Statement, oldCompound: Compound, budget_tasklink: Budget, budget_termlink: Budget=None) -> Task|None:
    '''
    {<M --> S>, <C ==> <M --> P>>} |- <(and, <#x --> S>, C) ==> <#x --> P>>
    {<M --> S>, (and, C, <M --> P>)} |- (and, C, <<#x --> S> ==> <#x --> P>>)
    
    Args:
        taskContent: The first premise directly used in internal induction,<M --> S>
        beliefContent: The componentCommon to be used as a premise in internal induction, <M --> P>
        oldCompound: The whole contentInd of the first premise, Implication or Conjunction
    '''
    tasks_derived = []

    taskSentence: Sentence = task.sentence
    if not taskSentence.is_judgement or (premise1.copula != premise2.copula) or oldCompound.contain_component(premise1):
        return
    
    subject1 = premise1.subject
    subject2 = premise2.subject
    predicate1 = premise1.predicate
    predicate2 = premise2.predicate
    commonTerm1: Term; commonTerm2: Term
    if subject1 == subject2:
        commonTerm1 = subject1
        commonTerm2 = secondCommonTerm(predicate1, predicate2, 0)
    elif predicate1 == predicate2:
        commonTerm1 = predicate1
        commonTerm2 = secondCommonTerm(subject1, subject2, 0)
    else:
        return

    substitute = dict[Term, Term]()
    substitute[commonTerm1] = Variable.Dependent("varDep2")
    content = Compound.Conjunction(premise1, oldCompound)
    VariableTools.applySubstitute(content, substitute)
    truth = Truth_intersection(taskSentence.truth, belief.truth)
    budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget, False))
    substitute.clear()
    substitute[commonTerm1] = Variable.Independent("varInd1")
    if commonTerm2 is not None:
        substitute[commonTerm2] = Variable.Independent("varInd2")

    content = util.make_implication_statement(premise1, oldCompound)
    if content is None:
        return tasks_derived

    VariableTools.applySubstitute(content, substitute)
    if premise1 == taskSentence.term:
        truth = Truth_induction(belief.truth, taskSentence.truth)
    else:
        truth = Truth_induction(taskSentence.truth, belief.truth)

    budget = Budget_forward(truth, budget_tasklink, budget_termlink)
    tasks_derived.append(util.double_premise_task(task, belief, content, truth, budget))
    return tasks_derived
# }


def secondCommonTerm(term1: Term|Compound, term2: Term|Compound, index: int) -> Term:
    '''
    Introduce a second independent variable into two terms with a common component

    Args:
        term1: The first term
        term2: The second term
        index: The index of the terms in their statement
    '''
    commonTerm: Term = None
    # term1: Compound = term1
    # term2: Compound = term2
    if index == 0:
        if term1.connector is Connector.ExtensionalImage and term2.connector is Connector.ExtensionalImage:
            commonTerm = term1.get_the_other_component()
            if (commonTerm is None) or (not term2.contain_term(commonTerm)):
                commonTerm = term2.get_the_other_component()
                if (commonTerm is None) or (not term1.contain_term(commonTerm)):
                    commonTerm = None
    else:
        if ((term1.connector is Connector.IntensionalImage) and (term2.connector is Connector.IntensionalImage)):

            commonTerm = term1.get_the_other_component()
            if (commonTerm is None) or (not term2.contain_term(commonTerm)):
                commonTerm = term2.get_the_other_component()
                if (commonTerm is None) or (not term1.contain_term(commonTerm)):
                    commonTerm = None
    
    return commonTerm


""" ------------------ Helper functions ------------------ """

def introduceVariables(implicationEquivalenceOrJunction: Term, subject: bool) -> set[tuple[Term, float]]:
    '''
    Introduction of variables that appear either within subjects or within predicates and more than once

    Args:
        implicationEquivalenceOrJunction
        subject
    Returns:
        The terms of the variable introduction variants plus the penalty from the amount of vars introduced
    '''
    result = set[tuple[Term, float]]()
    validForIntroduction = \
        (implicationEquivalenceOrJunction.is_compound and \
            implicationEquivalenceOrJunction.connector.is_junction
        ) or \
        (implicationEquivalenceOrJunction.is_statement and \
            (implicationEquivalenceOrJunction.copula.is_implication or \
            implicationEquivalenceOrJunction.copula.is_equivalence)
        )
    
    if not validForIntroduction:
        return result

    app = dict[Term, Term]()
    candidates = set[Term]()
#     if (implicationEquivalenceOrJunction.is_statement and (implicationEquivalenceOrJunction.copula.is_implication or implicationEquivalenceOrJunction.copula.is_equivalence)):
#         addVariableCandidates(candidates, ((Statement)implicationEquivalenceOrJunction).getSubject(),   subject);
#         addVariableCandidates(candidates, ((Statement)implicationEquivalenceOrJunction).getPredicate(), subject);
#     }
#     if(implicationEquivalenceOrJunction instanceof Conjunction or implicationEquivalenceOrJunction instanceof Disjunction) {
#         addVariableCandidates(candidates, implicationEquivalenceOrJunction, subject);
#     }
#     Map<Term,Integer> termCounts = implicationEquivalenceOrJunction.countTermRecursively(null);
#     int k = 0;
#     for(Term t : candidates) {
#         if(termCounts.getOrDefault(t, 0) > 1) {
#             //ok it appeared as subject or predicate but appears in the Conjunction more than once
#             //=> introduce a dependent variable for it!
#             String varType = "#";
#             if(implicationEquivalenceOrJunction instanceof Implication or implicationEquivalenceOrJunction instanceof Equivalence) {
#                 Statement imp = (Statement) implicationEquivalenceOrJunction;
#                 if(imp.getSubject().containsTermRecursively(t) && imp.getPredicate().containsTermRecursively(t)) {
#                     varType = "$";
#                 }
#             }
#             Variable introVar = new Variable(varType + "ind" + k);
#             app.put(t, introVar);
#             k++;
#         }
#     }
    
# #     List<Term> shuffledVariables = new ArrayList<Term>();
# #     for(Term t : app.keySet()) {
# #         shuffledVariables.add(t);
# #     }
# #     Collections.shuffle(shuffledVariables, nal.memory.randomNumber);
# #     Set<Term> selected = new LinkedHashSet<Term>();
# #     int i = 1;
# #     for(Term t : shuffledVariables) {
# #         selected.add(t);
# #         if(Math.pow(2.0, i) > nal.narParameters.VARIABLE_INTRODUCTION_COMBINATIONS_MAX) {
# #             break;
# #         }
# #         i++;
# #     }
# #     Set<Set<Term>> powerset = powerSet(selected);
# #     for(Set<Term> combo : powerset) {
# #         Map<Term,Term> mapping = new LinkedHashMap<>();
# #         for(Term vIntro : combo) {
# #             mapping.put(vIntro, app.get(vIntro));
# #         }
# #         if(mapping.size() > 0) {
# #             Float generalizationPenalty = (float) Math.pow(nal.narParameters.VARIABLE_INTRODUCTION_CONFIDENCE_MUL, mapping.size()-1);
# #             result.add(new ImmutablePair<>(((CompoundTerm)implicationEquivalenceOrJunction).applySubstitute(mapping),generalizationPenalty));
# #         }
# #     }
# #     return result;
# # }



def addVariableCandidates(candidates: set[Term], side: Term, subject: bool) -> None:
    '''
    Add the variable candidates that appear as subjects and predicates

    Args:
        candidates manipulated set of candidates
        side
        subject
    '''
#     boolean junction = (side instanceof Conjunction || side instanceof Disjunction || side instanceof Negation);
#     int n = junction ? ((CompoundTerm) side).size() : 1;
#     for(int i=0; i<n; i++) {
#         // we found an Inheritance
#         Term t = null;
#         if(i<n) {
#             if(junction) {
#                 t = ((CompoundTerm) side).term[i];
#             } else {
#                 t = side;
#             }
#         }
#         if(t instanceof Conjunction || t instanceof Disjunction || t instanceof Negation) { //component itself is a conjunction/disjunction
#             addVariableCandidates(candidates, t, subject);
#         }
#         if(t instanceof Inheritance) {
#             Inheritance inh = (Inheritance) t;
#             Term subjT = inh.getSubject();
#             Term predT = inh.getPredicate();
#             boolean addSubject = subject || subjT instanceof ImageInt; //also allow for images due to equivalence transform
#             Set<Term> removals = new LinkedHashSet<Term>();
#             if(addSubject && !subjT.hasVar()) {
#                 Set<Term> ret = CompoundTerm.addComponentsRecursively(subjT, null);
#                 for(Term ct : ret) {
#                     if(ct instanceof Image) {
#                         removals.add(((Image) ct).term[((Image) ct).relationIndex]);
#                     }
#                     candidates.add(ct);
#                 }
#             }
#             boolean addPredicate = !subject || predT instanceof ImageExt; //also allow for images due to equivalence transform
#             if(addPredicate && !predT.hasVar()) {
#                 Set<Term> ret = CompoundTerm.addComponentsRecursively(predT, null);
#                 for(Term ct : ret) {
#                     if(ct instanceof Image) {
#                         removals.add(((Image) ct).term[((Image) ct).relationIndex]);
#                     }
#                     candidates.add(ct);
#                 }
#             }
#             for(Term remove : removals) { //but do not introduce variables for image relation, only if they appear as product
#                 candidates.remove(remove);
#             }
#         }
#     }
# }
