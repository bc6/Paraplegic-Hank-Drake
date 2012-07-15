#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/math.py
import geo2
import math
import util
import blue

def FloatCloseEnough(a, b, epsilon = None):
    if not epsilon:
        epsilon = const.FLOAT_TOLERANCE
    return abs(a - b) < epsilon


def VectorCloseEnough(a, b):
    for i in range(len(a)):
        if not FloatCloseEnough(a[i], b[i]):
            return False

    return True


def TrinityMatrixCloseEnough(a, b):
    return FloatCloseEnough(a._11, b._11) and FloatCloseEnough(a._21, b._21) and FloatCloseEnough(a._31, b._31) and FloatCloseEnough(a._41, b._41) and FloatCloseEnough(a._12, b._12) and FloatCloseEnough(a._22, b._22) and FloatCloseEnough(a._32, b._32) and FloatCloseEnough(a._42, b._42) and FloatCloseEnough(a._13, b._13) and FloatCloseEnough(a._23, b._23) and FloatCloseEnough(a._33, b._33) and FloatCloseEnough(a._43, b._43) and FloatCloseEnough(a._14, b._14) and FloatCloseEnough(a._24, b._24) and FloatCloseEnough(a._34, b._34) and FloatCloseEnough(a._44, b._44)


def MatrixCloseEnough(a, b):
    for i in xrange(0, 4):
        for j in xrange(0, 4):
            if not FloatCloseEnough(a[i][j], b[i][j]):
                return False

    return True


def RotateQuatByYaw(oldRot, yawAngle):
    newRot = (0,
     math.sin(yawAngle / 2.0),
     0,
     math.cos(yawAngle / 2.0))
    return geo2.QuaternionMultiply(oldRot, newRot)


def CalculateShortestRotation(angle):
    angle = math.fmod(angle, 2 * math.pi)
    if angle <= -math.pi:
        angle += math.pi * 2
    elif angle > math.pi:
        angle -= math.pi * 2
    return angle


def BoundedRotateQuatByYaw(entityRotation, facingAngle, maxRotate):
    if abs(facingAngle) < 0.01:
        return entityRotation
    maxRotate = abs(maxRotate)
    facingAngle = CalculateShortestRotation(facingAngle)
    if maxRotate < abs(facingAngle):
        if facingAngle < 0:
            facingAngle = -maxRotate
        else:
            facingAngle = maxRotate
    return RotateQuatByYaw(entityRotation, facingAngle)


def GetLesserAngleBetweenYaws(first, second):
    return CalculateShortestRotation(second - first)


def GetDeltaAngleToFaceTarget(sourcePos, sourceRot, targetPos):
    targetVec = geo2.Vec3Subtract(targetPos, sourcePos)
    theta = GetYawAngleFromDirectionVector(targetVec)
    yaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(sourceRot)
    return GetLesserAngleBetweenYaws(yaw, theta)


def CreateDirectionVectorFromYawAngle(yaw):
    return (math.sin(yaw), 0.0, math.cos(yaw))


def CreateDirectionVectorFromYawAndPitchAngle(yaw, pitch):
    direction = (-math.sin(pitch) * math.cos(yaw), math.cos(pitch), -math.sin(pitch) * math.sin(yaw))
    return direction


def GetYawAngleFromDirectionVector(vec3):
    testVec = list(vec3)
    testVec[1] = 0.0
    testVec = list(geo2.Vec3Normalize(testVec))
    if testVec[2] >= 1.0:
        testVec[2] = 1.0
    elif testVec[2] <= -1.0:
        testVec[2] = -1.0
    yaw = math.acos(testVec[2])
    if testVec[0] < 0.0:
        yaw = math.pi * 2 - yaw
    return yaw


def GetPitchAngleFromDirectionVector(vec3):
    testVec = list(geo2.Vec3Normalize(vec3))
    if testVec[1] >= 1.0:
        testVec[1] = 1.0
    elif testVec[1] <= -1.0:
        testVec[1] = -1.0
    pitch = math.asin(testVec[1])
    return pitch


def GetNewQuatToFacePos(sourcePos, sourceRot, targetPos):
    deltaAngle = GetDeltaAngleToFaceTarget(sourcePos, sourceRot, targetPos)
    yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(sourceRot)
    yaw += deltaAngle
    return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)


def CalcLinearIntpValue(startVal, targetVal, startTime, curTime, howLong):
    endTime = startTime + howLong
    if curTime > endTime:
        return targetVal
    elif startTime > curTime:
        return startVal
    else:
        timeFactor = max(1.0 * (curTime - startTime) / howLong, 0)
        return startVal + timeFactor * (targetVal - startVal)


def CalcScaledValueOverInterval(startVal, targetVal, intervalLength, intervalRemaining, minFactor = None, maxFactor = None):
    if intervalLength == 0:
        return targetVal
    factor = 1.0 - 1.0 * intervalRemaining / intervalLength
    if minFactor:
        factor = max(factor, minFactor)
    if maxFactor:
        factor = min(factor, maxFactor)
    return startVal + (targetVal - startVal) * factor


def LineIntersectVerticalPlaneWithTwoPoints(lineV1, lineV2, planeV1, planeV2):
    v1 = planeV1
    v2 = planeV2
    v3 = geo2.Vector(*planeV1)
    v3.y += 1
    plane = geo2.PlaneFromPoints(v1, v2, v3)
    intersectionPoint = geo2.PlaneIntersectLine(plane, lineV1, lineV2)
    return intersectionPoint


def DecomposeMatrix(matrix):
    if hasattr(matrix, '__bluetype__') and matrix.__bluetype__ == 'trinity.TriMatrix':
        matrix = util.ConvertTriToTupleMatrix(matrix)
    scale, rot, pos = geo2.MatrixDecompose(matrix)
    rot = geo2.QuaternionRotationGetYawPitchRoll(rot)
    return (pos, rot, scale)


def ComposeMatrix(pos, rot, scale):
    return geo2.MatrixTransformation(None, None, scale, None, rot, pos)


def GetViewFrustumPlanes(viewProjMat):
    left = (viewProjMat[0][0] + viewProjMat[0][3],
     viewProjMat[1][0] + viewProjMat[1][3],
     viewProjMat[2][0] + viewProjMat[2][3],
     viewProjMat[3][0] + viewProjMat[3][3])
    right = (-viewProjMat[0][0] + viewProjMat[0][3],
     -viewProjMat[1][0] + viewProjMat[1][3],
     -viewProjMat[2][0] + viewProjMat[2][3],
     -viewProjMat[3][0] + viewProjMat[3][3])
    bottom = (viewProjMat[0][1] + viewProjMat[0][3],
     viewProjMat[1][1] + viewProjMat[1][3],
     viewProjMat[2][1] + viewProjMat[2][3],
     viewProjMat[3][1] + viewProjMat[3][3])
    top = (-viewProjMat[0][1] + viewProjMat[0][3],
     -viewProjMat[1][1] + viewProjMat[1][3],
     -viewProjMat[2][1] + viewProjMat[2][3],
     -viewProjMat[3][1] + viewProjMat[3][3])
    near = (viewProjMat[0][2] + viewProjMat[0][3],
     viewProjMat[1][2] + viewProjMat[1][3],
     viewProjMat[2][2] + viewProjMat[2][3],
     viewProjMat[3][2] + viewProjMat[3][3])
    far = (-viewProjMat[0][2] + viewProjMat[0][3],
     -viewProjMat[1][2] + viewProjMat[1][3],
     -viewProjMat[2][2] + viewProjMat[2][3],
     -viewProjMat[3][2] + viewProjMat[3][3])
    return [left,
     right,
     bottom,
     top,
     near,
     far]


exports = {}
exports['mathCommon.FloatCloseEnough'] = FloatCloseEnough
exports['mathCommon.RotateQuatByYaw'] = RotateQuatByYaw
exports['mathCommon.BoundedRotateQuatByYaw'] = BoundedRotateQuatByYaw
exports['mathCommon.GetDeltaAngleToFaceTarget'] = GetDeltaAngleToFaceTarget
exports['mathCommon.GetYawAngleFromDirectionVector'] = GetYawAngleFromDirectionVector
exports['mathCommon.GetPitchAngleFromDirectionVector'] = GetPitchAngleFromDirectionVector
exports['mathCommon.GetLesserAngleBetweenYaws'] = GetLesserAngleBetweenYaws
exports['mathCommon.CreateDirectionVectorFromYawAngle'] = CreateDirectionVectorFromYawAngle
exports['mathCommon.CreateDirectionVectorFromYawAndPitchAngle'] = CreateDirectionVectorFromYawAndPitchAngle
exports['mathCommon.CalcLinearIntpValue'] = CalcLinearIntpValue
exports['mathCommon.CalcScaledValueOverInterval'] = CalcScaledValueOverInterval
exports['mathCommon.VectorCloseEnough'] = VectorCloseEnough
exports['mathCommon.LineIntersectVerticalPlaneWithTwoPoints'] = LineIntersectVerticalPlaneWithTwoPoints
exports['mathCommon.TrinityMatrixCloseEnough'] = TrinityMatrixCloseEnough
exports['mathCommon.GetNewQuatToFacePos'] = GetNewQuatToFacePos
exports['mathCommon.GetViewFrustumPlanes'] = GetViewFrustumPlanes
exports['mathCommon.MatrixCloseEnough'] = MatrixCloseEnough
exports['mathCommon.DecomposeMatrix'] = DecomposeMatrix
exports['mathCommon.ComposeMatrix'] = ComposeMatrix