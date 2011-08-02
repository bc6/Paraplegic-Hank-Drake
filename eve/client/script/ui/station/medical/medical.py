import base
import blue
import draw
import form
import listentry
import log
import service
import sys
import uix
import uiutil
import uthread
import util
import xtriui
import uicls
import uiconst

class MedicalWindow(uicls.Window):
    __guid__ = 'form.MedicalWindow'
    __notifyevents__ = ['OnCloneJumpUpdate', 'OnCloneTypeUpdatedClient']
    default_width = 400
    default_height = 300

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.homeStation = None
        self.potentialHomeStations = None
        self.cloneTypeID = None
        sm.RegisterNotify(self)
        self.SetWndIcon('ui_18_128_3', mainTop=-8)
        self.SetMinSize([350, 270])
        self.SetCaption(mls.UI_STATION_MEDICAL)
        uicls.WndCaptionLabel(text=mls.UI_SHARED_MAPOPS34, parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.scope = 'station'
        btns = uicls.ButtonGroup(btns=[('medicalServicesChangeStationBtn',
          mls.UI_CMD_CHANGESTATION,
          self.PickNewHomeStation,
          None,
          81), ('medicalServicesUpgradeCloneBtn',
          mls.UI_CMD_UPGRADECLONE,
          self.PickNewCloneType,
          None,
          81)], line=1, forcedButtonNames=True)
        self.sr.main.children.append(btns)
        self.sr.cloneBtns = btns
        btns = uicls.ButtonGroup(btns=[(mls.UI_CMD_INSTALL,
          self.InstallClone,
          (),
          84), (mls.UI_CMD_DESTROY,
          self.DestroyClone,
          (),
          84)], line=1)
        self.sr.main.children.append(btns)
        self.sr.jumpcloneBtns = btns
        tabs = ([mls.UI_GENERIC_CLONE,
          self.sr.main,
          self,
          'podclone',
          self.sr.cloneBtns], [mls.UI_GENERIC_JUMPCLONE,
          self.sr.main,
          self,
          'jumpclone',
          self.sr.jumpcloneBtns])
        self.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=1)
        self.maintabs.Startup(tabs, 'clonespanel')
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))



    def OnClose_(self, *args):
        sm.UnregisterNotify(self)



    def Load(self, key):
        self.sr.scroll.ShowHint(None)
        if key == 'podclone':
            self.ShowMedicalInfo()
        elif key == 'jumpclone':
            self.ShowJumpCloneInfo()



    def RefreshInfo(self, refreshCharacterSheet = True):
        if refreshCharacterSheet:
            sm.GetService('charactersheet').LoadGeneralInfo()
        self.ShowMedicalInfo()



    def GetHomeStation(self):
        if self.homeStation is None:
            self.homeStation = sm.RemoteSvc('charMgr').GetHomeStation()
        return self.homeStation



    def SetHomeStation(self, newHomeStationID):
        sm.GetService('corp').GetCorpStationManager().SetHomeStation(newHomeStationID)
        self.homeStation = newHomeStationID
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetHomeStation')
        self.RefreshInfo()



    def GetCloneTypeID(self):
        if self.cloneTypeID == None:
            self.cloneTypeID = sm.RemoteSvc('charMgr').GetCloneTypeID()
        if not self.cloneTypeID:
            self.cloneTypeID = const.typeCloneGradeAlpha
        return self.cloneTypeID



    def SetCloneTypeID(self, typeID):
        sm.GetService('corp').GetCorpStationManager().SetCloneTypeID(typeID)
        self.cloneTypeID = typeID
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetCloneTypeID')
        self.RefreshInfo()



    def GetPotentialHomeStations(self):
        if self.potentialHomeStations == None:
            self.potentialHomeStations = sm.GetService('corp').GetCorpStationManager().GetPotentialHomeStations()
        return self.potentialHomeStations



    def OnCloneJumpUpdate(self):
        if self.maintabs and self.maintabs.GetSelectedArgs() == 'jumpclone':
            self.ShowJumpCloneInfo()



    def ShowJumpCloneInfo(self):
        cloneID = sm.GetService('clonejump').GetCloneAtLocation(eve.session.stationid)
        scrolllist = []
        if cloneID:
            self.sr.scroll.ShowHint(None)
            scrolllist.append(listentry.Get('Header', {'label': '%s %s' % (mls.UI_SHARED_LOCATEDIN, cfg.evelocations.Get(eve.session.stationid).name)}))
            godma = sm.GetService('godma')
            implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in sm.GetService('clonejump').GetImplantsForClone(cloneID) ])
            if implants:
                for cloneImplantRow in implants:
                    scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': cloneImplantRow,
                     'label': cfg.invtypes.Get(cloneImplantRow.typeID).name}))

            else:
                scrolllist.append(listentry.Get('Text', {'label': mls.UI_SHARED_NOIMPLANTSINSTALLED,
                 'text': mls.UI_SHARED_NOIMPLANTSINSTALLED}))
        self.sr.scroll.Load(contentList=scrolllist)
        if not scrolllist:
            self.sr.scroll.ShowHint(mls.UI_STATION_TEXT3)



    def ShowMedicalInfo(self):
        homeStationID = self.GetHomeStation()
        cloneTypeID = self.GetCloneTypeID()
        cloneType = cfg.invtypes.Get(cloneTypeID)
        currentCloneGodmaInfo = sm.GetService('godma').GetType(cloneTypeID)
        scrolllist = []
        data = {'line': 1,
         'label': mls.UI_GENERIC_CLONETYPE,
         'text': cloneType.name,
         'typeID': cloneTypeID,
         'iconID': cloneType.iconID}
        scrolllist.append(listentry.Get('LabelTextTop', data))
        data = {'line': 1,
         'label': mls.UI_GENERIC_SKILLPOINTS,
         'text': mls.UI_STATION_TEXT56 % {'skillPoints': '<b>%s</b>' % util.FmtAmt(currentCloneGodmaInfo.skillPointsSaved)},
         'iconID': cfg.invtypes.Get(const.typeScience).iconID}
        scrolllist.append(listentry.Get('LabelTextTop', data))
        data = {'line': 1,
         'label': mls.UI_GENERIC_LOCATION,
         'text': cfg.evelocations.Get(homeStationID).name,
         'isStation': 1,
         'itemID': homeStationID}
        scrolllist.append(listentry.Get('LabelTextTop', data))
        self.sr.scroll.Load(contentList=scrolllist)
        if not scrolllist:
            self.SetHint('_nothing found')



    def PickNewHomeStation(self, *args):
        if getattr(self, 'picking', 0):
            return 
        try:
            self.picking = 1
            homeStationID = self.GetHomeStation()
            stations = self.GetPotentialHomeStations()
            stationTypeIDbyStationID = {}
            for station in stations:
                stationTypeIDbyStationID[station.stationID] = (station.typeID, station.serviceMask)

            cfg.evelocations.Prime(stationTypeIDbyStationID.keys())
            stationsWithMedical = []
            stationsWithoutMedical = []
            mapSvc = sm.GetService('map')
            uiSvc = sm.GetService('ui')
            for (stationID, stationData,) in stationTypeIDbyStationID.iteritems():
                (typeID, serviceMask,) = stationData
                station = cfg.evelocations.Get(stationID)
                systemID = uiSvc.GetStation(stationID).solarSystemID
                regionID = mapSvc.GetRegionForSolarSystem(systemID)
                sec = mapSvc.GetSecurityStatus(systemID)
                secStatus = util.FmtSystemSecStatus(sec)
                region = cfg.evelocations.Get(regionID)
                data = util.KeyVal()
                data.label = '%s<t><right>%s<t>%s' % (station.name, secStatus, region.name)
                data.itemID = stationID
                data.typeID = typeID
                data.listvalue = [station.name, stationID]
                data.sublevel = 1
                if serviceMask & const.stationServiceCloning == const.stationServiceCloning:
                    stationsWithMedical.append(data)
                else:
                    stationsWithoutMedical.append(data)

            groupWithMedical = util.KeyVal()
            groupWithMedical.label = mls.UI_STATION_STATIONSWITHCLONING
            groupWithMedical.id = ('clonePicker', 1)
            groupWithMedical.showicon = 'hide'
            groupWithMedical.BlockOpenWindow = 1
            groupWithMedical.state = 'locked'
            groupWithMedical.showlen = 1
            groupWithMedical.sublevel = 0
            groupWithMedical.groupItems = stationsWithMedical
            groupWithoutMedical = util.KeyVal()
            groupWithoutMedical.label = mls.UI_STATION_STATIONSWITHOUTCLONING
            groupWithoutMedical.id = ('clonePicker', 2)
            groupWithoutMedical.showicon = 'hide'
            groupWithoutMedical.BlockOpenWindow = 1
            groupWithoutMedical.state = 'locked'
            groupWithoutMedical.showlen = 1
            groupWithoutMedical.sublevel = 0
            groupWithoutMedical.groupItems = stationsWithoutMedical
            scrollHeaders = [mls.UI_GENERIC_STATION, mls.UI_GENERIC_SECURITYSHORT, mls.UI_GENERIC_REGION]
            ret = uix.ListWnd([groupWithMedical, groupWithoutMedical], 'station', mls.UI_STATION_TEXT5, None, 1, windowName='newHomeStationWindow', lstDataIsGrouped=1, scrollHeaders=scrollHeaders)
            if ret:
                if not stationTypeIDbyStationID[ret[1]][1] & const.stationServiceCloning == const.stationServiceCloning:
                    if eve.Message('AskSetHomeStationWithoutMedical', buttons=uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                        self.picking = 0
                        return 
                newHomeStationID = ret[1]
            else:
                self.picking = 0
                return 
            if newHomeStationID == homeStationID:
                raise UserError('MedicalYouAlreadyHaveACloneContractAtThatStation')
            newHomeStationTypeID = stationTypeIDbyStationID[newHomeStationID][0]
            if sm.GetService('godma').GetType(newHomeStationTypeID).isPlayerOwnable == 1:
                if eve.Message('AskSetHomeStationAtPOS', {}, uiconst.YESNO) != uiconst.ID_YES:
                    self.picking = 0
                    return 
            if eve.Message('AskAcceptCloneContractCost', {'cost': util.FmtCurrency(const.costCloneContract, currency=None)}, uiconst.YESNO) != uiconst.ID_YES:
                self.picking = 0
                return 
            self.SetHomeStation(newHomeStationID)

        finally:
            self.picking = 0




    def PickNewCloneType(self, *args):
        if getattr(self, 'picking', 0):
            return 
        try:
            self.picking = 1
            cloneList = []
            currentCloneGodmaInfo = sm.GetService('godma').GetType(self.GetCloneTypeID())
            for typeInfo in cfg.typesByGroups.get(const.groupClone, []):
                godmaInfo = sm.GetService('godma').GetType(typeInfo.typeID)
                if godmaInfo.skillPointsSaved <= currentCloneGodmaInfo.skillPointsSaved:
                    continue
                cloneList.append([typeInfo.typeID, godmaInfo.skillPointsSaved, typeInfo.basePrice])

            if len(cloneList) == 0:
                raise UserError('MedicalAlreadyHaveBestCloneType')
            cloneList.sort(lambda a, b: -(a[1] > b[1]))
            cloneDisplayList = []
            currentSkillPoints = sm.GetService('skills').GetSkillPoints()
            for clone in cloneList:
                typeID = clone[0]
                skillPointsSaved = clone[1]
                basePrice = clone[2]
                text = '%s - %s %s - %s' % (cfg.invtypes.Get(typeID).name,
                 mls.UI_STATION_TEXT6,
                 util.FmtAmt(skillPointsSaved),
                 util.FmtISK(basePrice))
                if skillPointsSaved < currentSkillPoints:
                    text = '<color=gray>%s</color>' % text
                cloneDisplayList.append([text, typeID, typeID])

            hint = mls.UI_STATION_TEXT7 % {'num': util.FmtAmt(currentSkillPoints)}
            ret = uix.ListWnd(cloneDisplayList, 'type', mls.UI_STATION_TEXT8, hint, 0, 300)
            if ret:
                newCloneTypeID = ret[2]
            else:
                self.picking = 0
                return 
            if sm.GetService('godma').GetType(newCloneTypeID).skillPointsSaved < sm.GetService('godma').GetType(self.GetCloneTypeID()).skillPointsSaved:
                raise UserError('MedicalThisCloneIsWorse')
            if eve.Message('AskAcceptCloneTypeCost', {'cost': util.FmtCurrency(cfg.invtypes.Get(newCloneTypeID).basePrice, currency=None)}, uiconst.YESNO) != uiconst.ID_YES:
                self.picking = 0
                return 
            self.SetCloneTypeID(newCloneTypeID)

        finally:
            self.picking = 0




    def InstallClone(self, *args):
        sm.GetService('clonejump').InstallCloneInStation()



    def DestroyClone(self, *args):
        cloneID = sm.GetService('clonejump').GetCloneAtLocation(eve.session.stationid)
        if cloneID:
            sm.GetService('clonejump').DestroyInstalledClone(cloneID)



    def OnCloneTypeUpdatedClient(self):
        if self and not self.destroyed:
            self.RefreshInfo(refreshCharacterSheet=False)




