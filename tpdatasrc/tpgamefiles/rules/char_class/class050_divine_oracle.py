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

classEnum = stat_level_divine_oracle

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
    # The class advances DIVINE spellcasting (all progression hooks bind to
    # GetHighestDivineClass), so require divine casting -- an arcane-only caster
    # could otherwise meet the prereq but gain no spellcasting progression.
    if obj.divine_spell_level_can_cast() < 1:
        return 0
    # "Able to cast at least 2 divination spells." The requirement is character
    # -wide, so count distinct castable divinations across ALL of the
    # character's divine casting classes (a multiclass caster may satisfy it
    # from any one of them).
    divine_classes = (stat_level_cleric, stat_level_druid, stat_level_paladin,
                      stat_level_ranger, stat_level_blackguard, stat_level_favored_soul)
    divinations = set()
    for cls in divine_classes:
        cls_lvl = obj.stat_level_get(cls)
        if cls_lvl < 1:
            continue
        # Cleric/druid prepare from the full divine list, which always contains
        # well over two divinations -- they qualify outright.
        if cls == stat_level_cleric or cls == stat_level_druid:
            return 1
        # Spontaneous casters (Favored Soul) cast only what they know; prepared
        # casters with a limited list (paladin/ranger/blackguard) cast their
        # whole available class list, each up to its OWN max spell level.
        if cls == stat_level_favored_soul:
            class_spells = obj.spells_known
        else:
            max_lvl = char_editor.get_max_spell_level(obj, cls, cls_lvl)
            if max_lvl < 1:
                continue
            class_spells = char_editor.get_learnable_spells(obj, cls, max_lvl)
        for sp in class_spells:
            if sp.spell_level > 0 and tpdp.SpellEntry(sp.spell_enum).spell_school_enum == Divination:
                divinations.add(sp.spell_enum)
                if len(divinations) >= 2:
                    return 1
    return 0


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
