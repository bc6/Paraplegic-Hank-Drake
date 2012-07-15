#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/taleCommon.py
import blue
import util

def CalculateDecayedInfluence(info):
    currentTime = blue.os.GetWallclockTime()
    return CalculateDecayedInfluenceWithTime(info.influence, info.lastUpdated, currentTime, info.decayRate, info.graceTime)


def CalculateDecayedInfluenceWithTime(influence, lastUpdated, currentTime, decayRate, graceTime):
    if decayRate > 0.0 and currentTime - graceTime * const.MIN > lastUpdated:
        timePastGrace = (currentTime - lastUpdated) / const.MIN - graceTime
        hourPast = max(timePastGrace / 60.0, 0.0)
        decay = decayRate * hourPast
        influence = influence - decay
    else:
        influence = influence
    if influence < 0.0001:
        influence = 0.0
    return influence


exports = util.AutoExports('taleCommon', locals())