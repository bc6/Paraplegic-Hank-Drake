import util
import dbg
import menu
from fleetcommon import *
from types import TupleType
import localization
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
broadcastNames = {'EnemySpotted': 'UI/Fleet/FleetBroadcast/Commands/EnemySpotted',
 'Target': 'UI/Fleet/FleetBroadcast/Commands/BroadcastTarget',
 'HealArmor': 'UI/Fleet/FleetBroadcast/Commands/HealArmor',
 'HealShield': 'UI/Fleet/FleetBroadcast/Commands/HealShield',
 'HealCapacitor': 'UI/Fleet/FleetBroadcast/Commands/HealCapacitor',
 'WarpTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo',
 'NeedBackup': 'UI/Fleet/FleetBroadcast/Commands/NeedBackup',
 'AlignTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo',
 'JumpTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastJumpTo',
 'TravelTo': 'UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo',
 'InPosition': 'UI/Fleet/FleetBroadcast/Commands/InPosition',
 'HoldPosition': 'UI/Fleet/FleetBroadcast/Commands/HoldPosition',
 'JumpBeacon': 'UI/Fleet/FleetBroadcast/Commands/JumpBeacon',
 'Location': 'UI/Fleet/FleetBroadcast/Commands/Location',
 'Event': 'UI/Fleet/FleetBroadcast/FleetEvent'}
broadcastScopes = {BROADCAST_DOWN: {BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeDown',
                  BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeDownSystem',
                  BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeDownBubble'},
 BROADCAST_UP: {BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeUp',
                BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeUpSystem',
                BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeUpBubble'},
 BROADCAST_ALL: {BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeAll',
                 BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeAllSystem',
                 BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeAllBubble'}}
broadcastRanges = {'Target': BROADCAST_BUBBLE,
 'HealArmor': BROADCAST_BUBBLE,
 'HealShield': BROADCAST_BUBBLE,
 'HealCapacitor': BROADCAST_BUBBLE,
 'WarpTo': BROADCAST_SYSTEM,
 'AlignTo': BROADCAST_SYSTEM,
 'JumpTo': BROADCAST_SYSTEM}
defaultBroadcastRange = BROADCAST_UNIVERSE
broadcastRangeNames = {BROADCAST_UNIVERSE: 'UI/Fleet/FleetBroadcast/BroadcastRangeGlobal',
 BROADCAST_SYSTEM: 'UI/Fleet/FleetBroadcast/BroadcastRangeSystem',
 BROADCAST_BUBBLE: 'UI/Fleet/FleetBroadcast/BroadcastRangeBubble'}

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
        m.extend([[localization.GetByLabel('UI/Fleet/WarpToMember'), menuSvc.WarpToMember, (charID, float(defaultWarpDist))],
         [(localization.GetByLabel('UI/Fleet/WarpToMemberSubmenuOption'), menu.ACTIONSGROUP), menuSvc.WarpToMenu(menuSvc.WarpToMember, charID)],
         [localization.GetByLabel('UI/Fleet/WarpFleetToMember'), menuSvc.WarpFleetToMember, (charID, float(defaultWarpDist))],
         [localization.GetByLabel('UI/Fleet/FleetSubmenus/WarpFleetToMember'), menuSvc.WarpToMenu(menuSvc.WarpFleetToMember, charID)]])
    else:
        m.extend(GetMenu_TravelTo(charID, locationID, nearID))
    return m


GetMenu_NeedBackup = GetMenu_InPosition = GetMenu_EnemySpotted

def GetMenu_TravelTo(charID, solarSystemID, destinationID):
    destinationID = destinationID or solarSystemID
    menuSvc = sm.GetService('menu')
    waypoints = sm.StartService('starmap').GetWaypoints()
    m = [[localization.GetByLabel('UI/Inflight/SetDestination'), sm.StartService('starmap').SetWaypoint, (destinationID, True)]]
    if destinationID in waypoints:
        m.append([localization.GetByLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (destinationID,)])
    else:
        m.append([localization.GetByLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (destinationID,)])
    return m



def GetMenu_Location(charID, solarSystemID, nearID):
    menuSvc = sm.GetService('menu')
    if solarSystemID != eve.session.solarsystemid2:
        m = GetMenu_TravelTo(charID, solarSystemID, None)
        m.append([localization.GetByLabel('UI/Fleet/FleetSubmenus/ShowDistance'), sm.GetService('fleet').DistanceToFleetMate, (solarSystemID, nearID)])
    else:
        m = GetMenu_WarpTo(charID, solarSystemID, nearID)
    return m



def GetMenu_JumpBeacon(charID, solarSystemID, itemID):
    menuSvc = sm.GetService('menu')
    waypoints = sm.StartService('starmap').GetWaypoints()
    beacon = (solarSystemID, itemID)
    m = [[localization.GetByLabel('UI/Inflight/JumpToFleetMember'), sm.StartService('menu').JumpToBeaconFleet, (charID, beacon)]]
    isTitan = False
    if eve.session.solarsystemid and eve.session.shipid:
        ship = sm.StartService('godma').GetItem(eve.session.shipid)
        if ship.groupID in [const.groupTitan, const.groupBlackOps]:
            isTitan = True
    if isTitan:
        m.append([localization.GetByLabel('UI/Fleet/BridgeToMember'), sm.StartService('menu').BridgeToBeacon, (charID, beacon)])
    m.append(None)
    m.append([localization.GetByLabel('UI/Inflight/SetDestination'), sm.StartService('starmap').SetWaypoint, (solarSystemID, True)])
    if solarSystemID in waypoints:
        m.append([localization.GetByLabel('UI/Inflight/RemoveWaypoint'), sm.StartService('starmap').ClearWaypoints, (solarSystemID,)])
    else:
        m.append([localization.GetByLabel('UI/Inflight/AddWaypoint'), sm.StartService('starmap').SetWaypoint, (solarSystemID,)])
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
    ret = [[localization.GetByLabel('UI/Inflight/WarpToBookmark'), menuSvc.WarpToItem, (locationID, float(defaultWarpDist))], [localization.GetByLabel('UI/Inflight/Submenus/WarpToWithin'), menuSvc.WarpToMenu(menuSvc.WarpToItem, locationID)], [localization.GetByLabel('UI/Inflight/AlignTo'), menuSvc.AlignTo, (locationID,)]]
    if eve.session.fleetrole == const.fleetRoleLeader:
        ret.extend([[localization.GetByLabel('UI/Fleet/WarpFleetToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [localization.GetByLabel('UI/Fleet/FleetSubmenus/WarpFleetToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif eve.session.fleetrole == const.fleetRoleWingCmdr:
        ret.extend([[localization.GetByLabel('UI/Fleet/WarpWingToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [localization.GetByLabel('UI/Fleet/FleetSubmenus/WarpWingToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif eve.session.fleetrole == const.fleetRoleSquadCmdr:
        ret.extend([[localization.GetByLabel('UI/Fleet/WarpSquadToLocation'), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [localization.GetByLabel('UI/Fleet/FleetSubmenus/WarpSquadToLocationWithin'), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    return ret



def GetMenu_Target(charID, solarSystemID, shipID):
    m = []
    targetSvc = sm.GetService('target')
    targets = targetSvc.GetTargets()
    if not targetSvc.BeingTargeted(shipID) and shipID not in targets:
        m = [(localization.GetByLabel('UI/Inflight/LockTarget'), targetSvc.TryLockTarget, (shipID,))]
    return m



def GetMenu_Member(charID):
    m = [(localization.GetByLabel('UI/Fleet/Ranks/FleetMember'), sm.GetService('menu').FleetMenu(charID, unparsed=False))]
    return m



def GetMenu_Ignore(name):
    isListen = settings.user.ui.Get('listenBroadcast_%s' % name, True)
    if isListen:
        m = [(localization.GetByLabel('UI/Fleet/FleetBroadcast/IgnoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, False))]
    else:
        m = [(localization.GetByLabel('UI/Fleet/FleetBroadcast/UnignoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, True))]
    return m


GetMenu_HealArmor = GetMenu_HealShield = GetMenu_HealCapacitor = GetMenu_Target
GetMenu_JumpTo = GetMenu_AlignTo = GetMenu_WarpTo

def _Rank(role):
    if not hasattr(_Rank, 'ranks'):
        _Rank.ranks = {const.fleetRoleLeader: 4,
         const.fleetRoleWingCmdr: 3,
         const.fleetRoleSquadCmdr: 2,
         const.fleetRoleMember: 1}
    return _Rank.ranks.get(role, -1)



def GetRankName(member):
    if member.job & const.fleetJobCreator:
        if member.role == const.fleetRoleLeader:
            return localization.GetByLabel('UI/Fleet/Ranks/FleetCommanderBoss')
        else:
            if member.role == const.fleetRoleWingCmdr:
                return localization.GetByLabel('UI/Fleet/Ranks/WingCommanderBoss')
            if member.role == const.fleetRoleSquadCmdr:
                return localization.GetByLabel('UI/Fleet/Ranks/SquadCommanderBoss')
            if member.role == const.fleetRoleMember:
                return localization.GetByLabel('UI/Fleet/Ranks/SquadMemberBoss')
            return localization.GetByLabel('UI/Fleet/Ranks/NonMember')
    else:
        return GetRoleName(member.role)



def GetBoosterName(roleBooster):
    boosternames = {const.fleetBoosterFleet: localization.GetByLabel('UI/Fleet/Ranks/FleetBooster'),
     const.fleetBoosterWing: localization.GetByLabel('UI/Fleet/Ranks/WingBooster'),
     const.fleetBoosterSquad: localization.GetByLabel('UI/Fleet/Ranks/SquadBooster')}
    name = boosternames.get(roleBooster, '')
    return name



def GetRoleName(role):
    if role == const.fleetRoleLeader:
        return localization.GetByLabel('UI/Fleet/Ranks/FleetCommander')
    else:
        if role == const.fleetRoleWingCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/WingCommander')
        if role == const.fleetRoleSquadCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadCommander')
        if role == const.fleetRoleMember:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadMember')
        return localization.GetByLabel('UI/Fleet/Ranks/NonMember')



def _ICareAbout(*args):

    def MySuperior(role, wingID, squadID):
        return _Rank(role) > _Rank(eve.session.fleetrole) and wingID in (eve.session.wingid, -1) and squadID in (eve.session.squadid, -1)



    def SubordinateICareAbout(role, wingID, squadID):
        return role != const.fleetRoleMember and _Rank(role) == _Rank(eve.session.fleetrole) - 1 and eve.session.wingid in (-1, wingID)


    return MySuperior(*args) or SubordinateICareAbout(*args)


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
            m.append((localization.GetByLabel('UI/Chat/ChannelWindow/LeaveChannel'), sm.GetService('vivox').LeaveChannel, (channel,)))
            if sm.StartService('vivox').GetSpeakingChannel() != channel:
                m.append((localization.GetByLabel('UI/Chat/MakeSpeakingChannel'), sm.StartService('vivox').SetSpeakingChannel, (channel,)))
        elif type(channel) is not TupleType or not channel[0].startswith('inst'):
            m.append((localization.GetByLabel('UI/Chat/ChannelWindow/JoinChannel'), sm.StartService('vivox').JoinChannel, (channel,)))
        m.append(None)
    m += sm.GetService('menu').CharacterMenu(charID)
    return m



def GetBroadcastScopeName(scope, where = BROADCAST_UNIVERSE):
    labelName = broadcastScopes.get(scope, {}).get(where, 'UI/Fleet/FleetBroadcast/BroadcastRangeAll')
    return localization.GetByLabel(labelName)



def GetBroadcastWhere(name):
    return broadcastRanges.get(name, defaultBroadcastRange)



def GetBroadcastWhereName(scope):
    return localization.GetByLabel(broadcastRangeNames[scope])



def GetBroadcastName(broadcastType):
    return localization.GetByLabel(broadcastNames[broadcastType])


exports = util.AutoExports('fleetbr', locals())

