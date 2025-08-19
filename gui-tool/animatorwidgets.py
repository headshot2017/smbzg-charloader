import os
import copy

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import characterdata
import actiontabs


class BaseAnimatorWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/animatorwidget.ui", self)

        self.btn_stop.clicked.connect(self.onStop)
        self.btn_play.clicked.connect(self.onPlay)

        if os.path.exists("backgrounds"):
            for f in os.listdir("backgrounds"): self.comboBox_background.addItem(f)
        self.comboBox_background.currentTextChanged.connect(self.onChangeBackground)

    def reset(self):
        self.animationsTree.clear()
        self.actionTabs.clear()

        self.animatorView.animator.setSprite(0,0,0,0)
        self.animatorView.reloadSprite("")

    def populateGeneralTab(self, animName):
        pass

    def populateAnimTabs(self, animName, frameInd):
        pass


    @QtCore.pyqtSlot()
    def onActionTabValueChange(self):
        self.animatorView.animator.refresh()

    @QtCore.pyqtSlot(str)
    def onChangeBackground(self, value):
        self.animatorView.setBackground(None if value == "No background" else QtGui.QPixmap("backgrounds/"+value))

    @QtCore.pyqtSlot()
    def onStop(self):
        self.animatorView.animator.stop()

    @QtCore.pyqtSlot()
    def onPlay(self):
        self.animatorView.animator.stop()
        self.animatorView.animator.setFrame(0)
        self.animatorView.animator.start()


class CharacterAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__()

        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)
        self.btn_reloadSprite.clicked.connect(self.onRefresh)

    def reset(self):
        super().reset()

        addAnim = QtWidgets.QTreeWidgetItem(self.animationsTree, ["Add animation..."])
        addAnim.itemLevel = -1

    def populateGeneralTab(self, animName):
        if not characterdata.jsonFile or animName not in characterdata.jsonFile["anims"]:
            return

        anim = characterdata.jsonFile["anims"][animName]

        self.actionTabs.clear()

        general = actiontabs.ActionTab_General(self.actionTabs, anim)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, animName)

        self.animatorView.animator.setAnimation(anim)

    def populateAnimTabs(self, animName, frameInd):
        if not characterdata.jsonFile or animName not in characterdata.jsonFile["anims"]:
            return

        actions = characterdata.jsonFile["anims"][animName]["frames"][frameInd]
        
        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                self.actionTabs.addTab(widget, action)

        self.animatorView.animator.setAnimation(characterdata.jsonFile["anims"][animName])
        self.animatorView.animator.setFrame(frameInd)

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
        if len(characterdata.jsonFile["anims"][animName]["frames"]) == 1:
            self.addAction("frame", rootFrameTree)

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
            "BurstVictoryStrike",
            "BurstVictoryStrike_MR",
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

    def reloadTree(self):
        self.animationsTree.clear()

        addAnim = QtWidgets.QTreeWidgetItem(self.animationsTree, ["Add animation..."])
        addAnim.itemLevel = -1

        for animName in characterdata.jsonFile["anims"]:
            anim = characterdata.jsonFile["anims"][animName]
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
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)


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
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            actionDuplicate = menu.addAction("Duplicate")
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
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
        self.reloadTree()

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
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateFrame(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        duplicatedFrame = copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd])
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd, duplicatedFrame)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveTop(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].insert(0, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveUp(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd-1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDown(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd >= len(characterdata.jsonFile["anims"][animName]["frames"])-1: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd+1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveBottom(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd >= len(characterdata.jsonFile["anims"][animName]["frames"])-1: return

        anim = characterdata.jsonFile["anims"][animName]["frames"].pop(frameInd)
        characterdata.jsonFile["anims"][animName]["frames"].append(anim)

        self.reloadTree()

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

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onRefresh(self):
        path = gamepath.getCharacterPath(characterdata.name)
        self.animatorView.reloadSprite("%s/sheet.png" % path)
        self.animatorView.animator.globalOffset = characterdata.jsonFile["general"]["offset"]["ingame"]
        self.animatorView.animator.globalScale = characterdata.jsonFile["general"]["scale"]["ingame"]


class EffectAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__()

        self.animationsTree.setHeaderLabel("Effects")
        self.btn_reloadSprite.setText("Reload sprite")

        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)
        self.btn_reloadSprite.clicked.connect(self.onRefresh)

        self.currentFx = ""

    def reset(self):
        super().reset()

        addEffect = QtWidgets.QTreeWidgetItem(self.animationsTree, ["New effect..."])
        addEffect.itemLevel = -1

    def refreshFx(self):
        if not self.currentFx: return
        path = gamepath.getCharacterPath(characterdata.name)
        fx = characterdata.jsonFile["effects"][self.currentFx]
        self.animatorView.reloadSprite("%s/effects/%s.png" % (path, fx["texture"] if "texture" in fx else ""))

    def populateGeneralTab(self, fxName):
        if not characterdata.jsonFile or fxName not in characterdata.jsonFile["effects"]:
            return

        self.currentFx = fxName
        self.refreshFx()

        fx = characterdata.jsonFile["effects"][fxName]

        self.actionTabs.clear()

        general = actiontabs.ActionTab_GeneralEffect(self.actionTabs, fx)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, fxName)

        self.animatorView.animator.setAnimation(fx)
        self.animatorView.animator.setLoopCount(1)

    def populateAnimTabs(self, fxName, frameInd):
        if not characterdata.jsonFile or fxName not in characterdata.jsonFile["effects"]:
            return

        self.currentFx = fxName
        self.refreshFx()

        actions = characterdata.jsonFile["effects"][fxName]["frames"][frameInd]

        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                self.actionTabs.addTab(widget, action)

        self.animatorView.animator.setAnimation(characterdata.jsonFile["effects"][fxName])
        self.animatorView.animator.setFrame(frameInd)
        self.animatorView.animator.setLoopCount(1)

    def addEffect(self, fxName):
        animTree = QtWidgets.QTreeWidgetItem([fxName])
        animTree.itemLevel = 0
        addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
        addFrame.itemLevel = -2
        self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

        characterdata.jsonFile["effects"][fxName] = {"frames": []}
        return animTree

    def addFrame(self, animTree):
        frameInd = animTree.childCount()-1
        rootFrameTree = QtWidgets.QTreeWidgetItem([ "Frame %d" % (frameInd+1) ])
        rootFrameTree.itemLevel = 1
        rootFrameTree.frame = frameInd
        animTree.insertChild(frameInd, rootFrameTree)
        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
        addAction.itemLevel = -3

        fxName = animTree.text(0)
        characterdata.jsonFile["effects"][fxName]["frames"].append({})

        self.addAction("delay", rootFrameTree)
        if len(characterdata.jsonFile["effects"][fxName]["frames"]) == 1:
            self.addAction("frame", rootFrameTree)

        return rootFrameTree

    def addAction(self, actionName, rootFrameTree):
        animTree = rootFrameTree.parent()
        frameInd = animTree.indexOfChild(rootFrameTree)
        fxName = animTree.text(0)

        if actionName in characterdata.jsonFile["effects"][fxName]["frames"][frameInd]:
            return None

        thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
        thisFrameTree.itemLevel = 2
        rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

        characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName] = characterdata.defaultAction(actionName)
        return thisFrameTree

    def reloadTree(self):
        self.animationsTree.clear()

        addEffect = QtWidgets.QTreeWidgetItem(self.animationsTree, ["New effect..."])
        addEffect.itemLevel = -1

        for fxName in characterdata.jsonFile["effects"]:
            fx = characterdata.jsonFile["effects"][fxName]
            fxTree = QtWidgets.QTreeWidgetItem([fxName])
            fxTree.itemLevel = 0

            if "frames" in fx:
                frames = fx["frames"]
                for frameInd in range(len(frames)):
                    frameDict = frames[frameInd]
                    rootFrameTree = QtWidgets.QTreeWidgetItem(fxTree, [ "Frame %d" % (frameInd+1) ] )
                    rootFrameTree.itemLevel = 1
                    for frameName in frameDict:
                        frame = frameDict[frameName]
                        thisFrameTree = QtWidgets.QTreeWidgetItem(rootFrameTree, [frameName])
                        thisFrameTree.itemLevel = 2
                    addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                    addAction.itemLevel = -3

            addFrame = QtWidgets.QTreeWidgetItem(fxTree, ["Add frame..."])
            addFrame.itemLevel = -2
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, fxTree)


    @QtCore.pyqtSlot()
    def onActionTabValueChange(self):
        self.refreshFx()
        self.animatorView.animator.refresh()

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onAnimationTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.populateGeneralTab(current.text(0))
        if current.itemLevel == 1:
            animTree = current.parent()
            frameInd = animTree.indexOfChild(current)
            fxName = animTree.text(0)
            self.populateAnimTabs(fxName, frameInd)
        if current.itemLevel == 2:
            rootFrameTree = current.parent()
            animTree = rootFrameTree.parent()
            actionInd = rootFrameTree.indexOfChild(current)
            frameInd = animTree.indexOfChild(rootFrameTree)
            fxName = animTree.text(0)
            self.populateAnimTabs(fxName, frameInd)
            self.actionTabs.setCurrentIndex(actionInd)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onAnimationTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            fxName, ok = QtWidgets.QInputDialog.getText(self, "New effect", "Enter a name for the effect")
            if ok:
                if fxName in characterdata.jsonFile["effects"]:
                    QtWidgets.QMessageBox.warning(self, "Error", "Effect '%s' already exists" % fxName)
                    return

                self.addEffect(fxName)

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
                fxName = animTree.text(0)

                actionTree = self.addAction(actionName, rootFrameTree)
                if not actionTree:
                    QtWidgets.QMessageBox.warning(self, "Error", "Action '%s' already exists" % actionName)
                    return

                self.populateAnimTabs(fxName, frameInd)
                self.actionTabs.setCurrentIndex(rootFrameTree.indexOfChild(actionTree))

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
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            actionDuplicate = menu.addAction("Duplicate")
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        actionDelete = menu.addAction("Delete")
        actionDelete.triggered.connect(self.onMenuActionDelete)
        actionDelete.setData(item)

        menu.exec(self.animationsTree.mapToGlobal(point))

    @QtCore.pyqtSlot()
    def onMenuActionRename(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename effect", "Rename the effect '%s' to..." % oldName)
        if not ok or not newName: return

        newFxDict = {}
        for fx in characterdata.jsonFile["effects"]:
            newFxDict[newName if fx == oldName else fx] = characterdata.jsonFile["effects"][fx]

        characterdata.jsonFile["effects"] = newFxDict
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateAnim(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate effect", "Enter a name for the duplicated effect")
        if not ok or not newName: return

        newFxDict = {}
        for fx in characterdata.jsonFile["effects"]:
            newFxDict[fx] = characterdata.jsonFile["effects"][fx]
            if fx == oldName:
                newFxDict[newName] = copy.deepcopy(characterdata.jsonFile["effects"][fx])

        characterdata.jsonFile["effects"] = newFxDict
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateFrame(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        duplicatedFrame = copy.deepcopy(characterdata.jsonFile["effects"][fxName]["frames"][frameInd])
        characterdata.jsonFile["effects"][fxName]["frames"].insert(frameInd, duplicatedFrame)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveTop(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        anim = characterdata.jsonFile["effects"][fxName]["frames"].pop(frameInd)
        characterdata.jsonFile["effects"][fxName]["frames"].insert(0, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveUp(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        anim = characterdata.jsonFile["effects"][fxName]["frames"].pop(frameInd)
        characterdata.jsonFile["effects"][fxName]["frames"].insert(frameInd-1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDown(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd >= len(characterdata.jsonFile["effects"][fxName]["frames"])-1: return

        anim = characterdata.jsonFile["effects"][fxName]["frames"].pop(frameInd)
        characterdata.jsonFile["effects"][fxName]["frames"].insert(frameInd+1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveBottom(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd >= len(characterdata.jsonFile["effects"][fxName]["frames"])-1: return

        anim = characterdata.jsonFile["effects"][fxName]["frames"].pop(frameInd)
        characterdata.jsonFile["effects"][fxName]["frames"].append(anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDelete(self):
        message = ""
        item = self.sender().data()

        if item.itemLevel == 0:
            fxName = item.text(0)
            message = "You are about to delete the effect '%s'.\nAre you sure?" % fxName
        elif item.itemLevel == 1:
            animTree = item.parent()
            fxName = animTree.text(0)
            message = "You are about to delete %s from the effect '%s'.\nAre you sure?" % (item.text(0), fxName)
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            frameName = rootFrameTree.text(0)
            animTree = rootFrameTree.parent()
            fxName = animTree.text(0)
            message = "You are about to delete action '%s' from %s of the effect '%s'.\nAre you sure?" % (item.text(0), frameName, fxName)

        result = QtWidgets.QMessageBox.warning(self, "Warning", message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result != QtWidgets.QMessageBox.Yes: return

        if item.itemLevel == 0:
            del characterdata.jsonFile["effects"][item.text(0)]
        elif item.itemLevel == 1:
            animTree = item.parent()
            fxName = animTree.text(0)
            frameInd = animTree.indexOfChild(item)
            del characterdata.jsonFile["effects"][fxName]["frames"][frameInd]
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            animTree = rootFrameTree.parent()
            fxName = animTree.text(0)
            frameInd = animTree.indexOfChild(rootFrameTree)
            del characterdata.jsonFile["effects"][fxName]["frames"][frameInd][item.text(0)]

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onRefresh(self):
        self.refreshFx()


class CompanionAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__()

        self.animationsTree.setHeaderLabel("Companions")
        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)
        self.btn_reloadSprite.clicked.connect(self.onRefresh)

    def reset(self):
        super().reset()

        addCompanion = QtWidgets.QTreeWidgetItem(self.animationsTree, ["New companion..."])
        addCompanion.itemLevel = -1

    def setCompanionSprite(self, companionName):
        companion = characterdata.companionJson[companionName]
        path = gamepath.getCharacterPath(characterdata.name)

        self.animatorView.reloadSprite("%s/companions/%s/sheet.png" % (path, companionName))
        self.animatorView.animator.globalOffset = companion.get("general", {}).get("offset", [0, 0])
        self.animatorView.animator.globalScale = companion.get("general", {}).get("scale", 1)

    def populateCompanionTab(self, companionName):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        self.actionTabs.clear()

        general = actiontabs.ActionTab_Companion(self.actionTabs, companionName)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, companionName)

        self.setCompanionSprite(companionName)

    def populateGeneralTab(self, companionName, animName):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        companion = characterdata.companionJson[companionName]
        if animName not in companion["anims"]:
            return

        anim = companion["anims"][animName]

        self.actionTabs.clear()

        general = actiontabs.ActionTab_General(self.actionTabs, anim)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, animName)

        self.setCompanionSprite(companionName)
        self.animatorView.animator.setAnimation(anim)

    def populateAnimTabs(self, companionName, animName, frameInd):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        companion = characterdata.companionJson[companionName]
        if animName not in companion["anims"]:
            return

        actions = companion["anims"][animName]["frames"][frameInd]
        
        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                self.actionTabs.addTab(widget, action)

        self.setCompanionSprite(companionName)
        self.animatorView.animator.setAnimation(companion["anims"][animName])
        self.animatorView.animator.setFrame(frameInd)

    def addCompanion(self, companionName):
        companionTree = QtWidgets.QTreeWidgetItem([companionName])
        companionTree.itemLevel = 0
        addAnimation = QtWidgets.QTreeWidgetItem(companionTree, ["Add animation..."])
        addAnimation.itemLevel = -2
        self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, companionTree)

        characterdata.companionJson[companionName] = characterdata.defaultCompanion()
        return companionTree

    def addAnimation(self, companionTree, animName):
        companionName = companionTree.text(0)
        animInd = companionTree.childCount()-1
        animTree = QtWidgets.QTreeWidgetItem([animName])
        animTree.itemLevel = 1
        addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
        addFrame.itemLevel = -3
        companionTree.insertChild(animInd, animTree)

        characterdata.companionJson[companionName]["anims"][animName] = {"frames": []}
        return animTree

    def addFrame(self, animTree):
        frameInd = animTree.childCount()-1
        rootFrameTree = QtWidgets.QTreeWidgetItem([ "Frame %d" % (frameInd+1) ])
        rootFrameTree.itemLevel = 2
        rootFrameTree.frame = frameInd
        animTree.insertChild(frameInd, rootFrameTree)
        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
        addAction.itemLevel = -4

        companionTree = animTree.parent()
        animName = animTree.text(0)
        companionName = companionTree.text(0)
        characterdata.companionJson[companionName]["anims"][animName]["frames"].append({})

        self.addAction("delay", rootFrameTree)
        if len(characterdata.companionJson[companionName]["anims"][animName]["frames"]) == 1:
            self.addAction("frame", rootFrameTree)

        return rootFrameTree

    def addAction(self, actionName, rootFrameTree):
        animTree = rootFrameTree.parent()
        companionTree = animTree.parent()
        frameInd = animTree.indexOfChild(rootFrameTree)
        animName = animTree.text(0)
        companionName = companionTree.text(0)

        if actionName in characterdata.companionJson[companionName]["anims"][animName]["frames"][frameInd]:
            return None

        thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
        thisFrameTree.itemLevel = 3
        rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

        characterdata.companionJson[companionName]["anims"][animName]["frames"][frameInd][actionName] = characterdata.defaultAction(actionName)
        return thisFrameTree

    def addNecessaryAnimations(self, companionTree):
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
            "BurstVictoryStrike",
            "BurstVictoryStrike_MR",
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
            animTree = self.addAnimation(companionTree, animName)

    def reloadTree(self):
        self.animationsTree.clear()

        addCompanion = QtWidgets.QTreeWidgetItem(self.animationsTree, ["New companion..."])
        addCompanion.itemLevel = -1

        for companionName in characterdata.companionJson:
            companion = characterdata.companionJson[companionName]
            companionTree = QtWidgets.QTreeWidgetItem([companionName])
            companionTree.itemLevel = 0

            for animName in companion.get("anims", {}):
                anim = companion["anims"][animName]
                animTree = QtWidgets.QTreeWidgetItem(companionTree, [animName])
                animTree.itemLevel = 1

                if "frames" in anim:
                    frames = anim["frames"]
                    for frameInd in range(len(frames)):
                        frameDict = frames[frameInd]
                        rootFrameTree = QtWidgets.QTreeWidgetItem(animTree, [ "Frame %d" % (frameInd+1) ] )
                        rootFrameTree.itemLevel = 2
                        for frameName in frameDict:
                            frame = frameDict[frameName]
                            thisFrameTree = QtWidgets.QTreeWidgetItem(rootFrameTree, [frameName])
                            thisFrameTree.itemLevel = 3
                        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                        addAction.itemLevel = -4

                addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
                addFrame.itemLevel = -3

            addAnim = QtWidgets.QTreeWidgetItem(companionTree, ["Add animation..."])
            addAnim.itemLevel = -2
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, companionTree)


    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onAnimationTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.populateCompanionTab(current.text(0))
        if current.itemLevel == 1:
            companionTree = current.parent()
            companionName = companionTree.text(0)
            self.populateGeneralTab(companionName, current.text(0))
        if current.itemLevel == 2:
            animTree = current.parent()
            companionTree = animTree.parent()
            frameInd = animTree.indexOfChild(current)
            animName = animTree.text(0)
            companionName = companionTree.text(0)
            self.populateAnimTabs(companionName, animName, frameInd)
        if current.itemLevel == 3:
            rootFrameTree = current.parent()
            animTree = rootFrameTree.parent()
            companionTree = animTree.parent()
            actionInd = rootFrameTree.indexOfChild(current)
            frameInd = animTree.indexOfChild(rootFrameTree)
            animName = animTree.text(0)
            companionName = companionTree.text(0)
            self.populateAnimTabs(companionName, animName, frameInd)
            self.actionTabs.setCurrentIndex(actionInd)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onAnimationTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            name, ok = QtWidgets.QInputDialog.getText(self, "New companion", "Enter a name for the companion character")
            if ok:
                if name in characterdata.companionJson:
                    QtWidgets.QMessageBox.warning(self, "Error", "Companion '%s' already exists" % name)
                    return

                companionTree = self.addCompanion(name)
                characterdata.createCompanionDir(name)

                result = QtWidgets.QMessageBox.question(self, "Add animations?",
                    "Would you like to add all base character animation entries to this companion?\n" + 
                    "\n" +
                    "If you're making a transformation for the base character, click Yes\n" +
                    "If you're making an NPC, click No",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )

                if result == QtWidgets.QMessageBox.Yes:
                    self.addNecessaryAnimations(companionTree)

                self.populateCompanionTab(name)
                QtWidgets.QMessageBox.information(self, "Done", "Companion '%s' created.\nYou must add a sprite sheet image in the companion folder, named 'sheet.png'." % name)

        if item.itemLevel == -2:
            companionTree = item.parent()
            companionName = companionTree.text(0)
            animName, ok = QtWidgets.QInputDialog.getText(self, "Add animation", "Enter a name for the animation")
            if ok:
                if animName in characterdata.companionJson[companionName]["anims"]:
                    QtWidgets.QMessageBox.warning(self, "Error", "Animation '%s' already exists" % animName)
                    return

                self.addAnimation(companionTree, animName)

        if item.itemLevel == -3:
            animTree = item.parent()
            self.addFrame(animTree)

        if item.itemLevel == -4:
            actionDialog = actiontabs.ActionDialog(self)
            if actionDialog.exec():
                actionName = actionDialog.comboBox.currentText()
                rootFrameTree = item.parent()
                animTree = rootFrameTree.parent()
                companionTree = animTree.parent()
                frameInd = animTree.indexOfChild(rootFrameTree)
                animName = animTree.text(0)
                companionName = companionTree.text(0)

                actionTree = self.addAction(actionName, rootFrameTree)
                if not actionTree:
                    QtWidgets.QMessageBox.warning(self, "Error", "Action '%s' already exists" % actionName)
                    return

                self.populateAnimTabs(companionName, animName, frameInd)
                self.actionTabs.setCurrentIndex(rootFrameTree.indexOfChild(actionTree))

    @QtCore.pyqtSlot(QtCore.QPoint)
    def onAnimationTreeContextMenu(self, point):
        item = self.animationsTree.itemAt(point)
        if item.itemLevel < 0: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 1:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateAnim)
            actionRename.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == 2:
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            actionDuplicate = menu.addAction("Duplicate")
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        actionDelete = menu.addAction("Delete")
        actionDelete.triggered.connect(self.onMenuActionDelete)
        actionDelete.setData(item)

        menu.exec(self.animationsTree.mapToGlobal(point))

    @QtCore.pyqtSlot()
    def onMenuActionRename(self):
        animTree = self.sender().data()
        companionTree = item.parent()
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename animation", "Rename the animation '%s' to..." % oldName)
        if not ok or not newName: return

        newAnimsDict = {}
        for anim in companion["anims"]:
            newAnimsDict[newName if anim == oldName else anim] = companion["anims"][anim]

        companion["anims"] = newAnimsDict
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateAnim(self):
        item = self.sender().data()
        companionTree = item.parent()
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate animation", "Enter a name for the duplicated animation")
        if not ok or not newName: return

        newAnimsDict = {}
        for anim in companion["anims"]:
            newAnimsDict[anim] = companion["anims"][anim]
            if anim == oldName:
                newAnimsDict[newName] = copy.deepcopy(companion["anims"][anim])

        companion["anims"] = newAnimsDict
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateFrame(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        duplicatedFrame = copy.deepcopy(companion["anims"][animName]["frames"][frameInd])
        companion["anims"][animName]["frames"].insert(frameInd, duplicatedFrame)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveTop(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]
        if frameInd == 0: return

        anim = companion["anims"][animName]["frames"].pop(frameInd)
        companion["anims"][animName]["frames"].insert(0, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveUp(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]
        if frameInd == 0: return

        anim = companion["anims"][animName]["frames"].pop(frameInd)
        companion["anims"][animName]["frames"].insert(frameInd-1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDown(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]
        if frameInd >= len(characterdata.jsonFile["anims"][animName]["frames"])-1: return

        anim = companion["anims"][animName]["frames"].pop(frameInd)
        companion["anims"][animName]["frames"].insert(frameInd+1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveBottom(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]
        if frameInd >= len(characterdata.jsonFile["anims"][animName]["frames"])-1: return

        anim = companion["anims"][animName]["frames"].pop(frameInd)
        companion["anims"][animName]["frames"].append(anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDelete(self):
        message = ""
        item = self.sender().data()

        if item.itemLevel == 0:
            companionName = item.text(0)
            message = "You are about to delete the companion character '%s'.\nThis will also delete the '%s' directory from the companions folder.\nAre you sure?" % (companionName, companionName)
        elif item.itemLevel == 1:
            animName = item.text(0)
            message = "You are about to delete the animation '%s'.\nAre you sure?" % animName
        elif item.itemLevel == 2:
            animTree = item.parent()
            animName = animTree.text(0)
            message = "You are about to delete %s from the animation '%s'.\nAre you sure?" % (item.text(0), animName)
        elif item.itemLevel == 3:
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
            characterdata.deleteCompanion(item.text(0))
        elif item.itemLevel == 1:
            companionTree = item.parent()
            companionName = companionTree.text(0)
            del characterdata.companionJson[companionName]["anims"][item.text(0)]
        elif item.itemLevel == 2:
            animTree = item.parent()
            companionTree = animTree.parent()
            animName = animTree.text(0)
            frameInd = animTree.indexOfChild(item)
            companionName = companionTree.text(0)
            del characterdata.companionJson[companionName]["anims"][animName]["frames"][frameInd]
        elif item.itemLevel == 3:
            rootFrameTree = item.parent()
            animTree = rootFrameTree.parent()
            companionTree = animTree.parent()
            animName = animTree.text(0)
            frameInd = animTree.indexOfChild(rootFrameTree)
            companionName = companionTree.text(0)
            del characterdata.companionJson[companionName]["anims"][animName]["frames"][frameInd][item.text(0)]

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onRefresh(self):
        self.animatorView.animator.refresh()
