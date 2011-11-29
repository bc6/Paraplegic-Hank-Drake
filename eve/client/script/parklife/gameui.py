from __future__ import with_statement
import uix
import uiconst
import uiutil
import uthread
import blue
import form
import util
import log
import moniker
import trinity
import sys
import service
import antiaddiction
import urllib2
import appUtils
import audioConst
import const
import ccUtil
import viewstate
from sceneManager import SCENE_TYPE_SPACE
from service import SERVICE_RUNNING
import localization
import localizationUtil
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L

class GameUI(service.Service):
    __guid__ = 'svc.gameui'
    __sessionparams__ = []
    __exportedcalls__ = {'StartupUI': [],
     'MessageBox': [],
     'Say': [],
     'GetShipAccess': [],
     'GetEntityAccess': [],
     'GetCurrentScope': []}
    __startupdependencies__ = ['device', 'settings']
    __dependencies__ = ['michelle', 'machoNet', 'inv']
    __notifyevents__ = ['OnConnectionRefused',
     'OnDisconnect',
     'OnServerMessage',
     'OnRemoteMessage',
     'DoSessionChanging',
     'ProcessSessionChange',
     'OnSessionChanged',
     'DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'OnNewState',
     'OnClusterShutdownInitiated',
     'OnClusterShutdownCancelled',
     'OnJumpQueueMessage',
     'ProcessActiveShipChanged']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.wannaBeEgo = -1
        self.languages = None
        self.shutdownTime = None
        self.startErrorMessage = None
        self.currentScope = []
        self.sceneManager = sm.GetService('sceneManager')
        audioConst.BTNCLICK_DEFAULT = 'click'
        defaults = {'debug': 0,
         'port': sm.services['machoNet'].defaultProxyPortOffset,
         'newbie': 1,
         'inputhost': 'localhost',
         'digit': ',',
         'decimal': '.',
         'eulaagreed': 0,
         'host': 0}
        for (k, v,) in defaults.items():
            if not prefs.HasKey(k):
                prefs.SetValue(k, v)

        self.uiLayerList = [('l_hint', None, None),
         ('l_menu', None, None),
         ('l_mloading', None, None),
         ('l_modal', None, [('l_systemmenu', form.SystemMenu, None)]),
         ('l_abovemain', None, None),
         ('l_loading', None, None),
         ('l_dragging', None, None),
         ('l_main', None, None),
         ('l_viewstate', None, None)]
        self.shipAccess = None
        self.state = SERVICE_RUNNING
        uthread.worker('gameui::ShutdownTimer', self._GameUI__ShutdownTimer)
        uthread.worker('gameui::SessionTimeoutTimer', self._GameUI__SessionTimeoutTimer)



    def GetShipAccess(self):
        if self.shipAccess is not None:
            (shipAccess, locationID, shipID, charID,) = self.shipAccess
            if locationID != eve.session.solarsystemid or eve.session.stationid:
                self.shipAccess = None
            elif shipID != eve.session.shipid:
                self.shipAccess = None
            elif charID != eve.session.charid:
                self.shipAccess = None
        if self.shipAccess is None:
            self.shipAccess = [moniker.GetShipAccess(),
             eve.session.solarsystemid or eve.session.stationid,
             eve.session.shipid,
             eve.session.charid]
        return self.shipAccess[0]



    def GetEntityAccess(self):
        return moniker.GetEntityAccess()



    def OnDisconnect(self, reason = 0, msg = ''):
        self.LogInfo('Received OnDisconnect with reason=', reason, ' and msg=', msg)
        if reason in (0, 1):
            self.LogWarn('GameUI::OnDisconnect', reason, msg)
            appUtils.Reboot('connection lost')



    def OnConnectionRefused(self):
        sm.GetService('loading').CleanUp()



    def OnServerMessage(self, msg):
        uthread.new(self.OnServerMessage_thread, msg).context = 'gameui.ServerMessage'



    def OnServerMessage_thread(self, msg):
        if isinstance(msg, tuple) and len(msg) == 2:
            (label, kwargs,) = msg
            msg = localization.GetByLabel(label, **kwargs)
        eve.Message('ServerMessage', {'msg': msg})



    def OnClusterShutdownInitiated(self, msg, when):
        self.shutdownTime = when
        eve.Message('CluShutdownInitiated', {'explanation': msg})



    def OnJumpQueueMessage(self, msg, ready):
        self.Say(msg)



    def OnClusterShutdownCancelled(self, msg):
        self.shutdownTime = None
        self.Say(localization.GetByLabel('UI/Shared/ClusterShutdownDelayed'))
        eve.Message('CluShutdownCancelled', {'explanation': msg})



    def __ShutdownTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if self.shutdownTime and self.shutdownTime - blue.os.GetWallclockTime() < 5 * MIN:
                    timeLeft = max(0L, self.shutdownTime - blue.os.GetWallclockTime())
                    self.Say(localization.GetByLabel('UI/Shared/ClusterShutdownInSeconds', timeLeft=timeLeft))
            except:
                log.LogException()
                sys.exc_clear()
            blue.pyos.synchro.SleepWallclock(5000)




    def __SessionTimeoutTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if eve.session.maxSessionTime and eve.session.maxSessionTime - blue.os.GetWallclockTime() < 15 * MIN:
                    self.Say(localization.GetByLabel('UI/Shared/MaxSessionTimeExpiring', timeLeft=eve.session.maxSessionTime - blue.os.GetWallclockTime()))
            except:
                log.LogException()
                sys.exc_clear()
            blue.pyos.synchro.SleepWallclock(5000)




    def OnRemoteMessage(self, msgID, dict = None, kw = {}):
        if msgID in ('SelfDestructInitiatedOther', 'SelfDestructImmediateOther', 'SelfDestructAbortedOther2') and not settings.user.ui.Get('notifyMessagesEnabled', 1):
            return 
        uthread.new(eve.Message, msgID, dict, **kw).context = 'gameui.ServerMessage'



    def TransitionCleanup(self, session, change):
        uicore.layer.menu.Flush()
        for each in uicore.registry.GetWindows()[:]:
            if hasattr(each, 'content') and getattr(each.content, '__guid__', None) == 'form.InflightCargoView' and each.id != session.shipid:
                if hasattr(each, 'Close'):
                    each.Close()
                else:
                    each.CloseByUser()
            if each.name.startswith('infowindow') and 'shipid' in change and each.sr.itemID in change['shipid']:
                each.Close()




    def ClearCacheFiles(self):
        if eve.Message('AskClearCacheReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.clearcache = 1
            appUtils.Reboot('clear cache')



    def ClearSettings(self):
        if eve.Message('AskClearSettingsReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.resetsettings = 1
            appUtils.Reboot('clear settings')



    def Stop(self, ms = None):
        service.Service.Stop(self, ms)



    def ProcessSessionChange(self, isRemote, session, change, cheat = 0):
        if 'shipid' in change and change['shipid'][0] and not session.stationid2:
            sm.GetService('invCache').CloseContainer(change['shipid'][0])
        self.settings.SaveSettings()
        self.LogInfo('ProcessSessionChange: ', change, ', ', session)
        if not isRemote:
            return 



    def DoSessionChanging(self, isRemote, session, change):
        self.TransitionCleanup(session, change)
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            self.shipAccess = None



    def AnythingImportantInChange(self, change):
        ignoreKeys = ('fleetid', 'wingid', 'squadid', 'fleetrole', 'languageID')
        ck = change.keys()
        for k in ignoreKeys:
            try:
                ck.remove(k)
            except ValueError:
                pass

        return bool(ck)



    def OnSessionChanged(self, isRemote, session, change):
        if not self.AnythingImportantInChange(change):
            return 
        ok = 0
        for each in ['userid',
         'charid',
         'solarsystemid',
         'stationid',
         'shipid',
         'worldspaceid']:
            if each in change:
                ok = 1
                break

        if not ok:
            return 
        viewSvc = sm.GetService('viewState')
        if 'userid' in change:
            sm.GetService('window').LoadUIColors()
            sm.GetService('tactical')
        if 'userid' in change or 'charid' in change:
            self.settings.LoadSettings()
        if 'shipid' in change and session.sessionChangeReason == 'selfdestruct':
            session.sessionChangeReason = 'board'
        if session.charid is None:
            antiaddiction.OnLogin()
            self.LogNotice('GameUI::OnSessionChanged, Heading for character selection', isRemote, session, change)
            postAuthMessage = sm.RemoteSvc('authentication').GetPostAuthenticationMessage()
            if postAuthMessage:
                self.MessageBox(postAuthMessage.message, '', uiconst.OK, None, None, None, 260)
            if sm.GetService('webtools').GetVars():
                return 
            if settings.public.generic.Get('showintro2', None) is None:
                settings.public.generic.Set('showintro2', prefs.GetValue('showintro2', 1))
            if settings.public.generic.Get('showintro2', 1):
                uthread.pool('GameUI::ActivateView::intro', viewSvc.ActivateView, 'intro')
            else:
                characters = sm.GetService('cc').GetCharactersToSelect(False)
                if characters:
                    uthread.pool('GameUI::ActivateView::charsel', viewSvc.ActivateView, 'charsel')
                else:
                    uthread.pool('GameUI::GoCharacterCreation', self.GoCharacterCreation)
        elif session.stationid is not None:
            if 'stationid' in change:
                self.LogNotice('GameUI::OnSessionChanged, Heading for station', isRemote, session, change)
                activateViewFunc = viewSvc.ActivateView if viewSvc.IsViewActive('charactercreation') else viewSvc.ChangePrimaryView
                view = settings.user.ui.Get('defaultDockingView', 'station')
                if view == 'station' and not prefs.GetValue('loadstationenv2', 1):
                    self.LogInfo('Docking into hangar because we have disabled the station environments')
                    view = 'hangar'
                uthread.pool('GameUI::ActivateView::station', activateViewFunc, view, change=change)
        elif session.worldspaceid is not None:
            if 'worldspaceid' in change:
                self.LogWarn('GameUI::OnSessionChanged, Heading for worldspace', isRemote, session, change)
                activateViewFunc = viewSvc.ActivateView if viewSvc.IsViewActive('charactercreation') else viewSvc.ChangePrimaryView
                uthread.pool('GameUI::ActivateView::station', activateViewFunc, 'station', change=change)
        elif session.solarsystemid is not None:
            if 'solarsystemid' in change:
                (oldSolarSystemID, newSolarSystemID,) = change['solarsystemid']
                if oldSolarSystemID:
                    sm.GetService('FxSequencer').ClearAll()
                    self.LogInfo('Cleared effects')
                self.LogNotice('GameUI::OnSessionChanged, Heading for inflight', isRemote, session, change)
                uthread.pool('GameUI::ChangePrimaryView::inflight', viewSvc.ChangePrimaryView, 'inflight', change=change)
            elif 'shipid' in change and change['shipid'][1] is not None:
                michelle = sm.GetService('michelle')
                bp = michelle.GetBallpark()
                if bp:
                    if change['shipid'][0]:
                        self.KillCargoView(change['shipid'][0])
                    uthread.new(sm.GetService('target').ClearTargets)
                    if session.shipid in bp.balls:
                        self.LogInfo('Changing ego:', bp.ego, '->', session.shipid)
                        bp.ego = session.shipid
                        self.OnNewState(bp, localization.GetByLabel('UI/Inflight/BoardingShip'))
                    else:
                        self.LogInfo('Postponing ego:', bp.ego, '->', session.shipid)
                    self.wannaBeEgo = session.shipid
        else:
            self.LogWarn('GameUI::OnSessionChanged, Lame Teardown of the client, it should get propper OnDisconnect event', isRemote, session, change)
            self.ScopeCheck()



    def KillCargoView(self, id_, guidsToKill = None):
        if guidsToKill is None:
            guidsToKill = ('form.DockedCargoView', 'form.InflightCargoView', 'form.LootCargoView', 'form.DroneBay', 'form.CorpHangar', 'form.ShipCorpHangars', 'form.CorpHangarArray', 'form.SpecialCargoBay', 'form.PlanetInventory')
        for each in uicore.registry.GetWindows()[:]:
            if getattr(each, '__guid__', None) in guidsToKill and getattr(each, 'itemID', None) == id_:
                if not each.destroyed:
                    if hasattr(each, 'Close'):
                        each.Close()
                    else:
                        each.CloseByUser()




    def ScopeCheck(self, scope = []):
        scope += ['all']
        self.currentScope = scope
        for each in uicore.registry.GetWindows()[:]:
            if getattr(each, 'content', None) and hasattr(each.content, 'scope') and each.content.scope:
                if each.content.scope not in scope:
                    if each is not None and not each.destroyed:
                        if hasattr(each, 'Close'):
                            self.LogInfo('ScopeCheck::Close', each.name, 'scope', scope)
                            each.Close()
                        else:
                            self.LogInfo('ScopeCheck::Close', each.name, 'scope', scope)
                            each.CloseByUser()
            elif hasattr(each, 'scope') and each.scope not in scope:
                if each is not None and not each.destroyed:
                    if hasattr(each, 'Close'):
                        self.LogInfo('ScopeCheck::Close2', each.name, 'scope', scope)
                        each.Close()
                    else:
                        self.LogInfo('ScopeCheck::Close2', each.name, 'scope', scope)
                        each.CloseByUser()




    def GetCurrentScope(self):
        return self.currentScope



    def StartupUI(self, *args):
        if boot.region == 'optic':
            url = 'http://www.eve-online.com.cn'
        else:
            url = 'http://www.eveonline.com'
        url = url + '/firewallcheck.htm'
        try:
            urllib2.urlopen(url)
        except:
            sys.exc_clear()
        trinity.device.legacyModeEnabled = False
        uicore.Startup(self.uiLayerList)
        uicore.Message = eve.Message
        uiutil.AskName = uix.NamePopup
        log.SetUiMessageFunc(uicore.Message)
        trinity.device.scene = None
        if blue.win32.IsTransgaming():
            sm.StartService('cider')
        self.SetupViewStates()
        sm.GetService('device').SetupUIScaling()
        sceneManager = sm.StartService('sceneManager')
        sceneManager.SetSceneType(SCENE_TYPE_SPACE)
        sceneManager.Initialize(trinity.device.scene, trinity.EveSpaceScene(), None)
        sm.StartService('connection')
        sm.StartService('damage')
        sm.StartService('logger')
        sm.StartService('vivox')
        sm.StartService('ownerprimer')
        sm.StartService('petition')
        sm.StartService('ui')
        sm.StartService('window')
        sm.StartService('log')
        sm.StartService('z')
        sm.StartService('consider')
        sm.StartService('incursion')
        sm.StartService('cameraClient')
        sm.StartService('moonScan')
        if blue.win32:
            try:
                blue.win32.WTSRegisterSessionNotification(trinity.device.GetWindow(), 0)
                uicore.uilib.SessionChangeHandler = self.OnWindowsUserSessionChange
            except:
                sys.exc_clear()
                uicore.uilib.SessionChangeHandler = None
        rebootReason = settings.public.generic.Get('rebootReason', None)
        rebootTime = settings.public.generic.Get('rebootTime', blue.os.GetWallclockTime())
        if rebootReason == 'connection lost' and blue.os.GetWallclockTime() - rebootTime < MIN:
            sm.GetService('viewState').ActivateView('login', connectionLost=True)
        else:
            pr = sm.GetService('webtools').GetVars()
            if pr:
                sm.GetService('webtools').GoSlimLogin()
            else:
                sm.GetService('viewState').ActivateView('login')
                if self.startErrorMessage:
                    eve.Message(self.startErrorMessage)
                    self.startErrorMessage = None
        settings.public.generic.Set('rebootReason', '')



    def SetupViewStates(self):
        viewSvc = sm.GetService('viewState')
        viewSvc.Initialize(uicore.layer.viewstate)
        viewSvc.AddView('login', viewstate.LoginView())
        viewSvc.AddView('intro', viewstate.IntroView())
        viewSvc.AddView('charsel', viewstate.CharacterSelectorView())
        viewSvc.AddView('inflight', viewstate.SpaceView())
        viewSvc.AddView('station', viewstate.CQView())
        viewSvc.AddView('hangar', viewstate.HangarView())
        viewSvc.AddView('starmap', viewstate.StarMapView(), viewType=viewstate.ViewType.Secondary)
        viewSvc.AddView('systemmap', viewstate.SystemMapView(), viewType=viewstate.ViewType.Secondary)
        viewSvc.AddView('planet', viewstate.PlanetView(), viewType=viewstate.ViewType.Secondary)
        viewSvc.AddView('charactercreation', viewstate.CharacterCustomizationView(), viewType=viewstate.ViewType.Secondary)
        viewSvc.AddTransition(None, 'login')
        viewSvc.AddTransitions(('login',), ('intro', 'charsel', 'charactercreation'), viewstate.FadeToBlackTransition(fadeTimeMS=250))
        viewSvc.AddTransitions(('intro',), ('charsel', 'charactercreation'), viewstate.FadeToBlackLiteTransition(fadeTimeMS=250))
        viewSvc.AddTransitions(('charsel',), ('inflight', 'charactercreation', 'hangar'), viewstate.FadeToBlackTransition(fadeTimeMS=250))
        viewSvc.AddTransitions(('charactercreation',), ('hangar', 'charsel'), viewstate.FadeToBlackTransition(fadeTimeMS=250, allowReopen=False))
        viewSvc.AddTransitions(('inflight', 'hangar', 'starmap', 'systemmap', 'planet'), ('hangar', 'starmap', 'systemmap', 'planet', 'inflight'), viewstate.FadeToBlackLiteTransition(fadeTimeMS=100))
        viewSvc.AddTransition('inflight', 'inflight', viewstate.SpaceToSpaceTransition(fadeTimeMS=100))
        viewSvc.AddTransition('starmap', 'starmap')
        viewSvc.AddTransitions(('station',), ('hangar', 'starmap', 'systemmap', 'planet'), viewstate.FadeToBlackLiteTransition(fadeTimeMS=100))
        viewSvc.AddTransitions(('inflight', 'starmap', 'systemmap', 'planet', 'charsel', 'hangar', 'charactercreation', 'station'), ('station',), viewstate.FadeToCQTransition(fadeTimeMS=200))
        viewSvc.AddTransitions(('station', 'hangar', 'starmap', 'systemmap'), ('charactercreation',), viewstate.FadeToBlackTransition(fadeTimeMS=200))
        viewSvc.AddTransition('charactercreation', 'station', viewstate.FadeFromCharRecustomToCQTransition(fadeTimeMS=250))
        viewSvc.AddTransition('station', 'inflight', viewstate.FadeFromCQToSpaceTransition(fadeTimeMS=250))
        viewSvc.AddOverlay('neocom', None)
        viewSvc.AddOverlay('shipui', form.ShipUI)
        viewSvc.AddOverlay('target', None)
        viewSvc.AddOverlay('stationEntityBrackets', None)



    def SetLanguage(self, key):
        if boot.region == 'optic' and not eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            key = 'ZH'
        convertedKey = localizationUtil.ConvertToLanguageSet('MLS', 'languageID', key)
        if convertedKey in localization.GetLanguages() and key != prefs.languageID:
            if session.userid is not None:
                sm.RemoteSvc('authentication').SetLanguageID(key)
            else:
                session.__dict__['languageID'] = key
            prefs.languageID = key
            localization.LoadSecondaryLanguage(key)
            sm.ChainEvent('ProcessUIRefresh')
            sm.ScatterEvent('OnUIRefresh')



    def HasActiveOverlay(self):
        return sm.IsServiceRunning('viewState') and sm.GetService('viewState').IsCurrentViewSecondary()



    def GoLogin(self, step = 1, connectionLost = 0, *args):
        blue.statistics.SetTimelineSectionName('login')
        if self.sceneManager.scene1 is not None:
            self.sceneManager.scene1.display = False
        login = uicore.layer.login
        if connectionLost:
            uthread.new(eve.Message, 'ConnectionLost', {'what': ''})



    def GoCharacterCreationCurrentCharacter(self, *args):
        if None in (session.charid, session.genderID, session.bloodlineID):
            return 
        if sm.GetService('viewState').IsViewActive('charactercreation'):
            return 
        stationSvc = sm.GetService('station')
        dollState = stationSvc.GetPaperdollStateCache()
        msg = None
        if dollState == const.paperdollStateResculpting:
            msg = 'AskRecustomizeCharacter'
        elif dollState == const.paperdollStateFullRecustomizing:
            msg = 'AskRecustomizeCharacterChangeBloodline'
        message = uiconst.ID_NO
        if msg is not None:
            message = eve.Message(msg, {'charName': cfg.eveowners.Get(session.charid).ownerName}, uiconst.YESNO, default=uiconst.ID_NO, suppress=uiconst.ID_NO)
        if message == uiconst.ID_YES:
            self.GoCharacterCreation(session.charid, session.genderID, session.bloodlineID, dollState=dollState)
            stationSvc.ClearPaperdollStateCache()
        elif message == uiconst.ID_NO:
            self.GoCharacterCreation(session.charid, session.genderID, session.bloodlineID, dollState=const.paperdollStateNoRecustomization)



    def GoCharacterCreation(self, charID = None, gender = None, bloodlineID = None, askUseLowShader = True, dollState = None, *args):
        if sm.GetService('station').exitingstation:
            return 
        if askUseLowShader:
            msg = uiconst.ID_YES
            if not sm.StartService('device').SupportsSM3():
                msg = eve.Message('AskMissingSM3', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg != uiconst.ID_YES:
                return 
            msg = uiconst.ID_YES
            if ccUtil.SupportsHigherShaderModel():
                msg = eve.Message('AskUseLowShader', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg != uiconst.ID_YES:
                return 
        sm.GetService('viewState').ActivateView('charactercreation', charID=charID, gender=gender, bloodlineID=bloodlineID, dollState=dollState)



    def MessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, height = None, blockconfirmonreturn = 0, default = None, modal = True):
        if not getattr(uicore, 'desktop', None):
            return 
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = form.MessageBox.Open(useDefaultPos=True)
        msgbox.state = uiconst.UI_HIDDEN
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        msgbox.Execute(text, title, buttons, icon, suppText, customicon, height, default=default, modal=modal)
        if modal:
            ret = msgbox.ShowModal()
        else:
            ret = msgbox.ShowDialog()
        return (ret, msgbox.suppress)



    def RadioButtonMessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, radioOptions = [], height = None, width = None, blockconfirmonreturn = 0, default = None, modal = True):
        if not getattr(uicore, 'desktop', None):
            return 
        if buttons is None:
            buttons = uiconst.ID_OK
        msgbox = form.RadioButtonMessageBox.Open(useDefaultPos=True)
        msgbox.isModal = modal
        msgbox.blockconfirmonreturn = blockconfirmonreturn
        msgbox.Execute(text, title, buttons, radioOptions, icon, suppText, customicon, height, width=width, default=default, modal=modal)
        if modal:
            buttonResult = msgbox.ShowModal()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        else:
            buttonResult = msgbox.ShowDialog()
            radioSelection = msgbox.GetRadioSelection()
            ret = (buttonResult, radioSelection)
        return (ret, msgbox.suppress)



    def Say(self, msgtext, time = 100):
        uicore.Say(msgtext, time)



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::gameui')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, lst):
        for each in lst:
            self.DoBallAdd(*each)




    def DoBallAdd(self, ball, slimItem):
        if ball.id == self.wannaBeEgo:
            bp = sm.GetService('michelle').GetBallpark()
            self.LogInfo('Post-ego change: ', bp.ego, '->', self.wannaBeEgo)
            bp.ego = self.wannaBeEgo
            self.wannaBeEgo = -1
            self.OnNewState(bp, localization.GetByLabel('UI/Inflight/BoardingShip'))



    def DoBallRemove(self, ball, slimItem, terminal):
        if not slimItem or slimItem.itemID is None or slimItem.itemID < 0:
            return 
        self.LogInfo('DoBallRemove::gameui', slimItem.itemID)
        self.CheckIfCargo(slimItem)



    def DoBallClear(self, solItem):
        uthread.new(self._DoBallClear, solItem)



    def _DoBallClear(self, solItem):
        sm.GetService('tactical').TearDownOverlay()
        sc = self.sceneManager.GetScene()
        self.sceneManager.UnregisterScene('default')
        self.sceneManager.UnregisterScene2('default')
        self.sceneManager.UnregisterCamera('default')
        self.sceneManager.LoadScene(sc, sc, inflight=1, registerKey='default')
        if eve.session.solarsystemid:
            sm.GetService('tactical').CheckInit()



    def CheckIfCargo(self, slimItem):
        if slimItem is None:
            return 
        import __builtin__
        if not hasattr(__builtin__, 'const'):
            return 
        groupsToClose = (const.groupControlTower,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupConstructionPlatform,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer,
         const.groupWreck,
         const.groupStationUpgradePlatform,
         const.groupStationImprovementPlatform,
         const.groupPlanetaryCustomsOffices,
         const.groupInfrastructureHub)
        if slimItem.groupID in groupsToClose:
            self._CloseInvWindow(slimItem.itemID)



    def _CloseInvWindow(self, invID):
        for each in uicore.registry.GetWindows()[:]:
            if each.windowID in ['shipCargo_%s' % eve.session.shipid, 'drones_%s' % eve.session.shipid]:
                continue
            if hasattr(each, 'id') and each.id == invID:
                if hasattr(each, 'Close'):
                    each.Close()
                else:
                    each.CloseByUser()




    def CacheCameraTranslation(self, inflight = 0):
        camera = self.sceneManager.GetRegisteredCamera('default')
        if camera and eve.session.shipid:
            self.SetCachedCameraTranslation((eve.session.shipid, inflight), camera.translationFromParent.z)



    def GetCachedCameraTranslation(self, id):
        c = settings.user.ui.Get('cachedCamTranslations', {})
        return c.get(id, None)



    def SetCachedCameraTranslation(self, id, translation):
        c = settings.user.ui.Get('cachedCamTranslations', {})
        c[id] = translation
        settings.user.ui.Set('cachedCamTranslations', c)



    def TogglePostProcess(self, mode):
        if sm.GetService('device').IsHdrEnabled():
            if mode is None or mode in ('starmap', 'systemmap'):
                trinity.device.postProcess.display = 0
            else:
                trinity.device.postProcess.display = 1



    def OnNewState(self, bp, hint = None):
        uthread.pool('GameUI::New shipui state', self._NewState, bp, hint)



    def _NewState(self, bp, hint):
        if hint:
            sm.GetService('loading').ProgressWnd(hint, localization.GetByLabel('UI/Shared/CheckingNavigationSystems'), 5, 6)
        else:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Inflight/EnteringSpace'), localization.GetByLabel('UI/Shared/CheckingNavigationSystems'), 5, 6)
        blue.pyos.synchro.Yield()
        if bp and bp.balls.get(bp.ego, None):
            sm.GetService('camera').LookAt(bp.ego, self.GetCachedCameraTranslation((eve.session.shipid, 1)))
            if session.solarsystemid:
                uicore.layer.shipui.OnOpenView()
                uicore.layer.shipui.Init(bp.balls.get(bp.ego, None))
        if hint:
            sm.GetService('loading').ProgressWnd(hint, localization.GetByLabel('UI/Shared/CheckingNavigationSystems'), 6, 6)
        else:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Inflight/EnteringSpace'), localization.GetByLabel('UI/Shared/CheckingNavigationSystems'), 6, 6)
        blue.pyos.synchro.Yield()



    def DoWindowIdentification(self):
        triapp = trinity.app
        if eve.session.charid and settings.user.ui.Get('windowidentification', 0):
            charName = cfg.eveowners.Get(eve.session.charid).name
            triapp.title = '%s - %s' % (uicore.triappargs['title'], charName)
        else:
            trinity.app.title = uicore.triappargs['title']



    def OnWindowsUserSessionChange(self, wp, lp):
        audio = sm.GetService('audio')
        if wp == 1:
            sm.GetService('vivox').OnSessionReconnect()
            if audio.IsActivated() and audio.GetMasterVolume() > 0.0:
                audio.SetMasterVolume(audio.GetMasterVolume(), persist=True)
        elif wp == 2:
            sm.GetService('vivox').OnSessionDisconnect()
            if audio.IsActivated() and audio.GetMasterVolume() > 0.0:
                audio.SetMasterVolume(0.0, persist=False)



    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if oldShipID:
            self.KillCargoView(oldShipID)




