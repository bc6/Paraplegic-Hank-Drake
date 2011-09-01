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
FRAME_WIDTH = 10
FRAME_SEPERATION = 30
BACKGROUND_COLOR = (0,
 0,
 0,
 0.1)
BUTTONHEIGHT = 30
MO = [3.5455531962,
 3.36937132567,
 2.59914513634,
 1.61375875964,
 0.63290495212,
 0.05177315618,
 0.0]
LOCATION_LINE_HEIGHT = 14

class NeocomContainer(uicls.Container):
    __guid__ = 'uicls.NeocomContainer'
    default_name = 'neocomContainer'
    default_padTop = FRAME_SEPERATION
    default_align = uiconst.TOTOP
    default_collapsable = False
    FRAME_PADDING = (-FRAME_WIDTH,
     -FRAME_WIDTH,
     -FRAME_WIDTH,
     -FRAME_WIDTH)

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.collapsable = attributes.get('collapsable', self.default_collapsable)
        if self.collapsable:
            self.collapseContainer = uicls.Container(parent=self, name='collapseContainer', align=uiconst.TOPRIGHT, pos=(0, 0, 15, 15), state=uiconst.UI_NORMAL)
            self.collapseIcon = uicls.Sprite(name='collapseIcon', parent=self.collapseContainer, texturePath='res:/UI/Texture/Shared/expanderUp.png', pos=(1, 2, 11, 11), hint=mls.UI_CMD_COLLAPSE)
            self.collapseHighlight = uicls.Fill(parent=self.collapseContainer, color=(1, 1, 1, 0.25), state=uiconst.UI_HIDDEN)
            self.collapseIcon.OnClick = self.ToggleCollapseState
            self.collapseIcon.OnMouseEnter = (self.CollapseButtonEnter, self.collapseIcon)
            self.collapseIcon.OnMouseExit = (self.CollapseButtonExit, self.collapseIcon)
            self.collapsed = False
        self.content = uicls.Container(parent=self, name='content', align=uiconst.TOALL)
        background = uicls.Container(parent=self, name='background', align=uiconst.TOALL, padding=self.FRAME_PADDING)
        uicls.Frame(parent=background, color=BACKGROUND_COLOR, name='backgroundFrame')
        uicls.Fill(parent=background, color=BACKGROUND_COLOR, name='backgroundColor')



    def ToggleCollapseState(self, discard = None):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.collapseIcon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
            self.collapseIcon.SetHint(mls.UI_CMD_EXPAND)
        else:
            self.collapseIcon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
            self.collapseIcon.SetHint(mls.UI_CMD_COLLAPSE)
        self.OnCollapse(self.collapsed)



    def CollapseButtonEnter(self, discard):
        self.collapseHighlight.state = uiconst.UI_DISABLED



    def CollapseButtonExit(self, discard):
        self.collapseHighlight.state = uiconst.UI_HIDDEN



    def OnCollapse(self, collaspsed):
        pass




class NeocomSvc(service.Service):
    __update_on_reload__ = 0
    __exportedcalls__ = {'Blink': [],
     'BlinkOff': [],
     'Position': [],
     'SetXtraText': [],
     'GetSideOffset': [],
     'Minimize': [],
     'Maximize': [],
     'UpdateMenu': [],
     'UpdateNeocom': [],
     'SetLocationInfoState': []}
    __guid__ = 'svc.neocom'
    __dependencies__ = ['settings']
    __notifyevents__ = ['OnSetDevice',
     'OnSessionChanged',
     'OnAggressionChanged',
     'ProcessRookieStateChange',
     'OnSystemStatusChanged',
     'OnSovereigntyChanged',
     'OnPostCfgDataChanged',
     'OnEntitySelectionChanged']

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



    def Stop(self, memStream = None):
        self.CloseNeocomLeftSide()
        if self.wnd is not None and not self.wnd.destroyed:
            self.wnd.Close()
            self.wnd = None
        self.Reset()



    def OnSystemStatusChanged(self, *args):
        if eve.session.charid:
            self.UpdateNeocom(0)



    def OnSovereigntyChanged(self, solarSystemID, allianceID):
        self.UpdateLocationText()



    def OnEntitySelectionChanged(self, entityID):
        self.UpdateLocationText()



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
            if settings.user.ui.Get('showSessionTimer', 0):
                uthread.new(self.UpdateChangeTimer)



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
            self.UpdateCriminal(charcrimes, corpcrimes)



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
        self.exitbtn = None
        self.clock = None
        self.clocktimer = None
        self.locationTimer = None
        self.btnresettimer = None
        self.lastLocationID = None
        self.updating = False
        self.pushUpdatePending = None
        self.pushUpdatePendingData = None
        self.updatingPush = False
        self.ahidden = 0
        self.activeshipicon = None
        self.activeshipname = None
        self.locationText = None
        self.extraText = None
        self.xtratext = ''
        self.destPathData = None
        self.destPathColorCont = None
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
        self.moving = False
        self.inited = 0
        self.criminalTimer = None



    def Initialize(self):
        for each in uicore.layer.main.children[:]:
            if each.name in ('neocom', 'locationInfo', 'neocomLeftSide'):
                each.Close()

        self.wnd = uicls.Container(parent=uicore.layer.neocom, idx=0, pos=(0,
         0,
         136,
         uicore.desktop.height), name='neocom', state=uiconst.UI_HIDDEN, align=uiconst.RELATIVE)
        autohideparent = uicls.Container(parent=self.wnd, name='autohideparent', state=uiconst.UI_PICKCHILDREN)
        autohidedetector = uicls.Container(parent=autohideparent, width=8, name='autohidedetector', state=uiconst.UI_NORMAL, align=uiconst.TOLEFT)
        maincontainer = uicls.Container(parent=self.wnd, padding=(2, 0, 2, 0), name='maincontainer', state=uiconst.UI_NORMAL)
        mainNameParent = uicls.Container(parent=maincontainer, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 128), state=uiconst.UI_NORMAL)
        expander = uicls.Sprite(parent=mainNameParent, name='expander', pos=(5, 5, 11, 11), align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderLeft.png')
        nameParent = uicls.Transform(parent=mainNameParent, pos=(-41, 52, 116, 28), name='nameParent', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        self.wnd.sr.charname = uicls.Label(text='', parent=nameParent, left=0, top=0, align=uiconst.TOPLEFT, width=100, fontsize=12, state=uiconst.UI_DISABLED)
        self.nameFill = uicls.Fill(name='nameFill', parent=mainNameParent, color=(0.0, 0.0, 0.0, 0.6))
        charpic = uicls.Sprite(parent=maincontainer, height=128, name='charactersheet', state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        clockpar = uicls.Container(parent=maincontainer, pos=(0, 0, 128, 16), name='clockpar', state=uiconst.UI_DISABLED, align=uiconst.TOBOTTOM)
        linepar = uicls.Container(parent=clockpar, pos=(0, 0, 2, 2), name='line', state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        uicls.Line(parent=linepar, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOBOTTOM, name='white')
        uicls.Line(parent=linepar, color=(0.0, 0.0, 0.0, 1.0), align=uiconst.TOBOTTOM, name='black')
        exitbtnParent = uicls.Container(parent=maincontainer, height=64, name='exitbtnParent', state=uiconst.UI_NORMAL, align=uiconst.TOBOTTOM)
        exitbtn = uicls.Container(parent=exitbtnParent, name='exitbtn', align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64))
        exitIcon = uicls.Icon(parent=exitbtn, icon='ui_9_64_6', state=uiconst.UI_DISABLED, align=uiconst.TOALL, ignoreSize=True, filter=True)
        self.wnd.sr.btnparent = uicls.Container(parent=maincontainer, name='btnparent', state=uiconst.UI_PICKCHILDREN, clipChildren=True, align=uiconst.TOALL)
        onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
        self.wnd.SetAlign([uiconst.TORIGHT, uiconst.TOLEFT][onLeft])
        BIG = settings.user.windows.Get('neowidth', 1) and not self.ahidden
        self.wnd.width = [[36, 2], [132, 2]][BIG][self.ahidden]
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
        self.clockparDeco.displayName = mls.UI_CAL_CALENDAR
        self.clock = uicls.Label(text='', parent=self.clockparDeco, left=0, top=3, align=uiconst.TOPLEFT, width=120, height=14, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, autowidth=False, autoheight=False)
        self.dateCont = uicls.Container(parent=self.clockparDeco, name='dateCont', align=uiconst.TOBOTTOM, pos=(0, 0, 0, 14), clipChildren=1)
        self.dateText = uicls.Label(text='', parent=self.dateCont, left=0, top=0, align=uiconst.TOPLEFT, width=120, height=14, letterspace=1, fontsize=14, state=uiconst.UI_DISABLED, uppercase=1, idx=0, autowidth=False, autoheight=False)
        self.autohidearea = autohidedetector
        self.autohidearea.OnMouseEnter = self.OnAutohideEnter
        self.exitbtn = exitbtn
        self.exitbtn.top = -4
        self.wnd.sr.exitbtnText = uicls.Label(text='', parent=uiutil.GetChild(self.wnd, 'exitbtnParent'), left=0, top=44, align=uiconst.CENTERTOP, width=100, height=14, letterspace=2, fontsize=11, state=uiconst.UI_DISABLED, uppercase=1, autowidth=False, autoheight=False)
        self.neocomLeftSide = uicls.Container(parent=uicore.layer.neocom, name='neocomLeftside', align=uiconst.TOLEFT, pos=(8, 0, 288, 0), padding=(16, 0, 0, 0))
        self.locationParent = uicls.NeocomContainer(parent=self.neocomLeftSide, name='locationInfo', padTop=10)
        self.locationParent.children[1].padTop = 0
        self.locationInfo = self.locationParent.content
        if settings.user.windows.Get('neoautohide', 0):
            self.AutoHide()
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            if settings.public.ui.Get('Insider', True):
                uthread.pool('neocom::ShowInsider', self.ShowInsider)
        self.inited = 1
        self.UpdateClock()
        uthread.pool('neocom::CheckSkills', self.CheckSkills)
        sm.GetService('ui').SortGlobalLayer()



    def ShowInsider(self):
        sm.GetService('insider').Show()



    def UpdateChangeTimer(self):
        if hasattr(self, 'changeTimer') and not self.changeTimer.destroyed:
            self.changeTimer.Close()
        TIMER_LENGTH = 30
        SEC = 10000000L
        self.changeTimer = uicls.Container(name='changeTimer', align=uiconst.TOPLEFT, parent=self.neocomLeftSide, pos=(self.solText.left + self.solText.textwidth,
         self.solText.top + 7,
         16,
         16), clipChildren=True, idx=0)
        changing = uicls.AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPLEFT, parent=self.changeTimer, pos=(-2, 0, 16, 16), state=uiconst.UI_NORMAL)
        changing.hint = mls.UI_GENERIC_SESSIONCHANGEHINT % {'time': util.FmtTimeInterval(TIMER_LENGTH * SEC, breakAt='sec')}
        changing.Play()
        t = blue.os.GetTime()
        while blue.os.GetTime() < t + TIMER_LENGTH * SEC:
            if hasattr(changing, 'hint'):
                changing.hint = mls.UI_GENERIC_SESSIONCHANGEHINT % {'time': util.FmtTimeInterval(int(t + TIMER_LENGTH * SEC) - blue.os.GetTime(), breakAt='sec')}
            blue.pyos.synchro.Sleep(500)
            if self.changeTimer.destroyed or changing.destroyed:
                return 

        changing.Stop()
        self.changeTimer.Close()



    def CheckSkills(self):
        skillInTraining = sm.GetService('skills').SkillInTraining()
        if skillInTraining:
            godma = sm.StartService('godma')
            endOfTraining = godma.GetStateManager().GetEndOfTraining(skillInTraining.itemID)
            godma.GetStateManager().endOfTraining[skillInTraining.itemID] = endOfTraining
        else:
            self.Blink('charactersheet')



    def GetLocationInfo(self):
        itemmapping = [['nearest', mls.UI_GENERIC_NEAREST],
         ['occupancy', mls.UI_SHARED_OCCUPANCY],
         ['sovereignty', mls.UI_SHARED_MAPSOVEREIGNTY],
         ['constellation', mls.UI_GENERIC_CONSTELLATION],
         ['region', mls.UI_GENERIC_REGION],
         ['signature', mls.UI_GENERIC_LOCUSSIGN],
         ['security', mls.UI_INFOWND_SECURITYLEVEL],
         ['station', mls.UI_SHARED_MAPDOCKEDIN]]
        inView = settings.user.windows.Get('neocomLocationInfo2', None)
        if inView is None:
            inView = [ each[0] for each in itemmapping ]
        return (itemmapping, inView)



    def GetIconMappings(self, btnname = None):
        mapping = [['charactersheet',
          'OpenCharactersheet',
          mls.UI_SHARED_CHARACTERSHEET,
          'ui_2_64_16',
          False],
         ['addressbook',
          'OpenPeopleAndPlaces',
          mls.UI_SHARED_PEOPLEANDPLACES,
          'ui_12_64_2',
          False],
         ['mail',
          'OpenMail',
          mls.UI_SHARED_EVEMAIL,
          'ui_94_64_8',
          False],
         ['fitting',
          'OpenFitting',
          mls.UI_GENERIC_FITTING,
          'ui_17_128_4',
          False],
         ['notepad',
          'OpenNotepad',
          mls.UI_SHARED_NOTEPAD,
          'ui_49_64_2',
          False],
         ['market',
          'OpenMarket',
          mls.UI_MARKET_MARKET,
          'ui_18_128_1',
          False],
         ['factories',
          'OpenFactories',
          mls.UI_RMR_SCIENCEANDINDUSTRY,
          'ui_57_64_9',
          False],
         ['contracts',
          'OpenContracts',
          mls.UI_CONTRACTS_CONTRACTS,
          'ui_64_64_10',
          False],
         ['map',
          'CmdToggleMap',
          mls.UI_SHARED_MAP,
          'ui_7_64_4',
          False],
         ['corporation',
          'OpenCorporationPanel',
          mls.UI_GENERIC_CORPORATION,
          'ui_7_64_6',
          False],
         ['assets',
          'OpenAssets',
          mls.UI_CORP_ASSETS,
          'ui_7_64_13',
          False],
         ['wallet',
          'OpenWallet',
          mls.UI_SHARED_WALLET,
          'ui_7_64_12',
          False],
         ['fleet',
          'OpenFleet',
          mls.UI_FLEET_FLEET,
          'ui_94_64_9',
          False],
         ['calculator',
          'OpenCalculator',
          mls.UI_GENERIC_CALCULATOR,
          'ui_49_64_1',
          False],
         ['browser',
          'OpenBrowser',
          mls.UI_SHARED_BROWSER,
          'ui_9_64_4',
          False],
         ['journal',
          'OpenJournal',
          mls.UI_GENERIC_JOURNAL,
          'ui_25_64_3',
          False],
         ['jukebox',
          'OpenJukebox',
          mls.UI_SHARED_JUKEBOX,
          'ui_12_64_5',
          False],
         ['log',
          'OpenLog',
          mls.UI_SHARED_LOG,
          'ui_34_64_4',
          False],
         ['accessories',
          None,
          mls.UI_CMD_ACCESSORIES,
          'ui_6_64_2',
          False],
         ['stationservices',
          None,
          mls.UI_GENERIC_SERVICES,
          'ui_76_64_2',
          False],
         ['navyoffices',
          'OpenMilitia',
          mls.UI_STATION_MILITIAOFFICE,
          'ui_61_128_3',
          False],
         ['help',
          'OpenHelp',
          mls.UI_SHARED_HELP,
          'ui_74_64_13',
          False],
         ['ships',
          'OpenShipHangar',
          mls.UI_GENERIC_SHIPS,
          'ui_9_64_5',
          True],
         ['items',
          'OpenHangarFloor',
          mls.UI_GENERIC_ITEMS,
          'ui_12_64_3',
          True]]
        newmapping = {}
        for (i, iconmap,) in enumerate(mapping):
            (lbl, cmdstr, label, icon, stationonly,) = iconmap
            newmapping[lbl] = (i,
             cmdstr,
             label,
             icon,
             stationonly)

        if btnname:
            return newmapping.get(btnname, None)
        return newmapping



    def GetIconMapping(self, sortBy = None, all = False):
        iconmapping = []
        icons = self.GetIconMappings()
        for (service, info,) in icons.iteritems():
            sortby = info[0]
            if sortBy == 'name':
                sortby = info[2]
            if eve.session.stationid and settings.user.windows.Get('dockshipsanditems', 0) and service in ('ships', 'items'):
                continue
            if service == 'navyoffices' and not sm.StartService('facwar').CheckStationElegibleForMilitia():
                continue
            if not info[4] or info[4] and session.stationid2:
                iconmapping.append((sortby, (service,
                  info[1],
                  info[2],
                  info[3],
                  info[4])))

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
            if info[4] == True:
                continue
            sortby = info[0]
            if sortBy == 'name':
                sortby = info[2]
            if not info[4] or all or info[4] and session.stationid:
                for serviceID in info[5]:
                    if not info[4] or all or eve.stationItem.serviceMask & serviceID == serviceID:
                        if service not in icons:
                            data = (sortby, (service,
                              info[1],
                              info[2],
                              info[3],
                              info[4]))
                            if data not in iconmapping:
                                iconmapping.append(data)


        inStationServices = settings.user.windows.Get('neocomStationservices', None)
        if inStationServices is None:
            inStationServices = [ service for (service, info,) in services.iteritems() if service not in icons if not info[4] ]
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
        for (name, cmdstr, displayName, iconNum, stationOnly,) in iconMapping:
            if name == 'accessories' and not inUtils:
                continue
            if name == 'stationservices' and not inStationServices:
                continue
            btn = self.GetButton(displayName, iconNum, btnpar)
            btn.name = name
            btn.cmdstr = cmdstr
            btn.OnClick = (self.BtnClick, btn)
            btn.OnMouseEnter = (self.BtnEnter, btn)
            btn.OnMouseExit = (self.BtnExit, btn)
            if name in ('accessories', 'stationservices'):
                if name == 'accessories' and inUtils:
                    btn.GetMenu = self.GetToolsMenu
                if name == 'stationservices' and inStationServices:
                    btn.GetMenu = self.GetStationServiceMenu
                btn.GetMenuPosition = self.ReturnMenuPos
                btn.expandOnLeft = 1
                btn.state = uiconst.UI_NORMAL
                menuArrow = uicls.Icon(icon='ui_38_16_228', parent=btn, size=16, idx=0, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED)
                btn.sr.menuArrow = menuArrow
                self.btns.append(btn)
                continue
            if name in inUtils or name in inStationServices:
                continue
            if name == 'jukebox':
                btn.GetMenu = self.GetJukeboxMenu
                btn.GetMenuPosition = self.ReturnMenuPos
            if name in ('items', 'ships'):
                btn.OnDropData = self.DropInHangar
            self.btns.append(btn)
            setattr(self, '%sbtn' % name, btn)
            btn.state = uiconst.UI_NORMAL

        if self.menubtn is not None and not self.menubtn.destroyed:
            self.btns.remove(self.menubtn)
            self.menubtn.Close()
            self.menubtn = None
        if self.bottomline is not None and not self.bottomline.destroyed:
            self.bottomline.Close()
            self.bottomline = None
        self.exitbtn.parent.state = uiconst.UI_HIDDEN
        if session.stationid2:
            self.exitbtn.OnClick = (self.BtnClick, self.exitbtn)
            self.exitbtn.parent.state = uiconst.UI_NORMAL
            self.exitbtn.OnMouseEnter = (self.BtnEnter, self.exitbtn)
            self.exitbtn.OnMouseExit = (self.BtnExit, self.exitbtn)
            self.exitbtn.name = 'undock'
            self.exitbtn.displayName = mls.UI_GENERIC_UNDOCK
            self.exitbtn.cmdstr = 'CmdExitStation'
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
        for (name, cmdstr, displayName, iconNum, stationOnly,) in iconMapping:
            if name not in inStationServices:
                continue
            m.append((displayName,
             self.CmdMenuAction,
             (cmdstr,),
             (iconNum, 32)))

        return m



    def GetToolsMenu(self, *args):
        m = []
        (iconMapping, inUtils, inStationServices,) = self.GetIconMapping('name')
        for (name, cmdstr, displayName, iconNum, stationOnly,) in iconMapping:
            if name not in inUtils:
                continue
            m.append((displayName,
             self.CmdMenuAction,
             (cmdstr,),
             (iconNum, 32)))

        return m



    def GetJukeboxMenu(self, *args):
        ret = [(mls.UI_GENERIC_SHOW, lambda *args: uicore.cmd.OpenJukebox()), None]
        if sm.GetService('jukebox').jukeboxState == 'play':
            ret += [(mls.UI_SHARED_JUKEBOXPAUSE, lambda *args: sm.GetService('jukebox').Pause())]
        else:
            ret += [(mls.UI_SHARED_JUKEBOXPLAY, lambda *args: sm.GetService('jukebox').Play())]
        ret += [(mls.UI_SHARED_JUKEBOXNEXT, lambda *args: sm.GetService('jukebox').AdvanceTrack()), (mls.UI_SHARED_JUKEBOXPREV, lambda *args: sm.GetService('jukebox').AdvanceTrack(forward=False))]
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
        btn.sr.nme = uicls.Label(text='', parent=textPar, left=4, align=uiconst.CENTERLEFT, top=1, width=90, letterspace=1, fontsize=10, uppercase=1, linespace=10)
        btn.sr.icon = icon
        return btn



    def GetBlink(self, btn):
        if btn.sr.blink:
            return btn.sr.blink
        if not hasattr(btn, 'children'):
            print 'NOBLINK',
            print btn.name,
            print btn.children
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



    def Position(self, autohiding = None, action = None):
        if autohiding is not None:
            self.ahidden = autohiding
        LEFT = settings.user.windows.Get('neoalign', 'left') == 'left'
        BIG = settings.user.windows.Get('neowidth', 1) and not self.ahidden
        width = [[36, 2], [132, 2]][BIG][self.ahidden]
        data = self.PrepareForWindowPush(neoWidth=width)
        self.moving = True
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
            topdown = 0
            if unicode(cn) != unicode(cn).encode('ascii', 'replace'):
                cn = '<center>' + ''.join([ letter + '<br>' for letter in cn ])
                topdown = 1
                charname.autoheight = 0
                charname.height = 100
                charname.text = cn
                charname.parent.SetRotation(0.0)
                charname.parent.top = 24
            else:
                charname.parent.SetRotation(math.pi / 2)
                charname.autoheight = 1
                charname.text = cn
            if LEFT:
                self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderRight.png', 'res:/UI/Texture/Shared/expanderLeft.png'][BIG])
            else:
                self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderLeft.png', 'res:/UI/Texture/Shared/expanderRight.png'][BIG])
            width = [[36, 2], [132, 2]][BIG][self.ahidden]
            bh = self.GetButtonHeight()
            for btn in self.btns:
                btn.sr.icon.align = [uiconst.TOLEFT, uiconst.TORIGHT][LEFT]
                btn.sr.nme.left = [4, 8][LEFT]
                if btn.sr.menuArrow:
                    btn.sr.menuArrow.SetAlign([uiconst.CENTERLEFT, uiconst.CENTERRIGHT][LEFT])
                    btn.sr.menuArrow.LoadIcon(['ui_38_16_227', 'ui_38_16_228'][LEFT])
                if BIG:
                    btn.sr.nme.text = btn.displayName
                else:
                    btn.sr.nme.text = ''

            self.wnd.sr.exitbtnText.text = ['', '<center><b>%s</b>' % mls.UI_GENERIC_UNDOCK][BIG]
            if session.stationid2:
                uicore.effect.MorphUI(self.exitbtn.parent, 'height', [max(BUTTONHEIGHT, bh), 60][BIG], time)
                uicore.effect.MorphUI(self.exitbtn, 'left', [[[0, 0], [37, 37]], [[0, -37], [37, -37]]][LEFT][BIG][self.ahidden], time)
                uicore.effect.MorphUI(self.exitbtn, 'width', [BUTTONHEIGHT, 54][BIG], time, 1, 1)
            if data:
                self.UpdateWindowPush(data, width, action)
            self.ResetBtns(0)
            blue.pyos.synchro.Sleep(int(time))
            self.UpdateClock()

        finally:
            self.moving = False

        mb = sm.GetService('window').GetWindow('mapbrowser', create=0)
        if mb and mb.state != uiconst.UI_HIDDEN:
            mb.SetCorrectLeft()



    def GetWnd(self):
        return self.wnd



    def PrepareForWindowPush(self, neoWidth = None):
        if self.updatingPush:
            self.pushUpdatePending = True
            self.pushUpdatePendingData = neoWidth
            return 
        self.updatingPush = True
        lpush = 0
        rpush = 0
        mbLeftPush = 0
        mbRightPush = 0
        currentMBWidth = 0
        mb = sm.GetService('window').GetWindow('mapbrowser', create=0)
        if mb:
            currentMBWidth = mb.width
            if mb.GetAlign() == uiconst.TOLEFT:
                mbLeftPush = currentMBWidth
            else:
                mbRightPush = currentMBWidth
        onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
        neo = self.GetWnd()
        currentWidth = neo.width
        neoLeftPush = [0, currentWidth][onLeft]
        neoRightPush = [0, currentWidth][(not onLeft)]
        validWnds = sm.GetService('window').GetValidWindows(floatingOnly=True)
        d = uicore.desktop
        leftEdge0 = 0
        leftEdge1 = neoLeftPush
        leftEdge2 = mbLeftPush
        leftEdge3 = neoLeftPush + mbLeftPush
        rightEdge0 = d.width
        rightEdge1 = d.width - neoRightPush
        rightEdge2 = d.width - mbRightPush
        rightEdge3 = d.width - neoRightPush - mbRightPush
        wndsOnLeft = []
        wndsOnRight = []
        wndsOnLeftOffset = []
        wndsOnRightOffset = []
        for wnd in validWnds:
            (l, t, w, h,) = wnd.GetAbsolute()
            if l in (leftEdge0,
             leftEdge1,
             leftEdge2,
             leftEdge3):
                wndsOnLeft.append(wnd)
            elif l in (leftEdge0 + 16,
             leftEdge1 + 16,
             leftEdge2 + 16,
             leftEdge3 + 16):
                wndsOnLeftOffset.append(wnd)
            if l + w in (rightEdge0,
             rightEdge1,
             rightEdge2,
             rightEdge3):
                wndsOnRight.append(wnd)
            elif l + w in (rightEdge0 - 16,
             rightEdge1 - 16,
             rightEdge2 - 16,
             rightEdge3 - 16):
                wndsOnRightOffset.append(wnd)

        return (wndsOnLeft,
         wndsOnLeftOffset,
         wndsOnRight,
         wndsOnRightOffset)



    def UpdateWindowPush(self, data, setNeoWidth = None, action = None, time = 150.0):
        if data:
            (wndsOnLeft, wndsOnLeftOffset, wndsOnRight, wndsOnRightOffset,) = data
        else:
            wndsOnLeft = wndsOnLeftOffset = wndsOnRight = wndsOnRightOffset = []
        mbLeftPush = 0
        mbRightPush = 0
        mb = sm.GetService('window').GetWindow('mapbrowser', create=0)
        if mb and uiutil.IsVisible(mb):
            if mb.GetAlign() == uiconst.TOLEFT:
                mbLeftPush = mb.width
            else:
                mbRightPush = mb.width
        neoLeftPush = 0
        neoRightPush = 0
        onLeft = settings.user.windows.Get('neoalign', 'left') == 'left'
        imBig = settings.user.windows.Get('neowidth', 1) and not self.ahidden
        neo = self.GetWnd()
        if neo:
            neoWidth = setNeoWidth or neo.width
            if uiutil.IsVisible(neo):
                if onLeft:
                    neoLeftPush = neoWidth
                else:
                    neoRightPush = neoWidth
                if action and self.wnd.width != neoWidth:
                    eve.Message('NeoCom' + action)
                uicore.effect.MorphUI(self.wnd, 'width', neoWidth, time)
                self.wnd.SetAlign([uiconst.TORIGHT, uiconst.TOLEFT][onLeft])
                if onLeft:
                    self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderRight.png', 'res:/UI/Texture/Shared/expanderLeft.png'][imBig])
                else:
                    self.expander.SetTexturePath(['res:/UI/Texture/Shared/expanderLeft.png', 'res:/UI/Texture/Shared/expanderRight.png'][imBig])
            else:
                self.wnd.width = neoWidth
        if mb and mb.align == self.wnd.align == uiconst.TOLEFT:
            uicore.effect.MorphUI(mb, 'left', neoLeftPush, time)
        elif mb and mb.align == self.wnd.align == uiconst.TORIGHT:
            uicore.effect.MorphUI(mb, 'left', neoRightPush, time)
        lpush = mbLeftPush + neoLeftPush
        rpush = mbRightPush + neoRightPush
        for wnd in wndsOnLeft:
            uicore.effect.MorphUI(wnd, 'left', lpush, time)

        for wnd in wndsOnLeftOffset:
            uicore.effect.MorphUI(wnd, 'left', lpush + 16, time)

        dw = uicore.desktop.width
        for wnd in wndsOnRight:
            uicore.effect.MorphUI(wnd, 'left', dw - wnd.width - rpush, time)

        for wnd in wndsOnRightOffset:
            uicore.effect.MorphUI(wnd, 'left', dw - wnd.width - rpush - 16, time)

        uicore.effect.MorphUI(uicore.layer.inflight, 'left', lpush, time, ifWidthConstrain=0)
        uicore.effect.MorphUI(uicore.layer.station, 'left', lpush, time, ifWidthConstrain=0)
        uicore.effect.MorphUI(uicore.layer.inflight, 'width', rpush, time, ifWidthConstrain=0)
        uicore.effect.MorphUI(uicore.layer.station, 'width', rpush, time, ifWidthConstrain=0)

        def UpdateDone():
            blue.pyos.synchro.Sleep(int(time) + 100)
            self.updatingPush = 0
            if self.pushUpdatePending:
                self.UpdateWindowPush(self.PrepareForWindowPush(self.pushUpdatePendingData), setNeoWidth=self.pushUpdatePendingData)
            self.pushUpdatePending = False


        uthread.new(UpdateDone)



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
            if not self.locationText:
                self.locationInfo.Flush()
                self.criminalText = uicls.Label(name='criminalText', text='XXX', parent=self.locationInfo, top=-2, left=11, color=None, state=uiconst.UI_HIDDEN)
                caption = uicls.CaptionLabel(text='', align=uiconst.TOPLEFT, fontsize=14, parent=self.locationInfo, left=18, letterspace=5, top=10)
                caption.name = 'caption'
                self.solText = caption
                listbtn = xtriui.ListSurroundingsBtn(parent=self.locationInfo, align=uiconst.TOPLEFT, pos=(-6, 5, 24, 24), showIcon=True)
                listbtn.hint = mls.UI_SHARED_LISTITEMSINSOLARSYSTEM
                listbtn.sr.owner = self
                listbtn.sr.groupByType = 1
                listbtn.filterCurrent = 1
                listbtn.sr.itemID = eve.session.solarsystemid2
                listbtn.sr.typeID = const.typeSolarSystem
                self.listbtn = listbtn
                self.locationTextTopOffset = 30
                txt = uicls.Label(name='locationText', text='', parent=self.locationInfo, width=400, top=self.locationTextTopOffset, color=None, state=uiconst.UI_DISABLED, autowidth=False, tabs=[110, 120, 300])
                txt._tabMargin = 0
                self.locationText = txt
                self.extraTextCont = uicls.NeocomContainer(name='extraTextContainer', parent=self.neocomLeftSide, state=uiconst.UI_HIDDEN)
                txt = uicls.Label(name='autopilotText', text='', parent=self.extraTextCont.content, color=None, tabs=[110, 120, 300])
                txt._tabMargin = 0
                self.extraText = txt
                self.destPathColorCont = uicls.Container(parent=self.extraTextCont.content, name='destPathColorCont', align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), padBottom=8)
                sovLabelText = '<url=localsvc:service=sov&method=GetSovOverview>%s</url>' % mls.UI_SHARED_MAPSOVEREIGNTY
                self.sovLabel = uicls.Label(name='sovLink', text=sovLabelText, parent=self.locationInfo, top=self.locationTextTopOffset, color=None, state=uiconst.UI_HIDDEN)
            if eve.session.solarsystemid2:
                self.locationText.state = uiconst.UI_DISABLED
                self.listbtn.state = uiconst.UI_NORMAL
                self.solText.state = uiconst.UI_DISABLED
                self.UpdateLocationText()
                solarsystemitems = sm.RemoteSvc('config').GetMapObjects(eve.session.solarsystemid2, 0, 0, 0, 1, 0)
                self.listbtn.sr.mapitems = solarsystemitems
                self.listbtn.solarsystemid = eve.session.solarsystemid2
                self.listbtn.sr.itemID = eve.session.solarsystemid2
                self.listbtn.sr.typeID = const.typeSolarSystem
                solarSystemName = cfg.evelocations.Get(eve.session.solarsystemid2).name
                self.solText.text = '<b>%s</b>' % solarSystemName
            else:
                self.locationText.state = uiconst.UI_HIDDEN
                self.listbtn.state = uiconst.UI_HIDDEN
                self.solText.state = uiconst.UI_HIDDEN
            self.UpdateCriminal()

        finally:
            self.updating = False




    def GetSolarSystemStatusText(self, systemStatus = None, returnNone = False):
        if systemStatus is None:
            systemStatus = sm.StartService('facwar').GetSystemStatus()
        xtra = ''
        if systemStatus == const.contestionStateCaptured:
            xtra = mls.UI_INFLIGHT_SYSTEMLOST
        elif systemStatus == const.contestionStateVulnerable:
            xtra = mls.UI_INFLIGHT_SYSTEMVULNERABLE
        elif systemStatus == const.contestionStateContested:
            xtra = mls.UI_INFLIGHT_SYSTEMCONTESTED
        elif systemStatus == const.contestionStateNone and returnNone:
            xtra = mls.UI_INFLIGHT_SYSTEMUNCONTESTED
        return xtra



    def UpdateLocationText(self, nearestBall = None):
        (itemmapping, inView,) = self.GetLocationInfo()
        trace = []
        sovOffset = None
        lines = 0
        if 'station' in inView:
            if eve.session.stationid2:
                stationName = cfg.evelocations.Get(eve.session.stationid2).name
                trace.append('%s<t>&gt;<t><b>%s</b>' % (mls.UI_SHARED_MAPDOCKEDIN.capitalize(), stationName))
                lines += 1
        if 'nearest' in inView:
            nearestBall = nearestBall or self.GetNearestBall()
            if nearestBall:
                self.nearby = nearestBall.id
                trace.append('%s<t>&gt;<t><b>%s</b>' % (mls.UI_GENERIC_NEAREST, nearestBall.name))
                lines += 1
        if 'occupancy' in inView:
            facwarsys = sm.StartService('facwar').GetFacWarSystem(eve.session.solarsystemid2)
            if facwarsys:
                xtra = self.GetSolarSystemStatusText()
                if xtra:
                    xtra = ' (%s)' % xtra
                fac = cfg.eveowners.Get(facwarsys.get('occupierID')).name
                trace.append('%s<t>&gt;<t><b>%s</b>%s' % (mls.UI_SHARED_OCCUPANCY, fac, xtra))
                lines += 1
        if 'sovereignty' in inView:
            ss = sm.RemoteSvc('stationSvc').GetSolarSystem(eve.session.solarsystemid2)
            if ss:
                solSovOwner = ss.factionID
                sovInfo = None
                if solSovOwner is None:
                    sovInfo = sm.GetService('sov').GetSystemSovereigntyInfo(session.solarsystemid2)
                    if sovInfo:
                        solSovOwner = sovInfo.allianceID
                if solSovOwner:
                    trace.append('<t>&gt;<t><b>%s</b>%s' % (cfg.eveowners.Get(solSovOwner).name, sm.GetService('sov').GetContestedState(session.solarsystemid2)))
                elif util.IsWormholeRegion(eve.session.regionid):
                    unclaimText = mls.UI_SHARED_UNCLAIMABLE
                else:
                    unclaimText = mls.UI_SHARED_UNCLAIMED
                trace.append('<t>&gt;<t><i>%s</i>' % unclaimText)
                sovOffset = lines
                lines += 1
        if util.IsWormholeSystem(eve.session.solarsystemid2):
            if 'signature' in inView:
                trace.append('%s<t>&gt;<t>%s' % (mls.UI_GENERIC_LOCUSSIGN, cfg.evelocations.Get(eve.session.solarsystemid2).name))
                lines += 1
        elif 'constellation' in inView or 'region' in inView:
            for (locationID, label, config,) in [(eve.session.constellationid, mls.UI_GENERIC_CONSTELLATION, 'constellation'), (eve.session.regionid, mls.UI_GENERIC_REGION, 'region')]:
                if locationID and config in inView:
                    trace.append('%s<t>&gt;<t>%s' % (label, cfg.evelocations.Get(locationID).name))
                    lines += 1

        if 'security' in inView:
            try:
                (sec, col,) = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(eve.session.solarsystemid2), 1)
                col.a = 1.0
                trace.append(u'%s<t>&gt;<t><color=%s>%.1f</color>' % (mls.UI_INFOWND_SECURITYLEVEL, util.StrFromColor(col), sec))
                lines += 1
            except KeyError:
                self.LogError('Neocom failed to get security status for item', ss.itemID, 'displaying BROKEN')
                log.LogException()
                trace.append('%s > %s' % (mls.UI_INFOWND_SECURITYLEVEL, mls.UI_GENERIC_BROKEN))
                lines += 1
                sys.exc_clear()
        self.locationText.text = '<br>'.join(trace)
        self.locationParent.height = self.locationTextTopOffset + self.locationText.textheight
        if sovOffset is None:
            self.sovLabel.state = uiconst.UI_HIDDEN
        else:
            numLines = self.locationText._numLines
            textheight = (self.locationText.textheight - 1) / numLines
            sovOffset += numLines - lines
            self.sovLabel.top = self.locationTextTopOffset + sovOffset * textheight
            self.sovLabel.state = uiconst.UI_NORMAL
        self.destPathColorCont.Flush()
        waypoints = deque(sm.GetService('starmap').GetWaypoints())
        if self.destPathData:
            MAXPERROW = 36
            WIDTH = 6
            HEIGHT = 6
            for (i, solarSystemID,) in enumerate(self.destPathData):
                row = i / MAXPERROW
                if waypoints and solarSystemID == waypoints[0]:
                    isWaypoint = True
                    waypoints.popleft()
                else:
                    isWaypoint = False
                SolarSystemIcon(parent=self.destPathColorCont, pos=(i % MAXPERROW * WIDTH + 2 * (i % MAXPERROW),
                 row * (HEIGHT + 2),
                 WIDTH,
                 HEIGHT), solarSystemID=solarSystemID, isWaypoint=isWaypoint)

            numRows = len(self.destPathData) / MAXPERROW + 1
            self.destPathColorCont.height = numRows * HEIGHT
        if self.xtratext != '':
            if sm.GetService('map').ViewingStarMap():
                self.extraText.tabs = [110, 120, 300]
            else:
                self.extraText.tabs = [110, 120, 300]
            self.extraText.text = self.xtratext
            self.extraTextCont.state = uiconst.UI_PICKCHILDREN
            self.extraTextCont.height = self.extraText.height + self.destPathColorCont.height + 9
        else:
            self.extraTextCont.state = uiconst.UI_HIDDEN
            self.extraText.text = ''
        if self.locationTimer is None:
            self.locationTimer = base.AutoTimer(1313, self.CheckNearest)



    def UpdateCriminal(self, charcrimes = None, corpcrimes = None):
        if charcrimes is None:
            (charcrimes, corpcrimes,) = sm.GetService('michelle').GetCriminalFlagCountDown()
        if getattr(self, 'criminalText', None) is None:
            return 
        if charcrimes.has_key(None) or corpcrimes.has_key(None):
            criminalTimer = max(charcrimes.get(None, 0), corpcrimes.get(None, 0))
            (color, text,) = ('0xffff0000', mls.UI_SHARED_GLOBALCRIMINAL)
        elif charcrimes and corpcrimes:
            criminalTimer = max(max(charcrimes.values()), max(corpcrimes.values()))
            (color, text,) = ('0xffffff00', mls.UI_GENERIC_AGGRESSION)
        elif charcrimes:
            criminalTimer = max(charcrimes.values())
            (color, text,) = ('0xffffff00', mls.UI_GENERIC_AGGRESSION)
        elif corpcrimes:
            criminalTimer = max(corpcrimes.values())
            (color, text,) = ('0xffffff00', mls.UI_GENERIC_AGGRESSION)
        else:
            criminalTimer = 0
        if criminalTimer > 0:
            self.criminalText.state = uiconst.UI_NORMAL
            self.criminalText.text = '<b><color=%s>%s %s: %s ' % (color,
             text,
             mls.UI_GENERIC_COUNTDOWN,
             util.FmtTimeInterval(criminalTimer - blue.os.GetTime(), breakAt='min'))
            if uicore.uilib.mouseOver == self.criminalText:
                keystoprime = charcrimes.keys() + corpcrimes.keys()
                while None in keystoprime:
                    keystoprime.remove(None)

                cfg.eveowners.Prime(keystoprime)
                criminal = []
                if charcrimes.has_key(None):
                    criminal.append('%s: %s<br>' % (mls.UI_SHARED_GLOBALCRIMINALFLAG, util.FmtDate(charcrimes[None] - blue.os.GetTime(), 'ns')))
                charcrimestr = [ '%s: %s<br>' % (cfg.eveowners.Get(key).name, util.FmtDate(value - blue.os.GetTime(), 'ns')) for (key, value,) in charcrimes.iteritems() if key is not None ]
                if charcrimestr:
                    criminal.append('%s:<br>' % mls.UI_SHARED_YOURCRIMES)
                    criminal += charcrimestr
                corpcrimestr = [ '%s: %s<br>' % (cfg.eveowners.Get(key).name, util.FmtDate(value - blue.os.GetTime(), 'ns')) for (key, value,) in corpcrimes.iteritems() ]
                if corpcrimestr:
                    criminal.append('%s:<br>' % mls.UI_SHARED_CRIMESOFYOURCORP)
                    criminal += corpcrimestr
                self.criminalText.sr.hint = ''.join(criminal)
                uicore.UpdateHint(self.criminalText)
            if not self.criminalTimer:
                self.criminalTimer = base.AutoTimer(1000, self.UpdateCriminal)
        else:
            self.criminalText.sr.hint = ''
            self.criminalText.state = uiconst.UI_HIDDEN
            self.criminalTimer = None



    def CheckNearest(self):
        if not eve.session.solarsystemid or not self.locationText:
            self.locationTimer = None
            return 
        nearestBall = self.GetNearestBall()
        if nearestBall and self.nearby != nearestBall.id:
            self.UpdateLocationText(nearestBall)



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



    def SetXtraText(self, txt = None, destPathData = None):
        change = self.xtratext != (txt or '') or destPathData != self.destPathData
        self.xtratext = txt or ''
        self.destPathData = destPathData
        if change:
            self.UpdateNeocom(0)



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
        while self.btnsready == 0:
            blue.pyos.synchro.Sleep(250)

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
            hilite = self.GetBlink(self.exitbtn)
            hilite.state = uiconst.UI_DISABLED
            hilite.top = hilite.height = 0
            hilite.padBottom = -8
            sm.GetService('ui').BlinkSpriteRGB(self.exitbtn.sr.blink, min(1.0, self.exitbtn.r * (1.0 + bright * 0.25)), min(1.0, self.exitbtn.g * (1.0 + bright * 0.25)), min(1.0, self.exitbtn.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)
            self.Maximize()
        if what == 'clock':
            blink = self.GetBlink(self.dateCont)
            blink.state = uiconst.UI_DISABLED
            blink.top = -8
            blink.height = -20
            sm.GetService('ui').BlinkSpriteRGB(blink, min(1.0, self.dateCont.r * (1.0 + bright * 0.25)), min(1.0, self.dateCont.g * (1.0 + bright * 0.25)), min(1.0, self.dateCont.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)
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
            self.GetBlink(self.exitbtn).state = uiconst.UI_HIDDEN
        if what == 'clock':
            self.GetBlink(self.dateCont).state = uiconst.UI_HIDDEN
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
        now = blue.os.GetTime()
        (date, hours,) = util.FmtDate(now, 'ss').split(' ')
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(now)
        if settings.user.windows.Get('neowidth', 1):
            self.clock.width = 124
            self.clock.text = '<center>%s' % hours
            self.dateText.width = 124
            self.dateText.text = '<center>%s' % date
            self.dateText.fontsize = 9
            self.dateText.top = 1
        else:
            self.clock.width = 32
            self.clock.text = '<center>%s' % hours
            self.dateText.width = 32
            self.dateText.text = '<center>%s' % day
            self.dateText.fontsize = 14
            self.dateText.top = -1



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
        if btn.name != 'undock':
            btn.sr.selection.state = uiconst.UI_DISABLED
        hint = btn.displayName
        cmdstr = getattr(btn, 'cmdstr', None)
        if cmdstr:
            cmdshortcut = uicore.cmd.GetShortcutByString(cmdstr)
            hint += (' [%s]' % cmdshortcut, '')[(cmdshortcut is None)]
        if btn.name == 'wallet':
            wealth = util.FmtISK(sm.GetService('wallet').GetWealth())
            aurWealth = util.FmtAUR(sm.GetService('wallet').GetAurWealth())
            hint += '<br>%s:<br>%s<br>%s' % (mls.UI_GENERIC_BALANCE, wealth, aurWealth)
            if settings.user.windows.Get('neowidth', 1) == 1:
                btn.hint = hint
        if btn.name == 'charactersheet':
            skill = sm.GetService('skills').SkillInTraining()
            if skill is None:
                hint += ' - %s' % mls.UI_SHARED_NOSKILLINTRAINING
            elif sm.GetService('godma').GetStateManager().HasTrainingTimeForSkill(skill.itemID):
                if skill.skillTrainingEnd is None:
                    hint += ' - %s' % mls.UI_SHARED_NOSKILLINTRAINING
                else:
                    secUntilDone = (skill.skillTrainingEnd - blue.os.GetTime()) / const.SEC
                    hint += '<br>%s: %s' % (mls.GENERIC_TRAINING, skill.name)
                    hint += '<br>%s: %s' % (mls.CHAR_SKILLS_LEVEL, skill.skillLevel + 1)
                    hint += '<br>%s: %s' % (mls.UI_GENERIC_ETA, uix.GetTimeText(secUntilDone))
            else:
                hint += '<br>%s: %s' % (mls.GENERIC_TRAINING, skill.name)
                hint += '<br>%s: %s' % (mls.CHAR_SKILLS_LEVEL, skill.skillLevel + 1)
                hint += '<br>%s: %s' % (mls.UI_GENERIC_ETA, mls.UI_GENERIC_LOADING)
                uthread.new(self.RefreshSkillTrainingTime)
            if settings.user.windows.Get('neowidth', 1) == 1:
                btn.hint = hint
        blinkhint = getattr(self, btn.name + '_hint', None)
        if blinkhint:
            hint += ' - ' + blinkhint
        left = settings.user.windows.Get('neoalign', 'left') == 'left'
        if settings.user.windows.Get('neowidth', 1) != 1:
            btn.hint = hint
            btn.sr.hintAbTop = btn.absoluteTop
            (xtraLeft, xtraRight,) = self.GetSideOffset()
            if left:
                btn.sr.hintAbLeft = xtraLeft
            else:
                btn.sr.hintAbRight = uicore.desktop.width - xtraRight
        btn.sr.timer = base.AutoTimer(250, self.ResetHilite, btn)



    def RefreshSkillTrainingTime(self):
        skill = sm.GetService('skills').SkillInTraining()
        if skill is not None:
            return skill.skillTrainingEnd



    def ResetHilite(self, btn, *args):
        pass



    def BtnExit(self, btn, *args):
        if btn.name != 'undock':
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



    def GetSideOffset(self):
        xtraLeft = 0
        xtraRight = 0
        if self.wnd and not self.moving:
            w = self.wnd.width
            if settings.user.windows.Get('neoalign', 'left') == 'left':
                xtraLeft += w
            else:
                xtraRight += w
        return (xtraLeft, xtraRight)



    def GetMainMenu(self):
        m = []
        if settings.user.windows.Get('neoalign', 'left') == 'left':
            m.append((mls.UI_CMD_ALIGNRIGHT, self.ChangeAlign, ('right',)))
        else:
            m.append((mls.UI_CMD_ALIGNLEFT, self.ChangeAlign, ('left',)))
        neoautohide = settings.user.windows.Get('neoautohide', 0)
        m.append(([mls.UI_CMD_TURNAUTOHIDEON, mls.UI_CMD_TURNAUTOHIDEOFF][(neoautohide == 1)], self.ChangeConfig, ('neoautohide', neoautohide != 1)))
        m.append((mls.UI_GENERIC_CONFIGURE, ('isDynamic', self.ConfigureNeocom, ())))
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            m.append(None)
            m += [('Toggle Insider', lambda : sm.StartService('insider').Toggle(forceShow=True))]
            m += [('Reload Insider', lambda : sm.StartService('insider').Reload())]
        return m



    def ConfigureNeocom(self, *args):
        m = []
        m.append((mls.UI_CMD_ACCESSORIES, self.ConfigureNeocomIcons, ('accessories',)))
        m.append((mls.UI_GENERIC_SERVICES, self.ConfigureNeocomIcons, ('stationservices',)))
        m.append((mls.UI_SHARED_MAPWORLDINFO, self.ConfigureNeocomInfo))
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
        for each in iconMapping:
            if len(each) == 5:
                (name, cmdstr, displayName, iconNum, stationOnly,) = each
            elif len(each) == 2:
                (name, displayName,) = each
            if name not in valid:
                continue
            format.append({'type': 'checkbox',
             'setvalue': bool(name in inView),
             'key': name,
             'label': '_hide',
             'required': 1,
             'text': displayName,
             'frame': 1})

        format += [{'type': 'push',
          'frame': 1}, {'type': 'bbline'}]
        retval = uix.HybridWnd(format, mls.UI_CMD_UPDATENEOCOMSETTINGS, 1, buttons=uiconst.OKCANCEL, minW=240, minH=100, icon='ui_2_64_16', unresizeAble=1)
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



    def ConfigureNeocomInfo(self):
        label = mls.UI_SHARED_SHOWHIDEINFO
        setting = 'neocomLocationInfo2'
        valid = ['nearest',
         'occupancy',
         'sovereignty',
         'constellation',
         'region',
         'signature',
         'security',
         'station']
        current = self.GetLocationInfo()
        self.ConfigureNeocomOptions(label, setting, valid, current)



    def ConfigureNeocomIcons(self, option = 'accessories', *args):
        label = mls.UI_SHARED_SHOWHIDEBTNS2 % {'category': self.GetIconMappings(option)[2]}
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
            valid = [ each[0] for each in sm.StartService('station').GetStationServiceInfo() ]
            current = (iconMapping, inStationServices)
        self.ConfigureNeocomOptions(label, setting, valid, current)



    def OnAutohideEnter(self, *args):
        uthread.new(self.Position, 0, action='In')



    def ChangeConfig(self, configname, value):
        settings.user.windows.Set(configname, value)
        if configname == 'neoautohide':
            if value:
                self.AutoHide()
            else:
                self.autohidetimer = None
                uthread.new(self.Position, 0, action='In')



    def AutoHide(self):
        mo = uicore.uilib.mouseOver
        if uiutil.IsUnder(mo, self.wnd):
            return 
        if settings.user.windows.Get('neoautohide', 0):
            self.Position(1, action='Out')
        self.autohidetimer = None



    def ChangeAlign(self, align):
        data = self.PrepareForWindowPush()
        settings.user.windows.Set('neoalign', align)
        if data:
            self.UpdateWindowPush(data)
        self.Position()



    def CharPicEnter(self, *args):
        self.autohidetimer = None



    def CharPicExit(self, *args):
        if settings.user.windows.Get('neoautohide', 0):
            self.SetAutohideTimer()



    def ExpanderClick(self, *args):
        settings.user.windows.Set('neowidth', not settings.user.windows.Get('neowidth', 1))
        self.Position(action=('Out', 'In')[settings.user.windows.Get('neowidth', 1)])



    def Minimize(self):
        if settings.user.windows.Get('neowidth', 1):
            settings.user.windows.Set('neowidth', 0)
            self.Position(action='Out')



    def Maximize(self):
        if not settings.user.windows.Get('neowidth', 1):
            settings.user.windows.Set('neowidth', 1)
            self.Position(action='In')



    def ShowSkillNotification(self, skillTypeIDs):
        ahidden = self.ahidden or settings.user.windows.Get('neoalign', 'left') != 'left'
        BIG = settings.user.windows.Get('neowidth', 1) and not ahidden
        left = [[36, 2], [132, 2]][BIG][ahidden] + 14
        sm.GetService('skills').ShowSkillNotification(skillTypeIDs, left)



    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            self.UpdateLocationText()



    def GetAHidden(self):
        return self.ahidden



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
            eve.GetInventoryFromId(const.containerHangar).MultiAdd(inv, locationID, flag=const.flagHangar)




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
                nameParts = item.itemName.split('(')
                if len(nameParts) > 1:
                    systemName = nameParts[-1].replace(')', '')
                    entryName = mls.UI_INFLIGHT_TOSTARGATE % {'solarsystemName': systemName}
                else:
                    entryName = item.itemName
                typemenu.append((entryName.lower(), (entryName, ('isDynamic', self.ExpandCelestial, (item,)))))
                continue
            elif item.groupID == const.groupAsteroidBelt:
                entryName = item.itemName.replace(mls.UI_GENERIC_ASTEROIDBELT + ' ', '')
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
                m += [(mls.UI_CMD_SHOWINFO, sm.GetService('menu').ShowInfo, (self.sr.typeID, self.sr.itemID))]
            menuItems = {const.groupAsteroidBelt: 'GENERIC_ASTEROIDBELTS',
             const.groupPlanet: 'GENERIC_PLANETS',
             const.groupStargate: 'UI_GENERIC_STARGATES',
             const.groupStation: 'UI_GENERIC_STATIONS'}
            for item in self.sr.mapitems:
                if item.groupID in (const.groupMoon, const.groupSun, const.groupSecondarySun):
                    continue
                mlskey = menuItems[item.groupID]
                if mls.HasLabel(mlskey):
                    name = getattr(mls, mlskey)
                else:
                    name = cfg.invgroups.Get(item.groupID).name
                if not typedict.has_key(name):
                    typedict[name] = []
                typedict[name].append(item)

            sortkeys = uiutil.SortListOfTuples([ [typename, typename] for typename in typedict.iterkeys() ])
            for key in sortkeys:
                m.append((key, ('isDynamic', self.ExpandTypeMenu, (typedict[key],))))

            places = sm.GetService('addressbook').GetMapBookmarks(1)
            bookmarkMenu = []
            if places:
                if self.filterCurrent:
                    places = filter(lambda each: each.locationID == eve.session.solarsystemid2, places)
                bmsByID = {}
                for each in places:
                    bmsByID[each.bookmarkID] = each

                if len(bmsByID):
                    cfg.evelocations.Prime([ bookmark.itemID for bookmark in bmsByID.itervalues() if bookmark.itemID is not None ])
                idsInGroups = []
                groups = uicore.registry.GetListGroups('places2_%s' % eve.session.charid)
                bookmarkGroups = []
                for group in groups.itervalues():
                    if not group or not group['groupItems']:
                        continue
                    sub = []
                    ok = filter(lambda bookmarkID: bookmarkID in bmsByID, group['groupItems'])
                    if not ok:
                        continue
                    for bookmarkID in ok:
                        bookmark = bmsByID[bookmarkID]
                        (hint, comment,) = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
                        if len(hint) > 25:
                            hint = hint[:25] + ' ...'
                        sub.append((hint, (hint, ('isDynamic', self.CelestialMenu, (bookmark.itemID,
                            None,
                            None,
                            0,
                            None,
                            None,
                            bookmark)))))
                        idsInGroups.append(bookmark.bookmarkID)

                    if sub:
                        sub = uiutil.SortListOfTuples(sub)
                        hint = group['label']
                        if len(hint) > 25:
                            hint = hint[:25] + ' ...'
                        bookmarkGroups.append((hint.lower(), ((hint, None), sub)))

                bookmarkGroups = uiutil.SortListOfTuples(bookmarkGroups)
                if bookmarkGroups:
                    bookmarkMenu += bookmarkGroups
                theRest = []
                for (bookmarkID, bookmark,) in bmsByID.iteritems():
                    if bookmarkID in idsInGroups:
                        continue
                    (hint, comment,) = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
                    if len(hint) > 25:
                        hint = hint[:25] + ' ...'
                    theRest.append(((hint.lower(), bookmarkID), ((hint, None), ('isDynamic', self.CelestialMenu, (bookmark.itemID,
                        None,
                        None,
                        0,
                        None,
                        None,
                        bookmark)))))

                if theRest:
                    theRest = uiutil.SortListOfTuples(theRest)
                    theRest.insert(0, None)
                    bookmarkMenu += theRest
            if bookmarkMenu:
                m += [None, ('%s:' % mls.UI_GENERIC_MYPLACES, self.DoNothing)] + bookmarkMenu
            agentMenu = sm.GetService('journal').GetMyAgentJournalBookmarks()
            if agentMenu:
                agentMenu2 = []
                for (missionName, bms, agentID,) in agentMenu:
                    tmp = ['%s (%s)' % (missionName, sm.GetService('agents').GetAgentDisplayName(agentID)), []]
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
                    m += [None, ('%s:' % mls.UI_GENERIC_AGENTMISSIONS, self.DoNothing)] + agentMenu2
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
        if showRoute:
            m.append((mls.UI_SHARED_HIDEROUTE, self.ShowHideRoute, (0,)))
        else:
            m.append((mls.UI_SHARED_SHOWROUTE, self.ShowHideRoute, (1,)))
        if len(starmapSvc.GetWaypoints()) > 0:
            m.append(((mls.UI_SHARED_MAPCLEARALLWAYPOINTS, None), starmapSvc.ClearWaypoints, (None,)))
        return m



    def ShowHideRoute(self, show = 1):
        settings.user.ui.Set('neocomRouteVisible', show)
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
            eve.Message('Command', {'command': mls.UI_SHARED_WARPINGTOTUTSITE})
            bp.WarpToTutorial()



    def GetDragData(self, *args):
        itemID = self.sr.Get('itemID', None)
        typeID = self.sr.Get('typeID', None)
        if not itemID or not typeID:
            return []
        label = ''
        if typeID in (const.typeRegion, const.typeConstellation, const.typeSolarSystem):
            label += cfg.evelocations.Get(itemID).name
            elabel = {const.typeRegion: mls.UI_GENERIC_REGION,
             const.typeConstellation: mls.UI_GENERIC_CONSTELLATION,
             const.typeSolarSystem: mls.UI_GENERIC_SOLARSYSTEM}
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




class SolarSystemIcon(uicls.Icon):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_size = 8
    default_ignoreSize = True

    def ApplyAttributes(self, attributes):
        self.solarSystemID = attributes.solarSystemID
        self.isWaypoint = attributes.isWaypoint
        num = attributes.num
        if self.isWaypoint:
            icon = 'ui_73_16_51'
        else:
            icon = 'ui_73_16_52'
        attributes['icon'] = icon
        uicls.Icon.ApplyAttributes(self, attributes)
        color = sm.GetService('starmap').GetSystemColor(self.solarSystemID)
        self.color.SetRGB(color.r, color.g, color.b)
        self.rectTop += 4
        self.rectLeft += 4
        self.rectWidth = 8
        self.rectHeight = 8



    def GetHint(self, *args):
        (securityTxt, color,) = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(self.solarSystemID), 1)
        colorHex = sm.GetService('starmap').GetSystemColorString(self.solarSystemID)
        return '%s <color=%s>%s' % (cfg.evelocations.Get(self.solarSystemID).name, colorHex, securityTxt)



    def GetMenu(self, *args):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(self.solarSystemID, const.typeSolarSystem)



    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(const.typeSolarSystem, self.solarSystemID)




