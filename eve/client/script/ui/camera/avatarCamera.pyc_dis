#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/camera/avatarCamera.py
import util
import blue
import cameras
import trinity
SCROLL_AMOUNT = 0.42
MOUSE_SCROLL_MODIFIER = 0.7
CLOSEST_CAMERA_DISTANCE = 0.2

class AvatarCamera(cameras.IncarnaCamera):
    __guid__ = 'cameras.AvatarCamera'

    def __init__(self):
        cameras.IncarnaCamera.__init__(self)
        self.minZoom = 0.8
        self.maxZoom = cameras.INCARNA_MAX_ZOOM
        self.sceneManager = sm.GetService('sceneManager')
        self.viewState = sm.GetService('viewState')
        self.pitch = 1.93245
        self.zoom = self.collisionZoom = self.maxZoom
        self.zoomRequest = None
        self.userSelectedZoom = self.maxZoom
        self.zoomAccelerate = 1.0
        self.lastScrollDelta = 0
        self.colliding = False

    def PickHangarScene(self, posX, posY):
        if self.viewState.IsViewActive('station'):
            stationView = self.viewState.GetView('station')
            if stationView.hangarScene:
                view = self.sceneManager.backgroundView
                projection = self.sceneManager.backgroundProjection
                oldSceneItem = stationView.hangarScene.PickObject(posX, posY, projection, view, trinity.device.viewport)
                return oldSceneItem

    def AdjustZoom(self, delta):
        if delta > 0:
            delta = SCROLL_AMOUNT
        else:
            delta = -SCROLL_AMOUNT
        self.lastScrollDelta = delta
        if self.zoom + delta < self.minZoom:
            desiredZoom = self.minZoom
        elif self.zoom + delta > self.maxZoom:
            desiredZoom = self.maxZoom
        else:
            desiredZoom = self.zoom + delta
        self.zoomRequest = desiredZoom

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
        now = blue.os.GetWallclockTime()
        self.frameTime = float(now - self.lastUpdateTime) / const.SEC
        self.lastUpdateTime = now
        if self.frameTime <= 0.0:
            return
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
        self.HandleMouseMove()
        for priority, behavior in self.cameraBehaviors:
            behavior.ProcessCameraUpdate(self, now, self.frameTime)

        self.ResetMouseMoveDelta()
        self.AssembleViewMatrix(self.poi, self.yaw, self.pitch, self.zoom)
        self.HandleMouseMoveDelta()
        self.HandleAudioListener()


exports = util.AutoExports('cameras', locals())