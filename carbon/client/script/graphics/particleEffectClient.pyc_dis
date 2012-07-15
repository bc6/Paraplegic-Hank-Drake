#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/particleEffectClient.py
import service
import zaction
import GameWorld
import trinity
import locks
import uthread
import blue
import util
import geo2
import math
import types

class ParticleEffectClient(service.Service):
    __guid__ = 'svc.particleEffectClient'
    __displayname__ = 'Particle Effect Client Service'
    __dependencies__ = ['graphicClient', 'entityClient', 'attributeClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.idCounter = 0L
        self.activeParticleEffects = {}
        self.timedParticleEffects = []
        self.activeParticlesSemaphore = uthread.CriticalSection('CriticalSection for dynamic particle effects')
        self.updateTaskletLock = locks.Event('particleEffectClientUpdateTaskletLock')

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        uthread.new(self._UpdateTasklet).context = 'particleEffectClient::Run'
        procArgs = ('ENTID', 'redFile', 'boneName', 'duration', 'xOffset', 'yOffset', 'zOffset', 'yawOffset', 'pitchOffset', 'rollOffset', 'ignoreTransform', 'effectIDProp')
        GameWorld.RegisterPythonActionProc('ApplyParticleEffect', self.ApplyParticleEffect, procArgs, True)
        GameWorld.RegisterPythonActionProc('RemoveParticleEffect', self.RemoveParticleEffectProc, ('effectIDProp',))

    def _GetNextEffectID(self):
        self.idCounter += 1
        return self.idCounter

    def _PopTimedParticleEffect(self):
        self._RemoveParticleEffect(self.timedParticleEffects[0].effectID)

    def _RemoveParticleEffect(self, effectID):
        try:
            effectData = self.activeParticleEffects.pop(effectID)
        except KeyError:
            self.LogWarn('Particle Effect Client: Trying to remove invalid effect ID!')
            return

        if effectData in self.timedParticleEffects:
            self.timedParticleEffects.remove(effectData)
        scene = self.graphicClient.GetScene(effectData.sceneID)
        scene.RemoveDynamic(effectData.trinityObject)
        if effectData.curveSet:
            scene.RemoveCurveSetFromScene(effectData.curveSet)

    def OnGraphicSettingsChanged(self, *args):
        if sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True):
            return
        with self.activeParticlesSemaphore:
            map(self._RemoveParticleEffect, self.activeParticleEffects.keys())
        self.updateTaskletLock.set()

    def _UpdateTasklet(self):
        while True:
            blue.synchro.Yield()
            self.updateTaskletLock.clear()
            if self.timedParticleEffects:
                with self.activeParticlesSemaphore:
                    effectData = self.timedParticleEffects[0]
                    currentTime = blue.os.GetWallclockTimeNow()
                    if effectData.expireTime < currentTime:
                        self._PopTimedParticleEffect()
                        continue
                timeLeft = effectData.expireTime - currentTime
                timeLeft = float(timeLeft) / const.SEC
                self.updateTaskletLock.wait(timeLeft)
            else:
                self.updateTaskletLock.wait()

    def RemoveParticleEffectProc(self, effectIDProp):
        if not sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True):
            return True
        effectID = GameWorld.GetPropertyForCurrentPythonProc(effectIDProp)
        if effectID is not None:
            removeEffectTasklet = uthread.new(self._RemoveParticleEffectProcTasklet, effectID)
            removeEffectTasklet.context = 'particleEffectClient::RemoveParticleEffectProc'
            return True
        return False

    def _RemoveParticleEffectProcTasklet(self, effectID):
        with self.activeParticlesSemaphore:
            self._RemoveParticleEffect(effectID)

    def ApplyParticleEffect(self, *args):
        if not sm.GetService('device').GetAppFeatureState('Interior.ParticlesEnabled', True):
            return True
        entityID, effectFilePath, boneName, duration, xOffset, yOffset, zOffset = args[:7]
        yawOffset, pitchOffset, rollOffset, ignoreTransform, effectStringID = args[7:]
        effectID = self._GetNextEffectID()
        zaction.AddPropertyForCurrentPythonProc({effectStringID: effectID})
        translation = geo2.MatrixTranslation(xOffset, yOffset, zOffset)
        rotation = geo2.MatrixRotationYawPitchRoll(math.radians(yawOffset), math.radians(pitchOffset), math.radians(rollOffset))
        offset = geo2.MatrixMultiply(rotation, translation)
        with self.activeParticlesSemaphore:
            trinityObject = trinity.Load(effectFilePath)
            entity = self.entityClient.FindEntityByID(entityID)
            scene = self.graphicClient.GetScene(entity.scene.sceneID)
            scene.AddDynamic(trinityObject)
            curveSet = None
            positionComponent = entity.GetComponent('position')
            if boneName or positionComponent:
                curveSet = trinity.TriCurveSet()
                scene.AddCurveSetToScene(curveSet)
                if boneName:
                    paperDollComponent = entity.GetComponent('paperdoll')
                    model = paperDollComponent.doll.avatar
                    curve = trinity.Tr2BoneMatrixCurve()
                    curve.skinnedObject = model
                    curve.bone = boneName
                    if not ignoreTransform:
                        offset = geo2.MatrixMultiply(offset, trinityObject.transform)
                    curve.transform = offset
                else:
                    curve = GameWorld.PositionComponentCurve()
                    curve.positionComponent = positionComponent
                    curve.positionOffset = geo2.Vector(xOffset, yOffset, zOffset)
                    curve.rotationOffset = geo2.QuaternionRotationSetYawPitchRoll(yawOffset, pitchOffset, rollOffset)
                bind = trinity.TriValueBinding()
                bind.destinationObject = trinityObject
                bind.destinationAttribute = 'transform'
                bind.sourceObject = curve
                bind.sourceAttribute = 'currentValue'
                curveSet.curves.append(curve)
                curveSet.bindings.append(bind)
                curveSet.Play()
            expireTime = blue.os.GetWallclockTime() + duration * const.MSEC
            effectData = util.KeyVal(effectID=effectID, entityID=entityID, effectFilePath=effectFilePath, expireTime=expireTime, offset=offset, trinityObject=trinityObject, sceneID=entity.scene.sceneID, curveSet=curveSet)
            self.activeParticleEffects[effectID] = effectData
            if duration > 0:
                self.timedParticleEffects.append(effectData)
                self.timedParticleEffects.sort(key=lambda entry: entry.expireTime)
                self.updateTaskletLock.set()
            self._ConnectEffectCurveSets(effectData, effectStringID)
        return True

    def _CreateAttributeBinding(self, entityID, attributeID, binding):

        def CopyAttribute(source, dest):
            dest.value = self.attributeClient.GetAttributeValueFromEntityByID(attributeID, entityID)

        binding.copyValueCallable = lambda source, dest: CopyAttribute(source, dest)

    def _CheckForAttributeBinding(self, entityID, attrName, binding):
        if 'Tr2FloatParameter' == type(binding.destinationObject).__name__:
            attributeID = self.attributeClient.GetAttributeIDFromName(attrName)
            if attributeID is not None:
                self._CreateAttributeBinding(entityID, attributeID, binding)
                return True
        return False

    def _ConnectEffectCurveSets(self, effectData, effectStringID):
        if not hasattr(effectData.trinityObject, 'curveSets'):
            return
        for curveSet in effectData.trinityObject.curveSets:
            removableBindings = []
            for binding in curveSet.bindings:
                typename = type(binding.sourceObject).__name__
                if typename.startswith('Tr2PyBindingSentinel'):
                    if 'Tr2PyBindingSentinelFloat' == typename:
                        if self._CheckForAttributeBinding(effectData.entityID, binding.sourceObject.name, binding):
                            continue
                    prop = zaction.GetPropertyForCurrentPythonProc(effectStringID + '.' + binding.sourceObject.name)
                    if prop is None:
                        prop = zaction.GetPropertyForCurrentPythonProc(binding.sourceObject.name)
                    if prop is not None:
                        if 'Tr2PyBindingSentinelFloat' == typename:
                            binding.sourceObject.value = prop
                        elif type(prop) == types.ListType:
                            if 'Tr2PyBindingSentinelVector2' == typename and len(prop) >= 2:
                                binding.sourceObject.value = prop[:2]
                            elif 'Tr2PyBindingSentinelVector3' == typename and len(prop) >= 3:
                                binding.sourceObject.value = prop[:3]
                            elif 'Tr2PyBindingSentinelVector4' == typename and len(prop) >= 4:
                                binding.sourceObject.value = prop[:4]
                            else:
                                self.LogWarn('Found Tr2PyBindingSentinel for a particle effect and matching list property, but types or list lengths do not match!', binding.sourceObject.name, typename, type(prop))
                        else:
                            self.LogWarn('Found Tr2PyBindingSentinel for a particle effect and matching property, but types do not match!', binding.sourceObject.name, typename, type(prop))
                    else:
                        self.LogWarn('Found Tr2PyBindingSentinel for a particle effect and no matching attribute or property!', binding.sourceObject.name, typename)
                    removableBindings.append(binding)

            curveSet.Update()
            for binding in removableBindings:
                curveSet.bindings.remove(binding)


exports = {'actionProcTypes.ApplyParticleEffect': zaction.ProcTypeDef(isMaster=True, procCategory='Graphics', displayName='Apply Particle Effect', properties=[zaction.ProcPropertyTypeDef('redFile', 'S', userDataType=None, isPrivate=True, displayName='Red File'),
                                         zaction.ProcPropertyTypeDef('duration', 'I', userDataType=None, isPrivate=True, displayName='Duration (milliseconds)'),
                                         zaction.ProcPropertyTypeDef('boneName', 'S', userDataType=None, isPrivate=True, displayName='Bone Name'),
                                         zaction.ProcPropertyTypeDef('xOffset', 'F', userDataType=None, isPrivate=True, displayName='X Offset'),
                                         zaction.ProcPropertyTypeDef('yOffset', 'F', userDataType=None, isPrivate=True, displayName='Y Offset'),
                                         zaction.ProcPropertyTypeDef('zOffset', 'F', userDataType=None, isPrivate=True, displayName='Z Offset'),
                                         zaction.ProcPropertyTypeDef('yawOffset', 'F', userDataType=None, isPrivate=True, displayName='Yaw Offset (deg)'),
                                         zaction.ProcPropertyTypeDef('pitchOffset', 'F', userDataType=None, isPrivate=True, displayName='Pitch Offset (deg)'),
                                         zaction.ProcPropertyTypeDef('rollOffset', 'F', userDataType=None, isPrivate=True, displayName='Roll Offset (deg)'),
                                         zaction.ProcPropertyTypeDef('ignoreTransform', 'B', userDataType=None, isPrivate=True, displayName='Ignore Effect Transform'),
                                         zaction.ProcPropertyTypeDef('effectIDProp', 'S', userDataType=None, isPrivate=True, displayName='Effect ID Storage Property')], description='Creates a particle effect on the entity. Effect will offset from entity position if Bone Name is omitted.'),
 'actionProcTypes.RemoveParticleEffect': zaction.ProcTypeDef(isMaster=True, procCategory='Graphics', displayName='Remove Particle Effect', properties=[zaction.ProcPropertyTypeDef('effectIDProp', 'S', userDataType=None, isPrivate=True, displayName='Effect ID Storage Property')], description='Removes a particle effect on the entity. This uses a previously stored effect ID in the specified property.')}