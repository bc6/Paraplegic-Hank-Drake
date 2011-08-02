import functools
import time
import logging
logger = logging.getLogger('CORE.Stims')
from const import TYPEID_NONE
try:
    from dust.stats import MakeStimsHandleModuleCallbackContext
    from dust.stats import MakeStimsComputeBonusesContext
    from dust.stats import MakeStimsCalculateDiffsContext
except ImportError:
    import contextlib

    @contextlib.contextmanager
    def ResourceTracking(Name = None):
        yield None



    def MakeDummyContext(*args, **kwargs):
        return ResourceTracking(*args, **kwargs)


    MakeStimsHandleModuleCallbackContext = MakeStimsComputeBonusesContext = MakeStimsCalculateDiffsContext = MakeDummyContext
SLOTTYPE_VEHICLE_HIGH = 'VH'
SLOTTYPE_VEHICLE_LOW = 'VL'
SLOTTYPE_INFANTRY_HIGH = 'IH'
SLOTTYPE_INFANTRY_LOW = 'IL'
SLOTTYPE_INFANTRY_SMALL_GRENADE = 'GS'
SLOTTYPE_INFANTRY_MEDIUM_GRENADE = 'GM'
SLOTTYPE_INFANTRY_LARGE_GRENADE = 'GL'
SLOTTYPE_IMPLANT = 'I'
SLOTTYPE_HANDHELD_WEAPON = 'WE'
SLOTTYPE_SMALL_WEAPON = 'A'
SLOTTYPE_MEDIUM_WEAPON = 'B'
SLOTTYPE_LARGE_WEAPON = 'C'
SLOTTYPE_EXTRA_LARGE_WEAPON = 'D'
SLOTTYPE_LARGE_OMS = 'O'
SLOTTYPE_MEDIUM_OMS = 'M'
SLOTTYPE_SMALL_OMS = 'S'
SLOTTYPE_RESERVED = 'R'
slotTypes = {SLOTTYPE_VEHICLE_HIGH: 'Vehicle High-Powered Module',
 SLOTTYPE_VEHICLE_LOW: 'Vehicle Low-Powered Module',
 SLOTTYPE_INFANTRY_HIGH: 'Infantry High-Powered Module',
 SLOTTYPE_INFANTRY_LOW: 'Infantry Low-Powered Module',
 SLOTTYPE_INFANTRY_SMALL_GRENADE: 'Infantry Small Grenade',
 SLOTTYPE_INFANTRY_MEDIUM_GRENADE: 'Infantry Medium Grenade',
 SLOTTYPE_INFANTRY_LARGE_GRENADE: 'Infantry Large Grenade',
 SLOTTYPE_IMPLANT: 'Implant',
 SLOTTYPE_HANDHELD_WEAPON: 'Handheld Weapon',
 SLOTTYPE_SMALL_WEAPON: 'Small Weapon',
 SLOTTYPE_MEDIUM_WEAPON: 'Medium Weapon',
 SLOTTYPE_LARGE_WEAPON: 'Large Weapon',
 SLOTTYPE_EXTRA_LARGE_WEAPON: 'Extra Large Weapon',
 SLOTTYPE_LARGE_OMS: 'Large Off Map Support Module (Commander)',
 SLOTTYPE_MEDIUM_OMS: 'Medium Off Map Support Module (Squadron Leader)',
 SLOTTYPE_SMALL_OMS: 'Small Off Map Support Module (Infantry)',
 SLOTTYPE_RESERVED: 'Reserved Module'}
slotCompatibleMap = {SLOTTYPE_INFANTRY_MEDIUM_GRENADE: [SLOTTYPE_INFANTRY_SMALL_GRENADE],
 SLOTTYPE_INFANTRY_LARGE_GRENADE: [SLOTTYPE_INFANTRY_MEDIUM_GRENADE, SLOTTYPE_INFANTRY_SMALL_GRENADE]}

def IsSlotCompatible(typeOnSlot, typeOnModule):
    return typeOnModule == typeOnSlot or typeOnModule in slotCompatibleMap.get(typeOnSlot, [])


STATE_FIT = 1001
STATE_UNFIT = 1002
STATE_IDLE = 2001
STATE_ACTIVATING = 2002
STATE_PULSE_ON = 2003
STATE_PULSE_OFF = 2004
STATE_CHARGING = 2005
STATE_ALL = (STATE_FIT,
 STATE_UNFIT,
 STATE_IDLE,
 STATE_ACTIVATING,
 STATE_PULSE_ON,
 STATE_PULSE_OFF,
 STATE_CHARGING)
stateTransitionActive = {STATE_UNFIT: [STATE_FIT],
 STATE_FIT: [STATE_IDLE, STATE_UNFIT],
 STATE_IDLE: [STATE_ACTIVATING, STATE_UNFIT],
 STATE_ACTIVATING: [STATE_PULSE_ON, STATE_CHARGING],
 STATE_PULSE_ON: [STATE_PULSE_OFF, STATE_CHARGING],
 STATE_PULSE_OFF: [STATE_PULSE_ON, STATE_CHARGING],
 STATE_CHARGING: [STATE_IDLE]}
stateTransitionPassive = {STATE_UNFIT: [STATE_FIT],
 STATE_FIT: [STATE_UNFIT]}
stateNames = {STATE_FIT: 'Fit',
 STATE_UNFIT: 'Unfit',
 STATE_IDLE: 'Idle',
 STATE_ACTIVATING: 'Activating',
 STATE_PULSE_ON: 'PulseOn',
 STATE_PULSE_OFF: 'PulseOff',
 STATE_CHARGING: 'Charging'}
TINY_TIME = 0.1
MANNER_PASSIVE = 'PASSIVE'
MANNER_ACTIVE = 'ACTIVE_TRANSIENT'
MANNER_ACTIVE_DIRECT = 'ACTIVE_PERSISTENT'
MOD_MANNERS_OF_USE_ALL = (MANNER_PASSIVE, MANNER_ACTIVE, MANNER_ACTIVE_DIRECT)
MOD_MANNERS_OF_USE_ACTIVE = (MANNER_ACTIVE, MANNER_ACTIVE_DIRECT)
MOD_BASE = 'BASE'
MOD_MUL = 'MULTIPLY'
MOD_ADD = 'ADD'
MOD_ALL = (MOD_BASE, MOD_MUL, MOD_ADD)
MOD_OPERATION = {MOD_BASE: lambda modifierValue, currentValue: modifierValue,
 MOD_MUL: lambda modifierValue, currentValue: modifierValue * currentValue,
 MOD_ADD: lambda modifierValue, currentValue: modifierValue + currentValue}

class StimsException(Exception):
    pass

class StateTransitionError(RuntimeError):
    pass

class Adapter(object):
    numAdapter = 0
    __slots__ = ['sequencer',
     'typeID',
     'slots',
     'attribBase',
     'attribPassive',
     'attribActive',
     'uniqueID',
     'cppPointer',
     '_activeDirty',
     '_bonusesComputationCycles']
    _attributeFlags = {}

    def CacheAttributeFlags(typeID, flags):
        logger.info('Caching adapter attribute flags for type %s' % typeID)
        Adapter._attributeFlags[typeID] = flags



    def SelectAttributesByAttFlag(self, attFlag):
        idAndNames = []
        attributes = Adapter._attributeFlags.get(self.typeID, {})
        for (attName, info,) in attributes.iteritems():
            if info[1] & attFlag:
                idAndNames.append((info[0], attName))

        return idAndNames



    def __init__(self, typeID, fittingInfo, attributes):
        self.sequencer = None
        self.typeID = typeID
        self.cppPointer = None
        bogus = set(fittingInfo) - set(slotTypes)
        if bogus:
            raise RuntimeError("Adapter: 'fittingInfo' contains bogus slot type(s): %s" % list(bogus))
        self.slots = [ [slotType, None] for slotType in fittingInfo ]
        if not isinstance(attributes, dict):
            raise RuntimeError("Adapter: 'attributes' must be a dict")
        self.attribBase = attributes
        self.attribPassive = {}
        self.attribActive = {}
        self.uniqueID = Adapter.numAdapter
        Adapter.numAdapter += 1
        self._activeDirty = False
        self._bonusesComputationCycles = 0



    def __repr__(self):
        return "Adapter<id='%s', type='%s', slots=%s>" % (self.uniqueID, self.typeID, len(self.slots))



    def MarkActiveDirty(self):
        self._activeDirty = True



    def GetBonusesComputationCycles(self):
        return self._bonusesComputationCycles



    def _FitModule(self, module, slotIndex = None):
        if module.adapter:
            raise StimsException("_FitModule: This module already fitted. Can't be refitted")
        if slotIndex is None:
            for (i, (slotType, fitted,),) in enumerate(self.slots):
                if IsSlotCompatible(slotType, module.slotType) and fitted is None:
                    slotIndex = i
                    break

            if slotIndex is None:
                raise StimsException('_FitModule: No slot available to fit this module[%s].' % module)
        else:
            (slotType, fitted,) = self.slots[slotIndex]
            if not IsSlotCompatible(slotType, module.slotType):
                raise StimsException('_FitModule: The slot [%s:%s] is incompatible with %s.' % (slotType, slotIndex, module.slotType))
            if fitted:
                self._UnfitModule(fitted)
        self.slots[slotIndex][1] = module
        module.slotIndex = slotIndex
        module.OnFitted(self)



    def _UnfitModule(self, module):
        self.slots[module.slotIndex][1] = None
        module.OnUnfitted()



    def ClearModules(self):
        for (i, (slotType, fitted,),) in enumerate(self.slots):
            self.UnfitModule(i)




    def AutoFitModules(self, modules):
        slotsByTypeID = {}
        for (slotIndex, (slotType, module,),) in enumerate(self.slots):
            if module:
                moduleTypeID = module.typeID
                if moduleTypeID not in slotsByTypeID:
                    slotsByTypeID[moduleTypeID] = [slotIndex]
                else:
                    slotsByTypeID[moduleTypeID].append(slotIndex)

        for newModule in modules:
            if newModule.typeID in slotsByTypeID:
                del slotsByTypeID[newModule.typeID][-1]
                if not len(slotsByTypeID[newModule.typeID]):
                    del slotsByTypeID[newModule.typeID]
                continue
            try:
                self.FitModule(newModule)
            except StimsException:
                logging.root.exception('Failed to fit type %s in slot %s', newModule.typeID, newModule.slotType)

        for (moduleTypeID, slotIndexes,) in slotsByTypeID.items():
            for slotIndex in slotIndexes:
                self.UnfitModule(slotIndex)





    def FitModule(self, module, slotIndex = None):
        self.FitModules([[module, slotIndex]])
        return module



    def FitModules(self, moduleList):
        logger.info('Adapter <%s> fit modules: %s' % (self.typeID, moduleList))
        try:
            for (module, slotIndex,) in moduleList:
                if module:
                    self._FitModule(module, slotIndex)
                else:
                    self._UnfitModule(self.slots[slotIndex][1])


        finally:
            self.ComputeBonuses(MANNER_PASSIVE)




    def UnfitModule(self, slotIndex):
        module = self.slots[slotIndex][1]
        if module:
            self._UnfitModule(module)
            self.ComputeBonuses(MANNER_PASSIVE)
            return module



    def TriggerState(self, isActivate, slotIndex):
        module = self.slots[slotIndex][1]
        if not module:
            raise RuntimeError("TriggerState: There's no module in slot %s" % slotIndex)
        module.EnterState(STATE_ACTIVATING if isActivate else STATE_CHARGING)



    def HandleRepState(self, slotIndex, repState):
        module = self.slots[slotIndex][1]
        if not module:
            raise RuntimeError("HandleRepState: There's no module in slot %s" % slotIndex)
        if repState not in STATE_ALL:
            raise RuntimeError('HandleRepState: replicated state is not valid: %s' % repState)
        module.HandleRepState(repState)



    def GetSlotNum(self):
        return len(self.slots)



    def ComputeBonuses(self, manner):
        if manner == MANNER_ACTIVE:
            if not self._activeDirty:
                return 
            self._activeDirty = False
            self.attribActive.clear()
        else:
            self.attribPassive.clear()
        with MakeStimsComputeBonusesContext():
            self._bonusesComputationCycles += 1
            modules = [ mod for (_, mod,) in self.slots if mod ]
            for operator in MOD_ALL:
                for module in modules:
                    if manner == MANNER_PASSIVE:
                        modifiers = module.attributeModifiers[operator]
                        for am in modifiers:
                            attribName = am.attributeName
                            baseValue = self.attribBase[attribName]
                            passiveValue = self.attribPassive.get(attribName, baseValue)
                            newValue = module.ComputeBonus(manner, attribName, operator, passiveValue)
                            self.attribPassive[attribName] = newValue

                    elif manner == MANNER_ACTIVE:
                        if module.state != STATE_PULSE_ON:
                            continue
                        modifiers = module.activeAttributeModifiers[operator]
                        for am in modifiers:
                            attribName = am.attributeName
                            baseValue = self.attribBase[attribName]
                            passiveValue = self.attribPassive.get(attribName, baseValue)
                            activeValue = self.attribActive.get(attribName, passiveValue)
                            newValue = module.ComputeBonus(manner, attribName, operator, activeValue)
                            self.attribActive[attribName] = newValue

                    elif manner == MANNER_ACTIVE_DIRECT:
                        pass
                    else:
                        raise RuntimeError('Invalid manner: {0}'.format(manner))


            if manner == MANNER_PASSIVE:
                self.MarkActiveDirty()
                self.ComputeBonuses(MANNER_ACTIVE)



    def GetAttributeValue(self, attName):
        base = self.attribBase.get(attName, None)
        passive = self.attribPassive.get(attName, base)
        active = self.attribActive.get(attName, passive)
        return (base, passive, active)



    def GetAttributeValues(self):
        d = {}
        for attName in self.attribBase.keys():
            d[attName] = self.GetAttributeValue(attName)

        return d



    def GetFittedModuleType(self, slotIndex):
        if self.slots[slotIndex][1]:
            return self.slots[slotIndex][1].typeID
        return TYPEID_NONE



    def RemoveFromSequencer(self):
        if self.sequencer:
            self.sequencer.RemoveAdapter(self)



    def GetSlotsInfo(self):
        return self.slots



    def GetModuleList(self):
        modulesList = []
        for slot in self.slots:
            typeID = slot[1].typeID if slot[1] else TYPEID_NONE
            modulesList.append(str(typeID))

        moduleListStr = ','.join(modulesList)
        return moduleListStr



    def DbgPrint(self):
        print self
        print ''
        print 'Attributes:'
        for attName in self.attribBase.keys():
            (base, passive, active,) = self.GetAttributeValue(attName)
            print '   %s: %.1f -> %.1f = %1.f' % (attName,
             base,
             passive,
             active)

        print ''
        print 'Fitting:'
        for (slotType, module,) in self.slots:
            print '   [%s]\t%s' % (slotType, module if module else '')





def MakeRepr(obj):
    attributes = [ (k, getattr(obj, k, '<undefined>')) for k in obj.__slots__ ]
    return '{0}<{1}>'.format(obj.__class__, attributes)



class AttributeModifier(object):
    __slots__ = ['attributeName', 'modifierType', 'modifierValue']
    __repr__ = MakeRepr

    def __init__(self, **kwargs):
        for k in self.__slots__:
            setattr(self, k, kwargs[k])

        if self.modifierType not in MOD_ALL:
            raise RuntimeError("AttributeModifier: invalid 'modifierType' {0}".format(self.modifierType))




class LockOnSpec(object):
    __slots__ = ['mLockOnRequired',
     'mMinNumTargets',
     'mMaxNumTargets',
     'mPrimaryLockOnRange',
     'mLockOnAcquisitionTime']
    __repr__ = MakeRepr

    def __init__(self, **kwargs):
        for k in self.__slots__:
            setattr(self, k, kwargs[k])




dummyLockOnSpec = LockOnSpec(**dict(((k, None) for k in LockOnSpec.__slots__)))

class ModuleData(object):
    _autoInitSlots = ['manner',
     'slotType',
     'duration',
     'rechargeTime',
     'cycles',
     'activationTime',
     'pulseDuration']
    __slots__ = _autoInitSlots + ['typeID',
     'cycleDuration',
     'attributeModifiers',
     'activeAttributeModifiers',
     'lockOnSpec']
    _cache = {}

    @staticmethod
    def _Categorize(attributeModifiers):
        categorized = dict(((operator, []) for operator in MOD_ALL))
        for am in attributeModifiers:
            modifiers = categorized[am.modifierType]
            for otherAM in modifiers:
                if otherAM.attributeName == am.attributeName:
                    if am.modifierType == MOD_BASE:
                        raise RuntimeError('ModuleData: Module {0} got an attributeModifier {1} conflicting with a previous one {2} for the operator (BASE)'.format(self.typeID, am, otherAM))
                    op = MOD_OPERATION[am.modifierType]
                    otherAM.modifierValue = op(otherAM.modifierValue, am.modifierValue)
                    break
            else:
                modifiers.append(am)


        return categorized



    def __init__(self, parameters, attributeModifiers, activeAttributeModifiers, lockOnSpec):
        for (k, v,) in parameters.iteritems():
            setattr(self, k, v)

        if self.manner in MOD_MANNERS_OF_USE_ACTIVE:
            if not getattr(self, 'cycles', None):
                self.cycles = 1
                self.pulseDuration = self.duration
            self.cycleDuration = self.duration / self.cycles
        self.attributeModifiers = ModuleData._Categorize(attributeModifiers)
        self.activeAttributeModifiers = ModuleData._Categorize(activeAttributeModifiers)
        self.lockOnSpec = dummyLockOnSpec
        if self.manner not in MOD_MANNERS_OF_USE_ALL:
            raise RuntimeError("ModuleData: Module {0} with invalid 'manner' {1}".format(self.typeID, self.manner))
        if self.manner == MANNER_PASSIVE:
            for name in self.__slots__:
                if not hasattr(self, name):
                    setattr(self, name, None)

        else:
            missingParameters = [ name for name in self.__slots__ if getattr(self, name, None) is None ]
            if missingParameters:
                raise RuntimeError('ModuleData: Module {0} missing parameters {1}'.format(self.typeID, missingParameters))
        if self.slotType not in slotTypes:
            raise RuntimeError("ModuleData: Module {0} with invalid 'slotType' {1}".format(self.typeID, self.slotType))
        if self.manner in MOD_MANNERS_OF_USE_ACTIVE and self.cycleDuration < self.pulseDuration:
            logger.warn("ModuleData: Module {0} got 'pulseDuration' {1} capped to 'cycleDuration' {2}".format(self.typeID, self.pulseDuration, self.cycleDuration))
            self.pulseDuration = self.cycleDuration




class Module(object):
    __slots__ = ['_moduleData',
     'state',
     'adapter',
     'slotIndex',
     'currentCycle',
     'timeToNextState',
     '_timeStampActivation',
     '_pendingEventID']
    __repr__ = MakeRepr

    def __init__(self, moduleData):
        self._moduleData = moduleData
        self.state = STATE_UNFIT
        self.adapter = None
        self.slotIndex = None
        self.currentCycle = 0
        self.timeToNextState = None
        self._timeStampActivation = 0
        self._pendingEventID = None



    def __getattr__(self, name):
        return getattr(self._moduleData, name)



    def OnFitted(self, adapter):
        if self.adapter:
            raise StimsException("Module::OnFitted: This module already fitted. Can't be refitted")
        self.adapter = adapter
        self.EnterState(STATE_FIT)



    def OnUnfitted(self):
        self.EnterState(STATE_UNFIT)
        self.adapter = None



    def ComputeBonus(self, manner, attributeName, modifierType, currentValue):
        attributeModifiers = self.attributeModifiers if manner == MANNER_PASSIVE else self.activeAttributeModifiers
        for am in attributeModifiers[modifierType]:
            if attributeName != am.attributeName:
                continue
            op = MOD_OPERATION[modifierType]
            valueType = type(currentValue)
            return valueType(op(am.modifierValue, currentValue))

        return currentValue



    def GetTimeUntilNextState(self, currTime = None):
        diff = None
        if self.timeToNextState is not None:
            if currTime is None:
                if self.adapter.sequencer:
                    currTime = self.adapter.sequencer.currentTime
                else:
                    raise RuntimeError('Sequencer is missing so module state transition is not supported!')
            diff = self.timeToNextState - currTime
        return diff



    def GetActiveTimeTotal(self):
        return self.duration



    def GetActiveTimeLeft(self):
        if self.adapter.sequencer:
            currentTime = self.adapter.sequencer.currentTime
        else:
            raise RuntimeError('Unable to compute activeTimeLeft: sequencer is missing')
        return self.duration - max(currentTime - self._timeStampActivation, 0)



    def GetPulseOnTimeTotal(self):
        return self.pulseDuration



    def GetPulseOnTimeLeft(self):
        if self.state == STATE_PULSE_ON:
            return self.GetTimeUntilNextState()



    def _Verify(self, attributeModifiers):
        for (operator, modifiers,) in attributeModifiers.iteritems():
            verified = []
            for am in modifiers:
                if am.attributeName not in self.adapter.attribBase:
                    logger.warn("Module._Verify: Module {0} contains an attributeModifier {1} with invalid 'attributeName'".format(self.typeID, am))
                else:
                    verified.append(am)

            attributeModifiers[operator] = verified




    def _BeginState_Fit(self):
        self._Verify(self.attributeModifiers)
        self._Verify(self.activeAttributeModifiers)
        if self.manner in MOD_MANNERS_OF_USE_ACTIVE:
            self._TimedEnterState(0.01, STATE_IDLE)



    def _BeginState_Unfit(self):
        self.adapter.MarkActiveDirty()



    def _BeginState_Idle(self):
        pass



    def _BeginState_Activating(self):
        self.currentCycle = 0
        self._TimedEnterState(self.activationTime, STATE_PULSE_ON)



    def _BeginState_PulseOn(self):
        if 0 == self.currentCycle and self.adapter.sequencer:
            self._timeStampActivation = self.adapter.sequencer.currentTime
        self.currentCycle += 1
        if self.manner == MANNER_ACTIVE_DIRECT:
            if self.adapter.sequencer:
                self.adapter.sequencer.QueueDirectAttribChange(self)
        else:
            self.adapter.MarkActiveDirty()
        self._TimedEnterState(self.pulseDuration, STATE_PULSE_OFF)



    def _BeginState_PulseOff(self):
        if self.manner == MANNER_ACTIVE_DIRECT:
            pass
        else:
            self.adapter.MarkActiveDirty()
        duration = self.cycleDuration - self.pulseDuration
        self._TimedEnterState(duration, STATE_PULSE_ON if self.currentCycle < self.cycles else STATE_CHARGING)



    def _BeginState_Charging(self):
        self._TimedEnterState(self.rechargeTime, STATE_IDLE)



    def _EndState(self, stateName):
        if stateName == STATE_PULSE_ON:
            self.adapter.MarkActiveDirty()



    def HandleRepState(self, repState):
        logger.info('HandleRepState, local state <%s>, remote state <%s>' % (stateNames[self.state], stateNames[repState]))
        targetState = None
        activeStates = (STATE_ACTIVATING, STATE_PULSE_ON, STATE_PULSE_OFF)
        deactiveStates = (STATE_IDLE, STATE_CHARGING)
        if self.state in activeStates:
            if repState in deactiveStates:
                targetState = repState
        if self.state in deactiveStates:
            if repState in activeStates:
                startFullSimulation = True
                if startFullSimulation:
                    targetState = STATE_ACTIVATING
                else:
                    targetState = repState
        if targetState is not None:
            logger.info(' -> transit to state <%s>' % stateNames[targetState])
            self.EnterState(targetState, False)



    def _TimedEnterState(self, inSeconds, stateName):
        if self.adapter.sequencer:
            (self.timeToNextState, self._pendingEventID,) = self.adapter.sequencer.Schedule(inSeconds, functools.partial(self.EnterState, stateName))
        else:
            self.timeToNextState = None



    def EnterState(self, gotoState, enforceTransitionCheck = True):
        if gotoState == self.state:
            return 
        if enforceTransitionCheck:
            transitionMap = stateTransitionActive if self.manner in MOD_MANNERS_OF_USE_ACTIVE else stateTransitionPassive
            validEndStates = transitionMap[self.state]
            if gotoState not in validEndStates:
                raise StateTransitionError('Invalid transition from %s to %s' % (stateNames[self.state], stateNames[gotoState]))
        funcName = '_BeginState_%s' % stateNames[gotoState]
        func = getattr(self, funcName, None)
        if not func:
            raise RuntimeError("Couldn't find begin state function on Module: %s" % funcName)
        if not callable(func):
            raise RuntimeError('%s is not a callable' % funcName)
        if self.adapter.sequencer and self._pendingEventID is not None:
            self.adapter.sequencer.Cancel(self._pendingEventID)
        self._pendingEventID = None
        self.timeToNextState = None
        func()
        self._EndState(self.state)
        self.state = gotoState
        if self.adapter.sequencer:
            self.adapter.sequencer.QueueStateChange(self)




class Sequencer(object):

    def __init__(self):
        self.adapters = {}
        self.timeline = []
        self.cancelledEvents = []
        self.stateChanges = []
        self.directAttribChanges = []
        self.lastDiff = {}
        self.adapterCycles = {}
        self.currentTime = 0.0
        self.nextEventID = 0



    def FlushAll(self):
        for adapter in self.adapters.itervalues():
            adapter.sequencer = None

        self.adapters.clear()
        self.timeline = []
        self.stateChanges = []
        self.directAttribChanges = []
        self.lastDiff.clear()
        self.adapterCycles.clear()
        self.nextEventID = 0



    def UpdateTime(self, currentTime):
        self.currentTime = currentTime
        with MakeStimsHandleModuleCallbackContext():
            newList = []
            for (eventID, dueTime, callback,) in self.timeline:
                if eventID not in self.cancelledEvents:
                    if dueTime < currentTime:
                        try:
                            callback()
                        except Exception as e:
                            logger.exception(e)
                    else:
                        newList.append((eventID, dueTime, callback))

            self.timeline = newList
            self.cancelledEvents = []
        attribChanges = []
        for adapter in self.adapters.itervalues():
            adapter.ComputeBonuses(MANNER_ACTIVE)
            attributeFlags = Adapter._attributeFlags.get(adapter.typeID, {})
            currentCycle = adapter.GetBonusesComputationCycles()
            lastCycle = self.adapterCycles.get(adapter, None)
            if currentCycle != lastCycle:
                self.adapterCycles[adapter] = currentCycle
                with MakeStimsCalculateDiffsContext():
                    if adapter not in self.lastDiff:
                        self.lastDiff[adapter] = {}
                    lastDiff = self.lastDiff[adapter]
                    changes = []
                    for attName in adapter.attribBase.iterkeys():
                        (attID, attFlag,) = attributeFlags.get(attName, (0, 0))
                        curr = adapter.attribPassive.get(attName, None)
                        curr = adapter.attribActive.get(attName, curr)
                        last = lastDiff.get(attName, None)
                        if curr is not None and last is not None:
                            if curr != last:
                                lastDiff[attName] = curr
                                changes.append((attName,
                                 curr,
                                 attID,
                                 attFlag))
                        elif curr is not None:
                            lastDiff[attName] = curr
                            changes.append((attName,
                             curr,
                             attID,
                             attFlag))
                        elif last is not None:
                            del lastDiff[attName]
                            changes.append((attName,
                             adapter.attribBase[attName],
                             attID,
                             attFlag))

                    attribChanges.append((adapter, changes))

        stateChanges = self.stateChanges
        directAttribChanges = self.directAttribChanges
        self.stateChanges = []
        self.directAttribChanges = []
        return (stateChanges, attribChanges, directAttribChanges)



    def QueueStateChange(self, module, state = None):
        if state is None:
            state = module.state
        change = (self.currentTime,
         module.adapter,
         module,
         state,
         module.currentCycle)
        self.stateChanges.append(change)



    def QueueDirectAttribChange(self, module):
        rawAMs = []
        attributeFlags = Adapter._attributeFlags.get(module.adapter.typeID, {})
        for modifiers in module.activeAttributeModifiers.itervalues():
            for am in modifiers:
                (attribID, attribFlag,) = attributeFlags.get(am.attributeName, (0, 0))
                rawAMs.append((am.attributeName,
                 MOD_ALL.index(am.modifierType),
                 am.modifierValue,
                 attribID,
                 attribFlag))


        change = (self.currentTime,
         module.adapter,
         module,
         rawAMs)
        self.directAttribChanges.append(change)



    def AddAdapter(self, adapter):
        if adapter.uniqueID in self.adapters:
            raise RuntimeError('Adapter with ID %s already exists' % adapter.uniqueID)
        if adapter.sequencer:
            raise RuntimeError('Adapter has already registered with a sequencer')
        self.adapters[adapter.uniqueID] = adapter
        adapter.sequencer = self



    def Schedule(self, inSeconds, event):
        if not callable(event):
            raise RuntimeError('%s is not callable' % event)
        dueTime = self.currentTime + inSeconds
        oldID = self.nextEventID
        self.timeline.append((self.nextEventID, dueTime, event))
        self.nextEventID += 1
        return (dueTime, oldID)



    def Cancel(self, eventID):
        self.cancelledEvents.append(eventID)



    def GetAdapterByID(self, adapterID):
        return self.adapters.get(adapterID, None)



    def RemoveAdapter(self, adapter):
        if adapter.uniqueID not in self.adapters:
            raise RuntimeError('Adapter with ID %s is not registered with this sequencer' % adapter.uniqueID)
        del self.adapters[adapter.uniqueID]
        adapter.sequencer = None
        if adapter in self.lastDiff:
            del self.lastDiff[adapter]
        if adapter in self.adapterCycles:
            del self.adapterCycles[adapter]




