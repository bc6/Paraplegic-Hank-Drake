import blue
import localization
from entities import entityConstants
locals().update(entityConstants)
STRUCTURE_UNANCHORED = 0
STRUCTURE_ANCHORED = 1
STRUCTURE_ONLINING = 2
STRUCTURE_REINFORCED = 3
STRUCTURE_ONLINE = 4
STRUCTURE_OPERATING = 5
STRUCTURE_VULNERABLE = 6
STRUCTURE_SHIELD_REINFORCE = 7
STRUCTURE_ARMOR_REINFORCE = 8
STRUCTURE_INVULNERABLE = 9
ANCHORED_STRUCTURE_STATES = (STRUCTURE_ANCHORED,
 STRUCTURE_ONLINING,
 STRUCTURE_REINFORCED,
 STRUCTURE_ONLINE,
 STRUCTURE_OPERATING,
 STRUCTURE_VULNERABLE,
 STRUCTURE_SHIELD_REINFORCE,
 STRUCTURE_ARMOR_REINFORCE,
 STRUCTURE_INVULNERABLE)
db2Entity = {STRUCTURE_UNANCHORED: [STATE_UNANCHORING, STATE_UNANCHORED],
 STRUCTURE_ANCHORED: [STATE_ANCHORING, STATE_ANCHORED],
 STRUCTURE_ONLINING: [STATE_ONLINING, STATE_ONLINING],
 STRUCTURE_REINFORCED: [STATE_REINFORCED],
 STRUCTURE_ONLINE: [STATE_IDLE],
 STRUCTURE_OPERATING: [STATE_OPERATING, STATE_IDLE],
 STRUCTURE_VULNERABLE: [STATE_VULNERABLE],
 STRUCTURE_SHIELD_REINFORCE: [STATE_SHIELD_REINFORCE],
 STRUCTURE_ARMOR_REINFORCE: [STATE_ARMOR_REINFORCE]}

def GetJumpFuelConsumption(distance, consumptionRate, massFactor):
    return max(long(distance * consumptionRate * massFactor), 1)



def GetEntityStatesForDBState(dbState):
    return db2Entity.get(dbState, [])



def IsStructureAnchored(item, settings):
    if settings.state in ANCHORED_STRUCTURE_STATES:
        return 1
    if settings.state == STRUCTURE_UNANCHORED and settings.stateTimestamp is not None:
        diffMs = (blue.os.GetWallclockTime() - settings.stateTimestamp) / 10000
        return diffMs < sm.services['dogmaIM'].GetTypeAttribute2(item.typeID, const.attributeUnanchoringDelay)
    return 0


ONLINE_STABLE_STATES = (STRUCTURE_REINFORCED,
 STRUCTURE_ONLINE,
 STRUCTURE_OPERATING,
 STRUCTURE_VULNERABLE,
 STRUCTURE_INVULNERABLE,
 STRUCTURE_SHIELD_REINFORCE,
 STRUCTURE_ARMOR_REINFORCE)

def Entity2DB(activityState):
    if activityState in (STATE_UNANCHORING, STATE_UNANCHORED):
        return STRUCTURE_UNANCHORED
    if activityState in (STATE_ANCHORING, STATE_ANCHORED):
        return STRUCTURE_ANCHORED
    if activityState == STATE_ONLINING:
        return STRUCTURE_ONLINING
    if activityState == STATE_REINFORCED:
        return STRUCTURE_REINFORCED
    if activityState == STATE_VULNERABLE:
        return STRUCTURE_VULNERABLE
    if activityState == STATE_INVULNERABLE:
        return STRUCTURE_INVULNERABLE
    if activityState == STATE_OPERATING:
        return STRUCTURE_OPERATING
    if activityState == STATE_SHIELD_REINFORCE:
        return STRUCTURE_SHIELD_REINFORCE
    if activityState == STATE_ARMOR_REINFORCE:
        return STRUCTURE_ARMOR_REINFORCE
    if activityState >= STATE_IDLE:
        return STRUCTURE_ONLINE


exports = {'pos.IsStructureAnchored': IsStructureAnchored,
 'pos.GetEntityStatesForDBState': GetEntityStatesForDBState,
 'pos.ONLINE_STABLE_STATES': ONLINE_STABLE_STATES,
 'pos.Entity2DB': Entity2DB,
 'pos.GetJumpFuelConsumption': GetJumpFuelConsumption,
 'pos.STRUCTURE_ANCHORED': STRUCTURE_ANCHORED,
 'pos.STRUCTURE_UNANCHORED': STRUCTURE_UNANCHORED,
 'pos.STRUCTURE_ONLINING': STRUCTURE_ONLINING,
 'pos.STRUCTURE_REINFORCED': STRUCTURE_REINFORCED,
 'pos.STRUCTURE_ONLINE': STRUCTURE_ONLINE,
 'pos.STRUCTURE_OPERATING': STRUCTURE_OPERATING,
 'pos.STRUCTURE_VULNERABLE': STRUCTURE_VULNERABLE,
 'pos.STRUCTURE_SHIELD_REINFORCE': STRUCTURE_SHIELD_REINFORCE,
 'pos.STRUCTURE_ARMOR_REINFORCE': STRUCTURE_ARMOR_REINFORCE,
 'pos.STRUCTURE_INVULNERABLE': STRUCTURE_INVULNERABLE,
 'pos.DISPLAY_NAMES': {STRUCTURE_ANCHORED: localization.GetByLabel('Entities/States/Anchored'),
                       STRUCTURE_UNANCHORED: localization.GetByLabel('Entities/States/Unanchored'),
                       STRUCTURE_ONLINING: localization.GetByLabel('Entities/States/Onlining'),
                       STRUCTURE_REINFORCED: localization.GetByLabel('Entities/States/Reinforced'),
                       STRUCTURE_ONLINE: localization.GetByLabel('Entities/States/Online'),
                       STRUCTURE_OPERATING: localization.GetByLabel('Entities/States/Operating'),
                       STRUCTURE_VULNERABLE: localization.GetByLabel('Entities/States/Vulnerable'),
                       STRUCTURE_SHIELD_REINFORCE: localization.GetByLabel('Entities/States/ShieldReinforcedVerbose'),
                       STRUCTURE_ARMOR_REINFORCE: localization.GetByLabel('Entities/States/ArmorReinforcedVerbose'),
                       STRUCTURE_INVULNERABLE: localization.GetByLabel('Entities/States/Invulnerable')}}

