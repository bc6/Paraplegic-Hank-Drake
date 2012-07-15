#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/world/worldSpaceCommonSvc.py
import blue
import collections
import service

class BaseWorldSpaceService(service.Service):
    __guid__ = 'world.CoreBaseWorldSpaceService'
    __dependencies__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.worldSpaceLookup = collections.defaultdict(list)
        self.instances = {}

    def GetConfigValue(self, name, defaultValue = None):
        raise NotImplemented('GetConfigValue')

    def LoadWorldSpace(self, worldSpaceID):
        raise RuntimeError('LoadWorldSpace needs to be implemented')

    def GetLoadedWorldSpaceIDs(self):
        return self.instances.keys()

    def GetWorldSpaceInstance(self, instanceID):
        return self.instances.get(instanceID, None)

    def GetWorldSpaceTypeIDFromWorldSpaceID(self, worldSpaceID):
        pass

    def GetWorldSpaceIDsOfWorldSpace(self, worldSpaceID):
        result = self.worldSpaceLookup[worldSpaceID] if worldSpaceID in self.worldSpaceLookup else []
        return filter(self.IsInstanceLoaded, result)

    def IsWorldSpaceLoaded(self, worldSpaceID):
        if worldSpaceID in self.worldSpaceLookup:
            for instanceID in self.worldSpaceLookup[worldSpaceID]:
                if self.IsInstanceLoaded(instanceID):
                    return True

        return False

    def IsInstanceLoaded(self, instanceID):
        return instanceID in self.instances

    def HasAnyInstanceLoaded(self):
        return len(self.instances) > 0

    def UnloadWorldSpaceInstance(self, instanceID):
        instance = self.instances[instanceID]
        if instance is not None:
            del self.instances[instanceID]
            worldSpaceID = instance.GetWorldSpaceTypeID()
            self.worldSpaceLookup[worldSpaceID].remove(instanceID)
            if not self.worldSpaceLookup[worldSpaceID]:
                del self.worldSpaceLookup[worldSpaceID]

    def OnEntitySceneLoaded(self, sceneID):
        ws = self.GetWorldSpaceInstance(sceneID)
        gw = sm.GetService('gameWorld' + boot.role.title()).GetGameWorld(sceneID)
        gw.LoadPathData(ws.GetWorldSpaceTypeID(), blue.pyos.packaged)