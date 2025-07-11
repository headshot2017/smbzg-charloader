import os
import json

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import commandwidget

class GUIToolMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("form.ui", self)

        self.setCentralWidget(self.centralwidget)

        self.lbl_portrait.clicked.connect(self.onPortraitClicked)
        self.lbl_battlePortrait.clicked.connect(self.onPortraitClicked)
        self.btn_addCmd.clicked.connect(self.onAddCommand)
        self.actionNew.triggered.connect(self.onActionNew)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionSave.triggered.connect(self.onActionSave)
        self.actionQuit.triggered.connect(self.onActionQuit)

        self.currentCharacter = ""

    def reset(self):
        layout = self.cmdlist_scrollContents.layout()
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().deleteLater()

    def loadCharacter(self, name):
        if not os.path.exists("%s/character.json" % gamepath.getCharacterPath(name)):
            return

        self.reset()
        self.currentCharacter = name

        self.refreshPortrait()
        self.refreshBattlePortrait()

        jsonFile = json.load(open("%s/character.json" % gamepath.getCharacterPath(name)))

        if "general" in jsonFile:
            general = jsonFile["general"]
            if "displayName" in general:
                self.lineEdit_displayName.setText(general["displayName"])
            if "scale" in general:
                scale = general["scale"]
                if "charSelect" in scale:
                    self.spinbox_scale_charselect.setValue(scale["charSelect"])
                if "results" in scale:
                    self.spinbox_scale_results.setValue(scale["results"])
                if "ingame" in scale:
                    self.spinbox_scale_ingame.setValue(scale["ingame"])
            if "offset" in general:
                offset = general["offset"]
                if "charSelect" in offset:
                    self.spinbox_offsetX_charselect.setValue(offset["charSelect"][0])
                    self.spinbox_offsetY_charselect.setValue(offset["charSelect"][1])
                if "results" in offset:
                    self.spinbox_offsetX_results.setValue(offset["results"][0])
                    self.spinbox_offsetY_results.setValue(offset["results"][1])
                if "ingame" in offset:
                    self.spinbox_offsetX_ingame.setValue(offset["ingame"][0])
                    self.spinbox_offsetY_ingame.setValue(offset["ingame"][1])
            if "colors" in general:
                colors = general["colors"]
                if "primary" in colors:
                    primary = colors["primary"]
                    self.view_primaryColor.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(primary[0], primary[1], primary[2])))
                if "secondary" in colors:
                    secondary = colors["secondary"]
                    self.view_secondaryColor.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(secondary[0], secondary[1], secondary[2])))


        if "commandList" in jsonFile:
            commandList = jsonFile["commandList"]
            for command in commandList:
                title = command["title"] if "title" in command else ""
                subtitle = command["subtitle"] if "subtitle" in command else ""
                addinfo = command["additionalInfo"] if "additionalInfo" in command else ""
                imageList = command["imageList"] if "imageList" in command else ""
                featureList = command["featureList"] if "featureList" in command else ""

                cmdWidget = self.addCommand()
                cmdWidget.lineEdit_title.setText(title)
                cmdWidget.lineEdit_subtitle.setText(subtitle)
                cmdWidget.lineEdit_addinfo.setText(addinfo)
                cmdWidget.parseImageList(imageList)
                cmdWidget.parseFeatureList(featureList)

    def refreshPortrait(self):
        portrait = "%s/portrait.png" % gamepath.getCharacterPath(self.currentCharacter)
        self.lbl_portrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else ":/prefix/default_portrait.png"))

    def refreshBattlePortrait(self):
        portrait = "%s/battleportrait.png" % gamepath.getCharacterPath(self.currentCharacter)
        self.lbl_battlePortrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else ":/prefix/default_portrait.png"))

    def addCommand(self):
        cmdWidget = commandwidget.AttackCommandWidget(self)
        cmdWidget.moveUp.connect(self.moveCommandUp)
        cmdWidget.moveDown.connect(self.moveCommandDown)

        self.cmdlist_scrollContents.layout().addWidget(cmdWidget)
        return cmdWidget


    @QtCore.pyqtSlot(QtWidgets.QLabel)
    def onPortraitClicked(self, label):
        if label == self.lbl_portrait: self.refreshPortrait()
        if label == self.lbl_battlePortrait: self.refreshBattlePortrait()

    @QtCore.pyqtSlot()
    def onAddCommand(self):
        self.addCommand()

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def moveCommandUp(self, cmdWidget):
        layout = self.cmdlist_scrollContents.layout()
        ind = layout.indexOf(cmdWidget)
        if ind != 0:
            layout.removeWidget(cmdWidget)
            layout.insertWidget(ind-1, cmdWidget)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def moveCommandDown(self, cmdWidget):
        layout = self.cmdlist_scrollContents.layout()
        ind = layout.indexOf(cmdWidget)
        if ind != layout.count()-1:
            layout.removeWidget(cmdWidget)
            layout.insertWidget(ind+1, cmdWidget)

    @QtCore.pyqtSlot()
    def onActionNew(self):
        self.reset()

    @QtCore.pyqtSlot()
    def onActionOpen(self):
        fileName, type = QtWidgets.QFileDialog.getOpenFileName(self, "Open character.json", gamepath.customCharsPath, "JSON (*.json)")
        self.loadCharacter(os.path.basename(os.path.dirname(fileName)))

    @QtCore.pyqtSlot()
    def onActionSave(self):
        pass

    @QtCore.pyqtSlot()
    def onActionQuit(self):
        quit()