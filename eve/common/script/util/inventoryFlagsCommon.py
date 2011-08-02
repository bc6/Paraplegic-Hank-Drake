import util
import const
inventoryFlagData = {const.flagCargo: {'name': mls.UI_GENERIC_CARGO,
                   'openCommand': mls.UI_CMD_OPENCARGO,
                   'attribute': const.attributeCapacity,
                   'allowCategories': None,
                   'allowGroups': None,
                   'blockGroups': None,
                   'allowTypes': None,
                   'blockTypes': None},
 const.flagDroneBay: {'name': mls.UI_GENERIC_DRONEBAY,
                      'openCommand': mls.UI_CMD_OPENDRONEBAY,
                      'attribute': const.attributeDroneCapacity,
                      'allowCategories': (const.categoryDrone,),
                      'allowGroups': None,
                      'blockGroups': None,
                      'allowTypes': None,
                      'blockTypes': None},
 const.flagShipHangar: {'name': mls.UI_SHIPMAINTENANCEBAY,
                        'openCommand': mls.UI_CMD_OPENSHIPMAINTENANCEBAY,
                        'attribute': const.attributeShipMaintenanceBayCapacity,
                        'allowCategories': (const.categoryShip,),
                        'allowGroups': None,
                        'blockGroups': (const.groupCapsule,),
                        'allowTypes': None,
                        'blockTypes': None},
 const.flagSpecializedFuelBay: {'name': mls.UI_GENERIC_FUELBAY,
                                'openCommand': mls.UI_CMD_OPENFUELBAY,
                                'attribute': const.attributeSpecialFuelBayCapacity,
                                'allowCategories': None,
                                'blockCategories': None,
                                'allowGroups': (const.groupIceProduct,),
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedOreHold: {'name': mls.UI_GENERIC_OREHOLD,
                                'openCommand': mls.UI_CMD_OPENOREHOLD,
                                'attribute': const.attributeSpecialOreHoldCapacity,
                                'allowCategories': (const.categoryAsteroid,),
                                'blockCategories': None,
                                'allowGroups': None,
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedGasHold: {'name': mls.UI_GENERIC_GASHOLD,
                                'openCommand': mls.UI_CMD_OPENGASHOLD,
                                'attribute': const.attributeSpecialGasHoldCapacity,
                                'allowCategories': None,
                                'blockCategories': None,
                                'allowGroups': (const.groupHarvestableCloud,),
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedMineralHold: {'name': mls.UI_GENERIC_MINERALHOLD,
                                    'openCommand': mls.UI_CMD_OPENMINERALHOLD,
                                    'attribute': const.attributeSpecialMineralHoldCapacity,
                                    'allowCategories': None,
                                    'blockCategories': None,
                                    'allowGroups': (const.groupMineral,),
                                    'blockGroups': None,
                                    'allowTypes': None,
                                    'blockTypes': None},
 const.flagSpecializedSalvageHold: {'name': mls.UI_GENERIC_SALVAGEHOLD,
                                    'openCommand': mls.UI_CMD_OPENSALVAGEHOLD,
                                    'attribute': const.attributeSpecialSalvageHoldCapacity,
                                    'allowCategories': None,
                                    'blockCategories': None,
                                    'allowGroups': (const.groupAncientSalvage, const.groupSalvagedMaterials, const.groupRefinables),
                                    'blockGroups': None,
                                    'allowTypes': None,
                                    'blockTypes': None},
 const.flagSpecializedShipHold: {'name': mls.UI_GENERIC_SHIPHOLD,
                                 'openCommand': mls.UI_CMD_OPENSHIPHOLD,
                                 'attribute': const.attributeSpecialShipHoldCapacity,
                                 'allowCategories': (const.categoryShip,),
                                 'blockCategories': None,
                                 'allowGroups': None,
                                 'blockGroups': None,
                                 'allowTypes': None,
                                 'blockTypes': None},
 const.flagSpecializedSmallShipHold: {'name': mls.UI_GENERIC_SMALLSHIPHOLD,
                                      'openCommand': mls.UI_CMD_OPENSMALLSHIPHOLD,
                                      'attribute': const.attributeSpecialSmallShipHoldCapacity,
                                      'allowCategories': None,
                                      'blockCategories': None,
                                      'allowGroups': (const.groupFrigate,
                                                      const.groupAssaultShip,
                                                      const.groupDestroyer,
                                                      const.groupInterdictor,
                                                      const.groupInterceptor,
                                                      const.groupCovertOps,
                                                      const.groupElectronicAttackShips,
                                                      const.groupStealthBomber),
                                      'blockGroups': None,
                                      'allowTypes': None,
                                      'blockTypes': None},
 const.flagSpecializedMediumShipHold: {'name': mls.UI_GENERIC_MEDIUMSHIPHOLD,
                                       'openCommand': mls.UI_CMD_OPENMEDIUMSHIPHOLD,
                                       'attribute': const.attributeSpecialMediumShipHoldCapacity,
                                       'allowCategories': None,
                                       'blockCategories': None,
                                       'allowGroups': (const.groupCruiser,
                                                       const.groupCombatReconShip,
                                                       const.groupCommandShip,
                                                       const.groupHeavyAssaultShip,
                                                       const.groupHeavyInterdictors,
                                                       const.groupLogistics,
                                                       const.groupStrategicCruiser,
                                                       const.groupBattlecruiser,
                                                       const.groupForceReconShip),
                                       'blockGroups': None,
                                       'allowTypes': None,
                                       'blockTypes': None},
 const.flagSpecializedLargeShipHold: {'name': mls.UI_GENERIC_LARGESHIPHOLD,
                                      'openCommand': mls.UI_CMD_OPENLARGESHIPHOLD,
                                      'attribute': const.attributeSpecialLargeShipHoldCapacity,
                                      'allowCategories': None,
                                      'blockCategories': None,
                                      'allowGroups': (const.groupBattleship, const.groupBlackOps, const.groupMarauders),
                                      'blockGroups': None,
                                      'allowTypes': None,
                                      'blockTypes': None},
 const.flagSpecializedIndustrialShipHold: {'name': mls.UI_GENERIC_INDUSTRIALSHIPHOLD,
                                           'openCommand': mls.UI_CMD_OPENINDUSTRIALSHIPHOLD,
                                           'attribute': const.attributeSpecialIndustrialShipHoldCapacity,
                                           'allowCategories': None,
                                           'blockCategories': None,
                                           'allowGroups': (const.groupIndustrial,
                                                           const.groupExhumer,
                                                           const.groupMiningBarge,
                                                           const.groupTransportShip),
                                           'blockGroups': None,
                                           'allowTypes': None,
                                           'blockTypes': None},
 const.flagSpecializedAmmoHold: {'name': mls.UI_GENERIC_AMMOHOLD,
                                 'openCommand': mls.UI_CMD_OPENAMMOHOLD,
                                 'attribute': const.attributeSpecialAmmoHoldCapacity,
                                 'allowCategories': (const.categoryCharge,),
                                 'blockCategories': None,
                                 'allowGroups': None,
                                 'blockGroups': None,
                                 'allowTypes': None,
                                 'blockTypes': None},
 const.flagSpecializedCommandCenterHold: {'name': mls.UI_GENERIC_COMMANDCENTERHOLD,
                                          'openCommand': mls.UI_CMD_OPENCOMMANDCENTERHOLD,
                                          'attribute': const.attributeSpecialCommandCenterHoldCapacity,
                                          'allowCategories': None,
                                          'blockCategories': None,
                                          'allowGroups': (const.groupCommandPins,),
                                          'blockGroups': None,
                                          'allowTypes': None,
                                          'blockTypes': None},
 const.flagSpecializedPlanetaryCommoditiesHold: {'name': mls.UI_GENERIC_PLANETARYCOMMODITIESHOLD,
                                                 'openCommand': mls.UI_CMD_OPENPLANETARYCOMMODITIESHOLD,
                                                 'attribute': const.attributeSpecialPlanetaryCommoditiesHoldCapacity,
                                                 'allowCategories': (const.categoryPlanetaryCommodities, const.categoryPlanetaryResources),
                                                 'blockCategories': None,
                                                 'allowGroups': None,
                                                 'blockGroups': None,
                                                 'allowTypes': (const.typeWater, const.typeOxygen),
                                                 'blockTypes': None}}

def ShouldAllowAdd(flag, categoryID, groupID, typeID):
    if flag not in inventoryFlagData:
        return 
    flagData = inventoryFlagData[flag]
    errorTuple = None
    useAllow = True
    if flagData['allowCategories'] is not None:
        if categoryID in flagData['allowCategories']:
            useAllow = False
        else:
            errorTuple = (CATID, categoryID)
    if useAllow:
        if flagData['allowGroups'] is not None:
            if groupID in flagData['allowGroups']:
                errorTuple = None
                useAllow = False
            else:
                errorTuple = (GROUPID, groupID)
                useAllow = True
    elif flagData['blockGroups'] is not None:
        if groupID in flagData['blockGroups']:
            errorTuple = (GROUPID, groupID)
            useAllow = True
        else:
            errorTuple = None
            useAllow = False
    if useAllow:
        if flagData['allowTypes'] is not None:
            if typeID in flagData['allowTypes']:
                errorTuple = None
            else:
                errorTuple = (TYPEID, typeID)
    elif flagData['blockTypes'] is not None:
        if typeID in flagData['blockTypes']:
            errorTuple = (TYPEID, typeID)
        else:
            errorTuple = None
    return errorTuple


autoConsumeTypes = {}
autoConsumeGroups = {const.groupIceProduct: (const.flagSpecializedFuelBay,)}
autoConsumeCategories = {}

def GetBaysToCheck(typeID, priorityBays = []):
    baysToCheck = priorityBays
    if baysToCheck is None:
        baysToCheck = []
    if typeID in autoConsumeTypes:
        baysToCheck.extend(autoConsumeTypes[typeID])
    else:
        invType = cfg.invtypes.Get(typeID)
        if invType.groupID in autoConsumeGroups:
            baysToCheck.extend(autoConsumeGroups[invType.groupID])
        elif invType.categoryID in autoConsumeCategories:
            baysToCheck.extend(autoConsumeCategories[invType.categoryID])
    if const.flagCargo not in baysToCheck:
        baysToCheck.append(const.flagCargo)
    return baysToCheck


exports = util.AutoExports('inventoryFlagsCommon', locals())

