from PyQt5 import QtWidgets, QtCore, QtGui, uic

import characterdata

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

        for snd in characterdata.sounds:
            self.combobox_soundlist.addItem(snd)
            if snd == actionInfo:
                self.combobox_soundlist.setCurrentIndex(self.combobox_soundlist.count()-1)

        self.combobox_soundlist.currentTextChanged.connect(self.onChange)
        self.btn_play.clicked.connect(self.onPlay)

    @QtCore.pyqtSlot(str)
    def onChange(self, newText):
        self.action["sound"] = newText
        self.valueChanged.emit()

    @QtCore.pyqtSlot(bool)
    def onPlay(self, checked):
        i = self.combobox_soundlist.currentText()
        characterdata.sounds[i].play()


class ActionTab_Color(BaseActionTab):
    def __init__(self, parent, actionInfo, action):
        super().__init__(parent)
        uic.loadUi("ui/actiontab_color.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.colorView.setColor(QtGui.QColor(actionInfo[0], actionInfo[1], actionInfo[2]))
        self.colorView.changed.connect(self.onChange)

    @QtCore.pyqtSlot(QtGui.QColor)
    def onChange(self, color):
        self.action["color"] = [color.red(), color.green(), color.blue()]
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


class ActionDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/actiondialog.ui", self)

        for action in actionTabsDict:
            self.comboBox.addItem(action)
