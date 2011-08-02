import blue
import util
import types
import math
import xml.parsers.expat

def CombatLog_CopyText(mail, *args):
    args = {'system': cfg.evelocations.Get(mail.solarSystemID).name,
     'target': cfg.invtypes.Get(mail.victimShipTypeID).name,
     'damage': mail.victimDamageTaken}
    if boot.role == 'client':
        args['security'] = sm.GetService('map').GetSecurityStatus(mail.solarSystemID)
    else:
        systemSecurities = sm.StartService('map').GetSolarSystemPseudoSecurities().Index('solarSystemID')
        args['security'] = systemSecurities[mail.solarSystemID].security
    if mail.moonID is not None:
        args['moon'] = cfg.evelocations.Get(mail.moonID).name
    else:
        args['moon'] = mls.UNKNOWN
    if mail.victimCharacterID is not None:
        if mail.victimCorporationID is None:
            return 
        copy = mls.AGGRESSION_KILLMAIL_MAIN_HEADER_SHIP3
        args['victim'] = cfg.eveowners.Get(mail.victimCharacterID).name
        args['victimc'] = cfg.eveowners.Get(mail.victimCorporationID).name
    elif mail.victimCorporationID is not None:
        copy = mls.AGGRESSION_KILLMAIL_MAIN_HEADER_STRUCTURE3
        args['victim'] = cfg.eveowners.Get(mail.victimCorporationID).name
    else:
        return 
    if mail.victimAllianceID is not None:
        args['victima'] = cfg.eveowners.Get(mail.victimAllianceID).name
    else:
        args['victima'] = mls.UI_GENERIC_UNKNOWN
    if mail.victimFactionID is not None:
        args['victimf'] = cfg.eveowners.Get(mail.victimFactionID).name
    else:
        args['victimf'] = mls.UI_GENERIC_UNKNOWN
    copy = copy % args
    import re
    rx = re.compile('=(\\d+(?:\\.\\d+)?)')
    tempBlob = rx.sub('="\\1"', mail.killBlob)
    attackers = []
    items = []
    pstate = util.Object()
    pstate.Set('state', 0)
    pstate.Set('lastitem', None)

    def _xmlTagStart(tag, attrs):
        state = pstate.Get('state', 0)
        if state == 99:
            return 
        if tag == 'doc':
            return 
        if tag == 'attackers':
            if state != 0:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 1)
        elif tag == 'a':
            if state != 1:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 2)
            attacker = util.KeyVal()
            attacker.characterID = attrs.get('c', None)
            attacker.corporationID = attrs.get('r', None)
            attacker.allianceID = attrs.get('a', None)
            attacker.factionID = attrs.get('f', None)
            attacker.shipTypeID = attrs.get('s', None)
            attacker.weaponTypeID = attrs.get('w', None)
            attacker.damageDone = int(float(attrs.get('d', 0)))
            attacker.secStatusText = attrs.get('t', '0.0')
            attacker.finalBlow = False
            attackers.append((attacker.damageDone, attacker))
        elif tag == 'items':
            if state != 0 and state != 3:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 4)
        elif tag == 'i':
            if state != 4 and state != 5:
                pstate.Set('state', 99)
                return 
            item = util.KeyVal()
            item.typeID = attrs.get('t', None)
            item.flag = int(float(attrs.get('f', 0)))
            item.qtyDropped = int(float(attrs.get('d', 0)))
            item.qtyDestroyed = int(float(attrs.get('x', 0)))
            item.contents = []
            if state == 4:
                pstate.Set('state', 5)
                if item.qtyDropped > 0 and item.qtyDestroyed > 0:
                    item2 = util.KeyVal()
                    item2.typeID = item.typeID
                    item2.flag = item.flag
                    item2.qtyDropped = item.qtyDropped
                    item2.qtyDestroyed = 0
                    item2.contents = []
                    item.qtyDropped = 0
                    items.append(item)
                    items.append(item2)
                else:
                    items.append(item)
                    pstate.Set('lastitem', item)
            else:
                pstate.Set('state', 6)
                litem = pstate.Get('lastitem', None)
                if litem is not None:
                    litem.contents.append(item)
                    pstate.Set('lastitem', litem)
                else:
                    pstate.Set('state', 99)
        else:
            pstate.Set('state', 99)



    def _xmlTagEnd(tag):
        state = pstate.Get('state', 0)
        if state == 99:
            return 
        if tag == 'doc':
            return 
        if tag == 'attackers':
            if state != 1:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 3)
        elif tag == 'a':
            if state != 2:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 1)
        elif tag == 'items':
            if state != 4:
                pstate.Set('state', 99)
                return 
            pstate.Set('state', 7)
        elif tag == 'i':
            if state != 5 and state != 6:
                pstate.Set('state', 99)
                return 
            if state == 5:
                pstate.Set('state', 4)
            else:
                pstate.Set('state', 5)
        else:
            pstate.Set('state', 99)


    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = _xmlTagStart
    parser.EndElementHandler = _xmlTagEnd
    parser.buffer_text = True
    parser.returns_unicode = False
    parser.Parse('<doc>' + tempBlob + '</doc>', 1)
    finalBlow = util.KeyVal()
    finalBlow.characterID = mail.finalCharacterID
    finalBlow.corporationID = mail.finalCorporationID
    finalBlow.allianceID = mail.finalAllianceID
    finalBlow.factionID = mail.finalFactionID
    finalBlow.shipTypeID = mail.finalShipTypeID
    finalBlow.weaponTypeID = mail.finalWeaponTypeID
    finalBlow.damageDone = mail.finalDamageDone
    if mail.finalSecurityStatus is None:
        finalBlow.secStatusText = '0.0'
    else:
        finalBlow.secStatusText = util.FmtSystemSecStatus(mail.finalSecurityStatus)
    finalBlow.finalBlow = True
    attackers.append((finalBlow.damageDone, finalBlow))
    attackers.sort(reverse=True)
    for row in attackers:
        attacker = row[1]
        data = {'damage': attacker.damageDone}
        if attacker.characterID is not None:
            if attacker.finalBlow:
                text = mls.AGGRESSION_KILLMAIL_PLAYER_KILLER_ENTRY3
            else:
                text = mls.AGGRESSION_KILLMAIL_PLAYER_ATTACKER_ENTRY3
            data['attacker'] = cfg.eveowners.Get(attacker.characterID).name
            data['sec'] = attacker.secStatusText
            data['corp'] = cfg.eveowners.Get(attacker.corporationID).name
            if attacker.allianceID is not None:
                data['attackera'] = cfg.eveowners.Get(attacker.allianceID).name
            else:
                data['attackera'] = mls.NONE
            if attacker.factionID is not None:
                data['attackerf'] = cfg.eveowners.Get(attacker.factionID).name
            else:
                data['attackerf'] = mls.NONE
            if attacker.shipTypeID is not None:
                data['ship'] = cfg.invtypes.Get(attacker.shipTypeID).name
            else:
                data['ship'] = mls.UNKNOWN
            if attacker.weaponTypeID is not None:
                data['weapon'] = cfg.invtypes.Get(attacker.weaponTypeID).name
            else:
                data['weapon'] = mls.UNKNOWN
        elif attacker.corporationID is not None:
            if attacker.finalBlow:
                text = mls.AGGRESSION_KILLMAIL_NPC_KILLER_ENTRY2
            else:
                text = mls.AGGRESSION_KILLMAIL_NPC_ATTACKER_ENTRY2
            if attacker.shipTypeID is not None:
                data['attacker'] = cfg.invtypes.Get(attacker.shipTypeID).name
            else:
                data['attacker'] = mls.UNKNOWN
            data['owner'] = cfg.eveowners.Get(attacker.corporationID).name
        else:
            text = ''
        copy += text % data

    textDropped = textDestroyed = ''
    for item in items:
        data = {'type': cfg.invtypes.Get(item.typeID).name}
        if item.qtyDropped > 0:
            qty = item.qtyDropped
            wasDropped = True
        else:
            qty = item.qtyDestroyed
            wasDropped = False
        data['qty'] = qty
        if item.flag == const.flagCargo:
            data['loc'] = ' (%s)' % mls.CARGO
        elif item.flag == const.flagDroneBay:
            data['loc'] = ' (%s)' % mls.DRONEBAY
        else:
            data['loc'] = ''
        if qty > 1:
            text = mls.AGGRESSION_KILLMAIL_LOST_STACK_ENTRY
        else:
            text = mls.AGGRESSION_KILLMAIL_LOST_ITEM_ENTRY
        if wasDropped:
            textDropped += text % data
        else:
            textDestroyed += text % data
        if len(item.contents) > 0:
            for subitem in item.contents:
                subdata = {'type': cfg.invtypes.Get(subitem.typeID).name,
                 'loc': ' (%s)' % mls.IN_CONTAINER}
                if subitem.qtyDropped > 0:
                    qty = subitem.qtyDropped
                else:
                    qty = subitem.qtyDestroyed
                subdata['qty'] = qty
                if qty > 1:
                    subtext = mls.AGGRESSION_KILLMAIL_LOST_CONTAINER_STACK_ENTRY
                else:
                    subtext = mls.AGGRESSION_KILLMAIL_LOST_CONTAINER_ITEM_ENTRY
                if wasDropped:
                    textDropped += subtext % subdata
                else:
                    textDestroyed += subtext % subdata


    extraBR = False
    if textDestroyed != '':
        extraBR = True
        copy += mls.AGGRESSION_KILLMAIL_LOST_ITEM_HEADER + textDestroyed
    if textDropped != '':
        if extraBR:
            copy += '<br>'
        copy += mls.AGGRESSION_KILLMAIL_DROPPED_ITEM_HEADER + textDropped
    copy = util.FmtDate(mail.killTime, fmt='ll') + '<br>' + copy
    pstate.Set('state', 0)
    pstate.Set('lastitem', None)
    return copy



def SecurityClassFromLevel(level):
    if level <= 0.0:
        return const.securityClassZeroSec
    else:
        if level < 0.45:
            return const.securityClassLowSec
        return const.securityClassHighSec



def GetPseudoeSecFromRawSec(rawSecLevel):
    if rawSecLevel > 0.0 and rawSecLevel < 0.05:
        return 0.05
    else:
        return rawSecLevel



def ComputeRadiusFromQuantity(categoryID, groupID, typeID, quantity):
    if quantity < 0:
        quantity = 1
    if categoryID == const.categoryAsteroid:
        qty = quantity
        if qty > 130000:
            qty = 130000
        return 89.675 * math.exp(4e-05 * qty)
    if groupID == const.groupHarvestableCloud:
        return quantity * cfg.invtypes.Get(typeID).radius / 10.0
    return quantity * cfg.invtypes.Get(typeID).radius



def ComputeQuantityFromRadius(categoryID, groupID, typeID, radius):
    if categoryID == const.categoryAsteroid:
        quantity = math.log(radius / 89.675) * (1.0 / 4e-05)
        return quantity
    if groupID == const.groupHarvestableCloud:
        quantity = radius * 10.0 / cfg.invtypes.Get(typeID).radius
        return quantity
    return radius / cfg.invtypes.Get(typeID).radius



def IsMemberlessLocal(channelID):
    if type(channelID) != types.IntType:
        if type(channelID[0]) == types.TupleType:
            channelID = channelID[0]
        if channelID[0] == 'solarsystemid2':
            if util.IsWormholeSystem(channelID[1]):
                return True
    return False



def Flatten(sequence):
    if isinstance(sequence, basestring) or not hasattr(sequence, '__iter__'):
        yield sequence
        return 
    for thingie in sequence:
        for dude in Flatten(thingie):
            yield dude




exports = {'util.CombatLog_CopyText': CombatLog_CopyText,
 'util.SecurityClassFromLevel': SecurityClassFromLevel,
 'util.GetPseudoeSecFromRawSec': GetPseudoeSecFromRawSec,
 'util.IsMemberlessLocal': IsMemberlessLocal,
 'util.ComputeRadiusFromQuantity': ComputeRadiusFromQuantity,
 'util.ComputeQuantityFromRadius': ComputeQuantityFromRadius,
 'util.Flatten': Flatten}

