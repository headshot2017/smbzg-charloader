import os
import json
import copy

from pygame import mixer

import gamepath


name = ""
jsonFile = None
sounds = {}
effects = []
companions = []

__defaultaction = {
    "frame": [0, 0, 0, 0],
	"delay": 0,
    "setAnim": "",
    "offset": [0, 0],
    "scale": [1, 1],
    "angle": 0,
    "sound": "",
    "color": [255, 255, 255],
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
                "ingame": 1
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

def reset(defaultName=""):
    global name, jsonFile, sounds, effects, companions
    name = defaultName
    jsonFile = defaultCharacterData()
    sounds = {}
    effects = []
    companions = []

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
    companions = os.listdir("%s/companions" % path) if os.path.exists("%s/companions" % path) else []

    return jsonFile

def save():
    if not name:
        return False

    path = gamepath.getCharacterPath(name)
    json.dump(jsonFile, open("%s/character.json" % path, "w"), indent=2)
    return True
