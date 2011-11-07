from __future__ import with_statement
import uix
import uiutil
import uiconst
import uthread
import blue
import form
import michelle
import xtriui
import util
import types
import traceback
import log
import moniker
import trinity
import audio2
import sys
import service
import os
import errno
import antiaddiction
import dbg
import urllib2
import appUtils
import nodemanager
import audioConst
import locks
import paperDoll
import geo2
import const
import uicls
import entities
import bluepy
import ccUtil
from sceneManager import SCENE_TYPE_SPACE
from sceneManager import SCENE_TYPE_INTERIOR
from sceneManager import SCENE_TYPE_CHARACTER_CREATION
from service import SERVICE_RUNNING
globals().update(service.consts)
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
     'GoCharacterSelection': [],
     'GoCharacterCreation': [],
     'GoIntro': [],
     'GoWorldSpace': [],
     'GetLanguages': [],
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
     'OnJumpQueueMessage']

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
         ('l_tabs', None, None),
         ('l_main', None, None),
         ('l_exclusive', None, [('l_login', form.LoginII, None),
           ('l_intro', form.Intro, None),
           ('l_charsel', form.CharSelection, None),
           ('l_newneocom', None, None),
           ('l_charactercreation', uicls.CharacterCreationLayer, None),
           ('l_neocom', None, None),
           ('l_station', form.StationLayer, None),
           ('l_inflight', form.SpaceLayer, [('l_shipui', form.ShipUI, None),
             ('l_bracket', None, None),
             ('l_target', None, None),
             ('l_tactical', None, None)]),
           ('l_charControl', uicls.CharControl, None)]),
         ('l_map', None, None),
         ('l_systemmap', None, None),
         ('l_planet', None, None)]
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
            if settings.user.ui.Get('rebootOnDisconnect', 1):
                appUtils.Reboot('connection lost')
            elif msg and reason == 0:
                uthread.new(eve.Message, 'GPSTransportClosed', {'what': msg})
            uicore.LoadLayers(self.uiLayerList)
            self.GoLogin(step=2, connectionLost=reason == 0)



    def OnConnectionRefused(self, msg):
        sm.GetService('loading').CleanUp()



    def OnServerMessage(self, msg):
        uthread.new(self.OnServerMessage_thread, msg).context = 'gameui.ServerMessage'



    def OnServerMessage_thread(self, msg):
        eve.Message('ServerMessage', {'msg': msg})



    def OnClusterShutdownInitiated(self, msg, when):
        self.shutdownTime = when
        eve.Message('CluShutdownInitiated', {'explanation': msg})



    def OnJumpQueueMessage(self, msg, ready):
        self.Say(msg)



    def OnClusterShutdownCancelled(self, msg):
        self.shutdownTime = None
        self.Say(mls.UI_SHARED_CLUSTERSHUTDOWNDELAYED)
        eve.Message('CluShutdownCancelled', {'explanation': msg})



    def __ShutdownTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if self.shutdownTime and self.shutdownTime - blue.os.GetTime() < 5 * MIN:
                    self.Say(mls.UI_SHARED_CLUSTERSHUTDOWN + ' ' + util.FmtTimeInterval(self.shutdownTime - blue.os.GetTime(), 'sec'))
            except:
                log.LogException()
                sys.exc_clear()
            blue.pyos.synchro.Sleep(5000)




    def __SessionTimeoutTimer(self):
        while self.state == SERVICE_RUNNING:
            try:
                if eve.session.maxSessionTime and eve.session.maxSessionTime - blue.os.GetTime() < 15 * MIN:
                    self.Say(mls.UI_SHARED_MAXSESSIONTIMEEXPIRING + ' ' + util.FmtTimeInterval(eve.session.maxSessionTime - blue.os.GetTime(), 'sec'))
            except:
                log.LogException()
                sys.exc_clear()
            blue.pyos.synchro.Sleep(5000)




    def OnRemoteMessage(self, msgID, dict = None, kw = {}):
        if msgID in ('SelfDestructInitiatedOther', 'SelfDestructImmediateOther', 'SelfDestructAbortedOther2') and not settings.user.ui.Get('notifyMessagesEnabled', 1):
            return 
        uthread.new(eve.Message, msgID, dict, **kw).context = 'gameui.ServerMessage'



    def TransitionCleanup(self, session, change):
        uicore.layer.menu.Flush()
        for each in sm.GetService('window').GetWindows()[:]:
            if hasattr(each, 'content') and getattr(each.content, '__guid__', None) == 'form.InflightCargoView' and each.id != session.shipid:
                if hasattr(each, 'SelfDestruct'):
                    each.SelfDestruct()
                else:
                    each.CloseX()
            if each.name.startswith('infowindow') and 'shipid' in change and each.sr.itemID in change['shipid']:
                each.SelfDestruct()




    def ClearCacheFiles(self):
        if eve.Message('AskClearCacheReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.clearcache = 1
            appUtils.Reboot('clear cache')



    def ClearSettings(self):
        if eve.Message('AskClearSettingsReboot', {}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.resetsettings = 1
            appUtils.Reboot('clear settings')



    def Stop(self, ms = None):
        self.settings.SaveSettings()
        service.Service.Stop(self, ms)



    def ProcessSessionChange(self, isRemote, session, change, cheat = 0):
        if 'shipid' in change and change['shipid'][0] and not session.stationid2:
            sm.GetService('invCache').CloseContainer(change['shipid'][0])
        self.settings.SaveSettings()
        self.LogInfo('ProcessSessionChange: ', change, ', ', session)
        if not isRemote:
            return 



    def DoSessionChanging(self, isRemote, session, change):
        if 'map' in sm.services and sm.GetService('map').IsOpen() and not session.charid:
            sm.GetService('map').Close()
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
        if 'userid' in change:
            sm.GetService('window').LoadUIColors()
        if 'userid' in change or 'charid' in change:
            self.settings.LoadSettings()
        if 'solarsystemid' in change:
            sm.GetService('FxSequencer').ClearAll()
            self.CacheCameraTranslation(inflight=bool(change['solarsystemid'][0]))
            self.michelle.RemoveBallpark()
        if 'worldspaceid' in change and change['worldspaceid'][1] is None:
            self.LogWarn('GameUI::OnSessionChanged, Leaving a worldspace', isRemote, session, change)
            uthread.pool('GameUI :: LeaveWorldSpace', self.LeaveWorldSpace, change)
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
                uthread.pool('GameUI :: GoIntro', self.GoIntro)
            else:
                uthread.pool('GameUI :: GoCharacterSelection', self.GoCharacterSelection)
        elif session.stationid is not None:
            if 'stationid' in change:
                self.LogNotice('GameUI::OnSessionChanged, Heading for station', isRemote, session, change)
                uthread.pool('GameUI::ActivateView::station', self.GoWorldSpace, change)
        elif session.worldspaceid is not None:
            if 'worldspaceid' in change:
                self.LogWarn('GameUI::OnSessionChanged, Heading for worldspace', isRemote, session, change)
                uthread.pool('GameUI :: GoWorldSpace', self.GoWorldSpace, change)
        elif session.solarsystemid is not None:
            self.LogNotice('GameUI::OnSessionChanged, Heading for inflight', isRemote, session, change)
            uthread.pool('GameUI :: GoInflight', self.GoInflight, change)
        else:
            self.LogWarn('GameUI::OnSessionChanged, Lame Teardown of the client, it should get propper OnDisconnect event', isRemote, session, change)
            self.ScopeCheck()



    def KillCargoView(self, id_, guidsToKill = None):
        if guidsToKill is None:
            guidsToKill = ('form.DockedCargoView', 'form.InflightCargoView', 'form.LootCargoView', 'form.DroneBay', 'form.CorpHangar', 'form.ShipCorpHangars', 'form.CorpHangarArray', 'form.SpecialCargoBay', 'form.PlanetInventory')
        for each in sm.GetService('window').GetWindows()[:]:
            if getattr(each, '__guid__', None) in guidsToKill and getattr(each, 'itemID', None) == id_:
                if not each.destroyed:
                    if hasattr(each, 'SelfDestruct'):
                        each.SelfDestruct()
                    else:
                        each.CloseX()




    def ScopeCheck(self, scope = []):
        scope += ['all']
        self.currentScope = scope
        for each in sm.GetService('window').GetWindows()[:]:
            if getattr(each, 'content', None) and hasattr(each.content, 'scope') and each.content.scope:
                if each.content.scope not in scope:
                    if each is not None and not each.destroyed:
                        if hasattr(each, 'SelfDestruct'):
                            self.LogInfo('ScopeCheck::SelfDestruct', each.name, 'scope', scope)
                            each.SelfDestruct()
                        else:
                            self.LogInfo('ScopeCheck::Close', each.name, 'scope', scope)
                            each.CloseX()
            elif hasattr(each, 'scope') and each.scope not in scope:
                if each is not None and not each.destroyed:
                    if hasattr(each, 'SelfDestruct'):
                        self.LogInfo('ScopeCheck::SelfDestruct2', each.name, 'scope', scope)
                        each.SelfDestruct()
                    else:
                        self.LogInfo('ScopeCheck::Close2', each.name, 'scope', scope)
                        each.CloseX()




    def GetCurrentScope(self):
        return self.currentScope



    def ShowExclusive(self, layerName = 'exclusive'):
        for layer in (uicore.layer.exclusive, uicore.layer.maps):
            if layerName and layer.name == 'l_' + layerName:
                layer.state = uiconst.UI_PICKCHILDREN
            else:
                layer.state = uiconst.UI_HIDDEN




    def ResetExclusive(self):
        self.ShowExclusive()



    def OpenExclusive(self, layerName, checkScope = 0):
        for _layerName in ['login',
         'charsel',
         'charactercreation',
         'intro',
         'inflight',
         'station',
         'ccreate',
         'charcontrol']:
            if layerName == _layerName:
                continue
            layer = uicore.layer.Get(_layerName)
            if layer:
                layer.CloseView()

        if layerName == 'charactercreation':
            uicore.layer.main.state = uiconst.UI_HIDDEN
            uicore.layer.neocom.state = uiconst.UI_HIDDEN
            uicore.layer.tabs.state = uiconst.UI_HIDDEN
        elif not eve.hiddenUIState:
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
            uicore.layer.neocom.state = uiconst.UI_PICKCHILDREN
            uicore.layer.tabs.state = uiconst.UI_PICKCHILDREN
        layer = uicore.layer.Get(layerName)
        layer.OpenView()
        if checkScope:
            if layerName == 'charcontrol':
                scope = ['station']
            else:
                scope = [layerName]
            if layerName in ('station', 'inflight', 'charcontrol'):
                scope.append('station_inflight')
            self.ScopeCheck(scope)



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
        rebootReason = settings.public.generic.Get('rebootReason', None)
        rebootTime = settings.public.generic.Get('rebootTime', blue.os.GetTime())
        if rebootReason == 'connection lost' and blue.os.GetTime() - rebootTime < MIN:
            self.GoLogin(step=2, connectionLost=1)
        else:
            pr = sm.GetService('webtools').GetVars()
            if pr:
                sm.GetService('webtools').GoSlimLogin()
            else:
                self.GoLogin()
                if self.startErrorMessage:
                    eve.Message(self.startErrorMessage)
                    self.startErrorMessage = None
        settings.public.generic.Set('rebootReason', '')



    def GetLanguages(self):
        if eve.session.userid:
            if not self.languages:
                self.languages = []
                for row in sm.RemoteSvc('languageSvc').GetLanguages():
                    if boot.region == 'optic' and row.languageID != 'ZH' or boot.region != 'optic' and row.languageID == 'ZH':
                        continue
                    self.languages.append([row.languageID, row.languageName, row.translatedName])

            return self.languages
        else:
            return []



    def GetLanguageIDs(self):
        return [ languageID for (languageID, languageName, translatedName,) in self.GetLanguages() ]



    def SetLanguage(self, key):
        if boot.region == 'optic' and not eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            key = 'ZH'
        if key in self.GetLanguageIDs():
            sm.RemoteSvc('authentication').SetLanguageID(key)
            mls.LoadTranslations(key)
            prefs.languageID = key



    def HasActiveOverlay(self):
        return sm.IsServiceRunning('map') and sm.GetService('map').IsOpen() or sm.IsServiceRunning('planetUI') and sm.GetService('planetUI').IsOpen()



    def GoLogin(self, step = 1, connectionLost = 0, *args):
        blue.statistics.SetTimelineSectionName('login')
        sm.GetService('loading').GoBlack()
        if self.sceneManager.scene1 is not None:
            self.sceneManager.scene1.display = 0
        self.OpenExclusive('login')
        login = uicore.layer.login
        if connectionLost:
            uthread.new(eve.Message, 'ConnectionLost', {'what': ''})



    def GoIntro(self, *args):
        blue.statistics.SetTimelineSectionName('intro')
        sm.GetService('loading').ProgressWnd(mls.UI_LOGIN_ENTERINGINTRO, '', 1, 2)
        self.OpenExclusive('intro', 1)
        sm.GetService('loading').ProgressWnd(mls.UI_LOGIN_ENTERINGINTRO, '', 2, 2)



    def GoCharacterSelection(self, force = 0, *args):
        blue.statistics.SetTimelineSectionName('charSel')
        self.sceneManager.SetSceneType(SCENE_TYPE_SPACE)
        c = sm.GetService('cc').GetCharactersToSelect(force)
        if c:
            sm.StartService('menu')
            sm.StartService('tutorial')
            sm.GetService('loading').ProgressWnd(mls.UI_CHARSEL_ENTERINGCHARSEL, '', 1, 2)
            self.OpenExclusive('charsel', 1)
            sm.GetService('loading').ProgressWnd(mls.UI_CHARSEL_ENTERINGCHARSEL, '', 2, 2)
        else:
            uthread.pool('GameUI :: GoCharacterCreation', self.GoCharacterCreation, 0)



    def GoCharacterCreationCurrentCharacter(self, *args):
        if None in (session.charid, session.genderID, session.bloodlineID):
            return 
        ccLayer = uicore.layer.Get('charactercreation')
        if ccLayer is not None and ccLayer.isopen:
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
            self.GoCharacterCreation(0, session.charid, session.genderID, session.bloodlineID, fromCharSel=0, dollState=dollState)
            stationSvc.ClearPaperdollStateCache()
        elif message == uiconst.ID_NO:
            self.GoCharacterCreation(0, session.charid, session.genderID, session.bloodlineID, fromCharSel=0, dollState=None)



    def GoCharacterCreation(self, canReturnToCharsel = 1, charID = None, gender = None, bloodlineID = None, fromCharSel = 1, askUseLowShader = 1, dollState = None, *args):
        if charID is not None:
            if session.worldspaceid == session.stationid2:
                player = sm.GetService('entityClient').GetPlayerEntity()
                if player is not None:
                    pos = player.GetComponent('position')
                    if pos is not None:
                        self.cachedPlayerPos = pos.position
                        self.cachedPlayerRot = pos.rotation
            change = {'worldspaceid': [session.worldspaceid, None]}
            sm.GetService('entityClient').ProcessSessionChange(False, session, change)
            self.OnSessionChanged(False, session, change)
        factory = sm.GetService('character').factory
        factory.compressTextures = False
        factory.allowTextureCache = False
        clothSimulation = sm.GetService('device').GetAppFeatureState('CharacterCreation.clothSimulation', True)
        factory.clothSimulationActive = clothSimulation
        blue.statistics.SetTimelineSectionName('charCreation')
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
        sm.GetService('loading').FadeToBlack()
        if charID:
            text = mls.UI_CHARCREA_ENTERINGCHARRECUST
        else:
            text = mls.UI_CHARCREA_ENTERINGCHARCREA
        sm.GetService('loading').ProgressWnd(text, '', 1, 2)
        self.OpenExclusive('charactercreation')
        self.sceneManager.SetSceneType(SCENE_TYPE_CHARACTER_CREATION)
        sm.GetService('cc').GoCharacterCreation(charID, gender, bloodlineID, dollState=dollState)
        sm.GetService('loading').FadeFromBlack()
        sm.GetService('loading').ProgressWnd(text, '', 2, 2)



    def GoWorldSpace(self, change):
        view = util.GetCurrentView()
        self.LogInfo('Going to ', view)
        if view == 'station':
            factory = sm.GetService('paperDollClient').dollFactory
            factory.compressTextures = True
            factory.allowTextureCache = True
            clothSimulation = sm.GetService('device').GetAppFeatureState('Interior.clothSimulation', False)
            factory.clothSimulationActive = clothSimulation
            if not self.HasActiveOverlay():
                self.OpenExclusive('charcontrol', 1)
            if change['worldspaceid'][0] is None:
                eve.SynchronizeClock()
                sm.GetService('wallet')
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.CloseView()
        if view == 'hangar':
            sm.GetService('entityClient').UnloadEntityScene(session.worldspaceid)
            if not self.HasActiveOverlay():
                self.OpenExclusive('station', 1)
            if uicore.layer.shipui.isopen:
                uicore.layer.shipui.CloseView()
        if util.IsStation(session.stationid):
            self._GoStation(change)
        if hasattr(self, 'cachedPlayerPos') and session.worldspaceid == session.stationid2 and view == 'station':
            pos = sm.GetService('entityClient').GetPlayerEntity(True).GetComponent('position')
            pos.position = self.cachedPlayerPos or pos.position
            pos.rotation = self.cachedPlayerRot or pos.rotation
            self.cachedPlayerPos = None
            self.cachedPlayerRot = None
        sm.GetService('neocom').ShowToggleHangarCQButton()
        uthread.new(sm.GetService('loading').FadeFromBlack, 3000)
        sm.GetService('loading').ProgressWnd()
        self.DoWindowIdentification()
        sm.ScatterEvent('OnClientReady', 'worldspace')
        if not self.HasActiveOverlay():
            if view == 'station':
                if not uix.GetWorldspaceNav(create=0):
                    if '/thinclient' not in blue.pyos.GetArg():
                        uix.GetWorldspaceNav()
                uicore.registry.SetFocus(uicore.GetLayer('charcontrol'))
            elif view == 'hangar':
                uix.GetStationNav()



    def LeaveWorldSpace(self, change):
        uicore.layer.charcontrol.CloseView()
        wsClient = sm.GetService('worldSpaceClient')
        wsClient.TearDownWorldSpaceRendering()
        uicore.uilib.scenePickFunction = None



    def _GoStation(self, change):
        if 'stationid' in change:
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSTATION, '', 1, 5)
            sm.GetService('michelle').RemoveBallpark()
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSTATION, mls.UI_STATION_CLEARINGCURRENTSTATE, 2, 5)
            tostation = change['stationid'][1]
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSTATION, cfg.evelocations.Get(tostation).name, 3, 5)
            if tostation is not None:
                sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSTATION, mls.UI_STATION_SETUPSTATION + ': ' + cfg.evelocations.Get(tostation).name, 4, 5)
                sm.GetService('station').CleanUp()
                sm.GetService('station').StopAllStationServices()
                sm.GetService('station').Setup()
                view = util.GetCurrentView()
                if view == 'hangar':
                    self.LeaveWorldSpace(change)
                    sm.GetService('station').SetupHangarScene()
                else:
                    sm.GetService('entitySpawnClient').SpawnClientSidePlayer(change)
                    sm.GetService('station').SetupCaptainsQuartersScene()
                    if settings.user.ui.Get('doIntroTutorial%s' % session.charid, 0):
                        tutID = uix.tutorialTutorials
                    else:
                        tutID = uix.tutorialWorldspaceNavigation
                    uthread.new(self.OpenStationTutorial_thread, tutID)
                if 'shipid' in change and change['shipid'][1] is None:
                    uthread.new(sm.GetService('charactersheet').LoadGeneralInfo)
            elif tostation is None:
                sm.GetService('station').CleanUp()
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSTATION, mls.UI_GENERIC_DONE, 5, 5)
            sm.GetService('loading').FadeFromBlack()
        else:
            sm.GetService('station').CheckSession(change)



    def OpenStationTutorial_thread(self, tutID):
        blue.pyos.synchro.Sleep(5000)
        sm.GetService('tutorial').OpenTutorialSequence_Check(tutID)



    def GoInflight(self, change):
        blue.statistics.SetTimelineSectionName('inFlight')
        self.sceneManager.SetSceneType(SCENE_TYPE_SPACE)
        eve.SynchronizeClock()
        try:
            sm.StartServiceAndWaitForRunningState('wreck')
        except:
            log.LogException()
            sys.exc_clear()
        sm.StartService('standing')
        sm.StartService('tactical')
        sm.StartService('pathfinder')
        sm.StartService('map')
        sm.StartService('wallet')
        sm.StartService('space')
        sm.StartService('state')
        sm.StartService('bracket')
        sm.StartService('target')
        sm.StartService('fleet')
        sm.StartService('surveyScan')
        sm.StartService('autoPilot')
        sm.StartService('info')
        sm.StartService('neocom')
        sm.StartService('corp')
        sm.StartService('alliance')
        sm.StartService('skillqueue')
        sm.StartService('notepad')
        sm.StartService('dungeonTracking')
        sm.StartService('transmission')
        sm.StartService('clonejump')
        sm.StartService('assets')
        sm.StartService('charactersheet')
        sm.StartService('trigger')
        sm.StartService('contracts')
        sm.StartService('certificates')
        sm.StartService('billboard')
        sm.StartService('sov')
        sm.StartService('turret')
        if eve.session.role & service.ROLE_CONTENT:
            sm.StartService('scenario')
        sm.StartServiceAndWaitForRunningState('camera')
        self.OpenExclusive('inflight', 1)
        michelle = sm.GetService('michelle')
        bp = michelle.GetBallpark()
        if bp is None:
            self.LogInfo('Adding new ballpark')
            bp = michelle.AddBallpark(session.solarsystemid)
        elif 'solarsystemid' in change:
            bp = michelle.AddBallpark(session.solarsystemid)
        elif 'shipid' in change and change['shipid'][1] is not None:
            if change['shipid'][0]:
                self.KillCargoView(change['shipid'][0])
            uthread.new(sm.GetService('target').ClearTargets)
            if session.shipid in bp.balls:
                self.LogInfo('Changing ego: ', bp.ego, '->', session.shipid)
                bp.ego = session.shipid
                self.OnNewState(bp, mls.UI_INFLIGHT_BOARDINGSHIP)
            else:
                self.LogInfo('Postponing ego: ', bp.ego, '->', session.shipid)
            self.wannaBeEgo = session.shipid
        self.cachedPlayerPos = None
        self.cachedPlayerRot = None
        self.DoWindowIdentification()
        sm.ScatterEvent('OnClientReady', 'inflight')
        if not sm.GetService('map').IsOpen() and not sm.GetService('planetUI').IsOpen():
            uix.GetInflightNav()



    def MessageBox(self, text, title = 'EVE', buttons = None, icon = None, suppText = None, customicon = None, height = None, blockconfirmonreturn = 0, default = None, modal = True):
        if not getattr(uicore, 'desktop', None):
            return 
        if buttons is None:
            buttons = uiconst.ID_OK
        sm.GetService('window').ResetToDefaults('MessageBox')
        msgbox = sm.GetService('window').GetWindow('MessageBox', create=1, prefsName='modal', ignoreCurrent=1)
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
        sm.GetService('window').ResetToDefaults('RadioButtonMessageBox')
        msgbox = sm.GetService('window').GetWindow('RadioButtonMessageBox', create=1, prefsName='modal', ignoreCurrent=1)
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
            self.OnNewState(bp, mls.UI_INFLIGHT_BOARDINGSHIP)



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
        for each in sm.GetService('window').GetWindows()[:]:
            if each.name in ['shipCargo_%s' % eve.session.shipid, 'drones_%s' % eve.session.shipid]:
                continue
            if hasattr(each, 'id') and each.id == invID:
                if hasattr(each, 'SelfDestruct'):
                    each.SelfDestruct()
                else:
                    each.CloseX()




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
            sm.GetService('loading').ProgressWnd(hint, mls.UI_INFLIGHT_CHECKINGNAVSYSTEMS, 5, 6)
        else:
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSPACE, mls.UI_INFLIGHT_CHECKINGNAVSYSTEMS, 5, 6)
        blue.pyos.synchro.Yield()
        shipui = uicore.layer.shipui
        if bp and bp.balls.get(bp.ego, None):
            sm.GetService('camera').LookAt(bp.ego, self.GetCachedCameraTranslation((eve.session.shipid, 1)))
            if shipui.isopen:
                shipui.form.Init(bp.balls.get(bp.ego, None))
            else:
                shipui.OpenView()
        else:
            shipui.CloseView()
        uthread.new(sm.GetService('loading').FadeFromBlack, 2500)
        if hint:
            sm.GetService('loading').ProgressWnd(hint, mls.UI_INFLIGHT_CHECKINGNAVSYSTEMS, 6, 6)
        else:
            sm.GetService('loading').ProgressWnd(mls.UI_STATION_ENTERINGSPACE, mls.UI_INFLIGHT_CHECKINGNAVSYSTEMS, 6, 6)
        blue.pyos.synchro.Yield()



    def DoWindowIdentification(self):
        triapp = trinity.app
        if eve.session.charid and settings.user.ui.Get('windowidentification', 0):
            charName = cfg.eveowners.Get(eve.session.charid).name
            triapp.title = '%s - %s' % (uicore.triappargs['title'], charName)
        else:
            trinity.app.title = uicore.triappargs['title']




def GetCurrentView():
    view = settings.user.ui.Get('defaultDockingView', 'station')
    if view == 'station' and not prefs.GetValue('loadstationenv', 1):
        view = 'hangar'
    settings.user.ui.Set('defaultDockingView', view)
    return view


exports = util.AutoExports('util', {'GetCurrentView': GetCurrentView})

