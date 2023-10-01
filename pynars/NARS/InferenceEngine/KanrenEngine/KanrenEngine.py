from kanren import run, eq, var
from kanren.constraints import neq, ConstrainedVar
from unification import unify, reify
from cons import cons, car, cdr

from itertools import combinations

from pynars import Narsese, Global
from pynars.Narsese import Term, Copula, Connector, Statement, Compound, Variable, VarPrefix, Sentence, Punctuation, Stamp

from pynars.NAL.Functions import *
from pynars.NARS.DataStructures import Concept, Task, TaskLink, TermLink, Judgement, Question
from pynars.NAL.Functions.Tools import project_truth, revisible
from collections import defaultdict
from typing import List

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
'TODO: need alternative syntax for decomposition
'i.e. {(--, <M --> (&, T1, T2)>). <M --> _T1>} |- (--, <M --> ((&, T1, T2) - _T1)>) .ded
{(--, <M --> (&, T2, T1)>). <M --> T1>} |- (--, <M --> T2>) .ded
{<M --> (|, T1, T2)>. (--, <M --> T1>)} |- <M --> T2> .ded
{<M --> (|, T2, T1)>. (--, <M --> T1>)} |- <M --> T2> .ded
{(--, <M --> (-, T1, T2)>). <M --> T1>} |- <M --> T2> .ded
{(--, <M --> (-, T2, T1)>). (--, <M --> T1>)} |- (--, <M --> T2>) .ded
{(--, <(|, T2, T1) --> M>). <T1 --> M>} |- (--, <T2 --> M>) .ded
{(--, <(|, T1, T2) --> M>). <T1 --> M>} |- (--, <T2 --> M>) .ded
{<(&, T2, T1) --> M>. (--, <T1 --> M>)} |- <T2 --> M> .ded
{<(&, T1, T2) --> M>. (--, <T1 --> M>)} |- <T2 --> M> .ded
{(--, <(~, T1, T2) --> M>). <T1 --> M>} |- <T2 --> M> .ded
{(--, <(~, T2, T1) --> M>). (--, <T1 --> M>)} |- (--, <T2 --> M>) .ded
{(--, (&&, T1, T2)). T1} |- (--, T2) .ded
{(--, (&&, T2, T1)). T1} |- (--, T2) .ded
{(||, T1, T2). (--, T1)} |- T2 .ded
{(||, T2, T1). (--, T1)} |- T2 .ded
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
{<(&&, S, C) ==> P>. _S} |- <((&&, S, C) - _S) ==> P> .ded

'(C ^ S) => P, M => S |- (C ^ M) => P (alternative syntax below)
{<(&&, C, S) ==> P>. <M ==> _S>} |- <(&&, ((&&, C, S) - _S), M) ==> P> .ded
{<(&&, S, C) ==> P>. <M ==> _S>} |- <(&&, ((&&, S, C) - _S), M) ==> P> .ded

'(C ^ S) => P, C => P |- S (alternative syntax below)
{<(&&, C, S) ==> P>. <_C ==> P>} |- ((&&, C, S) - _C) .abd
{<(&&, S, C) ==> P>. <_C ==> P>} |- ((&&, S, C) - _C) .abd

'(C ^ S) => P, (C ^ M) => P |- M => S (alternative syntax below)
{<(&&, C, S) ==> P>. <(&&, _C, M) ==> P>} |- <((&&, _C, M) - C) ==> ((&&, C, S) - _C)> .abd
{<(&&, S, C) ==> P>. <(&&, _C, M) ==> P>} |- <((&&, _C, M) - C) ==> ((&&, S, C) - _C)> .abd
{<(&&, C, S) ==> P>. <(&&, M, _C) ==> P>} |- <((&&, M, _C) - C) ==> ((&&, C, S) - _C)> .abd
{<(&&, S, C) ==> P>. <(&&, M, _C) ==> P>} |- <((&&, M, _C) - C) ==> ((&&, S, C) - _C)> .abd

'{<C ==> P>. S} |- <(&&, C, S) ==> P> .ind (alternative syntax below)
{<(&&, C, M) ==> P>. (&&, S, M)} |- <(&&, C, S, M) ==> P> .ind
{<(&&, M, C) ==> P>. (&&, S, M)} |- <(&&, C, S, M) ==> P> .ind
{<(&&, C, M) ==> P>. (&&, M, S)} |- <(&&, C, S, M) ==> P> .ind
{<(&&, M, C) ==> P>. (&&, M, S)} |- <(&&, C, S, M) ==> P> .ind

'(C ^ M) => P, M => S |- (C ^ S) => P (alternative syntax below)
{<(&&, C, M) ==> P>. <_M ==> S>} |- <(&&, ((&&, C, M) - _M), S) ==> P> .ind
{<(&&, M, C) ==> P>. <_M ==> S>} |- <(&&, ((&&, M, C) - _M), S) ==> P> .ind
'''

immediate = '''
S |- (--, S) .neg
<S --> P> |- <P --> S> .cnv
<S ==> P> |- <P ==> S> .cnv
<S ==> P> |- <(--, P) ==> (--, S)> .cnt
'''

conditional_compositional = '''
{P. S} |- <S ==> P> .ind
{P. S} |- <P ==> S> .abd
{P. S} |- <S <=> P> .com
{T1. T2} |- (&&, T1, T2) .int
{T1. T2} |- (||, T1, T2) .uni
{<C ==> P>. S} |- <(&&, C, S) ==> P> .ind
'''

theorems = '''
'inheritance
<(T1 & T2) --> T1>
<T1 --> (T1 | T2)>
<(T1 - T2) --> T1>
<((/, R, _, T) * T) --> R>
<R --> ((\, R, _, T) * T)>

'similarity
<(--, (--, T)) <-> T>
<(/, (T1 * T2), _, T2) <-> T1>
<(\, (T1 * T2), _, T2) <-> T1>

'implication
<<S <-> P> ==> <S --> P>>
<<S <=> P> ==> <S ==> P>>
<(&&, S1, S2) ==> S1>
<(&&, S1, S2) ==> S2>
<S1 ==> (||, S1, S2)>
<S2 ==> (||, S1, S2)>

<<S --> P> ==> <(S | M) --> (P | M)>>
<<S --> P> ==> <(S & M) --> (P & M)>>
<<S <-> P> ==> <(S | M) <-> (P | M)>>
<<S <-> P> ==> <(S & M) <-> (P & M)>>
<<P <-> S> ==> <(S | M) <-> (P | M)>>
<<P <-> S> ==> <(S & M) <-> (P & M)>>

<<S ==> P> ==> <(S || M) ==> (P || M)>>
<<S ==> P> ==> <(S && M) ==> (P && M)>>
<<S <=> P> ==> <(S || M) <=> (P || M)>>
<<S <=> P> ==> <(S && M) <=> (P && M)>>
<<P <=> S> ==> <(S || M) <=> (P || M)>>
<<P <=> S> ==> <(S && M) <=> (P && M)>>

<<S --> P> ==> <(S - M) --> (P - M)>>
<<S --> P> ==> <(M - P) --> (M - S)>>
<<S --> P> ==> <(S ~ M) --> (P ~ M)>>
<<S --> P> ==> <(M ~ P) --> (M ~ S)>>

<<S <-> P> ==> <(S - M) <-> (P - M)>>
<<S <-> P> ==> <(M - P) <-> (M - S)>>
<<S <-> P> ==> <(S ~ M) <-> (P ~ M)>>
<<S <-> P> ==> <(M ~ P) <-> (M ~ S)>>
<<P <-> S> ==> <(S - M) <-> (P - M)>>
<<P <-> S> ==> <(M - P) <-> (M - S)>>
<<P <-> S> ==> <(S ~ M) <-> (P ~ M)>>
<<P <-> S> ==> <(M ~ P) <-> (M ~ S)>>

<<M --> (T1 - T2)> ==> (--, <M --> T2>)>
<<(T1 ~ T2) --> M> ==> (--, <T2 --> M>)>

<<S --> P> ==> <(/, S, _, M) --> (/, P, _, M)>>
<<S --> P> ==> <(\, S, _, M) --> (\, P, _, M)>>
<<S --> P> ==> <(/, M, _, P) --> (/, M, _, S)>>
<<S --> P> ==> <(\, M, _, P) --> (\, M, _, S)>>

'equivalence
<<S <-> P> <=> (&&, <S --> P>, <P --> S>)>
<<P <-> S> <=> (&&, <S --> P>, <P --> S>)>
<<S <=> P> <=> (&&, <S ==> P>, <P ==> S>)>
<<P <=> S> <=> (&&, <S ==> P>, <P ==> S>)>

<<S <-> P> <=> <{S} <-> {P}>>
<<P <-> S> <=> <{S} <-> {P}>>
<<S <-> P> <=> <[S] <-> [P]>>
<<P <-> S> <=> <[S] <-> [P]>>

<<S --> {P}> <=> <S <-> {P}>>
<<[S] --> P> <=> <[S] <-> P>>

<<(S1 * S2) --> (P1 * P2)> <=> (&&, <S1 --> P1>, <S2 --> P2>)>
<<(S1 * S2) <-> (P1 * P2)> <=> (&&, <S1 <-> P1>, <S2 <-> P2>)>
<<(P1 * P2) <-> (S1 * S2)> <=> (&&, <S1 <-> P1>, <S2 <-> P2>)>

<<S --> P> <=> <(M * S) --> (M * P)>>
<<S --> P> <=> <(S * M) --> (P * M)>>
<<S <-> P> <=> <(M * S) <-> (M * P)>>
<<S <-> P> <=> <(S * M) <-> (P * M)>>
<<P <-> S> <=> <(M * S) <-> (M * P)>>
<<P <-> S> <=> <(S * M) <-> (P * M)>>


<<(T1 * T2) --> R> <=> <T1 --> (/, R, _, T2)>>
<<(T1 * T2) --> R> <=> <T2 --> (/, R, T1, _)>>
<<R --> (T1 * T2)> <=> <(\, R, _, T2) --> T1>>
<<R --> (T1 * T2)> <=> <(\, R, T1, _) --> T2>>

<<S1 ==> <S2 ==> S3>> <=> <(S1 && S2) ==> S3>>

<(--, (S1 && S2)) <=> (||, (--, S1), (--, S2))>
<(--, (S1 && S2)) <=> (&&, (--, S1), (--, S2))>
<(--, (S2 && S1)) <=> (||, (--, S1), (--, S2))>
<(--, (S2 && S1)) <=> (&&, (--, S1), (--, S2))>

<<S1 <=> S2> <=> <(--, S1) <=> (--, S2)>>
<<S2 <=> S1> <=> <(--, S1) <=> (--, S2)>>

'not in the NAL book but a nice to have
<<T1 --> (/, R, _, T2)> <=> <T2 --> (/, R, T1, _)>>
'''

def split_rules(rules: str) -> List[str]:
    lines = []
    for line in rules.splitlines():
        if len(line) and not (line.startswith("'") or line.startswith("#")):
            lines.append(line)
    return lines

def parse(narsese: str, rule=False):
    task = Narsese.parser.parse(narsese)
    return task.term if rule else task.sentence


class KanrenEngine:

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
        'dif': Truth_difference,

        'neg': Truth_negation,
        'cnv': Truth_conversion,
        'cnt': Truth_contraposition
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

        self.rules_strong = [] # populated by the line below for use in structural inference
        
        self.rules_syllogistic = [self._convert(r) for r in rules]

        self.rules_immediate = [self._convert_immediate(r) for r in split_rules(immediate)]

        self.rules_conditional_compositional = [self._convert(r, True) for r in split_rules(conditional_compositional)]

        self.theorems = [self._convert_theorems(t) for t in split_rules(theorems)]


    #################################################
    ### Conversion between Narsese and miniKanren ###
    #################################################

    def _convert(self, rule, conditional_compositional=False):
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
        # filter out combinations like (_C, C) allowing them to be the same
        cond = lambda x, y: x.token.replace('_', '') != y.token.replace('_', '')
        constraints = [neq(c[0], c[1]) for c in var_combinations if cond(c[0], c[1])]

        if not conditional_compositional: # conditional compositional rules require special treatment
            if r.replace("'", '') in ['ded', 'ana', 'res', 'int', 'uni', 'dif']:
                self.rules_strong.append(((p1, p2, c), (r, constraints)))

        return ((p1, p2, c), (r, constraints))
    
    def _convert_immediate(self, rule):
        # convert to logical form
        premise, conclusion = rule.split(" |- ")
        conclusion = conclusion.split(" .")
        c = conclusion[0]
        r = conclusion[1]

        # TODO: can we parse statements instead?
        p = parse(premise+'.', True)
        c = parse(c+'.', True)

        self._variables.clear() # clear scratchpad

        p = self.logic(p, True)
        c = self.logic(c, True)
        
        var_combinations = list(combinations(self._variables, 2))
        # filter out combinations like (_C, C) allowing them to be the same
        cond = lambda x, y: x.token.replace('_', '') != y.token.replace('_', '')
        constraints = [neq(c[0], c[1]) for c in var_combinations if cond(c[0], c[1])]

        return ((p, c), (r, constraints))
    
    def _convert_theorems(self, theorem):
        # TODO: can we parse statements instead?
        t = parse(theorem+'.', True)
        l = self.logic(t, True, True, prefix='_theorem_')
        sub_terms = set(t.sub_terms)
        return (l, sub_terms)

    def logic(self, term: Term, rule=False, substitution=False, var_intro=False, structural=False, prefix='_rule_'):
        if term.is_atom:
            name = prefix+term.word if rule else term.word
            if type(term) is Variable:
                vname = term.word + term.name
                name = prefix+vname if rule else vname 
                if rule and not substitution: # collect rule variable names
                    self._variables.add(var(name))
                return var(name) if not structural else term
            if rule and not substitution: # collect rule variable names
                self._variables.add(var(name))
            return var(name) if rule else term
        if term.is_statement:
            return cons(term.copula, *[self.logic(t, rule, substitution, var_intro, structural, prefix) for t in term.terms])
        if term.is_compound:
            # when used in variable introduction, treat single component compounds as atoms
            if rule and var_intro and len(term.terms) == 1 \
                and term.connector is Connector.ExtensionalSet \
                or term.connector is Connector.IntensionalSet:
                    name = prefix+term.word
                    return var(name)
            
            # extensional and intensional images are not composable
            if term.connector is Connector.ExtensionalImage \
                or term.connector is Connector.IntensionalImage:
                return cons(term.connector, *[self.logic(t, rule, substitution, var_intro, structural, prefix) for t in term.terms])

            terms = list(term.terms)
            multi = []
            while len(terms) > 2:
                t = terms.pop(0)
                multi.append(self.logic(t, rule, substitution, var_intro, structural, prefix))
                multi.append(term.connector)
            multi.extend(self.logic(t, rule, substitution, var_intro, structural, prefix) for t in terms)
            
            return cons(term.connector, *multi)

    def term(self, logic):
        if type(logic) is Term:
            return logic
        if type(logic) is Variable:
            return logic
        if type(logic) is var or type(logic) is ConstrainedVar:
            name = logic.token.replace('_rule_', '').replace('_theorem_', '')
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
                is_list = type(t) is cons and not (type(car(t)) is Copula or type(car(t)) is Connector)
                terms = self.to_list(cdr(logic)) if is_list else [self.term(t)]
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
                    if difference is not None and difference != -1:
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
            if predicate.is_compound and difference is not None and difference != -1: # already failed one check
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
        if task.is_judgement and not task.immediate_structural_rules_applied: # TODO: handle other cases
            Global.States.record_premises(task)

            results = []#self.inference_immediate(task.sentence)

            # results.extend(self.inference_structural(task.sentence))

            for term, truth in results:
                # TODO: how to properly handle stamp for immediate rules?
                stamp_task: Stamp = task.stamp

                if task.is_judgement: # TODO: hadle other cases
                    # TODO: calculate budget
                    budget = Budget_forward(truth, task_link.budget, None)
                    sentence_derived = Judgement(term[0], stamp_task, truth)
                    task_derived = Task(sentence_derived, budget)
                    # set flag to prevent repeated processing
                    task_derived.immediate_structural_rules_applied = True
                    # normalize the variable indices
                    task_derived.term._normalize_variables()
                    tasks_derived.append(task_derived)

            # record immediate rule application for task
            task.immediate_structural_rules_applied = True

        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False

        for _ in range(len(concept.term_links)): # TODO: should limit max number of links to process
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            term_link: TermLink = concept.term_links.take(remove=True)
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

            results = self.inference(task.sentence, belief.sentence)

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

    def inference(self, t1: Sentence, t2: Sentence) -> list:
        results = []

        t1e = self._variable_elimination(t1.term, t2.term)
        t2e = self._variable_elimination(t2.term, t1.term)

        # TODO: what about other possibilities?
        t1t = t1e[0] if len(t1e) else t1.term
        t2t = t2e[0] if len(t2e) else t2.term

        l1 = self.logic(t1t)
        l2 = self.logic(t2t)
        for rule in self.rules_syllogistic:
            res = self.apply(rule, l1, l2)
            if res is not None:
                r, _ = rule[1]
                inverse = True if r[-1] == "'" else False
                r = r.replace("'", '') # remove trailing '
                tr1, tr2 = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
                truth = self._truth_functions[r](tr1, tr2)
                results.append((res, truth))

        return results

    def apply(self, rule, l1, l2):
        # print("\nRULE:", rule)
        (p1, p2, c), (r, constraints) = rule[0], rule[1]

        result = run(1, c, eq((p1, p2), (l1, l2)), *constraints)
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

    def inference_immediate(self, t: Sentence):
        results = []

        l = self.logic(t.term)
        for rule in self.rules_immediate:
            (p, c), (r, constraints) = rule[0], rule[1]

            result = run(1, c, eq(p, l), *constraints)
            # print(result)

            if result:
                conclusion = self.term(result[0])
                # print(conclusion)
                truth = self._truth_functions[r](t.truth)
                results.append(((conclusion, r), truth))
            
        return results
    
    def inference_structural(self, t: Sentence):
        results = []

        l1 = self.logic(t.term, structural=True)
        for (l2, sub_terms) in self.theorems:
            for rule in self.rules_strong:
                res = self.apply(rule, l1, l2)
                if res is not None:
                    # ensure no theorem terms in conclusion
                    if sub_terms.isdisjoint(res[0].sub_terms):
                        r, _ = rule[1]
                        inverse = True if r[-1] == "'" else False
                        r = r.replace("'", '') # remove trailing '
                        tr1, tr2 = (t.truth, truth_analytic) if not inverse else (truth_analytic, t.truth)
                        truth = self._truth_functions[r](tr1, tr2)
                        results.append((res, truth))

        return results
    
    '''variable introduction'''
    def inference_compositional(self, t1: Sentence, t2: Sentence):
        results = []
        
        common = set(t1.term.sub_terms).intersection(t2.term.sub_terms)

        if len(common) == 0:
            return results
        
        l1 = self.logic(t1.term)
        l2 = self.logic(t2.term)
        for rule in self.rules_conditional_compositional:
            res = self.apply(rule, l1, l2)
            if res is not None:
                prefix = '$' if res[0].is_statement else '#'
                substitution = {self.logic(c, True, var_intro=True): var(prefix=prefix) for c in common}
                reified = reify(self.logic(res[0], True, var_intro=True), substitution)

                conclusion = self.term(reified)

                r, _ = rule[1]
                tr1, tr2 = (t1.truth, t2.truth)
                truth = self._truth_functions[r](tr1, tr2)

                results.append(((conclusion, r), truth))
        
        return results


#################################################
### EXAMPLES ###

engine = KanrenEngine()

t1 = parse('<(&&,<$y --> lock>,<$x --> key>) ==> <$y --> (/,open,$x,_)>>. %1.00;0.81%').term
t2 = parse('<(&&,<$2 --> lock>,<$1 --> key>) ==> <$2 --> (/,open,$1,_)>>. %1.00;0.81%').term

print(t1.identical(t2)) # True

# convert to logic and then back to term
_t1 = engine.term(engine.logic(t1))

print(_t1.equal(t1)) # True

print(_t1.identical(t2)) # False


vars_all = defaultdict(lambda: len(vars_all))

def create_var(name, prefix: VarPrefix):
    vars_all[name]
    var = Variable(prefix, name)
    idx = vars_all[name]
    if prefix is VarPrefix.Independent:
        var._vars_independent.add(idx, [])
    if prefix is VarPrefix.Dependent:
        var._vars_dependent.add(idx, [])
    if prefix is VarPrefix.Query:
        var._vars-quit.add(idx, [])
    return var

t1m = Statement(Compound(Connector.Conjunction, 
                         Statement(create_var('y', VarPrefix.Independent), Copula.Inheritance, Term('lock')),
                         Statement(create_var('x', VarPrefix.Independent), Copula.Inheritance, Term('key'))),
                Copula.Implication,
                Statement(create_var('y', VarPrefix.Independent), Copula.Inheritance, 
                          Compound.ExtensionalImage(Term('open'), create_var('x', VarPrefix.Independent), Term('_', True))))

print('\n---\n', t1m.identical(t1))

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