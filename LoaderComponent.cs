using UnityEngine;
using System.Collections;
using UnityEngine.Networking;
using MelonLoader;
using TinyJSON;
using System.Reflection;

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

            Variant json = JSON.Load(File.ReadAllText($"{path}/character.json"));
            CustomCharacter cc = new CustomCharacter();

            CurrCharacterLoading = charName;
            cc.internalName = charName;
            cc.charSelectScale = json["general"]["scale"]["charSelect"];
            cc.resultsScale = json["general"]["scale"]["results"];
            cc.charSelectOffset = new Vector2(json["general"]["offset"]["charSelect"][0], json["general"]["offset"]["charSelect"][1]);
            cc.resultsOffset = new Vector2(json["general"]["offset"]["results"][0], json["general"]["offset"]["results"][1]);

            cc.rootCharacter = new CharacterCompanion();
            cc.rootCharacter.name = json["general"]["displayName"];
            cc.rootCharacter.scale = json["general"]["scale"]["ingame"];
            cc.rootCharacter.offset = new Vector2(json["general"]["offset"]["ingame"][0], json["general"]["offset"]["ingame"][1]);

            yield return TextureDownload($"{path}/sheet.png");
            texture.filterMode = FilterMode.Point;
            cc.rootCharacter.sheet = texture;

            yield return TextureDownload($"{path}/portrait.png");
            cc.portrait = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, 0), 50);

            yield return TextureDownload($"{path}/battleportrait.png");
            texture.filterMode = FilterMode.Point;
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

            CharacterData_SO Data = ScriptableObject.CreateInstance<CharacterData_SO>();
            Data.Prefab_SpecialCharacterSettingsUI = BattleCache.ins.CharacterData_Sonic.Prefab_SpecialCharacterSettingsUI;
            Data.Character = (BattleCache.CharacterEnum)(100 + CharLoader.Core.customCharacters.Count);
            Data.name = $"[CharacterData] {cc.internalName}";
            Data.DittoHue = BattleCache.ins.CharacterData_Mario.DittoHue;
            Data.DittoSaturation = BattleCache.ins.CharacterData_Mario.DittoSaturation;
            Data.DittoContrast = BattleCache.ins.CharacterData_Mario.DittoContrast;

            ProxyObject generalObj = json["general"] as ProxyObject;
            if (generalObj.Keys.Contains("colors"))
            {
                ProxyObject colors = generalObj["colors"] as ProxyObject;
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

            Variant animsRoot = json["anims"];
            cc.rootCharacter.animations = new Dictionary<int, CustomAnimation>();
            foreach (var pair in animsRoot as ProxyObject)
            {
                ProxyObject animObject = pair.Value as ProxyObject;
                CustomAnimation customAnim = new CustomAnimation();
                customAnim.actions = new List<AnimAction>();
                customAnim.hash = Animator.StringToHash(pair.Key);
                customAnim.loops = animObject.Keys.Contains("loops") ? animObject["loops"] : -1;
                customAnim.interpolate = animObject.Keys.Contains("interpolate") ? animObject["interpolate"] : true;
                if (animObject.Keys.Contains("scale")) customAnim.scale = new Vector2(animObject["scale"][0], animObject["scale"][1]);
                if (animObject.Keys.Contains("offset")) customAnim.offset = new Vector2(animObject["offset"][0], animObject["offset"][1]);
                bool isGetUp = (pair.Key == "GetUp");

                Variant animList = animObject["frames"];
                foreach (ProxyObject actionVar in animList as ProxyArray)
                {
                    AnimAction action = ParseAction(actionVar, cc.rootCharacter.sheet, cc.sounds);

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

            Variant effectsRoot = json["effects"];
            cc.effects = new Dictionary<string, CustomEffectEntry>();
            foreach (var pair in effectsRoot as ProxyObject)
            {
                ProxyObject effectObject = pair.Value as ProxyObject;

                CustomEffectEntry customEffect = new CustomEffectEntry();
                yield return TextureDownload($"{path}/effects/{effectObject["texture"]}.png");
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
                    AnimAction action = ParseAction(actionVar, customEffect.texture, cc.sounds);

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

                    Variant companionJson = JSON.Load(File.ReadAllText($"{companionPath}/companion.json"));

                    CharacterCompanion companion = new CharacterCompanion();
                    companion.name = companionName;

                    companion.scale = companionJson["general"]["scale"];
                    companion.offset = new Vector2(companionJson["general"]["offset"][0], companionJson["general"]["offset"][1]);

                    yield return TextureDownload($"{companionPath}/sheet.png");
                    texture.filterMode = FilterMode.Point;
                    companion.sheet = texture;

                    companion.prefab = GameObject.Instantiate(CharPrefab);
                    companion.prefab.name = companionName;
                    companion.prefab.SetActive(false);
                    GameObject.DontDestroyOnLoad(companion.prefab);

                    companion.animations = new Dictionary<int, CustomAnimation>();
                    Variant cAnimsRoot = companionJson["anims"];
                    foreach (var pair in cAnimsRoot as ProxyObject)
                    {
                        ProxyObject animObject = pair.Value as ProxyObject;
                        CustomAnimation customAnim = new CustomAnimation();
                        customAnim.actions = new List<AnimAction>();
                        customAnim.hash = Animator.StringToHash(pair.Key);
                        customAnim.loops = animObject.Keys.Contains("loops") ? animObject["loops"] : -1;
                        customAnim.interpolate = animObject.Keys.Contains("interpolate") ? animObject["interpolate"] : true;
                        if (animObject.Keys.Contains("scale")) customAnim.scale = new Vector2(animObject["scale"][0], animObject["scale"][1]);
                        if (animObject.Keys.Contains("offset")) customAnim.offset = new Vector2(animObject["offset"][0], animObject["offset"][1]);

                        Variant animList = animObject["frames"];
                        foreach (ProxyObject actionVar in animList as ProxyArray)
                        {
                            AnimAction action = ParseAction(actionVar, companion.sheet, cc.sounds);

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

    AnimAction ParseAction(ProxyObject actionVar, Texture2D texture, Dictionary<string, AudioClip> soundKeys)
    {
        AnimAction action = new AnimAction();

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

            action.frame = Sprite.Create(texture, new Rect(x, -y + (h * (texture.height / h - 1)), w, h), new Vector2(.5f, .5f), 20);
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
}