using System.Reflection;
using System.Collections;
using UnityEngine;
using SMBZG;

public class CustomKoopaBroControl : KoopaBroControl
{
    public BaseCharacter ActualLeader;

    public CustomKoopaRedControl KoopaLeader
    {
        get
        {
            return (CustomKoopaRedControl)GetType().BaseType.GetField("KoopaLeader", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("KoopaLeader", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public float RestPositionOffset
    {
        get
        {
            return (float)GetType().GetField("RestPositionOffset", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("RestPositionOffset", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
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

    public bool QueueHasBeenCleared
    {
        get
        {
            return (bool)GetType().BaseType.GetField("QueueHasBeenCleared", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("QueueHasBeenCleared", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public bool QueueInProcess
    {
        get
        {
            return (bool)GetType().BaseType.GetField("QueueInProcess", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().BaseType.GetField("QueueInProcess", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public bool PreventDrag
    {
        get
        {
            return (bool)GetType().GetField("PreventDrag", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("PreventDrag", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public KoopaBroDataModel.BroModel BroDataReference
    {
        get
        {
            return (KoopaBroDataModel.BroModel)GetType().GetField("BroDataReference", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("BroDataReference", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public BroTypeEnum BroType
    {
        get
        {
            return (BroTypeEnum)GetType().GetField("BroType", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("BroType", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public Coroutine Coro_KnockoutFadeToBackgroundAndRecover
    {
        get
        {
            return (Coroutine)GetType().GetField("Coro_KnockoutFadeToBackgroundAndRecover", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(this);
        }
        set
        {
            GetType().GetField("Coro_KnockoutFadeToBackgroundAndRecover", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(this, value);
        }
    }

    public Animator Comp_Animator;
    public Rigidbody2D Comp_Rigidbody2D;


    protected override void Awake()
    {
        base.Awake();
        Comp_Animator = GetComponent<Animator>();
        Comp_Rigidbody2D = GetComponent<Rigidbody2D>();
    }

    public void SetupCustom(CustomKoopaRedControl koopaRedControl, KoopaBroDataModel.BroModel data)
    {
        if (BroDataReference != null)
        {
            BroDataReference.OnHealthChange -= OnHealthChange;
        }

        BroDataReference = data;
        BroDataReference.OnHealthChange += OnHealthChange;
        OnHealthChange();
        if (KoopaLeader != null)
        {
            KoopaLeader.MaxMoveSpeed.OnChange -= Handle_OnLeaderMaxMoveSpeedChanged;
        }

        ActualLeader = KoopaLeader = koopaRedControl;
        KoopaLeader.MaxMoveSpeed.OnChange += Handle_OnLeaderMaxMoveSpeedChanged;

        bool IsUsingAlternateColors = (bool)typeof(CharacterControl).GetField("IsUsingAlternateColors", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(koopaRedControl.MyCharacterControl);
        if (IsUsingAlternateColors)
            SetAlternativeColors(IsUsingAlternateColors);
    }

    private void OnHealthChange()
    {
        if (0f < BroDataReference.KnockoutCountdownTimer && BroDataReference.IsKnockedOut)
        {
            if (Coro_KnockoutFadeToBackgroundAndRecover != null)
            {
                StopCoroutine(Coro_KnockoutFadeToBackgroundAndRecover);
            }

            ClearQueue();
            Coro_KnockoutFadeToBackgroundAndRecover = base.StartCoroutine("KnockoutAndFadeIntoBackground", 0);
        }
    }

    private void ClearQueue()
    {
        if (TaskQueue.Count != 0)
        {
            StopAllCoroutines();
            QueueHasBeenCleared = true;
            QueueInProcess = false;
            TaskQueue.Clear();
        }
    }

    protected override void Update_Moving()
    {
        if (TaskQueue.Count != 0 || !IsIdle || IsInputLocked || !(ActualLeader != null))
        {
            return;
        }

        float num = ActualLeader.transform.position.x + RestPositionOffset * -ActualLeader.FaceDir;
        bool moveLeft = false;
        bool moveRight = false;
        if (Mathf.Abs(num - transform.position.x) > 0.35f)
        {
            if (num < transform.position.x)
            {
                moveLeft = true;
            }
            else if (transform.position.x < num)
            {
                moveRight = true;
            }
        }

        Move(moveLeft, moveRight);
    }

    private void Move(bool MoveLeft, bool MoveRight)
    {
        float num = (base.IsOnGround ? GroundedAcceleration : AerialAcceleration);
        if (MoveLeft || MoveRight)
        {
            PreventDrag = true;
            IsFacingRight = MoveRight;
            int num2 = ((!MoveLeft) ? 1 : (-1));
            if (!Physics2D.Linecast(end: new Vector2(base.transform.position.x + (float)num2, base.transform.position.y), start: base.transform.position, layerMask: 1 << LayerMask.NameToLayer("Ground")))
            {
                Vector2 vector = Vector2.zero;
                if (Mathf.Abs(Comp_Rigidbody2D.velocity.x) < MaxMoveSpeed.GetValue())
                {
                    vector = new Vector2(num * (float)num2, 0f) * BattleController.instance.ActorDeltaTime;
                }

                if ((MoveLeft && 0f < Comp_Rigidbody2D.velocity.x) || (MoveRight && Comp_Rigidbody2D.velocity.x < 0f))
                {
                    vector = new Vector2(num * (float)num2 * 2f, 0f) * BattleController.instance.ActorDeltaTime;
                }

                Comp_Rigidbody2D.velocity += vector;
            }
        }
        else
        {
            PreventDrag = false;
            if (ActualLeader != null)
            {
                IsFacingRight = ActualLeader.FaceDir == 1;
            }
        }

        Comp_Animator.SetBool("InputingLeft", MoveLeft);
        Comp_Animator.SetBool("InputingRight", MoveRight);

        if (BattleController.instance.BackgroundTreadmillEffect != 0 && ActualLeader != null && (ActualLeader.IsHurt || SMBZGlobals.MovementRushManager.ActiveMovementRush != null))
        {
            if (BattleController.instance.BackgroundTreadmillEffect == BattleController.BackgroundTreadmillEffectENUM.RushLeft)
            {
                Comp_Animator.SetBool("InputingRight", value: true);
                Comp_Animator.SetBool("InputingLeft", value: false);
                IsFacingRight = false;
            }
            else if (BattleController.instance.BackgroundTreadmillEffect == BattleController.BackgroundTreadmillEffectENUM.RushRight)
            {
                Comp_Animator.SetBool("InputingLeft", value: true);
                Comp_Animator.SetBool("InputingRight", value: false);
                IsFacingRight = true;
            }
        }
    }
}