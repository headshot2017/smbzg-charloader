import copy

from PyQt5 import QtWidgets, QtCore, QtGui, uic


commands = [
    ["up"],
    ["down"],
    ["left"],
    ["right"],
    ["jump"],
    ["guard", "block", "defend"],
    ["attack"],
    ["z"],
    ["fss", "fullstun", "fullstunstrike"],
    ["guardbreaker"],
    ["critical", "crit", "criticalstrike"]
]

class AttackCommandWidget(QtWidgets.QWidget):
    moveUp = QtCore.pyqtSignal(QtWidgets.QWidget)
    moveDown = QtCore.pyqtSignal(QtWidgets.QWidget)
    deleted = QtCore.pyqtSignal(QtWidgets.QWidget)
    commandJson = None

    def __init__(self, parent, commandJson):
        super().__init__(parent)
        uic.loadUi("ui/commandwidget.ui", self)

        if "title" not in commandJson: commandJson["title"] = ""
        if "subtitle" not in commandJson: commandJson["subtitle"] = ""
        if "additionalInfo" not in commandJson: commandJson["additionalInfo"] = ""
        if "imageList" not in commandJson: commandJson["imageList"] = []
        if "featureList" not in commandJson: commandJson["featureList"] = []

        self.lineEdit_title.setText(commandJson["title"])
        self.lineEdit_subtitle.setText(commandJson["subtitle"])
        self.lineEdit_addinfo.setText(commandJson["additionalInfo"])
        self.parseImageList(commandJson["imageList"])
        self.parseFeatureList(commandJson["featureList"])

        self.lineEdit_title.textChanged.connect(self.onEditTitle)
        self.lineEdit_subtitle.textChanged.connect(self.onEditSubtitle)
        self.lineEdit_addinfo.textChanged.connect(self.onEditAddInfo)
        self.btn_moveUp.clicked.connect(self.onMoveUp)
        self.btn_moveDown.clicked.connect(self.onMoveDown)
        self.btn_delete.clicked.connect(self.onDelete)

        menu1 = QtWidgets.QMenu()
        menu2 = QtWidgets.QMenu()
        for cmd in commands:
            action = QtWidgets.QAction(cmd[0], self)
            action.setIcon(QtGui.QIcon("images/%s.png" % cmd[0]))
            menu1.addAction(action)
        for cmd in commands:
            action = QtWidgets.QAction(cmd[0], self)
            action.setIcon(QtGui.QIcon("images/%s.png" % cmd[0]))
            menu2.addAction(action)
        menu1.triggered.connect(self.onAddButton)
        menu2.triggered.connect(self.onAddFeature)
        self.btn_addButton.setMenu(menu1)
        self.btn_addFeature.setMenu(menu2)

        self.commandJson = commandJson

    def createCommandButton(self, parent, image):
        btn = QtWidgets.QPushButton(parent)
        btn.setIcon(QtGui.QIcon("images/%s.png" % image))
        btn.setIconSize(QtCore.QSize(32, 32))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("QPushButton::menu-indicator{width:0px;}")

        menu = QtWidgets.QMenu(btn)
        menu.addAction("Move left")
        menu.addAction("Move right")
        menu.addAction("Delete")
        menu.triggered.connect(self.onCommandButtonAction)
        btn.setMenu(menu)

        return btn

    def addAttackButton(self, name):
        layout = self.scrollWidget_buttons.layout()
        layout.insertWidget(layout.count()-1, self.createCommandButton(self.scrollWidget_buttons, name))
        if self.commandJson: self.commandJson["imageList"].append(name)
    
    def addFeatureButton(self, name):
        layout = self.scrollWidget_features.layout()
        layout.insertWidget(layout.count()-1, self.createCommandButton(self.scrollWidget_features, name))
        if self.commandJson: self.commandJson["featureList"].append(name)

    def parseImageList(self, _list):
        theList = copy.deepcopy(_list)
        for theCommand in theList:
            for altCmds in commands:
                for cmd in altCmds:
                    if theCommand == cmd:
                        self.addAttackButton(altCmds[0])

    def parseFeatureList(self, _list):
        theList = copy.deepcopy(_list)
        for theCommand in theList:
            for altCmds in commands:
                for cmd in altCmds:
                    if theCommand == cmd:
                        self.addFeatureButton(altCmds[0])


    @QtCore.pyqtSlot(str)
    def onEditTitle(self, text):
        self.commandJson["title"] = text

    @QtCore.pyqtSlot(str)
    def onEditSubtitle(self, text):
        self.commandJson["subtitle"] = text

    @QtCore.pyqtSlot(str)
    def onEditAddInfo(self, text):
        self.commandJson["additionalInfo"] = text

    @QtCore.pyqtSlot()
    def onMoveUp(self):
        self.moveUp.emit(self)

    @QtCore.pyqtSlot()
    def onMoveDown(self):
        self.moveDown.emit(self)

    @QtCore.pyqtSlot()
    def onDelete(self):
        self.deleted.emit(self)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onCommandButtonAction(self, thisAction):
        menu = thisAction.parent()
        btn = menu.parent()
        widget = btn.parent()
        layout = widget.layout()

        theList = self.commandJson["imageList"]
        if widget == self.scrollWidget_features:
            theList = self.commandJson["featureList"]

        for action in menu.actions():
            if (action != thisAction): continue

            i = menu.actions().index(thisAction)
            btnInd = layout.indexOf(btn)
            if i == 0 and btnInd != 0: # left
                layout.removeWidget(btn)
                layout.insertWidget(btnInd-1, btn)
                image = theList.pop(btnInd)
                theList.insert(btnInd-1, image)
            if i == 1 and btnInd != layout.count()-2: # right
                layout.removeWidget(btn)
                layout.insertWidget(btnInd+1, btn)
                image = theList.pop(btnInd)
                theList.insert(btnInd+1, image)
            if i == 2: # delete
                btn.deleteLater()
                del theList[btnInd]
            return

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onAddButton(self, action):
        self.addAttackButton(action.text())

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onAddFeature(self, action):
        self.addFeatureButton(action.text())
