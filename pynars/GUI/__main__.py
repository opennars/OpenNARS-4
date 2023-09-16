import sys
from PySide6 import QtWidgets
from .MainWindow import apply_stylesheet, NARSWindow
from .Console import run_nars
from multiprocessing import Process

app = QtWidgets.QApplication(sys.argv)
# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')

window = NARSWindow()
p_nars = Process(target=run_nars, args=(None,))
p_nars.start()
p_nars.join()

# run
window.show()
app.exec()