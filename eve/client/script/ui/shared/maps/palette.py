import blue
import uthread
import uix
import uiutil
import form
import trinity
import util
import listentry
import types
import uiconst
import uicls
import maputils
import log
import mapcommon
from service import ROLE_GML
import util
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
    default_left = '__right__'
    default_top = 0
    default_width = 400
    default_height = 320

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
        self.SetCaption(mls.UI_SHARED_MAPWORLDCTRLPANEL)
        self.MakeUnKillable()
        self.loadedTab = None
        if self.destroyed:
            return 
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
        waypointopt = uicls.Container(name='waypointopt', parent=self.sr.main, align=uiconst.TOBOTTOM, height=85, idx=0)
        waypointbtns2 = uicls.ButtonGroup(btns=[[mls.UI_SHARED_MAPOPTIMIZE,
          self.TravellingSalesman,
          (),
          66]], parent=waypointopt)
        label = uicls.Label(text=mls.UI_SHARED_MAPMOVEWAYPOINTS, parent=waypointopt, pos=(5, 2, 0, 0))
        cbox = uicls.Checkbox(text=mls.UI_SHARED_MAPWAYPOINTSEXPANDED, parent=waypointopt, configName='expandwaypoints', retval=None, checked=settings.user.ui.Get('expandwaypoints', 1), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(5, 18, 140, 0))
        cbox.data = {'key': 'expandwaypoints',
         'retval': None}
        waypointopt.height = waypointbtns2.height + cbox.height + const.defaultPadding + 18
        self.sr.waypointopt = waypointopt
        flattened = settings.user.ui.Get('mapFlattened', 1)
        toggleFlatLabel = mls.UI_CMD_FLATTENMAP
        if flattened:
            toggleFlatLabel = mls.UI_CMD_UNFLATTEN
        if sm.GetService('map').ViewingStarMap():
            toggleMapLabel = mls.UI_GENERIC_SOLARSYSTEMMAP
        else:
            toggleMapLabel = mls.UI_GENERIC_STARMAP
        btns = uicls.ButtonGroup(btns=[['mapCloseBtn',
          mls.UI_CMD_CLOSEMAP,
          sm.GetService('map').Close,
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
        uicls.Label(text=mls.UI_SHARED_MAPTYPELOCATIONNAME, parent=inpt, letterspace=1, fontsize=9, left=0, top=-14, state=uiconst.UI_DISABLED, uppercase=1)
        uicls.Button(parent=inpt.parent, label=mls.UI_CMD_SEARCH, func=self.Search, args=1, pos=(inpt.left + inpt.width + 4,
         inpt.top,
         0,
         0), btn_default=1)
        starviewstabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        starviewstabs.Startup([[mls.UI_SHARED_MAPSTARS,
          self.sr.scroll2,
          self,
          'starview_color'],
         [mls.UI_SHARED_MAPLABELS,
          self.sr.scroll2,
          self,
          'mapsettings_labels'],
         [mls.UI_SHARED_MAPLINES,
          self.sr.scroll2,
          self,
          'mapsettings_lines'],
         [mls.UI_SHARED_MAP_TILES,
          self.sr.scroll2,
          self,
          'mapsettings_tiles'],
         [mls.UI_SHARED_MAPLEGEND,
          self.sr.scroll2,
          self,
          'mapsettings_legend'],
         [mls.UI_SHARED_MAPANIMATION,
          self.sr.scroll2,
          self,
          'mapsettings_other']], 'starviewssub', autoselecttab=0)
        autopilottabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        autopilottabs.Startup([[mls.UI_SHARED_MAPWAYPOINTS,
          self.sr.scroll2,
          self,
          'waypointconf',
          waypointopt], [mls.UI_GENERIC_SETTINGS,
          self.sr.scroll2,
          self,
          'autopilotconf',
          None], [mls.UI_SHARED_MAPAVOIDANCE,
          self.sr.scroll2,
          self,
          'avoidconf',
          None]], 'autopilottabs', autoselecttab=0)
        self.sr.autopilottabs = autopilottabs
        self.sr.starviewstabs = starviewstabs
        self.sr.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        self.sr.maintabs.Startup([[mls.UI_SHARED_MAPSEARCH,
          self.sr.scroll,
          self,
          'mapsearchpanel',
          searchpar],
         [mls.UI_GENERIC_STARMAP,
          self.sr.scroll2,
          self,
          'mapsettings',
          starviewstabs],
         [mls.UI_GENERIC_SOLARSYSTEMMAP,
          self.sr.scroll2,
          self,
          'mapsettings_solarsystem',
          None],
         [mls.UI_GENERIC_AUTOPILOT,
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
            btn.SetLabel(mls.UI_CMD_UNFLATTEN)
        else:
            btn.SetLabel(mls.UI_CMD_FLATTENMAP)



    def ShowPanel(self, panelname):
        if panelname == mls.UI_SHARED_MAPWAYPOINTS:
            self.sr.autopilottabs.ShowPanelByName(mls.UI_SHARED_MAPWAYPOINTS)
            self.sr.maintabs.ShowPanelByName(mls.UI_GENERIC_AUTOPILOT)
        else:
            uthread.pool('MapPalette::ShowPanel', self.sr.maintabs.ShowPanelByName, panelname)



    def Load(self, key):
        self.SetHint()
        if key == 'mapsettings_solarsystem':
            self.sr.waypointopt.state = uiconst.UI_HIDDEN
        if key == 'mapsearchpanel':
            self.Search(0)
            self.sr.waypointopt.state = uiconst.UI_HIDDEN
        elif key == 'mapsettings':
            self.sr.starviewstabs.AutoSelect()
            self.sr.waypointopt.state = uiconst.UI_HIDDEN
        elif key == 'options':
            self.sr.optionstabs.AutoSelect()
            self.sr.waypointopt.state = uiconst.UI_HIDDEN
        elif key == 'autopilot':
            self.sr.autopilottabs.AutoSelect()
        elif key[:11] == 'mapsettings' or key == 'autopilotconf' or key[:8] == 'starview':
            if key == self.loadedTab:
                return 
            self.LoadSettings(key)
        elif key == 'waypointconf':
            self.LoadWaypoints()
        elif key == 'avoidconf':
            self.LoadAvoidance()
        if self.destroyed:
            return 
        self.loadedTab = key



    def CloseX(self, *args):
        if not eve.rookieState:
            uicls.Window.CloseX(self, *args)



    def OnMapModeChangeDone(self, mode):
        if self.destroyed or not hasattr(self, 'sr'):
            return 
        btnFlat = self.sr.flattenBtns.children[0].children[2]
        btnMode = self.sr.flattenBtns.children[0].children[1]
        if mode == 'starmap':
            btnFlat.Enable()
            btnMode.SetLabel(mls.UI_GENERIC_SOLARSYSTEMMAP)
        elif mode == 'systemmap':
            btnFlat.Disable()
            btnMode.SetLabel(mls.UI_GENERIC_STARMAP)



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
                eve.Message('CustomInfo', {'info': mls.UI_SHARED_PLEASETYPESOMETHINGINFO})
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
                trace = ''
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            trace += ' / ' + item.itemName

                scrolllist.append(listentry.Get('Item', {'itemID': each.itemID,
                 'typeID': each.typeID,
                 'label': '%s%s<t>%s' % (each.itemName, trace, cfg.invtypes.Get(each.typeID).name)}))

        if self is None or self.destroyed:
            return 
        self.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_NAME, mls.UI_GENERIC_TYPE])
        if not len(scrolllist):
            self.SetHint(mls.UI_GENERIC_NOTHINGFOUND)



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
            scrolllist.append(listentry.Get('Item', {'itemID': currentPlace.itemID,
             'typeID': currentPlace.typeID,
             'label': '%s:  ' % mls.UI_SHARED_MAPCURRENTLOCTION + currentPlace.itemName,
             'orderID': -1,
             'actualID': 0}))
            for waypointID in waypoints:
                blue.pyos.BeNice()
                actualID = actualID + 1
                each = mapSvc.GetItem(waypointID)
                description = ' ( ' + cfg.invgroups.Get(each.typeID).name + ' ) '
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
                             'label': '   \x95 ' + sunItem.itemName,
                             'orderID': -1,
                             'actualID': actualID}))

                scrolllist.append(listentry.Get('AutoPilotItem', {'itemID': waypointID,
                 'typeID': each.typeID,
                 'label': str(counter + 1) + '. ' + each.itemName + description,
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
            self.SetHint(mls.UI_SHARED_NOWAYPOINTS)
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
                description = ' ( ' + cfg.invgroups.Get(each.typeID).name + ' ) '
                wasID = each.itemID
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            description = description + ' / ' + item.itemName

                scrolllist.append(listentry.Get('Item', {'itemID': itemsID,
                 'typeID': each.typeID,
                 'label': each.itemName + description}))

        if self == None:
            return 
        self.sr.scroll2.Load(contentList=scrolllist)
        if not len(scrolllist):
            self.SetHint(mls.UI_SHARED_NOAVOIDANCEITEMS)



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
                msg = mls.UI_SHARED_MAPQUESTION1
            elif numWaypoints > 10:
                msg = mls.UI_SHARED_MAPQUESTION2
            if msg:
                yesNo = eve.Message('AskAreYouSure', {'cons': msg % {'num': len(waypoints)}}, uiconst.YESNO)
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
            startTime = blue.os.GetTime(1)
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
            blue.pyos.synchro.Sleep(1)
            endTime = blue.os.GetTime(1)
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
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPROUTEPLANNING}))
            for config in [['pfRouteType',
              'shortest',
              mls.UI_SHARED_MAPOPS1,
              pfRouteType == 'shortest'], ['pfRouteType',
              'safe',
              mls.UI_SHARED_MAPOPS2,
              pfRouteType == 'safe'], ['pfRouteType',
              'unsafe',
              mls.UI_SHARED_MAPOPS3,
              pfRouteType == 'unsafe']]:
                self.AddCheckBox(config, scrolllist, 'pfRouteType', 1)

            for config in [['pfAvoidPodKill',
              None,
              mls.UI_SHARED_MAPAVOIDSYS,
              settings.char.ui.Get('pfAvoidPodKill', 0) == 1], ['pfAvoidSystems',
              None,
              mls.UI_SHARED_MAPAVOIDSELSYS,
              settings.char.ui.Get('pfAvoidSystems', 1) == 1]]:
                self.AddCheckBox(config, scrolllist, usecharsettings=1)

            self.AddSlider('pfPenalty', scrolllist, mls.UI_SHARED_MAPSECURITYPENALTY, 1.0, 100.0, mls.UI_SHARED_MAPHINT5)
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPWAYPOINTS}))
            autopilot_stop_at_each_waypoint = settings.user.ui.Get('autopilot_stop_at_each_waypoint', 0)
            for config in [['autopilot_stop_at_each_waypoint',
              0,
              mls.UI_SHARED_MAPOPS4,
              autopilot_stop_at_each_waypoint == 0], ['autopilot_stop_at_each_waypoint',
              1,
              mls.UI_SHARED_MAPOPS5,
              autopilot_stop_at_each_waypoint == 1]]:
                self.AddCheckBox(config, scrolllist, 'autopilot_stop_at_each_waypoint')

        if what == 'mapsettings_lines':
            showlines = settings.user.ui.Get('showlines', 4)
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPCONNLINES}))
            for config in [['showlines',
              0,
              mls.UI_SHARED_MAPOPS6,
              showlines == 0],
             ['showlines',
              1,
              mls.UI_SHARED_MAPOPS7,
              showlines == 1],
             ['showlines',
              2,
              mls.UI_SHARED_MAPOPS8,
              showlines == 2],
             ['showlines',
              3,
              mls.UI_SHARED_MAPOPS9,
              showlines == 3],
             ['showlines',
              4,
              mls.UI_SHARED_MAPOPS10,
              showlines == 4]]:
                self.AddCheckBox(config, scrolllist, 'showlines')

            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPCOLORLINESBY}))
            for config in [['mapcolorby',
              mapcommon.COLORMODE_UNIFORM,
              mls.UI_SHARED_MAPJUMPTYPE,
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_UNIFORM], ['mapcolorby',
              mapcommon.COLORMODE_REGION,
              mls.UI_GENERIC_REGION,
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_REGION], ['mapcolorby',
              mapcommon.COLORMODE_STANDINGS,
              mls.UI_GENERIC_STANDINGS,
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_STANDINGS]]:
                self.AddCheckBox(config, scrolllist, 'mapcolorby')

        if what == 'mapsettings_tiles':
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAP_TILE_SETTINGS}))
            for config in [['map_tile_no_tiles',
              None,
              mls.UI_SHARED_MAP_NO_TILES,
              settings.user.ui.Get('map_tile_no_tiles', 1) == 1],
             ['map_tile_activity',
              None,
              mls.UI_SHARED_MAPSOVEREIGNTY_SHOW_CHANGES,
              settings.user.ui.Get('map_tile_activity', 0) == 1],
             ['map_tile_show_unflattened',
              None,
              mls.UI_SHARED_MAPSOVEREIGNTY_SHOW_WHILE_UNFLATTENED,
              settings.user.ui.Get('map_tile_show_unflattened', 0) == 1],
             ['map_tile_show_outlines',
              None,
              mls.UI_SHARED_MAPSOVEREIGNTY_SHOW_OUTLINES,
              settings.user.ui.Get('map_tile_show_outlines', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

            activeTileMode = settings.user.ui.Get('map_tile_mode', 0)
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPSOVEREIGNTY_COLOR_TILES_BY}))
            for (tileMode, text,) in [(0, mls.UI_SHARED_MAPSOVEREIGNTY), (1, mls.UI_GENERIC_STANDINGS)]:
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
             mls.UI_SHARED_MAPOPS53,
             settings.user.ui.Get('mapautoframe', 1) == 1], scrolllist)
            if settings.user.ui.Get('mapautoframe', 1) == 1:
                self.AddCheckBox(['mapautozoom',
                 None,
                 mls.UI_SHARED_MAPOPS54,
                 settings.user.ui.Get('mapautozoom', 0) == 1], scrolllist)
        if what == 'mapsettings_labels':
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPREGIONLABELS}))
            for config in [['rlabel_region',
              0,
              mls.UI_SHARED_MAPOPS55,
              settings.user.ui.Get('rlabel_region', 1) == 0],
             ['rlabel_region',
              1,
              mls.UI_SHARED_MAPOPS56,
              settings.user.ui.Get('rlabel_region', 1) == 1],
             ['rlabel_region',
              2,
              mls.UI_SHARED_MAPOPS57,
              settings.user.ui.Get('rlabel_region', 1) == 2],
             ['rlabel_region',
              3,
              mls.UI_SHARED_MAPOPS58,
              settings.user.ui.Get('rlabel_region', 1) == 3]]:
                self.AddCheckBox(config, scrolllist, 'rlabel_region')

            scrolllist.append(listentry.Get('Header', {'label': mls.UI_SHARED_MAPOTHERLABELS}))
            for config in [['label_constellation',
              None,
              mls.UI_SHARED_MAPOPS59,
              settings.user.ui.Get('label_constellation', 1) == 1], ['label_solarsystem',
              None,
              mls.UI_SHARED_MAPOPS60,
              settings.user.ui.Get('label_solarsystem', 1) == 1], ['label_landmarknames',
              None,
              mls.UI_SHARED_MAPOPS61,
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
                options = {mapcommon.STARMODE_FACTION: ('Sovereignty', mls.UI_SHARED_MAPOPS52),
                 mapcommon.STARMODE_MILITIA: ('Occupancy', mls.UI_SHARED_MAPOPS70)}.get(_starmode, (None, None))
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
        ret = [[mls.UI_SHARED_MAPOPS11, mapcommon.STARMODE_REAL],
         [mls.UI_SHARED_MAPOPS12, mapcommon.STARMODE_SECURITY],
         [mls.UI_GENERIC_REGION, mapcommon.STARMODE_REGION],
         [mls.UI_SHARED_MAPOPS63, mapcommon.STARMODE_DUNGEONS],
         [mls.UI_SHARED_MAPOPS68, mapcommon.STARMODE_DUNGEONSAGENTS],
         [mls.UI_SHARED_MAP_INCURSIONS, mapcommon.STARMODE_INCURSION]]
        if eve.session.role & ROLE_GML:
            ret.append([mls.UI_SHARED_MAP_INCURSIONSGM, mapcommon.STARMODE_INCURSIONGM])
        ret.sort()
        return ret



    def GetAutopilotOptions(self):
        ret = [[mls.UI_SHARED_MAPOPS73, mapcommon.STARMODE_AVOIDANCE]]
        return ret



    def GetStatisticsOptions(self):
        ret = [[mls.UI_SHARED_MAPOPS16, mapcommon.STARMODE_PLAYERCOUNT],
         [mls.UI_SHARED_MAPOPS17, mapcommon.STARMODE_PLAYERDOCKED],
         [mls.UI_SHARED_MAPOPS18, mapcommon.STARMODE_JUMPS1HR],
         [mls.UI_SHARED_MAPOPS19, mapcommon.STARMODE_SHIPKILLS1HR],
         [mls.UI_SHARED_MAPOPS20, mapcommon.STARMODE_SHIPKILLS24HR],
         [mls.UI_SHARED_MAPOPS21, mapcommon.STARMODE_PODKILLS1HR],
         [mls.UI_SHARED_MAPOPS22, mapcommon.STARMODE_PODKILLS24HR],
         [mls.UI_SHARED_MAPOPS23, mapcommon.STARMODE_FACTIONKILLS1HR],
         [mls.UI_SHARED_MAPOPS25, mapcommon.STARMODE_STATIONCOUNT],
         [mls.UI_SHARED_MAPOPS27, mapcommon.STARMODE_CYNOSURALFIELDS]]
        ret.sort()
        return ret



    def GetOccupancy_StatisticsOptions(self):
        ret = [[mls.UI_SHARED_MAPOPS71, mapcommon.STARMODE_MILITIAKILLS1HR], [mls.UI_SHARED_MAPOPS72, mapcommon.STARMODE_MILITIAKILLS24HR]]
        ret.sort()
        return ret



    def GetPersonalOptions(self):
        ret = [[mls.UI_SHARED_MAPOPS14, mapcommon.STARMODE_BOOKMARKED],
         [mls.UI_SHARED_MAPOPS15, mapcommon.STARMODE_ASSETS],
         [mls.UI_SHARED_MAPOPS24, mapcommon.STARMODE_VISITED],
         [mls.UI_SHARED_MAPOPS26, mapcommon.STARMODE_CARGOILLEGALITY],
         [mls.UI_PI_SCAN_RANGE, mapcommon.STARMODE_PISCANRANGE]]
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole != 0:
            ret += [[mls.UI_CORP_OFFICES, mapcommon.STARMODE_CORPOFFICES],
             [mls.UI_CORP_IMPOUNDED, mapcommon.STARMODE_CORPIMPOUNDED],
             [mls.UI_CORP_PROPERTY, mapcommon.STARMODE_CORPPROPERTY],
             [mls.UI_CORP_DELIVERIES, mapcommon.STARMODE_CORPDELIVERIES]]
        ret += [[mls.UI_SHARED_MAPOPS28, mapcommon.STARMODE_FRIENDS_CORP], [mls.UI_SHARED_MAPOPS29, mapcommon.STARMODE_FRIENDS_FLEET], [mls.UI_SHARED_MAPOPS30, mapcommon.STARMODE_FRIENDS_AGENT]]
        ret.append([mls.UI_PI_MY_COLONIES, mapcommon.STARMODE_MYCOLONIES])
        ret.sort()
        return ret



    def GetServicesOptions(self):
        ret = [[mls.UI_SHARED_MAPOPS33, mapcommon.STARMODE_SERVICE_BountyMissions],
         [mls.UI_SHARED_MAPOPS34, mapcommon.STARMODE_SERVICE_Cloning],
         [mls.UI_SHARED_MAPOPS37, mapcommon.STARMODE_SERVICE_Factory],
         [mls.UI_SHARED_MAPOPS38, mapcommon.STARMODE_SERVICE_Fitting],
         [mls.UI_SHARED_MAPOPS40, mapcommon.STARMODE_SERVICE_Insurance],
         [mls.UI_SHARED_MAPOPS42, mapcommon.STARMODE_SERVICE_Laboratory],
         [mls.UI_SHARED_MAPOPS46, mapcommon.STARMODE_SERVICE_Refinery],
         [mls.UI_SHARED_MAPOPS47, mapcommon.STARMODE_SERVICE_RepairFacilities],
         [mls.UI_STATION_MILITIAOFFICE, mapcommon.STARMODE_SERVICE_NavyOffices],
         [mls.UI_SHARED_MAPOPS48, mapcommon.STARMODE_SERVICE_ReprocessingPlant]]
        ret.sort()
        return ret



    def GetOccupancy_OccupancyOptions(self):
        warfactionlist = []
        for factionID in sm.StartService('facwar').GetWarFactions():
            factionName = cfg.eveowners.Get(factionID).name
            warfactionlist.append([factionName.lower(), factionName, factionID])

        warfactionlist.sort()
        ret = [[mls.UI_SHARED_MAPOPS70, (mapcommon.STARMODE_MILITIA, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)]]
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
            ret.append([mls.UI_FACWAR_MYMILITIA, (starmode, mapcommon.STARMODE_FILTER_FACWAR_MINE)])
            if direction == 'defending':
                ret.append([mls.UI_FACWAR_ENEMYMILITIA, (starmode, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)])
        for (fNL, factionName, factionID,) in warfactionlist:
            ret.append([factionName, (starmode, factionID)])

        return ret



    def GetSovereignty_SovereigntyOptions(self):
        loadSvc = sm.StartService('loading')
        try:
            loadSvc.ProgressWnd(mls.UI_RMR_FETCHINGDATA, '', 1, 3)
            factionlist = []
            factionIDs = sm.GetService('starmap').GetAllFactionsAndAlliances()
            cfg.eveowners.Prime(factionIDs)
            for factionID in factionIDs:
                factionName = cfg.eveowners.Get(factionID).name
                factionlist.append([factionName.lower(), factionName, factionID])

            loadSvc.ProgressWnd(mls.UI_RMR_FETCHINGDATA, mls.UI_SHARED_MAPSORTINGDATA, 2, 3)
            factionlist.sort()
            ret = [[mls.UI_SHARED_MAPOPS52, (mapcommon.STARMODE_FACTION, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)]]
            ret.append([mls.UI_FLEET_STANDINGONLY, mapcommon.STARMODE_SOV_STANDINGS])
            ret.append([mls.UI_SHARED_MAPOPS74, (mapcommon.STARMODE_FACTIONEMPIRE, mapcommon.STARMODE_FILTER_EMPIRE)])
            for (fNL, factionName, factionID,) in factionlist:
                ret.append([factionName, (mapcommon.STARMODE_FACTION, factionID)])


        finally:
            loadSvc.ProgressWnd(mls.UI_RMR_FETCHINGDATA, mls.UI_GENERIC_DONE, 3, 3)

        return ret



    def GetSovereignty_ChangesOptions(self):
        ret = [(mls.SOVEREIGNTY_RECENTCHANGES, mapcommon.STARMODE_SOV_CHANGE),
         (mls.SOVEREIGNTY_SOVGAIN, mapcommon.STARMODE_SOV_GAIN),
         (mls.SOVEREIGNTY_SOVLOSS, mapcommon.STARMODE_SOV_LOSS),
         (mls.SOVEREIGNTY_STATIONGAIN, mapcommon.STARMODE_OUTPOST_GAIN),
         (mls.SOVEREIGNTY_STATIONLOSS, mapcommon.STARMODE_OUTPOST_LOSS)]
        return ret



    def GetSovereignty_Development_IndicesOptions(self):
        ret = [[mls.SOVEREIGNTY_STRATEGIC, mapcommon.STARMODE_INDEX_STRATEGIC], [mls.UI_TUTORIAL_MILITARY, mapcommon.STARMODE_INDEX_MILITARY], [mls.UI_TUTORIAL_INDUSTRY, mapcommon.STARMODE_INDEX_INDUSTRY]]
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
                data.label = getattr(mls, 'UI_GENERIC_' + groupID.upper())
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
            starColorGroups = [('Personal', mls.UI_SHARED_MAPPERSONAL, []),
             ('Services', mls.UI_SHARED_MAPSERVICES, []),
             ('Statistics', mls.UI_SHARED_MAPSTATISTICS, []),
             ('Sovereignty', mls.UI_SHARED_MAPSOVEREIGNTY, [('Sovereignty_Sovereignty', mls.UI_SHARED_MAPSOVEREIGNTY, []), ('Sovereignty_Changes', mls.SOVEREIGNTY_RECENTCHANGES, []), ('Sovereignty_Development_Indices', mls.SOVEREIGNTY_DEVELOPMENTINDICES, [])]),
             ('Occupancy', mls.UI_GENERIC_OCCUPANCY, [('Occupancy_Occupancy', mls.UI_GENERIC_OCCUPANCY, []),
               ('Occupancy_Defensive', mls.UI_GENERIC_DEFENSIVE, []),
               ('Occupancy_Offensive', mls.UI_GENERIC_OFFENSIVE, []),
               ('Occupancy_Statistics', mls.UI_SHARED_MAPSTATISTICS, [])]),
             ('Autopilot', mls.UI_GENERIC_AUTOPILOT, []),
             ('Planets', mls.UI_GENERIC_PLANETS, [])]
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
             'key': groupName,
             'posttext': ''}
            if activeGroup == groupName:
                data['posttext'] = ' (' + activeLabel + ')'
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
             'posttext': '',
             'sublevel': 1}
            if activeGroup == groupName:
                data['posttext'] = ' (' + activeLabel + ')'
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
                post = ' (' + activeLabel + ')'
            entry.posttext = post
            if entry.panel:
                entry.panel.UpdateLabel()




    def GetLegendGroups(self):
        common = {'groupItems': [],
         'iconMargin': 32,
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1,
         'posttext': ''}
        scrolllist = []
        for (groupName, groupLabel,) in [('star', mls.UI_SHARED_MAPSTARS), ('tile', mls.UI_SHARED_MAP_TILES)]:
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
        data.displayName = uiutil.UpperCase(displayName)
        data.setsliderlabel = self.SetSliderLabel
        data.endsetslidervalue = self.EndSetSliderValue
        data.hint = hint
        data.selectable = False
        scrolllist.append(listentry.Get('Slider', data=data))



    def SetSliderLabel(self, label, idname, dname, value):
        label.text = '%s %d' % (dname, int(value))



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
        viewingStarmap = sm.GetService('map').ViewingStarMap()
        if viewingStarmap:
            if key == 'mapautoframe':
                starmapSvc.SetInterest()
            elif key == 'mapautozoom':
                starmapSvc.SetInterest()
            elif key == 'mapcolorby':
                starmapSvc.UpdateLines(updateColor=1)
            elif key == 'showlines':
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
        uicls.Label(text=header, parent=where, align=uiconst.TOTOP, height=12, autowidth=False, autoheight=False, state=uiconst.UI_NORMAL)



    def OnSelectionChange(self, selected):
        dataList = []
        colorList = []
        for node in selected:
            if node.key == 'tile':
                if node.legend.data is not None:
                    dataList.append(node.legend.data)
                else:
                    colorList.append(node.legend.color)

        if sm.GetService('map').ViewingStarMap():
            sm.GetService('starmap').HighlightTiles(dataList, colorList)




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
        eye = uicls.Icon(icon='ui_38_16_110', pos=pos, name='eye', hint=mls.UI_GENERIC_SHOW, **props)
        eye.OnClick = self.ToggleVisibility
        self.sr.eyeoff = uicls.Icon(icon='ui_38_16_111', pos=pos, **props)
        hint = uicls.Icon(icon='ui_38_16_109', name='hint', hint=mls.UI_GENERIC_SHOWHINT, **props)
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




