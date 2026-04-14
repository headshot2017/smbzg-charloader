import os
import copy

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import characterdata
import actiontabs
import frameClipboard


class BaseAnimatorWidget(QtWidgets.QWidget):
    def __init__(self, file):
        super().__init__()
        uic.loadUi(file, self)

        self.btn_stop.clicked.connect(self.onStop)
        self.btn_play.clicked.connect(self.onPlay)
        self.btn_zoomIn.clicked.connect(self.onZoomIn)
        self.btn_zoomOut.clicked.connect(self.onZoomOut)
        self.btn_zoomReset.clicked.connect(self.onZoomReset)

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

    def setInactivePuppets(self, on):
        self.animatorView.animator.setInactivePuppets(on)


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

    @QtCore.pyqtSlot()
    def onZoomIn(self):
        self.animatorView.scale(1.25, 1.25)

    @QtCore.pyqtSlot()
    def onZoomOut(self):
        self.animatorView.scale(0.8, 0.8)

    @QtCore.pyqtSlot()
    def onZoomReset(self):
        self.animatorView.resetTransform()


class CharacterAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__("ui/animatorwidget.ui")

        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)

        self.puppetsTree.currentItemChanged.connect(self.onPuppetTreeChange)
        self.puppetsTree.itemDoubleClicked.connect(self.onPuppetTreeDoubleClick)
        self.puppetsTree.customContextMenuRequested.connect(self.onPuppetTreeContextMenu)

        self.btn_zoomInP.clicked.connect(self.onZoomInPuppet)
        self.btn_zoomOutP.clicked.connect(self.onZoomOutPuppet)
        self.btn_zoomResetP.clicked.connect(self.onZoomResetPuppet)

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

        general = actiontabs.ActionTab_General(self.actionTabs, characterdata.jsonFile["editor"], anim)
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
                widget = actiontabs.actionTabsDict[action](self.actionTabs, characterdata.jsonFile["editor"], actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                widget.setupForCharacter(characterdata.jsonFile)
                self.actionTabs.addTab(widget, action)

        self.animatorView.animator.setAnimation(characterdata.jsonFile["anims"][animName])
        self.animatorView.animator.setFrame(frameInd)

    def populatePuppetTab(self, puppetName):
        if not characterdata.jsonFile or puppetName not in characterdata.jsonFile["puppets"]:
            return

        puppet = characterdata.jsonFile["puppets"][puppetName]

        self.puppetsTabs.clear()

        general = actiontabs.PuppetTab(self.puppetsTabs, characterdata.jsonFile["editor"], puppet)
        general.valueChanged.connect(self.onActionTabValueChangePuppet)
        self.puppetsTabs.addTab(general, puppetName)

        self.puppetView.animator.setAnimation( {"frames": [{"frame": puppet}]} )

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

        theAction = characterdata.defaultAction(actionName)
        if actionName == "delay":
            theAction = characterdata.jsonFile["editor"]["defaultDelay"]

        characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName] = theAction
        return thisFrameTree

    def addPuppet(self, puppetName):
        puppetTree = QtWidgets.QTreeWidgetItem([puppetName])
        puppetTree.itemLevel = 0
        self.puppetsTree.insertTopLevelItem(self.puppetsTree.topLevelItemCount()-1, puppetTree)

        characterdata.jsonFile["puppets"][puppetName] = [0, 0, 0, 0]
        return puppetTree

    def addNecessaryAnimations(self):
        for anim in characterdata.defaultAnimationEntries():
            animName, loopCount = anim
            animTree = self.addAnimation(animName)
            characterdata.jsonFile["anims"][animName]["loops"] = loopCount

    def reloadTree(self):
        expanded = {}
        for i in range(self.animationsTree.topLevelItemCount()):
            animItem = self.animationsTree.topLevelItem(i)
            if not animItem.isExpanded(): continue

            expanded[animItem.text(0)] = {}
            for j in range(animItem.childCount()):
                frameItem = animItem.child(j)
                if not frameItem.isExpanded(): continue

                expanded[animItem.text(0)][frameItem.text(0)] = False

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

                    if animName in expanded and rootFrameTree.text(0) in expanded[animName]:
                        expanded[animName][rootFrameTree.text(0)] = rootFrameTree

                    addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                    addAction.itemLevel = -3

            addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
            addFrame.itemLevel = -2
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

            if animName in expanded:
                animTree.setExpanded(True)
                for k in expanded[animName]:
                    if not expanded[animName][k]: continue
                    expanded[animName][k].setExpanded(True)

    def reloadPuppetsTree(self):
        self.puppetsTree.clear()

        addPuppet = QtWidgets.QTreeWidgetItem(self.puppetsTree, ["Add puppet..."])
        addPuppet.itemLevel = -1

        for puppetName in characterdata.jsonFile["puppets"]:
            puppetTree = QtWidgets.QTreeWidgetItem([puppetName])
            puppetTree.itemLevel = 0
            self.puppetsTree.insertTopLevelItem(self.puppetsTree.topLevelItemCount()-1, puppetTree)


    @QtCore.pyqtSlot()
    def onActionTabValueChangePuppet(self):
        self.puppetView.animator.refresh()
        self.animatorView.animator.updatePuppetList(characterdata.jsonFile["puppets"])

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
        if item.itemLevel < 0 and item.itemLevel > -2: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 0: # animation
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            menu.addSeparator()

            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateAnim)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUpAnim)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDownAnim)

            actionRename.setData(item)
            actionDuplicate.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)

        elif item.itemLevel == 1: # frame
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            menu.addSeparator()

            actionCut.triggered.connect(self.onMenuActionCut)
            actionCopy.triggered.connect(self.onMenuActionCopy)
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == 2: # action
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")

            actionCut.triggered.connect(self.onMenuActionCutAction)
            actionCopy.triggered.connect(self.onMenuActionCopyAction)
            actionPaste.triggered.connect(self.onMenuActionPasteAction)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)

        elif item.itemLevel == -2: # 'Add frame'
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionPaste.setData(item)

        elif item.itemLevel == -3: # 'Add action'
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPasteAction)
            actionPaste.setData(item)

        if item.itemLevel >= 0: # animation, frame or action
            actionDelete = menu.addAction("Delete")
            actionDelete.triggered.connect(self.onMenuActionDelete)
            actionDelete.setData(item)

        menu.exec(self.animationsTree.mapToGlobal(point))

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onPuppetTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.populatePuppetTab(current.text(0))

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onPuppetTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            puppetName, ok = QtWidgets.QInputDialog.getText(self, "Add puppet", "Enter a name for the new puppet")
            if ok:
                if puppetName in characterdata.jsonFile["puppets"]:
                    QtWidgets.QMessageBox.warning(self, "Error", "Puppet '%s' already exists" % puppetName)
                    return

                self.addPuppet(puppetName)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def onPuppetTreeContextMenu(self, point):
        item = self.puppetsTree.itemAt(point)
        if item.itemLevel < 0: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 0:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            actionRename.triggered.connect(self.onMenuActionRenamePuppet)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicatePuppet)
            actionRename.setData(item)
            actionDuplicate.setData(item)

        actionDelete = menu.addAction("Delete")
        actionDelete.triggered.connect(self.onMenuActionDeletePuppet)
        actionDelete.setData(item)

        menu.exec(self.puppetsTree.mapToGlobal(point))

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
    def onMenuActionMoveUpAnim(self):
        item = self.sender().data()
        animName = item.text(0)
        keyList = [k for k in characterdata.jsonFile["anims"].keys()]
        animInd = keyList.index(animName)
        if animInd == 0: return

        animKey = keyList.pop(animInd)
        keyList.insert(animInd-1, animKey)

        newAnimsDict = {}
        for anim in keyList:
            newAnimsDict[anim] = characterdata.jsonFile["anims"][anim]
        characterdata.jsonFile["anims"] = newAnimsDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDownAnim(self):
        item = self.sender().data()
        animName = item.text(0)
        keyList = [k for k in characterdata.jsonFile["anims"].keys()]
        animInd = keyList.index(animName)
        if animInd >= len(keyList)-1: return

        animKey = keyList.pop(animInd)
        keyList.insert(animInd+1, animKey)

        newAnimsDict = {}
        for anim in keyList:
            newAnimsDict[anim] = characterdata.jsonFile["anims"][anim]
        characterdata.jsonFile["anims"] = newAnimsDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCut(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        frameClipboard.frame = copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd])
        del characterdata.jsonFile["anims"][animName]["frames"][frameInd]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopy(self):
        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        frameClipboard.frame = copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd])

    @QtCore.pyqtSlot()
    def onMenuActionPaste(self):
        if not frameClipboard.frame:
            return

        item = self.sender().data()
        animTree = item.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        characterdata.jsonFile["anims"][animName]["frames"].insert(frameInd, copy.deepcopy(frameClipboard.frame))

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
    def onMenuActionCutAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        frameClipboard.action = [actionName, copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName])]
        del characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopyAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        frameClipboard.action = [actionName, copy.deepcopy(characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName])]

    @QtCore.pyqtSlot()
    def onMenuActionPasteAction(self):
        if not frameClipboard.action:
            return

        item = self.sender().data()
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        actionName, action = frameClipboard.action

        if actionName in characterdata.jsonFile["anims"][animName]["frames"][frameInd]:
            result = QtWidgets.QMessageBox.warning(self,
                "Warning",
                "The action '%s' already exists in Frame %d of animation '%s'.\nOverwrite it with clipboard contents?" % (actionName, frameInd+1, animName),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if result != QtWidgets.QMessageBox.Yes: return

        characterdata.jsonFile["anims"][animName]["frames"][frameInd][actionName] = copy.deepcopy(frameClipboard.action[1])

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
    def onMenuActionRenamePuppet(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename puppet", "Rename the puppet '%s' to..." % oldName)
        if not ok or not newName: return

        newPuppetsDict = {}
        for puppet in characterdata.jsonFile["puppets"]:
            newPuppetsDict[newName if puppet == oldName else puppet] = characterdata.jsonFile["puppets"][puppet]

        characterdata.jsonFile["puppets"] = newPuppetsDict
        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.jsonFile["puppets"])

    @QtCore.pyqtSlot()
    def onMenuActionDuplicatePuppet(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate puppet", "Enter a name for the duplicated puppet")
        if not ok or not newName: return

        newPuppetsDict = {}
        for puppet in characterdata.jsonFile["puppets"]:
            newPuppetsDict[puppet] = characterdata.jsonFile["puppets"][puppet]
            if puppet == oldName:
                newPuppetsDict[newName] = copy.deepcopy(characterdata.jsonFile["puppets"][puppet])

        characterdata.jsonFile["puppets"] = newPuppetsDict
        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.jsonFile["puppets"])

    @QtCore.pyqtSlot()
    def onMenuActionDeletePuppet(self):
        message = ""
        item = self.sender().data()

        if item.itemLevel == 0:
            message = "You are about to delete the puppet '%s'.\nAre you sure?" % item.text(0)

        result = QtWidgets.QMessageBox.warning(self, "Warning", message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result != QtWidgets.QMessageBox.Yes: return

        if item.itemLevel == 0:
            del characterdata.jsonFile["puppets"][item.text(0)]

        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.jsonFile["puppets"])

    @QtCore.pyqtSlot()
    def onRefresh(self):
        path = gamepath.getCharacterPath(characterdata.name)

        for view in [self.animatorView, self.puppetView]:
            view.animator.globalOffset = characterdata.jsonFile["general"]["offset"]["ingame"]
            view.animator.globalScale = characterdata.jsonFile["general"]["scale"]["ingame"]
            view.reloadSprite("%s/sheet.png" % path)
            characterdata.jsonFile["editor"]["imgW"] = view.animator.fullPixmap.size().width()
            characterdata.jsonFile["editor"]["imgH"] = view.animator.fullPixmap.size().height()
        self.animatorView.animator.updatePuppetList(characterdata.jsonFile["puppets"])

    @QtCore.pyqtSlot()
    def onZoomInPuppet(self):
        self.puppetView.scale(1.25, 1.25)

    @QtCore.pyqtSlot()
    def onZoomOutPuppet(self):
        self.puppetView.scale(0.8, 0.8)

    @QtCore.pyqtSlot()
    def onZoomResetPuppet(self):
        self.puppetView.resetTransform()


class EffectAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__("ui/animatoreffectwidget.ui")

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
        fx["editor"]["imgW"] = self.animatorView.animator.fullPixmap.size().width()
        fx["editor"]["imgH"] = self.animatorView.animator.fullPixmap.size().height()

    def populateGeneralTab(self, fxName):
        if not characterdata.jsonFile or fxName not in characterdata.jsonFile["effects"]:
            return

        if "editor" not in characterdata.jsonFile["effects"][fxName]:
            characterdata.jsonFile["effects"][fxName]["editor"] = characterdata.defaultEffect()["editor"]

        self.currentFx = fxName
        self.refreshFx()

        fx = characterdata.jsonFile["effects"][fxName]
        if "loops" not in fx: fx["loops"] = 0

        self.actionTabs.clear()

        general = actiontabs.ActionTab_GeneralEffect(self.actionTabs, fx["editor"], fx)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, fxName)

        self.animatorView.animator.setAnimation(fx)

    def populateAnimTabs(self, fxName, frameInd):
        if not characterdata.jsonFile or fxName not in characterdata.jsonFile["effects"]:
            return

        if "editor" not in characterdata.jsonFile["effects"][fxName]:
            characterdata.jsonFile["effects"][fxName]["editor"] = characterdata.defaultEffect()["editor"]

        self.currentFx = fxName
        self.refreshFx()

        fx = characterdata.jsonFile["effects"][fxName]
        if "loops" not in fx: fx["loops"] = 0

        actions = fx["frames"][frameInd]

        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, fx["editor"], actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                self.actionTabs.addTab(widget, action)

        self.animatorView.animator.setAnimation(fx)
        self.animatorView.animator.setFrame(frameInd)

    def addEffect(self, fxName):
        animTree = QtWidgets.QTreeWidgetItem([fxName])
        animTree.itemLevel = 0
        addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
        addFrame.itemLevel = -2
        self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, animTree)

        characterdata.jsonFile["effects"][fxName] = characterdata.defaultEffect()
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

        theAction = characterdata.defaultAction(actionName)
        if actionName == "delay":
            theAction = characterdata.jsonFile["editor"]["defaultDelay"]

        characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName] = theAction
        return thisFrameTree

    def reloadTree(self):
        expanded = {}
        for i in range(self.animationsTree.topLevelItemCount()):
            animItem = self.animationsTree.topLevelItem(i)
            if not animItem.isExpanded(): continue

            expanded[animItem.text(0)] = {}
            for j in range(animItem.childCount()):
                frameItem = animItem.child(j)
                if not frameItem.isExpanded(): continue

                expanded[animItem.text(0)][frameItem.text(0)] = False

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

                    if fxName in expanded and rootFrameTree.text(0) in expanded[fxName]:
                        expanded[fxName][rootFrameTree.text(0)] = rootFrameTree

                    addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                    addAction.itemLevel = -3

            addFrame = QtWidgets.QTreeWidgetItem(fxTree, ["Add frame..."])
            addFrame.itemLevel = -2
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, fxTree)

            if fxName in expanded:
                fxTree.setExpanded(True)
                for k in expanded[fxName]:
                    if not expanded[fxName][k]: continue
                    expanded[fxName][k].setExpanded(True)


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
        if item.itemLevel < 0 and item.itemLevel > -2: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 0:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            menu.addSeparator()

            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateAnim)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUpAnim)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDownAnim)

            actionRename.setData(item)
            actionDuplicate.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)

        elif item.itemLevel == 1:
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            menu.addSeparator()

            actionCut.triggered.connect(self.onMenuActionCut)
            actionCopy.triggered.connect(self.onMenuActionCopy)
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == 2: # action
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")

            actionCut.triggered.connect(self.onMenuActionCutAction)
            actionCopy.triggered.connect(self.onMenuActionCopyAction)
            actionPaste.triggered.connect(self.onMenuActionPasteAction)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)

        elif item.itemLevel == -2:
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionPaste.setData(item)

        elif item.itemLevel == -3:
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPasteAction)
            actionPaste.setData(item)

        if item.itemLevel >= 0:
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
    def onMenuActionMoveUpAnim(self):
        item = self.sender().data()
        fxName = item.text(0)
        keyList = [k for k in characterdata.jsonFile["effects"].keys()]
        fxInd = keyList.index(fxName)
        if fxInd == 0: return

        fxKey = keyList.pop(fxInd)
        keyList.insert(fxInd-1, fxKey)

        newFxDict = {}
        for fx in keyList:
            newFxDict[fx] = characterdata.jsonFile["effects"][fx]
        characterdata.jsonFile["effects"] = newFxDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDownAnim(self):
        item = self.sender().data()
        fxName = item.text(0)
        keyList = [k for k in characterdata.jsonFile["effects"].keys()]
        fxInd = keyList.index(fxName)
        if fxInd >= len(keyList)-1: return

        fxKey = keyList.pop(fxInd)
        keyList.insert(fxInd+1, fxKey)

        newFxDict = {}
        for fx in keyList:
            newFxDict[fx] = characterdata.jsonFile["effects"][fx]
        characterdata.jsonFile["effects"] = newFxDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCut(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        frameClipboard.frame = copy.deepcopy(characterdata.jsonFile["effects"][fxName]["frames"][frameInd])
        del characterdata.jsonFile["effects"][fxName]["frames"][frameInd]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopy(self):
        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        frameClipboard.frame = copy.deepcopy(characterdata.jsonFile["effects"][fxName]["frames"][frameInd])

    @QtCore.pyqtSlot()
    def onMenuActionPaste(self):
        if not frameClipboard.frame:
            return

        item = self.sender().data()
        animTree = item.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        characterdata.jsonFile["effects"][fxName]["frames"].insert(frameInd, copy.deepcopy(frameClipboard.frame))

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
    def onMenuActionCutAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        frameClipboard.action = [actionName, copy.deepcopy(characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName])]
        del characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopyAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        frameClipboard.action = [actionName, copy.deepcopy(characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName])]

    @QtCore.pyqtSlot()
    def onMenuActionPasteAction(self):
        if not frameClipboard.action:
            return

        item = self.sender().data()
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        fxName = animTree.text(0)
        frameInd = animTree.indexOfChild(frameTree)

        actionName, action = frameClipboard.action

        if actionName in characterdata.jsonFile["effects"][fxName]["frames"][frameInd]:
            result = QtWidgets.QMessageBox.warning(self,
                "Warning",
                "The action '%s' already exists in Frame %d of effect '%s'.\nOverwrite it with clipboard contents?" % (actionName, frameInd+1, fxName),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if result != QtWidgets.QMessageBox.Yes: return

        characterdata.jsonFile["effects"][fxName]["frames"][frameInd][actionName] = copy.deepcopy(frameClipboard.action[1])

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
        super().__init__("ui/animatorwidget.ui")

        self.animationsTree.setHeaderLabel("Companions")
        self.animationsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.animationsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)

        self.puppetsTree.currentItemChanged.connect(self.onPuppetTreeChange)
        self.puppetsTree.itemDoubleClicked.connect(self.onPuppetTreeDoubleClick)
        self.puppetsTree.customContextMenuRequested.connect(self.onPuppetTreeContextMenu)

        self.btn_zoomInP.clicked.connect(self.onZoomInPuppet)
        self.btn_zoomOutP.clicked.connect(self.onZoomOutPuppet)
        self.btn_zoomResetP.clicked.connect(self.onZoomResetPuppet)

        self.btn_reloadSprite.clicked.connect(self.onRefresh)

    def reset(self):
        super().reset()

        addCompanion = QtWidgets.QTreeWidgetItem(self.animationsTree, ["New companion..."])
        addCompanion.itemLevel = -1

    def setCompanionSprite(self, view, companionName):
        companion = characterdata.companionJson[companionName]
        path = gamepath.getCharacterPath(characterdata.name)

        view.reloadSprite("%s/companions/%s/sheet.png" % (path, companionName))
        companion["editor"]["imgW"] = view.animator.fullPixmap.size().width()
        companion["editor"]["imgH"] = view.animator.fullPixmap.size().height()

        view.animator.globalOffset = companion.get("general", {}).get("offset", [0, 0])
        view.animator.globalScale = companion.get("general", {}).get("scale", 1)
        if view == self.animatorView:
            view.animator.updatePuppetList(companion["puppets"])

    def populateCompanionTab(self, companionName):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        if "editor" not in characterdata.companionJson[companionName]:
            characterdata.companionJson[companionName]["editor"] = characterdata.defaultCompanion()["editor"]

        self.actionTabs.clear()
        self.setCompanionSprite(self.animatorView, companionName)

        general = actiontabs.ActionTab_Companion(self.actionTabs, characterdata.companionJson[companionName]["editor"], companionName)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, companionName)

    def populateGeneralTab(self, companionName, animName):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        companion = characterdata.companionJson[companionName]
        if animName not in companion["anims"]:
            return

        if "editor" not in companion:
            companion["editor"] = characterdata.defaultCompanion()["editor"]

        anim = companion["anims"][animName]
        self.setCompanionSprite(self.animatorView, companionName)
        self.animatorView.animator.setAnimation(anim)

        self.actionTabs.clear()

        general = actiontabs.ActionTab_General(self.actionTabs, companion["editor"], anim)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, animName)

    def populateAnimTabs(self, companionName, animName, frameInd):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return

        companion = characterdata.companionJson[companionName]
        if animName not in companion["anims"]:
            return

        if "editor" not in companion:
            companion["editor"] = characterdata.defaultCompanion()["editor"]

        self.setCompanionSprite(self.animatorView, companionName)
        self.animatorView.animator.setAnimation(companion["anims"][animName])
        self.animatorView.animator.setFrame(frameInd)

        actions = companion["anims"][animName]["frames"][frameInd]

        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, companion["editor"], actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                widget.setupForCharacter(companion)
                self.actionTabs.addTab(widget, action)

    def populatePuppetTab(self, companionName, puppetName):
        if not characterdata.companionJson or companionName not in characterdata.companionJson:
            return
        companion = characterdata.companionJson[companionName]
        if puppetName not in companion["puppets"]:
            return

        puppet = companion["puppets"][puppetName]

        self.puppetsTabs.clear()

        self.setCompanionSprite(self.puppetView, companionName)
        self.puppetView.animator.setAnimation( {"frames": [{"frame": puppet}]} )

        general = actiontabs.PuppetTab(self.puppetsTabs, companion["editor"], puppet)
        general.valueChanged.connect(self.onActionTabValueChangePuppet)
        self.puppetsTabs.addTab(general, puppetName)

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

        theAction = characterdata.defaultAction(actionName)
        if actionName == "delay":
            theAction = characterdata.jsonFile["editor"]["defaultDelay"]

        thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
        thisFrameTree.itemLevel = 3
        rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

        characterdata.companionJson[companionName]["anims"][animName]["frames"][frameInd][actionName] = theAction
        return thisFrameTree

    def addPuppet(self, companionTree, puppetName):
        companionName = companionTree.text(0)
        puppetInd = companionTree.childCount()-1
        puppetTree = QtWidgets.QTreeWidgetItem([puppetName])
        puppetTree.itemLevel = 1
        companionTree.insertChild(puppetInd, puppetTree)

        characterdata.companionJson[companionName]["puppets"][puppetName] = [0, 0, 0, 0]
        return puppetTree

    def addNecessaryAnimations(self, companionTree):
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        for anim in characterdata.defaultAnimationEntries():
            animName, loopCount = anim
            animTree = self.addAnimation(companionTree, animName)
            companion["anims"][animName]["loops"] = loopCount

    def reloadTree(self):
        expanded = {}
        for i in range(self.animationsTree.topLevelItemCount()):
            companionItem = self.animationsTree.topLevelItem(i)
            if not companionItem.isExpanded(): continue

            expanded[companionItem.text(0)] = {}
            for j in range(companionItem.childCount()):
                animItem = companionItem.child(j)
                if not animItem.isExpanded(): continue

                expanded[companionItem.text(0)][animItem.text(0)] = {}
                for k in range(animItem.childCount()):
                    frameItem = animItem.child(k)
                    if not frameItem.isExpanded(): continue

                    expanded[companionItem.text(0)][animItem.text(0)][frameItem.text(0)] = False

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

                        if companionName in expanded and animName in expanded[companionName] and rootFrameTree.text(0) in expanded[companionName][animName]:
                            expanded[companionName][animName][rootFrameTree.text(0)] = rootFrameTree

                        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                        addAction.itemLevel = -4

                if companionName in expanded and animName in expanded[companionName]:
                    expanded[companionName][animName][0] = animTree

                addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
                addFrame.itemLevel = -3

            addAnim = QtWidgets.QTreeWidgetItem(companionTree, ["Add animation..."])
            addAnim.itemLevel = -2
            self.animationsTree.insertTopLevelItem(self.animationsTree.topLevelItemCount()-1, companionTree)

            if companionName in expanded:
                companionTree.setExpanded(True)
                for animName in expanded[companionName]:
                    for k in expanded[companionName][animName]:
                        if not expanded[companionName][animName][k]: continue
                        expanded[companionName][animName][k].setExpanded(True)

    def reloadPuppetsTree(self):
        self.puppetsTree.clear()

        for companionName in characterdata.companionJson:
            companion = characterdata.companionJson[companionName]
            companionTree = QtWidgets.QTreeWidgetItem([companionName])
            companionTree.itemLevel = 0

            for puppetName in companion["puppets"]:
                puppetTree = QtWidgets.QTreeWidgetItem(companionTree, [puppetName])
                puppetTree.itemLevel = 1

            addPuppet = QtWidgets.QTreeWidgetItem(companionTree, ["Add puppet..."])
            addPuppet.itemLevel = -2

            self.puppetsTree.insertTopLevelItem(self.puppetsTree.topLevelItemCount(), companionTree)


    @QtCore.pyqtSlot()
    def onActionTabValueChangePuppet(self):
        companionName = self.puppetsTree.currentItem().parent().text(0)
        self.puppetView.animator.refresh()
        self.animatorView.animator.updatePuppetList(characterdata.companionJson[companionName]["puppets"])

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
        if item.itemLevel < 0 and item.itemLevel > -3: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 1:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            menu.addSeparator()

            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateAnim)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUpAnim)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDownAnim)

            actionRename.setData(item)
            actionDuplicate.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)

        elif item.itemLevel == 2:
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            menu.addSeparator()

            actionCut.triggered.connect(self.onMenuActionCut)
            actionCopy.triggered.connect(self.onMenuActionCopy)
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.triggered.connect(self.onMenuActionMoveTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveBottom)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == 3: # action
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")

            actionCut.triggered.connect(self.onMenuActionCutAction)
            actionCopy.triggered.connect(self.onMenuActionCopyAction)
            actionPaste.triggered.connect(self.onMenuActionPasteAction)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)

        elif item.itemLevel == -3:
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionPaste.setData(item)

        elif item.itemLevel == -4:
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPasteAction)
            actionPaste.setData(item)

        if item.itemLevel >= 0:
            actionDelete = menu.addAction("Delete")
            actionDelete.triggered.connect(self.onMenuActionDelete)
            actionDelete.setData(item)

        menu.exec(self.animationsTree.mapToGlobal(point))

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onPuppetTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.puppetsTabs.clear()
        elif current.itemLevel == 1:
            companionTree = current.parent()
            companionName = companionTree.text(0)
            self.populatePuppetTab(companionName, current.text(0))

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onPuppetTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -2:
            companionTree = item.parent()
            companionName = companionTree.text(0)
            puppetName, ok = QtWidgets.QInputDialog.getText(self, "Add puppet", "Enter a name for the new puppet")
            if ok:
                if puppetName in characterdata.companionJson[companionName]["puppets"]:
                    QtWidgets.QMessageBox.warning(self, "Error", "Puppet '%s' already exists" % puppetName)
                    return

                self.addPuppet(companionTree, puppetName)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def onPuppetTreeContextMenu(self, point):
        item = self.puppetsTree.itemAt(point)
        if item.itemLevel <= 0: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 1:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            actionRename.triggered.connect(self.onMenuActionRenamePuppet)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicatePuppet)
            actionRename.setData(item)
            actionDuplicate.setData(item)

        actionDelete = menu.addAction("Delete")
        actionDelete.triggered.connect(self.onMenuActionDeletePuppet)
        actionDelete.setData(item)

        menu.exec(self.puppetsTree.mapToGlobal(point))

    @QtCore.pyqtSlot()
    def onMenuActionRename(self):
        item = self.sender().data()
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
    def onMenuActionMoveUpAnim(self):
        item = self.sender().data()
        animName = item.text(0)
        companionTree = item.parent()
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        keyList = [k for k in companion["anims"].keys()]
        animInd = keyList.index(animName)
        if animInd == 0: return

        animKey = keyList.pop(animInd)
        keyList.insert(animInd-1, animKey)

        newAnimsDict = {}
        for anim in keyList:
            newAnimsDict[anim] = companion["anims"][anim]
        companion["anims"] = newAnimsDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveDownAnim(self):
        item = self.sender().data()
        animName = item.text(0)
        companionTree = item.parent()
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        keyList = [k for k in companion["anims"].keys()]
        animInd = keyList.index(animName)
        if animInd >= len(keyList)-1: return

        animKey = keyList.pop(animInd)
        keyList.insert(animInd+1, animKey)

        newAnimsDict = {}
        for anim in keyList:
            newAnimsDict[anim] = companion["anims"][anim]
        companion["anims"] = newAnimsDict

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCut(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        frameClipboard.frame = copy.deepcopy(companion["anims"][animName]["frames"][frameInd])
        del companion["anims"][animName]["frames"][frameInd]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopy(self):
        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        frameClipboard.frame = copy.deepcopy(companion["anims"][animName]["frames"][frameInd])

    @QtCore.pyqtSlot()
    def onMenuActionPaste(self):
        if not frameClipboard.frame:
            return

        item = self.sender().data()
        animTree = item.parent()
        companionTree = animTree.parent()
        animName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        companionName = companionTree.text(0)
        companion = characterdata.companionJson[companionName]

        companion["anims"][animName]["frames"].insert(frameInd, copy.deepcopy(frameClipboard.frame))

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
        if frameInd >= len(companion["anims"][animName]["frames"])-1: return

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
        if frameInd >= len(companion["anims"][animName]["frames"])-1: return

        anim = companion["anims"][animName]["frames"].pop(frameInd)
        companion["anims"][animName]["frames"].append(anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCutAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        companionTree = animTree.parent()
        companionName = companionTree.text(0)

        frameInd = animTree.indexOfChild(frameTree)
        companion = characterdata.companionJson[companionName]

        frameClipboard.action = [actionName, copy.deepcopy(companion["anims"][animName]["frames"][frameInd][actionName])]
        del companion["anims"][animName]["frames"][frameInd][actionName]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopyAction(self):
        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        companionTree = animTree.parent()
        companionName = companionTree.text(0)

        frameInd = animTree.indexOfChild(frameTree)
        companion = characterdata.companionJson[companionName]

        frameClipboard.action = [actionName, copy.deepcopy(companion["anims"][animName]["frames"][frameInd][actionName])]

    @QtCore.pyqtSlot()
    def onMenuActionPasteAction(self):
        if not frameClipboard.action:
            return

        item = self.sender().data()
        actionName = item.text(0)
        frameTree = item.parent()
        frameName = frameTree.text(0)
        animTree = frameTree.parent()
        animName = animTree.text(0)
        companionTree = animTree.parent()
        companionName = companionTree.text(0)

        frameInd = animTree.indexOfChild(frameTree)
        companion = characterdata.companionJson[companionName]

        actionName, action = frameClipboard.action

        if actionName in companion["anims"][animName]["frames"][frameInd]:
            result = QtWidgets.QMessageBox.warning(self,
                "Warning",
                "The action '%s' already exists in Frame %d of animation '%s'.\nOverwrite it with clipboard contents?" % (actionName, frameInd+1, animName),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if result != QtWidgets.QMessageBox.Yes: return

        companion["anims"][animName]["frames"][frameInd][actionName] = copy.deepcopy(frameClipboard.action[1])

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
        self.reloadPuppetsTree()

    @QtCore.pyqtSlot()
    def onMenuActionRenamePuppet(self):
        item = self.sender().data()
        companionTree = item.parent()
        companionName = companionTree.text(0)
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename puppet", "Rename the puppet '%s' to..." % oldName)
        if not ok or not newName: return

        newPuppetsDict = {}
        for puppet in characterdata.companionJson[companionName]["puppets"]:
            newPuppetsDict[newName if puppet == oldName else puppet] = characterdata.companionJson[companionName]["puppets"][puppet]

        characterdata.companionJson[companionName]["puppets"] = newPuppetsDict
        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.companionJson[companionName]["puppets"])

    @QtCore.pyqtSlot()
    def onMenuActionDuplicatePuppet(self):
        item = self.sender().data()
        companionTree = item.parent()
        companionName = companionTree.text(0)
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate puppet", "Enter a name for the duplicated puppet")
        if not ok or not newName: return

        newPuppetsDict = {}
        for puppet in characterdata.companionJson[companionName]["puppets"]:
            newPuppetsDict[puppet] = characterdata.companionJson[companionName]["puppets"][puppet]
            if puppet == oldName:
                newPuppetsDict[newName] = copy.deepcopy(characterdata.companionJson[companionName]["puppets"][puppet])

        characterdata.companionJson[companionName]["puppets"] = newPuppetsDict
        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.companionJson[companionName]["puppets"])

    @QtCore.pyqtSlot()
    def onMenuActionDeletePuppet(self):
        message = ""
        item = self.sender().data()
        companionTree = item.parent()
        companionName = companionTree.text(0)

        if item.itemLevel == 1:
            message = "You are about to delete the puppet '%s'.\nAre you sure?" % item.text(0)

        result = QtWidgets.QMessageBox.warning(self, "Warning", message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result != QtWidgets.QMessageBox.Yes: return

        if item.itemLevel == 1:
            del characterdata.companionJson[companionName]["puppets"][item.text(0)]

        self.reloadPuppetsTree()
        self.animatorView.animator.updatePuppetList(characterdata.companionJson[companionName]["puppets"])

    @QtCore.pyqtSlot()
    def onRefresh(self):
        self.animatorView.animator.refresh()
        self.puppetView.animator.refresh()

    @QtCore.pyqtSlot()
    def onZoomInPuppet(self):
        self.puppetView.scale(1.25, 1.25)

    @QtCore.pyqtSlot()
    def onZoomOutPuppet(self):
        self.puppetView.scale(0.8, 0.8)

    @QtCore.pyqtSlot()
    def onZoomResetPuppet(self):
        self.puppetView.resetTransform()
