from operator import imod
import os 
from pathlib import Path
from inspect import getmembers, isfunction
import importlib
import re
from typing import Any, List, Tuple, Union
from typing_extensions import Protocol
from collections import OrderedDict

from numpy import product

from pynars.Config import Enable
from pynars.Narsese import Copula, Task
from pynars.Narsese import Connector, Statement, Belief, Term, Truth, Compound, Budget
from ..DataStructures import LinkType, TaskLink, TermLink
from pynars.NAL.Inference import *
from pynars.utils.SparseLUT import SparseLUT
from pynars.utils.tools import get_size

from pynars.utils.Print import out_print, PrintType

import time
from datetime import datetime
import pickle
import sty
from ._extract_feature import extract_feature, _compound_has_common, _compound_at
from pynars import Global

from .Rules import *

class RuleMap:
    def __init__(self, build=True, add_rules={1,2,3,4,5,6,7,8,9}) -> None:
        n_link_types = max([t.value for t in LinkType.__members__.values()])
        n_copula = len(Copula)
        n_has_common_id = 2
        n_match_reverse = 2
        n_common_id = 4
        n_compound_common_id = 4
        n_connector = len(Connector)
        n_sentence_type = 4

        n_has_compound_common_id = 2
        n_has_at = 2
        n_has_compound_at = 2
        n_the_other_compound_has_common = 2
        n_the_other_compound_p1_at_p2 = 2
        n_the_other_compound_p2_at_p1 = 2
        n_is_belief_valid = 2
        n_at_compound_pos = 2
        n_p1_at_p2 = 2
        n_p2_at_p1 = 2

        self._init_type_map(
            ("is_belief_valid", bool, n_is_belief_valid),

            ("sentence_type", int, n_sentence_type),

            ("match_reverse", bool, n_match_reverse),

            ("LinkType1", LinkType, n_link_types),
            ("LinkType2", LinkType, n_link_types),

            ("Copula1", Copula, n_copula),
            ("Copula2", Copula, max(n_copula, n_connector)),

            ("Connector1", Connector, n_connector),
            ("Connector2", Connector, n_connector),

            ("has_compound_at", bool, n_has_compound_at),
            ("at_compound_pos", int, n_at_compound_pos),
            ("the_other_compound_has_common", bool, n_the_other_compound_has_common),
            ("the_other_compound_p1_at_p2", bool, n_the_other_compound_p1_at_p2),
            ("the_other_compound_p2_at_p1", bool, n_the_other_compound_p2_at_p1),

            
            ("compound_common_id", CommonId, n_compound_common_id),
            
            ("has_common_id", bool, n_has_common_id),
            ("has_compound_common_id", bool, n_has_compound_common_id),
            ("has_at", bool, n_has_at),
            ("p1_at_p2", bool, n_p1_at_p2),
            ("p2_at_p1", bool, n_p2_at_p1),
            ("common_id", CommonId, n_common_id),

        )
        
        add_rules__NAL1(self.map, self.structure_map) if 1 in add_rules else None
        add_rules__NAL2(self.map, self.structure_map) if 2 in add_rules else None
        add_rules__NAL3(self.map, self.structure_map) if 3 in add_rules else None
        add_rules__NAL4(self.map, self.structure_map) if 4 in add_rules else None
        add_rules__NAL5(self.map, self.structure_map) if 5 in add_rules else None
        add_rules__NAL6(self.map, self.structure_map) if 6 in add_rules else None
        add_rules__NAL7(self.map, self.structure_map) if 7 in add_rules else None
        add_rules__NAL8(self.map, self.structure_map) if 8 in add_rules else None
        add_rules__NAL9(self.map, self.structure_map) if 9 in add_rules else None

        self.build() if build else None

        
        pass


    def _init_type_map(self, *slots: Tuple[object, str, int]):
        '''
        slots (List[Tuple[object, str, int]]): each slot is filled in with the type, which is a int number, of an object.
        '''
        self.structure_map = OrderedDict([(slot[0], tuple(slot[1:])) for slot in slots])
        # self.map = np.empty([n_type for *_, n_type in slots], dtype=object) # Shape: [LinkType, LinkType, Copula, Copula, match_reverse, common_id, Connector, Connector]. It cost about 1.2GB in memory... it's too expensive. So we have to adopt a more economic way.
        shape = tuple([n_type for *_, n_type in slots])
        self.map = SparseLUT(shape)
        pass


    def build(self, clear=True):
        root_path = Path(__file__).parent
        def check_update():
            cache_path = root_path/'LUT.pkl'
            try:
                if not cache_path.exists(): return True
                this_filepath = Path(__file__)
                filepaths = (this_filepath.parent/"Rules").glob("NAL*.py")
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
            # t_start = time.time()
            # self.map.build(clear)
            # t_end = time.time()
            # self.map.dump(str(root_path))
            # if Enable.debug: out_print(PrintType.INFO, f'Building time cost: {t_end-t_start}s.')
            self.rebuild(root_path, clear)
        else:
            self.load(str(root_path))

        # if Enable.debug: out_print(PrintType.INFO, f'The size of map: {get_size(self.map.lut)/1024/1024:.6f}MB')
        
    def load(self, root_path: str):
        if Enable.debug: out_print(PrintType.INFO, f'Loading RuleMap...')
        t_start = time.time()
        self.map.load(str(root_path))
        t_end = time.time()
        if Enable.debug: out_print(PrintType.INFO, f'Done. Time-cost: {t_end-t_start}s.')

    def rebuild(self, root_path: str, clear=True):
        ''''''
        if Enable.debug: out_print(PrintType.INFO, f'Building RuleMap...')
        t_start = time.time()
        self.map.build(clear)
        t_end = time.time()
        if Enable.debug: out_print(PrintType.INFO, f'Done. Time-cost: {t_end-t_start}s.')
        if Enable.debug: out_print(PrintType.INFO, f'Saving RuleMap...')
        self.map.dump(str(root_path))
        if Enable.debug: out_print(PrintType.INFO, f'Done.')


    def draw(self, show_labels=True):
        self.map.draw(show_labels)


    def match(self, task: Task, belief: Union[Belief, None], belief_term: Union[Term, Compound, Statement, None], task_link: TaskLink, term_link: TermLink):
        '''
        Given a task and a belief, find the matched rules for one step inference.
        ''' 
        link1 = task_link.type
        link2 = term_link.type if term_link is not None else None # `term_link` may be `None` in case of single premise inference.
        
        the_other_compound_has_common = the_other_compound_p1_at_p2 = the_other_compound_p2_at_p1 = False
        connector1 = connector2 = None
        at_compound_pos = None

        common_id = None
        compound_common_id = None

        feature = extract_feature(task.term, (belief.term if belief is not None else belief_term))
        if belief_term is None:
            if link1 is LinkType.TRANSFORM:
                compound_transform: Compound = task.term[task_link.component_index[:-1]]
                if compound_transform.is_compound:
                    connector1 = compound_transform.connector
                    if connector1 in (Connector.ExtensionalImage, Connector.IntensionalImage) and task_link.component_index[-1] == 0:
                        connector1 = None

        else:
            if feature.match_reverse is True:
                pass
            elif feature.has_common_id:
                if feature.has_at:
                    if feature.common_id_task is not None:
                        common_id = feature.common_id_task 
                    elif feature.common_id_belief is not None:
                        common_id = feature.common_id_belief
                    else: raise "Invalid case."
                elif feature.has_compound_at:
                    if feature.compound_common_id_task is not None:
                        common_id = feature.compound_common_id_task 
                        compound: Compound = task.term[common_id]
                        connector1 = compound.connector
                    elif feature.compound_common_id_belief is not None:
                        common_id = feature.compound_common_id_belief
                        compound: Compound = belief_term[common_id]
                        connector2 = compound.connector
                    else: raise "Invalid case."

                    if compound.is_double_only:
                        if compound[0] == belief_term: 
                            at_compound_pos = 0 
                        elif compound[1] == belief_term:
                            at_compound_pos = 1
                        else: raise "Invalid case."
                elif feature.has_compound_common_id:
                    
                    if feature.compound_common_id_belief is not None and feature.compound_common_id_task is not None: 
                        # Now, both `task` and `belief` are not None.
                        compound_task_term: Compound = task.term[feature.compound_common_id_task]
                        compound_belief_term: Compound = belief_term[feature.compound_common_id_belief]
                        compound_p1_at_p2 = _compound_at(compound_task_term, compound_belief_term, False)
                        compound_p2_at_p1 = _compound_at(compound_belief_term, compound_task_term, False)
                        if compound_p1_at_p2 and compound_belief_term.is_compound:
                            connector2 = compound_belief_term.connector
                        if compound_p2_at_p1 and compound_task_term.is_compound:
                            connector1 = compound_task_term.connector
                        
                        compound_common_id = feature.compound_common_id_task*2 + feature.compound_common_id_belief
                    elif feature.compound_common_id_belief is None and belief_term.is_compound: 
                        # Now, `belief` is None
                        compound_common_id = feature.compound_common_id_task
                        connector2 = belief_term.connector

                        common_term = task.term[compound_common_id]
                        if belief_term.is_double_only:
                            if common_term == belief_term[0]: 
                                at_compound_pos = 0 
                            elif common_term == belief_term[1]:
                                at_compound_pos = 1
                            else: raise "Invalid case."
                        elif belief_term.is_multiple_only:
                            if common_term == belief_term[0]: 
                                at_compound_pos = 0 
                            else:
                                at_compound_pos = 1
                            pass

                    elif feature.compound_common_id_task is None: 
                        # Now, `task` is None
                        compound_common_id = feature.compound_common_id_belief
                        task_term: Compound = task.term
                        if task_term.is_compound: 
                            connector1 = task_term.connector
                        #     # raise "Is this case valid?"


                        # compound_common_id = feature.compound_common_id_belief
                        # connector1 = task_term.connector

                        # common_term = belief.term[compound_common_id]
                        # if task_term.is_double_only:
                        #     if common_term == task_term[0]: 
                        #         at_compound_pos = 0 
                        #     elif common_term == task_term[1]:
                        #         at_compound_pos = 1
                        #     else: raise "Invalid case."
                        # elif task_term.is_multiple_only:
                        #     if common_term == task_term[0]: 
                        #         at_compound_pos = 0 
                        #     else:
                        #         at_compound_pos = 1
                        #     pass

                elif feature.common_id_task is not None and feature.common_id_belief is not None:
                    common_id = feature.common_id_task*2 + feature.common_id_belief
                else:
                    if feature.p1_at_p2 and belief_term.is_compound:
                        connector2 = belief_term.connector
                    if feature.p2_at_p1 and task.term.is_compound:
                        connector1 = task.term.connector
            else:
                if task.term.is_compound:
                    connector1 = task.term.connector
                if belief_term.is_compound:
                    connector2 = belief_term.connector
            
            term1, term2 = feature.the_other1, feature.the_other2
            if term1 is not None and term2 is not None:
                the_other_compound_has_common = _compound_has_common(term1, term2)
                # _the_other_compound_has_common1 = _the_other_compound_has_common2 = False
                

                if the_other_compound_has_common:
                    the_other_compound_p1_at_p2 = _compound_at(term1, term2, the_other_compound_has_common)
                    the_other_compound_p2_at_p1 = _compound_at(term2, term1, the_other_compound_has_common)

                    if the_other_compound_p1_at_p2 and the_other_compound_p2_at_p1: 
                        term1: Compound
                        term2: Compound
                        connector1 = term1.connector
                        connector2 = term2.connector
                    elif the_other_compound_p1_at_p2: 
                        term2: Compound
                        connector1 = None
                        connector2 = term2.connector
                        # if term2.is_double_only:
                        #     if term1 == term2[0]: at_compound_pos = 0 
                        #     elif term1 == term2[1]: at_compound_pos = 1
                        #     else: raise "Invalid case."
                    elif the_other_compound_p2_at_p1: 
                        term1: Compound
                        connector1 = term1.connector
                        connector2 = None
                        # if term1.is_double_only:
                        #     if term2 == term1[0]: at_compound_pos = 0 
                        #     elif term2 == term1[1]: at_compound_pos = 1
                        #     else: raise "Invalid case."
        


        indices = (
            int(False) if belief is None else int(True),
            task_type_id(task),
            int(feature.match_reverse),
            
            link1.value,
            link2.value if link2 is not None else None,

            int(task.term.copula) if not task.term.is_atom else None, 
            int(belief.term.copula) if belief is not None else (int(belief_term.connector) if ((belief_term is not None) and (not belief_term.is_atom) and belief_term.is_compound) else None),

            int(connector1) if connector1 is not None else None, 
            int(connector2) if connector2 is not None else None,

            int(feature.has_compound_at), 
            at_compound_pos,
            int(the_other_compound_has_common),
            int(the_other_compound_p1_at_p2),
            int(the_other_compound_p2_at_p1),

            compound_common_id,

            int(feature.has_common_id), 
            int(feature.has_compound_common_id), 
            int(feature.has_at), 
            int(feature.p1_at_p2) if feature.p1_at_p2 is not None else None,
            int(feature.p2_at_p1) if feature.p2_at_p1 is not None else None,
            common_id, 
            
            
        )
        rules: RuleCallable = self.map[indices]
        return rules


    def verify(self, task_link: TaskLink, term_link: TermLink, *args):
        raise "Invalid function."


    def diagnose(self, indices):
        '''
        Given a `indices`, check whether a valid rule can be retrieved.
        If not, return the index of the position where an error occurs.
        Else, return None.
        In each case, Prompt message is printed.
        '''
        for i in range(1,len(indices)):
            if self.map[indices[:i]] is None:
                name_str, (name_type, _) = list(self.structure_map.items())[i]
                print(f"{sty.fg.blue}Diagnose: {sty.fg.red}ERROR.\n    {sty.fg.blue}{i}: {sty.ef.bold}{name_str}, {name_type}{sty.rs.all}")
                
                return i
        print(f"{sty.fg.blue}Diagnose: {sty.fg.green}PASS.{sty.rs.all}")
        return None


    def __repr__(self) -> str:
        '''print self.type_map'''
        r = f"<RuleMap: #rules={len(self.map)}>\n"
        for key, item in self.structure_map.items():
            r += f"    {key}, {item}\n"
        return r
    


if __name__ == '__main__':
    root_path = Path(__file__).parent
    rulemap = RuleMap(build=False)
    rulemap.rebuild(root_path)
