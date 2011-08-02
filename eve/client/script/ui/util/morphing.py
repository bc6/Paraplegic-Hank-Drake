import blue
import bluepy
import uthread
import random
import base
import log

class RotationVictim(bluepy.WrapBlueClass('trinity.TriTransform')):
    __guid__ = 'facelib.RotationVictim'
    __persistvars__ = ['rotationDeform',
     'planePosition',
     'rotationAxis',
     'planeTilt',
     'planeSmoothing',
     'baseBuffer',
     'rotateChildren',
     'mode',
     'vx',
     'face']

    def Init(self, model, rotateChildren = 1):
        import trinity
        self.rotateChildren = rotateChildren
        self.translation = model.translation.CopyTo()
        self.rotation = model.rotation.CopyTo()
        self.scaling = model.scaling.CopyTo()
        self.object = model.object
        self.pickable = 0
        self.sorted = 0
        self.face = None
        self.vx = None
        if model.object:
            model.object.PrepareTriModel(1)
            if model.object.vertexRes:
                if model.object.vertexRes.vertexBuffer:
                    self.baseBuffer = model.object.vertexRes.vertexBuffer.CopyTo()
                    self.vx = model.object.vertexRes.vertexBuffer
                    self.baseBuffer.LockBuffer()
        childowner = trinity.TriTransform()
        childowner.sorted = 0
        childowner.name = model.name
        for child in model.children:
            childowner.children.append(child)

        if len(childowner.children) > 0:
            self.children.append(childowner)
        self.rotationDeform = trinity.TriQuaternion()
        self.planePosition = trinity.TriVector(0.0, -0.7, 0.5)
        self.rotationAxis = trinity.TriVector(0.0, -0.1, 0.4)
        self.planeTilt = 0.7
        self.planeSmoothing = 1.0



    def CheckIfInvalidated(self):
        if self.vx:
            vx = self.object.vertexRes.vertexBuffer
            if vx != self.vx:
                vx = self.vx
                self.object.vertexRes.vertexBuffer = vx



    def Clone(self):
        if self.vx:
            self.vx.Clone(self.baseBuffer)



    def LockBuffer(self, discard = 0):
        if self.vx:
            self.vx.LockBuffer(discard)



    def FlushBuffer(self):
        if self.vx:
            self.vx.FlushBuffer()



    def Rotate(self):
        if self.vx:
            self.vx.RotateAboveSoftPlane(self.planePosition, self.planeTilt, self.planeSmoothing, self.rotationDeform, self.rotationAxis)
        if self.face and len(self.children) > 0 and self.rotateChildren == 1:
            child = self.children[0]
            head = self.face
            t = self.rotationAxis.CopyTo()
            child.translation = -t
            child.translation.TransformQuaternion(self.rotationDeform)
            child.translation = child.translation + t
            child.rotation = self.rotationDeform




class MorphTarget(bluepy.WrapBlueClass('trinity.TriTransform')):
    __guid__ = 'facelib.MorphTarget'
    __persistvars__ = ['targetWeights',
     'vertices',
     'currentWeights',
     'snapList',
     'valid',
     'baseModel',
     'valueCurves',
     'yawCurve',
     'pitchCurve',
     'rotationDeform',
     'planePosition',
     'rotationAxis',
     'planeTilt',
     'planeSmoothing',
     'storedSnapListTranslation']

    def Initalize(self, model, vertexPaths, blendShapeBufferPath, snapList = []):
        import trinity
        name = model.name
        self.object = model
        self.vertices = {}
        self.targetWeights = {}
        self.valueCurves = {}
        self.currentWeights = {}
        model.PrepareTriModel(1)
        model.vertexRes.vertexBuffer = blue.os.LoadObject(blendShapeBufferPath)
        vx = model.vertexRes.vertexBuffer
        self.vx = vx
        self.storedSnapListTranslation = {}
        self.snapList = snapList
        self.rotationDeform = trinity.TriQuaternion()
        for vertexPath in vertexPaths:
            self.vertices[vertexPath] = None
            self.targetWeights[vertexPath] = 0.0
            self.currentWeights[vertexPath] = 0.0
            self.valueCurves[vertexPath] = trinity.TriScalarCurve()
            self.valueCurves[vertexPath].extrapolation = trinity.TRIEXT_CONSTANT
            self.valueCurves[vertexPath].value = 0.0

        self.valid = 1
        numbers = ['1',
         '2',
         '3',
         '4']
        directions = ['e',
         'w',
         's',
         'n']
        self.morphNameToID = {}
        c = 0
        for n in numbers:
            for d in directions:
                self.morphNameToID[d + n] = c
                c += 1





    def SetBlend(self, vertexPath, value):
        if not self.valid:
            return 
        self.targetWeights[vertexPath] = value



    def CheckIfInvalidated(self):
        vx = self.object.vertexRes.vertexBuffer
        if vx != self.vx:
            vx = self.vx
            self.object.vertexRes.vertexBuffer = vx



    def UpdateModel(self):
        vx = self.object.vertexRes.vertexBuffer
        if vx != self.vx:
            vx = self.vx
            self.object.vertexRes.vertexBuffer = vx
            print 'force updated vertexbuffer of ',
            print self.name
        now = blue.os.GetTime(0)
        for vertexPath in self.targetWeights.keys():
            w = self.valueCurves[vertexPath].GetScalarAt(now)
            targetID = self.morphNameToID[vertexPath]
            vx.SetTargetWeight(targetID, w)

        vx.ApplyMorph()



    def SetSnaplistPosition(self):
        import trinity
        vx = self.object.vertexRes.vertexBuffer
        for (transform, vertexID, offset,) in self.snapList:
            p1 = vx.GetVertexElementData(vertexID, trinity.TRIVSDE_POSITION)
            self.storedSnapListTranslation[transform] = trinity.TriVector(p1[0], p1[1], p1[2]) + offset




    def RotateSnaplistPosition(self):
        for (transform, vertexID, offset,) in self.snapList:
            translation = self.storedSnapListTranslation[transform]
            translation = translation - self.rotationAxis
            translation.TransformQuaternion(self.rotationDeform)
            translation = translation + self.rotationAxis
            transform.translation = translation




    def ApplyBlendsLinear(self, steps = 1, rotationVictims = []):
        import trinity
        if steps == 1:
            self.object.PrepareTriModel(0)
            vx = self.object.vertexRes.vertexBuffer
            for key in self.targetWeights.iterkeys():
                valueCurve = trinity.TriScalarCurve()
                valueCurve.value = self.targetWeights[key]
                valueCurve.extrapolation = trinity.TRIEXT_CONSTANT
                valueCurve.start = blue.os.GetTime()
                self.valueCurves[key] = valueCurve

        else:
            self.ApplyBlendsSmooth(steps, trinity.TRIINT_LINEAR)



    def ApplyBlendsSmooth(self, steps = 1, rotationVictims = [], interpolation = None):
        import trinity
        if interpolation is None:
            interpolation = trinity.TRIINT_HERMITE
        if not self.valid:
            return 
        vx = self.object.vertexRes.vertexBuffer
        now = blue.os.GetTime()
        maxlen = 0.0
        for key in self.targetWeights.iterkeys():
            valueCurve = trinity.TriScalarCurve()
            valueCurve.AddKey(0.0, self.valueCurves[key].GetScalarAt(now), 0.0, 0.0, interpolation)
            timeLength = random.random() * 0.3 + 0.4
            maxlen = max(maxlen, timeLength)
            valueCurve.AddKey(timeLength, self.targetWeights[key], 0.0, 0.0, interpolation)
            valueCurve.Sort()
            valueCurve.extrapolation = trinity.TRIEXT_CONSTANT
            valueCurve.start = blue.os.GetTime()
            self.valueCurves[key] = valueCurve




    def Rotate(self):
        vx = self.object.vertexRes.vertexBuffer
        vx.RotateAboveSoftPlane(self.planePosition, self.planeTilt, self.planeSmoothing, self.rotationDeform, self.rotationAxis)



exports = {'facelib.MorphTarget': MorphTarget,
 'facelib.RotationVictim': RotationVictim}

