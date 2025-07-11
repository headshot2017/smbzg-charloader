from PyQt5 import QtWidgets, QtCore

class PortraitLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(QtWidgets.QLabel)

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

    def mousePressEvent(self, ev):
        self.clicked.emit(self)