import trinity
import uix
import math
import blue
import util
import string
import geo2
import mapcommon
from mapcommon import LegendItem, COLORCURVE_SECURITY, COLOR_STANDINGS_GOOD, COLOR_STANDINGS_BAD, COLOR_STANDINGS_NEUTRAL
from collections import defaultdict
import taleConst
DEFAULT_MAX_COLOR = trinity.TriColor(0.0, 1.0, 0.0)

def ColorStarsByDevIndex(colorInfo, starColorMode, indexID, indexName):
    sovSvc = sm.GetService('sov')
    indexData = sovSvc.GetAllDevelopmentIndicesMapped()
    color = trinity.TriColor(0.4, 0.4, 1.0)
    for (solarSystemID, info,) in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        if levelInfo.level == 0:
            continue
        size = levelInfo.level * 2.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         1.0,
         '%s %s: %d' % (indexName, mls.SKILL_LEVEL, levelInfo.level),
         color)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_HAS_NO_DEV_INDEX, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_DEV_INDEX, color, data=None))



def ColorStarsByAssets(colorInfo, starColorMode):
    myassets = sm.GetService('assets').GetAll('allitems', blueprintOnly=0, isCorp=0)
    assetColor = trinity.TriColor(0.5, 0.1, 0.0)
    bySystemID = {}
    stuffToPrime = []
    for (solarsystemID, station,) in myassets:
        stuffToPrime.append(station.stationID)
        stuffToPrime.append(solarsystemID)
        if solarsystemID not in bySystemID:
            bySystemID[solarsystemID] = []
        bySystemID[solarsystemID].append(station)

    if stuffToPrime:
        cfg.evelocations.Prime(stuffToPrime)
    for (solarsystemID, stations,) in bySystemID.iteritems():
        total = 0
        c = []
        for station in stations:
            subc = '%s: %d' % (uix.EditStationName(cfg.evelocations.Get(station.stationID).name, usename=1), station.itemCount)
            c.append((subc, ('OnClick', 'OpenAssets', (station.stationID,))))
            total += station.itemCount

        size = 4.0 + math.log10(total)
        colorInfo.solarSystemDict[solarsystemID] = (size,
         1.0,
         ([mls.UI_SHARED_MAPOPS15], c),
         assetColor)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_ASSETS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_ASSETS, assetColor, data=None))



def ColorStarsByVisited(colorInfo, starColorMode):
    history = sm.RemoteSvc('map').GetSolarSystemVisits()
    visited = []
    for entry in history:
        visited.append((entry.lastDateTime, entry.solarSystemID, entry.visits))

    if len(visited):
        divisor = 1.0 / float(len(visited))
    visited.sort()
    starmap = sm.GetService('starmap')
    caption = mls.UI_SHARED_MAP_LAST_VISITED
    for (i, (lastDateTime, solarSystemID, visits,),) in enumerate(visited):
        solarsystem = starmap.map.GetItem(solarSystemID)
        comment = caption % {'systemName': solarsystem.itemName,
         'count': visits,
         'dateTime': util.FmtDate(lastDateTime, 'll')}
        colorInfo.solarSystemDict[solarSystemID] = (3.0 + math.log10(float(visits)) * 4.0,
         float(i) * divisor,
         comment,
         None)

    colorInfo.colorList = (trinity.TriColor(0.3, 0.0, 0.0), trinity.TriColor(1.0, 0.0, 0.0), trinity.TriColor(1.0, 1.0, 0.0))
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_HAS_NOT_VISITED, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_SHORTEST_TIME_SINCE_VISTITED, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_HAS_LONGEST_TIME_SINCE_VISTITED, colorInfo.colorList[2], data=None))



def ColorStarsBySecurity(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        secStatus = starmap.map.GetSecurityStatus(solarSystemID)
        colorInfo.solarSystemDict[solarSystemID] = (2,
         secStatus,
         '%s: ' % mls.UI_SHARED_MAPSECSTATUS + str(secStatus),
         None)

    colorInfo.colorList = COLORCURVE_SECURITY
    colorInfo.legend.add(LegendItem(0, '%s: 1.0' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[10], data=None))
    colorInfo.legend.add(LegendItem(1, '%s: 0.9' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[9], data=None))
    colorInfo.legend.add(LegendItem(2, '%s: 0.8' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[8], data=None))
    colorInfo.legend.add(LegendItem(3, '%s: 0.7' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[7], data=None))
    colorInfo.legend.add(LegendItem(4, '%s: 0.6' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[6], data=None))
    colorInfo.legend.add(LegendItem(5, '%s: 0.5' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[5], data=None))
    colorInfo.legend.add(LegendItem(6, '%s: 0.4' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[4], data=None))
    colorInfo.legend.add(LegendItem(7, '%s: 0.3' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[3], data=None))
    colorInfo.legend.add(LegendItem(8, '%s: 0.2' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[2], data=None))
    colorInfo.legend.add(LegendItem(9, '%s: 0.1' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[1], data=None))
    colorInfo.legend.add(LegendItem(10, '%s: 0.0' % mls.UI_INFOWND_SECURITYLEVEL, COLORCURVE_SECURITY[0], data=None))



def ColorStarsBySovChanges(colorInfo, starColorMode, changeMode):
    if changeMode in (mapcommon.SOV_CHANGES_OUTPOST_GAIN, mapcommon.SOV_CHANGES_SOV_GAIN):
        color = trinity.TriColor(0.0, 1.0, 0.0)
    elif changeMode in (mapcommon.SOV_CHANGES_OUTPOST_LOST, mapcommon.SOV_CHANGES_SOV_LOST):
        color = trinity.TriColor(1.0, 0.0, 0.0)
    else:
        color = trinity.TriColor(0.9, 0.6, 0.1)
    changes = GetSovChangeList(changeMode)
    for (solarSystemID, comments,) in changes.iteritems():
        colorInfo.solarSystemDict[solarSystemID] = (len(comments) * 2.0,
         1.0,
         '<br><br>'.join(comments),
         color)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_HAS_NO_SOV_CHANGES, mapcommon.NEUTRAL_COLOR, None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_SOV_CHANGES, color, None))



def GetSovChangeList(changeMode):
    data = sm.GetService('sov').GetRecentActivity()
    changes = []
    resultMap = {}
    toPrime = set()
    for item in data:
        if item.stationID is None:
            if bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.oldOwnerID is None:
                changes.append((item.solarSystemID, mls.SOVEREIGNTY_SOVGAINED, (None, item.ownerID)))
                toPrime.add(item.ownerID)
            elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_LOST) and item.ownerID is None:
                changes.append((item.solarSystemID, mls.SOVEREIGNTY_SOVLOST, (item.oldOwnerID, None)))
                toPrime.add(item.oldOwnerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.oldOwnerID is None:
            changes.append((item.solarSystemID, mls.SOVEREIGNTY_OUTPOST_CONSTRUCTED, (None, item.ownerID)))
            toPrime.add(item.ownerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.ownerID is not None:
            changes.append((item.solarSystemID, mls.SOVEREIGNTY_OUTPOST_CONQUERED, (item.ownerID, item.oldOwnerID)))
            toPrime.add(item.ownerID)
            toPrime.add(item.oldOwnerID)

    cfg.eveowners.Prime(list(toPrime))
    for (solarSystemID, text, owners,) in changes:
        kw = {'oldOwner': '' if owners[0] is None else cfg.eveowners.Get(owners[0]).ownerName,
         'owner': '' if owners[1] is None else cfg.eveowners.Get(owners[1]).ownerName}
        if solarSystemID not in resultMap:
            resultMap[solarSystemID] = []
        resultMap[solarSystemID].append(text % kw)

    return resultMap



def ColorStarsByFactionStandings(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    colorByFaction = {}
    neutral = trinity.TriColor(*COLOR_STANDINGS_NEUTRAL)
    for factionID in starmap.GetAllFactionsAndAlliances():
        colorByFaction[factionID] = trinity.TriColor(*starmap.GetColorByStandings(factionID))

    allianceSolarSystems = starmap.GetAllianceSolarSystems()
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        color = colorByFaction.get(starmap._GetFactionIDFromSolarSystem(allianceSolarSystems, solarSystemID), neutral)
        colorInfo.solarSystemDict[solarSystemID] = (2.0,
         1.0,
         mls.UI_FLEET_STANDINGONLY,
         color)

    colorInfo.legend.add(LegendItem(0, mls.UI_FLEET_GOODSTANDING, trinity.TriColor(*COLOR_STANDINGS_GOOD), data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_GENERIC_STANDINGNEUTRAL, trinity.TriColor(*COLOR_STANDINGS_NEUTRAL), data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_BADSTANDINGS, trinity.TriColor(*COLOR_STANDINGS_BAD), data=None))



def ColorStarsByFaction(colorInfo, starColorMode):
    factionID = starColorMode[1]
    starmap = sm.GetService('starmap')
    allianceSolarSystems = starmap.GetAllianceSolarSystems()
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        if factionID == mapcommon.STARMODE_FILTER_EMPIRE:
            secClass = starmap.map.GetSecurityStatus(solarSystemID)
            if not util.IsFaction(solarsystem.factionID) or secClass == const.securityClassZeroSec:
                continue
        elif factionID >= 0:
            if solarsystem.factionID != factionID and (not allianceSolarSystems.has_key(solarSystemID) or allianceSolarSystems[solarSystemID] != factionID):
                continue
        if solarsystem.factionID is not None:
            sovHolderID = solarsystem.factionID
        elif allianceSolarSystems.has_key(solarSystemID):
            sovHolderID = allianceSolarSystems[solarSystemID]
        else:
            continue
        col = starmap.GetFactionOrAllianceColor(sovHolderID)
        name = cfg.eveowners.Get(sovHolderID).name
        colorInfo.solarSystemDict[solarSystemID] = (2.0,
         0.0,
         '%s: %s' % (mls.UI_SHARED_MAPSOVEREIGNTY, name),
         col)
        colorInfo.legend.add(LegendItem(None, name, col, data=sovHolderID))




def ColorStarsByMilitia(colorInfo, starColorMode):
    factionID = starColorMode[1]
    facWar = sm.GetService('facwar')
    starmap = sm.GetService('starmap')
    warfactionSolarSystems = facWar.GetFacWarSystems()
    warFactions = facWar.GetWarFactions()
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        warfactionSolarSystem = warfactionSolarSystems.get(solarSystemID)
        occupierID = None
        if warfactionSolarSystem:
            occupierID = warfactionSolarSystem.get('occupierID')
        if factionID == -1:
            if not warfactionSolarSystems.has_key(solarSystemID):
                continue
        elif factionID != -1:
            if occupierID != factionID:
                continue
        if occupierID not in warFactions:
            continue
        if occupierID:
            col = starmap.GetFactionOrAllianceColor(occupierID)
            name = cfg.eveowners.Get(occupierID).name
            colorInfo.solarSystemDict[solarSystemID] = (2,
             starmap.map.GetSecurityStatus(solarSystemID),
             '%s: %s' % (mls.UI_SHARED_OCCUPANCY, name),
             col)
            colorInfo.legend.add(LegendItem(None, name, col, data=occupierID))




def ColorStarsByMilitiaActions(colorInfo, starColorMode):
    if not eve.session.warfactionid:
        if starColorMode[1] in (-1, mapcommon.STARMODE_FILTER_FACWAR_MINE):
            return 
    starFaction = [starColorMode[1]]
    starmap = sm.GetService('starmap')
    if eve.session.warfactionid:
        if starColorMode[1] == mapcommon.STARMODE_FILTER_FACWAR_ENEMY:
            starFaction = sm.GetService('facwar').GetEnemies(eve.session.warfactionid)
        elif starColorMode[1] == mapcommon.STARMODE_FILTER_FACWAR_MINE:
            starFaction = [eve.session.warfactionid]
    information = {mapcommon.STARMODE_MILITIAOFFENSIVE: {'mode': 'attacking',
                                           'factions': starFaction},
     mapcommon.STARMODE_MILITIADEFENSIVE: {'mode': 'defending',
                                           'factions': starFaction}}.get(starColorMode[0], None)
    multiplier = 1.0
    if information:
        history = starmap.GetVictoryPoints()
        blue.pyos.synchro.Yield()
        maxPoints = 1
        maxThreshold = 1
        for factionID in information.get('factions'):
            tmp = history.get(factionID).get(information.get('mode'))
            for (solarSystemID, d,) in tmp.iteritems():
                threshold = d.get('threshold')
                current = d.get('current')
                if threshold > maxThreshold:
                    maxThreshold = threshold
                if current > maxPoints:
                    maxPoints = current


        multiplier = max(1.0, maxThreshold / maxPoints)
        for factionID in information.get('factions'):
            tmp = history.get(factionID).get(information.get('mode'))
            for (solarSystemID, d,) in tmp.iteritems():
                threshold = d.get('threshold')
                current = d.get('current')
                state = d.get('state')
                solarsystem = starmap.map.GetItem(solarSystemID)
                if solarsystem is None:
                    continue
                age = multiplier * float(current)
                size = 2.0 + pow(age, 0.35)
                comment = solarsystem.itemName + ': ' + starmap.neocom.GetSolarSystemStatusText(state, True)
                col = starmap.GetFactionOrAllianceColor(factionID)
                colorInfo.solarSystemDict[solarSystemID] = (size,
                 age,
                 comment,
                 col)
                name = cfg.eveowners.Get(factionID).name
                colorInfo.legend.add(LegendItem(None, name, col, data=factionID))


        colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.0))



def ColorStarsByRegion(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        constellation = starmap.map.GetItem(solarsystem.locationID)
        region = starmap.map.GetItem(constellation.locationID)
        col = starmap.GetRegionColor(region.itemID)
        colorInfo.solarSystemDict[solarSystemID] = (2,
         1.0,
         '%s: ' % mls.UI_GENERIC_REGION + region.itemName,
         col)
        colorInfo.legend.add(LegendItem(None, region.itemName, col, data=region.itemID))




def ColorStarsByCargoIllegality(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    CONFISCATED_COLOR = trinity.TriColor(0.8, 0.4, 0.0)
    ATTACKED_COLOR = trinity.TriColor(1.0, 0.0, 0.0)
    inv = eve.GetInventoryFromId(eve.session.shipid)
    factionIllegality = {}
    shipCargo = inv.List()
    while len(shipCargo) > 0:
        item = shipCargo.pop(0)
        if item.groupID in [const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer]:
            shipCargo.extend(eve.GetInventoryFromId(item.itemID).List())
        itemIllegalities = cfg.invtypes.Get(item.typeID).Illegality()
        if itemIllegalities:
            for (factionID, illegality,) in itemIllegalities.iteritems():
                if factionID not in factionIllegality:
                    factionIllegality[factionID] = {}
                if item.typeID not in factionIllegality[factionID]:
                    factionIllegality[factionID][item.typeID] = [max(0.0, illegality.confiscateMinSec), max(0.0, illegality.attackMinSec)]


    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        colour = None
        if solarsystem.factionID is None:
            continue
        if solarsystem.factionID not in factionIllegality:
            continue
        systemDescription = ''
        systemIllegality = False
        for typeID in factionIllegality[solarsystem.factionID]:
            if starmap.map.GetSecurityStatus(solarSystemID) >= factionIllegality[solarsystem.factionID][typeID][1]:
                systemIllegality = True
                if not colour or colour[0] < 2:
                    colour = (2, ATTACKED_COLOR)
                if systemDescription != '':
                    systemDescription += '<br>'
                systemDescription += mls.UI_SHARED_MAPHINT1 % {'stuff': cfg.invtypes.Get(typeID).name}
            elif starmap.map.GetSecurityStatus(solarSystemID) >= factionIllegality[solarsystem.factionID][typeID][0]:
                systemIllegality = True
                if not colour:
                    colour = (1, CONFISCATED_COLOR)
                if systemDescription != '':
                    systemDescription += '<br>'
                systemDescription += mls.UI_SHARED_MAPHINT2 % {'item': cfg.invtypes.Get(typeID).name}

        if systemIllegality:
            colorInfo.solarSystemDict[solarSystemID] = (3.0,
             0.0,
             systemDescription,
             colour[1])

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_CARGO_CARRIES_NO_CONSEQUENCES, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_CARGO_WILL_BE_CONFISCATED, CONFISCATED_COLOR, data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_CARGO_WILL_PROMT_ATTACK, ATTACKED_COLOR, data=None))



def ColorStarsByNumPilots(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
        caption = mls.UI_SHARED_MAP_HINT_PILOTS_IN_SPACE
        captionPlural = mls.UI_SHARED_MAP_HINT_PILOTS_IN_SPACE_PLURAL
    else:
        caption = mls.UI_SHARED_MAP_HINT_PILOTS_DOCKED
        captionPlural = mls.UI_SHARED_MAP_HINT_PILOTS_DOCKED_PLURAL
    (sol, sta, statDivisor,) = sm.ProxySvc('machoNet').GetClusterSessionStatistics()
    maxCount = 0
    total = 0
    docked = 0
    multiplier = 1.0
    pilotcountDict = {}
    for sfoo in sol.iterkeys():
        solarSystemID = sfoo + 30000000
        amount_docked = sta.get(sfoo, 0) / statDivisor
        amount_inspace = (sol.get(sfoo, 0) - sta.get(sfoo, 0)) / statDivisor
        if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
            amount = amount_inspace
        else:
            amount = amount_docked
        pilotcountDict[solarSystemID] = amount
        total = total + amount
        if amount > maxCount:
            maxCount = amount

    if maxCount > 0:
        multiplier /= math.sqrt(maxCount)
    sorted = pilotcountDict.values()
    sorted.sort()
    for solarSystemID in pilotcountDict.iterkeys():
        solarsystem = starmap.map.GetItem(solarSystemID)
        pilotCount = pilotcountDict[solarSystemID]
        if pilotCount == 0:
            continue
        comment = (caption if pilotCount == 1 else captionPlural) % {'count': pilotCount,
         'systemName': solarsystem.itemName}
        size = 2 * math.sqrt(pilotCount)
        colorInfo.solarSystemDict[solarSystemID] = (size,
         math.sqrt(pilotCount) * multiplier,
         comment,
         None)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.0, 0.0))
    colorCurve = starmap.GetColorCurve(colorInfo.colorList)
    startColor = starmap.GetColorCurveValue(colorCurve, multiplier)
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_PILOTS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_ONE_PILOT, startColor, data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_MAX_NUM_PILOTS % {'maxNumPilots': maxCount}, colorInfo.colorList[-1], data=None))



def ColorStarsByStationCount(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starmap.stationCountCache is None:
        starmap.stationCountCache = sm.RemoteSvc('map').GetStationCount()
    history = starmap.stationCountCache
    maxCount = 0
    for (solarSystemID, amount,) in history:
        if amount > maxCount:
            maxCount = amount

    if maxCount > 0:
        multiplier = 1.0 / float(maxCount)
    caption = mls.UI_SHARED_MAP_STATIONS_IN_SYSTEM
    for (solarSystemID, amount,) in history:
        solarsystem = starmap.map.GetItem(solarSystemID)
        if solarsystem is None:
            continue
        age = multiplier * float(amount)
        size = 2.0 + pow(age, 0.5) * 4.0
        comment = caption % {'systemName': solarsystem.itemName,
         'count': amount}
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         comment,
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.0))
    colorCurve = starmap.GetColorCurve(colorInfo.colorList)
    startColor = starmap.GetColorCurveValue(colorCurve, multiplier)
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_STATIONS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_ONE_STATION, startColor, data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_MAX_NUM_STATIONS % {'maxNumStations': maxCount}, colorInfo.colorList[-1], data=None))



def ColorStarsByDungeons(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_DUNGEONS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceComplexMap(eve.session.languageID)
    elif starColorMode == mapcommon.STARMODE_DUNGEONSAGENTS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceAgentsMap(eve.session.languageID)
    if dungeons is None:
        return 
    solmap = {}
    for (solarSystemID, dungeonID, difficulty, dungeonName,) in dungeons:
        if solarSystemID in solmap:
            solmap[solarSystemID].append((dungeonID, difficulty, dungeonName))
        else:
            solmap[solarSystemID] = [(dungeonID, difficulty, dungeonName)]

    for solarSystemID in solmap:
        solarsystem = starmap.map.GetItem(solarSystemID)
        if solarsystem is None:
            continue
        comments = []
        diff = 1
        for (dungeonID, difficulty, dungeonName,) in solmap[solarSystemID]:
            ded = ''
            if difficulty:
                ded = ' ' + mls.UI_SHARED_DED % {'difficulty': difficulty}
                diff = max(diff, difficulty)
            comments.append('\xb7 %s%s' % (dungeonName, ded))

        diff = (10 - diff) / 9.0
        colorInfo.solarSystemDict[solarSystemID] = (3.0 * len(solmap[solarSystemID]),
         diff,
         '<br><br>'.join(comments),
         None)

    colorInfo.colorList = COLORCURVE_SECURITY
    colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 1}, starmap.GetColorCurveValue(colorCurve, 9 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 2}, starmap.GetColorCurveValue(colorCurve, 8 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 3}, starmap.GetColorCurveValue(colorCurve, 7 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(3, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 4}, starmap.GetColorCurveValue(colorCurve, 6 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(4, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 5}, starmap.GetColorCurveValue(colorCurve, 5 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(5, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 6}, starmap.GetColorCurveValue(colorCurve, 4 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(6, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 7}, starmap.GetColorCurveValue(colorCurve, 3 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(7, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 8}, starmap.GetColorCurveValue(colorCurve, 2 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(8, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 9}, starmap.GetColorCurveValue(colorCurve, 1 / 9.0), data=None))
    colorInfo.legend.add(LegendItem(9, mls.UI_SHARED_MAP_LEGEND_DED % {'difficulty': 10}, starmap.GetColorCurveValue(colorCurve, 0 / 9.0), data=None))



def ColorStarsByJumps1Hour(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    historyDB = sm.RemoteSvc('map').GetHistory(1, 1)
    history = []
    for entry in historyDB:
        if entry.value1 > 0:
            history.append((entry.solarSystemID, entry.value1))

    maxCount = 0
    for (solarSystemID, amount,) in history:
        if amount > maxCount:
            maxCount = amount

    if maxCount > 1:
        divisor = 1.0 / math.log(pow(float(maxCount), 4.0))
        c = 0
        if len(history):
            jumpCount = 1.0 / float(len(history))
        caption = mls.UI_SHARED_MAP_JUMPS_IN_THE_LAST_HOUR
        for (solarSystemID, amount,) in history:
            solarsystem = starmap.map.GetItem(solarSystemID)
            if solarsystem is None:
                continue
            age = divisor * math.log(pow(float(amount), 4.0))
            size = 2.0 + pow(age, 0.5) * 2.0
            comment = caption % {'systemName': solarsystem.itemName,
             'count': amount}
            colorInfo.solarSystemDict[solarSystemID] = (size,
             age,
             comment,
             None)
            c += 1

    colorInfo.colorList = (trinity.TriColor(0.0, 0.0, 1.0),
     trinity.TriColor(0.0, 1.0, 1.0),
     trinity.TriColor(1.0, 1.0, 0.0),
     trinity.TriColor(1.0, 0.0, 0.0))
    colorInfo.legend.add(LegendItem(0, '%s: 0' % mls.UI_GENERIC_JUMPS, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, '%s: %d' % (mls.UI_GENERIC_JUMPS, maxCount), colorInfo.colorList[-1], data=None))



def ColorStarsByKills(colorInfo, starColorMode, statID, hours):
    starmap = sm.GetService('starmap')
    if hours != 1:
        timestep = '%d %s' % (hours, mls.UI_GENERIC_HOURS)
    else:
        timestep = mls.UI_GENERIC_HOUR
    historyDB = sm.RemoteSvc('map').GetHistory(statID, hours)
    history = []
    for entry in historyDB:
        if entry.value1 - entry.value2 > 0:
            history.append((entry.solarSystemID, entry.value1 - entry.value2))

    maxCount = 0
    for (solarSystemID, amount,) in history:
        if amount > maxCount:
            maxCount = amount

    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    c = 0
    caption = mls.UI_SHARED_MAP_SHIPS_DESTROYED_IN_TIME
    for (solarSystemID, amount,) in history:
        solarsystem = starmap.map.GetItem(solarSystemID)
        if solarsystem is None:
            continue
        age = divisor * float(amount)
        size = 2.0 + pow(amount, 0.5) * 4.0
        comment = caption % {'systemName': solarsystem.itemName,
         'count': amount,
         'timeStep': timestep}
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         comment,
         None)
        c += 1

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, '%s: 0' % mls.UI_GENERIC_KILLS, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, '%s: %d' % (mls.UI_GENERIC_KILLS, maxCount), colorInfo.colorList[-1], data=None))



def ColorStarsByPodKills(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_PODKILLS24HR:
        historyDB = sm.RemoteSvc('map').GetHistory(3, 24)
        timestep = '24 ' + mls.UI_GENERIC_HOURS
    else:
        historyDB = sm.RemoteSvc('map').GetHistory(3, 1)
        timestep = mls.UI_GENERIC_HOUR
    history = []
    for entry in historyDB:
        if entry.value3 > 0:
            history.append((entry.solarSystemID, entry.value3))

    maxCount = 0
    for (solarSystemID, amount,) in history:
        if amount > maxCount:
            maxCount = amount

    divisor = 0.0
    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    c = 0
    caption = mls.UI_SHARED_MAP_POD_KILLS_IN_LAST
    for (solarSystemID, amount,) in history:
        solarsystem = starmap.map.GetItem(solarSystemID)
        if solarsystem is None:
            continue
        age = divisor * float(amount)
        size = 2.0 + pow(amount, 0.5) * 4.0
        comment = caption % {'systemName': solarsystem.itemName,
         'count': amount,
         'timeStep': timestep}
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         comment,
         None)
        c += 1

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, '%s: 0' % mls.UI_GENERIC_PODS_DESTROYED, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, '%s: %d' % (mls.UI_GENERIC_PODS_DESTROYED, maxCount), colorInfo.colorList[-1], data=None))



def ColorStarsByFactionKills(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    historyDB = sm.RemoteSvc('map').GetHistory(3, 24)
    history = []
    for entry in historyDB:
        if entry.value2 > 0:
            history.append((entry.solarSystemID, entry.value2))

    maxCount = 0
    for (solarSystemID, amount,) in history:
        if amount > maxCount:
            maxCount = amount

    divisor = 0.0
    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    c = 0
    caption = mls.UI_SHARED_MAP_FACTION_SHIPS_KILLED
    for (solarSystemID, amount,) in history:
        solarsystem = starmap.map.GetItem(solarSystemID)
        if solarsystem is None:
            continue
        age = divisor * float(amount)
        size = 1.0 + math.log(amount) * 2.0
        comment = caption % {'systemName': solarsystem.itemName,
         'count': amount,
         'timeStep': '24 %s' % mls.UI_GENERIC_HOURS}
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         comment,
         None)
        c += 1

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, '%s: 0' % mls.UI_GENERIC_KILLS, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, '%s: %d' % (mls.UI_GENERIC_KILLS, maxCount), colorInfo.colorList[-1], data=None))



def ColorStarsByBookmarks(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    bms = sm.GetService('addressbook').GetMapBookmarks()
    highlightSystems = {}
    for bookmark in bms:
        item = starmap.map.GetItem(bookmark.locationID)
        if item is not None and item.typeID == const.typeSolarSystem:
            solarSystemID = bookmark.locationID
        else:
            solarSystemID = bookmark.itemID
        memo = bookmark.memo
        if len(memo):
            tabindex = string.find(memo, '\t')
            if tabindex != -1:
                comment = memo[:tabindex]
        else:
            comment = None
        if not highlightSystems.has_key(solarSystemID):
            highlightSystems[solarSystemID] = '<br>' + comment
        else:
            highlightSystems[solarSystemID] += '<br>' + comment

    for system in highlightSystems:
        colorInfo.solarSystemDict[system] = (4,
         1.0,
         highlightSystems[system],
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_BOOKMARKS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_BOOKMARKS_PRESENT, colorInfo.colorList[-1], data=None))



def ColorStarsByCynosuralFields(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    fields = sm.RemoteSvc('map').GetBeaconCount()
    highlightSystems = {}
    orange = trinity.TriColor(1.0, 0.4, 0.0, 1.0)
    green = trinity.TriColor(0.2, 1.0, 1.0, 1.0)
    red = trinity.TriColor(1.0, 0.0, 0.0, 1.0)
    for (solarSystemID, cnt,) in fields.iteritems():
        (moduleCnt, structureCnt,) = cnt
        if moduleCnt > 0 and structureCnt > 0:
            ttlcnt = moduleCnt + structureCnt
            colorInfo.solarSystemDict[solarSystemID] = (4 * ttlcnt,
             1.0,
             '%s: %d' % (mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_FIELDS_AND_GENERATORS, ttlcnt),
             red)
        elif moduleCnt:
            colorInfo.solarSystemDict[solarSystemID] = (4 * moduleCnt,
             1.0,
             '%s: %d' % (mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_FIELDS, moduleCnt),
             green)
        elif structureCnt:
            colorInfo.solarSystemDict[solarSystemID] = (4 * structureCnt,
             1.0,
             '%s: %d' % (mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_GENERATORS, structureCnt),
             orange)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_ACTIVE_CYNO_FIELDS_AND_GENERATORS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_FIELDS, green, data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_GENERATORS, orange, data=None))
    colorInfo.legend.add(LegendItem(3, mls.UI_SHARED_MAP_LEGEND_ACTIVE_CYNO_FIELDS_AND_GENERATORS, red, data=None))



def ColorStarsByCorpAssets(colorInfo, starColorMode, assetKey, legendName):
    rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, assetKey)
    solarsystems = {}
    stuffToPrime = []
    for row in rows:
        stationID = row.locationID
        try:
            solarsystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
        except:
            solarsystemID = row.locationID
        if solarsystemID not in solarsystems:
            solarsystems[solarsystemID] = {}
            stuffToPrime.append(solarsystemID)
        if stationID not in solarsystems[solarsystemID]:
            solarsystems[solarsystemID][stationID] = []
            stuffToPrime.append(stationID)
        solarsystems[solarsystemID][stationID].append(row)

    cfg.evelocations.Prime(stuffToPrime)
    for solarsystemID in solarsystems:
        for stationID in solarsystems[solarsystemID]:
            caption = cfg.evelocations.Get(stationID).name
            total = 100000
            color = trinity.TriColor(1.0, 0.8, 0.0, 1.0)

        size = 4.0 + math.log10(total)
        colorInfo.solarSystemDict[solarsystemID] = (size,
         1.0,
         caption,
         color)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.1, 0.0))
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_ASSETS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, legendName, colorInfo.colorList[-1], data=None))



def ColorStarsByServices(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    serviceTypeID = starColorMode[1]
    (stations, opservices, services,) = sm.RemoteSvc('map').GetStationExtraInfo()
    opservDict = {}
    stationIDs = []
    solarsystems = {}
    for each in opservices:
        if each.operationID not in opservDict:
            opservDict[each.operationID] = []
        opservDict[each.operationID].append(each.serviceID)

    if starmap.warFactionByOwner is None and serviceTypeID == const.stationServiceNavyOffices:
        starmap.warFactionByOwner = {}
        factions = sm.GetService('facwar').GetWarFactions().keys()
        for stationRow in stations:
            ownerID = stationRow.ownerID
            if ownerID not in starmap.warFactionByOwner:
                faction = sm.GetService('faction').GetFaction(ownerID)
                if faction and faction in factions:
                    starmap.warFactionByOwner[ownerID] = faction

    for stationRow in stations:
        solarSystemID = stationRow.solarSystemID
        if stationRow.operationID == None:
            continue
        if serviceTypeID not in opservDict[stationRow.operationID]:
            continue
        if serviceTypeID == const.stationServiceNavyOffices and stationRow.ownerID not in starmap.warFactionByOwner:
            continue
        if solarSystemID not in solarsystems:
            solarsystems[solarSystemID] = []
        solarsystems[solarSystemID].append(stationRow.stationID)
        stationIDs.append(stationRow.stationID)

    cfg.evelocations.Prime(stationIDs)
    red = trinity.TriColor(1.0, 0.0, 0.0, 1.0)
    for solarsystemID in solarsystems.iterkeys():
        item = starmap.map.GetItem(solarsystemID)
        if item == None:
            continue
        caption = item.itemName + ':'
        for stationID in solarsystems[solarsystemID]:
            caption += '<br>' + cfg.evelocations.Get(stationID).name

        colorInfo.solarSystemDict[solarsystemID] = (4.0,
         1.0,
         caption,
         red)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.1, 0.0))
    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_SERVICES, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_SERVICES, red, data=None))



def ColorStarsByFleetMembers(colorInfo, starColorMode):
    fleetComposition = sm.GetService('fleet').GetFleetComposition()
    if fleetComposition is not None:
        solarsystems = {}
        for each in fleetComposition:
            if each.solarSystemID not in solarsystems:
                solarsystems[each.solarSystemID] = []
            solarsystems[each.solarSystemID].append(each.characterID)

        for locationID in solarsystems:
            caption = cfg.evelocations.Get(locationID).name + ':'
            for characterID in solarsystems[locationID]:
                caption = caption + '<br>' + cfg.eveowners.Get(characterID).name

            colorInfo.solarSystemDict[locationID] = (4.0,
             1.0,
             caption,
             DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_FLEET_MEMBERS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_FLEET_MEMBERS, DEFAULT_MAX_COLOR, data=None))



def ColorStarsByCorpMembers(colorInfo, starColorMode):
    corp = sm.RemoteSvc('map').GetMyExtraMapInfo()
    if corp is not None:
        corp = corp[:2]
        solarsystems = {}
        for each in corp:
            if each.locationID not in solarsystems:
                solarsystems[each.locationID] = []
            solarsystems[each.locationID].append(each.characterID)

        for locationID in solarsystems:
            caption = cfg.evelocations.Get(locationID).name + ':'
            for characterID in solarsystems[locationID]:
                caption = caption + '<br>' + cfg.eveowners.Get(characterID).name

            colorInfo.solarSystemDict[locationID] = (4,
             1.0,
             caption,
             DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_CORP_MEMBERS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_CORP_MEMBERS, DEFAULT_MAX_COLOR, data=None))



def ColorStarsByMyAgents(colorInfo, starColorMode):
    standingInfo = sm.RemoteSvc('map').GetMyExtraMapInfoAgents().Index('fromID')
    solarsystems = {}
    valid = (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent)
    agentsByID = sm.GetService('agents').GetAgentsByID()
    facWarService = sm.GetService('facwar')
    skills = {}
    for agentID in agentsByID:
        agent = agentsByID[agentID]
        fa = standingInfo.get(agent.factionID, 0.0)
        if fa:
            fa = fa.rank * 10.0
        co = standingInfo.get(agent.corporationID, 0.0)
        if co:
            co = co.rank * 10.0
        ca = standingInfo.get(agent.agentID, 0.0)
        if ca:
            ca = ca.rank * 10.0
        isLimitedToFacWar = False
        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarService.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            isLimitedToFacWar = True
        if agent.agentTypeID in valid and util.CanUseAgent(agent.level, agent.agentTypeID, fa, co, ca, agent.corporationID, agent.factionID, skills) and isLimitedToFacWar == False:
            if agent.stationID:
                if agent.solarsystemID not in solarsystems:
                    solarsystems[agent.solarsystemID] = {}
                if agent.stationID not in solarsystems[agent.solarsystemID]:
                    solarsystems[agent.solarsystemID][agent.stationID] = []
                solarsystems[agent.solarsystemID][agent.stationID].append(agent)

    npcDivisions = sm.GetService('agents').GetDivisions()
    for solarsystemID in solarsystems:
        caption = ''
        totalAgents = 0
        for (stationID, agents,) in solarsystems[solarsystemID].iteritems():
            caption += '<b>%s:</b><br>' % uix.EditStationName(cfg.evelocations.Get(stationID).name, 1)
            for agent in agents:
                caption += '%s (%s, %s: %s)<br>' % (cfg.eveowners.Get(agent.agentID).name,
                 npcDivisions[agent.divisionID].divisionName,
                 mls.UI_GENERIC_LEVEL,
                 agent.level)

            caption += '<br>'
            totalAgents += len(agents)

        colorInfo.solarSystemDict[solarsystemID] = (int(totalAgents),
         1.0,
         caption,
         DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_NO_AVAILABLE_AGENTS, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_HAS_AVAILABLE_AGENTS, DEFAULT_MAX_COLOR, data=None))



def ColorStarsByAvoidedSystems(colorInfo, starColorMode):
    avoidanceSolarSystemIDs = sm.GetService('pathfinder').GetAvoidanceItems(True)
    red = trinity.TriColor(1.0, 0.0, 0.0)
    hint = mls.UI_SHARED_MAPSYSTEMISAVOIDED
    for solarSystemID in avoidanceSolarSystemIDs:
        colorInfo.solarSystemDict[solarSystemID] = (1,
         1.0,
         hint,
         red)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_SYSTEM_NOT_AVOIDED, mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_SYSTEM_AVOIDED, red, data=None))



def ColorStarsByRealSunColor(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    cacheSunTypes = starmap.map.GetMapCache()['sunTypes']
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        star = mapcommon.SUN_DATA[cacheSunTypes[solarSystemID]]
        secStatus = starmap.map.GetSecurityStatus(solarSystemID)
        colorInfo.solarSystemDict[solarSystemID] = (1,
         0.0,
         '',
         trinity.TriColor(*star.color))

    colorInfo.overglowFactor = mapcommon.ACTUAL_COLOR_OVERGLOWFACTOR
    for (typeID, sunType,) in mapcommon.SUN_DATA.iteritems():
        name = cfg.invtypes.Get(typeID).typeName
        colorInfo.legend.add(LegendItem(name, name, trinity.TriColor(*sunType.color), data=None))




def ColorStarsByPIScanRange(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    highlightSystems = {}
    playerLoc = cfg.evelocations.Get(session.solarsystemid2)
    playerPos = (playerLoc.x, playerLoc.y, playerLoc.z)
    skills = sm.GetService('skills').MySkillLevelsByID()
    remoteSensing = skills.get(const.typeRemoteSensing, 0)
    for (particleID, solarSystemID,) in starmap.particleIDToSystemIDMap.iteritems():
        systemLoc = cfg.evelocations.Get(solarSystemID)
        systemPos = (systemLoc.x, systemLoc.y, systemLoc.z)
        dist = geo2.Vec3Distance(playerPos, systemPos) / const.LIGHTYEAR
        proximity = None
        for (i, each,) in enumerate(const.planetResourceScanningRanges):
            if not i >= 5 - remoteSensing:
                continue
            if each >= dist:
                proximity = i

        if proximity is not None:
            colorInfo.solarSystemDict[solarSystemID] = (max(1, proximity),
             1.0 / 5.0 * proximity,
             mls.UI_PI_SCAN_RANGE_HINT % (dist,),
             None)

    colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
    for (i, each,) in enumerate(const.planetResourceScanningRanges):
        if not i >= 5 - remoteSensing:
            continue
        colorInfo.legend.add(LegendItem(i, mls.UI_PI_SCANRANGELEGEND % const.planetResourceScanningRanges[i], starmap.GetColorCurveValue(colorCurve, 1.0 / 5.0 * i), data=None))




def ColorStarsByPlanetType(colorInfo, starColorMode):
    planetTypeID = starColorMode[1]
    starmap = sm.GetService('starmap')
    systems = defaultdict(int)
    for info in starmap.map.IteratePlanetInfo():
        if info.typeID == planetTypeID:
            systems[info.solarSystemID] += 1

    maxCount = max(systems.itervalues())
    if maxCount > 1:
        divisor = 1.0 / (maxCount - 1)
    planetTypeName = cfg.invtypes.Get(planetTypeID).typeName
    caption = planetTypeName + ': %d'
    for (solarSystemID, count,) in systems.iteritems():
        solarsystem = starmap.map.GetItem(solarSystemID)
        if maxCount > 1:
            age = divisor * float(count)
        else:
            age = 1.0
        size = 2.0 + pow(count, 0.5) * 2.0
        comment = caption % count
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         comment,
         None)

    colorInfo.colorList = (trinity.TriColor(0.46, 0.34, 0.1), trinity.TriColor(0.3, 1.0, 0.3))
    if maxCount > 1:
        colorInfo.legend.add(LegendItem(0, caption % 1, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, caption % maxCount, colorInfo.colorList[-1], data=None))



def ColorStarsByMyColonies(colorInfo, starColorMode):
    planetSvc = sm.GetService('planetSvc')
    planetRows = planetSvc.GetMyPlanets()
    if len(planetRows):
        mapSvc = sm.GetService('map')
        systems = defaultdict(int)
        for row in planetRows:
            systems[row.solarSystemID] += 1

        maxCount = max(systems.itervalues())
        divisor = 1.0 if maxCount == 1 else 1.0 / (maxCount - 1)
        caption = mls.UI_PI_COLONIES + ': %d'
        for (solarSystemID, count,) in systems.iteritems():
            solarsystem = mapSvc.GetItem(solarSystemID)
            if maxCount > 1:
                age = divisor * float(count - 1)
            else:
                age = 1.0
            size = 2.0 + pow(count, 0.5) * 4.0
            comment = caption % count
            colorInfo.solarSystemDict[solarSystemID] = (size,
             age,
             comment,
             None)

        colorInfo.colorList = (trinity.TriColor(0.0, 0.22, 0.55), trinity.TriColor(0.2, 0.5, 1.0))
        if maxCount > 1:
            colorInfo.legend.add(LegendItem(0, caption % 1, colorInfo.colorList[0], data=None))
        colorInfo.legend.add(LegendItem(1, caption % maxCount, colorInfo.colorList[-1], data=None))



def ColorStarsByIncursions(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursions()
    yellow = trinity.TriColor(1.0, 1.0, 0.0)
    orange = trinity.TriColor(1.0, 0.4, 0.0)
    for (solarSystemID, sceneType,) in participatingSystems:
        if sceneType == taleConst.scenesTypes.staging:
            colorInfo.solarSystemDict[solarSystemID] = (5,
             0,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_STAGING,
             yellow)
        elif sceneType == taleConst.scenesTypes.vanguard:
            colorInfo.solarSystemDict[solarSystemID] = (2.5,
             1,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_PARTICIPANT,
             orange)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_INCURSION_STAGING, yellow, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_INCURSION_PARTICIPANT, orange, data=None))



def ColorStarsByIncursionsGM(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursionsGM()
    green = trinity.TriColor(0.0, 1.0, 0.0)
    yellow = trinity.TriColor(1.0, 1.0, 0.0)
    orange = trinity.TriColor(1.0, 0.4, 0.0)
    red = trinity.TriColor(1.0, 0.0, 0.0)
    for (solarSystemID, sceneType,) in participatingSystems:
        if sceneType == taleConst.scenesTypes.staging:
            colorInfo.solarSystemDict[solarSystemID] = (5,
             0,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_STAGING,
             green)
        elif sceneType == taleConst.scenesTypes.vanguard:
            colorInfo.solarSystemDict[solarSystemID] = (2.5,
             1,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_VANGUARD,
             yellow)
        elif sceneType == taleConst.scenesTypes.assault:
            colorInfo.solarSystemDict[solarSystemID] = (2.5,
             2,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_ASSAULT,
             orange)
        elif sceneType == taleConst.scenesTypes.headquarters:
            colorInfo.solarSystemDict[solarSystemID] = (2.5,
             3,
             mls.UI_SHARED_MAP_LEGEND_INCURSION_HQ,
             red)

    colorInfo.legend.add(LegendItem(0, mls.UI_SHARED_MAP_LEGEND_INCURSION_STAGING, green, data=None))
    colorInfo.legend.add(LegendItem(1, mls.UI_SHARED_MAP_LEGEND_INCURSION_VANGUARD, yellow, data=None))
    colorInfo.legend.add(LegendItem(2, mls.UI_SHARED_MAP_LEGEND_INCURSION_ASSAULT, orange, data=None))
    colorInfo.legend.add(LegendItem(3, mls.UI_SHARED_MAP_LEGEND_INCURSION_HQ, red, data=None))


exports = {'starmap.ColorStarsByDevIndex': ColorStarsByDevIndex,
 'starmap.ColorStarsByAssets': ColorStarsByAssets,
 'starmap.ColorStarsByVisited': ColorStarsByVisited,
 'starmap.ColorStarsBySecurity': ColorStarsBySecurity,
 'starmap.ColorStarsBySovChanges': ColorStarsBySovChanges,
 'starmap.ColorStarsByFactionStandings': ColorStarsByFactionStandings,
 'starmap.ColorStarsByFaction': ColorStarsByFaction,
 'starmap.ColorStarsByMilitia': ColorStarsByMilitia,
 'starmap.ColorStarsByMilitiaActions': ColorStarsByMilitiaActions,
 'starmap.ColorStarsByRegion': ColorStarsByRegion,
 'starmap.ColorStarsByCargoIllegality': ColorStarsByCargoIllegality,
 'starmap.ColorStarsByNumPilots': ColorStarsByNumPilots,
 'starmap.ColorStarsByStationCount': ColorStarsByStationCount,
 'starmap.ColorStarsByDungeons': ColorStarsByDungeons,
 'starmap.ColorStarsByJumps1Hour': ColorStarsByJumps1Hour,
 'starmap.ColorStarsByKills': ColorStarsByKills,
 'starmap.ColorStarsByPodKills': ColorStarsByPodKills,
 'starmap.ColorStarsByFactionKills': ColorStarsByFactionKills,
 'starmap.ColorStarsByBookmarks': ColorStarsByBookmarks,
 'starmap.ColorStarsByCynosuralFields': ColorStarsByCynosuralFields,
 'starmap.ColorStarsByCorpAssets': ColorStarsByCorpAssets,
 'starmap.ColorStarsByServices': ColorStarsByServices,
 'starmap.ColorStarsByFleetMembers': ColorStarsByFleetMembers,
 'starmap.ColorStarsByCorpMembers': ColorStarsByCorpMembers,
 'starmap.ColorStarsByMyAgents': ColorStarsByMyAgents,
 'starmap.ColorStarsByAvoidedSystems': ColorStarsByAvoidedSystems,
 'starmap.ColorStarsByRealSunColor': ColorStarsByRealSunColor,
 'starmap.ColorStarsByPIScanRange': ColorStarsByPIScanRange,
 'starmap.ColorStarsByMyColonies': ColorStarsByMyColonies,
 'starmap.ColorStarsByPlanetType': ColorStarsByPlanetType,
 'starmap.ColorStarsByIncursions': ColorStarsByIncursions,
 'starmap.ColorStarsByIncursionsGM': ColorStarsByIncursionsGM}

