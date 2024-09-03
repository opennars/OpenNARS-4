from enum import Enum
from sty import bg, fg, ef, rs


class PrintType(Enum):
    IN = f'{fg.cyan}IN    :{fg.rs}'
    OUT = f'{fg.yellow}OUT   :{fg.rs}'
    ERROR = f'{fg.red}ERROR :{fg.rs}'
    ANSWER = f'{fg.green}ANSWER:{fg.rs}'
    ACHIEVED = f'{fg.green}ACHIEVED:{fg.rs}'
    EXE = f'{fg.green}EXE   :{fg.rs}'
    INFO = f'{fg.blue}INFO  :{fg.rs}'
    COMMENT = F'{fg.grey}COMMENT:{fg.rs}'

def print_filename(filename):
        print(f'{fg.li_blue}-- File: {ef.italic}{filename}{rs.italic} --{fg.rs}')

def print_out(type: PrintType, content, p: float=None, d: float=None, q: float=None, comment_title: str=None, end: str=None):
    # show_budget = True
    # if isinstance(p, float) and isinstance(d, float) and isinstance(q, float):
    #     if p<0 or p>1 or q<0 or q>1 or d<0 or d>1:
    #         show_budget = False
    # else:
    #     show_budget = False

    if isinstance(p, float) and p>=0 and p<=1:
        bg1 = bg(min(255, int(255*p/2+10)),10,10)
        p = f'{round(p, 2):.2f}'
    else:
        p = '    '
        bg1 = ''
    if isinstance(d, float) and d>=0 and d<=1:
        bg2 = bg(10,min(255, int(255*d/2+10)),10)
        d = f'{round(d, 2):.2f}'
    else:
        d = '    '
        bg2 = ''
    if isinstance(q, float) and q>=0 and q<=1:
        bg3 = bg(10,10,min(255, int(255*q/2+10)))
        q = f'{round(q, 2):.2f}'
    else:
        q = '    '
        bg3 = ''

    # print(F'{bg(int(256*p),0,0)} {p} {bg(0,int(256*q),0)} {q} {bg(0,0,int(256*d))} {d} {bg.rs}{type.value} {str(content)}')

    if type is PrintType.COMMENT and comment_title is not None:
        print(f'{fg.da_grey}{comment_title}: {str(content)}{fg.rs}', end=end)
    elif type is PrintType.INFO:
        print(f'{bg1} {p} {bg.rs}{bg2} {d} {bg.rs}{bg3} {q} {bg.rs} {type.value} {fg.grey}{str(content)}{fg.rs}', end=end, )
    else:
        print(f'{bg1} {p} {bg.rs}{bg2} {d} {bg.rs}{bg3} {q} {bg.rs} {type.value} {str(content)}', end=end, )
    