#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/skillUtil.py
import const
import math
MAXSKILLLEVEL = 5
DIVCONSTANT = math.log(2) * 2.5

def GetSkillPointsPerMinute(primaryAttributeValue, secondaryAttributeValue):
    pointsPerMinute = primaryAttributeValue + secondaryAttributeValue / 2.0
    return pointsPerMinute


def GetSPForLevelRaw(skillTimeConstant, level):
    skillTimeConstant = skillTimeConstant * const.skillPointMultiplier
    if level <= 0:
        return 0
    if level > MAXSKILLLEVEL:
        level = MAXSKILLLEVEL
    ret = skillTimeConstant * 2 ** (2.5 * (level - 1))
    return int(math.ceil(ret))


def GetSkillLevelRaw(skillPoints, skillTimeConstant):
    baseSkillLevelConstant = skillTimeConstant * const.skillPointMultiplier
    if baseSkillLevelConstant > skillPoints:
        return 0
    if baseSkillLevelConstant == 0:
        return 0
    return min(int(math.log(skillPoints / baseSkillLevelConstant) / DIVCONSTANT) + 1, MAXSKILLLEVEL)


exports = {'skillUtil.GetSkillPointsPerMinute': GetSkillPointsPerMinute,
 'skillUtil.GetSPForLevelRaw': GetSPForLevelRaw,
 'skillUtil.GetSkillLevelRaw': GetSkillLevelRaw,
 'skillUtil.MAXSKILLLEVEL': MAXSKILLLEVEL}