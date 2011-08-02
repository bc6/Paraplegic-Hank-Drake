import util
import trinity
import planet
import uix
import math
import mathUtil
import uiutil
import planetCommon
import log
import blue
PLANET_ZOOM_MAX = 4000.0
PLANET_ZOOM_MIN = 1150.0
PLANET_SCALE = 1000.0
PLANET_TEXTURE_SIZE = 2048
PLANET_RESOURCE_TEX_WIDTH = 2048
PLANET_RESOURCE_TEX_HEIGHT = 1024
PLANET_HEATMAP_COLORS = ((0, 0, 0.5, 0.5),
 (0, 0, 1, 1),
 (0, 0.5, 1, 1),
 (0, 1, 1, 1),
 (0, 1, 0.5, 1),
 (0, 1, 0, 1),
 (0.5, 1, 0, 1),
 (1, 1, 0, 1),
 (1, 0.5, 0, 1),
 (1, 0, 0, 1))
PLANET_COLOR_POWER = (236 / 255.0, 28 / 255.0, 36 / 255.0)
PLANET_COLOR_CPU = (0.0, 255 / 255.0, 212 / 255.0)
PLANET_COLOR_CYCLE = (1.0, 1.0, 1.0)
PLANET_COLOR_BANDWIDTH = (1.0, 1.0, 1.0)
PLANET_COLOR_LINKEDITMODE = (255 / 255.0,
 205 / 255.0,
 0.0,
 1.0)
PLANET_COLOR_PINEDITMODE = (255 / 255.0, 205 / 255.0, 0.0)
PLANET_COLOR_STORAGE = (10 / 255.0,
 67 / 255.0,
 102 / 255.0,
 1.0)
PLANET_COLOR_EXTRACTOR = (0 / 255.0,
 153 / 255.0,
 153 / 255.0,
 1.0)
PLANET_COLOR_PROCESSOR = (178 / 255.0,
 98 / 255.0,
 45 / 255.0,
 1.0)
PLANET_COLOR_CURRLEVEL = (0.247, 0.745, 0.165, 1.0)
PLANET_COLOR_UPGRADELEVEL = (0.271, 0.494, 0.137, 1.0)
PLANET_COLOR_POWERUPGRADE = (0.671, 0.047, 0.071, 1.0)
PLANET_COLOR_CPUUPGRADE = (0.278, 0.655, 0.592, 1.0)
PLANET_COLOR_EXTRACTIONLINK = (0.4, 1.0, 1.0, 1.0)
PLANET_COLOR_USED_STORAGE = (0 / 255.0, 169 / 255.0, 244 / 255.0)
PLANET_COLOR_USED_PROCESSOR = (237 / 255.0, 153 / 255.0, 53 / 255.0)
PLANET_COLOR_ICON_COMMANDCENTER = (171 / 255.0, 243 / 255.0, 255 / 255.0)
PLANET_COLOR_ICON_STORAGE = (2 / 255.0, 106 / 255.0, 147 / 255.0)
PLANET_COLOR_ICON_SPACEPORT = (3 / 255.0, 178 / 255.0, 239 / 255.0)
PLANET_COLOR_ICON_EXTRACTOR = (48 / 255.0, 239 / 255.0, 216 / 255.0)
PLANET_COLOR_ICON_PROCESSOR = (237 / 255.0, 153 / 255.0, 53 / 255.0)
PINTYPE_NOPICK = 0
PINTYPE_NORMAL = 1
PINTYPE_NORMALEDIT = 2
PINTYPE_EXTRACTIONHEAD = 3
PINTYPE_OTHERS = 4
PINTYPE_DEPLETION = 5
PLANET_2PI = math.pi * 2
PLANET_PI_DIV_2 = math.pi / 2
PLANET_COMMANDCENTERMAXLEVEL = 5
DARKPLANETS = (const.typePlanetPlasma, const.typePlanetLava, const.typePlanetSandstorm)

def GetContrastColorForCurrPlanet():
    if not sm.GetService('planetUI').IsOpen():
        return None
    else:
        planetTypeID = sm.GetService('planetUI').planet.planetTypeID
        if planetTypeID in DARKPLANETS:
            return util.Color.WHITE
        return util.Color.BLACK



def GetPickIntersectionPoint(x = None, y = None):
    if None in (x, y):
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
    device = trinity.GetDevice()
    (proj, view, vp,) = uix.GetFullscreenProjectionViewAndViewport()
    (ray, start,) = device.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
    lineVec = trinity.TriVector(ray.x, ray.y, ray.z)
    lineP0 = trinity.TriVector(start.x, start.y, start.z)
    sphereP0 = trinity.TriVector(0.0, 0.0, 0.0)
    sphereRad = 1000.0
    pInt = GetSphereLineIntersectionPoint(lineP0, lineVec, sphereP0, sphereRad)
    if not pInt:
        return 
    ret = planet.SurfacePoint(pInt.x, pInt.y, pInt.z)
    ret.SetRadius(1.0)
    return ret



def GetSphereLineIntersectionPoint(lineP0, lineVec, sphereP0, sphereRad):
    a = 1
    b = (lineVec * 2).DotProduct(lineP0 - sphereP0)
    c = (lineP0 - sphereP0).Length() ** 2 - sphereRad ** 2
    d = b ** 2.0 - 4.0 * a * c
    if d < 0:
        return None
    else:
        if d == 0:
            t = -b / (2 * a)
            return lineP0 + lineVec * t / lineVec.Length()
        d = math.sqrt(d)
        t1 = (-b + d) / (2 * a)
        t2 = (-b - d) / (2 * a)
        lineLength = lineVec.Length()
        P1 = lineP0 + lineVec * t1 / lineLength
        P2 = lineP0 + lineVec * t2 / lineLength
        l1 = (lineP0 - P1).LengthSq()
        l2 = (lineP0 - P2).LengthSq()
        if l1 < l2:
            return P1
        return P2



def NormalizeLatitude(angle):
    while angle < -PLANET_PI_DIV_2:
        angle += math.pi

    while angle > PLANET_PI_DIV_2:
        angle -= math.pi

    return angle



def NormalizeLongitude(angle):
    while angle <= -math.pi:
        angle += PLANET_2PI

    while angle > math.pi:
        angle -= PLANET_2PI

    return angle



def FmtGeoCoordinates(latitude, longitude):
    latitude = mathUtil.RadToDeg(NormalizeLatitude(latitude))
    longitude = mathUtil.RadToDeg(NormalizeLongitude(longitude))
    (d1, m1, s1,) = ConvertToDMS(latitude)
    (d2, m2, s2,) = ConvertToDMS(longitude)
    dir1 = 'N' if d1 >= 0 else 'S'
    dir2 = 'E' if d2 >= 0 else 'W'
    return "%d\xb0 %d' %d'' %s, %d\xb0 %d' %d'' %s" % (d1,
     m1,
     s1,
     dir1,
     d2,
     m2,
     s2,
     dir2)



def ConvertToDMS(value):
    degrees = int(value)
    minPart = abs(value - degrees)
    secPart = minPart - int(minPart)
    return (degrees, int(minPart * 60), int(round(secPart * 60)))



def GetPinCycleInfo(pin, cycleTime = None):
    if cycleTime is None:
        cycleTime = pin.GetCycleTime()
    if pin.IsActive() and not pin.IsInEditMode():
        currCycle = min(blue.os.GetTime() - pin.lastRunTime, cycleTime)
        currCycleProportion = currCycle / float(cycleTime)
    else:
        currCycle = currCycleProportion = 0
    if cycleTime is None:
        cycleText = mls.UI_GENERIC_INACTIVE
    else:
        cycleText = '%s / %s' % (util.FmtTime(currCycle), util.FmtTime(cycleTime))
    return (cycleText, currCycleProportion)



def GetSchematicData(processorTypeID):
    schematicsData = cfg.schematicsByPin[processorTypeID]
    if len(schematicsData) == 0:
        log.LogTraceback('Authoring error: No schematics found for processor pin with typeID %s' % processorTypeID)
    schematics = []
    for s in schematicsData:
        try:
            schematic = cfg.schematics.Get(s.schematicID)
        except:
            log.LogTraceback('Authoring error: No schematic found with id=%s' % s.schematicID)
            raise 
        (inputs, outputs,) = _GetSchematicInputsAndOutputs(schematic.schematicID)
        outputsDict = {}
        for o in outputs:
            outputsDict[o.typeID] = o.quantity

        volumePerCycle = planetCommon.GetCommodityTotalVolume(outputsDict)
        volumePerHour = planetCommon.GetBandwidth(volumePerCycle, schematic.cycleTime * SEC)
        sData = util.KeyVal(name=schematic.schematicName, schematicID=schematic.schematicID, cycleTime=schematic.cycleTime, outputs=outputs, inputs=inputs, outputVolume=volumePerHour)
        schematics.append((sData.name, sData))

    return uiutil.SortListOfTuples(schematics)



def _GetSchematicInputsAndOutputs(schematicID):
    inputs = []
    outputs = []
    schematicstypemap = cfg.schematicstypemap[schematicID]
    if len(schematicstypemap) == 0:
        log.LogTraceback('Authoring error: No inputs/outputs defined for schematic with id=%s' % schematicID)
    for typeInfo in schematicstypemap:
        data = util.KeyVal(name=cfg.invtypes.Get(typeInfo.typeID).typeName, typeID=typeInfo.typeID, quantity=typeInfo.quantity)
        if typeInfo.isInput:
            inputs.append(data)
        else:
            outputs.append(data)

    return (inputs, outputs)



def GetSchematicDataByGroupID():
    schematics = GetSchematicData()
    ret = {}
    for schematic in schematics:
        groupID = cfg.invtypes.Get(schematic.output.typeID).groupID
        if groupID not in ret:
            ret[groupID] = []
        ret[groupID].append(schematic)

    return ret



def PinHasBeenBuilt(pinID):
    if isinstance(pinID, tuple):
        return False
    return True


exports = util.AutoExports('planetCommon', locals())

