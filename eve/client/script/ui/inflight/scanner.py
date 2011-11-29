import uix
import uiutil
import uiconst
import mathUtil
import xtriui
import uthread
import form
import blue
import util
import trinity
import service
import listentry
import base
import math
import sys
import geo2
import maputils
import state
from math import pi, cos, sin, sqrt
from foo import Vector3
from mapcommon import SYSTEMMAP_SCALE
import functools
import uicls
import localization
import localizationUtil
CIRCLE_SCALE = 0.01
CIRCLE_COLOR = (1.0,
 0.0,
 0.0,
 1.0)
POINT_ICON_PROPS = ('ui_38_16_254',
 0,
 0.0,
 1e+32,
 0,
 1)
POINT_ICON_DUNGEON = ('ui_38_16_14',
 0.0,
 0,
 0.0,
 1e+32,
 0,
 1)
POINT_COLOR_RED = (1.0,
 0.0,
 0.0,
 1.0)
POINT_COLOR_YELLOW = (1.0,
 1.0,
 0.0,
 1.0)
POINT_COLOR_GREEN = (0.0,
 1.0,
 0.0,
 1.0)
SET_PROBE_DESTINATION_TIMEOUT = 3000
AXIS_Y = geo2.Vector(0.0, 1.0, 0.0)
CURSOR_SCALE_ARG_1 = 2000000.0
CURSOR_SCALE = SYSTEMMAP_SCALE * 250000000000.0
CURSOR_COLORPARAMETERIDX = 1
CURSOR_DEFAULT_COLOR = (0.7960784435272217,
 0.8313725590705872,
 0.8509804010391235,
 1.0)
CURSOR_HIGHLIGHT_COLOR = (0.29411764705882354,
 0.7254901960784313,
 0.996078431372549,
 1.0)
LINESET_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/LinesAdditive.fx'
INTERSECTION_COLOR = (0.3,
 0.5,
 0.7,
 1.0)
RANGE_INDICATOR_CIRCLE_COLOR = (INTERSECTION_COLOR[0] * 0.5,
 INTERSECTION_COLOR[1] * 0.5,
 INTERSECTION_COLOR[2] * 0.5,
 1.0)
RANGE_INDICATOR_CROSS_COLOR = (INTERSECTION_COLOR[0] * 0.25,
 INTERSECTION_COLOR[1] * 0.25,
 INTERSECTION_COLOR[2] * 0.25,
 1.0)
INTERSECTION_ACTIVE = 1.0
INTERSECTION_FADED = 0.4
INTERSECTION_INACTIVE = 0.15
CIRCLE_NUM_POINTS = 256
CIRCLE_ANGLE_SIZE = 2.0 * pi / CIRCLE_NUM_POINTS
CIRCLE_POINTS = []
for i in xrange(CIRCLE_NUM_POINTS):
    (x, y,) = (cos(CIRCLE_ANGLE_SIZE * i), sin(CIRCLE_ANGLE_SIZE * i))
    CIRCLE_POINTS.append((x, 0.0, y))

MAX_PROBE_DIST_FROM_SUN_SQUARED = (const.AU * 250) ** 2
MIN_WARP_DISTANCE_SQUARED = const.minWarpDistance ** 2
CENTROID_LINE_COLOR = (0.1,
 1.0,
 0.1,
 0.75)
CENTROID_LINE_WIDTH = 1.5
DISTRING_LINE_WIDTH = 1.0
DISTANCE_RING_RANGES = [1,
 2,
 4,
 8,
 16,
 32,
 64,
 128]
MAX_DIST_RING_RANGE = DISTANCE_RING_RANGES[-1]
SQRT_05 = sqrt(0.5)

def UserErrorIfScanning(action, *args, **kwargs):

    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        if sm.GetService('scanSvc').IsScanning():
            raise UserError('ScanInProgressGeneric')
        return action(*args, **kwargs)


    return wrapper



def IsResultWithinWarpDistance(result):
    ballpark = sm.GetService('michelle').GetBallpark()
    egoBall = ballpark.GetBall(ballpark.ego)
    egoPos = geo2.Vector(egoBall.x, egoBall.y, egoBall.z)
    resultPos = geo2.Vector(*result.data)
    distanceSquared = geo2.Vec3LengthSq(egoPos - resultPos)
    return distanceSquared > MIN_WARP_DISTANCE_SQUARED



class Scanner(uicls.Window):
    __guid__ = 'form.Scanner'
    __notifyevents__ = ['OnSessionChanged',
     'OnProbeAdded',
     'OnProbeRemoved',
     'OnSystemScanBegun',
     'OnSystemScanDone',
     'OnNewScannerFilterSet',
     'OnProbeStateUpdated',
     'OnProbeRangeUpdated',
     'OnScannerDisconnected',
     'OnRefreshScanResults',
     'OnReconnectToProbesAvailable',
     'OnModuleOnlineChange']
    default_windowID = 'scanner'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scanGroups = {}
        self.scanGroups[const.probeScanGroupAnomalies] = localization.GetByLabel('UI/Inflight/Scanner/CosmicAnomaly')
        self.scanGroups[const.probeScanGroupSignatures] = localization.GetByLabel('UI/Inflight/Scanner/CosmicSignature')
        self.scanGroups[const.probeScanGroupShips] = localization.GetByLabel('UI/Inflight/Scanner/Ship')
        self.scanGroups[const.probeScanGroupStructures] = localization.GetByLabel('UI/Inflight/Scanner/Structure')
        self.scanGroups[const.probeScanGroupDronesAndProbes] = localization.GetByLabel('UI/Inflight/Scanner/DroneAndProbe')
        self._Scanner__disallowanalysisgroups = [const.groupSurveyProbe]
        self.busy = False
        self.scanresult = []
        self.lastScaleUpdate = None
        self.lastMoveUpdate = None
        self.scanangle = mathUtil.DegToRad(90)
        self.sr.probeSpheresByID = {}
        self.sr.rangeIndicators = {}
        self.sr.resultObjectsByID = {}
        self.sr.probeIntersectionsByPair = {}
        self.sr.distanceRings = None
        self.centroidLines = None
        self.lastProbeIDs = None
        self.sr.systemParent = None
        activeFilter = settings.user.ui.Get('activeProbeScannerFilter', None)
        currentFilters = settings.user.ui.Get('probeScannerFilters', {})
        self.currentFilter = currentFilters.get(activeFilter, [])
        self.activeScanGroupInFilter = set()
        self.sr.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKey)
        self.sr.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKey)
        self.scope = 'inflight'
        self.SetCaption(localization.GetByLabel('UI/Generic/Scanner'))
        self.SetMinSize([340, 320])
        self.SetTopparentHeight(0)
        self.SetWndIcon(None)
        self.HideMainIcon()
        currentryActiveColumn = settings.user.ui.Get('activeSortColumns', {})
        if 'probeResultGroupColumn' not in currentryActiveColumn:
            currentryActiveColumn['probeResultGroupColumn'] = 1
            settings.user.ui.Set('activeSortColumns', currentryActiveColumn)
        systemsParent = uicls.Container(name='system', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.systemsParent = systemsParent
        topParent = uicls.Container(name='systemSettings', parent=systemsParent, align=uiconst.TOTOP, height=40)
        topParent.padTop = 6
        topParent.padLeft = 6
        topParent.padRight = 6
        self.sr.systemTopParent = topParent
        btn = uix.GetBigButton(32, topParent)
        btn.Click = self.Analyze
        btn.hint = localization.GetByLabel('UI/Inflight/Scanner/Analyze')
        btn.sr.icon.LoadIcon('77_57')
        self.sr.analyzeBtn = btn
        btn = uix.GetBigButton(32, topParent, left=44)
        btn.Click = self.RecoverActiveProbes
        btn.hint = localization.GetByLabel('UI/Inflight/Scanner/RecoverActiveProbes')
        btn.sr.icon.LoadIcon('77_58')
        self.sr.recoverBtn = btn
        btn = uix.GetBigButton(32, topParent, left=76)
        btn.Click = self.ReconnectToLostProbes
        btn.hint = localization.GetByLabel('UI/Inflight/Scanner/ReconnectActiveProbes')
        btn.sr.icon.LoadIcon('77_59')
        self.sr.reconnectBtn = btn
        btn = uix.GetBigButton(32, topParent, left=108)
        btn.Click = self.DestroyActiveProbes
        btn.hint = localization.GetByLabel('UI/Inflight/Scanner/DestroyActiveProbes')
        btn.sr.icon.LoadIcon('77_60')
        self.sr.destroyBtn = btn
        btn = uix.GetBigButton(32, topParent)
        btn.SetAlign(align=uiconst.TOPRIGHT)
        btn.OnClick = self.OpenMap
        btn.hint = localization.GetByLabel('UI/Common/Map')
        btn.sr.icon.LoadIcon('7_4')
        probesHeaderParent = uicls.Container(parent=systemsParent, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=24)
        probesHeaderParent.padBottom = 6
        t = uicls.EveLabelMedium(text=['<b>', localization.GetByLabel('UI/Inflight/Scanner/ProbesInSpace'), '</b>'], parent=probesHeaderParent, state=uiconst.UI_DISABLED, left=const.defaultPadding, align=uiconst.CENTERLEFT)
        probesHeaderParent.height = max(20, t.textheight + 6)
        self.sr.probesHeaderParent = probesHeaderParent
        l = uicls.Line(parent=probesHeaderParent, align=uiconst.TOTOP, color=(0.0, 0.0, 0.0, 0.25))
        l = uicls.Line(parent=probesHeaderParent, align=uiconst.TOTOP)
        l = uicls.Line(parent=probesHeaderParent, align=uiconst.TOBOTTOM)
        l = uicls.Line(parent=probesHeaderParent, align=uiconst.TOBOTTOM, color=(0.0, 0.0, 0.0, 0.25))
        probesClipper = uicls.Container(parent=systemsParent, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=100)
        probesClipper.padLeft = const.defaultPadding
        probesClipper.padRight = const.defaultPadding
        self.sr.probesClipper = probesClipper
        self.sr.scroll = uicls.Scroll(name='scroll', parent=probesClipper, align=uiconst.TOALL)
        divPar = uicls.Container(name='divider', align=uiconst.TOBOTTOM, height=const.defaultPadding, parent=probesClipper, idx=0)
        divider = xtriui.Divider(name='divider', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=divPar, state=uiconst.UI_NORMAL, idx=0)
        divider.Startup(probesClipper, 'height', 'y', 57, 800)
        divider.OnSizeChanged = self._OnProbesSizeChanged
        divider.OnSizeChangeStarting = self._OnProbesSizeChangeStarting
        divider.OnSizeChanging = self._OnProbesSizeChanging
        l = uicls.Line(parent=divider, align=uiconst.CENTER, width=6, height=1)
        self.sr.divider = divider
        resultHeaderParent = uicls.Container(parent=systemsParent, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=24)
        t = uicls.EveLabelMedium(text=['<b>', localization.GetByLabel('UI/Inflight/Scanner/ScanResults'), '</b>'], parent=resultHeaderParent, state=uiconst.UI_DISABLED, left=const.defaultPadding, align=uiconst.CENTERLEFT)
        resultHeaderParent.height = max(20, t.textheight + 6)
        self.sr.resultHeaderParent = resultHeaderParent
        l = uicls.Line(parent=resultHeaderParent, align=uiconst.TOTOP, color=(0.0, 0.0, 0.0, 0.25))
        l = uicls.Line(parent=resultHeaderParent, align=uiconst.TOTOP)
        l = uicls.Line(parent=resultHeaderParent, align=uiconst.TOBOTTOM)
        l = uicls.Line(parent=resultHeaderParent, align=uiconst.TOBOTTOM, color=(0.0, 0.0, 0.0, 0.25))
        resultClipper = uicls.Container(parent=systemsParent, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN)
        resultClipper.padLeft = const.defaultPadding
        resultClipper.padRight = const.defaultPadding
        resultClipper.padBottom = 6
        resultClipper.padTop = 6
        self.sr.resultClipper = resultClipper
        hintContainer = uicls.Container(parent=resultClipper, align=uiconst.TOTOP, height=18)
        t = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Inflight/Scanner/ScanResultFilter'), parent=hintContainer, left=26, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT)
        filterContainer = uicls.Container(parent=resultClipper, align=uiconst.TOTOP, height=18)
        filterContainer.padTop = 2
        filterContainer.padBottom = 4
        filterCombo = uicls.Combo(label='', parent=filterContainer, options=[], name='probeScanningFilter', select=None, callback=self.OnFilterComboChange, align=uiconst.TOALL)
        filterCombo.left = 23
        filterCombo.width = 1
        self.sr.filterCombo = filterCombo
        presetMenu = uicls.MenuIcon()
        presetMenu.GetMenu = self.GetFilterMenu
        presetMenu.left = 2
        presetMenu.top = 0
        presetMenu.hint = ''
        filterContainer.children.append(presetMenu)
        self.sr.resultscroll = uicls.Scroll(name='resultscroll', parent=resultClipper)
        self.sr.resultscroll.OnSelectionChange = self.OnSelectionChange
        directionBox = uicls.Container(name='direction', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding, height=const.defaultPadding)
        directionSettingsBox = uicls.Container(name='direction', parent=directionBox, align=uiconst.TOTOP, height=60)
        self.sr.useoverview = uicls.Checkbox(text=localization.GetByLabel('UI/Inflight/Scanner/UseActiveOverviewSettings'), parent=directionSettingsBox, configName='', retval=0, checked=settings.user.ui.Get('scannerusesoverviewsettings', 0), align=uiconst.TOTOP, callback=self.UseOverviewChanged, pos=(5, 4, 0, 18))
        self.dir_rangeinput = uicls.SinglelineEdit(name='edit', parent=directionSettingsBox, ints=(1, None), align=uiconst.TOPLEFT, pos=(5, 36, 85, 0), maxLength=len(str(sys.maxint)) + 1)
        self.dir_rangeinput.SetValue(settings.user.ui.Get('dir_scanrange', 1000))
        self.dir_rangeinput.OnReturn = self.DirectionSearch
        uicls.EveLabelSmall(text=localization.GetByLabel('UI/Inflight/Scanner/RangeKm'), parent=directionSettingsBox, width=240, left=6, top=23, state=uiconst.UI_DISABLED)
        uicls.Button(parent=directionSettingsBox, label=localization.GetByLabel('UI/Inflight/Scanner/Scan'), pos=(180, 37, 0, 0), func=self.DirectionSearch)
        slider = uix.GetSlider('slider', directionSettingsBox, 'scanangle', 5, 360, localization.GetByLabel('UI/Inflight/Scanner/Angle'), '', uiconst.RELATIVE, 90, 18, 90, 36, getvaluefunc=self.GetSliderValue, endsliderfunc=self.EndSetSliderValue, gethintfunc=lambda idname, dname, value: localizationUtil.FormatNumeric(int(round(value))), increments=(5, 15, 30, 60, 90, 180, 360), underlay=0)
        lbl = uiutil.GetChild(slider, 'label')
        lbl.top = -13
        lbl.left = 2
        lbl.state = uiconst.UI_DISABLED
        uiutil.SetOrder(slider, 0)
        self.sr.dirscroll = uicls.Scroll(name='scroll', parent=directionBox)
        self.sr.dirscroll.sr.id = 'scanner_dirscroll'
        self.sr.moonscanner = xtriui.MoonScanView(name='moonparent', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.moonscanner.Startup()
        self.sr.tabs = uicls.TabGroup(name='scannertabs', height=18, align=uiconst.TOTOP, parent=self.sr.main, idx=0, tabs=[[localization.GetByLabel('UI/Inflight/Scanner/SystemScanner'),
          systemsParent,
          self,
          'system'], [localization.GetByLabel('UI/Inflight/Scanner/DirectionalScan'),
          directionBox,
          self,
          'directionalscan'], [localization.GetByLabel('UI/Inflight/Scanner/MoonAnalysis'),
          self.sr.moonscanner,
          self,
          'moon']], groupID='scannertabs', autoselecttab=1)
        systemMapSvc = sm.GetService('systemmap')
        systemMapSvc.LoadProbesAndScanResult()
        systemMapSvc.LoadSolarsystemBrackets(True)
        self.LoadProbeList()
        if self.destroyed:
            return 
        self.UpdateProbeSpheres()
        uthread.new(self.ApplyProbesPortion)



    def _OnClose(self, *args):
        self.Cleanup()
        self.SetMapAngle(0)
        systemMap = sm.GetService('systemmap')
        systemMap.LoadProbesAndScanResult_Delayed()
        uthread.new(systemMap.LoadSolarsystemBrackets, True)



    def OnGlobalKey(self, *args):
        if getattr(self, 'lastScaleUpdate', None) is not None:
            (probeID, pos,) = self.lastScaleUpdate
            probeControl = self.GetProbeSphere(probeID)
            if probeControl:
                self.ScaleProbe(probeControl, pos, force=1)
            self.lastScaleUpdate = None
        elif getattr(self, 'lastMoveUpdate', None) is not None:
            (probeID, translation,) = self.lastMoveUpdate
            probeControl = self.GetProbeSphere(probeID)
            if probeControl:
                self.MoveProbe(probeControl, translation)
            self.lastMoveUpdate = None
        return 1



    def SetScanDronesState(self, value):
        for probe in self.sr.probeSpheresByID.values():
            probe.SetScanDronesState(value)




    def OnSystemScanBegun(self):
        self.Refresh()
        self.SetScanDronesState(1)



    def OnSystemScanDone(self):
        self.SetScanDronesState(0)
        self.Refresh()



    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change and not eve.session.stationid:
            self.LoadProbeList()
            self.LoadResultList()



    def OnNewScannerFilterSet(self, *args):
        self.LoadFiltersOptions()



    def OnProbeStateUpdated(self, probeID, state):
        self.sr.loadProbeList = base.AutoTimer(200, self.LoadProbeList)
        self.sr.updateProbeSpheresTimer = base.AutoTimer(200, self.UpdateProbeSpheres)



    def OnProbeRangeUpdated(self, probeID, scanRange):
        probe = self.GetProbeSphere(probeID)
        if probe:
            probe.SetRange(scanRange)



    def OnScannerDisconnected(self):
        self.LoadProbeList()
        self.LoadResultList()
        self.UpdateProbeSpheres()
        self.CheckButtonStates()



    def OnProbeRemoved(self, probeID):
        uthread.new(self._OnProbeRemove, probeID)



    def _OnProbeRemove(self, probeID):
        rm = []
        cnt = 0
        for entry in self.sr.scroll.GetNodes():
            if entry.Get('probe', None) is None:
                continue
            if entry.probe.probeID == probeID:
                rm.append(entry)
            cnt += 1

        if rm:
            self.sr.scroll.RemoveEntries(rm)
        if cnt <= 1:
            uthread.new(self.LoadProbeList)
        self.CheckButtonStates()
        self.UpdateProbeSpheres()



    def OnProbeAdded(self, probe):
        uthread.new(self._OnProbeAdded, probe)



    def _OnProbeAdded(self, probe):
        self.UpdateProbeSpheres()
        self.LoadProbeList()
        sm.GetService('systemmap').LoadProbesAndScanResult()



    def UpdateProbeState(self, probeID, probeState):
        probe = self.GetProbeSphere(probeID)
        if probe:
            busy = False
            if probeState != const.probeStateIdle:
                busy = True
            probe.cursor.display = not busy



    def Cleanup(self):
        self.sr.probeSpheresByID = {}
        bracketWnd = uicore.layer.systemMapBrackets
        for each in bracketWnd.children[:]:
            if each.name in ('__probeSphereBracket', '__pointResultBracket'):
                each.trackTransform = None
                each.Close()

        self.CleanupResultShapes()
        scene = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene:
            for intersection in self.sr.probeIntersectionsByPair.values():
                if intersection.lineSet in scene.objects:
                    scene.objects.remove(intersection.lineSet)

            if self.sr.distanceRings and self.sr.distanceRings.lineSet in scene.objects:
                scene.objects.remove(self.sr.distanceRings.lineSet)
        self.sr.probeIntersectionsByPair = {}
        self.sr.distanceRings = None
        parent = self.GetSystemParent(create=0)
        currentSystem = sm.GetService('systemmap').GetCurrentSolarSystem()
        if currentSystem and parent:
            if parent in currentSystem.children[:]:
                currentSystem.children.remove(parent)
        self.sr.systemParent = None
        sm.GetService('systemmap').HighlightItemsWithinProbeRange()



    def SetEntries(self, entries):
        self.sr.moonscanner.SetEntries(entries)
        if self.sr.tabs.GetSelectedArgs() != 'moon':
            self.sr.tabs.BlinkPanelByName(localization.GetByLabel('UI/Inflight/Scanner/MoonAnalysis'), blink=1)



    def ClearMoons(self):
        self.sr.moonscanner.Clear()
        if self.sr.tabs.GetSelectedArgs() != 'moon':
            self.sr.tabs.BlinkPanelByName(localization.GetByLabel('UI/Inflight/Scanner/MoonAnalysis'), blink=1)



    def OpenMap(self, *args):
        sm.GetService('viewState').ToggleSecondaryView('systemmap')



    def GetFilterMenu(self, *args):
        filterName = self.sr.filterCombo.GetKey()
        filterData = self.sr.filterCombo.GetValue()
        m = [(localization.GetByLabel('UI/Inflight/Scanner/CreateNewFilter'), self.AddFilter)]
        if filterName and filterData:
            m.append((localization.GetByLabel('UI/Inflight/Scanner/EditCurrentFilter'), self.EditCurrentFilter))
            m.append((localization.GetByLabel('UI/Inflight/Scanner/DeleteCurrentFilter'), self.DeleteCurrentFilter))
        scanSvc = sm.GetService('scanSvc')
        if len(scanSvc.resultsIgnored) > 0:
            m.append(None)
            m.append((localization.GetByLabel('UI/Inflight/Scanner/ClearAllIgnoredResults'), scanSvc.ClearIgnoredResults))
            ids = sorted(scanSvc.resultsIgnored)
            m.append((localization.GetByLabel('UI/Inflight/Scanner/ClearIgnoredResult'), [ (id, scanSvc.ShowIgnoredResult, (id,)) for id in ids ]))
        return m



    def LoadFiltersOptions(self):
        currentFilters = settings.user.ui.Get('probeScannerFilters', {})
        activeFilter = settings.user.ui.Get('activeProbeScannerFilter', None)
        if activeFilter not in currentFilters:
            activeFilter = None
        k = currentFilters.keys()
        k.sort(key=unicode.lower)
        filterOps = [(localization.GetByLabel('UI/Common/Show all'), False)]
        for label in k:
            filterOps.append((label, True))

        self.sr.filterCombo.LoadOptions(filterOps)
        if activeFilter is not None:
            self.sr.filterCombo.SelectItemByLabel(activeFilter)
        else:
            self.sr.filterCombo.SelectItemByLabel(localization.GetByLabel('UI/Common/Show all'))
        self.currentFilter = currentFilters.get(activeFilter, [])
        self.activeScanGroupInFilter = set()
        for groupID in self.currentFilter:
            for (scanGroupID, scanGroup,) in const.probeScanGroups.iteritems():
                if isinstance(groupID, tuple):
                    groupID = groupID[0]
                if groupID in scanGroup:
                    self.activeScanGroupInFilter.add(scanGroupID)


        self.LoadResultList()



    def AddFilter(self, *args):
        editor = form.ScannerFilterEditor.Open()
        editor.LoadData(None)



    def EditCurrentFilter(self, *args):
        activeFilter = settings.user.ui.Get('activeProbeScannerFilter', None)
        editor = form.ScannerFilterEditor.Open()
        editor.LoadData(activeFilter)



    def DeleteCurrentFilter(self, *args):
        activeFilter = settings.user.ui.Get('activeProbeScannerFilter', None)
        currentFilters = settings.user.ui.Get('probeScannerFilters', {})
        if activeFilter in currentFilters:
            del currentFilters[activeFilter]
            settings.user.ui.Set('probeScannerFilters', currentFilters)
        settings.user.ui.Set('activeProbeScannerFilter', None)
        self.LoadFiltersOptions()



    def OnFilterComboChange(self, combo, key, value, *args):
        if not value:
            self.currentFilter = []
            settings.user.ui.Set('activeProbeScannerFilter', None)
        else:
            settings.user.ui.Set('activeProbeScannerFilter', key)
            groups = settings.user.ui.Get('probeScannerFilters', {})
            self.currentFilter = groups.get(key, [])
        sm.ScatterEvent('OnNewScannerFilterSet', key, self.currentFilter)



    def ApplyProbesPortion(self):
        if not util.GetAttrs(self, 'sr', 'probesClipper') or getattr(self, '_ignorePortion', False) or not uiutil.IsVisible(self.sr.probesClipper):
            return 
        portion = settings.user.ui.Get('scannerProbesPortion', 0.5)
        minResultSpace = self.sr.resultHeaderParent.height + 18
        (sl, st, sw, sh,) = self.sr.systemsParent.GetAbsolute()
        (rcl, rct, rcw, rch,) = self.sr.resultClipper.GetAbsolute()
        spread = sh - self.sr.probesHeaderParent.height - self.sr.systemTopParent.height
        height = int(spread * portion)
        self.sr.probesClipper.height = min(height, spread - minResultSpace)



    def OnResizeUpdate(self, *args):
        uthread.new(self.ApplyProbesPortion)



    def _OnProbesSizeChanged(self, *args):
        (sl, st, sw, sh,) = self.sr.systemsParent.GetAbsolute()
        probesPart = self.sr.probesHeaderParent.height + self.sr.probesClipper.height
        (rcl, rct, rcw, rch,) = self.sr.resultClipper.GetAbsolute()
        resultPart = self.sr.resultHeaderParent.height + rch
        portion = probesPart / float(sh - self.sr.systemTopParent.height)
        settings.user.ui.Set('scannerProbesPortion', portion)
        self._ignorePortion = False



    def _OnProbesSizeChangeStarting(self, *args):
        self._ignorePortion = True
        (l, t, w, h,) = self.sr.probesClipper.GetAbsolute()
        minResultSpace = self.sr.resultHeaderParent.height + 18
        maxValue = uicore.desktop.height - t - minResultSpace
        self.sr.divider.SetMinMax(maxValue=maxValue)
        self._maxProbesClipperHeight = maxValue



    def _OnProbesSizeChanging(self, *args):
        if self.sr.probesClipper.height < self._maxProbesClipperHeight:
            if self.sr.stack:
                (l, t, w, h,) = self.sr.stack.GetAbsolute()
            else:
                (l, t, w, h,) = self.GetAbsolute()
            minResultSpace = self.sr.resultHeaderParent.height + 18
            if t + h - uicore.uilib.y < minResultSpace:
                if self.sr.stack:
                    self.sr.stack.height = uicore.uilib.y + minResultSpace - t
                else:
                    self.height = uicore.uilib.y + minResultSpace - t



    def Load(self, what):
        if what == 'moon':
            sm.GetService('moonScan').Refresh()
        if what == 'system':
            self.Refresh()
            self.ApplyProbesPortion()



    def DirectionSearch(self, *args):
        if self.destroyed or self.busy:
            return 
        self.busy = True
        self.ShowLoad()
        self.scanresult = []
        if self.sr.useoverview.checked:
            filters = sm.GetService('tactical').GetValidGroups()
        camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
        if not camera:
            self.busy = False
            self.HideLoad()
            raise RuntimeError('No camera found?!')
        rot = camera.rotationAroundParent
        vec = trinity.TriVector(0.0, 0.0, -1.0)
        vec.TransformQuaternion(rot)
        vec.Normalize()
        rnge = self.dir_rangeinput.GetValue()
        result = None
        try:
            result = sm.GetService('scanSvc').ConeScan(self.scanangle, rnge * 1000, vec.x, vec.y, vec.z)
        except (UserError, RuntimeError) as err:
            result = None
            self.busy = False
            self.HideLoad()
            raise err
        settings.user.ui.Set('dir_scanrange', rnge)
        if result:
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                for rec in result:
                    if self.sr.useoverview.checked:
                        if rec.groupID not in filters:
                            continue
                    if rec.id in bp.balls:
                        self.scanresult.append([None, bp.balls[rec.id], rec])
                    else:
                        self.scanresult.append([None, None, rec])

        self.ShowDirectionalSearchResult()
        self.busy = False
        self.HideLoad()



    def ShowDirectionalSearchResult(self, *args):
        self.listtype = 'location'
        scrolllist = []
        if self.scanresult and len(self.scanresult):
            myball = None
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark:
                myball = ballpark.GetBall(eve.session.shipid)
            prime = []
            for result in self.scanresult:
                (slimItem, ball, celestialRec,) = result
                if not slimItem and celestialRec:
                    prime.append(celestialRec.id)

            if prime:
                cfg.evelocations.Prime(prime)
            sortdist = []
            for (slimItem, ball, celestialRec,) in self.scanresult:
                if self is None or self.destroyed:
                    return 
                dist = 0
                if slimItem:
                    typeinfo = cfg.invtypes.Get(slimItem.typeID)
                    entryname = uix.GetSlimItemName(slimItem)
                    itemID = slimItem.itemID
                    typeID = slimItem.typeID
                    if not entryname:
                        entryname = typeinfo.Group().name
                elif celestialRec:
                    typeinfo = cfg.invtypes.Get(celestialRec.typeID)
                    if typeinfo.groupID == const.groupHarvestableCloud:
                        entryname = localization.GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', typeinfo.name)
                    elif typeinfo.categoryID == const.categoryAsteroid:
                        entryname = localization.GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', typeinfo.name)
                    else:
                        entryname = cfg.evelocations.Get(celestialRec.id).name
                    if not entryname:
                        entryname = typeinfo.name
                    itemID = celestialRec.id
                    typeID = celestialRec.typeID
                else:
                    continue
                if ball is not None:
                    dist = ball.surfaceDist
                    diststr = util.FmtDist(dist, maxdemicals=1)
                else:
                    dist = 0
                    diststr = '-'
                groupID = cfg.invtypes.Get(typeID).groupID
                if not eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                    if groupID == const.groupCloud:
                        continue
                data = util.KeyVal()
                data.label = '%s<t>%s<t>%s' % (entryname, typeinfo.name, diststr)
                data.Set('sort_%s' % localization.GetByLabel('UI/Common/Distance'), dist)
                data.columnID = 'directionalResultGroupColumn'
                data.result = result
                data.itemID = itemID
                data.typeID = typeID
                data.GetMenu = self.DirectionalResultMenu
                scrolllist.append(listentry.Get('Generic', data=data))
                blue.pyos.BeNice()

        if not len(scrolllist):
            data = util.KeyVal()
            data.label = localization.GetByLabel('UI/Inflight/Scanner/DirectionalNoResult')
            data.hideLines = 1
            scrolllist.append(listentry.Get('Generic', data=data))
            headers = []
        else:
            headers = [localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Distance')]
        self.sr.dirscroll.Load(contentList=scrolllist, headers=headers)



    def DirectionalResultMenu(self, entry, *args):
        if entry.sr.node.itemID:
            return sm.GetService('menu').CelestialMenu(entry.sr.node.itemID, typeID=entry.sr.node.typeID)
        return []



    def GetSliderValue(self, *args):
        (config, value,) = args
        self.SetMapAngle(mathUtil.DegToRad(value))



    def SetMapAngle(self, angle):
        if angle is not None:
            self.scanangle = angle
        wnd = form.MapBrowserWnd.GetIfOpen()
        if wnd:
            wnd.SetTempAngle(angle)



    def EndSetSliderValue(self, *args):
        uthread.new(self.DirectionSearch)



    def UseOverviewChanged(self, checked):
        settings.user.ui.Set('scannerusesoverviewsettings', self.sr.useoverview.checked)



    def LoadResultList(self):
        if self.destroyed:
            return 
        scanSvc = sm.GetService('scanSvc')
        currentScan = scanSvc.GetCurrentScan()
        scanningProbes = scanSvc.GetScanningProbes()
        results = scanSvc.GetScanResults()
        if self.destroyed:
            return 
        self.CleanupResultShapes()
        resultlist = []
        if currentScan and blue.os.TimeDiffInMs(currentScan.startTime, blue.os.GetSimTime()) < currentScan.duration:
            data = util.KeyVal()
            data.header = localization.GetByLabel('UI/Inflight/Scanner/Analyzing')
            data.startTime = currentScan.startTime
            data.duration = currentScan.duration
            resultlist.append(listentry.Get('Progress', data=data))
        elif scanningProbes and session.shipid not in scanningProbes:
            data = util.KeyVal()
            data.label = localization.GetByLabel('UI/Inflight/Scanner/WaitingForProbes')
            data.hideLines = 1
            resultlist.append(listentry.Get('Generic', data=data))
        elif results:
            bp = sm.GetService('michelle').GetBallpark(doWait=True)
            if bp is None:
                return 
            ego = bp.balls[bp.ego]
            myPos = Vector3(ego.x, ego.y, ego.z)
            for result in results:
                if result.id in scanSvc.resultsIgnored:
                    continue
                if self.currentFilter is not None and len(self.currentFilter) > 0:
                    if result.certainty >= const.probeResultGood:
                        if result.groupID == const.groupCosmicSignature:
                            if (result.groupID, result.strengthAttributeID) not in self.currentFilter:
                                continue
                        elif result.groupID not in self.currentFilter:
                            continue
                    elif result.scanGroupID not in self.activeScanGroupInFilter:
                        continue
                id = result.id
                probeID = result.probeID
                certainty = result.certainty
                typeID = result.Get('typeID', None)
                result.typeName = None
                result.groupName = None
                result.scanGroupName = self.scanGroups[result.scanGroupID]
                if certainty >= const.probeResultGood:
                    explorationSite = result.groupID in (const.groupCosmicAnomaly, const.groupCosmicSignature)
                    if explorationSite:
                        result.groupName = self.GetExplorationSiteType(result.strengthAttributeID)
                    else:
                        result.groupName = cfg.invgroups.Get(result.groupID).name
                    if certainty >= const.probeResultInformative:
                        if explorationSite:
                            result.typeName = result.dungeonName
                        else:
                            result.typeName = cfg.invtypes.Get(typeID).name
                if isinstance(result.data, Vector3):
                    dist = (result.data - myPos).Length()
                elif isinstance(result.data, float):
                    dist = result.data
                    certainty = min(0.9999, certainty)
                else:
                    dist = (result.data.point - myPos).Length()
                    certainty = min(0.9999, certainty)
                texts = [result.id,
                 result.scanGroupName,
                 result.groupName or '',
                 result.typeName or '',
                 localization.GetByLabel('UI/Inflight/Scanner/SignalStrengthPercentage', signalStrength=min(1.0, certainty) * 100),
                 util.FmtDist(dist)]
                sortdata = [result.id,
                 result.scanGroupName,
                 result.groupName or '',
                 result.typeName or '',
                 min(1.0, certainty) * 100,
                 dist]
                data = util.KeyVal()
                data.texts = texts
                data.sortData = sortdata
                data.columnID = 'probeResultGroupColumn'
                data.result = result
                data.GetMenu = self.ResultMenu
                resultlist.append(listentry.Get('ColumnLine', data=data))

            resultlist = listentry.SortColumnEntries(resultlist, 'probeResultGroupColumn')
            data = util.KeyVal()
            data.texts = [localization.GetByLabel('UI/Common/ID'),
             localization.GetByLabel('UI/Inflight/Scanner/ScanGroup'),
             localization.GetByLabel('UI/Inventory/ItemGroup'),
             localization.GetByLabel('UI/Common/Type'),
             localization.GetByLabel('UI/Inflight/Scanner/SignalStrength'),
             localization.GetByLabel('UI/Common/Distance')]
            data.columnID = 'probeResultGroupColumn'
            data.editable = True
            data.showBottomLine = True
            data.selectable = False
            data.hilightable = False
            resultlist.insert(0, listentry.Get('ColumnLine', data=data))
            listentry.InitCustomTabstops(data.columnID, resultlist)
        if not resultlist:
            data = util.KeyVal()
            data.label = localization.GetByLabel('UI/Inflight/Scanner/NoScanResult')
            data.hideLines = 1
            resultlist.append(listentry.Get('Generic', data=data))
        resultlist.append(listentry.Get('Line', data=util.KeyVal(height=1)))
        self.sr.resultscroll.Load(contentList=resultlist)
        self.sr.resultscroll.ShowHint('')
        self.HighlightGoodResults()



    def ClearScanResult(self, *args):
        data = util.KeyVal()
        data.label = localization.GetByLabel('UI/Inflight/Scanner/NoScanResult')
        data.hideLines = 1
        self.sr.resultscroll.Load(contentList=[listentry.Get('Generic', data=data)])
        self.sr.resultscroll.ShowHint('')



    def GetProbeEntry(self, probe, selectedIDs = None):
        selectedIDs = selectedIDs or []
        data = util.KeyVal()
        (data.texts, data.sortData,) = self.GetProbeLabelAndSortData(probe)
        data.columnID = 'probeGroupColumn'
        data.probe = probe
        data.probeID = probe.probeID
        data.isSelected = probe.probeID in selectedIDs
        data.GetMenu = self.GetProbeMenu
        data.scanRangeSteps = sm.GetService('scanSvc').GetScanRangeStepsByTypeID(probe.typeID)
        iconPar = uicls.Container(name='iconParent', parent=None, align=uiconst.TOPLEFT, width=36, height=16, state=uiconst.UI_PICKCHILDREN)
        icon1 = uicls.Icon(parent=iconPar, icon='ui_38_16_181', pos=(0, 0, 16, 16), align=uiconst.RELATIVE)
        icon1.hint = localization.GetByLabel('UI/Inflight/Scanner/RecoverProbe')
        icon1.probeID = probe.probeID
        icon1.OnClick = (self.RecoverProbeClick, icon1)
        icon2 = uicls.Icon(parent=iconPar, icon='ui_38_16_182', pos=(20, 0, 16, 16), align=uiconst.RELATIVE)
        icon2.hint = localization.GetByLabel('UI/Inflight/Scanner/DestroyProbe')
        icon2.probeID = probe.probeID
        icon2.OnClick = (self.DestroyProbeClick, icon2)
        data.overlay = iconPar
        entry = listentry.Get('ColumnLine', data=data)
        return entry



    def LoadProbeList(self):
        selectedIDs = self.GetSelectedProbes(asIds=1)
        scans = sm.GetService('scanSvc')
        scrolllist = []
        for (probeID, probe,) in scans.GetProbeData().items():
            if cfg.invtypes.Get(probe.typeID).groupID in self._Scanner__disallowanalysisgroups:
                continue
            entry = self.GetProbeEntry(probe, selectedIDs)
            scrolllist.append(entry)

        scrolllist = listentry.SortColumnEntries(scrolllist, 'probeGroupColumn')
        if not len(scrolllist):
            data = util.KeyVal()
            data.label = localization.GetByLabel('UI/Inflight/Scanner/OnBoardScanner')
            data.hideLines = 1
            scrolllist.append(listentry.Get('Generic', data=data))
        else:
            data = util.KeyVal()
            data.texts = [localization.GetByLabel('UI/Common/ID'),
             localization.GetByLabel('UI/Inflight/Scanner/Range'),
             localization.GetByLabel('UI/Inflight/Scanner/ExpiresIn'),
             localization.GetByLabel('UI/Inflight/Scanner/Status'),
             localization.GetByLabel('UI/Inflight/Scanner/Active')]
            data.columnID = 'probeGroupColumn'
            data.editable = True
            data.showBottomLine = True
            data.selectable = False
            data.hilightable = False
            scrolllist.insert(0, listentry.Get('ColumnLine', data=data))
            listentry.InitCustomTabstops(data.columnID, scrolllist)
        scrolllist.append(listentry.Get('Line', data=util.KeyVal(height=1)))
        self.sr.scroll.Load(contentList=scrolllist)
        self.sr.scroll.ShowHint('')
        self.UpdateProbeList()
        self.sr.updateProbes = base.AutoTimer(1000, self.UpdateProbeList)
        self.CheckButtonStates()
        self.sr.loadProbeList = None



    def GetProbeLabelAndSortData(self, probe, entry = None):
        if probe.expiry is None:
            expiryText = localization.GetByLabel('UI/Generic/None')
        else:
            expiry = max(0L, long(probe.expiry) - blue.os.GetSimTime())
            if expiry <= 0:
                expiryText = localization.GetByLabel('UI/Inflight/Scanner/Expired')
            else:
                expiryText = util.FmtDate(expiry, 'ss')
        scanSvc = sm.GetService('scanSvc')
        isActive = scanSvc.IsProbeActive(probe.probeID)
        probeStateSortText = util.FmtProbeState(probe.state)
        probeStateDisplayText = util.FmtProbeState(probe.state, colorize=True)
        if entry:
            sortData = entry.sortData[:]
            texts = entry.texts[:]
            sortData[4] = isActive
            texts[4].SetChecked(isActive, report=0)
            sortData[1] = probe.scanRange
            texts[1] = util.FmtDist(probe.scanRange)
            sortData[2] = probe.expiry
            texts[2] = expiryText
            sortData[3] = probeStateSortText
            texts[3] = probeStateDisplayText
        else:
            label = scanSvc.GetProbeLabel(probe.probeID)
            invType = cfg.invtypes.Get(probe.typeID)
            sortData = [probe.probeID,
             probe.scanRange,
             probe.expiry,
             probeStateSortText,
             isActive]
            checkBox = uicls.Checkbox(text='', parent=None, configName='probeactive', retval=probe.probeID, checked=isActive, callback=self.OnProbeCheckboxChange, align=uiconst.CENTER)
            checkBox.hint = localization.GetByLabel('UI/Inflight/Scanner/MakeActive')
            texts = [label,
             util.FmtDist(probe.scanRange),
             expiryText,
             probeStateDisplayText,
             checkBox]
        return (texts, sortData)



    def OnProbeCheckboxChange(self, checkbox, *args):
        selected = self.sr.scroll.GetSelected()
        probeIDs = [ each.probe.probeID for each in selected if getattr(each, 'probe') ]
        probeID = checkbox.data['value']
        if probeID not in probeIDs:
            probeIDs = [probeID]
        for probeID in probeIDs:
            sm.GetService('scanSvc').SetProbeActiveState(probeID, checkbox.checked)

        self.UpdateProbeList()
        self.CheckButtonStates()



    def UpdateProbeList(self):
        if self is None or self.destroyed:
            self.sr.updateProbes = None
            return 
        bracketsByProbeID = {}
        for each in uicore.layer.systemMapBrackets.children[:]:
            probe = getattr(each, 'probe', None)
            if probe is None:
                continue
            bracketsByProbeID[probe.probeID] = each

        probeEntries = []
        for entry in self.sr.scroll.GetNodes():
            if entry.Get('probe', None) is None:
                continue
            probe = entry.probe
            (newtexts, newsortData,) = self.GetProbeLabelAndSortData(probe, entry)
            if newtexts != entry.texts or newsortData != entry.sortData:
                entry.needReload = 1
            else:
                entry.needReload = 0
            entry.sortData = newsortData
            entry.texts = newtexts
            probeEntries.append(entry)
            bracket = bracketsByProbeID.get(probe.probeID, None)
            if bracket:
                bracket.displayName = localization.GetByLabel('UI/Inflight/Scanner/ProbeBracket', probeLabel=newtexts[0], probeStatus=newtexts[3], probeRange=newtexts[1])

        self.sr.scroll.state = uiconst.UI_DISABLED
        self.UpdateColumnSort(probeEntries, 'probeGroupColumn')
        self.sr.scroll.state = uiconst.UI_NORMAL



    def UpdateColumnSort(self, entries, columnID):
        if not entries:
            return 
        startIdx = entries[0].idx
        endIdx = entries[-1].idx
        entries = listentry.SortColumnEntries(entries, columnID)
        self.sr.scroll.sr.nodes = self.sr.scroll.sr.nodes[:startIdx] + entries + self.sr.scroll.sr.nodes[(endIdx + 1):]
        self.sr.scroll.UpdatePosition('UpdateColumnSort_Scanner')
        idx = 0
        for entry in self.sr.scroll.GetNodes()[startIdx:]:
            if entry.Get('needReload', 0) and entry.panel:
                entry.panel.LoadLite(entry)
            idx += 1




    def ValidateProbesState(self, probeIDs, isEntryButton = False):
        scanSvc = sm.GetService('scanSvc')
        probeData = scanSvc.GetProbeData()
        for probeID in probeIDs:
            if probeID in probeData:
                probe = probeData[probeID]
                if isEntryButton:
                    if probe.state not in (const.probeStateIdle, const.probeStateInactive):
                        return False
                elif probe.state != const.probeStateIdle:
                    return False

        return True



    def CheckButtonStates(self):
        probes = sm.GetService('scanSvc').GetActiveProbes()
        scanningProbes = sm.GetService('scanSvc').GetScanningProbes()
        allIdle = self.ValidateProbesState(probes)
        if probes and allIdle:
            self.sr.destroyBtn.Enable()
            self.sr.recoverBtn.Enable()
        else:
            self.sr.destroyBtn.Disable()
            self.sr.destroyBtn.opacity = 0.25
            self.sr.recoverBtn.Disable()
            self.sr.recoverBtn.opacity = 0.25
        canClaim = sm.GetService('scanSvc').CanClaimProbes()
        if canClaim:
            self.sr.reconnectBtn.Enable()
        else:
            self.sr.reconnectBtn.Disable()
            self.sr.reconnectBtn.opacity = 0.25
        if scanningProbes:
            self.sr.analyzeBtn.Disable()
            self.sr.analyzeBtn.opacity = 0.25
        else:
            self.sr.analyzeBtn.Enable()



    def OnModuleOnlineChange(self, item, oldValue, newValue):
        if item.groupID == const.groupScanProbeLauncher:
            self.CheckButtonStates()



    def GetShipScannerEntry(self):
        scanRange = 5
        label = '%s<t>%s<t>%s' % (localization.GetByLabel('UI/Inflight/Scanner/OnBoardScanner'), util.FmtDist(scanRange * const.AU), '')
        data = util.KeyVal()
        data.label = label
        data.probe = None
        data.probeID = eve.session.shipid
        data.isSelected = False
        data.GetMenu = self.GetProbeMenu
        return listentry.Get('Generic', data=data)



    def GetProbeMenu(self, entry, *args):
        probeIDs = self.GetSelectedProbes(asIds=1)
        return sm.GetService('scanSvc').GetProbeMenu(entry.sr.node.probeID, probeIDs)



    @UserErrorIfScanning
    def DestroyActiveProbes(self, *args):
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetActiveProbes()
        allIdle = self.ValidateProbesState(probes)
        if probes and allIdle and eve.Message('DestroyProbes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            for _probeID in probes[:]:
                if scanSvc.GetProbeState(_probeID) != const.probeStateIdle:
                    self.ClearScanResult()
                scanSvc.DestroyProbe(_probeID)




    @UserErrorIfScanning
    def DestroyProbeClick(self, icon):
        probeID = getattr(icon, 'probeID', None)
        probes = [probeID]
        allIdle = self.ValidateProbesState(probes, True)
        if probeID and allIdle and eve.Message('DestroySelectedProbes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('scanSvc').DestroyProbe(probeID)



    @UserErrorIfScanning
    def ReconnectToLostProbes(self, *args):
        self.sr.reconnectBtn.opacity = 0.25
        sm.GetService('scanSvc').ReconnectToLostProbes()
        self.LoadProbeList()



    @UserErrorIfScanning
    def RecoverActiveProbes(self, *args):
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetProbeData()
        recall = [ pID for (pID, p,) in probes.iteritems() if p.state == const.probeStateIdle ]
        scanSvc.RecoverProbes(recall)



    @UserErrorIfScanning
    def RecoverProbeClick(self, icon):
        probeID = getattr(icon, 'probeID', None)
        if not probeID:
            return 
        sm.GetService('scanSvc').RecoverProbes([probeID])



    def GetSelectedProbes(self, asIds = 0):
        selected = self.sr.scroll.GetSelected()
        retval = []
        for each in selected:
            if each.Get('probe', None) is not None:
                if asIds:
                    retval.append(each.probe.probeID)
                else:
                    retval.append(each)

        return retval



    def UpdateProbeSpheres(self, *args):
        if getattr(self, 'isUpdatingProbeSpheres', False):
            return 
        try:
            self.isUpdatingProbeSpheres = True
            scanSvc = sm.GetService('scanSvc')
            bp = sm.GetService('michelle').GetBallpark()
            if not bp or eve.session.shipid not in bp.balls or not sm.GetService('viewState').IsViewActive('systemmap'):
                self.Cleanup()
                return 
            parent = self.GetSystemParent()
            probeData = scanSvc.GetProbeData()
            probeIDs = self.sr.probeSpheresByID.keys()[:]
            for probeID in probeIDs:
                if probeID not in probeData or probeData[probeID].state == const.probeStateInactive:
                    probeControl = self.sr.probeSpheresByID[probeID]
                    for bracket in uicore.layer.systemMapBrackets.children[:]:
                        if getattr(bracket, 'probeID', None) == probeID:
                            bracket.trackTransform = None
                            bracket.Close()

                    if probeControl.locator in parent.children:
                        parent.children.remove(probeControl.locator)
                    del self.sr.probeSpheresByID[probeID]

            for (probeID, probe,) in probeData.items():
                if probe.state == const.probeStateInactive:
                    continue
                if probeID not in self.sr.probeSpheresByID:
                    probeControl = xtriui.ProbeControl(probeID, probe, parent, self)
                    self.sr.probeSpheresByID[probeID] = probeControl
                else:
                    probeControl = self.sr.probeSpheresByID[probeID]
                probeControl.SetRange(probe.scanRange)
                probeControl.SetPosition(probe.destination)
                self.UpdateProbeState(probeID, probe.state)

            self.HighlightProbeIntersections()
            sm.GetService('systemmap').HighlightItemsWithinProbeRange()

        finally:
            self.isUpdatingProbeSpheres = False
            self.sr.updateProbeSpheresTimer = None




    def HighlightProbeIntersections(self):
        scanSvc = sm.GetService('scanSvc')
        if self.sr.distanceRings:
            movingProbeID = self.sr.distanceRings.probeID
        else:
            movingProbeID = None
        probeIDs = scanSvc.GetActiveProbes()
        probeIDs.sort()
        possiblePairs = [ tuple(c) for c in util.xuniqueCombinations(probeIDs, 2) ]
        activePairs = []
        for pair in possiblePairs:
            pair = tuple(pair)
            (id1, id2,) = tuple(pair)
            probe1 = self.GetProbeSphere(id1)
            probe2 = self.GetProbeSphere(id2)
            if not probe1 or not probe2:
                self.RemoveIntersection(pair)
                continue
            pos1 = probe1.GetPosition()
            radius1 = probe1.GetRange()
            pos2 = probe2.GetPosition()
            radius2 = probe2.GetRange()
            distance = geo2.Vec3Length(pos1 - pos2)
            if distance > 0.0 and distance < radius1 + radius2:
                if radius1 > distance + radius2 or radius2 > distance + radius1:
                    self.RemoveIntersection(pair)
                if pair not in self.sr.probeIntersectionsByPair:
                    self.CreateIntersectionHighlight(pair)
                intersection = self.sr.probeIntersectionsByPair[pair]
                newConfig = (pos1,
                 pos2,
                 radius1,
                 radius2)
                if newConfig != intersection.lastConfig:
                    intersection.lastConfig = newConfig
                    self.SetIntersectionColor(intersection, INTERSECTION_ACTIVE)
                    self.UpdateIntersectionHighlight(pair, distance)
                    activePairs.append(pair)
                else:
                    if movingProbeID in pair:
                        self.SetIntersectionColor(intersection, INTERSECTION_ACTIVE)
                        activePairs.append(pair)
                    else:
                        self.SetIntersectionColor(intersection, INTERSECTION_FADED)
            else:
                self.RemoveIntersection(pair)

        for pair in self.sr.probeIntersectionsByPair.keys():
            if pair not in possiblePairs:
                self.RemoveIntersection(pair)

        self.UpdateDistanceRings()
        self.sr.deactivatingIntersections = False
        self.sr.fadeActiveIntersectionsTimer = base.AutoTimer(500, self.FadeActiveIntersections, activePairs)
        self.sr.deactivateIntersectionsTimer = base.AutoTimer(3000, self.DeactivateIntersections)



    def RemoveIntersection(self, pair):
        scene = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if not scene:
            return 
        if pair in self.sr.probeIntersectionsByPair:
            intersection = self.sr.probeIntersectionsByPair[pair]
            if intersection.lineSet in scene.objects:
                scene.objects.remove(intersection.lineSet)
            del self.sr.probeIntersectionsByPair[pair]



    def UpdateIntersectionHighlight(self, pair, distance):
        intersection = self.sr.probeIntersectionsByPair[pair]
        data = self.ComputeHighlightCircle(distance, *intersection.lastConfig)
        if data:
            (point, rotation, radius,) = data
            lineSet = intersection.lineSet
            lineSet.translationCurve.value.SetXYZ(*point)
            lineSet.rotationCurve.value.SetXYZW(*rotation)
            lineSet.scaling = (radius, radius, radius)
        else:
            self.RemoveIntersection(pair)



    def ComputeHighlightCircle(self, distance, pos1, pos2, rad1, rad2):
        rad1_sq = rad1 ** 2
        rad2_sq = rad2 ** 2
        dist_sq = distance ** 2
        distToPoint = (rad1_sq - rad2_sq + dist_sq) / (2 * distance)
        radius_sq = rad1_sq - distToPoint ** 2
        if radius_sq < 0.0:
            return None
        radius = math.sqrt(radius_sq)
        normal = geo2.Vec3Normalize(pos2 - pos1)
        normal = geo2.Vector(*normal)
        point = pos1 + normal * distToPoint
        rotation = geo2.QuaternionRotationArc(AXIS_Y, normal)
        return (point * SYSTEMMAP_SCALE, rotation, radius * SYSTEMMAP_SCALE)



    def CreateIntersectionHighlight(self, pair):
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if not scene2:
            return 
        lineSet = self.CreateLineSet()
        scene2.objects.append(lineSet)
        self.DrawCircle(lineSet, 1.0, INTERSECTION_COLOR)
        lineSet.SubmitChanges()
        lineSet.translationCurve = trinity.TriVectorCurve()
        lineSet.rotationCurve = trinity.TriRotationCurve()
        intersection = util.KeyVal(lastConfig=None, lineSet=lineSet, colorState=INTERSECTION_ACTIVE)
        self.sr.probeIntersectionsByPair[pair] = intersection



    def DrawCircle(self, lineSet, size, color):
        for idx in xrange(CIRCLE_NUM_POINTS):
            p1 = CIRCLE_POINTS[idx]
            p2 = CIRCLE_POINTS[((idx + 1) % CIRCLE_NUM_POINTS)]
            lineSet.AddLine((p1[0] * size, p1[1] * size, p1[2] * size), color, (p2[0] * size, p2[1] * size, p2[2] * size), color)




    def FadeActiveIntersections(self, activePairs):
        if self.sr.distanceRings and self.sr.distanceRings.probeID:
            return 
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        while ndt != 1.0:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 500.0, 1.0))
            colorRatio = mathUtil.Lerp(INTERSECTION_ACTIVE, INTERSECTION_FADED, ndt)
            for pair in activePairs:
                if pair in self.sr.probeIntersectionsByPair:
                    intersection = self.sr.probeIntersectionsByPair[pair]
                    self.SetIntersectionColor(intersection, colorRatio)

            blue.pyos.synchro.SleepWallclock(50)
            if self.destroyed:
                return 

        self.sr.fadeActiveIntersectionsTimer = None



    def DeactivateIntersections(self):
        self.sr.deactivatingIntersections = True
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        while self.sr.deactivatingIntersections and ndt != 1.0:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 2000.0, 1.0))
            colorRatio = mathUtil.Lerp(INTERSECTION_FADED, INTERSECTION_INACTIVE, ndt)
            for intersection in self.sr.probeIntersectionsByPair.itervalues():
                self.SetIntersectionColor(intersection, colorRatio)

            blue.pyos.synchro.SleepWallclock(100)
            if self.destroyed:
                return 

        self.sr.deactivateIntersectionsTimer = None



    def SetIntersectionColor(self, intersection, colorState = 1.0):
        if intersection.colorState == colorState:
            return 
        intersection.colorState = colorState
        color = (INTERSECTION_COLOR[0] * colorState,
         INTERSECTION_COLOR[1] * colorState,
         INTERSECTION_COLOR[2] * colorState,
         1.0)
        lineSet = intersection.lineSet
        for i in xrange(CIRCLE_NUM_POINTS):
            intersection.lineSet.ChangeLineColor(i, color, color)

        lineSet.SubmitChanges()



    def ShowDistanceRings(self, probeControl, axis):
        scene = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene:
            if not self.sr.distanceRings:
                lineSet = trinity.EveCurveLineSet()
                lineSet.additive = True
                tex2D = trinity.TriTexture2DParameter()
                tex2D.name = 'TexMap'
                tex2D.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
                lineSet.lineEffect.resources.append(tex2D)
                baseColor = RANGE_INDICATOR_CIRCLE_COLOR
                for (i, r,) in enumerate(DISTANCE_RING_RANGES):
                    div = 1.0 + i * 0.5
                    color = (baseColor[0] / div,
                     baseColor[1] / div,
                     baseColor[2] / div,
                     1.0)
                    unitcircle = ((r, 0, 0),
                     (0, 0, r),
                     (-r, 0, 0),
                     (0, 0, -r))
                    for i in xrange(4):
                        (a, b,) = (unitcircle[(i - 1)], unitcircle[i])
                        lineID = lineSet.AddSpheredLineCrt(a, color, b, color, (0, 0, 0), DISTRING_LINE_WIDTH)
                        lineSet.ChangeLineSegmentation(lineID, 10 * r)


                lineSet.AddStraightLine((MAX_DIST_RING_RANGE, 0.0, 0.0), RANGE_INDICATOR_CROSS_COLOR, (-MAX_DIST_RING_RANGE, 0.0, 0.0), RANGE_INDICATOR_CROSS_COLOR, DISTRING_LINE_WIDTH)
                lineSet.AddStraightLine((0.0, 0.0, MAX_DIST_RING_RANGE), RANGE_INDICATOR_CROSS_COLOR, (0.0, 0.0, -MAX_DIST_RING_RANGE), RANGE_INDICATOR_CROSS_COLOR, DISTRING_LINE_WIDTH)
                lineSet.SubmitChanges()
                self.sr.distanceRings = util.KeyVal(__doc__='distanceRings', lineSet=lineSet)
            if self.sr.distanceRings.lineSet not in probeControl.locator.children:
                probeControl.locator.children.append(self.sr.distanceRings.lineSet)
            self.sr.distanceRings.axis = axis
            self.sr.distanceRings.probeID = probeControl.probeID
            self.UpdateDistanceRings()



    def UpdateDistanceRings(self):
        if self.sr.distanceRings:
            probeControl = self.GetProbeSphere(self.sr.distanceRings.probeID)
            if probeControl:
                lineSet = self.sr.distanceRings.lineSet
                axis = self.sr.distanceRings.axis
                location = probeControl.GetWorldPosition()
                scale = probeControl.GetRange() / MAX_DIST_RING_RANGE
                lineSet.scaling = (scale, scale, scale)
                if axis == 'xy':
                    lineSet.rotation = (SQRT_05,
                     0.0,
                     0.0,
                     SQRT_05)
                elif axis == 'yz':
                    lineSet.rotation = (SQRT_05,
                     SQRT_05,
                     0.0,
                     0.0)
                elif axis == 'xz':
                    lineSet.rotation = (0.0, 0.0, 0.0, 0.0)
                else:
                    self.HideDistanceRings()



    def HideDistanceRings(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if self.sr.distanceRings and scene:
            parent = self.GetSystemParent()
            for tr in parent.children:
                if self.sr.distanceRings.lineSet in tr.children:
                    tr.children.remove(self.sr.distanceRings.lineSet)

            self.sr.distanceRings.axis = None
            self.sr.distanceRings.probeID = None



    def ScaleProbe(self, probeControl, pos, force = 0):
        pVector = trinity.TriVector(*probeControl.locator.translation)
        cVector = trinity.TriVector(*(pos * (1.0 / SYSTEMMAP_SCALE)))
        s = max(probeControl.scanRanges[0], (pVector - cVector).Length())
        probeControl.SetRange(s)
        closest = probeControl.scanRanges[-1]
        for scanRange in probeControl.scanRanges:
            if not closest or abs(scanRange - s) <= abs(closest - s):
                closest = scanRange

        probeData = sm.GetService('scanSvc').GetProbeData()
        if probeControl and (getattr(self, 'lastScaleUpdate', None) or force):
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if shift:
                range = probeControl.GetRange()
                for (_probeID, _probe,) in sm.GetService('scanSvc').GetProbeData().iteritems():
                    if _probeID == probeControl.probeID:
                        continue
                    _probeControl = self.GetProbeSphere(_probeID)
                    if _probeControl is None:
                        continue
                    _probeControl.SetRange(range)

            else:
                for (_probeID, _probe,) in sm.GetService('scanSvc').GetProbeData().iteritems():
                    if _probeID == probeControl.probeID:
                        continue
                    _probeControl = self.GetProbeSphere(_probeID)
                    if _probeControl is None:
                        continue
                    _probeControl.SetRange(_probe.scanRange)

        self.HighlightProbeIntersections()
        self.lastScaleUpdate = (probeControl.probeID, pos)
        probeControl.bracket.displayName = localization.GetByLabel('UI/Inflight/Scanner/ProbeRange', curDist=util.FmtDist(s), maxDist=util.FmtDist(closest))
        if getattr(probeControl.bracket, 'label', None):
            probeControl.bracket.label.UpdateLabelAndOffset()
        sm.GetService('systemmap').HighlightItemsWithinProbeRange()
        probeControl.ShowScanRanges()



    def RegisterProbeRange(self, probeControl):
        self.lastScaleUpdate = None
        targetRange = probeControl.GetRange()
        closest = probeControl.scanRanges[-1]
        for scanRange in probeControl.scanRanges:
            if not closest or abs(scanRange - targetRange) <= abs(closest - targetRange):
                closest = scanRange

        if closest:
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if shift:
                probeIDs = sm.GetService('scanSvc').GetActiveProbes()
            else:
                probeIDs = [probeControl.probeID]
            rangeStep = probeControl.scanRanges.index(closest) + 1
            for _probeID in probeIDs:
                self.UpdateProbeRangeUI(_probeID, closest, rangeStep)
                sm.GetService('scanSvc').SetProbeRangeStep(_probeID, rangeStep)

        sm.GetService('systemmap').HighlightItemsWithinProbeRange()
        self.HighlightProbeIntersections()
        probeControl.HideScanRanges()



    def UpdateProbeRangeUI(self, probeID, range, rangeStep):
        probe = self.GetProbeSphere(probeID)
        if probe:
            probe.SetRange(range)



    def GetProbeSphere(self, probeID):
        return self.sr.probeSpheresByID.get(probeID, None)



    def GetProbeSpheres(self):
        return self.sr.probeSpheresByID



    def HiliteCursor(self, pickObject = None):
        for (probeID, probeControl,) in self.sr.probeSpheresByID.iteritems():
            probeControl.ResetCursorHighlight()

        cursor = None
        if pickObject:
            (cursorName, side, probeID,) = pickObject.name.split('_')
            hiliteAxis = cursorName[6:]
            probeID = int(probeID)
            if probeID in self.sr.probeSpheresByID:
                probeControl = self.sr.probeSpheresByID[probeID]
                probeControl.HighlightAxis(hiliteAxis)



    def ShowCentroidLines(self):
        if self.centroidLines is None:
            systemMap = sm.GetService('systemmap')
            if systemMap.currentSolarsystem is None:
                return 
            self.centroidLines = trinity.EveCurveLineSet()
            tex2D = trinity.TriTexture2DParameter()
            tex2D.name = 'TexMap'
            tex2D.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
            self.centroidLines.lineEffect.resources.append(tex2D)
            systemMap.currentSolarsystem.children.append(self.centroidLines)
        else:
            self.centroidLines.display = True
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetProbeData()
        probeIDs = [ probeID for (probeID, probe,) in probes.iteritems() if probe.state == const.probeStateIdle ]
        if probeIDs:
            probeIDs.sort()
            update = self.lastProbeIDs == probeIDs
            if not update:
                self.lastProbeIDs = probeIDs
                self.centroidLines.ClearLines()
            centroid = geo2.Vector(0, 0, 0)
            probePositions = []
            for (index, probeID,) in enumerate(probeIDs):
                probeControl = self.GetProbeSphere(probeID)
                if probeControl:
                    p = Vector3(*probeControl.GetPosition())
                    centroid += p
                    probePositions.append((p.x, p.y, p.z))

            centroid /= len(probeIDs)
            c = (centroid.x, centroid.y, centroid.z)
            for (index, position,) in enumerate(probePositions):
                if update:
                    self.centroidLines.ChangeLinePositionCrt(index, c, position)
                else:
                    self.centroidLines.AddStraightLine(c, CENTROID_LINE_COLOR, position, CENTROID_LINE_COLOR, CENTROID_LINE_WIDTH)
                self.centroidLines.ChangeLineAnimation(index, CENTROID_LINE_COLOR, -0.25, 10.0)

            self.centroidLines.SubmitChanges()
        self.centroidTimer = base.AutoTimer(500, self.RemoveCentroidLines)



    def RemoveCentroidLines(self):
        if self.centroidLines is not None:
            self.centroidLines.display = False
        self.centroidTimer = None



    def RegisterProbeMove(self, *args):
        self.lastMoveUpdate = None
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetProbeData()
        for (probeID, probe,) in probes.iteritems():
            if probe.state != const.probeStateIdle:
                continue
            probeControl = self.GetProbeSphere(probeID)
            if probeControl:
                cachedPos = Vector3(*probes[probeID].destination)
                currentPos = Vector3(*probeControl.locator.translation)
                if (cachedPos - currentPos).Length():
                    scanSvc.SetProbeDestination(probeID, currentPos)

        sm.GetService('systemmap').HighlightItemsWithinProbeRange()



    def MoveProbe(self, probeControl, translation):
        probeControl.ShiftPosition(translation)
        scanSvc = sm.GetService('scanSvc')
        probeID = probeControl.probeID
        probes = scanSvc.GetProbeData()
        if probeID not in probes:
            return 
        cachedPos = Vector3(*probes[probeID].destination)
        currentPos = Vector3(*probeControl.locator.translation)
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            diffPos = currentPos - cachedPos
            for (_probeID, probe,) in probes.iteritems():
                if _probeID == probeID or probe.state != const.probeStateIdle:
                    continue
                _probeControl = self.GetProbeSphere(_probeID)
                if _probeControl is None:
                    continue
                _cachedPos = Vector3(*probes[_probeID].destination)
                _newPos = _cachedPos + diffPos
                _probeControl.SetPosition(_newPos)

        self.lastMoveUpdate = (probeControl.probeID, translation)
        sm.GetService('systemmap').HighlightItemsWithinProbeRange()
        self.HighlightProbeIntersections()



    def CancelProbeMoveOrScaling(self, *args):
        for (probeID, probe,) in sm.GetService('scanSvc').GetProbeData().iteritems():
            if probe.state != const.probeStateIdle:
                continue
            probeControl = self.GetProbeSphere(probeID)
            probeControl.SetPosition(probe.destination)
            probeControl.SetRange(probe.scanRange)
            probeControl.HideScanRanges()

        sm.GetService('systemmap').HighlightItemsWithinProbeRange()



    @UserErrorIfScanning
    def Analyze(self, *args):
        self.sr.analyzeBtn.Disable()
        self.sr.analyzeBtn.opacity = 0.25
        scanSvc = sm.GetService('scanSvc')
        try:
            scanSvc.RequestScans()
        except UserError as e:
            self.CheckButtonStates()
            raise e
        self.LoadResultList()



    def ResultMenu(self, panel, *args):
        result = panel.sr.node.result
        scanSvc = sm.GetService('scanSvc')
        menu = []
        if result.certainty >= const.probeResultPerfect and isinstance(result.data, Vector3):
            if IsResultWithinWarpDistance(result):
                menu += sm.GetService('menu').SolarsystemScanMenu(result.id)
            menu.append(None)
            bookmarkData = util.KeyVal(id=result.id, position=result.data, name=result.typeName)
            menu.append((localization.GetByLabel('UI/Inflight/BookmarkLocation'), sm.GetService('addressbook').BookmarkLocationPopup, (eve.session.solarsystemid,
              None,
              None,
              None,
              bookmarkData)))
            menu.append(None)
        nodes = self.sr.resultscroll.GetSelected()
        idList = tuple(set([ n.result.id for n in nodes if hasattr(n.result, 'id') ]))
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/IngoreResult'), scanSvc.IgnoreResult, idList))
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/IgnoreOtherResults'), scanSvc.IgnoreOtherResults, idList))
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/ClearResult'), scanSvc.ClearResults, idList))
        return menu



    def OnSelectionChange(self, entries):
        self.DisplaySelectedResults()



    def DisplaySelectedResults(self):
        if 'scanresult' not in maputils.GetVisibleSolarsystemBrackets():
            self.HideAllResults()
        else:
            nodes = self.sr.resultscroll.GetSelected()
            excludeSet = set()
            for entry in nodes:
                if entry.result:
                    self.DisplayResult(entry.result)
                    if entry.result in self.sr.resultObjectsByID:
                        excludeSet.add(entry.result)

            resultSet = set(self.sr.resultObjectsByID.keys())
            resultsToHide = resultSet - excludeSet
            for resultID in resultsToHide:
                self.HideResult(resultID)




    def HideAllResults(self):
        for resultID in self.sr.resultObjectsByID.keys():
            self.HideResult(resultID)




    def DisplayResult(self, result):
        if result in self.sr.resultObjectsByID:
            obj = self.sr.resultObjectsByID[result]
            if obj.__bluetype__ in ('trinity.EveTransform', 'trinity.EveRootTransform'):
                obj.display = 1
            elif obj.__bluetype__ == 'trinity.EveLineSet':
                scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
                if scene2:
                    if obj not in scene2.objects:
                        scene2.objects.append(obj)
            elif isinstance(obj, uicls.Bracket):
                obj.state = uiconst.UI_PICKCHILDREN
                if 'scanresult' in maputils.GetHintsOnSolarsystemBrackets():
                    obj.ShowBubble(obj.hint)
                else:
                    obj.ShowBubble(None)
        elif isinstance(result.data, float):
            self.CreateSphereResult(result)
        elif isinstance(result.data, Vector3):
            self.CreatePointResult(result)
        else:
            self.CreateCircleResult(result)



    def HideResult(self, resultID):
        if resultID in self.sr.resultObjectsByID:
            obj = self.sr.resultObjectsByID[resultID]
            if obj.__bluetype__ in ('trinity.EveTransform', 'trinity.EveRootTransform'):
                obj.display = 0
            elif obj.__bluetype__ == 'trinity.EveLineSet':
                scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
                if scene2:
                    if obj in scene2.objects:
                        scene2.objects.remove(obj)
            elif isinstance(obj, uicls.Bracket):
                obj.state = uiconst.UI_HIDDEN



    def CreateSphereResult(self, result):
        sphereSize = result.data
        sphere = trinity.Load('res:/dx9/model/UI/Resultbubble.red')
        sphere.name = 'Result sphere'
        sphere.children[0].scaling = (2.0, 2.0, 2.0)
        sphere.scaling = (sphereSize, sphereSize, sphereSize)
        locator = trinity.EveTransform()
        locator.name = 'scanResult_%s' % result.id
        locator.translation = result.pos.AsTuple()
        locator.children.append(sphere)
        parent = self.GetSystemParent()
        parent.children.append(locator)
        self.sr.resultObjectsByID[result] = locator



    def CreateCircleResult(self, result):
        numPoints = 256
        lineSet = self.CreateLineSet()
        lineSet.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
        parentPos = geo2.Vector(*result.data.point)
        dirVec = geo2.Vector(*result.data.normal)
        radius = result.data.radius
        if radius == 0:
            return 
        fwdVec = geo2.Vector(0.0, 1.0, 0.0)
        dirVec = geo2.Vec3Normalize(dirVec)
        fwdVec = geo2.Vec3Normalize(fwdVec)
        stepSize = pi * 2.0 / numPoints
        rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
        matrix = geo2.MatrixAffineTransformation(1.0, geo2.Vector(0.0, 0.0, 0.0), rotation, parentPos)
        coordinates = []
        for step in xrange(numPoints):
            angle = step * stepSize
            x = cos(angle) * radius
            z = sin(angle) * radius
            pos = geo2.Vector(x, 0.0, z)
            pos = geo2.Vec3TransformCoord(pos, matrix)
            coordinates.append(pos)

        for start in xrange(numPoints):
            end = (start + 1) % numPoints
            lineSet.AddLine(coordinates[start], CIRCLE_COLOR, coordinates[end], CIRCLE_COLOR)

        lineSet.SubmitChanges()
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene2:
            scene2.objects.append(lineSet)
        self.sr.resultObjectsByID[result] = lineSet



    def CreatePointResult(self, result):
        pointLocator = trinity.EveTransform()
        pointLocator.name = 'scanResult_' + result.id
        pointLocator.translation = result.data.AsTuple()
        pointLocator.display = 1
        if result.certainty >= const.probeResultPerfect:
            resultBracket = xtriui.WarpableResultBracket()
        else:
            resultBracket = xtriui.BaseBracket()
        resultBracket.width = resultBracket.height = 16
        resultBracket.name = '__pointResultBracket'
        resultBracket.trackTransform = pointLocator
        resultBracket.resultID = result.id
        resultBracket.result = result
        resultBracket.invisible = False
        resultBracket.align = uiconst.ABSOLUTE
        resultBracket.state = uiconst.UI_NORMAL
        resultBracket.fadeColor = False
        resultBracket.displayName = result.typeName or result.groupName or result.scanGroupName
        resultBracket.groupID = None
        hint = result.scanGroupName
        if result.typeName is not None:
            hint += ': %s' % result.typeName
        elif result.groupName is not None:
            hint += ': %s' % result.groupName
        resultBracket.hint = hint
        if 'scanresult' in maputils.GetHintsOnSolarsystemBrackets():
            resultBracket.ShowBubble(hint)
            resultBracket.showLabel = 0
        if result.certainty >= const.probeResultInformative:
            typeID = result.Get('typeID', None)
            t = cfg.invtypes.Get(typeID)
            groupID = t.groupID
            categoryID = t.categoryID
        elif result.certainty >= const.probeResultGood:
            typeID = None
            groupID = result.Get('groupID', None)
            categoryID = cfg.invgroups.Get(result.groupID).categoryID
        else:
            typeID = None
            groupID = None
            categoryID = result.Get('categoryID', None)
        (iconNo, color,) = self.GetIconBasedOnQuality(categoryID, groupID, typeID, result.certainty)
        resultBracket.Startup(('result', result.id), groupID, categoryID, iconNo)
        resultBracket.sr.icon.color.SetRGB(*color)
        uicore.layer.systemMapBrackets.children.insert(0, resultBracket)
        parent = self.GetSystemParent()
        parent.children.append(pointLocator)
        self.sr.resultObjectsByID[result] = resultBracket



    def GetIconBasedOnQuality(self, categoryID, groupID, typeID, certainty):
        if groupID in (const.groupCosmicAnomaly, const.groupCosmicSignature):
            props = POINT_ICON_DUNGEON
        elif categoryID == const.categoryShip and groupID is None:
            props = sm.GetService('bracket').GetMappedBracketProps(const.categoryShip, const.groupFrigate, None, default=POINT_ICON_PROPS)
        else:
            props = sm.GetService('bracket').GetMappedBracketProps(categoryID, groupID, typeID, default=POINT_ICON_PROPS)
        iconNo = props[0]
        if certainty >= const.probeResultPerfect:
            color = POINT_COLOR_GREEN
        elif certainty >= const.probeResultGood:
            color = POINT_COLOR_YELLOW
        else:
            color = POINT_COLOR_RED
        return (iconNo, color)



    def GetSystemParent(self, create = 1):
        if not create:
            return self.sr.systemParent
        if self.sr.systemParent is None:
            systemParent = trinity.EveTransform()
            systemParent.name = 'systemParent_%d' % session.solarsystemid2
            self.sr.systemParent = systemParent
        if sm.GetService('viewState').IsViewActive('systemmap'):
            currentSystem = sm.GetService('systemmap').GetCurrentSolarSystem()
            if self.sr.systemParent not in currentSystem.children:
                currentSystem.children.append(self.sr.systemParent)
        return self.sr.systemParent



    def CleanupResultShapes(self):
        bracketWnd = uicore.layer.systemMapBrackets
        for bracket in bracketWnd.children[:]:
            if bracket.name == '__pointResultBracket':
                bracket.trackTransform = None
                bracket.Close()

        parent = self.GetSystemParent(0)
        if parent:
            for model in parent.children[:]:
                if model.name.startswith('scanResult_'):
                    parent.children.remove(model)

        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene2:
            for result in self.sr.resultObjectsByID.itervalues():
                if result in scene2.objects:
                    scene2.objects.remove(result)

        self.sr.resultObjectsByID = {}



    def HighlightGoodResults(self):
        for entry in self.sr.resultscroll.GetNodes():
            if entry.Get('result', None) is not None:
                if not isinstance(entry.result.data, float):
                    self.sr.resultscroll._SelectNode(entry)




    def Refresh(self):
        self.sr.doRefresh = base.AutoTimer(200, self.DoRefresh)



    def DoRefresh(self):
        sm.GetService('scanSvc').LogInfo('Scanner Refresh')
        sm.GetService('systemmap').LoadProbesAndScanResult_Delayed()
        self.UpdateProbeSpheres()
        self.CheckButtonStates()
        self.LoadProbeList()
        self.LoadFiltersOptions()
        self.sr.doRefresh = None



    def CreateLineSet(self):
        lineSet = trinity.EveLineSet()
        lineSet.effect = trinity.Tr2Effect()
        lineSet.effect.effectFilePath = LINESET_EFFECT
        lineSet.renderTransparent = False
        return lineSet



    def GetExplorationSiteType(self, attributeID):
        label = const.EXPLORATION_SITE_TYPES[attributeID]
        return localization.GetByLabel(label)



    def OnRefreshScanResults(self):
        self.Refresh()



    def OnReconnectToProbesAvailable(self):
        self.CheckButtonStates()




class WarpableResultBracket(xtriui.BaseBracket):
    __guid__ = 'xtriui.WarpableResultBracket'

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        if IsResultWithinWarpDistance(self.result):
            menu = sm.GetService('menu').SolarsystemScanMenu(self.resultID)
            menu.append(None)
        else:
            menu = []
        bookmarkData = util.KeyVal(id=self.result.id, position=self.result.data, name=self.result.typeName)
        menu.append((localization.GetByLabel('UI/Inflight/BookmarkLocation'), sm.GetService('addressbook').BookmarkLocationPopup, (eve.session.solarsystemid,
          None,
          None,
          None,
          bookmarkData)))
        menu.append(None)
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/IngoreResult'), scanSvc.IgnoreResult, (self.result.id,)))
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/IgnoreOtherResults'), scanSvc.IgnoreOtherResults, (self.result.id,)))
        menu.append((localization.GetByLabel('UI/Inflight/Scanner/ClearResult'), scanSvc.ClearResults, (self.result.id,)))
        return menu




class ProbeBracket(xtriui.BaseBracket):
    __guid__ = 'xtriui.ProbeBracket'

    def Startup(self, itemID, typeID, iconNo):
        xtriui.BaseBracket.Startup(self, itemID, None, None, iconNo)
        self.typeID = typeID



    def GetMenu(self):
        return sm.GetService('scanSvc').GetProbeMenu(self.itemID)



    def Select(self, *args):
        pass



    def OnClick(self, *args):
        sm.GetService('state').SetState(self.itemID, state.selected, 1)




class ProbeControl(object):
    __guid__ = 'xtriui.ProbeControl'
    __update_on_reload__ = 1

    def __init__(self, probeID, probe, parent, scanner):
        scanSvc = sm.GetService('scanSvc')
        locator = trinity.EveTransform()
        locator.name = 'spherePar_%s' % probeID
        parent.children.append(locator)
        sphereBracket = uicls.Bracket()
        sphereBracket.align = uiconst.NOALIGN
        sphereBracket.width = sphereBracket.height = 2
        sphereBracket.state = uiconst.UI_DISABLED
        sphereBracket.name = '__probeSphereBracket'
        sphereBracket.trackTransform = locator
        sphereBracket.probeID = probeID
        sphereBracket.positionProbeID = probeID
        uicore.layer.systemMapBrackets.children.insert(0, sphereBracket)
        sphere = trinity.Load('res:/dx9/model/UI/Scanbubble.red')
        sphere.name = 'Scanbubble'
        sphere.children[0].scaling = (2.0, 2.0, 2.0)
        sphere.children[0].children[0].scaling = (-50.0, 50.0, 50.0)
        sphere.children[0].children[1].scaling = (50.0, 50.0, 50.0)
        sphere.children[0].children[2].scaling = (50.0, 50.0, 50.0)
        sphere.children[0].curveSets[1].curves[0].keys[1].time = 0.0625
        sphere.children[0].curveSets[1].curves[0].Sort()
        locator.children.append(sphere)
        cal = trinity.EveTransform()
        cal.name = 'cameraAlignedLocation'
        cal.modifier = 3
        sphere.children.append(cal)
        tracker = trinity.EveTransform()
        tracker.name = 'pr_%d' % probe.probeID
        val = math.sin(mathUtil.DegToRad(45.0)) * 0.33
        translation = (val, val, 0.0)
        tracker.translation = translation
        cal.children.append(tracker)
        bracket = xtriui.ProbeBracket()
        bracket.name = '__probeSphereBracket'
        bracket.align = uiconst.NOALIGN
        bracket.state = uiconst.UI_PICKCHILDREN
        bracket.width = bracket.height = 16
        bracket.dock = False
        bracket.minDispRange = 0.0
        bracket.maxDispRange = 1e+32
        bracket.inflight = False
        bracket.color = None
        bracket.invisible = False
        bracket.fadeColor = False
        bracket.showLabel = 2
        bracket.probe = probe
        bracket.probeID = probeID
        bracket.displayName = scanSvc.GetProbeLabel(probeID)
        bracket.showDistance = 0
        bracket.noIcon = True
        bracket.Startup(probeID, probe.typeID, None)
        bracket.trackTransform = tracker
        uicore.layer.systemMapBrackets.children.insert(0, bracket)
        bracket.ShowLabel()
        shadow = trinity.Load('res:/Model/UI/probeShadow.red')
        locator.children.append(shadow)
        intersection = trinity.Load('res:/Model/UI/probeIntersection.red')
        intersection.display = False
        intersection.scaling = (2.0, 2.0, 2.0)
        sphere.children.append(intersection)
        cursor = trinity.Load('res:/Model/UI/probeCursor.red')
        cursor.scaling = (CURSOR_SCALE, CURSOR_SCALE, CURSOR_SCALE)
        cursor.useDistanceBasedScale = True
        cursor.distanceBasedScaleArg1 = 1500000.0
        cursor.distanceBasedScaleArg2 = 0.0
        cursor.translation = (0.0, 0.0, 0.0)
        for c in cursor.children:
            c.name += '_' + str(probeID)

        locator.children.append(cursor)
        self.bracket = bracket
        self.scanRanges = scanSvc.GetScanRangeStepsByTypeID(probe.typeID)
        self.cursor = cursor
        self.shadow = shadow
        self.intersection = intersection
        self.locator = locator
        self.sphere = sphere
        self.cameraAlignedLocation = cal
        self.probeID = probeID
        self.scanrangeCircles = None
        self._highlighted = True
        self.HighlightBorder(0)



    def SetScanDronesState(self, state):
        for c in self.sphere.children[0].children:
            if c.name == 'Circle':
                c.display = state




    def SetRange(self, range):
        self.sphere.scaling = (range, range, range)
        self.shadow.scaling = (range * 2, range * 2, range * 2)



    def ScaleRange(self, scale):
        scale = self.sphere.scaling[0] * scale
        self.SetRange((scale, scale, scale))



    def SetPosition(self, position):
        position = geo2.Vector(*position)
        distSq = geo2.Vec3LengthSq(position)
        if distSq > MAX_PROBE_DIST_FROM_SUN_SQUARED:
            position *= MAX_PROBE_DIST_FROM_SUN_SQUARED / distSq
        self.locator.translation = position
        self.shadow.translation = (0.0, -y, 0.0)



    def GetPosition(self):
        return geo2.Vector(*self.locator.translation)



    def GetWorldPosition(self):
        return geo2.Vector(*self.locator.worldTransform[3][:3])



    def ShiftPosition(self, translation):
        newPos = geo2.Vector(*self.locator.translation) + geo2.Vector(*translation)
        self.SetPosition(newPos)



    def GetRange(self):
        return self.sphere.scaling[0]



    def ResetCursorHighlight(self):
        for each in self.cursor.children:
            each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLORPARAMETERIDX].value = CURSOR_DEFAULT_COLOR




    def HighlightAxis(self, hiliteAxis):
        for each in self.cursor.children:
            (cursorName, side, probeID,) = each.name.split('_')
            cursorAxis = cursorName[6:]
            if hiliteAxis == cursorAxis:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLORPARAMETERIDX].value = CURSOR_HIGHLIGHT_COLOR
            elif len(hiliteAxis) == 2 and cursorAxis in hiliteAxis:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLORPARAMETERIDX].value = CURSOR_HIGHLIGHT_COLOR




    def HighlightBorder(self, on = 1):
        if bool(on) == self._highlighted:
            return 
        self._highlighted = bool(on)
        curveSets = self.sphere.Find('trinity.TriCurveSet')
        curveSet = None
        for each in curveSets:
            if getattr(each, 'name', None) == 'Highlight':
                curveSet = each
                break

        if curveSet:
            curveSet.Stop()
            if on:
                curveSet.scale = 1.0
                curveSet.Play()
            else:
                curveSet.scale = -1.0
                curveSet.PlayFrom(curveSet.GetMaxCurveDuration())



    def ShowIntersection(self, axis = None, side = None):
        if axis == 'xy':
            q = geo2.QuaternionRotationSetYawPitchRoll(0.0, 0.0, 0.0)
            self.intersection.rotation = q
            self.intersection.display = True
            if side == 0:
                self.intersection.translation = (0.0, 0.0, -2.0)
            else:
                self.intersection.translation = (0.0, 0.0, 2.0)
        elif axis == 'yz':
            q = geo2.QuaternionRotationSetYawPitchRoll(pi * 0.5, 0.0, 0.0)
            self.intersection.rotation = q
            self.intersection.display = True
            if side == 0:
                self.intersection.translation = (-2.0, 0.0, 0.0)
            else:
                self.intersection.translation = (2.0, 0.0, 0.0)
        else:
            self.intersection.display = False



    def HideScanRanges(self):
        if self.scanrangeCircles is not None:
            self.scanrangeCircles.display = False



    def ShowScanRanges(self):
        if self.scanrangeCircles is None:
            par = trinity.EveTransform()
            self.scanrangeCircles = par
            par.modifier = 3
            self.locator.children.append(par)
            for r in self.scanRanges:
                r *= 100.0
                sr = trinity.Load('res:/Model/UI/probeRange.red')
                sr.scaling = (r, r, r)
                par.children.append(sr)

        self.scanrangeCircles.display = True




