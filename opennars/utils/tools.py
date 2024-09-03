import sys
from typing import Callable, List

try:
    sys.getsizeof(0)
    getsizeof = lambda x: sys.getsizeof(x)
except:
    # import resource
    getsizeof = lambda _: 1#resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = getsizeof(obj)
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])

    return size


def list_contains(base_list, obj_list):
    ''''''
    if len(base_list) < len(obj_list): return False

    obj0 = obj_list[0]
    for i, base in enumerate(base_list[:len(base_list)+1 - len(obj_list)]):
        if base == obj0:
            if base_list[i: i+len(obj_list)] == obj_list:
                return True
    return False


def rand_seed(x: int):
    import random
    random.seed(x)
    
    # import numpy as np
    # np.random.seed(x)

    # if using pytorch, set its seed!
    # # import torch
    # # torch.manual_seed(x)
    # # torch.cuda.manual_seed(x)
    # # torch.cuda.manual_seed_all(x)


find_var_with_pos: Callable[[list, list, List[list]], list] = lambda pos_search, variables, positions: [var for var, pos in zip(variables, positions) if pos[:len(pos_search)] == pos_search] # find those variables with a common head of position. e.g. pos_search=[0], variables=[1, 1, 2, 2], and positions=[[0, 2, 0, 0], [0, 2, 1, 0], [0, 3, 0], [1, 0]], then return [1, 1, 2]
find_pos_with_pos: Callable[[list, List[list]], list] = lambda pos_search, positions: [pos for pos in positions if pos[:len(pos_search)] == pos_search]

find_pos_with_var: Callable[[int, list, List[list]], list] = lambda var_search, variables, positions: [pos for var, pos in zip(variables, positions) if var == var_search]