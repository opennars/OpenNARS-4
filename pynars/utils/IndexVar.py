from copy import deepcopy
from typing import Union
import enum
from typing import Callable, List, Tuple, Type
from ordered_set import OrderedSet
from bidict import bidict

from numpy import prod

class IntVar:
    def __init__(self, num: int) -> None:
        self.num = int(num)
    
    def __eq__(self, o: Type['IntVar']) -> bool:
        if isinstance(o, IntVar): return self.num == o.num  
        else: return self.num == o
    
    def __int__(self) -> bool:
        return self.num

    def __hash__(self) -> int:
        return hash(self.num)

    def __repr__(self) -> str:
        return str(self.num)

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

    _positions_normalized: tuple = None
    _hash_value = None

    def __init__(self) -> None:
        self.positions_dvar = [] # the positions of each dependent variable
        self.positions_ivar = [] # the positions of each independent variable
        self.positions_qvar = [] # the positions of each query variable
        
        self.var_dependent = [] # the dependent variable in each position.
        self.var_independent = [] # the independent variable in each position.
        self.var_query = [] # the query variable in each position.

        self.dependents: List[tuple] = []

        self.names_var: bidict = bidict()


    # def add_position_ivar(self, index: int):
    #     self.positions_ivar.append(index)


    # def add_position_dvar(self, index: int):
    #     self.positions_dvar.append(index)


    # def add_position_qvar(self, index: int):
    #     self.positions_qvar.append(index)


    def add_ivar(self, index: int, name: str=None, index_var_component: Type['IndexVar']=None):
        self._add_var(self.positions_ivar, self.var_independent, index, name, index_var_component)


    def add_dvar(self, index: int, name: str=None, index_var_component: Type['IndexVar']=None):
        self._add_var(self.positions_dvar, self.var_dependent, index, name, index_var_component)


    def add_qvar(self, index: int, name: str=None, index_var_component: Type['IndexVar']=None):
        self._add_var(self.positions_qvar, self.var_query, index, name, index_var_component)


    def _add_var(self, positions: list, variables: list, index, name: str=None, index_var_component: Type['IndexVar']=None):
        positions.append(index)
        if name is not None:
            if name not in self.names_var: 
                self.names_var[name] = len(self.names_var)
            variables.append(IntVar(self.names_var[name]))
        # if index_var_component is not None:
        #     pass
        


    def normalize(self):
        '''normalize the index, so that the index is unique in terms of one statement which has variable(s).'''
        if self._positions_normalized is None:
            self._positions_normalized = (
                _normalize([int(var) for var in self.var_independent]), 
                _normalize([int(var) for var in self.var_dependent]), 
                _normalize([int(var) for var in self.var_query])
            )
        return self._positions_normalized

    @property
    def postions_normalized(self):
        return self.normalize() if self._positions_normalized is None else self._positions_normalized


    def do_hashing(self):
        # if self._positions_normalized is None: self._normalize()
        self._hash_value = hash(self.postions_normalized)
        return self._hash_value


    def __hash__(self) -> int:
        return self._hash_value if self._hash_value is not None else self.do_hashing()


    def __eq__(self, o: Type['IndexVar']) -> bool:
        return hash(self) == hash(o)

    def clone(self):
        return deepcopy(self)


def _normalize(variables):
    p1 = list(OrderedSet(variables))
    p2 = list(range(len(p1)))
    mapping = dict(zip(p1, p2))
    return tuple(mapping[p] for p in variables)