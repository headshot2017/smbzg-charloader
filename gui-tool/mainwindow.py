import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import characterdata
import commandwidget

class GUIToolMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/form.ui", self)

        self.setCentralWidget(self.centralwidget)

        self.actionNew.triggered.connect(self.onActionNew)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionSave.triggered.connect(self.onActionSave)
        self.actionSaveAs.triggered.connect(self.onActionSaveAs)
        self.actionPrintJson.triggered.connect(self.onActionPrintJson)
        self.actionQuit.triggered.connect(self.onActionQuit)

        self.lbl_portrait.clicked.connect(self.onPortraitClicked)
        self.lbl_battlePortrait.clicked.connect(self.onPortraitClicked)
        self.lineEdit_displayName.textChanged.connect(self.onDisplayNameChanged)
        self.combobox_platform.currentIndexChanged.connect(self.onPlatformChanged)
        self.checkbox_unbalanced.stateChanged.connect(self.onUnbalancedChanged)
        self.spinbox_scale_charselect.valueChanged.connect(self.onScaleCharSelectChanged)
        self.spinbox_scale_results.valueChanged.connect(self.onScaleResultsChanged)
        self.spinbox_scale_ingame.valueChanged.connect(self.onScaleIngameChanged)
        self.spinbox_offsetX_charselect.valueChanged.connect(self.onXOffsetCharSelectChanged)
        self.spinbox_offsetY_charselect.valueChanged.connect(self.onYOffsetCharSelectChanged)
        self.spinbox_offsetX_results.valueChanged.connect(self.onXOffsetResultsChanged)
        self.spinbox_offsetY_results.valueChanged.connect(self.onYOffsetResultsChanged)
        self.spinbox_offsetX_ingame.valueChanged.connect(self.onXOffsetIngameChanged)
        self.spinbox_offsetY_ingame.valueChanged.connect(self.onYOffsetIngameChanged)
        self.view_primaryColor.changed.connect(self.onPrimaryColorChanged)
        self.view_secondaryColor.changed.connect(self.onSecondaryColorChanged)
        self.slider_hue.valueChanged.connect(self.onHueChanged)
        self.slider_saturation.valueChanged.connect(self.onSaturationChanged)
        self.slider_contrast.valueChanged.connect(self.onContrastChanged)
        self.btn_openFolder.clicked.connect(self.onOpenFolder)

        self.btn_addCmd.clicked.connect(self.onAddCommand)

        self.reset()

        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, False)

    def reset(self, charName=""):
        characterdata.reset(charName)

        self.refreshPortrait()
        self.refreshBattlePortrait()
        self.lineEdit_displayName.clear()
        self.combobox_platform.setCurrentIndex(0)
        self.checkbox_unbalanced.setChecked(False)
        self.spinbox_scale_charselect.setValue(characterdata.jsonFile["general"]["scale"]["charSelect"])
        self.spinbox_scale_results.setValue(characterdata.jsonFile["general"]["scale"]["results"])
        self.spinbox_scale_ingame.setValue(characterdata.jsonFile["general"]["scale"]["ingame"])
        self.spinbox_offsetX_charselect.setValue(characterdata.jsonFile["general"]["offset"]["charSelect"][0])
        self.spinbox_offsetY_charselect.setValue(characterdata.jsonFile["general"]["offset"]["charSelect"][1])
        self.spinbox_offsetX_results.setValue(characterdata.jsonFile["general"]["offset"]["results"][0])
        self.spinbox_offsetY_results.setValue(characterdata.jsonFile["general"]["offset"]["results"][1])
        self.spinbox_offsetX_ingame.setValue(characterdata.jsonFile["general"]["offset"]["ingame"][0])
        self.spinbox_offsetY_ingame.setValue(characterdata.jsonFile["general"]["offset"]["ingame"][1])
        self.view_primaryColor.setColor(QtGui.QColor(*characterdata.jsonFile["general"]["colors"]["primary"]))
        self.view_secondaryColor.setColor(QtGui.QColor(*characterdata.jsonFile["general"]["colors"]["secondary"]))
        self.slider_hue.setValue(int(characterdata.jsonFile["general"]["colors"]["alternateColors"][0]*100))
        self.slider_saturation.setValue(int(characterdata.jsonFile["general"]["colors"]["alternateColors"][1]*100))
        self.slider_contrast.setValue(int(characterdata.jsonFile["general"]["colors"]["alternateColors"][2]*100))

        self.tab_anims.reset()
        self.tab_effects.reset()
        self.tab_companions.reset()

        cmdlistLayout = self.cmdlist_scrollContents.layout()
        for i in reversed(range(cmdlistLayout.count())): 
            cmdlistLayout.itemAt(i).widget().deleteLater()

        for i in range(self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, True)

    def loadCharacter(self, name):
        if not os.path.exists("%s/character.json" % gamepath.getCharacterPath(name)):
            return

        self.reset()

        jsonFile = characterdata.load(name)

        self.refreshPortrait()
        self.refreshBattlePortrait()

        if "general" in jsonFile:
            general = jsonFile["general"]
            if "displayName" in general:
                self.lineEdit_displayName.setText(general["displayName"])
            if "unbalanced" in general:
                self.checkbox_unbalanced.setChecked(general["unbalanced"])
            if "platform" in general:
                self.checkbox_unbalanced.setCurrentIndex(general["platform"])
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
                if "primary" not in colors: colors["primary"] = [255, 255, 255]
                if "secondary" not in colors: colors["secondary"] = [0, 0, 0]
                if "alternateColors" not in colors: colors["alternateColors"] = [0.57, 1, 1]
                primary = colors["primary"]
                secondary = colors["secondary"]
                alternateColors = colors["alternateColors"]

                self.view_primaryColor.setColor(QtGui.QColor(primary[0], primary[1], primary[2]))
                self.view_secondaryColor.setColor(QtGui.QColor(secondary[0], secondary[1], secondary[2]))
                self.slider_hue.setValue(int(alternateColors[0]*100))
                self.slider_saturation.setValue(int(alternateColors[1]*100))
                self.slider_contrast.setValue(int(alternateColors[2]*100))

        if "anims" in jsonFile:
            self.tab_anims.reloadTree()
        if "effects" in jsonFile:
            self.tab_effects.reloadTree()
        if characterdata.companionJson:
            self.tab_companions.reloadTree()

        if "commandList" in jsonFile:
            commandList = jsonFile["commandList"]
            for command in commandList:
                cmdWidget = self.addCommand(command)

    def refreshPortrait(self):
        portrait = "%s/portrait.png" % gamepath.getCharacterPath(characterdata.name)
        self.lbl_portrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else "images/default_portrait.png"))

    def refreshBattlePortrait(self):
        portrait = "%s/battleportrait.png" % gamepath.getCharacterPath(characterdata.name)
        self.lbl_battlePortrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else "images/default_portrait.png"))

    def addCommand(self, commandInJson):
        cmdWidget = commandwidget.AttackCommandWidget(self, commandInJson)
        cmdWidget.moveUp.connect(self.moveCommandUp)
        cmdWidget.moveDown.connect(self.moveCommandDown)
        cmdWidget.deleted.connect(self.onCommandDeleted)

        self.cmdlist_scrollContents.layout().addWidget(cmdWidget)
        return cmdWidget


    @QtCore.pyqtSlot(QtWidgets.QLabel)
    def onPortraitClicked(self, label):
        if label == self.lbl_portrait: self.refreshPortrait()
        if label == self.lbl_battlePortrait: self.refreshBattlePortrait()

    @QtCore.pyqtSlot(str)
    def onDisplayNameChanged(self, text):
        characterdata.jsonFile["general"]["displayName"] = text

    @QtCore.pyqtSlot(int)
    def onPlatformChanged(self, value):
        characterdata.jsonFile["general"]["platform"] = value

    @QtCore.pyqtSlot(int)
    def onUnbalancedChanged(self, value):
        characterdata.jsonFile["general"]["unbalanced"] = value > 0

    @QtCore.pyqtSlot(float)
    def onScaleCharSelectChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["charSelect"] = value

    @QtCore.pyqtSlot(float)
    def onScaleResultsChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["results"] = value

    @QtCore.pyqtSlot(float)
    def onScaleIngameChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["ingame"] = value
        self.tab_anims.onRefresh()

    @QtCore.pyqtSlot(float)
    def onXOffsetCharSelectChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["charSelect"][0] = value

    @QtCore.pyqtSlot(float)
    def onYOffsetCharSelectChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["charSelect"][1] = value

    @QtCore.pyqtSlot(float)
    def onXOffsetResultsChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["results"][0] = value

    @QtCore.pyqtSlot(float)
    def onYOffsetResultsChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["results"][1] = value

    @QtCore.pyqtSlot(float)
    def onXOffsetIngameChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["ingame"][0] = value
        self.tab_anims.onRefresh()

    @QtCore.pyqtSlot(float)
    def onYOffsetIngameChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["ingame"][1] = value
        self.tab_anims.onRefresh()

    @QtCore.pyqtSlot(QtGui.QColor)
    def onPrimaryColorChanged(self, color):
        characterdata.jsonFile["general"]["colors"]["primary"] = color.getRgb()[:3]

    @QtCore.pyqtSlot(QtGui.QColor)
    def onSecondaryColorChanged(self, color):
        characterdata.jsonFile["general"]["colors"]["secondary"] = color.getRgb()[:3]

    @QtCore.pyqtSlot(int)
    def onHueChanged(self, value):
        realValue = value / 100.
        self.lbl_hue.setText("Hue: %.2f" % realValue)
        characterdata.jsonFile["general"]["colors"]["alternateColors"][0] = realValue

    @QtCore.pyqtSlot(int)
    def onSaturationChanged(self, value):
        realValue = value / 100.
        self.lbl_saturation.setText("Saturation: %.2f" % realValue)
        characterdata.jsonFile["general"]["colors"]["alternateColors"][1] = realValue

    @QtCore.pyqtSlot(int)
    def onContrastChanged(self, value):
        realValue = value / 100.
        self.lbl_contrast.setText("Contrast: %.2f" % realValue)
        characterdata.jsonFile["general"]["colors"]["alternateColors"][2] = realValue

    @QtCore.pyqtSlot()
    def onOpenFolder(self):
        webbrowser.open(gamepath.getCharacterPath(characterdata.name))

    @QtCore.pyqtSlot()
    def onAddCommand(self):
        newCommand = characterdata.defaultCommand()
        characterdata.jsonFile["commandList"].append(newCommand)
        self.addCommand(newCommand)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def moveCommandUp(self, cmdWidget):
        layout = self.cmdlist_scrollContents.layout()
        ind = layout.indexOf(cmdWidget)
        if ind != 0:
            layout.removeWidget(cmdWidget)
            layout.insertWidget(ind-1, cmdWidget)
            command = characterdata.jsonFile["commandList"].pop(ind)
            characterdata.jsonFile["commandList"].insert(ind-1, command)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def moveCommandDown(self, cmdWidget):
        layout = self.cmdlist_scrollContents.layout()
        ind = layout.indexOf(cmdWidget)
        if ind != layout.count()-1:
            layout.removeWidget(cmdWidget)
            layout.insertWidget(ind+1, cmdWidget)
            command = characterdata.jsonFile["commandList"].pop(ind)
            characterdata.jsonFile["commandList"].insert(ind+1, command)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def onCommandDeleted(self, cmdWidget):
        layout = self.cmdlist_scrollContents.layout()
        ind = layout.indexOf(cmdWidget)
        layout.removeWidget(cmdWidget)
        del characterdata.jsonFile["commandList"][ind]

    @QtCore.pyqtSlot()
    def onActionNew(self):
        charName, ok = QtWidgets.QInputDialog.getText(self, "New character", "Enter the character's folder name.\n\nThis name will also be used for the character's internal name in SMBZ-G.")
        if not ok: return

        path = gamepath.getCharacterPath(charName)

        if os.path.exists(path) and os.path.exists(path+"/character.json"):
            result = QtWidgets.QMessageBox.warning(self, "Warning",
                "The character '%s' already exists in your custom characters folder.\n\nDo you want to continue and replace it?" % charName,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if result != QtWidgets.QMessageBox.Yes:
                return

        elif not os.path.exists(path):
            os.makedirs(path)

        extraPaths = [
            path+"/music",
            path+"/sounds",
            path+"/effects",
            path+"/companions"
        ]
        for extraPath in extraPaths:
            if not os.path.exists(extraPath): os.mkdir(extraPath)

        self.reset(charName)

        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)

        if self.tabWidget.tabText(0) == "Welcome":
            self.tabWidget.removeTab(0)

        self.tab_anims.addNecessaryAnimations()
        open(path+"/portrait.png", "wb").write(open("images/default_portrait.png", "rb").read())
        open(path+"/battleportrait.png", "wb").write(open("images/default_battleportrait.png", "rb").read())

        QtWidgets.QMessageBox.information(self, "Done",
            "Character '%s' created.\n" % (charName) +
            "Remember to do the following:\n" +
            "* Add a sprite sheet for your character with the file name 'sheet.png'\n" +
            "* Add portrait images for your character: portrait.png and battleportrait.png\n" +
            "* OPTIONAL: Add custom sounds to the 'sounds' directory: .wav, .ogg and .mp3 files are accepted\n" +
            "* OPTIONAL: Add custom particle images to the 'effects' directory: .png only"
        )

        self.statusbar.showMessage("Created character '%s'" % charName, 3000)

    @QtCore.pyqtSlot()
    def onActionOpen(self):
        fileName, type = QtWidgets.QFileDialog.getOpenFileName(self, "Open character.json", gamepath.customCharsPath, "JSON (*.json)")
        if not fileName: return

        charName = os.path.basename(os.path.dirname(fileName))
        self.loadCharacter(charName)

        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)

        if self.tabWidget.tabText(0) == "Welcome":
            self.tabWidget.removeTab(0)

        self.statusbar.showMessage("Loaded character '%s'" % charName, 3000)

    @QtCore.pyqtSlot()
    def onActionSave(self):
        characterdata.save()
        self.statusbar.showMessage("Saved character '%s'" % characterdata.name, 3000)

    @QtCore.pyqtSlot()
    def onActionSaveAs(self):
        charName, ok = QtWidgets.QInputDialog.getText(self, "New character", "Enter the character's folder name.\n\nThis name will also be used for the character's internal name in SMBZ-G.")
        if not ok: return

        characterdata.name = charName
        characterdata.save()
        self.statusbar.showMessage("Saved character '%s'" % characterdata.name, 3000)

    @QtCore.pyqtSlot()
    def onActionPrintJson(self):
        print("character.json:")
        print(characterdata.jsonFile)
        for companion in characterdata.companionJson:
            print()
            print("'%s' companion.json:" % companion)
            print(characterdata.companionJson[companion])

    @QtCore.pyqtSlot()
    def onActionQuit(self):
        quit()
