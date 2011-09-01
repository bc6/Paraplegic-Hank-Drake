import sys
import types
import log
import util
import math
import blue
import uiutil
import mathUtil
import uicls
import form
import uiconst
import trinity
advchannelsTutorial = 50
cloningTutorial = 42
cloningWhenPoddedTutorial = 27
podriskTutorial = 43
skillfittingTutorial = 51
insuranceTutorial = 41
tutorial = 109
tutorialAuraIntroduction = 5
tutorialBoarding = 6
tutorialCharacterSheet = 7
tutorialControlConsole = 18
tutorialItems = 8
tutorialNavigation = 19
tutorialOverview = 21
tutorialSelling = 10
tutorialShips = 6
tutorialSpace = 17
tutorialTargeting = 20
tutorialUndock = 16
tutorialWallet = 11
tutorialWarpingDC = 23
tutorialCombatChooseTheVenue = 103
tutorialCombatConcepts = 105
tutorialCombatKnowYourEquipment = 104
tutorialCombatStudyTheOpponent = 102
tutorialInformativeCareerPlanning = 99
tutorialInformativeCharacterSheetAdvancedInformation = 100
tutorialInformativeContracts = 54
tutorialInformativeCorporations = 33
tutorialInformativeCosmosComplexes = 101
tutorialInformativeCrimeAndPunishment = 97
tutorialInformativeDrones = 65
tutorialInformativeExploration = 124
tutorialInformativeFittingStationService = 13
tutorialInformativeHeat = 123
tutorialInformativeMap = 14
tutorialInformativeMarket = 12
tutorialInformativePeopleAndPlaces = 15
tutorialInformativePoliticsAndmanagement = 98
tutorialInformativeRepairshop = 46
tutorialInformativeReprocessingPlant = 9
tutorialInformativeSalvaging = 122
tutorialInformativeScanning = 63
tutorialInformativeScienceIndustry = 52
tutorialWorldspaceNavigation = 235
tutorialTutorials = 215
CLOSE = 4
OKCLOSE = 5
AUTOPOSCENTER = 17
TABMARGIN = 6
escapes = {'amp': '&',
 'lt': '<',
 'gt': '>'}

def Possessive(owner):
    if eve.session.languageID == 'EN':
        return owner + ("'s", "'")[owner.endswith('s')]
    return owner



def Plural(n, constant):
    return getattr(mls, constant + ['', 'S'][(n != 1)])



def TakeTime(label, func, *args, **kw):
    if eve.taketime:
        t = blue.pyos.taskletTimer.EnterTasklet(label)
        try:
            return func(*args, **kw)

        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(t)

    else:
        return func(*args, **kw)



def Click(*args):
    print 'UIXClickX',
    print args


import re
tag = re.compile('<color=0x.*?>|<right>|<center>|<left>')

def DeTag(s):
    return tag.sub('', s)



def Flush(wnd):
    wnd.Flush()



def GetBuffersize(size):
    return uiutil.GetBuffersize(size)



def GetItemData(rec, viewMode, viewOnly = 0, container = None, scrollID = None, *args, **kw):
    attribs = {}
    for attribute in sm.GetService('godma').GetType(rec.typeID).displayAttributes:
        attribs[attribute.attributeID] = attribute.value

    sort_slotsize = 0
    for effect in cfg.dgmtypeeffects.get(rec.typeID, []):
        if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
            sort_slotsize = 1
            break

    data = uiutil.Bunch()
    data.__guid__ = 'listentry.InvItem'
    data.item = rec
    data.rec = rec
    data.itemID = rec.itemID
    data.godmaattribs = attribs
    data.invtype = cfg.invtypes.Get(rec.typeID)
    data.container = container
    data.viewMode = viewMode
    data.viewOnly = viewOnly
    data.locked = rec.flagID == const.flagLocked
    if not data.locked and rec.flagID != const.flagUnlocked and container and container.IsLockableContainer():
        if hasattr(container, 'GetShell'):
            containerItem = container.GetShell().GetItem()
            if containerItem.groupID in (const.groupAuditLogSecureContainer, const.groupStation) or containerItem.typeID == const.typeOffice:
                data.locked = sm.GetService('corp').IsItemLocked(rec)
    data.factionID = sm.GetService('faction').GetCurrentFactionID()
    if rec.singleton or rec.typeID in (const.typeBookmark,):
        data.sort_qty = 0
    else:
        data.sort_qty = rec.stacksize
    ml = data.godmaattribs.get(const.attributeMetaLevel, None)
    if not ml:
        metaLevel = ''
    else:
        metaLevel = util.FmtAmt(ml)
    data.metaLevel = metaLevel
    data.groupName = data.invtype.Group().name
    data.categoryName = cfg.invcategories.Get(data.invtype.categoryID).categoryName
    data.sort_ammosizeconstraints = attribs.has_key(const.attributeChargeSize)
    data.sort_slotsize = sort_slotsize
    data.Set('sort_%s' % mls.UI_GENERIC_NAME, GetItemName(rec, data).lower())
    data.Set('sort_%s' % mls.UI_GENERIC_TYPE, GetCategoryGroupTypeStringForItem(rec).lower())
    data.Set('sort_%s' % mls.UI_SHARED_METALVL, ml or 0.0)
    data.Set('sort_%s' % mls.UI_GENERIC_GROUP, data.groupName.lower())
    data.Set('sort_%s' % mls.UI_GENERIC_CATEGORY, data.categoryName.lower())
    if data.rec.typeID == const.typePlasticWrap:
        data.volume = ''
        data.Set('sort_%s' % mls.UI_GENERIC_VOLUME, 0)
    else:
        volume = cfg.GetItemVolume(rec)
        u = cfg.dgmunits.Get(const.unitVolume)
        unit = Tr(u.displayName, 'dogma.units.displayName', u.dataID)
        data.volume = '%s %s' % (util.FmtAmt(volume), unit)
        data.Set('sort_%s' % mls.UI_GENERIC_VOLUME, volume)
    data.scrollID = scrollID
    return data



def GetItemLabel(rec, data, new = 0):
    if getattr(data, 'label', None) and data.viewMode == 'icons' and not new:
        return data.label
    name = GetItemName(rec, data)
    if data.viewMode in ('list', 'details'):
        pType = ' '
        fType = ' '
        attribs = getattr(data, 'godmaattribs', {})
        if attribs.has_key(const.attributeImplantness):
            kv = util.KeyVal(unitID=int, attributeID=const.attributeImplantness)
            v = attribs[const.attributeImplantness]
            fType = sm.GetService('info').GetFormatAndValue(kv, v)
        elif attribs.has_key(const.attributeBoosterness):
            kv = util.KeyVal(unitID=int, attributeID=const.attributeBoosterness)
            v = attribs[const.attributeBoosterness]
            fType = sm.GetService('info').GetFormatAndValue(kv, v)
        elif attribs.has_key(const.attributeChargeSize):
            kv = util.KeyVal(unitID=const.unitSizeclass, attributeID=const.attributeChargeSize)
            v = attribs[const.attributeChargeSize]
            pType = sm.GetService('info').GetFormatAndValue(kv, v)
        techLevel = data.godmaattribs.get(const.attributeTechLevel, '')
        if techLevel:
            techLevel = util.FmtAmt(techLevel)
        for effect in cfg.dgmtypeeffects.get(rec.typeID, []):
            if effect.effectID in (const.effectRigSlot,
             const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower):
                fType = {const.effectRigSlot: mls.UI_GENERIC_RIGS,
                 const.effectHiPower: mls.UI_GENERIC_HIGH,
                 const.effectMedPower: mls.UI_GENERIC_MEDIUM,
                 const.effectLoPower: mls.UI_GENERIC_LOW}.get(effect.effectID)
                continue

        stringDict = {mls.UI_GENERIC_NAME: name,
         mls.UI_GENERIC_QTY: '<right>%s' % GetItemQty(data, 'ln'),
         mls.UI_GENERIC_GROUP: data.groupName,
         mls.UI_GENERIC_CATEGORY: data.categoryName,
         mls.UI_GENERIC_SIZE: pType,
         mls.UI_GENERIC_SLOT: fType,
         mls.UI_GENERIC_VOLUME: '<right>%s' % data.volume,
         mls.UI_SHARED_METALVL: '<right>%s' % data.metaLevel,
         mls.UI_SHARED_TECHLVL: '<right>%s' % techLevel}
        headers = GetVisibleItemHeaders(data.scrollID)
        label = ''
        for each in headers:
            string = stringDict.get(each, '')
            label += '%s<t>' % string

        if label.endswith('<t>'):
            label = label[:-3]
        data.label = label
    else:
        data.label = '<center>%s' % name
    return data.label



def GetItemQty(data, fmt = 'ln'):
    ret = getattr(data, 'qty_%s' % fmt, None)
    if ret is not None and ret[0] == data.item.stacksize:
        return ret[1]
    ret = ''
    if not (data.item.singleton or data.item.typeID in (const.typeBookmark,)):
        import util
        ret = util.FmtAmt(data.item.stacksize, fmt)
    setattr(data, 'qty_%s' % fmt, (data.item.stacksize, ret))
    return ret



def GetItemName(invItem, data = None):
    if data and getattr(data, 'name', None):
        return data.name
    name = cfg.invtypes.Get(invItem.typeID).name
    if invItem.categoryID == const.categoryStation and invItem.groupID == const.groupStation:
        try:
            name = mls.UI_STATION_STATIONINSOLARSYSTEM % {'stationname': cfg.evelocations.Get(invItem.itemID).name,
             'solarsystemname': cfg.evelocations.Get(invItem.locationID).name}
        except KeyError('RecordNotFound'):
            sys.exc_clear()
    elif invItem.groupID == const.groupVoucher:
        voucher = sm.GetService('voucherCache').GetVoucher(invItem.itemID)
        if voucher is None:
            name = mls.UI_GENERIC_BOOKMARK
        else:
            name = voucher.GetDescription()
            if invItem.typeID == const.typeBookmark:
                try:
                    (name, _desc,) = sm.GetService('addressbook').UnzipMemo(voucher.GetDescription())
                except:
                    name = mls.UI_GENERIC_BOOKMARK
                    sys.exc_clear()
            if data:
                data.voucher = voucher
    elif (invItem.categoryID == const.categoryShip or invItem.groupID in (const.groupWreck,
     const.groupCargoContainer,
     const.groupSecureCargoContainer,
     const.groupAuditLogSecureContainer,
     const.groupFreightContainer)) and invItem.singleton:
        cfg.evelocations.Prime([invItem.itemID])
        try:
            locationName = cfg.evelocations.Get(invItem.itemID).name
            if locationName:
                name = locationName
        except:
            sys.exc_clear()
    if data:
        data.name = name
    return name



def GetCategoryGroupTypeStringForItem(invItem):
    try:
        return '%s %s %s' % (cfg.invcategories.Get(invItem.categoryID).categoryName, cfg.invgroups.Get(invItem.groupID).groupName, cfg.invtypes.Get(invItem.typeID).typeName)
    except IndexError:
        if invItem is None:
            log.LogTraceback('None is not an invItem')
            sys.exc_clear()
            return 'Unknown Unknown Unknown'
        log.LogTraceback('InvalidItem Report')
        sys.exc_clear()
        LogError('--------------------------------------------------')
        LogError('Invalid Item Report')
        LogError('Item: ', invItem)
        reason = ''
        typeName = 'Unknown'
        groupName = 'Unknown'
        categoryName = 'Unknown'
        typeinfo = None
        groupinfo = None
        categoryinfo = None
        try:
            typeID = getattr(invItem, 'typeID', None)
        except IndexError:
            typeID = None
            sys.exc_clear()
        try:
            groupID = getattr(invItem, 'groupID', None)
        except IndexError:
            groupID = None
            sys.exc_clear()
        try:
            categoryID = getattr(invItem, 'categoryID', None)
        except IndexError:
            categoryID = None
            sys.exc_clear()
        if typeID is None:
            LogError('typeID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute typeID is missing (Probably a coding mistake). '
        else:
            typeinfo = cfg.invtypes.GetIfExists(typeID)
            if typeinfo is None:
                LogError('THERE IS NO type info FOR typeID:', typeID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS TYPE')
                reason += 'The type %s no longer exists. Database requires cleanup. ' % typeID
        if groupID is None:
            LogError('groupID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute groupID is missing (Probably a coding mistake?). '
            if typeinfo is not None:
                LogWarn('Extracting groupID from typeinfo')
                groupID = typeinfo.groupID
        if groupID is not None:
            groupinfo = cfg.invgroups.GetIfExists(groupID)
            if groupinfo is None:
                LogError('THERE IS NO group info FOR groupID:', groupID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS GROUP')
                reason += 'The group %s no longer exists. Database requires cleanup. ' % groupID
        if categoryID is None:
            LogError('categoryID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute categoryID is missing (Probably a coding mistake?). '
            if groupinfo is not None:
                LogWarn('Extracting categoryID from typeinfo')
                categoryID = groupinfo.categoryID
        if categoryID is not None:
            categoryinfo = cfg.invcategories.GetIfExists(categoryID)
            if categoryinfo is None:
                LogError('THERE IS NO category info FOR categoryID:', categoryID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS CATEGORY')
                reason += 'The category %s no longer exists. Database requires cleanup. ' % categoryID
        if typeinfo is not None:
            typeName = typeinfo.typeName
        if groupinfo is not None:
            groupName = groupinfo.groupName
        if categoryinfo is not None:
            categoryName = categoryinfo.categoryName
        LogError('--------------------------------------------------')
        eve.Message('CustomInfo', {'info': 'Invalid item detected:<br>Item:%s<br>CGT:%s %s %s<br>Reason: %s' % (invItem,
                  categoryName,
                  groupName,
                  typeName,
                  reason)})
        return '%s %s %s' % (categoryName, groupName, typeName)



def GetSlimItemName(slimItem):
    import util
    if slimItem.groupID == const.groupHarvestableCloud:
        return '%s (%s)' % (mls.UI_GENERIC_HARVESTABLE_CLOUD, cfg.invtypes.Get(slimItem.typeID).name)
    else:
        if slimItem.categoryID == const.categoryAsteroid:
            return '%s (%s)' % (mls.UI_GENERIC_ASTEROID, cfg.invtypes.Get(slimItem.typeID).name)
        if slimItem.categoryID == const.categoryShip:
            if not slimItem.charID or slimItem.charID == eve.session.charid and slimItem.itemID != eve.session.shipid:
                return cfg.invtypes.Get(slimItem.typeID).name
            if util.IsCharacter(slimItem.charID):
                return cfg.eveowners.Get(slimItem.charID).name
        locationname = cfg.evelocations.Get(slimItem.itemID).name
        if locationname and locationname[0] != '@':
            if slimItem.groupID == const.groupBeacon:
                name = getattr(slimItem, 'dungeonDataID', None)
                if name:
                    translatedName = Tr(locationname, 'dungeon.dungeons.dungeonName', slimItem.dungeonDataID)
                    return translatedName
            return locationname
        return cfg.invtypes.Get(slimItem.typeID).name



def EditStationName(stationname, compact = 0, usename = 0):
    if compact:
        stationname = stationname.replace('Moon ', 'M').replace('moon', 'm')
    _stationname = stationname.split(' - ')
    if len(_stationname) >= 2 and usename:
        stationname = _stationname[-1]
    return stationname



def GetOrMakeChild(parent, name, make):
    ret = uiutil.FindChild(parent, name)
    if ret:
        return ret
    else:
        ret = make()
        ret.state = uiconst.UI_HIDDEN
        ret.name = name
        parent.children.insert(0, ret)
        return ret



def GetTextHeight(strng, width = 0, fontsize = 12, linespace = None, hspace = 0, autoWidth = 0, singleLine = 0, uppercase = 0, specialIndent = 0, getTextObj = 0, tabs = []):
    return sm.GetService('font').GetTextHeight(strng, width=width, font=None, fontsize=fontsize, linespace=linespace, letterspace=hspace, autowidth=autoWidth, singleline=singleLine, uppercase=uppercase, specialIndent=specialIndent, getTextObj=getTextObj, tabs=tabs)



def GetTextWidth(strng, fontsize = 12, hspace = 0, uppercase = 0):
    return sm.GetService('font').GetTextWidth(strng, fontsize, hspace, uppercase)



def GetWindowAbove(fromItem):
    if fromItem == uicore.desktop:
        return None
    if getattr(fromItem, 'isDockWnd', 0) == 1:
        return fromItem
    if fromItem.parent and not fromItem.parent.destroyed:
        return GetWindowAbove(fromItem.parent)



def ShowMinDevice():
    for each in uicore.desktop.children[:]:
        if each.name == 'devicegrid':
            each.Close()

    sizes = [(1024, 768)]
    for (w, h,) in sizes:
        p = uicls.Container(name='devicegrid', parent=uicore.desktop, pos=(0,
         0,
         w,
         h), state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        uicls.Frame(parent=p, color=(1.0, 1.0, 1.0, 0.25))




def RefreshHeight(w):
    w.height = sum([ x.height for x in w.children if x.state != uiconst.UI_HIDDEN if x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ])



def GetStanding(standing, type = 0):
    if standing > 5:
        return mls.UI_GENERIC_STANDINGEXCELLENT
    else:
        if standing > 0:
            return mls.UI_GENERIC_STANDINGGOOD
        if standing == 0:
            return mls.UI_GENERIC_STANDINGNEUTRAL
        if standing < -5:
            return mls.UI_GENERIC_STANDINGTERRIBLE
        if standing < 0:
            return mls.UI_GENERIC_STANDINGBAD
        return mls.UI_GENERIC_STANDINGUNKOWN



def GetMappedRankBase(rank, warFactionID, align):
    logo = uicls.Sprite(align=align)
    if rank < 0:
        logo.texture = None
    else:
        iconNum = '%s_%s' % (rank / 4 + 1, rank % 4 + 1)
        MapLogo(iconNum, logo, root='res:/UI/Texture/Medals/Ranks/%s_' % warFactionID)
    if align != uiconst.TOALL:
        logo.width = logo.height = 128
    else:
        logo.width = logo.height = 0
    return logo



def MapLogo(iconNum, sprite, root = 'res:/UI/Texture/Corps/corps'):
    (texpix, num,) = iconNum.split('_')
    while texpix.find('0') == 0:
        texpix = texpix[1:]

    sprite.texturePath = '%s%s%s.dds' % (root, ['', '0'][(int(texpix) < 10)], texpix)
    num = int(num)
    sprite.rectWidth = sprite.rectHeight = 128
    sprite.rectLeft = [0, 128][(num in (2, 4))]
    sprite.rectTop = [0, 128][(num > 2)]



def GetTechLevelIcon(tlicon = None, offset = 0, typeID = None):
    if typeID is None:
        return 
    groupDict = {3: 'ui_73_16_245',
     4: 'ui_73_16_246',
     5: 'ui_73_16_248',
     6: 'ui_73_16_247'}
    try:
        invtype = cfg.invtypes.Get(typeID)
        invgroup = invtype.Group()
        if invgroup.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
            bpType = cfg.invbptypes.Get(typeID)
            ptID = bpType.productTypeID
            if ptID is not None:
                typeID = ptID
    except Exception:
        pass
    techLevel = sm.GetService('godma').GetTypeAttribute(typeID, const.attributeTechLevel)
    if techLevel:
        techLevel = int(techLevel)
    groupID = None
    metaGroupID = sm.GetService('godma').GetTypeAttribute(typeID, const.attributeMetaGroupID)
    if metaGroupID:
        groupID = int(metaGroupID)
    if groupID or techLevel in (2, 3):
        if groupID:
            icon = groupDict.get(groupID)
            hint = cfg.invmetagroups.Get(groupID).name
        else:
            (icon, hint,) = {2: ('ui_73_16_242', mls.UI_GENERIC_TECHLEVEL2),
             3: ('ui_73_16_243', mls.UI_GENERIC_TECHLEVEL3)}.get(techLevel, None)
        if tlicon is None:
            tlicon = uicls.Icon(icon=icon, parent=None, width=16, height=16, align=uiconst.TOPLEFT, idx=0, hint=hint)
        else:
            uiutil.MapIcon(tlicon, icon)
            tlicon.hint = hint
        if offset:
            tlicon.top = offset
        tlicon.state = uiconst.UI_NORMAL
    elif tlicon:
        tlicon.state = uiconst.UI_HIDDEN
    return tlicon



def GetIconSize(sheetNum):
    sheetNum = int(sheetNum)
    one = [90,
     91,
     92,
     93]
    two = [17,
     18,
     19,
     28,
     29,
     32,
     33,
     59,
     60,
     61,
     65,
     66,
     67,
     80,
     85,
     86,
     87,
     88,
     89,
     102,
     103,
     104]
    eight = [22,
     44,
     75,
     77,
     105]
    sixteen = [38, 73]
    if sheetNum in one:
        return 256
    if sheetNum in two:
        return 128
    if sheetNum in eight:
        return 32
    if sheetNum in sixteen:
        return 16
    return 64



def GetBigButton(size = 128, where = None, left = 0, top = 0, menu = 0, align = 0, iconMargin = 0, hint = '', width = None, height = None):
    import xtriui
    if width is None:
        width = size
    if height is None:
        height = size
    btn = xtriui.BigButton(parent=where, left=left, top=top, width=width, height=height, hint=hint, align=align)
    btn.Startup(width, height, iconMargin)
    return btn



def GetBallparkRecord(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp and hasattr(bp, 'GetInvItem'):
        return bp.GetInvItem(itemID)
    else:
        return None



def _GetNavigation(what, create, new):
    what = what.lower()
    navName = what + 'nav'
    navNames = ('systemmapnav', 'mapnav', 'stationnav', 'inflightnav', 'planetnav', 'charcontrolnav')
    navLayers = (uicore.layer.systemmap,
     uicore.layer.map,
     uicore.layer.station,
     uicore.layer.inflight,
     uicore.layer.planet,
     uicore.layer.charcontrol)
    layerClassesByName = {'charcontrol': uicls.CharControl}
    allNavs = []
    for navLayer in navLayers:
        for each in navLayer.children:
            if each.name not in navNames:
                continue
            else:
                allNavs.append(each)


    if not new and create and len(allNavs) == 1 and allNavs[0].name == navName:
        return allNavs[0]
    new = new or bool(len(allNavs) > 1)
    for each in allNavs:
        if new:
            each.Close()
            continue
        if not create and each.name == navName:
            return each
        if create and each.name != navName:
            each.Close()

    if not new and not create:
        return 
    par = uicore.layer.Get(what)
    if what in layerClassesByName:
        navCls = layerClassesByName[what]
    else:
        navCls = getattr(form, '%sNav' % what.capitalize(), None)
    nav = navCls(parent=par, name=navName, state=uiconst.UI_NORMAL)
    nav.Startup()
    eve._navigation = nav
    return nav



def GetStationNav(create = 1, new = 0):
    return _GetNavigation('station', create, new)



def GetMapNav(create = 1, new = 0):
    return _GetNavigation('map', create, new)



def GetInflightNav(create = 1, new = 0):
    return _GetNavigation('inflight', create, new)



def GetSystemmapNav(create = 1, new = 0):
    return _GetNavigation('systemmap', create, new)



def GetPlanetNav(create = 1, new = 0):
    return _GetNavigation('planet', create, new)



def GetWorldspaceNav(create = 1, new = 0):
    ret = _GetNavigation('charcontrol', 0, 0)
    if ret is None:
        ret = _GetNavigation('charcontrol', 1, 0)
    return ret



def Close(owner, wndNames):
    for each in wndNames:
        if getattr(owner, each, None):
            wnd = getattr(owner, each, None)
            setattr(owner, each, None)
            if not wnd.destroyed:
                wnd.Close()




def GetDatePicker(where, setval = None, left = 0, top = 0, idx = None, withTime = False, timeparts = 4, startYear = None, yearRange = None):
    import xtriui
    picker = xtriui.DatePicker(name='datepicker', parent=where, align=uiconst.TOPLEFT, width=256, height=18, left=left, top=top)
    picker.Startup(setval, withTime, timeparts, startYear, yearRange)
    if idx is not None:
        uiutil.SetOrder(picker, idx)
    return picker



def GetContainerHeader(caption, where, bothlines = 1, xmargin = 0):
    container = uicls.Container(name='headercontainer', parent=where, align=uiconst.TOTOP, height=18)
    par = uicls.Container(name='headerparent', align=uiconst.TOALL, parent=container, padding=(xmargin,
     0,
     xmargin,
     0))
    uicls.Line(parent=par, align=uiconst.TOBOTTOM)
    if bothlines:
        uicls.Line(parent=par, align=uiconst.TOTOP)
    else:
        uicls.Container(name='push', align=uiconst.TOTOP, parent=par, height=1)
        container.padBottom -= 1
    t = uicls.Label(text=caption, name='header1', parent=par, padding=(8, 2, 8, 2), align=uiconst.TOTOP, letterspace=1, fontsize=10, uppercase=1)
    container.height = t.textheight + 5
    return container



def GetSlider(name = 'slider', where = None, config = '', minval = None, maxval = None, header = '', hint = '', align = None, width = 0, height = 18, left = 0, top = 0, setlabelfunc = None, getvaluefunc = None, endsliderfunc = None, increments = [], underlay = 1):
    import xtriui
    if align is None:
        align = uicons.TOTOP
    mainpar = uicls.Container(name=config + '_slider', align=align, width=width, height=height, left=left, top=top, state=uiconst.UI_NORMAL, parent=where)
    slider = xtriui.Slider(parent=mainpar, align=uiconst.TOPLEFT, top=6, state=uiconst.UI_NORMAL)
    lbl = uicls.Label(text='', parent=mainpar, left=7, top=-14, fontsize=10, letterspace=1, state=uiconst.UI_NORMAL)
    lbl.name = 'label'
    if getvaluefunc:
        slider.GetSliderValue = getvaluefunc
    if setlabelfunc:
        slider.SetSliderLabel = setlabelfunc
    slider.Startup(config, minval, maxval, config, header, increments=increments)
    slider.name = name
    slider.hint = mainpar.hint = hint
    if endsliderfunc:
        slider.EndSetSliderValue = endsliderfunc
    return mainpar


SEL_FILES = 0
SEL_FOLDERS = 1
SEL_BOTH = 2

def GetFileDialog(path = None, fileExtensions = None, multiSelect = False, selectionType = SEL_FILES):
    wnd = sm.GetService('window').GetWindow('FileDialog', create=1, path=path, fileExtensions=fileExtensions, multiSelect=multiSelect, selectionType=selectionType)
    wnd.width = 400
    wnd.height = 400
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None



def __Search(searchStr, groupID, exact, filterCorpID, hideNPC = False):
    if groupID == const.groupCharacter:
        if hideNPC:
            result = sm.RemoteSvc('lookupSvc').LookupPlayerCharacters(searchStr, exact)
        else:
            result = sm.RemoteSvc('lookupSvc').LookupCharacters(searchStr, exact)
        if result:
            cfg.eveowners.Prime([ each.characterID for each in result ])
    elif groupID == const.groupCorporation:
        if exact == -1:
            result = sm.RemoteSvc('lookupSvc').LookupCorporationTickers(searchStr.upper()[:5], 0)
        elif filterCorpID == -1:
            result = sm.RemoteSvc('lookupSvc').LookupPlayerCorporations(searchStr, exact)
        else:
            result = sm.RemoteSvc('lookupSvc').LookupCorporations(searchStr, exact)
        if result:
            cfg.eveowners.Prime([ each.corporationID for each in result ])
    elif groupID == const.groupAlliance:
        if exact == -1:
            result = sm.RemoteSvc('lookupSvc').LookupAllianceShortNames(searchStr.upper()[:5], 0)
        else:
            result = sm.RemoteSvc('lookupSvc').LookupAlliances(searchStr, exact)
        if result:
            cfg.eveowners.Prime([ each.allianceID for each in result ])
    elif groupID == const.groupStation:
        result = sm.RemoteSvc('lookupSvc').LookupStations(searchStr, exact)
    elif groupID == const.groupFaction:
        result = sm.RemoteSvc('lookupSvc').LookupFactions(searchStr, exact)
    elif cfg.invgroups.Get(groupID).categoryID == const.categoryCelestial:
        result = sm.RemoteSvc('lookupSvc').LookupKnownLocationsByGroup(groupID, searchStr)
        if result:
            cfg.evelocations.Prime([ each.itemID for each in result ])
    else:
        return None
    return result



def FilterResult(result, filterGroups, hideNPC, attrGroupName):
    import util
    if hideNPC:
        result = [ each for each in result if not util.IsNPC(GetAttr(each, 'ID', attrGroupName)) ]
    if filterGroups:
        result = [ each for each in result if each.groupID in filterGroups ]
    return result



def Search(searchStr, groupID, categoryID = None, modal = 1, exact = 0, getError = 0, notifyOneMatch = 0, filterCorpID = None, hideNPC = 0, filterGroups = [], searchWndName = 'mySearch', getWindow = 1):
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_PLEASETYPESOMETHING
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return 
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_TOOLONGSEARCHSTRING
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_TOOLONGSEARCHSTRING})
        return 
    import util
    attrGroupName = {const.groupCharacter: 'Character',
     const.groupCorporation: 'Corporation',
     const.groupFaction: 'Faction',
     const.groupStation: 'Station',
     const.groupAsteroidBelt: 'Asteroid Belt',
     const.groupSolarSystem: 'SolarSystem',
     const.groupConstellation: 'Constellation',
     const.groupRegion: 'Region',
     const.groupAlliance: 'Alliance'}.get(groupID, '')
    if categoryID is not None and categoryID == const.categoryOwner:
        result = FilterResult(sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact), filterGroups, hideNPC, attrGroupName)
        owners = [ each.ownerID for each in result ]
        if owners:
            cfg.eveowners.Prime(owners)
        displayGroupName = mls.UI_GENERIC_OWNER.lower()
        displayGroupNamePlural = mls.UI_GENERIC_OWNERS
    else:
        displayGroupName = cfg.invgroups.Get(groupID).name
        if attrGroupName:
            displayGroupNamePlural = getattr(mls, 'UI_GENERIC_' + attrGroupName.upper().replace(' ', '') + 'S')
        else:
            displayGroupNamePlural = displayGroupName
        result = FilterResult(__Search(searchStr, groupID, exact, filterCorpID, hideNPC), filterGroups, [0, hideNPC][(groupID in (const.groupCharacter, const.groupCorporation))], attrGroupName)
    if result is None or not len(result):
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_NOGROUPFOUNDWITH % {'group': displayGroupName,
             'with': searchStr}
        if exact and groupID == const.groupCharacter:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_ONEGROUPFOUNDWITHEXACT % {'name': searchStr}})
        else:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_NOGROUPFOUNDWITH % {'group': displayGroupName,
                      'with': searchStr}})
        return 
    if len(result) >= 1:
        if len(result) == 1:
            if GetAttr(result[0], 'ID', attrGroupName) and modal:
                if notifyOneMatch:
                    return (GetAttr(result[0], 'ID', attrGroupName), 1)
                return GetAttr(result[0], 'ID', attrGroupName)
            hint = mls.UI_SHARED_ONEGROUPFOUNDWITH % {'group': displayGroupName,
             'with': searchStr}
        else:
            hint = mls.UI_SHARED_MANYGROUPSFOUNDWITH % {'num': len(result),
             'group': displayGroupNamePlural,
             'with': searchStr}
        tmplist = []
        for each in result:
            id = GetAttr(each, 'ID', attrGroupName)
            if groupID == const.groupCorporation and exact == -1:
                name = '[%s] %s' % (GetAttr(each, 'tickerName', attrGroupName), GetAttr(each, 'Name', attrGroupName))
            elif groupID == const.groupAlliance and exact == -1:
                name = '[%s] %s' % (GetAttr(each, 'shortName', attrGroupName), GetAttr(each, 'Name', attrGroupName))
            elif groupID == const.groupCharacter and util.IsNPC(id):
                agentInfo = sm.GetService('agents').GetAgentByID(id)
                if agentInfo is not None and agentInfo.agentTypeID == const.agentTypeAura:
                    if id != sm.GetService('agents').GetAuraAgentID():
                        continue
            name = GetAttr(each, 'Name', attrGroupName)
            typeID = GetAttr(each, 'TypeID', attrGroupName)
            if id and name:
                tmplist.append((name, id, typeID or 0))

        sm.GetService('loading').StopCycle()
        if getWindow:
            chosen = ListWnd(tmplist, attrGroupName.lower(), [displayGroupNamePlural, '%s %s' % (mls.UI_GENERIC_SELECT, displayGroupName)][modal], hint, 1, minChoices=modal, isModal=modal, windowName=searchWndName, unstackable=1)
            if chosen:
                return chosen[1]
        else:
            return tmplist



def GetAttr(rec, attr, groupName = None):
    if groupName:
        if hasattr(rec, '%s%s' % (groupName.lower(), attr)):
            return getattr(rec, '%s%s' % (groupName.lower(), attr), None)
    for attrType in (attr[0].lower() + attr[1:],
     attr.lower(),
     'item%s' % attr,
     'owner%s' % attr,
     'location%s' % attr):
        if hasattr(rec, attrType):
            return getattr(rec, attrType, None)

    if attr == 'TypeID' and groupName:
        return util.LookupConstValue('type%s' % groupName.replace(' ', ''), None)



def SearchOwners(searchStr, groupIDs = None, exact = False, notifyOneMatch = False, hideNPC = False, getError = False, searchWndName = 'mySearch'):
    if type(groupIDs) == int:
        groupIDs = [groupIDs]
    elif groupIDs is None:
        groupIDs = [const.groupCharacter,
         const.groupCorporation,
         const.groupAlliance,
         const.groupFaction]
    groupNames = {const.groupCharacter: [mls.UI_GENERIC_CHARACTER, mls.UI_GENERIC_CHARACTERS],
     const.groupCorporation: [mls.UI_GENERIC_CORPORATION, mls.UI_GENERIC_CORPORATIONS],
     const.groupAlliance: [mls.UI_GENERIC_ALLIANCE, mls.UI_GENERIC_ALLIANCES],
     const.groupFaction: [mls.UI_GENERIC_FACTION, mls.UI_GENERIC_FACTIONS]}
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_PLEASETYPESOMETHING
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return 
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_TOOLONGSEARCHSTRING
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_TOOLONGSEARCHSTRING})
        return 
    displayGroupName = ''
    displayGroupNamePlural = ''
    for g in groupNames:
        if g in groupIDs:
            displayGroupName += groupNames[g][0] + '/'
            displayGroupNamePlural += groupNames[g][1] + '/'

    displayGroupName = displayGroupName[:(len(displayGroupName) - 1)]
    displayGroupNamePlural = displayGroupNamePlural[:(len(displayGroupNamePlural) - 1)]
    if hideNPC:
        owners = sm.RemoteSvc('lookupSvc').LookupPCOwners(searchStr, exact)
    else:
        owners = sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact)
    list = []
    for o in owners:
        if o.groupID in groupIDs:
            list.append(('%s [%s]' % (o.ownerName, groupNames[o.groupID][0]), o.ownerID, o.typeID))

    if not list:
        sm.GetService('loading').StopCycle()
        if getError:
            return mls.UI_SHARED_NOGROUPFOUNDWITH % {'group': displayGroupName,
             'with': searchStr}
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_NOGROUPFOUNDWITH % {'group': displayGroupName,
                  'with': searchStr}})
        return 
    if len(list) == 1 and not notifyOneMatch:
        return list[0][1]
    caption = '%s %s' % (mls.UI_GENERIC_SELECT, displayGroupName)
    hint = mls.UI_SHARED_MANYGROUPSFOUNDWITH % {'num': len(list),
     'group': displayGroupNamePlural,
     'with': searchStr}
    chosen = ListWnd(lst=list, listtype='owner', caption='%s %s' % (mls.UI_GENERIC_SELECT, displayGroupName), hint=hint, ordered=1, minChoices=1, windowName=searchWndName)
    if chosen:
        return chosen[1]



def ShowInfo(typeID, itemID, abstractinfo = None, *args):
    sm.GetService('info').ShowInfo(typeID=typeID, itemID=itemID, abstractinfo=abstractinfo)



def GetStationByName(searchstr, flag = 0):
    result = None
    try:
        result = sm.RemoteSvc('lookupSvc').LookupStations(searchstr)
    except:
        sys.exc_clear()
        return 
    return result



def SearchStation(stationname, flag = 0):
    if len(stationname) < 1:
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_PLEASETYPESOMETHINGINFO})
        return 
    stationinfo = GetStationByName(stationname.lower(), flag)
    if stationinfo is None or not len(stationinfo):
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_NOSTATIONFOUNDWITH % {'with': stationname}})
        return 
    if len(stationinfo) > 20:
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': mls.UI_SHARED_MORETHEN10STATIONSFOUND % {'what': stationname}})
        return 
    if len(stationinfo) >= 1 and len(stationinfo) <= 20:
        if len(stationinfo) == 1:
            if stationinfo[0].stationName == stationname:
                return 
            hint = mls.UI_SHARED_ONESTATIONFOUNDWITH % {'what': stationname}
        elif len(stationinfo) <= 25:
            hint = mls.UI_SHARED_MANYSTAIONSFOUNDWITH % {'num': len(stationinfo),
             'with': stationname}
        if len(stationinfo) > 25:
            hint = mls.UI_SHARED_MORETHEN25STATIONSFOUND % {'with': stationinfo}
        if len(stationinfo) == 1:
            return stationinfo[0].stationID
        tmplist = []
        for each in stationinfo:
            tmplist.append((each.stationName, each.stationID, 0))

        sm.GetService('loading').StopCycle()
        choosestation = ListWnd(tmplist, 'station', mls.UI_MARKET_SELECTSTATION, hint, 1)
        if choosestation:
            return choosestation[1]



def FitKeys():
    return ['Hi', 'Med', 'Lo']



def FittingFlags():
    flags = []
    for key in FitKeys():
        for i in range(8):
            flags.append(util.LookupConstValue('flag%sSlot%s' % (key, i)))


    return flags



def ListWnd(lst, listtype = None, caption = None, hint = None, ordered = 0, minw = 200, minh = 256, minChoices = 1, maxChoices = 1, initChoices = [], validator = None, isModal = 1, scrollHeaders = [], iconMargin = 0, windowName = 'listwindow', lstDataIsGrouped = 0, unstackable = 0):
    if caption is None:
        caption = mls.UI_MARKET_SELECTITEM
    wnd = sm.GetService('window').GetWindow(windowName)
    if wnd:
        wnd.SelfDestruct()
    wnd = sm.GetService('window').GetWindow(windowName, create=1, decoClass=form.ListWindow, lst=lst, listtype=listtype, ordered=ordered, minSize=(minw, minh), caption=caption, minChoices=minChoices, maxChoices=maxChoices, initChoices=initChoices, validator=validator, scrollHeaders=scrollHeaders, iconMargin=iconMargin, lstDataIsGrouped=lstDataIsGrouped)
    if hint:
        wnd.SetHint('<center>' + hint)
    if unstackable:
        wnd.MakeUnstackable()
    if isModal:
        wnd.DefineButtons(uiconst.OKCANCEL)
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
        else:
            return 
    else:
        wnd.DefineButtons(uiconst.CLOSE)
        wnd.Maximize()
        uiutil.SetOrder(wnd, 0)



def HybridWnd(format, caption, modal = 1, wndID = None, buttons = None, location = None, minW = 256, minH = 256, blockconfirm = 0, icon = None, unresizeAble = 0, ignoreCurrent = 1):
    if wndID is not None:
        for each in sm.GetService('window').GetWindows()[:]:
            if hasattr(each, 'wndID') and each.wndID == wndID and not each.destroyed:
                return 

    if buttons is None:
        buttons = uiconst.OK
    if modal == 1:
        sm.GetService('window').ResetToDefaults(caption)
    wnd = sm.GetService('window').GetWindow(caption, create=1, decoClass=form.HybridWindow, ignoreCurrent=ignoreCurrent, format=format, caption=caption, modal=modal, wndID=wndID, buttons=buttons, location=location, minW=minW, minH=minH, icon=icon, blockconfirm=blockconfirm)
    wnd.MakeUnstackable()
    if unresizeAble:
        wnd.MakeUnResizeable()
    import uthread
    uthread.new(wnd.OnScale_)
    if modal == 1:
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
        else:
            return 
    return wnd



def NamePopup(caption = None, label = None, setvalue = '', icon = -1, modal = 1, btns = None, maxLength = None, passwordChar = None, validator = None):
    if caption is None:
        caption = mls.UI_SHARED_TYPEINNAME
    if label is None:
        label = mls.UI_SHARED_TYPEINNAME
    if icon == -1:
        icon = uiconst.QUESTION
    if validator:
        check = validator
    else:
        check = NamePopupErrorCheck
    format = [{'type': 'btline'},
     {'type': 'text',
      'text': label,
      'frame': 1},
     {'type': 'edit',
      'setvalue': setvalue,
      'label': '_hide',
      'key': 'name',
      'required': 1,
      'frame': 1,
      'maxLength': maxLength,
      'passwordChar': passwordChar,
      'setfocus': 1,
      'selectall': 1},
     {'type': 'bbline'},
     {'type': 'errorcheck',
      'errorcheck': check}]
    if btns is None:
        btns = uiconst.OKCANCEL
    wnd = HybridWnd(format, caption, modal, None, btns, minW=240, minH=100, icon=icon)
    if not modal:
        return wnd.Execute()
    else:
        return wnd



def TextBox(header, txt, modal = 0, wndID = 'generictextbox2', tabs = [], preformatted = 0, scrolltotop = 1):
    wnd = sm.GetService('window').GetWindow(header)
    if wnd is None or wnd.destroyed or uicore.uilib.Key(uiconst.VK_SHIFT):
        format = [{'type': 'textedit',
          'readonly': 1,
          'label': '_hide',
          'key': 'text'}]
        wnd = HybridWnd(format, header, modal, wndID, uiconst.CLOSE, None, minW=256, minH=128)
        if wnd:
            wnd.form.align = uiconst.TOALL
            wnd.form.left = wnd.form.width = 3
            wnd.form.top = -2
            wnd.form.height = 6
            wnd.form.sr.text.parent.align = uiconst.TOALL
            wnd.form.sr.text.parent.left = wnd.form.sr.text.parent.top = wnd.form.sr.text.parent.width = wnd.form.sr.text.parent.height = 0
            wnd.form.sr.text.parent.children[0].height = 0
            wnd.form.sr.text.autoScrollToBottom = 0
    if wnd is not None:
        i = 1
        for t in tabs:
            setattr(wnd.form.sr.text.content.control, 'tabstop%s' % i, t)
            i = i + 1

        wnd.form.sr.text.SetValue(txt, scrolltotop=scrolltotop, preformatted=preformatted)
        if wnd.state == uiconst.UI_NORMAL:
            uiutil.SetOrder(wnd, 0)
        else:
            wnd.Maximize()



def NamePopupErrorCheck(ret):
    if not len(ret['name']) or len(ret['name']) and len(ret['name'].strip()) < 1:
        return mls.UI_SHARED_PLEASETYPESOMETHINGINFO
    return ''



def QtyPopup(maxvalue = None, minvalue = 0, setvalue = '', hint = None, caption = None, label = '', digits = 0):
    if caption is None:
        caption = mls.UI_SHARED_SETQTY
    if maxvalue is not None and hint is None:
        hint = mls.UI_SHARED_SETQTYBETWEEN % {'from': util.FmtAmt(minvalue),
         'to': util.FmtAmt(maxvalue)}
        if setvalue == 0:
            setvalue = maxvalue
    maxvalue = maxvalue or min(maxvalue, sys.maxint)
    format = [{'type': 'btline'}]
    if hint is not None:
        format += [{'type': 'text',
          'text': hint,
          'frame': 1}]
    if label is not None:
        format += [{'type': 'labeltext',
          'label': label,
          'text': '',
          'frame': 1,
          'labelwidth': 180}]
    if digits:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'floatonly': [minvalue, maxvalue, digits],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1}, {'type': 'bbline'}]
    else:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'intonly': [minvalue, maxvalue],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1}, {'type': 'bbline'}]
    return HybridWnd(format, caption, 1, None, uiconst.OKCANCEL, None, minW=240, minH=80)



def GetInvItemDefaultHiddenHeaders():
    return [mls.UI_SHARED_METALVL, mls.UI_SHARED_TECHLVL, mls.UI_GENERIC_CATEGORY]



def GetInvItemDefaultHeaders():
    return [mls.UI_GENERIC_NAME,
     mls.UI_GENERIC_QTY,
     mls.UI_GENERIC_GROUP,
     mls.UI_GENERIC_CATEGORY,
     mls.UI_GENERIC_SIZE,
     mls.UI_GENERIC_SLOT,
     mls.UI_GENERIC_VOLUME,
     mls.UI_SHARED_METALVL,
     mls.UI_SHARED_TECHLVL]



def GetVisibleItemHeaders(scrollID):
    defaultHeaders = GetInvItemDefaultHeaders()
    hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % uiconst.SCROLLVERSION, {}).get(scrollID, [])
    allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % uiconst.SCROLLVERSION, {}).get(scrollID, [])
    filterColumns = filter(lambda x: x not in allHiddenColumns, defaultHeaders)
    return filterColumns



def CheckAudioFileForEnglish(audioPath):
    if settings.user.ui.Get('forceEnglishVoice', False):
        audioPath = audioPath[:-3] + 'EN.' + audioPath[-3:]
    return audioPath



def GetLightYearDistance(fromSystem, toSystem, fraction = True):
    for system in (fromSystem, toSystem):
        if type(system) not in (types.IntType, types.InstanceType, types.LongType):
            return None


    def GetLoc(system):
        if type(system) in (types.IntType, types.LongType):
            return cfg.evelocations.Get(system)
        if type(system) == types.InstanceType:
            return system


    fromSystem = GetLoc(fromSystem)
    toSystem = GetLoc(toSystem)
    dist = math.sqrt((toSystem.x - fromSystem.x) ** 2 + (toSystem.y - fromSystem.y) ** 2 + (toSystem.z - fromSystem.z) ** 2) / const.LIGHTYEAR
    if fraction:
        dist = float(int(dist * 10)) / 10
    return dist



def GetRankLabel(factionID, rank):
    rank = min(9, rank)
    (rankLabel, rankDescription,) = ('', '')
    if rank < 0:
        rankLabel = mls.UI_FACWAR_NORANK
        rankDescription = ''
    else:
        rankLabel = mls.GetLabelIfExists('UI_FACWAR_FACTION_%s_RANK_%s' % (factionID, rank)) or mls.UI_FACWAR_NORANK
        rankDescription = mls.GetLabelIfExists('UI_FACWAR_FACTION_%s_RANKDESCRIPTION_%s' % (factionID, rank)) or rankLabel
    return (rankLabel, rankDescription)



def GetCertificateLabel(certificateID):
    classes = sm.RemoteSvc('certificateMgr').GetCertificateClasses()
    data = cfg.certificates.Get(certificateID)
    label = cfg.invtypes.Get(const.typeCertificate).name
    desc = cfg.invtypes.Get(const.typeCertificate).description
    grade = mls.UI_SHARED_CERTGRADE1
    if data:
        classdata = classes[data.classID]
        if classdata:
            label = Tr(classdata.className, 'cert.classes.className', classdata.dataID)
        grade = getattr(mls, 'UI_SHARED_CERTGRADE%d' % data.grade)
        desc = data.description
    return (label, grade, desc)



def HideButtonFromGroup(btns, label, button = None):
    if label:
        btn = uiutil.FindChild(btns, '%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_HIDDEN
    if button:
        btn.state = uiconst.UI_HIDDEN



def ShowButtonFromGroup(btns, label, button = None):
    if label:
        btn = uiutil.FindChild(btns, '%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_NORMAL
    if button:
        btn.state = uiconst.UI_NORMAL



def GetTimeText(secs, defaultText = None, short = 0):
    if defaultText is None:
        defaultText = mls.UI_SHARED_COMPLETIONIMMINENT
    secs = max(0.0, secs)
    seconds = int(secs % 60)
    minutes = int(secs / 60 % 60)
    hours = int(secs / 60 / 60 % 24)
    days = int(secs / 60 / 60 / 24)
    if not short:
        s = ''
        if days:
            s = '%s %s' % (days, (mls.UI_GENERIC_DAYS, mls.UI_GENERIC_DAY)[(days == 1)])
        if hours:
            s = '%s%s %s' % (s and '%s, ' % s, hours, (mls.UI_GENERIC_HOURS, mls.UI_GENERIC_HOUR)[(hours == 1)])
        if minutes:
            s = '%s%s %s' % (s and '%s, ' % s, minutes, (mls.UI_GENERIC_MINUTES, mls.UI_GENERIC_MINUTE)[(minutes == 1)])
        if seconds:
            s = '%s%s %s' % (s and '%s, ' % s, seconds, (mls.UI_GENERIC_SECONDS, mls.UI_GENERIC_SECOND)[(seconds == 1)])
    else:
        s = ''
        if days:
            s = '%s%s' % (days, mls.UI_GENERIC_DAYVERYSHORT)
        if hours:
            s = '%s%s%s' % (s and '%s, ' % s, hours, mls.UI_GENERIC_HOURVERYSHORT)
        if minutes:
            s = '%s%s%s' % (s and '%s, ' % s, minutes, mls.UI_GENERIC_MINUTEVERYSHORT)
        if seconds:
            s = '%s%s%s' % (s and '%s, ' % s, seconds, mls.UI_GENERIC_SECONDVERYSHORT)
    return s or defaultText



def FadeCont(cont, fadeIn, after = 0, fadeTime = 500.0):
    if getattr(cont, 'fading', 0) == 1:
        return 
    if fadeIn:
        current = cont.opacity
        end = 1.0
    else:
        current = cont.opacity
        end = 0.0
    setattr(cont, 'fading', 1)
    blue.pyos.synchro.Sleep(after)
    (start, ndt,) = (blue.os.GetTime(), 0.0)
    while ndt != 1.0:
        if not cont or cont.destroyed:
            break
        ndt = min(blue.os.TimeDiffInMs(start) / fadeTime, 1.0)
        cont.opacity = mathUtil.Lerp(current, end, ndt)
        blue.pyos.synchro.Yield()

    if cont and not cont.dead:
        setattr(cont, 'fading', 0)



def FormatMedalData(data):
    import xtriui
    fdata = []
    for part in (1, 2):
        dpart = {1: xtriui.Ribbon,
         2: xtriui.Medal}.get(part, None)
        pdata = []
        for row in data.Filter('part').get(part):
            (label, icon,) = row.graphic.split('.')
            color = row.color
            pdata.append((label, icon, color))

        fdata.append([dpart, pdata])

    return fdata



def GetFullscreenProjectionViewAndViewport():
    import trinity
    dev = trinity.GetDevice()
    viewport = dev.viewport
    camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
    view = trinity.TriView()
    view.transform = ((camera.view._11,
      camera.view._12,
      camera.view._13,
      camera.view._14),
     (camera.view._21,
      camera.view._22,
      camera.view._23,
      camera.view._24),
     (camera.view._31,
      camera.view._32,
      camera.view._33,
      camera.view._34),
     (camera.view._41,
      camera.view._42,
      camera.view._43,
      camera.view._44))
    return (camera.triProjection, view, viewport)



def SetStateFlag(container, data, top = 20, left = 4, showHint = True):
    import xtriui
    if container.destroyed:
        return 
    charID = getattr(data, 'charID', 0)
    if container.destroyed or container.state == uiconst.UI_HIDDEN or charID == eve.session.charid:
        return 
    fakeSlimItem = util.KeyVal()
    fakeSlimItem.ownerID = charID
    fakeSlimItem.charID = charID
    fakeSlimItem.corpID = data.Get('corpID', 0)
    fakeSlimItem.allianceID = data.Get('allianceID', 0)
    fakeSlimItem.warFactionID = data.Get('warFactionID', 0)
    if data.bounty:
        if data.bounty.bounty > 0.0:
            fakeSlimItem.bounty = data.bounty
    fakeSlimItem.groupID = data.Get('groupID', const.groupCharacter)
    fakeSlimItem.categoryID = data.Get('categoryID', const.categoryOwner)
    fakeSlimItem.securityStatus = data.Get('securityStatus', None)
    flag = sm.GetService('state').CheckStates(fakeSlimItem, 'flag')
    SetStateFlagForFlag(container, flag, charID=charID, top=top, left=left, showHint=showHint)



def SetStateFlagForFlag(container, flag, charID = None, top = 20, left = 4, showHint = True):
    import xtriui
    if flag and flag != -1:
        if container is None or container.destroyed:
            return 
        if session.charid == charID:
            ClearStateFlag(container)
            return 
        props = sm.GetService('state').GetStateProps(flag)
        filterName = props[0]
        if filterName:
            if getattr(container.sr, 'flag', None) is None:
                container.sr.flag = uicls.Container(parent=container, pos=(0, 0, 10, 10), name='flag', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, idx=0)
                uicls.Sprite(parent=container.sr.flag, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE)
                uicls.Fill(parent=container.sr.flag)
            col = sm.GetService('state').GetStateColor(flag)
            blink = sm.GetService('state').GetStateBlink('flag', flag)
            container.sr.flag.children[1].color.SetRGB(*col)
            container.sr.flag.children[1].color.a *= 0.75
            if blink:
                sm.GetService('ui').BlinkSpriteA(container.sr.flag.children[0], 1.0, 500, None, passColor=0)
                sm.GetService('ui').BlinkSpriteA(container.sr.flag.children[1], container.sr.flag.children[0].color.a, 500, None, passColor=0)
            else:
                sm.GetService('ui').StopBlink(container.sr.flag.children[0])
                sm.GetService('ui').StopBlink(container.sr.flag.children[1])
            iconNum = props[4] + 1
            container.sr.flag.width = container.sr.flag.height = 9
            container.sr.flag.left = left
            container.sr.flag.top = top
            if showHint:
                container.sr.flag.hint = filterName
            container.sr.flag.children[0].rectLeft = iconNum * 10
            return 
    if not container or container.destroyed:
        return 
    ClearStateFlag(container)



def ClearStateFlag(container):
    if container.destroyed:
        return 
    if getattr(container.sr, 'flag', None) is not None:
        flag = container.sr.flag
        container.sr.flag = None
        flag.Close()



def GetOwnerLogo(parent, ownerID, size = 64, noServerCall = False):
    if util.IsCharacter(ownerID):
        logo = uicls.Icon(icon=None, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
        if size < 64:
            fetchSize = 64
        else:
            fetchSize = size
        sm.GetService('photo').GetPortrait(ownerID, fetchSize, logo)
    elif util.IsCorporation(ownerID) or util.IsAlliance(ownerID) or util.IsFaction(ownerID):
        uiutil.GetLogoIcon(itemID=ownerID, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
    else:
        raise RuntimeError('ownerID %d is not of an owner type!!' % ownerID)


exports = util.AutoExports('uix', locals())

