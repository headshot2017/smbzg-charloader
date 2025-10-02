using MelonLoader;
using UnityEngine;

[assembly: MelonInfo(typeof(CustomCharacterTemplate.Core), "CustomCharacterTemplate", "1.0.0", "YourNameHere", null)]
[assembly: MelonGame("Jonathan Miller aka Zethros", "SMBZ-G")]

namespace CustomCharacterTemplate
{
    public class Core : MelonMod
    {
        public CustomCharacter myCC;

        public override void OnInitializeMelon()
        {
            LoggerInstance.Msg("Initialized.");

            // Add our own "LoadCharacter" function to CharLoader's "afterCharacterLoad" callbacks.
            // This will be called after CharLoader finishes reading a character's "character.json" file.
            // NOTE: Make sure to add SMBZ-G/Mods/CharLoader.dll as an assembly dependency!
            CharLoader.Core.afterCharacterLoad += LoadMyCharacter;


            // If you want to add an inventory system (e.g. a transformation item, or projectiles like Yoshi's eggs),
            // See the following lines of code.

            // This is called on UI_Participant.Reset()
            //CharLoader.Core.resetBattleParticipant += ResetBattleParticipant;

            // This is called on UI_InventoryContainer.SetupCharacterSpecificInventory()
            //CharLoader.Core.setupSpecificInventory += SetupCharacterSpecificInventory;
        }

        void LoadMyCharacter(CustomCharacter cc)
        {
            // Check if this custom character's internal name matches the one you're making.
            // The internal name is represented by the folder name in SMBZ-G_Data/StreamingAssets/CustomChars/<InternalName>
            if (cc.internalName != "CharacterInternalName") return;

            // This is our character!
            myCC = cc;

            // Grab our character's BattleGameObject prefab and...
            GameObject Prefab = cc.characterData.Prefab_BattleGameObject;

            // Replace the CustomBaseCharacter component with our own character's component.
            // See YourCharacterControl.cs. It's recommended that you rename the file name AND the class name to fit your character's name, e.g. DevilMarioControl
            CustomBaseCharacter old = Prefab.GetComponent<CustomBaseCharacter>();
            YourCharacterControl control = Prefab.AddComponent<YourCharacterControl>();

            // Transfer some important stuff from the old component to our new one.
            control.SetupFromOldComponent(cc, old);

            // Remove the old CustomBaseCharacter component.
            GameObject.Destroy(old);

            // Done at this point
        }


        // If you want to add an inventory system (e.g. a transformation item, or projectiles like Yoshi's eggs),
        // See the following lines of code.

        /*
        
        // This is called on UI_Participant.Reset()
        // This sets up the inventory data model. It is called first.
        void ResetBattleParticipant(BattleParticipantDataModel participant)
        {
            // Check that this is our character.
            if (participant.InitialCharacterData != myCC.characterData)
                return;

            // Check if we have an InventoryDataModel on our character's specific data dictionary.
            // if not, we add it.
            // You have to make this inventorydatamodel class yourself.
            // If you want an example, you can use another character's inventory data model as reference:
            // SMBZG.MarioInventoryDataModel
            // SMBZG.YoshiInventoryDataModel
            // SMBZG.MechaSonicInventoryDataModel
            // Or any other character's InventoryDataModel in the "SMBZG" namespace.
            // You can press F12 to look at disassembled source code of these classes.
            
            participant.AdditionalCharacterSpecificDataDictionary.TryGetValue("MyInventoryData", out var value);
            if (value == null)
            {
                YourCharacterInventoryDataModel value2 = new YourCharacterInventoryDataModel();
                participant.AdditionalCharacterSpecificDataDictionary.Add("MyInventoryData", value2);
            }
        }

        // This is called on UI_InventoryContainer.SetupCharacterSpecificInventory()
        // This sets up the inventory UI for the character. It is set up after creating the inventory data model.
        void SetupCharacterSpecificInventory(UI_InventoryContainer container, BattleParticipantDataModel participant)
        {
            // Check that this is our character.
            if (participant.InitialCharacterData != myCC.characterData)
                return;

            // Get the inventory data model that we set up earlier.
            participant.AdditionalCharacterSpecificDataDictionary.TryGetValue("MyInventoryData", out var obj);

            // Setup the inventory UI here!
            (obj as YourCharacterInventoryDataModel).SetupInventoryUI(container);
            return;
        }
        */
    }
}