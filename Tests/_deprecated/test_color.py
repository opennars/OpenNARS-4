import tqdm
from sty import fg, bg, ef, rs

foo = fg.red + 'This is red text!' + fg.rs
bar = bg.blue + 'This has a blue background!' + bg.rs
baz = ef.italic + 'This is italic text' + rs.italic
qux = fg(201) + 'This is pink text using 8bit colors' + fg.rs
qui = bg(255, 10, 10) + 'This is red text using 24bit colors.' + bg.rs

# Add custom colors:

from sty import Style, RgbFg

fg.orange = Style(RgbFg(255, 150, 50))

buf = fg.orange + 'Yay, Im orange.' + fg.rs

print(foo, bar, baz, qux, qui, buf, sep='\n')