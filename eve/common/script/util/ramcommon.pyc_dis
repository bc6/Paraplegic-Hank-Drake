#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/ramcommon.py
import util
import blue
import random
METALEVEL_OUTPUT = 5
jumpsPerSkillLevel = {0: -1,
 1: 0,
 2: 5,
 3: 10,
 4: 20,
 5: 50}
SECOND = 10000000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
BASE_INVENTION_ME = -4.0
BASE_INVENTION_PE = -4.0

def SelectRandomFromArray(arr):
    if arr == []:
        return None
    num = int(random.random() * len(arr))
    return arr[min(num, len(arr) - 1)]


def GetActualManufacturingTimeForBlueprintEx(bpt, bpi):
    time = bpt.productionTime
    if bpi is not None and bpi.productivityLevel > 0:
        time = time - (1.0 - 1.0 / (1 + bpi.productivityLevel)) * bpt.productivityModifier
    return int(time)


def GetActualWastageFactorAsPercentageForBlueprintEx(bpt, bpi):
    res = 0.0
    res = bpt.wasteFactor / 100.0
    if bpi is not None and bpi.materialLevel and bpt.wasteFactor > 0:
        w = bpt.wasteFactor / 100.0
        m = bpi.materialLevel
        if bpi.materialLevel < 0:
            res = w * -(-1.0 + m)
        else:
            res = w * (1.0 / (1.0 + m))
    if res < 0:
        res = 0
    return float(res)


exports = util.AutoExports('ramcommon', locals())