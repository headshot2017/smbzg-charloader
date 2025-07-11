from PyQt5 import QtWidgets, QtCore, QtGui, uic

"""
if (image == "guard" || image == "block" || image == "defend") images.Add(CommandImageDisplayEnum.Defend);
if (image == "jump") images.Add(CommandImageDisplayEnum.Jump);
if (image == "z") images.Add(CommandImageDisplayEnum.ZTrigger);
if (image == "critical" || image == "crit" || image == "criticalstrike") images.Add(CommandImageDisplayEnum.CriticalStrike);
if (image == "guardbreaker") images.Add(CommandImageDisplayEnum.GuardBreaker);
if (image == "fss" || image == "fullstun" || image == "fullstunstrike") images.Add(CommandImageDisplayEnum.FullStunStrike);
"""

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

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("commandwidget.ui", self)

        self.btn_moveUp.clicked.connect(self.onMoveUp)
        self.btn_moveDown.clicked.connect(self.onMoveDown)
        self.btn_delete.clicked.connect(self.deleteLater)

        menu1 = QtWidgets.QMenu()
        menu2 = QtWidgets.QMenu()
        for cmd in commands:
            action = QtWidgets.QAction(cmd[0], self)
            action.setIcon(QtGui.QIcon(":/prefix/%s.png" % cmd[0]))
            menu1.addAction(action)
        for cmd in commands:
            action = QtWidgets.QAction(cmd[0], self)
            action.setIcon(QtGui.QIcon(":/prefix/%s.png" % cmd[0]))
            menu2.addAction(action)
        menu1.triggered.connect(self.onAddButton)
        menu2.triggered.connect(self.onAddFeature)
        self.btn_addButton.setMenu(menu1)
        self.btn_addFeature.setMenu(menu2)

    def createCommandButton(self, parent, image):
        btn = QtWidgets.QPushButton(parent)
        btn.setIcon(QtGui.QIcon(":/prefix/%s.png" % image))
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
    
    def addFeatureButton(self, name):
        layout = self.scrollWidget_features.layout()
        layout.insertWidget(layout.count()-1, self.createCommandButton(self.scrollWidget_features, name))

    def parseImageList(self, theList):
        for theCommand in theList:
            for altCmds in commands:
                for cmd in altCmds:
                    if theCommand == cmd:
                        self.addAttackButton(altCmds[0])

    def parseFeatureList(self, theList):
        for theCommand in theList:
            for altCmds in commands:
                for cmd in altCmds:
                    if theCommand == cmd:
                        self.addFeatureButton(altCmds[0])

    @QtCore.pyqtSlot()
    def onMoveUp(self):
        self.moveUp.emit(self)

    @QtCore.pyqtSlot()
    def onMoveDown(self):
        self.moveDown.emit(self)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onCommandButtonAction(self, thisAction):
        menu = thisAction.parent()
        btn = menu.parent()
        widget = btn.parent()
        layout = widget.layout()

        for action in menu.actions():
            if (action != thisAction): continue

            i = menu.actions().index(thisAction)
            btnInd = layout.indexOf(btn)
            if i == 0 and btnInd != 0: # left
                layout.removeWidget(btn)
                layout.insertWidget(btnInd-1, btn)
            if i == 1 and btnInd != layout.count()-2: # right
                layout.removeWidget(btn)
                layout.insertWidget(btnInd+1, btn)
            if i == 2: # delete
                btn.deleteLater()
            return

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onAddButton(self, action):
        self.addAttackButton(action.text())

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def onAddFeature(self, action):
        self.addFeatureButton(action.text())
