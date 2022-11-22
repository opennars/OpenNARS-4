# Narsese

## Term

Import  related functions and classes:

```Python
from pynars import Narsese
from pynars.Narsese import Term, Statement, Compound, Variable, VarPrefix
```

To create a term, there are two alternatives. One is to use `parse` function, the other is to create a `Term` directly:

```Python
term1 = Narsese.parse("A.").term
term2 = Term("B")
```

The `Term` contains a `IndexVar` in order to handle variables. See sec. [IndexVar](###IndexVar)

## Statement

## Compound



### Terms


## Variable

To create an atomic variable, use the class `Variable`. The definition of `Variable` is `def __init__(self, prefix: VarPrefix, word: str, idx: int=0, do_hashing=False)`. The first argument is the prefix of the variable, `$`, `#`, or `?`. The second argument is the name of the variable. The third argument is the index of the variable, which is an integer. The index `idx` indicates the number a variable is marked, starting from $0$. For example, in the sentence `(&&, <<$x-->robin>==><$x-->bird>>, <<robin-->$y>==><bird-->$y>>, <#z-->bird>, <#z-->animal>).`, the variable `$x`'s `idx` is `0`, and the variable `#y`'s `idx` is `1`, while the `#z`'s `idx` is `0`.

```Python
var1 = Variable(VarPrefix.Independent, "x", 0)
var2 = Variable.Dependent("x", 0)
```


### IndexVar