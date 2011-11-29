import turret
import sys
import service
import uix
import uiutil
import uthread
import blue
import form
import log
import trinity
import util
import uicls
import uiconst
import localization

class StationSvc(service.Service):
    __guid__ = 'svc.station'
    __sessionparams__ = []
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetGuests': [],
     'IsGuest': [],
     'Setup': [],
     'Exit': [],
     'GetSvc': [],
     'LoadSvc': [],
     'GiveHint': [],
     'ClearHint': [],
     'GetStationServiceInfo': [],
     'StopAllStationServices': [],
     'CleanUp': [],
     'SelectShipDlg': [],
     'GetServiceState': []}
    __dependencies__ = ['journal', 'insurance', 't3ShipSvc']
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnStationOwnerChanged',
     'OnDogmaItemChange',
     'ProcessStationServiceItemChange',
     'ProcessSessionChange',
     'OnCharacterHandler',
     'OnDogmaAttributeChanged',
     'OnSessionChanged',
     'OnActiveShipModelChange']

    def Run(self, memStream = None):
        self.LogInfo('Starting Station Service')
        self.CleanUp()



    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change:
            (oldLocation, newLocation,) = change['locationid']
            if util.IsStation(oldLocation):
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
        uthread.pool('StationSvc::OnStationOwnerChanged --> LoadLobby', self.ReloadLobby)



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
        if len(self.guests) == 0:
            guests = sm.RemoteSvc('station').GetGuests()
            for (charID, corpID, allianceID, warFactionID,) in guests:
                self.guests[charID] = (corpID, allianceID, warFactionID)

        return self.guests



    def IsGuest(self, whoID):
        if len(self.guests) == 0:
            self.GetGuests()
        return whoID in self.guests



    def Stop(self, memStream = None):
        self.LogInfo('Stopping Station Service')
        self.CleanUp()



    def CheckSession(self, change):
        if self.activeShip != eve.session.shipid:
            if eve.session.shipid:
                hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
                hangarItems = hangarInv.List()
                for each in hangarItems:
                    if each.itemID == eve.session.shipid:
                        self.activeShipItem = each
                        break




    def GetStation(self):
        self.station = sm.GetService('ui').GetStation(eve.session.stationid)



    def GetStationServiceInfo(self, sortBy = None, stationInfo = None):
        if not self.station and eve.session.stationid:
            self.GetStation()
        services = []
        for (service, info,) in self.GetStationServices().iteritems():
            sortItem = info.index
            if sortBy == 'name':
                sortItem = info.label
            services.append(((sortItem, service), info))

        services = uiutil.SortListOfTuples(services)
        return services



    def GetServiceDisplayName(self, service):
        s = self.GetStationServices(service)
        if s:
            return s.label
        return localization.GetByLabel('UI/Common/Unknown')



    def GetStationServices(self, service = None):
        mapping = [util.KeyVal(name='vstore', command='OpenStore', label=localization.GetByLabel('UI/Station/VirtualGoodsStore'), iconID='65_3', scope=const.neocomButtonScopeStation, serviceIDs=(-1,)),
         util.KeyVal(name='charcustomization', command='OpenCharacterCustomization', label=localization.GetByLabel('UI/Station/CharacterRecustomization'), iconID='66_3', scope=const.neocomButtonScopeStation, serviceIDs=(-1,)),
         util.KeyVal(name='medical', command='OpenMedical', label=localization.GetByLabel('UI/Medical/Medical'), iconID='ui_18_128_3', scope=const.neocomButtonScopeStation, serviceIDs=(const.stationServiceCloning, const.stationServiceSurgery, const.stationServiceDNATherapy)),
         util.KeyVal(name='repairshop', command='OpenRepairshop', label=localization.GetByLabel('UI/Station/Repairshop'), iconID='ui_18_128_4', scope=const.neocomButtonScopeStation, serviceIDs=(const.stationServiceRepairFacilities,)),
         util.KeyVal(name='reprocessingPlant', command='OpenReprocessingPlant', label=localization.GetByLabel('UI/Station/ReprocessingPlant'), iconID='ui_17_128_1', scope=const.neocomButtonScopeStation, serviceIDs=(const.stationServiceReprocessingPlant,)),
         util.KeyVal(name='market', command='OpenMarket', label=localization.GetByLabel('UI/Station/Market'), iconID='ui_18_128_1', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceMarket,)),
         util.KeyVal(name='fitting', command='OpenFitting', label=localization.GetByLabel('UI/Station/Fitting'), iconID='ui_17_128_4', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceFitting,)),
         util.KeyVal(name='factories', command='OpenScienceAndIndustry', label=localization.GetByLabel('UI/Station/ScienceAndIndustry'), iconID='57_9', scope=const.neocomButtonScopeStation, serviceIDs=(const.stationServiceFactory, const.stationServiceLaboratory)),
         util.KeyVal(name='missions', command='OpenMissions', label=localization.GetByLabel('UI/Station/BountyOffice/BountyOffice'), iconID='61_2', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceBountyMissions, const.stationServiceAssassinationMissions)),
         util.KeyVal(name='navyoffices', command='OpenMilitia', label=localization.GetByLabel('UI/Station/MilitiaOffice'), iconID='61_3', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceNavyOffices,)),
         util.KeyVal(name='insurance', command='OpenInsurance', label=localization.GetByLabel('UI/Station/Insurance'), iconID='33_4', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceInsurance,)),
         util.KeyVal(name='lpstore', command='OpenLpstore', label=localization.GetByLabel('UI/Station/LPStore'), iconID='ui_70_128_11', scope=const.neocomButtonScopeStationOrWorldspace, serviceIDs=(const.stationServiceLoyaltyPointStore,))]
        newmapping = {}
        for (i, info,) in enumerate(mapping):
            info.index = i
            newmapping[info.name] = info

        if service:
            return newmapping.get(service, None)
        return newmapping



    def CheckHasStationService(self, service, serviceMask):
        pass



    def CleanUp(self, storeCamera = 1):
        try:
            if getattr(self, 'underlay', None):
                uicore.registry.UnregisterWindow(self.underlay)
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
        self.refreshingfitting = False
        self.activeShip = None
        self.activeShipItem = None
        self.activeshipmodel = None
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



    def StopAllStationServices(self):
        services = self.GetStationServiceInfo()
        for service in services:
            if sm.IsServiceRunning(service.name):
                sm.services[service.name].Stop()




    def Setup(self, reloading = 0):
        self.CleanUp(0)
        self.loading = 1
        if not reloading:
            eve.Message('OnEnterStation')
        if self.station is None and eve.session.stationid:
            self.station = sm.GetService('ui').GetStation(eve.session.stationid)
        sm.GetService('autoPilot').SetOff('toggled by Station Entry')
        if sm.GetService('viewState').IsViewActive('starmap', 'systemmap'):
            sm.StartService('map').MinimizeWindows()
        if sm.GetService('viewState').IsViewActive('planet'):
            sm.GetService('planetUI').MinimizeWindows()
        self.loading = 0
        self.sprite = None
        if not reloading:
            if util.GetActiveShip() is None:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningWhenPoddedTutorial)
            if sm.GetService('skills').GetSkillPoints() >= 1500000:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.cloningTutorial)



    def GetPaperdollStateCache(self):
        if self.paperdollState is None:
            self.paperdollState = sm.RemoteSvc('charMgr').GetPaperdollState()
        return self.paperdollState



    def OnCharacterHandler(self):
        self.ClearPaperdollStateCache()



    def ClearPaperdollStateCache(self):
        self.paperdollState = None



    def BlinkButton(self, what):
        lobby = form.Lobby.GetIfOpen()
        if lobby:
            lobby.BlinkButton(what)



    def DoPOSWarning(self):
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            eve.Message('POStationWarning')



    def TryActivateShip(self, invitem, onSessionChanged = 0, secondTry = 0):
        shipid = invitem.itemID
        if shipid == self.activeShip:
            return 
        if self.activatingShip:
            return 
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogmaLocation.CheckSkillRequirementsForType(invitem.typeID, 'ShipHasSkillPrerequisites')
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




    def GetTech3ShipFromSlimItem(self, slimItem):
        subSystemIds = {}
        for module in slimItem.modules:
            if module.categoryID == const.categorySubSystem:
                subSystemIds[module.groupID] = module.typeID

        if len(subSystemIds) < const.visibleSubSystems:
            form.AssembleShip.Open(windowID='AssembleShip', ship=slimItem, groupIDs=subSystemIds.keys())
            return 
        return self.t3ShipSvc.GetTech3ShipFromDict(slimItem.typeID, subSystemIds)



    def FindHierarchicalBoundingBox(self, transform, printout, indent = '', minx = 1e+100, maxx = -1e+100, miny = 1e+100, maxy = -1e+100, minz = 1e+100, maxz = -1e+100):
        transform.Update(blue.os.GetSimTime())
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



    def OnActiveShipModelChange(self, model, shipID):
        self.activeShip = shipID
        self.activeshipmodel = model
        self.FitHardpoints()



    def FitHardpoints(self):
        if not self.activeshipmodel or self.refreshingfitting:
            return 
        self.refreshingfitting = True
        activeShip = util.GetActiveShip()
        turret.TurretSet.FitTurrets(activeShip, self.activeshipmodel)
        self.refreshingfitting = False



    def ModuleListFromGodmaSlimItem(self, slimItem):
        list = []
        for module in slimItem.modules:
            list.append((module.itemID, module.typeID))

        list.sort()
        return list



    def GetUnderlay(self):
        if self.underlay is None:
            for each in uicore.layer.main.children[:]:
                if each is not None and not each.destroyed and each.name == 'services':
                    uicore.registry.UnregisterWindow(each)
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
            self.closeBtn = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/CmdClose'),
              self.CloseSvc,
              None,
              81]], parent=sub)
            self.sr.underlay = uicls.WindowUnderlay(parent=main)
            self.sr.underlay.SetPadding(-1, -10, -1, 0)
            svcparent = uicls.Container(name='serviceparent', parent=sub, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.underlay.sr.main = main
            self.underlay.sr.svcparent = svcparent
            self.underlay.sr.caption = caption
            uicore.registry.RegisterWindow(self.underlay)
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
            self.ExecuteCommand(serviceInfo.command)
            return 
        if getattr(self, 'loadingSvc', 0):
            return 
        self.loadingSvc = 1
        while self.loading:
            blue.pyos.synchro.SleepWallclock(500)

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



    def ReloadLobby(self):
        form.Lobby.CloseIfOpen()
        form.Lobby.Open()



    def _LoadSvc(self, inout, service = None):
        self.loading = 1
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
        blue.pyos.synchro.SleepWallclock([750, 1250][inout])
        if inout == 0:
            sm.GetService('neocom').SetLocationInfoState(1)
        if newsvc is not None:
            if svctype == 'form':
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
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Station/AbortUndock'), '', 1, 1)
        self.dockaborted = 1
        self.exitingstation = 0
        self.ReloadLobby()
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
        sm.GetService('uipointerSvc').ClearPointers()
        msg = [(localization.GetByLabel('UI/Station/PrepareToUndock'), localization.GetByLabel('UI/Station/RequestingUndockPermission')),
         (localization.GetByLabel('UI/Station/PrepareToUndock'), localization.GetByLabel('UI/Station/WaitingForConfirmation')),
         (localization.GetByLabel('UI/Station/PrepareToUndock'), localization.GetByLabel('UI/Station/UndockingConfirmed')),
         (localization.GetByLabel('UI/Station/EnteringSpace'), localization.GetByLabel('UI/Station/PreparingShip')),
         (localization.GetByLabel('UI/Station/EnteringSpace'), localization.GetByLabel('UI/Station/ShipReady'))]
        minSleepTime = max(len(msg) * 1000, ((eve.session.nextSessionChange or 0.0) - blue.os.GetSimTime()) / (SEC / 1000)) / len(msg)
        for i in xrange(len(msg)):
            if self.dockaborted:
                self.exitingstation = 0
                break
            sm.GetService('loading').ProgressWnd(msg[i][0], msg[i][1], i + 1, len(msg) + 1, abortFunc=self.AbortUndock)
            blue.pyos.synchro.SleepSim(minSleepTime)

        blue.pyos.synchro.SleepSim(1000)
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
        try:
            shipsvc = sm.GetService('gameui').GetShipAccess()
            undockingLogLabel = localization.GetByLabel('UI/Station/UndockingFromStationToSystem', fromStation=eve.session.stationid2, toSystem=eve.session.solarsystemid2)
            sm.GetService('logger').AddText(undockingLogLabel)
            if observedSuppressed:
                ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            onlineModules = sm.GetService('clientDogmaIM').GetDogmaLocation().GetOnlineModules(shipID)
            try:
                sm.GetService('sessionMgr').PerformSessionChange('undock', shipsvc.Undock, shipID, ignoreContraband, onlineModules=onlineModules)
            except UserError as e:
                if e.msg == 'ShipNotInHangar':
                    capsuleID = e.dict.get('capsuleID', None)
                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    if capsuleID is not None:
                        dogmaLocation.MakeShipActive(capsuleID)
                    raise 
                elif e.msg == 'ShipContrabandWarningUndock':
                    if eve.Message(e.msg, e.dict, uiconst.OKCANCEL) == uiconst.ID_OK:
                        sys.exc_clear()
                        self.DoUndockAttempt(True, False, shipID)
                        return 
                    else:
                        settings.user.suppress.Set('suppress.ShipContrabandWarningUndock', None)
                        self.AbortUndock()
                        return 
                else:
                    raise 
            self.CloseFitting()
        except Exception as e:
            self.AbortUndock()
            raise 
        self.exitingstation = 0
        self.hangarScene = None



    def CloseFitting(self):
        form.FittingWindow.CloseIfOpen()



    def ShipPicker(self):
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List()
        tmplst = []
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((cfg.invtypes.Get(item[const.ixTypeID]).name, item[const.ixItemID], item[const.ixTypeID]))

        ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
        if ret is None:
            return 
        return ret[1]



    def SelectShipDlg(self):
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List()
        tmplst = []
        activeShipID = util.GetActiveShip()
        for item in items:
            if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
                tmplst.append((cfg.invtypes.Get(item[const.ixTypeID]).name, item, item[const.ixTypeID]))

        if not tmplst:
            self.exitingstation = 0
            eve.Message('NeedShipToUndock')
            return 
        ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
        if ret is None or ret[1].itemID == activeShipID:
            self.exitingstation = 0
            return 
        newActiveShip = ret[1]
        try:
            self.TryActivateShip(newActiveShip)
        except:
            self.exitingstation = 0
            raise 



    def ChangeColorOfActiveShip(self, typeName, colorID, typeID):
        self.previewColorIDs[typeName] = colorID
        self.t3ShipSvc.ChangeColor(self.activeshipmodel, self.previewColorIDs, typeID)



    def ConfirmChangeColor(self):
        if self.previewColorIDs is None:
            return 
        sm.GetService('invCache').GetInventoryFromId(self.activeShip).ChangeColor(self.previewColorIDs)
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






class StationLayer(uicls.LayerCore):
    __guid__ = 'form.StationLayer'

    def OnCloseView(self):
        sm.GetService('station').CleanUp()



    def OnOpenView(self):
        pass




