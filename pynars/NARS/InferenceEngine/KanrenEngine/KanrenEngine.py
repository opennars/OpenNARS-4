from .util import *

class KanrenEngine:

    _inference_time_avg = 0
    _run_count = 0
    _structural_time_avg = 0

    def __init__(self):
        
        with open(f'{Path(__file__).parent}/nal-rules.yml', 'r') as file:
            config = yaml.safe_load(file)

        # print(config['rules'])
        # for level, rules in config['rules'].items():
        #     print(level)
        #     for rule in split_rules(rules):
        #         print(rule)

        nal1_rules = split_rules(config['rules']['nal1'])
        nal2_rules = split_rules(config['rules']['nal2'])
        nal3_rules = split_rules(config['rules']['nal3'])

        nal5_rules = split_rules(config['rules']['nal5'])
        
        # NAL5 includes higher order variants of NAL1-3 rules
        for rule in (nal1_rules + nal2_rules):
            # replace --> with ==> in NAL1 & NAL2
            rule = rule.replace('-->', '==>')
            # replace <-> with <=> in NAL2
            rule = rule.replace('<->', '<=>')

            nal5_rules.append(rule)

        for rule in nal3_rules:
            # replace --> with ==> in NAL3 (except difference)
            if '(-,' not in rule and '(~,' not in rule:
                rule = rule.replace('-->', '==>')
                
                # replace | with || in NAL3 (except difference)
                if '||' not in rule:
                    parts = rule.split(' |- ')
                    parts = (part.replace('|', '||') for part in parts)
                    rule = ' |- '.join(parts)
                
                # replace & with && in NAL3 (except difference)
                if '&&' not in rule:
                    rule = rule.replace('&', '&&')
                
                nal5_rules.append(rule)
        
        rules = nal1_rules + nal2_rules + nal3_rules + nal5_rules
        
        self.rules_syllogistic = [convert(r) for r in rules]

        self.rules_immediate = [convert_immediate(r) for r in split_rules(config['rules']['immediate'])]

        self.rules_conditional_compositional = [convert(r, True) for r in split_rules(config['rules']['conditional_compositional'])]

        self.theorems = [convert_theorems(t) for t in split_rules(config['theorems'])]


    #################################################

    # INFERENCE (SYLLOGISTIC)

    def inference(self, t1: Sentence, t2: Sentence) -> list:
        results = []

        t1e = variable_elimination(t1.term, t2.term)
        t2e = variable_elimination(t2.term, t1.term)

        # TODO: what about other possibilities?
        t1t = t1e[0] if len(t1e) else t1.term
        t2t = t2e[0] if len(t2e) else t2.term

        l1 = logic(t1t)
        l2 = logic(t2t)
        for rule in self.rules_syllogistic:
            res = self.apply(rule, l1, l2)
            if res is not None:
                r, _ = rule[1]
                inverse = True if r[-1] == "'" else False
                r = r.replace("'", '') # remove trailing '
                tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
                truth = truth_functions[r](tr1, tr2)
                results.append((res, truth))

        return results

    def apply(self, rule, l1, l2):
        # print("\nRULE:", rule)
        (p1, p2, c), (r, constraints) = rule[0], rule[1]

        result = run(1, c, eq((p1, p2), (l1, l2)), *constraints)
        # print(result)

        if result:
            conclusion = term(result[0])
            # print(conclusion)
            # apply diff connector
            difference = diff(conclusion)
            if difference == None:
                # print("Rule application failed.")
                return None
            elif difference == -1:
                # print(conclusion) # no diff application
                return (conclusion, r)
            else:
                # print(difference) # diff applied successfully
                return (difference, r)
        else:
            # print("Rule application failed.")
            return None


    #############
    # IMMEDIATE #
    #############
        
    def inference_immediate(self, t: Sentence):
        results = []

        l = logic(t.term)
        for rule in self.rules_immediate:
            (p, c), (r, constraints) = rule[0], rule[1]

            result = run(1, c, eq(p, l), *constraints)

            if result:
                conclusion = term(result[0])
                truth = truth_functions[r](t.truth)
                results.append(((conclusion, r), truth))
            
        return results

    ##############
    # STRUCTURAL #
    ##############

    @cache_notify
    def inference_structural(self, t: Sentence, theorems = None):
        results = []

        if not theorems:
            theorems = self.theorems

        l1 = logic(t.term, structural=True)
        for (l2, sub_terms) in theorems:
            for rule in rules_strong:
                res = self.apply(rule, l2, l1)
                if res is not None:
                    # ensure no theorem terms in conclusion
                    # TODO: ensure _ is only found inside / or \
                    if sub_terms.isdisjoint(res[0].sub_terms):
                        r, _ = rule[1]
                        inverse = True if r[-1] == "'" else False
                        r = r.replace("'", '') # remove trailing '
                        tr1, tr2 = (t.truth, truth_analytic) if not inverse else (truth_analytic, t.truth)
                        truth = truth_functions[r](tr1, tr2)
                        results.append((res, truth))

        return results
    
    #################
    # COMPOSITIONAL #
    #################

    def inference_compositional(self, t1: Sentence, t2: Sentence):
        results = []
        
        common = set(t1.term.sub_terms).intersection(t2.term.sub_terms)

        if len(common) == 0:
            return results
        
        l1 = logic(t1.term)
        l2 = logic(t2.term)
        for rule in self.rules_conditional_compositional:
            res = self.apply(rule, l1, l2)
            if res is not None:
                r, _ = rule[1]
                tr1, tr2 = (t1.truth, t2.truth)
                truth = truth_functions[r](tr1, tr2)

                results.append(((res[0], r), truth))

                # variable introduction
                prefix = '$' if res[0].is_statement else '#'
                substitution = {logic(c, True, var_intro=True): var(prefix=prefix) for c in common}
                reified = reify(logic(res[0], True, var_intro=True), substitution)

                conclusion = term(reified)

                results.append(((conclusion, r), truth))
        
        return results



#################################################

    # INFERENCE STEP -- TODO: Move to Reasoner class

    def step(self, concept: Concept):
        '''One step inference.'''
        tasks_derived = []

        Global.States.record_concept(concept)
        
        # Based on the selected concept, take out a task and a belief for further inference.
        task_link: TaskLink = concept.task_links.take(remove=True)
        
        if task_link is None: 
            return tasks_derived
        
        concept.task_links.put_back(task_link)

        task: Task = task_link.target

        # inference for single-premise rules
        if task.is_judgement and not task.immediate_rules_applied: # TODO: handle other cases
            Global.States.record_premises(task)

            results = []

            results.extend(self.inference_immediate(task.sentence))

            for term, truth in results:
                # TODO: how to properly handle stamp for immediate rules?
                stamp_task: Stamp = task.stamp

                if task.is_judgement: # TODO: hadle other cases
                    # TODO: calculate budget
                    budget = Budget_forward(truth, task_link.budget, None)
                    budget.priority = budget.priority * 1/term[0].complexity
                    sentence_derived = Judgement(term[0], stamp_task, truth)
                    task_derived = Task(sentence_derived, budget)
                    # set flag to prevent repeated processing
                    task_derived.immediate_rules_applied = True
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

            # record immediate rule application for task
            task.immediate_rules_applied = True


        self._run_count += 1


        ### STRUCTURAL

        if task.is_judgement: #and not task.structural_rules_applied: # TODO: handle other cases
            Global.States.record_premises(task)

            results = []

            t0 = time()
            theorems = []
            for _ in range(5):
                theorem = concept.theorems.take(remove=True)
                theorems.append(theorem)
            
            for theorem in theorems:
                # print(term(theorem._theorem))
                # results.extend(self.inference_structural(task.sentence))
                res, cached = self.inference_structural(task.sentence, tuple([theorem._theorem]))
                # print(res)
                # print("")
                if not cached:
                    if res:
                        new_priority = theorem.budget.priority + 0.3
                        theorem.budget.priority = min(0.99, new_priority)
                    else:
                        new_priority = theorem.budget.priority - 0.3
                        theorem.budget.priority = max(0.1, new_priority)

                concept.theorems.put(theorem)

                results.extend(res)
            t1 = time() - t0
            self._structural_time_avg += (t1 - self._structural_time_avg) / self._run_count
            # print("structural: ", 1 // self._structural_time_avg, "per second")
            # for r in results:
            #     print(r, r[0][0].complexity)
            # print(task.budget.priority)
            # print(task_link.budget.priority)
            for term, truth in results:
                # TODO: how to properly handle stamp for structural rules?
                stamp_task: Stamp = task.stamp

                if task.is_judgement: # TODO: hadle other cases
                    # TODO: calculate budget
                    budget = Budget_forward(truth, task_link.budget, None)
                    budget.priority = budget.priority * 1/term[0].complexity
                    sentence_derived = Judgement(term[0], stamp_task, truth)
                    task_derived = Task(sentence_derived, budget)
                    # task_derived.structural_rules_applied = True
                    
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

            # record structural rule application for task
            # task.structural_rules_applied = True

        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False
        n = len(concept.term_links)
        t0 = time()
        iter = 0
        for _ in range(len(concept.term_links)): # TODO: should limit max number of links to process
            iter += 1
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            _t = time()
            term_link: TermLink = concept.term_links.take(remove=True)
            # print(round((time() - _t)*1000, 2))
            term_links.append(term_link)

            if not task_link.novel(term_link, Global.time):
                continue
            
            concept_target: Concept = term_link.target
            belief = concept_target.get_belief() # TODO: consider all beliefs.
            
            if belief is None: 
                continue
            
            if task == belief:
                # if task.sentence.punct == belief.sentence.punct:
                #     is_revision = revisible(task, belief)
                continue
            # TODO: currently causes infinite recursion with variables
            # elif task.term.equal(belief.term): 
            #     # TODO: here
            #     continue
            elif not belief.evidential_base.is_overlaped(task.evidential_base):
                term_link_valid = term_link
                is_valid = True
                break

        t1 = time() - t0
        loop_time = round(t1 * 1000, 2)
        # if loop_time > 20:
        #     print("hello")
        # print(iter, '/', n, "- loop time", loop_time, is_valid)
        # print(is_valid, "Concept", concept.term)
        if is_valid \
            and task.is_judgement: # TODO: handle other cases
            
            Global.States.record_premises(task, belief)
            
            # Temporal Projection and Eternalization
            if belief is not None:
                # TODO: Handle the backward inference.
                if not belief.is_eternal and (belief.is_judgement or belief.is_goal):
                    truth_belief = project_truth(task.sentence, belief.sentence)
                    belief = belief.eternalize(truth_belief)
                    # beleif_eternalized = belief # TODO: should it be added into the `tasks_derived`?

            t0 = time()

            results = self.inference(task.sentence, belief.sentence)

            t1 = time() - t0

            # print("inf:", 1 // t1, "per second")

            self._inference_time_avg += (t1 - self._inference_time_avg) / self._run_count

            # print("avg:", 1 // self._inference_time_avg, "per second")

            results.extend(self.inference_compositional(task.sentence, belief.sentence))

            # print(">>>", results)

            for term, truth in results:
                stamp_task: Stamp = task.stamp
                stamp_belief: Stamp = belief.stamp
                stamp = Stamp_merge(stamp_task, stamp_belief)

                # TODO: calculate budget
                budget = Budget_forward(truth, task_link.budget, term_link_valid.budget)
                sentence_derived = Judgement(term[0], stamp, truth)
                    
                task_derived = Task(sentence_derived, budget)
                # normalize the variable indices
                task_derived.term._normalize_variables()
                tasks_derived.append(task_derived)

            if term_link is not None: # TODO: Check here whether the budget updating is the same as OpenNARS 3.0.4.
                for task in tasks_derived: 
                    TermLink.update_budget(term_link.budget, task.budget.quality, belief.budget.priority if belief is not None else concept_target.budget.priority)

        for term_link in term_links: 
            concept.term_links.put_back(term_link)
        
        return list(filter(lambda t: t.truth.c > 0, tasks_derived))
    


### EXAMPLES ###

# engine = KanrenEngine()

# from time import time

# j1 = parse('<bird --> (&, animal, [flying])>.')

# t = time()
# print(
#     engine.inference_structural(j1)
# )
# print(time() - t)

# print("\n\n")

# t1 = parse('<bird-->robin>. %1.000;0.474%')
# t2 = parse('<bird-->animal>. %1.000;0.900%')
# print(engine.inference_compositional(t1, t2))

# print("\n")

# exit()
'''
# CONDITIONAL

t1 = parse('<(&&, A, B, C, D) ==> Z>.')

t2 = parse('B.') # positive example
print(engine.inference(t1, t2))

t2 = parse('U.') # negative example
print(engine.inference(t1, t2))

t2 = parse('(&&, B, C).') # complex example
print(engine.inference(t1, t2))

print('\n--NAL 5--')

t2 = parse('<U ==> B>.')
print(engine.inference(t1, t2))

t2 = parse('<B ==> Z>.')
# print(engine.inference(t1, t2))
for r in engine.inference(t1, t2):
    print(r)

t2 = parse('<U ==> B>.')
print(engine.inference(t1, t2))

print('\n----DEDUCTION')

import time
def timeit():
    t = time.time()
    engine.inference(t1, t2)
    t = time.time() - t
    print(len(engine.rules), 'rules processed in', t, 'seconds')

# DEDUCTION

t1 = parse('<bird --> animal>.')
t2 = parse('<robin --> bird>.')
print(engine.inference(t1, t2))
timeit()

print("\n\n----VARIABLE SUBSTITUTION")

# CONDITIONAL SYLLOGISTIC

print('\n--nal6.7')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<robin --> bird>.')
print(engine.inference(t1, t2))
timeit()

print('\n--nal6.8')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<tiger --> animal>.')
print(engine.inference(t1, t2))
timeit()

print('\n--nal6.12')

t1 = parse('<(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>.')
t2 = parse('<{Tweety} --> flyer>.')
print(engine.inference(t1, t2))
timeit()


# THEOREMS

print('\n\n----THEOREMS')

theorem = parse('<<$S <-> $P> ==> <$S --> $P>>.', False)

t1 = parse('<dog <-> pet>.', False)

# t2 = engine._variable_elimination(theorem, t1)[0]

# from pynars.Narsese import Base
# from pynars import Global

# t1 = Sentence(t1, Punctuation.Judgement, Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_external=False))
# t2 = Sentence(t2, Punctuation.Judgement, Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)), is_external=False))
# print(t1, t2)
print(engine.inference(theorem, t1))
'''