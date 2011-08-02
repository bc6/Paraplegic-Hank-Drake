import service
from service import SERVICE_START_PENDING, SERVICE_RUNNING
import base
import blue
import log
import trinity
import uix
import uiutil
import uthread
import util
import xtriui
import sys
import state
import bracket
import hint
import maputils
import uiconst
import uicls
from mapcommon import SYSTEMMAP_SCALE, ZOOM_FAR_SYSTEMMAP
import geo2
from math import sin, cos, pi
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
DAY = HOUR * 24L
WEEK = DAY * 7L
MONTH = WEEK * 4L
YEAR = DAY * 365L
NEUTRAL_COLOR = (0.25,
 0.25,
 0.25,
 1.0)

class SystemMapSvc(service.Service):
    __guid__ = 'svc.systemmap'
    __notifyevents__ = ['OnSessionChanged',
     'OnStateChange',
     'OnBookmarkCreated',
     'OnBookmarksDeleted',
     'OnSolarsystemMapSettingsChange',
     'OnTacticalOverlayChange',
     'OnNewScanResult',
     'DoBallsAdded',
     'DoBallRemove',
     'OnSystemScanBegun',
     'OnProbeRemoved',
     'OnProbeAdded',
     'OnProbeStateChanged',
     'OnProbeStateUpdated',
     'OnProbeWarpStart',
     'OnProbeWarpEnd',
     'OnDistributionDungeonEntered',
     'OnEscalatingPathDungeonEntered',
     'OnSlimItemChange',
     'OnMapReset',
     'OnMapModeChangeDone']
    __servicename__ = 'systemmap'
    __displayname__ = 'System Map Client Service'
    __dependencies__ = ['station', 'map', 'settings']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.LogInfo('Starting System Map Client Svc')
        self.Reset()
        self.state = SERVICE_RUNNING



    def Stop(self, memStream = None):
        if trinity.device is None:
            return 
        self.LogInfo('Map svc')
        self.Reset()



    def CleanUp(self):
        self.Reset()
        scene1 = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene1:
            del scene1.models[:]
        if scene2:
            del scene2.objects[:]
        sm.GetService('sceneManager').UnregisterScene('systemmap')
        sm.GetService('sceneManager').UnregisterScene2('systemmap')
        sm.GetService('sceneManager').UnregisterCamera('systemmap')



    def Open(self):
        self.map.OpenSystemMap()



    def OnMapModeChangeDone(self, mapMode):
        if mapMode == 'systemmap':
            if self.updateDisplayInfomationWorkerRunning == False:
                self.updateDisplayInfomationWorkerRunning = True
                uthread.new(self.UpdateDisplayInformationWorker).context = 'systemMapSvc::UpdateDisplayInformationWorker'



    def UpdateDisplayInformationWorker(self):
        while self.map.ViewingSystemMap():
            startTime = blue.os.GetTime()
            for panel in self.bracketPanels[:]:
                if panel and not panel.destroyed:
                    if panel.ball:
                        panel.ball.GetVectorAt(blue.os.GetTime())
                    if getattr(panel, 'hasBubbleHintShowing', False):
                        if panel.itemID and panel.slimItem and hasattr(panel.sr, 'bubble'):
                            if panel.sr.bubble.state != uiconst.UI_HIDDEN:
                                hintText = self.GetBubbleHint(panel.itemID, panel.slimItem, bracket=panel, extended=0)
                                panel.ShowBubble(hintText)
                blue.pyos.BeNice()

            diff = blue.os.TimeDiffInMs(startTime, blue.os.GetTime())
            sleep = max(500, 2000 - diff)
            blue.pyos.synchro.Sleep(sleep)

        self.updateDisplayInfomationWorkerRunning = False



    def OnMapReset(self):
        self.Reset()



    def InitMap(self):
        registered = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if registered is None or self.currentSolarsystemID != eve.session.solarsystemid2:
            sm.GetService('loading').Cycle(mls.UI_SHARED_MAPINITINGMAP)
            try:
                oldScene = trinity.Load(sm.GetService('sceneManager').GetScene())
                texturePath = oldScene.nebula.children[0].object.areas[0].areaTextures[0].pixels
                res = trinity.TriTextureCubeParameter()
                res.name = 'ReflectionMap'
                res.resourcePath = texturePath
                scene2 = trinity.EveSpaceScene()
                scene2.backgroundEffect = trinity.Tr2Effect()
                scene2.backgroundEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Nebula.fx'
                scene2.backgroundEffect.resources.append(res)
                scene2.backgroundEffectScaling = 8.0
                scene2.backgroundRenderingEnabled = True
            except:
                scene2 = trinity.Load('res:/Scene/map_background.red')
                scene2.backgroundEffectScaling = 8.0
            lineSet = self.map.CreateLineSet()
            lineSet.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
            scene2.objects.append(lineSet)
            self.orbitLineSet = lineSet
            (ssmap, self.solarsystemSunID,) = self.DrawSolarSystem(eve.session.solarsystemid2)
            self.currentSolarsystemID = eve.session.solarsystemid2
            scene1 = trinity.TriScene()
            scene1.fogStart = -100.0
            scene1.fogEnd = 1000000.0
            scene1.update = 1
            scene1.fogEnable = 1
            scene1.fogColor.SetRGB(0.0, 0.0, 0.0)
            scene1.fogTableMode = trinity.TRIFOG_LINEAR
            camera = None
            if getattr(scene1, 'camera', None) is not None:
                camera = scene1.camera
                scene1.camera = None
            else:
                camera = trinity.EveCamera()
            camera.idleMove = 0
            camera.friction = 25.0
            camera.fieldOfView = 0.2
            for each in camera.zoomCurve.keys:
                each.value = 0.2

            scene1.pointStarfield.display = 0
            camera.translationFromParent.z = settings.user.ui.Get('systemmapTFP', 0.8 * ZOOM_FAR_SYSTEMMAP)
            if camera.translationFromParent.z < 0:
                camera.translationFromParent.z = -camera.translationFromParent.z
            camera.OrbitParent(0.0, 10.0)
            ssmap.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
            scene2.objects.append(ssmap)
            self.currentSolarsystem = ssmap
            sm.GetService('sceneManager').RegisterScenes('systemmap', scene1, scene2)
            sm.GetService('sceneManager').RegisterCamera('systemmap', camera)
            uix.GetSystemmapNav().SetInterest(eve.session.shipid)
            self.lastHighlightItemsWithinProbeRange = blue.os.GetTime()
        uicore.layer.map.state = uiconst.UI_HIDDEN
        uicore.layer.systemmap.state = uiconst.UI_PICKCHILDREN
        uix.GetSystemmapNav()
        sm.GetService('sceneManager').SetRegisteredScenes('systemmap')
        self.LoadProbesAndScanResult()
        self.LoadBookmarks()
        self.LoadSolarsystemBrackets()
        self.LoadBeacons()
        self.LoadSovereigntyStructures()
        self.LoadDungeons()
        uthread.new(self.ShowRanges, settings.user.overview.Get('viewTactical', 0))
        scanner = sm.GetService('window').GetWindow('scanner', create=0)
        if scanner is not None:
            scanner.Refresh()
        sm.GetService('loading').StopCycle()



    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            return 
        if 'solarsystemid' in change:
            if self.map.ViewingSystemMap():
                self.InitMap()
            else:
                self.ClearAllBrackets()



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::map')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, lst, ignoreMoons = 0, ignoreAsteroids = 1):
        if self.map.ViewingSystemMap():
            groupIDs = []
            for (ball, slimItem,) in lst:
                groupIDs.append(slimItem.groupID)
                if ball.id == session.shipid:
                    self.LoadSolarsystemBrackets(1)

            if const.groupCosmicSignature in groupIDs or const.groupCosmicAnomaly in groupIDs:
                uthread.worker('MapMgr::LoadDungeons', self.LoadDungeons)
            if const.groupScannerProbe in groupIDs:
                self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)
            if slimItem.groupID in const.sovereigntyClaimStructuresGroups:
                self.LoadSovereigntyStructures()



    def DoBallRemove(self, ball, slimItem, terminal):
        if not trinity.device or not trinity.device.scene:
            return 
        if self.map.ViewingSystemMap():
            if slimItem.groupID == const.groupScannerProbe:
                self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)
        if self.map.ViewingSystemMap():
            if slimItem.groupID in const.sovereigntyClaimStructuresGroups:
                self.LoadSovereigntyStructures()



    def OnProbeWarpStart(self, probeID, fromPos, toPos, startTime, duration):
        uthread.worker('MapMgr::OnProbeWarpStart_Thread', self.OnProbeWarpStart_Thread, probeID, fromPos, toPos, startTime, duration)



    def OnProbeWarpStart_Thread(self, probeID, fromPos, toPos, startTime, duration):
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if scene2 is None:
            return 
        if not hasattr(self, 'probeRoutes'):
            self.probeRoutes = {}
        scanSvc = sm.GetService('scanSvc')
        data = scanSvc.GetProbeData()
        if probeID not in data:
            return 
        probe = data[probeID]
        route = xtriui.MapRoute()
        route.ballScale = 0.4
        route.timeBase = duration
        route.scale = SYSTEMMAP_SCALE
        route.lineColor = (0.0, 1.0, 0.0, 0.1)
        route.resPath = 'res:/dx9/model/Sprite/ProbeRouteSprite.red'
        route.name = 'probeRoute_' + str(probeID)
        route.DrawRoute((probe.pos.AsTuple(), probe.destination.AsTuple()), usePoints=True, drawLines=True, blinking=False)
        scene2.objects.append(route.model)
        scene2.objects.append(route.lineSet)
        self.probeRoutes[probeID] = route
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)



    def OnProbeWarpEnd(self, probeID):
        uthread.worker('MapMgr::OnProbeWarpEnd_Thread', self.OnProbeWarpEnd_Thread, probeID)



    def OnProbeWarpEnd_Thread(self, probeID):
        if hasattr(self, 'probeRoutes') and probeID in self.probeRoutes:
            scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
            if scene2 is None:
                return 
            route = self.probeRoutes[probeID]
            if route.model in scene2.objects:
                scene2.objects.remove(route.model)
            if route.lineSet in scene2.objects:
                scene2.objects.remove(route.lineSet)
            del self.probeRoutes[probeID]
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)



    def OnSystemScanBegun(self, *args):
        self.LoadProbesAndScanResult_Delayed()



    def OnProbeRemoved(self, probeID):
        self.LoadProbesAndScanResult_Delayed()



    def OnProbeAdded(self, probe):
        self.LoadProbesAndScanResult_Delayed()



    def OnProbeStateChanged(self, probeID, probeState):
        self.LoadProbesAndScanResult_Delayed()



    def OnProbeStateUpdated(self, probeID, probeState):
        self.LoadProbesAndScanResult_Delayed()



    def LoadProbesAndScanResult_Delayed(self):
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)



    def OnStateChange(self, itemID, flag, true, *args):
        if not self.map.IsOpen():
            return None
        if flag == state.gbTravelTo:
            self.broadcastBrackets = self.broadcastBrackets or {}
            (gbID, charID,) = args
            if true:
                self.broadcastBrackets[itemID] = (gbID, sm.GetService('starmap').MakeBroadcastBracket('TravelTo', itemID, charID))
            else:
                (lastGBID, bracket,) = self.broadcastBrackets.get(itemID, (None, None))
                if lastGBID == gbID:
                    del self.broadcastBrackets[itemID]
        bracket = self.GetBracket(itemID)
        if bracket:
            bracket.OnStateChange(itemID, flag, true, *args)



    def OnBookmarkCreated(self, bookmarkID, comment):
        if self.map.ViewingSystemMap():
            self.LoadBookmarks()
            sm.GetService('bracket').ResetOverlaps()



    def OnBookmarksDeleted(self, bookmarkIDs):
        if self.map.ViewingSystemMap():
            self.LoadBookmarks()
            sm.GetService('bracket').ResetOverlaps()



    def OnSolarsystemMapSettingsChange(self, change, *args):
        if self.map.ViewingSystemMap() and change == 'brackets':
            self.LoadBookmarks()
            self.LoadProbesAndScanResult()
            self.LoadSolarsystemBrackets(1)
            self.LoadBeacons()
            self.LoadSovereigntyStructures()
            self.LoadDungeons()



    def OnDistributionDungeonEntered(self, row):
        self.LoadDungeons()



    def OnEscalatingPathDungeonEntered(self, row):
        self.LoadDungeons()



    def OnTacticalOverlayChange(self, on):
        if self.map.ViewingSystemMap():
            self.ShowRanges(on)



    def OnNewScanResult(self, results):
        if self.map.ViewingSystemMap():
            self.LoadProbesAndScanResult(results)



    def Reset(self):
        self.LogInfo('System Map Reset')
        self.currentSolarsystemID = None
        self.currentSolarsystem = None
        self.solarsystemBracketsLoaded = None
        self.solarsystemHierarchyData = {}
        self.expandingHint = None
        self.talking = set()
        rangeCircleTF = getattr(self, 'rangeCircleTF', None)
        if rangeCircleTF:
            for each in rangeCircleTF.curveSets[:]:
                rangeCircleTF.curveSets.remove(each)

        self.rangeCircleTF = None
        self.rangeLineSet = None
        self.ssitems = None
        self.broadcastBrackets = None
        self.taxLevel = None
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.cursor = None
        self.uicursor = None
        self.minimizedWindows = []
        self.activeMap = ''
        toRemove = getattr(self, 'bracketPanels', [])
        for each in toRemove:
            each.Close()

        self.bracketPanels = []
        self.updateDisplayInfomationWorkerRunning = False



    def GetBracket(self, itemID):
        wnd = uicore.layer.systemmap
        for each in wnd.children:
            if getattr(each, 'IsBracket', 0) and getattr(each, 'itemID', None) == itemID:
                return each




    def GetSolarsystemHierarchy(self, solarsystemID = None, toplevel = None):
        toplevel = toplevel or (const.groupPlanet,
         const.groupSun,
         const.groupStargate,
         const.groupStation)
        solarsystemID = solarsystemID or self.currentSolarsystemID
        if not solarsystemID:
            return ({}, {})
        if (solarsystemID, toplevel) in self.solarsystemHierarchyData:
            return self.solarsystemHierarchyData[(solarsystemID, toplevel)]
        ssData = self.GetSolarsystemData(solarsystemID).Index('itemID')
        groups = {}
        noOrbitID = []
        for id in ssData:
            each = ssData[id]
            if cfg.invtypes.Get(each.typeID).groupID in toplevel:
                if each.itemID not in groups:
                    groups[each.itemID] = []
            elif each.orbitID is None:
                noOrbitID.append(each)

        for each in noOrbitID:
            if cfg.invtypes.Get(each.typeID).groupID == const.groupSun:
                continue
            pos = trinity.TriVector(each.x, each.y, each.z)
            lst = []
            for (parentID, orbits,) in groups.iteritems():
                parentItem = ssData[parentID]
                parentPos = trinity.TriVector(parentItem.x, parentItem.y, parentItem.z)
                dist = (pos - parentPos).Length()
                lst.append((dist, parentID))

            lst.sort()
            groups[lst[0][1]].append(each)

        parentLess = []
        for id in ssData:
            each = ssData[id]
            if each.itemID not in groups:
                if each.orbitID in groups:
                    groups[each.orbitID].append(each)
                elif each.orbitID:
                    parent = ssData[each.orbitID]
                    if parent.orbitID in groups:
                        groups[parent.orbitID].append(each)
                    else:
                        parentLess.append(each)

        self.solarsystemHierarchyData[(solarsystemID, toplevel)] = (groups, ssData)
        return (groups, ssData)



    def ClearAllBrackets(self):
        solarsystem = self.GetCurrentSolarSystem()
        bracketWnd = uicore.layer.systemmap
        for each in bracketWnd.children[:]:
            each.Close()

        self.solarsystemBracketsLoaded = None



    def ClearBrackets(self, _ui = None, _tf = None):
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem and _tf:
            for tf in solarsystem.children[:]:
                if hasattr(tf, 'name') and tf.name.startswith(_tf):
                    solarsystem.children.remove(tf)

        bracketWnd = uicore.layer.systemmap
        for each in bracketWnd.children[:]:
            if each.name == _ui:
                each.Close()




    def LoadBookmarks(self):
        self.ClearBrackets('__bookmarkbracket', 'bm_')
        if 'bookmark' not in maputils.GetVisibleSolarsystemBrackets():
            return 
        bookmarks = sm.GetService('addressbook').GetBookmarks()
        ballPark = sm.GetService('michelle').GetBallpark()
        bracketWnd = uicore.layer.systemmap
        solarsystem = self.GetCurrentSolarSystem()
        for bookmark in bookmarks.itervalues():
            pos = None
            if bookmark.locationID != eve.session.solarsystemid2:
                continue
            if bookmark.x is None:
                if bookmark.itemID is not None:
                    if ballPark and bookmark.itemID in ballPark.balls:
                        ball = ballPark.balls[bookmark.itemID]
                        pos = (ball.x, ball.y, ball.z)
                    elif solarsystem:
                        for tf in solarsystem.children:
                            try:
                                itemID = int(tf.name)
                            except:
                                sys.exc_clear()
                                continue
                            if itemID == bookmark.itemID:
                                pos = tf.translation
                                break
                        else:
                            self.LogError('Didnt find propper item to track for bookmark', bookmark)
                            continue

                    else:
                        self.LogError('No ballpark or solarsystem to search for transform to track', bookmark)
                        continue
                else:
                    self.LogError('Cannot draw bookmark into solarsystem view', bookmark)
                    continue
            else:
                pos = (bookmark.x, bookmark.y, bookmark.z)
            if solarsystem and pos:
                panel = xtriui.BookmarkBracket()
                panel.name = '__bookmarkbracket'
                panel.align = uiconst.NOALIGN
                panel.state = uiconst.UI_NORMAL
                panel.width = panel.height = 16
                panel.dock = 0
                panel.minDispRange = 0.0
                panel.maxDispRange = 1e+32
                panel.inflight = False
                panel.color = None
                panel.invisible = False
                panel.bmData = bookmark
                panel.fadeColor = 0
                tf = trinity.EveTransform()
                tf.name = 'bm_%d' % bookmark.bookmarkID
                solarsystem.children.append(tf)
                panel.trackTransform = tf
                tf.translation = geo2.Vector(*pos)
                (caption, note,) = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
                panel.displayName = mls.UI_GENERIC_BOOKMARK + ': ' + caption
                panel.Startup(bookmark.bookmarkID, None, None, 'ui_38_16_150')
                bracketWnd.children.insert(0, panel)




    def HighlightItemsWithinProbeRange(self):
        if not self.map.ViewingSystemMap():
            return 
        timeDiff = blue.os.TimeDiffInMs(self.lastHighlightItemsWithinProbeRange)
        if timeDiff > 200.0:
            self.lastHighlightItemsWithinProbeRange = blue.os.GetTime()
        else:
            return 
        scannerWnd = sm.GetService('window').GetWindow('scanner')
        bracketWnd = uicore.layer.systemmap
        scanSvc = sm.GetService('scanSvc')
        probeData = scanSvc.GetProbeData()
        validProbes = [ probeID for (probeID, probe,) in probeData.iteritems() if probe.state != const.probeStateInactive ]
        reset = not bool(validProbes)
        inRangeOfProbe = []
        if scannerWnd:
            probeControls = scannerWnd.GetProbeSpheres()
            for probeID in validProbes:
                if probeID not in probeControls:
                    continue
                probeControl = probeControls[probeID]
                pPos = probeControl.GetPosition()
                pRange = probeControl.GetRange()
                for bracket in bracketWnd.children:
                    cls = getattr(bracket, '__class__', None)
                    if not cls or not issubclass(cls, xtriui.BaseBracket) or issubclass(cls, xtriui.ProbeBracket):
                        continue
                    if bracket.trackTransform:
                        bPos = geo2.Vector(*bracket.trackTransform.translation)
                        if pRange > geo2.Vec3Length(pPos - bPos):
                            inRangeOfProbe.append(bracket)


        else:
            reset = True
        for bracket in bracketWnd.children:
            cls = getattr(bracket, '__class__', None)
            if not cls or not issubclass(cls, xtriui.BaseBracket) or issubclass(cls, xtriui.ProbeBracket):
                continue
            if bracket.name == '__iamherebracket':
                continue
            if reset or bracket in inRangeOfProbe:
                bracket.opacity = 1.0
            else:
                bracket.opacity = 0.125




    def LoadProbesAndScanResult(self, *args):
        self.ClearBrackets('__probebracket', 'pr_')
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return 
        if not eve.session.IsItSafe():
            return 
        scanSvc = sm.GetService('scanSvc')
        if not self.map.ViewingSystemMap():
            return 
        bracketWnd = uicore.layer.systemmap
        visible = maputils.GetVisibleSolarsystemBrackets()
        activeProbes = sm.GetService('scanSvc').GetActiveProbes()
        scannerWnd = sm.GetService('window').GetWindow('scanner')
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        suppressBubbleHints = scannerWnd is not None
        probes = scanSvc.GetProbeData()
        if const.groupScannerProbe in visible and probes is not None and len(probes) > 0:
            for probe in probes.itervalues():
                if scannerWnd and probe.probeID in activeProbes:
                    continue
                panel = xtriui.ProbeBracket()
                panel.name = '__probebracket'
                panel.align = uiconst.ABSOLUTE
                panel.state = uiconst.UI_NORMAL
                panel.width = panel.height = 16
                panel.dock = 0
                panel.minDispRange = 0.0
                panel.maxDispRange = 1e+32
                panel.inflight = False
                panel.color = None
                panel.invisible = False
                panel.fadeColor = False
                panel.showLabel = bracket.SHOWLABELS_ONMOUSEENTER
                panel.probe = probe
                tf = trinity.EveTransform()
                tf.name = 'pr_%d' % probe.probeID
                solarsystem.children.append(tf)
                panel.displayName = scanSvc.GetProbeLabel(probe.probeID)
                panel.showDistance = 0
                panel.Startup(probe.probeID, probe.typeID, 'ui_38_16_120')
                bracketWnd.children.insert(0, panel)
                panel.trackTransform = tf
                tf.translation = probe.pos.AsTuple()
                invType = cfg.invtypes.Get(probe.typeID)
                slimItem = util.KeyVal()
                slimItem.jumps = []
                slimItem.itemID = probe.probeID
                slimItem.typeID = probe.typeID
                slimItem.groupID = invType.groupID
                slimItem.categoryID = invType.categoryID
                if not suppressBubbleHints and slimItem.groupID in showhint:
                    panel.sr.icon.SetAlign(uiconst.CENTER)
                    panel.ShowBubble(self.GetBubbleHint(probe.probeID, slimItem, bracket=panel, extended=0))

        nav = uix.GetSystemmapNav(0)
        if nav and not nav.destroyed:
            nav.SendMessage(uiconst.UI_MOUSEENTER)
        if scannerWnd is not None:
            scannerWnd.DisplaySelectedResults()
        self.HighlightItemsWithinProbeRange()
        self.UpdateBrackets()
        self.loadProbeAndScanResultTimer = None



    def GetSolarsystem(self):
        return getattr(self, 'currentSolarsystem', None)



    def RefreshBubble(self, bubble):
        bracket = bubble.parent
        if bracket is None:
            log.LogTraceback('RefreshBubble: no bracket')
            return 
        if bubble.expanded:
            bubble.ShowHint(bracket.expandedHint)
        else:
            bubble.ShowHint(bracket.collapsedHint)
        bracket.sr.bubble.sr.ExpandBubbleHint = lambda *args: self.ExpandBubbleHint(*args)



    def ShowRanges(self, on = 1):
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        if self.rangeCircleTF:
            for each in self.rangeCircleTF.curveSets[:]:
                self.rangeCircleTF.curveSets.remove(each)

            if self.rangeCircleTF in scene2.objects:
                scene2.objects.remove(self.rangeCircleTF)
        if self.rangeLineSet and self.rangeLineSet in scene2.objects:
            scene2.objects.remove(self.rangeLineSet)
        self.rangeLineSet = None
        self.rangeCircleTF = None
        if not on:
            return 
        ranges = trinity.EveRootTransform()
        ranges.name = 'rangeCircleLabels'
        ranges.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
        scene2.objects.append(ranges)
        self.rangeCircleTF = ranges
        lineSet = self.map.CreateLineSet()
        for r in [5,
         10,
         15,
         20,
         25]:
            color = 0.25
            if r in (10, 20):
                color = 0.33
            radius = r * const.AU
            self.AddCircle(lineSet, radius * SYSTEMMAP_SCALE, color=color)
            self.AddRangeLabel(ranges, str(r) + 'AU', radius)

        lineSet.SubmitChanges()
        scene2.objects.append(lineSet)
        self.rangeLineSet = lineSet
        for each in ranges.curveSets[:]:
            ranges.curveSets.remove(each)

        if eve.session.solarsystemid:
            t = 0
            sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
            while sunBall is None:
                blue.pyos.synchro.Sleep(1000)
                sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
                t += 1
                if t == 15:
                    return 

            vectorCurve = trinity.TriVectorCurve()
            vectorCurve.value.SetXYZ(-SYSTEMMAP_SCALE, -SYSTEMMAP_SCALE, -SYSTEMMAP_SCALE)
            vectorSequencer = trinity.TriVectorSequencer()
            vectorSequencer.operator = trinity.TRIOP_MULTIPLY
            vectorSequencer.functions.append(sunBall)
            vectorSequencer.functions.append(vectorCurve)
            binding = trinity.TriValueBinding()
            binding.sourceAttribute = 'value'
            binding.destinationAttribute = 'translation'
            binding.scale = 1.0
            binding.sourceObject = vectorSequencer
            binding.destinationObject = ranges
            curveSet = trinity.TriCurveSet()
            curveSet.name = 'translationCurveSet'
            curveSet.playOnLoad = True
            curveSet.curves.append(vectorSequencer)
            curveSet.bindings.append(binding)
            ranges.curveSets.append(curveSet)
            curveSet.Play()
            lineSet.translationCurve = vectorSequencer
        else:
            pos = maputils.GetMyPos()
            vectorCurve = trinity.TriVectorCurve()
            vectorCurve.value.SetXYZ(pos.x * SYSTEMMAP_SCALE, pos.y * SYSTEMMAP_SCALE, pos.z * SYSTEMMAP_SCALE)
            ranges.translationCurve = vectorCurve
            lineSet.translationCurve = vectorCurve



    def AddRangeLabel(self, parent, text, radius):
        for (x, z,) in [(0.0, radius),
         (radius, 0.0),
         (0.0, -radius),
         (-radius, 0.0)]:
            label = xtriui.TransformableLabel(text, parent, shadow=0, hspace=0)
            label.transform.translation = (x, 0.0, z)
            scale = geo2.Vector(*label.transform.scaling) * 1250000000.0
            label.transform.scaling = scale
            label.SetDiffuseColor((0.7, 0.7, 0.7, 1.0))




    def AddCircle(self, lineSet, radius, numberOfPoints = 256, color = 0.35):
        color = (color,
         color,
         color,
         color)
        step = pi * 2.0 / numberOfPoints
        points = []
        for idx in range(numberOfPoints):
            angle = idx * step
            x = cos(angle) * radius
            z = sin(angle) * radius
            points.append((x, 0.0, z))

        for idx1 in range(numberOfPoints):
            idx2 = (idx1 + 1) % numberOfPoints
            lineSet.AddLine(points[idx1], color, points[idx2], color)




    def LoadSolarsystemBrackets(self, reload = 0):
        if self.solarsystemBracketsLoaded == eve.session.solarsystemid2 and not reload:
            return 
        bracketWnd = uicore.layer.systemmap
        bp = sm.GetService('michelle').GetBallpark()
        (groups, ssData,) = self.GetSolarsystemHierarchy(self.currentSolarsystemID)
        self.ClearBrackets('__solarsystembracket')
        self.ClearBrackets('__iamherebracket')
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return 
        self.solarsystemBracketsLoaded = eve.session.solarsystemid2
        validGroups = groups
        inf = 1e+32
        visible = maputils.GetVisibleSolarsystemBrackets()
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        self.bracketPanels = []
        bracket = xtriui.Bracket(parent=bracketWnd, name='__iamherebracket', align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN)
        bubble = xtriui.BubbleHint(parent=bracket, name='bubblehint', align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_PICKCHILDREN)
        bubble.ShowHint(mls.UI_SHARED_MAPYOUAREHERE, 2)
        if eve.session.stationid:
            pos = maputils.GetMyPos()
            tf = trinity.EveTransform()
            tf.name = 'mypos'
            tf.translation = (pos.x, pos.y, pos.z)
            solarsystem.children.append(tf)
            bracket.trackTransform = tf
        elif eve.session.solarsystemid:
            sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
            bracket.trackBall = sunBall
            bracket.ballTrackingScaling = -SYSTEMMAP_SCALE
        self.bracketPanels.append(bracket)
        suppressBubbleHints = sm.GetService('window').GetWindow('scanner') is not None
        for tf in solarsystem.children:
            try:
                itemID = int(tf.name)
                itemData = ssData[itemID]
            except:
                sys.exc_clear()
                continue
            if bp is not None and bp.slimItems:
                slimItem = bp.GetInvItem(itemID)
                ball = bp.GetBall(itemID)
                invType = cfg.invtypes.Get(slimItem.typeID)
                if invType.groupID not in visible:
                    continue
            else:
                invType = cfg.invtypes.Get(itemData.typeID)
                if invType.groupID not in visible:
                    continue
                ball = None
                slimItem = util.KeyVal()
                slimItem.jumps = []
                slimItem.itemID = itemData.itemID
                slimItem.ballID = None
                slimItem.charID = None
                slimItem.ownerID = None
                slimItem.typeID = itemData.typeID
                slimItem.groupID = invType.groupID
                slimItem.categoryID = invType.categoryID
                slimItem.corpID = getattr(itemData, 'corpID', None)
                slimItem.locationID = getattr(itemData, 'locationID', None)
                slimItem.warFactionID = getattr(itemData, 'warFactionID', 0)
                slimItem.allianceID = getattr(itemData, 'allianceID', None)
            panel = xtriui.Bracket()
            panel.name = '__solarsystembracket'
            panel.align = uiconst.NOALIGN
            panel.state = uiconst.UI_NORMAL
            panel.width = panel.height = 16
            panel.data = sm.GetService('bracket').GetBracketProps(slimItem, ball)
            try:
                displayName = uix.GetSlimItemName(slimItem)
            except:
                sys.exc_clear()
                continue
            if slimItem.groupID == const.groupStation:
                displayName = uix.EditStationName(displayName, usename=1)
            (_iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag,) = panel.data
            panel.displayName = displayName
            bracketWnd.children.insert(0, panel)
            panel.trackTransform = tf
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.updateItem = False
            panel.fadeColor = 0
            panel.sr.slimItem = slimItem
            panel.ssData = itemData
            panel.groupID = slimItem.groupID
            panel.ball = ball
            panel.Startup(slimItem, ball, tf)
            if not suppressBubbleHints and slimItem.groupID in showhint:
                panel.hasBubbleHintShowing = True
                panel.pickState = uiconst.TR2_SPS_CHILDREN
                panel.width = panel.height = 800
                panel.sr.icon.SetAlign(uiconst.CENTER)
                if panel.sr.tempIcon:
                    panel.sr.tempIcon.SetAlign(uiconst.CENTER)
                panel.ShowBubble(self.GetBubbleHint(itemID, slimItem, bracket=panel, extended=0))
                panel.showLabel = 0
                if slimItem.groupID in (const.groupStation,):
                    panel.sr.bubble.sr.ExpandHint = self.ExpandBubbleHint
            self.bracketPanels.append(panel)

        self.SortBubbles()



    def LoadBeacons(self):
        self.LoadBallparkItems('__beaconbracket', 'beacon_', [const.groupBeacon], overrideWidthHeight=(800, 800))



    def LoadSovereigntyStructures(self):
        self.LoadBallparkItems('__sovereigntybracket', 'sovereignty_', [const.groupSovereigntyClaimMarkers, const.groupSovereigntyDisruptionStructures])



    def LoadBallparkItems(self, bracketName, bracketPrefix, itemGroupIDs, overrideWidthHeight = None):
        solarsystem = self.GetSolarsystem()
        if solarsystem is None:
            log.LogInfo('no solar system (', bracketPrefix, 'Structures)')
            return 
        self.ClearBrackets(bracketName, bracketPrefix)
        itemGroupIDlist = []
        visibleGroups = maputils.GetVisibleSolarsystemBrackets()
        for groupID in itemGroupIDs:
            if groupID in visibleGroups:
                itemGroupIDlist.append(groupID)

        if not itemGroupIDlist:
            return 
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        bracketWnd = uicore.layer.systemmap
        for (itemID, ball,) in ballpark.balls.iteritems():
            if ballpark is None:
                break
            slimItem = ballpark.GetInvItem(itemID)
            if not slimItem:
                continue
            if slimItem.groupID not in itemGroupIDlist:
                continue
            panel = xtriui.Bracket()
            panel.name = bracketName
            panel.align = uiconst.NOALIGN
            panel.state = uiconst.UI_NORMAL
            panel.width = panel.height = 16
            panel.data = sm.GetService('bracket').GetBracketProps(slimItem, ball)
            try:
                displayName = uix.GetSlimItemName(slimItem)
            except:
                sys.exc_clear()
                continue
            (_iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag,) = panel.data
            panel.displayName = displayName
            bracketWnd.children.insert(0, panel)
            tracker = trinity.EveTransform()
            tracker.name = '%s%d' % (bracketPrefix, itemID)
            tracker.translation = (ball.x, ball.y, ball.z)
            solarsystem.children.append(tracker)
            panel.trackTransform = tracker
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.updateItem = False
            panel.fadeColor = 0
            panel.sr.slimItem = slimItem
            panel.groupID = slimItem.groupID
            panel.Startup(slimItem, ball)
            if slimItem.groupID in showhint:
                if overrideWidthHeight is not None:
                    (panel.width, panel.height,) = overrideWidthHeight
                panel.sr.icon.SetAlign(uiconst.CENTER)
                panel.ShowBubble(self.GetBubbleHint(itemID, slimItem, bracket=panel, extended=0))
                panel.showLabel = 0
                panel.sr.bubble.sr.ExpandHint = self.ExpandBubbleHint

        self.SortBubbles()



    def OnSlimItemChange(self, oldItem, newItem):
        if newItem.groupID in const.sovereigntyClaimStructuresGroups:
            self.LoadSovereigntyStructures()



    def LoadDungeons(self):
        self.ClearBrackets('__dungeonbracket', 'dg_')
        if not eve.session.solarsystemid:
            return 
        escalatingPath = sm.GetService('dungeonTracking').GetEscalatingPathDungeonsEntered()
        knownDungeons = sm.GetService('dungeonTracking').GetDistributionDungeonsEntered()
        self._LoadDungeons(escalatingPath)
        self._LoadDungeons(knownDungeons)



    def _LoadDungeons(self, data):
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return 
        if not data:
            return 
        bracketWnd = uicore.layer.systemmap
        for each in data:
            panel = xtriui.BaseBracket()
            bracketWnd.children.insert(0, panel)
            panel.name = '__dungeonbracket'
            panel.align = uiconst.NOALIGN
            panel.state = uiconst.UI_NORMAL
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.fadeColor = False
            tf = trinity.EveTransform()
            tf.name = 'dg_%s_%s' % (repr(each.name), getattr(each, 'ballID', -1))
            solarsystem.children.append(tf)
            panel.trackTransform = tf
            tf.translation = (each.x, each.y, each.z)
            panel.displayName = each.name
            panel.Startup(tf.name, None, None, 'ui_38_16_14')
            panel.sr.icon.SetAlign(uiconst.CENTER)
            panel.ShowBubble(each.name)
            panel.showLabel = 0

        self.SortBubbles()



    def GetBubbleHint(self, itemID, slimItem = None, mapData = None, bracket = None, extended = 0):
        if extended and getattr(bracket, 'expandedHint', None):
            return bracket.expandedHint
        if not extended and getattr(bracket, 'collapsedHint', None):
            return bracket.collapsedHint
        if eve.session.solarsystemid and slimItem is None:
            slimItem = sm.GetService('michelle').GetItem(itemID)
        if slimItem is None and mapData is None:
            mapData = self.map.GetItem(itemID)
            if mapData is None:
                return ''
        typeID = None
        groupID = None
        orbitID = None
        hint = []
        if slimItem:
            groupID = slimItem.groupID
            typeID = slimItem.typeID
            displayName = uix.GetSlimItemName(slimItem)
        if mapData:
            displayName = mapData.itemName
            if groupID is None:
                if hasattr(mapData, 'groupID'):
                    groupID = mapData.groupID
                else:
                    groupID = cfg.invtypes.Get(mapData.typeID).groupID
            if hasattr(mapData, 'orbitID'):
                orbitID = mapData.orbitID
            typeID = mapData.typeID
        if groupID is None:
            return hint
        ball = None
        transform = None
        if bracket:
            ball = bracket.trackBall or getattr(bracket.sr, 'trackBall', None)
            transform = bracket.trackTransform
        if groupID == const.groupStation:
            displayName = uix.EditStationName(displayName, usename=1)
        hint.append(('<b>' + displayName + '</b>', ('OnClick', 'ShowInfo', (typeID, itemID))))
        import maputils
        if groupID == const.groupSolarSystem:
            ss = self.map.GetSecurityStatus(itemID)
            if ss is not None:
                hint.append('%s: %s' % (mls.UI_GENERIC_SECURITYSTATUS, ss))
        else:
            distance = maputils.GetDistance(slimItem, mapData, ball, transform)
            if distance is not None:
                hint.append('%s: %s' % (mls.UI_GENERIC_DISTANCE, util.FmtDist(distance)))
        if extended:
            if groupID == const.groupBeacon:
                if eve.session.solarsystemid:
                    beacon = sm.GetService('michelle').GetItem(itemID)
                    if beacon and hasattr(beacon, 'dunDescription') and beacon.dunDescription:
                        desc = beacon.dunDescription
                        hint.append(desc)
            elif groupID in const.sovereigntyClaimStructuresGroups:
                if eve.session.solarsystemid:
                    (stateName, stateTimestamp, stateDelay,) = sm.GetService('pwn').GetStructureState(slimItem)
                    if stateName is not None:
                        hint.append(getattr(mls, 'UI_GENERIC_' + stateName.upper()))
            elif groupID == const.groupSolarSystem:
                hint.append('<dotline>')
                (groups, ssData,) = self.GetSolarsystemHierarchy(itemID, (const.groupPlanet,))
                for (id, orbits,) in groups.iteritems():
                    planet = ssData[id]
                    hint.append(('%s %s' % (mls.GENERIC_PLANET, planet.itemName), ('OnClick', 'ShowInfo', (planet.typeID, planet.itemID))))
                    byGroup = {}
                    for orbit in orbits:
                        _groupID = cfg.invtypes.Get(orbit.typeID).groupID
                        if _groupID not in byGroup:
                            byGroup[_groupID] = []
                        byGroup[_groupID].append(orbit)

                    sh = ''
                    for (_groupID, orbits,) in byGroup.iteritems():
                        if _groupID not in (const.groupStation, const.groupStargate, const.groupSecondarySun):
                            displayGroupNamePlural = uix.Plural(len(orbits), 'UI_GENERIC_' + cfg.invgroups.Get(_groupID)._groupName.upper().replace(' ', ''))
                            sh += '%s %s, ' % (len(orbits), displayGroupNamePlural)

                    if sh:
                        hint.append(sh[:-2])
                    for station in byGroup.get(const.groupStation, []):
                        hint.append((uix.EditStationName(station.itemName, usename=1), ('OnMouseEnter', 'ShowSubhint', ('GetBubbleHint', (station.itemID,
                            None,
                            station,
                            None,
                            1)))))

                    for stargate in byGroup.get(const.groupStargate, []):
                        hint.append((stargate.itemName, ('OnClick', 'ShowInfo', (stargate.typeID, stargate.itemID))))

                    hint.append('<dotline>')

                hint = hint[:-1]
            elif groupID == const.groupStation:
                services = []
                (stationInfo, opservices, _services,) = sm.GetService('ui').GetStation(itemID, 1)
                opservDict = {}
                facWarService = sm.GetService('facwar')
                for each in opservices:
                    if each.operationID not in opservDict:
                        opservDict[each.operationID] = []
                    opservDict[each.operationID].append(each.serviceID)

                for (name, cmdStr, displayName, iconpath, stationOnly, bits,) in self.station.GetStationServiceInfo():
                    for bit in bits:
                        if bit == const.stationServiceNavyOffices and facWarService.GetCorporationWarFactionID(stationInfo.ownerID) is None:
                            continue
                        if bit in opservDict[stationInfo.operationID]:
                            services.append(displayName)
                            break


                if services:
                    hint.append('<dotline>')
                    hint.append((mls.UI_GENERIC_SERVICES + ':', ('OnMouseEnter', 'ShowSubhint', (services,))))
                agentsByStationID = sm.GetService('agents').GetAgentsByStationID()
                agentByStation = {}
                for agent in agentsByStationID[itemID]:
                    if agent.agentTypeID in (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent) and agent.stationID:
                        if agent.stationID not in agentByStation:
                            agentByStation[agent.stationID] = []
                        agentByStation[agent.stationID].append(agent)

                agents = []
                facWarService = sm.GetService('facwar')
                if itemID in agentByStation:
                    npcDivisions = sm.GetService('agents').GetDivisions()
                    agentsAtStation = agentByStation[itemID]
                    for agent in agentsAtStation:
                        agentsub = []
                        agentsub.append('%s: %s' % (mls.UI_GENERIC_DIVISION, npcDivisions[agent.divisionID].divisionName))
                        agentsub.append('%s: %s' % (mls.UI_GENERIC_LEVEL, uiutil.GetLevel(agent.level)))
                        isLimitedToFacWar = False
                        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarService.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                            isLimitedToFacWar = True
                        if agent.agentTypeID in (const.agentTypeResearchAgent,
                         const.agentTypeBasicAgent,
                         const.agentTypeEventMissionAgent,
                         const.agentTypeFactionalWarfareAgent) and sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) and isLimitedToFacWar == False:
                            agentsub.append(mls.UI_INFOWND_AVAILABLETOYOU)
                        else:
                            agentsub.append(mls.UI_INFOWND_NOTAVAILABLETOYOU)
                        agents.append((cfg.eveowners.Get(agent.agentID).name, ('OnMouseEnter', 'ShowSubhint', (agentsub,))))

                if agents:
                    hint.append('<dotline>')
                    hint.append((mls.UI_GENERIC_AGENTS + ':', ('OnMouseEnter', 'ShowSubhint', (agents,))))
                myassets = sm.GetService('assets').GetAll('sysitems', blueprintOnly=0, isCorp=0)
                for (solarsystemID, station,) in myassets:
                    if station.stationID == itemID:
                        hint.append('<dotline>')
                        hint.append((mls.UI_SHARED_MAPOPS15 + ': %d' % station.itemCount, ('OnClick', 'OpenAssets', (station.stationID,))))

                try:
                    if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 1:
                        corpassets = sm.GetService('assets').GetAll('sysitems', blueprintOnly=0, isCorp=1)
                        for (solarsystemID, station,) in myassets:
                            if station.stationID == itemID:
                                hint.append('<dotline>')
                                hint.append(mls.UI_SHARED_MAPOPS15 + ': %d' % station.itemCount)

                except RuntimeError as what:
                    if what.args[0] != 'NotSupported':
                        log.LogException()
                    sys.exc_clear()
                officeData = sm.RemoteSvc('config').GetMapOffices(stationInfo.solarSystemID)
                offices = []
                for office in officeData:
                    if office.stationID == itemID:
                        offices.append((cfg.eveowners.Get(office.corporationID).name, ('OnClick', 'ShowInfo', (const.groupCorporation, office.corporationID))))

                if offices:
                    hint.append('<dotline>')
                    hint.append((mls.UI_CORP_OFFICES + ':', ('OnMouseEnter', 'ShowSubhint', (offices,))))
        return hint



    def CollapseBubbles(self, ignore = []):
        bracketWnd = uicore.layer.systemmap
        for bracket in bracketWnd.children[:]:
            if getattr(bracket, 'IsBracket', 0) and getattr(bracket.sr, 'bubble', None) is not None:
                if bracket in ignore:
                    continue
                bracket.sr.bubble.ClearSubs()
                self._ExpandBubbleHint(bracket.sr.bubble, 0)

        self.expandingHint = 0



    def ExpandBubbleHint(self, bubble, expand = 1):
        if self.expandingHint:
            return 
        uthread.new(self._ExpandBubbleHint, bubble, expand)



    def _ExpandBubbleHint(self, bubble, expand = 1):
        bracket = bubble.parent
        if not bracket:
            return 
        if not expand and util.GetAttrs(bubble, 'sr', 'CollapseCleanup'):
            force = bubble.sr.CollapseCleanup(bracket)
        else:
            force = False
        if bubble.destroyed:
            return 
        if not force and expand == bubble.expanded:
            return 
        if expand:
            uiutil.SetOrder(bracket, 0)
            blue.pyos.synchro.Yield()
            self.CollapseBubbles([bracket])
        self.expandingHint = id(bracket)
        hint = self.GetBubbleHint(bracket.itemID, getattr(bracket, 'slimItem', None), bracket=bracket, extended=expand)
        if bubble.destroyed:
            return 
        (currentHint, pointer,) = bubble.data
        if hint != currentHint:
            bubble.ShowHint(hint, pointer)
        bubble.expanded = expand
        self.expandingHint = 0



    def SortBubbles(self, ignore = []):
        last = getattr(self, 'lastBubbleSort', None)
        if last and blue.os.TimeDiffInMs(last) < 500:
            return 
        bracketWnd = uicore.layer.systemmap
        order = []
        cameraParent = sm.GetService('camera').GetCameraParent(source='systemmap')
        if cameraParent is None:
            return 
        pos = cameraParent.translation
        camPos = geo2.Vector(pos.x, pos.y, pos.z)
        for bracket in bracketWnd.children:
            if getattr(bracket, 'IsBracket', 0) and getattr(bracket, 'trackTransform', None) is not None and getattr(bracket.sr, 'bubble', None) is not None:
                bracketPos = geo2.Vector(*bracket.trackTransform.translation)
                order.append((geo2.Vec3LengthSq(camPos - bracketPos), bracket))

        order = uiutil.SortListOfTuples(order)
        order.reverse()
        for bracket in order:
            uiutil.SetOrder(bracket, 0)

        self.lastBubbleSort = blue.os.GetTime()
        self.UpdateBrackets()



    def UpdateBrackets(self):
        uthread.new(self._UpdateBrackets)



    def _UpdateBrackets(self):
        blue.pyos.synchro.Yield()
        bracketWnd = uicore.layer.systemmap
        if bracketWnd and len(bracketWnd.children):
            uicore.uilib.RecalcWindows(bracketWnd.children[-1])



    def GetCurrentSolarSystem(self):
        return self.currentSolarsystem



    def GetSolarsystemData(self, ssid):
        self.ssitems = self.ssitems or {}
        if ssid not in self.ssitems:
            self.ssitems[ssid] = sm.RemoteSvc('config').GetMap(ssid)
        return self.ssitems[ssid]



    def DrawSolarSystem(self, ssid):
        ssitems = self.GetSolarsystemData(ssid)
        parent = trinity.EveTransform()
        parent.name = 'solarsystem_%s' % ssid
        orbits = []
        objects = {}
        sunID = None
        pm = (const.groupPlanet, const.groupMoon)
        for each in ssitems:
            if each.itemID == each.locationID:
                continue
            invtype = cfg.invtypes.Get(each.typeID)
            if invtype.groupID == const.groupSecondarySun:
                continue
            transform = trinity.EveTransform()
            if invtype.groupID in pm:
                parentID = self.FindCelestialParent(each, ssitems)
                orbits.append([each.itemID, parentID])
            elif invtype.groupID == const.groupSun:
                sunID = each.itemID
            pos = geo2.Vector(each.x, each.y, each.z)
            transform.translation = pos
            transform.name = str(each.itemID)
            parent.children.append(transform)
            objects[each.itemID] = transform

        for (childID, parentID,) in orbits:
            if childID in objects and parentID in objects:
                self.Add3DCircle(objects[childID], objects[parentID])

        cfg.evelocations.Prime(objects.keys(), 0)
        self.orbitLineSet.SubmitChanges()
        return (parent, sunID)



    def FindCelestialParent(self, body, ssitems):
        bodyPos = geo2.Vector(body.x, body.y, body.z)
        planets = []
        typeinfo = cfg.invtypes.Get(body.typeID)
        if typeinfo.groupID == const.groupPlanet or typeinfo.groupID == const.groupStargate:
            for object in ssitems:
                typeinfo2 = cfg.invtypes.Get(object.typeID).groupID
                if typeinfo2 == const.groupSun:
                    return object.itemID

        for each in ssitems:
            if each.itemID == body.itemID:
                continue
            typeinfo = cfg.invtypes.Get(each.typeID)
            if typeinfo.groupID != const.groupPlanet:
                continue
            pos = geo2.Vector(each.x, each.y, each.z)
            diffPos = pos - bodyPos
            planets.append([geo2.Vec3Length(diffPos), each])

        planets.sort()
        return planets[0][1].itemID



    def Add3DCircle(self, orbitem, parent, points = 256):
        orbitPos = geo2.Vector(*orbitem.translation)
        parentPos = geo2.Vector(*parent.translation)
        dirVec = orbitPos - parentPos
        radius = geo2.Vec3Length(dirVec)
        if radius == 0:
            return 
        fwdVec = geo2.Vector(-1.0, 0.0, 0.0)
        dirVec = geo2.Vec3Normalize(dirVec)
        fwdVec = geo2.Vec3Normalize(fwdVec)
        color = (0.1, 0.1, 0.1, 1.0)
        stepSize = pi * 2.0 / points
        lineSet = self.orbitLineSet
        rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
        matrix = geo2.MatrixAffineTransformation(1.0, geo2.Vector(0.0, 0.0, 0.0), rotation, geo2.Vector(*parent.translation))
        coordinates = []
        for step in range(points):
            angle = step * stepSize
            x = cos(angle) * radius
            z = sin(angle) * radius
            pos = geo2.Vector(x, 0.0, z)
            pos = geo2.Vec3TransformCoord(pos, matrix)
            coordinates.append(pos)

        for start in xrange(points):
            end = (start + 1) % points
            lineSet.AddLine(coordinates[start], color, coordinates[end], color)





class BookmarkBracket(xtriui.BaseBracket):
    __guid__ = 'xtriui.BookmarkBracket'

    def Startup(self, itemID, groupID, categoryID, iconNo):
        xtriui.BaseBracket.Startup(self, itemID, groupID, categoryID, iconNo)
        sm.GetService('state').SetState(itemID, state.selected, 0)



    def GetMenu(self, *args):
        if getattr(self, 'bmData', None):
            bmData = getattr(self, 'bmData', None)
            m = sm.GetService('menu').CelestialMenu(bmData.itemID, bookmark=bmData)
            m.append((mls.UI_CMD_EDITVIEWLOCATION, sm.GetService('addressbook').EditBookmark, (bmData,)))
            return m
        if getattr(self, 'scanResult', None):
            return sm.GetService('menu').SolarsystemScanMenu(getattr(self, 'scanResult', None))



    def OnClick(self, *args):
        sm.GetService('state').SetState(self.itemID, state.selected, 1)



    def OnMouseEnter(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 1)



    def OnMouseExit(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 0)




