import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import characterdata
import game


class BaseActionTab(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

    def __init__(self, parent, jsonEditorRoot):
        super().__init__(parent)

        self.jsonEditorRoot = jsonEditorRoot

    def setupForCharacter(self, jsonRoot):
        pass


class ActionTab_General(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, anim):
        super().__init__(parent, jsonEditorRoot)
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

        self.refreshLength()

    def refreshLength(self):
        loops = self.anim["loops"] if "loops" in self.anim else -1
        if "frames" in self.anim:
            length = 0
            for f in self.anim["frames"]:
                length += f["delay"] if "delay" in f else 0
            lengthLoops = length * (loops+1)

            finalStr = "Animation length: %.3fs" % length
            if lengthLoops <= 0:
                finalStr += "\nTotal length: Infinity"
            else:
                finalStr += "\nTotal length: %.3fs" % lengthLoops

            self.lbl_length.setText(finalStr)

    @QtCore.pyqtSlot(int)
    def onSetInterpolate(self, value):
        self.anim["interpolate"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeLoops(self, value):
        self.anim["loops"] = value
        self.refreshLength()
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
    def __init__(self, parent, jsonEditorRoot, effect):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_generalEffect.ui", self)

        self.effect = effect

        self.checkbox_interpolate.setChecked(effect["interpolate"] if "interpolate" in effect else True)
        self.spinbox_loops.setValue(effect["loops"] if "loops" in effect else 0)
        self.combobox_filter.setCurrentIndex(effect["filter"] if "filter" in effect else 1)
        self.spinbox_offsetX.setValue(effect["offset"][0] if "offset" in effect else 0)
        self.spinbox_offsetY.setValue(effect["offset"][1] if "offset" in effect else 0)
        self.spinbox_scaleX.setValue(effect["scale"][0] if "scale" in effect else 1)
        self.spinbox_scaleY.setValue(effect["scale"][1] if "scale" in effect else 1)
        self.spinbox_defaultW.setValue(jsonEditorRoot["defaultFrameSize"][0] if "defaultFrameSize" in jsonEditorRoot else 0)
        self.spinbox_defaultH.setValue(jsonEditorRoot["defaultFrameSize"][1] if "defaultFrameSize" in jsonEditorRoot else 0)
        self.spinbox_spacingX.setValue(jsonEditorRoot["spriteSpacing"][0] if "spriteSpacing" in jsonEditorRoot else 0)
        self.spinbox_spacingY.setValue(jsonEditorRoot["spriteSpacing"][1] if "spriteSpacing" in jsonEditorRoot else 0)

        self.checkbox_interpolate.stateChanged.connect(self.onSetInterpolate)
        self.spinbox_loops.valueChanged.connect(self.onChangeLoops)
        self.btn_openFolder.clicked.connect(self.onOpenEffectsFolder)
        self.btn_refresh.clicked.connect(self.onRefreshClicked)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)
        self.spinbox_defaultW.valueChanged.connect(self.onDefaultWChanged)
        self.spinbox_defaultH.valueChanged.connect(self.onDefaultHChanged)

        self.refreshList()
        self.combobox_textures.currentTextChanged.connect(self.onChangeTexture)
        self.combobox_filter.currentIndexChanged.connect(self.onChangeFilter)

        self.refreshLength()

    def refreshLength(self):
        loops = self.effect["loops"] if "loops" in self.effect else 0
        if "frames" in self.effect:
            length = 0
            for f in self.effect["frames"]:
                length += f["delay"] if "delay" in f else 0
            lengthLoops = length * (loops+1)

            finalStr = "Animation length: %.3fs" % length
            if lengthLoops <= 0:
                finalStr += "\nTotal length: Infinity"
            else:
                finalStr += "\nTotal length: %.3fs" % lengthLoops

            self.lbl_length.setText(finalStr)

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

    @QtCore.pyqtSlot(int)
    def onChangeLoops(self, value):
        self.effect["loops"] = value
        self.refreshLength()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(str)
    def onChangeTexture(self, value):
        self.effect["texture"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeFilter(self, value):
        self.effect["filter"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot()
    def onOpenEffectsFolder(self):
        path = game.getCharacterPath(characterdata.name)
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

    @QtCore.pyqtSlot(int)
    def onDefaultWChanged(self, value):
        self.jsonEditorRoot["defaultFrameSize"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onDefaultHChanged(self, value):
        self.jsonEditorRoot["defaultFrameSize"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onSpacingXChanged(self, value):
        self.jsonEditorRoot["spriteSpacing"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onSpacingYChanged(self, value):
        self.jsonEditorRoot["spriteSpacing"][1] = value
        self.valueChanged.emit()


class ActionTab_Companion(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, companionName):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_companion.ui", self)

        self.companionName = companionName
        self.companion = characterdata.companionJson[companionName]
        path = game.getCharacterPath(characterdata.name)

        self.lbl_portrait.setImages("%s/companions/%s/portrait.png" % (path, self.companionName), "images/default_portrait_unbalanced.png")
        self.lbl_battlePortrait.setImages("%s/companions/%s/battleportrait.png" % (path, self.companionName), "images/default_portrait_unbalanced.png")
        for platform in game.assembly.GetType("BattleCache").GetMember("PlatformEnum")[0].GetEnumNames():
            self.combobox_platform.addItem(platform)


        # JSON values

        # General tab
        self.combobox_sheetFilter.setCurrentIndex(self.companion.get("general", {}).get("sheetFilter", 0))
        self.spinbox_offsetX.setValue(self.companion.get("general", {}).get("offset", [0, 0])[0])
        self.spinbox_offsetY.setValue(self.companion.get("general", {}).get("offset", [0, 0])[1])
        self.spinbox_scale.setValue(self.companion.get("general", {}).get("scale", 0.4))
        self.spinbox_defaultW.setValue(jsonEditorRoot["defaultFrameSize"][0] if "defaultFrameSize" in jsonEditorRoot else 0)
        self.spinbox_defaultH.setValue(jsonEditorRoot["defaultFrameSize"][1] if "defaultFrameSize" in jsonEditorRoot else 0)
        self.spinbox_spacingX.setValue(jsonEditorRoot["spriteSpacing"][0] if "spriteSpacing" in jsonEditorRoot else 0)
        self.spinbox_spacingY.setValue(jsonEditorRoot["spriteSpacing"][1] if "spriteSpacing" in jsonEditorRoot else 0)

        # Transformation tab
        self.checkbox_isForm.setChecked(self.companion.get("general", {}).get("isForm", False))
        self.lineEdit_displayName.setText(self.companion.get("general", {}).get("displayName", ""))
        self.combobox_platform.setCurrentIndex(self.companion.get("general", {}).get("platform", 0))
        self.combobox_battlePortraitFilter.setCurrentIndex(self.companion.get("general", {}).get("battlePortraitFilter", 0))
        self.combobox_platformFilter.setCurrentIndex(self.companion.get("general", {}).get("platformFilter", 0))

        # Qt signals

        # General tab
        self.btn_openFolder.clicked.connect(self.onOpenCompanionFolder)
        self.combobox_sheetFilter.currentIndexChanged.connect(self.onSheetFilterChanged)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scale.valueChanged.connect(self.onChangeScale)
        self.spinbox_defaultW.valueChanged.connect(self.onDefaultWChanged)
        self.spinbox_defaultH.valueChanged.connect(self.onDefaultHChanged)
        self.spinbox_spacingX.valueChanged.connect(self.onSpacingXChanged)
        self.spinbox_spacingY.valueChanged.connect(self.onSpacingYChanged)

        # Transformation tab
        self.checkbox_isForm.stateChanged.connect(self.onChangeIsForm)
        self.lineEdit_displayName.textChanged.connect(self.onDisplayNameChanged)
        self.combobox_platform.currentIndexChanged.connect(self.onPlatformChanged)
        self.combobox_battlePortraitFilter.currentIndexChanged.connect(self.onBattlePortraitFilterChanged)
        self.combobox_platformFilter.currentIndexChanged.connect(self.onPlatformFilterChanged)

    @QtCore.pyqtSlot()
    def onOpenCompanionFolder(self):
        path = game.getCharacterPath(characterdata.name)
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

    @QtCore.pyqtSlot(int)
    def onSheetFilterChanged(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["sheetFilter"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onDefaultWChanged(self, value):
        self.jsonEditorRoot["defaultFrameSize"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onDefaultHChanged(self, value):
        self.jsonEditorRoot["defaultFrameSize"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onSpacingXChanged(self, value):
        self.jsonEditorRoot["spriteSpacing"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onSpacingYChanged(self, value):
        self.jsonEditorRoot["spriteSpacing"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeIsForm(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["isForm"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(str)
    def onDisplayNameChanged(self, text):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["displayName"] = text
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onPlatformChanged(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["platform"] = value

    @QtCore.pyqtSlot(int)
    def onBattlePortraitFilterChanged(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["battlePortraitFilter"] = value

    @QtCore.pyqtSlot(int)
    def onPlatformFilterChanged(self, value):
        if "general" not in self.companion: self.companion["general"] = {}
        self.companion["general"]["platformFilter"] = value


class ActionTab_Frame(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)

        self.frameSizesAreSet = jsonEditorRoot["defaultFrameSize"][0] and jsonEditorRoot["defaultFrameSize"][1]
        if self.frameSizesAreSet:
            uic.loadUi("ui/actiontab_frameAlt.ui", self)
            if actionInfo[2] == 0: actionInfo[2] = jsonEditorRoot["defaultFrameSize"][0]
            if actionInfo[3] == 0: actionInfo[3] = jsonEditorRoot["defaultFrameSize"][1]
        else:
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
        self.btn_loadPreset.clicked.connect(self.onLoadPreset)
        self.btn_savePreset.clicked.connect(self.onSavePreset)
        self.btn_deletePreset.clicked.connect(self.onDeletePreset)

        self.checkSizeBounds()
        self.reloadPresets()

        if self.frameSizesAreSet:
            differentValues = actionInfo[2] != jsonEditorRoot["defaultFrameSize"][0] or actionInfo[3] != jsonEditorRoot["defaultFrameSize"][1]
            self.checkbox_changeSize.setChecked(differentValues)
            self.checkbox_changeSize.stateChanged.connect(self.onCheckboxChangeSize)
            self.changeBehavior(not differentValues)

    def checkSizeBounds(self):
        w = self.jsonEditorRoot["imgW"] if self.actionInfo[2] == -1 else self.actionInfo[2]
        h = self.jsonEditorRoot["imgH"] if self.actionInfo[3] == -1 else self.actionInfo[3]
        self.lbl_warning.setVisible(
            self.actionInfo[0] + w > self.jsonEditorRoot["imgW"] or
            self.actionInfo[1] + h > self.jsonEditorRoot["imgH"]
        )

    def reloadPresets(self):
        self.combobox_presets.clear()
        if "framePresets" not in self.jsonEditorRoot:
            self.jsonEditorRoot["framePresets"] = {}

        for preset in self.jsonEditorRoot["framePresets"]:
            self.combobox_presets.addItem(preset)

    def changeBehavior(self, sizesLocked):
        singleSteps = [
            self.jsonEditorRoot["defaultFrameSize"][0]+self.jsonEditorRoot["spriteSpacing"][0] if sizesLocked else 1,
            self.jsonEditorRoot["defaultFrameSize"][1]+self.jsonEditorRoot["spriteSpacing"][1] if sizesLocked else 1
        ]
        self.spinbox_x.setSingleStep(singleSteps[0])
        self.spinbox_y.setSingleStep(singleSteps[1])
        self.spinbox_w.setEnabled(not sizesLocked)
        self.spinbox_h.setEnabled(not sizesLocked)
        if sizesLocked:
            newX = self.actionInfo[0] // singleSteps[0] * singleSteps[0]
            newY = self.actionInfo[1] // singleSteps[1] * singleSteps[1]
            self.spinbox_w.setValue(self.jsonEditorRoot["defaultFrameSize"][0])
            self.spinbox_h.setValue(self.jsonEditorRoot["defaultFrameSize"][1])
            self.spinbox_x.setValue(newX)
            self.spinbox_y.setValue(newY)

    @QtCore.pyqtSlot(int)
    def onChangeX(self, value):
        if self.frameSizesAreSet and not self.checkbox_changeSize.isChecked():
            singleStep = self.jsonEditorRoot["defaultFrameSize"][0]+self.jsonEditorRoot["spriteSpacing"][0]
            value = value // singleStep * singleStep
            self.spinbox_x.blockSignals(True)
            self.spinbox_x.setValue(value)
            self.spinbox_x.blockSignals(False)
        self.actionInfo[0] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeY(self, value):
        if self.frameSizesAreSet and not self.checkbox_changeSize.isChecked():
            singleStep = self.jsonEditorRoot["defaultFrameSize"][1]+self.jsonEditorRoot["spriteSpacing"][1]
            value = value // singleStep * singleStep
            self.spinbox_y.blockSignals(True)
            self.spinbox_y.setValue(value)
            self.spinbox_y.blockSignals(False)
        self.actionInfo[1] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeW(self, value):
        self.actionInfo[2] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeH(self, value):
        self.actionInfo[3] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onCheckboxChangeSize(self, value):
        on = value > 0
        self.changeBehavior(not on)

    @QtCore.pyqtSlot()
    def onLoadPreset(self):
        if not self.combobox_presets.count() or\
           self.combobox_presets.currentText() not in self.jsonEditorRoot["framePresets"]:
            return

        preset = self.combobox_presets.currentText()
        self.spinbox_x.setValue(self.jsonEditorRoot["framePresets"][preset][0])
        self.spinbox_y.setValue(self.jsonEditorRoot["framePresets"][preset][1])
        self.spinbox_w.setValue(self.jsonEditorRoot["framePresets"][preset][2])
        self.spinbox_h.setValue(self.jsonEditorRoot["framePresets"][preset][3])

    @QtCore.pyqtSlot()
    def onSavePreset(self):
        current = self.combobox_presets.currentText() if self.combobox_presets.count() else ""

        name, ok = QtWidgets.QInputDialog.getText(self, "Save preset", "Enter a name for this coordinate preset", QtWidgets.QLineEdit.Normal, current)
        if not ok or not name: return

        self.jsonEditorRoot["framePresets"][name] = [
            self.spinbox_x.value(),
            self.spinbox_y.value(),
            self.spinbox_w.value(),
            self.spinbox_h.value()
        ]

        self.reloadPresets()

    @QtCore.pyqtSlot()
    def onDeletePreset(self):
        if not self.combobox_presets.count() or\
           self.combobox_presets.currentText() not in self.jsonEditorRoot["framePresets"]:
            return

        preset = self.combobox_presets.currentText()
        del self.jsonEditorRoot["framePresets"][preset]

        self.reloadPresets()


class ActionTab_Delay(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_setAnim.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.combobox_animslist.currentTextChanged.connect(self.onChange)

    def setupForCharacter(self, jsonRoot):
        for anim in jsonRoot["anims"]:
            self.combobox_animslist.addItem(anim)
            if anim == self.actionInfo:
                self.combobox_animslist.setCurrentIndex(self.combobox_animslist.count()-1)

    @QtCore.pyqtSlot(str)
    def onChange(self, newText):
        self.action["setAnim"] = newText
        self.valueChanged.emit()


class ActionTab_Offset(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_sound.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        if type(self.actionInfo) == str:
            self.legacyActionSetup()

        self.refresh()

        self.checkbox_loop.setChecked(self.actionInfo["loop"] if "loop" in self.actionInfo else False)
        self.checkbox_pause.setChecked(self.actionInfo["pauseWithGame"] if "pauseWithGame" in self.actionInfo else False)
        self.slider_volume.setValue(self.actionInfo["volume"] if "volume" in self.actionInfo else 100)
        self.slider_pitch.setValue(self.actionInfo["pitch"] if "pitch" in self.actionInfo else 100)
        self.lbl_volume.setText("%d%%" % (self.slider_volume.value()))
        self.lbl_pitch.setText("%d%%" % (self.slider_pitch.value()))

        self.list_sounds.itemDoubleClicked.connect(self.onItemDoubleClick)
        self.checkbox_loop.stateChanged.connect(self.onSetLoop)
        self.checkbox_pause.stateChanged.connect(self.onSetPause)
        self.slider_volume.valueChanged.connect(self.onVolumeChanged)
        self.slider_pitch.valueChanged.connect(self.onPitchChanged)
        self.btn_add.clicked.connect(self.onAdd)
        self.btn_remove.clicked.connect(self.onRemove)

    def legacyActionSetup(self):
        # CharLoader v1.2: new SoundAction class
        newAction = characterdata.defaultAction("sound")
        newAction["sounds"] = [self.actionInfo]

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

    @QtCore.pyqtSlot(int)
    def onSetPause(self, value):
        self.actionInfo["pauseWithGame"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onVolumeChanged(self, value):
        self.lbl_volume.setText("%d%%" % value)
        self.actionInfo["volume"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onPitchChanged(self, value):
        self.lbl_pitch.setText("%d%%" % value)
        self.actionInfo["pitch"] = value
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
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
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_hitbox.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.checkbox_active.setChecked(actionInfo["on"])
        self.spinbox_offsetX.setValue(actionInfo["pos"][0] if "pos" in actionInfo else 0)
        self.spinbox_offsetY.setValue(actionInfo["pos"][1] if "pos" in actionInfo else 0)
        self.spinbox_scaleX.setValue(actionInfo["scale"][0] if "scale" in actionInfo else 0)
        self.spinbox_scaleY.setValue(actionInfo["scale"][1] if "scale" in actionInfo else 0)
        self.spinbox_angle.setValue(actionInfo["angle"] if "angle" in actionInfo else 0)

        self.checkbox_active.stateChanged.connect(self.onSetActive)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)
        self.spinbox_angle.valueChanged.connect(self.onChangeAngle)

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

    @QtCore.pyqtSlot(float)
    def onChangeAngle(self, value):
        self.actionInfo["angle"] = value
        self.valueChanged.emit()


class ActionTab_CustomQueue(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_callCustomQueue.ui", self)

        self.actionInfo = actionInfo
        self.action = action


class ActionTab_Puppets(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_puppets.ui", self)

        self.actionInfo = actionInfo
        self.action = action
        self.puppetsDict = {}

        self.currentPuppetInd = -1

        self.list_puppets.itemClicked.connect(self.onItemClick)
        self.btn_add.clicked.connect(self.onAdd)
        self.btn_remove.clicked.connect(self.onRemove)
        self.checkbox_visible.stateChanged.connect(self.onSetVisible)
        self.spinbox_layer.valueChanged.connect(self.onChangeLayer)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)
        self.spinbox_angle.valueChanged.connect(self.onChangeAngle)

    def setupForCharacter(self, jsonRoot):
        self.puppetsDict = jsonRoot["puppets"]
        self.reloadList()

    def reloadList(self):
        self.list_puppets.clear()
        self.currentPuppetInd = -1

        for k in self.puppetsDict:
            i = self.getIndexOfPuppet(k)
            if str(i) in self.actionInfo:
                self.list_puppets.addItem(k)

    def setupTab(self):
        if self.currentPuppetInd < 0: return
        actionInfo = self.actionInfo[str(self.currentPuppetInd)]

        self.checkbox_visible.setChecked(actionInfo["on"])
        self.spinbox_layer.setValue(actionInfo["layer"] if "layer" in actionInfo else 0)
        self.spinbox_offsetX.setValue(actionInfo["offset"][0] if "offset" in actionInfo else 0)
        self.spinbox_offsetY.setValue(actionInfo["offset"][1] if "offset" in actionInfo else 0)
        self.spinbox_scaleX.setValue(actionInfo["scale"][0] if "scale" in actionInfo else 0)
        self.spinbox_scaleY.setValue(actionInfo["scale"][1] if "scale" in actionInfo else 0)
        self.spinbox_angle.setValue(actionInfo["angle"] if "angle" in actionInfo else 0)

    def getIndexOfPuppet(self, name):
        i = 0
        for k in self.puppetsDict:
            if k == name:
                return i
                break
            i += 1
        return -1

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onItemClick(self, item):
        self.currentPuppetInd = self.getIndexOfPuppet(item.text())
        self.setupTab()

    @QtCore.pyqtSlot(bool)
    def onAdd(self, checked):
        actionDialog = ActionDialog_Puppet(self, self.puppetsDict)
        if actionDialog.exec():
            puppetInd = actionDialog.comboBox.currentIndex()
            if str(puppetInd) in self.actionInfo: return

            self.actionInfo[str(puppetInd)] = characterdata.defaultPuppetAction()
            self.valueChanged.emit()
            self.reloadList()

    @QtCore.pyqtSlot(bool)
    def onRemove(self, checked):
        item = self.list_puppets.currentItem()
        if not item: return

        ind = self.getIndexOfPuppet(item.text())
        if ind < 0: return

        del self.actionInfo[str(ind)]
        self.valueChanged.emit()
        self.reloadList()

    @QtCore.pyqtSlot(int)
    def onSetVisible(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["on"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeLayer(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["layer"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetX(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["offset"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeOffsetY(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["offset"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleX(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["scale"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleY(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["scale"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeAngle(self, value):
        if self.currentPuppetInd < 0: return
        self.actionInfo[str(self.currentPuppetInd)]["angle"] = value
        self.valueChanged.emit()


class ActionTab_Interpolation(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_interpolation.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.combobox_interp.setCurrentIndex(actionInfo)
        self.combobox_interp.currentIndexChanged.connect(self.onChangeInterpolation)

    @QtCore.pyqtSlot(int)
    def onChangeInterpolation(self, value):
        self.action["interpolation"] = value
        self.valueChanged.emit()


class ActionTab_ReinitHitbox(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_reinitHitbox.ui", self)

        self.actionInfo = actionInfo
        self.action = action


class ActionTab_ComboLink(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_comboLink.ui", self)

        self.actionInfo = actionInfo
        self.action = action


class ActionTab_QueueCinematics(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_queueCinematics.ui", self)

        self.actionInfo = actionInfo
        self.action = action


class ActionTab_VelocityX(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_velocity.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.lbl_velocity.setText("X velocity")
        self.checkbox_relative.setChecked(actionInfo["relative"])
        self.spinbox_velocity.setValue(actionInfo["velocity"])

        self.checkbox_relative.stateChanged.connect(self.onRelativeChanged)
        self.spinbox_velocity.valueChanged.connect(self.onChangeVelocity)

    @QtCore.pyqtSlot(int)
    def onRelativeChanged(self, value):
        self.actionInfo["relative"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeVelocity(self, value):
        self.actionInfo["velocity"] = value
        self.valueChanged.emit()


class ActionTab_VelocityY(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_velocity.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.lbl_velocity.setText("Y velocity")
        self.checkbox_relative.setChecked(actionInfo["relative"])
        self.spinbox_velocity.setValue(actionInfo["velocity"])

        self.checkbox_relative.stateChanged.connect(self.onRelativeChanged)
        self.spinbox_velocity.valueChanged.connect(self.onChangeVelocity)

    @QtCore.pyqtSlot(int)
    def onRelativeChanged(self, value):
        self.actionInfo["relative"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeVelocity(self, value):
        self.actionInfo["velocity"] = value
        self.valueChanged.emit()


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


class ActionDialog_Puppet(QtWidgets.QDialog):
    def __init__(self, parent, puppetsDict):
        super().__init__(parent)
        uic.loadUi("ui/actiondialog_puppet.ui", self)

        for puppet in puppetsDict:
            self.comboBox.addItem(puppet)


class PuppetTab(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/puppettab.ui", self)

        self.actionInfo = actionInfo

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])
        self.spinbox_w.setValue(actionInfo[2])
        self.spinbox_h.setValue(actionInfo[3])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)
        self.spinbox_w.valueChanged.connect(self.onChangeW)
        self.spinbox_h.valueChanged.connect(self.onChangeH)

        self.checkSizeBounds()

    def checkSizeBounds(self):
        w = self.jsonEditorRoot["imgW"] if self.actionInfo[2] == -1 else self.actionInfo[2]
        h = self.jsonEditorRoot["imgH"] if self.actionInfo[3] == -1 else self.actionInfo[3]
        self.lbl_warning.setVisible(
            self.actionInfo[0] + w > self.jsonEditorRoot["imgW"] or
            self.actionInfo[1] + h > self.jsonEditorRoot["imgH"]
        )

    @QtCore.pyqtSlot(int)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeW(self, value):
        self.actionInfo[2] = value
        self.checkSizeBounds()
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeH(self, value):
        self.actionInfo[3] = value
        self.checkSizeBounds()
        self.valueChanged.emit()


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
    "puppets": ActionTab_Puppets,
    "interpolation": ActionTab_Interpolation,
    "reinitHitbox": ActionTab_ReinitHitbox,
    "comboLink": ActionTab_ComboLink,
    "queueCinematics": ActionTab_QueueCinematics,
    "velocityX": ActionTab_VelocityX,
    "velocityY": ActionTab_VelocityY
}