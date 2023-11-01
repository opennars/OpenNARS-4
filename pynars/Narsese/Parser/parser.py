from pynars.Narsese import Term, Judgement, Tense, Statement, Copula, Truth, Stamp, Interval
from pynars.Narsese import Base, Operator, Budget, Task, Goal, Punctuation, Question, Quest, Sentence, VarPrefix, Variable, Connector, Compound, SELF
from pathlib import Path
from datetime import datetime
from pynars import Config, Global
from collections import defaultdict

root_path = Path(__file__).parent
narsese_path = root_path/Path('./narsese.lark')


narsese_py_path = root_path/Path('./narsese_lark.py')
# get the last modified time of the file
mtime_lark = datetime.fromtimestamp(narsese_path.stat().st_mtime)
mtime_py = datetime.fromtimestamp(narsese_py_path.stat().st_mtime)
if mtime_lark > mtime_py:
    # re-generate the ``nasese_lark.py'' file
    import os
    print(f'generating [{narsese_py_path}] ...')
    os.system(f'python -m lark.tools.standalone {narsese_path} > {narsese_py_path}')

import sys
try:
    from .narsese_lark import Lark_StandAlone, Transformer, v_args, Token
except:
    print('Wrong generation.')
    exit()
inline_args = v_args(inline=True)


class TreeToNarsese(Transformer):

    k: int
    p_judgement: float
    d_judgement: float
    p_question: float
    d_question: float
    p_quest: float
    d_quest: float
    p_goal: float
    d_goal: float

    f: float
    c_judgement: float
    c_goal: float
    k: int

    temporal_window: int

    names_ivar: defaultdict
    names_dvar: defaultdict
    names_qvar: defaultdict

    @inline_args
    def task(self, *args):
        kwargs = dict(args)
        sentence: Sentence = kwargs['sentence']
        budget = kwargs.get('budget', None)
        # budget = (p, d, q)
        priority, durability, quality = budget or (None, None, None)
        if budget is None or durability is None or quality is None:
            if sentence.punct ==  Punctuation.Judgement: # judgement
                judgement: Judgement = sentence
                p = priority or self.p_judgement
                d = durability or self.d_judgement
                q = quality or Budget.quality_from_truth(judgement.truth)
            elif sentence.punct ==  Punctuation.Question: # question
                p = priority or self.p_question
                d = durability or self.d_question
                q = quality or 1.0
            elif sentence.punct ==  Punctuation.Quest: # quest
                p = priority or self.p_quest
                d = durability or self.d_quest
                q = quality or 1.0
            elif sentence.punct ==  Punctuation.Goal: # goal
                goal: Goal = sentence
                p = priority or self.p_goal
                d = durability or self.d_goal
                q = quality or Budget.quality_from_truth(goal.truth)
        else:
            p, d, q = priority, durability, quality

        budget = Budget(p, d, q)

        kwargs['sentence'] = sentence
        kwargs['budget'] = budget
        return Task(**kwargs)

    @inline_args
    def judgement(self, statement: 'Term|Statement|Compound', *args):
        statement._rebuild_vars()
        kwargs = dict(args)
        truth = kwargs.pop('truth', None)
        tense = kwargs.pop('tense', None)
        if truth is not None:
            f, c, k = truth
            if c is None:
                c = self.c_judgement
        else:
            f, c, k = self.f, self.c_judgement, self.k

        tense = Global.time + tense if tense is not None else tense
        base = Base((Global.get_input_id(),))
        kwargs['truth'] = Truth(f,c,k)
        kwargs['stamp'] =  Stamp(Global.time, tense, None, base)
        return ('sentence', Judgement(statement, **kwargs))

    @inline_args
    def question(self, statement: 'Term|Statement|Compound', *args):
        statement._rebuild_vars()
        kwargs = dict(args)
        tense = kwargs.pop('tense', None)
        tense = Global.time + tense if tense is not None else tense
        base = Base((Global.get_input_id(),))
        kwargs['stamp'] =  Stamp(Global.time, tense, None, base)
        return ('sentence', Question(statement, **kwargs))

    @inline_args
    def quest(self, statement: 'Term|Statement|Compound', *args):
        statement._rebuild_vars()
        kwargs = dict(args)
        tense = kwargs.pop('tense', None)
        tense = Global.time + tense if tense is not None else tense
        base = Base((Global.get_input_id(),))
        kwargs['stamp'] =  Stamp(Global.time, tense, None, base)
        return ('sentence', Quest(statement, **kwargs))

    @inline_args
    def goal(self, statement: 'Term|Statement|Compound', *args):
        statement._rebuild_vars()
        kwargs = dict(args)
        desire = kwargs.pop('truth', None)
        tense = kwargs.pop('tense', None)
        if desire is not None:
            f, c, k = desire
            if c is None:
                c = self.c_goal
        else:
            f, c, k = self.f, self.c_goal, self.k
        tense = Global.time + tense if tense is not None else tense
        base = Base((Global.get_input_id(),))
        kwargs['desire'] = Truth(f,c,k)
        kwargs['stamp'] =  Stamp(Global.time, tense, None, base)
        return ('sentence', Goal(statement, **kwargs))


    @inline_args
    def statement(self, term1, copula, term2):
        if copula == Copula.Instance:
            term1 = Compound(Connector.ExtensionalSet, term1, is_input=True)
            copula = Copula.Inheritance
        elif copula == Copula.Property:
            term2 = Compound(Connector.IntensionalSet, term2, is_input=True)
            copula = Copula.Inheritance
        if copula == Copula.InstanceProperty:
            term1 = Compound(Connector.ExtensionalSet, term1, is_input=True)
            term2 = Compound(Connector.IntensionalSet, term2, is_input=True)
            copula = Copula.Inheritance
        return Statement(term1, copula, term2, is_input=True)
    @inline_args
    def truth(self, f: Token, c: Token=None, k: Token=None):
        # truth : "%" frequency [";" confidence [";" k_evidence]] "%"
        f = float(f.value)
        c = float(c.value) if c is not None else None
        k = float(k.value) if k is not None else self.k
        return ('truth',(f, c, k))

    # @inline_args
    # def desire(self, truth: tuple):
    #     # desire : truth
    #     return ('desire', truth[1])

    @inline_args
    def budget(self, p: Token, d: Token=None, q: Token=None):
        # budget : "$" priority [";" durability [";" quality]] "$"
        p = float(p.value)
        d = float(d.value) if d is not None else None
        q = float(q.value) if q is not None else None
        return ('budget', (p, d, q))

    @inline_args
    def atom_term(self, word: Token):
        word = word.value
        return Term(word, is_input=True)

    @inline_args
    def op(self, word: Token):
        word = word.value
        return Operator(word)

    @inline_args
    def interval(self, word: Token):
        num = int(word.value)
        return Interval(num)

    @inline_args
    def variable_term(self, var: Variable):
        # name = var.prefix.value+var.name
        # if not name in self.names_var:
        #     idx = len(self.names_var)
        #     self.names_var[name] = idx
        # else:
        #     idx = self.names_var[name]
        # var.variables
        return var

    @inline_args
    def compound_term(self, compound):
        return compound

    @inline_args
    def statement_term(self, statement):
        return statement

    @inline_args
    def statement_operation1(self, op: Operator, *args: str):
        terms = (term for term in args)
        return Statement(Compound(Connector.Product, *terms, is_input=True), Copula.Inheritance, op, is_input=True)

    @inline_args
    def statement_operation2(self, word: Token, *args: str):
        op = word.value
        terms = (term for term in args)
        return Statement(Compound(Connector.Product, *terms, is_input=True), Copula.Inheritance, Operator(op), is_input=True)

    @inline_args
    def inheritance(self):
        return Copula.Inheritance

    @inline_args
    def similarity(self):
        return Copula.Similarity

    @inline_args
    def instance(self):
        return Copula.Instance

    @inline_args
    def property(self):
        return Copula.Property

    @inline_args
    def instance_property(self):
        return Copula.InstanceProperty

    @inline_args
    def implication(self):
        return Copula.Implication

    @inline_args
    def predictive_implication(self):
        return Copula.PredictiveImplication


    @inline_args
    def concurrent_implication(self):
        return Copula.ConcurrentImplication

    @inline_args
    def retrospective_implication(self):
        return Copula.RetrospectiveImplication

    @inline_args
    def equivalence(self):
        return Copula.Equivalence

    @inline_args
    def predictive_equivalence(self):
        return Copula.PredictiveEquivalence

    @inline_args
    def concurrent_equivalence(self):
        return Copula.ConcurrentEquivalence





    '''tense'''
    # @inline_args
    def tense_present(self, *args):
        return ('tense', 0)

    @inline_args
    def tense_future(self, *args):
        return ('tense', self.temporal_window)

    @inline_args
    def tense_past(self, *args):
        return ('tense', -self.temporal_window)

    @inline_args
    def tense_time(self, number: Token):
        return ('tense', int(number.value))


    '''multi'''
    @inline_args
    def multi_prefix(self, connector, *args):
        return Compound(connector, *args, is_input=True)

    @inline_args
    def multi_prefix_product(self, *args):
        return self.multi_prefix(Connector.Product, *args)

    @inline_args
    def multi_infix(self, expr):
        # connector = args[1] # TODO: Parse expression according to priorities of the connectors.
        # terms = [term for i, term in enumerate(args) if i%2==0]
        # return Compound(connector, *terms, is_input=True)
        return expr

    @inline_args
    def multi_prod_expr(self, *args):
        return Compound(Connector.Product, *args, is_input=True)

    @inline_args
    def multi_extint_expr(self, *args):
        return Compound(Connector.ExtensionalIntersection, *args, is_input=True)

    @inline_args
    def multi_intint_expr(self, *args):
        return Compound(Connector.IntensionalIntersection, *args, is_input=True)

    @inline_args
    def multi_parallel_expr(self, *args):
        return Compound(Connector.ParallelEvents, *args, is_input=True)

    @inline_args
    def multi_sequential_expr(self, *args):
        return Compound(Connector.SequentialEvents, *args, is_input=True)

    @inline_args
    def multi_conj_expr(self, *args):
        return Compound(Connector.Conjunction, *args, is_input=True)

    @inline_args
    def multi_disj_expr(self, *args):
        return Compound(Connector.Disjunction, *args, is_input=True)

    '''single'''
    @inline_args
    def single_prefix(self, connector, term1, term2):
        return Compound(connector, term1, term2, is_input=True)

    @inline_args
    def single_infix(self, term1, connector, term2):
        return Compound(connector, term1, term2, is_input=True)

    @inline_args
    def negation(self, connector, term):
        return Compound(connector, term, is_input=True)

    @inline_args
    def ext_image(self, connector, *args):
        return Compound(connector, *args, is_input=True)

    @inline_args
    def int_image(self, connector, *args):
        return Compound(connector, *args, is_input=True)

    '''connectors'''

    @inline_args
    def con_conjunction(self):
        return Connector.Conjunction

    @inline_args
    def con_product(self):
        return Connector.Product

    @inline_args
    def con_disjunction(self):
        return Connector.Disjunction

    @inline_args
    def con_parallel_events(self):
        return Connector.ParallelEvents

    @inline_args
    def con_sequential_events(self):
        return Connector.SequentialEvents

    @inline_args
    def con_intensional_intersection(self):
        return Connector.IntensionalIntersection

    @inline_args
    def con_extensional_intersection(self):
        return Connector.ExtensionalIntersection

    @inline_args
    def con_extensional_difference(self):
        return Connector.ExtensionalDifference

    @inline_args
    def con_intensional_difference(self):
        return Connector.IntensionalDifference

    @inline_args
    def con_int_set(self):
        return Connector.IntensionalSet

    @inline_args
    def con_ext_set(self):
        return Connector.ExtensionalSet

    @inline_args
    def con_negation(self):
        return Connector.Negation

    @inline_args
    def con_int_image(self):
        return Connector.IntensionalImage

    @inline_args
    def con_ext_image(self):
        return Connector.ExtensionalImage

    @inline_args
    def independent_var(self, term: Token):
        var = Variable(VarPrefix.Independent, term.value)
        name = var.prefix.value+var.name
        idx = self.names_ivar[name]
        var._vars_independent.add(idx, [])
        return var
    
    @inline_args
    def dependent_var(self, term: Token):
        var = Variable(VarPrefix.Dependent, term.value)
        name = var.prefix.value+var.name
        idx = self.names_dvar[name]
        var._vars_dependent.add(idx, [])
        return var
        
    @inline_args
    def query_var(self, term: Token):
        var = Variable(VarPrefix.Query, term.value)
        name = var.prefix.value+var.name
        idx = self.names_qvar[name]
        var._vars_query.add(idx, [])
        return var

    '''set'''
    @inline_args
    def set(self, connector, *terms):
        return Compound(connector, *terms, is_input=True)

    @inline_args
    def con_int_set(self):
        return Connector.IntensionalSet

    @inline_args
    def con_ext_set(self, *args):
        return Connector.ExtensionalSet

    # '''list_set'''
    # def list_set(self, terms):
    #     return Compound(Connector.List, *terms, is_input=True)


class LarkParser:
    def __init__(self) -> None:
        self.config()
        tree = TreeToNarsese()
        tree.names_ivar = defaultdict(lambda: len(tree.names_ivar)) # for variables
        tree.names_dvar = defaultdict(lambda: len(tree.names_dvar)) # for variables
        tree.names_qvar = defaultdict(lambda: len(tree.names_qvar)) # for variables
        self._parser = Lark_StandAlone(transformer=tree)
        self._tree = tree

    def config(self, config_path='./config.json'):
        Config.load(config_path)

        # budget
        TreeToNarsese.p_judgement = Config.Config.p_judgement
        TreeToNarsese.d_judgement = Config.Config.d_judgement
        TreeToNarsese.p_question = Config.Config.p_question
        TreeToNarsese.d_question = Config.Config.d_question
        TreeToNarsese.p_quest = Config.Config.p_quest
        TreeToNarsese.d_quest = Config.Config.d_quest
        TreeToNarsese.p_goal = Config.Config.p_goal
        TreeToNarsese.d_goal = Config.Config.d_goal

        # truth
        TreeToNarsese.f = Config.Config.f
        TreeToNarsese.c_judgement = Config.Config.c_judgement
        TreeToNarsese.c_goal = Config.Config.c_goal
        TreeToNarsese.k = Config.Config.k

        # temporal reasoning relative
        TreeToNarsese.temporal_window = Config.Config.temporal_duration


    def parse(self, text: str) -> Task:
        self._tree.names_ivar.clear()
        self._tree.names_dvar.clear()
        self._tree.names_qvar.clear()
        return self._parser.parse(text)

parser = LarkParser()
def parse(text: str): return parser.parse(text)

# from lark import Lark, Transformer 
# parser = Lark.open(narsese_path, parser='lalr')

# if __name__ == '__main__':
#     with open(sys.argv[1]) as f:
#         print(parser.parse(f.read()))