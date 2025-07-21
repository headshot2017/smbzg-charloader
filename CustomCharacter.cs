using UnityEngine;

public class HitboxAction
{
    public bool on;
    public Vector2 pos;
    public Vector2 scale;
}

public class AnimAction
{
    public Sprite frame = null;
    public string setAnim = null;
    public AudioClip sound = null;
    public HitboxAction hitbox = null;
    public Vector2 scale = Vector2.one;
    public Vector2 offset;
    public Color color = Color.white;
    public float angle;
    public bool callCustomQueue;
    public float delay;
}

public class CustomAnimation
{
    public int hash;
    public int loops;
    public Vector2 scale = Vector2.one;
    public Vector2 offset;
    public bool interpolate;
    public List<AnimAction> actions;
}

public class CustomEffectEntry
{
    public Texture2D texture;
    public CustomAnimation anim;
}

public class CharacterCompanion
{
    public string name;
    public float scale;
    public Vector2 offset;

    public Texture2D sheet;
    public Dictionary<int, CustomAnimation> animations;

    public GameObject prefab;
}

public class CustomCharacter
{
    public string internalName;

    public float charSelectScale;
    public float resultsScale;
    public Vector2 charSelectOffset;
    public Vector2 resultsOffset;

    public CharacterCompanion rootCharacter;
    public CharacterData_SO characterData;
    public CommandListModel commandList;
    public Sprite portrait;
    public Sprite battlePortrait;

    public Dictionary<string, CustomEffectEntry> effects;
    public Dictionary<string, CharacterCompanion> companions;
    public Dictionary<string, AudioClip> sounds;
    public Dictionary<string, AudioClip> music;
    public float getUpTimer;
}