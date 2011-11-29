import entities

class EntitySpawnClient(entities.EntitySpawnService):
    __guid__ = 'svc.entitySpawnClient'
    __dependencies__ = entities.EntitySpawnService.__dependencies__
    __dependencies__ += ['worldSpaceClient']

    def Run(self, *args):
        entities.EntitySpawnService.Run(self, args)
        self.idCounter = const.minFakeClientItem



    def GetNextEntityID(self):
        self.idCounter += 1
        return self.idCounter



    def GetWorldSpaceTypeID(self, sceneID):
        return self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)



    def GetSceneID(self, worldSpaceTypeID):
        raise NotImplementedError('GetSceneID() function not implemented on: ', self.__guid__)




