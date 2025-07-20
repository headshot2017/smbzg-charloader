import os

from PyQt5 import QtWidgets


smbzgPath = ""
customCharsPath = ""


def init():
    global smbzgPath, customCharsPath

    if os.path.exists("smbzg-path.txt"):
        smbzgPath = open("smbzg-path.txt").read()

    if not smbzgPath or not os.path.exists(smbzgPath):
        smbzgPath = askGamePath()

        if not smbzgPath:
            return False

        open("smbzg-path.txt", "w").write(smbzgPath)

    customCharsPath = "%s/SMBZ-G_Data/StreamingAssets/CustomChars" % smbzgPath
    return True

def getCharacterPath(name):
    return "%s/SMBZ-G_Data/StreamingAssets/CustomChars/%s" % (smbzgPath, name)

def askGamePath():
    fileName, type = QtWidgets.QFileDialog.getOpenFileName(None, "Find SMBZ-G.exe", ".", "SMBZ-G.exe")
    print("Game path: %s" % os.path.dirname(fileName))
    return os.path.dirname(fileName)
