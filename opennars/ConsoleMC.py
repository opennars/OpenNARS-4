import os
import argparse
import matplotlib.pyplot as plt
from opennars.utils.tools import rand_seed
from opennars.utils.Print import print_out, PrintType
from opennars.NARS.Control.ReasonerMC import ReasonerMC


def info(title):
    print(f"""
    ============= {title} =============
    module name: {__name__}
    parent process: {os.getppid()}
    process id: {os.getpid()}
    ============={'=' * (len(title) + 2)}=============
    """)


def run_nars_MC():
    info('Console')
    seed = 1024
    rand_seed(seed)
    print_out(PrintType.COMMENT, f'rand_seed={seed}', comment_title='Setup')
    nars = ReasonerMC(100)
    print_out(PrintType.COMMENT, 'Init...', comment_title='NARS')
    print_out(PrintType.COMMENT, 'Run...', comment_title='NARS')
    # console
    print_out(PrintType.COMMENT, 'Console.', comment_title='NARS')
    nars.root.mainloop()
    plt.figure()
    plt.plot(nars.time_consumption)
    plt.show()

    print("Finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse NAL files.')
    parser.add_argument('filepath', metavar='Path', type=str, nargs='*',
                        help='file path of an *.nal file.')
    args = parser.parse_args()

    try:
        run_nars_MC()
    except KeyboardInterrupt:
        print_out(PrintType.COMMENT, 'Stop...', comment_title='\n\nNARS')

    print('Done.')
