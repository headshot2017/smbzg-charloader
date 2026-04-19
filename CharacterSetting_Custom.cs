using System.Reflection;
using UnityEngine;
using UnityEngine.UI;

namespace SMBZG.CharacterSelect;

public class CharacterSetting_Custom : CharacterSetting
{
    public Dictionary<string, object> Settings = [];

    public void SetupCustom(UI_Participant participantUI)
    {
        CharacterSetting AdditionalSettings = (CharacterSetting)participantUI.GetType().GetField("AdditionalSettings", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(participantUI);
        GameObject SettingsUI = AdditionalSettings.gameObject;

        // Modify each selectable's navigations
        Transform list = SettingsUI.transform.Find("VerticalList");

        Selectable alternateColors = list.GetChild(0).GetComponentInChildren<Selectable>();
        Selectable afterAlternateColors = alternateColors.navigation.selectOnDown;
        

        for (int i = 0; i < list.childCount; i++)
        {
            Selectable currentItem = list.GetChild(i).GetComponentInChildren<Selectable>();
            Selectable prevItem = (i > 0) ? list.GetChild(i-1).GetComponentInChildren<Selectable>() : null;
            Selectable nextItem = (i < list.childCount - 1) ? list.GetChild(i+1).GetComponentInChildren<Selectable>() : null;

            Navigation nav = currentItem.navigation;
            nav.mode = Navigation.Mode.Explicit;

            // if prevItem == null, this is first item
            if (prevItem)
            {
                Navigation prevNav = prevItem.navigation;
                prevNav.selectOnDown = currentItem;
                nav.selectOnUp = prevItem;
                prevItem.navigation = prevNav;
            }

            if (nextItem)
            {
                Navigation nextNav = nextItem.navigation;
                nextNav.selectOnUp = currentItem;
                nav.selectOnDown = nextItem;
                nextItem.navigation = nextNav;
            }
            else
            {
                // this is the last item
                Navigation afterAltColorsNav = afterAlternateColors.navigation;
                afterAltColorsNav.selectOnUp = currentItem;
                nav.selectOnDown = afterAlternateColors;
                afterAlternateColors.navigation = afterAltColorsNav;
            }
            currentItem.navigation = nav;
        }

        Toggle editAltColors = list.Find("EditAltColors").GetComponentInChildren<Toggle>();
        editAltColors.onValueChanged.RemoveAllListeners();
        editAltColors.onValueChanged.AddListener(delegate {
            MelonLoader.Melon<CharLoader.Core>.Instance.ShowColorEditor(participantUI);
        });
    }
}