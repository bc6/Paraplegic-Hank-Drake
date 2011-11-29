import sys
import blue
import uthread
import uix
import uiutil
import xtriui
import util
import service
import base
import trinity
import re
import uicls
import log
import uiconst
import math
from collections import deque
import form
import localization
import fontConst
import bookmarkUtil
from service import ROLE_GML
FRAME_WIDTH = 20
FRAME_SEPERATION = 10
NEOCOM_PANELWIDTH = 328
LOCATION_PANELWIDTH = 600
BACKGROUND_COLOR = (0,
 0,
 0,
 0.1)
BUTTONHEIGHT = 30
ROUTE_MARKERSIZE = 8
ROUTE_MARKERGAP = 2
IDLE_ROUTEMARKER_ALPHA = 0.75
STD_TEXTSHADOWOFFSET = (0, 1)
MO = [3.5455531962,
 3.36937132567,
 2.59914513634,
 1.61375875964,
 0.63290495212,
 0.05177315618,
 0.0]
EXPANDED_SIZE = 132
COLLAPSED_SIZE = 36

class SessionTimeIndicator(uicls.Container):
    __guid__ = 'uicls.SessionTimeIndicator'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        size = 24
        self.ramps = uicls.Container(parent=self, name='ramps', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        leftRampCont = uicls.Container(parent=self.ramps, name='leftRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.leftRamp = uicls.Transform(parent=leftRampCont, name='leftRamp', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        uicls.Sprite(parent=self.leftRamp, name='rampSprite', pos=(0,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/left.png', color=(0, 0, 0, 0.5))
        rightRampCont = uicls.Container(parent=self.ramps, name='rightRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.rightRamp = uicls.Transform(parent=rightRampCont, name='rightRamp', pos=(-size / 2,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        uicls.Sprite(parent=self.rightRamp, name='rampSprite', pos=(size / 2,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/right.png', color=(0, 0, 0, 0.5))
        self.coloredPie = uicls.Sprite(parent=self, name='tidiColoredPie', pos=(0,
         0,
         size,
         size), texturePath='res:/UI/Texture/classes/TiDiIndicator/circle.png', state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.5))



    def SetStopTime(self, stopTime):
        startTime = blue.os.GetSimTime()
        duration = stopTime - startTime
        while blue.os.GetSimTime() < stopTime:
            timeDiff = stopTime - blue.os.GetSimTime()
            progress = timeDiff / float(duration)
            self.SetProgress(1.0 - progress)
            timeLeft = util.FmtTimeInterval(timeDiff, breakAt='sec')
            self.hint = localization.GetByLabel('UI/Neocom/SessionChangeHint', timeLeft=timeLeft)
            self.state = uiconst.UI_NORMAL
            uicore.CheckHint()
            blue.pyos.synchro.Yield()

        self.SetProgress(1.0)
        self.state = uiconst.UI_HIDDEN



    def SetProgress(self, progress):
        progress = max(0.0, min(1.0, progress))
        leftRamp = min(1.0, max(0.0, progress * 2))
        rightRamp = min(1.0, max(0.0, progress * 2 - 1.0))
        self.leftRamp.SetRotation(math.pi + math.pi * leftRamp)
        self.rightRamp.SetRotation(math.pi + math.pi * rightRamp)




class NeocomContainer(uicls.Container):
    __guid__ = 'uicls.NeocomContainer'
    default_name = 'neocomContainer'
    default_padTop = FRAME_SEPERATION
    default_padRight = LOCATION_PANELWIDTH - NEOCOM_PANELWIDTH
    default_align = uiconst.TOTOP
    default_collapsable = False

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.collapsable = attributes.get('collapsable', self.default_collapsable)
        if self.collapsable:
            self.collapseContainer = uicls.Container(parent=self, name='collapseContainer', align=uiconst.TOPRIGHT, pos=(FRAME_WIDTH,
             0,
             15,
             15), state=uiconst.UI_NORMAL)
            self.collapseIcon = uicls.Sprite(name='collapseIcon', parent=self.collapseContainer, texturePath='res:/UI/Texture/Shared/expanderUp.png', pos=(1, 2, 11, 11), hint=localization.GetByLabel('UI/Neocom/Collapse'))
            self.collapseHighlight = uicls.Fill(parent=self.collapseContainer, color=(1, 1, 1, 0.25), state=uiconst.UI_HIDDEN)
            self.collapseIcon.OnClick = self.ToggleCollapseState
            self.collapseIcon.OnMouseEnter = (self.CollapseButtonEnter, self.collapseIcon)
            self.collapseIcon.OnMouseExit = (self.CollapseButtonExit, self.collapseIcon)
            self.collapsed = False
        contentPadding = attributes.get('contentPadding', FRAME_WIDTH)
        self.content = uicls.Container(parent=self, name='content', align=uiconst.TOALL, padding=(contentPadding,
         0,
         contentPadding,
         0))



    def PostApplyAttributes(self, attributes):
        self.UpdateStandardAppearance()



    def UpdateStandardAppearance(self, *args):

        def WalkContainer(container):
            for each in container.children:
                if getattr(each, 'children', None):
                    WalkContainer(each)
                elif isinstance(each, uicls.Label):
                    each.shadowOffset = STD_TEXTSHADOWOFFSET



        WalkContainer(self.content)



    def Flush(self):
        self.content.Flush()



    def ToggleCollapseState(self, discard = None):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.collapseIcon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
            self.collapseIcon.SetHint(localization.GetByLabel('UI/Neocom/Expand'))
        else:
            self.collapseIcon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
            self.collapseIcon.SetHint(localization.GetByLabel('UI/Neocom/Collapse'))
        self.OnCollapse(self.collapsed)



    def CollapseButtonEnter(self, discard):
        self.collapseHighlight.state = uiconst.UI_DISABLED



    def CollapseButtonExit(self, discard):
        self.collapseHighlight.state = uiconst.UI_HIDDEN



    def OnCollapse(self, collaspsed):
        pass



    def _OnSizeChange_NoBlock(self, newWidth, newHeight):
        softShadow = uicore.layer.neocom.FindChild('softShadow')
        if softShadow:
            totalHeight = sum([ each.height + each.padTop + each.padBottom for each in self.parent.children if isinstance(each, uicls.NeocomContainer) ])
            softShadow.height = int(totalHeight * 2)




class NeocomSvc(service.Service):
    __update_on_reload__ = 0
    __exportedcalls__ = {'Blink': [],
     'BlinkOff': [],
     'Position': [],
     'LoadRouteData': [],
     'GetSideOffset': [],
     'Minimize': [],
     'Maximize': [],
     'UpdateMenu': [],
     'SetLocationInfoState': []}
    __guid__ = 'svc.neocom'
    __dependencies__ = ['settings', 'contracts']
    __notifyevents__ = ['OnSetDevice',
     'OnSessionChanged',
     'OnAggressionChanged',
     'ProcessRookieStateChange',
     'OnSystemStatusChanged',
     'OnSovereigntyChanged',
     'OnPostCfgDataChanged',
     'ProcessUIRefresh',
     'OnEntitySelectionChanged',
     'OnViewStateChanged']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, memStream = None):
        self.LogInfo('Starting Neocom')
        self.validNearBy = [const.groupAsteroidBelt,
         const.groupMoon,
         const.groupPlanet,
         const.groupWarpGate,
         const.groupStargate]
        self.Reset()
        if eve.session.charid and not (eve.rookieState and eve.rookieState < 2):
            self.UpdateNeocom()
            if 'starmap' in sm.services:
                routeData = sm.GetService('starmap').GetDestinationPath()
                if routeData != [None]:
                    self.LoadRouteData(routeData)



    def Stop(self, memStream = None):
        self.CloseNeocomLeftSide()
        if self.wnd is not None and not self.wnd.destroyed:
            self.wnd.Close()
            self.wnd = None
        self.Reset()



    def ProcessUIRefresh(self):
        self.Stop()
        self.Run()



    def OnSystemStatusChanged(self, *args):
        if eve.session.charid:
            self.UpdateNeocom(0)



    def OnSovereigntyChanged(self, solarSystemID, allianceID):
        self.UpdateAllLocationInfo()



    def OnEntitySelectionChanged(self, entityID):
        self.UpdateAllLocationInfo()



    def ProcessRookieStateChange(self, state):
        if eve.session.charid:
            if not not (eve.rookieState and eve.rookieState < 2):
                self.CloseNeocomLeftSide()
                if self.wnd is not None and not self.wnd.destroyed:
                    self.wnd.Close()
                    self.wnd = None
                self.Reset()
            elif self.wnd:
                self.UpdateMenu()
            else:
                self.UpdateNeocom()



    def OnSessionChanged(self, isRemote, sess, change):
        if session.charid is None:
            self.CloseNeocomLeftSide()
            if self.wnd is not None and not self.wnd.destroyed:
                self.wnd.Close()
                self.wnd = None
            self.Reset()
        else:
            self.UpdateNeocom('solarsystemid2' in change or 'solarsystemid' in change or 'stationid' in change)
            self.UpdateSessionTimer()



    def OnViewStateChanged(self, oldViewName, newViewName):
        uthread.new(self.UpdateRouteInfo)



    def CloseNeocomLeftSide(self):
        if self.neocomLeftSide is not None and not self.neocomLeftSide.destroyed:
            self.neocomLeftSide.Close()
            self.neocomLeftSide = None



    def ShowHideNeoComLeftSide(self, hide = 1, *args):
        if self.neocomLeftSide is not None and not self.neocomLeftSide.destroyed:
            if hide:
                self.neocomLeftSide.state = uiconst.UI_HIDDEN
            else:
                self.neocomLeftSide.state = uiconst.UI_PICKCHILDREN



    def OnAggressionChanged(self, solarsystemID, aggressors):
        blue.pyos.synchro.Yield()
        (charcrimes, corpcrimes,) = sm.GetService('michelle').GetCriminalFlagCountDown()
        if charcrimes or corpcrimes:
            self.UpdateCrimeInfo(charcrimes, corpcrimes)



    def OnSetDevice(self):
        if self.wnd is not None and not self.wnd.destroyed:
            self.wnd.height = uicore.desktop.height



    def Reset(self):
        self.stopbtnreset = 0
        self.nearby = None
        self.locationParent = None
        self.locationInfo = None
        self.neocomLeftSide = None
        self.expander = None
        self.autohidearea = None
        self.clock = None
        self.clocktimer = None
        self.locationTimer = None
        self.btnresettimer = None
        self.lastLocationID = None
        self.updating = False
        self.updatingWindowPush = False
        self.activeshipicon = None
        self.activeshipname = None
        self.mainLocationInfo = None
        self.routeContainer = None
        if not hasattr(self, 'routeData'):
            self.routeData = None
        self.wnd = None
        self.menubtn = None
        self.bottomline = None
        self.shipsbtn = None
        self.itemsbtn = None
        if getattr(self, 'btns', None):
            uiutil.FlushList(self.btns)
        self.btns = []
        self.btnsready = 0
        self.blinkingBtns = {}
        self.main = None
        self.inited = 0
        self.criminalTimer = None



    def Initialize(self):
        for each in uicore.layer.neocom.children[:]:
            if each.name in ('neocom', 'softShadow'):
                each.Close()

        self.wnd = uicls.Container(parent=uicore.layer.neocom, name='neocom', state=uiconst.UI_HIDDEN, align=uiconst.TOLEFT, idx=0)
        autohideparent = uicls.Container(parent=self.wnd, name='autohideparent', state=uiconst.UI_PICKCHILDREN)
        autohidedetector = uicls.Container(parent=autohideparent, width=8, name='autohidedetector', state=uiconst.UI_NORMAL, align=uiconst.TOLEFT)
        maincontainer = uicls.Container(parent=self.wnd, padding=(2, 0, 2, 0), name='maincontainer', state=uiconst.UI_NORMAL)
        mainNameParent = uicls.Container(parent=maincontainer, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 128), state=uiconst.UI_NORMAL)
        expander = uicls.Sprite(parent=mainNameParent, name='expander', pos=(5, 5, 11, 11), align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderLeft.png')
        nameParent = uicls.Transform(parent=mainNameParent, pos=(-41, 52, 116, 28), name='nameParent', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        self.wnd.sr.charname = uicls.EveLabelMedium(text='', parent=nameParent, align=uiconst.TOPLEFT, width=100, state=uiconst.UI_DISABLED)
        self.nameFill = uicls.Fill(name='nameFill', parent=mainNameParent, color=(0.0, 0.0, 0.0, 0.6))
        charpic = uicls.Sprite(parent=maincontainer, height=128, name='charactersheet', state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        clockpar = uicls.Container(parent=maincontainer, pos=(0, 0, 128, 16), name='clockpar', state=uiconst.UI_DISABLED, align=uiconst.TOBOTTOM)
        linepar = uicls.Container(parent=clockpar, pos=(0, 0, 2, 2), name='line', state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        uicls.Line(parent=linepar, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOBOTTOM, name='white')
        uicls.Line(parent=linepar, color=(0.0, 0.0, 0.0, 1.0), align=uiconst.TOBOTTOM, name='black')
        exitbtnParent = uicls.Container(parent=maincontainer, height=64, name='exitbtnParent', state=uiconst.UI_NORMAL, align=uiconst.TOBOTTOM)
        self.undockBlinker = uicls.Container(parent=exitbtnParent, state=uiconst.UI_NORMAL)
        self.undockIcon = uicls.Sprite(parent=self.undockBlinker, texturePath='res:/UI/Texture/Icons/9_64_6.png', state=uiconst.UI_NORMAL)
        self.wnd.sr.btnparent = uicls.Container(parent=maincontainer, name='btnparent', state=uiconst.UI_PICKCHILDREN, clipChildren=True, align=uiconst.TOALL)
        onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
        self.wnd.SetAlign([uiconst.TORIGHT, uiconst.TOLEFT][onLeft])
        if settings.user.windows.Get('neoautohide', 0):
            self.AutoHide()
        else:
            BIG = settings.user.windows.Get('neowidth', 1)
            self.wnd.width = [COLLAPSED_SIZE, EXPANDED_SIZE][BIG]
        self.wnd.sr.underlay = uicls.WindowUnderlay(parent=self.wnd)
        self.wnd.sr.underlay.SetPadding(-1, -10, -1, -10)
        self.main = maincontainer
        maincontainer.OnMouseEnter = self.MainEnter
        maincontainer.OnMouseExit = self.MainExit
        maincontainer.GetMenu = self.GetMainMenu
        charpic.OnMouseEnter = self.CharPicEnter
        charpic.OnMouseExit = self.CharPicExit
        charpic.OnClick = (self.BtnClick, charpic)
        charpic.cmdstr = 'OpenCharactersheet'
        self.expander = expander
        self.expander.OnClick = self.ExpanderClick
        self.expander.parent.state = uiconst.UI_PICKCHILDREN
        sm.GetService('photo').GetPortrait(eve.session.charid, 256, charpic)
        clockpar.name = 'clock'
        clockpar.height = 28
        self.clockparDeco = clockpar
        selection = uicls.Fill(parent=self.clockparDeco, padding=(-1, -1, -1, -1), align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_HIDDEN)
        self.clockparDeco.sr.selection = selection
        self.clockparDeco.OnMouseEnter = (self.BtnEnter, self.clockparDeco)
        self.clockparDeco.OnMouseExit = (self.BtnExit, self.clockparDeco)
        self.clockparDeco.OnClick = (self.BtnClick, self.clockparDeco)
        self.clockparDeco.cmdstr = 'OpenCalendar'
        self.clockparDeco.state = uiconst.UI_NORMAL
        self.clockparDeco.GetMenu = self.GetMainMenu
        self.clockparDeco.displayName = localization.GetByLabel('UI/Neocom/CalendarBtn')
        self.clock = uicls.EveHeaderSmall(parent=self.clockparDeco, left=0, top=3, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, idx=0)
        self.dateText = uicls.Label(parent=self.clockparDeco, align=uiconst.CENTERTOP, fontsize=14, state=uiconst.UI_DISABLED, idx=0)
        self.autohidearea = autohidedetector
        self.autohidearea.OnMouseEnter = self.OnAutohideEnter
        self.neocomLeftSide = uicls.Container(parent=uicore.layer.neocom, name='neocomLeftside', align=uiconst.TOLEFT, width=LOCATION_PANELWIDTH, padLeft=12)
        uicls.Sprite(parent=uicore.layer.neocom, name='softShadow', texturePath='res:/UI/Texture/classes/Neocom/infopanelSoftShadow2.png', width=500, height=500, left=-20, state=uiconst.UI_DISABLED, color=(0, 0, 0, 0.3))
        self.locationParent = uicls.NeocomContainer(parent=self.neocomLeftSide, name='locationInfo', padRight=0, showBackground=True, contentPadding=0)
        self.locationInfo = self.locationParent.content
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            if settings.public.ui.Get('Insider', True):
                uthread.pool('neocom::ShowInsider', self.ShowInsider)
        self.inited = 1
        self.UpdateClock()
        uthread.pool('neocom::CheckSkills', self.CheckSkills)



    def ShowInsider(self):
        sm.GetService('insider').Show()



    def UpdateSessionTimer(self):
        if settings.user.ui.Get('showSessionTimer', 0):
            uthread.new(self.sessionTimer.SetStopTime, session.nextSessionChange)



    def CheckSkills(self):
        skillInTraining = sm.GetService('skills').SkillInTraining()
        if skillInTraining:
            godma = sm.StartService('godma')
            endOfTraining = godma.GetStateManager().GetEndOfTraining(skillInTraining.itemID)
            godma.GetStateManager().endOfTraining[skillInTraining.itemID] = endOfTraining
        else:
            self.Blink('charactersheet')



    def GetIconMappings(self, btnname = None):
        mapping = [util.KeyVal(name='charactersheet', command='OpenCharactersheet', label=localization.GetByLabel('UI/Neocom/CharacterSheetBtn'), iconID='ui_2_64_16', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='addressbook', command='OpenPeopleAndPlaces', label=localization.GetByLabel('UI/Neocom/PeopleAndPlacesBtn'), iconID='ui_12_64_2', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='mail', command='OpenMail', label=localization.GetByLabel('UI/Neocom/EvemailBtn'), iconID='ui_94_64_8', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='fitting', command='OpenFitting', label=localization.GetByLabel('UI/Neocom/FittingBtn'), iconID='ui_17_128_4', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='notepad', command='OpenNotepad', label=localization.GetByLabel('UI/Neocom/NotepadBtn'), iconID='ui_49_64_2', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='market', command='OpenMarket', label=localization.GetByLabel('UI/Neocom/MarketBtn'), iconID='ui_18_128_1', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='factories', command='OpenScienceAndIndustry', label=localization.GetByLabel('UI/Neocom/ScienceAndIndustryBtn'), iconID='ui_57_64_9', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='contracts', command='OpenContracts', label=localization.GetByLabel('UI/Neocom/ContractsBtn'), iconID='ui_64_64_10', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='map', command='CmdToggleMap', label=localization.GetByLabel('UI/Neocom/MapBtn'), iconID='ui_7_64_4', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='corporation', command='OpenCorporationPanel', label=localization.GetByLabel('UI/Neocom/CorporationBtn'), iconID='ui_7_64_6', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='assets', command='OpenAssets', label=localization.GetByLabel('UI/Neocom/AssetsBtn'), iconID='ui_7_64_13', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='wallet', command='OpenWallet', label=localization.GetByLabel('UI/Neocom/WalletBtn'), iconID='ui_7_64_12', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='fleet', command='OpenFleet', label=localization.GetByLabel('UI/Neocom/FleetBtn'), iconID='ui_94_64_9', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='calculator', command='OpenCalculator', label=localization.GetByLabel('UI/Neocom/CalculatorBtn'), iconID='ui_49_64_1', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='browser', command='OpenBrowser', label=localization.GetByLabel('UI/Neocom/BrowserBtn'), iconID='ui_9_64_4', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='journal', command='OpenJournal', label=localization.GetByLabel('UI/Neocom/JournalBtn'), iconID='ui_25_64_3', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='jukebox', command='OpenJukebox', label=localization.GetByLabel('UI/Neocom/JukeboxBtn'), iconID='ui_12_64_5', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='log', command='OpenLog', label=localization.GetByLabel('UI/Neocom/logBtn'), iconID='ui_34_64_4', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='accessories', command=None, label=localization.GetByLabel('UI/Neocom/AccessoriesBtn'), iconID='ui_6_64_2', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='stationservices', command=None, label=localization.GetByLabel('UI/Neocom/ServicesBtn'), iconID='ui_76_64_2', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='navyoffices', command='OpenMilitia', label=localization.GetByLabel('UI/Neocom/MilitiaOfficeBtn'), iconID='ui_61_128_3', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='help', command='OpenHelp', label=localization.GetByLabel('UI/Neocom/HelpBtn'), iconID='ui_74_64_13', scope=const.neocomButtonScopeEverywhere),
         util.KeyVal(name='ships', command='OpenShipHangar', label=localization.GetByLabel('UI/Neocom/ShipsBtn'), iconID='ui_9_64_5', scope=const.neocomButtonScopeStationOrWorldspace),
         util.KeyVal(name='items', command='OpenHangarFloor', label=localization.GetByLabel('UI/Neocom/ItemsBtn'), iconID='ui_12_64_3', scope=const.neocomButtonScopeStationOrWorldspace)]
        newmapping = {}
        for (i, iconmap,) in enumerate(mapping):
            iconmap.index = i
            newmapping[iconmap.name] = iconmap

        if btnname:
            return newmapping.get(btnname, None)
        return newmapping



    def GetIconMapping(self, sortBy = None, all = False):
        iconmapping = []
        icons = self.GetIconMappings()
        for (service, info,) in icons.iteritems():
            sortItem = info.index
            if sortBy == 'name':
                sortItem = info.label
            if eve.session.stationid and settings.user.windows.Get('dockshipsanditems', 0) and service in ('ships', 'items'):
                continue
            if service == 'navyoffices' and not sm.StartService('facwar').CheckStationElegibleForMilitia():
                continue
            if info.scope == const.neocomButtonScopeEverywhere or info.scope == const.neocomButtonScopeInflight and session.stationid2 is None or info.scope == const.neocomButtonScopeStation and session.stationid2 is not None and session.stationid2 == session.worldspaceid or info.scope == const.neocomButtonScopeStationOrWorldspace and session.stationid2 is not None:
                iconmapping.append(((sortItem, service), info))

        (stationiconmapping, inStationServices,) = self.GetStationServiceMapping(sortBy, all)
        iconmapping.extend(stationiconmapping)
        iconmapping = uiutil.SortListOfTuples(iconmapping)
        inUtils = settings.user.windows.Get('neocomAccessories', None)
        if inUtils is None:
            inUtils = ['notepad', 'calculator', 'log']
        return (iconmapping, inUtils, inStationServices)



    def GetStationServiceMapping(self, sortBy = None, all = False, applySort = False):
        icons = self.GetIconMappings()
        iconmapping = []
        services = sm.GetService('station').GetStationServices()
        for (service, info,) in services.iteritems():
            if info.scope in (const.neocomButtonScopeStation, const.neocomButtonScopeStationOrWorldspace):
                continue
            sortItem = info.name
            if sortBy == 'name':
                sortItem = info.label
            subSortBy = service
            if all or info.scope in (const.neocomButtonScopeStation, const.neocomButtonScopeStationOrWorldspace) and session.stationid2 is not None or info.scope == const.neocomButtonScopeEverywhere:
                for serviceID in info.serviceIDs:
                    if info.scope not in (const.neocomButtonScopeStation, const.neocomButtonScopeStationOrWorldspace) or all or eve.stationItem.serviceMask & serviceID == serviceID:
                        if service not in icons:
                            data = ((sortItem,
                              service,
                              info.command,
                              info.label,
                              info.iconID), info)
                            if data not in iconmapping:
                                iconmapping.append(data)


        inStationServices = settings.user.windows.Get('neocomStationservices', None)
        if inStationServices is None:
            inStationServices = [ service for (service, info,) in services.iteritems() if service not in icons if info.scope not in (const.neocomButtonScopeStation, const.neocomButtonScopeStationOrWorldspace) ]
        if applySort:
            iconmapping = uiutil.SortListOfTuples(iconmapping)
        return (iconmapping, inStationServices)



    def UpdateMenu(self):
        if not self.wnd:
            return 
        btnpar = self.wnd.sr.btnparent
        btnpar.Flush()
        self.btns = []
        (iconMapping, inUtils, inStationServices,) = self.GetIconMapping()
        for info in iconMapping:
            if info.name == 'accessories' and not inUtils:
                continue
            if info.name == 'stationservices' and not inStationServices:
                continue
            btn = self.GetButton(info.label, info.iconID, btnpar)
            btn.name = info.name
            btn.cmdstr = info.command
            btn.OnClick = (self.BtnClick, btn)
            btn.OnMouseEnter = (self.BtnEnter, btn)
            btn.OnMouseExit = (self.BtnExit, btn)
            if info.name in ('accessories', 'stationservices'):
                if info.name == 'accessories' and inUtils:
                    btn.GetMenu = self.GetToolsMenu
                if info.name == 'stationservices' and inStationServices:
                    btn.GetMenu = self.GetStationServiceMenu
                btn.GetMenuPosition = self.ReturnMenuPos
                btn.expandOnLeft = 1
                btn.state = uiconst.UI_NORMAL
                menuArrow = uicls.Icon(icon='ui_38_16_228', parent=btn, size=16, idx=0, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED)
                btn.sr.menuArrow = menuArrow
                self.btns.append(btn)
                continue
            if info.name in inUtils or info.name in inStationServices:
                continue
            if info.name == 'jukebox':
                btn.GetMenu = self.GetJukeboxMenu
                btn.GetMenuPosition = self.ReturnMenuPos
            if info.name in ('items', 'ships'):
                btn.OnDropData = self.DropInHangar
            self.btns.append(btn)
            setattr(self, '%sbtn' % info.name, btn)
            btn.state = uiconst.UI_NORMAL

        if self.menubtn is not None and not self.menubtn.destroyed:
            self.btns.remove(self.menubtn)
            self.menubtn.Close()
            self.menubtn = None
        if self.bottomline is not None and not self.bottomline.destroyed:
            self.bottomline.Close()
            self.bottomline = None
        self.undockIcon.parent.state = uiconst.UI_HIDDEN
        if session.stationid2:
            self.undockIcon.OnClick = (self.BtnClick, self.undockIcon)
            self.undockIcon.parent.state = uiconst.UI_NORMAL
            self.undockIcon.OnMouseEnter = (self.BtnEnter, self.undockIcon)
            self.undockIcon.OnMouseExit = (self.BtnExit, self.undockIcon)
            self.undockIcon.name = 'undock'
            self.undockIcon.displayName = localization.GetByLabel('UI/Neocom/UndockBtn')
            self.undockIcon.hint = self.undockIcon.displayName
            self.undockIcon.cmdstr = 'CmdExitStation'
        self.bottomline = uicls.Line(parent=btnpar, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOTOP, name='whiteline')
        self.Position()
        self.btnsready = 1
        for each in self.blinkingBtns:
            self.Blink(each, force=0)




    def ReturnMenuPos(self, btn, *args):
        (l, t, w, h,) = btn.GetAbsolute()
        onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
        if onLeft:
            return (l + w, t + 4, 1)
        else:
            return (l, t + 4, 0)



    def GetNeocomMenu(self, which):
        if which == 'accessories':
            return self.GetToolsMenu()
        else:
            if which == 'stationservices':
                return self.GetStationServiceMenu()
            return []



    def GetStationServiceMenu(self, *args):
        m = []
        (iconMapping, inUtils, inStationServices,) = self.GetIconMapping('name')
        for info in iconMapping:
            if info.name not in inStationServices:
                continue
            m.append((info.label,
             self.CmdMenuAction,
             (info.command,),
             (info.iconID, 32)))

        return m



    def GetToolsMenu(self, *args):
        m = []
        (iconMapping, inUtils, inStationServices,) = self.GetIconMapping('name')
        for info in iconMapping:
            if info.name not in inUtils:
                continue
            m.append((info.label,
             self.CmdMenuAction,
             (info.command,),
             (info.iconID, 32)))

        return m



    def GetJukeboxMenu(self, *args):
        ret = [(localization.GetByLabel('UI/Jukebox/ShowJukebox'), lambda *args: uicore.cmd.OpenJukebox()), None]
        if sm.GetService('jukebox').jukeboxState == 'play':
            ret += [(localization.GetByLabel('UI/Jukebox/Pause'), lambda *args: sm.GetService('jukebox').Pause())]
        else:
            ret += [(localization.GetByLabel('UI/Jukebox/Play'), lambda *args: sm.GetService('jukebox').Play())]
        ret += [(localization.GetByLabel('UI/Jukebox/Next'), lambda *args: sm.GetService('jukebox').AdvanceTrack()), (localization.GetByLabel('UI/Jukebox/Previous'), lambda *args: sm.GetService('jukebox').AdvanceTrack(forward=False))]
        return ret



    def GetButton(self, svcname, iconNum, btnpar):
        btn = uicls.Container(parent=btnpar, height=BUTTONHEIGHT, name=svcname, hint=svcname, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP)
        btn.sr.selection = uicls.Fill(parent=btn, name='btnselection', state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.15))
        uicls.Line(parent=btn, color=(0.0, 0.0, 0.0, 0.5), align=uiconst.TOBOTTOM, name='blackline')
        uicls.Line(parent=btn, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOTOP, name='whiteline')
        btn.sr.blink = None
        btn.displayName = svcname
        iconPar = uicls.Container(name='iconpar', parent=btn, idx=0, state=uiconst.UI_DISABLED, top=-1, height=-1)
        icon = uicls.Icon(icon=iconNum, parent=iconPar, align=uiconst.TORIGHT, ignoreSize=True, size=32)
        textPar = uicls.Container(name='textPar', parent=iconPar, clipChildren=1)
        btn.sr.nme = uicls.EveLabelSmall(text='', parent=textPar, align=uiconst.CENTERLEFT, top=1)
        btn.sr.icon = icon
        return btn



    def GetBlink(self, btn):
        if btn.sr.blink:
            return btn.sr.blink
        if not hasattr(btn, 'children'):
            return None
        blink = uicls.Fill(parent=btn, name='hiliteFrame', padTop=1, state=uiconst.UI_DISABLED, color=(0.28, 0.3, 0.35, 1.0), align=uiconst.TOALL, blendMode=trinity.TR2_SBM_ADD)
        btn.sr.blink = blink
        btn.r = 0.28
        btn.g = 0.3
        btn.b = 0.35
        return btn.sr.blink



    def GetButtonHeight(self):
        maxTotal = uicore.desktop.height - 218
        if self.btns:
            return min(BUTTONHEIGHT, maxTotal / len(self.btns))
        else:
            return BUTTONHEIGHT



    def Position(self, action = None, windowData = None):
        LEFT = settings.user.windows.Get('neoalign', 'left') == 'left'
        BIG = settings.user.windows.Get('neowidth', 1)
        if BIG:
            width = EXPANDED_SIZE
        else:
            width = COLLAPSED_SIZE
        windowData = windowData or self.PrepareForWindowPush()
        try:
            if self.wnd is None or self.wnd.destroyed:
                return 
            time = 150.0
            cn = cfg.eveowners.Get(eve.session.charid).name
            charname = self.wnd.sr.charname
            charname.parent.parent.width = BUTTONHEIGHT + 2
            charname.parent.parent.SetAlign([uiconst.TOPLEFT, uiconst.TOPRIGHT][LEFT])
            if getattr(self, 'nameFill', None) is not None:
                if BIG:
                    self.nameFill.SetAlpha(0.6)
                else:
                    self.nameFill.SetAlpha(1.0)
            if unicode(cn) != unicode(cn).encode('ascii', 'replace'):
                cn = '<center>' + ''.join([ letter + '<br>' for letter in cn ])
                charname.height = 100
                charname.text = cn
                charname.parent.SetRotation(0.0)
                charname.parent.top = 24
            else:
                charname.parent.SetRotation(math.pi / 2)
                charname.text = cn
            if LEFT:
                self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderRight.png', 'res:/UI/Texture/Shared/expanderLeft.png'][BIG])
            else:
                self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderLeft.png', 'res:/UI/Texture/Shared/expanderRight.png'][BIG])
            bh = self.GetButtonHeight()
            for btn in self.btns:
                btn.sr.icon.align = [uiconst.TOLEFT, uiconst.TORIGHT][LEFT]
                if btn.sr.menuArrow:
                    btn.sr.menuArrow.SetAlign([uiconst.CENTERLEFT, uiconst.CENTERRIGHT][LEFT])
                    btn.sr.menuArrow.LoadIcon(['ui_38_16_227', 'ui_38_16_228'][LEFT])
                if BIG:
                    (labelParWidth, labelParHeight,) = btn.sr.nme.parent.GetAbsoluteSize()
                    btn.sr.nme.left = [4, 8][LEFT]
                    btn.sr.nme.width = max(88, labelParWidth - btn.sr.nme.left)
                    btn.sr.nme.text = btn.displayName
                else:
                    btn.sr.nme.text = ''

            self.AlignUndockButton(BIG, bh)
            self.UpdateWindowPush(windowData, width, action)
            self.ResetBtns(0)
            blue.pyos.synchro.SleepWallclock(int(time))
            self.UpdateClock()

        finally:
            pass




    def GetWnd(self):
        return self.wnd



    def AlignUndockButton(self, big, bh):
        self.undockIcon.align = uiconst.CENTER
        self.undockIcon.width = 54 if big else max(BUTTONHEIGHT, bh)
        self.undockIcon.height = 60 if big else max(BUTTONHEIGHT, bh)



    def PrepareForWindowPush(self, canWait = False):
        if canWait:
            while self.updatingWindowPush:
                blue.pyos.synchro.Sleep(1)

        if settings.user.windows.Get('neoautohide', 0) and getattr(self, 'isAutoExpanded', False):
            (leftOffset, rightOffset,) = self.GetSideOffset(ignoreAutoHide=True)
        else:
            (leftOffset, rightOffset,) = self.GetSideOffset(ignoreAutoHide=False)
        validWnds = uicore.registry.GetValidWindows(floatingOnly=True)
        desktopWidth = uicore.desktop.width
        wndsOnLeft = []
        wndsOnRight = []
        wndsOnLeftOffset = []
        wndsOnRightOffset = []
        for wnd in validWnds:
            (l, t, w, h,) = (wnd.left,
             wnd.top,
             wnd.width,
             wnd.height)
            if l in (0, leftOffset):
                wndsOnLeft.append(wnd)
            elif l in (16, leftOffset + 16):
                wndsOnLeftOffset.append(wnd)
            if l + w in (desktopWidth, desktopWidth - rightOffset):
                wndsOnRight.append(wnd)
            elif l + w in (desktopWidth - 16, desktopWidth - rightOffset - 16):
                wndsOnRightOffset.append(wnd)

        self.LogInfo('Neocom.PrepareForWindowPush', wndsOnLeft, wndsOnLeftOffset, wndsOnRight, wndsOnRightOffset, 'canWait', canWait)
        return (wndsOnLeft,
         wndsOnLeftOffset,
         wndsOnRight,
         wndsOnRightOffset)



    def UpdateWindowPush(self, windowData, setNeoWidth = None, action = None, time = 150.0):
        self.updatingWindowPush = True
        try:
            autoHide = settings.user.windows.Get('neoautohide', 0)
            if self.wnd and setNeoWidth is not None:
                onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
                imBig = settings.user.windows.Get('neowidth', 1)
                self.wnd.SetAlign([uiconst.TORIGHT, uiconst.TOLEFT][onLeft])
                if onLeft:
                    self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderRight.png', 'res:/UI/Texture/Shared/expanderLeft.png'][imBig])
                else:
                    self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderLeft.png', 'res:/UI/Texture/Shared/expanderRight.png'][imBig])
                if autoHide:
                    self.AutoHide()
                elif uiutil.IsVisible(self.wnd):
                    if action and self.wnd.width != setNeoWidth:
                        eve.Message('NeoCom' + action)
                    uicore.effect.MorphUI(self.wnd, 'width', setNeoWidth, time)
                self.wnd.width = setNeoWidth
            if autoHide and getattr(self, 'isAutoExpanded', False):
                (leftOffset, rightOffset,) = self.GetSideOffset(ignoreAutoHide=True)
            else:
                (leftOffset, rightOffset,) = self.GetSideOffset(ignoreAutoHide=False)
            self.LogInfo('Neocom.UpdateWindowPush, leftOffset', leftOffset, 'rightOffset', rightOffset)
            if windowData:
                (wndsOnLeft, wndsOnLeftOffset, wndsOnRight, wndsOnRightOffset,) = windowData
                for wnd in wndsOnLeft:
                    self.LogInfo('Neocom.UpdateWindowPush, window on left', wnd.windowID)
                    uicore.effect.MorphUI(wnd, 'left', leftOffset, time)

                for wnd in wndsOnLeftOffset:
                    self.LogInfo('Neocom.UpdateWindowPush, window on left+16', wnd.windowID)
                    uicore.effect.MorphUI(wnd, 'left', leftOffset + 16, time)

                dw = uicore.desktop.width
                for wnd in wndsOnRight:
                    self.LogInfo('Neocom.UpdateWindowPush, window on right', wnd.windowID)
                    uicore.effect.MorphUI(wnd, 'left', dw - wnd.width - rightOffset, time)

                for wnd in wndsOnRightOffset:
                    self.LogInfo('Neocom.UpdateWindowPush, window on right+16', wnd.windowID)
                    uicore.effect.MorphUI(wnd, 'left', dw - wnd.width - rightOffset - 16, time)

            uicore.effect.MorphUI(uicore.layer.inflight, 'padLeft', leftOffset, time)
            uicore.effect.MorphUI(uicore.layer.station, 'padLeft', leftOffset, time)
            uicore.effect.MorphUI(uicore.layer.inflight, 'padRight', rightOffset, time)
            uicore.effect.MorphUI(uicore.layer.station, 'padRight', rightOffset, time)
            blue.pyos.synchro.SleepWallclock(int(time))

        finally:
            self.updatingWindowPush = False




    def GetSolarSystemTrace(self, itemID, altText = None):
        if util.IsStation(itemID):
            solarSystemID = cfg.stations.Get(itemID).solarSystemID
        else:
            solarSystemID = itemID
        try:
            (sec, col,) = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(solarSystemID), 1)
            col.a = 1.0
            securityLabel = "</b> <color=%s><hint='%s'>%s</hint></color>" % (util.StrFromColor(col), localization.GetByLabel('UI/Map/StarMap/SecurityStatus'), sec)
        except KeyError:
            self.LogError('Neocom failed to get security status for item', solarSystemID, 'displaying BROKEN')
            log.LogException()
            sys.exc_clear()
            securityLabel = ''
        constellationID = cfg.solarsystems.Get(solarSystemID).constellationID
        regionID = cfg.constellations.Get(constellationID).regionID
        if altText:
            solarSystemAlt = " alt='%s'" % altText
        else:
            solarSystemAlt = ''
        locationTrace = '<url=showinfo:%s//%s%s>%s</url>%s &lt; <url=showinfo:%s//%s>%s</url> &lt; <url=showinfo:%s//%s>%s</url>' % (const.typeSolarSystem,
         solarSystemID,
         solarSystemAlt,
         cfg.evelocations.Get(solarSystemID).locationName,
         securityLabel,
         const.typeConstellation,
         constellationID,
         cfg.evelocations.Get(constellationID).locationName,
         const.typeRegion,
         regionID,
         cfg.evelocations.Get(regionID).locationName)
        return locationTrace



    def UpdateNeocom(self, all = 1):
        if self.updating:
            return 
        self.updating = True
        try:
            if not eve.session.charid:
                return 
            if not self.inited:
                self.Initialize()
            if all:
                self.UpdateMenu()
                self.Position()
            self.wnd.state = uiconst.UI_NORMAL
            if self.locationInfo is None or self.locationInfo.destroyed:
                return 
            if not self.mainLocationInfo:
                self.locationInfo.Flush()
                self.criminalText = uicls.EveLabelSmall(name='criminalText', parent=self.locationInfo, left=FRAME_WIDTH, state=uiconst.UI_HIDDEN)
                listbtn = xtriui.ListSurroundingsBtn(parent=self.locationInfo, align=uiconst.TOPLEFT, pos=(-4, 9, 24, 24), showIcon=True)
                listbtn.hint = localization.GetByLabel('UI/Neocom/ListItemsInSystem')
                listbtn.sr.owner = self
                listbtn.sr.groupByType = 1
                listbtn.filterCurrent = 1
                listbtn.sr.itemID = eve.session.solarsystemid2
                listbtn.sr.typeID = const.typeSolarSystem
                self.listbtn = listbtn
                self.mainLocationInfo = uicls.EveCaptionMedium(name='caption', align=uiconst.TOPLEFT, parent=self.locationInfo, left=FRAME_WIDTH, top=8)
                self.sessionTimer = uicls.SessionTimeIndicator(parent=self.locationInfo, pos=(-4, -4, 24, 24), state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
                self.nearestLocationInfo = uicls.EveLabelMedium(name='nearestLocationInfo', parent=self.locationInfo, left=FRAME_WIDTH)
                self.sovLocationInfo = uicls.EveLabelMedium(name='sovLocationInfo', hint=localization.GetByLabel('UI/Neocom/Sovereignty'), parent=self.locationInfo, left=FRAME_WIDTH)
                self.occupancyLocationInfo = uicls.EveLabelMedium(name='occupancyLocationInfo', hint=localization.GetByLabel('UI/Neocom/Occupancy'), parent=self.locationInfo, left=FRAME_WIDTH)
                bgColor = (1, 1, 1, 0.15)
                self.routeContainer = uicls.Container(parent=self.locationInfo, align=uiconst.TOPLEFT, name='routeContainer', left=FRAME_WIDTH, width=NEOCOM_PANELWIDTH - FRAME_WIDTH - FRAME_WIDTH)
                self.routeContainer.headerParent = uicls.Container(parent=self.routeContainer, align=uiconst.TOTOP, padTop=16, padBottom=4)
                self.routeContainer.header = uicls.EveCaptionMedium(name='header', parent=self.routeContainer.headerParent)
                self.routeContainer.currentParent = uicls.Container(parent=self.routeContainer, align=uiconst.TOTOP, padBottom=12, height=19)
                self.routeContainer.currentTrace = uicls.EveLabelMedium(name='currentTrace', parent=self.routeContainer.currentParent, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=NEOCOM_PANELWIDTH - 16, lineSpacing=-0.15)
                uicls.Fill(parent=self.routeContainer.currentParent, color=bgColor)
                currentPointer = uicls.Sprite(parent=self.routeContainer.currentParent, texturePath='res:/UI/Texture/classes/LocationInfo/pointerDown.png', pos=(0, -10, 10, 10), state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT, color=bgColor, idx=0)
                import ccConst
                frame = uicls.Frame(parent=self.routeContainer.currentParent, frameConst=ccConst.FRAME_SOFTSHADE, color=(0, 0, 0, 0.25))
                frame.SetPadding(-5, -5, -5, -10)
                self.routeContainer.markersParent = uicls.Container(parent=self.routeContainer, align=uiconst.TOTOP)
                self.routeContainer.endParent = uicls.Container(parent=self.routeContainer, align=uiconst.TOBOTTOM, padTop=12, height=19)
                self.routeContainer.endTrace = uicls.EveLabelMedium(name='endTrace', parent=self.routeContainer.endParent, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=NEOCOM_PANELWIDTH - 16, lineSpacing=-0.15)
                uicls.Fill(parent=self.routeContainer.endParent, color=bgColor)
                self.routeContainer.endPointer = uicls.Sprite(parent=self.routeContainer.endParent, texturePath='res:/UI/Texture/classes/LocationInfo/pointerUp.png', pos=(0, -10, 10, 10), state=uiconst.UI_DISABLED, color=bgColor, idx=0)
                frame = uicls.Frame(parent=self.routeContainer.endParent, frameConst=ccConst.FRAME_SOFTSHADE, color=(0, 0, 0, 0.25))
                frame.SetPadding(-5, -5, -5, -10)
                self.tidiIndicator = uicls.tidiIndicator(parent=self.locationInfo, name='tidiIndicator', align=uiconst.TOPLEFT, pos=(0, 18, 24, 24))
                self.locationParent.UpdateStandardAppearance()
            if eve.session.solarsystemid2:
                self.UpdateAllLocationInfo()
            else:
                self.mainLocationInfo.state = uiconst.UI_HIDDEN
                self.listbtn.state = uiconst.UI_HIDDEN
            self.AutoHide()

        finally:
            self.updating = False




    def GetSolarSystemStatusText(self, systemStatus = None, returnNone = False):
        if systemStatus is None:
            systemStatus = sm.StartService('facwar').GetSystemStatus()
        xtra = ''
        if systemStatus == const.contestionStateCaptured:
            xtra = localization.GetByLabel('UI/Neocom/SystemLost')
        elif systemStatus == const.contestionStateVulnerable:
            xtra = localization.GetByLabel('UI/Neocom/Vulnerable')
        elif systemStatus == const.contestionStateContested:
            xtra = localization.GetByLabel('UI/Neocom/Contested')
        elif systemStatus == const.contestionStateNone and returnNone:
            xtra = localization.GetByLabel('UI/Neocom/Uncontested')
        return xtra



    def UpdateAllLocationInfo(self):
        self.UpdateCrimeInfo()
        self.UpdateMainLocationInfo()
        self.UpdateNearestOrStationLocationInfo()
        self.UpdateSOVLocationInfo()
        self.UpdateOccupancyLocationInfo()
        self.UpdateRouteInfo()



    def UpdateMainLocationInfo(self):
        if eve.session.solarsystemid2:
            solarSystemLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (const.typeSolarSystem,
             eve.session.solarsystemid2,
             localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=const.typeSolarSystem),
             cfg.evelocations.Get(eve.session.solarsystemid2).name)
            try:
                (sec, col,) = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(eve.session.solarsystemid2), 1)
                col.a = 1.0
                securityLabel = "</b> <color=%s><hint='%s'>%s</hint></color>" % (util.StrFromColor(col), localization.GetByLabel('UI/Map/StarMap/SecurityStatus'), sec)
            except KeyError:
                self.LogError('Neocom failed to get security status for item', eve.session.solarsystemid2, 'displaying BROKEN')
                log.LogException()
                sys.exc_clear()
                securityLabel = '</b>'
            if util.IsWormholeRegion(eve.session.regionid):
                locationTrace = ''
            else:
                locationTrace = "<fontsize=14> &lt; <url=showinfo:%s//%s alt='%s'>%s</url> &lt; <url=showinfo:%s//%s alt='%s'>%s</url></fontsize>" % (const.typeConstellation,
                 eve.session.constellationid,
                 localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=const.typeConstellation),
                 cfg.evelocations.Get(eve.session.constellationid).name,
                 const.typeRegion,
                 eve.session.regionid,
                 localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=const.typeRegion),
                 cfg.evelocations.Get(eve.session.regionid).name)
            self.mainLocationInfo.text = solarSystemLabel + securityLabel + locationTrace
            self.mainLocationInfo.state = uiconst.UI_NORMAL
            self.tidiIndicator.left = self.mainLocationInfo.left + self.mainLocationInfo.textwidth + 4
            solarsystemitems = sm.RemoteSvc('config').GetMapObjects(eve.session.solarsystemid2, 0, 0, 0, 1, 0)
            self.listbtn.sr.mapitems = solarsystemitems
            self.listbtn.solarsystemid = eve.session.solarsystemid2
            self.listbtn.sr.itemID = eve.session.solarsystemid2
            self.listbtn.sr.typeID = const.typeSolarSystem
            self.listbtn.state = uiconst.UI_NORMAL



    def UpdateNearestOrStationLocationInfo(self, nearestBall = None):
        infoSettings = self.GetLocationInfoSettings()
        nearestOrStationLabel = ''
        if 'nearest' in infoSettings and eve.session.solarsystemid2:
            if eve.session.stationid2:
                stationName = cfg.evelocations.Get(eve.stationItem.itemID).name
                nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (eve.stationItem.stationTypeID,
                 eve.stationItem.itemID,
                 localization.GetByLabel('UI/Generic/CurrentStation'),
                 stationName)
            else:
                nearestBall = nearestBall or self.GetNearestBall()
                if nearestBall:
                    self.nearby = nearestBall.id
                    slimItem = sm.StartService('michelle').GetItem(nearestBall.id)
                    if slimItem:
                        nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (slimItem.typeID,
                         slimItem.itemID,
                         localization.GetByLabel('UI/Neocom/Nearest'),
                         cfg.evelocations.Get(nearestBall.id).locationName)
                if self.locationTimer is None:
                    self.locationTimer = base.AutoTimer(1313, self.CheckNearest)
        if nearestOrStationLabel:
            self.nearestLocationInfo.text = nearestOrStationLabel
            self.nearestLocationInfo.state = uiconst.UI_NORMAL
        else:
            self.nearestLocationInfo.state = uiconst.UI_HIDDEN
        self.UpdateLocationInfoLayout()



    def UpdateOccupancyLocationInfo(self):
        infoSettings = self.GetLocationInfoSettings()
        occupancyLabel = ''
        if 'occupancy' in infoSettings and eve.session.solarsystemid2:
            facwarsys = sm.StartService('facwar').GetFacWarSystem(eve.session.solarsystemid2)
            if facwarsys:
                xtra = self.GetSolarSystemStatusText()
                facOwner = cfg.eveowners.Get(facwarsys.get('occupierID'))
                occupancyLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (facOwner.typeID,
                 facOwner.ownerID,
                 localization.GetByLabel('UI/Neocom/Occupancy'),
                 facOwner.name)
                if xtra:
                    occupancyLabel += ' ' + xtra
        if occupancyLabel:
            self.occupancyLocationInfo.text = occupancyLabel
            self.occupancyLocationInfo.state = uiconst.UI_NORMAL
        else:
            self.occupancyLocationInfo.state = uiconst.UI_HIDDEN
        self.UpdateLocationInfoLayout()



    def UpdateSOVLocationInfo(self):
        sovLabel = ''
        infoSettings = self.GetLocationInfoSettings()
        if 'sovereignty' in infoSettings and eve.session.solarsystemid2:
            ss = sm.RemoteSvc('stationSvc').GetSolarSystem(eve.session.solarsystemid2)
            if ss:
                solSovOwner = ss.factionID
                if solSovOwner is None:
                    sovInfo = sm.GetService('sov').GetSystemSovereigntyInfo(session.solarsystemid2)
                    if sovInfo:
                        solSovOwner = sovInfo.allianceID
                contestedState = ''
                if solSovOwner:
                    sovText = cfg.eveowners.Get(solSovOwner).name
                    contestedState = sm.GetService('sov').GetContestedState(session.solarsystemid2) or ''
                elif util.IsWormholeRegion(eve.session.regionid):
                    sovText = localization.GetByLabel('UI/Neocom/Unclaimable')
                else:
                    sovText = localization.GetByLabel('UI/Neocom/Unclaimed')
                sovLabel = "<url=localsvc:service=sov&method=GetSovOverview alt='%s'>%s</url> %s" % (localization.GetByLabel('UI/Neocom/Sovereignty'), sovText, contestedState)
        if sovLabel:
            self.sovLocationInfo.text = sovLabel
            self.sovLocationInfo.state = uiconst.UI_NORMAL
        else:
            self.sovLocationInfo.state = uiconst.UI_HIDDEN
        self.UpdateLocationInfoLayout()



    def UpdateRouteInfo(self, jumpChange = False):
        if not session.solarsystemid2:
            return 
        planetView = sm.GetService('viewState').IsViewActive('planet')
        autoPilotActive = sm.GetService('autoPilot').GetState()
        updatingRouteData = getattr(self, 'updatingRouteData', None)
        if updatingRouteData == (autoPilotActive, planetView, self.routeData):
            return 
        if not self.routeData:
            if self.routeContainer:
                self.routeContainer.Hide()
                self.routeContainer.markersParent.Flush()
                self.UpdateLocationInfoLayout()
            return 
        self.updatingRouteData = (autoPilotActive, planetView, self.routeData[:])
        numJumps = self._GetNumJumps(self.routeData)
        self.routeContainer.header.text = '%s <fontsize=13></b>%s %s' % (localization.GetByLabel('UI/InfoWindow/TabNames/Route'), numJumps, localization.GetByLabel('UI/Common/Jumps'))
        self.routeContainer.headerParent.height = self.routeContainer.header.height
        self.routeContainer.Show()
        infoSettings = self.GetLocationInfoSettings()
        if planetView or 'route' not in infoSettings:
            self.routeContainer.currentParent.Hide()
            self.routeContainer.markersParent.Hide()
            self.routeContainer.endParent.Hide()
        else:
            self.routeContainer.currentParent.Show()
            self.routeContainer.endParent.Show()
            self.routeContainer.markersParent.Show()
            currentTrace = self.routeContainer.currentTrace
            currentTrace.text = '<center>' + self.GetSolarSystemTrace(self.routeData[0], localization.GetByLabel('UI/Neocom/Autopilot/NextSystemInRoute'))
            self.routeContainer.currentParent.height = max(19, currentTrace.textheight + 4)
            waypoints = deque(sm.GetService('starmap').GetWaypoints())
            markersParent = self.routeContainer.markersParent
            doBlink = autoPilotActive and jumpChange
            routeIDs = []
            lastStationSystemID = None
            for (i, id,) in enumerate(self.routeData):
                isLast = i == len(self.routeData) - 1
                if util.IsSolarSystem(id) and not isLast and not util.IsSolarSystem(self.routeData[(i + 1)]):
                    continue
                if util.IsSolarSystem(id) and lastStationSystemID == id:
                    continue
                if util.IsStation(id):
                    lastStationSystemID = cfg.stations.Get(id).solarSystemID
                routeIDs.append(id)

            if len(markersParent.children):
                while markersParent.children and markersParent.children[0].solarSystemID != routeIDs[0]:
                    markersParent.children[0].Close()

            if len(markersParent.children) > len(routeIDs):
                for each in markersParent.children[len(routeIDs):]:
                    each.Close()

            (absWidth, absHeight,) = markersParent.GetAbsoluteSize()
            markerX = 0
            markerY = 0
            for (i, destinationID,) in enumerate(routeIDs):
                if waypoints and destinationID == waypoints[0]:
                    isWaypoint = True
                    waypoints.popleft()
                else:
                    isWaypoint = False
                if util.IsSolarSystem(destinationID):
                    isStation = False
                    solarSystemID = destinationID
                elif util.IsStation(destinationID):
                    isStation = True
                    solarSystemID = cfg.stations.Get(destinationID).solarSystemID
                else:
                    self.LogError('UpdateRouteInfo: Unknown item. I can only handle solar systems and stations, you gave me', destinationID)
                if len(markersParent.children) > i:
                    systemIcon = markersParent.children[i]
                    systemIcon.left = markerX
                    systemIcon.top = markerY
                    systemIcon.SetSolarSystemAndDestinationID(solarSystemID, destinationID)
                    systemIcon.SetIsWaypoint(isWaypoint)
                    systemIcon.SetIsStation(isStation)
                else:
                    systemIcon = uicls.AutopilotDestinationIcon(parent=markersParent, pos=(markerX,
                     markerY,
                     ROUTE_MARKERSIZE,
                     ROUTE_MARKERSIZE), solarSystemID=solarSystemID, isWaypoint=isWaypoint, isStation=isStation, destinationID=destinationID, idx=i)
                markerX += ROUTE_MARKERGAP + ROUTE_MARKERSIZE
                if markerX + ROUTE_MARKERSIZE > absWidth:
                    markerX = 0
                    markerY += ROUTE_MARKERGAP + ROUTE_MARKERSIZE
                lastSystemIcon = markersParent.children[-1]
                markersParent.height = markerY + ROUTE_MARKERSIZE
                self.routeContainer.height = sum((each.height + each.padTop + each.padBottom for each in self.routeContainer.children if each.state != uiconst.UI_HIDDEN))

            if len(routeIDs) > 1:
                endTrace = self.routeContainer.endTrace
                endTrace.text = '<center>' + self.GetSolarSystemTrace(routeIDs[-1], localization.GetByLabel('UI/Neocom/Autopilot/CurrentDestination'))
                self.routeContainer.endParent.height = max(19, endTrace.textheight + 4)
                self.routeContainer.endPointer.left = markerX - ROUTE_MARKERSIZE - ROUTE_MARKERGAP - 1
                self.routeContainer.endParent.Show()
            else:
                self.routeContainer.endParent.Hide()
        self.routeContainer.height = sum((each.height + each.padTop + each.padBottom for each in self.routeContainer.children if each.state != uiconst.UI_HIDDEN))
        self.UpdateLocationInfoLayout()
        self.updatingRouteData = None



    def _GetNumJumps(self, routeData):
        ids = []
        lastID = None
        for id in routeData:
            if util.IsStation(id):
                id = cfg.stations.Get(id).solarSystemID
            if id != lastID:
                ids.append(id)
            lastID = id

        numJumps = len(ids)
        if ids and ids[0] == session.solarsystemid2:
            numJumps -= 1
        return numJumps



    def UpdateCrimeInfo(self, charcrimes = None, corpcrimes = None):
        if getattr(self, 'criminalText', None) is None:
            return 
        if charcrimes is None:
            (charcrimes, corpcrimes,) = sm.GetService('michelle').GetCriminalFlagCountDown()
        if None in charcrimes or None in corpcrimes:
            criminalTimer = max(charcrimes.get(None, 0), corpcrimes.get(None, 0))
            labelPath = 'UI/Neocom/UpdateCriminalGlobalCriminal'
        elif charcrimes and corpcrimes:
            criminalTimer = max(max(charcrimes.values()), max(corpcrimes.values()))
            labelPath = 'UI/Neocom/UpdateCriminalAggression'
        elif charcrimes:
            criminalTimer = max(charcrimes.values())
            labelPath = 'UI/Neocom/UpdateCriminalAggression'
        elif corpcrimes:
            criminalTimer = max(corpcrimes.values())
            labelPath = 'UI/Neocom/UpdateCriminalAggression'
        else:
            criminalTimer = 0
        if criminalTimer > 0:
            self.criminalText.state = uiconst.UI_NORMAL
            self.criminalText.text = localization.GetByLabel(labelPath, countdownTimer=util.FmtTimeInterval(criminalTimer - blue.os.GetSimTime(), breakAt='min'))
            if uicore.uilib.mouseOver == self.criminalText:
                keystoprime = charcrimes.keys() + corpcrimes.keys()
                while None in keystoprime:
                    keystoprime.remove(None)

                cfg.eveowners.Prime(keystoprime)
                criminal = []
                if None in charcrimes:
                    string = localization.GetByLabel('UI/Neocom/CriminalFlagGlobal', timeLeft=util.FmtDate(charcrimes[None] - blue.os.GetSimTime(), 'ns'))
                    criminal.append(string)
                charcrimestr = []
                for (key, value,) in charcrimes.iteritems():
                    if key is not None:
                        string = localization.GetByLabel('UI/Neocom/CriminalFlagYourOrCorpCrimes', victim=cfg.eveowners.Get(key).name, timeLeft=util.FmtDate(value - blue.os.GetSimTime(), 'ns'))
                        charcrimestr.append(string)

                if charcrimestr:
                    criminal.append(localization.GetByLabel('UI/Neocom/YourCrimes'))
                    criminal += charcrimestr
                corpcrimestr = []
                for (key, value,) in corpcrimes.iteritems():
                    string = localization.GetByLabel('UI/Neocom/CriminalFlagYourOrCorpCrimes', victim=cfg.eveowners.Get(key).name, timeLeft=util.FmtDate(value - blue.os.GetSimTime(), 'ns'))
                    corpcrimestr.append(string)

                if corpcrimestr:
                    criminal.append(localization.GetByLabel('UI/Neocom/YourCorpsCrimes'))
                    criminal += corpcrimestr
                self.criminalText.hint = '<br>'.join(criminal)
                uicore.UpdateHint(self.criminalText)
            if not self.criminalTimer:
                self.criminalTimer = base.AutoTimer(1000, self.UpdateCrimeInfo)
        else:
            self.criminalText.hint = ''
            self.criminalText.state = uiconst.UI_HIDDEN
            self.criminalTimer = None



    def UpdateLocationInfoLayout(self):
        mainInfoTop = 16
        self.mainLocationInfo.top = mainInfoTop
        self.listbtn.top = mainInfoTop
        textY = self.mainLocationInfo.top + self.mainLocationInfo.textheight
        for textControl in (self.nearestLocationInfo, self.sovLocationInfo, self.occupancyLocationInfo):
            if textControl.state == uiconst.UI_HIDDEN:
                continue
            textControl.top = textY
            textY += textControl.height

        if self.routeContainer.state != uiconst.UI_HIDDEN:
            self.routeContainer.top = textY + 16
            textY = self.routeContainer.top + self.routeContainer.height
        self.locationParent.height = textY + FRAME_WIDTH



    def CheckNearest(self):
        if not eve.session.solarsystemid or not self.mainLocationInfo:
            self.locationTimer = None
            return 
        nearestBall = self.GetNearestBall()
        if nearestBall and self.nearby != nearestBall.id:
            self.UpdateNearestOrStationLocationInfo(nearestBall)



    def GetNearestBall(self, fromBall = None, getDist = 0):
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return 
        lst = []
        for (ballID, ball,) in ballPark.balls.iteritems():
            slimItem = ballPark.GetInvItem(ballID)
            if slimItem and slimItem.groupID in self.validNearBy:
                if fromBall:
                    dist = trinity.TriVector(ball.x - fromBall.x, ball.y - fromBall.y, ball.z - fromBall.z).Length()
                    lst.append((dist, ball))
                else:
                    lst.append((ball.surfaceDist, ball))

        lst.sort()
        if getDist:
            return lst[0]
        if lst:
            return lst[0][1]



    def FakeJump(self):
        if self.routeData:
            self.LoadRouteData(self.routeData[1:])



    def LoadRouteData(self, routeData = None):
        change = routeData != self.routeData
        if self.routeData:
            jumpChange = routeData == self.routeData[1:]
        else:
            jumpChange = False
        self.routeData = routeData
        uthread.new(self.UpdateRouteInfo, jumpChange)



    def SetLocationInfoState(self, active = 1):
        self.locationInfo.width = [0, 256][active]



    def StopAllBlink(self):
        for each in self.btns:
            if each is None or each.destroyed:
                continue
            if each.sr.blink:
                each.sr.blink.state = uiconst.UI_HIDDEN
                setattr(self, each.name + '_hint', None)

        self.blinkingBtns = {}



    def Blink(self, what, hint = None, force = 1, blinkcount = 3, frequency = 750, bright = 0):
        if not self.wnd:
            return 
        if not settings.user.windows.Get('neoblink', True):
            self.blinkingBtns[what] = 1
            return 
        while self.btnsready == 0:
            blue.pyos.synchro.SleepWallclock(250)

        self.OnAutohideEnter()
        for each in self.btns:
            if each is None or each.destroyed:
                continue
            if each.name == what:
                blink = self.GetBlink(each)
                if blink:
                    blink.state = uiconst.UI_DISABLED
                sm.GetService('ui').BlinkSpriteRGB(each.sr.blink, min(1.0, each.r * (1.0 + bright * 0.25)), min(1.0, each.g * (1.0 + bright * 0.25)), min(1.0, each.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)
                setattr(self, each.name + '_hint', hint)

        if what == 'undock':
            hilite = self.GetBlink(self.undockBlinker)
            hilite.state = uiconst.UI_DISABLED
            hilite.top = hilite.height = 0
            hilite.padBottom = -8
            sm.GetService('ui').BlinkSpriteRGB(self.undockBlinker.sr.blink, min(1.0, self.undockBlinker.r * (1.0 + bright * 0.25)), min(1.0, self.undockBlinker.g * (1.0 + bright * 0.25)), min(1.0, self.undockBlinker.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)
            self.Maximize()
        if what == 'clock':
            blink = self.GetBlink(self.clockparDeco)
            blink.state = uiconst.UI_DISABLED
            sm.GetService('ui').BlinkSpriteRGB(blink, min(1.0, self.clockparDeco.r * (1.0 + bright * 0.25)), min(1.0, self.clockparDeco.g * (1.0 + bright * 0.25)), min(1.0, self.clockparDeco.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)
        self.blinkingBtns[what] = 1



    def BlinkOff(self, what):
        for each in self.btns:
            if each is None or each.destroyed:
                continue
            if each.name == what and each.sr.blink:
                blink = self.GetBlink(each)
                if blink:
                    blink.state = uiconst.UI_HIDDEN
                setattr(self, each.name + '_hint', None)

        if what == 'undock':
            self.GetBlink(self.undockBlinker).state = uiconst.UI_HIDDEN
        if what == 'clock':
            self.GetBlink(self.clockparDeco).state = uiconst.UI_HIDDEN
        if self.blinkingBtns.has_key(what):
            del self.blinkingBtns[what]



    def BtnClick(self, btn, *args):
        eve.Message('NeocomButtonSelect')
        self.BlinkOff(btn.name)
        oldState = btn.state
        btn.state = uiconst.UI_DISABLED
        try:
            cmdstr = getattr(btn, 'cmdstr', None)
            if cmdstr:
                self.ExecuteCommand(btn.cmdstr)
            else:
                self.GetNeocomMenu(btn.name)

        finally:
            btn.state = oldState

        if not btn.destroyed:
            btn.SendMessage(uiconst.UI_MOUSEEXIT)



    def CmdMenuAction(self, action):
        self.ExecuteCommand(action)



    def ExecuteCommand(self, cmdstr):
        func = getattr(uicore.cmd, cmdstr, None)
        if func:
            func()



    def SetResetBtnTimer(self):
        self.btnresettimer = base.AutoTimer(1000, self.ResetBtns)



    def SetAutohideTimer(self):
        self.autohidetimer = base.AutoTimer(2000, self.AutoHide)



    def UpdateClock(self):
        if self.wnd is None or self.wnd.destroyed:
            self.clocktimer = None
            return 
        if self.clocktimer is None:
            self.clocktimer = base.AutoTimer(60000, self.UpdateClock)
        now = blue.os.GetWallclockTime()
        hours = localization.GetByLabel('/Carbon/UI/Common/DateTime/HoursAndMinutes', datetime=now)
        if settings.user.windows.Get('neowidth', 1):
            date = localization.GetByLabel('/Carbon/UI/Common/DateTime/DateLongNone', datetime=now)
            self.clock.text = hours
            self.dateText.text = date
            self.dateText.fontsize = fontConst.EVE_SMALL_FONTSIZE
            self.dateText.top = self.clock.top + self.clock.textheight - 2
        else:
            day = localization.GetByLabel('/Carbon/UI/Common/DateTime/DateDay', datetime=now)
            self.clock.text = hours
            self.dateText.text = day
            self.dateText.fontsize = fontConst.EVE_LARGE_FONTSIZE
            self.dateText.top = self.clock.top + self.clock.textheight - 5



    def ResetBtns(self, smooth = 1):
        buttonHeight = self.GetButtonHeight()
        uthread.new(self.NewReset, buttonHeight, smooth)
        self.wnd.state = uiconst.UI_NORMAL
        self.btnresettimer = None



    def NewReset(self, bh, smooth):
        if smooth:
            bySizeBig = uiutil.SortListOfTuples([ (btn.height, btn) for btn in self.btns if btn.height > bh ])
            bySizeSmall = uiutil.SortListOfTuples([ (btn.height, btn) for btn in self.btns if btn.height < bh ])
            self.stopbtnreset = 0
            while 1 and not self.stopbtnreset:
                if bySizeBig:
                    bbtn = bySizeBig.pop(0)
                    bbtn.height -= 1
                    if bbtn.height > bh:
                        bySizeBig.append(bbtn)
                    if bySizeSmall:
                        sbtn = bySizeSmall.pop(0)
                        sbtn.height += 1
                        if sbtn.height < bh:
                            bySizeSmall.append(sbtn)
                else:
                    for btn in self.btns:
                        if btn.height < bh:
                            btn.height += 1

                allDone = 1
                for btn in self.btns:
                    if btn.height != bh:
                        allDone = 0
                        break

                if allDone:
                    break
                blue.pyos.synchro.Yield()

        else:
            for btn in self.btns:
                btn.height = bh




    def BtnEnter(self, btn, *args):
        self.stopbtnreset = 1
        buttonHeight = self.GetButtonHeight()
        btn.sr.hint = ''
        btn.sr.hintAbTop = None
        btn.sr.hintAbLeft = None
        btn.sr.hintAbBottom = None
        btn.sr.hintAbRight = None
        eve.Message('NeocomButtonEnter')
        self.autohidetimer = None
        if btn.name not in ('cq', 'undock'):
            btn.sr.selection.state = uiconst.UI_DISABLED
        hint = btn.displayName
        cmdstr = getattr(btn, 'cmdstr', None)
        if cmdstr:
            cmdshortcut = uicore.cmd.GetShortcutByString(cmdstr)
            if cmdshortcut is not None:
                hint = localization.GetByLabel('UI/Neocom/NeocomBtnHintWithShortcut', btnDisplayName=btn.displayName, shortcut=cmdshortcut)
        if btn.name == 'wallet':
            uthread.new(self.GetWalletHint, btn)
            return 
        if btn.name == 'charactersheet':
            skill = sm.GetService('skills').SkillInTraining()
            if skill is None:
                hint = localization.GetByLabel('UI/Neocom/CharacterSheetBtnHintNotTraining', btnNameAndShortcut=hint)
            elif sm.GetService('godma').GetStateManager().HasTrainingTimeForSkill(skill.itemID):
                if skill.skillTrainingEnd is None:
                    hint = localization.GetByLabel('UI/Neocom/CharacterSheetBtnHintNotTraining', btnNameAndShortcut=hint)
                else:
                    timeUntilDone = long(skill.skillTrainingEnd - blue.os.GetWallclockTime())
                    if timeUntilDone < const.SEC:
                        finishTime = localization.GetByLabel('UI/Neocom/CompletionImminent')
                    else:
                        finishTime = util.FmtTimeInterval(timeUntilDone, breakAt='sec')
                    hint = localization.GetByLabel('UI/Neocom/CharacterSheetBtnTrainingSkill', btnNameAndShortcut=hint, skillName=skill.name, skillLevel=skill.skillLevel + 1, finishTime=finishTime)
            else:
                hint = localization.GetByLabel('UI/Neocom/CharacterSheetBtnTrainingSkillLoading', btnNameAndShortcut=hint, skillName=skill.name, skillLevel=skill.skillLevel + 1)
                uthread.new(self.RefreshSkillTrainingTime)
            if settings.user.windows.Get('neowidth', 1) == 1:
                btn.hint = hint
        self.UpdateHint(btn, hint)
        btn.sr.timer = base.AutoTimer(250, self.ResetHilite, btn)



    def UpdateHint(self, btn, hint):
        blinkhint = getattr(self, btn.name + '_hint', None)
        if blinkhint:
            hint = localization.GetByLabel('UI/Neocom/NeocomBtnHintWithBlinkHint', hint=hint, blinkhint=blinkhint)
        left = settings.user.windows.Get('neoalign', 'left') == 'left'
        if settings.user.windows.Get('neowidth', 1) != 1:
            btn.hint = hint
            btn.sr.hintAbTop = btn.absoluteTop
            (xtraLeft, xtraRight,) = self.GetSideOffset()
            if left:
                btn.sr.hintAbLeft = xtraLeft
            else:
                btn.sr.hintAbRight = uicore.desktop.width - xtraRight



    def GetWalletHint(self, btn):
        walletSvc = sm.GetService('wallet')
        personalWealth = util.FmtISK(walletSvc.GetWealth())
        canAccess = walletSvc.HaveReadAccessToCorpWalletDivision(session.corpAccountKey)
        btnName = btn.displayName
        cmdstr = getattr(btn, 'cmdstr', None)
        if cmdstr:
            cmdshortcut = uicore.cmd.GetShortcutByString(cmdstr)
            if cmdshortcut is not None:
                btnName = localization.GetByLabel('UI/Neocom/NeocomBtnHintWithShortcut', btnDisplayName=btn.displayName, shortcut=cmdshortcut)
        if canAccess:
            corpWealth = util.FmtISK(walletSvc.GetCorpWealth(session.corpAccountKey))
            hint = localization.GetByLabel('UI/Neocom/WalletBtnHintCorp', btnNameAndShortcut=btnName, iskWealth=personalWealth, corpWealth=corpWealth)
        else:
            hint = localization.GetByLabel('UI/Neocom/WalletBtnHintPersonal', btnNameAndShortcut=btnName, iskWealth=personalWealth)
        if settings.user.windows.Get('neowidth', 1) == 1:
            btn.hint = hint
        self.UpdateHint(btn, hint)
        btn.sr.timer = base.AutoTimer(250, self.ResetHilite, btn)



    def RefreshSkillTrainingTime(self):
        skill = sm.GetService('skills').SkillInTraining()
        if skill is not None:
            return skill.skillTrainingEnd



    def ResetHilite(self, btn, *args):
        pass



    def BtnExit(self, btn, *args):
        if btn.name not in ('cq', 'undock'):
            btn.sr.selection.state = uiconst.UI_HIDDEN
        self.SetResetBtnTimer()
        if settings.user.windows.Get('neoautohide', 0):
            self.SetAutohideTimer()
        btn.sr.timer = None



    def MainEnter(self, *args):
        self.autohidetimer = None



    def MainExit(self, *args):
        if settings.user.windows.Get('neoautohide', 0):
            self.SetAutohideTimer()



    def GetSideOffset(self, ignoreAutoHide = False):
        xtraLeft = 0
        xtraRight = 0
        if eve.session.charid:
            if not ignoreAutoHide:
                autoHideMode = settings.user.windows.Get('neoautohide', 0)
            else:
                autoHideMode = False
            onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
            isBig = settings.user.windows.Get('neowidth', 1)
            if autoHideMode:
                size = 0
            elif isBig:
                size = EXPANDED_SIZE
            else:
                size = COLLAPSED_SIZE
            if onLeft:
                xtraLeft += size
            else:
                xtraRight += size
        mb = form.MapBrowserWnd.GetIfOpen()
        if mb and mb.state != uiconst.UI_HIDDEN:
            if mb.GetAlign() == uiconst.TOLEFT:
                xtraLeft += mb.width
            else:
                xtraRight += mb.width
        return (xtraLeft, xtraRight)



    def GetMainMenu(self):
        m = []
        if settings.user.windows.Get('neoalign', 'left') == 'left':
            m.append((localization.GetByLabel('UI/Neocom/AlignRight'), self.ChangeAlign, ('right',)))
        else:
            m.append((localization.GetByLabel('UI/Neocom/AlignLeft'), self.ChangeAlign, ('left',)))
        neoautohide = settings.user.windows.Get('neoautohide', 0)
        m.append(([localization.GetByLabel('UI/Neocom/AutohideOn'), localization.GetByLabel('UI/Neocom/AutohideOff')][(neoautohide == 1)], self.ChangeConfig, ('neoautohide', neoautohide != 1)))
        neoblink = settings.user.windows.Get('neoblink', True)
        blinkText = localization.GetByLabel('UI/Neocom/ConfigBlinkOn') if not neoblink else localization.GetByLabel('UI/Neocom/ConfigBlinkOff')
        m.append((blinkText, self.ChangeConfig, ('neoblink', not neoblink)))
        m.append((localization.GetByLabel('UI/Neocom/ConfigureSubmenu'), ('isDynamic', self.ConfigureNeocom, ())))
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            m.append(None)
            m += [('Toggle Insider', lambda : sm.StartService('insider').Toggle(forceShow=True))]
            m += [('Reload Insider', lambda : sm.StartService('insider').Reload())]
        return m



    def ConfigureLocationInfo(self):
        label = localization.GetByLabel('UI/Neocom/ConfigureWoldInfoText')
        setting = 'neocomLocationInfo_3'
        valid = ['nearest',
         'occupancy',
         'sovereignty',
         'signature',
         'route']
        current = self.GetLocationInfoSettings()
        itemmapping = [util.KeyVal(name='nearest', label='%s / %s' % (localization.GetByLabel('UI/Neocom/Nearest'), localization.GetByLabel('UI/Neocom/DockedIn'))),
         util.KeyVal(name='occupancy', label=localization.GetByLabel('UI/Neocom/Occupancy')),
         util.KeyVal(name='sovereignty', label=localization.GetByLabel('UI/Neocom/Sovereignty')),
         util.KeyVal(name='signature', label=localization.GetByLabel('UI/Neocom/LocusSignature')),
         util.KeyVal(name='route', label=localization.GetByLabel('UI/InfoWindow/TabNames/Route'))]
        self.ConfigureNeocomOptions(label, setting, valid, (itemmapping, current))



    def GetLocationInfoSettings(self):
        inView = settings.user.windows.Get('neocomLocationInfo_3', None)
        if inView is None:
            inView = ['nearest',
             'occupancy',
             'sovereignty',
             'signature',
             'route']
        return inView



    def ConfigureNeocom(self, *args):
        m = []
        m.append((localization.GetByLabel('UI/Neocom/AccessoriesBtn'), self.ConfigureNeocomIcons, ('accessories',)))
        m.append((localization.GetByLabel('UI/Neocom/ServicesBtn'), self.ConfigureNeocomIcons, ('stationservices',)))
        m.append((localization.GetByLabel('UI/Neocom/WorldInformationMenuOption'), self.ConfigureLocationInfo))
        return m



    def ConfigureNeocomOptions(self, hlabel, setting, valid, current):
        format = [{'type': 'btline'},
         {'type': 'text',
          'text': hlabel,
          'frame': 1},
         {'type': 'btline'},
         {'type': 'push',
          'frame': 1}]
        (iconMapping, inView,) = current
        for info in iconMapping:
            if info.name not in valid:
                continue
            format.append({'type': 'checkbox',
             'setvalue': bool(info.name in inView),
             'key': info.name,
             'label': '_hide',
             'required': 1,
             'text': info.label,
             'frame': 1,
             'onchange': self.ConfigCheckboxChange})

        format += [{'type': 'push',
          'frame': 1}, {'type': 'bbline'}]
        caption = localization.GetByLabel('UI/Neocom/UpdateLocationSettings')
        retval = uix.HybridWnd(format, caption, 1, buttons=uiconst.OKCANCEL, minW=240, minH=100, icon='ui_2_64_16', unresizeAble=1)
        if retval:
            newsettings = []
            for (k, v,) in retval.iteritems():
                if v == 1:
                    newsettings.append(k)

            settings.user.windows.Set(setting, newsettings)
            self.StopAllBlink()
            self.Blink(setting[6:].lower())
            self.UpdateNeocom()
            self.AutoHide()



    def ConfigCheckboxChange(self, checkbox, *args):
        if checkbox.data['key'] in ('nearest', 'occupancy', 'sovereignty', 'signature', 'route'):
            current = self.GetLocationInfoSettings()
            if checkbox.GetValue():
                if checkbox.data['key'] not in current:
                    current.append(checkbox.data['key'])
            elif checkbox.data['key'] in current:
                current.remove(checkbox.data['key'])
            settings.user.windows.Set('neocomLocationInfo_3', current)
            self.UpdateAllLocationInfo()



    def ConfigureNeocomIcons(self, option = 'accessories', *args):
        label = localization.GetByLabel('UI/Neocom/ConfigureCategoryText', category=self.GetIconMappings(option).label)
        setting = 'neocom%s' % option.capitalize()
        (iconMapping, inUtils, inStationServices,) = self.GetIconMapping('name', True)
        if option == 'accessories':
            valid = ['notepad',
             'calculator',
             'browser',
             'jukebox',
             'log']
            current = (iconMapping, inUtils)
        if option == 'stationservices':
            valid = [ each.name for each in sm.StartService('station').GetStationServiceInfo() ]
            current = (iconMapping, inStationServices)
        self.ConfigureNeocomOptions(label, setting, valid, current)



    def ChangeConfig(self, configname, value):
        settings.user.windows.Set(configname, value)
        if configname == 'neoautohide':
            if value:
                self.AutoHide()
            else:
                self.ExpandAutoHide()
        if configname == 'neoblink':
            if value:
                for each in self.blinkingBtns:
                    self.Blink(each, force=0)

            else:
                for each in self.btns:
                    if each.destroyed:
                        continue
                    blink = self.GetBlink(each)
                    if blink:
                        blink.Hide()




    def OnAutohideEnter(self, *args):
        uthread.new(self.ExpandAutoHide)



    def ExpandAutoHide(self):
        imBig = settings.user.windows.Get('neowidth', 1)
        if imBig:
            setWidth = EXPANDED_SIZE
        else:
            setWidth = COLLAPSED_SIZE
        if self.wnd.width != setWidth:
            windowData = self.PrepareForWindowPush()
            self.isAutoExpanded = True
            uicore.effect.MorphUI(self.wnd, 'width', setWidth, 150.0, newthread=False)
            eve.Message('NeoComIn')
            self.UpdateWindowPush(windowData)



    def AutoHide(self):
        if not settings.user.windows.Get('neoautohide', 0):
            return 
        mo = uicore.uilib.mouseOver
        if uiutil.IsUnder(mo, self.wnd):
            return 
        self.LogInfo('Neocom.AutoHide')
        windowData = self.PrepareForWindowPush()
        self.isAutoExpanded = False
        if self.wnd.width != 2:
            uicore.effect.MorphUI(self.wnd, 'width', 2, 150.0, newthread=False)
            eve.Message('NeoComOut')
        self.UpdateWindowPush(windowData)
        self.autohidetimer = None



    def ChangeAlign(self, align):
        windowData = self.PrepareForWindowPush()
        settings.user.windows.Set('neoalign', align)
        self.Position(windowData=windowData)



    def CharPicEnter(self, *args):
        self.autohidetimer = None



    def CharPicExit(self, *args):
        if settings.user.windows.Get('neoautohide', 0):
            self.SetAutohideTimer()



    def ExpanderClick(self, *args):
        windowData = self.PrepareForWindowPush()
        settings.user.windows.Set('neowidth', not settings.user.windows.Get('neowidth', 1))
        self.Position(action=('Out', 'In')[settings.user.windows.Get('neowidth', 1)], windowData=windowData)



    def Minimize(self):
        if settings.user.windows.Get('neowidth', 1):
            windowData = self.PrepareForWindowPush()
            settings.user.windows.Set('neowidth', 0)
            self.Position(action='Out', windowData=windowData)



    def Maximize(self):
        if not settings.user.windows.Get('neowidth', 1):
            settings.user.windows.Set('neowidth', 1)
            self.Position(action='In')



    def ShowSkillNotification(self, skillTypeIDs):
        (leftSide, rightSide,) = self.GetSideOffset()
        sm.GetService('skills').ShowSkillNotification(skillTypeIDs, leftSide + 14)



    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            self.UpdateAllLocationInfo()



    def DropInHangar(self, dragObj, nodes, *args):
        inv = []
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                if cfg.IsShipFittingFlag(node.rec.flagID):
                    if node.rec.categoryID == const.categoryCharge:
                        dogmaLocation.UnloadChargeToContainer(node.rec.locationID, node.rec.itemID, (const.containerHangar,), const.flagHangar)
                    else:
                        dogmaLocation.UnloadModuleToContainer(node.rec.locationID, node.rec.itemID, (const.containerHangar,), const.flagHangar)
                else:
                    locationID = node.rec.locationID
                    inv.append(node.itemID)

        if inv:
            sm.GetService('invCache').GetInventoryFromId(const.containerHangar).MultiAdd(inv, locationID, flag=const.flagHangar)




class ListSurroundingsBtn(uicls.Container):
    __guid__ = 'xtriui.ListSurroundingsBtn'
    __update_on_reload__ = 1
    default_name = 'ListSurroundingsBtn'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.expandOnLeft = 1
        self.itemssorted = 0
        self.filterCurrent = 1
        if attributes.showIcon:
            self.icon = uicls.MenuIcon(parent=self, size=24, ignoreSize=True, state=uiconst.UI_DISABLED)
        else:
            self.icon = None



    def GetInt(self, string):
        value = filter(lambda x: x in '0123456789', string)
        try:
            value = int(value)
        except:
            sys.exc_clear()
        return value



    def CelestialMenu(self, *args):
        return sm.GetService('menu').CelestialMenu(*args)



    def ExpandCelestial(self, mapItem):
        return sm.GetService('menu').CelestialMenu(mapItem.itemID, mapItem=mapItem)



    def ExpandTypeMenu(self, items):
        systemName = cfg.evelocations.Get(items[0].locationID).locationName
        expression = re.compile('%s (?P<roman>[XIV]*)(?P<typeName>\\D*)(?P<sequence>\\d*)' % systemName)
        typemenu = []
        for item in items:
            if item.groupID == const.groupStation:
                name = cfg.evelocations.Get(item.itemID).name
                entryName = uix.EditStationName(name, 1)
            elif item.groupID == const.groupStargate:
                entryName = cfg.evelocations.Get(item.itemID).locationName
                typemenu.append((entryName.lower(), (entryName, ('isDynamic', self.ExpandCelestial, (item,)))))
                continue
            else:
                entryName = item.itemName or 'no name!'
            escapeSorter = roman = typeName = None
            sequence = ''
            sorter = expression.match(item.itemName)
            if sorter:
                (roman, typeName, sequence,) = sorter.groups()
            else:
                escapeSorter = item.itemName
            typemenu.append(((util.RomanToInt(roman) if roman is not None else escapeSorter, typeName if typeName is not None else 1, int(sequence) if sequence != '' else 1), (entryName, ('isDynamic', self.ExpandCelestial, (item,)))))

        typemenu = uiutil.SortListOfTuples(typemenu)
        return typemenu



    def GetMenu(self, *args):
        if eve.rookieState and eve.rookieState < 32:
            return []
        m = []
        if self.sr.Get('groupByType', 0):
            typedict = {}
            if self.sr.typeID and self.sr.itemID:
                m += [(localization.GetByLabel('UI/Commands/ShowInfo'), sm.GetService('menu').ShowInfo, (self.sr.typeID, self.sr.itemID))]
            menuItems = {const.groupAsteroidBelt: 'UI/Common/LocationTypes/AsteroidBelts',
             const.groupPlanet: 'UI/Common/LocationTypes/Planets',
             const.groupStargate: 'UI/Common/LocationTypes/Stargates',
             const.groupStation: 'UI/Common/LocationTypes/Stations'}
            for item in self.sr.mapitems:
                if item.groupID in (const.groupMoon, const.groupSun, const.groupSecondarySun):
                    continue
                labelPath = menuItems[item.groupID]
                name = localization.GetByLabel(labelPath)
                if not typedict.has_key(name):
                    typedict[name] = []
                typedict[name].append(item)

            sortkeys = uiutil.SortListOfTuples([ [typename, typename] for typename in typedict.iterkeys() ])
            for key in sortkeys:
                m.append((key, ('isDynamic', self.ExpandTypeMenu, (typedict[key],))))

            bookmarks = {}
            folders = {}
            (b, f,) = sm.GetService('bookmarkSvc').GetBookmarksAndFolders()
            bookmarks.update(b)
            folders.update(f)
            bookmarkMenu = bookmarkUtil.GetBookmarkMenuForSystem(bookmarks, folders)
            if bookmarkMenu:
                m += [None, (localization.GetByLabel('UI/Neocom/MyPlacesSubmenu'), self.DoNothing)] + bookmarkMenu
            agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
            if agentMenu:
                agentMenu2 = []
                for (missionName, bms, agentID,) in agentMenu:
                    agentMenuText = localization.GetByLabel('UI/Neocom/MissionNameSubmenu', missionName=missionName, agent=agentID)
                    tmp = [agentMenuText, []]
                    for bm in bms:
                        if bm.solarsystemID == eve.session.solarsystemid2:
                            txt = bm.hint
                            systemName = cfg.evelocations.Get(bm.solarsystemID).name
                            if bm.locationType == 'dungeon':
                                txt = txt.replace(' - %s' % systemName, '')
                            if '- Moon ' in txt:
                                txt = txt.replace(' - Moon ', ' - M')
                            if txt.endswith('- '):
                                txt = txt[:-2]
                            tmp[1].append((txt, ('isDynamic', self.CelestialMenu, (bm.itemID,
                               None,
                               None,
                               0,
                               None,
                               None,
                               bm))))

                    if tmp[1]:
                        agentMenu2.append(tmp)

                if agentMenu2:
                    agentMenuText = localization.GetByLabel('UI/Neocom/AgentMissionsSubmenu')
                    m += [None, (agentMenuText, self.DoNothing)] + agentMenu2
            contractsMenu = sm.GetService('contracts').GetContractsBookmarkMenu()
            if contractsMenu:
                m += contractsMenu
        elif not self.itemssorted:
            self.sr.mapitems = uiutil.SortListOfTuples([ (item.itemName.lower(), item) for item in self.sr.mapitems ])
            self.itemssorted = 1
        maxmenu = 25
        if len(self.sr.mapitems) > maxmenu:
            groups = []
            approxgroupcount = len(self.sr.mapitems) / float(maxmenu)
            counter = 0
            while counter < len(self.sr.mapitems):
                groups.append(self.sr.mapitems[counter:(counter + maxmenu)])
                counter = counter + maxmenu

            for group in groups:
                groupmenu = []
                for item in group:
                    groupmenu.append((item.itemName or 'no name!', self.CelestialMenu(item.itemID, item)))

                if len(groupmenu):
                    fromLetter = '???'
                    if group[0].itemName:
                        fromLetter = group[0].itemName[0]
                    toLetter = '???'
                    if group[-1].itemName:
                        toLetter = group[-1].itemName[0]
                    m.append((fromLetter + '...' + toLetter, groupmenu))

            return m
        for item in self.sr.mapitems[:30]:
            m.append((item.itemName or 'no name!', self.CelestialMenu(item.itemID, item)))

        m.append(None)
        starmapSvc = sm.GetService('starmap')
        showRoute = settings.user.ui.Get('neocomRouteVisible', 1)
        infoSettings = sm.GetService('neocom').GetLocationInfoSettings()
        if 'route' in infoSettings:
            m.append((localization.GetByLabel('UI/Neocom/HideAutopilotRoute'), self.ShowHideRoute, (0,)))
        else:
            m.append((localization.GetByLabel('UI/Neocom/ShowAutopilotRoute'), self.ShowHideRoute, (1,)))
        if len(starmapSvc.GetWaypoints()) > 0:
            m.append(((localization.GetByLabel('UI/Neocom/ClearAllAutopilotWaypoints'), None), starmapSvc.ClearWaypoints, (None,)))
        return m



    def ShowHideRoute(self, show = 1):
        current = sm.GetService('neocom').GetLocationInfoSettings()
        if show:
            if 'route' not in current:
                current.append('route')
        elif 'route' in current:
            current.remove('route')
        settings.user.windows.Set('neocomLocationInfo_3', current)
        sm.GetService('starmap').DecorateNeocom()



    def DoNothing(self):
        pass



    def DoWarpToHidden(self, instanceID):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.WarpToStuff('epinstance', instanceID)



    def DoTutorial(self):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None and sm.GetService('space').CanWarp(forTut=True):
            eve.Message('Command', {'command': localization.GetByLabel('UI/Neocom/WarpingToTutorialSide')})
            bp.WarpToTutorial()



    def GetDragData(self, *args):
        itemID = self.sr.Get('itemID', None)
        typeID = self.sr.Get('typeID', None)
        if not itemID or not typeID:
            return []
        label = ''
        if typeID in (const.typeRegion, const.typeConstellation, const.typeSolarSystem):
            label += cfg.evelocations.Get(itemID).name
            elabel = {const.typeRegion: localization.GetByLabel('UI/Neocom/Region'),
             const.typeConstellation: localization.GetByLabel('UI/Neocom/Constellation'),
             const.typeSolarSystem: localization.GetByLabel('UI/Neocom/SolarSystem')}
            label += ' %s' % elabel.get(typeID)
        entry = util.KeyVal()
        entry.itemID = itemID
        entry.typeID = typeID
        entry.__guid__ = 'xtriui.ListSurroundingsBtn'
        entry.label = label
        return [entry]



    def OnMouseEnter(self, *args):
        if self.icon:
            self.icon.OnMouseEnter()



    def OnMouseExit(self, *args):
        if self.icon:
            self.icon.OnMouseExit()




class AutopilotDestinationIcon(uicls.Container):
    __guid__ = 'uicls.AutopilotDestinationIcon'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.fill = uicls.Fill(parent=self)
        self.wayPointIcon = None
        self.isWaypoint = None
        self.solarSystemID = None
        self.destinationID = None
        self.stationIcon = None
        self.isStation = None
        self.hiliteTimer = None
        self.SetSolarSystemAndDestinationID(attributes.solarSystemID, attributes.destinationID)
        self.SetIsWaypoint(attributes.isWaypoint)
        self.SetIsStation(attributes.isStation)



    def SetIsStation(self, isStation):
        if self.isStation == isStation:
            return 
        if isStation and not self.isStation:
            self.stationIcon = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/classes/LocationInfo/stationRoute.png', pos=(0, 0, 8, 8), state=uiconst.UI_DISABLED, idx=0)
        elif not isStation and self.stationIcon:
            self.stationIcon.Close()
            self.stationIcon = None
        self.isStation = isStation



    def SetIsWaypoint(self, isWaypoint):
        if self.isWaypoint == isWaypoint:
            return 
        if isWaypoint and not self.wayPointIcon:
            self.wayPointIcon = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/classes/LocationInfo/waypoint.png', pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, align=uiconst.CENTER, idx=0)
        elif not isWaypoint and self.wayPointIcon:
            self.wayPointIcon.Close()
            self.wayPointIcon = None
        self.isWaypoint = isWaypoint



    def SetSolarSystemAndDestinationID(self, solarSystemID, destinationID):
        if self.solarSystemID == solarSystemID and self.destinationID == destinationID:
            return 
        c = sm.GetService('map').GetSystemColor(solarSystemID)
        self.fill.SetRGB(c.r, c.g, c.b, IDLE_ROUTEMARKER_ALPHA)
        self.solarSystemID = solarSystemID
        self.destinationID = destinationID



    def OnMouseEnter(self, *args):
        uicore.animations.FadeTo(self.fill, startVal=self.fill.color.a, endVal=1.0, duration=0.125, loops=1)
        if self.hiliteTimer is None:
            self.hiliteTimer = base.AutoTimer(111, self.CheckIfMouseOver)



    def CheckIfMouseOver(self, *args):
        if uicore.uilib.mouseOver == self:
            return 
        uicore.animations.FadeTo(self.fill, startVal=self.fill.color.a, endVal=IDLE_ROUTEMARKER_ALPHA, duration=0.5, loops=1)
        self.hiliteTimer = None



    def OnMouseExit(self, *args):
        self.CheckIfMouseOver()



    def GetHint(self, *args):
        ret = sm.GetService('neocom').GetSolarSystemTrace(self.destinationID)
        if util.IsStation(self.destinationID):
            ret += '<br>' + cfg.evelocations.Get(self.destinationID).name
        return ret



    def GetMenu(self, *args):
        if util.IsSolarSystem(self.destinationID):
            return sm.GetService('menu').GetMenuFormItemIDTypeID(self.destinationID, const.typeSolarSystem)
        if util.IsStation(self.destinationID):
            station = sm.StartService('ui').GetStation(self.destinationID)
            return sm.GetService('menu').GetMenuFormItemIDTypeID(self.destinationID, station.stationTypeID)



    def OnClick(self, *args):
        if util.IsSolarSystem(self.destinationID):
            sm.GetService('info').ShowInfo(const.typeSolarSystem, self.destinationID)
        elif util.IsStation(self.destinationID):
            station = sm.StartService('ui').GetStation(self.destinationID)
            sm.GetService('info').ShowInfo(station.stationTypeID, self.destinationID)



    def GetDragData(self, *args):
        entry = util.KeyVal()
        entry.__guid__ = 'xtriui.ListSurroundingsBtn'
        entry.itemID = self.destinationID
        entry.label = cfg.evelocations.Get(self.destinationID).name
        if util.IsSolarSystem(self.destinationID):
            entry.typeID = const.typeSolarSystem
        else:
            station = sm.StartService('ui').GetStation(self.destinationID)
            entry.typeID = station.stationTypeID
        return [entry]




