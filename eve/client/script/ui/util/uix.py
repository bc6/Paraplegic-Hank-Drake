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
import localization
import fontConst
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
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Name'), GetItemName(rec, data).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), GetCategoryGroupTypeStringForItem(rec).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemMetaLevel'), ml or 0.0)
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Group'), data.groupName.lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Category'), data.categoryName.lower())
    if data.rec.typeID == const.typePlasticWrap:
        data.volume = ''
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Volume'), 0)
    else:
        volume = cfg.GetItemVolume(rec)
        u = cfg.dgmunits.Get(const.unitVolume)
        unit = u.displayName
        decimalPlaces = 2 if abs(volume - int(volume)) > const.FLOAT_TOLERANCE else 0
        data.volume = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=util.FmtAmt(volume, showFraction=decimalPlaces), unit=unit)
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Volume'), volume)
    data.scrollID = scrollID
    return data



def GetItemLabel(rec, data, new = 0):
    if getattr(data, 'label', None) and data.viewMode == 'icons' and not new:
        return data.label
    name = GetItemName(rec, data)
    if data.viewMode in ('list', 'details'):
        pType = ''
        fType = ''
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
                fType = {const.effectRigSlot: localization.GetByLabel('UI/Inventory/SlotRigs'),
                 const.effectHiPower: localization.GetByLabel('UI/Inventory/SlotHigh'),
                 const.effectMedPower: localization.GetByLabel('UI/Inventory/SlotMedium'),
                 const.effectLoPower: localization.GetByLabel('UI/Inventory/SlotLow')}.get(effect.effectID)
                continue

        stringDict = {localization.GetByLabel('UI/Common/Name'): name,
         localization.GetByLabel('UI/Inventory/ItemQuantity'): '<right>%s' % GetItemQty(data, 'ln'),
         localization.GetByLabel('UI/Inventory/ItemGroup'): data.groupName,
         localization.GetByLabel('UI/Inventory/ItemCategory'): data.categoryName,
         localization.GetByLabel('UI/Inventory/ItemSize'): pType,
         localization.GetByLabel('UI/Inventory/ItemSlot'): fType,
         localization.GetByLabel('UI/Inventory/ItemVolume'): '<right>%s' % data.volume,
         localization.GetByLabel('UI/Inventory/ItemMetaLevel'): '<right>%s' % data.metaLevel,
         localization.GetByLabel('UI/Inventory/ItemTechLevel'): '<right>%s' % techLevel}
        headers = GetVisibleItemHeaders(data.scrollID)
        labelList = []
        for each in headers:
            string = stringDict.get(each, '')
            labelList.append(string)

        label = '<t>'.join(labelList)
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
            name = localization.GetByLabel('UI/Station/StationInSolarSystem', station=invItem.itemID, solarsystem=invItem.locationID)
        except KeyError('RecordNotFound'):
            sys.exc_clear()
    elif invItem.groupID == const.groupVoucher:
        voucher = sm.GetService('voucherCache').GetVoucher(invItem.itemID)
        if voucher is None:
            name = localization.GetByLabel('UI/Common/Bookmark')
        else:
            name = voucher.GetDescription()
            if invItem.typeID == const.typeBookmark:
                try:
                    (name, _desc,) = sm.GetService('addressbook').UnzipMemo(voucher.GetDescription())
                except:
                    name = localization.GetByLabel('UI/Common/Bookmark')
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
        return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', cloudType=cfg.invtypes.Get(slimItem.typeID).name)
    else:
        if slimItem.categoryID == const.categoryAsteroid:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', asteroidType=cfg.invtypes.Get(slimItem.typeID).name)
        if slimItem.categoryID == const.categoryShip:
            if not slimItem.charID or slimItem.charID == eve.session.charid and slimItem.itemID != eve.session.shipid:
                return cfg.invtypes.Get(slimItem.typeID).name
            if util.IsCharacter(slimItem.charID):
                return cfg.eveowners.Get(slimItem.charID).name
        elif slimItem.categoryID == const.categoryOrbital:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimOrbital', typeID=slimItem.typeID, planetID=slimItem.planetID, corpName=cfg.eveowners.Get(slimItem.ownerID).name)
        locationname = cfg.evelocations.Get(slimItem.itemID).name
        if locationname and locationname[0] != '@':
            if slimItem.groupID == const.groupBeacon:
                dungeonNameID = getattr(slimItem, 'dungeonNameID', None)
                if dungeonNameID:
                    translatedName = localization.GetByMessageID(dungeonNameID)
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



def GetTextHeight(strng, width = 0, fontsize = fontConst.EVE_MEDIUM_FONTSIZE, linespace = None, hspace = 0, singleLine = 0, uppercase = 0, specialIndent = 0, getTextObj = 0, tabs = [], **kwds):
    return sm.GetService('font').GetTextHeight(strng, width=width, font=None, fontsize=fontsize, linespace=linespace, letterspace=hspace, singleline=singleLine, uppercase=uppercase, specialIndent=specialIndent, getTextObj=getTextObj, tabs=tabs)



def GetTextWidth(strng, fontsize = fontConst.EVE_MEDIUM_FONTSIZE, hspace = 0, uppercase = 0):
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
        return localization.GetByLabel('UI/Standings/Excellent')
    else:
        if standing > 0:
            return localization.GetByLabel('UI/Standings/Good')
        if standing == 0:
            return localization.GetByLabel('UI/Standings/Neutral')
        if standing < -5:
            return localization.GetByLabel('UI/Standings/Terrible')
        if standing < 0:
            return localization.GetByLabel('UI/Standings/Bad')
        return localization.GetByLabel('UI/Standings/Unknown')



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
            (icon, hint,) = {2: ('ui_73_16_242', localization.GetByLabel('UI/Inventory/TechLevel2')),
             3: ('ui_73_16_243', localization.GetByLabel('UI/Inventory/TechLevel3'))}.get(techLevel, None)
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
    t = uicls.EveLabelMedium(text=caption, name='header1', parent=par, padding=(8, 1, 8, 2), align=uiconst.TOTOP, bold=True)
    container.height = t.textheight + 3
    return container



def GetSlider(name = 'slider', where = None, config = '', minval = None, maxval = None, header = '', hint = '', align = None, width = 0, height = 18, left = 0, top = 0, setlabelfunc = None, getvaluefunc = None, endsliderfunc = None, gethintfunc = None, increments = [], underlay = 1):
    import xtriui
    if align is None:
        align = uiconst.TOTOP
    mainpar = uicls.Container(name=config + '_slider', align=align, width=width, height=height, left=left, top=top, state=uiconst.UI_NORMAL, parent=where)
    slider = xtriui.Slider(parent=mainpar, align=uiconst.TOPLEFT, top=6, state=uiconst.UI_NORMAL)
    lbl = uicls.EveLabelSmall(text='', parent=mainpar, left=7, top=-14, state=uiconst.UI_NORMAL)
    lbl.name = 'label'
    if getvaluefunc:
        slider.GetSliderValue = getvaluefunc
    if setlabelfunc:
        slider.SetSliderLabel = setlabelfunc
    if gethintfunc:
        slider.GetSliderHint = gethintfunc
    slider.Startup(config, minval, maxval, config, header, increments=increments)
    slider.name = name
    mainpar.hint = hint
    if endsliderfunc:
        slider.EndSetSliderValue = endsliderfunc
    return mainpar


SEL_FILES = 0
SEL_FOLDERS = 1
SEL_BOTH = 2

def GetFileDialog(path = None, fileExtensions = None, multiSelect = False, selectionType = SEL_FILES):
    wnd = form.FileDialog.Open(path=path, fileExtensions=fileExtensions, multiSelect=multiSelect, selectionType=selectionType)
    wnd.width = 400
    wnd.height = 400
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None



def __Search(searchStr, groupID, exact, filterCorpID, hideNPC = False):
    if groupID == const.groupCharacter:
        if hideNPC:
            result = sm.RemoteSvc('lookupSvc').LookupEvePlayerCharacters(searchStr, exact)
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
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return 
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
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
    attrLocGroupNamePlural = {const.groupCharacter: 'UI/Common/Characters',
     const.groupCorporation: 'UI/Common/Corporations',
     const.groupFaction: 'UI/Common/Factions',
     const.groupStation: 'UI/Common/Stations',
     const.groupAsteroidBelt: 'UI/Common/AsteroidBelts',
     const.groupSolarSystem: 'UI/Common/SolarSystems',
     const.groupConstellation: 'UI/Common/Constellations',
     const.groupRegion: 'UI/Common/Regions',
     const.groupAlliance: 'UI/Common/Alliances'}.get(groupID, '')
    if categoryID is not None and categoryID == const.categoryOwner:
        result = FilterResult(sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact), filterGroups, hideNPC, attrGroupName)
        owners = [ each.ownerID for each in result ]
        if owners:
            cfg.eveowners.Prime(owners)
        displayGroupName = localization.GetByLabel('UI/Common/Owner')
        displayGroupNamePlural = localization.GetByLabel('UI/Common/Owners')
    else:
        displayGroupName = cfg.invgroups.Get(groupID).name
        if attrGroupName and attrLocGroupNamePlural:
            displayGroupNamePlural = localization.GetByLabel(attrLocGroupNamePlural)
        else:
            displayGroupNamePlural = displayGroupName
        result = FilterResult(__Search(searchStr, groupID, exact, filterCorpID, hideNPC), filterGroups, [0, hideNPC][(groupID in (const.groupCharacter, const.groupCorporation))], attrGroupName)
    if result is None or not len(result):
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        if exact and groupID == const.groupCharacter:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoCharacterFoundWith', searchTerm=searchStr)})
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return 
    if len(result) >= 1:
        if len(result) == 1:
            if GetAttr(result[0], 'ID', attrGroupName) and modal:
                if notifyOneMatch:
                    return (GetAttr(result[0], 'ID', attrGroupName), 1)
                return GetAttr(result[0], 'ID', attrGroupName)
            hint = localization.GetByLabel('UI/Search/OneGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        else:
            hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(result), groupNames=displayGroupNamePlural, searchTerm=searchStr)
        tmplist = []
        for each in result:
            id = GetAttr(each, 'ID', attrGroupName)
            if groupID == const.groupCorporation and exact == -1:
                name = '%s %s' % (GetAttr(each, 'tickerName', attrGroupName), GetAttr(each, 'Name', attrGroupName))
            elif groupID == const.groupAlliance and exact == -1:
                name = '%s %s' % (GetAttr(each, 'shortName', attrGroupName), GetAttr(each, 'Name', attrGroupName))
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
            selectionText = localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName)
            chosen = ListWnd(tmplist, attrGroupName.lower(), [displayGroupNamePlural, selectionText][modal], hint, 1, minChoices=modal, isModal=modal, windowName=searchWndName, unstackable=1)
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
    groupNames = {const.groupCharacter: [localization.GetByLabel('UI/Common/Character'), localization.GetByLabel('UI/Common/Characters')],
     const.groupCorporation: [localization.GetByLabel('UI/Common/Corporation'), localization.GetByLabel('UI/Common/Corporations')],
     const.groupAlliance: [localization.GetByLabel('UI/Common/Alliance'), localization.GetByLabel('UI/Common/Alliances')],
     const.groupFaction: [localization.GetByLabel('UI/Common/Faction'), localization.GetByLabel('UI/Common/Factions')]}
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return 
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
        return 
    displayGroupName = ''
    displayGroupNamePlural = ''
    for g in groupNames:
        if g in groupIDs:
            displayGroupName += groupNames[g][0] + '/'
            displayGroupNamePlural += groupNames[g][1] + '/'

    displayGroupName = displayGroupName[:-1]
    displayGroupNamePlural = displayGroupNamePlural[:-1]
    if hideNPC:
        owners = sm.RemoteSvc('lookupSvc').LookupPCOwners(searchStr, exact)
    else:
        owners = sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact)
    list = []
    for o in owners:
        if o.groupID in groupIDs:
            list.append(('%s %s' % (o.ownerName, groupNames[o.groupID][0]), o.ownerID, o.typeID))

    if not list:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return 
    if len(list) == 1 and not notifyOneMatch:
        return list[0][1]
    hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(list), groupNames=displayGroupNamePlural, searchTerm=searchStr)
    chosen = ListWnd(lst=list, listtype='owner', caption=localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName), hint=hint, ordered=1, minChoices=1, windowName=searchWndName)
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
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/PleaseTypeSomething')})
        return 
    stationinfo = GetStationByName(stationname.lower(), flag)
    if stationinfo is None or not len(stationinfo):
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoStationFoundWith', searchTerm=stationname)})
        return 
    if len(stationinfo) > 20:
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/MoreThanLimitStationsFound', limit=20, searchTerm=stationname)})
        return 
    if len(stationinfo) >= 1 and len(stationinfo) <= 20:
        if len(stationinfo) == 1:
            if stationinfo[0].stationName == stationname:
                return 
            hint = localization.GetByLabel('UI/Search/OneStationFoundWith', searchTerm=stationname)
        elif len(stationinfo) <= 20:
            hint = localization.GetByLabel('UI/Search/ManyStationsFoundWith', itemCount=len(stationinfo), searchTerm=stationname)
        if len(stationinfo) == 1:
            return stationinfo[0].stationID
        tmplist = []
        for each in stationinfo:
            tmplist.append((each.stationName, each.stationID, 0))

        sm.GetService('loading').StopCycle()
        choosestation = ListWnd(tmplist, 'station', localization.GetByLabel('UI/Search/SelectStation'), hint, 1)
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
        caption = localization.GetByLabel('UI/Search/SelectItem')
    form.ListWindow.CloseIfOpen(windowID=windowName)
    wnd = form.ListWindow(windowID=windowName, lst=lst, listtype=listtype, ordered=ordered, minSize=(minw, minh), caption=caption, minChoices=minChoices, maxChoices=maxChoices, initChoices=initChoices, validator=validator, scrollHeaders=scrollHeaders, iconMargin=iconMargin, lstDataIsGrouped=lstDataIsGrouped)
    if hint:
        wnd.SetHint(['<center>', hint])
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



def HybridWnd(format, caption, modal = 1, windowID = None, buttons = None, location = None, minW = 256, minH = 256, blockconfirm = 0, icon = None, unresizeAble = 0, ignoreCurrent = 1):
    if windowID is not None:
        wnd = uicls.Window.GetIfOpen(windowID=windowID)
        if wnd:
            return 
    windowID = windowID or caption
    if buttons is None:
        buttons = uiconst.OK
    wnd = form.HybridWindow.Open(ignoreCurrent=ignoreCurrent, format=format, caption=caption, modal=modal, windowID=windowID, buttons=buttons, location=location, minW=minW, minH=minH, icon=icon, blockconfirm=blockconfirm)
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
        caption = localization.GetByLabel('UI/Common/Name/TypeInName')
    if label is None:
        label = localization.GetByLabel('UI/Common/Name/TypeInName')
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



def TextBox(header, txt, modal = 0, windowID = 'generictextbox2', tabs = [], preformatted = 0, scrolltotop = 1):
    wnd = uicls.Window.GetIfOpen(windowID=windowID)
    if wnd is None or wnd.destroyed or uicore.uilib.Key(uiconst.VK_SHIFT):
        format = [{'type': 'textedit',
          'readonly': 1,
          'label': '_hide',
          'key': 'text'}]
        wnd = HybridWnd(format, header, modal, windowID, uiconst.CLOSE, None, minW=256, minH=128)
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
        return localization.GetByLabel('UI/Common/PleaseTypeSomething')
    return ''



def QtyPopup(maxvalue = None, minvalue = 0, setvalue = '', hint = None, caption = None, label = '', digits = 0):
    if caption is None:
        caption = localization.GetByLabel('UI/Common/SetQuantity')
    if maxvalue is not None and hint is None:
        hint = localization.GetByLabel('UI/Common/SetQtyBetween', min=util.FmtAmt(minvalue), max=util.FmtAmt(maxvalue))
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
    return [localization.GetByLabel('UI/Inventory/ItemMetaLevel'), localization.GetByLabel('UI/Inventory/ItemTechLevel'), localization.GetByLabel('UI/Inventory/ItemCategory')]



def GetInvItemDefaultHeaders():
    return [localization.GetByLabel('UI/Common/Name'),
     localization.GetByLabel('UI/Common/Quantity'),
     localization.GetByLabel('UI/Inventory/ItemGroup'),
     localization.GetByLabel('UI/Inventory/ItemCategory'),
     localization.GetByLabel('UI/Inventory/ItemSize'),
     localization.GetByLabel('UI/Inventory/ItemSlot'),
     localization.GetByLabel('UI/Inventory/ItemVolume'),
     localization.GetByLabel('UI/Inventory/ItemMetaLevel'),
     localization.GetByLabel('UI/Inventory/ItemTechLevel')]



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
    blue.pyos.synchro.SleepWallclock(after)
    (start, ndt,) = (blue.os.GetWallclockTime(), 0.0)
    while ndt != 1.0:
        if not cont or cont.destroyed:
            break
        ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / fadeTime, 1.0)
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

