import GameWorld
import blue
import service
import collections

class AimingComponent:
    __guid__ = 'AI.AimingComponent'

    def __init__(self, state):
        self.state = state




class AimingEntityData(object):
    __guid__ = 'AI.AimingEntityData'
    entID = 0


class aimingCommon(service.Service):
    __guid__ = 'AI.aimingCommon'
    sceneManagers = {}
    __componentTypes__ = ['aiming']

    def CreateComponent(self, name, state):
        return AimingComponent(state)



    def SetupComponent(self, entity, component):
        pass



    def RegisterComponent(self, entity, component):
        if entity.scene.sceneID not in self.sceneManagers:
            self.LogError('Trying to register a aiming component thats doesnt have a valid scene', entity.entityID)
            return 
        positionComponent = entity.GetComponent('position')
        aimingManager = self.sceneManagers[entity.scene.sceneID]
        aimingManager.AddEntity(component.entData.entID, positionComponent)



    def UnRegisterComponent(self, entity, component):
        if entity.scene.sceneID not in self.sceneManagers:
            self.LogError("Trying to remove a aiming entity who's scene doesn't have a manager", entity.entityID)
            return 
        aimingManager = self.sceneManagers[entity.scene.sceneID]
        aimingManager.RemoveEntity(entity.entityID)



    def TearDownComponent(self, entity, component):
        pass



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return component.state



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.state = state
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Entity Type'] = component.state['entityType']
        return report



    def GetAimingManager(self, sceneID):
        return self.sceneManagers[sceneID]



    def MakeAimingManager(self):
        raise NotImplementedError('This is a pure virtual function to create a aiming manager')



    def OnLoadEntityScene(self, sceneID):
        self.LogInfo('Registering a new aiming system for scene ', sceneID)
        if sceneID in self.sceneManagers:
            self.LogError('Duplicate scene passed to aiming system Register from entityService ', sceneID)
            return 
        aimingManager = self.MakeAimingManager()
        self.sceneManagers[sceneID] = aimingManager
        aimingManager.SetStaticSettings((self.GetValidTargets(),))
        gw = self.gameWorldService.GetGameWorld(sceneID)
        gw.aimingManager = aimingManager
        aimingManager.SetGameWorld(gw)
        self.LogInfo('Done Creating a new aiming system for scene ', sceneID)



    def OnUnloadEntityScene(self, sceneID):
        self.LogInfo('Unloading aiming system for scene ', sceneID)
        gw = self.gameWorldService.GetGameWorld(sceneID)
        gw.aimingManager = None
        if sceneID in self.sceneManagers:
            del self.sceneManagers[sceneID]
        else:
            self.LogError('Non-existent scene passed to aiming system Unload from entityService ', sceneID)
        self.LogInfo('Done Unloading aiming system for scene ', sceneID)



    def GetValidTargets(self):
        validTargets = []
        for aimTarget in const.aiming.AIMING_VALID_TARGETS.values():
            if self.IsTargetClientServerValid(aimTarget[const.aiming.AIMING_VALID_TARGETS_FIELD_CLIENTSERVER_FLAG]):
                validTargets.append((aimTarget[const.aiming.AIMING_VALID_TARGETS_FIELD_ID], aimTarget[const.aiming.AIMING_VALID_TARGETS_FIELD_NAME], aimTarget[const.aiming.AIMING_VALID_TARGETS_FIELD_RESELECTDELAY]))

        return tuple(validTargets)




