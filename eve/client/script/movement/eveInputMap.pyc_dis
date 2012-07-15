#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/movement/eveInputMap.py
import movement
import geo2
import math
import GameWorld
import mathCommon

class EveInputMap(movement.InputMap):
    __guid__ = 'movement.EveInputMap'
    AVATAR_COLLISION_RESTRICTION_ANGLE_DP = 0.15
    AVATAR_COLLISION_DETECTION_FEELER_LENGTH = 0.45
    AVATAR_COLLISION_DETECTION_FEELER_RADIUS = 0.1
    AVATAR_COLLISION_DETECTION_CAPSULE_HEIGHT_MOD = 0.23

    def NewDirectionObstacleCheck(self, destYaw, heading):
        entity = self.entityClient.GetPlayerEntity()
        gw = GameWorld.Manager.GetGameWorld(long(entity.scene.sceneID))
        posComp = entity.GetComponent('position')
        movComp = entity.GetComponent('movement')
        start = posComp.position
        start = geo2.Vec3Add(start, (0.0, self.AVATAR_COLLISION_DETECTION_CAPSULE_HEIGHT_MOD * movComp.characterController.height, 0.0))
        yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(posComp.rotation)
        direction = geo2.QuaternionRotationSetYawPitchRoll(yaw + destYaw, 0, 0)
        end = heading
        end = geo2.QuaternionTransformVector(direction, end)
        direction = end = geo2.Vec3Scale(end, self.AVATAR_COLLISION_DETECTION_FEELER_LENGTH)
        end = geo2.Vec3Add(end, start)
        hitResult = gw.SweptSphere(start, end, self.AVATAR_COLLISION_DETECTION_FEELER_RADIUS)
        result = False
        if hitResult:
            dotProduct = geo2.Vec3Dot(direction, hitResult[1])
            if abs(dotProduct) > self.AVATAR_COLLISION_RESTRICTION_ANGLE_DP:
                result = True
        return result

    def CheckStaticStateOK(self, staticIndex, destYaw):
        staticState = self.metaState[const.movement.METASTATE_STATIC_STATES][staticIndex]
        camOffset = staticState.get(const.movement.STATICSTATE_CAMERAOFFSET, 0.0) * math.pi / 180.0
        destYaw = destYaw + camOffset
        heading = staticState[const.movement.STATICSTATE_HEADING]
        if geo2.Vec3Length(heading):
            if self.NewDirectionObstacleCheck(destYaw, heading):
                staticIndex = self.GetDesiredState(0, 0, 0)
        return staticIndex