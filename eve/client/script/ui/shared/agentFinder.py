import blue
import listentry
import math
import standingUtil
import types
import uicls
import uiconst
import uthread
import uiutil
import uix
import util
from collections import defaultdict
AGENT_LINES = 3
AGENT_COLUMNS = 2
NUM_AGENTS = 6
BIG_WIDTH = 580
SMALL_WIDTH = 400
HEIGHT = 420
SEARCH_WIDTH = 180
LINE_COLOR = (1.0, 1.0, 1.0, 0.5)
ADJUSTER_WIDTH = 16
SLIDER_PADDING = 20
SLIDER_COLUMNS = 4
HOVER_ALPHA = 1.0
NORMAL_ALPHA = 0.8
FACTIONIDBYRACEID = {const.raceCaldari: const.factionCaldariState,
 const.raceMinmatar: const.factionMinmatarRepublic,
 const.raceAmarr: const.factionAmarrEmpire,
 const.raceGallente: const.factionGallenteFederation}

class AgentFinderWnd(uicls.Window):
    __guid__ = 'form.AgentFinderWnd'
    __notifyevents__ = ['OnSessionChanged']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.SetCaption(mls.UI_SHARED_AGENTFINDER)
        self.SetMinSize([SMALL_WIDTH, HEIGHT])
        self.SetTopparentHeight(0)
        self.agentsList = []
        self.pos = 0
        self.numPages = 0
        self.totalAgents = 0
        self.agentLevel = 0
        self.med = 0
        self.agents = []
        self.factionIDs = set()
        self.corporationIDs = set()
        self.corpIDsByFactionID = defaultdict(set)
        self.divisionIDs = set()
        self.regionIDs = set()
        self.solarsystemIDs = set()
        self.systemIDsByRegionID = defaultdict(set)
        self.stationIDs = set()
        self.agentTypeIDs = set()
        self.standings = {}
        self.corpStandings = {}
        self.bestFactionStanding = 0
        self.bestCorpStanding = 0
        self.mapSvc = sm.GetService('map')
        self.standingSvc = sm.GetService('standing')
        self.factionID = None
        self.corporationID = None
        self.agentType = None
        self.regionID = None
        self.solarSystemID = None
        self.secStatus = None
        self.ConstructLayout()



    def ConstructLayout(self):
        self.leftCont = uicls.Container(name='leftCont', parent=self.sr.main, align=uiconst.TOLEFT, width=SEARCH_WIDTH, clipChildren=True)
        self.rightCont = uicls.Container(name='rightCont', parent=self.sr.main, align=uiconst.TOALL)
        topCont = uicls.Container(name='topCont', parent=self.rightCont, align=uiconst.TOTOP, height=90)
        uicls.Label(text=mls.UI_SHARED_AGENTLEVEL, parent=topCont, align=uiconst.CENTERTOP, top=4, uppercase=True)
        self.sliderCont = uicls.Container(name='sliderCont', parent=topCont, align=uiconst.TOTOP, pos=(0, 28, 0, 20), padding=(SLIDER_PADDING,
         0,
         SLIDER_PADDING,
         0))
        self.sliderAdjusterCont = uicls.Container(name='sliderAdjusterCont', parent=topCont, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         ADJUSTER_WIDTH), padding=(SLIDER_PADDING,
         0,
         SLIDER_PADDING,
         0))
        browseCont = uicls.Container(name='browseCont', parent=self.rightCont, align=uiconst.TOBOTTOM, height=22, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0), state=uiconst.UI_NORMAL)
        self.prevBtn = uicls.BrowseButton(parent=browseCont, prev=True, state=uiconst.UI_NORMAL, func=self.BrowseAgents)
        self.nextBtn = uicls.BrowseButton(parent=browseCont, prev=False, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, func=self.BrowseAgents)
        self.pageNumText = uicls.Label(text='', parent=browseCont, align=uiconst.CENTERTOP, state=uiconst.UI_HIDDEN)
        self.noAgentsCont = uicls.Container(name='noAgentsCont', parent=self.rightCont, align=uiconst.TOALL, padding=(const.defaultPadding * 3,
         const.defaultPadding,
         const.defaultPadding * 3,
         const.defaultPadding), state=uiconst.UI_HIDDEN)
        self.noAgentsOrLoadingText = uicls.CaptionLabel(text='', parent=self.noAgentsCont)
        self.mainCont = uicls.GridContainer(name='mainCont', parent=self.rightCont, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.mainCont.lines = AGENT_LINES
        self.mainCont.columns = AGENT_COLUMNS
        self.expanderCont = uicls.Container(parent=topCont, align=uiconst.BOTTOMLEFT, height=16, width=60, top=8, state=uiconst.UI_NORMAL, left=6)
        self.expanderIcon = uicls.Icon(parent=self.expanderCont, idx=0, size=16, state=uiconst.UI_DISABLED, icon='ui_1_16_100')
        l = uicls.Label(text=mls.UI_SHARED_FILTEROPTIONS, parent=self.expanderCont, left=16)
        self.expanderCont.SetOpacity(NORMAL_ALPHA)
        self.expanderCont.width = l.width + 16
        self.expanderCont.OnClick = self.OnChangeSize
        self.expanderCont.OnMouseEnter = (self.OnContMouseEnter, self.expanderCont)
        self.expanderCont.OnMouseExit = (self.OnContMouseExit, self.expanderCont)
        self.GetStandings()
        self.GetAllAgentInfo()
        self.ConstructSearchUI()
        self.agentLevel = settings.user.ui.Get('agentFinderLevel', self.bestCorpStanding)
        self.ConstructSlider()
        expanded = settings.user.ui.Get('agentFinderExpanded', None)
        if expanded is None:
            settings.user.ui.Set('agentFinderExpanded', False)
        if expanded:
            self.ExpandSearch()
        else:
            self.CollapseSearch()
        self.GetAgents()



    def GetStandings(self):
        self.standings = sm.RemoteSvc('standing2').GetCharStandings()
        self.corpStandings = sm.RemoteSvc('standing2').GetCorpStandings()
        if type(self.standings) != types.DictType:
            self.standings = self.standings.Index('fromID')
        if type(self.corpStandings) != types.DictType:
            self.corpStandings = self.corpStandings.Index('fromID')



    def ConstructSearchUI(self):
        self.corporationID = settings.user.ui.Get('agentFinderCorporation', -1)
        self.divisionID = settings.user.ui.Get('agentFinderDivision', -1)
        self.locationID = settings.user.ui.Get('agentFinderLocation', -1)
        self.regionID = settings.user.ui.Get('agentFinderRegion', -1)
        self.secStatus = settings.user.ui.Get('agentFinderSecStatus', -1)
        showAvail = settings.user.ui.Get('agentFinderAvailable', True)
        bottomCont = uicls.Container(parent=self.leftCont, align=uiconst.TOBOTTOM, height=30, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        topCont = uicls.Container(parent=self.leftCont, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        combos = []
        top = 16
        factionOptions = self.GetFactions()
        self.factionID = settings.user.ui.Get('agentFinderFaction', self.bestFactionStanding)
        self.factionCombo = uicls.Combo(label=mls.UI_GENERIC_FACTION, parent=topCont, select=self.factionID, top=top, left=8, options=factionOptions, callback=self.OnFactionChange, adjustWidth=True)
        combos.append(self.factionCombo)
        top += 48
        self.corpCombo = uicls.Combo(label=mls.UI_GENERIC_CORPORATION, parent=topCont, select=self.corporationID, top=top, left=8, options=self.GetCorporations(), callback=self.OnCorporationChange, adjustWidth=True)
        combos.append(self.corpCombo)
        top += 48
        self.divisionCombo = uicls.Combo(label=mls.UI_SHARED_AGENTTYPE, parent=topCont, select=self.divisionID, top=top, left=8, options=self.GetDivisions(), callback=self.OnDivisionChange, adjustWidth=True)
        combos.append(self.divisionCombo)
        top += 48
        self.regionCombo = uicls.Combo(label=mls.UI_GENERIC_REGION, parent=topCont, select=self.regionID, top=top, left=8, options=self.GetRegions(), callback=self.OnRegionChange, adjustWidth=True)
        combos.append(self.regionCombo)
        top += 48
        self.locationCombo = uicls.Combo(label=mls.UI_GENERIC_SOLARSYSTEM, parent=topCont, select=self.locationID, top=top, left=8, options=self.GetSolarsystems(), callback=self.OnLocationChange, adjustWidth=True)
        combos.append(self.locationCombo)
        top += 48
        self.secStatusCombo = uicls.Combo(label=mls.UI_GENERIC_SECURITYSTATUS, parent=topCont, select=self.secStatus, top=top, left=8, options=self.GetSecurityStatus(), callback=self.OnSecStatusChange, adjustWidth=True)
        combos.append(self.secStatusCombo)
        top += 32
        self.showOnlyAvail = uicls.Checkbox(text=mls.UI_MARKET_SHOWONLYAVAIL, parent=topCont, checked=showAvail, top=top, callback=self.OnShowAvailChange, left=6, align=uiconst.TOPLEFT, width=SEARCH_WIDTH - 30)
        comboWidth = max(self.factionCombo.width, self.corpCombo.width, self.divisionCombo, self.locationCombo, self.secStatusCombo)
        maxWidth = min(comboWidth, SEARCH_WIDTH - 30)
        for combo in combos:
            combo.adjustWidth = False
            combo.width = maxWidth




    def ConstructSlider(self):
        sliderTextCont = uicls.GridContainer(name='mainCont', parent=self.sliderCont, align=uiconst.TOTOP, height=16)
        sliderTextCont.lines = 1
        sliderTextCont.columns = SLIDER_COLUMNS * 2
        sliderCont = uicls.GridContainer(name='mainCont', parent=self.sliderCont, align=uiconst.TOALL)
        sliderCont.lines = 1
        sliderCont.columns = SLIDER_COLUMNS
        for i in xrange(1, SLIDER_COLUMNS + 1):
            textcontLeft = uicls.Container(parent=sliderTextCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
            textcontLeft.OnClick = (self.OnLevelClick, i)
            textcontRight = uicls.Container(parent=sliderTextCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
            textcontRight.OnClick = (self.OnLevelClick, i + 1)
            cont = uicls.Container(parent=sliderCont, align=uiconst.TOALL)
            label = uicls.Label(text='', parent=textcontRight, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, left=-6, fontsize=18, top=-4)
            label.SetAlpha(NORMAL_ALPHA)
            label.OnClick = (self.OnLevelClick, i + 1)
            label.GetMenu = []
            label.OnMouseExit = (self.OnAdjusterMouseExit, label)
            label.OnMouseEnter = (self.OnAdjusterMouseEnter, label)
            labelName = 'level%d' % i
            setattr(self.sr, labelName, label)
            uicls.Line(name='scaleBase', parent=cont, align=uiconst.TOBOTTOM, color=LINE_COLOR)
            if i == 1:
                firstLabel = uicls.Label(text=i, parent=textcontLeft, left=-4, state=uiconst.UI_NORMAL, fontsize=18, top=-4)
                labelName = 'label%s' % i
                setattr(self, labelName, firstLabel)
                firstLabel.SetAlpha(NORMAL_ALPHA)
                firstLabel.GetMenu = []
                firstLabel.OnClick = (self.OnLevelClick, i)
                firstLabel.OnMouseExit = (self.OnAdjusterMouseExit, firstLabel)
                firstLabel.OnMouseEnter = (self.OnAdjusterMouseEnter, firstLabel)
                textcontLeft.OnMouseEnter = (self.OnAdjusterMouseEnter, firstLabel)
                textcontLeft.OnMouseExit = (self.OnAdjusterMouseExit, firstLabel)
                uicls.Line(name='leftTick', parent=cont, align=uiconst.TOLEFT, color=LINE_COLOR)
            else:
                prevLabel = self.sr.Get('level%d' % (i - 1))
                textcontLeft.OnMouseEnter = (self.OnAdjusterMouseEnter, prevLabel)
                textcontLeft.OnMouseExit = (self.OnAdjusterMouseExit, prevLabel)
            textcontRight.OnMouseEnter = (self.OnAdjusterMouseEnter, label)
            textcontRight.OnMouseExit = (self.OnAdjusterMouseExit, label)
            label.text = i + 1
            uicls.Line(name='rightTick', parent=cont, align=uiconst.TORIGHT, color=LINE_COLOR)

        self.leftSpacer = uicls.Container(parent=self.sliderAdjusterCont, name='leftSpacer', align=uiconst.TOLEFT, pos=(-ADJUSTER_WIDTH / 2,
         0,
         ADJUSTER_WIDTH,
         ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        adjuster = uicls.Icon(name='adjuster', icon='38_230', parent=self.leftSpacer, align=uiconst.TORIGHT, pos=(0,
         0,
         ADJUSTER_WIDTH,
         ADJUSTER_WIDTH), state=uiconst.UI_NORMAL, color=LINE_COLOR)
        adjuster.OnMouseDown = self.OnAdjustMouseDown
        adjuster.OnMouseUp = self.OnAdjustMouseUp
        adjuster.OnMouseMove = self.OnAdjustMouseMove
        adjuster.OnMouseEnter = (self.OnAdjusterMouseEnter, adjuster)
        adjuster.OnMouseExit = (self.OnAdjusterMouseExit, adjuster)
        self.adjuster = adjuster
        self.UpdateAdjuster()



    def OnLevelClick(self, level, *args):
        if self.agentLevel == level:
            return 
        self.agentLevel = level
        self.UpdateAdjuster(animate=True)



    def OnAdjusterMouseEnter(self, item, *args):
        item.color.SetAlpha(HOVER_ALPHA)



    def OnAdjusterMouseExit(self, item, *args):
        item.color.SetAlpha(NORMAL_ALPHA)



    def OnAdjustMouseDown(self, button):
        if button == uiconst.MOUSELEFT:
            self.adjuster.dragging = True



    def OnAdjustMouseUp(self, button):
        if button == uiconst.MOUSELEFT:
            self.adjuster.dragging = False
            self.UpdateAdjuster(animate=True)



    def OnAdjustMouseMove(self, *args):
        if getattr(self.adjuster, 'dragging', False) and uicore.uilib.leftbtn:
            width = self.leftSpacer.width
            dx = uicore.uilib.dx
            (w, h,) = self.sliderCont.GetAbsoluteSize()
            width += dx
            if width < ADJUSTER_WIDTH:
                width = ADJUSTER_WIDTH
            elif width > w + ADJUSTER_WIDTH:
                width = w + ADJUSTER_WIDTH
            self.med = w / SLIDER_COLUMNS
            frac = width - ADJUSTER_WIDTH
            self.agentLevel = round(float(frac) / float(self.med)) + 1
            self.leftSpacer.width = width



    def ShowLoading(self):
        self.noAgentsCont.state = uiconst.UI_DISABLED
        self.mainCont.state = uiconst.UI_HIDDEN
        self.prevBtn.Disable()
        self.nextBtn.Disable()
        self.noAgentsOrLoadingText.text = '%s...' % mls.UI_GENERIC_LOADING



    def HideLoading(self):
        self.noAgentsCont.state = uiconst.UI_HIDDEN
        self.mainCont.state = uiconst.UI_PICKCHILDREN



    def GetAgents(self, *args):
        uthread.new(self.GetAgents_thread)



    def GetAgents_thread(self):
        self.ShowLoading()
        self.agentsList = []
        factionID = self.factionCombo.GetValue()
        corporationID = self.corpCombo.GetValue()
        divisionID = self.divisionCombo.GetValue()
        regionID = self.regionCombo.GetValue()
        solarsystemID = self.locationCombo.GetValue()
        securityStatus = self.secStatusCombo.GetValue()
        showOnlyAvail = self.showOnlyAvail.checked
        agentLevel = self.agentLevel
        for agent in self.agents:
            blue.pyos.BeNice()
            if agent.level != agentLevel:
                continue
            if factionID != -1 and agent.factionID != factionID:
                continue
            if corporationID != -1 and agent.corporationID != corporationID:
                continue
            if divisionID != -1:
                if divisionID == const.agentTypeStorylineMissionAgent:
                    if agent.agentTypeID not in (const.agentTypeStorylineMissionAgent, const.agentTypeGenericStorylineMissionAgent):
                        continue
                elif divisionID == const.agentTypeFactionalWarfareAgent:
                    if agent.agentTypeID != const.agentTypeFactionalWarfareAgent:
                        continue
                elif agent.divisionID != divisionID or agent.agentTypeID in (const.agentTypeFactionalWarfareAgent, const.agentTypeStorylineMissionAgent, const.agentTypeGenericStorylineMissionAgent):
                    continue
            if agent.solarsystemID is None:
                agentSolarSystemID = sm.GetService('agents').GetSolarSystemOfAgent(agent.agentID)
            else:
                agentSolarSystemID = agent.solarsystemID
            if agentSolarSystemID is None:
                continue
            else:
                agentRegionID = self.mapSvc.GetRegionForSolarSystem(agentSolarSystemID)
                if regionID != -1 and agentRegionID != regionID:
                    continue
            if solarsystemID != -1 and agentSolarSystemID != solarsystemID:
                continue
            sec = self.mapSvc.GetSecurityStatus(agentSolarSystemID)
            secStatus = util.FmtSystemSecStatus(sec)
            secClass = util.SecurityClassFromLevel(secStatus)
            if securityStatus != -1 and secClass != securityStatus:
                continue
            if showOnlyAvail:
                if not session.warfactionid and agent.agentTypeID == const.agentTypeFactionalWarfareAgent:
                    continue
                if agent.level != 1 or agent.agentTypeID == const.agentTypeResearchAgent:
                    if not self.standingSvc.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID):
                        continue
            agentKV = util.KeyVal()
            agentKV.agentID = agent.agentID
            agentKV.agentTypeID = agent.agentTypeID
            agentKV.divisionID = agent.divisionID
            agentKV.level = agent.level
            agentKV.stationID = agent.stationID
            agentKV.corporationID = agent.corporationID
            agentKV.factionID = agent.factionID
            agentKV.solarsystemID = agentSolarSystemID
            jumps = 999
            if agentSolarSystemID:
                jumps = len(sm.GetService('starmap').ShortestGeneralPath(agentSolarSystemID)) - 1
                if jumps == -1:
                    jumps = 999
            agentKV.jumps = jumps
            self.agentsList.append(agentKV)

        self.agentsList.sort(key=lambda x: x.jumps)
        self.totalAgents = len(self.agentsList)
        self.pos = 0
        if self.totalAgents == 0:
            self.noAgentsOrLoadingText.text = mls.UI_SHARED_NOAGENTSFOUND
            self.DisplayBrowse()
        else:
            self.HideLoading()
            self.DrawAgents()



    def GetAllAgentInfo(self):
        agentsByID = sm.GetService('agents').GetAgentsByID()
        for agentID in agentsByID:
            agent = agentsByID[agentID]
            if agent.agentTypeID not in (const.agentTypeEventMissionAgent, const.agentTypeAura):
                self.agents.append(agent)
                self.agentTypeIDs.add(agent.agentTypeID)
                self.factionIDs.add(agent.factionID)
                self.corporationIDs.add(agent.corporationID)
                self.corpIDsByFactionID[agent.factionID].add(agent.corporationID)
                self.divisionIDs.add(agent.divisionID)
                if agent.solarsystemID:
                    agentSolarSystemID = agent.solarsystemID
                else:
                    agentSolarSystemID = sm.GetService('agents').GetSolarSystemOfAgent(agent.agentID)
                if agentSolarSystemID:
                    self.solarsystemIDs.add(agentSolarSystemID)
                    regionID = self.mapSvc.GetRegionForSolarSystem(agentSolarSystemID)
                    self.regionIDs.add(regionID)
                    self.systemIDsByRegionID[regionID].add(agentSolarSystemID)
                self.stationIDs.add(agent.stationID)




    def OnFactionChange(self, *args):
        if self.factionID == self.factionCombo.GetValue():
            return 
        self.factionID = self.factionCombo.GetValue()
        settings.user.ui.Set('agentFinderFaction', self.factionID)
        self.corpCombo.LoadOptions(self.GetCorporations())
        self.GetAgents()



    def OnCorporationChange(self, *args):
        if self.corporationID == self.corpCombo.GetValue():
            return 
        self.corporationID = self.corpCombo.GetValue()
        settings.user.ui.Set('agentFinderCorporation', self.corporationID)
        self.GetAgents()



    def OnDivisionChange(self, *args):
        if self.divisionID == self.divisionCombo.GetValue():
            return 
        self.divisionID = self.divisionCombo.GetValue()
        settings.user.ui.Set('agentFinderDivision', self.divisionID)
        self.GetAgents()



    def OnRegionChange(self, *args):
        if self.regionID == self.regionCombo.GetValue():
            return 
        self.regionID = self.regionCombo.GetValue()
        settings.user.ui.Set('agentFinderRegion', self.regionID)
        self.locationCombo.LoadOptions(self.GetSolarsystems())
        self.GetAgents()



    def OnLocationChange(self, *args):
        if self.locationID == self.locationCombo.GetValue():
            return 
        self.locationID = self.locationCombo.GetValue()
        settings.user.ui.Set('agentFinderLocation', self.locationID)
        self.GetAgents()



    def OnSecStatusChange(self, *args):
        if self.secStatus == self.secStatusCombo.GetValue():
            return 
        self.secStatus = self.secStatusCombo.GetValue()
        settings.user.ui.Set('agentFinderSecStatus', self.secStatus)
        self.GetAgents()



    def OnShowAvailChange(self, *args):
        settings.user.ui.Set('agentFinderAvailable', self.showOnlyAvail.checked)
        self.GetAgents()



    def GetFactions(self):
        factionStandingList = []
        options = []
        isNoob = True
        for factionID in self.factionIDs:
            if factionID:
                options.append([cfg.eveowners.Get(factionID).name, factionID])
                standing = self.standingSvc.GetStanding(factionID, session.charid)
                factionStanding = util.KeyVal()
                factionStanding.factionID = factionID
                factionStanding.standing = standing
                if standing != 0:
                    isNoob = False
                factionStandingList.append(factionStanding)

        if isNoob:
            factionID = FACTIONIDBYRACEID[session.raceID]
            self.bestFactionStanding = factionID
        else:
            factionStandingList.sort(key=lambda x: x.standing)
            self.bestFactionStanding = factionStandingList[-1].factionID
        options.sort()
        options.insert(0, [mls.UI_GENERIC_ANY, -1])
        return options



    def GetCorporations(self):
        corpStandingList = []
        options = []
        factionID = self.factionCombo.GetValue()
        if factionID == -1:
            corps = self.corporationIDs
        else:
            corps = self.corpIDsByFactionID[factionID]
        for corporationID in corps:
            if corporationID:
                options.append([cfg.eveowners.Get(corporationID).name, corporationID])
                options.sort()
                standing = self.standingSvc.GetStanding(corporationID, session.charid)
                corpStanding = util.KeyVal()
                corpStanding.corporationID = corporationID
                corpStanding.standing = standing
                corpStandingList.append(corpStanding)

        corpStandingList.sort(key=lambda x: x.standing)
        self.bestCorpStanding = corpStandingList[-1].standing
        self.bestCorpStanding = int((self.bestCorpStanding + 1) / 2 + 1)
        if self.bestCorpStanding <= 1:
            self.bestCorpStanding = max(self.bestCorpStanding, 1)
        else:
            self.bestCorpStanding = min(self.bestCorpStanding, 5)
        options.insert(0, [mls.UI_GENERIC_ANY, -1])
        return options



    def GetDivisions(self):
        options = []
        for divisionID in self.divisionIDs:
            if divisionID:
                divisionName = sm.GetService('agents').GetDivisions()[divisionID].divisionName.replace('&', '&amp;')
                options.append([divisionName, divisionID])

        for agentTypeID in self.agentTypeIDs:
            if agentTypeID == const.agentTypeStorylineMissionAgent:
                options.append([mls.UI_SHARED_STORYLINE, agentTypeID])
            elif agentTypeID == const.agentTypeFactionalWarfareAgent:
                options.append([mls.UI_FACWAR_FACTIONALWARFARE, agentTypeID])

        options.sort()
        options.insert(0, [mls.UI_GENERIC_ANY, -1])
        return options



    def GetRegions(self):
        options = []
        for regionID in self.regionIDs:
            if regionID:
                options.append([cfg.evelocations.Get(regionID).name, regionID])

        options.sort()
        options.insert(0, [mls.UI_GENERIC_ANY, -1])
        return options



    def GetSolarsystems(self):
        options = []
        regionID = self.regionCombo.GetValue()
        if regionID == -1:
            solarsystems = self.solarsystemIDs
        else:
            solarsystems = self.systemIDsByRegionID[regionID]
        for solarsystemID in solarsystems:
            if solarsystemID:
                options.append([cfg.evelocations.Get(solarsystemID).name, solarsystemID])

        options.sort()
        options.insert(0, [mls.UI_GENERIC_ANY, -1])
        return options



    def GetSecurityStatus(self):
        options = [(mls.UI_GENERIC_ANY, -1),
         (mls.UI_GENERIC_HIGHSEC, const.securityClassHighSec),
         (mls.UI_GENERIC_LOWSEC, const.securityClassLowSec),
         (mls.UI_GENERIC_NULLSEC, const.securityClassZeroSec)]
        return options



    def DrawAgents(self):
        self.numPages = int(math.ceil(self.totalAgents / float(NUM_AGENTS)))
        self.mainCont.Flush()
        for i in xrange(AGENT_LINES * AGENT_COLUMNS):
            agentCont = uicls.Container(parent=self.mainCont, align=uiconst.TOALL, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), state=uiconst.UI_NORMAL)
            self.AddAgentInfo(agentCont, i)

        self.DisplayBrowse()



    def AddAgentInfo(self, agentCont, i):
        if i + self.pos >= self.totalAgents:
            return 
        agent = self.agentsList[(i + self.pos)]
        agentID = agent.agentID
        divisionID = agent.divisionID
        agentTypeID = agent.agentTypeID
        factionID = agent.factionID
        corporationID = agent.corporationID
        stationID = agent.stationID
        solarSystemID = agent.solarsystemID
        agentLevel = agent.level
        jumps = agent.jumps
        if self.showOnlyAvail.checked:
            isAvailable = True
        elif agent.level == 1 and agent.agentTypeID != const.agentTypeResearchAgent:
            if not session.warfactionid and agent.agentTypeID == const.agentTypeFactionalWarfareAgent:
                isAvailable = False
            else:
                isAvailable = True
        else:
            isAvailable = self.standingSvc.CanUseAgent(factionID, corporationID, agentID, agentLevel, agentTypeID)
        nameLabel = cfg.eveowners.Get(agentID).name
        corpLabel = ''
        if corporationID:
            corpLabel = cfg.eveowners.Get(corporationID).name
        locationLabel = ''
        solarSystemName = cfg.evelocations.Get(solarSystemID).name
        if stationID:
            station = sm.StartService('ui').GetStation(stationID)
            stationName = cfg.evelocations.Get(stationID).name
            stationTypeID = station.stationTypeID
            locationLink = '<url=showinfo:%d//%d>%s</url>' % (stationTypeID, stationID, solarSystemName)
        else:
            locationLink = '<url=showinfo:%d//%d>%s</url>' % (const.typeSolarSystem, solarSystemID, solarSystemName)
        sec = sm.GetService('map').GetSecurityStatus(solarSystemID)
        (secStatus, color,) = util.FmtSystemSecStatus(sec, True)
        color = util.Color.RGBtoHex(color.r, color.g, color.b)
        secStatus = '<color=%s>%s</color>' % (color, secStatus)
        if jumps != 999:
            if jumps == 1:
                numJumpsTxt = '%s %s' % (jumps, mls.UI_GENERIC_JUMP)
            else:
                numJumpsTxt = '%s %s' % (jumps, mls.UI_GENERIC_JUMPS)
        else:
            numJumpsTxt = mls.UI_GENERIC_UNREACHABLE
        locationLabel = '%s %s (%s)' % (locationLink, secStatus, numJumpsTxt)
        levelAndTypeLabel = ''
        if agentID in sm.GetService('agents').GetTutorialAgentIDs():
            levelAndTypeLabel = mls.CHAR_TUTORIAL_AGENT
        elif agentTypeID == const.agentTypeEpicArcAgent:
            levelAndTypeLabel = mls.CHAR_EPICARC_AGENT
        elif agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
            levelAndTypeLabel = '%s %s' % (mls.UI_GENERIC_LEVEL, uiutil.GetLevel(agentLevel))
        else:
            t = {const.agentTypeGenericStorylineMissionAgent: mls.UI_SHARED_STORYLINE,
             const.agentTypeStorylineMissionAgent: mls.UI_SHARED_STORYLINE}.get(agentTypeID, None)
            if t:
                levelAndTypeLabel = t
        levelAndTypeLabel += ' - %s' % sm.GetService('agents').GetDivisions()[divisionID].divisionName.replace('&', '&amp;')
        leftCont = uicls.Container(name='leftCont', parent=agentCont, align=uiconst.TOLEFT, width=64)
        infoCont = uicls.Container(name='infoCont', parent=agentCont, align=uiconst.TOALL, clipChildren=True, padLeft=const.defaultPadding)
        icon = uicls.Icon(parent=leftCont, align=uiconst.TOPLEFT, size=64, ignoreSize=True)
        typeID = cfg.eveowners.Get(agentID).typeID
        icon.typeID = typeID
        icon.itemID = agentID
        icon.OnClick = (self.ShowInfo, icon)
        icon.GetMenu = (self.GetAgentMenu, icon)
        icon.LoadIconByTypeID(typeID, itemID=agentID, ignoreSize=True)
        if session.stationid:
            hint = mls.UI_CMD_STARTCONVERSATION
        else:
            hint = mls.UI_CMD_SHOWINFO
        icon.hint = hint
        top = 0
        nameText = '<url=showinfo:%d//%d><color=-2039584>%s</color></url>' % (const.typeCharacterAmarr, agentID, nameLabel)
        name = uicls.Label(text=nameText, parent=infoCont, top=top, state=uiconst.UI_NORMAL, bold=True)
        name.GetMenu = (self.GetAgentMenu, icon)
        name.hint = mls.UI_CMD_SHOWINFO
        top += 16
        corpText = '<url=showinfo:%d//%d><color=-2039584>%s</color></url>' % (const.typeCorporation, corporationID, corpLabel)
        corp = uicls.Label(text=corpText, parent=infoCont, top=top, state=uiconst.UI_NORMAL, bold=True)
        corp.typeID = const.typeCorporation
        corp.itemID = corporationID
        corp.OnClick = (self.ShowInfo, corp, True)
        corp.hint = mls.UI_CMD_SHOWINFO
        top += 16
        levelAndType = uicls.Label(text=levelAndTypeLabel, parent=infoCont, top=top)
        top += 16
        location = uicls.Label(text=locationLabel, parent=infoCont, top=top, state=uiconst.UI_NORMAL)
        if not isAvailable:
            for item in infoCont.children:
                item.SetAlpha(0.4)

            icon.SetAlpha(0.4)



    def GetAgentMenu(self, icon, *args):
        m = []
        m = sm.GetService('menu').CharacterMenu(icon.itemID)
        m.append((mls.UI_CMD_SHOWINFO, self.ShowInfo, (icon, True)))
        return m



    def BrowseAgents(self, btn, *args):
        browse = btn.backforth
        pos = max(0, self.pos + NUM_AGENTS * browse)
        self.pos = pos
        self.DrawAgents()



    def DisplayBrowse(self):
        numAgents = len(self.agentsList)
        pageNo = self.pos / NUM_AGENTS + 1
        if numAgents <= NUM_AGENTS:
            self.pageNumText.state = uiconst.UI_HIDDEN
        else:
            self.pageNumText.state = uiconst.UI_DISABLED
            self.pageNumText.text = mls.UI_TUTORIAL_PAGEOF % {'num': pageNo,
             'total': self.numPages}
        if self.pos == 0:
            self.prevBtn.Disable()
        else:
            self.prevBtn.Enable()
        if self.pos + NUM_AGENTS >= numAgents:
            self.nextBtn.Disable()
        else:
            self.nextBtn.Enable()



    def ShowInfo(self, item, onlyInfo = False, *args):
        if session.stationid and not onlyInfo:
            sm.GetService('agents').InteractWith(item.itemID)
        else:
            sm.GetService('info').ShowInfo(item.typeID, item.itemID)



    def OnChangeSize(self, *args):
        expanded = settings.user.ui.Get('agentFinderExpanded', False)
        if expanded:
            self.CollapseSearch(animate=True)
        else:
            self.ExpandSearch(animate=True)



    def ExpandSearch(self, animate = False):
        self.expanderIcon.LoadIcon(icon='ui_1_16_100')
        if animate:
            settings.user.ui.Set('agentFinderExpanded', True)
            if not self.sr.stack:
                self.expanderCont.Disable()
                self.leftCont.opacity = 0
                uicore.animations.FadeIn(self.leftCont)
                uicore.animations.MorphScalar(self, 'width', startVal=self.width, endVal=self.width + SEARCH_WIDTH, duration=0.5)
                uicore.animations.MorphScalar(self.leftCont, 'width', startVal=0, endVal=SEARCH_WIDTH, duration=0.5)
                uicore.animations.MorphScalar(self, 'left', startVal=self.left, endVal=self.left - SEARCH_WIDTH, duration=0.5, callback=self.EnableButton)
            else:
                uicore.animations.FadeIn(self.leftCont)
        self.SetMinSize([BIG_WIDTH, HEIGHT])
        self.leftCont.state = uiconst.UI_PICKCHILDREN



    def CollapseSearch(self, animate = False):
        self.expanderIcon.LoadIcon(icon='ui_1_16_99')
        if animate:
            settings.user.ui.Set('agentFinderExpanded', False)
            if not self.sr.stack:
                self.expanderCont.Disable()
                uicore.animations.FadeOut(self.leftCont)
                uicore.animations.MorphScalar(self, 'width', startVal=self.width, endVal=self.width - SEARCH_WIDTH, duration=0.5)
                uicore.animations.MorphScalar(self.leftCont, 'width', startVal=SEARCH_WIDTH, endVal=0, duration=0.5)
                uicore.animations.MorphScalar(self, 'left', startVal=self.left, endVal=self.left + SEARCH_WIDTH, duration=0.5, sleep=True, callback=self.EnableButton)
            else:
                uicore.animations.FadeOut(self.leftCont)
        self.SetMinSize([SMALL_WIDTH, HEIGHT])
        self.leftCont.state = uiconst.UI_HIDDEN



    def EnableButton(self):
        self.expanderCont.Enable()



    def UpdateAdjuster(self, animate = False):
        if not hasattr(self, 'leftSpacer'):
            return 
        (w, h,) = self.sliderCont.GetAbsoluteSize()
        self.med = w / SLIDER_COLUMNS
        newWidth = (self.agentLevel - 1) * self.med + ADJUSTER_WIDTH
        if animate:
            oldWidth = self.leftSpacer.width
            uicore.animations.MorphScalar(self.leftSpacer, 'width', startVal=oldWidth, endVal=newWidth, duration=0.25, callback=self.UpdatingWithAdjuster)
        else:
            self.leftSpacer.width = newWidth



    def UpdatingWithAdjuster(self):
        settings.user.ui.Set('agentFinderLevel', self.agentLevel)
        self.GetAgents()



    def OnSessionChanged(self, isremote, sess, change):
        self.GetAgents()



    def _OnResize(self, *args):
        uthread.new(self.UpdateAdjuster)



    def OnContMouseEnter(self, container, *args):
        container.SetOpacity(HOVER_ALPHA)



    def OnContMouseExit(self, container, *args):
        container.SetOpacity(NORMAL_ALPHA)




