from templeplus.pymod import PythonModifier
from toee import *
import tpdp
import char_class_utils

###################################################

def GetConditionName():
    return "Divine Oracle"

def GetSpellCasterConditionName():
    return "Divine Oracle Spellcasting"

print "Registering " + GetConditionName()

classEnum = stat_level_divine_oracle
classSpecModule = __import__('class050_divine_oracle')

###################################################


#### standard callbacks - BAB and Save values
def OnGetToHitBonusBase(attachee, args, evt_obj):
    classLvl = attachee.stat_level_get(classEnum)
    babvalue = game.get_bab_for_class(classEnum, classLvl)
    evt_obj.bonus_list.add(babvalue, 0, 137) # untyped, description: "Class"
    return 0

def OnGetSaveThrowFort(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Fortitude)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

def OnGetSaveThrowReflex(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Reflex)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

def OnGetSaveThrowWill(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Will)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

classSpecObj = PythonModifier(GetConditionName(), 0)
classSpecObj.AddHook(ET_OnToHitBonusBase, EK_NONE, OnGetToHitBonusBase, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_FORTITUDE, OnGetSaveThrowFort, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_REFLEX, OnGetSaveThrowReflex, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_WILL, OnGetSaveThrowWill, ())


##### Spell casting
# Divine Oracle raises the caster level for the divine base class specified in Modifier arg 0

def OnAddSpellCasting(attachee, args, evt_obj):
    if args.get_arg(0) == 0:
        args.set_arg(0, char_class_utils.GetHighestDivineClass(attachee))
    return 0

def OnGetBaseCasterLevel(attachee, args, evt_obj):
    class_extended_1 = args.get_arg(0)
    class_code = evt_obj.arg0
    if class_code != class_extended_1:
        if evt_obj.arg1 == 0:
            return 0
    classLvl = attachee.stat_level_get(classEnum)
    if classLvl == 0:
        return 0
    evt_obj.bonus_list.add(classLvl, 0, 137)
    return 0

def OnSpellListExtensionGet(attachee, args, evt_obj):
    class_extended_1 = args.get_arg(0)
    class_code = evt_obj.arg0
    if class_code != class_extended_1:
        if evt_obj.arg1 == 0:
            return 0
    classLvl = attachee.stat_level_get(classEnum)
    if classLvl == 0:
        return 0
    evt_obj.bonus_list.add(classLvl, 0, 137)
    return 0

def OnInitLevelupSpellSelection(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    classSpecModule.InitSpellSelection(attachee, class_extended_1)
    return 0

def OnLevelupSpellsCheckComplete(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    if not classSpecModule.LevelupCheckSpells(attachee, class_extended_1):
        evt_obj.bonus_list.add(-1, 0, 137)
    return 1

def OnLevelupSpellsFinalize(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    classSpecModule.LevelupSpellsFinalize(attachee, class_extended_1)
    return

spellCasterSpecObj = PythonModifier(GetSpellCasterConditionName(), 8)
spellCasterSpecObj.AddHook(ET_OnConditionAdd, EK_NONE, OnAddSpellCasting, ())
spellCasterSpecObj.AddHook(ET_OnGetBaseCasterLevel, EK_NONE, OnGetBaseCasterLevel, ())
spellCasterSpecObj.AddHook(ET_OnSpellListExtensionGet, EK_NONE, OnSpellListExtensionGet, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Activate, OnInitLevelupSpellSelection, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Check_Complete, OnLevelupSpellsCheckComplete, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Finalize, OnLevelupSpellsFinalize, ())


#### Divine Oracle Class Features ####

## Scry Bonus (Su) ##
# +1 sacred bonus to the save DC of all Divination (Scrying) spells.
def ScryBonusOnGetSpellDcMod(attachee, args, evt_obj):
    spell_entry = evt_obj.spell_entry
    if spell_entry.spell_school_enum != Divination:
        return 0
    if spell_entry.spell_subschool_enum != Scrying:
        return 0
    evt_obj.bonus_list.add(1, 17, "Divine Oracle Scry Bonus") # Sacred bonus
    return 0

scryBonus = PythonModifier("Divine Oracle Scry Bonus", 0)
scryBonus.MapToFeat("Divine Oracle Scry Bonus")
scryBonus.AddHook(ET_OnGetSpellDcMod, EK_NONE, ScryBonusOnGetSpellDcMod, ())


## Oracle Domain ##
# Grants the Oracle domain granted power: cast Divination spells at +2 caster level.
def OracleDomainCasterLevelMod(attachee, args, evt_obj):
    spellPkt = evt_obj.get_spell_packet()
    if spellPkt is None:
        return 0
    spell_enum = spellPkt.spell_enum
    if spell_enum <= 0:
        return 0
    spell_entry = tpdp.SpellEntry(spell_enum)
    if spell_entry.spell_school_enum != Divination:
        return 0
    evt_obj.return_val += 2
    return 0

oracleDomain = PythonModifier("Divine Oracle Oracle Domain", 0)
oracleDomain.MapToFeat("Divine Oracle Oracle Domain")
oracleDomain.AddHook(ET_OnGetCasterLevelMod, EK_NONE, OracleDomainCasterLevelMod, ())


## Prescient Sense (Ex) ##
# Marker feat. Mechanical effect is granted via feat_evasion in the class spec
# class_feats dict at level 2. Listed here so the feature appears on the sheet.
prescientSense = PythonModifier("Divine Oracle Prescient Sense", 0)
prescientSense.MapToFeat("Divine Oracle Prescient Sense")


## Divination Enhancement (Ex) ##
# Roll twice and take the better result when casting divination spells such as
# augury or divination. ToEE has no engine support for re-rolling such spell
# outcomes, so the feature is registered as a marker.
divinationEnhancement = PythonModifier("Divine Oracle Divination Enhancement", 0)
divinationEnhancement.MapToFeat("Divine Oracle Divination Enhancement")


## Immune to Surprise (Ex) ##
# Marker feat for the character sheet. Mechanical effect is implemented in
# C++ at TurnBasedSys add-to-initiative time: Divine Oracle 10+ characters
# skip the engine "Surprised" condition entirely (turn_based.cpp).
immuneSurprise = PythonModifier("Divine Oracle Immune to Surprise", 0)
immuneSurprise.MapToFeat("Divine Oracle Immune to Surprise")
