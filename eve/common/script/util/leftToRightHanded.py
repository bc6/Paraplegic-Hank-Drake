import geo2
import math

def ConvertPosition(x, y, z):
    return (x, y, -z)



def ConvertSpherical(latitude, longitude):
    return (latitude, -longitude)


convertRotationMatrix = geo2.MatrixScaling(1.0, 1.0, -1.0)

def ConvertQuaternionRotation(rot):
    rotMatrix = geo2.MatrixRotationQuaternion(rot)
    tempMatrix = geo2.MatrixMultiply(convertRotationMatrix, rotMatrix)
    invRotMatrix = geo2.MatrixMultiply(tempMatrix, convertRotationMatrix)
    invRotQuat = geo2.QuaternionRotationMatrix(invRotMatrix)
    return invRotQuat



def ConvertYawPitchRollRotation(yaw, pitch, roll):
    (yaw, pitch, roll,) = geo2.Vec3Scale((yaw, pitch, roll), math.pi / 180)
    quaternion = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
    quaternion = ConvertQuaternionRotation(quaternion)
    return geo2.Vec3Scale(geo2.QuaternionRotationGetYawPitchRoll(quaternion), 180 / math.pi)



def GetYawPitchRoll(row):
    yaw = getattr(row, 'yaw', None)
    pitch = getattr(row, 'pitch', None)
    roll = getattr(row, 'roll', None)
    if yaw is None and pitch is None and roll is None:
        return 
    if yaw is None:
        yaw = 0
    if pitch is None:
        pitch = 0
    if roll is None:
        roll = 0
    return (yaw, pitch, roll)



def GetXYZ(row):
    x = getattr(row, 'x', None)
    y = getattr(row, 'y', None)
    z = getattr(row, 'z', None)
    if x is None and y is None and z is None:
        return 
    if x is None:
        x = 0
    if y is None:
        y = 0
    if z is None:
        z = 0
    return (x, y, z)


exports = {'lh2rhUtil.ConvertPosition': ConvertPosition,
 'lh2rhUtil.ConvertSpherical': ConvertSpherical,
 'lh2rhUtil.ConvertQuaternionRotation': ConvertQuaternionRotation,
 'lh2rhUtil.ConvertYawPitchRollRotation': ConvertYawPitchRollRotation,
 'lh2rhUtil.GetYawPitchRoll': GetYawPitchRoll,
 'lh2rhUtil.GetXYZ': GetXYZ}

