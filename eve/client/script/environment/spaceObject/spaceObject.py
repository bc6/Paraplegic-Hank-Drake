import blue
import bluepy
import sys
import timecurves
import uthread
import trinity
import destiny
import random
import log
import uix
import types
import audio2
import geo2
import util
from foo import Vector3
import linalg
from math import sin, cos, tan, sqrt, pow
import locks
from string import split
DEG2RAD = 0.0174532925199

class SpaceObject(bluepy.WrapBlueClass('destiny.ClientBall')):
    __guid__ = 'spaceObject.SpaceObject'
    __persistdeco__ = 0
    __update_on_reload__ = 1

    def __init__(self):
        self.explodeOnRemove = False
        self.exploded = False
        self.model = None
        self.released = False
        self.forceLOD = False
        self.wreckID = None
        self.audioEntities = []
        self.generalAudioEntity = None
        self.boosterAudioEvent = ''
        self.audioPumpStarted = False
        self.logChannel = log.GetChannel(self.__guid__)
        self.modelLoadedEvent = locks.Event()
        self.explosionModel = None



    def Log(self, channelID, *args, **keywords):
        if self.logChannel.IsOpen(channelID):
            try:
                self.logChannel.Log(' '.join(map(strx, args)), channelID, keywords.get('backtrace', 1))
            except TypeError:
                self.logChannel.Log('[X]'.join(map(strx, args)).replace('\x00', '\\0'), channelID, keywords.get('backtrace', 1))
                sys.exc_clear()



    def LogInfo(self, *args, **keywords):
        self.Log(1, '[', self.id, ']', *args, **keywords)



    def LogWarn(self, *args, **keywords):
        self.Log(2, '[', self.id, ']', *args, **keywords)



    def LogError(self, *args, **keywords):
        self.Log(4, '[', self.id, ']', *args, **keywords)



    def Prepare(self, spaceMgr):
        self.spaceMgr = spaceMgr
        self.LoadModel()
        self.Assemble()



    def GetTrinityVersionFilename(self, fileName):
        return fileName.replace(':/Model', ':/dx9/Model').replace('.blue', '.red')



    def HasBlueInterface(self, object, interfaceName):
        if hasattr(object, 'TypeInfo'):
            return interfaceName in object.TypeInfo()[1]
        return False



    def GetModel(self):
        if not self.model:
            self.modelLoadedEvent.wait()
        return self.model



    def LoadModel(self, fileName = None, useInstance = False, loadedModel = None):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if useInstance:
            if slimItem is not None:
                self.LogError('Object of type:', slimItem.typeID, 'was trying to useInstance in spaceObject.LoadModel')
        if fileName is None and loadedModel is None:
            if slimItem is None:
                return 
            if cfg.invtypes.Get(slimItem.typeID).graphicID is not None:
                if type(cfg.invtypes.Get(slimItem.typeID).graphicID) != type(0):
                    raise RuntimeError('NeedGraphicIDNotMoniker', slimItem.itemID)
                if cfg.invtypes.Get(slimItem.typeID).Graphic():
                    fileName = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
                    if not (fileName.lower().endswith('.red') or fileName.lower().endswith('.blue')):
                        filename_and_turret_type = split(fileName, ' ')
                        fileName = filename_and_turret_type[0]
        self.LogInfo('LoadModel', fileName)
        if fileName is None and loadedModel is None:
            self.LogError('Error: Object type %s has invalid graphicFile, using graphicID: %s' % (slimItem.typeID, cfg.invtypes.Get(slimItem.typeID).graphicID))
            return 
        model = None
        if fileName is not None and len(fileName) and loadedModel is None:
            tryFileName = self.GetTrinityVersionFilename(fileName)
            if tryFileName is not None:
                try:
                    model = blue.os.LoadObject(tryFileName)
                except:
                    model = None
                    sys.exc_clear()
                if model is None:
                    self.LogError('Was looking for:', tryFileName, 'but it does not exist!')
            if model is None:
                try:
                    model = blue.os.LoadObject(fileName)
                except:
                    model = None
                    sys.exc_clear()
        else:
            model = loadedModel
        if not model:
            log.LogError('Could not load model for spaceobject. FileName:', fileName, ' id:', self.id, ' typeID:', getattr(slimItem, 'typeID', '?'))
            if slimItem is not None and hasattr(slimItem, 'typeID'):
                log.LogError('Type is:', cfg.invtypes.Get(slimItem.typeID).typeName)
            return 
        self.model = model
        if not hasattr(model, 'translationCurve'):
            self.LogError('LoadModel - Model in', fileName, "doesn't have a translationCurve.")
        else:
            model.translationCurve = self
            model.rotationCurve = self
        model.name = '%d' % self.id
        if hasattr(model, 'useCurves'):
            model.useCurves = 1
        self.model.display = 0
        if self.model is not None and self.HasBlueInterface(self.model, 'IEveSpaceObject2'):
            scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
            scene2.objects.append(self.model)
        else:
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.models.append(self.model)
        sm.StartService('FxSequencer').NotifyModelLoaded(self.id)
        self.modelLoadedEvent.set()



    def Assemble(self):
        pass



    def SetDefaultLOD(self):
        if self.model is None:
            return 
        if self.model.__typename__ == 'TriLODGroup':
            if settings.user.ui.Get('lod', 1) == 0 and not self.forceLOD:
                self.model.lodBy = trinity.TRILB_NONE
                self.model.activeLevel = 0
            else:
                self.model.lodBy = trinity.TRITB_CAMERA_DISTANCE_FOV_HEIGHT
                self.SetLODGroupRadius()
                for i in range(8):
                    setattr(self.model, 'treshold' + str(i), 0.0)

                childrenCnt = len(self.model.children)
                if childrenCnt == 4:
                    self.model.treshold0 = 0.025
                    self.model.treshold1 = 0.025
                    self.model.treshold2 = 0.013
                elif childrenCnt == 3:
                    self.model.treshold0 = 0.08
                    self.model.treshold1 = 0.009
                self.model.treshold0 = 0.025



    def SetStaticRotation(self):
        if self.model is None:
            return 
        self.model.rotationCurve = None
        slimItem = sm.StartService('michelle').GetItem(self.id)
        if slimItem:
            rot = getattr(slimItem, 'dunRotation', None)
            if rot is not None:
                (yaw, pitch, roll,) = rot
                if hasattr(self.model, 'rotation'):
                    if type(self.model.rotation) == types.TupleType:
                        self.model.rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw * DEG2RAD, pitch * DEG2RAD, roll * DEG2RAD)
                    else:
                        self.model.rotation.SetYawPitchRoll(yaw * DEG2RAD, pitch * DEG2RAD, roll * DEG2RAD)
                else:
                    self.model.rotationCurve = trinity.TriRotationCurve()
                    self.model.rotationCurve.value.SetYawPitchRoll(yaw * DEG2RAD, pitch * DEG2RAD, roll * DEG2RAD)



    def FindClosestMoonDir(self):
        bp = sm.StartService('michelle').GetBallpark()
        dist = 1e+100
        closestMoonID = None
        for (ballID, slimItem,) in bp.slimItems.iteritems():
            if slimItem.groupID == const.groupMoon:
                test = bp.DistanceBetween(self.id, ballID)
                if test < dist:
                    dist = test
                    closestMoonID = ballID

        if closestMoonID is None:
            return Vector3([1.0, 0.0, 0.0])
        moon = bp.GetBall(closestMoonID)
        direction = Vector3([self.x - moon.x, self.y - moon.y, self.z - moon.z])
        return direction



    def FindClosestPlanetDir(self):
        bp = sm.StartService('michelle').GetBallpark()
        dist = 1e+100
        closestPlanetID = None
        for (ballID, slimItem,) in bp.slimItems.iteritems():
            if slimItem.groupID == const.groupPlanet:
                test = bp.DistanceBetween(self.id, ballID)
                if test < dist:
                    dist = test
                    closestPlanetID = ballID

        if closestPlanetID is None:
            return Vector3([1.0, 0.0, 0.0])
        planet = bp.GetBall(closestPlanetID)
        direction = Vector3([self.x - planet.x, self.y - planet.y, self.z - planet.z])
        return direction



    def GetStaticDirection(self):
        slimItem = sm.StartService('michelle').GetItem(self.id)
        if slimItem is None:
            return 
        if slimItem.groupID == const.groupMoonMining:
            direction = self.FindClosestMoonDir()
        elif slimItem.groupID == const.groupPlanetaryCustomsOffices:
            direction = self.FindClosestPlanetDir()
        else:
            direction = getattr(slimItem, 'dunDirection', None)
        return direction



    def SetStaticDirection(self):
        if self.model is None:
            return 
        self.model.rotationCurve = None
        direction = self.GetStaticDirection()
        if direction is None:
            self.LogError('Space object', self.id, 'has no static direction defined - no rotation will be applied')
            return 
        self.AlignToDirection(direction)



    def AlignToDirection(self, direction):
        zaxis = Vector3(direction)
        if zaxis.Length2() > 0.0:
            Up = Vector3([0.0, 1.0, 0.0])
            zaxis.Normalize()
            xaxis = zaxis ^ Up
            if xaxis.Length2() == 0.0:
                zaxis += Vector3().Randomize(0.0001)
                zaxis.Normalize()
                xaxis = zaxis ^ Up
            xaxis.Normalize()
            yaxis = xaxis ^ zaxis
        else:
            self.LogError('Space object', self.id, 'has zero dunDirection. I cannot rotate it.')
            return 
        mat = trinity.TriMatrix(xaxis[0], xaxis[1], xaxis[2], 0.0, yaxis[0], yaxis[1], yaxis[2], 0.0, -zaxis[0], -zaxis[1], -zaxis[2], 0.0)
        if self.model and self.HasBlueInterface(self.model, 'IEveSpaceObject2') and hasattr(self.model, 'modelRotationCurve'):
            if not self.model.modelRotationCurve:
                self.model.modelRotationCurve = trinity.TriRotationCurve(0.0, 0.0, 0.0, 1.0)
            self.model.modelRotationCurve.value.RotationMatrix(mat)
        else:
            self.model.rotationCurve = None



    def UnSync(self):
        if self.model is None:
            return 
        startTime = long(random.random() * 123456.0 * 1234.0)
        scaling = 0.95 + random.random() * 0.1
        curves = timecurves.ReadCurves(self.model)
        timecurves.ResetTimeCurves(curves, startTime, scaling)



    def SetMiniballExplosions(self, gfx):
        if gfx is None:
            return 
        if not self.HasBlueInterface(gfx, 'IEveSpaceObject2'):
            self.LogWarn(self.id, 'SetMiniBallExplosions called for old content!')
            return 
        miniExplosions = [ x for x in gfx.Find('trinity.EveTransform') if x.name == 'SmallExplosion' ]
        if len(self.miniBalls) > 0:
            for explosionTransform in miniExplosions:
                miniball = random.choice(self.miniBalls)
                explosionTransform.translation = (miniball.x, miniball.y, miniball.z)




    def Display(self, display = 1):
        if self.model is None:
            self.LogWarn('Display - No model')
            return 
        if display and self.IsCloaked():
            if eve.session.shipid == self.id:
                sm.StartService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, None, 'effects.CloakNoAmim', 0, 1, 0, 5, 0)
            return 
        self.model.display = display



    def IsCloaked(self):
        return self.isCloaked



    def OnDamageState(self, damageState):
        pass



    def GetDamageState(self):
        return self.spaceMgr.ballpark.GetDamageState(self.id)



    def DoFinalCleanup(self):
        if not sm.IsServiceRunning('FxSequencer'):
            return 
        sm.GetService('FxSequencer').RemoveAllBallActivations(self.id)
        if hasattr(self, 'gfx') and self.gfx is not None:
            self.RemoveAndClearModel(self.gfx)
            self.gfx = None
        if self.explosionModel is not None:
            if getattr(self, 'explosionDisplayBinding', False):
                self.explosionDisplayBinding.destinationObject = None
                self.explosionDisplayBinding = None
            self.RemoveAndClearModel(self.explosionModel)
            self.explosionModel = None
        if not self.released:
            self.explodeOnRemove = False
            self.Release()



    def Release(self, origin = None):
        self.LogInfo('Release')
        if self.released:
            return 
        if self.explodeOnRemove:
            delayedRemove = self.Explode()
            if delayedRemove:
                return 
        self.released = True
        self.Display(0)
        self.RemoveAndClearModel(self.model)
        self.audioEntities = []
        self.generalAudioEntity = None
        self.model = None
        self.spaceMgr = None



    def RemoveAndClearModel(self, model):
        dev = trinity.GetDevice()
        if model:
            if hasattr(model, 'translationCurve'):
                model.translationCurve = None
                model.rotationCurve = None
            if hasattr(model, 'observers'):
                for ob in model.observers:
                    ob.observer = None

        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        if scene:
            scene.models.fremove(model)
        if scene2:
            scene2.objects.fremove(model)



    def OnPartition(self, lox, loy, loz, hix, hiy, hiz, radius, cubes):
        if self.rubixCube is None:
            self.FitRubixCube()
        if cubes is None:
            self.RemoveRubixCube()
        else:
            self.SetCubeAnchorPointAndScale(lox, loy, loz, 3 * (hiz - loz))
            self.HideCubes(cubes)



    def FitRubixCube(self):
        cube = trinity.Load('res:/Model/Global/rubix.blue')
        self.rubixCube = cube
        self.rubixCube.scaling.SetXYZ(self.radius / 50.0, self.radius / 50.0, self.radius / 50.0)
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene.children.append(cube)



    def SetCubeAnchorPointAndScale(self, x, y, z, scale):
        self.rubixCube.scaling.SetXYZ(scale / 100.0, scale / 100.0, scale / 100.0)
        cubeScaling = self.rubixCube.scaling.x * 100.0 / 3.0
        self.rubixCube.translation.SetXYZ(x + 0.5 * cubeScaling, y + 0.5 * cubeScaling, z + 0.5 * cubeScaling)



    def RemoveRubixCube(self):
        if hasattr(self, 'rubixCube') and self.rubixCube:
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.children.fremove(self.rubixCube)
            self.rubixCube = None



    def HideCubes(self, cubes):
        for area in self.rubixCube.object.areas:
            i = int(area.name[0])
            j = int(area.name[1])
            k = int(area.name[2])
            area.display = cubes[(i + j * 3 + 9 * k)]




    def ShakeCamera(self, magnitude, position):
        if not settings.user.ui.Get('cameraShakeEnabled', 1):
            return 
        camera = sm.StartService('sceneManager').GetRegisteredCamera('default')
        timeFactor = pow(magnitude / 400.0, 0.7)
        noiseScaleCurve = trinity.TriScalarCurve()
        noiseScaleCurve.AddKey(0.0, 1.2, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(0.1, 0.1, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(1.5 * timeFactor, 0.13, 0.0, 0.0, 3)
        noiseScaleCurve.AddKey(2.0 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseScaleCurve.extrapolation = 1
        noiseDampCurve = trinity.TriScalarCurve()
        noiseDampCurve.AddKey(0.0, 80.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(0.1, 20.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(1.5 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseDampCurve.AddKey(2.0 * timeFactor, 0.0, 0.0, 0.0, 3)
        noiseDampCurve.extrapolation = 1
        newPos = position - camera.pos
        distance = newPos.Length()
        if distance < 700.0:
            distance = 700.0
        elif distance > 2000000000:
            distance = 2000000000
        actualMagnitude = 0.7 * magnitude / pow(distance, 0.7)
        noiseScaleCurve.ScaleValue(actualMagnitude)
        noiseDampCurve.ScaleValue(actualMagnitude)
        if camera.noiseScaleCurve != None and camera.noiseScaleCurve.value > noiseScaleCurve.keys[1].value:
            return 
        now = blue.os.GetTime()
        noiseScaleCurve.start = now
        noiseDampCurve.start = now
        camera.noise = 1
        camera.noiseScaleCurve = noiseScaleCurve
        camera.noiseDampCurve = noiseDampCurve



    def FlashScreen(self, magnitude, duration = 0.5):
        self.spaceMgr.FlashScreen(magnitude, duration)



    def Explode(self, explosionURL = None, absoluteScaling = None, scaling = 1.0, randomRotation = False, explosionCleanupDelay = None):
        self.LogInfo('Exploding')
        if self.exploded:
            return False
        if explosionCleanupDelay is None:
            explosionCleanupDelay = 14000
        self.exploded = True
        if self.model is not None:
            self.model.display = False
        if settings.user.ui.Get('explosionEffectsEnabled', 1):
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            if explosionURL is None:
                explosionURL = 'res:/Emitter/explosion_end.blue'
                slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
                if slimItem is not None:
                    graphicID = cfg.invtypes.Get(slimItem.typeID).graphicID
                    if graphicID in cfg.graphics:
                        explosionID = cfg.graphics.Get(graphicID).explosionID
                        if explosionID:
                            explosionURL = util.GraphicFile(explosionID)
                            scaling = 0.1
            explosionURL = explosionURL.replace('.blue', '.red').replace('/Effect/', '/Effect3/')
            gfx = trinity.Load(explosionURL)
            if not gfx:
                self.LogError('Failed to load explosion: ', explosionURL, ' - using default')
                gfx = trinity.Load('res:/Model/Effect/Explosion/entityExplode_large.red')
            if gfx.__bluetype__ != 'trinity.EveRootTransform':
                root = trinity.EveRootTransform()
                root.children.append(gfx)
                root.name = explosionURL
                gfx = root
            gfx.translationCurve = self
            self.explosionModel = gfx
            scale = scaling
            if absoluteScaling is not None:
                scale *= absoluteScaling
            gfx.scaling = (gfx.scaling[0] * scale, gfx.scaling[1] * scale, gfx.scaling[2] * scale)
            scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
            scene2.objects.append(gfx)
        if self.wreckID is not None:
            wreckBall = sm.StartService('michelle').GetBall(self.wreckID)
            if wreckBall is not None:
                uthread.pool('Wreck::DisplayWreck', wreckBall.DisplayWreck, 500)
        return False



    def ShowDestinyBalls(self):
        sphere = trinity.Load('res:/Model/Global/greenSphere.blue')
        del sphere.children[:]
        ownballs = []
        if len(self.miniBalls) > 0:
            for miniball in self.miniBalls:
                ball = sphere.CopyTo()
                ball.translation.SetXYZ(miniball.x / self.model.children[0].scaling.x, miniball.y / self.model.children[0].scaling.y, miniball.z / self.model.children[0].scaling.z)
                ball.scaling.SetXYZ(miniball.radius * 2 / self.model.children[0].scaling.x, miniball.radius * 2 / self.model.children[0].scaling.x, miniball.radius * 2 / self.model.children[0].scaling.x)
                ownballs.append(ball)

        for LOD in self.model.children:
            for miniball in ownballs:
                LOD.children.append(miniball)





    def SetLODGroupRadius(self):
        r = self.FindSimpleBoundingRadius(self.model.children[0])
        self.model.boundingSphereRadius = r
        self.boundingSphereRadius = r



    def FindSimpleBoundingRadius(self, transform):
        if hasattr(transform, 'object') and hasattr(transform.object, 'vertexRes') and transform.object.vertexRes is not None:
            minbox = transform.object.vertexRes.meshBoxMin.CopyTo()
            maxbox = transform.object.vertexRes.meshBoxMax.CopyTo()
            minbox.TransformCoord(transform.localTransform)
            maxbox.TransformCoord(transform.localTransform)
            spear = maxbox - minbox
            r = spear.Length() * 0.5
            if r * 10.0 < self.radius:
                r = self.radius
            return r
        return self.radius



    def FindHierarchicalBoundingBox(self, transform, printout, parentMat = trinity.TriMatrix(), indent = '', minx = 1e+100, maxx = -1e+100, miny = 1e+100, maxy = -1e+100, minz = 1e+100, maxz = -1e+100, parentScale = trinity.TriVector(1.0, 1.0, 1.0)):
        transform.Update(blue.os.GetTime())
        if printout:
            print indent,
            print transform.name
        if hasattr(transform, 'translation') and transform.__typename__ in ('TriTransform', 'TriSplTransform', 'TriLODGroup'):
            if transform.__typename__ == 'TriTransform':
                if transform.transformBase != trinity.TRITB_OBJECT:
                    return (minx,
                     maxx,
                     miny,
                     maxy,
                     minz,
                     maxz)
            if hasattr(transform, 'object') and hasattr(transform.object, 'vertexRes') and transform.object.vertexRes is not None:
                v = transform.object.vertexRes
                if printout and (minx < v.meshBoxMin.x or maxx > v.meshBoxMax.x or miny < v.meshBoxMin.y or maxy > v.meshBoxMax.y or minz < v.meshBoxMin.z or maxz > v.meshBoxMax.z):
                    print indent,
                    print 'MESHMIN:',
                    print v.meshBoxMin,
                    print 'MESHMAX:',
                    print v.meshBoxMax,
                    print 'TRANSLATION:',
                    print transform.translation
                damin = transform.object.vertexRes.meshBoxMin.CopyTo()
                damax = transform.object.vertexRes.meshBoxMax.CopyTo()
                damin.TransformCoord(transform.localTransform)
                damax.TransformCoord(transform.localTransform)
                damin.TransformCoord(parentMat)
                damax.TransformCoord(parentMat)
                minx = min(minx, min(damin.x, damax.x))
                maxx = max(maxx, max(damin.x, damax.x))
                miny = min(miny, min(damin.y, damax.y))
                maxy = max(maxy, max(damin.y, damax.y))
                minz = min(minz, min(damin.z, damax.z))
                maxz = max(maxz, max(damin.z, damax.z))
                if printout:
                    print indent,
                    print 'MESHMIN:',
                    print v.meshBoxMin,
                    print 'MESHMAX:',
                    print v.meshBoxMax,
                    print indent,
                    print minx,
                    print maxx,
                    print miny,
                    print maxy,
                    print minz,
                    print maxz
                    print indent,
                    print parentMat
                    print indent,
                    print transform.localTransform
            newmat = transform.localTransform.CopyTo()
            newmat.Multiply(parentMat)
            for child in transform.children:
                indent = indent + '  '
                (minx, maxx, miny, maxy, minz, maxz,) = self.FindHierarchicalBoundingBox(child, printout, newmat, indent, minx, maxx, miny, maxy, minz, maxz, parentScale)

        return (minx,
         maxx,
         miny,
         maxy,
         minz,
         maxz)



    def FitBoosters2(self, graphicID = None, alwaysOn = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is None:
            self.LogError('No invitem property for ship')
            return 
        godmaStateManager = sm.StartService('godma').GetStateManager()
        godmaType = godmaStateManager.GetType(slimItem.typeID)
        if graphicID is None:
            graphicID = godmaType.gfxBoosterID
            if graphicID == 0:
                graphicID = 395
        graphicURL = util.GraphicFile(graphicID)
        graphicURL = graphicURL.replace('.blue', '.red')
        graphicURL = graphicURL.replace(':/model/', ':/dx9/model/')
        try:
            self.model.boosters = trinity.Load(graphicURL)
            self.model.boosters.maxVel = self.maxVelocity
            self.model.RebuildBoosterSet()
            self.model.boosters.alwaysOn = alwaysOn
        except:
            sys.exc_clear()
            self.LogError('Type', slimItem.typeID, 'has no booster locators', 'Could not fit booster ID ' + strx(graphicID) + ' URL' + graphicURL + ' to ' + self.model.name)
            return 
        boosterAudioLocators = filter(lambda node: node.name.startswith('locator_audio_booster'), self.model.locators)
        import audio2
        tmpEntity = None
        tmpParameter = None
        for audLocator in boosterAudioLocators:
            tlpo = trinity.TriObserverLocal()
            transform = audLocator.transform
            tlpo.front = (-transform[2][0], -transform[2][1], -transform[2][2])
            tlpo.position = (transform[3][0], transform[3][1], transform[3][2])
            if tmpEntity is None:
                tmpEntity = audio2.AudEmitter('ship_' + str(self.id) + '_booster')
                tmpParameter = audio2.AudParameter()
                tmpParameter.name = u'ship_speed'
                tmpEntity.parameters.append(tmpParameter)
                self.shipSpeedParameter = tmpParameter
            tlpo.observer = tmpEntity
            self.audioEntities.append(tmpEntity)
            self.model.observers.append(tlpo)

        boosterGodmaType = godmaType.gfxBoosterID
        if boosterGodmaType == 0:
            boosterGodmaType = 395
        boosterTypes = {394: 'booster_blue',
         395: 'booster_yellow',
         396: 'booster_green',
         397: 'booster_red'}
        boosterType = boosterTypes[boosterGodmaType]
        boosterSize = 'l'
        if self.radius > 99:
            if self.radius > 309:
                boosterSize = 'lb'
            else:
                boosterSize = 'lc'
        self.boosterAudioEvent = '_'.join(['ship',
         boosterType,
         boosterSize,
         'play'])
        if tmpEntity is not None:
            audioModifier = trinity.TriCurveSet()
            audioModifier.name = 'AudioModifier'
            speedToVolumeCurve = trinity.TriScalarCurve()
            speedToVolumeCurve.name = 'SpeedToVolumeCurve'
            speedToVolumeCurve.extrapolation = trinity.TRIEXT_CONSTANT
            speedToVolumeCurve.AddKey(0.0, 0.0, 1.0, 1.0, trinity.TRIINT_LINEAR)
            speedToVolumeCurve.AddKey(0.1, 0.0, 1.0, 1.0, trinity.TRIINT_LINEAR)
            speedToVolumeCurve.AddKey(1.0, 1.0, 1.0, 1.0, trinity.TRIINT_LINEAR)
            speedToVolumeCurve.AddKey(1000000000.0, 10.0, 1.0, 1.0, trinity.TRIINT_LINEAR)
            audioModifier.curves.append(speedToVolumeCurve)
            binding = trinity.TriValueBinding()
            binding.name = 'BindShipSpeedToAudioModifierCurve'
            baseVelocity = 1
            if util.IsNPC(self.id):
                baseVelocity = sm.StartService('godma').GetTypeAttribte(slimItem.typeID, const.attributeEntityCruiseSpeed)
            else:
                baseVelocity = sm.StartService('godma').GetTypeAttribute(slimItem.typeID, const.attributeMaxVelocity)
            if baseVelocity is None:
                baseVelocity = 1.0
            binding.scale = 1.0 / baseVelocity
            binding.sourceObject = self.model.speed
            binding.destinationObject = audioModifier
            binding.sourceAttribute = 'value'
            binding.destinationAttribute = 'scaledTime'
            binding2 = trinity.TriValueBinding()
            binding2.name = 'BindAudioVolumeToRTPC'
            binding2.sourceObject = speedToVolumeCurve
            binding2.destinationObject = tmpParameter
            binding2.sourceAttribute = 'value'
            binding2.destinationAttribute = 'value'
            audioBinder = trinity.TriCurveSet()
            audioBinder.name = 'AudioSpeedBinding'
            audioBinder.bindings.append(binding)
            audioModifier.bindings.append(binding2)
            self.model.curveSets.append(audioBinder)
            self.model.curveSets.append(audioModifier)
            audioBinder.Play()
            audioModifier.Play()
            tmpEntity.SendEvent(unicode(self.boosterAudioEvent))



    def SetupAmbientAudio(self, defaultSoundUrl = None):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        spaceAudio = sm.GetService('spaceAudioSvc')
        validResource = True
        soundUrl = None
        soundUrl = spaceAudio.GetSoundUrlForType(slimItem)
        if soundUrl is not None:
            validResource = soundUrl.startswith('wise:/')
        if soundUrl is None or len(soundUrl) <= 0 or not validResource:
            if not validResource:
                self.LogWarn(self.id, 'Specified sound resource is not a Wwise resource, either default sound or no sound will be played! (url = %s)' % soundUrl)
            if defaultSoundUrl is None:
                return 
            soundUrl = defaultSoundUrl
        self.PlayGeneralAudioEvent(unicode(soundUrl))



    def LookAtMe(self):
        pass



    def GetGeneralAudioEntity(self):
        if self.generalAudioEntity is None:
            if self.model is not None and hasattr(self.model, 'observers'):
                triObserver = trinity.TriObserverLocal()
                self.generalAudioEntity = audio2.AudEmitter('spaceObject_' + str(self.id) + '_general')
                triObserver.observer = self.generalAudioEntity
                self.audioEntities.append(self.generalAudioEntity)
                self.model.observers.append(triObserver)
            else:
                self.LogWarn(self.id, 'unable to construct generalized audio entity - model has no observers property')
        return self.generalAudioEntity



    def PlayGeneralAudioEvent(self, eventName):
        audEntity = self.GetGeneralAudioEntity()
        if audEntity is None:
            return 
        if eventName.startswith('wise:/'):
            eventName = eventName[6:]
        self.LogInfo(self.id, 'playing audio event', eventName, 'on generalized emitter')
        audEntity.SendEvent(unicode(eventName))



exports = {'spaceObject.SpaceObject': SpaceObject}

