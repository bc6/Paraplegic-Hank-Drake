#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/animUtils.py
import geo2
import mathCommon
import math
import blue
import random
import uthread
import log
import util

def IsSynchedAnim(animInfo):
    return const.animation.METADATA_SYNCHRONIZED in animInfo and animInfo[const.animation.METADATA_SYNCHRONIZED] == True


def IsFixedMoveAnimation(animInfo, entityType):
    return animInfo is not None and entityType in animInfo and (const.animation.METADATA_END_OFFSET in animInfo[entityType] or const.animation.METADATA_YAW in animInfo[entityType])


def IsLockedMovementAnimation(animInfo):
    if animInfo:
        return animInfo.get(const.animation.METADATA_LOCK_MOVEMENT, True)
    return False


def GetQuatFromDirection(sourcePos, targetPos):
    yaw = GetYawFromDirection(sourcePos, targetPos)
    return geo2.QuaternionRotationSetYawPitchRoll(yaw, 0.0, 0.0)


def GetYawFromDirection(sourcePos, targetPos):
    targetVec = geo2.Vec3Subtract(targetPos, sourcePos)
    return mathCommon.GetYawAngleFromDirectionVector(geo2.Vector(*targetVec))


def GetSynchedAnimStartLocation(sourcePos, sourceRot, targetPos, targetRot, animInfo):
    relVec = geo2.Vec3Subtract(sourcePos, targetPos)
    curDist = geo2.Vec3Length(relVec)
    if curDist <= 0.01:
        sourcePos = geo2.Vec3Add(targetPos, (0, 0, -1))
        relVec = geo2.Vec3Subtract(sourcePos, targetPos)
    entName = const.animation.ATTACKER_NAME
    if entName in animInfo and const.animation.METADATA_TURN_TO_FACE in animInfo[entName] and animInfo[entName][const.animation.METADATA_TURN_TO_FACE] == False:
        newSourceRot = sourceRot
    else:
        newSourceRot = GetQuatFromDirection(sourcePos, targetPos)
    entName = const.animation.VICTIM_NAME
    if entName in animInfo and const.animation.METADATA_TURN_TO_FACE in animInfo[entName] and animInfo[entName][const.animation.METADATA_TURN_TO_FACE] == False:
        newTargetRot = targetRot
        newTargetYaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(targetRot)
    else:
        newTargetRot = GetQuatFromDirection(targetPos, sourcePos)
        if entName in animInfo and const.animation.METADATA_START_OFFSET_YAW in animInfo[entName]:
            degrees = animInfo[entName][const.animation.METADATA_START_OFFSET_YAW]
            offsetYaw = math.pi * -degrees / 180.0
            offsetRot = geo2.QuaternionRotationSetYawPitchRoll(offsetYaw, 0.0, 0.0)
            newTargetRot = geo2.QuaternionMultiply(newTargetRot, offsetRot)
    distance = 0.5
    if const.animation.METADATA_START_DISTANCE in animInfo:
        distance = animInfo[const.animation.METADATA_START_DISTANCE]
    entName = const.animation.VICTIM_NAME
    if entName in animInfo and const.animation.METADATA_START_OFFSET_YAW in animInfo[entName]:
        if '/righthanded' in blue.pyos.GetArg():
            front = (0, 0, distance)
        else:
            front = (0, 0, -distance)
        degrees = animInfo[entName][const.animation.METADATA_START_OFFSET_YAW]
        radians = math.pi * degrees / 180.0
        offsetRot = geo2.QuaternionRotationSetYawPitchRoll(radians, 0.0, 0.0)
        yawOffsetQuat = geo2.QuaternionMultiply(newTargetRot, offsetRot)
        radOffset = geo2.QuaternionTransformVector(yawOffsetQuat, front)
        newSourcePos = geo2.Vec3Add(targetPos, radOffset)
        newSourceRot = GetQuatFromDirection(newSourcePos, targetPos)
    else:
        direction = geo2.Vec3Normalize(relVec)
        newSourcePos = geo2.Vec3Add(targetPos, (distance * direction[0], distance * direction[1], distance * direction[2]))
    entName = const.animation.ATTACKER_NAME
    if entName in animInfo and const.animation.METADATA_START_OFFSET_YAW in animInfo[entName]:
        degrees = animInfo[entName][const.animation.METADATA_START_OFFSET_YAW]
        radians = math.pi * -degrees / 180.0
        offsetRot = geo2.QuaternionRotationSetYawPitchRoll(radians, 0.0, 0.0)
        newSourceRot = geo2.QuaternionMultiply(newSourceRot, offsetRot)
    return (newSourcePos,
     newSourceRot,
     targetPos,
     newTargetRot)


def TransformAccumulatedAnimFromEnt(ent, animInfo, entityType):
    if not ent or not ent.HasComponent('movement'):
        return
    entPos = ent.GetComponent('position').position
    entRot = ent.GetComponent('position').rotation
    offsetXZ = animInfo[entityType][const.animation.METADATA_END_OFFSET]
    offsetPos = (0.01 * offsetXZ[0], 0.0, 0.01 * offsetXZ[1])
    offsetYaw = animInfo[entityType][const.animation.METADATA_YAW]
    return TransformAccumulatedAnimFromPos(entPos, entRot, offsetPos, offsetYaw)


def TransformAccumulatedAnimFromPos(curPos, curRot, offsetTranslation, offsetYaw):
    offsetYaw = offsetYaw * math.pi / 180.0
    trajRot = geo2.QuaternionRotationSetYawPitchRoll(offsetYaw, 0.0, 0.0)
    offsetPosRotated = geo2.QuaternionTransformVector(curRot, offsetTranslation)
    newPos = geo2.Vec3Add(curPos, offsetPosRotated)
    newRot = geo2.QuaternionMultiply(trajRot, curRot)
    return (newPos, newRot)


def GetSynchedAnimEndingDeltas(animInfo):
    atkPos = (0.0, 0.0, 0.0)
    atkRot = geo2.QuaternionIdentity()
    vicPos = (0.0, 0.0, -1.0)
    vicRot = geo2.QuaternionIdentity()
    atkPos, atkRot, vicPos, vicRot = GetSynchedAnimStartLocation(atkPos, atkRot, vicPos, vicRot, animInfo)
    offsetXZ = animInfo[const.animation.ATTACKER_NAME][const.animation.METADATA_END_OFFSET]
    offsetPos = (0.01 * offsetXZ[0], 0.0, 0.01 * offsetXZ[1])
    atkPos, atkRot = TransformAccumulatedAnimFromPos(atkPos, atkRot, offsetPos, animInfo[const.animation.ATTACKER_NAME][const.animation.METADATA_YAW])
    offsetXZ = animInfo[const.animation.VICTIM_NAME][const.animation.METADATA_END_OFFSET]
    offsetPos = (0.01 * offsetXZ[0], 0.0, 0.01 * offsetXZ[1])
    vicPos, vicRot = TransformAccumulatedAnimFromPos(vicPos, vicRot, offsetPos, animInfo[const.animation.VICTIM_NAME][const.animation.METADATA_YAW])
    deltaPos = geo2.Vec3Subtract(vicPos, atkPos)
    deltaPos = geo2.QuaternionTransformVector(atkRot, deltaPos)
    deltaRot = geo2.QuaternionMultiply(vicRot, atkRot)
    return (deltaPos, deltaRot)


def GetAnimInfoByName(animationDict, animName):
    if animationDict is None:
        pass
    if animName not in animationDict:
        return animationDict[const.animation.DEFAULT_ANIMATION_NAME]
    return animationDict[animName]


def CallbackOnAnimationFinish(animInfo, callbackBundle):
    uthread.new(_CallbackOnAnimationFinish_NoBlock, animInfo, callbackBundle).context = 'animUtils::CallbackOnAnimationFinish'


def _CallbackOnAnimationFinish_NoBlock(animInfo, callbackBundle):
    duration = int(animInfo[const.animation.METADATA_DURATION] * 1000)
    blue.pyos.synchro.SleepWallclock(duration)
    method = callbackBundle[0]
    method(*callbackBundle[1:])


def GetRampUpAndRampDownFromAnimationName(animationName, animationDict):
    if animationName not in animationDict:
        return (0L, 0L, const.animation.DEFAULT_ANIMATION_NAME)
    animInfo = GetModifiedAnimInfo(animationDict[animationName])
    duration = animInfo[const.animation.METADATA_DURATION]
    rampUp = long(duration * const.SEC * animInfo[const.animation.METADATA_IMPACT_POINT])
    rampDown = long(duration * const.SEC - rampUp)
    return (rampUp, rampDown, animInfo)


def GetEntityTrajectoryPosition(modelReference, animationNetwork):
    mat = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (modelReference.scaling[0], modelReference.scaling[1], modelReference.scaling[2]), (0, 0, 0), (modelReference.rotation[0],
     modelReference.rotation[1],
     modelReference.rotation[2],
     modelReference.rotation[3]), (modelReference.translation[0], modelReference.translation[1], modelReference.translation[2]))
    matTuple = mat[0] + mat[1] + mat[2] + mat[3]
    accumulated = animationNetwork.GetAccumulatedTrajectory(matTuple)[0]
    return accumulated


def ShouldSnapEntityPositionToGround(entity):
    return entity.GetComponent('animation').inThrow


def GetSynchedAnimPosition(entity):
    model = sm.GetService('animationClient').GetEntityModel(entity.entityID)
    if model is not None:
        pos = geo2.Vector(model.translation[0], model.translation[1], model.translation[2])
        if ShouldSnapEntityPositionToGround(entity):
            pos = geo2.Vector(*GetEntityTrajectoryPosition(model, entity.GetComponent('animation').controller.animationNetwork))
            height = sm.GetService('gameWorldClient').GetFloorHeight(pos, entity.scene.sceneID)
            pos.y = height
        return pos
    return entity.GetComponent('position').position


def SleepUntilImpact(animInfo):
    duration = animInfo[const.animation.METADATA_DURATION]
    impactPoint = animInfo[const.animation.METADATA_IMPACT_POINT]
    duration = int(impactPoint * duration * 1000)
    blue.pyos.synchro.SleepWallclock(duration)


def GetUprightCapsulePosAndRot(curPos, curRot, floorHeight):
    yaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(curRot)
    rot = geo2.QuaternionRotationSetYawPitchRoll(yaw, 0, 0)
    pos = geo2.Vector(*curPos)
    adjustment = geo2.QuaternionTransformVector(curRot, adjustment)
    pos = pos + adjustment
    pos.y = floorHeight
    return (pos, rot)


def CanWalkToStartPositionForSynchedAnim(sourceEnt, targetEnt, animInfo, callback, callbackArgs):
    gw = sm.GetService('gameWorld' + boot.role.title()).GetGameWorld(sourceEnt.scene.sceneID)
    sourceEntityPosition = sourceEnt.GetComponent('position').position
    sourceEntityRotation = sourceEnt.GetComponent('position').rotation
    targetEntityPosition = targetEnt.GetComponent('position').position
    targetEntityRotation = targetEnt.GetComponent('position').rotation
    endPos, trash, trash, trash = GetSynchedAnimStartLocation(sourceEntityPosition, sourceEntityRotation, targetEntityPosition, targetEntityRotation, animInfo)
    sourceEnt.GetComponent('movement').characterController.CollisionCheckMovementPosition(endPos)
    gw.CanPathTo(sourceEntityPosition, endPos, const.AVATAR_RADIUS, const.AVATAR_HEIGHT, callback, callbackArgs)


def GetModifiedAnimInfoByName(staticActionData, animName, atkEnt = None, vicEnt = None):
    animInfo = staticActionData.GetAnimInfoByName(animName)
    return GetModifiedAnimInfo(animInfo, atkEnt, vicEnt)


def GetModifiedAnimInfo(animInfo, atkEnt = None, vicEnt = None):
    victimIndex = const.animation.METADATA_ON_VICTIM_INDEX
    listName = const.animation.METADATA_INDEXED_LIST
    index = 0
    if victimIndex in animInfo:
        if None != vicEnt and hasattr(vicEnt.animation, 'controller'):
            animParm = animInfo[victimIndex]
            parm = vicEnt.animation.controller.GetControlParameter(animParm, forceLookup=True)
            index = int(parm * len(animInfo[listName]) - 0.1)
        elif listName in animInfo:
            best = None
            bestDur = 0
            for info in animInfo[listName]:
                duration = info[const.animation.METADATA_DURATION]
                if None != duration and duration > bestDur:
                    best = info
                    bestDur = duration

            if None != best:
                return best
    if listName in animInfo:
        animInfo = animInfo[listName][index]
    if const.animation.METADATA_IMPACT_POINT not in animInfo:
        animInfo[const.animation.METADATA_IMPACT_POINT] = 0.5
    if const.animation.METADATA_START_DISTANCE not in animInfo:
        animInfo[const.animation.METADATA_START_DISTANCE] = 0.5
    return animInfo


def GetRelativeLookAtVector(sourcePosition, sourceRotation, targetPosition):
    lookAtVector = geo2.Vec3Subtract(targetPosition, sourcePosition)
    yaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(sourceRotation)
    yaw = -yaw
    relativeLookAtVector = (lookAtVector[0] * math.cos(yaw) + lookAtVector[2] * math.sin(yaw), lookAtVector[1], -lookAtVector[0] * math.sin(yaw) + lookAtVector[2] * math.cos(yaw))
    return relativeLookAtVector


def GetMaxLookAtWeight_Facing(ent, targetPos):
    sourcePos = ent.GetComponent('position').position
    sourceRot = ent.GetComponent('position').rotation
    source2Target = geo2.Vec3Subtract(targetPos, sourcePos)
    source2Target = geo2.Vec3Normalize(source2Target)
    facingDir = mathCommon.CreateDirectionVectorFromYawAngle(geo2.QuaternionRotationGetYawPitchRoll(sourceRot)[0])
    dot = geo2.Vec3Dot(source2Target, facingDir)
    return max(dot, 0)


exports = util.AutoExports('animUtils', globals())