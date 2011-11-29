import blue
import uthread
import uiutil
import trinity
import util
import listentry
import types
import uiconst
import uicls
import maputils
import log
import form
import mapcommon
from service import ROLE_GML
import localization
ROUTECOL = {'White': trinity.TriColor(1.0, 1.0, 1.0, 0.5),
 'Red': trinity.TriColor(1.0, 0.0, 0.0, 0.5),
 'Green': trinity.TriColor(0.0, 1.0, 0.0, 0.5),
 'Blue': trinity.TriColor(0.0, 0.0, 1.0, 0.5),
 'Yellow': trinity.TriColor(1.0, 1.0, 0.0, 0.5)}
ILLEGALITY_AVOID_NONE = 0
ILLEGALITY_AVOID_STANDING_LOSS = 1
ILLEGALITY_AVOID_CONFISCATE = 2
ILLEGALITY_AVOID_ATTACK = 3
PLANET_TYPES = (const.typePlanetEarthlike,
 const.typePlanetPlasma,
 const.typePlanetGas,
 const.typePlanetIce,
 const.typePlanetOcean,
 const.typePlanetLava,
 const.typePlanetSandstorm,
 const.typePlanetThunderstorm,
 const.typePlanetShattered)

class MapPalette(uicls.Window):
    __guid__ = 'form.MapsPalette'
    __notifyevents__ = ['OnDestinationSet',
     'OnAvoidanceItemsChanged',
     'OnMapModeChangeDone',
     'OnLoadWMCPSettings',
     'OnFlattenModeChanged']
    default_top = '__center__'
    default_width = 400
    default_height = 320
    default_windowID = 'mapspalette'

    @staticmethod
    def default_left(*args):
        (leftpush, rightpush,) = uicls.Window.GetSideOffset(uicls.Window)
        return uicore.desktop.width - rightpush - form.MapsPalette.default_width - 80



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self._cfgTopHeaderTmpl = None
        self._cfgTopDivTmpl = None
        self._cfgTopPushTmpl = None
        self._cfgCheckBoxTmpl = None
        self._cfgBottomHeaderTmpl = None
        self._cfgButtonTmpl = None
        self.starColorGroups = []
        self.starColorByID = None
        self.scope = 'station_inflight'
        self.SetWndIcon('ui_7_64_4', mainTop=-14)
        self.SetMinSize([400, 200])
        self.SetTopparentHeight(36)
        self.SetCaption(localization.GetByLabel('UI/Map/MapPallet/CaptionMapPallet'))
        self.MakeUnKillable()
        self.loadedTab = None
        if self.destroyed:
            return 
        waypointbtns2 = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Map/MapPallet/btnOptimizeRoute'),
          self.TravellingSalesman,
          (),
          66]], parent=self.sr.main, idx=0)
        self.waypointBtns = waypointbtns2
        waypointopt = uicls.Container(name='waypointopt', parent=self.sr.main, align=uiconst.TOBOTTOM, height=0, clipChildren=1, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'mapspalletescroll_withsort'
        self.sr.scroll2 = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll2.sr.id = 'mapspalletescroll_withhoutsort'
        self.sr.scroll2.OnSelectionChange = self.OnSelectionChange
        self.sr.scroll2.sr.content.OnDropData = self.MoveWaypoints
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Map/MapPallet/lblChangeWaypointPriority'), parent=waypointopt, pos=(3, 2, 0, 0), padding=(0, 0, 0, 0))
        cbox = uicls.Checkbox(text=localization.GetByLabel('UI/Map/MapPallet/cbExpandWaypoints'), parent=waypointopt, configName='expandwaypoints', retval=None, checked=settings.user.ui.Get('expandwaypoints', 1), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(1, 18, 140, 0))
        cbox.data = {'key': 'expandwaypoints',
         'retval': None}
        waypointopt.height = cbox.height + const.defaultPadding + 18
        self.sr.waypointopt = waypointopt
        flattened = settings.user.ui.Get('mapFlattened', 1)
        toggleFlatLabel = localization.GetByLabel('UI/Map/MapPallet/btnFlattenMap')
        if flattened:
            toggleFlatLabel = localization.GetByLabel('UI/Map/MapPallet/btnUnflattenMap')
        if sm.GetService('viewState').IsViewActive('starmap'):
            toggleMapLabel = localization.GetByLabel('UI/Map/MapPallet/btnSolarsystemMap')
        else:
            toggleMapLabel = localization.GetByLabel('UI/Map/MapPallet/btnStarMap')
        btns = uicls.ButtonGroup(btns=[['mapCloseBtn',
          localization.GetByLabel('UI/Map/MapPallet/btnCloseMap'),
          sm.GetService('viewState').CloseSecondaryView,
          (),
          80], ['mapToggleMapBtn',
          toggleMapLabel,
          self.ToggleMapMode,
          (),
          130], ['mapUnflattenFlattenBtn',
          toggleFlatLabel,
          self.ClickToggleFlatten,
          'self',
          80]], parent=self.sr.topParent, align=uiconst.CENTER, left=15, line=0, idx=0, forcedButtonNames=True, fixedWidth=True, unisize=False)
        self.sr.flattenBtns = btns
        searchpar = uicls.Container(name='searchpar', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 40), idx=0)
        searchpar.OnTabSelect = self.GiveInputFocus
        inpt = uicls.SinglelineEdit(name='', parent=searchpar, pos=(5, 22, 98, 0), maxLength=64)
        inpt.OnReturn = self.OnReturnSearch
        self.sr.searchinput = inpt
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Map/MapPallet/lblSearchForLocation'), parent=inpt, left=0, top=-14, state=uiconst.UI_DISABLED)
        uicls.Button(parent=inpt.parent, label=localization.GetByLabel('UI/Map/MapPallet/btnSearchForLocation'), func=self.Search, args=1, pos=(inpt.left + inpt.width + 4,
         inpt.top,
         0,
         0), btn_default=1)
        starviewstabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        starviewstabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabStars'),
          self.sr.scroll2,
          self,
          'starview_color'],
         [localization.GetByLabel('UI/Map/MapPallet/tabLabels'),
          self.sr.scroll2,
          self,
          'mapsettings_labels'],
         [localization.GetByLabel('UI/Map/MapPallet/tabMapLines'),
          self.sr.scroll2,
          self,
          'mapsettings_lines'],
         [localization.GetByLabel('UI/Map/MapPallet/tabTiles'),
          self.sr.scroll2,
          self,
          'mapsettings_tiles'],
         [localization.GetByLabel('UI/Map/MapPallet/tabLegend'),
          self.sr.scroll2,
          self,
          'mapsettings_legend'],
         [localization.GetByLabel('UI/Map/MapPallet/tabMapAnimation'),
          self.sr.scroll2,
          self,
          'mapsettings_other']], 'starviewssub', autoselecttab=0)
        autopilottabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        autopilottabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabWaypoints'),
          self.sr.scroll2,
          self,
          'waypointconf',
          waypointopt], [localization.GetByLabel('UI/Map/MapPallet/tabSettings'),
          self.sr.scroll2,
          self,
          'autopilotconf',
          None], [localization.GetByLabel('UI/Map/MapPallet/tabMapAdvoidance'),
          self.sr.scroll2,
          self,
          'avoidconf',
          None]], 'autopilottabs', autoselecttab=0)
        self.sr.autopilottabs = autopilottabs
        self.sr.starviewstabs = starviewstabs
        self.sr.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        self.sr.maintabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabSearch'),
          self.sr.scroll,
          self,
          'mapsearchpanel',
          searchpar],
         [localization.GetByLabel('UI/Map/MapPallet/tabStarMap'),
          self.sr.scroll2,
          self,
          'mapsettings',
          starviewstabs],
         [localization.GetByLabel('UI/Map/MapPallet/tabSolarSystemMap'),
          self.sr.scroll2,
          self,
          'mapsettings_solarsystem',
          None],
         [localization.GetByLabel('UI/Map/MapPallet/tabAutoPilot'),
          self.sr.scroll2,
          self,
          'autopilot',
          autopilottabs]], 'mapspalette', autoselecttab=1)



    def MoveWaypoints(self, dragObj, entries, orderID = -1, *args):
        self.ChangeWaypointSorting(orderID=orderID)



    def GiveInputFocus(self, *args):
        uicore.registry.SetFocus(self.sr.searchinput)



    def ToggleMapMode(self, *args):
        sm.GetService('map').ToggleMode()



    def ClickToggleFlatten(self, btn, *args):
        sm.GetService('starmap').ToggleFlattenMode()



    def OnFlattenModeChanged(self, isFlat, *args):
        btn = self.sr.flattenBtns.children[0].children[2]
        if isFlat:
            btn.SetLabel(localization.GetByLabel('UI/Map/MapPallet/btnUnflattenMap'))
        else:
            btn.SetLabel(localization.GetByLabel('UI/Map/MapPallet/btnFlattenMap'))



    def ShowPanel(self, panelname):
        if panelname == localization.GetByLabel('UI/Map/MapPallet/tabWaypoints'):
            self.sr.autopilottabs.ShowPanelByName(localization.GetByLabel('UI/Map/MapPallet/tabWaypoints'))
            self.sr.maintabs.ShowPanelByName(localization.GetByLabel('UI/Map/MapPallet/tabAutoPilot'))
        else:
            uthread.pool('MapPalette::ShowPanel', self.sr.maintabs.ShowPanelByName, panelname)



    def Load(self, key):
        self.SetHint()
        self.waypointBtns.display = False
        if key == 'mapsettings_solarsystem':
            self.sr.waypointopt.display = False
        if key == 'mapsearchpanel':
            self.Search(0)
            self.sr.waypointopt.display = False
        elif key == 'mapsettings':
            self.sr.starviewstabs.AutoSelect()
            self.sr.waypointopt.display = False
        elif key == 'options':
            self.sr.optionstabs.AutoSelect()
            self.sr.waypointopt.display = False
        elif key == 'autopilot':
            self.sr.autopilottabs.AutoSelect()
        elif key[:11] == 'mapsettings' or key == 'autopilotconf' or key[:8] == 'starview':
            if key == self.loadedTab:
                return 
            self.LoadSettings(key)
        elif key == 'waypointconf':
            self.waypointBtns.display = True
            self.LoadWaypoints()
        elif key == 'avoidconf':
            self.LoadAvoidance()
        if self.destroyed:
            return 
        self.loadedTab = key



    def CloseByUser(self, *args):
        if not eve.rookieState:
            uicls.Window.CloseByUser(self, *args)



    def OnMapModeChangeDone(self, mode):
        if self.destroyed or not hasattr(self, 'sr'):
            return 
        btnFlat = self.sr.flattenBtns.children[0].children[2]
        btnMode = self.sr.flattenBtns.children[0].children[1]
        if mode == 'starmap':
            btnFlat.Enable()
            btnMode.SetLabel(localization.GetByLabel('UI/Map/MapPallet/tabSolarSystemMap'))
        elif mode == 'systemmap':
            btnFlat.Disable()
            btnMode.SetLabel(localization.GetByLabel('UI/Map/MapPallet/tabStarMap'))



    def OnReturnSearch(self, *args):
        self.Search(1)



    def Search(self, errorifnothing, *args):
        t = uthread.new(self.Search_thread, errorifnothing)
        t.context = 'mappalette::Search'



    def Search_thread(self, errorifnothing):
        if not self or self.destroyed:
            return 
        self.searchresult = None
        search = self.sr.searchinput.GetValue().strip()
        if len(search) < 1:
            if errorifnothing:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Map/MapPallet/msgPleaseTypeSomething')})
                return 
        else:
            self.SetHint()
            if self is not None and not self.destroyed:
                self.ShowLoad()
            else:
                return 
            self.searchresult = sm.GetService('map').FindByName(search)
        if self is None or self.destroyed:
            return 
        self.ShowSearchResult()
        if self == None:
            return 
        self.HideLoad()



    def ShowSearchResult(self, *args):
        self.listtype = 'location'
        mapSvc = sm.GetService('map')
        tmplst = []
        scrolllist = []
        if self.searchresult and len(self.searchresult):
            for each in self.searchresult:
                wasID = each.itemID
                found = [each.itemName]
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            found.append(item.itemName)

                if len(found) == 3:
                    trace = localization.GetByLabel('UI/Map/MapPallet/Trace3Locations', location1=found[0], location2=found[1], location3=found[2])
                elif len(found) == 2:
                    trace = localization.GetByLabel('UI/Map/MapPallet/Trace2Locations', location1=found[0], location2=found[1])
                else:
                    trace = '/'.join(found)
                scrolllist.append(listentry.Get('Item', {'itemID': each.itemID,
                 'typeID': each.typeID,
                 'label': '%s<t>%s' % (trace, cfg.invtypes.Get(each.typeID).name)}))

        if self is None or self.destroyed:
            return 
        headers = [localization.GetByLabel('UI/Map/MapPallet/hdrSearchName'), localization.GetByLabel('UI/Map/MapPallet/hdrSearchType')]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/lblSearchNothingFound'))



    def OnDestinationSet(self, *args):
        if self.destroyed:
            return 
        if self.sr.maintabs.GetSelectedArgs() == 'autopilot':
            if self.sr.autopilottabs.GetSelectedArgs() == 'waypointconf':
                self.LoadWaypoints()



    def OnAvoidanceItemsChanged(self):
        if self.destroyed:
            return 
        if self.sr.maintabs.GetSelectedArgs() == 'autopilot' and self.sr.autopilottabs.GetSelectedArgs() == 'avoidconf':
            self.LoadAvoidance()



    def LoadWaypoints(self, *args):
        mapSvc = sm.GetService('map')
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        tmplst = []
        fromID = eve.session.solarsystemid2
        scrolllist = []
        actualID = 0
        selectedItem = None
        if waypoints and len(waypoints):
            self.SetHint()
            counter = 0
            currentPlace = mapSvc.GetItem(eve.session.solarsystemid2)
            opts = {'itemID': currentPlace.itemID,
             'typeID': currentPlace.typeID,
             'label': localization.GetByLabel('UI/Map/MapPallet/lblCurrentLocation', locationName=currentPlace.itemName),
             'orderID': -1,
             'actualID': 0}
            scrolllist.append(listentry.Get('Item', opts))
            for waypointID in waypoints:
                blue.pyos.BeNice()
                actualID = actualID + 1
                each = mapSvc.GetItem(waypointID)
                description = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=cfg.invtypes.Get(each.typeID).name)
                wasID = each.itemID
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            description = description + ' / ' + item.itemName

                if settings.user.ui.Get('expandwaypoints', 1) == 1:
                    solarsystems = starmapSvc.GetRouteFromWaypoints([waypointID], fromID)
                    if len(solarsystems):
                        for solarsystemID in solarsystems[1:-1]:
                            actualID = actualID + 1
                            sunItem = mapSvc.GetItem(solarsystemID)
                            scrolllist.append(listentry.Get('AutoPilotItem', {'itemID': solarsystemID,
                             'typeID': sunItem.typeID,
                             'label': localization.GetByLabel('UI/Map/MapPallet/lblWaypointListEntryNoCount', itemName=sunItem.itemName),
                             'orderID': -1,
                             'actualID': actualID}))

                lblTxt = localization.GetByLabel('UI/Map/MapPallet/lblWaypointListEntry', counter=counter + 1, itemName=each.itemName, description=description)
                scrolllist.append(listentry.Get('AutoPilotItem', {'itemID': waypointID,
                 'typeID': each.typeID,
                 'label': lblTxt,
                 'orderID': counter,
                 'actualID': actualID,
                 'canDrag': 1}))
                if self.sr.Get('selectedWaypoint', None) is not None and self.sr.selectedWaypoint < len(waypoints) and waypointID == waypoints[self.sr.selectedWaypoint]:
                    selectedItem = actualID
                counter = counter + 1
                fromID = waypointID

        if self == None:
            return 
        destinationPath = starmapSvc.GetDestinationPath()
        self.sr.scroll2.Load(contentList=scrolllist)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/hintNoWaypoints'))
        if selectedItem is not None:
            self.sr.scroll2.SetSelected(selectedItem)



    def LoadAvoidance(self, *args):
        mapSvc = sm.StartService('map')
        items = sm.StartService('pathfinder').GetAvoidanceItems()
        scrolllist = []
        if items and len(items):
            self.SetHint()
            counter = 0
            for itemsID in items:
                blue.pyos.BeNice()
                each = mapSvc.GetItem(itemsID)
                description = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=cfg.invgroups.Get(each.typeID).name)
                wasID = each.itemID
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            description = description + ' / ' + item.itemName

                scrolllist.append(listentry.Get('Item', {'itemID': itemsID,
                 'typeID': each.typeID,
                 'label': localization.GetByLabel('UI/Map/MapPallet/lblAdvoidanceListEntry', itemName=each.itemName, description=description)}))

        if self == None:
            return 
        self.sr.scroll2.Load(contentList=scrolllist)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/hintNoAdvoidanceItems'))



    def TravellingSalesman(self, *args):
        if getattr(self, 'isOptimizing', False):
            return 
        try:
            setattr(self, 'isOptimizing', True)
            starmapSvc = sm.GetService('starmap')
            waypoints = starmapSvc.GetWaypoints()
            isReturnTrip = False
            for idx in reversed(xrange(len(waypoints))):
                if waypoints[idx] == eve.session.solarsystemid2:
                    del waypoints[idx]
                    isReturnTrip = True
                    break

            numWaypoints = len(waypoints)
            if numWaypoints == 0:
                return 
            msg = None
            if numWaypoints > 12:
                msg = 'UI/Map/MapPallet/msgOptimizeQuestion1'
            elif numWaypoints > 10:
                msg = 'UI/Map/MapPallet/msgOptimizeQuestion2'
            if msg:
                yesNo = eve.Message('AskAreYouSure', {'cons': localization.GetByLabel(msg, numWaypoints=len(waypoints))}, uiconst.YESNO)
                if yesNo != uiconst.ID_YES:
                    return 
            distance = {}
            waypoints.append(eve.session.solarsystemid2)
            for fromID in waypoints:
                distance[fromID] = {}
                for toID in waypoints:
                    if fromID == toID:
                        continue
                    distance[fromID][toID] = sm.GetService('pathfinder').GetJumpCountFromCurrent(toID, fromID)


            waypoints.pop()
            startTime = blue.os.GetWallclockTimeNow()
            prefix = [None]
            _push = prefix.append
            _pop = prefix.pop

            def FindShortestRoute(prefix, distanceSoFar, toID):
                distanceTo = distance[toID]
                prefix[-1] = toID
                shortestDist = shortestRouteSoFar[0]
                if len(prefix) < numWaypoints:
                    _push(None)
                    for i in indexes:
                        toID = waypoints[i]
                        if not toID:
                            continue
                        candidateDist = distanceSoFar + distanceTo[toID]
                        if candidateDist >= shortestDist:
                            continue
                        waypoints[i] = None
                        FindShortestRoute(prefix, candidateDist, toID)
                        waypoints[i] = toID

                    _pop()
                else:
                    for i in indexes:
                        toID = waypoints[i]
                        if not toID:
                            continue
                        candidateDist = distanceSoFar + distanceTo[toID]
                        if candidateDist < shortestDist:
                            shortestRouteSoFar[:] = [candidateDist, prefix[:], toID]
                            shortestDist = candidateDist



            shortestRouteSoFar = [999999999, None, None]
            indexes = range(len(waypoints))
            FindShortestRoute(prefix, 0, eve.session.solarsystemid2)
            (distance, waypoints, last,) = shortestRouteSoFar
            blue.pyos.synchro.SleepWallclock(1)
            endTime = blue.os.GetWallclockTimeNow()
            if waypoints is None:
                raise UserError('AutoPilotDisabledUnreachable')
            if isReturnTrip == True:
                sm.GetService('starmap').SetWaypoints(waypoints + [last] + [eve.session.solarsystemid2])
            else:
                sm.GetService('starmap').SetWaypoints(waypoints + [last])

        finally:
            setattr(self, 'isOptimizing', False)




    def Confirm(self, *args):
        pass



    def Deselect(self, *args):
        pass



    def Select(self, selection, *args):
        sm.GetService('starmap').SetInterest(selection.id)



    def ChangeWaypointSorting(self, orderID = -1, *args):
        if getattr(self, 'isChangingOrder', False):
            return 
        try:
            setattr(self, 'isChangingOrder', True)
            sel = self.sr.scroll2.GetSelected()
            starmapSvc = sm.GetService('starmap')
            if not len(sel):
                return 
            waypoints = starmapSvc.GetWaypoints()
            waypointIndex = sel[0].orderID
            if waypointIndex < 0:
                return 
            if waypointIndex > len(waypoints):
                return 
            waypoint = waypoints[waypointIndex]
            del waypoints[waypointIndex]
            if waypointIndex < orderID:
                orderID -= 1
            if orderID == -1:
                orderID = len(waypoints)
            waypoints.insert(orderID, waypoint)
            starmapSvc.SetWaypoints(waypoints)

        finally:
            setattr(self, 'isChangingOrder', False)




    def OnLoadWMCPSettings(self, tabName):
        if self.loadedTab == tabName:
            self.LoadSettings(tabName)



    def LoadSettings(self, what):
        scrolllist = []
        if what == 'autopilotconf':
            pfRouteType = settings.char.ui.Get('pfRouteType', 'safe')
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrRoutePlanning')}))
            for config in [['pfRouteType',
              'shortest',
              localization.GetByLabel('UI/Map/MapPallet/cbPreferShorter'),
              pfRouteType == 'shortest'], ['pfRouteType',
              'safe',
              localization.GetByLabel('UI/Map/MapPallet/cbPreferSafer'),
              pfRouteType == 'safe'], ['pfRouteType',
              'unsafe',
              localization.GetByLabel('UI/Map/MapPallet/cbPreferRisky'),
              pfRouteType == 'unsafe']]:
                self.AddCheckBox(config, scrolllist, 'pfRouteType', 1)

            for config in [['pfAvoidPodKill',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbAdvoidPodkill'),
              settings.char.ui.Get('pfAvoidPodKill', 0) == 1], ['pfAvoidSystems',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbAdvoidSystemsOnList'),
              settings.char.ui.Get('pfAvoidSystems', 1) == 1]]:
                self.AddCheckBox(config, scrolllist, usecharsettings=1)

            self.AddSlider('pfPenalty', scrolllist, localization.GetByLabel('UI/Map/MapPallet/lblSecurityPenelity'), 1.0, 100.0, localization.GetByLabel('UI/Map/MapPallet/hintSecurityPeneltySlider'))
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/tabWaypoints')}))
            autopilot_stop_at_each_waypoint = settings.user.ui.Get('autopilot_stop_at_each_waypoint', 0)
            for config in [['autopilot_stop_at_each_waypoint',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbDisableAtEachWaypoint'),
              autopilot_stop_at_each_waypoint == 0], ['autopilot_stop_at_each_waypoint',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbContinueAtEachWaypoint'),
              autopilot_stop_at_each_waypoint == 1]]:
                self.AddCheckBox(config, scrolllist, 'autopilot_stop_at_each_waypoint')

        if what == 'mapsettings_lines':
            showlines = settings.user.ui.Get('showlines', 4)
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrConnectionLines')}))
            for config in [['showlines',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbNoLines'),
              showlines == 0],
             ['showlines',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionLinesOnly'),
              showlines == 1],
             ['showlines',
              2,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionRegionLinesOnly'),
              showlines == 2],
             ['showlines',
              3,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionRegionNeighborLinesOnly'),
              showlines == 3],
             ['showlines',
              4,
              localization.GetByLabel('UI/Map/MapPallet/cbAllLinesOnly'),
              showlines == 4]]:
                self.AddCheckBox(config, scrolllist, 'showlines')

            for config in [['map_alliance_jump_lines',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbAllianceJumpLines'),
              settings.user.ui.Get('map_alliance_jump_lines', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrColorLinesBy')}))
            for config in [['mapcolorby',
              mapcommon.COLORMODE_UNIFORM,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByJumpType'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_UNIFORM], ['mapcolorby',
              mapcommon.COLORMODE_REGION,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByRegion'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_REGION], ['mapcolorby',
              mapcommon.COLORMODE_STANDINGS,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByStanding'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_STANDINGS]]:
                self.AddCheckBox(config, scrolllist, 'mapcolorby')

        if what == 'mapsettings_tiles':
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrTileSettings')}))
            for config in [['map_tile_no_tiles',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesNone'),
              settings.user.ui.Get('map_tile_no_tiles', 1) == 1],
             ['map_tile_activity',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChanges'),
              settings.user.ui.Get('map_tile_activity', 0) == 1],
             ['map_tile_show_unflattened',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChangesUnflattened'),
              settings.user.ui.Get('map_tile_show_unflattened', 0) == 1],
             ['map_tile_show_outlines',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChangesOutlined'),
              settings.user.ui.Get('map_tile_show_outlines', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

            activeTileMode = settings.user.ui.Get('map_tile_mode', 0)
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrTileSovColorBy')}))
            for (tileMode, text,) in [(0, localization.GetByLabel('UI/Map/MapPallet/cbTilesSovereignty')), (1, localization.GetByLabel('UI/Map/MapPallet/cbTilesStandings'))]:
                config = ['map_tile_mode',
                 tileMode,
                 text,
                 activeTileMode == tileMode]
                self.AddCheckBox(config, scrolllist, 'map_tile_mode')

        if what == 'mapsettings_legend':
            scrolllist += self.GetLegendGroups()
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        if what == 'starview_color':
            scrolllist += self.GetStarColorGroups()
        if what == 'mapsettings_solarsystem':
            scrolllist += self.GetSolarSystemOptions()
        if what == 'mapsettings_other':
            self.AddCheckBox(['mapautoframe',
             None,
             localization.GetByLabel('UI/Map/MapPallet/cbAnimFrameSelect'),
             settings.user.ui.Get('mapautoframe', 1) == 1], scrolllist)
            if settings.user.ui.Get('mapautoframe', 1) == 1:
                self.AddCheckBox(['mapautozoom',
                 None,
                 localization.GetByLabel('UI/Map/MapPallet/cbAnimAutoZoom'),
                 settings.user.ui.Get('mapautozoom', 0) == 1], scrolllist)
        if what == 'mapsettings_labels':
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrRegionLables')}))
            for config in [['rlabel_region',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionNoLabel'),
              settings.user.ui.Get('rlabel_region', 1) == 0],
             ['rlabel_region',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionSelected'),
              settings.user.ui.Get('rlabel_region', 1) == 1],
             ['rlabel_region',
              2,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionAndNeigbour'),
              settings.user.ui.Get('rlabel_region', 1) == 2],
             ['rlabel_region',
              3,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionAll'),
              settings.user.ui.Get('rlabel_region', 1) == 3]]:
                self.AddCheckBox(config, scrolllist, 'rlabel_region')

            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Map/MapPallet/hdrOtherLables')}))
            for config in [['label_constellation',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherConstellation'),
              settings.user.ui.Get('label_constellation', 1) == 1], ['label_solarsystem',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherSolarSysytem'),
              settings.user.ui.Get('label_solarsystem', 1) == 1], ['label_landmarknames',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherLandmarks'),
              settings.user.ui.Get('label_landmarknames', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

        if self.destroyed:
            return 
        self.sr.scroll2.Load(contentList=scrolllist)



    def GetActiveStarColorMode(self):
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        if not self.starColorByID:
            self.starColorByID = {}
            groupList = ['Root'] + self.GetAllStarColorGroupLabels()
            try:
                groupList.remove('Sovereignty_Sovereignty')
                groupList.remove('Occupancy_Occupancy')
            except ValueError:
                log.LogError('Error while removing a sov option from the prime list - a long load may be impending!')
            for groupName in groupList:
                func = getattr(self, 'Get%sOptions' % groupName, None)
                if func is None:
                    continue
                ops = func()
                for (label, id,) in ops:
                    self.starColorByID[id] = (groupName, label)


        if starscolorby not in self.starColorByID:
            if type(starscolorby) == types.TupleType and starscolorby[0] in (mapcommon.STARMODE_FACTION, mapcommon.STARMODE_MILITIA, mapcommon.STARMODE_FACTIONEMPIRE):
                (_starmode, factionID,) = starscolorby
                options = {mapcommon.STARMODE_FACTION: ('Sovereignty', localization.GetByLabel('UI/Map/MapPallet/cbModeFactions')),
                 mapcommon.STARMODE_MILITIA: ('Occupancy', localization.GetByLabel('UI/Map/MapPallet/cbModeMilitias'))}.get(_starmode, (None, None))
                (colorBy, factionName,) = options
                if factionID >= 0:
                    factionName = cfg.eveowners.Get(factionID).name
                self.starColorByID[starscolorby] = (colorBy, factionName)
        return self.starColorByID.get(starscolorby, (None, None))



    def GetStarColorEntries(self, forGroup):
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        func = getattr(self, 'Get%sOptions' % forGroup, None)
        if not func:
            log.LogError('Missing function to provide options for', forGroup)
            return []
        scrolllist = []
        sublevel = 2 if forGroup.find('_') > 0 else 0
        for (label, flag,) in func():
            config = ['starscolorby',
             flag,
             label,
             starscolorby == flag]
            entry = self.AddCheckBox(config, None, 'starscolorby', sublevel=sublevel)
            scrolllist.append(entry)

        return scrolllist



    def GetRootOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsActual'), mapcommon.STARMODE_REAL],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsSecurity'), mapcommon.STARMODE_SECURITY],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsRegion'), mapcommon.STARMODE_REGION],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsDedDeadspace'), mapcommon.STARMODE_DUNGEONS],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsDedAgents'), mapcommon.STARMODE_DUNGEONSAGENTS],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsIncursion'), mapcommon.STARMODE_INCURSION]]
        if eve.session.role & ROLE_GML:
            ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsIncursionGM'), mapcommon.STARMODE_INCURSIONGM])
        ret.sort()
        return ret



    def GetAutopilotOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsAdvoidance'), mapcommon.STARMODE_AVOIDANCE]]
        return ret



    def GetStatisticsOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsPilots30Min'), mapcommon.STARMODE_PLAYERCOUNT],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsPilotsDocked'), mapcommon.STARMODE_PLAYERDOCKED],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsJumps'), mapcommon.STARMODE_JUMPS1HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsDestroyed'), mapcommon.STARMODE_SHIPKILLS1HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsDestroyed24H'), mapcommon.STARMODE_SHIPKILLS24HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsPoded1H'), mapcommon.STARMODE_PODKILLS1HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsPoded24H'), mapcommon.STARMODE_PODKILLS24HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsNPCDestroyed'), mapcommon.STARMODE_FACTIONKILLS1HR],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsStationCount'), mapcommon.STARMODE_STATIONCOUNT],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsCynosuarl'), mapcommon.STARMODE_CYNOSURALFIELDS]]
        ret.sort()
        return ret



    def GetOccupancy_StatisticsOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed1H'), mapcommon.STARMODE_MILITIAKILLS1HR], [localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed24H'), mapcommon.STARMODE_MILITIAKILLS24HR]]
        ret.sort()
        return ret



    def GetPersonalOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsMyBookmarks'), mapcommon.STARMODE_BOOKMARKED],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsMyAssets'), mapcommon.STARMODE_ASSETS],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsIVisited'), mapcommon.STARMODE_VISITED],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsCargoLeagal'), mapcommon.STARMODE_CARGOILLEGALITY],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsPIScanRange'), mapcommon.STARMODE_PISCANRANGE]]
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole != 0:
            ret += [[localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpOffices'), mapcommon.STARMODE_CORPOFFICES],
             [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpImpounded'), mapcommon.STARMODE_CORPIMPOUNDED],
             [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpProperty'), mapcommon.STARMODE_CORPPROPERTY],
             [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpDeliveries'), mapcommon.STARMODE_CORPDELIVERIES]]
        ret += [[localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpMembers'), mapcommon.STARMODE_FRIENDS_CORP], [localization.GetByLabel('UI/Map/MapPallet/cbStarsFleetMembers'), mapcommon.STARMODE_FRIENDS_FLEET], [localization.GetByLabel('UI/Map/MapPallet/cbStarsMyAgents'), mapcommon.STARMODE_FRIENDS_AGENT]]
        ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsMyColonies'), mapcommon.STARMODE_MYCOLONIES])
        ret.sort()
        return ret



    def GetServicesOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsBounties'), mapcommon.STARMODE_SERVICE_BountyMissions],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsClone'), mapcommon.STARMODE_SERVICE_Cloning],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsFactory'), mapcommon.STARMODE_SERVICE_Factory],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsFitting'), mapcommon.STARMODE_SERVICE_Fitting],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsInsurance'), mapcommon.STARMODE_SERVICE_Insurance],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsLaboratory'), mapcommon.STARMODE_SERVICE_Laboratory],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsRefinery'), mapcommon.STARMODE_SERVICE_Refinery],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsRepair'), mapcommon.STARMODE_SERVICE_RepairFacilities],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitia'), mapcommon.STARMODE_SERVICE_NavyOffices],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsReprocessing'), mapcommon.STARMODE_SERVICE_ReprocessingPlant]]
        ret.sort()
        return ret



    def GetOccupancy_OccupancyOptions(self):
        warfactionlist = []
        for factionID in sm.StartService('facwar').GetWarFactions():
            factionName = cfg.eveowners.Get(factionID).name
            warfactionlist.append([factionName.lower(), factionName, factionID])

        warfactionlist.sort()
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbModeMilitias'), (mapcommon.STARMODE_MILITIA, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)]]
        for (fNL, factionName, factionID,) in warfactionlist:
            ret.append([factionName, (mapcommon.STARMODE_MILITIA, factionID)])

        return ret



    def GetOccupancy_DefensiveOptions(self):
        return self.GetOccupancyDefensiveOffensive('defending')



    def GetOccupancy_OffensiveOptions(self):
        return self.GetOccupancyDefensiveOffensive('attacking')



    def GetOccupancyDefensiveOffensive(self, direction = 'defending'):
        starmode = mapcommon.STARMODE_MILITIAOFFENSIVE if direction == 'attacking' else mapcommon.STARMODE_MILITIADEFENSIVE
        warfactionlist = []
        for factionID in sm.StartService('facwar').GetWarFactions():
            factionName = cfg.eveowners.Get(factionID).name
            warfactionlist.append([factionName.lower(), factionName, factionID])

        warfactionlist.sort()
        ret = []
        if eve.session.warfactionid:
            ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsMyMilitia'), (starmode, mapcommon.STARMODE_FILTER_FACWAR_MINE)])
            if direction == 'defending':
                ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsEnemyMilitia'), (starmode, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)])
        for (fNL, factionName, factionID,) in warfactionlist:
            ret.append([factionName, (starmode, factionID)])

        return ret



    def GetSovereignty_SovereigntyOptions(self):
        loadSvc = sm.StartService('loading')
        try:
            loadSvc.ProgressWnd(localization.GetByLabel('UI/Map/MapPallet/msgFetchingData'), '', 1, 3)
            factionlist = []
            factionIDs = sm.GetService('starmap').GetAllFactionsAndAlliances()
            cfg.eveowners.Prime(factionIDs)
            for factionID in factionIDs:
                factionName = cfg.eveowners.Get(factionID).name
                factionlist.append([factionName.lower(), factionName, factionID])

            loadSvc.ProgressWnd(localization.GetByLabel('UI/Map/MapPallet/msgFetchingData'), localization.GetByLabel('UI/Map/MapPallet/msgSortingData'), 2, 3)
            factionlist.sort()
            ret = [[localization.GetByLabel('UI/Map/MapPallet/cbModeFactions'), (mapcommon.STARMODE_FACTION, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)]]
            ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsByStandings'), mapcommon.STARMODE_SOV_STANDINGS])
            ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsByEmpireFactions'), (mapcommon.STARMODE_FACTIONEMPIRE, mapcommon.STARMODE_FILTER_EMPIRE)])
            for (fNL, factionName, factionID,) in factionlist:
                ret.append([factionName, (mapcommon.STARMODE_FACTION, factionID)])


        finally:
            loadSvc.ProgressWnd(localization.GetByLabel('UI/Map/MapPallet/msgFetchingData'), localization.GetByLabel('UI/Generic/Done'), 3, 3)

        return ret



    def GetSovereignty_ChangesOptions(self):
        ret = [(localization.GetByLabel('UI/Map/MapPallet/cbStarsByRecientSovChanges'), mapcommon.STARMODE_SOV_CHANGE),
         (localization.GetByLabel('UI/Map/MapPallet/cbStarsBySovGain'), mapcommon.STARMODE_SOV_GAIN),
         (localization.GetByLabel('UI/Map/MapPallet/cbStarsBySovLoss'), mapcommon.STARMODE_SOV_LOSS),
         (localization.GetByLabel('UI/Map/MapPallet/cbStarsByStationGain'), mapcommon.STARMODE_OUTPOST_GAIN),
         (localization.GetByLabel('UI/Map/MapPallet/cbStarsByStationLoss'), mapcommon.STARMODE_OUTPOST_LOSS)]
        return ret



    def GetSovereignty_Development_IndicesOptions(self):
        ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxStrategic'), mapcommon.STARMODE_INDEX_STRATEGIC], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxMilitary'), mapcommon.STARMODE_INDEX_MILITARY], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxIndustry'), mapcommon.STARMODE_INDEX_INDUSTRY]]
        return ret



    def GetPlanetsOptions(self):
        ret = []
        for planetTypeID in PLANET_TYPES:
            ret.append((cfg.invtypes.Get(planetTypeID).typeName, (mapcommon.STARMODE_PLANETTYPE, planetTypeID)))

        ret.sort()
        return ret



    def GetSolarSystemOptions(self):
        validGroups = maputils.GetValidSolarsystemGroups()
        wantedGroups = maputils.GetVisibleSolarsystemBrackets()
        wantedHints = maputils.GetHintsOnSolarsystemBrackets()
        scrolllist = []
        for groupID in validGroups:
            data = util.KeyVal()
            data.visible = groupID in wantedGroups
            data.showhint = groupID in wantedHints
            data.groupID = groupID
            if type(groupID) in types.StringTypes:
                cerbString = {'bookmark': 'UI/Map/MapPallet/cbSolarSystem_bookmark',
                 'scanresult': 'UI/Map/MapPallet/cbSolarSystem_scanresult'}[groupID]
                data.label = localization.GetByLabel(cerbString)
            else:
                data.label = cfg.invgroups.Get(groupID).name
            scrolllist.append((data.label, listentry.Get('BracketSelectorEntry', data=data)))

        if scrolllist:
            scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GetAllStarColorGroupLabels(self):
        self.GetStarColorGroupsSorted()
        topLevel = [ each[0] for each in self.starColorGroups ]
        tmp = [ each[2] for each in self.starColorGroups if each[2] != [] ]
        subLevel = []
        for each in tmp:
            subLevel.extend([ yu[0] for yu in each ])

        return topLevel + subLevel



    def GetStarColorGroupsSorted(self):
        if not self.starColorGroups:
            starColorGroups = [('Personal', localization.GetByLabel('UI/Map/MapPallet/hdrStarsMyInformation'), []),
             ('Services', localization.GetByLabel('UI/Map/MapPallet/hdrStarsServices'), []),
             ('Statistics', localization.GetByLabel('UI/Map/MapPallet/hdrStarsStatistics'), []),
             ('Sovereignty', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), [('Sovereignty_Sovereignty', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), []), ('Sovereignty_Changes', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyChanges'), []), ('Sovereignty_Development_Indices', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyIndixes'), [])]),
             ('Occupancy', localization.GetByLabel('UI/Map/MapPallet/hdrStarsOccupancy'), [('Occupancy_Occupancy', localization.GetByLabel('UI/Map/MapPallet/hdrStarsOccupancy'), []),
               ('Occupancy_Defensive', localization.GetByLabel('UI/Map/MapPallet/hdrStarsDefensive'), []),
               ('Occupancy_Offensive', localization.GetByLabel('UI/Map/MapPallet/hdrStarsOffensive'), []),
               ('Occupancy_Statistics', localization.GetByLabel('UI/Map/MapPallet/hdrStarsMapStats'), [])]),
             ('Autopilot', localization.GetByLabel('UI/Map/MapPallet/hdrStarsAutoPilot'), []),
             ('Planets', localization.GetByLabel('UI/Map/MapPallet/hdrStarsPlanets'), [])]
            for (group, label, subitems,) in starColorGroups:
                if subitems:
                    temp = []
                    for (_group, _label, _subitems,) in subitems:
                        temp.append((_label, (_group, _label, _subitems)))

                    temp = uiutil.SortListOfTuples(temp)
                    subitems = temp
                self.starColorGroups.append((label, (group, label, subitems)))

            self.starColorGroups = uiutil.SortListOfTuples(self.starColorGroups)
        return self.starColorGroups



    def GetStarColorGroups(self):
        self.GetStarColorGroupsSorted()
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        scrolllist = []
        scrolllist = self.GetStarColorEntries('Root')
        (activeGroup, activeLabel,) = self.GetActiveStarColorMode()
        for (groupName, groupLabel, subitems,) in self.starColorGroups:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = {'GetSubContent': self.GetSubContent,
             'label': groupLabel,
             'id': id,
             'groupItems': subitems,
             'iconMargin': 32,
             'showlen': 0,
             'state': 'locked',
             'BlockOpenWindow': 1,
             'key': groupName}
            if activeGroup == groupName:
                data['posttext'] = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            scrolllist.append(listentry.Get('Group', data))

        return scrolllist



    def GetStarColorSubGroups(self, subitems):
        scrolllist = []
        (activeGroup, activeLabel,) = self.GetActiveStarColorMode()
        for (groupName, groupLabel, subitems,) in subitems:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = {'GetSubContent': self.GetSubContent,
             'label': groupLabel,
             'id': id,
             'groupItems': [],
             'iconMargin': 32,
             'showlen': 0,
             'state': 'locked',
             'BlockOpenWindow': 1,
             'key': groupName,
             'sublevel': 1}
            if activeGroup == groupName:
                data['posttext'] = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            scrolllist.append(listentry.Get('Group', data))

        return scrolllist



    def GetSubContent(self, data, newitems = 0):
        if data.groupItems:
            return self.GetStarColorSubGroups(data.groupItems)
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                continue
            if entry.open:
                if entry.panel:
                    entry.panel.Toggle()
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, 0)
                    entry.scroll.PrepareSubContent(entry)

        if data.key in self.GetAllStarColorGroupLabels():
            return self.GetStarColorEntries(data.key)
        return []



    def UpdateActiveStarColor(self):
        (activeGroup, activeLabel,) = self.GetActiveStarColorMode()
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.key not in self.GetAllStarColorGroupLabels():
                continue
            post = ''
            if entry.key == activeGroup:
                post = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            entry.posttext = post
            if entry.panel:
                entry.panel.UpdateLabel()




    def GetLegendGroups(self):
        common = {'groupItems': [],
         'iconMargin': 32,
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1}
        scrolllist = []
        forLst = [('star', localization.GetByLabel('UI/Map/MapPallet/tabStars')), ('tile', localization.GetByLabel('UI/Map/MapPallet/tabTiles'))]
        for (groupName, groupLabel,) in forLst:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = common.copy()
            data.update({'GetSubContent': self.GetLegendEntries,
             'label': groupLabel,
             'id': id,
             'key': groupName})
            scrolllist.append(listentry.Get('Group', data))

        return scrolllist



    def GetLegendEntries(self, data):
        legendList = sm.GetService('starmap').GetLegend(data.key)
        legendList.sort()
        scrolllist = []
        for legendItem in legendList:
            kv = util.KeyVal()
            kv.label = legendItem.caption
            kv.key = data.key
            kv.editable = False
            kv.selectable = True
            kv.hilightable = False
            kv.legend = legendItem
            scrolllist.append(listentry.Get('LegendEntry', data=kv))

        return scrolllist



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)
            self.sr.scroll2.ShowHint(hintstr)



    def AddSlider(self, config, scrolllist, displayName, minValue, maxValue, hint):
        data = util.KeyVal()
        data.minValue = minValue
        data.maxValue = maxValue
        data.usePrefs = 1
        data.config = config
        data.label = ''
        data.sliderID = config
        data.displayName = displayName
        data.endsetslidervalue = self.EndSetSliderValue
        data.hint = hint
        data.selectable = False
        scrolllist.append(listentry.Get('Slider', data=data))



    def EndSetSliderValue(self, slider):
        settings.char.ui.Set('pfPenalty', slider.value)
        uthread.pool('Palette:EndSetSliderValueThread', self.EndSetSliderValueThread)



    def EndSetSliderValueThread(self):
        sm.GetService('pathfinder').MakeDirty()
        sm.GetService('starmap').UpdateRoute()



    def AddCheckBox(self, config, scrolllist, group = None, usecharsettings = 0, sublevel = 0):
        (cfgname, retval, desc, default,) = config
        data = util.KeyVal()
        data.label = desc
        data.checked = default
        data.cfgname = cfgname
        data.retval = retval
        data.group = group
        data.sublevel = sublevel
        data.OnChange = self.CheckBoxChange
        data.usecharsettings = usecharsettings
        if scrolllist is not None:
            scrolllist.append(listentry.Get('Checkbox', data=data))
        else:
            return listentry.Get('Checkbox', data=data)



    def CheckBoxChange(self, checkbox):
        starmapSvc = sm.GetService('starmap')
        key = checkbox.data['key']
        val = checkbox.data['retval']
        if val is None:
            val = checkbox.checked
        if checkbox.data.get('usecharsettings', 0):
            settings.char.ui.Set(key, val)
        else:
            settings.user.ui.Set(key, val)
        if key == 'mapautoframe':
            self.LoadSettings('mapsettings_other')
        viewingStarmap = sm.GetService('viewState').IsViewActive('starmap')
        if viewingStarmap:
            if key == 'mapautoframe':
                starmapSvc.SetInterest()
            elif key == 'mapautozoom':
                starmapSvc.SetInterest()
            elif key == 'mapcolorby':
                starmapSvc.UpdateLines(updateColor=1)
            elif key == 'showlines':
                starmapSvc.UpdateLines()
            elif key == 'map_alliance_jump_lines':
                starmapSvc.UpdateLines()
            elif key == 'starscolorby':
                starmapSvc.SetStarColorMode()
                self.UpdateActiveStarColor()
            elif key[:6] == 'label_':
                starmapSvc.CheckAllLabels('Mappalette::CheckBoxChange')
            elif key == 'rlabel_region':
                starmapSvc.CheckAllLabels('Mappalette::CheckBoxChange2')
            elif key.startswith('map_tile_'):
                starmapSvc.UpdateHexMap()
        if key == 'pfRouteType':
            sm.GetService('pathfinder').SetRouteType(val)
            starmapSvc.UpdateRoute()
        elif key in ('pfAvoidPodKill', 'pfAvoidSystems'):
            if key == 'pfAvoidPodKill':
                if val:
                    eve.Message('MapAutoPilotAvoidPodkillZones')
                sm.GetService('pathfinder').SetPodKillAvoidance(val)
            elif val:
                eve.Message('MapAutoPilotAvoidSystems')
            sm.GetService('pathfinder').SetSystemAvoidance(val)
            if viewingStarmap:
                starmapSvc.UpdateRoute()
        elif key == 'expandwaypoints':
            self.LoadWaypoints()



    def AddSeperator(self, height, where):
        uicls.Container(name='push', align=uiconst.TOTOP, height=height, parent=where)



    def AddHeader(self, header, where, height = 12):
        uicls.EveLabelMedium(text=header, parent=where, align=uiconst.TOTOP, height=12, state=uiconst.UI_NORMAL)



    def OnSelectionChange(self, selected):
        dataList = []
        colorList = []
        for node in selected:
            if node.key == 'tile':
                if node.legend.data is not None:
                    dataList.append(node.legend.data)
                else:
                    colorList.append(node.legend.color)

        if sm.GetService('viewState').IsViewActive('starmap'):
            sm.GetService('starmap').HighlightTiles(dataList, colorList)



    def Minimize(self, *args, **kwds):
        if self.windowID == 'mapspalette':
            settings.user.ui.Set('MapWindowMinimized', True)
        uicls.Window.Minimize(self, *args, **kwds)



    def Maximize(self, *args, **kwds):
        if self.windowID == 'mapspalette':
            settings.user.ui.Set('MapWindowMinimized', False)
        uicls.Window.Maximize(self, *args, **kwds)




class BracketSelectorEntry(listentry.Generic):
    __guid__ = 'listentry.BracketSelectorEntry'
    __update_on_reload__ = 1

    def init(self):
        pass



    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        props = {'parent': self,
         'align': uiconst.TOPRIGHT,
         'idx': 0}
        pos = (18, 0, 0, 0)
        eye = uicls.Icon(icon='ui_38_16_110', pos=pos, name='eye', hint=localization.GetByLabel('UI/Map/MapPallet/hintShow'), **props)
        eye.OnClick = self.ToggleVisibility
        self.sr.eyeoff = uicls.Icon(icon='ui_38_16_111', pos=pos, **props)
        hint = uicls.Icon(icon='ui_38_16_109', name='hint', hint=localization.GetByLabel('UI/Map/MapPallet/hintShowHint'), **props)
        hint.OnClick = self.ToggleBubbleHint
        self.sr.hintoff = uicls.Icon(icon='ui_38_16_111', **props)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        if node.visible:
            self.sr.eyeoff.state = uiconst.UI_HIDDEN
        else:
            self.sr.eyeoff.state = uiconst.UI_DISABLED
        if node.showhint:
            self.sr.hintoff.state = uiconst.UI_HIDDEN
        else:
            self.sr.hintoff.state = uiconst.UI_DISABLED



    def ToggleVisibility(self, *args):
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        visible = not self.sr.node.visible
        wantedGroups = maputils.GetVisibleSolarsystemBrackets()[:]
        for node in sel:
            node.visible = visible
            if node.groupID not in wantedGroups and visible:
                wantedGroups.append(node.groupID)
            elif node.groupID in wantedGroups and not visible:
                wantedGroups.remove(node.groupID)
            if node.panel:
                node.panel.Load(node)

        settings.user.ui.Set('groupsInSolarsystemMap', wantedGroups)
        sm.ScatterEvent('OnSolarsystemMapSettingsChange', 'brackets')



    def ToggleBubbleHint(self, *args):
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        showhint = not self.sr.node.showhint
        wantedHints = maputils.GetHintsOnSolarsystemBrackets()[:]
        for node in sel:
            node.showhint = showhint
            if node.groupID not in wantedHints and showhint:
                wantedHints.append(node.groupID)
            elif node.groupID in wantedHints and not showhint:
                wantedHints.remove(node.groupID)
            if node.panel:
                node.panel.Load(node)

        settings.user.ui.Set('hintsInSolarsystemMap', wantedHints)
        sm.ScatterEvent('OnSolarsystemMapSettingsChange', 'brackets')




class LegendEntry(listentry.Generic):
    __guid__ = 'listentry.LegendEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.legendColor = uicls.Container(name='legendColor', parent=self, align=uiconst.TOPLEFT, pos=(2, 2, 12, 12), idx=0)
        self.sr.colorFill = uicls.Fill(parent=self.sr.legendColor)
        uicls.Frame(parent=self.sr.legendColor, color=(0.25, 0.25, 0.25), idx=0)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.label.left = 18
        node.legend.color.a = 1.0
        c = node.legend.color
        self.sr.colorFill.SetRGB(c.r, c.g, c.b, c.a)
        self.key = node.key
        self.legend = node.legend



    def GetMenu(self):
        m = []
        if self.legend.data is not None:
            m += sm.GetService('menu').GetGMMenu(itemID=self.legend.data)
        if self.legend.data is not None:
            if util.IsFaction(self.legend.data):
                m += sm.GetService('menu').GetMenuFormItemIDTypeID(self.legend.data, const.typeFaction)
            elif util.IsRegion(self.legend.data):
                m += sm.GetService('menu').CelestialMenu(self.legend.data)
            else:
                m += sm.GetService('menu').GetMenuFormItemIDTypeID(self.legend.data, const.typeAlliance)
        return m




