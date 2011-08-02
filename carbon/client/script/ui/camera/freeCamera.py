import cameras
import util
import geo2
import math
import blue

class FreeCamera(cameras.PolarCamera):
    __guid__ = 'cameras.FreeCamera'

    def __init__(self):
        cameras.PolarCamera.__init__(self)
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.cameraPosition = (0, 0, 0)
        self.minPitch = -math.pi / 2 + 0.05
        self.maxPitch = math.pi / 2 - 0.05
        startingViewMatrix = self.CreateViewMatrix(self.cameraPosition, (self.yaw, self.pitch, self.roll))
        self.viewMatrix.transform = util.ConvertTriToTupleMatrix(startingViewMatrix)



    def AbsoluteMoveCamera(self, dx, dy, dz):
        newPos = (self.cameraPosition[0] + dx, self.cameraPosition[1] + dy, self.cameraPosition[2] + dz)
        curRot = (self.yaw, self.pitch, self.roll)
        newViewMatrix = self.CreateViewMatrix(newPos, curRot)
        self.viewMatrix.transform = util.ConvertTriToTupleMatrix(newViewMatrix)
        self.cameraPosition = newPos



    def MoveCamera(self, dx, dy, dz):
        rotMatrix = geo2.MatrixRotationYawPitchRoll(self.yaw, self.pitch, self.roll)
        relativeVector = geo2.Vec3Transform((dx, dy, dz), rotMatrix)
        newPos = geo2.Vec3Add(self.cameraPosition, relativeVector)
        curRot = (self.yaw, self.pitch, self.roll)
        newViewMatrix = self.CreateViewMatrix(newPos, curRot)
        self.viewMatrix.transform = util.ConvertTriToTupleMatrix(newViewMatrix)
        self.cameraPosition = newPos



    def RotateCamera(self, deltaYaw, deltaPitch, deltaRoll):
        newYaw = self.yaw + deltaYaw
        newPitch = max(min(self.pitch + deltaPitch, self.maxPitch), self.minPitch)
        newRoll = self.roll + deltaRoll
        newRot = (newYaw, newPitch, newRoll)
        newViewMatrix = self.CreateViewMatrix(self.cameraPosition, newRot)
        self.viewMatrix.transform = util.ConvertTriToTupleMatrix(newViewMatrix)
        self.yaw = newYaw % (2 * math.pi)
        self.roll = newRoll % (2 * math.pi)
        self.pitch = newPitch



    def Update(self):
        now = blue.os.GetTime()
        frameTime = float(now - self.lastUpdateTime) / const.SEC
        for (priority, behavior,) in self.cameraBehaviors:
            behavior.ProcessCameraUpdate(self, now, frameTime)

        self.lastUpdateTime = now




