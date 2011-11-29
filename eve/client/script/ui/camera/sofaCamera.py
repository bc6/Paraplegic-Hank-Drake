import geo2
import cameras
import cameraUtils

class SofaCamera(cameras.IncarnaCamera):
    __guid__ = 'cameras.SofaCamera'

    def __init__(self):
        cameras.IncarnaCamera.__init__(self)
        self.zoomAccelerate = 1.0
        self.setZoom = 2.9
        self.zoom = self.desiredZoom = 2.9
        self.minPitch = 1.5
        self.maxPitch = 2.0
        self.pushUp = 0.0
        self.colliding = False
        self.gameWorld = None
        self.entity = None



    def SetEntity(self, entity):
        self.entity = entity
        yaw = cameraUtils.GetEntityYaw(self.entity)
        yaw = cameraUtils.ReverseCameraYaw(yaw)
        self.SetYaw(yaw)
        poi = (self.entity.position.position[0], self.entity.position.position[1] + self.pushUp, self.entity.position.position[2])
        self.SetPointOfInterest(poi)
        gameWorldClient = sm.GetService('gameWorldClient')
        if gameWorldClient.HasGameWorld(session.worldspaceid):
            self.gameWorld = gameWorldClient.GetGameWorld(session.worldspaceid)



    def AvoidCollision(self):
        criticalFailInfo = self.gameWorld.SweptSphere(self.poi, self.cameraAdvancedPos, cameras.NORMAL_COLLISION_SPHERE)
        if criticalFailInfo:
            safeSpot = geo2.Vec3Add(criticalFailInfo[0], (val * cameras.NORMAL_COLLISION_SPHERE for val in criticalFailInfo[1]))
            if not self.colliding:
                self.colliding = True
            newZoom = geo2.Vec3Distance(self.poi, safeSpot)
            self.collisionZoom = self.zoom = self.desiredZoom = newZoom
        elif self.colliding:
            self.desiredZoom = self.setZoom
            self.collisionZoom = self.zoom
            self.colliding = False



    def CalcCamCurrAndAdvancedPosition(self):
        self.centerPoint = (self.entity.position.position[0], self.entity.position.position[1] + self.pushUp, self.entity.position.position[2])
        cameraAdvancedPos = self.YawPitchDistToPoint(self.yaw, self.pitch, self.setZoom)
        cameraAdvancedPos = geo2.Vec3Add(cameraAdvancedPos, self.poi)
        self.cameraAdvancedPos = cameraAdvancedPos



    def Update(self):
        cameras.IncarnaCamera.Update(self)
        if self.gameWorld:
            self.CalcCamCurrAndAdvancedPosition()
            self.AvoidCollision()




