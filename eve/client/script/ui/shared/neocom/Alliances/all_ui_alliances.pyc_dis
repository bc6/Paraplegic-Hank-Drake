#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/Alliances/all_ui_alliances.py
import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import uicls
import uiconst
import uiutil
import log
import localization

class FormAlliances(uicls.Container):
    __guid__ = 'form.Alliances'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSetAllianceStanding']

    def init(self):
        sm.RegisterNotify(self)
        self.sr.currentView = None

    def Load(self, key):
        alliancesLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances')
        sm.GetService('corpui').LoadTop('ui_7_64_6', alliancesLabel)
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.wndViewParent = uicls.Container(name='wndViewParent', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self)
            if session.allianceid:
                self.sr.contacts = form.ContactsForm(name='alliancecontactsform', parent=self, pos=(0, 0, 0, 0), startupParams=())
                self.sr.contacts.Setup('alliancecontact')
            else:
                self.sr.contacts = uicls.Scroll(name='alliancecontactsform', parent=self, padding=(const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding,
                 const.defaultPadding))
            homeLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home')
            rnksLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings')
            apliLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications')
            mbrsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members')
            cntcLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/AllianceContacts')
            tabs = [[homeLabel,
              self.sr.wndViewParent,
              self,
              'alliances_home'],
             [rnksLabel,
              self.sr.wndViewParent,
              self,
              'alliances_rankings'],
             [apliLabel,
              self.sr.wndViewParent,
              self,
              'alliances_applications'],
             [mbrsLabel,
              self.sr.wndViewParent,
              self,
              'alliances_members'],
             [cntcLabel,
              self.sr.contacts,
              self,
              'alliancecontact']]
            if session.allianceid is not None:
                bulletinsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Bulletins')
                tabs.insert(0, [bulletinsLabel,
                 self.sr.wndViewParent,
                 self,
                 'alliances_bulletins'])
            self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup(tabs, 'corpaccounts')
            return
        self.LoadViewClass(key)

    def LoadViewClass(self, tabName):
        self.sr.wndViewParent.Flush()
        visibleTab = None
        if self.sr.tabs:
            visibleTab = self.sr.tabs.GetVisible()
            if tabName == 'alliances':
                tabName = self.sr.tabs.GetSelectedArgs()
        if visibleTab and visibleTab.name == 'alliancecontactsform':
            if session.allianceid:
                self.sr.contacts.LoadContactsForm('alliancecontact')
                return
            else:
                corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/CorpNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
                self.sr.contacts.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
                return
        self.sr.contacts.state = uiconst.UI_HIDDEN
        if tabName == 'alliances_home':
            self.sr.currentView = form.AlliancesHome(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_rankings':
            self.sr.currentView = form.AlliancesRankings(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_applications':
            self.sr.currentView = form.AlliancesApplications(parent=self.sr.wndViewParent)
        elif tabName == 'alliances_members':
            self.sr.currentView = form.AlliancesMembers(parent=self.sr.wndViewParent, align=uiconst.TOALL)
        elif tabName == 'alliances_bulletins':
            self.sr.currentView = form.AlliancesBulletins(parent=self.sr.wndViewParent)
        if self.sr.currentView is not None:
            self.sr.currentView.CreateWindow()

    def OnSetAllianceStanding(self, *args):
        if uiutil.IsVisible(self) and self.sr.Get('inited', False) and self.sr.tabs:
            self.sr.tabs.ReloadVisible()

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceApplicationChanged')
        function = getattr(self.sr.currentView, 'OnAllianceApplicationChanged', None)
        if function is not None:
            function(allianceID, corpID, change)

    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceMemberChanged')
        function = getattr(self.sr.currentView, 'OnAllianceMemberChanged', None)
        if function is not None:
            function(allianceID, corpID, change)

    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceRelationshipChanged')
        function = getattr(self.sr.currentView, 'OnAllianceRelationshipChanged', None)
        if function is not None:
            function(allianceID, toID, change)

    def OnAllianceChanged(self, allianceID, change):
        log.LogInfo(self.__class__.__name__, 'OnAllianceChanged')
        function = getattr(self.sr.currentView, 'OnAllianceChanged', None)
        if function is not None:
            function(allianceID, change)