
from pynars.Narsese._py.Variable import VarPrefix, Variable
from pynars.Narsese._py.Sentence import Sentence, Tense
from pynars import Narsese
from pynars.Narsese import Budget
from pynars.Narsese import Compound, Connector
import unittest
from pynars.Narsese import Question, Quest, Judgement, Goal

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

class TEST_Parser(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_truthvalue(self):
        line = '<robin-->bird>. %1.0; 0.9%'
        content: Judgement = Narsese.parser.parse(line).sentence
        self.assertEqual(content.truth.f, 1.0)
        self.assertEqual(content.truth.c, 0.9)
        line = '<robin-->bird>. %0.5; 0.4%'
        content = Narsese.parser.parse(line).sentence
        self.assertEqual(content.truth.f, 0.5)
        self.assertEqual(content.truth.c, 0.4)

    def test_first_order_copula_1(self):
        line = '<robin-->bird>.'
        content = Narsese.parser.parse(line).sentence
        pass
    
    def test_higer_order_copula_1(self):
        line = '<<robin-->bird>==>P>.'
        content = Narsese.parser.parse(line).sentence
        line = '<<robin-->bird>==><robin-->animal>>.'
        content = Narsese.parser.parse(line).sentence
        pass

    def test_tense(self):
        line = '<robin-->bird>. :|:'
        content: Sentence = Narsese.parser.parse(line).sentence
        self.assertEqual(content.tense, Tense.Present)
        line = '<robin-->bird>. :/:'
        content: Sentence = Narsese.parser.parse(line).sentence
        self.assertEqual(content.tense, Tense.Future)
        line = '<robin-->bird>. :\:'
        content: Sentence = Narsese.parser.parse(line).sentence
        self.assertEqual(content.tense, Tense.Past)
        pass

    def test_compound_multi_1(self):
        line = '(&&, IsFlyer, IsSwimmer, IsSinger).'
        content = Narsese.parser.parse(line).sentence
        line = '(||, IsFlyer, IsSwimmer, IsSinger).'
        content = Narsese.parser.parse(line).sentence
        line = '(&|, IsFlyer, IsSwimmer, IsSinger).'
        content = Narsese.parser.parse(line).sentence
        line = '(&|, IsFlyer, IsSwimmer, IsSinger).'
        content = Narsese.parser.parse(line).sentence
        line = '(&/, IsFlyer, IsSwimmer, IsSinger).'
        content = Narsese.parser.parse(line).sentence
        pass

    def test_compound_multi_2(self):
        line = '<(&, flyer, swimmer, singer)-->foo>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(|, flyer, swimmer, singer)-->foo>.'
        content = Narsese.parser.parse(line).sentence
        pass
    
    def test_compound_multi_3(self): 
        line = '(IsFlyer || IsSwimmer && IsSinger).'
        # (||, IsFlyer, (&&, IsSwimmer, IsSinger)).
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertEqual(cmpd.connector, Connector.Disjunction)
        self.assertTrue(cmpd[0].word == 'IsFlyer')
        cmpd1: Compound = cmpd[1]
        self.assertEqual(cmpd1.connector, Connector.Conjunction)
        self.assertTrue(cmpd1[0].word == 'IsSwimmer')
        self.assertTrue(cmpd1[1].word == 'IsSinger')

        line = '(IsFlyer && IsSwimmer || IsSinger).'
        content = Narsese.parser.parse(line).sentence
        # (||, (&&, IsFlyer, IsSwimmer), IsSinger).
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertEqual(cmpd.connector, Connector.Disjunction)
        self.assertTrue(cmpd[1].word == 'IsSinger')
        cmpd1: Compound = cmpd[0]
        self.assertIsInstance(cmpd1, Compound)
        self.assertEqual(cmpd1.connector, Connector.Conjunction)
        self.assertTrue(cmpd1[0].word == 'IsFlyer')
        self.assertTrue(cmpd1[1].word == 'IsSwimmer')
        pass

    def test_compound_multi_4(self): 
        line = '<(*, acid, base)-->neutralization>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(acid * base)-->neutralization>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(acid, base)-->neutralization>.'
        content = Narsese.parser.parse(line).sentence
        pass

    def test_compound_multi_5(self): 
        line = '<(A*B*C*D)-->R>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(A&B&C&D)-->R>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(A|B|C|D)-->R>.'
        content = Narsese.parser.parse(line).sentence
        pass

    def test_compound_multi_6(self): 
        line = '<(A * B|C * D)-->R>.'
        content: Judgement = Narsese.parser.parse(line).sentence
        # <(*, A, (|, B, C), D)-->R>. 
        stat: Statement = content.term
        cmpd: Compound = stat.subject
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(cmpd.connector, Connector.Product)
        self.assertEqual(cmpd.count(), 3)
        cmpd1: Compound = cmpd[0]
        cmpd2: Compound = cmpd[1]
        cmpd3: Compound = cmpd[2]
        self.assertIsInstance(cmpd1, Term)
        self.assertIsInstance(cmpd2, Compound)
        self.assertIsInstance(cmpd3, Term)
        self.assertEqual(cmpd2.connector, Connector.IntensionalIntersection)

        line = '<(A&B | C&D)-->R>.'
        content = Narsese.parser.parse(line).sentence
        # <(|, (&, A, B), (&, C, D))-->R>.
        stat: Statement = content.term
        cmpd: Compound = stat.subject
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(cmpd.connector, Connector.IntensionalIntersection)
        self.assertEqual(cmpd.count(), 2)
        cmpd1: Compound = cmpd[0]
        cmpd2: Compound = cmpd[1]
        self.assertIsInstance(cmpd1, Compound)
        self.assertIsInstance(cmpd2, Compound)
        self.assertEqual(cmpd1.connector, Connector.ExtensionalIntersection)
        self.assertEqual(cmpd2.connector, Connector.ExtensionalIntersection)

        line = '<(A*B&C*D|E*F&G*H)-->R>.'
        content = Narsese.parser.parse(line).sentence
        # <(*, A, (&, B, C), (|, D, E), (&, F, G), H)-->R>.
        stat: Statement = content.term
        cmpd: Compound = stat.subject
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(cmpd.connector, Connector.Product)
        self.assertEqual(cmpd.count(), 5)
        cmpd1: Compound = cmpd[0]
        cmpd2: Compound = cmpd[1]
        cmpd3: Compound = cmpd[2]
        cmpd4: Compound = cmpd[3]
        cmpd5: Compound = cmpd[4]
        self.assertIsInstance(cmpd1, Term)
        self.assertIsInstance(cmpd2, Compound)
        self.assertIsInstance(cmpd3, Compound)
        self.assertIsInstance(cmpd4, Compound)
        self.assertIsInstance(cmpd5, Term)
        self.assertEqual(cmpd2.connector, Connector.ExtensionalIntersection)
        self.assertEqual(cmpd3.connector, Connector.IntensionalIntersection)
        self.assertEqual(cmpd4.connector, Connector.ExtensionalIntersection)
        

        pass

    def test_compound_negation(self):
        line = '(--, A).'
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(len(cmpd), 1)
        self.assertEqual(cmpd.connector, Connector.Negation)

        line = '-- A.'
        content = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(len(cmpd), 1)
        self.assertEqual(cmpd.connector, Connector.Negation)
        pass

    def test_compound_single_1(self):
        line = '(A-B).'
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(len(cmpd), 2)
        self.assertEqual(cmpd.connector, Connector.ExtensionalDifference)

        line = '(A~B).'
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(len(cmpd), 2)
        self.assertEqual(cmpd.connector, Connector.IntensionalDifference)

    def test_compound_single_2(self):
        line = '(A*B-C*D).'
        content: Judgement = Narsese.parser.parse(line).sentence
        cmpd: Compound = content.term
        self.assertIsInstance(cmpd, Compound)
        self.assertEqual(cmpd.count(), 2)
        self.assertEqual(cmpd.connector, Connector.ExtensionalDifference)

    def test_question_1(self):
        line = '<A-->B>?'
        content: Question = Narsese.parser.parse(line).sentence
        pass

    def test_quest_1(self):
        line = '<A-->B>@'
        content: Quest = Narsese.parser.parse(line).sentence
        pass

    def test_goal_1(self):
        line = '<A-->B>!'
        content: Goal = Narsese.parser.parse(line).sentence
        line = '<A-->B>! :/:'
        content: Goal = Narsese.parser.parse(line).sentence
        line = '<A-->B>! %0.9;0.9%'
        content: Goal = Narsese.parser.parse(line).sentence
        line = '<A-->B>! :/: %0.9;0.9%'
        content: Goal = Narsese.parser.parse(line).sentence
        pass

    def test_variable_1(self):
        line = '<$x-->A>.'
        content: Judgement = Narsese.parser.parse(line).sentence
        stat: Statement = content.term
        self.assertIsInstance(stat.subject, Variable)
        self.assertEqual(stat.subject.prefix, VarPrefix.Independent)
        line = '<#x-->A>.'
        content: Judgement = Narsese.parser.parse(line).sentence
        stat: Statement = content.term
        self.assertIsInstance(stat.subject, Variable)
        self.assertEqual(stat.subject.prefix, VarPrefix.Dependent)

        line = '<?1 --> (&,[red],apple)>?'
        content: Judgement = Narsese.parser.parse(line).sentence
        stat: Statement = content.term
        self.assertIsInstance(stat.subject, Variable)
        self.assertEqual(stat.subject.prefix, VarPrefix.Query)
        pass

    def test_budget_1(self):
        line = r'$0.90;0.90$ <robin-->bird>.'
        content = Narsese.parser.parse(line).sentence
        line = '$0.90;0.90$ (&&, <robin --> swimmer>, <robin --> [flying]>). %0.9%'
        content = Narsese.parser.parse(line).sentence
        pass

    def test_error_cases_1(self):
        line = '<(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>.'
        content = Narsese.parser.parse(line)
        line = '<<$1 --> num> ==> <(*,$1) --> num>>. %1.00;0.90%'
        content = Narsese.parser.parse(line)
        line = '(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))!'
        line = '(^open,{t001})!'
        content = Narsese.parser.parse(line)
        line = '<aaa --> ^open>.'
        content = Narsese.parser.parse(line)
        line = '<(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,<(*,{t001}) --> ^open>) =/> <{t001} --> [opened]>>.'
        content = Narsese.parser.parse(line)

        line = 'open(aa).'
        content = Narsese.parser.parse(line)

        line = '<<$1 --> (/,livingIn,_,{graz})> ==> <$1 --> murder>>.'
        content = Narsese.parser.parse(line)

        
        pass

    def test_error_case_2(self):
        ''''''
        term = Narsese.parse("(&&, <(&&, <#x-->bird>, <#x-->swimer>)-->#y>, <swan-->#y>).").term
        pass
    
    def test_chinese(self):
        line = '<(&, 会飞, 会游泳) <-> 会飞且会游泳>.'
        content = Narsese.parser.parse(line).sentence
        line = '<(会飞&会游泳) <-> 会飞且会游泳>.'
        content = Narsese.parser.parse(line).sentence
        pass

    # def test_list(self):
    #     line = '(#,a,b,c,d).'
    #     content = Narsese.parser.parse(line).sentence
    #     pass

if __name__ == '__main__':
    unittest.main()


