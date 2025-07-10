# CharLoader

Custom character loader for SMBZ-G.

Requires [MelonLoader](https://github.com/LavaGang/MelonLoader/releases)

## Custom characters folder structure
```
└── SMBZ-G_Data
    └── StreamingAssets
        └── CustomChars
            └── (Internal Character Name)
                ├── effects/
                │   └── .png files
                ├── companions/
                │   └── (Companion character name)
                │       ├── sheet.png
                │       └── companion.json
                ├── sounds/
                │   └── .wav, .ogg or .mp3 files
                ├── sheet.png
                ├── battleportrait.png
                ├── portrait.png
                └── character.json
```

* **effects:** Assortment of png files that can be used as custom particle effects with CustomEffectSprite.
* **companions:** "Characters" that can be used as NPCs or transformations for the base character.
* **sounds:** Folder containing sound files
* **sheet.png**: Character's sprite sheet
* **battleportrait.png**: Portrait used in the battle HUD
* **portrait.png**: Portrait used in the character select screen
* **character.json**: Contains important definitions such as: Character's display name, scale, colors, effects (custom particles), the command list, and all of its' animations

## Quick starting point for developing custom characters

* Install MelonLoader on SMBZ-G
* Install the [MelonLoader Wizard Extension for Visual Studio](https://github.com/TrevTV/MelonLoader.VSWizard/releases)
* Download CharLoader.dll and put it in the SMBZ-G Mods folder
* Create a new project in Visual Studio using the MelonLoader Mod template
* When asked to select an executable file, choose SMBZ-G.exe
* Add CharLoader.dll as an assembly dependency
* CharLoader.Core has these callbacks that you can implement:
  * afterCharacterLoad: Called after a CustomCharacter is loaded. You must check if it's your character by comparing the internalName, which by then you can replace the SonicControl component with your own character control component. This one is important.
  * resetBattleParticipant: Called on BattleParticipantDataModel.Reset(). Compare participant.InitialCharacterData with CustomCharacter.characterData to check if it's your custom character. This is used for setting up participant.AdditionalCharacterSpecificDataDictionary, for things like inventory data models. If your character doesn't have an inventory, this can be ignored
  * setupSpecificInventory: Called when setting up the character's inventory UI. Compare participant.InitialCharacterData with CustomCharacter.characterData to check if it's your custom character. This is where you'd call the SetupInventoryUI function on your Inventory data model. If your character doesn't have an inventory, this can be ignored

## Some info

* It's recommended to use the CharLoader GUI Tool for animating your characters instead of editing character.json by hand
  * (This GUI tool program is still in development)
* In your character's C# code, character control classes must inherit CustomBaseCharacter instead of BaseCharacter
* You can use CustomEffectSprite to spawn custom particles

## Third-party libraries

* [TinyJSON](https://github.com/pbhogan/TinyJSON)
