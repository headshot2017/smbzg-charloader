using UnityEngine;
using System.Collections;
using UnityEngine.Networking;
using MelonLoader;
using TinyJSON;
using System.Reflection;
using System;
using static System.Collections.Specialized.BitVector32;

public class CharLoaderComponent : MonoBehaviour
{
    public Texture2D texture;

    string CurrCharacterLoading;

    void Start()
    {
        StartCoroutine(Load());
    }

    IEnumerator Load()
    {
        if (!Directory.Exists($"{Application.streamingAssetsPath}/CustomChars"))
            Directory.CreateDirectory($"{Application.streamingAssetsPath}/CustomChars");

        string[] chars = Directory.GetDirectories($"{Application.streamingAssetsPath}/CustomChars");
        foreach (string _charName in chars)
        {
            string path = _charName.Replace('\\', '/');
            string charName = Path.GetFileName(path);

            ProxyObject json = JSON.Load(File.ReadAllText($"{path}/character.json")) as ProxyObject;
            CustomCharacter cc = new CustomCharacter();

            ProxyObject general = json["general"] as ProxyObject;

            CurrCharacterLoading = charName;
            cc.internalName = charName;
            cc.charSelectScale = general["scale"]["charSelect"];
            cc.resultsScale = general["scale"]["results"];
            cc.charSelectOffset = new Vector2(general["offset"]["charSelect"][0], general["offset"]["charSelect"][1]);
            cc.resultsOffset = new Vector2(general["offset"]["results"][0], general["offset"]["results"][1]);

            cc.rootCharacter = new CharacterCompanion();
            cc.rootCharacter.name = general["displayName"];
            cc.rootCharacter.scale = general["scale"]["ingame"];
            cc.rootCharacter.offset = new Vector2(general["offset"]["ingame"][0], general["offset"]["ingame"][1]);

            FilterMode[] filterModes = new FilterMode[]
            {
                FilterMode.Point,
                FilterMode.Bilinear,
                FilterMode.Trilinear,
            };

            yield return TextureDownload($"{path}/sheet.png");
            texture.filterMode = (general.Keys.Contains("sheetFilter")) ? filterModes[general["sheetFilter"]] : FilterMode.Point;
            cc.rootCharacter.sheet = texture;

            yield return TextureDownload($"{path}/portrait.png");
            cc.portrait = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, 0), 50);

            yield return TextureDownload($"{path}/battleportrait.png");
            texture.filterMode = (general.Keys.Contains("battlePortraitFilter")) ? filterModes[general["battlePortraitFilter"]] : FilterMode.Point;
            cc.battlePortrait = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, .5f), 50);

            cc.sounds = new Dictionary<string, AudioClip>();
            if (Directory.Exists($"{path}/sounds"))
            {
                foreach (string _soundName in Directory.GetFiles($"{path}/sounds"))
                {
                    string soundPath = _soundName.Replace('\\', '/');
                    string soundName = Path.GetFileNameWithoutExtension(soundPath);
                    UnityWebRequest www = null;
                    if (File.Exists($"{path}/sounds/{soundName}.wav"))
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/sounds/{soundName}.wav", AudioType.WAV);
                    else if (File.Exists($"{path}/sounds/{soundName}.ogg"))
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/sounds/{soundName}.ogg", AudioType.OGGVORBIS);
                    else if (File.Exists($"{path}/sounds/{soundName}.mp3"))
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/sounds/{soundName}.mp3", AudioType.MPEG);

                    if (www != null)
                    {
                        www.SendWebRequest();
                        while (!www.isDone) ;

                        cc.sounds[soundName] = DownloadHandlerAudioClip.GetContent(www);
                    }
                }
            }

            cc.music = new Dictionary<string, AudioClip>();
            if (Directory.Exists($"{path}/music"))
            {
                foreach (string _musicName in Directory.GetFiles($"{path}/music"))
                {
                    string musicPath = _musicName.Replace('\\', '/');
                    string musicName = Path.GetFileNameWithoutExtension(musicPath);
                    Melon<CharLoader.Core>.Logger.Msg($"Load music {musicName}");

                    UnityWebRequest www = null;
                    DownloadHandlerAudioClip handler = null;

                    if (File.Exists($"{path}/music/{musicName}.wav"))
                    {
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/music/{musicName}.wav", AudioType.WAV);
                        handler = new DownloadHandlerAudioClip(string.Empty, AudioType.WAV);
                    }
                    else if (File.Exists($"{path}/music/{musicName}.ogg"))
                    {
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/music/{musicName}.ogg", AudioType.OGGVORBIS);
                        handler = new DownloadHandlerAudioClip(string.Empty, AudioType.OGGVORBIS);
                    }
                    else if (File.Exists($"{path}/music/{musicName}.mp3"))
                    {
                        www = UnityWebRequestMultimedia.GetAudioClip($"file:///{path}/music/{musicName}.mp3", AudioType.MPEG);
                        handler = new DownloadHandlerAudioClip(string.Empty, AudioType.MPEG);
                    }

                    if (www != null)
                    {
                        handler.streamAudio = true;
                        www.downloadHandler = handler;
                        www.SendWebRequest();
                        yield return www;
                        cc.music[musicName] = handler.audioClip;
                    }
                }
            }

            CustomCharacterData_SO Data = ScriptableObject.CreateInstance<CustomCharacterData_SO>();
            Data.Prefab_SpecialCharacterSettingsUI = BattleCache.ins.CharacterData_Sonic.Prefab_SpecialCharacterSettingsUI;
            Data.Character = (BattleCache.CharacterEnum)(1000 + CharLoader.Core.customCharacters.Count);
            Data.name = $"[CharacterData] {cc.internalName}";
            Data.DittoHue = BattleCache.ins.CharacterData_Mario.DittoHue;
            Data.DittoSaturation = BattleCache.ins.CharacterData_Mario.DittoSaturation;
            Data.DittoContrast = BattleCache.ins.CharacterData_Mario.DittoContrast;

            if (general.Keys.Contains("colors"))
            {
                ProxyObject colors = general["colors"] as ProxyObject;
                if (colors.Keys.Contains("primary"))
                    Data.PrimaryColor = new Color(
                        colors["primary"][0] / 255f,
                        colors["primary"][1] / 255f,
                        colors["primary"][2] / 255f
                    );
                if (colors.Keys.Contains("secondary"))
                    Data.SecondaryColor = new Color(
                        colors["secondary"][0] / 255f,
                        colors["secondary"][1] / 255f,
                        colors["secondary"][2] / 255f
                    );

                if (colors.Keys.Contains("alternateColors"))
                {
                    Data.DittoHue = colors["alternateColors"][0];
                    Data.DittoSaturation = colors["alternateColors"][1];
                    Data.DittoContrast = colors["alternateColors"][2];
                }
            }

            if (general.Keys.Contains("unbalanced"))
                Data.IsUnbalanced = general["unbalanced"];

            if (general.Keys.Contains("platform"))
            {
                int platform = general["platform"];
                Data.Platform = (BattleCache.PlatformEnum)platform;
            }

            cc.characterData = Data;

            GameObject CharPrefab = GameObject.Instantiate(BattleCache.ins.CharacterData_Sonic.Prefab_BattleGameObject);
            CharPrefab.name = cc.internalName;
            CharPrefab.SetActive(false);
            CharPrefab.AddComponent<CustomAnimator>();
            SonicControl old = CharPrefab.GetComponent<SonicControl>();
            CustomBaseCharacter baseChar = CharPrefab.AddComponent<CustomBaseCharacter>();
            baseChar.Comp_Hurtbox = old.Comp_Hurtbox;
            baseChar.CharacterData = cc.characterData;
            GameObject.Destroy(old);
            GameObject.DontDestroyOnLoad(CharPrefab);

            cc.rootCharacter.prefab = CharPrefab;
            Data.Prefab_BattleGameObject = CharPrefab;

            cc.getUpTimer = 0;

            // v1.6: Puppet animation
            SetupPuppets(cc.rootCharacter, json);

            Variant animsRoot = json["anims"];
            cc.rootCharacter.animations = new Dictionary<int, CustomAnimation>();
            foreach (var pair in animsRoot as ProxyObject)
            {
                ProxyObject animObject = pair.Value as ProxyObject;
                CustomAnimation customAnim = new CustomAnimation();

                string name = pair.Key;

                customAnim.actions = new List<AnimAction>();
                customAnim.hash = Animator.StringToHash(name);
                customAnim.loops = animObject.Keys.Contains("loops") ? animObject["loops"] : -1;
                customAnim.interpolate = animObject.Keys.Contains("interpolate") ? animObject["interpolate"] : true;
                if (animObject.Keys.Contains("scale")) customAnim.scale = new Vector2(animObject["scale"][0], animObject["scale"][1]);
                if (animObject.Keys.Contains("offset")) customAnim.offset = new Vector2(animObject["offset"][0], animObject["offset"][1]);
                bool isGetUp = (pair.Key == "GetUp");

                Variant animList = animObject["frames"];
                foreach (ProxyObject actionVar in animList as ProxyArray)
                {
                    AnimAction action = ParseAction(actionVar, cc.rootCharacter.sheet, cc.sounds, cc.rootCharacter.puppets);

                    if (isGetUp)
                        cc.getUpTimer += action.delay;

                    bool hitboxOff = (
                        action.hitbox != null &&
                        !action.hitbox.on &&
                        action.hitbox.pos == Vector2.zero &&
                        action.hitbox.scale == Vector2.zero
                    );

                    if (hitboxOff && customAnim.actions.Count > 0)
                    {
                        AnimAction lastAction = customAnim.actions[customAnim.actions.Count - 1];
                        if (lastAction.hitbox != null)
                        {
                            action.hitbox.pos = lastAction.hitbox.pos;
                            action.hitbox.scale = lastAction.hitbox.scale;
                        }
                    }

                    customAnim.actions.Add(action);
                }

                int alternateHash = Animator.StringToHash($"{Data.Character}_{pair.Key}");

                cc.rootCharacter.animations[customAnim.hash] = customAnim;
                cc.rootCharacter.animations[alternateHash] = customAnim;
            }

            // v1.6: New "PreJump" animation
            if (!cc.rootCharacter.animations.ContainsKey(CustomAnimator.ASN_PreJump) &&
                cc.rootCharacter.animations.ContainsKey(CustomAnimator.ASN_Land) &&
                cc.rootCharacter.animations[CustomAnimator.ASN_Land].actions.Count > 0)
            {
                CustomAnimation customAnim = new CustomAnimation();
                CustomAnimation baseAnim = cc.rootCharacter.animations[CustomAnimator.ASN_Land];

                customAnim.actions = new List<AnimAction>();
                customAnim.hash = CustomAnimator.ASN_PreJump;
                customAnim.loops = -1;
                customAnim.interpolate = true;
                customAnim.scale = baseAnim.scale;
                customAnim.offset = baseAnim.offset;
                customAnim.actions.Add(baseAnim.actions[0]);

                cc.rootCharacter.animations[CustomAnimator.ASN_PreJump] = customAnim;
            }

            // v1.6: New "IdleCharSelect" animation
            if (!cc.rootCharacter.animations.ContainsKey(Animator.StringToHash("IdleCharSelect")) ||
                cc.rootCharacter.animations[Animator.StringToHash("IdleCharSelect")].actions.Count == 0)
            {
                CustomAnimation customAnim = new CustomAnimation();
                CustomAnimation baseAnim = cc.rootCharacter.animations[CustomAnimator.ASN_Idle];

                customAnim.hash = Animator.StringToHash("IdleCharSelect");
                customAnim.loops = -1;
                customAnim.interpolate = true;
                customAnim.scale = baseAnim.scale;
                customAnim.offset = baseAnim.offset;
                customAnim.actions = baseAnim.actions;

                cc.rootCharacter.animations[Animator.StringToHash("IdleCharSelect")] = customAnim;
            }

            Variant effectsRoot = json["effects"];
            cc.effects = new Dictionary<string, CustomEffectEntry>();
            foreach (var pair in effectsRoot as ProxyObject)
            {
                ProxyObject effectObject = pair.Value as ProxyObject;

                CustomEffectEntry customEffect = new CustomEffectEntry();
                yield return TextureDownload($"{path}/effects/{effectObject["texture"]}.png");
                texture.filterMode = effectObject.Keys.Contains("filter") ? filterModes[effectObject["filter"]] : FilterMode.Bilinear;
                customEffect.texture = texture;

                CustomAnimation customAnim = new CustomAnimation();
                customAnim.actions = new List<AnimAction>();
                customAnim.hash = Animator.StringToHash(pair.Key);
                customAnim.loops = 0;
                customAnim.interpolate = effectObject.Keys.Contains("interpolate") ? effectObject["interpolate"] : true;
                if (effectObject.Keys.Contains("scale")) customAnim.scale = new Vector2(effectObject["scale"][0], effectObject["scale"][1]);
                if (effectObject.Keys.Contains("offset")) customAnim.offset = new Vector2(effectObject["offset"][0], effectObject["offset"][1]);

                Variant animList = effectObject["frames"];
                foreach (ProxyObject actionVar in animList as ProxyArray)
                {
                    AnimAction action = ParseAction(actionVar, customEffect.texture, cc.sounds, null);

                    customAnim.actions.Add(action);
                }

                customEffect.anim = customAnim;
                cc.effects[pair.Key] = customEffect;
            }

            cc.companions = new Dictionary<string, CharacterCompanion>();
            if (Directory.Exists($"{path}/companions"))
            {
                string[] companions = Directory.GetDirectories($"{path}/companions");
                foreach (string _companionName in companions)
                {
                    string companionPath = _companionName.Replace('\\', '/');
                    string companionName = Path.GetFileName(companionPath);

                    ProxyObject companionJson = JSON.Load(File.ReadAllText($"{companionPath}/companion.json")) as ProxyObject;
                    ProxyObject companionGeneral = companionJson["general"] as ProxyObject;

                    CharacterCompanion companion = new CharacterCompanion();
                    companion.name = companionName;

                    companion.scale = companionGeneral["scale"];
                    companion.offset = new Vector2(companionGeneral["offset"][0], companionGeneral["offset"][1]);

                    yield return TextureDownload($"{companionPath}/sheet.png");
                    texture.filterMode = (companionGeneral.Keys.Contains("sheetFilter")) ? filterModes[companionGeneral["sheetFilter"]] : FilterMode.Point;
                    companion.sheet = texture;

                    companion.prefab = GameObject.Instantiate(CharPrefab);
                    companion.prefab.name = companionName;
                    companion.prefab.SetActive(false);
                    GameObject.DontDestroyOnLoad(companion.prefab);

                    // v1.6: Puppet animation
                    SetupPuppets(companion, companionJson);

                    companion.animations = new Dictionary<int, CustomAnimation>();
                    Variant cAnimsRoot = companionJson["anims"];
                    foreach (var pair in cAnimsRoot as ProxyObject)
                    {
                        ProxyObject animObject = pair.Value as ProxyObject;
                        CustomAnimation customAnim = new CustomAnimation();

                        string name = pair.Key;

                        customAnim.actions = new List<AnimAction>();
                        customAnim.hash = Animator.StringToHash(name);
                        customAnim.loops = animObject.Keys.Contains("loops") ? animObject["loops"] : -1;
                        customAnim.interpolate = animObject.Keys.Contains("interpolate") ? animObject["interpolate"] : true;
                        if (animObject.Keys.Contains("scale")) customAnim.scale = new Vector2(animObject["scale"][0], animObject["scale"][1]);
                        if (animObject.Keys.Contains("offset")) customAnim.offset = new Vector2(animObject["offset"][0], animObject["offset"][1]);

                        Variant animList = animObject["frames"];
                        foreach (ProxyObject actionVar in animList as ProxyArray)
                        {
                            AnimAction action = ParseAction(actionVar, companion.sheet, cc.sounds, companion.puppets);

                            bool hitboxOff = (
                                action.hitbox != null &&
                                !action.hitbox.on &&
                                action.hitbox.pos == Vector2.zero &&
                                action.hitbox.scale == Vector2.zero
                            );

                            if (hitboxOff && customAnim.actions.Count > 0)
                            {
                                AnimAction lastAction = customAnim.actions[customAnim.actions.Count - 1];
                                if (lastAction.hitbox != null)
                                {
                                    action.hitbox.pos = lastAction.hitbox.pos;
                                    action.hitbox.scale = lastAction.hitbox.scale;
                                }
                            }

                            customAnim.actions.Add(action);
                        }

                        companion.animations[customAnim.hash] = customAnim;
                    }

                    cc.companions[companion.name] = companion;

                    // v1.6: New "PreJump" animation
                    if (!cc.companions[companion.name].animations.ContainsKey(CustomAnimator.ASN_PreJump) &&
                        cc.companions[companion.name].animations.ContainsKey(CustomAnimator.ASN_Land) &&
                        cc.companions[companion.name].animations[CustomAnimator.ASN_Land].actions.Count > 0)
                    {
                        CustomAnimation customAnim = new CustomAnimation();
                        CustomAnimation baseAnim = cc.companions[companion.name].animations[CustomAnimator.ASN_Land];

                        customAnim.actions = new List<AnimAction>();
                        customAnim.hash = CustomAnimator.ASN_PreJump;
                        customAnim.loops = -1;
                        customAnim.interpolate = true;
                        customAnim.scale = baseAnim.scale;
                        customAnim.offset = baseAnim.offset;
                        customAnim.actions.Add(baseAnim.actions[0]);

                        cc.companions[companion.name].animations[CustomAnimator.ASN_PreJump] = customAnim;
                    }
                }
            }

            Variant cmdListRoot = json["commandList"];
            cc.commandList = new CommandListModel();
            cc.commandList.CharacterName = cc.rootCharacter.name;
            foreach (ProxyObject command in cmdListRoot as ProxyArray)
            {
                CommandListRecordModel commandRecord = new CommandListRecordModel();
                commandRecord.Title = command["title"];
                if (command.Keys.Contains("subtitle")) commandRecord.Subtitle = command["subtitle"];
                if (command.Keys.Contains("additionalInfo")) commandRecord.AdditionalInfo = command["additionalInfo"];
                if (command.Keys.Contains("imageList")) commandRecord.CommandImageList = ParseCommandImages(command["imageList"]);
                if (command.Keys.Contains("featureList")) commandRecord.FeatureImageList = ParseCommandImages(command["featureList"]);
                cc.commandList.RecordList.Add(commandRecord);
            }

            CharLoader.Core.customCharacters.Add(cc);
            CharLoader.Core.s_CharLoadCallbackHandler?.Invoke(cc);

            List<CharacterSkinDataStore> CharacterSkinDataList = 
                (List<CharacterSkinDataStore>)typeof(CharacterSkinManager).GetField("CharacterSkinDataList", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(CharacterSkinManager.ins);

            CharacterSkinDataStore characterSkinDataStore = CharacterSkinDataList.FirstOrDefault((CharacterSkinDataStore c) => c.InternalCharacterName == cc.internalName);
            if (characterSkinDataStore == null)
            {
                characterSkinDataStore = new CharacterSkinDataStore(cc.internalName);
                if (characterSkinDataStore.Character == BattleCache.CharacterEnum.UNSET)
                    throw new Exception($"CharLoader mod: Character Skin Loader unable to find character enum for internal name \"{cc.internalName}\"");

                characterSkinDataStore.SkinList.Add(new CharacterSkinDataStore.Skin("Default", $"{path}/sheet.png"));
                CharacterSkinDataList.Add(characterSkinDataStore);
            }

            FormsListManager.CharacterFormsDictionary[Data.Character] = new List<string>() { cc.internalName };
            SaveData.Data.unlockedCharacters[Data.Character] = true;

            CharLoader.Core.ArcadeModeLineupDisabledDefault.Add(Data.Character);
            Melon<CharLoader.Core>.Instance.ResetArcadeLineup();

            Melon<CharLoader.Core>.Logger.Msg($"Loaded custom character \"{cc.rootCharacter.name}\"");
            Debug.Log($"Loaded custom character \"{cc.rootCharacter.name}\"");
        }

        Destroy(gameObject);
    }

    IEnumerator TextureDownload(string url)
    {
        using (UnityWebRequest www = UnityWebRequestTexture.GetTexture(url))
        {
            yield return www.SendWebRequest();
            texture = DownloadHandlerTexture.GetContent(www);
        }
    }

    AnimAction ParseAction(ProxyObject actionVar, Texture2D texture, Dictionary<string, AudioClip> soundKeys, List<Sprite> puppets)
    {
        AnimAction action = new AnimAction();

        // v1.6: Puppet animation
        if (puppets != null)
        {
            action.puppets = new List<PuppetAction>();
            for (int i = 0; i < puppets.Count; i++)
            {
                PuppetAction puppet = new PuppetAction();
                puppet.on = false;
                action.puppets.Add(puppet);
            }
        }

        if (actionVar.Keys.Contains("frame"))
        {
            Variant frameVar = actionVar["frame"];
            int x = frameVar[0];
            int y = frameVar[1];
            int w = frameVar[2];
            int h = frameVar[3];
            if (w < 0) w = texture.width;
            if (h < 0) h = texture.height;

            if (h == 0)
            {
                // don't divide by zero, warn the user too
                Melon<CharLoader.Core>.Logger.Msg($"WARNING: {CurrCharacterLoading} has a 'frame' action with height = zero! ({x}, {y}, {w}, {h})");
                h = texture.height;
            }

            action.frame = Sprite.Create(texture, new Rect(x, texture.height - y - h, w, h), new Vector2(.5f, .5f), 20);
        }

        if (actionVar.Keys.Contains("setAnim"))
            action.setAnim = actionVar["setAnim"];

        if (actionVar.Keys.Contains("scale"))
            action.scale = new Vector2(actionVar["scale"][0], actionVar["scale"][1]);

        if (actionVar.Keys.Contains("offset"))
            action.offset = new Vector2(actionVar["offset"][0], actionVar["offset"][1]);

        if (actionVar.Keys.Contains("angle"))
            action.angle = actionVar["angle"];

        if (actionVar.Keys.Contains("sound") && soundKeys != null)
        {
            // v1.2: change from string to "SoundAction" class
            Variant soundVar = actionVar["sound"];
            action.sound = new SoundAction();

            if (soundVar as ProxyString != null)
            {
                if (soundKeys.ContainsKey(soundVar)) action.sound.sounds.Add(soundKeys[soundVar]);
                action.sound.loop = false;
            }
            else
            {
                foreach (Variant soundName in soundVar["sounds"] as ProxyArray)
                    if (soundKeys.ContainsKey(soundName)) action.sound.sounds.Add(soundKeys[soundName]);
                action.sound.loop = soundVar["loop"];
            }
        }

        if (actionVar.Keys.Contains("color"))
            action.color = new Color(
                actionVar["color"][0] / 255f,
                actionVar["color"][1] / 255f,
                actionVar["color"][2] / 255f,
                actionVar["color"][3] / 255f
            );

        if (actionVar.Keys.Contains("hitbox"))
        {
            ProxyObject hitboxObj = actionVar["hitbox"] as ProxyObject;
            action.hitbox = new HitboxAction();
            action.hitbox.on = hitboxObj["on"];
            if (hitboxObj.Keys.Contains("pos"))
                action.hitbox.pos = new Vector2(hitboxObj["pos"][0], hitboxObj["pos"][1]);
            if (hitboxObj.Keys.Contains("scale"))
                action.hitbox.scale = new Vector2(hitboxObj["scale"][0], hitboxObj["scale"][1]);
        }

        // v1.6: Puppet animation
        if (actionVar.Keys.Contains("puppets"))
        {
            foreach (var pair in actionVar["puppets"] as ProxyObject)
            {
                int i;
                if (int.TryParse(pair.Key, out i))
                {
                    ProxyObject puppetObj = pair.Value as ProxyObject;

                    action.puppets[i].on = puppetObj["on"];
                    action.puppets[i].layer = puppetObj["layer"];
                    if (puppetObj.Keys.Contains("angle"))
                        action.puppets[i].angle = puppetObj["angle"];
                    if (puppetObj.Keys.Contains("offset"))
                        action.puppets[i].offset = new Vector2(puppetObj["offset"][0], puppetObj["offset"][1]);
                    if (puppetObj.Keys.Contains("scale"))
                        action.puppets[i].scale = new Vector2(puppetObj["scale"][0], puppetObj["scale"][1]);
                }
            }
        }

        // v1.6: Interpolation type
        if (actionVar.Keys.Contains("interpolation"))
        {
            int value = actionVar["interpolation"];
            action.interpolation = (ActionInterpType)value;
        }

        action.callCustomQueue = actionVar.Keys.Contains("callCustomQueue");

        action.delay = (actionVar.Keys.Contains("delay")) ? (float)actionVar["delay"] : 0;

        return action;
    }

    List<CommandImageDisplayEnum> ParseCommandImages(Variant imagesObj)
    {
        List<CommandImageDisplayEnum> images = new List<CommandImageDisplayEnum>();

        foreach (Variant image in imagesObj as ProxyArray)
        {
            // ugly as shit, but let's be real, this only runs when loading the character anyway

            if (image == "empty") images.Add(CommandImageDisplayEnum.Empty);
            if (image == "up") images.Add(CommandImageDisplayEnum.Up);
            if (image == "down") images.Add(CommandImageDisplayEnum.Down);
            if (image == "left") images.Add(CommandImageDisplayEnum.Left);
            if (image == "right") images.Add(CommandImageDisplayEnum.Right);
            if (image == "attack") images.Add(CommandImageDisplayEnum.Attack);
            if (image == "guard" || image == "block" || image == "defend") images.Add(CommandImageDisplayEnum.Defend);
            if (image == "jump") images.Add(CommandImageDisplayEnum.Jump);
            if (image == "z") images.Add(CommandImageDisplayEnum.ZTrigger);
            if (image == "critical" || image == "crit" || image == "criticalstrike") images.Add(CommandImageDisplayEnum.CriticalStrike);
            if (image == "guardbreaker") images.Add(CommandImageDisplayEnum.GuardBreaker);
            if (image == "fss" || image == "fullstun" || image == "fullstunstrike") images.Add(CommandImageDisplayEnum.FullStunStrike);
        }

        return images;
    }

    // v1.6: Puppet animation
    void SetupPuppets(CharacterCompanion companion, ProxyObject jsonRoot)
    {
        companion.puppets = new List<Sprite>();

        GameObject SpriteContainer = companion.prefab.transform.Find("SpriteRenderer").gameObject;
        GameObject SpriteChildPrefab = GameObject.Instantiate(SpriteContainer);
        SpriteChildPrefab.SetActive(false);
        SpriteContainer.transform.RemoveAllChildren();

        if (!jsonRoot.Keys.Contains("puppets"))
            return;

        foreach (var pair in jsonRoot["puppets"] as ProxyObject)
        {
            ProxyArray puppetFrameArr = pair.Value as ProxyArray;

            string name = pair.Key;

            int x = puppetFrameArr[0];
            int y = puppetFrameArr[1];
            int w = puppetFrameArr[2];
            int h = puppetFrameArr[3];
            if (w < 0) w = companion.sheet.width;
            if (h < 0) h = companion.sheet.height;

            if (h == 0)
            {
                // don't divide by zero, warn the user too
                Melon<CharLoader.Core>.Logger.Msg($"WARNING: puppet '{name}' in {CurrCharacterLoading} has height zero! ({x}, {y}, {w}, {h})");
                h = companion.sheet.height;
            }

            GameObject PuppetGameObj = GameObject.Instantiate(SpriteChildPrefab, SpriteContainer.transform);
            PuppetGameObj.name = $"puppet_{name}";
            PuppetGameObj.SetActive(true);

            SpriteRenderer comp = PuppetGameObj.GetComponent<SpriteRenderer>();
            comp.sprite = Sprite.Create(companion.sheet, new Rect(x, companion.sheet.height - y - h, w, h), new Vector2(.5f, .5f), 20);

            companion.puppets.Add(comp.sprite);
        }

        GameObject.Destroy(SpriteChildPrefab);
    }
}