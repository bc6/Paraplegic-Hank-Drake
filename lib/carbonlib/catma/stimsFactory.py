from catmaConfig import ATTRIB_FLAGS
from const import TYPEID_NONE
import stims
from stims import logger, TINY_TIME
from axiom import GetAttributeID
import catmaDB

def CreateAdapter(typeName, db):
    return CreateAdapterByID(db.GetTypeID(typeName), db)



def CreateAdapterByID(adapterTypeID, db):
    adapterType = db.GetTypeByID(adapterTypeID)
    if adapterTypeID not in stims.Adapter._attributeFlags:
        attributes = adapterType.GetAllValues(ATTRIB_FLAGS.MODULIZED, includeAttFlag=True)
        flags = {}
        for (attName, valueInfo,) in attributes.items():
            flags[attName] = (GetAttributeID(attName), valueInfo[1])
            attributes[attName] = valueInfo[0]

        stims.Adapter.CacheAttributeFlags(adapterTypeID, flags)
    else:
        attributes = adapterType.GetAllValues(ATTRIB_FLAGS.MODULIZED)
    fittingInfo = GetSlotAttributeValuesAll(adapterTypeID, 'slotType', db)
    adapter = stims.Adapter(adapterTypeID, fittingInfo, attributes)
    return adapter



def GetSlotAttributeValuesAll(adapterTypeID, slotAttributeName, db):
    adapterType = db.GetTypeByID(adapterTypeID)
    attributesInfo = []
    try:
        slots = adapterType.GetValue('mModuleSlots')
        slots.CacheInheritedValues()
    except catmaDB.CatmaDBError:
        return []
    slotNames = slots.GetValueNames()
    slotNames.sort()
    for slotName in slotNames:
        slotInfo = slots.GetValue(slotName)
        attrValue = slotInfo.GetValue(slotAttributeName, None)
        attributesInfo.append(attrValue)

    return attributesInfo



def GetAllSpawnedAdapterModuleType(adapterTypeID):
    db = catmaDB.GetDB()
    spawnedTypes = []
    defaultModuleTypes = GetSlotAttributeValuesAll(adapterTypeID, 'defaultModuleType', db)
    for moduleTypeID in defaultModuleTypes:
        moduleType = db.GetValueByTypeID(moduleTypeID, 'moduleType', None)
        if moduleType == 'MT_Spawn' and moduleTypeID not in spawnedTypes:
            spawnedTypes.append(moduleTypeID)

    return spawnedTypes



def GetSlotAttributeValue(adapterTypeID, slotIndex, slotAttributeName, db):
    allValues = GetSlotAttributeValuesAll(adapterTypeID, slotAttributeName, db)
    if slotIndex < len(allValues):
        return allValues[slotIndex]



def _GetAttributeModifiers(moduleType, field):
    attributeModifiers = []
    try:
        attributeModifierSet = moduleType.GetValue(field)
        attributeModifierSet.CacheInheritedValues()
    except catmaDB.CatmaDBError:
        pass
    else:
        for name in attributeModifierSet.GetValueNames():
            e = attributeModifierSet.GetValue(name)
            e = dict(((f, e.GetValue(f)) for f in stims.AttributeModifier.__slots__))
            attributeModifiers.append(stims.AttributeModifier(**e))

    return attributeModifiers



def GetModuleData(typeID, db):
    if typeID not in stims.ModuleData._cache:
        try:
            moduleType = db.GetTypeByID(typeID)
            if moduleType.HasClassName('DustModule'):
                parameters = {}
                parameters['typeID'] = typeID
                for field in stims.ModuleData._autoInitSlots:
                    parameters[field] = moduleType.GetValue(field, None)

                if not parameters['manner']:
                    parameters['manner'] = stims.MANNER_PASSIVE
                attributeModifiers = _GetAttributeModifiers(moduleType, 'modifier')
                activeAttributeModifiers = _GetAttributeModifiers(moduleType, 'activeAttributeModifiers')
                lockOnSpec = stims.dummyLockOnSpec
                if moduleType.HasClassName('DustLockOnSpec'):
                    lockOnSpec = dict(((f, moduleType.GetValue(f)) for f in stims.LockOnSpec.__slots__))
                    lockOnSpec = stims.LockOnSpec(**lockOnSpec)
            else:
                return 
            moduleData = stims.ModuleData(parameters, attributeModifiers, activeAttributeModifiers, lockOnSpec)
        except Exception as e:
            logger.exception('Failed to get module data for typeID {0}: {1}'.format(typeID, e))
            return 
        stims.ModuleData._cache[typeID] = moduleData
    moduleData = stims.ModuleData._cache[typeID]
    return moduleData



def CreateModule(typeID, db):
    logger.info('Creating module: {0}'.format(typeID))
    moduleData = GetModuleData(typeID, db)
    if moduleData:
        return stims.Module(moduleData)



def ApplyDefaultFitting(db, adapter):
    defaultModuleList = GetSlotAttributeValuesAll(adapter.typeID, 'defaultModuleType', db)
    slotIndex = 0
    for moduleTypeID in defaultModuleList:
        if moduleTypeID and moduleTypeID != TYPEID_NONE:
            newModule = CreateModule(moduleTypeID, db)
            if newModule:
                adapter.FitModule(newModule, slotIndex)
        slotIndex = slotIndex + 1




def ApplyFitting(db, adapter, moduleList, autoFitting = False):
    if autoFitting:
        modules = []
        for moduleTypeID in moduleList:
            if moduleTypeID:
                module = CreateModule(moduleTypeID, db)
                if module:
                    modules.append(module)

        adapter.AutoFitModules(modules)
        return 
    if len(moduleList) != len(adapter.slots):
        raise StimsException("ApplyFitting: Entries in 'moduleList' <%s> doesn't match number of slots on the adapter <%s>." % (moduleList, len(adapter.slots)))
    operations = []
    for (i, moduleTypeID,) in enumerate(moduleList):
        (slotType, module,) = adapter.slots[i]
        if moduleTypeID is None:
            if module:
                operations.append((None, i))
        elif module is None or module.typeID != moduleTypeID:
            newModule = CreateModule(moduleTypeID, db)
            if newModule:
                operations.append((newModule, i))

    adapter.FitModules(operations)



def GetModulePGCPUInfo(db, moduleTypeID):
    rv = {'mVICProp.amountPowerUsage': 0,
     'mVICProp.amountCpuUsage': 0}
    moduleData = GetModuleData(moduleTypeID, db)
    if moduleData:
        for modifierType in stims.MOD_ALL:
            for am in moduleData.attributeModifiers[modifierType]:
                currentValue = rv.get(am.attributeName, None)
                if currentValue is not None:
                    op = stims.MOD_OPERATION[am.modifierType]
                    currentValue = op(am.modifierValue, currentValue)
                    rv[am.attributeName] = currentValue


        return (rv['mVICProp.amountPowerUsage'], rv['mVICProp.amountCpuUsage'])
    else:
        return [None, None]



