import base
import blue
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
import localization

class MedicalWindow(uicls.Window):
    __guid__ = 'form.MedicalWindow'
    __notifyevents__ = ['OnCloneJumpUpdate', 'OnCloneTypeUpdatedClient']
    default_width = 400
    default_height = 300
    default_windowID = 'medical'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.homeStation = None
        self.potentialHomeStations = None
        self.cloneTypeID = None
        sm.RegisterNotify(self)
        self.SetWndIcon('ui_18_128_3', mainTop=-8)
        self.SetMinSize([350, 270])
        self.SetCaption(localization.GetByLabel('UI/Medical/Medical'))
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Medical/Cloning'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.scope = 'station'
        cloneButtons = [('medicalServicesChangeStationBtn',
          localization.GetByLabel('UI/Medical/Clone/ChangeStation'),
          self.PickNewHomeStation,
          None,
          81), ('medicalServicesUpgradeCloneBtn',
          localization.GetByLabel('UI/Medical/Clone/UpgradeClone'),
          self.PickNewCloneType,
          None,
          81)]
        btns = uicls.ButtonGroup(btns=cloneButtons, line=1, forcedButtonNames=True)
        self.sr.main.children.append(btns)
        self.sr.cloneBtns = btns
        btns = uicls.ButtonGroup(btns=[(localization.GetByLabel('UI/Medical/JumpClone/Install'),
          self.InstallClone,
          (),
          84), (localization.GetByLabel('UI/Medical/JumpClone/Destroy'),
          self.DestroyClone,
          (),
          84)], line=1)
        self.sr.main.children.append(btns)
        self.sr.jumpcloneBtns = btns
        tabs = ([localization.GetByLabel('UI/Medical/Clone'),
          self.sr.main,
          self,
          'podclone',
          self.sr.cloneBtns], [localization.GetByLabel('UI/Medical/JumpClone'),
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



    def _OnClose(self, *args):
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
        cloneID = sm.GetService('clonejump').GetCloneAtLocation(session.stationid2)
        scrolllist = []
        if cloneID:
            self.sr.scroll.ShowHint(None)
            locatedIn = localization.GetByLabel('UI/Medical/JumpClone/LocatedIn', stationLocation=session.stationid2)
            scrolllist.append(listentry.Get('Header', {'label': locatedIn}))
            godma = sm.GetService('godma')
            implantsPerClone = []
            for implant in sm.GetService('clonejump').GetImplantsForClone(cloneID):
                implantsPerClone.append((getattr(godma.GetType(implant.typeID), 'implantness', None), implant))

            implants = uiutil.SortListOfTuples(implantsPerClone)
            if implants:
                for cloneImplantRow in implants:
                    data = {'implant_booster': cloneImplantRow,
                     'label': cfg.invtypes.Get(cloneImplantRow.typeID).name}
                    scrolllist.append(listentry.Get('ImplantEntry', data))

            else:
                data = {'label': localization.GetByLabel('UI/Medical/JumpClone/NoImplantsInstalled'),
                 'text': localization.GetByLabel('UI/Medical/JumpClone/NoImplantsInstalled')}
                scrolllist.append(listentry.Get('Text', data))
        self.sr.scroll.Load(contentList=scrolllist)
        if not scrolllist:
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Medical/JumpClone/NoClonesAtStation'))



    def ShowMedicalInfo(self):
        homeStationID = self.GetHomeStation()
        cloneTypeID = self.GetCloneTypeID()
        cloneType = cfg.invtypes.Get(cloneTypeID)
        currentCloneGodmaInfo = sm.GetService('godma').GetType(cloneTypeID)
        scrolllist = []
        data = {'line': 1,
         'label': localization.GetByLabel('UI/Medical/Clone/CloneType'),
         'text': cloneType.name,
         'typeID': cloneTypeID,
         'iconID': cloneType.iconID}
        scrolllist.append(listentry.Get('LabelTextTop', data))
        data = {'line': 1,
         'label': localization.GetByLabel('UI/Medical/Clone/SkillPoints'),
         'text': localization.GetByLabel('UI/Medical/Clone/KeepsSkillPoints', skillPointsSaved=util.FmtAmt(currentCloneGodmaInfo.skillPointsSaved)),
         'iconID': cfg.invtypes.Get(const.typeScience).iconID}
        scrolllist.append(listentry.Get('LabelTextTop', data))
        data = {'line': 1,
         'label': localization.GetByLabel('UI/Medical/Clone/Location'),
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
                data.label = '%s<t>%s<t>%s' % (station.name, localization.GetByLabel('UI/Medical/Clone/NewHomeSecStatusEntry', securityStatus=secStatus), region.name)
                data.itemID = stationID
                data.typeID = typeID
                data.listvalue = [station.name, stationID]
                data.sublevel = 1
                if serviceMask & const.stationServiceCloning == const.stationServiceCloning:
                    stationsWithMedical.append(data)
                else:
                    stationsWithoutMedical.append(data)

            groupWithMedical = util.KeyVal()
            groupWithMedical.label = localization.GetByLabel('UI/Medical/Clone/StationsWithCloning')
            groupWithMedical.id = ('clonePicker', 1)
            groupWithMedical.showicon = 'hide'
            groupWithMedical.BlockOpenWindow = 1
            groupWithMedical.state = 'locked'
            groupWithMedical.showlen = 1
            groupWithMedical.sublevel = 0
            groupWithMedical.groupItems = stationsWithMedical
            groupWithoutMedical = util.KeyVal()
            groupWithoutMedical.label = localization.GetByLabel('UI/Medical/Clone/StationsWithoutCloning')
            groupWithoutMedical.id = ('clonePicker', 2)
            groupWithoutMedical.showicon = 'hide'
            groupWithoutMedical.BlockOpenWindow = 1
            groupWithoutMedical.state = 'locked'
            groupWithoutMedical.showlen = 1
            groupWithoutMedical.sublevel = 0
            groupWithoutMedical.groupItems = stationsWithoutMedical
            scrollHeaders = [localization.GetByLabel('UI/Medical/Clone/Station'), localization.GetByLabel('UI/Medical/Clone/SecurityStatus'), localization.GetByLabel('UI/Common/LocationTypes/Region')]
            ret = uix.ListWnd([groupWithMedical, groupWithoutMedical], 'station', localization.GetByLabel('UI/Medical/Clone/SelectHomeStation'), None, 1, windowName='newHomeStationWindow', lstDataIsGrouped=1, scrollHeaders=scrollHeaders)
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
            if eve.Message('AskAcceptCloneContractCost', {'cost': const.costCloneContract}, uiconst.YESNO) != uiconst.ID_YES:
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
                text = localization.GetByLabel('UI/Medical/Clone/SkillPointsKept', cloneType=typeID, skillPointsSaved=util.FmtAmt(skillPointsSaved), cloneCost=util.FmtISK(basePrice))
                if skillPointsSaved < currentSkillPoints:
                    text = localization.GetByLabel('UI/Medical/Clone/InsufficientClone', skillPointsKept=text)
                cloneDisplayList.append([text, typeID, typeID])

            hint = localization.GetByLabel('UI/Medical/Clone/CurrentSkillPoints', skillPoints=util.FmtAmt(currentSkillPoints))
            ret = uix.ListWnd(cloneDisplayList, 'type', localization.GetByLabel('UI/Medical/Clone/SelectCloneType'), hint, 0, 300)
            if ret:
                newCloneTypeID = ret[2]
            else:
                self.picking = 0
                return 
            if sm.GetService('godma').GetType(newCloneTypeID).skillPointsSaved < sm.GetService('godma').GetType(self.GetCloneTypeID()).skillPointsSaved:
                raise UserError('MedicalThisCloneIsWorse')
            if eve.Message('AskAcceptCloneTypeCost', {'cost': cfg.invtypes.Get(newCloneTypeID).basePrice}, uiconst.YESNO) != uiconst.ID_YES:
                self.picking = 0
                return 
            self.SetCloneTypeID(newCloneTypeID)

        finally:
            self.picking = 0




    def InstallClone(self, *args):
        sm.GetService('clonejump').InstallCloneInStation()



    def DestroyClone(self, *args):
        cloneID = sm.GetService('clonejump').GetCloneAtLocation(session.stationid2)
        if cloneID:
            sm.GetService('clonejump').DestroyInstalledClone(cloneID)



    def OnCloneTypeUpdatedClient(self):
        if self and not self.destroyed:
            self.RefreshInfo(refreshCharacterSheet=False)




