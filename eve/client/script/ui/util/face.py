import sys
import facelib
import blue
import log
import os.path
import uthread
import math
import trinity
logging = 0
eyeLocations = {}
eyeVertices = {'aaf01': [79, 160],
 'aam01': [2095, 2176],
 'anf01': [63, 155],
 'anm01': [44, 128],
 'ccf01': [81, 173],
 'ccm01': [153, 43],
 'cdf01': [83, 167],
 'cdm01': [2083, 2136],
 'ggf01': [110, 261],
 'ggm01': [44, 137],
 'gif01': [86, 238],
 'gim01': [3546, 3651],
 'mbf01': [65, 139],
 'mbm01': [2197, 2132],
 'msf01': [77, 154],
 'msm01': [51, 150],
 'jmm01': [4691, 4620],
 'cam01': [4195, 4181],
 'caf01': [5296, 5385],
 'mvf01': [6737, 6596],
 'akf01': [8538, 8473],
 'mvf01': [7249, 7102],
 'gjf01': [7699, 7818],
 'caf01': [8772, 8491],
 'mvm01': [7289, 7471],
 'cam01': [7880, 7550],
 'gjm01': [9388, 9087],
 'akm01': [8658, 8879]}
morphingReady = ('msf',
 'msm',
 'mbf',
 'mbm',
 'ccf',
 'ccm',
 'cdf',
 'cdm',
 'aaf',
 'aam',
 'anm',
 'anf',
 'ggf',
 'ggm',
 'gif',
 'gim',
 'jmm',
 'cam',
 'caf',
 'mvm',
 'mvf',
 'akm',
 'akf',
 'gjm',
 'gjf')
allOptions = ['skins',
 'eyes',
 'eyebrows',
 'makeups',
 'lipsticks',
 'decos',
 'hairs',
 'beards',
 'accessories',
 'costumes',
 'lights',
 'backgrounds']
stems = ['skin',
 'eyes',
 'eyebrows',
 'makeup',
 'lipstick',
 'deco',
 'hair',
 'beard',
 'accessory',
 'costume',
 'light',
 'background']

def GetRotationAxes():
    return {'default': (trinity.TriVector(0.0, -0.7, 0.5),
                 trinity.TriVector(0.0, -0.1, 0.4),
                 0.7,
                 0.8),
     'gjf': (trinity.TriVector(0.0, 3.49, 0.5),
             trinity.TriVector(0.0, 3.45, 0.4),
             0.7,
             0.6),
     'caf': (trinity.TriVector(0.0, -0.7, 0.5),
             trinity.TriVector(0.0, -0.6, 0.4),
             0.7,
             1.0),
     'akf': (trinity.TriVector(0.0, -0.7, 0.5),
             trinity.TriVector(0.0, -1.0, 0.0),
             0.7,
             0.6),
     'mvf': (trinity.TriVector(0.0, -0.7, 0.5),
             trinity.TriVector(0.0, -0.1, 0.4),
             0.7,
             0.6),
     'mvm': (trinity.TriVector(0.0, -0.3, 0.5),
             trinity.TriVector(0.0, -0.1, 0.4),
             0.7,
             0.8),
     'akm': (trinity.TriVector(0.0, -12.3, 5.7),
             trinity.TriVector(0.0, -12.3, 8.0),
             0.7,
             6.0),
     'gjm': (trinity.TriVector(0.0, -12.3, 5.7),
             trinity.TriVector(0.0, -12.3, 8.0),
             0.7,
             8.0),
     'cam': (trinity.TriVector(0.0, -0.3, 0.5),
             trinity.TriVector(0.0, -0.1, 0.4),
             0.7,
             0.7)}



def GetRot():
    try:
        return eve.rot
    except NameError:
        sys.exc_clear()
        return blue.os.CreateInstance('blue.Rot')



def GetDev():
    try:
        return trinity.device
    except NameError:
        sys.exc_clear()
        return GetRot().GetInstance('tri:/dev')



def FindModel(name, lst = None):
    if lst is None:
        lst = GetDev().scene.models
    for each in lst:
        if each.name == name:
            return each
        ret = FindModel(name, getattr(each, 'children', []))
        if ret:
            return ret




class CharAppearance():
    __guid__ = 'util.CharAppearance'

    def __init__(self, bloodlineID, genderID, appearance = None, animate = 0, morphing = 1):
        self.Reset()
        bloodline = sm.GetService('cc').GetData('bloodlines', ['bloodlineID', bloodlineID])
        race = sm.GetService('cc').GetData('races', ['raceID', bloodline.raceID])
        self.path = '/'.join((race.raceName, bloodline.bloodlineName.replace('-', ''), ('female', 'male')[genderID]))
        self.tla = ''.join([ each[0].lower() for each in self.path.split('/') ])
        self.path = unicode(self.path)
        self.tla = unicode(self.tla)
        self.appear = {}
        self.LoadCharScene()
        self.scene.display = 0
        self.LoadModel()
        self.InitOptionDestinations()
        if morphing:
            if appearance:
                self.InitMorphing((animate, appearance))
            else:
                self.InitMorphing()
        self.animate = animate
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.lightSemaphore = uthread.Semaphore('face')
        if appearance:
            self.LoadAppearance(appearance)
        if morphing:
            self.UpdateModels()
        self.scene.display = 1



    def Reset(self):
        self.animate = None
        self.yaw = None
        self.pitch = None
        self.roll = None
        self.morphEnabled = None
        self.path = None
        self.tla = None
        self.appear = None
        self.lightSemaphore = None
        self.leftEye = None
        self.rightEye = None
        self.morphModels = None
        self.costume = None
        self.hair = None
        self.head = None
        self.accessories = None
        self.background = None
        self.scene = None
        self.planePosition = None
        self.rotationAxis = None
        self.planeTilt = None
        self.planeSmoothing = None
        self.cameraYaw = 0.0
        self.cameraPitch = 0.0



    def LoadAppearance(self, appearance):
        rotations = ('camPos', 'headRotation', 'eyeRotation')
        for (k, v,) in appearance.iteritems():
            if k[:-1] not in rotations:
                self[k] = v

        for each in rotations:
            ypr = [ appearance[(each + n)] for n in ('1', '2', '3') ]
            if None not in ypr:
                getattr(self, 'Set_%s' % each)(*ypr)

        if self.morphEnabled:
            for k in appearance:
                if k.startswith('morph'):
                    self.ApplyMorph(immediate=1)
                    return 




    def AsDict(self):
        ret = self.appear.copy()
        for (n, v,) in zip(('1', '2', '3'), (self.cameraYaw, self.cameraPitch, 0.0)):
            ret['camPos%s' % n] = v

        for (n, v,) in zip(('1', '2', '3'), self.leftEye.rotation.GetYawPitchRoll()):
            ret['eyeRotation%s' % n] = v

        headRotation = trinity.TriQuaternion()
        headRotation.SetYawPitchRoll(self.yaw, self.pitch, self.roll)
        for (n, v,) in zip(('1', '2', '3'), headRotation.GetYawPitchRoll()):
            ret['headRotation%s' % n] = v

        return ret



    def Morph(self, morphX, morphY, area):
        (dirX, cancelX,) = ('ns'[(morphX > 0)], 'ns'[(not morphX > 0)])
        (dirY, cancelY,) = ('we'[(morphY > 0)], 'we'[(not morphY > 0)])
        for (model, tag,) in self.morphModels:
            blendNameX = dirX + unicode(area)
            cancelNameX = cancelX + unicode(area)
            model.SetBlend(blendNameX, abs(morphX))
            model.SetBlend(cancelNameX, 0.0)
            blendNameY = dirY + unicode(area)
            cancelNameY = cancelY + unicode(area)
            model.SetBlend(blendNameY, abs(morphY))
            model.SetBlend(cancelNameY, 0.0)

        self.appear['morph%s%s' % (area, dirX)] = abs(morphX)
        if 'morph%s%s' % (area, cancelX) in self.appear:
            del self.appear['morph%s%s' % (area, cancelX)]
        self.appear['morph%s%s' % (area, dirY)] = abs(morphY)
        if 'morph%s%s' % (area, cancelY) in self.appear:
            del self.appear['morph%s%s' % (area, cancelY)]



    def ApplyMorph(self, steps = 1, immediate = 0):
        for (each, tag,) in self.morphModels:
            if immediate:
                each.ApplyBlendsLinear(1)
            elif steps == 1:
                uthread.new(each.ApplyBlendsLinear, steps)
            else:
                uthread.new(each.ApplyBlendsSmooth, steps)




    def UpdateModels(self):
        times = []
        for (each, tag,) in self.morphModels:
            times.append((blue.os.GetTime(1), 'start morphing ' + each.name))
            if not each.object.vertexRes.vertexBuffer:
                each.object.PrepareTriModel(1)
                continue
            each.CheckIfInvalidated()
            each.object.vertexRes.vertexBuffer.LockBuffer(1)
            times.append((blue.os.GetTime(1), 'locked buffer'))
            each.UpdateModel()
            times.append((blue.os.GetTime(1), 'updated model'))
            each.SetSnaplistPosition()
            times.append((blue.os.GetTime(1), 'set snaplist'))
            each.rotationDeform.SetYawPitchRoll(self.yaw, self.pitch, self.roll)
            balls = self.GetEyes()
            for ball in balls:
                (yaw, pitch, roll,) = ball.rotation.GetYawPitchRoll()
                ball.rotation.SetYawPitchRoll(yaw, pitch, roll)
                times.append((blue.os.GetTime(1), 'set eye rotation'))

            each.Rotate()
            times.append((blue.os.GetTime(1), 'rotate'))
            each.object.vertexRes.vertexBuffer.FlushBuffer()
            times.append((blue.os.GetTime(1), 'flushed buffer'))
            each.RotateSnaplistPosition()
            times.append((blue.os.GetTime(1), 'rotated snaplist'))

        for each_guy in [self.costume, self.hair]:
            if len(each_guy.children) > 0:
                times.append((blue.os.GetTime(1), 'start ' + each_guy.name))
                child = each_guy.children[0]
                child.CheckIfInvalidated()
                child.rotationDeform.SetYawPitchRoll(self.yaw, self.pitch, self.roll)
                child.LockBuffer(1)
                times.append((blue.os.GetTime(1), 'lock buffer'))
                child.Clone()
                times.append((blue.os.GetTime(1), 'clone'))
                child.Rotate()
                times.append((blue.os.GetTime(1), 'rotate'))
                child.FlushBuffer()
                times.append((blue.os.GetTime(1), 'flush buffer'))

        if len(self.accessories.children) > 0:
            times.append((blue.os.GetTime(1), 'start accessory'))
            child = self.accessories.children[0]
            head = self.head.children[0]
            t = head.rotationAxis.CopyTo()
            t.x = t.x * head.scaling.x
            t.y = t.y * head.scaling.y
            t.z = t.z * head.scaling.z
            child.translation = -head.translation - t
            child.translation.TransformQuaternion(each.rotationDeform)
            child.translation = child.translation + head.translation + t
            child.rotation = each.rotationDeform
            times.append((blue.os.GetTime(1), 'end accessory'))
        wastime = times[0][0]
        starttime = wastime
        if logging == 1:
            for (time, description,) in times:
                deltatime = float(time - wastime) / 1000000.0
                log.general.Log(description + ' -> ' + str(deltatime))
                wastime = time

            totaltime = float(time - starttime) / 1000000.0
            log.general.Log('__----------------- TOTAL ' + str(totaltime) + ' --------------')



    def GetEyes(self):
        return (self.leftEye, self.rightEye)



    def __setitem__(self, key, value):
        try:
            self.DoSetItem(key, value)
        except blue.error:
            log.LogException(channel='uix', toMsgWindow=0)
            sys.exc_clear()



    def DoSetItem(self, key, value):
        self.appear[key] = value
        if type(value) in (list, tuple) and map(type, value) == (float, float, float):
            self.appear[key + '1'] = value[0]
            self.appear[key + '2'] = value[1]
            self.appear[key + '3'] = value[2]
        if value is None:
            return 
        if key.endswith('ID') and key != 'typeID':
            name = sm.GetService('cc').GetCharAppearanceInfo()[key[:-2]][value]
            key = key[:-2]
        if key == 'light':
            try:
                self.LoadLights(GetRot().GetCopy(str('res:/Model/Face/SceneOptions/Lights/' + name + '/default.blue')))
            except blue.error:
                try:
                    self.LoadLights(GetRot().GetCopy(str('res:/Model/Face/' + self.path + '/face/Lights/' + name + '/default.blue')))
                except blue.error:
                    log.LogException(channel='uix', toMsgWindow=0)
                sys.exc_clear()
            return 
        if key == 'background':
            del self.background.children[:]
            bookmarkPath = str('res:/Model/Face/SceneOptions/Background/' + name + '/default.blue')
            try:
                background = GetRot().GetCopy(bookmarkPath)
            except:
                log.LogTraceback("Can't find character creation bookmark " + bookmarkPath)
                sys.exc_clear()
                return 
            background.translation.z = 200.0
            background.pickable = 0
            sx = max(180.0, background.scaling.x)
            diff = sx / background.scaling.x
            background.scaling.x = sx
            background.scaling.z = background.scaling.z * diff
            self.background.children.append(background)
            return 
        if key in ('hair', 'accessories', 'costume', 'accessory'):
            if key == 'accessory':
                key = 'accessories'
            lst = getattr(self, key).children
            del lst[:]
            bookmarkPath = '/'.join(('res:/Model/Face',
             self.path,
             'face',
             key,
             name,
             'default.blue'))
            try:
                tmp = GetRot().GetCopy(str(bookmarkPath))
            except:
                log.LogTraceback("Can't find character creation bookmark " + bookmarkPath)
                sys.exc_clear()
                return 
            tmp.pickable = 0
            for shader in tmp.Find('trinity.TriShader'):
                isTransparent = 0
                for renderpass in shader.passes:
                    if renderpass.blendOp == trinity.TRIBLENDOP_DISABLE:
                        continue
                    if renderpass.dstBlend != trinity.TRIBLEND_ZERO:
                        isTransparent = 1

                if isTransparent == 1:
                    if shader.opaque != 0:
                        shader.opaque = 0

            rotationVictim = facelib.RotationVictim()
            if key == 'costume':
                rotationVictim.Init(tmp, 0)
            else:
                rotationVictim.Init(tmp)
            rotationVictim.face = self.head.children[0]
            if self.tla in GetRotationAxes():
                (rotationVictim.planePosition, rotationVictim.rotationAxis, rotationVictim.planeTilt, rotationVictim.planeSmoothing,) = GetRotationAxes()[self.tla]
            else:
                (rotationVictim.planePosition, rotationVictim.rotationAxis, rotationVictim.planeTilt, rotationVictim.planeSmoothing,) = GetRotationAxes()['default']
            nullV = trinity.TriVector()
            nullR = trinity.TriQuaternion()
            headTransform = trinity.TriSplTransform()
            targetTransform = trinity.TriSplTransform()
            headTransform.scaling = rotationVictim.face.scaling
            headTransform.translation = rotationVictim.face.translation
            targetTransform.scaling = rotationVictim.scaling
            targetTransform.translation = rotationVictim.translation
            headTransform.Update(blue.os.GetTime())
            targetTransform.Update(blue.os.GetTime())
            headTransformMTR = headTransform.localTransform.CopyTo()
            targetTransformMTR = targetTransform.localTransform.CopyTo()
            targetTransformMTR.Inverse()
            headTransformMTR.Multiply(targetTransformMTR)
            rotationVictim.planePosition.TransformCoord(headTransformMTR)
            rotationVictim.rotationAxis.TransformCoord(headTransformMTR)
            lst.append(rotationVictim)
            return 
        if key.startswith('morph'):
            if self.morphEnabled:
                for (model, tag,) in self.morphModels:
                    path = '%s%s' % (key[-1], key[-2])
                    model.SetBlend(path, float(value))

            return 
        if key in stems:
            bookmarkPath = '/'.join(('res:/Model/Face',
             self.path,
             'face',
             key,
             name,
             'default.blue'))
            try:
                stuff = GetRot().GetCopy(str(bookmarkPath))
            except:
                log.LogTraceback("Can't find character creation bookmark " + bookmarkPath)
                sys.exc_clear()
                return 
            facelib.setDirAttrib2((key, name), [ each for each in stuff.children ], self.optionDestinations)



    def Set_eyeRotation(self, *value):
        for each in (self.leftEye, self.rightEye):
            each.rotation.SetYawPitchRoll(*value)




    def Set_camPos(self, yaw, pitch, roll):
        yawQ = trinity.TriQuaternion()
        pitchQ = trinity.TriQuaternion()
        yawQ.SetYawPitchRoll(yaw, 0.0, 0.0)
        pitchQ.SetYawPitchRoll(0.0, pitch, 0.0)
        cameraYaw = self.cameraYaw
        cameraPitch = self.cameraPitch
        for model in self.scene.models:
            if model.name == 'background':
                continue
            model.rotation.SetYawPitchRoll(0.0, 0.0, 0.0)
            model.rotation.Multiply(yawQ)
            model.rotation.Multiply(pitchQ)




    def Set_headRotation(self, yaw, pitch, roll):
        headRotation = trinity.TriQuaternion()
        headRotation.SetYawPitchRoll(yaw, pitch, roll)
        (yaw, pitch, roll,) = headRotation.GetYawPitchRoll()
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll



    def LoadCharScene(self):
        scene = trinity.Load('res:/Model/Face/facescene.red')
        self.scene = scene
        self.camera = scene.camera



    def LoadModel(self):
        for model in self.scene.models:
            if model.name == '__head__':
                self.head = model
                del model.children[:]
            elif model.name == '__hair__':
                self.hair = model
                del model.children[:]
            elif model.name == '__accessories__':
                self.accessories = model
                del model.children[:]
            elif model.name == 'background':
                self.background = model
                del model.children[:]
            elif model.name == '__costume__':
                self.costume = model
                del model.children[:]

        try:
            head = GetRot().GetCopy('res:/Model/Face/' + self.path + '/face/' + self.tla + '01.blue')
        except:
            log.LogException('Model not found  res:/Model/Face/' + self.path + '/face/' + self.tla + '01.blue')
            self.path = 'Amarr/amarr/female'
            self.tla = 'aaf'
            head = GetRot().GetCopy('res:/Model/Face/Amarr/amarr/female/face/aaf01.blue')
            sys.exc_clear()
        head.pickable = 0
        self.head.children.append(head)
        (self.leftEye, self.rightEye,) = (FindModel('eye_l', head.children), FindModel('eye_r', head.children))



    def InitOptionDestinations(self):
        locs = []
        for type_ in ('TriTexture', 'TriPass', 'TriMaterial'):
            locs.extend(self.head.Find('trinity.%s' % type_))

        self.optionDestinations = locs



    def InitMorphing(self, args = None):
        if args:
            (animate, appearance,) = args
        else:
            animate = None
            appearance = None
        self.morphEnabled = 0
        if self.tla not in morphingReady:
            print 'not ready'
            return 
        self.morphModels = []
        for (model, tag, snapList, parent,) in [(FindModel('eyelashes', self.head.children[0].children),
          'eyelashes',
          [],
          self.head.children[0]), (self.head.children[0],
          '%s01_blend' % self.tla,
          self.GetEyeSnapList(),
          self.head)]:
            if model == None:
                continue
            if tag == 'eyelashes':
                model.display = 0
                continue
            tmp = 'res:/Model/Face/%s/face/%s_' % (self.path, tag)
            vertexPaths = [ '%s%s' % (dir_, num) for num in xrange(1, 5) for dir_ in 'wens' ]
            if animate == 0:
                newVertexPaths = []
                morphKeys = []
                for key in appearance.iterkeys():
                    if key[:5] == 'morph':
                        morphKeys.append(key[-2:])

                for vertexPath in vertexPaths:
                    if vertexPath[-12:][:2] in morphKeys:
                        newVertexPaths.append(vertexPath)

                if len(newVertexPaths):
                    vertexPaths = newVertexPaths
                vertexPaths = newVertexPaths
            newmodel = facelib.MorphTarget()
            if self.tla in GetRotationAxes():
                (self.planePosition, self.rotationAxis, self.planeTilt, self.planeSmoothing,) = GetRotationAxes()[self.tla]
            else:
                (self.planePosition, self.rotationAxis, self.planeTilt, self.planeSmoothing,) = GetRotationAxes()['default']
            newmodel.planePosition = self.planePosition
            newmodel.rotationAxis = self.rotationAxis
            newmodel.planeTilt = self.planeTilt
            newmodel.planeSmoothing = self.planeSmoothing
            (newmodel.translation, newmodel.scaling,) = (model.translation, model.scaling)
            for each in model.children[:]:
                model.children.remove(each)
                newmodel.children.append(each)

            blendShapeBufferPath = 'res:/Model/Face/' + self.path + '/face/' + self.tla + '01_blend_vb.blue'
            newmodel.Initalize(model.object, vertexPaths, blendShapeBufferPath, snapList)
            parent.children.remove(model)
            parent.children.append(newmodel)
            self.morphModels.append((newmodel, tag))

        if len(self.morphModels) > 1:
            if self.morphModels[1][0].valid:
                if not self.morphModels[0][0].valid:
                    self.morphModels[0][0].display = 0
            else:
                return 
        self.morphEnabled = 1



    def GetEyeSnapList(self):
        if self.tla + '01' not in eyeVertices:
            log.LogException('Missing eye vertices %s%s' % (self.tla, '01'))
        (rightVertexID, leftVertexID,) = eyeVertices.get(self.tla + '01', [0, 0])
        if self.tla in eyeLocations.keys():
            return [(self.leftEye, eyeLocations[self.tla][0], eyeLocations[self.tla][1]), (self.rightEye, eyeLocations[self.tla][2], eyeLocations[self.tla][3])]
        self.head.children[0].object.PrepareTriModel(1)
        vb = self.head.children[0].object.vertexRes.vertexBuffer
        vb.LockBuffer()
        lv = vb.GetVertexElementData(leftVertexID, trinity.TRIVSDE_POSITION)
        rv = vb.GetVertexElementData(rightVertexID, trinity.TRIVSDE_POSITION)
        if self.leftEye:
            deltaTrans1 = self.leftEye.translation - trinity.TriVector(*lv)
        else:
            deltaTrans1 = trinity.TriVector()
        if self.rightEye:
            deltaTrans2 = self.rightEye.translation - trinity.TriVector(*rv)
        else:
            deltaTrans2 = trinity.TriVector()
        eyeLocations[self.tla] = (leftVertexID,
         deltaTrans1,
         rightVertexID,
         deltaTrans2)
        return [(self.leftEye, eyeLocations[self.tla][0], eyeLocations[self.tla][1]), (self.rightEye, eyeLocations[self.tla][2], eyeLocations[self.tla][3])]



    def LoadLights(self, lights):
        if lights.__typename__ == 'List':
            litez = lights
        elif lights.__typename__ == 'TriRenderObjectList':
            litez = lights.children
        elif lights.__typename__ == 'TriLight':
            litez = [lights]
        else:
            raise RuntimeError('Dunno this!', lights.__typename__)
        self.litezinited = getattr(self, 'litezinited', 0) + 1
        if self.animate:
            uthread.new(self.LightTransition, litez)
        else:
            del self.scene.lights[:]
            for each in litez:
                self.scene.lights.append(each)




    def LightTransition(self, new):
        self.lightSemaphore.claim()
        try:
            me = self.currentLightAnim = uthread.uniqueId() or uthread.uniqueId()

        finally:
            self.lightSemaphore.release()

        lights = sm.GetService('sceneManager').GetRegisteredScene(None, defaultOnActiveScene=True).lights
        old = lights[:]
        startTime = blue.os.GetTime()
        totalTime = 1000.0
        endTime = startTime + totalTime
        out = [ (each,
         (each.ambient.r, each.ambient.g, each.ambient.b),
         (each.diffuse.r, each.diffuse.g, each.diffuse.b),
         (each.specular.r, each.specular.g, each.specular.b)) for each in old ]
        in_ = [ (each,
         (each.ambient.r, each.ambient.g, each.ambient.b),
         (each.diffuse.r, each.diffuse.g, each.diffuse.b),
         (each.specular.r, each.specular.g, each.specular.b)) for each in new ]
        self.lightSemaphore.claim()
        if self.currentLightAnim == me:
            for each in new:
                lights.append(each)

        while self.currentLightAnim == me:
            time = blue.os.TimeDiffInMs(startTime)
            portion = min(1.0, time / totalTime)
            pr = pow(math.sin(math.pi / 2 * portion), 2.0)
            for (light, am, df, sp,) in in_:
                light.diffuse.SetRGB(*[ min(1.0, each * pr) for each in df ])
                light.ambient.SetRGB(*[ min(1.0, each * pr) for each in am ])
                light.specular.SetRGB(*[ min(1.0, each * pr) for each in sp ])

            for (light, am, df, sp,) in out:
                light.diffuse.SetRGB(*[ max(0.0, each * (1.0 - pr)) for each in df ])
                light.ambient.SetRGB(*[ max(0.0, each * (1.0 - pr)) for each in am ])
                light.specular.SetRGB(*[ max(0.0, each * (1.0 - pr)) for each in sp ])

            if portion >= 1.0:
                for each in old:
                    if each in lights:
                        lights.remove(each)

                self.currentLightAnim = None
            blue.pyos.synchro.Sleep(1)

        self.lightSemaphore.release()



exports = {'chapp.allOptions': allOptions,
 'chapp.stems': stems,
 'chapp.CharAppearance': CharAppearance}

