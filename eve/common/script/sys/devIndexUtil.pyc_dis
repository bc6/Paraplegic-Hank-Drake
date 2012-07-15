#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/sys/devIndexUtil.py
import util
timeIndexLevels = {1: 7,
 2: 21,
 3: 35,
 4: 65,
 5: 100}
devIndexDecayRate = 100000
devIndexDecayTime = 96

def GetDevIndexLevels():
    totalLevels = 5
    developmentIndexDecayRate = {}
    for indexID in [const.attributeDevIndexMilitary, const.attributeDevIndexIndustrial]:
        nextFloor = 0
        developmentIndexDecayRate[indexID] = {}
        for i in xrange(totalLevels + 1):
            developmentIndexDecayRate[indexID][i] = kv = util.KeyVal(level=i, minLevel=nextFloor, maxLevel=nextFloor + devIndexDecayRate * devIndexDecayTime)
            nextFloor = kv.maxLevel

    for i, (militaryModifier, industrialModifier) in enumerate([(5, 4),
     (2, 2),
     (1, 1),
     (0.75, 0.5),
     (0.5, 0.25),
     (0.25, 0.125)]):
        developmentIndexDecayRate[const.attributeDevIndexMilitary][i].modifier = militaryModifier
        developmentIndexDecayRate[const.attributeDevIndexIndustrial][i].modifier = industrialModifier

    return developmentIndexDecayRate


def GetTimeIndexLevels():
    day = 86400
    ret = []
    for i in xrange(1, 6):
        ret.append(timeIndexLevels[i] * day)

    return ret


def GetTimeIndexLevelForDays(days):
    daysInSeconds = days * 24 * 60
    for level in xrange(5, 0, -1):
        if days >= timeIndexLevels[level]:
            return level

    return 0


exports = {'util.GetDevIndexLevels': GetDevIndexLevels,
 'util.GetTimeIndexLevels': GetTimeIndexLevels,
 'util.GetTimeIndexLevelForDays': GetTimeIndexLevelForDays,
 'util.timeIndexLevels': timeIndexLevels,
 'util.devIndexDecayRate': devIndexDecayRate}