from .util import *

class KanrenEngine:
    
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
            # replace --> with ==> and <-> with <=> in NAL3 (except difference)
            if '(-,' not in rule and '(~,' not in rule:
                rule = rule.replace('-->', '==>')
                rule = rule.replace('<->', '<=>')
                
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
    @cache_notify
    def inference(self, t1: Sentence, t2: Sentence, common: Term) -> list:
        # print(f'Inference syllogistic\n{t1}\n{t2}')
        results = []

        t1e, t2e = variable_elimination(t1.term, t2.term, common)

        # TODO: what about other possibilities?
        t1t = t1e[0] if len(t1e) else t1.term
        t2t = t2e[0] if len(t2e) else t2.term

        if t1t != t1.term:
            results.append(((t1t, ''), t1.truth))
        if t2t != t2.term:
            results.append(((t2t, ''), t2.truth))

        l1 = logic(t1t)
        l2 = logic(t2t)

        # temporal = t1.tense is not Tense.Eternal and t2.tense is not Tense.Eternal
        # print(temporal)
        # t0 = time()
        for rule in self.rules_syllogistic:
        
            # if temporal:
            #     c = term(rule[0][2])
            #     if type(c) is Statement \
            #         and (c.copula == Copula.Implication):

            #         (p1, p2, _), (r, constraints) = rule[0], rule[1]

            #         if t1.stamp.t_occurrence < t2.stamp.t_occurrence:
            #             c.copula = Copula.RetrospectiveImplication
            #         else:
            #             c.copula = Copula.PredictiveImplication
                    
            #         rule = ((p1, p2, logic(c, True)), (r, constraints))
                    
            res = self.apply(rule, l1, l2)
            if res is not None:
                r, _ = rule[1]
                inverse = True if r[-1] == "'" else False
                r = r.replace("'", '') # remove trailing '
                tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
                truth = truth_functions[r](tr1, tr2)
                results.append((res, truth))

            # r, _ = rule[1]
            # inverse = True if r[-1] == "'" else False
            # r = r.replace("'", '') # remove trailing '
            
            # res = self.apply(rule, l1, l2)
            # if res is not None:
            #     # print(res)
            #     tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
            #     truth = truth_functions[r](tr1, tr2)
            #     results.append((res, truth))

            # inverse = not inverse # try swapping the premises
            # res = self.apply(rule, l2, l1)
            # if res is not None:
            #     # print(res)
            #     tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
            #     truth = truth_functions[r](tr1, tr2)
            #     results.append((res, truth))
            
            # x = int((time()-t0)*1000)
            # if x > 100:
            #     print(rule)

            # t0 = time()

        return results

    def apply(self, rule, l1, l2):
        # print("\nRULE:", rule)
        (p1, p2, c), (r, constraints) = rule[0], rule[1]
        result = run(1, c, eq((p1, p2), (l1, l2)), *constraints)

        if result:
            # t0 = time()
            conclusion = term(result[0])
            # print('--', time()-t0)
            # print(conclusion)
            
            # apply diff connector
            difference = diff(conclusion)
            # print(difference)

            # sanity check - single variable is not a valid conclusion
            if type(conclusion) is Variable or type(conclusion) is cons \
                or type(difference) is Variable or type(difference) is cons:
                return None
            
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
    
    @cache_notify
    def inference_immediate(self, t: Sentence):
        # print(f'Inference immediate\n{t}')
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
        # print(f'Inference structural\n{t}')
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

    @cache_notify
    def inference_compositional(self, t1: Sentence, t2: Sentence):
        # print(f'Inference compositional\n{t1}\n{t2}')
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