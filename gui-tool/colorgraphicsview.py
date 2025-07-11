from PyQt5 import QtWidgets, QtCore, QtGui

class ColorGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.theScene = QtWidgets.QGraphicsScene(0, 0, 128, 128)
        self.setScene(self.theScene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def mousePressEvent(self, ev):
        dialog = QtWidgets.QColorDialog()
        res = dialog.exec_()
        if res == 1:
            self.setBackgroundBrush(QtGui.QBrush(dialog.currentColor()))
