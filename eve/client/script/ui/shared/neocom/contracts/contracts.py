import blue
import dbg
import xtriui
import uix
import uiutil
import uthread
import form
import listentry
import service
import util
import base
import uicls
import uiconst
import sys
import copy
import log
from collections import defaultdict
from contractutils import *
RESULTS_PER_PAGE = 100
BCancel = 0
BAccept = 1
BReject = 2
BComplete = 3
BDelete = 4
BSucceed = 5
BFail = 6
BGetItems = 7
BGetMoney = 8
BAcceptForCorp = 9
BPlaceBid = 10
MIN_CONTRACT_MONEY = 1000
HISTORY_LENGTH = 10
MAX_IGNORED = 1000
CACHE_TIME = 10

def GetSecurityClassText(securityClass):
    txt = {const.securityClassZeroSec: '<color=0xffbb0000>%s</color>' % mls.UI_GENERIC_NULLSEC,
     const.securityClassLowSec: '<color=0xffbbbb00>%s</color>' % mls.UI_GENERIC_LOWSEC,
     const.securityClassHighSec: '<color=0xff00bb00>%s</color>' % mls.UI_GENERIC_HIGHSEC}.get(securityClass, mls.UI_GENERIC_UNKNOWN)
    return txt



class ContractsSvc(service.Service):
    __exportedcalls__ = {'GetContract': {},
     'AcceptContract': {},
     'DeleteContract': {},
     'CompleteContract': {},
     'FailContract': {},
     'RejectContract': {},
     'CreateContract': {},
     'PlaceBid': {},
     'FinishAuction': {},
     'GetMarketTypes': {},
     'NumOutstandingContracts': {},
     'GetItemsInContainer': {},
     'GetItemsInStation': {},
     'DeleteNotification': {},
     'CollectMyPageInfo': {},
     'ClearCache': {},
     'OpenJournal': [service.ROLE_IGB | service.ROLE_ANY],
     'OpenCreateContract': [service.ROLE_IGB | service.ROLE_ANY],
     'OpenAvailableTab': [service.ROLE_IGB | service.ROLE_ANY],
     'AddIgnore': {},
     'OpenIgnoreList': [service.ROLE_IGB],
     'GetMessages': {},
     'DeliverCourierContractFromItemID': {},
     'FindCourierContractFromItemID': {}}
    __guid__ = 'svc.contracts'
    __notifyevents__ = ['ProcessSessionChange',
     'OnContractAssigned',
     'OnContractCompleted',
     'OnContractAccepted',
     'OnContractRejected',
     'OnContractFailed',
     'OnContractOutbid',
     'OnContractBuyout']
    __servicename__ = 'Contracts'
    __displayname__ = 'Contracts Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def __init__(self):
        service.Service.__init__(self)
        self.detailsByRegionByTypeFlag = {}
        self.contractID = None
        self.markettypes = None
        self.contracts = {}
        self.myPageInfo = None
        self.myExpiredContractList = None
        self.contractsInProgress = {}
        self.messages = []
        self.inited = False



    def Run(self, memStream = None):
        self.contractSvc = sm.ProxySvc('contractProxy')
        self.Init()



    def Stop(self, memStream = None):
        wnd = sm.GetService('window').GetWindow('contracts')
        if wnd is not None:
            wnd.CloseX()



    def Init(self):
        if session.charid and not self.inited:
            uthread.new(self.NeocomBlink)
            self.inited = True



    def GetContractsInProgress(self):
        return self.contractsInProgress



    def GetContractsBookmarkMenu(self):
        contractsMenu = []
        stationsPickup = set()
        stationsDropoff = set()
        for (contractID, contract,) in self.contractsInProgress.iteritems():
            if contract[-1] < blue.os.GetTime():
                continue
            if sm.GetService('ui').GetStation(contract[0]).solarSystemID == session.solarsystemid2:
                stationsPickup.add(contract[0])
            if sm.GetService('ui').GetStation(contract[1]).solarSystemID == session.solarsystemid2:
                stationsDropoff.add(contract[1])

        for stationID in stationsPickup:
            contractsMenu.append((mls.UI_CONTRACTS_COURIERPICKUP % {'station': cfg.evelocations.Get(stationID).name}, ('isDynamic', sm.GetService('menu').CelestialMenu, (stationID,
               None,
               None,
               0,
               None,
               None,
               None))))

        for stationID in stationsDropoff:
            contractsMenu.append((mls.UI_CONTRACTS_COURIERDELIVERY % {'station': cfg.evelocations.Get(stationID).name}, ('isDynamic', sm.GetService('menu').CelestialMenu, (stationID,
               None,
               None,
               0,
               None,
               None,
               None))))

        return contractsMenu



    def FindRelated(self, typeID, groupID, categoryID, issuerID, locationID, endLocationID, contractType = None, reset = True, *args):
        if contractType != const.conTypeCourier:
            contractType = CONTYPE_AUCTIONANDITEMECHANGE
        self.OpenSearchTab(typeID, groupID, categoryID, issuerID, locationID, endLocationID, const.conAvailPublic, contractType, reset)



    def GetRelatedMenu(self, contract, typeID, reset = True):
        m = []
        startConstellationID = sm.GetService('map').GetItem(contract.startSolarSystemID).locationID
        if typeID and contract.type != const.conTypeCourier:
            itemType = cfg.invtypes.Get(typeID)
            m += [(mls.UI_CONTRACTS_RELATED_SAMETYPE, self.FindRelated, (typeID,
               None,
               None,
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [(mls.UI_CONTRACTS_RELATED_SAMEGROUP, self.FindRelated, (None,
               itemType.groupID,
               None,
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [(mls.UI_CONTRACTS_RELATED_SAMECATEGORY, self.FindRelated, (None,
               None,
               itemType.Group().categoryID,
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [None]
        m += [(mls.UI_CONTRACTS_RELATED_FROMSAMEISSUER, self.FindRelated, (None,
           None,
           None,
           contract.issuerCorpID if contract.forCorp else contract.issuerID,
           None,
           None,
           contract.type,
           reset))]
        m += [None]
        m += [(mls.UI_CONTRACTS_RELATED_FROMSAMESOLARSYSTEM, self.FindRelated, (None,
           None,
           None,
           None,
           contract.startSolarSystemID,
           None,
           contract.type,
           reset))]
        m += [(mls.UI_CONTRACTS_RELATED_FROMSAMECONSTELLATION, self.FindRelated, (None,
           None,
           None,
           None,
           startConstellationID,
           None,
           contract.type,
           reset))]
        m += [(mls.UI_CONTRACTS_RELATED_FROMSAMEREGION, self.FindRelated, (None,
           None,
           None,
           None,
           contract.startRegionID,
           None,
           contract.type,
           reset))]
        if contract.type == const.conTypeCourier:
            endConstellationID = sm.GetService('map').GetItem(contract.endSolarSystemID).locationID
            m += [None]
            m += [(mls.UI_CONTRACTS_RELATED_TOSAMESOLARSYSTEM, self.FindRelated, (None,
               None,
               None,
               None,
               None,
               contract.endSolarSystemID,
               contract.type,
               reset))]
            m += [(mls.UI_CONTRACTS_RELATED_TOSAMECONSTELLATION, self.FindRelated, (None,
               None,
               None,
               None,
               None,
               endConstellationID,
               contract.type,
               reset))]
            m += [(mls.UI_CONTRACTS_RELATED_TOSAMEREGION, self.FindRelated, (None,
               None,
               None,
               None,
               None,
               contract.endRegionID,
               contract.type,
               reset))]
        return m



    def NeocomBlink(self):
        kv = self.contractSvc.GetLoginInfo()
        txt1 = txt2 = ''
        func = None
        ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
        assignedToMe = []
        for contract in kv.assignedToMe:
            if contract.issuerID not in ignoreList:
                assignedToMe.append(contract.contractID)

        if len(assignedToMe) > 0:
            sm.GetService('neocom').Blink('contracts', mls.UI_CONTRACTS_CONTRACTSREQUIREYOURATTENTION, blinkcount=10)
            if len(assignedToMe) == 1:
                txt1 = mls.UI_CONTRACTS_ACONTRACTISASSIGNEDTOYOU
                func = lambda x: self.ShowContract(assignedToMe[0])
            else:
                txt1 = mls.UI_CONTRACTS_CONTRACTSASSIGNEDTOYOU % {'num': len(assignedToMe)}
            func = self.ShowAssignedTo
        if len(kv.needsAttention) > 0:
            sm.GetService('neocom').Blink('journal', mls.UI_CONTRACTS_CONTRACTSREQUIREYOURATTENTION, blinkcount=10)
            if len(kv.needsAttention) == 1:
                txt2 = mls.UI_CONTRACTS_CONTRACTNEEDATTENTION
                contractID = kv.needsAttention[0].contractID
                func = lambda x: self.ShowContract(contractID)
            else:
                txt2 = mls.UI_CONTRACTS_CONTRACTSNEEDATTENTION % {'num': len(kv.needsAttention)}
            func = lambda x: self.OpenJournal(0, kv.needsAttention[0][1])
        if txt1 and txt2:
            func = lambda x: self.Show(None, 0)
        if txt1 or txt2:
            icon = sm.GetService('mailSvc').ShowMailNotification(mls.UI_CONTRACTS_CONTRACTS, txt1, txt2)
            icon.OnClick = func
            icon.sr.icon.LoadIcon('ui_64_64_10', ignoreSize=True)
            icon.sr.icon.width = 48
            icon.sr.icon.height = 48
            icon.sr.icon.left = 5
        if len(kv.inProgress):
            ip = {}
            for contract in kv.inProgress:
                ip[contract.contractID] = [contract.startStationID, contract.endStationID, contract.expires]

            self.contractsInProgress = ip



    def ProcessSessionChange(self, isremote, sess, change):
        if 'charid' in change:
            self.Init()



    def OnContractAssigned(self, contractID):
        contract = self.GetContract(contractID)
        c = contract.contract
        issuerID = [c.issuerID, c.issuerCorpID][c.forCorp]
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        if issuerID in ignoreList:
            return 
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_ASSIGNED, contractID)



    def OnContractCompleted(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_COMPLETED, contractID)



    def OnContractAccepted(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_ACCEPTED, contractID)



    def OnContractRejected(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_REJECTED, contractID)



    def OnContractFailed(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_FAILED, contractID)



    def OnContractOutbid(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_OUTBID, contractID)



    def OnContractBuyout(self, contractID):
        self.ContractNotify(mls.UI_CONTRACTS_MESSAGE_BUYOUT, contractID)



    def ContractNotify(self, msg, contractID):
        contract = self.GetContract(contractID, force=False)
        c = contract.contract
        title = GetContractTitle(c, contract.items)
        title = '<a href="contract:%s//%s">%s</a>' % (c.startSolarSystemID, contractID, title)
        msg = msg % {'title': title}
        msg = '[%s] %s' % (util.FmtDate(blue.os.GetTime(), 'ls'), msg)
        self.messages.append(msg)
        MAX_NUM_MESSAGES = 5
        if len(self.messages) > MAX_NUM_MESSAGES:
            self.messages.pop(0)
        self.Blink()
        self.ClearCache()



    def Blink(self):
        sm.GetService('neocom').Blink('contracts', mls.UI_CONTRACTS_CONTRACTSREQUIREYOURATTENTION, blinkcount=10)



    def ShowAssignedTo(self, *args):
        self.Show()
        self.OpenAvailableTab(3, 1)



    def Show(self, lookup = None, idx = None):
        sm.GetService('tutorial').OpenTutorialSequence_Check(uix.tutorialInformativeContracts)
        wnd = sm.GetService('window').GetWindow('contracts')
        if wnd is None:
            wnd = sm.GetService('window').GetWindow('contracts', 1, decoClass=form.ContractsWindow, lookup=lookup, idx=idx)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
        if wnd is not None and lookup:
            wnd.LookupOwner(lookup)



    def GetRouteSecurityWarning(self, startSolarSystemID, endSolarSystemID):
        mapSvc = sm.GetService('map')
        path = sm.GetService('pathfinder').GetPathBetween(startSolarSystemID, endSolarSystemID)
        txt = ''
        if not path:
            txt = '<color=0xffbb0000>%s</color>' % mls.UI_GENERIC_UNREACHABLE.upper()
        else:
            mySecurityClass = mapSvc.GetSecurityClass(session.solarsystemid2)
            pathClasses = set()
            for solarSystemID in path:
                pathClasses.add(mapSvc.GetSecurityClass(solarSystemID))

            classTxt = ''
            for p in pathClasses:
                if p != mySecurityClass:
                    classTxt += '%s, ' % GetSecurityClassText(p)

            if classTxt:
                classTxt = classTxt[:-3]
                txt = mls.UI_CONTRACTS_ROUTEWILLTAKEYOUTHROUGH % {'sec': classTxt}
        return txt



    def ShowContract(self, contractID):
        self.contractID = contractID
        wnd = sm.GetService('window').GetWindow('contractdetails')
        if wnd:
            wnd.SelfDestruct()
        wnd = sm.GetService('window').GetWindow('contractdetails', create=True, maximize=True, decoClass=form.ContractDetailsWindow, contractID=contractID)



    def GetContract(self, contractID, force = False):
        v = self.contracts.get(contractID, None)
        diff = 0
        if v:
            diff = blue.os.GetTime() - v.time
        if contractID not in self.contracts or force or diff > 5 * MIN and not force:
            self.LogInfo('Fetching contract %s from the server' % contractID)
            contract = self.contractSvc.GetContract(contractID)
            v = util.KeyVal()
            v.time = blue.os.GetTime()
            v.contract = contract
            self.contracts[contractID] = v
        else:
            self.LogInfo('Using client cache for contract %s' % contractID)
        return self.contracts[contractID].contract



    def AcceptContract(self, contractID, forCorp):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        if not contract:
            raise UserError('ConContractNotFound')
        if not self.CheckForPOS(c):
            return 
        n = sm.GetService('pathfinder').GetJumpCountFromCurrent(c.startSolarSystemID)
        n2 = 0
        if c.endSolarSystemID:
            n2 = sm.GetService('pathfinder').GetJumpCountFromCurrent(c.endSolarSystemID)
        n = max(n, n2)
        if n > 1000:
            if eve.Message('ConConfirmNotReachable', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        wallet = sm.GetService('corp').GetMyCorpAccountName()
        args = {'youoryourcorp': {False: mls.UI_GENERIC_YOU,
                           True: mls.UI_CONTRACTS_YOURCORP_NAME2 % {'corpname': cfg.eveowners.Get(eve.session.corpid).name,
                                  'wallet': wallet}}[forCorp]}
        args['contractname'] = GetContractTitle(c, contract.items)
        if c.type == const.conTypeAuction:
            raise RuntimeError('You cannot accept an auction')
        elif c.type == const.conTypeItemExchange:
            msg = 'ConConfirmAcceptItemExchange'
            reportGet = reportPay = ''
            for item in contract.items:
                if item.inCrate:
                    reportGet += '<t>%s.<br>' % cfg.FormatConvert(TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity)).capitalize()
                else:
                    reportPay += '<t>%s.<br>' % cfg.FormatConvert(TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity)).capitalize()

            if reportGet != '':
                reportGet = mls.UI_CONTRACTS_CONFIRMACCEPT_ITEMSGET % {'items': reportGet}
            if reportPay != '':
                reportPay = mls.UI_CONTRACTS_CONFIRMACCEPT_ITEMSPAY % {'items': reportPay}
            if reportGet == '' and c.reward == 0 and (reportPay != '' or c.price > 0):
                msg += mls.UI_CONTRACTS_GIFT
            if reportPay != '' and forCorp:
                reportPay += mls.UI_CONTRACTS_CONFIRMACCEPTCORPITEMS
            args['itemsget'] = reportGet
            args['itemspay'] = reportPay
            payorgetmoney = ''
            if c.price > 0:
                payorgetmoney = mls.UI_CONTRACTS_CONFIRMACCEPT_PAYMONEY % {'money': FmtISKWithDescription(c.price)}
            elif c.reward > 0:
                payorgetmoney = mls.UI_CONTRACTS_CONFIRMACCEPT_GETMONEY % {'money': FmtISKWithDescription(c.reward)}
            args['payorgetmoney'] = payorgetmoney
        elif c.type == const.conTypeCourier:
            if c.volume > const_conCourierWarningVolume:
                if eve.Message('ConNeedFreighter', {'vol': util.FmtAmt(c.volume, showFraction=3)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
            if c.volume <= const_conCourierWarningVolume:
                ship = sm.GetService('godma').GetItem(eve.session.shipid)
                if ship:
                    maxVolume = ship.GetCapacity().capacity
                    if maxVolume < c.volume:
                        if eve.Message('ConCourierDoesNotFit', {'max': util.FmtAmt(maxVolume, showFraction=3),
                         'vol': util.FmtAmt(c.volume, showFraction=3)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return False
            msg = 'ConConfirmAcceptCourier'
            args['numdays'] = c.numDays
            args['destination'] = cfg.evelocations.Get(c.endStationID).name
            args['volume'] = c.volume
            collateral = ''
            if c.collateral > 0:
                collateral = mls.UI_CONTRACTS_YOUWILLHAVETOPROVIDECOLLATERAL_AMOUNT % {'collateral': FmtISKWithDescription(c.collateral)}
            args['collateral'] = collateral
        else:
            raise RuntimeError('Invalid contract type')
        if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.LogInfo('Accepting contract %s' % contractID)
        contract = self.contractSvc.AcceptContract(contractID, forCorp)
        if contract.type == const.conTypeCourier:
            self.contractsInProgress[contract.contractID] = [contract.startStationID, contract.endStationID, contract.dateAccepted + DAY * contract.numDays]
        self.ClearCache()
        return True



    def DeleteContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        if not contract:
            raise UserError('ConContractNotFound')
        c = contract.contract
        if c.dateExpired >= blue.os.GetTime() and c.status != const.conStatusRejected:
            args = {}
            args['contractname'] = GetContractTitle(c, contract.items)
            msg = 'ConConfirmDeleteContract'
            if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
                return False
        self.LogInfo('Deleting contract', contractID)
        if self.contractSvc.DeleteContract(contractID):
            sm.ScatterEvent('OnDeleteContract', contractID)
        self.ClearCache()
        return True



    def CompleteContract(self, contractID):
        ret = False
        if eve.Message('ConConfirmComplete', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.LogInfo('Completing contract %s' % contractID)
            self.ClearCache()
            ret = self.contractSvc.CompleteContract(contractID, const.conStatusFinished)
            if contractID in self.contractsInProgress:
                del self.contractsInProgress[contractID]
            eve.Message('ConCourierContractDelivered')
        return ret



    def FailContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        args['contractname'] = GetContractTitle(c, contract.items)
        if c.acceptorID == eve.session.charid or c.acceptorID == eve.session.corpid:
            msg = 'ConConfirmFailContractAcceptor'
            args['collateral'] = mls.UI_CONTRACTS_CONFIRMFAIL_LOSECOLLATERAL % {'collateral': FmtISKWithDescription(c.collateral)}
        elif blue.os.GetTime() > c.dateAccepted + DAY * c.numDays and c.status == const.conStatusInProgress:
            msg = 'ConConfirmFailContractIssuerOverdue'
            args['timeoverdue'] = util.FmtDate(blue.os.GetTime() - (c.dateAccepted + c.numDays), 'ls')
        else:
            msg = 'ConConfirmFailContractIssuerFinishedAcceptor'
        args['acceptor'] = cfg.eveowners.Get(c.acceptorID).name
        if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.ClearCache()
        self.LogInfo('Failing contract %s' % contractID)
        ret = self.contractSvc.CompleteContract(contractID, const.conStatusFailed)
        if contractID in self.contractsInProgress:
            del self.contractsInProgress[contractID]
        return ret



    def RejectContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        args['contractname'] = GetContractTitle(c, contract.items)
        args['issuer'] = cfg.eveowners.Get({False: c.issuerID,
         True: c.issuerCorpID}[c.forCorp]).name
        if c.assigneeID == session.charid:
            msg = 'ConConfirmRejectContract'
        elif c.assigneeID == session.corpid:
            msg = 'ConConfirmRejectContractCorp'
        else:
            raise UserError('ConNotYourContract')
        if eve.Message(msg, args, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        self.LogInfo('Rejecting contract %s' % contractID)
        self.ClearCache()
        return self.contractSvc.CompleteContract(contractID, const.conStatusRejected)



    def CreateContract(self, type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList, flag, requestItemTypeList, forCorp, confirm = None):
        self.LogNotice('CreateContract', type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList, flag, requestItemTypeList, forCorp)
        ret = self.contractSvc.CreateContract(type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList=itemList, flag=flag, requestItemTypeList=requestItemTypeList, forCorp=forCorp, confirm=confirm)
        self.ClearCache()
        return ret



    def PlaceBid(self, contractID, force = None):
        uthread.ReentrantLock(self)
        try:
            isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
            contract = self.GetContract(contractID, force=force)
            self.contract = contract
            c = contract.contract
            if not self.CheckForPOS(c):
                return 
            else:
                currentBid = 0
                numBids = 0
                maxBid = MAX_AMOUNT
                if len(contract.bids) > 0:
                    currentBid = contract.bids[0].amount
                    numBids = len(contract.bids)
                b = currentBid + max(int(0.1 * c.price), 1000)
                if c.collateral > 0:
                    b = min(b, c.collateral)
                    maxBid = c.collateral
                minBid = int(max(c.price, b))
                if c.collateral > 0:
                    collateral = FmtISKWithDescription(c.collateral)
                else:
                    collateral = mls.UI_CONTRACTS_NOBUYOUTPRICE
                format = [{'type': 'btline'},
                 {'type': 'text',
                  'text': mls.UI_CONTRACTS_BIDDINGON_NAME % {'name': GetContractTitle(c, contract.items)},
                  'frame': 1,
                  'labelwidth': 100},
                 {'type': 'labeltext',
                  'label': mls.UI_CONTRACTS_STARTINGBID,
                  'text': FmtISKWithDescription(c.price),
                  'frame': 1,
                  'labelwidth': 100},
                 {'type': 'labeltext',
                  'label': mls.UI_CONTRACTS_BUYOUTPRICE,
                  'text': collateral,
                  'frame': 1,
                  'labelwidth': 100},
                 {'type': 'labeltext',
                  'label': mls.UI_CONTRACTS_CURRENTBID,
                  'text': FmtISKWithDescription(currentBid),
                  'frame': 1,
                  'labelwidth': 100},
                 {'type': 'edit',
                  'setvalue': '0.1',
                  'floatonly': [0, maxBid],
                  'setvalue': minBid,
                  'key': 'bid',
                  'labelwidth': 100,
                  'label': mls.UI_CONTRACTS_YOURBID,
                  'required': 1,
                  'frame': 1,
                  'setfocus': 1}]
                if isContractMgr and not (c.forCorp and c.issuerCorpID == eve.session.corpid):
                    format.append({'type': 'checkbox',
                     'required': 1,
                     'height': 16,
                     'setvalue': 0,
                     'key': 'forCorp',
                     'label': '',
                     'text': mls.UI_CONTRACTS_PLACEBIDONBEHALFOFCORP,
                     'frame': 1})
                if c.collateral > 0:
                    format.append({'type': 'checkbox',
                     'required': 1,
                     'height': 16,
                     'setvalue': 0,
                     'key': 'buyout',
                     'label': '',
                     'text': mls.UI_CONTRACTS_BUYOUT,
                     'frame': 1,
                     'onchange': self.PlaceBidBuyoutCallback})
                format.append({'type': 'push',
                 'frame': 1})
                format.append({'type': 'bbline'})
                retval = uix.HybridWnd(format, mls.UI_CONTRACTS_BIDDING_ON_CONTRACT, 1, buttons=uiconst.OKCANCEL, minW=340, minH=100, icon='07_12')
                if retval:
                    forCorp = not not retval.get('forCorp', False)
                    buyout = not not retval.get('buyout', False)
                    bid = int(retval['bid'])
                    if buyout:
                        if c.collateral < c.price:
                            raise RuntimeError('Buyout is lower than starting bid!')
                        bid = c.collateral
                    try:
                        retval = self.DoPlaceBid(contractID, bid, forCorp)
                    except UserError as e:
                        if e.args[0] == 'ConBidTooLow':
                            eve.Message(e.args[0], e.args[1])
                            self.PlaceBid(contractID, force=True)
                        else:
                            raise 
                return not not retval

        finally:
            uthread.UnLock(self)
            self.ClearCache()




    def PlaceBidBuyoutCallback(self, chkbox, *args):
        c = self.contract.contract
        buyout = c.collateral
        currentBid = 0
        if len(self.contract.bids) > 0:
            currentBid = self.contract.bids[0].amount
        minBid = int(max(c.price, min(currentBid + 0.1 * c.price + 0.1, c.collateral)))
        wnd = chkbox.parent.parent
        edit = uiutil.FindChild(wnd, 'edit_bid')
        if chkbox.GetValue():
            edit.state = uiconst.UI_DISABLED
            edit.SetText(buyout)
        else:
            edit.state = uiconst.UI_NORMAL
            edit.SetText(minBid)



    def DoPlaceBid(self, contractID, bid, forCorp):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        wallet = sm.GetService('corp').GetMyCorpAccountName()
        args = {'youoryourcorp': {False: mls.UI_GENERIC_YOU,
                           True: mls.UI_CONTRACTS_YOURCORP_NAME2 % {'corpname': cfg.eveowners.Get(eve.session.corpid).name,
                                  'wallet': wallet}}[forCorp]}
        args['contractname'] = GetContractTitle(c, contract.items)
        args['amount'] = FmtISKWithDescription(bid)
        reportGet = ''
        for item in contract.items:
            if item.inCrate:
                reportGet += '<t>%s.<br>' % cfg.FormatConvert(TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity)).capitalize()

        if reportGet != '':
            reportGet = mls.UI_CONTRACTS_CONFIRMACCEPT_ITEMSGET % {'items': reportGet}
        args['itemsget'] = reportGet
        msg = 'ConConfirmPlaceBid'
        if eve.Message(msg, args, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        self.LogInfo('Placing bid of %s on contract %s' % (FmtISKWithDescription(bid), contractID))
        return self.contractSvc.PlaceBid(contractID, bid, forCorp)



    def FinishAuction(self, contractID, isIssuer):
        self.LogInfo('Finishing Auction %s' % contractID)
        self.ClearCache()
        return self.contractSvc.FinishAuction(contractID, isIssuer)



    def GetMarketTypes(self):
        if not self.markettypes:
            self.markettypes = GetMarketTypes()
        return self.markettypes



    def NumOutstandingContracts(self, forCorp = False):
        self.LogInfo('Getting number of outstanding contracts%s' % ['', ' (for corp)'][forCorp])
        return self.contractSvc.NumOutstandingContracts()



    def SplitStack(self, stationID, itemID, qty, forCorp, flag):
        self.LogInfo('Splitting stack of item %s, qty=%s%s' % (itemID, qty, ['', ' (for corp)'][forCorp]))
        ret = self.contractSvc.SplitStack(stationID, itemID, qty, forCorp, flag)
        if ret:
            wnd = sm.GetService('window').GetWindow('createcontract')
            if wnd is not None and not wnd.destroyed:
                wnd.OnItemSplit(itemID, qty)
                wnd.Refresh()
        return ret



    def GetItemsInContainer(self, stationID, containerID, forCorp, flag):
        return self.contractSvc.GetItemsInContainer(stationID, containerID, forCorp, flag)



    def GetItemsInStation(self, stationID, forCorp):
        return self.contractSvc.GetItemsInStation(stationID, forCorp)



    def DeleteNotification(self, contractID, forCorp):
        self.ClearCache()
        return self.contractSvc.DeleteNotification(contractID, forCorp)



    def CollectMyPageInfo(self, force = False):
        mpi = util.KeyVal()
        if self.myPageInfo is None or self.myPageInfo.timeout < blue.os.GetTime() or force:
            mpi = self.contractSvc.CollectMyPageInfo()
            skill = sm.GetService('skills').HasSkill(const.typeContracting)
            if skill is None:
                lvl = 0
            else:
                lvl = skill.skillLevel
            skill = sm.GetService('skills').HasSkill(const.typeCorporationContracting)
            if skill is None:
                lvlCorp = 0
            else:
                lvlCorp = skill.skillLevel
            maxNumContracts = NUM_CONTRACTS_BY_SKILL[lvl]
            maxNumContractsCorp = NUM_CONTRACTS_BY_SKILL_CORP[lvlCorp]
            mpi.numContractsLeft = maxNumContracts - mpi.numOutstandingContractsNonCorp
            mpi.numContractsLeftForCorp = maxNumContractsCorp - mpi.numOutstandingContractsForCorp
            mpi.numContractsTotal = maxNumContracts
            mpi.numContractsLeftInCorp = MAX_NUM_CONTRACTS - mpi.numOutstandingContracts
            mpi.timeout = blue.os.GetTime() + CACHE_TIME * MINUTE
            self.myPageInfo = mpi
        else:
            self.LogInfo('CollectMyPageInfo returning cached result')
            mpi = self.myPageInfo
        return mpi



    def GetMyExpiredContractList(self):
        l = None
        if self.myExpiredContractList is None or self.myExpiredContractList.timeout < blue.os.GetTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.mySelf = sm.ProxySvc('contractProxy').GetMyExpiredContractList(False)
            l.myCorp = sm.ProxySvc('contractProxy').GetMyExpiredContractList(True)
            l.timeout = blue.os.GetTime() + CACHE_TIME * MINUTE
            self.myExpiredContractList = l
        else:
            self.LogInfo('GetMyExpiredContractList returning cached result')
            l = self.myExpiredContractList
        return l



    def GetMyBids(self, forCorp):
        l = None
        val = getattr(self, 'myBids_%s' % forCorp, None)
        if val is None or val.timeout < blue.os.GetTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.list = sm.ProxySvc('contractProxy').GetMyBids(forCorp)
            l.timeout = blue.os.GetTime() + CACHE_TIME * MINUTE
            setattr(self, 'myBids_%s' % forCorp, l)
        else:
            self.LogInfo('GetMyBids(', forCorp, ') returning cached result')
            l = val
        return l



    def GetMyCurrentContractList(self, isAccepted, forCorp):
        l = None
        val = getattr(self, 'myCurrentList_%s_%s' % (isAccepted, forCorp), None)
        if val is None or val.timeout < blue.os.GetTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.list = sm.ProxySvc('contractProxy').GetMyCurrentContractList(isAccepted, forCorp)
            l.timeout = blue.os.GetTime() + CACHE_TIME * MINUTE
            setattr(self, 'myCurrentList_%s_%s' % (isAccepted, forCorp), l)
        else:
            self.LogInfo('GetMyCurrentContractList(', isAccepted, forCorp, ') returning cached result')
            l = val
        return l



    def ClearCache(self):
        setattr(self, 'myCurrentList_True_True', None)
        setattr(self, 'myCurrentList_True_False', None)
        setattr(self, 'myCurrentList_False_True', None)
        setattr(self, 'myCurrentList_False_False', None)
        setattr(self, 'myBids_False', None)
        setattr(self, 'myBids_True', None)
        self.myExpiredContractList = None
        self.myPageInfo = None
        sm.ScatterEvent('OnContractCacheCleared')



    def OpenJournal(self, status = 0, forCorp = 0):
        settings.user.tabgroups.Set('journalmaintabs', 2)
        sm.GetService('journal').Show()
        wnd = util.KeyVal(forCorp=forCorp)
        sm.GetService('journal').ShowContracts(wnd, status)



    def OpenCreateContract(self, items = None, contract = None):
        wnd = sm.GetService('window').GetWindow('createcontract')
        if wnd:
            wnd.SelfDestruct()
        sm.GetService('window').GetWindow('createcontract', 1, decoClass=form.CreateContract, recipientID=None, contractItems=items, copyContract=contract)



    def OpenCreateContractFromIGB(self, contractType = None, stationID = None, itemIDs = None):
        wnd = sm.GetService('window').GetWindow('createcontract')
        if wnd:
            wnd.SelfDestruct()
        sm.GetService('window').GetWindow('createcontract', 1, decoClass=form.CreateContract, recipientID=None, contractItems=None, copyContract=None, contractType=contractType, stationID=stationID, itemIDs=itemIDs)



    def OpenAvailableTab(self, view, reset = False, typeID = None, contractType = CONTYPE_AUCTIONANDITEMECHANGE):
        wnd = sm.GetService('window').GetWindow('contracts')
        if wnd is not None:
            assigneeID = {3: const.conAvailMyself,
             4: const.conAvailMyCorp}.get(view, const.conAvailPublic)
            self.OpenSearchTab(typeID, None, None, None, None, None, assigneeID, contractType)



    def OpenSearchTab(self, *args):
        wnd = sm.GetService('window').GetWindow('contracts')
        if wnd is None:
            wnd = sm.GetService('window').GetWindow('contracts', 1, decoClass=form.ContractsWindow)
        if wnd is not None:
            wnd.Maximize()
            blue.pyos.synchro.Sleep(10)
            wnd.sr.maintabs.SelectByIdx(2)
            wnd.sr.contractSearchContent.FindRelated(*args)



    def AddIgnore(self, issuerID):
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        if len(ignoreList) >= MAX_IGNORED:
            raise UserError('ConIgnoreListFull', {'n': MAX_IGNORED})
        if issuerID not in ignoreList:
            ignoreList.append(issuerID)
        settings.user.ui.Set('contracts_ignorelist', ignoreList)
        self.ClearCache()
        sm.ScatterEvent('OnAddIgnore', issuerID)



    def OpenIgnoreList(self):
        wnd = sm.GetService('window').GetWindow('contractignorelist')
        if wnd is not None:
            wnd.SelfDestruct()
        sm.GetService('window').GetWindow('contractignorelist', 1, decoClass=form.IgnoreListWindow)



    def GetMessages(self):
        return self.messages



    def DeliverCourierContractFromItemID(self, itemID):
        info = self.contractSvc.GetCourierContractFromItemID(itemID)
        if info is None:
            raise UserError('ConContractNotFoundForCrate')
        contractID = info.contractID
        self.CompleteContract(contractID)



    def FindCourierContractFromItemID(self, itemID):
        info = self.contractSvc.GetCourierContractFromItemID(itemID)
        if info is None:
            raise UserError('ConContractNotFoundForCrate')
        self.ShowContract(info.contractID)



    def IsStationInaccessible(self, stationID):
        if stationID is None:
            return False
        station = sm.GetService('ui').GetStation(stationID)
        isPlayerOwnable = sm.GetService('godma').GetType(station.stationTypeID).isPlayerOwnable
        if isPlayerOwnable and station.ownerID != session.corpid and stationID != session.stationid:
            return True
        return False



    def CheckForPOS(self, c):
        msg = 'ConStationIsPOS'
        s1 = s2 = ''
        if self.IsStationInaccessible(c.startStationID):
            station = sm.GetService('ui').GetStation(c.startStationID)
            s1 = mls.UI_CONTRACTS_STARTSTATIONPOSINFO % {'name': cfg.evelocations.Get(c.startStationID).name,
             'owner': cfg.eveowners.Get(station.ownerID).name}
        if c.type == const.conTypeCourier and self.IsStationInaccessible(c.endStationID):
            station = sm.GetService('ui').GetStation(c.endStationID)
            s2 = mls.UI_CONTRACTS_ENDSTATIONPOSINFO % {'name': cfg.evelocations.Get(c.endStationID).name,
             'owner': cfg.eveowners.Get(station.ownerID).name}
        if s1 != '' or s2 != '':
            if eve.Message(msg, {'s1': s1,
             's2': s2}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return False
        return True



    def GetSystemSecurityDot(self, solarSystemID):
        (sec, col,) = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(solarSystemID), 1)
        col.a = 1.0
        colString = hex(col.AsInt() & 4294967295L)
        return '<color=%s>\x95</color>' % colString




class ContractsWindow(uicls.Window):
    __guid__ = 'form.ContractsWindow'
    __notifyevents__ = ['OnDeleteContract', 'OnAddIgnore']
    default_width = 630
    default_height = 500

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        lookup = attributes.lookup
        idx = attributes.idx
        self.scope = 'all'
        self.SetCaption(mls.UI_CONTRACTS_CONTRACTS)
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)
        self.SetMinSize([700, 560])
        self.SetTopparentHeight(0)
        self.pages = {0: None}
        self.currPage = 0
        self.previousPageContractID = None
        self.currentPageContractID = None
        self.nextPageContractID = None
        self.parsingIssuers = False
        self.parsingType = False
        self.issuersByName = {}
        self.fetching = 0
        btns = []
        btns.append(['createContractButton',
         mls.UI_CONTRACTS_CREATECONTRACT,
         self.OpenCreateContract,
         None,
         None])
        uicls.ButtonGroup(btns=btns, parent=self.sr.main, line=1, unisize=1, forcedButtonNames=True)
        self.LoadTabs(lookup, idx)



    def OpenCreateContract(self, *args):
        sm.GetService('contracts').OpenCreateContract()



    def MouseEnterHighlightOn(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 0.0)



    def MouseExitHighlightOff(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 1.0)



    def LookupOwner(self, ownerName):
        try:
            self.Maximize()
            setattr(self.sr.myContractsParent, 'lookup', ownerName)
            self.sr.maintabs.SelectByIdx(1)
            self.sr.myContractsParent.sr.fltToFrom.SetValue(None)
            self.sr.myContractsParent.sr.fltOwner.SetValue(ownerName)
            self.sr.myContractsParent.sr.fltStatus.SelectItemByValue(const.conStatusFinished)
            self.sr.myContractsParent.sr.fltType.SelectItemByValue(None)
            self.sr.myContractsParent.FetchContracts()
        except:
            sys.exc_clear()



    def LoadTabs(self, lookup = None, idx = None):
        self.sr.startPageParent = xtriui.StartPagePanel(name='startPageParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.myContractsParent = xtriui.MyContractsPanel(name='myContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.contractSearchParent = uicls.Container(name='contractSearchParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.contractSearchContent = form.ContractSearchWindow(parent=self.sr.contractSearchParent, name='contractsearch', pos=(0, 0, 0, 0))
        self.sr.privateContractsParent = uicls.Container(name='privateContractsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        tabs = uicls.TabGroup(name='contractsTabs', parent=self.sr.main, idx=0)
        tabList = [[mls.UI_CONTRACTS_STARTPAGE,
          self.sr.startPageParent,
          self,
          'startPage'], [mls.UI_CONTRACTS_MYCONTRACTS,
          self.sr.myContractsParent,
          self,
          'myContracts'], [mls.UI_CONTRACTS_AVAILABLECONTRACTS,
          self.sr.contractSearchParent,
          self,
          'contractSearch']]
        tabs.Startup(tabList, 'contractsTabs', autoselecttab=0)
        if idx:
            tabs.SelectByIdx(idx)
        elif lookup:
            setattr(self.sr.myContractsParent, 'lookup', lookup)
            tabs.SelectByIdx(1)
        else:
            h = getattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', False)
            if not h:
                tabs.SelectByIdx(0)
                setattr(sm.StartService('contracts'), 'hasContractWindowBeenOpened', True)
            else:
                tabs.AutoSelect()
        self.sr.maintabs = tabs



    def Load(self, key):
        doInit = self.TabNotInitiatedCheck(key)
        if key == 'myContracts':
            if doInit:
                self.sr.myContractsParent.Init()
        elif key == 'startPage':
            self.sr.startPageParent.Init()
        elif key == 'contractSearch':
            self.sr.contractSearchContent.Load(key)
            self.sr.contractSearchContent.SetInitialFocus()



    def TabNotInitiatedCheck(self, key):
        doInit = not getattr(self, 'init_%s' % key, False)
        setattr(self, 'init_%s' % key, True)
        return doInit



    def Confirm(self, *etc):
        if self.sr.maintabs.GetSelectedArgs() == 'availableContracts':
            self.OnReturn_AvailableContracts()



    def GetError(self, checkNumber = 1):
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})



    def OnDeleteContract(self, contractID, *args):

        def DeleteContractInList(list, contractID):
            nodes = list.GetNodes()
            for n in nodes:
                if n.contractID == contractID:
                    list.RemoveEntries([n])
                    return 



        list = uiutil.FindChild(self.sr.main, 'mycontractlist')
        if list:
            DeleteContractInList(list, contractID)



    def OnAddIgnore(self, ignoreID, *args):
        if self.sr.Get('contractlist'):
            list = self.sr.contractlist
        else:
            cont = self.sr.myContractsParent
            list = None
            for child in cont.children:
                if hasattr(child, 'name') and child.name == 'mycontractlist':
                    list = child
                    break





class StartPagePanel(uicls.Container):
    __notifyevents__ = ['OnContractCacheCleared']
    __guid__ = 'xtriui.StartPagePanel'

    def init(self):
        self.inited = 0
        self.submitFunc = None



    def Init(self):

        def AddItem(icon, header, text, url, isSmall = False):
            if isSmall:
                return '\n                <tr><td width=1%% align=center valign=top><img src="icon:%s" size=16></td><td><a href="localsvc:service=contracts&%s">%s</a><br>%s</td></tr>\n                ' % (icon,
                 url,
                 header,
                 text)
            else:
                return '\n                <tr><td width=1%%><img style:vertical-align:top src="icon:%s" size=32></td><td><h6><a href="localsvc:service=contracts&%s">%s</a></h6>%s<br></td></tr>\n                ' % (icon,
                 url,
                 header,
                 text)


        if not self.inited:
            descParent = uicls.Container(name='desc', parent=self, align=uiconst.TOALL, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.mypagedesc = uicls.Edit(parent=descParent, readonly=1, hideBackground=1)
            uicls.Frame(parent=self.mypagedesc, color=(1.0, 1.0, 1.0, 0.2))
            self.inited = 1
            sm.RegisterNotify(self)
        mpi = sm.GetService('contracts').CollectMyPageInfo()
        n = mpi.numContractsLeft
        ntot = mpi.numContractsTotal
        np = mpi.numContractsLeftInCorp
        nforcorp = mpi.numContractsLeftForCorp
        html = '<html><body>\n        <h3>%s</h3>\n        <table width=100%%>\n            <tr><td colspan=2><hr></td></tr>' % mls.UI_CONTRACTS_MYSTARTPAGE
        desc = mls.UI_CONTRACTS_MYPAGE_YOUCANCREATE_DESC1NEW % {'n1': ntot}
        if not util.IsNPC(eve.session.corpid):
            desc += '<br>' + mls.UI_CONTRACTS_MYPAGE_YOUCANCREATE_DESC2 % {'n': np}
        if eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager:
            desc += '<br>' + mls.UI_CONTRACTS_MYPAGE_YOUCANCREATE_DESC3 % {'n': nforcorp}
        html += AddItem('64_10', mls.UI_CONTRACTS_MYPAGE_YOUCANCREATE % {'n': n}, desc, 'method=OpenCreateContract')
        html += '<tr><td colspan=2><hr></td></tr>'
        html2 = ''
        ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
        numAssignedToMeAuctionItemExchange = 0
        numAssignedToMeCourier = 0
        numAssignedToMyCorpAuctionItemExchange = 0
        numAssignedToMyCorpCourier = 0
        if mpi.outstandingContracts is None:
            eve.Message('ConNotReady')
            mpi.outstandingContracts = []
        else:
            for contract in mpi.outstandingContracts:
                if contract[0] in ignoreList or contract[1] in ignoreList:
                    continue
                if contract[2] == session.charid:
                    if contract[3] == const.conTypeCourier:
                        numAssignedToMeCourier += 1
                    else:
                        numAssignedToMeAuctionItemExchange += 1
                elif contract[3] == const.conTypeCourier:
                    numAssignedToMyCorpCourier += 1
                else:
                    numAssignedToMyCorpAuctionItemExchange += 1

        if mpi.numRequiresAttention > 0:
            html2 += AddItem('ui_9_64_11', mls.UI_CONTRACTS_MYPAGE_REQATT % {'n': mpi.numRequiresAttention}, mls.UI_CONTRACTS_MYPAGE_REQATT_DESC, 'method=OpenJournal&status=0&forCorp=0')
        if mpi.numRequiresAttentionCorp > 0:
            html2 += AddItem('ui_9_64_11', mls.UI_CONTRACTS_MYPAGE_REQATTCORP % {'n': mpi.numRequiresAttentionCorp}, mls.UI_CONTRACTS_MYPAGE_REQATTCORP_DESC, 'method=OpenJournal&forCorp=1')
        if numAssignedToMeAuctionItemExchange > 0 or numAssignedToMeCourier > 0:
            html2 += '<tr>\n                        <td width=1%% align=center valign=top><img src="icon:%s" size=32></td>\n                        <td><h6>%s</h6>\n                        ' % ('ui_9_64_9', mls.UI_CONTRACTS_MYPAGE_ASSIGNED % {'n': numAssignedToMeAuctionItemExchange + numAssignedToMeCourier})
            if numAssignedToMeAuctionItemExchange > 0:
                html2 += ' - <a href="localsvc:service=contracts&%s">%s</a><br>' % ('method=OpenAvailableTab&view=3&reset=1&contractType=%s' % CONTYPE_AUCTIONANDITEMECHANGE, mls.UI_CONTRACTS_MYPAGE_ASSIGNED_AUCTIONITEMEXCHANGE % {'n': numAssignedToMeAuctionItemExchange})
            if numAssignedToMeCourier > 0:
                html2 += ' - <a href="localsvc:service=contracts&%s">%s</a><br>' % ('method=OpenAvailableTab&view=3&reset=1&contractType=%s' % const.conTypeCourier, mls.UI_CONTRACTS_MYPAGE_ASSIGNED_COURIER % {'n': numAssignedToMeCourier})
        if numAssignedToMyCorpAuctionItemExchange > 0 or numAssignedToMyCorpCourier > 0:
            html2 += '<tr>\n                        <td width=1%% align=center valign=top><img src="icon:%s" size=32></td>\n                        <td><h6>%s</h6>\n                        ' % ('ui_9_64_9', mls.UI_CONTRACTS_MYPAGE_ASSIGNEDCORP % {'n': numAssignedToMyCorpAuctionItemExchange + numAssignedToMyCorpCourier})
            if numAssignedToMyCorpAuctionItemExchange > 0:
                html2 += ' - <a href="localsvc:service=contracts&%s">%s</a><br>' % ('method=OpenAvailableTab&view=4&reset=1&contractType=%s' % CONTYPE_AUCTIONANDITEMECHANGE, mls.UI_CONTRACTS_MYPAGE_ASSIGNEDCORP_AUCTIONITEMEXCHANGE % {'n': numAssignedToMyCorpAuctionItemExchange})
            if numAssignedToMyCorpCourier > 0:
                html2 += ' - <a href="localsvc:service=contracts&%s">%s</a><br>' % ('method=OpenAvailableTab&view=4&reset=1&contractType=%s' % const.conTypeCourier, mls.UI_CONTRACTS_MYPAGE_ASSIGNEDCORP_COURIER % {'n': numAssignedToMyCorpCourier})
        if mpi.numBiddingOn > 0:
            html2 += AddItem('64_16', mls.UI_CONTRACTS_MYPAGE_BIDDINGON % {'n': mpi.numBiddingOn}, mls.UI_CONTRACTS_MYPAGE_BIDDINGON_DESC, 'method=OpenJournal&status=3&forCorp=0')
        if mpi.numInProgress > 0:
            html2 += AddItem('ui_9_64_9', mls.UI_CONTRACTS_MYPAGE_INPROGRESS % {'n': mpi.numInProgress}, mls.UI_CONTRACTS_MYPAGE_INPROGRESS_DESC, 'method=OpenJournal&status=2&forCorp=0')
        if mpi.numBiddingOnCorp > 0:
            html2 += AddItem('64_16', mls.UI_CONTRACTS_MYPAGE_BIDDINGONCORP % {'n': mpi.numBiddingOnCorp}, mls.UI_CONTRACTS_MYPAGE_BIDDINGONCORP_DESC, 'method=OpenJournal&status=3&forCorp=1')
        if mpi.numInProgressCorp > 0:
            html2 += AddItem('ui_9_64_9', mls.UI_CONTRACTS_MYPAGE_INPROGRESSCORP % {'n': mpi.numInProgressCorp}, mls.UI_CONTRACTS_MYPAGE_INPROGRESSCORP_DESC, 'method=OpenJournal&status=2&forCorp=1')
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        if html2 != '':
            html2 += '<tr><td colspan=2><hr></td></tr>'
        html += html2
        l = len(ignoreList)
        if l > 0:
            html += AddItem('ui_38_16_208', mls.UI_CONTRACTS_MYPAGE_IGNORING % {'n': l}, mls.UI_CONTRACTS_MYPAGE_IGNORING_DESC % {'n': MAX_IGNORED}, 'method=OpenIgnoreList', isSmall=True)
            html += '<tr><td colspan=2><hr></td></tr>'
        html2 = ''
        mess = sm.GetService('contracts').GetMessages()
        if len(mess) > 0:
            for i in mess:
                html2 = '<tr><td width=1%% align=center valign=middle><img src="icon:%s" size=16></td><td>%s</td></tr>' % ('ui_38_16_208', i) + html2

        html += html2
        html += '</table></body></html>'
        uthread.new(self.LoadStartPage, html)



    def LoadStartPage(self, html):
        self.mypagedesc.SetValue(html)



    def OnContractCacheCleared(self, *args):
        if self.IsVisible():
            self.Init()



    def IsVisible(self):
        tabs = uiutil.FindChild(self.parent.parent, 'contractsTabs')
        selectedTab = tabs.GetVisible()
        return selectedTab.name == 'startPageParent'




class MyContractsPanel(uicls.Container):
    __guid__ = 'xtriui.MyContractsPanel'

    def init(self):
        self.inited = 0
        self.submitFunc = None



    def _OnClose(self):
        uicls.Container._OnClose(self)
        if self.inited:
            settings.user.ui.Set('mycontracts_filter_tofrom', self.sr.fltToFrom.GetValue())
            settings.char.ui.Set('mycontracts_filter_owner', self.sr.fltOwner.GetValue())
            settings.user.ui.Set('mycontracts_filter_status', self.sr.fltStatus.GetValue())
            settings.user.ui.Set('mycontracts_filter_type', self.sr.fltType.GetValue())



    def Init(self):
        if not self.inited:
            self.WriteFilters()
            self.sr.contractlistParent = contractlistParent = uicls.Container(name='contractlistParent', align=uiconst.TOALL, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), parent=self)
            self.sr.contractlist = contractlist = uicls.Scroll(parent=contractlistParent, name='mycontractlist')
            contractlist.sr.id = 'mycontractlist'
            contractlist.ShowHint(mls.UI_CONTRACTS_CONTRACTLISTHINT_CLICKGETCONTRACTS)
            contractlist.multiSelect = 0
            contractlistParent.top = 5
            self.currPage = 0
            self.pages = {0: None}
            self.fetchingContracts = 0
        self.inited = 1



    def WriteFilters(self):
        self.sr.filters = filters = uicls.Container(name='filters', parent=self, height=34, align=uiconst.TOTOP)
        top = 16
        left = 5
        options = [(mls.UI_CONTRACTS_ISSUEDTOBY, None), (mls.UI_CONTRACTS_ISSUEDBY, False), (mls.UI_CONTRACTS_ISSUEDTO, True)]
        c = self.sr.fltToFrom = uicls.Combo(label=mls.UI_GENERIC_ACTION, parent=filters, options=options, name='tofrom', select=settings.user.ui.Get('mycontracts_filter_tofrom', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0))
        left += c.width + 5
        corpName = cfg.eveowners.Get(eve.session.corpid).name
        charName = cfg.eveowners.Get(eve.session.charid).name
        val = getattr(self, 'lookup', None)
        if not val:
            val = settings.char.ui.Get('mycontracts_filter_owner', charName)
        self.sr.fltOwner = c = uicls.SinglelineEdit(name='edit', parent=filters, width=120, label=mls.UI_GENERIC_OWNER, setvalue=val, left=left, top=top)
        left += c.width + 5
        ops = [(charName, charName), (corpName, corpName)]
        c.LoadCombo('usernamecombo', ops, self.OnComboChange)
        self.status = [(mls.UI_CONTRACTS_OUTSTANDING, const.conStatusOutstanding), (mls.UI_CONTRACTS_INPROGRESS, const.conStatusInProgress), (mls.UI_CONTRACTS_FINISHED, const.conStatusFinished)]
        c = self.sr.fltStatus = uicls.Combo(label=mls.UI_GENERIC_STATUS, parent=filters, options=self.status, name='status', select=settings.user.ui.Get('mycontracts_filter_status', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0))
        left += c.width + 5
        mrk = '----------'
        fltTypeOptions = [(mls.UI_GENERIC_ALL, None),
         (mrk, -1),
         (mls.UI_CONTRACTS_AUCTION, const.conTypeAuction),
         (mls.UI_CONTRACTS_ITEMEXCHANGE, const.conTypeItemExchange),
         (mls.UI_CONTRACTS_COURIER, const.conTypeCourier)]
        self.sr.fltType = c = uicls.Combo(label=mls.UI_CONTRACTS_TYPE, parent=filters, options=fltTypeOptions, name='types', select=settings.user.ui.Get('mycontracts_filter_type', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0))
        left += c.width + 5
        self.sr.submitBtn = submit = uicls.Button(parent=filters, label=mls.UI_CONTRACTS_GETCONTRACTS, func=self.FetchContracts, pos=(const.defaultPadding,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        sidepar = uicls.Container(name='sidepar', parent=filters, align=uiconst.BOTTOMRIGHT, left=const.defaultPadding, width=54, height=30)
        btn = uix.GetBigButton(24, sidepar, 4, 6)
        btn.state = uiconst.UI_HIDDEN
        btn.OnClick = (self.BrowseMyContracts, -1)
        btn.hint = mls.UI_GENERIC_PREVIOUS
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.sr.transMyBackBtn = btn
        btn = uix.GetBigButton(24, sidepar, 28, 6)
        btn.state = uiconst.UI_HIDDEN
        btn.OnClick = (self.BrowseMyContracts, 1)
        btn.hint = mls.UI_GENERIC_VIEWMORE
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.transMyFwdBtn = btn
        sidepar.left = submit.width + const.defaultPadding



    def BrowseMyContracts(self, direction, *args):
        self.currPage = max(0, self.currPage + direction)
        self.DoFetchContracts()



    def FetchContracts(self, *args):
        if self.fetchingContracts:
            return 
        self.sr.submitBtn.state = uiconst.UI_DISABLED
        self.sr.submitBtn.SetLabel('<color=gray>' + self.sr.submitBtn.text + '</color>')
        self.fetchingContracts = 1
        uthread.new(self.EnableButtonTimer)
        self.currPage = 0
        self.pages = {0: None}
        self.DoFetchContracts()



    def EnableButtonTimer(self):
        blue.pyos.synchro.Sleep(5000)
        try:
            self.fetchingContracts = 0
            self.sr.submitBtn.state = uiconst.UI_NORMAL
            self.sr.submitBtn.SetLabel(mls.UI_CONTRACTS_GETCONTRACTS)
        except:
            pass



    def DoFetchContracts(self):
        self.sr.contractlist.Load(contentList=[])
        self.sr.contractlist.ShowHint(mls.UI_RMR_FETCHINGDATA)
        try:
            if self.currPage == 0:
                self.sr.transMyBackBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.transMyBackBtn.state = uiconst.UI_NORMAL
            isAccepted = self.sr.fltToFrom.GetValue()
            ownerName = self.sr.fltOwner.GetValue()
            ownerID = None
            if ownerName == cfg.eveowners.Get(eve.session.charid).name:
                ownerID = eve.session.charid
            elif ownerName == cfg.eveowners.Get(eve.session.corpid).name:
                ownerID = eve.session.corpid
            elif IsSearchStringLongEnough(ownerName):
                ownerID = uix.Search(ownerName.lower(), None, const.categoryOwner, hideNPC=1, filterGroups=[const.groupCharacter, const.groupCorporation], exact=1, searchWndName='contractOwnerNameSearch')
            if ownerID == None:
                return 
            filtStatus = int(self.sr.fltStatus.GetValue())
            contractType = self.sr.fltType.GetValue()
            startContractID = self.pages.get(self.currPage, None)
            _contracts = sm.ProxySvc('contractProxy').GetContractListForOwner(ownerID, filtStatus, contractType, isAccepted, num=RESULTS_PER_PAGE, startContractID=startContractID)
            contracts = _contracts.contracts
            ownerIDs = {}
            for r in contracts:
                ownerIDs[r.issuerID] = 1
                ownerIDs[r.issuerCorpID] = 1
                ownerIDs[r.acceptorID] = 1
                ownerIDs[r.assigneeID] = 1

            cfg.eveowners.Prime(ownerIDs.keys())
            scrolllist = []
            for c in contracts:
                additionalColumns = ''
                if filtStatus == const.conStatusOutstanding:
                    issued = {False: util.FmtDate(c.dateIssued, 'ss'),
                     True: '-'}[(c.type == const.conTypeAuction and c.issuerID != eve.session.charid)]
                    additionalColumns = '<t>%s<t>%s' % (issued, ConFmtDate(c.dateExpired - blue.os.GetTime(), c.type == const.conTypeAuction))
                elif filtStatus == const.conStatusInProgress:
                    additionalColumns = '<t>%s<t>%s' % (util.FmtDate(c.dateAccepted, 'ss'), ConFmtDate(c.dateAccepted + DAY * c.numDays - blue.os.GetTime(), c.type == const.conTypeAuction))
                else:
                    additionalColumns = '<t>%s<t>%s' % (GetColoredContractStatusText(c.status), util.FmtDate(c.dateCompleted, 'ss'))
                text = '...'
                data = {'contract': c,
                 'contractItems': _contracts.items.get(c.contractID, []),
                 'status': filtStatus,
                 'text': text,
                 'label': text,
                 'additionalColumns': additionalColumns,
                 'callback': self.OnSelectContract,
                 'sort_%s' % mls.UI_CONTRACTS_CONTRACT: -c.contractID,
                 'sort_%s' % mls.UI_CONTRACTS_DATECOMPLETED: -c.dateCompleted,
                 'sort_%s' % mls.UI_CONTRACTS_TIMELEFT: -c.dateExpired}
                scrolllist.append(listentry.Get('ContractEntrySmall', data))

            headers = [mls.UI_CONTRACTS_CONTRACT,
             mls.UI_GENERIC_TYPE,
             mls.UI_GENERIC_FROM,
             mls.UI_GENERIC_TO]
            if filtStatus == const.conStatusOutstanding:
                headers.extend([mls.UI_CONTRACTS_DATEISSUED, mls.UI_CONTRACTS_TIMELEFT])
            elif filtStatus == const.conStatusInProgress:
                headers.extend([mls.UI_CONTRACTS_DATEACCEPTED, mls.UI_CONTRACTS_TIMELEFT])
            else:
                headers.extend([mls.UI_GENERIC_STATUS, mls.UI_CONTRACTS_DATECOMPLETED])
            self.sr.contractlist.ShowHint()
            self.sr.contractlist.Load(contentList=scrolllist, headers=headers)
            if len(scrolllist) == 0:
                self.sr.contractlist.ShowHint(mls.UI_CONTRACTS_NOCONTRACTSFOUND)
            if len(contracts) >= 2:
                self.pages[self.currPage] = contracts[0].contractID
                self.pages[self.currPage + 1] = contracts[-1].contractID
            if len(scrolllist) < RESULTS_PER_PAGE:
                self.sr.transMyFwdBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.transMyFwdBtn.state = uiconst.UI_NORMAL
        except UserError:
            self.sr.contractlist.ShowHint(mls.UI_CONTRACTS_NOCONTRACTSFOUND)
            raise 



    def OnComboChange(self, obj, *args):
        if obj == self.sr.fltType and self.sr.fltType.GetValue() == -1:
            self.sr.fltType.SetValue(None)



    def OnSelectContract(self, *args):
        pass




class CreateContract(uicls.Window):
    __guid__ = 'form.CreateContract'
    __notifyevents__ = ['OnDeleteContract']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.ResetWizard()
        recipientID = attributes.recipientID
        contractItems = attributes.contractItems
        copyContract = attributes.copyContract
        stationID = attributes.stationID
        flag = attributes.flag
        itemIDs = attributes.itemIDs
        if stationID:
            self.data.startStation = stationID
            self.data.startStationDivision = const.flagHangar
        if flag:
            self.data.startStationDivision = flag
        if attributes.contractType:
            self.data.type = attributes.contractType
        else:
            self.contractType = const.conTypeNothing
        self.data.items = {}
        self.data.childItems = {}
        if stationID and itemIDs:
            foundItems = []
            itemsInStation = sm.GetService('contracts').GetItemsInStation(self.data.startStation, False)
            for item in itemsInStation:
                if item.itemID in itemIDs:
                    foundItems.append(item)

            flagID = const.flagHangar
            if foundItems:
                self.data.startStationDivision = foundItems[0].flagID
                for item in foundItems:
                    self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        self.currPage = 0
        self.NUM_STEPS = 4
        self.CREATECONTRACT_TITLES = {const.conTypeNothing: [mls.UI_CONTRACTS_SELECTCONTRACTTYPE,
                                '',
                                '',
                                ''],
         const.conTypeAuction: [mls.UI_CONTRACTS_SELECTCONTRACTTYPE,
                                mls.UI_CONTRACTS_PICKITEMS,
                                mls.UI_CONTRACTS_SELECTOPTIONS,
                                mls.UI_CONTRACTS_CONFIRM],
         const.conTypeItemExchange: [mls.UI_CONTRACTS_SELECTCONTRACTTYPE,
                                     mls.UI_CONTRACTS_PICKITEMS,
                                     mls.UI_CONTRACTS_SELECTOPTIONS,
                                     mls.UI_CONTRACTS_CONFIRM],
         const.conTypeCourier: [mls.UI_CONTRACTS_SELECTCONTRACTTYPE,
                                mls.UI_CONTRACTS_PICKITEMS,
                                mls.UI_CONTRACTS_SELECTOPTIONS,
                                mls.UI_CONTRACTS_CONFIRM]}
        self.isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)
        self.SetCaption(mls.UI_CONTRACTS_CREATECONTRACT)
        self.SetMinSize([400, 330])
        self.NoSeeThrough()
        self.SetScope('all')
        main = self.sr.main
        uix.Flush(self.sr.main)
        self.marketTypes = sm.GetService('contracts').GetMarketTypes()
        self.sr.pageWnd = {}
        self.lockedItems = {}
        self.state = uiconst.UI_NORMAL
        self.blockconfirmonreturn = 1
        setattr(self, 'first', True)
        if contractItems is not None:
            item = contractItems[0]
            self.data.startStation = item.locationID
            self.data.items = {}
            for item in contractItems:
                self.data.items[item.itemID] = [item.typeID, item.stacksize, item]
                if item.ownerID == session.corpid:
                    if eve.session.corprole & const.corpRoleContractManager == 0:
                        raise UserError('ConNotContractManager')
                    self.data.forCorp = True
                    self.data.startStation = sm.StartService('invCache').GetStationIDOfItem(item)
                    self.data.startStationDivision = item.flagID
                elif item.ownerID != session.charid:
                    raise RuntimeError('Not your item!')

        self.buttons = [(mls.UI_CMD_CANCEL,
          self.OnCancel,
          (),
          84), (mls.UI_CMD_PREVIOUS,
          self.OnStepChange,
          -1,
          84), (mls.UI_CMD_NEXT,
          self.OnStepChange,
          1,
          84)]
        self.sr.buttonWnd = uicls.ButtonGroup(btns=self.buttons, parent=self.sr.main, unisize=1)
        self.sr.buttonCancel = self.sr.buttonWnd.GetBtnByIdx(0)
        self.sr.buttonPrev = self.sr.buttonWnd.GetBtnByIdx(1)
        self.sr.buttonNext = self.sr.buttonWnd.GetBtnByIdx(2)
        if copyContract:
            self.CopyContract(copyContract)
        self.formWnd = xtriui.FormWnd(name='form', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self.sr.main)
        self.GotoPage(0)
        return self



    def CopyContract(self, contract):
        c = contract.contract
        self.data.type = c.type
        self.data.startStation = c.startStationID
        self.data.endStation = c.endStationID
        expireTime = 1440 * ((c.dateExpired - c.dateIssued) / const.DAY)
        self.data.expiretime = expireTime
        self.data.duration = c.numDays
        self.data.description = c.title
        if c.availability == 0:
            self.data.avail = 0
        elif c.assigneeID == session.corpid:
            self.data.avail = 2
        elif session.allianceid and c.assigneeID == session.allianceid:
            self.data.avail = 3
        else:
            self.data.avail = 1
        self.data.assigneeID = c.assigneeID
        if self.data.assigneeID:
            self.data.name = cfg.eveowners.Get(self.data.assigneeID).name
        self.data.price = c.price
        self.data.reward = c.reward
        self.data.collateral = c.collateral
        self.data.forCorp = c.forCorp
        self.data.reqItems = {}
        requestItems = defaultdict(int)
        sellItems = defaultdict(int)
        if self.data.type == const.conTypeCourier:
            uthread.new(eve.Message, 'ConCopyContractCourier')
        foundBlueprint = False
        if contract.items:
            for contractItem in contract.items:
                if contractItem.inCrate:
                    if cfg.invtypes.Get(contractItem.itemTypeID).Group().categoryID == const.categoryBlueprint:
                        foundBlueprint = True
                    sellItems[contractItem.itemTypeID] += contractItem.quantity
                else:
                    requestItems[contractItem.itemTypeID] += contractItem.quantity

            for (typeID, quantity,) in requestItems.iteritems():
                self.data.reqItems[typeID] = quantity

            self.data.items = {}
            self.data.childItems = {}
            if sellItems:
                foundItems = defaultdict(list)
                itemsInStation = sm.GetService('contracts').GetItemsInStation(self.data.startStation, self.data.forCorp)
                for item in itemsInStation:
                    if item.typeID in sellItems and sellItems[item.typeID] == item.stacksize:
                        for foundItem in foundItems[item.flagID]:
                            if item.typeID == foundItem.typeID:
                                break
                        else:
                            foundItems[item.flagID].append(item)


                flagID = const.flagHangar
                if len(foundItems) > 1:
                    maxLen = 0
                    l = []
                    for (flag, itemList,) in foundItems.iteritems():
                        if len(itemList) > maxLen or len(itemList) == maxLen and flag == const.flagHangar:
                            l = itemList
                            flagID = flag

                    foundItems = l
                elif len(foundItems) == 1:
                    foundItems = foundItems.values()[0]
                notFound = []
                for (typeID, quantity,) in sellItems.iteritems():
                    for item in foundItems:
                        if item.typeID == typeID and item.stacksize == quantity:
                            break
                    else:
                        notFound.append((typeID, quantity))


                if notFound:
                    types = ''
                    for (t, q,) in notFound:
                        types += '<li>%s x %s</li>' % (cfg.invtypes.Get(t).name, q)

                    uthread.new(eve.Message, 'ConCopyContractMissingItems', {'types': types})
                if foundItems:
                    self.data.startStationDivision = foundItems[0].flagID
                    for item in foundItems:
                        self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        if foundBlueprint:
            uthread.new(eve.Message, 'ConCopyContractBlueprint')



    def OnClose_(self, *args):
        self.UnlockItems()



    def Refresh(self):
        self.GotoPage(self.currPage)



    def Confirm(self, *args):
        pass



    def SetTitle(self):
        title = self.CREATECONTRACT_TITLES[self.data.type][self.currPage]
        title += ' (%s/%s)' % (self.currPage + 1, self.NUM_STEPS)
        if self.sr.Get('windowCaption', None) is None:
            self.sr.windowCaption = uicls.CaptionLabel(text=title, parent=self.sr.topParent, align=uiconst.RELATIVE, left=60, top=18, state=uiconst.UI_DISABLED, fontsize=18)
            uiutil.Update(self)
        else:
            self.sr.windowCaption.text = title



    def UnlockItems(self):
        for i in self.lockedItems.iterkeys():
            sm.StartService('invCache').UnlockItem(i)

        self.lockedItems = {}



    def LockItems(self, itemIDs):
        for i in itemIDs.iterkeys():
            item = itemIDs[i]
            self.lockedItems[i] = i
            sm.StartService('invCache').TryLockItem(i, 'lockItemContractFunction', {'itemType': TypeName(item[0]),
             'action': mls.UI_CONTRACTS_CREATINGCONTRACT.lower()}, 1)




    def GotoPage(self, n):
        uthread.Lock(self)
        try:
            if n < 2:
                self.UnlockItems()
            self.currPage = n
            self.SetTitle()
            for p in self.sr.pageWnd:
                self.sr.pageWnd[p].state = uiconst.UI_HIDDEN

            uix.Flush(self.formWnd)
            format = []
            self.form = retfields = reqresult = errorcheck = []
            self.sr.buttonNext.SetLabel(mls.UI_CMD_NEXT)
            self.sr.buttonPrev.state = uiconst.UI_NORMAL
            if self.data.type != const.conTypeNothing:
                self.SetWndIcon(GetContractIcon(self.data.type), mainTop=-10)
            if n == 0:
                self.sr.buttonPrev.state = uiconst.UI_HIDDEN
                uicls.Container(name='push', parent=self.formWnd, align=uiconst.TOLEFT, width=const.defaultPadding)
                s = [0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0]
                s[self.data.type] = 1
                if self.data.type == const.conTypeNothing:
                    s[const.conTypeItemExchange] = 1
                format = [{'type': 'text',
                  'text': mls.UI_CONTRACTS_CONTRACTTYPE},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'key': const.conTypeItemExchange,
                  'text': ' ' + mls.UI_CONTRACTS_ITEMEXCHANGE,
                  'required': 1,
                  'frame': 0,
                  'setvalue': s[const.conTypeItemExchange],
                  'group': 'type'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'key': const.conTypeAuction,
                  'text': ' ' + mls.UI_CONTRACTS_AUCTION,
                  'required': 1,
                  'frame': 0,
                  'setvalue': s[const.conTypeAuction],
                  'group': 'type'},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'key': const.conTypeCourier,
                  'text': ' ' + mls.UI_CONTRACTS_COURIER,
                  'required': 1,
                  'frame': 0,
                  'setvalue': s[const.conTypeCourier],
                  'group': 'type'},
                 {'type': 'btline'}]
                s = [0,
                 0,
                 0,
                 0]
                s[getattr(self.data, 'avail', 0)] = 1
                n = getattr(self.data, 'name', '')
                format.extend([{'type': 'text',
                  'text': mls.UI_CONTRACTS_CONTRACTAVAILABILITY},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'key': 0,
                  'text': ' ' + mls.UI_CONTRACTS_PUBLIC,
                  'required': 1,
                  'frame': 0,
                  'setvalue': s[0],
                  'group': 'avail',
                  'onchange': self.OnAvailChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'key': 1,
                  'text': ' ' + mls.UI_CONTRACTS_PRIVATE,
                  'required': 1,
                  'frame': 0,
                  'setvalue': s[1],
                  'group': 'avail',
                  'onchange': self.OnAvailChange},
                 {'type': 'edit',
                  'width': 120,
                  'label': '     ' + mls.UI_GENERIC_NAME_PERSON,
                  'key': 'name',
                  'required': 0,
                  'frame': 0,
                  'setvalue': n,
                  'group': 'name'}])
                if not util.IsNPC(session.corpid):
                    format.extend([{'type': 'checkbox',
                      'label': '_hide',
                      'key': 2,
                      'text': ' ' + mls.UI_CONTRACTS_MYCORP,
                      'required': 1,
                      'frame': 0,
                      'setvalue': s[2],
                      'group': 'avail',
                      'onchange': self.OnAvailChange}])
                if session.allianceid:
                    format.extend([{'type': 'checkbox',
                      'label': '_hide',
                      'key': 3,
                      'text': ' ' + mls.UI_CONTRACTS_MYALLIANCE,
                      'required': 1,
                      'frame': 0,
                      'setvalue': s[3],
                      'group': 'avail',
                      'onchange': self.OnAvailChange}])
                forCorp = getattr(self.data, 'forCorp', 0)
                if self.isContractMgr:
                    format.append({'type': 'btline'})
                    format.append({'type': 'checkbox',
                     'label': '_hide',
                     'key': 'forCorp',
                     'text': ' ' + mls.UI_CONTRACTS_ONBEHALFOFCORP % {'corpname': cfg.eveowners.Get(eve.session.corpid).name} + ' (%s)' % sm.GetService('corp').GetMyCorpAccountName(),
                     'required': 1,
                     'frame': 0,
                     'setvalue': forCorp,
                     'onchange': self.OnForCorpChange})
                else:
                    format.append({'type': 'data',
                     'key': 'forCorp',
                     'data': {'forCorp': 0}})
                uthread.new(self.WriteNumContractsAndLimitsLazy)
                n = '?'
                maxNumContracts = '?'
                limitsParent = uicls.Container(name='limitsParent', parent=self.formWnd, align=uiconst.TOBOTTOM, height=12, idx=0)
                self.limitTextWnd = uicls.Label(text='<color=0xff999999>%s: <b>%s / %s</b></color>' % (mls.UI_CONTRACTS_NUMBEROFOUTSTANDING, n, maxNumContracts), parent=limitsParent, autowidth=True, letterspace=1, fontsize=11, state=uiconst.UI_DISABLED, uppercase=0)
                (self.form, retfields, reqresult, self.panels, errorcheck, refresh,) = sm.GetService('form').GetForm(format, self.formWnd)
            elif n == 1:
                self.WriteSelectItems(mls.UI_CONTRACTS_SELECTSTATIONTOGETITEMSFROM)
            elif n == 2:
                expireTime = getattr(self.data, 'expiretime', None)
                if expireTime is None:
                    expireTime = settings.char.ui.Get('contracts_expiretime_%s' % self.data.type, 1440)
                duration = getattr(self.data, 'duration', None)
                if duration is None:
                    duration = settings.char.ui.Get('contracts_duration_%s' % self.data.type, 1)
                expireTimeOptions = []
                for t in EXPIRE_TIMES:
                    num = numDays = t / 1440
                    txt = [mls.GENERIC_DAY, mls.GENERIC_DAYS_LOWER][(numDays > 1)]
                    numWeeks = t / 10080
                    if numWeeks >= 1:
                        txt = [mls.UI_GENERIC_WEEK, mls.UI_GENERIC_WEEKS][(numWeeks > 1)]
                        num = numWeeks
                    expireTimeOptions.append(('%s %s' % (num, txt), t))

                if self.data.type == const.conTypeAuction:
                    del expireTimeOptions[-1]
                    format = [{'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 200,
                      'label': mls.UI_CONTRACTS_STARTINGBID,
                      'key': 'price',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'price', 0)},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_BUYOUTPRICEOPTIONAL,
                      'key': 'collateral',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'collateral', 0)},
                     {'type': 'push'},
                     {'type': 'combo',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_AUCTIONTIME,
                      'key': 'expiretime',
                      'options': expireTimeOptions,
                      'setvalue': getattr(self.data, 'expiretime', expireTime)},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 220,
                      'label': mls.UI_CONTRACTS_DECRIPTIONOPTIONAL,
                      'key': 'description',
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'setvalue': getattr(self.data, 'description', '')}]
                    (self.form, retfields, reqresult, self.panels, errorcheck, refresh,) = sm.GetService('form').GetForm(format, self.formWnd)
                    btnparent = uicls.Container(name='btnparent', parent=self.formWnd.sr.price, align=uiconst.TORIGHT, width=76, idx=0, padLeft=const.defaultPadding)
                    uicls.Button(parent=btnparent, label=mls.GD_TYPE_BASEPRICE, func=self.CalcBasePricePrice, btn_default=0)
                elif self.data.type == const.conTypeItemExchange:
                    isRequestItems = not not self.data.reqItems
                    format = [{'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_IWILLPAY,
                      'key': 'reward',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'reward', 0)},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 200,
                      'label': mls.UI_CONTRACTS_IWILLRECEIVE,
                      'key': 'price',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'price', 0)},
                     {'type': 'push'},
                     {'type': 'combo',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_EXPIRATION,
                      'key': 'expiretime',
                      'options': expireTimeOptions,
                      'setvalue': getattr(self.data, 'expiretime', expireTime)},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 220,
                      'label': mls.UI_CONTRACTS_DECRIPTIONOPTIONAL,
                      'key': 'description',
                      'required': 0,
                      'frame': 0,
                      'maxLength': 50,
                      'group': 'avail',
                      'setvalue': getattr(self.data, 'description', '')},
                     {'type': 'push',
                      'height': 10},
                     {'type': 'checkbox',
                      'required': 1,
                      'height': 16,
                      'setvalue': isRequestItems,
                      'key': 'requestitems',
                      'label': '',
                      'text': mls.UI_CONTRACTS_ALSOREQUESTITEMS,
                      'frame': 0,
                      'onchange': self.OnRequestItemsChange}]
                    (self.form, retfields, reqresult, self.panels, errorcheck, refresh,) = sm.GetService('form').GetForm(format, self.formWnd)
                    self.sr.reqItemsParent = reqItemsParent = uicls.Container(name='reqItemsParent', parent=self.formWnd, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=50)
                    left = const.defaultPadding + 3
                    top = 16
                    self.reqItemTypeWnd = c = uicls.SinglelineEdit(name='itemtype', parent=reqItemsParent, label=mls.UI_CONTRACTS_ITEMTYPE, align=uiconst.TOPLEFT, width=248)
                    c.OnFocusLost = self.ParseItemType
                    c.left = left
                    c.top = top
                    left += c.width + 5
                    self.reqItemQtyWnd = c = uicls.SinglelineEdit(name='itemqty', parent=reqItemsParent, label=mls.UI_GENERIC_QUANTITY, align=uiconst.TOPLEFT, width=50, ints=[0], setvalue=1)
                    c.left = left
                    c.top = top
                    left += c.width + 5
                    c = uicls.Button(parent=reqItemsParent, label=mls.UI_GENERIC_ADDITEM, func=self.AddRequestItem, pos=(left,
                     top,
                     0,
                     0), align=uiconst.TOPLEFT)
                    c.top = top
                    self.reqItemScroll = uicls.Scroll(parent=reqItemsParent, padding=(const.defaultPadding,
                     top + c.height + const.defaultPadding,
                     const.defaultPadding,
                     const.defaultPadding))
                    self.reqItemScroll.sr.id = 'reqitemscroll'
                    self.PopulateReqItemScroll()
                    btnparent = uicls.Container(name='btnparent', parent=self.formWnd.sr.price, align=uiconst.TORIGHT, width=76, idx=0, padLeft=const.defaultPadding)
                    uicls.Button(parent=btnparent, label=mls.GD_TYPE_BASEPRICE, func=self.CalcBasePricePrice, btn_default=0)
                    self.ToggleShowRequestItems(isRequestItems)
                elif self.data.type == const.conTypeCourier:
                    stationName = ''
                    if not self.data.endStation and len(self.data.items) == 1 and self.data.items.values()[0][0] == const.typePlasticWrap:
                        stationName = cfg.evelocations.Get(self.data.items.keys()[0]).name.replace('>>', '')
                    format = [{'type': 'push'},
                     {'type': 'edit',
                      'label': mls.UI_GENERIC_SHIPTO,
                      'labelwidth': 150,
                      'width': 200,
                      'key': 'endStationName',
                      'frame': 0,
                      'maxLength': 80,
                      'setvalue': stationName},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_REWARD,
                      'key': 'reward',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'reward', 0)},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 200,
                      'label': mls.UI_CONTRACTS_COLLATERAL,
                      'key': 'collateral',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'floatonly': [0, MAX_AMOUNT],
                      'setvalue': getattr(self.data, 'collateral', 0)},
                     {'type': 'push'},
                     {'type': 'combo',
                      'labelwidth': 150,
                      'width': 120,
                      'label': mls.UI_CONTRACTS_EXPIRATION,
                      'key': 'expiretime',
                      'options': expireTimeOptions,
                      'setvalue': expireTime},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 32,
                      'label': mls.UI_CONTRACTS_FREEFORMTIME,
                      'key': 'duration',
                      'autoselect': 1,
                      'required': 0,
                      'frame': 0,
                      'group': 'duration',
                      'setvalue': duration,
                      'intonly': [1, 365]},
                     {'type': 'push'},
                     {'type': 'edit',
                      'labelwidth': 150,
                      'width': 220,
                      'label': mls.UI_CONTRACTS_DECRIPTIONOPTIONAL,
                      'key': 'description',
                      'required': 0,
                      'frame': 0,
                      'group': 'avail',
                      'setvalue': getattr(self.data, 'description', '')}]
                    (self.form, retfields, reqresult, self.panels, errorcheck, refresh,) = sm.GetService('form').GetForm(format, self.formWnd)
                    btnparent = uicls.Container(name='btnparent', parent=self.formWnd.sr.endStationName, align=uiconst.TORIGHT, idx=0, padLeft=const.defaultPadding)
                    btn = uicls.Button(parent=btnparent, label=mls.UI_CMD_SEARCH, func=self.SearchStationFromBtn, btn_default=0)
                    if self.data.endStation:
                        self.SearchStation(self.data.endStation)
                    c = uicls.Container(name='push', parent=self.formWnd, align=uiconst.TOTOP, height=10)
                    uicls.Line(parent=c, align=uiconst.TOBOTTOM)
                    c = uicls.Container(name='push', parent=self.formWnd, align=uiconst.TOTOP, height=5)
                    self.sr.courierHint = uicls.Label(text='', align=uiconst.TOLEFT, parent=self.formWnd, autowidth=True, letterspace=1, fontsize=11, state=uiconst.UI_DISABLED, uppercase=0, left=6)
                    self.UpdateCourierHint()
                    if not getattr(self, 'courierHint', None):
                        self.courierHint = base.AutoTimer(1000, self.UpdateCourierHint)
                    btnparent2 = uicls.Container(name='btnparent', parent=self.formWnd.sr.collateral, align=uiconst.TORIGHT, idx=0, padLeft=const.defaultPadding)
                    btn2 = uicls.Button(parent=btnparent2, label=mls.GD_TYPE_BASEPRICE, func=self.CalcBasePriceCollateral, btn_default=0)
                    btnWidth = max(btn.width, btn2.width)
                    btnparent.width = btnWidth
                    btnparent2.width = btnWidth
            elif n == 3:
                if hasattr(self.data, 'expiretime'):
                    settings.char.ui.Set('contracts_expiretime_%s' % self.data.type, self.data.expiretime)
                if hasattr(self.data, 'duration'):
                    settings.char.ui.Set('contracts_duration_%s' % self.data.type, self.data.duration)
                rows = []
                rows.append([mls.UI_CONTRACTS_CONTRACTTYPE, GetContractTypeText(self.data.type)])
                desc = self.data.description
                if desc == '':
                    desc = mls.UI_CONTRACTS_NONE
                rows.append([mls.UI_CONTRACTS_DESCRIPTION, desc])
                avail = self.data.avail
                a = mls.UI_CONTRACTS_PUBLIC
                if avail > 0:
                    a = mls.UI_CONTRACTS_PRIVATE
                    assignee = cfg.eveowners.Get(self.data.assigneeID)
                    a += ' (<a href=showinfo:%s//%s>%s</a>)' % (assignee.typeID, self.data.assigneeID, assignee.name)
                else:
                    a += ' (%s: <b>%s</b>)' % (mls.UI_GENERIC_REGION, cfg.evelocations.Get(cfg.evelocations.Get(self.data.startStation).Station().regionID).name)
                rows.append([mls.UI_CONTRACTS_AVAILABILITY, a])
                loc = mls.UI_CONTRACTS_NONE
                if self.data.startStation:
                    loc = cfg.evelocations.Get(self.data.startStation).name
                    startStationTypeID = sm.GetService('ui').GetStation(self.data.startStation).stationTypeID
                    loc = '<a href=showinfo:%s//%s>%s</a>' % (startStationTypeID, self.data.startStation, loc)
                rows.append([mls.UI_CONTRACTS_LOCATION, loc])
                rows.append([mls.UI_CONTRACTS_EXPIRATION, '%s (%s)' % (util.FmtDate(self.data.expiretime * MIN + blue.os.GetTime(), 'ss'), util.FmtDate(self.data.expiretime * MIN))])
                salesTax = ''
                brokersFee = ''
                deposit = ''
                if self.data.avail > 0:
                    salesTax = mls.UI_CONTRACTS_NONE
                    brokersFee = util.FmtISK(const_conBrokersFeeMinimum, 0)
                    deposit = util.FmtISK(0.0, 0)
                else:
                    skillLevels = util.KeyVal()
                    skillLevels.brokerRelations = getattr(sm.GetService('skills').HasSkill(const.typeBrokerRelations), 'skillLevel', 0)
                    skillLevels.accounting = getattr(sm.GetService('skills').HasSkill(const.typeAccounting), 'skillLevel', 0)
                    ret = CalcContractFees(self.data.Get('price', 0), self.data.Get('reward', 0), self.data.type, self.data.expiretime, skillLevels)
                    salesTax = '%s (%s%%)' % (util.FmtISK(ret.salesTaxAmt, 0), ret.salesTax * 100.0)
                    if ret.brokersFeeAmt == const_conBrokersFeeMinimum:
                        brokersFee = '%s (%s)' % (util.FmtISK(ret.brokersFeeAmt, 0), mls.UI_GENERIC_MINIMUM.lower())
                    else:
                        brokersFee = '%s (%s%%)' % (util.FmtISK(ret.brokersFeeAmt, 0), ret.brokersFee * 100.0)
                    minDeposit = const_conDepositMinimum
                    if self.data.type == const.conTypeCourier:
                        minDeposit = minDeposit / 10
                    if ret.depositAmt == minDeposit:
                        deposit = '%s (%s)' % (util.FmtISK(ret.depositAmt, 0), mls.UI_GENERIC_MINIMUM.lower())
                    else:
                        deposit = '%s (%s%%)' % (util.FmtISK(ret.depositAmt, 0), ret.deposit * 100.0)
                    if self.data.type == const.conTypeAuction:
                        p = const_conSalesTax - float(skillLevels.accounting) * 0.001
                        buyout = self.data.collateral
                        if buyout < self.data.Get('price', 0):
                            buyout = MAX_AMOUNT
                        ret2 = CalcContractFees(buyout, self.data.Get('reward', 0), self.data.type, self.data.expiretime, skillLevels)
                        maxSalesTax = ret2.salesTaxAmt
                        salesTax = '%s%% %s (%s)' % (100.0 * p, mls.UI_CONTRACTS_OFSELLPRICE, mls.UI_CONTRACTS_MAXSALESTAX % {'amt': FmtISKWithDescription(maxSalesTax, True)})
                    elif self.data.type == const.conTypeCourier:
                        salesTax = mls.UI_CONTRACTS_NONE
                rows.append([mls.UI_CONTRACTS_SALESTAX, salesTax])
                rows.append([mls.UI_CONTRACTS_BROKERSFEE, brokersFee])
                rows.append([mls.UI_CONTRACTS_DEPOSIT, deposit])
                rows.append([])
                if self.data.type == const.conTypeAuction:
                    rows.append([mls.UI_CONTRACTS_STARTINGBID, FmtISKWithDescription(self.data.price)])
                    buyout = mls.UI_CONTRACTS_NONE
                    if self.data.collateral > 0:
                        buyout = FmtISKWithDescription(self.data.collateral)
                    rows.append([mls.UI_CONTRACTS_BUYOUTPRICE, buyout])
                    items = ''
                    for i in self.data.items:
                        items += '%s x %s<br>' % (TypeName(self.data.items[i][0]), util.FmtAmt(self.data.items[i][1]))
                        chld = self.data.childItems.get(i, [])
                        for c in chld:
                            items += ' - %s x %s<br>' % (TypeName(c[1]), c[2])


                    rows.append([mls.UI_CONTRACTS_ITEMSFORSALE, items])
                elif self.data.type == const.conTypeItemExchange:
                    rows.append([mls.UI_CONTRACTS_IWILLPAY, FmtISKWithDescription(self.data.reward)])
                    rows.append([mls.UI_CONTRACTS_IWILLRECEIVE, FmtISKWithDescription(self.data.price)])
                    items = ''
                    for i in self.data.items:
                        items += '%s x %s<br>' % (TypeName(self.data.items[i][0]), util.FmtCurrency(self.data.items[i][1], showFractionsAlways=0, currency=None))
                        chld = self.data.childItems.get(i, [])
                        for c in chld:
                            items += ' - %s x %s<br>' % (TypeName(c[1]), c[2])


                    rows.append([mls.UI_CONTRACTS_ITEMSFORSALE, items])
                    itemStr = '<br>'.join([ '%s x %s' % (TypeName(typeID), util.FmtCurrency(qty, showFractionsAlways=0, currency=None)) for (typeID, qty,) in self.data.reqItems.iteritems() ])
                    rows.append([mls.UI_CONTRACTS_ITEMSREQUIRED, itemStr])
                elif self.data.type == const.conTypeCourier:
                    rows.append([mls.UI_CONTRACTS_REWARD, FmtISKWithDescription(self.data.reward)])
                    rows.append([mls.UI_CONTRACTS_COLLATERAL, FmtISKWithDescription(self.data.collateral)])
                    loc = ''
                    if self.data.startStation:
                        loc = cfg.evelocations.Get(self.data.endStation).name
                        typeID = sm.GetService('ui').GetStation(self.data.endStation).stationTypeID
                        loc = '<a href=showinfo:%s//%s>%s</a>' % (typeID, self.data.endStation, loc)
                    rows.append([mls.UI_CONTRACTS_DESTINATION, loc])
                    rows.append([mls.UI_CONTRACTS_FREEFORMTIME, self.data.duration])
                    volume = 0
                    for i in self.data.items:
                        volume += self.GetItemVolumeMaybe(self.data.items[i][2], int(self.data.items[i][1]))

                    rows.append([mls.UI_CONTRACTS_VOLUME, '%s m\xb3' % util.FmtAmt(volume, showFraction=3)])
                    items = ''
                    for i in self.data.items:
                        items += '%s x %s<br>' % (TypeName(self.data.items[i][0]), util.FmtCurrency(self.data.items[i][1], showFractionsAlways=0, currency=None))
                        chld = self.data.childItems.get(i, [])
                        for c in chld:
                            items += ' - %s x %s<br>' % (TypeName(c[1]), c[2])


                    rows.append([mls.UI_CONTRACTS_ITEMS, items])
                else:
                    raise RuntimeError('Contract type not implemented!')
                self.WriteConfirm(rows)
                self.sr.buttonNext.SetLabel(mls.UI_CMD_FINISH)
            self.formdata = [retfields, reqresult, errorcheck]

        finally:
            uthread.UnLock(self)




    def OnRequestItemsChange(self, chkbox, *args):
        if not chkbox.GetValue():
            self.reqItemScroll.Clear()
            self.data.reqItems = {}
        self.ToggleShowRequestItems(not not chkbox.GetValue())



    def ToggleShowRequestItems(self, isIt):
        self.sr.reqItemsParent.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][isIt]



    def WriteNumContractsAndLimitsLazy(self):
        try:
            (n, maxNumContracts,) = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
            self.limitTextWnd.text = ' <color=0xff999999>%s: <b>%s / %s</b></color>' % (mls.UI_CONTRACTS_NUMBEROFOUTSTANDING, n, maxNumContracts)
        except:
            sys.exc_clear()



    def OnForCorpChange(self, wnd, *args):
        self.data.forCorp = wnd.GetValue()
        self.OnAvailChange(None)
        self.data.items = {}



    def OnAvailChange(self, wnd, *args):
        if not wnd:
            key = getattr(self.data, 'lastAvailKey', 0)
        else:
            key = wnd.data.get('key')
            self.data.lastAvailKey = key
        if key == 2:
            (n, maxNumContracts,) = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), eve.session.corpid)
        elif key == 1:
            (n, maxNumContracts,) = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
        else:
            (n, maxNumContracts,) = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), 0)
        try:
            self.limitTextWnd.text = ' <color=0xff999999>%s: <b>%s / %s</b></color>' % (mls.UI_CONTRACTS_NUMBEROFOUTSTANDING, n, maxNumContracts)
        except:
            sys.exc_clear()



    def CreateContract(self):
        sm.GetService('loading').ProgressWnd(mls.UI_CONTRACTS_CREATINGCONTRACT, '', 2, 10)
        try:
            self.state = uiconst.UI_HIDDEN
            type = getattr(self.data, 'type', const.conTypeNothing)
            assigneeID = getattr(self.data, 'assigneeID', 0)
            startStationID = getattr(self.data, 'startStation', 0)
            startStationDivision = getattr(self.data, 'startStationDivision', None)
            endStationID = getattr(self.data, 'endStation', 0)
            forCorp = getattr(self.data, 'forCorp', 0) > 0
            if not forCorp:
                startStationDivision = 4
            price = getattr(self.data, 'price', 0)
            reward = getattr(self.data, 'reward', 0)
            collateral = getattr(self.data, 'collateral', 0)
            expiretime = getattr(self.data, 'expiretime', 0)
            duration = getattr(self.data, 'duration', 0)
            title = getattr(self.data, 'description', '')
            description = getattr(self.data, 'body', '')
            items = []
            itemsReq = map(list, self.data.reqItems.items())
            for i in self.data.items:
                items.append([i, self.data.items[i][1]])

            isPrivate = not not assigneeID
            args = (type,
             isPrivate,
             assigneeID,
             expiretime,
             duration,
             startStationID,
             endStationID,
             price,
             reward,
             collateral,
             title,
             description,
             items,
             startStationDivision,
             itemsReq,
             forCorp)
            try:
                contractID = sm.GetService('contracts').CreateContract(*args)
            except UserError as e:
                if e.msg == 'NotEnoughCargoSpace':
                    if eve.Message('ConAskRemoveToHangar', {}, uiconst.YESNO) == uiconst.ID_YES:
                        contractID = sm.GetService('contracts').CreateContract(confirm=CREATECONTRACT_CONFIRM_CHARGESTOHANGAR, *args)
                    else:
                        raise 
                else:
                    raise 
            if contractID:
                locData = util.KeyVal(**{'locationID': startStationID,
                 'groupID': const.groupStation})
                sm.GetService('contracts').ShowContract(contractID)
                self.SelfDestruct()
            else:
                self.state = uiconst.UI_NORMAL

        finally:
            self.state = uiconst.UI_NORMAL
            sm.GetService('loading').ProgressWnd(mls.UI_CONTRACTS_CREATINGCONTRACT, '', 10, 10)




    def WriteConfirm(self, rows):
        body = ''
        for r in rows:
            if r == []:
                body += '<tr><td colspan=2><hr></td></tr>'
            else:
                body += '<tr><td width=100 valign=top><b>%(key)s</b></td><td>%(val)s</td></tr>' % {'key': r[0],
                 'val': r[1]}

        message = '\n              <TABLE width="98%%">%s</TABLE>\n        ' % body
        messageArea = uicls.Edit(parent=self.formWnd, readonly=1, hideBackground=1)
        messageArea.SetValue(message)



    def ParseItemType(self, wnd, *args):
        if self.destroyed or getattr(self, 'parsingItemType', False):
            return 
        try:
            self.parsingItemType = True
            txt = wnd.GetValue()
            if len(txt) == 0 or not IsSearchStringLongEnough(txt):
                return 
            else:
                types = []
                for t in self.marketTypes:
                    if MatchInvTypeName(txt, t):
                        types.append(t.typeID)

                typeID = SelectItemTypeDlg(types)
                if typeID:
                    wnd.SetValue(TypeName(typeID))
                    self.parsedItemType = typeID
                return typeID
            self.parsedItemType = typeID

        finally:
            self.parsingItemType = False




    def AddRequestItem(self, *args):
        typeID = getattr(self, 'parsedItemType', None) or self.ParseItemType(self.reqItemTypeWnd)
        self.parsedItemType = None
        if not typeID:
            return 
        qty = self.reqItemQtyWnd.GetValue()
        if qty < 1:
            return 
        self.data.reqItems[typeID] = qty
        self.reqItemTypeWnd.SetValue('')
        self.reqItemQtyWnd.SetValue(1)
        self.PopulateReqItemScroll()



    def RemoveRequestItem(self, wnd, *args):
        del self.data.reqItems[wnd.sr.node.typeID]
        self.PopulateReqItemScroll()



    def PopulateReqItemScroll(self):
        scrolllist = []
        self.reqItemScroll.Clear()
        for (typeID, qty,) in self.data.reqItems.iteritems():
            typeName = TypeName(typeID)
            data = util.KeyVal()
            data.label = '%s x %s' % (typeName, qty)
            data.typeID = typeID
            data.name = typeName
            data.OnDblClick = self.RemoveRequestItem
            data.GetMenu = self.GetReqItemMenu
            scrolllist.append(listentry.Get('Generic', data=data))

        self.reqItemScroll.Load(contentList=scrolllist, headers=[])
        if scrolllist == []:
            self.reqItemScroll.ShowHint(mls.UI_CONTRACTS_ADDITEMSABOVE)
        else:
            self.reqItemScroll.ShowHint()



    def GetReqItemMenu(self, wnd, *args):
        m = []
        m.append((mls.UI_GENERIC_REMOVEITEM, self.RemoveRequestItem, (wnd,)))
        return m



    def SearchStationFromBtn(self, *args):
        self.SearchStation()



    def SearchStation(self, stationID = None, *args):
        searchstr = self.form.sr.endStationName.GetValue().strip()
        if stationID is None and not IsSearchStringLongEnough(searchstr):
            return 
        sm.GetService('loading').Cycle(mls.UI_GENERIC_SEARCHING, mls.UI_LOAD_SEARCHHINT2 % {'name': searchstr})
        if stationID is None:
            stationID = uix.Search(searchstr.lower(), const.groupStation, searchWndName='contractSearchStationSearch')
        sm.GetService('loading').StopCycle()
        if stationID:
            locationinfo = cfg.evelocations.Get(stationID)
            self.courierDropLocation = stationID
            self.form.sr.endStationName.SetValue(locationinfo.name)
        self.data.endStation = stationID



    def UpdateCourierHint(self):
        if self.data.endStation and self.data.startStation and self.sr.courierHint and not self.sr.courierHint.destroyed:
            startSolarSystemID = sm.GetService('ui').GetStation(self.data.startStation).solarSystemID
            endSolarSystemID = sm.GetService('ui').GetStation(self.data.endStation).solarSystemID
            numJumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(endSolarSystemID, startSolarSystemID)
            perJump = 0
            perJump = self.formWnd.sr.reward.GetValue() / (numJumps or 1)
            sec = sm.GetService('contracts').GetRouteSecurityWarning(startSolarSystemID, endSolarSystemID)
            hint = mls.UI_CONTRACTS_COURIERHINT % {'jumps': numJumps,
             'amt': util.FmtAmt(perJump)}
            if sec:
                hint += '<br>' + sec
            self.sr.courierHint.SetText(hint)



    def GetNumContractsAndLimits(self, forCorp, assigneeID):
        skill = sm.GetService('skills').HasSkill([const.typeContracting, const.typeCorporationContracting][forCorp])
        if skill is None:
            lvl = 0
        else:
            lvl = skill.skillLevel
        if forCorp:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL_CORP[lvl]
        else:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL[lvl]
        innerCorp = False
        if assigneeID > 0:
            if util.IsCorporation(assigneeID):
                if assigneeID == eve.session.corpid:
                    innerCorp = True
            elif util.IsCharacter(assigneeID):
                corpID = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(assigneeID)
                if corpID == eve.session.corpid and not util.IsNPC(eve.session.corpid):
                    innerCorp = True
        n = 0
        try:
            if getattr(self, 'numOutstandingContracts', None) is None:
                self.numOutstandingContracts = sm.GetService('contracts').NumOutstandingContracts()
            if forCorp:
                if innerCorp:
                    n = self.numOutstandingContracts.myCorpTotal
                else:
                    n = self.numOutstandingContracts.nonCorpForMyCorp
            elif innerCorp:
                n = self.numOutstandingContracts.myCharTotal
            else:
                n = self.numOutstandingContracts.nonCorpForMyChar

        finally:
            return (n, [maxNumContracts, MAX_NUM_CONTRACTS][innerCorp])




    def FinishStep(self, step):
        uthread.Lock(self)
        try:
            result = sm.GetService('form').ProcessForm(self.formdata[0], self.formdata[1])
            lastType = getattr(self.data, 'type', None)
            if step == 0 and result['type'] != lastType and not getattr(self, 'first', False):
                self.ResetWizard()
            setattr(self, 'first', False)
            for i in result:
                setattr(self.data, str(i), result[i])

            if step == 0:
                ownerID = None
                if self.data.avail == 1:
                    if IsSearchStringLongEnough(self.data.name):
                        ownerID = uix.Search(self.data.name.lower(), const.groupCharacter, const.categoryOwner, hideNPC=1, filterGroups=[const.groupCharacter, const.groupCorporation, const.groupAlliance], searchWndName='contractFinishStepSearch')
                    if not ownerID:
                        return False
                    if self.data.type == const.conTypeAuction:
                        owner = cfg.eveowners.Get(ownerID)
                        if owner.IsCharacter() or owner.IsCorporation() and ownerID != session.corpid:
                            raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_24})
                elif self.data.name != '':
                    raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_1})
                elif self.data.avail == 2:
                    ownerID = eve.session.corpid
                elif self.data.avail == 3:
                    ownerID = eve.session.allianceid
                    if not ownerID:
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_18})
                self.data.assigneeID = ownerID
                forCorp = not not self.data.forCorp
                (n, maxNumContracts,) = self.GetNumContractsAndLimits(forCorp, self.data.assigneeID)
                if n >= maxNumContracts and maxNumContracts >= 0:
                    info = mls.UI_CONTRACTS_CREATEWIZ_MAXNUMINFO_INCREASESKILL % {'skill': TypeName([const.typeContracting, const.typeCorporationContracting][forCorp])}
                    raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_17 % {'num': maxNumContracts,
                              'info': info}})
            elif step == 1:
                ILLEGAL_ITEMGROUPS = [const.groupCapsule]
                self.data.childItems = {}
                for i in self.data.items:
                    type = cfg.invtypes.Get(self.data.items[i][0])
                    if type.groupID in ILLEGAL_ITEMGROUPS:
                        raise UserError('ConIllegalType')
                    if i in (eve.session.shipid, util.GetActiveShip()):
                        raise UserError('ConCannotTradeCurrentShip')
                    isContainer = type.categoryID == const.categoryShip or type.groupID in (const.groupCargoContainer,
                     const.groupSecureCargoContainer,
                     const.groupAuditLogSecureContainer,
                     const.groupFreightContainer)
                    if isContainer:
                        div = 4
                        if self.data.forCorp:
                            div = self.data.startStationDivision
                        items = sm.GetService('contracts').GetItemsInContainer(self.data.startStation, i, self.data.forCorp, div)
                        if items is not None and len(items) > 0:
                            lst = ''
                            totalVolume = 0
                            for l in items:
                                lst += TypeName(l.typeID) + ', '
                                val = [l.itemID, l.typeID, l.stacksize]
                                if i not in self.data.childItems:
                                    self.data.childItems[i] = []
                                self.data.childItems[i].append(val)
                                totalVolume += self.GetItemVolumeMaybe(l, l.stacksize)

                            if eve.Message('ConNonEmptyContainer2', {'container': TypeName(type.typeID),
                             'items': lst,
                             'volume': totalVolume}, uiconst.YESNO) != uiconst.ID_YES:
                                return False

                if self.data.type == const.conTypeCourier:
                    volume = 0
                    for i in self.data.items:
                        type = cfg.invtypes.Get(self.data.items[i][0])
                        item = self.data.items[i][2]
                        volume += self.GetItemVolumeMaybe(item, int(self.data.items[i][1]))

                    if volume > const_conCourierMaxVolume:
                        raise UserError('ConExceedsMaxVolume', {'max': util.FmtAmt(const_conCourierMaxVolume, showFraction=3),
                         'vol': util.FmtAmt(volume, showFraction=3)})
                    elif volume > const_conCourierWarningVolume:
                        if eve.Message('ConNeedFreighter', {'vol': util.FmtAmt(volume, showFraction=3)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return False
                if not self.data.startStation or self.data.startStation == 0:
                    raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_3})
                elif self.data.type in [const.conTypeCourier, const.conTypeAuction] and len(self.data.items) == 0:
                    raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_4})
                if self.data.type in [const.conTypeAuction, const.conTypeItemExchange]:
                    div = 4
                    insuranceContracts = []
                    for i in self.data.items:
                        item = self.data.items[i]
                        categoryID = cfg.invtypes.Get(item[0]).categoryID
                        if item[2].singleton and categoryID == const.categoryShip:
                            contract = sm.RemoteSvc('insuranceSvc').GetContractForShip(i)
                            if contract:
                                insuranceContracts.append([contract, item[0]])

                    for contract in insuranceContracts:
                        example = (TYPEID, contract[1])
                        if (contract[0].ownerID == eve.session.corpid or self.data.forCorp) and self.data.avail != const.conAvailPublic:
                            if eve.Message('ConInsuredShipCorp', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                                return False
                        else:
                            if eve.Message('ConInsuredShip', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                                return False

                    for i in self.data.items:
                        item = self.data.items[i]
                        categoryID = cfg.invtypes.Get(item[0]).categoryID
                        if categoryID == const.categoryShip and item[2].singleton:
                            sm.GetService('invCache').RemoveInventoryContainer(item[2])

                self.LockItems(self.data.items)
            elif step == 2:
                if hasattr(self.data, 'price'):
                    self.data.price = int(self.data.price)
                if hasattr(self.data, 'reward'):
                    self.data.reward = int(self.data.reward)
                if hasattr(self.data, 'collateral'):
                    self.data.collateral = int(self.data.collateral)
                if len(self.data.description) > MAX_TITLE_LENGTH:
                    raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_16 % {'len': len(self.data.description),
                              'max': MAX_TITLE_LENGTH}})
                if self.data.type == const.conTypeAuction:
                    if self.data.price < const_conBidMinimum and self.data.avail == 0:
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_5 % {'min': util.FmtAmt(const_conBidMinimum)}})
                    elif self.data.price > self.data.collateral and self.data.collateral > 0:
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_6})
                elif self.data.type == const.conTypeCourier:
                    if not self.data.endStation and len(self.form.sr.endStationName.GetValue()) > 0:
                        self.SearchStation()
                        if not self.data.endStation:
                            return False
                    if not self.data.endStation:
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_7})
                    if not self.data.assigneeID:
                        if self.data.reward < MIN_CONTRACT_MONEY:
                            raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_11})
                        if self.data.collateral < MIN_CONTRACT_MONEY:
                            raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_12})
                elif self.data.type == const.conTypeItemExchange:
                    if self.data.price != 0.0 and self.data.reward != 0.0:
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_8})
                    if not self.data.assigneeID:
                        if self.data.reqItems == {} and self.data.price < MIN_CONTRACT_MONEY:
                            raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_20})
                    if self.reqItemTypeWnd.GetValue() != '':
                        raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_19})
                    if not self.data.assigneeID:
                        if (self.data.reqItems != {} or self.data.price > 0) and len(self.data.items) == 0 and self.data.reward == 0:
                            raise UserError('CustomInfo', {'info': mls.UI_CONTRACTS_CREATEWIZ_23})
                else:
                    raise RuntimeError('Not implemented!')
            else:
                raise RuntimeError('Illegal step (%s)' % step)
            return True

        finally:
            uthread.UnLock(self)




    def OnComboChange(self, wnd, *args):
        if wnd.name == 'startStation' or wnd.name == 'startStationDivision':
            if wnd.name == 'startStation':
                self.data.startStation = wnd.GetValue()
            else:
                self.data.startStationDivision = wnd.GetValue()
            self.data.items = {}
            self.GotoPage(self.currPage)



    def OnStepChange(self, move, *args):
        if self.currPage + move >= 4:
            if eve.Message('ConConfirmCreateContract', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                try:
                    self.CreateContract()
                except:
                    self.Maximize()
                    raise 
        elif self.currPage + move >= 0 and (move < 0 or self.FinishStep(self.currPage)):
            self.GotoPage(self.currPage + move)



    def ClickItem(self, *args):
        pass



    def OnDeleteContract(self, contractID, *args):
        self.numOutstandingContracts = None



    def OnCancel(self, *args):
        if eve.Message('ConAreYouSureYouWantToCancel', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.SelfDestruct()



    def ResetWizard(self):
        self.data = util.KeyVal()
        self.data.items = {}
        self.data.reqItems = {}
        self.data.startStation = None
        self.data.endStation = None
        self.data.startStationDivision = 0
        self.data.type = const.conTypeNothing
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)



    def WriteSelectItems(self, title):
        forCorp = self.data.forCorp
        deliveriesRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        if forCorp:
            rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'offices')
            sortops = []
            for r in rows:
                stationName = cfg.evelocations.Get(r.locationID).name
                sortops.append((stationName, (stationName, r.locationID)))

            if eve.session.corprole & deliveriesRoles > 0:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'deliveries')
                for r in rows:
                    stationName = cfg.evelocations.Get(r.locationID).name
                    stat = (stationName, (stationName, r.locationID))
                    if stat not in sortops:
                        sortops.append(stat)

            ops = [(title, 0)] + uiutil.SortListOfTuples(sortops)
        else:
            stations = eve.GetInventory(const.containerGlobal).ListStations()
            primeloc = []
            for station in stations:
                primeloc.append(station.stationID)

            if len(primeloc):
                cfg.evelocations.Prime(primeloc)
            sortops = []
            for station in stations:
                stationName = cfg.evelocations.Get(station.stationID).name
                sortops.append((stationName.lower(), ('%s (%s %s)' % (stationName, station.itemCount, mls.UI_GENERIC_ITEMS), station.stationID)))

            ops = [(title, 0)] + uiutil.SortListOfTuples(sortops)
        comboParent = uicls.Container(name='comboParent', parent=self.formWnd, align=uiconst.TOTOP, top=const.defaultPadding)
        uicls.Container(name='push', parent=comboParent, align=uiconst.TOLEFT, width=1)
        uicls.Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=1)
        combo = uicls.Combo(label=None, parent=comboParent, options=ops, name='startStation', select=None, callback=self.OnComboChange, align=uiconst.TOALL)
        comboParent.height = 18
        nudge = 0
        if forCorp:
            divs = [(mls.UI_GENERIC_SELECTDIVISION, 0)]
            paramsByDivision = {1: (const.flagHangar, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
             2: (const.flagCorpSAG2, const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
             3: (const.flagCorpSAG3, const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
             4: (const.flagCorpSAG4, const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
             5: (const.flagCorpSAG5, const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
             6: (const.flagCorpSAG6, const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
             7: (const.flagCorpSAG7, const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
            divisions = sm.GetService('corp').GetDivisionNames()
            i = 0
            NUM_DIVISIONS = 7
            while i < NUM_DIVISIONS:
                i += 1
                (flag, roleCanQuery, roleCanTake,) = paramsByDivision[i]
                divisionName = divisions[i]
                divs.append((divisionName, flag))

            if eve.session.corprole & deliveriesRoles > 0:
                divs.append((mls.UI_CMD_DELIVERIES, const.flagCorpMarket))
            comboDiv = uicls.Combo(label='', parent=comboParent, options=divs, name='startStationDivision', select=None, callback=self.OnComboChange, align=uiconst.TORIGHT, width=100, pos=(1, 0, 0, 0), idx=0)
            uicls.Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=4, idx=1)
            nudge = 18
        if eve.session.stationid and self.data.startStation is None:
            self.data.startStation = eve.session.stationid
        i = 0
        for (name, val,) in combo.entries:
            if val == self.data.startStation:
                combo.SelectItemByIndex(i)
                break
            i += 1

        if forCorp:
            i = 0
            for (name, val,) in comboDiv.entries:
                if val == self.data.startStationDivision:
                    comboDiv.SelectItemByIndex(i)
                    break
                i += 1

        c = uicls.Container(name='volume', parent=self.formWnd, align=uiconst.TOBOTTOM, width=6, height=20)
        self.sr.volumeText = uicls.Label(text=mls.UI_CONTRACTS_NUMBEROFSELECTED % {'num': 0,
         'vol': 0}, parent=c, letterspace=1, fontsize=12, state=uiconst.UI_DISABLED, uppercase=0, align=uiconst.CENTERRIGHT)
        self.UpdateNumberOfItems()
        self.sr.itemsScroll = uicls.Scroll(parent=self.formWnd, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        if forCorp:
            if not self.data.startStation:
                self.sr.itemsScroll.ShowHint(mls.UI_MARKET_SELECTSTATION)
                if self.data.startStationDivision == 0:
                    self.sr.itemsScroll.ShowHint(mls.UI_GENERIC_SELECTSTATIONDIVISION)
            elif self.data.startStationDivision == 0:
                self.sr.itemsScroll.ShowHint(mls.UI_GENERIC_SELECTDIVISION)
        if self.data.startStation and (not forCorp or self.data.startStationDivision):
            self.sr.itemsScroll.Load(contentList=[], headers=[], noContentHint=mls.UI_GENERIC_NOITEMSFOUND)
            self.sr.itemsScroll.sr.fixedColumns = {mls.UI_GENERIC_TYPE: 180,
             mls.UI_GENERIC_QTY: 70,
             mls.UI_GENERIC_NAME: 160}
            self.sr.itemsScroll.ShowHint(mls.UI_CONTRACTS_GETTINGITEMS)
            items = sm.GetService('contracts').GetItemsInStation(self.data.startStation, forCorp)
            self.sr.itemsScroll.hiliteSorted = 0
            scrolllist = []
            for item in items:
                if forCorp and self.data.startStationDivision != item.flagID:
                    continue
                data = uix.GetItemData(item, 'list', viewOnly=1)
                ty = cfg.invtypes.Get(item.typeID)
                volume = self.GetItemVolumeMaybe(item)
                if item.typeID == const.typePlasticWrap:
                    volume = mls.UI_GENERIC_UNKNOWN
                itemName = ''
                isContainer = item.groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer) and item.singleton
                if item.categoryID == const.categoryShip or isContainer:
                    shipName = cfg.evelocations.GetIfExists(item.itemID)
                    if shipName is not None:
                        itemName = shipName.locationName
                details = itemName
                label = '%s<t>%s<t>%s<t>%s' % (ty.typeName,
                 item.stacksize,
                 volume,
                 details)
                scrolllist.append(listentry.Get('ContractItemSelect', {'info': item,
                 'stationID': self.data.startStation,
                 'forCorp': forCorp,
                 'flag': item.flagID,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'isCopy': item.categoryID == const.categoryBlueprint and item.singleton == const.singletonBlueprintCopy,
                 'label': label,
                 'quantity': item.stacksize,
                 'getIcon': 1,
                 'item': item,
                 'checked': item.itemID in self.data.items,
                 'cfgname': item.itemID,
                 'retval': (item,
                            item.itemID,
                            item.typeID,
                            item.stacksize),
                 'OnChange': self.OnItemSelectedChanged}))

            if self.sr.itemsScroll is not None:
                if scrolllist:
                    self.sr.itemsScroll.ShowHint()
                self.sr.itemsScroll.sr.id = 'itemsScroll'
                self.sr.itemsScroll.sr.lastSelected = None
                self.sr.itemsScroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_TYPE,
                 mls.UI_GENERIC_QTY,
                 mls.UI_GENERIC_VOLUME,
                 mls.UI_GENERIC_DETAILS])



    def OnItemSelectedChanged(self, checkbox, *args):
        (item, itemID, typeID, qty,) = checkbox.data['retval']
        gv = True
        try:
            gv = checkbox.GetValue()
        except:
            pass
        if gv:
            self.data.items[itemID] = [typeID, qty, item]
        elif itemID in self.data.items:
            del self.data.items[itemID]
        self.UpdateNumberOfItems()



    def GetItemVolumeMaybe(self, item, qty = None):
        volume = 0
        if item.typeID != const.typePlasticWrap:
            volume = cfg.GetItemVolume(item, qty)
        return volume



    def UpdateNumberOfItems(self):
        totalVolume = 0
        num = 0
        for (itemID, item,) in self.data.items.iteritems():
            totalVolume += self.GetItemVolumeMaybe(item[2])
            num += 1

        if num > MAX_NUM_ITEMS:
            num = '<color=red>%s</color>' % num
        self.sr.volumeText.text = mls.UI_CONTRACTS_NUMBEROFSELECTED % {'num': num,
         'vol': util.FmtAmt(totalVolume)}



    def CalcBasePrice(self):
        price = 0
        for item in self.data.items.itervalues():
            ty = cfg.invtypes.Get(item[0])
            price += int(float(ty.basePrice) / ty.portionSize * item[1])

        if price > 1000000:
            price = int(price / 100000) * 100000
        if price == 0:
            raise UserError('ConNoBasePrice')
        return price



    def CalcBasePriceCollateral(self, *args):
        price = self.CalcBasePrice()
        if eve.Message('ConBasePrice', {'price': util.FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.collateral.SetValue(price)



    def CalcBasePricePrice(self, *args):
        price = self.CalcBasePrice()
        if eve.Message('ConBasePrice', {'price': util.FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.price.SetValue(price)



    def OnItemSplit(self, itemID, amountRemoved):
        if itemID in self.data.items:
            self.data.items[itemID][1] -= amountRemoved
            if self.data.items[itemID][1] <= 0:
                del self.data.items[itemID]




class ContractDraggableIcon(uicls.Container):
    __guid__ = 'xtriui.ContractDraggableIcon'

    def Startup(self, icon, contract, contractTitle):
        self.contract = contract
        self.contractTitle = contractTitle



    def GetDragData(self, *args):
        entry = util.KeyVal()
        entry.solarSystemID = self.contract.startSolarSystemID
        entry.contractID = self.contract.contractID
        entry.name = self.contractTitle
        entry.__guid__ = 'listentry.ContractEntry'
        return [entry]




class ContractDetailsWindow(uicls.Window):
    __guid__ = 'form.ContractDetailsWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        contractID = attributes.contractID
        self.contract = None
        self.buttons = []
        self.isContractMgr = False
        self.contractID = contractID
        self.sr.main = uiutil.GetChild(self, 'main')
        self.scope = 'all'
        self.SetCaption(mls.UI_CONTRACTS_CONTRACT % {'name': '-'})
        self.LoadTabs()
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-5)
        self.SetMinSize([500, 200])
        self.MakeUnstackable()
        self.MakeUncollapseable()
        self.history = settings.user.ui.Get('contracts_history', [])
        self.state = uiconst.UI_HIDDEN
        self.Init()



    def Init(self):

        def AddBasicInfoRow(key, val):
            return '<b>%(key)s</b><t>%(val)s<br>' % {'key': key,
             'val': val}


        self.sr.main.Flush()
        self.buttons = []
        contract = sm.GetService('contracts').GetContract(self.contractID, force=True)
        if not contract:
            self.HistoryRemove(self.contractID)
            self.SelfDestruct()
            raise UserError('ConContractNotFound')
        self.contract = contract
        c = contract.contract
        self.contractID = c.contractID
        self.isContractMgr = isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
        isAssignedToMe = c.assigneeID == eve.session.charid or c.assigneeID == eve.session.corpid and isContractMgr
        isAssignedToMePersonally = c.assigneeID == eve.session.charid
        isAcceptedByMe = c.acceptorID == eve.session.charid or c.acceptorID == eve.session.corpid and isContractMgr
        isAcceptedByMyCorp = c.acceptorID == eve.session.corpid
        isIssuedByMe = c.issuerID == eve.session.charid or c.issuerCorpID == eve.session.corpid and c.forCorp and isContractMgr
        isIssuedByMePersonally = c.issuerID == eve.session.charid
        isCorpContract = c.forCorp
        isExpired = c.dateExpired < blue.os.GetTime()
        isOverdue = c.dateAccepted + DAY * c.numDays < blue.os.GetTime()
        title = GetContractTitle(c, contract.items)
        title += ' (%s)' % GetContractTypeText(c.type)
        ic = GetContractIcon(c.type)
        self.SetWndIcon(ic, mainTop=-5)
        icon = xtriui.ContractDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=self, height=64, width=64, left=0, top=11)
        icon.Startup(ic, c, title)
        icon.state = uiconst.UI_NORMAL
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=6)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=6)
        titleParent = uicls.Container(name='titleparent', parent=self.sr.topParent, align=uiconst.TOPLEFT, top=18, left=70, width=150)
        l = uicls.Label(text=title, parent=titleParent, width=400, autowidth=False, letterspace=1, fontsize=14, state=uiconst.UI_DISABLED, uppercase=0)
        titleParent.height = l.textheight
        self.HistoryAdd(self.contractID, c.startSolarSystemID, title)
        text = ''
        desc = c.title
        if desc == '':
            desc = mls.UI_CONTRACTS_NONE
        text += AddBasicInfoRow(mls.UI_CONTRACTS_INFOBYISSUER, '<color=0xff999999>%s</color>' % desc)
        text += AddBasicInfoRow(mls.UI_GENERIC_TYPE, GetContractTypeText(c.type))
        issuerID = {False: c.issuerID,
         True: c.issuerCorpID}[c.forCorp]
        try:
            issuer = cfg.eveowners.Get(issuerID)
            issuerTypeID = issuer.typeID
            issuerName = issuer.ownerName
        except:
            issuerTypeID = cfg.eveowners.Get(session.charid).typeID
            issuerName = mls.UNKNOWN
            log.LogException()
        more = ''
        if isIssuedByMe and isCorpContract:
            more = ' (%s: %s)' % (mls.UI_CORP_WALLETDIVISION, sm.GetService('corp').GetCorpAccountName(c.issuerWalletKey))
        text += AddBasicInfoRow(mls.UI_CONTRACTS_ISSUEDBY, '<url:showinfo:%(issuedByTypeID)s//%(issuedByID)s>%(issuedByName)s</url>%(more)s' % {'issuedByTypeID': issuerTypeID,
         'issuedByID': issuerID,
         'issuedByName': issuerName,
         'more': more})
        isPrivate = not not c.availability
        a = mls.UI_CONTRACTS_PUBLIC
        if isPrivate:
            a = mls.UI_CONTRACTS_PRIVATE
        if isPrivate:
            assignee = cfg.eveowners.Get(c.assigneeID)
            a += ' (<url:showinfo:%s//%s>%s</url>)' % (assignee.typeID, c.assigneeID, assignee.name)
        else:
            reg = [mls.UI_CONTRACTS_OTHERREGION, mls.UI_CONTRACTS_CURRENTREGION][(c.startRegionID == session.regionid)]
            a += ' - %s: <b>%s</b> (%s)' % (mls.UI_GENERIC_REGION, cfg.evelocations.Get(c.startRegionID).name, reg)
        text += AddBasicInfoRow(mls.UI_CONTRACTS_AVAILABILITY, a)
        if c.acceptorID > 0 and (c.status != const.conStatusInProgress or c.issuerID == eve.session.charid or c.issuerCorpID == eve.session.corpid and c.forCorp or c.acceptorID == eve.session.charid or c.acceptorID == eve.session.corpid):
            acceptor = cfg.eveowners.Get(c.acceptorID)
            more = ''
            if c.acceptorID == eve.session.corpid and isContractMgr:
                more = ' (%s: %s)' % (mls.UI_CORP_WALLETDIVISION, sm.GetService('corp').GetCorpAccountName(c.acceptorWalletKey))
            text += AddBasicInfoRow(mls.UI_CONTRACTS_CONTRACTOR, '<url:showinfo:%(acceptorTypeID)s//%(acceptorID)s>%(acceptorName)s</url>%(more)s' % {'acceptorTypeID': acceptor.typeID,
             'acceptorID': c.acceptorID,
             'acceptorName': acceptor.ownerName,
             'more': more})
        st = GetContractStatusText(c.status, c.type)
        if c.status == const.conStatusFailed:
            st = '<b><color=red>%s</color></b>' % st
        text += '<b>%(statusKey)s</b><t>%(status)s<br>' % {'statusKey': mls.UI_CONTRACTS_STATUS,
         'status': st}
        if c.startStationID == 0:
            loc = mls.UI_CONTRACTS_NONE
        else:
            owner = cfg.evelocations.Get(c.startStationID)
            startStationTypeID = sm.GetService('ui').GetStation(c.startStationID).stationTypeID
            startStationIsPlayerOwnable = sm.GetService('godma').GetType(startStationTypeID).isPlayerOwnable
            dot = sm.GetService('contracts').GetSystemSecurityDot(c.startSolarSystemID)
            loc = '%s <url:showinfo:%s//%s>%s</url>' % (dot,
             startStationTypeID,
             c.startStationID,
             owner.name)
            if c.startStationID == eve.session.stationid:
                loc += '<br><t>%s' % mls.UI_GENERIC_CURRENTSTATION
            elif c.startSolarSystemID == eve.session.solarsystemid:
                loc += '<br><t>%s' % mls.UI_GENERIC_CURRENTSYSTEM
            elif startStationIsPlayerOwnable:
                loc += '<br><t><color=0xffbb0000>%s</color>' % mls.UI_CONTRACTS_MIGHTBEINACCESSIBLE
            n = sm.GetService('pathfinder').GetJumpCountFromCurrent(c.startSolarSystemID)
            securityClass = sm.GetService('map').GetSecurityClass(c.startSolarSystemID)
            mr = sm.GetService('contracts').GetRouteSecurityWarning(session.solarsystemid2, c.startSolarSystemID)
            if mr:
                mr = '<br><t>%s' % mr
            loc += '<br><t>%s - <url:showrouteto:%s>%s</url>%s' % (mls.UI_CONTRACTS_JUMPSAWAY % {'jumps': int(n)},
             c.startSolarSystemID,
             mls.UI_CONTRACTS_SHOWROUTE,
             mr)
        text += AddBasicInfoRow(mls.UI_CONTRACTS_LOCATION, loc)
        if c.type != const.conTypeAuction or c.status != const.conStatusOutstanding or session.charid == c.issuerID:
            text += AddBasicInfoRow(mls.UI_CONTRACTS_DATEISSUED, util.FmtDate(c.dateIssued, 'ss'))
        if c.status == const.conStatusInProgress:
            cb = c.dateAccepted + DAY * c.numDays
            if cb < blue.os.GetTime() + HOUR:
                if cb - blue.os.GetTime() < 0:
                    timeleft = mls.UI_CONTRACTS_OVERDUE
                else:
                    timeleft = mls.UI_CONTRACTS_TIMELEFT_VALUE % {'time': util.FmtDate(cb - blue.os.GetTime(), 'ls')}
                cb = '<color=red>%s (%s)</color>' % (util.FmtDate(cb, 'ls'), timeleft)
            else:
                cb = util.FmtDate(cb, 'ls')
            text += AddBasicInfoRow(mls.UI_CONTRACTS_COMPLETEBEFORE, cb)
        elif c.status != const.conStatusOutstanding:
            text += AddBasicInfoRow(mls.UI_CONTRACTS_DATECOMPLETED, util.FmtDate(c.dateCompleted, 'ls'))
        elif c.type != const.conTypeAuction:
            text += AddBasicInfoRow(mls.UI_CONTRACTS_DATEEXPIRED, '%s (%s)' % (util.FmtDate(c.dateExpired, 'ls'), ConFmtDate(c.dateExpired - blue.os.GetTime(), False)))
        tabs = [105, 480]
        basicInfoParent = uicls.Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, padRight=const.defaultPadding)
        basicInfo = uicls.Label(text=text, parent=basicInfoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
        basicInfoParent.height = basicInfo.textheight + 5
        uicls.Line(parent=basicInfoParent, align=uiconst.TOTOP)
        isResizable = False
        if c.status == const.conStatusInProgress:
            if isAcceptedByMe:
                if c.type != 4:
                    self.AddButton(BComplete)
                self.AddButton(BFail)
            elif isIssuedByMe and isOverdue:
                self.AddButton(BFail)
            elif isAcceptedByMyCorp and c.type == const.conTypeCourier:
                self.AddButton(BComplete)
        if c.type == const.conTypeAuction:
            text = ''
            text += AddBasicInfoRow(mls.UI_CONTRACTS_STARTINGBID, FmtISKWithDescription(c.price))
            bo = [mls.UI_CONTRACTS_NONE, FmtISKWithDescription(c.collateral)][(c.collateral > 0)]
            text += AddBasicInfoRow(mls.UI_CONTRACTS_BUYOUTPRICE, bo)
            b = mls.UI_CONTRACTS_NOBIDS
            if len(contract.bids) > 0:
                b = '<b>%s</b> (%s %s)' % (FmtISKWithDescription(contract.bids[0].amount), len(contract.bids), mls.UI_CONTRACTS_BIDSSOFAR)
            text += AddBasicInfoRow(mls.UI_CONTRACTS_CURRENTBID, b)
            timeleft = '%s' % mls.UI_CONTRACTS_FINISHED
            if c.status == const.conStatusOutstanding:
                diff = c.dateExpired - blue.os.GetTime()
                if c.dateExpired - blue.os.GetTime() > 0:
                    timeleft = ConFmtDate(diff, True)
            text += AddBasicInfoRow(mls.UI_CONTRACTS_TIMELEFT, timeleft)
            isExpired = c.dateExpired < blue.os.GetTime()
            highBidder = None
            if len(contract.bids) > 0:
                highBidder = contract.bids[0].bidderID
            if eve.session.charid == highBidder:
                text += AddBasicInfoRow('', '<color=' + COL_GET + '><b>' + [mls.UI_CONTRACTS_YOUARETHEHIGHESTBIDDER, mls.UI_CONTRACTS_YOUWON][isExpired] + '</b></color>')
            elif eve.session.corpid == highBidder:
                text += AddBasicInfoRow('', '<color=' + COL_GET + '><b>' + [mls.UI_CONTRACTS_YOURCORPISTHEHIGHESTBIDDER, mls.UI_CONTRACTS_YOURCORPWON][isExpired] + '</b></color>')
            else:
                for i in range(len(contract.bids)):
                    b = contract.bids[i]
                    if i != 0:
                        if b.bidderID == eve.session.charid:
                            text += AddBasicInfoRow('', '<color=' + COL_PAY + '><b>' + [mls.UI_CONTRACTS_YOUHAVEBEENOUTBID, mls.UI_CONTRACTS_YOULOST][isExpired] + '</b></color>')
                        elif b.bidderID == eve.session.corpid:
                            text += AddBasicInfoRow('', '<color=' + COL_PAY + '><b>' + [mls.UI_CONTRACTS_YOURCORPHASBEENOUTBID, mls.UI_CONTRACTS_YOURCORPLOST][isExpired] + '</b></color>')
                        break

                if isExpired and len(contract.bids) > 0:
                    winner = cfg.eveowners.Get(contract.bids[0].bidderID)
                    text += AddBasicInfoRow('', '<url:showinfo:%(acceptorTypeID)s//%(acceptorID)s>%(acceptorName)s</url> %(won)s' % {'acceptorTypeID': winner.typeID,
                     'acceptorID': winner.ownerID,
                     'acceptorName': winner.ownerName,
                     'won': mls.UI_CONTRACTS_WONTHISAUCTION})
            infoParent = uicls.Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = uicls.Label(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
            infoParent.height = info.textheight
            uicls.Line(parent=infoParent, align=uiconst.TOTOP)
            uicls.Line(parent=infoParent, align=uiconst.TOBOTTOM)
            isResizable = self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_GET, [mls.UI_CONTRACTS_YOUWILLGET, mls.UI_CONTRACTS_BUYERWILLGET][(session.charid == c.issuerID)]), True, 3)
            if len(contract.bids) > 0 and isExpired:
                if c.status != const.conStatusFinishedIssuer and c.status != const.conStatusFinished and isIssuedByMe:
                    self.AddButton(BGetMoney)
                if c.status != const.conStatusFinishedContractor and c.status != const.conStatusFinished and (contract.bids[0].bidderID == eve.session.charid or contract.bids[0].bidderID == eve.session.corpid and isContractMgr):
                    self.AddButton(BGetItems)
            if isIssuedByMe:
                if (c.status == const.conStatusOutstanding or c.status == const.conStatusRejected) and len(contract.bids) == 0:
                    self.AddButton(BDelete)
            if not isIssuedByMePersonally and c.status == const.conStatusOutstanding:
                if not isExpired:
                    self.AddButton(BPlaceBid)
                    if isAssignedToMe and not highBidder:
                        self.AddButton(BReject)
        elif c.type == const.conTypeItemExchange:
            text = ''
            if c.price > 0:
                text += AddBasicInfoRow([mls.UI_CONTRACTS_YOUWILLPAY, mls.UI_CONTRACTS_BUYERWILLPAY][(session.charid == c.issuerID)], '<color=%s><b>%s</b></color>' % (COL_PAY, FmtISKWithDescription(c.price)))
            if c.reward > 0 or c.price == 0:
                text += AddBasicInfoRow([mls.UI_CONTRACTS_YOUWILLGET, mls.UI_CONTRACTS_BUYERWILLGET][(session.charid == c.issuerID)], '<color=%s><b>%s</b></color>' % (COL_GET, FmtISKWithDescription(c.reward)))
            infoParent = uicls.Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = uicls.Label(text=text, parent=infoParent, top=const.defaultPadding + 3, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, fontsize=14)
            infoParent.height = info.textheight
            uicls.Line(parent=infoParent, align=uiconst.TOTOP)
            uicls.Line(parent=infoParent, align=uiconst.TOBOTTOM)
            fixedSize = False
            for i in contract.items:
                if not i.inCrate:
                    fixedSize = True

            isResizable = self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_GET, [mls.UI_CONTRACTS_YOUWILLGET, mls.UI_CONTRACTS_BUYERWILLGET][(session.charid == c.issuerID)]), True, 2, fixedSize=fixedSize)
            if self.InsertItemList(contract, '<color=%s>%s</color>' % (COL_PAY, [mls.UI_CONTRACTS_YOUWILLPAY, mls.UI_CONTRACTS_BUYERWILLPAY][(session.charid == c.issuerID)]), False, 2, hint=mls.UI_CONTRACTS_NOREQUIREDITEMS, forceList=True):
                isResizable = True
            if isIssuedByMe:
                if c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusOutstanding and (not isIssuedByMePersonally or isAssignedToMePersonally):
                if not isExpired:
                    self.AddButton(BAccept)
                    if isContractMgr:
                        self.AddButton(BAcceptForCorp)
                    if isAssignedToMe:
                        self.AddButton(BReject)
        elif c.type == const.conTypeCourier:
            timeleft = '<font color=' + COL_GET + '>%s</font>' % mls.UI_CONTRACTS_FINISHED
            text = ''
            if c.status == const.conStatusInProgress:
                timeleft = '<font color=' + COL_PAY + '>%s</font>' % mls.UI_CONTRACTS_EXPIRED
                de = c.dateExpired
                if c.status == const.conStatusInProgress:
                    de = c.dateAccepted + DAY * c.numDays
                    timeleft = mls.UI_CONTRACTS_OVERDUE_AGO % util.FmtDate(-(de - blue.os.GetTime()), 'ss')
                diff = de - blue.os.GetTime()
                if diff > 0:
                    timeleft = '%s (%s)' % (ConFmtDate(diff, False), util.FmtDate(de, 'ss'))
                text += AddBasicInfoRow(mls.UI_CONTRACTS_TIMELEFT, timeleft)
            elif c.status == const.conStatusOutstanding:
                text += AddBasicInfoRow(mls.UI_CONTRACTS_COMPLETEIN, '%s %s' % (c.numDays, [mls.GENERIC_DAY, mls.GENERIC_DAYS_LOWER][(c.numDays != 1)]))
            text += AddBasicInfoRow(mls.UI_CONTRACTS_VOLUME, '%s %s' % (util.FmtAmt(c.volume, showFraction=3), mls.UI_CONTRACTS_CUBEMETRES))
            numJumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(c.endSolarSystemID, c.startSolarSystemID)
            perjump = ''
            if numJumps:
                perjump = int(c.reward / numJumps)
                perjump = ' (%s / %s)' % (FmtISKWithDescription(perjump, justDesc=True), mls.UI_GENERIC_JUMP)
            text += AddBasicInfoRow(mls.UI_CONTRACTS_REWARD, {False: mls.UI_CONTRACTS_NONE,
             True: '<color=%s><b>%s</b></color>%s' % (COL_GET, FmtISKWithDescription(c.reward), perjump)}[(c.reward > 0)])
            text += AddBasicInfoRow(mls.UI_CONTRACTS_COLLATERAL, {False: mls.UI_CONTRACTS_NONE,
             True: '<color=%s><b>%s</b></color>' % (COL_PAY, FmtISKWithDescription(c.collateral))}[(c.collateral > 0)])
            owner = cfg.evelocations.Get(c.endStationID)
            mr = sm.GetService('contracts').GetRouteSecurityWarning(c.startSolarSystemID, c.endSolarSystemID)
            securityClass = sm.GetService('map').GetSecurityClass(c.endSolarSystemID)
            if mr:
                mr = '<t>%s' % mr
            dot = sm.GetService('contracts').GetSystemSecurityDot(c.endSolarSystemID)
            endStationTypeID = sm.GetService('ui').GetStation(c.endStationID).stationTypeID
            loc = '%s <url:showinfo:%s//%s>%s</url>' % (dot,
             endStationTypeID,
             c.endStationID,
             owner.name)
            endStation = sm.RemoteSvc('stationSvc').GetStation(c.endStationID)
            endStationIsPlayerOwnable = sm.GetService('godma').GetType(endStation.stationTypeID).isPlayerOwnable
            if endStationIsPlayerOwnable:
                loc += '<br><t><color=0xffbb0000>%s</color>' % mls.UI_CONTRACTS_MIGHTBEINACCESSIBLE
            loc += '<br><t><b>%d</b> %s - <url:showrouteto:%s>%s</url><br>' % (sm.GetService('pathfinder').GetJumpCountFromCurrent(c.endSolarSystemID),
             mls.UI_CONTRACTS_JUMPSFROMCURRENT,
             c.endSolarSystemID,
             mls.UI_CONTRACTS_SHOWROUTE)
            if c.startSolarSystemID != session.solarsystemid2:
                loc += '<t><b>%d</b> %s - <url:showrouteto:%s::%s>%s</url>' % (numJumps,
                 mls.UI_CONTRACTS_JUMPSFROMSTART,
                 c.endSolarSystemID,
                 c.startSolarSystemID,
                 mls.UI_CONTRACTS_SHOWROUTE)
            if mr:
                loc += '<br>%s' % mr
            text += AddBasicInfoRow(mls.UI_CONTRACTS_DESTINATION, loc)
            infoParent = uicls.Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = uicls.Label(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
            infoParent.height = info.textheight
            uicls.Line(parent=infoParent, align=uiconst.TOTOP)
            if isIssuedByMe:
                if c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusOutstanding and (not isIssuedByMePersonally or isAssignedToMePersonally):
                if not isExpired:
                    self.AddButton(BAccept)
                    if isContractMgr:
                        self.AddButton(BAcceptForCorp)
                    if isAssignedToMe:
                        self.AddButton(BReject)
        elif c.type == const.conTypeLoan:
            text = ''
            if c.status == const.conStatusInProgress:
                timeleft = '<font color=red>%s</font>' % mls.UI_CONTRACTS_EXPIRED
                de = c.dateExpired
                if c.status == const.conStatusInProgress:
                    de = c.dateAccepted + DAY * c.numDays
                    timeleft = mls.UI_CONTRACTS_OVERDUE_AGO % util.FmtDate(-(de - blue.os.GetTime()), 'ss')
                diff = de - blue.os.GetTime()
                if diff > 0:
                    timeleft = '%s (%s)' % (ConFmtDate(diff, False), util.FmtDate(de, 'ss'))
                text += AddBasicInfoRow(mls.UI_CONTRACTS_TIMELEFT, timeleft)
            elif c.status == const.conStatusOutstanding or c.status == const.conStatusRejected:
                self.AddButton(BDelete)
            text += AddBasicInfoRow(mls.UI_CONTRACTS_PRICE, {False: mls.UI_CONTRACTS_NONE,
             True: '<color=%s><b>%s</b></color>' % (COL_PAY, FmtISKWithDescription(c.price))}[(c.price > 0)])
            text += AddBasicInfoRow(mls.UI_CONTRACTS_COLLATERAL, {False: mls.UI_CONTRACTS_NONE,
             True: '<color=%s><b>%s</b></color>' % (COL_PAY, FmtISKWithDescription(c.collateral))}[(c.collateral > 0)])
            if c.reward > 0:
                text += AddBasicInfoRow(mls.UI_CONTRACTS_MONEYBORROWED, '<color=%s>%s</color>' % (COL_GET, FmtISKWithDescription(c.reward)))
            infoParent = uicls.Container(name='infocontainer', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            info = uicls.Label(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
            infoParent.height = info.textheight
            uicls.Line(parent=infoParent, align=uiconst.TOTOP)
            uicls.Line(parent=infoParent, align=uiconst.TOBOTTOM)
            isResizable = self.InsertItemList(contract, mls.UI_CONTRACTS_BORROWEDITEMS, True, 3, fixedSize=True)
            if isIssuedByMe:
                if c.status == const.conStatusRejected:
                    self.AddButton(BDelete)
            if c.status == const.conStatusInProgress:
                nocollateral = ''
                if not c.collateral:
                    isk = c.reward or 0
                    nocollateral = "Since this contract doesn't have any collateral and operates completely on trust it should be straightforward for the contract acceptor to create an Item Exchange contract to transfer the lent items and/or cash back to the issuer. You should transfer a total of <b>%s</b> plus any items found in this contract back to the issuer." % util.FmtISK(isk)
                else:
                    nocollateral = '<b>Note that you have put collateral into escrow on this contract.</b> Your best course of action is to contact Customer Support to get your collateral back.'
                html = "<font color=0xffff4444><h4>This contract type is no longer supported!</h4></font>\n                You will not be able to complete this loan contract because it is no longer supported in the system.<Br>It is recommended that you click the 'Fail' button below and repay the contract manually.<br><br>%s<br><br>\n                We apologize for the inconvenience this causes. If you need further assistance please file a petition and the customer support staff will be able to help you.\n                " % nocollateral
                descParent = uicls.Container(name='desc', parent=self.sr.main, align=uiconst.TOTOP, left=const.defaultPadding, top=const.defaultPadding, height=180)
                desc = uicls.Edit(parent=descParent, readonly=1, hideBackground=1)
                desc.SetValue('<html><body>%s</body></html>' % html)
        else:
            raise RuntimeError('Invalid contract type!')
        self.AddButton(BCancel)
        childrenList = self.sr.main.children
        height = sum([ x.height for x in childrenList if x.state != uiconst.UI_HIDDEN if x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ]) + 110
        (w, h,) = self.minsize
        add = {False: 0,
         True: 160}[isResizable]
        self.SetMinSize([w, height + add])
        self.buttonWnd = uicls.ButtonGroup(btns=self.buttons, parent=self.sr.main, unisize=0, idx=0)
        self.state = uiconst.UI_NORMAL
        self.sr.captionpush = uicls.Container(name='captionpush', parent=self.sr.main, align=uiconst.TOBOTTOM, height=12, left=0, top=-16)
        historyicon = uicls.MenuIcon(size=24, ignoreSize=True, align=uiconst.CENTERLEFT)
        historyicon.GetMenu = lambda : self.GetHistoryMenu()
        historyicon.hint = mls.UI_GENERIC_HISTORY
        self.sr.captionpush = uicls.Container(name='captionpush', parent=self.sr.main, align=uiconst.TOBOTTOM, height=12, left=0, top=-16)
        self.sr.captionpush.children.insert(1000, historyicon)
        return self



    def GetHistoryMenu(self):
        m = []
        if self.contract.contract.issuerID == session.charid:
            m.append((mls.UI_CONTRACTS_COPYCONTRACT, sm.GetService('contracts').OpenCreateContract, (None, self.contract)))
        typeID = None
        if self.contract.items and len(self.contract.items) == 1:
            typeID = self.contract.items[0].itemTypeID
        m += [(mls.UI_CONTRACTS_FINDRELATED, ('isDynamic', sm.GetService('contracts').GetRelatedMenu, (self.contract.contract, typeID)))]
        m += [None]
        for i in range(len(self.history)):
            h = self.history[(-(i + 1))]
            m.append((h.title, self.SelectHistory, (h.contractID, h.solarSystemID)))

        return m



    def SelectHistory(self, contractID, solarSystemID):
        sm.GetService('contracts').ShowContract(contractID)



    def AddButton(self, which):
        caption = function = None
        if which == BCancel:
            caption = mls.UI_GENERIC_CLOSE
            function = self.Cancel
        elif which == BAccept:
            caption = mls.UI_CONTRACTS_ACCEPT
            function = self.Accept
        elif which == BAcceptForCorp:
            caption = mls.UI_CONTRACTS_ACCEPT_FORCORP
            function = self.AcceptForCorp
        elif which == BReject:
            caption = mls.UI_CONTRACTS_REJECT
            function = self.Reject
        elif which == BComplete:
            caption = mls.UI_CONTRACTS_COMPLETE
            function = self.Complete
        elif which == BDelete:
            caption = mls.UI_CONTRACTS_DELETE
            function = self.Delete
        elif which == BSucceed:
            caption = mls.UI_CONTRACTS_SUCCEED
            function = self.Succeed
        elif which == BFail:
            caption = mls.UI_CONTRACTS_FAIL
            function = self.Fail
        elif which == BGetItems:
            caption = mls.UI_CONTRACTS_GETITEMS
            function = self.GetItems
        elif which == BGetMoney:
            caption = mls.UI_CONTRACTS_GETMONEY
            function = self.GetMoney
        elif which == BPlaceBid:
            caption = mls.UI_CONTRACTS_PLACEBID
            function = self.PlaceBid
        button = (caption,
         function,
         (),
         84)
        self.buttons.append(button)



    def Cancel(self):
        self.SelfDestruct()



    def TryHideLoad(self):
        try:
            self.HideLoad()
        except:
            pass



    def Accept(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').AcceptContract(self.contractID, False):
                if not self or self.destroyed:
                    return 
                self.Init()

        finally:
            self.TryHideLoad()




    def AcceptForCorp(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').AcceptContract(self.contractID, True):
                self.Init()

        finally:
            self.TryHideLoad()




    def Reject(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').RejectContract(self.contractID):
                self.Init()

        finally:
            self.TryHideLoad()




    def Complete(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').CompleteContract(self.contractID):
                self.Init()

        finally:
            self.TryHideLoad()




    def Delete(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').DeleteContract(self.contractID):
                self.SelfDestruct()

        finally:
            try:
                self.TryHideLoad()
            except:
                pass




    def Succeed(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').CompleteContract(self.contractID):
                self.Init()

        finally:
            self.TryHideLoad()




    def Fail(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').FailContract(self.contractID):
                self.Init()

        finally:
            self.TryHideLoad()




    def GetItems(self):
        try:
            self.ShowLoad()
            sm.GetService('contracts').FinishAuction(self.contractID, False)
            self.Init()

        finally:
            self.TryHideLoad()




    def GetMoney(self):
        try:
            self.ShowLoad()
            sm.GetService('contracts').FinishAuction(self.contractID, True)
            self.Init()

        finally:
            self.TryHideLoad()




    def PlaceBid(self):
        try:
            self.ShowLoad()
            if sm.GetService('contracts').PlaceBid(self.contractID):
                if not self.destroyed:
                    self.Init()

        finally:
            self.TryHideLoad()




    def InsertItemList(self, contract, title, inCrate, numRows, hint = None, fixedSize = False, forceList = False):
        shouldHideBlueprintInfo = contract.contract.status in [const.conStatusFinished, const.conStatusFinishedContractor]
        items = [ e for e in contract.items if e.inCrate == inCrate ]
        if len(items) == 0:
            if len(contract.items) > 1:
                return True
            else:
                return False
        else:
            titleParent = uicls.Container(name='title', parent=self.sr.main, align=uiconst.TOTOP, width=const.defaultPadding)
            title = uicls.Label(text='<b>%s</b>' % title, parent=titleParent, top=6, idx=0, fontsize=14, state=uiconst.UI_NORMAL, left=6)
            titleParent.height = title.textheight + 6
            if len(items) == 1 and not forceList:
                item = items[0]
                typeID = item.itemTypeID
                itemID = item.itemID
                type = cfg.invtypes.Get(item.itemTypeID)
                typeName = type.typeName
                group = cfg.invgroups.Get(type.groupID)
                groupName = group.groupName
                categoryName = CategoryName(group.categoryID)
                q = ' x %s' % util.FmtAmt(max(1, item.quantity))
                details = ''
                iid = ''
                if item.itemID > 0:
                    iid = '//%s' % item.itemID
                if group.categoryID == const.categoryBlueprint:
                    if item.copy == 1:
                        if shouldHideBlueprintInfo:
                            details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTCOPYSIMPLE
                        else:
                            details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTCOPY % {'runs': item.licensedProductionRunsRemaining or 0,
                             'ME': item.materialLevel or 0,
                             'PE': item.productivityLevel or 0}
                    elif shouldHideBlueprintInfo:
                        details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTORIGINALSIMPLE
                    else:
                        details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTORIGINAL % {'ME': item.materialLevel or 0,
                         'PE': item.productivityLevel or 0}
                descParent = uicls.Container(name='desc', parent=self.sr.main, align=uiconst.TOTOP, left=const.defaultPadding, top=const.defaultPadding, height=100)
                leftParent = picParent = uicls.Container(name='leftParent', parent=descParent, align=uiconst.TOLEFT, width=72)
                picParent = uicls.Container(name='picParent', parent=leftParent, align=uiconst.TOPRIGHT, width=64, height=64, state=uiconst.UI_NORMAL)
                infoParent = uicls.Container(name='infoParent', parent=descParent, align=uiconst.TOALL, padding=(8,
                 2,
                 const.defaultPadding,
                 0))
                if getattr(item, 'copy', False):
                    isCopy = True
                else:
                    isCopy = False
                icon = uicls.DraggableIcon(parent=picParent, typeID=typeID, isCopy=isCopy, state=uiconst.UI_DISABLED)
                techSprite = uix.GetTechLevelIcon(None, 0, typeID)
                c = uicls.Container(name='techIcon', align=uiconst.TOPLEFT, parent=icon, width=16, height=16, idx=0)
                c.children.append(techSprite)
                if util.IsPreviewable(typeID):
                    setattr(picParent, 'typeID', typeID)
                    picParent.cursor = uiconst.UICURSOR_MAGNIFIER
                    picParent.OnClick = (self.OnPreviewClick, picParent)
                captionText = '%s%s' % (typeName, q)
                self.caption = uicls.CaptionLabel(parent=infoParent, text=captionText, uppercase=False, letterspace=0, padRight=16)
                self.infolink = uicls.InfoIcon(itemID=itemID, typeID=typeID, size=16, left=0, top=const.defaultPadding, parent=infoParent, idx=0)
                self.infolink.left = self.caption.textwidth + 8
                categoryAndGroupText = '%s / %s' % (categoryName, groupName)
                self.categoryAndGroup = uicls.Label(parent=infoParent, top=self.caption.textheight, text=categoryAndGroupText)
                if self.GetItemDamageText(item):
                    damageAndTextilsText = '<color=red>%s</color> %s' % (self.GetItemDamageText(item), details)
                else:
                    damageAndTextilsText = details
                self.damageAndTextils = uicls.Label(parent=infoParent, top=self.categoryAndGroup.textheight + self.categoryAndGroup.top, text=damageAndTextilsText)
                return False
            else:
                if fixedSize:
                    self.sr.scroll = uicls.Scroll(parent=self.sr.main, align=uiconst.TOTOP, padding=(const.defaultPadding,
                     const.defaultPadding,
                     const.defaultPadding,
                     const.defaultPadding), height=100)
                else:
                    self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
                     const.defaultPadding,
                     const.defaultPadding,
                     const.defaultPadding))
                self.sr.scroll.sr.id = 'contractDetailScroll'
                self.sr.data = {'items': []}
                parents = []
                children = []
                for item in items:
                    if not item.parentID:
                        parents.append(item)
                    else:
                        children.append(item)

                items = []
                for parent in parents:
                    items.append(parent)
                    for child in children:
                        if child.parentID == parent.itemID:
                            items.append(child)


                for child in children:
                    for item in items:
                        if child.itemID == item.itemID:
                            break
                    else:
                        items.append(child)


                scrolllist = []
                for item in items:
                    if item.inCrate != inCrate:
                        continue
                    type = cfg.invtypes.Get(item.itemTypeID)
                    typeName = type.typeName
                    group = cfg.invgroups.Get(type.groupID)
                    groupName = GroupName(type.groupID)
                    details = ''
                    if group.categoryID == const.categoryBlueprint:
                        if item.copy == 1:
                            details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTCOPY % {'runs': item.licensedProductionRunsRemaining or 0,
                             'ME': item.materialLevel or 0,
                             'PE': item.productivityLevel or 0}
                        else:
                            details = mls.UI_CONTRACTS_ITEMDETAILS_BLUEPRINTORIGINAL % {'ME': item.materialLevel or 0,
                             'PE': item.productivityLevel or 0}
                    chld = ''
                    if item.parentID > 0:
                        chld = ' '
                    mrdmg = self.GetItemDamageText(item)
                    if item.flagID and cfg.IsShipFittingFlag(item.flagID):
                        if cfg.IsShipFittingFlag(item.flagID):
                            details = mls.UI_GENERIC_FITTED
                    label = '%s%s<t>%s<t>%s<t>%s%s' % (chld,
                     typeName,
                     max(1, item.quantity) if item.quantity is not None else None,
                     groupName,
                     details,
                     mrdmg)
                    if forceList:
                        label = '%s%s<t>%s<t>%s' % (chld,
                         typeName,
                         max(1, item.quantity) if item.quantity is not None else None,
                         groupName)
                        hdr = [mls.UI_GENERIC_NAME, mls.UI_GENERIC_QTY, mls.UI_GENERIC_TYPE]
                    else:
                        label = '%s%s<t>%s<t>%s<t>%s%s' % (chld,
                         typeName,
                         max(1, item.quantity) if item.quantity is not None else None,
                         groupName,
                         details,
                         mrdmg)
                        hdr = [mls.UI_GENERIC_NAME,
                         mls.UI_GENERIC_QTY,
                         mls.UI_GENERIC_TYPE,
                         mls.UI_GENERIC_DETAILS]
                    itemTypeID = item.itemTypeID
                    scrolllist.append(listentry.Get('Item', {'itemID': item.itemID,
                     'typeID': itemTypeID,
                     'label': label}))

                self.sr.scroll.Load(None, scrolllist, headers=hdr)
                if len(scrolllist) >= 1:
                    hint = None
                elif hint is None:
                    hint = mls.UI_GENERIC_NOITEMSFOUND
                self.sr.scroll.ShowHint(hint)
                return not fixedSize



    def OnPreviewClick(self, wnd, *args):
        sm.GetService('preview').PreviewType(getattr(wnd, 'typeID'))



    def UpdateTexts(self):
        if hasattr(self, 'caption'):
            self.infolink.left = self.caption.textwidth + 8
            self.categoryAndGroup.top = self.caption.textheight
            self.damageAndTextils.top = self.categoryAndGroup.top + self.categoryAndGroup.textheight



    def _OnResize(self, *args):
        self.UpdateTexts()



    def GetItemDamageText(self, item):
        dmg = 0
        if item.damage:
            for attribute in cfg.dgmtypeattribs.get(item.itemTypeID, []):
                if attribute.attributeID == const.attributeHp and attribute.value:
                    dmg = item.damage / attribute.value
                    dmg = int(dmg * 100)
                    break

        txt = ''
        if dmg > 0:
            txt = ' <color=0xffff4444>%s</color>' % (mls.UI_CONTRACTS_PERCENTDAMAGED % {'dmg': dmg})
        return txt



    def GetContractItemSubContent(self, tmp, *args):
        scrolllist = []
        scrolllist.append(listentry.Get('Header', {'label': mls.UI_INFOWND_AVAILABLETOYOU}))
        entry = listentry.Get('Item', {'itemID': None,
         'typeID': each[2],
         'label': each[1],
         'getIcon': 1})
        return scrolllist



    def LoadTabs(self):
        pass



    def Load(self, key):
        pass



    def Confirm(self, *etc):
        pass



    def GetError(self, checkNumber = 1):
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})



    def HistoryAdd(self, id, solarSystemID, title):
        self.HistoryRemove(id)
        kv = util.KeyVal()
        kv.contractID = id
        kv.solarSystemID = solarSystemID
        kv.title = title
        self.history.append(kv)
        if len(self.history) > HISTORY_LENGTH:
            del self.history[0]
        settings.user.ui.Set('contracts_history', self.history)



    def HistoryRemove(self, id):
        for i in range(len(self.history)):
            if self.history[i].contractID == id:
                del self.history[i]
                return 





class IgnoreListWindow(uicls.Window):
    __guid__ = 'form.IgnoreListWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.locationInfo = {}
        self.scope = 'all'
        self.SetCaption(mls.UI_CONTRACTS_IGNORELIST)
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)
        self.SetMinSize([200, 200], 1)
        self.SetTopparentHeight(0)
        self.MakeUnMinimizable()
        self.ModalPosition()
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        hp = uicls.Container(name='hintparent', parent=self.sr.main, align=uiconst.TOTOP, height=16, state=uiconst.UI_HIDDEN)
        t = uicls.Label(text=mls.UI_CONTRACTS_IGNOREHEADER, parent=hp, top=-3, width=self.minsize[0] - 32, autowidth=False, state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        hp.state = uiconst.UI_DISABLED
        hp.height = t.height + 8
        sub = uicls.Container(name='subparent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=26)
        self.sr.ignoreListParent = ignoreListParent = uicls.Container(name='ignoreList', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self.sr.main)
        self.sr.ignoreList = ignoreList = uicls.Scroll(parent=ignoreListParent)
        ignoreList.sr.id = 'ignoreList'
        captionparent = uicls.Container(name='captionparent', parent=self.sr.main, align=uiconst.TOPLEFT, left=128, top=36, idx=0)
        caption = uicls.CaptionLabel(text='', parent=captionparent)
        self.closeBtn = uicls.ButtonGroup(btns=[[mls.UI_CMD_CLOSE,
          self.SelfDestruct,
          None,
          81]], parent=sub)
        self.PopulateIgnoreList()
        return self



    def PopulateIgnoreList(self):
        headers = []
        scrolllist = []
        list = settings.user.ui.Get('contracts_ignorelist', [])
        for l in list:
            data = util.KeyVal()
            data.charID = l
            label = '%s<t>' % cfg.eveowners.Get(l).name
            data.label = label
            data.charID = l
            data.OnDblClick = self.DblClickEntry
            scrolllist.append(listentry.Get('User', data=data))

        self.sr.ignoreList.Load(contentList=scrolllist, headers=headers)
        if len(scrolllist) > 0:
            self.sr.ignoreList.ShowHint()
        else:
            self.sr.ignoreList.ShowHint(mls.UI_CONTRACTS_NOIGNORED)



    def DblClickEntry(self, entry, *args):
        list = settings.user.ui.Get('contracts_ignorelist', [])
        list = [ l for l in list if l != entry.sr.node.charID ]
        settings.user.ui.Set('contracts_ignorelist', list)
        self.PopulateIgnoreList()
        sm.GetService('contracts').ClearCache()




