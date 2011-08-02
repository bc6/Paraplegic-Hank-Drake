import blue
import service
import util
import uix
import moniker
import uthread
import sys
import pos
import log
import uiconst
ONLINE_STATES = (pos.STRUCTURE_ONLINING,
 pos.STRUCTURE_REINFORCED,
 pos.STRUCTURE_ONLINE,
 pos.STRUCTURE_OPERATING,
 pos.STRUCTURE_VULNERABLE,
 pos.STRUCTURE_SHIELD_REINFORCE,
 pos.STRUCTURE_ARMOR_REINFORCE,
 pos.STRUCTURE_INVULNERABLE)
UNANCHORABLE_STATES = (pos.STRUCTURE_ONLINING,
 pos.STRUCTURE_REINFORCED,
 pos.STRUCTURE_ONLINE,
 pos.STRUCTURE_OPERATING,
 pos.STRUCTURE_UNANCHORED,
 pos.STRUCTURE_VULNERABLE,
 pos.STRUCTURE_SHIELD_REINFORCE,
 pos.STRUCTURE_ARMOR_REINFORCE,
 pos.STRUCTURE_INVULNERABLE)

class PlayerOwned(service.Service):
    __guid__ = 'svc.pwn'
    __exportedcalls__ = {'CanAnchorStructure': [],
     'CanUnanchorStructure': [],
     'CanOnlineStructure': [],
     'CanOfflineStructure': [],
     'CanAssumeControlStructure': [],
     'GetStructureState': [],
     'CompareShipStructureHarmonic': [],
     'CheckAnchoringPosition': [],
     'Anchor': [],
     'EnterTowerPassword': [],
     'EnterShipPassword': [],
     'AssumeStructureControl': [],
     'RelinquishStructureControl': [],
     'UnlockStructureTarget': [],
     'GetCurrentTarget': [],
     'ClrCurrentTarget': [],
     'GetCurrentControl': [],
     'GetActiveBridgeForShip': [],
     'GetActiveBridgeForStructure': []}
    __notifyevents__ = ['OnSlimItemChange',
     'OnTargetOBO',
     'OnAllianceBridgeModeChange',
     'ProcessAllianceBridgeModePurge',
     'DoSessionChanging',
     'DoBallsAdded',
     'DoBallRemove']
    __dependencies__ = ['godma', 'michelle']

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        sm.FavourMe(self.DoBallsAdded)
        self.currenttargets = {}
        self.currentcontrol = {}
        self.allianceBridgesByShip = {}
        self.currentlyAssuming = {}



    def Stop(self, stream):
        service.Service.Stop(self)



    def OnSlimItemChange(self, oldItem, newItem):
        if newItem.categoryID != const.categoryStructure:
            return 
        if newItem.posState == oldItem.posState and newItem.posTimestamp == oldItem.posTimestamp and newItem.controllerID == oldItem.controllerID and newItem.incapacitated == oldItem.incapacitated:
            return 
        if oldItem.controllerID is not None and newItem.controllerID == None:
            uthread.new(self.RelinquishStructureControl, oldItem, silent=True, force=True)
        (stateName, stateTimestamp, stateDelay,) = self.GetStructureState(newItem)
        if stateName == 'onlining':
            uthread.pool('pwn::StalledOnlineEvent', self.StalledOnlineEvent, newItem.itemID, newItem.posState, stateTimestamp, stateDelay)



    def StalledOnlineEvent(self, itemID, posState, stateTimestamp, stateDelay):
        item = self.michelle.GetItem(itemID)
        if item is None or item.posState != posState or item.posTimestamp != stateTimestamp:
            return 
        (x1, x2, stateDelay,) = self.GetStructureState(item)
        blue.pyos.synchro.Sleep(stateDelay)
        item = self.michelle.GetItem(itemID)
        if item is None:
            return 
        if item.posState != posState or item.posTimestamp != stateTimestamp:
            if item.posState != pos.STRUCTURE_ONLINE:
                return 
        sm.ScatterEvent('OnStructureFullyOnline', itemID)
        if item.controlTowerID is not None:
            sm.ScatterEvent('OnSpecialFX', item.controlTowerID, itemID, item.typeID, None, None, [], 'effects.StructureOnlined', 0, 1, 0)



    def CompareShipStructureHarmonic(self, shipID, itemID):
        item = self.michelle.GetItem(itemID)
        if not item:
            return False
        if item.groupID == const.groupControlTower:
            controlTowerID = itemID
            towerItem = item
        else:
            controlTowerID = item.controlTowerID
            if controlTowerID is None:
                return False
            towerItem = self.michelle.GetItem(controlTowerID)
            if towerItem is None:
                return False
        forceFieldID = towerItem.forceFieldID
        if forceFieldID is None:
            return False
        fieldBall = self.michelle.GetBall(forceFieldID)
        shipBall = self.michelle.GetBall(shipID)
        if not shipBall or not fieldBall:
            return False
        if fieldBall.harmonic != -1 and fieldBall.harmonic == shipBall.harmonic:
            return True
        return False



    def GetStructureState(self, slimItem):
        stateName = 'Unknown_State_%s' % slimItem.posState
        stateTimestamp = None
        stateDelay = None
        godmaSM = self.godma.GetStateManager()
        if slimItem.posState == pos.STRUCTURE_ANCHORED:
            stateName = 'anchored'
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
                if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = 'anchoring'
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_ONLINING:
            stateName = 'online'
            if slimItem.posState == pos.STRUCTURE_ONLINING and slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).onliningDelay
                if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = 'onlining'
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_UNANCHORED:
            stateName = 'unanchored'
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).unanchoringDelay
                if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = 'unanchoring'
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_VULNERABLE:
            stateName = 'vulnerable'
        elif slimItem.posState == pos.STRUCTURE_INVULNERABLE:
            stateName = 'invulnerable'
        elif slimItem.posState == pos.STRUCTURE_REINFORCED:
            delayMs = (blue.os.GetTime() - slimItem.posTimestamp) / 10000
            if delayMs < 0:
                stateName = 'reinforced'
                stateDelay = -delayMs
                stateTimestamp = blue.os.GetTime() + delayMs
        elif slimItem.posState in (pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE):
            stateName = 'reinforced'
            stateTimestamp = slimItem.posTimestamp + slimItem.posDelayTime
            stateDelay = slimItem.posDelayTime
        elif slimItem.posState == pos.STRUCTURE_OPERATING:
            stateName = 'online'
            delayMs = (blue.os.GetTime() - slimItem.posTimestamp) / 10000
            if delayMs < 0:
                stateName = 'operating'
                stateDelay = -delayMs
                stateTimestamp = blue.os.GetTime() + delayMs
        elif slimItem.posState == pos.STRUCTURE_ONLINE:
            stateName = 'online'
        if slimItem.incapacitated:
            stateName = 'incapacitated'
        return (stateName, stateTimestamp, stateDelay)



    def EnterTowerPassword(self, towerID):
        password = uix.NamePopup(caption=mls.UI_INFLIGHT_TOWERSHIELDHARMONIC, label=mls.UI_INFLIGHT_ENTERTHESHAREDSECRET, setvalue='', icon=-1, modal=1, btns=None, maxLength=50, passwordChar='*')
        if password is None:
            return 
        posMgr = moniker.GetPOSMgr()
        posMgr.SetTowerPassword(towerID, password['name'])



    def EnterShipPassword(self):
        format = [{'type': 'text',
          'refreshheight': 1,
          'text': mls.UI_INFLIGHT_ENTERHARMONICPASSW,
          'frame': 1}, {'type': 'edit',
          'setvalue': '',
          'label': '_hide',
          'key': 'name',
          'maxLength': 50,
          'passwordChar': '*',
          'setfocus': 1,
          'frame': 1}, {'type': 'text',
          'refreshheight': 1,
          'text': mls.UI_INFLIGHT_HARMONICPASSWTEXT,
          'frame': 1}]
        retval = uix.HybridWnd(format, mls.UI_INFLIGHT_SHIPSHIELDHARMONIC, 1, None, uiconst.OKCANCEL, icon=uiconst.OKCANCEL, minW=240, minH=170)
        if retval is not None:
            if session.stationid:
                eve.Message('CannotSetShieldHarmonicPassword')
            else:
                posMgr = moniker.GetPOSMgr()
                posMgr.SetShipPassword(retval['name'])



    def Anchor(self, itemID, position):
        item = sm.GetService('michelle').GetItem(itemID)
        for row in cfg.dgmtypeeffects.get(item.typeID, []):
            if row.effectID == const.effectAnchorDropForStructures:
                posMgr = moniker.GetPOSMgr()
                posMgr.AnchorStructure(itemID, position)
                break




    def CheckAnchoringPosition(self, itemID, position):
        item = self.michelle.GetItem(itemID)
        if item.categoryID != const.categoryStructure:
            raise UserError('CantConfigureThat')
        bp = self.michelle.GetBallpark()
        shipBall = bp.GetBall(session.shipid)
        itemBall = bp.GetBall(itemID)
        if item.groupID == const.groupControlTower:
            actualDistance = bp.GetCenterDist(session.shipid, itemID) - shipBall.radius - itemBall.radius
            if actualDistance > 30000:
                raise UserError('CantConfigureDistant2', {'actual': actualDistance,
                 'needed': 30000})
            self.CheckForStructures(itemID)
        else:
            towerID = self.LocateControlTower(itemID, 'CantAnchorRequireTower')
            self.CheckTowerAvailablility(towerID, itemID)



    def CheckForStructures(self, towerID):
        bp = self.michelle.GetBallpark()
        typeID = self.michelle.GetItem(towerID).typeID
        maxRange = self.godma.GetType(typeID).maxStructureDistance
        self.LogInfo('CheckForStructures', towerID, maxRange)
        for ballID in bp.balls.itervalues():
            if ballID < 0:
                continue
            self.LogInfo('CheckForStructures.iteration', ballID)
            ballItem = self.michelle.GetItem(ballID)
            if ballItem is None:
                continue
            if ballItem.categoryID == const.categoryStructure:
                ball = bp.GetBall(ballID)
                if not ball.isFree:
                    raise UserError('CantAnchorTowerInvalidStructures', {'item': (TYPEID, ballItem.typeID)})
                self.LogInfo('Anchor ignore', cfg.invtypes.Get(ballItem.typeID).name)




    def LocateControlTower(self, locusID, raiseError = None):
        bp = self.michelle.GetBallpark()
        for ballID in bp.GetBallIdsAndDistInRange(locusID, 300000):
            if ballID < 0:
                continue
            item = self.michelle.GetItem(ballID)
            if item is None or item.groupID != const.groupControlTower:
                continue
            maxDistance = self.godma.GetType(item.typeID).maxStructureDistance
            if bp.DistanceBetween(ballID, locusID) <= maxDistance:
                return ballID

        if raiseError is not None:
            item = self.michelle.GetItem(locusID)
            raise UserError(raiseError, {'item': (TYPEID, item.typeID)})



    def CheckTowerAvailablility(self, towerID, structureID):
        if towerID is None:
            return 
        if towerID != structureID:
            if not self.IsStructureFullyOnline(towerID):
                raise UserError('CantTowerNotOnline')



    def IsStructureFullyAnchored(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return 0
        slimItem = bp.GetInvItem(itemID)
        if slimItem.posState != pos.STRUCTURE_ANCHORED:
            return 0
        if slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
            if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1



    def IsStructureFullyOnline(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None or itemID is None:
            return 0
        slimItem = bp.GetInvItem(itemID)
        if not hasattr(slimItem, 'posState'):
            return 0
        if slimItem.posState not in ONLINE_STATES:
            return 0
        if slimItem.posState == pos.STRUCTURE_ONLINING and slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).onliningDelay
            if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1



    def IsStructureFullyUnanchored(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return 0
        slimItem = bp.GetInvItem(itemID)
        if slimItem.posState != pos.STRUCTURE_UNANCHORED:
            return 0
        if slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).unanchoringDelay
            if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1



    def CanAnchorStructure(self, itemID):
        return self.IsStructureFullyUnanchored(itemID)



    def CanOnlineStructure(self, itemID, fullyAnchored = None):
        return self.IsStructureFullyAnchored(itemID)



    def CanOfflineStructure(self, itemID, fullyOnline = None):
        return self.IsStructureFullyOnline(itemID)



    def CanUnanchorStructure(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(itemID)
        godmaSM = self.godma.GetStateManager()
        if slimItem.posState == pos.STRUCTURE_ANCHORED:
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
                if blue.os.GetTime() - slimItem.posTimestamp < delayMs * 10000:
                    return 0
        elif slimItem.posState in UNANCHORABLE_STATES:
            return 0
        return godmaSM.TypeHasEffect(slimItem.typeID, const.effectAnchorLiftForStructures)



    def StructureIsOrphan(self, itemID):
        item = self.michelle.GetItem(itemID)
        if item.categoryID == const.categorySovereigntyStructure:
            return False
        if item.groupID == const.groupControlTower:
            return False
        controlTowerID = item.controlTowerID
        if controlTowerID is None:
            return True
        towerItem = self.michelle.GetItem(controlTowerID)
        if towerItem is None:
            return True
        return False



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::playerOwned')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, ballsToAdd):
        for (ball, slimItem,) in ballsToAdd:
            try:
                if slimItem == None:
                    continue
                if slimItem.categoryID != const.categoryStructure:
                    continue
                controllerID = slimItem.controllerID
                if controllerID is not None and controllerID == eve.session.shipid:
                    uthread.new(self.RelinquishStructureControl, slimItem)
            except:
                self.LogError('DoBallsAdded - failed to say i have control', (ball, slimItem))
                log.LogTraceback()
                sys.exc_clear()




    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem == None:
            return 
        if slimItem.categoryID != const.categoryStructure:
            return 
        if slimItem.controllerID == eve.session.charid:
            uthread.new(self.RelinquishStructureControl, slimItem, silent=True, force=True)



    def DoSessionChanging(self, isRemote, session, change):
        if 'stationid' in change:
            self.currenttargets = {}
            self.currentcontrol = {}



    def CanAssumeControlStructure(self, structureID):
        item = sm.GetService('michelle').GetItem(structureID)
        for row in cfg.dgmtypeattribs.get(item.typeID, []):
            if row.attributeID == const.attributePosPlayerControlStructure:
                return 1

        return 0



    def AssumeStructureControl(self, slimItem, silent = False, force = False):
        item = sm.GetService('michelle').GetItem(slimItem.itemID) or slimItem
        if item and getattr(item, 'itemID', None) and (item.itemID in self.currentlyAssuming or item.itemID in self.currentcontrol):
            raise UserError('StructureControlled', {'item': (TYPEID, item.typeID)})
        if slimItem.posState < pos.STRUCTURE_ONLINING:
            raise UserError('StructureNotControllableUntilOnline', {'item': (TYPEID, item.typeID)})
        self.currentlyAssuming[item.itemID] = True
        if item and not item.controllerID or force:
            for row in cfg.dgmtypeattribs.get(item.typeID, []):
                if row.attributeID == const.attributePosPlayerControlStructure:
                    self.currentcontrol[item.itemID] = True
                    if not silent:
                        try:
                            posMgr = moniker.GetPOSMgr()
                            posMgr.AssumeStructureControl(item.itemID)
                        except UserError as e:
                            del self.currentcontrol[item.itemID]
                            self.currentlyAssuming.pop(item.itemID, None)
                            eve.Message(e.msg, e.dict)
                            sys.exc_clear()
                    sm.ScatterEvent('OnAssumeStructureControl', item.itemID)
                    break

        self.currentlyAssuming.pop(item.itemID, None)



    def RelinquishStructureControl(self, slimItem, silent = False, force = False):
        item = sm.GetService('michelle').GetItem(slimItem.itemID) or slimItem
        if item and item.controllerID or force:
            for row in cfg.dgmtypeattribs.get(item.typeID, []):
                if row.attributeID == const.attributePosPlayerControlStructure:
                    if self.currentcontrol.has_key(item.itemID):
                        del self.currentcontrol[item.itemID]
                    if self.currenttargets.has_key(item.itemID):
                        del self.currenttargets[item.itemID]
                    if not silent:
                        try:
                            posMgr = moniker.GetPOSMgr()
                            posMgr.RelinquishStructureControl(item.itemID)
                        except UserError as e:
                            eve.Message(e.msg, e.dict)
                            sys.exc_clear()
                    sm.ScatterEvent('OnRelinquishStructureControl', item.itemID)
                    break




    def UnlockStructureTarget(self, structureID):
        if self.currenttargets.has_key(structureID):
            sm.GetService('pwntarget').UnLockTargetOBO(structureID, self.currenttargets[structureID])
            del self.currenttargets[structureID]



    def GetControllerIDName(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(itemID)
        controller = getattr(slimItem, 'controllerID', 0)
        if controller:
            ct = cfg.eveowners.Get(controller).name
        else:
            ct = mls.UI_GENERIC_NOTAVAILABLESHORT
            if self.currenttargets.has_key(itemID):
                del self.currenttargets[itemID]
        return (controller, ct)



    def GetDogmaLM(self):
        return self.godma.GetStateManager().GetDogmaLM()



    def OnTargetOBO(self, what, sid = None, tid = None, reason = None):
        if what == 'add':
            self.currenttargets[sid] = tid
        elif what == 'lost':
            if self.currenttargets.has_key(sid):
                del self.currenttargets[sid]



    def ClrCurrentTarget(self, structureID = None):
        if structureID and self.currenttargets.has_key(structureID):
            del self.currenttargets[structureID]
            del self.currentcontrol[structureID]
        elif structureID is None:
            self.currenttargets = {}
            self.currentcontrol = {}



    def GetCurrentTarget(self, structureID = None):
        if structureID is None:
            return self.currenttargets
        return self.currenttargets.get(structureID, None)



    def GetCurrentControl(self, structureID = None):
        if structureID is None:
            return self.currentcontrol
        return self.currentcontrol.get(structureID, None)



    def ProcessAllianceBridgeModePurge(self):
        self.allianceBridgesByShip.clear()



    def OnAllianceBridgeModeChange(self, shipID, toSolarsystemID, toBeaconID, flag):
        if flag:
            self.allianceBridgesByShip[shipID] = (toSolarsystemID, toBeaconID)
        elif shipID in self.allianceBridgesByShip:
            del self.allianceBridgesByShip[shipID]



    def GetActiveBridgeForShip(self, shipID):
        if shipID in self.allianceBridgesByShip:
            return self.allianceBridgesByShip[shipID]



    def GetActiveBridgeForStructure(self, structureID):
        slim = self.michelle.GetItem(structureID)
        if slim:
            remoteStructureID = getattr(slim, 'remoteStructureID', None)
            remoteSystemID = getattr(slim, 'remoteSystemID', None)
            if remoteStructureID and remoteSystemID:
                return (remoteStructureID, remoteSystemID)




