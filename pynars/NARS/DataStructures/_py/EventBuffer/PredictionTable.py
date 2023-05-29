import numpy as np
from depq import DEPQ
from pynars.Narsese import Task
from ..Memory import Memory
from ..Table import Table


class PredictionTable(Table):
    ''''''
    def __init__(self, capacity) -> None:
        super().__init__(capacity)
