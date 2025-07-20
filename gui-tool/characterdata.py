import os
import shutil
import json
import copy

from pygame import mixer

import gamepath


name = ""
jsonFile = None
sounds = {}
effects = []
companionJson = {}

__defaultaction = {
    "frame": [0, 0, 0, 0],
	"delay": 0,
    "setAnim": "",
    "offset": [0, 0],
    "scale": [1, 1],
    "angle": 0,
    "sound": "",
    "color": [255, 255, 255, 255],
    "hitbox": {"on": False, "pos": [0, 0], "scale": [1, 1]},
    "callCustomQueue": True,
}

def defaultAction(name):
    return copy.deepcopy(__defaultaction[name]) if name in __defaultaction else None

def defaultCharacterData():
    return {
        "general": {
            "displayName": "",
            "scale": {
                "charSelect": 1,
                "results": 1,
                "ingame": 0.4
            },
            "offset": {
                "charSelect": [ 0, 0 ],
                "results": [ 0, 0 ],
                "ingame": [ 0, 0 ]
            },
            "colors": {
                "primary": [ 255, 255, 255 ],
                "secondary": [ 0, 0, 0 ]
            }
        },

        "effects": {},

        "commandList": [],
        
        "anims": {}
    }

def defaultCompanion():
    return {
        "general": {
            "scale": 0.4,
            "offset": [0, 0]
        },

        "anims": {}
    }

def createCompanionDir(companionName):
    path = gamepath.getCharacterPath(name)
    companionPath = "%s/companions/%s" % (path, companionName)
    if not os.path.exists(companionPath): os.makedirs(companionPath)

def deleteCompanion(companionName):
    path = gamepath.getCharacterPath(name)
    companionPath = "%s/companions/%s" % (path, companionName)

    if os.path.exists(companionPath): shutil.rmtree(companionPath)
    if companionName in companionJson: del companionJson[companionName]

def reset(defaultName=""):
    global name, jsonFile, sounds, effects, companionJson
    name = defaultName
    jsonFile = defaultCharacterData()
    sounds = {}
    effects = []
    companionJson = {}

def load(charName):
    global name, jsonFile, sounds, effects, companions

    reset()

    path = gamepath.getCharacterPath(charName)

    name = charName
    jsonFile = json.load(open("%s/character.json" % path))
    if not jsonFile: return None

    if os.path.exists("%s/sounds" % path):
        for f in os.listdir("%s/sounds" % path):
            sounds[os.path.splitext(f)[0]] = mixer.Sound("%s/sounds/%s" % (path, f))

    effects = os.listdir("%s/effects" % path) if os.path.exists("%s/effects" % path) else []

    if os.path.exists("%s/companions" % path):
        for f in os.listdir("%s/companions" % path):
            if not os.path.isdir("%s/companions/%s" % (path, f)): continue
            jsonFilePath = "%s/companions/%s/companion.json" % (path, f)
            companionJson[f] = json.load(open(jsonFilePath)) if os.path.exists(jsonFilePath) else {}

    return jsonFile

def save():
    if not name:
        return False

    path = gamepath.getCharacterPath(name)
    json.dump(jsonFile, open("%s/character.json" % path, "w"), indent=2)

    for companion in companionJson:
        companionPath = "%s/companions/%s" % (path, companion)
        if not os.path.exists(companionPath): os.makedirs(companionPath)
        json.dump(companionJson[companion], open("%s/companion.json" % companionPath, "w"), indent=2)

    return True
