from pynars.Narsese import Compound, Term, Interval

terms1 = [Term('a'), Interval(1), Interval(1), Term('b')]
terms2 = [Term('a'), Interval(2), Term('b')]

term1 = Compound.SequentialEvents(*terms1)
term2 = Compound.SequentialEvents(*terms2)

print(term1)
print(term2)
print(term1.equal(term2))