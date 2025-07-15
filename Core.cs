using MelonLoader;
using SMBZG;
using SMBZG.CharacterSelect;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
using HarmonyLib;
using System.Collections.Generic;

[assembly: MelonInfo(typeof(CharLoader.Core), "CharLoader", "1.0.1", "Headshotnoby/headshot2017", null)]
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

        public override void OnLateInitializeMelon()
        {
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

        void SetupCharSelectArcade()
        {
            // Add character portraits
            Transform PortraitTable = GameObject.Find("CharacterSelect").transform.Find("CharacterSelectPortraitTable");

            foreach (CustomCharacter cc in customCharacters)
            {
                GameObject PortraitGameObj = GameObject.Instantiate(PortraitTable.GetChild(0).gameObject, PortraitTable);
                CharacterPortrait Portrait = PortraitGameObj.GetComponent<CharacterPortrait>();
                Image PortraitImg = PortraitGameObj.GetComponent<Image>();
                PortraitGameObj.name = $"Character_{cc.internalName}";
                Portrait.Data = cc.characterData;
                Portrait.DataDash = null;
                Portrait.DataJump = null;
                Portrait.DataTaunt = null;
                Portrait.DataPursue = null;
                Portrait.DataZAttack = null;
                PortraitImg.sprite = cc.portrait;
                CharacterSelectAcradeScript.ins.CharacterPortraitList.Add(Portrait);
            }

            // Setup additional UIs

            // Part 1: GameObjects
            Transform root = GameObject.Find("Canvas").transform.Find("CharacterSelect").Find("VBox_Settings");

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
            BattleCustomCharsToggle.onValueChanged.RemoveAllListeners();
            BattleCustomCharsToggle.isOn = ArcadeModeLineup.Value;
            BattleCustomCharsToggle.onValueChanged.AddListener(OnCustomCharsToggle);
        }

        void SetupCharSelectVersus()
        {
            // Add character portraits
            Transform PortraitTable = CharacterSelectScript.ins.Section_CharacterSelect.transform.Find("CharacterSelectPortraitTable");

            foreach (CustomCharacter cc in customCharacters)
            {
                GameObject PortraitGameObj = GameObject.Instantiate(PortraitTable.GetChild(0).gameObject, PortraitTable);
                CharacterPortrait Portrait = PortraitGameObj.GetComponent<CharacterPortrait>();
                Image PortraitImg = PortraitGameObj.GetComponent<Image>();
                PortraitGameObj.name = $"Character_{cc.internalName}";
                Portrait.Data = cc.characterData;
                Portrait.DataDash = null;
                Portrait.DataJump = null;
                Portrait.DataTaunt = null;
                Portrait.DataPursue = null;
                Portrait.DataZAttack = null;
                PortraitImg.sprite = cc.portrait;
                CharacterSelectScript.ins.CharacterPortraitList.Add(Portrait);
            }
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