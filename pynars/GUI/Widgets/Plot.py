from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
from pyqtgraph.widgets.PlotWidget import PlotWidget
import numpy as np

class Plot(pg.PlotWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.y = np.full(100, np.nan)  # 100 time points
        self.x = np.full(100, np.nan)  # 100 data points

        pen = pg.mkPen(color=(0, 255, 0))
        self.data_line =  self.plot(self.y, self.x, pen=pen)

    def update_values(self, values: 'float|list'):
        if isinstance(values, float): values = (values,)
        y0 = int(self.x[-1]) if not np.isnan(self.x[-1]) else 0
        if len(values) >= len(self.y): 
            self.y[:] = values[-len(self.y):]
            self.x[:] = list(range(y0+len(values)-len(self.y)+1, y0+len(values)+1))
        else:
            self.y[:-len(values)] = self.y[len(values):]
            self.y[-len(values):] = values
            self.x[:-len(values)] = self.x[len(values):]
            self.x[-len(values):] = list(range(y0+1, y0+len(values)+1))
        self.data_line.setData(self.x, self.y)  # Update the data.
