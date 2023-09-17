from kanren import run, eq, var
from unification import unify, reify
from cons import cons, car, cdr

from pynars import Narsese
from pynars.Narsese import Term, Copula, Connector, Statement, Compound, Variable, VarPrefix, Sentence

from pynars.NAL.Functions.TruthValueFunctions import *

def parse(narsese: str, rule=False):
    task = Narsese.parser.parse(narsese)
    return task.term if rule else task.sentence

class KanrenEngine:
    _all_rules = '''{<M --> P>. <S --> M>} |- <S --> P> .ded
{<P --> M>. <M --> S>} |- <P --> S> .ded'
{<M ==> P>. <S ==> M>} |- <S ==> P> .ded
{<P ==> M>. <M ==> S>} |- <P ==> S> .ded'
{<S ==> P>. S} |- P .ded
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
{<M --> P>. <M --> S>} |- <S --> P> .ind
{<M --> P>. <M --> S>} |- <P --> S> .ind'
{<M ==> P>. <M ==> S>} |- <S ==> P> .ind
{<M ==> P>. <M ==> S>} |- <P ==> S> .ind'
{<P --> M>. <S --> M>} |- <S --> P> .abd
{<P --> M>. <S --> M>} |- <P --> S> .abd'
{<P ==> M>. <S ==> M>} |- <S ==> P> .abd
{<P ==> M>. <S ==> M>} |- <P ==> S> .abd'
{<P ==> S>. S} |- P .abd
{<P --> M>. <M --> S>} |- <S --> P> .exe
{<M --> P>. <S --> M>} |- <P --> S> .exe'
{<P ==> M>. <M ==> S>} |- <S ==> P> .exe
{<M ==> P>. <S ==> M>} |- <P ==> S> .exe'
{<M --> P>. <M --> S>} |- <S <-> P> .com
{<P --> M>. <S --> M>} |- <S <-> P> .com'
{<M ==> P>. <M ==> S>} |- <S <=> P> .com
{<P ==> M>. <S ==> M>} |- <S <=> P> .com'
{<M --> P>. <S <-> M>} |- <S --> P> .ana
{<P --> M>. <S <-> M>} |- <P --> S> .ana
{<M <-> P>. <S --> M>} |- <S --> P> .ana'
{<M <-> P>. <M --> S>} |- <P --> S> .ana'
{<M ==> P>. <S <=> M>} |- <S ==> P> .ana
{<P ==> M>. <S <=> M>} |- <P ==> S> .ana
{<M <=> P>. <S ==> M>} |- <S ==> P> .ana'
{<M <=> P>. <M ==> S>} |- <P ==> S> .ana'
{S. <S <=> P>} |- P .ana
{<M --> P>. <M <-> S>} |- <S --> P> .ana
{<P --> M>. <M <-> S>} |- <P --> S> .ana
{<P <-> M>. <S --> M>} |- <S --> P> .ana'
{<P <-> M>. <M --> S>} |- <P --> S> .ana'
{<M ==> P>. <M <=> S>} |- <S ==> P> .ana
{<P ==> M>. <M <=> S>} |- <P ==> S> .ana
{<P <=> M>. <S ==> M>} |- <S ==> P> .ana'
{<P <=> M>. <M ==> S>} |- <P ==> S> .ana'
{S. <P <=> S>} |- P .ana
{<M <-> P>. <S <-> M>} |- <S <-> P> .res
{<S --> P>. <P --> S>} |- <S <-> P> .res
{<S --> P>. <P <-> S>} |- <P --> S> .res
{<M <=> P>. <S <=> M>} |- <S <=> P> .res
{<S ==> P>. <P ==> S>} |- <S <=> P> .res
{<S ==> P>. <P <=> S>} |- <P ==> S> .res
{<P <-> M>. <S <-> M>} |- <S <-> P> .res
{<M <-> P>. <M <-> S>} |- <S <-> P> .res
{<P <-> M>. <M <-> S>} |- <S <-> P> .res
{<S --> P>. <S <-> P>} |- <P --> S> .res
{<P <=> M>. <S <=> M>} |- <S <=> P> .res
{<M <=> P>. <M <=> S>} |- <S <=> P> .res
{<P <=> M>. <M <=> S>} |- <S <=> P> .res
{<S ==> P>. <S <=> P>} |- <P ==> S> .res
{<M --> T1>. <M --> T2>} |- <M --> (&, T1, T2)> .int
{<T1 --> M>. <T2 --> M>} |- <(|, T1, T2) --> M> .int
{<M ==> T1>. <M ==> T2>} |- <M ==> (&&, T1, T2)> .int
{<T1 ==> M>. <T2 ==> M>} |- <(||, T1, T2) --> M> .int
{<T1 --> T2>. <T2 --> T1>} |- (&&, <T1 --> T2>, <T2 --> T1>) .int
{<M --> T1>. <M --> T2>} |- <M --> (|, T1, T2)> .uni
{<T1 --> M>. <T2 --> M>} |- <(&, T1, T2) --> M> .uni
{<M ==> T1>. <M ==> T2>} |- <M ==> (||, T1, T2)> .uni
{<T1 ==> M>. <T2 ==> M>} |- <(&&, T1, T2) --> M> .uni
{<T1 --> T2>. <T2 --> T1>} |- (||, <T1 --> T2>, <T2 --> T1>) .uni
{<M --> T1>. <M --> T2>} |- <M --> (-, T1, T2)> .dif
{<M --> T1>. <M --> T2>} |- <M --> (-, T2, T1)> .dif'
{<T1 --> M>. <T2 --> M>} |- <(~, T1, T2) --> M> .dif
{<T1 --> M>. <T2 --> M>} |- <(~, T2, T1) --> M> .dif'
{<(&&, C, S) ==> P>. M} |- <((&&, C, S) - M) ==> P> .ded
{<(&&, C, S) ==> P>. <X ==> M>} |- <((&&, C, S) - <X ==> M>) ==> P> .ded
'''

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
        rules = self._all_rules.splitlines()
        self.rules = [self._convert(rule) for rule in rules]



    #################################################
    ### Conversion between Narsese and miniKanren ###
    #################################################

    _prefix = '_rule_'

    def logic(self, term: Term, rule=False):
        if term.is_atom:
            name = self._prefix+term.word if rule else term.word
            if type(term) is Variable:
                vname = term.word + term.name
                name = self._prefix+vname if rule else vname 
                return var(name)
            return var(name) if rule else term
        if term.is_statement:
            return cons(term.copula, *[self.logic(t, rule) for t in term.terms])
        if term.is_compound:
            return cons(term.connector, *[self.logic(t, rule) for t in term.terms])

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

        # WARNING: terrible code below :)

    ### quick and dirty example of applying diff ####

    def _diff(self, c):
        difference = -1 # result of applying diff

        if type(c) is Statement:
            if c.subject.is_compound and c.copula is Copula.Implication:
                if c.subject.connector is Connector.ExtensionalDifference:
                    if len(c.subject.terms.terms) == 2:
                        components = c.subject.terms.terms
                        l = components[0]
                        r = components[1]
                        if l.contains(r) and not l.equal(r):
                            difference = l - r
                        else:
                            difference = None

        if difference == None or difference == -1:
            return difference
        else:
            return Statement(difference, c.copula, c.predicate)

    # UNIFICATION

    def _variable_elimination(self, t1: Term, t2: Term) -> list:
        unified = filter(None, (unify(self.logic(t), self.logic(t2, True)) for t in t1.terms))
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

        p1 = self.logic(p1, True)
        p2 = self.logic(p2, True)
        c = self.logic(c, True)
        return ((p1, p2, c), r)

    def inference(self, t1: Sentence, t2: Sentence) -> list:
        results = []
        for rule in self.rules:
            res = self.apply(rule, t1.term, t2.term)
            if res is not None:
                r = rule[1]
                inverse = True if r[-1] == "'" else False
                r = r.replace("'", '') # remove trailing '
                t1t, t2t = (t1.truth, t2.truth) if not inverse else (t2.truth, t1.truth)
                truth = self._truth_functions[r](t1t, t2t)
                results.append((res, truth))
        return results

    def apply(self, rule: tuple, *args: Term):
        # print("\nRULE:", rule)
        (p1, p2, c), r = rule[0], rule[1]

        # test statements
        t1, t2 = args
        # print("Test:", t1, t2)

        # TODO: what about other possibilities?
        t1e = self._variable_elimination(t1, t2)
        t2e = self._variable_elimination(t2, t1)

        t1 = t1e[0] if len(t1e) else t1
        t2 = t2e[0] if len(t2e) else t2

        # if len(t1e) or len(t2e):
        #     print("Substituted:", t1, t2)

        # apply rule
        result = run(1, c, eq((p1, p2), (self.logic(t1), self.logic(t2))))
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


engine = KanrenEngine()

# CONDITIONAL

t1 = parse('<(&&, A, B, C, D) ==> Z>.')

t2 = parse('B.') # positive example
print(engine.inference(t1, t2))
t2 = parse('U.') # negative example
print(engine.inference(t1, t2))

t2 = parse('(&&, B, C).') # complex example
print(engine.inference(t1, t2))

# DEDUCTION

t1 = parse('<bird --> animal>.')
t2 = parse('<robin --> bird>.')
print(engine.inference(t1, t2))

print("\n\n----VARIABLE SUBSTITUTION")

# CONDITIONAL SYLLOGISTIC

print('\n--nal6.7')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<robin --> bird>.')
print(engine.inference(t1, t2))

print('\n--nal6.8')
t1 = parse('<<$x --> bird> ==> <$x --> animal>>.')
t2 = parse('<tiger --> animal>.')
print(engine.inference(t1, t2))

print('\n--nal6.12')

t1 = parse('<(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>.')
t2 = parse('<{Tweety} --> flyer>.')
print(engine.inference(t1, t2))
