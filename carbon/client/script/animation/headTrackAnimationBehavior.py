import animation
import aiming
import perception
import geo2
import mathCommon
import math
MAXIMUM_HEAD_LOOK_ANGLE_YAW = 130.0 / 180.0 * math.pi
MAXIMUM_HEAD_LOOK_ANGLE_YAW_MOVING = 60.0 / 180.0 * math.pi
MAXIMUM_HEAD_LOOK_ANGLE_PITCH = 90.0 / 180.0 * math.pi
MAXIMUM_HEAD_LOOK_ANGLE_PITCH_MOVING = 60.0 / 180.0 * math.pi

class HeadTrackAnimationBehavior(animation.animationBehavior):
    __guid__ = 'animation.headTrackAnimationBehavior'

    def __init__(self):
        animation.animationBehavior.__init__(self)
        self.entityService = sm.GetService('entityClient')
        self.aimingClient = sm.GetService('aimingClient')
        self.perceptionClient = sm.GetService('perceptionClient')



    def Update(self, controller):
        if hasattr(controller.entityRef, 'aiming'):
            debugBoneName = 'fj_eyeballLeft'
            gazeAtEntityID = self.aimingClient.GetTargetEntityID(controller.entityRef, const.aiming.AIMING_VALID_TARGET_GAZE_ID)
            if gazeAtEntityID:
                gazeAtEntity = self.entityService.FindEntityByID(gazeAtEntityID)
                if gazeAtEntity:
                    sensorPos = geo2.Vector(*controller.entityRef.position.position)
                    sensorPos = sensorPos + self.perceptionClient.GetSensorOffset(controller.entityRef)
                    focusPos = geo2.Vector(*gazeAtEntity.position.position)
                    focusPos = focusPos + self.perceptionClient.GetSensorOffset(gazeAtEntity)
                    headTransform = controller.animationNetwork.GetBoneTransform(debugBoneName)
                    if headTransform is None:
                        return 
                    (headTranslation, headRotation,) = headTransform
                    useBlendToHeadBone = False
                    if useBlendToHeadBone:
                        workPos = geo2.Vec3Subtract(focusPos, controller.entPos)
                        entRotInvQuat = geo2.QuaternionInverse(controller.entRot)
                        entRotInvQuat = geo2.QuaternionNormalize(entRotInvQuat)
                        workPos = geo2.QuaternionTransformVector(entRotInvQuat, workPos)
                        workPos = geo2.Vec3Subtract(workPos, headTranslation)
                        headRotInvQuat = geo2.QuaternionInverse(headRotation)
                        headRotInvQuat = geo2.QuaternionNormalize(headRotInvQuat)
                        workPos = geo2.QuaternionTransformVector(headRotInvQuat, workPos)
                        relativeLookAtYaw = mathCommon.GetYawAngleFromDirectionVector(workPos)
                        relativeLookAtPitch = mathCommon.GetPitchAngleFromDirectionVector(workPos)
                    else:
                        sensorToFocusVec = geo2.Vec3Subtract(focusPos, sensorPos)
                        yawToFocus = mathCommon.GetYawAngleFromDirectionVector(sensorToFocusVec)
                        pitchToFocus = mathCommon.GetPitchAngleFromDirectionVector(sensorToFocusVec)
                        (entityYaw, trash, trash,) = geo2.QuaternionRotationGetYawPitchRoll(controller.entRot)
                        relativeLookAtYaw = yawToFocus - entityYaw
                        relativeLookAtPitch = pitchToFocus
                    relativeLookAtYaw = math.fmod(relativeLookAtYaw, 2 * math.pi)
                    relativeLookAtPitch = math.fmod(relativeLookAtPitch, 2 * math.pi)
                    if relativeLookAtYaw < 0:
                        relativeLookAtYaw = relativeLookAtYaw + 2 * math.pi
                    if relativeLookAtPitch < 0:
                        relativeLookAtPitch = relativeLookAtPitch + 2 * math.pi
                    if relativeLookAtYaw > math.pi:
                        relativeLookAtYaw = relativeLookAtYaw - 2 * math.pi
                    if relativeLookAtPitch > math.pi:
                        relativeLookAtPitch = relativeLookAtPitch - 2 * math.pi
                    if geo2.Vec3LengthSq(controller.entityRef.movement.physics.velocity) > 0.0:
                        maxYaw = MAXIMUM_HEAD_LOOK_ANGLE_YAW_MOVING
                        maxPitch = MAXIMUM_HEAD_LOOK_ANGLE_PITCH_MOVING
                    else:
                        maxYaw = MAXIMUM_HEAD_LOOK_ANGLE_YAW
                        maxPitch = MAXIMUM_HEAD_LOOK_ANGLE_PITCH
                    if abs(relativeLookAtYaw) < maxYaw and abs(relativeLookAtPitch) < maxPitch:
                        controller.SetControlParameter('Aim_X', -relativeLookAtYaw)
                        controller.SetControlParameter('Aim_Y', -relativeLookAtPitch)
                        controller.SetControlParameter('HeadLookWeight', 1)
                        aimingManager = self.aimingClient.GetAimingManager(controller.entityRef.scene.sceneID)
                        if aimingManager.IsDebugRendering():
                            self.aimingClient.GetAimingManager(controller.entityRef.scene.sceneID).SetDebugUsedParams(controller.entityRef.entityID, relativeLookAtYaw, -relativeLookAtPitch, maxYaw, maxPitch, headTranslation, headRotation)
                        return 
            controller.SetControlParameter('HeadLookWeight', 0)
            aimingManager = self.aimingClient.GetAimingManager(controller.entityRef.scene.sceneID)
            if aimingManager.IsDebugRendering():
                (translation, orientation,) = controller.entityRef.animation.updater.network.GetBoneTransform(debugBoneName)
                self.aimingClient.GetAimingManager(controller.entityRef.scene.sceneID).SetDebugUsedParams(controller.entityRef.entityID, -99, -99, MAXIMUM_HEAD_LOOK_ANGLE_YAW, MAXIMUM_HEAD_LOOK_ANGLE_PITCH, translation, orientation)




