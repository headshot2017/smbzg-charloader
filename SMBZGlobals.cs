using System;
using System.Collections.Generic;
using System.Collections;
using System.Reflection;
using UnityEngine;
using SMBZG;
using static SMBZG.BattleCameraManager;

public static class SMBZGlobals
{
    [Obsolete("SMBZGlobals.PlaySound() is obsolete. Use SoundCache.ins.PlaySound() instead.")]
    public static AudioSource PlaySound(AudioClip clip, float volume = 1f, bool DestroyAfterPlay = true, float? DestroyAfterTimeOverride = null, float pitch = 1f, bool pauseWithGame = false)
    {
        return SoundCache.ins.PlaySound(clip, volume, DestroyAfterPlay, DestroyAfterTimeOverride, pitch, pauseWithGame);
    }

    public static bool IsCustomCharacter(BaseCharacter character)
    {
        return (character.GetType().IsSubclassOf(typeof(CustomBaseCharacter)) || character.GetType() == typeof(CustomBaseCharacter));
    }

    public static BaseCharacter.PlayerStateENUM GetPlayerState(BaseCharacter character)
    {
        return (BaseCharacter.PlayerStateENUM)character.GetType().GetField("PlayerState", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetPlayerState(BaseCharacter character, BaseCharacter.PlayerStateENUM state)
    {
        character.GetType().GetField("PlayerState", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, state);
    }

    public static CharacterControl GetCharacterControl(BaseCharacter character)
    {
        return (CharacterControl)character.GetType().GetField("MyCharacterControl", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static bool GetIsNPC(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("IsNPC", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static bool GetIsCPU(BaseCharacter character)
    {
        return (bool)character.GetType().GetProperty("IsCPUControlled", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static float GetHitStun(BaseCharacter character)
    {
        return (float)character.GetType().GetProperty("HitStun", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetHitStun(BaseCharacter character, float value)
    {
        character.GetType().GetProperty("HitStun", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, value);
    }

    public static float? GetDragOverride(BaseCharacter character)
    {
        return (float?)character.GetType().GetField("DragOverride", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetDragOverride(BaseCharacter character, float? value)
    {
        character.GetType().GetField("DragOverride", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, value);
    }

    public static bool GetIsRushing(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("IsRushing", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static bool GetIsBursting(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("IsBursting", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static bool GetIsIntangible(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("IsIntangible", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetIsIntangible(BaseCharacter character, bool value)
    {
        character.GetType().GetField("IsIntangible", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, value);
    }

    public static bool GetIsFacingRight(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetIsFacingRight(BaseCharacter character, bool value)
    {
        character.GetType().GetField("IsFacingRight", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, value);
    }

    public static bool GetPreventDrag(BaseCharacter character)
    {
        return (bool)character.GetType().GetField("PreventDrag", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(character);
    }

    public static void SetPreventDrag(BaseCharacter character, bool value)
    {
        character.GetType().GetField("PreventDrag", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(character, value);
    }

    public static bool IsThereTwoOrLessPlayersAreAlive()
    {
        return ActiveCharacterControlList.Count((CharacterControl c) => c.ParticipantDataReference.Health.GetCurrent() > 0f) <= 2;
    }

    public static bool IsThereMoreThanTwoPlayersAreAlive()
    {
        return ActiveCharacterControlList.Count((CharacterControl c) => c.ParticipantDataReference.Health.GetCurrent() > 0f) > 2;
    }

    public static bool IsThereMoreThanTwoPlayersInThisBattle()
    {
        return ActiveCharacterControlList.Count > 2;
    }

    public static ClashAndBurstManager ClashAndBurstManager =>
        (ClashAndBurstManager)typeof(BattleController).GetField("ClashAndBurstManager", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static MovementRushManager MovementRushManager =>
        (MovementRushManager)typeof(BattleController).GetField("MovementRushManager", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static BattleCameraManager CameraManager =>
        (BattleCameraManager)typeof(BattleController).GetField("CameraManager", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(BattleController.instance);

    public static CameraSettingsDataStore CameraSettings =>
        (CameraSettingsDataStore)typeof(BattleCameraManager).GetField("Settings", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(CameraManager);

    public static BattleBackgroundManager BackgroundManager =>
        (BattleBackgroundManager)typeof(BattleController).GetField("BackgroundManager", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(BattleController.instance);

    public static BattleBackgroundData ActiveBattleBackgroundData =>
        (BattleBackgroundData)typeof(BattleBackgroundManager).GetField("ActiveBattleBackgroundData", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(BackgroundManager);

    public static IntensityDataStore Intensity =>
        (IntensityDataStore)typeof(BattleController).GetField("Intensity", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(BattleController.instance);

    public static List<CharacterControl> ActiveCharacterControlList =>
        (List<CharacterControl>)typeof(BattleController).GetField("ActiveCharacterControlList", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static BattleController.BattleStateENUM BattleState =>
        (BattleController.BattleStateENUM)typeof(BattleController).GetField("BattleState", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static bool IsPaused => 
        (bool)typeof(BattleController).GetField("IsPaused", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static bool IsSetup =>
        (bool)typeof(BattleController).GetField("IsSetup", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static bool BattleHasBegun =>
        (bool)typeof(BattleController).GetField("BattleHasBegun", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);

    public static bool SomeoneHasDied =>
        (bool)typeof(BattleController).GetField("SomeoneHasDied", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(BattleController.instance);
}
