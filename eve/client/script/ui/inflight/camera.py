import sys
import uix
import mathUtil
import blue
import service
import util
import xtriui
import types
import trinity
import base
import listentry
import uthread
import form
import state
import destiny
import draw
import math
import hint
import log
import dbg
import _weakref
import uthread
import geo2
import uiconst
import uicls
from math import sin, cos, tan, pi
from foo import Vector3
from mapcommon import ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP, ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP
SIZEFACTOR = 1e-07
FREELOOK_KEYS = 'WASDRF'

class CameraMgr(service.Service):
    __guid__ = 'svc.camera'
    __update_on_reload__ = 0
    __notifyevents__ = ['OnSpecialFX',
     'DoBallClear',
     'DoBallRemove',
     'OnSessionChanged',
     'OnSetDevice']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.freeLook = False
        self.clientToolsScene = None



    def Run(self, *args):
        self.Reset()
        self.pending = None
        self.busy = None



    def Stop(self, stream):
        self.Cleanup()



    def DoBallClear(self, solitem):
        if self.IsFreeLook():
            self.SetFreeLook(False)
        cameraParent = self.GetCameraParent()
        if cameraParent:
            cameraParent.translationCurve = None



    def DoBallRemove(self, ball, slimItem, terminal):
        uthread.new(self.AdjustLookAtTarget, ball)



    def AdjustLookAtTarget(self, ball):
        cameraParent = self.GetCameraParent()
        lookingAtID = self.LookingAt()
        if cameraParent and cameraParent.translationCurve and cameraParent.translationCurve == ball:
            if self.IsFreeLook():
                self.SetFreeLook(False)
            cameraParent.translationCurve = None
        if lookingAtID and ball.id == lookingAtID and lookingAtID != eve.session.shipid:
            self.LookAt(eve.session.shipid)



    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        if guid == 'effects.Warping' and shipID == eve.session.shipid:
            if self.IsFreeLook():
                self.SetFreeLook(False)
            if self.LookingAt() != eve.session.shipid:
                self.LookAt(eve.session.shipid)



    def OnSetDevice(self, *args):
        if session.stationid:
            return 
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        blue.synchro.Yield()
        self.boundingBoxCache = {}
        camera.translationFromParent.z = self.CheckTranslationFromParent(camera.translationFromParent.z)



    def OnSessionChanged(self, isRemote, sess, change):
        if 'locationid' in change.iterkeys():
            if self.IsFreeLook():
                self.SetFreeLook(False)



    def Cleanup(self):
        if trinity.device is None:
            return 
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        for attrName in ['cameraParent']:
            each = getattr(self, attrName, None)
            if each and each in scene.models:
                scene.models.remove(each)
            setattr(self, attrName, None)




    def Reset(self):
        self.inited = 0
        self.lookingAt = None
        self.ssitems = {}
        self.boundingBoxCache = {}
        self.solarsystem = None
        self.rangeCircles = None
        self.currentSolarsystemID = None
        self.solarsystemSunID = None
        self.current = None
        self.flareData = None
        self.hiddenSpaceObjects = {}
        self.lastInflightLookat = None
        self.zoomFactor = None
        self.ssbracketsLoaded = False
        self.rangeNumberShader = None
        self.viewlevels = ['default', 'systemmap', 'starmap']
        self.translatedViewLevels = {'default': mls.UI_CMD_INFLIGHT,
         'systemmap': mls.UI_GENERIC_SOLARSYSTEMMAP,
         'starmap': mls.UI_GENERIC_STARMAP}
        self.mmUniverse = (-100.0, -20000.0)
        self.mmRegion = (-100.0, -20000.0)
        self.mmConstellation = (-100.0, -20000.0)
        self.mmSolarsystem = (-1000.0, -300000.0)
        self.mmTactical = (-500.0, -700000.0)
        self.mmSpace = (-30.0, -1000000.0)
        tm = sm.GetService('tactical').GetMain()
        if tm:
            for each in tm.children[:]:
                if each.name in ('camerastate', 'camlevels'):
                    each.Close()

        st = uicore.layer.station
        if st:
            for each in st.children[:]:
                if each.name in ('camerastate', 'camlevels'):
                    each.Close()

        self.freeLook = False
        self.drawAxis = True
        self.gridEnabled = True
        self.gridSpacing = 1000.0
        self.gridLength = 20000.0
        self.camBall = None



    def Zoom(self, direction = 1):
        print 'Camera Zoom',
        print direction



    def SetCameraInterest(self, itemID):
        if self.freeLook:
            return 
        cameraInterest = self.GetCameraInterest()
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if itemID is None:
            camera.interest = None
            cameraInterest.translationCurve = None
            return 
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            camera.interest = None
            cameraInterest.translationCurve = None
            return 
        tracker = None
        if item.model.__bluetype__ in ('eve.EveShip', 'eve.EveStation'):
            tracker = trinity.EveSOModelCenterPos()
            tracker.parent = item.model
        elif item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
        if scene.globalScale == 1.0:
            if tracker:
                cameraInterest.translationCurve = tracker
            else:
                cameraInterest.translationCurve = item
            cameraInterest.useCurves = 1
        camera.interest = cameraInterest



    def SetCameraParent(self, itemID):
        if self.freeLook:
            return 
        cameraParent = self.GetCameraParent()
        if cameraParent is None:
            return 
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            self.LookAt(eve.session.shipid)
            return 
        tracker = None
        tempTF = None
        if item.model.__bluetype__ in ('eve.EveShip', 'eve.EveStation'):
            tracker = trinity.EveSOModelCenterPos()
            tracker.parent = item.model
        elif item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if tracker:
            cameraParent.translationCurve = tracker
        else:
            cameraParent.translationCurve = item
        cameraParent.useCurves = 1
        camera.parent = cameraParent



    def LookAt(self, itemID, setZ = None, ignoreDist = 0, resetCamera = False):
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            if hasattr(item, 'loadingModel'):
                while item.loadingModel:
                    blue.synchro.Yield()

        if self.IsFreeLook():
            self.camBall.x = item.x
            self.camBall.y = item.y
            self.camBall.z = item.z
            return 
        obs = sm.GetService('target').IsObserving()
        scene = sm.GetService('sceneManager').GetRegisteredScene2('default')
        if itemID != eve.session.shipid:
            if scene.dustfield is not None:
                scene.dustfield.display = 0
            if item.mode == destiny.DSTBALL_WARP:
                return 
            if not (ignoreDist or obs) and item.surfaceDist > 100000.0:
                uicore.Say(mls.UI_MENUHINT_CHECKLOOKATDISTNOT)
                return 
        elif scene.dustfield is not None:
            scene.dustfield.display = 1
        uthread.pool('MenuSvc>LookAt', self._LookAt, item, itemID, setZ, resetCamera)



    def _LookAt(self, item, itemID, setZ = None, resetCamera = False):
        if not item:
            return 
        if item.GetModel() is None:
            return 
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        camera.interest = None
        self.GetCameraInterest().translationCurve = None
        cameraParent = self.GetCameraParent()
        if cameraParent is None:
            return 
        sm.StartService('state').SetState(itemID, state.lookingAt, 1)
        self.lookingAt = itemID
        item.LookAtMe()
        if cameraParent.translationCurve:
            startPos = cameraParent.translationCurve.GetVectorAt(blue.os.GetTime())
            cameraParent.translationCurve = None
        else:
            startPos = camera.parent.translation.CopyTo()
        startFov = camera.fieldOfView
        if resetCamera:
            endFov = sm.GetService('gameui').maxFov
        else:
            endFov = camera.fieldOfView
        if setZ is not None:
            camera.translationFromParent.z = self.CheckTranslationFromParent(setZ)
            startTrZ = None
            endTrZ = None
        else:
            startTrZ = camera.translationFromParent.z
            endTrZ = self.CheckTranslationFromParent(1.0) * 2
        start = blue.os.GetTime()
        ndt = 0.0
        time = 500.0
        tracker = None
        tempTF = None
        if item.model.__bluetype__ in ('eve.EveShip', 'eve.EveStation'):
            tracker = trinity.EveSOModelCenterPos()
            tracker.parent = item.model
            tempTF = trinity.TriTransform()
            tempTF.useCurves = 1
            tempTF.translationCurve = tracker
            scene.models.append(tempTF)
        elif item.model.__bluetype__ in ('trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
            tracker = trinity.EveSO2ModelCenterPos()
            tracker.parent = item.model
            tempTF = trinity.TriTransform()
            tempTF.useCurves = 1
            tempTF.translationCurve = tracker
            scene.models.append(tempTF)
        while ndt != 1.0:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            if tracker:
                endPos = tracker.value.CopyTo()
            elif getattr(item.model, 'translationCurve', None) is not None:
                endPos = item.model.translationCurve.GetVectorAt(blue.os.GetTime())
            else:
                endPos = item.model.translation.CopyTo()
            endPos.Scale(scene.globalScale)
            if startPos and endPos:
                cameraParent.translation.x = mathUtil.Lerp(startPos.x, endPos.x, ndt)
                cameraParent.translation.y = mathUtil.Lerp(startPos.y, endPos.y, ndt)
                cameraParent.translation.z = mathUtil.Lerp(startPos.z, endPos.z, ndt)
            if startTrZ and endTrZ:
                camera.translationFromParent.z = mathUtil.Lerp(startTrZ, endTrZ, ndt)
            if startFov != endFov:
                camera.fieldOfView = mathUtil.Lerp(startFov, endFov, ndt)
            blue.pyos.synchro.Yield()

        if scene.globalScale == 1.0:
            if tracker:
                cameraParent.translationCurve = tracker
            else:
                cameraParent.translationCurve = item
            cameraParent.useCurves = 1
        if tempTF:
            scene.models.remove(tempTF)
        if self.current == 'default':
            self.lastInflightLookat = [itemID, camera.translationFromParent.z]



    def PanCamera(self, posbeg = None, posend = None, cambeg = None, camend = None, time = 500.0, thread = 1, fovEnd = None, source = 'default'):
        if self.IsFreeLook():
            return 
        if thread:
            uthread.new(self._PanCamera, posbeg, posend, cambeg, camend, fovEnd, time, source)
        else:
            self._PanCamera(posbeg, posend, cambeg, camend, fovEnd, time, source)



    def _PanCamera(self, posbeg = None, posend = None, cambeg = None, camend = None, fovEnd = None, time = 500.0, source = 'default'):
        cameraParent = self.GetCameraParent(source)
        if cameraParent is None:
            return 
        start = blue.os.GetTime()
        ndt = 0.0
        fovBeg = None
        camera = sm.GetService('sceneManager').GetRegisteredCamera(source)
        if fovEnd is not None:
            fovBeg = camera.fieldOfView
        while ndt != 1.0:
            ndt = max(0.0, min(blue.os.TimeDiffInMs(start) / time, 1.0))
            if posbeg and posend:
                cameraParent.translation.x = mathUtil.Lerp(posbeg.x, posend.x, ndt)
                cameraParent.translation.y = mathUtil.Lerp(posbeg.y, posend.y, ndt)
                cameraParent.translation.z = mathUtil.Lerp(posbeg.z, posend.z, ndt)
            if cambeg and camend:
                camera.translationFromParent.z = self.CheckTranslationFromParent(mathUtil.Lerp(cambeg, camend, ndt), source=source)
            if fovBeg and fovEnd:
                camera.fieldOfView = mathUtil.Lerp(fovBeg, fovEnd, ndt)
            blue.pyos.synchro.Yield()




    def GetCameraParent(self, source = 'default'):
        sceneManager = sm.services.get('sceneManager', None)
        if sceneManager is None or sceneManager.state != service.SERVICE_RUNNING:
            return 
        scene = sceneManager.GetRegisteredScene(source)
        camera = sceneManager.GetRegisteredCamera(source)
        if scene is None or camera is None:
            return 
        cameraParent = getattr(self, 'cameraParent_%s' % source, None)
        if cameraParent is None:
            for each in scene.models:
                if each.name == 'cameraParent':
                    setattr(self, 'cameraParent_%s' % source, each)
                    cameraParent = each
                    break
            else:
                cameraParent = trinity.TriTransform()
                cameraParent.name = 'cameraParent'
                scene.models.append(cameraParent)
                setattr(self, 'cameraParent_%s' % source, cameraParent)

        if cameraParent != camera.parent:
            if camera.parent:
                cameraParent.translation = camera.parent.translation.CopyTo()
            else:
                cameraParent.translation.SetXYZ(0.0, 0.0, 0.0)
        if camera.parent != cameraParent:
            camera.parent = cameraParent
        return cameraParent



    def GetCameraInterest(self, source = 'default'):
        scene = sm.GetService('sceneManager').GetRegisteredScene(source)
        cameraInterest = getattr(self, 'cameraInterest_%s' % source, None)
        if cameraInterest is None:
            for each in scene.models:
                if each.name == 'cameraInterest':
                    setattr(self, 'cameraInterest_%s' % source, each)
                    cameraInterest = each
                    break
            else:
                cameraInterest = trinity.TriTransform()
                cameraInterest.name = 'cameraInterest'
                scene.models.append(cameraInterest)
                setattr(self, 'cameraInterest_%s' % source, cameraInterest)

        return cameraInterest



    def ResetCamera(self, *args):
        self.LookAt(eve.session.shipid)



    def LookingAt(self):
        return getattr(self, 'lookingAt', eve.session.shipid)



    def GetTranslationFromParentForItem(self, itemID, fov = None):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if fov is None:
            fov = camera.fieldOfView
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            ball = ballpark.GetBall(itemID)
            if ball and ball.model:
                rad = None
                if ball.model.__bluetype__ in ('eve.EveShip', 'eve.EveStation', 'trinity.EveShip2', 'trinity.EveStation2', 'trinity.EveRootTransform'):
                    rad = ball.model.GetBoundingSphereRadius()
                    zoomMultiplier = 1.0
                    aspectRatio = trinity.GetAspectRatio()
                    if aspectRatio > 1.6:
                        zoomMultiplier = aspectRatio / 1.6
                    return (rad + camera.frontClip) * zoomMultiplier + 2
                if hasattr(ball.model, 'children'):
                    if ball.model.children:
                        rad = ball.model.children[0].GetBoundingSphereRadius()
                if not rad or rad <= 0.0:
                    rad = ball.radius
                camangle = camera.fieldOfView * 0.5
                return max(15.0, rad / sin(camangle) * cos(camangle))



    def CheckTranslationFromParent(self, distance, getMinMax = 0, source = 'default'):
        if source == 'starmap':
            (mn, mx,) = (ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP)
        elif source == 'systemmap':
            (mn, mx,) = (ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP)
            aspectRatio = trinity.device.viewport.GetAspectRatio()
            if aspectRatio > 1.6:
                mx = mx * aspectRatio / 1.6
        else:
            lookingAt = self.LookingAt() or eve.session.shipid
            mn = 10.0
            if lookingAt not in self.boundingBoxCache:
                mn = self.GetTranslationFromParentForItem(lookingAt)
                if mn is not None:
                    self.boundingBoxCache[lookingAt] = mn
            else:
                mn = self.boundingBoxCache[lookingAt]
            (mn, mx,) = (mn, 1000000.0)
        retval = max(mn, min(distance, mx))
        if getMinMax:
            return (retval, mn, mx)
        self.RegisterCameraTranslation(retval, source)
        return retval



    def ClearBoundingInfoForID(self, id):
        if id in self.boundingBoxCache:
            del self.boundingBoxCache[id]



    def RegisterCameraTranslation(self, tr, source):
        settings.user.ui.Set('%sTFP' % source, tr)
        if source == 'default' and getattr(self, 'lastInflightLookat', None):
            self.lastInflightLookat[1] = tr



    def GetMyPos(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp and bp.ego:
            ego = bp.balls[bp.ego]
            myPos = trinity.TriVector(ego.x, ego.y, ego.z)
        elif eve.session.stationid:
            s = sm.RemoteSvc('stationSvc').GetStation(eve.session.stationid)
            myPos = trinity.TriVector(s.x, s.y, s.z)
        else:
            myPos = trinity.TriVector()
        return myPos



    def IsFreeLook(self):
        return self.freeLook



    def SetFreeLook(self, freeLook = True):
        if self.freeLook == freeLook:
            return 
        self.freeLook = freeLook
        camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
        cmdSvc = uicore.cmd
        if freeLook:
            playerPos = self.GetMyPos()
            bp = sm.StartService('michelle').GetBallpark()
            if self.camBall is None or self.camBall.ballpark != bp:
                self.camBall = bp.AddBall(0, 1.0, 0.0, 0, 0, 0, 0, 0, 0, playerPos.x, playerPos.y, playerPos.z, 0, 0, 0, 0, 1.0)
            cameraParent = self.GetCameraParent()
            cameraParent.translationCurve = self.camBall
            cameraParent.rotationCurve = self.camBall
            cameraParent.useCurves = 1
            cameraParent.Update(blue.os.GetTime())
            self.axisLines = trinity.Tr2LineSet()
            self.axisLines.effect = trinity.Tr2Effect()
            self.axisLines.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/LinesWithZ.fx'
            scene = self.GetClientToolsScene()
            self.clientToolsScene.primitives.append(self.axisLines)
            self._ChangeCamPos(-camera.parent.translation)
            self.BuildGridAndAxes()
            uthread.new(self._UpdateFreelookCamera)
        else:
            self.ResetCamera()
            try:
                self.clientToolsScene.primitives.remove(self.axisLines)
            except ValueError:
                pass
            self.axisLines = None



    def IsDrawingAxis(self):
        return self.drawAxis



    def SetDrawAxis(self, enabled = True):
        self.drawAxis = enabled



    def IsGridEnabled(self):
        return self.gridEnabled



    def SetGridState(self, enabled = True):
        self.gridEnabled = enabled



    def GetGridSpacing(self):
        return self.gridSpacing



    def SetGridSpacing(self, spacing = 100.0):
        if self.gridLength / spacing > 200:
            spacing = self.gridLength / 200
        elif self.gridLength / spacing <= 1:
            spacing = self.gridLength / 20
        if spacing < 1.0:
            spacing = 1.0
        self.gridSpacing = spacing
        self.BuildGridAndAxes()



    def GetGridLength(self):
        return self.gridLength



    def SetGridLength(self, length = 100.0):
        if length / self.gridSpacing > 200:
            self.gridSpacing = length / 200
        elif length / self.gridSpacing <= 1:
            self.gridSpacing = length / 20
        if length < 1.0:
            length = 1.0
        self.gridLength = length
        self.BuildGridAndAxes()



    def BuildGridAndAxes(self):
        self.axisLines.ClearLines()
        self.axisLines.SubmitChanges()
        if self.IsDrawingAxis():
            red = (1, 0, 0, 1)
            green = (0, 1, 0, 1)
            blue = (0, 0, 1, 1)
            xAxis = (100.0, 0.0, 0.0)
            yAxis = (0.0, 100.0, 0.0)
            zAxis = (0.0, 0.0, 100.0)
            origin = (0.0, 0.0, 0.0)
            self.axisLines.AddLine(origin, red, xAxis, red)
            self.axisLines.AddLine(origin, green, yAxis, green)
            self.axisLines.AddLine(origin, blue, zAxis, blue)
        if self.IsGridEnabled():
            grey = (0.4, 0.4, 0.4, 0.5)
            lightGrey = (0.5, 0.5, 0.5, 0.5)
            offWhite = (1, 1, 1, 0.8)
            minGridPos = -self.gridLength / 2.0
            maxGridPos = self.gridLength / 2.0
            halfNumSquares = int(self.gridLength / self.gridSpacing) / 2
            for i in xrange(-halfNumSquares, halfNumSquares + 1):
                color = grey
                if i % 10 == 0:
                    color = lightGrey
                if i % 20 == 0:
                    color = offWhite
                gridPos = i * self.gridSpacing
                startZ = (gridPos, 0.0, minGridPos)
                endZ = (gridPos, 0.0, maxGridPos)
                startX = (minGridPos, 0.0, gridPos)
                endX = (maxGridPos, 0.0, gridPos)
                if i != 0 or not self.drawAxis:
                    self.axisLines.AddLine(startZ, color, endZ, color)
                    self.axisLines.AddLine(startX, color, endX, color)
                else:
                    self.axisLines.AddLine(startZ, color, origin, color)
                    self.axisLines.AddLine(zAxis, color, endZ, color)
                    self.axisLines.AddLine(startX, color, origin, color)
                    self.axisLines.AddLine(xAxis, color, endX, color)

            color = offWhite
            startZ = (minGridPos, 0.0, minGridPos)
            endZ = (minGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, minGridPos)
            endX = (maxGridPos, 0.0, minGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
            startZ = (maxGridPos, 0.0, minGridPos)
            endZ = (maxGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, maxGridPos)
            endX = (maxGridPos, 0.0, maxGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
        self.axisLines.SubmitChanges()



    def _ChangeCamPos(self, vec):
        self.camBall.x += vec.x
        self.camBall.y += vec.y
        self.camBall.z += vec.z



    def _UpdateFreelookCamera(self):
        lastTime = blue.os.GetTime()
        while self.IsFreeLook():
            camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
            delta = blue.os.TimeDiffInMs(lastTime)
            keyDown = uicore.uilib.Key
            if keyDown(uiconst.VK_CONTROL) and not keyDown(uiconst.VK_MENU) and not keyDown(uiconst.VK_SHIFT):
                if keyDown(uiconst.VK_W):
                    self._ChangeCamPos(camera.viewVec * delta)
                if keyDown(uiconst.VK_S):
                    self._ChangeCamPos(-camera.viewVec * delta)
                if keyDown(uiconst.VK_A):
                    self._ChangeCamPos(-camera.rightVec * delta)
                if keyDown(uiconst.VK_D):
                    self._ChangeCamPos(camera.rightVec * delta)
                if keyDown(uiconst.VK_R):
                    self._ChangeCamPos(camera.upVec * delta)
                if keyDown(uiconst.VK_F):
                    self._ChangeCamPos(-camera.upVec * delta)
            self.axisLines.localTransform = geo2.MatrixTranslation(camera.parent.translation.x, camera.parent.translation.y, camera.parent.translation.z)
            lastTime = blue.os.GetTime()
            blue.synchro.Yield()




    def GetClientToolsScene(self):
        if self.clientToolsScene is not None:
            return self.clientToolsScene
        renderManager = sm.GetService('sceneManager')
        rj = renderManager.fisRenderJob
        scene = rj.GetClientToolsScene()
        if scene is not None:
            self.clientToolsScene = scene
            return self.clientToolsScene
        self.clientToolsScene = trinity.Tr2PrimitiveScene()
        rj.SetClientToolsScene(self.clientToolsScene)
        return self.clientToolsScene




