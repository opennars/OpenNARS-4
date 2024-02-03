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

        if result:
            conclusion = term(result[0])
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