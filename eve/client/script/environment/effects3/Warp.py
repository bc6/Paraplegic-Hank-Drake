import blue
import effects
import uthread
import destiny
import trinity
from math import cos, pow
from foo import Vector3
FX_SCALE_EFFECT_NONE = 0
FX_USEBALLTRANSLATION = 1
FX_USEBALLROTATION = 2

class Warp(effects.ShipEffect):
    __guid__ = 'effects.Warping'
    __gfx__ = 'res:/Model/Effect3/warpTunnel.red'
    __scaleTime__ = False
    __scaling__ = FX_SCALE_EFFECT_NONE
    __positioning__ = 0

    def _GetDuration():
        return 1200000


    _GetDuration = staticmethod(_GetDuration)

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Prepare(self):
        shipID = self.GetEffectShipID()
        if shipID != session.shipid:
            return 
        effects.ShipEffect.Prepare(self)
        self.AlignToDirection()



    def Start(self, duration):
        if self.gfx is None:
            return 
        self.active = True
        self.hasExploded = False
        self.hasWind = False
        effects.ShipEffect.Start(self, duration)
        bp = sm.StartService('michelle').GetBallpark()
        shipID = self.GetEffectShipID()
        shipBall = bp.GetBall(shipID)
        self.shipModel = getattr(shipBall, 'model', None)
        slimItem = bp.GetInvItem(shipID)
        self.curveSet = [ x for x in self.gfx.curveSets if x.name == 'SpeedBinding' ][0]
        binding = self.curveSet.bindings[0]
        binding.sourceObject = self.shipModel.speed
        warpSpeedModifier = sm.StartService('godma').GetTypeAttribute(slimItem.typeID, const.attributeWarpSpeedMultiplier)
        if warpSpeedModifier is None:
            warpSpeedModifier = 1.0
        binding.scale *= 1.0 / (3.0 * const.AU * warpSpeedModifier)
        uthread.worker('FxSequencer::WarpEffectLoop', self.WarpLoop, shipBall)



    def WarpLoop(self, ball):
        sm.StartService('space').StartWarpIndication()
        sm.ScatterEvent('OnWarpStarted')
        while ball.mode == destiny.DSTBALL_WARP:
            sm.GetService('space').IndicateWarp()
            self.ShakeCamera(ball)
            if not self.hasExploded or self.hasWind:
                speedFraction = self.shipModel.speed.value * self.curveSet.bindings[0].scale
                if not self.hasExploded and speedFraction > 0.05:
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_explosion_play')
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_play')
                    self.hasExploded = True
                    self.hasWind = True
                elif self.hasWind and speedFraction < 0.001:
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_stop')
                    self.hasWind = False
            blue.synchro.Sleep(1000)

        sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_stop')
        sm.StartService('FxSequencer').OnSpecialFX(ball.id, None, None, None, None, [], 'effects.Warping', 0, 0, 0)
        sm.ScatterEvent('OnWarpFinished')
        sm.StartService('space').StopWarpIndication()



    def Stop(self):
        if self.gfx is None:
            return 
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        camera.noise = 0
        effects.ShipEffect.Stop(self)



    def ShakeCamera(self, ball):
        shakeEnabled = settings.user.ui.Get('cameraShakeEnabled', 1)
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if camera is None:
            return 
        if not shakeEnabled:
            camera.noise = 0
            return 
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        speedVector = trinity.TriVector(ball.vx, ball.vy, ball.vz)
        speed = speedVector.Length()
        maxSpeed = ballpark.warpSpeed * const.AU - ball.maxVelocity
        speed = (speed - ball.maxVelocity) / maxSpeed
        speed = max(0.0, speed)
        rumbleFactor = 0.5 - 0.5 * cos(6.28 * pow(speed, 0.1))
        tempRfactor = rumbleFactor
        rumbleFactor = (rumbleFactor - 0.2) / 0.8
        rumbleFactor = max(rumbleFactor, 0.0)
        rumbleFactor = pow(rumbleFactor, 0.8)
        shakeFactor = 0.7 * rumbleFactor
        if camera.noiseScaleCurve is None:
            noiseScale = 0.0
        else:
            noiseScale = camera.noiseScale
        noisescaleCurve = trinity.TriScalarCurve()
        noisescaleCurve.extrapolation = trinity.TRIEXT_CONSTANT
        noisescaleCurve.AddKey(0.0, noiseScale, 0.0, 0.0, trinity.TRIINT_LINEAR)
        noisescaleCurve.AddKey(0.5, shakeFactor * 2.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
        noisescaleCurve.AddKey(5.0, 0.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
        noisescaleCurve.Sort()
        camera.noiseScaleCurve = noisescaleCurve
        now = blue.os.GetTime()
        camera.noiseScaleCurve.start = now
        camera.noise = 1



    def AlignToDirection(self):
        destination = sm.StartService('space').warpDestinationCache[3]
        ballPark = sm.StartService('michelle').GetBallpark()
        egoball = ballPark.GetBall(ballPark.ego)
        direction = [destination[0] - egoball.x, destination[1] - egoball.y, destination[2] - egoball.z]
        zaxis = Vector3(direction)
        if zaxis.Length2() > 0.0:
            Up = Vector3([0.0, 1.0, 0.0])
            zaxis.Normalize()
            xaxis = Up ^ zaxis
            if xaxis.Length2() == 0.0:
                zaxis += Vector3().Randomize(0.0001)
                zaxis.Normalize()
                xaxis = Up ^ zaxis
            xaxis.Normalize()
            yaxis = zaxis ^ xaxis
        else:
            __positioning__ = FX_USEBALLTRANSLATION | FX_USEBALLROTATION
            self.Prepare()
            return 
        mat = trinity.TriMatrix(xaxis[0], xaxis[1], xaxis[2], 0.0, yaxis[0], yaxis[1], yaxis[2], 0.0, zaxis[0], zaxis[1], zaxis[2], 0.0)
        self.gfxModel.rotationCurve = None
        if self.gfxModel and hasattr(self.gfxModel, 'modelRotationCurve'):
            self.gfxModel.modelRotationCurve = trinity.TriRotationCurve(0.0, 0.0, 0.0, 1.0)
            self.gfxModel.modelRotationCurve.value.RotationMatrix(mat)




