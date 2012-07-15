#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/paperDoll/paperDollStatistics.py
import blue
import util
CST_COUNTER_HIGH = 0
CST_COUNTER_LOW = 1
CST_MEMORY = 2
CST_TIME = 3

def CreateOrGetStatistic(name, desc, statType, resetPerFrame):
    stat = blue.statistics.Find(name)
    if not stat:
        stat = blue.CcpStatisticsEntry()
        stat.name = name
        stat.type = statType
        stat.resetPerFrame = resetPerFrame
        stat.description = desc
        blue.statistics.Register(stat)
    return stat


updateCount = CreateOrGetStatistic(name='paperDoll/updateCount', desc='The total number of calls to doll.Update', statType=CST_COUNTER_LOW, resetPerFrame=False)
updateTime = CreateOrGetStatistic(name='paperDoll/updateTime', desc='The time duration of doll.Update', statType=CST_TIME, resetPerFrame=False)
mapsComposited = CreateOrGetStatistic(name='paperDoll/mapsComposited', desc='The total number of composited maps composited', statType=CST_COUNTER_LOW, resetPerFrame=False)
compositeTime = CreateOrGetStatistic(name='paperDoll/compositeTime', desc='The time duration of texture compositing', statType=CST_TIME, resetPerFrame=False)

def Reset():
    updateCount.Set(0)
    updateTime.Set(0)
    mapsComposited.Set(0)
    compositeTime.Set(0)


def GetTimeDiffInSeconds(since):
    return 1e-06 * blue.os.TimeDiffInUs(since, blue.os.GetTime())


exports = util.AutoExports('paperDoll.statistics', globals())