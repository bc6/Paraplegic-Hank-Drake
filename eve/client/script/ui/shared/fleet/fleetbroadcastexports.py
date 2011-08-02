import util
import dbg
import menu
from fleetcommon import *
from types import TupleType
activeBroadcastColor = 'ddffffff'
types = {'EnemySpotted': {'bigIcon': 'ui_44_32_51',
                  'smallIcon': 'ui_38_16_88'},
 'Target': {'bigIcon': 'ui_44_32_17',
            'smallIcon': 'ui_38_16_72'},
 'HealArmor': {'bigIcon': 'ui_44_32_53',
               'smallIcon': 'ui_38_16_74'},
 'HealShield': {'bigIcon': 'ui_44_32_52',
                'smallIcon': 'ui_38_16_73'},
 'HealCapacitor': {'bigIcon': 'ui_44_32_54',
                   'smallIcon': 'ui_38_16_75'},
 'WarpTo': {'bigIcon': 'ui_44_32_55',
            'smallIcon': 'ui_38_16_76'},
 'NeedBackup': {'bigIcon': 'ui_44_32_56',
                'smallIcon': 'ui_38_16_77'},
 'AlignTo': {'bigIcon': 'ui_44_32_57',
             'smallIcon': 'ui_38_16_78'},
 'JumpTo': {'bigIcon': 'ui_44_32_39',
            'smallIcon': 'ui_38_16_86'},
 'TravelTo': {'bigIcon': 'ui_44_32_58',
              'smallIcon': 'ui_38_16_87'},
 'InPosition': {'bigIcon': 'ui_44_32_49',
                'smallIcon': 'ui_38_16_70'},
 'HoldPosition': {'bigIcon': 'ui_44_32_50',
                  'smallIcon': 'ui_38_16_71'},
 'JumpBeacon': {'bigIcon': 'ui_44_32_58',
                'smallIcon': 'ui_38_16_76'},
 'Location': {'bigIcon': 'ui_44_32_58',
              'smallIcon': 'ui_38_16_87'}}
defaultIcon = ['ui_44_32_29', 'ui_38_16_70']

def ShouldListen(gbName, senderRole, senderJob, senderWingID, senderSquadID):
    return settings.user.ui.Get('listenBroadcast_%s' % gbName, True) or senderRole == const.fleetRoleLeader or senderJob == const.fleetJobCreator or senderRole == const.fleetRoleWingCmdr and senderWingID == eve.session.wingid or senderRole == const.fleetRoleSquadCmdr and senderSquadID == eve.session.squadid



def FilteredBroadcast(f, name):

    def deco(self, senderID, *args, **kw):
        rec = sm.GetService('fleet').GetMembers().get(senderID)
        if not rec or ShouldListen(name, rec.role, rec.job, rec.wingID, rec.squadID):
            f(self, senderID, *args, **kw)


    return deco



def MenuGetter(gbType, *args):
    GetMenu = globals()[('GetMenu_%s' % gbType)]
    return lambda : GetMenu(*args)



def GetMenu_EnemySpotted(charID, locationID, nearID):
    where = Where(charID, locationID)
    menuSvc = sm.GetService('menu')
    m = []
    if where in (inSystem, inBubble):
        defaultWarpDist = menuSvc.GetDefaultActionDistance('WarpTo')
        m.extend([[mls.UI_CMD_WARPTOMEMBER, menuSvc.WarpToMember, (charID, float(defaultWarpDist))],
         [(mls.UI_CMD_WARPTOMEMBERDIST % {'dist': ''}, menu.ACTIONSGROUP), menuSvc.WarpToMenu(menuSvc.WarpToMember, charID)],
         [mls.UI_CMD_WARPFLEETTOMEMBER, menuSvc.WarpFleetToMember, (charID, float(defaultWarpDist))],
         [(mls.UI_CMD_WARPFLEETTOMEMBERDIST % {'dist': ''}, menu.FLEETGROUP), menuSvc.WarpToMenu(menuSvc.WarpFleetToMember, charID)]])
    else:
        m.extend(GetMenu_TravelTo(charID, locationID, nearID))
    return m


GetMenu_NeedBackup = GetMenu_InPosition = GetMenu_EnemySpotted

def GetMenu_TravelTo(charID, solarSystemID, destinationID):
    destinationID = destinationID or solarSystemID
    menuSvc = sm.GetService('menu')
    waypoints = sm.StartService('starmap').GetWaypoints()
    m = [[mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (destinationID, 1)]]
    if destinationID in waypoints:
        m.append([mls.UI_CMD_REMOVEWAYPOINT, sm.StartService('starmap').ClearWaypoints, (destinationID,)])
    else:
        m.append([mls.UI_CMD_ADDWAYPOINT, sm.StartService('starmap').SetWaypoint, (destinationID,)])
    return m



def GetMenu_Location(charID, solarSystemID, nearID):
    menuSvc = sm.GetService('menu')
    if solarSystemID != eve.session.solarsystemid2:
        m = GetMenu_TravelTo(charID, solarSystemID, None)
        m.append([mls.UI_GENERIC_DISTANCE, sm.GetService('fleet').DistanceToFleetMate, (solarSystemID, nearID)])
    else:
        m = GetMenu_WarpTo(charID, solarSystemID, nearID)
    return m



def GetMenu_JumpBeacon(charID, solarSystemID, itemID):
    menuSvc = sm.GetService('menu')
    waypoints = sm.StartService('starmap').GetWaypoints()
    beacon = (solarSystemID, itemID)
    m = [[mls.UI_CMD_JUMPTOMEMBER, sm.StartService('menu').JumpToBeaconFleet, (charID, beacon)]]
    isTitan = False
    if eve.session.solarsystemid and eve.session.shipid:
        ship = sm.StartService('godma').GetItem(eve.session.shipid)
        if ship.groupID in [const.groupTitan, const.groupBlackOps]:
            isTitan = True
    if isTitan:
        m.append([mls.UI_CMD_BRIDGETOMEMBER, sm.StartService('menu').BridgeToBeacon, (charID, beacon)])
    m.append(None)
    m.append([mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (solarSystemID, 1)])
    if solarSystemID in waypoints:
        m.append([mls.UI_CMD_REMOVEWAYPOINT, sm.StartService('starmap').ClearWaypoints, (solarSystemID,)])
    else:
        m.append([mls.UI_CMD_ADDWAYPOINT, sm.StartService('starmap').SetWaypoint, (solarSystemID,)])
    return m



def GetMenu_WarpTo(charID, solarSystemID, locationID):
    bp = sm.GetService('michelle').GetBallpark()
    ball = bp and bp.GetBall(locationID)
    m = GetWarpLocationMenu(locationID)
    return m



def GetWarpLocationMenu(locationID):
    if session.solarsystemid is None:
        return []
    menuSvc = sm.GetService('menu')
    defaultWarpDist = menuSvc.GetDefaultActionDistance('WarpTo')
    ret = [[mls.UI_CMD_WARPTOLOCATION, menuSvc.WarpToItem, (locationID, float(defaultWarpDist))], [mls.UI_CMD_WARPTOLOCATIONWITHIN % {'dist': ''}, menuSvc.WarpToMenu(menuSvc.WarpToItem, locationID)], [mls.UI_CMD_ALIGNTO, menuSvc.AlignTo, (locationID,)]]
    if eve.session.fleetrole == const.fleetRoleLeader:
        ret.extend([[mls.UI_CMD_WARPFLEETTOLOCATION, menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [(mls.UI_CMD_WARPFLEETTOLOCATIONWITHIN % {'dist': ''}, menu.FLEETGROUP), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif eve.session.fleetrole == const.fleetRoleWingCmdr:
        ret.extend([[mls.UI_CMD_WARPWINGTOLOCATION, menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [(mls.UI_CMD_WARPWINGTOLOCATIONWITHIN % {'dist': ''}, menu.FLEETGROUP), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif eve.session.fleetrole == const.fleetRoleSquadCmdr:
        ret.extend([[mls.UI_CMD_WARPSQUADTOLOCATION, menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [(mls.UI_CMD_WARPSQUADTOLOCATIONWITHIN % {'dist': ''}, menu.FLEETGROUP), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    return ret



def GetMenu_Target(charID, solarSystemID, shipID):
    m = []
    targetSvc = sm.GetService('target')
    targets = targetSvc.GetTargets()
    if not targetSvc.BeingTargeted(shipID) and shipID not in targets:
        m = [(mls.UI_CMD_LOCKTARGET, targetSvc.TryLockTarget, (shipID,))]
    return m



def GetMenu_Member(charID):
    m = [(mls.UI_FLEET_FLEETMEMBER, sm.GetService('menu').FleetMenu(charID, unparsed=False))]
    return m



def GetMenu_Ignore(name):
    isListen = settings.user.ui.Get('listenBroadcast_%s' % name, True)
    if isListen:
        m = [(mls.UI_FLEET_IGNOREBROADCAST, sm.GetService('fleet').SetListenBroadcast, (name, False))]
    else:
        m = [(mls.UI_FLEET_UNIGNOREBROADCAST, sm.GetService('fleet').SetListenBroadcast, (name, True))]
    return m


GetMenu_HealArmor = GetMenu_HealShield = GetMenu_HealCapacitor = GetMenu_Target
GetMenu_JumpTo = GetMenu_AlignTo = GetMenu_WarpTo

def GetCaption_EnemySpotted(charID, solarSystemID, nearID):
    nohl = mls.UI_FLEET_IN_LOCATION % {'location': cfg.evelocations.Get(nearID).name}
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_ENEMYSPOTTED)
    return GetCaption(charID, text, nohl)



def GetCaption_NeedBackup(charID, solarSystemID, nearID):
    nohl = 'in %s' % cfg.evelocations.Get(nearID).name
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_NEEDBACKUP)
    return GetCaption(charID, text, nohl)



def GetCaption_Target(charID, solarSystemID, shipID):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_TARGET)



def GetCaption_HealArmor(charID, solarSystemID, shipID):
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_HEALARMOR)
    return GetCaption(charID, text)



def GetCaption_HealShield(charID, solarSystemID, shipID):
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_HEALSHIELD)
    return GetCaption(charID, text)



def GetCaption_HealCapacitor(charID, solarSystemID, shipID):
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_HEALCAPACITOR)
    return GetCaption(charID, text)



def GetCaption_WarpTo(charID, solarSystemID, locationID):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_WARPTO, cfg.evelocations.Get(locationID).name)



def GetCaption_AlignTo(charID, solarSystemID, locationID):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_ALIGNTO, cfg.evelocations.Get(locationID).name)



def GetCaption_JumpTo(charID, solarSystemID, locationID):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_JUMPTO, cfg.evelocations.Get(locationID).name)



def GetCaption_TravelTo(charID, solarSystemID, locationID):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_TRAVELTO, cfg.evelocations.Get(locationID).name)



def GetCaption_InPosition(charID, solarSystemID, nearID):
    if solarSystemID == eve.session.solarsystemid:
        locID = nearID
    else:
        locID = solarSystemID
    text = '%s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_INPOSITION)
    return GetCaption(charID, text, cfg.evelocations.Get(locID).name)



def GetCaption_HoldPosition(charID, *blah, **bleh):
    return GetCaption(charID, mls.UI_FLEET_BROADCAST_HOLDPOSITION)



def GetCaption_JumpBeacon(charID, solarSystemID, itemID):
    nhl = ' %s %s' % (mls.UI_GENERIC_IN, cfg.evelocations.Get(solarSystemID).name)
    ret = '%s - %s %s' % (cfg.eveowners.Get(charID).name, mls.UI_FLEET_BROADCAST_JUMPBEACON, nhl)
    return ret



def GetCaption_Location(charID, solarSystemID, nearID):
    nhl = ' %s %s' % (mls.UI_GENERIC_IN, cfg.evelocations.Get(solarSystemID).name)
    ret = '%s - Located %s' % (cfg.eveowners.Get(charID).name, nhl)
    return ret



def GetCaption_OnFleetJoin(rec):
    if rec.charID == eve.session.charid:
        return mls.UI_FLEET_MEJOINED % {'newrank': GetRankName(rec)}
    if _ICareAbout(rec.role, rec.wingID, rec.squadID):
        return mls.UI_FLEET_OTHERJOINED % {'name': cfg.eveowners.Get(rec.charID).name,
         'newrank': GetRankName(rec)}



def GetCaption_OnFleetLeave(rec):
    if rec.charID == eve.session.charid or not hasattr(rec, 'role'):
        return None
    if _ICareAbout(rec.role, rec.wingID, rec.squadID):
        return mls.UI_FLEET_OTHERLEFT % {'name': cfg.eveowners.Get(rec.charID).name,
         'rank': GetRankName(rec)}



def _Rank(role):
    if not hasattr(_Rank, 'ranks'):
        _Rank.ranks = {const.fleetRoleLeader: 4,
         const.fleetRoleWingCmdr: 3,
         const.fleetRoleSquadCmdr: 2,
         const.fleetRoleMember: 1}
    return _Rank.ranks.get(role, -1)



def GetRankName(member):
    ranknames = {const.fleetRoleLeader: mls.UI_FLEET_FLEETCOMMANDER,
     const.fleetRoleWingCmdr: mls.UI_FLEET_WINGCOMMANDER,
     const.fleetRoleSquadCmdr: mls.UI_FLEET_SQUADCOMMANDER,
     const.fleetRoleMember: mls.UI_FLEET_SQUADMEMBER,
     None: mls.UI_FLEET_NONMEMBER}
    name = ranknames.get(member.role, '-')
    if member.job & const.fleetJobCreator:
        name += ' - %s' % mls.UI_FLEET_BOSS
    return name



def GetBoosterName(roleBooster):
    boosternames = {const.fleetBoosterFleet: mls.UI_FLEET_FLEETBOOSTER,
     const.fleetBoosterWing: mls.UI_FLEET_WINGBOOSTER,
     const.fleetBoosterSquad: mls.UI_FLEET_SQUADBOOSTER}
    name = boosternames.get(roleBooster, mls.UI_GENERIC_NONE)
    return name



def GetRoleName(role):
    ranknames = {const.fleetRoleLeader: mls.UI_FLEET_FLEETCOMMANDER,
     const.fleetRoleWingCmdr: mls.UI_FLEET_WINGCOMMANDER,
     const.fleetRoleSquadCmdr: mls.UI_FLEET_SQUADCOMMANDER,
     const.fleetRoleMember: mls.UI_FLEET_SQUADMEMBER,
     None: mls.UI_FLEET_NONMEMBER}
    name = ranknames.get(role, '-')
    return name



def _ICareAbout(*args):

    def MySuperior(role, wingID, squadID):
        return _Rank(role) > _Rank(eve.session.fleetrole) and wingID in (eve.session.wingid, -1) and squadID in (eve.session.squadid, -1)



    def SubordinateICareAbout(role, wingID, squadID):
        return role != const.fleetRoleMember and _Rank(role) == _Rank(eve.session.fleetrole) - 1 and eve.session.wingid in (-1, wingID)


    return MySuperior(*args) or SubordinateICareAbout(*args)



def GetCaption(senderID, hl, nohl = None):
    if not nohl:
        nohl = ''
    else:
        nohl = ' %s' % nohl
    ret = '<b>%s</b>%s' % (hl, nohl)
    return ret


inBubble = 1
inSystem = 2
exSystem = 3

def Where(charID, locationID = None):
    if util.SlimItemFromCharID(charID) is not None:
        return inBubble
    else:
        if locationID in (None, eve.session.solarsystemid):
            return inSystem
        return exSystem



def GetRoleIconFromCharID(charID):
    if charID is None:
        return 
    info = sm.GetService('fleet').GetMemberInfo(int(charID))
    if info is None:
        return 
    if info.job & const.fleetJobCreator:
        iconRole = '73_20'
    else:
        iconRole = {const.fleetRoleLeader: '73_17',
         const.fleetRoleWingCmdr: '73_18',
         const.fleetRoleSquadCmdr: '73_19'}.get(info.role, None)
    return iconRole



def GetVoiceMenu(entry, charID = None, channel = None):
    if entry:
        charID = entry.sr.node.charID
        channel = entry.sr.node.channel
    m = []
    charID = int(charID)
    if channel:
        state = sm.GetService('fleet').GetVoiceChannelState(channel)
        if state in [CHANNELSTATE_LISTENING, CHANNELSTATE_SPEAKING, CHANNELSTATE_MAYSPEAK]:
            m.append((mls.UI_CMD_LEAVECHANNEL, sm.GetService('vivox').LeaveChannel, (channel,)))
            if sm.StartService('vivox').GetSpeakingChannel() != channel:
                m.append((mls.UI_CMD_MAKESPEAKINGCHANNEL, sm.StartService('vivox').SetSpeakingChannel, (channel,)))
        elif type(channel) is not TupleType or not channel[0].startswith('inst'):
            m.append((mls.UI_CMD_JOINCHANNEL, sm.StartService('vivox').JoinChannel, (channel,)))
        m.append(None)
    m += sm.GetService('menu').CharacterMenu(charID)
    return m



def GetBroadcastScopeName(scope):
    ret = {BROADCAST_NONE: mls.UI_FLEET_BROADCAST_NONE,
     BROADCAST_DOWN: mls.UI_FLEET_BROADCAST_DOWN,
     BROADCAST_UP: mls.UI_FLEET_BROADCAST_UP,
     BROADCAST_ALL: mls.UI_FLEET_BROADCAST_ALL}.get(scope, mls.UI_GENERIC_UNKNOWN)
    return ret



def GetBroadcastWhere(name):
    if name in ('Target', 'HealArmor', 'HealShield', 'HealCapacitor'):
        return BROADCAST_BUBBLE
    else:
        if name in ('WarpTo', 'AlignTo', 'JumpTo'):
            return BROADCAST_SYSTEM
        return BROADCAST_UNIVERSE



def GetBroadcastWhereName(scope):
    ret = {BROADCAST_BUBBLE: mls.UI_FLEET_BROADCAST_BUBBLE,
     BROADCAST_SYSTEM: mls.UI_FLEET_BROADCAST_SYSTEM}.get(scope, '')
    return ret


exports = util.AutoExports('fleetbr', locals())

