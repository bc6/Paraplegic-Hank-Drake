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
import localization
import re

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
            wnd.Close()



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
            if stationID is not None:
                wnd.sr.maintabs.ShowPanelByName(localization.GetByLabel('UI/Inventory/Inventory/AssetsWindow/AllItems'))
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
        stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations(blueprintOnly, isCorp)
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        return stations



    def GetWnd(self, new = 0):
        if new:
            return form.AssetsWindow.Open()
        return form.AssetsWindow.GetIfOpen()



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.SetHint(hintstr)




class AssetsWindow(uicls.Window):
    __guid__ = 'form.AssetsWindow'
    default_width = 395
    default_height = 400
    default_minSize = (395, 256)
    default_windowID = 'assets'

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
        self.SetCaption(localization.GetByLabel('UI/Inventory/AssetsWindow/Assets'))
        self.SetWndIcon('ui_7_64_13', mainTop=-8, size=128)
        self.SetMainIconSize(64)
        self.sr.topParent.state = uiconst.UI_DISABLED
        self.sortOptions = [(localization.GetByLabel('UI/Common/Name'), 0), (localization.GetByLabel('UI/Common/NumberOfJumps'), 1), (localization.GetByLabel('UI/Common/NumberOfItems'), 2)]
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Inventory/AssetsWindow/PersonalAssets'), subcaption=localization.GetByLabel('UI/Inventory/AssetsWindow/DelayedFiveMinutes'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.searchRegex = re.compile('\n                (?:\\s*)                         # \n                (?P<name>\\w*)                   # the argument name\n                [:]\\s*                          #\n                (?:\\"                           # match group for for quoted strings, skipped\n                    (?:                         # match group for the closing quote, skipped\n                        (?P<value>.*?)          # contents of a qouted string\n                            (?<!\\\\)             # ignoring a trailing escape \n                    \\") |                       # end of match group OR\n                    (?P<value2>[\\w\\d\\.\\,+-]*)   # value of a key:value pair for non-quoted instances, allows values used for numbers and negatives\n                )', re.UNICODE + re.IGNORECASE + re.VERBOSE)
        self.Refresh()



    def ReloadTabs(self, *args):
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
        self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
        self.sr.scroll.allowFilterColumns = 1
        self.sr.scroll.OnNewHeaders = self.ReloadTabs
        self.sr.scroll.sortGroups = True
        self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        tabs = [[localization.GetByLabel('UI/Inventory/AssetsWindow/AllItems'),
          self.sr.scroll,
          self,
          'allitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/Region'),
          self.sr.scroll,
          self,
          'regitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/Constellation'),
          self.sr.scroll,
          self,
          'conitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
          self.sr.scroll,
          self,
          'sysitems'],
         [localization.GetByLabel('UI/Common/Buttons/Search'),
          self.sr.scroll,
          self,
          'search']]
        if eve.session.stationid:
            tabs.insert(4, [localization.GetByLabel('UI/Common/LocationTypes/Station'),
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
                tabs = [[localization.GetByLabel('UI/Common/ItemTypes/Ships'),
                  self.sr.scroll,
                  self,
                  '%sships' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Modules'),
                  self.sr.scroll,
                  self,
                  '%smodules' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Charges'),
                  self.sr.scroll,
                  self,
                  '%scharges' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Minerals'),
                  self.sr.scroll,
                  self,
                  '%sminerals' % key],
                 [localization.GetByLabel('UI/Common/Other'),
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
                self.sr.sortcombo = c = uicls.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.filt_cont, options=self.sortOptions, name='sortcombo', select=None, callback=self.Filter, width=100, pos=(5, 16, 0, 0))
                l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
                self.sr.filtcombo = c = uicls.Combo(label=localization.GetByLabel('UI/Common/View'), parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=100, pos=(l,
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
                self.sr.search_cont = uicls.Container(align=uiconst.TOTOP, height=37, parent=self.sr.main, idx=1)
                top = const.defaultPadding + 14
                self.sr.sortcombosearch = uicls.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.search_cont, options=self.sortOptions, name='sortcombosearch', select=None, callback=self.Search, width=100, pos=(const.defaultPadding,
                 top,
                 0,
                 0))
                left = self.sr.sortcombosearch.left + self.sr.sortcombosearch.width + const.defaultPadding
                self.sr.searchtype = uicls.SinglelineEdit(name='assetssearchtype', parent=self.sr.search_cont, left=left, width=200, top=top, label=localization.GetByLabel('UI/Common/SearchText'), maxLength=100)
                left = self.sr.searchtype.left + self.sr.searchtype.width + const.defaultPadding
                button = uicls.Button(parent=self.sr.search_cont, label=localization.GetByLabel('UI/Common/Buttons/Search'), left=left, top=top, func=self.Search)
                self.sr.searchtype.OnReturn = self.Search
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



    def ParseString(self, text):
        advancedMatches = self.searchRegex.findall(text)
        if advancedMatches:
            text = text.split(advancedMatches[0][0] + ':', 1)[0]
        return (text.strip(), advancedMatches)



    def GetConditions(self, advancedMatches):
        uiSvc = sm.StartService('ui')
        conditions = []
        for (word, quoted, value,) in advancedMatches:
            value = quoted or value
            try:
                if 'type'.startswith(word):
                    typeName = value

                    def CheckType(item):
                        t = cfg.invtypes.Get(item.typeID)
                        return t.name.lower().find(typeName) > -1


                    conditions.append(CheckType)
                elif 'group'.startswith(word):
                    groupName = value

                    def CheckGroup(item):
                        g = cfg.invgroups.Get(item.groupID)
                        return g.name.lower().find(groupName) > -1


                    conditions.append(CheckGroup)
                elif 'category'.startswith(word):
                    categoryName = value

                    def CheckCategory(item):
                        c = cfg.invcategories.Get(item.categoryID)
                        return c.name.lower().find(categoryName) > -1


                    conditions.append(CheckCategory)
                elif 'minimum'.startswith(word):
                    quantity = int(value)

                    def CheckMinQuantity(item):
                        return item.stacksize >= quantity


                    conditions.append(CheckMinQuantity)
                elif 'maximum'.startswith(word):
                    quantity = int(value)

                    def CheckMaxQuantity(item):
                        return item.stacksize <= quantity


                    conditions.append(CheckMaxQuantity)
                elif 'metalevel'.startswith(word):
                    level = int(value)

                    def CheckMetaLevel(item):
                        metaLevel = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaLevel, 0))
                        return level == metaLevel


                    conditions.append(CheckMetaLevel)
                elif 'metagroup'.startswith(word):
                    groupName = value

                    def CheckMetaGroup(item):
                        metaGroupID = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMetaGroupID, 0))
                        if metaGroupID > 0:
                            metaGroup = cfg.invmetagroups.Get(metaGroupID)
                            return groupName in metaGroup.name.lower()
                        return False


                    conditions.append(CheckMetaGroup)
                elif 'techlevel'.startswith(word):
                    level = int(value)

                    def CheckTechLevel(item):
                        techLevel = int(sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeTechLevel, 1))
                        return level == techLevel


                    conditions.append(CheckTechLevel)
                elif 'minsecurity'.startswith(word):
                    secLevel = float(value)

                    def CheckMinSecurity(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
                        return systemSec >= secLevel


                    conditions.append(CheckMinSecurity)
                elif 'maxsecurity'.startswith(word):
                    secLevel = float(value)

                    def CheckMaxSecurity(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        systemSec = sm.GetService('map').GetSecurityStatus(solarSystemID)
                        return systemSec <= secLevel


                    conditions.append(CheckMaxSecurity)
                elif 'security'.startswith(word):
                    if 'high'.startswith(value):
                        secClass = [const.securityClassHighSec]
                    elif 'low'.startswith(value):
                        secClass = [const.securityClassLowSec]
                    elif 'null'.startswith(value) or 'zero'.startswith(value):
                        secClass = [const.securityClassZeroSec]
                    elif 'empire'.startswith(value):
                        secClass = [const.securityClassHighSec, const.securityClassLowSec]
                    else:
                        continue

                    def CheckSecurityClass(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        systemSecClass = sm.GetService('map').GetSecurityClass(solarSystemID)
                        return systemSecClass in secClass


                    conditions.append(CheckSecurityClass)
                elif 'system'.startswith(word):
                    name = value

                    def CheckSolarSystem(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        item = sm.GetService('map').GetItem(solarSystemID)
                        return name in item.itemName.lower()


                    conditions.append(CheckSolarSystem)
                elif 'constellation'.startswith(word):
                    name = value

                    def CheckConstellation(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        mapSvc = sm.GetService('map')
                        constellationID = mapSvc.GetConstellationForSolarSystem(solarSystemID)
                        item = mapSvc.GetItem(constellationID)
                        return name in item.itemName.lower()


                    conditions.append(CheckConstellation)
                elif 'region'.startswith(word):
                    name = value

                    def CheckRegion(item):
                        solarSystemID = uiSvc.GetStation(item.locationID).solarSystemID
                        mapSvc = sm.GetService('map')
                        regionID = mapSvc.GetRegionForSolarSystem(solarSystemID)
                        item = mapSvc.GetItem(regionID)
                        return name in item.itemName.lower()


                    conditions.append(CheckRegion)
                elif 'station'.startswith(word):
                    name = value

                    def CheckStation(item):
                        stationName = cfg.evelocations.Get(item.locationID).locationName.lower()
                        return name in stationName


                    conditions.append(CheckStation)
                elif 'blueprint'.startswith(word):
                    if 'copy'.startswith(value):
                        isBpo = False
                    elif 'original'.startswith(value):
                        isBpo = True
                    else:
                        continue

                    def CheckBlueprintType(item):
                        if item.categoryID == const.categoryBlueprint:
                            if isBpo:
                                return item.singleton != const.singletonBlueprintCopy
                            else:
                                return item.singleton == const.singletonBlueprintCopy
                        return False


                    conditions.append(CheckBlueprintType)
            except:
                sm.GetService('assets').LogInfo('Failed parsing keyword', word, 'value', value, 'and happily ignoring it')

        return conditions



    def Search(self, *args):
        self.ShowLoad()
        self.sr.scroll.Load(contentList=[])
        self.SetHint(localization.GetByLabel('UI/Common/GettingData'))
        blue.pyos.synchro.Yield()
        container = sm.GetService('invCache').GetInventory(const.containerGlobal)
        allitems = container.List()
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        uiSvc = sm.StartService('ui')
        solarsystems = {}
        self.SetHint(localization.GetByLabel('UI/Common/Searching'))
        blue.pyos.synchro.Yield()
        searchtype = unicode(self.sr.searchtype.GetValue() or '').lower()
        (searchtype, advancedMatches,) = self.ParseString(searchtype)
        conditions = self.GetConditions(advancedMatches)
        stations = {}
        for item in allitems:
            stationID = item.locationID
            if util.IsJunkLocation(stationID) or stationID in badLocations:
                continue
            if item.stacksize == 0:
                continue
            if len(searchtype):
                if cfg.invtypes.Get(item.typeID).name.lower().find(searchtype) > -1:
                    pass
                elif cfg.invgroups.Get(item.groupID).name.lower().find(searchtype) > -1:
                    pass
                elif cfg.invcategories.Get(item.categoryID).name.lower().find(searchtype) > -1:
                    pass
                else:
                    continue
            if not all((condition(item) for condition in conditions)):
                continue
            if stationID not in stations:
                stations[stationID] = []
            stations[stationID].append(item)

        sortlocations = []
        for stationID in stations:
            solarsystemID = uiSvc.GetStation(stationID).solarSystemID
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
        options = [(localization.GetByLabel('UI/Common/Current'), (key, 0))]
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
        locText = {'allitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsAtStation'),
         'regitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInRegion'),
         'conitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInConstellation'),
         'sysitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInSolarSystem')}
        self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=locText[key])
        self.HideLoad()



    def ShowStationItems(self, key):
        self.ShowLoad()
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List()
        if not len(items):
            self.SetHint(localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssets'))
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

        locText = {'ships': localization.GetByLabel('UI/Inventory/AssetsWindow/NoShipsAtStation'),
         'modules': localization.GetByLabel('UI/Inventory/AssetsWindow/NoModulesAtStation'),
         'minerals': localization.GetByLabel('UI/Inventory/AssetsWindow/NoMineralsAtStation'),
         'charges': localization.GetByLabel('UI/Inventory/AssetsWindow/NoChargesAtStation')}
        if not len(assets):
            if not itemname:
                self.SetHint(localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInCategoryAtStation'))
            else:
                self.SetHint(locText[key])
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
        if key is not 'sysitems':
            label = localization.GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabel', location=location.locationID, itemCount=itemCount, jumps=jumps)
        else:
            label = localization.GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabelNoJump', location=location.locationID, itemCount=itemCount)
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
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            items = hangarInv.List()
            scrolllist = []
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet):
                    continue
                scrolllist.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=data.scrollID)))

            return scrolllist
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(data.location.locationID)
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

        self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Common/NothingFound'))
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




