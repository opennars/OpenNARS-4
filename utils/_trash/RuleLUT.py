from copy import copy
from typing import Any, List
import networkx as nx
from ordered_set import OrderedSet
# import matplotlib.pyplot as plt

class RuleLUT:
    '''
    '''
    def __init__(self, shape: tuple) -> None:
        self.shape = tuple(shape)
        self._rules_list = []
        self._lut = dict() # which should be initialized in `self.build(...)`
        self.depth = len(self.shape)
        pass


    def add(self, value, indices: list):
        '''
        Each element of indices shoud be one of the following three types:
            1) int
            2) Any
            3) List[int] 
        '''
        indices = list(indices)
        
        '''Check the validation of the input param `indices`.'''
        assert len(indices) == len(self.shape)
        indices_norm = []
        for index, n_shape in zip(indices, self.shape):
            if isinstance(index, int):
                assert index < n_shape
                index = (index, )
            elif index is Any:
                index = tuple(range(n_shape))
            elif isinstance(index, list):
                for idx in index:
                    assert isinstance(idx, int)
                    assert idx < n_shape
                index = tuple(index)
            else: raise 'Invalid case.'
            indices_norm.append(index)


        '''Store it for further building. See `self.build(...)`'''
        self._rules_list.append([indices_norm, value])

    def new_graph(self, indices: list):
        def add_nodes(range_node, i_nodes, i_layer):
            for node, i_node in zip(range_node, i_nodes):
                g.add_node(node, cnt_pass=0, layer=i_layer, nodes_postedge={}, index=i_node)
            return range_node

        g = nx.DiGraph()

        nodes0 = add_nodes(range(len(indices[0])), indices[0], 0)
        nodes = nodes0
        for i_layer, i_nodes_next in enumerate(indices[1:]):
            i_layer_next = i_layer+1
            nodes_next = add_nodes(range(nodes[-1]+1, nodes[-1]+len(i_nodes_next)+1), i_nodes_next, i_layer_next)
            for node in nodes:
                for node_next, i_node_next in zip(nodes_next, i_nodes_next):
                    g.add_edge(node, node_next, cnt_pass=0, index=i_node_next)
            nodes = nodes_next

        node_root = "root"
        g.add_node(node_root, layer=-1)
        for node, i_node in zip(nodes0, indices[0]):
            g.add_edge(node_root, node, cnt_pass=0, index=i_node)

        # back-propagate the cnt_pass

        return g


    def build(self):
        '''
        given a list of indices to the rule (i.e. `self._rules_list`), build a dict (i.e. `self._rules_dict`) for further accessing.

        '''
        indices_all, values_all =  zip(*self._rules_list)

        # for indices in indices_all:
        #     g_new = self.new_graph(indices)
        #     plt.clf()
        #     pos = nx.multipartite_layout(g_new, subset_key="layer")
        #     nx.draw(g_new, pos, with_labels=True,)
        #     plt.show()
        # g_base = nx.DiGraph()

        g0 = self.new_graph(indices_all[0])
        g1 = self.new_graph(indices_all[2])



        def remove_path(g: nx.DiGraph, path: List[int]):
            pass

        def add_pass(g: nx.DiGraph, path: List[int]):
            node_current = "root"
            nodes = list(g[node_current])
            nodes_index = [node['index'] for node in g[node_current].values()]
            for index in path:
                i_node = nodes_index.index(index)
                if i_node == -1: 
                    remove_path(g, path)
                    break
                node_next = nodes[i_node]

                g.nodes[node_current]['cnt_pass'] += 1
                g.edges[node_current, node_next]['cnt_pass'] += 1

                node_current = node_next
                nodes = list(g[node_current])
                nodes_index = [node['index'] for node in g[node_current].values()]



        # 1. seperate intersectant sub-graph between g0 and g1
        indices1 = indices_all[2]
        def get_accessible(g: nx.DiGraph, node_last, indices_all: List[tuple], curr_idx: List[int], i_depth, depth, ret=None):
            ret = [] if ret is None else ret

            nodes = list(g[node_last])
            nodes_index = set(node['index'] for node in g[node_last].values())

            indices = indices_all[i_depth]
            if i_depth == depth-1:
                for index in indices:
                    if index in nodes_index: 
                        curr_idx.append(index)
                        ret.append(curr_idx)
            else:
                for index, node in zip(indices, nodes):
                    if index in nodes_index:
                        get_accessible(g, node, indices_all, curr_idx+[index], i_depth+1, depth, ret)
            return ret
        intersect = get_accessible(g0, "root", indices1, [], 0, len(indices1))


        def eliminate_path(g, path):
            for i_layer, i_node in enumerate(path):
                pass


        for path in intersect:
            pass

        pass

    def __getitem__(self, indices: tuple):
        lut = self._lut
        if isinstance(indices, int): return lut.get(indices, None)
        for index in indices[:-1]:
            lut = lut.get(index, None)
            if lut is None: return None
        index = indices[-1]
        return lut.get(index, None)
    
    def __repr__(self) -> str:
        return f'<RuleLUT: {str(self.shape)}>'


if __name__ == '__main__':
    lut = RuleLUT((5, 5, 3, 4, 5, 5))
    lut.add("A", [0, 0, 0, Any, 0, 0])
    lut.add("B", [0, 0, Any, 0, 0, 0])
    lut.add("C", [0, 0, Any, [1,2], 0, 0])
    lut.build()
    pass
