from pathlib import Path
import pickle
from typing import List, Tuple, Union
from ordered_set import OrderedSet
from .branch_list import BranchList, Node
from typing import Any
from copy import deepcopy
from tqdm import tqdm
# import sty



class SparseLUT:
    shape: Tuple[int]
    depth: int
    blist: BranchList
    lut: dict
    data: list

    def __init__(self, shape: tuple) -> None:
        self.shape = tuple(shape)
        self.depth = len(self.shape) - 1
        self.blist = BranchList(shape)
        self.lut = dict()
        self.data = []
    
    def add(self, indices: Union[list, tuple], value):
        self.data.append((indices, value))
        
    
    def build(self, clear=True):
        if len(self.data) == 0: return
        for i, (indices, value) in enumerate(tqdm(self.data)):
            self.blist.add(indices, value)
        self.blist.build(OrderedSet, OrderedSet.add)
        # lut = self.lut

        def set_value(blists:List[Node], lut, i_depth=0):
            ''''''
            # if i_depth <= self.depth:
            for blist in blists:
                if i_depth < self.depth:
                    keys, blist_next = blist.index, list(blist.next_nodes.values())
                    lut_next = dict()
                    set_value(blist_next, lut_next, i_depth+1)
                    for key in keys:
                        lut[key] = lut_next
                        
                else:
                    keys, blist_next = blist.index, blist.next_nodes
                    for key in keys:
                        lut[key] = deepcopy(blist.next_nodes)
            # else:
                

        
        set_value(list(self.blist.blists[1].values()), self.lut)


        if clear: self.blist.clear()
    
    def clear(self):
        self.blist.clear()
        del self.lut
        self.lut = dict()
    

    def dump(self, root_path: str, name_cache: str='LUT'):
        with open(Path(root_path)/f'{name_cache}.pkl', 'wb') as f:
            pickle.dump((self.data, self.lut), f)
    
    def load(self, root_path: str, name_cache: str='LUT'):
        with open(Path(root_path)/f'{name_cache}.pkl', 'rb') as f:
            self.data, self.lut = pickle.load(f)

    def draw(self, show_labels=True):
        self.blist.draw(show_labels=show_labels)

    def __setitem__(self, indices: tuple, value):
        # indices = tuple(index if index is not None else slice(None) for index in indices)
        self.add(indices, value)
    
    def get(self, indices: tuple):
        '''
        each item in indices should be int, Any/None.
        '''
        lut = self.lut
        for index in indices[:-1]:
            # print(index)
            if index is Any: index = None
            lut = lut.get(index, None)
            if lut is None: return None
        index = indices[-1] if indices is not Any else None
        return lut.get(index, None)

    def __getitem__(self, indices: tuple):
        if isinstance(indices, int): indices = (indices,)
        return self.get(indices)

    def __len__(self):
        return len(self.data)