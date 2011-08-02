import service
import collections
import geo2

class MovementService(service.Service):
    __guid__ = 'movement.movementService'
    __dependencies__ = ['machoNet']

    def ReportState(self, component, entity):
        if component.avatar:
            report = collections.OrderedDict()
            report['Position'] = ', '.join([ '%.2f' % f for f in component.avatar.pos ])
            report['Rotation (Yaw/Pitch/Roll)'] = ', '.join([ '%.2f' % f for f in geo2.QuaternionRotationGetYawPitchRoll(component.avatar.rot) ])
            report['Local Heading'] = ', '.join([ '%.2f' % f for f in component.avatar.localHeading ])
            report['Avatar Type'] = component.avatar.avatarType
            report['Move Mode'] = component.avatar.GetActiveMoveMode()
            report['Motion State'] = component.avatar.motionState
            report['Kynapse Name'] = component.avatar.kynapseName
            report['Is Allowed To Mode'] = component.avatar.allowedToMove
            report['Is Ready'] = component.avatar.isReady
            report['Is Portaling'] = component.avatar.isPortaling
            report['Is On Ground'] = component.avatar.onGround
            report['Is In Synced Anim'] = component.avatar.IsInSyncedAnim
            report['Max Speed'] = '%.2f' % component.avatar.maxSpeed
            report['Max Rotate'] = '%.2f' % component.avatar.maxRotate
            report['Jump Height'] = '%.2f' % component.avatar.jumpHeight
            report['Radius'] = '%.2f' % component.avatar.radius
            report['Height'] = '%.2f' % component.avatar.height
            return report




