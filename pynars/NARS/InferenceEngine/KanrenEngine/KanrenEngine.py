from kanren import run, eq, var
from kanren.constraints import neq
from unification import unify, reify
from cons import cons, car, cdr

from itertools import combinations

from pynars import Narsese
from pynars.Narsese import Term, Copula, Connector, Statement, Compound, Variable, VarPrefix, Sentence, Punctuation, Stamp

from pynars.NAL.Functions.TruthValueFunctions import *


nal1 = '''
{<M --> P>. <S --> M>} |- <S --> P> .ded
{<P --> M>. <M --> S>} |- <P --> S> .ded'
{<M --> P>. <M --> S>} |- <S --> P> .ind
{<M --> P>. <M --> S>} |- <P --> S> .ind'
{<P --> M>. <S --> M>} |- <S --> P> .abd
{<P --> M>. <S --> M>} |- <P --> S> .abd'
{<P --> M>. <M --> S>} |- <S --> P> .exe
{<M --> P>. <S --> M>} |- <P --> S> .exe'
'''

nal2 = '''
{<M <-> P>. <S <-> M>} |- <S <-> P> .res
{<M <-> P>. <M <-> S>} |- <S <-> P> .res
{<P <-> M>. <S <-> M>} |- <S <-> P> .res
{<P <-> M>. <M <-> S>} |- <S <-> P> .res
{<M --> P>. <M --> S>} |- <S <-> P> .com
{<P --> M>. <S --> M>} |- <S <-> P> .com'
{<M --> P>. <S <-> M>} |- <S --> P> .ana
{<M --> P>. <M <-> S>} |- <S --> P> .ana
{<P --> M>. <S <-> M>} |- <P --> S> .ana
{<P --> M>. <M <-> S>} |- <P --> S> .ana
{<M <-> P>. <S --> M>} |- <S --> P> .ana'
{<P <-> M>. <S --> M>} |- <S --> P> .ana'
{<M <-> P>. <M --> S>} |- <P --> S> .ana'
{<P <-> M>. <M --> S>} |- <P --> S> .ana'
'''

nal3 = '''
'composition
{<M --> T1>. <M --> T2>} |- <M --> (&, T1, T2)> .int
{<T1 --> M>. <T2 --> M>} |- <(|, T1, T2) --> M> .int
{<M --> T1>. <M --> T2>} |- <M --> (|, T1, T2)> .uni
{<T1 --> M>. <T2 --> M>} |- <(&, T1, T2) --> M> .uni
{<M --> T1>. <M --> T2>} |- <M --> (-, T1, T2)> .dif
{<M --> T1>. <M --> T2>} |- <M --> (-, T2, T1)> .dif'
{<T1 --> M>. <T2 --> M>} |- <(~, T1, T2) --> M> .dif
{<T1 --> M>. <T2 --> M>} |- <(~, T2, T1) --> M> .dif'
'decomposition
{(--, <M --> (&, T1, T2)>). <M --> T1>} |- (--, <M --> T2>) .ded
{<M --> (|, T1, T2)>. (--, <M --> T1>)} |- <M --> T2> .ded
{(--, <M --> (-, T1, T2)>). <M --> T1>} |- <M --> T2> .ded
{(--, <M --> (-, T2, T1)>). (--, <M --> T1>)} |- (--, <M --> T2>) .ded
{(--, <(|, T2, T1) --> M>). <T1 --> M>} |- (--, <T2 --> M>) .ded
{<(&, T2, T1) --> M>. (--, <T1 --> M>)} |- <T2 --> M> .ded
{(--, <(~, T1, T2) --> M>). <T1 --> M>} |- <T2 --> M> .ded
{(--, <(~, T2, T1) --> M>). (--, <T1 --> M>)} |- (--, <T2 --> M>) .ded
{(--, (&&, T1, T2)). T1} |- (--, T2) .ded
{(||, T1, T2). (--, T1)} |- T2 .ded
'''

nal5 = '''
'conditional syllogistic
{<S ==> P>. S} |- P .ded
{<P ==> S>. S} |- P .abd
{S. <S <=> P>} |- P .ana
{S. <P <=> S>} |- P .ana
{<S <=> P>. S} |- P .ana'
{<P <=> S>. S} |- P .ana'

'conditional conjunctive
'(C ^ S) => P, S |- C => P (alternative syntax below)
{<(&&, C, S) ==> P>. _S} |- <((&&, C, S) - _S) ==> P> .ded

'(C ^ S) => P, M => S |- (C ^ M) => P (alternative syntax below)
{<(&&, C, S) ==> P>. <M ==> _S>} |- <(&&, ((&&, C, S) - _S), M) ==> P> .ded

'(C ^ S) => P, C => P |- S (alternative syntax below)
{<(&&, C, S) ==> P>. <_C ==> P>} |- ((&&, C, S) - _C) .abd

'(C ^ S) => P, (C ^ M) => P |- M => S (alternative syntax below)
{<(&&, C, S) ==> P>. <(&&, _C, M) ==> P>} |- <((&&, _C, M) - C) ==> ((&&, C, S) - _C)> .abd

'{<C ==> P>. S} |- <(&&, C, S) ==> P> .ind (alternative syntax below)
{<(&&, C, M) ==> P>. (&&, S, M)} |- <(&&, C, S, M) ==> P> .ind

'(C ^ M) => P, M => S |- (C ^ S) => P (alternative syntax below)
{<(&&, C, M) ==> P>. <_M ==> S>} |- <(&&, ((&&, C, M) - _M), S) ==> P> .ind
'''

def split_rules(rules: str) -> list[str]:
    lines = []
    for line in rules.splitlines():
        if len(line) and not line.startswith("'"):
            lines.append(line)
    return lines

def parse(narsese: str, rule=False):
    task = Narsese.parser.parse(narsese)
    return task.term if rule else task.sentence


class KanrenEngine:

    _prefix = '_rule_'

    _truth_functions = {
        'ded': Truth_deduction,
        'ana': Truth_analogy,
        'res': Truth_resemblance,
        'abd': Truth_abduction,
        'ind': Truth_induction,
        'exe': Truth_exemplification,
        'com': Truth_comparison,
        'int': Truth_intersection,
        'uni': Truth_union,
        'dif': Truth_difference
    }

    def __init__(self):
        
        nal1_rules = split_rules(nal1)
        nal2_rules = split_rules(nal2)
        nal3_rules = split_rules(nal3)

        nal5_rules = split_rules(nal5)
        
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

        self._variables = set() # used as scratchpad while converting
        self.rules = [self._convert(rule) for rule in rules]


    #################################################
    ### Conversion between Narsese and miniKanren ###
    #################################################

    def _convert(self, rule):
        # convert to logical form
        premises, conclusion = rule.split(" |- ")

        p1, p2 = premises.strip("{}").split(". ")
        conclusion = conclusion.split(" .")
        c = conclusion[0]
        r = conclusion[1]

        # TODO: can we parse statements instead?
        p1 = parse(p1+'.', True)
        p2 = parse(p2+'.', True)
        c = parse(c+'.', True)

        self._variables.clear() # clear scratchpad

        p1 = self.logic(p1, True)
        p2 = self.logic(p2, True)
        c = self.logic(c, True)

        var_combinations = list(combinations(self._variables, 2))
        constraints = [neq(c[0], c[1]) for c in var_combinations]

        return ((p1, p2, c), (r, constraints))
    
    def logic(self, term: Term, rule=False, substitution=False):
        if term.is_atom:
            name = self._prefix+term.word if rule else term.word
            if type(term) is Variable:
                vname = term.word + term.name
                name = self._prefix+vname if rule else vname 
                if rule and not substitution: # collect rule variable names
                    self._variables.add(var(name))
                return var(name)
            if rule and not substitution: # collect rule variable names
                # allow variables like _C and C (used in rules) to be interchangeable
                self._variables.add(var(name.replace(self._prefix+'_', self._prefix)))
            return var(name) if rule else term
        if term.is_statement:
            return cons(term.copula, *[self.logic(t, rule, substitution) for t in term.terms])
        if term.is_compound:
            return cons(term.connector, *[self.logic(t, rule, substitution) for t in term.terms])

    def term(self, logic):
        if type(logic) is Term:
            return logic
        if type(logic) is var:
            name = logic.token.replace(self._prefix, '')
            if name[0] == '$':
                return Variable(VarPrefix.Independent, name[1:])
            if name[0] == '#':
                return Variable(VarPrefix.Dependent, name[1:])
            if name[0] == '?':
                return Variable(VarPrefix.Query, name[1:])
            else:
                return Term(name)
        if type(logic) is cons:
            if type(car(logic)) is Copula:
                sub = car(cdr(logic))
                cop = car(logic)
                pre = cdr(cdr(logic))
                return Statement(self.term(sub), cop, self.term(pre))
            if type(car(logic)) is Connector:
                con = car(logic)
                t = cdr(logic)
                terms = self.to_list(cdr(logic)) if type(t) is cons else [self.term(t)]
                return Compound(con, *terms)
        return logic # cons

    def to_list(self, pair) -> list:
        l = [self.term(car(pair))]
        if type(cdr(pair)) is list and cdr(pair) == []:
            () # empty TODO: there's gotta be a better way to check
        elif type(cdr(pair)) is cons:
            t = self.term(cdr(pair))
            if type(t) is cons:
                l.extend(self.to_list(t)) # recurse
            else:
                l.append(t)
        else:
            l.append(self.term(cdr(pair))) # atom
        return l

    #################################################
    ### quick and dirty example of applying diff ####
    #################################################

    def _diff(self, c):
        # TODO: room for improvement
        difference = -1 # result of applying diff

        def calculate_difference(l: Term, r: Term):
            return (l - r) if l.contains(r) and not l.equal(r) else None
            
        def do_diff(t: Term):
            nonlocal difference
            if len(t.terms.terms) == 2:
                components = t.terms.terms
                difference = calculate_difference(*components)


        # COMPOUND
        if type(c) is Compound and c.connector is Connector.ExtensionalDifference:
            if len(c.terms.terms) == 2:
                return calculate_difference(*c.terms.terms)

        # STATEMENT
        elif type(c) is Statement and c.copula is Copula.Implication:
            # check subject
            subject = c.subject
            if subject.is_compound:
                if subject.connector is Connector.ExtensionalDifference:
                    do_diff(c.subject)
                    if difference is not None:
                        subject = difference

                # check for nested difference
                elif subject.connector is Connector.Conjunction:
                    if len(subject.terms.terms) == 2:
                        components = subject.terms.terms
                        if components[0].is_compound:
                            if components[0].connector is Connector.ExtensionalDifference:
                                do_diff(components[0])
                                # if components[0].terms.terms[0] == components[1]:
                                #     difference = None
                                if difference is not None:
                                    subject = Compound(subject.connector, difference, components[1])

            # check predicate
            predicate = c.predicate
            if predicate.is_compound and difference is not None: # already failed one check
                if predicate.connector is Connector.ExtensionalDifference:
                    do_diff(predicate)
                    if difference is not None:
                        predicate = difference

            # check for success
            if difference == None or difference == -1:
                return difference
            else:
                return Statement(subject, c.copula, predicate)

        return -1 # no difference was applied

    # UNIFICATION

    def _variable_elimination(self, t1: Term, t2: Term) -> list:
        unified = filter(None, (unify(self.logic(t), self.logic(t2, True, True)) for t in t1.terms))
        substitution = []
        for u in unified:
            d = {k: v for k, v in u.items() if type(self.term(k)) is Variable}
            if len(d):
                substitution.append(d)
        result = []
        for s in substitution:
            reified = reify(self.logic(t1), s)
            result.append(self.term(reified))

        return result

    #################################################

    # INFERENCE

    def inference(self, t1: Sentence, t2: Sentence) -> list:
        results = []

        t1e = self._variable_elimination(t1.term, t2.term)
        t2e = self._variable_elimination(t2.term, t1.term)

        # TODO: what about other possibilities?
        t1t = t1e[0] if len(t1e) else t1.term
        t2t = t2e[0] if len(t2e) else t2.term

        for rule in self.rules:
            res = self.apply(rule, t1t, t2t)
            if res is not None:
                r, _ = rule[1]
                inverse = True if r[-1] == "'" else False
                r = r.replace("'", '') # remove trailing '
                tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
                truth = self._truth_functions[r](tr1, tr2)
                # results.append(((res, truth), self.term(rule[0][0]), self.term(rule[0][1]), self.term(rule[0][2])))
                results.append((res, truth))
        return results

    def apply(self, rule: tuple, t1: Term, t2: Term):
        # print("\nRULE:", rule)
        (p1, p2, c), (r, constraints) = rule[0], rule[1]

        result = run(1, c, eq((p1, p2), (self.logic(t1), self.logic(t2))), *constraints)
        # print(result)

        if result:
            conclusion = self.term(result[0])
            # print(conclusion)
            # apply diff connector
            difference = self._diff(conclusion)
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


#################################################

### EXAMPLES ###

engine = KanrenEngine()

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