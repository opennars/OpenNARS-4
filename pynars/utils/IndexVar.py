from copy import deepcopy
from typing import Union
import enum
from typing import Callable, List, Tuple, Type
from ordered_set import OrderedSet
from bidict import bidict

class IntVar:
    def __init__(self, num: int) -> None:
        self.num = int(num)
        self.parent: IntVar = None
        self.son: IntVar = None
    
    def __eq__(self, o: 'IntVar') -> bool:
        if isinstance(o, IntVar): return self.num == o.num  
        else: return self.num == o
    
    def __int__(self) -> bool:
        return self.num

    def __hash__(self) -> int:
        return hash(self.num)

    def __repr__(self) -> str:
        return f'_{self.num}'

    def __call__(self, num: Union[int, None]):
        if num is not None: self.num = int(num)
        return self

    def __gt__(self, o: Type['IntVar']):
        if isinstance(o, IntVar): o = int(o)
        return self.num > int(o)

    def __ge__(self, o: Type['IntVar']):
        if isinstance(o, IntVar): o = int(o)
        return self.num >= int(o)

    def __lt__(self, o: Type['IntVar']):
        if isinstance(o, IntVar): o = int(o)
        return self.num < int(o)

    def __le__(self, o: Type['IntVar']):
        return self.num <= int(o)

    def __ne__(self, o: Type['IntVar']):
        if isinstance(o, IntVar): o = int(o)
        return self.num != int(o)

    def __add__(self, o: Type['IntVar']):
        return self.num + o

    def __radd__(self, o: int):
        return self + o

    def __sub__(self, o: Type['IntVar']):
        return self.num - o

    def __rsub__(self, o: int):
        return -self.num + o

    def __mul__(self, o: Type['IntVar']):
        return self.num * o

    def __rmul__(self, o: Type['IntVar']):
        return o * self.num

    def __div__(self, o: Type['IntVar']):
        return self.num / o

    def __rdiv__(self, o: Type['IntVar']):
        return  o / self.num

    def __pos__(self, o: Type['IntVar']):
        return  self

    def __neg__(self, o: Type['IntVar']):
        return IntVar(-self.num)
    
    def connect(self, son: 'IntVar'):
        ''''''
        self.son = son
        son.parent = self
    
    def propagate_down(self):
        ''''''
        num = self.num
        iv = self.son
        while iv is not None:
            iv.num = num
            iv = iv.son
    
    def propagate_up(self):
        ''''''
        num = self.num
        iv = self.parent
        while iv is not None:
            iv.num = num
            iv = iv.parent
    
    # def clone(self):
    #     return IntVar(self.num)


class IndexVar:
    '''
    Examples:
        (&&, <$1-->A>, <$2-->B>, <$1-->C>)
        positions = [[0, 2], [1]]
        positions_unfolded = [[0, 2], [1]]
        variables = [0, 1, 0]

        (&&, <<$1-->A>==><$2-->B>>, <$2-->C>, <$3-->D>)
        positions = [[(0, 0)], [(0, 1), 1], [2]]
        positions_unfolded = [[0], [1, 2], [3]]
        variables = [[0, 1], 1, 2]
        variables_unfolded = [0, 1, 1, 2]
    '''

    _indices_normalized: tuple = None
    _hash_value = None

    def __init__(self) -> None:
        self.positions = [] # the positions of each dependent variable
        self.indices = [] # the dependent variable in each position.

        # self.predecessor: IndexVar = None
        self.successors: List[IndexVar] = []

        self._is_built = False


    def normalize(self):
        '''normalize the index, so that the index is unique in terms of one statement which has variable(s).'''
        if self._indices_normalized is None:
            self._indices_normalized = _normalize([int(var) for var in self.indices])
        return self._indices_normalized

    @property
    def indices_normalized(self):
        return self.normalize() if self._indices_normalized is None else self._indices_normalized


    def do_hashing(self):
        # if self._positions_normalized is None: self._normalize()
        self._hash_value = hash(self.indices_normalized)
        return self._hash_value


    def __hash__(self) -> int:
        return self._hash_value if self._hash_value is not None else self.do_hashing()


    def __eq__(self, o: Type['IndexVar']) -> bool:
        return hash(self) == hash(o)

    
    def __repr__(self) -> str:
        return f'<IndexVar: {repr(self.indices)}, {self.positions}, {self.indices_normalized}>'

    def clone(self):
        return deepcopy(self)

    
    def connect(self, successor: 'IndexVar', generate_pos=False):
        ''''''
        self.successors.append(successor)
        # successor.predecessor = self

        if not generate_pos: return

        bias_pos = len(self.successors)-1
        indices = [idx for idx in successor.indices]
        positions = [[bias_pos]+pos for pos in successor.positions]
        self.indices.extend(indices)
        self.positions.extend(positions)

    def build(self, rebuild=False):
        ''''''
        if not rebuild and self._is_built: return

        if len(self.successors) > 0:
            self.indices.clear()
            self.positions.clear()
        for bias_pos, successor in enumerate(self.successors):
            successor.build(rebuild)
            indices = [idx for idx in successor.indices]
            positions = [[bias_pos]+pos for pos in successor.positions]
            self.indices.extend(indices)
            self.positions.extend(positions)

        self._is_built = True


    def rebuild(self):
        ''''''
        self.build(rebuild=True)

    
    def add(self, idx, position):
        iv = IntVar(idx)

        if len(position) == 0:
            self.positions.clear()
            self.indices.clear()

        idxvar = self
        for pos in position:
            idxvar = idxvar.successors[pos]
        idxvar.positions.append([])
        idxvar.indices.append(iv)

        return iv


    def remove(self, position: List[int]):
        ''''''
        index = self
        for pos in position:
            index = index.successors[pos]
        index.indices.clear()
        index.positions.clear()


def _normalize(variables):
    p1 = list(OrderedSet(variables))
    p2 = list(range(len(p1)))
    mapping = dict(zip(p1, p2))
    return tuple(mapping[p] for p in variables)