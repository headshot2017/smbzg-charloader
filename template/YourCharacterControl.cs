// This is your character's custom class.
// It's where you will be setting up the attacks and such.

using UnityEngine;
using System.Collections;

public class YourCharacterControl : CustomBaseCharacter
{
    // Cinematic Rush properties.
    public Base_RushProperties RushProperties;

    protected override void Awake()
    {
        base.Awake();

        // See CustomBaseCharacter for things you can modify
        // (right-click -> go to definition, or press F12 on it)
        // You also have access to your CustomCharacter with the "cc" field.
        // If you want to spawn a CustomEffectSprite, or play a custom sound, that is what you will be accessing.
        // e.g.
        // CustomEffectSprite.Create(transform.position, cc.effects["explosion"]);
        // SoundCache.ins.PlaySound(cc.sounds["explosion"]);

        // NOTE: If you want to change the character's animation in some way at some point,
        // Make sure to use Comp_CustomAnimator instead of Comp_Animator!


        // To change movement rush sound effects, see:
        // SoundEffect_MR_Dodge
        // SoundEffect_MR_DodgeSuccess
        // SoundEffect_MR_Engage
        // SoundEffect_MR_Strike
        // SoundEffect_MR_Whiff


        // If you want to change the character/character collision hitbox size:
        //Comp_InterplayerCollider.gameObject.GetComponent<CapsuleCollider2D>().size = new Vector2(2f, 1f);
    }

    protected override void Update_General()
    {
        base.Update_General();
        if (!IsPursuing)
            Update_ReadAttackInput(); // This allows the game to read your character's attack inputs
    }

    protected override void Update_Pursue()
    {
        if (IsFrozen || PursueData == null)
        {
            return;
        }

        // See a character's Update_Pursue function to shape it to how you want your character's pursue to behave.
        // MarioControl: Rushing on the ground
        // LuigiControl: Something like a missile
        // YoshiControl: Flying tackle
        // MechaSonicControl: Homing towards opponent
    }

    protected override IEnumerator OnPursueMiss()
    {
        return base.OnPursueMiss();
    }

    protected override IEnumerator OnPursueContact()
    {
        yield return new WaitForEndOfFrame();

        if (PursueData == null)
        {
            yield break;
        }
    }

    protected override void Handle_OnComboEnd()
    {
        base.Handle_OnComboEnd();

        // If you have any StaleableMoves, call their Clear() functions here.
        // e.g. Staleable_Jab.Clear();
    }

    public override IEnumerator OnBurst_Victory(CharacterControl target, BurstDataStore.VictoryStrikeENUM victoryStrikeType = BurstDataStore.VictoryStrikeENUM.General)
    {
        // This is called when winning a clash.
        // Play the BurstVictoryStrike or BurstVictoryStrike_MR animation depending on the victoryStrikeType.
        // (Or just play BurstVictoryStrike no matter what. Up to you)

        base.OnBurst_Victory(target, victoryStrikeType);
        yield return null;
    }


    // To alter movement rush behavior, see the PerformAction_() functions.


    // To implement attacks, override a Perform_X_YZ function, where:
    // X = "Grounded" or "Air"
    // Y = "Neutral", "Up" or "Down"
    // Z = "Taunt", "Attack", "Special" or "Super"
    // e.g.
    // protected override void Perform_Grounded_NeutralAttack()

    // NOTE: For grounded neutral attack, use ComboSwingCounter to control the jab combos.


    // To make an attack behave as the critical strike, use this in your specific Perform_X_YZ() attack code:
    /*
    if (SMBZGlobals.Intensity.IsCriticalHitReady(GetMyParticipantDataReference().ParticipantIndex))
    {
        SMBZGlobals.Intensity.UseCriticalStrike(GetMyParticipantDataReference().ParticipantIndex);
        PrepareAnAttack(AttBun_CriticalStrike);
        return;
    }
    */


    // By default, your character has a maximum of 200 energy.
    // To make a super attack use up energy, use this:
    /*
    if (GetMyParticipantDataReference().Energy.GetCurrent() < 100) return;
    GetMyParticipantDataReference().UseEnergy(100);
    PrepareAnAttack(AttBun_MySuperAttack);
    */


    // To set up a Cinematic Rush, create a Begin_Rush() function and override Update_Rush().
    // Normally, a Cinematic Rush deals between 20 - 30 HP damage.
    protected override bool Update_Rush()
    {
        if (!base.Update_Rush())
            return false;

        if (RushProperties.Target == null)
        {
            End_Rush();
            return false;
        }

        if (CurrentAttackData?.OnUpdate != null)
        {
            CurrentAttackData.OnUpdate();
        }

        SMBZGlobals.SetHitStun(RushProperties.Target, 20f);
        SMBZGlobals.SetPreventDrag(RushProperties.Target, true);

        Update_RushRhythmCommandReading(RushProperties);
        if (RushProperties.CinematicWaitTimer > 0f)
        {
            RushProperties.CinematicWaitTimer -= Time.deltaTime;
            return true;
        }

        // Uncomment this if you plan to make a Cinematic Rush where your character
        // takes the opponent very high into the sky or something.
        // This prevents them from being teleported back to the ground after a few seconds
        /*
        CharacterControl t_MyCharacterControl = SMBZGlobals.GetCharacterControl(RushProperties.Target);
        MyCharacterControl.TooFarAwayTimer = 0;
        t_MyCharacterControl.TooFarAwayTimer = 0;
        */

        return true;
    }


    // This function controls your CPU.
    // It's recommended you look at another character's CPU code for reference.
    protected override void Update_CPU_Thoughts()
    {
        base.Update_CPU_Thoughts();

        if (!AI.DeltaData.ShouldContinueWithProcessing)
            return;

        // Mood
        AI.MoodSwitchTimer -= BattleController.instance.UnscaledDeltaTime;
        if (AI.MoodSwitchTimer <= 0)
        {
            var values = Enum.GetValues(typeof(AI_Bundle.Enum_Mood));
            AI.SetMood((AI_Bundle.Enum_Mood)values.GetValue(UnityEngine.Random.Range(0, values.Length)));
            AI.MoodSwitchTimer = AI.GetRethinkCooldown(AI_Bundle.Enum_RethinkCooldownType.Mood);
        }

        // Further CPU code...
    }
}