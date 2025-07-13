from PyQt5 import QtWidgets, QtCore, QtGui, uic

class AnimatorGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.theScene = QtWidgets.QGraphicsScene()
        self.setScene(self.theScene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(224, 224, 224)))
