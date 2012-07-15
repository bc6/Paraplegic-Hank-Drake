#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/station/insurance/base_insurance.py
import base
import blue
import form
import listentry
import log
import service
import sys
import uix
import uiutil
import uthread
import util
import xtriui
import uicls
import uiconst
import localization

class InsuranceSvc(service.Service):
    __exportedcalls__ = {'CleanUp': [],
     'Reset': [],
     'GetContracts': []}
    __guid__ = 'svc.insurance'
    __notifyevents__ = []
    __servicename__ = 'insurance'
    __displayname__ = 'Insurance Service'
    __dependencies__ = ['corp', 'station']

    def __init__(self):
        service.Service.__init__(self)
        self.scroll = None
        self.insurance = None
        self.contracts = {}
        self.stuff = {}
        self.insurancePrice = {}

    def Run(self, memStream = None):
        self.LogInfo('Insurance Service Started')
        self.wnd = None
        self.CleanUp()

    def Stop(self, memStream = None):
        self.LogInfo('Insurance Medical Service')
        self.CleanUp()
        service.Service.Stop(self)

    def CleanUp(self):
        self.insurance = None
        self.contracts = {}
        self.stuff = {}

    def Reset(self):
        pass

    def GetInsuranceMgr(self):
        if self.insurance is not None:
            return self.insurance
        self.insurance = util.Moniker('insuranceSvc', session.stationid2)
        self.insurance.SetSessionCheck({'stationid2': session.stationid2})
        return self.insurance

    def GetContracts(self):
        self.contracts = {}
        if session.stationid2:
            contracts = self.GetInsuranceMgr().GetContracts()
        else:
            contracts = sm.RemoteSvc('insuranceSvc').GetContracts()
        for contract in contracts:
            self.contracts[contract.shipID] = contract

        if eve.session.corprole & (const.corpRoleJuniorAccountant | const.corpRoleAccountant) != 0:
            contracts = self.GetInsuranceMgr().GetContracts(1)
            for contract in contracts:
                self.contracts[contract.shipID] = contract

        return self.contracts

    def GetInsurancePrice(self, typeID):
        if typeID in self.insurancePrice:
            return self.insurancePrice[typeID]
        if session.stationid2:
            self.insurancePrice[typeID] = self.GetInsuranceMgr().GetInsurancePrice(typeID)
        else:
            self.insurancePrice[typeID] = sm.RemoteSvc('insuranceSvc').GetInsurancePrice(typeID)
        return self.insurancePrice[typeID]

    def GetItems(self):
        self.stuff = {}
        items = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = items.List()
        for item in items:
            if item.categoryID != const.categoryShip:
                continue
            if not item.singleton:
                continue
            if self.GetInsurancePrice(item.typeID) <= 0:
                continue
            self.stuff[item.itemID] = item

        if eve.session.corprole & (const.corpRoleAccountant | const.corpRoleJuniorAccountant) != 0:
            office = self.corp.GetOffice()
            if office is not None:
                items = sm.GetService('invCache').GetInventoryFromId(office.itemID, locationID=session.stationid2)
                items = items.List()
                for item in items:
                    if item.categoryID != const.categoryShip:
                        continue
                    if not item.singleton:
                        continue
                    if self.GetInsurancePrice(item.typeID) <= 0:
                        continue
                    self.stuff[item.itemID] = item

        return self.stuff


class InsuranceWindow(uicls.Window):
    __guid__ = 'form.InsuranceWindow'
    default_width = 400
    default_height = 300
    default_windowID = 'insurance'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.contracts = {}
        self.stuff = {}
        self.SetWndIcon('33_4', mainTop=-8)
        self.SetMinSize([350, 270])
        self.SetCaption(localization.GetByLabel('UI/Insurance/InsuranceWindow/Title'))
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Insurance/InsuranceWindow/Title'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.scope = 'station'
        btns = uicls.ButtonGroup(btns=[(localization.GetByLabel('UI/Insurance/InsuranceWindow/Commands/Insure'),
          self.InsureFromBtn,
          None,
          81)], line=1)
        self.sr.main.children.append(btns)
        self.sr.insureBtns = btns
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'insurance'
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 30}
        self.ShowInsuranceInfo()

    def BlueprintComboChange(self):
        pass

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def GetInsuranceName(self, fraction):
        fraction = '%.1f' % fraction
        return {'0.5': localization.GetByLabel('UI/Insurance/QuoteWindow/Basic'),
         '0.6': localization.GetByLabel('UI/Insurance/QuoteWindow/Standard'),
         '0.7': localization.GetByLabel('UI/Insurance/QuoteWindow/Bronze'),
         '0.8': localization.GetByLabel('UI/Insurance/QuoteWindow/Silver'),
         '0.9': localization.GetByLabel('UI/Insurance/QuoteWindow/Gold'),
         '1.0': localization.GetByLabel('UI/Insurance/QuoteWindow/Platinum')}.get(fraction, fraction)

    def GetItemMenu(self, entry):
        item = entry.sr.node.info
        contract = self.contracts.get(item.itemID, None)
        m = []
        if contract is None:
            if item.ownerID == eve.session.charid or item.ownerID == eve.session.corpid and eve.session.corprole & const.corpRoleAccountant == const.corpRoleAccountant:
                m = [(uiutil.MenuLabel('UI/Insurance/InsuranceWindow/Commands/Insure'), self.Insure, (item,))]
        elif contract.ownerID == eve.session.charid:
            m = [(uiutil.MenuLabel('UI/Insurance/InsuranceWindow/Commands/CancelInsurance'), self.UnInsure, (item,))]
        if m != []:
            m.append(None)
        m += sm.GetService('menu').InvItemMenu(item, 1)
        return m

    def ShowInsuranceInfo(self):
        uthread.pool('Insurance :: ShowInsuranceInfo', self._ShowInsuranceInfo)

    def _ShowInsuranceInfo(self):
        insurance = sm.GetService('insurance')
        self.contracts = insurance.GetContracts()
        self.stuff = insurance.GetItems()
        self.SetHint()
        owners = [eve.session.charid]
        if eve.session.corprole & (const.corpRoleJuniorAccountant | const.corpRoleAccountant) != 0:
            owners.append(eve.session.corpid)
        scrolllist = []
        itemList = []
        for ownerID in owners:
            for itemID in self.stuff:
                item = self.stuff[itemID]
                if item.ownerID != ownerID:
                    continue
                if item.categoryID == const.categoryShip:
                    itemList.append(item.itemID)

        cfg.evelocations.Prime(itemList)
        for ownerID in owners:
            for itemID in self.stuff:
                item = self.stuff[itemID]
                if item.ownerID != ownerID:
                    continue
                itemName = ''
                if item.categoryID == const.categoryShip:
                    shipName = cfg.evelocations.GetIfExists(item.itemID)
                    if shipName is not None:
                        itemName = shipName.locationName
                contract = None
                if self.contracts.has_key(item.itemID):
                    contract = self.contracts[item.itemID]
                if item.ownerID == eve.session.corpid:
                    name = localization.GetByLabel('UI/Insurance/InsuranceWindow/OwnedByCorporation', typeID=item.typeID)
                else:
                    name = cfg.invtypes.Get(item.typeID).name
                if contract is None:
                    label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                     '-',
                     '-',
                     '-',
                     itemName)
                else:
                    label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                     util.FmtDate(contract.startDate, 'ls'),
                     util.FmtDate(contract.endDate, 'ls'),
                     self.GetInsuranceName(contract.fraction),
                     itemName)
                scrolllist.append(listentry.Get('Item', {'info': item,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'label': label,
                 'getIcon': 1,
                 'GetMenu': self.GetItemMenu}))

        self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Type'),
         localization.GetByLabel('UI/Common/DateWords/FromDate'),
         localization.GetByLabel('UI/Common/DateWords/ToDate'),
         localization.GetByLabel('UI/Insurance/InsuranceWindow/Level'),
         localization.GetByLabel('UI/Insurance/InsuranceWindow/Name')])
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Insurance/InsuranceWindow/NothingToInsure'))

    def UnInsure(self, item, *args):
        if item is None or not len(item):
            return
        if eve.Message('InsAskUnInsure', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('insurance').GetInsuranceMgr().UnInsureShip(item.itemID)
        self.ShowInsuranceInfo()

    def GetQuoteForShip(self, ship):
        if ship is None:
            raise UserError('InsCouldNotFindItem')
        insurancePrice = sm.GetService('insurance').GetInsurancePrice(ship.typeID)
        fivePC = float(insurancePrice) * 0.05
        cost = fivePC
        fraction = 0.5
        quotes = util.Rowset(['fraction', 'amount'])
        while fraction <= 1.0:
            quotes.lines.append([fraction, cost])
            fraction += 0.1
            cost += fivePC

        return quotes

    def GetSelected(self):
        return [ node.info for node in self.sr.scroll.GetSelected() ]

    def InsureFromBtn(self, *args):
        self.Insure(None)

    def Insure(self, item, *args):
        if item is None or not len(item):
            item = self.GetSelected()
            if not item:
                eve.Message('SelectShipToInsure')
                return
            item = item[0]
        isCorpItem = 0
        if item.ownerID == eve.session.corpid:
            isCorpItem = 1
        if item.ownerID == eve.session.corpid:
            msg = 'InsAskAcceptTermsCorp'
        else:
            msg = 'InsAskAcceptTerms'
        if eve.Message(msg, {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        quotes = self.GetQuoteForShip(item)
        format = []
        stati = {}
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Insurance/QuoteWindow/SelectInsuranceLevel')})
        format.append({'type': 'push'})
        insurancePrice = sm.GetService('insurance').GetInsurancePrice(item.typeID)
        for quote in quotes:
            text = localization.GetByLabel('UI/Insurance/QuoteWindow/Line', name=self.GetInsuranceName(quote.fraction), cost=localization.GetByLabel('UI/Common/Cost'), amount=util.FmtISK(quote.amount), payout=localization.GetByLabel('UI/Insurance/QuoteWindow/EstimatedPayout'), price=util.FmtISK(quote.fraction * insurancePrice))
            format.append({'type': 'checkbox',
             'setvalue': quote.fraction == 0.5,
             'key': str(quote.fraction),
             'text': text,
             'group': 'quotes'})
            format.append({'type': 'push',
             'height': 12})

        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Insurance/QuoteWindow/Title'), 1, None, uiconst.OKCANCEL, [left, top], 500)
        if retval is not None:
            try:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Insurance/ProgressWindow/Insuring'), '', 0, 2)
                blue.pyos.synchro.Yield()
                fraction = float(retval['quotes'])
                for quote in quotes:
                    if str(quote.fraction) != str(fraction):
                        continue
                    try:
                        sm.GetService('insurance').GetInsuranceMgr().InsureShip(item.itemID, quote.amount, isCorpItem)
                    except UserError as e:
                        if e.msg == 'InsureShipFailedSingleContract':
                            ownerName = e.args[1]['ownerName']
                            if eve.Message('InsureShipAlreadyInsured', {'ownerName': ownerName}, uiconst.YESNO) == uiconst.ID_YES:
                                sm.GetService('insurance').GetInsuranceMgr().InsureShip(item.itemID, quote.amount, isCorpItem, voidOld=True)
                                self.ShowInsuranceInfo()
                                return
                            else:
                                return
                        if e.msg != 'InsureShipFailed':
                            raise 
                        self.ShowInsuranceInfo()
                        raise 

                    self.ShowInsuranceInfo()
                    return

            finally:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Insurance/ProgressWindow/Insuring'), '', 1, 2)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Insurance/ProgressWindow/Insuring'), '', 2, 2)
                blue.pyos.synchro.Yield()