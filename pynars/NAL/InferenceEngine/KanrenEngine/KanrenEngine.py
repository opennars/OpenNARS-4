from .util import *

class KanrenEngine:
    
    def __init__(self):
        
        with open(f'{Path(__file__).parent}/nal-rules.yml', 'r') as file:
            config = yaml.safe_load(file)

        nal1_rules = split_rules(config['rules']['nal1'])
        nal2_rules = split_rules(config['rules']['nal2'])
        nal3_rules = split_rules(config['rules']['nal3'])

        nal5_rules = split_rules(config['rules']['nal5'])

        conditional_syllogistic = split_rules(config['rules']['conditional_syllogistic'])

        higher_order = []
        
        # NAL5 includes higher order variants of NAL1-3 rules
        for rule in (nal1_rules + nal2_rules):
            # replace --> with ==> in NAL1 & NAL2
            rule = rule.replace('-->', '==>')
            # replace <-> with <=> in NAL2
            rule = rule.replace('<->', '<=>')

            higher_order.append(rule)

        # save subset for backward inference
        self.rules_backward = [convert(r, True) for r in nal1_rules + nal2_rules 
                               + higher_order 
                               + conditional_syllogistic
                               ]
        
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
                
                higher_order.append(rule)
        
        rules = nal1_rules + nal2_rules + nal3_rules + nal5_rules + higher_order + conditional_syllogistic

        self.rules_syllogistic = [convert(r) for r in rules]

        self.rules_immediate = [convert_immediate(r) for r in split_rules(config['rules']['immediate'])]

        self.rules_conditional_compositional = [convert(r, True) for r in split_rules(config['rules']['conditional_compositional'])]

        self.theorems = [convert_theorems(t) for t in split_rules(config['theorems'])]


    #################################################

    @cache_notify
    def backward(self, q: Sentence, t: Sentence) -> list:
        results = []

        lq = logic(q.term)
        lt = logic(t.term)

        for rule in self.rules_backward:
            res = self.apply(rule, lt, lq, backward=True)
            if res is not None:
                # TODO: what is a better way of handling this?
                if res[0].complexity > (q.term.complexity + t.term.complexity):
                    continue
                (p1, p2, c) = rule[0]
                sub_terms = term(p1).sub_terms | term(p2).sub_terms | term(c).sub_terms
                # conclusion should not have terms from the rule like S, P, or M
                if sub_terms.isdisjoint(res[0].sub_terms):
                    r, _ = rule[1]
                    inverse = True if r[-1] == "'" else False
                    r = r.replace("'", '') # remove trailing '
                    if type(q) is Question:
                        truth = None
                    else:
                        tr1, tr2 = (q.truth, t.truth) if not inverse else (t.truth, q.truth)
                        truth = truth_functions[r](tr1, tr2)
                    results.append((res, truth))
        
        return results

    # INFERENCE (SYLLOGISTIC)
    @cache_notify
    def inference(self, t1: Sentence, t2: Sentence) -> list:
        # print(f'Inference syllogistic\n{t1}\n{t2}')
        results = []

        t1e, t2e = variable_elimination(t1.term, t2.term)

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
                conclusion = self.determine_temporal_order(t1.term, t2.term, res[0])
                results.append(((conclusion, r), truth))

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

        return results

    def apply(self, rule, l1, l2, backward = False):
        # print("\nRULE:", rule)
        (p1, p2, c), (r, constraints) = rule[0], rule[1]

        if backward:
            result = run(1, p2, eq((p1, c), (l1, l2)), *constraints)
        else:
            result = run(1, c, eq((p1, p2), (l1, l2)), *constraints)

        if result:
            conclusion = term(result[0])
            
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
    def inference_immediate(self, t: Sentence, backward=False):
        # print(f'Inference immediate\n{t}')
        results = []

        l = logic(t.term)
        for rule in self.rules_immediate:
            (p, c), (r, constraints) = rule[0], rule[1]

            if backward:
                result = run(1, p, eq(c, l), *constraints)
            else:
                result = run(1, c, eq(p, l), *constraints)

            if result:
                conclusion = term(result[0])
                truth = truth_analytic if backward else truth_functions[r](t.truth)
                results.append(((conclusion, r), truth))
            
        return results

    ##############
    # STRUCTURAL #
    ##############

    @cache_notify
    def inference_structural(self, t: Sentence, theorem):
        # print(f'Inference structural\n{t}')
        results = []

        l1 = logic(t.term, structural=True)
        (l2, sub_terms, matching_rules) = theorem
        for i in matching_rules:
            rule = rules_strong[i] 
            res = self.apply(rule, l2, l1)
            if res is not None:
                # ensure no theorem terms in conclusion
                # TODO: ensure _ is only found inside / or \
                if sub_terms.isdisjoint(res[0].sub_terms):
                    r, _ = rule[1]
                    inverse = True if r[-1] == "'" else False
                    r = r.replace("'", '') # remove trailing '
                    if type(t) is Question:
                        truth = None
                    else:
                        tr1, tr2 = (t.truth, truth_analytic) if not inverse else (truth_analytic, t.truth)
                        truth = truth_functions[r](tr1, tr2)
                    results.append((res, truth))

                    # variable introduction
                    if type(res[0]) is Statement \
                        and res[0].copula == Copula.RetrospectiveImplication \
                        or res[0].copula == Copula.PredictiveImplication:
                        common_terms = self.common_terms(res[0].subject, res[0].predicate)
                        if len(common_terms):
                            intro = self.variable_introduction(res[0], common_terms)
                            if intro != res[0]:
                                results.append(((intro, res[1]), truth))

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

                conclusion = self.determine_order(t1, t2, res[0])

                # results.append(((conclusion, r), truth))

                # variable introduction
                # TODO: handle nested statements
                # currently compound inside statement will not be handled correctly
                # see test_second_variable_introduction_induction
                prefix = '$' if conclusion.is_statement else '#'
                substitution = {logic(c, True, var_intro=True): var(prefix=prefix) for c in common}
                reified = reify(logic(conclusion, True, var_intro=True), substitution)

                conclusion = term(reified)

                results.append(((conclusion, r), truth))
        
        return results
    
    def common_terms(self, t1: Term, t2: Term):
        return set(t1.sub_terms).intersection(t2.sub_terms) - set([place_holder])
        
    def variable_introduction(self, conclusion: Term, common: set):
        prefix = '$' if conclusion.is_statement else '#'
        substitution = {logic(c, True, var_intro=True): var(prefix=prefix) for c in common}
        reified = reify(logic(conclusion, True, var_intro=True), substitution)
        conclusion = term(reified)
        return conclusion


    # TODO: refactor and merge two temporal order functions

    def determine_order(self, t1: Sentence, t2: Sentence, conclusion: Term):
        # TODO: add .temporal() functions to Compound
        # remove this condition when done
        if type(conclusion) is Statement:
            if t1.is_event and t2.is_event:
                diff = t1.stamp.t_occurrence - t2.stamp.t_occurrence
                if diff == 0:
                    conclusion = conclusion.concurrent()
                if diff > 0:
                    conclusion = conclusion.predictive()
                if diff < 0:
                    conclusion = conclusion.retrospective()
        return conclusion
    
    def determine_temporal_order(self, t1: Term, t2: Term, conclusion: Term):
        if type(conclusion) is Compound \
        and conclusion.connector == Connector.Conjunction:
            # TODO: finish this
            if type(t2) is Compound or type(t2) is Statement:
                if t2.is_predictive:
                    conclusion = conclusion.predictive()
                if t2.is_concurrent:
                    conclusion = conclusion.concurrent()

        if type(conclusion) is Statement \
        and (conclusion.copula == Copula.Equivalence \
        or conclusion.copula == Copula.Implication):

            if type(t1) is Statement \
            and type(t2) is Statement:
                
                if t1.copula.is_concurrent and t2.copula.is_concurrent:
                    # both concurrent
                    conclusion = conclusion.concurrent()

                if t1.copula.is_predictive and t2.copula.is_predictive:
                    # both predictive
                    conclusion = conclusion.predictive()

                if t1.copula.is_retrospective and t2.copula.is_retrospective:
                    # both retrospective
                    conclusion = conclusion.retrospective()

                if (t1.copula.is_concurrent and t2.copula.is_predictive) \
                or (t2.copula.is_concurrent and t1.copula.is_predictive):
                    # one concurrent, one predictive
                    conclusion = conclusion.predictive()
                
                if (t1.copula.is_concurrent and t2.copula.is_retrospective) \
                or (t2.copula.is_concurrent and t1.copula.is_retrospective):
                    # one concurrent, one retrospective
                    conclusion = conclusion.retrospective()

                terms = [] # more complex combinations require extra work

                if t1.copula.is_predictive and t2.copula.is_retrospective:
                    terms = [t1.subject, t1.predicate]
                    if t2.subject in terms:
                        idx = terms.index(t2.subject)
                        terms.insert(idx, t2.predicate)
                    if t2.predicate in terms:
                        idx = terms.index(t2.predicate)
                        terms.insert(idx + 1, t2.subject)
                elif t2.copula.is_predictive and t1.copula.is_retrospective:
                    terms = [t2.subject, t2.predicate]
                    if t1.subject in terms:
                        idx = terms.index(t1.subject)
                        terms.insert(idx, t1.predicate)
                    if t1.predicate in terms:
                        idx = terms.index(t1.predicate)
                        terms.insert(idx + 1, t1.subject)

                if conclusion.predicate in terms and conclusion.subject in terms:
                    cpi = terms.index(conclusion.predicate)
                    csi = terms.index(conclusion.subject)
                    if cpi > csi:
                        # predicate after subject
                        conclusion = conclusion.predictive()
                    else:
                        # predicate before subject
                        conclusion = conclusion.retrospective()

        return conclusion
    