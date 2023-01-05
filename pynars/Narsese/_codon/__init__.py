from .Term import *
from .Statement import *
from .Variable import *
from .Compound import *
from .Copula import *
from .Connector import *
from .Sentence import *
from .Truth import *
from .Item import *
from .Task import *
from .Budget import *
from .Evidence import *
from .Operation import *
from .Interval import *
from .Terms import *

SELF = Compound(Connector.ExtensionalSet, Term('SELF', do_hashing=True))

TRUE = Term('TRUE', do_hashing=True)
FALSE = Term('FALSE', do_hashing=True)
UNSURE = Term('UNSURE', do_hashing=True)
