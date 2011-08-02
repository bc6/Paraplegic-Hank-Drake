import service
import blue
import uthread
import uix
import uiutil
import form
import util
import listentry
import sys
import uicls
import uiconst

class AssetsSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'SetHint': []}
    __guid__ = 'svc.assets'
    __notifyevents__ = ['ProcessSessionChange', 'OnItemChange', 'OnPostCfgDataChanged']
    __servicename__ = 'assets'
    __displayname__ = 'Assets Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Assets')
        self.locationCache = {}



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.SelfDestruct()



    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
        else:
            wnd = self.GetWnd()
            if wnd and not wnd.destroyed:
                uthread.new(wnd.Refresh)



    def OnItemChange(self, item, change):
        itemLocationIDs = [item.locationID]
        if const.ixLocationID in change:
            itemLocationIDs.append(change[const.ixLocationID])
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            if change.keys() == [const.ixLocationID] and change.values() == [0]:
                return 
            if util.IsStation(item.locationID) or const.ixLocationID in change and util.IsStation(change[const.ixLocationID]):
                key = wnd.sr.maintabs.GetSelectedArgs()
                if key is not None:
                    if key[:7] == 'station':
                        if eve.session.stationid in itemLocationIDs:
                            wnd.sr.maintabs.ReloadVisible()
                    elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
                        uthread.new(wnd.UpdateLite, item.locationID, key, change.get(const.ixLocationID, item.locationID))



    def Show(self, stationID = None):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            wnd.Refresh()
            if stationID is not None:
                wnd.sr.maintabs.ShowPanelByName(mls.UI_SHARED_ALLITEMS)
                blue.pyos.synchro.Yield()
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ == 'listentry.Group':
                        if entry.id == ('assetslocations_allitems', stationID):
                            uicore.registry.SetListGroupOpenState(('assetslocations_allitems', stationID), 1)
                            wnd.sr.scroll.PrepareSubContent(entry)
                            wnd.sr.scroll.ShowNodeIdx(entry.idx)




    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed and wnd.key and wnd.key[:7] == 'station':
                wnd.sr.maintabs.ReloadVisible()



    def GetAll(self, key, blueprintOnly = 0, isCorp = 0, keyID = None, sortKey = 0):
        stations = self.GetStations(blueprintOnly, isCorp)
        sortlocations = []
        mapSvc = sm.StartService('map')
        uiSvc = sm.StartService('ui')
        for station in stations:
            blue.pyos.BeNice()
            solarsystemID = uiSvc.GetStation(station.stationID).solarSystemID
            loc = self.locationCache.get(solarsystemID, None)
            if loc is None:
                constellationID = mapSvc.GetParent(solarsystemID)
                loc = self.locationCache.get(constellationID, None)
                if loc is None:
                    regionID = mapSvc.GetParent(constellationID)
                    loc = (solarsystemID, constellationID, regionID)
                else:
                    regionID = loc[2]
                self.locationCache[solarsystemID] = loc
                self.locationCache[constellationID] = loc
                self.locationCache[regionID] = loc
            else:
                constellationID = loc[1]
                regionID = loc[2]
            if key == 'allitems':
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'sysitems':
                if solarsystemID == (keyID or eve.session.solarsystemid2):
                    sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'conitems' and constellationID == (keyID or eve.session.constellationid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'regitems' and regionID == (keyID or eve.session.regionid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))

        sortlocations = uiutil.SortListOfTuples(sortlocations)
        return sortlocations



    def GetStations(self, blueprintOnly = 0, isCorp = 0):
        stations = eve.GetInventory(const.containerGlobal).ListStations(blueprintOnly, isCorp)
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        return stations



    def GetWnd(self, new = 0):
        return sm.StartService('window').GetWindow('assets', new, decoClass=form.AssetsWindow)



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.SetHint(hintstr)




class AssetsWindow(uicls.Window):
    __guid__ = 'form.AssetsWindow'
    default_width = 500
    default_height = 400
    default_minSize = (500, 256)

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.key = None
        self.invalidateOpenState_regitems = 1
        self.invalidateOpenState_allitems = 1
        self.invalidateOpenState_conitems = 1
        self.invalidateOpenState_sysitems = 1
        self.searchlist = None
        self.pending = None
        self.loading = 0
        self.SetScope('station_inflight')
        self.SetCaption(mls.UI_CORP_ASSETS)
        self.SetWndIcon('ui_7_64_13', mainTop=-8, size=128)
        self.SetMainIconSize(64)
        self.sr.topParent.state = uiconst.UI_DISABLED
        uicls.WndCaptionLabel(text=mls.UI_GENERIC_PERSONALASSETS, subcaption=mls.UI_CORP_DELAYED5MINUTES, parent=self.sr.topParent, align=uiconst.RELATIVE)



    def Reload(self, *args):
        self.sr.maintabs.ReloadVisible()



    def Refresh(self, *args):
        self.station_inited = 0
        self.search_inited = 0
        self.filt_inited = 0
        uix.Flush(self.sr.main)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'assets'
        self.sr.scroll.sr.minColumnWidth = {mls.UI_GENERIC_NAME: 44}
        self.sr.scroll.allowFilterColumns = 1
        self.sr.scroll.OnNewHeaders = self.Reload
        self.sr.scroll.sortGroups = True
        self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        tabs = [[mls.UI_SHARED_ALLITEMS,
          self.sr.scroll,
          self,
          'allitems'],
         [mls.UI_GENERIC_REGION,
          self.sr.scroll,
          self,
          'regitems'],
         [mls.UI_GENERIC_CONSTELLATION,
          self.sr.scroll,
          self,
          'conitems'],
         [mls.UI_GENERIC_SOLARSYSTEM,
          self.sr.scroll,
          self,
          'sysitems'],
         [mls.UI_CMD_SEARCH,
          self.sr.scroll,
          self,
          'search']]
        if eve.session.stationid:
            tabs.insert(4, [mls.UI_GENERIC_STATION,
             self.sr.scroll,
             self,
             'station'])
        self.sr.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0, tabs=tabs, groupID='assetspanel', silently=True)



    def Load(self, key, reloadStationID = None):
        if self.loading:
            self.pending = (key, reloadStationID)
            return 
        uthread.new(self._Load, key, reloadStationID)



    def _Load(self, key, reloadStationID = None):
        self.loading = 1
        self.pending = None
        self.key = key
        if key[:7] == 'station':
            if not self.station_inited:
                idx = self.sr.main.children.index(self.sr.maintabs)
                self.sr.station_tabs = uicls.TabGroup(name='tabparent2', parent=self.sr.main, idx=idx + 1)
                tabs = [[mls.UI_GENERIC_SHIPS,
                  self.sr.scroll,
                  self,
                  '%sships' % key],
                 [mls.UI_GENERIC_MODULES,
                  self.sr.scroll,
                  self,
                  '%smodules' % key],
                 [mls.UI_GENERIC_CHARGES,
                  self.sr.scroll,
                  self,
                  '%scharges' % key],
                 [mls.UI_GENERIC_MINERALS,
                  self.sr.scroll,
                  self,
                  '%sminerals' % key],
                 [mls.UI_GENERIC_OTHER,
                  self.sr.scroll,
                  self,
                  '%sother' % key]]
                self.station_inited = 1
                self.sr.station_tabs.Startup(tabs, 'assetsatstation', silently=True)
            if self.sr.Get('filt_cont', None):
                self.sr.filt_cont.state = uiconst.UI_HIDDEN
            self.sr.station_tabs.state = uiconst.UI_NORMAL
            if self.sr.Get('search_cont', None):
                self.sr.search_cont.state = uiconst.UI_HIDDEN
            if key != 'station':
                self.ShowStationItems(key[7:])
            else:
                self.sr.station_tabs.AutoSelect(1)
        elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
            if not getattr(self, 'filt_inited', False):
                self.sr.filt_cont = uicls.Container(align=uiconst.TOTOP, height=67, parent=self.sr.main, top=2, idx=1)
                sortoptions = [(mls.UI_GENERIC_NAME, 0), (mls.UI_GENERIC_NUMJUMPS, 1), (mls.UI_GENERIC_NUMITEMS, 2)]
                self.sr.sortcombo = c = uicls.Combo(label=mls.UI_CMD_SORTBY, parent=self.sr.filt_cont, options=sortoptions, name='sortcombo', select=None, callback=self.Filter, width=100, pos=(5, 16, 0, 0))
                l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
                self.sr.filtcombo = c = uicls.Combo(label=mls.UI_GENERIC_VIEW, parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=100, pos=(l,
                 16,
                 0,
                 0))
                self.sr.filt_cont.height = self.sr.filtcombo.top + self.sr.filtcombo.height
                self.filt_inited = 1
            self.sr.filt_cont.state = uiconst.UI_PICKCHILDREN
            if key in ('regitems', 'conitems', 'sysitems'):
                self.sr.filtcombo.state = uiconst.UI_NORMAL
            else:
                self.sr.filtcombo.state = uiconst.UI_HIDDEN
            if self.sr.Get('station_tabs', None):
                self.sr.station_tabs.state = uiconst.UI_HIDDEN
            if self.sr.Get('search_cont', None):
                self.sr.search_cont.state = uiconst.UI_HIDDEN
            self.ShowAll(key, None, None)
        elif key == 'search':
            if self.sr.Get('station_tabs', None):
                self.sr.station_tabs.state = uiconst.UI_HIDDEN
            if not self.search_inited:
                t = const.defaultPadding + 14
                self.sr.search_cont = uicls.Container(align=uiconst.TOTOP, height=37, parent=self.sr.main, idx=1)
                t = const.defaultPadding + 14
                sortoptions = [(mls.UI_GENERIC_NAME, 0), (mls.UI_GENERIC_NUMJUMPS, 1), (mls.UI_GENERIC_NUMITEMS, 2)]
                last = self.sr.sortcombosearch = c = uicls.Combo(label=mls.UI_CMD_SORTBY, parent=self.sr.search_cont, options=sortoptions, name='sortcombosearch', select=None, callback=self.Search, width=100, pos=(5,
                 t,
                 0,
                 0))
                l = last.left + last.width + const.defaultPadding
                searchoptions = [(mls.UI_GENERIC_ALL, 0),
                 (mls.UI_GENERIC_TYPE, 1),
                 (mls.UI_GENERIC_GROUP, 2),
                 (mls.UI_GENERIC_CATEGORY, 3)]
                last = self.sr.searchwhich = uicls.Combo(label=mls.UI_GENERIC_SEARCHBY, parent=self.sr.search_cont, options=searchoptions, left=l, top=t, name='searchcombo', select=None)
                l = last.left + last.width + const.defaultPadding
                last = self.sr.searchtype = uicls.SinglelineEdit(name='assetssearchtype', parent=self.sr.search_cont, left=l, width=80, top=t, label=mls.UI_GENERIC_STRING, maxLength=100)
                l = last.left + last.width + const.defaultPadding
                last = self.sr.searchquantmin = uicls.SinglelineEdit(name='assetssearchqantmin', parent=self.sr.search_cont, left=l, width=70, ints=(0, 9999999), top=t, label=mls.UI_GENERIC_MINQTY)
                l = last.left + last.width + const.defaultPadding
                last = self.sr.searchquantmax = uicls.SinglelineEdit(name='assetssearchqantmax', parent=self.sr.search_cont, left=l, width=70, ints=(0, 9999999), top=t, label=mls.UI_GENERIC_MAXQTY)
                l = last.left + last.width + const.defaultPadding
                b1 = uicls.Button(parent=self.sr.search_cont, label=mls.UI_CMD_SEARCH, left=l, top=t, func=self.Search)
                self.sr.search_cont.height = self.sr.searchquantmax.top + self.sr.searchquantmax.height
                self.sr.searchtype.OnReturn = self.Search
                self.sr.searchquantmin.OnReturn = self.Search
                self.sr.searchquantmax.OnReturn = self.Search
                self.search_inited = 1
            if self.sr.Get('filt_cont', None):
                self.sr.filt_cont.state = uiconst.UI_HIDDEN
            self.sr.search_cont.state = uiconst.UI_PICKCHILDREN
            sortKeySearch = settings.char.ui.Get('assetsSearchSortKey', None)
            self.ShowSearch(sortKeySearch)
        self.loading = 0
        if self.pending:
            self.Load(*self.pending)



    def Filter(self, *args):
        (key, keyID,) = self.sr.filtcombo.GetValue()
        sortKey = self.sr.sortcombo.GetValue()
        self.ShowAll(key, keyID, sortKey)



    def Search(self, *args):
        self.ShowLoad()
        self.sr.scroll.Load(contentList=[])
        self.SetHint(mls.UI_SHARED_MAPGETTINGDATA)
        blue.pyos.synchro.Sleep(1)
        container = eve.GetInventory(const.containerGlobal)
        allitems = container.List()
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        solarsystems = {}
        self.SetHint(mls.UI_GENERIC_SEARCHING)
        blue.pyos.synchro.Sleep(1)
        searchtype = unicode(self.sr.searchtype.GetValue() or '').lower()
        searchquantmin = int(self.sr.searchquantmin.GetValue() or 0)
        searchquantmax = int(self.sr.searchquantmax.GetValue() or 0)
        searchwhich = int(self.sr.searchwhich.GetValue() or 0)
        stations = {}
        for each in allitems:
            stationID = each.locationID
            if util.IsJunkLocation(stationID) or stationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            if len(searchtype):
                found = False
                t = cfg.invtypes.Get(each.typeID)
                if searchwhich in (0, 1):
                    if t.name.lower().find(searchtype) > -1:
                        found = True
                if not found:
                    g = cfg.invgroups.Get(t.groupID)
                    if searchwhich in (0, 2):
                        if g.name.lower().find(searchtype) > -1:
                            found = True
                    if not found and searchwhich in (0, 3):
                        c = cfg.invcategories.Get(g.categoryID)
                        if c.name.lower().find(searchtype) > -1:
                            found = True
                if not found:
                    continue
            if each.stacksize < searchquantmin:
                continue
            if searchquantmax > 0 and each.stacksize > searchquantmax:
                continue
            if stationID not in stations:
                stations[stationID] = []
            stations[stationID].append(each)

        sortlocations = []
        for stationID in stations:
            solarsystemID = sm.StartService('ui').GetStation(stationID).solarSystemID
            sortlocations.append((solarsystemID, stationID, stations[stationID]))

        sortlocations.sort()
        sortlocations = sortlocations
        self.searchlist = sortlocations
        sortKey = self.sr.sortcombosearch.GetValue()
        self.ShowSearch(sortKey)



    def ShowAll(self, key, keyID, sortKey, *args):
        if keyID is None:
            keyID = settings.char.ui.Get('assetsKeyID_%s' % key, None)
        if sortKey is None:
            sortKey = settings.char.ui.Get('assetsSortKey', None)
        settings.char.ui.Set('assetsKeyID_%s' % key, keyID)
        settings.char.ui.Set('assetsSortKey', sortKey)
        self.ShowLoad()
        self.SetHint()
        closed = [0, 1][getattr(self, 'invalidateOpenState_%s' % key, 0)]
        sortlocations = sm.StartService('assets').GetAll(key, keyID=keyID, sortKey=sortKey)
        options = [(mls.UI_GENERIC_CURRENT, (key, 0))]
        opts = {}
        for r in sm.StartService('assets').locationCache.iterkeys():
            if key == 'regitems' and util.IsRegion(r) or key == 'conitems' and util.IsConstellation(r) or key == 'sysitems' and util.IsSolarSystem(r):
                opts[cfg.evelocations.Get(r).name] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, (key, opts[k])))

        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if keyID:
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(keyID).name)
            if sortKey:
                self.sr.sortcombo.SelectItemByIndex(sortKey)
        except (Exception,) as e:
            sys.exc_clear()
        scrolllist = []
        for (solarsystemID, station,) in sortlocations:
            scrolllist.append(listentry.Get('Group', self.GetLocationData(solarsystemID, station, key, forceClosed=closed, scrollID=self.sr.scroll.sr.id, sortKey=sortKey)))

        if self.destroyed:
            return 
        setattr(self, 'invalidateOpenState_%s' % key, 0)
        k = {'allitems': 0,
         'regitems': 1,
         'conitems': 2,
         'sysitems': 3}
        noContent = mls.UI_SHARED_NOITEMSAT % {'where': [mls.UI_SHARED_ATSTATION,
                   mls.UI_SHARED_INREGION,
                   mls.UI_SHARED_INCONSTELLATION,
                   mls.UI_SHARED_INSOLARSYSTEM][k[key]]}
        self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=noContent)
        self.HideLoad()



    def ShowStationItems(self, key):
        self.ShowLoad()
        hangarInv = eve.GetInventory(const.containerHangar)
        items = hangarInv.List()
        if not len(items):
            self.SetHint(mls.UI_SHARED_NOASSETS)
            return 
        assets = []
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], headers=uix.GetInvItemDefaultHeaders())
        itemname = ' ' + key
        for each in items:
            if each.flagID not in (const.flagHangar, const.flagWallet):
                continue
            if key == 'ships':
                if each.categoryID != const.categoryShip:
                    continue
            elif key == 'modules':
                if not cfg.invtypes.Get(each.typeID).Group().Category().IsHardware():
                    continue
            elif key == 'minerals':
                if each.groupID != const.groupMineral:
                    continue
            elif key == 'charges':
                if each.categoryID != const.categoryCharge:
                    continue
            else:
                itemname = None
                if each.categoryID == const.categoryShip or cfg.invtypes.Get(each.typeID).Group().Category().IsHardware() or each.groupID == const.groupMineral or each.categoryID == const.categoryCharge:
                    continue
            assets.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=self.sr.scroll.sr.id)))

        if not len(assets):
            if not itemname:
                self.SetHint(mls.UI_SHARED_NOITEMSCATATSTATION)
            else:
                self.SetHint(mls.UI_SHARED_NOITEMATSTATION % {'type': getattr(mls, 'UI_GENERIC_' + key.upper())})
        else:
            self.SetHint()
        self.sr.scroll.Load(contentList=assets, sortby='label', headers=uix.GetInvItemDefaultHeaders())
        self.HideLoad()



    def GetLocationData(self, solarsystemID, station, key, expanded = 0, forceClosed = 0, scrollID = None, sortKey = None, fakeItems = None, fakeJumps = None):
        location = cfg.evelocations.Get(station.stationID)
        if forceClosed:
            uicore.registry.SetListGroupOpenState(('assetslocations_%s' % key, location.locationID), 0)
        jumps = fakeJumps or sm.StartService('pathfinder').GetJumpCountFromCurrent(solarsystemID)
        itemCount = fakeItems or station.itemCount
        label = '%s - %s%s' % (location.name, uix.Plural(station.itemCount, 'UI_SHARED_NUM_ITEM') % {'num': itemCount}, ['', ' - %s' % (uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})][(key != 'sysitems')])
        if sortKey == 1:
            sortVal = (jumps, location.name, itemCount)
        elif sortKey == 2:
            sortVal = (itemCount, location.name, jumps)
        else:
            sortVal = (location.name, itemCount, jumps)
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetMenuLocationMenu,
         'label': label,
         'jumps': jumps,
         'itemCount': station.itemCount,
         'groupItems': [],
         'id': ('assetslocations_%s' % key, location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'scrollID': scrollID}
        headers = uix.GetInvItemDefaultHeaders()
        for each in headers:
            data['sort_%s' % each] = sortVal

        return data



    def GetSubContent(self, data, *args):
        if data.key == 'search':
            scrolllist = []
            items = []
            for (solarsystemID, stationID, station,) in self.searchlist:
                if stationID == data.location.locationID:
                    items = station
                    break

            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet):
                    continue
                scrolllist.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=data.scrollID)))

            return scrolllist
        if eve.session.stationid and data.location.locationID == eve.session.stationid:
            hangarInv = eve.GetInventory(const.containerHangar)
            items = hangarInv.List()
            scrolllist = []
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet):
                    continue
                scrolllist.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=data.scrollID)))

            return scrolllist
        items = eve.GetInventory(const.containerGlobal).ListStationItems(data.location.locationID)
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        scrolllist = []
        for each in items:
            if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            data = uix.GetItemData(each, 'details', scrollID=data.scrollID)
            if util.IsStation(each.locationID):
                station = sm.RemoteSvc('stationSvc').GetStation(each.locationID)
                if station:
                    data.factionID = sm.StartService('faction').GetFactionOfSolarSystem(station.solarSystemID)
            scrolllist.append(listentry.Get('InvAssetItem', data=data))

        return scrolllist



    def UpdateLite(self, stationID, key, fromID):
        if not self or self.destroyed:
            return 
        self.ShowLoad()
        station = None
        stations = sm.StartService('assets').GetStations()
        for station in stations:
            if station.stationID == stationID:
                break

        if station:
            solarsystemID = sm.StartService('ui').GetStation(station.stationID).solarSystemID
            pos = self.sr.scroll.GetScrollProportion()
            searchKey = set()
            searchKey.add(('assetslocations_%s' % key, stationID))
            if fromID:
                searchKey.add(('assetslocations_%s' % key, fromID))
            for node in self.sr.scroll.GetNodes():
                if node.Get('id', None) in searchKey:
                    node.data = self.GetLocationData(solarsystemID, station, key, scrollID=self.sr.scroll.sr.id)
                    if node.panel:
                        node.panel.Load(node)
                    self.sr.scroll.PrepareSubContent(node)
                    self.sr.scroll.ScrollToProportion(pos)

        self.Refresh()
        self.HideLoad()



    def ShowSearch(self, sortKey = None, *args):
        if sortKey is None:
            sortKey = settings.char.ui.Get('assetsSearchSortKey', None)
        settings.char.ui.Set('assetsSearchSortKey', sortKey)
        if sortKey:
            self.sr.sortcombosearch.SelectItemByIndex(sortKey)
        self.SetHint()
        scrolllist = []
        searchlist = getattr(self, 'searchlist', []) or []
        sortedList = []
        for (solarsystemID, stationID, items,) in searchlist:
            station = util.KeyVal()
            station.stationID = stationID
            station.solarsystemID = solarsystemID
            station.stationName = cfg.evelocations.Get(stationID).name
            station.itemCount = len(items)
            sortedList.append(station)

        for station in sortedList:
            scrolllist.append(listentry.Get('Group', self.GetLocationData(station.solarsystemID, station, 'search', scrollID=self.sr.scroll.sr.id, sortKey=sortKey)))

        self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=mls.UI_GENERIC_NOTHINGFOUND)
        self.HideLoad()



    def GetMenuLocationMenu(self, node):
        stationInfo = sm.StartService('ui').GetStation(node.location.locationID)
        return sm.StartService('menu').CelestialMenu(node.location.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def OnGroupDeleted(self, ids):
        pass



    def OnGroupDragEnter(self, group, drag):
        pass




