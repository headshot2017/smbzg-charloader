from PyQt5 import QtWidgets, QtCore, QtGui, uic

import gamepath
import characterdata


def lerp(a, b, x):
    return a + ((b-a) * x)

def convertPosToUnity(posList):
    return [posList[0]*50, -posList[1]*50]

def convertScaleToUnity(scale):
    return scale/0.4

def convertHitboxPosToUnity(posList):
    return [posList[0]*50, posList[1]*50]

def calculateHitboxCoordinates(pos, scale):
    pos2 = [pos[0] - 0.5*scale[0], pos[1] + 0.5*scale[1]]
    return convertPosToUnity(pos2), convertHitboxPosToUnity(scale)


class PixmapAnimator(QtCore.QAbstractAnimation):
    def __init__(self, graphicsView):
        super().__init__()
        self.graphicsView = graphicsView

        self.pixmapItem = QtWidgets.QGraphicsPixmapItem()
        self.hitboxItem = QtWidgets.QGraphicsRectItem(0, 0, 0, 0)
        self.graphicsView.scene().addItem(self.pixmapItem)
        self.graphicsView.scene().addItem(self.hitboxItem)
        self.hitboxItem.setPos(self.graphicsView.sceneRect().width()/2, self.graphicsView.sceneRect().height()/2)

        self.hitboxItem.setBrush(QtGui.QColor(255, 0, 0, 128))
        self.hitboxItem.setPen(QtGui.QColor(255, 0, 0, 255))

        self.fullPixmap = None
        self.animDict = None

        self.frame = 0
        self.animDuration = 0
        self.currentLoopChanged.connect(self.onLoop)

    def setSprite(self, x, y, w, h):
        if not self.fullPixmap: return
        self.pixmapItem.setPixmap(self.fullPixmap.copy(x, y, w, h))
        self.pixmapItem.setOffset(-w/2, -h/2)

    def reloadCharacter(self):
        path = gamepath.getCharacterPath(characterdata.name)
        self.fullPixmap = QtGui.QPixmap("%s/sheet.png" % path)
        self.setSprite(0,0,0,0)
        self.hitboxItem.setRect(0, 0, 0, 0)

    def setAnimation(self, anim):
        self.stop()

        self.animDict = anim
        self.frame = 0
        self.animDuration = 0
        if not anim: return

        loops = anim["loops"] if "loops" in anim else -1
        self.setLoopCount(-1 if loops == -1 else loops+1)

        for frame in self.animDict["frames"]:
            if "delay" in frame:
                self.animDuration += frame["delay"]*1000

        self.onFrameChange(False)

    def setFrame(self, ind):
        self.frame = ind
        self.onFrameChange()

    def refresh(self):
        if not self.animDict: return

        self.onFrameChange(False)
        self.animDuration = 0
        for frame in self.animDict["frames"]:
            if "delay" in frame:
                self.animDuration += frame["delay"]*1000


    def onFrameChange(self, playSound=True):
        if not self.animDict or self.frame < 0 or self.frame >= len(self.animDict["frames"]):
            return False

        globalOffset = convertPosToUnity(self.animDict["offset"] if "offset" in self.animDict else [0, 0])
        globalCharOffset = convertPosToUnity(characterdata.jsonFile["general"]["offset"]["ingame"])
        globalOffset[0] += globalCharOffset[0]
        globalOffset[1] += globalCharOffset[1]

        globalScale = self.animDict["scale"] if "scale" in self.animDict else [1, 1]
        globalCharScale = convertScaleToUnity(characterdata.jsonFile["general"]["scale"]["ingame"])
        globalScale = [globalScale[0] * globalCharScale, globalScale[1] * globalCharScale]

        frame = self.animDict["frames"][self.frame]

        offsetPos = convertPosToUnity(frame["offset"] if "offset" in frame else [0, 0])
        offsetPos[0] += globalOffset[0]
        offsetPos[1] += globalOffset[1]

        self.pixmapItem.resetTransform()
        self.pixmapItem.setPos(self.graphicsView.sceneRect().width()/2, self.graphicsView.sceneRect().height()/2)
        self.pixmapItem.setRotation(frame["angle"] if "angle" in frame else 0)
        self.pixmapItem.moveBy(*offsetPos)
        self.pixmapItem.setTransform(self.pixmapItem.transform().scale(
            globalScale[0] * (frame["scale"][0] if "scale" in frame else 1),
            globalScale[1] * (frame["scale"][1] if "scale" in frame else 1)
        ))

        if playSound and "sound" in frame and frame["sound"] in characterdata.sounds:
            characterdata.sounds[frame["sound"]].play()

        spriteFrame = frame
        spriteFrameInd = self.frame
        while "frame" not in spriteFrame and spriteFrameInd > 0:
            spriteFrameInd -= 1
            spriteFrame = self.animDict["frames"][spriteFrameInd]
        if "frame" in spriteFrame:
            self.setSprite(*spriteFrame["frame"])

        hitboxFrame = frame
        hitboxFrameInd = self.frame
        while "hitbox" not in hitboxFrame and hitboxFrameInd > 0:
            hitboxFrameInd -= 1
            hitboxFrame = self.animDict["frames"][hitboxFrameInd]
        if "hitbox" in hitboxFrame:
            hitbox = hitboxFrame["hitbox"]
            on = hitbox["on"]
            pos, scale = calculateHitboxCoordinates(
                hitbox["pos"] if "pos" in hitbox else [0, 0],
                hitbox["scale"] if "scale" in hitbox else [0, 0],
            )

            self.hitboxItem.setRect(pos[0], pos[1], scale[0], scale[1])
            self.hitboxItem.setBrush(QtGui.QColor(255, 0, 0, 0 if not on else 128))
            self.hitboxItem.setVisible(True)
        else:
            self.hitboxItem.setVisible(False)

        return True

    def interpolateFrames(self, x):
        globalOffset = self.animDict["offset"] if "offset" in self.animDict else [0, 0]
        globalCharOffset = characterdata.jsonFile["general"]["offset"]["ingame"]
        globalOffset = [globalOffset[0] + globalCharOffset[0], globalOffset[1] + globalCharOffset[1]]

        globalScale = self.animDict["scale"] if "scale" in self.animDict else [1, 1]
        globalCharScale = convertScaleToUnity(characterdata.jsonFile["general"]["scale"]["ingame"])
        globalScale = [globalScale[0] * globalCharScale, globalScale[1] * globalCharScale]

        currAction = self.animDict["frames"][self.frame]
        if currAction["delay"] <= 0: return

        nextAction = None
        if self.frame >= len(self.animDict["frames"])-1:
            nextAction = self.animDict["frames"][0] if self.loopCount() < 0 or self.currentLoop() < self.loopCount()-1 else currAction
        else:
            nextAction = self.animDict["frames"][self.frame+1]

        if "hitbox" in currAction and "hitbox" in nextAction:
            on = currAction["hitbox"]["on"]

            nextHitbox = nextAction["hitbox"]
            hitboxOff = (
                not nextHitbox["on"] and
                ("pos" not in nextHitbox or nextHitbox["pos"] == [0,0]) and
                ("scale" not in nextHitbox or nextHitbox["scale"] == [0,0])
            )
            if hitboxOff:
                nextHitbox = currAction["hitbox"]

            posLerp = [
                lerp(
                    currAction["hitbox"]["pos"][0] if "pos" in currAction["hitbox"] else 0,
                    nextHitbox["pos"][0] if "pos" in nextHitbox else 0,
                    x
                ),
                lerp(
                    currAction["hitbox"]["pos"][1] if "pos" in currAction["hitbox"] else 0,
                    nextHitbox["pos"][1] if "pos" in nextHitbox else 0,
                    x
                )
            ]
            scaleLerp = [
                lerp(
                    currAction["hitbox"]["scale"][0] if "scale" in currAction["hitbox"] else 0,
                    nextHitbox["scale"][0] if "scale" in nextHitbox else 0,
                    x
                ),
                lerp(
                    currAction["hitbox"]["scale"][1] if "scale" in currAction["hitbox"] else 0,
                    nextHitbox["scale"][1] if "scale" in nextHitbox else 0,
                    x
                )
            ]
            posLerp, scaleLerp = calculateHitboxCoordinates(posLerp, scaleLerp)

            self.hitboxItem.setRect(posLerp[0], posLerp[1], scaleLerp[0], scaleLerp[1])
            self.hitboxItem.setBrush(QtGui.QColor(255, 0, 0, 0 if not on else 128))


        angleLerp = lerp(
            currAction["angle"] if "angle" in currAction else 0,
            nextAction["angle"] if "angle" in nextAction else 0,
            x
        )

        scaleLerp = [
            globalScale[0] * lerp(
                currAction["scale"][0] if "scale" in currAction else 1,
                nextAction["scale"][0] if "scale" in nextAction else 1,
                x
            ),
            globalScale[1] * lerp(
                currAction["scale"][1] if "scale" in currAction else 1,
                nextAction["scale"][1] if "scale" in nextAction else 1,
                x
            )
        ]

        offsetLerp = convertPosToUnity([
            globalOffset[0] + lerp(
                currAction["offset"][0] if "offset" in currAction else 0,
                nextAction["offset"][0] if "offset" in nextAction else 0,
                x
            ),
            globalOffset[1] + lerp(
                currAction["offset"][1] if "offset" in currAction else 0,
                nextAction["offset"][1] if "offset" in nextAction else 0,
                x
            )
        ])

        self.pixmapItem.resetTransform()
        self.pixmapItem.setPos(self.graphicsView.sceneRect().width()/2, self.graphicsView.sceneRect().height()/2)
        self.pixmapItem.setRotation(angleLerp)
        self.pixmapItem.moveBy(*offsetLerp)
        self.pixmapItem.setTransform(self.pixmapItem.transform().scale(*scaleLerp))

    def getTimeFrames(self):
        timeToNextFrame = 0
        timeFromLastFrame = 0
        for i in range(self.frame+1):
            if i >= len(self.animDict["frames"]): break
            frame = self.animDict["frames"][i]
            if "delay" in frame:
                timeToNextFrame += frame["delay"]*1000
                if i != self.frame: timeFromLastFrame += frame["delay"]*1000
        return timeToNextFrame, timeFromLastFrame

    def duration(self):
        return self.animDuration

    def updateCurrentTime(self, currentTime):
        timeToNextFrame, timeFromLastFrame = self.getTimeFrames()

        if "interpolate" not in self.animDict or self.animDict["interpolate"]:
            a = currentTime - timeFromLastFrame
            b = timeToNextFrame - timeFromLastFrame
            self.interpolateFrames(a/b)

        while currentTime >= timeToNextFrame:
            self.frame += 1
            if not self.onFrameChange(): return
            timeToNextFrame, timeFromLastFrame = self.getTimeFrames()

    def onLoop(self):
        self.frame = 0
        self.onFrameChange()


class AnimatorGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.theScene = QtWidgets.QGraphicsScene()
        self.setScene(self.theScene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(224, 224, 224)))

        self.setSceneRect(QtCore.QRectF(self.viewport().rect()))

        self.backgroundItem = QtWidgets.QGraphicsPixmapItem()
        self.theScene.addItem(self.backgroundItem)

        self.animator = PixmapAnimator(self)

    def reloadCharacter(self):
        self.animator.reloadCharacter()

    def setBackground(self, pixmap):
        if not pixmap:
            self.backgroundItem.setVisible(False)
            return

        self.backgroundItem.setVisible(True)
        self.backgroundItem.setPixmap(pixmap)
        self.backgroundItem.setPos(-pixmap.width()/2, -pixmap.height()/2)
