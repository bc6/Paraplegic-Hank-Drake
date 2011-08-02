import blue
import xtriui
import form
import uix
import uiutil
import util
import listentry
import uthread
import sys
import base
import service
import draw
import log
import uicls
import uiconst
MINSCROLLHEIGHT = 64
LEFTSIDEWIDTH = 80
LABELWIDTH = 100

class MarketUtils(service.Service):
    __exportedcalls__ = {'Buy': [],
     'Sell': [],
     'ModifyOrder': [],
     'GetMarketGroups': [],
     'GetMarketTypes': [],
     'GetJumps': [],
     'GetPrice': [],
     'GetType': [],
     'GetLocation': [],
     'GetExpiresIn': [],
     'GetQuantity': [],
     'GetMarketRange': [],
     'GetQuantitySlashVolume': [],
     'GetMinVolume': [],
     'GetSolarsystem': [],
     'GetRegion': [],
     'GetConstellation': [],
     'GetRange': [],
     'BuyStationAsk': [service.ROLE_IGB],
     'ShowMarketDetails': [service.ROLE_IGB],
     'MatchOrder': [service.ROLE_IGB],
     'ProcessRequest': [service.ROLE_IGB],
     'StartupCheck': {'role': service.ROLE_ANY,
                      'preargs': ['regionid'],
                      'caching': {'versionCheck': ('1 minute', None, None),
                                  'sessionInfo': 'regionid'},
                      'callhandlerargs': {'PreCall_CachedMethodCall.retainMachoVersion': 1}}}
    __guid__ = 'svc.marketutils'
    __servicename__ = 'Market Utils'
    __displayname__ = 'Market Utils'
    __notifyevents__ = []
    __dependencies__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None
        self.mode = None



    def Run(self, memStream = None):
        self.Reset()



    def Reset(self):
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None



    def StartupCheck(self):
        now = blue.os.GetTime()
        if self.regionUpAt is not None:
            if self.regionUpAt.time < now - 2 * MIN:
                return 
            raise UserError(self.regionUpAt.msg, self.regionUpAt.dict)
        try:
            sm.ProxySvc('marketProxy').StartupCheck()
        except UserError as e:
            if eve.session.role & service.ROLE_GMH == 0:
                self.regionUpAt = util.Row(['time', 'msg', 'dict'], [now, e.msg, e.dict])
            sys.exc_clear()
            raise UserError(e.msg, e.dict)



    def GetMarketRange(self):
        if eve.session.stationid:
            r = settings.user.ui.Get('marketRangeFilterStation', const.rangeStation)
        else:
            r = settings.user.ui.Get('marketRangeFilterSpace', const.rangeRegion)
        return r



    def SetMarketRange(self, value):
        if eve.session.stationid:
            r = settings.user.ui.Set('marketRangeFilterStation', value)
        else:
            r = settings.user.ui.Set('marketRangeFilterSpace', value)
        return r



    def BuyStationAsk(self, typeID):
        if eve.session.stationid:
            asks = sm.GetService('marketQuote').GetStationAsks()
            for ask in asks.itervalues():
                if ask.typeID == typeID:
                    self.Buy(typeID, ask)
                    return 




    def FindMarketGroup(self, typeID, groupInfo = None, trace = None):
        groupInfo = groupInfo or self.GetMarketGroups()[None]
        trace = trace or ''
        for _groupInfo in groupInfo:
            if typeID in _groupInfo.types:
                trace += _groupInfo.marketGroupName.strip() + ' / '
                if not _groupInfo.hasTypes:
                    return self.FindMarketGroup(typeID, self.GetMarketGroups()[_groupInfo.marketGroupID], trace)
                return (_groupInfo, trace)

        return (None, trace)



    def ProcessRequest(self, subMethod, typeID = None, orderID = None):
        if subMethod == 'Buy':
            self.Buy(typeID, orderID)
        elif subMethod == 'ShowMarketDetails':
            self.ShowMarketDetails(typeID, orderID)
        else:
            raise RuntimeError('Unsupported subMethod call. Possible h4x0r attempt.')



    def MatchOrder(self, typeID, orderID):
        order = None
        if orderID:
            order = sm.GetService('marketQuote').GetOrder(orderID, typeID)
        self.Buy(typeID, order, placeOrder=order is None)



    def ShowMarketDetails(self, typeID, orderID):
        marketWnd = sm.GetService('window').GetWindow('market', maximize=1)
        if not marketWnd:
            uicore.cmd.OpenMarket()
        marketWnd = sm.GetService('window').GetWindow('market')
        if marketWnd:
            marketWnd.LoadTypeID_Ext(typeID)



    def GetMarketGroups(self, getall = 0):
        if self.marketgroups is None:
            self.marketgroups = sm.GetService('marketQuote').GetMarketProxy().GetMarketGroups()
            self.allgroups = {}
            translate = prefs.languageID != 'EN'
            for mgID in self.marketgroups.iterkeys():
                for entry in self.marketgroups[mgID]:
                    if translate:
                        entry.marketGroupName = Tr(entry.marketGroupName, 'inventory.marketGroups.marketGroupName', entry.dataID)
                        entry.description = Tr(entry.description, 'inventory.marketGroups.description', entry.dataID)
                    self.allgroups[entry.marketGroupID] = entry


        if getall:
            return self.allgroups
        return self.marketgroups



    def GetMarketTypes(self):
        t = []
        for each in self.GetMarketGroups()[None]:
            t += each.types

        return t



    def GetMarketGroup(self, findMarketGroupID):
        all = self.GetMarketGroups(1)
        return all.get(findMarketGroupID, None)



    def AllowTrade(self, bid, order = None, locationID = None):
        limits = sm.GetService('marketQuote').GetSkillLimits()
        askLimit = limits['ask']
        bidLimit = limits['bid']
        inStation = session.stationid
        if bid:
            if inStation:
                if locationID != session.solarsystemid2:
                    pass
                return True
            if bidLimit == const.rangeStation and order is None:
                raise UserError('CustomError', {'error': mls.UI_MARKET_ERROR1})
        else:
            if not inStation and askLimit == const.rangeStation:
                raise UserError('CustomError', {'error': mls.UI_MARKET_ERROR2})
            return True



    def Buy(self, typeID, order = None, duration = 1, placeOrder = 0, prePickedLocationID = None, ignoreAdvanced = False):
        locationID = None
        self.AllowTrade(1, order)
        if order is None:
            if prePickedLocationID:
                locationID = prePickedLocationID
            elif eve.session.stationid:
                locationID = session.stationid
            elif eve.session.solarsystemid:
                stationData = sm.GetService('marketutils').PickStation()
                if stationData:
                    locationID = stationData[1]
            if locationID is None:
                return 
        sm.GetService('marketutils').StartupCheck()
        if locationID == None and order.stationID != None:
            locationID = order.stationID
        wnd = sm.GetService('window').GetWindow('marketbuyaction', decoClass=form.MarketActionWindow, create=1, maximize=1)
        advancedBuyWnd = settings.char.ui.Get('advancedBuyWnd', 0)
        if uicore.uilib.Key(uiconst.VK_SHIFT) or placeOrder or advancedBuyWnd and not ignoreAdvanced:
            wnd.LoadBuy_Detailed(typeID, order, duration, locationID, forceRange=True)
        elif locationID is not None:
            sm.GetService('marketQuote').RefreshJumps(typeID, locationID)
        wnd.TradeSimple('buy', typeID=typeID, order=order, locationID=locationID, ignoreAdvanced=ignoreAdvanced)



    def Sell(self, typeID, invItem = None, placeOrder = 0):
        self.AllowTrade(0)
        if invItem is None:
            invItem = self.PickItem(typeID)
        if invItem is None:
            return 
        if invItem.singleton:
            raise UserError('RepackageBeforeSelling', {'item': (TYPEID, typeID)})
        retList = []
        stationID = sm.GetService('invCache').GetStationIDOfItem(invItem)
        if stationID is None:
            return 
        if not sm.GetService('marketQuote').CanTradeAtStation(0, stationID, retList):
            jumps = retList[0]
            limit = retList[1]
            if jumps == const.rangeRegion:
                raise UserError('MktInvalidRegion')
            else:
                jumpText = mls.UI_GENERIC_JUMP if jumps == 1 else mls.UI_GENERIC_JUMPS
                limitText = mls.UI_GENERIC_JUMP if limit == 1 else mls.UI_GENERIC_JUMPS
                if limit >= 0:
                    raise UserError('MktCantSellItem2', {'numJumps': jumps,
                     'jumpText1': jumpText,
                     'numLimit': limit,
                     'jumpText2': limitText})
                else:
                    raise UserError('MktCantSellItemOutsideStation', {'numJumps': jumps,
                     'jumpText': jumpText})
        sm.GetService('marketutils').StartupCheck()
        wnd = sm.GetService('window').GetWindow('marketsellaction', decoClass=form.MarketActionWindow, create=1, maximize=1)
        advancedSellWnd = settings.char.ui.Get('advancedSellWnd', 0)
        if uicore.uilib.Key(uiconst.VK_SHIFT) or placeOrder or advancedSellWnd:
            wnd.LoadSell_Detailed(invItem)
        else:
            wnd.TradeSimple('sell', invItem=invItem)



    def ModifyOrder(self, order):
        wnd = sm.GetService('window').GetWindow('marketmodifyaction', decoClass=form.MarketActionWindow, create=1, maximize=1)
        wnd.LoadModify(order)



    def PickStation(self):
        if not session.solarsystemid2:
            return None
        stations = sm.RemoteSvc('stationSvc').GetStationsByRegion(eve.session.regionid)
        quote = sm.GetService('marketQuote')
        limits = quote.GetSkillLimits()
        bidDistance = limits['bid']
        stationsToList = [ each for each in stations if quote.GetStationDistance(each.stationID) <= bidDistance ]
        if len(stationsToList) == 0:
            return None
        for each in stationsToList:
            itemID = each.stationID
            if itemID not in cfg.evelocations:
                staData = [itemID,
                 each.stationName,
                 each.x,
                 each.y,
                 each.z]
                cfg.evelocations.Hint(itemID, staData)

        stationLst = [ (cfg.evelocations.Get(station.stationID).name, station.stationID) for station in stationsToList ]
        station = uix.ListWnd(stationLst, 'generic', mls.UI_MARKET_SELECTSTATION, hint=mls.UI_MARKET_TEXT4, isModal=1, ordered=1)
        if station:
            return station



    def PickItem(self, typeID, quantity = None):
        stations = eve.GetInventory(const.containerGlobal).ListStations()
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        else:
            return None
        stationLst = [ (cfg.evelocations.Get(station.stationID).name + ' (' + str(station.itemCount) + ' items)', station.stationID) for station in stations ]
        station = uix.ListWnd(stationLst, 'generic', mls.UI_MARKET_SELECTSTATION, hint=mls.UI_MARKET_TEXT5, isModal=1)
        if station:
            items = eve.GetInventory(const.containerGlobal).ListStationItems(station[1])
            badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
            valid = []
            for each in items:
                if each.typeID != typeID:
                    continue
                if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                    continue
                if each.stacksize == 0 or each.stacksize < quantity:
                    continue
                valid.append(each)

            if len(valid) == 1:
                return valid[0]
            scrolllist = []
            for each in valid:
                invtype = cfg.invtypes.Get(each.typeID)
                scrolllist.append(('%s<t>%s' % (invtype.name, util.FmtAmt(each.stacksize)), each))

            if not scrolllist:
                if eve.Message('CustomQuestion', {'header': mls.UI_MARKET_TRYANOTHERSTATION,
                 'question': mls.UI_MARKET_TEXT6 % {'type': cfg.invtypes.Get(typeID).name,
                              'station': station[0]}}, uiconst.YESNO) == uiconst.ID_YES:
                    return self.PickItem(typeID, quantity)
                return None
            item = uix.ListWnd(scrolllist, 'generic', mls.UI_MARKET_SELECTITEM, hint=mls.UI_MARKET_TEXT7, isModal=1, scrollHeaders=[mls.UI_GENERIC_TYPE, mls.UI_GENERIC_QUANTITY])
            if item:
                return item[1]



    def GetFuncMaps(self):
        return {mls.UI_GENERIC_TYPE: 'GetType',
         mls.UI_GENERIC_QUANTITY: 'GetQuantity',
         mls.UI_GENERIC_PRICE: 'GetPrice',
         mls.UI_GENERIC_LOCATION: 'GetLocation',
         mls.UI_GENERIC_RANGE: 'GetRange',
         mls.UI_GENERIC_MINVOLUME: 'GetMinVolume',
         mls.UI_GENERIC_EXPIRESIN: 'GetExpiresIn',
         mls.UI_GENERIC_ISSUEDBY: 'GetIssuedBy',
         mls.UI_GENERIC_JUMPS: 'GetJumps',
         mls.UI_GENERIC_WALLETDIVISION: 'GetWalletDivision'}



    def GetJumps(self, record, data):
        sortJumps = record.jumps
        if record.jumps == 0:
            if record.stationID == session.stationid:
                data.label += '%s<t>' % mls.UI_GENERIC_STATION
                sortJumps = -1
            else:
                data.label += '%s<t>' % mls.UI_GENERIC_SOLARSYSTEMSYSTEM
        elif record.jumps == 1000000:
            data.label += '%s<t>' % mls.UI_GENERIC_UNREACHABLE
        else:
            data.label += '<right>%i<t>' % record.jumps
        data.Set('sort_%s' % mls.UI_GENERIC_JUMPS, sortJumps)



    def GetWalletDivision(self, record, data):
        data.label += '%s <t>' % sm.GetService('corp').GetDivisionNames()[(record.keyID - 1000 + 8)]



    def GetPrice(self, record, data):
        data.label += '<right>%s<t>' % util.FmtISK(record.price)
        data.Set('sort_%s' % mls.UI_GENERIC_PRICE, record.price)



    def GetType(self, record, data):
        typeObject = cfg.invtypes.GetIfExists(record.typeID)
        if typeObject is not None:
            data.label += typeObject.name + '<t>'
            data.Set('sort_%s' % mls.UI_GENERIC_TYPE, typeObject.name.lower())
        else:
            data.label += 'Unknown Entity: ' + str(record.typeID) + '<t>'
            data.Set('sort_%s' % mls.UI_GENERIC_TYPE, 'unknown entity: ' + str(record.typeID))



    def GetLocation(self, record, data):
        locationName = cfg.evelocations.Get(record.stationID).name
        data.label += locationName + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_LOCATION, locationName.lower())



    def GetExpiresIn(self, record, data):
        exp = record.issueDate + record.duration * DAY - blue.os.GetTime()
        if exp < 0:
            data.label += '%s<t>' % mls.UI_GENERIC_EXPIRED
        else:
            data.label += util.FmtDate(exp, 'ss') + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_EXPIRESIN, record.issueDate + record.duration * DAY)



    def GetQuantity(self, record, data):
        data.label += '<right>%s<t>' % util.FmtAmt(int(record.volRemaining))
        data.Set('sort_%s' % mls.UI_GENERIC_QUANTITY, int(record.volRemaining))



    def GetQuantitySlashVolume(self, record, data):
        data.label += '<right>%s/%s<t>' % (util.FmtAmt(int(record.volRemaining)), util.FmtAmt(int(record.volEntered)))
        data.Set('sort_%s' % mls.UI_GENERIC_QUANTITY, (int(record.volRemaining), record.volEntered))



    def GetMinVolume(self, record, data):
        vol = int(min(record.volRemaining, record.minVolume))
        data.label += '<right>%s<t>' % util.FmtAmt(vol)
        data.Set('sort_%s' % mls.UI_GENERIC_MINVOLUME, vol)



    def GetSolarsystem(self, record, data):
        solarsystemName = cfg.evelocations.Get(record.solarSystemID).name
        data.label += solarsystemName + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_SOLARSYSTEM, solarsystemName.lower())



    def GetRegion(self, record, data):
        regionName = cfg.evelocations.Get(record.regionID).name
        data.label += regionName + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_REGION, regionName.lower())



    def GetConstellation(self, record, data):
        constellationName = cfg.evelocations.Get(record.constellationID).name
        data.label += constellationName + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_CONSTELLATION, constellationName.lower())



    def GetRange(self, record, data):
        if record.range == const.rangeStation:
            range = mls.UI_GENERIC_STATION
            sortval = 0
        elif record.range == const.rangeSolarSystem:
            range = mls.UI_GENERIC_SOLARSYSTEM
            sortval = 0.5
        elif record.range == const.rangeRegion:
            range = mls.UI_GENERIC_REGION
            sortval = sys.maxint
        else:
            range = uix.Plural(record.range, 'UI_SHARED_NUM_JUMP') % {'num': record.range}
            sortval = record.range
        data.label += range + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_RANGE, sortval)



    def GetIssuedBy(self, record, data):
        name = cfg.eveowners.Get(record.charID).name
        data.label += name + '<t>'
        data.Set('sort_%s' % mls.UI_GENERIC_ISSUEDBY, name.lower())



    def GetFilterops(self, marketGroupID):
        mg = self.GetMarketGroups()
        ret = []
        for level1 in mg[marketGroupID]:
            ret.append((level1.marketGroupName, level1.marketGroupID))

        ret.sort()
        ret.insert(0, (mls.UI_GENERIC_ALL, None))
        return ret



    def GetTypeFilterIDs(self, marketGroupID, checkcategory = 1):
        c = []
        mg = self.GetMarketGroups()[marketGroupID]
        if mg:
            for each in mg:
                for typeID in each.types:
                    invType = cfg.invtypes.Get(typeID)
                    if checkcategory:
                        if invType.categoryID not in c:
                            c.append(invType.categoryID)
                    elif invType.groupID not in c:
                        c.append(invType.groupID)


        else:
            types = cfg.typesByMarketGroups.get(marketGroupID, [])
            for t in types:
                if checkcategory:
                    if t.categoryID not in c:
                        c.append(t.categoryID)
                elif t.groupID not in c:
                    c.append(t.groupID)

        return c



    def GetProducableGroups(self, lineGroups, lineCategs):
        valid = [ group.groupID for group in lineGroups ]
        validcategs = [ categ.categoryID for categ in lineCategs ]
        return (valid, validcategs)



    def GetProducableCategories(self, lineGroups, lineCategs):
        valid = [ categ.categoryID for categ in lineCategs ]
        for group in lineGroups:
            invGroup = cfg.invgroups.Get(group.groupID)
            if invGroup.categoryID not in valid:
                valid.append(invGroup.categoryID)

        return valid




class MarketActionWindow(uicls.Window):
    __guid__ = 'form.MarketActionWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.clipChildren = 1
        self.scope = 'station_inflight'
        self.sr.currentOrder = None
        self.sr.sellItem = None
        self.sr.stationID = None
        self.mode = None
        self.quantity = None
        self.remoteBuyLocation = None
        self.bestAskDict = {}
        self.bestMatchableAskDict = {}
        self.bestBidDict = {}
        self.durations = [[mls.UI_GENERIC_IMMEDIATE, 0],
         [mls.UI_GENERIC_DAY, 1],
         ['3 %s' % mls.UI_GENERIC_DAYS, 3],
         [mls.UI_GENERIC_WEEK, 7],
         ['2 %s' % mls.UI_GENERIC_WEEKS, 14],
         [mls.UI_GENERIC_MONTH, 30],
         ['3 %s' % mls.UI_GENERIC_MONTHS, 90]]
        self.ranges = [[mls.UI_GENERIC_STATION, const.rangeStation],
         [mls.UI_GENERIC_SOLARSYSTEM, const.rangeSolarSystem],
         [mls.UI_GENERIC_REGION, const.rangeRegion],
         [mls.UI_SHARED_NUM_JUMP % {'num': 1}, 1],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 2}, 2],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 3}, 3],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 4}, 4],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 5}, 5],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 10}, 10],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 20}, 20],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 30}, 30],
         [mls.UI_SHARED_NUM_JUMPS % {'num': 40}, 40]]
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([480, 310], 1)
        self.NoSeeThrough()
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding * 2)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        self.bidprice = None
        self.qty = None
        self.min = None
        self.duration = None
        self.range = None
        self.useCorp = None



    def OnClose_(self, *args):
        if self.sr.sellItem:
            sm.StartService('invCache').UnlockItem(self.sr.sellItem.itemID)



    def FlushMain(self, fromObject):
        uiutil.FlushList(self.sr.main.children[fromObject:])



    def LoadBuy_Detailed(self, typeID, order = None, duration = 1, locationID = None, forceRange = False):
        settings.char.ui.Set('advancedBuyWnd', 1)
        self.mode = 'buy'
        self.remoteBuyLocation = None
        if locationID:
            self.remoteBuyLocation = locationID
            location = cfg.evelocations.Get(locationID)
        elif order:
            location = cfg.evelocations.Get(order.stationID)
        setattr(self, 'order', order)
        if location is None:
            return 
        self.sr.stationID = location.locationID
        self.loading = 'buy'
        self.ready = False
        self.FlushMain(4)
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        bestMatchableAsk = quote.GetBestAskInRange(typeID, self.sr.stationID, const.rangeStation, 1)
        if bestMatchableAsk:
            self.sr.hasMatch = True
        else:
            self.sr.hasMatch = False
        self.invType = invType = cfg.invtypes.Get(typeID)
        self.DefineButtons(uiconst.OKCANCEL, okLabel=mls.UI_CMD_BUY, okFunc=self.Buy, cancelFunc=self.Cancel)
        self.SetCaption('%s %s' % (mls.UI_MARKET_BUY, invType.name))
        self.AddSpace(where=self.sr.main)
        self.AddBigText(None, invType.name, typeID=invType.typeID)
        name = location.name
        self.sr.isBuy = True
        if len(name) > 64:
            name = name[:61] + '...'
        locationText = self.AddText(mls.UI_GENERIC_LOCATION, '&gt;&gt; <color=0xffffbb00>%s</color> &lt;&lt;' % name)
        lt = locationText.children[1]
        lt.GetMenu = self.GetLocationMenu
        lt.expandOnLeft = 1
        lt.hint = mls.UI_MARKET_SELECTSTATION
        lt.height += 1
        self.AddSpace(where=self.sr.main)
        if order:
            price = self.bidprice if self.bidprice is not None else order.price
            self.AddEdit(mls.UI_MARKET_BIDPRICE, price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        elif bestMatchableAsk:
            bestPrice = bestMatchableAsk.price
        else:
            bestPrice = averagePrice
        price = self.bidprice if self.bidprice is not None else bestPrice
        self.AddEdit(mls.UI_MARKET_BIDPRICE, price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        self.AddSpace(where=self.sr.main)
        self.AddText(mls.UI_MARKET_REGIONALAVG, util.FmtISK(averagePrice), height=14)
        self.AddText(mls.UI_MARKET_BESTREGIONAL, '', 'quoteText', height=14)
        self.AddText(mls.UI_MARKET_BESTMATCHABLE, '', refName='matchText', height=14)
        self.AddSpace(where=self.sr.main)
        quantity = self.qty if self.qty is not None else 1
        self.AddEdit(mls.UI_GENERIC_QUANTITY, quantity, ints=(1, sys.maxint), refName='quantity', showMin=1)
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and buySettings.has_key('duration'):
            duration = buySettings['duration']
        limits = quote.GetSkillLimits()
        dist = quote.GetStationDistance(self.sr.stationID)
        canRemoteTrade = False
        if dist <= limits['bid']:
            canRemoteTrade = True
        duration2 = self.duration if self.duration is not None else duration
        if canRemoteTrade:
            self.AddCombo(mls.UI_GENERIC_DURATION, self.durations, duration2, 'duration', refName='duration')
        else:
            self.AddCombo(mls.UI_GENERIC_DURATION, self.durations[0:1], 0, 'duration', refName='duration')
        if not session.stationid == locationID and (order or session.stationid is None or forceRange):
            ranges = [self.ranges[0]]
            if canRemoteTrade:
                for range in self.ranges[1:]:
                    if range[1] <= limits['vis'] or limits['vis'] > self.ranges[-1][1]:
                        ranges.append(range)

        else:
            ranges = self.ranges
        firstRange = const.rangeStation
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and buySettings.has_key('range'):
            firstRange = buySettings['range']
        range = self.range if self.range is not None else firstRange
        combo = self.AddCombo(mls.UI_GENERIC_RANGE, ranges, range, 'duration', refName='range')
        self.OnComboChange(combo, mls.UI_GENERIC_STATION, const.rangeStation)
        self.AddSpace(where=self.sr.main)
        self.AddText(mls.UI_MARKET_BROKERSFEE, '-', 'fee')
        self.AddBigText(mls.UI_GENERIC_TOTAL, '-', 'totalOrder')
        self.MakeCorpCheckboxMaybe()
        self.AddSpace(where=self.sr.main)
        cont = uicls.Container(name='cont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
        self.sr.rememberBuySettings = uicls.Checkbox(text='%s' % mls.UI_MARKET_REMEMBER_SETTINGS, parent=cont, configName='rememberBuySettings', retval=None, align=uiconst.TOPLEFT, pos=(0, 0, 350, 0))
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, typeID)
        btn.hint = mls.UI_MARKET_CLICKFORDETAIL
        btn.SetAlign(uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('ui_7_64_1')
        self.sr.currentOrder = order
        self.ready = True
        mainBtnPar = uiutil.GetChild(self, 'btnsmainparent')
        btn = uicls.Button(parent=mainBtnPar, label='&lt;&lt; %s' % mls.UI_GENERIC_SIMPLE, func=self.GoPlaceBuyOrder, args=(typeID,
         order,
         1,
         locationID), align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0))
        self.UpdateTotals()



    def MakeCorpCheckboxMaybe(self):
        if session.corprole & (const.corpRoleAccountant | const.corpRoleTrader):
            n = sm.GetService('corp').GetMyCorpAccountName()
            if n is not None:
                useCorpWallet = False
                if self.mode == 'sell':
                    sellSettings = settings.user.ui.Get('selldefault', {})
                    if sellSettings and sellSettings.has_key('useCorpWallet'):
                        useCorpWallet = sellSettings['useCorpWallet']
                elif self.mode == 'buy':
                    buySettings = settings.user.ui.Get('buydefault', {})
                    if buySettings and buySettings.has_key('useCorpWallet'):
                        useCorpWallet = buySettings['useCorpWallet']
                useCorpWallet2 = self.useCorp if self.useCorp is not None else useCorpWallet
                cont = uicls.Container(name='cont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
                self.sr.usecorp = uicls.Checkbox(text='%s (%s)' % (mls.UI_MARKET_USECORPACCOUNT, n), parent=cont, configName='usecorp', retval=None, checked=useCorpWallet2, align=uiconst.TOPLEFT, pos=(0, 0, 350, 0))



    def TradeSimple(self, mode, invItem = None, typeID = None, order = None, locationID = None, ignoreAdvanced = False):
        if not ignoreAdvanced:
            if mode == 'buy':
                settings.char.ui.Set('advancedBuyWnd', 0)
            else:
                settings.char.ui.Set('advancedSellWnd', 0)
        self.mode = mode
        self.remoteBuyLocation = None
        if self.sr.sellItem:
            sm.StartService('invCache').UnlockItem(self.sr.sellItem.itemID)
        self.SetMinSize([400, 220], 1)
        typeID = typeID or invItem.typeID
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        marketRange = sm.GetService('marketutils').GetMarketRange()
        if mode == 'buy':
            self.invType = invType = cfg.invtypes.Get(typeID)
            if locationID:
                self.remoteBuyLocation = locationID
                location = cfg.evelocations.Get(locationID)
            elif order:
                location = cfg.evelocations.Get(order.stationID)
            if location is None:
                return 
            self.sr.stationID = location.locationID
            if order is None and not eve.session.stationid:
                marketRange = const.rangeStation
                order = quote.GetBestAskInRange(typeID, self.sr.stationID, const.rangeStation, 1)
                if order:
                    order.jumps = quote.GetStationDistance(self.sr.stationID, False)
            else:
                order = order or quote.GetBestAskInRange(typeID, self.sr.stationID, marketRange, 1)
            if order is not None:
                location = cfg.evelocations.Get(order.stationID)
                locationID = location.locationID
                self.remoteBuyLocation = locationID
                self.sr.stationID = locationID
        else:
            sm.StartService('invCache').TryLockItem(invItem.itemID, 'lockItemMenuFunction', {'itemType': cfg.invtypes.Get(invItem.typeID).typeName,
             'action': mls.UI_MARKET_SOLD.lower()}, 1)
            self.invType = invType = cfg.invtypes.Get(invItem.typeID)
            typeID = typeID or invItem.typeID
            stationID = sm.GetService('invCache').GetStationIDOfItem(invItem)
            station = sm.GetService('ui').GetStation(stationID)
            if station is None:
                return 
            location = cfg.evelocations.Get(stationID)
            self.sr.stationID = stationID
            self.sr.solarSystemID = None
            order = quote.GetBestMatchableBid(invItem.typeID, self.sr.stationID, invItem.stacksize)
        self.SetCaption('%s %s' % (getattr(mls, 'UI_MARKET_' + mode.upper()), invType.name))
        self.loading = mode
        self.ready = False
        self.FlushMain(4)
        self.AddSpace(where=self.sr.main)
        self.AddBigText(None, invType.name, typeID=invType.typeID)
        if order:
            locationText = self.AddText(mls.UI_GENERIC_LOCATION, '&gt;&gt; %s &lt;&lt;' % location.name)
            self.sr.isBuy = False
            lt = locationText.children[1]
            lt.GetMenu = self.GetLocationMenu
            lt.height += 1
            if mode == 'buy':
                if session.stationid and order.stationID != session.stationid:
                    if order.jumps == 0:
                        self.AddText(mls.UI_GENERIC_WARNING, mls.UI_MARKET_TEXT8, color=(1.0, 0.0, 0.0, 1.0))
                    else:
                        self.AddText(mls.UI_GENERIC_WARNING, mls.UI_MARKET_TEXT9 % {'jumps': order.jumps,
                         'jump': uix.Plural(order.jumps, 'UI_GENERIC_JUMP')}, color=(1.0, 0.0, 0.0, 1.0))
                elif session.solarsystemid and order.jumps > 0:
                    self.AddText(mls.UI_GENERIC_WARNING, mls.UI_MARKET_TEXT9 % {'jumps': order.jumps,
                     'jump': uix.Plural(order.jumps, 'UI_GENERIC_JUMP')}, color=(1.0, 0.0, 0.0, 1.0))
        self.AddSpace(where=self.sr.main)
        if order:
            colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
            if order.bid:
                colors.reverse()
            self.sr.percentage = (order.price - averagePrice) / averagePrice
            self.AddText(mls.UI_GENERIC_PRICE, util.FmtISK(order.price) + ' [ %s%s%s %s<color=0xffffffff> ]' % (colors[(order.price >= averagePrice)],
             round(100 * self.sr.percentage, 2),
             [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(order.price < averagePrice)].replace('%%', '%'),
             mls.UI_MARKET_REGIONALAVG.lower()))
        else:
            self.AddText('hide', [mls.UI_MARKET_TEXT11, mls.UI_MARKET_TEXT10][(mode == 'sell')] % {'item': invType.name,
             'location': {const.rangeStation: mls.UI_GENERIC_STATION,
                          const.rangeSolarSystem: mls.UI_GENERIC_SOLARSYSTEM,
                          const.rangeRegion: mls.UI_GENERIC_REGION}[marketRange].lower()})
        if order:
            self.AddSpace(where=self.sr.main)
            if mode == 'buy':
                editBox = self.AddEdit(mls.UI_GENERIC_QUANTITY, 1, ints=(1, order.volRemaining), refName='quantity', rightText=mls.UI_MARKET_TEXT12 % {'qty': util.FmtAmt(order.volRemaining),
                 'item': uix.Plural(order.volRemaining, 'UI_GENERIC_ITEM')})
                uicore.registry.SetFocus(editBox)
            else:
                self.AddText(mls.UI_GENERIC_QUANTITY, util.FmtAmt(min(invItem.stacksize, order.volRemaining)))
        if order:
            if mode == 'sell':
                self.AddText(mls.UI_MARKET_SALESTAX, '-', 'transactionTax')
            self.AddBigText(mls.UI_GENERIC_TOTAL, '-', 'totalOrder')
        if order:
            self.MakeCorpCheckboxMaybe()
        if order:
            self.DefineButtons(uiconst.OKCANCEL, okLabel=getattr(mls, 'UI_CMD_' + mode.upper()), okFunc=getattr(self, mode.capitalize()), cancelFunc=self.Cancel)
        else:
            self.DefineButtons(uiconst.CLOSE)
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, typeID)
        btn.hint = mls.UI_MARKET_CLICKFORDETAIL
        btn.SetAlign(uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('ui_7_64_1')
        mainBtnPar = uiutil.GetChild(self, 'btnsmainparent')
        if mode == 'sell':
            btn = uicls.Button(parent=mainBtnPar, label='%s &gt;&gt;' % mls.UI_GENERIC_ADVANCED, func=self.GoPlaceSellOrder, args=invItem, align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0))
        else:
            btn = uicls.Button(parent=mainBtnPar, label='%s &gt;&gt;' % mls.UI_GENERIC_ADVANCED, func=self.GoPlaceBuyOrder, args=(typeID,
             order,
             0,
             locationID), align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0))
        self.sr.currentOrder = order
        self.sr.sellItem = invItem
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()



    def GetLocationMenu(self):
        m = [(mls.UI_MARKET_SELECTSTATION, self.SelectStation)]
        if self.sr.stationID:
            stationInfo = sm.GetService('ui').GetStation(self.sr.stationID)
            if stationInfo:
                m += sm.GetService('menu').MapMenu([stationInfo.solarSystemID])
        return m



    def SelectStation(self):
        format = []
        format.append({'type': 'header',
         'text': mls.UI_MARKET_SELECTSTATIONFORREMOTEBUYORDER,
         'frame': 1})
        format.append({'type': 'edit',
         'labelwidth': 60,
         'label': mls.UI_GENERIC_STATION,
         'key': 'station',
         'required': 0,
         'frame': 1,
         'group': 'avail',
         'setvalue': ''})
        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = uix.HybridWnd(format, mls.UI_MARKET_SELECTSTATION, 1, None, uiconst.OKCANCEL, [left, top], 300, 100, unresizeAble=1, icon='ui_7_64_1')
        if retval:
            name = retval['station']
            if name:
                stationID = uix.Search(name.lower(), const.groupStation, searchWndName='marketQuoteSelectStationSearch')
                if stationID:
                    retList = []
                    if not sm.GetService('marketQuote').CanTradeAtStation(self.sr.Get('isBuy', False), stationID, retList):
                        jumps = retList[0]
                        limit = retList[1]
                        if jumps == const.rangeRegion:
                            raise UserError('MktInvalidRegion')
                        else:
                            jumpText = mls.UI_GENERIC_JUMP if jumps == 1 else mls.UI_GENERIC_JUMPS
                            limitText = mls.UI_GENERIC_JUMP if limit == 1 else mls.UI_GENERIC_JUMPS
                            if limit >= 0:
                                raise UserError('MktCantSellItem2', {'numJumps': jumps,
                                 'jumpText1': jumpText,
                                 'numLimit': limit,
                                 'jumpText2': limitText})
                            else:
                                raise UserError('MktCantSellItemOutsideStation', {'numJumps': jumps,
                                 'jumpText': jumpText})
                    if self.sr.Get('price'):
                        self.bidprice = self.sr.price.GetValue()
                    if self.sr.Get('quantity'):
                        self.qty = self.sr.quantity.GetValue()
                    if self.sr.Get('duration'):
                        self.duration = self.sr.duration.GetValue()
                    if self.sr.Get('range'):
                        self.range = self.sr.range.GetValue()
                    if self.sr.Get('quantityMin', None):
                        self.min = self.sr.quantityMin.GetValue()
                    if util.GetAttrs(self, 'sr', 'usecorp') is not None:
                        self.useCorp = self.sr.usecorp.GetValue()
                    else:
                        self.useCorp = False
                    self.LoadBuy_Detailed(self.invType.typeID, order=getattr(self, 'order', None), locationID=stationID, forceRange=True)



    def LoadSell_Detailed(self, invItem, duration = 1):
        settings.char.ui.Set('advancedSellWnd', 1)
        self.mode = 'sell'
        self.invType = invType = cfg.invtypes.Get(invItem.typeID)
        stationID = sm.GetService('invCache').GetStationIDOfItem(invItem)
        station = sm.GetService('ui').GetStation(stationID)
        if station is None:
            return 
        sm.StartService('invCache').TryLockItem(invItem.itemID, 'lockItemMenuFunction', {'itemType': cfg.invtypes.Get(invItem.typeID).typeName,
         'action': mls.UI_MARKET_SOLD.lower()}, 1)
        self.sr.stationID = stationID
        self.sr.solarSystemID = None
        self.loading = 'sell'
        self.ready = False
        self.FlushMain(4)
        self.ShowLoad()
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(invItem.typeID)
        bestMatchableBid = quote.GetBestMatchableBid(invItem.typeID, self.sr.stationID, invItem.stacksize)
        self.sr.solarSystemID = station.solarSystemID
        self.DefineButtons(uiconst.OKCANCEL, okLabel=mls.UI_CMD_SELL, okFunc=self.Sell, cancelFunc=self.Cancel)
        self.SetCaption('%s %s' % (mls.UI_CMD_SELL, invType.name))
        self.AddSpace(where=self.sr.main)
        self.AddBigText(None, invType.name, typeID=invType.typeID)
        self.AddSpace(where=self.sr.main)
        if bestMatchableBid:
            bestPrice = bestMatchableBid.price
        else:
            bestPrice = averagePrice
        self.AddEdit(mls.UI_MARKET_ASKPRICE, bestPrice, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        self.AddSpace(where=self.sr.main)
        self.AddText(mls.UI_MARKET_REGIONALAVG, util.FmtISK(averagePrice), height=14)
        self.AddText(mls.UI_MARKET_BESTREGIONAL, '', 'quoteText', height=14)
        self.AddText(mls.UI_MARKET_REGIONALAVG, util.FmtISK(averagePrice), height=14)
        self.AddText(mls.UI_MARKET_BESTMATCHABLE, '', refName='matchText', height=14)
        self.AddSpace(where=self.sr.main)
        qty = invItem.stacksize
        qtyEdit = self.AddEdit(mls.UI_GENERIC_QUANTITY, qty, ints=(1, long(qty)), refName='quantity', showMin=0)
        sellSettings = settings.user.ui.Get('selldefault', {})
        if sellSettings and sellSettings.has_key('duration'):
            duration = sellSettings['duration']
        self.AddSpace(where=self.sr.main)
        self.AddCombo(mls.UI_GENERIC_DURATION, self.durations, duration, 'duration', refName='duration')
        self.AddSpace(where=self.sr.main)
        self.AddText(mls.UI_MARKET_BROKERSFEE, '-', 'fee')
        self.AddText(mls.UI_MARKET_SALESTAX, '-', 'transactionTax')
        self.AddBigText(mls.UI_GENERIC_TOTAL, '-', 'totalOrder')
        self.MakeCorpCheckboxMaybe()
        self.AddSpace(where=self.sr.main)
        cont = uicls.Container(name='cont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
        self.sr.rememberSellSettings = uicls.Checkbox(text='%s' % mls.UI_MARKET_REMEMBER_SETTINGS, parent=cont, configName='rememberSellSettings', retval=None, align=uiconst.TOPLEFT, pos=(0, 0, 350, 0))
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, invItem.typeID)
        btn.hint = mls.UI_MARKET_CLICKFORDETAIL
        btn.SetAlign(align=uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('ui_7_64_1')
        self.sr.sellItem = invItem
        self.ready = True
        mainBtnPar = uiutil.GetChild(self, 'btnsmainparent')
        btn = uicls.Button(parent=mainBtnPar, label='&lt;&lt; %s' % mls.UI_GENERIC_SIMPLE, func=self.GoPlaceSellOrder, args=(invItem, 1), align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0))
        self.UpdateTotals()
        self.HideLoad()



    def RemeberBuySettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        range = const.rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            range = self.sr.range.GetValue()
        settings.user.ui.Set('buydefault', {'duration': duration,
         'useCorpWallet': useCorp,
         'range': range})



    def RemeberSellSettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        settings.user.ui.Set('selldefault', {'duration': duration,
         'useCorpWallet': useCorp})



    def ViewDetails(self, typeID, simple = 0, *args):
        uthread.new(self.ViewDetails_, typeID, simple)



    def ViewDetails_(self, typeID, simple = 0, *args):
        sm.GetService('marketutils').ShowMarketDetails(typeID, None)
        uiutil.SetOrder(self, 0)



    def GoPlaceSellOrder(self, invItem, simple = 0, *args):
        settings.char.ui.Set('advancedSellWnd', not simple)
        uthread.new(sm.GetService('marketutils').Sell, invItem.typeID, invItem, not simple)
        self.SelfDestruct()



    def GoPlaceBuyOrder(self, typeID, order = None, simple = 0, prePickedLocationID = None, *args):
        settings.char.ui.Set('advancedBuyWnd', not simple)
        uthread.new(sm.GetService('marketutils').Buy, typeID, order=order, placeOrder=not simple, prePickedLocationID=prePickedLocationID)
        self.SelfDestruct()



    def LoadModify(self, order):
        if order is None:
            return 
        self.loading = 'modify'
        self.ready = False
        self.FlushMain(3)
        self.ShowLoad()
        self.invType = invType = cfg.invtypes.Get(order.typeID)
        location = cfg.evelocations.Get(order.stationID)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Modify, cancelFunc=self.Cancel)
        self.SetCaption(mls.UI_CMD_MODIFYORDER)
        self.AddText(mls.UI_GENERIC_TYPE, invType.name)
        self.AddText(mls.UI_GENERIC_LOCATION, location.name)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        self.AddText([mls.UI_MARKET_OLDSELLPRICE, mls.UI_MARKET_OLDBUYPRICE][order.bid], util.FmtISK(order.price))
        self.AddText(mls.UI_MARKET_QTYREMAINING, util.FmtAmt(order.volRemaining))
        self.quantity = order.volRemaining
        edit = self.AddEdit([mls.UI_MARKET_NEWSELLPRICE, mls.UI_MARKET_NEWBUYPRICE][order.bid], '%.2f' % order.price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        uicore.registry.SetFocus(edit)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        self.AddText(mls.UI_MARKET_TOTALCHANGE, '-', 'totalOrder')
        self.AddText(mls.UI_MARKET_BROKERSFEE, '-', 'fee')
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()



    def AddSpace(self, where, height = 6):
        uicls.Container(name='space', parent=where, height=height, align=uiconst.TOTOP)



    def Cancel(self, *args):
        self.SelfDestruct()



    def Modify(self, *args):
        if self.sr.currentOrder is None:
            return 
        price = self.sr.price.GetValue()
        order = self.sr.currentOrder
        if self.sr.percentage < -0.5 or self.sr.percentage > 1.0:
            aboveOrBelow = mls.UI_MARKET_PERCENTBELOW if self.sr.percentage < 0.0 else mls.UI_MARKET_PERCENTABOVE
            ret = eve.Message('MktConfirmTrade', {'amount': str(round(100 * abs(self.sr.percentage), 2)) + aboveOrBelow}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return 
        self.SelfDestruct()
        sm.GetService('marketQuote').ModifyOrder(order, price)



    def Buy(self, *args):
        if self.invType is None:
            return 
        self.mode = 'buy'
        typeID = self.invType.typeID
        quantity = self.sr.quantity.GetValue()
        duration = 0
        brokersFee = 0
        if self.sr.Get('fee') and not self.sr.fee.destroyed and self.sr.fee.text != '-' and eve.Message('ConfirmMarketOrder', {'isk': self.sr.fee.text}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        if self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        if self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = self.sr.duration.GetValue()
        orderRange = const.rangeStation
        if self.sr.Get('range') and not self.sr.range.destroyed:
            orderRange = self.sr.range.GetValue()
        if self.remoteBuyLocation or not eve.session.stationid:
            stationID = self.remoteBuyLocation
        else:
            stationID = self.sr.currentOrder.stationID
        minVolume = 1
        if self.sr.Get('quantityMin', None) and not self.sr.quantityMin.destroyed:
            minVolume = self.sr.quantityMin.GetValue()
        if util.GetAttrs(self, 'sr', 'usecorp') is not None and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        else:
            useCorp = False
        if self.sr.percentage > 1.0:
            ret = eve.Message('MktConfirmTrade', {'amount': str(round(100 * abs(self.sr.percentage), 2)) + mls.UI_MARKET_PERCENTABOVE}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return 
        if self.sr.Get('rememberBuySettings') and not self.sr.rememberBuySettings.destroyed and self.sr.rememberBuySettings.checked:
            self.RemeberBuySettings()
        self.SelfDestruct()
        sm.GetService('marketQuote').BuyStuff(stationID, typeID, price, quantity, orderRange, minVolume, duration, useCorp)



    def Sell(self, *args):
        if self.sr.sellItem is None:
            return 
        self.mode = 'sell'
        duration = 0
        if self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = self.sr.duration.GetValue()
        if self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder:
            price = self.sr.currentOrder.price
        if self.sr.Get('quantity') and not self.sr.quantity.destroyed:
            quantity = self.sr.quantity.GetValue()
        elif self.sr.currentOrder:
            quantity = min(self.sr.sellItem.stacksize, self.sr.currentOrder.volRemaining)
        (stationID, officeFolderID, officeID,) = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(self.sr.sellItem)
        located = None
        if officeFolderID is not None:
            located = [officeFolderID, officeID]
        itemID = self.sr.sellItem.itemID
        typeID = self.sr.sellItem.typeID
        if util.GetAttrs(self, 'sr', 'usecorp') is not None:
            useCorp = self.sr.usecorp.GetValue()
        else:
            useCorp = False
        minVolume = 1
        if self.sr.Get('quantityMin', None) and not self.sr.quantityMin.destroyed:
            minVolume = self.sr.quantityMin.GetValue()
        if self.sr.percentage < -0.5:
            ret = eve.Message('MktConfirmTrade', {'amount': str(round(100 * abs(self.sr.percentage), 2)) + mls.UI_MARKET_PERCENTBELOW}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return 
        if self.sr.Get('rememberSellSettings') and self.sr.rememberSellSettings.checked:
            self.RemeberSellSettings()
        self.SelfDestruct()
        sm.GetService('marketQuote').SellStuff(stationID, typeID, itemID, price, quantity, duration, useCorp, located)



    def AddText(self, label, text, refName = None, height = 20, color = None):
        par = uicls.Container(name='text', parent=self.sr.main, align=uiconst.TOTOP, height=height)
        left = LABELWIDTH
        if label == 'hide':
            left = 0
        elif label:
            uicls.Label(text=label, parent=par, width=LABELWIDTH, autowidth=False, left=0, top=6, fontsize=9, letterspace=2, color=color, linespace=9, state=uiconst.UI_NORMAL)
        t = uicls.Label(text=text, parent=par, width=self.Width() - LABELWIDTH - 16, autowidth=False, left=left, top=4, fontsize=12, color=color, state=uiconst.UI_NORMAL)
        par.height = max(20, t.textheight)
        if refName:
            setattr(self.sr, refName, t)
        return par



    def AddBigText(self, label, text, refName = None, height = 28, typeID = None):
        par = uicls.Container(name='text', parent=self.sr.main, align=uiconst.TOTOP, height=height)
        left = 0
        if label:
            uicls.Label(text=label, parent=par, width=LABELWIDTH, autowidth=False, left=0, top=13, fontsize=9, letterspace=2, color=None, state=uiconst.UI_NORMAL)
            left = LABELWIDTH
        offset = 0
        if typeID:
            offset = 36
            icon = uicls.Icon(parent=par, pos=(left,
             -4,
             32,
             32), typeID=typeID, align=uiconst.TOPLEFT)
            icon.SetSize(32, 32)
        t = uicls.CaptionLabel(text=text, parent=par, align=uiconst.RELATIVE, width=self.Width() - left + offset - 16, left=left + offset, uppercase=False, letterspace=0, autowidth=0)
        if refName:
            setattr(self.sr, refName, t)
        par.height = t.textheight + 4



    def AddEdit(self, label, setvalue, ints = None, floats = None, width = 80, showMin = 0, refName = None, rightText = None, left = LABELWIDTH):
        minHeight = 20
        parent = uicls.Container(name=label, parent=self.sr.main, height=20, align=uiconst.TOTOP)
        edit = uicls.SinglelineEdit(name=label, parent=parent, pos=(LABELWIDTH,
         1,
         width,
         0), align=uiconst.TOPLEFT)
        if refName == 'quantity':
            edit.OnChange = self.OnChanged_quantity
        else:
            edit.OnChange = self.OnEditChange
        edit.OnFocusLost = self.OnEditChange
        if showMin:
            min = 1
            if refName == 'quantity':
                min = self.min if self.min is not None else min
            minedit = uicls.SinglelineEdit(name=label, parent=parent, setvalue=min, ints=(1, sys.maxint), width=40, left=edit.left + edit.width + 50, top=2, align=uiconst.TOPLEFT)
            minedit.OnChange = self.OnEditChange
            if refName:
                setattr(self.sr, refName + 'Min', minedit)
            uicls.Label(text=mls.UI_GENERIC_MINIMUM, parent=parent, width=200, left=edit.left + edit.width + 6, top=7, autowidth=False, fontsize=9, letterspace=2, state=uiconst.UI_NORMAL)
        if ints:
            edit.IntMode(*ints)
        elif floats:
            edit.FloatMode(*floats)
        if setvalue:
            edit.SetValue(setvalue)
        _label = uicls.Label(text=label, parent=parent, width=LABELWIDTH, left=0, top=[6, -1][(label.find('<br>') >= 0)], autowidth=False, fontsize=9, letterspace=2, linespace=9, state=uiconst.UI_NORMAL)
        if rightText is not None:
            _rightText = uicls.Label(text=rightText, parent=parent, width=self.Width() - width - left - 6 - 8, left=width + left + 6, top=4, autowidth=False, state=uiconst.UI_NORMAL)
            minHeight = max(minHeight, _rightText.textheight + 8)
            if refName:
                setattr(self.sr, refName + '_rightText', _rightText)
            parent.height = minHeight
        if refName:
            setattr(self.sr, refName, edit)
        return edit



    def AddCombo(self, label, options, setvalue, configname, width = 80, refName = None):
        parent = uicls.Container(name=configname, parent=self.sr.main, height=20, align=uiconst.TOTOP)
        combo = uicls.Combo(label='', parent=parent, options=options, name=configname, callback=self.OnComboChange, width=width, pos=(LABELWIDTH,
         2,
         0,
         0))
        _label = uicls.Label(text=label, parent=parent, width=LABELWIDTH, autowidth=False, left=0, top=[7, -1][(label.find('<br>') >= 0)], fontsize=9, letterspace=2, linespace=9, state=uiconst.UI_NORMAL)
        combo.sr.label = _label
        if setvalue is not None:
            combo.SelectItemByValue(setvalue)
        if refName:
            setattr(self.sr, refName, combo)
        return combo



    def OnChanged_quantity(self, quantity):
        if not self.ready:
            return 
        uthread.pool('MarketActionWindow::OnChanged_quantity', self.OnChanged_quantityThread, quantity)



    def OnChanged_quantityThread(self, quantity):
        try:
            if self.loading == 'sell':
                if quantity is None or len(quantity) == 0:
                    quantity = 1
                quantity = max(1, long(quantity))
                quote = sm.GetService('marketQuote')
                bestBid = quote.GetBestMatchableBid(self.invType.typeID, self.sr.stationID, quantity)
                if bestBid:
                    if bestBid.price > self.sr.price.GetValue():
                        self.sr.price.SetValue(bestBid.price)
                    if self.sr.matchText:
                        averagePrice = sm.GetService('marketQuote').GetAveragePrice(self.invType.typeID)
                        self.sr.matchText.text = util.FmtISK(bestBid.price) + ' [ %s%s %s, %s %s ]' % (round(100 * (bestBid.price - averagePrice) / averagePrice, 2),
                         [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(bestBid.price < averagePrice)],
                         mls.UI_MARKET_REGIONALAVG,
                         int(bestBid.volRemaining),
                         [mls.UI_GENERIC_UNIT, mls.UI_GENERIC_UNITS][(int(bestBid.volRemaining) != 1)])
                        self.CheckHeights(self.sr.matchText, 'matchText')
                elif self.sr.matchText:
                    self.sr.matchText.text = mls.UI_MARKET_TEXT13
                    self.CheckHeights(self.sr.matchText, 'matchText')
            self.UpdateTotals()
        except:
            log.LogException()
            sys.exc_clear()



    def OnEditChange(self, *args):
        if not self or self.destroyed:
            return 
        uthread.pool('MarketActionWindow::OnEditChange', self.OnEditChangeThread, *args)



    def OnEditChangeThread(self, *args):
        self.UpdateTotals()



    def OnComboChange(self, combo, header, value, *args):
        uthread.pool('MarketActionWindow::OnComboChange', self.OnComboChangeThread, combo, header, value, *args)



    def OnComboChangeThread(self, combo, header, value, *args):
        self.UpdateTotals()



    def UpdateTotals(self):
        if self.destroyed:
            return 
        if not self.ready:
            return 
        if not self.invType:
            return 
        if not hasattr(self, 'sr'):
            return 
        quote = sm.GetService('marketQuote')
        limits = quote.GetSkillLimits()
        averagePrice = quote.GetAveragePrice(self.invType.typeID)
        colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
        if not self or self.destroyed or not hasattr(self, 'sr'):
            return 
        self.sr.percentage = 0
        price = 0
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        if self.loading == 'modify':
            quantity = self.sr.currentOrder.volRemaining
        else:
            quantity = 1
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantity') and not self.sr.quantity.destroyed:
                quantity = self.sr.quantity.GetValue(refreshDigits=0) or 0
            elif self.sr.currentOrder is not None:
                if self.loading == 'sell' and self.sr.sellItem is not None:
                    quantity = min(self.sr.sellItem.quantity, self.sr.currentOrder.volRemaining)
                else:
                    quantity = self.sr.currentOrder.volRemaining
        quantity = max(1, quantity)
        quantityMin = 1
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantityMin') and not self.sr.quantityMin.destroyed:
            quantityMin = self.sr.quantityMin.GetValue()
        range = const.rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            range = self.sr.range.GetValue()
        fee = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('fee') and not self.sr.fee.destroyed:
            if duration > 0:
                _fee = quote.BrokersFee(self.sr.stationID, price * quantity, limits['fee'])
                fee = _fee.amt
                if _fee.percentage < 0:
                    p = mls.UI_GENERIC_MINIMUM
                else:
                    p = '%s%%' % round(_fee.percentage * 100, 2)
                self.sr.fee.text = '%s (%s)' % (util.FmtISK(fee), p)
            else:
                self.sr.fee.text = '-'
            self.CheckHeights(self.sr.fee, 'fee')
        tax = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('transactionTax') and not self.sr.transactionTax.destroyed:
            tax = price * quantity * limits['acc']
            self.sr.transactionTax.text = '%s (%.1f%%)' % (util.FmtISK(tax), limits['acc'] * 100.0)
            self.CheckHeights(self.sr.transactionTax, 'transactionTax')
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('totalOrder') and not self.sr.totalOrder.destroyed:
            if self.loading == 'buy':
                sumTotal = -price * quantity
            else:
                sumTotal = price * quantity
            color = 'green'
            if sumTotal - tax - fee < 0.0:
                color = 'red'
            self.sr.totalOrder.text = '<color=%s>' % color + util.FmtISK(abs(sumTotal - tax - fee))
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
        if self.loading == 'buy':
            colors.reverse()
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('matchText') and not self.sr.matchText.destroyed:
                bestMatchableAskKey = (self.invType.typeID,
                 self.sr.stationID,
                 const.rangeRegion,
                 quantityMin)
                bestMatchableAsk = self.bestMatchableAskDict.get(bestMatchableAskKey, -1)
                if bestMatchableAsk == -1:
                    bestMatchableAsk = quote.GetBestAskInRange(self.invType.typeID, self.sr.stationID, range, amount=quantityMin)
                    self.ManageBestMatchableAskDict(key=bestMatchableAskKey, value=bestMatchableAsk)
                if bestMatchableAsk:
                    jumps = int(bestMatchableAsk.jumps)
                    if jumps == 0 and bestMatchableAsk.stationID == self.sr.stationID:
                        jumps = mls.UI_MARKET_INSAMESTATION
                    else:
                        jumps = [mls.UI_MARKET_JUMPSAWAY, mls.UI_MARKET_JUMPSAWAY][(jumps != 1)] % {'jumps': jumps}
                    matchText = util.FmtISK(bestMatchableAsk.price) + ' [ %s%s %s, %s %s %s ]' % (round(100 * (bestMatchableAsk.price - averagePrice) / averagePrice, 2),
                     [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(bestMatchableAsk.price < averagePrice)],
                     mls.UI_MARKET_REGIONALAVG,
                     int(bestMatchableAsk.volRemaining),
                     [mls.UI_GENERIC_UNIT, mls.UI_GENERIC_UNITS][(int(bestMatchableAsk.volRemaining) != 1)],
                     jumps)
                else:
                    matchText = mls.UI_MARKET_TEXT14
                self.sr.matchText.text = matchText
                self.CheckHeights(self.sr.matchText, 'matchText')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quoteText') and not self.sr.quoteText.destroyed:
                bestAskKey = (self.invType.typeID, self.sr.stationID, const.rangeRegion)
                bestAsk = self.bestAskDict.get(bestAskKey, -1)
                if bestAsk == -1:
                    bestAsk = quote.GetBestAskInRange(self.invType.typeID, self.sr.stationID, const.rangeRegion)
                    self.bestAskDict[bestAskKey] = bestAsk
                if bestAsk:
                    jumps = int(bestAsk.jumps)
                    if jumps == 0 and bestAsk.stationID == self.sr.stationID:
                        jumps = mls.UI_MARKET_INSAMESTATION
                    else:
                        jumps = [mls.UI_MARKET_JUMPSAWAY, mls.UI_MARKET_JUMPSAWAY][(jumps != 1)] % {'jumps': jumps}
                    quoteText = util.FmtISK(bestAsk.price) + ' [ %s%s %s, %s %s %s ]' % (round(100 * (bestAsk.price - averagePrice) / averagePrice, 2),
                     [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(bestAsk.price < averagePrice)],
                     mls.UI_MARKET_REGIONALAVG,
                     int(bestAsk.volRemaining),
                     [mls.UI_GENERIC_UNIT, mls.UI_GENERIC_UNITS][(int(bestAsk.volRemaining) != 1)],
                     jumps)
                else:
                    quoteText = mls.UI_MARKET_TEXT14
                self.sr.quoteText.text = quoteText
                self.CheckHeights(self.sr.quoteText, 'quoteText')
            self.sr.percentage = (price - averagePrice) / averagePrice
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                self.sr.price_rightText.text = ' [ %s%s%s %s<color=0xffffffff> ]' % (colors[(price < averagePrice)],
                 round(100 * self.sr.percentage, 2),
                 [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(price < averagePrice)],
                 mls.UI_MARKET_REGIONALAVG)
                self.CheckHeights(self.sr.price_rightText, 'price_rightText')
        elif self.loading == 'sell':
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quoteText') and not self.sr.quoteText.destroyed:
                bestBidKey = (self.invType.typeID, self.sr.solarSystemID)
                bestBid = self.bestBidDict.get(bestBidKey, -1)
                if bestBid == -1:
                    bestBid = quote.GetBestBid(self.invType.typeID, locationID=self.sr.solarSystemID)
                    self.bestBidDict[bestBidKey] = bestBid
                if bestBid:
                    jumps = max(bestBid.jumps - max(0, bestBid.range), 0)
                    if jumps == 0 and self.sr.stationID == bestBid.stationID:
                        jumpText = mls.UI_MARKET_INSAMESTATIONASITEMS
                    else:
                        jumpText = [mls.UI_MARKET_JUMPFROMTHISITEM, mls.UI_MARKET_JUMPSFROMTHISITEM][(jumps == 0 or jumps > 1)] % {'jumps': jumps}
                    quoteText = '%s [ %s %s %s ]' % (util.FmtISK(bestBid.price),
                     util.FmtAmt(long(bestBid.volRemaining)),
                     [mls.UI_MARKET_UNITMATCHABLE, mls.UI_MARKET_UNITSMATCHABLE][(bestBid.volRemaining >= 2)],
                     jumpText)
                    if bestBid.minVolume > 1 and bestBid.volRemaining >= bestBid.minVolume:
                        quoteText += ' %s' % mls.UI_MARKET_TEXT15 % {'min': bestBid.minVolume}
                else:
                    quoteText = mls.UI_MARKET_TEXT13
                self.sr.quoteText.text = quoteText
                self.CheckHeights(self.sr.quoteText, 'quoteText')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                self.sr.percentage = (price - averagePrice) / averagePrice
                self.sr.price_rightText.text = ' [ %s%.2f%s %s<color=0xffffffff> ]' % (colors[(price < averagePrice)],
                 100 * self.sr.percentage,
                 [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(price < averagePrice)],
                 mls.UI_MARKET_REGIONALAVG)
                self.CheckHeights(self.sr.price_rightText, 'price_rightText')
        elif self.loading == 'modify':
            if self.sr.currentOrder.bid:
                colors.reverse()
            oldPrice = self.sr.currentOrder.price
            self.sr.totalOrder.text = util.FmtISK((price - oldPrice) * quantity)
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
            if price - oldPrice < 0:
                self.sr.fee.text = util.FmtISK(const.mktMinimumFee)
            else:
                self.sr.fee.text = util.FmtISK(max(const.mktMinimumFee, (price - oldPrice) * quantity * limits['fee']))
            self.CheckHeights(self.sr.fee, 'fee')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                self.sr.percentage = (price - averagePrice) / averagePrice
                self.sr.price_rightText.text = ' [ %s%s%s %s<color=0xffffffff> ]' % (colors[(price < averagePrice)],
                 round(100 * self.sr.percentage, 2),
                 [mls.UI_MARKET_PERCENTABOVE, mls.UI_MARKET_PERCENTBELOW][(price < averagePrice)],
                 mls.UI_MARKET_REGIONALAVG)
                self.CheckHeights(self.sr.price_rightText, 'price_rightText')



    def ManageBestMatchableAskDict(self, key, value):
        if len(self.bestMatchableAskDict) > 15:
            self.bestMatchableAskDict = {}
        else:
            self.bestMatchableAskDict[key] = value



    def CheckHeights(self, t, what = None):
        t.parent.height = t.textheight + t.top * 2
        theight = sum([ each.height for each in t.parent.parent.children if each.align == uiconst.TOTOP ])
        self.SetMinSize([self.Width(), theight + 56], 1)




