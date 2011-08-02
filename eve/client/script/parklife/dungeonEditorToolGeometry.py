import geo2
import trinity
import math
import sys
import util
LIGHT_GREEN = (0.25, 1.0, 0.6, 1.0)
LIGHT_GRAY = (0.5, 0.5, 0.5, 1.0)
DARK_GRAY = (0.12, 0.12, 0.12, 1.0)
RED = (1.0, 0.01, 0.01, 1.0)
GREEN = (0.01, 1.0, 0.01, 1.0)
BLUE = (0.01, 0.01, 1.0, 1.0)
YELLOW = (1.0, 1.0, 0.01, 1.0)
MAGENTA = (1.0, 0.01, 1.0, 1.0)
DARK_MAGENTA = (0.5, 0.01, 0.5, 1.0)
CYAN = (0.0, 1.0, 1.0, 1.0)
BOX_LINES = [geo2.Vector(-0.5, -0.5, 0.5),
 geo2.Vector(0.5, -0.5, 0.5),
 geo2.Vector(-0.5, 0.5, 0.5),
 geo2.Vector(0.5, 0.5, 0.5),
 geo2.Vector(-0.5, 0.5, -0.5),
 geo2.Vector(0.5, 0.5, -0.5),
 geo2.Vector(-0.5, -0.5, -0.5),
 geo2.Vector(0.5, -0.5, -0.5),
 geo2.Vector(-0.5, -0.5, 0.5),
 geo2.Vector(-0.5, 0.5, 0.5),
 geo2.Vector(0.5, -0.5, 0.5),
 geo2.Vector(0.5, 0.5, 0.5),
 geo2.Vector(-0.5, 0.5, 0.5),
 geo2.Vector(-0.5, 0.5, -0.5),
 geo2.Vector(0.5, 0.5, 0.5),
 geo2.Vector(0.5, 0.5, -0.5),
 geo2.Vector(-0.5, 0.5, -0.5),
 geo2.Vector(-0.5, -0.5, -0.5),
 geo2.Vector(0.5, 0.5, -0.5),
 geo2.Vector(0.5, -0.5, -0.5),
 geo2.Vector(-0.5, -0.5, -0.5),
 geo2.Vector(-0.5, -0.5, 0.5),
 geo2.Vector(0.5, -0.5, -0.5),
 geo2.Vector(0.5, -0.5, 0.5)]

def GeoToTri(obj):
    if len(obj) == 3:
        return trinity.TriVector(*obj)
    if len(obj) == 4:
        if isinstance(obj[0], tuple):
            tempTuple = obj[0] + obj[1] + obj[2] + obj[3]
            return trinity.TriMatrix(*tempTuple)
        else:
            return trinity.TriQuaternion(*obj)
    else:
        raise TypeError('Unsupported type')



def GenBoxTriangles():
    points = [(-0.0750000029802, -0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, 0.0750000029802),
     (0.0750000029802, 0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, 0.0750000029802),
     (0.0750000029802, 0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, 0.0750000029802, -0.0750000029802),
     (0.0750000029802, 0.0750000029802, 0.0750000029802),
     (0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, 0.0750000029802, -0.0750000029802),
     (0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, -0.0750000029802),
     (0.0750000029802, 0.0750000029802, -0.0750000029802),
     (0.0750000029802, -0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, -0.0750000029802),
     (0.0750000029802, -0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, 0.0750000029802),
     (-0.0750000029802, -0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, -0.0750000029802),
     (0.0750000029802, -0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, -0.0750000029802),
     (0.0750000029802, 0.0750000029802, 0.0750000029802),
     (0.0750000029802, 0.0750000029802, 0.0750000029802),
     (0.0750000029802, -0.0750000029802, -0.0750000029802),
     (0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, 0.0750000029802, -0.0750000029802),
     (-0.0750000029802, -0.0750000029802, 0.0750000029802),
     (-0.0750000029802, 0.0750000029802, 0.0750000029802)]
    triangles = []
    for i in range(12):
        triangles.append(geo2.Vector(*points[(i * 3)]))
        triangles.append(geo2.Vector(*points[(i * 3 + 1)]))
        triangles.append(geo2.Vector(*points[(i * 3 + 2)]))

    return triangles



def GenCubeTriangles(size = 0.075):
    points = [(-size, -size, size),
     (size, -size, size),
     (-size, size, size),
     (-size, size, size),
     (size, -size, size),
     (size, size, size),
     (-size, size, size),
     (size, size, size),
     (-size, size, -size),
     (-size, size, -size),
     (size, size, size),
     (size, size, -size),
     (-size, size, -size),
     (size, size, -size),
     (-size, -size, -size),
     (-size, -size, -size),
     (size, size, -size),
     (size, -size, -size),
     (-size, -size, -size),
     (size, -size, -size),
     (-size, -size, size),
     (-size, -size, size),
     (size, -size, -size),
     (size, -size, size),
     (size, -size, size),
     (size, -size, -size),
     (size, size, size),
     (size, size, size),
     (size, -size, -size),
     (size, size, -size),
     (-size, -size, -size),
     (-size, -size, size),
     (-size, size, -size),
     (-size, size, -size),
     (-size, -size, size),
     (-size, size, size)]
    triangles = []
    for i in range(12):
        triangles.append(points[(i * 3)])
        triangles.append(points[(i * 3 + 1)])
        triangles.append(points[(i * 3 + 2)])

    return triangles



def GenConeTriangles():
    top = geo2.Vector(0.0, 0.25, 0.0)
    pi = math.pi
    rad = pi / 10.0
    triangles = []
    for each in range(20):
        triangles.append(top)
        triangles.append(geo2.Vector(math.cos((each + 1) * rad) * 0.1, 0.0, math.sin((each + 1) * rad) * 0.1))
        triangles.append(geo2.Vector(math.cos(each * rad) * 0.1, 0.0, math.sin(each * rad) * 0.1))
        triangles.append(geo2.Vector(math.cos((each + 1) * rad) * 0.1, 0.0, math.sin((each + 1) * rad) * 0.1))
        triangles.append(geo2.Vector(0.0, 0.0, 0.0))
        triangles.append(geo2.Vector(math.cos(each * rad) * 0.1, 0.0, math.sin(each * rad) * 0.1))

    return triangles



def GenCirclePoints(radius, subd = 20):
    pi = math.pi
    rad = pi / (subd / 2.0)
    lines = []
    for each in range(subd):
        lines.append((math.cos(each * rad) * radius, math.sin(each * rad) * radius, 0.0))
        lines.append((math.cos((each + 1) * rad) * radius, math.sin((each + 1) * rad) * radius, 0.0))

    return lines



def GenCircleTriangles(radius, subd = 20):
    pi = math.pi
    rad = pi / (subd / 2.0)
    triangles = []
    startPoint = (math.cos(0.0) * radius, math.sin(0.0) * radius, 0.0)
    for each in range(1, subd):
        triangles.append(startPoint)
        triangles.append((math.cos(each * rad) * radius, math.sin(each * rad) * radius, 0.0))
        triangles.append((math.cos((each + 1) * rad) * radius, math.sin((each + 1) * rad) * radius, 0.0))

    return triangles



def GenLightSpikes(radius, subd = 8):
    pi = math.pi
    rad = pi / (subd / 2.0)
    lines = []
    for each in range(subd):
        lines.append(geo2.Vector(math.cos(each * rad) * radius, 0.0, math.sin(each * rad) * radius))
        lines.append(geo2.Vector(math.cos(each * rad) * radius * 2.0, 0.0, math.sin(each * rad) * radius * 2.0))

    return lines



def GenSquarePoints():
    pi = math.pi
    rad = pi / 10.0
    lines = []
    c = math.cos(pi / 4)
    s = math.sin(pi / 4 * 3)
    lines = [geo2.Vector(s, 0.0, c),
     geo2.Vector(-s, 0.0, c),
     geo2.Vector(-s, 0.0, c),
     geo2.Vector(-s, 0.0, -c),
     geo2.Vector(-s, 0.0, -c),
     geo2.Vector(s, 0.0, -c),
     geo2.Vector(s, 0.0, -c),
     geo2.Vector(s, 0.0, c)]
    return lines



def GetGeometry(mlist):
    lines = []
    for i in range(0, len(mlist), 2):
        lines.append(geo2.Vector(*mlist[i]))
        lines.append(geo2.Vector(*mlist[(i + 1)]))

    return lines


BOX_TRIS = GenBoxTriangles()
CUBE_TRIS = GenCubeTriangles()
CONE_TRIS = GenConeTriangles()
CIRCLE_POINTS_QUART = GenCirclePoints(0.25)
CIRCLE_POINTS_UNIT = GenCirclePoints(1.0)
SQUARE_POINTS = GenSquarePoints()
LIGHT_SPIKES_QUART = GenLightSpikes(0.25)
LIGHT_SPIKES_UNIT = GenLightSpikes(1.0)
QUAD = [geo2.Vector(-1.0, 0.0, -1.0),
 geo2.Vector(1.0, 0.0, 1.0),
 geo2.Vector(1.0, 0.0, -1.0),
 geo2.Vector(-1.0, 0.0, -1.0),
 geo2.Vector(1.0, 0.0, -1.0),
 geo2.Vector(1.0, 0.0, 1.0)]

def GetSolidAroundLine(line, radius):
    rad = math.pi * 2.0 / 3.0
    triangle1 = []
    triangle1.append((math.cos(0) * radius, math.sin(0) * radius, 0.0))
    triangle1.append((math.cos(rad) * radius, math.sin(rad) * radius, 0.0))
    triangle1.append((math.cos(2 * rad) * radius, math.sin(2 * rad) * radius, 0.0))
    dirOfLine = geo2.Vec3Normalize(geo2.Vec3Subtract(line[1], line[0]))
    if abs(geo2.Vec3Dot((0.0, 0.0, 1.0), dirOfLine)) != 1.0:
        rot = geo2.QuaternionRotationArc((0.0, 0.0, 1.0), dirOfLine)
    else:
        rot = geo2.QuaternionIdentity()
    rot = geo2.MatrixRotationQuaternion(rot)
    t1 = geo2.MatrixTranslation(*line[0])
    t2 = geo2.MatrixTranslation(*line[1])
    compA = geo2.MatrixMultiply(rot, t1)
    compB = geo2.MatrixMultiply(rot, t2)
    startTri = geo2.Vec3TransformCoordArray(triangle1, compA)
    endTri = geo2.Vec3TransformCoordArray(triangle1, compB)
    triangles = [startTri[1],
     endTri[0],
     startTri[0],
     endTri[1],
     endTri[0],
     startTri[1],
     startTri[2],
     endTri[1],
     startTri[1],
     endTri[2],
     endTri[1],
     startTri[2],
     startTri[0],
     endTri[2],
     startTri[2],
     endTri[0],
     endTri[2],
     startTri[0]]
    return triangles



def GetSolidAroundLines(poslist, width):
    triangles = []
    for each in xrange(0, len(poslist), 2):
        triangles.extend(GetSolidAroundLine((poslist[each], poslist[(each + 1)]), width))

    return triangles



class basearea(object):

    def __init__(self, name, color = (0.0, 0.0, 0.0, 1.0), primitiveScene = None):
        object.__init__(self)
        self.name = name
        self._color = color
        self._display = False
        self.primitiveScene = primitiveScene
        self.primitives = []
        self.valuebindings = []
        self.localTransform = geo2.MatrixIdentity()



    def __del__(self):
        if self.primitiveScene is not None:
            for each in iter(self.primitives):
                self.primitiveScene.primitives.fremove(each)




    def SetSourceObject(self, obj, attr, call = None):
        for each in iter(self.valuebindings):
            each.sourceAttribute = attr
            each.sourceObject = obj
            if callable(call):
                each.copyValueCallable = call




    def SetDisplay(self, val):
        if self.primitiveScene is not None:
            if val:
                for each in iter(self.primitives):
                    if each not in self.primitiveScene.primitives:
                        self.primitiveScene.primitives.append(each)

            else:
                for each in iter(self.primitives):
                    self.primitiveScene.primitives.fremove(each)

        self._display = val



    def GetDisplay(self):
        return self._display


    display = property(GetDisplay, SetDisplay)

    def SetColor(self, val):
        self._color = val
        for each in iter(self.primitives):
            each.color = val




    def GetColor(self):
        return self._color


    color = property(GetColor, SetColor)

    def UpdateTransform(self, transform):
        mat = geo2.MatrixMultiply(self.localTransform, transform)
        for each in iter(self.primitives):
            each.localTransform = mat





class area(basearea):

    def __init__(self, name, color = (0.0, 0.0, 0.0, 1.0), scaleByDistance = True, viewOriented = False, primitiveScene = None):
        basearea.__init__(self, name, color, primitiveScene)
        self._lineset = trinity.Tr2LineSet()
        self._lineset.scaleByDistanceToView = scaleByDistance
        self._lineset.viewOriented = viewOriented
        self._lineset.name = name
        self._lineset.effect = trinity.Tr2Effect()
        self._lineset.pickEffect = trinity.Tr2Effect()
        self._lineset.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/LinesNoZ.fx'
        self._lineset.pickEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/PrimitivePicking.fx'
        self._solidset = trinity.Tr2SolidSet()
        self._solidset.scaleByDistanceToView = scaleByDistance
        self._solidset.name = name
        self._solidset.effect = trinity.Tr2Effect()
        self._solidset.pickEffect = trinity.Tr2Effect()
        self._solidset.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/SolidsNoZ.fx'
        self._solidset.pickEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/PrimitivePicking.fx'
        self.primitives.append(self._solidset)
        self.primitives.append(self._lineset)



    def SetColor(self, val):
        self._color = val
        for each in iter(self.primitives):
            each.color = val




    def GetColor(self):
        return self._color


    color = property(GetColor, SetColor)

    def Update(self, transform):
        mat = geo2.MatrixMultiply(self.localTransform, transform)
        tmat = GeoToTri(mat)
        if len(self.lines) > 0:
            self.lineset.transform = tmat
        if len(self.triangles) > 0:
            self.solidset.transform = tmat
        if len(self.points) > 0:
            self.pointset.transform = tmat
        if self.bounds:
            try:
                self.bounds.Update(mat)
            except Exception as e:
                import traceback
                traceback.print_exc()
                sys.exc_clear()



    def Render(self):
        if len(self.lines) > 0:
            self.lineset.Render()
        if len(self.triangles) > 0:
            self.solidset.Render()
        if len(self.points) > 0:
            self.pointset.Render()
        if self.drawBounds:
            try:
                self.bounds.Render()
            except Exception as e:
                import traceback
                traceback.print_exc()
                sys.exc_clear()



    def AddToPickingSet(self, poslist):
        if len(poslist) % 3 != 0:
            raise RuntimeError('The number of points must be a multiple of 3')
        for i in xrange(0, len(poslist), 3):
            self._lineset.AddPickingTriangle(poslist[i], poslist[(i + 1)], poslist[(i + 2)])

        self._lineset.SubmitChanges()



    def AddToLineSet(self, poslist, genPickingGeo = False):
        if len(poslist) % 2 != 0:
            raise RuntimeError('The number of points must be a multiple of 2')
        for i in xrange(0, len(poslist), 2):
            self._lineset.AddLine(poslist[i], self._color, poslist[(i + 1)], self._color)

        if genPickingGeo:
            triangles = GetSolidAroundLines(poslist, 0.08)
            self.AddToPickingSet(triangles)
        else:
            self._lineset.SubmitChanges()



    def AddToPointSet(self, poslist):
        if self.bounds:
            self.bounds.ComputeBounds(poslist)
        xr = xrange(len(poslist))
        vec = geo2.Vector
        points = self.points
        p_append = points.append
        for i in xr:
            a = vec(*poslist[i])
            p_append(a)

        self.pointset.SetDefaultColor(self._color)
        self.pointset.AddPoints(points)



    def AddToSolidSet(self, poslist):
        if len(poslist) % 3 != 0:
            raise RuntimeError('The number of points must be a multiple of 3')
        for i in xrange(0, len(poslist), 3):
            self._solidset.AddTriangle(poslist[i], self._color, poslist[(i + 1)], self._color, poslist[(i + 2)], self._color)

        self._solidset.SubmitChanges()



    def BoundProbe(self, ray, start):
        if self.bounds:
            return self.bounds.RayToBound(ray, start)
        else:
            return False




class geometry(object):

    def __init__(self, primitiveScene):
        self.primitiveScene = primitiveScene
        self.areas = []
        self.groups = {}
        self.visible_areas = []
        self._display = False



    def Update(self, transform):
        self.visible_areas = []
        for each in iter(self.areas):
            if each.display:
                each.UpdateTransform(transform)
                self.visible_areas.append(each)

        return self.visible_areas



    def AppendArea(self, a):
        self.areas.append(a)
        g = self.groups.get(a.name, [])
        g.append(a)
        self.groups[a.name] = g
        a.primitiveScene = self.primitiveScene



    def ExtendArea(self, a):
        self.areas.extend(a)
        g = self.groups.get(a[0].name, [])
        g.extend(a)
        self.groups[a[0].name] = g
        for each in a:
            each.primitiveScene = self.primitiveScene




    def GetArea(self, name):
        for each in self.areas:
            if each.name == name:
                return each




    def SetArea(self, name, area):
        found = False
        for (i, each,) in enumerate(self.areas):
            if each.name == name:
                found = True
                break

        if found:
            self.areas[i] = area
        return found



    def GetAreas(self, name):
        areas = []
        for each in self.areas:
            if each.name == name:
                areas.append(each)

        return areas



    def SetDisplay(self, val):
        for each in self.areas:
            each.display = val

        self._display = val



    def GetDisplay(self):
        return self._display


    display = property(GetDisplay, SetDisplay)

exports = util.AutoExports('dungeonEditorToolGeometry', locals())

