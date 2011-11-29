import trinity
import uthread
import uix
import uiutil
import state
import blue
import geo2
import maputils
import uicls
import form
from collections import namedtuple
import uiconst
import log
from mapcommon import SYSTEMMAP_SCALE
X_AXIS = geo2.Vector(1.0, 0.0, 0.0)
Y_AXIS = geo2.Vector(0.0, 1.0, 0.0)
Z_AXIS = geo2.Vector(0.0, 0.0, 1.0)
WorldToScreenParameters = namedtuple('WorldToScreenParameters', 'viewport projectionTransform viewTransform')

def GetRayAndPointFromScreen(x, y):
    (proj, view, vp,) = uix.GetFullscreenProjectionViewAndViewport()
    (ray, start,) = trinity.device.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
    ray = geo2.Vector(ray.x, ray.y, ray.z)
    start = geo2.Vector(start.x, start.y, start.z)
    return (ray, start)



def GetWorldToScreenParameters():
    dev = trinity.GetDevice()
    vp = dev.viewport
    viewport = (vp.x,
     vp.y,
     vp.width,
     vp.height,
     vp.minZ,
     vp.maxZ)
    camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
    viewTransform = ((camera.view._11,
      camera.view._12,
      camera.view._13,
      camera.view._14),
     (camera.view._21,
      camera.view._22,
      camera.view._23,
      camera.view._24),
     (camera.view._31,
      camera.view._32,
      camera.view._33,
      camera.view._34),
     (camera.view._41,
      camera.view._42,
      camera.view._43,
      camera.view._44))
    return WorldToScreenParameters(viewport, camera.triProjection.transform, viewTransform)



def ProjectTransform(projectionParameters, worldTransform):
    return geo2.Vec3Project(worldTransform[3][:3], projectionParameters.viewport, projectionParameters.projectionTransform, projectionParameters.viewTransform, worldTransform)



def RayToPlaneIntersection(P, d, Q, n):
    denom = geo2.Vec3Dot(n, d)
    if abs(denom) < 1e-05:
        return P
    else:
        distance = -geo2.Vec3Dot(Q, n)
        t = -(geo2.Vec3Dot(n, P) + distance) / denom
        scaledRay = geo2.Vector(*d) * t
        P += scaledRay
        return P



class SystemMapLayer(uicls.LayerCore):
    __guid__ = 'uicls.SystemMapLayer'
    __update_on_reload__ = 0
    __notifyevents__ = ['OnStateChange']

    def init(self):
        self.align = uiconst.TOALL
        self.cursor = uiconst.UICURSOR_SELECTDOWN
        self.activeManipAxis = None
        self._isPicked = False



    def Startup(self):
        self.sr.movingProbe = None
        self.sr.rangeProbe = None
        sm.RegisterNotify(self)



    def OnStateChange(self, itemID, flag, true, *args):
        if flag == state.selected and true:
            self.SetInterest(itemID)



    def SetInterest(self, itemID):
        solarsystem = sm.GetService('systemmap').GetCurrentSolarSystem()
        if solarsystem is None:
            log.LogTrace('No solar system (SystemmapNav::SetInterest)')
            return 
        endPos = None
        for tf in solarsystem.children:
            tfName = getattr(tf, 'name', None)
            if tfName is None:
                continue
            if tfName.startswith('systemParent_'):
                for stf in tf.children:
                    stfName = getattr(stf, 'name', None)
                    if stfName is None:
                        continue
                    try:
                        stfItemID = int(stfName.split('_')[1])
                    except:
                        continue
                    if stfItemID == itemID:
                        pos = (stf.worldTransform[3][0], stf.worldTransform[3][1], stf.worldTransform[3][2])
                        endPos = trinity.TriVector(*pos)
                        break

                if endPos:
                    break
                else:
                    continue
            if tfName.endswith(str(itemID)):
                pos = (tf.worldTransform[3][0], tf.worldTransform[3][1], tf.worldTransform[3][2])
                endPos = trinity.TriVector(*pos)
                break

        if endPos is None and itemID == eve.session.shipid:
            endPos = maputils.GetMyPos()
            endPos.Scale(SYSTEMMAP_SCALE)
        if endPos:
            now = blue.os.GetSimTime()
            cameraParent = sm.GetService('camera').GetCameraParent('systemmap')
            if cameraParent.translationCurve:
                startPos = cameraParent.translationCurve.GetVectorAt(now)
            else:
                startPos = cameraParent.translation
            nullV = trinity.TriVector()
            vc = trinity.TriVectorCurve()
            vc.extrapolation = trinity.TRIEXT_CONSTANT
            vc.AddKey(0.0, startPos, nullV, nullV, trinity.TRIINT_HERMITE)
            vc.AddKey(0.5, endPos, nullV, nullV, trinity.TRIINT_HERMITE)
            vc.Sort()
            cameraParent.translationCurve = vc
            cameraParent.useCurves = 1
            vc.start = now



    def OnMouseMove(self, *args):
        self.sr.hint = ''
        lib = uicore.uilib
        ctrl = lib.Key(uiconst.VK_CONTROL)
        alt = lib.Key(uiconst.VK_MENU)
        camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
        dx = lib.dx
        dy = lib.dy
        if not lib.leftbtn and not lib.rightbtn and not self.sr.rangeProbe:
            uthread.new(self.TryToHilight)
        if not self._isPicked:
            return 
        if lib.leftbtn:
            if self.sr.movingProbe:
                if alt:
                    self.ScaleProbesAroundCenter()
                else:
                    (x, y,) = (uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
                    self.MoveActiveProbe(x, y)
                    self.ShowGrid()
                return 
            if self.sr.rangeProbe:
                self.ScaleActiveProbe()
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
                return 
        if lib.leftbtn and not lib.rightbtn:
            fov = camera.fieldOfView
            camera.OrbitParent(-dx * fov * 0.1, dy * fov * 0.1)
            sm.GetService('systemmap').SortBubbles()
        elif lib.rightbtn and not lib.leftbtn:
            cameraParent = sm.GetService('camera').GetCameraParent('systemmap')
            if cameraParent.translationCurve:
                pos = cameraParent.translationCurve.GetVectorAt(blue.os.GetSimTime())
                cameraParent.translationCurve = None
                cameraParent.useCurves = 0
                cameraParent.translation = pos
            scalefactor = camera.translationFromParent.z * (camera.fieldOfView * 0.001)
            offset = trinity.TriVector(dx * scalefactor, -dy * scalefactor, 0.0)
            rot = camera.rotationAroundParent
            offset.TransformQuaternion(rot)
            cameraParent.translation -= offset
        elif lib.leftbtn and lib.rightbtn:
            camera.Dolly(-(dy * 0.01) * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z, source='systemmap')



    def OnMouseEnter(self, *args):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN



    def OnMouseDown(self, button):
        systemmap = sm.GetService('systemmap')
        self._isPicked = True
        uiutil.SetOrder(self, 0)
        systemmap.CollapseBubbles()
        systemmap.SortBubbles()
        sm.GetService('bracket').ResetOverlaps()
        scannerWnd = form.Scanner.GetIfOpen()
        (picktype, pickobject,) = self.GetPick()
        if uicore.uilib.leftbtn and pickobject:
            if pickobject.name[:6] == 'cursor':
                (cursorName, side, probeID,) = pickobject.name.split('_')
                if probeID:
                    probeID = int(probeID)
                    probe = scannerWnd.GetProbeSphere(probeID)
                    if probe:
                        cursorAxis = cursorName[6:]
                        x = uicore.ScaleDpi(uicore.uilib.x)
                        y = uicore.ScaleDpi(uicore.uilib.y)
                        self.PickAxis(x, y, probe, cursorAxis.lower())
                        if scannerWnd:
                            scannerWnd.HighlightProbeIntersections()
                        return 
        if scannerWnd and button == 0:
            pickedProbeControl = self.TryPickSphereBorder()
            if pickedProbeControl:
                self.sr.rangeProbe = pickedProbeControl
                pickedProbeControl.ShowScanRanges()
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
            else:
                uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)



    def OnMouseUp(self, button):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self._isPicked = False
        if button == 1:
            if uicore.uilib.leftbtn and (self.sr.movingProbe or self.sr.rangeProbe):
                scannerWnd = form.Scanner.GetIfOpen()
                if scannerWnd:
                    scannerWnd.CancelProbeMoveOrScaling()
                    if self.sr.movingProbe:
                        self.sr.movingProbe.ShowIntersection()
                    self.sr.movingProbe = None
                    self.sr.rangeProbe = None
                    scannerWnd.lastScaleUpdate = None
                    scannerWnd.lastMoveUpdate = None
            uthread.new(self.TryToHilight)
            uiutil.SetOrder(self, -1)
            return 
        uiutil.SetOrder(self, -1)
        scannerWnd = form.Scanner.GetIfOpen()
        if scannerWnd and self.sr.rangeProbe:
            uthread.new(scannerWnd.RegisterProbeRange, self.sr.rangeProbe)
        if scannerWnd and self.sr.movingProbe:
            uthread.new(scannerWnd.RegisterProbeMove, self.sr.movingProbe)
        self.sr.rangeProbe = None
        if self.sr.movingProbe:
            self.sr.movingProbe.ShowIntersection()
        self.sr.movingProbe = None
        if scannerWnd:
            scannerWnd.HideDistanceRings()
        uthread.new(self.TryToHilight)
        sm.GetService('systemmap').SortBubbles()
        sm.GetService('ui').ForceCursorUpdate()



    def OnMouseWheel(self, *args):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
        if camera.__typename__ == 'EveCamera':
            camera.Dolly(uicore.uilib.dz * 0.001 * abs(camera.translationFromParent.z))
            camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z, source='systemmap')
        return 1



    def ScaleProbesAroundCenter(self):
        (x, y,) = (uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
        mousePos = geo2.Vector(x, y, 0)
        probeData = sm.GetService('scanSvc').GetProbeData()
        scannerWnd = form.Scanner.GetIfOpen()
        if scannerWnd is None:
            return 
        probes = scannerWnd.GetProbeSpheres()
        probeScreenPoints = {}
        centroid = geo2.Vector(0, 0, 0)
        numProbes = 0
        for (probeID, probeControl,) in probes.iteritems():
            if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                continue
            probePos = probeControl.GetWorldPosition()
            centroid += probePos
            numProbes += 1

        if numProbes <= 1:
            return 
        centroid /= numProbes
        projectionParams = GetWorldToScreenParameters()
        centroidTansform = ((SYSTEMMAP_SCALE,
          0,
          0,
          0),
         (0,
          SYSTEMMAP_SCALE,
          0,
          0),
         (0,
          0,
          SYSTEMMAP_SCALE,
          0),
         (centroid.x,
          centroid.y,
          centroid.z,
          1.0))
        screenCentroid = geo2.Vector(*ProjectTransform(projectionParams, centroidTansform))
        screenCentroid.z = 0
        probeScreenPos = geo2.Vector(*ProjectTransform(projectionParams, self.sr.movingProbe.locator.worldTransform))
        probeScreenPos.z = 0
        centerToProbe = probeScreenPos - screenCentroid
        centerToProbeLength = geo2.Vec2Length(centerToProbe)
        if centerToProbeLength < 0.1:
            return 
        centerToProbeNormal = centerToProbe / centerToProbeLength
        toMouseDotProduct = geo2.Vec2Dot(mousePos - screenCentroid, centerToProbeNormal)
        projectedPos = screenCentroid + toMouseDotProduct * centerToProbeNormal
        toProjectedLength = geo2.Vec2Length(projectedPos - screenCentroid)
        if toProjectedLength < 0.1:
            return 
        moveScale = toProjectedLength / centerToProbeLength
        if toMouseDotProduct < 0:
            moveScale = -moveScale
        for (probeID, probeControl,) in probes.iteritems():
            if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                continue
            pos = probeControl.GetWorldPosition()
            toProbe = pos - centroid
            endPos = centroid + toProbe * moveScale
            endPos = (endPos.x / SYSTEMMAP_SCALE, endPos.y / SYSTEMMAP_SCALE, endPos.z / SYSTEMMAP_SCALE)
            probeControl.SetPosition(endPos)

        scannerWnd.ShowCentroidLines()
        scannerWnd.HighlightProbeIntersections()
        sm.GetService('systemmap').HighlightItemsWithinProbeRange()



    def GetMenu(self, *args):
        (picktype, pickobject,) = self.GetPick()
        if pickobject and pickobject.name[:6] == 'cursor':
            (cursorName, side, probeID,) = pickobject.name.split('_')
            if probeID:
                probeID = int(probeID)
                return sm.StartService('scanSvc').GetProbeMenu(probeID)
        return []



    def GetDotInCameraAlignedPlaneFromProbe(self, probeControl):
        (x, y,) = (uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
        (ray, start,) = GetRayAndPointFromScreen(x, y)
        camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
        viewDir = trinity.TriVector(0.0, 0.0, 1.0)
        viewDir.TransformQuaternion(camera.rotationAroundParent)
        viewDir.Normalize()
        targetPlaneNormal = geo2.Vector(viewDir.x, viewDir.y, viewDir.z)
        targetPlanePos = probeControl.GetWorldPosition()
        pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
        return pos



    def TryToHilight(self):
        if getattr(self, '_tryToHilight_Busy', None):
            self._tryToHilight_Pending = True
            return 
        if self.destroyed:
            return 
        self._tryToHilight_Busy = True
        (picktype, pickobject,) = self.GetPick()
        if pickobject and hasattr(pickobject, 'name') and pickobject.name[:6] == 'cursor':
            scannerWnd = form.Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.HiliteCursor(pickobject)
            self.HighlightBorderOfProbe()
            if uicore.uilib.mouseOver == self:
                uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)
        else:
            scannerWnd = form.Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.HiliteCursor()
            pickedProbeControl = self.TryPickSphereBorder()
            blue.pyos.synchro.SleepWallclock(100)
            if self.destroyed:
                return 
            _pickedProbeControl = self.TryPickSphereBorder()
            if _pickedProbeControl and _pickedProbeControl == pickedProbeControl:
                self.HighlightBorderOfProbe(pickedProbeControl)
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
            else:
                self.HighlightBorderOfProbe()
                if uicore.uilib.mouseOver == self:
                    uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)
        if self.destroyed:
            return 
        self._tryToHilight_Busy = False
        if getattr(self, '_tryToHilight_Pending', None):
            self._tryToHilight_Pending = False
            self.TryToHilight()



    def TryPickSphereBorder(self):
        matches = []
        scannerWnd = form.Scanner.GetIfOpen()
        if scannerWnd:
            (x, y,) = (uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
            (ray, start,) = GetRayAndPointFromScreen(x, y)
            (pickRadiusRay, pickRadiusStart,) = GetRayAndPointFromScreen(x - 30, y)
            camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
            viewDir = trinity.TriVector(0.0, 0.0, 1.0)
            viewDir.TransformQuaternion(camera.rotationAroundParent)
            viewDir.Normalize()
            targetPlaneNormal = geo2.Vector(viewDir.x, viewDir.y, viewDir.z)
            scanSvc = sm.StartService('scanSvc')
            probeData = scanSvc.GetProbeData()
            probes = scannerWnd.GetProbeSpheres()
            for (probeID, probeControl,) in probes.iteritems():
                if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                    continue
                targetPlanePos = geo2.Vector(probeControl.locator.worldTransform[3][0], probeControl.locator.worldTransform[3][1], probeControl.locator.worldTransform[3][2])
                rad = list(probeControl.sphere.scaling)[0] * SYSTEMMAP_SCALE
                pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
                picRadiusPos = RayToPlaneIntersection(pickRadiusStart, pickRadiusRay, targetPlanePos, targetPlaneNormal)
                pickRad = (trinity.TriVector(*picRadiusPos) - trinity.TriVector(*pos)).Length()
                diffFromPickToSphereBorder = (trinity.TriVector(*targetPlanePos) - trinity.TriVector(*pos)).Length()
                if rad + pickRad > diffFromPickToSphereBorder > rad - pickRad:
                    matches.append((abs(rad - diffFromPickToSphereBorder), probeControl))

        if matches:
            matches = uiutil.SortListOfTuples(matches)
            return matches[0]



    def HighlightBorderOfProbe(self, probeControl = None):
        scannerWnd = form.Scanner.GetIfOpen()
        if scannerWnd:
            probes = scannerWnd.GetProbeSpheres()
            for (_probeID, _probeControl,) in probes.iteritems():
                if probeControl and _probeControl == probeControl:
                    probeControl.HighlightBorder(True)
                else:
                    _probeControl.HighlightBorder(False)




    def _DiffProjectedPoint(self, ray, start):
        self.endPlanePos = RayToPlaneIntersection(start, ray, self.targetPlanePos, self.targetPlaneNormal)
        displacement = self.endPlanePos - self.startPlanePos
        self.startPlanePos = self.endPlanePos
        if self.activeManipAxis in ('xy', 'yz', 'xz'):
            finalDisplacement = displacement
        elif self.activeManipAxis == 'x':
            scaledDir = geo2.Vector(1.0, 0.0, 0.0)
        elif self.activeManipAxis == 'y':
            scaledDir = geo2.Vector(0.0, 1.0, 0.0)
        elif self.activeManipAxis == 'z':
            scaledDir = geo2.Vector(0.0, 0.0, 1.0)
        dot = geo2.Vec3Dot(displacement, scaledDir)
        scaledDir = geo2.Vec3Scale(scaledDir, dot)
        finalDisplacement = scaledDir
        return finalDisplacement



    def GetTranslation(self):
        return geo2.Vector(self.sr.movingProbe.locator.worldTransform[3][0], self.sr.movingProbe.locator.worldTransform[3][1], self.sr.movingProbe.locator.worldTransform[3][2])



    def PickAxis(self, x, y, pickobject, axis):
        (ray, start,) = GetRayAndPointFromScreen(x, y)
        self.sr.movingProbe = pickobject
        self.activeManipAxis = axis
        self.ShowGrid()
        self.targetPlaneNormal = self.GetTargetPlaneNormal(ray)
        self.targetPlanePos = self.GetTranslation()
        if self.targetPlaneNormal and pickobject:
            self.startPlanePos = RayToPlaneIntersection(start, ray, self.targetPlanePos, self.targetPlaneNormal)



    def ScaleActiveProbe(self, *args):
        if self.sr.rangeProbe:
            scannerWnd = form.Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.ScaleProbe(self.sr.rangeProbe, self.GetDotInCameraAlignedPlaneFromProbe(self.sr.rangeProbe))



    def MoveActiveProbe(self, x, y):
        if self.activeManipAxis and self.targetPlaneNormal and self.sr.movingProbe:
            (ray, start,) = GetRayAndPointFromScreen(x, y)
            diff = self._DiffProjectedPoint(ray, start)
            scannerWnd = form.Scanner.GetIfOpen()
            if scannerWnd:
                diff = geo2.Vector(*diff)
                diff *= 1.0 / SYSTEMMAP_SCALE
                scannerWnd.MoveProbe(self.sr.movingProbe, diff)
                scannerWnd.ShowCentroidLines()



    def GetTargetPlaneNormal(self, ray):
        if self.activeManipAxis in ('y',):
            camera = sm.GetService('sceneManager').GetRegisteredCamera('systemmap')
            cq = camera.rotationAroundParent.CopyTo()
            (y, p, r,) = geo2.QuaternionRotationGetYawPitchRoll((cq.x,
             cq.y,
             cq.z,
             cq.w))
            q = geo2.QuaternionRotationSetYawPitchRoll(y, 0.0, 0.0)
            return geo2.QuaternionTransformVector(q, (0.0, 0.0, 1.0))
        else:
            if self.activeManipAxis in ('x', 'z', 'xz'):
                return Y_AXIS
            if self.activeManipAxis in ('y', 'xy'):
                return Z_AXIS
            return X_AXIS



    def _OnClose(self):
        pass



    def ShowGrid(self):
        XZ = bool(self.activeManipAxis == 'xz')
        YZ = bool(self.activeManipAxis == 'yz')
        XY = bool(self.activeManipAxis == 'xy')
        if self.sr.movingProbe and (XZ or YZ or XY):
            scannerWnd = form.Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.ShowDistanceRings(self.sr.movingProbe, self.activeManipAxis)



    def GetPick(self):
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('systemmap')
        (x, y,) = (uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
        if scene2:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            pick = scene2.PickObject(x, y, projection, view, viewport)
            if pick:
                return ('scene', pick)
        return (None, None)




