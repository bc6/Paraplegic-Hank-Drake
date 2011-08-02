import service
import GameWorld
import locks
import log
import collections

class ProximityComponent(object):
    __guid__ = 'proximity.ProximityComponent'

    def __init__(self):
        pass




class Proximity(service.Service):
    __guid__ = 'svc.proximity'
    __dependencies__ = ['gps']
    __notifyevents__ = ['OnWorldSpaceLoaded']
    __componentTypes__ = ['proximity']

    def Run(self, *etc):
        self.worldSpaceSvc = sm.GetService('worldSpace' + boot.role.title())
        self.gameWorldSvc = sm.GetService('gameWorld' + boot.role.title())
        gameWorldServiceName = {'server': 'gameWorldServer',
         'client': 'gameWorldClient'}.get(boot.role)
        self.gameWorldService = sm.GetService(gameWorldServiceName)
        self.nextIndex = 0
        self.storedCallBacks = {}
        self.Proximity = self.gameWorldService.GetGameWorldManager().proximity
        self.proximityTrees = {}
        self.waitingForProximityTrees = {}



    def CreateComponent(self, name, state):
        return ProximityComponent()



    def PackUpForClientTransfer(self, component):
        return True



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return True



    def UnPackFromSceneTransfer(self, component, entity, state):
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        bounds = component.tree.GetBoundsOfNode(component.entityID)
        report['Min'] = ',\t\t'.join([ '%.2f' % f for f in bounds[0] ])
        report['Max'] = ',\t\t'.join([ '%.2f' % f for f in bounds[1] ])
        return report



    def OnLoadEntityScene(self, sceneID):
        self.LogInfo('Registering a new proximity scene for', sceneID)
        gw = self.gameWorldService.GetGameWorld(sceneID)
        self.LogInfo('Proximity tree got Gameworld for scene ', sceneID, ' initialized')
        proximityTree = GameWorld.ProximityTree()
        self.LogInfo('Proximity tree for scene ', sceneID, ' created')
        proximityTree.Initialize(2000, 0.35, 32)
        self.LogInfo('Proximity tree for scene ', sceneID, ' initialized')
        gw.grid = proximityTree
        self.proximityTrees[sceneID] = proximityTree
        if sceneID in self.waitingForProximityTrees:
            self.waitingForProximityTrees.pop(sceneID).set()
        self.LogInfo('Done Registering a new proximity scene for', sceneID)



    def OnUnloadEntityScene(self, sceneID):
        self.LogInfo('Unloading the proximity scene for', sceneID)
        gw = self.gameWorldService.GetGameWorld(sceneID)
        for entry in self.storedCallBacks.itervalues():
            (callbackDef, instanceLookup, entIDSet,) = entry
            if sceneID in instanceLookup:
                gw.grid.RemoveListener(instanceLookup[sceneID])
                del instanceLookup[sceneID]

        gw.grid = None
        if sceneID in self.proximityTrees:
            del self.proximityTrees[sceneID]
        if sceneID in self.waitingForProximityTrees:
            self.waitingForProximityTrees.pop(sceneID).set()
        self.LogInfo('Done Unloading the proximity scene for', sceneID)



    def RegisterComponent(self, entity, component):
        if entity.scene.sceneID not in self.proximityTrees:
            log.LogWarn('waiting for proximity scene when registering proximity component')
        tree = self.GetProximityTree(entity.scene.sceneID)
        if entity.HasComponent('position') and entity.HasComponent('boundingVolume'):
            tree.AddFromComponents(entity.entityID, entity.GetComponent('position'), entity.GetComponent('boundingVolume'))
        else:
            self.LogError('Cannot create proximity without position and bounds')
            return 
        component.tree = tree
        component.entityID = entity.entityID



    def UnRegisterComponent(self, entity, component):
        tree = self.GetProximityTree(entity.scene.sceneID)
        tree.Delete(entity.entityID)
        indexList = []
        for (index, entry,) in self.storedCallBacks.iteritems():
            (callbackDef, instanceLookup, entIDSet,) = entry
            if entity.entityID in entIDSet:
                indexList.append(index)

        for index in indexList:
            self.OnSensorExit(index, [entity.entityID])

        component.tree = None



    def GetProximityTree(self, sceneID):
        tree = self.proximityTrees.get(sceneID, None)
        if tree:
            return tree
        if sceneID not in self.waitingForProximityTrees:
            self.waitingForProximityTrees[sceneID] = locks.Event('ProximityTreeLoad_%s' % sceneID)
        self.waitingForProximityTrees[sceneID].wait()
        tree = self.proximityTrees.get(sceneID, None)
        return tree



    def GetEntIDsInRange(self, instanceID, pos, range):
        return self.Proximity.GetEntIDsInRange(instanceID, pos, range)



    def _FindOrCreateFreeIndex(self):
        self.nextIndex += 1
        return self.nextIndex



    def _CreateProximityListener(self, *args):
        return GameWorld.ProximityListener()



    def _CreateProximityListenerCylinder(self, height):
        listener = GameWorld.ProximityCylinder()
        listener.SetHeight(height)
        return listener



    def OnSensorEnter(self, callbackIndex, addedEntIDs):
        if callbackIndex not in self.storedCallBacks:
            return 
        (callbackDef, instanceLookup, entIDSet,) = self.storedCallBacks[callbackIndex]
        (instanceID, pos, range, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances, createMethod, createArgs,) = callbackDef
        onEnterCallback(callbackArgs, addedEntIDs)
        entIDSet.update(addedEntIDs)



    def OnSensorExit(self, callbackIndex, removedEntIDs):
        if callbackIndex not in self.storedCallBacks:
            return 
        (callbackDef, instanceLookup, entIDSet,) = self.storedCallBacks[callbackIndex]
        filteredList = filter(lambda entID: entID in entIDSet, removedEntIDs)
        if filteredList:
            (instanceID, pos, range, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances, createMethod, createArgs,) = callbackDef
            onExitCallback(callbackArgs, filteredList)
            entIDSet.difference_update(filteredList)



    def AddCallbacks(self, instanceID, pos, range, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances = True):
        newIndex = self._FindOrCreateFreeIndex()
        entry = ((instanceID,
          pos,
          range,
          msToCheck,
          onEnterCallback,
          onExitCallback,
          callbackArgs,
          lookAcrossInstances,
          self._CreateProximityListener,
          ()), {}, set())
        self.storedCallBacks[newIndex] = entry
        self._UpdateAllCallbacks()
        return newIndex



    def AddCylinderCallbacks(self, instanceID, pos, radius, height, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances = True):
        newIndex = self._FindOrCreateFreeIndex()
        entry = ((instanceID,
          pos,
          radius,
          msToCheck,
          onEnterCallback,
          onExitCallback,
          callbackArgs,
          lookAcrossInstances,
          self._CreateProximityListenerCylinder,
          (height,)), {}, set())
        self.storedCallBacks[newIndex] = entry
        self._UpdateAllCallbacks()
        return newIndex



    def ChangeCallbackPosition(self, index, newInstanceID, newPos):
        entry = self.storedCallBacks[index]
        (callbackDef, instanceLookup, entIDSet,) = entry
        (instanceID, pos, range, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances, createMethod, createArgs,) = callbackDef
        if instanceID != newInstanceID or pos != newPos:
            entry = ((newInstanceID,
              newPos,
              range,
              msToCheck,
              onEnterCallback,
              onExitCallback,
              callbackArgs,
              lookAcrossInstances,
              createMethod,
              createArgs), instanceLookup, entIDSet)
            self.storedCallBacks[index] = entry
            if lookAcrossInstances:
                positions = self.gps.ConvertCoordinateToConnectedInstances(newInstanceID, newPos, range)
            else:
                positions = {newInstanceID: newPos}
            for (instanceID, pos,) in positions.iteritems():
                if not self.worldSpaceSvc.IsInstanceLoaded(instanceID):
                    continue
                if pos is not None:
                    if instanceID not in instanceLookup:
                        gw = self.gameWorldSvc.GetGameWorld(instanceID)
                        listener = createMethod(*createArgs)
                        listener.Init(self.OnSensorEnter, self.OnSensorExit, index, pos, range, msToCheck)
                        gw.grid.AddListener(listener)
                        instanceLookup[instanceID] = listener
                    else:
                        instanceLookup[instanceID].pos = pos

            for instanceID in instanceLookup.keys():
                if instanceID not in positions:
                    gw = self.gameWorldSvc.GetGameWorld(instanceID)
                    gw.grid.RemoveListener(instanceLookup[instanceID])
                    del instanceLookup[instanceID]




    def RemoveCallback(self, index):
        (callbackDef, instanceLookup, entIDSet,) = self.storedCallBacks[index]
        for (instanceID, listener,) in instanceLookup.iteritems():
            if self.worldSpaceSvc.IsInstanceLoaded(instanceID):
                gw = self.gameWorldSvc.GetGameWorld(instanceID)
                gw.grid.RemoveListener(listener)

        del self.storedCallBacks[index]



    def _UpdateAllCallbacks(self):
        for (index, entry,) in self.storedCallBacks.iteritems():
            (callbackDef, instanceLookup, entIDSet,) = entry
            (instanceID, pos, range, msToCheck, onEnterCallback, onExitCallback, callbackArgs, lookAcrossInstances, createMethod, createArgs,) = callbackDef
            if lookAcrossInstances:
                positions = self.gps.ConvertCoordinateToConnectedInstances(instanceID, pos, range)
            else:
                positions = {instanceID: pos}
            for (instanceID, pos,) in positions.iteritems():
                if not self.worldSpaceSvc.IsInstanceLoaded(instanceID) or instanceID in instanceLookup:
                    continue
                if pos is not None:
                    gw = self.gameWorldSvc.GetGameWorld(instanceID)
                    listener = createMethod(*createArgs)
                    listener.Init(self.OnSensorEnter, self.OnSensorExit, index, pos, range, msToCheck)
                    gw.grid.AddListener(listener)
                    instanceLookup[instanceID] = listener





    def _RemoveInstanceFromCallbacks(self, instance):
        worldSpaceID = instance.GetWorldSpaceID()
        for entry in self.storedCallBacks.itervalues():
            (callbackDef, instanceLookup, entIDSet,) = entry
            if worldSpaceID in instanceLookup:
                gw = instance.GetGameWorld()
                gw.grid.RemoveListener(instanceLookup[worldSpaceID])
                del instanceLookup[worldSpaceID]




    def OnWorldSpaceLoaded(self, worldSpaceID, instanceID):
        self._UpdateAllCallbacks()



    def UnloadInstance(self, instance):
        self._RemoveInstanceFromCallbacks(instance)



    def GetEntIDsInRangeOfEntityID(self, entid, range):
        ent = self.entityService.FindEntityByID(entid)
        if ent:
            return self.GetEntIDsInRangeOfEntity(ent, range)



    def GetEntIDsInRangeOfEntity(self, ent, range):
        if ent.HasComponent('position'):
            pos = ent.position.position
        elif ent.HasComponent('collisionMesh'):
            pos = ent.collisionMesh.pos
        else:
            return None
        return self.GetEntIDsInRange(ent.scene.sceneID, pos, range)




