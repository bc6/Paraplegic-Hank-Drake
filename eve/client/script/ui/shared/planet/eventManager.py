import uiconst
STATE_NORMAL = 0
STATE_BUILDPIN = 1
STATE_CREATELINKSTART = 2
STATE_CREATELINKEND = 3
STATE_CREATEROUTE = 4
STATE_SURVEY = 5
SUBSTATE_NORMAL = 0
SUBSTATE_MOVEEXTRACTIONHEAD = 1

class EventManager:
    __guid__ = 'planet.ui.EventManager'
    __notifyevents__ = []

    def __init__(self):
        sm.RegisterNotify(self)
        self.state = STATE_NORMAL
        self.subState = SUBSTATE_NORMAL



    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.myPinManager = self.planetUISvc.myPinManager
        self.myPinManager = self.planetUISvc.myPinManager
        self.otherPinManager = self.planetUISvc.otherPinManager



    def OnPlanetViewClosed(self):
        self.SetStateNormal()



    def SetStateNormal(self):
        self._SetState(STATE_NORMAL)
        self._SetSubState(SUBSTATE_NORMAL)



    def SetStateBuildPin(self):
        self._SetState(STATE_BUILDPIN)



    def SetStateCreateLinkStart(self):
        self._SetState(STATE_CREATELINKSTART)



    def SetStateCreateLinkEnd(self):
        self._SetState(STATE_CREATELINKEND)



    def SetStateCreateRoute(self):
        self._SetState(STATE_CREATEROUTE)



    def SetStateSurvey(self):
        self._SetState(STATE_SURVEY)



    def _SetState(self, state):
        if state == self.state:
            return 
        oldState = self.state
        self.state = state
        if oldState == STATE_BUILDPIN:
            self.myPinManager.EndPlacingPin()
        elif oldState == STATE_CREATELINKSTART and state != STATE_CREATELINKEND:
            self.myPinManager.EndLinkCreation()
        elif oldState == STATE_CREATELINKEND:
            self.myPinManager.EndLinkCreation()
        elif oldState == STATE_CREATEROUTE:
            self.myPinManager.LeaveRouteMode()
        elif oldState == STATE_SURVEY:
            self.myPinManager.LeaveSurveyMode()



    def SetSubStateNormal(self):
        self._SetSubState(SUBSTATE_NORMAL)



    def SetSubStateMoveExtractionHead(self):
        self._SetSubState(SUBSTATE_MOVEEXTRACTIONHEAD)



    def _SetSubState(self, subState):
        if subState == self.subState:
            return 
        oldSubState = self.subState
        self.subState = subState



    def OnPlanetPinClicked(self, pinID):
        if pinID not in self.myPinManager.pinsByID:
            return 
        if uicore.uilib.rightbtn:
            return 
        if self.state == STATE_CREATEROUTE:
            self.myPinManager.SetRouteWaypoint(pinID)
            if self.myPinManager.oneoffRoute:
                self.myPinManager.CreateRoute()
            elif self.planetUISvc.currentContainer:
                self.planetUISvc.currentContainer.OnPlanetRouteWaypointAdded(self.myPinManager.currentRoute)
        elif uicore.uilib.Key(uiconst.VK_CONTROL) or self.state == STATE_CREATELINKSTART:
            self.planetUISvc.CloseCurrentlyOpenContainer()
            self.myPinManager.SetLinkParent(pinID)
        elif self.state == STATE_CREATELINKEND:
            self.planetUISvc.CloseCurrentlyOpenContainer()
            self.myPinManager.SetLinkChild(self.myPinManager.linkParentID, pinID)
        else:
            pin = self.myPinManager.pinsByID[pinID]
            if self.planetUISvc.currentContainer and self.planetUISvc.currentContainer.pin == pin.pin:
                return 
            self.planetUISvc.OpenContainer(pin)
            pin.OnClicked()



    def OnPlanetPinDblClicked(self, pinID):
        if self.state == STATE_CREATEROUTE:
            if self.myPinManager.oneoffRoute:
                return 
            self.myPinManager.SetRouteWaypoint(pinID)
            self.planetUISvc.currentContainer.SubmitRoute()
        elif self.planetUISvc.currentContainer:
            self.planetUISvc.currentContainer.ShowDefaultPanel()



    def OnDepletionPinClicked(self, index):
        self.planetUISvc.CloseCurrentlyOpenContainer()
        import form
        sm.GetService('window').GetWindow('depletionManager', create=1, decoClass=form.DepletionManager, pinManager=self.myPinManager)



    def OnPlanetPinMouseEnter(self, pinID):
        if not self:
            return 
        pin = self.myPinManager.pinsByID.get(pinID, None)
        if not pin:
            return 
        pin.OnMouseEnter()
        planet = sm.GetService('planetUI').planet
        if planet is None:
            return 
        colony = planet.GetColony(pin.pin.ownerID)
        if self.state == STATE_CREATEROUTE:
            if pinID not in self.myPinManager.currentRoute:
                path = colony.FindShortestPathIDs(self.myPinManager.currentRoute[-1], pinID)
                self.myPinManager.routeHoverPath = path
                links = self.myPinManager.GetLinksFromPath(path)
                for (l, id,) in links:
                    l.ShowAsRoute(id, 1, 1, self.myPinManager.currRouteVolume)

        elif self.state == STATE_CREATELINKEND:
            parentPin = self.myPinManager.pinsByID.get(self.myPinManager.linkParentID)
            if not parentPin:
                return 
            self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.myPinManager.rubberLink, pin.surfacePoint, parentPin.surfacePoint)
            self.myPinManager.UpdateRubberLinkLabels(pin.surfacePoint, parentPin.surfacePoint)
        elif colony and colony.colonyData is not None:
            routesFrom = colony.colonyData.GetSourceRoutesForPin(pin.pin.id)
            routesTo = colony.colonyData.GetDestinationRoutesForPin(pin.pin.id)
            numRoutes = len(routesFrom)
            for (i, route,) in enumerate(routesFrom):
                path = route.path
                links = self.myPinManager.GetLinksFromPath(path)
                for (l, id,) in links:
                    l.ShowAsRoute(id, i, numRoutes)

                pin = self.myPinManager.pinsByID[path[-1]]
                pin.SetAsRoute()

            numRoutes = len(routesTo)
            for (i, routeID,) in enumerate(routesTo):
                r = colony.GetRoute(routeID)
                path = r.path
                links = self.myPinManager.GetLinksFromPath(path)
                for (l, id,) in links:
                    l.ShowAsRoute(id, i, numRoutes)

                pin = self.myPinManager.pinsByID[path[0]]
                pin.SetAsRoute()




    def OnPlanetPinMouseExit(self, pinID):
        if not self:
            return 
        pin = self.myPinManager.pinsByID.get(pinID, None)
        if not pin:
            return 
        pin.OnMouseExit()
        planet = self.planetUISvc.GetCurrentPlanet()
        if planet is None:
            return 
        if self.state == STATE_CREATEROUTE:
            path = getattr(self.myPinManager, 'routeHoverPath', [])
            links = self.myPinManager.GetLinksFromPath(path)
            for (l, id,) in links:
                l.RemoveAsRoute(id)

        else:
            colony = planet.GetColonyByPinID(pin.pin.id)
            if colony is None or colony.colonyData is None:
                return 
            routesFrom = colony.colonyData.GetSourceRoutesForPin(pin.pin.id)
            routesTo = colony.colonyData.GetDestinationRoutesForPin(pin.pin.id)
            for route in routesFrom:
                path = route.path
                links = self.myPinManager.GetLinksFromPath(path)
                for (l, id,) in links:
                    l.RemoveAsRoute(id)

                pin = self.myPinManager.pinsByID[path[-1]]
                pin.ResetAsRoute()

            for routeID in routesTo:
                r = colony.GetRoute(routeID)
                path = r.path
                links = self.myPinManager.GetLinksFromPath(path)
                for (l, id,) in links:
                    l.RemoveAsRoute(id)

                pin = self.myPinManager.pinsByID[path[0]]
                pin.ResetAsRoute()




    def OnExtractionHeadMouseEnter(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            self.myPinManager.OnExtractionHeadMouseEnter(ecuID, headNum)



    def OnExtractionHeadMouseExit(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            self.myPinManager.OnExtractionHeadMouseExit(ecuID, headNum)



    def OnExtractionHeadMouseDown(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            self.myPinManager.BeginDragExtractionHead(ecuID, headNum)



    def OnOtherCharactersCommandPinClicked(self, pinID):
        pin = self.otherPinManager.otherPlayerPinsByPinID.get(pinID)
        if not pin:
            return 
        if cfg.invtypes.Get(pin.typeID).groupID != const.groupCommandPins:
            return 
        self.otherPinManager.RenderOtherCharactersNetwork(pin.ownerID)



    def OnPlanetOtherPinMouseEnter(self, pinID):
        if pinID not in self.otherPinManager.otherPlayerPinsByPinID:
            return 
        pin = self.otherPinManager.otherPlayerPinsByPinID[pinID]
        pin.OnMouseEnter()



    def OnPlanetOtherPinMouseExit(self, pinID):
        if pinID not in self.otherPinManager.otherPlayerPinsByPinID:
            return 
        pin = self.otherPinManager.otherPlayerPinsByPinID[pinID]
        pin.OnMouseExit()



    def OnPlanetNavClicked(self, surfacePoint, wasDragged):
        if not wasDragged:
            self.planetUISvc.CloseCurrentlyOpenContainer()
            self.otherPinManager.HideOtherCharactersNetwork()
        if surfacePoint and not wasDragged:
            if self.state == STATE_BUILDPIN:
                self.myPinManager.PlacePin(surfacePoint)
                self.state = STATE_NORMAL



    def OnPlanetNavMouseUp(self):
        if self.state == STATE_SURVEY:
            if self.subState == SUBSTATE_MOVEEXTRACTIONHEAD:
                self.myPinManager.EndDragExtractionHead()



    def OnPlanetNavRightClicked(self):
        if self.state != STATE_NORMAL:
            self.SetStateNormal()
            return True
        else:
            return False



    def OnPlanetSurfaceDblClicked(self, surfacePoint):
        sm.GetService('planetUI').FocusCameraOnCommandCenter()



    def OnPlanetSurfaceMouseMoved(self, surfacePoint):
        if self.state == STATE_CREATELINKEND:
            self.myPinManager.UpdateRubberLink(surfacePoint)
        elif self.state == STATE_BUILDPIN:
            if self.myPinManager.buildIndicatorPin:
                self.myPinManager.buildIndicatorPin.SetLocation(surfacePoint)
                canBuild = self.myPinManager.DistanceToOtherPinsOK(surfacePoint)
                self.myPinManager.buildIndicatorPin.SetCanBuildIndication(canBuild)
        elif self.state == STATE_SURVEY:
            if self.subState == SUBSTATE_MOVEEXTRACTIONHEAD:
                self.myPinManager.DragExtractionHeadTo(surfacePoint)



    def OnPlanetNavFocusLost(self):
        if self.state in (STATE_CREATELINKEND, STATE_BUILDPIN):
            self.SetStateNormal()



    def OnPlanetLinkClicked(self, linkID):
        if self.state == STATE_CREATEROUTE:
            return 
        if linkID not in self.myPinManager.linksByGraphicID:
            return 
        link = self.myPinManager.linksByGraphicID[linkID]
        if self.planetUISvc.currentContainer and self.planetUISvc.currentContainer.pin == link:
            return 
        link.OnClick()
        self.planetUISvc.OpenContainer(link)



    def OnPlanetLinkDblClicked(self, linkID):
        if self.planetUISvc.currentContainer:
            self.planetUISvc.currentContainer.ShowDefaultPanel()



    def OnPlanetLinkMouseEnter(self, lineID):
        if self.state == STATE_CREATEROUTE:
            return 
        if lineID in self.myPinManager.linksByGraphicID:
            link = self.myPinManager.linksByGraphicID[lineID]
            link.OnMouseEnter()



    def OnPlanetLinkMouseExit(self, areaID):
        if self.state == STATE_CREATEROUTE:
            return 
        if areaID in self.myPinManager.linksByGraphicID:
            link = self.myPinManager.linksByGraphicID[areaID]
            link.OnMouseExit()



    def BeginCreateLink(self, sourcePinID):
        self._SetState(STATE_CREATELINKSTART)
        self.planetUISvc.CloseCurrentlyOpenContainer()
        self.myPinManager.SetLinkParent(sourcePinID)




