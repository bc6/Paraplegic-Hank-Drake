import entityCommon
import entities
import random
import copy

class EntitySpawnClient(entities.EntitySpawnService):
    __guid__ = 'svc.entitySpawnClient'
    __notifyevents__ = ['ProcessEntitySceneUnloading', 'OnEntityDeleted']

    def Run(self, *args):
        entities.EntitySpawnService.Run(self, args)
        self.idCounter = 0
        self.entityRecipeSvc = sm.GetService('entityRecipeSvc')
        self.gameWorldService = sm.GetService('gameWorldClient')



    def MapSceneIDToWorldSpaceID(self, sceneID):
        return sm.GetService('worldSpaceClient').GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)



    def GetGenerators(self, sceneID):
        typeID = self.MapSceneIDToWorldSpaceID(sceneID)
        return [ generator for generator in cfg.entityGeneratorsByWorldSpace.get(typeID, []) if generator.spawnOnClient ]



    def GetNextSpawnID(self, sceneID, typeID):
        self.idCounter = self.idCounter + 1
        return const.minFakeClientItem + self.idCounter




