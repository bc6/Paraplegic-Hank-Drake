import service
from service import SERVICE_START_PENDING, SERVICE_RUNNING, ROLE_GML
from math import sin, cos, pi
import blue
import bluepy
import trinity
import types
import uix
import mathUtil
import uthread
import util
import xtriui
import sys
import fleetbr
import bracket
import mapcommon
from mapcommon import STARMAP_SCALE, SUN_DATA, JUMP_TYPES, JUMP_COLORS, ZOOM_MAX_STARMAP, ZOOM_MIN_STARMAP, TILE_MODE_SOVEREIGNTY, TILE_MODE_STANDIGS
import geo2
import uiconst
import hexmap
import starmap
import uicls
SUNBASE = 15.0
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
DAY = HOUR * 24L
WEEK = DAY * 7L
MONTH = WEEK * 4L
YEAR = DAY * 365L
LINESTEP_CONSTELLATION = 20.0
LINESTEP_REGION = 40.0
doingDebug = 0
SHOW_NONE = 0
SHOW_SELECTION = 1
SHOW_REGION = 2
SHOW_NEIGHBORS = 3
SHOW_ALL = 4
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/ParticleStarmap.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/MapSprite.dds'
OVERGLOW_FACTOR = 'OverGlowFactor'
DEFAULT_STAR_PARTICLE_COLOR = (0.1,
 0.1,
 0.1,
 1.0)
NEUTRAL_COLOR = (0.25,
 0.25,
 0.25,
 1.0)
HINT_LOCATION_HEADERS = (mls.UI_GENERIC_REGION,
 mls.UI_GENERIC_CONSTELLATION,
 mls.UI_GENERIC_SOLARSYSTEM,
 '')
PICK_SCALE = 0.3
PICK_RADIUS = 400.0
PICK_RADIUS_NEAR = 100.0
PICK_RADIUS_FAR = 400.0
REGION_LABEL_SCALE = 10.0
MAP_FLATTEN_ANIM_TIME = 750.0
MAP_ROTATION = (0.0, mathUtil.DegToRad(180.0), 0.0)
MAP_XYZW_ROTATION = (1.0,
 0.0,
 0.0,
 0.0)
MAP_XYZW_INV_ROTATION = (-1.0,
 0.0,
 0.0,
 0.0)
HEX_TILE_SIZE = 60

class PriorityDictionary(dict):

    def __init__(self):
        self._PriorityDictionary__heap = []
        dict.__init__(self)



    def smallest(self):
        if len(self) == 0:
            raise IndexError, 'smallest of empty PriorityDictionary'
        heap = self._PriorityDictionary__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2 * insertionPoint + 1
                if smallChild + 1 < len(heap) and heap[smallChild] > heap[(smallChild + 1)]:
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild


        return heap[0][1]



    def __iter__(self):

        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]



        return iterfn()



    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        heap = self._PriorityDictionary__heap
        if len(heap) > 2 * len(self):
            self._PriorityDictionary__heap = [ (v, k) for (k, v,) in self.iteritems() ]
            self._PriorityDictionary__heap.sort()
        else:
            newPair = (val, key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and newPair < heap[((insertionPoint - 1) // 2)]:
                heap[insertionPoint] = heap[((insertionPoint - 1) // 2)]
                insertionPoint = (insertionPoint - 1) // 2

            heap[insertionPoint] = newPair



    def setdefault(self, key, val):
        if key not in self:
            self[key] = val
        return self[key]




class StarMapSvc(service.Service):
    __guid__ = 'svc.starmap'
    __notifyevents__ = ['OnSessionChanged',
     'OnServerMapDataPush',
     'OnAvoidanceItemsChanged',
     'OnMapReset']
    __servicename__ = 'starmap'
    __displayname__ = 'Star Map Client Service'
    __dependencies__ = ['neocom', 'pathfinder', 'map']
    __startupdependencies__ = ['settings']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.LogInfo('Starting Map Client Svc')
        self.Reset()
        self.state = SERVICE_RUNNING



    def Stop(self, memStream = None):
        if trinity.device is None:
            return 
        self.LogInfo('Map svc')
        self.Reset()



    def Open(self, interestID = None, starColorMode = None, *args):
        self.map.OpenStarMap()
        if interestID:
            sm.GetService('starmap').SetInterest(interestID)
        if starColorMode:
            self.SetStarColorMode(starColorMode)



    def OnSessionChanged(self, isremote, session, change):
        if eve.session.charid is None:
            return 
        if self.map.ViewingStarMap():
            self.ShowWhereIAm()
        self.UpdateRoute(fakeUpdate=1)



    def OnAvoidanceItemsChanged(self):
        if self.map.ViewingStarMap():
            starColorMode = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
            if starColorMode == mapcommon.STARMODE_AVOIDANCE:
                self.SetStarColorMode(mapcommon.STARMODE_AVOIDANCE)



    def OnMapReset(self):
        self.Reset()



    def CleanUp(self):
        cachedDestinationPath = self.destinationPath
        self.Reset()
        self.destinationPath = cachedDestinationPath
        for child in uicore.layer.map.children:
            if child.name == '__cursor' or child.name == 'myloc':
                child.Close()

        scene1 = sm.GetService('sceneManager').GetRegisteredScene('starmap')
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
        if scene1:
            del scene1.models[:]
        if scene2:
            del scene2.objects[:]
        sm.GetService('sceneManager').UnregisterScene('starmap')
        sm.GetService('sceneManager').UnregisterScene2('starmap')
        sm.GetService('sceneManager').UnregisterCamera('starmap')
        self.mylocation = None



    def Reset(self):
        self.LogInfo('MapSvc Reset')
        self.securityInfo = None
        self.destinationPath = [None]
        self.interest = None
        self.currentSolarsystemID = None
        self.currentSolarsystem = None
        self.solarsystemBracketsLoaded = None
        self.solarsystemHierarchyData = {}
        self.expandingHint = None
        rangeCircleTF = getattr(self, 'rangeCircleTF', None)
        if rangeCircleTF:
            for each in rangeCircleTF.curveSets[:]:
                rangeCircleTF.curveSets.remove(each)

        self.rangeCircleTF = None
        self.rangeLineSet = None
        if hasattr(self, 'mapRoot') and self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        if hasattr(self, 'hexMap') and self.hexMap is not None:
            self.hexMap.tilePool = []
            self.hexMap = None
        self.particleIDToSystemIDMap = None
        self.mapNumIdx = None
        self.mapconnectionscache = None
        self.autoPilotRoute = None
        self.genericRoute = None
        self.genericRoutePath = None
        self.flattened = settings.user.ui.Get('mapFlattened', 1)
        self.wasConnectionViewMode = None
        self.regionLabels = None
        self.regionLabelParent = None
        self.solarsystemsCache = None
        self.solarSystemJumpIDdict = None
        self.allianceSolarSystems = {'s': {},
         'c': {}}
        self.LM_InitLandMarks()
        self.ClearLabels()
        toClose = getattr(self, 'labels', {})
        for each in toClose.itervalues():
            each.Close()

        self.labels = {}
        self.labeltrackersTF = None
        self.landmarkTF = None
        self.labeltrackers = {}
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.cursor = None
        toClose = getattr(self, 'uicursor', None)
        if toClose:
            toClose.Close()
        self.uicursor = None
        self.minimizedWindows = []
        self.stationCountCache = None
        self.warFactionByOwner = None



    def GetInterest(self):
        if self.interest is None:
            self.interest = [eve.session.regionid, eve.session.constellationid, eve.session.solarsystemid2]
        return self.interest



    def OnServerMapDataPush(self, tricolors, data):
        self.map.OpenStarMap()
        processedData = {}
        for (systemID, blobSize, colorScale, descriptionText, overrideColor,) in data:
            if overrideColor == (None, None, None):
                processedData[systemID] = (blobSize,
                 colorScale,
                 descriptionText,
                 None)
            else:
                processedData[systemID] = (blobSize,
                 colorScale,
                 descriptionText,
                 trinity.TriColor(overrideColor[0], overrideColor[1], overrideColor[2]))

        self.HighlightSolarSystems(processedData, [ trinity.TriColor(x[0], x[1], x[2]) for x in tricolors ])



    def PickSolarSystemID(self):
        if self.starParticles is None:
            return 
        (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
        particleID = self.starParticles.PickParticle(uicore.uilib.x, uicore.uilib.y, projection, view, viewport, PICK_SCALE, self.GetStarPickRadius())
        return self.particleIDToSystemIDMap.get(particleID, None)



    def PickParticle(self):
        if self.starParticles is None:
            return 
        else:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            particleID = self.starParticles.PickParticle(uicore.uilib.x + 1, uicore.uilib.y + 1, projection, view, viewport, PICK_SCALE, self.GetStarPickRadius())
            if particleID != -1:
                return particleID
            return 



    def GetItemMenu(self, itemID):
        item = self.map.GetItem(itemID, retall=True)
        if not item:
            return []
        m = []
        m.append(('%s - %s' % (item.item.itemName, cfg.invgroups.Get(item.item.typeID).name), self.SetInterest, (item.item.itemID,)))
        hierarchy = item.hierarchy[:]
        hierarchy.reverse()
        for parentID in hierarchy[1:]:
            parent = self.map.GetItem(parentID)
            if parent is not None:
                m.append((' ( %s - %s )' % (parent.itemName, cfg.invgroups.Get(parent.typeID).name), self.SetInterest, (parentID,)))

        m.append(None)
        mm = []
        while len(hierarchy) != 3:
            hierarchy.insert(0, None)

        (solarSystemID, constellationID, regionID,) = hierarchy
        if solarSystemID:
            mm.append((mls.SYSTEM, self.DrillToLocation, (solarSystemID, constellationID, regionID)))
        if constellationID:
            mm.append((mls.CONSTELLATION, self.DrillToLocation, (None, constellationID, regionID)))
        mm.append((mls.REGION, self.DrillToLocation, (None, None, regionID)))
        m.append((mls.SOVEREIGNTY_VIEWINDASHBOARD, mm))
        m.append(None)
        m += sm.GetService('menu').CelestialMenu(itemID, noTrace=1, mapItem=item.item)
        m.append(None)
        m.append((mls.UI_CMD_CENTERONSCREEN, self.SetInterest, (itemID, 1)))
        return m



    def DrillToLocation(self, systemID, constellationID, regionID):
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)



    def MakeBroadcastBracket(self, gbType, itemID, charID):
        if gbType != 'TravelTo':
            raise NotImplementedError
        if self.mapRoot is None:
            return 
        sysname = cfg.evelocations.Get(itemID).name.encode('utf-8')
        tracker = trinity.EveTransform()
        tracker.name = '__fleetbroadcast_%s' % sysname
        self.mapRoot.children.append(tracker)
        loc = self.map.GetItem(itemID)
        pos = (loc.x * STARMAP_SCALE, loc.y * STARMAP_SCALE, loc.z * STARMAP_SCALE)
        tracker.translation = pos
        anchor = xtriui.Bracket(parent=uicore.layer.map)
        anchor.state = uiconst.UI_DISABLED
        anchor.width = anchor.height = 1
        anchor.align = uiconst.NOALIGN
        anchor.name = 'fleetBroadcastAnchor_%s' % sysname
        anchor.itemID = itemID
        anchor.display = True
        anchor.trackTransform = tracker
        iconPath = fleetbr.types['TravelTo']['bigIcon']
        icon = uicls.Icon(icon=iconPath, parent=anchor, idx=0, pos=(0, 0, 32, 32), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        icon.name = 'fleetBroadcastIcon_%s' % sysname
        icon.hint = fleetbr.GetCaption_TravelTo(charID, itemID, itemID)
        icon.GetMenu = fleetbr.MenuGetter('TravelTo', charID, itemID)

        def Cleanup(*args):
            try:
                self.mapRoot.children.fremove(tracker)
            except (AttributeError, ValueError):
                sys.exc_clear()


        icon.OnClose = Cleanup
        return anchor



    def GetCloudNumFromItemID(self, itemID):
        if itemID in self.mapNumIdx:
            return self.mapNumIdx[itemID]



    def GetItemIDFromParticleID(self, particleID):
        solarSystemID = None
        if self.particleIDToSystemIDMap:
            solarSystemID = self.particleIDToSystemIDMap[particleID]
        return solarSystemID



    def UpdateHint(self, nav = None):
        if getattr(self, 'doinghint', 0):
            return 
        self.doinghint = 1
        if self.starParticles is None:
            self.doinghint = 0
            return 
        (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
        particleID = self.starParticles.PickParticle(uicore.uilib.x, uicore.uilib.y, projection, view, viewport, PICK_SCALE, self.GetStarPickRadius())
        if getattr(self, 'lastpick', None) == particleID:
            self.doinghint = 0
            return 
        hint = ''
        if particleID in self.particleIDToSystemIDMap:
            itemID = self.particleIDToSystemIDMap[particleID]
            item = self.map.GetItem(itemID)
            hint = item.itemName
            hierarchy = self.map.GetParentLocationID(itemID, 1)
            if hierarchy:
                locs = []
                for locationID in hierarchy[1:]:
                    if locationID is not None:
                        if locationID not in locs:
                            locs.append(locationID)

                if len(locs):
                    cfg.evelocations.Prime(locs)
                hintParts = []
                for (i, locationID,) in enumerate(hierarchy[1:]):
                    if locationID is not None:
                        hintParts.appen('%s %s' % (cfg.evelocations.Get(locationID).name, HINT_LOCATION_HEADERS[i]))

                hint = ' - '.join(hintParts)
        self.lastpick = particleID
        if nav:
            nav.hint = hint
        self.doinghint = 0



    def RemoveChild(self, tf, childname):
        for each in tf.children[:]:
            if each.name == childname:
                tf.children.remove(each)




    def ShowJumpDriveRange(self):
        if getattr(self, 'mylocation', None):
            for each in self.mylocation.trackerTransform.children[:]:
                if each.name == 'jumpDriveRange':
                    self.mylocation.trackerTransform.children.remove(each)

        else:
            return 
        if eve.session.regionid > const.mapWormholeRegionMin or session.shipid is None:
            return 
        driveRange = sm.GetService('godma').GetItem(session.shipid).jumpDriveRange
        if driveRange is None or driveRange == 0:
            return 
        scale = 2.0 * driveRange * const.LIGHTYEAR * STARMAP_SCALE
        sphere = trinity.Load('res:/dx9/model/UI/JumpRangeBubble.red')
        sphere.scaling = (scale, scale, scale)
        sphere.name = 'jumpDriveRange'
        if self.IsFlat():
            sphere.display = False
        self.mylocation.trackerTransform.children.append(sphere)



    def RemoveMyLocation(self):
        self.RemoveChild(self.mapRoot, '__mylocation')
        if getattr(self, 'mylocationBracket', None):
            self.mylocationBracket.Close()
            self.mylocationBracket = None
            self.mylocation = None



    def ShowWhereIAm(self):
        if self.mapRoot is None:
            return 
        if eve.session.regionid > const.mapWormholeRegionMin:
            self.RemoveMyLocation()
        else:
            locationid = eve.session.solarsystemid2
            waypoints = self.GetWaypoints()
            if getattr(self, 'mylocation', None) is None:
                self.RemoveMyLocation()
                tracker = trinity.EveTransform()
                tracker.name = '__mylocation'
                self.mapRoot.children.append(tracker)
                label = self.GetCurrLocationBracket()
                label.Startup('myloc', locationid, None, tracker, None, 1)
                labeltext = uicls.Label(text=mls.UI_SHARED_MAPYOUAREHERE, parent=label, left=210, top=0, autoheight=False, height=12, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0)
                sm.GetService('ui').BlinkSpriteA(labeltext, 1.0, 750, None, passColor=0, minA=0.5)
                self.labeltext = labeltext
                self.mylocationBracket = label
            else:
                tracker = self.mylocation.trackerTransform
            uicore.effect.MorphUI(self.labeltext, 'top', [7, 19][(locationid in waypoints)])
            location = self.map.GetItem(locationid)
            pos = geo2.Vector(location.x, location.y, location.z)
            pos *= STARMAP_SCALE
            tracker.translation = pos
            bp = sm.GetService('michelle').GetBallpark()
            if bp is not None:
                ship = bp.GetBall(eve.session.shipid)
                if ship is not None:
                    shipPos = geo2.Vector(ship.x, ship.y, ship.z)
                    shipPos *= STARMAP_SCALE
                    pos += shipPos
                    tracker.translation = pos
            self.mylocation = util.KeyVal(locationID=locationid, trackerTransform=tracker)
        self.ShowDestination()
        self.ShowJumpDriveRange()



    def ShowDestination(self):
        if not self.map.IsOpen():
            return 
        waypoints = self.GetWaypoints()
        self.mydestination = getattr(self, 'mydestination', [])
        if len(self.mydestination) == 0:
            if len(waypoints) == 0:
                return 
        else:
            for waypoint in self.mydestination:
                waypoint.label.Close()
                self.mapRoot.children.fremove(waypoint.tracker)

        self.mydestination = []
        lastWaypoint = eve.session.solarsystemid2
        totalJumps = 0
        if len(waypoints) > 0:
            currentExtractWaypoint = waypoints[0]
            waypointIndex = 0
            waypointSystemList = []
            currentSystemList = [lastWaypoint]
            for systemID in self.destinationPath:
                currentSystemList.append(systemID)
                if systemID == currentExtractWaypoint:
                    waypointSystemList.append(currentSystemList)
                    currentSystemList = [systemID]
                    waypointIndex += 1
                    if waypointIndex == len(waypoints):
                        break
                    currentExtractWaypoint = waypoints[waypointIndex]

        else:
            waypointSystemList = []
        waypointIndex = 0
        for (waypointIndex, waypointID,) in enumerate(waypoints):
            if waypointIndex < len(waypointSystemList):
                solarsystems = waypointSystemList[waypointIndex]
            else:
                solarsystems = []
            if not len(solarsystems):
                comment = ' - %s ' % mls.UI_GENERIC_UNREACHABLE
            else:
                totalJumps = totalJumps + len(solarsystems) - 1
                comment = ' - %s' % (uix.Plural(totalJumps, 'UI_SHARED_NUM_JUMP') % {'num': totalJumps})
                lastWaypoint = solarsystems[-1]
            tracker = trinity.EveTransform()
            tracker.name = '__waypoint_%d' % waypointIndex
            if self.mapRoot:
                self.mapRoot.children.append(tracker)
            label = self.GetCurrLocationBracket()
            label.Startup('myDest', waypointID, const.groupSolarSystem, tracker, None, 1)
            targetItem = self.map.GetItem(waypointID)
            extraText = ''
            if targetItem.groupID == const.groupConstellation:
                extraText = ' %s ' % mls.UI_GENERIC_CONSTELLATION
            elif targetItem.groupID == const.groupRegion:
                extraText = ' %s ' % mls.UI_GENERIC_REGION
            text = '%s ' % mls.UI_SHARED_MAPWAYPOINT + str(waypointIndex + 1) + ': ' + extraText + targetItem.itemName + comment
            labeltext = uicls.Label(text=text, parent=label, left=210, top=7, autoheight=False, height=12, letterspace=2, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0)
            labeltext.color.SetRGB(1.0, 1.0, 0.0)
            sm.GetService('ui').BlinkSpriteA(labeltext, 1.0, 750, None, passColor=0, minA=0.5)
            location = self.map.GetItem(waypointID)
            pos = (location.x * STARMAP_SCALE, location.y * STARMAP_SCALE, location.z * STARMAP_SCALE)
            tracker.translation = pos
            self.mydestination.append(util.KeyVal(waypointID=waypointID, tracker=tracker, label=label))
            label.state = uiconst.UI_DISABLED




    def GetCurrLocationBracket(self):
        currentLocation = xtriui.MapLabel(parent=uicore.layer.map, name='currentlocation', pos=(0, 0, 280, 20), align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN, dock=False)
        white = uicls.Fill(parent=currentLocation, name='white', pos=(154, 11, 48, 1), state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOPLEFT)
        frame = uicls.Sprite(parent=currentLocation, name='frame', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/StarMapSvc/currentLocation.png')
        return currentLocation



    def IsFlat(self):
        return self.flattened



    def Unflatten(self):
        registeredScene = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
        if not self.flattened or registeredScene is None:
            return 
        try:
            uicore.desktop.state = uiconst.UI_DISABLED
            start = blue.os.GetTime()
            cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
            current = self.mapRoot.rotationCurve.GetQuaternionAt(start)
            self.mapRoot.rotationCurve.keys[0].value.SetXYZW(current.x, current.y, current.z, current.w)
            self.mapRoot.rotationCurve.keys[1].time = 1.0
            self.mapRoot.rotationCurve.keys[1].value.SetXYZW(*MAP_XYZW_ROTATION)
            self.mapRoot.rotationCurve.start = start
            redrawRoute = False
            if self.autoPilotRoute or self.genericRoute:
                redrawRoute = True
                self.ClearRoute('autoPilotRoute')
            redrawGenericRoute = False
            if self.genericRoute:
                redrawGenericRoute = True
                self.ClearRoute('genericRoute')
            if self.rollCamera:
                self.rollCamera = False
                self.starmapCamera.OrbitParent(0.0, 10.0)
            self.UpdateHexMap(isFlat=False)
            if getattr(self, 'mylocation', None):
                for each in self.mylocation.trackerTransform.children[:]:
                    if each.name == 'jumpDriveRange':
                        each.display = True

            posEnd = self.interestEndPos
            posBegin = geo2.Vector(cameraParent.translation.x, cameraParent.translation.y, cameraParent.translation.z)
            self.regionLabelParent.display = False
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / 1000.0, 1.0))
                self.mapRoot.scaling = self.solarSystemJumpLineSet.scaling = (1.0, mathUtil.Lerp(0.0001, 1.0, ndt), 1.0)
                if posBegin and posEnd:
                    pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                    cameraParent.translation.SetXYZ(*pos)
                blue.pyos.synchro.Yield()

            for labelTransform in self.regionLabelParent.children:
                (x, y, z,) = labelTransform.scaling
                labelTransform.scaling = (x, y * 0.0001, z)

            if settings.user.ui.Get('rlabel_region', 1):
                self.regionLabelParent.display = True
            self.flattened = 0
            settings.user.ui.Set('mapFlattened', self.flattened)
            sm.ScatterEvent('OnFlattenModeChanged', self.flattened)
            if redrawRoute:
                self.UpdateRoute()
            if redrawGenericRoute and self.genericRoutePath:
                self.DrawRouteTo(targetID=self.genericRoutePath[-1], sourceID=self.genericRoutePath[0])

        finally:
            uicore.desktop.state = uiconst.UI_NORMAL




    def Flatten(self, initing = False):
        if not initing:
            registeredScene = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
            if self.flattened or registeredScene is None:
                return 
        try:
            uicore.desktop.state = uiconst.UI_DISABLED
            if initing:
                duration = 0.0001
            else:
                duration = 1.0
            start = blue.os.GetTime()
            cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
            camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
            (cY, cP, cR,) = camera.rotationAroundParent.GetYawPitchRoll()
            current = self.mapRoot.rotationCurve.GetQuaternionAt(start)
            self.mapRoot.rotationCurve.keys[0].value.SetXYZW(current.x, current.y, current.z, current.w)
            self.mapRoot.rotationCurve.keys[1].time = duration
            self.mapRoot.rotationCurve.keys[1].value.SetYawPitchRoll(cY, cP - pi * 0.5, cR)
            self.mapRoot.rotationCurve.start = start
            redrawRoute = False
            if self.autoPilotRoute or self.genericRoute:
                redrawRoute = True
                self.ClearRoute('autoPilotRoute')
            redrawGenericRoute = False
            if self.genericRoute:
                redrawGenericRoute = True
                self.ClearRoute('genericRoute')
            curveQuat = geo2.QuaternionRotationSetYawPitchRoll(cY, cP - pi * 0.5, cR)
            camPos = cameraParent.translation
            posBegin = geo2.Vector(camPos.x, camPos.y, camPos.z)
            reverseQuat = MAP_XYZW_INV_ROTATION
            localCam = geo2.QuaternionTransformVector(reverseQuat, posBegin)
            localCam = geo2.Vector(*localCam)
            localCam.y = 0.0
            posEnd = geo2.QuaternionTransformVector(curveQuat, localCam)
            self.regionLabelParent.display = False
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / (duration * 1000.0), 1.0))
                self.mapRoot.scaling = self.solarSystemJumpLineSet.scaling = (1.0, mathUtil.Lerp(1.0, 0.0001, ndt), 1.0)
                if posBegin and posEnd:
                    pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                    cameraParent.translation.SetXYZ(*pos)
                blue.pyos.synchro.Yield()

            for labelTransform in self.regionLabelParent.children:
                (x, y, z,) = labelTransform.scaling
                labelTransform.scaling = (x, y * 10000.0, z)

            self.hexMap.Enable(True)
            if getattr(self, 'mylocation', None):
                for each in self.mylocation.trackerTransform.children[:]:
                    if each.name == 'jumpDriveRange':
                        each.display = False

            if settings.user.ui.Get('rlabel_region', 1):
                self.regionLabelParent.display = True
            self.flattened = 1
            settings.user.ui.Set('mapFlattened', self.flattened)
            self.UpdateHexMap(isFlat=True)
            sm.ScatterEvent('OnFlattenModeChanged', self.flattened)
            if redrawRoute:
                self.UpdateRoute()
            if redrawGenericRoute and self.genericRoutePath:
                self.DrawRouteTo(targetID=self.genericRoutePath[-1], sourceID=self.genericRoutePath[0])

        finally:
            uicore.desktop.state = uiconst.UI_NORMAL




    def ToggleFlattenMode(self):
        flattened = settings.user.ui.Get('mapFlattened', 1)
        if flattened:
            sm.GetService('starmap').Unflatten()
        else:
            sm.GetService('starmap').Flatten()



    def DrawPoints(self, parent):
        self.mapStars = trinity.EveTransform()
        self.mapStars.name = '__mapStars'
        tex = trinity.TriTexture2DParameter()
        tex.name = 'TexMap'
        tex.resourcePath = PARTICLE_SPRITE_TEXTURE
        overglowFactor = trinity.TriFloatParameter()
        overglowFactor.name = OVERGLOW_FACTOR
        overglowFactor.value = 0.0
        self.overglowFactor = overglowFactor
        self.starParticles = trinity.EveSpriteParticleSystem()
        self.starParticles.maxParticleCount = 8200
        self.starParticles.updateSimulation = False
        self.starParticles.effect = trinity.Tr2Effect()
        self.starParticles.effect.effectFilePath = PARTICLE_EFFECT
        self.starParticles.effect.resources.append(tex)
        self.starParticles.effect.parameters.append(overglowFactor)
        emitter = trinity.EveEmitterStatic()
        emitter.particleSystem = self.starParticles
        self.mapStars.particleSystems.append(self.starParticles)
        self.mapStars.particleEmitters.append(emitter)
        solarSystemList = []
        particleID = 0
        cache = self.map.GetMapCache()
        self.particleIDToSystemIDMap = {}
        self.mapNumIdx = {}
        self.particleColors = []
        cacheItems = cache['items']
        cacheHierarchy = cache['hierarchy']
        cacheSunTypes = cache['sunTypes']
        for regionID in self.map.GetKnownspaceRegions():
            self.mapNumIdx[regionID] = []
            for constellationid in cacheHierarchy[regionID].iterkeys():
                for solarSystemID in cacheHierarchy[regionID][constellationid].iterkeys():
                    solarSystemInfo = cacheItems[solarSystemID]
                    solarSystem = solarSystemInfo.item
                    solarSystemList.append(solarSystem)
                    self.mapNumIdx[solarSystemID] = particleID
                    self.particleIDToSystemIDMap[particleID] = solarSystemID
                    self.particleColors.append(list(SUN_DATA[cacheSunTypes[solarSystemID]].color))
                    particleID += 1



        self.SetSolarSystemPoints(solarSystemList, trinity.TriVector(0.0, 0.0, 0.0), emitter, 1)
        parent.children.append(self.mapStars)



    def InitMap(self):
        self.LogInfo('MapSvc: InitStarMap')
        init = False
        self.StartLoadingBar('starmap_init', mls.UI_SHARED_MAPINITINGMAP, mls.UI_SHARED_MAPBUILDINGMODEL, 4)
        if self.mapRoot is None:
            init = True
            scene = trinity.EveSpaceScene()
            self.mapRoot = trinity.EveRootTransform()
            initialRotation = trinity.TriQuaternion()
            initialRotation.SetYawPitchRoll(*MAP_ROTATION)
            nullQ = trinity.TriQuaternion()
            rotationCurve = trinity.TriRotationCurve()
            rotationCurve.extrapolation = trinity.TRIEXT_CONSTANT
            rotationCurve.AddKey(0.0, initialRotation, nullQ, nullQ, trinity.TRIINT_SQUAD)
            rotationCurve.AddKey(1.0, initialRotation, nullQ, nullQ, trinity.TRIINT_SQUAD)
            rotationCurve.Sort()
            self.mapRoot.rotationCurve = rotationCurve
            scene.objects.append(self.mapRoot)
            scene1 = trinity.TriScene()
            scene1.fogStart = -100.0
            scene1.fogEnd = 1000000.0
            scene1.update = 1
            scene1.fogEnable = 1
            scene1.fogColor.SetRGB(0.0, 0.0, 0.0)
            scene1.fogTableMode = trinity.TRIFOG_LINEAR
            scene1.pointStarfield.display = 0
            self.starmapCamera = camera = trinity.EveCamera()
            camera.idleMove = 0
            camera.friction = 25.0
            camera.translationFromParent.z = settings.user.ui.Get('starmapTFP', 0.6 * ZOOM_MAX_STARMAP)
            if camera.translationFromParent.z < 0:
                camera.translationFromParent.z = -camera.translationFromParent.z
            if not self.IsFlat():
                camera.OrbitParent(0.0, 20.0)
            landmarkTF = trinity.EveTransform()
            landmarkTF.name = '__landmarkTF'
            self.mapRoot.children.append(landmarkTF)
            self.landmarkTF = landmarkTF
            labeltrackersTF = trinity.EveTransform()
            labeltrackersTF.name = '__labeltrackersTF'
            self.mapRoot.children.append(labeltrackersTF)
            self.labeltrackersTF = labeltrackersTF
            localCameraParent = trinity.EveTransform()
            localCameraParent.name = '__localCameraParent'
            self.mapRoot.children.append(localCameraParent)
            self.localCameraParent = localCameraParent
            self.mapRoot.name = 'universe'
            self.mapRoot.display = 1
            lineSet = self.map.CreateLineSet()
            scene.objects.append(lineSet)
            self.solarSystemJumpLineSet = lineSet
            self.solarSystemJumpLineSet.rotationCurve = rotationCurve
            self.DrawPoints(self.mapRoot)
            self.DrawSystemJumpLines()
            self.cursor = trinity.EveTransform()
            self.cursor.name = '__cursorTF'
            self.mapRoot.children.append(self.cursor)
            self.uicursor = uicls.Bracket(parent=uicore.layer.map, align=uiconst.NOALIGN)
            self.uicursor.name = '__cursor'
            self.uicursor.width = uicore.uilib.desktop.width * 2
            self.uicursor.height = uicore.uilib.desktop.height * 2
            self.uicursor.state = uiconst.UI_HIDDEN
            icon = uicls.Icon(icon='ui_38_16_255', parent=self.uicursor, pos=(0, 0, 16, 16), align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0)
            self.uicursor.trackTransform = self.cursor
            self.MakeRegionLabels()
            self.uicursor.dock = False
            self.starLegend = []
            self.tileLegend = []
            if self.regionLabelParent:
                self.regionLabelParent.display = 0
            sm.GetService('sceneManager').RegisterCamera('starmap', camera)
            sm.GetService('sceneManager').RegisterScenes('starmap', scene1, scene)
            hexMapRoot = trinity.EveTransform()
            hexMapRoot.name = '__hexMapRoot'
            hexMapRoot.translation = (0.0, 20000.0, 0.0)
            self.hexMap = hexmap.HexMapController(hexMapRoot)
            self.mapRoot.children.append(hexMapRoot)
            mapFlattened = settings.user.ui.Get('mapFlattened', 1)
            if mapFlattened == 1:
                self.Flatten(initing=True)
                self.rollCamera = True
            else:
                camera.OrbitParent(0.0, 20.0)
                self.rollCamera = False
            self.SetInterest(session.solarsystemid2)
            self.RegisterStarColorModes()
        uicore.layer.map.state = uiconst.UI_PICKCHILDREN
        uicore.layer.systemmap.state = uiconst.UI_HIDDEN
        uix.GetMapNav()
        sm.GetService('sceneManager').SetRegisteredScenes('starmap')
        self.UpdateLoadingBar('starmap_init', mls.UI_SHARED_MAPINITINGMAP, mls.UI_SHARED_MAPGETTINGDATA, 1, 4)
        self.SetStarColorMode()
        self.UpdateLoadingBar('starmap_init', mls.UI_SHARED_MAPINITINGMAP, mls.UI_SHARED_MAPGETTINGDATA, 2, 4)
        self.UpdateLines(updateColor=1, hint='InitStarMap')
        self.UpdateRoute()
        self.CheckAllLabels('InitStarMap')
        self.UpdateLoadingBar('starmap_init', mls.UI_SHARED_MAPINITINGMAP, mls.UI_SHARED_MAPGETTINGDATA, 3, 4)
        self.UpdateHexMap()
        self.ShowWhereIAm()
        if init:
            self.SetInterest(session.solarsystemid2)
        self.StopLoadingBar('starmap_init')



    def GetStarPickRadius(self):
        range = ZOOM_MAX_STARMAP - ZOOM_MIN_STARMAP
        dist = self.starmapCamera.translationFromParent.z - ZOOM_MIN_STARMAP
        return PICK_RADIUS_NEAR + (PICK_RADIUS_FAR - PICK_RADIUS_NEAR) * (dist / range)



    def GetUICursor(self):
        return self.uicursor



    def ShowCursorInterest(self, solarsystemID):
        if solarsystemID:
            item = self.map.GetItem(solarsystemID)
            pos = (item.x * STARMAP_SCALE, item.y * STARMAP_SCALE, item.z * STARMAP_SCALE)
            self.cursor.translation = pos
            self.uicursor.display = True
        else:
            self.uicursor.display = False



    def GetLandmark(self, landmarkID):
        return self.map.GetMapCache()['landmarks'][landmarkID]



    def CheckAllLabels(self, hint = ''):
        if getattr(self, 'checkingalllabels', 0) or self.mapRoot is None:
            return 
        self.checkingalllabels = 1
        tomake = []
        todelete = self.labels.keys()
        interest = self.GetInterest()
        cache = self.map.GetMapCache()
        doSolarSystems = settings.user.ui.Get('label_solarsystem', 1)
        doConstellations = settings.user.ui.Get('label_constellation', 1)
        doRegions = settings.user.ui.Get('rlabel_region', 1)
        if doRegions == 0:
            if self.regionLabelParent:
                self.regionLabelParent.display = 0
        elif self.regionLabelParent:
            self.regionLabelParent.display = 1
        if self.regionLabels:
            currRegion = interest[0]
            currRegionNeightbors = self.map.GetNeighbors(currRegion)
            for regionID in self.map.GetKnownspaceRegions():
                if doRegions == 3:
                    self.regionLabels[regionID].SetDisplay(True)
                    continue
                elif doRegions == 1:
                    if regionID == interest[0]:
                        self.regionLabels[regionID].SetDisplay(True)
                    else:
                        self.regionLabels[regionID].SetDisplay(False)
                elif doRegions == 2:
                    if regionID == interest[0] or regionID in currRegionNeightbors:
                        self.regionLabels[regionID].SetDisplay(True)
                    else:
                        self.regionLabels[regionID].SetDisplay(False)

        if settings.user.ui.Get('label_landmarknames', 1):
            for landmarkID in cache['landmarks'].iterkeys():
                tomake.append(landmarkID * -1)

        if interest[2] == None:
            if interest[1] == None:
                if doConstellations:
                    tomake = tomake + self.map.GetChildren(interest[0])
            else:
                constellationID = interest[1]
                if doConstellations:
                    tomake = [constellationID] + self.map.GetNeighbors(constellationID)
                if doSolarSystems:
                    tomake = tomake + self.map.GetChildren(constellationID)
        else:
            solarsystemID = interest[2]
            if doSolarSystems and solarsystemID and not util.IsWormholeSystem(solarsystemID):
                tomake = tomake + [solarsystemID] + self.map.GetNeighbors(solarsystemID)
            solarsystemItem = self.map.GetItem(solarsystemID)
            if doConstellations and solarsystemItem and not util.IsWormholeConstellation(solarsystemItem.locationID):
                costellationID = solarsystemItem.locationID
                tomake.append(costellationID)
        if doSolarSystems:
            for wayPointID in self.GetDestinationPath():
                if wayPointID not in tomake and wayPointID is not None:
                    tomake.append(wayPointID)

        if hasattr(self, 'focusLabel'):
            if self.focusLabel is not None and self.focusLabel not in tomake:
                tomake.append(self.focusLabel)
        new = [ id for id in tomake if id not in todelete ]
        old = [ id for id in todelete if id not in tomake ]
        self.ClearLabels(old)
        self.CreateLabels(new)
        self.CheckLabelDist()
        self.checkingalllabels = 0



    def GetNeighbors(self, itemID):
        if util.IsWormholeSystem(itemID) or util.IsWormholeConstellation(itemID) or util.IsWormholeRegion(itemID):
            return []
        else:
            cache = self.map.GetMapCache()
            if itemID in cache['neighbors']:
                return cache['neighbors'][itemID]
            item = self.map.GetItem(itemID, 1)
            ssitem = item.item
            if ssitem.groupID == const.typeSolarSystem:
                return [ locID for jumpgroup in item.jumps for locID in jumpgroup ]
            return []



    def CheckLabelDist(self):
        if self.mapRoot is None:
            return 
        uthread.new(self.CheckCloudLabels, 'checkLabelDist')



    def CheckCloudLabels(self, reason = ''):
        if doingDebug == 1:
            self.LogInfo('checkloudlabels ', reason)
        if getattr(self, 'checkinglabels', 0):
            return 
        setattr(self, 'checkinglabels', 1)
        sel = self.GetInterest()
        dst = self.GetDestination()
        for label in self.labels.itervalues():
            if label is not None and not label.destroyed:
                if len(label.children):
                    if label.sr.id in sel or label.sr.id == getattr(self, 'highlightLabel', -1) or label.sr.id == dst:
                        label.children[0].color.a = 1.0
                    else:
                        label.children[0].color.a = 0.7

        setattr(self, 'checkinglabels', 0)



    def GetStarData(self):
        return getattr(self, 'starData', {})



    def GetPickRay(self, x, y):
        dev = trinity.GetDevice()
        (proj, view, vp,) = uix.GetFullscreenProjectionViewAndViewport()
        (ray, start,) = dev.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
        return util.KeyVal(normal=(ray.x, ray.y, ray.z), startPos=(start.x, start.y, start.z))



    def TranslateCamera(self, x, y, dx, dy):
        self.interestEndPos = None
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
        toRay = self.GetPickRay(x, y)
        fromRay = self.GetPickRay(x - dx, y - dy)
        pos = cameraParent.translation
        planePoint = (pos.x, pos.y, pos.z)
        viewVec = camera.viewVec
        viewVec = (viewVec.x, viewVec.y, viewVec.z)
        pickPlane = geo2.PlaneFromPointNormal(planePoint, viewVec)
        toPoint = geo2.PlaneIntersectLine(pickPlane, toRay.startPos, toRay.startPos + geo2.Vector(*toRay.normal) * 1000000.0)
        if toPoint is None:
            return 
        fromPoint = geo2.PlaneIntersectLine(pickPlane, fromRay.startPos, fromRay.startPos + geo2.Vector(*fromRay.normal) * 1000000.0)
        if fromPoint is None:
            return 
        offset = geo2.Vector(*fromPoint) - toPoint
        cameraParent.translation += trinity.TriVector(*offset)
        uthread.new(self.CheckLabelDist)



    def GetWorldPosFromLocalCoord(self, vector = None, flatten = True):
        pos = geo2.Vector(*(vector or self.localCameraParent.translation))
        if flatten and self.IsFlat():
            pos.y = 0.0
        curveQuat = self.mapRoot.rotationCurve.value
        curveQuat = (curveQuat.x,
         curveQuat.y,
         curveQuat.z,
         curveQuat.w)
        pos = geo2.QuaternionTransformVector(curveQuat, pos)
        return geo2.Vector(*pos)



    def SetInterest(self, itemID = None, forceframe = None, forcezoom = None):
        if forceframe is None:
            forceframe = settings.user.ui.Get('mapautoframe', 1)
        if forcezoom is None:
            forcezoom = settings.user.ui.Get('mapautozoom', 0)
        self.LogInfo('Map Setinterest ', itemID)
        if doingDebug == 1:
            self.LogInfo('setinterest ', itemID, forceframe)
        if self.mapRoot is None:
            return 
        dollyEndval = None
        camDuration = None
        interest = self.GetInterest()
        cache = self.map.GetMapCache()
        itemID = itemID or interest[2] or interest[1] or interest[0] or eve.session.regionid
        endPos = self.GetWorldPosFromLocalCoord(flatten=True)
        self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
        if itemID is None:
            return 
        if itemID == const.locationUniverse:
            pos = geo2.Vector(0.0, 0.0, 0.0)
            dollyEndval = 20000.0
        elif itemID < 0:
            lm = cache['landmarks'][(itemID * -1)]
            pos = geo2.Vector(lm.x, lm.y, lm.z)
            pos *= STARMAP_SCALE
            self.localCameraParent.translation = pos
            endPos = self.GetWorldPosFromLocalCoord(flatten=True)
            self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
        else:
            item = self.map.GetItem(itemID)
            if item is None:
                return 
            self.UpdateLines(item.itemID, hint='SetInterest')
            if item.typeID == const.typeSolarSystem:
                interest[0] = cache['parents'][cache['parents'][item.itemID]]
                interest[1] = cache['parents'][item.itemID]
                interest[2] = item.itemID
            elif item.typeID == const.typeConstellation:
                interest[0] = cache['parents'][item.itemID]
                interest[1] = item.itemID
                interest[2] = None
            elif item.typeID == const.groupRegion and self.regionLabels:
                interest[0] = item.itemID
                interest[1] = None
                interest[2] = None
                for regionID in self.map.GetKnownspaceRegions():
                    self.regionLabels[regionID].SetHighlight(False)

                if not util.IsWormholeRegion(itemID):
                    self.regionLabels[item.itemID].SetHighlight(True)
            if util.IsWormholeRegion(interest[0]):
                item = self.map.GetItem(30005204)
            pos = geo2.Vector(item.x, 0.0 if self.IsFlat() else item.y, item.z)
            pos *= STARMAP_SCALE
            camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
            dollyEndval = camera.translationFromParent.z
            if forceframe and forcezoom:
                if util.IsSolarSystem(item.itemID):
                    dollyEndval = ZOOM_MIN_STARMAP + (ZOOM_MAX_STARMAP - ZOOM_MIN_STARMAP) * 0.05
                else:
                    mx = abs(item.xMin) + item.xMax
                    my = abs(item.yMin) + item.yMax
                    mz = abs(item.zMin) + item.zMax
                    size = geo2.Vector(mx * STARMAP_SCALE, my * STARMAP_SCALE, mz * STARMAP_SCALE)
                    radius = max(*size) * 0.5
                    camangle = camera.fieldOfView * 0.5
                    dollyEndval = radius / sin(camangle) * cos(camangle)
            self.localCameraParent.translation = pos
            endPos = self.GetWorldPosFromLocalCoord()
            self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
            cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
            mapPos = geo2.Vector(cameraParent.translation.x, cameraParent.translation.y, cameraParent.translation.z)
            camDuration = max(0.25, min(1.0, geo2.Vec3Length(endPos - mapPos) * 1e-05))
        if self.mapRoot is None:
            return 
        if forceframe:
            uthread.new(self.MoveInterest, endPos, (camDuration or 0.2) * 1000.0)
            if forcezoom and dollyEndval is not None:
                self.Dolly(dollyEndval, camDuration or 0.2, 1)
        self.CheckAllLabels('SetInterest')
        self.UpdateLines()



    def MoveInterest(self, posEnd, time = 500.0):
        uicore.desktop.state = uiconst.UI_DISABLED
        count = 50
        while getattr(self, 'moving', False) and count:
            blue.pyos.synchro.Sleep(100)
            count -= 1

        try:
            try:
                self.moving = True
                cameraParent = sm.GetService('camera').GetCameraParent(source='starmap')
                startPos = cameraParent.translation
                posBegin = geo2.Vector(startPos.x, startPos.y, startPos.z)
                start = blue.os.GetTime()
                ndt = 0.0
                while ndt != 1.0:
                    ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                    if posBegin and posEnd:
                        pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                        cameraParent.translation.SetXYZ(*pos)
                    blue.pyos.synchro.Yield()

            except AttributeError:
                pass

        finally:
            uicore.desktop.state = uiconst.UI_NORMAL
            self.moving = False




    def Dolly(self, end, length = 2.0, updatelabels = 0):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('starmap')
        beg = camera.translationFromParent.z
        end = sm.GetService('camera').CheckTranslationFromParent(end, source='starmap')
        sm.GetService('camera').PanCamera(None, None, beg, end, time=length * 1000.0, source='starmap')
        self.CheckLabelDist()



    def MakeRegionLabels(self):
        self.LogInfo('MakeRegionLabels')
        regionLabelParent = trinity.EveTransform()
        regionLabelParent.display = 0
        self.mapRoot.children.append(regionLabelParent)
        regionLabelParent.name = '__regionLabels'
        self.regionLabels = {}
        for regionID in self.map.GetKnownspaceRegions():
            regionItem = self.map.GetItem(regionID)
            label = xtriui.TransformableLabel(regionItem.itemName, regionLabelParent, size=127)
            label.transform.translation = (regionItem.x * STARMAP_SCALE, regionItem.y * STARMAP_SCALE, regionItem.z * STARMAP_SCALE)
            label.transform.scaling = geo2.Vector(*label.transform.scaling) * REGION_LABEL_SCALE
            label.SetDisplay(False)
            self.regionLabels[regionID] = label

        self.regionLabelParent = regionLabelParent



    def DrawRouteTo(self, targetID, verbose = 1, sourceID = None):
        self.LogInfo('DrawRouteTo ', targetID)
        if targetID == eve.session.solarsystemid2:
            self.ClearRoute('genericRoute')
            return 
        targetItem = self.map.GetItem(targetID)
        if targetID in [eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid]:
            return []
        routeList = self.ShortestGeneralPath(targetID, sourceID=sourceID)
        self.ClearRoute('genericRoute')
        route = xtriui.MapRoute()
        route.DrawRoute(routeList, flattened=self.flattened, rotationQuaternion=self.GetCurrentStarmapRotation())
        self.genericRoute = route
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
        scene2.objects.append(route.model)
        if not len(routeList):
            if self.map.ViewingStarMap():
                if verbose == 1:
                    eve.Message('Command', {'command': '%s ' % mls.UI_SHARED_MAPNOPATHFOUND + targetItem.itemName + '.'})
            return []
        self.CheckAllLabels('DrawRouteTo')
        if self.map.ViewingStarMap():
            if verbose == 1:
                jumptype = ''
                if targetItem.groupID == const.typeRegion:
                    jumptype = ' ' + mls.UI_GENERIC_REGION
                hopCount = len(routeList) - 1
                if sourceID:
                    sourceItem = self.map.GetItem(sourceID)
                    eve.Message('Command', {'command': mls.UI_SHARED_MAPTHEPATHBETWEENWILLTAKEYOU % {'path': self.GetRouteType(1),
                                 'startlocation': sourceItem.itemName,
                                 'endlocation': targetItem.itemName,
                                 'hops': hopCount,
                                 'jumptype': jumptype,
                                 'jump': uix.Plural(hopCount, 'UI_GENERIC_JUMP')}})
                else:
                    eve.Message('Command', {'command': mls.UI_SHARED_MAPTHEPATHWILLTAKEYOU % {'path': self.GetRouteType(1),
                                 'endlocation': targetItem.itemName,
                                 'hops': hopCount,
                                 'jumptype': jumptype,
                                 'jump': uix.Plural(hopCount, 'UI_GENERIC_JUMP')}})
        self.genericRoutePath = routeList
        self.UpdateLines(updateColor=1)
        return routeList



    def RemoveGenericPath(self):
        self.genericRoutePath = None
        self.ClearRoute('genericRoute')
        self.UpdateLines(updateColor=True)



    def ClearRoute(self, routeName = 'autoPilotRoute'):
        route = getattr(self, routeName, None)
        if route:
            scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
            if route.model in scene2.objects:
                scene2.objects.fremove(route.model)
            setattr(self, routeName, None)



    def Dijkstra(self, start, end):
        D = {}
        P = {}
        Q = PriorityDictionary()
        Q[start] = 0.0
        securityBias = float(settings.user.ui.Get('autopilot_safety', 0) - 1)
        if settings.user.ui.Get('autopilot_safety', 0) == 3:
            omitUnsafe = 1
            securityBias = 0.0
        else:
            omitUnsafe = 0
        AVOIDPODKILLS = settings.user.ui.Get('autopilot_avoidpodkill', 0) == 1
        if AVOIDPODKILLS:
            historyDB = sm.RemoteSvc('map').GetHistory(3, 24)
            killsites = {}
            for each in historyDB:
                if each.value3 > 0:
                    killsites[each.solarSystemID] = each.value3

            killsiteL = killsites.keys()
        cache = self.map.GetMapCache()
        for v in Q:
            D[v] = Q[v]
            if v == end:
                break
            item = self.map.GetItem(v, 1)
            ssitem = item[0]
            if ssitem.groupID == const.typeRegion:
                dests = cache['neighbors'][v]
            else:
                dests = [ locID for jumpgroup in item[2] for locID in jumpgroup ]
            for w in dests:
                if securityBias == 0.0:
                    vwLength = D[v] + 1.0
                else:
                    destSec = self.map.GetSecurityStatus(w) - 0.5
                    if securityBias * destSec > 0.0:
                        vwLength = D[v] + 1000000.0
                    else:
                        destSec = destSec * securityBias
                        vwLength = D[v] + 0.1 + (0.5 + destSec) * 1.0
                if AVOIDPODKILLS:
                    if w in killsiteL:
                        vwLength = D[v] + 10000000000.0
                if w in D:
                    if vwLength < D[w]:
                        raise ValueError, 'Dijkstra: found better path to already-final vertex'
                elif w not in Q or vwLength < Q[w]:
                    Q[w] = vwLength
                    P[w] = v


        return (D, P)



    def ShortestPath(self, start, end):
        return sm.GetService('pathfinder').GetPathBetween(start, end) or []



    def ShortestGeneralPath(self, targetID, sourceID = None):
        targetItem = self.map.GetItem(targetID)
        if sourceID == None:
            sourceID = eve.session.solarsystemid2
        cache = self.map.GetMapCache()
        if targetItem.groupID == const.typeConstellation:
            targets = self.map.GetChildren(targetID)
            regionID = self.map.GetItem(targetID, 1).hierarchy[0]
        elif targetItem.groupID == const.typeRegion:
            targets = []
            constellations = self.map.GetChildren(targetID)
            for constellationID in constellations:
                solarsystems = self.map.GetChildren(constellationID)
                for solarsystemID in solarsystems:
                    solarSystemInfo = cache['items'][solarsystemID]
                    regionJumps = solarSystemInfo.jumps[0]
                    targets += regionJumps


        else:
            targets = [targetID]
        paths = []
        for target in targets:
            routeList = self.ShortestPath(sourceID, target)
            if routeList:
                paths.append([len(routeList), routeList])

        paths.sort()
        if not len(paths):
            return paths
        return paths[0][1]



    def GetAllFactions(self):
        factions = {}
        cache = self.map.GetMapCache()
        for regionID in cache['hierarchy'].iterkeys():
            for constellationid in cache['hierarchy'][regionID].iterkeys():
                for solarSystemID in cache['hierarchy'][regionID][constellationid].iterkeys():
                    solarSystemInfo = cache['items'][solarSystemID]
                    solarsystem = solarSystemInfo.item
                    if solarsystem.factionID is not None:
                        factions[solarsystem.factionID] = 1



        return factions.keys()



    def GetAllianceSolarSystems(self):
        self.allianceSolarSystems = {'s': {},
         'c': {}}
        allianceSolarSystems = {}
        getMapping = 's'
        if self.allianceSolarSystems[getMapping]:
            return self.allianceSolarSystems[getMapping]
        allianceSystemCache = sm.RemoteSvc('stationSvc').GetAllianceSystems()
        for x in allianceSystemCache:
            allianceSolarSystems[x.solarSystemID] = x.allianceID

        self.allianceSolarSystems[getMapping] = allianceSolarSystems
        return self.allianceSolarSystems[getMapping]



    def GetAllFactionsAndAlliances(self):
        factionsAndAlliances = {}
        allianceSolarSystems = self.GetAllianceSolarSystems()
        for solarSystemID in self.map.IterateSolarSystemIDs():
            solarsystem = self.map.GetItem(solarSystemID)
            if solarsystem.factionID is not None:
                factionsAndAlliances[solarsystem.factionID] = 1
            elif allianceSolarSystems.has_key(solarSystemID):
                factionsAndAlliances[allianceSolarSystems[solarSystemID]] = 1

        return factionsAndAlliances.keys()



    def GetDestination(self):
        if self.destinationPath != [None]:
            return self.destinationPath[-1]



    def GetDestinationPath(self):
        if not len(self.destinationPath):
            return [None]
        return self.destinationPath



    def GetFactionColor(self, factionID):
        if not hasattr(self, 'factionColors'):
            self.factionColors = {}
        if factionID not in self.factionColors:
            col = trinity.TriColor()
            hue = factionID * 12.345 * 3.0
            s = factionID % 2 * 0.5 + 0.5
            col.SetHSV(hue % 360.0, s, 1.0)
            self.factionColors[factionID] = col
        return self.factionColors[factionID]



    def GetFactionOrAllianceColor(self, entityID):
        if not hasattr(self, 'factionOrAllianceColors'):
            self.factionOrAllianceColors = {}
        if entityID not in self.factionOrAllianceColors:
            col = trinity.TriColor()
            hue = entityID * 12.345 * 3.0
            s = entityID % 2 * 0.5 + 0.5
            col.SetHSV(hue % 360.0, s, 1.0)
            self.factionOrAllianceColors[entityID] = col
        return self.factionOrAllianceColors[entityID]



    def DrawSystemJumpLines(self):
        cache = self.map.GetMapCache()
        self.solarSystemJumpIDdict = cache['solarSystemJumpIDdict']
        self.jumpLines = self.solarSystemJumpIDdict['jumpLines']
        self.jumpLineInfoByLineID = {}
        for info in self.jumpLines:
            self.jumpLineInfoByLineID[info.lineID] = info

        lineSet = self.solarSystemJumpLineSet
        for info in self.jumpLines:
            lineSet.AddLine(info.fromPos, info.fromColor, info.toPos, info.toColor)

        lineSet.SubmitChanges()



    def SetSolarSystemPoints(self, solarSystemList, regionPos, emitter, randomizeFrame = 0, sFactor = None, size = None):
        if sFactor is None:
            sFactor = STARMAP_SCALE
        if size is None:
            size = SUNBASE
        solarSystemIDs = []
        emitter.particleSystem.ClearParticles()
        sunTypeMap = self.map.GetMapCache()['sunTypes']
        for solarsystem in solarSystemList:
            star = SUN_DATA[sunTypeMap[solarsystem.itemID]]
            pos = (solarsystem.x * STARMAP_SCALE, solarsystem.y * STARMAP_SCALE, solarsystem.z * STARMAP_SCALE)
            newParticle = trinity.EveEmitterStaticData()
            newParticle.size = SUNBASE
            newParticle.position = pos
            newParticle.color = star.color
            emitter.particleData.append(newParticle)
            solarSystemIDs.append(solarsystem.itemID)

        return solarSystemIDs



    def UpdateLines(self, hiliteID = None, updateColor = 0, showlines = None, hint = '', path = None):
        if showlines is None:
            showlines = settings.user.ui.Get('showlines', SHOW_ALL)
        interest = self.GetInterest()
        if showlines == SHOW_NONE:
            self.SetJumpLineAlpha(0.0)
        elif hiliteID == None:
            hiliteID = interest[2] or interest[1] or interest[0]
        hiliteItem = self.map.GetItem(hiliteID, 1)
        if showlines == SHOW_ALL:
            self.SetJumpLineAlpha(0.35)
        else:
            self.SetJumpLineAlpha(0.0)
            if showlines > SHOW_SELECTION:
                regionsToShow = [interest[0]]
                if showlines == SHOW_NEIGHBORS:
                    regionsToShow = regionsToShow + self.map.GetNeighbors(interest[0])
                self.SetJumpLineAlpha(0.0)
                for regionID in regionsToShow:
                    constellations = self.map.GetChildren(regionID)
                    IDsToSet = []
                    lineIDs = []
                    for constellationID in constellations:
                        IDsToSet.extend(self.map.GetChildren(constellationID))

                    for solID in IDsToSet:
                        newLineIDs = self.solarSystemJumpIDdict[solID]
                        lineIDs.extend(map(lambda i: i[0], newLineIDs))

                    self.SetJumpLineAlpha(0.35, lineIDs)

        if hiliteItem:
            if hiliteItem.item.typeID == const.typeSolarSystem:
                done = [hiliteID]
                lineIDs = self.solarSystemJumpIDdict[hiliteID]
                self.SetJumpLineAlpha(1.0, [ lineID for (lineID, solarSystemID,) in lineIDs ])
                for neighborID in [ locID for jumpgroup in hiliteItem.jumps for locID in jumpgroup ]:
                    lineIDs = self.solarSystemJumpIDdict[neighborID]
                    done.append(neighborID)
                    self.SetJumpLineAlpha(0.6, [ lineID for (lineID, solarSystemID,) in lineIDs ])

            elif hiliteItem.item.typeID == const.typeConstellation:
                solarSystemIDs = self.map.GetChildren(hiliteID)
                lineIDs = []
                for solID in solarSystemIDs:
                    newLineIDs = self.solarSystemJumpIDdict[solID]
                    lineIDs.extend([ lineID for (lineID, solarSystemID,) in newLineIDs ])

                self.SetJumpLineAlpha(1.0, lineIDs)
            elif hiliteItem.item.typeID == const.typeRegion:
                constellations = self.map.GetChildren(hiliteID)
                IDsToSet = []
                lineIDs = []
                for constellationID in constellations:
                    IDsToSet.extend(self.map.GetChildren(constellationID))

                for solID in IDsToSet:
                    newLineIDs = self.solarSystemJumpIDdict[solID]
                    lineIDs.extend([ lineID for (lineID, solarSystemID,) in newLineIDs ])

                self.SetJumpLineAlpha(1.0, lineIDs)
        if updateColor:
            self.UpdateLineColor()
        if path:
            self.ShowPath(path)
        if self.genericRoutePath:
            self.ShowPath(self.genericRoutePath)
        self.ShowDestinationPath()
        self.solarSystemJumpLineSet.SubmitChanges()



    def SetJumpLineAlpha(self, alpha, lineIDs = None):
        lineSet = self.solarSystemJumpLineSet
        if lineIDs is None:
            lineIDs = [ info.lineID for info in self.jumpLines ]
        for id in lineIDs:
            fromColor = self.jumpLines[id].fromColor
            toColor = self.jumpLines[id].toColor
            fromColor[3] = alpha
            toColor[3] = alpha
            lineSet.ChangeLineColor(id, fromColor, toColor)




    def SetJumpLineColor(self, color, lineIDs = None):
        lineSet = self.solarSystemJumpLineSet
        if lineIDs is None:
            lineIDs = [ info.lineID for info in self.jumpLines ]
        for id in lineIDs:
            fromColor = self.jumpLines[id].fromColor
            toColor = self.jumpLines[id].toColor
            for (i, val,) in enumerate(color):
                fromColor[i] = val
                toColor[i] = val

            lineSet.ChangeLineColor(id, fromColor, toColor)




    def SetJumpLineColors(self, lineIDs, fromColor, toColor):
        lineSet = self.solarSystemJumpLineSet
        for id in lineIDs:
            _fromColor = self.jumpLines[id].fromColor
            _toColor = self.jumpLines[id].toColor
            for (i, val,) in enumerate(fromColor):
                _fromColor[i] = val

            for (i, val,) in enumerate(toColor):
                _toColor[i] = val

            lineSet.ChangeLineColor(id, _fromColor, _toColor)




    def SetJumpLineColorAt(self, lineID, atID, color):
        lineSet = self.solarSystemJumpLineSet
        info = self.jumpLines[lineID]
        if atID == info.fromID:
            changeColor = info.fromColor
        else:
            changeColor = info.toColor
        for (i, val,) in enumerate(color):
            changeColor[i] = val

        lineSet.ChangeLineColor(lineID, info.fromColor, info.toColor)



    def SetJumpLineAlphaAt(self, lineID, atID, alpha):
        lineSet = self.solarSystemJumpLineSet
        info = self.jumpLines[lineID]
        if atID == info.fromID:
            info.fromColor[3] = alpha
        else:
            info.toColor[3] = alpha
        lineSet.ChangeLineColor(lineID, info.fromColor, info.toColor)



    def SetStarParticleAlpha(self, alpha, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleIDs = xrange(len(self.particleColors))
        for id in particleIDs:
            color = self.particleColors[id]
            color[3] = alpha
            particleSystem.SetParticleColor(id, color)




    def SetStarParticleColor(self, color, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleIDs = xrange(len(self.particleColors))
        for id in particleIDs:
            rbga = self.particleColors[id]
            for (i, val,) in enumerate(color):
                rbga[i] = val

            particleSystem.SetParticleColor(id, color)




    def SetStarParticleSize(self, size, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleIDs = xrange(len(self.particleColors))
        for id in particleIDs:
            particleSystem.SetParticleSize(id, size)




    def UpdateLineColor(self):
        colorMode = settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM)
        if colorMode == mapcommon.COLORMODE_UNIFORM:
            for jumpType in JUMP_TYPES:
                lineIDs = self.solarSystemJumpIDdict['jumpType'][jumpType]
                self.SetJumpLineColor(JUMP_COLORS[jumpType][:3], lineIDs)

        elif colorMode == mapcommon.COLORMODE_REGION:
            if not hasattr(self, 'regionJumpColorList'):
                self.regionJumpColorList = []
                for info in self.jumpLines:
                    fromColor = self.GetRegionColor(self.map.GetRegionForSolarSystem(info.fromID))
                    toColor = self.GetRegionColor(self.map.GetRegionForSolarSystem(info.toID))
                    self.regionJumpColorList.append(([info.lineID], (fromColor.r, fromColor.g, fromColor.b), (toColor.r, toColor.g, toColor.b)))

            for (lineID, formColor, toColor,) in self.regionJumpColorList:
                self.SetJumpLineColors(lineID, formColor, toColor)

        elif colorMode == mapcommon.COLORMODE_STANDINGS:
            colorByFaction = {}
            for factionID in self.GetAllFactionsAndAlliances():
                colorByFaction[factionID] = self.GetColorByStandings(factionID)

            allianceSolarSystems = self.GetAllianceSolarSystems()
            for info in self.jumpLines:
                fromColor = colorByFaction.get(self._GetFactionIDFromSolarSystem(allianceSolarSystems, info.fromID), mapcommon.COLOR_STANDINGS_NEUTRAL)
                toColor = colorByFaction.get(self._GetFactionIDFromSolarSystem(allianceSolarSystems, info.toID), mapcommon.COLOR_STANDINGS_NEUTRAL)
                self.SetJumpLineColors([info.lineID], fromColor, toColor)




    def GetColorByStandings(self, factionID):
        if factionID == session.allianceid:
            return mapcommon.COLOR_STANDINGS_GOOD
        standingSvc = sm.StartService('standing')
        standings = [standingSvc.GetStanding(session.charid, factionID) or 0, standingSvc.GetStanding(session.corpid, factionID) or 0, standingSvc.GetStanding(session.allianceid, factionID) or 0]
        standings = [ s for s in standings if s != 0 ]
        standing = 0 if len(standings) == 0 else max(standings)
        if standing == 0:
            color = mapcommon.COLOR_STANDINGS_NEUTRAL
        elif standing > 0:
            color = mapcommon.COLOR_STANDINGS_GOOD
        else:
            color = mapcommon.COLOR_STANDINGS_BAD
        return color



    def _GetFactionIDFromSolarSystem(self, allianceSolarSystems, solarSystemID):
        if solarSystemID in allianceSolarSystems:
            return allianceSolarSystems[solarSystemID]
        else:
            return self.map.GetItem(solarSystemID).factionID



    def ShowPath(self, path):
        if path:
            linesToHighlight = []
            for a in range(len(path) - 1):
                fromID = path[a]
                toID = path[1:][a]
                linesToHighlight.append(self.solarSystemJumpIDdict[(fromID, toID)][0])

            self.SetJumpLineColor((1.0, 0.5, 0.0, 0.8), linesToHighlight)



    def ShowDestinationPath(self):
        if self.destinationPath[0] is not None:
            lineSet = self.solarSystemJumpLineSet
            destPath = self.destinationPath
            if destPath[0] != eve.session.solarsystemid2:
                destPath = [eve.session.solarsystemid2] + destPath
            for a in range(len(destPath) - 1):
                fromID = destPath[a]
                toID = destPath[1:][a]
                (lineID, id1,) = self.solarSystemJumpIDdict[(fromID, toID)]
                if fromID == id1:
                    id2 = toID
                else:
                    id1 = toID
                    id2 = fromID
                rawSec1 = self.map.GetSecurityStatus(id1)
                rawSec2 = self.map.GetSecurityStatus(id2)
                (sec1, color1,) = util.FmtSystemSecStatus(rawSec1, 1)
                (sec2, color2,) = util.FmtSystemSecStatus(rawSec2, 1)
                lineSet.ChangeLineColor(lineID, (color1.r,
                 color1.g,
                 color1.b,
                 1.0), (color2.r,
                 color2.g,
                 color2.b,
                 1.0))




    def HighlightNeighborStars(self, solarSystemID = None, distance = 1):
        interest = self.GetInterest()
        if solarSystemID == None:
            solarSystemID = interest[2]
        self.SetStarParticleAlpha(0.5)
        done = [solarSystemID]
        pointIDs = [self.mapNumIdx[solarSystemID]]
        self.SetStarParticleAlpha(1.0, pointIDs)
        solarSystemItem = self.map.GetItem(solarSystemID, 1)
        for neighborID in [ locID for jumpgroup in solarSystemItem.jumps for locID in jumpgroup ]:
            pointIDs = [self.mapNumIdx[neighborID]]
            done.append(neighborID)
            self.SetStarParticleAlpha(0.8, pointIDs)

        for neighborID in [ locID for jumpgroup in solarSystemItem.jumps for locID in jumpgroup ]:
            neighborSystemItem = self.map.GetItem(neighborID, 1)
            for subneighborID in [ locID for jumpgroup in neighborSystemItem.jumps for locID in jumpgroup ]:
                if subneighborID in done:
                    continue
                pointIDs = [self.mapNumIdx[subneighborID]]
                done.append(subneighborID)
                self.SetStarParticleAlpha(0.7, pointIDs)





    def RegisterStarColorModes(self):
        self.starColorHandlers = {mapcommon.STARMODE_ASSETS: (mls.UI_SHARED_MAPSHOWASSETS, starmap.ColorStarsByAssets),
         mapcommon.STARMODE_VISITED: (mls.UI_SHARED_MAPSHOWVISITEDSYSTEMS, starmap.ColorStarsByVisited),
         mapcommon.STARMODE_SECURITY: (mls.UI_SHARED_MAPSECSTATUS, starmap.ColorStarsBySecurity),
         mapcommon.STARMODE_INDEX_STRATEGIC: (mls.SOVEREIGNTY_STRATEGIC,
                                              starmap.ColorStarsByDevIndex,
                                              const.attributeDevIndexSovereignty,
                                              mls.SOVEREIGNTY_STRATEGIC),
         mapcommon.STARMODE_INDEX_MILITARY: (mls.UI_TUTORIAL_MILITARY,
                                             starmap.ColorStarsByDevIndex,
                                             const.attributeDevIndexMilitary,
                                             mls.UI_TUTORIAL_MILITARY),
         mapcommon.STARMODE_INDEX_INDUSTRY: (mls.UI_TUTORIAL_INDUSTRY,
                                             starmap.ColorStarsByDevIndex,
                                             const.attributeDevIndexIndustrial,
                                             mls.UI_TUTORIAL_INDUSTRY),
         mapcommon.STARMODE_SOV_CHANGE: (mls.SOVEREIGNTY_RECENTCHANGES, starmap.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_ALL),
         mapcommon.STARMODE_SOV_GAIN: (mls.SOVEREIGNTY_SOVGAIN, starmap.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_SOV_GAIN),
         mapcommon.STARMODE_SOV_LOSS: (mls.SOVEREIGNTY_SOVLOSS, starmap.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_SOV_LOST),
         mapcommon.STARMODE_OUTPOST_GAIN: (mls.SOVEREIGNTY_STATIONGAIN, starmap.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_OUTPOST_GAIN),
         mapcommon.STARMODE_OUTPOST_LOSS: (mls.SOVEREIGNTY_STATIONLOSS, starmap.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_OUTPOST_LOST),
         mapcommon.STARMODE_SOV_STANDINGS: (mls.UI_GENERIC_STANDINGS, starmap.ColorStarsByFactionStandings),
         mapcommon.STARMODE_FACTION: (mls.UI_SHARED_MAPSOVEREIGNTYMAP, starmap.ColorStarsByFaction),
         mapcommon.STARMODE_FACTIONEMPIRE: (mls.UI_SHARED_MAPSOVEREIGNTYMAP, starmap.ColorStarsByFaction),
         mapcommon.STARMODE_MILITIA: (mls.UI_SHARED_OCCUPANCY, starmap.ColorStarsByMilitia),
         mapcommon.STARMODE_MILITIAOFFENSIVE: (mls.UI_SHARED_MAPSHOWSOCCUPANCY, starmap.ColorStarsByMilitiaActions),
         mapcommon.STARMODE_MILITIADEFENSIVE: (mls.UI_SHARED_MAPSHOWSOCCUPANCY, starmap.ColorStarsByMilitiaActions),
         mapcommon.STARMODE_REGION: (mls.UI_SHARED_MAPCOLORSTARSMYREG, starmap.ColorStarsByRegion),
         mapcommon.STARMODE_CARGOILLEGALITY: (mls.UI_SHARED_MAPOPS26, starmap.ColorStarsByCargoIllegality),
         mapcommon.STARMODE_PLAYERCOUNT: ('%s %s' % (mls.UI_GENERIC_SHOW, mls.UI_SHARED_MAPPILOTSINSPACE), starmap.ColorStarsByNumPilots),
         mapcommon.STARMODE_PLAYERDOCKED: ('%s %s' % (mls.UI_GENERIC_SHOW, mls.UI_SHARED_MAPPILOTSDOCKED), starmap.ColorStarsByNumPilots),
         mapcommon.STARMODE_STATIONCOUNT: (mls.UI_SHARED_MAPSHOWSTATIONCOUNT, starmap.ColorStarsByStationCount),
         mapcommon.STARMODE_DUNGEONS: (mls.UI_SHARED_MAPSHOWDEADSPACECOMPL, starmap.ColorStarsByDungeons),
         mapcommon.STARMODE_DUNGEONSAGENTS: (mls.UI_SHARED_MAPSHOWAGENTSITES, starmap.ColorStarsByDungeons),
         mapcommon.STARMODE_JUMPS1HR: (mls.UI_SHARED_MAPSHOWRECENTJUMPS, starmap.ColorStarsByJumps1Hour),
         mapcommon.STARMODE_SHIPKILLS1HR: (mls.UI_SHARED_MAPSHOWSHIPSDESTROYED,
                                           starmap.ColorStarsByKills,
                                           3,
                                           1),
         mapcommon.STARMODE_SHIPKILLS24HR: (mls.UI_SHARED_MAPSHOWSHIPSDESTROYED,
                                            starmap.ColorStarsByKills,
                                            3,
                                            24),
         mapcommon.STARMODE_MILITIAKILLS1HR: (mls.UI_SHARED_MAPSHOWMILITIASHIPSDESTROYED,
                                              starmap.ColorStarsByKills,
                                              5,
                                              1),
         mapcommon.STARMODE_MILITIAKILLS24HR: (mls.UI_SHARED_MAPSHOWMILITIASHIPSDESTROYED,
                                               starmap.ColorStarsByKills,
                                               5,
                                               24),
         mapcommon.STARMODE_PODKILLS1HR: (mls.UI_SHARED_MAPSHOWMILITIASHIPSDESTROYED, starmap.ColorStarsByPodKills),
         mapcommon.STARMODE_PODKILLS24HR: (mls.UI_SHARED_MAPSHOWMILITIASHIPSDESTROYED, starmap.ColorStarsByPodKills),
         mapcommon.STARMODE_FACTIONKILLS1HR: (mls.UI_SHARED_MAPSHOWFACTIONSHIPS, starmap.ColorStarsByFactionKills),
         mapcommon.STARMODE_BOOKMARKED: (mls.UI_SHARED_MAPSHOWBOOKMARKS, starmap.ColorStarsByBookmarks),
         mapcommon.STARMODE_CYNOSURALFIELDS: (mls.UI_SHARED_MAPACTIVECYNO, starmap.ColorStarsByCynosuralFields),
         mapcommon.STARMODE_CORPOFFICES: (mls.UI_SHARED_MAPSHOWASSETS,
                                          starmap.ColorStarsByCorpAssets,
                                          'offices',
                                          mls.UI_CORP_OFFICES),
         mapcommon.STARMODE_CORPIMPOUNDED: (mls.UI_SHARED_MAPSHOWASSETS,
                                            starmap.ColorStarsByCorpAssets,
                                            'junk',
                                            mls.UI_CORP_IMPOUNDED),
         mapcommon.STARMODE_CORPPROPERTY: (mls.UI_SHARED_MAPSHOWASSETS,
                                           starmap.ColorStarsByCorpAssets,
                                           'property',
                                           mls.UI_CORP_PROPERTY),
         mapcommon.STARMODE_CORPDELIVERIES: (mls.UI_SHARED_MAPSHOWASSETS,
                                             starmap.ColorStarsByCorpAssets,
                                             'deliveries',
                                             mls.UI_CORP_DELIVERIES),
         mapcommon.STARMODE_FRIENDS_FLEET: (mls.UI_SHARED_MAPFINDASSOCIATES, starmap.ColorStarsByFleetMembers),
         mapcommon.STARMODE_FRIENDS_CORP: (mls.UI_SHARED_MAPFINDASSOCIATES, starmap.ColorStarsByCorpMembers),
         mapcommon.STARMODE_FRIENDS_AGENT: (mls.UI_SHARED_MAPFINDASSOCIATES, starmap.ColorStarsByMyAgents),
         mapcommon.STARMODE_AVOIDANCE: (mls.UI_SHARED_MAPOPS73, starmap.ColorStarsByAvoidedSystems),
         mapcommon.STARMODE_REAL: (mls.UI_SHARED_MAPOPS11, starmap.ColorStarsByRealSunColor),
         mapcommon.STARMODE_SERVICE: (mls.UI_SHARED_MAPFINDSTATIONSVC, starmap.ColorStarsByServices),
         mapcommon.STARMODE_PISCANRANGE: (mls.UI_PI_SCAN_RANGE, starmap.ColorStarsByPIScanRange),
         mapcommon.STARMODE_MYCOLONIES: (mls.UI_PI_MY_COLONIES, starmap.ColorStarsByMyColonies),
         mapcommon.STARMODE_PLANETTYPE: (mls.UI_SHARED_MAP_PLANET_TYPES, starmap.ColorStarsByPlanetType),
         mapcommon.STARMODE_INCURSION: (mls.UI_SHARED_MAP_INCURSIONS, starmap.ColorStarsByIncursions)}
        if eve.session.role & ROLE_GML:
            self.starColorHandlers[mapcommon.STARMODE_INCURSIONGM] = (mls.UI_SHARED_MAP_INCURSIONSGM, starmap.ColorStarsByIncursionsGM)



    def SetStarColorMode(self, starColorMode = None):
        if starColorMode is None:
            starColorMode = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        self.LogInfo('SetStarColorMode ', starColorMode)
        self.starData = {}
        solarSystemDict = {}
        self.starLegend = []
        mode = starColorMode[0] if type(starColorMode) == types.TupleType else starColorMode
        definition = self.starColorHandlers.get(mode, (mls.UI_SHARED_MAPOPS11, starmap.ColorStarsByRealSunColor))
        (desc, colorFunc, args,) = (definition[0], definition[1], definition[2:])
        self.StartLoadingBar('set_star_color', mls.UI_SHARED_MAPGETTINGDATA, desc, 2)
        blue.pyos.synchro.Sleep(1)
        colorInfo = util.KeyVal(solarSystemDict={}, colorList=None, overglowFactor=0.0, legend=set())
        colorFunc(colorInfo, starColorMode, *args)
        self.starLegend = list(colorInfo.legend)
        self.UpdateLoadingBar('set_star_color', desc, mls.UI_SHARED_MAPGETTINGDATA, 1, 2)
        blue.pyos.synchro.Sleep(1)
        self.HighlightSolarSystems(colorInfo.solarSystemDict, colorInfo.colorList, colorInfo.overglowFactor)
        self.StopLoadingBar('set_star_color')
        self.DecorateNeocom()



    def GetVictoryPoints(self):
        oldhistory = sm.RemoteSvc('map').GetVictoryPoints()

        def GetSystemState(threshold, current):
            if threshold > current:
                if current == 0:
                    return const.contestionStateNone
                else:
                    return const.contestionStateContested
            if current >= threshold:
                return const.contestionStateVulnerable


        newhistory = {}
        for (factionID, data,) in oldhistory.iteritems():
            if not newhistory.has_key(factionID):
                newhistory[factionID] = {'attacking': {},
                 'defending': {}}
            for (viewmode, soldata,) in data.iteritems():
                tempHistory = newhistory[factionID][viewmode]
                for (solarsystemid, threshold, current,) in soldata:
                    if not tempHistory.has_key(solarsystemid):
                        tempHistory[solarsystemid] = {'threshold': threshold,
                         'current': current,
                         'state': GetSystemState(threshold, current)}



        return newhistory



    def GetRegionColor(self, regionID):
        if not hasattr(self, 'regionColorCache'):
            self.regionColorCache = {}
        if regionID not in self.regionColorCache:
            color = trinity.TriColor()
            color.SetHSV(float(regionID) * 21 % 360.0, 0.5, 0.8)
            color.a = 0.75
            self.regionColorCache[regionID] = color
        return self.regionColorCache[regionID]



    def GetColorCurve(self, colorList):
        colorCurve = trinity.TriColorCurve()
        black = trinity.TriColor()
        for colorID in range(len(colorList)):
            time = float(colorID) / float(len(colorList) - 1)
            colorCurve.AddKey(time, colorList[colorID], black, black, trinity.TRIINT_LINEAR)

        colorCurve.Sort()
        colorCurve.extrapolation = trinity.TRIEXT_CONSTANT
        colorCurve.start = 0L
        return colorCurve



    def GetColorCurveValue(self, colorCurve, time):
        return colorCurve.GetColorAt(long(SEC * time))



    def HighlightSolarSystems(self, solarSystemDict, colorList = None, overglowFactor = 0.0):
        self.starData = {}
        colorCurve = self.GetColorCurve(colorList or self.GetDefaultColorList())
        self.overglowFactor.value = overglowFactor
        for (particleID, solarSystemID,) in self.particleIDToSystemIDMap.iteritems():
            solarsystem = self.map.GetItem(solarSystemID)
            if solarSystemID in solarSystemDict:
                (size, age, comment, uniqueColor,) = solarSystemDict[solarSystemID]
                size *= SUNBASE
                if uniqueColor == None:
                    col = self.GetColorCurveValue(colorCurve, age)
                else:
                    col = uniqueColor
                if comment:
                    self.starData[particleID] = comment
                self.SetStarParticleColor((col.r,
                 col.g,
                 col.b,
                 1.0), (particleID,))
                self.SetStarParticleSize(size, (particleID,))
            else:
                self.SetStarParticleColor(NEUTRAL_COLOR, (particleID,))
                self.SetStarParticleSize(SUNBASE, (particleID,))

        self.mapStars.display = 1



    def GetDefaultColorList(self):
        return [trinity.TriColor(1.0, 0.0, 0.0), trinity.TriColor(1.0, 1.0, 0.0), trinity.TriColor(0.0, 1.0, 0.0)]



    def HighlightSolarSystemsBulk(self, solarSystemList, size, colorList = None):
        self.starData = {}
        if colorList is None:
            colorList = (1.0, 0.0, 0.0)
        else:
            colorList = (colorList[0].r, colorList[0].g, colorList[0].b)
        solarsystems = {}
        particles2highlight = []
        for (solarSystemID, comment,) in solarSystemList:
            particleID = self.GetCloudNumFromItemID(solarSystemID)
            particles2highlight.append(particleID)
            if comment:
                if len(comment):
                    self.starData[particleID] = comment

        self.SetStarParticleColor(NEUTRAL_COLOR[:3])
        self.SetStarParticleColor(colorList, particles2highlight)
        self.mapStars.display = 1



    def GetRegionLabel(self, labelID):
        return self.regionLabels[labelID]



    def GetRouteType(self, label = False):
        pfRouteType = settings.user.ui.Get('pfRouteType', 'safe')
        if label:
            return {'shortest': mls.UI_GENERIC_SHORTEST,
             'safe': mls.UI_GENERIC_SAFEST,
             'unsafe': mls.UI_GENERIC_LESSSECURE}.get(pfRouteType, mls.UI_GENERIC_UNKNOWN).lower()
        return pfRouteType



    def SetWaypoint(self, solarSystemID, clearOtherWaypoints = 0, first = 0):
        waypoints = self.GetWaypoints()
        if solarSystemID in waypoints:
            eve.Message('WaypointAlreadySet')
            return 
        if solarSystemID == eve.session.constellationid:
            eve.Message('WaypointAlreadyInConstellation')
            return 
        if solarSystemID == eve.session.regionid:
            eve.Message('WaypointAlreadyInRegion')
            return 
        if clearOtherWaypoints:
            if len(waypoints):
                pass
            waypoints = []
        if not self.map.GetItem(solarSystemID):
            eve.Message('Command', {'command': mls.UI_SHARED_MAPHINT4})
            return 
        if first:
            waypoints.insert(0, solarSystemID)
        else:
            waypoints.append(solarSystemID)
        settings.char.ui.Set('autopilot_waypoints', waypoints)
        self.UpdateRoute()
        self.ShowWhereIAm()



    def SetWaypoints(self, waypoints):
        self.LogInfo('SetWaypoints')
        settings.char.ui.Set('autopilot_waypoints', waypoints)
        self.UpdateRoute()



    def GetWaypoints(self):
        return settings.char.ui.Get('autopilot_waypoints', [])



    def ClearWaypoints(self, solarSystemID = None):
        self.LogInfo('Map: ClearWaypoints')
        waypoints = self.GetWaypoints()
        if solarSystemID is not None:
            if solarSystemID in waypoints:
                waypoints.remove(solarSystemID)
                settings.char.ui.Set('autopilot_waypoints', waypoints)
                self.UpdateRoute()
                self.ShowWhereIAm()
                return 
            self.LogError('Utried to remove waypoint %s  that was not in waypoint list &s ' % (solarSystemID, waypoints))
        else:
            waypoints = []
            self.destinationPath = [None]
        settings.char.ui.Set('autopilot_waypoints', waypoints)
        sm.ScatterEvent('OnDestinationSet', self.destinationPath[0])
        if self.mapRoot:
            self.ClearRoute('autoPilotRoute')
            self.UpdateLines(hint='ClearWaypoints')
            self.ShowDestination()
            self.CheckAllLabels('ClearWaypoints')
        self.DecorateNeocom()



    def GetRouteFromWaypoints(self, waypoints, startSystem = None):
        if startSystem == None:
            startSystem = eve.session.solarsystemid2
        fullWaypointList = [startSystem] + waypoints
        destinationPath = sm.GetService('pathfinder').GetWaypointPath(fullWaypointList)
        if destinationPath is None:
            destinationPath = []
        return destinationPath



    def UpdateRoute(self, updateLabels = 1, fakeUpdate = 0):
        if not updateLabels:
            if getattr(self, 'doingRouteUpdate', 0) == 1:
                return 
        self.doingRouteUpdate = 1
        waypoints = self.GetWaypoints()
        self.LogInfo('UpdateRoute - waypoints ', waypoints)
        if len(waypoints):
            for each in [eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid]:
                if waypoints[0] == each:
                    waypoints = waypoints[1:]
                    settings.char.ui.Set('autopilot_waypoints', waypoints)
                    if settings.user.ui.Get('autopilot_stop_at_each_waypoint', 0) == 0:
                        if sm.GetService('autoPilot').GetState():
                            sm.GetService('autoPilot').SetOff('  - waypoint reached')
                    break

        self.ClearRoute('autoPilotRoute')
        if not len(waypoints):
            self.destinationPath = [None]
            if self.map.ViewingStarMap():
                self.UpdateLines(hint='UpdateRoute')
            self.DecorateNeocom()
            self.ShowDestination()
            sm.ScatterEvent('OnDestinationSet', None)
            self.LogInfo('UpdateRoute done no wp')
            self.doingRouteUpdate = 0
            return 
        if not fakeUpdate or not hasattr(self, 'destinationPath') or self.destinationPath[0] != session.solarsystemid:
            destinationPath = self.GetRouteFromWaypoints(waypoints)
        else:
            destinationPath = self.destinationPath[1:]
        if not len(destinationPath):
            self.destinationPath = [None]
            if self.map.ViewingStarMap():
                self.UpdateLines(hint='UpdateRoute2')
            self.DecorateNeocom()
            self.ShowDestination()
            sm.ScatterEvent('OnDestinationSet', None)
            self.LogInfo('UpdateRoute done no route to wp')
            self.doingRouteUpdate = 0
            return 
        self.destinationPath = destinationPath
        if self.destinationPath[0] == eve.session.solarsystemid2:
            self.LogWarn('self destination path 0 is own solarsystem, picking next node instead. Path: ', self.destinationPath)
            self.destinationPath = self.destinationPath[1:]
            if not len(self.destinationPath):
                self.destinationPath = [None]
        if self.map.ViewingStarMap():
            if updateLabels:
                route = xtriui.MapRoute()
                route.DrawRoute([eve.session.solarsystemid2] + self.destinationPath, flattened=self.flattened, rotationQuaternion=self.GetCurrentStarmapRotation())
                self.autoPilotRoute = route
                scene2 = sm.GetService('sceneManager').GetRegisteredScene2('starmap')
                scene2.objects.append(route.model)
                self.ShowDestination()
                self.CheckAllLabels('UpdateRoute')
            self.UpdateLines(hint='UpdateRoute3')
        if updateLabels:
            self.DecorateNeocom()
            sm.ScatterEvent('OnDestinationSet', self.destinationPath[0])
        self.LogInfo('UpdateRoute done')
        self.doingRouteUpdate = 0



    def GetCurrentStarmapRotation(self):
        if len(self.mapRoot.rotationCurve.keys) > 0:
            return self.mapRoot.rotationCurve.keys[-1].value
        else:
            return None



    def SetTileMode(self, tileMode):
        settings.user.ui.Set('map_tile_mode', tileMode)
        settings.user.ui.Set('map_tile_no_tiles', 0)
        sm.ScatterEvent('OnLoadWMCPSettings', 'mapsettings_tiles')
        if not self.IsFlat() and settings.user.ui.Get('map_tile_show_unflattened', 0) == 0:
            self.Flatten()
        self.UpdateHexMap()



    def UpdateHexMap(self, isFlat = None):
        showHexMap = settings.user.ui.Get('map_tile_no_tiles', 1) == 0
        showUnflattened = settings.user.ui.Get('map_tile_show_unflattened', 0)
        self.tileLegend = []
        if isFlat is None:
            isFlat = self.IsFlat()
        if showHexMap and (showUnflattened or isFlat):
            systemToAllianceMap = self.GetAllianceSolarSystems()
            changeList = []
            if settings.user.ui.Get('map_tile_activity', 0) == 1:
                changeList = sm.GetService('sov').GetRecentActivity()
            tileMode = settings.user.ui.Get('map_tile_mode', TILE_MODE_SOVEREIGNTY)
            colorByStandings = tileMode == TILE_MODE_STANDIGS
            self.hexMap.LayoutTiles(HEX_TILE_SIZE, systemToAllianceMap, changeList, colorByStandings)
            self.hexMap.Enable()
            showOutlines = settings.user.ui.Get('map_tile_show_outlines', 1) == 1
            self.hexMap.EnableOutlines(showOutlines)
            self.tileLegend = self.hexMap.legend
        else:
            self.hexMap.Enable(False)



    def HighlightTiles(self, dataList, colorList):
        self.hexMap.HighlightTiles(dataList, colorList)



    def GetLegend(self, name):
        return getattr(self, name + 'Legend', [])



    def CreateLabels(self, labelids):
        self.LogInfo('Map Create ', len(labelids), ' labels')
        for labelID in labelids:
            if self.labels.has_key(labelID):
                continue
            if labelID in self.labels:
                label = self.labels[labelID]
                if label is not None and not label.destroyed:
                    continue
                else:
                    del self.labels[labelID]
            self.AddLabel(labelID)




    def ClearLabels(self, labelids = 'all'):
        labels = getattr(self, 'labels', {})
        if labelids == 'all':
            labelids = labels.keys()
        for labelID in labelids:
            if labels.has_key(labelID):
                label = labels[labelID]
                if label is not None and not label.destroyed:
                    label.Close()
                del labels[labelID]
            if self.labeltrackers[labelID] in self.labeltrackersTF.children:
                self.labeltrackersTF.children.remove(self.labeltrackers[labelID])




    def AddLabel(self, itemID):
        if itemID > 0:
            iteminfo = self.map.GetItem(itemID)
            tracker = self.AddTracker(iteminfo.itemName, iteminfo.itemID, iteminfo.x, iteminfo.y, iteminfo.z)
            itemName = iteminfo.itemName
            itemID = iteminfo.itemID
            typeID = iteminfo.typeID
        else:
            lm = self.map.GetMapCache()['landmarks'][(itemID * -1)]
            iteminfo = self.map.GetItem(itemID)
            tracker = self.AddTracker(lm.landmarkName, itemID, lm.x, lm.y, lm.z)
            itemName = lm.landmarkName
            itemID = itemID
            typeID = const.typeMapLandmark
        if not itemName:
            return 
        label = xtriui.MapLabel(parent=uicore.layer.map, name=itemName, align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN, dock=False, width=300, height=32)
        label.Startup(itemName, itemID, typeID, tracker, None)
        self.labels[itemID] = label



    def AddTracker(self, name, itemID, x = 0.0, y = 0.0, z = 0.0, factor = None):
        if itemID in self.labeltrackers and self.labeltrackers[itemID] not in self.labeltrackersTF.children:
            self.labeltrackersTF.children.append(self.labeltrackers[itemID])
            return self.labeltrackers[itemID]
        tracker = trinity.EveTransform()
        trackPos = (x * STARMAP_SCALE, y * STARMAP_SCALE, z * STARMAP_SCALE)
        tracker.translation = trackPos
        self.labeltrackersTF.children.append(tracker)
        self.labeltrackers[itemID] = tracker
        return tracker



    def StartLoadingBar(self, key, tile, action, total):
        if getattr(self, 'loadingBarActive', None) is None:
            sm.GetService('loading').ProgressWnd(tile, action, 0, total)
            self.loadingBarActive = key



    def UpdateLoadingBar(self, key, tile, action, part, total):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').ProgressWnd(tile, action, part, total)



    def StopLoadingBar(self, key):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').StopCycle()
            self.loadingBarActive = None



    def DecorateNeocom(self):
        self.LogInfo('DecorateNeocom ')
        neoComText = ''
        destPathData = None
        destID = self.destinationPath[-1]
        (destSecurityTxt, destColor,) = util.FmtSystemSecStatus(self.map.GetSecurityStatus(destID), True)
        destColorStr = self.GetSystemColorString(destID)
        destItem = self.map.GetItem(destID)
        nextID = self.destinationPath[0]
        (nextSecurityTxt, nextColor,) = util.FmtSystemSecStatus(self.map.GetSecurityStatus(nextID), True)
        nextColorStr = self.GetSystemColorString(nextID)
        nextItem = self.map.GetItem(nextID)
        numJumpsTxt = uix.Plural(len(self.destinationPath), 'UI_SHARED_NUM_JUMP') % {'num': len(self.destinationPath)}
        showRoute = self.map.ViewingStarMap() or settings.user.ui.Get('neocomRouteVisible', 1)
        if self.destinationPath != [None] and showRoute:
            if nextItem is not None:
                neoComText = ''
                if sm.GetService('planetUI').IsOpen():
                    if self.destinationPath[0] is not None:
                        neoComText += '%s:<t>&gt;<t><color=%s>%s</color> %s (%s)<br>' % (mls.UI_SHARED_MAPCURRENTDESTINATION,
                         destColorStr,
                         destSecurityTxt,
                         destItem.itemName,
                         numJumpsTxt)
                        neoComText += '%s:<t>&gt;<t><color=%s>%s</color> %s' % (mls.UI_SHARED_MAP_NEXTSYSINROUTE,
                         nextColorStr,
                         nextSecurityTxt,
                         sm.GetService('map').GetItem(nextID).itemName)
                else:
                    constItem = self.map.GetItem(destItem.locationID)
                    regionItem = self.map.GetItem(constItem.locationID)
                    neoComText += '<b>%s:</b><br>%s<t>&gt;<t>%s' % (mls.UI_SHARED_MAPCURRENTDESTINATION, mls.UI_GENERIC_SOLARSYSTEM, destItem.itemName)
                    if nextItem.locationID != session.constellationid:
                        neoComText += '<br>%s<t>&gt;<t>%s' % (mls.UI_GENERIC_CONSTELLATION, constItem.itemName)
                    if constItem.locationID != session.regionid:
                        neoComText += '<br>%s<t>&gt;<t>%s' % (mls.UI_GENERIC_REGION, regionItem.itemName)
                    neoComText += '<br>%s<t>&gt;<t><color=%s>%s</color>' % (mls.UI_INFOWND_SECURITYLEVEL, destColorStr, destSecurityTxt)
                    if self.map.ViewingStarMap():
                        if self.destinationPath[0] is not None:
                            neoComText = neoComText + '<br><br><b>%s</b>: (%s)' % (mls.UI_GENERIC_ROUTE, numJumpsTxt)
                            waypoints = self.GetWaypoints()
                            if len(waypoints) > 1:
                                neoComText = neoComText + '<br>' + str(len(waypoints)) + ' %s<br>' % mls.UI_SHARED_MAPWAYPOINTS
                            wasRegion = self.map.GetItem(session.regionid)
                            wasConstellation = self.map.GetItem(session.constellationid)
                            for solarSystemID in self.destinationPath[:20]:
                                solarSystemItem = self.map.GetItem(solarSystemID)
                                newConstellation = self.map.GetItem(solarSystemItem.locationID)
                                newRegion = self.map.GetItem(newConstellation.locationID)
                                (sec, col,) = util.FmtSystemSecStatus(self.map.GetSecurityStatus(solarSystemID), True)
                                colStr = self.GetSystemColorString(solarSystemID)
                                if sec >= 0.0:
                                    sec = ' ' + str(sec)
                                neoComText += '<br><color=%s>%s</color> %s' % (colStr, sec, solarSystemItem.itemName)
                                if newRegion.itemID != wasRegion.itemID:
                                    neoComText += '<t>&gt;<t>%s ' % mls.UI_GENERIC_REGION + newRegion.itemName
                                elif newConstellation.itemID != wasConstellation.itemID:
                                    neoComText += '<t>&gt;<t>%s ' % mls.UI_GENERIC_CONSTELLATION + newConstellation.itemName
                                wasRegion = newRegion
                                wasConstellation = newConstellation

                            if len(self.destinationPath) > 20:
                                neoComText += '<br>&gt; ' + str(len(self.destinationPath) - 20) + ' %s...' % mls.UI_GENERIC_MORE
                    else:
                        constItem = self.map.GetItem(nextItem.locationID)
                        regionItem = self.map.GetItem(constItem.locationID)
                        neoComText += '<br><br><b>%s:</b>' % mls.UI_SHARED_MAP_NEXTSYSINROUTE
                        neoComText += '<br>%s<t>&gt;<t>%s' % (mls.UI_GENERIC_SOLARSYSTEMSYSTEM, nextItem.itemName)
                        if nextItem.locationID != session.constellationid:
                            neoComText += '<br>%s<t>&gt;<t>' % mls.UI_GENERIC_CONSTELLATION + constItem.itemName
                        if constItem.locationID != session.regionid:
                            neoComText += '<br>%s<t>&gt;<t>' % mls.UI_GENERIC_REGION + regionItem.itemName
                neoComText += '<br>%s<t>&gt;<t><color=%s>%.1f</color>' % (mls.UI_INFOWND_SECURITYLEVEL, nextColorStr, nextSecurityTxt)
                neoComText += '<br><br><b>%s:</b> (%s)' % (mls.UI_GENERIC_ROUTE, numJumpsTxt)
                destPathData = self.destinationPath[:]
        self.neocom.SetXtraText(neoComText, destPathData)
        self.neocom.UpdateNeocom(0)
        self.LogInfo('DecorateNeocom Done')



    def GetSystemColorString(self, solarSystemID):
        col = self.GetSystemColor(solarSystemID)
        return util.Color.RGBtoHex(col.r, col.g, col.b)



    def GetSystemColor(self, solarSystemID):
        (sec, col,) = util.FmtSystemSecStatus(self.map.GetSecurityStatus(solarSystemID), 1)
        return col



    def LM_InitLandMarks(self):
        self.MOD_landmarks = []
        self.MOD_showLandmarks = 0
        self.MOD_selectedLandmark = None



    def LM_DownloadLandmarks(self, filterNo = None):
        self.LM_ClearLandmarks()
        landmarks = sm.RemoteSvc('config').GetMapLandmarks()
        for landmark in landmarks:
            lmTF = LandMarkIdentifier()
            lmTF.name = str(landmark.landmarkID)
            lmTF.SetWorldCoordinates(landmark.x, landmark.y, landmark.z)
            lmTF.landmarkID = landmark.landmarkID
            lmTF.radius = landmark.radius
            lmTF.description = landmark.description
            lmTF.UpdateRadius()
            if filterNo is not None:
                if landmark.importance != filterNo:
                    continue
            lmTF.importance = landmark.importance
            self.MOD_landmarks.append(lmTF)
            self.landmarkTF.children.append(lmTF)

        return landmarks



    def LM_UploadLandmarks(self):
        landmarkData = []
        for landmark in self.MOD_landmarks:
            (x, y, z,) = landmark.translation
            data = (landmark.landmarkID,
             x / STARMAP_SCALE,
             y / STARMAP_SCALE,
             z / STARMAP_SCALE,
             landmark.GetRadius())
            landmarkData.append(data)

        landmarks = sm.RemoteSvc('config').SetMapLandmarks(landmarkData)



    def LM_ClearLandmarks(self):
        self.MOD_landmarks = []
        self.MOD_selectedLandmark = None
        del self.landmarkTF.children[:]




class LandMarkIdentifier(bluepy.WrapBlueClass('trinity.EveTransform')):
    __persistvars__ = ['radius',
     'importance',
     'landmarkID',
     'description']

    def __init__(self):
        self.radius = 1.0
        self.UpdateRadius()
        self.comment = None
        self.landmarkID = -1
        self.importance = 0
        sphere = trinity.Load('res:/dx9/model/UI/Resultbubble.red')
        sphere.scaling = (STARMAP_SCALE, STARMAP_SCALE, STARMAP_SCALE)
        sphere.children[0].scaling = (2.0, 2.0, 2.0)
        self.children.append(sphere)
        self.frustrumCull = 0



    def UpdateRadius(self):
        rad = max(80.0, self.radius)
        self.scaling = (rad, rad, rad)



    def GetRadius(self):
        return self.scaling[0]



    def SetWorldCoordinates(self, x, y, z):
        self.translation = (x * STARMAP_SCALE, y * STARMAP_SCALE, z * STARMAP_SCALE)



    def SetColor(self, color):
        pass




