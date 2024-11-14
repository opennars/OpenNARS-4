from opennars.NAL.InferenceEngine import IfStatementEngine
from typing import Literal
from opennars.Narsese import Task, Sentence
from opennars.NARS.DataStructures import Concept, TaskLink, TermLink, Task
from opennars import Global
from opennars.NARS.InferenceEngine.GeneralEngine import GeneralEngine as IndexedEngine

class InferenceEngine:
    def __init__(self, engine: Literal["IfStatementEngine", "IndexedEngine"]=None):
        if engine is None: # default engine. Now only IfStatementEngine is available
            engine = 'IfStatementEngine'

        match engine:
            case 'IfStatementEngine':
                self.engine = IfStatementEngine
            case 'IndexedEngine':
                self.engine = IndexedEngine()
                self.step = self.engine.step
            case _:
                raise RuntimeError(f"Unknown inference engine: {engine}")
        
    def step(self, concept: Concept) -> list[Task]:
        ''''''
        tasks_derived = []

        # Based on the selected concept, take out a task and a belief for further inference.
        task_link_valid: TaskLink = concept.task_links.take(remove=True)
        if task_link_valid is None: return tasks_derived
        concept.task_links.put_back(task_link_valid)

        task: Task = task_link_valid.target

        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False
        for _ in range(len(concept.term_links)):
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            term_link: TermLink = concept.term_links.take(remove=True)
            term_links.append(term_link)

            
            concept_target: Concept = term_link.target

            if not task_link_valid.novel(term_link, Global.time):
                for belief in concept_target.belief_table:
                    if belief is None: break
                    elif not task_link_valid.novel_belief(belief, Global.time):
                        continue
                    else: break
                else:
                    belief = None
                if belief is None:
                    continue
            else:
                belief = concept_target.get_belief() 
        term_link_valid = term_link

        budget_tasklink = task_link_valid.budget
        budget_termlink = term_link_valid.budget if term_link_valid is not None else None
        if task is not None and belief is not None:
            new_tasks = self.engine.inference(task, belief, concept.term, budget_tasklink, budget_termlink)

            if term_link_valid is not None:
                # reward the termlink
                for new_task in new_tasks:
                    reward: float = max(new_task.budget.priority, task.achieving_level())
                    term_link_valid.reward_budget(reward)

            tasks_derived.extend(new_tasks)

        for term_link in term_links: concept.term_links.put_back(term_link)

        return tasks_derived

                

