import uiconst
import service
import moniker
import util
import uix
import sys
import form

class CloneJump(service.Service):
    __exportedcalls__ = {'GetClones': [],
     'GetCloneImplants': [],
     'GetShipClones': [],
     'GetStationClones': [],
     'HasCloneReceivingBay': [],
     'GetCloneAtLocation': [],
     'GetImplantsForClone': [],
     'DestroyInstalledClone': [],
     'CloneJump': [],
     'OfferShipCloneInstallation': [],
     'LastCloneJumpTime': []}
    __guid__ = 'svc.clonejump'
    __displayname__ = 'Clone Jump Service'
    __notifyevents__ = ['OnShipJumpCloneInstallationOffered',
     'OnShipJumpCloneInstallationDone',
     'OnJumpCloneCacheInvalidated',
     'OnShipJumpCloneCacheInvalidated',
     'OnStationJumpCloneCacheInvalidated',
     'OnShipJumpCloneInstallationCanceled']
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.shipJumpClones = None
        self.timeLastJump = None
        self.stationJumpClones = None
        self.cloneInstallOfferActive = 0
        self.lastCloneJumpTime = None



    def GetClones(self):
        self.GetCloneState()
        return self.jumpClones



    def GetCloneImplants(self):
        self.GetCloneState()
        return self.jumpCloneImplants



    def GetLM(self):
        if eve.session.solarsystemid:
            return util.Moniker('jumpCloneSvc', (eve.session.solarsystemid, const.groupSolarSystem))
        else:
            return util.Moniker('jumpCloneSvc', (eve.session.stationid, const.groupStation))



    def GetCloneState(self):
        if not self.jumpClones:
            lm = self.GetLM()
            kv = lm.GetCloneState()
            self.jumpClones = kv.clones
            self.jumpCloneImplants = kv.implants
            self.timeLastJump = kv.timeLastJump



    def GetShipClones(self):
        if not self.shipJumpClones:
            lm = self.GetLM()
            self.shipJumpClones = lm.GetShipCloneState()
        return self.shipJumpClones



    def GetStationClones(self):
        if not self.stationJumpClones:
            lm = self.GetLM()
            self.stationJumpClones = lm.GetStationCloneState()
        return self.stationJumpClones



    def OfferShipCloneInstallation(self, charID):
        lm = self.GetLM()
        sm.GetService('loading').ProgressWnd(mls.UI_INFLIGHT_WAITINGACKNOWLEDGE, mls.UI_INFLIGHT_INSTALLATIONINVITE % {'name': cfg.eveowners.Get(charID).name}, 1, 2, abortFunc=self.CancelShipCloneInstallation)
        try:
            lm.OfferShipCloneInstallation(charID)
        except UserError as e:
            sm.GetService('loading').ProgressWnd(mls.UI_INFLIGHT_CLONEINSTALLATIONABORTED, '', 1, 1)
            raise 



    def LastCloneJumpTime(self):
        self.GetCloneState()
        return self.timeLastJump



    def DestroyInstalledClone(self, cloneID):
        text = None
        myClones = self.GetClones()
        if myClones:
            myClones = myClones.Index('jumpCloneID')
            if cloneID in myClones:
                if myClones[cloneID].locationID == eve.session.stationid:
                    text = mls.UI_INFLIGHT_DESTROYINSTALLEDCLONE1
                else:
                    cfg.evelocations.Prime([myClones[cloneID].locationID])
                    text = mls.UI_INFLIGHT_DESTROYINSTALLEDCLONE2 % {'location': cfg.evelocations.Get(myClones[cloneID].locationID).name}
        if not text:
            if util.GetActiveShip():
                shipClones = self.GetShipClones()
                if shipClones:
                    shipClones = shipClones.Index('jumpCloneID')
                    if cloneID in shipClones:
                        cfg.eveowners.Prime([shipClones[cloneID].ownerID])
                        cfg.evelocations.Prime([shipClones[cloneID].locationID])
                        text = mls.UI_INFLIGHT_DESTROYINSTALLEDCLONE3 % {'name': cfg.eveowners.Get(shipClones[cloneID].ownerID).name,
                         'location': cfg.evelocations.Get(shipClones[cloneID].locationID).name}
        if not text:
            return 
        ret = eve.Message('AskAreYouSure', {'cons': mls.UI_INFLIGHT_DESTROYINSTALLEDCLONE4 % {'text': text}}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            lm = self.GetLM()
            lm.DestroyInstalledClone(cloneID)



    def InstallCloneInStation(self):
        if not eve.session.stationid:
            return 
        lm = self.GetLM()
        ret = eve.Message('AskAcceptJumpCloneCost', {'cost': util.FmtISK(lm.GetPriceForClone())}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            lm.InstallCloneInStation()



    def CancelShipCloneInstallation(self, *args):
        sm.GetService('loading').ProgressWnd(mls.UI_INFLIGHT_CLONEINSTALLATIONABORTED, '', 1, 1)
        lm = self.GetLM()
        lm.CancelShipCloneInstallation()



    def CloneJump(self, destLocationID):
        if uiconst.ID_YES != eve.Message('ConfirmStripApparel', {}, uiconst.YESNO, suppress=uiconst.ID_YES):
            return 
        if not eve.session.stationid:
            eve.Message('NotAtStation')
            return 
        for each in sm.GetService('window').GetWindows()[:]:
            if isinstance(each, form.VirtualInvWindow) and each.__guid__ not in ('form.ItemHangar', 'form.ShipHangar'):
                each.CloseX()

        lm = self.GetLM()
        try:
            sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, False)
        except UserError as e:
            if e.msg not in ('JumpCheckWillLoseExistingCloneAndImplants', 'JumpCheckWillLoseExistingClone', 'JumpCheckIntoShip'):
                raise e
            if eve.Message(e.msg, {}, uiconst.YESNO) == uiconst.ID_YES:
                eve.session.ResetSessionChangeTimer('Retrying with confirmation approval')
                sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, True)
            sys.exc_clear()
        sm.GetService('cc').ClearCurrentPaperDollData()



    def GetCloneAtLocation(self, locationID):
        clones = self.GetClones()
        if clones:
            for c in clones:
                if locationID == c.locationID:
                    return c.jumpCloneID




    def GetImplantsForClone(self, cloneID):
        cloneImplants = self.GetCloneImplants()
        if not cloneImplants:
            return []
        implantsByCloneID = cloneImplants.Filter('jumpCloneID')
        return implantsByCloneID.get(cloneID, [])



    def HasCloneReceivingBay(self):
        if eve.session.shipid:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            for module in ship.modules:
                if const.typeCloneVatBayI == module.typeID:
                    return True

        return False



    def ProcessSessionChange(self, isRemote, session, change):
        if 'shipid' in change:
            self.shipJumpClones = None
        if 'solarsystemid2' in change or 'solarsystemid' in change or 'stationid' in change:
            self.stationJumpClones = None



    def OnJumpCloneCacheInvalidated(self):
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.timeLastJump = None
        sm.ScatterEvent('OnCloneJumpUpdate')



    def OnShipJumpCloneCacheInvalidated(self, locationID, charID):
        if eve.session.shipid == locationID:
            self.shipJumpClones = None
            sm.ScatterEvent('OnShipCloneJumpUpdate')



    def OnStationJumpCloneCacheInvalidated(self, locationID, charID):
        if eve.session.stationid == locationID:
            self.stationJumpClones = None
            sm.ScatterEvent('OnStationCloneJumpUpdate')



    def OnShipJumpCloneInstallationOffered(self, args):
        (offeringCharID, targetCharID, shipID, b,) = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 1
        cfg.eveowners.Prime([offeringCharID, targetCharID])
        offeringChar = cfg.eveowners.Get(offeringCharID)
        cfg.evelocations.Prime([shipID])
        ship = cfg.evelocations.Get(shipID)
        lm = self.GetLM()
        costs = lm.GetPriceForClone()
        ret = eve.Message('JumpCloneInstallationOffered', {'offerer': offeringChar.name,
         'shipname': ship.name,
         'costs': util.FmtISK(costs)}, uiconst.YESNO)
        try:
            if ret == uiconst.ID_YES:
                lm.AcceptShipCloneInstallation()
            elif ret != uiconst.ID_CLOSE:
                lm.CancelShipCloneInstallation()
        except UserError as e:
            eve.Message(e.msg, e.dict)
            sys.exc_clear()
        self.cloneInstallOfferActive = 0



    def OnShipJumpCloneInstallationDone(self, args):
        (offeringCharID, targetCharID, shipID, b,) = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 0
        sm.ScatterEvent('OnShipJumpCloneUpdate')
        sm.GetService('loading').ProgressWnd(mls.UI_INFLIGHT_CLONEINSTALLATIONFINISHED, '', 1, 1)



    def OnShipJumpCloneInstallationCanceled(self, args):
        try:
            sm.GetService('loading').ProgressWnd(mls.UI_INFLIGHT_CLONEINSTALLATIONABORTED, '', 1, 1)
            lm = self.GetLM()
            lm.CancelShipCloneInstallation()
        except UserError as e:
            self.LogInfo('Ignoring usererror', e.msg, 'while cancelling ship clone installation')
            sys.exc_clear()




