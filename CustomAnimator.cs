using UnityEngine;
using System.Reflection;
using MelonLoader;

public class CustomAnimator : MonoBehaviour
{
    Dictionary<int, CustomAnimation> m_Animations = null;
    public CustomAnimation m_CurrentAnimation = null;
    AttackBundle m_CurrentAttack;
    HitBox m_Hitbox;

    UnityEngine.UI.Image m_CompImage;
    SpriteRenderer m_CompSpriteRenderer;
    public Animator m_OriginalAnimator;

    float m_GlobalScale;
    Vector2 m_GlobalOffset;
    bool m_Playing;
    float m_Time;
    int m_Loops;
    public bool IgnoreIngameSprite = false;
    public bool IgnoreColorAction = false;
    public bool m_Ended { get; private set; }
    public int m_Frame { get; private set; }

    // some Comp_Animator properties
    public class Properties
    {
        public float hspeed;
        public float vspeed;
        public float HitStun;
        public float BlockStun;
        public float Intensity;
        public bool OnGround;
        public bool Guarding;
        public bool Bursting;
        public bool DontChangeSprite;
        public bool InputingLeft;
        public bool InputingRight;
    }
    public Properties m_CurrentProperties;
    Properties m_LastProperties;
    public float m_GetUpTimer;

    public static readonly int ASN_Idle = Animator.StringToHash("Idle");
    public static readonly int ASN_IdleB = Animator.StringToHash("IdleB");
    public static readonly int ASN_Walk = Animator.StringToHash("Walk");
    public static readonly int ASN_Run = Animator.StringToHash("Run");
    public static readonly int ASN_Sprint = Animator.StringToHash("Sprint");
    public static readonly int ASN_Bursting = Animator.StringToHash("Bursting");
    public static readonly int ASN_Slide = Animator.StringToHash("Slide");
    public static readonly int ASN_Guard = Animator.StringToHash("Guard");
    public static readonly int ASN_Block = Animator.StringToHash("Block");
    public static readonly int ASN_Jump = Animator.StringToHash("Jump");
    public static readonly int ASN_Fall = Animator.StringToHash("Fall");
    public static readonly int ASN_Land = Animator.StringToHash("Land");
    public static readonly int ASN_Hit = Animator.StringToHash("Hit");
    public static readonly int ASN_Hurt = Animator.StringToHash("Hurt");
    public static readonly int ASN_Hurt_AirUpwards = Animator.StringToHash("Hurt_AirUpwards");
    public static readonly int ASN_Hurt_AirDownwards = Animator.StringToHash("Hurt_AirDownwards");
    public static readonly int ASN_Tumble = Animator.StringToHash("Tumble");
    public static readonly int ASN_Grounded = Animator.StringToHash("Grounded");
    public static readonly int ASN_GetUp = Animator.StringToHash("GetUp");

    public void Awake()
    {
        m_GetUpTimer = 0;
        m_CurrentProperties = new Properties();
        m_LastProperties = new Properties();

        m_OriginalAnimator = GetComponent<Animator>();
        if (m_Animations == null || m_CurrentAnimation == null)
        {
            m_CompImage = null;
            m_CompSpriteRenderer = null;
            m_GlobalScale = 1;
            m_GlobalOffset = Vector2.zero;
            m_Playing = false;
            m_Ended = false;
            m_Time = 0;
            m_Frame = 0;
        }
    }

    public void Update()
    {
        HandleIngameSprite();

        if (!m_Playing || m_CurrentAnimation.actions.Count <= 0) return;

        if (m_OriginalAnimator != null)
            m_OriginalAnimator.enabled = false;
        InterpolateFrames();

        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];

        while ((m_Time += Time.deltaTime) > currAction.delay)
        {
            if (currAction.delay <= 0)
                m_Time = currAction.delay - Time.deltaTime;
            else
                m_Time -= currAction.delay;

            if (m_CurrentAnimation.loops < 0 || m_Loops < m_CurrentAnimation.loops)
            {
                m_Frame = (m_Frame + 1) % m_CurrentAnimation.actions.Count;
                if (m_Frame == 0) m_Loops++;
            }
            else if (m_Frame < m_CurrentAnimation.actions.Count - 1)
                m_Frame++;
            else
                m_Ended = true;

            currAction = m_CurrentAnimation.actions[m_Frame];

            if (OnFrameChange()) return;
        }

        m_LastProperties = m_CurrentProperties;
    }

    bool OnFrameChange()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];

        if (m_CurrentProperties != null && m_CurrentProperties.HitStun <= 0)
            SetColor(currAction.color);
        SetScale();
        SetOffset();
        SetAngle();
        if (currAction.frame != null)
            SetSprite(currAction.frame);

        if (m_Hitbox != null && currAction.hitbox != null)
        {
            m_Hitbox.IsActive = currAction.hitbox.on;
            m_Hitbox.transform.localPosition = currAction.hitbox.pos;
            m_Hitbox.transform.localScale = currAction.hitbox.scale;
        }

        if (m_CurrentAttack != null)
        {
            if (currAction.callCustomQueue && m_CurrentAttack.OnCustomQueue != null && m_CurrentAttack.CustomQueueCallCount < m_CurrentAttack.CustomQueueCallLimit)
                m_CurrentAttack.ExecuteCustomQueue();

            if (m_Ended && m_CurrentAttack.OnAnimationEnd != null)
            {
                m_CurrentAttack.OnAnimationEnd();
                m_CurrentAttack = null;
                return true;
            }
        }

        if (currAction.sound != null)
        {
            SMBZGlobals.PlaySound(currAction.sound);
        }

        if (currAction.setAnim != null)
        {
            Play(Animator.StringToHash(currAction.setAnim), m_CurrentAttack);
            return true;
        }

        return false;
    }

    public void SetAnimList(Dictionary<int, CustomAnimation> animations, GameObject obj, Vector2 globalOffset, float globalScale=1, HitBox hitbox=null)
    {
        m_Animations = animations;
        m_GlobalOffset = globalOffset;
        m_GlobalScale = globalScale;
        m_Hitbox = hitbox;
        m_CompImage = obj.GetComponent<UnityEngine.UI.Image>();
        m_CompSpriteRenderer = obj.GetComponent<SpriteRenderer>();
        if (!m_CompImage && !m_CompSpriteRenderer)
        {
            throw new Exception($"This GameObject ({obj.name}) doesn't have an UI.Image or SpriteRenderer component to set the sprite into");
        }
        if (m_CompImage) m_CompImage.preserveAspect = true;
    }

    public void SetSingleAnim(CustomAnimation animation, GameObject obj, Vector2 globalOffset, float globalScale = 1, HitBox hitbox = null)
    {
        m_Animations = null;
        m_CurrentAnimation = animation;

        m_GlobalOffset = globalOffset;
        m_GlobalScale = globalScale;
        m_Hitbox = hitbox;
        m_CompImage = obj.GetComponent<UnityEngine.UI.Image>();
        m_CompSpriteRenderer = obj.GetComponent<SpriteRenderer>();
        if (!m_CompImage && !m_CompSpriteRenderer)
        {
            throw new Exception($"This GameObject ({obj.name}) doesn't have an UI.Image or SpriteRenderer component to set the sprite into");
        }
        if (m_CompImage) m_CompImage.preserveAspect = true;

        m_Time = 0;
        m_Frame = 0;
        m_Loops = 0;
        m_Playing = true;
        m_Ended = false;
        m_CurrentAttack = null;
        if (m_Hitbox != null) m_Hitbox.IsActive = false;
        OnFrameChange();
    }

    public void SetSprite(Sprite spr)
    {
        if (m_CompImage) m_CompImage.sprite = spr;
        if (m_CompSpriteRenderer) m_CompSpriteRenderer.sprite = spr;
    }

    public void SetColor(Color color)
    {
        if (IgnoreColorAction) return;

        if (m_CompImage) m_CompImage.color = color;
        if (m_CompSpriteRenderer) m_CompSpriteRenderer.color = color;
    }

    public void SetScale()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        if (m_CompImage)
        {
            RectTransform t = m_CompImage.rectTransform;

            t.localScale = new Vector3(
                m_GlobalScale * m_CurrentAnimation.scale.x * currAction.scale.x,
                m_GlobalScale * m_CurrentAnimation.scale.y * currAction.scale.y,
            1);
            t.sizeDelta = new Vector2(m_CurrentAnimation.actions[0].frame.rect.width * m_GlobalScale, m_CurrentAnimation.actions[0].frame.rect.height * m_GlobalScale);
        }
        if (m_CompSpriteRenderer)
        {
            Transform t = m_CompSpriteRenderer.gameObject.transform;

            t.localScale = new Vector3(
                m_GlobalScale * m_CurrentAnimation.scale.x * currAction.scale.x,
                m_GlobalScale * m_CurrentAnimation.scale.y * currAction.scale.y,
            1);
        }
    }

    public void SetOffset()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        if (m_CompImage)
        {
            Transform t = m_CompImage.transform;
            t.localPosition = m_GlobalOffset + m_CurrentAnimation.offset + currAction.offset;
        }
        if (m_CompSpriteRenderer)
        {
            Transform t = m_CompSpriteRenderer.gameObject.transform;
            t.localPosition = m_GlobalOffset + m_CurrentAnimation.offset + currAction.offset;
        }
    }

    public void SetAngle()
    {
        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        Vector3 angle = new Vector3(0, 0, -currAction.angle);
        if (m_CompImage)
        {
            m_CompImage.transform.localEulerAngles = angle;
        }
        if (m_CompSpriteRenderer)
        {
            m_CompSpriteRenderer.gameObject.transform.localEulerAngles = angle;
        }
    }

    public void Stop()
    {
        if (!m_Playing) return;
        m_Playing = false;
        m_OriginalAnimator.enabled = true;
        m_CurrentAnimation = null;
        m_CurrentAttack = null;
    }

    public bool Play(int animHash, bool replay=false)
    {
        if (m_Animations == null || !m_Animations.ContainsKey(animHash))
            return false;
        if (m_CurrentAnimation != null && m_CurrentAnimation.hash == animHash && !replay)
            return true;

        m_CurrentAnimation = m_Animations[animHash];
        m_OriginalAnimator.enabled = false;
        m_Time = 0;
        m_Frame = 0;
        m_Loops = 0;
        m_Playing = true;
        m_Ended = false;
        m_CurrentAttack = null;
        if (m_Hitbox != null) m_Hitbox.IsActive = false;
        OnFrameChange();
        return true;
    }

    public bool Play(string animName)
    {
        return Play(Animator.StringToHash(animName));
    }

    public bool Play(int animHash, AttackBundle attack)
    {
        if (!Play(animHash, true)) return false;
        m_CurrentAttack = attack;
        if (attack != null && attack.OnAnimationStart != null && !attack.OnAnimationStart_HasExecuted)
        {
            attack.OnAnimationStart();
            attack.OnAnimationStart_HasExecuted = true;
        }
        return true;
    }

    void HandleIngameSprite()
    {
        if (IgnoreIngameSprite || !m_CompSpriteRenderer || (m_CurrentAnimation != null && m_CurrentAnimation.hash == ASN_Land && !m_Ended)) return;

        Properties p = m_CurrentProperties;

        if (p.HitStun > 0)
        {
            // switch/case doesn't work here... this shit hurts my soul

            if (m_CurrentAnimation.hash == ASN_Hit)
            {
                if (m_Ended) Play(p.OnGround ? ASN_Hurt : p.vspeed > 0 ? ASN_Hurt_AirUpwards : ASN_Hurt_AirDownwards);
            }
            else if (m_CurrentAnimation.hash == ASN_Hurt_AirUpwards || m_CurrentAnimation.hash == ASN_Hurt_AirDownwards)
            {
                Play(p.vspeed > 0 ? ASN_Hurt_AirUpwards : ASN_Hurt_AirDownwards);
            }
            else if (m_CurrentAnimation.hash == ASN_Tumble)
            {
                if (m_Ended) Play(p.OnGround ? ASN_Grounded : p.vspeed > 0 ? ASN_Hurt_AirUpwards : ASN_Hurt_AirDownwards);
            }
            else if (m_CurrentAnimation.hash == ASN_Hurt || m_CurrentAnimation.hash == ASN_Grounded || m_CurrentAnimation.hash == ASN_GetUp)
            {
                if (m_Ended)
                {
                    if (!p.OnGround)
                        Play(p.vspeed > 0 ? ASN_Hurt_AirUpwards : ASN_Hurt_AirDownwards);
                    else
                        Play(p.HitStun <= m_GetUpTimer ? ASN_GetUp : ASN_Grounded);
                }
            }
            else
                Play(ASN_Hit);

            return;
        }

        if (p.BlockStun > 0)
        {
            Play(ASN_Block);
            return;
        }

        if (p.DontChangeSprite) return;

        if (p.Guarding)
        {
            Play(ASN_Guard);
            return;
        }

        if (p.Bursting)
        {
            Play(ASN_Bursting);
            return;
        }

        if (!p.OnGround)
        {
            Play(p.vspeed > 0 ? ASN_Jump : ASN_Fall);
            return;
        }

        if (p.InputingLeft || p.InputingRight)
        {
            if (p.hspeed < 5)
                Play(ASN_Walk);
            else if (p.hspeed < 20)
                Play(ASN_Run);
            else
                Play(ASN_Sprint);
        }
        else if (p.hspeed != 0)
            Play(ASN_Slide);
        else
            Play(m_CurrentProperties.Intensity < 50 ? ASN_Idle : ASN_IdleB);
    }

    void InterpolateFrames()
    {
        if (m_CurrentAnimation == null || !m_CurrentAnimation.interpolate) return;

        AnimAction currAction = m_CurrentAnimation.actions[m_Frame];
        if (currAction.delay <= 0) return;

        float lerp = m_Time / currAction.delay;
        AnimAction nextAction;
        if (m_Frame >= m_CurrentAnimation.actions.Count - 1)
            nextAction = (m_CurrentAnimation.loops < 0 || m_Loops < m_CurrentAnimation.loops) ? m_CurrentAnimation.actions[0] : currAction;
        else
            nextAction = m_CurrentAnimation.actions[m_Frame + 1];

        if (m_Hitbox != null && currAction.hitbox != null && nextAction.hitbox != null)
        {
            m_Hitbox.transform.localPosition = Vector3.Lerp(currAction.hitbox.pos, nextAction.hitbox.pos, lerp);
            m_Hitbox.transform.localScale = Vector3.Lerp(currAction.hitbox.scale, nextAction.hitbox.scale, lerp);
        }

        Color colorLerp = Color.Lerp(currAction.color, nextAction.color, lerp);

        Vector2 scaleLerp = m_GlobalScale * m_CurrentAnimation.scale;
        scaleLerp.x *= Mathf.Lerp(currAction.scale.x, nextAction.scale.x, lerp);
        scaleLerp.y *= Mathf.Lerp(currAction.scale.y, nextAction.scale.y, lerp);

        Vector2 offsetLerp = m_GlobalOffset + m_CurrentAnimation.offset;
        offsetLerp.x += Mathf.Lerp(currAction.offset.x, nextAction.offset.x, lerp);
        offsetLerp.y += Mathf.Lerp(currAction.offset.y, nextAction.offset.y, lerp);

        float angleLerp = Mathf.Lerp(currAction.angle, nextAction.angle, lerp);

        if (m_CompImage)
        {
            RectTransform t = m_CompImage.rectTransform;

            t.localPosition = offsetLerp;
            t.localEulerAngles = new Vector3(0, 0, -angleLerp);
            t.localScale = scaleLerp;
            t.sizeDelta = new Vector2(m_CurrentAnimation.actions[0].frame.rect.width * m_GlobalScale, m_CurrentAnimation.actions[0].frame.rect.height * m_GlobalScale);

            if (!IgnoreColorAction && m_CurrentProperties != null && m_CurrentProperties.HitStun <= 0)
                m_CompImage.color = colorLerp;
        }
        if (m_CompSpriteRenderer)
        {
            Transform t = m_CompSpriteRenderer.gameObject.transform;

            t.localPosition = offsetLerp;
            t.localEulerAngles = new Vector3(0, 0, -angleLerp);
            t.localScale = scaleLerp;

            if (!IgnoreColorAction && m_CurrentProperties != null && m_CurrentProperties.HitStun <= 0)
                m_CompSpriteRenderer.color = colorLerp;
        }
    }
}