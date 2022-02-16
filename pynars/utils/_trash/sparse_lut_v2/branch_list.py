

from ctypes import Union
from typing import Any, Callable, Dict, List, Tuple, Type, Set
import typing
from collections import OrderedDict
from copy import deepcopy, copy
import marshal
# import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from ordered_set import OrderedSet
import sty
import cython

# deepcopy = lambda x: marshal.loads(marshal.dumps(x))
deepcopy2 = lambda x: marshal.loads(marshal.dumps(x))


class Node:
    next_nodes: Union[typing.OrderedDict[tuple, 'Node'], Set]
    last_nodes: typing.OrderedDict[tuple, 'Node']
    is_end: bool
    def __init__(self, index: set, is_end=False, depth: int=-1, next_nodes: typing.OrderedDict[tuple, 'Node']=None, last_nodes: typing.OrderedDict[tuple, 'Node']=None) -> None:
        self.index = index
        self.is_end = is_end
        self.next_nodes = next_nodes or (None if is_end else OrderedDict())
        self.last_nodes= last_nodes or OrderedDict()
        self.depth = depth
        pass

    def append(self, node: Type['Node']):
        self.next_nodes[tuple(node.index)] = node
        node.last_nodes[(tuple(self.index), id(self))] = self


    def duplicate_shallow(self, index: set=None):
        node = Node(index or self.index, self.is_end, self.depth)
        for next_node in self.next_nodes_list:
            node.append(next_node)
        return node


    def duplicate_deep(self, index:set=None):
        node = Node(index or self.index, self.is_end, self.depth)
        for next_node in self.next_nodes_list:
            next_node = next_node.duplicate_deep()
            node.append(next_node)
            
        return node


    def remove_next(self, node: Type['Node']):
        ''''''
        self.next_nodes.pop(tuple(node.index), None)
        node.last_nodes.pop((tuple(self.index), id(self)), None)


    def remove_last(self, node: Type['Node']):
        ''''''
        self.last_nodes.pop((tuple(node.index), id(node)), None)
        node.next_nodes.pop(tuple(self.index), None)
    
    def reset_index(self, index):
        ''''''
        # index_old = tuple(self.index)
        next_nodes: List[Node] = self.next_nodes_list 
        last_nodes: List[Node] = self.last_nodes_list 
        for node in next_nodes: node.remove_last(self)
        for node in last_nodes: node.remove_next(self)
        self.index = index
        for node in next_nodes: self.append(node)
        for node in last_nodes: node.append(self)


    @property
    def is_fan_in(self):
        return (self.last_nodes is not None) and (len(self.last_nodes) > 1)


    @property
    def next_nodes_list(self):
        return list(self.next_nodes.values()) if self.next_nodes is not None else []

    @property
    def last_nodes_list(self):
        return list(self.last_nodes.values()) if self.last_nodes is not None else []

    def __getitem__(self, i):
        if i == 0: return self.index
        elif i == 1: return self.next_nodes
        else: return None
    

    def __setitem__(self, i, value):
        if i == 0: self.index = value
        elif i == 1: self.next_nodes = value
        else: raise "Invalid case."
    

    def __repr__(self) -> str:
        return f'<Node: {repr(self.index)} {repr(self.next_nodes)}>'


class BranchList:
    blists: Node
    def __init__(self, shape: tuple) -> None:
        self.shape = tuple(shape)

        self.blists = Node({})
        self.lists = []
        self.depth = len(self.shape) - 1

    def _normalize(self, indices: list):
        indices_norm = []
        for i, index in enumerate(indices):
            if isinstance(index, int):
                indices_norm.append(set((index,)))
            elif isinstance(index, list) or isinstance(index, tuple):
                indices_norm.append(set(index))
            elif index is Any or index is None:
                indices_norm.append(set((*range(self.shape[i]), None)))
            else:
                raise "Invalid case."
        
        return indices_norm


    def _merge(self, blists: List[Node], blist_in: List[Node], blist_last: Node=None, blist_in_last: Node=None, is_new_blist: bool=False, depth=0):
        '''merge the new indices into `self.blist`
        
        blists: all the blist under the current depth.
        blist_in: the new blist. Non-branch should be ensured.
        depth: the current depth.
        '''
        if depth == 0: # OK
            if len(blist_in) > 0: blist_in: Node = blist_in[0]
            else: return
            index_new = blist_in.index
            index_new_diff = index_new - set().union(*(blist[0] for blist in blists))
            if len(index_new_diff) > 0:
                blist_new_diff = blist_in.duplicate_deep(index_new_diff)
                blist_last.append(blist_new_diff)

            _is_new_blist = is_new_blist
            for blist in blists:
                ''''''
                is_new_blist = _is_new_blist
                # get index_common and index_old_diff.
                index_old = blist[0] # e.g. index_old = {0, 1}
                index_common = index_new & index_old
                index_old_diff = index_old - index_new
                index_new_diff = index_new - index_old
                index_new = index_new_diff
                
                if len(index_old_diff) > 0: 
                    # keep the old one
                    blist.reset_index(index_old_diff)

                    # build the new one
                    if len(index_common) > 0:
                        # BUG
                        # since the indexes of son-nodes of  `blist_last` are all different (orthogonal), the `index_common`s of the `blist`s are also different.
                        blist_in_common = blist_in.duplicate_deep(index_common)
                        # blist_in_common = Node(blist_in.index, blist_in.is_end, blist_in.depth)
                        blist_last.append(blist_in_common)
                        self._merge(blist.next_nodes_list, blist_in_common.next_nodes_list, blist, blist_in_common, True, depth+1)
                    
                else:
                    if len(index_common) > 0:
                        # needn't to build a new link
                        self._merge(blist.next_nodes_list, blist_in.next_nodes_list, blist, blist_in, False, depth+1)
                    pass

        elif 0 < depth <= self.depth:
            # if len(blist_in) > 0: blist_in: Node = blist_in[0]
            # else: return
            blist_in: Node = blist_in[0]

            # blist_in_last.next_nodes = OrderedDict() # TODO: modify the edges.

            index_new = blist_in.index
            index_new_diff = index_new - set().union(*(blist[0] for blist in blists))
            if len(index_new_diff) > 0:
                # the new one to be add
                blist_new = blist_in.duplicate_deep(index_new_diff)
                if not is_new_blist: blist_last.append(blist_new)
                else: blist_in_last.append(blist_new)

            _is_new_blist = is_new_blist
            for blist in blists:
                ''''''
                is_new_blist = _is_new_blist
                # get index_common and index_old_diff.
                index_old = blist[0] # e.g. index_old = {0, 1}
                index_common = index_new & index_old
                index_old_diff = index_old - index_new
                index_new_diff = index_new - index_old
                index_new = index_new_diff

                if blist.is_fan_in: # there are multiple input nodes.
                    # remove the blist from fan-in, and add a copied one.
                    if len(index_common) > 0:
                        blist_last.remove_next(blist)
                        blist = blist.duplicate_shallow()
                        blist_last.append(blist)

                    if len(index_old_diff) > 0: 
                        # keep the old one
                        blist_old_diff = blist
                        blist_old_diff.reset_index(index_old_diff)
                        if is_new_blist:
                            blist_in_last.append(blist_old_diff)

                        # build the new one
                        if len(index_common) > 0:
                            # since the indexes of son-nodes of  `blist_last` are all different (orthogonal), the `index_common`s of the `blist`s are also different.
                            blist_old_common = blist.duplicate_shallow(index_common)
                            blist_last.append(blist_old_common)
                            # blist_in_common = blist_in.duplicate_deep(index_common)
                            blist_in_common = Node(blist_in.index, blist_in.is_end, blist_in.depth)
                            if is_new_blist: # TODO: check here
                                blist_in_last.append(blist_in_common) # or blist_last.append(blist_in_common)?
                            else:
                                blist_last.append(blist_in_common)
                            self._merge(blist_old_common.next_nodes_list, blist_in.next_nodes_list, blist_old_common, blist_in_common, True, depth+1)
                    else: # len(index_old_diff) == 0
                        # BUG
                        if len(index_common) > 0:
                            # needn't to build a new link
                            # blist_in_common = blist_in.duplicate_shallow()
                            blist_in_common = blist_in
                            if is_new_blist:
                                blist_in_last.append(blist_in_common)
                            self._merge(blist.next_nodes_list, blist_in.next_nodes_list, blist, blist_in_common, True, depth+1)
                        pass
                    pass
                else: # not fan_in
                    if len(index_old_diff) > 0: 
                        # keep the old one
                        blist.reset_index(index_old_diff)
                        
                        if is_new_blist:
                            blist_in_last.append(blist)

                        # build the new one
                        if len(index_common) > 0:
                            # since the indexes of son-nodes of  `blist_last` are all different (orthogonal), the `index_common`s of the `blist`s are also different.
                            blist_old_common = blist.duplicate_shallow(index_common)
                            blist_last.append(blist_old_common)
                            # blist_in_common = blist_in.duplicate_deep(index_common)
                            blist_in_common = Node(blist_in.index, blist_in.is_end, blist_in.depth)
                            blist_in_last.append(blist_in_common)
                            self._merge(blist.next_nodes_list, blist_in.next_nodes_list, blist_old_common, blist_in_common, True, depth+1)
                    else:
                        # BUG
                        if len(index_common) > 0:
                            # needn't to build a new link
                            blist_in_common = blist_in.duplicate_shallow()
                            if is_new_blist:
                                blist_in_last.append(blist_in_common)
                            # if is_new_blist:
                            #     # blist_in_common = blist_in.duplicate_deep(index_common)
                            #     blist_in_common = Node(index_common, blist_in.index, blist_in.depth)
                            #     blist_in_last.append(blist_in_common)
                            # else:
                            #     blist_in_common = blist_in
                            #     # blist_in_last.append(blist_in_common)
                            self._merge(blist.next_nodes_list, blist_in.next_nodes_list, blist, blist_in_common, is_new_blist, depth+1)
                        pass
                    pass

            

        elif depth == self.depth:
            pass
        else:
            pass

    # @cython.cfunc
    def _make_blist(self, indices):
        blist_original = blist = Node(indices[0], False, 0)

        if self.depth == 0: return blist_original
        
        for i_depth, index in enumerate(indices[1:], 1):
            if i_depth == self.depth:
                blist.append(Node(index, True, i_depth))
            else:
                blist_new = Node(index, False, i_depth)
                blist.append(blist_new)
                blist = blist_new

        return blist_original


    def add(self, indices: list, value):
        indices = self._normalize(indices)
        self.lists.append((indices, value))

        if len(self.blists.next_nodes) == 0:
            self.blists.append(self._make_blist(indices))
            return 

        # Now, `self.blist` is not None
        
        blist_index = self._make_blist(indices)
        self._merge(self.blists.next_nodes_list, [blist_index], self.blists)
        pass
        
    
    def build(self, value_func: Callable=OrderedSet, add_func: Callable=OrderedSet.add): # list, OrderedSet, etc.
        # @cython.cfunc
        # @cython.returns(cython.void)
        # @cython.locals()
        def set_value_by_func(blists: List[Node], indices, value_func: Callable, depth=0):
            '''it should be ensured that `indices` is in `blists`'''
            index: set = indices[depth]
            for blist in blists:
                if index.issuperset(blist[0]):
                    if depth < self.depth:
                        set_value_by_func(list(blist[1].values()), indices, value_func, depth+1)
                    else:
                        blist[1] = value_func()

        # @cython.cfunc
        # @cython.returns()
        # @cython.locals()
        def get_value(blists, indices, depth=0, ret=None):
            '''it should be ensured that `indices` is in `blists`'''
            ret = [] if ret is None else ret
            index: set = indices[depth]
            for blist in blists:
                if index.issuperset(blist[0]):
                    if depth < self.depth:
                        get_value(list(blist[1].values()), indices, depth+1, ret)
                    else:
                        ret.append(blist[1])
            return ret

        blists = list(self.blists[1].values())
        for indices, _ in self.lists:
            set_value_by_func(blists, indices, value_func)

        for indices, value in self.lists:
            list_values = get_value(blists, indices)
            for values in list_values:
                assert values is not None
                add_func(values, value)


    def clear(self):
        ''''''
        blists = list(self.blists[1].values())
        if len(self.blists[1]) == 0: return
        for blist in blists:
            del blist
        del blists
        self.blists[1] = None


    def draw(self, blists: List[Node]=None, show_labels=True):
        ''''''
        # from matplotlib.text import Text
        blists = list(self.blists[1].values())
        if len(blists) == 0:
            print('None BranchList.')
            return
        g = nx.DiGraph()
        def add_nodes(g: nx.DiGraph, node_current, label_node_current, blists_next: List[Node], i_layer=0):
            n_node = g.number_of_nodes()
            args_next = []
            if node_current not in g:
                g.add_node(node_current, label=label_node_current, layer=i_layer)
                n_node += 1
            if i_layer <= self.depth:
                # for node, blist_next in enumerate(blists_next, n_node):
                for blist_next in blists_next:
                    label = blist_next[0]
                    node = id(blist_next)
                    g.add_node(node, label=label, layer=i_layer+1)
                    g.add_edge(node_current, node)
                    if blist_next[1] is not None and len(blist_next[1]) > 0:
                        args_next.append((node, label, (list(blist_next[1].values()) if i_layer < self.depth else blist_next[1]), i_layer+1))
                        

                for arg_next in args_next:
                    add_nodes(g, *arg_next)
            else:
                node = id(blists_next)
                g.add_node(node, label=blists_next, layer=i_layer+1)
                g.add_edge(node_current, node)
                pass

        add_nodes(g, "root", "root", blists)
        plt.clf()
        labels = {node: attr['label'] for node, attr in g.nodes.items()}
        pos = nx.multipartite_layout(g, subset_key="layer")
        if show_labels:
            labels = nx.draw_networkx_labels(g,pos, labels)
            for t in labels.values():
                t.set_rotation(30)
        nx.draw(g, pos, with_labels=False, node_size=5)
        # nx.draw(g)
        plt.show()

        pass



if __name__ == '__main__':
    blist = BranchList((4, 4, 4, 4))
    blist.add([0, 0, 0, 1], "A")
    blist.add([0, [1,2], 0, 1], "B")
    blist.add([0, 3, 0, 1], "C")
    blist.add([0, [0,1,2,3], 0, [1,2]], "D")
    blist.draw()
    blist.build()
    blist.draw()



    # blist = BranchList((3,3,3,4,3,3))
    # blist.add([0, 0, 1, 0, 2, 3])
    # blist.add([0, 0, 1, 2, 0, 1])
    # blist.add([0, 0, 2, 0, 2, 3])
    # blist.add([0, 0, [1,2], 0, [0,2], 3])

    # blist.add([0,0,0,Any,0,0])
    # blist.add([0,0,Any,[1,2],0,0])
    # all = []
    # bl = blist.blist
    # for _ in range(blist.depth):
    #     all.append(bl[0])
    #     bl = bl[1][0]
    pass


# if cython.compiled:
#     print(f"{sty.fg.blue}[BranchList]Info{sty.fg.rs}: {sty.fg.green}Cython{sty.fg.rs} version.")
# else:
#     print(f"{sty.fg.cyan}[BranchList]Warning{sty.fg.cyan}: {sty.fg.red}Python{sty.fg.red} version.")