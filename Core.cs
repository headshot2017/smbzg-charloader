using MelonLoader;
using SMBZG;
using SMBZG.CharacterSelect;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
using HarmonyLib;

[assembly: MelonInfo(typeof(CharLoader.Core), "CharLoader", "1.6", "Headshotnoby/headshot2017", null)]
[assembly: MelonGame("Jonathan Miller aka Zethros", "SMBZ-G")]

namespace CharLoader
{
    public class Core : MelonMod
    {
        public static List<CustomCharacter> customCharacters = new List<CustomCharacter>();

        public delegate void PostCharacterLoad(CustomCharacter cc);
        public delegate void BattleParticipantDelegate(BattleParticipantDataModel participant);
        public delegate void SetupInventoryUIDelegate(UI_InventoryContainer container, BattleParticipantDataModel participant);

        public static PostCharacterLoad s_CharLoadCallbackHandler;
        public static BattleParticipantDelegate s_ResetBPCallbackHandler;
        public static SetupInventoryUIDelegate s_SetupSpecificInventoryCallbackHandler;

        public static event PostCharacterLoad afterCharacterLoad
        {
            add
            {
                s_CharLoadCallbackHandler = (PostCharacterLoad)Delegate.Combine(s_CharLoadCallbackHandler, value);
            }
            remove
            {
                s_CharLoadCallbackHandler = (PostCharacterLoad)Delegate.Remove(s_CharLoadCallbackHandler, value);
            }
        }

        public static event BattleParticipantDelegate resetBattleParticipant
        {
            add
            {
                s_ResetBPCallbackHandler = (BattleParticipantDelegate)Delegate.Combine(s_ResetBPCallbackHandler, value);
            }
            remove
            {
                s_ResetBPCallbackHandler = (BattleParticipantDelegate)Delegate.Remove(s_ResetBPCallbackHandler, value);
            }
        }

        public static event SetupInventoryUIDelegate setupSpecificInventory
        {
            add
            {
                s_SetupSpecificInventoryCallbackHandler = (SetupInventoryUIDelegate)Delegate.Combine(s_SetupSpecificInventoryCallbackHandler, value);
            }
            remove
            {
                s_SetupSpecificInventoryCallbackHandler = (SetupInventoryUIDelegate)Delegate.Remove(s_SetupSpecificInventoryCallbackHandler, value);
            }
        }


        public static MelonPreferences_Category Preferences_General;
        public static MelonPreferences_Entry<bool> ArcadeModeLineup;


        public override void OnInitializeMelon()
        {
            Preferences_General = MelonPreferences.CreateCategory("General");
            Preferences_General.SetFilePath("UserData/CharLoader.cfg");

            ArcadeModeLineup = Preferences_General.CreateEntry<bool>("CustomCharsOnArcadeLineup", false);

            LoggerInstance.Msg("Initialized.");
        }

        void LogHandler(string message, string stacktrace, LogType type)
        {
            if (type != LogType.Exception && type != LogType.Error)
                return;
            LoggerInstance.Msg($"{message}\n{stacktrace}");
        }

        public override void OnLateInitializeMelon()
        {
            Application.logMessageReceived += LogHandler;

            // change all characters' CharacterData_SO instances to CustomCharacterData_SO
            // this allows adding extra information to them that can be used by custom characters
            foreach (FieldInfo field in typeof(BattleCache).GetFields())
            {
                if (!field.Name.StartsWith("CharacterData_")) continue;

                CharacterData_SO oldData = (CharacterData_SO)field.GetValue(BattleCache.ins);
                if (oldData == null) continue;
                CustomCharacterData_SO newData = ScriptableObject.CreateInstance<CustomCharacterData_SO>();
                newData.name = oldData.name;
                newData.hideFlags = oldData.hideFlags;

                // copy all the fields from old one to new one
                foreach (FieldInfo dataField in typeof(CharacterData_SO).GetFields())
                    dataField.SetValue(newData, dataField.GetValue(oldData));

                field.SetValue(BattleCache.ins, newData);
            }

            // modify koopa bros to use a custom class
            // that way, custom characters can do shenanigans such as changing the leader,
            // making the bros follow a different character
            GameObject KoopaBrosPrefab = BattleCache.ins.CharacterData_KoopaBros.Prefab_BattleGameObject;

            KoopaRedControl original = KoopaBrosPrefab.GetComponent<KoopaRedControl>();
            CustomKoopaRedControl custom = KoopaBrosPrefab.AddComponent<CustomKoopaRedControl>();
            foreach (FieldInfo field in original.GetType().GetFields(BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic))
            {
                try
                {
                    custom.GetType().BaseType.GetField(field.Name, BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).SetValue(custom, field.GetValue(original));
                }
                catch (Exception)
                {

                }
            }
            typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(custom,
                typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(original));

            KoopaBroControl originalBro = original.KoopaBro_Prefab.GetComponent<KoopaBroControl>();
            CustomKoopaBroControl customBro = original.KoopaBro_Prefab.AddComponent<CustomKoopaBroControl>();
            foreach (FieldInfo field in originalBro.GetType().GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic))
            {
                try
                {
                    customBro.GetType().BaseType.GetField(field.Name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).SetValue(customBro, field.GetValue(originalBro));
                }
                catch (Exception)
                {

                }
            }
            typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(customBro,
                typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(originalBro));

            GameObject.Destroy(originalBro);
            GameObject.Destroy(original);


            LoadCustomCharList();
        }

        public override void OnSceneWasInitialized(int buildIndex, string sceneName)
        {
            if (buildIndex == 7)
                SetupCharSelectVersus();
            if (buildIndex == 8)
                SetupCharSelectArcade();
        }

        void LoadCustomCharList()
        {
            GameObject obj = new GameObject("CharLoader");
            GameObject.DontDestroyOnLoad(obj);
            CharLoaderComponent dl = obj.AddComponent<CharLoaderComponent>();
        }

        void SetupPortraits(Transform PortraitTableRoot, CharacterSelectScript_Base charSelect)
        {
            // Add character portraits

            Transform PortraitRow = PortraitTableRoot.GetChild(PortraitTableRoot.childCount - 1);
            GameObject PortraitNewRow = GameObject.Instantiate(PortraitRow.gameObject, PortraitTableRoot);
            PortraitNewRow.transform.RemoveAllChildren();
            PortraitNewRow.name = "CustomRow";
            PortraitNewRow.transform.localPosition = PortraitRow.localPosition + new Vector3(0, -65);

            foreach (CustomCharacter cc in customCharacters)
            {
                GameObject PortraitGameObj = GameObject.Instantiate(PortraitRow.GetChild(0).gameObject, PortraitNewRow.transform);
                CharacterPortrait Portrait = PortraitGameObj.GetComponent<CharacterPortrait>();
                Image PortraitImg = PortraitGameObj.GetComponent<Image>();
                PortraitGameObj.name = $"Character_{cc.internalName}";
                Portrait.Data = cc.characterData;
                PortraitImg.sprite = cc.portrait;
                charSelect.CharacterPortraitList.Add(Portrait);
            }
        }

        void SetupCharSelectArcade()
        {
            Transform CharacterSelectRoot = GameObject.Find("Canvas").transform.Find("CharacterSelect");
            Transform PortraitTableRoot = CharacterSelectRoot.Find("CharacterSelectPortraitTable");
            SetupPortraits(PortraitTableRoot, CharacterSelectAcradeScript.ins);

            // Setup additional UIs

            // Part 1: GameObjects
            Transform root = CharacterSelectRoot.Find("VBox_Settings");

            GameObject BattleCustomCharsObj = GameObject.Instantiate(root.Find("BattleRandomSkins").gameObject, root);
            GameObject BattleCustomCharsLabelObj = BattleCustomCharsObj.transform.GetChild(0).gameObject;
            GameObject BattleCustomCharsToggleObj = BattleCustomCharsObj.transform.GetChild(1).gameObject;

            BattleCustomCharsObj.name = "BattleCustomChars";
            BattleCustomCharsLabelObj.name = "Label_BattleCustomChars";
            BattleCustomCharsToggleObj.name = "Toggle_BattleCustomChars";


            // Part 2: Components
            TMPro.TextMeshProUGUI BattleCustomCharsLabel = BattleCustomCharsLabelObj.GetComponent<TMPro.TextMeshProUGUI>();
            Toggle BattleCustomCharsToggle = BattleCustomCharsToggleObj.GetComponent<Toggle>();

            BattleCustomCharsLabel.text = "Custom Characters in Line-up";
            BattleCustomCharsLabel.fontSize = 20;
            BattleCustomCharsToggle.onValueChanged.RemoveAllListeners();
            BattleCustomCharsToggle.isOn = ArcadeModeLineup.Value;
            BattleCustomCharsToggle.onValueChanged.AddListener(OnCustomCharsToggle);
        }

        void SetupCharSelectVersus()
        {
            Transform PortraitTableRoot = CharacterSelectScript.ins.Section_CharacterSelect.transform.Find("CharacterSelectPortraitTable");
            SetupPortraits(PortraitTableRoot, CharacterSelectScript.ins);
        }

        void OnCustomCharsToggle(bool on)
        {
            ArcadeModeLineup.Value = on;
            MelonPreferences.Save();
        }

        [HarmonyPatch(typeof(CharacterSelectAcradeScript), "OnSubmit")]
        private static class ArcadeSubmitPatch
        {
            private static bool Prefix(CharacterSelectAcradeScript __instance)
            {
                if (!ArcadeModeLineup.Value)
                    return true;

                List<CharacterSelectPlayerInputHandler_Base> ActiveCharacterSelectPlayerInputHandlerList =
                    (List<CharacterSelectPlayerInputHandler_Base>)__instance.GetType().GetField("ActiveCharacterSelectPlayerInputHandlerList", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(__instance);

                bool flag = true;
                foreach (CharacterSelectArcadePlayerInputHandler activeCharacterSelectPlayerInputHandler in ActiveCharacterSelectPlayerInputHandlerList)
                {
                    int CurrentState = (int)activeCharacterSelectPlayerInputHandler.GetType().GetProperty("CurrentState", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(activeCharacterSelectPlayerInputHandler);
                    UI_Participant ParticipantUI_MyPrimary = (UI_Participant)activeCharacterSelectPlayerInputHandler.GetType().GetProperty("ParticipantUI_MyPrimary", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(activeCharacterSelectPlayerInputHandler);

                    if (CurrentState != 7 && ParticipantUI_MyPrimary != null)
                    {
                        // 7 = HoveringGoNext
                        flag = false;
                        break;
                    }
                }

                bool flag2 = __instance.GetParticipantUIs().Count >= 1;
                if (!flag || !flag2)
                {
                    LeanTween.cancel(__instance.UI_NextFromCharacterToStageSelect.gameObject);
                    __instance.UI_NextFromCharacterToStageSelect.transform.localScale = Vector3.one;
                    LeanTween.scale(__instance.UI_NextFromCharacterToStageSelect.gameObject, Vector3.one * 1.1f, 0.1f).setOnComplete((Action)delegate
                    {
                        LeanTween.scale(__instance.UI_NextFromCharacterToStageSelect.gameObject, Vector3.one, 0.1f);
                    });
                    return false;
                }

                SaveData.Data.LastUsedArcadeCpuHealth = Helpers.TryParseToFloatWithFallback(__instance.Input_BattleHealth.text, 150f);
                SaveData.Save();

                List<CharacterData_SO> array = new List<CharacterData_SO>
                {
                    BattleCache.ins.CharacterData_Mario,
                    BattleCache.ins.CharacterData_Luigi,
                    BattleCache.ins.CharacterData_Yoshi,
                    BattleCache.ins.CharacterData_Goomba,
                    BattleCache.ins.CharacterData_KoopaBros,
                    BattleCache.ins.CharacterData_Sonic,
                    BattleCache.ins.CharacterData_AxemRangersX,
                    BattleCache.ins.CharacterData_Shadow,
                    BattleCache.ins.CharacterData_Basilisx,
                    BattleCache.ins.CharacterData_MechaSonic
                };
                foreach (CustomCharacter cc in customCharacters)
                    array.Add(cc.characterData);

                List<BattleSettings> list = new List<BattleSettings>();
                foreach (CharacterData_SO characterData_SO in array)
                {
                    BattleSettings battleSettings = new BattleSettings
                    {
                        RoundsToWin = 1,
                        Stage = BattleCache.GetRandomStage(),
                        TeamsList = new List<BattleSettings.TeamDataModel>(),
                        DefaultParticipantHealth = SaveData.Data.LastUsedArcadeCpuHealth
                    };
                    BattleSettings.TeamDataModel teamDataModel = new BattleSettings.TeamDataModel(BattleCache.teamTags[1])
                    {
                        ParticipantSettingList = new List<BattleParticipantSettings>()
                    };
                    battleSettings.TeamsList.Add(teamDataModel);
                    UI_Participant[] array2 = UnityEngine.Object.FindObjectsOfType<UI_Participant>(includeInactive: true);
                    UI_Participant[] array3 = array2;
                    foreach (UI_Participant uI_Participant in array3)
                    {
                        // I HATE THIS
                        int ParticipantIndex = (int)uI_Participant.GetType().GetField("ParticipantIndex", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        CharacterData_SO SelectedCharacter = (CharacterData_SO)uI_Participant.GetType().GetField("SelectedCharacter", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        BattleCache.CPUSettingsENUM CPUSetting = (BattleCache.CPUSettingsENUM)uI_Participant.GetType().GetField("CPUSetting", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        int? InputPlayerIndex = (int?)uI_Participant.GetType().GetField("InputPlayerIndex", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        string SkinName = ((CharacterSkinDataStore.Skin)uI_Participant.Input_Skin.GetType().GetMethod("GetValue", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(uI_Participant.Input_Skin, null)).Name;
                        PlayerProfileModel SelectedProfile = (PlayerProfileModel)uI_Participant.GetType().GetMethod("GetSelectedProfile", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(uI_Participant, null);
                        bool AlternateColor_IsEnabled = (bool)uI_Participant.GetType().GetField("AlternateColor_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        bool StandaloneTransformation_IsEnabled = (bool)uI_Participant.GetType().GetField("StandaloneTransformation_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        bool Luigi_SJPGambit_IsEnabled = (bool)uI_Participant.GetType().GetField("Luigi_SJPGambit_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        bool Luigi_ItemToss_IsEnabled = (bool)uI_Participant.GetType().GetField("Luigi_ItemToss_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        bool Goomba_SSMechaIntro_IsEnabled = (bool)uI_Participant.GetType().GetField("Goomba_SSMechaIntro_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);
                        bool KoopaBros_KoopaBro_IsEnabled = (bool)uI_Participant.GetType().GetField("KoopaBros_KoopaBro_IsEnabled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(uI_Participant);

                        BattleParticipantSettings item = new BattleParticipantSettings
                        {
                            ParticipantIndex = ParticipantIndex,
                            CharacterData = SelectedCharacter,
                            TeamTag = teamDataModel.TeamTag,
                            CPUSettings = CPUSetting,
                            HealthMax = (uI_Participant.Toggle_Health.isOn ? uI_Participant.Input_Health.value : battleSettings.DefaultParticipantHealth),
                            InputDelay = (int)uI_Participant.Input_Delay.value,
                            InputPlayerIndex = InputPlayerIndex,
                            SkinName = SkinName,
                            PlayerProfile = SelectedProfile,
                            UseAlternateColor = AlternateColor_IsEnabled,
                            IsStandaloneTransformation = StandaloneTransformation_IsEnabled,
                            Luigi_SJPGambit_IsEnabled = Luigi_SJPGambit_IsEnabled,
                            Luigi_ItemToss_IsEnabled = Luigi_ItemToss_IsEnabled,
                            Goomba_SSMechaIntro_IsEnabled = Goomba_SSMechaIntro_IsEnabled,
                            KoopaBros_KoopaBro_IsEnabled = KoopaBros_KoopaBro_IsEnabled
                        };
                        teamDataModel.ParticipantSettingList.Add(item);
                    }

                    List<BattleCache.CPUSettingsENUM> CPUSettingList = (List<BattleCache.CPUSettingsENUM>)__instance.GetType().GetField("CPUSettingList", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(__instance);
                    battleSettings.TeamsList.Add(new BattleSettings.TeamDataModel(BattleCache.teamTags[2])
                    {
                        ParticipantSettingList = new List<BattleParticipantSettings>
                        {
                            new BattleParticipantSettings(1, BattleCache.teamTags[2], characterData_SO, CPUSettingList[__instance.Difficulty_CPUSetting.value], SaveData.Data.LastUsedArcadeCpuHealth, string.Empty, 0, null)
                            {
                                ParticipantIndex = array2.Select((UI_Participant p) => (int)p.GetType().GetField("ParticipantIndex", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(p)).DefaultIfEmpty(1).Max() + 100
                            }
                        }
                    });
                    if (SaveData.Data.ArcadeRandomSkinsEnabled)
                    {
                        foreach (BattleParticipantSettings participantSetting in battleSettings.TeamsList[1].ParticipantSettingList)
                        {
                            CharacterSkinDataStore.Skin random = CharacterSkinManager.ins.GetCharacterSkinData(characterData_SO.Character).SkinList.GetRandom();
                            participantSetting.SkinName = random.Name;
                        }
                    }
                    else if (SaveData.Data.Get_MainMenuScenaryMode() == SceneConstants.MainMenuScenaryModeENUM.Halloween2022)
                    {
                        foreach (BattleParticipantSettings participantSetting2 in battleSettings.TeamsList[1].ParticipantSettingList)
                        {
                            participantSetting2.SkinName = "Halloween";
                        }
                    }

                    list.Add(battleSettings);
                }

                BattleParticipantSettings battleParticipantSettings = list.First((BattleSettings r) => r.TeamsList[1].ParticipantSettingList[0].CharacterData.Character == BattleCache.CharacterEnum.Goomba).TeamsList[1].ParticipantSettingList[0];
                battleParticipantSettings.HealthMax = Mathf.Round(battleParticipantSettings.HealthMax * 0.6666666f);
                if (battleParticipantSettings.HealthMax < 0f)
                {
                    battleParticipantSettings.HealthMax = 1f;
                }

                list.Last().TeamsList[1].ParticipantSettingList[0].HealthMax *= 1.25f;

                Melon<Core>.Logger.Msg($"Starting Arcade Mode with the following character line-up:");
                foreach (CharacterData_SO characterData_SO in array)
                {
                    Melon<Core>.Logger.Msg(BattleCache.Character_GetDisplayName(characterData_SO.Character));
                }

                GC.ins.InitArcadeBattles(list);

                return false;
            }
        }

        [HarmonyPatch(typeof(BattleParticipantDataModel), "Reset")]
        private static class ResetBattleParticipantPatch
        {
            private static void Postfix(BattleParticipantDataModel __instance)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != __instance.InitialCharacterData) continue;
                    s_ResetBPCallbackHandler?.Invoke(__instance);
                }
            }
        }

        [HarmonyPatch(typeof(UI_InventoryContainer), "SetupCharacterSpecificInventory", new Type[] { typeof(BattleParticipantDataModel) })]
        private static class SetupInventoryPatch
        {
            private static void Postfix(UI_InventoryContainer __instance, BattleParticipantDataModel participant)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != participant.InitialCharacterData) continue;
                    s_SetupSpecificInventoryCallbackHandler?.Invoke(__instance, participant);
                }
            }
        }


        [HarmonyPatch(typeof(BattleController), "Pause_OnClick_CommandList", new Type[] { typeof(int) })]
        private static class CommandListPatch
        {
            private static bool Prefix(BattleController __instance, int PlayerIndex)
            {
                //CharacterControl Player1 = (CharacterControl)typeof(BattleController).GetField("Player1", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                //CharacterControl Player2 = (CharacterControl)typeof(BattleController).GetField("Player2", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                List<CharacterControl> ActiveCharacterControlList = (List<CharacterControl>)typeof(BattleController).GetField("ActiveCharacterControlList", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                CharacterControl characterControl = ((PlayerIndex == 2) ? ActiveCharacterControlList.ElementAtOrDefault(1) : ActiveCharacterControlList.ElementAtOrDefault(0));
                BattleParticipantDataModel PlayerModel = characterControl.ParticipantDataReference;
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData == PlayerModel.InitialCharacterData)
                    {
                        __instance.PauseMenuPanel_CommandList.gameObject.SetActive(true);
                        __instance.PauseMenuPanel_CommandList.Button_Close.Select();
                        __instance.PauseMenuPanel_CommandList.Load(cc.commandList);
                        return false;
                    }
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(BattleCache), "Character_GetDisplayName", new Type[] { typeof(BattleCache.CharacterEnum) })]
        private static class DisplayNamePatch
        {
            private static bool Prefix(ref string __result, BattleCache.CharacterEnum character)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData.Character != character) continue;
                    __result = cc.rootCharacter.name;
                    return false;
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(BattleCache), "Character_GetInternalName", new Type[] { typeof(BattleCache.CharacterEnum) })]
        private static class InternalNamePatch
        {
            private static bool Prefix(ref string __result, BattleCache.CharacterEnum character)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData.Character != character) continue;
                    __result = cc.internalName;
                    return false;
                }

                return true;
            }
        }

        /*
        [HarmonyPatch(typeof(FormsListManager), "Character_GetFormsLists", new Type[] { typeof(BattleCache.CharacterEnum) })]
        private static class FormsListPatch
        {
            private static bool Prefix(ref string __result, BattleCache.CharacterEnum character)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData.Character != character) continue;
                    __result = cc.internalName+"Forms";
                    return false;
                }

                return true;
            }
        }
        */

        [HarmonyPatch(typeof(BattleCache), "GetCharacterByInternalCharacterName", new Type[] { typeof(string) })]
        private static class InternalStringNamePatch
        {
            private static bool Prefix(ref BattleCache.CharacterEnum __result, string internalCharacterName)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.internalName != internalCharacterName) continue;
                    __result = cc.characterData.Character;
                    return false;
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(BattleCache), "Character_GetPrefab", new Type[] { typeof(BattleCache.CharacterEnum) })]
        private static class GetPrefabPatch
        {
            private static bool Prefix(BattleCache __instance, ref GameObject __result, BattleCache.CharacterEnum character)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData.Character != character) continue;
                    __result = cc.characterData.Prefab_BattleGameObject;
                    return false;
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(UI_Participant), "HoverCharacter", new Type[] { typeof(CharacterData_SO) })]
        private static class HoverCharacterPatch
        {
            private static bool Prefix(UI_Participant __instance, CharacterData_SO characterData)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != characterData) continue;

                    GameObject imageObj = null;
                    for (int i = 0; i < __instance.gameObject.transform.childCount; i++)
                    {
                        GameObject temp = __instance.gameObject.transform.GetChild(i).gameObject;
                        if (temp.name == "Image_Character")
                        {
                            imageObj = temp;
                            break;
                        }
                    }

                    if (!imageObj) break;

                    CustomAnimator c = imageObj.GetComponent<CustomAnimator>();
                    if (!c) c = imageObj.AddComponent<CustomAnimator>();
                    c.IgnoreColorAction = true;
                    c.SetAnimList(cc.rootCharacter.animations, imageObj.transform.GetChild(0).gameObject, cc.charSelectOffset, cc.charSelectScale);
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(UI_Participant), "SelectCharacter", new Type[] { typeof(CharacterData_SO) })]
        private static class SelectCharacterPatch
        {
            private static bool Prefix(UI_Participant __instance, CharacterData_SO characterData)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != characterData) continue;

                    GameObject imageObj = null;
                    for (int i = 0; i < __instance.gameObject.transform.childCount; i++)
                    {
                        GameObject temp = __instance.gameObject.transform.GetChild(i).gameObject;
                        if (temp.name == "Image_Character")
                        {
                            imageObj = temp;
                            break;
                        }
                    }

                    if (!imageObj) break;

                    CustomAnimator c = imageObj.GetComponent<CustomAnimator>();
                    if (!c) c = imageObj.AddComponent<CustomAnimator>();
                    c.m_OriginalAnimator = imageObj.GetComponent<Animator>();
                    c.IgnoreColorAction = true;
                    c.SetAnimList(cc.rootCharacter.animations, imageObj.transform.GetChild(0).gameObject, cc.charSelectOffset, cc.charSelectScale);
                }

                return true;
            }
        }

        [HarmonyPatch(typeof(UI_Participant), "HandleInput")]
        private static class HandleInputPatch
        {
            private static bool Prefix(UI_Participant __instance)
            {
                int? UI_OwnershipPlayerIndex = (int?)typeof(UI_Participant).GetProperty("UI_OwnershipPlayerIndex", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                if (UI_OwnershipPlayerIndex == null)
                    return false;

                var playerInput = GlobalInputManager.ins.GetPlayerInputByIndex(UI_OwnershipPlayerIndex);
                if (playerInput == null)
                {
                    LogHelper.LogError($"Failed to find player index {UI_OwnershipPlayerIndex.Value}");
                    return false;
                }

                var pInput = playerInput.InputActionAsset.CharacterSelect;
                var selectedElement = playerInput.EventSystem.currentSelectedGameObject;
                if (selectedElement == __instance.Input_Health.gameObject)
                {
                    // sliders already increment/decrement by 1, so keep that in mind.
                    int increment = 9;
                    if (pInput.Submit.IsPressed())
                    {
                        increment -= 9;
                    }
                    if (increment != 0)
                    {
                        if (pInput.Right.WasPressedThisFrame())
                        {
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                            __instance.Input_Health.value += increment;
                        }
                        else if (pInput.Left.WasPressedThisFrame())
                        {
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                            __instance.Input_Health.value -= increment;
                        }
                    }
                }
                if (selectedElement == __instance.Input_Delay.gameObject)
                {
                    // sliders already increment/decrement by 1, so keep that in mind.
                    int increment = 9;
                    if (pInput.Submit.IsPressed())
                    {
                        increment += 9;
                    }
                    if (increment != 0)
                    {
                        if (pInput.Right.WasPressedThisFrame())
                        {
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                            __instance.Input_Delay.value += increment;
                        }
                        else if (pInput.Left.WasPressedThisFrame())
                        {
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                            __instance.Input_Delay.value -= increment;
                        }
                    }
                }
                if (selectedElement == __instance.Image_Team.gameObject)
                {
                    string TeamTag = (string)typeof(UI_Participant).GetField("TeamTag", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                    var index = BattleCache.teamTags.IndexOf(TeamTag);
                    bool doChangeTeam = false;
                    if (pInput.Right.WasPressedThisFrame())
                    {
                        index++;
                        doChangeTeam = true;
                        SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                    }
                    else if (pInput.Left.WasPressedThisFrame())
                    {
                        index--;
                        doChangeTeam = true;
                        SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                    }
                    if (doChangeTeam)
                    {
                        if (index < 1)
                            index = BattleCache.teamTags.Count - 1;
                        if (index > BattleCache.teamTags.Count - 1)
                            index = 1;
                        __instance.UpdateTeamTag(BattleCache.teamTags[index]);
                    }
                }

                var handler = (CharacterSelectPlayerInputHandler_Base)typeof(UI_Participant).GetMethod("GetHandler", BindingFlags.NonPublic | BindingFlags.Instance).Invoke(__instance, null);

                // When participant doesn't have a character selected...
                if (selectedElement == __instance.Input_SelectedCharacter.gameObject)
                {
                    CharacterData_SO SelectedCharacter = (CharacterData_SO)typeof(UI_Participant).GetField("SelectedCharacter", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                    CharacterSelectScript_Base CSScript = (CharacterSelectScript_Base)typeof(UI_Participant).GetField("CSScript", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);
                    FieldInfo CharacterSelectionCurrentIndex = handler.GetType().GetField("CharacterSelectionCurrentIndex", BindingFlags.NonPublic | BindingFlags.Instance);
                    FieldInfo StandaloneTransformation_IsEnabled = typeof(UI_Participant).GetField("StandaloneTransformation_IsEnabled", BindingFlags.NonPublic | BindingFlags.Instance);
                    FieldInfo FollowPlayerEventSystem = typeof(UI_PlayerCursor).GetField("FollowPlayerEventSystem", BindingFlags.NonPublic | BindingFlags.Instance);
                    MethodInfo HoverCharacterPortrait = typeof(UI_Participant).GetMethod("HoverCharacterPortrait", BindingFlags.NonPublic | BindingFlags.Instance, null, new Type[] { typeof(CharacterPortrait) }, null);
                    MethodInfo SelectCharacter = typeof(UI_Participant).GetMethod("SelectCharacter", BindingFlags.NonPublic | BindingFlags.Instance, null, new Type[] { typeof(CharacterData_SO) }, null);
                    MethodInfo BeginCharacterSelection = typeof(UI_Participant).GetMethod("BeginCharacterSelection", BindingFlags.NonPublic | BindingFlags.Instance);
                    MethodInfo MoveToPosition = typeof(UI_PlayerCursor).GetMethod("MoveToPosition", BindingFlags.NonPublic | BindingFlags.Instance, null, new Type[] { typeof(RectTransform) }, null);
                    MethodInfo SetState_HoveringLastActionButton = handler.GetType().GetMethod("SetState_HoveringLastActionButton", BindingFlags.NonPublic | BindingFlags.Instance);
                    UI_Participant ParticipantUI_CurrentlySelected = (UI_Participant)handler.GetType().GetField("ParticipantUI_CurrentlySelected", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(handler);
                    bool IsCPU = (bool)typeof(UI_Participant).GetProperty("IsCPU", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(__instance);

                    if (SelectedCharacter == null)
                    {
                        var cList = CSScript.CharacterPortraitList;

                        Transform CharacterSelectRoot = GameObject.Find("Canvas").transform.Find("CharacterSelect");
                        if (!CharacterSelectRoot)
                            CharacterSelectRoot = GameObject.Find("Canvas").transform.Find("CharacterSelectPage");
                        Transform PortraitTableRoot = CharacterSelectRoot.Find("CharacterSelectPortraitTable");

                        int rowCount = PortraitTableRoot.childCount;
                        List<int> columnsInRows = new List<int>();
                        List<int> rowStartIndex = new List<int>();
                        for (int i = 0; i < rowCount; i++)
                        {
                            rowStartIndex.Add(columnsInRows.Sum(x => x));
                            columnsInRows.Add(PortraitTableRoot.GetChild(i).childCount);
                        }
                        int currentRow = -1;
                        for (int i=rowCount-1; i>=0; i--)
                        {
                            if ((int)CharacterSelectionCurrentIndex.GetValue(handler) >= rowStartIndex[i])
                            {
                                currentRow = i;
                                break;
                            }
                        }

                        // Listen to left/right inputs to switch between the options.
                        if (pInput.Right.WasPressedThisFrame())
                        {
                            CharacterSelectionCurrentIndex.SetValue(handler, (int)CharacterSelectionCurrentIndex.GetValue(handler) + 1);
                            if (cList.Count <= (int)CharacterSelectionCurrentIndex.GetValue(handler))
                                CharacterSelectionCurrentIndex.SetValue(handler, 0);
                            var portrait = cList[(int)CharacterSelectionCurrentIndex.GetValue(handler)];
                            HoverCharacterPortrait.Invoke(__instance, new object[] { portrait });
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }
                        else if (pInput.Left.WasPressedThisFrame())
                        {
                            CharacterSelectionCurrentIndex.SetValue(handler, (int)CharacterSelectionCurrentIndex.GetValue(handler) - 1);
                            if ((int)CharacterSelectionCurrentIndex.GetValue(handler) < 0)
                                CharacterSelectionCurrentIndex.SetValue(handler, cList.Count - 1);
                            var portrait = cList[(int)CharacterSelectionCurrentIndex.GetValue(handler)];
                            HoverCharacterPortrait.Invoke(__instance, new object[] { portrait });
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }
                        if (pInput.Down.WasPressedThisFrame())
                        {
                            int nextRow = currentRow + 1;
                            if (nextRow >= rowCount) nextRow = 0;
                            bool evenDifferences = (columnsInRows[currentRow] % 2) != (columnsInRows[nextRow] % 2);
                            int awayFromCenter = -(rowStartIndex[currentRow] + columnsInRows[currentRow]/2 - (int)CharacterSelectionCurrentIndex.GetValue(handler));
                            if (evenDifferences)
                            {
                                if (columnsInRows[currentRow] % 2 == 0)
                                    awayFromCenter++;
                                else
                                    awayFromCenter--;
                            }

                            int nextIndex = Mathf.Clamp(
                                rowStartIndex[nextRow] + columnsInRows[nextRow]/2 + awayFromCenter,
                                rowStartIndex[nextRow],
                                rowStartIndex[nextRow] + columnsInRows[nextRow] - 1
                            );
                            CharacterSelectionCurrentIndex.SetValue(handler, nextIndex);

                            var portrait = cList[(int)CharacterSelectionCurrentIndex.GetValue(handler)];
                            HoverCharacterPortrait.Invoke(__instance, new object[] { portrait });
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }
                        else if (pInput.Up.WasPressedThisFrame())
                        {
                            int nextRow = currentRow - 1;
                            if (nextRow < 0) nextRow = rowCount-1;
                            bool evenDifferences = (columnsInRows[currentRow] % 2) != (columnsInRows[nextRow] % 2);
                            int awayFromCenter = -(rowStartIndex[currentRow] + columnsInRows[currentRow] / 2 - (int)CharacterSelectionCurrentIndex.GetValue(handler));
                            if (evenDifferences)
                            {
                                if (columnsInRows[currentRow] % 2 == 0)
                                    awayFromCenter++;
                                else
                                    awayFromCenter--;
                            }

                            int nextIndex = Mathf.Clamp(
                                rowStartIndex[nextRow] + columnsInRows[nextRow] / 2 + awayFromCenter,
                                rowStartIndex[nextRow],
                                rowStartIndex[nextRow] + columnsInRows[nextRow] - 1
                            );
                            CharacterSelectionCurrentIndex.SetValue(handler, nextIndex);

                            var portrait = cList[(int)CharacterSelectionCurrentIndex.GetValue(handler)];
                            HoverCharacterPortrait.Invoke(__instance, new object[] { portrait });
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }

                        // Listen to Submit input to select the character.
                        if (pInput.Submit.WasPressedThisFrame())
                        {
                            var portrait = cList[(int)CharacterSelectionCurrentIndex.GetValue(handler)];
                            if (portrait.IsRandom)
                            {
                                StandaloneTransformation_IsEnabled.SetValue(__instance, false);
                                SelectCharacter.Invoke(__instance, new object[] { CSScript.GetRandomCharacter().Data });
                                __instance.StandaloneTransformation_Marker.gameObject.SetActive(false);
                            }
                            else if (portrait.Data != null)
                            {
                                StandaloneTransformation_IsEnabled.SetValue(__instance, false);
                                SelectCharacter.Invoke(__instance, new object[] { portrait.Data });
                                __instance.StandaloneTransformation_Marker.gameObject.SetActive(false);
                            }
                            else
                            {
                                LogHelper.LogError("Submitted but no valid option available...");
                            }
                            FollowPlayerEventSystem.SetValue(handler.UI_PlayerCursor, true);
                            MoveToPosition.Invoke(handler.UI_PlayerCursor, new object[] { __instance.rectTransform });
                            playerInput.EventSystem.playerRoot = __instance.gameObject;
                            if (IsCPU)
                                playerInput.EventSystem.SetSelectedGameObject(__instance.Button_Okay.gameObject);
                            else
                                playerInput.EventSystem.SetSelectedGameObject(__instance.Dropdown_Profile.gameObject);
                        }
                        // Listen to Cancel input to deactivate the UI again.
                        else if (pInput.Cancel.WasPressedThisFrame())
                        {
                            CSScript.RemoveParticipantUI(ParticipantUI_CurrentlySelected);
                            SetState_HoveringLastActionButton.Invoke(handler, null);
                            __instance.StandaloneTransformation_Marker.gameObject.SetActive(false);
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }
                    }
                    else
                    {
                        // Listen to deselect character.
                        if (pInput.Submit.WasPressedThisFrame())
                        {
                            BeginCharacterSelection.Invoke(__instance, null);
                            __instance.StandaloneTransformation_Marker.gameObject.SetActive(false);
                            SoundCache.ins.PlaySound(SoundCache.ins.Menu_Navigate);
                        }
                    }
                }

                return false;
            }
        }

        [HarmonyPatch(typeof(UI_ParticipantHUD_OneVersusOne), "RefreshCharacterNameAndPortrait", new Type[] { typeof(BattleParticipantDataModel) })]
        private static class Portrait1v1_Patch
        {
            private static void Postfix(UI_ParticipantHUD_OneVersusOne __instance, BattleParticipantDataModel particpant)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != particpant.InitialCharacterData) continue;
                    __instance.CharacterPortraitAnimator.enabled = false;
                    Transform t = __instance.gameObject.transform.Find("TopStatusContainer").Find("PortraitContainer").Find("Mask").Find("Image");
                    Image img = t.GetComponent<Image>();
                    if (img != null)
                    {
                        t.localPosition = Vector3.zero;
                        img.sprite = cc.battlePortrait;
                    }
                    return;
                }
            }
        }

        [HarmonyPatch(typeof(UI_ParticipantHUD_Small), "RefreshCharacterNameAndPortrait")]
        private static class PortraitSmall_Patch
        {
            private static void Postfix(UI_ParticipantHUD_Small __instance)
            {
                BattleParticipantDataModel TargetParticipant =
                    (BattleParticipantDataModel)__instance.GetType().GetField("TargetParticipant", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(__instance);

                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != TargetParticipant.InitialCharacterData) continue;
                    __instance.CharacterPortraitAnimator.enabled = false;
                    Transform t = __instance.gameObject.transform.Find("Portrait").Find("Mask").Find("Image");
                    Image img = t.GetComponent<Image>();
                    if (img != null)
                    {
                        t.localPosition = Vector3.zero;
                        img.sprite = cc.battlePortrait;
                    }
                    return;
                }
            }
        }

        [HarmonyPatch(typeof(UI_BattleResultsParticpant), "Setup", new Type[] { typeof(List<EndOfMatchDataStore>), typeof(BattleParticipantDataModel) })]
        private static class ResultsSetupPatch
        {
            private static void Prefix(UI_BattleResultsParticpant __instance, List<EndOfMatchDataStore> endOfMatchDataList, BattleParticipantDataModel participant)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData != participant.InitialCharacterData) continue;
                    __instance.Animator_CharacterImage.enabled = false;
                    GameObject imageObj = __instance.gameObject.transform.Find("Image_Character").gameObject;
                    CustomAnimator anim = imageObj.AddComponent<CustomAnimator>();
                    anim.IgnoreColorAction = true;
                    anim.SetAnimList(cc.rootCharacter.animations, imageObj, cc.resultsOffset, cc.resultsScale);
                    return;
                }
            }
        }

        [HarmonyPatch(typeof(Animator), "Play", new Type[] { typeof(string) })]
        private static class PlayPatch
        {
            private static bool Prefix(Animator __instance, string stateName)
            {
                // surely there's a more performant way of doing this...
                CustomAnimator c = __instance.gameObject.GetComponent<CustomAnimator>();
                if (!c) { return true; }
                if (!c.Play(stateName))
                {
                    c.Stop();
                    return true;
                }
                return false;
            }
        }

        [HarmonyPatch(typeof(Animator), "Play", new Type[] { typeof(int) })]
        private static class PlayHashPatch
        {
            private static bool Prefix(Animator __instance, int stateNameHash)
            {
                // surely there's a more performant way of doing this...
                CustomAnimator c = __instance.gameObject.GetComponent<CustomAnimator>();
                if (!c) { return true; }
                /*
                if (!c.Play(stateNameHash))
                {
                    c.Stop();
                    return true;
                }
                */
                c.Play(stateNameHash);
                return false;
            }
        }

        [HarmonyPatch(typeof(Animator), "Play", new Type[] { typeof(int), typeof(int) })]
        private static class PlayHashLayerPatch
        {
            private static bool Prefix(Animator __instance, int stateNameHash, int layer)
            {
                // surely there's a more performant way of doing this...
                CustomAnimator c = __instance.gameObject.GetComponent<CustomAnimator>();
                if (!c) { return true; }
                if (!c.Play(stateNameHash))
                {
                    c.Stop();
                    return true;
                }
                return false;
            }
        }
    }
}