import spaceObject
import blue
import geo2
import trinity
import destiny
import nodemanager
import timecurves
import uthread
import foo
import math
from string import split
import log
import random

class Missile(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Missile'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.exploded = False
        self.collided = False
        self.targetId = None
        self.ownerID = None
        self.gfx = None
        self.enabled = settings.user.ui.Get('missilesEnabled', 1)



    def LoadModel(self):
        if not self.enabled:
            return 
        bp = sm.StartService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(self.id)
        fileName = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
        self.ownerID = slimItem.ownerID
        self.targetId = self.followId
        self.model = trinity.Load(fileName)
        self.targets = [self.model]
        self.missileFileName = fileName
        explosionPath = 'res:/Model/Effect/Explosion/Missile/MExplosion_' + split(self.missileFileName, '/')[-1:][0][8:]
        explosionPath = self.GetTrinityVersionFilename(explosionPath)
        self.gfx = trinity.Load(explosionPath)
        if self.model is None:
            return 
        self.model.translationCurve = self
        self.model.rotationCurve = self
        self.model.name = 'Missile in %s' % self.id
        self.model.useCurves = 1
        self.model.display = False
        if self.HasBlueInterface(self.model, 'IEveSpaceObject2'):
            scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
            scene2.objects.append(self.model)
        else:
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.models.append(self.model)



    def Assemble(self):
        if self.model is not None:
            if self.model.__bluetype__ == 'trinity.TriLODGroup':
                self.model.lodBy = trinity.TRITB_CAMERA_DISTANCE_FOV_HEIGHT
                self.model.boundingSphereRadius = 20.0
                self.model.treshold0 = 0.003
                self.model.treshold1 = 0.001
            else:
                log.LogWarn('Missile model of suspicious type: ' + str(self.model.__bluetype__))
        self.targets = [self.model]



    def Prepare(self, spaceMgr):
        spaceObject.SpaceObject.Prepare(self, spaceMgr)
        if self.EstimateTimeToTarget() < 1.0:
            self.DoCollision(self.targetId, 0.0, 0.0, 0.0, False)



    def EstimateTimeToTarget(self):
        bp = sm.StartService('michelle').GetBallpark()
        targetBall = bp.GetBallById(self.targetId)
        if targetBall is None:
            return 
        now = blue.os.GetTime()
        myPos = self.GetVectorAt(now)
        targetPos = targetBall.GetVectorAt(now)
        offset = myPos - targetPos
        collisionTime = offset.Length() / self.maxVelocity
        return collisionTime



    def DoCollision(self, targetId, fx, fy, fz, fake = False):
        if self.model is None:
            return 
        bp = sm.StartService('michelle').GetBallpark()
        if targetId < 0 and targetId != self.id:
            targetBall = bp.GetBall(targetId)
            if targetBall is not None:
                if targetBall.mode == destiny.DSTBALL_MINIBALL:
                    targetId = targetBall.ownerId
        if targetId < 0:
            return 
        if self.exploded or self.collided and not fake:
            return 
        if targetId != self.id:
            if self.mode == destiny.DSTBALL_MISSILE and self.followId != targetId:
                return 
        now = blue.os.GetTime()
        myPos = self.GetVectorAt(now)
        myVel = self.GetVectorDotAt(now)
        targetBall = bp.GetBallById(self.targetId)
        if targetBall is None:
            return 
        targetPos = targetBall.GetVectorAt(now)
        targetVel = targetBall.GetVectorDotAt(now)
        nullV = trinity.TriVector()
        offset = myPos - targetPos
        collisionTime = offset.Length() / self.maxVelocity
        curve = trinity.TriVectorCurve()
        curve.AddKey(0.0, offset, 3.0 * myVel, nullV, trinity.TRIINT_HERMITE)
        curve.AddKey(collisionTime, nullV, 3.0 * targetVel, nullV, trinity.TRIINT_HERMITE)
        curve.Sort()
        curve.extrapolation = 1
        curve.start = now
        missileModel = self.model
        missileModel.useCurves = 1
        if hasattr(missileModel, 'translationCurve'):
            missileModel.translationCurve = curve
        if hasattr(missileModel, 'rotationCurve'):
            missileModel.rotationCurve = None
        self.model = trinity.TriTransform()
        self.model.translationCurve = targetBall
        self.model.useCurves = 1
        self.model.children.append(missileModel)
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene.models.append(self.model)
        scene.models.fremove(missileModel)
        missileModel.display = 1
        self.model.display = 1
        self.collided = True
        if collisionTime > 2:
            collisionTime = 2
        uthread.pool('Missile::CollisionExplode', self.CollisionExplode, long(collisionTime * 1000), self.model.translation, fake)



    def CollisionExplode(self, delay, translation, fake = False):
        if delay > 2000:
            delay = 2000
        blue.pyos.synchro.Sleep(delay)
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        if not self.released:
            if self.model:
                if hasattr(self.model, 'translationCurve'):
                    self.model.translationCurve = None
                if hasattr(self.model, 'rotationCurve'):
                    self.model.rotationCurve = None
            if scene and trinity.device:
                scene.models.fremove(self.model)
        if fake:
            self.exploded = True
            sm.StartService('bracket').ClearBracket(self.id)
            self.gfx = None
            return 
        if self.exploded:
            return 
        self.exploded = True
        sm.StartService('bracket').ClearBracket(self.id)
        if self.gfx is None:
            return 
        gfx = self.gfx
        self.gfx = None
        self.explosionModel = gfx
        if self.enabled:
            curves = timecurves.ReadTimeAndSoundCurvesF(gfx)
            duration = int(timecurves.MaxLenF(curves) * 1000.0)
            timecurves.ResetTimeAndSoundCurvesF(curves)
            gfx.translation = (translation.x, translation.y, translation.z)
            rndRotation = geo2.QuaternionRotationSetYawPitchRoll(random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi)
            gfx.rotation = rndRotation
            scene2.objects.append(gfx)
            self.ShakeCamera(250, translation)
            for curveSet in gfx.curveSets:
                curveSet.Play()

            bp = sm.StartService('michelle').GetBallpark()
            targetBall = bp.GetBallById(self.targetId)
            if targetBall:
                missileAudio = split(self.missileFileName, '/')[-1:][0][8:-5]
                missileAudio = 'effects_missile_mexplosion_' + missileAudio.lower() + '_play'
                targetBall.PlayGeneralAudioEvent(missileAudio)
        uthread.pool('Missile::DelayedRemove', self.DelayedRemove, duration, gfx)



    def DelayedRemove(self, delay, model):
        blue.pyos.synchro.Sleep(delay)
        self.RemoveAndClearModel(model)



    def Explode(self):
        return self.collided



    def Release(self):
        if not self.collided and self.explodeOnRemove and self.enabled:
            self.collided = True
            uthread.pool('Missile::DoFakeCollision', self.DoCollision, self.targetId, 0.0, 0.0, 0.0, True)
        sm.StartService('bracket').ClearBracket(self.id)
        self.targets = None
        if self.collided and self.model is not None:
            if len(self.model.children) > 0:
                if hasattr(self.model.children[0], 'translationCurve'):
                    self.model.children[0].translationCurve = None
                if hasattr(self.model.children[0], 'rotationCurve'):
                    self.model.children[0].rotationCurve = None
        spaceObject.SpaceObject.Release(self, 'Missile')



    def Display(self, display = 1):
        if self.enabled:
            spaceObject.SpaceObject.Display(self, display)



exports = {'spaceObject.Missile': Missile}

