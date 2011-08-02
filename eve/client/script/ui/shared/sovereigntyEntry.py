import uthread
import uix
import uiconst
import trinity
import uiutil
import util
import uicls
from sovereignty import SovereigntyTab
COLOR = (1.0, 1.0, 1.0, 0.5)

class SovereigntyEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.SovereigntyEntry'
    __nonpersistvars__ = ['selection', 'id']

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.label = uicls.Label(text='', parent=self, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1)
        self.sr.icon = uicls.Container(name='icon', parent=self, align=uiconst.TOPLEFT, padding=(0, 0, 0, 0), pos=(0, 0, 14, 14), state=uiconst.UI_DISABLED)
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.loss = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 0.0, 0.0, 0.25))



    def Load(self, node):
        self.sr.node = node
        self.sr.label.left = 16
        self.sr.label.text = node.label
        self.locationID = ''
        self.locationID = node.locationID
        self.allianceID = node.allianceID
        self.corpID = node.Get('corpID', None)
        self.scope = node.scope
        self.regionID = node.regionID
        uix.SetStateFlagForFlag(self.sr.icon, node.flag, top=3, showHint=False)
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]
        if node.loss is True:
            self.sr.loss.state = uiconst.UI_DISABLED
        else:
            self.sr.loss.state = uiconst.UI_HIDDEN



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 1
        return node.height



    def OnMouseHover(self, *args):
        uthread.new(self.SetHint)



    def OnDblClick(self, *args):
        if self.scope != SovereigntyTab.SolarSystem:
            self.DrillToLocation()



    def SetHint(self, *args):
        pass



    def ShowInfo(self, *args):
        pass



    def OnMouseEnter(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]



    def GetMenu(self):
        m = []
        mm = []
        mmm = []
        if self.locationID:
            if self.regionID is None:
                label = ''
                if self.scope == SovereigntyTab.SolarSystem:
                    label = None
                    mm += sm.GetService('menu').CelestialMenu(self.locationID)
                    m.append((mls.SYSTEM, mm))
                if self.scope == SovereigntyTab.World:
                    label = mls.REGION
                    mm += sm.GetService('menu').CelestialMenu(self.locationID)
                    m.append((mls.REGION, mm))
                elif self.scope == SovereigntyTab.Region:
                    label = mls.CONSTELLATION
                    mm += sm.GetService('menu').CelestialMenu(self.locationID)
                    m.append((mls.CONSTELLATION, mm))
                elif self.scope == SovereigntyTab.Constellation:
                    label = mls.SYSTEM
                    mm += sm.GetService('menu').CelestialMenu(self.locationID)
                    m.append((mls.SYSTEM, mm))
                m.append(None)
                if label is not None:
                    m.append(['%s %s' % (mls.UI_GENERIC_VIEW, label), self.DrillToLocation])
            else:
                mm += sm.GetService('menu').CelestialMenu(self.locationID)
                m.append((mls.SYSTEM, mm))
                mmm += sm.GetService('menu').CelestialMenu(self.regionID)
                m.append((mls.REGION, mmm))
                m.append(None)
            if self.allianceID is not None:
                if util.IsFaction(self.allianceID):
                    m.append([mls.UI_GENERIC_SHOWINFOONFACTION, self.ShowInfoOnSovHolder, (const.typeFaction, self.allianceID)])
                else:
                    m.append([mls.UI_GENERIC_SHOWINFOONALLIANCE, self.ShowInfoOnSovHolder, (const.typeAlliance, self.allianceID)])
            elif self.corpID is not None:
                m.append([mls.UI_GENERIC_SHOWINFOONCORPORATION, self.ShowInfoOnSovHolder, (const.typeCorporation, self.corpID)])
            return m
        else:
            return 



    def DrillToLocation(self):
        systemID = None
        constellationID = None
        regionID = None
        if self.scope in (SovereigntyTab.Constellation, SovereigntyTab.Changes):
            systemID = self.locationID
            constellationID = sm.GetService('map').GetParent(systemID)
            regionID = sm.GetService('map').GetParent(constellationID)
        if self.scope == SovereigntyTab.Region:
            constellationID = self.locationID
            regionID = sm.GetService('map').GetParent(constellationID)
        if self.scope == SovereigntyTab.World:
            regionID = self.locationID
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)



    def ShowInfoOnSovHolder(self, typeID, allianceID):
        sm.StartService('info').ShowInfo(typeID, allianceID)




class HeaderEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.HeaderEntry'

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.container = uicls.Container(name='container', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.industry = uicls.Container(name='industry', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 0), padding=(0, 0, 7, 0))
        self.sr.military = uicls.Container(name='military', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 0), padding=(0, 0, 8, 0))
        self.sr.claimTime = uicls.Container(name='claimTime', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 0), padding=(0, 0, 8, 0))
        self.sr.system = uicls.Container(name='solarsystem', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(4, 0, 0, 0))
        self.sr.systemHeader = uicls.Label(text='', parent=self.sr.system, left=0, top=4, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1, fontsize=10, uppercase=1, letterspace=2)
        self.sr.claimTimeHeader = uicls.Label(text='', parent=self.sr.claimTime, left=0, top=4, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1, fontsize=10, uppercase=1, letterspace=2)
        self.sr.militaryHeader = uicls.Label(text='', parent=self.sr.military, left=0, top=4, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1, fontsize=10, uppercase=1, letterspace=2)
        self.sr.industryHeader = uicls.Label(text='', parent=self.sr.industry, left=0, top=4, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1, fontsize=10, uppercase=1, letterspace=2)



    def Load(self, node):
        self.sr.node = node
        self.sr.militaryHeader.text = uiutil.UpperCase(node.militaryHeader)
        self.sr.systemHeader.text = uiutil.UpperCase(node.systemHeader)
        self.sr.claimTimeHeader.text = uiutil.UpperCase(node.claimTimeHeader)
        self.sr.industryHeader.text = uiutil.UpperCase(node.industryHeader)




class IndexEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.IndexEntry'

    def Startup(self, *etc):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125))
        self.sr.container = uicls.Container(name='container', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.industry = uicls.Container(name='industry', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 10), padding=(0, 3, 8, 4))
        self.sr.military = uicls.Container(name='military', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 10), padding=(0, 3, 8, 4))
        self.sr.claimTime = uicls.Container(name='claimTime', parent=self, align=uiconst.TORIGHT, pos=(0, 0, 88, 10), padding=(0, 3, 8, 4))
        self.sr.system = uicls.Container(name='solarsystem', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.location = uicls.Label(text='', parent=self.sr.system, left=6, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0, singleline=1)
        uicls.Line(parent=self.sr.claimTime, align=uiconst.TOTOP, color=COLOR)
        uicls.Line(parent=self.sr.claimTime, align=uiconst.TOBOTTOM, color=COLOR)
        uicls.Line(parent=self.sr.claimTime, align=uiconst.TOLEFT, color=COLOR)
        uicls.Line(parent=self.sr.claimTime, align=uiconst.TORIGHT, color=COLOR)
        for i in xrange(5):
            f = uicls.Fill(parent=self.sr.claimTime, name='claimTime%d' % i, align=uiconst.TOPLEFT, color=COLOR, pos=(2 + i * 17,
             2,
             16,
             6))
            setattr(self.sr, 'claimTime_%s' % i, f)

        uicls.Line(parent=self.sr.military, align=uiconst.TOTOP, color=COLOR)
        uicls.Line(parent=self.sr.military, align=uiconst.TOBOTTOM, color=COLOR)
        uicls.Line(parent=self.sr.military, align=uiconst.TOLEFT, color=COLOR)
        uicls.Line(parent=self.sr.military, align=uiconst.TORIGHT, color=COLOR)
        for i in xrange(5):
            f = uicls.Fill(parent=self.sr.military, name='military%d' % i, align=uiconst.TOPLEFT, color=COLOR, pos=(2 + i * 17,
             2,
             16,
             6))
            setattr(self.sr, 'military_%s' % i, f)

        uicls.Line(parent=self.sr.industry, align=uiconst.TOTOP, color=COLOR)
        uicls.Line(parent=self.sr.industry, align=uiconst.TOBOTTOM, color=COLOR)
        uicls.Line(parent=self.sr.industry, align=uiconst.TOLEFT, color=COLOR)
        uicls.Line(parent=self.sr.industry, align=uiconst.TORIGHT, color=COLOR)
        for i in xrange(5):
            f = uicls.Fill(parent=self.sr.industry, name='industry%d' % i, align=uiconst.TOPLEFT, color=COLOR, pos=(2 + i * 17,
             2,
             16,
             6))
            setattr(self.sr, 'industry_%s' % i, f)




    def Load(self, node):
        self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]
        self.sr.node = node
        self.sr.location.text = node.label
        self.locationID = node.locationID
        self.scope = node.scope
        self.DrawLevels('industry', const.attributeDevIndexIndustrial, node.industrialPoints)
        self.DrawLevels('military', const.attributeDevIndexMilitary, node.militaryPoints)
        self.DrawLevels('claimTime', const.attributeDevIndexSovereignty, node.claimedFor * const.DAY / const.SEC)



    def DrawLevels(self, indexName = None, indexID = None, value = None):
        indexInfo = sm.GetService('sov').GetIndexLevel(value, indexID)
        for i in xrange(5):
            fill = self.sr.Get('%s_%s' % (indexName, i))
            fill.color.SetRGB(1.0, 1.0, 1.0, 0.5)
            if indexInfo.level > i:
                fill.state = uiconst.UI_DISABLED
            else:
                fill.state = uiconst.UI_HIDDEN




    def OnMouseEnter(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = uiconst.UI_DISABLED



    def OnMouseExit(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.sr.selection.state = (uiconst.UI_HIDDEN, uiconst.UI_DISABLED)[self.sr.node.Get('selected', 0)]



    def OnDblClick(self, *args):
        if self.scope != SovereigntyTab.SolarSystem:
            self.DrillToLocation()



    def GetMenu(self):
        m = []
        mm = []
        if self.locationID:
            label = ''
            if self.scope == SovereigntyTab.SolarSystem:
                label = None
                mm += sm.GetService('menu').CelestialMenu(self.locationID)
                m.append((mls.SYSTEM, mm))
            if self.scope == SovereigntyTab.World:
                label = mls.REGION
                mm += sm.GetService('menu').CelestialMenu(self.locationID)
                m.append((mls.REGION, mm))
            elif self.scope == SovereigntyTab.Region:
                label = mls.CONSTELLATION
                mm += sm.GetService('menu').CelestialMenu(self.locationID)
                m.append((mls.CONSTELLATION, mm))
            elif self.scope == SovereigntyTab.Constellation:
                label = mls.SYSTEM
                mm += sm.GetService('menu').CelestialMenu(self.locationID)
                m.append((mls.SYSTEM, mm))
            m.append(None)
            if label is not None:
                m.append(['%s %s' % (mls.UI_GENERIC_VIEW, label), self.DrillToLocation])
            return m
        else:
            return 



    def DrillToLocation(self):
        systemID = None
        constellationID = None
        regionID = None
        if self.scope == SovereigntyTab.Constellation:
            systemID = self.locationID
            constellationID = sm.GetService('map').GetParent(systemID)
            regionID = sm.GetService('map').GetParent(constellationID)
        if self.scope == SovereigntyTab.Region:
            constellationID = self.locationID
            regionID = sm.GetService('map').GetParent(constellationID)
        if self.scope == SovereigntyTab.World:
            regionID = self.locationID
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)




