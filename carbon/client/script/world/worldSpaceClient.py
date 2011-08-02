import collections
import stackless
import uthread
import world

class WorldSpaceClient(world.BaseWorldSpaceService):
    __guid__ = 'svc.worldSpaceClient'
    __dependencies__ = world.BaseWorldSpaceService.__dependencies__[:]
    __dependencies__.extend(['physicalPortalClient', 'occluderClient'])

    def __init__(self):
        world.BaseWorldSpaceService.__init__(self)
        self.trinityInitialized = False
        self.activeWorldSpace = None
        self.showLoadingWindow = False
        self.instanceLoadedChannel = collections.defaultdict(list)



    def Run(self, *etc):
        world.BaseWorldSpaceService.Run(self, *etc)
        self.UnloadOtherWorldSpaces = True



    def GetCurrentDistrict(self):
        if session.worldspaceid is None:
            return 
        worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(session.worldspaceid)
        if worldSpaceTypeID is None:
            return 
        ws = world.GetWorldSpace(worldSpaceTypeID)
        return ws.GetDistrictID()



    def UnloadWorldSpaceInstance(self, instanceID):
        if self.IsInstanceLoaded(instanceID):
            uthread.Lock(self, 'Worldspace', instanceID)
            try:
                if self.IsInstanceLoaded(instanceID) and (session.worldspaceid is None or session.worldspaceid and session.worldspaceid != instanceID):
                    self.LogInfo('Unloading worldspace instance', instanceID)
                    instance = self.instances[instanceID]
                    self._GameSpecificUnloading(instance)
                    proximity = sm.GetService('proximity')
                    proximity.UnloadInstance(instance)
                    worldSpaceID = instance.GetWorldSpaceTypeID()
                    sm.ChainEvent('ProcessWorldSpaceUnloading', instanceID)
                    world.BaseWorldSpaceService.UnloadWorldSpaceInstance(self, instanceID)
                    if not self.IsWorldSpaceLoaded(worldSpaceID):
                        gps = sm.GetService('gps')
                        gps.UnloadPathCostsForWorldSpace(worldSpaceID)
                    sm.ScatterEvent('OnWorldSpaceUnloaded', instanceID)

            finally:
                self.LogInfo('Unloaded worldspace instance', instanceID)
                uthread.UnLock(self, 'Worldspace', instanceID)




    def _GameSpecificUnloading(self, instance):
        pass



    def _LoadWorldSpaceFromServer(self, instanceID, worldSpaceID):
        if not self.IsWorldSpaceLoaded(worldSpaceID):
            self.LogInfo('adding instance', instanceID, 'to GPS')
            gps = sm.GetService('gps')
            gps.LoadPathCostsForWorldSpace(worldSpaceID)
        self.LogInfo('Creating worldSpace layout', worldSpaceID, 'for instance', instanceID)
        newWorldSpace = world.WorldSpaceScene(worldSpaceID, instanceID)
        sm.ChainEvent('ProcessWorldSpaceLoading', instanceID, newWorldSpace)
        newWorldSpace.LoadProperties()
        self._FinishLoadingInstance(newWorldSpace)
        return newWorldSpace



    def LoadWorldSpaceInstance(self, instanceID, worldSpaceTypeID = None):
        uthread.Lock(self, 'Worldspace', instanceID)
        try:
            self.LogInfo('Loading WorldSpaceInstance')
            if instanceID not in self.instances:
                if worldSpaceTypeID is None:
                    worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(instanceID)
                newWorldSpace = self._LoadWorldSpaceFromServer(instanceID, worldSpaceTypeID)

        finally:
            self.LogInfo('Done loading WorldSpaceInstance')
            uthread.UnLock(self, 'Worldspace', instanceID)




    def _FinishLoadingInstance(self, instance):
        worldSpaceID = instance.GetWorldSpaceID()
        worldSpaceTypeID = instance.GetWorldSpaceTypeID()
        self.instances[worldSpaceID] = instance
        self.worldSpaceLookup[worldSpaceTypeID].append(worldSpaceID)
        for each in self.instanceLoadedChannel[worldSpaceID]:
            while each.balance < 0:
                each.send(None)


        del self.instanceLoadedChannel[worldSpaceID]
        self.LogInfo('Loaded worldspace from server: worldSpaceID', worldSpaceID, 'worldSpaceTypeID', worldSpaceTypeID)
        sm.ScatterEvent('OnWorldSpaceLoaded', worldSpaceTypeID, worldSpaceID)



    def WaitForInstance(self, instanceID):
        if not self.IsInstanceLoaded(instanceID):
            self.instanceLoadedChannel[instanceID].append(stackless.channel())
            self.instanceLoadedChannel[instanceID][-1].receive()



    def UnloadInstances(self, unloadInstanceIDs):
        realInstanceIDList = []
        for instanceID in unloadInstanceIDs:
            realInstanceIDList.append(instanceID)

        for instanceID in realInstanceIDList:
            uthread.new(self.UnloadWorldSpaceInstance, instanceID).context = 'worldSpaceClient::UnloadWorldSpaceInstance'





