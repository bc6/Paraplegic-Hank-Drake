import blue
import xtriui
import uix
import uiutil
import uthread
import form
import listentry
import service
import util
import base
import sys
import copy
import types
import log
import uiconst
import uicls
import localization
import localizationUtil
LOCATION_BLUEPRINT = 9999

class ManufacturingSvc(service.Service):
    __exportedcalls__ = {}
    __guid__ = 'svc.manufacturing'
    __notifyevents__ = ['OnSessionChanged', 'OnItemChange']
    __servicename__ = 'Manufacturing'
    __displayname__ = 'Manufacturing Service'
    __dependencies__ = []
    __update_on_reload__ = 0
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.detailsByRegionByTypeFlag = {}
        self.activities = None
        self.activitiesIdx = None



    def Run(self, memStream = None):
        if session.userid:
            self.PopulateActivities()
        self.relevantskills = None
        self.relevantskillscachetime = None



    def Stop(self, memStream = None):
        form.Manufacturing.CloseIfOpen()
        self.detailsByRegionByTypeFlag = {}



    def _FillActivities(self):
        self.detailsByRegionByTypeFlag = {}
        self.PopulateActivities(force=True)



    def PopulateActivities(self, force = False):
        if not force and self.activities:
            return 
        self.LogInfo('Populating activities')
        allActivitiesLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/AllActivities'
        manufacturingLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/Manufacturing'
        materialResearchLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/MaterialResearch'
        timeEffLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/TimeEfficiencyResearch'
        copyingLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/Copying'
        dublicatingLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/Duplicating'
        technologyLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/Technology'
        inventionLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/Invention'
        reversEngineeringLabel = 'UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/ReverseEngineering'
        activities = [[const.activityNone, allActivitiesLabel],
         [const.activityManufacturing, manufacturingLabel],
         [const.activityResearchingMaterialProductivity, materialResearchLabel],
         [const.activityResearchingTimeProductivity, timeEffLabel],
         [const.activityCopying, copyingLabel],
         [const.activityDuplicating, dublicatingLabel],
         [const.activityResearchingTechnology, technologyLabel],
         [const.activityInvention, inventionLabel],
         [const.activityReverseEngineering, reversEngineeringLabel]]
        self.activities = [ (activityID, labelPath) for (activityID, labelPath,) in activities if cfg.ramactivities.Get(activityID).published ]
        self.activitiesIdx = dict(self.activities)



    def GetActivities(self):
        self.PopulateActivities()
        return self.activities



    def GetRestrictionMasks(self):
        allianceLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Settings/AllowAlliance')
        corporationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Settings/AllowCorporation')
        standingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Settings/AllowByStanding')
        securityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Settings/AllowBySecurityStanding')
        m = [(allianceLabel, 'ramRestrictByAlliance', const.ramRestrictByAlliance),
         (corporationLabel, 'ramRestrictByCorp', const.ramRestrictByCorp),
         (standingLabel, 'ramRestrictByStanding', const.ramRestrictByStanding),
         (securityLabel, 'ramRestrictBySecurity', const.ramRestrictBySecurity)]
        return m



    def GetRanges(self, beyondCurrent = False):
        systemLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/CurrentSolarSystem')
        constallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/CurrentConstellation')
        regionLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/CurrentRegion')
        ranges = [((eve.session.solarsystemid2, const.groupSolarSystem), systemLabel), ((eve.session.constellationid, const.groupConstellation), constallationLabel), ((eve.session.regionid, const.groupRegion), regionLabel)]
        if beyondCurrent:
            universeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/CurrentUniverse')
            (ranges.append(((0, 0), universeLabel)),)
        if eve.session.stationid:
            stationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/CurrentStation')
            ranges.insert(0, ((eve.session.stationid, const.groupStation), stationLabel))
        self.ranges = [ (locationData, text) for (locationData, text,) in ranges ]
        self.rangesIdx = dict(self.ranges)
        return self.ranges



    def OnSessionChanged(self, isremote, sess, change):
        if 'userid' in change:
            self._FillActivities()
        if 'regionid' in change or 'shipid' in change:
            self.detailsByRegionByTypeFlag = {}
        if 'stationid' in change or 'solarsystemid' in change or 'regionid' in change or 'constellationid' in change or 'shipid' in change:
            wnd = form.Manufacturing.GetIfOpen()
            if wnd:
                wnd.ReloadTabs()



    def Reset(self, wnd):
        for key in ['pers', 'corp']:
            setattr(wnd, '%sBlueprintsInited' % key, 0)




    def OnItemChange(self, item, change):
        if item.categoryID not in (const.categoryBlueprint, const.categoryAncientRelic):
            return 
        if const.ixFlag in change and const.ixOwnerID not in change and const.ixLocationID not in change:
            (corpID, currentFlagBeingViewed,) = settings.user.ui.Get('blueprint_divisionfilter', (None, None))
            (oldFlag, newFlag,) = (change[const.ixFlag], item[const.ixFlag])
            corpHangarFlags = (const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7)
            if oldFlag in corpHangarFlags and newFlag in corpHangarFlags:
                if currentFlagBeingViewed is None or currentFlagBeingViewed not in (oldFlag, newFlag):
                    return 
        wnd = form.Manufacturing.GetIfOpen()
        if wnd is not None and not wnd.destroyed:
            self.ReloadBlueprints()



    def GetAvailableHangars(self, canView = 1, canTake = 1, all = 0, locationID = None):
        options = []
        paramsByDivision = {1: (const.flagHangar, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
         2: (const.flagCorpSAG2, const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
         3: (const.flagCorpSAG3, const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
         4: (const.flagCorpSAG4, const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
         5: (const.flagCorpSAG5, const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
         6: (const.flagCorpSAG6, const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
         7: (const.flagCorpSAG7, const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
        divisions = sm.GetService('corp').GetDivisionNames()
        options = []
        i = 0
        roleSet = 0L
        if locationID is None:
            roleSet = eve.session.corprole
        elif hasattr(eve.session, 'hqID') and locationID == eve.session.hqID:
            roleSet = eve.session.rolesAtHQ | eve.session.rolesAtAll
        elif hasattr(eve.session, 'baseID') and locationID == eve.session.baseID:
            roleSet = eve.session.rolesAtBase | eve.session.rolesAtAll
        else:
            roleSet = eve.session.rolesAtOther | eve.session.rolesAtAll
        while i < 7:
            i += 1
            param = paramsByDivision[i]
            if not all:
                if canView:
                    if roleSet & param[1] != param[1]:
                        continue
                if canTake:
                    if roleSet & param[2] != param[2]:
                        continue
            hangarDescription = divisions[i]
            options.append((hangarDescription, (eve.session.corpid, param[0])))

        return options



    def CreateJob(self, invItem = None, assemblyLine = None, activityID = None, installationDetails = None):
        wnd = form.ManufacturingInstallation.GetIfOpen()
        if wnd is not None and not wnd.destroyed:
            wnd.Show()
            return 
        if activityID is None:
            activityID = installationDetails.activityID
        wnd = form.ManufacturingInstallation.Open(activityID=activityID, loadData=(invItem,
         assemblyLine,
         activityID,
         installationDetails))



    def CompleteJob(self, jobdata, cancel = False):
        if cfg.invtypes.Get(jobdata.containerTypeID).categoryID == const.categoryShip:
            if jobdata.containerID != eve.session.shipid:
                uthread.new(eve.Message, 'RamCompletionMustBeInShip')
                return 
        if util.IsStation(jobdata.containerID):
            log.LogInfo('its in a station')
            installationLocationData = [[jobdata.containerID, const.groupStation], [], [jobdata.containerID]]
        else:
            log.LogInfo('ship or starbase')
            if jobdata.containerID == eve.session.shipid:
                log.LogInfo('its in a ship')
                path = []
                if util.IsStation(eve.session.locationid):
                    invLocationGroupID = const.groupStation
                    path.append([eve.session.locationid, eve.session.charid, const.flagHangar])
                else:
                    invLocationGroupID = const.groupSolarSystem
                installationLocationData = [[eve.session.locationid, invLocationGroupID], path, [jobdata.containerID]]
            else:
                log.LogInfo('its in a starbase')
                installationLocationData = [[jobdata.installedInSolarSystemID, const.groupSolarSystem], [], [jobdata.containerID]]
        completingJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CompletingJobs')
        cancellingJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CancellingJobs')
        title = {False: completingJobsLabel,
         True: cancellingJobsLabel}[cancel]
        text = {False: completingJobsLabel,
         True: cancellingJobsLabel}[cancel]
        try:
            sm.GetService('loading').ProgressWnd(title, text, 1, 2)
            result = sm.ProxySvc('ramProxy').CompleteJob(installationLocationData, jobdata.jobID, cancel)
            if hasattr(result, 'messageLabel'):
                inventionResultLabel = localization.GetByLabel(result.messageLabel)
                if result.jobCompletedSuccessfully:
                    eve.Message('RamInventionJobSucceeded', {'info': inventionResultLabel,
                     'me': result.outputME,
                     'pe': result.outputPE,
                     'runs': result.outputRuns,
                     'type': result.outputTypeID,
                     'typeid': str(result.outputTypeID),
                     'itemid': str(result.outputItemID)})
                else:
                    eve.Message('RamInventionJobFailed', {'info': inventionResultLabel})
            if hasattr(result, 'message'):
                eve.Message(result.message.msg, result.message.args)
            doneLabel = localization.GetByLabel('UI/Common/Done')
            sm.GetService('loading').ProgressWnd(title, doneLabel, 2, 2)
        except UserError as what:
            doneLabel = localization.GetByLabel('UI/Common/Done')
            sm.GetService('loading').ProgressWnd(title, doneLabel, 1, 1)
            raise 



    def GetRegionDetails(self, typeFlag = 'region'):
        regionid = eve.session.regionid
        if regionid not in self.detailsByRegionByTypeFlag:
            self.detailsByRegionByTypeFlag[regionid] = {}
        if typeFlag == 'region':
            details = sm.ProxySvc('ramProxy').AssemblyLinesSelectPublic()
        elif typeFlag == 'char':
            details = sm.ProxySvc('ramProxy').AssemblyLinesSelectPrivate()
        elif typeFlag == 'corp':
            details = sm.ProxySvc('ramProxy').AssemblyLinesSelectCorp()
        elif typeFlag == 'alliance':
            details = sm.ProxySvc('ramProxy').AssemblyLinesSelectAlliance()
        else:
            details = None
        if details is None:
            self.LogError('RAM Proxy returned a null set of assembly lines.')
            return 
        details.header.append('activityID')
        for row in details:
            row.line.append(cfg.ramaltypes.Get(row.assemblyLineTypeID).activityID)

        self.detailsByRegionByTypeFlag[regionid][typeFlag] = details
        prime = []
        for line in details:
            prime.append(line.containerID)

        if len(prime):
            cfg.evelocations.Prime(prime)
        return self.detailsByRegionByTypeFlag[regionid][typeFlag]



    def GetRelevantCharSkills(self):
        self.ResetRelevantCharSkills()
        if not self.relevantskills:
            self.relevantskills = sm.ProxySvc('ramProxy').GetRelevantCharSkills()
            self.relevantskillscachetime = blue.os.GetWallclockTime()
        return self.relevantskills



    def ResetRelevantCharSkills(self):
        if self.relevantskills is None:
            return 
        t = blue.os.GetWallclockTime()
        if t - self.relevantskillscachetime > MIN * 15:
            self.relevantskills = None



    def GetInstallationDetails(self, installationLocationData):
        return sm.ProxySvc('ramProxy').GetInstallationDetails(installationLocationData)



    def IsRamInstallable(self, item):
        if item.categoryID != const.categoryBlueprint:
            return False
        if util.IsStation(item.locationID):
            return True
        if util.GetActiveShip() == item.locationID:
            return True
        if item.ownerID != session.corpid:
            return False
        locationItem = sm.GetService('michelle').GetItem(item.locationID)
        if locationItem and locationItem.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray, const.groupMobileLaboratory):
            return True
        if not locationItem and sm.GetService('invCache').GetStationIDOfItem(item) in (r.stationID for r in sm.GetService('corp').GetMyCorporationsOffices()):
            return True
        return False



    def IsReverseEngineering(self, item):
        if item.categoryID != const.categoryAncientRelic:
            return False
        locationItem = sm.GetService('michelle').GetItem(item.locationID)
        if locationItem and locationItem.groupID == const.groupMobileLaboratory:
            return True
        if not locationItem:
            if util.IsStation(item.locationID):
                return True
            if sm.GetService('invCache').GetStationIDOfItem(item) in (r.stationID for r in sm.GetService('corp').GetMyCorporationsOffices()):
                return True
        return False



    def IsRamCompatible(self, itemID):
        isRAMCompatible = False
        if itemID == eve.session.shipid:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            isRAMCompatible = sm.GetService('godma').GetType(ship.typeID).isRAMcompatible
        elif util.IsStation(itemID):
            if self.CheckStationService(itemID, const.stationServiceFactory):
                isRAMCompatible = True
            elif self.CheckStationService(itemID, const.stationServiceLaboratory):
                isRAMCompatible = True
        return isRAMCompatible



    def CheckStationService(self, stationID, serviceID):
        (stations, opservices, services,) = sm.RemoteSvc('map').GetStationExtraInfo()
        stations = stations.Index('stationID')
        if stationID in stations:
            station = stations[stationID]
            operationID = station.operationID
            s = {}
            for each in opservices:
                if each.operationID not in s:
                    s[each.operationID] = []
                s[each.operationID].append(each.serviceID)

            return bool(serviceID in s[operationID])
        return False



    def GetQuoteDialog(self, quoteData):
        if not quoteData.assemblyLine:
            raise UserError('RamPleasePickAnInstalltion')
        if not quoteData.blueprint:
            raise UserError('RamPleasePickAnItemToInstall')
        needInputFlag = True
        needOutputFlag = True
        core1 = None
        core2 = None
        base = None
        interface = None
        if not quoteData.ownerInputAndflagInput:
            blueprintTypeID = quoteData.blueprint.typeID
            myBlueprint = cfg.invbptypes.Get(blueprintTypeID)
            requiresMaterials = False
            if quoteData.activityID == const.activityManufacturing:
                for row in cfg.invtypematerials.get(myBlueprint.productTypeID, []):
                    if row.quantity:
                        requiresMaterials = True
                        break

            if not requiresMaterials:
                if (blueprintTypeID, quoteData.activityID) in cfg.ramtyperequirements:
                    for row in cfg.ramtyperequirements[(blueprintTypeID, quoteData.activityID)]:
                        reqType = cfg.invtypes.Get(row.requiredTypeID)
                        if reqType.categoryID == const.categorySkill:
                            continue
                        if row.quantity:
                            requiresMaterials = True
                            break

            if requiresMaterials:
                eve.Message('PleaseSelectInputLocation')
                return 
            needInputFlag = False
        if quoteData.activityID in (const.ramActivityResearchingTimeProductivity, const.ramActivityResearchingMaterialProductivity):
            needOutputFlag = False
        elif not quoteData.ownerOutputAndflagOutput:
            eve.Message('PleaseSelectOutputLocation')
            return 
        if needInputFlag:
            (ownerInput, flagInput,) = quoteData.ownerInputAndflagInput
        else:
            (ownerInput, flagInput,) = (None, const.flagNone)
        if needOutputFlag:
            (ownerOutput, flagOutput,) = quoteData.ownerOutputAndflagOutput
        else:
            (ownerOutput, flagOutput,) = (None, const.flagNone)
        settings.user.ui.Set('rmInputCombo', (ownerInput, flagInput))
        settings.user.ui.Set('rmOutputCombo', (ownerOutput, flagOutput))
        if util.IsStation(quoteData.containerID):
            invLocationGroupID = const.groupStation
        elif quoteData.containerID == session.shipid:
            invLocationGroupID = [const.groupSolarSystem, const.groupStation][(session.locationid == session.stationid)]
        else:
            invLocationGroupID = const.groupSolarSystem
        invLocation = []
        if ownerInput == session.charid:
            if flagInput == const.flagCargo:
                invLocation = [session.locationid, invLocationGroupID]
                bomLocationData = [[session.locationid, invLocationGroupID], [[quoteData.containerID, session.charid, flagInput]], []]
            elif flagInput == const.flagHangar:
                invLocation = [quoteData.containerID, invLocationGroupID]
                bomLocationData = [[quoteData.containerID, invLocationGroupID], [[quoteData.containerID, session.charid, flagInput]], []]
            else:
                raise UserError('RamInstalledItemBadLocation')
        elif ownerInput == session.corpid:
            if flagInput == const.flagCargo:
                raise UserError('RamCorpInstalledItemNotInCargo')
            elif flagInput in (const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7):
                if not quoteData.containerID:
                    raise UserError('RamPleasePickAnInstalltion')
                if util.IsStation(quoteData.containerID):
                    offices = sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('stationID', [quoteData.containerID])
                    officeFolderID = None
                    officeID = None
                    if offices and len(offices):
                        for office in offices:
                            if quoteData.containerID == office.stationID:
                                officeFolderID = office.officeFolderID
                                officeID = office.officeID

                    if officeID is None:
                        raise UserError('RamCorpBOMItemNoSuchOffice', {'location': quoteData.containerID})
                    invLocation = [quoteData.containerID, const.groupStation]
                    path = []
                    path.append([quoteData.containerID, const.ownerStation, 0])
                    path.append([officeFolderID, session.corpid, const.flagHangar])
                    path.append([officeID, session.corpid, flagInput])
                    bomLocationData = [invLocation, path, []]
                elif util.IsSolarSystem(quoteData.containerLocationID):
                    invLocation = [quoteData.containerLocationID, const.groupSolarSystem]
                    path = []
                    path.append([quoteData.containerID, session.corpid, flagInput])
                    bomLocationData = [invLocation, path, []]
                else:
                    raise UserError('RamPleasePickAnInstalltion')
            else:
                raise UserError('RamNotYourItemToInstall')
        else:
            bomLocationData = None
            if not needInputFlag:
                if ownerID in (session.charid, session.corpid):
                    invLocation = [quoteData.ontainerID, invLocationGroupID]
                    bomLocationData = [[quoteData.containerID, invLocationGroupID], [[const.flagNone]], []]
            if bomLocationData is None:
                raise UserError('RamNotYourItemToInstall')
        installedItemLocationData = sm.GetService('manufacturing').GetPathToItem(quoteData.blueprint)
        installationLocationData = [invLocation, [], [quoteData.containerID]]
        installationLocationData[2].append(quoteData.assemblyLineID)
        calculateQuoteLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CalculatingQuote')
        gettingQuoteLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GettingQuoteFromInstallation')
        sm.GetService('loading').ProgressWnd(calculateQuoteLabel, gettingQuoteLabel, 1, 3)
        blue.pyos.synchro.SleepWallclock(0)
        quote = None
        try:
            job = sm.ProxySvc('ramProxy').InstallJob(installationLocationData, installedItemLocationData, bomLocationData, flagOutput, quoteData.buildRuns, quoteData.activityID, quoteData.licensedProductionRuns, not quoteData.ownerFlag, 'blah', quoteOnly=1, installedItem=quoteData.blueprint, maxJobStartTime=quoteData.assemblyLine.nextFreeTime + 1 * MIN, inventionItems=quoteData.inventionItems, inventionOutputItemID=quoteData.inventionItems.outputType)
            quote = job.quote
            if job.installedItemID:
                quoteData.blueprint.itemID = job.installedItemID
                installedItemLocationData[2] = [job.installedItemID]
        except UserError as e:
            cancelingQuoteLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CancellingQuote')
            quoteNotAcceptedLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/QuoteNotAccepted')
            sm.GetService('loading').ProgressWnd(cancelingQuoteLabel, quoteNotAcceptedLabel, 1, 1)
            raise 
        installingJobLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallingJob')
        finishingText = localization.GetByLabel('UI/Common/Done')
        if quote is not None:
            sm.GetService('loading').ProgressWnd(calculateQuoteLabel, gettingQuoteLabel, 3, 3)
            form.ManufacturingQuoteWindow.CloseIfOpen()
            cancellingInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CancellingInstallation')
            wnd = form.ManufacturingQuoteWindow.Open(quote=quote, quoteData=quoteData)
            if wnd.ShowDialog() == uiconst.ID_OK:
                installinginCurrontLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallInCurrentInstallation')
                sm.GetService('loading').ProgressWnd(installingJobLabel, installinginCurrontLabel, 2, 4)
                try:
                    authorizedCost = quote.cost
                    sm.services['objectCaching'].InvalidateCachedMethodCall('ramProxy', 'AssemblyLinesGet', quoteData.containerID)
                    sm.ProxySvc('ramProxy').InstallJob(installationLocationData, installedItemLocationData, bomLocationData, flagOutput, quoteData.buildRuns, quoteData.activityID, quoteData.licensedProductionRuns, not quoteData.ownerFlag, 'blah', quoteOnly=0, authorizedCost=authorizedCost, installedItem=quoteData.blueprint, maxJobStartTime=quoteData.assemblyLine.nextFreeTime + 1 * MIN, inventionItems=quoteData.inventionItems, inventionOutputItemID=quoteData.inventionItems.outputType)
                    sm.GetService('objectCaching').InvalidateCachedMethodCall('ramProxy', 'GetJobs2', ownerInput, 0)
                    sm.GetService('manufacturing').ReloadBlueprints()
                    sm.GetService('manufacturing').ReloadInstallations()
                    completingInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CompletingInstallation')
                    sm.GetService('loading').ProgressWnd(installingJobLabel, completingInstallationLabel, 3, 4)
                    form.ManufacturingInstallation.CloseIfOpen()
                except UserError as what:

                    def f():
                        raise what


                    uthread.new(f)
                    sys.exc_clear()
                    finishingText = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CancellingInstallation')
                    sm.GetService('loading').ProgressWnd(installingJobLabel, cancellingInstallationLabel, 3, 4)
            else:
                finishingText = cancellingInstallationLabel
        sm.GetService('loading').ProgressWnd(installingJobLabel, finishingText, 4, 4)



    def ReloadBlueprints(self, windowClass = None, args = ('persBlueprints', 'sciAndIndustryCorpBlueprintsTab')):
        windowClass = windowClass or form.Manufacturing
        now = blue.os.GetWallclockTimeNow()
        self.lastReloadBlueprintsCallTime = now
        blue.pyos.synchro.SleepWallclock(1000)
        if now != self.lastReloadBlueprintsCallTime:
            return 
        wnd = windowClass.GetIfOpen()
        if wnd is None or wnd.destroyed:
            return 
        uthread.Lock(self, 'ReloadBlueprints')
        try:
            sm.GetService('invCache').InvalidateGlobal()
            wnd = windowClass.GetIfOpen()
            if wnd and wnd.sr.maintabs.GetSelectedArgs() in args:
                wnd.sr.maintabs.ReloadVisible()
            wnd = form.AssetsWindow.GetIfOpen()
            if wnd:
                wnd.sr.maintabs.ReloadVisible()

        finally:
            uthread.UnLock(self, 'ReloadBlueprints')




    def ReloadInstallations(self):
        wnd = form.Manufacturing.GetIfOpen()
        if wnd and getattr(wnd.sr.installationsParent, 'inited', 0):
            selected = wnd.sr.installationsParent.sr.installationsScroll.GetSelected()
            if selected:
                selected = selected[0].idx
            else:
                selected = None
            wnd.sr.installationsParent.LoadInstallations()
            if selected is not None:
                wnd.sr.installationsParent.sr.installationsScroll.SetSelected(selected)



    def GetActivityName(self, activityID):
        self.PopulateActivities()
        if activityID in self.activitiesIdx:
            labelPath = self.activitiesIdx[activityID]
            return localization.GetByLabel(labelPath)
        else:
            return localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/UnknownID', activityId=activityID)



    def GetPathToItem(self, item):
        invLocationID = None
        invGroupID = None
        path = []
        itemSpecification = []
        itemSpecification.append(item.itemID)
        if item.flagID == const.flagCargo:
            if util.IsStation(eve.session.locationid):
                invLocationID = eve.session.locationid
                invGroupID = const.groupStation
                path.append([eve.session.locationid, eve.session.charid, const.flagHangar])
            else:
                invLocationID = eve.session.solarsystemid
                invGroupID = const.groupSolarSystem
            path.append([item.locationID, item.ownerID, item.flagID])
        else:
            flagHangarOrCorpHangar = (const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7)
            if item.flagID in flagHangarOrCorpHangar:
                if util.IsStation(item.locationID) and item.ownerID == eve.session.charid:
                    invLocationID = item.locationID
                    invGroupID = const.groupStation
                    path.append([item.locationID, item.ownerID, item.flagID])
                elif item.locationID == eve.session.shipid and item.ownerID == eve.session.charid:
                    invLocationID = eve.session.locationid
                    if util.IsStation(eve.session.locationid):
                        invGroupID = const.groupStation
                        path.append([invLocationID, item.ownerID, const.flagHangar])
                    else:
                        invGroupID = const.groupSolarSystem
                    path.append([item.locationID, item.ownerID, item.flagID])
                else:
                    (stationID, officeFolderID, officeID,) = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(item)
                    if officeID is not None:
                        path.append([stationID, const.ownerStation, 0])
                        path.append([officeFolderID, eve.session.corpid, const.flagHangar])
                        path.append([officeID, eve.session.corpid, item.flagID])
                        invLocationID = stationID
                        invGroupID = const.groupStation
                    else:
                        invLocationID = eve.session.locationid
                        invGroupID = const.groupSolarSystem
                        path.append([item.locationID, item.ownerID, item.flagID])
        if invGroupID is None or invLocationID is None:
            raise UserError('RamInstalledItemBadLocation')
        invLocation = [invLocationID, invGroupID]
        return [invLocation, path, itemSpecification]




class BlueprintData():
    __guid__ = 'xtriui.BlueprintData'

    def CanSeeCorpBlueprints(self):
        return session.corprole & (const.corpRoleCanRentResearchSlot | const.corpRoleFactoryManager | const.corpRoleCanRentFactorySlot) > 0



    def GetLocationData(self, solarsystemID, station, key, expanded = 0, isCorp = 0, scrollID = None):
        location = cfg.evelocations.Get(station.stationID)
        if getattr(self, 'invalidateOpenState', 1):
            uicore.registry.SetListGroupOpenState(('rmpickpblocations', location.locationID), 0)
            self.invalidateOpenState = 0
        jumps = int(sm.GetService('pathfinder').GetJumpCountFromCurrent(solarsystemID))
        label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfBlueprintsNumberOfJumps', locationName=location.name, blueprints=station.blueprintCount, jumps=jumps)
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetBlueprintMenu,
         'label': label,
         'groupItems': [],
         'id': ('rmpickpblocations', location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'isCorp': isCorp,
         'officeID': getattr(station, 'officeID', None),
         'solarsystemID': solarsystemID,
         'scrollID': scrollID}
        return data



    def GetLocationDataStructure(self, solarsystemID, structure, key, expanded = 0, isCorp = 0, locationName = None, scrollID = None):
        location = cfg.evelocations.Get(structure.structureID)
        if getattr(self, 'invalidateOpenState', 1):
            uicore.registry.SetListGroupOpenState(('rmpickpblocations', location.locationID), 0)
            self.invalidateOpenState = 0
        jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarsystemID)
        label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfJumps', locationName=locationName, jumps=int(jumps))
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetBlueprintMenu,
         'label': label,
         'groupItems': [],
         'id': ('rmpickpblocations', location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'isCorp': isCorp,
         'officeID': getattr(structure, 'officeID', structure.structureID),
         'solarsystemID': solarsystemID,
         'scrollID': scrollID}
        return data



    def GetLocationDataCargo(self, blueprintCount, key, isCorp = 0, scrollID = None):
        location = cfg.evelocations.Get(eve.session.shipid)
        if getattr(self, 'invalidateOpenState', 1):
            uicore.registry.SetListGroupOpenState(('rmpickpblocations', eve.session.shipid), 0)
            self.invalidateOpenState = 0
        jumps = 0
        label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfItemsNumberOfJumps', locationName=location.name, items=blueprintCount, jumps=int(jumps))
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetBlueprintMenu,
         'label': label,
         'groupItems': [],
         'id': ('rmpickpblocations', location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'isCorp': isCorp,
         'officeID': None,
         'solarsystemID': eve.session.solarsystemid2,
         'scrollID': scrollID}
        return data



    def GetBlueprintMenu(self, node):
        stationInfo = sm.GetService('ui').GetStation(node.location.locationID)
        if not stationInfo:
            return sm.GetService('menu').CelestialMenu(node.location.locationID)
        return sm.GetService('menu').CelestialMenu(node.location.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)



    def GetSubContent(self, data, *args):
        solarsystemID = data.solarsystemID
        stationID = data.location.locationID
        locationID = data.officeID or data.location.locationID
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationBlueprintItems(locationID, data.location.locationID, data.isCorp)
        isCorp = data.isCorp
        scrollID = data.scrollID
        if isCorp:
            divisionFilter = self.sr.blueprintDivisionFilter.GetValue()
            if util.IsStation(stationID):
                sm.GetService('corp').GetLockedItemsByLocation(stationID)
        key = ['pers', 'corp'][isCorp]
        combo = self.sr.Get('%s_blueprintCopyFilter' % key, None)
        copyFilter = combo.GetValue()
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        scrolllist = []
        for each in items:
            if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            if isCorp and divisionFilter[1] and each.flagID != divisionFilter[1]:
                continue
            item = util.KeyVal()
            blueprint = util.KeyVal()
            for colName in items.header:
                colName = colName[0]
                if colName not in ('productivityLevel', 'materialLevel', 'copy', 'licensedProductionRunsRemaining'):
                    setattr(item, colName, getattr(each, colName))
                else:
                    value = getattr(each, colName)
                    if value is None:
                        if colName in ('productivityLevel', 'materialLevel', 'copy', 'flagID'):
                            value = 0
                        if colName == 'licensedProductionRunsRemaining':
                            value = -1
                    setattr(blueprint, colName, value)

            typeOb = cfg.invtypes.Get(each.typeID)
            item.groupID = typeOb.groupID
            item.categoryID = typeOb.categoryID
            if copyFilter is not None:
                if blueprint.copy != copyFilter:
                    continue
            data = uix.GetItemData(item, 'details', 1, scrollID=scrollID)
            data.listvalue = item
            data.blueprint = blueprint
            if isCorp:
                data.locked = sm.GetService('corp').IsItemLocked(item)
            data.factionID = sm.GetService('faction').GetFactionOfSolarSystem(solarsystemID)
            noLabel = localization.GetByLabel('UI/Common/No')
            yesLabel = localization.GetByLabel('UI/Common/Yes')
            isCopy = [noLabel, yesLabel][blueprint.copy]
            ml = blueprint.materialLevel
            pl = blueprint.productivityLevel
            lprr = blueprint.licensedProductionRunsRemaining
            if lprr == -1:
                lprr = ''
            copyLabel = localization.GetByLabel('UI/Common/Copy')
            mlLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ML')
            plLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PL')
            runsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Runs')
            data.Set('sort_%s' % copyLabel, isCopy)
            data.Set('sort_%s' % mlLabel, ml)
            data.Set('sort_%s' % plLabel, pl)
            data.Set('sort_%s' % runsLabel, lprr)
            scrolllist.append(listentry.Get('InvBlueprintItem', data=data))

        return scrolllist



    def OnGroupDeleted(self, ids):
        pass



    def OnGroupDragEnter(self, group, drag):
        pass



    def Error(self, *args):
        pass




class ItemByGroupData():
    __guid__ = 'xtriui.ItemByGroupData'

    def GetLocationData(self, solarsystemID, station, groupID, key, expanded = 0, isCorp = 0, scrollID = None):
        location = cfg.evelocations.Get(station.stationID)
        if getattr(self, 'invalidateOpenState', 1):
            uicore.registry.SetListGroupOpenState(('rmpickpblocations', location.locationID), 0)
            self.invalidateOpenState = 0
        jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarsystemID)
        label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfJumps', locationName=location.name, jumps=int(jumps))
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetItemMenu,
         'label': label,
         'groupItems': [],
         'id': ('rmpickpblocations', location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'isCorp': isCorp,
         'officeID': getattr(station, 'officeID', None),
         'solarsystemID': solarsystemID,
         'groupID': groupID,
         'scrollID': scrollID}
        return data



    def GetLocationDataStructure(self, solarsystemID, structure, key, expanded = 0, isCorp = 0, locationName = None, scrollID = None):
        location = cfg.evelocations.Get(structure.structureID)
        if getattr(self, 'invalidateOpenState', 1):
            uicore.registry.SetListGroupOpenState(('rmpickpblocations', location.locationID), 0)
            self.invalidateOpenState = 0
        jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarsystemID)
        label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfItemsNumberOfJumps', locationName=location.name, items=station.blueprintCount, jumps=int(jumps))
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetItemMenu,
         'label': label,
         'groupItems': [],
         'id': ('rmpickpblocations', location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'isCorp': isCorp,
         'officeID': getattr(structure, 'officeID', structure.structureID),
         'solarsystemID': solarsystemID,
         'scrollID': scrollID}
        return data



    def GetItemMenu(self, node):
        stationInfo = sm.GetService('ui').GetStation(node.location.locationID)
        return sm.GetService('menu').CelestialMenu(node.location.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)



    def GetSubContent(self, data, *args):
        solarsystemID = data.solarsystemID
        stationID = data.location.locationID
        locationID = data.officeID or data.location.locationID
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(locationID)
        isCorp = data.isCorp
        scrollID = data.scrollID
        if isCorp:
            divisionFilter = self.sr.blueprintDivisionFilter.GetValue()
        key = ['pers', 'corp'][isCorp]
        combo = self.sr.Get('%s_blueprintCopyFilter' % key, None)
        isCopies = combo.GetValue()
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        scrolllist = []
        for each in items:
            if each.groupID != self.groupID and self.groupID > 0:
                continue
            if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            if isCorp and divisionFilter[1] and each.flagID != divisionFilter[1]:
                continue
            if isCopies != None and (isCopies == 1 and each.copy or isCopies == 0 and not each.copy):
                continue
            (header, line,) = ([], [])
            (bpheader, bpline,) = (['blueprintID'], [each.itemID])
            for colName in each.header:
                header.append(colName)
                line.append(getattr(each, colName))

            typeOb = cfg.invtypes.Get(each.typeID)
            header.append('groupID')
            line.append(typeOb.groupID)
            header.append('categoryID')
            line.append(typeOb.categoryID)
            item = util.Row(header, line)
            blueprint = util.Row(bpheader, bpline)
            data = uix.GetItemData(item, 'details', 1, scrollID=scrollID)
            data.listvalue = item
            data.blueprint = blueprint
            data.factionID = sm.GetService('faction').GetFactionOfSolarSystem(solarsystemID)
            scrolllist.append(listentry.Get('InvItem', data=data))

        return scrolllist



    def OnGroupDeleted(self, ids):
        pass



    def OnGroupDragEnter(self, group, drag):
        pass



    def Error(self, *args):
        pass




class Manufacturing(uicls.Window, BlueprintData):
    __guid__ = 'form.Manufacturing'
    default_width = 635
    default_height = 500
    default_windowID = 'manufacturing'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        activeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Filters/AnyActiveState')
        pendingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Pending')
        inProgressLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InProgress')
        readyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Ready')
        deliveredLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Delivered')
        states = [(None, activeLabel),
         (const.ramJobStatusPending, pendingLabel),
         (const.ramJobStatusInProgress, inProgressLabel),
         (const.ramJobStatusReady, readyLabel),
         (const.ramJobStatusDelivered, deliveredLabel)]
        self.states = [ (stateID, text) for (stateID, text,) in states ]
        self.scope = 'all'
        sAndILabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ScienceAndIndustry')
        self.SetCaption(sAndILabel)
        self.LoadTabs()
        self.SetWndIcon('ui_57_64_9', mainTop=-10)
        self.SetMinSize([635, 500])
        capt = uicls.WndCaptionLabel(text=sAndILabel, parent=self.sr.topParent, align=uiconst.TOPLEFT, left=70, top=10)
        self.sr.caption = capt
        panelName = attributes.panelName
        if panelName is not None:
            uthread.new(self.sr.maintabs.ShowPanelByName, panelName)



    def _OnClose(self, *args):
        if getattr(self, 'jobsinited', 0):
            settings.user.ui.Set('factory_statefilter', self.sr.stateFilter.GetValue())
            settings.user.ui.Set('factory_ownerfilter', self.sr.ownerFilter.GetValue())
            settings.user.ui.Set('factory_creatorfilter', self.sr.creatorFilter.GetValue())
            settings.user.ui.Set('factory_locationfilter', self.sr.locationFilter.GetValue())
            settings.user.ui.Set('factory_fromdatefilter', self.sr.jobsFromDate.GetValue())
        if getattr(self, 'corpBlueprintsInited', 0):
            settings.user.ui.Set('blueprint_divisionfilter', self.sr.blueprintDivisionFilter.GetValue())
            settings.user.ui.Set('corp_blueprint_copyfilter', self.sr.corp_blueprintCopyFilter.GetValue())
        if getattr(self, 'persBlueprintsInited', 0):
            settings.user.ui.Set('pers_blueprint_copyfilter', self.sr.pers_blueprintCopyFilter.GetValue())



    def LoadTabs(self):
        self.sr.main.Flush()
        self.sr.jobsParent = uicls.Container(name='jobsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.persBlueprintsParent = uicls.Container(name='persBlueprintsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        self.sr.installationsParent = xtriui.InstallationPanel(name='installationsParent', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.planetParent = xtriui.PlanetPanel(name='planetParent', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.settingsParent = uicls.Container(name='settingsParent', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.corpBlueprintsParent = uicls.Container(name='corpBlueprintsParent', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_HIDDEN, idx=1)
        planetsLabel = localization.GetByLabel('UI/Common/Planets')
        jobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Jobs')
        blueprintsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Blueprints')
        installationsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Installations')
        settingsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Settings')
        tabs = uicls.TabGroup(name='factoryTabs', parent=self.sr.main, idx=0)
        tabContent = []
        tabContent.append([jobsLabel,
         self.sr.jobsParent,
         self,
         'jobs'])
        tabContent.append([blueprintsLabel,
         self.sr.persBlueprintsParent,
         self,
         'persBlueprints'])
        if not util.IsNPC(eve.session.corpid) and self.CanSeeCorpBlueprints():
            corpBlueprintsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CorporationBlueprints')
            tabContent.append([corpBlueprintsLabel,
             self.sr.corpBlueprintsParent,
             self,
             'sciAndIndustryCorpBlueprintsTab'])
        tabContent.append([installationsLabel,
         self.sr.installationsParent,
         self,
         'installations'])
        tabContent.append([planetsLabel,
         self.sr.planetParent,
         self,
         'planets'])
        tabContent.append([settingsLabel,
         self.sr.settingsParent,
         self,
         'settings'])
        tabs.Startup(tabContent, 'factoryTabs', UIIDPrefix='scienceAndIndustryTab')
        self.sr.maintabs = tabs



    def Load(self, key):
        self.sr.detailtimer = None
        self.sr.limits = self.GetSkillLimits()
        delayLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Delayed5Minutes')
        if key == 'jobs':
            self.ShowJobs()
        elif key == 'persBlueprints':
            self.ShowBlueprints()
            self.sr.caption.SetSubcaption(delayLabel)
        elif key == 'sciAndIndustryCorpBlueprintsTab':
            self.sr.caption.SetSubcaption(delayLabel)
            self.ShowBlueprints(1)
        elif key == 'installations':
            self.sr.caption.SetSubcaption(delayLabel)
            self.ShowInstallations()
        elif key == 'planets':
            self.ShowPlanets()
        elif key == 'settings':
            self.ShowSettings()
        if key not in ('installations', 'persBlueprints', 'sciAndIndustryCorpBlueprintsTab'):
            self.sr.caption.SetSubcaption('')



    def ShowInstallations(self):
        if not getattr(self.sr.installationsParent, 'inited', 0):
            self.sr.installationsParent.Init()



    def ShowPlanets(self):
        if not getattr(self.sr.planetParent, 'inited', 0):
            self.sr.planetParent.Init()



    def ReloadTabs(self):
        self.settingsinited = 0
        self.jobsinited = 0
        self.persBlueprintsInited = 0
        self.corpBlueprintsInited = 0
        self.LoadTabs()



    def ShowBlueprints(self, isCorp = 0):
        key = ['pers', 'corp'][isCorp]
        if not getattr(self, '%sBlueprintsInited' % key, 0):
            bpParent = self.sr.Get('%sBlueprintsParent' % key, None)
            filters = uicls.Container(name='filters', parent=bpParent, height=33, align=uiconst.TOTOP)
            allLabel = localization.GetByLabel('UI/Common/All')
            copiesLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Copies')
            originalsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Originals')
            copies = [(allLabel, None), (copiesLabel, 1), (originalsLabel, 0)]
            typeLabel = localization.GetByLabel('UI/Common/Type')
            c = uicls.Combo(label=typeLabel, parent=filters, options=copies, name='copies', select=settings.user.ui.Get('%s_blueprint_copyfilter' % key, None), callback=self.BlueprintComboChange, pos=(5, 0, 0, 0), align=uiconst.TOPLEFT)
            c.top = top = -c.sr.label.top
            filters.height = c.top + c.height
            setattr(self.sr, '%s_blueprintCopyFilter' % key, c)
            if isCorp:
                divisions = sm.GetService('manufacturing').GetAvailableHangars(canView=0, canTake=0)
                divisions.insert(0, (allLabel, (None, None)))
                divisionLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Division')
                c = uicls.Combo(label=divisionLabel, parent=filters, options=divisions, name='divisions', select=settings.user.ui.Get('blueprint_divisionfilter', (None, None)), callback=self.BlueprintComboChange, pos=(self.sr.corp_blueprintCopyFilter.left + self.sr.corp_blueprintCopyFilter.width + 4,
                 top,
                 0,
                 0), align=uiconst.TOPLEFT)
                self.sr.blueprintDivisionFilter = c
            scroll = uicls.Scroll(parent=bpParent, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            scroll.sr.id = '%sBlueprintsScroll' % key
            scroll.multiSelect = 0
            setattr(self.sr, '%sBlueprintsScroll' % key, scroll)
            setattr(self, '%sBlueprintsInited' % key, 1)
            par = uicls.Container(name='infoParent', parent=bpParent, align=uiconst.TOBOTTOM, height=68, idx=0)
            (skillLevels, attributeValues,) = sm.GetService('manufacturing').GetRelevantCharSkills()
            maxManufacturingJobCount = int(attributeValues[const.attributeManufactureSlotLimit])
            maxResearchJobCount = int(attributeValues[const.attributeMaxLaborotorySlots])
            collection = []
            maxManufacturingJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumManufacturingJobs', value=maxManufacturingJobCount)
            maxResearchJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumResearchJobs', value=maxResearchJobCount)
            left = 3
            t = uicls.EveLabelMedium(text=maxManufacturingJobsLabel + '<br>' + maxResearchJobsLabel, parent=par, left=left, top=0, tabs=[170, 220])
            uicls.Line(parent=par, align=uiconst.RELATIVE, width=1, height=64, left=222)
            collection.append(t)
            left = +228
            remoteAbilityList = []
            limitedToStationsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LimitedToStations')
            rmjLimit = self.sr.limits['remoteManufacturingJob']
            rrjLimit = self.sr.limits['remoteResearchJob']
            if rmjLimit == -1 and rrjLimit == -1:
                remoteAbilityList = [limitedToStationsLabel, limitedToStationsLabel]
            else:
                limitedToSystemsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LimitedToSolarSystems')
                limitedToRegionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LimitedToRegions')
                limitedToJumpsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LimetedToJumps', jumps=rmjLimit)
                if rmjLimit == -1:
                    rmjText = limitedToStationsLabel
                elif rmjLimit == 0:
                    rmjText = limitedToSystemsLabel
                elif rmjLimit == 50:
                    rmjText = limitedToRegionsLabel
                else:
                    rmjText = limitedToJumpsLabel
                if rrjLimit == -1:
                    rrjText = limitedToStationsLabel
                elif rrjLimit == 0:
                    rrjText = limitedToSystemsLabel
                elif rrjLimit == 50:
                    rrjText = limitedToRegionsLabel
                else:
                    rrjText = limitedToJumpsLabel
                remoteAbilityList = [rmjText, rrjText]
            remoteManufacturingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RemoteManufacturing')
            remoteResearchLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RemoteResearch')
            t = uicls.EveLabelMedium(text='%s<t><right>%s<br>%s<t><right>%s' % (remoteManufacturingLabel,
             remoteAbilityList[0],
             remoteResearchLabel,
             remoteAbilityList[1]), parent=par, left=left, top=0, tabs=[160, 328])
            collection.append(t)
            par.height = max(par.height, max([ each.textheight for each in collection ]) + 6)
        else:
            scroll = self.sr.Get('%sBlueprintsScroll' % key, None)
        defaultHeaders = uix.GetInvItemDefaultHeaders()
        copyLabel = localization.GetByLabel('UI/Common/Copy')
        mlLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ML')
        plLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PL')
        runsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Runs')
        headers = defaultHeaders[:4] + [copyLabel,
         mlLabel,
         plLabel,
         runsLabel]
        scroll.SetColumnsHiddenByDefault(defaultHeaders[4:])
        scrolllist = []
        accessScrollHint = ''
        sortlocations = sm.GetService('assets').GetAll('regitems', blueprintOnly=1, isCorp=isCorp)
        scrolllist = []
        if eve.session.solarsystemid is not None:
            dist = 0
            bp = sm.StartService('michelle').GetBallpark()
            if bp:
                invCache = sm.GetService('invCache')
                for ballID in bp.balls.iterkeys():
                    slimItem = bp.GetInvItem(ballID)
                    if slimItem is None or slimItem.groupID not in (const.groupAssemblyArray, const.groupMobileLaboratory):
                        continue
                    locationName = cfg.evelocations.Get(ballID).locationName
                    if not (locationName and locationName[0] != '@'):
                        locationName = cfg.invtypes.Get(slimItem.typeID).typeName
                    otherBall = bp and bp.GetBall(ballID) or None
                    ownBall = bp and bp.GetBall(eve.session.shipid) or None
                    dist = otherBall and max(0, otherBall.surfaceDist)
                    if dist is None:
                        dist = 2 * const.maxCargoContainerTransferDistance
                    if dist >= const.maxCargoContainerTransferDistance:
                        text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationOutOfRangeMaxRange', locationName=locationName, maxRange=const.maxCargoContainerTransferDistance)
                        scrolllist.append(listentry.Get('Text', {'text': text}))
                    else:
                        blueprintCount = 0
                        inv = invCache.GetInventoryFromId(ballID)
                        for invItem in inv.List():
                            if invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
                                blueprintCount += 1

                        if blueprintCount > 0:
                            structure = util.KeyVal()
                            structure.structureID = ballID
                            structure.blueprintCount = blueprintCount
                            locationData = self.GetLocationDataStructure(eve.session.solarsystemid, structure, 'allitems', isCorp=isCorp, locationName=locationName, scrollID=scroll.sr.id)
                            scrolllist.append(listentry.Get('Group', locationData))

        for (solarsystemID, station,) in sortlocations:
            if station.blueprintCount:
                scrolllist.append(listentry.Get('Group', self.GetLocationData(solarsystemID, station, 'allitems', isCorp=isCorp, scrollID=scroll.sr.id)))

        if not len(scrolllist):
            regionName = cfg.evelocations.Get(eve.session.regionid).name
            if bool(isCorp):
                accessScrollHint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoCorporationBlueprintInRegion', regionName=regionName)
            else:
                accessScrollHint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoBlueprintInRegion', regionName=regionName)
        if scroll.destroyed:
            return 
        scroll.Load(contentList=scrolllist, headers=headers)
        scroll.ShowHint(accessScrollHint)



    def BlueprintComboChange(self, *args):
        if getattr(self, 'corpBlueprintsInited', 0):
            settings.user.ui.Set('blueprint_divisionfilter', self.sr.blueprintDivisionFilter.GetValue())
            settings.user.ui.Set('corp_blueprint_copyfilter', self.sr.corp_blueprintCopyFilter.GetValue())
        if getattr(self, 'persBlueprintsInited', 0):
            settings.user.ui.Set('pers_blueprint_copyfilter', self.sr.pers_blueprintCopyFilter.GetValue())
        sm.GetService('manufacturing').ReloadBlueprints()



    def GetSkillLimits(self):
        jumpsPerSkillLevel = {0: -1,
         1: 0,
         2: 5,
         3: 10,
         4: 20,
         5: 50}
        limits = {}
        currentOpen = 0
        myskills = sm.GetService('skills').MySkillLevelsByID()
        researchLevel = myskills.get(const.typeResearch, 0)
        industryLevel = myskills.get(const.typeIndustry, 0)
        metallurgyLevel = myskills.get(const.typeMetallurgy, 0)
        massProductionLevel = myskills.get(const.typeMassProduction, 0)
        advancedMassProductionLevel = myskills.get(const.typeAdvancedMassProduction, 0)
        laboratoryOperationLevel = myskills.get(const.typeLaboratoryOperation, 0)
        advancedLabOpLevel = myskills.get(const.typeAdvancedLaboratoryOperation, 0)
        supplyChainManagementLevel = myskills.get(const.typeSupplyChainManagement, 0)
        scientificNetworkingLevel = myskills.get(const.typeScientificNetworking, 0)
        maxManufacturingJobs = 1 + massProductionLevel + advancedMassProductionLevel
        maxResearchJobs = 1 + laboratoryOperationLevel + advancedLabOpLevel
        limits['maxManufacturingJob'] = maxManufacturingJobs
        limits['maxResearchJob'] = maxResearchJobs
        limits['remoteManufacturingJob'] = jumpsPerSkillLevel[supplyChainManagementLevel]
        limits['remoteResearchJob'] = jumpsPerSkillLevel[scientificNetworkingLevel]
        return limits



    def ShowSettings(self):
        if not getattr(self, 'settingsinited', 0):
            parent = self.sr.settingsParent
            settingsInOutLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SettingsInputOutput')
            settingsByBpLocationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/DefinedByBlueprintHangarLocation')
            settingsByUserDefLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/DefinedByUser')
            filteringOptionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FilteringOptions')
            details = uicls.Container(name='col2', align=uiconst.TOALL, parent=parent, pos=(const.defaultPadding,
             0,
             const.defaultPadding,
             0))
            uicls.Frame(parent=details, color=(1.0, 1.0, 1.0, 0.2), idx=0)
            uix.GetContainerHeader(settingsInOutLabel, details, 0)
            uicls.Container(name='push', align=uiconst.TOLEFT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TORIGHT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            for (height, label, configname, retval, checked, groupname,) in [(12,
              settingsByBpLocationLabel,
              'manufacturingfiltersetting1',
              0,
              settings.user.ui.Get('manufacturingfiltersetting1', 0) == 0,
              'manufacturingfiltersetting1'), (12,
              settingsByUserDefLabel,
              'manufacturingfiltersetting1',
              1,
              settings.user.ui.Get('manufacturingfiltersetting1', 0) == 1,
              'manufacturingfiltersetting1')]:
                cb = uicls.Checkbox(text=label, parent=details, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.ChangeFilter)
                cb.hint = label

            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=details)
            uix.GetContainerHeader(filteringOptionsLabel, details, xmargin=-6)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            masks = [ (12,
             maskName,
             'assemblyLineFilterCheckBox%s' % maskConst,
             maskConst,
             settings.user.ui.Get('assemblyLineFilterCheckBox%s' % maskConst, maskConst) == maskConst,
             None) for (maskName, maskID, maskConst,) in sm.GetService('manufacturing').GetRestrictionMasks() ]
            for (height, label, configname, retval, checked, groupname,) in masks:
                cb = uicls.Checkbox(text=label, parent=details, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.ChangeFilter)
                cb.hint = label

            self.settingsinited = 1



    def ChangeFilter(self, checkbox):
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if checkbox.data.has_key('value'):
                value = checkbox.data['value']
                if value is None:
                    settings.user.ui.Set(config, checkbox.checked)
                else:
                    settings.user.ui.Set(config, value)
        if checkbox and checkbox.name.startswith('assemblyLineFilterCheckBox'):
            xtriui.InstallationPanel().OnCheckboxChange(checkbox)



    def ShowJobs(self):
        if not getattr(self, 'jobsinited', 0):
            details = uicls.Container(name='details', parent=self.sr.jobsParent, height=70, align=uiconst.TOBOTTOM, idx=1)
            self.sr.details = details
            filters = uicls.Container(name='filters', parent=self.sr.jobsParent, height=48, align=uiconst.TOTOP)
            self.sr.filters = filters
            filteringOptionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FilteringOptions')
            uicls.EveLabelSmall(text=filteringOptionsLabel, parent=filters, left=8, top=3)
            a = uicls.EveLabelSmall(text='', parent=filters, left=18, top=3, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
            a.OnClick = self.ToggleAdvancedFilters
            a.GetMenu = None
            self.sr.ml = a
            expander = uicls.Sprite(parent=filters, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderUp.png', align=uiconst.TOPRIGHT)
            expander.OnClick = self.ToggleAdvancedFilters
            self.sr.jobsAdvanceExp = expander
            self.sr.activities = [ (localization.GetByLabel(labelPath), actID) for (actID, labelPath,) in sm.GetService('manufacturing').GetActivities() ]
            activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
            c = uicls.Combo(label=activityLabel, parent=filters, options=self.sr.activities, name='activity', select=settings.user.ui.Get('factory_activityfilter', None), callback=self.ComboChange, pos=(5, 1, 0, 0), width=114, align=uiconst.TOPLEFT)
            self.sr.activityFilter = c
            c.top = top = -c.sr.label.top + 4 + 15
            self.sr.states = [ (text, actID) for (actID, text,) in self.states ]
            stateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/State')
            c = uicls.Combo(label=stateLabel, parent=filters, options=self.sr.states, name='state', select=settings.user.ui.Get('factory_statefilter', None), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.stateFilter = c
            self.sr.ranges = [ (text, locationData) for (locationData, text,) in sm.GetService('manufacturing').GetRanges(True) ]
            rangeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Range')
            c = uicls.Combo(label=rangeLabel, parent=filters, options=self.sr.ranges, name='location', select=settings.user.ui.Get('factory_locationfilter', (eve.session.regionid, const.groupRegion)), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.locationFilter = c
            meLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Me')
            opts = [(meLabel, eve.session.charid)]
            if self.CanSeeCorpJobs():
                myCorpLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MyCorporation')
                opts.append((myCorpLabel, eve.session.corpid))
            self.sr.owners = opts
            ownerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Owner')
            c = uicls.Combo(label=ownerLabel, parent=filters, options=self.sr.owners, name='owner', select=settings.user.ui.Get('factory_ownerfilter', None), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.ownerFilter = c
            self.inadvHeight = c.top + c.height
            rowTop = -c.sr.label.top + c.top + c.height + 6
            anyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Any')
            self.sr.creators = [(anyLabel, None), (meLabel, eve.session.charid)]
            c = uicls.Combo(label=localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Creator'), parent=filters, options=self.sr.creators, name='creator', select=settings.user.ui.Get('factory_creatorfilter', None), callback=self.ComboChange, pos=(5,
             rowTop,
             0,
             0), align=uiconst.TOPLEFT)
            self.sr.creatorFilter = c
            fromDateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FromDate')
            fromDate = uicls.SinglelineEdit(name=fromDateLabel, parent=filters, setvalue=settings.user.ui.Get('factory_fromdatefilter', self.GetOffsetTime(-DAY)), align=uiconst.TOPLEFT, pos=(c.left + c.width + 4,
             rowTop,
             86,
             0), maxLength=16, label=fromDateLabel)
            self.sr.jobsFromDate = fromDate
            toDateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ToDate')
            toDate = uicls.SinglelineEdit(name=toDateLabel, parent=filters, setvalue=self.GetNow(), align=uiconst.TOPLEFT, pos=(fromDate.left + fromDate.width + 4,
             rowTop,
             86,
             0), maxLength=16, label=toDateLabel)
            self.sr.jobsToDate = toDate
            self.advHeight = toDate.top + toDate.height
            getJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GetJobsCommand')
            submit = uicls.Button(parent=filters, label=getJobsLabel, func=self.LoadJobs, pos=(6, 2, 0, 0), btn_default=1, align=uiconst.BOTTOMRIGHT)
            self.sr.jobsScroll = uicls.Scroll(parent=self.sr.jobsParent, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.jobsScroll.sr.id = 'jobsScroll'
            self.sr.jobsScroll.multiSelect = 1
            hintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ClickGetJobsWithFilters')
            self.sr.jobsScroll.ShowHint(hintLabel)
            self.jobsinited = 1
            advanced = not settings.user.ui.Get('advancedManuFilters', 0)
            settings.user.ui.Set('advancedManuFilters', advanced)
            self.ToggleAdvancedFilters()



    def CanSeeCorpJobs(self):
        roles = [const.corpRoleDirector, const.corpRoleFactoryManager]
        canseejobs = False
        for role in roles:
            if eve.session.corprole & role == role:
                canseejobs = True

        return canseejobs



    def ComboChange(self, *args):
        pass



    def ToggleAdvancedFilters(self, *args):
        advanced = not settings.user.ui.Get('advancedManuFilters', 0)
        settings.user.ui.Set('advancedManuFilters', advanced)
        if advanced:
            self.sr.jobsAdvanceExp.texturePath = 'res:/UI/Texture/Shared/expanderUp.png'
        else:
            self.sr.jobsAdvanceExp.texturePath = 'res:/UI/Texture/Shared/expanderDown.png'
        self.sr.filters.height = [self.inadvHeight, self.advHeight][advanced]
        showMoreOptionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ShowMoreOptions')
        showLessOptionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ShowFewerOptions')
        self.sr.ml.text = [showMoreOptionsLabel, showLessOptionsLabel][advanced]
        self.sr.creatorFilter.state = self.sr.jobsToDate.state = self.sr.jobsFromDate.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][advanced]



    def LoadJobs(self, *args):
        self.ShowLoad()
        hintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FetchingData')
        self.sr.jobsScroll.ShowHint(hintLabel)
        self.sr.jobsScroll.Load(contentList=[])
        uix.Flush(self.sr.details)
        if self.sr.Get('activeDetails'):
            self.sr.activeDetails = None
        activity = self.sr.activityFilter.GetValue()
        state = self.sr.stateFilter.GetValue()
        owner = self.sr.ownerFilter.GetValue()
        location = self.sr.locationFilter.GetValue()
        completed = state == const.ramJobStatusDelivered
        advanced = settings.user.ui.Get('advancedManuFilters', 0)
        if advanced:
            creator = self.sr.creatorFilter.GetValue()
            fdate = _fdate = self.sr.jobsFromDate.GetValue()
            try:
                fdate = util.ParseDate(fdate)
            except Exception as e:
                newDefaultFDate = self.GetOffsetTime(-MONTH)
                fdate = util.ParseDate(newDefaultFDate)
                self.sr.jobsFromDate.SetValue(newDefaultFDate)
            tdate = self.sr.jobsToDate.GetValue()
            try:
                tdate = util.ParseDate(tdate)
            except Exception as e:
                newDefaultTDate = self.GetNow()
                tdate = util.ParseDate(newDefaultTDate)
                self.sr.jobsToDate.SetValue(newDefaultTDate)
        else:
            creator = None
            fdate = None
            tdate = None
        try:
            jobs = sm.ProxySvc('ramProxy').GetJobs2(owner, completed)
        except:
            hintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FailedGetData')
            self.sr.jobsScroll.ShowHint(hintLabel)
            self.sr.jobsScroll.Load(contentList=[])
            self.HideLoad()
            return 
        scrolllist = []
        jumpsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Jumps')
        installDateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallDate')
        endDateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/EndDate')
        if jobs is not None:
            for j in jobs:
                if state and state != self.GetStateTextOrID(j)[1]:
                    continue
                if activity and activity != j.activityID:
                    continue
                if fdate is not None and j.installTime < fdate:
                    continue
                if tdate is not None and j.installTime >= tdate + const.DAY:
                    continue
                if location is not None:
                    (locationID, locationGroup,) = location
                    if locationGroup == const.groupStation:
                        if j.containerID != locationID:
                            continue
                    solarsystemID = j.containerLocationID
                    if locationGroup == const.groupSolarSystem:
                        if solarsystemID != locationID:
                            continue
                    constellationID = sm.GetService('map').GetParent(solarsystemID)
                    if locationGroup == const.groupConstellation:
                        if constellationID != locationID:
                            continue
                    regionID = sm.GetService('map').GetParent(constellationID)
                    if locationGroup == const.groupRegion:
                        if regionID != locationID:
                            continue
                j_creator = j.installerID
                if hasattr(j, 'creator'):
                    j_creator = j.creator
                if j_creator == creator or creator is None:
                    if j.pauseProductionTime is not None:
                        endProductionTime = util.FmtTimeInterval(j.endProductionTime - j.pauseProductionTime)
                    else:
                        endProductionTime = util.FmtDate(j.endProductionTime, 'ss')
                    jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(j.installedInSolarSystemID)
                    data = util.KeyVal()
                    label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (sm.GetService('manufacturing').GetActivityName(j.activityID),
                     cfg.invtypes.Get(j.installedItemTypeID).name,
                     self.GetJobLocationName(j.containerID, j.containerTypeID, j.containerLocationID),
                     localizationUtil.FormatNumeric(jumps, decimalPlaces=0, useGrouping=True),
                     cfg.eveowners.Get(j.installerID).name,
                     cfg.eveowners.Get(j.installedItemOwnerID).name,
                     util.FmtDate(j.installTime, 'ss'),
                     endProductionTime)
                    data.label = '%s<t>%s' % (self.GetStateTextOrID(j)[0], label)
                    data.labelNoStatus = label
                    data.OnClick = self.ClickJob
                    data.GetMenu = self.GetJobLineMenu
                    data.jobData = j
                    data.id = j.installedItemTypeID
                    data.Set('sort_%s' % jumpsLabel, jumps)
                    data.Set('sort_%s' % installDateLabel, j.installTime)
                    data.Set('sort_%s' % endDateLabel, j.endProductionTime)
                    scrolllist.append(listentry.Get('RMJobEntry', data=data))

        if not scrolllist:
            if activity or completed or owner or creator or location:
                hintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoJobsWithFilters')
                self.sr.jobsScroll.ShowHint(hintLabel)
            else:
                hintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoJobsInstalled')
                self.sr.jobsScroll.ShowHint(hintLabel)
        else:
            self.sr.jobsScroll.ShowHint()
            self.sr.jobsScroll.OnSelectionChange = self.SelectJob
            typeLabel = localization.GetByLabel('UI/Common/Type')
            activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
            stateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/State')
            ownerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Owner')
            locationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Location')
            installerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Installer')
            headers = [stateLabel,
             activityLabel,
             typeLabel,
             locationLabel,
             jumpsLabel,
             installerLabel,
             ownerLabel,
             installDateLabel,
             endDateLabel]
            self.sr.jobsScroll.Load(contentList=scrolllist, headers=headers)
        self.HideLoad()



    def GetJobLineMenu(self, entry):
        m = []
        if entry.sr.node.jobData:
            if eve.session.solarsystemid != entry.sr.node.jobData.installedInSolarSystemID:
                (itemID, typeID,) = (entry.sr.node.jobData.installedInSolarSystemID, entry.sr.node.jobData.containerTypeID)
            else:
                (itemID, typeID,) = (entry.sr.node.jobData.containerID, entry.sr.node.jobData.containerTypeID)
            locationCmdLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationCommand')
            m += [(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo, (entry.sr.node.id, None))]
            m += [None]
            m += [(locationCmdLabel, sm.GetService('menu').CelestialMenu(itemID=itemID, mapItem=None, typeID=typeID))]
            m += [None]
            (itemID, typeID,) = (entry.sr.node.jobData.installedItemID, entry.sr.node.jobData.installedItemTypeID)
            blueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Blueprint')
            m += [(blueprintLabel, sm.GetService('menu').GetMenuFormItemIDTypeID(itemID, typeID))]
            m += [None]
            installerID = entry.sr.node.jobData.installerID
            ownerID = entry.sr.node.jobData.installedItemOwnerID
            ownerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Owner')
            installerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Installer')
            menuCharacters = [(installerID, cfg.eveowners.Get(installerID).name, installerLabel), (ownerID, cfg.eveowners.Get(ownerID).name, ownerLabel)]
            for characterData in menuCharacters:
                tmp = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/JobLineMenuUser', char=characterData[0], role=characterData[2])
                menufunc = None
                if util.IsCharacter(characterData[0]):
                    m += [(tmp, sm.GetService('menu').CharacterMenu(characterData[0]))]
                elif util.IsCorporation(characterData[0]):
                    m += [(tmp, sm.GetService('menu').GetMenuFormItemIDTypeID(characterData[0], const.typeCorporation))]

        return m



    def ShowInfo(self, typeID, itemID):
        sm.GetService('info').ShowInfo(typeID, itemID)



    def GetJobLocationName(self, containerID, containerTypeID, containerLocationID):
        containerType = cfg.invtypes.Get(containerTypeID)
        if util.IsStation(containerID):
            installedItemLocationName = cfg.evelocations.Get(containerID).name
        elif containerType.groupID in (const.groupAssemblyArray, const.groupMobileLaboratory):
            cfg.evelocations.Prime([containerID])
            installedItemLocationName = cfg.evelocations.Get(containerID).name
            if not installedItemLocationName:
                installedItemLocationName = containerType.typeName
        else:
            installedItemLocationName = containerType.typeName
        return installedItemLocationName



    def GetStateTextOrID(self, jobdata):
        now = blue.os.GetWallclockTime()
        self.sr.stateText = ''
        self.sr.stateID = None
        if now >= jobdata.endProductionTime:
            if jobdata.completed == 1:
                self.sr.stateText = cfg.ramcompletedstatuses.Get(jobdata.completedStatus).completedStatusText
                self.sr.stateID = const.ramJobStatusDelivered
            if jobdata.completed == 0:
                if jobdata.pauseProductionTime is not None:
                    if util.IsStation(jobdata.containerID):
                        incapacitatedLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Incapacitated')
                        self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % incapacitatedLabel
                    else:
                        offlineLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Offline')
                        self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % offlineLabel
                    self.sr.stateID = const.ramJobStatusPending
                else:
                    readyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Ready')
                    self.sr.stateText = '<color=0xff00FF00>%s<color=0xffffffff>' % readyLabel
                    self.sr.stateID = const.ramJobStatusReady
        elif now < jobdata.beginProductionTime:
            pendingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Pending')
            self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % pendingLabel
            self.sr.stateID = const.ramJobStatusPending
        if now >= jobdata.beginProductionTime and now < jobdata.endProductionTime:
            inProgressLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InProgress')
            self.sr.stateText = '<color=0xFFFFFF00>%s<color=0xffffffff>' % inProgressLabel
            self.sr.stateID = const.ramJobStatusInProgress
        if jobdata.pauseProductionTime is not None:
            if util.IsStation(jobdata.containerID):
                incapacitatedLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Incapacitated')
                self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % incapacitatedLabel
            else:
                offlineLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Offline')
                self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % offlineLabel
            self.sr.stateID = const.ramJobStatusPending
        return (self.sr.stateText, self.sr.stateID)



    def ClickJob(self, entry):
        self.ShowJobDetails(entry.sr.node.jobData)



    def SelectJob(self, entry):
        if len(entry) == 1:
            self.ShowJobDetails(entry[0].panel.sr.node.jobData)



    def ShowJobDetails(self, jobdata):
        self.sr.detailtext = None
        uix.Flush(self.sr.details)
        self.sr.activeDetails = jobdata
        left = 3
        col1 = 100
        col2 = 415
        (stateText, stateID,) = self.GetStateTextOrID(self.sr.activeDetails)
        activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
        stateLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/State')
        outputLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/OutputLocation')
        t = uicls.EveLabelMedium(text='%s<t><right>%s' % (activityLabel, sm.GetService('manufacturing').GetActivityName(jobdata.activityID)), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col1, col2])
        t = uicls.EveLabelMedium(text='%s<t><right>%s' % (stateLabel, stateText), parent=self.sr.details, left=left, top=12, singleline=0, tabs=[col1, col2])
        t = uicls.EveLabelMedium(text='%s<t><right>%s' % (outputLabel, self.GetJobLocationName(jobdata.containerID, jobdata.containerTypeID, jobdata.containerLocationID)), parent=self.sr.details, left=left, top=36, singleline=1, tabs=[col1, col2])
        outputType = cfg.invtypes.Get(jobdata.outputTypeID)
        if jobdata.activityID != const.ramActivityReverseEngineering:
            runs = 1
            if not outputType.categoryID == const.categoryBlueprint:
                runs = jobdata.runs
            amount = runs * outputType.portionSize
            text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/UnitsOfType', items=amount, type=outputType)
            outputTypeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/OutputType')
            t = uicls.EveLabelMedium(text='%s<t><right>%s' % (outputTypeLabel, text), parent=self.sr.details, left=left, top=48, singleline=1, tabs=[col1, col2])
            left = +col2
            col3 = 100
            col4 = 160
            if jobdata.activityID == const.ramActivityResearchingTimeProductivity:
                installPELabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallPE')
                endPELabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/EndPE')
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (installPELabel, jobdata.installedItemProductivityLevel), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, col4])
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (endPELabel, jobdata.installedItemProductivityLevel + jobdata.runs), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
            if jobdata.activityID == const.ramActivityResearchingMaterialProductivity:
                installMELabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallME')
                endMELabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/EndME')
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (installMELabel, jobdata.installedItemMaterialLevel), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, col4])
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (endMELabel, jobdata.installedItemMaterialLevel + jobdata.runs), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
            if jobdata.activityID == const.ramActivityCopying:
                copiesLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Copies')
                productionRunsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductionRuns')
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (copiesLabel, jobdata.runs), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, 160])
                t = uicls.EveLabelMedium(text='%s<t><right>%s' % (productionRunsLabel, jobdata.licensedProductionRuns), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
        self.sr.detailtext = uicls.EveLabelMedium(text='', parent=self.sr.details, left=3, top=24, singleline=1, tabs=[130, col2])
        uicls.Line(parent=self.sr.details, align=uiconst.RELATIVE, width=1, height=64, left=col2)
        showDeliverButton = False
        sel = self.sr.jobsScroll.GetSelected()
        for entry in sel:
            if blue.os.GetWallclockTime() > entry.jobData.endProductionTime and not entry.jobData.completed and not entry.jobData.pauseProductionTime:
                showDeliverButton = True
                break

        if showDeliverButton:
            deliverLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Deliver')
            submit = uicls.Button(parent=self.sr.details, label=deliverLabel, func=self.Deliver, pos=(12, 10, 0, 0), align=uiconst.BOTTOMRIGHT)
        elif stateID != const.ramJobStatusDelivered:
            cancelJobLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CancelJobCommand')
            submit = uicls.Button(parent=self.sr.details, label=cancelJobLabel, func=self.CancelJob, pos=(12, 10, 0, 0), align=uiconst.BOTTOMRIGHT)
        self.UpdateDetails(0)
        if stateID in (const.ramJobStatusInProgress, const.ramJobStatusPending) and not jobdata.pauseProductionTime:
            self.sr.detailtimer = base.AutoTimer(1000, self.UpdateDetails)



    def Deliver(self, *args):
        if getattr(self, 'delivering', 0):
            return 
        self.delivering = 1
        self.sr.activeDetails = None
        try:
            sel = self.sr.jobsScroll.GetSelected()
            completingJobsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CompletingJobs')
            completingInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CompletingInstallation')
            sm.GetService('loading').ProgressWnd(completingJobsLabel, completingInstallationLabel, 1, 2)
            blue.pyos.synchro.SleepWallclock(1000)
            for entry in sel:
                if self.GetStateTextOrID(entry.jobData)[1] == const.ramJobStatusReady:
                    sm.GetService('manufacturing').CompleteJob(entry.jobData)

            if len(sel) > 0:
                sm.GetService('objectCaching').InvalidateCachedMethodCall('ramProxy', 'GetJobs2', sel[0].jobData.installedItemOwnerID, 0)
            doneLabel = localization.GetByLabel('UI/Common/Done')
            sm.GetService('loading').ProgressWnd(completingJobsLabel, doneLabel, 2, 2)

        finally:
            sm.GetService('manufacturing').ReloadBlueprints()
            self.LoadJobs()
            self.UpdateDetails()
            self.delivering = 0




    def CancelJob(self, *args):
        if eve.Message('RamCancelJobConfirm', {}, uiconst.YESNO) != uiconst.ID_YES:
            return 
        if getattr(self, 'cancelling', 0):
            return 
        self.cancelling = 1
        self.sr.activeDetails = None
        try:
            sel = self.sr.jobsScroll.GetSelected()
            blue.pyos.synchro.SleepWallclock(1000)
            for entry in sel:
                cancel = self.GetStateTextOrID(entry.jobData)[1] != const.ramJobStatusReady
                if entry.jobData.pauseProductionTime is not None:
                    eve.Message('CantUseOfflineStructure', {'typeID': entry.jobData.containerTypeID})
                else:
                    sm.GetService('manufacturing').CompleteJob(entry.jobData, cancel)

            if len(sel) > 0:
                sm.GetService('objectCaching').InvalidateCachedMethodCall('ramProxy', 'GetJobs2', sel[0].jobData.installedItemOwnerID, 0)
            sm.GetService('manufacturing').ReloadBlueprints()
            self.LoadJobs()
            self.UpdateDetails()

        finally:
            self.cancelling = 0




    def UpdateDetails(self, timerUpdate = 1):
        if self.sr.activeDetails:
            endTime = self.sr.activeDetails.endProductionTime
            pauseProductionTime = self.sr.activeDetails.pauseProductionTime
            if pauseProductionTime is None:
                endTime -= blue.os.GetWallclockTime()
                endTime = max(0, endTime)
            else:
                endTime -= pauseProductionTime
                endTime = max(0, endTime)
            detailtextvalue = ''
            if endTime <= 0:
                readyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Ready')
                detailtextvalue = '<color=0xff00FF00>%s' % readyLabel
                if self.sr.activeDetails.completed == 1:
                    deliveredLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Delivered')
                    detailtextvalue = deliveredLabel
                if timerUpdate:
                    self.ShowJobDetails(self.sr.activeDetails)
                self.sr.detailtimer = None
            else:
                timeLeftLabel = localizationUtil.FormatTimeIntervalShortWritten(endTime)
                detailtextvalue = '<color=0xFFFFFF00>%s</color>' % timeLeftLabel
            entry = self.GetJobEntry(self.sr.activeDetails.jobID)
            if entry:
                entry.label = '%s<t><color=0xFFFFFFFF>%s</color>' % (self.GetStateTextOrID(self.sr.activeDetails)[0], entry.labelNoStatus)
                if entry.panel:
                    entry.panel.Load(entry)
            ttcLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TTC')
            self.sr.detailtext.text = '%s<t><right>%s' % (ttcLabel, detailtextvalue)
        else:
            self.sr.detailtext = None
            self.sr.detailtimer = None
            uix.Flush(self.sr.details)



    def GetJobEntry(self, jobID):
        for entry in self.sr.jobsScroll.GetNodes():
            if entry.jobData.jobID == jobID:
                return entry




    def GetNow(self):
        return util.FmtDate(blue.os.GetWallclockTime(), 'sn')



    def GetOffsetTime(self, shift):
        return util.FmtDate(blue.os.GetWallclockTime() + shift, 'sn')




class RMJobEntry(listentry.Generic):
    __guid__ = 'listentry.RMJobEntry'

    def Load(self, node):
        listentry.Generic.Load(self, node)




class InstallationPanel(uicls.Container):
    __guid__ = 'xtriui.InstallationPanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.submitHeader = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallJobCommand')
        self.inited = 0
        self.submitFunc = None
        self.selectedAssemblyLine = None
        self.delaySelection = None
        self.producableStringCache = {}
        self.blueprintLocationID = None
        self.showAllAssemblyLines = True
        self.filterHeight = 0



    def _OnClose(self):
        uicls.Container._OnClose(self)
        if self.inited:
            if self.activityID is None:
                settings.user.ui.Set('factory_installationsactivityfilter', self.sr.installationsActivityFilter.GetValue())
            settings.user.ui.Set('factory_installationslocationsfilter', self.sr.installationsLocationsFilter.GetValue())
            settings.user.ui.Set('factory_installationsrangesfilter', self.sr.installationsRangesFilter.GetValue())
            settings.user.ui.Set('factory_installationstypeflagfilter', self.sr.installationsTypeFlagFilter.GetValue())
        self.submitFunc = None
        self.selectedAssemblyLine = None



    def Init(self, activityID = None, stationID = None):
        self.activityID = activityID
        self.sr.filters = uicls.Container(name='filters', parent=self, height=33, align=uiconst.TOTOP)
        self.sr.activities = [ (localization.GetByLabel(labelPath), actID) for (actID, labelPath,) in sm.GetService('manufacturing').GetActivities() ]
        if activityID is None:
            activityID = settings.user.ui.Get('factory_installationsactivityfilter', const.ramActivityManufacturing)
        activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
        c = uicls.Combo(label=activityLabel, parent=self.sr.filters, options=self.sr.activities, name='activity', select=activityID, callback=self.InstallationsComboChange, pos=(1, 0, 0, 0), align=uiconst.TOPLEFT)
        c.top = top = -c.sr.label.top - 4
        self.sr.filters.height = c.top + c.height + 5
        self.sr.installationsActivityFilter = c
        stationsLabel = localization.GetByLabel('UI/Common/Stations')
        assemblyArraysLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AssemblyArrays')
        mobileLabsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MobileLaboratories')
        locationtypes = [(stationsLabel, (const.groupStation,)), (assemblyArraysLabel, (const.groupAssemblyArray,)), (mobileLabsLabel, (const.groupMobileLaboratory,))]
        if session.shipid:
            myShipLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MyShip')
            locationtypes.insert(1, (myShipLabel, (const.groupCapitalIndustrialShip, const.groupFreighter)))
        locationtypes.sort()
        anyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Any')
        locationtypes.insert(0, (anyLabel, None))
        self.sr.locationtypes = locationtypes
        loc = (anyLabel, None)
        if not stationID:
            loc = settings.user.ui.Get('factory_installationslocationsfilter', (const.groupSolarSystem, eve.session.solarsystemid2))
        locationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Location')
        c = uicls.Combo(label=locationLabel, parent=self.sr.filters, options=self.sr.locationtypes, name=' location', select=loc, callback=self.InstallationsComboChange, pos=(self.sr.installationsActivityFilter.left + self.sr.installationsActivityFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsLocationsFilter = c
        self.sr.ranges = [ (text, locationData) for (locationData, text,) in sm.GetService('manufacturing').GetRanges() ]
        self.blueprintLocationID = stationID
        if stationID:
            bpLocationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CurrentBlueprintLocation')
            self.sr.ranges.insert(0, (bpLocationLabel, (stationID, LOCATION_BLUEPRINT)))
            rng = (stationID, LOCATION_BLUEPRINT)
        else:
            rng = settings.user.ui.Get('factory_installationsrangesfilter', (const.groupRegion, eve.session.regionid))
        rangeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Range')
        c = uicls.Combo(label=rangeLabel, parent=self.sr.filters, options=self.sr.ranges, name='range', select=rng, callback=self.InstallationsComboChange, pos=(self.sr.installationsLocationsFilter.left + self.sr.installationsLocationsFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsRangesFilter = c
        publicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Public')
        personalLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Personal')
        self.sr.assemblytypeflag = [(publicLabel, (const.groupRegion, 'region', None)), (personalLabel, (const.groupCharacter, 'char', eve.session.charid))]
        if not util.IsNPC(eve.session.corpid):
            corporationLabel = localization.GetByLabel('UI/Common/Corporation')
            self.sr.assemblytypeflag += [(corporationLabel, (const.groupCorporation, 'corp', eve.session.corpid))]
        if eve.session.allianceid is not None:
            allianceLabel = localization.GetByLabel('UI/Common/Alliance')
            self.sr.assemblytypeflag += [(allianceLabel, (const.groupAlliance, 'alliance', eve.session.allianceid))]
        typeLabel = localization.GetByLabel('UI/Common/Type')
        c = uicls.Combo(label=typeLabel, parent=self.sr.filters, options=self.sr.assemblytypeflag, name='typeflag', select=settings.user.ui.Get('factory_installationstypeflagfilter', (const.groupRegion, 'region', None)), callback=self.InstallationsComboChange, pos=(self.sr.installationsRangesFilter.left + self.sr.installationsRangesFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsTypeFlagFilter = c
        catdefault = settings.user.ui.Get('factory_installationscatfilter', None)
        catfilters = sm.GetService('marketutils').GetFilterops(None)
        if catdefault not in [ v for (k, v,) in catfilters ]:
            catdefault = None
        prodCategoryLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductionCategory')
        self.sr.filterCategory = uicls.Combo(label=prodCategoryLabel, parent=self.sr.filters, options=sm.GetService('marketutils').GetFilterops(None), name='filterCateg', select=catdefault, callback=self.InstallationsComboChange, pos=(self.sr.installationsTypeFlagFilter.left + self.sr.installationsTypeFlagFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        groupdefault = settings.user.ui.Get('factory_installationsgroupfilter', None)
        if catdefault is None:
            allLabel = localization.GetByLabel('UI/Common/All')
            ops = [(allLabel, None)]
        else:
            ops = sm.GetService('marketutils').GetFilterops(catdefault)
        if groupdefault not in [ v for (k, v,) in ops ]:
            groupdefault = None
        productionGroupLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductionGroup')
        self.sr.filterGroup = uicls.Combo(label=productionGroupLabel, parent=self.sr.filters, options=ops, name='filterGroup', select=groupdefault, callback=self.InstallationsComboChange, pos=(self.sr.filterCategory.left + self.sr.filterCategory.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        if activityID not in (const.ramActivityNone, const.ramActivityManufacturing):
            self.sr.filterCategory.state = uiconst.UI_HIDDEN
            self.sr.filterGroup.state = uiconst.UI_HIDDEN
        h = settings.user.ui.Get('installationsScrollHeight', 128)
        self.sr.installationsScroll = uicls.Scroll(name='installationsScroll', parent=self, height=h, align=uiconst.TOTOP)
        self.sr.installationsScroll.sr.id = 'installationsScroll'
        self.sr.installationsScroll.multiSelect = 0
        self.sr.installationsScroll.OnSelectionChange = self.OnSelectionChangeInstallationsScroll
        self.sr.assemblyLineFilters = uicls.Container(name='assemblyLineFilters', parent=self, height=4, top=0, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, clipChildren=1)
        uicls.Container(name='push', parent=self.sr.assemblyLineFilters, align=uiconst.TOTOP, height=4, state=uiconst.UI_PICKCHILDREN)
        filterCont = uicls.Container(name='assemblyLineFiltersSub', left=2, top=2, parent=self.sr.assemblyLineFilters, align=uiconst.TOALL, pos=(2, 2, 2, 2))
        uicls.Frame(parent=self.sr.assemblyLineFilters)
        uicls.Fill(parent=self.sr.assemblyLineFilters, color=(1.0, 1.0, 1.0, 0.25))
        masks = [ (12,
         maskName,
         'assemblyLineFilterCheckBox%s' % maskConst,
         maskConst,
         settings.user.ui.Get('assemblyLineFilterCheckBox%s' % maskConst, maskConst) == maskConst,
         None) for (maskName, maskID, maskConst,) in sm.GetService('manufacturing').GetRestrictionMasks() ]
        filteringOptionsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FilteringOptions')
        t = uicls.EveLabelMedium(text=filteringOptionsLabel, parent=filterCont, padLeft=4, padTop=4, width=100, align=uiconst.TOLEFT, idx=0)
        for (height, label, configname, retval, checked, groupname,) in masks:
            cb = uicls.Checkbox(text=label, parent=filterCont, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChange, align=uiconst.TOLEFT, pos=(0, 0, 120, 0))
            setattr(self.sr, '%s' % configname, cb)
            cb.hint = label
            if cb.height > self.filterHeight:
                self.filterHeight = cb.height

        divider = xtriui.Divider(name='divider', align=uiconst.TOTOP, height=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.installationsScroll, 'height', 'y', 80, 224)
        divider.OnSizeChanged = self.OnInstallationScrollSizeChanged
        self.sr.assemblyLinesScroll = uicls.Scroll(name='assemblyLinesScroll', parent=self)
        self.sr.assemblyLinesScroll.sr.id = 'assemblyLinesScroll'
        self.sr.installationDetails = uicls.Container(name='installationDetails', parent=self, height=68, align=uiconst.TOBOTTOM, idx=0)
        self.inited = 1
        self.InstallationsComboChange(None, None, None)



    def OnCheckboxChange(self, checkbox):
        if checkbox and checkbox.name.startswith('assemblyLineFilterCheckBox'):
            config = checkbox.data['config']
            if checkbox.data.has_key('value'):
                if checkbox.checked:
                    settings.user.ui.Set(config, checkbox.data['value'])
                else:
                    settings.user.ui.Set(config, checkbox.checked)
            if self.sr.Get('installationsScroll'):
                selectedInstallationDetails = [ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0]
                if selectedInstallationDetails:
                    self.ShowAssemblyLines(selectedInstallationDetails[0])



    def OnInstallationScrollSizeChanged(self):
        settings.user.ui.Set('installationsScrollHeight', self.sr.installationsScroll.height)



    def InstallationsComboChange(self, combo, label, value, *args):
        if combo and combo.name == 'filterCateg':
            if value is None:
                allLabel = localization.GetByLabel('UI/Common/All')
                ops = [(allLabel, None)]
            else:
                ops = sm.GetService('marketutils').GetFilterops(value)
            self.sr.filterGroup.LoadOptions(ops)
            settings.user.ui.Set('factory_installationscatfilter', value)
        elif combo and combo.name == 'filterGroup':
            settings.user.ui.Set('factory_installationsgroupfilter', value)
        elif combo and combo.name in 'activity':
            if value in (const.ramActivityNone, const.ramActivityManufacturing):
                self.sr.filterCategory.state = uiconst.UI_NORMAL
                self.sr.filterGroup.state = uiconst.UI_NORMAL
            else:
                self.sr.filterCategory.state = uiconst.UI_HIDDEN
                self.sr.filterGroup.state = uiconst.UI_HIDDEN
        self.LoadInstallations()



    def OnSelectionChangeInstallationsScroll(self, *args):
        selected = args[0]
        for selection in selected:
            log.LogInfo('OnSelectionChangeInstallationsScroll')
            now = blue.os.GetWallclockTime()
            self.delaySelection = (now, selection)
            uthread.new(self.DelaySelection, now)
            break




    def DelaySelection(self, issueTime):
        blue.pyos.synchro.SleepWallclock(250)
        if self.delaySelection is None:
            return 
        (issuedAt, selection,) = self.delaySelection
        if issuedAt != issueTime:
            return 
        if not self.sr.installationsScroll.GetSelected():
            return 
        selectedInstallation = [ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0]
        if selection.assemblyLine.containerID != selectedInstallation[0].containerID:
            return 
        self.delaySelection = None
        self.ShowAssemblyLines(selection.assemblyLine)



    def LoadInstallations(self, *args):
        uix.Flush(self.sr.installationDetails)
        uicore.effect.MorphUI(self.sr.assemblyLineFilters, 'height', 0, endState=uiconst.UI_HIDDEN)
        self.sr.assemblyLinesScroll.Load(contentList=[], headers=[])
        self.sr.assemblyLinesScroll.ShowHint()
        self.sr.installationsScroll.Load(contentList=[], headers=[])
        fetchingInstallationsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FetchingInstallations')
        self.sr.installationsScroll.ShowHint(fetchingInstallationsLabel)
        activityFilter = self.sr.installationsActivityFilter.GetValue()
        locationFilter = self.sr.installationsLocationsFilter.GetValue()
        rangesFilter = self.sr.installationsRangesFilter.GetValue()
        typeflagFilter = self.sr.installationsTypeFlagFilter.GetValue()
        categs = None
        groups = None
        if activityFilter in (const.ramActivityNone, const.ramActivityManufacturing):
            categoryFilter = self.sr.filterCategory.GetValue()
            groupFilter = self.sr.filterGroup.GetValue()
            if categoryFilter:
                if groupFilter is None:
                    categs = sm.GetService('marketutils').GetTypeFilterIDs(categoryFilter)
                else:
                    groups = sm.GetService('marketutils').GetTypeFilterIDs(groupFilter, 0)
        (scrolllist, headers,) = self.GetAssemblyLinesScrolllist(onclick=self.ClickInstallation, ongetmenu=self.GetInstallationLineMenu, filterActivity=activityFilter, filterLocation=locationFilter, filterTypeFlag=typeflagFilter, filterRange=rangesFilter, filterCategs=categs, filterGroups=groups)
        self.sr.installationsScroll.Load(contentList=scrolllist, headers=headers)
        if scrolllist:
            self.sr.installationsScroll.ShowHint()
        else:
            noInstallationsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoInstallationsFoundWithFilters')
            self.sr.installationsScroll.ShowHint(noInstallationsLabel)
        if scrolllist:
            self.sr.assemblyLinesScroll.state = uiconst.UI_NORMAL
            pickInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickInstallation')
            self.sr.assemblyLinesScroll.ShowHint(pickInstallationLabel)
        if self.blueprintLocationID and rangesFilter == (self.blueprintLocationID, LOCATION_BLUEPRINT):
            self.sr.installationsScroll.SetSelected(0)



    def GetInstallationLineMenu(self, entry):
        m = []
        if self.sr.installationsScroll.GetSelected():
            selectedInstallationDetails = [ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0]
            if util.IsStation(selectedInstallationDetails[0].containerID) and eve.session.solarsystemid != selectedInstallationDetails[0].containerLocationID:
                m += sm.GetService('menu').CelestialMenu(selectedInstallationDetails[0].containerLocationID)
            else:
                m += sm.GetService('menu').CelestialMenu(selectedInstallationDetails[0].containerID)
        return m



    def ClickInstallation(self, entry):
        self.delaySelection = None
        self.ShowAssemblyLines(entry.sr.node.assemblyLine)



    def ShowAssemblyLines(self, assemblyLine):
        log.LogInfo('ShowAssemblyLines::InstallationID::%s' % assemblyLine)
        uix.Flush(self.sr.installationDetails)
        containerID = assemblyLine.containerID
        ownerID = None
        if hasattr(assemblyLine, 'ownerID'):
            ownerID = assemblyLine.ownerID
        lineType = cfg.ramaltypes.Get(assemblyLine.assemblyLineTypeID)
        assemblyLines = sm.ProxySvc('ramProxy').AssemblyLinesGet(containerID)
        (scrolllist, headers,) = self.GetAssemblyLineDetailsScrolllist(assemblyLines, onclick=self.ShowAssemblyLineDetails, ongetmenu=self.GetAssemblyLineMenu, filterActivity=lineType.activityID, filterAssemblyLineType=lineType.assemblyLineTypeID)
        self.sr.assemblyLinesScroll.Load(contentList=scrolllist, headers=headers)
        self.sr.assemblyLinesScroll.ShowHint('')
        toBecomeHeight = self.filterHeight + 6 if self.filterHeight else 36
        if headers and not util.IsNPC(ownerID):
            if not self.sr.assemblyLineFilters.height == toBecomeHeight:
                self.sr.assemblyLineFilters.state = uiconst.UI_NORMAL
                uicore.effect.MorphUI(self.sr.assemblyLineFilters, 'height', toBecomeHeight)
            if not scrolllist:
                self.sr.assemblyLinesScroll.Load()
                noResultLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/FiltersReturnedNoResults')
                self.sr.assemblyLinesScroll.ShowHint(noResultLabel)
        selectAssemblyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SelectAssemblyLine')
        t = uicls.EveLabelMedium(text=selectAssemblyLabel, parent=self.sr.installationDetails, left=10, top=30, singleline=1, tabs=[128, 170])
        if scrolllist:
            toggleFullListLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ToggleFullList')
            self.sr.toggleLinesButt = uicls.Button(parent=self.sr.installationDetails, label=toggleFullListLabel, func=self.ToggleFullAssemblyLinesList, pos=(0,
             const.defaultPadding,
             0,
             0), align=uiconst.BOTTOMRIGHT)



    def ShowAssemblyLineDetails(self, entry):
        uix.Flush(self.sr.installationDetails)
        goodStandingDiscountLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GoodStandingDiscount')
        badStandingSurchargeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/BadStandingSurcharge')
        minStandingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumStanding')
        minCharSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumCharacterSecurity')
        maxCharSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumCharacterSecurity')
        minCorpSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumCorporationSecurity')
        maxCorpSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumCorporationSecurity')
        d = [(goodStandingDiscountLabel, 'discountPerGoodStandingPoint'),
         (badStandingSurchargeLabel, 'surchargePerBadStandingPoint'),
         (minStandingLabel, 'minimumStanding'),
         (minCharSecLabel, 'minimumCharSecurity'),
         (maxCharSecLabel, 'maximumCharSecurity'),
         (minCorpSecLabel, 'minimumCorpSecurity'),
         (maxCorpSecLabel, 'maximumCorpSecurity')]
        i = 0
        left = 0
        top = 5
        col1 = 165
        col2 = 205
        for (header, key,) in d:
            if key not in entry.sr.node.assemblyLine.header:
                continue
            value = entry.sr.node.assemblyLine[key]
            value = localizationUtil.FormatNumeric(value)
            t = uicls.EveLabelMedium(text='%s<t><right>%s' % (header, value), parent=self.sr.installationDetails, left=left, top=top, singleline=1, tabs=[col1, col2])
            t.hint = header
            i += 1
            if i == 4:
                left += col2 + 8
                uicls.Line(parent=self.sr.installationDetails, align=uiconst.RELATIVE, width=1, top=5, height=64, left=left - 7)
                i = 0
                top = 5
            else:
                top += t.textheight

        if i != 0:
            uicls.Line(parent=self.sr.installationDetails, align=uiconst.RELATIVE, width=1, top=5, height=64, left=left + col2)
        buttonTop = const.defaultPadding
        if self.submitHeader:
            submit = uicls.Button(parent=self.sr.installationDetails, label=self.submitHeader, func=self.Submit, args=None, pos=(0,
             const.defaultPadding,
             0,
             0), align=uiconst.TOPRIGHT)
            buttonTop = submit.top + submit.height + 2
        self.selectedAssemblyLine = entry.sr.node.assemblyLine
        if self.CanManageAssemblyLines():
            manageAssebmlyLinesLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ManageAssemblyLines')
            submit = uicls.Button(parent=self.sr.installationDetails, label=manageAssebmlyLinesLabel, func=self.ManageAssemblyLines, pos=(0,
             buttonTop,
             0,
             0), align=uiconst.TOPRIGHT)



    def CanManageAssemblyLines(self, *args):
        canManage = False
        if self.sr.assemblyLinesScroll.GetSelected():
            selectedInstallationDetails = [ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0]
            selectedAssemblyLineDetails = [ entry.listvalue for entry in self.sr.assemblyLinesScroll.GetSelected() ][0]
            if not selectedInstallationDetails or len(selectedAssemblyLineDetails) == 0:
                raise UserError('RamPleasePickAnInstalltion')
            ownerID = selectedInstallationDetails[0].ownerID
            if cfg.eveowners.Get(ownerID).typeID == const.typeCorporation:
                if eve.session.corpid == ownerID:
                    if eve.session.corprole & const.corpRoleStationManager == const.corpRoleStationManager:
                        canManage = True
        return canManage



    def Submit(self, *args):
        if self.sr.assemblyLinesScroll.GetSelected():
            if not self.submitFunc:
                (selectedInstallationDetails, selectedAssemblyLineDetails,) = ([ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0], [ entry.listvalue for entry in self.sr.assemblyLinesScroll.GetSelected() ][0])
                sm.GetService('manufacturing').CreateJob(None, selectedAssemblyLineDetails[0], None, selectedInstallationDetails[0])
            else:
                apply(self.submitFunc)



    def GetAssemblyLineMenu(self, entry):
        m = []
        if self.sr.assemblyLinesScroll.GetSelected():
            (selectedInstallationDetails, selectedAssemblyLineDetails,) = ([ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0], [ entry.listvalue for entry in self.sr.assemblyLinesScroll.GetSelected() ][0])
            installJobLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallJobCommand')
            m += [(installJobLabel, sm.GetService('manufacturing').CreateJob, (None,
               selectedAssemblyLineDetails[0],
               None,
               selectedInstallationDetails[0]))]
        return m



    def GetAssemblyLinesScrolllist(self, onclick = None, ondblclick = None, ongetmenu = None, filterActivity = None, filterLocation = None, filterTypeFlag = None, filterRange = None, filterCategs = None, filterGroups = None):
        all = sm.GetService('manufacturing').GetRegionDetails(filterTypeFlag[1])
        scrolllist = []
        headers = []
        for line in all:
            if filterActivity and line.activityID != filterActivity:
                continue
            if filterRange and line.containerID != eve.session.shipid:
                solarsystemID = None
                constellationID = None
                regionID = None
                (locationID, locationGroup,) = filterRange
                if locationGroup == const.groupStation:
                    if line.containerID != locationID:
                        continue
                solarsystemID = line.containerLocationID
                if locationGroup == const.groupSolarSystem:
                    if solarsystemID != locationID:
                        continue
                constellationID = sm.GetService('map').GetParent(solarsystemID)
                if locationGroup == const.groupConstellation:
                    if constellationID != locationID:
                        continue
                regionID = sm.GetService('map').GetParent(constellationID)
                if locationGroup == const.groupRegion:
                    if regionID != locationID:
                        continue
                if int(locationGroup) == LOCATION_BLUEPRINT:
                    if locationID != line.containerID:
                        continue
            containerGroup = cfg.invgroups.Get(cfg.invtypes.Get(line.containerTypeID).groupID)
            if filterLocation and containerGroup.groupID not in filterLocation:
                continue
            lineType = cfg.ramaltypes.Get(line.assemblyLineTypeID)
            lineGroup = cfg.ramaltypesdetailpergroup.get(line.assemblyLineTypeID, [])
            lineCategory = cfg.ramaltypesdetailpercategory.get(line.assemblyLineTypeID, [])
            if filterGroups:
                (prodGroups, prodCategs,) = sm.GetService('marketutils').GetProducableGroups(lineGroup, lineCategory)
                valid = [ groupID for groupID in prodGroups if groupID in filterGroups ]
                if not valid:
                    for groupID in filterGroups:
                        invGroup = cfg.invgroups.Get(groupID)
                        if invGroup.categoryID in prodCategs:
                            valid.append(groupID)
                            break

                if not valid:
                    continue
            elif filterCategs:
                prodCategs = sm.GetService('marketutils').GetProducableCategories(lineGroup, lineCategory)
                valid = [ categoryID for categoryID in prodCategs if categoryID in filterCategs ]
                if not valid:
                    continue
            if line.containerID == eve.session.shipid:
                jumps = 0
            else:
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(line.containerLocationID)
            containerLocationName = cfg.evelocations.Get(line.containerID).name
            if not containerLocationName:
                containerLocationName = cfg.invtypes.Get(line.containerTypeID).name
            activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
            qtyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/QTY')
            locationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Location')
            jumpsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Jumps')
            installationTypeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallationType')
            ownerLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Owner')
            headers = [activityLabel,
             qtyLabel,
             locationLabel,
             jumpsLabel,
             installationTypeLabel,
             ownerLabel]
            groupName = containerGroup.name
            data = util.KeyVal()
            data.label = '%s<t><right>%s<t>%s<t><right>%s<t>%s<t>%s' % (sm.GetService('manufacturing').GetActivityName(lineType.activityID),
             localizationUtil.FormatNumeric(line.quantity, useGrouping=True),
             containerLocationName,
             localizationUtil.FormatNumeric(jumps, useGrouping=True),
             groupName,
             cfg.eveowners.Get(line.ownerID).name)
            data.confirmOnDblClick = 1
            data.listvalue = (line,
             lineType,
             lineGroup,
             lineCategory)
            data.OnClick = onclick
            data.OnDblClick = ondblclick
            data.GetMenu = ongetmenu
            data.assemblyLine = line
            data.Set('sort_%s' % qtyLabel, line.quantity)
            data.Set('sort_%s' % jumpsLabel, jumps)
            data.hint = data.label.replace('<right>', '') + '<br>' + self.GetProducableString(lineType, lineGroup, lineCategory)
            scrolllist.append(listentry.Get('Generic', data=data))

        return (scrolllist, headers)



    def GetProducableString(self, lineType, lineGroups, lineCategs):
        if lineType.assemblyLineTypeID in self.producableStringCache:
            return self.producableStringCache.get(lineType.assemblyLineTypeID, '')
        validc = []
        for categ in lineCategs:
            validc.append(cfg.invcategories.Get(categ.categoryID).name)

        validg = []
        for group in lineGroups:
            validg.append(cfg.invgroups.Get(group.groupID).name)

        validc.sort()
        validg.sort()
        v = ''
        if validc:
            v += localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProducibleCategories')
            v += '<br>'
            v += localizationUtil.FormatGenericList(validc)
            v += '<br><br>'
        if validg:
            v += localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProducibleGroups')
            v += '<br>'
            v += localizationUtil.FormatGenericList(validg)
        self.producableStringCache[lineType.assemblyLineTypeID] = v
        return v



    def AssemblyLineRow(self, data):
        line = data.assemblyLine
        lineType = cfg.ramaltypes.Get(data.assemblyLine.assemblyLineTypeID)
        expirationTime = ''
        nextFreeTimeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NextFreeTime')
        nft = data.Get('sort_%s' % nextFreeTimeLabel, 0)
        if nft <= 0:
            nowLabel = localization.GetByLabel('UI/Common/Now')
            expirationTime = '<color=0xff00FF00><t>%s<color=0xffffffff>' % nowLabel
        else:
            expirationTime = '<color=0xFFFFFF00><t>%s<color=0xffffffff>' % util.FmtDate(nft)
        m = sm.GetService('manufacturing').GetRestrictionMasks()
        rmText = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PubliclyAvailable')
        if line.restrictionMask:
            rmText = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Restricted')
        data.label = '%s<t>%s%s<t><right>%s<t><right>%s<t><right>%s<t><right>%s<t>%s' % (localizationUtil.FormatNumeric(data.numLines, decimalPlaces=0),
         sm.GetService('manufacturing').GetActivityName(lineType.activityID),
         expirationTime,
         util.FmtISK(line.costInstall),
         util.FmtISK(line.costPerHour),
         localizationUtil.FormatNumeric(lineType.baseTimeMultiplier, decimalPlaces=1),
         localizationUtil.FormatNumeric(lineType.baseMaterialMultiplier, decimalPlaces=1),
         rmText)
        installCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallCost')
        costPerHourLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CostPerHour')
        timeMultiplierLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TimeMultiplier')
        materialMultiplierLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialMultiplier')
        data.Set('sort_#', data.numLines)
        data.Set('sort_%s' % installCostLabel, line.costInstall)
        data.Set('sort_%s' % costPerHourLabel, line.costPerHour)
        data.Set('sort_%s' % timeMultiplierLabel, lineType.baseTimeMultiplier)
        data.Set('sort_%s' % materialMultiplierLabel, lineType.baseMaterialMultiplier)
        return data



    def IsAssemblyLineFilteredOut(self, thisRow):
        ret = False
        filtervalues = []
        for (maskName, maskEntry, maskConstant,) in sm.GetService('manufacturing').GetRestrictionMasks():
            mn = 'assemblyLineFilterCheckBox%s' % maskConstant
            if self.sr.Get(mn):
                theBox = self.sr.Get(mn)
                if theBox.GetValue() and theBox.data.has_key('config'):
                    config = theBox.data['config']
                    if theBox.data.has_key('value'):
                        value = theBox.data['value']
                        if value:
                            filtervalues.append(value)

        if len(filtervalues):
            ret = False
            for maskConstant in filtervalues:
                if thisRow[3] & maskConstant != maskConstant:
                    ret = True
                    break

        return ret



    def GetAssemblyLineDetailsScrolllist(self, installation, onclick = None, ondblclick = None, ongetmenu = None, filterActivity = None, filterAssemblyLineType = None):
        scrolllist = []
        lastRow = []
        lastRowData = util.KeyVal()
        lastLine = None
        numLines = 0
        rows = []
        nextFreeTimeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NextFreeTime')
        for line in installation:
            thisRow = [line.assemblyLineTypeID,
             line.costInstall,
             line.costPerHour,
             line.restrictionMask]
            lineType = cfg.ramaltypes.Get(line.assemblyLineTypeID)
            if filterActivity and lineType.activityID != filterActivity:
                continue
            if filterAssemblyLineType and lineType.assemblyLineTypeID != filterAssemblyLineType:
                continue
            if thisRow[3] and self.IsAssemblyLineFilteredOut(thisRow):
                continue
            numLines += 1
            lineGroup = cfg.ramaltypesdetailpergroup.get(line.assemblyLineTypeID, [])
            lineCategory = cfg.ramaltypesdetailpercategory.get(line.assemblyLineTypeID, [])
            expirationTime = line.nextFreeTime
            expirationTime -= blue.os.GetWallclockTime()
            expirationTimeSort = int(expirationTime / MIN) * MIN
            data = util.KeyVal()
            data.confirmOnDblClick = 1
            data.Set('sort_%s' % nextFreeTimeLabel, expirationTimeSort)
            data.listvalue = (line,
             lineType,
             lineGroup,
             lineCategory)
            data.OnClick = onclick
            data.OnDblClick = ondblclick
            data.GetMenu = ongetmenu
            data.assemblyLine = line
            data.numLines = 1
            if self.showAllAssemblyLines:
                scrolllist.append(listentry.Get('Generic', data=self.AssemblyLineRow(data)))
            else:
                for i in range(len(rows)):
                    r = rows[i]
                    if r.assemblyLine.assemblyLineTypeID == thisRow[0] and r.assemblyLine.costInstall == thisRow[1] and r.assemblyLine.costPerHour == thisRow[2]:
                        if expirationTimeSort < r.Get('sort_%s' % nextFreeTimeLabel, 0):
                            r.Set('sort_%s' % nextFreeTimeLabel, expirationTimeSort)
                            r.assemblyLine = line
                            r.listvalue = (line,
                             lineType,
                             lineGroup,
                             lineCategory)
                        rows[i].numLines += 1
                        break
                else:
                    rows.append(data)

                numLines = 0

        if not self.showAllAssemblyLines and rows:
            for data in rows:
                scrolllist.append(listentry.Get('Generic', data=self.AssemblyLineRow(data)))

        numberHashLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NumberHash')
        activityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Activity')
        installCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallCost')
        costPerHour = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CostPerHour')
        timeMultiplierLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TimeMultiplier')
        materialMultiplierLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialMultiplier')
        availabilityLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Availability')
        tmpHeaders = [numberHashLabel,
         activityLabel,
         nextFreeTimeLabel,
         installCostLabel,
         costPerHour,
         timeMultiplierLabel,
         materialMultiplierLabel,
         availabilityLabel]
        headers = []
        for header in tmpHeaders:
            h = uiutil.ReplaceStringWithTags(header)
            headers.append(h)

        return (scrolllist, headers)



    def ToggleFullAssemblyLinesList(self, entry):
        self.sr.assemblyLinesScroll.SetSelected(0)
        selectedAssemblyLineDetails = [ entry.listvalue for entry in self.sr.assemblyLinesScroll.GetSelected() ]
        entry = selectedAssemblyLineDetails[0][0]
        self.showAllAssemblyLines = not self.showAllAssemblyLines
        self.ShowAssemblyLines(entry)



    def ManageAssemblyLines(self, entry):
        selectedInstallationDetails = [ entry.listvalue for entry in self.sr.installationsScroll.GetSelected() ][0]
        selectedAssemblyLineDetails = [ entry.listvalue for entry in self.sr.assemblyLinesScroll.GetSelected() ]
        if not selectedInstallationDetails or len(selectedAssemblyLineDetails) == 0:
            raise UserError('RamPleasePickAnInstalltion')
        entry = selectedAssemblyLineDetails[0][0]
        if not self.showAllAssemblyLines:
            self.showAllAssemblyLines = True
            self.ShowAssemblyLines(entry)
            return 
        if not const.corpRoleStationManager & eve.session.corprole == const.corpRoleStationManager:
            eve.Message('MissingRoleStationMgt')
            return 
        installCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallCost')
        costPrHourLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CostPerHour')
        goodStandingDiscountLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GoodStandingDiscount')
        badStandingSurchargeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/BadStandingSurcharge')
        minStandingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumStanding')
        minCharSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumCharacterSecurity')
        maxCharSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumCharacterSecurity')
        minCorpSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MinimumCorporationSecurity')
        maxCorpSecLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaximumCorporationSecurity')
        d = [(installCostLabel,
          'costInstall',
          0.0,
          None,
          entry.costInstall),
         (costPrHourLabel,
          'costPerHour',
          0.0,
          None,
          entry.costPerHour),
         (goodStandingDiscountLabel,
          'discountPerGoodStandingPoint',
          0.0,
          10.0,
          entry.discountPerGoodStandingPoint),
         (badStandingSurchargeLabel,
          'surchargePerBadStandingPoint',
          0.0,
          10.0,
          entry.surchargePerBadStandingPoint),
         (minStandingLabel,
          'minimumStanding',
          -10.0,
          10.0,
          entry.minimumStanding),
         (minCharSecLabel,
          'minimumCharSecurity',
          -10.0,
          10.0,
          entry.minimumCharSecurity),
         (maxCharSecLabel,
          'maximumCharSecurity',
          -10.0,
          10.0,
          entry.maximumCharSecurity),
         (minCorpSecLabel,
          'minimumCorpSecurity',
          -10.0,
          10.0,
          entry.minimumCorpSecurity),
         (maxCorpSecLabel,
          'maximumCorpSecurity',
          -10.0,
          10.0,
          entry.maximumCorpSecurity)]
        format = []
        parametersLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Parameters')
        format.append({'type': 'header',
         'text': parametersLabel,
         'frame': 1})
        for (label, key, minvalue, maxvalue, setvalue,) in d:
            format.append({'type': 'edit',
             'setvalue': setvalue,
             'floatonly': [minvalue, maxvalue, 1],
             'key': key,
             'labelwidth': 190,
             'label': label,
             'required': 1,
             'frame': 1,
             'setfocus': 0})

        format.append({'type': 'push',
         'frame': 1})
        m = sm.GetService('manufacturing').GetRestrictionMasks()
        restrictionsMaskLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RestrictionMasks')
        format.append({'type': 'header',
         'text': restrictionsMaskLabel,
         'frame': 1})
        for (label, key, constant,) in m:
            format.append({'type': 'checkbox',
             'setvalue': not not entry.restrictionMask & constant == constant,
             'key': key,
             'label': '_hide',
             'required': 1,
             'text': label,
             'frame': 1})

        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        updateAssemblyLineSettingsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/UpdateAssemblyLineSettings')
        retval = uix.HybridWnd(format, updateAssemblyLineSettingsLabel, 1, buttons=uiconst.OKCANCEL, minW=340, minH=100, icon='ui_57_64_9', unresizeAble=1)
        if retval:
            if util.IsStation(entry.containerID):
                log.LogInfo('its in a station')
                installationLocationData = [[entry.containerID, const.groupStation], [], [entry.containerID]]
            else:
                log.LogInfo('ship or starbase')
                if entry.containerID == eve.session.shipid:
                    log.LogInfo('its in a ship')
                    path = []
                    if util.IsStation(eve.session.locationid):
                        invLocationGroupID = const.groupStation
                        path.append([eve.session.locationid, eve.session.charid, const.flagHangar])
                    else:
                        invLocationGroupID = const.groupSolarSystem
                    installationLocationData = [[eve.session.locationid, invLocationGroupID], path, [entry.containerID]]
                else:
                    log.LogInfo('its in a starbase')
                    installationLocationData = [[selectedInstallationDetails[0].containerLocationID, const.groupSolarSystem], [], [entry.containerID]]
            rowset = None
            for (line, lineType, lineGroup, lineCategory,) in selectedAssemblyLineDetails:
                if rowset is None:
                    rowset = util.Rowset(line.header)
                rowset.append(line)

            header = rowset.header
            retval = util.KeyVal(**retval)
            for line in rowset.lines:
                ID = line[header.index('assemblyLineID')]
                line[header.index('UIGroupingID')] = 0
                line[header.index('costInstall')] = retval.costInstall
                line[header.index('costPerHour')] = retval.costPerHour
                restrictionMask = 0
                if retval.ramRestrictBySecurity:
                    restrictionMask |= const.ramRestrictBySecurity
                if retval.ramRestrictByStanding:
                    restrictionMask |= const.ramRestrictByStanding
                if retval.ramRestrictByCorp:
                    restrictionMask |= const.ramRestrictByCorp
                if retval.ramRestrictByAlliance:
                    restrictionMask |= const.ramRestrictByAlliance
                line[header.index('restrictionMask')] = restrictionMask
                line[header.index('discountPerGoodStandingPoint')] = retval.discountPerGoodStandingPoint
                line[header.index('surchargePerBadStandingPoint')] = retval.surchargePerBadStandingPoint
                line[header.index('minimumStanding')] = retval.minimumStanding
                line[header.index('minimumCharSecurity')] = retval.minimumCharSecurity
                line[header.index('minimumCorpSecurity')] = retval.minimumCorpSecurity
                line[header.index('maximumCharSecurity')] = retval.maximumCharSecurity
                line[header.index('maximumCorpSecurity')] = retval.maximumCorpSecurity

            sm.ProxySvc('ramProxy').UpdateAssemblyLineConfigurations(installationLocationData, rowset)
        self.ShowAssemblyLines(entry)




class InstallationWindow(uicls.Window):
    __guid__ = 'form.ManufacturingInstallation'
    default_windowID = 'ManufacturingInstallation'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        activityID = attributes.activityID
        loadData = attributes.loadData
        if activityID is None:
            self.sr.activityID = 0
        else:
            self.sr.activityID = activityID
        bottom = uicls.Container(name='bottom', parent=self.sr.maincontainer, align=uiconst.TOBOTTOM, height=24, idx=0)
        self.scope = 'all'
        sAndILabelLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ScienceAndIndustry')
        self.SetCaption(sAndILabelLabel)
        self.SetMinSize([410, 240])
        self.NoSeeThrough()
        self.DefineButtons(uiconst.OKCANCEL, cancelFunc=self.Close, okFunc=self.Confirm)
        self.MakeUnResizeable()
        self.SetInstallationWindowCaption(self.sr.activityID)
        if loadData is not None:
            self.Load(*loadData)



    def SetInstallationWindowCaption(self, activityID):
        self.sr.activities = {const.ramActivityNone: 'ui_57_64_9',
         const.ramActivityManufacturing: 'ui_57_64_10',
         const.ramActivityResearchingMaterialProductivity: 'ui_57_64_11',
         const.ramActivityResearchingTimeProductivity: 'ui_57_64_12',
         const.ramActivityCopying: 'ui_57_64_13',
         const.ramActivityInvention: 'ui_57_64_11',
         const.ramActivityReverseEngineering: 'ui_57_64_11'}
        icon = self.sr.activities[activityID]
        self.SetWndIcon(icon, mainTop=-8)
        if self.sr.Get('installationWindowCaption', None) is None:
            capt = uicls.WndCaptionLabel(text=sm.GetService('manufacturing').GetActivityName(activityID), parent=self.sr.topParent, align=uiconst.RELATIVE, left=70, top=10)
            self.sr.installationWindowCaption = capt
            uiutil.Update(self)
        if self.sr.Get('activityID', None) != activityID:
            self.sr.installationWindowCaption.text = sm.GetService('manufacturing').GetActivityName(activityID)



    def Load(self, invItem = None, assemblyLine = None, activityID = None, installationDetails = None):
        uix.Flush(self.sr.main)
        if invItem and invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic) and invItem.ownerID not in [eve.session.charid, eve.session.corpid]:
            self.CloseByUser()
            raise UserError('RamCannotInstallItemForAnother')
        stationID = None
        if installationDetails:
            stationID = installationDetails.containerID
        instPar = uicls.Container(name='instPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        bpPar = uicls.Container(name='bpPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        inputPar = uicls.Container(name='inputPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        runsPar = self.sr.runsPar = uicls.Container(name='runsPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        copyRunsPar = self.sr.copyRunsPar = uicls.Container(name='copyRunsPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        inventionItemPar = self.sr.inventionItemPar = uicls.Container(name='inventionItemPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        inventionDecryptorPar = self.sr.inventionDecryptorPar = uicls.Container(name='inventionDecryptorPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        inventionOutputPar = self.sr.inventionOutputPar = uicls.Container(name='inventionOutputPar', parent=self.sr.main, align=uiconst.TOTOP, height=22, state=uiconst.UI_PICKCHILDREN)
        stringLeft = 8
        stringTop = 1
        installationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Installation')
        installationText = uicls.EveLabelSmall(text=installationLabel, parent=instPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        if activityID is not None and activityID == const.ramActivityReverseEngineering:
            ancientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AncientRelic')
            blueprintText = uicls.EveLabelSmall(text=ancientRelicLabel, parent=bpPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        else:
            blueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Blueprint')
            blueprintText = uicls.EveLabelSmall(text=blueprintLabel, parent=bpPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        inputOutputLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InputOutput')
        licencedRunsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LicencedRuns')
        baseItemLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/BaseItem')
        decryptorLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Decryptor')
        outputTypeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/OutputType')
        inputOutputText = uicls.EveLabelSmall(text=inputOutputLabel, parent=inputPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        self.sr.runsText = uicls.EveLabelSmall(text='', parent=runsPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        licencedRunsText = uicls.EveLabelSmall(text=licencedRunsLabel, parent=copyRunsPar, left=stringLeft, top=stringTop, width=80, align=uiconst.CENTERLEFT)
        baseItemText = uicls.EveLabelSmall(text=baseItemLabel, parent=inventionItemPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        decryptorText = uicls.EveLabelSmall(text=decryptorLabel, parent=inventionDecryptorPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        outputTypeText = uicls.EveLabelSmall(text=outputTypeLabel, parent=inventionOutputPar, left=stringLeft, top=stringTop, align=uiconst.CENTERLEFT)
        left = max(installationText.textwidth, blueprintText.textwidth, inputOutputText.textwidth, self.sr.runsText.textwidth, licencedRunsText.textwidth, baseItemText.textwidth, decryptorText.textwidth, outputTypeText.textwidth) + 15
        pickInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickInstallationCommand')
        changeInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeInstallationCommand')
        longestText = pickInstallationLabel
        if activityID == const.ramActivityReverseEngineering:
            pickAncientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickAncientRelicCommand')
            changeAncientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeAncientRelicCommand')
            for each in [changeInstallationLabel, pickAncientRelicLabel, changeAncientRelicLabel]:
                if len(longestText) < len(each):
                    longestText = each

        else:
            pickBlueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickBlueprintCommand')
            changeBlueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeBlueprintCommand')
            for each in [changeInstallationLabel, pickBlueprintLabel, changeBlueprintLabel]:
                if len(longestText) < len(each):
                    longestText = each

        instButtonPar = uicls.Container(name='instButtonPar', parent=instPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
        self.sr.pickInstallationBtn = uicls.Button(parent=instButtonPar, label=longestText, align=uiconst.TOPLEFT, func=self.PickInstallation, args=(activityID,), pos=(const.defaultPadding,
         2,
         0,
         0))
        if activityID == const.ramActivityReverseEngineering:
            bpButtonPar = uicls.Container(name='bpButtonPar', parent=bpPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
            changeAncientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeAncientRelicCommand')
            self.sr.pickBlueprintBtn = uicls.Button(parent=bpButtonPar, label=pickAncientRelicLabel, func=self.PickAncientRelic, pos=(const.defaultPadding,
             2,
             0,
             0))
        else:
            bpButtonPar = uicls.Container(name='bpButtonPar', parent=bpPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
            pickBlueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickBlueprintCommand')
            self.sr.pickBlueprintBtn = uicls.Button(parent=bpButtonPar, label=pickBlueprintLabel, func=self.PickBlueprint, pos=(const.defaultPadding,
             2,
             0,
             0))
        self.sr.pickInstallationBtn.setWidth = self.sr.pickBlueprintBtn.setWidth = self.sr.pickInstallationBtn.width
        instButtonPar.width = bpButtonPar.width = self.sr.pickInstallationBtn.setWidth + 8
        self.sr.pickInstallationBtn.SetLabel(pickInstallationLabel)
        editWith = self.width - instButtonPar.width - left
        pickOneLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickOne')
        self.sr.installationEdit = uicls.SinglelineEdit(name='installationEdit', parent=instPar, setvalue=pickOneLabel, align=uiconst.TOPLEFT, pos=(left,
         2,
         editWith,
         0))
        self.sr.installationEdit.readonly = 1
        if installationDetails:
            self.sr.installationDetails = installationDetails
        else:
            self.sr.installationDetails = None
        if assemblyLine:
            installationName = cfg.evelocations.Get(installationDetails.containerID).name
            if not installationName:
                installationName = cfg.invtypes.Get(installationDetails.containerTypeID).name
            self.sr.installationEdit.SetValue(installationName)
            self.sr.assemblyLine = assemblyLine
            changeInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeInstallationCommand')
            self.sr.pickInstallationBtn.SetLabel(changeInstallationLabel)
        else:
            self.sr.assemblyLine = None
        self.isMine = 1
        self.sr.bluePrint = None
        if invItem and invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
            self.sr.bluePrint = copy.deepcopy(invItem)
            self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
        self.sr.bpEdit = uicls.SinglelineEdit(name='bpEdit', parent=bpPar, setvalue=pickOneLabel, align=uiconst.TOPLEFT, pos=(left,
         2,
         editWith,
         0))
        self.sr.bpEdit.readonly = 1
        if self.sr.bluePrint:
            self.sr.bpEdit.SetValue(cfg.invtypes.Get(self.sr.bluePrint.typeID).name)
            if activityID is not None and activityID == const.ramActivityReverseEngineering:
                changeAncientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeAncientRelicCommand')
                self.sr.pickBlueprintBtn.SetLabel(changeAncientRelicLabel)
            else:
                changeBlueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeBlueprintCommand')
                self.sr.pickBlueprintBtn.SetLabel(changeBlueprintLabel)
        self.sr.pickInstallationBtn.width = self.sr.pickBlueprintBtn.width = max(self.sr.pickBlueprintBtn.width, self.sr.pickInstallationBtn.width)
        inOutWidth = (editWith - 4) / 2
        ioLocationID = None
        if stationID is not None:
            ioLocationID = stationID
        elif self.sr.bluePrint is not None:
            ioLocationID = sm.GetService('invCache').GetStationIDOfItem(self.sr.bluePrint)
        (inputOptions, outputOptions, inputDefault, outputDefault,) = self.GetInputOutputLocations(self.isMine, locationID=ioLocationID)
        self.sr.inputCombo = uicls.Combo(label='', parent=inputPar, options=inputOptions, name='rmInputCombo', select=inputDefault, callback=self.OnComboChange, pos=(left,
         2,
         0,
         0), width=inOutWidth, align=uiconst.TOPLEFT)
        self.sr.outputCombo = uicls.Combo(label='', parent=inputPar, options=outputOptions, name='rmOutputCombo', select=outputDefault, callback=self.OnComboChange, pos=(self.sr.inputCombo.left + self.sr.inputCombo.width + 4,
         2,
         0,
         0), width=inOutWidth, align=uiconst.TOPLEFT)
        maxRuns = None
        if activityID and activityID == const.ramActivityCopying:
            maxRuns = const.ramMaxCopyRuns
        self.sr.runsEdit = uicls.SinglelineEdit(name='runsEdit', parent=runsPar, ints=(1, maxRuns), align=uiconst.TOPLEFT, pos=(left,
         2,
         50,
         0))
        self.blueprintMPLrange = (1, None)
        if self.sr.bluePrint is not None:
            self.blueprintMPLrange = (1, cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit)
        self.sr.copyRunsEdit = uicls.SinglelineEdit(name='copyRunsEdit', parent=copyRunsPar, ints=self.blueprintMPLrange, align=uiconst.TOPLEFT, pos=(left,
         2,
         50,
         0))
        self.sr.copyRunsPar.state = uiconst.UI_HIDDEN
        self.sr.runsPar.state = uiconst.UI_HIDDEN
        noBaseItemLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoBaseItemFound')
        options = [(noBaseItemLabel, 0)]
        self.sr.inventionBaseItemCombo = uicls.Combo(label='', parent=inventionItemPar, options=options, name='rmInventionItemCombo', select=0, callback=self.OnComboChange, pos=(left,
         2,
         0,
         0), width=editWith, align=uiconst.TOPLEFT)
        noDecryptorFoundLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoDecryptorsFound')
        options = [(noDecryptorFoundLabel, 0)]
        self.sr.inventionDecryptorCombo = uicls.Combo(label='', parent=inventionDecryptorPar, options=options, name='rmInventionDecryptorCombo', select=0, callback=self.OnComboChange, pos=(left,
         2,
         0,
         0), width=editWith, align=uiconst.TOPLEFT)
        options = []
        self.sr.inventionOutputCombo = uicls.Combo(label='', parent=inventionOutputPar, options=options, name='rmInventionOutputCombo', select=0, callback=self.OnComboChange, pos=(left,
         2,
         0,
         0), width=editWith)
        if self.sr.bluePrint is not None:
            self.CheckInventionItems()
        if assemblyLine or activityID:
            if getattr(self.sr.assemblyLine, 'activityID', None):
                self.activityID = self.sr.assemblyLine.activityID
        self.GetRunsTextAndState(activityID)



    def GetInputOutputLocations(self, isMine = True, locationID = None):
        defaultFlag = (eve.session.charid, const.flagHangar) if isMine else (eve.session.corpid, const.flagHangar)
        inputSetvalue = outputSetvalue = None
        if isMine:
            if self.sr.assemblyLine and self.sr.assemblyLine.containerID == eve.session.shipid:
                defaultFlag = (eve.session.charid, const.flagCargo)
                myCargoLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MyCargo')
                containerIptOps = containerOptOps = [(myCargoLabel, (eve.session.charid, const.flagCargo))]
                for inputOption in sm.GetService('manufacturing').GetAvailableHangars(canView=0, locationID=locationID):
                    containerIptOps.append(inputOption)

            else:
                myHangarLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MyHangar')
                containerIptOps = containerOptOps = [(myHangarLabel, (eve.session.charid, const.flagHangar))]
            inputSetvalue = settings.user.ui.Get('rmInputCombo', defaultFlag)
            outputSetvalue = settings.user.ui.Get('rmOutputCombo', defaultFlag)
        else:
            inputSetvalue = settings.user.ui.Get('rmInputCombo', defaultFlag)
            outputSetvalue = settings.user.ui.Get('rmOutputCombo', defaultFlag)
            containerIptOps = sm.GetService('manufacturing').GetAvailableHangars(canView=0, locationID=locationID)
            containerOptOps = sm.GetService('manufacturing').GetAvailableHangars(all=1)
        if self.sr.bluePrint is not None:
            blueprint = self.sr.bluePrint
            for (locationString, ownerAndFlag,) in containerIptOps:
                (ownerID, flag,) = ownerAndFlag
                inputOutputSetting = settings.user.ui.Get('manufacturingfiltersetting1', 0)
                if not inputOutputSetting and ownerID == blueprint.ownerID and flag == blueprint.flagID:
                    inputSetvalue = ownerAndFlag
                    outputSetvalue = ownerAndFlag
                    break

        if len(containerIptOps):
            inputCheck = [ loc for (label, loc,) in containerIptOps if inputSetvalue == loc ]
            if not inputCheck:
                inputSetvalue = containerIptOps[0][1]
        if len(containerOptOps):
            outputCheck = [ loc for (label, loc,) in containerOptOps if outputSetvalue == loc ]
            if not outputCheck:
                outputSetvalue = containerOptOps[0][1]
        return (containerIptOps,
         containerOptOps,
         inputSetvalue,
         outputSetvalue)



    def GetQuote(self):
        quoteData = util.KeyVal()
        quoteData.blueprint = util.KeyVal(self.sr.bluePrint)
        quoteData.activityID = getattr(self.sr.installationDetails, 'activityID', None)
        quoteData.ownerInputAndflagInput = self.sr.inputCombo.GetValue()
        quoteData.ownerOutputAndflagOutput = self.sr.outputCombo.GetValue()
        quoteData.assemblyLine = self.sr.assemblyLine
        quoteData.containerID = getattr(self.sr.assemblyLine, 'containerID', None)
        quoteData.assemblyLineID = getattr(self.sr.assemblyLine, 'assemblyLineID', None)
        quoteData.ownerFlag = self.isMine
        quoteData.buildRuns = self.sr.runsEdit.GetValue()
        quoteData.containerLocationID = getattr(self.sr.installationDetails, 'containerLocationID', None)
        quoteData.ownerID = self.sr.bluePrint.ownerID
        quoteData.licensedProductionRuns = 0
        inventionItems = util.KeyVal()
        inventionItems.baseItemType = None
        inventionItems.decryptorType = None
        inventionItems.outputType = None
        if quoteData.activityID == const.ramActivityCopying:
            licensedProductionRuns = self.sr.copyRunsEdit.GetValue()
            quoteData.licensedProductionRuns = licensedProductionRuns
        elif quoteData.activityID == const.ramActivityInvention:
            inventionItems.baseItemType = self.sr.inventionBaseItemCombo.GetValue()
            inventionItems.decryptorType = self.sr.inventionDecryptorCombo.GetValue()
            inventionItems.outputType = self.sr.inventionOutputCombo.GetValue()
        elif quoteData.activityID == const.ramActivityReverseEngineering:
            inventionItems.decryptorType = self.sr.inventionDecryptorCombo.GetValue()
            inventionItems.outputType = inventionItems.decryptorType
        quoteData.inventionItems = inventionItems
        sm.GetService('manufacturing').GetQuoteDialog(quoteData)



    def Confirm(self, *args):
        self.GetQuote()



    def OnComboChange(self, combo, header, value, *args):
        if combo.name == 'rmInputCombo' and value:
            (ownerInput, flagInput,) = self.sr.inputCombo.GetValue()
            settings.user.ui.Set('rmInputCombo', (ownerInput, flagInput))
            self.CheckInventionItems()
        elif combo.name == 'rmOutputCombo' and value:
            (ownerOutput, flagOutput,) = self.sr.outputCombo.GetValue()
            settings.user.ui.Set('rmOutputCombo', (ownerOutput, flagOutput))
        elif combo.name == 'rmInventionItemCombo':
            pass
        elif combo.name == 'rmInventionDecryptorCombo':
            pass



    def GetRunsTextAndState(self, activityID):
        self.sr.runsText.hint = ''
        if activityID == const.activityCopying:
            self.sr.runsText.text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Copies')
            self.sr.copyRunsPar.state = uiconst.UI_NORMAL
        else:
            self.sr.runsText.text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Runs')
            self.sr.copyRunsPar.state = uiconst.UI_HIDDEN
        if activityID == const.activityResearchingMaterialProductivity:
            self.sr.runsText.text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MLLevels')
            self.sr.runsText.hint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialLevel')
        elif activityID == const.activityResearchingTimeProductivity:
            self.sr.runsText.text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PLLevels')
            self.sr.runsText.hint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductivityLevel')
        if activityID == const.ramActivityInvention:
            self.sr.runsPar.state = uiconst.UI_HIDDEN
        elif activityID == const.ramActivityReverseEngineering:
            self.sr.runsPar.state = uiconst.UI_HIDDEN
            self.sr.inventionItemPar.state = uiconst.UI_HIDDEN
            self.sr.inventionBaseItemCombo.state = uiconst.UI_HIDDEN
            self.sr.inventionOutputPar.state = uiconst.UI_HIDDEN
        else:
            self.sr.inventionItemPar.state = uiconst.UI_HIDDEN
            self.sr.inventionDecryptorPar.state = uiconst.UI_HIDDEN
            self.sr.inventionBaseItemCombo.state = uiconst.UI_HIDDEN
            self.sr.inventionDecryptorCombo.state = uiconst.UI_HIDDEN
            self.sr.inventionOutputPar.state = uiconst.UI_HIDDEN
            self.sr.runsPar.state = uiconst.UI_NORMAL
        if activityID in (const.ramActivityResearchingTimeProductivity, const.ramActivityResearchingMaterialProductivity):
            self.sr.outputCombo.state = uiconst.UI_HIDDEN
        else:
            self.sr.outputCombo.state = uiconst.UI_NORMAL



    def PickInstallation(self, activityID):
        self.pickingInstallation = getattr(self, 'pickingInstallation', False)
        if self.pickingInstallation:
            return 
        try:
            self.pickingInstallation = True
            stationID = None
            if self.sr.bluePrint:
                (stationID, dummy, dummy,) = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(self.sr.bluePrint)
            wnd = form.PickInstallationWindow.Open(activityID=activityID, stationID=stationID)
            if wnd.ShowModal() == uiconst.ID_OK:
                (installationDetails, assemblyLineDetails,) = wnd.result
                (iline, ilineType, ilineGroup, ilineCategory,) = installationDetails
                self.sr.installationDetails = iline
                (line, lineType, lineGroup, lineCategory,) = assemblyLineDetails
                installationName = cfg.evelocations.Get(iline.containerID).name
                if not installationName:
                    installationName = cfg.invtypes.Get(iline.containerTypeID).name
                self.sr.installationEdit.SetValue(installationName)
                self.sr.assemblyLine = line
                self.GetRunsTextAndState(self.sr.installationDetails.activityID)
                changeInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeInstallationCommand')
                self.sr.pickInstallationBtn.SetLabel(changeInstallationLabel)
                self.SetInstallationWindowCaption(self.sr.installationDetails.activityID)
                self.CheckInputOutput()
                self.CheckRuns(self.sr.installationDetails.activityID)
                self.CheckInventionItems()

        finally:
            self.pickingInstallation = False

        uthread.new(uicore.registry.SetFocus, self)



    def PickBlueprint(self, *args):
        self.pickingBlueprint = getattr(self, 'pickingBlueprint', False)
        if self.pickingBlueprint:
            return 
        if not self.sr.installationDetails:
            raise UserError('RamMustSelectInstallation')
        try:
            self.pickingBlueprint = True
            wnd = form.PickBlueprintWindow.Open(assemblyLine=self.sr.assemblyLine, installationDetails=self.sr.installationDetails)
            if wnd.ShowModal() == uiconst.ID_OK and wnd.result is not None:
                invItem = wnd.result
                self.sr.bpEdit.SetValue(cfg.invtypes.Get(invItem.typeID).name)
                self.sr.bluePrint = copy.deepcopy(invItem)
                self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
                self.GetRunsTextAndState(self.sr.installationDetails.activityID)
                self.blueprintMPLrange = (1, cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit)
                changeBlueprintLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeBlueprintCommand')
                self.sr.pickBlueprintBtn.SetLabel(changeBlueprintLabel)
                self.CheckInputOutput()
                self.CheckRuns(self.sr.installationDetails.activityID)
                self.CheckInventionItems()

        finally:
            self.pickingBlueprint = False

        uthread.new(uicore.registry.SetFocus, self)



    def PickAncientRelic(self, *args):
        self.pickingBlueprint = getattr(self, 'pickingBlueprint', False)
        if self.pickingBlueprint:
            return 
        if not self.sr.installationDetails:
            raise UserError('RamMustSelectInstallation')
        try:
            self.pickingBlueprint = True
            wnd = form.PickBlueprintWindow.Open(assemblyLine=self.sr.assemblyLine, installationDetails=self.sr.installationDetails)
            if wnd.ShowModal() == uiconst.ID_OK and wnd.result is not None:
                invItem = wnd.result
                self.sr.bpEdit.SetValue(cfg.invtypes.Get(invItem.typeID).name)
                self.sr.bluePrint = copy.deepcopy(invItem)
                self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
                self.GetRunsTextAndState(self.sr.installationDetails.activityID)
                self.blueprintMPLrange = (1, cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit)
                changeAncientRelicLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ChangeAncientRelicCommand')
                self.sr.pickBlueprintBtn.SetLabel(changeAncientRelicLabel)
                self.CheckInputOutput()
                self.CheckRuns(self.sr.installationDetails.activityID)
                self.CheckInventionItems()

        finally:
            self.pickingBlueprint = False

        uthread.new(uicore.registry.SetFocus, self)



    def CheckInputOutput(self, *args):
        preInput = self.sr.inputCombo.GetValue()
        preOutput = self.sr.outputCombo.GetValue()
        locationID = None
        if self.sr.installationDetails is not None:
            locationID = self.sr.installationDetails.containerID
        elif self.sr.bluePrint is not None:
            locationID = sm.GetService('invCache').GetStationIDOfItem(self.sr.bluePrint)
        (inputOptions, outputOption, inputSetValue, outputSetValue,) = self.GetInputOutputLocations(self.isMine, locationID=locationID)
        if preInput in [ ownerAndFlag for (locationString, ownerAndFlag,) in inputOptions ]:
            usedInputValue = preInput
        else:
            usedInputValue = inputSetValue
        if preOutput in [ ownerAndFlag for (locationString, ownerAndFlag,) in outputOption ]:
            usedOutputValue = preOutput
        else:
            usedOutputValue = outputSetValue
        self.sr.inputCombo.LoadOptions(inputOptions, usedInputValue)
        self.sr.outputCombo.LoadOptions(outputOption, usedOutputValue)



    def CheckRuns(self, activityID):
        if util.GetAttrs(self, 'sr', 'bluePrint'):
            if activityID and activityID == const.activityCopying:
                maxCopyRuns = cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit
                maxRunRuns = const.ramMaxCopyRuns
            else:
                maxCopyRuns = maxRunRuns = sys.maxint
            if self.sr.copyRunsEdit.GetValue() > maxCopyRuns:
                self.sr.copyRunsEdit.SetValue(maxCopyRuns)
            self.sr.copyRunsEdit.IntMode(0, maxCopyRuns)
            if self.sr.runsEdit.GetValue() > maxRunRuns:
                self.sr.runsEdit.SetValue(maxRunRuns)
            self.sr.runsEdit.IntMode(0, maxRunRuns)



    def GetInventionBaseItemTypes(self, blueprint, metaLevel = None):
        types = []
        if blueprint:
            try:
                invBlueprintType = cfg.invbptypes.Get(blueprint.typeID)
                typeID = invBlueprintType.productTypeID
                dogmaIM = sm.RemoteSvc('dogmaIM')
                metaTypes = cfg.invmetatypesByParent.get(typeID, [])
                types = []
                if not metaLevel:
                    types = [ x.typeID for x in metaTypes ]
                    if typeID not in types:
                        types.append(typeID)
                else:
                    for item in metaTypes:
                        for typeAttr in cfg.dgmtypeattribs.get(item.typeID, []):
                            if typeAttr.attributeID == const.attributeMetaLevel and typeAttr.value == metaLevel:
                                bpTypeID = self.GetBlueprintByProducedType(item.typeID)
                                types.append(bpTypeID)


            except Exception as e:
                log.LogError(e, 'Failed getting invention base items:')
                log.LogException()
                sys.exc_clear()
            return types



    def GetBlueprintByProducedType(self, itemTypeID):
        if not getattr(self, 'BPByProducedType', None):
            self.BPByProducedType = {}
            for typeID in cfg.invbptypes.data:
                self.BPByProducedType[cfg.invbptypes.Get(typeID).productTypeID] = typeID

        return self.BPByProducedType[itemTypeID]



    def GetInventionDecryptorTypes(self, blueprint):
        types = []
        for g in cfg.groupsByCategories.get(const.categoryDecryptors, []):
            for t in cfg.typesByGroups.get(g.groupID, []):
                types.append(t.typeID)


        return types



    def GetCompatibleInventionListFromHangar(self, stationID, flag, types, isCorp, activityID = None):
        if isCorp:
            if eve.session.locationid == stationID:
                officeID = sm.GetService('corp').GetOffice().itemID
                items = sm.GetService('invCache').GetInventoryFromId(officeID).List()
            else:
                which = {False: 'offices',
                 True: 'property'}[(not util.IsStation(stationID))]
                items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, stationID, which)
        else:
            inv = sm.GetService('invCache').GetInventory(const.containerGlobal)
            inv.InvalidateStationItemsCache(stationID)
            items = inv.ListStationItems(stationID)
        compatibleItemTypes = []
        if activityID is not None and activityID == const.ramActivityReverseEngineering:
            races = {}
            for r in cfg.races:
                races[r.raceID] = r.raceName

            for item in items:
                if item.typeID in types and item.flagID == flag:
                    type = cfg.invtypes.Get(item.typeID)
                    if type.raceID is not None:
                        name = type.typeName + ' (%s)' % races.get(type.raceID, 1)
                        name = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InventionListTypeText', item=item.typeID, race=races.get(type.raceID, 1))
                        if (name, item.typeID) not in compatibleItemTypes:
                            compatibleItemTypes.append((name, item.typeID))

        else:
            for item in items:
                if item.typeID in types and item.flagID == flag:
                    name = cfg.invtypes.Get(item.typeID).name
                    if (name, item.typeID) not in compatibleItemTypes:
                        compatibleItemTypes.append((name, item.typeID))

        return compatibleItemTypes



    def CheckInventionItems(self):
        details = self.sr.installationDetails
        if not details or details.activityID not in [const.ramActivityInvention, const.ramActivityReverseEngineering]:
            return 
        selectBaseItemLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SelectBaseItemOptional')
        itemOptions = [(selectBaseItemLabel, 0)]
        outputTypes = []
        (ownerInput, flagInput,) = self.sr.inputCombo.GetValue()
        if details.activityID == const.ramActivityInvention:
            types = self.GetInventionBaseItemTypes(self.sr.bluePrint)
            itemOptions = self.GetCompatibleInventionListFromHangar(details.containerID, flagInput, types, not self.isMine)
            if len(itemOptions) == 0:
                noBaseItemLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoBaseItemFound')
                itemOptions.insert(0, (noBaseItemLabel, 0))
            else:
                itemOptions.insert(0, (selectBaseItemLabel, 0))
        types = self.GetInventionDecryptorTypes(self.sr.bluePrint)
        decryptorOptions = self.GetCompatibleInventionListFromHangar(details.containerID, flagInput, types, not self.isMine, activityID=details.activityID)
        if len(decryptorOptions) == 0:
            noDecryptorFoundLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoDecryptorsFound')
            decryptorOptions.insert(0, (noDecryptorFoundLabel, 0))
        elif details.activityID == const.ramActivityInvention:
            selectDecryptorLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SelectDecryptorOptional')
            decryptorOptions.insert(0, (selectDecryptorLabel, 0))
        elif details.activityID == const.ramActivityReverseEngineering:
            selectDecryptorRequiredLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SelectDecryptorRequired')
            decryptorOptions.insert(0, (selectDecryptorRequiredLabel, 0))
        outputTypeIDs = self.GetInventionBaseItemTypes(self.sr.bluePrint, 5.0)
        self.sr.inventionDecryptorCombo.LoadOptions(decryptorOptions, 0)
        if outputTypeIDs:
            for typeID in outputTypeIDs:
                name = cfg.invtypes.Get(typeID).name
                outputTypes.append((name, typeID))

            self.sr.inventionBaseItemCombo.LoadOptions(itemOptions, 0)
            self.sr.inventionOutputCombo.LoadOptions(outputTypes)




class PickInstallationWindow(form.ListWindow):
    __guid__ = 'form.PickInstallationWindow'
    __nonpersistvars__ = []
    default_windowID = 'pickinstallation'

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        activityID = attributes.activityID
        stationID = attributes.stationID
        pickInstallationLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ScienceIndustryPickInstallation')
        self.scope = 'all'
        self.name = 'pickinstallation'
        self.SetCaption(pickInstallationLabel)
        self.DefineButtons(uiconst.CLOSE)
        self.invalidateOpenState = 1
        self.scroll.state = uiconst.UI_HIDDEN
        self.SetMinSize([620, 500])
        self.ModalPosition()
        self.state = uiconst.UI_NORMAL
        self.sr.installationPanel = xtriui.InstallationPanel(name='installationParent', parent=self.scroll.parent, pos=(const.defaultPadding,
         12,
         const.defaultPadding,
         12))
        self.sr.installationPanel.Init(activityID, stationID)
        self.sr.installationPanel.submitHeader = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/UseAssemblylineCommand')
        self.sr.installationPanel.submitFunc = self.SubmitInstallation



    def SubmitInstallation(self, *args):
        sel = self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected()
        if len(sel):
            line = [ entry.listvalue for entry in sel ][0]
            v = line[0].nextFreeTime
            diff = v - blue.os.GetWallclockTime()
            if diff > 5 * MIN:
                if eve.Message('RamLineInUseConfirm', {'time': diff}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
        self.Confirm()



    def Confirm(self, *etc):
        if not self.isModal:
            return 
        self.Error(self.GetError())
        if not self.GetError():
            if self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected():
                self.result = ([ entry.listvalue for entry in self.sr.installationPanel.sr.installationsScroll.GetSelected() ][0], [ entry.listvalue for entry in self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected() ][0])
            self.SetModalResult(uiconst.ID_OK)



    def GetError(self, checkNumber = 1):
        if self.sr.Get('installationPanel', None):
            if not self.sr.installationPanel.sr.installationsScroll.GetSelected():
                return localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickOneInstallation')
            if not self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected():
                return localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PickOneAssemblyLine')
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})




class PickBlueprintWindow(form.ListWindow, BlueprintData):
    __guid__ = 'form.PickBlueprintWindow'
    __nonpersistvars__ = []
    default_windowID = 'pickblueprint'

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        assemblyLine = attributes.assemblyLine
        installationDetails = attributes.installationDetails
        self.assemblyLine = assemblyLine
        self.installationDetails = installationDetails
        self.scope = 'all'
        pickBpLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ScienceIndustryPickBlueprint')
        self.SetCaption(pickBpLabel)
        self.DefineButtons(uiconst.OKCANCEL)
        self.invalidateOpenState = 1
        self.scroll.state = uiconst.UI_HIDDEN
        main = self.scroll.parent
        self.sr.corpParent = uicls.Container(name='corpParent', parent=main, pos=(0, 0, 0, 0))
        self.sr.persParent = uicls.Container(name='persParent', parent=main, pos=(0, 0, 0, 0))
        self.SetMinSize([500, 400])
        self.ModalPosition()
        self.state = uiconst.UI_NORMAL
        tabs = uicls.TabGroup(name='factoryTabs', parent=main, idx=0)
        myBpsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MyBlueprints')
        tabContent = []
        tabContent.append([myBpsLabel,
         self.sr.persParent,
         self,
         'persPickBlueprints'])
        if not util.IsNPC(eve.session.corpid) and self.CanSeeCorpBlueprints():
            corpBlueprintsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/CorporationBlueprints')
            tabContent.append([corpBlueprintsLabel,
             self.sr.corpParent,
             self,
             'corpPickBlueprints'])
        tabs.Startup(tabContent, 'pickBlueprintWindowTabs', UIIDPrefix='scienceAndIndustryTab')
        self.sr.maintabs = tabs



    def Load(self, key):
        self.LoadBlueprints(bool(key == 'persPickBlueprints'))



    def LoadBlueprints(self, isMine = 1):
        key = ['corp', 'pers'][isMine]
        isCorp = not isMine
        if not getattr(self, '%sInited' % key, None):
            parent = self.sr.Get('%sParent' % key, None)
            filters = uicls.Container(name='filters', parent=parent, height=33, align=uiconst.TOTOP)
            allLabel = localization.GetByLabel('UI/Common/All')
            copiesLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Copies')
            originalsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Originals')
            copies = [(allLabel, None), (copiesLabel, 1), (originalsLabel, 0)]
            typeLabel = localization.GetByLabel('UI/Common/Type')
            c = uicls.Combo(label=typeLabel, parent=filters, options=copies, name='copies', select=settings.user.ui.Get('blueprint_copyfilter', None), callback=self.BlueprintComboChange, pos=(7, 15, 0, 0), align=uiconst.TOPLEFT)
            setattr(self.sr, '%s_blueprintCopyFilter' % key, c)
            if isCorp:
                divisions = sm.GetService('manufacturing').GetAvailableHangars(canView=1, canTake=1)
                divisions.insert(0, (allLabel, (None, None)))
                divisionLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Division')
                c = uicls.Combo(label=divisionLabel, parent=filters, options=divisions, name='divisions', select=settings.user.ui.Get('blueprint_divisionfilter', (None, None)), callback=self.BlueprintComboChange, pos=(self.sr.corp_blueprintCopyFilter.left + self.sr.corp_blueprintCopyFilter.width + 4,
                 15,
                 0,
                 0), align=uiconst.TOPLEFT)
                self.sr.blueprintDivisionFilter = c
            scroll = uicls.Scroll(parent=parent, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            scroll.sr.id = '%sPickBlueprintsScroll' % key
            scroll.multiSelect = 0
            setattr(self.sr, '%sPickBlueprintsScroll' % key, scroll)
        scroll = self.sr.Get('%sPickBlueprintsScroll' % key, None)
        accessScrollHint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoBlueprintsInRegion', regionName=cfg.evelocations.Get(eve.session.regionid).name)
        defaultHeaders = uix.GetInvItemDefaultHeaders()
        copyLabel = localization.GetByLabel('UI/Common/Copy')
        mlLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ML')
        plLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PL')
        runsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Runs')
        headers = defaultHeaders[:4] + [copyLabel,
         mlLabel,
         plLabel,
         runsLabel]
        scroll.SetColumnsHiddenByDefault(defaultHeaders[4:])
        scrolllist = []
        containerType = cfg.invtypes.Get(self.installationDetails.containerTypeID)
        if isCorp:
            if containerType.groupID in (const.groupAssemblyArray, const.groupMobileLaboratory):
                if eve.session.solarsystemid == self.installationDetails.containerLocationID:
                    locationName = cfg.evelocations.Get(self.installationDetails.containerID).locationName
                    if not (locationName and locationName[0] != '@'):
                        locationName = cfg.invtypes.Get(self.installationDetails.containerTypeID).typeName
                    dist = 0
                    bp = sm.StartService('michelle').GetBallpark()
                    if bp:
                        otherBall = bp and bp.GetBall(self.installationDetails.containerID) or None
                        ownBall = bp and bp.GetBall(eve.session.shipid) or None
                        dist = otherBall and max(0, otherBall.surfaceDist)
                    if dist is None:
                        dist = 2 * const.maxCargoContainerTransferDistance
                    if dist >= const.maxCargoContainerTransferDistance:
                        text = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationOutOfRangeMaxRange', locationName=locationName, maxRange=const.maxCargoContainerTransferDistance)
                        scrolllist.append(listentry.Get('Text', {'text': text}))
                    else:
                        blueprintCount = 0
                        installationID = self.installationDetails.containerID
                        inv = sm.GetService('invCache').GetInventoryFromId(installationID)
                        for invItem in inv.List():
                            if invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
                                blueprintCount += 1

                        if blueprintCount > 0:
                            structure = util.KeyVal()
                            structure.structureID = installationID
                            structure.blueprintCount = blueprintCount
                            locationData = self.GetLocationDataStructure(eve.session.solarsystemid, structure, 'allitems', isCorp=isCorp, locationName=locationName, scrollID=scroll.sr.id)
                            scrolllist.append(listentry.Get('Group', locationData))
            setattr(self, '%sInited' % key, 1)
        if self.assemblyLine and self.assemblyLine.containerID == eve.session.shipid:
            if not isMine:
                accessScrollHint = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AssemblyIsAShip')
            else:
                blueprintCount = 0
                inv = sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)
                for invItem in inv.List(const.flagCargo):
                    if invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
                        blueprintCount += 1

                scrolllist.append(listentry.Get('Group', self.GetLocationDataCargo(blueprintCount, 'allitems', scrollID=scroll.sr.id)))
                setattr(self, '%sInited' % key, 1)
        else:
            sortlocations = sm.GetService('assets').GetAll('regitems', blueprintOnly=1, isCorp=isCorp)
            for (solarsystemID, station,) in sortlocations:
                if station.blueprintCount:
                    scrolllist.append(listentry.Get('Group', self.GetLocationData(solarsystemID, station, 'allitems', isCorp=isCorp, scrollID=scroll.sr.id)))

            setattr(self, '%sInited' % key, 1)
        scroll.Load(contentList=scrolllist, headers=headers)
        if not len(scrolllist):
            scroll.ShowHint(accessScrollHint)



    def BlueprintComboChange(self, *args):
        sm.GetService('manufacturing').ReloadBlueprints(form.PickBlueprintWindow, ('persPickBlueprints', 'corpPickBlueprints'))



    def ReloadBlueprints(self):
        wnd = form.PickBlueprintWindow.GetIfOpen()
        if wnd and wnd.sr.maintabs.GetSelectedArgs() in ('persPickBlueprints', 'corpPickBlueprints'):
            wnd.sr.maintabs.ReloadVisible()
        wnd = form.AssetsWindow.GetIfOpen()
        if wnd:
            wnd.sr.maintabs.ReloadVisible()



    def Confirm(self, *etc):
        if not self.isModal:
            return 
        self.Error(self.GetError())
        if not self.GetError():
            scrollName = None
            if self.sr.maintabs.GetSelectedArgs() == 'persPickBlueprints':
                scrollName = 'persPickBlueprintsScroll'
            else:
                scrollName = 'corpPickBlueprintsScroll'
            if scrollName is not None:
                selected = self.sr.Get(scrollName, None).GetSelected()
                if len(selected):
                    self.result = [ entry.listvalue for entry in selected ][0]
                    self.SetModalResult(uiconst.ID_OK)



    def GetError(self, checkNumber = 1):
        return ''




class ManufacturingQuoteWindow(form.ListWindow):
    __guid__ = 'form.ManufacturingQuoteWindow'
    __nonpersistvars__ = []
    default_windowID = 'manufacturingquotewindow'
    default_quote = None
    quote_doc = 'Quote'

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        quote = attributes.quote
        quoteData = attributes.quoteData
        acceptQuoteLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AcceptQuote')
        acceptQuoteCmdLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AcceptQuoteCommand')
        self.scope = 'all'
        self.SetCaption(acceptQuoteLabel)
        self.DefineButtons(uiconst.CLOSE)
        self.invalidateOpenState = 1
        self.scroll.state = uiconst.UI_HIDDEN
        self.MakeUnResizeable()
        self.state = uiconst.UI_NORMAL
        self.sr.quotePanel = xtriui.QuotePanel(name='quoteParent', parent=self.scroll.parent, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.quotePanel.Init(quote, quoteData)
        self.sr.quotePanel.submitHeader = acceptQuoteCmdLabel
        self.sr.quotePanel.submitFunc = self.AcceptQuote
        scroll = uiutil.GetChild(self.sr.quotePanel, 'installationsScroll')
        details = uiutil.GetChild(self.sr.quotePanel, 'installationDetails')
        content = uiutil.GetChild(scroll, '__content')
        minScrollHeight = 128
        maxScrollHeight = 384
        scroll.height = minScrollHeight
        blue.pyos.synchro.SleepWallclock(0)
        scroll.height = min(maxScrollHeight, scroll.height + scroll.scrollingRange)
        self.height = scroll.height + details.height + 76
        self.SetMinSize([600, self.height])



    def AcceptQuote(self, *args):
        self.Confirm()



    def Confirm(self, *etc):
        self.SetModalResult(uiconst.ID_OK)



    def GetError(self):
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})




class QuotePanel(uicls.Container):
    __guid__ = 'xtriui.QuotePanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.submitHeader = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/AcceptQuoteCommand')
        self.inited = 0
        self.submitFunc = None



    def _OnClose(self):
        uicls.Container._OnClose(self)
        self.submitFunc = None
        self.selectedAssemblyLine = None



    def Init(self, quote, quoteData):
        self.quote = quote
        self.quoteData = quoteData
        self.sr.quoteScroll = uicls.Scroll(name='installationsScroll', parent=self, align=uiconst.TOTOP, height=256)
        self.sr.quoteScroll.sr.id = 'quoteScroll'
        self.sr.quoteDetails = uicls.Container(name='installationDetails', parent=self, height=64, align=uiconst.TOBOTTOM, idx=0)
        self.inited = 1
        self.LoadQuote()



    def FindItemInHangar(typeID, hangar, flag):
        pass



    def GetMissingMaterialString(self, content, missing):
        contentCount = len(content)
        missingCount = 0
        if type(content) == types.DictType:
            for (typeID, level,) in content.iteritems():
                if missing.has_key(typeID):
                    missingCount += 1

        else:
            for each in content:
                typeID = getattr(each, 'requiredTypeID', None)
                if typeID and missing.has_key(typeID):
                    missingCount += 1

        if missingCount == 0:
            return ''
        return localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MissingAmountOfUnit', missing=missingCount, content=contentCount)



    def LoadQuote(self, *args):
        uix.Flush(self.sr.quoteDetails)
        self.sr.quoteScroll.Load(contentList=[], headers=[])
        self.sr.quoteScroll.ShowHint('Fetching quote...')
        nameLabel = localization.GetByLabel('UI/Common/Name')
        requiredLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Required')
        missingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Missing')
        dmgJobLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/DamagePerJob')
        wasteLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Waste')
        scrolllist = []
        bom = []
        headers = [nameLabel,
         requiredLabel,
         missingLabel,
         dmgJobLabel,
         wasteLabel]
        self.sr.quoteScroll.sr.fixedColumns = {nameLabel: 224,
         requiredLabel: 70,
         missingLabel: 70,
         dmgJobLabel: 60,
         wasteLabel: 60}
        if self.quote.bom:
            if len(self.quote.bom.rawMaterials):
                rawMaterialLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RawMaterial')
                bom.append((rawMaterialLabel, self.quote.bom.rawMaterials))
            if len(self.quote.bom.extras):
                extraMaterialLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ExtraMaterial')
                bom.append((extraMaterialLabel, self.quote.bom.extras))
            if len(self.quote.bom.skills):
                skillLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Skill')
                bom.append((skillLabel, self.quote.bom.skills))
            for (label, content,) in bom:
                id = ('BOM', label)
                uicore.registry.SetListGroupOpenState(id, 1)
                data = {'GetSubContent': self.GetBOMSubContent,
                 'label': label,
                 'groupItems': content,
                 'wasteMaterials': self.quote.bom.wasteMaterials,
                 'missingMaterials': self.quote.missingMaterials,
                 'id': id,
                 'tabs': [],
                 'showlen': False,
                 'posttext': self.GetMissingMaterialString(content, self.quote.missingMaterials),
                 'state': 'locked',
                 'showicon': 'hide',
                 'hideExpander': True,
                 'hideExpanderLine': True,
                 'disableToggle': True,
                 'BlockOpenWindow': True}
                scrolllist.append(listentry.Get('Group', data))

        self.sr.quoteScroll.Load(contentList=scrolllist, headers=headers)
        if scrolllist:
            self.sr.quoteScroll.ShowHint()
        else:
            noMaterialsRequiredLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoMaterialsRequired')
            self.sr.quoteScroll.ShowHint(noMaterialsRequiredLabel)
        uix.Flush(self.sr.quoteDetails)
        productionStartTimeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductionStartTime')
        productionTimeLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ProductionTime')
        totalCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TotalCost')
        installCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/InstallCost')
        usageCostLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/UsageCost')
        walletDivisionLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/WalletDivision')
        mtrlMultiAsmblyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialMultiplierAssemblyItem')
        mtrlMultiSkillLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialMultiplierSkill')
        timeMultiAsmblyLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TimeMultiplierAssemblyItem')
        timeMultiSkillLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/TimeMultiplierSkill')
        d = [(productionStartTimeLabel, 'maxJobStartTime'),
         (productionTimeLabel, 'productionTime'),
         (totalCostLabel, 'cost'),
         (installCostLabel, 'installCost'),
         (usageCostLabel, 'usageCost')]
        d.append((walletDivisionLabel, 'accountKey'))
        d.extend([(mtrlMultiAsmblyLabel, 'materialMultiplier'),
         (mtrlMultiSkillLabel, 'charMaterialMultiplier'),
         (timeMultiAsmblyLabel, 'timeMultiplier'),
         (timeMultiSkillLabel, 'charTimeMultiplier')])
        i = 0
        j = -1
        left = 0
        tabs = [130, 300]
        top = 4
        maxHeight = 0
        for (header, key,) in d:
            if j == -1:
                top = 4
            if key not in self.quote.header:
                continue
            value = getattr(self.quote, key, '')
            if key in ('charTimeMultiplier',):
                value = value / 2
            if key in ('cost', 'installCost', 'usageCost'):
                value = util.FmtISK(value)
            if key == 'accountKey':
                value = sm.GetService('corp').GetCorpAccountName(value)
            if key == 'productionTime':
                value = util.FmtDate(long(float(value) * 10000000L))
            if key == 'maxJobStartTime':
                if value is not None:
                    value = value - blue.os.GetWallclockTime()
                    if value < 0:
                        nowLabel = localization.GetByLabel('UI/Common/Now')
                        value = '<color=0xff00FF00>%s<color=0xffffffff>' % nowLabel
                    else:
                        value = int(value / 600000000L) * 10000000L * 60
                    value = '<color=0xffFF0000>%s<color=0xffffffff>' % util.FmtDate(value)
            t = uicls.EveLabelMedium(text='%s<t><right>%s' % (header, value), parent=self.sr.quoteDetails, left=left, top=top, singleline=0, tabs=tabs)
            t.hint = header
            top = top + t.height
            maxHeight = max(top, maxHeight)
            i += 1
            j += 1
            if i == 5:
                j = -1
                left += 300
                tabs = [220, 280]

        uicls.Line(parent=self.sr.quoteDetails, align=uiconst.RELATIVE, top=4, width=1, height=maxHeight, left=300)
        top = maxHeight + 8
        if len(self.quote.missingMaterials) > 0:
            materialOrSkillMissingLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/MaterialOrSkillMissing')
            t = uicls.EveLabelMedium(text='<color=0xffff0000>%s' % materialOrSkillMissingLabel, parent=self.sr.quoteDetails, left=6, top=top, singleline=0)
        submit = uicls.Button(parent=self.sr.quoteDetails, label=self.submitHeader, func=self.Submit, args=None, pos=(0,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        refreshLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RefreshCommand')
        refreshBtn = uicls.Button(parent=self.sr.quoteDetails, label=refreshLabel, func=self.Refresh, args=None, pos=(submit.width + 4,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        top = submit.height + top
        self.sr.quoteDetails.height = top + 6
        uicore.registry.SetFocus(submit)



    def Refresh(self, *args):
        sm.GetService('manufacturing').GetQuoteDialog(self.quoteData)



    def Refresh(self, *args):
        sm.GetService('manufacturing').GetQuoteDialog(self.quoteData)



    def GetBOMSubContent(self, nodedata, *args):
        scrolllist = []
        rawMaterialLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/RawMaterial')
        if rawMaterialLabel in [nodedata.label, nodedata.Get('cleanLabel', None)]:
            for rawMaterial in nodedata.groupItems:
                waste = 0
                qty = rawMaterial.quantity
                for x in nodedata.wasteMaterials:
                    if x.requiredTypeID == rawMaterial.requiredTypeID:
                        waste = int(float(x.quantity) / float(rawMaterial.quantity + x.quantity) * 1000.0) / 10.0
                        qty += x.quantity
                        break

                data = util.KeyVal()
                data.checked = True
                req = 0
                if nodedata.missingMaterials.has_key(rawMaterial.requiredTypeID):
                    data.checked = False
                    req = nodedata.missingMaterials.get(rawMaterial.requiredTypeID)
                invType = cfg.invtypes.Get(rawMaterial.requiredTypeID)
                data.text = '%s<t>%s<t>%s<t>%s<t>%s' % (invType.typeName,
                 qty,
                 req,
                 '100%',
                 '%s%%' % waste)
                data.showinfo = True
                data.typeID = rawMaterial.requiredTypeID
                data.sublevel = 1
                data.line = 1
                factorLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Factor')
                data.Set('sort_%s' % factorLabel, rawMaterial.quantity)
                scrolllist.append(listentry.Get('CheckEntry', data=data))

        extraMaterialLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ExtraMaterial')
        if extraMaterialLabel in [nodedata.label, nodedata.Get('cleanLabel', None)]:
            for extra in nodedata.groupItems:
                if extra.isSkillCheck:
                    continue
                data = util.KeyVal()
                data.checked = True
                req = 0
                reqStr = ''
                if nodedata.missingMaterials.has_key(extra.requiredTypeID):
                    data.checked = False
                    reqStr = req = nodedata.missingMaterials.get(extra.requiredTypeID)
                data.text = '%s<t>%s<t>%s<t>%s<t>%s' % (cfg.invtypes.Get(extra.requiredTypeID).typeName,
                 extra.quantity,
                 reqStr,
                 '%s %%' % (100.0 * float(extra.damagePerJob)),
                 '')
                data.showinfo = True
                data.typeID = extra.requiredTypeID
                data.sublevel = 1
                data.line = 1
                scrolllist.append(listentry.Get('CheckEntry', data=data))

        skillLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Skill')
        if skillLabel in [nodedata.label, nodedata.Get('cleanLabel', None)]:
            for (typeID, level,) in nodedata.groupItems.iteritems():
                data = util.KeyVal()
                data.checked = True
                req = 0
                if nodedata.missingMaterials.has_key(typeID):
                    data.checked = False
                    req = nodedata.missingMaterials.get(typeID)
                data.text = '%s<t>%s<t>%s<t>%s<t>%s' % (cfg.invtypes.Get(typeID).typeName,
                 level,
                 req or '',
                 '',
                 '')
                data.showinfo = True
                data.typeID = typeID
                data.sublevel = 1
                data.line = 1
                scrolllist.append(listentry.Get('CheckEntry', data=data))

        return scrolllist



    def Submit(self, *args):
        if self.submitFunc:
            self.submitFunc()




class PlanetPanel(uicls.Container):
    __guid__ = 'xtriui.PlanetPanel'
    __notifyevents__ = ['OnPlanetCommandCenterDeployedOrRemoved',
     'OnPlanetPinsChanged',
     'OnColonyPinCountUpdated',
     'OnSessionChanged']

    def Init(self):
        self.inited = 1
        sm.RegisterNotify(self)
        self.parentContainer = uicls.Container(name='parent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.planetScroll = uicls.Scroll(name='installationsScroll', parent=self.parentContainer)
        self.sr.planetScroll.multiSelect = False
        self.sr.planetScroll.sr.id = 'planetscroll'
        self.sr.planetScroll.OnSelectionChange = self.OnPlanetScrollSelectionChange
        self.planetClickID = None
        (scrolllist, headers,) = self.GetPlanetScrollList()
        noCommandBuiltLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NoCommandCenterBuilt')
        self.sr.planetScroll.Load(contentList=scrolllist, headers=headers, noContentHint=noCommandBuiltLabel)
        viewPlanetLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ViewPlanet')
        self.sr.buttons = uicls.ButtonGroup(btns=[[viewPlanetLabel, self.ViewPlanet, ()]], parent=self.parentContainer, idx=0)
        viewPlanetLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/ViewPlanet')
        self.sr.viewPlanetBtn = self.sr.buttons.GetBtnByLabel(viewPlanetLabel)
        self.sr.viewPlanetBtn.Disable()



    def GetPlanetScrollList(self):
        scrolllist = []
        rows = sm.GetService('planetSvc').GetMyPlanets()
        locationIDs = set()
        for row in rows:
            locationIDs.update([row.planetID, row.solarSystemID])

        cfg.evelocations.Prime(locationIDs)
        for row in rows:
            planetName = cfg.evelocations.Get(row.planetID).locationName
            planetInstallationsLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PlanetHasInstallations', planetName=planetName, installations=row.numberOfPins)
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (cfg.evelocations.Get(row.solarSystemID).locationName,
             cfg.invtypes.Get(row.typeID).typeName,
             planetName,
             localizationUtil.FormatNumeric(row.numberOfPins, decimalPlaces=0, useGrouping=True)), GetMenu=self.GetPlanetEntryMenu, OnClick=self.OnPlanetEntryClick, planetID=row.planetID, typeID=row.typeID, hint=planetInstallationsLabel, solarSystemID=row.solarSystemID, OnDblClick=self.OnPlanetEntryDblClick)
            scrolllist.append(listentry.Get('Generic', data=data))

        headers = [localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/SystemName'),
         localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PlanetType'),
         localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/PlanetName'),
         localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Installations')]
        return (scrolllist, headers)



    def OnPlanetScrollSelectionChange(self, selected):
        if selected:
            self.sr.viewPlanetBtn.Enable()
        else:
            self.sr.viewPlanetBtn.Disable()



    def OnPlanetCommandCenterDeployedOrRemoved(self):
        self.LoadPlanetScroll()



    def OnPlanetPinsChanged(self, planetID):
        self.LoadPlanetScroll()



    def OnColonyPinCountUpdated(self, planetID):
        self.LoadPlanetScroll()



    def OnSessionChanged(self, isRemote, sess, change):
        self.LoadPlanetScroll()



    def LoadPlanetScroll(self):
        (scrolllist, headers,) = self.GetPlanetScrollList()
        self.sr.planetScroll.Load(contentList=scrolllist, headers=headers)



    def GetPlanetEntryMenu(self, entry):
        node = entry.sr.node
        menu = []
        menuSvc = sm.GetService('menu')
        if node.solarSystemID != session.solarsystemid:
            mapItem = sm.StartService('map').GetItem(node.solarSystemID)
            if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                gmExtrasLabel = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GMWMExtrasCommand')
                menu += [(gmExtrasLabel, ('isDynamic', menuSvc.GetGMMenu, (node.planetID,
                    None,
                    None,
                    None,
                    mapItem)))]
            menu += menuSvc.MapMenu([node.solarSystemID])
            isOpen = sm.GetService('viewState').IsViewActive('planet') and sm.GetService('planetUI').planetID == node.planetID
            if isOpen:
                menu += [[localization.GetByLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ()]]
            else:
                openPlanet = lambda planetID: sm.GetService('viewState').ActivateView('planet', planetID=planetID)
                menu += [(localization.GetByLabel('UI/PI/Common/ViewInPlanetMode'), sm.GetService('planetUI').Open, (node.planetID,))]
            menu += [(localization.GetByLabel('UI/Commands/ShowInfo'), menuSvc.ShowInfo, (node.typeID,
               node.planetID,
               0,
               None,
               None))]
        else:
            menu += menuSvc.CelestialMenu(node.planetID)
        return menu



    def ViewPlanet(self):
        if self.planetClickID is None:
            return 
        sm.GetService('viewState').ActivateView('planet', planetID=self.planetClickID)



    def OnPlanetEntryClick(self, entry):
        node = entry.sr.node
        self.planetClickID = node.planetID



    def OnPlanetEntryDblClick(self, entry):
        node = entry.sr.node
        sm.GetService('viewState').ActivateView('planet', planetID=node.planetID)




