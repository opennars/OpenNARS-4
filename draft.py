from pynars.Narsese import parser, Term, Statement
from pynars.NAL.Inference import temporal__deduction_sequence_eliminate, temporal__deduction_sequence_replace, conditional__deduction

A = parser.parse("A. \n")
B = parser.parse("<A =/> B>. \n")

C = conditional__deduction(B, A)
print(1)
