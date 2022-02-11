import operator
from typing import Callable, Dict, List
from copy import copy
from ordered_set import OrderedSet
from copy import deepcopy

class SparseLUT:
    ''''''
    def __init__(self, shape: tuple) -> None:
        self.shape = tuple(shape)
        self.lut = dict()
        self.depth = len(shape) - 1

    def _slice_to_tuple(self, s: slice, depth: int):
        
        n = self.shape[depth]
        start = 0 if s.start is None else s.start
        stop = n if s.stop is None else s.stop
        step = 1 if s.step is None else s.step
        range_slice = range(start, stop, step)
        if s == slice(None): range_slice = (*range_slice, None) 
        
        return range_slice

    def _set_value(self, current_index: List[int], lut_dict: dict, index, value, slot_match=None, match_key: Callable=None, ret=None):
        ''''''
        ret = dict() if ret is None else ret

        val_lut: list = lut_dict.get(index, None)
        if match_key is not None:
            if match_key(val_lut, slot_match):
                lut_dict[index] = value
            else:
                content = ret.get(id(val_lut), None)
                if content is None:
                    content = (val_lut, [])
                    ret[id(val_lut)] = content
                content[1].append(current_index)

        else: 
            lut_dict[index] = value
        return ret

    def _setitem_slice(self, current_index: List[int], lut: dict, value: object, range_slice: list, indices: tuple, depth: int, slot_match=None, match_key=None, ret=None, is_updating=False):
        ret = dict() if ret is None else ret

        if depth == self.depth:
            for index in range_slice:
                current_index.append(index)
                ret = self._set_value(current_index, lut, index, value, slot_match, match_key, ret)
        else:           
            # TODO: There seems a bug
            current_index.append(tuple(range_slice))
            range_slice = iter(range_slice)
            index = next(range_slice)
            if not is_updating:
                lut_next = lut.get(index, None)
                if lut_next is None: 
                    lut_next = dict()
                    lut[index] = (True, lut_next)
                else:
                    lut_next = lut_next[1]
            else:
                lut_next = dict()
                lut[index] = (True, lut_next)
            self._setitem(current_index, lut_next, value, indices, depth+1, slot_match, match_key, ret)
            for index in range_slice:
                lut[index] = (True, lut_next)
        return ret



    def _setitem(self, current_index: List[int], lut: dict, value: object, indices: tuple, depth: int, slot_match=None, match_key=None, ret=None, is_updating=False):
        ''''''
        ret = dict() if ret is None else ret

        for depth, index in enumerate(indices[depth:], depth):
            if depth == self.depth:
                if isinstance(index, int): 
                    current_index.append(index)
                    ret = self._set_value(current_index, lut, index, value, slot_match, match_key, ret)
                elif isinstance(index, slice):
                    range_slice = self._slice_to_tuple(index, depth)
                    for index in range_slice:
                        curr_idx = copy(current_index)
                        curr_idx.append(index)
                        ret = self._set_value(curr_idx, lut, index, value, slot_match, match_key, ret)
                elif isinstance(index, list):
                    index_ = index
                    for index in index_:
                        curr_idx = copy(current_index)
                        curr_idx.append(index)
                        ret = self._set_value(curr_idx, lut, index, value, slot_match, match_key, ret)
            else:
                if isinstance(index, int):
                    current_index.append(index)
                    lut_next = lut.get(index, None)
                    if not is_updating:
                        if lut_next is None: 
                            lut_next = dict()
                            lut[index] = (False, lut_next)
                        else:
                            lut_next = lut_next[1]
                    else:
                        if lut_next is not None:
                            is_shared_item, lut_next = lut_next
                        if lut_next is None or is_shared_item:
                            lut_next = dict()
                            lut[index] = (False, lut_next)
                    lut = lut_next
                elif isinstance(index, slice):
                    range_slice = self._slice_to_tuple(index, depth)
                    self._setitem_slice(current_index, lut, value, range_slice, indices, depth, slot_match, match_key, ret, is_updating=is_updating)
                    break
                elif isinstance(index, list):
                    self._setitem_slice(current_index, lut, value, index, indices, depth, slot_match, match_key, ret, is_updating=is_updating)
                    break
        return ret
        


    def __setitem__(self, indices: tuple, value):
        indices = tuple(index if index is not None else slice(None) for index in indices)
        self._setitem([], self.lut, value, indices, 0, is_updating=True)

    def add(self, rule, indices: tuple):
        value = OrderedSet([rule])
        indices = tuple(index if index is not None else slice(None) for index in indices)
        ret = self._setitem([], self.lut, value, indices, 0, None, operator.is_)
        slots = list(ret.values())
        for slot, indices in slots: 
            indices: list
            slot: OrderedSet = deepcopy(slot)
            indices = [set(index) for index in zip(*indices)]
            indices_ = tuple(list(index)[0] if len(index) <= 1 else list(index) for index in indices)
            indices = []
            for index in indices_:
                if isinstance(index, int):
                    indices.append(index)
                elif isinstance(index, tuple):
                    index = list(index)
                    indices.append(index)
                elif isinstance(index, list):
                    index_ = index
                    index = []
                    for idx in index_:
                        if isinstance(idx, int) or idx is None:
                            index.append(idx)
                        elif isinstance(idx, tuple):
                            raise "Invalid case."
                            index.extend(idx)
                        else: raise "Invalid case."
                    index = list(set(index))
                    indices.append(index)
                else: raise "Invalid case."

            slot.add(rule)
            self[indices] = slot
        return 
        
        
        
    def get(self, indices: tuple):
        lut = self.lut
        for index in indices[:-1]:
            lut = lut.get(index, None)
            if lut is None: return None
            lut = lut[1]
        index = indices[-1]
        return lut.get(index, None)

    def __getitem__(self, indices: tuple):
        if isinstance(indices, int): indices = (indices,)
        return self.get(indices)

    def __repr__(self) -> str:
        return repr(self.lut)