import util
import blue
import cameras
CAMERA_ZOOM_CLOSE = 0
CAMERA_ZOOM_FAR = 1
ZOOM_SPEED_MODIFIER = 2.0

class AvatarCamera(cameras.IncarnaCamera):
    __guid__ = 'cameras.AvatarCamera'

    def __init__(self):
        cameras.IncarnaCamera.__init__(self)
        self.minZoom = 1.9
        self.maxZoom = 2.9
        self.wantToToggleZoom = False
        self.zoomAccelerate = 1.0
        self.zoomToggle = CAMERA_ZOOM_CLOSE



    def AdjustZoom(self, delta):
        if self.zoomToggle == cameras.CAMERA_ZOOM_CLOSE and delta > 0 or self.zoomToggle == cameras.CAMERA_ZOOM_FAR and delta < 0:
            self.wantToToggleZoom = True



    def SetCollisionZoom(self, zoom, amountPerFrame):
        zoom = min(zoom, cameras.CLOSEST_CAMERA_DISTANCE)
        self.collisionZoom = zoom
        self.collisionCorrectionPerFrame = amountPerFrame



    def SetZoom(self, zoom):
        self.desiredZoom = zoom
        self.desiredZoom = max(self.desiredZoom, self.minZoom)
        self.desiredZoom = min(self.desiredZoom, self.maxZoom)



    def Update(self):
        self.Init()
        now = blue.os.GetTime()
        self.frameTime = float(now - self.lastUpdateTime) / const.SEC
        self.HandleYawAndPitch()
        if abs(self.zoom - self.collisionZoom) > 0.01:
            if abs(self.zoom - self.collisionZoom) <= abs(self.collisionCorrectionPerFrame):
                self.zoom = self.collisionZoom
                self.zoomAccelerate = 1.0
            elif self.zoom + abs(self.collisionCorrectionPerFrame * self.zoomAccelerate) < self.collisionZoom:
                self.zoom += abs(self.collisionCorrectionPerFrame * self.zoomAccelerate)
            elif self.zoom - abs(self.collisionCorrectionPerFrame * self.zoomAccelerate) > self.collisionZoom:
                self.zoom -= abs(self.collisionCorrectionPerFrame * self.zoomAccelerate)
            else:
                self.zoom = self.collisionZoom
            self.desiredZoom = self.zoom
        else:
            self.HandleZooming()
        self.lastUpdateTime = now
        self.HandleMouseMove()
        for (priority, behavior,) in self.cameraBehaviors:
            behavior.ProcessCameraUpdate(self, now, self.frameTime)

        self.ResetMouseMoveDelta()
        self.wantToToggleZoom = False
        self.AssembleViewMatrix(self.poi, self.yaw, self.pitch, self.zoom)
        self.HandleMouseMoveDelta()
        self.HandleAudioListener()



exports = util.AutoExports('cameras', locals())

