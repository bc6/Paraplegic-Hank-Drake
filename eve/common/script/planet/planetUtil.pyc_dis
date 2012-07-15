#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/planet/planetUtil.py
import util
import math
MATH_2PI = math.pi * 2
MATH_PI_DIV_2 = math.pi * 0.5

def IterCorrectedScanGrid(latitude, longitude, radius, numSamplesPerAxis):
    diameter = 2 * radius
    hasPole = True
    if latitude - radius < 0.0 or diameter / math.cos(latitude - radius - MATH_PI_DIV_2) > MATH_2PI:
        minLatitude, maxLatitude = 0.0, latitude + radius
        minLongitude, maxLongitude = 0.0, MATH_2PI
    elif latitude + radius > math.pi or diameter / math.cos(latitude + radius - MATH_PI_DIV_2) > MATH_2PI:
        minLatitude, maxLatitude = latitude - radius, math.pi
        minLongitude, maxLongitude = 0.0, MATH_2PI
    else:
        minLatitude, maxLatitude = latitude - radius, latitude + radius
        minLongitude, maxLongitude = longitude - radius, longitude + radius
        hasPole = False
    latitudeStepSize = (maxLatitude - minLatitude) / (numSamplesPerAxis - 1)
    longitudeStepSize = (maxLongitude - minLongitude) / (numSamplesPerAxis - 1)
    _latitude = 0
    for x in xrange(numSamplesPerAxis):
        _latitude = minLatitude + x * latitudeStepSize
        for y in xrange(numSamplesPerAxis):
            if hasPole:
                _longitude = minLongitude + y * longitudeStepSize
            else:
                tempDiameter = diameter / math.cos(_latitude - MATH_PI_DIV_2)
                tempStepSize = 1.0 / (numSamplesPerAxis - 1) * tempDiameter
                _longitude = longitude - tempDiameter * 0.5 + y * tempStepSize
            yield (_latitude, _longitude)


exports = util.AutoExports('planetUtil', locals())