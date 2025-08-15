using UnityEngine;

public class CustomEffectSprite : MonoBehaviour
{
    Transform AnchorObject;
    Vector2 AnchorOffset;

    public SpriteRenderer Comp_SpriteRenderer;
    public CustomAnimator Comp_CustomAnimator;

    public static CustomEffectSprite Create(Vector2 position, CustomEffectEntry effect, bool isFacingRight = true, bool AlwaysAppearAboveFighters = false)
    {
        GameObject effectObj = Instantiate(BattleController.instance.EffectSpritePrefab, position, default(Quaternion));
        effectObj.name = "aCustomEffect";
        Destroy(effectObj.GetComponent<EffectSprite>());
        Destroy(effectObj.GetComponent<Animator>());
        CustomEffectSprite component = effectObj.AddComponent<CustomEffectSprite>();
        component.Comp_CustomAnimator = effectObj.AddComponent<CustomAnimator>();

        GameObject spriteRendererObj = effectObj.transform.Find("sprite").gameObject;
        component.Comp_CustomAnimator.SetSingleAnim(effect.anim, spriteRendererObj, effect.anim.offset);
        component.Comp_CustomAnimator.IgnoreIngameSprite = true;
        component.Comp_SpriteRenderer = spriteRendererObj.GetComponent<SpriteRenderer>();

        component.transform.localScale = Vector3.Scale(effectObj.transform.localScale, new Vector3(isFacingRight ? 1 : (-1), 1f, 1f));
        component.SpriteRenderer_SetSortOrder(AlwaysAppearAboveFighters ? 30 : 0);

        return component;
    }

    public void SpriteRenderer_SetSortOrder(int sortOrder)
    {
        Comp_SpriteRenderer.sortingOrder = sortOrder;
    }

    public void AnchorPositionToObject(Transform obj, Vector2 offset)
    {
        AnchorObject = obj;
        AnchorOffset = offset;
        Update();
    }

    private void Update()
    {
        Comp_CustomAnimator.enabled = !SMBZGlobals.IsPaused && BattleController.instance.CinematicSettings.PauseTimer <= 0f;

        if (AnchorObject != null)
        {
            Vector3 position = AnchorObject.position + (Vector3)AnchorOffset;
            position.z = transform.position.z;
            transform.position = position;
        }

        if (!Comp_CustomAnimator.m_Ended) return;

        Destroy(gameObject);
    }
}