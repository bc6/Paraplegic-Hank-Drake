from __future__ import with_statement
import service
import destiny
import effects
import uthread
import base
import blue
import util
import blue.heapq as heapq
import sys
import log
import locks
SECOND = 10000000L
FX_REPEAT = 0
FX_ONESHOT = 1
FX_TOGGLE = 2
FX_GUIDS = ['effects.AnchorDrop',
 'effects.AnchorLift',
 'effects.ArmorRepair',
 'effects.Barrage',
 'effects.CargoScan',
 'effects.Cloak',
 'effects.Cloaking',
 'effects.CloakNoAmim',
 'effects.CloakRegardless',
 'effects.CloudMining',
 'effects.DecloakWave',
 'effects.ECMBurst',
 'effects.ElectronicAttributeModifyActivate',
 'effects.ElectronicAttributeModifyTarget',
 'effects.EMPWave',
 'effects.EMPWaveGrid',
 'effects.EnergyDestabilization',
 'effects.EnergyTransfer',
 'effects.EnergyVampire',
 'effects.GateActivity',
 'effects.WormholeActivity',
 'effects.GenericEffect',
 'effects.HybridFired',
 'effects.Jettison',
 'effects.JumpDriveIn',
 'effects.JumpDriveOut',
 'effects.JumpDriveInBO',
 'effects.JumpDriveOutBO',
 'effects.JumpIn',
 'effects.JumpOut',
 'effects.JumpOutWormhole',
 'effects.JumpPortal',
 'effects.JumpPortalBO',
 'effects.Laser',
 'effects.Mining',
 'effects.MissileDeployment',
 'effects.ModifyShieldResonance',
 'effects.ModifyTargetSpeed',
 'effects.ProjectileFired',
 'effects.ProjectileFiredForEntities',
 'effects.RemoteArmourRepair',
 'effects.RemoteECM',
 'effects.ScanStrengthBonusActivate',
 'effects.ScanStrengthBonusTarget',
 'effects.ShieldBoosting',
 'effects.ShieldTransfer',
 'effects.ShipEffect',
 'effects.ShipScan',
 'effects.SiegeMode',
 'effects.SpeedBoost',
 'effects.StandardWeapon',
 'effects.StretchEffect',
 'effects.StructureOffline',
 'effects.StructureOnline',
 'effects.StructureOnlined',
 'effects.StructureRepair',
 'effects.SurveyScan',
 'effects.Target_paint',
 'effects.TargetPaint',
 'effects.TargetScan',
 'effects.TorpedoDeployment',
 'effects.TriageMode',
 'effects.TurretWeaponRangeTrackingSpeedMultiplyActivate',
 'effects.TurretWeaponRangeTrackingSpeedMultiplyTarget',
 'effects.Uncloak',
 'effects.WarpDisruptFieldGenerating',
 'effects.Warping',
 'effects.WarpScramble',
 'effects.SuperWeaponAmarr',
 'effects.SuperWeaponCaldari',
 'effects.SuperWeaponGallente',
 'effects.SuperWeaponMinmatar']
FX_TURRET_EFFECT_GUIDS = ['effects.Laser',
 'effects.ProjectileFiredForEntities',
 'effects.ProjectileFired',
 'effects.HybridFiredeffects.TractorBeam',
 'effects.Salvaging']
FX_PROTECTED_EFFECT_GUIDS = ['effects.GenericEffect',
 'effects.GateActivity',
 'effects.WormholeActivity',
 'effects.JumpDriveIn',
 'effects.JumpDriveOut',
 'effects.JumpDriveInBO',
 'effects.JumpDriveOutBO',
 'effects.JumpIn',
 'effects.JumpOut',
 'effects.JumpOutWormhole',
 'effects.Warping',
 'effects.Cloaking',
 'effects.Uncloak',
 'effects.Cloak',
 'effects.CloakNoAmim',
 'effects.CloakRegardless',
 'effects.StructureOffline',
 'effects.StructureOnlined',
 'effects.AnchorDrop',
 'effects.AnchorLift',
 'effects.SiegeMode',
 'effects.TriageMode',
 'effects.WarpDisruptFieldGenerating',
 'effects.WarpScramble']
FX_LONG_ONESHOT_GUIDS = ['effects.SuperWeaponAmarr',
 'effects.SuperWeaponCaldari',
 'effects.SuperWeaponGallente',
 'effects.SuperWeaponMinmatar']

class Trigger(util.KeyVal):
    __guid__ = 'util.Trigger'

    def __le__(self, other):
        return self.stamp <= other.stamp



    def __eq__(self, other):
        return self.shipID == other.shipID and self.moduleID == other.moduleID and self.targetID == other.targetID and self.guid == other.guid




class Activation():

    def __init__(self, broker):
        self.triggers = []
        self.effect = None
        self.stamp = -1
        self.duration = -1
        self.broker = broker
        self.key = None
        self.isOn = False



    def __le__(self, other):
        return self.stamp <= other.stamp



    def AddTrigger(self, trigger):
        for t in self.triggers:
            if trigger.moduleID == t.moduleID:
                sm.services['FxSequencer'].LogWarn('Activation: Duplicate Activations for a Module')
                return 

        heapq.heappush(self.triggers, trigger)
        stampUpdated = self.UpdateRepeatTime()
        if self.effect is None:
            try:
                self.effect = CreateInstance(trigger.guid, (trigger,))
            except:
                self.effect = CreateInstance('effects.GenericEffect', (trigger,))
                import traceback
                traceback.print_exc()
                sys.exc_clear()
            if self.effect.__blockingIO__:
                uthread.worker('FXSequencer::PrepareAndAddBlockingIO', self.PrepareAndStart)
            else:
                self.PrepareAndStart()
            self.isOn = True
        return stampUpdated



    def PrepareAndStart(self):
        try:
            self.effect.Prepare()
            self.effect.Start(self.duration)
        except:
            log.LogException()
            sys.exc_clear()



    def RemoveTrigger(self, trigger):
        try:
            ix = self.triggers.index(trigger)
        except ValueError:
            ix = -1
        if ix >= 0:
            del self.triggers[ix]
            heapq.heapify(self.triggers)
            self.PurgeTriggers()
            return self.UpdateRepeatTime()
        self.broker.LogError('Activation::RemoveTrigger: trigger not found')



    def UpdateRepeatTime(self):
        lastTime = -1
        candidate = None
        for trigger in self.triggers:
            if trigger.stamp > lastTime:
                lastTime = trigger.stamp
                candidate = trigger

        if candidate is None:
            return -1
        now = blue.os.GetSimTime()
        wholeRepeatsLeft = long((candidate.stamp - now) / (candidate.duration * SECOND / 1000.0))
        if wholeRepeatsLeft == candidate.repeat:
            newStamp = candidate.stamp - (wholeRepeatsLeft - 1) * long(candidate.duration * SECOND / 1000.0)
        else:
            newStamp = candidate.stamp - wholeRepeatsLeft * long(candidate.duration * SECOND / 1000.0)
        if newStamp == self.stamp:
            return 0
        self.stamp = newStamp
        self.duration = candidate.duration
        return 1



    def Repeat(self):
        if self.effect is None:
            raise RuntimeError('Activation::Repeat: No effect defined')
        stampUpdated = self.PurgeTriggers()
        if not self.triggers:
            self.Stop()
            return -1
        if not self.isOn:
            return stampUpdated
        try:
            self.effect.Repeat(self.duration)
        except:
            log.LogException()
            sys.exc_clear()
        return stampUpdated



    def Stop(self):
        if not self.isOn:
            return 
        if self.effect is None:
            raise RuntimeError('Activation::Stop: No effect defined')
        try:
            self.effect.Stop()
        except:
            log.LogException()
            sys.exc_clear()
        self.isOn = False



    def PurgeTriggers(self):
        now = blue.os.GetSimTime()
        changes = False
        while self.triggers and self.triggers[0].stamp <= now:
            changes = True
            heapq.heappop(self.triggers)

        return self.UpdateRepeatTime()



    def GetBalls(self):
        if self.effect is None:
            raise RuntimeError('Activation has no effect')
        return self.effect.GetBalls()



    def GetName(self):
        if self.triggers:
            return self.triggers[0].guid
        else:
            return 'unknown'




class FxSequencer(service.Service):
    __guid__ = 'svc.FxSequencer'
    __exportedcalls__ = {'ClearAll': [],
     'NotifyModelLoaded': [],
     'EnableGuids': [],
     'DisableGuids': [],
     'GetDisabledGuids': []}
    __notifyevents__ = ['OnSpecialFX', 'DoBallRemove']
    __dependencies__ = ['michelle']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.activations = {}
        self.stopCandidates = []
        self.ballRegister = {}
        self.delayedtriggers = {}
        self.killLoop = True
        self.sequencerTasklet = None
        self.disabledGuids = {}



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.lock = locks.RLock()
        self.disabledGuids = settings.user.ui.Get('disabledGuids', {})
        self.sequencerTasklet = uthread.new(self.SequencerLoop)
        self.sequencerTasklet.context = 'FxSequencer::SequencerLoop'
        if settings.user.ui.Get('turretsEnabled', 1):
            self.EnableGuids(FX_TURRET_EFFECT_GUIDS)
        else:
            self.DisableGuids(FX_TURRET_EFFECT_GUIDS)
        candidateEffects = []
        for guid in FX_GUIDS:
            if guid not in FX_TURRET_EFFECT_GUIDS and guid not in FX_PROTECTED_EFFECT_GUIDS:
                candidateEffects.append(guid)

        if settings.user.ui.Get('effectsEnabled', 1):
            self.EnableGuids(candidateEffects)
        else:
            self.DisableGuids(candidateEffects)



    def Stop(self, ms):
        service.Service.Stop(self)
        self.killLoop = True
        blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, 0, -1)
        self.sequencerTasklet = None



    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        if start == 1 and guid in self.disabledGuids:
            return 
        if startTime is not None and guid in FX_LONG_ONESHOT_GUIDS:
            now = blue.os.GetSimTime()
            if now - startTime > 150000000:
                return 
        trigger = Trigger(shipID=shipID, moduleID=moduleID, moduleTypeID=moduleTypeID, targetID=targetID, otherTypeID=otherTypeID, area=area, guid=guid, isOffensive=isOffensive, duration=duration, repeat=repeat, startTime=startTime, graphicInfo=graphicInfo)
        if trigger.repeat is None or trigger.repeat <= 0:
            trigger.repeat = 1
        else:
            trigger.repeat += 1
        if guid is None:
            self.LogWarn('FxSequencer::OnSpecialFx: No guid in trigger for moduleTypeID', moduleTypeID, 'and graphicInfo', graphicInfo)
            return 
        splitGuid = guid.split('.')
        if len(splitGuid) != 2:
            self.LogInfo('FxSequencer::OnSpecialFx: No guid in trigger')
            return 
        niceName = guid.split('.')[1]
        if shipID == session.shipid:
            ship = 'for myself'
        elif util.IsFullLogging():
            ship = 'for ship: %s' % shipID
        else:
            ship = 'for another ship'
        if start == 1:
            if active == 0:
                self.LogInfo('FxSequencer::OnSpecialFX: Got ONE-SHOT event:', niceName, ship, '[', moduleID, '] with duration:', duration)
            if trigger.repeat is not None and trigger.repeat > 0:
                self.LogInfo('Starting REPEAT event:', niceName, ship, '[', moduleID, '] with duration:', duration / 1000.0, 'and repeat:', trigger.repeat)
                self.AddTrigger(trigger)
            else:
                self.LogInfo('FxSequencer::OnSpecialFX: Starting TOGGLE event:', niceName, ship, '[', moduleID, ']')
            if targetID is not None:
                if targetID == session.shipid:
                    target = 'myself'
                else:
                    target = targetID
                self.LogInfo('targeted at:', target, 'and is', ['not', ''][isOffensive], 'offensive')
        else:
            self.RemoveTrigger(trigger)
            self.LogInfo('FxSequencer::OnSpecialFX: Stopping', niceName, 'for ship:', ship, 'and module:', moduleID)



    def EnableGuids(self, guids):
        for guid in guids:
            if guid in self.disabledGuids:
                del self.disabledGuids[guid]

        settings.user.ui.Set('disabledGuids', self.disabledGuids)
        self.LogInfo('FxSequencer::EnableGuids', guids, ' Current disabled guids:', self.disabledGuids)



    def DisableGuids(self, guids):
        for guid in guids:
            if guid not in self.disabledGuids and guid not in FX_PROTECTED_EFFECT_GUIDS:
                self.disabledGuids[guid] = None

        settings.user.ui.Set('disabledGuids', self.disabledGuids)
        self.LogInfo('FxSequencer::DisableGuids', guids, ' Current disabled guids:', self.disabledGuids)



    def GetDisabledGuids(self):
        return self.disabledGuids



    def GetClassObject(self, guid):
        (_FxSequencer__module, _FxSequencer__class,) = guid.split('.')
        module = __import__(_FxSequencer__module)
        klass = getattr(module, _FxSequencer__class, getattr(module, 'GenericEffect'))
        if klass.__guid__.endswith('GenericEffect'):
            self.LogError('Effect GUID ', guid, ' not found.')
        return klass



    def AddTrigger(self, trigger):
        with self.lock:
            self.LogInfo('\tFxSequencer::AddTrigger: Entering')
            shipBall = None
            targetBall = None
            if trigger.shipID is not None:
                shipBall = self.michelle.GetBall(trigger.shipID)
            if trigger.targetID is not None:
                targetBall = self.michelle.GetBall(trigger.targetID)
            if shipBall is None:
                self.LogWarn('\tFxSequencer::AddTrigger: ship not in ballpark. Trigger ignored')
                return 
            if getattr(shipBall, '__guid__', '') == 'spaceObject.PlayerOwnedStructure' and getattr(trigger, 'moduleID', None) is not None:
                trigger.shipID = trigger.moduleID
            if trigger.targetID is not None and targetBall is None:
                self.LogWarn('\tFxSequencer::AddTrigger: target not in ballpark. Trigger ignored')
                return 
            if getattr(shipBall, 'model', None) is None:
                self.LogWarn('\tFxSequencer::AddTrigger: ship model not loaded. Trigger delayed', trigger.shipID)
                if trigger.shipID in self.delayedtriggers:
                    self.delayedtriggers[trigger.shipID].append(trigger)
                else:
                    self.delayedtriggers[trigger.shipID] = [trigger]
                return 
            if trigger.targetID is not None and getattr(targetBall, 'model', None) is None:
                self.LogWarn('\tFxSequencer::AddTrigger: target ship model not loaded. Trigger delayed', trigger.targetID)
                if trigger.targetID in self.delayedtriggers:
                    self.delayedtriggers[trigger.targetID].append(trigger)
                else:
                    self.delayedtriggers[trigger.targetID] = [trigger]
                return 
            klass = self.GetClassObject(trigger.guid)
            if klass is None:
                return 
            key = klass._Key(trigger)
            if trigger.duration is None or trigger.duration <= 0.0:
                trigger.duration = klass._GetDuration()
            if trigger.repeat is None or trigger.repeat == 0:
                trigger.repeat = 1
            trigger.__dict__['stamp'] = blue.os.GetSimTime() + long(trigger.duration * trigger.repeat / 1000.0 * SECOND)
            if key in self.activations and not klass.__guid__ == 'effects.Uncloak':
                activation = self.activations[key]
                activation.AddTrigger(trigger)
            else:
                self.AddActivation(trigger, key)
        self.LogInfo('\tFxSequencer::AddTrigger: Done')



    def RemoveTrigger(self, trigger):
        self.LogInfo('\tFxSequencer::RemoveTrigger: Entering')
        klass = self.GetClassObject(trigger.guid)
        if klass is None:
            self.LogError('\tFxSequencer::RemoveTrigger: Could not remove trigger, None klass')
            return 
        shipBall = None
        if trigger.shipID is not None:
            shipBall = self.michelle.GetBall(trigger.shipID)
        if getattr(shipBall, '__guid__', '') == 'spaceObject.PlayerOwnedStructure' and getattr(trigger, 'moduleID', None) is not None:
            trigger.shipID = trigger.moduleID
        key = klass._Key(trigger)
        if key not in self.activations:
            self.LogInfo('\tFxSequencer::RemoveTrigger: Trigger not found')
            return 
        activation = self.activations[key]
        updateTime = activation.RemoveTrigger(trigger)
        if updateTime == -1:
            self.LogInfo('\tFxSequencer::RemoveTrigger: Activation empty. Deleting it.')
            self.RemoveActivation(activation, fromSequencer=True)
        self.LogInfo('\tFxSequencer::RemoveTrigger:', trigger.guid, 'Done')



    def SequencerLoop(self):
        self.killLoop = False
        reason = None
        self.LogInfo('FxSequencer: Sequencer loop starting')
        while not getattr(self, 'killLoop', True):
            self.CheckForStopCandidates()
            now = blue.os.GetSimTime()
            if self.stopCandidates:
                wakeupTime = self.stopCandidates[0].stamp
            else:
                wakeupTime = blue.os.GetSimTime() + 60 * SECOND
            reason = blue.pyos.synchro.SleepUntilSim(wakeupTime)

        self.LogInfo('FxSequencer: Sequencer loop terminated with reason', reason)



    def CheckForStopCandidates(self):
        now = blue.os.GetSimTime()
        while self.stopCandidates and self.stopCandidates[0].stamp <= now:
            blue.pyos.BeNice()
            activation = heapq.heappop(self.stopCandidates)
            state = activation.Repeat()
            if state == -1:
                self.LogInfo('FxSequencer::CheckForStopCandidates: activation expired')
                self.RemoveActivation(activation)
            else:
                heapq.heappush(self.stopCandidates, activation)
            now = blue.os.GetSimTime()




    def DoBallRemove(self, ball, slimItem, terminal):
        self.RemoveAllBallActivations(ball.id)



    def AddActivation(self, trigger, key = None):
        if key is None:
            klass = self.GetClassObject(trigger.guid)
            key = klass._Key(trigger)
        activation = Activation(self)
        activation.key = key
        self.activations[key] = activation
        activation.AddTrigger(trigger)
        self.AddActivationToBallRegister(activation)
        self.AddActivationToSequencer(activation)



    def AddActivationToSequencer(self, activation):
        currentStopTime = activation.stamp
        reschedule = True
        if self.stopCandidates:
            if self.stopCandidates[0].stamp <= currentStopTime:
                reschedule = False
        heapq.heappush(self.stopCandidates, activation)
        if reschedule:
            try:
                self.LogInfo('\t\tAddActivationToSequencer: just going for some rescheduling here')
                blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, currentStopTime)
            except:
                self.LogInfo('\t\tAddActivationToSequencer: Activation rescedule failed, sequencer will wake up by itself')
                sys.exc_clear()
        self.LogInfo('\t\tAddActivationToSequencer: Activation added')



    def RemoveActivation(self, activation, fromSequencer = False):
        niceName = activation.GetName()
        activation.Stop()
        if activation.key in self.activations:
            del self.activations[activation.key]
        self.RemoveActivationFromBallRegister(activation)
        if fromSequencer:
            self.RemoveActivationFromSequencer(activation)
        self.LogInfo('FxSequencer::RemoveActivation:', niceName, 'activation removed.', len(self.activations), 'remaining')



    def RemoveActivationFromSequencer(self, activation):
        found = True
        try:
            self.stopCandidates.remove(activation)
        except:
            found = False
            sys.exc_clear()
        if found:
            heapq.heapify(self.stopCandidates)
            try:
                if self.stopCandidates:
                    blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, self.stopCandidates[0].stamp)
                else:
                    blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, blue.os.GetSimTime() + 60 * SECOND)
            except:
                pass
            self.LogInfo('RemoveActivationFromSequencer:', activation)



    def ClearAll(self):
        self.LogInfo('FxSequencer::ClearAll')
        for activation in self.activations.values():
            self.RemoveActivation(activation, fromSequencer=True)

        if len(self.delayedtriggers):
            self.LogWarn('FxSequencer::ClearAll: Model Loaded notifications never came through?')
            self.delayedtriggers = {}
        if len(self.stopCandidates) or len(self.activations) or len(self.ballRegister):
            self.LogWarn('FxSequencer::ClearAll: Incomplete reset')



    def NotifyModelLoaded(self, ballID):
        if ballID in self.delayedtriggers:
            initiateTriggers = self.delayedtriggers[ballID]
            self.LogInfo('FxSequencer::NotifyModelLoaded', ballID, 'initiating', len(initiateTriggers), 'triggers')
            del self.delayedtriggers[ballID]
            for trigger in initiateTriggers:
                self.AddTrigger(trigger)




    def GetAllBallActivations(self, ballID):
        if ballID in self.ballRegister:
            return self.ballRegister[ballID]
        return []



    def RemoveAllBallActivations(self, ballID):
        self.LogInfo('FxSequencer::RemoveAllBallActivations for ball', ballID)
        if ballID in self.ballRegister:
            for activation in self.ballRegister[ballID][:]:
                self.RemoveActivation(activation, fromSequencer=True)




    def AddActivationToBallRegister(self, activation):
        for ballID in activation.GetBalls():
            if ballID in self.ballRegister:
                self.ballRegister[ballID].append(activation)
            else:
                self.ballRegister[ballID] = [activation]




    def RemoveActivationFromBallRegister(self, activation):
        for ballID in activation.GetBalls():
            if ballID in self.ballRegister:
                try:
                    self.ballRegister[ballID].remove(activation)
                except ValueError:
                    pass
                if len(self.ballRegister[ballID]) == 0:
                    del self.ballRegister[ballID]




exports = {'FxSequencer.fxGuids': FX_GUIDS,
 'FxSequencer.fxTurretGuids': FX_TURRET_EFFECT_GUIDS,
 'FxSequencer.fxProtectedGuids': FX_PROTECTED_EFFECT_GUIDS}

