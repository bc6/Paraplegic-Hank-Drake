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
import dbg
import math
import types
import log
import uiconst
import uicls
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
        states = [(None, mls.UI_RMR_ANYACTIVESTATE),
         (const.ramJobStatusPending, mls.UI_RMR_PENDING),
         (const.ramJobStatusInProgress, mls.UI_RMR_INPROGRESS),
         (const.ramJobStatusReady, mls.UI_RMR_READY),
         (const.ramJobStatusDelivered, mls.UI_RMR_DELIVERED)]
        self.states = [ (stateID, text) for (stateID, text,) in states ]
        self.statesIdx = dict(self.states)
        self.relevantskills = None
        self.relevantskillscachetime = None



    def Stop(self, memStream = None):
        if not sm.IsServiceRunning('window'):
            return 
        wnd = sm.GetService('window').GetWindow('manufacturing')
        if wnd is not None:
            wnd.CloseX()
        self.detailsByRegionByTypeFlag = {}



    def _FillActivities(self):
        self.detailsByRegionByTypeFlag = {}
        activities = [[const.activityNone, mls.UI_RMR_ALLACTIVITIES],
         [const.activityManufacturing, mls.UI_RMR_MANUFACTURING],
         [const.activityResearchingMaterialProductivity, mls.UI_RMR_MATERIALRESEARCH],
         [const.activityResearchingTimeProductivity, mls.UI_RMR_TIMEEFFICIENCYRESEARCH],
         [const.activityCopying, mls.UI_RMR_COPYING],
         [const.activityDuplicating, mls.UI_RMR_DUBLICATING],
         [const.activityResearchingTechnology, mls.UI_RMR_TECHNOLOGY],
         [const.activityInvention, mls.UI_RMR_INVENTION],
         [const.activityReverseEngineering, mls.UI_RMR_REVERSEENGINEERING]]
        self.activities = [ (activityID, text) for (activityID, text,) in activities if cfg.ramactivities.Get(activityID).published ]
        self.activitiesIdx = dict(self.activities)



    def PopulateActivities(self):
        if self.activities:
            return 
        self.LogInfo('Populating activities')
        activities = [[const.activityNone, mls.UI_RMR_ALLACTIVITIES],
         [const.activityManufacturing, mls.UI_RMR_MANUFACTURING],
         [const.activityResearchingMaterialProductivity, mls.UI_RMR_MATERIALRESEARCH],
         [const.activityResearchingTimeProductivity, mls.UI_RMR_TIMEEFFICIENCYRESEARCH],
         [const.activityCopying, mls.UI_RMR_COPYING],
         [const.activityDuplicating, mls.UI_RMR_DUBLICATING],
         [const.activityResearchingTechnology, mls.UI_RMR_TECHNOLOGY],
         [const.activityInvention, mls.UI_RMR_INVENTION],
         [const.activityReverseEngineering, mls.UI_RMR_REVERSEENGINEERING]]
        self.activities = [ (activityID, text) for (activityID, text,) in activities if cfg.ramactivities.Get(activityID).published ]
        self.activitiesIdx = dict(self.activities)



    def GetActivities(self):
        self.PopulateActivities()
        return self.activities



    def GetStates(self):
        return self.states



    def GetRestrictionMasks(self):
        m = [(mls.UI_RMR_ALLOWALLIANCEMEMBERUSAGE, 'ramRestrictByAlliance', const.ramRestrictByAlliance),
         (mls.UI_RMR_ALLOWCORPMEMBERUSAGE, 'ramRestrictByCorp', const.ramRestrictByCorp),
         (mls.UI_RMR_ALLOWBYSTANDINGRANGE, 'ramRestrictByStanding', const.ramRestrictByStanding),
         (mls.UI_RMR_ALLOWSECURITYRANGE, 'ramRestrictBySecurity', const.ramRestrictBySecurity)]
        return m



    def GetRanges(self, beyondCurrent = False):
        ranges = [((eve.session.solarsystemid2, const.groupSolarSystem), mls.UI_GENERIC_CURRENTSOLARSYS), ((eve.session.constellationid, const.groupConstellation), mls.UI_GENERIC_CURRENTCONSTELLATION), ((eve.session.regionid, const.groupRegion), mls.UI_GENERIC_CURRENTREGION)]
        if beyondCurrent:
            (ranges.append(((0, 0), mls.UI_GENERIC_CURRENTUNIVERSE)),)
        if eve.session.stationid:
            ranges.insert(0, ((eve.session.stationid, const.groupStation), mls.UI_GENERIC_CURRENTSTATION))
        self.ranges = [ (locationData, text) for (locationData, text,) in ranges ]
        self.rangesIdx = dict(self.ranges)
        return self.ranges



    def OnSessionChanged(self, isremote, sess, change):
        if 'userid' in change:
            self._FillActivities()
        if 'regionid' in change or 'shipid' in change:
            self.detailsByRegionByTypeFlag = {}
        if 'stationid' in change or 'solarsystemid' in change or 'regionid' in change or 'constellationid' in change or 'shipid' in change:
            wnd = sm.GetService('window').GetWindow('manufacturing')
            if wnd:
                wnd.Reload()



    def Show(self, minimized = False, panelName = None):
        window = sm.GetService('window').GetWindow('manufacturing', decoClass=form.Manufacturing, maximize=1, create=1)
        if panelName is not None:
            uthread.new(window.sr.maintabs.ShowPanelByName, panelName)



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
        wnd = sm.GetService('window').GetWindow('manufacturing')
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
        wnd = sm.GetService('window').GetWindow('ManufacturingInstallation')
        if wnd is not None and not wnd.destroyed:
            wnd.Show()
            return 
        if activityID is None:
            activityID = installationDetails.activityID
        wnd = sm.GetService('window').GetWindow('ManufacturingInstallation', create=1, activityID=activityID)
        wnd.Load(invItem, assemblyLine, activityID, installationDetails)



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
        title = {False: mls.UI_RMR_COMPLETINGJOBS,
         True: mls.UI_RMR_CANCELLINGJOBS}[cancel]
        text = {False: mls.UI_RMR_COMPLETINGJOBS,
         True: mls.UI_RMR_CANCELLINGJOBS}[cancel]
        try:
            sm.GetService('loading').ProgressWnd(title, text, 1, 2)
            result = sm.ProxySvc('ramProxy').CompleteJob(installationLocationData, jobdata.jobID, cancel)
            if hasattr(result, 'messageLabel'):
                if result.jobCompletedSuccessfully:
                    eve.Message('RamInventionJobSucceeded', {'info': getattr(mls, result.messageLabel, ''),
                     'me': result.outputME,
                     'pe': result.outputPE,
                     'runs': result.outputRuns,
                     'type': (TYPEID, result.outputTypeID),
                     'typeid': result.outputTypeID,
                     'itemid': result.outputItemID})
                else:
                    eve.Message('RamInventionJobFailed', {'info': getattr(mls, result.messageLabel, '')})
            if hasattr(result, 'message'):
                eve.Message(result.message.msg, result.message.args)
            sm.GetService('loading').ProgressWnd(title, mls.UI_GENERIC_DONE, 2, 2)
        except UserError as what:
            sm.GetService('loading').ProgressWnd(title, mls.UI_GENERIC_DONE, 1, 1)
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
            self.relevantskillscachetime = blue.os.GetTime()
        return self.relevantskills



    def ResetRelevantCharSkills(self):
        if self.relevantskills is None:
            return 
        t = blue.os.GetTime()
        if t - self.relevantskillscachetime > MIN * 15:
            self.relevantskills = None



    def GetInstallationDetails(self, installationLocationData):
        return sm.ProxySvc('ramProxy').GetInstallationDetails(installationLocationData)



    def IsRamInstallable(self, item):
        if item.categoryID == const.categoryBlueprint:
            return True
        return False



    def IsReverseEngineering(self, item):
        if item.categoryID == const.categoryAncientRelic:
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
        if session.shipid <= 0:
            raise UserError('RamNoShip')
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
                        raise UserError('RamCorpBOMItemNoSuchOffice', {'location': cfg.evelocations.Get(quoteData.containerID).locationName})
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
        sm.GetService('loading').ProgressWnd(mls.UI_RMR_CALCULATINGQUOTE, mls.UI_RMR_GETTINGQUOTEFROMINSTALLATION, 1, 3)
        blue.pyos.synchro.Sleep(0)
        quote = None
        try:
            job = sm.ProxySvc('ramProxy').InstallJob(installationLocationData, installedItemLocationData, bomLocationData, flagOutput, quoteData.buildRuns, quoteData.activityID, quoteData.licensedProductionRuns, not quoteData.ownerFlag, 'blah', quoteOnly=1, installedItem=quoteData.blueprint, maxJobStartTime=quoteData.assemblyLine.nextFreeTime + 1 * MIN, inventionItems=quoteData.inventionItems, inventionOutputItemID=quoteData.inventionItems.outputType)
            quote = job.quote
            if job.installedItemID:
                quoteData.blueprint.itemID = job.installedItemID
                installedItemLocationData[2] = [job.installedItemID]
        except UserError as e:
            sm.GetService('loading').ProgressWnd(mls.UI_RMR_CANCELLINGQUOTE, mls.UI_RMR_QUOTENOTACCEPTED, 1, 1)
            raise 
        finishingText = mls.UI_GENERIC_DONE
        if quote is not None:
            sm.GetService('loading').ProgressWnd(mls.UI_RMR_CALCULATINGQUOTE, mls.UI_RMR_GETTINGQUOTEFROMINSTALLATION, 3, 3)
            wnd = sm.GetService('window').GetWindow('manufacturingquotewindow')
            if wnd:
                wnd.CloseX()
            wnd = sm.GetService('window').GetWindow('manufacturingquotewindow', create=1, decoClass=form.ManufacturingQuoteWindow, quote=quote, quoteData=quoteData)
            if wnd.ShowDialog() == uiconst.ID_OK:
                sm.GetService('loading').ProgressWnd(mls.UI_RMR_INSTALLINGJOB, mls.UI_RMR_INSTALLINGJOBHINT, 2, 4)
                try:
                    authorizedCost = quote.cost
                    sm.services['objectCaching'].InvalidateCachedMethodCall('ramProxy', 'AssemblyLinesGet', quoteData.containerID)
                    sm.ProxySvc('ramProxy').InstallJob(installationLocationData, installedItemLocationData, bomLocationData, flagOutput, quoteData.buildRuns, quoteData.activityID, quoteData.licensedProductionRuns, not quoteData.ownerFlag, 'blah', quoteOnly=0, authorizedCost=authorizedCost, installedItem=quoteData.blueprint, maxJobStartTime=quoteData.assemblyLine.nextFreeTime + 1 * MIN, inventionItems=quoteData.inventionItems, inventionOutputItemID=quoteData.inventionItems.outputType)
                    sm.GetService('objectCaching').InvalidateCachedMethodCall('ramProxy', 'GetJobs2', ownerInput, 0)
                    sm.GetService('manufacturing').ReloadBlueprints()
                    sm.GetService('manufacturing').ReloadInstallations()
                    sm.GetService('loading').ProgressWnd(mls.UI_RMR_INSTALLINGJOB, mls.UI_RMR_COMPLETINGINSTALLATION, 3, 4)
                    wnd.CloseX()
                    wnd = sm.GetService('window').GetWindow('ManufacturingInstallation')
                    if wnd:
                        wnd.CloseX()
                except UserError as what:

                    def f():
                        raise what


                    uthread.new(f)
                    sys.exc_clear()
                    finishingText = mls.UI_RMR_CANCELLINGINSTALLATION
                    sm.GetService('loading').ProgressWnd(mls.UI_RMR_INSTALLINGJOB, mls.UI_RMR_CANCELLINGINSTALLATION, 3, 4)
            else:
                finishingText = mls.UI_RMR_CANCELLINGINSTALLATION
        sm.GetService('loading').ProgressWnd(mls.UI_RMR_INSTALLINGJOB, finishingText, 4, 4)



    def ReloadBlueprints(self, windowname = 'manufacturing', args = ('persBlueprints', 'sciAndIndustryCorpBlueprintsTab')):
        now = blue.os.GetTime(1)
        self.lastReloadBlueprintsCallTime = now
        blue.pyos.synchro.Sleep(1000)
        if now != self.lastReloadBlueprintsCallTime:
            return 
        wnd = sm.GetService('window').GetWindow(windowname)
        if wnd is None or wnd.destroyed:
            return 
        uthread.Lock(self, 'ReloadBlueprints')
        try:
            sm.GetService('invCache').InvalidateGlobal()
            wnd = sm.GetService('window').GetWindow(windowname)
            if wnd and wnd.sr.maintabs.GetSelectedArgs() in args:
                wnd.sr.maintabs.ReloadVisible()
            wnd = sm.GetService('window').GetWindow('assets')
            if wnd:
                wnd.sr.maintabs.ReloadVisible()

        finally:
            uthread.UnLock(self, 'ReloadBlueprints')




    def ReloadInstallations(self):
        wnd = sm.GetService('window').GetWindow('manufacturing')
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
            return self.activitiesIdx[activityID]
        else:
            return mls.UI_RMR_UNKNOWNACTIVITYID % {'id': activityID}



    def GetStateName(self, stateID):
        if stateID in self.statesIdx:
            return self.statesIdx[stateID]
        else:
            return 'Unknown %s' % stateID



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
        label = '%s - %s - %s' % (location.name, uix.Plural(station.blueprintCount, 'UI_RMR_NUM_BLUEPRINT') % {'num': station.blueprintCount}, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
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
        jumpText = mls.UI_SHARED_NUM_JUMP % {'num': 1} if int(jumps) == 1 else mls.UI_SHARED_NUM_JUMPS % {'num': int(jumps)}
        label = '%s - %s' % (locationName, jumpText)
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
        itemText = mls.UI_SHARED_NUM_ITEMS % {'num': blueprintCount} if blueprintCount > 1 else mls.UI_SHARED_NUM_ITEM % {'num': blueprintCount}
        jumpText = mls.UI_SHARED_NUM_JUMP % {'num': 1} if int(jumps) == 1 else mls.UI_SHARED_NUM_JUMPS % {'num': int(jumps)}
        label = '%s - %s - %s' % (location.name, itemText, jumpText)
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
        items = eve.GetInventory(const.containerGlobal).ListStationBlueprintItems(locationID, data.location.locationID, data.isCorp)
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
            isCopy = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][blueprint.copy]
            ml = blueprint.materialLevel
            pl = blueprint.productivityLevel
            lprr = blueprint.licensedProductionRunsRemaining
            if lprr == -1:
                lprr = ''
            data.Set('sort_%s' % mls.UI_GENERIC_COPY, isCopy)
            data.Set('sort_%s' % mls.UI_RMR_ML, ml)
            data.Set('sort_%s' % mls.UI_RMR_PL, pl)
            data.Set('sort_%s' % mls.UI_GENERIC_RUNS, lprr)
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
        jumpText = mls.UI_SHARED_NUM_JUMP % {'num': 1} if int(jumps) == 1 else mls.UI_SHARED_NUM_JUMPS % {'num': int(jumps)}
        label = '%s - %s' % (location.name, jumpText)
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
        itemText = mls.UI_SHARED_NUM_ITEMS % {'num': station.blueprintCount} if blueprintCount > 1 else mls.UI_SHARED_NUM_ITEM % {'num': station.blueprintCount}
        jumpText = mls.UI_SHARED_NUM_JUMP % {'num': 1} if int(jumps) == 1 else mls.UI_SHARED_NUM_JUMPS % {'num': int(jumps)}
        label = '%s - %s - %s' % (location.name, itemText, jumpText)
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
        items = eve.GetInventory(const.containerGlobal).ListStationItems(locationID)
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

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.SetCaption(mls.UI_RMR_SCIENCEANDINDUSTRY)
        self.LoadTabs()
        self.SetWndIcon('ui_57_64_9', mainTop=-10)
        self.SetMinSize([635, 500])
        capt = uicls.WndCaptionLabel(text=mls.UI_RMR_SCIENCEANDINDUSTRY, parent=self.sr.topParent, align=uiconst.TOPLEFT, left=70, top=10)
        self.sr.caption = capt



    def OnClose_(self, *args):
        if not self.destroyed:
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
        tabs = uicls.TabGroup(name='factoryTabs', parent=self.sr.main, idx=0)
        tabContent = []
        tabContent.append([mls.UI_RMR_JOBS,
         self.sr.jobsParent,
         self,
         'jobs'])
        tabContent.append([mls.UI_RMR_BLUEPRINTS,
         self.sr.persBlueprintsParent,
         self,
         'persBlueprints'])
        if not util.IsNPC(eve.session.corpid) and self.CanSeeCorpBlueprints():
            tabContent.append([mls.UI_RMR_CORPBLUEPRINTS,
             self.sr.corpBlueprintsParent,
             self,
             'sciAndIndustryCorpBlueprintsTab'])
        tabContent.append([mls.UI_RMR_INSTALLATIONS,
         self.sr.installationsParent,
         self,
         'installations'])
        tabContent.append([mls.UI_GENERIC_PLANETS,
         self.sr.planetParent,
         self,
         'planets'])
        tabContent.append([mls.UI_GENERIC_SETTINGS,
         self.sr.settingsParent,
         self,
         'settings'])
        tabs.Startup(tabContent, 'factoryTabs', UIIDPrefix='scienceAndIndustryTab')
        self.sr.maintabs = tabs



    def Load(self, key):
        self.sr.detailtimer = None
        self.sr.limits = self.GetSkillLimits()
        if key == 'jobs':
            self.ShowJobs()
        elif key == 'persBlueprints':
            self.ShowBlueprints()
        elif key == 'sciAndIndustryCorpBlueprintsTab':
            self.ShowBlueprints(1)
        elif key == 'installations':
            self.sr.caption.SetSubcaption(mls.UI_CORP_DELAYED5MINUTES)
            self.ShowInstallations()
        elif key == 'planets':
            self.ShowPlanets()
        elif key == 'settings':
            self.ShowSettings()
        if key != 'installations':
            self.sr.caption.SetSubcaption('')



    def ShowInstallations(self):
        if not getattr(self.sr.installationsParent, 'inited', 0):
            self.sr.installationsParent.Init()



    def ShowPlanets(self):
        if not getattr(self.sr.planetParent, 'inited', 0):
            self.sr.planetParent.Init()



    def Reload(self):
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
            copies = [(mls.UI_RMR_ALL, None), (mls.UI_RMR_COPIES, 1), (mls.UI_RMR_ORIGINALS, 0)]
            c = uicls.Combo(label=mls.UI_GENERIC_TYPE, parent=filters, options=copies, name='copies', select=settings.user.ui.Get('%s_blueprint_copyfilter' % key, None), callback=self.BlueprintComboChange, pos=(5, 0, 0, 0), align=uiconst.TOPLEFT)
            c.top = top = -c.sr.label.top
            filters.height = c.top + c.height
            setattr(self.sr, '%s_blueprintCopyFilter' % key, c)
            t = uicls.Label(text=mls.UI_CORP_DELAYED5MINUTES, parent=filters, align=uiconst.TOALL, left=c.width + 12, top=13, fontsize=11, letterspace=2, uppercase=0, autoheight=False, autowidth=False)
            t.hint = mls.UI_RMR_TEXT1
            if isCorp:
                divisions = sm.GetService('manufacturing').GetAvailableHangars(canView=0, canTake=0)
                divisions.insert(0, (mls.UI_RMR_ALL, (None, None)))
                c = uicls.Combo(label=mls.UI_RMR_DIVISION, parent=filters, options=divisions, name='divisions', select=settings.user.ui.Get('blueprint_divisionfilter', (None, None)), callback=self.BlueprintComboChange, pos=(self.sr.corp_blueprintCopyFilter.left + self.sr.corp_blueprintCopyFilter.width + 4,
                 top,
                 0,
                 0), align=uiconst.TOPLEFT)
                self.sr.blueprintDivisionFilter = c
                t.left += c.width + 4
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
            left = 3
            t = uicls.Label(text='%s<t><right>%s<br>%s<t><right>%s' % (mls.UI_RMR_MAXMANUFACTURINGJOBS,
             maxManufacturingJobCount,
             mls.UI_RMR_MAXRESEARCHJOBS,
             maxResearchJobCount), parent=par, left=left, top=0, tabs=[170, 220])
            uicls.Line(parent=par, align=uiconst.RELATIVE, width=1, height=64, left=220)
            collection.append(t)
            left = +220
            remoteAbilityList = []
            rmjLimit = self.sr.limits['remoteManufacturingJob']
            rrjLimit = self.sr.limits['remoteResearchJob']
            if rmjLimit == -1 and rrjLimit == -1:
                remoteAbilityList = [mls.UI_RMR_LIMITEDTOSTATIONS, mls.UI_RMR_LIMITEDTOSTATIONS]
            elif rmjLimit == -1:
                rmjText = mls.UI_RMR_LIMITEDTOSTATIONS
            elif rmjLimit == 0:
                rmjText = mls.UI_RMR_LIMITEDTOSOLARSYSTEMS
            elif rmjLimit == 50:
                rmjText = mls.UI_RMR_LIMITEDTOREGIONS
            else:
                rmjText = mls.UI_RMR_LIMITEDTOJUMPS % {'jumps': rmjLimit,
                 'jump': uix.Plural(rmjLimit, 'UI_GENERIC_JUMP')}
            if rrjLimit == -1:
                rrjText = mls.UI_RMR_LIMITEDTOSTATIONS
            elif rrjLimit == 0:
                rrjText = mls.UI_RMR_LIMITEDTOSOLARSYSTEMS
            elif rrjLimit == 50:
                rrjText = mls.UI_RMR_LIMITEDTOREGIONS
            else:
                rrjText = mls.UI_RMR_LIMITEDTOJUMPS % {'jumps': rrjLimit,
                 'jump': uix.Plural(rrjLimit, 'UI_GENERIC_JUMP')}
            remoteAbilityList = [rmjText, rrjText]
            t = uicls.Label(text='%s<t><right>%s<br>%s<t><right>%s' % (mls.UI_RMR_REMOTEMANUFACTURING,
             remoteAbilityList[0],
             mls.UI_RMR_REMOTERESEARCH,
             remoteAbilityList[1]), parent=par, left=left, top=0, tabs=[160, 328])
            collection.append(t)
            par.height = max(par.height, max([ each.textheight for each in collection ]) + 6)
        else:
            scroll = self.sr.Get('%sBlueprintsScroll' % key, None)
        defaultHeaders = uix.GetInvItemDefaultHeaders()
        headers = defaultHeaders[:4] + [mls.UI_GENERIC_COPY,
         mls.UI_RMR_ML,
         mls.UI_RMR_PL,
         mls.UI_GENERIC_RUNS]
        scroll.SetColumnsHiddenByDefault(defaultHeaders[4:])
        scrolllist = []
        accessScrollHint = ''
        sortlocations = sm.GetService('assets').GetAll('regitems', blueprintOnly=1, isCorp=isCorp)
        scrolllist = []
        if eve.session.solarsystemid is not None:
            dist = 0
            bp = sm.StartService('michelle').GetBallpark()
            if bp:
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
                        text = mls.UI_RMR_MAXRANGE % {'location': locationName,
                         'maxRange': util.FmtDist(const.maxCargoContainerTransferDistance)}
                        scrolllist.append(listentry.Get('Text', {'text': text}))
                    else:
                        blueprintCount = 0
                        inv = eve.GetInventoryFromId(ballID)
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
            accessScrollHint = [mls.UI_RMR_TEXT3, mls.UI_RMR_TEXT2][bool(isCorp)] % {'location': cfg.evelocations.Get(eve.session.regionid).name}
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
            details = uicls.Container(name='col2', align=uiconst.TOALL, parent=parent, pos=(const.defaultPadding,
             0,
             const.defaultPadding,
             0))
            uicls.Frame(parent=details, color=(1.0, 1.0, 1.0, 0.2), idx=0)
            uix.GetContainerHeader(mls.UI_RMR_SETTINGS_INPUTOUTPUT, details, 0)
            uicls.Container(name='push', align=uiconst.TOLEFT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TORIGHT, width=6, parent=details)
            uicls.Container(name='push', align=uiconst.TOTOP, height=6, parent=details)
            for (height, label, configname, retval, checked, groupname,) in [(12,
              mls.UI_RMR_SETTINGSBYBLUEPRINTLOCATION,
              'manufacturingfiltersetting1',
              0,
              settings.user.ui.Get('manufacturingfiltersetting1', 0) == 0,
              'manufacturingfiltersetting1'), (12,
              mls.UI_RMR_SETTINGSBYUSERDEFINITION,
              'manufacturingfiltersetting1',
              1,
              settings.user.ui.Get('manufacturingfiltersetting1', 0) == 1,
              'manufacturingfiltersetting1')]:
                cb = uicls.Checkbox(text=label, parent=details, configName=configname, retval=retval, checked=checked, groupname=groupname, callback=self.ChangeFilter)
                cb.hint = label

            uicls.Container(name='push', align=uiconst.TOTOP, height=8, parent=details)
            uix.GetContainerHeader(mls.UI_GENERIC_FILTERINGOPTIONS, details, xmargin=-6)
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
            uicls.Line(parent=filters, align=uiconst.TOTOP, top=15, color=(0.0, 0.0, 0.0, 0.25))
            uicls.Line(parent=filters, align=uiconst.TOTOP)
            self.sr.filters = filters
            uicls.Label(text=mls.UI_GENERIC_FILTERINGOPTIONS, parent=filters, left=8, top=3, fontsize=9, letterspace=2, uppercase=1)
            a = uicls.Label(text='', parent=filters, left=18, top=3, fontsize=9, letterspace=2, uppercase=1, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
            a.OnClick = self.ToggleAdvancedFilters
            a.GetMenu = None
            self.sr.ml = a
            expander = uicls.Sprite(parent=filters, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderUp.png', align=uiconst.TOPRIGHT)
            expander.OnClick = self.ToggleAdvancedFilters
            self.sr.jobsAdvanceExp = expander
            self.sr.activities = [ (text, actID) for (actID, text,) in sm.GetService('manufacturing').GetActivities() ]
            c = uicls.Combo(label=mls.UI_RMR_ACTIVITY, parent=filters, options=self.sr.activities, name='activity', select=settings.user.ui.Get('factory_activityfilter', None), callback=self.ComboChange, pos=(5, 1, 0, 0), width=114, align=uiconst.TOPLEFT)
            self.sr.activityFilter = c
            c.top = top = -c.sr.label.top + 4 + 15
            self.sr.states = [ (text, actID) for (actID, text,) in sm.GetService('manufacturing').GetStates() ]
            c = uicls.Combo(label=mls.UI_GENERIC_STATE, parent=filters, options=self.sr.states, name='state', select=settings.user.ui.Get('factory_statefilter', None), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.stateFilter = c
            self.sr.ranges = [ (text, locationData) for (locationData, text,) in sm.GetService('manufacturing').GetRanges(True) ]
            c = uicls.Combo(label=mls.UI_GENERIC_RANGE, parent=filters, options=self.sr.ranges, name='location', select=settings.user.ui.Get('factory_locationfilter', (eve.session.regionid, const.groupRegion)), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.locationFilter = c
            opts = [(mls.UI_GENERIC_ME, eve.session.charid)]
            if self.CanSeeCorpJobs():
                opts.append((mls.UI_GENERIC_MYCORPORATION, eve.session.corpid))
            self.sr.owners = opts
            c = uicls.Combo(label=mls.UI_GENERIC_OWNER, parent=filters, options=self.sr.owners, name='owner', select=settings.user.ui.Get('factory_ownerfilter', None), callback=self.ComboChange, pos=(c.left + c.width + 4,
             top,
             0,
             0), width=114, align=uiconst.TOPLEFT)
            self.sr.ownerFilter = c
            self.inadvHeight = c.top + c.height
            rowTop = -c.sr.label.top + c.top + c.height + 6
            self.sr.creators = [(mls.UI_GENERIC_ANY, None), (mls.UI_GENERIC_ME, eve.session.charid)]
            c = uicls.Combo(label=mls.UI_GENERIC_CREATOR, parent=filters, options=self.sr.creators, name='creator', select=settings.user.ui.Get('factory_creatorfilter', None), callback=self.ComboChange, pos=(5,
             rowTop,
             0,
             0), align=uiconst.TOPLEFT)
            self.sr.creatorFilter = c
            fromDate = uicls.SinglelineEdit(name=mls.UI_GENERIC_FROMDATE, parent=filters, setvalue=settings.user.ui.Get('factory_fromdatefilter', self.GetOffsetTime(-DAY)), align=uiconst.TOPLEFT, pos=(c.left + c.width + 4,
             rowTop,
             86,
             0), maxLength=16, label=mls.UI_GENERIC_FROMDATE)
            self.sr.jobsFromDate = fromDate
            toDate = uicls.SinglelineEdit(name=mls.UI_GENERIC_TODATE, parent=filters, setvalue=self.GetNow(), align=uiconst.TOPLEFT, pos=(fromDate.left + fromDate.width + 4,
             rowTop,
             86,
             0), maxLength=16, label=mls.UI_GENERIC_TODATE)
            self.sr.jobsToDate = toDate
            self.advHeight = toDate.top + toDate.height
            submit = uicls.Button(parent=filters, label=mls.UI_CMD_GETJOBS, func=self.LoadJobs, pos=(6, 2, 0, 0), btn_default=1, align=uiconst.BOTTOMRIGHT)
            self.sr.jobsScroll = uicls.Scroll(parent=self.sr.jobsParent, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.jobsScroll.sr.id = 'jobsScroll'
            self.sr.jobsScroll.multiSelect = 1
            self.sr.jobsScroll.ShowHint(mls.UI_RMR_TEXT4)
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
        self.sr.ml.text = [mls.UI_RMR_SHOWMOREOPTIONS, mls.UI_RMR_SHOWLESSOPTIONS][advanced]
        self.sr.creatorFilter.state = self.sr.jobsToDate.state = self.sr.jobsFromDate.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][advanced]



    def LoadJobs(self, *args):
        self.ShowLoad()
        self.sr.jobsScroll.ShowHint(mls.UI_RMR_FETCHINGDATA)
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
            self.sr.jobsScroll.ShowHint(mls.UI_RMR_FAILEDTOGETDATA)
            self.sr.jobsScroll.Load(contentList=[])
            self.HideLoad()
            return 
        scrolllist = []
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
                    label = '%s<t>%s<t>%s<t>%d<t>%s<t>%s<t>%s<t>%s' % (sm.GetService('manufacturing').GetActivityName(j.activityID),
                     cfg.invtypes.Get(j.installedItemTypeID).name,
                     self.GetJobLocationName(j.containerID, j.containerTypeID, j.containerLocationID),
                     jumps,
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
                    data.Set('sort_%s' % mls.UI_GENERIC_JUMPS, jumps)
                    data.Set('sort_%s' % mls.UI_RMR_INSTALLDATE, j.installTime)
                    data.Set('sort_%s' % mls.UI_RMR_ENDDATE, j.endProductionTime)
                    scrolllist.append(listentry.Get('RMJobEntry', data=data))

        if not scrolllist:
            if activity or completed or owner or creator or location:
                self.sr.jobsScroll.ShowHint(mls.UI_RMR_TEXT5)
            else:
                self.sr.jobsScroll.ShowHint(mls.UI_RMR_TEXT6)
        else:
            self.sr.jobsScroll.ShowHint()
            self.sr.jobsScroll.OnSelectionChange = self.SelectJob
            self.sr.jobsScroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_STATE,
             mls.UI_RMR_ACTIVITY,
             mls.UI_GENERIC_TYPE,
             mls.UI_GENERIC_LOCATION,
             mls.UI_GENERIC_JUMPS,
             mls.UI_RMR_INSTALLER,
             mls.UI_GENERIC_OWNER,
             mls.UI_RMR_INSTALLDATE,
             mls.UI_RMR_ENDDATE])
        self.HideLoad()



    def GetJobLineMenu(self, entry):
        m = []
        if entry.sr.node.jobData:
            if eve.session.solarsystemid != entry.sr.node.jobData.installedInSolarSystemID:
                (itemID, typeID,) = (entry.sr.node.jobData.installedInSolarSystemID, entry.sr.node.jobData.containerTypeID)
            else:
                (itemID, typeID,) = (entry.sr.node.jobData.containerID, entry.sr.node.jobData.containerTypeID)
            m += [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (entry.sr.node.id, None))]
            m += [None]
            m += [(mls.UI_CMD_LOCATION, sm.GetService('menu').CelestialMenu(itemID=itemID, mapItem=None, typeID=typeID))]
            m += [None]
            (itemID, typeID,) = (entry.sr.node.jobData.installedItemID, entry.sr.node.jobData.installedItemTypeID)
            m += [(mls.UI_GENERIC_BLUEPRINT, sm.GetService('menu').GetMenuFormItemIDTypeID(itemID, typeID))]
            m += [None]
            installerID = entry.sr.node.jobData.installerID
            ownerID = entry.sr.node.jobData.installedItemOwnerID
            menuCharacters = [(installerID, cfg.eveowners.Get(installerID).name, mls.UI_RMR_INSTALLER), (ownerID, cfg.eveowners.Get(ownerID).name, mls.UI_GENERIC_OWNER)]
            for characterData in menuCharacters:
                tmp = '%s (%s)' % (characterData[1], characterData[2])
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
        now = blue.os.GetTime()
        self.sr.stateText = ''
        self.sr.stateID = None
        if now >= jobdata.endProductionTime:
            if jobdata.completed == 1:
                self.sr.stateText = cfg.ramcompletedstatuses.Get(jobdata.completedStatus).completedStatusName
                self.sr.stateID = const.ramJobStatusDelivered
            if jobdata.completed == 0:
                if jobdata.pauseProductionTime is not None:
                    if util.IsStation(jobdata.containerID):
                        self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_GENERIC_INCAPACITATED
                    else:
                        self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_GENERIC_OFFLINE
                    self.sr.stateID = const.ramJobStatusPending
                else:
                    self.sr.stateText = '<color=0xff00FF00>%s<color=0xffffffff>' % mls.UI_RMR_READY
                    self.sr.stateID = const.ramJobStatusReady
        elif now < jobdata.beginProductionTime:
            self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_RMR_PENDING
            self.sr.stateID = const.ramJobStatusPending
        if now >= jobdata.beginProductionTime and now < jobdata.endProductionTime:
            self.sr.stateText = '<color=0xFFFFFF00>%s<color=0xffffffff>' % mls.UI_RMR_INPROGRESS
            self.sr.stateID = const.ramJobStatusInProgress
        if jobdata.pauseProductionTime is not None:
            if util.IsStation(jobdata.containerID):
                self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_GENERIC_INCAPACITATED
            else:
                self.sr.stateText = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_GENERIC_OFFLINE
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
        t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_ACTIVITY, sm.GetService('manufacturing').GetActivityName(jobdata.activityID)), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col1, col2])
        t = uicls.Label(text='%s<t><right>%s' % (mls.UI_GENERIC_STATE, stateText), parent=self.sr.details, left=left, top=12, singleline=0, tabs=[col1, col2])
        t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_OUTPUTLOCATION, self.GetJobLocationName(jobdata.containerID, jobdata.containerTypeID, jobdata.containerLocationID)), parent=self.sr.details, left=left, top=36, singleline=1, tabs=[col1, col2])
        outputType = cfg.invtypes.Get(jobdata.outputTypeID)
        if jobdata.activityID != const.ramActivityReverseEngineering:
            text = ''
            runs = 1
            if not outputType.categoryID == const.categoryBlueprint:
                runs = jobdata.runs
            amount = runs * outputType.portionSize
            if amount == 1:
                text = mls.UI_RMR_UNITOFTYPE % {'type': outputType.name}
            else:
                text = mls.UI_RMR_UNITSOFTYPE % {'num': amount,
                 'type': outputType.name}
            t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_OUTPUTTYPE, text), parent=self.sr.details, left=left, top=48, singleline=1, tabs=[col1, col2])
            left = +col2
            col3 = 100
            col4 = 160
            if jobdata.activityID == const.ramActivityResearchingTimeProductivity:
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_INSTALLPE, jobdata.installedItemProductivityLevel), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, col4])
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_ENDPE, jobdata.installedItemProductivityLevel + jobdata.runs), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
            if jobdata.activityID == const.ramActivityResearchingMaterialProductivity:
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_INSTALLME, jobdata.installedItemMaterialLevel), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, col4])
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_ENDME, jobdata.installedItemMaterialLevel + jobdata.runs), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
            if jobdata.activityID == const.ramActivityCopying:
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_COPIES, jobdata.runs), parent=self.sr.details, left=left, top=0, singleline=1, tabs=[col3, 160])
                t = uicls.Label(text='%s<t><right>%s' % (mls.UI_RMR_PRODUCTIONRUNS, jobdata.licensedProductionRuns), parent=self.sr.details, left=left, top=12, singleline=1, tabs=[col3, col4])
        self.sr.detailtext = uicls.Label(text='', parent=self.sr.details, left=3, top=24, singleline=1, tabs=[130, col2])
        uicls.Line(parent=self.sr.details, align=uiconst.RELATIVE, width=1, height=64, left=col2)
        showDeliverButton = False
        sel = self.sr.jobsScroll.GetSelected()
        for entry in sel:
            if blue.os.GetTime() > entry.jobData.endProductionTime and not entry.jobData.completed and not entry.jobData.pauseProductionTime:
                showDeliverButton = True
                break

        if showDeliverButton:
            submit = uicls.Button(parent=self.sr.details, label=mls.UI_RMR_DELIVER, func=self.Deliver, pos=(12, 10, 0, 0), align=uiconst.BOTTOMRIGHT)
        elif stateID != const.ramJobStatusDelivered:
            submit = uicls.Button(parent=self.sr.details, label=mls.UI_CMD_CANCELJOB, func=self.CancelJob, pos=(12, 10, 0, 0), align=uiconst.BOTTOMRIGHT)
        self.UpdateDetails(0)
        if stateID in (const.ramJobStatusInProgress, const.ramJobStatusPending) and not jobdata.pauseProductionTime:
            self.sr.detailtimer = base.AutoTimer(1000, self.UpdateDetails)



    def Deliver(self, *args):
        if getattr(self, 'delivering', 0):
            return 
        if not eve.session.shipid:
            raise UserError('CantDoThatNoShip')
        self.delivering = 1
        self.sr.activeDetails = None
        try:
            sel = self.sr.jobsScroll.GetSelected()
            sm.GetService('loading').ProgressWnd(mls.UI_RMR_COMPLETINGJOBS, mls.UI_RMR_COMPLETINGINSTALLATION, 1, 2)
            blue.pyos.synchro.Sleep(1000)
            for entry in sel:
                if self.GetStateTextOrID(entry.jobData)[1] == const.ramJobStatusReady:
                    sm.GetService('manufacturing').CompleteJob(entry.jobData)

            if len(sel) > 0:
                sm.GetService('objectCaching').InvalidateCachedMethodCall('ramProxy', 'GetJobs2', sel[0].jobData.installedItemOwnerID, 0)
            sm.GetService('loading').ProgressWnd(mls.UI_RMR_COMPLETINGJOBS, mls.UI_GENERIC_DONE, 2, 2)

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
        if not eve.session.shipid:
            raise UserError('CantDoThatNoShip')
        self.cancelling = 1
        self.sr.activeDetails = None
        try:
            sel = self.sr.jobsScroll.GetSelected()
            blue.pyos.synchro.Sleep(1000)
            for entry in sel:
                cancel = self.GetStateTextOrID(entry.jobData)[1] != const.ramJobStatusReady
                if entry.jobData.pauseProductionTime is not None:
                    eve.Message('CantUseOfflineStructure', {'structure': (TYPEID, entry.jobData.containerTypeID)})
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
                endTime -= blue.os.GetTime()
                endTime = max(0, endTime)
            else:
                endTime -= pauseProductionTime
                endTime = max(0, endTime)
            detailtextvalue = ''
            if endTime <= 0:
                detailtextvalue = '<color=0xff00FF00>%s' % mls.UI_RMR_READY
                if self.sr.activeDetails.completed == 1:
                    detailtextvalue = mls.UI_RMR_DELIVERED
                if timerUpdate:
                    self.ShowJobDetails(self.sr.activeDetails)
                self.sr.detailtimer = None
            else:
                detailtextvalue = '<color=0xFFFFFF00>%s' % util.FmtDate(endTime)
            entry = self.GetJobEntry(self.sr.activeDetails.jobID)
            if entry:
                entry.label = '%s<t><color=0xFFFFFFFF>%s<' % (self.GetStateTextOrID(self.sr.activeDetails)[0], entry.labelNoStatus)
                if entry.panel:
                    entry.panel.Load(entry)
            self.sr.detailtext.text = '%s<t><right>%s' % (mls.UI_RMR_TTC, detailtextvalue)
        else:
            self.sr.detailtext = None
            self.sr.detailtimer = None
            uix.Flush(self.sr.details)



    def GetJobEntry(self, jobID):
        for entry in self.sr.jobsScroll.GetNodes():
            if entry.jobData.jobID == jobID:
                return entry




    def GetNow(self):
        return util.FmtDate(blue.os.GetTime(), 'sn')



    def GetOffsetTime(self, shift):
        (year, month, weekday, day, hour, minute, second, ms,) = blue.os.GetTimeParts(blue.os.GetTime() + shift)
        return '%s.%.2d.%.2d' % (year, month, day)




class RMJobEntry(listentry.Generic):
    __guid__ = 'listentry.RMJobEntry'

    def Load(self, node):
        listentry.Generic.Load(self, node)




class InstallationPanel(uicls.Container):
    __guid__ = 'xtriui.InstallationPanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.submitHeader = mls.UI_CMD_INSTALLJOB
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
        self.sr.activities = [ (text, actID) for (actID, text,) in sm.GetService('manufacturing').GetActivities() ]
        if activityID is None:
            activityID = settings.user.ui.Get('factory_installationsactivityfilter', const.ramActivityManufacturing)
        c = uicls.Combo(label=mls.UI_RMR_ACTIVITY, parent=self.sr.filters, options=self.sr.activities, name='activity', select=activityID, callback=self.InstallationsComboChange, pos=(1, 0, 0, 0), align=uiconst.TOPLEFT)
        c.top = top = -c.sr.label.top - 4
        self.sr.filters.height = c.top + c.height + 5
        self.sr.installationsActivityFilter = c
        locationtypes = [(mls.UI_GENERIC_STATIONS, (const.groupStation,)), (mls.UI_RMR_ASSEMBLYARRAYS, (const.groupAssemblyArray,)), (mls.UI_RMR_MOBILELABS, (const.groupMobileLaboratory,))]
        if session.shipid:
            locationtypes.insert(1, (mls.UI_GENERIC_MYSHIP, (const.groupCapitalIndustrialShip, const.groupFreighter)))
        locationtypes.sort()
        locationtypes.insert(0, (mls.UI_GENERIC_ANY, None))
        self.sr.locationtypes = locationtypes
        loc = (mls.UI_GENERIC_ANY, None)
        if not stationID:
            loc = settings.user.ui.Get('factory_installationslocationsfilter', (const.groupSolarSystem, eve.session.solarsystemid2))
        c = uicls.Combo(label=mls.UI_GENERIC_LOCATION, parent=self.sr.filters, options=self.sr.locationtypes, name='location', select=loc, callback=self.InstallationsComboChange, pos=(self.sr.installationsActivityFilter.left + self.sr.installationsActivityFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsLocationsFilter = c
        self.sr.ranges = [ (text, locationData) for (locationData, text,) in sm.GetService('manufacturing').GetRanges() ]
        self.blueprintLocationID = stationID
        if stationID:
            self.sr.ranges.insert(0, (mls.UI_RMR_CURRBLUEPRINTLOCATION, (stationID, LOCATION_BLUEPRINT)))
            rng = (stationID, LOCATION_BLUEPRINT)
        else:
            rng = settings.user.ui.Get('factory_installationsrangesfilter', (const.groupRegion, eve.session.regionid))
        c = uicls.Combo(label=mls.UI_GENERIC_RANGE, parent=self.sr.filters, options=self.sr.ranges, name='range', select=rng, callback=self.InstallationsComboChange, pos=(self.sr.installationsLocationsFilter.left + self.sr.installationsLocationsFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsRangesFilter = c
        self.sr.assemblytypeflag = [(mls.UI_GENERIC_PUBLIC, (const.groupRegion, 'region', None)), (mls.UI_GENERIC_PERSONAL, (const.groupCharacter, 'char', eve.session.charid))]
        if not util.IsNPC(eve.session.corpid):
            self.sr.assemblytypeflag += [(mls.UI_GENERIC_CORPORATION, (const.groupCorporation, 'corp', eve.session.corpid))]
        if eve.session.allianceid is not None:
            self.sr.assemblytypeflag += [(mls.UI_GENERIC_ALLIANCE, (const.groupAlliance, 'alliance', eve.session.allianceid))]
        c = uicls.Combo(label=mls.UI_GENERIC_TYPE, parent=self.sr.filters, options=self.sr.assemblytypeflag, name='typeflag', select=settings.user.ui.Get('factory_installationstypeflagfilter', (const.groupRegion, 'region', None)), callback=self.InstallationsComboChange, pos=(self.sr.installationsRangesFilter.left + self.sr.installationsRangesFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        self.sr.installationsTypeFlagFilter = c
        catdefault = settings.user.ui.Get('factory_installationscatfilter', None)
        catfilters = sm.GetService('marketutils').GetFilterops(None)
        if catdefault not in [ v for (k, v,) in catfilters ]:
            catdefault = None
        self.sr.filterCategory = uicls.Combo(label=mls.UI_RMR_PRODCATEGORY, parent=self.sr.filters, options=sm.GetService('marketutils').GetFilterops(None), name='filterCateg', select=catdefault, callback=self.InstallationsComboChange, pos=(self.sr.installationsTypeFlagFilter.left + self.sr.installationsTypeFlagFilter.width + 4,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        groupdefault = settings.user.ui.Get('factory_installationsgroupfilter', None)
        if catdefault is None:
            ops = [(mls.UI_GENERIC_ALL, None)]
        else:
            ops = sm.GetService('marketutils').GetFilterops(catdefault)
        if groupdefault not in [ v for (k, v,) in ops ]:
            groupdefault = None
        self.sr.filterGroup = uicls.Combo(label=mls.UI_RMR_PRODGROUP, parent=self.sr.filters, options=ops, name='filterGroup', select=groupdefault, callback=self.InstallationsComboChange, pos=(self.sr.filterCategory.left + self.sr.filterCategory.width + 4,
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
        t = uicls.Label(text=mls.UI_GENERIC_FILTERINGOPTIONS, parent=filterCont, left=4, top=4, width=100, autowidth=False, align=uiconst.TOLEFT, idx=0)
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
                ops = [(mls.UI_GENERIC_ALL, None)]
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
            now = blue.os.GetTime()
            self.delaySelection = (now, selection)
            uthread.new(self.DelaySelection, now)
            break




    def DelaySelection(self, issueTime):
        blue.pyos.synchro.Sleep(250)
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
        self.sr.installationsScroll.ShowHint(mls.UI_RMR_FETCHINGINSTALLATIONS)
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
            self.sr.installationsScroll.ShowHint(mls.UI_RMR_TEXT7)
        if scrolllist:
            self.sr.assemblyLinesScroll.state = uiconst.UI_NORMAL
            self.sr.assemblyLinesScroll.ShowHint(mls.UI_RMR_TEXT8)
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
                self.sr.assemblyLinesScroll.ShowHint(mls.UI_RMR_TEXT10)
        t = uicls.Label(text='%s' % ('<b>%s</b>' % mls.UI_RMR_SELECTASSEMBLYLINEABOVE), parent=self.sr.installationDetails, left=10, top=30, singleline=1, tabs=[128, 170])
        if scrolllist:
            self.sr.toggleLinesButt = uicls.Button(parent=self.sr.installationDetails, label=mls.UI_RMR_TOGGLEFULLLIST, func=self.ToggleFullAssemblyLinesList, pos=(0,
             const.defaultPadding,
             0,
             0), align=uiconst.BOTTOMRIGHT)



    def ShowAssemblyLineDetails(self, entry):
        uix.Flush(self.sr.installationDetails)
        d = [(mls.UI_RMR_GOODSTANDINGDISCOUNT, 'discountPerGoodStandingPoint'),
         (mls.UI_RMR_BADSTANDINGSURCHARGE, 'surchargePerBadStandingPoint'),
         (mls.UI_RMR_MINSTANDING, 'minimumStanding'),
         (mls.UI_RMR_MINCHARACTERSECURITY, 'minimumCharSecurity'),
         (mls.UI_RMR_MAXCHARACTERSECURITY, 'maximumCharSecurity'),
         (mls.UI_RMR_MINCORPORATIONSECURITY, 'minimumCorpSecurity'),
         (mls.UI_RMR_MAXCORPORATIONSECURITY, 'maximumCorpSecurity')]
        i = 0
        left = 0
        top = 5
        col1 = 165
        col2 = 205
        for (header, key,) in d:
            if key not in entry.sr.node.assemblyLine.header:
                continue
            value = entry.sr.node.assemblyLine[key]
            t = uicls.Label(text='%s<t><right>%s' % (header, value), parent=self.sr.installationDetails, left=left, top=top, singleline=1, tabs=[col1, col2])
            t.hint = header
            i += 1
            if i == 4:
                left += col2
                uicls.Line(parent=self.sr.installationDetails, align=uiconst.RELATIVE, width=1, top=5, height=64, left=left)
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
            submit = uicls.Button(parent=self.sr.installationDetails, label=mls.UI_RMR_MANAGEASSEMBLYLINES, func=self.ManageAssemblyLines, pos=(0,
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
            m += [(mls.UI_CMD_INSTALLJOB, sm.GetService('manufacturing').CreateJob, (None,
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
            headers = [mls.UI_RMR_ACTIVITY,
             mls.UI_GENERIC_QTY,
             mls.UI_GENERIC_LOCATION,
             mls.UI_GENERIC_JUMPS,
             mls.UI_RMR_INSTALLATIONTYPE,
             mls.UI_GENERIC_OWNER]
            groupName = containerGroup.name
            data = util.KeyVal()
            data.label = '%s<t><right>%s<t>%s<t><right>%d<t>%s<t>%s' % (sm.GetService('manufacturing').GetActivityName(lineType.activityID),
             line.quantity,
             containerLocationName,
             jumps,
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
            data.Set('sort_%s' % mls.UI_GENERIC_QTY, line.quantity)
            data.Set('sort_%s' % mls.UI_GENERIC_JUMPS, jumps)
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
            v = '<br><b>%s:</b><br>' % mls.UI_RMR_PRODUCABLECATEGS
            v += ', '.join(validc)
            v += '<br><br>'
        if validg:
            v += '<b>%s:</b><br>' % mls.UI_RMR_PRODUCABLEGROUPS
            v += ', '.join(validg)
        self.producableStringCache[lineType.assemblyLineTypeID] = v
        return v



    def AssemblyLineRow(self, data):
        line = data.assemblyLine
        lineType = cfg.ramaltypes.Get(data.assemblyLine.assemblyLineTypeID)
        expirationTime = ''
        nft = data.Get('sort_%s' % mls.UI_RMR_NEXTFREETIME, 0)
        if nft <= 0:
            expirationTime = '<color=0xff00FF00><t>%s<color=0xffffffff>' % mls.UI_GENERIC_NOW
        else:
            expirationTime = '<color=0xFFFFFF00><t>%s<color=0xffffffff>' % util.FmtDate(nft)
        m = sm.GetService('manufacturing').GetRestrictionMasks()
        rmText = mls.UI_GENERIC_PUBLICLYAVAILABLE
        if line.restrictionMask:
            rmText = mls.RESTRICTED
        data.label = '%s<t>%s%s<t><right>%s<t><right>%s<t><right>%s<t><right>%s<t>%s' % (data.numLines,
         sm.GetService('manufacturing').GetActivityName(lineType.activityID),
         expirationTime,
         util.FmtISK(line.costInstall),
         util.FmtISK(line.costPerHour),
         lineType.baseTimeMultiplier,
         lineType.baseMaterialMultiplier,
         rmText)
        data.Set('sort_#', data.numLines)
        data.Set('sort_%s' % mls.UI_RMR_INSTALLCOST, line.costInstall)
        data.Set('sort_%s' % mls.UI_RMR_COSTPERHOUR, line.costPerHour)
        data.Set('sort_%s' % mls.UI_RMR_TIMEMULTIPLIER, lineType.baseTimeMultiplier)
        data.Set('sort_%s' % mls.UI_RMR_MATERIALMULTIPLIER, lineType.baseMaterialMultiplier)
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
            expirationTime -= blue.os.GetTime()
            expirationTimeSort = int(expirationTime / MIN) * MIN
            data = util.KeyVal()
            data.confirmOnDblClick = 1
            data.Set('sort_%s' % mls.UI_RMR_NEXTFREETIME, expirationTimeSort)
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
                        if expirationTimeSort < r.Get('sort_%s' % mls.UI_RMR_NEXTFREETIME, 0):
                            r.Set('sort_%s' % mls.UI_RMR_NEXTFREETIME, expirationTimeSort)
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

        tmpHeaders = ['#',
         mls.UI_RMR_ACTIVITY,
         mls.UI_RMR_NEXTFREETIME,
         mls.UI_RMR_INSTALLCOST,
         mls.UI_RMR_COSTPERHOUR,
         mls.UI_RMR_TIMEMULTIPLIER,
         mls.UI_RMR_MATERIALMULTIPLIER,
         mls.AGT_LOCATECHARACTER_GETINFOSVCDETAILS_AVAILABILITY]
        headers = []
        for header in tmpHeaders:
            headers.append(header.replace(' ', '<br>'))

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
        d = [(mls.UI_RMR_INSTALLCOST,
          'costInstall',
          0.0,
          None,
          entry.costInstall),
         (mls.UI_RMR_COSTPERHOUR,
          'costPerHour',
          0.0,
          None,
          entry.costPerHour),
         (mls.UI_RMR_GOODSTANDINGDISCOUNT,
          'discountPerGoodStandingPoint',
          0.0,
          10.0,
          entry.discountPerGoodStandingPoint),
         (mls.UI_RMR_BADSTANDINGSURCHARGE,
          'surchargePerBadStandingPoint',
          0.0,
          10.0,
          entry.surchargePerBadStandingPoint),
         (mls.UI_RMR_MINSTANDING,
          'minimumStanding',
          -10.0,
          10.0,
          entry.minimumStanding),
         (mls.UI_RMR_MINCHARACTERSECURITY,
          'minimumCharSecurity',
          -10.0,
          10.0,
          entry.minimumCharSecurity),
         (mls.UI_RMR_MAXCHARACTERSECURITY,
          'maximumCharSecurity',
          -10.0,
          10.0,
          entry.maximumCharSecurity),
         (mls.UI_RMR_MINCORPORATIONSECURITY,
          'minimumCorpSecurity',
          -10.0,
          10.0,
          entry.minimumCorpSecurity),
         (mls.UI_RMR_MAXCORPORATIONSECURITY,
          'maximumCorpSecurity',
          -10.0,
          10.0,
          entry.maximumCorpSecurity)]
        format = []
        format.append({'type': 'header',
         'text': mls.UI_RMR_PARAMETERS,
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
        format.append({'type': 'header',
         'text': mls.UI_RMR_RESTRICTIONMASKS,
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
        retval = uix.HybridWnd(format, mls.UI_RMR_UPDATEASSEMBLYLINESETTINGS, 1, buttons=uiconst.OKCANCEL, minW=340, minH=100, icon='ui_57_64_9', unresizeAble=1)
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

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        activityID = attributes.activityID
        if activityID is None:
            self.sr.activityID = 0
        else:
            self.sr.activityID = activityID
        bottom = uicls.Container(name='bottom', parent=self.sr.maincontainer, align=uiconst.TOBOTTOM, height=24, idx=0)
        self.scope = 'all'
        self.SetCaption(mls.UI_RMR_SCIENCEANDINDUSTRY)
        self.SetMinSize([410, 240])
        self.NoSeeThrough()
        self.DefineButtons(uiconst.OKCANCEL, cancelFunc=self.SelfDestruct, okFunc=self.Confirm)
        self.MakeUnResizeable()
        self.SetInstallationWindowCaption(self.sr.activityID)



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
            self.CloseX()
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
        installationText = uicls.Label(text=mls.UI_RMR_INSTALLATION, parent=instPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        if activityID is not None and activityID == const.ramActivityReverseEngineering:
            blueprintText = uicls.Label(text=mls.UI_GENERIC_ANCIENTRELIC, parent=bpPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        else:
            blueprintText = uicls.Label(text=mls.UI_GENERIC_BLUEPRINT, parent=bpPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        inputOutputText = uicls.Label(text=mls.UI_RMR_INPUTOUTPUT, parent=inputPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        self.sr.runsText = uicls.Label(text='', parent=runsPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        licencedRunsText = uicls.Label(text=mls.UI_RMR_LICENCEDRUNS, parent=copyRunsPar, left=8, top=1, width=80, autowidth=False, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        baseItemText = uicls.Label(text=mls.UI_RMR_BASE_ITEM, parent=inventionItemPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        decryptorText = uicls.Label(text=mls.UI_RMR_DECRYPTOR, parent=inventionDecryptorPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        outputTypeText = uicls.Label(text=mls.UI_RMR_OUTPUTTYPE, parent=inventionOutputPar, left=8, top=1, uppercase=1, fontsize=9, letterspace=2, align=uiconst.CENTERLEFT)
        left = max(installationText.textwidth, blueprintText.textwidth, inputOutputText.textwidth, self.sr.runsText.textwidth, licencedRunsText.textwidth, baseItemText.textwidth, decryptorText.textwidth, outputTypeText.textwidth) + 15
        longestText = mls.UI_CMD_PICKINSTALLATION
        if activityID == const.ramActivityReverseEngineering:
            for each in [mls.UI_CMD_CHANGEINSTALLATION, mls.UI_CMD_PICKANCIENTRELIC, mls.UI_CMD_CHANGEANCIENTRELIC]:
                if len(longestText) < len(each):
                    longestText = each

        else:
            for each in [mls.UI_CMD_CHANGEINSTALLATION, mls.UI_CMD_PICKBLUEPRINT, mls.UI_CMD_CHANGEBLUEPRINT]:
                if len(longestText) < len(each):
                    longestText = each

        instButtonPar = uicls.Container(name='instButtonPar', parent=instPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
        self.sr.pickInstallationBtn = uicls.Button(parent=instButtonPar, label=longestText, align=uiconst.TOPLEFT, func=self.PickInstallation, args=(activityID,), pos=(const.defaultPadding,
         2,
         0,
         0))
        if activityID == const.ramActivityReverseEngineering:
            bpButtonPar = uicls.Container(name='bpButtonPar', parent=bpPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
            self.sr.pickBlueprintBtn = uicls.Button(parent=bpButtonPar, label=mls.UI_CMD_PICKANCIENTRELIC, func=self.PickAncientRelic, pos=(const.defaultPadding,
             2,
             0,
             0))
        else:
            bpButtonPar = uicls.Container(name='bpButtonPar', parent=bpPar, align=uiconst.TORIGHT, height=22, state=uiconst.UI_PICKCHILDREN)
            self.sr.pickBlueprintBtn = uicls.Button(parent=bpButtonPar, label=mls.UI_CMD_PICKBLUEPRINT, func=self.PickBlueprint, pos=(const.defaultPadding,
             2,
             0,
             0))
        self.sr.pickInstallationBtn.setWidth = self.sr.pickBlueprintBtn.setWidth = self.sr.pickInstallationBtn.width
        instButtonPar.width = bpButtonPar.width = self.sr.pickInstallationBtn.setWidth + 8
        self.sr.pickInstallationBtn.SetLabel(mls.UI_CMD_PICKINSTALLATION)
        editWith = self.width - instButtonPar.width - left
        self.sr.installationEdit = uicls.SinglelineEdit(name='installationEdit', parent=instPar, setvalue=mls.UI_GENERIC_PICKONE, align=uiconst.TOPLEFT, pos=(left,
         2,
         editWith,
         0))
        self.sr.installationEdit.readonly = 1
        if installationDetails:
            self.sr.installationDetails = installationDetails
        else:
            self.sr.installationDetails = None
        if assemblyLine:
            lineType = cfg.ramaltypes.Get(assemblyLine.assemblyLineTypeID)
            installationName = cfg.evelocations.Get(installationDetails.containerID).name
            if not installationName:
                installationName = cfg.invtypes.Get(installationDetails.containerTypeID).name
            self.sr.installationEdit.SetValue(installationName)
            self.sr.assemblyLine = assemblyLine
            self.sr.pickInstallationBtn.SetLabel(mls.UI_CMD_CHANGEINSTALLATION)
        else:
            self.sr.assemblyLine = None
        self.isMine = 1
        self.sr.bluePrint = None
        if invItem and invItem.categoryID in (const.categoryBlueprint, const.categoryAncientRelic):
            self.sr.bluePrint = copy.deepcopy(invItem)
            self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
        self.sr.bpEdit = uicls.SinglelineEdit(name='bpEdit', parent=bpPar, setvalue=mls.UI_GENERIC_PICKONE, align=uiconst.TOPLEFT, pos=(left,
         2,
         editWith,
         0))
        self.sr.bpEdit.readonly = 1
        if self.sr.bluePrint:
            self.sr.bpEdit.SetValue(cfg.invtypes.Get(self.sr.bluePrint.typeID).name)
            if activityID is not None and activityID == const.ramActivityReverseEngineering:
                self.sr.pickBlueprintBtn.SetLabel(mls.UI_CMD_CHANGEANCIENTRELIC)
            else:
                self.sr.pickBlueprintBtn.SetLabel(mls.UI_CMD_CHANGEBLUEPRINT)
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
        options = [(mls.UI_RMR_SELECTBASEITEM_NOTFOUND, 0)]
        self.sr.inventionBaseItemCombo = uicls.Combo(label='', parent=inventionItemPar, options=options, name='rmInventionItemCombo', select=0, callback=self.OnComboChange, pos=(left,
         2,
         0,
         0), width=editWith, align=uiconst.TOPLEFT)
        options = [(mls.UI_RMR_SELECTDECRYPTOR_NOTFOUND, 0)]
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
                containerIptOps = containerOptOps = [(mls.UI_GENERIC_MYCARGO, (eve.session.charid, const.flagCargo))]
                for inputOption in sm.GetService('manufacturing').GetAvailableHangars(canView=0, locationID=locationID):
                    containerIptOps.append(inputOption)

            else:
                containerIptOps = containerOptOps = [(mls.UI_GENERIC_MYHANGAR, (eve.session.charid, const.flagHangar))]
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
            self.sr.runsText.text = mls.UI_RMR_COPIES
            self.sr.copyRunsPar.state = uiconst.UI_NORMAL
        else:
            self.sr.runsText.text = mls.UI_GENERIC_RUNS
            self.sr.copyRunsPar.state = uiconst.UI_HIDDEN
        if activityID == const.activityResearchingMaterialProductivity:
            self.sr.runsText.text = mls.UI_RMR_MLLEVELS
            self.sr.runsText.hint = mls.UI_INFOWND_MATERIALLEVEL
        elif activityID == const.activityResearchingTimeProductivity:
            self.sr.runsText.text = mls.UI_RMR_PLLEVELS
            self.sr.runsText.hint = mls.UI_INFOWND_PRODUCTIVITYEVEL
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
            wnd = sm.GetService('window').GetWindow('pickinstallation', create=1, decoClass=form.PickInstallationWindow, activityID=activityID, stationID=stationID)
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
                self.sr.pickInstallationBtn.SetLabel(mls.UI_CMD_CHANGEINSTALLATION)
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
            wnd = sm.GetService('window').GetWindow('pickblueprint', create=1, decoClass=form.PickBlueprintWindow, assemblyLine=self.sr.assemblyLine, installationDetails=self.sr.installationDetails)
            if wnd.ShowModal() == uiconst.ID_OK and wnd.result is not None:
                invItem = wnd.result
                self.sr.bpEdit.SetValue(cfg.invtypes.Get(invItem.typeID).name)
                self.sr.bluePrint = copy.deepcopy(invItem)
                self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
                self.GetRunsTextAndState(self.sr.installationDetails.activityID)
                self.blueprintMPLrange = (1, cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit)
                self.sr.pickBlueprintBtn.SetLabel(mls.UI_CMD_CHANGEBLUEPRINT)
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
            wnd = sm.GetService('window').GetWindow('pickblueprint', create=1, decoClass=form.PickBlueprintWindow, assemblyLine=self.sr.assemblyLine, installationDetails=self.sr.installationDetails)
            if wnd.ShowModal() == uiconst.ID_OK and wnd.result is not None:
                invItem = wnd.result
                self.sr.bpEdit.SetValue(cfg.invtypes.Get(invItem.typeID).name)
                self.sr.bluePrint = copy.deepcopy(invItem)
                self.isMine = self.sr.bluePrint.ownerID != eve.session.corpid
                self.GetRunsTextAndState(self.sr.installationDetails.activityID)
                self.blueprintMPLrange = (1, cfg.invbptypes.Get(self.sr.bluePrint.typeID).maxProductionLimit)
                self.sr.pickBlueprintBtn.SetLabel(mls.UI_CMD_CHANGEANCIENTRELIC)
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
                items = eve.GetInventoryFromId(officeID).List()
            else:
                which = {False: 'offices',
                 True: 'property'}[(not util.IsStation(stationID))]
                items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, stationID, which)
        else:
            eve.GetInventory(const.containerGlobal).InvalidateStationItemsCache(stationID)
            items = eve.GetInventory(const.containerGlobal).ListStationItems(stationID)
        compatibleItemTypes = []
        if activityID is not None and activityID == const.ramActivityReverseEngineering:
            races = {}
            for r in sm.services['cc'].GetData('races'):
                races[r.raceID] = r.raceName

            for item in items:
                if item.typeID in types and item.flagID == flag:
                    type = cfg.invtypes.Get(item.typeID)
                    if type.raceID is not None:
                        name = type.typeName + ' (%s)' % races.get(type.raceID, 1)
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
        itemOptions = [(mls.UI_RMR_SELECTBASEITEM, 0)]
        outputTypes = []
        (ownerInput, flagInput,) = self.sr.inputCombo.GetValue()
        if details.activityID == const.ramActivityInvention:
            types = self.GetInventionBaseItemTypes(self.sr.bluePrint)
            itemOptions = self.GetCompatibleInventionListFromHangar(details.containerID, flagInput, types, not self.isMine)
            if len(itemOptions) == 0:
                itemOptions.insert(0, (mls.UI_RMR_SELECTBASEITEM_NOTFOUND, 0))
            else:
                itemOptions.insert(0, (mls.UI_RMR_SELECTBASEITEM, 0))
        types = self.GetInventionDecryptorTypes(self.sr.bluePrint)
        decryptorOptions = self.GetCompatibleInventionListFromHangar(details.containerID, flagInput, types, not self.isMine, activityID=details.activityID)
        if len(decryptorOptions) == 0:
            decryptorOptions.insert(0, (mls.UI_RMR_SELECTDECRYPTOR_NOTFOUND, 0))
        elif details.activityID == const.ramActivityInvention:
            decryptorOptions.insert(0, (mls.UI_RMR_SELECTDECRYPTOR, 0))
        elif details.activityID == const.ramActivityReverseEngineering:
            decryptorOptions.insert(0, (mls.UI_RMR_SELECTDECRYPTORREQUIRED, 0))
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

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        activityID = attributes.activityID
        stationID = attributes.stationID
        self.scope = 'all'
        self.name = 'pickinstallation'
        self.SetCaption(mls.UI_RMR_SCIENCEANDINDUSTRYPICKINST)
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
        self.sr.installationPanel.submitHeader = mls.UI_CMD_USEASSEMBLYLINE
        self.sr.installationPanel.submitFunc = self.SubmitInstallation



    def SubmitInstallation(self, *args):
        sel = self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected()
        if len(sel):
            line = [ entry.listvalue for entry in sel ][0]
            v = line[0].nextFreeTime
            diff = v - blue.os.GetTime()
            if diff > 5 * MIN:
                if eve.Message('RamLineInUseConfirm', {'time': util.FmtDate(diff)}, uiconst.YESNO) != uiconst.ID_YES:
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
                return mls.UI_RMR_PICKONEINSTALLATION
            if not self.sr.installationPanel.sr.assemblyLinesScroll.GetSelected():
                return mls.UI_RMR_PICKONEASSEMBLYLINE
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})




class PickBlueprintWindow(form.ListWindow, BlueprintData):
    __guid__ = 'form.PickBlueprintWindow'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        assemblyLine = attributes.assemblyLine
        installationDetails = attributes.installationDetails
        self.assemblyLine = assemblyLine
        self.installationDetails = installationDetails
        self.scope = 'all'
        self.SetCaption(mls.UI_RMR_SCIENCEANDINDUSTRYPICKBP)
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
        tabContent = []
        tabContent.append([mls.UI_RMR_MYBLUEPRINTS,
         self.sr.persParent,
         self,
         'persPickBlueprints'])
        if not util.IsNPC(eve.session.corpid) and self.CanSeeCorpBlueprints():
            tabContent.append([mls.UI_RMR_CORPBLUEPRINTS,
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
            copies = [(mls.UI_RMR_ALL, None), (mls.UI_RMR_COPIES, 1), (mls.UI_RMR_ORIGINALS, 0)]
            c = uicls.Combo(label=mls.UI_GENERIC_TYPE, parent=filters, options=copies, name='copies', select=settings.user.ui.Get('blueprint_copyfilter', None), callback=self.BlueprintComboChange, pos=(7, 15, 0, 0), align=uiconst.TOPLEFT)
            setattr(self.sr, '%s_blueprintCopyFilter' % key, c)
            t = uicls.Label(text=mls.UI_CORP_DELAYED5MINUTES, parent=filters, left=c.width + c.left + 8, top=3, width=300, autowidth=False, fontsize=11, letterspace=2, uppercase=0)
            if isCorp:
                divisions = sm.GetService('manufacturing').GetAvailableHangars(canView=1, canTake=1)
                divisions.insert(0, (mls.UI_RMR_ALL, (None, None)))
                c = uicls.Combo(label=mls.UI_RMR_DIVISION, parent=filters, options=divisions, name='divisions', select=settings.user.ui.Get('blueprint_divisionfilter', (None, None)), callback=self.BlueprintComboChange, pos=(self.sr.corp_blueprintCopyFilter.left + self.sr.corp_blueprintCopyFilter.width + 4,
                 15,
                 0,
                 0), align=uiconst.TOPLEFT)
                self.sr.blueprintDivisionFilter = c
                t.left += c.width + 4
            scroll = uicls.Scroll(parent=parent, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            scroll.sr.id = '%sPickBlueprintsScroll' % key
            scroll.multiSelect = 0
            setattr(self.sr, '%sPickBlueprintsScroll' % key, scroll)
        scroll = self.sr.Get('%sPickBlueprintsScroll' % key, None)
        accessScrollHint = mls.UI_RMR_TEXT9 % {'location': cfg.evelocations.Get(eve.session.regionid).name}
        defaultHeaders = uix.GetInvItemDefaultHeaders()
        headers = defaultHeaders[:4] + [mls.UI_GENERIC_COPY,
         mls.UI_RMR_ML,
         mls.UI_RMR_PL,
         mls.UI_GENERIC_RUNS]
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
                        text = mls.UI_RMR_MAXRANGE % {'location': locationName,
                         'maxRange': util.FmtDist(const.maxCargoContainerTransferDistance)}
                        scrolllist.append(listentry.Get('Text', {'text': text}))
                    else:
                        blueprintCount = 0
                        installationID = self.installationDetails.containerID
                        inv = eve.GetInventoryFromId(installationID)
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
                accessScrollHint = mls.UI_RMR_ASSEMBLY_LINE_IN_SHIP
            else:
                blueprintCount = 0
                inv = eve.GetInventoryFromId(eve.session.shipid)
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
        sm.GetService('manufacturing').ReloadBlueprints('pickblueprint', ('persPickBlueprints', 'corpPickBlueprints'))



    def ReloadBlueprints(self):
        wnd = sm.GetService('window').GetWindow('pickblueprint')
        if wnd and wnd.sr.maintabs.GetSelectedArgs() in ('persPickBlueprints', 'corpPickBlueprints'):
            wnd.sr.maintabs.ReloadVisible()
        wnd = sm.GetService('window').GetWindow('assets')
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
    default_quote = None
    quote_doc = 'Quote'

    def ApplyAttributes(self, attributes):
        form.ListWindow.ApplyAttributes(self, attributes)
        quote = attributes.quote
        quoteData = attributes.quoteData
        self.scope = 'all'
        self.SetCaption(mls.UI_RMR_ACCEPTQUOTE)
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
        self.sr.quotePanel.submitHeader = mls.UI_CMD_ACCEPTQUOTE
        self.sr.quotePanel.submitFunc = self.AcceptQuote
        scroll = uiutil.GetChild(self.sr.quotePanel, 'installationsScroll')
        details = uiutil.GetChild(self.sr.quotePanel, 'installationDetails')
        content = uiutil.GetChild(scroll, '__content')
        minScrollHeight = 128
        maxScrollHeight = 384
        scroll.height = minScrollHeight
        blue.pyos.synchro.Sleep(0)
        scroll.height = min(maxScrollHeight, scroll.height + scroll.scrollingRange)
        self.height = scroll.height + details.height + 76
        self.SetMinSize([600, self.height])



    def AcceptQuote(self, *args):
        self.Confirm()



    def Confirm(self, *etc):
        self.SetModalResult(uiconst.ID_OK, close=False)



    def GetError(self):
        return ''



    def Error(self, error):
        if error:
            eve.Message('CustomInfo', {'info': error})




class QuotePanel(uicls.Container):
    __guid__ = 'xtriui.QuotePanel'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.submitHeader = mls.UI_CMD_ACCEPTQUOTE
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
        return ' - %s ' % uix.Plural(contentCount, 'UI_GENERIC_MISSINGAMOUNTOFUNIT') % {'first': missingCount,
         'second': contentCount}



    def LoadQuote(self, *args):
        uix.Flush(self.sr.quoteDetails)
        self.sr.quoteScroll.Load(contentList=[], headers=[])
        self.sr.quoteScroll.ShowHint('Fetching quote...')
        scrolllist = []
        bom = []
        headers = [mls.UI_GENERIC_NAME,
         mls.UI_GENERIC_REQUIRED,
         mls.UI_GENERIC_MISSING,
         mls.UI_RMR_DAMAGEPERJOB,
         mls.UI_RMR_WASTE]
        self.sr.quoteScroll.sr.fixedColumns = {mls.UI_GENERIC_NAME: 224,
         mls.UI_GENERIC_REQUIRED: 70,
         mls.UI_GENERIC_MISSING: 70,
         mls.UI_RMR_DAMAGEPERJOB: 60,
         mls.UI_RMR_WASTE: 60}
        if self.quote.bom:
            if len(self.quote.bom.rawMaterials):
                bom.append((mls.UI_RMR_RAWMATERIAL, self.quote.bom.rawMaterials))
            if len(self.quote.bom.extras):
                bom.append((mls.UI_RMR_EXTRAMATERIAL, self.quote.bom.extras))
            if len(self.quote.bom.skills):
                bom.append((mls.UI_GENERIC_SKILL, self.quote.bom.skills))
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
            self.sr.quoteScroll.ShowHint(mls.UI_RMR_NOQUOTEFOUND)
        uix.Flush(self.sr.quoteDetails)
        d = [(mls.UI_RMR_PRODUCTIONSTARTTIME, 'maxJobStartTime'),
         (mls.UI_RMR_PRODUCTIONTIME, 'productionTime'),
         (mls.UI_RMR_TOTALCOST, 'cost'),
         (mls.UI_RMR_INSTALLCOST, 'installCost'),
         (mls.UI_RMR_USAGECOST, 'usageCost')]
        d.append((mls.UI_CORP_WALLETDIVISION, 'accountKey'))
        d.extend([(mls.UI_RMR_MATERIALMULTIPL1, 'materialMultiplier'),
         (mls.UI_RMR_MATERIALMULTIPL2, 'charMaterialMultiplier'),
         (mls.UI_RMR_TIMEMULTIPL1, 'timeMultiplier'),
         (mls.UI_RMR_TIMEMULTIPL2, 'charTimeMultiplier')])
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
                    value = value - blue.os.GetTime()
                    if value < 0:
                        value = '<color=0xff00FF00>%s<color=0xffffffff>' % mls.UI_GENERIC_NOW
                    else:
                        value = int(value / 600000000L) * 10000000L * 60
                    value = '<color=0xffFF0000>%s<color=0xffffffff>' % util.FmtDate(value)
            t = uicls.Label(text='%s<t><right>%s' % (header, value), parent=self.sr.quoteDetails, left=left, top=top, singleline=0, tabs=tabs)
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
            t = uicls.Label(text='<color=0xffff0000>%s' % mls.UI_RMR_MISSINGMATERIALORSKILL, parent=self.sr.quoteDetails, left=6, top=top, singleline=0)
        submit = uicls.Button(parent=self.sr.quoteDetails, label=self.submitHeader, func=self.Submit, args=None, pos=(0,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        refreshBtn = uicls.Button(parent=self.sr.quoteDetails, label=mls.UI_CMD_REFRESH, func=self.Refresh, args=None, pos=(submit.width + 4,
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
        if mls.UI_RMR_RAWMATERIAL in [nodedata.label, nodedata.Get('cleanLabel', None)]:
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
                data.Set('sort_%s' % mls.UI_GENERIC_FACTORQTY, rawMaterial.quantity)
                scrolllist.append(listentry.Get('CheckEntry', data=data))

        if mls.UI_RMR_EXTRAMATERIAL in [nodedata.label, nodedata.Get('cleanLabel', None)]:
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

        if mls.UI_GENERIC_SKILL in [nodedata.label, nodedata.Get('cleanLabel', None)]:
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
        self.sr.planetScroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_PI_NOCOMMANDCENTERS)
        self.sr.buttons = uicls.ButtonGroup(btns=[[mls.UI_GENERIC_VIEWPLANET, self.ViewPlanet, ()]], parent=self.parentContainer, idx=0)
        self.sr.viewPlanetBtn = self.sr.buttons.GetBtnByLabel(mls.UI_GENERIC_VIEWPLANET)
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
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (cfg.evelocations.Get(row.solarSystemID).locationName,
             cfg.invtypes.Get(row.typeID).typeName,
             planetName,
             row.numberOfPins), GetMenu=self.GetPlanetEntryMenu, OnClick=self.OnPlanetEntryClick, planetID=row.planetID, typeID=row.typeID, hint=mls.UI_PI_PLANETENTRYHINT % {'planetName': planetName,
             'noOfInstallations': row.numberOfPins}, solarSystemID=row.solarSystemID, OnDblClick=self.OnPlanetEntryDblClick)
            scrolllist.append(listentry.Get('Generic', data=data))

        headers = [mls.UI_GENERIC_SYSTEMNAME,
         mls.UI_GENERIC_PLANETTYPE,
         mls.UI_GENERIC_PLANETNAME,
         mls.UI_GENERIC_INSTALLATIONS]
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
                menu += [(mls.UI_CMD_GMEXTRAS, ('isDynamic', menuSvc.GetGMMenu, (node.planetID,
                    None,
                    None,
                    None,
                    mapItem)))]
            menu += menuSvc.MapMenu([node.solarSystemID])
            isOpen = sm.GetService('planetUI').IsOpen() and sm.GetService('planetUI').planetID == node.planetID
            if isOpen:
                menu += [[mls.UI_PI_EXIT_PLANET_MODE, sm.GetService('planetUI').Close, ()]]
            else:
                menu += [(mls.UI_PI_VIEW_IN_PLANET_MODE, sm.GetService('planetUI').Open, (node.planetID,))]
            menu += [(mls.UI_CMD_SHOWINFO, menuSvc.ShowInfo, (node.typeID,
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
        sm.GetService('planetUI').Open(self.planetClickID)



    def OnPlanetEntryClick(self, entry):
        node = entry.sr.node
        self.planetClickID = node.planetID



    def OnPlanetEntryDblClick(self, entry):
        node = entry.sr.node
        sm.GetService('planetUI').Open(node.planetID)




