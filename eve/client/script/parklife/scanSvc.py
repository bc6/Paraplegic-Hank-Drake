import service
import util
import blue
import functools
import uix
import uthread
import uiconst
from foo import Vector3
CACHED_RESULT_GROUPS = (const.probeScanGroupSignatures, const.probeScanGroupAnomalies)
RECONNECT_DELAY_MINUTES = 5

def UserErrorIfScanning(action, *args, **kwargs):

    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        if sm.StartService('scanSvc').IsScanning():
            raise UserError('ScanInProgressGeneric')
        return action(*args, **kwargs)


    return wrapper



class ScanSvc(service.Service):
    __guid__ = 'svc.scanSvc'
    __servicename__ = 'svc.scanSvc'
    __displayname__ = 'Scanner Probe Service'
    __notifyevents__ = ['OnSessionChanged',
     'OnSystemScanStarted',
     'OnSystemScanStopped',
     'OnProbeWarpStart',
     'OnProbeStateChanged',
     'OnNewProbe',
     'OnRemoveProbe',
     'OnScannerInfoRemoved']
    __dependencies__ = ['michelle']
    __uthreads__ = []
    __exportedcalls__ = {'SetProbeDestination': [service.ROLE_ANY],
     'SetProbeRangeStep': [service.ROLE_ANY],
     'GetProbeData': [service.ROLE_ANY],
     'GetScanResults': [service.ROLE_ANY],
     'RequestScans': [service.ROLE_ANY],
     'RecoverProbe': [service.ROLE_ANY],
     'RecoverProbes': [service.ROLE_ANY],
     'ReconnectToLostProbes': [service.ROLE_ANY],
     'DestroyProbe': [service.ROLE_ANY],
     'GetScanRangeStepsByTypeID': [service.ROLE_ANY]}

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, ms):
        self.currentScan = None
        self.lastResults = None
        self.probeLabels = {}
        self.probeData = {}
        self.scanningProbes = None
        self.scanRangeByTypeID = {}
        self.lastReconnection = None
        self.lastRangeStepUsed = 5
        self.resultsIgnored = set()
        self.resultsCached = {}



    def OnNewProbe(self, probe):
        probe.rangeStep = self.lastRangeStepUsed
        probe.scanRange = self.GetScanRangeStepsByTypeID(probe.typeID)[(self.lastRangeStepUsed - 1)]
        probe.destination = probe.pos
        self.probeData[probe.probeID] = probe
        self.UpdateProbeState(probe.probeID, const.probeStateIdle, 'OnNewProbe')
        sm.ScatterEvent('OnProbeAdded', probe)



    def OnRemoveProbe(self, probeID):
        if probeID in self.probeData:
            del self.probeData[probeID]
        sm.ScatterEvent('OnProbeRemoved', probeID)



    def GetActiveProbes(self):
        return [ kv.probeID for kv in self.probeData.values() if kv.state != const.probeStateInactive ]



    def GetProbeState(self, probeID):
        if probeID in self.probeData:
            return self.probeData[probeID].state



    def IsProbeActive(self, probeID):
        return bool(probeID in self.probeData and self.probeData[probeID].state)



    def GetProbeData(self):
        return self.probeData



    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change or 'shipid' in change:
            self.FlushScannerState()



    def SetProbeDestination(self, probeID, location):
        self.probeData[probeID].destination = location



    def SetProbeRangeStep(self, probeID, rangeStep):
        if 1 <= rangeStep <= const.scanProbeNumberOfRangeSteps:
            self.lastRangeStepUsed = rangeStep
            probe = self.probeData[probeID]
            probe.rangeStep = rangeStep
            rangeSteps = self.GetScanRangeStepsByTypeID(probe.typeID)
            probe.scanRange = rangeSteps[(rangeStep - 1)]
            sm.ScatterEvent('OnProbeRangeUpdated', probeID, probe.scanRange)



    def SetProbeActiveState(self, probeID, state):
        if probeID in self.probeData:
            if (self.probeData[probeID].state, int(state)) in [(const.probeStateIdle, const.probeStateInactive), (const.probeStateInactive, const.probeStateIdle)]:
                self.UpdateProbeState(probeID, int(state), 'SetProbeActiveState')



    def RequestScans(self):
        if len(self.probeData) > 0:
            probes = dict([ (p.probeID, p) for p in self.probeData.itervalues() if p.state == const.probeStateIdle ]) or None
            if not probes:
                return 
        else:
            probes = None
        scanMan = sm.RemoteSvc('scanMgr').GetSystemScanMgr()
        scanMan.RequestScans(probes)
        if probes:
            self.scanningProbes = probes.keys()[:]
            for pID in probes:
                self.UpdateProbeState(pID, const.probeStateMoving, 'RequestScans')

            sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_moving_play'))
        else:
            self.scanningProbes = [session.shipid]



    def OnProbeStateChanged(self, probeID, probeState):
        self.LogInfo('OnProbeStageChanged', probeID, probeState)
        self.UpdateProbeState(probeID, probeState, 'OnProbeStateChanged')



    def GetScanningProbes(self):
        return self.scanningProbes



    def GetScanResults(self):
        return self.lastResults



    def GetCurrentScan(self):
        return self.currentScan



    def OnProbeWarpStart(self, probeID, fromPos, toPos, startTime, duration):
        self.LogInfo('OnProbeWarpStart', probeID)
        self.UpdateProbeState(probeID, const.probeStateWarping, 'OnProbeWarpStart')



    def UpdateProbeState(self, probeID, state, caller = None, notify = True):
        if probeID not in self.probeData:
            self.LogWarn('UpdateProbeState: probe', probeID, 'not in my list of probes. Called by', caller)
            return 
        self.probeData[probeID].state = state
        if notify:
            sm.ScatterEvent('OnProbeStateUpdated', probeID, state)



    def OnSystemScanStarted(self, startTime, durationMs, probes):
        self.LogInfo('OnSystemScanStarted', startTime, durationMs)
        self.currentScan = util.KeyVal(__doc__='currentScan')
        self.currentScan.startTime = startTime
        self.currentScan.duration = durationMs
        self.currentScan.probeIDs = []
        for pID in probes:
            self.UpdateProbeState(pID, const.probeStateScanning, 'OnSystemScanStarted', notify=False)
            if pID not in self.probeData:
                self.LogError('probe', pID, 'not in my list of probes')
                continue
            self.probeData[pID].pos = self.probeData[pID].destination = probes[pID].pos
            self.currentScan.probeIDs.append(pID)

        sm.ScatterEvent('OnSystemScanBegun')
        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_moving_stop'))
        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_analyzing_play'))



    def OnSystemScanStopped(self, probes, results):
        self.LogInfo('OnSystemScanStopped', probes, results)
        for pID in probes:
            self.UpdateProbeState(pID, const.probeStateIdle, 'OnSystemScanStopped', notify=False)

        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_moving_stop'))
        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_analyzing_stop'))
        self.currentScan = None
        self.scanningProbes = None
        if not results:
            sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_negative_play'))
            eve.Message('ScnNoResults')
        else:
            hasPerfectResult = False
            for result in results:
                if result.certainty >= const.probeResultPerfect and isinstance(result.data, Vector3):
                    hasPerfectResult = True
                    if result.scanGroupID in CACHED_RESULT_GROUPS:
                        self.resultsCached[result.id] = result

            if hasPerfectResult:
                sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_positive_play'))
            else:
                sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_partial_play'))
        if not results:
            results = []
        ids = set([ r.id for r in results ])
        for id in self.resultsCached:
            for result in results[:]:
                if result.id == id:
                    results.remove(result)

            results.append(self.resultsCached[id])

        if results:
            results.sort(key=lambda x: x.id)
        else:
            results = None
        self.lastResults = results
        sm.ScatterEvent('OnSystemScanDone')



    def GetScanRangeStepsByTypeID(self, typeID):
        if typeID not in self.scanRangeByTypeID:
            baseScanRange = sm.StartService('godma').GetTypeAttribute(typeID, const.attributeBaseScanRange)
            baseFactor = sm.StartService('godma').GetTypeAttribute(typeID, const.attributeRangeFactor)
            steps = []
            for i in xrange(const.scanProbeNumberOfRangeSteps):
                factor = baseFactor ** i
                scanRange = baseScanRange * factor * const.AU
                steps.append(scanRange)

            self.scanRangeByTypeID[typeID] = steps
            return steps
        return self.scanRangeByTypeID[typeID]



    def DestroyProbe(self, probeID):
        if probeID not in self.probeData:
            return 
        if self.probeData[probeID].state in (const.probeStateIdle, const.probeStateInactive):
            scanMan = sm.RemoteSvc('scanMgr').GetSystemScanMgr()
            scanMan.DestroyProbe(probeID)
            del self.probeData[probeID]



    def ConeScan(self, scanangle, scanRange, x, y, z):
        return sm.RemoteSvc('scanMgr').GetSystemScanMgr().ConeScan(scanangle, scanRange, x, y, z)



    def ReconnectToLostProbes(self):
        if not session.solarsystemid2:
            return 
        ship = sm.StartService('michelle').GetItem(eve.session.shipid)
        if ship and ship.groupID == const.groupCapsule:
            raise UserError('ScnProbeRecoverToPod')
        if self.CanClaimProbes():
            sm.RemoteSvc('scanMgr').GetSystemScanMgr().ReconnectToLostProbes()
            self.lastReconnection = blue.os.GetTime()
            uthread.new(self.Thread_ShowReconnectToProbesAvailable, self.lastReconnection)
        else:
            seconds = RECONNECT_DELAY_MINUTES * const.MIN - (blue.os.GetTime() - self.lastReconnection)
            raise UserError('ScannerProbeReconnectWait', {'when': (TIMESHRT, seconds)})



    def Thread_ShowReconnectToProbesAvailable(self, lastReconnection):
        blue.pyos.synchro.Sleep(RECONNECT_DELAY_MINUTES * 60 * 1000)
        sm.ScatterEvent('OnReconnectToProbesAvailable')



    def CanClaimProbes(self):
        if self.HasOnlineProbeLauncher() and (self.lastReconnection is None or blue.os.GetTime() - self.lastReconnection > 5 * const.MIN):
            return True
        return False



    def HasOnlineProbeLauncher(self):
        shipItem = sm.GetService('godma').GetStateManager().GetItem(session.shipid)
        for module in shipItem.modules:
            if module.groupID == const.groupScanProbeLauncher and module.isOnline:
                return True

        return False



    def GetProbeLabel(self, probeID):
        if probeID in self.probeLabels:
            return self.probeLabels[probeID]
        newlabel = mls.UI_INFLIGHT_PROBE_LABEL % (len(self.probeLabels) + 1)
        self.probeLabels[probeID] = newlabel
        return newlabel



    def RecoverProbe(self, probeID):
        if probeID not in self.probeData:
            return 
        if self.probeData[probeID].state in (const.probeStateIdle, const.probeStateInactive):
            self.RecoverProbes([probeID])



    def RecoverProbes(self, probeIDs):
        ship = sm.StartService('michelle').GetItem(eve.session.shipid)
        if ship and ship.groupID == const.groupCapsule:
            raise UserError('ScnProbeRecoverToPod')
        successProbeIDs = sm.RemoteSvc('scanMgr').GetSystemScanMgr().RecoverProbes(probeIDs)
        for pID in successProbeIDs:
            self.UpdateProbeState(pID, const.probeStateMoving, 'RecoverProbes')

        if len(successProbeIDs) < len(probeIDs):
            raise UserError('NotAllProbesReturnedSuccessfully')



    def OnScannerInfoRemoved(self):
        self.LogInfo('OnScannerInfoRemoved received: flushing scanner state')
        self.FlushScannerState()



    def FlushScannerState(self):
        self.LogInfo('FlushScannerState: resetting state and scattering OnScannerDisconnected')
        self.probeData = {}
        self.lastResults = None
        self.currentScan = None
        self.scanningProbes = None
        self.resultsIgnored = set()
        self.resultsCached = {}
        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_moving_stop'))
        sm.StartService('audio').SendUIEvent(unicode('wise:/msg_scanner_analyzing_stop'))
        sm.ScatterEvent('OnScannerDisconnected')



    def IsScanning(self):
        if self.scanningProbes:
            return True
        else:
            return False



    def GetProbeMenu(self, probeID, probeIDs = None, *args):
        menu = []
        if probeID == eve.session.shipid:
            return menu
        bp = sm.StartService('michelle').GetBallpark(doWait=True)
        if bp is None:
            return menu
        probeIDs = probeIDs or [probeID]
        if probeID not in probeIDs:
            probeIDs.append(probeID)
        probeSlim = bp.slimItems.get(probeID, None)
        if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            menu.append(('CopyID', self._GMCopyID, (probeID,)))
            menu.append(None)
        if self.IsProbeActive(probeID):
            menu.append((mls.UI_CMD_DEACTIVATE_PROBE, self.SetProbeActiveStateOff_Check, (probeID, probeIDs)))
        else:
            menu.append((mls.UI_CMD_ACTIVATE_PROBE, self.SetProbeActiveStateOn_Check, (probeID, probeIDs)))
        probes = self.GetProbeData()
        if probeID in probes:
            probe = probes[probeID]
            scanRanges = self.GetScanRangeStepsByTypeID(probe.typeID)
            menu.append((mls.UI_INFLIGHT_SCANRANGE, [ (util.FmtDist(range), self.SetScanRange_Check, (probeID,
               probeIDs,
               range,
               index + 1)) for (index, range,) in enumerate(scanRanges) ]))
        menu.append((mls.UI_CMD_RECOVER_PROBE, self.RecoverProbe_Check, (probeID, probeIDs)))
        menu.append((mls.UI_CMD_DESTROYPROBE, self.DestroyProbe_Check, (probeID, probeIDs)))
        return menu



    def _GMCopyID(self, id):
        blue.pyos.SetClipboardData(str(id))



    @UserErrorIfScanning
    def SetScanRange_Check(self, probeID, probeIDs, range, rangeStep):
        for _probeID in probeIDs:
            probe = self.GetProbeData()[_probeID]
            self.SetProbeRangeStep(_probeID, rangeStep)




    @UserErrorIfScanning
    def RecoverProbe_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.RecoverProbe(_probeID)




    @UserErrorIfScanning
    def SetProbeActiveStateOn_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.SetProbeActiveState(_probeID, True)




    @UserErrorIfScanning
    def SetProbeActiveStateOff_Check(self, probeID, probeIDs):
        for _probeID in probeIDs:
            self.SetProbeActiveState(_probeID, False)




    @UserErrorIfScanning
    def DestroyProbe_Check(self, probeID, probeIDs):
        if probeIDs and eve.Message('DestroySelectedProbes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            for _probeID in probeIDs:
                self.DestroyProbe(_probeID)




    def IgnoreResult(self, *targets):
        for targetID in targets:
            self.resultsIgnored.add(targetID)

        sm.ScatterEvent('OnRefreshScanResults')



    def ClearIgnoredResults(self):
        self.resultsIgnored = set()
        sm.ScatterEvent('OnRefreshScanResults')



    def ClearResults(self, *targets):
        for targetID in targets:
            if targetID in self.resultsIgnored:
                self.resultsIgnored.remove(targetID)
            if targetID in self.resultsCached:
                result = self.resultsCached[targetID]
                del self.resultsCached[targetID]

        items = [ r for r in self.lastResults if r.id in targets ]
        for target in items:
            self.lastResults.remove(target)

        sm.ScatterEvent('OnRefreshScanResults')



    def IgnoreOtherResults(self, *targets):
        if self.lastResults:
            for result in self.lastResults:
                self.resultsIgnored.add(result.id)

            for targetID in targets:
                if targetID in self.resultsIgnored:
                    self.resultsIgnored.remove(targetID)

            sm.ScatterEvent('OnRefreshScanResults')



    def ShowIgnoredResult(self, targetID):
        if targetID in self.resultsIgnored:
            self.resultsIgnored.remove(targetID)
            sm.ScatterEvent('OnRefreshScanResults')




