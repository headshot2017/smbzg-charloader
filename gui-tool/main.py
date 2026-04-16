from PyQt5 import QtWidgets
from pygame import mixer

import game
from mainwindow import GUIToolMainWindow

app = QtWidgets.QApplication([])
mixer.init()

if not game.init():
    quit()

window = GUIToolMainWindow()
window.show()
app.exec()
