import service
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import util
import skillUtil
import listentry
import base
import uicls
import uiconst
PLEX_URL = 'https://secure.eveonline.com/PLEX.aspx'

class CharacterSheet(service.Service):
    __exportedcalls__ = {'Show': [],
     'SetHint': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.charactersheet'
    __notifyevents__ = ['ProcessSessionChange',
     'OnGodmaSkillStartTraining',
     'OnGodmaSkillTrainingStopped',
     'OnGodmaSkillTrained',
     'OnGodmaItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnRankChange',
     'OnCloneJumpUpdate',
     'OnKillNotification',
     'OnSessionChanged',
     'OnCertificateIssued',
     'OnCertVisibilityChange',
     'OnUpdatedMedalsAvailable',
     'OnUpdatedMedalStatusAvailable',
     'OnRespecInfoUpdated',
     'OnGodmaSkillTrainingSaved',
     'OnGodmaSkillInjected',
     'OnSkillStarted',
     'OnSkillQueueRefreshed',
     'OnCloneTypeUpdated',
     'OnFreeSkillPointsChanged_Local']
    __servicename__ = 'charactersheet'
    __displayname__ = 'Character Sheet Client Service'
    __dependencies__ = ['clonejump']
    __startupdependencies__ = ['settings', 'skills', 'neocom']

    def Run(self, memStream = None):
        self.LogInfo('Starting Character Sheet')
        sm.FavourMe(self.OnSessionChanged)
        self.Reset()
        if not sm.GetService('skills').SkillInTraining():
            sm.GetService('neocom').Blink('charactersheet')



    def Stop(self, memStream = None):
        self.entryTmpl = None
        self.bio = None
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()



    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()



    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed:
                wnd.sr.employmentList = None
                selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'employment' ]
                if selection:
                    self.showing = None
                    self.Load('employment')



    def OnRankChange(self, oldrank, newrank):
        if not session.warfactionid:
            return 
        (rankLabel, rankDescription,) = uix.GetRankLabel(session.warfactionid, newrank)
        if newrank > oldrank:
            blinkMsg = cfg.GetMessage('RankGained', {'rank': rankLabel}).text
        else:
            blinkMsg = cfg.GetMessage('RankLost', {'rank': rankLabel}).text
        self.ReloadMyRanks()
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)



    def OnGodmaSkillStartTraining(self, *args):
        sm.GetService('neocom').BlinkOff('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnGodmaSkillTrainingStopped(self, skillID, silent = 0, *args):
        if not silent:
            sm.GetService('neocom').Blink('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnGodmaSkillTrained(self, skillID):
        sm.GetService('neocom').Blink('charactersheet')
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()
        self.LoadGeneralInfo()



    def OnGodmaSkillTrainingSaved(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnGodmaSkillInjected(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnGodmaItemChange(self, item, change):
        if const.ixLocationID in change and item.categoryID == const.categoryImplant and item.flagID in [const.flagBooster, const.flagImplant]:
            sm.GetService('neocom').Blink('charactersheet')
            if self.showing == 'myimplants_boosters':
                self.ShowMyImplantsAndBoosters()
        elif const.ixFlag in change and item.categoryID == const.categorySkill:
            if self.showing == 'myskills_skills':
                self.ReloadMySkills()
        self.LoadGeneralInfo()



    def OnAttribute(self, attributeName, item, value):
        if attributeName == 'skillPoints' and self.showing == 'myskills_skills':
            self.ReloadMySkills()
        elif attributeName in ('memory', 'intelligence', 'willpower', 'perception', 'charisma') and self.showing == 'myattributes':
            self.UpdateMyAttributes(util.LookupConstValue('attribute%s' % attributeName.capitalize(), 0), value)



    def OnAttributes(self, changes):
        for (attributeName, item, value,) in changes:
            self.OnAttribute(attributeName, item, value)




    def OnCloneJumpUpdate(self):
        if self.showing == 'jumpclones':
            self.ShowJumpClones()



    def OnKillNotification(self):
        sm.StartService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetRecentShipKillsAndLosses', 25, None)



    def OnCertificateIssued(self, certificateID = None):
        if certificateID:
            (certLabel, grade, certDescription,) = uix.GetCertificateLabel(certificateID)
            blinkMsg = cfg.GetMessage('CertAwarded', {'certificate': certLabel}).text
        else:
            blinkMsg = cfg.GetMessage('CertsAwarded').text
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)
        if self.showing == 'mycertificates_certificates':
            self.ShowMyCerts()



    def OnUpdatedMedalsAvailable(self):
        sm.GetService('neocom').Blink('charactersheet')
        wnd = self.GetWnd()
        if wnd is None:
            return 
        wnd.sr.decoMedalList = None
        if self.showing.startswith('mydecorations_'):
            self.ShowMyDecorations(self.showing)



    def OnUpdatedMedalStatusAvailable(self):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        if self.showing.startswith('mydecorations_permissions'):
            wnd.sr.decoMedalList = None
            self.ShowMyDecorations(self.showing)



    def OnRespecInfoUpdated(self):
        if self.showing == 'myattributes':
            self.ShowMyAttributes()



    def OnSkillStarted(self, skillID = None, level = None):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnSkillQueueRefreshed(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def OnCloneTypeUpdated(self, newCloneType):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetCloneTypeID')
        self.LoadGeneralInfo()
        sm.ScatterEvent('OnCloneTypeUpdatedClient')



    def OnFreeSkillPointsChanged_Local(self):
        if self.showing == 'myskills_skills':
            self.ReloadMySkills()



    def Reset(self):
        self.panels = []
        self.standingsinited = 0
        self.mydecorationsinited = 0
        self.standingtabs = None
        self.mydecorationstabs = None
        self.skillsinited = 0
        self.skilltabs = None
        self.killsinited = 0
        self.killstabs = None
        self.killentries = 25
        self.showing = None
        self.skillTimer = None
        self.jumpClones = False
        self.jumpCloneImplants = False
        self.bio = None
        self.visibilityChanged = {}
        self.daysLeft = -1



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            return wnd



    def GetWnd(self, getnew = 0):
        if not sm.IsServiceRunning('window'):
            return 
        wnd = sm.GetService('window').GetWindow('charactersheet')
        if not wnd and getnew:
            recentT3ShipLoss = settings.char.generic.Get('skillLossNotification', None)
            if recentT3ShipLoss is not None:
                eve.Message('RecentSkillLossDueToT3Ship', {'skillTypeID': (TYPEID, recentT3ShipLoss.skillTypeID),
                 'skillPoints': recentT3ShipLoss.skillPoints,
                 'shipTypeID': (TYPEID, recentT3ShipLoss.shipTypeID)})
                settings.char.generic.Set('skillLossNotification', None)
            wnd = sm.GetService('window').GetWindow('charactersheet', create=1, decoClass=form.CharacterSheet)
            wnd.scope = 'station_inflight'
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.sr.standingsinited = 0
            wnd.sr.skillsinited = 0
            wnd.sr.killsinited = 0
            wnd.sr.mydecorationsinited = 0
            wnd.sr.certsinited = 0
            wnd.sr.pilotlicenceinited = 0
            wnd.SetScope('station_inflight')
            wnd.SetCaption(mls.UI_SHARED_CHARACTERSHEET)
            wnd.OnClose_ = self.OnCloseWnd
            wnd.MouseDown = self.OnWndMouseDown
            wnd.IsBrowser = 1
            wnd.GoTo = self.GoTo
            wnd.SetWndIcon('ui_2_64_16')
            wnd.HideMainIcon()
            leftSide = uicls.Container(name='leftSide', parent=wnd.sr.main, align=uiconst.TOLEFT, left=const.defaultPadding, width=settings.user.ui.Get('charsheetleftwidth', 200), idx=0)
            wnd.sr.leftSide = leftSide
            wnd.sr.nav = uicls.Scroll(name='senderlist', parent=leftSide)
            wnd.sr.nav.top = const.defaultPadding
            wnd.sr.nav.height = const.defaultPadding
            wnd.sr.nav.OnSelectionChange = self.OnSelectEntry
            mainArea = uicls.Container(name='mainArea', parent=wnd.sr.main, align=uiconst.TOALL)
            wnd.sr.buttonParCert = uicls.Container(name='buttonParCert', align=uiconst.TOBOTTOM, height=25, parent=mainArea, state=uiconst.UI_HIDDEN)
            wnd.sr.buttonParDeco = uicls.Container(name='buttonParDeco', align=uiconst.TOBOTTOM, height=25, parent=mainArea, state=uiconst.UI_HIDDEN)
            buttonCert = uicls.Container(name='buttonCert', align=uiconst.TOBOTTOM, height=20, parent=wnd.sr.buttonParCert)
            buttonDeco = uicls.Container(name='buttonDeco', align=uiconst.TOBOTTOM, height=20, parent=wnd.sr.buttonParDeco)
            uicls.Container(name='push', parent=wnd.sr.buttonParCert, height=5, align=uiconst.TOBOTTOM)
            uicls.Container(name='push', parent=wnd.sr.buttonParDeco, height=5, align=uiconst.TOBOTTOM)
            mainArea2 = uicls.Container(name='mainArea2', parent=mainArea, align=uiconst.TOALL)
            divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding - 1, parent=mainArea2, state=uiconst.UI_NORMAL)
            divider.Startup(leftSide, 'width', 'x', 84, 220)
            wnd.sr.divider = divider
            uicls.Container(name='push', parent=mainArea2, state=uiconst.UI_PICKCHILDREN, width=const.defaultPadding, align=uiconst.TORIGHT)
            wnd.sr.skillpanel = uicls.Container(name='skillpanel', parent=mainArea2, align=uiconst.TOTOP, height=24, state=uiconst.UI_HIDDEN)
            wnd.sr.certificatepanel = uicls.Container(name='certificatepanel', parent=mainArea2, align=uiconst.TOTOP, height=24, state=uiconst.UI_HIDDEN)
            btn = uicls.Button(parent=wnd.sr.certificatepanel, label=mls.UI_CMD_OPENCERTIFICATEPLANNER, func=self.OpenCertificateWindow, pos=(0, 1, 0, 0), alwaysLite=True, align=uiconst.CENTERRIGHT)
            btn = uicls.Button(parent=wnd.sr.skillpanel, label=mls.UI_SHARED_SQ_OPENTRAININGQUEUE, func=self.OpenSkillQueueWindow, pos=(0, 1, 0, 0), alwaysLite=True, align=uiconst.CENTERRIGHT)
            btn.name = 'characterSheetOpenTrainingQueue'
            wnd.sr.certificatepanel.height = btn.height
            wnd.sr.skillpanel.height = btn.height
            btns = [(mls.UI_CMD_SAVE,
              self.SaveDecorationPermissionsChanges,
              (),
              64), (mls.UI_CMD_SETALL,
              self.SetAllDecorationPermissions,
              (),
              64)]
            uicls.ButtonGroup(btns=btns, parent=buttonDeco)
            btns = [(mls.UI_CMD_SAVE,
              self.SaveCertificatePermissionsChanges,
              (),
              64), (mls.UI_CMD_SETALL,
              self.SetAllCertificatePermissions,
              (),
              64)]
            uicls.ButtonGroup(btns=btns, parent=buttonCert)
            wnd.sr.scroll = uicls.Scroll(parent=mainArea2, padding=(0,
             const.defaultPadding,
             0,
             const.defaultPadding))
            wnd.sr.scroll.sr.id = 'charactersheetscroll'
            wnd.sr.hint = None
            wnd.sr.employmentList = None
            wnd.sr.decoRankList = None
            wnd.sr.decoMedalList = None
            wnd.sr.mainArea = mainArea
            wnd.sr.bioparent = uicls.Container(name='bio', parent=mainArea2, state=uiconst.UI_HIDDEN, padding=(0,
             const.defaultPadding,
             0,
             const.defaultPadding))
            self.LoadGeneralInfo()
            navEntries = self.GetNavEntries(wnd)
            scrolllist = []
            for (label, panel, icon, key, order, UIName,) in navEntries:
                data = util.KeyVal()
                data.text = label
                data.label = label
                data.icon = icon
                data.key = key
                data.hint = label
                data.name = UIName
                if key == 'killrights':
                    data.hint = mls.UI_INFOWND_KILLRIGHTSINFO
                scrolllist.append(listentry.Get('IconEntry', data=data))

            if wnd and wnd.destroyed:
                return 
            wnd.sr.nav.Load(contentList=scrolllist)
            wnd.sr.nav.SetSelected(min(len(navEntries) - 1, settings.char.ui.Get('charactersheetsel', 0)))
            self.visibilityChanged = {}
        return wnd



    def OnCertVisibilityChange(self, certID, flag, serverVisibility):
        wnd = self.GetWnd()
        if flag == serverVisibility:
            if certID in self.visibilityChanged:
                self.visibilityChanged.pop(certID)
        else:
            self.visibilityChanged[certID] = flag



    def OpenCertificateWindow(self, *args):
        sm.StartService('certificates').OpenCertificateWindow()



    def OpenSkillQueueWindow(self, *args):
        uicore.cmd.OpenSkillQueueWindow()



    def GetNavEntries(self, wnd):
        nav = [[mls.UI_GENERIC_SKILLS,
          wnd.sr.scroll,
          'ui_50_64_13',
          'myskills',
          settings.user.ui.Get('charsheetorder_myskills', 0),
          'characterSheetMenuSkillsBtn'],
         [mls.UI_SHARED_CERTIFICATES,
          wnd.sr.scroll,
          'ui_79_64_1',
          'mycertificates',
          settings.user.ui.Get('charsheetorder_mycertificates', 1),
          'characterSheetMenuCertificatesBtn'],
         [mls.UI_GENERIC_DECORATIONS,
          wnd.sr.scroll,
          'ui_35_64_9',
          'mydecorations',
          settings.user.ui.Get('charsheetorder_mydecorations', 2),
          'characterSheetMenuDecorationsBtn'],
         [mls.UI_GENERIC_ATTRIBUTES,
          wnd.sr.scroll,
          'ui_25_64_15',
          'myattributes',
          settings.user.ui.Get('charsheetorder_myattributes', 3),
          'characterSheetMenuAttributesBtn'],
         [mls.UI_GENERIC_AUGMENTATIONS,
          wnd.sr.scroll,
          'ui_25_64_14',
          'myimplants_boosters',
          settings.user.ui.Get('charsheetorder_myimplants_boosters', 4),
          'characterSheetMenuImplantsBtn'],
         [mls.UI_GENERIC_JUMPCLONES,
          wnd.sr.scroll,
          'ui_8_64_16',
          'jumpclones',
          settings.user.ui.Get('charsheetorder_jumpclones', 5),
          'characterSheetMenuJumpclonesBtn'],
         [mls.UI_GENERIC_BIO,
          wnd.sr.bioparent,
          'ui_7_64_8',
          'bio',
          settings.user.ui.Get('charsheetorder_bio', 6),
          'characterSheetMenuBioBtn'],
         [mls.UI_GENERIC_EMPLOYMENTHISTORY,
          wnd.sr.scroll,
          'ui_7_64_6',
          'employment',
          settings.user.ui.Get('charsheetorder_employment', 7),
          'characterSheetMenuEmploymentBtn'],
         [mls.UI_GENERIC_STANDINGS,
          wnd.sr.scroll,
          'ui_25_64_10',
          'mystandings',
          settings.user.ui.Get('charsheetorder_mystandings', 8),
          'characterSheetMenuStandingBtn'],
         [mls.UI_GENERIC_SECURITYSTATUS,
          wnd.sr.scroll,
          'ui_7_64_7',
          'securitystatus',
          settings.user.ui.Get('charsheetorder_securitystatus', 9),
          'characterSheetMenuSecurityStatusBtn'],
         [mls.UI_GENERIC_KILLRIGHTS,
          wnd.sr.scroll,
          'ui_26_64_5',
          'killrights',
          settings.user.ui.Get('charsheetorder_killrights', 10),
          'characterSheetMenuKillRightsBtn'],
         [mls.UI_GENERIC_COMBATLOG,
          wnd.sr.scroll,
          'ui_50_64_15',
          'mykills',
          settings.user.ui.Get('charsheetorder_mykills', 11),
          'characterSheetMenuKillsBtn']]
        if boot.region != 'optic':
            nav.append([mls.UI_GENERIC_PILOTLICENSE,
             wnd.sr.scroll,
             'ui_57_64_3',
             'pilotlicense',
             settings.user.ui.Get('charsheetorder_pilotlicense', 12),
             'characterSheetMenuPilotLicenseBtn'])
        navEntries = []
        for each in nav:
            navEntries.append((each[4], each))

        navEntries = uiutil.SortListOfTuples(navEntries)
        return navEntries



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.sr.scroll.ShowHint(hintstr)



    def OnCloseWnd(self, wnd, *args):
        if self.showing == 'bio':
            self.AutoSaveBio()
        self.bioinited = 0
        self.showing = None
        settings.user.ui.Set('charsheetleftwidth', wnd.sr.leftSide.width)
        self.panels = []



    def OnWndMouseDown(self, *args):
        sm.GetService('neocom').BlinkOff('charactersheet')



    def OnSelectEntry(self, node):
        if node != []:
            self.Load(node[0].key)
            settings.char.ui.Set('charactersheetselection', node[0].idx)



    def Load(self, key):
        wnd = self.GetWnd()
        if not wnd:
            return 
        if getattr(self, 'loading', 0) or self.showing == key:
            return 
        self.loading = 1
        if self.showing == 'bio':
            self.AutoSaveBio()
        for each in [wnd.sr.scroll, wnd.sr.bioparent]:
            each.state = uiconst.UI_HIDDEN

        for uielement in ['standingtabs',
         'killstabs',
         'skilltabs',
         'btnContainer',
         'mydecorationstabs',
         'buttonParCert',
         'buttonParDeco',
         'certificatepanel',
         'certtabs',
         'skillpanel']:
            e = getattr(wnd.sr, uielement, None)
            if e:
                e.state = uiconst.UI_HIDDEN

        if key.startswith('pilotlicense'):
            wnd.sr.scroll.Clear()
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if self.daysLeft == -1:
                charDetails = sm.RemoteSvc('charUnboundMgr').GetCharacterToSelect(eve.session.charid)
                self.daysLeft = getattr(charDetails, 'daysLeft', None)
            data = {'daysLeft': self.daysLeft,
             'buyPlexOnMarket': self.BuyPlexOnMarket,
             'buyPlexOnline': self.BuyPlexOnline}
            wnd.sr.pilotLicenceEntry = listentry.Get('PilotLicence', data)
            wnd.sr.scroll.Load(contentList=[wnd.sr.pilotLicenceEntry])
        elif key.startswith('mystandings'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.standingsinited:
                wnd.sr.standingsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[mls.UI_GENERIC_LIKEDBY,
                  wnd.sr.scroll,
                  self,
                  'mystandings_to_positive'], [mls.UI_GENERIC_DISLIKEDBY,
                  wnd.sr.scroll,
                  self,
                  'mystandings_to_negative']], groupID='cs_standings')
                wnd.sr.standingtabs = tabs
                self.loading = 0
                wnd.sr.standingtabs.AutoSelect()
                return 
            if getattr(wnd.sr, 'standingtabs', None):
                wnd.sr.standingtabs.state = uiconst.UI_NORMAL
            wnd.sr.standingtabs.state = uiconst.UI_NORMAL
            if key == 'mystandings':
                self.loading = 0
                wnd.sr.standingtabs.AutoSelect()
                return 
            self.SetHint()
            if key == 'mystandings_to_positive':
                positive = True
            else:
                positive = False
            self.ShowStandings(positive)
        elif key.startswith('myskills'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.skillsinited:
                wnd.sr.skillsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[mls.UI_GENERIC_SKILLS,
                  wnd.sr.scroll,
                  self,
                  'myskills_skills'], [mls.UI_GENERIC_HISTORY,
                  wnd.sr.scroll,
                  self,
                  'myskills_skillhistory'], [mls.UI_GENERIC_SETTINGS,
                  wnd.sr.scroll,
                  self,
                  'myskills_settings']], groupID='cs_skills', UIIDPrefix='characterSheetTab')
                wnd.sr.skilltabs = tabs
                self.loading = 0
                wnd.sr.skilltabs.AutoSelect()
                return 
            if getattr(wnd.sr, 'skilltabs', None):
                wnd.sr.skilltabs.state = uiconst.UI_NORMAL
            if key == 'myskills':
                if self.showing == 'myskills_skills':
                    if getattr(wnd.sr, 'skillpanel', None):
                        wnd.sr.skillpanel.state = uiconst.UI_NORMAL
                self.loading = 0
                wnd.sr.skilltabs.AutoSelect()
                return 
            self.SetHint()
            self.ShowSkills(key)
        elif key.startswith('mydecorations'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.mydecorationsinited:
                wnd.sr.mydecorationsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[mls.UI_GENERIC_RANKS,
                  wnd.sr.scroll,
                  self,
                  'mydecorations_ranks'], [mls.UI_GENERIC_MEDALS,
                  wnd.sr.scroll,
                  self,
                  'mydecorations_medals'], [mls.UI_SHARED_PERMISSIONS,
                  wnd.sr.scroll,
                  self,
                  'mydecorations_permissions']], groupID='cs_decorations')
                wnd.sr.mydecorationstabs = tabs
                self.loading = 0
                wnd.sr.mydecorationstabs.AutoSelect()
                return 
            if getattr(wnd.sr, 'mydecorationstabs', None):
                wnd.sr.mydecorationstabs.state = uiconst.UI_NORMAL
            if key == 'mydecorations':
                self.loading = 0
                wnd.sr.mydecorationstabs.AutoSelect()
                if self.showing == 'mydecorations_permissions':
                    wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
                return 
            self.SetHint()
            self.ShowMyDecorations(key)
        elif key.startswith('mykills'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.killsinited:
                wnd.sr.killsinited = 1
                btnContainer = uicls.Container(name='pageBtnContainer', parent=wnd.sr.mainArea, align=uiconst.TOBOTTOM, idx=0, padBottom=4)
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                btn.SetAlign(uiconst.CENTERRIGHT)
                btn.hint = mls.UI_GENERIC_VIEWMORE
                btn.sr.icon.LoadIcon('ui_23_64_2')
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                btn.SetAlign(uiconst.CENTERLEFT)
                btn.hint = mls.UI_GENERIC_PREVIOUS
                btn.sr.icon.LoadIcon('ui_23_64_1')
                btnContainer.height = max([ c.height for c in btnContainer.children ])
                wnd.sr.btnContainer = btnContainer
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[mls.UI_GENERIC_KILLS,
                  wnd.sr.scroll,
                  self,
                  'mykills_kills'], [mls.UI_GENERIC_LOSSES,
                  wnd.sr.scroll,
                  self,
                  'mykills_losses'], [mls.UI_GENERIC_SETTINGS,
                  wnd.sr.scroll,
                  self,
                  'mykills_settings']], groupID='cs_kills')
                wnd.sr.killstabs = tabs
                self.loading = 0
                wnd.sr.killstabs.AutoSelect()
                return 
            if getattr(wnd.sr, 'killstabs', None):
                wnd.sr.killstabs.state = uiconst.UI_NORMAL
            if key == 'mykills':
                self.loading = 0
                wnd.sr.killstabs.AutoSelect()
                return 
            self.SetHint()
            self.ShowKills(key)
        elif key.startswith('mycertificates'):
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            if not wnd.sr.certsinited:
                wnd.sr.certsinited = 1
                tabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[mls.UI_SHARED_CERTIFICATES,
                  wnd.sr.scroll,
                  self,
                  'mycertificates_certificates'], [mls.UI_SHARED_PERMISSIONS,
                  wnd.sr.scroll,
                  self,
                  'mycertificates_permissions'], [mls.UI_GENERIC_SETTINGS,
                  wnd.sr.scroll,
                  self,
                  'mycertificates_settings']], groupID='cs_certificates')
                wnd.sr.certtabs = tabs
                self.loading = 0
                wnd.sr.certtabs.AutoSelect()
                return 
            if hasattr(wnd.sr, 'certtabs'):
                wnd.sr.certtabs.state = uiconst.UI_NORMAL
            if key == 'mycertificates':
                self.loading = 0
                wnd.sr.certtabs.AutoSelect()
            else:
                self.SetHint()
                self.ShowCertificates(key)
        elif wnd.sr.standingsinited:
            wnd.sr.standingtabs.state = uiconst.UI_HIDDEN
        if wnd.sr.skillsinited:
            wnd.sr.skilltabs.state = uiconst.UI_HIDDEN
        if wnd.sr.killsinited:
            wnd.sr.killstabs.state = uiconst.UI_HIDDEN
        if wnd.sr.mydecorationsinited:
            wnd.sr.mydecorationstabs.state = uiconst.UI_HIDDEN
        if wnd.sr.certsinited:
            wnd.sr.certtabs.state = uiconst.UI_HIDDEN
        self.SetHint()
        if key == 'myattributes':
            self.ShowMyAttributes()
        elif key == 'myimplants_boosters':
            self.ShowMyImplantsAndBoosters()
        elif key == 'bio':
            self.ShowMyBio()
        elif key == 'securitystatus':
            self.ShowSecurityStatus()
        elif key == 'killrights':
            self.ShowKillRights()
        elif key == 'jumpclones':
            self.ShowJumpClones()
        elif key == 'employment':
            self.ShowEmploymentHistory()
        elif key == 'mysettings':
            self.ShowSettings()
        self.showing = key
        self.loading = 0



    def BuyPlexOnMarket(self, *args):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, const.typePilotLicence, None)



    def BuyPlexOnline(self, *args):
        self.GoTo(PLEX_URL)



    def LoadGeneralInfo(self):
        if getattr(self, 'loadingGeneral', 0):
            return 
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        self.loadingGeneral = 1
        uix.Flush(wnd.sr.topParent)
        characterName = cfg.eveowners.Get(eve.session.charid).name
        if not getattr(self, 'charMgr', None):
            self.charMgr = sm.RemoteSvc('charMgr')
        if not getattr(self, 'cc', None):
            self.charsvc = sm.GetService('cc')
        wnd.sr.charinfo = charinfo = self.charMgr.GetPublicInfo(eve.session.charid)
        if settings.user.ui.Get('charsheetExpanded', 1):
            lineCount = 12
            if eve.session.allianceid:
                lineCount = 13
            mtext = 'Xg<br>' * lineCount
            mtext = mtext[:-4]
            th = uix.GetTextHeight(mtext, autoWidth=1)
            wnd.SetTopparentHeight(max(175, th) + const.defaultPadding * 2 + 2)
            uiutil.Update(self)
            parent = wnd.sr.topParent
            wnd.sr.picParent = uicls.Container(name='picpar', parent=parent, align=uiconst.TOPLEFT, width=200, height=200, left=const.defaultPadding, top=16)
            wnd.sr.pic = uicls.Sprite(parent=wnd.sr.picParent, align=uiconst.TOALL, left=1, top=1, height=1, width=1)
            wnd.sr.pic.OnClick = self.OpenPortraitWnd
            wnd.sr.pic.cursor = uiconst.UICURSOR_MAGNIFIER
            uicls.Frame(parent=wnd.sr.picParent)
            sm.GetService('photo').GetPortrait(eve.session.charid, 256, wnd.sr.pic)
            wnd.sr.nameText = uicls.Label(text=characterName, parent=wnd.sr.topParent, left=200 + const.defaultPadding * 2 + 6, top=12, fontsize=18)
            wnd.sr.raceinfo = raceinfo = self.charsvc.GetData('races', ['raceID', charinfo.raceID])
            wnd.sr.bloodlineinfo = bloodlineinfo = self.charsvc.GetData('bloodlines', ['bloodlineID', charinfo.bloodlineID])
            wnd.sr.schoolinfo = schoolinfo = self.charsvc.GetData('schools', ['schoolID', charinfo.schoolID])
            wnd.sr.ancestryinfo = ancestryinfo = self.charsvc.GetData('ancestries', ['ancestryID', charinfo.ancestryID])
            if wnd is None or wnd.destroyed:
                self.loadingGeneral = 0
                return 
            securityStatus = sm.GetService('standing').GetMySecurityRating()
            securityStatus = '%.2f' % securityStatus
            cloneTypeID = self.GetCloneTypeID()
            godmaInfo = sm.GetService('godma').GetType(cloneTypeID)
            cloneLocation = sm.RemoteSvc('charMgr').GetHomeStation()
            if cloneLocation:
                cloneLocationInfo = sm.GetService('ui').GetStation(cloneLocation)
                if cloneLocationInfo:
                    cloneLocationHint = '%s (%s)' % (cfg.evelocations.Get(cloneLocation).name, cfg.evelocations.Get(cloneLocationInfo.solarSystemID).name)
                else:
                    cloneLocationHint = cfg.evelocations.Get(cloneLocation).name
                systemID = cloneLocationInfo.solarSystemID
                cloneLocation = cfg.evelocations.Get(systemID).name
            else:
                cloneLocation = mls.UI_GENERIC_UNKNOWN
                cloneLocationHint = ''
            alliance = ''
            if eve.session.allianceid:
                cfg.eveowners.Prime([eve.session.allianceid])
                alliance = (mls.UI_GENERIC_ALLIANCE, cfg.eveowners.Get(eve.session.allianceid).name, '')
            faction = ''
            if eve.session.warfactionid:
                fac = sm.StartService('facwar').GetFactionalWarStatus()
                faction = (mls.UI_GENERIC_MILITIA, cfg.eveowners.Get(fac.factionID).name, '')
            textList = [(mls.UI_GENERIC_SKILLPOINTS, util.FmtAmt(sm.GetService('skills').GetSkillPoints()), ''),
             (mls.UI_GENERIC_CLONE, '%s (%s)' % (cfg.invtypes.Get(cloneTypeID).name, util.FmtAmt(godmaInfo.skillPointsSaved)), ''),
             (mls.UI_GENERIC_HOMESYSTEM, cloneLocation, cloneLocationHint),
             (mls.UI_GENERIC_CHARACTERBACKGROUND, '%s - %s - %s' % (Tr(raceinfo.raceName, 'character.races.raceName', raceinfo.dataID), Tr(bloodlineinfo.bloodlineName, 'character.bloodlines.bloodlineName', bloodlineinfo.dataID), Tr(ancestryinfo.ancestryName, 'character.ancestries.ancestryName', ancestryinfo.dataID)), '%s, %s, %s' % (mls.UI_GENERIC_RACE, mls.UI_GENERIC_BLOODLINE, mls.UI_CHARCREA_ANCESTRY)),
             (mls.UI_CORP_DATEOFBIRTH, util.FmtDate(charinfo.createDateTime, 'll'), ''),
             (mls.SCHOOL, Tr(schoolinfo.schoolName, 'dbo.chrSchools.schoolName', schoolinfo.schoolID), ''),
             (mls.UI_GENERIC_CORPORATION, cfg.eveowners.Get(eve.session.corpid).name, ''),
             (mls.UI_GENERIC_SECURITYSTATUS, securityStatus, '')]
            if faction:
                textList.insert(len(textList) - 1, faction)
            if alliance:
                textList.insert(len(textList) - 1, alliance)
            top = 34
            left = 200 + const.defaultPadding * 2
            for (label, value, hint,) in textList:
                text = '%s<t><b>%s</b>' % (label, value)
                label = uicls.Label(text=text, parent=wnd.sr.topParent, tabs=[90, 476], left=left, top=top, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
                label.hint = hint
                label._tabMargin = 0
                top += 16

            wnd.SetTopparentHeight(220)
        else:
            wnd.SetTopparentHeight(18)
        charsheetExpanded = settings.user.ui.Get('charsheetExpanded', 1)
        if not charsheetExpanded:
            v = uicls.Label(text='%s' % characterName, parent=wnd.sr.topParent, left=8, top=1, fontsize=12, letterspace=2, uppercase=1, state=uiconst.UI_DISABLED)
        a = uicls.Label(text=[mls.UI_CMD_EXPAND, mls.UI_CMD_COLLAPSE][charsheetExpanded], parent=wnd.sr.topParent, left=18, top=3, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.ToggleGeneral
        expander = uicls.Sprite(parent=wnd.sr.topParent, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath=['res:/UI/Texture/Shared/expanderDown.png', 'res:/UI/Texture/Shared/expanderUp.png'][charsheetExpanded], align=uiconst.TOPRIGHT)
        expander.OnClick = self.ToggleGeneral
        self.loadingGeneral = 0



    def GetCloneTypeID(self):
        cloneTypeID = sm.RemoteSvc('charMgr').GetCloneTypeID()
        if not cloneTypeID:
            cloneTypeID = const.typeCloneGradeAlpha
        return cloneTypeID



    def OpenPortraitWnd(self, *args):
        wnd = sm.StartService('window').GetWindow('PortraitWindow')
        if wnd is None:
            wnd = sm.StartService('window').GetWindow('PortraitWindow', 1, decoClass=form.PortraitWindow, charID=session.charid)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            wnd.Load(session.charid)



    def ToggleGeneral(self, *args):
        charsheetExpanded = not settings.user.ui.Get('charsheetExpanded', 1)
        settings.user.ui.Set('charsheetExpanded', charsheetExpanded)
        self.LoadGeneralInfo()



    def ShowSecurityStatus(self):
        data = sm.RemoteSvc('standing2').GetStandingTransactions(const.ownerCONCORD, eve.session.charid, 1, None, None, None)
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if not wnd:
            return 
        wnd.sr.scroll.sr.id = 'charsheet_securitystatus'
        wnd.sr.scroll.Clear()
        scrolllist = []
        headers = []
        fromName = cfg.eveowners.Get(const.ownerCONCORD).name
        for each in data:
            when = util.FmtDate(each.eventDateTime, 'ls')
            (subject, body,) = util.FmtStandingTransaction(each)
            mod = '%-2.4f' % (each.modification * 100.0)
            while mod and mod[-1] == '0':
                if mod[-2:] == '.0':
                    break
                mod = mod[:-1]

            text = '%s<t>%s%%<t>%s' % (when, mod, subject)
            scrolllist.append(listentry.Get('StandingTransaction', {'sort_%s' % mls.UI_GENERIC_DATE: each.eventDateTime,
             'sort_%s' % mls.UI_GENERIC_CHANGE: each.modification,
             'line': 1,
             'text': text,
             'details': body}))

        if not wnd:
            return 
        headers = [mls.UI_GENERIC_DATE, mls.UI_GENERIC_CHANGE, mls.UI_GENERIC_SUBJECT]
        wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_GENERIC_NOSECURITYSTATUSCHANGES)



    def ShowMyDecorations(self, key = None):
        wnd = self.GetWnd()
        if wnd is None:
            return 
        wnd.sr.buttonParDeco.state = uiconst.UI_HIDDEN
        if key == 'mydecorations_ranks':
            self.ShowMyRanks()
        elif key == 'mydecorations_medals':
            self.ShowMyMedals()
        elif key == 'mydecorations_permissions':
            wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
            self.ShowMyDecorationPermissions()



    def ShowMyMedals(self, charID = None):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if charID is None:
            charID = session.charid
        if wnd.sr.decoMedalList is None:
            wnd.sr.decoMedalList = self.GetMedalScroll(charID)
        wnd.sr.scroll.sr.id = 'charsheet_mymedals'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoMedalList, noContentHint=mls.UI_GENERIC_NODECORATIONS)



    def GetMedalScroll(self, charID, noHeaders = False, publicOnly = False):
        scrolllist = []
        inDecoList = []
        publicDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [3]), mls.UI_GENERIC_PUBLIC)
        privateDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [2]), mls.UI_GENERIC_PRIVATE)
        (characterMedals, characterMedalInfo,) = sm.StartService('medals').GetMedalsReceived(charID)
        if publicOnly:
            t = (publicDeco,)
        else:
            t = (publicDeco, privateDeco)
        for (deco, hint,) in t:
            if deco and not noHeaders:
                scrolllist.append(listentry.Get('Header', {'label': hint}))
            for (medalID, medalData,) in deco.iteritems():
                if medalID in inDecoList:
                    continue
                inDecoList.append(medalID)
                details = characterMedalInfo.Filter('medalID')
                if details and details.has_key(medalID):
                    details = details.get(medalID)
                entry = sm.StartService('info').GetMedalEntry(None, medalData, details, 0)
                if entry:
                    scrolllist.append(entry)


        return scrolllist



    def ShowMyRanks(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.decoRankList is None:
            scrolllist = []
            characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
            for characterRank in characterRanks:
                entry = sm.StartService('info').GetRankEntry(None, characterRank)
                if entry:
                    scrolllist.append(entry)

            wnd.sr.decoRankList = scrolllist[:]
        wnd.sr.scroll.sr.id = 'charsheet_myranks'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoRankList, noContentHint=mls.UI_GENERIC_NODECORATIONS)



    def ShowEmploymentHistory(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.employmentList is None:
            wnd.sr.employmentList = sm.GetService('info').GetEmploymentHistorySubContent(eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_employmenthistory'
        wnd.sr.scroll.Load(contentList=wnd.sr.employmentList)



    def ShowKillRights(self):
        scrolllist = sm.GetService('info').GetKillRightsSubContent()
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        wnd.sr.scroll.sr.id = 'charsheet_killrights'
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=mls.UI_SHARED_NOKILLRIGHTSFOUND)



    def ShowJumpClones(self):
        jumpCloneSvc = sm.GetService('clonejump')
        jumpClones = jumpCloneSvc.GetClones()
        scrolllist = []
        lastJump = jumpCloneSvc.LastCloneJumpTime()
        hoursLimit = const.limitCloneJumpHours
        if lastJump:
            jumpTime = lastJump + hoursLimit * const.HOUR
            nextJump = jumpTime > blue.os.GetTime()
        else:
            nextJump = False
        if nextJump:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': mls.UI_SHARED_NEXTCLONEJUMP,
             'text': util.FmtDate(lastJump),
             'iconID': const.iconDuration,
             'countdownTime': jumpTime}))
        else:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': mls.UI_SHARED_NEXTCLONEJUMP,
             'text': mls.UI_GENERIC_NOW,
             'iconID': const.iconDuration,
             'countdownTime': 0}))
        if jumpClones:
            d = {}
            primeLocs = []
            for jc in jumpClones:
                jumpCloneID = jc.jumpCloneID
                locationID = jc.locationID
                primeLocs.append(locationID)
                label = 'station' if util.IsStation(locationID) else 'ship'
                if not d.has_key(label):
                    d[label] = {locationID: (jumpCloneID, locationID)}
                else:
                    d[label][locationID] = (jumpCloneID, locationID)

            cfg.evelocations.Prime(primeLocs)
            for k in ('station', 'ship'):
                if d.has_key(k):
                    locIDs = d[k].keys()
                    locNames = []
                    for locID in locIDs:
                        if locID in cfg.evelocations:
                            locName = cfg.evelocations.Get(locID).name
                        else:
                            locName = mls.UI_SHARED_LOCATIONDESTROYED
                        locNames.append((locName, locID))

                    locNames.sort()
                    for (locationName, locationID,) in locNames:
                        jumpCloneID = d[k][locationID]
                        groupID = d[k][locationID]
                        data = {'GetSubContent': self.GetCloneImplants,
                         'label': '%s %s %s' % (mls.UI_GENERIC_CLONE, mls.UI_SHARED_LOCATEDIN.lower(), locationName),
                         'id': groupID,
                         'jumpCloneID': d[k][locationID][0],
                         'locationID': d[k][locationID][1],
                         'state': 'locked',
                         'iconMargin': 18,
                         'showicon': 'ui_8_64_16',
                         'sublevel': 0,
                         'MenuFunction': self.JumpCloneMenu,
                         'showlen': 0}
                        scrolllist.append(listentry.Get('Group', data))


        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        wnd.sr.scroll.sr.id = 'charsheet_jumpclones'
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=mls.UI_SHARED_NOJUMPCLONESFOUND)



    def GetCloneImplants(self, nodedata, *args):
        scrolllist = []
        godma = sm.GetService('godma')
        scrolllist.append(listentry.Get('CloneButtons', {'locationID': nodedata.locationID,
         'jumpCloneID': nodedata.jumpCloneID}))
        implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in sm.GetService('clonejump').GetImplantsForClone(nodedata.jumpCloneID) ])
        if implants:
            for cloneImplantRow in implants:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': cloneImplantRow,
                 'label': cfg.invtypes.Get(cloneImplantRow.typeID).name}))

        else:
            scrolllist.append(listentry.Get('Text', {'label': mls.UI_SHARED_NOIMPLANTSINSTALLED,
             'text': mls.UI_SHARED_NOIMPLANTSINSTALLED}))
        return scrolllist



    def JumpCloneMenu(self, node):
        m = []
        validLocation = node.locationID in cfg.evelocations
        if eve.session.stationid and validLocation:
            m += [None, (mls.UI_CMD_JUMP, sm.GetService('clonejump').CloneJump, (node.locationID,))]
        if validLocation:
            m.append((mls.UI_CMD_DESTROY, sm.GetService('clonejump').DestroyInstalledClone, (node.jumpCloneID,)))
        return m



    def ShowMyBio(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        wnd.sr.bioparent.state = uiconst.UI_PICKCHILDREN
        if not getattr(self, 'bioinited', 0):
            blue.pyos.synchro.Yield()
            wnd.sr.bio = uicls.EditPlainText(parent=wnd.sr.bioparent, maxLength=1000, showattributepanel=1)
            wnd.sr.bio.sr.window = self
            wnd.sr.bioparent.OnTabDeselect = self.AutoSaveBio
            wnd.oldbio = ''
            if not self.bio:
                bio = sm.RemoteSvc('charMgr').GetCharacterDescription(eve.session.charid)
                if bio is not None:
                    self.bio = bio
                else:
                    self.bio = ''
            if not wnd or wnd.destroyed:
                return 
            if self.bio:
                wnd.oldbio = self.bio
            self.bioinited = 1
        if wnd and not wnd.destroyed:
            wnd.sr.bio.SetValue(wnd.oldbio or mls.UI_SHARED_HEREYOUCANTYPEBIO)



    def AutoSaveBio(self, edit = None, *args):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        newbio = (edit or wnd.sr.bio).GetValue()
        newbio = newbio.replace(mls.UI_SHARED_HEREYOUCANTYPEBIO, '')
        if not len(uiutil.StripTags(newbio)):
            newbio = ''
        self.bio = newbio
        if wnd and newbio.strip() != wnd.oldbio:
            uthread.pool('CharaacterSheet::AutoSaveBio', self._AutoSaveBio, newbio)
            if wnd:
                wnd.oldbio = newbio



    def _AutoSaveBio(self, newbio):
        sm.RemoteSvc('charMgr').SetCharacterDescription(newbio[:1000])



    def ReloadMySkills(self):
        self.skillTimer = base.AutoTimer(1000, self.ShowMySkills)



    def ReloadMyStandings(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mystandings' ]
            if selection:
                self.showing = None
                self.Load('mystandings')



    def ReloadMyRanks(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.decoRankList = None
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mydecorations' ]
            if selection:
                self.showing = None
                self.Load('mydecorations')



    def ShowMySkillHistory(self):
        wnd = self.GetWnd()
        if not wnd:
            return 

        def GetPts(lvl):
            return skillUtil.GetSPForLevelRaw(stc, lvl)


        wnd.sr.nav.DeselectAll()
        wnd.sr.scroll.sr.id = 'charsheet_skillhistory'
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        rs = sm.GetService('skills').GetSkillHistory()
        scrolllist = []
        actions = {34: mls.UI_GENERIC_SKILLCLONEPENALTY,
         36: mls.UI_GENERIC_SKILLTRAININGSTARTED,
         37: mls.UI_GENERIC_SKILLTRAININGCOMPLETE,
         38: mls.UI_GENERIC_SKILLTRAININGCANCELLED,
         39: mls.UI_GENERIC_GMGIVESKILL,
         53: mls.UI_GENERIC_SKILLTRAININGCOMPLETE,
         307: mls.UI_GENERIC_SKILLPOINTSAPPLIED}
        for r in rs:
            skill = sm.GetService('skills').HasSkill(r.skillTypeID)
            if skill:
                stc = skill.skillTimeConstant
                levels = [0,
                 GetPts(1),
                 GetPts(2),
                 GetPts(3),
                 GetPts(4),
                 GetPts(5)]
                level = 5
                spNext = levels[5]
                for i in range(len(levels)):
                    if levels[i] > r.absolutePoints:
                        level = i - 1
                        spNext = levels[i]
                        break

                data = util.KeyVal()
                data.label = '%s<t>%s<t>%s<t>%s' % (util.FmtDate(r.logDate, 'ls'),
                 cfg.invtypes.Get(r.skillTypeID).name,
                 actions.get(r.eventTypeID, 'unknown'),
                 level)
                data.Set('sort_%s' % mls.UI_GENERIC_DATE, r.logDate)
                data.id = r.skillTypeID
                data.GetMenu = self.GetItemMenu
                data.MenuFunction = self.GetItemMenu
                data.OnDblClick = (self.DblClickShowInfo, data)
                addItem = listentry.Get('Generic', data=data)
                scrolllist.append(addItem)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
         mls.UI_GENERIC_SKILL,
         mls.UI_GENERIC_ACTION,
         mls.UI_GENERIC_LEVEL], noContentHint=mls.UI_GENERIC_NORECORDSFOUND)



    def GetItemMenu(self, entry, *args):
        return [(mls.UI_CMD_SHOWINFO, self.ShowInfo, (entry.sr.node.id, 1))]



    def DblClickShowInfo(self, entry):
        skillTypeID = util.GetAttrs(entry, 'sr', 'node', 'id')
        if skillTypeID is not None:
            self.ShowInfo(skillTypeID)



    def ShowInfo(self, *args):
        skillID = args[0]
        sm.StartService('info').ShowInfo(skillID, None)



    def GetCombatEntries(self, recent, isCorp = 0):
        primeInvTypes = {}
        primeEveOwners = {}
        primeEveLocations = {}
        headers = []
        ret = []
        for kill in recent:
            primeEveLocations[kill.solarSystemID] = 1
            primeEveLocations[kill.moonID] = 1
            primeEveOwners[kill.victimCharacterID] = 1
            primeEveOwners[kill.victimCorporationID] = 1
            primeEveOwners[kill.victimAllianceID] = 1
            primeEveOwners[kill.victimFactionID] = 1
            primeInvTypes[kill.victimShipTypeID] = 1
            primeEveOwners[kill.finalCharacterID] = 1
            primeEveOwners[kill.finalCorporationID] = 1
            primeEveOwners[kill.finalAllianceID] = 1
            primeEveOwners[kill.finalFactionID] = 1
            primeInvTypes[kill.finalShipTypeID] = 1
            primeInvTypes[kill.finalWeaponTypeID] = 1
            if settings.user.ui.Get('charsheet_condensedcombatlog', 0) or isCorp:
                if not headers:
                    headers = [mls.UI_GENERIC_DATE,
                     mls.UI_GENERIC_SHIP,
                     mls.UI_GENERIC_NAME,
                     mls.UI_GENERIC_CORPORATION,
                     mls.UI_GENERIC_ALLIANCE,
                     mls.UI_GENERIC_FACTION]
                killShip = cfg.invtypes.GetIfExists(kill.victimShipTypeID)
                killChar = cfg.eveowners.GetIfExists(kill.victimCharacterID)
                killCorp = cfg.eveowners.GetIfExists(kill.victimCorporationID)
                killAlli = cfg.eveowners.GetIfExists(kill.victimAllianceID)
                killFact = cfg.eveowners.GetIfExists(kill.victimFactionID)
                data = util.KeyVal()
                data.label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(kill.killTime),
                 getattr(killShip, 'name', False) or mls.UI_GENERIC_UNKNOWN,
                 getattr(killChar, 'name', False) or mls.UI_GENERIC_UNKNOWN,
                 getattr(killCorp, 'name', False) or mls.UI_GENERIC_UNKNOWN,
                 getattr(killAlli, 'name', False) or mls.UI_GENERIC_UNKNOWN,
                 getattr(killFact, 'name', False) or mls.UI_GENERIC_UNKNOWN)
                data.GetMenu = self.GetCombatMenu
                data.OnDblClick = (self.GetCombatDblClick, data)
                data.kill = kill
                ret.append(listentry.Get('Generic', data=data))
            else:
                ret.append(listentry.Get('KillMail', {'mail': kill}))

        cfg.invtypes.Prime([ x for x in primeInvTypes.keys() if x is not None ])
        cfg.eveowners.Prime([ x for x in primeEveOwners.keys() if x is not None ])
        cfg.evelocations.Prime([ x for x in primeEveLocations.keys() if x is not None ])
        return (ret, headers)



    def GetCombatDblClick(self, entry, *args):
        ret = util.CombatLog_CopyText(entry.sr.node.kill)
        wnd = sm.GetService('window').GetWindow('CombatDetails')
        if wnd:
            wnd.UpdateDetails(ret)
            wnd.Maximize()
        else:
            wnd = sm.GetService('window').GetWindow('CombatDetails', decoClass=form.CombatDetailsWnd, create=1, ret=ret)



    def GetCombatMenu(self, entry, *args):
        m = [(mls.UI_COMBATLOG_COPYKILLINFO, self.GetCombatText, (entry.sr.node.kill, 1))]
        return m



    def ShowKillsEx(self, recent, pagenum, func, combatType):
        wnd = self.GetWnd()
        if not wnd:
            return 
        (scrolllist, headers,) = self.GetCombatEntries(recent)
        for c in wnd.sr.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        wnd.sr.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = wnd.sr.btnContainer.children[1]
        nextbtn = wnd.sr.btnContainer.children[0]
        if pagenum > 0:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            prevbtn.OnClick = (func, self.prevIDs[(pagenum - 1)], pagenum - 1)
        if len(recent) >= self.killentries:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), pagenum + 1)
            self.prevIDs.append(max(killIDs) + 1)
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        isCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
        if isCondensed:
            wnd.sr.scroll.sr.id = 'charsheet_kills'
        else:
            wnd.sr.scroll.sr.id = 'charsheet_kills2'
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = mls.UI_GENERIC_NOKILLSFOUND
        elif combatType == 'losses':
            noContentHintText = mls.UI_GENERIC_NOLOSSESFOUND
        pos = wnd.sr.scroll.GetScrollProportion()
        wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, scrollTo=pos, noContentHint=noContentHintText)



    def GetCombatText(self, kill, isCopy = 0):
        ret = util.CombatLog_CopyText(kill)
        if isCopy:
            blue.pyos.SetClipboardData(ret.replace('<br>', '\r\n').replace('<t>', '   '))
        else:
            return ret



    def ShowCombatSettings(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        for (cfgname, value, label, checked, group,) in [['charsheet_condensedcombatlog',
          None,
          mls.UI_SHARED_CONDENSEDCOMBATLOG,
          settings.user.ui.Get('charsheet_condensedcombatlog', 0),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        wnd.sr.scroll.sr.id = 'charsheet_combatsettings'
        wnd.sr.scroll.Load(contentList=scrolllist)



    def ShowCombatKills(self, startFrom = None, *args):
        recent = sm.GetService('info').GetKillsRecentKills(self.killentries, startFrom)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatKills, 'kills')



    def ShowCombatLosses(self, startFrom = None, *args):
        recent = sm.GetService('info').GetKillsRecentLosses(self.killentries, startFrom)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatLosses, 'losses')



    def ShowKills(self, key):
        self.prevIDs = []
        if key == 'mykills_kills':
            self.ShowCombatKills()
        elif key == 'mykills_losses':
            self.ShowCombatLosses()
        elif key == 'mykills_settings':
            self.ShowCombatSettings()



    def ShowSkills(self, key):
        if key == 'myskills_skills':
            self.ShowMySkills(force=True)
        elif key == 'myskills_skillhistory':
            self.ShowMySkillHistory()
        elif key == 'myskills_settings':
            self.ShowMySkillSettings()



    def ShowCertificates(self, key):
        wnd = self.GetWnd()
        if wnd is None:
            return 
        wnd.sr.buttonParCert.state = uiconst.UI_HIDDEN
        if key == 'mycertificates_certificates':
            self.ShowMyCerts()
        elif key == 'mycertificates_permissions':
            wnd.sr.buttonParCert.state = uiconst.UI_NORMAL
            self.ShowMyCertificatePermissions()
        elif key == 'mycertificates_settings':
            self.ShowMyCertificateSettings()



    def ShowMyCerts(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        if getattr(wnd.sr, 'certificatepanel', None):
            wnd.sr.certificatepanel.state = uiconst.UI_NORMAL
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        self.myCerts = sm.StartService('certificates').GetMyCertificates()
        myCertsInfo = {}
        for certID in self.myCerts.iterkeys():
            cert = cfg.certificates.GetIfExists(certID)
            if cert is None:
                self.LogInfo('ShowMyCerts - Skipping certificate', certID, '- does not exist')
                continue
            myCertsInfo[certID] = cert

        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        allCategories = sm.StartService('certificates').GetCategories(myCertsInfo)
        for (category, value,) in allCategories.iteritems():
            categoryObj = categoryData[category]
            data = {'GetSubContent': self.GetCertSubContent,
             'label': Tr(categoryObj.categoryName, 'cert.categories.categoryName', categoryObj.dataID),
             'groupItems': value,
             'id': ('charsheetGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked'}
            scrolllist.append((data.get('label', ''), listentry.Get('Group', data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        wnd.sr.scroll.sr.id = 'charsheet_mycerts'
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=mls.UI_SHARED_CERTNOFOUND)



    def GetCertSubContent(self, dataX, *args):
        scrolllist = []
        wnd = self.GetWnd()
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', 1)
        if toggleGroups:
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

        entries = self.GetEntries(dataX)
        return entries



    def GetEntries(self, data, *args):
        scrolllist = []
        highestEntries = sm.StartService('certificates').GetHighestLevelOfClass(data.groupItems)
        for each in highestEntries:
            entry = self.CreateEntry(each)
            scrolllist.append((entry.label, entry))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def CreateEntry(self, data, *args):
        scrolllist = []
        certID = data.certificateID
        (label, grade, descr,) = uix.GetCertificateLabel(certID)
        cert = self.myCerts.get(certID)
        visibility = cert.visibilityFlags
        entry = {'line': 1,
         'label': label,
         'grade': data.grade,
         'certID': certID,
         'icon': 'ui_79_64_%s' % (data.grade + 1),
         'visibility': visibility}
        return listentry.Get('CertEntry', entry)



    def ShowMySkills(self, force = False):
        if not force and self.showing != 'myskills_skills':
            return 
        self.skillTimer = None
        wnd = self.GetWnd()
        if not wnd:
            return 
        if getattr(wnd.sr, 'skillpanel', None):
            wnd.sr.skillpanel.state = uiconst.UI_NORMAL
        advancedView = settings.user.ui.Get('charsheet_showSkills', 'trained') in ('mytrainable', 'alltrainable')
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        groups = sm.GetService('skills').GetSkillGroups(advancedView)
        scrolllist = []
        currentSkillPoints = sm.GetService('skills').GetSkillPoints()
        skillCount = sm.GetService('skills').GetSkillCount()
        skillPoints = sm.StartService('skills').GetFreeSkillPoints()
        if skillPoints > 0:
            text = '<color=0xFF00FF00>%s: %s</color>' % (mls.UI_GENERIC_UNALLOCATEDSKILLPOINTS, util.FmtAmt(skillPoints))
            scrolllist.append(listentry.Get('Text', {'text': text,
             'hint': mls.UI_GENERIC_APPLYSKILLHINT}))
        scrolllist.append(listentry.Get('Text', {'text': mls.UI_SHARED_YOUCURRENTLYHAVESKILLS % {'numSkill': skillCount,
                  'skillPoints': util.FmtAmt(currentSkillPoints)}}))

        def Published(skill):
            return cfg.invtypes.Get(skill.typeID).published


        for (group, skills, untrained, intraining, inqueue, points,) in groups:
            untrained = filter(Published, untrained)
            if not len(skills) and not advancedView:
                continue
            tempList = []
            if advancedView and settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable':
                for utrained in untrained[:]:
                    if self.MeetSkillRequirements(utrained.typeID):
                        tempList.append(utrained)

                combinedSkills = skills[:] + tempList[:]
                if not len(skills) and tempList == []:
                    continue
            if settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable':
                combinedSkills = skills[:] + untrained[:]
            if advancedView:
                numSkills = mls.UI_SHARED_SEVENOFNINE % {'first': len(skills),
                 'second': len(combinedSkills)}
            else:
                numSkills = len(skills)
                combinedSkills = skills[:]
            combinedSkills.sort(lambda x, y: cmp(cfg.invtypes.Get(x.typeID).name, cfg.invtypes.Get(y.typeID).name))
            posttext = ''
            if len(inqueue):
                text = mls.UI_SHARED_SQ_SKILLSINQUEUE % {'num': len(inqueue)}
                posttext = ' %s' % text
            if len(intraining):
                posttext = ' <color=0xffeec900>%s' % posttext
            label = '%s, %s' % (mls.UI_SHARED_GROUPLABELSKILLS % {'groupName': group.groupName,
              'numSkills': numSkills}, mls.UI_SHARED_NUMPOINTS % {'points': util.FmtAmt(points)})
            data = {'GetSubContent': self.GetSubContent,
             'DragEnterCallback': self.OnGroupDragEnter,
             'DeleteCallback': self.OnGroupDeleted,
             'MenuFunction': self.GetMenu,
             'label': label,
             'groupItems': combinedSkills,
             'inqueue': inqueue,
             'id': ('myskills', group.groupID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0,
             'posttext': posttext}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist.append(listentry.Get('Space', {'height': 64}))
        pos = wnd.sr.scroll.GetScrollProportion()
        wnd.sr.scroll.sr.id = 'charsheet_myskills'
        wnd.sr.scroll.Load(contentList=scrolllist, headers=[], scrollTo=pos)



    def MeetSkillRequirements(self, typeID):
        mine = sm.GetService('skills').MySkillLevelsByID()
        requiredSkills = sm.GetService('info').GetRequiredSkills(typeID)
        haveSkills = 1
        if requiredSkills:
            for (skillID, level,) in requiredSkills:
                if skillID not in mine or mine[skillID] < level:
                    haveSkills = 0
                    break

        return haveSkills



    def GetSubContent(self, data, *args):
        scrolllist = []
        wnd = self.GetWnd()
        if not wnd:
            return 
        skillqueue = sm.StartService('skillqueue').GetServerQueue()
        skillsInQueue = data.inqueue
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', 1)
        if toggleGroups:
            dataWnd = sm.GetService('window').GetWindow(unicode(data.id), create=0)
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        for skill in data.groupItems:
            inQueue = None
            if skill.typeID in skillsInQueue:
                for i in xrange(5, skill.skillLevel, -1):
                    if (skill.typeID, i) in skillqueue:
                        inQueue = i
                        break

            inTraining = 0
            if hasattr(skill, 'flagID') and skill.flagID == const.flagSkillInTraining:
                inTraining = 1
            data = {}
            data['invtype'] = cfg.invtypes.Get(skill.typeID)
            data['skill'] = skill
            data['trained'] = skill.itemID != None
            data['plannedInQueue'] = inQueue
            data['skillID'] = skill.typeID
            data['inTraining'] = inTraining
            scrolllist.append(listentry.Get('SkillEntry', data))
            if inTraining:
                sm.StartService('godma').GetStateManager().GetEndOfTraining(skill.itemID)

        return scrolllist



    def OnGroupDeleted(self, ids):
        pass



    def OnGroupDragEnter(self, group, drag):
        pass



    def GetMenu(self, *args):
        return []



    def ShowStandings(self, positive):
        wnd = self.GetWnd()
        if not wnd:
            return 
        self.SetHint()
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_standings'
        wnd.sr.scroll.Load(contentList=scrolllist)



    def UpdateMyAttributes(self, attributeID, value):
        wnd = self.GetWnd()
        if not wnd:
            return 
        for entry in wnd.sr.scroll.GetNodes():
            if entry.attributeID == attributeID:
                entry.text = '%i %s' % (value, mls.UI_GENERIC_POINTS)
                if entry.panel:
                    entry.panel.sr.text.text = entry.text
                    entry.panel.hint = entry.text.replace('<t>', '  ')




    def ShowMyAttributes(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrollList = []
        sm.GetService('info').GetAttrItemInfo(eve.session.charid, const.typeCharacterAmarr, scrollList, [const.attributeIntelligence,
         const.attributePerception,
         const.attributeCharisma,
         const.attributeWillpower,
         const.attributeMemory])
        respecInfo = sm.GetService('skills').GetRespecInfo()
        self.respecEntry = listentry.Get('AttributeRespec', data=util.KeyVal(time=respecInfo['nextRespecTime'], freeRespecs=respecInfo['freeRespecs'], label=mls.UI_SHARED_NEXTDNAMODIFICATION))
        scrollList.append(self.respecEntry)
        wnd.sr.scroll.sr.id = 'charsheet_myattributes'
        wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrollList, noContentHint=mls.UI_SHARED_NOATTRSFOUND)



    def ShowMySkillSettings(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        for (cfgname, value, label, checked, group,) in [['charsheet_showSkills',
          'trained',
          mls.UI_SHARED_SHOWCURRENTSKILLS,
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'trained',
          'trainable'],
         ['charsheet_showSkills',
          'mytrainable',
          mls.UI_SHARED_SHOWMYTRAINABLESKILLS,
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable',
          'trainable'],
         ['charsheet_showSkills',
          'alltrainable',
          mls.UI_SHARED_SHOWALLTRAINABLESKILLS,
          settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable',
          'trainable'],
         ['charsheet_hilitePartiallyTrainedSkills',
          None,
          mls.UI_SHARED_HIGHLIGHTPARTIALLYTRAINED,
          settings.user.ui.Get('charsheet_hilitePartiallyTrainedSkills', 0),
          None],
         ['charsheet_toggleOneSkillGroupAtATime',
          None,
          mls.UI_SHARED_TOGGLEONESKILLGROUP,
          settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', 1),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        wnd.sr.scroll.sr.id = 'charsheet_skillsettings'
        wnd.sr.scroll.Load(contentList=scrolllist)



    def CheckBoxChange(self, checkbox):
        if checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'charsheet_showSkills':
                if checkbox.data['retval'] is None:
                    settings.user.ui.Set(key, checkbox.checked)
                else:
                    settings.user.ui.Set(key, checkbox.data['retval'])
            else:
                settings.user.ui.Set(key, checkbox.checked)



    def ShowMyImplantsAndBoosters(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        mygodma = self.GetMyGodmaItem(eve.session.charid)
        if not mygodma:
            return 
        implants = mygodma.implants
        boosters = mygodma.boosters
        godma = sm.GetService('godma')
        implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in implants ])
        boosters = uiutil.SortListOfTuples([ (getattr(godma.GetType(booster.typeID), 'boosterness', None), booster) for booster in boosters ])
        scrolllist = []
        if implants:
            scrolllist.append(listentry.Get('Header', {'label': uix.Plural(len(implants), 'UI_GENERIC_IMPLANT')}))
            for each in implants:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                 'label': cfg.invtypes.Get(each.typeID).name}))

            if boosters:
                scrolllist.append(listentry.Get('Divider'))
        if boosters:
            scrolllist.append(listentry.Get('Header', {'label': uix.Plural(len(boosters), 'UI_GENERIC_BOOSTER')}))
            for each in boosters:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                 'label': cfg.invtypes.Get(each.typeID).name}))
                boosterEffect = self.GetMyGodmaItem(each.itemID)
                for effect in boosterEffect.effects.values():
                    if effect.isActive:
                        eff = cfg.dgmeffects.Get(effect.effectID)
                        scrolllist.append(listentry.Get('IconEntry', {'line': 1,
                         'hint': eff.displayName,
                         'text': None,
                         'label': eff.displayName,
                         'icon': util.IconFile(eff.iconID),
                         'selectable': 0,
                         'iconoffset': 32,
                         'iconsize': 22,
                         'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                scrolllist.append(listentry.Get('Divider'))
                first = False

        wnd.sr.scroll.sr.id = 'charsheet_implantandboosters'
        wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, noContentHint=mls.UI_SHARED_NOIMPLANTSORBOOSTER)



    def GetMyGodmaItem(self, itemID):
        ret = sm.GetService('godma').GetItem(itemID)
        while ret is None and not getattr(getattr(self, 'wnd', None), 'destroyed', 1):
            self.LogWarn('godma item not ready yet. sleeping for it...')
            blue.pyos.synchro.Sleep(500)
            ret = sm.GetService('godma').GetItem(itemID)

        return ret



    def GetBoosterSubContent(self, nodedata):
        scrolllist = []
        for each in nodedata.groupItems:
            entry = listentry.Get('LabelTextTop', {'line': 1,
             'label': each[0],
             'text': each[1],
             'iconID': each[2]})
            scrolllist.append((each[0], entry))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def GoTo(self, URL, data = None, args = {}, scrollTo = None):
        URL = URL.encode('cp1252', 'replace')
        if URL.startswith('showinfo:') or URL.startswith('evemail:') or URL.startswith('evemailto:'):
            self.output.GoTo(self, URL, data, args)
        else:
            uicore.cmd.OpenBrowser(URL, data=data, args=args)



    def ShowMyDecorationPermissions(self):
        scrollHeaders = [mls.UI_GENERIC_NAME,
         mls.UI_GENERIC_PRIVATE,
         mls.UI_GENERIC_PUBLIC,
         mls.UI_CMD_REMOVE]
        wnd = self.GetWnd()
        if not wnd:
            return 
        wnd.sr.scroll.sr.fixedColumns = {mls.UI_GENERIC_PRIVATE: 60,
         mls.UI_GENERIC_PUBLIC: 60}
        wnd.sr.scroll.sr.id = 'charsheet_decopermissions'
        wnd.sr.scroll.Load(contentList=[], headers=scrollHeaders)
        wnd.sr.scroll.OnColumnChanged = self.OnDecorationPermissionsColumnChanged
        publicDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [3])
        privateDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [2])
        ppKeys = [ each for each in publicDeco.keys() + privateDeco.keys() ]
        scrolllist = []
        inMedalList = []
        (characterMedals, characterMedalInfo,) = sm.StartService('medals').GetMedalsReceived(session.charid)
        for characterMedal in characterMedals:
            medalID = characterMedal.medalID
            if medalID not in ppKeys:
                continue
            if medalID in inMedalList:
                continue
            inMedalList.append(medalID)
            details = characterMedalInfo.Filter('medalID')
            if details and details.has_key(medalID):
                details = details.get(medalID)
            entry = self.CreateDecorationPermissionsEntry(characterMedal)
            if entry:
                scrolllist.append(entry)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=mls.UI_GENERIC_NOTHINGFOUND)
        self.OnDecorationPermissionsColumnChanged()



    def ShowMyCertificatePermissions(self):
        scrollHeaders = [mls.UI_GENERIC_NAME, mls.UI_GENERIC_PRIVATE, mls.UI_GENERIC_PUBLIC]
        certsvc = sm.StartService('certificates')
        wnd = self.GetWnd()
        if not wnd:
            return 
        wnd.sr.scroll.sr.fixedColumns = {mls.UI_GENERIC_PRIVATE: 60,
         mls.UI_GENERIC_PUBLIC: 60}
        wnd.sr.scroll.sr.id = 'charsheet_certpermissions'
        wnd.sr.scroll.Load(contentList=[], headers=scrollHeaders)
        wnd.sr.scroll.OnColumnChanged = self.OnCertificatePermissionsColumnChanged
        myCertIDs = certsvc.GetMyCertificates()
        myCerts = {}
        for certID in myCertIDs:
            cert = cfg.certificates.GetIfExists(certID)
            if cert is None:
                self.LogInfo('Certificate Permissions - Skipping certificate', certID, '- does not exist')
                continue
            myCerts[certID] = cert

        categoryData = sm.RemoteSvc('certificateMgr').GetCertificateCategories()
        myCategories = certsvc.GetCategories(myCerts)
        scrolllist = []
        for (category, value,) in myCategories.iteritems():
            value = certsvc.GetHighestLevelOfClass(value)
            categoryObj = categoryData[category]
            data = {'GetSubContent': self.GetCertificatePermissionsEntries,
             'label': Tr(categoryObj.categoryName, 'cert.categories.categoryName', categoryObj.dataID),
             'groupItems': value,
             'id': ('certGroups_cat', category),
             'sublevel': 0,
             'showlen': 0,
             'showicon': 'hide',
             'cat': category,
             'state': 'locked',
             'BlockOpenWindow': 1}
            scrolllist.append((data['label'], listentry.Get('Group', data)))

        if scrolllist:
            scrolllist = uiutil.SortListOfTuples(scrolllist)
        wnd.sr.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=mls.UI_GENERIC_NOTHINGFOUND)
        self.OnCertificatePermissionsColumnChanged()



    def GetCertificatePermissionsEntries(self, data, *args):
        wnd = self.GetWnd()
        if wnd is None:
            return 
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneCertPermsGroupAtATime', 1)
        if toggleGroups:
            dataWnd = sm.GetService('window').GetWindow(unicode(data.id), create=0)
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        scrolllist = []
        for each in data.groupItems:
            entry = self.CreateCertificatePermissionsEntry(each)
            scrolllist.append((entry.label, entry))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def CreateCertificatePermissionsEntry(self, data):
        certID = data.certificateID
        myCerts = sm.StartService('certificates').GetMyCertificates()
        certObj = myCerts.get(certID)
        visibilityFlags = 0
        if certObj is not None:
            visibilityFlags = certObj.visibilityFlags
        tempFlag = self.visibilityChanged.get(certID, None)
        func = sm.StartService('charactersheet').OnCertVisibilityChange
        (label, grade, descr,) = uix.GetCertificateLabel(certID)
        entry = {'line': 1,
         'label': '%s - %s<t> <t> ' % (label, grade),
         'itemID': certID,
         'visibilityFlags': visibilityFlags,
         'tempFlag': tempFlag,
         'indent': 3,
         'selectable': 0,
         'func': func}
        return listentry.Get('CertificatePermissions', entry)



    def CreateDecorationPermissionsEntry(self, data):
        entry = {'line': 1,
         'label': '%s<t> <t> <t> ' % data.title,
         'itemID': data.medalID,
         'visibilityFlags': data.status,
         'indent': 3,
         'selectable': 0}
        return listentry.Get('DecorationPermissions', entry)



    def OnCertificatePermissionsColumnChanged(self, *args, **kwargs):
        wnd = self.GetWnd()
        if not wnd:
            return 
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                entry.panel.OnColumnChanged()




    def OnDecorationPermissionsColumnChanged(self, *args, **kwargs):
        wnd = self.GetWnd()
        if not wnd:
            return 
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                entry.panel.OnColumnChanged()




    def SaveDecorationPermissionsChanges(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        promptForDelete = False
        changes = {}
        for entry in wnd.sr.scroll.GetNodes():
            if entry.panel and hasattr(entry.panel, 'flag'):
                if entry.panel.HasChanged():
                    if entry.panel.flag == 1:
                        promptForDelete = True
                    changes[entry.panel.sr.node.itemID] = entry.panel.flag

        if promptForDelete == False or eve.Message('DeleteMedalConfirmation', {}, uiconst.YESNO) == uiconst.ID_YES:
            if len(changes) > 0:
                sm.StartService('medals').SetMedalStatus(changes)
        wnd.sr.decoMedalList = None



    def SetAllDecorationPermissions(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        permissionList = [(mls.UI_GENERIC_PRIVATE, 2), (mls.UI_GENERIC_PUBLIC, 3)]
        pickedPermission = uix.ListWnd(permissionList, 'generic', mls.UI_CMD_SETALL, mls.UI_SHARED_CHANGESSAVEDIMMEDIATELY, windowName='permissionPickerWnd')
        if not pickedPermission:
            return 
        permissionID = pickedPermission[1]
        (m, i,) = sm.StartService('medals').GetMedalsReceived(session.charid)
        myDecos = []
        for each in m:
            if each.status != 1:
                myDecos.append(each.medalID)

        myDecos = list(set(myDecos))
        updateDict = {}
        for decoID in myDecos:
            updateDict[decoID] = permissionID

        if len(updateDict) > 0:
            sm.StartService('medals').SetMedalStatus(updateDict)
            wnd.sr.decoMedalList = None
            self.ShowMyDecorations('mydecorations_permissions')



    def SaveCertificatePermissionsChanges(self):
        wnd = self.GetWnd()
        if not wnd:
            return 
        if len(self.visibilityChanged) > 0:
            sm.StartService('certificates').ChangeVisibilityFlag(self.visibilityChanged)
        self.visibilityChanged = {}



    def ShowMyCertificateSettings(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrolllist = []
        for (cfgname, value, label, checked, group,) in [['charsheet_toggleOneCertGroupAtATime',
          None,
          mls.UI_SHARED_TOGGLEONECERTGROUP,
          settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', 1),
          None], ['charsheet_toggleOneCertPermsGroupAtATime',
          None,
          mls.UI_SHARED_TOGGLEONECERTPERMSGROUP,
          settings.user.ui.Get('charsheet_toggleOneCertPermsGroupAtATime', 1),
          None]]:
            data = util.KeyVal()
            data.label = label
            data.checked = checked
            data.cfgname = cfgname
            data.retval = value
            data.group = group
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        wnd.sr.scroll.sr.id = 'charsheet_certsettings'
        wnd.sr.scroll.Load(contentList=scrolllist)



    def SetAllCertificatePermissions(self):
        permissionList = [(mls.UI_GENERIC_PRIVATE, 0), (mls.UI_GENERIC_PUBLIC, 1)]
        pickedPermission = uix.ListWnd(permissionList, 'generic', mls.UI_CMD_SETALL, mls.UI_SHARED_CHANGESSAVEDIMMEDIATELY, windowName='permissionPickerWnd')
        if not pickedPermission:
            return 
        permissionID = pickedPermission[1]
        certsvc = sm.StartService('certificates')
        myCerts = certsvc.GetMyCertificates()
        updateDict = {}
        for certID in myCerts.iterkeys():
            updateDict[certID] = permissionID

        if len(updateDict) > 0:
            certsvc.ChangeVisibilityFlag(updateDict)
            self.ShowCertificates('mycertificates_permissions')
            self.visibilityChanged = {}




class CharacterSheetWindow(uicls.Window):
    __guid__ = 'form.CharacterSheet'
    default_top = 0
    default_width = 497
    default_height = 456
    default_minSize = (497, 456)

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush




class PilotLicence(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.PilotLicence'
    __params__ = ['daysLeft', 'buyPlexOnMarket', 'buyPlexOnline']
    BUTTON_HEIGHT = 40

    def Load(self, node):
        if node.loaded:
            return 
        node.allowDynamicResize = True
        self.Setup(node.daysLeft, node.buyPlexOnMarket, node.buyPlexOnline)



    def Setup(self, daysLeft, buyPlexOnMarket, buyPlexOnline):
        if daysLeft:
            text = mls.UI_SHARED_PILOTLICENSE_LEFT % {'daysLeft': daysLeft}
            (r, g, b,) = (1.0, 0.0, 0.0)
        else:
            (r, g, b,) = (1.0, 1.0, 1.0)
            text = mls.UI_SHARED_PILOTLICENSE_FINE
        statebox = uicls.Container(name='statebox', align=uiconst.TOTOP, parent=self, state=uiconst.UI_DISABLED, height=60, padding=(10, 10, 5, 0))
        uicls.Fill(parent=statebox, color=(r,
         g,
         b,
         0.07))
        uicls.Frame(parent=statebox, state=uiconst.UI_DISABLED, color=(r,
         g,
         b,
         0.4), idx=1)
        stateTextCtr = uicls.Container(name='statectr', align=uiconst.CENTERTOP, parent=statebox, state=uiconst.UI_DISABLED, height=60, width=280, padding=(10, 0, 10, 0))
        uicls.Icon(align=uiconst.TOPLEFT, parent=stateTextCtr, icon='ui_57_64_3', pos=(0, 0, 55, 55), ignoreSize=True, idx=0)
        self.liceseneStateLabel = uicls.Label(name='licensestate', align=uiconst.TOALL, text=text, autoheight=1, parent=stateTextCtr, state=uiconst.UI_DISABLED, padding=(65, 10, 0, 0), autowidth=1)
        self.plexdesctext = uicls.Label(name='plexdesc', text=mls.UI_SHARED_PILOTLICENSE_ABOUT, parent=self, padding=(12, 10, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        buttonbox = uicls.Container(name='buttonbox', align=uiconst.TOALL, parent=self, padding=(10, 15, 0, 0))
        btn = uix.GetBigButton(50, buttonbox, width=180, height=PilotLicence.BUTTON_HEIGHT)
        btn.SetSmallCaption(mls.UI_SHARED_PILOTLICENSE_ON_MARKET, inside=1)
        btn.OnClick = buyPlexOnMarket
        btn.SetAlign(uiconst.CENTERTOP)
        btn = uix.GetBigButton(50, buttonbox, top=PilotLicence.BUTTON_HEIGHT + 15, width=180, height=PilotLicence.BUTTON_HEIGHT)
        btn.SetSmallCaption(mls.UI_SHARED_PILOTLICENSE_ONLINE, inside=1)
        btn.SetAlign(uiconst.CENTERTOP)
        btn.OnClick = buyPlexOnline
        self.sr.node.loaded = True



    def GetDynamicHeight(node, width):
        plexTextHeight = sm.GetService('font').GetTextHeight(mls.UI_SHARED_PILOTLICENSE_ABOUT, width=width - 10)
        padding = 50
        buttons = 2 * (PilotLicence.BUTTON_HEIGHT + 15)
        return plexTextHeight + buttons + padding + 60




class CloneButtons(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.CloneButtons'

    def Startup(self, args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.JumpBtn = uicls.Button(parent=self, label=mls.UI_CMD_JUMP, align=uiconst.CENTER, func=self.OnClickJump)
        self.sr.DecomissionBtn = uicls.Button(parent=self, label=mls.UI_CMD_DESTROY, align=uiconst.CENTER, func=self.OnClickDecomission)



    def Load(self, node):
        self.sr.node = node
        self.locationID = node.locationID
        self.jumpCloneID = node.jumpCloneID
        self.sr.JumpBtn.width = self.sr.DecomissionBtn.width = max(self.sr.JumpBtn.width, self.sr.DecomissionBtn.width)
        self.sr.JumpBtn.left = -self.sr.JumpBtn.width / 2
        self.sr.DecomissionBtn.left = self.sr.DecomissionBtn.width / 2
        self.sr.JumpBtn.Disable()
        self.sr.DecomissionBtn.Disable()
        validLocation = self.locationID in cfg.evelocations
        if validLocation:
            self.sr.DecomissionBtn.Enable()
            if session.stationid:
                self.sr.JumpBtn.Enable()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height



    def OnClickJump(self, *args):
        sm.GetService('clonejump').CloneJump(self.locationID)



    def OnClickDecomission(self, *args):
        sm.GetService('clonejump').DestroyInstalledClone(self.jumpCloneID)




class CombatDetailsWnd(uicls.Window):
    __guid__ = 'form.CombatDetailsWnd'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(mls.UI_COMBATLOG_COMBATDETAILS)
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        ret = attributes.ret
        uicls.ButtonGroup(btns=[[mls.UI_CMD_CLOSE,
          self.CloseX,
          None,
          81]], parent=self.sr.main)
        self.edit = uicls.Edit(parent=self.sr.main, align=uiconst.TOALL, readonly=True)
        self.UpdateDetails(ret)



    def UpdateDetails(self, ret = ''):
        self.edit.SetValue(ret)




