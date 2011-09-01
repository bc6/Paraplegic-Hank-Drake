import blue
import uthread
import uix
import uiutil
import uiconst
import mathUtil
import sys
import types
import util
import corebrowserutil
import zlib
import log
import trinity
import audio2
import uicls
import nodemanager
import locks
import bluepy
import const
from nasty import nasty

def GetVersion():
    subbuild = None
    try:
        subbuild = str(boot.build)
        if nasty.IsRunningWithOptionalUpgrade():
            currentCode = nasty.GetAppDataCompiledCodePath()
            subbuild = str(currentCode.build) + ' (' + str(boot.build) + ')'
    except:
        log.LogException()
        if subbuild is None:
            subbuild = '501'
    try:
        buildno = '%s.%s' % (boot.keyval['version'].split('=', 1)[1], subbuild)
    except:
        log.LogException()
        buildno = subbuild
    return buildno


LIVE_SERVER = '87.237.38.200'
TEST_SERVER1 = '87.237.38.50'
TEST_SERVER2 = '87.237.38.51'
TEST_SERVER3 = '87.237.38.60'
WEB_EVE = 'http://www.eveonline.com'
WEB_MYEVE = 'http://www.eveonline.com'
WEB_ACCOUNT = 'https://secure.eveonline.com/'
WEB_SUPPORT = 'http://www.eveonline.com/mb/support.asp'
WEB_MBPATCHNOTES = 'http://www.eveonline.com/mb/patchnotes.asp'
SERVERS = [('Tranquility', LIVE_SERVER),
 ('Test Server (Singularity)', TEST_SERVER1),
 ('Test Server (Multiplicity)', TEST_SERVER2),
 ('Test Server (Duality)', TEST_SERVER3),
 ('Singularity', TEST_SERVER1),
 ('Multiplicity', TEST_SERVER2),
 ('Duality', TEST_SERVER3)]
if boot.region == 'optic':
    LIVE_SERVER1 = 'tel.eve.gtgame.com.cn'
    LIVE_SERVER2 = 'cnc.eve.gtgame.com.cn'
    TEST_SERVER1 = 'beta.eve.gtgame.com.cn'
    TEST_SERVER2 = None
    TEST_SERVER3 = None
    WEB_EVE = 'http://eve.gtgame.com.cn'
    WEB_MYEVE = 'http://myeve.eve.gtgame.com.cn'
    WEB_ACCOUNT = 'http://passport.cdcgames.net/account/login.aspx'
    WEB_SUPPORT = 'http://bill.gtgame.com.cn/portal/customer/eveindex.jsp'
    WEB_MBPATCHNOTES = 'http://eve.gtgame.com.cn/mb/patchnotes.asp'
    SERVERS = [(u'\u6668\u66e6\uff08\u7535\u4fe1\uff09', LIVE_SERVER1), (u'\u6668\u66e6\uff08\u7f51\u901a\uff09', LIVE_SERVER2)]

def GetServerIP(checkServerName):
    for (serverName, serverIP,) in SERVERS:
        if checkServerName.lower() == serverName.lower():
            return serverIP

    return checkServerName



def GetServerName(checkServerIP):
    for (serverName, serverIP,) in SERVERS:
        if serverIP.lower() == checkServerIP.lower():
            return serverName

    return checkServerIP



class BackgroundWrapper(object):

    def __init__(self, fadeCont):
        trinity.device.RegisterResource(self)
        self.fadeCont = fadeCont
        self._PrepareBackground()



    def OnCreate(self, dev):
        uthread.new(self._PrepareBackground)



    def _PrepareBackground(self):
        self.backgroundSprite = sm.GetService('photo').GetScenePicture(res=128, blur=1)
        self.fadeCont.Flush()
        self.fadeCont.children.insert(0, self.backgroundSprite)




class Login(uicls.LayerCore):
    __guid__ = 'form.LoginII'
    __notifyevents__ = ['OnEndChangeDevice', 'OnGraphicSettingsChanged']

    def TerminateStartupTestLater_t(self):
        blue.synchro.Sleep(1000)
        bluepy.TerminateStartupTest()



    def OnCloseView(self):
        sys = uicore.layer.systemmenu
        if sys.isopen:
            uthread.new(sys.CloseMenu)
        self.Reset()
        self.ClearScene()
        sm.GetService('sceneManager').SetupSceneForRendering(None, None)
        sm.UnregisterNotify(self)
        del self.scene.curveSets[:]
        self.scene = None
        self.ship = None



    def OnEndChangeDevice(self, *args):
        if self.isopen:
            if self.reloading:
                self.pendingReload = 1
                return 
            currentUsername = self.usernameEditCtrl.GetValue()
            currentPassword = self.passwordEditCtrl.GetValue()
            self.reloading = 1
            activePanelArgs = self.pushButtons.GetSelected()
            self.Layout(1, activePanelArgs, currentUsername, currentPassword)
            self.reloading = 0
            if self.pendingReload:
                self.pendingReload = 0
                self.OnEndChangeDevice()



    @bluepy.CCP_STATS_ZONE_METHOD
    def Reset(self):
        self.serverStatus = {}
        self.serverStatusTextControl = None
        self.serverStatusTextFunc = None
        self.eulaParent = None
        self.eulaCRC = None
        self.eulaBrowser = None
        self.eulaBlock = None
        self.mainBrowserParent = None
        self.mainBrowser = None
        self.usernameEditCtrl = None
        self.passwordEditCtrl = None
        self.motdParent = None
        self.connecting = False
        self.pushButtons = None
        self.waitingForEula = 0
        self.acceptbtns = None
        self.scrollText = None
        self.reloading = 0
        self.pendingReload = 0
        self.bg = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnOpenView(self):
        self.Reset()
        uthread.worker('login::StatusTextWorker', self._Login__StatusTextWorker)
        sm.RegisterNotify(self)
        sm.GetService('loading').GoBlack()
        blue.resMan.Wait()
        self.serverName = util.GetServerName()
        self.serverIP = GetServerIP(self.serverName)
        self.serverName = GetServerName(self.serverIP)
        self.serverPort = util.GetServerPort()
        self.Layout()
        sm.ScatterEvent('OnClientReady', 'login')
        self.isopen = 1
        uthread.new(self.UpdateServerStatus)
        if bluepy.IsRunningStartupTest():
            uthread.new(self.TerminateStartupTestLater_t)



    def GetEulaConfirmation(self):
        self.waitingForEula = 1
        self.eulaclosex.state = uiconst.UI_HIDDEN
        self.eulaBlock = uicls.Fill(parent=self.eulaParent.parent, idx=self.eulaParent.parent.children.index(self.eulaParent) + 1, state=uiconst.UI_NORMAL, color=(0.0, 0.0, 0.0, 0.75))
        par = uicls.Container(name='btnpar', parent=self.eulaBrowser, align=uiconst.TOBOTTOM, height=40, idx=0)
        self.scrollText = uicls.Label(text=mls.UI_LOGIN_SCROLLTOBOTTOM, parent=par, align=uiconst.CENTER, width=400, autowidth=False, idx=0, state=uiconst.UI_NORMAL)
        btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_ACCEPT,
          self.AcceptEula,
          2,
          81,
          uiconst.ID_OK,
          0,
          0], [mls.UI_CMD_DECLINE,
          self.ClickExit,
          (),
          81,
          uiconst.ID_CANCEL,
          0,
          1]], line=0)
        btns.state = uiconst.UI_HIDDEN
        par.children.insert(0, btns)
        self.acceptbtns = btns
        self.pushButtons.SelectPanelByName(mls.UI_LOGIN_EULA)
        self.eulaBrowser.OnUpdatePosition = self.ScrollingEula
        self.waitingForEula = 1



    def ClickExit(self, *args):
        uicore.cmd.CmdQuitGame()



    def AcceptEula(self, *args):
        self.eulaBlock.Close()
        self.eulaclosex.state = uiconst.UI_NORMAL
        self.acceptbtns.parent.Close()
        self.waitingForEula = 0
        self.pushButtons.DeselectAll()
        self.acceptbtns = None
        self.scrollText = None
        self.eulaBlock = None
        settings.public.generic.Set('eulaCRC', self.eulaCRC)
        uthread.pool('Login::Fetching ads', self.CheckAds)
        uthread.new(self.LoadMotd)



    def ScrollingEula(self, scroll, *args):
        if self.eulaBrowser.viewing == 'eula_ccp':
            proportion = scroll.GetScrollProportion()
            if proportion >= 1.0 and self.acceptbtns:
                self.acceptbtns.state = uiconst.UI_NORMAL
                if self.scrollText:
                    self.scrollText.state = uiconst.UI_HIDDEN



    def FadeSplash(self, sprite):
        blue.pyos.synchro.Sleep(500)
        sm.GetService('ui').Fade(1.0, 0.0, sprite)
        sprite.Close()



    @bluepy.CCP_STATS_ZONE_METHOD
    def Layout(self, reloading = 0, pushBtnArgs = None, setUsername = None, setPassword = None):
        if not reloading:
            self.sceneLoadedEvent = locks.Event('loginScene')
            uthread.new(self.LoadScene)
        self.isWindow = True
        self.eulaInited = 0
        self.Flush()
        borderHeight = uicore.desktop.height / 6
        par = uicls.Container(name='underlayContainer', parent=self, align=uiconst.TOTOP, height=borderHeight)
        self.sr.underlay2 = uicls.WindowUnderlay(parent=par)
        self.sr.underlay2.SetPadding(-16, -16, -16, 0)
        bottomPar = uicls.Container(name='underlayContainer_Bottom', parent=self, align=uiconst.TOBOTTOM, height=borderHeight + 6)
        bottomUnderlay = uicls.WindowUnderlay(parent=bottomPar)
        bottomUnderlay.SetPadding(-16, 6, -16, -16)
        self.fadeCont = uicls.Container(name='fadeCont', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=uicore.desktop.width, height=uicore.desktop.height, idx=-1)
        if trinity.app.fullscreen:
            closex = uicls.Icon(icon='ui_73_16_49', parent=self, pos=(0, 1, 0, 0), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_NORMAL, hint=mls.UI_CMD_QUITGAME)
            closex.OnClick = self.ClickExit
            closex.sr.hintAbRight = uicore.desktop.width - 16
            closex.sr.hintAbTop = 16
        self.mainBrowserParent = uicls.Container(name='mainBrowserParent', parent=self, align=uiconst.CENTER, width=800, height=440, idx=0)
        self.mainBrowserParent.isWindow = True
        self.mainBrowser = uicls.Edit(parent=self.mainBrowserParent, padding=(8, 18, 8, 8), readonly=1)
        mainclosex = uicls.Icon(icon='ui_38_16_220', parent=self.mainBrowserParent, pos=(2, 1, 0, 0), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_NORMAL)
        mainclosex.OnClick = self.CloseMenu
        self.sr.wndUnderlay = uicls.WindowUnderlay(parent=self.mainBrowserParent)
        self.eulaParent = uicls.Container(name='eulaParent', parent=self, align=uiconst.CENTER, width=800, height=440, idx=0)
        self.eulaParent.isWindow = True
        eulaCont = uicls.Container(name='eulaCont', parent=self.eulaParent, align=uiconst.TOALL, padding=(0, 18, 0, 0))
        browser = uicls.Edit(parent=eulaCont, padding=(6, 6, 6, 6), readonly=1)
        browser.sr.scrollcontrols.state = uiconst.UI_NORMAL
        browser.viewing = 'eula_ccp'
        self.eulaBrowser = browser
        self.sr.eulaUnderlay = uicls.WindowUnderlay(parent=self.eulaParent)
        self.sr.maintabs = uicls.TabGroup(name='maintabs', parent=eulaCont, idx=0, tabs=[[mls.UI_EULAEVE,
          browser,
          self,
          'eula_ccp'], [mls.UI_EULA3RDPARTY,
          browser,
          self,
          'eula_others']], groupID='eula', autoselecttab=0)
        self.eulaclosex = uicls.Icon(icon='ui_38_16_220', parent=self.eulaParent, pos=(2, 1, 0, 0), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_NORMAL)
        self.eulaclosex.OnClick = self.CloseMenu
        bottomArea = uicls.Container(name='bottomArea', parent=bottomPar, idx=0, pos=(0, 0, 0, 0))
        bottomSub = uicls.Container(name='bottomSub', parent=bottomArea, align=uiconst.CENTER, idx=0, height=bottomPar.height, width=800)
        knownUserNames = settings.public.ui.Get('usernames', [])
        editswidth = 120
        if borderHeight <= 100:
            editstop = 30
        else:
            editstop = 40
        editsleft = (bottomSub.width - editswidth) / 2
        edit = uicls.SinglelineEdit(name='username', parent=bottomSub, pos=(editsleft,
         editstop,
         editswidth,
         0), maxLength=64)
        edit.SetHistoryVisibility(0)
        t1 = uicls.Label(text=mls.UI_LOGIN_USERNAME, parent=edit, letterspace=2, fontsize=9, top=1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.75), uppercase=1)
        if knownUserNames:
            ops = [ (name, name) for name in knownUserNames ]
            edit.LoadCombo('usernamecombo', ops, self.OnComboChange, comboIsTabStop=0)
        edit.SetValue(setUsername or settings.public.ui.Get('username', ''))
        edit.OnReturn = self.Confirm
        self.usernameEditCtrl = edit
        edit = uicls.SinglelineEdit(name='password', parent=bottomSub, pos=(editsleft,
         edit.top + edit.height + 6,
         editswidth,
         0), maxLength=64)
        t2 = uicls.Label(text=mls.UI_LOGIN_PASSWORD, parent=edit, letterspace=2, fontsize=9, top=1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.75), uppercase=1)
        edit.SetPasswordChar('\x95')
        edit.SetValue(setPassword or '')
        edit.OnReturn = self.Confirm
        self.passwordEditCtrl = edit
        tw = max(t1.textwidth, t2.textwidth)
        t1.left = t2.left = -tw - 6
        connectBtn = uicls.Button(parent=bottomSub, label=mls.UI_LOGIN_CONNECT, func=self.Connect, pos=(editsleft,
         edit.top + edit.height + 4,
         0,
         0), fixedwidth=120, btn_default=1)
        self.serverStatusTextControl = uicls.Label(text=mls.UI_LOGIN_CHECKINGSTATUS, parent=bottomSub, left=editsleft + editswidth + 6, top=editstop, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, mousehilite=1, letterspace=1)
        self.motdParent = uicls.Container(name='motdParent', parent=self, align=uiconst.CENTERBOTTOM, top=borderHeight + 16, width=400, height=64, state=uiconst.UI_HIDDEN)
        motdBrowser = uicls.Edit(parent=self.motdParent, readonly=1)
        motdBrowser.isTabStop = 0
        self.sr.motdBrowser = motdBrowser
        versionstr = '%s: %s' % (mls.UI_LOGIN_VERSION, GetVersion())
        vers = uicls.Label(text=versionstr, parent=self, left=6, top=6, letterspace=1, fontsize=9, uppercase=1, idx=0, state=uiconst.UI_NORMAL)
        tabs = [[mls.UI_GENERIC_SETTINGS,
          None,
          self,
          None,
          ('settings',)],
         [mls.UI_LOGIN_SUPPORT,
          self.mainBrowserParent,
          self,
          None,
          ('support',)],
         [mls.UI_LOGIN_NEWS,
          self.mainBrowserParent,
          self,
          None,
          ('news',)],
         [mls.UI_LOGIN_PATCHINFO,
          self.mainBrowserParent,
          self,
          None,
          ('patchinfo',)],
         [mls.UI_LOGIN_EULA,
          self.eulaParent,
          self,
          None,
          ('eula',)],
         [mls.UI_LOGIN_ACCOUNTMGMT,
          None,
          self,
          None,
          ('account',)]]
        self.pushButtons = uicls.PushButtonGroup(parent=bottomPar, align=uiconst.CENTERTOP, idx=0, top=-4)
        self.pushButtons.Startup(tabs)
        self.pushButtons.OnNoneSelected = self.OnPushButtonNoneSelected
        if boot.region == 'optic':
            self.eulaCRC = zlib.adler32(str(boot.version))
        else:
            self.eulaCRC = zlib.adler32(buffer(self.GetEulaCCP()))
        eulaAgreed = bool(settings.public.generic.Get('eulaCRC', None) == self.eulaCRC)
        if not eulaAgreed:
            self.GetEulaConfirmation()
        elif pushBtnArgs:
            self.pushButtons.SelectPanelByArgs(pushBtnArgs)
        uthread.pool('Login::Fetching ads', self.CheckAds, bool(pushBtnArgs))
        uthread.new(self.LoadMotd, bool(pushBtnArgs))
        if trinity.app.IsActive():
            if settings.public.ui.Get('username', ''):
                uicore.registry.SetFocus(self.passwordEditCtrl)
            else:
                uicore.registry.SetFocus(self.usernameEditCtrl)
        if boot.region != 'optic':
            esrbNoticeHeight = 70
            esrbNoticeWidth = 200
            allowedSizes = [1.0, 0.9, 0.8]
            desktopWidth = uicore.desktop.width
            useHeight = int(esrbNoticeHeight * 0.7)
            useWidth = int(esrbNoticeWidth * 0.7)
            for multiplier in allowedSizes:
                tempWidth = esrbNoticeWidth * multiplier
                if tempWidth <= desktopWidth * 0.11:
                    useWidth = int(tempWidth)
                    useHeight = int(esrbNoticeHeight * multiplier)
                    break

            cont = uicls.Container(name='esrbParent', parent=bottomArea, align=uiconst.TOPLEFT, top=editstop, width=useWidth, height=useHeight, state=uiconst.UI_NORMAL, idx=0, left=20)
            sprite = uicls.Sprite(name='ESRB', parent=cont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0), lockAspect=1, texturePath='res:/UI/Texture/ESRBnotice.dds')
            sprite.rectWidth = esrbNoticeWidth
            sprite.rectHeight = esrbNoticeHeight
            uthread.new(uix.FadeCont, cont, 0, after=6000, fadeTime=500.0)



    def Load(self, key, *args):
        self.eulaBrowser.viewing = key
        text = ''
        if key == 'eula_others':
            eula = self.GetEulaOthers()
            text = mls.UI_LOGIN_SCROLLTOEVEBOTTOM
        else:
            eula = self.GetEulaCCP()
            text = mls.UI_LOGIN_SCROLLTOBOTTOM
        if self.scrollText is not None:
            self.scrollText.text = text
        self.eulaBrowser.LoadHTML(eula)



    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_PauseCurves(self):
        if self.scene is not None:
            for model in self.scene.objects:
                for cs in model.curveSets:
                    cs.scale = 0.0


            for cs in self.scene.curveSets:
                cs.scale = 0.0




    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_PlayCurves(self):
        if self.scene is not None:
            for model in self.scene.objects:
                for cs in model.curveSets:
                    cs.scale = 1.0


            for cs in self.scene.curveSets:
                cs.scale = 1.0




    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_AssignFiringEffects(self):
        firingEffectResPath = 'res:/dx9/model/turret/energy/beam/m/beam_quad_t1_fx.red'
        for turretSet in self.ship.turretSets:
            for j in range(4):
                effect = trinity.Load(firingEffectResPath)
                if effect is not None:
                    effect.source = None
                    effect.dest = None
                    turretSet.firingEffects.append(effect)

            turretSet.FreezeHighDetailLOD()




    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_SetTarget(self):
        for model in self.scene.objects:
            if model.name == 'target':
                target = model
                break

        if target is None:
            log.LogError('Login scene: No target!')
            return 
        for each in self.ship.turretSets:
            each.targetObject = target




    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_Perform(self, action):
        uthread.new(self._R2_2011_Perform, action)



    @bluepy.CCP_STATS_ZONE_METHOD
    def _R2_2011_Perform(self, action):
        if self.ship is None:
            log.LogError('Login scene: could not find shooter')
            return 
        if action == 'Aim':
            try:
                for turretSet in self.ship.turretSets:
                    turretSet.EnterStateTargeting()

            except:
                log.LogError('Login scene: Failed to aim at target')
        elif action == 'Shoot':
            try:
                for turretSet in self.ship.turretSets:
                    turretSet.EnterStateFiring()

            except:
                log.LogError('Login scene: Failed to shoot')
        elif action == 'WarpIn':
            for turretSet in self.ship.turretSets:
                turretSet.ForceStateDeactive()

            curveSets = nodemanager.FindNodes(self.scene, 'WarpIn', 'trinity.TriCurveSet')
            for cs in curveSets:
                cs.Play()

        elif action == 'WarpOut':
            for turretSet in self.ship.turretSets:
                turretSet.EnterStateDeactive()

            for cs in self.ship.curveSets:
                if cs.name == 'WarpOut':
                    cs.Play()




    @bluepy.CCP_STATS_ZONE_METHOD
    def R2_2011_HookUpEventCurve(self):
        curveSet = trinity.TriCurveSet()
        eventCurve = trinity.TriEventCurve()
        eventCurve.AddKey(0.0, u'Start')
        eventCurve.AddCallableKey(0.01, self.R2_2011_Perform, ('WarpIn',))
        eventCurve.AddCallableKey(27.0, self.R2_2011_Perform, ('Aim',))
        eventCurve.AddCallableKey(41.455, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(43.636, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(45.818, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(50.182, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(56.727, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(61.091, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(63.273, self.R2_2011_Perform, ('Shoot',))
        eventCurve.AddCallableKey(70.0, self.R2_2011_Perform, ('WarpOut',))
        eventCurve.AddKey(128.727, u'End')
        eventCurve.extrapolation = trinity.TRIEXT_CYCLE
        curveSet.curves.append(eventCurve)
        curveSet.Play()
        self.scene.curveSets.append(curveSet)



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadScene(self):
        self.camera = trinity.Load('res:/dx9/scene/login_screen_camera.red')
        self.scene = trinity.Load('res:/dx9/scene/login_screen_incarna.red')
        blue.resMan.Wait()
        self.ship = None
        for model in self.scene.objects:
            if model.name == 'shooter':
                self.ship = model
                break

        if self.ship is None:
            log.LogError('Login scene: No ship')
            return 
        self.R2_2011_AssignFiringEffects()
        self.R2_2011_SetTarget()
        self.R2_2011_HookUpEventCurve()
        jukebox = sm.GetService('jukebox')
        jukebox.AddPlaylist('mls://UI_SHARED_PLAYLIST_EVE_LOGIN', 'res:/audio/login2.pink', isHidden=True)
        jukebox.SetPlaylist('mls://UI_SHARED_PLAYLIST_EVE_LOGIN', persist=False)
        jukebox.PlayTrack(0, ignoreState=True)
        self.camera.audio2Listener = audio2.GetListener(0)
        sm.GetService('sceneManager').SetCamera(self.camera)
        sm.GetService('sceneManager').SetupSceneForRendering(None, self.scene)
        self.sceneLoadedEvent.set()
        blue.pyos.synchro.Yield()
        sm.GetService('loading').FadeFromBlack()



    def CheckAds(self, hidden = False):
        alwaysShowAd = False
        try:
            extraParam = sm.GetService('patch').GetWebRequestParameters()
            if settings.public.ui.Get('usernames') is None and sm.GetService('patch').GetClientAffiliateID() != '':
                alwaysShowAd = True
            adUrl = WEB_EVE + '/ads.asp?%s' % extraParam
            sm.GetService('loading').LogInfo('ad URL:', adUrl)
            ads = corebrowserutil.GetStringFromURL(adUrl).read()
        except Exception as e:
            log.LogError('Failed to fetch ads', e)
            sys.exc_clear()
            self.CloseAd()
            return 
        ads = [ ad for ad in ads.split('\r\n') if ad ]
        for ad in ads:
            (imgpath, url,) = ad.split('|')
            didShowAd = settings.public.ui.Get(imgpath + 'Ad', 0)
            if not didShowAd or alwaysShowAd:
                try:
                    self.OpenAd(imgpath, url, hidden)
                except Exception as e:
                    log.LogError('Failed to display ad', e, imgpath, url)
                    sys.exc_clear()
                return 




    @bluepy.CCP_STATS_ZONE_METHOD
    def OpenAd(self, imgpath, url, hidden):
        adPar = uicls.Container(name='ad', parent=self, idx=0, width=690, height=282, left=0, top=0, state=uiconst.UI_NORMAL, align=uiconst.CENTER)
        mainclosex = uicls.Icon(icon='ui_38_16_220', parent=adPar, pos=(2, 1, 0, 0), align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, idx=0)
        mainclosex.OnClick = self.CloseAd
        ad = uicls.Sprite(name='adsprite', parent=adPar, width=690, height=282, left=0, top=0, state=uiconst.UI_NORMAL, color=(1.0, 1.0, 1.0, 0.0))
        (tex, w, h,) = sm.GetService('photo').GetTextureFromURL(imgpath)
        ad.rectWidth = ad.width = adPar.width = w
        ad.rectHeight = ad.height = adPar.height = h
        ad.rectLeft = 0
        ad.rectTop = 0
        ad.texture = tex
        ad.url = url
        ad.OnClick = (self.ClickAd, ad)
        if hidden:
            adPar.state = uiconst.UI_HIDDEN
        settings.public.ui.Set(imgpath + 'Ad', 1)
        sm.GetService('ui').Fade(0, 1.0, ad)
        sm.GetService('ui').Fade(0, 1.0, mainclosex)



    def ClickAd(self, ad):
        uthread.new(self.ClickURL, ad.url)



    def ShowAdIfAny(self):
        ad = uiutil.FindChild(self, 'ad')
        if ad:
            ad.state = uiconst.UI_NORMAL



    def HideAdIfAny(self):
        ad = uiutil.FindChild(self, 'ad')
        if ad:
            ad.state = uiconst.UI_HIDDEN



    def CloseAd(self, *args):
        ad = uiutil.FindChild(self, 'ad')
        if ad:
            ad.Close()



    def ClickURL(self, url, *args):
        blue.os.ShellExecute(url)



    def OnEsc(self):
        if not self.waitingForEula and self.pushButtons is not None:
            activePanelArgs = self.pushButtons.GetSelected()
            if activePanelArgs:
                activePanelName = activePanelArgs[0]
                self.pushButtons.DeselectAll()
            else:
                self.pushButtons.SelectPanelByName(mls.UI_GENERIC_SETTINGS)



    def OnButtonDeselected(self, args):
        args = args[0]
        if args == 'settings' and not self.reloading:
            sys = uicore.layer.systemmenu
            if sys.isopen:
                uthread.new(sys.CloseMenu)
        if self.pushButtons is None or self.pushButtons.destroyed:
            return 
        if self.pushButtons.GetSelected() is None:
            self.FadeOut()



    def CloseMenu(self, *args):
        uicore.cmd.OnEsc()



    def OnPushButtonNoneSelected(self, *args):
        self.ShowAdIfAny()
        if hasattr(self, 'motdText'):
            self.motdParent.state = uiconst.UI_NORMAL



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnButtonSelected(self, args):
        self.loadingPushButton = args
        self.HideAdIfAny()
        self.motdParent.state = uiconst.UI_HIDDEN
        self.suppressMotd = True
        args = args[0]
        if args != 'account':
            self.GetBackground()
        if args == 'settings':
            sys = uicore.layer.systemmenu
            if not sys.isopen:
                uthread.new(sys.OpenView)
        else:
            sys = uicore.layer.systemmenu
            if sys.isopen:
                uthread.new(sys.CloseMenu)
        if args in ('eula', 'patchinfo', 'news', 'support', 'account'):
            func = getattr(self, 'Load' + args.capitalize(), None)
            if func:
                func()
        self.loadingPushButton = 0



    def GetBackground(self, fade = 1):
        if self.bg is None:
            if self.sceneLoadedEvent and not self.sceneLoadedEvent.is_set():
                self.sceneLoadedEvent.wait()
            backgroundWrapper = BackgroundWrapper(self.fadeCont)
            backgroundWrapper.backgroundSprite.SetAlpha(0.0)
            self.bg = backgroundWrapper
        if fade:
            if self.bg.backgroundSprite.GetAlpha() != 1.0:
                uthread.new(self.FadeBG, self.bg.backgroundSprite.color.a, 1.0, 1, self.bg.backgroundSprite, time=1000.0)
        else:
            self.bg.backgroundSprite.SetAlpha(1.0)



    def FadeOut(self):
        if self.bg:
            uthread.new(self.FadeBG, 1.0, 0.0, 0, self.bg.backgroundSprite, time=1000.0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def FadeBG(self, fr, to, fadein, pic, time = 500.0):
        if self is None:
            return 
        ndt = 0.0
        start = blue.os.GetTime(1)
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start) / time, 1.0)
            if self is None or pic is None or pic.destroyed:
                break
            pic.SetAlpha(mathUtil.Lerp(fr, to, ndt))
            blue.pyos.synchro.Yield()

        if self is None:
            return 
        if not fadein:
            self.fadeCont.Flush()
            self.bg = None



    def OnComboChange(self, combo, header, value, *args):
        self.usernameEditCtrl.SetValue(value)
        self.passwordEditCtrl.SetValue('')
        uicore.registry.SetFocus(self.passwordEditCtrl)



    def GetEulaCCP(self, *args):
        thirdPartyInsert = ''
        thirdPartyInsert = mls.EVE_EULA_THIRDPARTYINSERT % {'tabName': '"%s"' % mls.UI_EULA3RDPARTY}
        thirdPartyInsert = thirdPartyInsert + '<br><br>'
        return mls.EVE_EULA2 % {'insert': thirdPartyInsert}



    def GetEulaOthers(self, *args):
        tgEula = ''
        if blue.win32.IsTransgaming():
            tgEula = mls.EVE_EULA_TRANSGAMING
        else:
            tgEula = mls.EVE_EULA_DIRECTX
        return tgEula + '<p><p>' + mls.EVE_EULA_CHROME + '<p><p>' + mls.EVE_EULA_XIPH



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadMotd(self, hidden = False):
        ip = self.serverIP
        try:
            extraParam = sm.StartService('patch').GetWebRequestParameters()
            ret = corebrowserutil.GetStringFromURL(WEB_EVE + '/motd.asp?server=%s&%s' % (ip, extraParam)).read()
        except Exception as e:
            log.LogError('Failed to fetch motd', e)
            sys.exc_clear()
            ret = ''
        if self.motdParent and not self.motdParent.destroyed:
            if ret and ret.startswith('MOTD '):
                ret = ret[5:]
                self.motdText = ret.decode('utf-8')
                if hidden:
                    self.motdParent.state = uiconst.UI_HIDDEN
                else:
                    self.motdParent.state = uiconst.UI_NORMAL
                self.sr.motdBrowser.LoadHTML('<html><body>%s</body></html>' % ret)
                self.motdParent.height = max(32, min(128, self.sr.motdBrowser.GetTotalHeight() + 10))
            else:
                self.motdParent.state = uiconst.UI_HIDDEN



    def LoadEula(self, *args):
        if getattr(self, 'eulaInited', 0):
            uicore.registry.SetFocus(self.eulaBrowser)
            return 
        self.sr.maintabs.SelectByIdx(0)
        uicore.registry.SetFocus(self.eulaBrowser)
        self.eulaInited = 1



    def LoadPatchinfo(self, *args):
        self.mainBrowser.GoTo(WEB_MBPATCHNOTES)
        uicore.registry.SetFocus(self.mainBrowser)



    def LoadNews(self, *args):
        newsURL = WEB_MYEVE + '/mb/news.asp?' + sm.GetService('patch').GetWebRequestParameters()
        if boot.region == 'optic':
            newsURL = WEB_EVE + '/gamenews/index.htm'
        self.mainBrowser.GoTo(newsURL)
        uicore.registry.SetFocus(self.mainBrowser)



    def LoadSupport(self, *args):
        self.mainBrowser.GoTo(WEB_SUPPORT)
        uicore.registry.SetFocus(self.mainBrowser)



    def LoadAccount(self, *args):
        self.ClickURL(WEB_ACCOUNT)
        self.pushButtons.DeselectAll()



    def SetMotdMessage(self, message):
        if self.motdParent and not self.motdParent.destroyed and not getattr(self, 'suppressMotd', False):
            self.sr.motdBrowser.LoadHTML('<html><body>%s</body></html>' % message)
            self.motdParent.height = max(32, min(128, self.sr.motdBrowser.GetTotalHeight() + 24))
            self.motdParent.state = uiconst.UI_NORMAL
        if message is None:
            self.motdParent.state = uiconst.UI_HIDDEN



    @bluepy.CCP_STATS_ZONE_METHOD
    def __StatusTextWorker(self):
        while not eve.session.userid:
            blue.pyos.synchro.Sleep(750)
            try:
                if getattr(self, 'serverStatusTextFunc', None) is not None:
                    if not getattr(self, 'connecting', 0):
                        self._Login__SetServerStatusText(refreshOnNone=True)
            except:
                log.LogException('Exception in status text worker')
                sys.exc_clear()




    @bluepy.CCP_STATS_ZONE_METHOD
    def __SetServerStatusText(self, refreshOnNone = False):
        if self.serverStatusTextFunc is None:
            self.ClearServerStatus()
            return 
        statusText = apply(self.serverStatusTextFunc[0])
        if statusText is None:
            self.ClearServerStatus()
            if refreshOnNone:
                uthread.new(self.UpdateServerStatus, False)
            return 
        (serverversion, serverbuild, serverUserCount,) = self.serverStatusTextFunc[1:]
        text = '%s: %s<br>%s: %s' % (mls.UI_LOGIN_SERVER,
         self.serverName,
         mls.UI_GENERIC_STATUS,
         statusText)
        if serverUserCount is not None:
            text += '<br>%s %s' % (util.FmtAmt(int(serverUserCount)), mls.UI_LOGIN_PLAYERS)
        if serverversion and serverbuild:
            if text.endswith(', '):
                text = self.serverStatusTextControl.text[:-2]
            if '%.2f' % serverversion != '%.2f' % boot.version or serverbuild > boot.build:
                text += '<br>%s %.2f.%s' % (mls.UI_LOGIN_VERSION, serverversion, serverbuild)
                text += '<color=0xffff0000> (%s).' % mls.UI_LOGIN_INCOMPATIBLE
        self.SetStatusText(text)



    def UpdateServerStatus(self, allowPatch = True):
        self.SetStatusText(mls.UI_LOGIN_CHECKINGSTATUS)
        self.serverStatusTextFunc = None
        blue.pyos.synchro.Yield()
        try:
            int(self.serverPort)
        except Exception as e:
            log.LogError(e)
            sys.exc_clear()
            self.SetStatusText('%s: %s' % (mls.UI_LOGIN_INVALIDPORTNUMBER, self.serverPort))
            self.serverStatusTextFunc = None
            return 
        serverUserCount = serverversion = serverbuild = servercodename = None
        patch = sm.GetService('patch')
        if boot.region == 'optic':
            isAutoPatch = self.serverIP == LIVE_SERVER1 or self.serverIP == LIVE_SERVER2 or self.serverIP in [TEST_SERVER1, TEST_SERVER2, TEST_SERVER3] or prefs.GetValue('forceAutopatch', 0) == 1
        else:
            isAutoPatch = self.serverIP == LIVE_SERVER or self.serverIP in [TEST_SERVER1, TEST_SERVER2, TEST_SERVER3] or prefs.GetValue('forceAutopatch', 0) == 1
        if isAutoPatch == False and [ arg for arg in blue.pyos.GetArg() if arg.lower().startswith('/patchinfourl:') ]:
            isAutoPatch = True
        if not allowPatch:
            isAutoPatch = False
        try:
            log.LogInfo('checking status of %s' % self.serverIP)
            try:
                (statusText, serverStatus,) = sm.GetService('machoNet').GetServerStatus('%s:%s' % (self.serverIP, self.serverPort))
            except UserError as e:
                if e.msg == 'AlreadyConnecting':
                    sys.exc_clear()
                    return 
                raise 
            if not self.isopen:
                return 
            self.serverStatus[self.serverIP] = (serverStatus.get('cluster_usercount', None),
             serverStatus.get('boot_version', None),
             serverStatus.get('boot_build', None),
             str(serverStatus.get('boot_codename', const.responseUnknown)),
             serverStatus.get('update_info', const.responseUnknown))
            (serverUserCount, serverversion, serverbuild, servercodename, updateinfo,) = self.serverStatus[self.serverIP]
            self.serverStatusTextFunc = None
            if serverUserCount:
                uthread.new(self.StartXFire, str(util.FmtAmt(serverUserCount)))
            if type(statusText) in (types.LambdaType, types.FunctionType, types.MethodType):
                self.serverStatusTextFunc = (statusText,
                 serverversion,
                 serverbuild,
                 serverUserCount)
            else:
                self.serverStatusTextFunc = (lambda statusText = statusText: statusText,
                 serverversion,
                 serverbuild,
                 serverUserCount)
            self._Login__SetServerStatusText()
            user = self.usernameEditCtrl.GetValue()
            if serverversion and serverbuild:
                if statusText == mls.UI_LOGIN_INCOMPATIBLE or '%.2f' % serverversion != '%.2f' % boot.version or serverbuild > boot.build:
                    if serverbuild > boot.build and isAutoPatch:
                        patch.Patch(user, self.serverIP, isForce=True)
                        patch.HandleProtocolMismatch()
            elif isAutoPatch:
                patch.Patch(user, self.serverIP, isForce=False)
            reasonText = None
            if callable(self.serverStatusTextFunc[0]):
                reasonText = self.serverStatusTextFunc[0]()
            else:
                reasonText = self.serverStatusTextFunc[0]
            if reasonText == mls.MACHONET_GETSERVERSTATUS_INCOMPATIBLE_PROTOCOL:
                patch.HandleProtocolMismatch()
            if updateinfo != const.responseUnknown:
                try:
                    patch.CheckServerUpgradeInfo(updateinfo)
                except Exception:
                    log.LogException()
                    sys.exc_clear()
        except Exception as e:
            log.LogError(e)
            sys.exc_clear()
            self.SetStatusText(mls.UI_LOGIN_UNABLETOCONNECTTO % {'ip': self.serverIP,
             'port': self.serverPort})
            self.serverStatusTextFunc = None
            if isAutoPatch:
                patch.Patch('', self.serverIP, isForce=False)
            patch.HandleProtocolMismatch()



    def StartXFire(self, serverUserCount):
        blue.pyos.synchro.Sleep(5000)
        sm.StartService('xfire').AddKeyValue('Users', serverUserCount)



    def SetStatusText(self, text):
        if self.serverStatusTextControl and not self.serverStatusTextControl.destroyed:
            if text is not None:
                self.serverStatusTextControl.text = text
            else:
                self.serverStatusTextControl.text = ''



    def ClearServerStatus(self, *args):
        self.SetStatusText('')
        self.serverStatusTextFunc = None
        return True



    def Confirm(self):
        self.Connect()



    def Connect(self, *args):
        if not self.waitingForEula:
            uthread.new(self._Connect)



    @bluepy.CCP_STATS_ZONE_METHOD
    def _Connect(self):
        if self.connecting:
            return 
        self.R2_2011_PauseCurves()
        self.connecting = True
        giveFocus = None
        try:
            try:
                user = self.usernameEditCtrl.GetValue()
                password = util.PasswordString(self.passwordEditCtrl.GetValue(raw=1))
                serverName = self.serverName
                eve.serverName = serverName
                invalidFields = []
                if user is None or len(user) == 0:
                    invalidFields.append(mls.UI_LOGIN_USERNAME.lower())
                    giveFocus = 'username'
                if password is None or len(password) == 0:
                    invalidFields.append(mls.UI_LOGIN_PASSWORD.lower())
                    giveFocus = 'password' if giveFocus is None else giveFocus
                invalidFieldsText = None
                if len(invalidFields):
                    invalidFieldsText = ''
                    while len(invalidFields) > 0:
                        field = invalidFields.pop(0)
                        if len(invalidFieldsText):
                            if len(invalidFields) == 0:
                                invalidFieldsText = '%s %s %s' % (invalidFieldsText, mls.UI_GENERIC_AND, field)
                            else:
                                invalidFieldsText = '%s, %s' % (invalidFieldsText, field)
                        else:
                            invalidFieldsText = field

                if invalidFieldsText is not None:
                    eve.Message('LoginParameterIncorrect', {'invalidFields': invalidFieldsText})
                    self.CancelLogin()
                    self.SetFocus(giveFocus)
                    return 
                log.LogInfo('server: %s selected' % self.serverIP)
                blue.pyos.synchro.Yield()
                if self.serverPort == sm.StartService('machoNet').defaultProxyPortOffset:
                    if self.serverIP not in self.serverStatus:
                        self.UpdateServerStatus()
                    try:
                        (serverUserCount, serverversion, serverbuild, servercodename, updateinfo,) = self.serverStatus[self.serverIP]
                        if serverbuild > boot.build:
                            if self.serverIP == LIVE_SERVER:
                                if eve.Message('PatchLiveServerConnectWrongVersion', {'serverVersion': serverbuild,
                                 'clientVersion': boot.build}, uiconst.YESNO) == uiconst.ID_YES:
                                    self.UpdateServerStatus()
                            else:
                                eve.Message('PatchTestServerWarning', {'serverVersion': serverbuild,
                                 'clientVersion': boot.build})
                            self.CancelLogin()
                            return 
                    except:
                        log.LogInfo('No serverStatus found for server %s' % self.serverIP)
                        sys.exc_clear()
                        eve.Message('UnableToConnectToServer')
                        self.CancelLogin()
                        return 
                sm.GetService('loading').ProgressWnd(mls.UI_LOGIN_LOGGINGIN, mls.UI_LOGIN_CONNECTINGCLUSTER, 1, 100)
                blue.pyos.synchro.Yield()
                eve.Message('OnConnecting')
                blue.pyos.synchro.Yield()
                eve.Message('OnConnecting2')
                blue.pyos.synchro.Yield()
                try:
                    sm.GetService('connection').Login([user,
                     password,
                     self.serverIP,
                     self.serverPort,
                     0])
                except:
                    self.CancelLogin()
                    raise 
                settings.public.ui.Set('username', user or '-')
                prefs.newbie = 0
                knownUserNames = settings.public.ui.Get('usernames', [])[:]
                if user and user not in knownUserNames:
                    knownUserNames.append(user)
                    settings.public.ui.Set('usernames', knownUserNames)
            except UserError as e:
                self.R2_2011_PlayCurves()
                if e.msg.startswith('LoginAuthFailed'):
                    giveFocus = 'password'
                eve.Message(e.msg, e.dict)
                self.SetFocus(giveFocus)

        finally:
            if not self.destroyed:
                self.connecting = 0




    def CancelLogin(self):
        self.R2_2011_PlayCurves()
        sm.GetService('loading').CleanUp()



    def SetFocus(self, where):
        if where is None:
            return 
        if where == 'username':
            uicore.registry.SetFocus(self.usernameEditCtrl)
        elif where == 'password':
            self.passwordEditCtrl.SetValue('')
            uicore.registry.SetFocus(self.passwordEditCtrl)



exports = {'login.servers': SERVERS,
 'login.GetServerIP': GetServerIP}

