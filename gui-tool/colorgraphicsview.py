from PyQt5 import QtWidgets, QtCore, QtGui

class ColorGraphicsView(QtWidgets.QGraphicsView):
    changed = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.theScene = QtWidgets.QGraphicsScene(0, 0, 64, 64)
        self.setScene(self.theScene)
        self.setColor(QtGui.QColor(0, 0, 0))

        self.allowAlpha = False

    def setColor(self, color):
        self.setBackgroundBrush(QtGui.QBrush(color))

    def mousePressEvent(self, ev):
        kwargs = {}
        if self.allowAlpha: kwargs = {"options": QtWidgets.QColorDialog.ShowAlphaChannel}

        color = QtWidgets.QColorDialog.getColor(self.backgroundBrush().color(), self, **kwargs)
        if color.isValid():
            self.setColor(color)
            self.changed.emit(color)
