import util
import math
import trinity
import planet
import geo2

class CurveLineDrawer:
    __guid__ = 'planet.ui.CurveLineDrawer'

    def __init__(self):
        self.p0 = (0.0, 0.0, 0.0)
        self.lineSets = {}
        self.lastZoom = None
        self.transformsByLineSets = {}



    def CreateLineSet(self, lsName, transform, animationTexture = None, scale = 1.0):
        ls = trinity.EveCurveLineSet()
        ls.scaling = (scale, scale, scale)
        tex2D_1 = trinity.TriTexture2DParameter()
        tex2D_1.name = 'TexMap'
        tex2D_1.resourcePath = 'res:/texture/global/lineSolid.dds'
        ls.lineEffect.resources.append(tex2D_1)
        if animationTexture:
            tex2D_2 = trinity.TriTexture2DParameter()
            tex2D_2.name = 'OverlayTexMap'
            tex2D_2.resourcePath = animationTexture
            ls.lineEffect.resources.append(tex2D_2)
        self.lineSets[lsName] = ls
        transform.children.append(ls)
        self.transformsByLineSets[ls] = transform
        return ls



    def GetLineSet(self, lsName):
        return self.lineSets[lsName]



    def ScaleLineSet(self, lsName, scale):
        ls = self.GetLineSet(lsName)
        ls.scaling = (scale, scale, scale)



    def RotateLineSet(self, lsName, rotX, rotY, rotZ):
        ls = self.GetLineSet(lsName)
        ls.rotation = (0.0,
         rotX,
         rotY,
         rotZ)



    def SetLineSetNumSegments(self, lsName, lineID, numSegments):
        ls = self.GetLineSet(lsName)
        ls.ChangeLineSegmentation(lineID, numSegments)



    def RemoveLine(self, lsName, lineID):
        ls = self.GetLineSet(lsName)
        ls.RemoveLine(lineID)
        ls.SubmitChanges()



    def ClearLineSets(self):
        for ls in self.lineSets.values():
            self.transformsByLineSets[ls].children.remove(ls)

        self.transformsByLineSets = {}
        self.lineSets = {}



    def ClearLines(self, lsName):
        if lsName not in self.lineSets:
            return None
        ls = self.lineSets[lsName]
        ls.ClearLines()
        ls.SubmitChanges()



    def ChangeLineColor(self, lsName, lineID, color):
        ls = self.GetLineSet(lsName)
        ls.ChangeLineColor(lineID, color, color)



    def ChangeLineSetWidth(self, lsName, widthFactor):
        ls = self.GetLineSet(lsName)
        ls.lineWidthFactor = widthFactor



    def ChangeLineWidth(self, lsName, lineID, width):
        ls = self.GetLineSet(lsName)
        ls.ChangeLineWidth(lineID, width)
        ls.SubmitChanges()



    def ChangeLinePosition(self, lsName, lineID, start, end):
        ls = self.GetLineSet(lsName)
        p1 = start.GetAsXYZTuple()
        p2 = end.GetAsXYZTuple()
        ls.ChangeLinePositionCrt(lineID, p1, p2)
        self.SubmitLineset(lsName)



    def ChangeLineAnimation(self, lsName, lineID, color, speed, scale):
        ls = self.GetLineSet(lsName)
        ls.ChangeLineAnimation(lineID, color, speed, scale)



    def DrawArc(self, lsName, surfacePoint1, surfacePoint2, lineWidth = 1.0, color1 = util.Color.WHITE, color2 = util.Color.WHITE):
        ls = self.GetLineSet(lsName)
        p1 = surfacePoint1.GetAsXYZTuple()
        p2 = surfacePoint2.GetAsXYZTuple()
        lineID = ls.AddSpheredLineCrt(p1, color1, p2, color2, self.p0, lineWidth)
        return lineID



    def DrawLine(self, lsName, surfacePoint1, surfacePoint2, lineWidth = 1.0, color1 = util.Color.WHITE, color2 = util.Color.WHITE):
        ls = self.GetLineSet(lsName)
        p1 = surfacePoint1.GetAsXYZTuple()
        p2 = surfacePoint2.GetAsXYZTuple()
        lineID = ls.AddStraightLine(p1, color1, p2, color2, lineWidth)
        return lineID



    def SubmitLineset(self, lsName):
        ls = self.GetLineSet(lsName)
        ls.SubmitChanges()



    def DrawMesh(self, zoom):
        layers = [util.KeyVal(numTheta=40, numPhi=20, showAtZoom=1.0, phiSkip=3, linesetName='planetExternalGrid', lineSet=None)]
        if not hasattr(self, 'meshInitialized'):
            for l in layers:
                self._DrawMesh(l.linesetName, l.numPhi, l.numTheta, l.phiSkip, 1.0)

            self.meshInitialized = True
        lineWidth = 2.0
        for l in layers:
            ls = self.GetLineSet(l.linesetName)
            if zoom <= l.showAtZoom:
                ls.lineWidthFactor = lineWidth
                lineWidth += 1.0
            else:
                ls.lineWidthFactor = 0.0




    def _DrawMesh(self, lsName, numPhi = 30, numTheta = 60, phiSkip = 0, lineWidth = 2.0, col = (1.0, 1.0, 1.0, 0.01)):
        col = (0.8, 0.8, 1.0, 0.3)
        colAnim = (1.0, 1.0, 1.0, 1.0)
        speedAnim = 0.06
        scaleAnim = 2.0
        phi0 = math.pi / 90
        phiStep = (math.pi - 2 * phi0) / numPhi
        phiInit = phi0 + phiStep * phiSkip
        ls = self.GetLineSet(lsName)
        for p in xrange(numPhi + 1):
            if p <= phiSkip - 1 or p > numPhi - phiSkip:
                continue
            phi = phi0 + float(p) * phiStep
            for quarter in xrange(0, 4):
                th0 = math.pi / 2 * quarter
                p1 = planet.SurfacePoint(theta=th0, phi=phi)
                p2 = planet.SurfacePoint(theta=th0 + math.pi / 2, phi=phi)
                pC = planet.SurfacePoint(0.0, p1.y, 0.0)
                lineID = ls.AddSpheredLineCrt(p1.GetAsXYZTuple(), col, p2.GetAsXYZTuple(), col, pC.GetAsXYZTuple(), lineWidth)
                ls.ChangeLineAnimation(lineID, colAnim, speedAnim, scaleAnim)


        for t in xrange(numTheta):
            th = float(t) / numTheta * math.pi * 2
            p1 = planet.SurfacePoint(theta=th, phi=math.pi / 2.0)
            p2 = planet.SurfacePoint(theta=th, phi=phiInit)
            lineID = ls.AddSpheredLineCrt(p1.GetAsXYZTuple(), col, p2.GetAsXYZTuple(), col, self.p0, lineWidth)
            ls.ChangeLineAnimation(lineID, colAnim, speedAnim, scaleAnim)
            p2 = planet.SurfacePoint(theta=th, phi=math.pi - phiInit)
            lineID = ls.AddSpheredLineCrt(p1.GetAsXYZTuple(), col, p2.GetAsXYZTuple(), col, self.p0, lineWidth)
            ls.ChangeLineAnimation(lineID, colAnim, speedAnim, scaleAnim)

        ls.SubmitChanges()



    def DrawCartesianAxis(self):
        lsName = 'cartesianAxis'
        sp = planet.SurfacePoint
        len = 1.5
        if getattr(self, 'cartesianAxisAlreadyDrawn', False):
            self.ClearLines(lsName)
            self.cartesianAxisAlreadyDrawn = False
            return 
        if lsName not in self.lineSets:
            self.CreateLineSet(lsName, sm.GetService('planetUI').planetTransform)
        self.DrawLine(lsName, sp(), sp(len, 0, 0), 3.0, util.Color.RED, util.Color.RED)
        self.DrawLine(lsName, sp(), sp(0, len, 0), 3.0, util.Color.GREEN, util.Color.GREEN)
        self.DrawLine(lsName, sp(), sp(0, 0, len), 3.0, util.Color.BLUE, util.Color.BLUE)
        self.SubmitLineset(lsName)
        self.cartesianAxisAlreadyDrawn = True



    def DrawIcosahedronGrid(self):
        detailLevel = 3
        t = (1.0 + math.sqrt(5)) / 2.0
        sp = planet.SurfacePoint
        sps = []
        sps = [sp(t, 1, 0),
         sp(-t, 1, 0),
         sp(t, -1, 0),
         sp(-t, -1, 0),
         sp(1, 0, t),
         sp(1, 0, -t),
         sp(-1, 0, t),
         sp(-1, 0, -t),
         sp(0, t, 1),
         sp(0, -t, 1),
         sp(0, t, -1),
         sp(0, -t, -1)]
        for p in sps:
            p.SetRadius(1.0)

        triangles = [(0, 8, 4),
         (0, 5, 10),
         (2, 4, 9),
         (2, 11, 5),
         (1, 6, 8),
         (1, 10, 7),
         (3, 9, 6),
         (3, 7, 11),
         (0, 10, 8),
         (1, 8, 10),
         (2, 9, 11),
         (3, 9, 11),
         (4, 2, 0),
         (5, 0, 2),
         (6, 1, 3),
         (7, 3, 1),
         (8, 6, 4),
         (9, 4, 6),
         (10, 5, 7),
         (11, 7, 5)]
        lines = set()
        cLines = set()
        hLines = set()
        for t in triangles:
            v0 = sps[t[0]]
            v1 = sps[t[1]]
            v2 = sps[t[2]]
            cLines.add((v0, v1))
            cLines.add((v1, v2))
            cLines.add((v2, v0))
            self._SplitTriangle(v0, v1, v2, lines, cLines, hLines, sps, detailLevel)

        cLineCol = (174.0 / 256,
         222.0 / 256,
         228.0 / 256,
         0.9)
        lineCol1 = cLineCol
        lineCol2 = (0.0, 0.0, 0.0, 0.0)
        hLineCol = (0.0, 0.0, 0.0, 0.0)
        for l in lines:
            self.DrawLine('icosahedron', l[0], l[1], 2.0, color1=lineCol1, color2=lineCol2)

        self.SubmitLineset('icosahedron')



    def _SplitTriangle(self, v0, v1, v2, lines, cLines, hLines, sps, level):
        level -= 1
        lc0 = self._GetLineCenterPoint(v0, v1)
        lc1 = self._GetLineCenterPoint(v1, v2)
        lc2 = self._GetLineCenterPoint(v2, v0)
        tc = self._GetTriangleCenterPoint(v0, v1, v2)
        if level > 0:
            self._SplitTriangle(v0, lc0, lc2, lines, cLines, hLines, sps, level)
            self._SplitTriangle(v1, lc1, lc0, lines, cLines, hLines, sps, level)
            self._SplitTriangle(v2, lc2, lc1, lines, cLines, hLines, sps, level)
            self._SplitTriangle(lc0, lc1, lc2, lines, cLines, hLines, sps, level)
        else:
            v = geo2.Vector
            vecC = v(*tc.GetAsXYZTuple())
            vec0 = v(*v0.GetAsXYZTuple())
            vec1 = v(*v0.GetAsXYZTuple())
            vec2 = v(*v0.GetAsXYZTuple())
            vec01 = v(*(v1.x - v0.x, v1.y - v0.y, v1.z - v0.z))
            n0 = v(*geo2.Vec3Cross(vecC, vec01))
            vec12 = v(*(v2.x - v1.x, v2.y - v1.y, v2.z - v1.z))
            n1 = v(*geo2.Vec3Cross(vecC, vec12))
            vec20 = v(*(v0.x - v2.x, v0.y - v2.y, v0.z - v2.z))
            n2 = v(*geo2.Vec3Cross(vecC, vec20))
            s = 0.16
            sGap = 0.1
            n0 = v(*(s * n0))
            n1 = v(*(s * n1))
            n2 = v(*(s * n2))
            lp0 = planet.SurfacePoint(*(vecC - n0))
            lp1 = planet.SurfacePoint(*(vecC - n1))
            lp2 = planet.SurfacePoint(*(vecC - n2))
            lr0 = planet.SurfacePoint(*(vecC - v(*(sGap * n0))))
            lr1 = planet.SurfacePoint(*(vecC - v(*(sGap * n1))))
            lr2 = planet.SurfacePoint(*(vecC - v(*(sGap * n2))))
            lp0.SetRadius(1.0)
            lp1.SetRadius(1.0)
            lp2.SetRadius(1.0)
            lr0.SetRadius(1.0)
            lr1.SetRadius(1.0)
            lr2.SetRadius(1.0)
            lines.add((lr0, lp0))
            lines.add((lr1, lp1))
            lines.add((lr2, lp2))



    def _GetTriangleCenterPoint(self, sp1, sp2, sp3):
        x = sp1.x / 3.0 + sp2.x / 3.0 + sp3.x / 3.0
        y = sp1.y / 3.0 + sp2.y / 3.0 + sp3.y / 3.0
        z = sp1.z / 3.0 + sp2.z / 3.0 + sp3.z / 3.0
        sp = planet.SurfacePoint(x, y, z)
        sp.SetRadius(1.0)
        return sp



    def _GetLineCenterPoint(self, sp1, sp2):
        x = sp1.x / 2.0 + sp2.x / 2.0
        y = sp1.y / 2.0 + sp2.y / 2.0
        z = sp1.z / 2.0 + sp2.z / 2.0
        sp = planet.SurfacePoint(x, y, z)
        sp.SetRadius(1.0)
        return sp




