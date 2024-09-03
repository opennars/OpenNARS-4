from pathlib import Path
from typing import Any, Callable, Iterable, List, Tuple, Union
from collections import OrderedDict


from sparse_lut import SparseLUT
from opennars.Config import Enable

from opennars.utils.Print import print_out, PrintType

import time
from datetime import datetime
import sty


class RuleMap:
    match_rule: Callable
    def __init__(self, build=True, add_rules={1,2,3,4,5,6,7,8,9}, name: str='LUT', root_rules: str=None):
        self.name = name
        self.root_rules = root_rules
        pass


    def init_type(self, *slots: Tuple[object, str, int]):
        '''
        slots (List[Tuple[object, str, int]]): each slot is filled in with the type, which is a int number, of an object.
        '''
        self.structure = OrderedDict([(slot[0], tuple(slot[1:])) for slot in slots])
        shape = tuple([n_type for *_, n_type in slots])
        self.map = SparseLUT(shape)
        pass


    def build(self, clear=True):
        name_cache = self.name
        root_path = Path(__file__).parent
        def check_update():
            if self.root_rules is None: return True

            cache_path = root_path/f'{name_cache}.pkl'
            try:
                if not cache_path.exists(): return True
                # this_filepath = Path(__file__)
                filepaths = Path(self.root_rules).glob("NAL*.py")
                mtime_cache = datetime.fromtimestamp(cache_path.stat().st_mtime)
                for filepath in filepaths:
                    mtime_this = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mtime_this > mtime_cache:
                        return True
                return False
            except: 
                if not cache_path.exists(): return True
                else: return False
                
        if check_update():
            self.rebuild(root_path, clear)
        else:
            self.load(str(root_path))

        # if Enable.debug: out_print(PrintType.INFO, f'The size of map: {get_size(self.map.lut)/1024/1024:.6f}MB')
        
    def load(self, root_path: str):
        if Enable.debug: print_out(PrintType.INFO, f'Loading RuleMap <{self.name}.pkl>...')
        t_start = time.time()
        self.map.load(str(root_path), self.name)
        t_end = time.time()
        if Enable.debug: print_out(PrintType.INFO, f'Done. Time-cost: {t_end-t_start}s.')

    def rebuild(self, root_path: str, clear=True):
        ''''''
        if Enable.debug: print_out(PrintType.INFO, f'Building RuleMap <{self.name}.pkl>...')
        t_start = time.time()
        self.map.build(clear)
        t_end = time.time()
        if Enable.debug: print_out(PrintType.INFO, f'Done. Time-cost: {t_end-t_start}s.')
        if Enable.debug: print_out(PrintType.INFO, f'Saving RuleMap...')
        self.map.dump(str(root_path), self.name)
        if Enable.debug: print_out(PrintType.INFO, f'Done.')


    def draw(self, show_labels=True):
        self.map.draw(show_labels)

    def diagnose(self, indices):
        '''
        Given a `indices`, check whether a valid rule can be retrieved.
        If not, return the index of the position where an error occurs.
        Else, return None.
        In each case, Prompt message is printed.
        '''
        for i in range(1,len(indices)):
            if self.map[indices[:i]] is None:
                name_str, (name_type, _) = list(self.structure.items())[i]
                print(f"{sty.fg.blue}Diagnose: {sty.fg.red}ERROR.\n    {sty.fg.blue}{i}: {sty.ef.bold}{name_str}, {name_type}{sty.rs.all}")
                
                return i
        print(f"{sty.fg.blue}Diagnose: {sty.fg.green}PASS.{sty.rs.all}")
        return None


    def __repr__(self) -> str:
        '''print self.type_map'''
        r = f"<RuleMap: #rules={len(self.map)}>\n"
        for key, item in self.structure.items():
            r += f"    {key}, {item}\n"
        return r
    
    def __getitem__(self, item: Iterable):
        return self.map[tuple(item)]


if __name__ == '__main__':
    root_path = Path(__file__).parent
    rulemap = RuleMap(build=False)
    rulemap.rebuild(root_path)
