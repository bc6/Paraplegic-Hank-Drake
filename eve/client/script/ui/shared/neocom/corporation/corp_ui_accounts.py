import blue
import uthread
import util
import uix
import form
import listentry
import log
import uiconst
import uicls
import sys
from contractutils import DoParseItemType

class CorpAccounts(uicls.Container):
    __guid__ = 'form.CorpAccounts'
    __nonpersistvars__ = ['assets']
    __notifyevents__ = ['OnCorpAssetChange']

    def init(self):
        self.sr.journalFromDate = blue.os.GetTime() - 24 * HOUR * 7 + HOUR
        self.sr.journalToDate = blue.os.GetTime() + HOUR
        self.sr.viewMode = 'details'
        self.key = None
        self.sr.search_inited = 0
        sm.RegisterNotify(self)



    def OnCorpAssetChange(self, items, stationID):
        if items[0].locationID != stationID:
            id = ('corpofficeassets', (stationID, items[0].flagID))
            which = 'deliveries'
        else:
            id = ('corpassets', stationID)
            which = 'offices'
        if not self.sr.Get('inited', 0):
            return 
        for node in self.sr.scroll.GetNodes():
            if node.Get('id', 0) == id:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
                for row in rows:
                    if stationID == row.locationID:
                        node.data = self.GetLocationData(row, 71, scrollID=self.sr.scroll.sr.id)

                if node.panel:
                    node.panel.Load(node)
                self.sr.scroll.PrepareSubContent(node)
                pos = self.sr.scroll.GetScrollProportion()
                self.sr.scroll.ScrollToProportion(pos)




    def Load(self, key):
        toparea = sm.GetService('corpui').LoadTop('ui_7_64_13', mls.UI_CORP_CORPASSETS, mls.UI_CORP_DELAYED5MINUTES)
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.scroll = uicls.Scroll(parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'CorporationAssets'
            self.sr.scroll.sr.minColumnWidth = {mls.UI_GENERIC_NAME: 44}
            self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
            self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup([[mls.UI_CORP_OFFICES,
              self.sr.scroll,
              self,
              'offices'],
             [mls.UI_CORP_IMPOUNDED,
              self.sr.scroll,
              self,
              'impounded'],
             [mls.UI_CORP_INSPACE,
              self.sr.scroll,
              self,
              'property'],
             [mls.UI_CORP_DELIVERIES,
              self.sr.scroll,
              self,
              'deliveries'],
             [mls.UI_CORP_LOCKDOWN,
              self.sr.scroll,
              self,
              'lockdown'],
             [mls.UI_CMD_SEARCH,
              self.sr.scroll,
              self,
              'search']], 'corpassetstab', autoselecttab=0)
        self.sr.scroll.Load(contentList=[], headers=uix.GetInvItemDefaultHeaders())
        self.sr.scroll.OnNewHeaders = self.OnNewHeadersSet
        self.sr.scroll.allowFilterColumns = 0
        if self.sr.Get('search_cont', None):
            self.sr.search_cont.state = uiconst.UI_HIDDEN
        if key == 'accounts':
            key = 'offices'
            self.sr.tabs.AutoSelect()
            return 
        if key != 'search':
            if not getattr(self, 'filt_inited', False):
                sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
                self.sr.filt_cont = uicls.Container(align=uiconst.TOTOP, height=37, parent=self, top=2, idx=1)
                sortoptions = [(mls.UI_GENERIC_NAME, 0), (mls.UI_GENERIC_NUMJUMPS, 1)]
                self.sr.sortcombo = uicls.Combo(label=mls.UI_CMD_SORTBY, parent=self.sr.filt_cont, options=sortoptions, name='sortcombo', select=sortKey, callback=self.Filter, width=100, pos=(5, 16, 0, 0))
                l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
                self.sr.filtcombo = uicls.Combo(label=mls.UI_GENERIC_VIEW, parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=100, pos=(l,
                 16,
                 0,
                 0))
                self.sr.filt_cont.height = self.sr.filtcombo.top + self.sr.filtcombo.height
                self.filt_inited = 1
            self.sr.filt_cont.state = uiconst.UI_PICKCHILDREN
        elif self.sr.Get('filt_cont', None):
            self.sr.filt_cont.state = uiconst.UI_HIDDEN
        if key in 'lockdown':
            uthread.new(self.ShowLockdown, None, None)
        elif key == 'search':
            self.sr.scroll.OnNewHeaders = self.Search
            uthread.new(self.ShowSearch)
        else:
            uthread.new(self.ShowAssets, key, None, None)



    def Filter(self, *args):
        (flagName, regionKey,) = self.sr.filtcombo.GetValue()
        sortKey = self.sr.sortcombo.GetValue()
        if flagName == 'lockdown':
            self.ShowLockdown(sortKey, regionKey)
        else:
            self.ShowAssets(flagName, sortKey, regionKey)



    def OnNewHeadersSet(self, *args):
        self.sr.tabs.ReloadVisible()



    def ShowAssets(self, flagName, sortKey, regionKey):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return 
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_%s' % flagName, None)
        settings.char.ui.Set('corpAssetsKeyID_%s' % flagName, regionKey)
        flag = {'offices': 71,
         'impounded': 72,
         'property': 74,
         'deliveries': 75}[flagName]
        which = {71: 'offices',
         72: 'junk',
         74: 'property',
         75: 'deliveries'}[flag]
        rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
        options = self.GetFilterOptions(rows, flagName)
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(regionKey).name)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(a.label, b.label)


        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(mls.UI_CORP_ACCESSDENIED6)
            sm.GetService('corpui').HideLoad()
            return 
        self.sr.scroll.allowFilterColumns = 1
        data = []
        scrolllist = []
        for row in rows:
            data.append(self.GetLocationData(row, flag, scrollID=self.sr.scroll.sr.id))

        data.sort(lambda x, y: cmp(x['label'], y['label']))
        for row in data:
            if regionKey == 1:
                scrolllist.append(listentry.Get('Group', row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(listentry.Get('Group', row))
            elif row['regionID'] == regionKey:
                scrolllist.append(listentry.Get('Group', row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=mls.UI_CORP_NOITEMSFOUND)
        sm.GetService('corpui').HideLoad()



    def GetFilterOptions(self, rows, flagName):
        filterOptions = self.GetRegions(rows, flagName)
        options = [(mls.UI_GENERIC_CURRENTREGION, (flagName, 0)), (mls.UI_CONTRACTS_ALLREGIONS, (flagName, 1))]
        opts = {}
        for r in filterOptions:
            if util.IsRegion(r):
                opts[cfg.evelocations.Get(r).name] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, (flagName, opts[k])))

        return options



    def GetRegions(self, rows, flagName):
        mapSvc = sm.GetService('map')
        regionIDs = []
        for row in rows:
            if flagName == 'lockdown':
                locationID = row
            else:
                locationID = row.locationID
            try:
                solarSystemID = sm.GetService('ui').GetStation(locationID).solarSystemID
            except:
                solarSystemID = locationID
            try:
                constellationID = mapSvc.GetParent(solarSystemID)
                regionID = mapSvc.GetParent(constellationID)
                regionIDs.append(regionID)
            except:
                log.LogException()

        return regionIDs



    def GetLocationData(self, row, flag, scrollID = None):
        jumps = -1
        try:
            solarSystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
        except:
            solarSystemID = row.locationID
        try:
            mapSvc = sm.GetService('map')
            jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
            locationName = cfg.evelocations.Get(row.locationID).locationName
            constellationID = mapSvc.GetParent(solarSystemID)
            regionID = mapSvc.GetParent(constellationID)
            label = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
        except:
            log.LogException()
            label = '%s' % locationName
        data = {'GetSubContent': self.GetSubContent,
         'label': label,
         'jumps': jumps,
         'groupItems': None,
         'flag': flag,
         'id': ('corpassets', row.locationID),
         'tabs': [],
         'state': 'locked',
         'locationID': row.locationID,
         'showicon': 'hide',
         'MenuFunction': self.GetLocationMenu,
         'regionID': regionID,
         'scrollID': scrollID}
        return data



    def GetLocationMenu(self, node):
        if util.IsStation(node.locationID):
            stationInfo = sm.GetService('ui').GetStation(node.locationID)
            menu = sm.GetService('menu').CelestialMenu(node.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)
            if node.flag == 72:
                checkIsDirector = const.corpRoleDirector == eve.session.corprole & const.corpRoleDirector
                if checkIsDirector:
                    menu.append((mls.UI_CMD_TRASHITEMSATLOCATION, self.TrashJunkAtLocation, (node.locationID,)))
            return menu
        if util.IsSolarSystem(node.locationID):
            return sm.GetService('menu').CelestialMenu(node.locationID)
        return []



    def TrashJunkAtLocation(self, locationID):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, locationID, 'junk')
        sm.GetService('menu').TrashInvItems(items)



    def GetSubContent(self, nodedata, *args):
        which = {71: 'offices',
         72: 'junk',
         74: 'property',
         75: 'deliveries'}[nodedata.flag]
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, which)
        scrolllist = []
        if len(items) == 0:
            label = mls.UI_GENERIC_NOITEM
            if nodedata.flag == 71:
                label = mls.UI_CORP_UNUSED_CORP_OFFICE
            return [listentry.Get('Generic', {'label': label,
              'sublevel': nodedata.Get('sublevel', 0) + 1})]
        items.header.virtual = items.header.virtual + [('groupID', lambda row: cfg.invtypes.Get(row.typeID).groupID), ('categoryID', lambda row: cfg.invtypes.Get(row.typeID).categoryID)]
        searchCondition = nodedata.Get('searchCondition', None)
        if which == 'offices' and searchCondition is None:
            divisionNames = sm.GetService('corp').GetDivisionNames()
            divisionIdFromHangarFlag = {const.flagHangar: 1,
             const.flagCorpSAG2: 2,
             const.flagCorpSAG3: 3,
             const.flagCorpSAG4: 4,
             const.flagCorpSAG5: 5,
             const.flagCorpSAG6: 6,
             const.flagCorpSAG7: 7}
            for (flag, divisionNumber,) in divisionIdFromHangarFlag.iteritems():
                label = '    ' + divisionNames[divisionNumber]
                data = {'GetSubContent': self.GetSubContentDivision,
                 'label': label,
                 'groupItems': None,
                 'flag': flag,
                 'id': ('corpofficeassets', (nodedata.locationID, flag)),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': nodedata.locationID,
                 'showicon': 'hide',
                 'sublevel': nodedata.Get('sublevel', 0) + 1,
                 'viewMode': self.sr.viewMode,
                 'scrollID': nodedata.scrollID}
                scrolllist.append(listentry.Get('Group', data))
                uicore.registry.SetListGroupOpenState(('corpofficeassets', (nodedata.locationID, flag)), 0)

        elif nodedata.flag in (71, 72):
            sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
        for each in items:
            if searchCondition is not None:
                if searchCondition.typeID is not None and searchCondition.typeID != each.typeID or searchCondition.groupID is not None and searchCondition.groupID != each.groupID or searchCondition.categoryID is not None and searchCondition.categoryID != each.categoryID or searchCondition.qty > each.stacksize:
                    continue
            data = uix.GetItemData(each, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.id = each.itemID
            data.remote = True
            if nodedata.flag in (71, 72) and each.categoryID == const.categoryBlueprint:
                data.locked = sm.GetService('corp').IsItemLocked(each)
            scrolllist.append(listentry.Get('InvItem', data=data))

        return scrolllist



    def GetSubContentDivision(self, nodedata, *args):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, 'offices')
        scrolllist = []
        if len(items) == 0:
            label = mls.UI_CORP_UNUSED_CORP_OFFICE
            data = util.KeyVal()
            data.label = label
            data.sublevel = nodedata.Get('sublevel', 1) + 1
            data.id = nodedata.flag
            return [listentry.Get('Generic', data=data)]
        items.header.virtual = items.header.virtual + [('groupID', lambda row: cfg.invtypes.Get(row.typeID).groupID), ('categoryID', lambda row: cfg.invtypes.Get(row.typeID).categoryID)]
        sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
        for each in items:
            if each.flagID != nodedata.flag:
                continue
            data = uix.GetItemData(each, nodedata.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.id = each.itemID
            data.remote = True
            data.sublevel = nodedata.Get('sublevel', 1) + 1
            if each.categoryID == const.categoryBlueprint:
                data.locked = sm.GetService('corp').IsItemLocked(each)
            data.label = '%s<t>%s<t>%s' % (cfg.invtypes.Get(each.typeID).name, each.stacksize, cfg.invgroups.Get(each.groupID).name)
            scrolllist.append(listentry.Get('InvItemWithVolume', data=data))

        return scrolllist



    def OnGetEmptyMenu(self, *args):
        return []



    def ShowJournal(self, *args):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return 
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(mls.UI_CORP_ACCESSDENIED6)
            self.sr.scroll.Clear()
            sm.GetService('corpui').HideLoad()
            return 
        keymap = sm.GetService('account').GetKeyMap()
        scrolllist = []
        for row in keymap:
            keyName = '%s (%s - %s)' % (row.keyName.capitalize(), util.FmtDate(self.sr.journalFromDate, 'ls'), util.FmtDate(self.sr.journalToDate, 'ls'))
            data = {'GetSubContent': self.GetJournalSubContent,
             'label': keyName,
             'groupItems': None,
             'id': ('corpaccounts', row.keyName),
             'tabs': [],
             'state': 'locked',
             'accountKey': row.keyID,
             'showicon': 'hide',
             'fromDate': self.sr.journalFromDate}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
         mls.UI_GENERIC_ID,
         mls.UI_GENERIC_AMOUNT,
         mls.UI_GENERIC_DESCRIPTION,
         mls.UI_GENERIC_AMOUNT])
        sm.GetService('corpui').HideLoad()



    def GetJournalSubContent(self, nodedata, *args):
        items = sm.GetService('account').GetJournal(nodedata.keyID, nodedata.fromDate, None, 1)
        scrolllist = []
        for row in items:
            if row.entryTypeID == const.refSkipLog:
                continue
            data = {}
            if row.entryTypeID in (const.refMarketEscrow, const.refTransactionTax, const.refBrokerfee):
                actor = cfg.eveowners.Get(row.ownerID1).name
            else:
                actor = ''
            data['label'] = '%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(row.transactionDate, 'ls'),
             row.transactionID,
             util.FmtCurrency(row.amount, currency=None, showFractionsAlways=0),
             util.FmtRef(row.entryTypeID, row.ownerID1, row.ownerID2, row.referenceID, amount=row.amount),
             actor)
            data['sort_%s' % mls.UI_GENERIC_DATE] = row.transactionDate
            data['sort_%s' % mls.UI_GENERIC_AMOUNT] = row.amount
            data['sort_%s' % mls.UI_GENERIC_ID] = row.transactionID
            scrolllist.append(listentry.Get('Generic', data))

        return scrolllist



    def OnLockedItemChangeUI(self, itemID, ownerID, locationID, change):
        self.LogInfo(self.__class__.__name__, 'OnLockedItemChangeUI')
        if self.sr.tabs.GetSelectedArgs() == 'lockdown':
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', None)
            self.ShowLockdown(sortKey, regionKey)



    def ShowLockdown(self, sortKey, regionKey, *args):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return 
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', None)
        settings.char.ui.Set('corpAssetsKeyID_lockdown', regionKey)
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(mls.UI_CORP_ACCESSDENIED7)
            self.sr.scroll.Clear()
            sm.GetService('corpui').HideLoad()
            return 
        scrolllistTmp = []
        self.sr.scroll.allowFilterColumns = 1
        locationIDs = sm.GetService('corp').GetLockedItemLocations()
        options = self.GetFilterOptions(locationIDs, 'lockdown')
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(regionKey).name)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(a.label, b.label)


        for locationID in locationIDs:
            try:
                solarSystemID = sm.GetService('ui').GetStation(locationID).solarSystemID
            except:
                solarSystemID = row.locationID
            try:
                mapSvc = sm.GetService('map')
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
                locationName = cfg.evelocations.Get(locationID).locationName
                constellationID = mapSvc.GetParent(solarSystemID)
                regionID = mapSvc.GetParent(constellationID)
                label = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
            except:
                log.LogException()
                label = '%s' % locationName
            data = {'label': label,
             'jumps': jumps,
             'GetSubContent': self.ShowLockdownSubcontent,
             'locationID': locationID,
             'regionID': regionID,
             'groupItems': None,
             'id': ('itemlocking', locationID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'scrollID': self.sr.scroll.sr.id}
            scrolllistTmp.append(listentry.Get('Group', data))

        scrolllistTmp.sort(lambda x, y: cmp(x['label'], y['label']))
        scrolllist = []
        for row in scrolllistTmp:
            if regionKey == 1:
                scrolllist.append(listentry.Get('Group', row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(listentry.Get('Group', row))
            elif row['regionID'] == regionKey:
                scrolllist.append(listentry.Get('Group', row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=mls.UI_CORP_NOITEMSFOUND)
        sm.GetService('corpui').HideLoad()



    def ShowLockdownSubcontent(self, nodedata, *args):
        scrolllist = []
        items = sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
        locationID = nodedata.locationID
        offices = sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('stationID', [locationID])
        if offices and len(offices):
            for office in offices:
                if locationID == office.stationID:
                    locationID = office.officeID

        header = ['itemID',
         'typeID',
         'ownerID',
         'groupID',
         'categoryID',
         'quantity',
         'singleton',
         'stacksize',
         'locationID',
         'flagID']
        for it in items.itervalues():
            typeInfo = cfg.invtypes.Get(it.typeID)
            line = [it.itemID,
             it.typeID,
             eve.session.corpid,
             typeInfo.groupID,
             typeInfo.categoryID,
             1,
             const.singletonBlueprintOriginal,
             1,
             locationID,
             4]
            fakeItem = util.Row(header, line)
            data = uix.GetItemData(fakeItem, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.GetMenu = self.OnGetEmptyMenu
            scrolllist.append(listentry.Get('InvItem', data))

        return scrolllist



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowSearch(self, *args):
        if not self.sr.search_inited:
            search_cont = uicls.Container(name='search_cont', parent=self, height=36, align=uiconst.TOTOP, idx=1)
            self.sr.search_cont = search_cont
            catOptions = [(mls.UI_CONTRACTS_ALL, None)]
            categories = []
            for c in cfg.invcategories:
                if c.categoryID > 0:
                    categories.append([c.categoryName, c.categoryID, c.published])

            categories.sort()
            for c in categories:
                if c[2]:
                    catOptions.append((c[0], c[1]))

            typeOptions = [(mls.UI_CORP_OFFICES, 'offices'),
             (mls.UI_CORP_IMPOUNDED, 'junk'),
             (mls.UI_CORP_INSPACE, 'property'),
             (mls.UI_CORP_DELIVERIES, 'deliveries')]
            left = 5
            top = 17
            self.sr.fltType = c = uicls.Combo(label=mls.UI_GENERIC_WHERE, parent=search_cont, options=typeOptions, name='flt_type', select=settings.user.ui.Get('corp_assets_filter_type', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltCategories = c = uicls.Combo(label=mls.UI_CONTRACTS_CATEGORY, parent=search_cont, options=catOptions, name='flt_category', select=settings.user.ui.Get('corp_assets_filter_categories', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            grpOptions = [(mls.UI_CONTRACTS_ALL, None)]
            self.sr.fltGroups = c = uicls.Combo(label=mls.UI_CONTRACTS_GROUP, parent=search_cont, options=grpOptions, name='flt_group', select=settings.user.ui.Get('corp_assets_filter_groups', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltItemType = c = uicls.SinglelineEdit(name='flt_exacttype', parent=search_cont, label=mls.UI_CONTRACTS_EXACTITEMTYPE, setvalue=settings.user.ui.Get('corp_assets_filter_itemtype', ''), width=106, top=top, left=left)
            left += c.width + 4
            c.OnFocusLost = self.ParseItemType
            self.sr.fltQuantity = c = uicls.SinglelineEdit(name='flt_quantity', parent=search_cont, label=mls.UI_SHARED_MINQUANTITY, setvalue=str(settings.user.ui.Get('corp_assets_filter_quantity', '')), width=60, top=top, left=left)
            left += c.width + 4
            c = self.sr.fltSearch = uicls.Button(parent=search_cont, label=mls.UI_CMD_SEARCH, func=self.Search, pos=(left,
             top,
             0,
             0), btn_default=1)
            self.PopulateGroupCombo(isSel=True)
            self.sr.search_inited = 1
        self.sr.search_cont.state = uiconst.UI_PICKCHILDREN
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:], noContentHint=mls.UI_CORP_NOITEMSFOUND)



    def ComboChange(self, wnd, *args):
        if wnd.name == 'flt_category':
            self.PopulateGroupCombo()



    def PopulateGroupCombo(self, isSel = False):
        categoryID = self.sr.fltCategories.GetValue()
        groups = [(mls.UI_CONTRACTS_ALL, None)]
        if categoryID:
            if categoryID in cfg.groupsByCategories:
                groupsByCategory = cfg.groupsByCategories[categoryID].Copy()
                groupsByCategory.Sort('groupName')
                for g in groupsByCategory:
                    if g.published:
                        groups.append((cfg.invgroups.Get(g.groupID).name, g.groupID))

        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_filter_groups', None)
        self.sr.fltGroups.LoadOptions(groups, sel)



    def ParseItemType(self, wnd, *args):
        if self.destroyed:
            return 
        if not hasattr(self, 'parsingItemType'):
            self.parsingItemType = None
        typeID = DoParseItemType(wnd, self.parsingItemType)
        if typeID:
            self.parsingItemType = cfg.invtypes.Get(typeID).name
        return typeID



    def Search(self, *args):
        if self is None or self.destroyed:
            return 
        sm.GetService('corpui').ShowLoad()
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:])
        self.SetHint(mls.UI_CORP_SEARCHING)
        scrolllist = []
        try:
            itemTypeID = None
            itemCategoryID = None
            itemGroupID = None
            txt = self.sr.fltItemType.GetValue()
            if txt != '':
                for t in sm.GetService('contracts').GetMarketTypes():
                    if txt == t.typeName:
                        itemTypeID = t.typeID
                        break

            txt = self.sr.fltGroups.GetValue()
            txtc = self.sr.fltCategories.GetValue()
            if txt and int(txt) > 0:
                itemGroupID = int(txt)
            elif txtc and int(txtc) > 0:
                itemCategoryID = int(txtc)
            qty = self.sr.fltQuantity.GetValue() or None
            try:
                qty = int(qty)
                if qty < 0:
                    qty = 0
            except:
                qty = None
            which = self.sr.fltType.GetValue() or None
            settings.user.ui.Set('corp_assets_filter_type', which)
            settings.user.ui.Set('corp_assets_filter_categories', itemCategoryID)
            settings.user.ui.Set('corp_assets_filter_groups', itemGroupID)
            settings.user.ui.Set('corp_assets_filter_itemtype', self.sr.fltItemType.GetValue())
            settings.user.ui.Set('corp_assets_filter_quantity', qty)
            rows = sm.RemoteSvc('corpmgr').SearchAssets(which, itemCategoryID, itemGroupID, itemTypeID, qty)
            searchCond = util.KeyVal(categoryID=itemCategoryID, groupID=itemGroupID, typeID=itemTypeID, qty=qty)
            flag = {'offices': 71,
             'junk': 72,
             'property': 74,
             'deliveries': 75}[which]
            self.SetHint(None)
            self.sr.scroll.allowFilterColumns = 1
            for row in rows:
                jumps = -1
                try:
                    solarSystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
                except:
                    solarSystemID = row.locationID
                try:
                    jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
                    locationName = cfg.evelocations.Get(row.locationID).locationName
                    label = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
                except:
                    log.LogException()
                    label = '%s' % locationName
                data = {'GetSubContent': self.GetSubContent,
                 'label': label,
                 'groupItems': None,
                 'flag': flag,
                 'id': ('corpassets', row.locationID),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': row.locationID,
                 'showicon': 'hide',
                 'MenuFunction': self.GetLocationMenu,
                 'searchCondition': searchCond,
                 'scrollID': self.sr.scroll.sr.id}
                scrolllist.append(listentry.Get('Group', data))
                uicore.registry.SetListGroupOpenState(('corpassets', row.locationID), 0)

            self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=mls.UI_CORP_NOITEMSFOUND)

        finally:
            sm.GetService('corpui').HideLoad()





