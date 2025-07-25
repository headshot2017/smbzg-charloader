using System;
using System.Collections.Generic;
using System.Collections;
using System.Reflection;
using UnityEngine;
using SMBZG;
using static SMBZG.BattleCameraManager;

public static class SMBZGlobals
{
    public static AudioSource PlaySound(AudioClip clip, float volume = 1f, bool DestroyAfterPlay = true, float? DestroyAfterTimeOverride = null, float pitch = 1f, bool pauseWithGame = false)
    {
        MethodInfo PlaySoundMethod = typeof(SoundCache).GetMethod("PlaySound", BindingFlags.NonPublic | BindingFlags.Instance, null, new[] { typeof(AudioClip), typeof(float), typeof(bool), typeof(float?), typeof(float), typeof(bool) }, null);
        return (AudioSource)PlaySoundMethod.Invoke(SoundCache.ins, new object[] { clip, volume, DestroyAfterPlay, DestroyAfterTimeOverride, pitch, pauseWithGame });
    }

    public static bool IsThereTwoOrLessPlayersAreAlive()
    {
        MethodInfo IsThereTwoOrLessPlayersAreAlive = typeof(BattleController).GetMethod("IsThereTwoOrLessPlayersAreAlive", BindingFlags.NonPublic | BindingFlags.Instance);
        return (bool)IsThereTwoOrLessPlayersAreAlive.Invoke(BattleController.instance, null);
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
