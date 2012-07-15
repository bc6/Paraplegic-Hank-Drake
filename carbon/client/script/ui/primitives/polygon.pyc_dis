#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/primitives/polygon.py
import uicls
import trinity
import math
import mathUtil

class Polygon(uicls.TexturedBase):
    __guid__ = 'uicls.Polygon'
    __renderObject__ = trinity.Tr2Sprite2dPolygon
    default_name = 'polygon'
    default_color = (1, 1, 1, 1)
    default_spriteEffect = trinity.TR2_SFX_FILL

    def Flush(self):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]

    def MakeArc(self, radius = 32.0, outerRadius = 66.0, segments = 12, fromDeg = 0.0, toDeg = 90.0, innerColor = default_color, outerColor = default_color, feather = 3.0):
        self.Flush()
        ro = self.GetRenderObject()
        segmentStep = (toDeg - fromDeg) / float(segments)
        TRANSPCOLOR = (0, 0, 0, 0)
        for i in xrange(segments + 1):
            a = mathUtil.DegToRad(fromDeg + i * segmentStep)
            x = math.cos(a)
            y = math.sin(a)
            innerVertex = trinity.Tr2Sprite2dVertex()
            innerVertex.position = (x * radius, y * radius)
            innerVertex.color = innerColor
            ro.vertices.append(innerVertex)
            outerVertex = trinity.Tr2Sprite2dVertex()
            outerVertex.position = (x * outerRadius, y * outerRadius)
            outerVertex.color = outerColor
            ro.vertices.append(outerVertex)

        for i in xrange(segments * 2):
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = i
            triangle.index1 = i + 1
            triangle.index2 = i + 2
            ro.triangles.append(triangle)

        if feather:
            shift = len(ro.vertices)
            for i in xrange(segments + 1):
                a = mathUtil.DegToRad(fromDeg + i * segmentStep)
                x = math.cos(a)
                y = math.sin(a)
                innerFeatherVertex = trinity.Tr2Sprite2dVertex()
                innerFeatherVertex.position = (x * (radius - feather), y * (radius - feather))
                innerFeatherVertex.color = TRANSPCOLOR
                ro.vertices.append(innerFeatherVertex)
                outerFeatherVertex = trinity.Tr2Sprite2dVertex()
                outerFeatherVertex.position = (x * (outerRadius + feather), y * (outerRadius + feather))
                outerFeatherVertex.color = TRANSPCOLOR
                ro.vertices.append(outerFeatherVertex)

            for i in xrange(segments * 2):
                triangle = trinity.Tr2Sprite2dTriangle()
                triangle.index0 = i
                triangle.index1 = shift + i
                triangle.index2 = shift + i + 2
                ro.triangles.append(triangle)
                triangle = trinity.Tr2Sprite2dTriangle()
                triangle.index0 = shift + i + 2
                triangle.index1 = i + 2
                triangle.index2 = i
                ro.triangles.append(triangle)

    def MakeCircle(self, radius = 64.0, segments = 12, centerColor = default_color, edgeColor = default_color):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        centerVertex = trinity.Tr2Sprite2dVertex()
        centerVertex.position = (radius, radius)
        centerVertex.color = centerColor
        centerVertex.texCoord0 = (0.5, 0.5)
        centerVertex.texCoord1 = (0.5, 0.5)
        ro.vertices.append(centerVertex)
        for i in xrange(segments):
            a = math.pi * 2.0 / float(segments) * float(i)
            x = math.cos(a)
            y = math.sin(a)
            edgeVertex = trinity.Tr2Sprite2dVertex()
            edgeVertex.position = (x * radius + radius, y * radius + radius)
            edgeVertex.color = edgeColor
            edgeVertex.texCoord0 = (x * 0.5 + 0.5, y * 0.5 + 0.5)
            edgeVertex.texCoord1 = edgeVertex.texCoord0
            ro.vertices.append(edgeVertex)

        for i in xrange(segments - 1):
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = 0
            triangle.index1 = i + 1
            triangle.index2 = i + 2
            ro.triangles.append(triangle)

        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = segments
        triangle.index2 = 1
        ro.triangles.append(triangle)

    def MakeRectangle(self, topLeft = (0, 0), topLeftColor = (1, 1, 1, 1), topRight = (64, 0), topRightColor = (1, 1, 1, 1), bottomRight = (64, 64), bottomRightColor = (1, 1, 1, 1), bottomLeft = (0, 64), bottomLeftColor = (1, 1, 1, 1)):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topLeft
        vertex.color = topLeftColor
        vertex.texCoord0 = (0, 0)
        vertex.texCoord1 = (0, 0)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topRight
        vertex.color = topRightColor
        vertex.texCoord0 = (1, 0)
        vertex.texCoord1 = (1, 0)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomRight
        vertex.color = bottomRightColor
        vertex.texCoord0 = (1, 1)
        vertex.texCoord1 = (1, 1)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomLeft
        vertex.color = bottomLeftColor
        vertex.texCoord0 = (0, 1)
        vertex.texCoord1 = (0, 1)
        ro.vertices.append(vertex)
        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = 1
        triangle.index2 = 2
        ro.triangles.append(triangle)
        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = 2
        triangle.index2 = 3
        ro.triangles.append(triangle)

    def MakeGradient(self, width = 256, height = 256, colorPoints = [(0, (0, 0, 0, 1)), (1, (1, 1, 1, 1))], rotation = 0):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        startPoint = colorPoints[0]
        startValue = startPoint[0]
        startColor = startPoint[1]
        topLeft = (startValue, 0)
        bottomLeft = (startValue, height)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topLeft
        vertex.color = startColor
        vertex.texCoord0 = (0, 0)
        vertex.texCoord1 = (0, 0)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomLeft
        vertex.color = startColor
        vertex.texCoord0 = (0, 1)
        vertex.texCoord1 = (0, 1)
        ro.vertices.append(vertex)
        baseIx = 0
        for i in xrange(len(colorPoints) - 1):
            endPoint = colorPoints[i + 1]
            endValue = endPoint[0]
            endColor = endPoint[1]
            topLeft = (endValue * width, 0)
            bottomLeft = (endValue * width, height)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = topLeft
            vertex.color = endColor
            vertex.texCoord0 = (endValue, 0)
            vertex.texCoord1 = (endValue, 0)
            ro.vertices.append(vertex)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = bottomLeft
            vertex.color = endColor
            vertex.texCoord0 = (endValue, 1)
            vertex.texCoord1 = (endValue, 1)
            ro.vertices.append(vertex)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 0
            triangle.index1 = baseIx + 1
            triangle.index2 = baseIx + 2
            ro.triangles.append(triangle)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 1
            triangle.index1 = baseIx + 2
            triangle.index2 = baseIx + 3
            ro.triangles.append(triangle)
            baseIx += 2
            startValue = endValue
            startColor = endColor

    def MakeSegmentedRectangle(self, segments, tex):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        self.texture = tex
        width = tex.atlasTexture.width
        height = tex.atlasTexture.height
        step = float(width) / float(segments)
        ustep = 1.0 / float(segments)
        x = 0.0
        u = 0.0
        yTop = 0.0
        yBottom = float(height)
        vTop = 0.0
        vBottom = 1.0
        color = (1, 1, 1, 1)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = (x, yTop)
        vertex.color = color
        vertex.texCoord0 = (u, vTop)
        vertex.texCoord1 = (u, vTop)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = (x, yBottom)
        vertex.color = color
        vertex.texCoord0 = (u, vBottom)
        vertex.texCoord1 = (u, vBottom)
        ro.vertices.append(vertex)
        baseIx = 0
        for i in xrange(segments):
            x += step
            u += ustep
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = (x, yTop)
            vertex.color = color
            vertex.texCoord0 = (u, vTop)
            vertex.texCoord1 = (u, vTop)
            ro.vertices.append(vertex)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = (x, yBottom)
            vertex.color = color
            vertex.texCoord0 = (u, vBottom)
            vertex.texCoord1 = (u, vBottom)
            ro.vertices.append(vertex)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 0
            triangle.index1 = baseIx + 1
            triangle.index2 = baseIx + 2
            ro.triangles.append(triangle)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 1
            triangle.index1 = baseIx + 2
            triangle.index2 = baseIx + 3
            ro.triangles.append(triangle)
            baseIx += 2