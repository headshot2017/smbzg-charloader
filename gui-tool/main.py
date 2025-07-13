from PyQt5 import QtWidgets
from pygame import mixer

import resource
import gamepath
from mainwindow import GUIToolMainWindow

app = QtWidgets.QApplication([])
mixer.init()

if not gamepath.init():
    quit()

window = GUIToolMainWindow()
window.show()
app.exec()
