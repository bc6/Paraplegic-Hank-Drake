import trinity
import sys
import math
import dungeonEditorToolGeometry
import geo2
import util
import uix
import uiconst
X_AXIS = geo2.Vector(1.0, 0.0, 0.0)
Y_AXIS = geo2.Vector(0.0, 1.0, 0.0)
Z_AXIS = geo2.Vector(0.0, 0.0, 1.0)
CHANGE_NONE = 0L
CHANGE_TRANSLATION = 1L
CHANGE_ROTATION = 2L
CHANGE_SCALE = 4L

def GetRayAndPointFromScreen(x, y):
    (proj, view, vp,) = uix.GetFullscreenProjectionViewAndViewport()
    (ray, start,) = trinity.device.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
    ray = geo2.Vector(ray.x, ray.y, ray.z)
    start = geo2.Vector(start.x, start.y, start.z)
    return (ray, start)



def RayToPlaneIntersection(P, d, Q, n):
    denom = geo2.Vec3Dot(n, d)
    if abs(denom) < 1e-05:
        return P
    else:
        distance = -geo2.Vec3Dot(Q, n)
        t = -(geo2.Vec3Dot(n, P) + distance) / denom
        scaledRay = geo2.Scale(d, t)
        ret = geo2.Add(scaledRay, P)
        return geo2.Vector(*ret)



def ProjectPointTowardsFrontPlane(point, dist = 7.0):
    ppos = point
    viewMat = trinity.GetViewTransform()
    cpos = geo2.Vector(*trinity.GetViewPosition())
    dir = geo2.Vec3Normalize(geo2.Subtract(cpos, ppos))
    lookat = geo2.Vector(viewMat[0][2], viewMat[1][2], viewMat[2][2])
    point = cpos + lookat * dist
    return RayToPlaneIntersection(ppos, dir, point, lookat)



def CameraFacingMatrix(objtransform):
    viewMat = trinity.GetViewTransform()
    objInv = geo2.MatrixInverse(objtransform)
    viewInv = geo2.MatrixInverse(viewMat)
    viewInv = geo2.MatrixMultiply(viewInv, objInv)
    rmat = geo2.MatrixRotationX(math.pi * 0.5)
    rmat = geo2.MatrixMultiply(rmat, viewInv)
    rmat = (rmat[0],
     rmat[1],
     rmat[2],
     (0.0,
      0.0,
      0.0,
      rmat[3][3]))
    return rmat



class BaseTool():

    def __init__(self, geometry, view, projection):
        self.geometry = geometry
        self.view = view
        self.projection = projection
        self.display = True
        self.worldTranslation = geo2.MatrixIdentity()
        self.frontPlaneTranslation = geo2.MatrixIdentity()



    def ApplyTransform(self):
        pass



    def onActivated(self):
        pass



    def Render(self):
        if self.display:
            viewTrans = trinity.GetViewTransform()
            view = geo2.Vector(viewTrans[0][2], viewTrans[1][2], viewTrans[2][2])
            localpos = self.GetTranslation()
            campos = geo2.Vector(*trinity.GetViewPosition())
            vec = localpos - campos
            vec = geo2.Vec3Normalize(vec)
            if geo2.Vec3Dot(vec, view) > 0.0:
                mat = self.GetTargetPlaneProjectionMatrix()
                areas = self.geometry.Update(mat)
                self.geometry.Render(self.Cull(areas))



    def Cull(self, areas):
        return areas



    def GetTargetPlaneProjectionMatrix(self):
        trans = self.GetTranslation()
        adjusted_translation = ProjectPointTowardsFrontPlane(trans)
        mat = self.worldTranslation
        rmat = geo2.MatrixRotationQuaternion(self.GetRotation())
        rmat = geo2.MatrixTranspose(rmat)
        mat = geo2.MatrixTranslation(adjusted_translation.x, adjusted_translation.y, adjusted_translation.z)
        self.frontPlaneTranslation = geo2.MatrixMultiply(rmat, mat)
        return self.frontPlaneTranslation



    def Show(self):
        self.transformed = False
        areas = self.geometry.areas
        for each in areas:
            each.display = True

        self.display = True



    def Hide(self):
        self.display = False
        areas = self.geometry.areas
        for each in areas:
            each.display = False




    def IsShown(self):
        return self.display



    def UpdatePrimitives(self):
        self.geometry.Update(self.worldTranslation)
        self._InternalUpdate()



    def Translate(self, trans):
        self.worldTranslation = list(self.worldTranslation)
        self.worldTranslation[3] = (trans.x,
         trans.y,
         trans.z,
         self.worldTranslation[3][3])



    def GetTranslation(self):
        return geo2.Vector(self.worldTranslation[3][0], self.worldTranslation[3][1], self.worldTranslation[3][2])



    def Rotate(self, rot):
        self.worldTranslation = geo2.MatrixRotationQuaternion(rot)



    def GetRotation(self):
        (scale, rotation, translation,) = geo2.MatrixDecompose(self.worldTranslation)
        rotation = geo2.QuaternionInverse(rotation)
        return rotation



    def Scale(self, scale):
        pass



    def GetScale(self):
        (scale, rotation, translation,) = geo2.MatrixDecompose(self.worldTranslation)
        return scale



    def GetUpVec(self):
        transForm = self.worldTranslation
        return geo2.Vector(transForm[1][0], transForm[1][1], transForm[1][2])



    def GetFrontVec(self):
        transForm = self.worldTranslation
        v = geo2.Vector(transForm[2][0], transForm[2][1], transForm[2][2])
        return v



    def GetRightVec(self):
        transForm = self.worldTranslation
        v = geo2.Vector(transForm[0][0], transForm[0][1], transForm[0][2])
        return v



    def _InternalUpdate(self):
        pass




class TransformationTool(BaseTool):

    def __init__(self, view, projection, primitiveScene):
        self.primitiveScene = primitiveScene
        BaseTool.__init__(self, self.GenGeometry(), view, projection)
        self.originalLocation = {'x': geo2.Vector(0.0, 0.0, 0.0),
         'y': geo2.Vector(0.0, 0.0, 0.0),
         'z': geo2.Vector(0.0, 0.0, 0.0),
         'w': geo2.Vector(0.0, 0.0, 0.0)}
        self.activeManipAxis = None
        self.targetPlaneNormal = None
        self.captured = False
        self.SetDefaultColors()
        self.preX = 0
        self.preY = 0
        self.curX = 0
        self.curY = 0
        self.invalidAxes = []



    def InvalidateAxes(self, axisList):
        for axis in axisList:
            if axis not in self.invalidAxes:
                self.invalidAxes.append(axis)
                self.HideAxis(axis)




    def ValidateAxes(self, axisList):
        for axis in axisList:
            if axis in self.invalidAxes:
                self.invalidAxes.remove(axis)
                self.ShowAxis(axis)




    def ValidateAllAxes(self):
        self.ValidateAxes(['x',
         'y',
         'z',
         'w',
         'ww'])



    def PickPrimitiveScene(self, x, y):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        view = trinity.TriView()
        view.transform = ((camera.view._11,
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
        proj = trinity.TriProjection()
        p = ((camera.projection._11,
          camera.projection._12,
          camera.projection._13,
          camera.projection._14),
         (camera.projection._21,
          camera.projection._22,
          camera.projection._23,
          camera.projection._24),
         (camera.projection._31,
          camera.projection._32,
          camera.projection._33,
          camera.projection._34),
         (camera.projection._41,
          camera.projection._42,
          camera.projection._43,
          camera.projection._44))
        proj.CustomProjection(p)
        res = self.primitiveScene.PickObject(x, y, proj, view, trinity.device.viewport)
        if res and res.name in self.PickableAxis():
            return res.name
        else:
            return None



    def PickableAxis(self):
        return ['x',
         'y',
         'z',
         'w',
         'ww']



    def PickAxis(self, x, y, pointOnPlane):
        (ray, start,) = GetRayAndPointFromScreen(x, y)
        axis = self.PickPrimitiveScene(x, y)
        self.SetDefaultColors()
        if axis:
            self.activeManipAxis = axis
            self.ColorActiveAxis()
            self.targetPlaneNormal = self.GetDesiredPlaneNormal(ray)
            if self.targetPlaneNormal:
                self.startPlanePos = RayToPlaneIntersection(start, ray, self.GetTranslation(), self.targetPlaneNormal)
            self.CaptureAxis()
        return axis



    def SetDefaultColors(self):
        for each in self.geometry.areas:
            if each.name == 'x':
                each.SetColor(dungeonEditorToolGeometry.RED)
            elif each.name == 'y':
                each.SetColor(dungeonEditorToolGeometry.GREEN)
            elif each.name == 'z':
                each.SetColor(dungeonEditorToolGeometry.BLUE)
            elif each.name == 'w':
                each.SetColor(dungeonEditorToolGeometry.CYAN)




    def ColorComponent(self, name, color):
        for each in self.geometry.areas:
            if each.name == name:
                each.SetColor(color)




    def ColorActiveAxis(self):
        self.ColorComponent(self.activeManipAxis, dungeonEditorToolGeometry.YELLOW)



    def CaptureAxis(self):
        for each in self.geometry.areas:
            if each.name == self.activeManipAxis:
                each.display = True

        self.captured = True



    def ReleaseAxis(self):
        self.ShowAllAxis()
        for axis in self.invalidAxes:
            self.HideAxis(axis)

        self.SetDefaultColors()
        self.activeManipAxis = None
        self.targetPlaneNormal = None
        self.captured = False



    def ShowAllAxis(self):
        for each in self.geometry.areas:
            each.display = True




    def HideAllAxis(self):
        for each in self.geometry.areas:
            each.display = False




    def HideAxis(self, name):
        for each in self.geometry.areas:
            if each.name == name:
                each.display = False




    def ShowAxis(self, name):
        for each in self.geometry.areas:
            if each.name == name:
                each.display = True




    def Transform(self, x, y):
        self.curX = x
        self.curY = y
        if self.activeManipAxis:
            dev = trinity.GetDevice()
            (ray, start,) = GetRayAndPointFromScreen(x, y)
            if self.targetPlaneNormal:
                diff = self._DiffProjectedPoint(ray, start)
                self._TransformContext(self._TransformAxis(diff))
        self.preX = x
        self.preY = y



    def GetDesiredPlaneNormal(self, ray):
        x_axis = X_AXIS
        y_axis = Y_AXIS
        z_axis = Z_AXIS
        if self.activeManipAxis:
            if self.activeManipAxis == 'x':
                ydot = abs(geo2.Vec3Dot(ray, y_axis))
                zdot = abs(geo2.Vec3Dot(ray, z_axis))
                if zdot > ydot:
                    return z_axis
                if ydot > zdot:
                    return y_axis
            elif self.activeManipAxis == 'y':
                zdot = abs(geo2.Vec3Dot(ray, z_axis))
                xdot = abs(geo2.Vec3Dot(ray, x_axis))
                if zdot > xdot:
                    return z_axis
                if xdot > zdot:
                    return x_axis
            elif self.activeManipAxis == 'z':
                xdot = abs(geo2.Vec3Dot(ray, x_axis))
                ydot = abs(geo2.Vec3Dot(ray, y_axis))
                if xdot > ydot:
                    return x_axis
                if ydot > xdot:
                    return y_axis
            else:
                viewMat = trinity.GetViewTransform()
                return geo2.Vector(viewMat[0][2], viewMat[1][2], viewMat[2][2])
        else:
            return None



    def _DiffProjectedPoint(self, ray, start):
        self.endPlanePos = RayToPlaneIntersection(start, ray, self.GetTranslation(), self.targetPlaneNormal)
        displacement = self.endPlanePos - self.startPlanePos
        self.startPlanePos = self.endPlanePos
        if self.activeManipAxis == 'w':
            finalDisplacement = displacement
        elif self.activeManipAxis == 'x':
            dir = self.GetRightVec()
        elif self.activeManipAxis == 'y':
            dir = self.GetUpVec()
        elif self.activeManipAxis == 'z':
            dir = self.GetFrontVec()
        dir = geo2.Vec3Normalize(dir)
        scaledDir = geo2.Vec3Scale(dir, geo2.Vec3Dot(displacement, dir))
        finalDisplacement = scaledDir
        return finalDisplacement



    def _TransformContext(self, v):
        pass



    def _TransformAxis(self, v):
        if self.activeManipAxis != 'w':
            ret = geo2.Vector(*v)
            worldTransInv = geo2.MatrixInverse(self.worldTranslation)
            v = geo2.Vec3TransformNormal(v, worldTransInv)
            t = self.GetTranslation()
            self.Translate(t + v)
            return ret
        return v




class TranslationTool(TransformationTool):

    def __init__(self, view, projection, primitiveScene):
        self.cones = []
        self.axes = []
        TransformationTool.__init__(self, view, projection, primitiveScene)
        self.action = None



    def GenGeometry(self):
        rotateMat = geo2.MatrixRotationZ(-math.pi / 2.0)
        transform = geo2.MatrixTranslation(0.0, 1.0, 0.0)
        transform = geo2.MatrixMultiply(transform, rotateMat)
        c_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CONE_TRIS, transform)
        xTransAreaCone = dungeonEditorToolGeometry.area('x', dungeonEditorToolGeometry.RED)
        xTransAreaCone.AddToSolidSet(c_tris)
        xTransAreaAxis = dungeonEditorToolGeometry.area('x', dungeonEditorToolGeometry.RED)
        xTransAreaAxis.AddToLineSet([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])
        t = dungeonEditorToolGeometry.GetSolidAroundLine([(0.3, 0.0, 0.0), (1.0, 0.0, 0.0)], 0.08)
        xTransAreaAxis.AddToPickingSet(t)
        transform = geo2.MatrixTranslation(0.0, 1.0, 0.0)
        c_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CONE_TRIS, transform)
        yTransAreaCone = dungeonEditorToolGeometry.area('y', dungeonEditorToolGeometry.GREEN)
        yTransAreaCone.AddToSolidSet(c_tris)
        yTransAreaAxis = dungeonEditorToolGeometry.area('y', dungeonEditorToolGeometry.GREEN)
        yTransAreaAxis.AddToLineSet([(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)])
        t = dungeonEditorToolGeometry.GetSolidAroundLine([(0.0, 0.3, 0.0), (0.0, 1.0, 0.0)], 0.08)
        yTransAreaAxis.AddToPickingSet(t)
        transform = geo2.MatrixTranslation(0.0, 1.0, 0.0)
        rotateMat = geo2.MatrixRotationX(math.pi / 2.0)
        transform = geo2.MatrixMultiply(transform, rotateMat)
        c_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CONE_TRIS, transform)
        zTransAreaCone = dungeonEditorToolGeometry.area('z', dungeonEditorToolGeometry.BLUE)
        zTransAreaCone.AddToSolidSet(c_tris)
        zTransAreaAxis = dungeonEditorToolGeometry.area('z', dungeonEditorToolGeometry.BLUE)
        zTransAreaAxis.AddToLineSet([(0.0, 0.0, 0.0), (0.0, 0.0, 1.0)])
        t = dungeonEditorToolGeometry.GetSolidAroundLine([(0.0, 0.0, 0.3), (0.0, 0.0, 1.0)], 0.08)
        zTransAreaAxis.AddToPickingSet(t)
        wTransAreaPlane = dungeonEditorToolGeometry.area('w', dungeonEditorToolGeometry.CYAN)
        wTransAreaPlane.AddToLineSet(dungeonEditorToolGeometry.CIRCLE_POINTS_QUART)
        wTransAreaPlane._lineset.viewOriented = True
        picking_tris = dungeonEditorToolGeometry.GenCircleTriangles(0.25)
        if not trinity.IsRightHanded():
            picking_tris.reverse()
        wTransAreaPlane.AddToPickingSet(picking_tris)
        translationGeo = dungeonEditorToolGeometry.geometry(self.primitiveScene)
        translationGeo.AppendArea(wTransAreaPlane)
        translationGeo.AppendArea(xTransAreaCone)
        translationGeo.AppendArea(xTransAreaAxis)
        translationGeo.AppendArea(yTransAreaCone)
        translationGeo.AppendArea(yTransAreaAxis)
        translationGeo.AppendArea(zTransAreaCone)
        translationGeo.AppendArea(zTransAreaAxis)
        self.cones.append(xTransAreaCone)
        self.cones.append(yTransAreaCone)
        self.cones.append(zTransAreaCone)
        self.axes.append(xTransAreaAxis)
        self.axes.append(yTransAreaAxis)
        self.axes.append(zTransAreaAxis)
        return translationGeo



    def Render(self):
        if self.display:
            self.ApplyTransform()
            mat = CameraFacingMatrix(self.worldTranslation)
            area = self.geometry.GetArea('w')
            area.localTransform = mat
            TransformationTool.Render(self)



    def _TransformContext(self, v):
        scenarioSvc = sm.StartService('scenario')
        michelleSvc = sm.StartService('michelle')
        for slimItem in scenarioSvc.GetSelObjects():
            if slimItem.dunObjectID in scenarioSvc.GetLockedObjects():
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    scenarioSvc.UnlockObject(slimItem.itemID, slimItem.dunObjectID, force=True)
                else:
                    continue
            targetBall = michelleSvc.GetBall(slimItem.itemID)
            targetModel = getattr(targetBall, 'model', None)
            if targetModel:
                targetModel.translationCurve.x += v.x
                targetModel.translationCurve.y += v.y
                targetModel.translationCurve.z += v.z
            else:
                try:
                    targetTransform = scenarioSvc.fakeTransforms[slimItem.itemID]
                    targetTransform.translationCurve.x += v.x
                    targetTransform.translationCurve.y += v.y
                    targetTransform.translationCurve.z += v.z
                except KeyError:
                    scenarioSvc.LogError('Unable to translate any ball for dungeon object:', slimItem.dunObjectID)
            slimItem.dunX += v.x
            slimItem.dunY += v.y
            slimItem.dunZ += v.z
            scenarioSvc.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_TRANSLATION)




    def _InternalUpdate(self):
        mat = CameraFacingMatrix(self.worldTranslation)
        area = self.geometry.GetArea('w')
        area.localTransform = mat




class ScalingTool(TransformationTool):

    def __init__(self, view, projection, primitiveScene):
        TransformationTool.__init__(self, view, projection, primitiveScene)
        self.preLength = 1.0
        self.action = None
        self.state = None
        self.initial_scaling = {}
        self.initial_position = {}
        self.targetPos = None
        self.scale = geo2.Vector(1.0, 1.0, 1.0)
        self.startPos = None
        self.startScreenX = 0
        self.toolPosition = None



    def GenGeometry(self):
        scalingGeo = dungeonEditorToolGeometry.geometry(self.primitiveScene)
        wBox = dungeonEditorToolGeometry.area('w', dungeonEditorToolGeometry.CYAN)
        wBox.AddToSolidSet(dungeonEditorToolGeometry.CUBE_TRIS)
        xBox = dungeonEditorToolGeometry.area('x', dungeonEditorToolGeometry.RED)
        transform = geo2.MatrixTranslation(1.0, 0.0, 0.0)
        x_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CUBE_TRIS, transform)
        xBox.AddToSolidSet(x_tris)
        xBox.AddToLineSet(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        transform = geo2.MatrixTranslation(0.0, 1.0, 0.0)
        y_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CUBE_TRIS, transform)
        yBox = dungeonEditorToolGeometry.area('y', dungeonEditorToolGeometry.GREEN)
        yBox.AddToSolidSet(y_tris)
        yBox.AddToLineSet(((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        transform = geo2.MatrixTranslation(0.0, 0.0, 1.0)
        z_tris = geo2.Vec3TransformCoordArray(dungeonEditorToolGeometry.CUBE_TRIS, transform)
        zBox = dungeonEditorToolGeometry.area('z', dungeonEditorToolGeometry.BLUE)
        zBox.AddToSolidSet(z_tris)
        zBox.AddToLineSet(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))
        scalingGeo.AppendArea(xBox)
        scalingGeo.AppendArea(yBox)
        scalingGeo.AppendArea(zBox)
        scalingGeo.AppendArea(wBox)
        return scalingGeo



    def GetInitialScaling(self):
        self.axis = {'x': self.GetRightVec(),
         'y': self.GetUpVec(),
         'z': self.GetFrontVec()}
        maxScale = 0.0
        for slimItem in sm.GetService('scenario').GetSelObjects():
            targetBall = sm.GetService('michelle').GetBall(slimItem.itemID)
            targetModel = getattr(targetBall, 'model', None)
            if not targetModel:
                return 
            if hasattr(targetModel, 'scaling'):
                maxScale = max(maxScale, targetModel.scaling.x)

        geo2.Vector(maxScale, maxScale, maxScale)



    def Render(self):
        if self.display:
            self.ApplyTransform()
            if not self.state:
                self.GetInitialScaling()
                self.state = 'start'
            if self.activeManipAxis:
                if self.activeManipAxis == 'w':
                    scale = self.scale.x
                else:
                    scale = getattr(self.scale, self.activeManipAxis)
            else:
                scale = 1.0
            axisLines = trinity.TriLineSet()
            axisLines.zEnable = False
            axisLines.SetDefaultColor(4286611584L)
            pos = self.GetTranslation()
            pos = ProjectPointTowardsFrontPlane(pos)
            right = self.GetRightVec()
            up = self.GetUpVec()
            front = self.GetFrontVec()
            xoffset = right * scale
            yoffset = up * scale
            zoffset = front * scale
            area = self.geometry.GetArea('x')
            area.localTransform = list(area.localTransform)
            area.localTransform[3] = (scale,
             0.0,
             0.0,
             area.localTransform[3][3])
            area = self.geometry.GetArea('y')
            area.localTransform = list(area.localTransform)
            area.localTransform[3] = (0.0,
             scale,
             0.0,
             area.localTransform[3][3])
            area = self.geometry.GetArea('z')
            area.localTransform = list(area.localTransform)
            area.localTransform[3] = (0.0,
             0.0,
             scale,
             area.localTransform[3][3])
            axisLines.AddLines([pos,
             pos + xoffset,
             pos,
             pos + yoffset,
             pos,
             pos + zoffset])
            axisLines.Render()
            TransformationTool.Render(self)



    def CaptureAxis(self):
        self.scale = geo2.Vector(1.0, 1.0, 1.0)
        self.startScreenX = self.curX
        self.toolPosition = sm.GetService('scenario').GetSelectionCenter()



    def ReleaseAxis(self):
        TransformationTool.ReleaseAxis(self)
        self.state = None
        self.targetPos = None
        self.startPos = None
        self.initial_scaling = {}
        self.initial_position = {}
        self.toolPosition = None
        for slimItem in sm.GetService('scenario').GetSelObjects():
            slimItem.initialRadius = None




    def _TransformContext(self, v):
        scenarioMgr = sm.StartService('scenario')
        michelleSvc = sm.StartService('michelle')
        dungeonOrigin = scenarioMgr.GetDungeonOrigin()
        (toolPositionX, toolPositionY, toolPositionZ,) = sm.GetService('scenario').GetSelectionCenter()
        toolOffset = (self.toolPosition[0] - dungeonOrigin.x, self.toolPosition[1] - dungeonOrigin.y, self.toolPosition[2] - dungeonOrigin.z)
        slimItems = scenarioMgr.GetSelObjects()
        for slimItem in slimItems:
            if slimItem.dunObjectID in sm.GetService('scenario').GetLockedObjects():
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    scenarioMgr.UnlockObject(slimItem.itemID, slimItem.dunObjectID, force=True)
                else:
                    continue
            targetBall = michelleSvc.GetBall(slimItem.itemID)
            targetModel = getattr(targetBall, 'model', None)
            if not targetModel:
                continue
            if slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud) and hasattr(targetModel, 'scaling'):
                if slimItem.itemID not in self.initial_scaling:
                    self.initial_scaling[slimItem.itemID] = trinity.TriVector(targetModel.scaling.x, targetModel.scaling.y, targetModel.scaling.z)
                initialScaling = self.initial_scaling[slimItem.itemID]
                scaleVector = trinity.TriVector(initialScaling.x * self.scale.x, initialScaling.y * self.scale.y, initialScaling.z * self.scale.z)
                targetModel.scaling = scaleVector
                slimItem.dunRadius = util.ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, targetModel.scaling.x / 2.0)
                scenarioMgr.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_SCALE)
            elif slimItem.categoryID == const.categoryAsteroid and hasattr(targetModel, 'modelScale'):
                if slimItem.itemID not in self.initial_scaling:
                    self.initial_scaling[slimItem.itemID] = targetModel.modelScale
                targetModel.modelScale = self.initial_scaling[slimItem.itemID] * self.scale.x
                slimItem.dunRadius = util.ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, targetModel.modelScale)
                scenarioMgr.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_SCALE)
            if len(slimItems) > 1 and not uicore.uilib.Key(uiconst.VK_SHIFT):
                if slimItem.itemID not in self.initial_position:
                    self.initial_position[slimItem.itemID] = ((targetModel.translationCurve.x, targetModel.translationCurve.y, targetModel.translationCurve.z), (slimItem.dunX, slimItem.dunY, slimItem.dunZ))
                (initialWorldPosition, initialDungeonPosition,) = self.initial_position[slimItem.itemID]
                relativeObjectPosition = trinity.TriVector(initialDungeonPosition[0] - toolOffset[0], initialDungeonPosition[1] - toolOffset[1], initialDungeonPosition[2] - toolOffset[2])
                scaledPosition = trinity.TriVector(relativeObjectPosition.x * self.scale.x, relativeObjectPosition.y * self.scale.y, relativeObjectPosition.z * self.scale.z)
                targetModel.translationCurve.x = scaledPosition.x + self.toolPosition[0]
                targetModel.translationCurve.y = scaledPosition.y + self.toolPosition[1]
                targetModel.translationCurve.z = scaledPosition.z + self.toolPosition[2]
                slimItem.dunX = scaledPosition.x + toolOffset[0]
                slimItem.dunY = scaledPosition.y + toolOffset[1]
                slimItem.dunZ = scaledPosition.z + toolOffset[2]
                scenarioMgr.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_TRANSLATION)




    def _TransformAxis(self, v):
        dev = trinity.GetDevice()
        pos = self.GetTranslation()
        if self.activeManipAxis == 'w':
            self.targetPos = pos - self.endPlanePos
            scale = abs(1.0 + float(self.curX - self.startScreenX) / dev.width * 4.0)
            self.scale = geo2.Vector(scale, scale, scale)
        else:
            dir = self.axis[self.activeManipAxis]
            self.targetPos = geo2.Vec3Scale(dir, geo2.Vec3Dot(pos - self.endPlanePos, dir))
            if not self.startPos:
                self.startPos = self.targetPos
            start_len = geo2.Vec3Length(self.startPos)
            current_len = geo2.Vec3Length(self.targetPos)
            scale = current_len / start_len
            if geo2.Vec3Dot(self.startPos, self.targetPos) < 0:
                scale = -scale
            scale = abs(scale)
            self.scale = geo2.Vector(scale, scale, scale)
        return v



    def _InternalUpdate(self):
        if not self.state:
            self.GetInitialScaling()
            self.state = 'start'
        if self.activeManipAxis:
            if self.activeManipAxis == 'w':
                scale = self.scale.x
            else:
                scale = getattr(self.scale, self.activeManipAxis)
        else:
            scale = 1.0




class RotationTool(TransformationTool):

    def __init__(self, view, projection, primitiveScene):
        TransformationTool.__init__(self, view, projection, primitiveScene)
        self.action = None
        self.axis = {'x': X_AXIS,
         'y': Y_AXIS,
         'z': Z_AXIS}
        self.axisCulling = True
        self.lastRotation = geo2.QuaternionIdentity()



    def SetAxisCulling(self, state):
        self.axisCulling = state



    def GenGeometry(self):
        xCircleAreas = []
        yCircleAreas = []
        zCircleAreas = []
        if not trinity.IsRightHanded():
            effectPath = 'res:/Graphics/Effect/Managed/Utility/LinesRotationToolLH.fx'
        else:
            effectPath = 'res:/Graphics/Effect/Managed/Utility/LinesRotationTool.fx'
        unit_circle = dungeonEditorToolGeometry.GenCirclePoints(1.0, 60)
        mat = geo2.MatrixRotationY(math.pi / 2)
        x_circle = geo2.Vec3TransformCoordArray(unit_circle, mat)
        xRotationHandleCircle = dungeonEditorToolGeometry.area('x', dungeonEditorToolGeometry.RED)
        xRotationHandleCircle.AddToLineSet(x_circle, True)
        xRotationHandleCircle._lineset.effect.effectFilePath = effectPath
        mat = geo2.MatrixRotationX(math.pi / 2)
        y_circle = geo2.Vec3TransformCoordArray(unit_circle, mat)
        yRotationHandleCircle = dungeonEditorToolGeometry.area('y', dungeonEditorToolGeometry.GREEN)
        yRotationHandleCircle.AddToLineSet(y_circle, True)
        yRotationHandleCircle._lineset.effect.effectFilePath = effectPath
        zRotationHandleCircle = dungeonEditorToolGeometry.area('z', dungeonEditorToolGeometry.BLUE)
        zRotationHandleCircle.AddToLineSet(unit_circle, True)
        zRotationHandleCircle._lineset.effect.effectFilePath = effectPath
        w_circle = dungeonEditorToolGeometry.GenCirclePoints(1.2, 60)
        wArea = dungeonEditorToolGeometry.area('w', dungeonEditorToolGeometry.CYAN)
        wArea.AddToLineSet(w_circle, True)
        wArea._lineset.viewOriented = True
        wwArea = dungeonEditorToolGeometry.area('ww', dungeonEditorToolGeometry.LIGHT_GRAY)
        wwArea.AddToLineSet(dungeonEditorToolGeometry.GenCirclePoints(1.0, 60))
        wwArea._lineset.viewOriented = True
        picking_tris = dungeonEditorToolGeometry.GenCircleTriangles(1.0, 60)
        if not trinity.IsRightHanded():
            picking_tris.reverse()
        wwArea.AddToPickingSet(picking_tris)
        rotationGeo = dungeonEditorToolGeometry.geometry(self.primitiveScene)
        rotationGeo.AppendArea(xRotationHandleCircle)
        rotationGeo.AppendArea(yRotationHandleCircle)
        rotationGeo.AppendArea(zRotationHandleCircle)
        rotationGeo.AppendArea(wArea)
        rotationGeo.AppendArea(wwArea)
        return rotationGeo



    def ColorActiveAxis(self):
        if self.activeManipAxis != 'ww':
            TransformationTool.ColorActiveAxis(self)



    def Render(self):
        if self.display:
            self.ApplyTransform()
            mat = CameraFacingMatrix(self.worldTranslation)
            warea = self.geometry.GetArea('w')
            wwarea = self.geometry.GetArea('ww')
            warea.localTransform = mat
            wwarea.localTransform = mat
            TransformationTool.Render(self)



    def Cull(self, areas):
        pos = geo2.Vector(self.frontPlaneTranslation[3][0], self.frontPlaneTranslation[3][1], self.frontPlaneTranslation[3][2])
        viewMat = trinity.GetViewTransform()
        lookat = geo2.Vector(-viewMat[0][2], -viewMat[1][2], -viewMat[2][2])
        x_area = dungeonEditorToolGeometry.area('x', 4294771202L)
        y_area = dungeonEditorToolGeometry.area('y', 4278385922L)
        z_area = dungeonEditorToolGeometry.area('z', 4278321917L)
        x_lines = []
        y_lines = []
        z_lines = []
        for each in iter(areas):
            name = each.name
            if name not in ('x', 'y', 'z'):
                continue
            b = pos - (each.bounds.updated_center - lookat * each.bounds.radius)
            if geo2.Vec3Dot(geo2.Vec3Normalize(b), lookat) < 0.0 or not self.axisCulling:
                if name == 'x':
                    x_area.SetColor(each.GetColor())
                    x_area.lineset.transform = each.lineset.transform
                    x_lines.extend(each.lines)
                elif name == 'y':
                    y_area.SetColor(each.GetColor())
                    y_area.lineset.transform = each.lineset.transform
                    y_lines.extend(each.lines)
                elif name == 'z':
                    z_area.SetColor(each.GetColor())
                    z_area.lineset.transform = each.lineset.transform
                    z_lines.extend(each.lines)
                self.geometry.visible_areas.append(each)

        x_area.AddToLineSet(x_lines)
        x_area.lineset.zEnable = False
        y_area.AddToLineSet(y_lines)
        y_area.lineset.zEnable = False
        z_area.AddToLineSet(z_lines)
        z_area.lineset.zEnable = False
        return [x_area,
         y_area,
         z_area,
         self.geometry.GetArea('w'),
         self.geometry.GetArea('ww')]



    def _Hemisphere(self, x, y):
        dev = trinity.GetDevice()
        center = geo2.Vector(self.frontPlaneTranslation[3][0], self.frontPlaneTranslation[3][1], self.frontPlaneTranslation[3][2])
        view = trinity.GetViewTransform()
        proj = trinity.GetProjectionTransform()
        side = center - geo2.Vector(view[0][0], view[1][0], view[2][0])
        center = geo2.Vec3TransformCoord(center, view)
        center = geo2.Vec3TransformCoord(center, proj)
        center = geo2.Vector(*center)
        side = geo2.Vec3TransformCoord(side, view)
        side = geo2.Vec3TransformCoord(side, proj)
        side = geo2.Vector(*side)
        side.x += 1.0
        side.y += 1.0
        center.x += 1.0
        center.y += 1.0
        dim = abs(dev.width * (side.x - center.x)) * 0.5
        screenx = int((dev.width - 1) * 0.5 * center.x)
        screeny = dev.height - int((dev.height - 1) * 0.5 * center.y)
        px = float(x - screenx) / float(dim)
        py = float(screeny - y) / float(dim)
        d = math.sqrt(px * px + py * py)
        if d > 1.0:
            a = 1.0 / d
            vec = geo2.Vector(px * a, py * a, 0.0)
        else:
            vec = geo2.Vector(px, py, -(1.0 - d))
        return geo2.Vec3Normalize(vec)



    def _TransformAxis(self, v):
        viewMat = trinity.GetViewTransform()
        viewVec = geo2.Vector(viewMat[0][2], viewMat[1][2], viewMat[2][2])
        pos = self.GetTranslation()
        start = self.startPlanePos - pos
        start = geo2.Vec3Normalize(start)
        end = self.endPlanePos - pos
        end = geo2.Vec3Normalize(end)
        q = geo2.QuaternionIdentity()
        dot = geo2.Vec3Dot(start, end)
        if 1.0 - dot < 1e-05:
            return q
        dnormal = geo2.Vec3Cross(start, end)
        if self.activeManipAxis == 'w':
            worldInv = geo2.MatrixInverse(self.worldTranslation)
            axis = geo2.Vec3TransformNormal(viewVec, worldInv)
            axis = geo2.Vector(*axis)
            rdot = geo2.Vec3Dot(axis, viewVec)
            ddot = geo2.Vec3Dot(dnormal, axis)
            if ddot < 0.0 and rdot > 0.0:
                axis = -axis
            elif ddot > 0.0 and rdot < 0.0:
                axis = -axis
        elif self.activeManipAxis == 'ww':
            curP = self._Hemisphere(self.curX, self.curY)
            preP = self._Hemisphere(self.preX, self.preY)
            viewInverse = geo2.MatrixInverse(viewMat)
            norm = geo2.Vec3Cross(preP, curP)
            worldInv = geo2.MatrixInverse(self.worldTranslation)
            axis = geo2.Vec3TransformNormal(norm, worldInv)
            axis = geo2.Vec3TransformNormal(axis, viewInverse)
            dot = geo2.Vec3Dot(curP, preP)
        else:
            axis = self.axis[self.activeManipAxis]
            if geo2.Vec3Dot(dnormal, axis) < 0.0:
                axis = -axis
            if self.activeManipAxis == 'x' and self.worldTranslation[0][0] < 0.0 or self.activeManipAxis == 'y' and self.worldTranslation[1][1] < 0.0 or self.activeManipAxis == 'z' and self.worldTranslation[2][2] < 0.0:
                axis = -axis
        self.startPlanePos = self.endPlanePos
        if dot < -1:
            dot = -1
        elif dot > 1:
            dot = 1
        q = geo2.QuaternionRotationAxis(axis, math.acos(dot))
        q = geo2.QuaternionNormalize(q)
        return q



    def _TransformContext(self, q):
        scenarioSvc = sm.StartService('scenario')
        originalToolRotation = self.GetRotation()
        dungeonOrigin = scenarioSvc.GetDungeonOrigin()
        (toolPositionX, toolPositionY, toolPositionZ,) = sm.GetService('scenario').GetSelectionCenter()
        toolOffset = geo2.Vector(toolPositionX - dungeonOrigin.x, toolPositionY - dungeonOrigin.y, toolPositionZ - dungeonOrigin.z)
        qout = geo2.QuaternionMultiply(originalToolRotation, q)
        qout = geo2.QuaternionNormalize(qout)
        inverse = geo2.QuaternionInverse(originalToolRotation)
        diff = geo2.QuaternionMultiply(qout, inverse)
        diff = geo2.QuaternionNormalize(diff)
        slimItems = scenarioSvc.GetSelObjects()
        for slimItem in slimItems:
            if slimItem.dunObjectID in scenarioSvc.GetLockedObjects():
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    scenarioSvc.UnlockObject(slimItem.itemID, slimItem.dunObjectID, force=True)
                else:
                    continue
            targetBall = sm.StartService('michelle').GetBall(slimItem.itemID)
            targetModel = getattr(targetBall, 'model', None)
            if targetModel and slimItem.categoryID != const.categoryAsteroid and slimItem.groupID != const.groupHarvestableCloud:
                objectRotation = (targetModel.rotationCurve.value.x,
                 targetModel.rotationCurve.value.y,
                 targetModel.rotationCurve.value.z,
                 targetModel.rotationCurve.value.w)
                qout = geo2.QuaternionMultiply(objectRotation, diff)
                qout = geo2.QuaternionNormalize(qout)
                targetModel.rotationCurve.value.SetXYZW(*qout)
                slimItem.dunDirection = geo2.QuaternionTransformVector(qout, geo2.Vector(0.0, 0.0, 1.0))
                scenarioSvc.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_ROTATION)
            if len(slimItems) > 1 and not uicore.uilib.Key(uiconst.VK_SHIFT):
                relativeObjectPosition = geo2.Vector(slimItem.dunX - toolOffset.x, slimItem.dunY - toolOffset.y, slimItem.dunZ - toolOffset.z)
                rotatedDirectionVector = geo2.QuaternionTransformVector(diff, relativeObjectPosition)
                if targetModel:
                    targetModel.translationCurve.x = rotatedDirectionVector[0] + toolPositionX
                    targetModel.translationCurve.y = rotatedDirectionVector[1] + toolPositionY
                    targetModel.translationCurve.z = rotatedDirectionVector[2] + toolPositionZ
                elif slimItem.groupID in scenarioSvc.groupsWithNoModel:
                    try:
                        targetTransform = scenarioSvc.fakeTransforms[slimItem.itemID]
                        targetTransform.translationCurve.x = rotatedDirectionVector[0] + toolPositionX
                        targetTransform.translationCurve.y = rotatedDirectionVector[1] + toolPositionY
                        targetTransform.translationCurve.z = rotatedDirectionVector[2] + toolPositionZ
                    except KeyError:
                        scenarioSvc.LogError('Unable to rotate any ball for dungeon object:', slimItem.dunObjectID)
                slimItem.dunX = rotatedDirectionVector[0] + toolOffset.x
                slimItem.dunY = rotatedDirectionVector[1] + toolOffset.y
                slimItem.dunZ = rotatedDirectionVector[2] + toolOffset.z
                scenarioSvc.UpdateUnsavedObjectChanges(slimItem.itemID, CHANGE_TRANSLATION)

        qout = geo2.QuaternionMultiply(q, originalToolRotation)
        qout = geo2.QuaternionNormalize(qout)
        self.Rotate(qout)



    def AddRotationCurveToObject(self, itemID):
        ball = sm.GetService('michelle').GetBall(itemID)
        if ball.model is None:
            return 
        if ball.model.rotationCurve is not None:
            return 
        ball.model.rotationCurve = ball.model.translationCurve



    def GetDesiredPlaneNormal(self, ray):
        viewMat = trinity.GetViewTransform()
        view = geo2.Vector(viewMat[0][2], viewMat[1][2], viewMat[2][2])
        local_axis = {'x': self.GetRightVec(),
         'y': self.GetUpVec(),
         'z': self.GetFrontVec()}
        if self.activeManipAxis in local_axis:
            axis = local_axis[self.activeManipAxis]
            if geo2.Vec3Dot(view, axis) > 0.0:
                norm = -axis
            else:
                norm = axis
        else:
            norm = view
        norm = geo2.Vec3Normalize(norm)
        return norm



    def _DiffProjectedPoint(self, ray, start):
        self.endPlanePos = RayToPlaneIntersection(start, ray, self.GetTranslation(), self.targetPlaneNormal)



    def _InternalUpdate(self):
        mat = CameraFacingMatrix(self.worldTranslation)
        warea = self.geometry.GetArea('w')
        wwarea = self.geometry.GetArea('ww')
        warea.localTransform = mat
        wwarea.localTransform = mat



exports = util.AutoExports('dungeonEditorTools', locals())

