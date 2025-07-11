from PyQt5 import QtWidgets

import resource
import gamepath
from mainwindow import GUIToolMainWindow

app = QtWidgets.QApplication([])

if not gamepath.init():
    quit()

window = GUIToolMainWindow()
window.show()
app.exec()
