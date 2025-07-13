import os

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import characterdata
import commandwidget
import actiontabs

class GUIToolMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("form.ui", self)

        self.setCentralWidget(self.centralwidget)

        self.actionNew.triggered.connect(self.onActionNew)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionSave.triggered.connect(self.onActionSave)
        self.actionSaveAs.triggered.connect(self.onActionSaveAs)
        self.actionPrintJson.triggered.connect(self.onActionPrintJson)
        self.actionQuit.triggered.connect(self.onActionQuit)

        self.lbl_portrait.clicked.connect(self.onPortraitClicked)
        self.lbl_battlePortrait.clicked.connect(self.onPortraitClicked)

        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)

        self.btn_addCmd.clicked.connect(self.onAddCommand)

        self.reset()

    def reset(self):
        characterdata.reset()

        self.refreshPortrait()
        self.refreshBattlePortrait()
        self.lineEdit_displayName.clear()
        self.spinbox_scale_charselect.setValue(1)
        self.spinbox_scale_results.setValue(1)
        self.spinbox_scale_ingame.setValue(1)
        self.spinbox_offsetX_charselect.setValue(0)
        self.spinbox_offsetY_charselect.setValue(0)
        self.spinbox_offsetX_results.setValue(0)
        self.spinbox_offsetY_results.setValue(0)
        self.spinbox_offsetX_ingame.setValue(0)
        self.spinbox_offsetY_ingame.setValue(0)
        self.view_primaryColor.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.white))
        self.view_secondaryColor.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black))

        self.animationsTree.clear()
        self.actionTabs.clear()

        addAnim = QtWidgets.QTreeWidgetItem(self.animationsTree, ["Add animation..."])
        addAnim.itemLevel = -1

        cmdlistLayout = self.cmdlist_scrollContents.layout()
        for i in reversed(range(cmdlistLayout.count())): 
            cmdlistLayout.itemAt(i).widget().deleteLater()

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

        if "anims" in jsonFile:
            anims = jsonFile["anims"]
            for animName in anims:
                anim = anims[animName]
                animTree = QtWidgets.QTreeWidgetItem([animName])
                animTree.itemLevel = 0

                if "frames" in anim:
                    frames = anim["frames"]
                    for frameDict in frames:
                        frameInd = frames.index(frameDict)
                        rootFrameTree = QtWidgets.QTreeWidgetItem(animTree, [ "Frame %d" % (frameInd+1) ] )
                        rootFrameTree.itemLevel = 1
                        for frameName in frameDict:
                            frame = frameDict[frameName]
                            thisFrameTree = QtWidgets.QTreeWidgetItem(rootFrameTree, [frameName])
                            thisFrameTree.itemLevel = 2
                        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                        addAction.itemLevel = -3
                        
                addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
                addFrame.itemLevel = -2
                self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

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
        portrait = "%s/portrait.png" % gamepath.getCharacterPath(characterdata.name)
        self.lbl_portrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else ":/prefix/default_portrait.png"))

    def refreshBattlePortrait(self):
        portrait = "%s/battleportrait.png" % gamepath.getCharacterPath(characterdata.name)
        self.lbl_battlePortrait.setPixmap(QtGui.QPixmap(portrait if os.path.exists(portrait) else ":/prefix/default_portrait.png"))

    def addCommand(self):
        cmdWidget = commandwidget.AttackCommandWidget(self)
        cmdWidget.moveUp.connect(self.moveCommandUp)
        cmdWidget.moveDown.connect(self.moveCommandDown)

        self.cmdlist_scrollContents.layout().addWidget(cmdWidget)
        return cmdWidget

    def populateGeneralTab(self, animName):
        json = characterdata.jsonFile
        if not json or "anims" not in json or animName not in json["anims"]:
            return

        anim = json["anims"][animName]

        self.actionTabs.clear()

        general = actiontabs.ActionTab_General(self.actionTabs, anim)
        self.actionTabs.addTab(general, animName)

    def populateAnimTabs(self, animName, frameInd):
        json = characterdata.jsonFile
        if not json or "anims" not in json or animName not in json["anims"]:
            return

        actions = json["anims"][animName]["frames"][frameInd]
        
        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, actions[action], actions)
                self.actionTabs.addTab(widget, action)


    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onAnimationTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            animName, ok = QtWidgets.QInputDialog.getText(self, "Add animation", "Enter a name for the animation")
            if ok:
                animTree = QtWidgets.QTreeWidgetItem([animName])
                animTree.itemLevel = 0
                addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
                addFrame.itemLevel = -2
                self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

                characterdata.jsonFile["anims"][animName] = {"frames": []}

        if item.itemLevel == -2:
            animTree = item.parent()
            frameInd = animTree.childCount()-1
            rootFrameTree = QtWidgets.QTreeWidgetItem([ "Frame %d" % (frameInd+1) ])
            rootFrameTree.itemLevel = 1
            rootFrameTree.frame = frameInd
            animTree.insertChild(frameInd, rootFrameTree)
            addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
            addAction.itemLevel = -3

            animName = animTree.text(0)
            characterdata.jsonFile["anims"][animName]["frames"].append({})

        if item.itemLevel == -3:
            actionDialog = actiontabs.ActionDialog(self)
            if actionDialog.exec():
                actionName = actionDialog.comboBox.currentText()

                rootFrameTree = item.parent()
                thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
                thisFrameTree.itemLevel = 2
                rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

                animTree = rootFrameTree.parent()
                frameInd = animTree.indexOfChild(rootFrameTree)
                animName = animTree.text(0)
                characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName] = characterdata.defaultAction(actionName)
                self.populateAnimTabs(animName, frameInd)
                

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onAnimationTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.populateGeneralTab(current.text(0))
        if current.itemLevel == 1:
            animTree = current.parent()
            frameInd = animTree.indexOfChild(current)
            animName = animTree.text(0)
            self.populateAnimTabs(animName, frameInd)
        if current.itemLevel == 2:
            rootFrameTree = current.parent()
            animTree = rootFrameTree.parent()
            actionInd = rootFrameTree.indexOfChild(current)
            frameInd = animTree.indexOfChild(rootFrameTree)
            animName = animTree.text(0)
            self.populateAnimTabs(animName, frameInd)
            self.actionTabs.setCurrentIndex(actionInd)

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
    def onActionSaveAs(self):
        pass

    @QtCore.pyqtSlot()
    def onActionPrintJson(self):
        print(characterdata.jsonFile)

    @QtCore.pyqtSlot()
    def onActionQuit(self):
        quit()