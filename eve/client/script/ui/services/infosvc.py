import sys
import service
import blue
import bluepy
import uthread
import uix
import uiutil
import xtriui
import form
import util
import copy
import base
import random
import types
import state
import listentry
import uiconst
import uicls
import log
MINWIDTH = 325
MINHEIGHTREGULAR = 280
MINHEIGHTMEDAL = 480

def ReturnNone():
    return None



def ReturnArg(arg):
    return arg



class BadArgs(RuntimeError):

    def __init__(self, msgID, dict = None):
        RuntimeError.__init__(self, msgID, dict or {})




class Info(service.Service):
    __exportedcalls__ = {'ShowInfo': [],
     'FormatWnd': [],
     'GetAttrTypeInfo': [],
     'GetAttrItemInfo': [],
     'GetSolarSystemReport': [],
     'FormatUnit': [],
     'FormatValue': [],
     'GetFormatAndValue': [],
     'GetKillsRecentKills': [],
     'GetKillsRecentLosses': [],
     'GetKillRightsSubContent': [],
     'GetEmploymentHistorySubContent': [],
     'GetAllianceMembersSubContent': []}
    __guid__ = 'svc.info'
    __notifyevents__ = ['DoSessionChanging',
     'OnItemChange',
     'OnAllianceRelationshipChanged',
     'OnContactChange']
    __update_on_reload__ = 0
    __servicename__ = 'info'
    __displayname__ = 'Information Service'
    __dependencies__ = ['dataconfig']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, memStream = None):
        self.LogInfo('Starting InfoSvc')
        self.wnds = []
        self.lastActive = None
        self.moniker = None
        self.attributesByName = None
        self.ClearWnds()



    def OnItemChange(self, item, change):
        if item.categoryID != const.categoryCharge and (item.locationID == eve.session.shipid or const.ixLocationID in change and change[const.ixLocationID] == eve.session.shipid):
            self.itemchangeTimer = base.AutoTimer(1000, self.DelayOnItemChange, item, change)
        itemGone = False
        if const.ixLocationID in change and util.IsJunkLocation(item.locationID):
            itemGone = True
        if const.ixQuantity in change and item.stacksize == 0:
            log.LogTraceback('infoSvc processing ixQuantity change')
            itemGone = True
        if const.ixStackSize in change and item.stacksize == 0:
            itemGone = True
        if itemGone:
            for each in self.wnds:
                if each is None or each.destroyed:
                    self.wnds.remove(each)
                    continue
                if each.sr.itemID == item.itemID:
                    self.FormatWnd(each, each.sr.typeID, None, None)




    def DelayOnItemChange(self, item, change):
        self.itemchangeTimer = None
        for each in self.wnds:
            if each is None or each.destroyed:
                self.wnds.remove(each)
                continue
            if each.sr.itemID == eve.session.shipid and not each.IsMinimized():
                self.FormatWnd(each, each.sr.typeID, each.sr.itemID, each.sr.rec)




    def OnContactChange(self, contactIDs, contactType = None):
        for contactID in contactIDs:
            self.UpdateWnd(contactID)




    def OnAllianceRelationshipChanged(self, *args):
        for allianceid in (args[0], args[1]):
            self.UpdateWnd(allianceid)




    def GetShipAttributes(self):
        if not hasattr(self, 'shipAttributes'):
            self.shipAttributes = [(mls.UI_GENERIC_STRUCTURE, [const.attributeCapacity,
               const.attributeDroneCapacity,
               const.attributeDroneBandwidth,
               const.attributeMass,
               const.attributeVolume,
               const.attributeAgility,
               const.attributeEmDamageResonance,
               const.attributeExplosiveDamageResonance,
               const.attributeKineticDamageResonance,
               const.attributeThermalDamageResonance,
               const.attributeSpecialAmmoHoldCapacity,
               const.attributeSpecialGasHoldCapacity,
               const.attributeSpecialIndustrialShipHoldCapacity,
               const.attributeSpecialLargeShipHoldCapacity,
               const.attributeSpecialMediumShipHoldCapacity,
               const.attributeSpecialMineralHoldCapacity,
               const.attributeSpecialOreHoldCapacity,
               const.attributeSpecialSalvageHoldCapacity,
               const.attributeSpecialShipHoldCapacity,
               const.attributeSpecialSmallShipHoldCapacity,
               const.attributeSpecialCommandCenterHoldCapacity,
               const.attributeSpecialPlanetaryCommoditiesHoldCapacity]),
             (mls.UI_GENERIC_ARMOR, [const.attributeArmorEmDamageResonance,
               const.attributeArmorExplosiveDamageResonance,
               const.attributeArmorKineticDamageResonance,
               const.attributeArmorThermalDamageResonance]),
             (mls.UI_GENERIC_SHIELD, [const.attributeShieldRechargeRate,
               const.attributeShieldEmDamageResonance,
               const.attributeShieldExplosiveDamageResonance,
               const.attributeShieldKineticDamageResonance,
               const.attributeShieldThermalDamageResonance]),
             (mls.UI_GENERIC_CAPACITOR, [const.attributeRechargeRate]),
             (mls.UI_GENERIC_TARGETING, [const.attributeMaxTargetRange,
               const.attributeMaxLockedTargets,
               const.attributeScanResolution,
               const.attributeScanLadarStrength,
               const.attributeScanMagnetometricStrength,
               const.attributeScanRadarStrength,
               const.attributeScanGravimetricStrength,
               const.attributeSignatureRadius]),
             (mls.UI_INFOWND_SHAREDFAC, [const.attributeCorporateHangarCapacity, const.attributeShipMaintenanceBayCapacity, const.attributeMaxJumpClones]),
             (mls.UI_INFOWND_JUMPDRIVESYS, [const.attributeJumpDriveCapacitorNeed,
               const.attributeJumpDriveRange,
               const.attributeJumpDriveConsumptionType,
               const.attributeJumpDriveConsumptionAmount,
               const.attributeJumpDriveDuration,
               const.attributeJumpPortalCapacitorNeed,
               const.attributeJumpPortalConsumptionMassFactor,
               const.attributeJumpPortalDuration,
               const.attributeSpecialFuelBayCapacity]),
             (mls.UI_GENERIC_PROPULSION, [const.attributeMaxVelocity])]
        return self.shipAttributes



    def GetBlueprintAttributes(self):
        self.blueprintAttributes = [(mls.UI_INFOWND_PRODUCES, ['productTypeID']),
         (mls.UI_GENERIC_GENERALINFO, ['materialLevel',
           'wastageFactor',
           'copy',
           'productivityLevel',
           'licensedProductionRunsRemaining',
           'maxProductionLimit']),
         (mls.UI_RMR_MANUFACTURING, ['manufacturingTime']),
         (mls.SHARED_RESEARCHING, ['researchMaterialTime',
           'researchCopyTime',
           'researchProductivityTime',
           'researchTechTime'])]
        return self.blueprintAttributes



    def GetAttributeOrder(self):
        if not hasattr(self, 'attributeOrder'):
            self.attributeOrder = [const.attributePrimaryAttribute,
             const.attributeSecondaryAttribute,
             const.attributeRequiredSkill1,
             const.attributeRequiredSkill2,
             const.attributeRequiredSkill3,
             const.attributeRequiredSkill4,
             const.attributeRequiredSkill5,
             const.attributeRequiredSkill6]
        return self.attributeOrder



    def Stop(self, memStream = None):
        self.ClearWnds()
        self.lastActive = None
        self.moniker = None
        self.attributesByName = None
        self.wnds = []



    def ClearWnds(self):
        self.wnds = []
        if sm.IsServiceRunning('window'):
            for each in sm.GetService('window').GetWindows()[:]:
                if each is not None and not each.destroyed and each.name.startswith('infowindow'):
                    each.Close()




    def DoSessionChanging(self, isremote, session, change):
        self.moniker = None
        if session.charid is None:
            self.ClearWnds()



    def GetSolarSystemReport(self, solarsystemID = None):
        solarsystemID = solarsystemID or eve.session.solarsystemid or eve.session.solarsystemid2
        if solarsystemID is None:
            return 
        items = sm.RemoteSvc('config').GetMapObjects(solarsystemID, 0, 0, 0, 1, 0)
        types = {}
        for celestial in items:
            types.setdefault(celestial.groupID, []).append(celestial)

        for groupID in types.iterkeys():
            if groupID == const.groupStation:
                continue

        if const.groupStation in types:
            for station in types[const.groupStation]:
                print '   ',
                print station.itemName




    def ShowInfo(self, typeID, itemID = None, new = 0, rec = None, parentID = None, headerOnly = 0, abstractinfo = None):
        if eve.session.charid and itemID == eve.session.charid:
            sm.GetService('charactersheet').Show()
            return 
        if itemID == const.factionUnknown:
            eve.Message('KillerOfUnknownFaction')
            return 
        modal = uicore.registry.GetModalWindow()
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        new = new or not settings.user.ui.Get('useexistinginfownd', 1) or uicore.uilib.Key(uiconst.VK_SHIFT)
        wnd = self.GetWnd(new, modal, itemID=itemID, typeID=typeID)
        if wnd is None or wnd.destroyed:
            wnd = self.GetWnd(1, modal, itemID=itemID, typeID=typeID)
        if getattr(wnd, 'IsBusy', 0):
            return 
        wnd.IsBrowser = 1
        wnd.GoTo = self.GoTo
        wnd.Maximize()
        self.FormatWnd(wnd, typeID, itemID, rec=rec, parentID=parentID, headerOnly=headerOnly, abstractinfo=abstractinfo)
        return wnd



    def UpdateWnd(self, itemID, maximize = 0):
        for wnd in self.wnds:
            if wnd.sr.itemID == itemID or getattr(wnd.sr, 'corpID', None) == itemID or getattr(wnd.sr, 'allianceID', None) == itemID:
                self.FormatWnd(wnd, wnd.sr.typeID, wnd.sr.itemID)
                if maximize:
                    wnd.Maximize()
                break




    def GetWnd(self, new = 0, modal = None, unknown = 0, itemID = None, typeID = None):
        if len(self.wnds):
            for each in self.wnds:
                if each is None or each.destroyed:
                    self.wnds.remove(each)

        if len(self.wnds) and not new:
            if self.lastActive is not None and self.lastActive in self.wnds:
                self.SaveNote(self.lastActive, closing=1)
                return self.lastActive
            wnd = self.wnds[-1]
            if not modal or modal and modal.parent == wnd.parent:
                self.SaveNote(wnd, closing=1)
                return wnd
        else:
            if new:
                sm.GetService('window').ResetToDefaults('infowindow')
            skipCornerAligmentCheck = False
            wndCheck = sm.GetService('window').GetWindow('infowindow')
            if not settings.user.ui.Get('useexistinginfownd', 1) and wndCheck:
                skipCornerAligmentCheck = True
            wnd = sm.GetService('window').GetWindow('infowindow', create=1, ignoreCurrent=new, skipCornerAligmentCheck=skipCornerAligmentCheck)
            if modal and not modal.destroyed and modal.name != 'progresswindow':
                uiutil.Transplant(wnd, modal.parent, 0)
            height = MINHEIGHTREGULAR
            if typeID and typeID == const.typeMedal:
                height = MINHEIGHTMEDAL
            wnd.SetMinSize([MINWIDTH, height])
            wnd.SetWndIcon()
            wnd.scope = 'station_inflight'
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            uix.Flush(wnd.sr.topParent)
            wnd.sr.toparea = uicls.Container(name='topareasub', parent=wnd.sr.topParent, align=uiconst.TOALL, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), clipChildren=0, state=uiconst.UI_PICKCHILDREN)
            wnd.sr.mainiconparent = uicls.Container(name='mainiconparent', parent=wnd.sr.toparea, align=uiconst.TOLEFT)
            wnd.sr.techicon = uicls.Sprite(name='techIcon', parent=wnd.sr.mainiconparent, align=uiconst.RELATIVE, left=0, width=16, height=16, idx=0)
            wnd.sr.mainicon = uicls.Container(name='mainicon', parent=wnd.sr.mainiconparent, align=uiconst.TOTOP)
            wnd.sr.leftpush = uicls.Container(name='leftpush', parent=wnd.sr.toparea, align=uiconst.TOLEFT, width=6, state=uiconst.UI_DISABLED)
            wnd.sr.captionpush = uicls.Container(name='captionpush', parent=wnd.sr.toparea, align=uiconst.TOTOP, height=6)
            wnd.sr.captioncontainer = uicls.Container(name='captioncontainer', parent=wnd.sr.toparea, align=uiconst.TOTOP, height=24, state=uiconst.UI_PICKCHILDREN)
            wnd.sr.subinfolinkcontainer = uicls.Container(name='subinfolinkcontainer', parent=wnd.sr.toparea, align=uiconst.TOTOP, height=24)
            wnd.sr.therestpush = uicls.Container(name='therestpush', parent=wnd.sr.toparea, align=uiconst.TOTOP, height=6)
            wnd.sr.therestcontainer = uicls.Container(name='therestcontainer', parent=wnd.sr.toparea, align=uiconst.TOTOP, height=24)
            wnd.sr.captioncontainer.OnResize = (self.RecalcCaptionContainer, wnd)
            wnd.sr.therestcontainer.OnResize = (self.RecalcTheRestContainer, wnd)
            wnd.sr.subcontainer = uicls.Container(name='maincontainersub', parent=wnd.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            wnd.sr.scroll = uicls.Scroll(name='scroll', parent=wnd.sr.subcontainer, state=uiconst.UI_HIDDEN, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            wnd.sr.scroll.sr.ignoreTabTrimming = True
            wnd.sr.notesedit = uicls.EditPlainText(parent=wnd.sr.subcontainer, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), align=uiconst.TOALL, maxLength=5000, showattributepanel=1, state=uiconst.UI_HIDDEN)
            wnd.sr.descedit = uicls.Edit(parent=wnd.sr.subcontainer, state=uiconst.UI_HIDDEN, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), readonly=1)
            wnd.sr.itemname = None
            wnd.OnClose_ = self.CloseWnd
            wnd.OnSetActive = self.OnActivateWnd
            if not unknown:
                self.wnds.append(wnd)
            wnd.state = uiconst.UI_HIDDEN
            wnd.sr.history = []
            wnd.sr.historyIdx = None
            return wnd



    def CloseWnd(self, wnd, *args):
        if wnd in self.wnds:
            self.wnds.remove(wnd)
        self.SaveNote(wnd, 1)
        if self.lastActive == wnd:
            self.lastActive = None
        for each in ['scroll', 'notesedit', 'descedit']:
            item = getattr(wnd.sr, each, None)
            if item is not None and not item.destroyed:
                item.Close()
            setattr(wnd.sr, each, None)

        wnd.sr.corpinfo = None
        wnd.sr.allianceinfo = None
        wnd.sr.factioninfo = None
        wnd.sr.warfactioninfo = None
        wnd.sr.plasticinfo = None
        wnd.sr.voucherinfo = None
        wnd.sr.allianceID = None
        wnd.sr.corpID = None
        wnd.OnClose_ = None
        wnd.OnSetActive = None



    def OnActivateWnd(self, wnd, *args):
        self.lastActive = wnd



    def ParseTabs(self, wnd, tabs = None):
        if tabs is None:
            tabs = self.GetInfoTabs()
            wnd.sr.data = {}
            wnd.sr.dynamicTabs = []
            wnd.sr.infotabs = tabs
            wnd.sr.data['buttons'] = []
        for (listtype, subtabs,) in tabs:
            wnd.sr.data[listtype] = {'name': listtype,
             'items': [],
             'subtabs': subtabs,
             'inited': 0,
             'headers': []}
            if subtabs:
                self.ParseTabs(wnd, subtabs)




    def GetInfoTabs(self):
        return [(mls.UI_GENERIC_ATTRIBUTES, []),
         (mls.UI_CORP_CORPMEMBERS, []),
         (mls.UI_INFOWND_NEIGHBORS, []),
         (mls.UI_INFOWND_CHILDREN, []),
         (mls.UI_GENERIC_FITTING, []),
         (mls.UI_SHARED_CERTPREREQ, [(mls.UI_GENERIC_SKILLS, []), (mls.UI_SHARED_CERTIFICATES, [])]),
         (mls.UI_SHARED_CERT_RECOMMENDED, []),
         (mls.UI_SHARED_CERT_RECOMMENDEDFOR, []),
         (mls.UI_GENERIC_VARIATIONS, []),
         (mls.UI_GENERIC_KILLRIGHTS, []),
         (mls.UI_GENERIC_LEGALITY, []),
         (mls.UI_GENERIC_JUMPS, []),
         (mls.UI_GENERIC_MODULES, []),
         (mls.UI_GENERIC_ORBITALBODIES, []),
         (mls.UI_GENERIC_SYSTEMS, []),
         (mls.UI_GENERIC_LOCATION, []),
         (mls.UI_GENERIC_AGENTINFO, []),
         (mls.UI_GENERIC_AGENTS, []),
         (mls.UI_GENERIC_ROUTE, []),
         (mls.UI_GENERIC_INSURANCE, []),
         (mls.UI_GENERIC_SERVICES, []),
         (mls.UI_GENERIC_STANDINGS, []),
         (mls.UI_GENERIC_DECORATIONS, [(mls.UI_SHARED_CERTIFICATES2, []), (mls.UI_GENERIC_MEDALS, []), (mls.UI_GENERIC_RANKS, [])]),
         (mls.UI_GENERIC_MEMBERCORPS, []),
         (mls.UI_GENERIC_MARTKETACTIVITY, []),
         (mls.UI_GENERIC_DATA, []),
         (mls.UI_GENERIC_BILLOFMATERIALS, [(mls.UI_GENERIC_MANUFACTURING, []),
           (mls.UI_GENERIC_COPYING, []),
           (mls.UI_GENERIC_RESEARCHINGMATERIALEFF, []),
           (mls.UI_GENERIC_RESEARCHTIMEPROD, []),
           (mls.UI_GENERIC_DUBLICATING, []),
           (mls.UI_GENERIC_REVERSEENGINEERING, []),
           (mls.UI_GENERIC_REVERSEENGINEERING2, [])]),
         (mls.UI_GENERIC_EMPLOYMENTHIST, []),
         (mls.UI_GENERIC_ALLIANCEHIST, []),
         (mls.UI_GENERIC_FUELREQUIREMENTS, []),
         (mls.UI_GENERIC_MATERIALREQUIREMENTS, []),
         (mls.UI_GENERIC_REACTION, []),
         (mls.UI_GENERIC_NOTES, []),
         (mls.UI_GENERIC_DOGMA, []),
         (mls.UI_GENERIC_MEMBERS, []),
         (mls.UI_GENERIC_UNKNOWN, []),
         (mls.UI_INFOWND_HIERARCHY, []),
         (mls.UI_PI_SCHEMATICS, []),
         (mls.UI_PI_PRODUCTIONINFO, [])]



    def __PreFormatWnd(self, wnd, typeID, itemID, *args):
        self.FormatWnd(wnd, typeID, itemID)
        return wnd



    def FormatWnd(self, wnd, typeID, itemID = None, rec = None, parentID = None, historyData = None, headerOnly = 0, abstractinfo = None):
        try:
            if wnd is not None and not wnd.destroyed:
                wnd.ShowLoad()
            else:
                return 
            self.loading = 1
            wnd.IsBusy = 1
            self.HideError(wnd)
            if wnd.top == uicore.desktop.height:
                wnd.Maximize()
            else:
                wnd.state = uiconst.UI_NORMAL
            wnd.sr.itemID = itemID
            wnd.sr.typeID = typeID
            wnd.sr.rec = rec
            wnd.sr.abstractinfo = abstractinfo
            wnd.sr.corpinfo = None
            wnd.sr.allianceinfo = None
            wnd.sr.factioninfo = None
            wnd.sr.warfactioninfo = None
            wnd.sr.stationinfo = None
            wnd.sr.plasticinfo = None
            wnd.sr.voucherinfo = None
            wnd.sr.itemname = None
            wnd.sr.variationbtm = None
            wnd.sr.corpID = None
            wnd.sr.allianceID = None
            wnd.sr.scroll.state = uiconst.UI_HIDDEN
            wnd.sr.notesedit.state = uiconst.UI_HIDDEN
            wnd.sr.descedit.state = uiconst.UI_HIDDEN
            setattr(wnd.sr, 'oldnotes', None)
            wnd.sr.maintabs = None
            self.ParseTabs(wnd)
            uix.Flush(wnd.sr.captionpush)
            uix.Flush(wnd.sr.captioncontainer)
            uix.Flush(wnd.sr.subinfolinkcontainer)
            uix.Flush(wnd.sr.therestcontainer)
            wnd.sr.subinfolinkcontainer.height = 0
            uiutil.FlushList(wnd.sr.subcontainer.children[:-3])
            self.GetWindowSettings(wnd, typeID, itemID)
            height = MINHEIGHTREGULAR
            if typeID == const.typeMedal:
                height = MINHEIGHTMEDAL
            wnd.SetMinSize([MINWIDTH, height])
            self.GetIcon(wnd, typeID, itemID)
            desc = self.GetNameAndDescription(wnd, typeID, itemID)
            bio = None
            if wnd.sr.isCharacter and itemID:
                if not headerOnly:
                    wnd.sr.dynamicTabs.append((mls.UI_GENERIC_NOTES, 'Notes'))
                corpid = None
                allianceid = None
                parallelCalls = []
                if util.IsNPC(itemID):
                    parallelCalls.append((ReturnNone, ()))
                    parallelCalls.append((ReturnNone, ()))
                else:
                    parallelCalls.append((sm.RemoteSvc('charMgr').GetPublicInfo3, (itemID,)))
                    parallelCalls.append((sm.GetService('corp').GetInfoWindowDataForChar, (itemID, 1)))
                if not util.IsNPC(itemID):
                    parallelCalls.append((sm.RemoteSvc('standing2').GetSecurityRating, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                (charinfo, corpCharInfo, security,) = uthread.parallel(parallelCalls)
                if not util.IsNPC(itemID):
                    charinfo = charinfo[0]
                    bio = charinfo.description
                    corpAge = blue.os.GetTime() - charinfo.startDateTime
                    if getattr(charinfo, 'medal1GraphicID', None):
                        uicls.Icon(icon='ui_50_64_16', parent=wnd.sr.mainicon, left=70, top=80, size=64, align=uiconst.RELATIVE, idx=0)
                if corpCharInfo:
                    corpid = corpCharInfo.corpID
                    allianceid = corpCharInfo.allianceID
                    wnd.sr.corpID = corpid
                    wnd.sr.allianceID = allianceid
                    title = ''
                    if corpCharInfo.title:
                        title = corpCharInfo.title
                    for ix in xrange(1, 17):
                        titleText = getattr(corpCharInfo, 'title%s' % ix, None)
                        if titleText:
                            title = '%s%s%s' % (title, ['', ', '][(not not len(title))], titleText)

                    if len(title) > 0:
                        text = uicls.Label(text='%s: %s' % (mls.UI_GENERIC_TITLE, title), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, fontsize=9, linespace=11, uppercase=1, letterspace=1)
                        if text.height > 405:
                            text.autoheight = 0
                            text.height = 405
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4, state=uiconst.UI_DISABLED)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                if not util.IsNPC(itemID):
                    uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP)
                    uicls.Container(name='push', parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, height=4)
                    uicls.Label(text='%s: %.1f' % (mls.UI_GENERIC_SECURITYSTATUS, security), parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                    standing = sm.GetService('standing').GetStanding(eve.session.corpid, itemID)
                    if standing is not None:
                        uicls.Label(text='%s: %.1f' % (mls.UI_GENERIC_CORPSTANDING, standing), parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                    if charinfo.bounty:
                        self.Wanted(wnd, charinfo.bounty)
                if wnd.sr.isCharacter and util.IsNPC(itemID):
                    agentInfo = sm.GetService('agents').GetAgentByID(itemID)
                    if agentInfo:
                        corpid = agentInfo.corporationID
                    else:
                        corpid = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(itemID)
                if corpid:
                    uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOTOP, height=4)
                    self.GetCorpLogo(corpid, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                    wnd.sr.subinfolinkcontainer.height = 64
                    if not util.IsNPC(itemID) and corpid:
                        uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                        tickerName = cfg.corptickernames.Get(corpid).tickerName
                        uicls.Label(text=mls.UI_INFOWND_MEMBEROFCORP % {'corpName': cfg.eveowners.Get(corpid).name,
                         'tickerName': tickerName}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=0, left=0, autowidth=False, autoheight=False)
                        uicls.Label(text=mls.UI_INFOWND_FORDAY % {'day': util.FmtTimeInterval(corpAge, 'day')}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOBOTTOM, left=4, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                        uthread.new(self.ShowRelationshipIcon, wnd, itemID, corpid, allianceid)
                    if not util.IsNPC(itemID) and allianceid:
                        uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, idx=0)
                        uicls.Label(text=cfg.eveowners.Get(allianceid).name, parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, top=4, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1, idx=1)
            elif wnd.sr.isShip and itemID or typeID and sm.GetService('godma').GetType(typeID).agentID:
                if itemID == eve.session.shipid:
                    otherCharID = eve.session.charid
                elif typeID and sm.GetService('godma').GetType(typeID).agentID:
                    otherCharID = sm.GetService('godma').GetType(typeID).agentID
                elif eve.session.solarsystemid is not None:
                    otherCharID = sm.GetService('michelle').GetCharIDFromShipID(itemID)
                else:
                    otherCharID = None
                if otherCharID:
                    btn = uix.GetBigButton(42, wnd.sr.subinfolinkcontainer, left=0, top=0, iconMargin=0)
                    btn.OnClick = (self._Info__PreFormatWnd,
                     wnd,
                     cfg.eveowners.Get(otherCharID).typeID,
                     otherCharID)
                    btn.hint = mls.UI_INFOWND_CLICKFORPILOTINFO
                    btn.sr.icon.LoadIconByTypeID(cfg.eveowners.Get(otherCharID).typeID, itemID=otherCharID, ignoreSize=True)
                    btn.sr.icon.SetAlign(uiconst.RELATIVE)
                    btn.sr.icon.SetSize(40, 40)
                    wnd.sr.subinfolinkcontainer.height = 42
            elif wnd.sr.abstractinfo is not None:
                if wnd.sr.isMedal or wnd.sr.isRibbon:
                    corpid = None
                    info = sm.GetService('medals').GetMedalDetails(itemID).info[0]
                    try:
                        corpid = info.ownerID
                    except:
                        sys.exc_clear()
                    if corpid:
                        uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOTOP, height=4)
                        self.GetCorpLogo(corpid, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                        wnd.sr.subinfolinkcontainer.height = 64
                        if corpid and not util.IsNPC(corpid):
                            uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                            tickerName = cfg.corptickernames.Get(corpid).tickerName
                            uicls.Label(text='%s %s [%s]' % (mls.UI_GENERIC_ISSUEDBY, cfg.eveowners.Get(corpid).name, tickerName), parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=0, left=0, autoheight=False, autowidth=False)
                        uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                        uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP)
                    uicls.Container(name='push', parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, height=4)
                    recipients = info.numberOfRecipients
                    txt = mls.UI_GENERIC_AWARDEDTIME % {'times': recipients}
                    uicls.Label(text=txt, parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                elif getattr(wnd.sr.abstractinfo, 'categoryID', None) == const.categoryBlueprint:
                    wnd.sr.isBlueprint = True
            elif wnd.sr.isCorporation:
                parallelCalls = []
                if wnd.sr.corpinfo is None:
                    parallelCalls.append((sm.RemoteSvc('corpmgr').GetPublicInfo, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                parallelCalls.append((sm.GetService('faction').GetFaction, (itemID,)))
                if wnd.sr.warfactioninfo is None:
                    parallelCalls.append((sm.GetService('facwar').GetCorporationWarFactionID, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                (corpinfo, factionID, warFaction,) = uthread.parallel(parallelCalls)
                wnd.sr.corpinfo = wnd.sr.corpinfo or corpinfo
                allianceid = wnd.sr.corpinfo.allianceID
                uthread.new(self.ShowRelationshipIcon, wnd, None, itemID, allianceid)
                uicls.Label(text='%s: %s' % (mls.UI_INFOWND_HEADQUARTERS, cfg.evelocations.Get(wnd.sr.corpinfo.stationID).name), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_DISABLED)
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
                memberDisp = None
                if factionID or warFaction:
                    faction = cfg.eveowners.Get(factionID) if factionID else cfg.eveowners.Get(warFaction)
                    logo = uiutil.GetLogoIcon(itemID=faction.ownerID, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, hint=mls.UI_INFOWND_CLICKFORFACTIONINFO, OnClick=(self._Info__PreFormatWnd,
                     wnd,
                     faction.typeID,
                     faction.ownerID), size=64, ignoreSize=True)
                    wnd.sr.subinfolinkcontainer.height = 64
                    memberDisp = cfg.eveowners.Get(faction.ownerID).name
                if allianceid:
                    alliance = cfg.eveowners.Get(allianceid)
                    logo = uiutil.GetLogoIcon(itemID=allianceid, align=uiconst.TOLEFT, parent=wnd.sr.subinfolinkcontainer, OnClick=(self._Info__PreFormatWnd,
                     wnd,
                     alliance.typeID,
                     allianceid), hint=mls.UI_INFOWND_CLICKFORALLIANCEINFO, state=uiconst.UI_NORMAL, size=64, ignoreSize=True)
                    wnd.sr.subinfolinkcontainer.height = 64
                    memberDisp = cfg.eveowners.Get(allianceid).name
                if memberDisp is not None:
                    uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                    uicls.Label(text=mls.UI_INFOWND_MEMBEROFALLIANCE % {'allianceName': memberDisp}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=4, left=0, autowidth=False, autoheight=False)
            elif wnd.sr.isAlliance:
                if wnd.sr.allianceinfo is None:
                    wnd.sr.allianceinfo = sm.GetService('alliance').GetAlliance(itemID)
                uthread.new(self.ShowRelationshipIcon, wnd, None, None, itemID)
            elif wnd.sr.isFaction:
                if wnd.sr.factioninfo is None:
                    wnd.sr.factioninfo = sm.GetService('faction').GetFactionEx(itemID)
                uicls.Label(text='%s: %s' % (mls.UI_INFOWND_HEADQUARTERS, cfg.evelocations.Get(wnd.sr.factioninfo.solarSystemID).name), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_DISABLED)
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
            invtype = cfg.invtypes.Get(typeID)
            if invtype.groupID == const.groupWormhole:
                desc2 = ''
                slimItem = sm.StartService('michelle').GetItem(itemID)
                if slimItem:
                    desc += '<br>'
                    desc += getattr(mls, 'UI_INFOWND_WORMHOLE_DESTDESC_%s' % slimItem.otherSolarSystemClass)
                    maxStableMass = slimItem.maxStableMAss
                    if slimItem.wormholeAge >= 3:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE4 + '<br>'
                    elif slimItem.wormholeAge >= 2:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE3 + '<br>'
                    elif slimItem.wormholeAge >= 1:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE2 + '<br>'
                    elif slimItem.wormholeAge >= 0:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE1 + '<br>'
                    desc2 += '<br>'
                    if slimItem.wormholeSize < 0.5:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS3 + '<br>'
                    elif slimItem.wormholeSize < 1:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS2 + '<br>'
                    else:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS1 + '<br>'
                    if desc2:
                        desc += '<br><br><hr><br>' + desc2
            wnd.HideGoBack()
            wnd.HideGoForward()
            if not headerOnly:
                self.GetWndData(wnd, typeID, itemID, parentID=parentID)
                historyIdx = None
                if historyData is None:
                    if wnd.sr.historyIdx is not None:
                        wnd.sr.history = wnd.sr.history[:(wnd.sr.historyIdx + 1)]
                    history = (typeID,
                     itemID,
                     parentID,
                     len(wnd.sr.history),
                     rec,
                     abstractinfo)
                    wnd.sr.history.append(history)
                    wnd.sr.historyIdx = None
                else:
                    (_typeID, _itemID, _parentID, historyIdx, _rec, _abstractinfo,) = historyData
                    wnd.sr.historyIdx = historyIdx
                if len(wnd.sr.history) > 1:
                    if historyIdx != 0:
                        if historyIdx:
                            wnd.GoBack = (self.Browse, wnd.sr.history[(historyIdx - 1)], wnd)
                        else:
                            wnd.GoBack = (self.Browse, wnd.sr.history[-2], wnd)
                        wnd.ShowGoBack()
                    if historyIdx is not None and historyIdx != len(wnd.sr.history) - 1:
                        wnd.GoForward = (self.Browse, wnd.sr.history[(historyIdx + 1)], wnd)
                        wnd.ShowGoForward()
            else:
                desc = ''
                bio = None
            if wnd is None or wnd.destroyed:
                return 
            tabgroup = []
            i = 0
            for (listtype, subtabs,) in wnd.sr.infotabs:
                items = wnd.sr.data[listtype]['items']
                tabname = wnd.sr.data[listtype]['name']
                if subtabs:
                    subtabgroup = []
                    for (sublisttype, subsubtabs,) in subtabs:
                        subitems = wnd.sr.data[sublisttype]['items']
                        subtabname = wnd.sr.data[sublisttype]['name']
                        if len(subitems):
                            subtabgroup.append([subtabname,
                             wnd.sr.scroll,
                             self,
                             (wnd, sublisttype, None)])

                    if subtabgroup:
                        _subtabs = uicls.TabGroup(name='%s_subtabs' % tabname.lower(), parent=wnd.sr.subcontainer, idx=0, tabs=subtabgroup, groupID='infowindow_%s' % sublisttype, autoselecttab=0)
                        tabgroup.append([tabname,
                         wnd.sr.scroll,
                         self,
                         (wnd,
                          'selectSubtab',
                          None,
                          _subtabs),
                         _subtabs])
                elif len(items):
                    tabgroup.append([tabname,
                     wnd.sr.scroll,
                     self,
                     (wnd, listtype, None)])

            for (listtype, funcName,) in wnd.sr.dynamicTabs:
                if listtype == mls.UI_GENERIC_NOTES:
                    tabgroup.append([listtype,
                     wnd.sr.notesedit,
                     self,
                     (wnd, listtype, funcName)])
                else:
                    tabgroup.append([listtype,
                     wnd.sr.scroll,
                     self,
                     (wnd, listtype, funcName)])

            widthRequirements = [MINWIDTH]
            if not headerOnly and wnd.sr.data['buttons']:
                btns = uicls.ButtonGroup(btns=wnd.sr.data['buttons'], parent=wnd.sr.subcontainer, idx=0, unisize=0)
                totalBtnWidth = 0
                for btn in btns.children[0].children:
                    totalBtnWidth += btn.width

                widthRequirements.append(totalBtnWidth)
            if desc:
                tabgroup.insert(0, [mls.UI_GENERIC_DESCRIPTION,
                 wnd.sr.descedit,
                 self,
                 (wnd,
                  'readOnlyText',
                  None,
                  desc)])
            if not util.IsNPC(itemID) and bio:
                tabgroup.insert(0, [mls.UI_GENERIC_BIO,
                 wnd.sr.descedit,
                 self,
                 (wnd,
                  'readOnlyText',
                  None,
                  bio)])
            if len(tabgroup):
                wnd.sr.maintabs = uicls.TabGroup(name='maintabs', parent=wnd.sr.subcontainer, idx=0, tabs=tabgroup, groupID='infowindow')
                widthRequirements.append(wnd.sr.maintabs.totalTabWidth + 16)
            if len(widthRequirements) > 1:
                height = MINHEIGHTREGULAR
                if typeID == const.typeMedal:
                    height = MINHEIGHTMEDAL
                wnd.SetMinSize([max(widthRequirements), height])
            self.lastActive = wnd
            self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
            self.RecalcTheRestContainer(wnd, wnd.sr.therestcontainer)
            wnd.sr.toparea.state = uiconst.UI_PICKCHILDREN
            if headerOnly:
                wnd.height = wnd.sr.toparea.parent.height
            wnd.HideLoad()
            wnd.ShowHeaderButtons(1)
            wnd.IsBusy = 0
            self.loading = 0
        except BadArgs as e:
            if not wnd.destroyed:
                wnd.HideLoad()
                wnd.ShowHeaderButtons(1)
                wnd.IsBusy = 0
                self.loading = 0
                self.ShowError(wnd, e.args)
            sys.exc_clear()
        except:
            if not wnd.destroyed:
                wnd.HideLoad()
                wnd.ShowHeaderButtons(1)
                wnd.IsBusy = 0
                self.loading = 0
                raise 
            sys.exc_clear()



    def GetMain(self, wnd):
        return wnd.sr.main



    def GetTop(self, wnd):
        return wnd.sr.topParent



    def ShowError(self, wnd, args):
        self.GetTop(wnd).state = uiconst.UI_HIDDEN
        errorPar = uicls.Container(parent=self.GetMain(wnd), name='errorPar', align=uiconst.TOALL, left=12, top=6, width=12, height=6, state=uiconst.UI_DISABLED)
        msg = cfg.GetMessage(*args)
        title = uicls.CaptionLabel(text=msg.title, parent=errorPar, align=uiconst.TOTOP)
        title.name = 'errorTitle'
        uicls.Container(parent=errorPar, name='separator', align=uiconst.TOTOP, height=6)
        details = uicls.Label(text=msg.text, name='errorDetails', parent=errorPar, align=uiconst.TOTOP, autowidth=False)



    def HideError(self, wnd):
        self.GetTop(wnd).state = uiconst.UI_PICKCHILDREN
        errorPar = uiutil.FindChild(self.GetMain(wnd), 'errorPar')
        if errorPar is not None:
            errorPar.Close()



    def GetWindowSettings(self, wnd, typeID, itemID):
        invtype = cfg.invtypes.Get(typeID)
        invgroup = invtype.Group()
        wnd.sr.isBookmark = invtype.id == const.typeBookmark
        wnd.sr.isVoucher = invtype.groupID == const.groupVoucher
        wnd.sr.isCharacter = invtype.groupID == const.groupCharacter
        wnd.sr.isStargate = invtype.groupID == const.groupStargate
        wnd.sr.isControlTower = invtype.groupID == const.groupControlTower
        wnd.sr.isConstructionPF = invtype.groupID in (const.groupStationUpgradePlatform, const.groupStationImprovementPlatform, const.groupConstructionPlatform)
        wnd.sr.isCorporation = invtype.groupID == const.groupCorporation
        wnd.sr.isAlliance = invtype.groupID == const.groupAlliance
        wnd.sr.isFaction = invtype.groupID == const.groupFaction
        wnd.sr.isOwned = invtype.groupID in (const.groupWreck,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupCargoContainer,
         const.groupFreightContainer,
         const.groupSentryGun,
         const.groupDestructibleSentryGun,
         const.groupMobileSentryGun,
         const.groupDeadspaceOverseersSentry) or invtype.categoryID in [const.categoryStructure, const.categorySovereigntyStructure, const.categoryOrbital]
        wnd.sr.isShip = invgroup.categoryID == const.categoryShip
        wnd.sr.isStation = invgroup.categoryID == const.categoryStation and invtype.groupID != const.groupStationServices
        wnd.sr.isModule = invgroup.categoryID in (const.categoryModule, const.categorySubSystem)
        wnd.sr.isStructure = invgroup.categoryID in (const.categoryStructure,
         const.categoryDeployable,
         const.categorySovereigntyStructure,
         const.categoryOrbital)
        wnd.sr.isCharge = invgroup.categoryID == const.categoryCharge
        wnd.sr.isBlueprint = invgroup.categoryID in (const.categoryBlueprint, const.categoryAncientRelic)
        wnd.sr.isReaction = invgroup.categoryID == const.categoryReaction
        wnd.sr.isDrone = invgroup.categoryID == const.categoryDrone
        wnd.sr.isCelestial = invgroup.categoryID in (const.categoryCelestial, const.categoryAsteroid) and invtype.groupID not in (const.groupWreck,
         const.groupCargoContainer,
         const.groupFreightContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer) or invtype.groupID in (const.groupLargeCollidableStructure, const.groupDeadspaceOverseersStructure, const.groupHarvestableCloud)
        wnd.sr.isGenericItem = invgroup.categoryID in (const.categoryImplant,
         const.categorySkill,
         const.categoryAccessories,
         const.categoryPlanetaryCommodities,
         const.categoryPlanetaryResources)
        wnd.sr.isGenericObject = invgroup.categoryID in (const.categoryEntity, const.categoryDrone)
        wnd.sr.isAnchorable = invgroup.categoryID in (const.categoryStructure, const.categoryDeployable, const.categoryOrbital) or invgroup.groupID in (const.groupSecureCargoContainer, const.groupAuditLogSecureContainer)
        wnd.sr.isPin = invgroup.categoryID in (const.categoryPlanetaryInteraction,) and invgroup.groupID not in (const.groupPlanetaryLinks, const.groupPlanetaryCustomsOffices)
        wnd.sr.isPinLink = invgroup.groupID == const.groupPlanetaryLinks
        wnd.sr.isCargoLink = invgroup.groupID == const.groupPlanetaryCustomsOffices
        wnd.sr.isPICommodity = invtype.id in cfg.schematicsByType
        wnd.sr.isApparel = invgroup.categoryID == const.categoryApparel
        wnd.sr.isStructureUpgrade = invgroup.categoryID == const.categoryStructureUpgrade
        wnd.sr.isRank = invtype.id == const.typeRank
        wnd.sr.isMedal = invtype.id == const.typeMedal
        wnd.sr.isRibbon = invtype.id == const.typeRibbon
        wnd.sr.isCertificate = invtype.id == const.typeCertificate
        wnd.sr.isSchematic = invtype.id == const.typeSchematic
        wnd.sr.isAbstract = invgroup.categoryID == const.categoryAbstract
        if wnd.sr.isVoucher:
            wnd.sr.voucherinfo = sm.GetService('voucherCache').GetVoucher(itemID)
        if wnd.sr.isBookmark:
            wnd.SetCaption('%s: %s' % (invtype.name, mls.UI_GENERIC_INFORMATION))
        elif typeID == const.typeMapLandmark:
            wnd.SetCaption(mls.UI_INFOWND_LANDMARKINFO)
        elif typeID == const.typeSchematic:
            wnd.SetCaption('%s: %s' % (mls.UI_PI_SCHEMATIC, mls.UI_GENERIC_INFORMATION))
        else:
            wnd.SetCaption('%s: %s' % (invtype.Group().name, mls.UI_GENERIC_INFORMATION))
        height = MINHEIGHTREGULAR
        if typeID == const.typeMedal:
            height = MINHEIGHTMEDAL
        wnd.SetMinSize([MINWIDTH, height])



    def ShowRelationshipIcon(self, wnd, itemID, corpid, allianceid):
        ret = sm.GetService('addressbook').GetRelationship(itemID, corpid, allianceid)
        relationships = [ret.persToCorp,
         ret.persToPers,
         ret.persToAlliance,
         ret.corpToPers,
         ret.corpToCorp,
         ret.corpToAlliance,
         ret.allianceToPers,
         ret.allianceToCorp,
         ret.allianceToAlliance]
        relationship = 0.0
        for r in relationships:
            if r != 0.0 and r > relationship or relationship == 0.0:
                relationship = r

        flag = None
        iconNum = 0
        if relationship > const.contactGoodStanding:
            flag = state.flagStandingHigh
            iconNum = 3
        elif relationship > const.contactNeutralStanding and relationship <= const.contactGoodStanding:
            flag = state.flagStandingGood
            iconNum = 3
        elif relationship < const.contactNeutralStanding and relationship >= const.contactBadStanding:
            flag = state.flagStandingBad
            iconNum = 4
        elif relationship < const.contactBadStanding:
            flag = state.flagStandingHorrible
            iconNum = 4
        if flag:
            if itemID:
                w = h = 14
                t = l = 110
                iconw = iconh = 15
            else:
                w = h = 12
                t = l = 50
                iconw = iconh = 13
            col = sm.GetService('state').GetStateColor(flag)
            icon = uicls.Container(parent=wnd.sr.mainicon, pos=(0, 0, 10, 10), name='flag', state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT, idx=0)
            uicls.Sprite(parent=icon, pos=(0, 0, 10, 10), name='icon', state=uiconst.UI_DISABLED, rectWidth=10, rectHeight=10, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png', align=uiconst.RELATIVE)
            uicls.Fill(parent=icon)
            icon.width = w
            icon.height = h
            icon.top = t
            icon.left = l
            icon.children[1].color.SetRGB(*col)
            icon.children[0].rectLeft = iconNum * 10
            icon.children[0].width = iconw
            icon.children[0].height = iconh
            i = 0.0
            while i < 0.6:
                icon.children[1].color.a = i
                i += 0.05
                blue.pyos.synchro.Sleep(30)




    def OnPreviewClick(self, wnd, *args):
        sm.GetService('preview').PreviewType(getattr(wnd, 'typeID'))



    def GetNameAndDescription(self, wnd, typeID, itemID):
        if wnd is None or wnd.destroyed:
            return (None, None)
        if typeID == const.typeMapLandmark:
            landmark = sm.GetService('map').GetLandmark(itemID * -1)
            capt = Tr(landmark.landmarkName, 'dbo.mapLandmarks.landmarkName', -itemID)
            desc = Tr(landmark.description, 'dbo.mapLandmarks.description', -itemID)
            label = ''
            wnd.sr.isCelestial = 0
        else:
            capt = None
            invtype = cfg.invtypes.Get(typeID)
            if itemID in cfg.evelocations.data:
                capt = cfg.evelocations.Get(itemID).name
            if not capt:
                capt = invtype.name
            desc = invtype.description
            label = ''
        if wnd.sr.isAbstract:
            if wnd.sr.abstractinfo is not None:
                if wnd.sr.isRank:
                    try:
                        (rankLabel, rankDescription,) = uix.GetRankLabel(wnd.sr.abstractinfo.warFactionID, wnd.sr.abstractinfo.currentRank)
                        desc = rankDescription
                        label = rankLabel
                    except:
                        sys.exc_clear()
                if wnd.sr.isMedal or wnd.sr.isRibbon:
                    try:
                        info = sm.GetService('medals').GetMedalDetails(itemID).info[0]
                        recipients = info.numberOfRecipients
                        desc = info.description
                        label = info.title
                    except:
                        sys.exc_clear()
                if wnd.sr.isCertificate:
                    try:
                        (className, grade, desc,) = uix.GetCertificateLabel(wnd.sr.abstractinfo.certificateID)
                        label = '%s - %s' % (className, grade)
                    except:
                        sys.exc_clear()
                if wnd.sr.isSchematic:
                    try:
                        label = wnd.sr.abstractinfo.schematicName
                        desc = ''
                    except:
                        sys.exc_clear()
        elif wnd.sr.isBookmark and itemID is not None:
            capt = 'Bookmark'
            if wnd.sr.voucherinfo:
                try:
                    (label, desc,) = sm.GetService('addressbook').UnzipMemo(wnd.sr.voucherinfo.GetDescription())
                except:
                    desc = wnd.sr.voucherinfo.GetDescription()
                    sys.exc_clear()
        elif wnd.sr.isCharacter and itemID is not None:
            if sm.GetService('agents').IsAgent(itemID):
                capt = desc = sm.GetService('agents').GetAgentDisplayName(itemID)
            else:
                capt = cfg.eveowners.Get(itemID).name
                desc = cfg.eveowners.Get(itemID).description
            if desc == capt:
                bloodline = self.GetBloodlineByTypeID(cfg.eveowners.Get(itemID).typeID)
                desc = Tr(bloodline.description, 'character.bloodlines.description', bloodline.dataID)
        elif wnd.sr.isCorporation and itemID is not None:
            if wnd.sr.corpinfo is None:
                wnd.sr.corpinfo = sm.RemoteSvc('corpmgr').GetPublicInfo(itemID)
            if wnd.sr.corpinfo.corporationID < 1100000:
                desc = Tr(wnd.sr.corpinfo.description, 'dbo.invItemDescriptions.description', wnd.sr.corpinfo.corporationID)
            else:
                desc = wnd.sr.corpinfo.description
            if uiutil.CheckCorpID(itemID):
                capt = ''
            else:
                capt = cfg.eveowners.Get(itemID).name
                if wnd.sr.corpinfo.deleted:
                    capt = '[' + mls.UI_GENERIC_CLOSED + '] ' + capt
        elif wnd.sr.isAlliance and itemID is not None:
            if wnd.sr.allianceinfo is None:
                wnd.sr.allianceinfo = sm.GetService('alliance').GetAlliance(itemID)
            capt = cfg.eveowners.Get(itemID).name
            desc = wnd.sr.allianceinfo.description
            if wnd.sr.allianceinfo.deleted:
                capt = '[' + mls.UI_GENERIC_CLOSED + '] ' + capt
        elif wnd.sr.isStation:
            if itemID is not None:
                if wnd.sr.stationinfo is None:
                    wnd.sr.stationinfo = sm.RemoteSvc('stationSvc').GetStation(itemID)
                capt = wnd.sr.stationinfo.stationName
                if itemID < 61000000 and wnd.sr.stationinfo.stationTypeID not in (12294, 12295, 12242):
                    desc = Tr(wnd.sr.stationinfo.description, 'dbo.staOperations.description', wnd.sr.stationinfo.operationID)
                else:
                    desc = wnd.sr.stationinfo.description
            else:
                desc = cfg.invtypes.Get(typeID).description or cfg.invtypes.Get(typeID).name
        elif wnd.sr.isCelestial or wnd.sr.isStargate:
            desc = ''
            if invtype.groupID in (const.groupSolarSystem, const.groupConstellation, const.groupRegion):
                label = invtype.name
                label += '<br><br>%s' % self.GetLocationTrace(itemID, [])
                mapdesc = cfg.mapcelestialdescriptions.GetIfExists(itemID)
                if mapdesc:
                    desc = '%s<br>' % mapdesc.description
            if not desc:
                desc = '%s<br>' % (invtype.description or invtype.name)
            capt = invtype.name
            if invtype.groupID == const.groupBeacon:
                beacon = sm.GetService('michelle').GetItem(itemID)
                if beacon and hasattr(beacon, 'dunDescription') and beacon.dunDescription:
                    desc = beacon.dunDescription
            locationname = None
            if invtype.categoryID == const.categoryAsteroid or invtype.groupID == const.groupHarvestableCloud:
                locationname = invtype.name
            elif itemID is not None:
                try:
                    locationname = cfg.evelocations.Get(itemID).name
                except KeyError:
                    locationname = invtype.name
                    sys.exc_clear()
            if locationname and locationname[0] != '@':
                capt = locationname
        elif wnd.sr.isFaction:
            capt = ''
            if wnd.sr.factioninfo is None:
                wnd.sr.factioninfo = sm.GetService('faction').GetFactionEx(itemID)
            desc = Tr(wnd.sr.factioninfo.description, 'character.factions.description', wnd.sr.factioninfo.dataID)
        actionMenu = self.GetActionMenu(itemID, typeID, wnd.sr.rec, wnd)
        infoicon = wnd.sr.headerIcon
        if actionMenu:
            wnd.SetHeaderIcon()
            infoicon = wnd.sr.headerIcon
            infoicon.state = uiconst.UI_NORMAL
            infoicon.expandOnLeft = 1
            infoicon.GetMenu = lambda *args: self.GetIconActionMenu(itemID, typeID, wnd.sr.rec, wnd)
            infoicon.hint = mls.UI_GENERIC_ACTIONS
            wnd.sr.presetMenu = infoicon
            infoicon.state = uiconst.UI_NORMAL
        elif infoicon:
            infoicon.state = uiconst.UI_HIDDEN
        left = wnd.sr.mainicon.left + wnd.sr.mainicon.width + const.defaultPadding
        if capt:
            wnd.sr.captionText = uicls.Label(text=uiutil.UpperCase(capt), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, letterspace=2, state=uiconst.UI_DISABLED)
            wnd.sr.captioncontainer.height = 30
            if label:
                uicls.Label(text=label, parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, tabs=[84], state=uiconst.UI_DISABLED)
        desc = desc or ''
        for each in ('<b>', '</b>', '\r'):
            desc = desc.replace(each, '')

        desc = desc.replace('\n', '<br>')
        return desc



    def GetIconActionMenu(self, itemID, typeID, rec, wnd):
        return self.GetActionMenu(itemID, typeID, rec, wnd)



    def RecalcCaptionContainer(self, wnd, subwnd, *args):
        uix.RefreshHeight(subwnd)
        wnd.sr.toparea.parent.height = wnd.sr.therestpush.height + wnd.sr.captionpush.height + wnd.sr.captioncontainer.height + wnd.sr.subinfolinkcontainer.height + wnd.sr.therestcontainer.height
        wnd.sr.toparea.parent.height = max(wnd.sr.toparea.parent.height, wnd.sr.mainiconparent.width, wnd.sr.mainiconparent.height) + const.defaultPadding * 2


    RecalcTheRestContainer = RecalcCaptionContainer

    def GetLocationTrace(self, itemID, trace, recursive = 0):
        parentID = sm.GetService('map').GetParent(itemID)
        if parentID != const.locationUniverse:
            parentItem = sm.GetService('map').GetItem(parentID)
            if parentItem:
                trace += self.GetLocationTrace(parentID, ['%s<t>&gt; %s' % (cfg.invtypes.Get(parentItem.typeID).name, parentItem.itemName)], 1)
        if recursive:
            return trace
        else:
            trace.reverse()
            item = sm.GetService('map').GetItem(itemID)
            if item and cfg.invtypes.Get(item.typeID).groupID == const.groupSolarSystem and item.security is not None:
                sec = sm.GetService('map').GetSecurityStatus(itemID)
                trace += ['%s<t>&gt; %.1f' % (mls.UI_INFOWND_SECURITYLEVEL, util.FmtSystemSecStatus(sec))]
            return '<br>'.join(trace)



    def GetIcon(self, wnd, typeID, itemID):
        geticon = 1
        invtype = cfg.invtypes.Get(typeID)
        iWidth = iHeight = 64
        rendersize = 128
        uix.Flush(wnd.sr.mainicon)
        wnd.sr.techicon.state = uiconst.UI_HIDDEN
        if (wnd.sr.isShip or wnd.sr.isStation or wnd.sr.isStargate or wnd.sr.isGenericObject or wnd.sr.isCelestial or wnd.sr.isOwned or wnd.sr.isRank) and invtype.groupID not in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupHarvestableCloud) and invtype.categoryID != const.categoryAsteroid:
            iWidth = iHeight = 128
            if invtype.groupID not in (const.groupRegion, const.groupConstellation, const.groupSolarSystem):
                rendersize = 256
        hasAbstractIcon = False
        if wnd.sr.isAbstract and wnd.sr.abstractinfo is not None:
            if wnd.sr.isRank:
                rank = xtriui.Rank(name='rankicon', align=uiconst.TOPLEFT, left=3, top=2, width=iWidth, height=iHeight, parent=wnd.sr.mainicon)
                rank.Startup(wnd.sr.abstractinfo.warFactionID, wnd.sr.abstractinfo.currentRank)
                hasAbstractIcon = True
            if wnd.sr.isMedal or wnd.sr.isRibbon:
                rendersize = 256
                (iWidth, iHeight,) = (128, 256)
                medal = xtriui.MedalRibbon(name='medalicon', align=uiconst.TOPLEFT, left=3, top=2, width=iWidth, height=iHeight, parent=wnd.sr.mainicon)
                medal.Startup(wnd.sr.abstractinfo, rendersize)
                hasAbstractIcon = True
            if wnd.sr.isCertificate:
                mapped = 'ui_79_64_%s' % (int(wnd.sr.abstractinfo.grade) + 1)
                sprite = uicls.Icon(parent=wnd.sr.mainicon, icon=mapped, align=uiconst.TOALL)
            if wnd.sr.isSchematic:
                sprite = uicls.Icon(parent=wnd.sr.mainicon, icon='ui_27_64_3', align=uiconst.TOALL)
                hasAbstractIcon = True
        if wnd.sr.isCharacter:
            sprite = uicls.Sprite(parent=wnd.sr.mainicon, align=uiconst.TOALL)
            sm.GetService('photo').GetPortrait(itemID, 256, sprite)
            iWidth = iHeight = 128
            sprite.cursor = uiconst.UICURSOR_MAGNIFIER
            sprite.OnClick = (self.OpenPortraitWnd, itemID)
        elif wnd.sr.isCorporation or wnd.sr.isFaction or wnd.sr.isAlliance:
            if wnd.sr.isCorporation:
                try:
                    cfg.eveowners.Get(itemID)
                except:
                    log.LogWarn('Tried to show info on bad corpID:', itemID)
                    raise BadArgs('InfoNoCorpWithID')
            uiutil.GetLogoIcon(itemID=itemID, parent=wnd.sr.mainicon, name='corplogo', acceptNone=False, align=uiconst.TOALL)
        elif typeID == const.typeMapLandmark:
            landmark = sm.GetService('map').GetLandmark(itemID * -1)
            if landmark.iconID:
                sprite = uicls.Sprite(parent=wnd.sr.mainicon, align=uiconst.TOALL)
                sprite.texture.resPath = util.IconFile(landmark.iconID)
                sprite.rectLeft = 64
                sprite.rectWidth = 128
                iWidth = iHeight = 128
        elif invtype.categoryID == const.categoryBlueprint and (itemID and itemID < const.minFakeItem or wnd.sr.abstractinfo is not None):
            if itemID and itemID < const.minFakeItem:
                wnd.sr.blueprintInfo = sm.RemoteSvc('factory').GetBlueprintAttributes(itemID)
                isCopy = wnd.sr.blueprintInfo.get('copy', False)
            elif wnd.sr.abstractinfo is not None:
                isCopy = wnd.sr.abstractinfo.isCopy
            icon = uicls.Icon(parent=wnd.sr.mainicon, align=uiconst.TOALL, size=rendersize, typeID=typeID, itemID=itemID, ignoreSize=True, isCopy=isCopy)
        elif not hasAbstractIcon:
            techSprite = uix.GetTechLevelIcon(wnd.sr.techicon, 0, typeID)
            icon = uicls.Icon(parent=wnd.sr.mainicon, align=uiconst.TOALL, size=rendersize, typeID=typeID, itemID=itemID, ignoreSize=True)
            if util.IsPreviewable(typeID):
                setattr(icon, 'typeID', typeID)
                icon.cursor = uiconst.UICURSOR_MAGNIFIER
                icon.OnClick = (self.OnPreviewClick, icon)
        wnd.sr.mainiconparent.width = wnd.sr.mainicon.width = iWidth
        wnd.sr.mainiconparent.height = wnd.sr.mainicon.height = iHeight



    def OpenPortraitWnd(self, charID, *args):
        wnd = sm.StartService('window').GetWindow('PortraitWindow')
        if wnd is None:
            wnd = sm.StartService('window').GetWindow('PortraitWindow', 1, decoClass=form.PortraitWindow, charID=charID)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            wnd.Load(charID)



    def GetActionMenu(self, itemID, typeID, invItem, wnd):
        m = []
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(itemID, typeID, filterFunc=[mls.UI_CMD_SHOWINFO], invItem=invItem)
        if wnd.sr.isCharacter or wnd.sr.isCorporation:
            if not util.IsNPC(itemID):
                m.append((mls.UI_CMD_SHOWCONTRACTS, self.ShowContracts, (itemID,)))
        if wnd.sr.isCharacter and not util.IsNPC(itemID):
            m.append((mls.UI_CMD_REPORTBOT, self.ReportBot, (itemID,)))
        return m



    def Wanted(self, wnd, bounty, *args):
        pic = uicls.Sprite(name='wanted', parent=wnd.sr.mainicon, idx=0, color=(1.0, 0.0, 0.0, 1.0), texturePath='res:/UI/Texture/wanted.png', width=96, height=48, left=10 + random.randint(1, 10), top=80 + random.randint(1, 10), hint=mls.UI_INFOWND_BOUNTYNOTE % {'bounty': util.FmtISK(bounty)})
        uicls.Label(text='%s: %s' % (mls.UI_GENERIC_BOUNTY, util.FmtISK(bounty)), parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1, state=uiconst.UI_NORMAL)



    def Browse(self, settings, wnd, *args):
        if getattr(self, 'browsing', 0):
            return 
        self.browsing = 1
        (typeID, itemID, parentID, historyIdx, rec, abstractinfo,) = settings
        self.FormatWnd(wnd, typeID, itemID, rec, parentID, settings, abstractinfo=abstractinfo)
        self.browsing = 0



    def LoadDecorations(self, wnd):
        if not wnd.sr.data[mls.UI_GENERIC_DECORATIONS]['inited']:
            itemID = wnd.sr.itemID
            rank = sm.StartService('facwar').GetCharacterRankInfo(itemID, wnd.sr.corpID)
            self.GetRankEntry(wnd, rank)
            certs = sm.StartService('certificates').GetCertificatesByCharacter(itemID)
            self.GetPublicCerts(wnd, certs)
            medals = sm.StartService('certificates').GetCertificatesByCharacter(itemID)
            self.GetPublicMedals(wnd, itemID)
            subtabs = self.GetSubTabs(mls.UI_GENERIC_DECORATIONS, wnd.sr.infotabs)
            subtabgroup = []
            for (sublisttype, subsubtabs,) in subtabs:
                subitems = wnd.sr.data[sublisttype]['items']
                subtabname = wnd.sr.data[sublisttype]['name']
                if len(subitems):
                    subtabgroup.append([subtabname,
                     wnd.sr.scroll,
                     self,
                     (wnd, sublisttype, None)])

            if len(subtabgroup) > 0 and wnd.sr.maintabs:
                _subtabs = uicls.TabGroup(name='decorations_subtabs', parent=wnd.sr.subcontainer, idx=1, tabs=subtabgroup, groupID='infowindow_%s' % sublisttype)
                wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_GENERIC_DECORATIONS, None).sr.panelparent = _subtabs
                wnd.sr.data[mls.UI_GENERIC_DECORATIONS]['inited'] = 1
                wnd.sr.decorations_subtabs = _subtabs
                wnd.sr.data[mls.UI_GENERIC_DECORATIONS]['inited'] = 1
                return 
            wnd.sr.decorations_subtabs = None
        if getattr(wnd.sr, 'decorations_subtabs', None) is not None:
            wnd.sr.decorations_subtabs.AutoSelect()
        else:
            wnd.sr.scroll.Load(contentList=[])
            wnd.sr.scroll.ShowHint(mls.UI_INFOWND_NOPUBLICDECORATIONS)



    def GetRankEntry(self, wnd, rank, hilite = False):
        facwarcurrrank = getattr(rank, 'currentRank', 1)
        facwarhighrank = getattr(rank, 'highestRank', 1)
        facwarfaction = getattr(rank, 'factionID', None)
        if rank and facwarfaction is not None:
            fac = sm.GetService('faction').GetFactionEx(facwarfaction)
            (lbl, desc,) = uix.GetRankLabel(facwarfaction, facwarcurrrank)
            if hilite:
                lbl = '%s (%s)' % (lbl, mls.UI_GENERIC_CURRENT)
            entry = listentry.Get('RankEntry', {'label': fac.factionName,
             'text': lbl,
             'rank': facwarcurrrank,
             'warFactionID': facwarfaction,
             'selected': False,
             'typeID': const.typeRank,
             'showinfo': 1,
             'line': 1})
            if wnd is None:
                return entry
            return wnd.sr.data[mls.UI_GENERIC_RANKS]['items'].append(entry)



    def GetMedalEntry(self, wnd, info, details, *args):
        d = details
        lenStr = ''
        if type(info) == list:
            m = info[0]
            lenStr = len(info)
        else:
            m = info
        sublevel = 1
        if args:
            sublevel = args[0]
        medalribbondata = uix.FormatMedalData(d)
        medalid = m.medalID
        title = m.title
        if lenStr:
            title += ' - %s' % mls.UI_GENERIC_AWARDEDTIME % {'times': lenStr}
        description = m.description
        createdate = m.date
        data = {'label': title,
         'text': description,
         'sublevel': sublevel,
         'id': m.medalID,
         'line': 1,
         'abstractinfo': medalribbondata,
         'typeID': const.typeMedal,
         'itemID': m.medalID,
         'icon': 'ui_51_64_4',
         'showinfo': True,
         'sort_%s' % mls.UI_GENERIC_TITLE: '_%s' % title.lower(),
         'iconsize': 26}
        entry = listentry.Get('MedalRibbonEntry', data)
        if wnd is None:
            return entry
        return wnd.sr.data[mls.UI_GENERIC_RANKS]['items'].append(entry)



    def GetPublicCerts(self, wnd, certs):
        if not wnd:
            return 
        entryList = []
        allCertInfo = {}
        for cert in certs:
            allCertInfo[cert.certificateID] = cfg.certificates.Get(cert.certificateID)

        groupList = self.GetCertGroupList(allCertInfo)
        wnd.sr.data[mls.UI_SHARED_CERTIFICATES2]['items'].extend(groupList)



    def GetPublicMedals(self, wnd, charID):
        if not wnd:
            return 
        scrolllist = sm.StartService('charactersheet').GetMedalScroll(charID, True, True)
        wnd.sr.data[mls.UI_GENERIC_MEDALS]['items'].extend(scrolllist)



    def EditContact(self, wnd, itemID, edit):
        self.SaveNote(wnd, 1)
        addressBookSvc = sm.GetService('addressbook')
        addressBookSvc.AddToPersonalMulti(itemID, 'contact', edit)



    def GetWndData(self, wnd, typeID, itemID, parentID = None):
        moonOrPlanet = 0
        title = None
        invtype = cfg.invtypes.Get(typeID)
        invgroup = invtype.Group()
        noShowCatergories = (const.categoryEntity, const.categoryStation)
        noShowGroups = (const.groupMoon,
         const.groupPlanet,
         const.groupConstellation,
         const.groupSolarSystem,
         const.groupRegion,
         const.groupLargeCollidableObject)
        noShowTypes = ()
        showAttrs = invtype.id not in noShowTypes and invgroup.Category().id not in noShowCatergories and invgroup.id not in noShowGroups
        if invgroup.categoryID == const.categoryEntity:
            tmp = [ each for each in sm.GetService('godma').GetType(typeID).displayAttributes if each.attributeID == const.attributeEntityKillBounty ]
            if tmp:
                self.Wanted(wnd, tmp[0].value)
        if itemID is not None and itemID < 0:
            pass
        if wnd.sr.isCharacter or wnd.sr.isCorporation:
            showAttrs = 0
            if not util.IsNPC(itemID):
                if eve.session.charid != itemID:
                    addressBookSvc = sm.GetService('addressbook')
                    if not addressBookSvc.IsInAddressBook(itemID, 'contact'):
                        wnd.sr.data['buttons'] += [(mls.UI_CONTACTS_ADDTOCONTACTS,
                          self.EditContact,
                          (wnd, itemID, False),
                          81)]
                    else:
                        wnd.sr.data['buttons'] += [(mls.UI_CONTACTS_EDITCONTACT,
                          self.EditContact,
                          (wnd, itemID, True),
                          81)]
                if wnd.sr.isCorporation:
                    wnd.sr.dynamicTabs.append((mls.UI_GENERIC_ALLIANCEHIST, 'AllianceHistory'))
                if wnd.sr.isCharacter:
                    wnd.sr.dynamicTabs.append((mls.UI_GENERIC_EMPLOYMENTHIST, 'EmploymentHistory'))
                    wnd.sr.dynamicTabs.append((mls.UI_GENERIC_DECORATIONS, 'Decorations'))
        if wnd.sr.isShip:
            try:
                shipinfo = sm.GetService('godma').GetItem(itemID)
            except:
                shipinfo = None
                sys.exc_clear()
            info = shipinfo or sm.GetService('godma').GetStateManager().GetShipType(typeID)
            attrDict = self.GetAttrDict(typeID)
            for (caption, attrs,) in self.GetShipAttributes():
                shipAttr = [ each for each in attrs if each in attrDict ]
                if shipAttr:
                    wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Header', {'label': caption}))
                    bd = self.GetBarData(itemID, info, caption)
                    if bd:
                        wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('StatusBar', bd))
                    self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], attrList=shipAttr)

            baseWarpSpeed = self.GetBaseWarpSpeed(typeID, shipinfo)
            if baseWarpSpeed:
                bwsAttr = cfg.dgmattribs.Get(const.attributeBaseWarpSpeed)
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': bwsAttr.displayName,
                 'text': baseWarpSpeed,
                 'iconID': bwsAttr.iconID}))
            GAV = self.GetGAVFunc(itemID, info)
            for (label, loadAttributeID, outputAttributeID,) in ((mls.UI_GENERIC_CPU, const.attributeCpuLoad, const.attributeCpuOutput), (mls.UI_GENERIC_POWERGRID, const.attributePowerLoad, const.attributePowerOutput), (mls.UI_GENERIC_CALIBRATION, const.attributeUpgradeLoad, const.attributeUpgradeCapacity)):
                wnd.sr.data[mls.UI_GENERIC_FITTING]['items'].append(listentry.Get('StatusBar', {'label': label,
                 'status': GAV(loadAttributeID),
                 'total': GAV(outputAttributeID)}))

            recommendedCerts = sm.StartService('certificates').GetCertificateRecommendationsByShipTypeID(typeID)
            tempList = []
            for cert in recommendedCerts:
                entry = self.GetCertEntry(cert)
                tempList.append((entry.get('level', ''), listentry.Get('CertEntry', entry)))

            sortedList = uiutil.SortListOfTuples(tempList)
            previousLevel = -1
            for each in sortedList:
                if each.level != previousLevel:
                    caption = getattr(mls, 'UI_CERT_RECLEVEL%s' % each.level, '')
                    if previousLevel != -1:
                        wnd.sr.data[mls.UI_SHARED_CERT_RECOMMENDED]['items'].append(listentry.Get('Divider'))
                    wnd.sr.data[mls.UI_SHARED_CERT_RECOMMENDED]['items'].append(listentry.Get('Header', {'label': caption}))
                    previousLevel = each.level
                wnd.sr.data[mls.UI_SHARED_CERT_RECOMMENDED]['items'].append(each)

            if attrDict.has_key(const.attributeMaxJumpClones) and info.maxJumpClones > 0:
                currentClones = []
                if eve.session.shipid:
                    currentClones = sm.GetService('clonejump').GetShipClones()
                wnd.sr.data[mls.UI_GENERIC_FITTING]['items'].append(listentry.Get('StatusBar', {'label': mls.UI_GENERIC_JUMPCLONES,
                 'status': len(currentClones),
                 'total': info.maxJumpClones}))
            if session.shipid and session.shipid == itemID:
                wnd.sr.data[mls.UI_GENERIC_KILLRIGHTS]['items'].extend(self.GetKillRightsSubContent())
            self.GetAttrTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_FITTING]['items'], [const.attributeLowSlots,
             const.attributeMedSlots,
             const.attributeHiSlots,
             const.attributeLauncherSlotsLeft,
             const.attributeTurretSlotsLeft,
             const.attributeUpgradeSlotsLeft,
             const.attributeMaxSubSystems,
             const.attributeRigSize], shipinfo)
            fmHeaderDone = 0
            consideredEffects = [const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower,
             const.effectRigSlot,
             const.effectSubSystem]
            if shipinfo is not None:
                moduleData = {}
                for each in shipinfo.modules:
                    for effect in cfg.dgmtypeeffects.get(each.typeID, []):
                        if effect.effectID in consideredEffects:
                            powerEffect = cfg.dgmeffects.Get(effect.effectID)
                            if moduleData.has_key(effect.effectID):
                                moduleData[effect.effectID] += [[powerEffect, each]]
                            else:
                                moduleData[effect.effectID] = [[powerEffect, each]]


                fitHeader = 0
                if moduleData:
                    for effect in consideredEffects:
                        if not fitHeader:
                            wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('Header', {'label': mls.UI_INFOWND_FITTEDMODULES}))
                            fitHeader = 1
                        if moduleData.has_key(effect):
                            fitSubheader = 0
                            for each in moduleData[effect]:
                                if not fitSubheader:
                                    wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('Subheader', {'label': uiutil.UpperCase(each[0].displayName)}))
                                    fitSubheader = 1
                                wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': mls.UI_GENERIC_MODULE,
                                 'text': each[1].name,
                                 'itemID': each[1].itemID,
                                 'typeID': each[1].typeID,
                                 'iconID': cfg.invtypes.Get(each[1].typeID).iconID}))


                    if fitHeader:
                        wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('Divider'))
                fitHeader = 0
                if shipinfo.sublocations:
                    for each in shipinfo.sublocations:
                        if not fitHeader:
                            wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('Header', {'label': mls.UI_INFOWND_FITTEDCHARGES}))
                            fitHeader = 1
                        wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_CHARGE,
                         'text': each.name,
                         'itemID': each.itemID,
                         'typeID': each.typeID,
                         'iconID': cfg.invtypes.Get(each.typeID).iconID}))

            else:
                shiptypeinfo = cfg.shiptypes.Get(typeID)
                fmHeaderDone = 1
                for key in ['weaponTypeID', 'miningTypeID']:
                    moduleTypeID = getattr(shiptypeinfo, key, None)
                    if moduleTypeID:
                        invtype = cfg.invtypes.Get(moduleTypeID)
                        wnd.sr.data[mls.UI_GENERIC_MODULES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_MODULE,
                         'text': invtype.name,
                         'typeID': moduleTypeID,
                         'iconID': invtype.iconID}))

            shiptypeinfo = cfg.shiptypes.Get(typeID)
            self.GetReqSkillInfo(typeID, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'])
            self.GetMetaTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_VARIATIONS]['items'], wnd)
            self.InitVariationBottom(wnd)
            if itemID:
                contract = sm.RemoteSvc('insuranceSvc').GetContractForShip(itemID)
                if contract and contract.ownerID in [eve.session.corpid, eve.session.charid]:
                    wnd.sr.data[mls.UI_GENERIC_INSURANCE]['items'].append(listentry.Get('Header', {'label': mls.UI_INFOWND_INSURANCEDETAILS}))
                    wnd.sr.data[mls.UI_GENERIC_INSURANCE]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': mls.UI_INFOWND_INSUREDBY,
                     'text': cfg.eveowners.Get(contract.ownerID).name}))
                    wnd.sr.data[mls.UI_GENERIC_INSURANCE]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': mls.UI_GENERIC_LEVEL,
                     'text': '%s%%' % (contract.fraction * 100)}))
                    wnd.sr.data[mls.UI_GENERIC_INSURANCE]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': mls.UI_GENERIC_FROM,
                     'text': util.FmtDate(contract.startDate)}))
                    wnd.sr.data[mls.UI_GENERIC_INSURANCE]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': mls.UI_GENERIC_TONUMBER,
                     'text': util.FmtDate(contract.endDate)}))
        elif wnd.sr.isModule or wnd.sr.isStructure or wnd.sr.isDrone or wnd.sr.isAnchorable or wnd.sr.isConstructionPF or wnd.sr.isStructureUpgrade or wnd.sr.isApparel:
            self.GetInvTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], self.FilterZero, [const.attributeCapacity, const.attributeVolume, const.attributeMass])
            if not itemID:
                ammoLoadeds = [ x for x in cfg.dgmtypeattribs.get(typeID, []) if x.attributeID == const.attributeAmmoLoaded ]
                if len(ammoLoadeds):
                    self.GetAttrTypeInfo(ammoLoadeds[0].value, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], [const.attributeEmDamage,
                     const.attributeThermalDamage,
                     const.attributeKineticDamage,
                     const.attributeExplosiveDamage])
            self.GetEffectTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_FITTING]['items'], [const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower,
             const.effectRigSlot,
             const.effectSubSystem])
            self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=[const.attributeCpu,
             const.attributePower,
             const.attributeRigSize,
             const.attributeCapacity,
             const.attributeVolume,
             const.attributeMass] + self.GetSkillAttrs())
            self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_FITTING]['items'], (const.attributeCpu, const.attributePower, const.attributeRigSize))
            self.GetReqSkillInfo(typeID, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'])
            self.GetMetaTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_VARIATIONS]['items'], wnd)
            self.InitVariationBottom(wnd)
        if invgroup.id in [const.groupSecureCargoContainer, const.groupAuditLogSecureContainer]:
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                ball = bp.GetBall(itemID)
            if bp and ball and not ball.isFree:
                bpr = sm.GetService('michelle').GetRemotePark()
                if bpr:
                    expiry = bpr.GetContainerExpiryDate(itemID)
                    daysLeft = max(0, (expiry - blue.os.GetTime()) / DAY)
                    expiryText = '%s %s' % (daysLeft, [mls.GENERIC_DAYS_LOWER, mls.GENERIC_DAY][(daysLeft == 1)])
                    expiryLabel = listentry.Get('LabelTextTop', {'line': 1,
                     'label': mls.UI_GENERIC_EXPIRES,
                     'text': expiryText,
                     'iconID': const.iconDuration})
                    wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(expiryLabel)
        elif wnd.sr.isCharge:
            self.GetInvTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], self.FilterZero, [const.attributeCapacity, const.attributeVolume])
            if itemID:
                self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=[const.attributeCapacity, const.attributeVolume] + self.GetSkillAttrs())
            else:
                self.GetAttrTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=[const.attributeCapacity, const.attributeVolume] + self.GetSkillAttrs())
            (bsd, bad,) = self.GetBaseDamageValue(typeID)
            if bad is not None and bsd is not None:
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_INFOWND_BASESHIELDDMG,
                 'text': '%s' % bsd[0],
                 'iconID': bsd[1]}))
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_INFOWND_BASEARMORDMG,
                 'text': '%s' % bad[0],
                 'iconID': bad[1]}))
            self.GetReqSkillInfo(typeID, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'])
            self.GetMetaTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_VARIATIONS]['items'], wnd)
            self.InitVariationBottom(wnd)
        elif wnd.sr.isCorporation:
            parallelCalls = []
            parallelCalls.append((sm.RemoteSvc('config').GetStationSolarSystemsByOwner, (itemID,)))
            if util.IsNPC(itemID):
                parallelCalls.append((sm.GetService('agents').GetAgentsByCorpID, (itemID,)))
                parallelCalls.append((sm.RemoteSvc('corporationSvc').GetCorpInfo, (itemID,)))
            else:
                parallelCalls.append((ReturnNone, ()))
                parallelCalls.append((ReturnNone, ()))
            parallelCalls.append((sm.GetService('faction').GetNPCCorpInfo, (itemID,)))
            (systems, agents, corpmktinfo, npcCorpInfo,) = uthread.parallel(parallelCalls)
            founderdone = 0
            if cfg.invtypes.Get(cfg.eveowners.Get(wnd.sr.corpinfo.ceoID).typeID).groupID == const.groupCharacter:
                if wnd.sr.corpinfo.creatorID == wnd.sr.corpinfo.ceoID:
                    ceoLabel = mls.UI_INFOWND_CEOANDFOUNDER
                    founderdone = 1
                else:
                    ceoLabel = mls.UI_GENERIC_CEO
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': ceoLabel,
                 'text': cfg.eveowners.Get(wnd.sr.corpinfo.ceoID).name,
                 'typeID': cfg.eveowners.Get(wnd.sr.corpinfo.ceoID).typeID,
                 'itemID': wnd.sr.corpinfo.ceoID}))
            if not founderdone and cfg.invtypes.Get(cfg.eveowners.Get(wnd.sr.corpinfo.creatorID).typeID).groupID == const.groupCharacter:
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_FOUNDER,
                 'text': cfg.eveowners.Get(wnd.sr.corpinfo.creatorID).name,
                 'typeID': cfg.eveowners.Get(wnd.sr.corpinfo.creatorID).typeID,
                 'itemID': wnd.sr.corpinfo.creatorID}))
            if wnd.sr.corpinfo.allianceID:
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_ALLIANCE,
                 'text': cfg.eveowners.Get(wnd.sr.corpinfo.allianceID).name,
                 'typeID': const.typeAlliance,
                 'itemID': wnd.sr.corpinfo.allianceID}))
            for each in [('tickerName', mls.UI_GENERIC_TICKERNAME),
             ('shares', mls.UI_GENERIC_SHARES),
             ('memberCount', mls.UI_GENERIC_MEMBERCOUNT),
             ('taxRate', mls.UI_GENERIC_TAXRATE)]:
                if each[0] == 'memberCount' and util.IsNPC(itemID):
                    continue
                val = getattr(wnd.sr.corpinfo, each[0], 0.0)
                if each[0] == 'taxRate':
                    val = '%s %%' % (val * 100)
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': each[1],
                 'text': val}))

            if wnd.sr.corpinfo.url:
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_URL,
                 'text': '<url=%s>%s</url>' % (wnd.sr.corpinfo.url, wnd.sr.corpinfo.url)}))
            if npcCorpInfo is not None and util.IsNPC(itemID):
                txt = {'T': mls.UI_GENERIC_TINY,
                 'S': mls.UI_GENERIC_SMALL,
                 'M': mls.UI_GENERIC_MEDIUM,
                 'L': mls.UI_GENERIC_LARGE,
                 'H': mls.UI_GENERIC_HUGE}[npcCorpInfo.size]
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_SIZE,
                 'text': txt}))
                txt = {'N': mls.UI_GENERIC_NATIONAL,
                 'G': mls.UI_GENERIC_GLOBAL,
                 'R': mls.UI_GENERIC_REGIONAL,
                 'L': mls.UI_GENERIC_LOCAL,
                 'C': mls.UI_GENERIC_CONSTELLATION}[npcCorpInfo.extent]
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_EXTENT,
                 'text': txt}))
            if itemID == session.corpid:
                for charinfo in sm.GetService('corp').GetMembersAsEveOwners():
                    if not util.IsNPC(charinfo.ownerID):
                        wnd.sr.data[mls.UI_CORP_CORPMEMBERS]['items'].append(listentry.Get('User', {'info': charinfo,
                         'charID': charinfo.ownerID}))

                wnd.sr.data[mls.UI_CORP_CORPMEMBERS]['headers'].append(mls.UI_GENERIC_NAME)
            solarSystemDict = {}
            for solarSys in systems:
                solarSystemDict[solarSys.solarSystemID] = (2.0,
                 1.0,
                 mls.UI_INFOWND_SETTLEDBY + ' ' + wnd.sr.corpinfo.corporationName,
                 None)

            mapSvc = sm.GetService('map')
            for solarSys in systems:
                parentConstellation = mapSvc.GetParent(solarSys.solarSystemID)
                parentRegion = mapSvc.GetParent(parentConstellation)
                name_with_path = ' / '.join([ mapSvc.GetItem(each).itemName for each in (parentRegion, parentConstellation, solarSys.solarSystemID) ])
                wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_SOLARSYSTEM,
                 'text': name_with_path,
                 'typeID': const.typeSolarSystem,
                 'itemID': solarSys.solarSystemID}))

            wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['name'] = mls.UI_INFOWND_SETTLEDSYSTEMS

            def ShowMap(*args):
                sm.GetService('map').OpenStarMap()
                sm.GetService('starmap').HighlightSolarSystems(solarSystemDict)


            wnd.sr.data['buttons'] += [(mls.UI_CMD_SHOWONMAP,
              ShowMap,
              (),
              66)]
            if not util.IsNPC(itemID):
                wnd.sr.data['buttons'] += [(mls.UI_CMD_APPLYTOJOIN, sm.GetService('corp').ApplyForMembership, (itemID,))]
            else:
                wnd.sr.data['buttons'] += [(mls.UI_SHARED_AGENTFINDER,
                  uicore.cmd.OpenAgentFinder,
                  (),
                  66)]

            def SortStuff(a, b):
                for i in xrange(3):
                    (x, y,) = (a[i], b[i])
                    if x.name < y.name:
                        return -1
                    if x.name > y.name:
                        return 1

                return 0


            if corpmktinfo is not None:
                sellStuff = []
                buyStuff = []
                for each in corpmktinfo:
                    t = cfg.invtypes.GetIfExists(each.typeID)
                    if t:
                        g = cfg.invgroups.Get(t.groupID)
                        c = cfg.invcategories.Get(g.categoryID)
                        if each.sellPrice is not None:
                            sellStuff.append((c,
                             g,
                             t,
                             each.sellPrice,
                             each.sellQuantity,
                             each.sellDate,
                             each.sellStationID))
                        if each.buyPrice is not None:
                            buyStuff.append((c,
                             g,
                             t,
                             each.buyPrice,
                             each.buyQuantity,
                             each.buyDate,
                             each.buyStationID))

                sellStuff.sort(SortStuff)
                buyStuff.sort(SortStuff)
                for (stuff, label,) in ((sellStuff, mls.UI_GENERIC_SUPPLY), (buyStuff, mls.UI_GENERIC_DEMAND)):
                    if stuff:
                        wnd.sr.data[mls.UI_GENERIC_MARTKETACTIVITY]['items'].append(listentry.Get('Header', {'label': label}))
                        for each in stuff:
                            (c, g, t, price, quantity, lastActivity, station,) = each
                            txt = mls.UI_INFOWND_MARKETENTRYTEXT % {'catname': c.name,
                             'groupname': g.name,
                             'typename': t.name,
                             'price': util.FmtISK(price)}
                            if lastActivity:
                                txt += ' ' + mls.UI_INFOWND_MARKETENTRYTEXT2 % {'lDate': util.FmtDate(lastActivity, 'ls'),
                                 'amt': quantity,
                                 'location': cfg.FormatConvert(LOCID, station)}
                            wnd.sr.data[mls.UI_GENERIC_MARTKETACTIVITY]['items'].append(listentry.Get('Text', {'line': 1,
                             'typeID': t.typeID,
                             'text': txt}))


            if util.IsNPC(itemID):
                agentCopy = agents[:]
                header = agentCopy.header
                acopy2 = util.Rowset(header)
                for (i, agent,) in enumerate(agentCopy):
                    if agent.agentTypeID in (const.agentTypeResearchAgent, const.agentTypeBasicAgent, const.agentTypeFactionalWarfareAgent):
                        acopy2.append(agent)

                agentCopy = acopy2
                self.GetAgentScrollGroups(agentCopy, wnd.sr.data[mls.UI_GENERIC_AGENTS]['items'])
        elif wnd.sr.isAlliance:
            rec = wnd.sr.allianceinfo
            for columnName in rec.header:
                value = getattr(rec, columnName)
                if columnName == 'executorCorpID':
                    executor = cfg.eveowners.GetIfExists(value)
                    if executor is not None:
                        params = {'line': 1,
                         'label': mls.UI_INFOWND_EXECUTOR,
                         'text': executor.ownerName,
                         'typeID': const.typeCorporation,
                         'itemID': value}
                    else:
                        params = {'line': 1,
                         'label': mls.UI_INFOWND_EXECUTOR,
                         'text': '-'}
                elif columnName == 'shortName':
                    params = {'line': 1,
                     'label': mls.UI_INFOWND_SHORTNAME,
                     'text': value}
                elif columnName == 'url':
                    params = {'line': 1,
                     'label': mls.UI_GENERIC_URL,
                     'text': '<url=%s>%s</url>' % (value, value)}
                elif columnName == 'creatorCorpID':
                    params = {'line': 1,
                     'label': mls.UI_INFOWND_CREATEDBYCORP,
                     'text': cfg.eveowners.Get(value).ownerName,
                     'typeID': const.typeCorporation,
                     'itemID': value}
                elif columnName == 'creatorCharID':
                    params = {'line': 1,
                     'label': mls.UI_INFOWND_CREATEDBY,
                     'text': cfg.eveowners.Get(value).ownerName,
                     'typeID': const.typeCharacterAmarr,
                     'itemID': value}
                elif columnName == 'startDate':
                    params = {'line': 1,
                     'label': mls.UI_INFOWND_STARTDATE,
                     'text': util.FmtDate(value, 'ls'),
                     'typeID': None,
                     'itemID': None}
                else:
                    continue
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', params))

        elif wnd.sr.isBlueprint:
            blueprintType = cfg.invbptypes.Get(typeID)
            isCopy = None
            if wnd.sr.blueprintInfo:
                bpi = wnd.sr.blueprintInfo
                wnd.sr.blueprintInfo = None
            elif wnd.sr.abstractinfo is not None:
                bpi = {}
                bpi['manufacturingTime'] = blueprintType.productionTime
                bpi['productivityLevel'] = getattr(wnd.sr.abstractinfo, 'productivityLevel', 0)
                bpi['materialLevel'] = getattr(wnd.sr.abstractinfo, 'materialLevel', 0)
                bpi['maxProductionLimit'] = blueprintType.maxProductionLimit
                bpi['researchMaterialTime'] = blueprintType.researchMaterialTime
                bpi['researchCopyTime'] = blueprintType.researchCopyTime
                bpi['researchProductivityTime'] = blueprintType.researchProductivityTime
                bpi['researchTechTime'] = blueprintType.researchTechTime
                bpi['wastageFactor'] = blueprintType.wasteFactor / 100.0
                bpi['productTypeID'] = blueprintType.productTypeID
                if wnd.sr.abstractinfo.isCopy:
                    bpi['copy'] = True
                    runs = wnd.sr.abstractinfo.Get('runs', None)
                    if runs is not None:
                        bpi['licensedProductionRunsRemaining'] = runs
            else:
                bpi = {}
                bpi['manufacturingTime'] = blueprintType.productionTime
                bpi['productivityLevel'] = 0
                bpi['materialLevel'] = 0
                bpi['maxProductionLimit'] = blueprintType.maxProductionLimit
                bpi['researchMaterialTime'] = blueprintType.researchMaterialTime
                bpi['researchCopyTime'] = blueprintType.researchCopyTime
                bpi['researchProductivityTime'] = blueprintType.researchProductivityTime
                bpi['researchTechTime'] = blueprintType.researchTechTime
                bpi['wastageFactor'] = blueprintType.wasteFactor / 100.0
                bpi['productTypeID'] = blueprintType.productTypeID
            godmaChar = sm.GetService('godma').GetItem(eve.session.charid)
            for (caption, attrs,) in self.GetBlueprintAttributes():
                bpAttr = [ each for each in attrs if each in bpi ]
                if bpAttr:
                    bpAttrValid = [ each for each in bpAttr if bpi.has_key(each) ]
                    for each in bpAttrValid:
                        if each == 'copy':
                            isCopy = bpi[each] > 0
                            break

                    if isCopy is not None:
                        break

            typeOb = cfg.invtypes.Get(typeID)
            groupID = typeOb.groupID
            categoryID = typeOb.categoryID
            if categoryID != const.categoryAncientRelic:
                if isCopy == True:
                    wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Item', {'itemID': None,
                     'isCopy': True,
                     'typeID': typeID,
                     'label': '%s <color=0xff999999><b>%s</b></color>' % (mls.UI_GENERIC_BLUEPRINT, mls.UI_GENERIC_COPY),
                     'getIcon': 1}))
                elif isCopy == False:
                    wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Item', {'itemID': None,
                     'typeID': typeID,
                     'label': '<color=0xff55bb55><b>%s</b></color> %s' % (mls.UI_GENERIC_ORIGINAL, mls.UI_GENERIC_BLUEPRINT),
                     'getIcon': 1}))
            if categoryID == const.categoryAncientRelic:
                propertyName = 'researchTechTime'
                propertyValue = bpi[propertyName]
                propertyName = mls.UI_INFOWND_RESEARCHTECHTIME
                propertyValue = self.FormatAsFactoryTime(propertyValue)
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Header', {'line': 1,
                 'label': mls.UI_GENERIC_REVERSEENGINEERING2}))
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': propertyName,
                 'text': propertyValue,
                 'iconID': const.iconDuration}))
            else:
                for (caption, attrs,) in self.GetBlueprintAttributes():
                    bpAttr = [ each for each in attrs if each in bpi ]
                    if bpAttr:
                        bpAttrValid = [ each for each in bpAttr if bpi.has_key(each) ]
                        if caption in [mls.UI_INFOWND_PRODUCES]:
                            pass
                        elif 'researchTechTime' in bpAttrValid or not isCopy or caption not in [mls.SHARED_RESEARCHING]:
                            wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Header', {'line': 1,
                             'label': caption}))
                        for each in bpAttrValid:
                            propertyName = each
                            propertyValue = bpi[each]
                            if propertyName == 'manufacturingTime':
                                propertyName = mls.UI_INFOWND_MANUFACTURINGTIME
                                batchTime = blueprintType.productionTime
                                pl = bpi['productivityLevel']
                                if pl > 0:
                                    batchTime = batchTime - (1.0 - 1.0 / (1 + pl)) * blueprintType.productivityModifier
                                elif pl < 0:
                                    batchTime = batchTime + (1.0 - pl) * blueprintType.productivityModifier
                                batchTime = int(batchTime)
                                propertyValue = self.FormatAsFactoryTime(batchTime)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                timeMultiplier = godmaChar.manufactureTimeMultiplier
                                batchTime = long(float(batchTime) * timeMultiplier)
                                propertyName += ' (%s)' % mls.UI_GENERIC_YOU
                                propertyValue = self.FormatAsFactoryTime(batchTime)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                continue
                            elif propertyName == 'researchMaterialTime':
                                if isCopy:
                                    continue
                                propertyName = mls.UI_INFOWND_RESEARCHMATERIALTIME
                                propertyValue = self.FormatAsFactoryTime(propertyValue)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                timeMultiplier = godmaChar.mineralNeedResearchSpeed
                                batchTime = blueprintType.researchMaterialTime
                                batchTime = long(float(batchTime) * timeMultiplier)
                                propertyName += ' (%s)' % mls.UI_GENERIC_YOU
                                propertyValue = self.FormatAsFactoryTime(batchTime)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                continue
                            elif propertyName == 'researchCopyTime':
                                if isCopy:
                                    continue
                                timeMultiplier = sm.GetService('godma').GetType(cfg.eveowners.Get(eve.session.charid).typeID).copySpeedPercent
                                propertyName = mls.UI_INFOWND_RESEARCHCOPYTIME
                                propertyValue = self.FormatAsFactoryTime(long(float(propertyValue) * timeMultiplier))
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                timeMultiplier = godmaChar.copySpeedPercent
                                percent = float(1) / float(blueprintType.maxProductionLimit)
                                batchTime = long(float(blueprintType.researchCopyTime) * percent)
                                batchTime = long(float(batchTime) * timeMultiplier)
                                propertyName += ' ' + mls.UI_INFOWND_YOUPERSINGLECOPY
                                propertyValue = self.FormatAsFactoryTime(batchTime)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                continue
                            elif propertyName == 'researchProductivityTime':
                                if isCopy:
                                    continue
                                propertyName = mls.UI_INFOWND_RESEARCHPRODUCTIVITYTIME
                                propertyValue = self.FormatAsFactoryTime(propertyValue)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                timeMultiplier = godmaChar.manufacturingTimeResearchSpeed
                                batchTime = blueprintType.researchProductivityTime
                                batchTime = long(float(batchTime) * timeMultiplier)
                                propertyName += ' (%s)' % mls.UI_GENERIC_YOU
                                propertyValue = self.FormatAsFactoryTime(batchTime)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                continue
                            elif propertyName == 'researchTechTime':
                                if not isCopy:
                                    continue
                                propertyName = mls.UI_INFOWND_RESEARCHTECHTIME
                                propertyValue = self.FormatAsFactoryTime(propertyValue)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': propertyName,
                                 'text': propertyValue,
                                 'iconID': const.iconDuration}))
                                continue
                            elif propertyName == 'materialLevel':
                                propertyName = mls.UI_INFOWND_MATERIALLEVEL
                            elif propertyName == 'maxProductionLimit':
                                propertyName = mls.UI_RMR_PRODUCTIONLIMIT
                            elif propertyName == 'productivityLevel':
                                propertyName = mls.UI_INFOWND_PRODUCTIVITYEVEL
                            elif propertyName == 'wastageFactor':
                                propertyName = mls.UI_INFOWND_WASTAGEFACTOR
                                propertyValue = '%s%%' % (float(int(propertyValue * 10000)) / 100)
                            elif propertyName == 'productTypeID':
                                propertyName = mls.UI_INFOWND_PRODUCES
                                typeInfo = cfg.invtypes.Get(propertyValue)
                                typeDescription = '%s %s [%s]' % (mls.UI_INFOWND_PRODUCES, typeInfo.typeName, typeInfo.portionSize)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('Item', {'itemID': None,
                                 'typeID': propertyValue,
                                 'label': typeDescription,
                                 'getIcon': 1}))
                                continue
                            elif propertyName == 'copy':
                                propertyName = mls.UI_GENERIC_COPY
                                propertyValue = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][propertyValue]
                            elif propertyName == 'licensedProductionRunsRemaining':
                                propertyName = mls.UI_INFOWND_LICENSEDPRODRUNSREMAINING
                                if propertyValue == -1:
                                    propertyValue = mls.UI_GENERIC_INFINITE
                            wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                             'label': propertyName,
                             'text': propertyValue}))


            bomByActivity = sm.RemoteSvc('factory').GetMaterialsForTypeWithActivity(typeID)
            activities = {const.activityManufacturing: mls.UI_GENERIC_MANUFACTURING,
             const.activityCopying: mls.UI_GENERIC_COPYING,
             const.activityResearchingMaterialProductivity: mls.UI_GENERIC_RESEARCHINGMATERIALEFF,
             const.activityResearchingTimeProductivity: mls.UI_GENERIC_RESEARCHTIMEPROD,
             const.activityDuplicating: mls.UI_GENERIC_DUBLICATING,
             const.activityReverseEngineering: mls.UI_GENERIC_REVERSEENGINEERING2,
             const.activityInvention: mls.UI_GENERIC_REVERSEENGINEERING}
            blueprintMaterialMultiplier = 0.0
            characterMaterialMultiplier = max(1.0, godmaChar.manufactureCostMultiplier)
            if bpi.has_key('wastageFactor'):
                blueprintMaterialMultiplier = bpi['wastageFactor']
            for activity in activities:
                if activity not in bomByActivity.keys():
                    continue
                activityName = activities[activity]
                skills = []
                materials = []
                commands = []
                indexedExtras = copy.deepcopy(bomByActivity[activity].extras).Index('requiredTypeID')
                for skill in bomByActivity[activity].skills:
                    propertyInfo = cfg.invtypes.Get(skill.requiredTypeID)
                    propertyName = propertyInfo.typeName
                    propertyValue = mls.UI_INFOWND_PROPERTYVALUE % {'propertyName': propertyName,
                     'qty': skill.quantity}
                    skills.append((propertyName,
                     propertyValue,
                     skill.requiredTypeID,
                     skill.quantity))

                for material in bomByActivity[activity].rawMaterials:
                    if material.quantity <= 0:
                        continue
                    propertyInfo = cfg.invtypes.Get(material.requiredTypeID)
                    propertyName = propertyInfo.typeName
                    amountRequired = amountRequiredByPlayer = material.quantity
                    blueprintWaste = characterWaste = 0.0
                    extraAmount = 0
                    if activity in (const.activityManufacturing, const.activityDuplicating):
                        if material.requiredTypeID in indexedExtras and indexedExtras[material.requiredTypeID].quantity > 0:
                            extraAmount = indexedExtras[material.requiredTypeID].quantity
                            indexedExtras[material.requiredTypeID].quantity = 0
                        if activity == const.activityManufacturing:
                            blueprintWaste = float(amountRequired) * float(blueprintMaterialMultiplier)
                        characterWaste = float(amountRequired) * float(characterMaterialMultiplier) - float(amountRequired)
                        amountRequired = amountRequired + extraAmount + blueprintWaste
                        amountRequiredByPlayer = int(round(amountRequired + characterWaste))
                        amountRequired = int(round(amountRequired))
                    if amountRequiredByPlayer == amountRequired:
                        propertyValue = '%s - [%s]' % (propertyName, amountRequiredByPlayer)
                    else:
                        propertyValue = '%s - [%s: %s - %s: %s]' % (propertyName,
                         mls.UI_GENERIC_YOU,
                         amountRequiredByPlayer,
                         mls.UI_GENERIC_PERFECT,
                         amountRequired)
                    if amountRequiredByPlayer >= 0.0:
                        commands.append((material.requiredTypeID, amountRequiredByPlayer))
                    materials.append((propertyName, propertyValue, material.requiredTypeID))

                for (key, extra,) in indexedExtras.iteritems():
                    if extra.quantity <= 0:
                        continue
                    propertyInfo = cfg.invtypes.Get(extra.requiredTypeID)
                    propertyName = propertyInfo.typeName
                    if extra.damagePerJob < 1.0:
                        propertyValue = '%s - [%s], %s: %s%%' % (propertyName,
                         extra.quantity,
                         mls.UI_GENERIC_DAMAGEPERRUN,
                         extra.damagePerJob * 100)
                    else:
                        propertyValue = '%s - [%s]' % (propertyName, extra.quantity)
                    materials.append((propertyName, propertyValue, extra.requiredTypeID))
                    commands.append((extra.requiredTypeID, extra.quantity))

                wnd.sr.data[activityName]['items'].append(listentry.Get('Text', {'line': 1,
                 'text': mls.UI_INFOWND_BOMTEXT1}))
                wnd.sr.data[activityName]['items'].append(listentry.Get('Divider'))
                for (label, content,) in ((mls.UI_GENERIC_SKILLS, skills), (mls.UI_GENERIC_MATERIALS, materials)):
                    data = {'GetSubContent': self.GetBOMSubContent,
                     'label': label,
                     'groupItems': content,
                     'id': ('BOM', label),
                     'tabs': [],
                     'state': 'locked',
                     'showicon': 'hide',
                     'commands': commands}
                    wnd.sr.data[activityName]['items'].append(listentry.Get('Group', data))


        elif wnd.sr.isStargate:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is not None:
                slimItem = bp.GetInvItem(itemID)
                if slimItem is not None:
                    locs = []
                    for each in slimItem.jumps:
                        if each.locationID not in locs:
                            locs.append(each.locationID)
                        if each.toCelestialID not in locs:
                            locs.append(each.toCelestialID)

                    if len(locs):
                        cfg.evelocations.Prime(locs)
                    for each in slimItem.jumps:
                        solname = cfg.evelocations.Get(each.locationID).name
                        destname = cfg.evelocations.Get(each.toCelestialID).name
                        wnd.sr.data[mls.UI_GENERIC_JUMPS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_JUMP,
                         'text': mls.UI_INFOWND_DESTINSOL % {'destination': destname,
                                  'solarsystem': solname},
                         'typeID': const.groupSolarSystem,
                         'itemID': each.locationID}))

        elif wnd.sr.isCelestial:
            if 40000000 < itemID < 50000000:
                celestialinfo = sm.RemoteSvc('config').GetCelestialStatistic(itemID)
                if len(celestialinfo):
                    for key in celestialinfo.columns:
                        if key not in 'celestialID':
                            val = celestialinfo[0][key]
                            text = val
                            if invgroup.id not in [const.groupSun] and key in ('spectralClass', 'luminosity', 'age'):
                                pass
                            elif invgroup.id in [const.groupSun] and key in ('orbitRadius', 'eccentricity', 'massDust', 'density', 'surfaceGravity', 'escapeVelocity', 'orbitPeriod', 'pressure'):
                                pass
                            elif key in ('fragmented', 'locked', 'rotationRate', 'mass', 'massGas', 'life'):
                                pass
                            if invgroup.id in [const.groupAsteroidBelt] and key in ('surfaceGravity', 'escapeVelocity', 'pressure', 'radius', 'temperature'):
                                pass
                            elif invgroup.id in [const.groupMoon] and key in ('eccentricity',):
                                pass
                            else:
                                (label, value,) = util.FmtPlanetAttributeKeyVal(key, val)
                                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                                 'label': label,
                                 'text': value}))

            (universeID, regionID, constellationID, solarsystemID, _itemID,) = sm.GetService('map').GetParentLocationID(itemID, 1)
            if solarsystemID is None and moonOrPlanet:
                solarsystemID = parentID
            if solarsystemID is not None:
                solarsystem = sm.RemoteSvc('config').GetMapObjects(solarsystemID, 0, 0, 0, 1, 0)
                sun = None
                if cfg.invtypes.Get(typeID).groupID == const.groupSolarSystem:
                    for each in solarsystem:
                        if cfg.invtypes.Get(each.typeID).groupID == const.groupSun:
                            sun = each.itemID

                    if sun:
                        itemID = sun
                orbitItems = []
                indent = 0
                if solarsystemID == itemID and sun:
                    rootID = [ each for each in solarsystem if cfg.invtypes.Get(each.typeID).groupID == const.groupSun ][0].itemID
                else:
                    rootID = itemID
                groupSort = {const.groupStation: -2,
                 const.groupStargate: -1,
                 const.groupAsteroidBelt: 1,
                 const.groupMoon: 2,
                 const.groupPlanet: 3}

                def DrawOrbitItems(rootID, indent):
                    tmp = [ each for each in solarsystem if each.orbitID == rootID ]
                    tmp.sort(lambda a, b: cmp(*[ groupSort.get(cfg.invtypes.Get(each.typeID).groupID, 0) for each in (a, b) ]) or cmp(a.itemName, b.itemName))
                    for each in tmp:
                        name = each.itemName
                        planet = False
                        if util.IsStation(each.itemID):
                            name = '<b>' + name + '</b>'
                        elif each.groupID == const.groupMoon:
                            name = '<color=0xff666666>' + name + '</color>'
                        elif each.groupID == const.groupPlanet:
                            planet = True
                        if planet:
                            wnd.sr.data[mls.UI_GENERIC_ORBITALBODIES]['items'].append(listentry.Get('LabelPlanetTextTop', {'line': 1,
                             'label': indent * '    ' + cfg.invtypes.Get(each.typeID).name,
                             'text': indent * '    ' + name,
                             'typeID': each.typeID,
                             'itemID': each.itemID,
                             'locationID': solarsystemID}))
                        else:
                            wnd.sr.data[mls.UI_GENERIC_ORBITALBODIES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                             'label': indent * '    ' + cfg.invtypes.Get(each.typeID).name,
                             'text': indent * '    ' + name,
                             'typeID': each.typeID,
                             'itemID': each.itemID}))
                        DrawOrbitItems(each.itemID, indent + 1)



                if sun:
                    DrawOrbitItems(rootID, 0)
                itemID = solarsystemID
            typeGroupID = cfg.invtypes.Get(typeID).groupID
            neighborGrouping = {const.groupConstellation: mls.UI_INFOWND_ADJACENTCONSTELLATIONS,
             const.groupRegion: mls.UI_INFOWND_ADJACENTREGIONS,
             const.groupSolarSystem: mls.UI_INFOWND_ADJACENTSOLARSYSTEMS}
            childGrouping = {const.groupRegion: mls.UI_INFOWND_RELATEDCONSTELLATIONS,
             const.groupConstellation: mls.UI_INFOWND_RELATEDSOLARSYSTEMS}
            if typeGroupID == const.groupConstellation:
                children = sm.GetService('map').GetChildren(itemID)
                for childID in children:
                    childItem = sm.GetService('map').GetItem(childID)
                    if childItem is not None:
                        wnd.sr.data[mls.UI_INFOWND_CHILDREN]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': cfg.invtypes.Get(childItem.typeID).name,
                         'text': childItem.itemName,
                         'typeID': childItem.typeID,
                         'itemID': childItem.itemID}))

                wnd.sr.data[mls.UI_INFOWND_CHILDREN]['name'] = childGrouping.get(typeGroupID, mls.UI_GENERIC_UNKNOWN)
            elif typeGroupID == const.groupRegion:
                children = sm.GetService('map').GetChildren(itemID)
                for childID in children:
                    childItem = sm.GetService('map').GetItem(childID)
                    if childItem is not None:
                        wnd.sr.data[mls.UI_INFOWND_CHILDREN]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': cfg.invtypes.Get(childItem.typeID).name,
                         'text': childItem.itemName,
                         'typeID': childItem.typeID,
                         'itemID': childItem.itemID}))

                wnd.sr.data[mls.UI_INFOWND_CHILDREN]['name'] = childGrouping.get(typeGroupID, mls.UI_GENERIC_UNKNOWN)
            if typeGroupID in [const.groupConstellation, const.groupRegion, const.groupSolarSystem]:
                neigbors = sm.GetService('map').GetNeighbors(itemID)
                for childID in neigbors:
                    childItem = sm.GetService('map').GetItem(childID)
                    if childItem is not None:
                        wnd.sr.data[mls.UI_INFOWND_NEIGHBORS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': cfg.invtypes.Get(childItem.typeID).name,
                         'text': childItem.itemName,
                         'typeID': childItem.typeID,
                         'itemID': childItem.itemID}))

                wnd.sr.data[mls.UI_INFOWND_NEIGHBORS]['name'] = neighborGrouping.get(typeGroupID, mls.UI_GENERIC_UNKNOWN)
            if cfg.invtypes.Get(typeID).groupID in [const.groupConstellation, const.groupSolarSystem]:
                mapSvc = sm.GetService('map')
                shortestRoute = sm.GetService('starmap').ShortestGeneralPath(itemID)
                shortestRoute = shortestRoute[1:]
                wasRegion = None
                wasConstellation = None
                for i in range(len(shortestRoute)):
                    childID = shortestRoute[i]
                    childItem = sm.GetService('map').GetItem(childID)
                    name_with_path = ''
                    parentConstellation = mapSvc.GetParent(childID)
                    parentRegion = mapSvc.GetParent(parentConstellation)
                    for each in [parentRegion, parentConstellation]:
                        parentItem = mapSvc.GetItem(each)
                        name_with_path = name_with_path + parentItem.itemName + ' / '

                    name_with_path = name_with_path + childItem.itemName
                    jumpDescription = str(i + 1) + '. '
                    if i > 0:
                        if wasRegion != parentRegion:
                            jumpDescription = jumpDescription + mls.UI_INFOWND_REGIONJUMP
                        elif wasConstellation != parentConstellation:
                            jumpDescription = jumpDescription + mls.UI_INFOWND_CONSTELLAIONTJUMP
                    wasRegion = parentRegion
                    wasConstellation = parentConstellation
                    if childItem is not None:
                        wnd.sr.data[mls.UI_GENERIC_ROUTE]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': jumpDescription,
                         'text': name_with_path,
                         'typeID': childItem.typeID,
                         'itemID': childItem.itemID}))

            groupID = cfg.invtypes.Get(typeID).groupID

            def ShowMap(idx, *args):
                sm.GetService('map').OpenStarMap()
                sm.GetService('starmap').SetInterest(itemID, forceframe=1)


            if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion]:
                loc = (None, None, None)
                if groupID == const.groupSolarSystem:
                    systemID = itemID
                    constellationID = sm.GetService('map').GetParent(itemID)
                    regionID = sm.GetService('map').GetParent(constellationID)
                    loc = (systemID, constellationID, regionID)
                elif groupID == const.groupConstellation:
                    constellationID = itemID
                    regionID = sm.GetService('map').GetParent(constellationID)
                    loc = (None, constellationID, regionID)
                elif groupID == const.groupRegion:
                    regionID = itemID
                    loc = (None, None, regionID)
                wnd.sr.data['buttons'] = [(mls.UI_CMD_BOOKMARKLOCATION,
                  self.Bookmark,
                  (itemID, typeID, parentID),
                  81), (mls.UI_CMD_SHOWONMAP,
                  ShowMap,
                  [const.groupSolarSystem, const.groupConstellation, const.groupRegion].index(groupID),
                  81), (mls.SOVEREIGNTY_SOVEREIGNTYDASHBOARD, self.DrillToLocation, loc)]
            invtype = cfg.invtypes.Get(typeID)
            if invtype.categoryID == const.categoryAsteroid or invtype.groupID == const.groupHarvestableCloud:
                t = cfg.invtypes.Get(typeID)
                fields = [(mls.UI_INFOWND_ASTEROIDVOLUME, t.volume), (mls.UI_INFOWND_UNITSTOREFINE, int(t.portionSize))]
                try:
                    fields.append((mls.UI_GENERIC_RADIUS, '%.1f' % sm.GetService('michelle').GetBallpark().GetBall(itemID).radius))
                except:
                    sys.exc_clear()
                for (header, text,) in fields:
                    wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': header,
                     'text': text}))

        if wnd.sr.isOwned:
            if eve.session.solarsystemid is not None:
                slimitem = sm.GetService('michelle').GetBallpark().GetInvItem(itemID)
                if slimitem is not None:
                    ownerID = slimitem.ownerID
                    ownerOb = cfg.eveowners.Get(ownerID)
                    if ownerOb.groupID == const.groupCharacter:
                        btn = uix.GetBigButton(42, wnd.sr.subinfolinkcontainer, left=0, top=0, iconMargin=2)
                        btn.OnClick = (self._Info__PreFormatWnd,
                         wnd,
                         ownerOb.typeID,
                         ownerID)
                        btn.hint = mls.UI_INFOWND_CLICKFORPILOTINFO
                        btn.sr.icon.LoadIconByTypeID(ownerOb.typeID, itemID=ownerID, ignoreSize=True)
                        btn.sr.icon.SetSize(0, 0)
                        wnd.sr.subinfolinkcontainer.height = 42
                    if ownerOb.groupID == const.groupCorporation:
                        self.GetCorpLogo(ownerID, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                        wnd.sr.subinfolinkcontainer.height = 64
        if wnd.sr.isFaction:
            (races, stations, systems,) = sm.GetService('faction').GetFactionInfo(itemID)
            memberRaces = ''
            for race in sm.GetService('cc').GetData('races'):
                if race.raceID in races:
                    memberRaces += race.raceName + ', '

            memberRaces = memberRaces[:-2]
            if memberRaces:
                wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_INFOWND_MEMBERRACES,
                 'text': memberRaces}))
            wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
             'label': mls.UI_INFOWND_SETTLEDSYSTEMS,
             'text': systems}))
            wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
             'label': mls.UI_GENERIC_STATIONS,
             'text': stations}))
            wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['name'] = mls.UI_GENERIC_STATISTICS

            def SortFunc(x, y):
                xname = cfg.eveowners.Get(x).name
                if xname.startswith('The '):
                    xname = xname[4:]
                yname = cfg.eveowners.Get(y).name
                if yname.startswith('The '):
                    yname = yname[4:]
                if xname < yname:
                    return -1
                if xname > yname:
                    return 1
                return 0


            corpsOfFaction = sm.GetService('faction').GetCorpsOfFaction(itemID)
            corpsOfFaction = copy.copy(corpsOfFaction)
            corpsOfFaction.sort(SortFunc)
            for corpID in corpsOfFaction:
                corp = cfg.eveowners.Get(corpID)
                wnd.sr.data[mls.UI_GENERIC_MEMBERCORPS]['items'].append(listentry.Get('Text', {'line': 1,
                 'typeID': corp.typeID,
                 'itemID': corp.ownerID,
                 'text': corp.name}))

            mapSvc = sm.GetService('map')
            (regions, constellations, solarsystems,) = sm.GetService('faction').GetFactionLocations(itemID)
            for regionID in regions:
                name_with_path = mapSvc.GetItem(regionID).itemName
                wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_REGION,
                 'text': name_with_path,
                 'typeID': const.typeRegion,
                 'itemID': regionID}))

            for constellationID in constellations:
                regionID = mapSvc.GetParent(constellationID)
                name_with_path = mapSvc.GetItem(regionID).itemName + ' / ' + mapSvc.GetItem(constellationID).itemName
                wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_CONSTELLATION,
                 'text': name_with_path,
                 'typeID': const.typeConstellation,
                 'itemID': constellationID}))

            for solarsystemID in solarsystems:
                constellationID = mapSvc.GetParent(solarsystemID)
                regionID = mapSvc.GetParent(constellationID)
                name_with_path = mapSvc.GetItem(regionID).itemName + ' / ' + mapSvc.GetItem(constellationID).itemName + ' / ' + mapSvc.GetItem(solarsystemID).itemName
                wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': mls.UI_GENERIC_SOLARSYSTEM,
                 'text': name_with_path,
                 'typeID': const.typeSolarSystem,
                 'itemID': solarsystemID}))

            wnd.sr.data[mls.UI_GENERIC_SYSTEMS]['name'] = mls.UI_INFOWND_CONTROLLEDTERRITORY
            illegalities = cfg.invcontrabandTypesByFaction.get(itemID, {})
            if illegalities:
                wnd.sr.data[mls.UI_GENERIC_LEGALITY]['items'].append(listentry.Get('Header', {'label': mls.UI_INFOWND_ILLEGALTYPES}))
            for (tmpTypeID, illegality,) in illegalities.iteritems():
                txt = self._Info__GetIllegalityString(illegality)
                wnd.sr.data[mls.UI_GENERIC_LEGALITY]['items'].append(listentry.Get('Text', {'line': 1,
                 'text': cfg.invtypes.Get(tmpTypeID).name + txt,
                 'typeID': tmpTypeID}))

        if wnd.sr.isCharacter and util.IsNPC(itemID) or invgroup == const.groupAgentsinSpace and sm.GetService('godma').GetType(typeID).agentID:
            agentID = itemID or sm.GetService('godma').GetType(typeID).agentID
            try:
                details = sm.GetService('agents').GetAgentMoniker(agentID).GetInfoServiceDetails()
                if details is not None:
                    npcDivisions = sm.GetService('agents').GetDivisions()
                    agentInfo = sm.GetService('agents').GetAgentByID(agentID)
                    if agentInfo:
                        t = {const.agentTypeGenericStorylineMissionAgent: mls.UI_INFOWND_AGENTTYPE1,
                         const.agentTypeStorylineMissionAgent: mls.UI_INFOWND_AGENTTYPE2,
                         const.agentTypeEventMissionAgent: mls.UI_INFOWND_AGENTTYPE4}.get(agentInfo.agentTypeID, None)
                        if t:
                            wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                             'label': mls.UI_GENERIC_TYPE,
                             'text': t}))
                    if agentInfo and agentInfo.agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_DIVISION,
                         'text': npcDivisions[agentInfo.divisionID].divisionName.replace('&', '&amp;')}))
                    if details.stationID:
                        stationinfo = sm.RemoteSvc('stationSvc').GetStation(details.stationID)
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_LOCATION,
                         'text': cfg.evelocations.Get(details.stationID).name,
                         'typeID': stationinfo.stationTypeID,
                         'itemID': details.stationID}))
                    else:
                        agentSolarSystemID = sm.GetService('agents').GetSolarSystemOfAgent(agentID)
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_LOCATION,
                         'text': cfg.evelocations.Get(agentSolarSystemID).name,
                         'typeID': const.typeSolarSystem,
                         'itemID': agentSolarSystemID}))
                    if agentInfo and agentInfo.agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_GENERIC_LEVEL,
                         'text': details.level}))
                    for each in details.services:
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('Header', {'label': each[0]}))
                        for other in each[1]:
                            wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                             'label': other[0],
                             'text': other[1]}))


                    if details.incompatible:
                        wnd.sr.data[mls.UI_GENERIC_AGENTINFO]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                         'label': mls.UI_INFOWND_COMPATIBILITY,
                         'text': details.incompatible}))
            except UserError as e:
                sys.exc_clear()
        if wnd.sr.isControlTower:
            wnd.sr.dynamicTabs.append((mls.UI_GENERIC_FUELREQUIREMENTS, 'FuelRequirements'))
        if wnd.sr.isConstructionPF:
            wnd.sr.dynamicTabs.append((mls.UI_GENERIC_MATERIALREQUIREMENTS, 'MaterialRequirements'))
        if wnd.sr.isReaction:
            wnd.sr.dynamicTabs.append((mls.UI_GENERIC_REACTION, 'Reaction'))
        if typeID not in (const.typeFaction,):
            illegalities = cfg.invtypes.Get(typeID).Illegality()
            if illegalities:
                wnd.sr.data[mls.UI_GENERIC_LEGALITY]['items'].append(listentry.Get('Header', {'label': mls.UI_INFOWND_LEGALIMPLICATIONS}))
            for (tmpFactionID, illegality,) in illegalities.iteritems():
                txt = self._Info__GetIllegalityString(illegality)
                wnd.sr.data[mls.UI_GENERIC_LEGALITY]['items'].append(listentry.Get('Text', {'line': 1,
                 'text': cfg.eveowners.Get(tmpFactionID).name + txt,
                 'typeID': const.typeFaction,
                 'itemID': tmpFactionID}))

        if wnd.sr.isFaction or wnd.sr.isCorporation or wnd.sr.isCharacter or wnd.sr.isAlliance:
            wnd.sr.dynamicTabs.append((mls.UI_GENERIC_STANDINGS, 'Standings'))
        if wnd.sr.isAlliance:
            wnd.sr.dynamicTabs.append((mls.UI_GENERIC_MEMBERS, 'AllianceMembers'))
        if typeID == const.typePlasticWrap:
            self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'])
            if itemID is not None:
                for each in wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items']:
                    if each.label == mls.UI_GENERIC_CAPACITY:
                        each.text = str(eve.GetInventoryFromId(itemID).GetCapacity().used)

        elif wnd.sr.isGenericItem and not moonOrPlanet:
            if itemID is not None and sm.GetService('godma').GetItem(itemID) is not None:
                self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=self.GetSkillAttrs())
            else:
                self.GetAttrTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=self.GetSkillAttrs())
            self.GetReqSkillInfo(typeID, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'])
        if wnd.sr.isStation and itemID is not None:
            sortServices = []
            stationInfo = sm.RemoteSvc('stationSvc').GetStation(itemID)
            mask = stationInfo.serviceMask
            for (name, cmdStr, displayName, iconpath, stationOnly, bits,) in sm.GetService('station').GetStationServiceInfo(stationInfo=stationInfo):
                if name == 'navyoffices':
                    faction = sm.GetService('faction').GetFaction(stationInfo.ownerID)
                    if faction and faction in [const.factionAmarrEmpire,
                     const.factionCaldariState,
                     const.factionGallenteFederation,
                     const.factionMinmatarRepublic]:
                        sortServices.append((displayName, (displayName, iconpath)))
                else:
                    for bit in bits:
                        if mask & bit:
                            sortServices.append((displayName, (displayName, iconpath)))
                            break


            if sortServices:
                sortServices = uiutil.SortListOfTuples(sortServices)
                for (displayName, iconpath,) in sortServices:
                    wnd.sr.data[mls.UI_GENERIC_SERVICES]['items'].append(listentry.Get('IconEntry', {'line': 1,
                     'label': displayName,
                     'selectable': 0,
                     'iconoffset': 4,
                     'icon': iconpath}))

            for locID in [stationInfo.regionID, stationInfo.constellationID, stationInfo.solarSystemID]:
                mapItem = sm.GetService('map').GetItem(locID)
                if mapItem is not None:
                    wnd.sr.data[mls.UI_GENERIC_LOCATION]['items'].append(listentry.Get('LabelTextTop', {'line': 1,
                     'label': cfg.invtypes.Get(mapItem.typeID).name,
                     'text': mapItem.itemName,
                     'typeID': mapItem.typeID,
                     'itemID': mapItem.itemID}))

            stationOwnerID = None
            if eve.session.solarsystemid is not None:
                slimitem = sm.GetService('michelle').GetBallpark().GetInvItem(itemID)
                if slimitem is not None:
                    stationOwnerID = slimitem.ownerID
            if stationOwnerID is None and stationInfo and stationInfo.ownerID:
                stationOwnerID = stationInfo.ownerID
            if stationOwnerID is not None:
                self.GetCorpLogo(stationOwnerID, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                wnd.sr.subinfolinkcontainer.height = 64
        if wnd.sr.isAbstract:
            if wnd.sr.abstractinfo is not None:
                if wnd.sr.isRank:
                    characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
                    characterRanks = [ each for each in characterRanks if each.factionID == wnd.sr.abstractinfo.warFactionID ]
                    for x in range(9, -1, -1):
                        hilite = False
                        if characterRanks:
                            if characterRanks[0].currentRank == x:
                                hilite = True
                        rank = util.KeyVal(currentRank=x, factionID=wnd.sr.abstractinfo.warFactionID)
                        wnd.sr.data[mls.UI_INFOWND_HIERARCHY]['items'].append(self.GetRankEntry(None, rank, hilite=hilite))

                elif wnd.sr.isCertificate:
                    self.GetReqSkillInfo(None, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'], sm.StartService('certificates').GetParentSkills(wnd.sr.abstractinfo.certificateID), True)
                    self.GetReqCertInfo(None, wnd.sr.data[mls.UI_SHARED_CERTIFICATES]['items'], sm.StartService('certificates').GetParentCertificates(wnd.sr.abstractinfo.certificateID))
                    if not len(wnd.sr.data[mls.UI_GENERIC_SKILLS]['items']):
                        wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'].append(listentry.Get('Text', {'line': 0,
                         'text': mls.UI_SHARED_CERT_NOSKILLSREQ}))
                    if not len(wnd.sr.data[mls.UI_SHARED_CERTIFICATES]['items']):
                        wnd.sr.data[mls.UI_SHARED_CERTIFICATES]['items'].append(listentry.Get('Text', {'line': 0,
                         'text': mls.UI_SHARED_CERT_NOCERTSREQ}))
                    self.GetRecommendedFor(wnd.sr.abstractinfo.certificateID, wnd.sr.data[mls.UI_SHARED_CERT_RECOMMENDEDFOR]['items'])
                elif wnd.sr.isSchematic:
                    self.GetSchematicTypeScrollList(wnd.sr.abstractinfo.schematicID, wnd.sr.data[mls.UI_PI_PRODUCTIONINFO]['items'])
                    self.GetSchematicAttributes(wnd.sr.abstractinfo.schematicID, wnd.sr.abstractinfo.cycleTime, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'])
        if wnd.sr.isPin:
            banAttrs = self.GetSkillAttrs()
            if cfg.invtypes.Get(typeID).groupID == const.groupExtractorPins:
                banAttrs.extend([const.attributePinCycleTime, const.attributePinExtractionQuantity])
            if itemID is not None and sm.GetService('godma').GetItem(itemID) is not None:
                self.GetAttrItemInfo(itemID, typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=banAttrs)
            else:
                self.GetAttrTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], banAttrs=banAttrs)
            self.GetReqSkillInfo(typeID, wnd.sr.data[mls.UI_GENERIC_SKILLS]['items'])
            if cfg.invtypes.Get(typeID).groupID == const.groupProcessPins:
                wnd.sr.dynamicTabs.append((mls.UI_PI_SCHEMATICS, 'ProcessPinSchematics'))
        if wnd.sr.isPICommodity:
            wnd.sr.dynamicTabs.append((mls.UI_PI_PRODUCTIONINFO, 'CommodityProductionInfo'))
        if showAttrs and not wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items']:
            for a in cfg.dgmattribs:
                try:
                    self.GetInvTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], self.FilterZero, [a.attributeID])
                except:
                    sys.exc_clear()

            for e in cfg.dgmeffects:
                try:
                    self.GetEffectTypeInfo(typeID, wnd.sr.data[mls.UI_GENERIC_ATTRIBUTES]['items'], [e.effectID])
                except:
                    sys.exc_clear()

        if prefs.GetValue('showdogmatab', 0) == 1:
            container = wnd.sr.data[mls.UI_GENERIC_DOGMA]['items']
            container.append(listentry.Get('Header', {'label': mls.UI_INFOWND_TYPEATTRS}))
            typeattribs = cfg.dgmtypeattribs.get(typeID, [])
            tattribs = []
            for ta in typeattribs:
                v = ta.value
                a = cfg.dgmattribs.Get(ta.attributeID)
                if v is None:
                    v = a.defaultValue
                tattribs.append([a.attributeID,
                 a.attributeName,
                 v,
                 a.attributeCategory,
                 a.description])

            tattribs.sort(lambda x, y: cmp(x[1], y[1]))
            for ta in tattribs:
                attributeID = ta[0]
                attributeName = ta[1]
                v = ta[2]
                attributeCategory = ta[3]
                description = ta[4]
                if attributeCategory == 7:
                    v = hex(int(v))
                entryData = {'line': 1,
                 'label': attributeName,
                 'text': '%s<br>%s' % (v, description)}
                entry = listentry.Get('LabelTextTop', entryData)
                container.append(entry)

            container.append(listentry.Get('Header', {'label': mls.UI_GENERIC_EFFECTS}))
            teffects = []
            for te in cfg.dgmtypeeffects.get(typeID, []):
                e = cfg.dgmeffects.Get(te.effectID)
                teffects.append([e, e.effectName])

            teffects.sort(lambda x, y: cmp(x[1], y[1]))
            for (e, effectName,) in teffects:
                entryData = {'label': effectName}
                entry = listentry.Get('Subheader', entryData)
                container.append(entry)
                for columnName in e.header:
                    entryData = {'line': 1,
                     'label': columnName,
                     'text': '%s' % getattr(e, columnName)}
                    entry = listentry.Get('LabelTextTop', entryData)
                    container.append(entry)





    def GetCorpLogo(self, corpID, wnd = None, parent = None):
        logo = uiutil.GetLogoIcon(itemID=corpID, parent=parent, state=uiconst.UI_NORMAL, hint=mls.UI_INFOWND_CLICKFORCORPINFO, align=uiconst.TOLEFT, pos=(0, 0, 64, 64), ignoreSize=True)
        parent.height = 64
        logo.OnClick = (self._Info__PreFormatWnd,
         wnd,
         const.typeCorporation,
         corpID)



    def GetGAVFunc(self, itemID, info):
        GAV = None
        if info.itemID is not None:
            GAV = lambda attributeID: getattr(info, cfg.dgmattribs.Get(attributeID).attributeName)
        elif itemID:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsItemLoaded(itemID):
                GAV = lambda attributeID: dogmaLocation.GetAttributeValue(itemID, attributeID)
        if GAV is None:
            GAV = lambda attributeID: getattr(info, cfg.dgmattribs.Get(attributeID).attributeName)
        return GAV



    def GetBarData(self, itemID, info, caption):
        GAV = self.GetGAVFunc(itemID, info)
        if caption == mls.UI_GENERIC_STRUCTURE:
            return {'attributeID': const.attributeHp,
             'label': caption,
             'status': max(0, GAV(const.attributeHp) - GAV(const.attributeDamage)),
             'total': GAV(const.attributeHp)}
        if caption == mls.UI_GENERIC_ARMOR:
            return {'attributeID': const.attributeDamage,
             'label': caption,
             'status': max(0, GAV(const.attributeArmorHP) - GAV(const.attributeArmorDamage)),
             'total': GAV(const.attributeArmorHP)}
        if caption == mls.UI_GENERIC_SHIELD:
            return {'attributeID': const.attributeShieldCapacity,
             'label': caption,
             'status': GAV(const.attributeShieldCharge),
             'total': GAV(const.attributeShieldCapacity)}
        if caption == mls.UI_GENERIC_CAPACITOR:
            return {'attributeID': const.attributeCapacitorCapacity,
             'label': caption,
             'status': GAV(const.attributeCharge),
             'total': GAV(const.attributeCapacitorCapacity)}



    def GetCertEntry(self, cert):
        certID = cert.certificateID
        level = getattr(cert, 'recommendationLevel', None)
        certInfo = cfg.certificates.Get(certID)
        (label, grade, descr,) = uix.GetCertificateLabel(certID)
        entry = {'line': 1,
         'label': label,
         'grade': certInfo.grade,
         'certID': certID,
         'icon': 'ui_79_64_%s' % (certInfo.grade + 1),
         'level': level,
         'hideBar': 1}
        return entry



    def DrillToLocation(self, systemID, constellationID, regionID):
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)



    def GetCertGroupList(self, certsInfo):
        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        scrolllist = []
        allCategories = sm.StartService('certificates').GetCategories(certsInfo)
        for (category, value,) in allCategories.iteritems():
            categoryObj = categoryData[category]
            data = {'GetSubContent': self.GetCertSubContent,
             'label': Tr(categoryObj.categoryName, 'cert.categories.categoryName', categoryObj.dataID),
             'groupItems': value,
             'id': ('infoCertGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked'}
            scrolllist.append((data.get('label', ''), listentry.Get('Group', data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GetCertSubContent(self, dataX, *args):
        scrolllist = []
        wnd = self.GetWnd()
        dataWnd = sm.GetService('window').GetWindow(unicode(dataX.id), create=0)
        if not dataWnd:
            for entry in wnd.sr.scroll.GetNodes():
                if entry.__guid__ != 'listentry.Group' or entry.id == dataX.id:
                    continue
                if entry.open:
                    if entry.panel:
                        entry.panel.Toggle()
                    else:
                        uicore.registry.SetListGroupOpenState(entry.id, 0)
                        entry.scroll.PrepareSubContent(entry)

        entries = self.GetCertEntries(dataX)
        return entries



    def GetCertEntries(self, data, *args):
        scrolllist = []
        highestEntries = sm.StartService('certificates').GetHighestLevelOfClass(data.groupItems)
        for each in highestEntries:
            certEntry = self.GetCertEntry(each)
            scrolllist.append((certEntry.get('label', ''), listentry.Get('CertEntry', certEntry)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GetAgentScrollGroups(self, agents, scroll):
        dudesToPrime = []
        locationsToPrime = []
        for each in agents:
            dudesToPrime.append(each.agentID)
            if each.stationID:
                locationsToPrime.append(each.stationID)
            locationsToPrime.append(each.solarsystemID)

        cfg.eveowners.Prime(dudesToPrime)
        cfg.evelocations.Prime(locationsToPrime)

        def SortFunc(level, agentID, x, y):
            if x[level] < y[level]:
                return -1
            if x[level] > y[level]:
                return 1
            xname = cfg.eveowners.Get(x[agentID]).name
            yname = cfg.eveowners.Get(y[agentID]).name
            if xname < yname:
                return -1
            if xname > yname:
                return 1
            return 0


        agents.sort(lambda x, y: SortFunc(agents.header.index('level'), agents.header.index('agentID'), x, y))
        allAgents = sm.RemoteSvc('agentMgr').GetAgents().Index('agentID')
        divisions = {}
        for each in agents:
            if allAgents[each[0]].divisionID not in divisions:
                divisions[allAgents[each[0]].divisionID] = 1

        npcDivisions = sm.GetService('agents').GetDivisions()

        def SortDivisions(npcDivisions, x, y):
            x = npcDivisions[x].divisionName.lower()
            y = npcDivisions[y].divisionName.lower()
            if x < y:
                return -1
            else:
                if x > y:
                    return 1
                return 0


        divisions = divisions.keys()
        divisions.sort(lambda x, y, npcDivisions = npcDivisions: SortDivisions(npcDivisions, x, y))
        for divisionID in divisions:
            amt = 0
            for agent in agents:
                if agent.divisionID == divisionID:
                    amt += 1

            data = {'GetSubContent': self.GetCorpAgentListSubContent,
             'label': '%s [%s]' % (npcDivisions[divisionID].divisionName.replace('&', '&amp;'), amt),
             'agentdata': (divisionID, agents),
             'id': ('AGENTDIVISIONS', divisionID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0}
            scroll.append(listentry.Get('Group', data))




    def InitVariationBottom(self, wnd):
        btns = [mls.UI_INFOWND_COMPARE,
         self.CompareTypes,
         wnd,
         81,
         uiconst.ID_OK,
         0,
         0]
        btns = uicls.ButtonGroup(btns=[btns], parent=wnd.sr.subcontainer, idx=0)
        wnd.sr.variationbtm = btns
        wnd.sr.variationbtm.state = uiconst.UI_HIDDEN



    def CompareTypes(self, wnd):
        typeWnd = sm.GetService('window').GetWindow('typecompare', decoClass=form.TypeCompare, create=1)
        typeWnd.AddEntry(wnd.sr.variationTypeDict)



    def GetBaseWarpSpeed(self, typeID, shipinfo = None):
        defaultWSM = 1.0
        defaultBWS = 3.0
        if shipinfo:
            wsm = getattr(shipinfo, 'warpSpeedMultiplier', defaultWSM)
            bws = getattr(shipinfo, 'baseWarpSpeed', defaultBWS)
        else:
            attrTypeInfo = util.IndexedRows(cfg.dgmtypeattribs.get(typeID, []), ('attributeID',))
            wsm = attrTypeInfo.get(const.attributeWarpSpeedMultiplier) or util.KeyVal(value=defaultWSM)
            bws = attrTypeInfo.get(const.attributeBaseWarpSpeed) or util.KeyVal(value=defaultBWS)
            wsm = wsm.value
            bws = bws.value
        return '%s/%s' % (util.FmtDist(max(1.0, bws) * wsm * 3 * const.AU, 2), mls.UI_GENERIC_SECONDVERYSHORT)



    def GetBaseDamageValue(self, typeID):
        bsd = None
        bad = None
        attrTypeInfo = util.IndexedRows(cfg.dgmtypeattribs.get(typeID, []), ('attributeID',))
        vals = []
        for attrID in [const.attributeEmDamage,
         const.attributeThermalDamage,
         const.attributeKineticDamage,
         const.attributeExplosiveDamage]:
            if attrID in attrTypeInfo:
                vals.append(attrTypeInfo[attrID].value)

        if len(vals) == 4:
            bsd = (vals[0] * 1.0 + vals[1] * 0.8 + vals[2] * 0.6 + vals[3] * 0.4, 69)
            bad = (vals[0] * 0.4 + vals[1] * 0.65 + vals[2] * 0.75 + vals[3] * 0.9, 68)
        return (bsd, bad)



    def FormatAsFactoryTime(self, value):
        strOut = ''
        strAdd = ''
        if value < 0:
            strAdd = ' %s' % mls.UI_GENERIC_OVERDUE
            value = -value
        secondsPerMinute = 60
        secondsPerHour = 3600
        secondsPerDay = 86400
        secondsPerWeek = 604800
        secondsPerYear = 31556926
        t = value
        years = t / secondsPerYear
        t -= years * secondsPerYear
        weeks = t / secondsPerWeek
        t -= weeks * secondsPerWeek
        days = t / secondsPerDay
        t -= days * secondsPerDay
        hours = t / secondsPerHour
        t -= hours * secondsPerHour
        minutes = t / secondsPerMinute
        t -= minutes * secondsPerMinute
        seconds = t
        timeUnits = [[years, mls.UI_GENERIC_YEAR, mls.UI_GENERIC_YEARS],
         [weeks, mls.UI_GENERIC_WEEK, mls.UI_GENERIC_WEEKS],
         [days, mls.UI_GENERIC_DAY, mls.UI_GENERIC_DAYS],
         [hours, mls.UI_GENERIC_HOUR, mls.UI_GENERIC_HOURS],
         [minutes, mls.UI_GENERIC_MINUTE, mls.UI_GENERIC_MINUTES]]
        SECOND = 10000000
        MINUTE = 60 * SECOND
        if value < 10 * secondsPerMinute:
            timeUnits.append([seconds, mls.UI_GENERIC_SECOND, mls.UI_GENERIC_SECONDS])
        for (timeUnit, timeUnitName, timeUnitNamePlural,) in timeUnits:
            (timeUnitName, timeUnitNamePlural,) = (timeUnitName.title(), timeUnitNamePlural.title())
            if timeUnit > 0:
                if len(strOut) > 0:
                    strOut += ', '
                if timeUnit == 1:
                    strOut += '1 %s' % timeUnitName
                elif timeUnit > 1:
                    strOut += '%s %s' % (timeUnit, timeUnitNamePlural)

        if len(strAdd):
            strOut += strAdd
        if strOut == '':
            strOut = mls.UI_GENERIC_LESSTHANAMINUTE
        return strOut



    def GetBOMSubContent(self, nodedata, *args):
        scrolllist = []
        if mls.UI_GENERIC_SKILLS in [nodedata.label, nodedata.Get('cleanLabel', None)]:
            skills = []
            for each in nodedata.groupItems:
                skills.append((each[0], (each[2], each[3])))

            if skills:
                skills = uiutil.SortListOfTuples(skills)
                self.GetReqSkillInfo(None, scrolllist, skills)
        else:
            for each in nodedata.groupItems:
                entry = listentry.Get('Item', {'itemID': None,
                 'typeID': each[2],
                 'label': each[1],
                 'getIcon': 1})
                scrolllist.append((each[0], entry))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            if eve.session.role & service.ROLE_GML == service.ROLE_GML:
                scrolllist.append(listentry.Get('Divider'))
                scrolllist.append(listentry.Get('Button', {'label': mls.UI_INFOWND_BOMTEXT2,
                 'caption': mls.UI_CMD_CREATE,
                 'OnClick': self.DoCreateMaterials,
                 'args': (nodedata.Get('commands', None), '', 10)}))
        return scrolllist



    def GetKillsRecentKills(self, num, startIndex):
        shipKills = sm.RemoteSvc('charMgr').GetRecentShipKillsAndLosses(num, startIndex)
        return [ k for k in shipKills if k.finalCharacterID == eve.session.charid ]



    def GetKillsRecentLosses(self, num, startIndex):
        shipKills = sm.RemoteSvc('charMgr').GetRecentShipKillsAndLosses(num, startIndex)
        return [ k for k in shipKills if k.victimCharacterID == eve.session.charid ]



    def GetKillRightsSubContent(self):
        scrolllist = []
        killRights = sm.GetService('consider').GetKillRights()
        killedRights = sm.GetService('consider').GetKilledRights()
        if killRights:
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_INFOWND_CANKILL}))
            for (ownerID, t,) in killRights.iteritems():
                scrolllist.append(listentry.Get('User', {'charID': ownerID,
                 'killTime': t}))

        if killedRights:
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_INFOWND_CANBEKILLEDBY}))
            for (ownerID, t,) in killedRights.iteritems():
                scrolllist.append(listentry.Get('User', {'charID': ownerID,
                 'killTime': t}))

        return scrolllist



    def GetAllianceHistorySubContent(self, itemID):
        scrolllist = []
        allianceHistory = sm.RemoteSvc('allianceRegistry').GetEmploymentRecord(itemID)

        def AddToScroll(**data):
            scrolllist.append(listentry.Get('LabelTextTop', data))


        if len(allianceHistory) == 0:
            AddToScroll(line=True, text='', label=mls.UI_CORP_NORECORDSFOUND, typeID=None, itemID=None)
        lastQuit = None
        for allianceRec in allianceHistory[:-1]:
            if allianceRec.allianceID is None:
                lastQuit = allianceRec.startDate
            else:
                alliance = cfg.eveowners.Get(allianceRec.allianceID)
                if allianceRec.startDate:
                    sd = util.FmtDate(allianceRec.startDate, 'ln')
                else:
                    sd = mls.UI_GENERIC_UNKNOWN
                if lastQuit:
                    ed = util.FmtDate(lastQuit, 'ln')
                else:
                    ed = mls.UI_GENERIC_THISDAY
                span = mls.UI_INFOWND_FROMTO % {'from': '<b>%s</b>' % sd,
                 'to': '<b>%s</b>' % ed}
                if allianceRec.deleted:
                    nameTxt = '%s (%s)' % (alliance.name, mls.UI_GENERIC_CLOSED)
                else:
                    nameTxt = alliance.name
                AddToScroll(line=True, label=mls.UI_GENERIC_ALLIANCE, text='%s %s' % (nameTxt, span), typeID=alliance.typeID, itemID=allianceRec.allianceID)
                lastQuit = None

        if len(allianceHistory) > 1:
            scrolllist.append(listentry.Get('Divider'))
        if len(allianceHistory) >= 1:
            AddToScroll(line=True, label=mls.UI_CORP_CORPORATIONFOUNDED, text=util.FmtDate(allianceHistory[-1].startDate, 'ln'), typeID=None, itemID=None)
        return scrolllist



    def GetEmploymentHistorySubContent(self, itemID):
        scrolllist = []
        employmentHistory = sm.RemoteSvc('corporationSvc').GetEmploymentRecord(itemID)
        nextDate = mls.UI_GENERIC_THISDAY
        for job in employmentHistory:
            corp = cfg.eveowners.Get(job.corporationID)
            if job.deleted:
                nameText = '%s (%s)' % (corp.name, mls.UI_GENERIC_CLOSED)
            else:
                nameText = corp.name
            date = util.FmtDate(job.startDate, 'ls')
            span = mls.UI_INFOWND_FROMTO % {'from': '<b>%s</b>' % date,
             'to': '<b>%s</b>' % nextDate}
            nextDate = date
            scrolllist.append(listentry.Get('LabelTextTop', {'line': True,
             'label': mls.UI_GENERIC_CORPORATION,
             'text': '%s %s' % (nameText, span),
             'typeID': corp.typeID,
             'itemID': job.corporationID}))

        return scrolllist



    def GetAllianceMembersSubContent(self, itemID):
        members = sm.RemoteSvc('allianceRegistry').GetAllianceMembers(itemID)
        cfg.eveowners.Prime([ m.corporationID for m in members ])
        scrolllist = []
        for m in members:
            corp = cfg.eveowners.Get(m.corporationID)
            data = {'line': True,
             'label': mls.UI_GENERIC_CORPORATION,
             'text': corp.name,
             'typeID': corp.typeID,
             'itemID': m.corporationID}
            scrolllist.append(listentry.Get('LabelTextTop', data))

        return scrolllist



    def GetCorpAgentListSubContent(self, tmp, *args):
        (divisionID, agents,) = tmp.agentdata
        scrolllist = []
        scrolllist.append(listentry.Get('Header', {'label': mls.UI_INFOWND_AVAILABLETOYOU}))
        noadd = 1
        for agent in agents:
            if agent.divisionID != divisionID:
                continue
            isLimitedToFacWar = False
            if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and sm.StartService('facwar').GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                isLimitedToFacWar = True
            if sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) and isLimitedToFacWar == False:
                scrolllist.append(listentry.Get('User', {'charID': agent.agentID,
                 'defaultDivisionID': agent.divisionID}))
                noadd = 0

        if noadd:
            scrolllist.pop(-1)
        scrolllist.append(listentry.Get('Header', {'label': mls.UI_INFOWND_NOTAVAILABLETOYOU}))
        noadd = 1
        for agent in agents:
            if agent.divisionID != divisionID:
                continue
            isLimitedToFacWar = False
            if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and sm.StartService('facwar').GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                isLimitedToFacWar = True
            if not sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) or isLimitedToFacWar == True:
                scrolllist.append(listentry.Get('User', {'charID': agent.agentID,
                 'defaultDivisionID': agent.divisionID}))
                noadd = 0

        if noadd:
            scrolllist.pop(-1)
        return scrolllist



    def __GetIllegalityString(self, illegality):
        txt = ''
        if illegality.standingLoss > 0.0:
            txt += ', %s %-2.2f' % (mls.UI_INFOWND_STANDINGLOSS, illegality.standingLoss)
        if illegality.confiscateMinSec <= 1.0:
            txt += ', %s >= %-2.2f' % (mls.UI_INFOWND_CONFISCATIONINSEC, max(illegality.confiscateMinSec, 0.0))
        if illegality.fineByValue > 0.0:
            txt += ', ' + mls.UI_INFOWND_FINEOFESTMARKETVALUE % {'value': '%-2.2f' % (illegality.fineByValue * 100.0)}
        if illegality.attackMinSec <= 1.0:
            txt += ', %s >= %-2.2f' % (mls.UI_INFOWND_ATTACKINSEC, max(illegality.attackMinSec, 0.0))
        if txt:
            txt = ':  ' + txt[2:]
        return txt



    def GetInvTypeInfo(self, typeID, scrolllist, filterValue, attrList):
        invTypeInfo = cfg.invtypes.Get(typeID)
        for attrID in attrList:
            attrTypeInfo = cfg.dgmattribs.Get(attrID)
            value = filterValue(getattr(invTypeInfo, attrTypeInfo.attributeName, None))
            if value is None:
                continue
            if not attrTypeInfo.published:
                continue
            if attrID == const.attributeVolume:
                packagedVolume = cfg.GetTypeVolume(typeID, 1)
                if value != packagedVolume:
                    text = '%s (%s %s)' % (value, packagedVolume, mls.UI_GENERIC_PACKAGED)
                else:
                    text = '%s %s' % (value, self.FormatUnit(attrTypeInfo.unitID))
            else:
                text = '%s %s' % (value, self.FormatUnit(attrTypeInfo.unitID))
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': attrTypeInfo.displayName,
             'text': text,
             'iconID': attrTypeInfo.iconID}))




    def GetMetaParentTypeID(self, typeID):
        parentTypeID = None
        if typeID in cfg.invmetatypesByParent:
            parentTypeID = typeID
        elif typeID in cfg.invmetatypes:
            parentTypeID = cfg.invmetatypes.Get(typeID).parentTypeID
        return parentTypeID



    def GetMetaTypeInfo(self, typeID, scrolllist, wnd):
        invTypeInfo = self.GetMetaTypesFromTypeID(typeID)
        wnd.sr.variationTypeDict = []
        sortByGroupID = {}
        sortHeaders = []
        if invTypeInfo:
            for each in invTypeInfo:
                if each.metaGroupID not in sortByGroupID:
                    sortByGroupID[each.metaGroupID] = []
                    sortHeaders.append((each.metaGroupID, each.metaGroupID))
                invType = cfg.invtypes.Get(each.typeID)
                sortByGroupID[each.metaGroupID].append((invType.name, (each, invType)))

        sortHeaders = uiutil.SortListOfTuples(sortHeaders)
        for (i, metaGroupID,) in enumerate(sortHeaders):
            sub = sortByGroupID[metaGroupID]
            sub = uiutil.SortListOfTuples(sub)
            if i > 0:
                scrolllist.append(listentry.Get('Divider'))
            scrolllist.append(listentry.Get('Header', {'line': metaGroupID,
             'label': cfg.invmetagroups.Get(metaGroupID).name,
             'text': None}))
            for (metaType, invType,) in sub:
                wnd.sr.variationTypeDict.append(invType)
                scrolllist.append(listentry.Get('Item', {'GetMenu': None,
                 'itemID': None,
                 'typeID': invType.typeID,
                 'label': invType.typeName,
                 'getIcon': 1}))





    def GetMetaTypesFromTypeID(self, typeID, groupOnly = 0):
        tmp = None
        if typeID in cfg.invmetatypesByParent:
            tmp = copy.deepcopy(cfg.invmetatypesByParent[typeID])
        grp = cfg.invmetagroups.Get(1)
        if not tmp:
            if typeID in cfg.invmetatypes:
                tmp = cfg.invmetatypes.Get(typeID)
            if tmp:
                grp = cfg.invmetagroups.Get(tmp.metaGroupID)
                tmp = self.GetMetaTypesFromTypeID(tmp.parentTypeID)
        else:
            metaGroupID = tmp[0].metaGroupID
            if metaGroupID != 14:
                metaGroupID = 1
            else:
                grp = cfg.invmetagroups.Get(14)
            tmp.append(blue.DBRow(tmp.header, [tmp[0].parentTypeID, tmp[0].parentTypeID, metaGroupID]))
        if groupOnly:
            return grp
        else:
            return tmp



    def GetAttrItemInfo(self, itemID, typeID, scrolllist, attrList = None, banAttrs = []):
        info = sm.GetService('godma').GetItem(itemID)
        if info:
            attrDict = self.GetAttrDict(typeID)
            for each in info.displayAttributes:
                attrDict[each.attributeID] = each.value

            typeVolume = cfg.GetTypeVolume(typeID, 1)
            if const.attributeVolume in attrDict and attrDict[const.attributeVolume] != typeVolume:
                fmtUnit = self.FormatUnit(cfg.dgmattribs.Get(const.attributeVolume).unitID)
                attrDict[const.attributeVolume] = '%s %s (%s %s %s)' % (attrDict[const.attributeVolume],
                 fmtUnit,
                 typeVolume,
                 fmtUnit,
                 mls.UI_GENERIC_PACKAGED)
            return self.GetAttrInfo(attrDict, scrolllist, attrList, banAttrs=banAttrs, itemID=itemID)
        else:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsItemLoaded(itemID):
                attrDict = self.GetAttrDict(typeID)
                attrDict.update(dogmaLocation.GetDisplayAttributes(itemID, attrDict.keys()))
                return self.GetAttrInfo(attrDict, scrolllist, attrList, banAttrs=banAttrs, itemID=itemID)
            return self.GetAttrTypeInfo(typeID, scrolllist, attrList, banAttrs=banAttrs, itemID=itemID)



    def GetAttrTypeInfo(self, typeID, scrolllist, attrList = None, attrValues = None, banAttrs = [], itemID = None):
        return self.GetAttrInfo(self.GetAttrDict(typeID), scrolllist, attrList, attrValues, banAttrs, itemID=itemID, typeID=typeID)



    def GetAttrInfo(self, attrdict, scrolllist, attrList = None, attrValues = None, banAttrs = [], itemID = None, typeID = None):
        if attrValues:
            for each in attrValues.displayAttributes:
                attrdict[each.attributeID] = each.value

        attrList = attrList or attrdict.keys()

        def GetAttr(attrID):
            if attrID not in banAttrs and attrID in attrdict:
                self.GetAttr(attrID, attrdict[attrID], scrolllist, itemID, typeID=typeID)


        order = self.GetAttributeOrder()
        for attrID_ in order:
            if attrID_ in attrList:
                GetAttr(attrID_)

        for attrID_ in attrList:
            if attrID_ not in order:
                GetAttr(attrID_)




    def GetAttrDict(self, typeID):
        ret = {}
        for each in cfg.dgmtypeattribs.get(typeID, []):
            attribute = cfg.dgmattribs.Get(each.attributeID)
            if attribute.attributeCategory == 9:
                ret[each.attributeID] = getattr(cfg.invtypes.Get(typeID), attribute.attributeName)
            else:
                ret[each.attributeID] = each.value

        invType = cfg.invtypes.Get(typeID)
        if not ret.has_key(const.attributeCapacity) and invType.capacity:
            ret[const.attributeCapacity] = invType.capacity
        if invType.categoryID in (const.categoryCharge, const.categoryModule):
            if not ret.has_key(const.attributeVolume) and invType.volume:
                ret[const.attributeVolume] = '%s m3' % util.FmtAmt(invType.volume, showFraction=1)
        if invType.categoryID in (const.categoryPlanetaryInteraction,) and invType.groupID not in (const.groupPlanetaryLinks, const.groupPlanetaryCustomsOffices):
            if not ret.has_key(const.attributeVolume) and invType.volume:
                value = '%s m3' % util.FmtAmt(invType.volume, showFraction=1)
                packagedVolume = cfg.GetTypeVolume(typeID, 1)
                if invType.volume != packagedVolume:
                    value += ' (%s m3 %s)' % (util.FmtAmt(packagedVolume, showFraction=1), mls.UI_GENERIC_PACKAGED)
                ret[const.attributeVolume] = value
        if invType.categoryID == const.categoryShip:
            if not ret.has_key(const.attributeMass) and invType.mass:
                ret[const.attributeMass] = invType.mass
            if not ret.has_key(const.attributeVolume) and invType.volume:
                value = '%s m3' % util.FmtAmt(invType.volume, showFraction=1)
                packagedVolume = cfg.GetTypeVolume(typeID, 1)
                if invType.volume != packagedVolume:
                    value += ' (%s m3 %s)' % (util.FmtAmt(packagedVolume, showFraction=1), mls.UI_GENERIC_PACKAGED)
                ret[const.attributeVolume] = value
        attrInfo = sm.GetService('godma').GetType(typeID)
        for each in attrInfo.displayAttributes:
            ret[each.attributeID] = each.value

        return ret



    def GetFormatAndValue(self, attributeType, value):
        attrUnit = self.FormatUnit(attributeType.unitID)
        if attributeType.unitID == const.unitGroupID:
            value = '%s' % cfg.invgroups.Get(value).name
        elif attributeType.unitID == const.unitTypeID:
            value = '%s' % cfg.invtypes.Get(value).name
        elif attributeType.unitID == const.unitSizeclass:
            value = '%s' % [mls.UI_GENERIC_SMALL,
             mls.UI_GENERIC_MEDIUM,
             mls.UI_GENERIC_LARGE,
             mls.UI_GENERIC_XLARGE][(int(value) - 1)]
        elif attributeType.unitID == const.unitAttributeID:
            attrInfo2 = cfg.dgmattribs.Get(value)
            value = attrInfo2.displayName or attrInfo2.attributeName
        elif attributeType.attributeID == const.attributeVolume:
            value = value
        elif attributeType.unitID == const.unitLevel:
            value = '%s %s' % (attrUnit, util.FmtAmt(value))
        elif attributeType.unitID == const.unitBoolean:
            if int(value) == 1:
                value = mls.UI_GENERIC_TRUE
            else:
                value = mls.UI_GENERIC_FALSE
        elif attributeType.unitID == const.unitSlot:
            value = '%s %s' % (attrUnit, util.FmtAmt(value))
        elif attributeType.unitID == const.unitBonus:
            if value >= 0:
                value = '%s%s' % (attrUnit, value)
        elif attributeType.unitID == const.unitGender:
            value = [mls.UI_GENERIC_MALE, mls.UI_GENERIC_UNISEX, mls.UI_GENERIC_FEMALE][(int(value) - 1)]
        else:
            value = '%s %s' % (self.FormatValue(value, attributeType.unitID), attrUnit)
        return value



    def GetAttr(self, id_, value, scrolllist, itemID = None, typeID = None):
        type_ = cfg.dgmattribs.Get(id_)
        if not type_.published or not value:
            return 
        iconID = type_.iconID
        infoTypeID = None
        if not iconID:
            if type_.unitID == const.unitTypeID:
                iconID = cfg.invtypes.Get(value).iconID
                infoTypeID = value
            if type_.unitID == const.unitGroupID:
                iconID = cfg.invgroups.Get(value).iconID
            if type_.unitID == const.unitAttributeID:
                attrInfo2 = cfg.dgmattribs.Get(value)
                iconID = attrInfo2.iconID
        value = self.GetFormatAndValue(type_, value)
        if itemID and infoTypeID and typeID != infoTypeID:
            itemID = None
        listItem = listentry.Get('LabelTextTop', {'attributeID': id_,
         'OnClick': (self.OnAttributeClick, id_, itemID),
         'line': 1,
         'label': type_.displayName,
         'text': value,
         'iconID': iconID,
         'typeID': infoTypeID,
         'itemID': itemID})
        scrolllist.append(listItem)



    def OnAttributeClick(self, id_, itemID):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not ctrl:
            return 
        if not shift and itemID is not None and (itemID >= const.minPlayerItem or util.IsCharacter(itemID)):
            sm.GetService('godma').LogAttribute(itemID, id_)
        if eve.session.role & service.ROLE_CONTENT == service.ROLE_CONTENT and ctrl and shift:
            self.GetUrlAdamDogmaAttribute(id_)



    def GetUrlAdamDogmaAttribute(self, id_):
        uthread.new(self.ClickURL, 'http://adam:50001/gd/type.py?action=DogmaModifyAttributeForm&attributeID=%s' % id_)



    def ClickURL(self, url, *args):
        blue.os.ShellExecute(url)



    def GetRequiredSkills(self, typeID):
        lst = []
        attrDict = self.GetAttrDict(typeID)
        for i in xrange(1, 7):
            skillID = attrDict.get(getattr(const, 'attributeRequiredSkill%s' % i), None)
            if skillID is not None and getattr(const, 'attributeRequiredSkill%sLevel' % i) in attrDict:
                lvl = attrDict.get(getattr(const, 'attributeRequiredSkill%sLevel' % i), 1.0)
                if lvl:
                    lst.append((skillID, lvl))

        return lst



    def GetSkillAttrs(self):
        skillAttrs = [ getattr(const, 'attributeRequiredSkill%s' % i, None) for i in xrange(1, 7) if hasattr(const, 'attributeRequiredSkill%s' % i) ] + [ getattr(const, 'attributeRequiredSkill%sLevel' % i, None) for i in xrange(1, 7) if hasattr(const, 'attributeRequiredSkill%sLevel' % i) ]
        return skillAttrs



    def GetReqCertInfo(self, typeID, scrolllist, reqCertificates = []):
        if session.charid is None:
            return 
        for certificateID in reqCertificates:
            (label, grade, desc,) = uix.GetCertificateLabel(certificateID)
            haveCert = sm.StartService('certificates').HaveCertificate(certificateID)
            inProgress = None
            hasPrereqs = None
            certInfo = cfg.certificates.Get(certificateID)
            if not haveCert:
                hasPrereqs = sm.StartService('certificates').HasPrerequisites(certificateID)
                if not hasPrereqs:
                    inProgress = sm.StartService('certificates').IsInProgress(certificateID)
            entry = {'line': 1,
             'text': '%s - %s' % (label, grade),
             'indent': 1,
             'haveCert': haveCert,
             'inProgress': inProgress,
             'hasPrereqs': hasPrereqs,
             'certID': certificateID,
             'grade': certInfo.grade}
            scrolllist.append(listentry.Get('CertTreeEntry', entry))




    def GetSchematicAttributes(self, schematicID, cycleTime, scrolllist):
        time = util.FmtTimeInterval(cycleTime * SEC, 'minute')
        scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
         'label': mls.UI_PI_GENERIC_CYCLETIME,
         'text': time,
         'iconID': 1392}))
        scrolllist.append(listentry.Get('Header', data=util.KeyVal(label=mls.UI_PI_CANBEUSED)))
        pinTypes = []
        for pinRow in cfg.schematicspinmap.get(schematicID, []):
            typeName = cfg.invtypes.Get(pinRow.pinTypeID).typeName
            data = util.KeyVal(label='%s' % typeName, typeID=pinRow.pinTypeID, itemID=None, getIcon=1)
            pinTypes.append((data.label, listentry.Get('Item', data=data)))

        pinTypes = uiutil.SortListOfTuples(pinTypes)
        scrolllist += pinTypes



    def GetSchematicTypeScrollList(self, schematicID, scrolllist):
        inputs = []
        outputs = []
        for typeInfo in cfg.schematicstypemap.get(schematicID, []):
            typeName = cfg.invtypes.Get(typeInfo.typeID).typeName
            data = util.KeyVal(label=mls.UI_PI_UNITSOFTYPE % {'typeName': typeName,
             'quantity': typeInfo.quantity}, typeID=typeInfo.typeID, itemID=None, getIcon=1, quantity=typeInfo.quantity)
            if typeInfo.isInput:
                inputs.append(data)
            else:
                outputs.append(data)

        scrolllist.append(listentry.Get('Header', data=util.KeyVal(label=mls.UI_PI_INPUT)))
        for data in inputs:
            scrolllist.append(listentry.Get('Item', data=data))

        scrolllist.append(listentry.Get('Header', data=util.KeyVal(label=mls.UI_PI_OUTPUT)))
        for data in outputs:
            scrolllist.append(listentry.Get('Item', data=data))




    def GetReqSkillInfo(self, typeID, scrolllist, reqSkills = [], showHeaders = False):
        i = 1
        commands = []
        skills = None
        if typeID is not None:
            skills = self.GetRequiredSkills(typeID)
        if reqSkills:
            skills = reqSkills
        if skills is None:
            return 
        for (skillID, lvl,) in skills:
            if showHeaders or typeID is not None:
                attr = cfg.dgmattribs.Get(getattr(const, 'attributeRequiredSkill%s' % i))
                scrolllist.append(listentry.Get('Header', {'line': 1,
                 'label': attr.displayName}))
            ret = self.DrawSkillTree(skillID, lvl, scrolllist, 0)
            scrolllist.append(listentry.Get('Divider'))
            commands = commands + ret
            i += 1

        cmds = {}
        for (typeID, level,) in commands:
            (typeID, level,) = (int(typeID), int(level))
            currentLevel = cmds.get(typeID, 0)
            cmds[typeID] = max(currentLevel, level)

        if i > 1 and eve.session.role & service.ROLE_GMH == service.ROLE_GMH:
            scrolllist.append(listentry.Get('Button', {'label': mls.UI_INFOWND_REQSKILLGMH,
             'caption': mls.UI_CMD_GIVE,
             'OnClick': self.DoGiveSkills,
             'args': (cmds,)}))
            scrolllist.append(listentry.Get('Divider'))



    def GetRecommendedFor(self, certID, scrolllist):
        recommendedFor = sm.StartService('certificates').GetCertificateRecommendationsFromCertificateID(certID)
        recommendedGroups = {}
        for each in recommendedFor:
            typeID = each.shipTypeID
            groupID = cfg.invtypes.Get(typeID).groupID
            current = recommendedGroups.get(groupID, [])
            current.append(typeID)
            recommendedGroups[groupID] = current

        scrolllist2 = []
        for (groupID, value,) in recommendedGroups.iteritems():
            label = cfg.invgroups.Get(groupID).name
            data = {'GetSubContent': self.GetEntries,
             'label': label,
             'groupItems': value,
             'id': ('cert_shipGroups', groupID),
             'sublevel': 0,
             'showlen': 1,
             'showicon': 'hide',
             'state': 'locked'}
            scrolllist2.append((label, listentry.Get('Group', data)))

        scrolllist2 = uiutil.SortListOfTuples(scrolllist2)
        scrolllist += scrolllist2



    def GetEntries(self, data, *args):
        scrolllist = []
        for each in data.groupItems:
            entry = self.CreateEntry(each)
            scrolllist.append(entry)

        return scrolllist



    def CreateEntry(self, typeID, *args):
        entry = util.KeyVal()
        entry.line = 1
        entry.label = cfg.invtypes.Get(typeID).name
        entry.sublevel = 1
        entry.showinfo = 1
        entry.typeID = typeID
        return listentry.Get('Generic', data=entry)



    def DoGiveSkills(self, cmds, button):
        cntFrom = 1
        cntTo = len(cmds) + 1
        sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_GMGIVESKILL, '', cntFrom, cntTo)
        for (typeID, level,) in cmds.iteritems():
            invType = cfg.invtypes.Get(typeID)
            cntFrom = cntFrom + 1
            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_GMGIVESKILL, mls.SKILL_TRAINING_COMPLETE_MAIL_BODY % (invType.typeName, level), cntFrom, cntTo)
            sm.RemoteSvc('slash').SlashCmd('/giveskill me %s %s' % (typeID, level))

        sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_DONE, '', cntTo, cntTo)



    def DoCreateMaterials(self, commands, header, qty, button):
        runs = {'qty': qty}
        hdr = mls.UI_INFOWND_BOMTEXT2
        if header:
            hdr = header
        if qty > 1:
            runs = uix.QtyPopup(100000, 1, qty, None, hdr)
        if runs is not None and runs.has_key('qty') and runs['qty'] > 0:
            cntFrom = 1
            cntTo = len(commands) + 1
            sm.GetService('loading').ProgressWnd(mls.CMD_GIVELOOT, '', cntFrom, cntTo)
            for (typeID, quantity,) in commands:
                invType = cfg.invtypes.Get(typeID)
                cntFrom = cntFrom + 1
                actualQty = quantity * runs['qty']
                qtyText = [mls.UI_STATION_TEXT55, mls.UI_STATION_TEXT54][(actualQty > 1)] % {'quantity': quantity * runs['qty'],
                 'typename': invType.typeName}
                sm.GetService('loading').ProgressWnd(mls.CMD_GIVELOOT, qtyText, cntFrom, cntTo)
                if actualQty > 0:
                    sm.RemoteSvc('slash').SlashCmd('/create %s %s' % (typeID, actualQty))

            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_DONE, '', cntTo, cntTo)



    def DrawSkillTree(self, typeID, lvl, scrolllist, indent, done = None, firstID = None):
        thisSet = [(typeID, lvl)]
        if done is None:
            done = []
        if firstID is None:
            firstID = typeID
        godmaCharItem = sm.GetService('godma').GetItem(eve.session.charid)
        skills = None
        if hasattr(godmaCharItem, 'skills'):
            skills = godmaCharItem.skills
        data = {'line': 1,
         'text': '%s %s %s' % (cfg.invtypes.Get(typeID).name, mls.UI_GENERIC_LEVEL, ['-',
                   'I',
                   'II',
                   'III',
                   'IV',
                   'V'][min(5, int(lvl))]),
         'skills': skills,
         'typeID': typeID,
         'lvl': lvl,
         'indent': indent + 1}
        scrolllist.append(listentry.Get('SkillTreeEntry', data))
        done.append(typeID)
        current = typeID
        for (typeID, lvl,) in self.GetRequiredSkills(typeID):
            if typeID == current:
                log.LogWarn('Here I have skill which has it self as required skill... skillTypeID is ' + str(typeID))
                continue
            newSet = self.DrawSkillTree(typeID, lvl, scrolllist, indent + 1, done, firstID)
            thisSet = thisSet + newSet

        return thisSet



    def GetEffectTypeInfo(self, typeID, scrolllist, effList):
        thisTypeEffects = cfg.dgmtypeeffects.get(typeID, [])
        for effectID in effList:
            itemDgmEffect = self.TypeHasEffect(effectID, thisTypeEffects)
            if not itemDgmEffect:
                continue
            effTypeInfo = cfg.dgmeffects.Get(effectID)
            if effTypeInfo.published:
                scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
                 'label': effTypeInfo.displayName,
                 'text': effTypeInfo.description,
                 'iconID': effTypeInfo.iconID}))




    def FilterZero(self, value):
        if value == 0:
            return None
        return value



    def FormatUnit(self, unitID, fmt = 'd'):
        if unitID == const.unitTime:
            return ''
        if unitID == const.unitLength:
            return ''
        if unitID in cfg.dgmunits and fmt == 'd':
            u = cfg.dgmunits.Get(unitID)
            return Tr(u.displayName, 'dogma.units.displayName', u.dataID)
        return ''



    def FormatValue(self, value, unitID = None):
        if value is None:
            return 
        if unitID == const.unitTime:
            return util.FmtDate(long(value * 10000.0), 'll')
        if unitID == const.unitMilliseconds:
            return '%.2f' % (value / 1000.0)
        if unitID in (const.unitInverseAbsolutePercent, const.unitInversedModifierPercent):
            value = 100 - value * 100
        if unitID == const.unitModifierPercent:
            value = abs(value * 100 - 100) * [1, -1][(value < 1.0)]
        if unitID == const.unitLength:
            return util.FmtDist2(value)
        if unitID == const.unitAbsolutePercent:
            value = value * 100
        if unitID == const.unitHour:
            return util.FmtDate(long(value * const.HOUR), 'll')
        if unitID == const.unitMoney:
            return util.FmtAmt(value)
        if type(value) is str:
            value = eval(value)
        if type(value) is not str and value - int(value) == 0:
            return util.FmtAmt(value)
        if unitID == const.unitAttributePoints:
            return round(value, 1)
        return value



    def TypeHasEffect(self, effectID, itemEffectTypeInfo = None, typeID = None):
        if itemEffectTypeInfo is None:
            itemEffectTypeInfo = cfg.dgmtypeeffects.get(typeID, [])
        for itemDgmEffect in itemEffectTypeInfo:
            if itemDgmEffect.effectID == effectID:
                return itemDgmEffect

        return 0



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBloodlineByTypeID(self, typeID):
        if not hasattr(self, 'bloodlines'):
            bls = {}
            for each in sm.GetService('cc').GetData('bloodlines'):
                name = each.bloodlineName.replace('-', '')
                bls[util.LookupConstValue('typeCharacter%s' % name)] = util.LookupConstValue('bloodline%s' % name)

            self.bloodlines = bls
        return sm.GetService('cc').GetData('bloodlines', ['bloodlineID', self.bloodlines[typeID]])



    def Load(self, passedargs, *args):
        listtype = None
        if type(passedargs) == types.TupleType:
            if len(passedargs) == 3:
                (wnd, listtype, funcName,) = passedargs
                func = getattr(self, 'Load%s' % funcName, None)
                if func:
                    apply(func, (wnd,))
                elif listtype in wnd.sr.data:
                    wnd.sr.scroll.Load(contentList=wnd.sr.data[listtype]['items'], headers=wnd.sr.data[listtype]['headers'])
            elif len(passedargs) == 4:
                (wnd, listtype, funcName, string,) = passedargs
                if listtype == 'readOnlyText':
                    uicore.uilib.RecalcWindows()
                    wnd.sr.descedit.sr.window = wnd
                    wnd.sr.descedit.SetValue(string.replace('\n', '<br>'), scrolltotop=1)
                elif listtype == 'selectSubtab':
                    (wnd, listtype, string, subtabgroup,) = passedargs
                    subtabgroup.AutoSelect()
        else:
            wnd = passedargs
            wnd.sr.scroll.Clear()
        variationBtm = getattr(wnd.sr, 'variationbtm', None)
        if variationBtm is not None:
            if listtype == mls.UI_GENERIC_VARIATIONS:
                wnd.sr.variationbtm.state = uiconst.UI_PICKCHILDREN
            else:
                wnd.sr.variationbtm.state = uiconst.UI_HIDDEN



    def GetSubTabs(self, listtype, infotabs):
        for (_listtype, subtabs,) in infotabs:
            if _listtype == listtype:
                return subtabs

        return []



    def LoadNotes(self, wnd):
        if not wnd.sr.data[mls.UI_GENERIC_NOTES]['inited']:
            itemID = wnd.sr.itemID
            oldnotes = ''
            if wnd.sr.isCharacter and itemID:
                oldnotes = sm.RemoteSvc('charMgr').GetNote(itemID)
            wnd.sr.notesedit.SetValue(oldnotes, scrolltotop=1)
            setattr(wnd.sr, 'oldnotes', oldnotes)
            wnd.sr.data[mls.UI_GENERIC_NOTES]['inited'] = 1



    def LoadEmploymentHistory(self, wnd):
        self.LoadGeneric(wnd, mls.UI_GENERIC_EMPLOYMENTHIST, self.GetEmploymentHistorySubContent)



    def LoadAllianceHistory(self, wnd):
        self.LoadGeneric(wnd, mls.UI_GENERIC_ALLIANCEHIST, self.GetAllianceHistorySubContent)



    def LoadAllianceMembers(self, wnd):
        self.LoadGeneric(wnd, mls.UI_GENERIC_MEMBERS, self.GetAllianceMembersSubContent)



    def LoadGeneric(self, wnd, label, GetSubContent):
        if not wnd.sr.data[label]['inited']:
            wnd.sr.data[label]['items'].extend(GetSubContent(wnd.sr.itemID))
            wnd.sr.data[label]['inited'] = True
        wnd.sr.scroll.Load(fixedEntryHeight=27, contentList=wnd.sr.data[label]['items'])



    def LoadFuelRequirements(self, wnd):
        if not wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['inited']:
            l = [(1, mls.UI_GENERIC_ONLINE),
             (2, mls.UI_GENERIC_POWER),
             (3, mls.UI_GENERIC_CPU),
             (4, mls.UI_GENERIC_REINFORCED)]
            cycle = sm.GetService('godma').GetType(wnd.sr.typeID).posControlTowerPeriod
            rs = sm.RemoteSvc('posMgr').GetControlTowerFuelRequirements()
            controlTowerResourcesByTypePurpose = {}
            for entry in rs:
                if not controlTowerResourcesByTypePurpose.has_key(entry.controlTowerTypeID):
                    controlTowerResourcesByTypePurpose[entry.controlTowerTypeID] = {entry.purpose: [entry]}
                elif not controlTowerResourcesByTypePurpose[entry.controlTowerTypeID].has_key(entry.purpose):
                    controlTowerResourcesByTypePurpose[entry.controlTowerTypeID][entry.purpose] = [entry]
                else:
                    controlTowerResourcesByTypePurpose[entry.controlTowerTypeID][entry.purpose].append(entry)

            commands = []
            for (purposeID, caption,) in l:
                wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['items'].append(listentry.Get('Header', {'label': caption}))
                if controlTowerResourcesByTypePurpose.has_key(wnd.sr.typeID):
                    if controlTowerResourcesByTypePurpose[wnd.sr.typeID].has_key(purposeID):
                        for row in controlTowerResourcesByTypePurpose[wnd.sr.typeID][purposeID]:
                            text = mls.UI_INFOWND_FUELREQUIREMENTRATE % {'qty': row.quantity,
                             'rate': ['%s %s' % (cycle / 3600000L, mls.UI_GENERIC_HOURS.lower()), mls.UI_GENERIC_HOUR.lower()][(cycle / 3600000L == 1)]}
                            extraText = ''
                            if row.factionID is not None:
                                extraText += '%s %s' % (cfg.eveowners.Get(row.factionID).name, mls.UI_GENERIC_SPACE.lower())
                            if row.minSecurityLevel is not None:
                                if len(extraText):
                                    extraText += '; '
                                extraText += '%s &gt;= %0.1f' % (mls.UI_INFOWND_SECURITYLEVEL.lower(), row.minSecurityLevel)
                            if len(extraText):
                                extraText = ' (%s %s)' % (mls.UI_GENERIC_IF, extraText)
                            resourceType = cfg.invtypes.Get(row.resourceTypeID)
                            menuFunc = lambda itemID = resourceType.typeID: sm.StartService('menu').GetMenuFormItemIDTypeID(None, itemID, ignoreMarketDetails=0)
                            le = listentry.Get('LabelTextTop', {'line': 1,
                             'label': resourceType.typeName,
                             'text': text + extraText,
                             'iconID': resourceType.iconID,
                             'typeID': resourceType.typeID,
                             'GetMenu': menuFunc})
                            commands.append((row.resourceTypeID, row.quantity))
                            wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['items'].append(le)


            if eve.session.role & service.ROLE_GML == service.ROLE_GML:
                wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['items'].append(listentry.Get('Divider'))
                wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['items'].append(listentry.Get('Button', {'label': mls.UI_INFOWND_BOMTEXT2,
                 'caption': mls.UI_CMD_CREATE,
                 'OnClick': self.DoCreateMaterials,
                 'args': (commands, '', 10)}))
            wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['inited'] = 1
        wnd.sr.scroll.Load(fixedEntryHeight=27, contentList=wnd.sr.data[mls.UI_GENERIC_FUELREQUIREMENTS]['items'])



    def LoadMaterialRequirements(self, wnd):
        if not wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['inited']:
            stationTypeID = sm.GetService('godma').GetType(wnd.sr.typeID).stationTypeID
            ingredients = sm.RemoteSvc('factory').GetMaterialCompositionOfItemType(stationTypeID)
            commands = []
            for material in ingredients:
                commands.append((material.typeID, material.quantity))
                text = '%s %s' % (util.FmtAmt(material.quantity), uix.Plural(material.quantity, 'UI_GENERIC_UNIT'))
                materialTypeID = cfg.invtypes.Get(material.typeID)
                le = listentry.Get('LabelTextTop', {'line': 1,
                 'label': materialTypeID.name,
                 'text': text,
                 'iconID': materialTypeID.iconID,
                 'typeID': materialTypeID.typeID})
                wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['items'].append(le)

            wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['inited'] = 1
            if eve.session.role & service.ROLE_GML == service.ROLE_GML:
                wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['items'].append(listentry.Get('Divider'))
                wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['items'].append(listentry.Get('Button', {'label': mls.UI_INFOWND_BOMTEXT2,
                 'caption': mls.UI_CMD_CREATE,
                 'OnClick': self.DoCreateMaterials,
                 'args': (commands, '', 1)}))
        wnd.sr.scroll.Load(fixedEntryHeight=27, contentList=wnd.sr.data[mls.UI_GENERIC_MATERIALREQUIREMENTS]['items'])



    def LoadReaction(self, wnd):
        if not wnd.sr.data[mls.UI_GENERIC_REACTION]['inited']:
            res = [ (row.typeID, row.quantity) for row in cfg.invtypereactions[wnd.sr.typeID] if row.input == 1 ]
            prod = [ (row.typeID, row.quantity) for row in cfg.invtypereactions[wnd.sr.typeID] if row.input == 0 ]
            godma = sm.GetService('godma')
            commands = []
            for (label, what,) in [(mls.UI_GENERIC_RESOURCES, res), (mls.UI_GENERIC_PRODUCTS, prod)]:
                wnd.sr.data[mls.UI_GENERIC_REACTION]['items'].append(listentry.Get('Header', {'label': label}))
                for (typeID, quantity,) in what:
                    invtype = cfg.invtypes.Get(typeID)
                    amount = godma.GetType(typeID).moonMiningAmount
                    text = '%s %s' % (util.FmtAmt(quantity * amount), uix.Plural(quantity * amount, 'UI_GENERIC_UNIT'))
                    commands.append((typeID, quantity * amount))
                    le = listentry.Get('LabelTextTop', {'line': 1,
                     'label': invtype.name,
                     'text': text,
                     'typeID': typeID,
                     'iconID': invtype.Icon().iconID})
                    wnd.sr.data[mls.UI_GENERIC_REACTION]['items'].append(le)


            if eve.session.role & service.ROLE_GML == service.ROLE_GML:
                wnd.sr.data[mls.UI_GENERIC_REACTION]['items'].append(listentry.Get('Divider'))
                wnd.sr.data[mls.UI_GENERIC_REACTION]['items'].append(listentry.Get('Button', {'label': mls.UI_INFOWND_BOMTEXT2,
                 'caption': mls.UI_CMD_CREATE,
                 'OnClick': self.DoCreateMaterials,
                 'args': (commands, '', 10)}))
            wnd.sr.data[mls.UI_GENERIC_REACTION]['inited'] = 1
        wnd.sr.scroll.Load(contentList=wnd.sr.data[mls.UI_GENERIC_REACTION]['items'])



    def LoadStandings(self, wnd):
        self.LoadGeneric(wnd, mls.UI_GENERIC_STANDINGS, self.GetStandingsHistorySubContent)



    def GetStandingsHistorySubContent(self, itemID):
        return sm.GetService('standing').GetStandingRelationshipEntries(itemID)



    def SaveNote(self, wnd, closing = 0, *args):
        edit = uicls.EditPlainTextCore
        if isinstance(wnd, edit):
            try:
                dad = wnd.parent.parent.parent
            except AttributeError:
                sys.exc_clear()
                return 
        else:
            dad = wnd
        if not getattr(dad.sr, 'itemID', None):
            return 
        oldnotes = getattr(dad.sr, 'oldnotes', None)
        if oldnotes is None:
            return 
        if not closing:
            t = uthread.new(self.SaveNote_thread, dad, oldnotes)
            t.context = 'tactical::SaveNote'
            return 
        self.SaveNote_thread(dad, oldnotes)



    def SaveNote_thread(self, dad, oldnotes):
        if dad.sr.isCharacter:
            text = dad.sr.notesedit.GetValue()
            if text is None:
                return 
            if len(uiutil.StripTags(text)):
                if oldnotes != text:
                    setattr(dad.sr, 'oldnotes', text)
                    uthread.pool('infosvc::SetNote', sm.RemoteSvc('charMgr').SetNote, dad.sr.itemID, text[:5000])
            elif oldnotes:
                uthread.pool('infosvc::SetNote', sm.RemoteSvc('charMgr').SetNote, dad.sr.itemID, '')



    def Bookmark(self, itemID, typeID, parentID, *args):
        sm.GetService('addressbook').BookmarkLocationPopup(itemID, typeID, parentID)



    def ShowContracts(self, itemID, *args):
        sm.GetService('contracts').Show(lookup=cfg.eveowners.Get(itemID).name)



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        URL = URL.encode('cp1252', 'replace')
        if URL.startswith('showinfo:') or URL.startswith('evemail:') or URL.startswith('evemailto:'):
            self.output.GoTo(self, URL, data, args)
        else:
            uicore.cmd.OpenBrowser(URL, data=data, args=args)



    def LoadProcessPinSchematics(self, wnd):
        if not wnd.sr.data[mls.UI_PI_SCHEMATICS]['inited']:
            schematicItems = []
            for schematicRow in cfg.schematicsByPin.get(wnd.sr.typeID, []):
                schematic = cfg.schematics.Get(schematicRow.schematicID)
                abstractinfo = util.KeyVal(schematicName=schematic.schematicName, schematicID=schematic.schematicID, cycleTime=schematic.cycleTime)
                le = listentry.Get('Item', {'itemID': None,
                 'typeID': const.typeSchematic,
                 'label': schematic.schematicName,
                 'getIcon': 0,
                 'abstractinfo': abstractinfo})
                schematicItems.append(le)

            wnd.sr.data[mls.UI_PI_SCHEMATICS]['items'] = schematicItems
            wnd.sr.data[mls.UI_PI_SCHEMATICS]['inited'] = 1
        wnd.sr.scroll.Load(contentList=wnd.sr.data[mls.UI_PI_SCHEMATICS]['items'])



    def LoadCommodityProductionInfo(self, wnd):
        if not wnd.sr.data[mls.UI_PI_PRODUCTIONINFO]['inited']:
            schematicItems = []
            producingStructureLines = []
            producingSchematicLines = []
            consumingSchematicLines = []
            for typeRow in cfg.schematicsByType.get(wnd.sr.typeID, []):
                data = util.KeyVal()
                if typeRow.schematicID not in cfg.schematics:
                    self.LogWarn('CONTENT ERROR - Schematic ID', typeRow.schematicID, 'is in type map but not in main schematics list')
                    continue
                schematic = cfg.schematics.Get(typeRow.schematicID)
                abstractinfo = util.KeyVal(schematicName=schematic.schematicName, schematicID=schematic.schematicID, typeID=typeRow.typeID, isInput=typeRow.isInput, quantity=typeRow.quantity, cycleTime=schematic.cycleTime)
                le = listentry.Get('Item', {'itemID': None,
                 'typeID': const.typeSchematic,
                 'label': schematic.schematicName,
                 'getIcon': 0,
                 'abstractinfo': abstractinfo})
                if typeRow.isInput:
                    consumingSchematicLines.append(le)
                else:
                    producingSchematicLines.append(le)

            godma = sm.GetService('godma')
            for pinType in cfg.typesByGroups.get(const.groupExtractorPins, []):
                pinType = cfg.invtypes.Get(pinType.typeID)
                pinProducedType = godma.GetTypeAttribute(pinType.typeID, const.attributeHarvesterType)
                if pinProducedType and pinProducedType == wnd.sr.typeID:
                    producingStructureLines.append(listentry.Get('Item', {'itemID': None,
                     'typeID': pinType.typeID,
                     'label': pinType.typeName,
                     'getIcon': 0}))

            if len(producingSchematicLines) > 0:
                schematicItems.append(listentry.Get('Header', {'label': mls.UI_PI_SCHEMATICSPRODUCEDBY}))
                schematicItems.extend(producingSchematicLines)
            if len(producingStructureLines) > 0:
                schematicItems.append(listentry.Get('Header', {'label': mls.UI_PI_STRUCTURESPRODUCEDBY}))
                schematicItems.extend(producingStructureLines)
            if len(consumingSchematicLines) > 0:
                schematicItems.append(listentry.Get('Header', {'label': mls.UI_PI_SCHEMATICSCONSUMING}))
                schematicItems.extend(consumingSchematicLines)
            wnd.sr.data[mls.UI_PI_PRODUCTIONINFO]['items'] = schematicItems
            wnd.sr.data[mls.UI_PI_PRODUCTIONINFO]['inited'] = 1
        wnd.sr.scroll.Load(contentList=wnd.sr.data[mls.UI_PI_PRODUCTIONINFO]['items'])



    def ReportBot(self, itemID, *args):
        if eve.Message('ConfirmReportBot', {'name': cfg.eveowners.Get(itemID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        if itemID == session.charid:
            raise UserError('ReportBotCannotReportYourself')
        sm.RemoteSvc('userSvc').ReportBot(itemID)
        eve.Message('BotReported', {'name': cfg.eveowners.Get(itemID).name})




class SkillTreeEntry(listentry.Text):
    __guid__ = 'listentry.SkillTreeEntry'

    def Startup(self, *args):
        listentry.Text.Startup(self, args)
        self.sr.text.color.SetRGB(1.0, 1.0, 1.0, 0.75)
        self.sr.have = uicls.Icon(parent=self, left=5, top=0, height=16, width=16, align=uiconst.CENTERLEFT)



    def Load(self, args):
        listentry.Text.Load(self, args)
        data = self.sr.node
        if data.skills is not None:
            if data.typeID in data.skills:
                if data.skills[data.typeID].skillLevel >= data.lvl:
                    self.sr.have.LoadIcon('ui_38_16_193')
                    self.sr.have.hint = mls.UI_SHARED_TRAINEDANDOFREQLEVEL
                else:
                    self.sr.have.LoadIcon('ui_38_16_195')
                    self.sr.have.hint = mls.UI_SHARED_TRAINEDBUTNOTREQLEVEL
            else:
                self.sr.have.LoadIcon('ui_38_16_194')
                self.sr.have.hint = mls.UI_SHARED_TRAINEDBUTNOT
        else:
            self.sr.have.LoadIcon('ui_38_16_194')
            self.sr.have.hint = mls.UI_SHARED_TRAINEDBUTNOT
        self.sr.have.left = 15 * data.indent - 11
        self.sr.text.left = 15 * data.indent + 5



    def GetMenu(self):
        m = []
        data = self.sr.node
        if data is not None:
            if data.typeID:
                if data.skills is not None and data.typeID in data.skills:
                    skill = sm.StartService('skills').GetMySkillsFromTypeID(data.typeID)
                    if skill is not None:
                        m += sm.StartService('skillqueue').GetAddMenuForSkillEntries(skill)
                m += sm.StartService('menu').GetMenuFormItemIDTypeID(None, data.typeID, ignoreMarketDetails=0)
        return m




class InfoWindow(uicls.Window):
    __guid__ = 'form.infowindow'
    default_width = 256
    default_height = 340
    default_top = 0

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush




class PortraitWindow(uicls.Window):
    __guid__ = 'form.PortraitWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        charID = attributes.charID
        self.charID = charID
        self.size = 512
        width = self.size + 2 * const.defaultPadding
        self.SetMinSize([width, width + 16])
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.picParent = uicls.Container(name='picpar', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.pic = uicls.Sprite(parent=self.picParent, align=uiconst.TOALL)
        self.pic.GetMenu = self.PicMenu
        self.Load(charID)



    def Load(self, charID):
        charName = cfg.eveowners.Get(charID).name
        self.SetCaption('%s: %s' % (mls.UI_GENERIC_CHARACTER, charName))
        sm.GetService('photo').GetPortrait(charID, self.size, self.pic)



    def PicMenu(self, *args):
        m = []
        m.append((mls.UI_CMD_CAPTUREPORTRAIT, sm.StartService('photo').SavePortraits, [self.charID]))
        m.append((mls.UI_CMD_CLOSE, self.CloseX))
        return m




