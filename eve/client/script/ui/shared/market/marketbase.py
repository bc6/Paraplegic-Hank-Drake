import base
import blue
import form
import listentry
import log
import service
import sys
import uicls
import uiconst
import uiutil
import uix
import uthread
import util
import xtriui
INFINITY = 999999999999999999L

class RegionalMarket(uicls.Window):
    __guid__ = 'form.RegionalMarket'
    default_width = 800
    default_height = 600

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station_inflight'
        self.SetCaption(mls.UI_MARKET_MARKET)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.SetMinSize([650, 416])
        self.SetWndIcon('ui_18_128_1')
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        self.sr.market = form.Market(name='marketbase', parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        self.sr.market.Startup()



    def OnEndScale_(self, *args):
        self.sr.market.OnEndScale_()



    def LoadTypeID_Ext(self, typeID):
        self.sr.market.LoadTypeID_Ext(typeID)
        uiutil.SetOrder(self, 0)




class StationMarket(uicls.Container):
    __guid__ = 'form.StationMarket'

    def Startup(self, *args):
        uicls.Line(parent=self, align=uiconst.TOTOP)
        self.sr.market = form.Market(name='marketbase', parent=self, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        self.sr.market.Startup(1)




class MarketBase(uicls.Container):
    __guid__ = 'form.Market'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnMarketQuickbarChange', 'OnOwnOrderChanged', 'OnSessionChanged']
    __update_on_reload__ = 1

    def init(self):
        self.inited = 0
        self.pendingType = None
        self.loadingType = 0
        self.lastdetailTab = mls.UI_MARKET_MARKETDATA
        self.lastOnOrderChangeTime = None
        self.refreshOrdersTimer = None
        self.groupListData = None
        self.sr.lastSearchResult = []
        self.sr.lastBrowseResult = []
        self.sr.marketgroups = None
        self.sr.quickType = None
        self.sr.pricehistory = None
        self.sr.grouplist = None
        self.sr.marketdata = None
        self.detailsInited = 0
        self.updatingGroups = 0
        self.settingsInited = 0
        self.OnChangeFuncs = {}
        self.lastid = 0
        self.name = 'MarketBase'
        self.sr.detailTypeID = None
        self.parentDictionary = {}



    def _OnClose(self, *args):
        if self.groupListData is not None:
            settings.char.ui.Set('market_groupList', self.groupListData)
        if self.sr.leftSide:
            settings.user.ui.Set('marketselectorwidth_%s' % self.idName, self.sr.leftSide.width)
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        settings.user.ui.Set('quickbar', self.folders)
        sm.UnregisterNotify(self)



    def Startup(self, isStationMarket = 0):
        self.idName = 'region'
        self.groupListData = settings.char.ui.Get('market_groupList', None)
        leftSide = uicls.Container(name='leftSide', parent=self, align=uiconst.TOLEFT, width=settings.user.ui.Get('marketselectorwidth_%s' % self.idName, 180))
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(leftSide, 'width', 'x', 180, 400)
        uicls.Line(parent=divider, align=uiconst.TORIGHT)
        uicls.Line(parent=divider, align=uiconst.TOLEFT)
        self.sr.leftSide = leftSide
        caption = '%s %s' % (cfg.evelocations.Get(session.regionid).name, mls.UI_MARKET_REGIONALMARKET)
        top = uicls.Container(name='top', parent=leftSide, align=uiconst.TOTOP, height=90)
        top.state = uiconst.UI_NORMAL
        self.sr.caption = uicls.CaptionLabel(text=caption, parent=top, align=uiconst.TOALL, left=8, top=4, uppercase=0, letterspace=0)
        combo = uicls.Combo(label=mls.UI_MARKET_RANGEFILTER, parent=top, options=self.GetOptions(), name='marketComboRangeFilter', select=self.GetRange(), align=uiconst.TOPLEFT, pos=(9, 68, 0, 0), callback=self.OnComboChange)
        self.sr.filtericon = uicls.Icon(name='icon', parent=top, width=16, height=16, left=combo.width + combo.left + 8, top=68, state=uiconst.UI_NORMAL)
        tabs = uicls.TabGroup(name='tabparent', parent=leftSide)
        uicls.Container(name='push', align=uiconst.TOLEFT, width=const.defaultPadding, parent=leftSide)
        uicls.Container(name='push', align=uiconst.TORIGHT, width=const.defaultPadding, parent=leftSide)
        uicls.Container(name='push', align=uiconst.TOBOTTOM, height=const.defaultPadding, parent=leftSide)
        uicls.Container(name='push', align=uiconst.TOTOP, height=const.defaultPadding, parent=leftSide)
        self.sr.sbTabs = tabs
        self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self)
        self.sr.grouplist = uicls.Edit(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), readonly=1, hideBackground=1)
        self.sr.grouplist.AllowResizeUpdates(0)
        uicls.Frame(parent=self.sr.grouplist, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.myorders = form.MarketOrders(name='orders', parent=self, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        searchparent = uicls.Container(name='searchparent', parent=leftSide, align=uiconst.TOTOP, padBottom=const.defaultPadding)
        btn = uicls.Button(parent=searchparent, label=mls.UI_CMD_SEARCH, func=self.Search, btn_default=1, idx=0, align=uiconst.TOPRIGHT)
        inpt = uicls.SinglelineEdit(name='edit', parent=searchparent, pos=(0, 0, 0, 0), padRight=btn.width + 6, maxLength=64, align=uiconst.TOTOP)
        inpt.OnReturn = self.Search
        searchparent.height = max(btn.height, inpt.height)
        self.sr.searchInput = inpt
        self.sr.soaCont = uicls.Container(name='show only available', align=uiconst.TOBOTTOM, height=16, state=uiconst.UI_HIDDEN, parent=leftSide)
        self.soaCb = uicls.Checkbox(text=mls.UI_MARKET_SHOWONLYAVAIL, parent=self.sr.soaCont, configName='showonlyavailable', retval=None, checked=settings.user.ui.Get('showonlyavailable', 1), callback=self.OnCheckboxChange, align=uiconst.TOTOP)
        self.sr.quickButtons = uicls.Container(name='quickButtons', align=uiconst.TOBOTTOM, height=20, padTop=4, state=uiconst.UI_HIDDEN, parent=leftSide)
        newFolder = uicls.Button(parent=self.sr.quickButtons, label=mls.UI_CMD_NEWFOLDER, align=uiconst.TOTOP, func=self.NewFolderClick, args=0)
        self.sr.quickButtons.height = newFolder.height
        self.sr.detailsparent = uicls.Container(name='details', parent=self)
        self.sr.settingsparent = uicls.Container(name='settings', parent=self, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        maintabs = [[mls.UI_MARKET_BROWSE,
          None,
          self,
          'browse'], [mls.UI_MARKET_SEARCH,
          searchparent,
          self,
          'search'], [mls.UI_MARKET_QUICKBAR,
          None,
          self,
          'quickbar']]
        subtabs = [[mls.UI_MARKET_DETAILS,
          self.sr.detailsparent,
          self,
          'details'], [mls.UI_MARKET_GROUPS,
          self.sr.grouplist,
          self,
          'groups'], [mls.UI_MARKET_MYORDERS,
          self.sr.myorders,
          self,
          'myorders']]
        if eve.session.corprole & const.corpRoleAccountant:
            self.sr.corporders = form.MarketOrders(name='corporders', parent=self, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            subtabs.append([mls.UI_MARKET_CORPORDERS,
             self.sr.corporders,
             self,
             'corporders'])
        subtabs.append([mls.UI_GENERIC_SETTINGS,
         self.sr.settingsparent,
         self,
         'settings'])
        if self.destroyed:
            return 
        self.sr.typescroll = uicls.Scroll(name='typescroll', parent=leftSide)
        self.sr.typescroll.multiSelect = 0
        self.sr.typescroll.OnSelectionChange = self.CheckTypeScrollSelection
        self.sr.sbTabs.Startup(maintabs, 'tbselectortabs_%s' % self.idName, autoselecttab=1, UIIDPrefix='marketTab')
        self.sr.tabs.Startup(subtabs, 'marketsubtabs_%s' % self.idName, autoselecttab=1, UIIDPrefix='marketTab')
        sm.RegisterNotify(self)
        self.inited = 1
        self.folders = settings.user.ui.Get('quickbar', {})
        self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
        self.SetupFilters()
        self.SetFilterIcon()
        self.maxdepth = 99



    def CheckTypeScrollSelection(self, sel):
        if len(sel) == 1:
            entry = sel[0]
            if entry.__guid__ == 'listentry.GenericMarketItem' or entry.__guid__ == 'listentry.QuickbarItem':
                self.OnTypeClick(entry.panel)



    def GetOptions(self):
        if eve.session.stationid:
            options = [(mls.UI_GENERIC_STATION, const.rangeStation), (mls.UI_GENERIC_SOLARSYSTEM, const.rangeSolarSystem), (mls.UI_GENERIC_REGION, const.rangeRegion)]
        else:
            options = [(mls.UI_GENERIC_SOLARSYSTEM, const.rangeSolarSystem), (mls.UI_GENERIC_REGION, const.rangeRegion)]
        return options



    def GetRange(self):
        return sm.StartService('marketutils').GetMarketRange()



    def OnComboChange(self, combo, header, value, *args):
        if self.inited:
            uthread.pool('BaseMarket::OnComboChange', self._OnComboChange, combo, header, value)



    def _OnComboChange(self, combo, header, value):
        sm.GetService('marketutils').SetMarketRange(value)
        self.ReloadMarketListTab()



    def ReloadMarketListTab(self, *args):
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketList()
        self.sr.tabs.ReloadVisible()



    def SetFilterIcon(self, *args):
        hint = ''
        (filtersInUse, filterUsed,) = self.FiltersInUse1()
        if filterUsed:
            ico = 'ui_38_16_205'
        else:
            ico = 'ui_38_16_204'
        self.sr.filtericon.LoadIcon(ico)
        self.sr.filtericon.hint = filtersInUse



    def OnCheckboxChange(self, sender, *args):
        settings.user.ui.Set(sender.name, bool(sender.checked))
        self.SetFilterIcon()
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketList()
        if self.sr.tabs.GetSelectedArgs() == 'browse':
            self.LoadMarketList()



    def OnCheckboxChangeSett(self, sender, *args):
        settings.user.ui.Set(sender.name, bool(sender.checked))



    def OnMarketQuickbarChange(self, menu = 0, *args):
        if self and not self.destroyed:
            if menu:
                self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
                self.folders = settings.user.ui.Get('quickbar', {})
            if self.sr.sbTabs.GetSelectedArgs() == 'quickbar':
                self.sr.filtericon.state = uiconst.UI_HIDDEN
                self.LoadQuickBar()



    def OnOwnOrderChanged(self, order, reason, isCorp):
        if self and not self.destroyed:
            if reason != 'Expiry':
                if self.lastOnOrderChangeTime and self.OnOrderChangeTimer is None:
                    intval = 15000
                    diff = blue.os.TimeDiffInMs(self.lastOnOrderChangeTime)
                    if diff > intval:
                        self._OnOwnOrderChanged(order.typeID)
                    else:
                        self.OnOrderChangeTimer = base.AutoTimer(intval - int(diff), self._OnOwnOrderChanged, (order.typeID,))
                else:
                    self._OnOwnOrderChanged(order.typeID)
            elif not settings.user.ui.Get('autorefresh', True) and self.sr.detailTypeID:
                if order.typeID == self.sr.detailTypeID:
                    self.sr.reloadBtn.state = uiconst.UI_NORMAL



    def _OnOwnOrderChanged(self, orderTypeID):
        if self and not self.destroyed:
            try:
                if settings.user.ui.Get('autorefresh', True):
                    if self.sr.sbTabs.GetSelectedArgs() == 'browse':
                        self.LoadMarketList()
                    self.sr.tabs.ReloadVisible()
                    self.OnOrderChangeTimer = None
                    self.lastOnOrderChangeTime = blue.os.GetTime()
                elif orderTypeID == self.sr.detailTypeID:
                    self.sr.reloadBtn.state = uiconst.UI_NORMAL
            except AttributeError:
                if not self or self.destoyed:
                    return 
                raise 



    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid' in change and self and not self.destroyed:
            combo = uiutil.FindChild(self, 'marketComboRangeFilter')
            if combo:
                oldValue = combo.GetValue()
                newValue = self.GetRange()
                combo.LoadOptions(self.GetOptions(), newValue)
                if oldValue != newValue:
                    self.ReloadMarketListTab()
            self.sr.caption.text = '%s %s' % (cfg.evelocations.Get(session.regionid).name, mls.UI_MARKET_REGIONALMARKET)



    def GetQuickItemMenu(self, btn, *args):
        m = [(mls.UI_CMD_REMOVE, self.RemoveFromQuickBar, (btn.sr.node,))]
        m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (btn.sr.node.invtype.typeID,))]
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            m.append(None)
            m += sm.GetService('menu').GetGMTypeMenu(btn.sr.node.typeID)
        return m



    def RemoveFromQuickBar(self, node):
        sm.GetService('menu').RemoveFromQuickBar(node)



    def OnEndScale_(self, *args):
        if self.sr.grouplist and self.sr.grouplist.state != uiconst.UI_HIDDEN:
            uthread.pool('MarketBase::OnEndScale_', self.ShowGroupPage)



    def LoadMarketList(self):
        if self.destroyed:
            return 
        self.SetFilterIcon()
        self.sr.soaCont.state = uiconst.UI_PICKCHILDREN
        self.sr.quickButtons.state = uiconst.UI_HIDDEN
        self.mine = self.GetMySkills()
        self.PopulateAsksForMyRange()
        scrolllist = self.GetGroupListForBrowse()
        if self.destroyed:
            return 
        self.sr.typescroll.Load(contentList=scrolllist, scrollTo=self.sr.typescroll.GetScrollProportion())



    def PopulateAsksForMyRange(self):
        quote = sm.StartService('marketQuote')
        marketRange = self.GetRange()
        if marketRange == const.rangeStation:
            self.asksForMyRange = quote.GetStationAsks()
        elif marketRange == const.rangeSolarSystem:
            self.asksForMyRange = quote.GetSystemAsks()
        else:
            self.asksForMyRange = quote.GetRegionBest()



    def GetGroupListForBrowse(self, nodedata = None, newitems = 0):
        scrolllist = []
        if nodedata and nodedata.marketGroupInfo.hasTypes:
            for typeID in nodedata.typeIDs:
                invType = cfg.invtypes.Get(typeID)
                data = util.KeyVal()
                data.label = invType.name
                data.invtype = invType
                data.sublevel = nodedata.sublevel + 1
                data.GetMenu = self.OnTypeMenu
                data.ignoreRightClick = 1
                data.showinfo = 1
                data.typeID = invType.typeID
                scrolllist.append((invType.name.lower(), listentry.Get('GenericMarketItem', data=data)))

        else:
            marketGroupID = None
            level = 0
            if nodedata:
                marketGroupID = nodedata.marketGroupInfo.marketGroupID
                level = nodedata.sublevel + 1
            grouplist = sm.GetService('marketutils').GetMarketGroups()[marketGroupID]
            for marketGroupInfo in grouplist:
                if not len(marketGroupInfo.types):
                    continue
                if self.destroyed:
                    return 
                typeIDs = self.FilterItemsForBrowse(marketGroupInfo)
                if len(typeIDs) == 0:
                    continue
                groupID = (marketGroupInfo.marketGroupName, marketGroupInfo.marketGroupID)
                data = {'GetSubContent': self.GetGroupListForBrowse,
                 'label': marketGroupInfo.marketGroupName,
                 'id': groupID,
                 'typeIDs': typeIDs,
                 'iconMargin': 18,
                 'showlen': 0,
                 'marketGroupInfo': marketGroupInfo,
                 'sublevel': level,
                 'state': 'locked',
                 'disableToggle': marketGroupInfo.hasTypes,
                 'OnClick': self.LoadGroup,
                 'showicon': [None, 'ui_38_16_173'][marketGroupInfo.hasTypes],
                 'iconID': marketGroupInfo.iconID,
                 'selected': False,
                 'hideExpander': marketGroupInfo.hasTypes,
                 'BlockOpenWindow': 1,
                 'MenuFunction': self.SelectFolderMenu}
                if marketGroupInfo.hasTypes and getattr(self, 'groupListData', None) and self.groupListData.marketGroupID != marketGroupInfo.marketGroupID:
                    uicore.registry.SetListGroupOpenState(groupID, 0)
                scrolllist.append(((marketGroupInfo.hasTypes, marketGroupInfo.marketGroupName.lower()), listentry.Get('Group', data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def LoadGroup(self, group, *args):
        self.state = uiconst.UI_DISABLED
        try:
            if group.sr.node.marketGroupInfo.hasTypes:
                groupID = group.sr.node.marketGroupInfo.marketGroupID
                for entry in self.sr.typescroll.GetNodes():
                    if entry.marketGroupInfo and entry.marketGroupInfo.hasTypes and entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            entry.open = 0
                            if entry.subNodes:
                                rm = entry.subNodes
                                entry.subNodes = []
                                entry.open = 0
                                self.sr.typescroll.RemoveEntries(rm)

                for entry in self.sr.typescroll.GetNodes():
                    if entry.marketGroupInfo and entry.marketGroupInfo.marketGroupID == groupID:
                        group = entry
                        if group.panel:
                            group.panel.Toggle()
                        else:
                            group.open = 1
                            self.sr.typescroll.PrepareSubContent(entry)
                        self.sr.typescroll.SelectNode(entry)
                        self.groupListData = entry.marketGroupInfo
                        self.sr.typescroll.ShowNodeIdx(entry.idx)
                        self.sr.tabs.ShowPanelByName(mls.UI_MARKET_GROUPS)


        finally:
            self.state = uiconst.UI_PICKCHILDREN




    def GetAttrDict(self, typeID):
        ret = {}
        for each in cfg.dgmtypeattribs.get(typeID, []):
            attribute = cfg.dgmattribs.Get(each.attributeID)
            if attribute.attributeCategory == 9:
                ret[each.attributeID] = getattr(cfg.invtypes.Get(typeID), attribute.attributeName)
            else:
                ret[each.attributeID] = each.value

        if not ret.has_key(const.attributeCapacity) and cfg.invtypes.Get(typeID).capacity:
            ret[const.attributeCapacity] = cfg.invtypes.Get(typeID).capacity
        attrInfo = sm.GetService('godma').GetType(typeID)
        for each in attrInfo.displayAttributes:
            ret[each.attributeID] = each.value

        return ret



    def GetActiveShipSlots(self):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return 0
        hiSlots = getattr(ship, 'hiSlots', 0)
        medSlots = getattr(ship, 'medSlots', 0)
        lowSlots = getattr(ship, 'lowSlots', 0)
        rigSlots = getattr(ship, 'rigSlots', 0)
        flags = []
        key = uix.FitKeys()
        for gidx in xrange(3):
            for sidx in xrange(8):
                flags.append(getattr(const, 'flag%sSlot%s' % (key[gidx], sidx)))


        for module in ship.modules:
            if module.flagID not in flags:
                continue
            for effect in module.effects.itervalues():
                if effect.effectID == const.effectHiPower:
                    hiSlots -= 1
                elif effect.effectID == const.effectMedPower:
                    medSlots -= 1
                elif effect.effectID == const.effectLoPower:
                    lowSlots -= 1
                elif effect.effectID == const.effectRigSlot:
                    rigSlots -= 1


        return (hiSlots,
         medSlots,
         lowSlots,
         rigSlots)



    def GetMySkills(self):
        return sm.GetService('skills').MySkillLevelsByID()



    def GetRequirement(self, invType, freeslots):
        requiredSkills = sm.GetService('info').GetRequiredSkills(invType.typeID)
        missingSkill = ''
        haveSkills = 1
        isSkill = cfg.invgroups.Get(invType.groupID).categoryID == const.categorySkill
        haveThisSkill = False
        mine = self.GetMySkills()
        if isSkill:
            if mine.get(invType.typeID, None) != None:
                haveThisSkill = True
        if requiredSkills:
            for (skillID, level,) in requiredSkills:
                if skillID not in mine or mine[skillID] < level:
                    missingSkill = ' ' + mls.UI_MARKET_MISSINGSKILLLEVEL % {'skill': cfg.invtypes.Get(skillID).name,
                     'level': int(level)}
                    haveSkills = 0
                    break

        if isSkill and haveThisSkill:
            ret = '\n                <table cellspacing=0 cellpadding=0 height=20 width=66>\n                    <tr height=16>\n                        <td width=22 valign=top>\n                            <img src="icon:38_193" size=16 alt="%s">\n                        </td>\n\n\n                ' % (mls.UI_GENERIC_YOUALREADYKNOWTHISSKILL,)
        elif requiredSkills:
            ret = '\n                <table cellspacing=0 cellpadding=0 height=32 width=66>\n                    <tr height=32>\n                        <td width=22 valign=top>\n                            <img src="icon:50_11" bgcolor=%s size=22 alt="%s%s">\n                        </td>\n\n\n                ' % (['#33ff0000', '#3300ff00'][haveSkills], mls.UI_GENERIC_REQUIREDSKILL, missingSkill)
        else:
            ret = '\n                <table cellspacing=0 cellpadding=0>\n                    <tr height=32>\n                '
        haveSlot = 0
        havePower = 0
        haveCpu = 0
        done = 0
        isHardware = invType.Group().Category().IsHardware()
        if isHardware:
            powerEffect = None
            powerIdx = None
            powerEffects = [const.effectHiPower, const.effectMedPower, const.effectLoPower]
            for effect in cfg.dgmtypeeffects.get(invType.typeID, []):
                if effect.effectID in powerEffects:
                    powerEffect = cfg.dgmeffects.Get(effect.effectID)
                    powerIdx = powerEffects.index(effect.effectID)
                    break

            powerLoad = 0
            cpuLoad = 0
            shipID = util.GetActiveShip()
            if shipID is not None and powerIdx is not None:
                ship = sm.GetService('godma').GetItem(eve.session.shipid)
                dgmAttr = sm.GetService('godma').GetType(invType.typeID)
                haveSlot = not not getattr(ship, ['hiSlots', 'medSlots', 'lowSlots'][powerIdx], 0)
                for attribute in dgmAttr.displayAttributes:
                    if attribute.attributeID in (const.attributeCpuLoad, const.attributeCpu):
                        cpuLoad += attribute.value
                    elif attribute.attributeID in (const.attributePowerLoad, const.attributePower):
                        powerLoad += attribute.value

                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                havePower = dogmaLocation.GetAttributeValue(shipID, const.attributePowerOutput) > powerLoad
                haveCpu = dogmaLocation.GetAttributeValue(shipID, const.attributeCpuOutput) > cpuLoad
            if powerEffect:
                cpuLoad = int(cpuLoad)
                powerLoad = int(powerLoad)
                ret += '\n                        <td width=22 align=center><img src="icon:ui_2_64_7" bgcolor=%s size=22 alt="%s"><br><font style="font-size:8; letter-spacing:1px">%s</font></td>\n                        <td width=22 align=center><img src="icon:ui_12_64_7" bgcolor=%s size=22 alt="%s" margin-left=-10><br><font style="font-size:8; letter-spacing:1px">%s</font></td>\n\n                ' % (['#33ff0000', '#3300ff00'][havePower],
                 mls.UI_GENERIC_POWERLOAD,
                 powerLoad,
                 ['#33ff0000', '#3300ff00'][haveCpu],
                 mls.UI_GENERIC_CPULOAD,
                 cpuLoad)
                done = 1
        ret += '\n            </tr>\n          </table>\n        '
        return ret



    def ShowGroupPage(self, *args):
        if self.updatingGroups:
            return 
        self.updatingGroups = 0
        self.PopulateAsksForMyRange()
        try:
            self.sr.grouplist.LoadHTML('<body>%s ...</body>' % mls.UI_GENERIC_LOADING, newThread=0)
            html = '\n                <body>\n                <br>\n                '
            group = self.groupListData
            if group:
                ship = None
                if eve.session.shipid:
                    ship = sm.GetService('godma').GetItem(eve.session.shipid)
                freeslots = self.GetActiveShipSlots()
                width = self.sr.grouplist.GetContentWidth() - 96
                sorted = []
                self.mine = self.GetMySkills()
                for data in self.FilterItemsForGroupPage(group):
                    invType = cfg.invtypes.Get(data.typeID)
                    sorted.append((invType.name.lower(), data))

                sorted = uiutil.SortListOfTuples(sorted)
                if not sorted:
                    html += '\n                        %s\n                        ' % mls.UI_SHARED_MARKETBASE_SHOWGROUPLIST_MSG1
                    if settings.user.ui.Get('showonlyavailable', 1):
                        html += '\n                            <br>%s\n                            ' % mls.UI_SHARED_MARKETBASE_SHOWGROUPLIST_MSG2
                for data in sorted:
                    invtype = cfg.invtypes.Get(data.typeID)
                    if data.qty:
                        buttonTxt = mls.UI_CMD_BUY
                    else:
                        buttonTxt = mls.UI_CMD_PLACEBUYORDER
                    btn = '<span style=text-align:right>'
                    btn += '<FORM ACTION="localsvc:service=marketutils&method=ProcessRequest&subMethod=Buy&typeID=%s" METHOD="get"><INPUT TYPE="submit" NAME="" VALUE="%s"></FORM>' % (data.typeID, buttonTxt)
                    btn += '<FORM ACTION="localsvc:service=marketutils&method=ProcessRequest&subMethod=ShowMarketDetails&typeID=%s" METHOD="get"><INPUT TYPE="submit" NAME="" VALUE="%s"><br></span></FORM>' % (data.typeID, mls.UI_MARKET_VIEWDETAILS)
                    jump = ''
                    if data.qty:
                        jumps = int(data.jumps)
                        if jumps == 0:
                            jump = ' %s' % mls.UI_MARKET_INTHISSYSTEM
                        elif jumps == -1:
                            jump = ' %s' % mls.UI_MARKET_INTHISSTATION
                        jump = ', %s' % [mls.UI_MARKET_JUMPAWAY, mls.UI_MARKET_JUMPSAWAY][(data.jumps > 1)] % {'jumps': data.jumps}
                    desc = invtype.description.replace('\r\n', '<br>').strip()
                    if desc.endswith('<br>'):
                        desc = desc[:(len(desc) - 4)]
                    where = {const.rangeStation: mls.UI_GENERIC_STATION,
                     const.rangeSolarSystem: mls.UI_GENERIC_SOLARSYSTEMSYSTEM,
                     const.rangeRegion: mls.UI_GENERIC_REGION}[self.GetRange()]
                    html += '\n                        <p>\n                        <img style=margin-right:10;margin-bottom:4 src="typeicon:typeID=%s&bumped=1&showFitting=1&showTechLevel=1" align=left>\n                        %s\n                        <font size=20 margin-left=20>%s</font>\n                        <a href=showinfo:%s><img style:vertical-align:bottom src="icon:38_208" size=16 alt="%s"></a>\n                        <br>\n                        </p>\n                        <font size=12>%s</font>\n                        <br><br>\n                        <font size=12>%s</font>\n                        <br>\n                        <font size=20>%s</font>\n                        <br>\n                        <font size=12>%s%s<br></font>\n                        %s\n\n                    ' % (data.typeID,
                     self.GetRequirement(invtype, freeslots),
                     invtype.name,
                     data.typeID,
                     mls.UI_CMD_SHOWINFO,
                     desc,
                     mls.UI_MARKET_BESTPRICEIN % {'where': where},
                     data.fmt_price,
                     mls.UI_MARKET_UNITAVAILABLE % {'units': data.fmt_qty},
                     jump,
                     btn)
                    html += '<hr>'

            else:
                html += '\n                    %s\n                    ' % mls.UI_MARKET_SELECTGROUPTOBROWSE
            html += '\n                </body>\n                '
            self.sr.grouplist.LoadHTML(html, newThread=0)

        finally:
            if self.destroyed:
                return 
            self.updatingGroups = 0




    def Load(self, key):
        if key == 'marketdata':
            self.lastdetailTab = mls.UI_MARKET_MARKETDATA
            self.LoadMarketData()
        elif key == 'quickbar':
            self.sr.filtericon.state = uiconst.UI_HIDDEN
            self.LoadQuickBar()
        elif key == 'details':
            self.LoadDetails()
        elif key == 'pricehistory':
            self.lastdetailTab = mls.UI_MARKET_PRICEHISTORY
            self.LoadPriceHistory()
        elif key == 'browse':
            self.sr.filtericon.state = uiconst.UI_NORMAL
            self.LoadMarketList()
        elif key == 'groups':
            self.ShowGroupPage()
        elif key == 'search':
            self.sr.filtericon.state = uiconst.UI_HIDDEN
            self.Search()
        elif key == 'myorders':
            self.LoadOrders()
        elif key == 'corporders':
            self.LoadCorpOrders()
        elif key == 'settings':
            self.LoadSettingsTab()



    def LoadOrders(self, *args):
        if not getattr(self, 'ordersInited', 0):
            self.sr.myorders.Setup('market')
            self.ordersInited = 1
        self.sr.myorders.ShowOrders()



    def LoadCorpOrders(self, *args):
        if not getattr(self, 'corpordersInited', 0):
            self.sr.corporders.Setup('market')
            self.corpordersInited = 1
        self.sr.corporders.ShowOrders(isCorp=True)



    def Search(self, *args):
        self.sr.filtericon.state = uiconst.UI_HIDDEN
        self.sr.soaCont.state = uiconst.UI_HIDDEN
        self.sr.quickButtons.state = uiconst.UI_HIDDEN
        search = self.sr.searchInput.GetValue().lower()
        if not search or search == ' ':
            self.sr.typescroll.Load(contentList=[listentry.Get('Generic', {'label': mls.UI_MARKET_PLEASETYPEANDSEARCH})])
            return 
        self.sr.typescroll.Load(contentList=[])
        self.sr.typescroll.ShowHint(mls.UI_GENERIC_SEARCHING)
        t = uix.TakeTime('Market::GetSearchResult', self.GetSearchResult)
        if not t:
            t = [listentry.Get('Generic', {'label': mls.UI_MARKET_NOTHINGFOUNDWITHSEARCH % {'search': search}})]
        self.sr.typescroll.ShowHint()
        self.sr.typescroll.Load(contentList=t)



    def LoadDetails(self):
        filtersInUse = self.FiltersInUse2()
        if not self.detailsInited:
            uicls.Container(name='push', parent=self.sr.detailsparent, align=uiconst.TOTOP, height=const.defaultPadding)
            top = uicls.Container(name='tabparent', align=uiconst.TOTOP, height=90, parent=self.sr.detailsparent, clipChildren=1)
            self.sr.reloadBtn = uicls.Button(parent=top, label=mls.UI_GENERIC_RELOAD, pos=(const.defaultPadding,
             0,
             0,
             0), func=self.OnReload, align=uiconst.TOPRIGHT)
            self.sr.reloadBtn.state = uiconst.UI_HIDDEN
            self.sr.detailIcon = uicls.DraggableIcon(parent=top, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, left=12, top=2)
            self.sr.techIcon = uicls.Sprite(name='techIcon', parent=top, align=uiconst.TOPLEFT, left=self.sr.detailIcon.left + 1, top=self.sr.detailIcon.top + 1, width=16, height=16, idx=0, state=uiconst.UI_HIDDEN)
            self.sr.detailGroupTrace = uicls.Label(text='', parent=top, top=2, left=86, state=uiconst.UI_NORMAL)
            self.sr.detailGroupTrace.OnClick = (self.ClickGroupTrace, self.sr.detailGroupTrace)
            self.sr.detailTop = uicls.CaptionLabel(text=mls.UI_MARKET_NOTYPESELECTED, parent=top, align=uiconst.TOPLEFT)
            self.sr.detailTop.left = 86
            self.sr.detailTop.top = 20
            self.sr.detailInfoicon = uicls.InfoIcon(size=16, left=78, top=0, parent=top, idx=0, state=uiconst.UI_HIDDEN)
            self.sr.detailInfoicon.OnClick = self.ShowInfoFromDetails
            self.sr.detailTypeID = None
            typeID = self.GetTypeIDFromDetails()
            self.sr.filtersText = uicls.Label(text='', parent=top, autowidth=False, align=uiconst.TOPLEFT, top=50, state=uiconst.UI_NORMAL, left=86)
            self.sr.detailtabs = uicls.TabGroup(name='tabparent', parent=self.sr.detailsparent)
            self.sr.marketdata = uicls.Container(name='marketinfo', parent=self.sr.detailsparent, pos=(0, 0, 0, 0))
            self.sr.pricehistory = xtriui.PriceHistoryParent(name='pricehistory', parent=self.sr.detailsparent, pos=(0, 0, 0, 0))
            detailtabs = [[mls.UI_MARKET_MARKETDATA,
              self.sr.marketdata,
              self,
              'marketdata'], [mls.UI_MARKET_PRICEHISTORY,
              self.sr.pricehistory,
              self,
              'pricehistory']]
            self.sr.detailtabs.Startup(detailtabs, 'marketdetailtabs', autoselecttab=1, UIIDPrefix='marketDetailsTab')
            self.sr.detailtabs.state = uiconst.UI_HIDDEN
            self.detailsInited = 1
            return 
        if self.lastdetailTab:
            self.sr.detailtabs.ShowPanelByName(self.lastdetailTab)
        filtersInUse = self.FiltersInUse2()
        self.sr.filtersText.text = ['', mls.UI_MARKET_FILTERS][bool(filtersInUse)]
        self.sr.filtersText.hint = ['', filtersInUse][bool(filtersInUse)]



    def OnReload(self, *args):
        self.sr.reloadBtn.state = uiconst.UI_HIDDEN
        self.sr.marketdata.children[0].OnReload()
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketList()
        self.OnOrderChangeTimer = None
        self.lastOnOrderChangeTime = blue.os.GetTime()



    def ShowInfoFromDetails(self, *args):
        typeID = self.GetTypeIDFromDetails()
        if typeID is not None:
            sm.GetService('info').ShowInfo(typeID)



    def PreviewFromDetails(self, *args):
        typeID = self.GetTypeIDFromDetails()
        if typeID is not None:
            sm.GetService('preview').PreviewType(typeID)



    def GetTypeIDFromDetails(self):
        typeID = None
        invtype = self.GetSelection()
        if invtype:
            typeID = invtype.typeID
        if typeID is None:
            if self.sr.Get('detailTypeID'):
                typeID = self.sr.detailTypeID
        return typeID



    def ClickGroupTrace(self, trace, *args):
        if trace.sr.marketGroupInfo:
            self.groupListData = trace.sr.marketGroupInfo
            self.sr.tabs.ShowPanelByName(mls.UI_MARKET_GROUPS)



    def LoadQuickBar(self, selectFolder = 0, *args):
        self.sr.filtericon.state = uiconst.UI_HIDDEN
        self.sr.soaCont.state = uiconst.UI_HIDDEN
        self.sr.quickButtons.state = uiconst.UI_PICKCHILDREN
        self.selectFolder = selectFolder
        self.folders = settings.user.ui.Get('quickbar', {})
        if not self.folders:
            if settings.user.ui.Get('marketquickbar', 0):
                self.LoadOldQuickBar()
        scrolllist = self.LoadQuickBarItems()
        if self.selectFolder:
            result = self.ListWnd([], 'item', mls.UI_MARKET_QUICKBAR_SELECTFOLDER, None, 1, contentList=scrolllist)
            if not result:
                return False
            (id, parentDepth,) = result
            if self.depth + 1 + parentDepth + 1 > 7:
                msg = mls.UI_MARKET_DEEPQUICKBAR
                yesNo = eve.Message('AskAreYouSure', {'cons': msg % {'num': self.depth + 1 + parentDepth + 1}}, uiconst.YESNO)
                return [False, id][(yesNo == uiconst.ID_YES)]
            return id
        self.sr.typescroll.Load(contentList=scrolllist)



    def LoadOldQuickBar(self):
        items = settings.user.ui.Get('marketquickbar', [])
        for each in items:
            n = util.KeyVal()
            n.parent = 0
            n.id = self.lastid
            n.label = each
            self.folders[n.id] = n
            self.lastid += 1

        settings.user.ui.Delete('marketquickbar')



    def LoadMarketData(self, *args):
        invtype = self.GetSelection()
        if self.sr.marketdata:
            if not len(self.sr.marketdata.children):
                form.MarketData(name='marketdata', parent=self.sr.marketdata, pos=(0, 0, 0, 0))
            if invtype:
                self.sr.marketdata.children[0].LoadType(invtype)
            else:
                self.sr.marketdata.children[0].ReloadType()
            self.sr.reloadBtn.state = uiconst.UI_HIDDEN



    def LoadPriceHistory(self, invtype = None, *args):
        invtype = invtype or self.GetSelection()
        if not invtype:
            return 
        if self.sr.pricehistory:
            self.sr.reloadBtn.state = uiconst.UI_HIDDEN
            if not self.sr.pricehistory.inited:
                self.sr.pricehistory.Startup()
            self.sr.pricehistory.LoadType(invtype)



    def GetSearchResult(self):
        marketTypes = sm.GetService('marketutils').GetMarketTypes()
        marketTypes = dict([ [i, None] for i in marketTypes ])
        search = self.sr.searchInput.GetValue().lower()
        if self.sr.lastSearchResult and self.sr.lastSearchResult[0] == search:
            scrollList = self.sr.lastSearchResult[1][:]
        else:
            scrollList = []
            if search:
                res = [ invtype for invtype in cfg.invtypes if invtype.typeID in marketTypes if invtype.typeName.lower().find(search) != -1 ]
                for t in res:
                    data = util.KeyVal()
                    data.label = t.name
                    data.GetMenu = self.OnTypeMenu
                    data.invtype = t
                    data.showinfo = 1
                    data.typeID = t.typeID
                    scrollList.append((t.name.lower(), listentry.Get('GenericMarketItem', data=data)))
                    blue.pyos.BeNice()

                scrollList = uiutil.SortListOfTuples(scrollList)
        self.sr.lastSearchResult = (search, scrollList[:])
        return scrollList



    def OnTypeClick(self, entry, *args):
        if not self.sr.typescroll.GetSelected():
            return 
        if self.loadingType:
            self.pendingType = 1
            return 
        self.sr.quickType = None
        self.ReloadType()



    def OnTypeMenu(self, entry):
        invtype = entry.sr.node.invtype
        categoryID = invtype.categoryID
        menu = [(mls.UI_CMD_ADDTOMARKETQUICKBAR, self.AddToQuickBar, (invtype,)), (mls.UI_CMD_SHOWINFO, self.ShowInfo, (invtype.typeID,))]
        if categoryID in const.previewCategories and invtype.Icon() and invtype.Icon().iconFile != '':
            menu.append((mls.UI_CMD_PREVIEW, sm.GetService('preview').PreviewType, (entry.sr.node.invtype.typeID,)))
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            menu.append(None)
            menu += sm.GetService('menu').GetGMTypeMenu(entry.sr.node.invtype.typeID)
        return menu



    def ShowInfo(self, typeID):
        sm.GetService('info').ShowInfo(typeID)



    def AddToQuickBar(self, invtype):
        settings.user.ui.Set('quickbar', self.folders)
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        sm.GetService('menu').AddToQuickBar(invtype.typeID)
        self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
        self.folders = settings.user.ui.Get('quickbar', {})



    def LoadQuickType(self, quick = None, *args):
        if quick:
            self.sr.quickType = quick.invType
            self.ReloadType()



    def LoadTypeID_Ext(self, typeID):
        self.sr.quickType = cfg.invtypes.Get(typeID)
        self.ReloadType()



    def ReloadType(self):
        self.pendingType = 0
        self.loadingType = 1
        blue.pyos.synchro.Yield()
        try:
            self.sr.tabs.ShowPanelByName(mls.UI_MARKET_DETAILS)
        except StandardError as e:
            self.loadingType = 0
            raise e
        blue.pyos.synchro.Yield()
        invtype = self.GetSelection()
        if not invtype:
            self.loadingType = 0
            return 
        self.sr.detailTop.text = invtype.name
        self.sr.detailIcon.LoadIconByTypeID(invtype.typeID)
        self.sr.detailIcon.SetSize(64, 64)
        techSprite = uix.GetTechLevelIcon(self.sr.techIcon, typeID=invtype.typeID)
        self.sr.detailIcon.state = uiconst.UI_DISABLED
        self.sr.detailtabs.state = uiconst.UI_NORMAL
        left = self.sr.detailTop.left + self.sr.detailTop.textwidth + 8
        top = self.sr.detailTop.top + 4
        self.sr.detailInfoicon.state = uiconst.UI_NORMAL
        self.sr.detailInfoicon.top = top
        self.sr.detailInfoicon.left = left
        typeID = invtype.typeID
        self.sr.detailTypeID = invtype.typeID
        (marketGroup, trace,) = sm.GetService('marketutils').FindMarketGroup(invtype.typeID)
        if marketGroup:
            self.sr.detailGroupTrace.sr.marketGroupInfo = marketGroup
            self.sr.detailGroupTrace.text = trace
        else:
            self.sr.detailGroupTrace.text = ''
            self.sr.detailGroupTrace.sr.marketGroupInfo = None
        self.loadingType = 0
        if self.pendingType:
            self.ReloadType()



    def GetSelection(self):
        if self.sr.quickType:
            return self.sr.quickType
        selection = self.sr.typescroll.GetSelected()
        if not selection:
            return None
        if hasattr(selection[0], 'invtype'):
            return selection[0].invtype



    def ResetQuickbar(self):
        self.folders = {}
        settings.user.ui.Set('quickbar', self.folders)
        self.lastid = 0
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        sm.ScatterEvent('OnMarketQuickbarChange')



    def ResetSettings(self):
        settings.user.ui.Set('showonlyskillsfor', False)
        settings.user.ui.Set('showhavecpuandpower', False)
        settings.user.ui.Set('shownewskills', False)
        settings.user.ui.Set('showonlyavailable', True)
        settings.user.ui.Set('autorefresh', True)
        self.soaCb.SetChecked(1)
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketList()
        settings.user.ui.Set('market_filter_price', False)
        settings.user.ui.Set('minEdit_market_filter_price', 0)
        settings.user.ui.Set('maxEdit_market_filter_price', 100000)
        settings.user.ui.Set('market_filter_jumps', False)
        settings.user.ui.Set('minEdit_market_filter_jumps', 0)
        settings.user.ui.Set('maxEdit_market_filter_jumps', 20)
        settings.user.ui.Set('market_filter_quantity', False)
        settings.user.ui.Set('minEdit_market_filter_quantity', 0)
        settings.user.ui.Set('maxEdit_market_filter_quantity', 1000)
        settings.user.ui.Set('market_filter_zerosec', True)
        settings.user.ui.Set('market_filter_lowsec', True)
        settings.user.ui.Set('market_filter_highsec', True)
        settings.user.ui.Set('market_filters_sellorderdev', False)
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', 0)
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', 0)
        settings.user.ui.Set('market_filters_buyorderdev', False)
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', 0)
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', 0)
        settings.user.ui.Set('buydefault', {'duration': 0,
         'useCorpWallet': 0,
         'range': const.rangeStation})
        settings.user.ui.Set('selldefault', {'duration': 0,
         'useCorpWallet': 0})
        self.LoadSettingsTab()



    def LoadQuickBarItems(self, *args):
        import types
        scrolllist = []
        notes = self.GetItems(parent=0)
        for (id, n,) in notes.items():
            if type(n.label) == types.UnicodeType:
                groupID = ('quickbar', id)
                data = {'GetSubContent': self.GetGroupSubContent,
                 'label': n.label,
                 'id': groupID,
                 'groupItems': self.GroupGetContentIDList(groupID),
                 'iconMargin': 18,
                 'showlen': 0,
                 'state': 0,
                 'sublevel': 0,
                 'MenuFunction': [self.GroupMenu, self.SelectFolderMenu][self.selectFolder],
                 'BlockOpenWindow': 1,
                 'DropData': self.GroupDropNode,
                 'ChangeLabel': self.GroupChangeLabel,
                 'DeleteFolder': self.GroupDeleteFolder,
                 'selected': 1,
                 'hideNoItem': self.selectFolder,
                 'selectGroup': 1}
                if self.selectFolder:
                    data['OnDblClick'] = self.OnDblClick
                    if data.get('sublevel', 0) + self.depth >= self.maxdepth:
                        return []
                scrolllist.append((n.label, listentry.Get('Group', data)))

        if scrolllist:
            scrolllist = uiutil.SortListOfTuples(scrolllist)
        tempScrolllist = []
        if not self.selectFolder:
            for (id, n,) in notes.items():
                if type(n.label) == types.IntType:
                    groupID = ('quickbar', id)
                    data = {'label': cfg.invtypes.Get(n.label).name,
                     'typeID': n.label,
                     'id': groupID,
                     'itemID': None,
                     'getIcon': 0,
                     'sublevel': 0,
                     'showinfo': 1,
                     'GetMenu': self.GetQuickItemMenu,
                     'DropData': self.GroupDropNode,
                     'parent': n.parent,
                     'selected': 1,
                     'invtype': cfg.invtypes.Get(n.label)}
                    tempScrolllist.append((cfg.invtypes.Get(n.label).name.lower(), listentry.Get('QuickbarItem', data)))

        if tempScrolllist:
            tempScrolllist = uiutil.SortListOfTuples(tempScrolllist)
            scrolllist.extend(tempScrolllist)
        return scrolllist



    def GroupMenu(self, node):
        m = []
        if node.sublevel < self.maxdepth:
            m.append((mls.UI_CMD_NEWFOLDER, self.NewFolder, (node.id[1], node)))
        return m



    def QuickbarHasFolder(self):
        import types
        if settings.user.ui.Get('quickbar', {}):
            for (id, node,) in settings.user.ui.Get('quickbar', {}).items():
                if type(node.label) == types.UnicodeType:
                    return True

        return False



    def SelectFolderMenu(self, node):
        m = []
        if node.sublevel < self.maxdepth:
            if self.QuickbarHasFolder():
                m.append((mls.UI_MARKET_QUICKBAR_ADDGROUPTOFOLDER, self.FolderPopUp, (node,)))
            m.append((mls.UI_MARKET_QUICKBAR_ADDGROUPTOROOT, self.FolderPopUp, (node, True)))
        return m



    def FolderPopUp(self, node, root = False):
        self.tempLastid = self.lastid
        self.tempFolders = {}
        (self.depth, firstID,) = self.AddGroupParent(nodedata=node)
        if root:
            id = 0
        else:
            id = self.LoadQuickBar(selectFolder=1)
        if id is not None and id is not False:
            self.tempFolders[firstID].parent = id
            for each in range(firstID, self.tempLastid + 1):
                self.folders[each] = self.tempFolders[each]

            self.lastid = self.tempLastid
            settings.user.ui.Set('quickbar_lastid', self.lastid)



    def GetGroupSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        notelist = self.GetItems(nodedata.id[1])
        if len(notelist):
            qi = 1
            NoteListLength = len(notelist)
            import types
            for (id, note,) in notelist.items():
                if type(note.label) == types.UnicodeType:
                    entry = self.GroupCreateEntry((note.label, id), nodedata.sublevel + 1)
                    if entry:
                        scrolllist.append((note.label.lower(), entry))

            if scrolllist:
                scrolllist = uiutil.SortListOfTuples(scrolllist)
            tempScrolllist = []
            if not self.selectFolder:
                for (id, note,) in notelist.items():
                    if type(note.label) == types.IntType:
                        entry = self.GroupCreateEntry((note.label, id), nodedata.sublevel + 1)
                        if entry:
                            tempScrolllist.append((cfg.invtypes.Get(note.label).name.lower(), entry))

            if tempScrolllist:
                tempScrolllist = uiutil.SortListOfTuples(tempScrolllist)
                scrolllist.extend(tempScrolllist)
            if len(nodedata.groupItems) != len(scrolllist):
                nodedata.groupItems = self.GroupGetContentIDList(nodedata.id)
        return scrolllist



    def GroupCreateEntry(self, id, sublevel):
        (note, id,) = (self.folders[id[1]], id[1])
        import types
        if type(note.label) == types.UnicodeType:
            groupID = ('quickbar', id)
            data = {'GetSubContent': self.GetGroupSubContent,
             'label': note.label,
             'id': groupID,
             'groupItems': self.GroupGetContentIDList(groupID),
             'iconMargin': 18,
             'showlen': 0,
             'state': 0,
             'sublevel': sublevel,
             'BlockOpenWindow': 1,
             'parent': note.parent,
             'MenuFunction': self.GroupMenu,
             'ChangeLabel': self.GroupChangeLabel,
             'DeleteFolder': self.GroupDeleteFolder,
             'selected': 1,
             'DropData': self.GroupDropNode,
             'hideNoItem': self.selectFolder,
             'selectGroup': 1}
            if self.selectFolder:
                data['OnDblClick'] = self.OnDblClick
                if data.get('sublevel', 0) + self.depth >= self.maxdepth:
                    return []
            return listentry.Get('Group', data)
        if type(note.label) == types.IntType:
            groupID = ('quickbar', id)
            data = {'label': cfg.invtypes.Get(note.label).name,
             'typeID': note.label,
             'id': groupID,
             'itemID': None,
             'getIcon': 0,
             'sublevel': sublevel,
             'showinfo': 1,
             'GetMenu': self.GetQuickItemMenu,
             'DropData': self.GroupDropNode,
             'parent': note.parent,
             'selected': 1,
             'invtype': cfg.invtypes.Get(note.label)}
            return listentry.Get('QuickbarItem', data)
        del self.folders[id]



    def OnDblClick(self, *args):
        pass



    def GroupGetContentIDList(self, id):
        ids = self.GetItems(id[1])
        test = [ (self.folders[id].label, id) for id in ids ]
        return test



    def GetItems(self, parent):
        dict = {}
        for id in self.folders:
            if self.folders[id].parent == parent:
                dict[id] = self.folders[id]

        return dict



    def NewFolderClick(self, *args):
        self.NewFolder(0)



    def GroupChangeLabel(self, id, newname):
        self.RenameFolder(id[1], name=newname)



    def RenameFolder(self, folderID = 0, entry = None, name = None, *args):
        if name is None:
            ret = uix.NamePopup(mls.UI_GENERIC_FOLDERNAME, mls.UI_SHARED_TYPENEWFOLDERNAME, maxLength=20)
            if ret is None:
                return self.folders[folderID].label
            name = ret['name']
        self.folders[folderID].label = name
        sm.ScatterEvent('OnMarketQuickbarChange')
        return name



    def NewFolder(self, folderID = 0, node = None, *args):
        ret = uix.NamePopup(mls.UI_GENERIC_FOLDERNAME, mls.UI_SHARED_TYPEFOLDERNAME, maxLength=20)
        if ret is not None:
            self.lastid += 1
            n = util.KeyVal()
            n.parent = folderID
            n.id = self.lastid
            n.label = ret['name']
            self.folders[n.id] = n
            settings.user.ui.Set('quickbar', self.folders)
            settings.user.ui.Set('quickbar_lastid', self.lastid)
            sm.ScatterEvent('OnMarketQuickbarChange')
            return n



    def GroupDeleteFolder(self, id):
        import types
        noteID = id[1]
        notes = self.GetItems(noteID)
        for (id, note,) in notes.items():
            if type(note.label) == types.UnicodeType:
                self.GroupDeleteFolder((0, id))
                continue
            self.DeleteFolderNote(id)

        self.DeleteFolderNote(noteID)
        sm.ScatterEvent('OnMarketQuickbarChange')



    def DeleteFolderNote(self, noteID):
        del self.folders[noteID]



    def GroupDropNode(self, id, nodes):
        for node in nodes:
            if node.__guid__ == 'listentry.QuickbarItem':
                noteID = node.id[1]
                if noteID in self.folders:
                    for (folderID, data,) in self.folders.items():
                        if not data.label == node.itemID:
                            self.folders[noteID].parent = id[1]


        sm.ScatterEvent('OnMarketQuickbarChange')



    def ShouldShowType(self, typeID):
        filterSkills = settings.user.ui.Get('showonlyskillsfor', 0)
        filterCpuPower = settings.user.ui.Get('showhavecpuandpower', 0)
        filterKnownSkills = settings.user.ui.Get('shownewskills', 0)
        doesMeetReq = True
        if filterSkills or filterCpuPower or filterKnownSkills:
            currShip = sm.StartService('godma').GetItem(eve.session.shipid)
            invtype = cfg.invtypes.Get(typeID)
            (doesMeetReq, hasSkills, hasPower, hasCpu, hasSkill,) = self.MeetsRequirements(invtype, ship=currShip, reqTypeSkills=filterSkills, reqTypeCpuPower=filterCpuPower, hasSkill=filterKnownSkills)
        return doesMeetReq



    def FilterItemsForBrowse(self, marketGroupInfo):
        filterNone = settings.user.ui.Get('showonlyavailable', 0)
        ret = []
        for typeID in marketGroupInfo.types:
            ask = self.asksForMyRange.get(typeID, None)
            if (not filterNone or ask) and self.ShouldShowType(typeID):
                ret.append(typeID)

        return ret



    def FilterItemsForGroupPage(self, marketGroupInfo):
        filterNone = settings.user.ui.Get('showonlyavailable', 0)
        marketSvc = sm.StartService('marketQuote')
        ret = []
        for typeID in marketGroupInfo.types:
            data = None
            ask = self.asksForMyRange.get(typeID, None)
            if ask is None and filterNone:
                continue
            shouldShow = self.ShouldShowType(typeID)
            if not shouldShow:
                continue
            data = util.KeyVal()
            data.typeID = typeID
            data.price = getattr(ask, 'price', 0)
            data.qty = getattr(ask, 'volRemaining', 0)
            data.fmt_price = util.FmtISK(data.price) if data.price else mls.UI_MARKET_NONEAVAIL
            data.fmt_qty = util.FmtAmt(data.qty) if data.qty else '0'
            data.jumps = marketSvc.GetStationDistance(ask.stationID, False) if ask else None
            ret.append(data)

        return ret



    def MeetsRequirements(self, invType, ship = None, reqTypeSkills = 0, reqTypeCpuPower = 0, hasSkill = 0):
        haveReqSkill = True
        haveReqPower = True
        haveReqCpu = True
        haveSkillAlready = True
        typeID = invType.typeID
        if hasSkill:
            isSkill = invType.categoryID == const.categorySkill
            if isSkill:
                if self.mine.get(typeID, None) is not None:
                    haveSkillAlready = False
        if reqTypeSkills:
            requiredSkills = sm.GetService('info').GetRequiredSkills(typeID)
            if requiredSkills:
                for (skillID, level,) in requiredSkills:
                    if skillID not in self.mine or self.mine[skillID] < level:
                        haveReqSkill = False
                        break

            else:
                haveReqSkill = True
        if reqTypeCpuPower:
            havePower = 0
            haveCpu = 0
            isHardware = invType.Group().Category().IsHardware()
            if isHardware:
                powerEffect = None
                powerIdx = None
                powerEffects = [const.effectHiPower, const.effectMedPower, const.effectLoPower]
                for effect in cfg.dgmtypeeffects.get(typeID, []):
                    if effect.effectID in powerEffects:
                        powerEffect = cfg.dgmeffects.Get(effect.effectID)
                        powerIdx = powerEffects.index(effect.effectID)
                        break

                powerLoad = 0
                cpuLoad = 0
                shipID = util.GetActiveShip()
                if shipID is not None and powerIdx is not None:
                    dgmAttr = sm.GetService('godma').GetType(typeID)
                    for attribute in dgmAttr.displayAttributes:
                        if attribute.attributeID in (const.attributeCpuLoad, const.attributeCpu):
                            cpuLoad += attribute.value
                        elif attribute.attributeID in (const.attributePowerLoad, const.attributePower):
                            powerLoad += attribute.value

                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    havePower = dogmaLocation.GetAttributeValue(shipID, const.attributePowerOutput) > powerLoad
                    haveCpu = dogmaLocation.GetAttributeValue(shipID, const.attributeCpuOutput) > cpuLoad
                if powerEffect:
                    haveReqPower = havePower
                    haveReqCpu = haveCpu
        meetsReq = haveReqSkill and haveReqPower and haveReqCpu and haveSkillAlready
        return (meetsReq,
         haveReqSkill,
         haveReqPower,
         haveReqCpu,
         haveSkillAlready)



    def LoadSettingsTab(self):
        if not getattr(self, 'settingsInited', 0):
            self.settingsInited = 1
            parent = self.sr.settingsparent
            uix.Flush(self.sr.settingsparent)
            details = uicls.Container(name='settings', align=uiconst.TOALL, parent=parent, padding=(0,
             const.defaultPadding,
             0,
             const.defaultPadding))
            self.sr.buttonPar = uicls.Container(name='buttonParent', align=uiconst.TOBOTTOM, height=20, parent=details)
            uicls.Frame(parent=details, idx=0)
            uix.GetContainerHeader('%s - %s' % (mls.UI_GENERIC_FILTERINGOPTIONS, mls.UI_MARKET_FILTERS_APPLY_TO_DETAILS), details, 0)
            uicls.Container(name='push', align=uiconst.TOLEFT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TORIGHT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=4, parent=details)
            boxes = [(12,
              mls.UI_GENERIC_PRICE,
              'market_filter_price',
              settings.user.ui.Get('market_filter_price', 0) == 1,
              settings.user.ui.Get('market_filter_price', 0),
              None,
              [0, 9223372036854L],
              None,
              True), (12,
              mls.UI_GENERIC_JUMPS,
              'market_filter_jumps',
              settings.user.ui.Get('market_filter_jumps', 0) == 1,
              settings.user.ui.Get('market_filter_jumps', 0),
              None,
              [0, None],
              None,
              False), (12,
              mls.UI_GENERIC_QUANTITY,
              'market_filter_quantity',
              settings.user.ui.Get('market_filter_quantity', 0) == 1,
              settings.user.ui.Get('market_filter_quantity', 0),
              None,
              [0, None],
              None,
              False)]
            self.OnChangeFuncs['market_filter_price_min'] = self.OnChange_minEdit_market_filter_price
            self.OnChangeFuncs['market_filter_price_max'] = self.OnChange_maxEdit_market_filter_price
            self.OnChangeFuncs['market_filter_jumps_min'] = self.OnChange_minEdit_market_filter_jump
            self.OnChangeFuncs['market_filter_jumps_max'] = self.OnChange_maxEdit_market_filter_jumps
            self.OnChangeFuncs['market_filter_quantity_min'] = self.OnChange_minEdit_market_filter_quantity
            self.OnChangeFuncs['market_filter_quantity_max'] = self.OnChange_maxEdit_market_filter_quantity
            self.CheckboxRange(boxes, details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            boxes = [(12,
              mls.UI_MARKET_FILTERS_SELLDEV,
              'market_filters_sellorderdev',
              settings.user.ui.Get('market_filters_sellorderdev', 0) == 1,
              settings.user.ui.Get('market_filters_sellorderdev', 0),
              None,
              [-100, None],
              mls.UI_MARKET_FILTERS_DEV_TOOLTIP_SELL,
              False), (12,
              mls.UI_MARKET_FILTERS_BUYDEV,
              'market_filters_buyorderdev',
              settings.user.ui.Get('market_filters_buyorderdev', 0) == 1,
              settings.user.ui.Get('market_filters_buyorderdev', 0),
              None,
              [-100, None],
              mls.UI_MARKET_FILTERS_DEV_TOOLTIP_BUY,
              False)]
            self.OnChangeFuncs['market_filters_sellorderdev_min'] = self.OnChange_minEdit_market_filters_sellorderdev
            self.OnChangeFuncs['market_filters_sellorderdev_max'] = self.OnChange_maxEdit_market_filters_sellorderdev
            self.OnChangeFuncs['market_filters_buyorderdev_min'] = self.OnChange_minEdit_market_filters_buyorderdev
            self.OnChangeFuncs['market_filters_buyorderdev_max'] = self.OnChange_maxEdit_market_filters_buyorderdev
            self.CheckboxRange(boxes, details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            boxes = [(12,
              mls.UI_MARKET_FILTERS_HIGH_SEC,
              'market_filter_highsec',
              settings.user.ui.Get('market_filter_highsec', 0) == 1,
              settings.user.ui.Get('market_filter_highsec', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_HIGHSEC_TOOLTIP), (12,
              mls.UI_MARKET_FILTERS_LOW_SEC,
              'market_filter_lowsec',
              settings.user.ui.Get('market_filter_lowsec', 0) == 1,
              settings.user.ui.Get('market_filter_lowsec', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_LOWSEC_TOOLTIP), (12,
              mls.UI_MARKET_FILTERS_ZERO_SEC,
              'market_filter_zerosec',
              settings.user.ui.Get('market_filter_zerosec', 0) == 1,
              settings.user.ui.Get('market_filter_zerosec', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_ZEROSEC_TOOLTIP)]
            for (height, label, configname, retval, checked, groupname, hasRange, hint,) in boxes:
                box = uicls.Container(name='checkbox_%s' % configname, parent=details, align=uiconst.TOTOP)
                cb = uicls.Checkbox(text='%s' % label, parent=box, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChangeSett, align=uiconst.TOPLEFT, pos=(0, 0, 400, 0))
                box.height = cb.height

            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            uix.GetContainerHeader(mls.UI_SYSMENU_ADVANCEDSETTINGS, details, xmargin=-6)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            boxes = [(12,
              mls.UI_MARKET_FILTERS_BY_SKILLS,
              'showonlyskillsfor',
              settings.user.ui.Get('showonlyskillsfor', 0) == 1,
              settings.user.ui.Get('showonlyskillsfor', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_BYSKILLS_TOOLTIP), (12,
              mls.UI_MARKET_FILTERS_BY_CPUPOWER,
              'showhavecpuandpower',
              settings.user.ui.Get('showhavecpuandpower', 0) == 1,
              settings.user.ui.Get('showhavecpuandpower', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_BYCPUPOWER_TOOLTIP), (12,
              mls.UI_MARKET_FILTERS_NEWSKILLS,
              'shownewskills',
              settings.user.ui.Get('shownewskills', 0) == 1,
              settings.user.ui.Get('shownewskills', 0),
              None,
              False,
              mls.UI_MARKET_FILTERS_NEWSKILLS_TOOLTIP)]
            for (height, label, configname, retval, checked, groupname, hasRange, hint,) in boxes:
                box = uicls.Container(name='checkbox_%s' % configname, parent=details, align=uiconst.TOTOP)
                cb = uicls.Checkbox(text='%s' % label, parent=box, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChange, align=uiconst.TOPLEFT, pos=(0, 0, 400, 0))
                box.height = cb.height
                if hint:
                    cb.hint = hint

            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            boxes = [(12,
              mls.UI_MARKET_AUTOREFRESH,
              'autorefresh',
              settings.user.ui.Get('autorefresh', 0) == 1,
              settings.user.ui.Get('autorefresh', 0),
              None,
              False,
              '')]
            for (height, label, configname, retval, checked, groupname, hasRange, hint,) in boxes:
                box = uicls.Container(name='checkbox_%s' % configname, parent=details, align=uiconst.TOTOP)
                cb = uicls.Checkbox(text='%s' % label, parent=box, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChange, align=uiconst.TOPLEFT, pos=(0, 0, 400, 0))
                box.height = cb.height
                if hint:
                    cb.hint = hint

            self.buttons = [(mls.UI_SYSMENU_RESETSETTINGS,
              self.ResetSettings,
              (),
              84), (mls.UI_MARKET_RESET_QUICKBAR,
              self.ResetQuickbar,
              (),
              84)]
            self.sr.buttonWnd = uicls.ButtonGroup(btns=self.buttons, parent=self.sr.buttonPar, unisize=1)
            self.sr.resetSettings = self.sr.buttonWnd.GetBtnByLabel(mls.UI_SYSMENU_RESETSETTINGS)
            self.sr.resetQuickbar = self.sr.buttonWnd.GetBtnByLabel(mls.UI_MARKET_RESET_QUICKBAR)
            self.settingsInited = 0



    def OnChange_minEdit_market_filter_price(self, value, *args):
        newValue = self.ConvertInput(value, 2)
        settings.user.ui.Set('minEdit_market_filter_price', newValue)



    def OnChange_maxEdit_market_filter_price(self, value, *args):
        newValue = self.ConvertInput(value, 2)
        settings.user.ui.Set('maxEdit_market_filter_price', newValue)



    def OnChange_minEdit_market_filter_jump(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filter_jumps', newValue)



    def OnChange_maxEdit_market_filter_jumps(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filter_jumps', newValue)



    def OnChange_minEdit_market_filter_quantity(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filter_quantity', newValue)



    def OnChange_maxEdit_market_filter_quantity(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filter_quantity', newValue)



    def OnChange_minEdit_market_filters_sellorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', newValue)



    def OnChange_maxEdit_market_filters_sellorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', newValue)



    def OnChange_minEdit_market_filters_buyorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', newValue)



    def OnChange_maxEdit_market_filters_buyorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', newValue)



    def ConvertInput(self, value, numDecimals = None):
        if not value:
            value = 0
        value = self.ConvertToPoint(value, numDecimals)
        return value



    def FiltersInUse1(self):
        filterUsed = False
        browseFilters = [(mls.UI_MARKET_SHOWONLYAVAIL, 'showonlyavailable'),
         (mls.UI_MARKET_FILTERS_BY_SKILLS, 'showonlyskillsfor'),
         (mls.UI_MARKET_FILTERS_BY_CPUPOWER, 'showhavecpuandpower'),
         (mls.UI_MARKET_FILTERS_NEWSKILLS, 'shownewskills')]
        retBrowse = ''
        for (label, filter,) in browseFilters:
            if settings.user.ui.Get('%s' % filter, 0):
                filterUsed = True
                temp = '%s<br>' % label
                retBrowse += temp

        if retBrowse == '' and not settings.user.ui.Get('showonlyavailable', 0):
            temp = '%s<br>' % mls.UI_STATION_SHOWALL
            retBrowse += temp
        if retBrowse:
            retBrowse = '<B>%s</B><br>%s' % (mls.UI_MARKET_FILTERS_BROWSE, retBrowse)
            retBrowse = retBrowse[:-1]
        return (retBrowse, filterUsed)



    def FiltersInUse2(self, *args):
        ret = ''
        jumpFilter = [(mls.UI_GENERIC_JUMPS, 'market_filter_jumps')]
        detailFilters = [(mls.UI_GENERIC_QUANTITY, 'market_filter_quantity'),
         (mls.UI_GENERIC_PRICE, 'market_filter_price'),
         (mls.UI_MARKET_FILTERS_SELLDEV, 'market_filters_sellorderdev'),
         (mls.UI_MARKET_FILTERS_BUYDEV, 'market_filters_buyorderdev')]
        secFilters = [(mls.UI_MARKET_FILTERS_NOHIGHSEC, 'market_filter_highsec'), (mls.UI_MARKET_FILTERS_NOLOWSEC, 'market_filter_lowsec'), (mls.UI_MARKET_FILTERS_NOZEROSEC, 'market_filter_zerosec')]
        retJump = ''
        for (label, filter,) in jumpFilter:
            if settings.user.ui.Get('%s' % filter, 0):
                min = float(settings.user.ui.Get('minEdit_%s' % filter, 0))
                max = float(settings.user.ui.Get('maxEdit_%s' % filter, 0))
                andUp = False
                if min > max:
                    andUp = True
                temp = '%s, %s: %s %s <br>' % (label,
                 mls.UI_GENERIC_FROMNUMBER,
                 settings.user.ui.Get('minEdit_%s' % filter, 0),
                 ['%s: %s' % (mls.UI_GENERIC_TONUMBER, int(max)), mls.UI_MARKET_ANDUP][andUp])
                retJump += temp

        retDetail = retJump
        for (label, filter,) in detailFilters:
            if settings.user.ui.Get('%s' % filter, 0):
                min = float(settings.user.ui.Get('minEdit_%s' % filter, 0))
                max = float(settings.user.ui.Get('maxEdit_%s' % filter, 0))
                andUp = False
                if min >= max:
                    andUp = True and filter not in ('market_filters_sellorderdev', 'market_filters_buyorderdev')
                temp = '%s, %s: %s %s <br>' % (label,
                 mls.UI_GENERIC_FROMNUMBER,
                 min,
                 ['%s: %s' % (mls.UI_GENERIC_TONUMBER, max), mls.UI_MARKET_ANDUP][andUp])
                retDetail += temp

        if retDetail:
            retDetail = '<B>%s</B><br>%s' % (mls.UI_MARKET_FILTERS_DETAIL, retDetail)
        retSecurity = ''
        for (label, filter,) in secFilters:
            if not settings.user.ui.Get('%s' % filter, 0):
                temp = '%s<br>' % label
                retSecurity += temp

        if retSecurity:
            retSecurity = '<B>%s</B><br>%s' % (mls.UI_MARKET_FILTERS_SECURITY, retSecurity)
        for each in [retDetail, retSecurity]:
            if each:
                ret += '%s<br>' % each

        if ret:
            ret = ret[:-1]
        return ret



    def CheckboxRange(self, boxes, container):
        for (height, label, configname, retval, checked, groupname, numRange, hint, isFloat,) in boxes:
            box = uicls.Container(name='checkbox_%s' % configname, parent=container, align=uiconst.TOTOP)
            rbox = uicls.Container(name='checkbox_%s' % configname, parent=box, align=uiconst.TORIGHT, width=180)
            cb = uicls.Checkbox(text='%s' % label, parent=box, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChangeSett, align=uiconst.CENTERLEFT, pos=(0, 0, 150, 0))
            if numRange:
                funcKey = '%s_min' % configname
                minText = uicls.Label(text=mls.UI_GENERIC_FROMNUMBER, parent=rbox, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                if not isFloat:
                    minEdit = uicls.SinglelineEdit(name='minEdit_%s' % configname, setvalue=settings.user.ui.Get('minEdit_%s' % configname, 0), parent=rbox, pos=(minText.left + minText.textwidth + const.defaultPadding,
                     0,
                     68,
                     0), maxLength=32, align=uiconst.TOPLEFT, ints=[numRange[0], numRange[1]], OnChange=self.OnChangeFuncs[funcKey])
                else:
                    minEdit = uicls.SinglelineEdit(name='minEdit_%s' % configname, setvalue=settings.user.ui.Get('minEdit_%s' % configname, 0), parent=rbox, pos=(minText.left + minText.textwidth + const.defaultPadding,
                     0,
                     68,
                     0), maxLength=32, align=uiconst.TOPLEFT, floats=[numRange[0], numRange[1], 2], OnChange=self.OnChangeFuncs[funcKey])
                funcKey = '%s_max' % configname
                maxText = uicls.Label(text=mls.UI_GENERIC_TONUMBER, parent=rbox, left=minEdit.left + minEdit.width + const.defaultPadding, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                if not isFloat:
                    maxEdit = uicls.SinglelineEdit(name='maxEdit_%s' % configname, setvalue=settings.user.ui.Get('maxEdit_%s' % configname, 0), parent=rbox, pos=(maxText.left + maxText.textwidth + const.defaultPadding,
                     0,
                     68,
                     0), maxLength=32, align=uiconst.TOPLEFT, ints=[numRange[0], numRange[1]], OnChange=self.OnChangeFuncs[funcKey])
                else:
                    maxEdit = uicls.SinglelineEdit(name='maxEdit_%s' % configname, setvalue=settings.user.ui.Get('maxEdit_%s' % configname, 0), parent=rbox, pos=(maxText.left + maxText.textwidth + const.defaultPadding,
                     0,
                     68,
                     0), maxLength=32, align=uiconst.TOPLEFT, floats=[numRange[0], numRange[1], 2], OnChange=self.OnChangeFuncs[funcKey])
                rbox.width = maxEdit.left + maxEdit.width + const.defaultPadding
                box.height = rbox.height = max(cb.height, minEdit.height + 2 * minEdit.top, maxEdit.height + 2 * maxEdit.top)
            uicls.Container(name='push', height=const.defaultPadding, parent=container, align=uiconst.TOTOP)
            if hint:
                cb.hint = hint




    def SetupFilters(self):
        settings.user.ui.Set('showonlyavailable', settings.user.ui.Get('showonlyavailable', True))
        settings.user.ui.Set('showonlyskillsfor', settings.user.ui.Get('showonlyskillsfor', False))
        settings.user.ui.Set('showhavecpuandpower', settings.user.ui.Get('showhavecpuandpower', False))
        settings.user.ui.Set('shownewskills', settings.user.ui.Get('shownewskills', False))
        settings.user.ui.Set('market_filter_price', settings.user.ui.Get('market_filter_price', False))
        settings.user.ui.Set('minEdit_market_filter_price', settings.user.ui.Get('minEdit_market_filter_price', 0))
        settings.user.ui.Set('maxEdit_market_filter_price', settings.user.ui.Get('maxEdit_market_filter_price', 100000))
        settings.user.ui.Set('market_filter_jumps', settings.user.ui.Get('market_filter_jumps', False))
        settings.user.ui.Set('minEdit_market_filter_jumps', settings.user.ui.Get('minEdit_market_filter_jumps', 0))
        settings.user.ui.Set('maxEdit_market_filter_jumps', settings.user.ui.Get('maxEdit_market_filter_jumps', 20))
        settings.user.ui.Set('market_filter_quantity', settings.user.ui.Get('market_filter_quantity', False))
        settings.user.ui.Set('minEdit_market_filter_quantity', settings.user.ui.Get('minEdit_market_filter_quantity', 0))
        settings.user.ui.Set('maxEdit_market_filter_quantity', settings.user.ui.Get('maxEdit_market_filter_quantity', 1000))
        settings.user.ui.Set('market_filter_zerosec', settings.user.ui.Get('market_filter_zerosec', True))
        settings.user.ui.Set('market_filter_lowsec', settings.user.ui.Get('market_filter_lowsec', True))
        settings.user.ui.Set('market_filter_highsec', settings.user.ui.Get('market_filter_highsec', True))
        settings.user.ui.Set('market_filters_sellorderdev', settings.user.ui.Get('market_filters_sellorderdev', False))
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', settings.user.ui.Get('minEdit_market_filters_sellorderdev', 0))
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', settings.user.ui.Get('maxEdit_market_filters_sellorderdev', 0))
        settings.user.ui.Set('market_filters_buyorderdev', settings.user.ui.Get('market_filters_buyorderdev', False))
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', settings.user.ui.Get('minEdit_market_filters_buyorderdev', 0))
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', settings.user.ui.Get('maxEdit_market_filters_buyorderdev', 0))
        settings.user.ui.Set('quickbar', settings.user.ui.Get('quickbar', {}))
        settings.user.ui.Set('autorefresh', settings.user.ui.Get('autorefresh', True))



    def AddGroupParent(self, nodedata = None, newitems = 0):
        marketGroupID = None
        self.parentDictionary = {}
        if nodedata:
            marketGroupID = nodedata.marketGroupInfo.marketGroupID
        firstID = self.InsertQuickbarGroupItem(nodedata.marketGroupInfo.marketGroupName, 0)
        self.parentDictionary[marketGroupID] = self.tempLastid
        scrolllist = self.AddGroupChildren(nodedata=nodedata)
        self.test = xtriui.QuickbarEntries()
        depth = self.test.Load(contentList=scrolllist, maxDepth=5, parentDepth=nodedata.sublevel)
        self.test.Close()
        return (depth, firstID)



    def AddGroupChildren(self, nodedata = None):
        scrolllist = []
        if nodedata and nodedata.marketGroupInfo.hasTypes:
            parent = self.parentDictionary.get(nodedata.marketGroupInfo.marketGroupID, 0)
            for typeID in nodedata.typeIDs:
                self.InsertQuickbarGroupItem(typeID, parent)

        else:
            marketGroupID = None
            level = 0
            if nodedata:
                marketGroupID = nodedata.marketGroupInfo.marketGroupID
                level = nodedata.sublevel + 1
            grouplist = sm.GetService('marketutils').GetMarketGroups()[marketGroupID]
            for marketGroupInfo in grouplist:
                if not len(marketGroupInfo.types):
                    continue
                if self.destroyed:
                    return 
                items = [ typeID for typeID in marketGroupInfo.types ]
                groupID = (marketGroupInfo.marketGroupName, marketGroupInfo.marketGroupID)
                data = {'GetSubContent': self.AddGroupChildren,
                 'id': groupID,
                 'typeIDs': items,
                 'marketGroupInfo': marketGroupInfo,
                 'sublevel': level}
                parent = self.parentDictionary.get(marketGroupInfo.parentGroupID, 0)
                self.InsertQuickbarGroupItem(marketGroupInfo.marketGroupName, parent)
                self.parentDictionary[marketGroupInfo.marketGroupID] = self.tempLastid
                scrolllist.append(((marketGroupInfo.hasTypes, marketGroupInfo.marketGroupName.lower()), listentry.Get('Group', data)))

        return scrolllist



    def InsertQuickbarGroupItem(self, label, parent):
        self.tempLastid += 1
        n = util.KeyVal()
        n.parent = parent
        n.id = self.tempLastid
        n.label = label
        self.tempFolders[n.id] = n
        return n.id



    def ListWnd(self, lst, listtype = None, caption = None, hint = None, ordered = 0, minw = 200, minh = 256, minChoices = 1, maxChoices = 1, initChoices = [], validator = None, isModal = 1, scrollHeaders = [], iconMargin = 0, contentList = None):
        if caption is None:
            caption = mls.UI_MARKET_QUICKBAR_SELECTFOLDER
        import form
        if not isModal:
            wnd = sm.GetService('window').GetWindow('listwindow')
            if wnd:
                wnd.SelfDestruct()
        wnd = sm.GetService('window').GetWindow('listwindow', create=1, decoClass=form.SelectFolderWindow, lst=[], listtype=listtype, ordered=ordered, minw=minw, minh=minh, caption=caption, minChoices=minChoices, maxChoices=maxChoices, initChoices=initChoices, validator=validator, scrollHeaders=scrollHeaders, iconMargin=iconMargin)
        wnd.scroll.Load(contentList=contentList)
        wnd.Error(wnd.GetError(checkNumber=0))
        if hint:
            wnd.SetHint('<center>' + hint)
        if isModal:
            wnd.DefineButtons(uiconst.OKCANCEL)
            if wnd.ShowModal() == uiconst.ID_OK:
                return wnd.result
            else:
                return 
        else:
            wnd.DefineButtons(uiconst.CLOSE)
            wnd.Maximize()



    def ConvertToPoint(self, value, numDigits = 0):
        ret = uiutil.ConvertDecimal(value, ',', '.', numDigits)
        if numDigits is not None:
            ret = '%.*f' % (numDigits, float(ret))
        return ret




class MarketGroup(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.MarketGroup'

    def Startup(self, *args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        left = uicls.Container(name='leftside', parent=self, align=uiconst.TOLEFT, width=70)
        right = uicls.Container(name='rightside', parent=self, align=uiconst.TOLEFT, width=8)
        self.sr.textarea = uicls.Edit(setvalue='', parent=self, readonly=1, hideBackground=1)



    def PreLoad(node):
        if not node.Get('loaded', 0):
            invtype = cfg.invtypes.Get(node.ask.typeID)
            jump = ''
            if node.ask.qty and node.marketRange != 0:
                jumps = int(node.ask.jumps)
                if jumps == 0:
                    jump = ' %s' % mls.UI_MARKET_INTHISSYSTEM
                else:
                    jump = ', %s' % [mls.UI_MARKET_JUMPAWAY, mls.UI_MARKET_JUMPSAWAY][(node.ask.jumps > 1)] % {'jumps': node.ask.jumps}
            where = [mls.UI_GENERIC_STATION, mls.UI_GENERIC_SOLARSYSTEMSYSTEM, mls.UI_GENERIC_REGION][node.marketRange]
            html = '\n                <html>\n                <body>\n                <br>\n                <font size=20>%s</font>\n                <br>\n                <font size=10>%s</font>\n                <br><br>\n                <font size=8>%s</font>\n                <br>\n                <font size=20>%s</font>\n                <br>\n                <font size=8>%s%s</font>\n\n                <br>\n                </body>\n                </html>\n                ' % (invtype.name,
             invtype.description.replace('\r\n', '<br>'),
             mls.UI_MARKET_BESTPRICEIN % {'where': where},
             node.ask.fmt_price,
             mls.UI_MARKET_UNITAVAILABLE % {'units': node.ask.fmt_qty},
             jump)
            node.text = html
            node.loaded = 1



    def Load(self, node, *args):
        self.sr.textarea.LoadHTML(node.text, newThread=0)
        node.height = 8 + sum([ each.height for each in self.sr.textarea.sr.content.children ])



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = node.Get('height', 1)
        return node.height



MINSCROLLHEIGHT = 64
LEFTSIDEWIDTH = 90
LABELWIDTH = 110

class MarketData(uicls.Container):
    __guid__ = 'form.MarketData'
    __notifyevents__ = ['OnPathfinderSettingsChange', 'OnSessionChanged']

    def init(self, *args):
        self.name = 'marketQuote'
        self.caption = 'Market Data'
        self.prefs = 'marketquote'
        self.invType = None
        self.loading = None
        self.scrollHeight = 0
        self.buyheaders = [mls.UI_GENERIC_JUMPS,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_PRICE,
         mls.UI_GENERIC_LOCATION,
         mls.UI_GENERIC_EXPIRESIN]
        self.sellheaders = [mls.UI_GENERIC_JUMPS,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_PRICE,
         mls.UI_GENERIC_LOCATION,
         mls.UI_GENERIC_RANGE,
         mls.UI_GENERIC_MINVOLUME,
         mls.UI_GENERIC_EXPIRESIN]
        self.avgSellPrice = None
        self.avgBuyPrice = None
        self.sr.buyParent = uicls.Container(name='buyParent', parent=self, align=uiconst.TOTOP, height=64)
        buyLeft = uicls.Container(name='buyLeft', parent=self.sr.buyParent, align=uiconst.TOTOP, height=20)
        cap = uicls.CaptionLabel(text=mls.UI_MARKET_SELLERS, parent=buyLeft, align=uiconst.RELATIVE, left=4, top=0, width=LEFTSIDEWIDTH)
        buyLeft.height = max(20, cap.textheight + 6)
        a = uicls.Label(text='', parent=buyLeft, left=24, top=3, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.BuyClick
        a.GetMenu = None
        self.buyFiltersActive1 = a
        a = uicls.Label(text='', parent=buyLeft, left=24, top=14, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.BuyClick
        a.GetMenu = None
        self.buyFiltersActive2 = a
        self.sr.buyIcon = uicls.Sprite(name='buyIcon', parent=buyLeft, width=16, height=16, left=6, top=2, align=uiconst.TOPRIGHT)
        self.sr.buyIcon.OnClick = self.BuyClick
        self.sr.buyIcon.state = uiconst.UI_HIDDEN
        btns = [(mls.UI_MARKET_EXPORTTOFILE,
          self.ExportToFile,
          (),
          84), (mls.UI_CMD_PLACEBUYORDER,
          self.PlaceOrder,
          ('buy',),
          84)]
        grp = uicls.ButtonGroup(btns=btns, parent=self, unisize=1)
        divider = xtriui.Divider(name='divider', align=uiconst.TOTOP, height=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.buyParent, 'height', 'y', 64, self.scrollHeight)
        divider.OnSizeChanged = self.OnDetailScrollSizeChanged
        self.sr.divider = divider
        uicls.Line(parent=divider, align=uiconst.TOTOP)
        uicls.Line(parent=divider, align=uiconst.TOBOTTOM)
        self.sr.buyscroll = uicls.Scroll(name='buyscroll', parent=self.sr.buyParent, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.buyscroll.multiSelect = 0
        self.sr.buyscroll.smartSort = 1
        self.sr.buyscroll.ignoreHeaderWidths = 1
        self.sr.buyscroll.sr.id = '%sBuyScroll' % self.prefs
        self.sr.buyscroll.OnColumnChanged = self.OnBuyColumnChanged
        uicls.Container(name='divider', align=uiconst.TOTOP, height=const.defaultPadding, parent=self)
        self.sr.sellParent = uicls.Container(name='sellParent', parent=self, align=uiconst.TOALL)
        sellLeft = uicls.Container(name='sellLeft', parent=self.sr.sellParent, align=uiconst.TOTOP, height=20)
        cap = uicls.CaptionLabel(text=mls.UI_MARKET_BUYERS, parent=sellLeft, align=uiconst.RELATIVE, left=4, top=0, width=LEFTSIDEWIDTH)
        sellLeft.height = max(20, cap.textheight + 6)
        a = uicls.Label(text='', parent=sellLeft, left=24, top=3, fontsize=9, letterspace=2, uppercase=1, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
        a.OnClick = self.SellClick
        a.GetMenu = None
        self.sellFiltersActive1 = a
        a = uicls.Label(text='', parent=sellLeft, left=24, top=14, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.SellClick
        a.GetMenu = None
        self.sellFiltersActive2 = a
        self.sr.sellIcon = uicls.Sprite(name='sellIcon', parent=sellLeft, width=16, height=16, left=6, top=2, align=uiconst.TOPRIGHT)
        self.sr.sellIcon.OnClick = self.SellClick
        self.sr.sellIcon.state = uiconst.UI_HIDDEN
        self.sr.sellscroll = uicls.Scroll(name='sellscroll', parent=self.sr.sellParent, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.sellscroll.multiSelect = 0
        self.sr.sellscroll.smartSort = 1
        self.sr.sellscroll.ignoreHeaderWidths = 1
        self.sr.sellscroll.sr.id = '%sSellScroll' % self.prefs
        self.sr.sellscroll.OnColumnChanged = self.OnSellColumnChanged
        self._OnResize()
        sm.RegisterNotify(self)
        self.inited = 1
        self.sr.buy_ActiveFilters = 1
        self.sr.sell_ActiveFilters = 1



    def OnDetailScrollSizeChanged(self):
        h = self.sr.buyParent.height
        absHeight = self.absoluteBottom - self.absoluteTop
        if h > absHeight - self.height - 64:
            h = absHeight - self.height - 64
            ratio = float(h) / absHeight
            settings.user.ui.Set('detailScrollHeight', ratio)
            self._OnResize()
            return 
        ratio = float(h) / absHeight
        settings.user.ui.Set('detailScrollHeight', ratio)



    def SellClick(self, *args):
        self.sr.sell_ActiveFilters = not self.sr.sell_ActiveFilters
        self.Reload('sell')



    def BuyClick(self, *args):
        self.sr.buy_ActiveFilters = not self.sr.buy_ActiveFilters
        self.Reload('buy')



    def ExportToFile(self, *args):
        if not self.invType:
            return 
        sm.GetService('marketQuote').DumpOrdersForType(self.invType.typeID)



    def OnPathfinderSettingsChange(self, *args):
        self.ReloadType()



    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid' in change:
            self.ReloadType()



    def _OnResize(self, *args):
        if self and not self.destroyed and self.sr.buyParent:
            self.scrollHeight = self.absoluteBottom - self.absoluteTop - 34 - 64
            height = (self.absoluteBottom - self.absoluteTop - 46) / 2
            absHeight = self.absoluteBottom - self.absoluteTop
            ratio = settings.user.ui.Get('detailScrollHeight', 0.5)
            h = int(ratio * absHeight)
            if h > self.scrollHeight:
                h = self.scrollHeight
            self.sr.buyParent.height = max(64, h)
            self.sr.divider.max = self.scrollHeight



    def OnBuyColumnChanged(self, tabstops):
        if self.loading != 'buy':
            self.Reload('buy')



    def OnSellColumnChanged(self, tabstops):
        if self.loading != 'sell':
            self.Reload('sell')



    def PlaceOrder(self, what, *args):
        if not self.invType:
            eve.Message('CustomNotify', {'notify': mls.UI_MARKET_NOTYPETOBUY})
            return 
        if what == 'buy':
            sm.GetService('marketutils').Buy(self.invType.typeID, placeOrder=True)
        elif what == 'sell':
            uicore.cmd.OpenAssets()



    def Reload(self, what):
        records = self.sr.Get('%sItems' % what, None)
        scrollList = []
        scroll = self.sr.Get('%sscroll' % what, None)
        self.loading = what
        headers = [self.buyheaders, self.sellheaders][(what == 'sell')]
        marketUtil = sm.GetService('marketutils')
        funcs = marketUtil.GetFuncMaps()

        def IsOrderASellWithinReach(order):
            return what == 'sell' and (order.jumps <= order.range or eve.session.stationid and order.range == -1 and order.stationID == eve.session.stationid or eve.session.solarsystemid and order.jumps == 0)


        usingFilters = self.GetFilters2()[0]
        foundCounter = 0
        if self.invType and records:
            dataList = []
            scroll.sr.headers = headers
            visibleHeaders = scroll.GetColumns()
            accumPrice = 0
            count = 0
            for order in records[0]:
                data = util.KeyVal()
                data.label = ''
                data.typeID = order.typeID
                data.order = order
                data.mode = what
                accumPrice += order.price * order.volRemaining
                count += order.volRemaining
                data.flag = IsOrderASellWithinReach(order)
                expires = order.issueDate + order.duration * DAY - blue.os.GetTime()
                if expires < 0:
                    continue
                for header in visibleHeaders:
                    funcName = funcs.get(header, None)
                    if funcName and hasattr(marketUtil, funcName):
                        apply(getattr(marketUtil, funcName, None), (order, data))
                    else:
                        log.LogWarn('Unsupported header in record', header, order)
                        data.label += '###<t>'

                self.SetDataValues(order, data)
                data.label = data.label[:-3]
                dataList.append(data)

            avg = None
            if count > 0:
                avg = round(float(accumPrice / count), 2)
            if what == 'sell':
                self.avgSellPrice = avg
            else:
                self.avgBuyPrice = avg
            for data in dataList:
                if self.ApplyDetailFilters(data, self.sr.Get('%s_ActiveFilters' % what, None)):
                    scrollList.append(listentry.Get('MarketOrder', data=data))
                else:
                    foundCounter += 1

        hintText = ''
        if not scrollList:
            if self.invType:
                if (usingFilters or settings.user.ui.Get('market_filters_%sorderdev' % ['buy', 'sell'][(what == 'buy')], 0)) and self.sr.Get('%s_ActiveFilters' % what, None):
                    hintText = mls.UI_MARKET_NOORDERSMATCHED
                else:
                    hintText = mls.UI_MARKET_NOORDERSFOUND
            else:
                hintText = mls.UI_MARKET_NOTYPESELECTED
                self.sr.filtersText.text = ''
                self.sr.filtersText.hint = ''
        scroll.Load(contentList=scrollList, headers=headers, noContentHint=hintText)
        if what == 'buy':
            if usingFilters or settings.user.ui.Get('market_filters_sellorderdev', 0):
                if self.sr.buy_ActiveFilters:
                    text1 = mls.UI_MARKET_FILTER_FOUNDMORE1 % {'num': foundCounter}
                    text2 = mls.UI_MARKET_FILTER_FOUNDMORE2
                else:
                    text1 = mls.UI_MARKET_FILTERS_TURNON
                    text2 = ''
                self.buyFiltersActive1.text = text1
                self.buyFiltersActive2.text = text2
                self.sr.buyIcon.state = uiconst.UI_NORMAL
                self.SetFilterIcon2(self.sr.buyIcon, on=bool(self.sr.buy_ActiveFilters))
            else:
                self.buyFiltersActive1.text = ''
                self.buyFiltersActive2.text = ''
                self.sr.buyIcon.state = uiconst.UI_HIDDEN
        if what == 'sell':
            if usingFilters or settings.user.ui.Get('market_filters_buyorderdev', 0):
                if self.sr.sell_ActiveFilters:
                    text1 = mls.UI_MARKET_FILTER_FOUNDMORE1 % {'num': foundCounter}
                    text2 = mls.UI_MARKET_FILTER_FOUNDMORE2
                else:
                    text1 = mls.UI_MARKET_FILTERS_TURNON
                    text2 = ''
                self.sellFiltersActive1.text = text1
                self.sellFiltersActive2.text = text2
                self.sr.sellIcon.state = uiconst.UI_NORMAL
                self.SetFilterIcon2(self.sr.sellIcon, on=bool(self.sr.sell_ActiveFilters))
            else:
                self.sellFiltersActive1.text = ''
                self.sellFiltersActive2.text = ''
                self.sr.sellIcon.state = uiconst.UI_HIDDEN
        self.loading = None



    def SetFilterIcon2(self, icon, on, *args):
        if on:
            iconNo = 'ui_38_16_205'
        else:
            iconNo = 'ui_38_16_204'
        icon.LoadIcon(iconNo)



    def SetDataValues(self, record, data):
        data.Set('filter_Price', record.price)
        filterJumps = record.jumps
        if record.jumps == 0:
            if record.stationID == session.stationid:
                filterJumps = -1
        data.Set('filter_Jumps', filterJumps)
        data.Set('filter_Quantity', int(record.volRemaining))



    def GetFilters2(self):
        self.filter_jumps_min = int(settings.user.ui.Get('minEdit_market_filter_jumps', 0))
        self.filter_jumps_max = int(settings.user.ui.Get('maxEdit_market_filter_jumps', 0))
        if self.filter_jumps_min == None or self.filter_jumps_min == '':
            self.filter_jumps_min = 0
        if self.filter_jumps_max == None or self.filter_jumps_max == '':
            self.filter_jumps_max = INFINITY
        if self.filter_jumps_min > self.filter_jumps_max:
            self.filter_jumps_max = INFINITY
        self.filter_quantity_min = int(settings.user.ui.Get('minEdit_market_filter_quantity', 0))
        self.filter_quantity_max = int(settings.user.ui.Get('maxEdit_market_filter_quantity', 0))
        if self.filter_quantity_min == None or self.filter_quantity_min == '':
            self.filter_quantity_min = 0
        if self.filter_quantity_max == None or self.filter_quantity_max == '':
            self.filter_quantity_max = INFINITY
        if self.filter_quantity_min >= self.filter_quantity_max:
            self.filter_quantity_max = INFINITY
        self.filter_price_min = float(settings.user.ui.Get('minEdit_market_filter_price', 0))
        self.filter_price_max = float(settings.user.ui.Get('maxEdit_market_filter_price', 0))
        if self.filter_price_min == None or self.filter_price_min == '':
            self.filter_price_min = 0
        if self.filter_price_max == None or self.filter_price_max == '':
            self.filter_price_max = INFINITY
        if self.filter_price_min >= self.filter_price_max:
            self.filter_price_max = INFINITY
        self.ignore_sellorder_min = settings.user.ui.Get('minEdit_market_filters_sellorderdev', 0)
        if self.ignore_sellorder_min == None or self.ignore_sellorder_min == '':
            self.ignore_sellorder_min = 0
        self.ignore_sellorder_max = settings.user.ui.Get('maxEdit_market_filters_sellorderdev', 0)
        if self.ignore_sellorder_max == None or self.ignore_sellorder_max == '':
            self.ignore_sellorder_max = 0
        self.ignore_buyorder_min = settings.user.ui.Get('minEdit_market_filters_buyorderdev', 0)
        if self.ignore_buyorder_min == None or self.ignore_buyorder_min == '':
            self.ignore_buyorder_min = 0
        self.ignore_buyorder_max = settings.user.ui.Get('maxEdit_market_filters_buyorderdev', 0)
        if self.ignore_buyorder_max == None or self.ignore_buyorder_max == '':
            self.ignore_buyorder_max = 0
        filters = [settings.user.ui.Get('market_filter_jumps', 0),
         settings.user.ui.Get('market_filter_quantity', 0),
         settings.user.ui.Get('market_filter_price', 0),
         not settings.user.ui.Get('market_filter_zerosec', 0),
         not settings.user.ui.Get('market_filter_highsec', 0),
         not settings.user.ui.Get('market_filter_lowsec', 0)]
        usingFilters = False
        for each in filters:
            if each:
                usingFilters = True
                break

        return [usingFilters,
         self.filter_jumps_min,
         self.filter_jumps_max,
         self.filter_quantity_min,
         self.filter_quantity_max,
         self.filter_price_min,
         self.filter_price_max,
         self.ignore_sellorder_min,
         self.ignore_sellorder_max,
         self.ignore_buyorder_min,
         self.ignore_buyorder_max]



    def ApplyDetailFilters(self, data, activeFilters = 1):
        if not activeFilters:
            return True
        if settings.user.ui.Get('market_filter_jumps', 0):
            if data.filter_Jumps:
                if self.filter_jumps_min > data.filter_Jumps or self.filter_jumps_max < data.filter_Jumps:
                    if not (self.filter_jumps_min == 0 and data.filter_Jumps == -1):
                        return False
        if settings.user.ui.Get('market_filter_quantity', 0):
            if data.filter_Quantity:
                if self.filter_quantity_min > data.filter_Quantity or self.filter_quantity_max < data.filter_Quantity:
                    return False
        if settings.user.ui.Get('market_filter_price', 0):
            if data.filter_Price:
                if self.filter_price_min > data.filter_Price or self.filter_price_max < data.filter_Price:
                    return False
        secClass = sm.StartService('map').GetSecurityClass(data.order.solarSystemID)
        if secClass == const.securityClassZeroSec:
            if not settings.user.ui.Get('market_filter_zerosec', 0):
                return False
        elif secClass == const.securityClassHighSec:
            if not settings.user.ui.Get('market_filter_highsec', 0):
                return False
        elif not settings.user.ui.Get('market_filter_lowsec', 0):
            return False
        if data.filter_Price:
            if settings.user.ui.Get('market_filters_sellorderdev', 0) and data.mode == 'buy':
                if self.avgBuyPrice:
                    percentage = (data.filter_Price - self.avgBuyPrice) / self.avgBuyPrice
                    if float(self.ignore_sellorder_max) < percentage * 100 or float(self.ignore_sellorder_min) > percentage * 100:
                        return False
            if settings.user.ui.Get('market_filters_buyorderdev', 0) and data.mode == 'sell':
                if self.avgSellPrice:
                    percentage = (data.filter_Price - self.avgSellPrice) / self.avgSellPrice
                    if float(self.ignore_buyorder_max) < percentage * 100 or float(self.ignore_buyorder_min) > percentage * 100:
                        return False
        return True



    def LoadType(self, invType):
        self.invType = invType
        self.ReloadType()



    def OnReload(self):
        self.ReloadType()



    def ReloadType(self, *args):
        if self.invType:
            self.sr.sellscroll.Load(contentList=[], fixedEntryHeight=18, headers=self.sellheaders)
            self.sr.buyscroll.Load(contentList=[], fixedEntryHeight=18, headers=self.buyheaders)
            self.sr.sellscroll.ShowHint(mls.UI_MARKET_FETCHINGORDERS)
            self.sr.buyscroll.ShowHint(mls.UI_MARKET_FETCHINGORDERS)
            (self.sr.buyItems, self.sr.sellItems,) = sm.GetService('marketQuote').GetOrders(self.invType.typeID)
            self.Reload('buy')
            self.Reload('sell')
        else:
            self.sr.sellscroll.Load(contentList=[], fixedEntryHeight=18)
            self.sr.buyscroll.Load(contentList=[], fixedEntryHeight=18)




class MarketOrder(listentry.Generic):
    __guid__ = 'listentry.MarketOrder'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.green = None



    def Load(self, node):
        listentry.Generic.Load(self, node)
        data = self.sr.node
        if data.flag == 1 and data.mode == 'sell':
            self.ShowGreen()
        elif self.sr.green:
            self.sr.green.state = uiconst.UI_HIDDEN



    def ShowGreen(self):
        if self.sr.green is None:
            self.sr.green = uicls.Fill(parent=self, color=(0.0, 1.0, 0.0, 0.25), state=uiconst.UI_DISABLED)
        else:
            self.sr.green.state = uiconst.UI_DISABLED



    def ClickButton(self, *args):
        if self.sr.node.mode == 'buy':
            self.Buy()
        elif self.sr.node.mode == 'sell':
            self.Sell()



    def Buy(self, node = None, ignoreAdvanced = False, *args):
        if not hasattr(self, 'sr'):
            return 
        node = node if node != None else self.sr.node
        sm.GetService('marketutils').Buy(self.sr.node.order.typeID, node.order, 0, ignoreAdvanced=ignoreAdvanced)



    def Sell(self, *args):
        sm.GetService('marketutils').Sell(self.sr.node.order.typeID, self.sr.node.order, 0)



    def ShowInfo(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('info').ShowInfo(node.order.typeID)



    def GetMenu(self):
        self.OnClick()
        m = []
        if self.sr.node.mode == 'buy':
            m.append((mls.UI_CMD_BUYTHIS, self.Buy, (self.sr.node, True)))
        m.append(None)
        m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (self.sr.node,))]
        stationID = self.sr.node.order.stationID
        if stationID:
            stationInfo = sm.GetService('ui').GetStation(stationID)
            m += [(mls.UI_CMD_LOCATION, sm.GetService('menu').CelestialMenu(stationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID, mapItem=None))]
        return m



    def OnDblClick(self, *args):
        self.Buy(ignoreAdvanced=True)




class GenericMarketItem(listentry.Generic):
    __guid__ = 'listentry.GenericMarketItem'

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)



    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes




class QuickbarItem(GenericMarketItem):
    __guid__ = 'listentry.QuickbarItem'

    def Startup(self, *args):
        listentry.GenericMarketItem.Startup(self, *args)



    def Load(self, node):
        listentry.GenericMarketItem.Load(self, node)
        self.sr.sublevel = node.Get('sublevel', 0)
        self.sr.label.left = 12 + max(0, self.sr.sublevel * 16)
        self.sr.label.text = node.label



    def OnClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)



    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 18
        return node.height




class QuickbarEntries(uicls.Container):
    __guid__ = 'xtriui.QuickbarEntries'
    __nonpersistvars__ = []

    def init(self):
        self.sr.nodes = []
        self.tooDeep = False



    def __Load(self, contentList = [], maxDepth = 99, parentDepth = 0):
        if self.destroyed:
            return 
        self.sr.nodes = []
        self.maxDepth = maxDepth
        self.parentDepth = parentDepth
        self.depth = 0
        self.AddEntries(0, contentList)
        if self.destroyed:
            return 
        return [0, self.depth - parentDepth][bool(self.depth)]


    Load = LoadContent = _QuickbarEntries__Load

    def AddEntry(self, idx, entry, update = 0, isSub = 0, fromW = None):
        _idx = idx
        if idx == -1:
            idx = len(self.GetNodes())
        entry.idx = idx
        if not self or not getattr(self, 'sr', None):
            return 
        self.ReloadEntry(entry)
        return entry



    def ReloadEntry(self, entry):
        if entry.id and entry.GetSubContent:
            self.depth = max(self.depth, entry.sublevel)
            subcontent = entry.GetSubContent(entry)
            if self.destroyed:
                return 
            self.AddEntries(entry.idx + 1, subcontent, entry)



    def AddEntries(self, fromIdx, entriesData, parentEntry = None):
        if self.parentDepth > self.maxDepth:
            self.tooDeep = True
            return 
        if fromIdx == -1:
            fromIdx = len(self.GetNodes())
        isSub = 0
        if parentEntry:
            isSub = getattr(parentEntry, 'sublevel', 0) + 1
        entries = []
        idx = fromIdx
        for (crap, data,) in entriesData:
            newentry = self.AddEntry(idx, data, isSub=isSub)
            if newentry is None:
                continue
            idx = newentry.idx + 1
            entries.append(newentry)

        if self.destroyed:
            return 



    def _OnClose(self):
        for each in self.GetNodes():
            each.scroll = None
            each.data = None

        self.sr.nodes = []



    def GetNodes(self):
        return self.sr.nodes




class SelectFolderWindow(form.ListWindow):
    __guid__ = 'form.SelectFolderWindow'

    def GetError(self, checkNumber = 1):
        result = None
        if self.scroll.GetSelected():
            result = [self.scroll.GetSelected()[0].id[1], self.scroll.GetSelected()[0].sublevel]
        if hasattr(self, 'customValidator'):
            ret = self.customValidator and self.customValidator(result) or ''
            if ret:
                return ret
        try:
            if checkNumber:
                if result == None:
                    if self.minChoices == self.maxChoices:
                        label = mls.UI_GENERIC_PICKERROR2B
                    else:
                        label = mls.UI_GENERIC_PICKERROR2A
                    return label % {'num': self.minChoices}
        except ValueError as e:
            log.LogException()
            sys.exc_clear()
            return 
        return ''



    def Confirm(self, *etc):
        if not self.isModal:
            return 
        self.Error(self.GetError(checkNumber=0))
        if not self.GetError():
            if self.scroll.GetSelected():
                if hasattr(self.scroll.GetSelected()[0], 'id'):
                    self.result = [self.scroll.GetSelected()[0].id[1], self.scroll.GetSelected()[0].sublevel]
            self.SetModalResult(uiconst.ID_OK)



    def Error(self, error):
        ep = uiutil.GetChild(self, 'errorParent')
        uix.Flush(ep)
        if error:
            t = uicls.Label(text='<center>' + error, top=-3, parent=ep, width=self.minsize[0] - 32, autowidth=False, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 1.0), align=uiconst.CENTER)
            ep.state = uiconst.UI_DISABLED
            ep.height = t.height + 8
        else:
            ep.state = uiconst.UI_HIDDEN




