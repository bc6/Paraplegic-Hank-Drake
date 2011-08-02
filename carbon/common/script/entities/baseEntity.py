import bluepy
import service
import uthread
import locks
import collections
import entities
import log
import sys
import entityCommon
import GameWorld

class Entity:
    __guid__ = 'entities.Entity'

    def __init__(self, scene, entityID):
        self.scene = scene
        self.entityID = entityID
        self.components = {}
        self.componentStates = {}
        self.state = const.cef.ENTITY_STATE_UNINITIALIZED
        self.entityLock = uthread.CriticalSection()



    def AddComponent(self, name, component):
        if name in self.components:
            msg = ('Adding a component:',
             name,
             "that's already on the entity:",
             self.entityID,
             ' Old component will be replaced')
            self.scene.service.LogError('Adding a component:', name, "that's already on the entity:", self.entityID, ' Old component will be replaced')
            if 'logging' in self.components:
                self.logging.Log(msg)
        if component is not None:
            self.components[name] = component
        else:
            log.LogWarn('Unable to add component', name, 'to entity', self.entityID)



    def HasComponent(self, name):
        return name in self.components



    def GetComponent(self, name):
        return self.components.get(name, None)



    def AddComponentState(self, name, state):
        if name in self.componentStates:
            msg = ('Adding a component state:',
             name,
             "that's already on the a entity:",
             self.entityID,
             ' Old component state will be replaced')
            self.scene.service.LogError('Adding a component state:', name, "that's already on the a entity:", self.entityID, ' Old component state will be replaced')
            if 'logging' in self.components:
                self.logging.Log(msg)
        self.componentStates[name] = state



    def __getattr__(self, attr):
        if self.components.has_key(attr):
            return self.components[attr]
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        raise AttributeError(attr)



    def Log(self, str):
        logging = self.components.get('logging', None)
        if logging:
            logging.Log(str)




class EntitySceneState:
    UNINITIALIZED = 0
    LOADING = 1
    READY = 2
    UNLOADING = 3


class EventQueue(object):

    def __init__(self, emptyEvent = None):
        self._task = None
        self._queue = collections.deque()
        self._emptyEvent = emptyEvent



    def AddEvent(self, event, *args):
        semaphore = locks.Event('event_%s' % event)
        self._queue.append((event, args, semaphore))
        return semaphore



    def StartEvents(self):
        if self._task is None:
            self._task = uthread.new(self._PumpEvent)
            self._task.context = 'EventQueue update'



    def GetLastSemaphore(self):
        try:
            (event, args, semaphore,) = self._queue[-1]
            return semaphore
        except:
            log.LogError('Missing semaphore')
            return None



    def _ProcessEvent(self, semaphore, event, *args):
        event(*args)
        semaphore.set()



    def _PumpEvent(self):
        while len(self._queue) > 0:
            (event, args, semaphore,) = self._queue[0]
            self._ProcessEvent(semaphore, event, *args)
            self._queue.popleft()

        self._task = None
        if self._emptyEvent is not None:
            self._emptyEvent()




class BaseEntityScene(object):
    __guid__ = 'entities.BaseEntityScene'
    __exportedcalls__ = {'ReceiveRemoteEntity': {'role': service.ROLE_SERVICE}}

    def __init__(self, broker, sceneID):
        self.state = EntitySceneState.UNINITIALIZED
        self.sceneID = sceneID
        self.entities = {}
        self.broker = broker
        self.eventQueue = EventQueue()
        self._entityList = {}
        self._startupEntities = []



    def IsUnloading(self):
        return self.state == EntitySceneState.UNLOADING



    def _LoadScene(self, semaphore):
        self.broker.LogInfo('Asynch scene load started for scene', self.sceneID)
        if semaphore is not None:
            self.broker.LogError('Scene load waiting for previous unload for scene', self.sceneID)
            semaphore.wait()
        self.state = EntitySceneState.LOADING
        self.broker.LogInfo('Scene load starting registration for scene', self.sceneID)
        self.broker._RegisterScene(self, self.loadSemaphore)
        self._startupEntities = self._entityList.keys()
        self.broker.LogInfo('Asynch scene load finished for scene', self.sceneID)



    def _UnloadScene(self):
        self.broker.LogInfo('Asynch scene unload started for scene', self.sceneID)
        self.state = EntitySceneState.UNLOADING
        self.broker.LogInfo('Scene unload starting unregistration for scene', self.sceneID)
        self.broker._UnregisterScene(self)
        semaphores = []
        for entityID in self._entityList.iterkeys():
            queue = self.broker._entityQueues.get(entityID, None)
            if queue is not None:
                semaphore = queue.GetLastSemaphore()
                if semaphore is not None:
                    semaphores.append(semaphore)

        for semaphore in semaphores:
            semaphore.wait()

        semaphores = []
        for entity in self.entities.itervalues():
            semaphores.append(self.UnregisterAndDestroyEntity(entity))

        for semaphore in semaphores:
            semaphore.wait()

        self.broker.LogInfo('Scene unload starting TearDown for scene', self.sceneID)
        self.broker._TearDownScene(self)
        self.broker.LogInfo('Asynch scene unload finished for scene', self.sceneID)



    def LoadScene(self, scene):
        semaphore = None
        if scene is not None:
            self.broker.LogError('Scene', self.sceneID, 'waiting for unload of the same scene')
            semaphore = scene.eventQueue.GetLastSemaphore()
            if semaphore is None:
                self.broker.LogError('OMG predcessor scene has no semaphore ', self.sceneID)
        self.loadSemaphore = self.eventQueue.AddEvent(self._LoadScene, semaphore)
        self.eventQueue.StartEvents()
        return self.loadSemaphore



    def UnloadScene(self):
        semaphore = self.eventQueue.AddEvent(self._UnloadScene)
        self.eventQueue.StartEvents()
        return semaphore



    def WaitOnStartupEntities(self):
        if self._startupEntities is not None:
            self.broker.LogInfo('Waiting on startup entities for scene', self.sceneID)
            self.broker.LogInfo('The pending entity IDs are', self._startupEntities)
            for entID in self._startupEntities:
                self.broker.WaitOnEntityEvents(entID)

            self.broker.LogInfo('Done Waiting on startup entities for scene', self.sceneID)
            self._startupEntities = None
            self.broker.LogInfo('Finished waiting on startup entities for scene', self.sceneID)



    def CreateEntity(self, entity, initData = None):
        self._entityList[entity.entityID] = entity
        channel = self.broker._AddEvent(entity.entityID, self.broker._CreateEntity, entity, self.loadSemaphore, initData)
        self.broker._StartEvents(entity.entityID)
        return channel



    def RegisterEntity(self, entity, initData = None):
        channel = self.broker._AddEvent(entity.entityID, self.broker._RegisterEntity, entity, initData)
        self.broker._StartEvents(entity.entityID)
        return channel



    def UpdateEntity(self, entity, updateData = None):
        channel = self.broker._AddEvent(entity.entityID, self.broker._UpdateEntity, entity, updateData)
        self.broker._StartEvents(entity.entityID)
        return channel



    def UnregisterEntity(self, entity):
        channel = self.broker._AddEvent(entity.entityID, self.broker._UnregisterEntity, entity)
        self.broker._StartEvents(entity.entityID)
        return channel



    def DestroyEntity(self, entity):
        del self._entityList[entity.entityID]
        channel = self.broker._AddEvent(entity.entityID, self.broker._DestroyEntity, entity)
        self.broker._StartEvents(entity.entityID)
        return channel



    def CreateAndRegisterEntity(self, entity, initData = None):
        self._entityList[entity.entityID] = entity
        self.broker._AddEvent(entity.entityID, self.broker._CreateEntity, entity, self.loadSemaphore, initData)
        channel = self.broker._AddEvent(entity.entityID, self.broker._RegisterEntity, entity, initData)
        self.broker._StartEvents(entity.entityID)
        return channel



    def UnregisterAndDestroyEntity(self, entity):
        del self._entityList[entity.entityID]
        self.broker._AddEvent(entity.entityID, self.broker._UnregisterEntity, entity)
        channel = self.broker._AddEvent(entity.entityID, self.broker._DestroyEntity, entity)
        self.broker._StartEvents(entity.entityID)
        return channel



    def AddEntityToRegisteredList(self, entity):
        self.entities[entity.entityID] = entity



    def RemoveEntityFromRegisteredList(self, entity):
        del self.entities[entity.entityID]



    def GetAllEntityIds(self):
        return self.entities.keys()



    def ReceiveRemoteEntity(self, fromSceneID, entityID, packedState):
        semaphore = self.broker.ReceiveRemoteEntity(fromSceneID, entityID, self.sceneID, packedState)
        semaphore.wait()




class BaseEntityService(service.Service):
    __guid__ = 'svc.BaseEntityService'
    __exportedcalls__ = {'ReceiveRemoteEntity': {'role': service.ROLE_ANY}}
    __entitySceneType__ = None
    __entitysystems__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.scenes = {}
        self.loadingScenes = {}
        self.unloadingScenes = {}
        self.loadingEntities = {}
        self.entityLocks = {}
        self.entityDestoryLocks = {}
        self.componentSystems = collections.defaultdict(set)
        self.componentFactories = {}
        self.sceneCreationSubscriptions = set()
        self._deadEntityList = {}
        self._entityQueues = {}
        self._entityProcessing = {}



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.entitySceneManager = GameWorld.EntitySceneManager()
        self.entitySceneManager.Init()
        calls = []
        for entitySystem in set(self.__entitysystems__):
            calls.append((self.SetupEntitySystem, (entitySystem,)))

        uthread.parallel(calls)



    def SetupEntitySystem(self, entitySystem):
        system = sm.GetService(entitySystem)
        system.entityService = self
        self.RegisterForSceneLifeCycle(system)
        for componentType in getattr(system, '__componentTypes__', []):
            if hasattr(system, 'CreateComponent'):
                self.RegisterComponentFactory(componentType, system)
            self.RegisterForComponentType(componentType, system)




    def IsClientSideOnly(self, sceneID):
        return False



    def LoadEntityScene(self, sceneID):
        if sceneID in self.scenes:
            return self.scenes[sceneID]
        scene = self.__entitySceneType__(self, sceneID)
        self.scenes[sceneID] = scene
        self.loadingScenes[sceneID] = scene.LoadScene(self.unloadingScenes.get(sceneID, None))
        return scene



    def LoadEntitySceneAndBlock(self, sceneID):
        self.LogInfo('Getting entity scene', sceneID)
        if sceneID in self.loadingScenes:
            self.LogInfo('Waiting for entity scene', sceneID, ' thats currently loading')
            self.loadingScenes[sceneID].wait()
            self.LogInfo('Done waiting for entity scene', sceneID, ' that just finished loading')
        if sceneID not in self.scenes:
            self.LogInfo('Starting to load up entity scene ', sceneID)
            self.LoadEntityScene(sceneID)
            self.loadingScenes[sceneID].wait()
            self.LogInfo('Done waiting for entity scene', sceneID, ' that just finished loading')
        return self.scenes[sceneID]



    def WaitForEntityScene(self, sceneID):
        if sceneID in self.loadingScenes:
            self.LogInfo('Waiting for entity scene', sceneID, ' thats currently loading')
            self.loadingScenes[sceneID].wait()
            self.LogInfo('Done waiting for entity scene', sceneID, ' that just finished loading')



    def UnloadEntityScene(self, sceneID):
        self.LogInfo('Unloading entity scene', sceneID)
        scene = self.scenes.get(sceneID, None)
        if scene is None:
            self.LogWarn("Requesting unload of entity scene I don't have")
            return 
        self.LogInfo('Removing Scene reference for scene', sceneID)
        del self.scenes[sceneID]
        if sceneID in self.loadingScenes:
            del self.loadingScenes[sceneID]
        self.unloadingScenes[sceneID] = scene
        return scene.UnloadScene()



    def GetEntityScene(self, sceneID):
        return self.scenes.get(sceneID, None)



    def GetEntitySceneIDs(self):
        return self.scenes.keys()



    def RegisterForSceneLifeCycle(self, system):
        self.sceneCreationSubscriptions.add(system)
        self.LogInfo('Registered', system, ' for lifecycle')



    def _RegisterScene(self, scene, loadSemaphore):
        sceneID = scene.sceneID
        self.LogInfo('Registering entity scene ', sceneID)
        registrationCalls = []
        for system in self.sceneCreationSubscriptions:
            if hasattr(system, 'OnLoadEntityScene'):
                registrationCalls.append((system.OnLoadEntityScene, (sceneID,)))

        uthread.parallel(registrationCalls)
        sceneLoadedCalls = []
        for system in self.sceneCreationSubscriptions:
            if hasattr(system, 'OnEntitySceneLoaded'):
                sceneLoadedCalls.append((system.OnEntitySceneLoaded, (sceneID,)))

        uthread.parallel(sceneLoadedCalls)
        scene.state = EntitySceneState.READY
        if self.loadingScenes.get(scene.sceneID) == loadSemaphore:
            del self.loadingScenes[scene.sceneID]
        self.LogInfo('Finished loading entity scene ', sceneID)



    def _UnregisterScene(self, scene):
        scene.state = EntitySceneState.UNLOADING
        self.LogInfo('Unloading entity Scene', scene.sceneID)
        sm.ChainEvent('ProcessEntitySceneUnloading', scene.sceneID)



    def _TearDownScene(self, scene):
        self.LogInfo('Tearing Down entity Scene', scene.sceneID)
        unloadCalls = []
        for system in self.sceneCreationSubscriptions:
            if hasattr(system, 'OnUnloadEntityScene'):
                unloadCalls.append((system.OnUnloadEntityScene, (scene.sceneID,)))

        self.LogInfo('Unloading Entity Scene from', len(unloadCalls), 'systems')
        uthread.parallel(unloadCalls)
        self.LogInfo('Done unloading Entity Scene from', len(unloadCalls), 'systems')
        unloadedCalls = []
        for system in self.sceneCreationSubscriptions:
            if hasattr(system, 'OnEntitySceneUnloaded'):
                unloadedCalls.append((system.OnEntitySceneUnloaded, (scene.sceneID,)))

        self.LogInfo('Notifying', len(unloadedCalls), 'systems about Entity Scene having been unloaded')
        uthread.parallel(unloadedCalls)
        self.LogInfo('Done notifying about successful unload')
        del self.unloadingScenes[scene.sceneID]
        self.LogInfo('Done Unloading entity Scene', scene.sceneID)



    def CreateComponent(self, name, state):
        if name == 'logging':
            return entities.LoggingComponent()
        factory = self.componentFactories.get(name, None)
        if factory:
            return factory.CreateComponent(name, state)
        self.LogInfo('Failed to find a factory to create component', name)



    def GetComponentSystems(self, componentType):
        return self.componentSystems[componentType]



    def RegisterForComponentType(self, componentType, system):
        self.componentSystems[componentType].add(system)
        self.LogInfo('Registered', system, 'for components of type', componentType)



    def RegisterComponentFactory(self, componentType, factory):
        self.componentFactories[componentType] = factory
        self.LogInfo('Registered', factory, 'as factory for components of type', componentType)



    def GetComponentState(self, entity, componentName):
        try:
            try:
                ret = None
                factory = self.componentFactories[componentName]
                component = entity.components[componentName]
                ret = factory.ReportState(component, entity)
            except (KeyError, AttributeError):
                log.LogException()
                sys.exc_clear()

        finally:
            return ret




    def GetComponentStateByID(self, entityID, componentName):
        entity = self.FindEntityByID(entityID)
        return self.GetComponentState(entity, componentName)



    def _SetupComponents(self, entity, initData = None):
        entity.Log('Starting to setup')
        self.LogInfo('Starting to setup entity', entity.entityID, 'to scene', entity.scene.sceneID)
        if entity.entityID in entity.scene.entities:
            self.LogError('Adding a entity', entity.entityID, 'that already in this scene', entity.scene.sceneID, 'Ignoring entity')
            return False
        with entity.entityLock:
            try:
                if entity.state == const.cef.ENTITY_STATE_UNINITIALIZED:
                    self.loadingEntities[entity.entityID] = entity
                    entity.state = const.cef.ENTITY_STATE_CREATING
                    preperationCalls = []
                    funcContexts = []
                    for (name, component,) in entity.components.iteritems():
                        systems = self.GetComponentSystems(name)
                        if systems:
                            for system in systems:
                                f = getattr(system, 'PrepareComponent', None)
                                if f:
                                    preperationCalls.append((f, (entity.scene.sceneID, entity.entityID, component)))
                                    funcContexts.append(system.__guid__)


                    if preperationCalls:
                        self.LogInfo('Sending', len(preperationCalls), 'preparation calls for entity', entity.entityID)
                        uthread.parallel(preperationCalls, contextSuffix='PrepareComponent', funcContextSuffixes=funcContexts)
                    else:
                        self.LogInfo('Entity', entity.entityID, 'has no components that should be prepared')
                    self.LogInfo('Entity ', entity.entityID, ' prepared. Starting setup')
                    setupCalls = []
                    funcContexts = []
                    for (name, component,) in entity.components.iteritems():
                        systems = self.GetComponentSystems(name)
                        if systems:
                            for system in systems:
                                f = getattr(system, 'SetupComponent', None)
                                if f:
                                    setupCalls.append((f, (entity, component)))
                                    funcContexts.append(system.__guid__)


                    if setupCalls:
                        self.LogInfo('Sending', len(setupCalls), 'setup calls for entity', entity.entityID)
                        uthread.parallel(setupCalls, contextSuffix='SetupComponent', funcContextSuffixes=funcContexts)
                    else:
                        self.LogInfo('Entity', entity.entityID, 'has no components that should be setup')
                    self.LogInfo('Entity ', entity.entityID, ' setup. Starting network sync')
                    setupCalls = []
                    funcContexts = []
                    for (name, component,) in entity.components.iteritems():
                        systems = self.GetComponentSystems(name)
                        if systems:
                            for system in systems:
                                f = getattr(system, 'NetworkSyncComponent', None)
                                if f:
                                    setupCalls.append((f, (entity, component)))
                                    funcContexts.append(system.__guid__)


                    if setupCalls:
                        self.LogInfo('Sending', len(setupCalls), 'network sync calls for entity', entity.entityID)
                        uthread.parallel(setupCalls, contextSuffix='NetworkSyncComponent', funcContextSuffixes=funcContexts)
                    else:
                        self.LogInfo('Entity', entity.entityID, 'has no components that should perform network sync')
                    self.LogInfo('Done setting up entity:', entity.entityID)
                    entity.Log('Done setting up entity')
                    entity.scene.entities[entity.entityID] = entity
                else:
                    self.LogError('SetupComponents: Entity state should be', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_UNINITIALIZED], ', is instead ', const.cef.ENTITY_STATE_NAMES[entity.state], '.')
            except Exception as e:
                self._deadEntityList[entity.entityID] = entity
                log.LogException(e)
        self.LogInfo('Setup entity', entity.entityID, 'to scene', entity.scene.sceneID)
        entity.Log('Setup')



    def _RegisterComponents(self, entity, initData = None):
        entity.Log('Registering to scene (%s)' % entity.scene.sceneID)
        self.LogInfo('Registering entity', entity.entityID, 'to scene', entity.scene.sceneID)
        with uthread.BlockTrapSection():
            with entity.entityLock:
                try:
                    if entity.state == const.cef.ENTITY_STATE_CREATING:
                        entity.state = const.cef.ENTITY_STATE_READY
                        entity.scene.AddEntityToRegisteredList(entity)
                        self.entitySceneManager.Register(entity.entityID, entity.scene.sceneID)
                        registerCalls = []
                        for (name, component,) in entity.components.iteritems():
                            systems = self.GetComponentSystems(name)
                            if systems:
                                for system in systems:
                                    f = getattr(system, 'RegisterComponent', None)
                                    if f:
                                        self.LogInfo('Entity Component:', name, 'will be registered for entity', entity.entityID, ' with system:', system)
                                        registerCalls.append((f, (entity, component)))


                        if registerCalls:
                            self.LogInfo('Sending', len(registerCalls), 'registration calls for entity', entity.entityID)
                            for (f, args,) in registerCalls:
                                f(*args)

                        else:
                            self.LogInfo('Entity', entity.entityID, 'has no components that should be registered')
                        del self.loadingEntities[entity.entityID]
                    elif entity.state == const.cef.ENTITY_STATE_UNINITIALIZED or entity.state == const.cef.ENTITY_STATE_DEAD or entity.state == const.cef.ENTITY_STATE_READY:
                        self.LogError('RegisterComponents: Entity state should be either', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_CREATING], 'or', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_DESTROYING], ', is instead', const.cef.ENTITY_STATE_NAMES[entity.state], '.')
                    sm.ScatterEvent('OnEntityCreated', entity.entityID)
                    self.LogInfo('Registered entity', entity.entityID, 'to scene', entity.scene.sceneID)
                    entity.Log('Registered')
                except Exception as e:
                    self._deadEntityList[entity.entityID] = entity
                    if entity.scene and entity.entityID in entity.scene.entities:
                        del entity.scene.entities[entity.entityID]
                        self.entitySceneManager.Unregister(entity.entityID)
                    log.LogException(e)



    def _UnRegisterComponents(self, entity):
        entity.Log('Unregistering from scene (%s)' % entity.scene.sceneID)
        self.LogInfo('Unregistering', entity.entityID, 'from scene', entity.scene.sceneID)
        with uthread.BlockTrapSection():
            with entity.entityLock:
                try:
                    if entity.state == const.cef.ENTITY_STATE_READY:
                        registerCalls = []
                        for (name, component,) in entity.components.iteritems():
                            systems = self.GetComponentSystems(name)
                            if systems:
                                for system in systems:
                                    f = getattr(system, 'UnRegisterComponent', None)
                                    if f:
                                        self.LogInfo('Entity Component:', name, 'will be unregistered for entity', entity.entityID, ' with system:', system)
                                        registerCalls.append((f, (entity, component)))


                        if registerCalls:
                            self.LogInfo('Sending', len(registerCalls), 'unregistration calls for entity', entity.entityID)
                            for (f, args,) in registerCalls:
                                try:
                                    f(*args)
                                except Exception as e:
                                    self._deadEntityList[entity.entityID] = entity
                                    log.LogException(e)

                        else:
                            self.LogInfo('Entity', entity.entityID, 'has no components that should be unregistered')
                    elif entity.state == const.cef.ENTITY_STATE_UNINITIALIZED or entity.state == const.cef.ENTITY_STATE_DEAD or entity.state == const.cef.ENTITY_STATE_DESTROYING:
                        self.LogError('SetupComponents: Entity state should be either ', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_CREATING], ' or ', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_READY], ', is instead ', const.cef.ENTITY_STATE_NAMES[entity.state], '.')
                    entity.scene.RemoveEntityFromRegisteredList(entity)
                    self.entitySceneManager.Unregister(entity.entityID)
                    entity.state = const.cef.ENTITY_STATE_DESTROYING
                    self.LogInfo('Unregistered', entity.entityID, 'from scene', entity.scene.sceneID)
                    entity.Log('Unregistered')
                except Exception as e:
                    self._deadEntityList[entity.entityID] = entity
                    if entity.scene and entity.entityID in entity.scene.entities:
                        del entity.scene.entities[entity.entityID]
                        self.entitySceneManager.Unregister(entity.entityID)
                    log.LogException(e)



    def _TearDownComponents(self, entity):
        entity.Log('Tearing down from scene (%s)' % entity.scene.sceneID)
        self.LogInfo('Tearing down', entity.entityID, 'from scene', entity.scene.sceneID)
        with entity.entityLock:
            try:
                if entity.state == const.cef.ENTITY_STATE_DESTROYING:
                    entity.state = const.cef.ENTITY_STATE_DEAD
                    preTearDownCalls = []
                    for (name, component,) in entity.components.iteritems():
                        systems = self.GetComponentSystems(name)
                        if systems:
                            for system in systems:
                                f = getattr(system, 'PreTearDownComponent', None)
                                if f:
                                    self.LogInfo('PreTearing down component:', name, ' for entity', entity.entityID, ' from system:', system)
                                    preTearDownCalls.append((f, (entity, component)))


                    if preTearDownCalls:
                        self.LogInfo('Sending', len(preTearDownCalls), ' preTearDownCalls calls for entity', entity.entityID)
                        uthread.parallel(preTearDownCalls)
                    else:
                        self.LogInfo('Entity', entity.entityID, 'has no components that should be PreTornDown')
                    tearDownCalls = []
                    for (name, component,) in entity.components.iteritems():
                        systems = self.GetComponentSystems(name)
                        if systems:
                            for system in systems:
                                f = getattr(system, 'TearDownComponent', None)
                                if f:
                                    self.LogInfo('Tearing down component:', name, ' for entity', entity.entityID, ' from system:', system)
                                    tearDownCalls.append((f, (entity, component)))


                    if tearDownCalls:
                        self.LogInfo('Sending', len(tearDownCalls), ' TearDownCalls calls for entity', entity.entityID)
                        uthread.parallel(tearDownCalls)
                    else:
                        self.LogInfo('Entity', entity.entityID, 'has no components that should be TornDown')
                else:
                    self.LogError('SetupComponents: Entity state should be ', const.cef.ENTITY_STATE_NAMES[const.cef.ENTITY_STATE_DESTROYING], ', is instead ', const.cef.ENTITY_STATE_NAMES[entity.state], '.')
                sm.ScatterEvent('OnEntityDeleted', entity.entityID, entity.scene.sceneID)
                self.LogInfo('Torn down', entity.entityID, 'from scene', entity.scene.sceneID)
                entity.Log('Torn down')
            except Exception as e:
                self._deadEntityList[entity.entityID] = entity
                log.LogException(e)



    def CreateEntityFromRecipe(self, scene, recipe, entityItemID):
        self.LogInfo('Creating entity from recipe with supplied recipe in scene', scene.sceneID)
        newEntity = entities.Entity(scene, entityItemID)
        for (componentID, initValues,) in recipe.iteritems():
            componentName = entityCommon.GetComponentName(componentID)
            component = self.CreateComponent(componentName, initValues)
            if component is not None:
                newEntity.AddComponent(componentName, component)
            else:
                self.LogInfo('Adding component state to entity', componentName, initValues, entityItemID)
                newEntity.AddComponentState(componentName, initValues)

        self.LogInfo('Done creating entity from recipe - entity ID is', entityItemID)
        return newEntity



    def UnregisterAndDestroyEntityByID(self, entityID):
        for scene in self.scenes.itervalues():
            if entityID in scene._entityList:
                return scene.UnregisterAndDestroyEntity(scene._entityList[entityID])

        self.LogError("Attempting to destroy entity %s that doesn't exist even in the queue" % entityID)



    def ReceiveRemoteEntity(self, fromSceneID, entityID, sceneID, packedState):
        scene = self.GetEntityScene(sceneID)
        entity = entities.Entity(scene, entityID)
        for (componentName, state,) in packedState.iteritems():
            componentFactory = self.componentFactories.get(componentName, None)
            if componentFactory:
                component = componentFactory.CreateComponent(componentName, state)
                component = componentFactory.UnPackFromSceneTransfer(component, entity, state)
                entity.AddComponent(componentName, component)
            else:
                entity.AddComponentState(componentName, state)

        return scene.CreateAndRegisterEntity(entity)



    def FindEntityByID(self, entityID):
        for scene in self.scenes.itervalues():
            entity = scene.entities.get(entityID, None)
            if entity is not None:
                return entity




    def DestroyEntityByID(self, entid):
        entity = self.FindEntityByID(entid)
        if entity is not None:
            self.DestroyEntity(entity)



    def DestroyEntity(self, entity):
        if entity is not None:
            entity.scene.UnregisterAndDestroyEntity(entity)



    def GetEntityIdsInScene(self, sceneID):
        if sceneID in self.scenes:
            return self.scenes[sceneID].GetAllEntityIds()



    def GetEntityState(self, entity):
        ret = {}
        components = entity.components
        for (name, component,) in components.iteritems():
            try:
                factory = self.componentFactories[name]
                state = factory.ReportState(component, entity)
                if state is not None:
                    ret[name] = state
            except (KeyError, AttributeError):
                self.LogWarn('Component', name, 'I either have no factory or the factory does not report state.')
                sys.exc_clear()

        return ret



    def GetEntityStateByID(self, entityID):
        entity = self.FindEntityByID(entityID)
        return self.GetEntityState(entity)



    def WaitOnEntityEvents(self, entityID):
        eventQueue = self._entityQueues.get(entityID, None)
        while eventQueue is not None:
            eventQueue.GetLastSemaphore().wait()
            eventQueue = self._entityQueues.get(entityID, None)




    def _CreateEntity(self, entity, loadSemaphore, initData):
        if loadSemaphore is not None:
            loadSemaphore.wait()
        with bluepy.Timer('EntityService::_SetupComponents'):
            self._SetupComponents(entity, initData)



    def _RegisterEntity(self, entity, initData):
        self._RegisterComponents(entity, initData)



    def _UpdateEntity(self, entity, updateData):
        pass



    def _UnregisterEntity(self, entity):
        self._UnRegisterComponents(entity)



    def _DestroyEntity(self, entity):
        self._TearDownComponents(entity)
        entity.scene = None



    def _AddEvent(self, entityID, event, *args):
        queue = self._entityQueues.setdefault(entityID, EventQueue(lambda : self._RemoveEntityQueue(entityID)))
        return queue.AddEvent(event, *args)



    def _StartEvents(self, entityID):
        queue = self._entityQueues[entityID]
        queue.StartEvents()



    def _RemoveEntityQueue(self, entityID):
        del self._entityQueues[entityID]



    def PackUpForClientTransfer(self, component):
        return None



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        machoNet = sm.GetService('machoNet')
        destinationNodeID = machoNet.GetNodeFromAddress(const.cluster.SERVICE_WORLDSPACE, destinationSceneID)
        nodeID = machoNet.GetNodeID()
        state = {'SameNode': destinationNodeID == nodeID}
        if destinationNodeID == nodeID:
            component.Log('Packed up state for intranode transfer')
            return component.history



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.history = state
        component.Log('Unpacked from intranode transfer')
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        for (time, text,) in component.history:
            report[time] = text

        return report




