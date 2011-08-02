import service
import uthread
import blue
import uix
import spaceObject
import trinity
import util
import base
import math
import sys
import state
import log
import geo2
import uiconst
import uicls

class SpaceMgr(service.Service):
    __guid__ = 'svc.space'
    __update_on_reload__ = 0
    __exportedcalls__ = {'StopNavigation': [],
     'CanWarp': [],
     'StartPartitionDisplayTimer': [],
     'StopPartitionDisplayTimer': [],
     'WarpDestination': [],
     'IndicateWarp': [],
     'StartWarpIndication': [],
     'StopWarpIndication': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnDamageStateChange',
     'OnSpecialFX',
     'OnDockingAccepted',
     'ProcessSessionChange',
     'OnBallparkCall',
     'OnNotifyPreload']
    __dependencies__ = ['michelle', 'transmission', 'settings']

    def __init__(self):
        service.Service.__init__(self)
        self.groupClasses = spaceObject.GetGroupDict()
        self.categoryClasses = spaceObject.GetCategoryDict()
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        self.killPreloadLoop = True
        self.preloadTasklet = None
        self.lazyLoadQueueCount = 0
        self.preloadQueueCount = 0
        self.planetManager = PlanetManager()



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        sm.FavourMe(self.DoBallsAdded)
        for each in uicore.layer.shipui.children[:]:
            if each.name in ('caption', 'indicationtext'):
                each.Close()

        self.indicationtext = None
        self.caption = None



    def Stop(self, stream):
        self.Indicate(None, None)
        service.Service.Stop(self)



    def ProcessSessionChange(self, *args):
        self.Indicate(None, None)



    def LoadObject(self, ball, slimItem, ob):
        if slimItem is None:
            return 
        itemID = slimItem.itemID
        if getattr(ob, 'released', 1):
            self.LogWarn(slimItem.itemID, 'has already been released')
            return 
        try:
            ob.Prepare(self)
            ob.Display(1)
        except Exception as e:
            log.LogException('Error adding SpaceObject of type', str(ob.__klass__), 'to scene')
            sys.exc_clear()



    def DoBallsAdded(self, *args, **kw):
        lst = []
        ballsToAdd = args[0]
        for (ball, slimItem,) in ballsToAdd:
            try:
                groupID = slimItem.groupID
                categoryID = slimItem.categoryID
                if groupID is not None and groupID in self.groupClasses:
                    klass = self.groupClasses[groupID]
                elif categoryID is not None and categoryID in self.categoryClasses:
                    klass = self.categoryClasses[categoryID]
                else:
                    self.LogWarn('SpaceObject class not specified for group: ', groupID, '- defaulting to basic SpaceObject')
                    klass = spaceObject.SpaceObject
                ob = klass(ball)
                if groupID == const.groupPlanet or groupID == const.groupMoon:
                    self.planetManager.RegisterPlanetBall(ob)
                lst.append((ball, slimItem, ob))
            except (Exception,) as e:
                self.LogError('DoBallsAdded - failed to add ball', (ball, slimItem))
                log.LogException()
                sys.exc_clear()

        if settings.public.generic.Get('lazyLoading', 1):
            uthread.new(self.DoBallsAdded_, lst)
        else:
            self.DoBallsAdded_(lst)



    def DoBallsAdded_(self, ballsToAdd):
        stateMgr = sm.StartService('state')
        self.LogInfo('DoBallsAdded_ - Starting to add', len(ballsToAdd), ' balls. lazy = ', settings.public.generic.Get('lazyLoading', 1))
        numLostBalls = 0
        preEmptiveLoads = []
        remainingBalls = ballsToAdd
        self.lazyLoadQueueCount = len(ballsToAdd)
        timeStarted = blue.os.GetTime(1)
        for i in xrange(len(ballsToAdd)):
            try:
                self.lazyLoadQueueCount = len(ballsToAdd) - i - 1
                (ball, slimItem, ob,) = ballsToAdd[i]
                bp = sm.StartService('michelle').GetBallpark()
                if bp is None:
                    return 
                if trinity.device is None:
                    return 
                slimItem = bp.GetInvItem(slimItem.itemID)
                if slimItem is None:
                    numLostBalls += 1
                    continue
                itemID = slimItem.itemID
                for j in xrange(len(ballsToAdd[(i + 1):])):
                    (ball2, slimItem2, ob2,) = ballsToAdd[(i + j)]
                    itemID2 = slimItem2.itemID
                    isPreempt = False
                    if slimItem2 and itemID2 not in preEmptiveLoads:
                        if slimItem2.categoryID in (const.categoryShip,) and getattr(slimItem2, 'charID', None) or slimItem2.categoryID in (const.categoryEntity,):
                            (attacking, hostile,) = stateMgr.GetStates(itemID2, [state.threatAttackingMe, state.threatTargetsMe])
                            if attacking or hostile:
                                isPreempt = True
                        elif slimItem2.categoryID in (const.categoryCelestial,) or util.IsUniverseCelestial(itemID2):
                            isPreempt = True
                    if isPreempt:
                        self.LogInfo('Preemptively loading', itemID2)
                        self.LoadObject(ball2, slimItem2, ob2)
                        preEmptiveLoads.append(itemID2)

                if itemID in preEmptiveLoads:
                    continue
                self.LoadObject(ball, slimItem, ob)
                if settings.public.generic.Get('lazyLoading', 1):
                    blue.pyos.synchro.Yield()
            except:
                self.LogError('DoBallsAdded - failed to add ball', (ball, slimItem))
                log.LogException()
                sys.exc_clear()

        self.LogInfo('DoBallsAdded_ - Done adding', len(ballsToAdd), ' balls in', util.FmtDate(blue.os.GetTime(1) - timeStarted, 'nl'), '.', numLostBalls, 'balls were lost. lazy = ', settings.public.generic.Get('lazyLoading', 1))



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        self.LogInfo('DoBallRemove::spaceMgr', ball.id)
        if hasattr(ball, 'Release'):
            uthread.new(ball.Release)
        if slimItem.groupID == const.groupPlanet or slimItem.groupID == const.groupMoon:
            self.planetManager.UnRegisterPlanetBall(ball)



    def OnBallparkCall(self, functionName, args):
        if functionName == 'WarpTo':
            x = args[1]
            y = args[2]
            z = args[3]
            if not self.warpDestinationCache:
                self.warpDestinationCache = [None,
                 None,
                 None,
                 (x, y, z)]
            else:
                self.warpDestinationCache[3] = (x, y, z)
            if self.planetManager is not None:
                self.planetManager.CheckPlanetPreloadingOnWarp(self.warpDestinationCache[3])
        elif functionName == 'SetBallRadius':
            ballID = args[0]
            newRadius = args[1]
            ball = sm.GetService('michelle').GetBall(ballID)
            if hasattr(ball, 'SetRadius'):
                ball.SetRadius(newRadius)



    def OnNotifyPreload(self, typeIDList):
        if settings.public.generic.Get('preload', 1):
            self.preloadTasklet = uthread.new(self.PreloadLoop, typeIDList)
            self.preloadTasklet.context = 'SpaceMgr::PreloadLoop'
        else:
            self.LogWarn('Preloading disabled')



    def PreloadLoop(self, typeIDList):
        self.LogInfo('SpaceMgr::PreloadLoop got', len(typeIDList), 'types to preload')
        MIN_SECONDS_IN_WARP = 20
        self.killPreloadLoop = False
        startWarpTime = blue.os.GetTime(1)
        timeLeft = MIN_SECONDS_IN_WARP * SEC
        avg = 0.0
        times = []
        numBetweenYields = 1
        self.preloadQueueCount = len(typeIDList)
        for (i, typeID,) in enumerate(typeIDList):
            self.preloadQueueCount = len(typeIDList) - i - 1
            if self.killPreloadLoop:
                self.preloadQueueCount = 0
                self.LogInfo('Quitting preloadloop with', len(typeIDList) - i, 'types left')
                self.preloadTasklet = None
                return 
            itemType = cfg.invtypes.Get(typeID)
            if itemType.graphicID is None:
                continue
            graphicFile = itemType.GraphicFile().split(' ')[0].lower()
            groupID = itemType.Group().id
            categoryID = itemType.Group().Category().id
            preloadUrl = ''
            if categoryID in [const.categoryShip, const.categoryEntity, const.categoryCelestial]:
                preloadUrl = graphicFile.replace('res:/model', 'res:/dx9/model').replace('.blue', '.red')
            elif groupID in [const.groupCloud, const.groupHarvestableCloud]:
                preloadUrl = graphicFile
            if preloadUrl:
                self.LogInfo('SpaceMgr::PreloadLoop preloading typeID =', typeID, ' url =', preloadUrl)
                try:
                    t0 = blue.os.GetTime(1)
                    x = trinity.Load(preloadUrl)
                    if len(times) % numBetweenYields == 0:
                        blue.pyos.synchro.Yield()
                    t = blue.os.GetTime(1)
                    times.append(t - t0)
                    if len(times) > 5 and timeLeft > 0:
                        timePassed = t - startWarpTime
                        timeLeft = MIN_SECONDS_IN_WARP * SEC - timePassed
                        iLeft = len(typeIDList) - i
                        for t in times:
                            avg += t

                        avg = avg / float(len(times)) / float(SEC)
                        doneIn = iLeft * avg
                        old = numBetweenYields
                        if doneIn > timeLeft / SEC and timeLeft / SEC > 0:
                            numBetweenYields = 5
                        else:
                            numBetweenYields = 1
                        self.LogInfo('Preloaded', len(times), 'types with', timePassed / float(SEC), 'sec in warp -', timeLeft / SEC, 'sec for remaining', iLeft, 'types. Average load time:', avg, ' sec. Preload finished in', doneIn, 'sec')
                        if old != numBetweenYields:
                            self.LogInfo(i, 'Num yields: ', old, '->', numBetweenYields)
                except (StandardError,) as e:
                    self.LogInfo('... Failed to preload', preloadUrl)
                    sys.exc_clear()




    def OnDamageStateChange(self, shipID, damageState):
        ball = sm.GetService('michelle').GetBall(shipID)
        if ball:
            if hasattr(ball, 'OnDamageState'):
                ball.OnDamageState(damageState)



    def OnTutorialStateChange(self, inTutorial):
        self.inTutorial = inTutorial



    def WarpDestination(self, celestialID, bookmarkID, fleetMemberID):
        self.warpDestinationCache[0] = celestialID
        self.warpDestinationCache[1] = bookmarkID
        self.warpDestinationCache[2] = fleetMemberID



    def StartWarpIndication(self):
        self.ConfirmWarpDestination()
        eve.Message('WarpDriveActive')
        self.LogNotice('StartWarpIndication', self.warpDestinationText, 'autopilot =', sm.GetService('autoPilot').GetState())



    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        self.LogInfo('Space::OnSpecialFX - ', guid)
        if util.IsFullLogging():
            self.LogInfo(shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration, repeat)
        if shipID == eve.session.shipid and guid in ('effects.JumpOut', 'effects.JumpOutWormhole'):
            bp = sm.StartService('michelle').GetBallpark()
            slimItem = bp.GetInvItem(targetID)
            if guid == 'effects.JumpOut':
                locations = [slimItem.jumps[0].locationID, slimItem.jumps[0].toCelestialID]
                cfg.evelocations.Prime(locations)
                solname = cfg.evelocations.Get(slimItem.jumps[0].locationID).name
                destname = cfg.evelocations.Get(slimItem.jumps[0].toCelestialID).name
                sm.GetService('logger').AddText(mls.UI_INFLIGHT_JUMPINGTO % {'location': destname,
                 'solarsystem': solname})
                self.Indicate(mls.UI_GENERIC_JUMPING, '<center>' + mls.UI_INFLIGHT_DESTINATIONIS % {'dest': destname,
                 'solarsystem': solname})
            elif guid == 'effects.JumpOutWormhole':
                if otherTypeID is None:
                    otherTypeID = 0
                self.Indicate(mls.UI_GENERIC_JUMPING_WORMHOLE, '<center>' + mls.UI_INFLIGHT_WORMHOLEJUMPING % {'space': getattr(mls, 'UI_GENERIC_WORMHOLECLASS_%s' % otherTypeID)})



    def OnDockingAccepted(self, dockingStartPos, dockingEndPos, stationID):
        sm.GetService('space').StopNavigation()
        eve.Message('DockingAccepted')
        self.Indicate(mls.UI_INFLIGHT_DOCKING, '<center>%s: %s' % (mls.UI_GENERIC_STATION, cfg.evelocations.Get(stationID).name))



    def CanWarp(self, targetID = None, forTut = False):
        tutorialBrowser = sm.GetService('tutorial').GetTutorialBrowser(create=0)
        if tutorialBrowser and not forTut and hasattr(tutorialBrowser, 'current'):
            (_tutorialID, _pageNo, _pageID, _pageCount, _sequenceID, _VID, _pageActionID,) = tutorialBrowser.current
            if _tutorialID is not None and _sequenceID is not None:
                return sm.GetService('tutorial').CheckWarpDriveActivation(_sequenceID, _tutorialID)
        return 1



    def OnReleaseBallpark(self):
        self.flashTransform = None



    def FlashScreen(self, magnitude, duration = 0.5):
        if hasattr(self, 'flashingScreen'):
            if self.flashingScreen:
                return 
        self.flashingScreen = 1

        def setFlashTransform():
            flashTransform = eve.rot.GetInstance('res:/Model/Global/flash.blue')
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            scene.children.append(flashTransform)
            self.flashTransform = flashTransform


        if not hasattr(self, 'flashTransform'):
            setFlashTransform()
        if not self.flashTransform:
            setFlashTransform()
        flashTransform = self.flashTransform
        damat = flashTransform.object.areas[0].areaMaterials[0]
        black = trinity.TriColor()
        black.a = 0.0
        alphaCurve = blue.os.CreateInstance('trinity.TriColorCurve')
        alphaCurve.extrapolation = trinity.TRIEXT_CONSTANT
        alphaCurve.AddKey(0.0, black, black, black, 3)
        alphaCurve.AddKey(duration, black, black, black, 3)
        alphaCurve.Sort()
        alphaCurve.keys[0].value.a = magnitude
        if damat.diffuseCurve.GetColorAt(blue.os.GetTime(1)).a > magnitude:
            return 
        displayCurve = flashTransform.displayCurve
        displayCurve.keys[1].time = duration
        displayCurve.Sort()
        damat.diffuseCurve = alphaCurve
        alphaCurve.start = blue.os.GetTime(1)
        displayCurve.start = blue.os.GetTime(1)
        self.flashingScreen = 0



    def StopNavigation(self):
        nav = uix.GetInflightNav(0)
        if nav is not None:
            nav.Close()



    def CheckWarpDestination(self, warpPoint, destinationPoint, egoPoint, angularTolerance, distanceTolerance):
        destinationOffset = [destinationPoint[0] - warpPoint[0], destinationPoint[1] - warpPoint[1], destinationPoint[2] - warpPoint[2]]
        destinationDirection = [warpPoint[0] - egoPoint[0], warpPoint[1] - egoPoint[1], warpPoint[2] - egoPoint[2]]
        warpDirection = [destinationPoint[0] - egoPoint[0], destinationPoint[1] - egoPoint[1], destinationPoint[2] - egoPoint[2]]
        vlen = self.VectorLength(destinationDirection)
        destinationDirection = [ x / vlen for x in destinationDirection ]
        vlen = self.VectorLength(warpDirection)
        warpDirection = [ x / vlen for x in warpDirection ]
        angularDifference = warpDirection[0] * destinationDirection[0] + warpDirection[1] * destinationDirection[1] + warpDirection[2] * destinationDirection[2]
        angularDifference = min(max(-1.0, angularDifference), 1.0)
        angularDifference = math.acos(angularDifference)
        if abs(angularDifference) < angularTolerance or self.VectorLength(destinationOffset) < distanceTolerance:
            return True
        else:
            return False



    def VectorLength(self, vector):
        result = 0
        for i in vector:
            result += pow(i, 2)

        return pow(result, 0.5)



    def GetWarpDestinationName(self, id):
        name = None
        item = uix.GetBallparkRecord(id)
        if item is None or item.categoryID not in [const.groupAsteroid]:
            name = cfg.evelocations.Get(id).name
        if not name and item:
            name = cfg.invtypes.Get(item.typeID).typeName
        return name



    def ConfirmWarpDestination(self):
        (destinationItemID, destinationBookmarkID, destinationfleetMemberID, destinationPosition, actualDestinationPosition,) = self.warpDestinationCache
        self.warpDestinationText = ''
        self.warpDestinationCache[4] = None
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return 
        egoball = ballPark.GetBall(ballPark.ego)
        if destinationItemID:
            if destinationItemID in ballPark.balls:
                b = ballPark.balls[destinationItemID]
                if self.CheckWarpDestination(destinationPosition, (b.x, b.y, b.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                    self.warpDestinationCache[4] = (b.x, b.y, b.z)
                    name = self.GetWarpDestinationName(destinationItemID)
                    self.warpDestinationText = '%s: %s<br>' % (mls.UI_GENERIC_DESTINATION, name)
        elif destinationBookmarkID:
            bookmarks = sm.GetService('addressbook').GetBookmarks()
            if destinationBookmarkID in bookmarks:
                bookmark = bookmarks[destinationBookmarkID]
                if bookmark.x is None:
                    if bookmark.memo:
                        titleEndPosition = bookmark.memo.find('\t')
                        if titleEndPosition > -1:
                            memoTitle = bookmark.memo[:titleEndPosition]
                        else:
                            memoTitle = bookmark.memo
                        self.warpDestinationText = '%s: %s<br>' % (mls.UI_GENERIC_DESTINATION, memoTitle)
                        if bookmark.itemID is not None:
                            b = ballPark.balls[bookmark.itemID]
                            if self.CheckWarpDestination(destinationPosition, (b.x, b.y, b.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                                self.warpDestinationCache[4] = (b.x, b.y, b.z)
                elif self.CheckWarpDestination(destinationPosition, (bookmark.x, bookmark.y, bookmark.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                    if bookmark.memo:
                        titleEndPosition = bookmark.memo.find('\t')
                        if titleEndPosition > -1:
                            memoTitle = bookmark.memo[:titleEndPosition]
                        else:
                            memoTitle = bookmark.memo
                        self.warpDestinationText = '%s: %s<br>' % (mls.UI_GENERIC_DESTINATION, memoTitle)
                        self.warpDestinationCache[4] = (bookmark.x, bookmark.y, bookmark.z)



    def IndicateWarp(self):
        (destinationItemID, destinationBookmarkID, destinationfleetMemberID, destinationPosition, actualDestinationPosition,) = self.warpDestinationCache
        if not destinationPosition:
            self.LogError('Space::IndicateWarp: Something is messed up, didnt get ballpark coordinates to verify warp')
            return 
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            self.LogWarn('Space::IndicateWarp: Trying to indicate warp without a ballpark?')
            return 
        text = '<center>' + getattr(self, 'warpDestinationText', '')
        egoball = ballPark.GetBall(ballPark.ego)
        if actualDestinationPosition is not None:
            warpDirection = [actualDestinationPosition[0] - egoball.x, actualDestinationPosition[1] - egoball.y, actualDestinationPosition[2] - egoball.z]
        else:
            warpDirection = [destinationPosition[0] - egoball.x, destinationPosition[1] - egoball.y, destinationPosition[2] - egoball.z]
        dist = self.VectorLength(warpDirection)
        if dist:
            text += '<center>%s: %s' % (mls.UI_GENERIC_DISTANCE, util.FmtDist(dist))
            if actualDestinationPosition is None:
                text += ' ' + mls.UI_INFLIGHT_DISTANCETOWARPBUBBLECOLLAPSE
        self.Indicate(mls.UI_INFLIGHT_WARPDRIVEACTIVE, text)
        self.LogInfo('Space::IndicateWarp', text)



    def Indicate(self, header, strng, delayMs = 0):
        if header is None and strng is None:
            if self.indicationtext is not None and not self.indicationtext.destroyed:
                self.indicationtext.Close()
                self.indicationtext = None
                self.caption.Close()
                self.caption = None
            return 
        if self.indicationtext is None or self.indicationtext.destroyed:
            self.indicationtext = uicls.Label(parent=uicore.layer.shipui.sr.indicationContainer, name='indicationtext', text=strng, align=uiconst.TOPLEFT, width=400, autoheight=1, state=uiconst.UI_DISABLED, autowidth=0)
            self.caption = uicls.CaptionLabel(text=header, parent=uicore.layer.shipui.sr.indicationContainer, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, top=1)
        else:
            self.indicationtext.text = strng
            self.caption.text = header
        if uicore.layer.shipui.sr.indicationContainer is None:
            return 
        self.indicationtext.left = (uicore.layer.shipui.sr.indicationContainer.width - self.indicationtext.width) / 2
        self.indicationtext.top = self.caption.top + self.caption.height
        if delayMs:
            uthread.new(self._DelayShowIndicateMsg, delayMs)



    def _DelayShowIndicateMsg(self, delayMs):
        if self.caption is None or self.caption.destroyed:
            return 
        self.caption.SetAlpha(0.0)
        self.indicationtext.SetAlpha(0.0)
        blue.pyos.synchro.Sleep(delayMs)
        if self.caption:
            self.caption.SetAlpha(1.0)
        if self.indicationtext:
            self.indicationtext.SetAlpha(1.0)



    def StopWarpIndication(self):
        self.LogNotice('StopWarpIndication', getattr(self, 'warpDestinationText', '-'), 'autopilot =', sm.GetService('autoPilot').GetState())
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        self.Indicate(None, None)
        self.transmission.StopWarpIndication()
        self.killPreloadLoop = True
        if self.planetManager is not None:
            self.planetManager.StopPlanetPreloading()



    def KillIndicationTimer(self, guid):
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        if hasattr(self, guid):
            delattr(self, guid)
            self.Indicate(None, None)
        self.killPreloadLoop = True



    def StartPartitionDisplayTimer(self, boxsize = 7):
        self.StopPartitionDisplayTimer()
        settings.user.ui.Set('partition_box_size', boxsize)
        self.partitionDisplayTimer = base.AutoTimer(50, self.UpdatePartitionDisplay)



    def StopPartitionDisplayTimer(self):
        self.partitionDisplayTimer = None
        self.CleanPartitionDisplay()



    def UpdatePartitionDisplay(self):
        boxRange = settings.user.ui.Get('partition_box_size', 7)
        allboxes = settings.user.ui.Get('partition_box_showall', 1)
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            self.StopPartitionDisplayTimer()
            return 
        box = eve.rot.GetInstance('res:/Model/Global/partitionBox.blue')
        egoball = ballpark.GetBall(ballpark.ego)
        boxesToDelete = []
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        for model in scene.children:
            if model.name == 'partitionBox':
                boxesToDelete.append(model)

        if allboxes == 1:
            boxRange = range(boxRange, 8)
        else:
            boxRange = [boxRange]
        for boxSize in boxRange:
            boxes = ballpark.GetActiveBoxes(boxSize)
            (width, coords,) = boxes
            if not boxes:
                continue
            for (x, y, z,) in coords:
                tf = trinity.TriTransform()
                x = x - egoball.x + width / 2
                y = y - egoball.y + width / 2
                z = z - egoball.z + width / 2
                tf.scaling.SetXYZ(width, width, width)
                tf.name = 'partitionBox'
                tf.children.append(box)
                tf.translation.SetXYZ(x, y, z)
                scene.children.append(tf)


        for model in boxesToDelete:
            scene.children.fremove(model)




    def CleanPartitionDisplay(self):
        boxesToDelete = []
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        for model in scene.children:
            if model.name == 'partitionBox':
                boxesToDelete.append(model)

        for model in boxesToDelete:
            scene.children.fremove(model)





class PlanetManager():

    def __init__(self):
        self.renderTarget = None
        self.offscreenSurface = None
        self.processingList = []
        self.planets = []
        self.planetWarpingList = []
        self.worker = None
        self.format = trinity.TRIFMT_A8R8G8B8
        self.maxSize = 2048
        self.maxSizeLimit = 2048



    def RegisterPlanetBall(self, planet):
        self.planets.append(planet)



    def UnRegisterPlanetBall(self, planet):
        planet = self.GetPlanet(planet.id)
        if planet is not None:
            self.planets.remove(planet)



    def DoPlanetPreprocessing(self, planet, size):
        self.processingList.append((planet, size))
        if self.worker is not None:
            if self.worker.alive:
                return 
        self.worker = uthread.new(self.PreProcessAll)



    def CreateRenderTarget(self):
        deviceSvc = sm.GetService('device')
        textureQuality = prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())
        self.maxSizeLimit = size = self.maxSize >> textureQuality
        rt = None
        while rt is None:
            try:
                rt = trinity.device.CreateRenderTarget(2 * size, size, self.format, trinity.TRIMULTISAMPLE_NONE, 0, 0)
            except trinity.D3DERR_OUTOFVIDEOMEMORY:
                if size < 2:
                    return 
                self.maxSizeLimit = size = size / 2
                rt = None
            except:
                return 

        return rt



    def CreateOffscreenSurface(self):
        deviceSvc = sm.GetService('device')
        textureQuality = prefs.GetValue('textureQuality', deviceSvc.GetDefaultTextureQuality())
        size = self.maxSize >> textureQuality
        return trinity.device.CreateOffscreenPlainSurface(2 * size, size, self.format, trinity.TRIPOOL_SYSTEMMEM)



    def PreProcessAll(self):
        if self.renderTarget is None:
            self.renderTarget = trinity.TriSurfaceManaged(self.CreateRenderTarget)
        if self.offscreenSurface is None:
            self.offscreenSurface = trinity.TriSurfaceManaged(self.CreateOffscreenSurface)
        while len(self.processingList) > 0:
            (planet, size,) = self.processingList.pop(0)
            if size > self.maxSizeLimit:
                size = self.maxSizeLimit
            planet.DoPreProcessEffect(size, self.format, self.renderTarget, self.offscreenSurface)




    def GetPlanet(self, ballid):
        for planet in self.planets:
            if planet.id == ballid:
                return planet




    def StopPlanetPreloading(self):
        for planet in self.planets:
            planet.WarpStopped()




    def DistanceFromSegment(self, p, p0, p1, v, c2):
        w = geo2.Vec3Subtract(p, p0)
        c1 = geo2.Vec3Dot(v, w)
        if c1 <= 0:
            return None
        if c2 <= c1:
            return geo2.Vec3Distance(p, p1)
        return geo2.Vec3Distance(p, geo2.Vec3Add(p0, geo2.Vec3Scale(v, c1 / c2)))



    def CheckPlanetPreloadingOnWarp(self, destinationWarpPoint):
        uthread.new(self._CheckPlanetPreloadingOnWarp, destinationWarpPoint)



    def _CheckPlanetPreloadingOnWarp(self, destinationWarpPoint):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        shipBall = ballpark.GetBall(eve.session.shipid)
        if shipBall is None:
            return 
        p1 = destinationWarpPoint
        p0 = (shipBall.x, shipBall.y, shipBall.z)
        v = geo2.Vec3Subtract(p1, p0)
        c2 = geo2.Vec3Dot(v, v)
        for planet in self.planets:
            blue.pyos.BeNice()
            planetBall = ballpark.GetBall(planet.id)
            if planetBall is not None:
                p = (planetBall.x, planetBall.y, planetBall.z)
                distance = self.DistanceFromSegment(p, p0, p1, v, c2)
                if distance is not None:
                    planet.PrepareForWarp(distance, destinationWarpPoint)





