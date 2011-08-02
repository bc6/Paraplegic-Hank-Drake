import blue
import bluepy
import GameWorld
import geo2
import log
import math
import miscUtil
import stackless
import uthread
import util
import world
failedCollision = []

class CoreWorldSpace(object):
    __guid__ = 'world.CoreWorldSpace'
    LOADING = 1
    NOT_LOADING = 2
    __dataTypes__ = {const.world.TYPE_OBJECT: util.KeyVal(createFuncName='_CreateObject', tableFullName=const.world.WORLD_SPACE_OBJECT_MAIN_TABLE, cfgName='worldspaceObjectsByWorldspaceID'),
     const.world.TYPE_PHYSICAL_PORTAL: util.KeyVal(createFuncName='_CreatePhysicalPortal', tableFullName=const.world.WORLD_PHYSICAL_PORTAL_MAIN_TABLE, cfgName='worldspacePhysicalPortals'),
     const.world.TYPE_LIGHT: util.KeyVal(createFuncName='_CreateLight', tableFullName=const.world.WORLD_LIGHTS_MAIN_TABLE, cfgName='worldspaceLights'),
     const.world.TYPE_OCCLUDER: util.KeyVal(createFuncName='_CreateOccluder', tableFullName=const.world.WORLD_OCCLUDERS_MAIN_TABLE, cfgName='worldspaceOccluders')}
    __worldOccluderClass__ = world.Occluder
    __worldSpaceObjectClass__ = world.WorldSpaceObject
    __worldLightClass__ = world.WorldLight
    __worldPhysicalPortalClass__ = world.PhysicalPortal

    def __init__(self, worldSpaceTypeID, worldSpaceID):
        self.worldSpaceTypeID = worldSpaceTypeID
        self.worldSpaceID = worldSpaceID
        if not hasattr(self, 'mainRow'):
            self.mainRow = cfg.worldspaces.Get(worldSpaceTypeID)
        if not hasattr(self, 'coreInventoryTypeRow'):
            self.coreInventoryTypeRow = cfg.invtypes.Get(worldSpaceTypeID)
        self.loadedData = {}
        for typeName in self.__dataTypes__:
            self.loadedData[typeName] = {}

        self.boundingBox = (geo2.Vector(0, 0, 0), geo2.Vector(0, 0, 0))
        self.ground = None
        self.isLoading = {}
        self.isLoaded = {}
        self.waitingOnLoad = {}
        self._SetupGraphicsSvc()



    def _SetupGraphicsSvc(self):
        role = boot.role
        if role == 'client':
            self.graphicSvc = sm.GetService('graphicClient')
        else:
            self.graphicSvc = sm.GetService('graphicServer')



    def GetWorldSpaceID(self):
        return self.worldSpaceID



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetName(self):
        return self.coreInventoryTypeRow.typeName



    def GetDescription(self):
        return self.coreInventoryTypeRow.description



    def GetParentWorldSpaceTypeID(self):
        return self.mainRow.parentWorldSpaceTypeID



    def GetSafeSpotPosition(self):
        return (self.mainRow.safeSpotX, self.mainRow.safeSpotY, self.mainRow.safeSpotZ)



    def SetSafeSpotPosition(self, pos):
        (self.mainRow.safeSpotX, self.mainRow.safeSpotY, self.mainRow.safeSpotZ,) = pos



    def GetSafeSpotYaw(self):
        return self.mainRow.safeSpotRotY



    def GetSafeSpotYawDegrees(self):
        return math.degrees(self.GetSafeSpotYaw())



    def GetDistrictID(self):
        row = self.mainRow
        while row and row.districtID is None and row.parentWorldSpaceTypeID is not None:
            row = cfg.worldspaces.Get(row.parentWorldSpaceTypeID)

        if row:
            return row.districtID
        districtlessWorldSpace = self.worldSpaceTypeID
        row = self.mainRow
        while row and row.districtID is None and row.parentWorldSpaceTypeID is not None:
            districtlessWorldSpace = row.parentWorldSpaceTypeID
            row = cfg.worldspaces.Get(row.parentWorldSpaceTypeID)

        log.LogError("WorldSpace doesn't have a parent or a district worldSpaceTypeID: %d" % districtlessWorldSpace)



    def IsInterior(self):
        return self.mainRow.isInterior



    def GetIsUnique(self):
        return self.mainRow.isUnique



    def IsObsolete(self):
        return self.mainRow.obsolete



    def GetSafeSpotTransformMatrix(self):
        rotQuat = geo2.QuaternionRotationSetYawPitchRoll(self.GetSafeSpotYaw(), 0, 0)
        rotMatrix = geo2.MatrixRotationQuaternion(rotQuat)
        rotMatrix = geo2.MatrixInverse(rotMatrix)
        transMatrix = geo2.MatrixTranslation(*self.GetSafeSpotPosition())
        return geo2.MatrixMultiply(rotMatrix, transMatrix)



    def SetIsUnique(self, isUnique):
        self.isUnique = False



    def _GetData(self, typeName, keyID):
        self.Load(typeName, keyID)
        return self.loadedData[typeName].get(keyID, None)



    def _GetDataAll(self, typeName):
        self.Load(typeName)
        return self.loadedData[typeName].values()



    def _HasData(self, typeName, keyID):
        return keyID in self.loadedData[typeName]



    def _SetData(self, typeName, keyID, value):
        self.loadedData[typeName][keyID] = value



    def Load(self, typeName = None, keyID = None):
        if typeName is None:
            for typeName in self.__dataTypes__.iterkeys():
                self.Load(typeName)

            return 
        if not self.isLoading.get(typeName, False):
            self.isLoading[typeName] = True
            for row in self._GetDataRows(typeName):
                self._LoadDataRow(typeName, row)
                blue.pyos.BeNice()

            self.isLoaded[typeName] = True
            for channel in self.waitingOnLoad.get(typeName, []):
                channel.send(None)

        if not self.isLoaded.get(typeName, False):
            if typeName not in self.waitingOnLoad:
                self.waitingOnLoad[typeName] = []
            channel = stackless.channel()
            self.waitingOnLoad[typeName].append(channel)
            channel.receive()



    def IsLoaded(self, typeName):
        return self.isLoaded.get(typeName, False)



    def SetLoaded(self, typeName):
        self.isLoaded[typeName] = True



    def _GetDataRows(self, typeName):
        dataType = self.__dataTypes__[typeName]
        return getattr(cfg, dataType.cfgName).get(self.GetWorldSpaceTypeID(), ())



    def _LoadDataRow(self, typeName, dataRow, keyID = None):
        obj = getattr(self, self.__dataTypes__[typeName].createFuncName)(dataRow)
        if obj is None:
            return 
        if keyID is None:
            keyID = obj.GetID()
        self.loadedData[typeName][keyID] = obj
        return obj



    def GetObject(self, objectID):
        return self._GetData(const.world.TYPE_OBJECT, objectID)



    def HasObject(self, objectID):
        return self._HasData(const.world.TYPE_OBJECT, objectID)



    def GetObjects(self):
        return self._GetDataAll(const.world.TYPE_OBJECT)



    def _CreateObject(self, row):
        return self.__worldSpaceObjectClass__(row)



    def GetPhysicalPortal(self, portalID):
        return self._GetData(const.world.TYPE_PHYSICAL_PORTAL, portalID)



    def HasPhysicalPortal(self, portalID):
        return self._HasData(const.world.TYPE_PHYSICAL_PORTAL, portalID)



    def GetPhysicalPortals(self):
        return self._GetDataAll(const.world.TYPE_PHYSICAL_PORTAL)



    def _CreatePhysicalPortal(self, row):
        return self.__worldPhysicalPortalClass__(row)



    def GetLight(self, lightID):
        return self._GetData(const.world.TYPE_LIGHT, lightID)



    def HasLight(self, lightID):
        return self._HasData(const.world.TYPE_LIGHT, lightID)



    def GetLights(self):
        return self._GetDataAll(const.world.TYPE_LIGHT)



    def _CreateLight(self, row):
        return self.__worldLightClass__(row)



    def GetOccluder(self, occluderID):
        return self._GetData(const.world.TYPE_OCCLUDER, occluderID)



    def HasOccluder(self, occluderID):
        return self._HasData(const.world.TYPE_OCCLUDER, occluderID)



    def GetOccluders(self):
        return self._GetDataAll(const.world.TYPE_OCCLUDER)



    def _CreateOccluder(self, row):
        return self.__worldOccluderClass__(row)



    def GetGameWorld(self):
        svcName = {'client': 'gameWorldClient',
         'server': 'gameWorldServer'}[boot.role]
        return sm.GetService(svcName).GetGameWorld(self.worldSpaceID)



    def HasGameWorld(self):
        svcName = {'client': 'gameWorldClient',
         'server': 'gameWorldServer'}[boot.role]
        return sm.GetService(svcName).HasGameWorld(self.worldSpaceID)



    def LoadGameWorldStaticObjects(self):
        with bluepy.Timer('worldSpaceLoad::staticObjectsLoad'):
            calls = []
            for staticObject in self.GetObjects():
                if not staticObject.IsEntity():
                    calls.append((self.LoadIndividualStaticObject, (staticObject,)))
                blue.pyos.BeNice()

            uthread.parallel(calls)
            self.loadedStaticObjects = True



    def LoadIndividualStaticObject(self, staticObject, entID = 0):
        with bluepy.Timer('worldSpaceLoad::staticObjectsLoad::individualObject'):
            if not self.HasGameWorld():
                return 
            PushMark('worldSpaceLoad::staticObjectsLoad::individualObject')
            if staticObject.GetGameWorldObject():
                self.GetGameWorld().RemoveStaticShape(staticObject.GetGameWorldObject())
                staticObject.SetGameWorldObject(None)
        gwStaticObject = None
        qRot = geo2.QuaternionRotationSetYawPitchRoll(*staticObject.GetRotation())
        collisionPath = staticObject.GetCollisionResFilePath()
        with bluepy.Timer('worldSpaceLoad::staticObjectsLoad::individualObject'):
            if staticObject.GetGameWorldObject():
                self.GetGameWorld().RemoveStaticShape(staticObject.GetGameWorldObject())
                staticObject.SetGameWorldObject(None)
            gwStaticObject = None
            qRot = geo2.QuaternionRotationSetYawPitchRoll(*staticObject.GetRotation())
            collisionPath = staticObject.GetCollisionResFilePath()
            if staticObject.IsCollidable() and collisionPath and collisionPath not in failedCollision:
                physXResPath = miscUtil.GetCommonResourcePath(collisionPath)
                fileChecker = blue.ResFile()
                if not fileChecker.FileExists(physXResPath):
                    log.LogError('Trying to load a nonexisting physX mesh:', physXResPath)
                    failedCollision.append(collisionPath)
                    aabb = (staticObject.GetPosition(), staticObject.GetPosition())
                    staticObject.SetBoundingBox(aabb)
                else:
                    gwStaticObject = GameWorld.CreateStaticMeshAndWait(self.GetGameWorld(), physXResPath, staticObject.GetPosition(), qRot)
                    if not gwStaticObject:
                        log.LogError('Loading of PhysXResource failed:', physXResPath)
                        failedCollision.append(collisionPath)
                        aabb = (staticObject.GetPosition(), staticObject.GetPosition())
                        staticObject.SetBoundingBox(aabb)
                        return 
                    gwStaticObject.entID = entID
                    aabb = gwStaticObject.GetWorldAABB()
                    staticObject.SetBoundingBox(aabb)
                    staticObject.SetGameWorldObject(gwStaticObject)
            else:
                return 
            return gwStaticObject



    def LoadEntities(self):
        systemName = boot.role.title()
        self.entitySvc = sm.GetService('entity' + systemName)
        self.entitySpawnSvc = sm.GetService('entitySpawn' + systemName)
        scene = self.entitySvc.GetEntityScene(self.GetWorldSpaceID())
        self.LoadObjectEntities(scene)



    def LoadObjectEntities(self, scene):
        for obj in self.GetObjects():
            self._CreateObjectEntity(scene, obj)
            blue.pyos.BeNice()




    def _CreateObjectEntity(self, scene, obj):
        recipe = {'position': {'position': obj.GetPosition(),
                      'rotation': obj.GetRotation()}}
        graphicRow = cfg.graphics.GetIfExists(obj.GetGraphicID())
        if graphicRow is None:
            log.LogError('WorldSpaceObject', obj.GetID(), 'in worldSpaceTypeID', self.GetWorldSpaceTypeID(), 'is using an invalid graphicID', obj.GetGraphicID())
            return 
        if graphicRow.collisionFile:
            recipe['collisionMesh'] = {'graphicID': obj.GetGraphicID()}
        e = self.entitySvc.CreateEntityFromRecipe(scene, recipe, self.entitySpawnSvc.GetNextSpawnID(self.GetWorldSpaceID(), 0))
        scene.CreateAndRegisterEntity(e)



worldSpaceCache = {}

def GetWorldSpace(worldSpaceID):
    global worldSpaceCache
    if worldSpaceID is None:
        return 
    ws = worldSpaceCache.get(worldSpaceID, None)
    if ws is None:
        try:
            ws = world.WorldSpace(worldSpaceID, None)
            worldSpaceCache[worldSpaceID] = ws
        except KeyError:
            return 
    return ws



def GetWorldSpaceName(worldSpaceID):
    if worldSpaceID is None:
        return 
    worldSpace = world.GetWorldSpace(worldSpaceID)
    if worldSpace:
        return worldSpace.GetName()


exports = {'world.GetWorldSpace': GetWorldSpace,
 'world.GetWorldSpaceName': GetWorldSpaceName}

