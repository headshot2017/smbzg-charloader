using MelonLoader;
using SMBZG;
using SMBZG.CharacterSelect;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
using HarmonyLib;

[assembly: MelonInfo(typeof(CharLoader.Core), "CharLoader", "1.8.1", "Headshotnoby/headshot2017", null)]
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
        public static List<CharacterData_SO> ArcadeModeLineup;
        public static List<CharacterData_SO> ArcadeModeLineupDisabled;
        public static List<CharacterData_SO> ArcadeModeLineupDefault;
        public static List<CharacterData_SO> ArcadeModeLineupDisabledDefault;
        public static int LineupSelectedOn;
        public static int LineupSelectedOff;

        public string LastErrorMsg;
        public float BoxColorTimer;
        public float BoxShowTimer;
        public bool SetupLineup;


        public override void OnInitializeMelon()
        {
            Preferences_General = MelonPreferences.CreateCategory("General");
            Preferences_General.SetFilePath("UserData/CharLoader.cfg");

            LoggerInstance.Msg("Initialized.");
        }

        public override void OnLateInitializeMelon()
        {
            Application.logMessageReceived += LogHandler;

            ArcadeModeLineupDefault = [.. BattleCache.ins.GetAcradeModeCharacterLineup()];
            ArcadeModeLineupDisabledDefault = new List<CharacterData_SO>();
            foreach (CustomCharacter cc in customCharacters)
                ArcadeModeLineupDisabledDefault.Add(cc.characterData);

            // there are custom character "mods" that are made through modification of the game's source code,
            // such as Plot Boi's character mods (Kirby, Super Sonic, Goku...)
            // this code will look for them in the BattleCache and add them to the list
            //
            // unfortunately this also adds standalone transformations, but there's nothing i can do about it
            foreach (BattleCache.CharacterEnum character in Enum.GetValues(typeof(BattleCache.CharacterEnum)))
            {
                CharacterData_SO charData = BattleCache.ins.Character_GetData(character);
                if (!charData || ArcadeModeLineupDefault.Contains(charData) || ArcadeModeLineupDisabledDefault.Contains(charData))
                    continue;

                ArcadeModeLineupDisabledDefault.Add(charData);
            }

            ResetArcadeLineup();

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

        void LogHandler(string message, string stacktrace, LogType type)
        {
            if (type != LogType.Exception && type != LogType.Error)
                return;

            string msg = $"{message}\n{stacktrace}";

            LoggerInstance.Msg(msg);
            ShowError(msg);
        }

        public void ShowError(string msg)
        {
            LastErrorMsg = msg;
            BoxColorTimer = 1f;
            BoxShowTimer = 5f;
        }

        public override void OnGUI()
        {
            if (BoxShowTimer > 0)
            {
                Vector2 size = GUI.skin.textField.CalcSize(new GUIContent(LastErrorMsg));

                int x = 32;
                int y = 32;
                int w = Screen.width / 2 - x;
                int h = (int)size.y;
                Color oldColor = GUI.contentColor;

                GUI.BeginGroup(new Rect(x, y, w, h+40));
                GUI.contentColor = new Color(1, 1-BoxColorTimer, 1-BoxColorTimer);
                GUI.Box(new Rect(0, 0, w, h+40), "Exception");
                GUI.contentColor = oldColor;
                GUI.Label(new Rect(8, 16, w - 16, h+32), LastErrorMsg);
                GUI.EndGroup();
            }

            if (SetupLineup)
            {
                Vector2 size1 = GUI.skin.textField.CalcSize(new GUIContent("Enabled"));
                Vector2 size2 = GUI.skin.textField.CalcSize(new GUIContent("Disabled"));

                int x = Screen.width / 8;
                int y = Screen.height / 12;
                int w = Screen.width - (x*2);
                int h = Screen.height - (y*2);
                List<string> enabled = new List<string>();
                List<string> disabled = new List<string>();
                foreach (var character in ArcadeModeLineup)
                    enabled.Add(BattleCache.Character_GetDisplayName(character.Character));
                foreach (var character in ArcadeModeLineupDisabled)
                    disabled.Add(BattleCache.Character_GetDisplayName(character.Character));

                GUI.BeginGroup(new Rect(x, y, w, h));
                GUI.Box(new Rect(0, 0, w, h), "Arcade Mode Lineup");

                GUI.Label(new Rect(8 + (w / 2 - 40)/2 - (size1.x / 2), 48-24, size1.x, size1.y), "Enabled");
                int selection = GUI.SelectionGrid(new Rect(8, 48, w / 2 - 40, h - 144), LineupSelectedOn, enabled.ToArray(), 1);
                if (selection >= 0) LineupSelectedOn = selection;
                if (LineupSelectedOn >= 0)
                {
                    if (LineupSelectedOn > 0 && GUI.Button(new Rect(8 + (w / 2 - 40) / 2 - 48 - (96+16), 48 + h - 144 + 8, 96, 32), "Move up"))
                    {
                        var moving = ArcadeModeLineup[LineupSelectedOn];
                        ArcadeModeLineup.Remove(moving);
                        ArcadeModeLineup.Insert(LineupSelectedOn-1, moving);
                        LineupSelectedOn--;
                    }
                    if (GUI.Button(new Rect(8 + (w / 2 - 40) / 2 - 48, 48 + h - 144 + 8, 96, 32), "Remove"))
                    {
                        var removing = ArcadeModeLineup[LineupSelectedOn];
                        ArcadeModeLineup.Remove(removing);
                        ArcadeModeLineupDisabled.Add(removing);
                        while (LineupSelectedOn >= ArcadeModeLineup.Count) LineupSelectedOn--;
                    }
                    if (LineupSelectedOn < ArcadeModeLineup.Count-1 && GUI.Button(new Rect(8 + (w / 2 - 40) / 2 - 48 + (96+16), 48 + h - 144 + 8, 96, 32), "Move down"))
                    {
                        var moving = ArcadeModeLineup[LineupSelectedOn];
                        ArcadeModeLineup.Remove(moving);
                        ArcadeModeLineup.Insert(LineupSelectedOn+1, moving);
                        LineupSelectedOn++;
                    }
                }

                GUI.Label(new Rect((w - (w / 2 - 40) - 8) + (w / 2 - 40) / 2 - (size2.x/2), 48-24, size2.x, size2.y), "Disabled");
                selection = GUI.SelectionGrid(new Rect(w - (w / 2 - 40) - 8, 48, w / 2 - 40, h - 144), LineupSelectedOff, disabled.ToArray(), 1);
                if (selection >= 0) LineupSelectedOff = selection;
                if (LineupSelectedOff >= 0 && GUI.Button(new Rect((w - (w / 2 - 40) - 8) + (w / 2 - 40) / 2 - 48, 48 + h - 144 + 8, 96, 32), "Add"))
                {
                    var adding = ArcadeModeLineupDisabled[LineupSelectedOff];
                    ArcadeModeLineupDisabled.Remove(adding);
                    ArcadeModeLineup.Add(adding);
                    while (LineupSelectedOff >= ArcadeModeLineupDisabled.Count) LineupSelectedOff--;
                }

                if (GUI.Button(new Rect(w/2 - 48, 48 + h - 144 + 8, 96, 32), "Reset"))
                {
                    ResetArcadeLineup();
                }

                if (GUI.Button(new Rect(8, h-48, w-16, 32), "Close"))
                    ShowLineupCustomizer(false);

                GUI.EndGroup();
            }
        }

        public override void OnSceneWasInitialized(int buildIndex, string sceneName)
        {
            if (buildIndex == 7)
                SetupCharSelectVersus();
            if (buildIndex == 8)
                SetupCharSelectArcade();
        }

        public override void OnUpdate()
        {
            if (BoxColorTimer > 0)
            {
                BoxColorTimer -= Time.deltaTime;
                if (BoxColorTimer <= 0) BoxColorTimer = 0;
            }
            BoxShowTimer -= Time.deltaTime;
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
            PortraitNewRow.transform.localPosition = PortraitRow.localPosition + new Vector3(0, PortraitTableRoot.GetChild(1).localPosition.y - PortraitTableRoot.GetChild(0).localPosition.y);

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

            Sprite uisprite = null;
            Sprite[] sprites = Resources.FindObjectsOfTypeAll<Sprite>();
            foreach (Sprite sprite in sprites)
            {
                if (sprite.name == "UISprite")
                    uisprite = sprite;
            }

            TMPro.TMP_FontAsset fnt = null;
            TMPro.TMP_FontAsset[] fonts = Resources.FindObjectsOfTypeAll<TMPro.TMP_FontAsset>();
            foreach (TMPro.TMP_FontAsset font in fonts)
            {
                if (font.name == "LiberationSans SDF")
                {
                    fnt = font;
                    break;
                }
            }

            // Part 1: GameObjects
            Transform AcradeSettings = CharacterSelectAcradeScript.ins.Page_ArcadeSettings.transform;
            Transform root = AcradeSettings.Find("VBox_Settings");

            GameObject BattleCustomCharsObj = GameObject.Instantiate(root.Find("ArcadeToggles").Find("BattleRandomSkins").gameObject, root);
            BattleCustomCharsObj.transform.RemoveAllChildren();
            GameObject BattleCustomCharsLabelObj = new GameObject("Label");

            BattleCustomCharsLabelObj.transform.SetParent(BattleCustomCharsObj.transform, false);
            BattleCustomCharsObj.name = "BattleCustomChars";


            // Part 2: Components
            BattleCustomCharsObj.GetComponent<HorizontalLayoutGroup>().childForceExpandWidth = true;
            Image img = BattleCustomCharsObj.AddComponent<Image>();
            TMPro.TextMeshProUGUI text = BattleCustomCharsLabelObj.AddComponent<TMPro.TextMeshProUGUI>();
            Button btn = BattleCustomCharsObj.AddComponent<Button>();

            img.sprite = uisprite;
            img.type = Image.Type.Sliced;
            btn.image = img;
            text.text = "Customize lineup";
            text.color = Color.black;
            text.fontSize = 24;
            text.fontStyle = TMPro.FontStyles.Normal;
            text.horizontalAlignment = TMPro.HorizontalAlignmentOptions.Center;
            text.font = fnt;

            //btn.onClick.RemoveAllListeners();
            btn.onClick.AddListener(OnCustomizeLineupClicked);

            BattleCustomCharsLabelObj.transform.localPosition = new Vector3(0, -8, 0);

            // put Customize button above Default Settings and Back buttons
            BattleCustomCharsObj.transform.SetSiblingIndex(BattleCustomCharsObj.transform.GetSiblingIndex() - 2);

            // disable the Semi Super Mecha Sonic checkbox?
            // but if this is disabled and players do not have the unlockable character,
            // they can never earn it...
            /*
            Toggle SemiSuperToggle = root.Find("SemiSuperToggle").Find("Toggle_SemiSuperToggle").GetComponent<Toggle>();
            SemiSuperToggle.interactable = false;
            */
        }

        void SetupCharSelectVersus()
        {
            Transform PortraitTableRoot = CharacterSelectScript.ins.Section_CharacterSelect.transform.Find("CharacterSelectPortraitTable");
            SetupPortraits(PortraitTableRoot, CharacterSelectScript.ins);
        }

        void OnCustomizeLineupClicked()
        {
            ShowLineupCustomizer(true);
        }

        void ShowLineupCustomizer(bool on)
        {
            GameObject root = GameObject.Find("Canvas").transform.Find("AcradeSettings").gameObject;
            root.SetActive(!on);
            SetupLineup = on;
            LineupSelectedOn = LineupSelectedOff = -1;

            // when clicking the Customize Lineup button, this puts it in the unity UI input module component,
            // so when you press D to, for example, add a character to the battle, it also triggers the Customize Lineup button from earlier.
            // this code will remove this button from any ZIG_PlayerInput(s) so that the D key can be pressed safely.
            foreach (ZIG_PlayerInput i in GameObject.FindObjectsOfType<ZIG_PlayerInput>())
            {
                var module = i.EventSystem;
                if (!module)
                    continue;

                module.SetSelectedGameObject(null);
            }
        }

        public void ResetArcadeLineup()
        {
            ArcadeModeLineup = [.. ArcadeModeLineupDefault];
            ArcadeModeLineupDisabled = [.. ArcadeModeLineupDisabledDefault];
        }

        [HarmonyPatch(typeof(CharacterSelectAcradeScript), "OnSubmit")]
        private static class ArcadeSubmitPatch
        {
            private static bool Prefix(CharacterSelectAcradeScript __instance)
            {
                List<CharacterSelectPlayerInputHandler_Base> ActiveCharacterSelectPlayerInputHandlerList =
                    (List<CharacterSelectPlayerInputHandler_Base>)__instance.GetType().GetField("ActiveCharacterSelectPlayerInputHandlerList", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(__instance);

                bool flag = true;
                foreach (CharacterSelectArcadePlayerInputHandler activeCharacterSelectPlayerInputHandler in ActiveCharacterSelectPlayerInputHandlerList)
                {
                    int CurrentState = (int)activeCharacterSelectPlayerInputHandler.GetType().GetProperty("CurrentState", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(activeCharacterSelectPlayerInputHandler);
                    UI_Participant ParticipantUI_MyPrimary = (UI_Participant)activeCharacterSelectPlayerInputHandler.GetType().GetProperty("ParticipantUI_MyPrimary", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(activeCharacterSelectPlayerInputHandler);

                    int HoveringGoNext = (int)activeCharacterSelectPlayerInputHandler.GetType().GetNestedType("StateENUM", BindingFlags.NonPublic).GetField("HoveringGoNext").GetValue(activeCharacterSelectPlayerInputHandler);

                    if (CurrentState != HoveringGoNext && ParticipantUI_MyPrimary != null)
                    {
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

                SaveData.Data.LastUsedArcadeCpuHealth = __instance.Input_BattleHealthV2.Value ?? 150f;
                __instance.GetType().GetMethod("OnMovementRushPlayerHealthCHange", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(__instance, [__instance.Input_MovementRushPlayerHealth.Value.ToString()]);

                List<CharacterData_SO> array = new List<CharacterData_SO>();
                foreach (var cc in ArcadeModeLineup)
                    array.Add(cc);

                BattleSettings battleSettings = new BattleSettings();
                List<BattleSettings> list = new List<BattleSettings>();
                foreach (CharacterData_SO characterData_SO in array)
                {
                    BattleSettings battleSettings2 = new BattleSettings
                    {
                        RoundsToWin = 1,
                        Stage = BattleCache.GetRandomStage(),
                        TeamsList = new List<BattleSettings.TeamDataModel>(),
                        DefaultParticipantHealth = SaveData.Data.LastUsedArcadeCpuHealth,
                        ActiveEnergyGainMultiplier = __instance.Input_BattleActiveEnergyGainMultiplier.Value ?? battleSettings.ActiveEnergyGainMultiplier,
                        IntensityMultipier = __instance.Input_BattleIntensityMultiplier.Value ?? battleSettings.IntensityMultipier,
                        PassiveEnergyGainMultiplier = __instance.Input_BattlePassiveEnergyGainMultiplier.Value ?? battleSettings.IntensityMultipier,
                        StunMultiplier = __instance.Input_BattleStunMultiplier.Value ?? battleSettings.StunMultiplier,
                        DefaultDamageMulitplier = __instance.Input_BattleDamageMultiplier.Value ?? battleSettings.DefaultDamageMulitplier
                    };
                    BattleSettings.TeamDataModel teamDataModel = new BattleSettings.TeamDataModel(BattleCache.teamTags[1])
                    {
                        ParticipantSettingList = new List<BattleParticipantSettings>()
                    };
                    UI_Participant[] array2 = UnityEngine.Object.FindObjectsOfType<UI_Participant>(includeInactive: true);
                    teamDataModel.TeamTag = (string)typeof(UI_Participant).GetField("TeamTag", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(array2.Last());
                    battleSettings2.TeamsList.Add(teamDataModel);
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
                            HealthMax = (uI_Participant.Toggle_Health.isOn ? uI_Participant.Input_Health.value : battleSettings2.DefaultParticipantHealth),
                            InputDelay = (int)uI_Participant.Input_Delay.value,
                            DamageMultiplierOverride = (uI_Participant.Toggle_DamageMultiplier.isOn ? uI_Participant.Input_DamageMultiplier.value : battleSettings2.DefaultDamageMulitplier),
                            ActiveEnergyGainMultiplierOverride = (uI_Participant.Toggle_ActiveEnergyGainMultiplier.isOn ? uI_Participant.Input_ActiveEnergyGainMultiplier.value : battleSettings2.ActiveEnergyGainMultiplier),
                            PassiveEnergyGainMultiplierOverride = (uI_Participant.Toggle_PassiveEnergyGainMultiplier.isOn ? uI_Participant.Input_PassiveEnergyGainMultiplier.value : battleSettings2.PassiveEnergyGainMultiplier),
                            StunMultiplierOverride = (uI_Participant.Toggle_StunMultiplier.isOn ? uI_Participant.Input_StunMultiplier.value : battleSettings2.StunMultiplier),
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

                    string text = BattleCache.teamTags[2];
                    if (teamDataModel.TeamTag == text)
                    {
                        text = BattleCache.teamTags[1];
                    }

                    List<BattleCache.CPUSettingsENUM> CPUSettingList = (List<BattleCache.CPUSettingsENUM>)__instance.GetType().GetField("CPUSettingList", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(__instance);
                    battleSettings2.TeamsList.Add(new BattleSettings.TeamDataModel(text)
                    {
                        ParticipantSettingList = new List<BattleParticipantSettings>
                        {
                            new BattleParticipantSettings(null, text, characterData_SO, CPUSettingList[__instance.Difficulty_CPUSetting.value], SaveData.Data.LastUsedArcadeCpuHealth, string.Empty, 0, null)
                            {
                                ParticipantIndex = array2.Select((UI_Participant p) => (int)p.GetType().GetField("ParticipantIndex", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(p)).DefaultIfEmpty(1).Max() + 100,
                                DamageMultiplierOverride = battleSettings2.DefaultDamageMulitplier
                            }
                        }
                    });
                    if (SaveData.Data.ArcadeRandomSkinsEnabled)
                    {
                        foreach (BattleParticipantSettings participantSetting in battleSettings2.TeamsList[1].ParticipantSettingList)
                        {
                            CharacterSkinDataStore.Skin random = CharacterSkinManager.ins.GetCharacterSkinData(characterData_SO.Character).SkinList.GetRandom();
                            participantSetting.SkinName = random.Name;
                        }
                    }
                    else if (SaveData.Data.Get_MainMenuScenaryMode() == SceneConstants.MainMenuScenaryModeENUM.Halloween2022)
                    {
                        foreach (BattleParticipantSettings participantSetting2 in battleSettings2.TeamsList[1].ParticipantSettingList)
                        {
                            participantSetting2.SkinName = "Halloween";
                        }
                    }

                    list.Add(battleSettings2);
                }

                // find goomba and reduce its' health
                BattleSettings setting = null;
                try
                {
                    setting = list.First((BattleSettings r) => r.TeamsList[1].ParticipantSettingList[0].CharacterData.Character == BattleCache.CharacterEnum.Goomba);
                }
                catch(InvalidOperationException)
                {
                    // if goomba is missing
                }
                if (setting != null)
                {
                    BattleParticipantSettings battleParticipantSettings = setting.TeamsList[1].ParticipantSettingList[0];
                    battleParticipantSettings.HealthMax = Mathf.Round(battleParticipantSettings.HealthMax * 0.6666666f);
                    if (battleParticipantSettings.HealthMax < 0f)
                    {
                        battleParticipantSettings.HealthMax = 1f;
                    }
                }

                // increase final boss health
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
            private static bool Prefix(ref GameObject __result, BattleCache.CharacterEnum character)
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

        [HarmonyPatch(typeof(BattleCache), "Character_GetData", new Type[] { typeof(BattleCache.CharacterEnum) })]
        private static class GetDataPatch
        {
            private static bool Prefix(ref CharacterData_SO __result, BattleCache.CharacterEnum character)
            {
                foreach (CustomCharacter cc in customCharacters)
                {
                    if (cc.characterData.Character != character) continue;
                    __result = cc.characterData;
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
                    c.SetAnimList(cc.rootCharacter.animations, imageObj.transform.Find("Image").gameObject, cc.charSelectOffset, cc.charSelectScale);
                    c.Play(Animator.StringToHash("IdleCharSelect"), true);

                    __instance.SelectedCharacterDisplay.gameObject.GetComponentInChildren<Image>().color = new Color(1f, 1f, 1f, 0.5f);
                    __instance.Label_SelectedCharacter.color = new Color(1f, 1f, 1f, 0.5f);
                    __instance.Label_SelectedCharacter.text = BattleCache.Character_GetDisplayName(characterData.Character);
                    __instance.CharacterPlatform.Play(characterData.Platform.ToString());

                    return false;
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
                    c.SetAnimList(cc.rootCharacter.animations, imageObj.transform.Find("Image").gameObject, cc.charSelectOffset, cc.charSelectScale);
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