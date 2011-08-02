import log
import uthread
import world
import blue
POINT_LIGHT = 0
SPOT_LIGHT = 1
BOX_LIGHT = 2

class WorldSpaceScene(world.WorldSpace):
    __guid__ = 'world.CoreWorldSpaceScene'

    def __init__(self, worldSpaceID = None, instanceID = None):
        world.WorldSpace.__init__(self, worldSpaceID, instanceID)
        self.scene = None
        self.properties = {}



    def IsFM(self):
        return '_FM' in self.GetName()



    def LoadEntities(self):
        self.entityClient = sm.GetService('entityClient')
        self.entitySpawnClient = sm.GetService('entitySpawnClient')
        scene = self.entityClient.GetEntityScene(self.GetWorldSpaceID())
        self.LoadObjectEntities(scene)
        self.LoadLightEntities(scene)
        self.LoadPhysicalPortalEntities(scene)
        self.LoadOccluderEntities(scene)



    def LoadLightEntities(self, scene):
        for light in self.GetLights():
            self._CreateLightEntity(scene, light)
            blue.pyos.BeNice()




    def LoadPhysicalPortalEntities(self, scene):
        for portal in self.GetPhysicalPortals():
            self._CreatePhysicalPortalEntity(scene, portal)
            blue.pyos.BeNice()




    def LoadOccluderEntities(self, scene):
        for occluder in self.GetOccluders():
            self._CreateOccluderEntity(scene, occluder)
            blue.pyos.BeNice()




    def _GetLightType(self, light):
        if light.GetLightType() == world.BASIC_LIGHT:
            if light.IsSpotLight():
                return SPOT_LIGHT
            else:
                return POINT_LIGHT
        elif light.GetLightType() == world.BOX_LIGHT:
            return BOX_LIGHT



    def _CreateLightEntity(self, scene, light):
        lightType = self._GetLightType(light)
        if lightType == SPOT_LIGHT:
            componentName = 'spotLight'
        elif lightType == POINT_LIGHT:
            componentName = 'pointLight'
        elif lightType == BOX_LIGHT:
            componentName = 'boxLight'
        recipe = {'position': {'position': light.GetPosition(),
                      'rotation': light.GetRotation()},
         componentName: light}
        e = self.entityClient.CreateEntityFromRecipe(scene, recipe, self.entitySpawnClient.GetNextSpawnID(self.GetWorldSpaceID(), 0))
        scene.CreateAndRegisterEntity(e)



    def _CreateObjectEntity(self, scene, obj):
        enlightenAreaRows = cfg.worldspaceEnlightenAreas.get(self.GetWorldSpaceTypeID(), {}).get(obj.GetID(), ())
        recipe = {'position': {'position': obj.GetPosition(),
                      'rotation': obj.GetRotation()}}
        graphicRow = cfg.graphics.GetIfExists(obj.GetGraphicID())
        if graphicRow is None:
            log.LogError('WorldSpaceObject', obj.GetID(), 'in worldSpaceTypeID', self.GetWorldSpaceTypeID(), 'is using an invalid graphicID', obj.GetGraphicID())
            return 
        if graphicRow.graphicType == 'Tr2InteriorStatic':
            recipe['interiorStatic'] = {'graphicID': obj.GetGraphicID(),
             'cellID': str(obj.GetCellID()),
             'systemID': str(obj.GetSystemID()),
             'objectID': obj.GetID(),
             'enlightenOverrides': enlightenAreaRows}
        else:
            recipe['interiorPlaceable'] = {'graphicID': obj.GetGraphicID()}
        if graphicRow.collisionFile:
            recipe['collisionMesh'] = {'graphicID': obj.GetGraphicID()}
        e = self.entityClient.CreateEntityFromRecipe(scene, recipe, self.entitySpawnClient.GetNextSpawnID(self.GetWorldSpaceID(), 0))
        scene.CreateAndRegisterEntity(e)



    def _CreatePhysicalPortalEntity(self, scene, physicalPortal):
        recipe = {'position': {'position': physicalPortal.GetPosition(),
                      'rotation': physicalPortal.GetRotation()},
         'physicalPortal': {'scaleX': physicalPortal.GetScale()[0],
                            'scaleY': physicalPortal.GetScale()[1],
                            'scaleZ': physicalPortal.GetScale()[2],
                            'cellA': physicalPortal.GetCellA(),
                            'cellB': physicalPortal.GetCellB()}}
        e = self.entityClient.CreateEntityFromRecipe(scene, recipe, self.entitySpawnClient.GetNextSpawnID(self.GetWorldSpaceID(), 0))
        scene.CreateAndRegisterEntity(e)



    def _CreateOccluderEntity(self, scene, occluder):
        recipe = {'position': {'position': occluder.GetPosition(),
                      'rotation': occluder.GetRotation()},
         'occluder': {'cellName': occluder.GetCellName(),
                      'scaleX': occluder.GetScale()[0],
                      'scaleY': occluder.GetScale()[1],
                      'scaleZ': occluder.GetScale()[2]}}
        e = self.entityClient.CreateEntityFromRecipe(scene, recipe, self.entitySpawnClient.GetNextSpawnID(self.GetWorldSpaceID(), 0))
        scene.CreateAndRegisterEntity(e)



    def _CreateObject(self, row):
        obj = world.WorldSpace._CreateObject(self, row)
        if obj.IsEntity():
            return None
        return obj



    def _CreatePhysicalPortal(self, row):
        portal = world.WorldSpace._CreatePhysicalPortal(self, row)
        return portal



    def _ConnectPhysicalPortal(self, portal):
        try:
            scene = sm.GetService('graphicClient').GetScene(self.GetWorldSpaceID())
        except AttributeError:
            scene = self.scene
        if scene:
            cells = scene.cells
            cellAObj = None
            cellBObj = None
            for cell in cells:
                if portal.GetCellA() == cell.name:
                    cellAObj = cell
                elif portal.GetCellB() == cell.name:
                    cellBObj = cell

            portal.GetRenderObject().ConnectCells(cellAObj, cellBObj)



    def LoadProperties(self):
        pass




