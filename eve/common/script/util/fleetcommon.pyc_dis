#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/util/fleetcommon.py
import util
import blue
FLEET_NONEID = -1
CHANNELSTATE_NONE = 0
CHANNELSTATE_LISTENING = 1
CHANNELSTATE_MAYSPEAK = 2
CHANNELSTATE_SPEAKING = 4
MIN_MEMBERS_IN_FLEET = 50
MAX_MEMBERS_IN_FLEET = 256
MAX_MEMBERS_IN_SQUAD = 10
MAX_SQUADS_IN_WING = 5
MAX_WINGS_IN_FLEET = 5
MIN_MEMBERS_CMDR_BONUSES = 2
MAX_NAME_LENGTH = 10
MAX_DAMAGE_SENDERS = 15
FLEET_STATUS_ACTIVE = 1
FLEET_STATUS_INACTIVE = 0
FLEET_STATUS_TOOFEWWINGS = -1
FLEET_STATUS_TOOMANYWINGS = -2
WING_STATUS_ACTIVE = 1
WING_STATUS_INACTIVE = 0
WING_STATUS_TOOFEWMEMBERS = -1
WING_STATUS_TOOMANYSQUADS = -2
SQUAD_STATUS_ACTIVE = 1
SQUAD_STATUS_INACTIVE = 0
SQUAD_STATUS_NOSQUADCOMMANDER = -1
SQUAD_STATUS_TOOMANYMEMBERS = -2
SQUAD_STATUS_TOOFEWMEMBERS = -3
BROADCAST_NONE = 0
BROADCAST_DOWN = 1
BROADCAST_UP = 2
BROADCAST_ALL = 3
BROADCAST_UNIVERSE = 0
BROADCAST_SYSTEM = 1
BROADCAST_BUBBLE = 2
INVITE_CLOSED = 0
INVITE_CORP = 1
INVITE_ALLIANCE = 2
INVITE_MILITIA = 4
INVITE_PUBLIC = 8
INVITE_ALL = 15
FLEETNAME_MAXLENGTH = 32
FLEETDESC_MAXLENGTH = 150
NODEID_MOD = 10000000
FLEETID_MOD = 10000
WINGID_MOD = 20000
SQUADID_MOD = 30000
ALL_BROADCASTS = ['EnemySpotted',
 'NeedBackup',
 'HoldPosition',
 'InPosition',
 'TravelTo',
 'JumpBeacon',
 'Location',
 'Target',
 'HealArmor',
 'HealShield',
 'HealCapacitor',
 'WarpTo',
 'AlignTo',
 'JumpTo']
RECONNECT_TIMEOUT = 2

def IsSuperior(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == const.fleetRoleLeader:
        return False
    if member.role == const.fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.role != const.fleetRoleMember and member.wingID == myself.wingID:
            return True
    return False


def IsSubordinateOrEqual(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == const.fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.squadID == myself.squadID:
            return True
    if myself.role == const.fleetRoleWingCmdr:
        if member.wingID == myself.wingID:
            return True
    return False


def ShouldSendBroadcastTo(member, myself, scope):
    if scope == BROADCAST_ALL:
        return True
    if scope == BROADCAST_UP and IsSuperior(member, myself):
        return True
    if scope == BROADCAST_DOWN and IsSubordinateOrEqual(member, myself):
        return True
    return False


def LogBroadcast(messageName, scope, itemID):
    for idx in range(len(ALL_BROADCASTS)):
        if ALL_BROADCASTS[idx] == messageName:
            break

    sm.GetService('infoGatheringMgr').LogInfoEventFromServer(const.infoEventFleetBroadcast, idx, int_1=1, int_2=scope)
    sm.GetService('fleetObjectHandler').LogPlayerEvent('Broadcast', messageName, scope, itemID)


def IsOpenToCorp(fleet):
    return fleet.inviteScope & INVITE_CORP == INVITE_CORP


def IsOpenToAlliance(fleet):
    return fleet.inviteScope & INVITE_ALLIANCE == INVITE_ALLIANCE


def IsOpenToMilitia(fleet):
    return fleet.inviteScope & INVITE_MILITIA == INVITE_MILITIA


def IsOpenToPublic(fleet):
    return fleet.inviteScope & INVITE_PUBLIC == INVITE_PUBLIC


exports = util.AutoExports('fleetcommon', locals())