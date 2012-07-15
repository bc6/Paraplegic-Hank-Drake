#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/camera/flyModeCamera.py
import geo2
import util
import math
import trinity
import cameras
import GameWorld
MOUSE_DELTA_SLOW_DOWN = 155.0
FLY_CAMERA_ACCELERATION = 2
FLY_CAMERA_BASE_MOVEMENT_SPEED = 0.005

class FlyModeCamera(cameras.BasicCamera):
    __guid__ = 'cameras.FlyModeCamera'

    def __init__(self):
        cameras.BasicCamera.__init__(self)
        self.avatar = None
        self.maxRotate = math.pi
        self.navigation = sm.GetService('navigation')
        avatarCamera = sm.GetService('cameraClient').GetCameraStack()[0]
        self.frontClip = 0.01
        self.fieldOfView = avatarCamera.fieldOfView
        self.SetYaw(avatarCamera.yaw)
        self.SetPitch(avatarCamera.pitch)
        self.cameraPosition = avatarCamera.cameraPosition
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.updateMouse = True

    def AdjustPitch(self, delta):
        delta = delta / MOUSE_DELTA_SLOW_DOWN
        if self.pitch + delta < 0.1:
            cameras.BasicCamera.SetPitch(self, 0.1)
        elif self.pitch + delta > math.pi:
            cameras.BasicCamera.SetPitch(self, math.pi)
        else:
            cameras.BasicCamera.SetPitch(self, self.pitch + delta)

    def AdjustYaw(self, delta):
        delta = delta / MOUSE_DELTA_SLOW_DOWN
        self.SetYaw(self.yaw + delta)

    def PerformPick(self, x, y, ignoreEntID = -1):
        startPoint, endPoint = self.GetRay(x, y)
        if not session.worldspaceid:
            return None
        else:
            gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
            if gameWorld:
                collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
                p = gameWorld.LineTestEntId(startPoint, endPoint, ignoreEntID, collisionGroups)
                return p
            return None

    def TurnOffAvatar(self):
        if self.avatar is None:
            entity = sm.GetService('entityClient').FindEntityByID(session.charid)
            if entity and entity.HasComponent('paperdoll'):
                self.avatar = entity.GetComponent('paperdoll')
                self.avatar.doll.avatar.display = False

    def Update(self):
        cameras.BasicCamera.Update(self)
        self.TurnOffAvatar()
        if not trinity.app.IsActive():
            return
        fwdActive, backActive, moveLActive, moveRActive = self.navigation.GetKeyState()
        speed = cameras.FLY_CAMERA_ACCELERATION * cameras.FLY_CAMERA_BASE_MOVEMENT_SPEED
        if fwdActive:
            self.cameraPosition = geo2.Vec3Add(self.cameraPosition, (val * -speed for val in self.direction))
        elif backActive:
            self.cameraPosition = geo2.Vec3Add(self.cameraPosition, (val * speed for val in self.direction))
        if moveLActive:
            rotateLeft = (-self.direction[2], self.direction[1], self.direction[0])
            translation = geo2.Vec3Add(self.cameraPosition, (val * speed for val in rotateLeft))
            self.cameraPosition = (translation[0], self.cameraPosition[1], translation[2])
        elif moveRActive:
            rotateRight = (self.direction[2], self.direction[1], -self.direction[0])
            translation = geo2.Vec3Add(self.cameraPosition, (val * speed for val in rotateRight))
            self.cameraPosition = (translation[0], self.cameraPosition[1], translation[2])


exports = util.AutoExports('cameras', locals())