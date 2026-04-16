import os

from PyQt5 import QtWidgets, QtGui, QtCore

class PortraitLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setImages("")

    def refresh(self):
        self.setPixmap(QtGui.QPixmap(self.pngFile if os.path.exists(self.pngFile) else self.defaultPng))

    def setImages(self, pngFile, default="images/default_portrait.png"):
        self.pngFile = pngFile
        self.defaultPng = default
        self.refresh()

    def mousePressEvent(self, ev):
        self.refresh()
