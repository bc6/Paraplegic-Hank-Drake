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

class FormAlliances(uicls.Container):
    __guid__ = 'form.Alliances'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSetAllianceStanding']

    def init(self):
        sm.RegisterNotify(self)
        self.sr.currentView = None



    def Load(self, key):
        sm.GetService('corpui').LoadTop('ui_7_64_6', mls.UI_GENERIC_ALLIANCES)
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
            tabs = [[mls.UI_CORP_HOME,
              self.sr.wndViewParent,
              self,
              'alliances_home'],
             [mls.UI_CORP_RANKINGS,
              self.sr.wndViewParent,
              self,
              'alliances_rankings'],
             [mls.UI_CORP_APPLICATIONS,
              self.sr.wndViewParent,
              self,
              'alliances_applications'],
             [mls.UI_CORP_MEMBERS,
              self.sr.wndViewParent,
              self,
              'alliances_members'],
             [mls.UI_CONTACTS_ALLIANCECONTACTS,
              self.sr.contacts,
              self,
              'alliancecontact']]
            if session.allianceid is not None:
                tabs.insert(0, [mls.UI_CORP_BULLETINS,
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
                sm.GetService('addressbook').ShowContacts('alliancecontact', self.sr.contacts)
                return 
            else:
                self.sr.contacts.Load(fixedEntryHeight=19, contentList=[], noContentHint=mls.UI_CORP_OWNERNOTINANYALLIANCE % {'owner': cfg.eveowners.Get(eve.session.corpid).ownerName})
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




