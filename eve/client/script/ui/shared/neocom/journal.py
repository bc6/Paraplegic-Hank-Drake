import service
import uix
import uiutil
import xtriui
import form
import util
import blue
import uthread
import listentry
import base
import uicls
import uiconst
import foo
import log
from contractutils import GetColoredContractStatusText, ConFmtDate, GetContractTitle
from incursion import IncursionTab
from operator import attrgetter
import re
NOBRREGX = re.compile('\\W*<br.*?>\\W*', re.I)
MAX_COL_LENGTH = 60

class ReportSortBy():
    (Constellation, LP, Jumps, Influence, StagingSolarSystem, Security,) = range(6)

REPORT_SORT_PARAMETERS = (('constellationName', False),
 ('loyaltyPoints', True),
 ('jumps', False),
 ('influence', True),
 ('stagingSolarSystemName', False),
 ('security', True))
REWARD_SCOUT = 8
REWARD_VANGUARD = 1
REWARD_ASSAULT = 2
REWARD_HQ = 3
REWARD_BOSS = 10
ENCOUNTERS = {'scout': (util.KeyVal(severity='scout', index=1, rewardID=REWARD_SCOUT),
           util.KeyVal(severity='scout', index=2, rewardID=REWARD_SCOUT),
           util.KeyVal(severity='scout', index=3, rewardID=REWARD_SCOUT),
           util.KeyVal(severity='scout', index=4, rewardID=REWARD_SCOUT)),
 'vanguard': (util.KeyVal(severity='vanguard', index=1, rewardID=REWARD_VANGUARD), util.KeyVal(severity='vanguard', index=2, rewardID=REWARD_VANGUARD), util.KeyVal(severity='vanguard', index=3, rewardID=REWARD_VANGUARD)),
 'assault': (util.KeyVal(severity='assault', index=1, rewardID=REWARD_ASSAULT), util.KeyVal(severity='assault', index=2, rewardID=REWARD_ASSAULT), util.KeyVal(severity='assault', index=3, rewardID=REWARD_ASSAULT)),
 'hq': (util.KeyVal(severity='hq', index=1, rewardID=REWARD_HQ),
        util.KeyVal(severity='hq', index=2, rewardID=REWARD_HQ),
        util.KeyVal(severity='hq', index=3, rewardID=REWARD_HQ),
        util.KeyVal(severity='hq', index=4, rewardID=REWARD_BOSS),
        util.KeyVal(severity='hq', index=5, rewardID=REWARD_BOSS))}

class LPTypeFilter():
    LPLost = -1
    LPPayedOut = -2


class JournalSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'Refresh': [],
     'GetMyAgentJournalDetails': [],
     'ShowContracts': [],
     'ShowIncursionTab': [service.ROLE_IGB]}
    __update_on_reload__ = 0
    __guid__ = 'svc.journal'
    __notifyevents__ = ['ProcessSessionChange',
     'OnAgentMissionChange',
     'OnDeleteContract',
     'OnEscalatingPathChange',
     'OnEscalatingPathMessage',
     'OnFleetEscalatingPathMessage',
     'OnLPStoreAcceptOffer',
     'OnLPChange',
     'OnPILaunchesChange',
     'OnEpicJournalChange']
    __servicename__ = 'journal'
    __displayname__ = 'Journal Client Service'
    __dependencies__ = ['window', 'settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Journal')
        self.Reset()
        self.outdatedAgentJournals = []
        self.contractFilters = {}
        self.outdatedCorpLP = True
        self.lpMapping = []
        self.pathPlexPositionByInstanceID = {}
        self.incursionLPLogData = None
        self.showingIncurisonTab = False



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()



    def ProcessSessionChange(self, isremote, session, change):
        if eve.session.charid is None:
            self.Stop()
            self.Reset()
        if 'locationid' in change:
            self.pathPlexPositionByInstanceID = {}
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and getattr(wnd.sr, 'maintabs', None):
            wnd.sr.maintabs.ReloadVisible()



    def OnAgentMissionChange(self, what, agentID, tutorialID = None):
        if agentID is None:
            self.agentjournal = None
        elif agentID not in self.outdatedAgentJournals:
            self.outdatedAgentJournals.append(agentID)
        sm.GetService('addressbook').RefreshWindow()
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and getattr(wnd.sr, 'maintabs', None):
            wnd.sr.maintabs.ReloadVisible()
        elif what not in (const.agentMissionDeclined,
         const.agentMissionCompleted,
         const.agentMissionQuit,
         const.agentMissionOfferAccepted,
         const.agentMissionOfferDeclined):
            sm.GetService('neocom').Blink('journal')



    def OnLPChange(self, what):
        self.outdatedCorpLP = True
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and getattr(wnd.sr, 'maintabs', None):
            wnd.sr.maintabs.ReloadVisible()
        else:
            sm.GetService('neocom').Blink('journal')



    def OnDeleteContract(self, contractID, *args):

        def DeleteContractInList(list, contractID):
            nodes = list.GetNodes()
            for n in nodes:
                if n.contract.contractID == contractID:
                    list.RemoveEntries([n])
                    return 



        wnd = self.GetWnd()
        if wnd is not None:
            list = wnd.sr.contractsListWnd
            DeleteContractInList(list, contractID)



    def OnEscalatingPathChange(self, *args):
        self.ShowExpeditions(1)



    def OnEscalatingPathMessage(self, instanceID):
        self.OnEscalatingPathChange(1)
        exp1 = self.GetExpeditions()
        exp2 = util.IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if not exp2.has_key(instanceID):
            exp1 = self.GetExpeditions(1)
            exp2 = util.IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if exp2.has_key(instanceID):
            data = util.KeyVal()
            data.rec = exp2[instanceID]
            self.PopupDungeonDescription(data)
        else:
            log.LogInfo("Someone tried loading a message that isn't there")



    def OnFleetEscalatingPathMessage(self, charID, pathStep):
        if charID != eve.session.charid:
            charName = ''
            charName = cfg.eveowners.GetIfExists(charID).name
            if not charName:
                charName = mls.UNKNOWN
            journalEntry = Tr(pathStep.journalEntryTemplate, 'dungeon.pathSteps.journalEntryTemplate', pathStep.dataID)
            data = util.KeyVal()
            data.instanceID = 0
            data.dungeonName = mls.PERSONSPEAKS % {'charName': charName}
            data.pathEntry = mls.UI_SHARED_EXPEDITIONFLEETTEXT % {'charName': '<b>%s</b>' % charName,
             'journalEntry': '<br><br>%s' % journalEntry}
            data.fakerec = True
            data.rec = data
            self.PopupDungeonDescription(data)



    def OnLPStoreAcceptOffer(self):
        self.outdatedCorpLP = True
        wnd = self.GetWnd()
        if wnd:
            wnd.sr.maintabs.ReloadVisible()



    def OnEpicJournalChange(self):
        self.epicJournalData = None
        wnd = self.GetWnd()
        if wnd:
            self.LoadEpicJournal(self.selectedArc)
        else:
            sm.GetService('neocom').Blink('journal')



    def Reset(self):
        self.entry = None
        self.agentjournal = None
        self.semaphore = uthread.Semaphore()
        self.notext = None
        self.expeditionRowset = None
        self.launchsRowSet = None
        self.lpMapping = []
        self.outdatedCorpLP = True
        self.curEpicArcId = None
        self.epicJournalData = None
        self.selectedArc = None



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def Refresh(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.maintabs.ReloadVisible()



    def GetWnd(self, new = 0, skipAutoSelect = False):
        if not sm.IsServiceRunning('window'):
            return 
        wnd = sm.GetService('window').GetWindow('journal')
        if not wnd and new:
            wnd = sm.GetService('window').GetWindow('journal', create=1, decoClass=form.Journal)
            wnd.SetScope('station_inflight')
            wnd.SetCaption(mls.UI_GENERIC_JOURNAL)
            wnd.MouseDown = self.WndMouseDown
            wnd.SetWndIcon('ui_25_64_3', mainTop=-7)
            wnd.SetTopparentHeight(0)
            wnd.sr.agenttabs = uicls.TabGroup(name='agenttabs', parent=wnd.sr.main)
            wnd.sr.incursiontabs = uicls.TabGroup(name='incursiontabs', parent=wnd.sr.main)
            width = settings.char.ui.Get('journalIncursionEncounterScrollWidth', 100)
            wnd.sr.incursionEncounterScroll = uicls.Scroll(parent=wnd.sr.main, name='encounterScroll', align=uiconst.TOLEFT, width=width, state=uiconst.UI_HIDDEN)
            self.LoadIncursionEncounters(wnd)
            divider = xtriui.Divider(name='incursionEncountersDivider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=wnd.sr.main, state=uiconst.UI_HIDDEN)
            divider.Startup(wnd.sr.incursionEncounterScroll, 'width', 'x', 100, 200)
            divider.OnSizeChanged = self.OnIncursionEncounterResize
            wnd.sr.incursionEncounterDivider = divider
            wnd.sr.incursionReportFilter = uicls.Container(name='incursionGlobalReportFilter', parent=wnd.sr.main, align=uiconst.TOTOP, height=36, state=uiconst.UI_HIDDEN)
            options = ((mls.UI_GENERIC_CONSTELLATION, ReportSortBy.Constellation),
             (mls.UI_INCURSION_STAGING_SYSTEM, ReportSortBy.StagingSolarSystem),
             (mls.UI_GENERIC_JUMPS, ReportSortBy.Jumps),
             (mls.UI_GENERIC_SECURITY, ReportSortBy.Security),
             (mls.UI_GENERIC_LP, ReportSortBy.LP),
             (mls.UI_INCURSION_INFLUENCE, ReportSortBy.Influence))
            wnd.sr.incursionReportSortCombo = uicls.Combo(label=mls.UI_CMD_SORTBY, parent=wnd.sr.incursionReportFilter, options=options, name='reportSortByCombo', callback=self.OnReportSortByComboChange, align=uiconst.TOLEFT, width=200, select=settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation), padding=(const.defaultPadding,
             18,
             0,
             0))
            refreshBtn = uix.GetBigButton(24, wnd.sr.incursionReportFilter, top=12, left=4)
            refreshBtn.hint = mls.UI_INCURSION_REPORT_HINT_REFRESH
            refreshBtn.sr.icon.LoadIcon('ui_105_32_22', ignoreSize=True)
            refreshBtn.SetAlign(uiconst.TOPRIGHT)
            refreshBtn.OnClick = lambda : self.ShowIncursionTab(IncursionTab.GlobalReport)
            wnd.sr.incursionLPLogFilters = uicls.Container(name='incursionLPLogFilters', parent=wnd.sr.main, height=36, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
            wnd.sr.incursionLPLoadbutton = uicls.Button(parent=wnd.sr.incursionLPLogFilters, label=mls.UI_GENERIC_LOAD, align=uiconst.BOTTOMRIGHT, func=self.LoadIncursionLPLog, left=4)
            now = util.FmtDate(blue.os.GetTime(), 'sn')
            wnd.sr.incursionLPDate = uicls.SinglelineEdit(name='incursionFromdate', parent=wnd.sr.incursionLPLogFilters, setvalue=now, align=uiconst.TOLEFT, maxLength=16, label=mls.UI_GENERIC_DATE, padding=(4, 16, 0, 0))
            options = [(mls.UI_SHARED_INCURSION_ALL, None)]
            wnd.sr.incursionLPTaleIDFilter = uicls.Combo(label=mls.UI_SHARED_INCURSIONS, parent=wnd.sr.incursionLPLogFilters, options=options, name='incursionTaleIDFilter', width=110, align=uiconst.TOLEFT, padding=(4, 16, 0, 0))
            options = [(mls.UI_SHARED_INCURSION_ALL_SOLARSYSTEM_TYPES, None)]
            wnd.sr.incursionLPTypeFilter = uicls.Combo(label=mls.UI_SHARED_INCURSION_SOLARSYSTEM_TYPE, parent=wnd.sr.incursionLPLogFilters, options=options, name='incursionTypeFilter', width=110, align=uiconst.TOLEFT, padding=(4, 16, 0, 0))
            wnd.sr.incursionEncounterEdit = uicls.Edit(parent=wnd.sr.main, name='incursionEncounterEdit', state=uiconst.UI_HIDDEN, readonly=True, align=uiconst.TOALL)
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.sr.scroll = uicls.Scroll(parent=wnd.sr.main, padding=(const.defaultPadding,) * 4)
            wnd.sr.scroll.multiSelect = 0
            wnd.sr.contractsWnd = uicls.Container(name='contracts', parent=wnd.sr.main, padding=(const.defaultPadding,) * 4, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
            filters = self.contractFiltersWnd = uicls.Container(name='filters', parent=wnd.sr.contractsWnd, height=36, align=uiconst.TOTOP)
            top = 13
            self.status = [(mls.UI_CONTRACTS_REQUIRESATTENTION, 0),
             (mls.UI_CONTRACTS_INPROGRESSISSUEDBY, 1),
             (mls.UI_CONTRACTS_INPROGRESSACCEPTEDBY, 2),
             (mls.UI_CONTRACTS_BIDONBY, 3)]
            c = self.statusCombo = uicls.Combo(label=mls.UI_GENERIC_STATUS, parent=filters, options=self.status, name='status', callback=self.OnComboChange, pos=(1,
             top,
             0,
             0), width=130)
            self.owners = [(mls.UI_GENERIC_ME, False), (mls.UI_GENERIC_MYCORPORATION, True)]
            c = self.ownerCombo = uicls.Combo(label=mls.UI_GENERIC_OWNER, parent=filters, options=self.owners, name='owner', callback=self.OnComboChange, pos=(c.width + c.left + 5,
             top,
             0,
             0))
            submit = uicls.Button(parent=filters, label=mls.UI_CONTRACTS_FETCHCONTRACTS, func=self.FetchContracts, pos=(c.left + c.width + 5,
             top,
             0,
             0))
            self.contractsNotifyWnd = uicls.Container(name='contractsnotify', parent=wnd.sr.contractsWnd, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=30, align=uiconst.TOBOTTOM)
            self.contractsNotifyWnd.state = uiconst.UI_HIDDEN
            wnd.sr.contractsListWnd = uicls.Scroll(parent=wnd.sr.contractsWnd)
            wnd.sr.contractsListWnd.multiSelect = 0
            self.CreateEpicJournal()
            wnd.sr.agenttabs.Startup([[mls.UI_GENERIC_MISSIONS,
              wnd.sr.scroll,
              self,
              ('agent_missions', 0)], [mls.UI_GENERIC_RESEARCH,
              wnd.sr.scroll,
              self,
              ('agent_research', 1)], [mls.UI_LPSTORE_LPS,
              wnd.sr.scroll,
              self,
              ('agent_lp', 2)]], 'journalagenttabs', autoselecttab=0)
            wnd.sr.incursiontabs.Startup([[mls.UI_SHARED_INCURSION_GLOBAL_REPORT,
              wnd.sr.scroll,
              self,
              ('incursions_globalreport', IncursionTab.GlobalReport)], [mls.UI_SHARED_INCURSION_ENCOUNTERS,
              wnd.sr.scroll,
              self,
              ('incursions_encounters', IncursionTab.Encounters)], [mls.UI_SHARED_INCURSION_LP_LOG,
              wnd.sr.scroll,
              self,
              ('incursions_lplog', IncursionTab.LPLog)]], 'journalincursiontabs', autoselecttab=0)
            wnd.sr.maintabs = uicls.TabGroup(name='maintabs', parent=wnd.sr.main, idx=0)
            wnd.sr.maintabs.Startup([[mls.UI_GENERIC_AGENTS,
              wnd.sr.scroll,
              self,
              ('agents', None)],
             [mls.UI_SHARED_EXPEDITIONS,
              wnd.sr.scroll,
              self,
              ('expeditions', None)],
             [mls.UI_CONTRACTS_CONTRACTS,
              wnd.sr.scroll,
              self,
              ('contracts', None)],
             [mls.UI_PI_LAUNCHES,
              wnd.sr.scroll,
              self,
              ('launches', None)],
             [mls.UI_GENERIC_EPIC_JOURNAL,
              wnd.sr.scroll,
              self,
              ('epicJournal', None)],
             [mls.UI_SHARED_INCURSIONS,
              wnd.sr.scroll,
              self,
              ('incursions', None)]], 'journalmaintabs', autoselecttab=0, UIIDPrefix='journalTab')
            if not skipAutoSelect:
                wnd.sr.maintabs.AutoSelect()
        return wnd



    def CreateEpicJournal(self):
        wnd = sm.GetService('window').GetWindow('journal')
        wnd.sr.epicJournalWnd = uicls.Container(name='epicJournal', parent=wnd.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        epicArcWidth = settings.user.ui.Get('journalEpicArcWidth', 100)
        self.epicArcContainer = uicls.Container(name='epicArcContainer', parent=wnd.sr.epicJournalWnd, align=uiconst.TOLEFT, clipChildren=1, width=epicArcWidth)
        self.epicArcTitle = uicls.Label(text='<center>' + mls.UI_GENERIC_EPIC_ARC_TITLE + '</center>', parent=self.epicArcContainer, height=20, align=uiconst.TOTOP, autoheight=False, state=uiconst.UI_NORMAL)
        self.epicArcScroll = uicls.Scroll(parent=self.epicArcContainer, name='epicArcScroll')
        self.epicArcScroll.OnSelectionChange = self.SelectEpicArc
        self.epicArcScroll.multiSelect = 0
        divider = xtriui.Divider(name='epicArcDivider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=wnd.sr.epicJournalWnd, state=uiconst.UI_NORMAL)
        divider.Startup(self.epicArcContainer, 'width', 'x', 100, 150)
        divider.OnSizeChanged = self.OnEpicArcSizeChanged
        epicMissionContainerWidth = settings.user.ui.Get('journalEpicMissionWidth', 150)
        self.epicMissionContainer = uicls.Container(name='epicMissionContainer', parent=wnd.sr.epicJournalWnd, align=uiconst.TORIGHT, clipChildren=1, width=epicMissionContainerWidth)
        self.epicMissionTitle = uicls.Label(text='<center>' + mls.UI_GENERIC_MISSIONS + '</center>', parent=self.epicMissionContainer, height=20, align=uiconst.TOTOP, autoheight=False, state=uiconst.UI_NORMAL)
        self.epicMissionScroll = uicls.Scroll(parent=self.epicMissionContainer, name='epicMissionScroll')
        self.epicMissionScroll.OnSelectionChange = self.SelectEpicMission
        self.epicMissionScroll.multiSelect = 0
        divider = xtriui.Divider(name='epicMissionDivider', align=uiconst.TORIGHT, width=const.defaultPadding, parent=wnd.sr.epicJournalWnd, state=uiconst.UI_NORMAL)
        divider.Startup(self.epicMissionContainer, 'width', 'x', 100, 200)
        divider.OnSizeChanged = self.OnEpicMissionSizeChanged
        self.epicMainContainer = uicls.Container(name='epicMainContainer', parent=wnd.sr.epicJournalWnd, align=uiconst.TOALL, clipChildren=1)
        self.epicArcTitleImage = uicls.Sprite(name='epicArcTitleImage', parent=self.epicMainContainer, align=uiconst.TOTOP)
        self.epicArcTitleImage._OnSizeChange_NoBlock = self.OnEpicArcTitleImageResize
        self.epicJournalText = uicls.Edit(parent=self.epicMainContainer, readonly=1)



    def OnEpicArcTitleImageResize(self, width, height):
        if width:
            self.epicArcTitleImage.height = int(width / 2.5)



    def OnEpicArcSizeChanged(self):
        settings.user.ui.Set('journalEpicArcWidth', self.epicArcContainer.width)



    def OnEpicMissionSizeChanged(self):
        settings.user.ui.Set('journalEpicMissionWidth', self.epicMissionContainer.width)



    def LoadEpicJournal(self, selectedArcName = None):
        scrolllist = []
        arcs = self.GetEpicArcs()
        selectIndex = 0
        for (i, (completed, arcName,),) in enumerate(arcs):
            if selectedArcName == arcName:
                selectIndex = i
            hint = arcName
            if completed:
                arcName = '<i>' + arcName + '</i>'
                hint += ' (' + mls.UI_GENERIC_COMPLETED + ')'
            else:
                hint += ' (' + mls.UI_GENERIC_INPROGRESS + ')'
            scrolllist.append(listentry.Get('Generic', {'label': arcName,
             'value': i,
             'hint': hint}))

        self.epicArcScroll.Load(contentList=scrolllist)
        self.epicArcScroll.SetSelected(selectIndex)
        if len(arcs) == 0:
            self.epicJournalText.SetText('<font size=20><b>' + uiutil.UpperCase(mls.UI_GENERIC_NO_EPIC_ARCS) + '</b></font>')



    def LoadEpicArc(self, epicArcId):
        self.curEpicArcId = epicArcId
        texture = self.epicArcTitleImage.texture
        texture.resPath = self.GetEpicArcGraphic(epicArcId)
        while texture.atlasTexture.isLoading:
            blue.synchro.Yield()

        self.epicArcTitleImage.state = uiconst.UI_NORMAL
        scrolllist = []
        missionTextList = []
        for (i, (chapterTitle, missionName, missionText, branches,),) in enumerate(self.GetEpicArcMissions(epicArcId)):
            if chapterTitle:
                scrolllist.append(listentry.Get('Subheader', {'label': uiutil.UpperCase(chapterTitle)}))
            if branches:
                branchList = [mls.UI_GENERIC_EPIC_BRANCHING_POINT]
                for branch in branches:
                    branchList.append(branch)

                scrolllist.append(listentry.Get('IconEntry', {'label': missionName,
                 'hint': '<BR>'.join(branchList),
                 'icon': 'ui_38_16_87',
                 'iconsize': 16,
                 'value': i}))
            else:
                scrolllist.append(listentry.Get('Generic', {'label': missionName,
                 'value': i}))

        self.epicMissionScroll.Load(contentList=scrolllist)
        self.LoadEpicArcText()



    def LoadEpicArcText(self, selectedMissionId = None):
        if self.curEpicArcId is None:
            return 
        missionTextList = []
        for (i, (chapterTitle, missionName, missionText, branches,),) in enumerate(self.GetEpicArcMissions(self.curEpicArcId)):
            if chapterTitle:
                if i != 0:
                    missionTextList.append('<BR>')
                missionTextList.append('<font size=16>' + chapterTitle + '</font>')
            if missionText:
                if selectedMissionId == i:
                    missionTextList.append('<img src=icon:38_254 size=16><b><font size=14>' + missionText + '</font></b>')
                else:
                    missionTextList.append('<img src=icon:38_254 size=12>' + missionText)

        self.epicJournalText.SetText('<BR>'.join(missionTextList))



    def SelectEpicArc(self, selected):
        if len(selected):
            self.LoadEpicArc(selected[0].value)
            self.selectedArc = selected[0].label
        else:
            self.epicMissionScroll.Clear()
            self.epicArcTitleImage.state = uiconst.UI_HIDDEN
            self.epicJournalText.SetText('')



    def SelectEpicMission(self, selected):
        if len(selected) and hasattr(selected[0], 'value'):
            self.LoadEpicArcText(selected[0].value)
        else:
            self.LoadEpicArcText()



    def ShowEpicJournal(self, open = False):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.epicJournalWnd.state = uiconst.UI_NORMAL
            self.LoadEpicJournal(self.selectedArc)
            self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_GENERIC_EPIC_JOURNAL))
        if open:
            self.Show()



    def MouseEnterHighlightOn(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 0.0)



    def MouseExitHighlightOff(self, wnd, *args):
        wnd.color.SetRGB(1.0, 1.0, 1.0)



    def ShowContracts(self, *args):
        self.Show()
        forCorp = False
        status = 0
        if len(args) > 0:
            wnd = args[0]
            forCorp = wnd.forCorp
        if len(args) > 1:
            status = args[1]
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.maintabs.ShowPanelByName(mls.UI_CONTRACTS_CONTRACTS)
            self.contractFilters['status'] = status
            self.contractFilters['forCorp'] = forCorp
            uthread.new(self.DelayedShowContracts)



    def Load(self, args):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        (key, flag,) = args
        self.SetHint()
        wnd.sr.contractsWnd.state = uiconst.UI_HIDDEN
        wnd.sr.epicJournalWnd.state = uiconst.UI_HIDDEN
        wnd.sr.incursiontabs.state = uiconst.UI_HIDDEN
        wnd.sr.incursionReportFilter.state = uiconst.UI_HIDDEN
        wnd.sr.incursionEncounterScroll.state = uiconst.UI_HIDDEN
        wnd.sr.incursionEncounterEdit.state = uiconst.UI_HIDDEN
        wnd.sr.agenttabs.state = uiconst.UI_HIDDEN
        wnd.sr.scroll.state = uiconst.UI_HIDDEN
        wnd.sr.incursionLPLogFilters.state = uiconst.UI_HIDDEN
        if key == 'agents':
            wnd.sr.scroll.state = uiconst.UI_NORMAL
            wnd.sr.agenttabs.state = uiconst.UI_NORMAL
            wnd.sr.agenttabs.AutoSelect(silently=1)
        elif key[:6] == 'agent_':
            wnd.sr.scroll.state = uiconst.UI_NORMAL
            wnd.sr.agenttabs.state = uiconst.UI_NORMAL
            self.ShowAgentTab(flag)
        elif key == 'expeditions':
            wnd.sr.scroll.state = uiconst.UI_NORMAL
            self.ShowExpeditions()
        elif key == 'contracts':
            wnd.sr.contractsWnd.state = uiconst.UI_NORMAL
            self.DoShowContracts()
        elif key == 'epicJournal':
            self.ShowEpicJournal()
        elif key == 'launches':
            wnd.sr.scroll.state = uiconst.UI_NORMAL
            self.ShowPILaunches()
        elif key.startswith('incursions'):
            wnd.sr.incursiontabs.state = uiconst.UI_NORMAL
            self.ShowIncursionTab(flag)



    def _SelectTab(self, tab):
        if not tab.IsSelected():
            tab.Select(1)



    def WndMouseDown(self, *args):
        sm.GetService('neocom').BlinkOff('journal')



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.ShowHint(hintstr)



    def ShowIncursionTab(self, flag = None, constellationID = None, taleID = None, open = False):
        if self.showingIncurisonTab:
            return 
        self.showingIncurisonTab = True
        if flag is None:
            flag = settings.char.ui.Get('journalIncursionTab', IncursionTab.GlobalReport)
        settings.char.ui.Set('journalIncursionTab', flag)
        wnd = self.GetWnd(new=open, skipAutoSelect=True)
        if wnd is not None and not wnd.destroyed:
            blue.pyos.synchro.Yield()
            self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_SHARED_INCURSIONS))
            self._SelectTab(wnd.sr.incursiontabs.sr.tabs[flag])
            if flag == IncursionTab.GlobalReport:
                wnd.sr.scroll.state = uiconst.UI_NORMAL
                wnd.sr.incursionReportFilter.state = uiconst.UI_PICKCHILDREN
                pathfinder = sm.GetService('pathfinder')
                starmap = sm.GetService('starmap')
                map = starmap.map

                def GetJumps(toID):
                    path = pathfinder.GetPathBetween(session.solarsystemid2, toID)
                    if path:
                        return len(path) - 1


                report = sm.RemoteSvc('map').GetIncursionGlobalReport()
                rewardGroupIDs = [ r.rewardGroupID for r in report ]
                delayedRewards = sm.GetService('incursion').GetDelayedRewardsByGroupIDs(rewardGroupIDs)
                scrolllist = []
                factionsToPrime = set()
                for data in report:
                    data.jumps = GetJumps(data.stagingSolarSystemID)
                    data.influenceData = util.KeyVal(influence=data.influence, lastUpdated=data.lastUpdated, graceTime=data.graceTime, decayRate=data.decayRate)
                    ssitem = map.GetItem(data.stagingSolarSystemID)
                    data.stagingSolarSystemName = ssitem.itemName
                    data.security = map.GetSecurityStatus(data.stagingSolarSystemID)
                    data.constellationID = ssitem.locationID
                    data.constellationName = map.GetItem(ssitem.locationID).itemName
                    data.factionID = ssitem.factionID or starmap.GetAllianceSolarSystems().get(data.stagingSolarSystemID, None)
                    factionsToPrime.add(data.factionID)
                    rewards = delayedRewards.get(data.rewardGroupID, None)
                    data.loyaltyPoints = rewards[0].rewardQuantity if rewards else 0
                    scrolllist.append(listentry.Get('GlobalIncursionReportEntry', data))

                cfg.eveowners.Prime(list(factionsToPrime))
                wnd.sr.scroll.LoadContent(contentList=scrolllist, scrollTo=0.0)
                self.SortIncursionGlobalReport()
            elif flag == IncursionTab.LPLog:
                wnd.sr.incursionLPLogFilters.state = uiconst.UI_NORMAL
                wnd.sr.scroll.state = uiconst.UI_NORMAL
                if taleID is not None and constellationID is not None:
                    self.LoadIncursionLPLog(wnd.sr.scroll, taleID, constellationID)
                elif self.incursionLPLogData is None:
                    wnd.sr.scroll.Clear()
                    wnd.sr.scroll.ShowHint(mls.UI_SHARED_CLICKLOADTOFETCH)
                else:
                    self.UpdateIncursionLPLog(self.incursionLPLogData)
            elif flag == IncursionTab.Encounters:
                wnd.sr.incursionEncounterEdit.state = uiconst.UI_NORMAL
                wnd.sr.incursionEncounterScroll.state = uiconst.UI_NORMAL
                wnd.sr.incursionEncounterDivider.state = uiconst.UI_NORMAL
        self.showingIncurisonTab = False
        if open:
            self.Show()



    def OnIncursionEncounterResize(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            settings.char.ui.Set('journalIncursionEncounterScrollWidth', wnd.sr.incursionEncounterScroll.width)



    def OnReportSortByComboChange(self, combo, key, value):
        self.SortIncursionGlobalReport(value)



    def LoadIncursionLPLog(self, scroll, taleID = None, constellationID = None):
        rewardMgr = session.ConnectToRemoteService('rewardMgr')
        self.incursionLPLogData = rewardMgr.GetRewardLPLogs()
        self.UpdateIncursionLPLog(self.incursionLPLogData, taleID, constellationID)



    def UpdateIncursionLPLog(self, data, selectedTaleID = None, selectedConstellationID = None):
        wnd = self.GetWnd()
        mapsvc = sm.GetService('map')
        taleIDFilter = wnd.sr.incursionLPTaleIDFilter.selectedValue
        solarsystemTypeFilter = wnd.sr.incursionLPTypeFilter.selectedValue
        try:
            fromDate = util.ParseSmallDate(wnd.sr.incursionLPDate.GetValue())
        except (Exception, TypeError):
            dateString = util.FmtDate(blue.os.GetTime(), 'sn')
            fromDate = util.ParseDate(dateString)
            wnd.sr.incursionLPDate.SetValue(dateString)
        fromDate += const.DAY
        dungeonTypes = set()
        taleIDs = {}
        filteredData = []
        for d in data:
            dungeonTypes.add(d.rewardMessageKey)
            constellationID = mapsvc.GetParent(d.solarSystemID)
            if constellationID is not None:
                constellation = mapsvc.GetItem(constellationID)
                if constellation is not None:
                    taleIDs[d.taleID] = constellation.itemName
            if selectedTaleID is not None:
                if selectedTaleID != d.taleID:
                    continue
            if taleIDFilter is not None and selectedTaleID is None:
                if taleIDFilter != d.taleID:
                    continue
            if solarsystemTypeFilter is not None:
                shouldAdd = False
                if solarsystemTypeFilter == LPTypeFilter.LPPayedOut:
                    if d.eventTypeID == const.eventRewardLPPayedOut:
                        shouldAdd = True
                elif solarsystemTypeFilter == LPTypeFilter.LPLost:
                    if d.eventTypeID == const.eventRewardLPPoolLost:
                        shouldAdd = True
                elif solarsystemTypeFilter == d.rewardMessageKey:
                    shouldAdd = True
                if not shouldAdd:
                    continue
            if fromDate < d.date:
                continue
            filteredData.append(d)

        if selectedTaleID is not None:
            if selectedTaleID not in taleIDs:
                constellation = mapsvc.GetItem(selectedConstellationID)
                if constellation is not None:
                    taleIDs[selectedTaleID] = constellation.itemName
        scrolllist = []
        for d in filteredData:
            solarSystemType = ''
            if d.eventTypeID == const.eventRewardLPPayedOut:
                solarSystemType = mls.UI_SHARED_INCURSION_LP_PAYED_OUT
            elif d.eventTypeID == const.eventRewardLPPoolLost:
                solarSystemType = mls.UI_SHARED_INCURSION_LP_LOST
            elif d.rewardMessageKey is not None and d.rewardMessageKey != '':
                solarSystemType = getattr(mls, d.rewardMessageKey)
            if d.lpAmountAddedToPool is None:
                d.lpAmountAddedToPool = 0
            if d.lpAmountAddedToPool == 0:
                LPAmountAddedToPool = '<color=0xFFFFFFFF>0</color>'
            else:
                LPAmountAddedToPool = '<color=0xFFFFFF00>%d</color>' % d.lpAmountAddedToPool
            if d.lpAmountPayedOut is None:
                d.lpAmountPayedOut = 0
            if d.lpAmountPayedOut == 0:
                LPAmountPayedOut = '<color=0xFFFFFFFF>0</color>'
            elif d.eventTypeID == const.eventRewardLPPoolLost:
                LPAmountPayedOut = '<color=0xFFFF0000>%d</color>' % 0
            else:
                LPAmountPayedOut = '<color=0xFF00FF00>%d</color>' % d.lpAmountPayedOut
            timeString = util.FmtSimpleDateUTC(d.date)
            if d.numberOfPlayers is None:
                d.numberOfPlayers = 0
            description = ''
            if d.eventTypeID == const.eventRewardLPDisqualified:
                if d.disqualifierType == const.rewardIneligibleReasonTrialAccount:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_TRIAL
                elif d.disqualifierType == const.rewardIneligibleReasonInvalidGroup:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_WRONG_SHIP % {'groupName': cfg.invgroups.Get(d.disqualifierData).groupName}
                elif d.disqualifierType == const.rewardIneligibleReasonShipCloaked:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_CLOAKED
                elif d.disqualifierType == const.rewardIneligibleReasonNotInFleet:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_NO_FLEET
                elif d.disqualifierType == const.rewardIneligibleReasonNotBestFleet:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_NOT_BEST_FLEET
                elif d.disqualifierType == const.rewardIneligibleReasonNotTop5:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_NOT_IN_TOP5
                elif d.disqualifierType == const.rewardIneligibleReasonNotRightAmoutOfPlayers:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_NOT_RIGHT_AMOUNT_PLAYERS
                elif d.disqualifierType == const.rewardIneligibleReasonTaleAlreadyEnded:
                    description = mls.UI_REWARD_DESCRIPTION_DISQUALIFIED_INCURSION_ALREADY_ENDED
            elif d.eventTypeID == const.eventRewardLPStoredInPool:
                description = mls.UI_SHARED_INCURSION_DESCRIPTION_LP_STORED % {'rewardedPlayers': d.numberOfPlayers}
            elif d.eventTypeID == const.eventRewardLPPayedOut:
                description = mls.UI_SHARED_INCURSION_DESCRIPTION_LP_PAYOUT
            elif d.eventTypeID == const.eventRewardLPPoolLost:
                description = mls.UI_SHARED_INCURSION_DESCRIPTION_LP_LOST
            hint = description
            description = NOBRREGX.sub(' ', description)
            texts = [timeString,
             solarSystemType,
             d.dungeonName,
             LPAmountAddedToPool,
             LPAmountPayedOut,
             description]
            label = '<t>'.join(texts)
            scrolllist.append(listentry.Get('Generic', {'label': label,
             'sort_%s' % mls.UI_SHARED_INCURSION_LP_STORED_IN_POOL_HEADER: d.lpAmountAddedToPool,
             'sort_%s' % mls.UI_SHARED_INCURSION_LP_PAYED_OUT_HEADER: d.lpAmountPayedOut,
             'hint': hint}))

        headers = [mls.UI_GENERIC_DATE,
         mls.UI_SHARED_INCURSION_SOLARSYSTEM_TYPE,
         mls.UI_SHARED_INCURSION_DUNGEON_NAME,
         mls.UI_SHARED_INCURSION_LP_STORED_IN_POOL_HEADER,
         mls.UI_SHARED_INCURSION_LP_PAYED_OUT_HEADER,
         mls.UI_SHARED_INCURSION_DESCRIPTION_HEADER]
        options = [(mls.UI_SHARED_INCURSION_ALL, None)]
        for (taleID, constellationName,) in taleIDs.iteritems():
            options.append((constellationName, taleID))

        wnd.sr.incursionLPTaleIDFilter.LoadOptions(options)
        if selectedTaleID is None:
            wnd.sr.incursionLPTaleIDFilter.SelectItemByValue(taleIDFilter)
        else:
            wnd.sr.incursionLPTaleIDFilter.SelectItemByValue(selectedTaleID)
        options = [(mls.UI_SHARED_INCURSION_ALL_SOLARSYSTEM_TYPES, None), (mls.UI_SHARED_INCURSION_LP_LOST, LPTypeFilter.LPLost), (mls.UI_SHARED_INCURSION_LP_PAYED_OUT, LPTypeFilter.LPPayedOut)]
        for dungeonType in dungeonTypes:
            if dungeonType is not None and dungeonType != '':
                options.append((getattr(mls, dungeonType), dungeonType))

        wnd.sr.incursionLPTypeFilter.LoadOptions(options)
        wnd.sr.incursionLPTypeFilter.SelectItemByValue(solarsystemTypeFilter)
        if scrolllist:
            sortBy = wnd.sr.scroll.GetSortBy()
            sortDirection = wnd.sr.scroll.GetSortDirection()
            wnd.sr.scroll.LoadContent(contentList=scrolllist, reversesort=1, headers=headers, scrollTo=0.0)
            if sortBy is None:
                wnd.sr.scroll.Sort(by=mls.UI_GENERIC_DATE, reversesort=1)
            else:
                wnd.sr.scroll.Sort(by=sortBy, reversesort=sortDirection)
        else:
            wnd.sr.scroll.Clear()
            wnd.sr.scroll.ShowHint(mls.UI_GENERIC_NORECORDSFOUND)



    def SortIncursionGlobalReport(self, sortBy = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            if sortBy is None:
                sortBy = settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation)
            else:
                settings.char.ui.Set('journalIncursionReportSort', sortBy)
            (attrName, reverse,) = REPORT_SORT_PARAMETERS[sortBy]
            scroll = wnd.sr.scroll
            sort = sorted(scroll.sr.nodes, key=attrgetter(attrName), reverse=reverse)
            scroll.sr.nodes = sorted(scroll.sr.nodes, key=attrgetter(attrName), reverse=reverse)
            scroll.UpdatePositionThreaded(fromWhere='SortIncursionGlobalReport')



    def ShowEncounter(self, node):
        data = node.sr.node
        enc = data.encounter
        wnd = self.GetWnd()
        if wnd is not None:
            params = (enc.severity.upper(), enc.index)
            html = getattr(mls, 'UI_INCURSION_ENCOUNTER_%s_%d' % params)
            params = {'lpAmount': util.FmtAmt(data.lpAmount),
             'iskAmount': util.FmtAmt(data.iskAmount),
             'imageAttributes': 'size=250 style=margin-left:8;margin-top:8'}
            wnd.sr.incursionEncounterEdit.LoadHTML(html % params)



    def GetEncounterSubContent(self, data, *args):
        scrolllist = []
        incursionSvc = sm.GetService('incursion')
        for encounter in data.encounters:
            data = {'label': getattr(mls, 'UI_INCURSION_ENCOUNTER_%s_%d_NAME' % (encounter.severity.upper(), encounter.index)),
             'OnClick': self.ShowEncounter,
             'encounter': encounter,
             'lpAmount': incursionSvc.GetMaxRewardValueByID(encounter.rewardID, const.rewardTypeLP),
             'iskAmount': incursionSvc.GetMaxRewardValueByID(encounter.rewardID, const.rewardTypeISK)}
            scrolllist.append(listentry.Get('Generic', data))

        return scrolllist



    def LoadIncursionEncounters(self, wnd):
        scrolllist = []
        for level in ('scout', 'vanguard', 'assault', 'hq'):
            data = {'GetSubContent': self.GetEncounterSubContent,
             'label': getattr(mls, 'UI_INCURSION_%s' % level.upper()),
             'encounters': ENCOUNTERS[level],
             'sublevel': 0,
             'selected': False,
             'id': ('encounter', level),
             'showlen': False,
             'state': 'locked',
             'BlockOpenWindow': True,
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))

        wnd.sr.incursionEncounterScroll.LoadContent(contentList=scrolllist)



    def GetLaunches(self, force = 0):
        if self.launchsRowSet is None or force:
            self.launchsRowSet = sm.RemoteSvc('planetMgr').GetMyLaunchesDetails()
        return self.launchsRowSet



    def OnPILaunchesChange(self, *args):
        self.ShowPILaunches(1)
        sm.GetService('neocom').Blink('journal')



    def ShowPILaunches(self, reload = 0):
        self.launchsRowSet = self.GetLaunches(force=reload)
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
            try:
                headers = [mls.UI_PI_REENTRYIN,
                 mls.UI_GENERIC_SOLARSYSTEM,
                 mls.PLANET,
                 mls.UI_PI_LAUNCHTIME]
                scrolllist = []
                for launch in self.launchsRowSet:
                    lable = '    <t>'
                    lable += '%s<t>' % cfg.evelocations.Get(launch.solarSystemID).name
                    lable += '%s<t>' % cfg.evelocations.Get(launch.planetID).name
                    lable += '%s' % util.FmtDate(launch.launchTime)
                    data = {'id': launch.launchID,
                     'label': lable,
                     'callback': None,
                     'selected': 0,
                     'expired': [True, False][(blue.os.GetTime() - launch.launchTime < const.piLaunchOrbitDecayTime)],
                     'rec': launch}
                    scrolllist.append(listentry.Get('PlanetaryInteractionLaunchEntry', data))

                wnd.sr.scroll.sr.id = 'launchesScroll'
                wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_PI_NOACTIVELAUNCHES)
                self.AutoUpdateLaunchDecayTimes()
                wnd.sr.launchtimer = base.AutoTimer(1000, self.AutoUpdateLaunchDecayTimes)

            finally:
                if wnd is not None and not wnd.destroyed:
                    self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_PI_LAUNCHES))
                    wnd.HideLoad()




    def AutoUpdateLaunchDecayTimes(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        if wnd.sr.maintabs.GetSelectedArgs()[0] != 'launches':
            wnd.sr.launchtimer = None
            return 
        for entry in wnd.sr.scroll.GetNodes():
            text = entry.label
            if not entry.rec:
                continue
            expiryLabel = ''
            expiryNumeric = blue.os.GetTime() - entry.rec.launchTime
            if expiryNumeric < const.piLaunchOrbitDecayTime:
                expiryLabel = '<color=0xFFFFFF00>%s</color>' % util.FmtDate(const.piLaunchOrbitDecayTime - expiryNumeric, 'ss')
            else:
                expiryLabel = '<color=0xffeb3700>%s</color>' % mls.UI_PI_BURNEDUP
                entry.expired = True
            entry.label = expiryLabel + text[len(text[:text.find('<t>')]):]
            if entry.panel:
                entry.panel.Load(entry)




    def GetExpeditions(self, force = 0):
        if self.expeditionRowset and not force:
            return self.expeditionRowset
        if not self.expeditionRowset or force:
            self.expeditionRowset = sm.RemoteSvc('dungeonExplorationMgr').GetMyEscalatingPathDetails()
        return self.expeditionRowset



    def ShowExpeditions(self, reload = 0):
        self.expeditionRowset = self.GetExpeditions(force=reload)
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
            try:
                headers = [mls.UI_GENERIC_EXPIRES,
                 mls.UI_GENERIC_CREATED,
                 mls.UI_GENERIC_SOLARSYSTEM,
                 mls.UI_GENERIC_JUMPS,
                 mls.UI_GENERIC_DESCRIPTION]
                scrolllist = []
                for expeditionData in self.expeditionRowset:
                    dungeonData = expeditionData.dungeon
                    srcDungeonData = expeditionData.srcDungeon
                    destDungeonData = expeditionData.destDungeon
                    pathStep = expeditionData.pathStep
                    expiryTime = expeditionData.expiryTime
                    if destDungeonData is not None:
                        jumps = sm.GetService('starmap').ShortestPath(dungeonData.solarSystemID, eve.session.solarsystemid2)
                        jumps = jumps or []
                        totaljumps = max(0, len(jumps) - 1)
                        if dungeonData.solarSystemID is not None:
                            solName = cfg.evelocations.Get(dungeonData.solarSystemID).name
                        else:
                            solName = mls.UI_GENERIC_UNKNOWN
                        txt = Tr(pathStep.journalEntryTemplate, 'dungeon.pathSteps.journalEntryTemplate', pathStep.dataID)
                        if len(txt) > MAX_COL_LENGTH:
                            txt = txt[:MAX_COL_LENGTH] + '...'
                        text = '%s<t>%s<t>%s<t>%s<t>%s' % ('      ',
                         util.FmtDate(dungeonData.creationTime),
                         solName,
                         totaljumps,
                         txt)
                        data = {'id': dungeonData.instanceID,
                         'rec': expeditionData,
                         'text': txt,
                         'label': text,
                         'hint': pathStep.journalEntryTemplate,
                         'jumps': totaljumps,
                         'expired': [True, False][(expiryTime - blue.os.GetTime() > 0)],
                         'sort_%s' % mls.UI_GENERIC_EXPIRES: expiryTime}
                        scrolllist.append(listentry.Get('EscalatingPathLocationEntry', data))

                wnd.sr.scroll.sr.id = 'expeditionScroll'
                wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_SHARED_NOACTIVEEXPEDITIONS)
                self.AutoUpdateExpeditionTimes()
                wnd.sr.expeditiontimer = base.AutoTimer(1000, self.AutoUpdateExpeditionTimes)

            finally:
                if wnd is not None and not wnd.destroyed:
                    self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_SHARED_EXPEDITIONS))
                    wnd.HideLoad()




    def PopupDungeonDescription(self, node):
        if node.get('fakerec', None):
            did = node.instanceID
            dname = node.dungeonName
            djentry = node.pathEntry
        elif node.rec:
            dungeonDstData = node.rec.destDungeon
            dungeonSrcData = node.rec.srcDungeon
            dungeonInstanceID = node.rec.dungeon.instanceID
            dungeonPath = node.rec.pathStep
        else:
            dungeonDstData = node.destDungeon
            dungeonSrcData = node.rec.srcDungeon
            dungeonInstanceID = node.dungeon.instanceID
            dungeonPath = node.pathStep
        did = dungeonInstanceID
        if dungeonDstData is not None:
            dname = Tr(dungeonDstData.dungeonName, 'dungeon.dungeons.dungeonName', dungeonDstData.dataID)
        elif dungeonSrcData is not None:
            dname = Tr(dungeonSrcData.dungeonName, 'dungeon.dungeons.dungeonName', dungeonSrcData.dataID)
        else:
            log.LogError('No dungeon data to get dungeon name from. id:', did)
            return 
        djentry = Tr(dungeonPath.journalEntryTemplate, 'dungeon.pathSteps.journalEntryTemplate', dungeonPath.dataID)
        data = util.KeyVal()
        data.rec = node
        data.header = dname
        data.icon = '40_14'
        data.text = djentry
        data.caption = mls.UI_SHARED_EXPEDITIONS
        data.hasDungeonWarp = True
        data.instanceID = did
        wnd = sm.GetService('transmission').OnIncomingTransmission(data)



    def AutoUpdateExpeditionTimes(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return 
        if wnd.sr.maintabs.GetSelectedArgs()[0] != 'expeditions':
            wnd.sr.expeditiontimer = None
            return 
        for entry in wnd.sr.scroll.GetNodes():
            text = entry.label
            if not entry.rec:
                continue
            expiryLabel = ''
            expiryNumeric = entry.rec.expiryTime - blue.os.GetTime()
            if expiryNumeric > 0:
                expiryLabel = '<color=0xFFFFFF00>%s</color>' % util.FmtDate(expiryNumeric, 'ss')
            else:
                expiryLabel = '<color=0xffeb3700>%s</color>' % mls.UI_GENERIC_EXPIRED
            entry.label = expiryLabel + text[len(text[:text.find('<t>')]):]
            if entry.panel:
                entry.panel.Load(entry)




    def DoShowContracts(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
        try:
            sm.GetService('neocom').BlinkOff('contracts')
            filtPriceMin = 0
            filtPriceMax = 0
            filters = {'string': '',
             'view': -1,
             'status': 0,
             'priceMin': filtPriceMin,
             'priceMax': filtPriceMax}
            forCorp = self.contractFilters.get('forCorp', False)
            status = int(self.contractFilters.get('status', 0))
            numRequiresAttention = numCorpRequiresAttention = 0
            l = sm.GetService('contracts').GetMyExpiredContractList()
            expiredContracts = l.mySelf
            expiredCorpContracts = l.myCorp
            numRequiresAttention = len(expiredContracts.contracts)
            if eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager:
                numCorpRequiresAttention = len(expiredCorpContracts.contracts)
            if status == 0:
                _contracts = {False: expiredContracts,
                 True: expiredCorpContracts}[forCorp]
            elif status == 3:
                _contracts = sm.GetService('contracts').GetMyBids(forCorp).list
            else:
                _contracts = sm.GetService('contracts').GetMyCurrentContractList(status == 2, forCorp).list
            if not _contracts:
                wnd.sr.contractsListWnd.Load(contentList=[], headers=[], noContentHint=mls.UI_CONTRACTS_NOCONTRACTSFOUND)
            contracts = _contracts.contracts
            ownerIDs = {}
            for r in contracts:
                ownerIDs[r.issuerID] = 1
                ownerIDs[r.issuerCorpID] = 1
                ownerIDs[r.acceptorID] = 1
                ownerIDs[r.assigneeID] = 1

            cfg.eveowners.Prime(ownerIDs.keys())
            scrolllist = []
            for c in contracts:
                blue.pyos.BeNice(50)
                canGetItems = False
                canGetMoney = False
                isOutbid = False
                if status == 0:
                    st = '<color=0xff885500>unknown'
                    if c.status == const.conStatusRejected:
                        st = '<color=0xff885500>' + mls.UI_CONTRACTS_REJECTED
                    elif c.type == const.conTypeAuction:
                        bids = _contracts.bids.get(c.contractID, [])
                        if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor, const.conStatusFinishedIssuer] and c.dateExpired < blue.os.GetTime():
                            if len(bids) > 0:
                                highBidder = bids[0].bidderID
                                if highBidder == eve.session.charid:
                                    st = '<color=green>' + mls.UI_CONTRACTS_YOUWON
                                    if forCorp:
                                        isOutbid = True
                                    elif c.status in [const.conStatusOutstanding, const.conStatusFinishedIssuer]:
                                        canGetItems = True
                                        st = '<color=green>' + mls.UI_CONTRACTS_YOUWONGETITEMS
                                elif highBidder == eve.session.corpid:
                                    st = '<color=green>' + mls.UI_CONTRACTS_YOURCORPWON
                                    if not forCorp:
                                        isOutbid = True
                                    elif c.status in [const.conStatusOutstanding, const.conStatusFinishedIssuer]:
                                        canGetItems = True
                                        st = '<color=green>' + mls.UI_CONTRACTS_YOURCORPWONGETITEMS
                                elif not forCorp and c.issuerID == eve.session.charid or forCorp and c.issuerCorpID == eve.session.corpid and c.forCorp:
                                    if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor]:
                                        st = '<color=white>' + mls.UI_CONTRACTS_FINISHEDGETMONEY
                                        canGetMoney = True
                                    else:
                                        st = '<color=white>' + mls.UI_CONTRACTS_AUCTIONFINISHED
                                st = '<color=red>' + mls.UI_CONTRACTS_AUCTIONFINISHED
                                isOutbid = True
                            else:
                                st = '<color=red>' + mls.UI_CONTRACTS_EXPIRED
                        elif c.dateExpired > blue.os.GetTime():
                            if len(bids) > 0:
                                for i in range(len(bids)):
                                    b = bids[i]
                                    if (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i != 0:
                                        st = '<color=red>' + mls.UI_CONTRACTS_YOUHAVEBEENOUTBID
                                        isOutbid = True
                                        break

                    elif c.status == const.conStatusOutstanding and c.dateExpired < blue.os.GetTime():
                        st = '<color=red>' + mls.UI_CONTRACTS_EXPIRED
                    elif c.status == const.conStatusInProgress and c.dateAccepted + DAY * c.numDays < blue.os.GetTime():
                        st = '<color=red>' + mls.UI_CONTRACTS_OVERDUE
                    elif c.status == const.conStatusInProgress:
                        col = 'white'
                        if c.dateAccepted + DAY * c.numDays < blue.os.GetTime() + 6 * HOUR:
                            col = '0xffdd5500'
                        st = '<color=%s>%s %s' % (col, util.FmtDate(c.dateAccepted + DAY * c.numDays - blue.os.GetTime(), 'ss'), mls.UI_GENERIC_REMAINING)
                    additionalColumns = '<t>%s' % st
                elif status == 3:
                    st = '<color=0xff885500>unknown'
                    bids = _contracts.bids.get(c.contractID, [])
                    if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor, const.conStatusFinishedIssuer] and c.dateExpired < blue.os.GetTime():
                        if len(bids) > 0:
                            highBidder = bids[0].bidderID
                            if highBidder == eve.session.charid:
                                st = '<color=green>' + mls.UI_CONTRACTS_YOUWON
                            elif highBidder == eve.session.corpid:
                                st = '<color=green>' + mls.UI_CONTRACTS_YOURCORPWON
                            st = '<color=white>' + mls.UI_CONTRACTS_AUCTIONFINISHED
                        else:
                            st = '<color=red>' + mls.UI_CONTRACTS_EXPIRED
                    elif c.dateExpired > blue.os.GetTime():
                        if len(bids) > 0:
                            for i in range(len(bids)):
                                b = bids[i]
                                if (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i == 0:
                                    if eve.session.charid == b.bidderID:
                                        st = '<color=green>' + mls.UI_CONTRACTS_YOUARETHEHIGHESTBIDDER
                                    elif eve.session.corpid == b.bidderID:
                                        st = '<color=green>' + mls.UI_CONTRACTS_YOURCORPISTHEHIGHESTBIDDER
                                    break
                                elif (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i != 0:
                                    st = '<color=red>' + mls.UI_CONTRACTS_YOUHAVEBEENOUTBID
                                    break

                    additionalColumns = '<t>%s' % st
                else:
                    additionalColumns = '<t>%s<t>%s<t>%s' % (GetColoredContractStatusText(c.status), util.FmtDate(c.dateAccepted, 'ss'), ConFmtDate(c.dateAccepted + DAY * c.numDays - blue.os.GetTime(), c.type == const.conTypeAuction))
                text = '.'
                canDismiss = False
                if status == 0 and c.type == const.conTypeAuction and isOutbid:
                    canDismiss = True
                data = {'contract': c,
                 'contractItems': _contracts.items.get(c.contractID, []),
                 'status': const.conStatusOutstanding,
                 'text': text,
                 'label': text,
                 'additionalColumns': additionalColumns,
                 'status': const.conStatusInProgress,
                 'callback': self.OnSelectContract,
                 'forCorp': forCorp,
                 'canDismiss': canDismiss,
                 'canGetMoney': canGetMoney,
                 'canGetItems': canGetItems,
                 'canIgnore': False,
                 'sort_%s' % mls.UI_CONTRACTS_CONTRACT: GetContractTitle(c, _contracts.items.get(c.contractID, []))}
                scrolllist.append(listentry.Get('ContractEntrySmall', data))

            wnd.sr.contractsListWnd.sr.id = 'contractsscroll'
            headers = [mls.UI_CONTRACTS_CONTRACT,
             mls.UI_GENERIC_TYPE,
             mls.UI_GENERIC_FROM,
             mls.UI_GENERIC_TO,
             mls.UI_GENERIC_STATUS]
            if status > 0 and status < 3:
                headers.extend([mls.UI_CONTRACTS_DATEISSUED, mls.UI_CONTRACTS_TIMELEFT])
            wnd.sr.contractsListWnd.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_CONTRACTS_NOCONTRACTSFOUND)
            self.statusCombo.SetValue(self.contractFilters.get('status', 0))
            self.ownerCombo.SetValue(self.contractFilters.get('forCorp', False))
            uix.Flush(self.contractsNotifyWnd)
            if numRequiresAttention > 0 or numCorpRequiresAttention > 0:
                icon = uicls.Icon(icon='ui_9_64_11', parent=self.contractsNotifyWnd, left=5, size=24, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED)
                pos = icon.left + icon.width + 2
                if numRequiresAttention > 0:
                    msg = ''
                    if numRequiresAttention == 1:
                        msg = mls.UI_CONTRACTS_ONECONTRACTREQUIRESYOURATTENTION
                    elif numRequiresAttention >= 100:
                        numRequiresAttention = 100
                        msg = mls.UI_CONTRACTS_ATLEAST
                    msg += mls.UI_CONTRACTS_CONTRACTSREQUIREYOURATTENTION_NUM % {'num': numRequiresAttention}
                    title = uicls.Label(text='<color=white>' + msg + '</color>', parent=self.contractsNotifyWnd, top=6, idx=0, left=pos, state=uiconst.UI_NORMAL)
                    title.forCorp = False
                    title.OnClick = self.ShowContracts
                    title.OnMouseEnter = (self.MouseEnterHighlightOn, title)
                    title.OnMouseExit = (self.MouseExitHighlightOff, title)
                    pos += title.width + 5
                if numCorpRequiresAttention > 0:
                    brk = {False: '',
                     True: ' - '}[(numRequiresAttention > 0)]
                    msg = ''
                    if numCorpRequiresAttention == 1:
                        msg = mls.UI_CONTRACTS_ONECORPCONTRACTREQUIRESYOURATTENTION
                    elif numCorpRequiresAttention >= 100:
                        numCorpRequiresAttention = 100
                        msg = mls.UI_CONTRACTS_ATLEAST
                    msg += mls.UI_CONTRACTS_CORPCONTRACTSREQUIREYOURATTENTION_NUM % {'num': numCorpRequiresAttention}
                    title = uicls.Label(text='<color=white>' + brk + msg + '</color>', parent=self.contractsNotifyWnd, top=6, idx=0, left=pos, state=uiconst.UI_NORMAL)
                    title.forCorp = True
                    title.OnClick = self.ShowContracts
                    title.OnMouseEnter = (self.MouseEnterHighlightOn, title)
                    title.OnMouseExit = (self.MouseExitHighlightOff, title)

        finally:
            if wnd is not None and not wnd.destroyed:
                self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_CONTRACTS_CONTRACTS))
                wnd.HideLoad()




    def OnComboChange(self, *args):
        pass



    def FetchContracts(self, *args):
        status = self.statusCombo.GetValue()
        forCorp = self.ownerCombo.GetValue() > 0
        self.contractFilters['status'] = status
        self.contractFilters['forCorp'] = forCorp
        self.DoShowContracts()



    def DelayedShowContracts(self):
        blue.pyos.synchro.Sleep(300)
        self.DoShowContracts()



    def OnSelectContract(self, entry, *args):
        pass



    def GetMyAgentJournalDetails(self):
        s = getattr(self, 'semaphore', None)
        if s is not None:
            s.acquire()
        try:
            if self.agentjournal is None:
                self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
            elif self.outdatedAgentJournals:
                parallelCalls = []
                tmp = self.outdatedAgentJournals
                for agentID in self.outdatedAgentJournals:
                    parallelCalls.append((sm.GetService('agents').GetAgentMoniker(agentID).GetMyJournalDetails, ()))

                self.outdatedAgentJournals = []
                parallelResults = uthread.parallel(parallelCalls)
                self.i = parallelResults
                if self.agentjournal is None:
                    self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
                else:
                    for agentID in tmp:
                        for mission in self.agentjournal[0]:
                            if mission[4] == agentID:
                                self.agentjournal[0].remove(mission)
                                break

                        for research in self.agentjournal[1]:
                            if research[0] == agentID:
                                self.agentjournal[1].remove(research)
                                break


                    for i in range(len(parallelResults)):
                        agentID = tmp[i]
                        for n in range(2):
                            self.agentjournal[n].extend(parallelResults[i][n])



        finally:
            if s is not None:
                s.release()

        return self.agentjournal



    def GetMyAgentJournalBookmarks(self):
        ret = []
        missions = self.GetMyAgentJournalDetails()[0]
        scrolllist = []
        if len(missions):
            i = 0
            for i in range(len(missions)):
                (missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable,) = missions[i]
                ret.append((missionName, bookmarks, agentID))

        return ret



    def GetMyLoyaltyPoints(self):
        if self.outdatedCorpLP == True:
            LPs = sm.RemoteSvc('LPSvc').GetLPsForCharacter()
            self.lpMapping = []
            for row in LPs:
                self.lpMapping.append((row[0], row[1]))

            self.outdatedCorpLP = False
        return self.lpMapping



    def GetMyEpicJournalData(self):
        if self.epicJournalData is None:
            self.epicJournalData = sm.RemoteSvc('agentMgr').GetMyEpicJournalDetails()
            self.epicJournalData.sort()
        return self.epicJournalData



    def GetEpicArcs(self):
        return [ (x[0], x[1]) for x in self.GetMyEpicJournalData() ]



    def GetEpicArcGraphic(self, epicArcIndex):
        return self.GetMyEpicJournalData()[epicArcIndex][2]



    def GetEpicArcMissions(self, epicArcIndex):
        return self.GetMyEpicJournalData()[epicArcIndex][3]



    def ShowCorpInfo(self):
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.entry.sr.node.corporationID).typeID, self.entry.sr.node.corporationID)



    def ShowConcordExchangeDialog(self):
        sm.GetService('lpstore').OpenConcordExchange(self.entry.sr.node.corporationID)



    def ShowCorpMenu(self, entry):
        self.entry = entry
        m = [(mls.UI_CMD_SHOWINFO, self.ShowCorpInfo)]
        lpSvc = sm.GetService('lpstore')
        xChangeRate = lpSvc.GetConcordLPExchangeRate(self.entry.sr.node.corporationID)
        concordLPs = lpSvc.GetMyConcordLPs()
        if eve.session.stationid is not None and xChangeRate is not None and xChangeRate > 0.0 and concordLPs > 0:
            m.append((mls.UI_LPSTORE_JOURNAL_LP_CONVERT_TO, self.ShowConcordExchangeDialog))
        return m



    def GetMissionIconDataForAgentTab(self, missionJournalDetails):
        (missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable,) = missionJournalDetails
        missionIconData = []
        chatBubbleIconID = 'ui_38_16_38'
        remoteMissionHints = []
        if remoteOfferable:
            remoteMissionHints.append(mls.AGT_STANDARDMISSION_ACCEPT_REMOTELY_HINT)
        if remoteCompletable:
            remoteMissionHints.append(mls.AGT_STANDARDMISSION_COMPLETE_REMOTELY_HINT)
        if remoteOfferable or remoteCompletable:
            remoteMissionHintText = '<br>'.join(remoteMissionHints)
            missionIconData.append((chatBubbleIconID, remoteMissionHintText))
        return missionIconData



    def ShowAgentTab(self, statusflag = -1):
        wnd = self.GetWnd()
        if wnd is None:
            return 
        self._SelectTab(wnd.sr.maintabs.sr.Get('%s_tab' % mls.UI_GENERIC_AGENTS))
        wnd.sr.agenttabs.state = uiconst.UI_NORMAL
        wnd.ShowLoad()
        if statusflag == 0:
            missions = self.GetMyAgentJournalDetails()[0]
            scrolllist = []
            if len(missions):
                missionIconData = []
                maxOptionalIcons = 0
                for i in xrange(len(missions)):
                    missionIconData.append(self.GetMissionIconDataForAgentTab(missions[i]))
                    maxOptionalIcons = max(maxOptionalIcons, len(missionIconData[i]))

                for i in xrange(len(missions)):
                    state = ''
                    (missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable,) = missions[i]
                    blankIconID = 'ui_38_16_39'
                    for j in xrange(maxOptionalIcons - len(missionIconData[i])):
                        missionIconData[i].insert(0, (blankIconID, ''))

                    missionStateLabel = {const.agentMissionStateAllocated: mls.UI_GENERIC_OFFERED,
                     const.agentMissionStateOffered: mls.UI_GENERIC_OFFERED,
                     const.agentMissionStateAccepted: mls.UI_GENERIC_ACCEPTED,
                     const.agentMissionStateFailed: mls.UI_GENERIC_FAILED}
                    missionLogInfo = '%s mission %d (%s) %s' % (missionStateLabel[missionState],
                     i,
                     missionName,
                     'expires in ' + util.FmtTimeInterval(expirationTime - blue.os.GetTime()) if expirationTime else 'does not expire')
                    self.LogInfo('Journal::ShowAgentTab:', missionLogInfo)
                    if importantMission:
                        missionType = '<color=0xFFFFFF00>%s ' % mls.UI_GENERIC_IMPORTANT + missionType + '<color=0xffffffff>'
                    if missionState in (const.agentMissionStateAllocated, const.agentMissionStateOffered):
                        state = '<color=0xFFFFFF00>%s<color=0xffffffff>' % mls.UI_GENERIC_OFFERED
                        agentName = sm.GetService('agents').GetAgentDisplayName(agentID)
                        if expirationTime > blue.os.GetTime() + WEEK + MIN:
                            expirationText = mls.UI_SHARED_THISOFFERSEXPIRESAT + ' ' + util.FmtDate(expirationTime, 'ln')
                            self.LogInfo('* Showing date only (expiration time is longer than ' + util.FmtTimeInterval(WEEK + MIN) + ')')
                        elif expirationTime > blue.os.GetTime() + DAY:
                            expirationText = mls.UI_SHARED_THISOFFERSEXPIRESAT + ' ' + util.FmtDate(expirationTime, 'ls')
                            self.LogInfo('* Showing hours/minutes (expiration time is between ' + util.FmtTimeInterval(DAY) + ' and ' + util.FmtTimeInterval(WEEK + MIN) + ')')
                        else:
                            self.LogInfo('* Showing other expiration message')
                            if expirationTime:
                                expirationTime -= blue.os.GetTime()
                                expirationTime = int(expirationTime / MIN) * MIN
                            if expirationTime == 0:
                                expirationText = mls.UI_SHARED_THISOFFERDOESNOTEXPIRE
                            elif not expirationTime:
                                expirationText = mls.UI_SHARED_THISOFFERSUNDEFINEDEXP
                            elif expirationTime > 0:
                                expirationText = mls.UI_SHARED_THISOFFERSEXPIRESIN + ' ' + util.FmtTimeInterval(expirationTime)
                            else:
                                expirationText = mls.UI_SHARED_THISOFFEREXPIRED
                                state = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_SHARED_OFFEREXPIRED
                        text = '%s<t>%s<t>%s<t>%s<t>%s' % (state,
                         agentName,
                         missionName,
                         missionType,
                         expirationText)
                    if missionState in (const.agentMissionStateAccepted, const.agentMissionStateFailed):
                        if missionState == const.agentMissionStateAccepted:
                            state = '<color=0xff00FF00>%s<color=0xffffffff>' % mls.UI_GENERIC_ACCEPTED
                        else:
                            state = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_GENERIC_FAILED
                        if expirationTime > blue.os.GetTime() + WEEK + MIN:
                            expirationText = mls.UI_SHARED_THISMISSIONEXPIRESAT + ' ' + util.FmtDate(expirationTime, 'ln')
                            self.LogInfo('* Showing date only (expiration time is longer than ' + util.FmtTimeInterval(WEEK + MIN) + ')')
                        elif expirationTime > blue.os.GetTime() + DAY:
                            expirationText = mls.UI_SHARED_THISMISSIONEXPIRESAT + ' ' + util.FmtDate(expirationTime, 'ls')
                            self.LogInfo('* Showing hours/minutes (expiration time is between ' + util.FmtTimeInterval(DAY) + ' and ' + util.FmtTimeInterval(WEEK + MIN) + ')')
                        else:
                            self.LogInfo('* Showing other expiration message')
                            if expirationTime:
                                expirationTime -= blue.os.GetTime()
                                expirationTime = int(expirationTime / MIN) * MIN
                            if expirationTime == 0:
                                expirationText = mls.UI_SHARED_THISMISSIONDOESNOTEXPIRE
                            elif not expirationTime:
                                expirationText = mls.UI_SHARED_THISMISSIONUNDEFINEDEXP
                            elif expirationTime > 0:
                                expirationText = mls.UI_SHARED_THISMISSIONEXPIRESIN + ' ' + util.FmtTimeInterval(expirationTime)
                            else:
                                expirationText = mls.UI_SHARED_THISMISSIONEXPIRED
                                state = '<color=0xffeb3700>%s<color=0xffffffff>' % mls.UI_SHARED_MISSIONEXPIRED
                        text = '%s<t>%s<t>%s<t>%s<t>%s' % (state,
                         sm.GetService('agents').GetAgentDisplayName(agentID),
                         missionName,
                         missionType,
                         expirationText)
                    scrolllist.append(listentry.Get('VirtualAgentMissionEntry', {'missionState': missionState,
                     'agentID': agentID,
                     'label': text,
                     'missionIconData': missionIconData[i]}))

            self._SelectTab(wnd.sr.agenttabs.sr.tabs[0])
            wnd.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_STATUS,
             mls.UI_GENERIC_AGENT,
             mls.UI_GENERIC_MISSION,
             mls.UI_GENERIC_TYPE,
             mls.UI_GENERIC_EXPIRES], noContentHint=mls.UI_SHARED_NOMISSIONOFFERD)
        elif statusflag == 1:
            research = self.GetMyAgentJournalDetails()[1]
            scrolllist = []
            if len(research):
                for i in xrange(len(research)):
                    (agentID, typeID, ppd, points, level, quality, stationID,) = research[i]
                    solarSystemID = sm.StartService('ui').GetStation(stationID).solarSystemID
                    text = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (sm.GetService('agents').GetAgentDisplayName(agentID),
                     cfg.invtypes.Get(typeID).name,
                     '%-2.2f' % points,
                     '%-2.2f' % ppd,
                     level,
                     cfg.evelocations.Get(stationID).name)
                    scrolllist.append(listentry.Get('VirtualResearchEntry', {'agentID': agentID,
                     'text': text,
                     'label': text,
                     'solarSystemID': solarSystemID}))

            self._SelectTab(wnd.sr.agenttabs.sr.tabs[1])
            wnd.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_AGENT,
             mls.UI_GENERIC_FIELD,
             mls.UI_GENERIC_CURRENTRP,
             mls.UI_GENERIC_RPDAY,
             mls.UI_GENERIC_LEVEL,
             mls.UI_GENERIC_LOCATION], noContentHint=mls.UI_SHARED_YOUARENTPERFORMINGANYRESEARCH)
        elif statusflag == 2:
            lps = self.GetMyLoyaltyPoints()
            scrolllist = []
            if len(lps):
                for i in xrange(len(lps)):
                    (corporationID, loyaltyPoints,) = lps[i]
                    label = '%s<t>%s' % (cfg.eveowners.Get(corporationID).name, loyaltyPoints)
                    data = util.KeyVal()
                    data.GetMenu = self.ShowCorpMenu
                    data.label = label
                    data.hilite = None
                    data.hint = ''
                    data.selection = None
                    data.corporationID = corporationID
                    scrolllist.append(listentry.Get('Generic', data=data))

            wnd.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_CORPORATION, mls.UI_LPSTORE_LPS], noContentHint=mls.UI_LPSTORE_NOLPS)
            self._SelectTab(wnd.sr.agenttabs.sr.tabs[2])
        wnd.HideLoad()




class EscalatingPathLocationEntry(listentry.Generic):
    __guid__ = 'listentry.EscalatingPathLocationEntry'

    def init(self):
        self.sr.selection = None
        self.sr.hilite = None
        self.OnSelectCallback = None



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = node.label
        self.OnSelectCallback = node.Get('callback', None)
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.Get('selected', 0)]
        self.state = uiconst.UI_NORMAL



    def OpenDetails(self):
        sm.GetService('journal').PopupDungeonDescription(self.sr.node)



    def OnDblClick(self, *args):
        self.OpenDetails()



    def GetMenu(self):
        node = self.sr.node
        m = []
        expired = [True, False][(node.rec.expiryTime - blue.os.GetTime() > 0)]
        if not expired:
            if node.rec.dungeon.solarSystemID is not None:
                m += sm.GetService('menu').CelestialMenu(node.rec.dungeon.solarSystemID)
                m.append(None)
                m.append((mls.UI_CMD_OPENDESCRIPTION, self.OpenDetails))
            if node.rec.dungeon.solarSystemID == eve.session.solarsystemid:
                journal = sm.GetService('journal')
                if node.rec.instanceID in journal.pathPlexPositionByInstanceID:
                    journal.LogInfo('Using cached path instance position')
                    resp = journal.pathPlexPositionByInstanceID[node.rec.instanceID]
                else:
                    resp = sm.RemoteSvc('keeper').CanWarpToPathPlex(node.rec.instanceID)
                if resp:
                    if resp is True:
                        m.append((mls.UI_CMD_WARPTOLOCATION, self.WarpToHiddenDungeon, (node.id, node)))
                    else:
                        mickey = sm.StartService('michelle')
                        me = mickey.GetBall(eve.session.shipid)
                        dist = (foo.Vector3(resp) - foo.Vector3(me.x, me.y, me.z)).Length()
                        if dist < const.minWarpDistance:
                            journal.pathPlexPositionByInstanceID[node.rec.instanceID] = resp
                            m.append((mls.UI_CMD_APPROACHLOCATION, self.Approach, list(resp)))
                        else:
                            m.append((mls.UI_CMD_WARPTOLOCATION, self.WarpToHiddenDungeon, (node.id, node)))
        else:
            m.append(None)
            m.append((mls.UI_CMD_REMOVE, self.DeleteExpeditionEntry, (node.id, node)))
        return m



    def Approach(self, x, y, z):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.GotoDirection(x, y, z)



    def DeleteExpeditionEntry(self, instanceID, *args):
        rm = []
        for entry in self.sr.node.scroll.GetNodes():
            if entry.id == instanceID:
                rm.append(entry)

        if rm:
            self.sr.node.scroll.RemoveEntries(rm)
        uthread.new(sm.RemoteSvc('dungeonExplorationMgr').DeleteExpiredPathStep, instanceID)
        uthread.new(sm.GetService('journal').GetExpeditions, force=1)



    def WarpToHiddenDungeon(self, instanceID, node, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('epinstance', instanceID)




class PlanetaryInteractionLaunchEntry(listentry.Generic):
    __guid__ = 'listentry.PlanetaryInteractionLaunchEntry'

    def init(self):
        self.sr.selection = None
        self.sr.hilite = None
        self.OnSelectCallback = None



    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.node = node
        self.sr.label.text = node.label
        self.OnSelectCallback = node.Get('callback', None)
        self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.Get('selected', 0)]
        self.state = uiconst.UI_NORMAL



    def GetMenu(self):
        node = self.sr.node
        m = []
        if not node.expired:
            if node.rec.solarSystemID is not None:
                m += sm.GetService('menu').CelestialMenu(node.rec.solarSystemID, filterFunc=[mls.UI_CMD_BOOKMARKLOCATION])
                m.append(None)
            if node.rec.solarSystemID == eve.session.solarsystemid:
                journal = sm.GetService('journal')
                mickey = sm.StartService('michelle')
                me = mickey.GetBall(eve.session.shipid)
                dirTo = foo.Vector3(node.rec.x, node.rec.y, node.rec.z) - foo.Vector3(me.x, me.y, me.z)
                dist = dirTo.Length()
                if dist < const.minWarpDistance:
                    m.append((mls.UI_CMD_APPROACHLOCATION, self.Approach, list((node.rec.itemID, node))))
                else:
                    m.append((mls.UI_CMD_WARPTOLOCATION, self.WarpToLaunchPickup, (node.rec.launchID, node)))
        else:
            m.append(None)
            m.append((mls.UI_CMD_REMOVE, self.DeleteLaunchEntry, (node.rec.launchID, node)))
        return m



    def Approach(self, launchID, node):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.FollowBall(launchID, 50)



    def WarpToLaunchPickup(self, launchID, node, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('launch', launchID)



    def DeleteLaunchEntry(self, launchID, *args):
        rm = []
        for entry in self.sr.node.scroll.GetNodes():
            if entry.id == launchID:
                rm.append(entry)

        if rm:
            self.sr.node.scroll.RemoveEntries(rm)
        uthread.new(sm.RemoteSvc('planetMgr').DeleteLaunch, launchID)
        uthread.new(sm.GetService('journal').GetLaunches, force=1)




class JournalWindow(uicls.Window):
    __guid__ = 'form.Journal'
    default_width = 525
    default_height = 300
    default_minSize = (465, 300)


