import blue
import copy
import entityCommon
import log
import random
import service
import uthread
import util
import GameWorld
import zaction

class EntitySpawnService(service.Service):
    __guid__ = 'entities.EntitySpawnService'
    __exportedcalls__ = {}
    __notifyevents__ = ['ProcessEntitySceneUnloading', 'OnEntityDeleted']
    __dependencies__ = ['entityRecipeSvc']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.generators = {}
        self.generatorThreads = {}
        self.lastSpawnIndexByGenerator = {}
        GameWorld.RegisterPythonActionProc('SpawnEntity', self._SpawnEntityProc, ('entitySceneID', 'posProp', 'rotProp', 'typeID', 'entityIDProp'))
        GameWorld.RegisterPythonActionProc('DespawnEntity', self._DespawnEntityProc, ('entityIDProp',))



    def _SpawnEntityProc(self, entitySceneID, posProp, rotProp, typeID, entityIDProp):
        position = GameWorld.GetPropertyForCurrentPythonProc(posProp)
        rotation = GameWorld.GetPropertyForCurrentPythonProc(rotProp)
        if position is None:
            self.LogError('SpawnEntityProc: Position property with name ', posProp, ' does not exist!')
            return False
        if rotation is None:
            self.LogError('SpawnEntityProc: Rotation property with name ', posProp, ' does not exist!')
            return False
        scene = self.entityService.LoadEntityScene(entitySceneID)
        overrides = {}
        positionComponentID = const.cef.POSITION_COMPONENT_ID
        overrides[positionComponentID] = {}
        overrides[positionComponentID]['position'] = position
        overrides[positionComponentID]['rotation'] = rotation
        recipe = sm.GetService('entityRecipeSvc').GetTypeRecipe(typeID, overrides)
        if recipe is None:
            self.LogError('SpawnEntityProc: Invalid type ID ', typeID, '!')
            return False
        itemID = self.GetNextSpawnID(entitySceneID, typeID)
        spawnedEntity = self.entityService.CreateEntityFromRecipe(scene, recipe, itemID)
        if spawnedEntity is None:
            self.LogError('SpawnEntityProc: Error spawning entity!')
            return False
        scene.CreateAndRegisterEntity(spawnedEntity)
        GameWorld.AddPropertyForCurrentPythonProc({entityIDProp: spawnedEntity.entityID})
        return True



    def _DespawnEntityProc(self, entityIDProp):
        entID = GameWorld.GetPropertyForCurrentPythonProc(entityIDProp)
        if entID is None:
            self.LogError('DespawnEntityProc: Entity ID property with name ', entityIDProp, ' does not exist!')
            return False
        self.entityService.UnregisterAndDestroyEntityByID(entID)
        return True



    def OnLoadEntityScene(self, sceneID):
        pass



    def OnEntitySceneLoaded(self, sceneID):
        self.LoadGenerators(sceneID)



    def OnUnloadEntityScene(self, sceneID):
        pass



    def MapSceneIDToWorldSpaceID(self, sceneID):
        raise NotImplementedError('calling common version of this')



    def LoadGenerators(self, sceneID):
        worldSpaceTypeID = self.MapSceneIDToWorldSpaceID(sceneID)
        self.LogInfo('Loading and spawning scene generators for sceneID', sceneID, '==> worldSpaceTypeID', worldSpaceTypeID)
        self.generators[sceneID] = []
        for generator in self.GetGenerators(sceneID):
            if boot.role == 'server' and generator.clientOnly:
                continue
            generatorSpawns = self.GetGeneratorSpawns(generator.generatorID)
            newGenerator = util.KeyVal(generatorID=generator.generatorID, sceneID=sceneID, worldSpaceTypeID=generator.worldSpaceTypeID, spawns=generatorSpawns, lastSpawnTime=None, maxSpawns=generator.maxSpawns, spawnPattern=generator.spawnPattern, spawnInterval=generator.spawnInterval * SEC, spawnPoint=(generator.spawnPointX, generator.spawnPointY, generator.spawnPointZ), spawnRotation=(generator.spawnRotationY, generator.spawnRotationX, generator.spawnRotationZ), spawnRadius=generator.spawnRadius, randomRotation=generator.randomRotation, currentSpawns=[], active=generator.generatorType == const.cef.GENERATOR_TYPE_ACTIVE_ON_LOAD, activationRefCount=1 if generator.generatorType == const.cef.GENERATOR_TYPE_ACTIVE_ON_LOAD else 0)
            self.generators[sceneID].append(newGenerator)

        nextSpawnTime = self._SpawnScene(sceneID)
        if nextSpawnTime is not None:
            self.generatorThreads[sceneID] = uthread.worker('EntitySpawnService::_SpawnLoop', self._SpawnLoop, sceneID, nextSpawnTime)



    def GetGeneratorSpawns(self, generatorID):
        generatorSpawns = []
        spawnRows = cfg.entitySpawnByGenerator.get(generatorID, [])
        for spawn in spawnRows:
            spawnOverrides = self._GetSpawnOverrides(spawn.spawnID)
            newSpawn = util.KeyVal(spawnID=spawn.spawnID, typeID=spawn.typeID, overrides=spawnOverrides, generatorID=generatorID)
            generatorSpawns.append(newSpawn)

        return generatorSpawns



    def _GetSpawnOverrides(self, spawnID):
        spawnOverrides = {}
        overrideRows = cfg.entitySpawnInitsBySpawn.get(spawnID, [])
        for overrideRow in overrideRows:
            if overrideRow.componentID not in spawnOverrides:
                spawnOverrides[overrideRow.componentID] = {}
            val = entityCommon.GetIngredientInitialValue(overrideRow, const.cef.SPAWN_OVERRIDES_TABLE_FULL_NAME)
            if overrideRow.keyName is None:
                spawnOverrides[overrideRow.componentID][overrideRow.initialValueName] = val
            else:
                if 'keyedData' not in spawnOverrides:
                    spawnOverrides['keyedData'] = {}
                if overrideRow.keyName not in spawnOverrides['keyedData']:
                    spawnOverrides['keyedData'][overrideRow.keyName] = {}
                spawnOverrides['keyedData'][overrideRow.keyName][overrideRow.initialValueName] = val

        return spawnOverrides



    def _SpawnLoop(self, sceneID, nextSpawnTime):
        sleepyTime = (nextSpawnTime - blue.os.GetTime()) / const.MSEC
        blue.pyos.synchro.Sleep(sleepyTime)
        while self.state == service.SERVICE_RUNNING:
            if sceneID not in self.generators or len(self.generators[sceneID]) < 1:
                break
            nextSpawnTime = self._SpawnScene(sceneID)
            if nextSpawnTime is None:
                break
            sleepyTime = (nextSpawnTime - blue.os.GetTime()) / const.MSEC
            self.LogInfo('_SpawnLoop :: Spawning for scene', sceneID, 'sleeping for', sleepyTime, 'msec')
            blue.pyos.synchro.Sleep(sleepyTime)




    def _SpawnScene(self, sceneID):
        generators = self.generators[sceneID]
        (generator, nextSpawnTime,) = self._GetNextSpawn(generators)
        while nextSpawnTime is not None and nextSpawnTime <= blue.os.GetTime():
            self._Spawn(generator)
            (generator, nextSpawnTime,) = self._GetNextSpawn(self.generators[sceneID])

        return nextSpawnTime



    def _GetNextSpawn(self, generatorList):
        if len(generatorList) < 1:
            return (None, None)
        earliestGenerator = earliestSpawnTime = None
        for generator in generatorList:
            if not generator.active:
                continue
            if len(generator.currentSpawns) >= generator.maxSpawns:
                continue
            if earliestGenerator is None:
                earliestGenerator = generator
                earliestSpawnTime = generator.lastSpawnTime + generator.spawnInterval if generator.lastSpawnTime is not None else blue.os.GetTime()
            elif generator.lastSpawnTime is None:
                earliestGenerator = generator
                earliestSpawnTime = blue.os.GetTime()
                break
            elif generator.lastSpawnTime + generator.spawnInterval < earliestSpawnTime:
                earliestGenerator = generator
                earliestSpawnTime = generator.lastSpawnTime + generator.spawnInterval

        return (earliestGenerator, earliestSpawnTime)



    def _Spawn(self, generator):
        if len(generator.spawns) >= 1:
            spawn = self._GetSpawnFromGenerator(generator)
            if spawn.typeID is not None:
                position = self._GetPositionFromGenerator(generator)
                rotation = self._GetRotationFromGenerator(generator)
                overrides = copy.deepcopy(spawn.overrides)
                overrides = self.OverridePosition(overrides, position, rotation)
                recipe = self.entityRecipeSvc.GetTypeRecipe(spawn.typeID, overrides)
                itemID = self.GetNextSpawnID(generator.sceneID, spawn.typeID)
                for (componentID, initValues,) in recipe.iteritems():
                    initValues['_spawnID'] = spawn.spawnID

                scene = self.entityService.LoadEntityScene(generator.sceneID)
                spawnedEntity = self.entityService.CreateEntityFromRecipe(scene, recipe, itemID)
                scene.CreateAndRegisterEntity(spawnedEntity)
                generator.currentSpawns.append(spawnedEntity.entityID)
            else:
                self.LogError('CONTENT ERROR - No type on spawn authored on generator', generator.generatorID)
        else:
            self.LogError('CONTENT ERROR - No spawns authored on generator', generator.generatorID)
        generator.lastSpawnTime = blue.os.GetTime()



    def _GetSpawnFromGenerator(self, generator):
        if generator.spawnPattern == const.cef.PATTERN_CYCLIC:
            index = self.lastSpawnIndexByGenerator.get(generator.generatorID, len(generator.spawns)) + 1
            if index >= len(generator.spawns):
                index = 0
            spawn = generator.spawns[index]
            self.lastSpawnIndexByGenerator[generator.generatorID] = index
        else:
            spawn = random.choice(generator.spawns)
        return spawn



    def _GetPositionFromGenerator(self, generator):
        position = generator.spawnPoint
        if generator.spawnRadius > 0.0:
            gw = self.gameWorldService.GetGameWorld(generator.sceneID)
            position = self.FindRandomPointAtFloor(position, generator.spawnRadius, gw)
        return position



    def _GetRotationFromGenerator(self, generator):
        rotation = generator.spawnRotation
        if generator.randomRotation:
            newYaw = rotation[0] + random.randrange(-180, 180)
            rotation = (newYaw, rotation[1], rotation[2])
        return rotation



    def ProcessEntitySceneUnloading(self, sceneID):
        self.LogInfo('EntitySpawnService::OnEntitySceneUnloading', sceneID)
        generators = self.generators.get(sceneID, [])
        for generator in generators:
            generator.activationRefCount = 0
            generator.active = False

        thread = self.generatorThreads.get(sceneID, None)
        if thread is not None and thread.alive:
            thread.kill()



    def OnEntityDeleted(self, entityID, sceneID):
        generators = self.generators.get(sceneID, [])
        entityGenerator = None
        for generator in generators:
            if entityID in generator.currentSpawns:
                entityGenerator = generator
                break

        if entityGenerator is not None:
            entityGenerator.currentSpawns.remove(entityID)
            if entityGenerator.active and len(entityGenerator.currentSpawns) < entityGenerator.maxSpawns:
                if sceneID not in self.generatorThreads or not self.generatorThreads[sceneID].alive:
                    self.LogInfo('OnEntityDeleted found generator', generator.generatorID, 'without live spawning thread - restarting spawn thread')
                    self.generatorThreads[sceneID] = uthread.new(self._SpawnLoop, sceneID, 0)
                    self.generatorThreads[sceneID].context = 'EntitySpawnService::OnEntityDeleted'



    def OverridePosition(self, overrides, position, rotation):
        positionComponentID = const.cef.POSITION_COMPONENT_ID
        if positionComponentID not in overrides:
            overrides[positionComponentID] = {}
        overrides[positionComponentID]['position'] = position
        overrides[positionComponentID]['rotation'] = rotation
        return overrides



    def FindRandomPointAtFloor(self, position, radius, gameworld):
        posAtFloor = None
        tries = 0
        while not posAtFloor:
            newX = position[0] + random.uniform(-radius, radius)
            newY = position[1]
            newZ = position[2] + random.uniform(-radius, radius)
            posAtFloor = gameworld.GetHeightAtPoint((newX, newY, newZ), 2.0, 2.0)
            blue.pyos.BeNice()
            tries += 1
            if tries > 50:
                break

        if posAtFloor:
            position = posAtFloor[0]
        else:
            log.LogError('Generator did not find a random spot on the floor, reveting to orgina position')
        return position



exports = {'actionProcTypes.SpawnEntity': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('typeID', 'I', userDataType=None, isPrivate=True),
                                 zaction.ProcPropertyTypeDef('posProp', 'S', userDataType='Position Property', isPrivate=True),
                                 zaction.ProcPropertyTypeDef('rotProp', 'S', userDataType='Rotation Property', isPrivate=True),
                                 zaction.ProcPropertyTypeDef('entityIDProp', 'S', userDataType='Entity ID Property', isPrivate=True)]),
 'actionProcTypes.DespawnEntity': zaction.ProcTypeDef(isMaster=True, procCategory='Entity', properties=[zaction.ProcPropertyTypeDef('entityIDProp', 'S', userDataType='Entity ID Property', isPrivate=True)])}

