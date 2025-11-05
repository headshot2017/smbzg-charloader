using System.Reflection;
using System.Collections;
using UnityEngine;
using SMBZG;

public class CustomKoopaRedControl : KoopaRedControl
{
    public KoopaBroDataModel KoopaBroData
    {
        get
        {
            return (KoopaBroDataModel)GetType().BaseType.GetProperty("KoopaBroData", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
    }

    public CharacterControl MyCharacterControl
    {
        get
        {
            return (CharacterControl)GetType().GetField("MyCharacterControl", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("MyCharacterControl", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public CharacterSkinDataStore.Skin CurrentSkin
    {
        get
        {
            return (CharacterSkinDataStore.Skin)GetType().GetField("CurrentSkin", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("CurrentSkin", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public MovementRushStateENUM MovementRushState
    {
        get
        {
            return (MovementRushStateENUM)GetType().GetField("MovementRushState", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("MovementRushState", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public bool IsFacingRight
    {
        get
        {
            return (bool)GetType().GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public CustomKoopaBroControl KoopaBlack
    {
        get
        {
            return (CustomKoopaBroControl)GetType().BaseType.GetField("KoopaBlack", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("KoopaBlack", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public CustomKoopaBroControl KoopaGreen
    {
        get
        {
            return (CustomKoopaBroControl)GetType().BaseType.GetField("KoopaGreen", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("KoopaGreen", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public CustomKoopaBroControl KoopaYellow
    {
        get
        {
            return (CustomKoopaBroControl)GetType().BaseType.GetField("KoopaYellow", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("KoopaYellow", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public List<KoopaBroControl> KoopaBroQueue
    {
        get
        {
            return (List<KoopaBroControl>)GetType().BaseType.GetField("KoopaBroQueue", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("KoopaBroQueue", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public string PlayerNumber
    {
        get
        {
            return (string)GetType().BaseType.GetField("PlayerNumber", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("PlayerNumber", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }


    protected override void Start()
    {
        base.Start();
        StopAllCoroutines();
        StartCoroutine(Custom_Start_Delayed());
    }

    IEnumerator Custom_Start_Delayed()
    {
        yield return new WaitUntil(() => BattleController.instance != null && BattleHUDManager.ins != null && MyCharacterControl != null && KoopaBroData != null);
        if (MovementRushState == MovementRushStateENUM.Inactive)
        {
            bool BattleHasBegun = (bool)typeof(BattleController).GetField("BattleHasBegun", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(BattleController.instance);
            SpawnCustomKoopaBros(BattleHasBegun);
        }
    }

    public void SpawnCustomKoopaBros(bool spawnOffscreen)
    {
        if (MyCharacterControl.ParticipantDataReference.KoopaBros_Single_IsEnabled)
        {
            return;
        }

        float num = -base.FaceDir;
        int num2 = 0;
        if (spawnOffscreen)
        {
            Vector3 vector = Camera.main.WorldToViewportPoint(transform.position, Camera.MonoOrStereoscopicEye.Mono);
            float x = vector.x;
            float num3 = 1f - vector.x;
            num = ((!(x < num3)) ? 1 : (-1));
            num2 = 5;
        }

        int num4 = 1;
        KoopaBlack = GameObject.Instantiate(KoopaBro_Prefab, transform.position + new Vector3((float)(num2 + num4) * num, 0.5f * (float)num4, 0f), transform.rotation, null).GetComponent<CustomKoopaBroControl>();
        num4++;
        KoopaGreen = GameObject.Instantiate(KoopaBro_Prefab, transform.position + new Vector3((float)(num2 + num4) * num, 0.5f * (float)num4, 0f), transform.rotation, null).GetComponent<CustomKoopaBroControl>();
        num4++;
        KoopaYellow = GameObject.Instantiate(KoopaBro_Prefab, transform.position + new Vector3((float)(num2 + num4) * num, 0.5f * (float)num4, 0f), transform.rotation, null).GetComponent<CustomKoopaBroControl>();
        CustomKoopaBroControl[] array = new CustomKoopaBroControl[3] { KoopaBlack, KoopaGreen, KoopaYellow };
        KoopaBroControl.BroTypeEnum[] array2 = new KoopaBroControl.BroTypeEnum[3]
        {
            KoopaBroControl.BroTypeEnum.Black,
            KoopaBroControl.BroTypeEnum.Green,
            KoopaBroControl.BroTypeEnum.Yellow
        };
        for (int i = 0; i < 3; i++)
        {
            array[i].BroType = array2[i];
            array[i].IsFacingRight = IsFacingRight;
            array[i].tag = base.tag;
            array[i].SetSkin(CurrentSkin);
            string teamTag = SMBZGlobals.ActiveBattleData.TeamsList[1].TeamTag;
            bool flag = MyCharacterControl.ParticipantDataReference.TeamTag == teamTag && SMBZGlobals.IsInArcadeMode;
            if (MyCharacterControl.ParticipantDataReference.CPUSettings != BattleCache.CPUSettingsENUM.Player || flag)
            {
                if (SMBZGlobals.ActiveBattleData.GetAllParticipants().Count > 2)
                {
                    int num5 = ((SMBZGlobals.ActiveCharacterControlList[0].ParticipantDataReference.ParticipantIndex != 0 || SMBZGlobals.ActiveCharacterControlList[0].ParticipantDataReference.InputPlayerIndex.HasValue) ? GlobalInputManager.ins.PIM.playerCount : 0);
                    num5 = (flag ? (num5 + 99) : num5);
                    PlayerNumber = "CPU-" + (MyCharacterControl.ParticipantDataReference.ParticipantIndex - num5 + 1);
                }
                else
                {
                    PlayerNumber = "CPU";
                }
            }
            else
            {
                PlayerNumber = "P" + (MyCharacterControl.ParticipantDataReference.InputPlayerIndex + 1);
            }

            if (SaveData.Data.Get_IsPlayerIndicatorsEnabled())
            {
                GameObject.Instantiate(BattleController.instance.PlayerIndicatorPrefab).GetComponent<PlayerIndicator>().Setup(array[i], array[i].tag, isNPC: true, PlayerNumber);
            }
        }

        KoopaBlack.SetupCustom(this, KoopaBroData.Black);
        KoopaGreen.SetupCustom(this, KoopaBroData.Green);
        KoopaYellow.SetupCustom(this, KoopaBroData.Yellow);
        KoopaBroQueue = new List<KoopaBroControl>(array);
    }
}