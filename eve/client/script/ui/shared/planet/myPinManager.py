import uix
import uiconst
import util
import math
import uicls
import planet
import log
import uthread
import planetCommon
import geo2
import trinity

class MyPinManager:
    __guid__ = 'planet.ui.MyPinManager'
    __notifyevents__ = ['OnPlanetPinsChanged',
     'OnRefreshPins',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetPinPlaced']

    def __init__(self):
        sm.RegisterNotify(self)
        self.planetUISvc = None
        self.linkParentID = None
        self.routeParentID = None
        self.currentExpandedPin = None
        self.currentRoute = []
        self.routeHoverPath = []
        self.oneoffRoute = False
        self.isEdit = False
        self.currRouteVolume = None
        self.newPinType = None
        self.canMoveHeads = None
        self.depletionPoints = []
        self.pinsByID = {}
        self.linksByPinIDs = {}
        self.linksByGraphicID = {}
        self.links = []
        self.buildIndicatorPin = None
        self.currentEcuPinID = None
        self.bracketCurveSet = trinity.TriCurveSet()
        self.bracketCurveSet.name = 'PlanetBrackets'
        uicore.desktop.GetRenderObject().curveSets.append(self.bracketCurveSet)



    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.eventManager = self.planetUISvc.eventManager
        sp = planet.SurfacePoint()
        rubberColor = (1.0, 1.0, 1.0, 1.0)
        self.rubberLink = self.planetUISvc.curveLineDrawer.DrawArc('rubberLink', sp, sp, 2.0, rubberColor, rubberColor)
        self.InitRubberLinkLabels()
        self.ReRender()
        self.depletionPoints = []
        self.bracketCurveSet.Play()



    def OnPlanetViewClosed(self):
        self.ClearPinsFromScene()
        self.bracketCurveSet.Stop()
        self.isEdit = False



    def ReRender(self):
        if not self.planetUISvc.IsOpen():
            return 
        self.RenderPins()
        self.RenderLinks()
        self.ResetPinData()



    def ReRenderPin(self, pin):
        if not self.planetUISvc.IsOpen():
            return 
        uiPin = self.pinsByID.get(pin.id, None)
        if uiPin is None:
            return 
        uiPin.Remove()
        self.RenderPin(pin)



    def InitRubberLinkLabels(self):
        self.rubberLinkLabelContainer = uicls.Container(name='rubberLinkLabels', parent=self.planetUISvc.planetUIContainer, pos=(400, 400, 110, 55), padding=(4, 4, 4, 4), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        self.rubberLinkLabels = util.KeyVal()
        self.rubberLinkLabels.padding = 3
        self.rubberLinkLabels.columnPadding = 9
        white = (1.0, 1.0, 1.0, 1.0)
        gray = (1.0, 1.0, 1.0, 0.6)
        self.rubberLinkLabels.distanceLbl = uicls.Label(text=mls.UI_GENERIC_DISTANCE, parent=self.rubberLinkLabelContainer, left=self.rubberLinkLabels.padding, autowidth=1, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray, autoheight=False)
        maxLabelWidth = uix.GetTextWidth(mls.UI_GENERIC_DISTANCE)
        self.rubberLinkLabels.powerLbl = uicls.Label(text=mls.UI_GENERIC_POWER, parent=self.rubberLinkLabelContainer, top=16, left=self.rubberLinkLabels.padding, autowidth=1, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray, autoheight=False)
        maxLabelWidth = max(maxLabelWidth, uix.GetTextWidth(mls.UI_GENERIC_POWER))
        self.rubberLinkLabels.cpuLbl = uicls.Label(text=mls.UI_GENERIC_CPU, parent=self.rubberLinkLabelContainer, top=32, left=self.rubberLinkLabels.padding, autowidth=1, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray, autoheight=False)
        maxLabelWidth = max(maxLabelWidth, uix.GetTextWidth(mls.UI_GENERIC_CPU))
        maxLabelWidth += self.rubberLinkLabels.columnPadding
        self.rubberLinkLabels.distance = uicls.Label(text='', parent=self.rubberLinkLabelContainer, left=2, autowidth=1, autoheight=1, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        self.rubberLinkLabels.power = uicls.Label(text='', parent=self.rubberLinkLabelContainer, left=2, top=16, autowidth=1, autoheight=1, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        self.rubberLinkLabels.cpu = uicls.Label(text='', parent=self.rubberLinkLabelContainer, left=2, top=32, autowidth=1, autoheight=1, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        uicls.Fill(parent=self.rubberLinkLabelContainer, color=(0.0, 0.0, 0.0, 0.5))



    def OnPlanetPinsChanged(self, planetID):
        if self.planetUISvc and self.planetUISvc.IsOpen() and self.planetUISvc.GetCurrentPlanet().planetID == planetID:
            self.planetUISvc.CloseCurrentlyOpenContainer()
            self.planetUISvc.SetPlanet(planetID)
            self.ReRender()
            self.linkParentID = None
            self.routeParentID = None
        self.currentRoute = []



    def ResetPinData(self):
        if self.planetUISvc.planet.colony is None:
            return 
        pinData = self.planetUISvc.planet.colony.colonyData.pins
        for (pinID, pinUI,) in self.pinsByID.iteritems():
            pinUI.ResetPinData(pinData[pinID])




    def OnRefreshPins(self, pinIDs = None):
        for p in self.pinsByID.values():
            p.OnRefreshPins()

        for l in self.linksByPinIDs.values():
            l.OnRefreshPins()




    def OnEditModeBuiltOrDestroyed(self):
        self.OnRefreshPins()



    def OnPlanetPinPlaced(self, pinID):
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        if planet is None:
            return 
        colony = planet.GetColony(session.charid)
        if colony is None:
            return 
        pin = colony.GetPin(pinID)
        if pin is None:
            return 
        UIpin = self.RenderPin(pin)
        UIpin.PlacementAnimation()



    def OnPlanetEnteredEditMode(self):
        sm.ScatterEvent('OnEditModeChanged', True)



    def OnPlanetExitedEditMode(self):
        self.ReRender()
        sm.ScatterEvent('OnEditModeChanged', False)
        if self.planetUISvc.currentContainer is not None:
            self.planetUISvc.CloseCurrentlyOpenContainer()



    def OnPlanetZoomChanged(self, zoom):
        for pin in self.pinsByID.values():
            pin.OnPlanetZoomChanged(zoom)




    def SetLinkParent(self, parentID):
        self.eventManager.SetStateCreateLinkEnd()
        self.linkParams = planetCommon.GetUsageParametersForLinkType(const.typeTestPlanetaryLink)
        pin = self.pinsByID[parentID]
        self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.rubberLink, pin.surfacePoint, pin.surfacePoint)
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 2.0)
        self.rubberLinkLabelContainer.state = uiconst.UI_DISABLED
        surfacePoint = planetCommon.GetPickIntersectionPoint()
        self.linkParentID = parentID
        self.UpdateRubberLink(surfacePoint)



    def EndLinkCreation(self):
        self.linkParentID = None
        self.eventManager.SetStateNormal()
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 0.0)
        self.rubberLinkLabelContainer.state = uiconst.UI_HIDDEN



    def LaunchCommodities(self, pinID, commoditiesToLaunch):
        self.planetUISvc.planet.LaunchCommodities(pinID, commoditiesToLaunch)



    def EnterRouteMode(self, parentID, typeID, oneoff = False):
        self.eventManager.SetStateCreateRoute()
        self.routeHoverPath = []
        self.currentRoute = [parentID]
        self.typeToRoute = typeID
        self.oneoffRoute = oneoff



    def LeaveRouteMode(self):
        links = self.GetLinksFromPath(self.currentRoute)
        for (l, id,) in links:
            l.RemoveAsRoute(id)

        if len(self.routeHoverPath) > 0:
            links = self.GetLinksFromPath(self.routeHoverPath)
            for (l, id,) in links:
                l.RemoveAsRoute(id)

        self.routeHoverPath = []
        self.currentRoute = []
        self.typeToRoute = None
        self.currRouteVolume = None
        self.eventManager.SetStateNormal()



    def SetRouteWaypoint(self, childID):
        if childID in self.currentRoute:
            i = self.currentRoute.index(childID)
            path = self.currentRoute[i:]
            links = self.GetLinksFromPath(path)
            for (l, id,) in links:
                l.RemoveAsRoute(id)

            self.currentRoute = self.currentRoute[:(i + 1)]
        else:
            lastWaypoint = self.currentRoute[-1]
            colony = self.planetUISvc.planet.GetColonyByPinID(lastWaypoint)
            shortestPath = colony.FindShortestPathIDs(lastWaypoint, childID)
            if not shortestPath:
                raise UserError('CreateRoutePathNotFound')
            self.currentRoute.extend(shortestPath[1:])
        self.routeHoverPath = []
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_routes_waypoint_play')



    def _CleanRoute(self, route):
        pinIDSet = set(route)
        for pinID in pinIDSet:
            if pinID not in route:
                continue
            if route.count(pinID) > 1:
                firstPos = route.index(pinID)
                pos = lastPos = firstPos
                while True:
                    try:
                        pos = route.index(pinID, pos + 1)
                        lastPos = pos
                    except ValueError:
                        break

                deletedPath = route[firstPos:(lastPos + 1)]
                links = self.GetLinksFromPath(deletedPath)
                for (l, id,) in links:
                    l.RemoveAsRoute(id)

                route = route[0:(firstPos + 1)] + route[(lastPos + 1):]




    def GetPinGraphicsClassForType(self, typeID):
        typeObj = cfg.invtypes.Get(typeID)
        if typeObj is None:
            raise RuntimeError('Unable to find inventory type for typeID', typeID)
        if typeObj.groupID == const.groupCommandPins:
            return planet.ui.CommandCenterPin
        if typeObj.groupID == const.groupExtractorPins:
            return planet.ui.ExtractorPin
        if typeObj.groupID == const.groupProcessPins:
            return planet.ui.ProcessorPin
        if typeObj.groupID == const.groupSpaceportPins:
            return planet.ui.Launchpad
        if typeObj.groupID == const.groupStoragePins:
            return planet.ui.StorageFacility
        if typeObj.groupID == const.groupExtractionControlUnitPins:
            return planet.ui.EcuPin
        raise RuntimeError('Unable to resolve UI container class for pin of type', typeID)



    def RenderPins(self):
        if self.planetUISvc.planet.colony is None:
            return 
        newPinData = self.planetUISvc.planet.colony.colonyData.pins
        newPinIDs = newPinData.keys()
        oldPinIDs = self.pinsByID.keys()
        pinsToDelete = [ pinID for pinID in oldPinIDs if pinID not in newPinIDs ]
        for pinID in pinsToDelete:
            pin = self.pinsByID.pop(pinID)
            pin.Remove()

        pinsToAdd = [ pinID for pinID in newPinIDs if pinID not in oldPinIDs ]
        for pinID in pinsToAdd:
            pin = newPinData[pinID]
            self.RenderPin(pin)




    def RenderPin(self, pin):
        if pin.id in self.pinsByID:
            self.pinsByID[pin.id].Remove()
        surfacePoint = planet.SurfacePoint(phi=pin.latitude, theta=pin.longitude)
        pinClass = self.GetPinGraphicsClassForType(pin.typeID)
        UIpin = pinClass(surfacePoint, pin, self.planetUISvc.pinTransform)
        self.pinsByID[pin.id] = UIpin
        return UIpin



    def RenderLinks(self):
        for link in self.links:
            link.Remove()

        self.planetUISvc.curveLineDrawer.ClearLines('links')
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 0.0)
        self.linksByPinIDs = {}
        self.links = []
        self.linksByGraphicID = {}
        if session.charid not in self.planetUISvc.planet.colonies:
            return 
        if self.planetUISvc.planet.colony is not None:
            for (linkID, linkObj,) in self.planetUISvc.planet.colony.colonyData.links.iteritems():
                (ep1ID, ep2ID,) = linkID
                self.AddLink(ep1ID, ep2ID, linkObj.typeID)




    def AddLink(self, parentID, childID, linkTypeID):
        colony = self.planetUISvc.planet.GetColony(session.charid)
        if colony is None:
            log.LogError('Unable to render link for planet without a colony')
            return 
        par = colony.GetPin(parentID)
        child = colony.GetPin(childID)
        if par is None or child is None:
            log.LogWarn('Trying to render link for non-existing pin', parentID, childID)
            return 
        p1 = planet.SurfacePoint(theta=par.longitude, phi=par.latitude)
        p2 = planet.SurfacePoint(theta=child.longitude, phi=child.latitude)
        planetLink = colony.colonyData.GetLink(parentID, childID)
        link = planet.ui.Link(p1, p2, parentID, childID, linkTypeID, planetLink)
        self.linksByPinIDs[(parentID, childID)] = link
        self.linksByPinIDs[(childID, parentID)] = link
        self.links.append(link)
        (linkGraphicID1, linkGraphicID2,) = link.GetGraphicIDs()
        self.linksByGraphicID[linkGraphicID1] = link
        self.linksByGraphicID[linkGraphicID2] = link



    def AddDepletionPoint(self, point):
        index = len(self.depletionPoints)
        self.depletionPoints.append(planet.ui.DepletionPin(point, index, self.planetUISvc.pinOthersTransform))



    def ClearPinsFromScene(self):
        for pin in self.pinsByID.values():
            pin.Remove()

        self.pinsByID = {}



    def GetPinMenu(self, pinID):
        pin = self.pinsByID.get(pinID)
        if pin:
            return pin.GetMenu()



    def GetLinkMenu(self, linkGraphicID):
        if linkGraphicID in self.linksByGraphicID:
            link = self.linksByGraphicID[linkGraphicID]
            return link.GetMenu()



    def EndPlacingPin(self):
        self.eventManager.SetStateNormal()
        self._RemoveBuildIndicatorPin()



    def _RemoveBuildIndicatorPin(self):
        if self.buildIndicatorPin is not None:
            self.buildIndicatorPin.Remove()
            self.buildIndicatorPin = None
        self.DisplayECUExtractionAreas(show=False)



    def DisplayECUExtractionAreas(self, show = True):
        for pin in self.pinsByID.values():
            typeObj = cfg.invtypes.Get(pin.pin.typeID)
            if typeObj.groupID == const.groupExtractionControlUnitPins:
                pin.ShowMaxDistanceCircle(show * 1.0)




    def ShowECUExtractionAreas(self):
        for pin in self.pinsByID.values():
            typeObj = cfg.invtypes.Get(pin.typeID)
            if typeObj.groupID == const.groupExtractionControlUnitPins:
                pin.ShowMaxDistanceCircle(1.0)




    def GetLinksFromPath(self, path):
        links = []
        last = None
        for pinID in path:
            if last is None:
                last = pinID
                continue
            id = (last, pinID)
            if id in self.linksByPinIDs:
                links.append((self.linksByPinIDs[id], id))
            else:
                log.LogWarn('Trying to fetch a non-existing link:', id)
            last = pinID

        return links



    def CreateRoute(self, amount = None):
        if self.oneoffRoute:
            self.planetUISvc.planet.OpenTransferWindow(self.currentRoute)
            self.planetUISvc.CloseCurrentlyOpenContainer()
        else:
            route = self.currentRoute
            links = self.GetLinksFromPath(self.currentRoute)
            typeToRoute = self.typeToRoute
            try:
                try:
                    self.planetUISvc.planet.CreateRoute(self.currentRoute, self.typeToRoute, amount)
                except UserError:
                    if self.currentRoute:
                        self.currentRoute = [self.currentRoute[0]]
                    raise 

            finally:
                for (link, id,) in links:
                    link.RemoveAsRoute(id)


        sm.GetService('audio').SendUIEvent('wise:/msg_pi_routes_destination_play')
        self.currentRoute = []



    def UpdateRubberLink(self, surfacePoint):
        pin = self.pinsByID.get(self.linkParentID)
        if not pin:
            return 
        if not surfacePoint:
            surfacePoint = pin.surfacePoint
        self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.rubberLink, pin.surfacePoint, surfacePoint)
        self.UpdateRubberLinkLabels(pin.surfacePoint, surfacePoint)



    def FocusCameraOnCommandCenter(self, time = 1.0):
        for p in self.pinsByID.values():
            typeObj = cfg.invtypes.Get(p.pin.typeID)
            if typeObj.groupID == const.groupCommandPins:
                try:
                    sm.GetService('planetUI').planetNav.camera.AutoOrbit(p.surfacePoint, newZoom=0.3, time=time)
                except AttributeError:
                    pass
                return 




    def UpdateRubberLinkLabels(self, surfacePointA, surfacePointB):
        self.rubberLinkLabelContainer.left = uicore.uilib.x + 3
        self.rubberLinkLabelContainer.top = uicore.uilib.y + 3
        if surfacePointA == surfacePointB:
            length = 0.0
        else:
            length = surfacePointA.GetDistanceToOther(surfacePointB) * self.planetUISvc.planet.radius
        self.rubberLinkLabels.distance.text = util.FmtDist(length)
        powerUsage = planetCommon.GetPowerUsageForLink(const.typeTestPlanetaryLink, length, 0, self.linkParams)
        cpuUsage = planetCommon.GetCpuUsageForLink(const.typeTestPlanetaryLink, length, 0, self.linkParams)
        self.rubberLinkLabels.power.text = '%d %s' % (powerUsage, mls.UI_GENERIC_MEGAWATTSHORT)
        self.rubberLinkLabels.cpu.text = '%d %s' % (cpuUsage, mls.UI_GENERIC_TERAFLOPSSHORT)



    def OnRouteVolumeChanged(self, volume):
        self.currRouteVolume = volume
        for (link, linkID,) in self.GetLinksFromPath(self.currentRoute):
            link.SetCurrentRouteVolume(volume)




    def DistanceToOtherPinsOK(self, surfacePoint):
        minDistance = 0.012
        for pin in self.pinsByID.values():
            if surfacePoint.GetDistanceToOther(pin.surfacePoint) < minDistance:
                return False

        return True



    def PlacePinOnNextClick(self, pinTypeID):
        self.eventManager.SetStateBuildPin()
        self._RemoveBuildIndicatorPin()
        self.newPinType = pinTypeID
        typeObj = cfg.invtypes.Get(pinTypeID)
        self.buildIndicatorPin = planet.ui.BuildIndicatorPin(planet.SurfacePoint(), pinTypeID, typeObj.groupID, self.planetUISvc.pinOthersTransform)
        if typeObj.groupID == const.groupExtractionControlUnitPins:
            self.DisplayECUExtractionAreas(show=True)



    def CreateLinkOnNextClick(self):
        self.eventManager.SetStateCreateLinkStart()



    def VerifySimulation(self):
        self.planetUISvc.planet.GMVerifySimulation()



    def HighlightLink(self, pinID, linkID, removeOld = True):
        link = self.linksByPinIDs[linkID]
        link.HighlightLink()



    def RemoveHighlightLink(self, linkID):
        self.linksByPinIDs[linkID].RemoveHighlightLink()



    def ShowRoute(self, routeID):
        route = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID)
        path = route.path
        for (link, linkID,) in self.GetLinksFromPath(path):
            link.ShowAsRoute(linkID, 1, 1)




    def StopShowingRoute(self, routeID):
        route = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID)
        path = route.path
        for (link, linkID,) in self.GetLinksFromPath(path):
            link.RemoveAsRoute(linkID)




    def GetCommandCenter(self):
        if not self.planetUISvc.planet:
            return None
        if not self.planetUISvc.planet.colony:
            return None
        if not self.planetUISvc.planet.colony.colonyData:
            return None
        return self.planetUISvc.planet.colony.colonyData.commandPin



    def RemovePin(self, pinID):
        self.planetUISvc.GetCurrentPlanet().RemovePin(pinID)
        pin = self.pinsByID.get(pinID, None)
        if pin:
            if pin.pin.IsCommandCenter():
                for p in self.pinsByID.values():
                    p.Remove()

                self.pinsByID = {}
            else:
                pin.Remove()
                self.pinsByID.pop(pinID)
        self.RenderLinks()
        self.linkParentID = None



    def RemoveLink(self, linkID):
        link = self.linksByPinIDs[linkID]
        link.Remove()
        self.links.remove(link)
        self.planetUISvc.planet.RemoveLink(*linkID)
        self.RenderLinks()



    def UpgradeLink(self, *args):
        self.planetUISvc.planet.SetLinkLevel(*args)



    def InstallSchematic(self, pinID, schematicID):
        self.planetUISvc.planet.InstallSchematic(pinID, schematicID)
        pin = self.pinsByID[pinID]
        pin.OnRefreshPins()



    def RemoveRoute(self, routeID):
        path = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID).path
        self.planetUISvc.planet.RemoveRoute(routeID)
        for (link, pinIDs,) in self.GetLinksFromPath(path):
            link.RenderAccordingToState()




    def PlacePin(self, surfacePoint):
        if not self.DistanceToOtherPinsOK(surfacePoint):
            raise UserError('CannotBuildPinCloseToOthers')
        if not self or self.planetUISvc.planet is None:
            return 
        self.EndPlacingPin()
        pin = self.planetUISvc.planet.CreatePin(self.newPinType, surfacePoint.phi, surfacePoint.theta)
        typeObj = cfg.invtypes.Get(self.newPinType)
        if typeObj.groupID == const.groupCommandPins:
            sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_command_play')
        else:
            sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_pin_play')



    def SetLinkChild(self, parentID, childID):
        try:
            self.planetUISvc.planet.CreateLink(parentID, childID, const.typeTestPlanetaryLink)
            self.AddLink(childID, parentID, const.typeTestPlanetaryLink)
            sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_link_play')

        finally:
            self.EndLinkCreation()




    def EnterSurveyMode(self, ecuPinID):
        self.eventManager.SetStateSurvey()
        self.planetUISvc.GetSurveyWindow(ecuPinID)
        self.currentEcuPinID = ecuPinID
        ecuPin = self.pinsByID[ecuPinID]
        ecuPin.SetExtractionHeadRadius(ecuPin.pin.headRadius)



    def LeaveSurveyMode(self):
        if self.currentEcuPinID is not None:
            ecuPin = self.pinsByID.get(self.currentEcuPinID, None)
            if ecuPin:
                ecuPin.ShowMaxDistanceCircle(0.0)
                ecuPin.ResetOverlapValues()
        self.currentEcuPinID = None
        self.planetUISvc.CloseSurveyWindow()



    def PlaceExtractionHead(self, ecuPinID, headID, surfacePoint, radius):
        self.planetUISvc.planet.AddExtractorHead(ecuPinID, headID, surfacePoint.phi, surfacePoint.theta)
        ecuPin = self.pinsByID[self.currentEcuPinID]
        ecuPin.AddHead(headID, surfacePoint)



    def SetExtractionHeadRadius(self, ecuPinID, radius):
        ecuPin = self.pinsByID[ecuPinID]
        ecuPin.pin.headRadius = radius
        ecuPin.SetExtractionHeadRadius(radius)



    def RemoveExtractionHead(self, ecuPinID, headID):
        self.planetUISvc.planet.RemoveExtractorHead(ecuPinID, headID)
        ecuPin = self.pinsByID[ecuPinID]
        ecuPin.RemoveHead(headID)



    def BeginDragExtractionHead(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return 
        ecuPin = self.pinsByID[ecuPinID]
        if ecuPinID != self.canMoveHeads:
            return 
        self.extractionHeadDragged = (ecuPin, headID)
        self.eventManager.SetSubStateMoveExtractionHead()
        surfacePoint = ecuPin.GetExtractionHead(headID).surfacePoint
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnBeginDragExtractionHead(headID, surfacePoint)



    def DragExtractionHeadTo(self, surfacePoint):
        (ecuPin, headID,) = self.extractionHeadDragged
        distanceFactor = self._EnforceMaximumDinstance(surfacePoint, ecuPin)
        ecuPin.ShowMaxDistanceCircle(distanceFactor)
        ecuPin.MoveExtractionHeadTo(headID, surfacePoint)
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnExtractionHeadMoved(headID, surfacePoint)



    def _EnforceMaximumDinstance(self, headSurfacePoint, uiPin):
        SAFETYFACTOR = 0.99
        ecuSurfacePoint = uiPin.surfacePoint
        distance = headSurfacePoint.GetDistanceToOther(ecuSurfacePoint)
        areaOfInfluence = uiPin.pin.GetAreaOfInfluence()
        if distance < areaOfInfluence:
            return distance / areaOfInfluence
        ecuVector = ecuSurfacePoint.GetAsXYZTuple()
        v = headSurfacePoint.GetAsXYZTuple()
        normal = geo2.Vec3Cross(ecuVector, v)
        rotMat = geo2.MatrixRotationAxis(normal, areaOfInfluence * SAFETYFACTOR)
        newV = geo2.Multiply(rotMat, ecuVector)
        headSurfacePoint.SetXYZ(*newV[:3])
        return 1.0



    def EndDragExtractionHead(self):
        (uiPin, headID,) = self.extractionHeadDragged
        headPin = uiPin.extractionHeadsByNum[headID]
        self._EnforceMaximumDinstance(headPin.surfacePoint, uiPin)
        sm.GetService('planetUI').GetCurrentPlanet().MoveExtractorHead(uiPin.pin.id, headID, headPin.surfacePoint.phi, headPin.surfacePoint.theta)
        self.extractionHeadDragged = None
        self.eventManager.SetSubStateNormal()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnEndDragExtractionHead()



    def OnExtractionHeadMouseEnter(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return 
        ecuPin = self.pinsByID[ecuPinID]
        if ecuPinID != self.canMoveHeads:
            return 
        head = ecuPin.GetExtractionHead(headID)
        if head:
            head.OnMouseEnter()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnHeadEntryMouseEnter(headID)



    def OnExtractionHeadMouseExit(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return 
        ecuPin = self.pinsByID[ecuPinID]
        head = ecuPin.GetExtractionHead(headID)
        if head:
            head.OnMouseExit()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnHeadEntryMouseExit(headID)



    def SetEcuOverlapValues(self, ecuPinID, overlapVals):
        ecuPin = self.pinsByID.get(ecuPinID, None)
        if ecuPin:
            ecuPin.SetOverlapValues(overlapVals)



    def UnlockHeads(self, pinID):
        self.canMoveHeads = pinID



    def LockHeads(self):
        self.canMoveHeads = None



    def GMRunDepletionSim(self, totalDuration):
        points = []
        for point in self.depletionPoints:
            points.append(util.KeyVal(longitude=point.surfacePoint.theta, latitude=point.surfacePoint.phi, amount=point.GetAmount(), duration=point.GetDuration(), headRadius=point.GetHeadRadius()))

        info = util.KeyVal(totalDuration=totalDuration, points=points)
        sm.GetService('planetUI').GetCurrentPlanet().GMRunDepletionSim(self.planetUISvc.selectedResourceTypeID, info)




