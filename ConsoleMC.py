from copy import deepcopy
from typing import Tuple, Union
from pathlib import Path
from pynars import Narsese, NAL, NARS
from time import sleep
from multiprocessing import Process
import os

from pynars.NARS.Control.ReasonerMC import ReasonerMC
from pynars.Narsese.Parser.parser import TreeToNarsese
from pynars.Narsese import Sentence
import random
from pynars.NARS import Reasoner as Reasoner
from pynars.utils.Print import out_print, PrintType
from pynars.Narsese import Task
from typing import List
from pynars.utils.tools import rand_seed
import argparse


def info(title):
    print(f'''
============= {title} =============
module name: {__name__}
parent process: {os.getppid()}
process id: {os.getpid()}
============={'=' * (len(title) + 2)}=============
    ''')


def run_nars_MC():
    """"""
    # info('Console')
    seed = 137
    rand_seed(seed)
    out_print(PrintType.COMMENT, f'rand_seed={seed}', comment_title='Setup')
    nars = ReasonerMC(100)
    out_print(PrintType.COMMENT, 'Init...', comment_title='NARS')
    out_print(PrintType.COMMENT, 'Run...', comment_title='NARS')
    # console
    out_print(PrintType.COMMENT, 'Console.', comment_title='NARS')
    for i in range(10):
        nars.cycle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse NAL files.')
    parser.add_argument('filepath', metavar='Path', type=str, nargs='*',
                        help='file path of an *.nal file.')
    args = parser.parse_args()

    try:
        run_nars_MC()
    except KeyboardInterrupt:
        out_print(PrintType.COMMENT, 'Stop...', comment_title='\n\nNARS')

    print('Done.')

# if __name__ == '__main__':
#     # Process
#     info('main')
#     try:
#         p_console = Process(target=run_console, args=())
#         p_nars = Process(target=run_nars, args=())
#         p_console.start()
#         p_nars.start()
#         p_nars.join()
#         p_console.close()
#     except KeyboardInterrupt:
#         print('\n\nStop NARS...')

#     print('Done.')
