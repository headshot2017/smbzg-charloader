from PyQt5 import QtWidgets, QtCore, QtGui

class ColorGraphicsView(QtWidgets.QGraphicsView):
    changed = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.theScene = QtWidgets.QGraphicsScene(0, 0, 128, 128)
        self.setScene(self.theScene)
        self.setColor(QtGui.QColor(0, 0, 0))

    def setColor(self, color):
        self.setBackgroundBrush(QtGui.QBrush(color))

    def mousePressEvent(self, ev):
        dialog = QtWidgets.QColorDialog()
        res = dialog.exec_()
        if res == 1:
            color = dialog.currentColor()
            self.setColor(color)
            self.changed.emit(color)
