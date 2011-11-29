import service
import uthread
import blue
import uix
import uiutil
import form
import util
import uiconst
import uicls
import localization

def ReturnNone():
    return None



class CorporationUI(service.Service):
    __exportedcalls__ = {'VoteWindow': [],
     'LoadTop': [],
     'Show': [],
     'ViewApplication': [],
     'ShowLoad': [],
     'HideLoad': [],
     'ResetWindow': [],
     'LoadLogo': [],
     'GetMemberDetails': [],
     'ApplyToJoinAlliance': [],
     'OnCorporationApplicationChanged': [],
     'OnCorporationRecruitmentAdChanged': [],
     'OnTitleChanged': [],
     'OnSanctionedActionChanged': [],
     'OnCorporationVoteCaseChanged': [],
     'OnCorporationVoteCaseOptionChanged': [],
     'OnCorporationVoteChanged': [],
     'OnAllianceApplicationChanged': [],
     'OnAllianceMemberChanged': [],
     'OnAllianceRelationshipChanged': [],
     'OnAllianceChanged': [],
     'OnWarChanged': [],
     'OnLockedItemChangeUI': [],
     'OnCorporationMedalAdded': []}
    __guid__ = 'svc.corpui'
    __notifyevents__ = ['ProcessSessionChange',
     'OnSessionChanged',
     'DoSessionChanging',
     'ProcessUIRefresh']
    __servicename__ = 'corpui'
    __displayname__ = 'Corporation UI Client Service'
    __dependencies__ = ['corp']
    __update_on_reload__ = 0

    def __init__(self):
        service.Service.__init__(self)
        self.wasVisible = 0



    def Run(self, memStream = None):
        self.LogInfo('Starting Corporation')
        self.state = service.SERVICE_START_PENDING
        self.locks = {}
        self.ResetWindow()
        self.state = service.SERVICE_RUNNING



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.Close()



    def ProcessUIRefresh(self):
        wnd = form.Corporation.GetIfOpen()
        showWindow = False
        if wnd and not wnd.IsHidden():
            showWindow = True
        self.Stop()
        self.ResetWindow(bShowIfVisible=showWindow)



    def DoSessionChanging(self, isRemote, session, change):
        self.wasVisible = 0
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and wnd.state != uiconst.UI_HIDDEN:
            self.wasVisible = 1
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            sm.StopService(self.__guid__[4:])



    def ProcessSessionChange(self, isRemote, session, change):
        if 'corpid' in change and bool(session.charid):
            sm.StartService('objectCaching').InvalidateCachedMethodCall('corporationSvc', 'GetEmploymentRecord', session.charid)



    def OnSessionChanged(self, isremote, sess, change):
        if 'corpid' in change or 'corprole' in change or 'allianceid' in change:
            self.ResetWindow(self.wasVisible)
        if 'corpid' in change or 'allianceid' in change:
            bulletinWnd = form.EditCorpBulletin.GetIfOpen()
            if bulletinWnd and ('corpid' in change or bulletinWnd.IsAlliance()):
                bulletinWnd.Close()
        if 'solarsystemid' in change:
            self.RefreshWindow()



    def RefreshWindow(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            if getattr(wnd.sr, 'maintabs', None) is not None:
                wnd.sr.maintabs.ReloadVisible()



    def GetWnd(self, haveto = 0, panelName = None):
        wnd = form.Corporation.GetIfOpen()
        if not wnd and haveto:
            wnd = form.Corporation.Open()
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.sr.main.left = wnd.sr.main.top = 0
            wnd.sr.main.clipChildren = 1
            wnd.SetCaption(localization.GetByLabel('UI/Corporations/BaseCorporationUI/Corporation'))
            wnd.OnScale_ = self.OnWndScale
            wnd.RefreshSize = self.RefreshSize
            wnd._OnClose = self.OnCloseWnd
            wnd.SetWndIcon('ui_7_64_6')
            wnd.SetTopparentHeight(0)
            self.Initialize(wnd, panelName)
        return wnd



    def OnCloseWnd(self, *args):
        for panels in self.panels.values():
            for panel in panels:
                if hasattr(panel, '_OnClose'):
                    panel._OnClose(args)


        self.ResetPanels()



    def ResetPanels(self):
        self.panelHome = None
        self.members = None
        self.recruitment = None
        self.wars = None
        self.standings = None
        self.votes = None
        self.sanctionable = None
        self.accounts = None
        self.auditing = None
        self.membertracking = None
        self.toparea = None
        self.findmember = None
        self.alliances = None
        self.titles = None
        self.decorations = None



    def RefreshSize(self, *args):
        for panels in self.panels.values():
            for each in panels:
                if each.state != uiconst.UI_HIDDEN and hasattr(each, 'OnContentResize'):
                    each.OnContentResize(1)
                    continue





    def OnWndScale(self, *args):
        for panels in self.panels.values():
            for each in panels:
                if each.state != uiconst.UI_HIDDEN and hasattr(each, 'OnContentResize'):
                    each.OnContentResize(0)
                    continue





    def ResetWindow(self, bShowIfVisible = 0):
        uthread.Lock(self)
        try:
            self.panels = {}
            self.votewindows = {}
            self.ResetPanels()
            wnd = self.GetWnd()
            if wnd and not wnd.destroyed:
                wnd.Close()
            if bShowIfVisible:
                self.Show()

        finally:
            uthread.UnLock(self)




    def Show(self, panelName = None):
        wnd = self.GetWnd(1, panelName)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def Initialize(self, wnd, panelName = None):
        while eve.session.mutating:
            blue.pyos.BeNice()

        wnd.ShowLoad()
        uix.Flush(wnd.sr.main)
        self.toparea = uicls.Container(parent=wnd.sr.main, name='corptop', pos=(0, 0, 0, 54), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        uicls.Icon(parent=self.toparea, name='simplepic', pos=(4, 0, 64, 64), icon='ui_7_64_5')
        self.panelHome = None
        self.members = None
        self.recruitment = None
        self.wars = None
        self.standings = None
        self.votes = None
        self.sanctionable = None
        self.accounts = None
        self.auditing = None
        self.membertracking = None
        self.findmember = None
        self.titles = None
        self.alliances = None
        tabpanels = []
        homeHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/AboutThisCorp')
        warsHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpWarsHint')
        standingsHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpStandingsHint')
        votesHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpVotesHint')
        sanctionableActionsHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpSanctionableActionsHint')
        accountsHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpAccountsHint')
        alliancesHint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/AlliancesHint')
        self.panelHome = form.CorpUIHome(name='corp_home', parent=wnd.sr.main, state=uiconst.UI_PICKCHILDREN)
        tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Home'),
         self.panelHome,
         self,
         'home',
         None,
         homeHint])
        self.panels['home'] = [self.panelHome]
        self.recruitment = form.CorpRecruitment(name='recruitmentpar', pos=(0, 0, 0, 0))
        wnd.sr.main.children.append(self.recruitment)
        tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Recruitment'),
         self.recruitment,
         self,
         'recruitment',
         None,
         None])
        self.panels['recruitment'] = [self.recruitment]
        membersTabEntries = []
        self.panels['members'] = []
        if not util.IsNPC(eve.session.corpid):
            self.membertracking = form.CorpMemberTracking(name='membertrackingpar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.membertracking)
            membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/MemberList'),
             self.membertracking,
             self.membertracking,
             'main'])
            self.panels['members'].append(self.membertracking)
            (grantableRoles, grantableRolesAtHQ, grantableRolesAtBase, grantableRolesAtOther,) = self.corp.GetMyGrantableRoles()
            if session.corprole & const.corpRolePersonnelManager | grantableRoles:
                self.findmember = form.CorpFindMembersInRole(name='findmember', parent=wnd.sr.main, left=const.defaultPadding, width=const.defaultPadding)
                membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/FindMemberInRole'),
                 self.findmember,
                 self.findmember,
                 'findmember'])
                self.panels['members'].append(self.findmember)
                self.members = form.CorpMembers(name='members', pos=(0, 0, 0, 0))
                wnd.sr.main.children.append(self.members)
                membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/RoleManagement'),
                 self.members,
                 self.members,
                 'roles'])
                self.panels['members'].append(self.members)
            if const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector:
                self.titles = form.CorpTitles(name='titles', pos=(0, 0, 0, 0))
                wnd.sr.main.children.append(self.titles)
                membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/TitleManagement'),
                 self.titles,
                 self.titles,
                 'titles'])
                self.panels['members'].append(self.titles)
        if eve.session.corprole & const.corpRoleAuditor == const.corpRoleAuditor:
            self.auditing = form.CorpAuditing(name='auditingpar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.auditing)
            membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Auditing'),
             self.auditing,
             self.auditing,
             'main'])
            self.panels['members'].append(self.auditing)
        self.decorations = form.CorpDecorations(name='decorations', pos=(0, 0, 0, 0))
        wnd.sr.main.children.append(self.decorations)
        membersTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Decorations'),
         self.decorations,
         self.decorations,
         'decorations'])
        self.panels['members'].append(self.decorations)
        wnd.sr.membersTabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.main, idx=0)
        wnd.sr.membersTabs.Startup(membersTabEntries, 'corpmembersstab', autoselecttab=0)
        tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Members'),
         None,
         self,
         'members',
         wnd.sr.membersTabs])
        if not util.IsNPC(session.corpid):
            self.standings = form.CorpStandings(name='standingspar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.standings)
            tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Standings'),
             self.standings,
             self,
             'standings',
             None,
             standingsHint])
            self.panels['standings'] = [self.standings]
        politicsTabEntries = []
        self.panels['politics'] = []
        if self.corp.CanViewVotes(eve.session.corpid):
            self.votes = form.CorpVotes(name='votespar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.votes)
            politicsTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Votes'),
             self.votes,
             self.votes,
             'votes',
             None,
             votesHint])
            self.panels['politics'].append(self.votes)
            self.sanctionable = form.CorpSanctionableActions(name='sanctionablepar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.sanctionable)
            politicsTabEntries.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/SanctionableActions'),
             self.sanctionable,
             self.sanctionable,
             'sanctionable',
             None,
             sanctionableActionsHint])
            self.panels['politics'].append(self.sanctionable)
        self.wars = form.CorpWars(name='warspar', pos=(0, 0, 0, 0))
        wnd.sr.main.children.append(self.wars)
        tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Wars'),
         self.wars,
         self,
         'wars',
         None,
         warsHint])
        self.panels['wars'] = [self.wars]
        if len(self.panels['politics']):
            wnd.sr.politicsTabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.main, idx=0)
            wnd.sr.politicsTabs.Startup(politicsTabEntries, 'corppoliticsstab', autoselecttab=0)
            tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Politics'),
             None,
             self,
             'politics',
             wnd.sr.politicsTabs])
        if const.corpRoleAccountant & eve.session.corprole != 0 or self.corp.UserIsCEO():
            self.accounts = form.CorpAccounts(name='accountspar', pos=(0, 0, 0, 0))
            wnd.sr.main.children.append(self.accounts)
            tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Assets'),
             self.accounts,
             self,
             'accounts',
             None,
             accountsHint])
            self.panels['accounts'] = [self.accounts]
        self.alliances = form.Alliances(name='alliances', pos=(0, 0, 0, 0))
        wnd.sr.main.children.append(self.alliances)
        tabpanels.append([localization.GetByLabel('UI/Corporations/BaseCorporationUI/Alliances'),
         self.alliances,
         self,
         'alliances',
         None,
         alliancesHint])
        self.panels['alliances'] = [self.alliances]
        wnd.sr.maintabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.main)
        wnd.sr.maintabs.Startup(tabpanels, 'corporationpanel', UIIDPrefix='corporationTab', autoselecttab=False)
        if panelName:
            wnd.sr.maintabs.ShowPanelByName(panelName.capitalize())
        else:
            wnd.sr.maintabs.AutoSelect()
        if wnd is None or wnd.destroyed:
            self.Reset(1, 0, 0)
            return 
        uiutil.SetOrder(wnd.sr.maintabs, 0)
        wnd.HideLoad()
        wnd.state = uiconst.UI_NORMAL
        uthread.new(sm.StartService('wallet').AskSetWalletDivision)



    def Load(self, args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        for (k, v,) in self.panels.iteritems():
            if k == args:
                visible = uiconst.UI_PICKCHILDREN
            else:
                visible = uiconst.UI_HIDDEN
            for panel in v:
                panel.state = visible


        if args == 'members':
            wnd.sr.membersTabs.AutoSelect()
        elif args == 'politics':
            wnd.sr.politicsTabs.AutoSelect()
        else:
            self.panels[args][0].Load(args)



    def ShowLoad(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
            return 1



    def HideLoad(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.HideLoad()
            return 1



    def LoadLogo(self, corporationID):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            return self.panelHome.LoadLogo(corporationID)



    def LoadTop(self, icon, caption, subcaption = None):
        uiutil.FlushList(self.toparea.children[1:])
        if icon is None and caption is None:
            self.toparea.state = uiconst.UI_HIDDEN
        else:
            self.toparea.state = uiconst.UI_DISABLED
        self.toparea.children[0].top = -4
        if icon is not None:
            self.toparea.children[0].LoadIcon(icon)
        uicls.WndCaptionLabel(text=caption, subcaption=subcaption, parent=self.toparea, align=uiconst.RELATIVE)
        return self.toparea



    def OnSanctionedActionChanged(self, corpID, voteCaseID, change):
        self.LogInfo(self.__class__.__name__, 'OnSanctionedActionChanged')
        if self.sanctionable is not None:
            self.sanctionable.OnSanctionedActionChanged(corpID, voteCaseID, change)



    def OnCorporationVoteCaseChanged(self, corporationID, voteCaseID, change):
        self.LogInfo(self.__class__.__name__, 'OnCorporationVoteCaseChanged')
        if self.votes is not None:
            self.votes.OnCorporationVoteCaseChanged(corporationID, voteCaseID, change)



    def OnCorporationVoteCaseOptionChanged(self, corporationID, voteCaseID, optionID, change):
        self.LogInfo(self.__class__.__name__, 'OnCorporationVoteCaseOptionChanged')
        if self.votes is not None:
            self.votes.OnCorporationVoteCaseOptionChanged(corporationID, voteCaseID, optionID, change)



    def OnCorporationVoteChanged(self, corporationID, voteCaseID, characterID, change):
        self.LogInfo(self.__class__.__name__, 'OnCorporationVoteChanged')
        if self.votes is not None:
            self.votes.OnCorporationVoteChanged(corporationID, voteCaseID, characterID, change)



    def OnCorporationApplicationChanged(self, applicantID, corporationID, change):
        self.LogInfo(self.__class__.__name__, 'OnCorporationApplicationChanged')
        if self.recruitment is not None:
            self.recruitment.OnCorporationApplicationChanged(applicantID, corporationID, change)



    def OnCorporationRecruitmentAdChanged(self, corporationID, adID, change):
        self.LogInfo(self.__class__.__name__, 'OnCorporationRecruitmentAdChanged')
        if self.recruitment is not None:
            self.recruitment.OnCorporationRecruitmentAdChanged(corporationID, adID, change)



    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        self.LogInfo(self.__class__.__name__, 'OnAllianceApplicationChanged')
        if self.alliances is not None:
            self.alliances.OnAllianceApplicationChanged(allianceID, corpID, change)



    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        self.LogInfo(self.__class__.__name__, 'OnAllianceMemberChanged')
        if self.alliances is not None:
            self.alliances.OnAllianceMemberChanged(allianceID, corpID, change)



    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        self.LogInfo(self.__class__.__name__, 'OnAllianceRelationshipChanged')
        if self.alliances is not None:
            self.alliances.OnAllianceRelationshipChanged(allianceID, toID, change)



    def OnAllianceChanged(self, allianceID, change):
        self.LogInfo(self.__class__.__name__, 'OnAllianceChanged')
        if self.alliances is not None:
            self.alliances.OnAllianceChanged(allianceID, change)



    def OnWarChanged(self, warID, declaredByID, againstID, change):
        self.LogInfo(self.__class__.__name__, 'OnWarChanged')
        if self.wars is not None:
            self.wars.OnWarChanged(warID, declaredByID, againstID, change)



    def ViewApplication(self, corporationID):
        o = form.CorpApplications()
        o.ViewApplication(corporationID)



    def GetMemberDetails(self, charid):
        if getattr(self, 'inited', 0) and getattr(self, 'members', None):
            self.members.MemberDetails(charid)



    def VoteWindow(self, corpID):
        if corpID in self.votewindows:
            wnd = self.votewindows[corpID]
            if wnd is not None and not wnd.destroyed:
                wnd.Maximize()
                return wnd
        wnd = uicls.Window.Open(name='voting')
        wnd.scope = 'station_inflight'
        wnd.SetCaption(localization.GetByLabel('UI/Corporations/BaseCorporationUI/VoteWindowCaption', corporationName=cfg.eveowners.Get(corpID).name))
        wnd.SetMinSize([256, 256])
        wnd.SetWndIcon(None)
        wnd.SetTopparentHeight(0)
        voteform = form.CorpVotes(parent=wnd.sr.main)
        voteform.corpID = corpID
        voteform.isCorpPanel = 0
        voteform.Load(None)
        self.votewindows[corpID] = wnd
        return wnd



    def OnTitleChanged(self, corpID, titleID, change):
        self.LogInfo(self.__class__.__name__, 'OnTitleChanged')
        if self.titles is not None:
            self.titles.OnTitleChanged(corpID, titleID, change)



    def ApplyToJoinAlliance(self, allianceID):
        if not eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/OnlyForActiveCEO')})
        if eve.session.charid != sm.GetService('corp').GetCorporation().ceoID:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/OnlyForActiveCEO')})
        alliance = sm.GetService('alliance').GetAlliance(allianceID)
        corp = sm.GetService('corp').GetCorporation(alliance.executorCorpID)
        myCorpName = cfg.eveowners.Get(eve.session.corpid).ownerName
        allianceName = cfg.eveowners.Get(allianceID).ownerName
        stdText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/AskJoinAlliance', ceo=cfg.eveowners.Get(corp.ceoID).ownerName, mycorp=myCorpName, alliancename=allianceName, sender=session.charid, mycorpname=myCorpName)
        format = []
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'applicationText',
         'setvalue': stdText,
         'label': '_hide',
         'maxLength': 1000,
         'height': 96,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'text',
         'text': localization.GetByLabel('UI/Corporations/BaseCorporationUI/ThisApplicationOverwritesOlderOnes'),
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Corporations/BaseCorporationUI/AllianceApplication'), 1, None, uiconst.OKCANCEL, [128, 128], minH=120, unresizeAble=1)
        if retval is None:
            return 
        sm.GetService('corp').ApplyToJoinAlliance(allianceID, retval['applicationText'])



    def OnLockedItemChangeUI(self, itemID, ownerID, locationID, change):
        self.LogInfo(self.__class__.__name__, 'OnLockedItemChangeUI')
        if self.accounts is not None:
            self.accounts.OnLockedItemChangeUI(itemID, ownerID, locationID, change)



    def OnCorporationMedalAdded(self, *args):
        self.LogInfo(self.__class__.__name__, 'OnCorporationMedalAdded')
        if self.decorations is not None:
            self.decorations.OnCorporationMedalAdded(args)




class CorporationWindow(uicls.Window):
    __guid__ = 'form.Corporation'
    default_width = 550
    default_height = 635
    default_minSize = (550, 635)
    default_windowID = 'corporation'

    def OnUIRefresh(self):
        pass




