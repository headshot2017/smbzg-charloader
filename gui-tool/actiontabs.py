import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import characterdata
import gamepath


class BaseActionTab(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

class ActionTab_General(BaseActionTab):
    def __init__(self, parent, anim):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_general.ui", self)

        self.anim = anim

        self.checkbox_interpolate.setChecked(anim["interpolate"] if "interpolate" in anim else True)
        self.spinbox_loops.setValue(anim["loops"] if "loops" in anim else -1)
        self.spinbox_offsetX.setValue(anim["offset"][0] if "offset" in anim else 0)
        self.spinbox_offsetY.setValue(anim["offset"][1] if "offset" in anim else 0)
        self.spinbox_scaleX.setValue(anim["scale"][0] if "scale" in anim else 1)
        self.spinbox_scaleY.setValue(anim["scale"][1] if "scale" in anim else 1)

        self.checkbox_interpolate.stateChanged.connect(self.onSetInterpolate)
        self.spinbox_loops.valueChanged.connect(self.onChangeLoops)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)

    @QtCore.pyqtSlot(int)
    def onSetInterpolate(self, value):
        self.anim["interpolate"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeLoops(self, value):
        self.anim["loops"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetX(self, value):
        if "offset" not in self.anim: self.anim["offset"] = [0, 0]
        self.anim["offset"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetY(self, value):
        if "offset" not in self.anim: self.anim["offset"] = [0, 0]
        self.anim["offset"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleX(self, value):
        if "scale" not in self.anim: self.anim["scale"] = [1, 1]
        self.anim["scale"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleY(self, value):
        if "scale" not in self.anim: self.anim["scale"] = [1, 1]
        self.anim["scale"][1] = value
        self.valueChanged.emit()


class ActionTab_GeneralEffect(BaseActionTab):
    def __init__(self, parent, effect):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_generalEffect.ui", self)

        self.effect = effect

        self.checkbox_interpolate.setChecked(effect["interpolate"] if "interpolate" in effect else True)
        self.spinbox_offsetX.setValue(effect["offset"][0] if "offset" in effect else 0)
        self.spinbox_offsetY.setValue(effect["offset"][1] if "offset" in effect else 0)
        self.spinbox_scaleX.setValue(effect["scale"][0] if "scale" in effect else 1)
        self.spinbox_scaleY.setValue(effect["scale"][1] if "scale" in effect else 1)

        self.checkbox_interpolate.stateChanged.connect(self.onSetInterpolate)
        self.btn_openFolder.clicked.connect(self.onOpenEffectsFolder)
        self.btn_refresh.clicked.connect(self.onRefreshClicked)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)

        self.refreshList()
        self.combobox_textures.currentTextChanged.connect(self.onChangeTexture)

    def refreshList(self, dirFolder=False):
        if dirFolder:
            characterdata.reloadEffects()

        self.combobox_textures.clear()
        for _fx in characterdata.effects:
            fx = os.path.splitext(_fx)[0]
            self.combobox_textures.addItem(fx)
            if "texture" in self.effect and fx == self.effect["texture"]:
                self.combobox_textures.setCurrentIndex(self.combobox_textures.count()-1)


    @QtCore.pyqtSlot(int)
    def onSetInterpolate(self, value):
        self.effect["interpolate"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(str)
    def onChangeTexture(self, value):
        self.effect["texture"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot()
    def onOpenEffectsFolder(self):
        path = gamepath.getCharacterPath(characterdata.name)
        webbrowser.open("%s/effects" % path)

    @QtCore.pyqtSlot()
    def onRefreshClicked(self):
        self.refreshList(True)

    @QtCore.pyqtSlot(float)
    def onChangeOffsetX(self, value):
        if "offset" not in self.effect: self.effect["offset"] = [0, 0]
        self.effect["offset"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetY(self, value):
        if "offset" not in self.effect: self.effect["offset"] = [0, 0]
        self.effect["offset"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleX(self, value):
        if "scale" not in self.effect: self.effect["scale"] = [1, 1]
        self.effect["scale"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleY(self, value):
        if "scale" not in self.effect: self.effect["scale"] = [1, 1]
        self.effect["scale"][1] = value
        self.valueChanged.emit()


class ActionTab_Companion(BaseActionTab):
    def __init__(self, parent, companionName):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_companion.ui", self)

        self.companionName = companionName
        self.companion = characterdata.companionJson[companionName]

        self.spinbox_offsetX.setValue(self.companion.get("general", {}).get("offset", [0, 0])[0])
        self.spinbox_offsetX.setValue(self.companion.get("general", {}).get("offset", [0, 0])[1])
        self.spinbox_scale.setValue(self.companion.get("general", {}).get("scale", 0.4))

        self.btn_openFolder.clicked.connect(self.onOpenCompanionFolder)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scale.valueChanged.connect(self.onChangeScale)

    @QtCore.pyqtSlot()
    def onOpenCompanionFolder(self):
        path = gamepath.getCharacterPath(characterdata.name)
        webbrowser.open("%s/companions/%s" % (path, self.companionName))

    @QtCore.pyqtSlot(float)
    def onChangeOffsetX(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        if "offset" not in self.companion["general"]: self.companion["general"]["offset"] = [0, 0]
        self.companion["general"]["offset"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetY(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        if "offset" not in self.companion["general"]: self.companion["general"]["offset"] = [0, 0]
        self.companion["general"]["offset"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScale(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["scale"] = value
        self.valueChanged.emit()


class ActionTab_Frame(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_frame.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])
        self.spinbox_w.setValue(actionInfo[2])
        self.spinbox_h.setValue(actionInfo[3])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)
        self.spinbox_w.valueChanged.connect(self.onChangeW)
        self.spinbox_h.valueChanged.connect(self.onChangeH)

    @QtCore.pyqtSlot(int)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeW(self, value):
        self.actionInfo[2] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeH(self, value):
        self.actionInfo[3] = value
        self.valueChanged.emit()


class ActionTab_Delay(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_delay.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_delay.setValue(actionInfo)
        self.spinbox_delay.valueChanged.connect(self.onChange)

    @QtCore.pyqtSlot(float)
    def onChange(self, value):
        self.action["delay"] = value
        self.valueChanged.emit()


class ActionTab_SetAnim(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_setAnim.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        anims = characterdata.jsonFile["anims"]
        for anim in anims:
            self.combobox_animslist.addItem(anim)
            if anim == actionInfo:
                self.combobox_animslist.setCurrentIndex(self.combobox_animslist.count()-1)

        self.combobox_animslist.currentTextChanged.connect(self.onChange)

    @QtCore.pyqtSlot(str)
    def onChange(self, newText):
        self.action["setAnim"] = newText
        self.valueChanged.emit()


class ActionTab_Offset(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_offset.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)

    @QtCore.pyqtSlot(float)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()


class ActionTab_Scale(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_scale.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)

    @QtCore.pyqtSlot(float)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()


class ActionTab_Angle(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_angle.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_angle.setValue(actionInfo)
        self.spinbox_angle.valueChanged.connect(self.onChange)

    @QtCore.pyqtSlot(float)
    def onChange(self, value):
        self.action["angle"] = value
        self.valueChanged.emit()


class ActionTab_Sound(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_sound.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        if type(self.actionInfo) == str:
            self.legacyActionSetup()

        self.refresh()

        self.checkbox_loop.setChecked(self.actionInfo["loop"] if "loop" in self.actionInfo else False)

        self.list_sounds.itemDoubleClicked.connect(self.onItemDoubleClick)
        self.checkbox_loop.stateChanged.connect(self.onSetLoop)
        self.btn_add.clicked.connect(self.onAdd)
        self.btn_remove.clicked.connect(self.onRemove)

    def legacyActionSetup(self):
        # CharLoader v1.2: new SoundAction class
        newAction = {
            "sounds": [self.actionInfo],
            "loop": False
        }

        self.actionInfo = newAction
        self.action["sound"] = self.actionInfo

    def refresh(self):
        self.list_sounds.clear()
        for snd in self.actionInfo["sounds"]:
            self.list_sounds.addItem(snd)


    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onItemDoubleClick(self, item):
        name = item.text()
        if name in characterdata.sounds:
            characterdata.sounds[name].play()

    @QtCore.pyqtSlot(int)
    def onSetLoop(self, value):
        self.actionInfo["loop"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot()
    def onAdd(self):
        actionDialog = ActionDialog_Sound(self)
        if actionDialog.exec():
            snd = actionDialog.comboBox.currentText()
            if snd in self.actionInfo["sounds"]: return
            self.actionInfo["sounds"].append(snd)
            self.valueChanged.emit()
            self.refresh()

    @QtCore.pyqtSlot()
    def onRemove(self):
        item = self.list_sounds.currentItem()
        if not item: return

        snd = item.text()
        if snd not in self.actionInfo["sounds"]: return

        self.actionInfo["sounds"].remove(snd)
        self.valueChanged.emit()
        self.refresh()


class ActionTab_Color(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_color.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.colorView.setColor(QtGui.QColor(actionInfo[0], actionInfo[1], actionInfo[2]))
        self.colorView.changed.connect(self.onChange)
        self.colorView.allowAlpha = True

    @QtCore.pyqtSlot(QtGui.QColor)
    def onChange(self, color):
        self.action["color"] = [color.red(), color.green(), color.blue(), color.alpha()]
        self.valueChanged.emit()


class ActionTab_Hitbox(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_hitbox.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.checkbox_active.setChecked(actionInfo["on"])
        self.spinbox_offsetX.setValue(actionInfo["pos"][0] if "pos" in actionInfo else 0)
        self.spinbox_offsetY.setValue(actionInfo["pos"][1] if "pos" in actionInfo else 0)
        self.spinbox_scaleX.setValue(actionInfo["scale"][0] if "scale" in actionInfo else 0)
        self.spinbox_scaleY.setValue(actionInfo["scale"][1] if "scale" in actionInfo else 0)

        self.checkbox_active.stateChanged.connect(self.onSetActive)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)

    @QtCore.pyqtSlot(int)
    def onSetActive(self, value):
        self.actionInfo["on"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetX(self, value):
        self.actionInfo["pos"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetY(self, value):
        self.actionInfo["pos"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleX(self, value):
        self.actionInfo["scale"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleY(self, value):
        self.actionInfo["scale"][1] = value
        self.valueChanged.emit()


class ActionTab_CustomQueue(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_callCustomQueue.ui", self)

        self.actionInfo = actionInfo
        self.action = action


class ActionDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/actiondialog.ui", self)

        for action in actionTabsDict:
            self.comboBox.addItem(action)


class ActionDialog_Sound(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/actiondialog_sound.ui", self)

        for snd in characterdata.sounds:
            self.comboBox.addItem(snd)

        self.btn_play.clicked.connect(self.onPlay)

    @QtCore.pyqtSlot(bool)
    def onPlay(self, checked):
        i = self.comboBox.currentText()
        characterdata.sounds[i].play()


actionTabsDict = {
	"frame": ActionTab_Frame,
	"delay": ActionTab_Delay,
    "setAnim": ActionTab_SetAnim,
    "offset": ActionTab_Offset,
    "scale": ActionTab_Scale,
    "angle": ActionTab_Angle,
    "sound": ActionTab_Sound,
    "color": ActionTab_Color,
    "hitbox": ActionTab_Hitbox,
    "callCustomQueue": ActionTab_CustomQueue,
}