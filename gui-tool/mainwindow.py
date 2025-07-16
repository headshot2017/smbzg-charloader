import os
import copy

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
        self.lineEdit_displayName.textChanged.connect(self.onDisplayNameChanged)
        self.spinbox_scale_charselect.valueChanged.connect(self.onScaleCharSelectChanged)
        self.spinbox_scale_results.valueChanged.connect(self.onScaleResultsChanged)
        self.spinbox_scale_ingame.valueChanged.connect(self.onScaleIngameChanged)
        self.spinbox_offsetX_charselect.valueChanged.connect(self.onXOffsetCharSelectChanged)
        self.spinbox_offsetY_charselect.valueChanged.connect(self.onYOffsetCharSelectChanged)
        self.spinbox_offsetX_results.valueChanged.connect(self.onXOffsetResultsChanged)
        self.spinbox_offsetY_results.valueChanged.connect(self.onYOffsetResultsChanged)
        self.spinbox_offsetX_ingame.valueChanged.connect(self.onXOffsetIngameChanged)
        self.spinbox_offsetY_ingame.valueChanged.connect(self.onYOffsetIngameChanged)

        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)
        self.btn_stopCharacter.clicked.connect(self.onStopCharacter)
        self.btn_playCharacter.clicked.connect(self.onPlayCharacter)
        self.btn_reloadSheetCharacter.clicked.connect(self.onRefreshCharacter)

        if os.path.exists("backgrounds"):
            for f in os.listdir("backgrounds"): self.comboBox_backgroundCharacter.addItem(f)
        self.comboBox_backgroundCharacter.currentTextChanged.connect(self.onChangeBackground)

        self.btn_addCmd.clicked.connect(self.onAddCommand)

        self.reset()

        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, False)

    def reset(self, charName=""):
        characterdata.reset(charName)

        self.refreshPortrait()
        self.refreshBattlePortrait()
        self.lineEdit_displayName.clear()
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

        self.animationsTree.clear()
        self.actionTabs.clear()

        self.characterView.animator.setSprite(0,0,0,0)
        self.characterView.reloadCharacter()

        addAnim = QtWidgets.QTreeWidgetItem(self.animationsTree, ["Add animation..."])
        addAnim.itemLevel = -1

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
        self.characterView.reloadCharacter()

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
                    self.view_primaryColor.setColor(QtGui.QColor(primary[0], primary[1], primary[2]))
                if "secondary" in colors:
                    secondary = colors["secondary"]
                    self.view_secondaryColor.setColor(QtGui.QColor(secondary[0], secondary[1], secondary[2]))

        if "anims" in jsonFile:
            self.reloadAnimationsTree(self.animationsTree, jsonFile["anims"])

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
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, animName)

        self.characterView.animator.setAnimation(anim)

    def populateAnimTabs(self, animName, frameInd):
        json = characterdata.jsonFile
        if not json or "anims" not in json or animName not in json["anims"]:
            return

        actions = json["anims"][animName]["frames"][frameInd]
        
        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                self.actionTabs.addTab(widget, action)

        frameAction = None
        frameIndSearch = frameInd
        while not frameAction and frameIndSearch >= 0:
            if "frame" not in json["anims"][animName]["frames"][frameIndSearch]:
                frameIndSearch -= 1
                continue
            frameAction = json["anims"][animName]["frames"][frameIndSearch]["frame"]

        if not frameAction: frameAction = [0, 0, 0, 0]

        self.characterView.animator.setAnimation(json["anims"][animName])
        self.characterView.animator.setFrame(frameInd)

    def addAnimation(self, animName):
        animTree = QtWidgets.QTreeWidgetItem([animName])
        animTree.itemLevel = 0
        addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
        addFrame.itemLevel = -2
        self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

        characterdata.jsonFile["anims"][animName] = {"frames": []}
        return animTree

    def addFrame(self, animTree):
        frameInd = animTree.childCount()-1
        rootFrameTree = QtWidgets.QTreeWidgetItem([ "Frame %d" % (frameInd+1) ])
        rootFrameTree.itemLevel = 1
        rootFrameTree.frame = frameInd
        animTree.insertChild(frameInd, rootFrameTree)
        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
        addAction.itemLevel = -3

        animName = animTree.text(0)
        characterdata.jsonFile["anims"][animName]["frames"].append({})

        self.addAction("delay", rootFrameTree)

        return rootFrameTree

    def addAction(self, actionName, rootFrameTree):
        animTree = rootFrameTree.parent()
        frameInd = animTree.indexOfChild(rootFrameTree)
        animName = animTree.text(0)

        if actionName in characterdata.jsonFile["anims"][animName]["frames"][frameInd]:
            return None

        thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
        thisFrameTree.itemLevel = 2
        rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

        characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName] = characterdata.defaultAction(actionName)
        return thisFrameTree

    def addNecessaryAnimations(self):
        allAnimations = [
            "OnSelect",
            "Victory",
            "Defeat",
            "Idle",
            "IdleB",
            "Guard",
            "Block",
            "Slide",
            "Hit",
            "Hurt",
            "Hurt_AirUpwards",
            "Hurt_AirDownwards",
            "Tumble",
            "Grounded",
            "GetUp",
            "Jump",
            "Fall",
            "Land",
            "Walk",
            "Run",
            "Sprint",
            "Bursting",
            "MR_Air_Idle",
            "MR_Air_MoveDownward",
            "MR_Air_MoveUpward",
            "MR_Air_MoveForward",
            "MR_Ground_Idle",
            "MR_Ground_Land",
            "MR_Ground_MoveForward",
            "MR_Strike_Approach",
            "MR_Strike_Attack",
            "MR_Strike_Finale",
            "MR_Dodge"
        ]

        for animName in allAnimations:
            animTree = self.addAnimation(animName)

    def reloadAnimationsTree(self, treeWidget, anims):
        treeWidget.clear()

        addAnim = QtWidgets.QTreeWidgetItem(treeWidget, ["Add animation..."])
        addAnim.itemLevel = -1

        for animName in anims:
            anim = anims[animName]
            animTree = QtWidgets.QTreeWidgetItem([animName])
            animTree.itemLevel = 0

            if "frames" in anim:
                frames = anim["frames"]
                for frameInd in range(len(frames)):
                    frameDict = frames[frameInd]
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
            treeWidget.insertTopLevelItem(treeWidget.topLevelItemCount()-1, animTree)


    @QtCore.pyqtSlot()
    def onActionTabValueChange(self):
        self.characterView.animator.refresh()

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onAnimationTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            animName, ok = QtWidgets.QInputDialog.getText(self, "Add animation", "Enter a name for the animation")
            if ok:
                if animName in characterdata.jsonFile["anims"]:
                    QtWidgets.QMessageBox.warning(self, "Error", "Animation '%s' already exists" % animName)
                    return

                self.addAnimation(animName)

        if item.itemLevel == -2:
            animTree = item.parent()
            self.addFrame(animTree)

        if item.itemLevel == -3:
            actionDialog = actiontabs.ActionDialog(self)
            if actionDialog.exec():
                actionName = actionDialog.comboBox.currentText()
                rootFrameTree = item.parent()
                animTree = rootFrameTree.parent()
                frameInd = animTree.indexOfChild(rootFrameTree)
                animName = animTree.text(0)

                actionTree = self.addAction(actionName, rootFrameTree)
                if not actionTree:
                    QtWidgets.QMessageBox.warning(self, "Error", "Action '%s' already exists" % actionName)
                    return

                self.populateAnimTabs(animName, frameInd)
                self.actionTabs.setCurrentIndex(rootFrameTree.indexOfChild(actionTree))
                

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

    @QtCore.pyqtSlot(QtCore.QPoint)
    def onAnimationTreeContextMenu(self, point):
        item = self.animationsTree.itemAt(point)
        if item.itemLevel < 0: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 0:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateAnim)
            actionRename.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == 1:
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionDuplicate = menu.addAction("Duplicate")
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionDuplicate.setData(item)

        actionDelete = menu.addAction("Delete")
        actionDelete.triggered.connect(self.onMenuActionDelete)
        actionDelete.setData(item)

        menu.exec(self.animationsTree.mapToGlobal(point))

    @QtCore.pyqtSlot()
    def onMenuActionRename(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename animation", "Rename the animation '%s' to..." % oldName)
        if not ok or not newName: return

        newAnimsDict = {}
        for anim in characterdata.jsonFile["anims"]:
            newAnimsDict[newName if anim == oldName else anim] = characterdata.jsonFile["anims"][anim]

        characterdata.jsonFile["anims"] = newAnimsDict
        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateAnim(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate animation", "Enter a name for the duplicated animation")
        if not ok or not newName: return

        newAnimsDict = {}
        for anim in characterdata.jsonFile["anims"]:
            newAnimsDict[anim] = characterdata.jsonFile["anims"][anim]
            if anim == oldName:
                newAnimsDict[newName] = copy.deepcopy(characterdata.jsonFile["anims"][anim])

        characterdata.jsonFile["anims"] = newAnimsDict
        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateFrame(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        duplicatedFrame = copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd])
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd, duplicatedFrame)

        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onMenuActionMoveUp(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd-1, anim)

        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onMenuActionMoveDown(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd >= len(characterdata.jsonFile["anims"][animName]["frames"])-1: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd+1, anim)

        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onMenuActionDelete(self):
        message = ""
        item = self.sender().data()

        if item.itemLevel == 0:
            animName = item.text(0)
            message = "You are about to delete the animation '%s'.\nAre you sure?" % animName
        elif item.itemLevel == 1:
            animTree = item.parent()
            animName = animTree.text(0)
            message = "You are about to delete %s from the animation '%s'.\nAre you sure?" % (item.text(0), animName)
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            frameName = rootFrameTree.text(0)
            animTree = rootFrameTree.parent()
            animName = animTree.text(0)
            message = "You are about to delete action '%s' from %s of the animation '%s'.\nAre you sure?" % (item.text(0), frameName, animName)

        result = QtWidgets.QMessageBox.warning(self, "Warning", message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result != QtWidgets.QMessageBox.Yes: return

        if item.itemLevel == 0:
            del characterdata.jsonFile["anims"][item.text(0)]
        elif item.itemLevel == 1:
            animTree = item.parent()
            animName = animTree.text(0)
            frameInd = animTree.indexOfChild(item)
            del characterdata.jsonFile["anims"][animName]["frames"][frameInd]
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            animTree = rootFrameTree.parent()
            animName = animTree.text(0)
            frameInd = animTree.indexOfChild(rootFrameTree)
            del characterdata.jsonFile["anims"][animName]["frames"][frameInd][item.text(0)]

        self.reloadAnimationsTree(self.animationsTree, characterdata.jsonFile["anims"])

    @QtCore.pyqtSlot()
    def onStopCharacter(self):
        self.characterView.animator.stop()

    @QtCore.pyqtSlot()
    def onPlayCharacter(self):
        self.characterView.animator.stop()
        self.characterView.animator.setFrame(0)
        self.characterView.animator.start()

    @QtCore.pyqtSlot()
    def onRefreshCharacter(self):
        self.characterView.reloadCharacter()

    @QtCore.pyqtSlot(str)
    def onChangeBackground(self, value):
        self.characterView.setBackground(None if value == "No background" else QtGui.QPixmap("backgrounds/"+value))

    @QtCore.pyqtSlot(QtWidgets.QLabel)
    def onPortraitClicked(self, label):
        if label == self.lbl_portrait: self.refreshPortrait()
        if label == self.lbl_battlePortrait: self.refreshBattlePortrait()

    @QtCore.pyqtSlot(str)
    def onDisplayNameChanged(self, text):
        characterdata.jsonFile["general"]["displayName"] = text

    @QtCore.pyqtSlot(float)
    def onScaleCharSelectChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["charSelect"] = value

    @QtCore.pyqtSlot(float)
    def onScaleResultsChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["results"] = value

    @QtCore.pyqtSlot(float)
    def onScaleIngameChanged(self, value):
        characterdata.jsonFile["general"]["scale"]["ingame"] = value

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
        self.characterView.animator.refresh()

    @QtCore.pyqtSlot(float)
    def onYOffsetIngameChanged(self, value):
        characterdata.jsonFile["general"]["offset"]["ingame"][1] = value
        self.characterView.animator.refresh()

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

        self.addNecessaryAnimations()

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
        print(characterdata.jsonFile)

    @QtCore.pyqtSlot()
    def onActionQuit(self):
        quit()
