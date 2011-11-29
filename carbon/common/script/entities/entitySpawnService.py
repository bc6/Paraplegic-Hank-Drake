import service

class EntitySpawnService(service.Service):
    __guid__ = 'entities.EntitySpawnService'
    __exportedcalls__ = {}
    __notifyevents__ = []
    __dependencies__ = ['entityRecipeSvc']

    def GetNextEntityID(self):
        raise NotImplementedError('GetNextEntityID() function not implemented on: ', self.__guid__)



    def GetWorldSpaceTypeID(self, sceneID):
        raise NotImplementedError('GetWorldSpaceTypeID() function not implemented on: ', self.__guid__)



    def GetSceneID(self, worldSpaceTypeID):
        raise NotImplementedError('GetSceneID() function not implemented on: ', self.__guid__)



    def LoadEntityFromSpawner(self, spawner):
        if not spawner.CanSpawn():
            return 
        itemID = spawner.GetEntityID()
        if itemID is False:
            itemID = self.GetNextEntityID()
        scene = self.entityService.LoadEntityScene(spawner.GetSceneID())
        spawnedEntity = self.entityService.CreateEntityFromRecipe(scene, spawner.GetRecipe(self.entityRecipeSvc), itemID)
        if spawnedEntity is not None:
            scene.CreateAndRegisterEntity(spawnedEntity)
        return spawnedEntity




