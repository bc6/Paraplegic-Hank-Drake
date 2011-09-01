import xtriui
import uthread
import uix
import uiutil
import form
import util
import uicls
import uiconst

class PVPTrade(uicls.Window):
    __guid__ = 'form.PVPTrade'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        tradeSession = attributes.tradeSession
        self.sr.session = tradeSession
        self.scope = 'station'
        self.tradedShips = []
        self.SetMinSize([300, 370])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.DefineButtons(uiconst.OKCANCEL, okLabel=mls.UI_CMD_ACCEPT, okFunc=self.OnClickAccept, cancelFunc=self.Cancel)
        sessionData = tradeSession.List()
        herID = sessionData.traders[(not sessionData.traders.index(eve.session.charid))]
        myinfo = cfg.eveowners.Get(eve.session.charid)
        herinfo = cfg.eveowners.Get(herID)
        my = sm.GetService('window').GetWindow("%s's offer_%s" % (myinfo.name, sessionData.tradeContainerID), create=1, decoClass=self.GetOfferViewClass(), id_=sessionData.tradeContainerID, ownerID=eve.session.charid, shell=tradeSession)
        my.state = uiconst.UI_HIDDEN
        her = sm.GetService('window').GetWindow("%s's offer_%s" % (herinfo.name, sessionData.tradeContainerID), create=1, decoClass=self.GetOfferViewClass(), id_=sessionData.tradeContainerID, ownerID=sessionData.traders[(not sessionData.traders.index(eve.session.charid))], shell=tradeSession)
        her.state = uiconst.UI_HIDDEN
        her.SetWndIcon()
        my.SetWndIcon()
        for each in my.sr.topParent.children:
            each.left += 27
            each.top += 6

        for each in her.sr.topParent.children:
            each.left += 27
            each.top += 6

        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=4)
        self.sr.myParent = uicls.Container(name='myParent', parent=self.sr.main, align=uiconst.TOTOP, height=165)
        myImgCont = uicls.Container(name='myImgCont', parent=my.sr.topParent, align=uiconst.TOPLEFT, width=64, height=64, padding=(2, 0, 0, 0))
        self.sr.myAccept = uicls.Icon(icon='ui_38_16_193', parent=my.sr.topParent, left=67, top=-1)
        uiutil.GetOwnerLogo(myImgCont, session.charid, size=64, noServerCall=True)
        uicls.Label(text=myinfo.name, parent=my.sr.topParent, left=82, top=0, fontsize=12, state=uiconst.UI_DISABLED, bold=1)
        self.sr.myMoney = uicls.Label(text=myinfo.name, parent=my.sr.topParent, left=const.defaultPadding + 2, top=-2, width=200, autowidth=False, fontsize=12, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        self.sr.line = uicls.Line(parent=self.sr.main, align=uiconst.TOTOP)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=4)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOBOTTOM, height=2)
        self.sr.otherParent = uicls.Container(name='otherParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.herAccept = uicls.Icon(icon='ui_38_16_193', parent=her.sr.topParent, left=67, top=-1)
        herImgCont = uicls.Container(name='herImgCont', parent=her.sr.topParent, align=uiconst.TOPLEFT, width=64, height=64, padding=(2, 0, 0, 0))
        uiutil.GetOwnerLogo(herImgCont, herID, size=64, noServerCall=True)
        uicls.Label(text=herinfo.name, parent=her.sr.topParent, left=82, top=0, fontsize=12, state=uiconst.UI_DISABLED, bold=1)
        self.sr.herMoney = uicls.Label(text=herinfo.name, parent=her.sr.topParent, left=const.defaultPadding + 2, top=-2, width=200, autowidth=False, fontsize=12, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        self.sr.my = my
        self.sr.her = her
        self.sr.herinfo = herinfo
        offerBtn = uicls.Button(parent=my.sr.topParent, label=mls.UI_CMD_OFFERMONEY, func=self.OnClickOfferMoney, args=None, idx=0, pos=(2, 2, 0, 0), align=uiconst.TOPRIGHT)
        uiutil.Transplant(self.sr.my, self.sr.myParent)
        self.sr.my.left = self.sr.my.top = -1
        self.sr.my.width = self.sr.my.height = -1
        self.sr.my.SetAlign(uiconst.TOALL)
        self.sr.my.HideUnderlay()
        self.sr.my.HideHeader()
        self.sr.my.HideHeaderButtons()
        self.sr.my.MakeUnResizeable()
        self.sr.my.MakeUnKillable()
        uiutil.Transplant(self.sr.her, self.sr.otherParent)
        self.sr.her.left = self.sr.her.top = -1
        self.sr.her.width = self.sr.her.height = -1
        self.sr.her.SetAlign(uiconst.TOALL)
        self.sr.her.HideUnderlay()
        self.sr.her.HideHeader()
        self.sr.her.HideHeaderButtons()
        self.sr.her.MakeUnResizeable()
        self.sr.her.MakeUnKillable()
        self.sr.myIx = sessionData.traders.index(eve.session.charid)
        self.sr.herIx = sessionData.traders.index(herID)
        self.OnMoneyOffer([0, 0])
        my.state = uiconst.UI_PICKCHILDREN
        her.state = uiconst.UI_PICKCHILDREN
        self.SetCaption(self.GetWindowCaptionText())
        uthread.new(self.OnScale_)



    def GetOfferViewClass(self):
        return form.PVPOfferView



    def OnClose_(self, *args):
        if self and getattr(self, 'sr', None):
            if self.sr.my:
                self.sr.my.SelfDestruct()
            if self.sr.her:
                self.sr.her.SelfDestruct()



    def Cancel(self, *etc):
        if self.sr.session and eve.Message('ConfirmCancelTrade', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            if self and not self.destroyed and hasattr(self, 'sr'):
                tmp = self.sr.session
                self.sr.session = None
                tmp.Abort()
            else:
                eve.Message('TradeNotCanceled')


    CloseX = Cancel

    def OnClickAccept(self, *etc):
        currentState = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED].index(self.sr.myAccept.state)
        self.tradedShips = []
        tradeItems = self.sr.session.List().items
        for item in tradeItems:
            if cfg.invgroups.Get(item.groupID).Category().id == const.categoryShip:
                self.tradedShips.append(item.itemID)
                sm.GetService('gameui').KillCargoView(item.itemID)

        try:
            self.sr.session.ToggleAccept(not currentState)
        except UserError as what:
            if not what.msg.startswith('TradeShipWarning'):
                raise 
            (msgName, msgDict,) = (what.msg, what.dict)
            if msgName is not None:
                if eve.Message('TradeShipWarning', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                    self.sr.session.ToggleAccept(not currentState, forceTrade=True)



    def GetWindowCaptionText(self):
        if self.sr.session.IsCEOTrade():
            return mls.UI_STATION_TEXT36 % {'name': self.sr.herinfo.name}
        return mls.UI_STATION_TEXT37 % {'name': self.sr.herinfo.name}



    def OnScale_(self, *args):
        (l, t, w, h,) = self.sr.main.GetAbsolute()
        self.sr.myParent.height = h / 2



    def OnStateToggle(self, states):
        self.sr.myAccept.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[states[self.sr.myIx]]
        self.sr.herAccept.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[states[self.sr.herIx]]
        if states[0] and states[1]:
            self.sr.my.invReady = 0
            self.sr.her.invReady = 0
            self.SelfDestruct()



    def OnMoneyOffer(self, money):
        myMoney = util.FmtISK(money[self.sr.myIx])
        if money[self.sr.myIx] > 0:
            myMoney = '<b><color=0xffff5555>%s</color></b>' % myMoney
        else:
            myMoney = '<color=gray>%s</color>' % myMoney
        herMoney = util.FmtISK(money[self.sr.herIx])
        if money[self.sr.herIx] > 0:
            herMoney = '<b><color=0xff55ff55>%s</color></b>' % herMoney
        else:
            herMoney = '<color=gray>%s</color>' % herMoney
        self.sr.myMoney.text = '<right>%s: %s' % (mls.UI_GENERIC_MONEY, myMoney)
        self.sr.herMoney.text = '<right>%s: %s' % (mls.UI_GENERIC_MONEY, herMoney)
        self.OnStateToggle([0, 0])



    def OnClickOfferMoney(self, *etc):
        self.sr.session.ToggleAccept(False)
        ret = uix.QtyPopup(sm.GetService('wallet').GetWealth(), 0, 0, digits=2)
        if ret is not None and self is not None and not self.destroyed:
            self.sr.session.OfferMoney(ret['qty'])



    def OnTradeComplete(self):
        for itemID in self.tradedShips:
            sm.GetService('gameui').KillCargoView(itemID)

        eve.Message('TradeComplete', {'name': self.sr.herinfo.name})
        self.sr.my.invReady = 0
        self.sr.her.invReady = 0
        self.SelfDestruct()



    def OnCancel(self):
        eve.Message('TradeCancel', {'name': self.sr.herinfo.name})
        self.sr.my.invReady = 0
        self.sr.her.invReady = 0
        self.SelfDestruct()




class PVPOfferView(form.VirtualInvWindow):
    __guid__ = 'form.PVPOfferView'

    def ApplyAttributes(self, attributes):
        form.VirtualInvWindow.ApplyAttributes(self, attributes)
        id = attributes.id_
        name = attributes.displayName
        ownerID = attributes.ownerID
        shell = attributes.shell
        self.minHeight = 65
        self.scope = 'station'
        self.viewOnly = 1
        self.enableQuickFilter = False
        self.Startup(id, name, ownerID, shell)



    def Startup(self, id_, name, ownerID, shell):
        self.id = self.itemID = id_
        self.displayName = name
        self.scope = 'station'
        self.hasCapacity = 0
        self.ownerID = ownerID
        self.sr.shell = shell
        self.flags = [(const.ixOwnerID, self.ownerID)]
        form.VirtualInvWindow.Startup(self)



    def GetShell(self):
        return self.sr.shell



    def List(self):
        return self.sr.shell.List().items



    def IsMine(self, rec):
        return rec.ownerID == self.ownerID and self.id == rec.locationID



    def IsLockableContainer(self):
        return False



    def _Add(self, rec, *args, **kwargs):
        if rec.itemID == util.GetActiveShip():
            raise UserError('PeopleAboardShip')
        if cfg.invtypes.Get(rec.typeID).Group().Category().id == const.categoryShip:
            foundShip = 0
            hangar = eve.GetInventory(const.containerHangar).List()
            for item in hangar:
                if item.itemID != rec.itemID and cfg.invtypes.Get(rec.typeID).Group().Category().id == const.categoryShip:
                    foundShip = 1

            if not foundShip and eve.Message('ConfirmGiveAwayOnlyShip', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return 
            sm.GetService('gameui').KillCargoView(rec.itemID)
        form.VirtualInvWindow._Add(self, rec, *args, **kwargs)



    def _MultiAdd(self, itemIDs, sourceLocation, flag = None):
        activeShipID = util.GetActiveShip()
        for itemID in itemIDs:
            if itemID == activeShipID:
                raise UserError('PeopleAboardShip')

        form.VirtualInvWindow._MultiAdd(self, itemIDs, sourceLocation, flag=flag)




class CEOVCEOTrade(PVPTrade):
    __guid__ = 'form.CEOVCEOTrade'

    def Startup(self, declaredByID, againstID, containerid):
        ceoID = None
        if declaredByID is not None and againstID is not None:
            aggressorIDs = [declaredByID, againstID]
            aggressorIDs.remove(eve.session.corpid)
            corporation = sm.RemoteSvc('corpmgr').GetCorporations(aggressorIDs[0])
            ceoID = corporation.ceoID
        stationsBtn = uiutil.GetChild(self, 'StationsBtn')
        uicls.Container(stationsBtn).OnClick = self.SelectStation
        stationsBtn.state = uiconst.UI_NORMAL
        res = PVPTrade.Startup(self, ceoID, containerid)
        stationsBtn.parent.width = stationsBtn.width * 3
        return res



    def SelectStation(self, *args):
        stationListing = []
        stations = sm.RemoteSvc('corpmgr').GetCorporationStations()
        for station in stations:
            if station.itemID in self.shell.GetStationIDs():
                continue
            stationListing.append([mls.UI_STATION_STATIONINSOLARSYSTEM % {'stationname': cfg.evelocations.Get(station.itemID).name,
              'solarsystemname': cfg.evelocations.Get(station.locationID).name}, station.itemID, station.typeID])

        ret = uix.ListWnd(stationListing, 'station')
        if ret:
            self.shell.Add(ret[1])



    def GetOfferViewClass(self):
        return form.CEOVCEOOfferView



    def GetWindowCaptionText(self):
        return mls.UI_STATION_TEXT38 % {'name': cfg.eveowners.Get(self.her.id).name}




class CEOVCEOOfferView(PVPOfferView):
    __guid__ = 'form.CEOVCEOOfferView'
    __nonpersistvars__ = ['corporationID']

    def init(self):
        PVPOfferView.init(self)



    def Startup(self, id_, name, ownerID, shell):
        PVPOfferView.startup(self, id_, name, ownerID, shell)
        self.corporationID = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(ownerID)



    def _Add(self, icon, *etc):
        if self.corporationID is None:
            self.corporationID = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(self.ownerID)
        if icon.rec[const.ixOwnerID] in [self.ownerID, self.corporationID]:
            form.VirtualInvWindow._Add(self, icon, *etc)



    def RemoveStation(self, itemID):
        if self.ownerID == eve.session.charid:
            self.shell.RemoveStationID(itemID)
        else:
            eve.Message('CannotRemoveItem')




