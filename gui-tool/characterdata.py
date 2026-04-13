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
    "sound": {"sounds": [], "loop": False, "volume": 100, "pitch": 100, "pauseWithGame": False},
    "color": [255, 255, 255, 255],
    "hitbox": {"on": False, "pos": [0, 0], "scale": [1, 1]},
    "callCustomQueue": True,
    "puppets": {},
    "interpolation": 0
}

def defaultAction(name):
    return copy.deepcopy(__defaultaction[name]) if name in __defaultaction else None

def defaultPuppetAction(on=True):
    return {
        "on": on,
        "layer": 0,
        "offset": [0, 0],
        "scale": [1, 1],
        "angle": 0
    }

def defaultCommand():
    return {
        "title": "",
        "subtitle": "",
        "additionalInfo": "",
        "imageList": [],
        "featureList": []
    }

def defaultAnimationEntries():
    return [
        ["OnSelect", 0],
        ["Victory", 0],
        ["Defeat", 0],
        ["IdleCharSelect", -1],
        ["Idle", -1],
        ["IdleB", -1],
        ["Guard", -1],
        ["Block", -1],
        ["Slide", -1],
        ["Hit", 0],
        ["Hurt", 0],
        ["Hurt_AirUpwards", -1],
        ["Hurt_AirDownwards", -1],
        ["Tumble", 0],
        ["Grounded", 0],
        ["GetUp", 0],
        ["PreJump", -1],
        ["Jump", 0],
        ["Fall", 0],
        ["Land", 0],
        ["Walk", -1],
        ["Run", -1],
        ["Sprint", -1],
        ["Bursting", -1],
        ["BurstVictoryStrike", 0],
        ["BurstVictoryStrike_MR", 0],
        ["MR_Air_Idle", -1],
        ["MR_Air_MoveDownward", -1],
        ["MR_Air_MoveUpward", -1],
        ["MR_Air_MoveForward", -1],
        ["MR_Ground_Idle", -1],
        ["MR_Ground_Land", -1],
        ["MR_Ground_MoveForward", -1],
        ["MR_Strike_Approach", -1],
        ["MR_Strike_Attack", -1],
        ["MR_Strike_Finale", -1],
        ["MR_Dodge", 0]
    ]

def defaultCharacterData():
    return {
        "general": {
            "displayName": "",
            "unbalanced": False,
            "platform": 0,
            "scale": {
                "charSelect": 1,
                "results": 1,
                "ingame": 0.4
            },
            "offset": {
                "charSelect": [ 64, 64 ],
                "results": [ 320, 64 ],
                "ingame": [ 0, 0 ]
            },
            "colors": {
                "primary": [ 255, 255, 255 ],
                "secondary": [ 0, 0, 0 ],
                "alternateColors": [ 0.57, 1, 1 ]
            }
        },

        "editor": {
            "defaultFrameSize": [0, 0],
            "spriteSpacing": [0, 0],
            "defaultDelay": 0.0
        },

        "puppets": {},

        "effects": {},

        "commandList": [],
        
        "anims": {}
    }

def defaultEffect():
    return {
        "editor": {
            "defaultFrameSize": [0, 0],
            "spriteSpacing": [0, 0]
        },

        "loops": 0,

        "frames": []
    }

def defaultCompanion():
    return {
        "general": {
            "scale": 0.4,
            "offset": [0, 0]
        },

        "editor": {
            "defaultFrameSize": [0, 0],
            "spriteSpacing": [0, 0]
        },

        "puppets": {},

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

def reloadEffects():
    global effects

    path = gamepath.getCharacterPath(name)
    effects = os.listdir("%s/effects" % path) if os.path.exists("%s/effects" % path) else []

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

    reloadEffects()

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
