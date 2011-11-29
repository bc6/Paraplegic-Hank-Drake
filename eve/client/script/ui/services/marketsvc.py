from service import *
import util
import blue
import dbutil
import localization
CACHE_INTERVAL = 300
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
DAY = 24 * HOUR
jumpsPerSkillLevel = {0: -1,
 1: 0,
 2: 5,
 3: 10,
 4: 20,
 5: 50}

def SortAsks(x, y, headers):
    priceIdx = headers.index('price')
    if x[priceIdx] < y[priceIdx]:
        return -1
    else:
        if x[priceIdx] > y[priceIdx]:
            return 1
        issuedIdx = headers.index('issueDate')
        if x[issuedIdx] < y[issuedIdx]:
            return -1
        if x[issuedIdx] > y[issuedIdx]:
            return 1
        jmpIdx = headers.index('jumps')
        if x[jmpIdx] < y[jmpIdx]:
            return -1
        if x[jmpIdx] > y[jmpIdx]:
            return 1
        orderIdx = headers.index('orderID')
        if x[orderIdx] < y[orderIdx]:
            return -1
        return 1



def SortBids(x, y, headers):
    priceIdx = headers.index('price')
    if x[priceIdx] < y[priceIdx]:
        return 1
    else:
        if x[priceIdx] > y[priceIdx]:
            return -1
        issuedIdx = headers.index('issueDate')
        if x[issuedIdx] < y[issuedIdx]:
            return -1
        if x[issuedIdx] > y[issuedIdx]:
            return 1
        jmpIdx = headers.index('jumps')
        rngIdx = headers.index('range')
        if x[jmpIdx] - max(0, x[rngIdx]) < y[jmpIdx] - max(0, y[rngIdx]):
            return -1
        if x[jmpIdx] - x[rngIdx] > y[jmpIdx] - y[rngIdx]:
            return 1
        orderIdx = headers.index('orderID')
        if x[orderIdx] < y[orderIdx]:
            return -1
        return 1



class MarketQuote(Service):
    __exportedcalls__ = {'GetMyOrders': [ROLE_ANY],
     'GetCorporationOrders': [ROLE_ANY],
     'PlaceOrder': [ROLE_ANY],
     'BuyStuff': [ROLE_ANY],
     'SellStuff': [ROLE_ANY],
     'CancelOrder': [ROLE_ANY],
     'ModifyOrder': [ROLE_ANY],
     'GetSkillLimits': [ROLE_ANY],
     'BrokersFee': [ROLE_ANY],
     'GetPriceHistory': [ROLE_ANY],
     'GetAveragePrice': [ROLE_ANY],
     'GetStationAsks': [ROLE_ANY],
     'GetSystemAsks': [ROLE_ANY],
     'GetOrders': [ROLE_ANY],
     'GetOrder': [ROLE_ANY],
     'GetRegionBest': [ROLE_ANY],
     'RefreshAll': [ROLE_ANY],
     'ClearAll': [ROLE_ANY],
     'GetStationDistance': [ROLE_ANY],
     'CanTradeAtStation': [ROLE_ANY],
     'GetBestMatchableBid': [ROLE_ANY],
     'GetBestBid': [ROLE_ANY],
     'GetBestAverageAsk': [ROLE_ANY],
     'GetBestAskInRange': [ROLE_ANY],
     'GetBestBidInRange': [ROLE_ANY],
     'DumpQuotes': [ROLE_ANY],
     'DumpOrdersForType': [ROLE_ANY],
     'GetMarketProxy': []}
    __guid__ = 'svc.marketQuote'
    __servicename__ = 'marketquote'
    __displayname__ = 'Market Quote Service'
    __notifyevents__ = ['OnSessionChanged', 'OnSkillTrained', 'OnOwnOrderChanged']
    __dependencies__ = ['pathfinder']
    __update_on_reload__ = 1

    def Run(self, ms):
        self.groupsQuotes = {}
        self.lastGotGroupsQuotes = {}
        self.lastGotGroupQuotes = {}
        self.groupQuotes = {}
        self.waitingFor = {}
        self.locks = {}
        self.orderCache = {}
        sm.FavourMe(self.OnOwnOrderChanged)



    def OnOwnOrderChanged(self, order, reason, isCorp):
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetCharOrders')
        if order is not None:
            sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetOrders', order.typeID)
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetSystemAsks')
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetStationAsks')



    def OnSkillTrained(self, skillID):
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetCharSkillLimits')



    def OnSessionChanged(self, isRemote, session, change):
        if 'regionid' in change:
            self.LogInfo('MarketSvc: Region change, clearing internal cache')
            self.ClearAll()



    def BrokersFee(self, stationID, amount, commissionPercentage):
        if amount < 0.0:
            raise AttributeError('Amount must be positive')
        orderValue = float(amount)
        station = sm.GetService('ui').GetStation(stationID)
        stationOwnerID = None
        if station is not None:
            stationOwnerID = station.ownerID
        factionChar = 0
        corpChar = 0
        if stationOwnerID:
            if util.IsNPC(stationOwnerID):
                factionID = sm.GetService('faction').GetFaction(stationOwnerID)
                factionChar = sm.GetService('standing').GetStanding(factionID, eve.session.charid) or 0.0
            corpChar = sm.GetService('standing').GetStanding(stationOwnerID, eve.session.charid) or 0.0
        weightedStanding = (0.7 * factionChar + 0.3 * corpChar) / 10.0
        commissionPercentage = commissionPercentage * 2.0 ** (-2 * weightedStanding)
        tax = util.KeyVal()
        tax.amt = commissionPercentage * orderValue
        tax.percentage = commissionPercentage
        if tax.amt <= const.mktMinimumFee:
            tax.amt = const.mktMinimumFee
            tax.percentage = -1.0
        return tax



    def CanTradeAtStation(self, bid, stationID, retList = None):
        limits = self.GetSkillLimits()
        if bid:
            jumps = self.GetStationDistance(stationID)
            if retList is not None:
                retList.append(jumps)
                retList.append(limits['bid'])
            if jumps <= limits['bid']:
                return True
        else:
            jumps = self.GetStationDistance(stationID)
            if retList is not None:
                retList.append(jumps)
                retList.append(limits['ask'])
            if jumps <= limits['ask']:
                return True
        return False



    def GetStationDistance(self, stationID, getFastestRoute = True):
        if session.stationid == stationID:
            return -1
        station = sm.GetService('ui').GetStation(stationID)
        solarSystemID = station.solarSystemID
        regionID = sm.GetService('map').GetRegionForSolarSystem(solarSystemID)
        if regionID != session.regionid:
            return const.rangeRegion
        if getFastestRoute:
            jumps = sm.StartService('pathfinder').GetShortestJumpCountFromCurrent(solarSystemID)
        else:
            jumps = sm.StartService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
        if jumps >= 1:
            return jumps
        return 0



    def GetRegionBest(self):
        return self.GetMarketProxy().GetRegionBest()



    def GetSkillLimits(self):
        limits = {}
        currentOpen = 0
        myskills = sm.GetService('skills').MySkillLevelsByID()
        retailLevel = myskills.get(const.typeRetail, 0)
        tradeLevel = myskills.get(const.typeTrade, 0)
        wholeSaleLevel = myskills.get(const.typeWholesale, 0)
        accountingLevel = myskills.get(const.typeAccounting, 0)
        brokerLevel = myskills.get(const.typeBrokerRelations, 0)
        tycoonLevel = myskills.get(const.typeTycoon, 0)
        marginTradingLevel = myskills.get(const.typeMarginTrading, 0)
        marketingLevel = myskills.get(const.typeMarketing, 0)
        procurementLevel = myskills.get(const.typeProcurement, 0)
        visibilityLevel = myskills.get(const.typeVisibility, 0)
        daytradingLevel = myskills.get(const.typeDaytrading, 0)
        maxOrderCount = 5 + tradeLevel * 4 + retailLevel * 8 + wholeSaleLevel * 16 + tycoonLevel * 32
        limits['cnt'] = maxOrderCount
        commissionPercentage = const.marketCommissionPercentage / 100.0
        commissionPercentage *= 1 - brokerLevel * 0.05
        transactionTax = const.mktTransactionTax / 100.0
        transactionTax *= 1 - accountingLevel * 0.1
        limits['fee'] = commissionPercentage
        limits['acc'] = transactionTax
        limits['ask'] = jumpsPerSkillLevel[marketingLevel]
        limits['bid'] = jumpsPerSkillLevel[procurementLevel]
        limits['vis'] = jumpsPerSkillLevel[visibilityLevel]
        limits['mod'] = jumpsPerSkillLevel[daytradingLevel]
        limits['esc'] = 0.75 ** marginTradingLevel
        return limits



    def GetMarketProxy(self):
        return sm.ProxySvc('marketProxy')



    def BuyStuff(self, stationID, typeID, price, quantity, orderRange = None, minVolume = 1, duration = 0, useCorp = False):
        if orderRange is None:
            orderRange = const.rangeStation
        self.PlaceOrder(stationID, typeID, price, quantity, 1, orderRange, None, minVolume, duration, useCorp)



    def SellStuff(self, stationID, typeID, itemID, price, quantity, duration = 0, useCorp = False, located = None):
        self.PlaceOrder(stationID, typeID, price, quantity, 0, const.rangeRegion, itemID, 1, duration, useCorp, located)



    def PlaceOrder(self, stationID, typeID, price, quantity, bid, orderRange, itemID = None, minVolume = 1, duration = 14, useCorp = False, located = None):
        price = round(price, 2)
        if price > 9223372036854.0:
            raise ValueError('Price can not exceed %s', 9223372036854.0)
        if quantity < 0:
            raise UserError('RepackageBeforeSelling', {'item': typeID})
        self.GetMarketProxy().PlaceCharOrder(int(stationID), int(typeID), round(float(price), 2), int(quantity), int(bid), int(orderRange), itemID, int(minVolume), int(duration), useCorp, located)



    def CancelOrder(self, orderID, regionID):
        self.GetMarketProxy().CancelCharOrder(orderID, regionID)



    def ModifyOrder(self, order, newPrice):
        if newPrice > 9223372036854.0:
            raise ValueError('Price can not exceed %s', 9223372036854.0)
        self.GetMarketProxy().ModifyCharOrder(order.orderID, newPrice, order.bid, order.stationID, order.solarSystemID, order.price, order.range, order.volRemaining, order.issueDate)



    def GetStationAsks(self):
        if session.stationid is None:
            raise AttributeError('Must be in station')
        return self.GetMarketProxy().GetStationAsks()



    def GetSystemAsks(self):
        if session.solarsystemid2 is None:
            raise AttributeError('Must be in a solarsystem')
        return self.GetMarketProxy().GetSystemAsks()



    def GetPriceHistory(self, typeID):
        old = self.GetMarketProxy().GetOldPriceHistory(typeID)
        new = self.GetMarketProxy().GetNewPriceHistory(typeID)
        history = dbutil.RowList((new.header, []))
        lastTime = blue.os.GetWallclockTimeNow()
        midnightToday = lastTime / const.DAY * const.DAY
        lastPrice = 0.0
        for entry in old:
            while lastTime + DAY < entry.historyDate:
                lastTime += DAY
                history.append(blue.DBRow(history.header, [lastTime,
                 lastPrice,
                 lastPrice,
                 lastPrice,
                 0,
                 0]))

            history.append(entry)
            lastTime = entry.historyDate
            lastPrice = entry.avgPrice

        while lastTime < midnightToday - DAY:
            lastTime += DAY
            history.append(blue.DBRow(history.header, [lastTime,
             lastPrice,
             lastPrice,
             lastPrice,
             0,
             0]))

        if len(new):
            history.extend(new)
        else:
            history.append(blue.DBRow(history.header, [blue.os.GetWallclockTimeNow(),
             lastPrice,
             lastPrice,
             lastPrice,
             0,
             0]))
        return history



    def GetAveragePrice(self, typeID, days = 7):
        history = self.GetPriceHistory(typeID)
        now = blue.os.GetWallclockTime()
        averagePrice = -1.0
        volume = 0
        priceVolume = 0.0
        for entry in history:
            if entry[0] < now - days * DAY:
                continue
            priceVolume += entry[3] * entry[4]
            volume += entry[4]

        if volume > 0:
            averagePrice = priceVolume / volume
        else:
            invType = cfg.invtypes.Get(typeID)
            averagePrice = float(invType.basePrice) / invType.portionSize
            if averagePrice <= 0.0:
                averagePrice = 1.0
        return round(float(averagePrice), 2)



    def GetMyOrders(self):
        return self.GetMarketProxy().GetCharOrders()



    def GetCorporationOrders(self):
        return self.GetMarketProxy().GetCorporationOrders()



    def DumpQuotes(self, typeID, amount = 1):
        typeName = cfg.invtypes.Get(typeID).name
        print '\n\nCurrently in station %s in solarsystem %s in constellation %s\n' % (session.stationid, session.solarsystemid2, session.constellationid)
        print 'Trying to buy %s units of %s from current position' % (amount, typeName)
        ranges = {1: 'station',
         3: 'solarsystem',
         4: 'constellation',
         5: 'region'}
        for (bidRange, name,) in ranges.iteritems():
            ask = self.GetBestAskInRange(typeID, bidRange, amount=amount)
            if ask is None:
                print '- In %15s' % name,
                print ': No one selling %s based within %s' % (typeName, name)
            else:
                print '- In %15s' % name,
                print ': Seller %s jumps away, selling %s units at %s ISK at station %s %s wide' % (int(sm.GetService('pathfinder').GetJumpCountFromCurrent(ask.solarSystemID)),
                 ask.volRemaining,
                 ask.price,
                 ask.stationID,
                 ranges[ask.range])

        print '\nTrying to buy %s units of %s from current position' % (amount, typeName)
        for (bidRange, name,) in ranges.iteritems():
            ask = self.GetBestAverageAsk(typeID, bidRange, amount=amount)
            if ask is None:
                print '- In %15s' % name,
                print ': No one selling %s based within %s' % (typeName, name)
            else:
                print '- In %15s' % name,
                print ': %s units of %s available at the average price of %s ISK %s jumps away at station %s' % (amount,
                 typeName,
                 ask[0],
                 int(sm.GetService('pathfinder').GetJumpCountFromCurrent(ask[2])),
                 ask[1])

        print '\nTrying to sell %s units of %s from current position:' % (amount, typeName)
        for (askRange, name,) in ranges.iteritems():
            bid = self.GetBestBidInRange(typeID, askRange, amount=amount)
            if bid is None:
                print '- In %15s' % name,
                print ': No one buying %s within here' % typeName
            else:
                print '- In %15s' % name,
                print ': Buyer buying %s units at %s ISK (located at %s %s jumps away)' % (bid.volRemaining,
                 bid.price,
                 bid.stationID,
                 int(sm.GetService('pathfinder').GetJumpCountFromCurrent(bid.solarSystemID)))




    def GetBestBid(self, typeID, locationID = None):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=locationID)
        bids = self.orderCache[typeID][1]
        if len(bids) > 0:
            return bids[0]



    def GetBestMatchableBid(self, typeID, stationID, amount = 1):
        station = sm.GetService('ui').GetStation(stationID)
        solarSystemID = station.solarSystemID
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=solarSystemID)
        bids = self.orderCache[typeID][1]
        if len(bids) == 0:
            return None
        candidates = dbutil.RowList([], bids.columns)
        jmpIdx = bids.columns.index('jumps')
        rngIdx = bids.columns.index('range')
        minIdx = bids.columns.index('minVolume')
        volIdx = bids.columns.index('volRemaining')
        staIdx = bids.columns.index('stationID')
        for x in bids:
            if x[jmpIdx] <= x[rngIdx] or x[rngIdx] == const.rangeStation and x[staIdx] == stationID and (x[minIdx] <= amount or x[volIdx] < x[minIdx] and amount == x[volIdx]):
                candidates.append(x)

        if len(candidates) > 0:
            return candidates[0]



    def GetBestAverageAsk(self, typeID, bidRange = None, amount = 1, locationID = None):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=locationID)
        if bidRange is None:
            bidRange = const.rangeRegion
        self.LogInfo('[GetBestAverageAsk]', 'typeID:', typeID, 'range:', bidRange, 'amount:', amount)
        self.RefreshOrderCache(typeID)
        saveAmount = amount
        amount = 1
        asks = self.orderCache[typeID][0]
        if len(asks) == 0:
            return 
        candidates = {}
        if bidRange == const.rangeRegion:
            for x in asks:
                if x.volRemaining >= amount:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        elif bidRange == const.rangeConstellation:
            for x in asks:
                if x.volRemaining >= amount and x.constellationID == session.constellationid:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        elif bidRange == const.rangeSolarSystem or session.stationid is None:
            for x in asks:
                if x.volRemaining >= amount and x.solarSystemID == session.solarsystemid2:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        else:
            for x in asks:
                if x.volRemaining >= amount and x.stationID == session.stationid:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        resultList = []
        amount = saveAmount
        for (stationID, askList,) in candidates.iteritems():
            saveAmount = amount
            averagePrice = 0.0
            cumulatedVolume = 0
            for ask in askList:
                solarsystemID = ask.solarSystemID
                available = min(ask.volRemaining, saveAmount)
                cumulatedVolume += available
                saveAmount -= available
                averagePrice += available * ask.price
                if saveAmount == 0:
                    break

            if cumulatedVolume < amount:
                continue
            averagePrice = averagePrice / cumulatedVolume
            resultList.append([averagePrice, stationID, solarsystemID])

        if len(resultList) == 0:
            return 
        resultList.sort()
        return resultList[0]



    def GetBestAskInRange(self, typeID, stationID, bidRange = None, amount = 1):
        if bidRange is None:
            bidRange = const.rangeRegion
        self.LogInfo('[GetBestAskInRange]', 'typeID:', typeID, 'range:', bidRange, 'amount:', amount)
        station = sm.GetService('ui').GetStation(stationID)
        solarSystemID = station.solarSystemID
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=solarSystemID)
        asks = self.orderCache[typeID][0]
        for x in asks:
            if x.jumps == 0 and x.stationID == stationID:
                jumps = -1
            else:
                jumps = x.jumps
            if jumps <= bidRange and x.volRemaining >= amount:
                return x




    def GetBestBidInRange(self, typeID, askRange = None, locationID = None, amount = 1):
        if askRange is None:
            askRange = const.rangeRegion
        if locationID is None:
            if askRange == const.rangeStation:
                locationID = session.stationid
                if locationID is None:
                    return 
            elif askRange == const.rangeSolarSystem:
                locationID = session.solarsystemid2
            elif askRange == const.rangeConstellation:
                locationID = session.constellationid
        self.LogInfo('[GetBestBidInRange]', 'typeID:', typeID, 'locationID:', locationID, 'range:', askRange, 'amount:', amount)
        self.RefreshOrderCache(typeID)
        bids = self.orderCache[typeID][1]
        if len(bids) == 0:
            return 
        if askRange == const.rangeStation:
            stationID = locationID
            solarsystemID = sm.RemoteSvc('map').GetStationExtraInfo()[0].Index('stationID')[stationID].solarSystemID
            constellationID = sm.GetService('map').GetItem(solarsystemID).locationID
        elif askRange == const.rangeSolarSystem:
            solarsystemID = locationID
            constellationID = sm.GetService('map').GetItem(solarsystemID).locationID
        elif askRange == const.rangeConstellation:
            constellationID = locationID
        stationIdx = bids.columns.index('stationID')
        rangeIdx = bids.columns.index('range')
        solIdx = bids.columns.index('solarSystemID')
        conIdx = bids.columns.index('constellationID')
        minIdx = bids.columns.index('minVolume')
        found = 0
        i = 0
        for x in bids:
            bidRange = x[rangeIdx]
            if askRange == const.rangeStation and amount >= x[minIdx] and (x[stationIdx] == stationID or bidRange == const.rangeSolarSystem and x[solIdx] == solarsystemID or bidRange == const.rangeConstellation and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeSolarSystem and amount >= x[minIdx] and (bidRange in [const.rangeStation, const.rangeSolarSystem] and x[solIdx] == solarsystemID or bidRange == const.rangeConstellation and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeConstellation and amount >= x[minIdx] and (bidRange in [const.rangeStation, const.rangeSolarSystem, const.rangeConstellation] and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeRegion and amount >= x[minIdx]:
                found = 1
                break
            i += 1

        if not found:
            return 
        self.LogInfo('[GetBestBidInRange] found:', bids[i])
        return bids[i]



    def GetOrders(self, typeID):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID)
        return [[self.orderCache[typeID][0], [['price', 1], ['jumps', 1]]], [self.orderCache[typeID][1], [['price', -1], ['jumps', 1]]]]



    def DumpOrdersForType(self, typeID):
        orders = self.GetOrders(typeID)
        sells = orders[0][0]
        buys = orders[1][0]
        if len(sells) > 0:
            dateIdx = sells[0].__columns__.index('issueDate')
        elif len(buys) > 0:
            dateIdx = buys[0].__columns__.index('issueDate')
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Market/MarketWindow/ExportNoData')})
            return 
        date = util.FmtDate(blue.os.GetWallclockTime())
        f = blue.os.CreateInstance('blue.ResFile')
        typeName = cfg.invtypes.Get(typeID).name
        invalidChars = '\\/:*?"<>|'
        for i in invalidChars:
            typeName = typeName.replace(i, '')

        directory = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL) + '\\EVE\\logs\\Marketlogs\\'
        filename = '%s-%s-%s.txt' % (cfg.evelocations.Get(session.regionid).name, typeName, util.FmtDate(blue.os.GetWallclockTime()).replace(':', ''))
        if not f.Open(directory + filename, 0):
            f.Create(directory + filename)
        first = 1
        for order in sells:
            if first:
                for key in order.__columns__:
                    f.Write('%s,' % key)

                f.Write('\r\n')
                first = 0
            for i in range(len(order)):
                first = 0
                if i == dateIdx:
                    f.Write('%s,' % util.FmtDate(order[i], 'el').replace('T', ' '))
                else:
                    f.Write('%s,' % order[i])

            f.Write('\r\n')

        for order in buys:
            if first:
                for key in order.__columns__:
                    f.Write('%s,' % key)

                f.Write('\r\n')
                first = 0
            for i in range(len(order)):
                if i == dateIdx:
                    f.Write('%s,' % util.FmtDate(order[i], 'el').replace('T', ' '))
                else:
                    f.Write('%s,' % order[i])

            f.Write('\r\n')

        f.Close()
        eve.Message('MarketExportInfo', {'sell': len(sells),
         'buy': len(buys),
         'typename': cfg.invtypes.Get(typeID).name,
         'filename': localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=filename),
         'directory': localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=directory)})



    def GetOrder(self, orderID, typeID = None):
        if typeID is not None:
            self.RefreshOrderCache(typeID)
            self.RefreshJumps(typeID)
        for asksAndBids in self.orderCache.values():
            (asks, bids, stamp,) = asksAndBids
            for order in asks:
                if order.orderID == orderID:
                    return order

            for order in bids:
                if order.orderID == orderID:
                    return order





    def RefreshJumps(self, typeID, refreshOrders = 0, locationID = None):
        if refreshOrders:
            self.RefreshOrderCache(typeID)
        asks = self.orderCache[typeID][0]
        bids = self.orderCache[typeID][1]
        systems = [ x.solarSystemID for x in asks ]
        jumps = self.pathfinder.GetJumpCountFromCurrent(systems, locationID)
        jmpIdx = asks.columns.index('jumps')
        i = 0
        for row in asks:
            row[jmpIdx] = jumps[i]
            i += 1

        systems = [ x.solarSystemID for x in bids ]
        jumps = self.pathfinder.GetJumpCountFromCurrent(systems, locationID)
        jmpIdx = bids.columns.index('jumps')
        i = 0
        for row in bids:
            row[jmpIdx] = jumps[i]
            i += 1

        asks.sort(lambda x, y, headers = asks.columns: SortAsks(x, y, headers))
        bids.sort(lambda x, y, headers = asks.columns: SortBids(x, y, headers))



    def ClearAll(self):
        self.orderCache = {}



    def RefreshAll(self):
        for typeID in self.orderCache.iterkeys():
            self.RefreshOrderCache(typeID)
            self.RefreshJumps(typeID)




    def RefreshOrderCache(self, typeID, forceUpdate = 0):
        self.LogInfo('[RefreshOrderCache] Refreshing', typeID)
        orders = self.GetMarketProxy().GetOrders(typeID)
        version = sm.GetService('objectCaching').GetCachedMethodCallVersion(None, 'marketProxy', 'GetOrders', (typeID,))
        if typeID in self.orderCache:
            if self.orderCache[typeID][2] == version:
                return 
        self.orderCache[typeID] = [orders[0], orders[1], version]
        self.LogInfo('[RefreshOrderCache] Refresh done:', len(orders[0]), 'asks and', len(orders[1]), 'bids')




