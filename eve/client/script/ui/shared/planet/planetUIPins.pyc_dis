#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/planetUIPins.py
import uiconst
import util
import math
import trinity
import uicls
import planet
import blue
import uthread
import geo2
import uiutil
import uix
from service import ROLE_GML, ROLE_GMH
import planetCommon
import random
import localization
RADIUS_PIN = 0.006
RADIUS_PINEXTENDED = RADIUS_PIN * 1.65
RADIUS_CYCLE = RADIUS_PIN * 0.7
RADIUS_CYCLEEXTENDED = RADIUS_PIN * 1.25
RADIUS_LOGO = RADIUS_PIN * 0.5
RADIUS_SHADOW = RADIUS_PIN * 1.2
RADIUS_SHADOWEXTENDED = RADIUS_PINEXTENDED * 1.2
RADIUS_BUILDPIN = RADIUS_PIN * 0.8
RADIUS_PINOTHERS = RADIUS_PIN * 0.5
RADIUS_EXTRACTIONHEAD = 0.003
SCALE_PINBASE = 1.01
SCALE_PINLIFTED = 1.0105
SCALE_ONGROUND = 1.001
SCALE_PINOTHERS = 1.005
PINCOLORS = {const.groupCommandPins: planetCommon.PLANET_COLOR_ICON_COMMANDCENTER,
 const.groupExtractorPins: planetCommon.PLANET_COLOR_ICON_EXTRACTOR,
 const.groupStoragePins: planetCommon.PLANET_COLOR_ICON_STORAGE,
 const.groupSpaceportPins: planetCommon.PLANET_COLOR_ICON_SPACEPORT,
 const.groupProcessPins: planetCommon.PLANET_COLOR_ICON_PROCESSOR,
 const.groupExtractionControlUnitPins: planetCommon.PLANET_COLOR_ICON_EXTRACTOR}
PINICONPATHS = {const.groupCommandPins: 'res:/UI/Texture/Planet/command.dds',
 const.groupExtractorPins: 'res:/UI/Texture/Planet/extractor.dds',
 const.groupStoragePins: 'res:/UI/Texture/Planet/storage.dds',
 const.groupSpaceportPins: 'res:/UI/Texture/Planet/spaceport.dds',
 const.groupProcessPins: 'res:/UI/Texture/Planet/process.dds',
 const.groupExtractionControlUnitPins: 'res:/UI/Texture/Planet/extractor.dds'}

class SpherePinStack():
    __guid__ = 'planet.ui.SpherePinStack'

    def __init__(self, surfacePoint, maxRadius):
        self.spherePins = []
        self.transformsBySpherePins = {}
        self.surfacePoint = surfacePoint
        self.maxRadius = maxRadius
        self.rotateThread = None
        self.destroyed = False
        self.model3D = None

    def CreateSpherePin(self, textureName, layer, radius, transform, isGauge = False, scale = 1.01, color = util.Color.WHITE, display = True, offsetScale = 1.0, xOffset = 0.0, yOffset = 0.0, maxRadius = None):
        if isGauge:
            shaderName = 'res:/Graphics/Effect/Managed/Space/UI/SpherePinThreshold.fx'
        else:
            shaderName = 'res:/Graphics/Effect/Managed/Space/UI/SpherePin1.fx'
        sp = trinity.EveSpherePin()
        transform.children.append(sp)
        self.spherePins.append(sp)
        self.transformsBySpherePins[sp] = transform
        sp.pinEffectResPath = shaderName
        sp.pinRadius = radius
        sp.pinMaxRadius = maxRadius or self.maxRadius
        sp.centerNormal = self.surfacePoint.GetAsXYZTuple()
        sp.scaling = (scale, scale, scale)
        sp.display = display
        sp.sortValueMultiplier = 1.0 - 0.01 * layer - 0.1 * scale
        sp.uvAtlasScaleOffset = (offsetScale,
         offsetScale,
         xOffset,
         yOffset)
        sm.GetService('planetUI').LoadSpherePinResources(sp, textureName)
        sp.pinColor = color
        return sp

    def CreateIconSpherePin(self, layer, radius, transform, typeID, scale = 1.01, color = util.Color.WHITE):
        invtype = cfg.invtypes.Get(typeID)
        iconFile = invtype.Icon().iconFile
        path = uicls.Icon.ConvertIconNoToResPath(None, iconFile)
        return self.CreateSpherePin(textureName=path, layer=layer, radius=radius, transform=transform, scale=scale, color=color, offsetScale=1.0, xOffset=0.0, yOffset=0.0)

    def SetLocation(self, surfacePoint):
        self.surfacePoint.Copy(surfacePoint)
        for spherePin in self.spherePins:
            centerNormal = self.surfacePoint.GetAsXYZTuple()
            spherePin.centerNormal = centerNormal

    def Remove(self):
        self.destroyed = True
        for spherePin, transform in self.transformsBySpherePins.iteritems():
            if spherePin in transform.children:
                transform.children.remove(spherePin)

        self.Hide3dModel()

    def RemoveSpherePin(self, spherePin):
        if self.destroyed:
            return
        transform = self.transformsBySpherePins.pop(spherePin)
        transform.children.remove(spherePin)

    def Show3DModel(self):
        if not self.model3D:
            return
        SCALE = 0.025
        EXT = 1.026
        self.model3D.scaling = (SCALE, SCALE, SCALE)
        self.model3D.sortValueMultiplier = 0.5
        self.model3D.translation = (EXT * self.surfacePoint.x, EXT * self.surfacePoint.y, EXT * self.surfacePoint.z)
        self.transform.children.append(self.model3D)
        self.rotateThread = uthread.new(self._Rotate3dModel)

    def _Rotate3dModel(self):
        t = 0.0
        plnSurfRotMat = geo2.MatrixRotationAxis(geo2.Vec3Cross(geo2.Vec3Normalize(self.surfacePoint.GetAsXYZTuple()), (0.0, 1.0, 0.0)), -math.acos(geo2.Vec3Dot(geo2.Vec3Normalize(self.surfacePoint.GetAsXYZTuple()), (0.0, 1.0, 0.0))))
        while True:
            if self.model3D:
                t += 0.5 / blue.os.fps
                zRotMat = geo2.MatrixRotationAxis((0.0, 1.0, 0.0), -t)
                rotation = geo2.MatrixMultiply(zRotMat, plnSurfRotMat)
                rotQuat = geo2.QuaternionRotationMatrix(rotation)
                self.model3D.rotation = rotQuat
            blue.pyos.synchro.Yield()

    def Hide3dModel(self):
        if not self.model3D:
            return
        if self.model3D in self.transform.children:
            self.transform.children.remove(self.model3D)
        if self.rotateThread is not None:
            self.rotateThread.kill()
            self.rotateThread = None


class BasePlanetPin(SpherePinStack):
    __guid__ = 'planet.ui.BasePlanetPin'
    __notifyevents__ = ['ProcessColonyDataSet']
    baseColor = planetCommon.PLANET_COLOR_STORAGE

    def __init__(self, surfacePoint, pin, transform, maxRadius = RADIUS_PINEXTENDED):
        SpherePinStack.__init__(self, surfacePoint, maxRadius)
        sm.RegisterNotify(self)
        self.renderState = util.KeyVal(mouseHover=False, asRoute=False, selected=False)
        self.pin = pin
        self.spherePins = []
        self.model3D = self.Get3DModel()
        self.firstCycle = True
        self.lastCycleProportion = 0.0
        self.producerCycleTime = 0.0
        self.transform = transform
        self.resourceIcons = []
        self.zoom = sm.GetService('planetUI').zoom
        typeObj = cfg.invtypes.Get(pin.typeID)
        pinIconPath = PINICONPATHS[typeObj.groupID]
        self.border = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base_y.dds', layer=0, radius=RADIUS_PINEXTENDED, transform=transform, scale=SCALE_PINBASE, color=(0.0, 0.0, 0.0, 0.0))
        self.border.display = False
        self.logo = self.CreateSpherePin(textureName=pinIconPath, layer=2, radius=RADIUS_LOGO, transform=transform, scale=SCALE_PINBASE, color=PINCOLORS[typeObj.groupID])
        self.mainPin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=1, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINBASE, color=(0.0, 0.0, 0.0, 0.4))
        self.gaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=3, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, color=self.baseColor)
        self.gauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=4, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_USED_STORAGE)
        self.cycle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/cycle_10px.dds', layer=5, radius=RADIUS_CYCLE, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_CYCLE)
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=0, radius=RADIUS_SHADOW, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.3))
        self.SetResourceIcons()
        self.pinExpansions = [(self.mainPin, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.gauge, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.gaugeUnderlay, RADIUS_PIN, RADIUS_PINEXTENDED),
         (self.cycle, RADIUS_CYCLE, RADIUS_CYCLEEXTENDED),
         (self.shadow, RADIUS_SHADOW, RADIUS_SHADOWEXTENDED)]
        self.AssignIDsToPins()
        self.UpdateStorageGauge()
        self.UpdateEditModeColors()
        uthread.new(self.UpdateCycleTimer)
        uthread.new(self.UpdateResourceIcons)

    def SetResourceIcons(self):
        return
        for sp in self.resourceIcons:
            self.RemoveSpherePin(sp)

        self.resourceIcons = []
        if self.pin.IsStorage():
            typeIDs = self.pin.GetContents().keys()
        elif self.pin.IsExtractor() and self.pin.IsActive():
            typeIDs = self.pin.GetProducts().keys()
        elif self.pin.IsProcessor():
            typeIDs = self.pin.GetProducts().keys()
        else:
            typeIDs = []
        for typeID in typeIDs:
            resourceIcon = self.CreateIconSpherePin(layer=10, radius=RADIUS_PIN, transform=self.transform, scale=SCALE_PINLIFTED * 1.01, typeID=typeID)
            resourceIcon.name = self.mainPin.name
            self.resourceIcons.append(resourceIcon)

        self.SetResourceIconAppearance()

    def SetResourceIconAppearance(self):
        return
        for pin in self.resourceIcons:
            pin.pinColor = (1.0,
             1.0,
             1.0,
             0.8 * (1.0 - self.zoom) ** 1.0)

    def UpdateResourceIcons(self):
        t = 0.0
        cycleTimeBase = 4.0
        while not getattr(self, 'destroyed', False):
            numIcons = len(self.resourceIcons)
            if numIcons > 1:
                cycleTime = cycleTimeBase * numIcons
                t += 1.0 / blue.os.fps
                t = t % cycleTime
                for i, icon in enumerate(self.resourceIcons):
                    icon.display = t > i * cycleTimeBase and t < (i + 1) * cycleTimeBase
                    x = t - i * cycleTimeBase
                    alpha = math.sin(math.pi * (2 * x / cycleTimeBase - 0.5)) / 2 + 0.5
                    icon.pinColor = (1.0,
                     1.0,
                     1.0,
                     alpha * 0.8)

            blue.pyos.synchro.Yield()

    def AssignIDsToPins(self):
        for pin in self.spherePins:
            if isinstance(self.pin.id, tuple):
                pinType = planetCommon.PINTYPE_NORMALEDIT
                pin.name = '%s,%s,%s' % (pinType, self.pin.id[0], self.pin.id[1])
            else:
                pinType = planetCommon.PINTYPE_NORMAL
                pin.name = '%s,%s' % (pinType, self.pin.id)

        self.border.name = self.shadow.name = ''

    def UpdateEditModeColors(self):
        if self and self.pin:
            if self.pin.IsInEditMode():
                self.mainPin.pinColor = planetCommon.PLANET_COLOR_PINEDITMODE
            else:
                self.mainPin.pinColor = (0.0, 0.0, 0.0, 0.4)

    def UpdateStorageGauge(self):
        if self.pin.IsStorage():
            usage = self.pin.capacityUsed / self.pin.GetCapacity()
        else:
            usage = 0.0
        if usage > 0:
            self.gauge.display = True
        else:
            self.gauge.display = False
        self.gauge.pinAlphaThreshold = usage

    def UpdateCycleTimer(self):
        while not getattr(self, 'destroyed', False):
            if self.pin.GetCycleTime() and self.pin.GetNextRunTime() and self.pin.IsActive() and not self.pin.IsInEditMode():
                self.cycle.display = True
                self.cycle.pinColor = util.Color.WHITE
                currCycle = self.pin.GetCycleTime() - (self.pin.GetNextRunTime() - blue.os.GetWallclockTime())
                cycleProportion = currCycle / float(self.pin.GetCycleTime())
                if self.lastCycleProportion > cycleProportion:
                    self.firstCycle = not self.firstCycle
                self.lastCycleProportion = cycleProportion
                if self.firstCycle:
                    self.cycle.pinAlphaThreshold = cycleProportion
                else:
                    self.cycle.pinAlphaThreshold = 1.0 - cycleProportion
                    self.cycle.pinRotation = cycleProportion * 2.0 * math.pi
            elif self.pin.IsProducer() and getattr(self.pin, 'schematicID', False):
                cycleLength = 3.0
                elapsed = 1.0 / blue.os.fps
                self.producerCycleTime += elapsed
                if self.producerCycleTime > cycleLength:
                    self.producerCycleTime -= cycleLength
                self.cycle.display = True
                self.cycle.pinAlphaThreshold = 1.0
                alpha = math.sin(math.pi * self.producerCycleTime / cycleLength)
                self.cycle.pinColor = (1.0,
                 1.0,
                 1.0,
                 alpha)
            else:
                self.cycle.display = False
            blue.pyos.synchro.Yield()

    def RenderAccordingToState(self):
        renderState = self.renderState
        if renderState.mouseHover:
            self.border.display = True
            self.border.pinColor = (1.0, 1.0, 1.0, 0.15)
        elif renderState.asRoute:
            self.border.display = True
            self.border.pinColor = (255.0 / 256,
             125.0 / 256,
             0.0 / 256,
             0.15)
        elif renderState.selected:
            pass
        else:
            self.border.display = False

    def ResetPinData(self, newPin):
        self.pin = newPin
        self.UpdateEditModeColors()

    def GetContainer(self, parent):
        return planet.ui.BasePinContainer(parent=parent, pin=self.pin)

    def GetMenu(self):
        ret = []
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        ret.extend([(uiutil.MenuLabel('UI/PI/Common/CreateLink'), sm.GetService('planetUI').eventManager.BeginCreateLink, [self.pin.id]), (uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.pin.typeID, self.pin.id])])
        return ret

    def GetGMMenu(self):
        ret = []
        ret.append(('PinID: %s' % (self.pin.id,), blue.pyos.SetClipboardData, [str(self.pin.id)]))
        return ret

    def OnRefreshPins(self):
        self.UpdateStorageGauge()
        self.SetResourceIcons()
        self.UpdateEditModeColors()

    def SetAsRoute(self):
        self.renderState.asRoute = True
        self.RenderAccordingToState()

    def ResetAsRoute(self):
        self.renderState.asRoute = False
        self.RenderAccordingToState()

    def OnClicked(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            uicls.UIEffects().MorphUI(pin, 'pinRadius', expandedRadius, time=250.0, float=1, newthread=1, maxSteps=1000)

        self.Show3DModel()

    def PlacementAnimation(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            pin.pinRadius = RADIUS_LOGO
            uicls.UIEffects().MorphUI(pin, 'pinRadius', radius, time=250.0, float=1, newthread=1, maxSteps=1000)

    def Get3DModel(self):
        graphic = cfg.invtypes.Get(self.pin.typeID).Graphic()
        if graphic and graphic.graphicFile:
            graphicFile = str(graphic.graphicFile)
            graphicFile = graphicFile.replace(':/model', ':/dx9/model').replace('.blue', '.red')
            return trinity.Load(graphicFile)
        if not self.model3D or self.model3D.__bluetype__ != 'trinity.EveTransform':
            return trinity.Load('res:/dx9/model/worldobject/Orbital/UI/Terrestrial/Command/CommT_T1/CommT_T1.red')

    def OnSomethingElseClicked(self):
        for pin, radius, expandedRadius in self.pinExpansions:
            uicls.UIEffects().MorphUI(pin, 'pinRadius', radius, time=250.0, float=1, newthread=1, maxSteps=1000)

        if self.model3D:
            self.Hide3dModel()

    def OnMouseEnter(self):
        self.renderState.mouseHover = True
        self.RenderAccordingToState()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.renderState.mouseHover = False
        self.RenderAccordingToState()

    def OnPlanetZoomChanged(self, zoom):
        self.zoom = zoom
        self.SetResourceIconAppearance()

    def ProcessColonyDataSet(self, planetID):
        if sm.GetService('planetUI').planetID != planetID:
            return
        self.pin = sm.GetService('planetSvc').GetPlanet(planetID).GetPin(self.pin.id)


class CommandCenterPin(BasePlanetPin):
    __guid__ = 'planet.ui.CommandCenterPin'
    BasePlanetPin.__notifyevents__.append('OnEditModeBuiltOrDestroyed')

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        gaugeRadius = 0.005
        gaugeRadiusExtended = 0.0082
        powerGauge = self.powerGauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=11, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_POWER)
        powerGaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=10, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=(0.35, 0, 0))
        powerGauge.name = powerGaugeUnderlay.name = '%s,%s' % (planetCommon.PINTYPE_NORMAL, self.pin.id)
        self.pinExpansions.append((powerGauge, gaugeRadius, gaugeRadiusExtended))
        self.pinExpansions.append((powerGaugeUnderlay, gaugeRadius, gaugeRadiusExtended))
        cpuGauge = self.cpuGauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=11, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_CPU)
        cpuGaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/hash15px.dds', layer=10, radius=gaugeRadius, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=(0.0, 0.329, 0.267, 1.0))
        cpuGauge.name = cpuGaugeUnderlay.name = '%s,%s' % (planetCommon.PINTYPE_NORMAL, self.pin.id)
        cpuGauge.pinRotation = cpuGaugeUnderlay.pinRotation = math.pi
        self.pinExpansions.append((cpuGauge, gaugeRadius, gaugeRadiusExtended))
        self.pinExpansions.append((cpuGaugeUnderlay, gaugeRadius, gaugeRadiusExtended))
        powerGaugeUnderlay.pinAlphaThreshold = 0.5
        cpuGaugeUnderlay.pinAlphaThreshold = 0.5
        self.AssignIDsToPins()
        self.UpdatePowerCPUGauge()

    def OnRefreshPins(self):
        BasePlanetPin.OnRefreshPins(self)
        self.UpdatePowerCPUGauge()

    def OnEditModeBuiltOrDestroyed(self):
        self.UpdatePowerCPUGauge()

    def UpdatePowerCPUGauge(self):
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Colony is gone but Command Pin window still open')
        if colony.colonyData.GetColonyPowerSupply() > 0:
            self.powerGauge.pinAlphaThreshold = min(1.0, float(colony.colonyData.GetColonyPowerUsage()) / colony.colonyData.GetColonyPowerSupply()) / 2.0
        else:
            self.powerGauge.pinAlphaThreshold = 0.0
        if colony.colonyData.GetColonyCpuSupply() > 0:
            self.cpuGauge.pinAlphaThreshold = min(1.0, float(colony.colonyData.GetColonyCpuUsage()) / float(colony.colonyData.GetColonyCpuSupply())) / 2.0
        else:
            self.cpuGauge.pinAlphaThreshold = 0.0

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        if session.role & ROLE_GMH == ROLE_GMH and not sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            menu.append(('Convert Command Center', self.ConvertCommandCenter))
        return menu

    def ConvertCommandCenter(self):
        sm.GetService('planetUI').planet.GMConvertCommandCenter(self.pin.id)

    def GetContainer(self, parent):
        return planet.ui.CommandCenterContainer(parent=parent, pin=self.pin)


class ProcessorPin(BasePlanetPin):
    __guid__ = 'planet.ui.ProcessorPin'

    def __init__(self, surfacePoint, pin, transform):
        self.hopperGauges = []
        self.hopperGaugeUnderlays = []
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        self.gauge.display = self.gaugeUnderlay.display = False
        for i in xrange(3):
            gauge = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=11, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_USED_PROCESSOR)
            gaugeUnderlay = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=10, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINLIFTED, isGauge=True, color=planetCommon.PLANET_COLOR_PROCESSOR)
            gauge.display = gaugeUnderlay.display = False
            self.hopperGauges.append(gauge)
            self.hopperGaugeUnderlays.append(gaugeUnderlay)
            self.pinExpansions.append((gauge, RADIUS_PIN, RADIUS_PINEXTENDED))
            self.pinExpansions.append((gaugeUnderlay, RADIUS_PIN, RADIUS_PINEXTENDED))

        self.AssignIDsToPins()
        self.UpdateStorageGauge()

    def UpdateStorageGauge(self):
        if not self.hopperGauges:
            return
        proportions = []
        ingredients = []
        gapConst = 0.04
        for i in cfg.schematicstypemap.get(self.pin.schematicID, []):
            if i.isInput:
                ingredients.append(i)

        numIngredients = len(ingredients)
        for i in xrange(3):
            if i > numIngredients - 1:
                self.hopperGauges[i].display = False
                self.hopperGaugeUnderlays[i].display = False
                continue
            hopperFill = self.pin.contents.get(ingredients[i].typeID, 0) / float(ingredients[i].quantity)
            if hopperFill > 1.0:
                hopperFill = 1.0
            if hopperFill > 0.0:
                self.hopperGauges[i].display = True
            self.hopperGaugeUnderlays[i].display = True
            if numIngredients > 1:
                gaugeThreshold = hopperFill / numIngredients * (1.0 - gapConst * numIngredients)
                underlayThreshold = 1.0 / numIngredients * (1.0 - gapConst * numIngredients)
            else:
                gaugeThreshold = hopperFill
                underlayThreshold = 1.0
            rotation = 2 * math.pi * (float(i) / numIngredients + gapConst / 2.0)
            self.hopperGauges[i].pinAlphaThreshold = gaugeThreshold
            self.hopperGaugeUnderlays[i].pinAlphaThreshold = underlayThreshold
            self.hopperGauges[i].pinRotation = rotation
            self.hopperGaugeUnderlays[i].pinRotation = rotation

    def GetContainer(self, parent):
        return planet.ui.ProcessorContainer(parent=parent, pin=self.pin)


class ExtractorPin(BasePlanetPin):
    __guid__ = 'planet.ui.ExtractorPin'
    baseColor = planetCommon.PLANET_COLOR_EXTRACTOR

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)

    def GetMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetMenu(self))
        return menu

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        return menu

    def GetContainer(self, parent):
        return planet.ui.ExtractorContainer(parent=parent, pin=self.pin)


class EcuPin(BasePlanetPin):
    __guid__ = 'planet.ui.EcuPin'
    baseColor = planetCommon.PLANET_COLOR_EXTRACTOR

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)
        self.rings = []
        self.extractionHeadsByNum = {}
        self.linksByHeadID = {}
        numRings = 6
        self.transform = transform
        for i in xrange(numRings):
            ring = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/gauge_15px.dds', layer=0, radius=0.0, transform=transform, color=util.Color(*planetCommon.PLANET_COLOR_EXTRACTOR).SetAlpha(0.3).GetRGBA())
            self.rings.append(ring)

        self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=0, radius=RADIUS_PIN * 0.25, scale=SCALE_ONGROUND * 1.0005, transform=transform, color=planetCommon.PLANET_COLOR_EXTRACTOR)
        areaOfInfluence = pin.GetAreaOfInfluence()
        self.maxDistanceCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=areaOfInfluence, scale=SCALE_ONGROUND * 1.0005, transform=transform, display=False)
        self.maxDistanceCircle.pinMaxRadius = areaOfInfluence
        self.RenderExtractionHeads()
        uthread.new(self.Animate)

    def ShowMaxDistanceCircle(self, distanceFactor):
        STARTSHOWVALUE = 0.7
        MAXALPHA = 0.2
        if distanceFactor > STARTSHOWVALUE:
            self.maxDistanceCircle.display = True
            color = planetCommon.GetContrastColorForCurrPlanet()
            x = (distanceFactor - STARTSHOWVALUE) / (1.0 - STARTSHOWVALUE)
            self.maxDistanceCircle.pinColor = util.Color(*color).SetAlpha(MAXALPHA * x).GetRGBA()
        else:
            self.maxDistanceCircle.display = False

    def GetExtractionHead(self, headID):
        return self.extractionHeadsByNum.get(headID, None)

    def RenderExtractionHeads(self):
        self.RemoveAllHeads()
        for headID, phi, theta in self.pin.heads:
            surfacePoint = planet.SurfacePoint(theta=theta, phi=phi)
            self.AddHead(headID, surfacePoint)

    def AddHead(self, headID, surfacePoint):
        extractionHead = planet.ui.ExtractionHeadPin(surfacePoint, self.transform, self.pin, headID, self.pin.headRadius or planetCommon.RADIUS_DRILLAREAMIN)
        self.extractionHeadsByNum[headID] = extractionHead
        link = planet.ui.LinkBase('linksExtraction', surfacePoint, self.surfacePoint, color=planetCommon.PLANET_COLOR_EXTRACTIONLINK)
        self.linksByHeadID[headID] = link

    def RemoveAllHeads(self):
        for headID in self.extractionHeadsByNum.keys():
            self.RemoveHead(headID)

    def RemoveHead(self, headID):
        head = self.extractionHeadsByNum.get(headID, None)
        if head:
            head.Remove()
            self.extractionHeadsByNum.pop(headID)
        link = self.linksByHeadID.get(headID, None)
        if link:
            link.Remove()
            self.linksByHeadID.pop(headID)

    def MoveExtractionHeadTo(self, headID, surfacePoint):
        head = self.extractionHeadsByNum.get(headID, None)
        if head:
            head.SetLocation(surfacePoint)
        link = self.linksByHeadID.get(headID, None)
        if link:
            link.Remove()
            link = planet.ui.LinkBase('linksExtraction', surfacePoint, self.surfacePoint, color=planetCommon.PLANET_COLOR_EXTRACTIONLINK)
        self.Hide3dModel()
        for head in self.extractionHeadsByNum.values():
            head.Hide3dModel()

    def ResetPinData(self, newPin):
        oldHeads = [ head for head in self.pin.heads ]
        newHeads = [ head for head in newPin.heads ]
        toRemove = [ head for head in oldHeads if head not in newHeads ]
        for headID, phi, theta in toRemove:
            self.RemoveHead(headID)

        toAdd = [ head for head in newHeads if head not in oldHeads ]
        for headID, phi, theta in toAdd:
            surfacePoint = planet.SurfacePoint(theta=theta, phi=phi)
            self.AddHead(headID, surfacePoint)

        for headUI in self.extractionHeadsByNum.values():
            headUI.pin = self.pin

        BasePlanetPin.ResetPinData(self, newPin)

    def ResetOverlapValues(self):
        for headUI in self.extractionHeadsByNum.values():
            headUI.SetOverlapValue(0)

    def SetOverlapValues(self, overlapVals):
        for headID, overlapVal in overlapVals.iteritems():
            head = self.extractionHeadsByNum.get(headID, None)
            if head:
                head.SetOverlapValue(overlapVal)

    def SetExtractionHeadRadius(self, radius, time = 1000.0):
        uthread.new(self._SetExtractionHeadRadius, radius, time)

    def _SetExtractionHeadRadius(self, radius, time):
        for head in self.extractionHeadsByNum.values():
            head.SetExtractionHeadRadius(radius, time)
            blue.pyos.synchro.SleepWallclock(100)

    def Remove(self):
        self.RemoveAllHeads()
        BasePlanetPin.Remove(self)

    def Animate(self):
        cycleTime = 10.0
        numRings = len(self.rings)
        scaleDiff = SCALE_PINLIFTED - 1.0
        elapsed = 0.0
        color = list(planetCommon.PLANET_COLOR_EXTRACTOR)
        while not getattr(self, 'destroyed', False):
            elapsed += 1.0 / blue.os.fps
            t = elapsed % cycleTime
            for i, ring in enumerate(self.rings):
                x = (float(i + 1) / numRings + t / cycleTime) % 1
                scale = x * scaleDiff + 1.0
                ring.scaling = (scale, scale, scale)
                ring.pinRadius = (x * 0.7 + 0.3) * self.mainPin.pinRadius
                color[3] = x
                ring.pinColor = color

            blue.pyos.synchro.Yield()

    def OnClicked(self):
        BasePlanetPin.OnClicked(self)
        for head in self.extractionHeadsByNum.values():
            head.Show3DModel()

    def OnSomethingElseClicked(self):
        BasePlanetPin.OnSomethingElseClicked(self)
        for head in self.extractionHeadsByNum.values():
            head.Hide3dModel()

    def GetMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetMenu(self))
        return menu

    def GetGMMenu(self):
        menu = []
        menu.extend(BasePlanetPin.GetGMMenu(self))
        if session.role & ROLE_GMH == ROLE_GMH and not sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            menu.append(('Deposit Designer', self.HotProgramInjection))
        return menu

    def HotProgramInjection(self):
        sm.GetService('planetUI').planet.GMInstallProgram(self.pin.id)

    def GetContainer(self, parent):
        return planet.ui.ECUContainer(parent=parent, pin=self.pin)


class LaunchpadPin(BasePlanetPin):
    __guid__ = 'planet.ui.Launchpad'

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)

    def GetContainer(self, parent):
        return planet.ui.LaunchpadContainer(parent=parent, pin=self.pin)


class StorageFacilityPin(BasePlanetPin):
    __guid__ = 'planet.ui.StorageFacility'

    def __init__(self, surfacePoint, pin, transform):
        BasePlanetPin.__init__(self, surfacePoint, pin, transform)

    def GetContainer(self, parent):
        return planet.ui.StorageFacilityContainer(parent=parent, pin=self.pin)


LINK_WIDTH = 6.0
LINK_OFFSET = 0.0006
LINK_FLOWSPEED = 0.002
LINK_SEGMENTRATIO = 25.0
LINK_COLOR_BASE = (0.0,
 0.0,
 0.0,
 1.0)
LINK_COLOR_DEFAULT = (0.0,
 1.0,
 1.0,
 1.0)
LINK_COLOR_ROUTED = (1.0,
 0.5,
 0.0,
 1.0)
LINK_COLOR_HOVER = (1.0,
 1.0,
 1.0,
 1.0)
LINK_COLOR_SELECTED = (1.0,
 1.0,
 0.0,
 1.0)
LINK_COLOR_INACTIVE = (0.0,
 0.0,
 0.0,
 0.3)

class LinkBase():
    __guid__ = 'planet.ui.LinkBase'

    def __init__(self, lsName, surfacePoint1, surfacePoint2, color = LINK_COLOR_DEFAULT):
        self.state = util.KeyVal(mouseHover=False, link1AsRoute=False, link2AsRoute=False, selected=False, link1Active=False, link2Active=False)
        self.lsName = lsName
        self.clDrawer = sm.GetService('planetUI').curveLineDrawer
        self.length = surfacePoint1.GetDistanceToOther(surfacePoint2)
        self.flowSpeed = LINK_FLOWSPEED / self.length
        self.texWidth = 1200.0 * self.length
        self.linkGraphicID = self.clDrawer.DrawArc(lsName, surfacePoint2, surfacePoint1, LINK_WIDTH * 0.5, LINK_COLOR_BASE, LINK_COLOR_BASE)
        numSegments = max(1, int(self.length * LINK_SEGMENTRATIO))
        self.clDrawer.SetLineSetNumSegments(lsName, self.linkGraphicID, numSegments)
        self.SetAnimation(color=color, isActive=True)

    def SetAnimation(self, color, isActive, speed = 1.0):
        self.clDrawer.ChangeLineAnimation(self.lsName, self.linkGraphicID, color, speed * self.flowSpeed, self.texWidth)
        self.clDrawer.SubmitLineset(self.lsName)

    def Remove(self):
        self.clDrawer.RemoveLine(self.lsName, self.linkGraphicID)


class Link():
    __guid__ = 'planet.ui.Link'

    def __init__(self, surfacePoint1, surfacePoint2, parentID, childID, typeID, link = None):
        self.link = link
        self.state = util.KeyVal(mouseHover=False, link1AsRoute=False, link2AsRoute=False, selected=False, link1Active=False, link2Active=False)
        self.clDrawer = sm.GetService('planetUI').curveLineDrawer
        self.sp1A, self.sp1B, self.sp2A, self.sp2B, self.surfacePoint = self._GetLinkEndPoints(surfacePoint1, surfacePoint2)
        self.length = surfacePoint1.GetDistanceToOther(surfacePoint2)
        self.IDTuple = (childID, parentID)
        self.typeID = typeID
        self.flowSpeed = LINK_FLOWSPEED / self.length
        self.texWidth = 600.0 * self.length
        self.currentRouteVolume = None
        self.linkGraphicID1 = self.clDrawer.DrawArc('links', self.sp1A, self.sp1B, LINK_WIDTH, LINK_COLOR_BASE, LINK_COLOR_BASE)
        self.linkGraphicID2 = self.clDrawer.DrawArc('links', self.sp2B, self.sp2A, LINK_WIDTH, LINK_COLOR_BASE, LINK_COLOR_BASE)
        numSegments = max(1, int(self.length * LINK_SEGMENTRATIO))
        self.clDrawer.SetLineSetNumSegments('links', self.linkGraphicID1, numSegments)
        self.clDrawer.SetLineSetNumSegments('links', self.linkGraphicID2, numSegments)
        self.clDrawer.SubmitLineset('links')
        self.graphicIDbyID = {(childID, parentID): self.linkGraphicID1,
         (parentID, childID): self.linkGraphicID2}
        self._InitInfoBracket()
        self.state.link1Active, self.state.link2Active = self._GetLinksActiveState()
        self.RenderAccordingToState()

    def _InitInfoBracket(self):
        self.infoBracket = uicls.Bracket()
        self.infoBracket.name = '__inflightbracket'
        self.infoBracket.align = uiconst.ABSOLUTE
        self.infoBracket.state = uiconst.UI_DISABLED
        self.infoBracket.dock = False
        self.infoBracket.display = False
        pad = 2
        self.infoBracket.padding = (pad,
         pad,
         pad,
         pad)
        self.infoBracket.trackTransform = trinity.EveTransform()
        self.infoBracket.trackTransform.name = 'LinkInfoBracket'
        t = self.surfacePoint.GetAsXYZTuple()
        scale = 1.01
        self.infoBracket.trackTransform.translation = (t[0] * scale, t[1] * scale, t[2] * scale)
        self.bracketCurveSet = sm.GetService('planetUI').myPinManager.bracketCurveSet
        self.bracketCurveSet.curves.append(self.infoBracket.projectBracket)
        sm.GetService('planetUI').planetTransform.children.append(self.infoBracket.trackTransform)
        sm.GetService('planetUI').pinInfoParent.children.insert(0, self.infoBracket)
        self.infoText = uicls.EveLabelSmall(text='', parent=self.infoBracket, align=uiconst.TOPLEFT, width=self.infoBracket.width, left=pad, top=pad, color=util.Color.WHITE, state=uiconst.UI_NORMAL)
        self._UpdateInfoBracket()
        self._ResizeInfoBracket()
        uicls.Fill(parent=self.infoBracket, color=(0.0, 0.0, 0.0, 0.5))
        self.infoBracket.state = uiconst.UI_HIDDEN

    def _ResizeInfoBracket(self):
        pad = 2
        l, t, w, h = self.infoText.GetAbsolute()
        self.infoBracket.width = w + pad * 2
        self.infoBracket.height = h + pad * 2 - 2

    def _UpdateInfoBracket(self):
        linkBandwidthUsage = self.link.GetBandwidthUsage()
        if self.currentRouteVolume is not None:
            addedPercentage = self.currentRouteVolume / self.link.GetTotalBandwidth() * 100.0
            if self.currentRouteVolume + linkBandwidthUsage > self.link.GetTotalBandwidth():
                addedText = localization.GetByLabel('UI/PI/Common/LinkCapacityAddedInvalid', addedPercentage=addedPercentage)
            else:
                addedText = localization.GetByLabel('UI/PI/Common/LinkCapacityAddedOK', addedPercentage=addedPercentage)
        else:
            addedText = ''
        usedPercentage = linkBandwidthUsage / self.link.GetTotalBandwidth() * 100.0
        bandwidthUsage = localization.GetByLabel('UI/PI/Common/LinkCapacityUsed', usedPercentage=usedPercentage, addedText=addedText)
        self.infoText.text = bandwidthUsage
        self._ResizeInfoBracket()

    def _GetLinkEndPoints(self, sp1, sp2):
        p1 = geo2.Vector(*sp1.GetAsXYZTuple())
        p2 = geo2.Vector(*sp2.GetAsXYZTuple())
        vecDiff = p2 - p1
        pOffset = geo2.Vec3Cross(p1, vecDiff)
        pOffset = geo2.Vec3Normalize(pOffset)
        pOffset = geo2.Vec3Scale(pOffset, LINK_OFFSET)
        link1Start = geo2.Vec3Normalize(p1 + pOffset)
        link1End = geo2.Vec3Normalize(p2 + pOffset)
        link2Start = geo2.Vec3Normalize(p1 - pOffset)
        link2End = geo2.Vec3Normalize(p2 - pOffset)
        centerPoint = geo2.Vec3Normalize(p1 + vecDiff * 0.5)
        sp = planet.SurfacePoint
        return (sp(*link1Start),
         sp(*link1End),
         sp(*link2Start),
         sp(*link2End),
         sp(*centerPoint))

    def RenderAccordingToState(self):
        state = self.state
        if state.mouseHover:
            self.SetLinkAppearance(LINK_COLOR_HOVER)
            self._UpdateInfoBracket()
            self.infoBracket.state = uiconst.UI_DISABLED
        elif state.link1AsRoute or state.link2AsRoute:
            if state.link1AsRoute:
                self.SetLinkAppearance(LINK_COLOR_ROUTED, self.linkGraphicID1, speed=3.0)
            if state.link2AsRoute:
                self.SetLinkAppearance(LINK_COLOR_ROUTED, self.linkGraphicID2, speed=3.0)
            self._UpdateInfoBracket()
            self.infoBracket.state = uiconst.UI_DISABLED
        else:
            if self.link.IsEditModeLink():
                color = planetCommon.PLANET_COLOR_LINKEDITMODE
            else:
                color = LINK_COLOR_DEFAULT
            self.SetLinkAppearance(color)
            self.infoBracket.state = uiconst.UI_HIDDEN

    def SetLinkAppearance(self, color, graphicID = None, speed = 1.0):
        link1Active, link2Active = self._GetLinksActiveState()
        if graphicID is None:
            self.clDrawer.ChangeLineAnimation('links', self.linkGraphicID1, color, link1Active * speed * self.flowSpeed, self.texWidth)
            self.clDrawer.ChangeLineAnimation('links', self.linkGraphicID2, color, link2Active * speed * self.flowSpeed, self.texWidth)
        else:
            self.clDrawer.ChangeLineAnimation('links', graphicID, color, speed * self.flowSpeed, self.texWidth)
            self.clDrawer.ChangeLineAnimation('links', graphicID, color, speed * self.flowSpeed, self.texWidth)
        if link1Active or self.link.IsEditModeLink():
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID1, LINK_COLOR_BASE)
        else:
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID1, LINK_COLOR_INACTIVE)
        if link2Active or self.link.IsEditModeLink():
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID2, LINK_COLOR_BASE)
        else:
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID2, LINK_COLOR_INACTIVE)
        self.clDrawer.SubmitLineset('links')

    def _GetLinksActiveState(self):
        link1Active = link2Active = False
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        if planet is None:
            return (False, False)
        colony = planet.GetColonyByPinID(self.IDTuple[0])
        if colony is None:
            return (False, False)
        for routeID in self.link.routesTransiting:
            route = colony.GetRoute(routeID)
            if route is None:
                continue
            route = route.path
            prevId = route[0]
            for currId in route[1:]:
                if prevId == self.IDTuple[0] and currId == self.IDTuple[1]:
                    link1Active = True
                if prevId == self.IDTuple[1] and currId == self.IDTuple[0]:
                    link2Active = True
                prevId = currId
                if link1Active and link2Active:
                    break

        return (link1Active, link2Active)

    def RemoveAsRoute(self, id):
        graphicID = self.graphicIDbyID[id]
        if graphicID == self.linkGraphicID1:
            self.state.link1AsRoute = False
        else:
            self.state.link2AsRoute = False
        self.RenderAccordingToState()
        self.currentRouteVolume = None

    def ShowAsRoute(self, id, numRoute, numTotal, volume = None):
        self.currentRouteVolume = volume
        graphicID = self.graphicIDbyID[id]
        if graphicID == self.linkGraphicID1:
            self.state.link1AsRoute = True
        else:
            self.state.link2AsRoute = True
        self.RenderAccordingToState()

    def HighlightLink(self):
        self.state.mouseHover = True
        self.RenderAccordingToState()

    def RemoveHighlightLink(self):
        self.state.mouseHover = False
        self.RenderAccordingToState()

    def OnRefreshPins(self):
        self.RenderAccordingToState()

    def OnClick(self):
        pass

    def OnMouseEnter(self):
        self.state.mouseHover = True
        self.RenderAccordingToState()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.state.mouseHover = False
        self.RenderAccordingToState()

    def OnSomethingElseClicked(self):
        pass

    def GetGraphicIDs(self):
        return (self.linkGraphicID1, self.linkGraphicID2)

    def GetIDTuple(self):
        return self.IDTuple

    def GetContainer(self, parent):
        return planet.ui.LinkContainer(parent=parent, pin=self, isLink=True)

    def GetMenu(self):
        return []

    def Remove(self):
        if self.infoBracket and self.bracketCurveSet:
            self.bracketCurveSet.curves.fremove(self.infoBracket.projectBracket)
            self.bracketCurveSet = None
        planetTransform = sm.GetService('planetUI').planetTransform
        if self.infoBracket.trackTransform in planetTransform.children:
            planetTransform.children.remove(self.infoBracket.trackTransform)
        pinInfoParent = sm.GetService('planetUI').pinInfoParent
        if self.infoBracket in pinInfoParent.children:
            pinInfoParent.children.remove(self.infoBracket)
        self.infoBracket = None

    def SetCurrentRouteVolume(self, volume):
        self.currentRouteVolume = volume
        self.RenderAccordingToState()

    def IsStorage(self):
        return False


class BuildIndicatorPin(SpherePinStack):
    __guid__ = 'planet.ui.BuildIndicatorPin'

    def __init__(self, surfacePoint, typeID, groupID, transform):
        areaOfInfluence = sm.GetService('godma').GetTypeAttribute2(typeID, const.attributeEcuAreaOfInfluence)
        SpherePinStack.__init__(self, surfacePoint, areaOfInfluence)
        self.surfacePin = self.CreateSpherePin(textureName=self.GetIconByGroupID(groupID), layer=10, radius=RADIUS_LOGO, transform=transform, scale=SCALE_PINBASE, color=(1.0, 1.0, 1.0, 0.4))
        self.cannotBuild = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=11, radius=RADIUS_PIN, transform=transform, scale=SCALE_PINBASE, color=(0.3, 0.0, 0.0, 0.5))
        self.cannotBuild.display = False
        self.shadow = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/disc_shadow.dds', layer=12, radius=RADIUS_SHADOW, transform=transform, scale=SCALE_ONGROUND, color=(0.0, 0.0, 0.0, 0.3))
        if groupID == const.groupExtractionControlUnitPins:
            color = planetCommon.GetContrastColorForCurrPlanet()
            color = util.Color(*color).SetAlpha(0.2).GetRGBA()
            self.maxDistanceCircle = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=areaOfInfluence, scale=SCALE_ONGROUND * 1.0005, transform=transform, color=color)
        sm.GetService('planetUI').planetNav.SetFocus()

    def SetCanBuildIndication(self, canBuild):
        self.cannotBuild.display = not canBuild

    def GetIconByGroupID(self, groupID):
        icons = {const.groupCommandPins: 'res:/UI/Texture/Planet/command.dds',
         const.groupExtractorPins: 'res:/UI/Texture/Planet/extractor.dds',
         const.groupProcessPins: 'res:/UI/Texture/Planet/process.dds',
         const.groupSpaceportPins: 'res:/UI/Texture/Planet/spaceport.dds',
         const.groupStoragePins: 'res:/UI/Texture/Planet/storage.dds',
         const.groupExtractionControlUnitPins: 'res:/UI/Texture/Planet/extractor.dds'}
        return icons.get(groupID)


class OtherPlayersPin(SpherePinStack):
    __guid__ = 'planet.ui.OtherPlayersPin'
    HOVERCOLOR = (1.0, 1.0, 1.0, 0.9)
    DEFAULTCOLOR = (0.0, 1.0, 1.0, 0.3)

    def __init__(self, surfacePoint, pinID, typeID, ownerID, transform, isActive = False):
        SpherePinStack.__init__(self, surfacePoint, RADIUS_PINOTHERS)
        self.pinID = pinID
        self.typeID = typeID
        self.ownerID = ownerID
        typeObj = cfg.invtypes.Get(typeID)
        pinIconPath = PINICONPATHS[typeObj.groupID]
        col = PINCOLORS[typeObj.groupID]
        self.ACTIVECOLOR = (col[0],
         col[1],
         col[2],
         0.6)
        self.spherePins = []
        if isActive:
            self.currColor = self.ACTIVECOLOR
        else:
            self.currColor = self.DEFAULTCOLOR
        self.surfacePin = self.CreateSpherePin(textureName=pinIconPath, layer=0, radius=RADIUS_PINOTHERS, transform=transform, scale=SCALE_PINOTHERS, color=self.currColor)
        self.surfacePin.name = '%s,%s' % (planetCommon.PINTYPE_OTHERS, pinID)

    def OnMouseEnter(self):
        self.surfacePin.pinColor = self.HOVERCOLOR
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.surfacePin.pinColor = self.currColor

    def RenderAsActive(self):
        self.surfacePin.pinColor = self.currColor = self.ACTIVECOLOR

    def RenderAsDefault(self):
        self.surfacePin.pinColor = self.currColor = self.DEFAULTCOLOR

    def GetGMMenu(self):
        return None

    def GetMenu(self):
        charTypeID = cfg.eveowners.Get(self.ownerID).typeID
        charName = localization.GetByLabel('UI/PI/Common/OwnerName', ownerName=cfg.eveowners.Get(self.ownerID).name)
        charMenu = [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [charTypeID, self.ownerID])]
        charMenu.extend(sm.GetService('menu').GetMenuFormItemIDTypeID(self.ownerID, charTypeID))
        ret = [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.typeID, self.pinID]), None, (charName, charMenu)]
        return ret


class ExtractionHeadPin(SpherePinStack):
    __guid__ = 'planet.ui.ExtractionHeadPin'
    NUMWAVES = 2

    def __init__(self, surfacePoint, transform, ecuPin, headID, radius):
        SpherePinStack.__init__(self, surfacePoint, planetCommon.RADIUS_DRILLAREAMAX)
        self.pin = ecuPin
        self.headID = headID
        self.animationThread = None
        self.disturbanceVal = 0.0
        self.headRadius = radius
        self.model3D = self.Get3DModel()
        self.transform = transform
        self.surfacePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/drill_pin.dds', layer=headID * 10 + 2, radius=RADIUS_PIN * 0.4, maxRadius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND * 1.001, color=planetCommon.PLANET_COLOR_EXTRACTOR)
        self.selectionArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/arrows_256.dds', layer=headID * 10 + 1, radius=RADIUS_PIN * 1.2, maxRadius=RADIUS_PIN * 1.2, transform=transform, scale=SCALE_ONGROUND * 1.001, color=util.Color(*planetCommon.PLANET_COLOR_EXTRACTOR).SetAlpha(0.7).SetSaturation(0.9).GetRGBA())
        self.selectionArea.display = False
        self.pinColor = util.Color(*planetCommon.PLANET_COLOR_EXTRACTOR).SetSaturation(0.4).GetRGBA()
        self.drillArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=headID * 10, radius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND, color=self.pinColor)
        self.SetExtractionHeadRadius(radius)
        self.waves = []
        for i in xrange(self.NUMWAVES):
            wave = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/donut_512.dds', layer=0, radius=0.0, transform=transform, scale=SCALE_ONGROUND, color=self.pinColor)
            wave.name = ''
            self.waves.append(wave)

        self.noisePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/white_noise_256.dds', layer=0, radius=RADIUS_PIN * 1.5, transform=transform, scale=SCALE_ONGROUND, color=util.Color.WHITE, display=False)
        self.pickArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/pin_base.dds', layer=headID * 10 + 2, radius=RADIUS_PIN * 1.9, maxRadius=RADIUS_PIN * 1.9, transform=transform, scale=SCALE_ONGROUND * 1.001, color=(0.0, 0.0, 0.0, 0.01))
        name = '%s,%s,%s' % (planetCommon.PINTYPE_EXTRACTIONHEAD, self.pin.id, headID)
        self.selectionArea.name = self.surfacePin.name = self.pickArea.name = name
        uthread.new(self.AnimateDrillArea)
        uthread.new(self.AnimateWaves)
        uthread.new(self.AnimateNoise)

    def Get3DModel(self):
        if sm.GetService('planetUI').planet.planetTypeID == const.typePlanetGas:
            id = 10098
        else:
            id = 10097
        return trinity.Load(cfg.graphics.Get(id).graphicFile)

    def SetExtractionHeadRadius(self, radius, time = 250.0):
        if radius is None:
            return
        self.headRadius = radius
        if self.animationThread:
            self.animationThread.kill()
        self.animationThread = uicls.UIEffects().MorphUI(self.drillArea, 'pinRadius', radius, time=time, float=1, newthread=1, maxSteps=1000)

    def SetOverlapValue(self, disturbanceVal):
        self.disturbanceVal = min(1.0, max(0.0, disturbanceVal))

    def OnMouseEnter(self):
        self.ShowSelectionArea()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.HideSelectionArea()

    def ShowSelectionArea(self):
        self.selectionArea.display = True

    def HideSelectionArea(self):
        self.selectionArea.display = False

    def AnimateDrillArea(self):
        cycleLength = 3.0
        elapsed = 0.0
        while not getattr(self, 'destroyed', False):
            elapsed += 1.0 / blue.os.fps
            x = (math.sin(math.pi * elapsed / cycleLength) + 1.0) / 2.0
            brightness = x * 0.2 + 0.7
            alpha = x * 0.15 + 0.2
            self.drillArea.pinColor = util.Color(*self.pinColor).SetBrightness(brightness).SetAlpha(alpha).GetRGBA()
            blue.pyos.synchro.Yield()

    def AnimateWaves(self):
        elapsed = 0.0
        cycleLength = self.NUMWAVES * 6.0
        phaseDiff = cycleLength / self.NUMWAVES
        while not getattr(self, 'destroyed', False):
            if self.pin.IsActive():
                elapsed += 1.0 / blue.os.fps
                x = elapsed % cycleLength
                for i, wave in enumerate(self.waves):
                    x = (elapsed + i * phaseDiff) % cycleLength / cycleLength
                    wave.pinColor = util.Color(*planetCommon.PLANET_COLOR_EXTRACTOR).SetHSB(0.5, 0.4, 0.7 + 0.3 * x ** 0.3, 0.5 * x).GetRGBA()
                    wave.pinRadius = (1.0 - x) * self.drillArea.pinRadius

            else:
                for wave in self.waves:
                    wave.pinRadius = 0.0

            blue.pyos.synchro.Yield()

    def AnimateNoise(self):
        while not getattr(self, 'destroyed', False):
            if self.disturbanceVal > 0.0:
                self.noisePin.display = True
                self.noisePin.pinRotation = random.random() * math.pi * 2
                scale = self.drillArea.pinRadius / planetCommon.RADIUS_DRILLAREAMAX
                xVal = random.random() * 0.05 * scale
                yVal = random.random() * 0.05 * scale
                self.noisePin.uvAtlasScaleOffset = (scale,
                 scale,
                 xVal,
                 xVal)
                self.noisePin.pinRadius = self.drillArea.pinRadius * 0.95
                self.noisePin.pinColor = (1.0,
                 1.0,
                 1.0,
                 self.disturbanceVal * 1.0)
            else:
                self.noisePin.display = False
            blue.pyos.synchro.SleepWallclock(10)


class DepletionPin(SpherePinStack):
    __guid__ = 'planet.ui.DepletionPin'

    def __init__(self, surfacePoint, index, transform):
        self.index = index
        SpherePinStack.__init__(self, surfacePoint, 0.1)
        self.surfacePin = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/drill_pin.dds', layer=0, radius=RADIUS_PIN * 0.4, transform=transform, scale=SCALE_ONGROUND * 1.001, color=util.Color.OLIVE)
        self.pinColor = util.Color(*planetCommon.PLANET_COLOR_EXTRACTOR).SetSaturation(0.4).GetRGBA()
        self.drillArea = self.CreateSpherePin(textureName='res:/UI/Texture/Planet/survey_ghost_512.dds', layer=0, radius=planetCommon.RADIUS_DRILLAREAMAX, transform=transform, scale=SCALE_ONGROUND, color=(0.4, 0.4, 0.9, 0.75))
        self.surfacePin.name = '5,%d' % index

    def GetDuration(self):
        return getattr(self, 'duration', 1440)

    def GetAmount(self):
        return getattr(self, 'amount', 500)

    def GetHeadRadius(self):
        return getattr(self, 'headRadius', planetCommon.RADIUS_DRILLAREAMAX)

    def GetContainer(self, parent):
        pass