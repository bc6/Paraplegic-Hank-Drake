import service
import util
import storeConst
import blue
import form

class storeSvc(service.Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.store'
    __exportedcalls__ = {}
    __dependencies__ = ['objectCaching']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.PopulatePaperdollGenderDict()
        self.preparedOffers = None
        self.offersByTypeIDs = {}
        self.storeClosed = None



    def PopulatePaperdollGenderDict(self):
        self.genderByTypeID = {}
        for resource in cfg.paperdollResources:
            typeID = resource.typeID
            if typeID is None:
                continue
            if typeID in self.genderByTypeID:
                genderInDict = self.genderByTypeID.get(typeID)
                if genderInDict != resource.resGender:
                    self.genderByTypeID[typeID] = None
            else:
                self.genderByTypeID[typeID] = resource.resGender




    def AcceptOffer(self, offerID, quantity):
        if session.stationid2 is None:
            raise UserError('VStoreNotAvailable')
        if offerID is None or quantity < 0:
            self.LogError('Trying to accept an offer without offerID or quantity', offerID, quantity)
            return 
        try:
            return sm.RemoteSvc('storeServer').AcceptOffer(offerID, quantity)
        except UserError as e:
            if e.msg == 'OfferNotAvailableNow':
                self.objectCaching.InvalidateCachedMethodCalls([('storeServer', 'GetAvailableOffers', ())])
            elif e.msg == 'VG_STORE_CLOSED':
                self.storeClosed = blue.os.GetWallclockTime()
                self.CloseStoreWindow()
            raise 



    def CheckStoreOpen(self):
        if self.storeClosed and blue.os.GetWallclockTime() - self.storeClosed < const.MIN * 15:
            self.CloseStoreWindow()
            raise UserError('VG_STORE_CLOSED')
        else:
            self.storeClosed = None



    def CloseStoreWindow(self):
        storeWnd = form.VirtualGoodsStore.GetIfOpen()
        if storeWnd is not None and not storeWnd.destroyed:
            storeWnd.CloseByUser()
        buyWnd = form.BuyVGoodsWindow.GetIfOpen()
        if buyWnd is not None and not buyWnd.destroyed:
            buyWnd.CloseByUser()



    def GetPreparedOffers(self, reloadOffers = None):
        self.CheckStoreOpen()
        if reloadOffers:
            self.preparedOffers = None
        if self.preparedOffers is not None:
            return self.preparedOffers
        try:
            availableOffers = sm.RemoteSvc('storeServer').GetAvailableOffers()
        except UserError as e:
            if e.msg == 'VG_STORE_CLOSED':
                self.storeClosed = blue.os.GetWallclockTime()
                self.CloseStoreWindow()
            raise 
        self.preparedOffers = {}
        self.offersByTypeIDs = {}
        for (offerID, offerInfo,) in availableOffers.iteritems():
            if not offerInfo.goods:
                continue
            offeredTypeID = None
            numberOffered = None
            genderForType = None
            bpME = None
            bpPE = None
            bpRuns = None
            priceMPLEX = 0
            corruptOffer = False
            try:
                for item in offerInfo.goods:
                    if item.offered == True:
                        if offeredTypeID is not None:
                            self.LogError("The store is offering more than one item, it shouldn't be doing that", item)
                            corruptOffer = True
                            break
                        if item.argumentType != storeConst.GOODTYPE_EVETYPEID:
                            self.LogError("The store is offering non-types, it shouldn't be doing that", item)
                            corruptOffer = True
                            break
                        offeredTypeID = item.argumentValue
                        numberOffered = item.amount
                        genderForType = self.genderByTypeID.get(offeredTypeID, None)
                        bpME = item.details1
                        bpPE = item.details2
                        bpRuns = item.details3
                        if offeredTypeID not in cfg.invtypes:
                            raise RuntimeError('Invalid offer because typeID not in invtypes', offeredTypeID, offerID)
                    else:
                        if item.argumentType != storeConst.GOODTYPE_CREDITS:
                            self.LogError("The store is asking for non-credits, it shouldn't be doing that", item)
                            corruptOffer = True
                            break
                        if item.argumentValue == const.creditsISK:
                            self.LogError("The store is asking for ISK, it shouldn't be doing that", item)
                            corruptOffer = True
                            break
                        elif item.argumentValue == const.creditsAURUM:
                            priceMPLEX += item.amount

            except Exception as e:
                self.LogError('The was something wrong with the offer - ', e)
                corruptOffer = True
            if corruptOffer:
                self.LogError('The offer was corrupt, so we are ignoring it', offerID)
                continue
            if offeredTypeID:
                if offeredTypeID in self.offersByTypeIDs:
                    (id, price,) = self.offersByTypeIDs[offeredTypeID]
                    if price > priceMPLEX:
                        self.offersByTypeIDs[offeredTypeID] = (offerID, priceMPLEX)
                else:
                    self.offersByTypeIDs[offeredTypeID] = (offerID, priceMPLEX)
                self.preparedOffers[offerID] = util.KeyVal(offerID=offerID, typeID=offeredTypeID, numberOffered=numberOffered, price=priceMPLEX, genderRestrictions=genderForType, bpME=bpME, bpPE=bpPE, bpRuns=bpRuns)

        return self.preparedOffers



    def GetAvailableLocalPlexes(self):
        plexes = sm.GetService('invCache').GetInventory(const.containerHangar).List(flag=const.flagHangar, typeID=const.typePilotLicence)
        return [ i for i in sorted(plexes, key=lambda p: p.stacksize, reverse=True) ]



    def GetPlexToAURExchangeRate(self):
        return const.Plex2AurExchangeRatio



    def SellLocalPlexForAur(self, plexes, qty):
        sm.GetService('invCache').GetInventoryMgr().ConvertPlexToCurrency(plexes, qty)



    def TryBuyType(self, typeID):
        self.GetPreparedOffers()
        if typeID not in self.offersByTypeIDs:
            raise UserError('VStoreTypeNotForSale')
        if not session.stationid2:
            raise UserError('VStoreNotAvailable')
        (offerID, price,) = self.offersByTypeIDs[typeID]
        self.GetBuyWnd(offerID)



    def GetBuyWnd(self, offerID, *args):
        offerKV = self.preparedOffers.get(offerID, None)
        if offerKV is None:
            raise UserError('VStoreTypeNotForSale')
        wnd = form.BuyVGoodsWindow.GetIfOpen()
        if wnd:
            if wnd.offerKV != offerKV:
                wnd.LoadWnd(offerKV=offerKV)
            wnd.Maximize()
        else:
            form.BuyVGoodsWindow.Open(offerKV=offerKV)




