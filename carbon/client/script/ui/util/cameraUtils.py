import geo2
import mathCommon
import math
import util

def GetEntityYaw(entity):
    playerRot = entity.GetComponent('position').rotation
    (playerYaw, pitch, roll,) = geo2.QuaternionRotationGetYawPitchRoll(playerRot)
    playerYaw = playerYaw + math.pi / 2
    return playerYaw



def GetAngleFromEntityToCamera(entity, overrideYaw = None, offset = None):
    activeCamera = sm.GetService('cameraClient').GetActiveCamera()
    cameraYaw = -activeCamera.GetYaw()
    if overrideYaw:
        cameraYaw = overrideYaw
    if offset:
        cameraYaw = offset + cameraYaw
    playerYaw = GetEntityYaw(entity)
    retval = 0.0
    if playerYaw != None and cameraYaw != None:
        lesserYaw = mathCommon.GetLesserAngleBetweenYaws(playerYaw, cameraYaw)
        retval = lesserYaw
    return retval



def CalcDesiredPlayerHeading(heading):
    headingYaw = mathCommon.GetYawAngleFromDirectionVector(heading)
    activeCamera = sm.GetService('cameraClient').GetActiveCamera()
    cameraYaw = -activeCamera.GetYaw()
    desiredYaw = cameraYaw + headingYaw
    return desiredYaw



def GetAngleFromEntityToYaw(entity, yaw):
    lesserYaw = mathCommon.GetLesserAngleBetweenYaws(GetEntityYaw(entity), yaw)
    return lesserYaw


exports = util.AutoExports('cameraUtils', globals())

