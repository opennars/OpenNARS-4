from pynars.Config import Enable
from pynars.NAL.Inference.LocalRules import solve_query, solution_query, solution_question
from pynars.NAL.MetaLevelInference.VariableSubstitution import unification__var_const

from pynars.NARS.DataStructures._py.Link import TaskLink
from pynars.Narsese._py.Sentence import Goal, Judgement, Question
from pynars.Narsese import Statement, Term, Sentence, Budget, Task
from pynars.Narsese._py.Task import Belief, Desire
from .Concept import Concept
from .Bag import Bag
from pynars.NAL.Functions.Tools import revisible
from pynars.NAL.Inference import local__revision
# from pynars.NARS import Operation

class Memory:
    def __init__(self, capacity: int, n_buckets: int = None, take_in_order: bool = False) -> None:
        self.concepts = Bag(capacity, n_buckets=n_buckets, take_in_order=take_in_order)
        
    def accept(self, task: Task):
        '''
        **Accept task**: Accept a task from the `Overall Experience`, and link it from all directly related concepts. Ref: *The Conceptual Design of OpenNARS 3.1.0*.
        '''
        # merging the new task as a concept into the memory
        concept: Concept = Concept._conceptualize(self, task.term, task.budget)
        if concept is None: return None # The memroy is full. The concept fails to get into the memory.

        # then process each task according to its type
        task_revised, goal_derived, answers_question, answer_quest = None, None, None, None
        if task.is_judgement:
            # revised the belief if there has been one, and try to solve question if there has been a corresponding one.
            task_revised, answers_question = self._accept_judgement(task, concept)
        elif task.is_goal:
            task_revised, belief_selected = self._accept_goal(task, concept)        
        elif task.is_question:
            # add the question to the question-table of the concept, and try to find a solution.
            answers_question = self._accept_question(task, concept)
        elif task.is_quest:
            answer_quest = self._accept_quest(task, concept)
        else:
            raise f"Invalid type {task.sentence.punct}"

        # Build the concepts corresponding to the terms of those components within the task.
        concept.accept(task, self.concepts, conceptualize=False)

        if Enable.temporal_rasoning or Enable.operation:
            # if (!task.sentence.isEternal() && !(task.sentence.term instanceof Operation)) {
            #     globalBuffer.eventInference(task, cont, false); //can be triggered by Buffer itself in the future
            # }
            raise # TODO
        
        return task_revised, goal_derived, answers_question, answer_quest
        
    
    def _accept_judgement(self, task: Task, concept: Concept):
        ''''''
        belief_revised = None
        answers = None
        if Enable.operation: raise # InternalExperienceBuffer.handleOperationFeedback(task, nal);
        if Enable.anticipation: raise # ProcessAnticipation.confirmAnticipation(task, concept, nal);
        
        # j1: Judgement = task.sentence
        belief: Belief = concept.match_belief(task.sentence)
        if belief is not None:
            # j2: Judgement = belief.sentence
            if revisible(task, belief):
                if Enable.temporal_rasoning:
                    '''
                    nal.setTheNewStamp(newStamp, oldStamp, nal.time.time());
                    final Sentence projectedBelief = oldBelief.projection(nal.time.time(), newStamp.getOccurrenceTime(), concept.memory);
                    
                    if (projectedBelief!=null) {
                        nal.setCurrentBelief(projectedBelief);
                        revision(judg, projectedBelief, concept, false, nal);
                        task.setAchievement(calcTaskAchievement(task.sentence.truth, projectedBelief.truth));
                    }
                    '''
                    raise
                belief_revised = local__revision(task, belief) # TODO: handling the stamps
                # reduce priority by achieving level
                task.reduce_budget_by_achieving_level(belief)
                
        if task.budget.is_above_thresh:
            '''final int nnq = concept.questions.size();
            for (int i = 0; i < nnq; i++) {
                trySolution(judg, concept.questions.get(i), nal, true);
            }
            final int nng = concept.desires.size();
            for (int i = 0; i < nng; i++) {
                trySolution(judg, concept.desires.get(i), nal, true);
            }'''
            concept.add_belief(task)

            # try to solve questions
            answers = self._solve_judgement(task, concept)

        
        return belief_revised, answers 
    

    def _accept_question(self, task: Task, concept: Concept):
        ''''''        
        concept.question_table.add(task, 0.5)

        if task.is_query: 
            answers = self._solve_query(task, concept)
        else: 
            answers = self._solve_question(task, concept)
        
        return answers


    def _accept_goal(self, task: Task, concept: Concept):
        ''''''
        desire_revised = None
        belief_selected = None
        if Enable.operation: raise # InternalExperienceBuffer.handleOperationFeedback(task, nal);
        if Enable.anticipation: raise # ProcessAnticipation.confirmAnticipation(task, concept, nal);
        
        g1: Goal = task.sentence
        desire: Desire = concept.match_desire(g1)
        if desire is not None:
            g2: Goal = desire.sentence
            if revisible(task, desire):
                # TODO: Temporal projection
                desire_revised = local__revision(task, desire) # TODO: handling the stamps
                # reduce priority by achieving level
                task.reduce_budget_by_achieving_level(desire)                
                
        if task.budget.is_above_thresh:
            '''
            for (final Task iQuest : concept.quests ) {
                trySolution(task.sentence, iQuest, nal, true);
            }
            if (beliefT != null) {
                // check if the Goal is already satisfied (manipulate budget)
                trySolution(beliefT.sentence, task, nal, true);
            }
            '''
            
            # 1. try to solve questions

            # 2. try to solve quests


            concept.add_desire(task)
        
        return desire_revised, belief_selected


    def _accept_quest(self, task: Task, concept: Concept):
        ''''''
        concept.quest_table.add(task, 0.5)

        if task.is_query: 
            answers = self._solve_query(task, concept)
        else: 
            answers = self._solve_quest(task, concept)
        
        return answers


    def _solve_judgement(self, belief: Task, concept: Concept):
        '''
        It should be ensured that the task has no query-variables.

        Args:
            task (Task): Its sentence should be a judgement.
            concept (Concept): The concept corresponding to the task.
        '''
        answers = []
        # 1. try to solve yn-questions
        for question in concept.question_table:
            answer = solution_question(question, belief)
            if answer is not None: answers.append(answer)
        # 2. try to solve wh-questions
        sub_terms = belief.term.sub_terms
        for sub_term in sub_terms:
            concept_term: Concept = self.concepts.take_by_key(sub_term, remove=False)
            if concept_term is None: continue
            task_link: TaskLink
            for task_link in concept_term.task_links:
                query = task_link.target
                if query is None: continue
                if not query.is_query: continue
                if not query.term.equal(belief.term): continue
                answer = solution_query(query, belief)
                if answer is not None: answers.append(answer)

        return answers



    def _solve_question(self, question: Task, concept: Concept):
        '''
        Args:
            task (Task): Its sentence should be a question.
            concept (Concept): The concept corresponding to the task.
        '''
        answers = []
        # 1. try to solve yn-questions
        belief_answer: Belief = concept.match_belief(question.sentence)
        if belief_answer is not None:
            answer = solution_question(question, belief_answer)
            if answer is not None: answers.append(answer)
        return answers
        

    def _solve_query(self, query: Task, concept: Concept):
        '''
        Args:
            task (Task): Its sentence should be a question or a quest and contains query-variable(s).
            concept (Concept): The concept corresponding to the task.
        '''
        answers = []
        # 1. try to solve wh-questions
        if query.is_question:
            sub_terms = query.term.sub_terms
            for sub_term in sub_terms:
                if sub_term.is_qvar: continue
                concept_term: Concept = self.concepts.take_by_key(sub_term, remove=False)
                if concept_term is None: continue
                task_link: TaskLink
                for task_link in concept_term.task_links:
                    concept_target: Concept = self.concepts.take_by_key(task_link.target.term, False)
                    if concept_target is None: continue
                    if not query.term.equal(concept_target.term): continue
                    subst = unification__var_const(query.term, concept_target.term, [], [])
                    if not subst.is_qvar_valid: continue
                    # if not (concept_target.term.equal(query.term) and subst is not None): continue
                    for belief in concept_target.belief_table:
                        answer = solution_query(query, belief)
                        if answer is not None: answers.append(answer)
            pass
        elif query.is_quest:
            pass
        else: raise "Invalid case."
        return answers


    def _solve_goal(self, task: Task, concept: Concept):
        '''
        Args:
            task (Task): Its sentence should be a goal.
            concept (Concept): The concept corresponding to the task.
        '''


    def _solve_quest(self, task: Task, concept: Concept):
        '''
        Args:
            task (Task): Its sentence should be a quest.
            concept (Concept): The concept corresponding to the task.
        '''
        answers = []
        return answers

        
    def take(self, remove=True) -> Concept:
        '''
        Take out a concept according to priority.
        '''
        return self.concepts.take(remove)

    def take_by_key(self, key: Task, remove=True) -> Concept:
        return self.concepts.take_by_key(key, remove)

    def put(self, concept: Concept):
        return self.concepts.put(concept)
    
    def put_back(self, concept: Concept):
        return self.concepts.put_back(concept)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: #items={len(self.concepts)}, #buckets={len(self.concepts.levels)}>"
    
    def __len__(self) -> int:
        return len(self.concepts)