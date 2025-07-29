using HarmonyLib;
using SMBZG;
using System.Reflection;
using System.Collections;
using UnityEngine;

public class CustomBaseCharacter : BaseCharacter
{
    public Animator Comp_Animator;
    public CustomAnimator Comp_CustomAnimator;
    public CustomCharacter cc;
    public Rigidbody2D Comp_Rigidbody2D;

    protected AudioClip SoundEffect_MR_Dodge;
    protected AudioClip SoundEffect_MR_DodgeSuccess;
    protected AudioClip SoundEffect_MR_Engage;
    protected AudioClip SoundEffect_MR_Whiff;
    protected AudioClip SoundEffect_MR_Strike;


    public CharacterData_SO CharacterData
    {
        get
        {
            return (CharacterData_SO)typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetField("CharacterData", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(this, value);
        }
    }

    public PursueBundle PursueData
    {
        get
        {
            return (PursueBundle)typeof(BaseCharacter).GetField("PursueData", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetField("PursueData", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public CharacterControl MyCharacterControl
    {
        get
        {
            return (CharacterControl)typeof(BaseCharacter).GetField("MyCharacterControl", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetField("MyCharacterControl", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public float HitStun
    {
        get
        {
            return (float)typeof(BaseCharacter).GetProperty("HitStun", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetProperty("HitStun", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public bool IsCPUControlled
    {
        get
        {
            return (bool)typeof(BaseCharacter).GetProperty("IsCPUControlled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
    }

    public bool IsNPC
    {
        get
        {
            return (bool)typeof(BaseCharacter).GetField("IsNPC", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetField("IsNPC", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public bool IsFacingRight
    {
        get
        {
            return (bool)typeof(BaseCharacter).GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            typeof(BaseCharacter).GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    protected override void Awake()
    {
        Comp_Animator = GetComponent<Animator>();
        Comp_CustomAnimator = GetComponent<CustomAnimator>();
        Comp_InterplayerCollider = gameObject.transform.GetChild(2).gameObject.GetComponent<InterplayerCollider>();
        Comp_InterplayerCollider.GetType().GetField("MyCharacter", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(Comp_InterplayerCollider, this);
        //Comp_InterplayerCollider.gameObject.GetComponent<CapsuleCollider2D>().size = new Vector2(2.8f, 1f);
        AdditionalCharacterSpriteList = new List<SpriteRenderer>();
        SupportingSpriteList = new List<SpriteRenderer>();

        base.Awake();

        Comp_Rigidbody2D = GetComponent<Rigidbody2D>();
        AerialAcceleration = 15f;
        GroundedAcceleration = 30f;
        GroundedDrag = 3f;
        HopPower = 10.5f;
        JumpChargeMax = 0f;
        Pursue_Speed = 25f;
        Pursue_StartupDelay = 0.1f;

        SetField("EnergyMax", 200f);
        SetField("EnergyStart", 100f);
        IsFacingRight = base.tag == "Team1";
    }

    public object GetField(string name)
    {
        return GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance).GetValue(this);
    }

    public void SetField(string name, object value)
    {
        GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance).SetValue(this, value);
    }

    public object GetProperty(string name)
    {
        return GetType().GetProperty(name, BindingFlags.NonPublic | BindingFlags.Instance).GetValue(this);
    }

    public void SetProperty(string name, object value)
    {
        GetType().GetProperty(name, BindingFlags.NonPublic | BindingFlags.Instance).SetValue(this, value);
    }

    public void SetPlayerState(PlayerStateENUM state)
    {
        SetField("PlayerState", state);
    }

    public PlayerStateENUM GetPlayerState()
    {
        return (PlayerStateENUM)GetField("PlayerState");
    }

    public void SetMovementRushState(MovementRushStateENUM state)
    {
        SetField("MovementRushState", state);
    }

    public MovementRushStateENUM GetMovementRushState()
    {
        return (MovementRushStateENUM)GetField("MovementRushState");
    }

    public virtual BattleParticipantDataModel GetMyParticipantDataReference()
    {
        return ((CharacterControl)GetField("MyCharacterControl")).ParticipantDataReference;
    }

    public HitBoxDamageParameters GetHitboxDamageProperties(HitBox which=null)
    {
        if (!which) which = base.HitBox_0;
        return (HitBoxDamageParameters)typeof(HitBox).GetField("DamageProperties", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(which);
    }

    public void SetHitboxDamageProperties(HitBoxDamageParameters properties, HitBox which=null)
    {
        if (!which) which = base.HitBox_0;
        typeof(HitBox).GetField("DamageProperties", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(which, properties);
    }

    [HarmonyPatch(typeof(BaseCharacter), "GetMyParticipantDataReference")]
    private static class GetParticipantDataPatch
    {
        private static bool Prefix(BaseCharacter __instance, ref BattleParticipantDataModel __result)
        {
            if (!__instance.GetType().IsSubclassOf(typeof(CustomBaseCharacter)))
                return true;

            CustomBaseCharacter i = (CustomBaseCharacter)__instance;
            __result = i.GetMyParticipantDataReference();
            return false;
        }
    }

    protected override void Start()
    {
        base.HitBox_0 = base.transform.Find("HitBox_0").GetComponent<HitBox>();
        base.HitBox_0.tag = base.tag;

        SoundEffect_MR_Dodge = SoundCache.ins.Battle_StaffSwish;
        SoundEffect_MR_DodgeSuccess = SoundCache.ins.Battle_Swish_Light;
        SoundEffect_MR_Engage = SoundCache.ins.Battle_Leap_DBZ2;
        SoundEffect_MR_Whiff = SoundCache.ins.Battle_Swish_Light;
        SoundEffect_MR_Strike = SoundCache.ins.Battle_Swish_Light;

        if (CharacterData == null) return;

        foreach (CustomCharacter ch in CharLoader.Core.customCharacters)
        {
            if (ch.characterData == CharacterData)
            {
                cc = ch;
                break;
            }
        }
        Comp_Animator.enabled = false;
        Comp_CustomAnimator.SetAnimList(cc.rootCharacter.animations, transform.Find("SpriteRenderer").gameObject, cc.rootCharacter.offset, cc.rootCharacter.scale, base.HitBox_0);
        Comp_CustomAnimator.IgnoreColorAction = true;
        Comp_CustomAnimator.m_GetUpTimer = cc.getUpTimer;

        if (cc.sounds.ContainsKey("jump")) SoundEffect_Jump = cc.sounds["jump"];
        if (cc.sounds.ContainsKey("land")) SoundEffect_Land = cc.sounds["land"];

        typeof(BattleParticipantDataModel).GetField("PreventManualEnergyGain", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(GetMyParticipantDataReference(), false);
        GetMyParticipantDataReference().OnComboEnd += Handle_OnComboEnd;
        foreach (Transform item in base.transform)
        {
            item.gameObject.tag = base.gameObject.tag;
        }

        if (HitStun > 0f)
        {
            Comp_CustomAnimator.Play("Hurt_AirUpwards");
        }
    }

    protected override void Update()
    {
        base.Update();

        if (SMBZGlobals.IsPaused)
        {
            return;
        }

        bool IsFrozen = (bool)GetField("IsFrozen");
        if (!IsFrozen && GetPlayerState() == PlayerStateENUM.Hurt && HitStun <= 0f)
        {
            SetPlayerState(PlayerStateENUM.Idle);
            int stateNameHash = !Comp_Animator.GetBool(AP_IsMovementRushing) ? ASN_Idle : (IsOnGround ? ASN_MR_Ground_Land : ASN_MR_Air_Idle);
            Comp_CustomAnimator.Play(stateNameHash);
        }

        bool MovementRushIntro = Comp_Animator.GetBool(AP_IsMovementRushing) && SMBZGlobals.BattleState == BattleController.BattleStateENUM.Normal;

        Comp_CustomAnimator.m_CurrentProperties.hspeed = Comp_Animator.GetFloat("hspeed");
        Comp_CustomAnimator.m_CurrentProperties.vspeed = Comp_Animator.GetFloat("vspeed");
        Comp_CustomAnimator.m_CurrentProperties.HitStun = Comp_Animator.GetFloat("HitStun");
        Comp_CustomAnimator.m_CurrentProperties.BlockStun = (float)GetField("BlockStun");
        Comp_CustomAnimator.m_CurrentProperties.Intensity = Comp_Animator.GetFloat("Intensity");
        Comp_CustomAnimator.m_CurrentProperties.OnGround = Comp_Animator.GetBool("OnGround");
        Comp_CustomAnimator.m_CurrentProperties.Guarding = GetPlayerState() == PlayerStateENUM.Guarding;
        Comp_CustomAnimator.m_CurrentProperties.Bursting = Comp_Animator.GetBool("Bursting");
        Comp_CustomAnimator.m_CurrentProperties.InputingLeft = Comp_Animator.GetBool("InputingLeft");
        Comp_CustomAnimator.m_CurrentProperties.InputingRight = Comp_Animator.GetBool("InputingRight");
        Comp_CustomAnimator.m_CurrentProperties.DontChangeSprite =
            !Comp_CustomAnimator.m_CurrentProperties.Bursting && (
                GetPlayerState() == PlayerStateENUM.Attacking ||
                GetPlayerState() == PlayerStateENUM.Pursuing ||
                GetPlayerState() == PlayerStateENUM.Cinematic_NoInput ||
                (Comp_Animator.GetBool(AP_IsMovementRushing) && !MovementRushIntro)
            );

        if (MovementRushIntro)
        {
            bool flag = SMBZGlobals.MovementRushManager.ActiveMovementRush?.IsDirectionOfRushRight ?? true;
            Comp_CustomAnimator.m_CurrentProperties.hspeed = 9;
            Comp_CustomAnimator.m_CurrentProperties.InputingLeft = !flag;
            Comp_CustomAnimator.m_CurrentProperties.InputingRight = flag;
        }

        if (!Comp_CustomAnimator.m_CurrentProperties.DontChangeSprite && CurrentAttackData != null)
            CurrentAttackData = null;
    }

    protected override void Update_MovementRushAnimator()
    {
        bool flag = SMBZGlobals.MovementRushManager.ActiveMovementRush?.IsDirectionOfRushRight ?? true;
        if (SMBZGlobals.BattleState == BattleController.BattleStateENUM.MovementRush_Grounded)
        {
            if (IsHurt || GetPlayerState() != PlayerStateENUM.Idle || GetMovementRushState() != MovementRushStateENUM.Idle)
                return;

            FlipSpriteByFacingDirection(flag);
            if (flag)
            {
                if (MyCharacterControl.IsInputtingRight)
                    Comp_CustomAnimator.Play(IsOnGround ? ASN_MR_Ground_MoveForward : ASN_MR_Air_Idle);
                else
                    Comp_CustomAnimator.Play(IsOnGround ? ASN_MR_Ground_Idle : ASN_MR_Air_Idle);
            }
            else
            {
                if (MyCharacterControl.IsInputtingLeft)
                    Comp_CustomAnimator.Play(IsOnGround ? ASN_MR_Ground_MoveForward : ASN_MR_Air_Idle);
                else
                    Comp_CustomAnimator.Play(IsOnGround ? ASN_MR_Ground_Idle : ASN_MR_Air_Idle);
            }
        }
        else
        {
            if (SMBZGlobals.BattleState != BattleController.BattleStateENUM.MovementRush_Aerial)
                return;

            if (!IsHurt && GetPlayerState() == PlayerStateENUM.Idle && GetMovementRushState() == MovementRushStateENUM.Idle)
            {
                if (MyCharacterControl.IsInputtingUp)
                    Comp_CustomAnimator.Play(ASN_MR_Air_MoveUpward);
                else if (MyCharacterControl.IsInputtingDown)
                    Comp_CustomAnimator.Play(ASN_MR_Air_MoveDownward);
                else if (MyCharacterControl.IsInputtingLeft || MyCharacterControl.IsInputtingRight)
                    Comp_CustomAnimator.Play(ASN_MR_Air_MoveForward);
                else
                    Comp_CustomAnimator.Play(ASN_MR_Air_Idle);
            }

            FlipSpriteByFacingDirection();
        }
    }

    [HarmonyPatch(typeof(BaseCharacter), "UpdateFrozenEffect")]
    private static class UpdateFrozenEffectPatch
    {
        private static bool Prefix(BaseCharacter __instance)
        {
            if (!__instance.GetType().IsSubclassOf(typeof(CustomBaseCharacter)) && __instance.GetType() != typeof(CustomBaseCharacter))
                return true;

            CustomBaseCharacter c = (CustomBaseCharacter)__instance;
            FieldInfo OnFrozen = typeof(BaseCharacter).GetField("OnFrozen", BindingFlags.Instance | BindingFlags.NonPublic);
            FieldInfo OffFrozen = typeof(BaseCharacter).GetField("OffFrozen", BindingFlags.Instance | BindingFlags.NonPublic);
            FieldInfo IsFrozen = typeof(BaseCharacter).GetField("IsFrozen", BindingFlags.Instance | BindingFlags.NonPublic);
            FieldInfo Frozen_PreservedVelocity = typeof(BaseCharacter).GetField("Frozen_PreservedVelocity", BindingFlags.Instance | BindingFlags.NonPublic);
            FieldInfo FreezeAnchor = typeof(BaseCharacter).GetField("FreezeAnchor", BindingFlags.Instance | BindingFlags.NonPublic);
            PropertyInfo FrozenTimer = typeof(BaseCharacter).GetProperty("FrozenTimer", BindingFlags.Instance | BindingFlags.NonPublic);

            if ((bool)OnFrozen.GetValue(c))
            {
                OnFrozen.SetValue(c, false);
                Frozen_PreservedVelocity.SetValue(c, c.Comp_Rigidbody2D.velocity);
                FreezeAnchor.SetValue(c, new Vector2(__instance.transform.position.x, __instance.transform.position.y));
                c.Comp_Rigidbody2D.isKinematic = true;
                if (!BattleController.instance.CinematicSettings.PauseExceptions.Contains(__instance.gameObject))
                {
                    if (c.IsHurt)
                    {
                        c.StartCoroutine(c.LateCustomAnimatorDisable());
                    }
                    else
                    {
                        c.Comp_CustomAnimator.enabled = false;
                    }
                }
            }

            if ((bool)IsFrozen.GetValue(c))
            {
                c.Comp_Rigidbody2D.velocity = new Vector3(0f, 0f, 0f);
            }

            if ((bool)OffFrozen.GetValue(c))
            {
                OffFrozen.SetValue(c, false);
                c.Comp_Rigidbody2D.isKinematic = false;
                c.Comp_Rigidbody2D.velocity = (Vector2)Frozen_PreservedVelocity.GetValue(c);
                __instance.transform.position = (Vector2)FreezeAnchor.GetValue(c);
                c.Comp_CustomAnimator.enabled = true;
                typeof(BaseCharacter).GetField("Frozen_PreservedVelocity_For_FixedUpdatePlayerToPlayerCollision", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(c, (Vector2?)Frozen_PreservedVelocity.GetValue(c));
            }

            bool isFrozen = (bool)IsFrozen.GetValue(c);
            IsFrozen.SetValue(c, (float)FrozenTimer.GetValue(c) > 0f);
            if ((bool)IsFrozen.GetValue(c))
            {
                FrozenTimer.SetValue(c, Mathf.Clamp((float)FrozenTimer.GetValue(c) - Time.deltaTime, 0f, float.MaxValue));
            }

            OnFrozen.SetValue(c, isFrozen != (bool)IsFrozen.GetValue(c) && (bool)IsFrozen.GetValue(c));
            OffFrozen.SetValue(c, isFrozen != (bool)IsFrozen.GetValue(c) && !(bool)IsFrozen.GetValue(c));

            return false;
        }
    }

    public IEnumerator LateCustomAnimatorDisable()
    {
        yield return new WaitForEndOfFrame();
        if ((bool)GetField("IsFrozen"))
        {
            Comp_CustomAnimator.enabled = false;
        }
    }

    protected override void Handle_OnContactGroundEvent()
    {
        base.Handle_OnContactGroundEvent();
        if (!Comp_CustomAnimator.enabled) return;

        if (IsHurt)
        {
            Comp_CustomAnimator.Play(ASN_Tumble);
            return;
        }
        if (GetPlayerState() == PlayerStateENUM.Idle)
            Comp_CustomAnimator.Play(ASN_Land);
    }

    protected override void OnMovementRush_Dodge()
    {
        SMBZGlobals.PlaySound(SoundEffect_MR_Dodge);
    }

    public override void OnMovementRush_DodgeSuccess()
    {
        SMBZGlobals.PlaySound(SoundEffect_MR_DodgeSuccess);
    }

    protected override void OnMovementRush_Engage()
    {
        SMBZGlobals.PlaySound(SoundEffect_MR_Engage);
    }

    protected override void OnMovementRush_Whiff()
    {
        SMBZGlobals.PlaySound(SoundEffect_MR_Whiff);
    }

    protected override void OnMovementRush_Strike()
    {
        SMBZGlobals.PlaySound(SoundEffect_MR_Strike);
    }

    public override void PerformAction_Dodge(Vector2? directionOverride = null)
    {
        base.PerformAction_Dodge(directionOverride);
        CurrentAttackData.ExecuteCustomQueue();
    }

    public override void PerformAction_Strike()
    {
        base.PerformAction_Strike();
        base.HitBox_0.transform.localPosition = Vector3.zero;
        base.HitBox_0.transform.localScale = new Vector3(2, 2, 1);
        base.HitBox_0.IsActive = true;
    }

    public override void PerformAction_Finale(CharacterControl target)
    {
        base.PerformAction_Finale(target);

        Comp_CustomAnimator.m_CurrentProperties.Bursting = false;
        Comp_CustomAnimator.m_CurrentProperties.DontChangeSprite = true;
    }

    public override void PrepareAnAttack(AttackBundle AttackToPrepare, float MinimumPrepTime = 0)
    {
        base.PrepareAnAttack(AttackToPrepare, MinimumPrepTime);
        if (AttackToPrepare.OnAnimationEnd == null)
        {
            AttackToPrepare.OnAnimationEnd = delegate
            {
                CurrentAttackData = null;
                PursueBundle PursueData = (PursueBundle)GetField("PursueData");
                SetPlayerState((!IsNPC && PursueData != null) ? PlayerStateENUM.Pursuing : PlayerStateENUM.Idle);
                if (IsNPC) return;
                SetField("ComboSwingCounter", 0);
                SetField("IsComboLinkAvailable", false);
            };
        }
        if (AttackToPrepare.OnInterrupt == null)
        {
            AttackToPrepare.OnInterrupt = delegate
            {
                if (IsNPC) return;
                SetField("ComboSwingCounter", 0);
                SetField("IsComboLinkAvailable", false);
            };
        }
        Comp_CustomAnimator.Play(AttackToPrepare.AnimationNameHash, AttackToPrepare);
    }

    public override void OnDeath()
    {
        base.OnDeath();
        if (cc.sounds.ContainsKey("death"))
            SMBZGlobals.PlaySound(cc.sounds["death"]);
    }
}
