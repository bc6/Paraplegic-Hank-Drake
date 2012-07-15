#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/parklife/damageSvc.py
import service
import base
import blue
import util
import log
SECOND = 10000000L

class DamageService(service.Service):
    __guid__ = 'svc.damage'
    __exportedcalls__ = {'GetTargetLocators': [],
     'GetDamageLocatorGeneratorTransform': [],
     'SetLODTargetLevel': [],
     'SetLocatorCacheTime': [],
     'GenerateDamageLocators': []}
    __notifyevents__ = ['DoBallRemove', 'ProcessSessionChange']
    __dependencies__ = ['michelle']

    def __init__(self):
        service.Service.__init__(self)
        self.targets = {}
        self.failedTargets = {}
        self.targetResultCacheTime = 5000.0
        self.targetLODLevel = 1
        self.generatedDamageLocators = 40

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)

    def Stop(self, ms):
        service.Service.Stop(self)

    def DoBallRemove(self, ball, slimItem, terminal):
        removeList = []
        for key in self.targets:
            if key[0] == ball.id or key[1] == ball.id:
                removeList.append(key)

        for key in removeList:
            del self.targets[key]

        if ball.id in self.failedTargets:
            del self.failedTargets[ball.id]

    def ProcessSessionChange(self, isremote, session, change):
        self.targets = {}
        self.failedTargets = {}

    def SetLODTargetLevel(self, level):
        pass

    def SetLocatorCacheTime(self, time):
        pass

    def GetTargetLocators(self, attackerID, targetID, locatorVariance = 1):
        timer = blue.pyos.taskletTimer.EnterTasklet('DamageService::GetTargetLocators')
        result = []
        try:
            targetBall = sm.GetService('michelle').GetBall(targetID)
            targetModel = getattr(targetBall, 'model', None)
            attackerBall = sm.GetService('michelle').GetBall(attackerID)
            attackerModel = getattr(attackerBall, 'model', None)
            if targetBall is None:
                self.LogError('DamageService::GetTargetLocators cannot find ball of targetID', targetID)
                return []
            if targetModel is None:
                self.LogError('DamageService::GetTargetLocators target ball has no model', targetID)
                return []
            if attackerBall is None:
                self.LogError('DamageService::GetTargetLocators cannot find ball of attackerID', attackerID)
                return []
            if attackerModel is None:
                self.LogError('DamageService::GetTargetLocators attacker ball has no model', attackerID)
                return []
            if (targetID, attackerID) in self.targets:
                cachedResultTime, cachedResultList = self.targets[targetID, attackerID]
                if blue.os.TimeDiffInMs(cachedResultTime, blue.os.GetWallclockTimeNow()) < self.targetResultCacheTime:
                    if len(cachedResultList) >= locatorVariance:
                        return cachedResultList[:locatorVariance]
                if targetID in self.failedTargets:
                    return [targetModel]
                del self.targets[targetID, attackerID]
            result = [targetModel]
            if hasattr(targetModel, 'activeLevel'):
                if targetModel.activeLevel >= self.targetLODLevel:
                    return [targetModel]
            self.LogInfo('Regenerating damage locator cache for pair: ', targetID, ' - ', attackerID)
            targetDamageLocators = getattr(targetBall, 'targets', None)
            if targetDamageLocators is None or len(targetDamageLocators) == 0:
                if targetID in self.failedTargets:
                    return [targetModel]
                self.LogWarn('DamageService::GetTargetLocators must regenerate damage locators', targetID)
                locators = self.GenerateDamageLocators(targetModel, self.generatedDamageLocators)
                if len(locators) == 0:
                    self.failedTargets[targetID] = targetModel
                    self.LogError("Couldn't generate damage locators on ", targetModel.name)
                    return [targetModel]
                targetDamageLocators = locators
                targetBall.targets = locators
            closestTargets = []
            for targetLocator in targetDamageLocators:
                closestTargets.append([(targetLocator.worldPosition - attackerModel.worldPosition).Length(), targetLocator])

            closestTargets.sort()
            result = [ x[1] for x in closestTargets ]
            self.targets[targetID, attackerID] = (blue.os.GetWallclockTimeNow(), result)
            result = result[:locatorVariance]
        except:
            log.LogException()
        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(timer)

        return result

    def GetDamageLocatorGeneratorTransformHeirarchy(self, transform):
        if transform.__typename__ == 'TriLODGroup':
            if len(transform.children) > 0:
                return self.GetDamageLocatorGeneratorTransform(transform.children[0], 0)
            else:
                self.LogError('DamageService::GetDamageLocatorGeneratorTransformHeirarchy: Passed an empty LODGroup. Not much that can be done here anyway.')
                return None
        self.LogError('DamageService::GetDamageLocatorGeneratorTransformHeirarchy: Attempting to generate damage locators on a', transform.__typename__)

    def GetDamageLocatorGeneratorTransform(self, transform, depth = 0):
        if depth == 0 and not hasattr(transform, 'object'):
            return
        if transform.display == 0:
            return
        if hasattr(transform, 'object') and transform.object is not None:
            if transform.object.__typename__ == 'TriModel':
                if transform.object.vertices != 'res:/Model/Global/locatorObject.tri':
                    if hasattr(transform, 'name'):
                        self.LogWarn('DamageService.GetDamageLocatorGeneratorTransform: Picked:', transform.name)
                    return [transform]
            if transform.object.__typename__ == 'TriParticleCloud':
                return [transform]
        result = None
        if depth < 3:
            for child in transform.children:
                result = self.GetDamageLocatorGeneratorTransform(child, depth + 1)
                if result is not None:
                    return [transform] + result

    def GenerateDamageLocators(self, rootTransform, generateNumber):
        timer = blue.pyos.taskletTimer.EnterTasklet('DamageService::GenerateDamageLocators')
        generatedLocators = []
        try:
            targetTransformHeirarchy = self.GetDamageLocatorGeneratorTransformHeirarchy(rootTransform)
            if targetTransformHeirarchy is None:
                self.LogError('DamageService::GenerateDamageLocators: Didnt get anything sensible back from GetDamageLocatorGeneratorTransformHeirarchy')
                return []
            targetTransform = targetTransformHeirarchy[-1]
            targetTransformHeirarchy = targetTransformHeirarchy[1:]
            transformCopyList = []

            def CopyAttributes(tf1, tf2, attributes):
                for attribute in attributes:
                    if getattr(tf1, attribute, None) is not None:
                        setattr(tf2, attribute, getattr(tf1, attribute).CopyTo())

            def CheckEmptyTransformation(tf):
                if tf.__typename__ != 'TriTransform':
                    return True
                if tf.useCurves:
                    if tf.scalingCurve is not None:
                        return False
                    if tf.rotationCurve is not None:
                        return False
                    if tf.translationCurve is not None:
                        return False
                if tf.scaling.x != 1.0 or tf.scaling.y != 1.0 or tf.scaling.z != 1.0:
                    return False
                if tf.translation.x != 0.0 or tf.translation.y != 0.0 or tf.translation.z != 0.0:
                    return False
                if tf.rotation.x != 0.0 or tf.rotation.y != 0.0 or tf.rotation.z != 0.0 or tf.rotation.w != 1.0:
                    return False
                return True

            for transformDepthIndex in range(len(targetTransformHeirarchy)):
                if CheckEmptyTransformation(targetTransformHeirarchy[transformDepthIndex]):
                    continue
                tfCopy = blue.classes.CreateInstance('trinity.TriTransform')
                tfCopy.frustrumCull = 0
                CopyAttributes(targetTransformHeirarchy[transformDepthIndex], tfCopy, ['scalingCurve',
                 'rotationCurve',
                 'translationCurve',
                 'scaling',
                 'rotation',
                 'translation'])
                if len(transformCopyList) > 0:
                    transformCopyList[-1].children.append(tfCopy)
                transformCopyList.append(tfCopy)

            if len(transformCopyList) > 0:
                transformCopyList[0].name = 'Generated Damage Locators'
            for v in range(generateNumber):
                pos = targetTransform.RandomSurfacePoint()
                if not pos:
                    self.LogError('DamageService.GenerateDamageLocators: RandomSurfacePoint generated a None vector')
                    break
                newDamageLocator = blue.classes.CreateInstance('trinity.TriSplTransform')
                newDamageLocator.scaling.Scale(0.2)
                newDamageLocator.name = 'locator_damage_' + str(v)
                newDamageLocator.translation = pos.CopyTo()
                targetTransform.children.append(newDamageLocator)
                if len(transformCopyList) > 0:
                    transformCopyList[-1].children.append(newDamageLocator)
                generatedLocators.append(newDamageLocator)

            for lodGroup in rootTransform.children[1:]:
                if len(transformCopyList) > 0:
                    lodGroup.children.append(transformCopyList[0])
                else:
                    for newLocator in generatedLocators:
                        lodGroup.children.append(newLocator)

        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(timer)

        return generatedLocators