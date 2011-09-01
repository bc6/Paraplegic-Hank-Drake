import sys
import service
import uix
import uiutil
import uthread
import blue
import form
import turret
import log
import trinity
import util
import uicls
import uiconst
import geo2
from util import ReadYamlFile
from math import pi, pow

class StationSvc(service.Service):
    __guid__ = 'svc.station'
    __sessionparams__ = []
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetGuests': [],
     'IsGuest': [],
     'GetActiveShip': [],
     'Setup': [],
     'Exit': [],
     'GetSvc': [],
     'LoadSvc': [],
     'GiveHint': [],
     'ClearHint': [],
     'GetLobby': [],
     'GetStationServiceInfo': [],
     'StopAllStationServices': [],
     'CleanUp': [],
     'SelectShipDlg': [],
     'GetServiceState': []}
    __dependencies__ = ['journal', 'insurance']
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnStationOwnerChanged',
     'OnDogmaItemChange',
     'ProcessStationServiceItemChange',
     'ProcessSessionChange',
     'OnCharacterHandler',
     'OnDogmaAttributeChanged',
     'ProcessActiveShipChanged']

    def Run(self, memStream = None):
        self.LogInfo('Starting Station Service')
        self.CleanUp()



    def ProcessSessionChange(self, isRemote, session, change):
        if 'stationid' in change:
            (oldStationID, newStationID,) = change['stationid']
            if newStationID:
                self.GetServiceStates(1)
            else:
                self.serviceItemsState = None
            sm.GetService('michelle').RefreshCriminalFlagCountDown()



    def ProcessStationServiceItemChange(self, stationID, solarSystemID, serviceID, stationServiceItemID, isEnabled):
        self.GetServiceStates()
        if serviceID in self.serviceItemsState:
            state = self.serviceItemsState[serviceID]
            state.stationServiceItemID = stationServiceItemID
            state.isEnabled = isEnabled
        sm.ScatterEvent('OnProcessStationServiceItemChange', stationID, solarSystemID, serviceID, stationServiceItemID, isEnabled)



    def GetServiceStates(self, force = 0):
        if not self.serviceItemsState or force:
            if util.IsOutpost(eve.session.stationid) or sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
                self.serviceItemsState = sm.RemoteSvc('corpStationMgr').GetStationServiceStates()
            else:
                self.serviceItemsState = {}



    def GetServiceState(self, serviceID):
        self.GetServiceStates()
        return self.serviceItemsState.get(serviceID, None)



    def OnStationOwnerChanged(self, *args):
        uthread.pool('StationSvc::OnStationOwnerChanged --> LoadLobby', self.LoadLobby)



    def OnCharNowInStation(self, rec):
        (charID, corpID, allianceID, warFactionID,) = rec
        if charID not in self.guests:
            self.guests[charID] = (corpID, allianceID, warFactionID)
        self.serviceItemsState = None



    def OnCharNoLongerInStation(self, rec):
        (charID, corpID, allianceID, factionID,) = rec
        if charID in self.guests:
            self.guests.pop(charID)
        self.serviceItemsState = None



    def GetGuests(self):
        guests = sm.RemoteSvc('station').GetGuests()
        self.guests = {}
        for (charID, corpID, allianceID, warFactionID,) in guests:
            self.guests[charID] = (corpID, allianceID, warFactionID)

        return self.guests



    def IsGuest(self, whoID):
        return whoID in self.guests



    def Stop(self, memStream = None):
        self.LogInfo('Stopping Station Service')
        self.CleanUp()



    def CheckSession(self, change):
        if self.activeShip != eve.session.shipid:
            if eve.session.shipid:
                hangarInv = eve.GetInventory(const.containerHangar)
                hangarItems = hangarInv.List()
                for each in hangarItems:
                    if each.itemID == eve.session.shipid:
                        self.activeShipItem = each
                        self.ShowActiveShip()
                        break




    def GetStation(self):
        self.station = sm.GetService('ui').GetStation(eve.session.stationid)



    def GetStationServiceInfo(self, sortBy = None, stationInfo = None):
        if not self.station and eve.session.stationid:
            self.GetStation()
        services = []
        for (service, info,) in self.GetStationServices().iteritems():
            sortby = info[0]
            if sortBy == 'name':
                sortby = info[2]
            services.append((sortby, (service,
              info[1],
              info[2],
              info[3],
              info[4],
              info[5])))

        services = uiutil.SortListOfTuples(services)
        return services



    def GetServiceDisplayName(self, service):
        s = self.GetStationServices(service)
        if s:
            return s[2]
        return mls.UI_GENERIC_UNKNOWN



    def GetStationServices(self, service = None):
        mapping = [['vstore',
          'OpenStore',
          mls.UI_VGSTORE_VGSTORE,
          '65_3',
          True,
          (-1,)],
         ['charcustomization',
          'OpenCharacterCustomization',
          mls.UI_CHARCREA_RECUSTOMIZATION,
          '66_3',
          True,
          (-1,)],
         ['medical',
          'OpenMedical',
          mls.UI_STATION_MEDICAL,
          'ui_18_128_3',
          True,
          (const.stationServiceCloning, const.stationServiceSurgery, const.stationServiceDNATherapy)],
         ['repairshop',
          'OpenRepairshop',
          mls.UI_STATION_REPAIRSHOP,
          'ui_18_128_4',
          True,
          (const.stationServiceRepairFacilities,)],
         ['reprocessingPlant',
          'OpenReprocessingPlant',
          mls.UI_STATION_REPROCESSINGPLANT,
          'ui_17_128_1',
          True,
          (const.stationServiceReprocessingPlant,)],
         ['market',
          'OpenMarket',
          mls.UI_MARKET_MARKET,
          'ui_18_128_1',
          False,
          (const.stationServiceMarket,)],
         ['fitting',
          'OpenFitting',
          mls.UI_STATION_FITTING,
          'ui_17_128_4',
          False,
          (const.stationServiceFitting,)],
         ['factories',
          'OpenFactories',
          mls.UI_RMR_SCIENCEANDINDUSTRY,
          '57_9',
          False,
          (const.stationServiceFactory, const.stationServiceLaboratory)],
         ['missions',
          'OpenMissions',
          mls.UI_STATION_BOUNTY,
          '61_2',
          True,
          (const.stationServiceBountyMissions, const.stationServiceAssassinationMissions)],
         ['navyoffices',
          'OpenMilitia',
          mls.UI_STATION_MILITIAOFFICE,
          '61_3',
          False,
          (const.stationServiceNavyOffices,)],
         ['insurance',
          'OpenInsurance',
          mls.UI_STATION_INSURANCE,
          '33_4',
          True,
          (const.stationServiceInsurance,)],
         ['lpstore',
          'OpenLpstore',
          mls.UI_LPSTORE_LPSTORE,
          '70_11',
          True,
          (const.stationServiceLoyaltyPointStore,)]]
        newmapping = {}
        for (i, servicemap,) in enumerate(mapping):
            (lbl, cmdstr, label, icon, stationonly, servicemasks,) = servicemap
            newmapping[lbl] = (i,
             cmdstr,
             label,
             icon,
             stationonly,
             servicemasks)

        if service:
            return newmapping.get(service, None)
        return newmapping



    def CheckHasStationService(self, service, serviceMask):
        pass



    def CleanUp(self, storeCamera = 1):
        try:
            if getattr(self, 'underlay', None):
                sm.GetService('window').UnregisterWindow(self.underlay)
                self.underlay.OnClick = None
                self.underlay.Minimize = None
                self.underlay.Maximize = None
        except:
            pass
        uix.Close(self, ['closeBtn',
         'hint',
         'underlay',
         'lobby'])
        self.lobby = None
        self.underlay = None
        self.closeBtn = None
        self.hint = None
        self.fittingflags = None
        self.selected_service = None
        self.loading = None
        self.active_service = None
        self.activeShip = None
        self.activeShipItem = None
        self.activeshipmodel = None
        self.refreshingfitting = 0
        self.loadingSvc = 0
        self.dockaborted = 0
        self.exitingstation = 0
        self.activatingShip = 0
        self.leavingShip = 0
        self.paperdollState = None
        self.guests = {}
        self.serviceItemsState = {}
        self.maxZoom = 750.0
        self.minZoom = 150.0
        self.station = None
        self.previewColorIDs = {'MAIN': 0,
         'MARKINGS': 0,
         'LIGHTS': 0}
        layer = uicore.layer.station
        if layer:
            uix.Flush(layer)



    def StopAllStationServices(self):
        services = self.GetStationServiceInfo()
        for service in services:
            if sm.IsServiceRunning(service[0]):
                sm.services[service[0]].Stop()




    def Setup(self, reloading = 0):
        self.CleanUp(0)
        self.loading = 1
        if not reloading:
            eve.Message('OnEnterStation')
        stationTypeID = eve.stationItem.stationTypeID
        stationType = cfg.invtypes.Get(stationTypeID)
        stationRace = stationType['raceID']
        if stationRace == const.raceAmarr:
            scenePath = 'res:/dx9/scene/hangar/amarr.red'
            shipPositionData = ReadYamlFile('res:/dx9/scene/hangar/shipPlacementAmarr.yaml')
            positioning = ReadYamlFile('res:/dx9/scene/hangar/amarrbalconyplacement.yaml')
            self.sceneTranslation = positioning['position']
            self.sceneRotation = geo2.QuaternionRotationSetYawPitchRoll(positioning['orientation'], 0.0, 0.0)
        elif stationRace == const.raceCaldari:
            scenePath = 'res:/dx9/scene/hangar/caldari.red'
            shipPositionData = ReadYamlFile('res:/dx9/scene/hangar/shipPlacementCaldari.yaml')
            positioning = ReadYamlFile('res:/dx9/scene/hangar/caldaribalconyplacement.yaml')
            self.sceneTranslation = positioning['position']
            self.sceneRotation = geo2.QuaternionRotationSetYawPitchRoll(positioning['orientation'], 0.0, 0.0)
        elif stationRace == const.raceGallente:
            scenePath = 'res:/dx9/scene/hangar/gallente.red'
            shipPositionData = ReadYamlFile('res:/dx9/scene/hangar/shipPlacementGallente.yaml')
            positioning = ReadYamlFile('res:/dx9/scene/hangar/gallentebalconyplacement.yaml')
            self.sceneTranslation = positioning['position']
            self.sceneRotation = geo2.QuaternionRotationSetYawPitchRoll(positioning['orientation'], 0.0, 0.0)
        elif stationRace == const.raceMinmatar:
            scenePath = 'res:/dx9/scene/hangar/minmatar.red'
            shipPositionData = ReadYamlFile('res:/dx9/scene/hangar/shipPlacementMinmatar.yaml')
            positioning = ReadYamlFile('res:/dx9/scene/hangar/minmatarbalconyplacement.yaml')
            self.sceneTranslation = positioning['position']
            self.sceneRotation = geo2.QuaternionRotationSetYawPitchRoll(positioning['orientation'], 0.0, 0.0)
        else:
            scenePath = 'res:/dx9/scene/hangar/gallente.red'
            shipPositionData = ReadYamlFile('res:/dx9/scene/hangar/shipPlacementGallente.yaml')
            positioning = ReadYamlFile('res:/dx9/scene/hangar/gallentebalconyplacement.yaml')
            self.sceneTranslation = positioning['position']
            self.sceneRotation = geo2.QuaternionRotationSetYawPitchRoll(positioning['orientation'], 0.0, 0.0)
        sm.GetService('sceneManager').UnregisterScene('default')
        sm.GetService('sceneManager').UnregisterScene2('default')
        sm.GetService('sceneManager').UnregisterCamera('default')
        self.hangarScene = blue.os.LoadObject(scenePath)
        sm.GetService('sceneManager').SetupIncarnaBackground(self.hangarScene, self.sceneTranslation, self.sceneRotation)
        self.shipPositionMinDistance = shipPositionData['minDistance']
        self.shipPositionMaxDistance = shipPositionData['maxDistance']
        self.shipPositionMaxSize = shipPositionData['shipMaxSize']
        self.shipPositionMinSize = shipPositionData['shipMinSize']
        self.shipPositionTargetHeightMin = shipPositionData['shipTargetHeightMin']
        self.shipPositionTargetHeightMax = shipPositionData['shipTargetHeightMax']
        self.shipPositionCurveRoot = shipPositionData['curveRoot']
        self.shipPositionRotation = shipPositionData['rotation']
        if self.hangarScene is not None:
            stationModel = self.hangarScene.objects[0]
            stationModel.enableShadow = False
        if util.GetActiveShip() is not None:
            self.ShowShip(util.GetActiveShip())
        if not (eve.rookieState and eve.rookieState < 5):
            self.LoadLobby()
        if self.station is None and eve.session.stationid:
            self.station = sm.GetService('ui').GetStation(eve.session.stationid)
        sm.GetService('autoPilot').SetOff('toggled by Station Entry')
        mapSvc = sm.StartService('map')
        if mapSvc.IsOpen():
            mapSvc.MinimizeWindows()
        planetUISvc = sm.GetService('planetUI')
        if planetUISvc.IsOpen():
            planetUISvc.MinimizeWindows()
        self.loading = 0
        self.sprite = None
        if not reloading:
            if util.GetActiveShip() is None:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningWhenPoddedTutorial)
            if sm.GetService('skills').GetSkillPoints() >= 1500000:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningTutorial)
            sm.GetService('loading').FadeFromBlack()



    def GetPaperdollStateCache(self):
        if self.paperdollState is None:
            self.paperdollState = sm.RemoteSvc('charMgr').GetPaperdollState()
        return self.paperdollState



    def OnCharacterHandler(self):
        self.ClearPaperdollStateCache()



    def ClearPaperdollStateCache(self):
        self.paperdollState = None



    def StopAllBlinkButtons(self):
        lobby = self.GetLobby()
        if not lobby:
            return 
        for each in uiutil.GetChild(lobby, 'btnparent').children:
            if hasattr(each, 'Blink'):
                each.Blink(0)




    def BlinkButton(self, what):
        lobby = self.GetLobby()
        if not lobby:
            return 
        for each in uiutil.GetChild(lobby, 'btnparent').children:
            if each.name.lower() == what.lower():
                each.Blink(blinks=40)




    def LoadLobby(self):
        if not eve.session.stationid:
            return 
        self.GetLobby(1, 1)



    def DoPOSWarning(self):
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            eve.Message('POStationWarning')



    def GetActiveShip(self):
        return util.GetActiveShip()



    def TryActivateShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        if shipid == self.activeShip:
            return 
        if self.activatingShip:
            return 
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogmaLocation.CheckSkillRequirementsForType(invitem.typeID, 'SkillHasPrerequisites')
        techLevel = sm.StartService('godma').GetTypeAttribute(invitem.typeID, const.attributeTechLevel)
        if techLevel is not None and int(techLevel) == 3:
            if eve.Message('AskActivateTech3Ship', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
        self.activatingShip = 1
        try:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            dogmaLocation.MakeShipActive(shipid)
            self.activeShipItem = invitem
            if invitem.groupID != const.groupRookieship:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.insuranceTutorial)

        finally:
            self.activatingShip = 0




    def TryLeaveShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        if shipid != self.activeShip:
            return 
        if self.leavingShip:
            return 
        self.leavingShip = 1
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            sm.GetService('gameui').KillCargoView(shipid)
            capsuleID = shipsvc.LeaveShip(shipid)
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            dogmaLocation.MakeShipActive(capsuleID)

        finally:
            self.leavingShip = 0




    def ShowShip(self, shipID):
        self.WaitForShip(shipID)
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        hangarItems = hangarInv.List()
        for each in hangarItems:
            if each.itemID == shipID:
                self.activeShipItem = each
                try:
                    uthread.new(self.ShowActiveShip)
                except Exception as e:
                    log.LogException('Failed to show ship')
                    sys.exc_clear()
                break




    def GetTech3ShipFromSlimItem(self, slimItem):
        subSystemIds = {}
        for module in slimItem.modules:
            if module.categoryID == const.categorySubSystem:
                subSystemIds[module.groupID] = module.typeID

        if len(subSystemIds) < const.visibleSubSystems:
            sm.services['window'].GetWindow('AssembleShip', create=1, decoClass=form.AssembleShip, ship=slimItem, groupIDs=subSystemIds.keys())
            return 
        return sm.StartService('t3ShipSvc').GetTech3ShipFromDict(slimItem.typeID, subSystemIds)



    def ShowActiveShip(self):
        if getattr(self, '__alreadyShowingActiveShip', False):
            log.LogTraceback("We're already in the process of showing the active ship")
            return 
        self._StationSvc__alreadyShowingActiveShip = True
        try:
            invitem = self.activeShipItem
            scene2 = getattr(self, 'hangarScene', None)
            if scene2:
                for each in scene2.objects:
                    if getattr(each, 'name', None) == str(self.activeShip):
                        scene2.objects.remove(each)

            try:
                techLevel = sm.GetService('godma').GetTypeAttribute(invitem.typeID, const.attributeTechLevel)
                if techLevel == 3.0:
                    try:
                        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                        dogmaItem = dogmaLocation.dogmaItems[self.activeShipItem.itemID]
                        newModel = self.MakeModularShipFromShipItem(dogmaItem)
                    except:
                        log.LogException('failed bulding modular ship')
                        sys.exc_clear()
                        return 
                else:
                    modelPath = cfg.invtypes.Get(invitem.typeID).GraphicFile()
                    newFilename = modelPath.lower().replace(':/model', ':/dx9/model')
                    newFilename = newFilename.replace('.blue', '.red')
                    newModel = trinity.Load(newFilename)
            except Exception as e:
                log.LogException(str(e))
                sys.exc_clear()
                return 
            newModel.FreezeHighDetailMesh()
            self.PositionShipModel(newModel)
            if hasattr(newModel, 'ChainAnimationEx'):
                newModel.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
            self.activeShip = invitem.itemID
            self.activeshipmodel = newModel
            self.FitHardpoints(0)
            newModel.display = 1
            newModel.name = str(invitem.itemID)
            if sm.GetService('clientDogmaIM').GetDogmaLocation().dogmaItems[util.GetActiveShip()].groupID != const.groupCapsule:
                scene2.objects.append(newModel)
            sm.ScatterEvent('OnActiveShipModelChange', newModel)

        finally:
            self._StationSvc__alreadyShowingActiveShip = False




    def GetActiveShipModel(self):
        return self.activeshipmodel



    def PositionShipModel(self, model):
        trinity.WaitForResourceLoads()
        localBB = model.GetLocalBoundingBox()
        if localBB[0] is None or localBB[1] is None:
            log.LogError("Failed to get bounding info for ship. Odds are the ship wasn't loaded properly.")
            localBB = (trinity.TriVector(0, 0, 0), trinity.TriVector(0, 0, 0))
        boundingCenter = model.boundingSphereCenter[1]
        radius = model.boundingSphereRadius - self.shipPositionMinSize
        val = radius / (self.shipPositionMaxSize - self.shipPositionMinSize)
        if val > 1.0:
            val = 1.0
        if val < 0:
            val = 0
        val = pow(val, 1.0 / self.shipPositionCurveRoot)
        shipDirection = (self.sceneTranslation[0], 0, self.sceneTranslation[2])
        shipDirection = geo2.Vec3Normalize(shipDirection)
        distancePosition = geo2.Lerp((self.shipPositionMinDistance, self.shipPositionTargetHeightMin), (self.shipPositionMaxDistance, self.shipPositionTargetHeightMax), val)
        y = distancePosition[1] - boundingCenter
        y = y + self.sceneTranslation[1]
        if y < -localBB[0].y + 180:
            y = -localBB[0].y + 180
        boundingBoxZCenter = localBB[0].z + localBB[1].z
        boundingBoxZCenter *= 0.5
        shipPos = geo2.Vec3Scale(shipDirection, -distancePosition[0])
        shipPos = geo2.Vec3Add(shipPos, self.sceneTranslation)
        shipPosition = (shipPos[0], y, shipPos[2])
        model.translationCurve = trinity.TriVectorCurve()
        model.translationCurve.value.x = shipPosition[0]
        model.translationCurve.value.y = shipPosition[1]
        model.translationCurve.value.z = shipPosition[2]
        model.rotationCurve = trinity.TriRotationCurve()
        model.rotationCurve.value.YawPitchRoll(self.shipPositionRotation * pi / 180, 0, 0)
        model.modelTranslationCurve = blue.os.LoadObject('res:/dx9/scene/hangar/ship_modelTranslationCurve.red')
        model.modelTranslationCurve.ZCurve.offset -= boundingBoxZCenter
        scaleMultiplier = 0.35 + 0.65 * (1 - val)
        capitalShips = [const.groupDreadnought,
         const.groupSupercarrier,
         const.groupTitan,
         const.groupFreighter,
         const.groupJumpFreighter,
         const.groupCarrier,
         const.groupCapitalIndustrialShip,
         const.groupIndustrialCommandShip]
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if getattr(dogmaLocation.GetDogmaItem(self.GetActiveShip()), 'groupID', None) in capitalShips:
            scaleMultiplier = 0.35 + 0.25 * (1 - val)
            model.modelRotationCurve = blue.os.LoadObject('res:/dx9/scene/hangar/ship_modelRotationCurve.red')
            model.modelRotationCurve.PitchCurve.speed *= scaleMultiplier
            model.modelRotationCurve.RollCurve.speed *= scaleMultiplier
            model.modelRotationCurve.YawCurve.speed *= scaleMultiplier
        elif val > 0.6:
            val = 0.6
        scaleMultiplier = 0.35 + 0.65 * (1 - val / 0.6)
        model.modelRotationCurve = blue.os.LoadObject('res:/dx9/scene/hangar/ship_modelRotationCurveSpinning.red')
        model.modelRotationCurve.PitchCurve.speed *= scaleMultiplier
        model.modelRotationCurve.RollCurve.speed *= scaleMultiplier
        model.modelRotationCurve.YawCurve.start = blue.os.GetTime()
        model.modelRotationCurve.YawCurve.ScaleTime(6 * val + 1)



    def FindHierarchicalBoundingBox(self, transform, printout, indent = '', minx = 1e+100, maxx = -1e+100, miny = 1e+100, maxy = -1e+100, minz = 1e+100, maxz = -1e+100):
        transform.Update(blue.os.GetTime())
        if printout:
            print indent,
            print transform.name
        if hasattr(transform, 'translation') and transform.__typename__ in ('TriTransform', 'TriSplTransform', 'TriLODGroup'):
            if transform.__typename__ == 'TriTransform':
                if transform.transformBase != trinity.TRITB_OBJECT:
                    return (minx,
                     maxx,
                     miny,
                     maxy,
                     minz,
                     maxz)
            if hasattr(transform, 'object') and transform.object is not None:
                doMesh = False
                if getattr(transform.object, 'vertexRes', None) is not None:
                    v = transform.object.vertexRes
                    meshBoxMin = v.meshBoxMin.CopyTo()
                    meshBoxMax = v.meshBoxMax.CopyTo()
                    doMesh = True
                elif transform.object.__typename__ in ('TriMesh', 'TriMultiMesh'):
                    meshBoxMin = transform.object.meshBoxMin.CopyTo()
                    meshBoxMax = transform.object.meshBoxMax.CopyTo()
                    doMesh = True
                if doMesh:
                    meshBoxMin.TransformCoord(transform.worldTransform)
                    meshBoxMax.TransformCoord(transform.worldTransform)
                    minx = min(minx, meshBoxMin.x)
                    maxx = max(maxx, meshBoxMax.x)
                    miny = min(miny, meshBoxMin.y)
                    maxy = max(maxy, meshBoxMax.y)
                    minz = min(minz, meshBoxMin.z)
                    maxz = max(maxz, meshBoxMax.z)
            for child in transform.children:
                indent = indent + '  '
                (minx, maxx, miny, maxy, minz, maxz,) = self.FindHierarchicalBoundingBox(child, printout, indent, minx, maxx, miny, maxy, minz, maxz)

        return (minx,
         maxx,
         miny,
         maxy,
         minz,
         maxz)



    def OnDogmaItemChange(self, item, change):
        if session.stationid is None:
            return 
        if item.groupID in const.turretModuleGroups:
            self.FitHardpoints()
        if item.locationID == change.get(const.ixLocationID, None) and item.flagID == change.get(const.ixFlag):
            return 
        activeShipID = util.GetActiveShip()
        if item.locationID == activeShipID and cfg.IsShipFittingFlag(item.flagID) and item.categoryID == const.categorySubSystem:
            sm.GetService('station').ShowShip(activeShipID)



    def ModuleListFromGodmaSlimItem(self, slimItem):
        list = []
        for module in slimItem.modules:
            list.append((module.itemID, module.typeID))

        list.sort()
        return list



    def FitHardpoints(self, checkScene = 1):
        if not self.activeshipmodel or self.refreshingfitting:
            return 
        self.refreshingfitting = 1
        turret.TurretSet.FitTurrets(util.GetActiveShip(), self.activeshipmodel)
        self.refreshingfitting = 0



    def GetUnderlay(self):
        if self.underlay is None:
            for each in uicore.layer.main.children[:]:
                if each is not None and not each.destroyed and each.name == 'services':
                    sm.GetService('window').UnregisterWindow(each)
                    each.OnClick = None
                    each.Minimize = None
                    each.Maximize = None
                    each.Close()

            self.underlay = uicls.Sprite(name='services', parent=uicore.layer.main, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
            self.underlay.scope = 'station'
            self.underlay.minimized = 0
            self.underlay.Minimize = self.MinimizeUnderlay
            self.underlay.Maximize = self.MaximizeUnderlay
            main = uicls.Container(name='mainparentXX', parent=self.underlay, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            main.OnClick = self.ClickParent
            main.state = uiconst.UI_NORMAL
            sub = uicls.Container(name='subparent', parent=main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            captionparent = uicls.Container(name='captionparent', parent=main, align=uiconst.TOPLEFT, left=128, top=36, idx=0)
            caption = uicls.CaptionLabel(text='', parent=captionparent)
            self.closeBtn = uicls.ButtonGroup(btns=[[mls.UI_CMD_CLOSE,
              self.CloseSvc,
              None,
              81]], parent=sub)
            self.sr.underlay = uicls.WindowUnderlay(parent=main)
            self.sr.underlay.SetPadding(-1, -10, -1, 0)
            svcparent = uicls.Container(name='serviceparent', parent=sub, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.underlay.sr.main = main
            self.underlay.sr.svcparent = svcparent
            self.underlay.sr.caption = caption
            sm.GetService('window').RegisterWindow(self.underlay)
        return self.underlay



    def MinimizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_HIDDEN



    def MaximizeUnderlay(self, *args):
        self.underlay.state = uiconst.UI_PICKCHILDREN
        self.ClickParent()



    def ClickParent(self, *args):
        for each in uicore.layer.main.children:
            if getattr(each, 'isDockWnd', 0) == 1 and each.state == uiconst.UI_NORMAL:
                uiutil.SetOrder(each, -1)




    def LoadSvc(self, service, close = 1):
        serviceInfo = self.GetStationServices(service)
        if service is not None and serviceInfo is not None:
            (pos, cmdstr, label, icon, stationonly, servicemasks,) = serviceInfo
            self.ExecuteCommand(cmdstr)
            return 
        if getattr(self, 'loadingSvc', 0):
            return 
        self.loadingSvc = 1
        while self.loading:
            blue.pyos.synchro.Sleep(500)

        if self.selected_service is None:
            if service:
                self._LoadSvc(1, service)
        elif service == self.selected_service:
            if close:
                self._LoadSvc(0)
        else:
            self._LoadSvc(0, service)
        self.loadingSvc = 0



    def ExecuteCommand(self, cmdstr):
        func = getattr(uicore.cmd, cmdstr, None)
        if func:
            func()



    def GetSvc(self, svcname = None):
        if self.active_service is not None:
            if svcname is not None:
                if self.selected_service == svcname:
                    return self.active_service
            else:
                return self.active_service



    def GetLobby(self, create = 0, doReload = 0):
        wnd = sm.GetService('window').GetWindow('lobby')
        if wnd and not wnd.destroyed:
            if doReload:
                wnd.SelfDestruct()
            else:
                return wnd
        wnd = sm.GetService('window').GetWindow('lobby', create=create, decoClass=form.Lobby)
        return wnd



    def _LoadSvc(self, inout, service = None):
        self.loading = 1
        print '_LoadSvc',
        print service
        wnd = self.GetUnderlay()
        newsvc = None
        if inout == 1 and wnd is not None:
            self.ClearHint()
            (newsvc, svctype,) = self.SetupService(wnd, service)
        if wnd.absoluteRight - wnd.absoluteLeft < 700 and inout == 1:
            sm.GetService('neocom').Minimize()
        height = uicore.desktop.height - 180
        wnd.state = uiconst.UI_PICKCHILDREN
        if inout == 1:
            sm.GetService('neocom').SetLocationInfoState(0)
        wnd.height = height
        if inout:
            wnd.top = -height
        uicore.effect.MorphUI(wnd, 'top', [-height, 0][inout], 500.0, 1, 1)
        snd = service
        if inout == 0:
            snd = self.selected_service
        if snd is not None:
            eve.Message('LoadSvc_%s%s' % (snd, ['Out', 'In'][inout]))
        blue.pyos.synchro.Sleep([750, 1250][inout])
        if inout == 0:
            sm.GetService('neocom').SetLocationInfoState(1)
        if newsvc is not None:
            if svctype == 'form':
                print 'Start service'
                newsvc.Startup(self)
            elif settings.user.ui.Get('nottry', 0):
                newsvc.Initialize(wnd.sr.svcparent)
            else:
                try:
                    newsvc.Initialize(wnd.sr.svcparent)
                except:
                    log.LogException(channel=self.__guid__)
                    sys.exc_clear()
            self.active_service = newsvc
            self.selected_service = service
        else:
            uix.Flush(wnd.sr.svcparent)
            if self.active_service and hasattr(self.active_service, 'Reset'):
                self.active_service.Reset()
            self.active_service = None
            self.selected_service = service
        self.loading = 0
        if inout == 0 and service is not None:
            self._LoadSvc(1, service)
        if inout == 0 and service is None:
            uix.Flush(wnd.sr.svcparent)



    def Startup(self, svc):
        uthread.new(svc.Startup, self)



    def GiveHint(self, hintstr, left = 80, top = 320, width = 300):
        self.ClearHint()
        if self.hint is None:
            par = uicls.Container(name='captionParent', parent=self.GetUnderlay().sr.main, align=uiconst.TOPLEFT, top=top, left=left, width=width, height=256, idx=0)
            self.hint = uicls.CaptionLabel(text='', parent=par, align=uiconst.TOALL, left=0, top=0)
        self.hint.parent.top = top
        self.hint.parent.left = left
        self.hint.parent.width = width
        self.hint.text = hintstr or ''



    def ClearHint(self):
        if self.hint is not None:
            self.hint.text = ''



    def SetupService(self, wnd, servicename):
        uix.Flush(wnd.sr.svcparent)
        svc = None
        topheight = 128
        btmheight = 0
        icon = 'ui_9_64_14'
        sz = 128
        top = -16
        icon = uicls.Icon(icon=icon, parent=wnd.sr.svcparent, left=0, top=top, size=sz, idx=0)
        iconpar = uicls.Container(name='iconpar', parent=wnd.sr.svcparent, align=uiconst.TOTOP, height=96, clipChildren=1, state=uiconst.UI_PICKCHILDREN)
        bigicon = icon.CopyTo()
        bigicon.width = bigicon.height = sz * 2
        bigicon.top = -64
        bigicon.color.a = 0.1
        iconpar.children.append(bigicon)
        closeX = uicls.Icon(icon='ui_38_16_220')
        closeX.align = uiconst.TOPRIGHT
        closeX.left = closeX.top = 2
        closeX.OnClick = self.CloseSvc
        iconpar.children.append(closeX)
        line = uicls.Line(parent=iconpar, align=uiconst.TOPRIGHT, height=1, left=2, top=16, width=18)
        icon.state = uiconst.UI_DISABLED
        wnd.sr.caption.text = self.GetServiceDisplayName(servicename)
        wnd.sr.caption.state = uiconst.UI_DISABLED
        return (svc, 'service')



    def CloseSvc(self, *args):
        uthread.new(self.LoadSvc, None)



    def AbortUndock(self, *args):
        sm.GetService('loading').ProgressWnd(mls.UI_STATION_ABORTUNDOCK, '', 1, 1)
        self.dockaborted = 1
        self.exitingstation = 0
        self.LoadLobby()
        sm.GetService('loading').FadeFromBlack()
        sm.GetService('tutorial').UnhideTutorialWindow()



    def Exit(self, *args):
        if self.exitingstation:
            return 
        if sm.GetService('actionObjectClientSvc').IsEntityUsingActionObject(session.charid):
            sm.GetService('actionObjectClientSvc').ExitActionObject(session.charid)
        sm.GetService('michelle').RefreshCriminalFlagCountDown()
        (charcrimes, corpcrimes,) = sm.GetService('michelle').GetCriminalFlagCountDown()
        systemSecStatus = sm.StartService('map').GetSecurityClass(eve.session.solarsystemid2)
        beenWarned = False
        if charcrimes.has_key(None):
            if systemSecStatus == const.securityClassHighSec:
                response = eve.Message('UndockCriminalConfirm', {}, uiconst.YESNO)
                beenWarned = True
                if response != uiconst.ID_YES:
                    return 
        if charcrimes and not beenWarned:
            if systemSecStatus > const.securityClassZeroSec:
                for (k, v,) in charcrimes.iteritems():
                    if k == eve.stationItem.ownerID or not util.IsNPC(k):
                        if eve.Message('UndockAggressionConfirm', {}, uiconst.YESNO) == uiconst.ID_YES:
                            break
                        return 

        shipID = util.GetActiveShip()
        if shipID is None:
            shipID = self.ShipPicker()
            if shipID is None:
                eve.Message('NeedShipToUndock')
                return 
            sm.GetService('clientDogmaIM').GetDogmaLocation().MakeShipActive(shipID)
        self.exitingstation = 1
        self.dockaborted = 0
        uthread.new(self.LoadSvc, None)
        lobby = self.GetLobby()
        if lobby is not None and not lobby.destroyed:
            lobby.SelfDestruct()
        sm.GetService('uipointerSvc').ClearPointers()
        msg = [(mls.UI_STATION_PREPARETOUNDOCK, mls.UI_STATION_REQUESTINGUNDOCK),
         (mls.UI_STATION_PREPARETOUNDOCK, mls.UI_STATION_WAITINGFORCONFIRM),
         (mls.UI_STATION_PREPARETOUNDOCK, mls.UI_STATION_UNDOCKCONFIRMED),
         (mls.UI_STATION_ENTERINGSPACE, mls.UI_STATION_PREPARINGSHIP),
         (mls.UI_STATION_ENTERINGSPACE, mls.UI_STATION_SHIPREADY)]
        minSleepTime = max(len(msg) * 1000, ((eve.session.nextSessionChange or 0.0) - blue.os.GetTime()) / (SEC / 1000)) / len(msg)
        uthread.new(sm.GetService('loading').FadeToBlack, 4000)
        for i in xrange(len(msg)):
            if self.dockaborted:
                self.exitingstation = 0
                break
            sm.GetService('loading').ProgressWnd(msg[i][0], msg[i][1], i + 1, len(msg) + 1, abortFunc=self.AbortUndock)
            blue.pyos.synchro.Sleep(minSleepTime)

        blue.pyos.synchro.Sleep(1000)
        if self.dockaborted:
            self.dockaborted = 0
            return 
        sm.GetService('loading').ProgressWnd(msg[i][0], msg[i][1], i + 2, len(msg) + 1)
        self.UndockAttempt(shipID)



    def UndockAttempt(self, shipID):
        systemCheckSupressed = settings.user.suppress.Get('suppress.FacWarWarningUndock', None) == uiconst.ID_OK
        if not systemCheckSupressed and eve.session.warfactionid:
            isSafe = sm.StartService('facwar').CheckForSafeSystem(eve.stationItem, eve.session.warfactionid)
            if not isSafe:
                if not eve.Message('FacWarWarningUndock', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                    settings.user.suppress.Set('suppress.FacWarWarningUndock', None)
                    self.exitingstation = 0
                    self.AbortUndock()
                    return 
        self.DoUndockAttempt(False, True, shipID)



    def DoUndockAttempt(self, ignoreContraband, observedSuppressed, shipID):
        stationID = session.stationid
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            sm.GetService('logger').AddText(mls.UI_STATION_UNDOCKINGFROMTO % {'from': cfg.evelocations.Get(eve.session.stationid2).name,
             'to': cfg.evelocations.Get(eve.session.solarsystemid2).name})
            if observedSuppressed:
                ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            onlineModules = sm.GetService('clientDogmaIM').GetDogmaLocation().GetOnlineModules(shipID)
            sm.GetService('sessionMgr').PerformSessionChange('undock', shipsvc.Undock, shipID, ignoreContraband, onlineModules=onlineModules)
            self.CloseFitting()
        except Exception as e:
            doRaise = True
            if isinstance(e, UserError) and e.msg == 'ShipContrabandWarningUndock':
                if eve.Message(e.msg, e.dict, uiconst.OKCANCEL) == uiconst.ID_OK:
                    self.DoUndockAttempt(True, False, shipID)
                    sys.exc_clear()
                    return 
                settings.user.suppress.Set('suppress.ShipContrabandWarningUndock', None)
                doRaise = False
            self.exitingstation = 0
            self.AbortUndock()
            if doRaise:
                raise 
            sys.exc_clear()
        self.exitingstation = 0
        self.hangarScene = None
        sm.GetService('worldSpaceClient').TearDownWorldSpaceRendering()
        sm.GetService('worldSpaceClient').UnloadWorldSpaceInstance(stationID)



    def CloseFitting(self):
        wnd = sm.GetService('window').GetWindow('fitting')
        if wnd:
            wnd.CloseX()



    def ShipPicker(self):
        hangarInv = eve.GetInventory(const.containerHangar)
        items = hangarInv.List()
        tmplst = []
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((cfg.invtypes.Get(item[const.ixTypeID]).name, item[const.ixItemID], item[const.ixTypeID]))

        ret = uix.ListWnd(tmplst, 'item', mls.UI_STATION_SELECTSHIP, None, 1)
        if ret is None:
            return 
        return ret[1]



    def SelectShipDlg(self):
        hangarInv = eve.GetInventory(const.containerHangar)
        items = hangarInv.List()
        tmplst = []
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((cfg.invtypes.Get(item[const.ixTypeID]).name, item[const.ixItemID], item[const.ixTypeID]))

        if not tmplst:
            self.exitingstation = 0
            eve.Message('NeedShipToUndock')
            return 
        ret = uix.ListWnd(tmplst, 'item', mls.UI_STATION_SELECTSHIP, None, 1)
        if ret is None or ret[1] == session.shipid:
            self.exitingstation = 0
            return 
        activeShip = ret[1]
        shipsvc = sm.GetService('gameui').GetShipAccess()
        try:
            sm.GetService('sessionMgr').PerformSessionChange('board', shipsvc.Board, activeShip, session.shipid if session.shipid else session.stationid)
            self.ShowShip(activeShip)
        except:
            self.exitingstation = 0
            raise 



    def WaitForShip(self, shipID):
        maximumWait = 10000
        sleepUnit = 100
        iterations = maximumWait / sleepUnit
        while util.GetActiveShip() != shipID and iterations:
            iterations -= 1
            blue.pyos.synchro.Sleep(sleepUnit)

        if util.GetActiveShip() != shipID:
            raise RuntimeError('Ship never came :(')
        self.LogInfo('Waited for ship for %d iterations.' % (maximumWait / sleepUnit - iterations))



    def ChangeColorOfActiveShip(self, typeName, colorID, typeID):
        self.previewColorIDs[typeName] = colorID
        sm.services['t3ShipSvc'].ChangeColor(self.activeshipmodel, self.previewColorIDs, typeID)



    def ConfirmChangeColor(self):
        if self.previewColorIDs is None:
            return 
        eve.GetInventoryFromId(self.activeShip).ChangeColor(self.previewColorIDs)
        eve.Message('ColorOfShipHasBeenChanged')



    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if self.activeshipmodel and attributeID == const.attributeIsOnline and shipID == util.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            slot = None
            for module in dogmaLocation.GetDogmaItem(shipID).GetFittedItems().itervalues():
                if module.itemID != itemID:
                    continue
                slot = module.flagID - const.flagHiSlot0 + 1
                sceneShip = self.activeshipmodel
                for turretSet in sceneShip.turretSets:
                    if turretSet.locatorName.split('_')[-1] == str(slot):
                        if module.IsOnline():
                            turretSet.EnterStateIdle()
                        else:
                            turretSet.EnterStateDeactive()





    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if oldShipID:
            sm.GetService('gameui').KillCargoView(oldShipID, ['form.InflightCargoView'])
        if session.stationid is not None and self.station is not None:
            self.ShowShip(shipID)



    def MakeModularShipFromShipItem(self, ship):
        subSystemIds = {}
        for fittedItem in ship.GetFittedItems().itervalues():
            if fittedItem.categoryID == const.categorySubSystem:
                subSystemIds[fittedItem.groupID] = fittedItem.typeID

        if len(subSystemIds) < const.visibleSubSystems:
            sm.GetService('window').GetWindow('AssembleShip', create=1, decoClass=form.AssembleShip, ship=ship, groupIDs=subSystemIds.keys())
            return 
        return sm.GetService('t3ShipSvc').GetTech3ShipFromDict(ship.typeID, subSystemIds)




class StationLayer(uicls.LayerCore):
    __guid__ = 'form.StationLayer'

    def OnCloseView(self):
        sm.GetService('station').CleanUp()



    def OnOpenView(self):
        pass




