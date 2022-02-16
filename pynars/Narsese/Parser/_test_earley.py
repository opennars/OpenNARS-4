from lark import Lark
from pynars.Narsese.Parser.parser import TreeToNarsese
from pathlib import Path

filepath = Path(r'Narsese\Parser\narsese.lark')
with open(filepath, 'r') as f:
    gramma = ''.join(f.readlines())
lark = Lark(grammar=gramma, parser='lalr')
content = lark.parse(r'$0.90;0.90;0.9$ <robin-->bird>.')

lark = Lark(grammar=gramma, parser='earley')
content = lark.parse(r'$0.90;0.90;0.9$ <robin-->bird>.')


print('done.')