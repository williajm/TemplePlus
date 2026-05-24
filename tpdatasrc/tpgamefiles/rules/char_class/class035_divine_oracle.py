from toee import *
import tpdp
import char_class_utils
import char_editor
###################################################

def GetConditionName():
    return "Divine Oracle"

def GetSpellCasterConditionName():
    return "Divine Oracle Spellcasting"

def GetCategory():
    return "Complete Divine Prestige Classes"

def GetClassDefinitionFlags():
    return CDF_None

def GetClassHelpTopic():
    return "TAG_DIVINE_ORACLES"

classEnum = stat_level_red_avenger # reusing this unused-but-declared enum slot to avoid C++ changes

###################################################


class_feats = {
1: ("Divine Oracle Oracle Domain", "Divine Oracle Scry Bonus",),
2: ("Divine Oracle Prescient Sense", feat_evasion,),
3: ("Divine Oracle Divination Enhancement",),
4: (feat_uncanny_dodge,),
6: (feat_improved_uncanny_dodge,),
10: ("Divine Oracle Immune to Surprise",),
}

class_skills = (skill_concentration, skill_craft, skill_heal, skill_intimidate, skill_knowledge_arcana, skill_knowledge_religion, skill_profession, skill_spellcraft)


def IsEnabled():
    return 1

def GetHitDieType():
    return 6

def GetSkillPtsPerLevel():
    return 2

def GetBabProgression():
    return base_attack_bonus_type_non_martial

def IsFortSaveFavored():
    return 0

def IsRefSaveFavored():
    return 0

def IsWillSaveFavored():
    return 1

# Spell casting
def GetSpellListType():
    return spell_list_type_extender

def GetSpellSourceType():
    return spell_source_type_divine

def IsClassSkill(skillEnum):
    return char_class_utils.IsClassSkill(class_skills, skillEnum)

def IsClassFeat(featEnum):
    return char_class_utils.IsClassFeat(class_feats, featEnum)

def GetClassFeats():
    return class_feats

def IsAlignmentCompatible(alignment):
    return 1

def ObjMeetsPrereqs(obj):
    # Knowledge (religion) 8 ranks
    if obj.skill_ranks_get(skill_knowledge_religion) < 8:
        return 0
    # Skill Focus (Knowledge) - ToEE only has the generic Skill Focus (Knowledge) feat
    if not obj.has_feat(feat_skill_focus_knowledge):
        return 0
    # Able to cast at least 2 divination spells (divine or arcane)
    if obj.divine_spell_level_can_cast() < 1 and obj.arcane_spell_level_can_cast() < 1:
        return 0
    divination_spells_known = 0
    for knSp in obj.spells_known:
        if knSp.spell_level > 0:
            spell_entry = tpdp.SpellEntry(knSp.spell_enum)
            if spell_entry.spell_school_enum == Divination:
                divination_spells_known += 1
                if divination_spells_known >= 2:
                    break
    # Vancian divine casters (cleric/druid) prepare from full list, so granting
    # them the qualification once they have access to 1st level divine spells.
    if divination_spells_known < 2 and obj.divine_spell_level_can_cast() < 1:
        return 0
    return 1


# Levelup

def IsSelectingSpellsOnLevelup(obj, class_extended_1=0):
    if class_extended_1 <= 0:
        class_extended_1 = char_class_utils.GetHighestDivineClass(obj)
    if char_editor.is_selecting_spells(obj, class_extended_1):
        return 1
    return 0


def LevelupCheckSpells(obj, class_extended_1=0):
    if class_extended_1 <= 0:
        class_extended_1 = char_class_utils.GetHighestDivineClass(obj)
    if not char_editor.spells_check_complete(obj, class_extended_1):
        return 0
    return 1


def InitSpellSelection(obj, class_extended_1=0):
    newLvl = obj.stat_level_get(classEnum) + 1
    if newLvl == 1 or class_extended_1 <= 0:
        class_extended_1 = char_class_utils.GetHighestDivineClass(obj)
    char_editor.init_spell_selection(obj, class_extended_1)
    return 0


def LevelupSpellsFinalize(obj, class_extended_1=0):
    if class_extended_1 <= 0:
        class_extended_1 = char_class_utils.GetHighestDivineClass(obj)
    char_editor.spells_finalize(obj, class_extended_1)
    return 0
