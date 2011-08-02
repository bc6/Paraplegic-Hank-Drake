import uix
import math
import blue
import util
import trinity
import uthread
import slayConst
import minigames
import slaycommon
import minigameConst
import graphicWrappers
HEX_ROT = (math.pi / 2.0, 0.0, 0.0)
UNIT_ROT = (0.0, 0.0, 0.0)
TILEOFFSET = -0.008
BORDER_TILEOFFSET = -0.009
START_LOC_X = -0.885
START_LOC_Y = 0.9
START_LOC_Z = -0.665
HOVER_ELEVATE_Y = 0.03
TABLE_EDGE_ROT = {1: (0.0, math.pi / 2, math.pi / 2),
 2: (0.0, math.pi / 2, math.pi / 6),
 3: (0.0, math.pi / 2, -math.pi / 6),
 4: (0.0, math.pi / 2, -math.pi / 2),
 5: (0.0, math.pi / 2, math.pi / 6),
 6: (0.0, math.pi / 2, -math.pi / 6)}

class SlayModelManager:
    __guid__ = 'minigames.SlayModelManager'

    def __init__(self, controller):
        self.controller = controller
        self.pickResult = None
        self.flashing = False
        self.possibleMoveTiles = []
        self.possibleMovesTuples = []
        self.terminated = False
        self.lightPositions = {}
        self.lightInstances = {}
        self.instanceIndex = {}
        self.highlightsInstance = []
        self.tilesInstances = []
        self.tilesBorderInstances = []
        self.flashHighlightInstances = []
        self.townsInstances = []
        self.spearmenInstances = []
        self.pineForestsInstances = []
        self.peasantsInstances = []
        self.palmForestsInstances = []
        self.knightsInstances = []
        self.deadInstances = []
        self.castlesInstances = []
        self.baronsInstances = []
        self.selectedAreaKey = None



    def Setup(self, placeableModel, config):
        self.placeableLocation = util.KeyVal(x=placeableModel.translation[0], y=placeableModel.translation[1], z=placeableModel.translation[2])
        self.startX = self.placeableLocation.x - slayConst.START_LOC_X_TABLE_SHIFT
        self.startY = self.placeableLocation.y - slayConst.START_LOC_Y_TABLE_SHIFT
        self.startZ = self.placeableLocation.z - slayConst.START_LOC_Z_TABLE_SHIFT
        hexagonGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].hexagon)
        hexagonNormalMap = self.GetNormalMap(hexagonGraphicUrl)
        self.tilesInstancesObj = self.PrepInstanceObject(placeableModel, hexagonGraphicUrl, hexagonNormalMap, None, None, slayConst.TILE_SCALE, 1.0, True)
        self.instanceIndex[self.tilesInstancesObj] = {}
        self.enemyActivityHighlightInstancesObj = self.PrepInstanceObject(placeableModel, hexagonGraphicUrl, hexagonNormalMap, hexagonNormalMap, hexagonNormalMap, slayConst.TILE_SCALE * 0.5, 1.0, False)
        self.instanceIndex[self.enemyActivityHighlightInstancesObj] = {}
        hexagonGlowMap = self.GetGlowMap(hexagonGraphicUrl)
        self.tilesBorderInstancesObj = self.PrepInstanceObject(placeableModel, hexagonGraphicUrl, hexagonNormalMap, hexagonGlowMap, hexagonGlowMap, slayConst.TILE_SCALE, 0.5, False)
        self.instanceIndex[self.tilesBorderInstancesObj] = {}
        self.flashHighlightObj = self.PrepInstanceObject(placeableModel, hexagonGraphicUrl, hexagonNormalMap, None, None, slayConst.TILE_SCALE / 2.0, 1.0, True)
        self.instanceIndex[self.flashHighlightObj] = {}
        townOpenGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].townOpen)
        townOpenDiffuseMap = self.GetDiffuseMap(townOpenGraphicUrl)
        townOpenNormalMap = self.GetNormalMap(townOpenGraphicUrl)
        townOpenSpecularMap = self.GetSpecularMap(townOpenGraphicUrl)
        self.townsInstancesObj = self.PrepInstanceObject(placeableModel, townOpenGraphicUrl, townOpenDiffuseMap, townOpenNormalMap, townOpenSpecularMap, slayConst.TOWN_SCALE, 1.0, False)
        self.instanceIndex[self.townsInstancesObj] = {}
        townClosedGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].townClosed)
        townClosedDiffuseMap = self.GetDiffuseMap(townOpenGraphicUrl)
        townClosedNormalMap = self.GetNormalMap(townOpenGraphicUrl)
        townClosedSpecularMap = self.GetSpecularMap(townOpenGraphicUrl)
        self.townsInstancesClosedObj = self.PrepInstanceObject(placeableModel, townClosedGraphicUrl, townClosedDiffuseMap, townClosedNormalMap, townClosedSpecularMap, slayConst.TOWN_SCALE, 1.0, False)
        self.instanceIndex[self.townsInstancesClosedObj] = {}
        castleGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].castle)
        castleDiffuseMap = self.GetDiffuseMap(castleGraphicUrl)
        castleNormalMap = self.GetNormalMap(castleGraphicUrl)
        castleSpecularMap = self.GetSpecularMap(castleGraphicUrl)
        self.castlesInstancesObj = self.PrepInstanceObject(placeableModel, castleGraphicUrl, castleDiffuseMap, castleNormalMap, castleSpecularMap, slayConst.CASTLE_SCALE, 1.0, False)
        self.instanceIndex[self.castlesInstancesObj] = {}
        pineForestGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].pineForest)
        pineForestDiffuseMap = self.GetDiffuseMap(pineForestGraphicUrl)
        pineForestNormalMap = self.GetNormalMap(pineForestGraphicUrl)
        pineForestSpecularMap = self.GetSpecularMap(pineForestGraphicUrl)
        self.pineForestsInstancesObj = self.PrepInstanceObject(placeableModel, pineForestGraphicUrl, pineForestDiffuseMap, pineForestNormalMap, pineForestSpecularMap, slayConst.FOREST_SCALE, 1.0, False)
        self.instanceIndex[self.pineForestsInstancesObj] = {}
        palmForestGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].palmForest)
        palmForestDiffuseMap = self.GetDiffuseMap(palmForestGraphicUrl)
        palmForestNormalMap = self.GetNormalMap(palmForestGraphicUrl)
        palmForestSpecularMap = self.GetSpecularMap(palmForestGraphicUrl)
        self.palmForestsInstancesObj = self.PrepInstanceObject(placeableModel, palmForestGraphicUrl, palmForestDiffuseMap, palmForestNormalMap, palmForestSpecularMap, slayConst.FOREST_SCALE, 1.0, False)
        self.instanceIndex[self.palmForestsInstancesObj] = {}
        peasantGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].peasant)
        peasantDiffuseMap = self.GetDiffuseMap(peasantGraphicUrl)
        peasantNormalMap = self.GetNormalMap(peasantGraphicUrl)
        peasantSpecularMap = self.GetSpecularMap(peasantGraphicUrl)
        self.peasantsInstancesObj = self.PrepInstanceObject(placeableModel, peasantGraphicUrl, peasantDiffuseMap, peasantNormalMap, peasantSpecularMap, slayConst.PEASANT_SCALE, 1.0, False)
        self.instanceIndex[self.peasantsInstancesObj] = {}
        spearmanGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].spearman)
        spearmanDiffuseMap = self.GetDiffuseMap(spearmanGraphicUrl)
        spearmanNormalMap = self.GetNormalMap(spearmanGraphicUrl)
        spearmanSpecularMap = self.GetSpecularMap(spearmanGraphicUrl)
        self.spearmenInstancesObj = self.PrepInstanceObject(placeableModel, spearmanGraphicUrl, spearmanDiffuseMap, spearmanNormalMap, spearmanSpecularMap, slayConst.SPEARMAN_SCALE, 1.0, False)
        self.instanceIndex[self.spearmenInstancesObj] = {}
        knightGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].knight)
        knightDiffuseMap = self.GetDiffuseMap(knightGraphicUrl)
        knightNormalMap = self.GetNormalMap(knightGraphicUrl)
        knightSpecularMap = self.GetSpecularMap(knightGraphicUrl)
        self.knightsInstancesObj = self.PrepInstanceObject(placeableModel, knightGraphicUrl, knightDiffuseMap, knightNormalMap, knightSpecularMap, slayConst.KNIGHT_SCALE, 1.0, False)
        self.instanceIndex[self.knightsInstancesObj] = {}
        baronGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].baron)
        baronDiffuseMap = self.GetDiffuseMap(baronGraphicUrl)
        baronNormalMap = self.GetNormalMap(baronGraphicUrl)
        baronSpecularMap = self.GetSpecularMap(baronGraphicUrl)
        self.baronsInstancesObj = self.PrepInstanceObject(placeableModel, baronGraphicUrl, baronDiffuseMap, baronNormalMap, baronSpecularMap, slayConst.BARON_SCALE, 1.0, False)
        self.instanceIndex[self.baronsInstancesObj] = {}
        deadGraphicUrl = util.GraphicFile(slayConst.slayUnitSetMapping[config.playUnitSet].dead)
        deadDiffuseMap = self.GetDiffuseMap(deadGraphicUrl)
        deadNormalMap = self.GetNormalMap(deadGraphicUrl)
        deadSpecularMap = self.GetSpecularMap(deadGraphicUrl)
        self.deadInstancesObj = self.PrepInstanceObject(placeableModel, deadGraphicUrl, deadDiffuseMap, deadNormalMap, deadSpecularMap, slayConst.RIP_SCALE, 1.0, False)
        self.instanceIndex[self.deadInstancesObj] = {}
        self.lightSourceObj = self.PrepInstanceObject(placeableModel, 'res:/Graphics/Generic/cylinder/cylinder.gr2', 'res:/Texture/Global/white.dds', None, None, 0.015, 1.0, True)
        self.lightVolumeInstances = []
        for key in config.lightPositions:
            self.lightPositions[key] = config.lightPositions[key]

        uthread.new(self.LightPulse)



    def GetDiffuseMap(self, modelPath):
        return modelPath.replace('.gr2', '_D.dds')



    def GetNormalMap(self, modelPath):
        return modelPath.replace('.gr2', '_N.dds')



    def GetSpecularMap(self, modelPath):
        return modelPath.replace('.gr2', '_S.dds')



    def GetGlowMap(self, modelPath):
        return modelPath.replace('.gr2', '_glow.dds')



    def PrepInstanceObject(self, placeable, geometry, diffuseMap, normalMap, specMap, scale, alphaColor, isTile):
        instanceObject = trinity.Tr2InteriorInstancedMesh()
        instanceObject.name = geometry
        instanceObject.mesh = trinity.Tr2Mesh()
        instanceObject.mesh.geometryResPath = geometry
        if isTile:
            slayTile = trinity.Tr2MeshArea()
            slayTile.effect = trinity.Tr2ShaderMaterial()
            slayTile.effect.highLevelShaderName = 'SlayTile'
            param = trinity.TriFloatParameter()
            param.name = 'TileScale'
            param.value = scale
            slayTile.effect.parameters['TileScale'] = param
            tex = trinity.TriTexture2DParameter()
            tex.name = 'DiffuseMap'
            tex.resourcePath = diffuseMap
            slayTile.effect.parameters['DiffuseMap'] = tex
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialDiffuseColor'
            param.value = (1.0,
             1.0,
             1.0,
             alphaColor)
            slayTile.effect.parameters['MaterialDiffuseColor'] = param
            instanceObject.mesh.transparentAreas.append(slayTile)
        else:
            slayUnit = trinity.Tr2MeshArea()
            slayUnit.effect = trinity.Tr2ShaderMaterial()
            slayUnit.effect.highLevelShaderName = 'SlayPiece'
            param = trinity.TriFloatParameter()
            param.name = 'TileScale'
            param.value = scale
            slayUnit.effect.parameters['TileScale'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialDiffuseColor'
            param.value = (1.0,
             1.0,
             1.0,
             alphaColor)
            slayUnit.effect.parameters['MaterialDiffuseColor'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialLibraryID'
            param.value = (11, 0, 0, 0)
            slayUnit.effect.parameters['MaterialSpecularFactors'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialSpecularCurve'
            param.value = (0, 50, 0, 0)
            slayUnit.effect.parameters['MaterialSpecularCurve'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialSpecularFactors'
            param.value = (1, 0, 0, 0)
            slayUnit.effect.parameters['MaterialSpecularFactors'] = param
            param = trinity.TriFloatParameter()
            param.name = 'TileLightScale'
            param.value = 1.5
            slayUnit.effect.parameters['TileLightScale'] = param
            param = trinity.TriFloatParameter()
            param.name = 'ExternalLightScale'
            param.value = 1
            slayUnit.effect.parameters['ExternalLightScale'] = param
            tex = trinity.TriTexture2DParameter()
            tex.name = 'DiffuseMap'
            tex.resourcePath = diffuseMap
            slayUnit.effect.parameters['DiffuseMap'] = tex
            tex = trinity.TriTexture2DParameter()
            tex.name = 'NormalMap'
            tex.resourcePath = normalMap
            slayUnit.effect.parameters['NormalMap'] = tex
            tex = trinity.TriTexture2DParameter()
            tex.name = 'SpecularMap'
            tex.resourcePath = specMap
            slayUnit.effect.parameters['SpecularMap'] = tex
            instanceObject.mesh.opaquePrepassAreas.append(slayUnit)
            normalDepth = trinity.Tr2MeshArea()
            normalDepth.effect = trinity.Tr2ShaderMaterial()
            normalDepth.effect.highLevelShaderName = 'SlayNormalDepth'
            normalDepth.effect.defaultSituation = 'InstanceRotation'
            param = trinity.TriFloatParameter()
            param.name = 'TileScale'
            param.value = scale
            normalDepth.effect.parameters['TileScale'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialLibraryID'
            param.value = (11, 0, 0, 0)
            normalDepth.effect.parameters['MaterialSpecularFactors'] = param
            param = trinity.TriVector4Parameter()
            param.name = 'MaterialSpecularCurve'
            param.value = (0, 50, 0, 0)
            normalDepth.effect.parameters['MaterialSpecularCurve'] = param
            tex = trinity.TriTexture2DParameter()
            tex.name = 'NormalMap'
            tex.resourcePath = normalMap
            normalDepth.effect.parameters['NormalMap'] = tex
            tex = trinity.TriTexture2DParameter()
            tex.name = 'SpecularMap'
            tex.resourcePath = specMap
            normalDepth.effect.parameters['SpecularMap'] = tex
            instanceObject.mesh.depthNormalAreas.append(normalDepth)
        pickable = trinity.Tr2MeshArea()
        pickable.effect = trinity.Tr2ShaderMaterial()
        pickable.effect.highLevelShaderName = 'SlayPicking'
        param = trinity.TriFloatParameter()
        param.name = 'TileScale'
        param.value = scale
        pickable.effect.parameters['TileScale'] = param
        instanceObject.mesh.pickableAreas.append(pickable)
        instanceObject.mesh.BindLowLevelShaders(['Prepass'])
        placeable.attachedObjects.append(instanceObject)
        return instanceObject



    def UpdateLights(self, lightsState):
        self.originalLights = {}
        self.lightsState = lightsState
        for index in self.lightsState:
            self.originalLights[index] = self.lightsState[index]

        if not hasattr(self, 'scene2'):
            graphicClient = sm.GetService('graphicClient')
            self.scene2 = graphicClient.GetScene(session.worldspaceid)
        self.ConfigLights()



    def ConfigLights(self):
        self.lightVolumeInstances = []
        for key in self.lightsState:
            if key not in self.lightInstances or self.lightInstances[key] is None:
                self.AddLight(key)
            pos = self.lightPositions[key]
            if self.lightsState[key] is None:
                self.lightInstances[key].color = slaycommon.ColorEnumToRGB(slayConst.UNUSED_SLOT)
                lightVolume = ((pos[0], pos[1], pos[2]),
                 TABLE_EDGE_ROT[key],
                 slaycommon.ColorEnumToRGB(slayConst.UNUSED_SLOT),
                 (0, 0, 0))
            else:
                self.lightInstances[key].color = self.lightsState[key]
                lightVolume = ((pos[0], pos[1], pos[2]),
                 TABLE_EDGE_ROT[key],
                 self.lightsState[key],
                 (0, 0, 0))
            self.lightVolumeInstances.append(lightVolume)

        self.lightSourceObj.SetInstanceData(self.lightVolumeInstances)



    def AddLight(self, slotIndex):
        pos = self.lightPositions[slotIndex]
        light = trinity.Tr2InteriorLightSource()
        light.name = 'slaySlotLight%d' % slotIndex
        light.radius = 5.0
        light.falloff = 2.5
        light.coneAlphaOuter = 180
        light.coneAlphaInner = 180
        light.primaryLighting = True
        light.secondaryLighting = False
        light.isStatic = True
        light.position = (self.placeableLocation.x + pos[0], self.placeableLocation.y + pos[1], self.placeableLocation.z + pos[2])
        self.lightInstances[slotIndex] = light
        self.scene2.AddLight(light)
        self.scene2.RebuildSceneData()



    def SetSlotHighlight(self, index):
        if index is None:
            return 
        for key in self.lightsState:
            if self.originalLights[index] is None:
                continue
            if index == key:
                magnify = 1.5
                r = self.originalLights[index][0] * magnify if self.originalLights[index][0] * magnify <= 1.0 else 1.0
                g = self.originalLights[index][1] * magnify if self.originalLights[index][1] * magnify <= 1.0 else 1.0
                b = self.originalLights[index][2] * magnify if self.originalLights[index][2] * magnify <= 1.0 else 1.0
                self.lightsState[key] = (r, g, b)
                lightVolume = self.lightVolumeInstances[(index - 1)]
                lightVolume = (lightVolume[0],
                 lightVolume[1],
                 (0.0, 0.0, 0.0),
                 lightVolume[3])
                self.lightVolumeInstances[index - 1] = lightVolume
                self.lightSourceObj.SetInstanceData(self.lightVolumeInstances)
            else:
                self.lightsState[key] = self.originalLights[key]

        self.ConfigLights()



    def LightPulse(self):
        lightIntensity = 0.0
        goingUp = True
        while not self.terminated:
            if goingUp:
                lightIntensity += 0.01
            else:
                lightIntensity -= 0.01
            if lightIntensity > 0.5:
                lightIntensity = 0.5
                goingUp = False
            elif lightIntensity < 0.0:
                lightIntensity = 0.0
                goingUp = True
            lightVolume = None
            for index in self.lightInstances:
                if self.lightsState[index] is None:
                    lightVolume = self.lightVolumeInstances[(index - 1)]
                    lightVolume = (lightVolume[0],
                     lightVolume[1],
                     (lightIntensity * 2, lightIntensity * 2, lightIntensity * 2),
                     lightVolume[3])
                    self.lightVolumeInstances[index - 1] = lightVolume
                    light = self.lightInstances[index]
                    newColor = (lightIntensity, lightIntensity, lightIntensity)
                    light.color = newColor

            if lightVolume is not None:
                self.lightSourceObj.SetInstanceData(self.lightVolumeInstances)
            blue.pyos.synchro.Sleep(20)




    def RefreshMouseMoveTile(self, tile):
        if tile:
            for tileIndex in self.instanceIndex[self.tilesInstancesObj]:
                if tileIndex < len(self.tilesInstances):
                    if self.instanceIndex[self.tilesInstancesObj][tileIndex].tileID == tile.tileID:
                        instanceTuple = self.tilesInstances[tileIndex]
                        instanceTuple = (instanceTuple[0],
                         instanceTuple[1],
                         self.CalcHighlightColor(tile.color),
                         instanceTuple[3])
                        self.tilesInstances[tileIndex] = instanceTuple
                    else:
                        theTile = self.instanceIndex[self.tilesInstancesObj][tileIndex]
                        instanceTuple = self.tilesInstances[tileIndex]
                        if theTile.tileID in self.possibleMoveTiles:
                            instanceTuple = (instanceTuple[0],
                             instanceTuple[1],
                             self.CalcPossibleMoveColor(theTile.color),
                             instanceTuple[3])
                        elif theTile.areaKey == self.selectedAreaKey:
                            instanceTuple = (instanceTuple[0],
                             instanceTuple[1],
                             self.CalcSelectedAreaColor(theTile.color),
                             instanceTuple[3])
                        else:
                            instanceTuple = (instanceTuple[0],
                             instanceTuple[1],
                             self.CalcColor(theTile.color),
                             instanceTuple[3])
                        self.tilesInstances[tileIndex] = instanceTuple

        self.tilesInstancesObj.SetInstanceData(self.tilesInstances)



    def SetPossibleMovesHighlight(self, possibleMoveTiles):
        if len(possibleMoveTiles) == 0:
            self.possibleMovesTuples = []
            for tileIndex in self.instanceIndex[self.tilesInstancesObj]:
                if tileIndex < len(self.tilesInstances):
                    selTile = self.instanceIndex[self.tilesInstancesObj][tileIndex]
                    instanceTuple = self.tilesInstances[tileIndex]
                    if selTile.areaKey == self.selectedAreaKey:
                        instanceTuple = (instanceTuple[0],
                         instanceTuple[1],
                         self.CalcSelectedAreaColor(selTile.color),
                         instanceTuple[3])
                    else:
                        instanceTuple = (instanceTuple[0],
                         instanceTuple[1],
                         self.CalcColor(selTile.color),
                         instanceTuple[3])
                    self.tilesInstances[tileIndex] = instanceTuple

        self.possibleMoveTiles = possibleMoveTiles
        for tileID in possibleMoveTiles:
            for tileIndex in self.instanceIndex[self.tilesInstancesObj]:
                if tileIndex < len(self.tilesInstances):
                    if self.instanceIndex[self.tilesInstancesObj][tileIndex].tileID == tileID:
                        instanceTuple = self.tilesInstances[tileIndex]
                        instanceTuple = (instanceTuple[0],
                         instanceTuple[1],
                         self.CalcPossibleMoveColor(self.instanceIndex[self.tilesInstancesObj][tileIndex].color),
                         instanceTuple[3])
                        self.tilesInstances[tileIndex] = instanceTuple
                        self.possibleMovesTuples.append(instanceTuple)


        self.tilesInstancesObj.SetInstanceData(self.tilesInstances)



    def SetSelectedArea(self, areaKey):
        self.selectedAreaKey = areaKey
        for tileIndex in self.instanceIndex[self.tilesInstancesObj]:
            if tileIndex < len(self.tilesInstances):
                selTile = self.instanceIndex[self.tilesInstancesObj][tileIndex]
                instanceTuple = self.tilesInstances[tileIndex]
                if selTile.areaKey == areaKey:
                    instanceTuple = (instanceTuple[0],
                     instanceTuple[1],
                     self.CalcSelectedAreaColor(selTile.color),
                     instanceTuple[3])
                    self.tilesInstances[tileIndex] = instanceTuple
                elif selTile.tileID not in self.possibleMoveTiles:
                    instanceTuple = (instanceTuple[0],
                     instanceTuple[1],
                     self.CalcColor(selTile.color),
                     instanceTuple[3])
                    self.tilesInstances[tileIndex] = instanceTuple

        self.tilesInstancesObj.SetInstanceData(self.tilesInstances)



    def IsPickingInGame(self, x, y):
        self.pickResult = None
        graphicClient = sm.GetService('graphicClient')
        scene2 = graphicClient.GetScene(session.worldspaceid)
        if scene2:
            (projection, view, viewport,) = uix.GetFullscreenProjectionViewAndViewport()
            cam = sm.GetService('cameraClient').GetActiveCamera()
            pick = scene2.PickObjectAndArea(x, y, cam.projectionMatrix, cam.viewMatrix, viewport)
            if pick and len(pick) > 0:
                if pick[0] in self.instanceIndex:
                    index = pick[1][1]
                    if index in self.instanceIndex[pick[0]]:
                        self.pickResult = (pick[0], pick[1][1])
                        return True
        return False



    def Flash(self):
        data = slaycommon.SlayData()
        step = 0
        while True:
            blue.pyos.synchro.Sleep(500)
            if self.flashing:
                tableData = data.GetCircularPattern(step)
                step += 1
                if step > 1:
                    step = 0
                self.Refresh(tableData, saveTableData=False)
            else:
                if self.clearTiles:
                    self.instanceIndex[self.tilesInstancesObj] = {}
                    self.tilesInstancesObj.SetInstanceData([])
                return 




    def StartFlashing(self):
        if self.flashing:
            return 
        self.flashing = True
        uthread.new(self.Flash)



    def StopFlashing(self, clearTiles = True):
        self.clearTiles = clearTiles
        self.flashing = False



    def GetPickedEntity(self):
        if self.pickResult is None:
            return 
        else:
            obj = self.pickResult[0]
            objIndex = self.pickResult[1]
            if obj in self.instanceIndex and objIndex in self.instanceIndex[obj]:
                return self.instanceIndex[obj][objIndex]
            return 



    def GetPickedEntityIndex(self):
        if self.pickResult is None:
            return 
        else:
            return self.pickResult[1]



    def HighlightSelected(self, x, y):
        picking = self.IsPickingInGame(x, y)
        if picking:
            tile = self.GetPickedEntity()
            if tile is not None:
                self.RefreshMouseMoveTile(tile)



    def CalcHighlightColor(self, colorEnum):
        normalColor = self.CalcColor(colorEnum)
        r = min(normalColor[0] + 0.7, 1.0)
        g = min(normalColor[1] + 0.7, 1.0)
        b = min(normalColor[2] + 0.7, 1.0)
        return (r, g, b)



    def CalcPossibleMoveColor(self, colorEnum):
        normalColor = self.CalcColor(colorEnum)
        r = min(normalColor[0] + 0.5, 1.0)
        g = min(normalColor[1] + 0.5, 1.0)
        b = min(normalColor[2] + 0.5, 1.0)
        return (r, g, b)



    def CalcSelectedAreaColor(self, colorEnum):
        normalColor = self.CalcColor(colorEnum)
        r = min(normalColor[0] + 0.2, 1.0)
        g = min(normalColor[1] + 0.2, 1.0)
        b = min(normalColor[2] + 0.2, 1.0)
        return (r, g, b)



    def CalcColor(self, colorEnum):
        if colorEnum in slaycommon.ColorEnum():
            col = slaycommon.ColorEnum()[colorEnum]
            return (col[0], col[1], col[2])
        else:
            return (1.0, 0.0, 0.0)



    def CalcColorUnderlit(self, color):
        color = self.CalcColor(color)
        factor = 0.8
        r = color[0] * factor if color[0] * factor <= 1.0 else 1.0
        g = color[1] * factor if color[1] * factor <= 1.0 else 1.0
        b = color[2] * factor if color[2] * factor <= 1.0 else 1.0
        return (r, g, b)



    def FlashUpgrades(self, upgrades):
        for i in xrange(0, 10):
            if i % 2 == 0:
                self.instanceIndex[self.flashHighlightObj] = {}
                self.flashHighlightObj.SetInstanceData([])
                self.flashHighlightInstances = []
            else:
                for tile in upgrades:
                    posY = tile.y * slayConst.MAP_Y_LOCATION_SCALE
                    posX = tile.x * slayConst.MAP_X_LOCATION_SCALE
                    if tile.x % 2 != 0:
                        x = START_LOC_X + posY + slayConst.HEXAGONMAP_ODDROW_OFFSET
                    else:
                        x = START_LOC_X + posY
                    y = START_LOC_Y
                    z = START_LOC_Z + posX
                    pos = util.KeyVal(x=x, y=y + slayConst.TILE_SLIGHT_HOVER_OFFSET, z=z)
                    color = self.CalcColor(slayConst.COLOR_7)
                    flashPoint = ((pos.x, pos.y, pos.z),
                     HEX_ROT,
                     color,
                     (1, 0, 0))
                    self.flashHighlightInstances.append(flashPoint)
                    self.instanceIndex[self.flashHighlightObj][len(self.flashHighlightInstances) - 1] = tile

                if len(self.flashHighlightInstances) > 0:
                    self.flashHighlightObj.SetInstanceData(self.flashHighlightInstances)
                else:
                    self.instanceIndex[self.flashHighlightObj] = {}
                    self.flashHighlightObj.SetInstanceData([])
            blue.pyos.synchro.Sleep(500)

        self.instanceIndex[self.flashHighlightObj] = {}
        self.flashHighlightObj.SetInstanceData([])



    def SetEnemyActivitiesHighlightings(self, enemyActivitiesHighlighting):
        if enemyActivitiesHighlighting is None:
            return 
        self.highlightsInstance = []
        for area in enemyActivitiesHighlighting.moves:
            for tile in area:
                posY = tile.y * slayConst.MAP_Y_LOCATION_SCALE
                posX = tile.x * slayConst.MAP_X_LOCATION_SCALE
                if tile.x % 2 != 0:
                    x = START_LOC_X + posY + slayConst.HEXAGONMAP_ODDROW_OFFSET
                else:
                    x = START_LOC_X + posY
                y = START_LOC_Y + HOVER_ELEVATE_Y
                z = START_LOC_Z + posX
                pos = util.KeyVal(x=x, y=y + TILEOFFSET + slayConst.TILE_SLIGHT_HOVER_OFFSET, z=z)
                color = (0.8, 0.8, 0.8)
                highlight = ((pos.x, pos.y, pos.z),
                 HEX_ROT,
                 color,
                 (1, 0, 0))
                self.highlightsInstance.append(highlight)


        uthread.new(self.FlashUpgrades, enemyActivitiesHighlighting.upgrades)
        self.enemyActivityHighlightInstancesObj.SetInstanceData([])
        if len(self.highlightsInstance):
            self.enemyActivityHighlightInstancesObj.SetInstanceData(self.highlightsInstance)



    def Refresh(self, tableData, selectedAreaKey = None, economics = None, currPlayerID = None, enemyActivitiesHighlighting = None, saveTableData = True):
        if currPlayerID != session.charid:
            selectedAreaKey = None
        if tableData is None:
            return 
        if saveTableData:
            self.storedTableData = tableData
        self.selectedAreaKey = selectedAreaKey
        self.ResetCommonInstances()
        unitIDs = [slayConst.OCCUPY_SPEARMAN,
         slayConst.OCCUPY_PEASANT,
         slayConst.OCCUPY_TOWN,
         slayConst.OCCUPY_PALMFOREST,
         slayConst.OCCUPY_PINEFOREST,
         slayConst.OCCUPY_KNIGHT,
         slayConst.OCCUPY_DEAD,
         slayConst.OCCUPY_CASTLE,
         slayConst.OCCUPY_BARON]
        unitIDPossiblyActive = [slayConst.OCCUPY_SPEARMAN,
         slayConst.OCCUPY_PEASANT,
         slayConst.OCCUPY_TOWN,
         slayConst.OCCUPY_KNIGHT,
         slayConst.OCCUPY_BARON]
        found = False
        areaSize = 0
        for key in tableData:
            if found:
                break
            tempTile = slaycommon.SlayTile()
            tempTile.FromRaw(tableData[key])
            if tempTile.areaKey == selectedAreaKey:
                areaSize += 1
            if areaSize > 1:
                found = True

        if not found:
            selectedAreaKey = None
        if self.possibleMovesTuples is not None:
            self.tilesInstances.extend(self.possibleMovesTuples)
        highlightScale = util.KeyVal(x=slayConst.HIGHLIGH_TILESCALE, y=slayConst.HIGHLIGHT_Y_SCALE, z=slayConst.HIGHLIGH_TILESCALE)
        for key in tableData:
            rawTile = tableData[key]
            if rawTile is None:
                continue
            tile = slaycommon.SlayTile()
            tile.FromRaw(rawTile)
            tileKey = '%s.%s' % (tile.x, tile.y)
            posY = tile.y * slayConst.MAP_Y_LOCATION_SCALE
            posX = tile.x * slayConst.MAP_X_LOCATION_SCALE
            if tile.x % 2 != 0:
                x = START_LOC_X + posY + slayConst.HEXAGONMAP_ODDROW_OFFSET
            else:
                x = START_LOC_X + posY
            y = START_LOC_Y
            z = START_LOC_Z + posX
            active = 0
            moneyLeft = False
            if currPlayerID == session.charid and self.controller.joined == True:
                if tile.active == True and tile.occupier.unitID in unitIDPossiblyActive:
                    active = 1
                if tile.areaKey in economics and economics[tile.areaKey].saved >= 10:
                    moneyLeft = True
                if tile.owner != session.charid:
                    moneyLeft = False
                    active = 0
            if tile.areaKey == selectedAreaKey:
                color = self.CalcSelectedAreaColor(tile.color)
                if tile.occupier.unitID == slayConst.OCCUPY_TOWN:
                    pos = util.KeyVal(x=x, y=y + TILEOFFSET, z=z)
                    unit = ((pos.x, pos.y, pos.z),
                     HEX_ROT,
                     color,
                     (0, 0, 0))
                else:
                    pos = util.KeyVal(x=x, y=y + TILEOFFSET, z=z)
                    unit = ((pos.x, pos.y, pos.z),
                     HEX_ROT,
                     color,
                     (0, 0, 0))
                pos = util.KeyVal(x=x, y=y + BORDER_TILEOFFSET, z=z)
            else:
                color = self.CalcColor(tile.color)
                if tile.occupier.unitID == slayConst.OCCUPY_TOWN:
                    pos = util.KeyVal(x=x, y=y + TILEOFFSET, z=z)
                    unit = ((pos.x, pos.y, pos.z),
                     HEX_ROT,
                     color,
                     (0, 0, 0))
                else:
                    pos = util.KeyVal(x=x, y=y + TILEOFFSET, z=z)
                    unit = ((pos.x, pos.y, pos.z),
                     HEX_ROT,
                     color,
                     (0, 0, 0))
            add = tile.tileID not in self.possibleMoveTiles
            if add:
                self.tilesInstances.append(unit)
                self.instanceIndex[self.tilesInstancesObj][len(self.tilesInstances) - 1] = tile
            unitID = tile.occupier.unitID
            color = self.CalcColorUnderlit(tile.color)
            if unitID == slayConst.OCCUPY_SPEARMAN:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (active, 0, 0))
                self.spearmenInstances.append(unit)
                self.instanceIndex[self.spearmenInstancesObj][len(self.spearmenInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_PEASANT:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (active, 0, 0))
                self.peasantsInstances.append(unit)
                self.instanceIndex[self.peasantsInstancesObj][len(self.peasantsInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_TOWN:
                pos = util.KeyVal(x=x, y=y + slayConst.TOWN_Y_OFFSET, z=z)
                if moneyLeft:
                    unit = ((pos.x, pos.y, pos.z),
                     UNIT_ROT,
                     color,
                     (0, 0, 0))
                    self.townsInstances.append(unit)
                    self.instanceIndex[self.townsInstancesObj][len(self.townsInstances) - 1] = tile
                else:
                    unit = ((pos.x, pos.y, pos.z),
                     UNIT_ROT,
                     color,
                     (0, 0, 0))
                    self.townsInstancesClosed.append(unit)
                    self.instanceIndex[self.townsInstancesClosedObj][len(self.townsInstancesClosed) - 1] = tile
            elif unitID == slayConst.OCCUPY_PALMFOREST:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (0, 0, 0))
                self.palmForestsInstances.append(unit)
                self.instanceIndex[self.palmForestsInstancesObj][len(self.palmForestsInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_PINEFOREST:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (0, 0, 0))
                self.pineForestsInstances.append(unit)
                self.instanceIndex[self.pineForestsInstancesObj][len(self.pineForestsInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_KNIGHT:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (active, 0, 0))
                self.knightsInstances.append(unit)
                self.instanceIndex[self.knightsInstancesObj][len(self.knightsInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_DEAD:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (0, 0, 0))
                self.deadInstances.append(unit)
                self.instanceIndex[self.deadInstancesObj][len(self.deadInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_CASTLE:
                pos = util.KeyVal(x=x, y=y + slayConst.UNITS_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (0, 0, 0))
                self.castlesInstances.append(unit)
                self.instanceIndex[self.castlesInstancesObj][len(self.castlesInstances) - 1] = tile
            elif unitID == slayConst.OCCUPY_BARON:
                pos = util.KeyVal(x=x, y=y + slayConst.BARON_Y_OFFSET, z=z)
                unit = ((pos.x, pos.y, pos.z),
                 UNIT_ROT,
                 color,
                 (active, 0, 0))
                self.baronsInstances.append(unit)
                self.instanceIndex[self.baronsInstancesObj][len(self.baronsInstances) - 1] = tile

        self.tilesBorderInstancesObj.SetInstanceData(self.tilesBorderInstances)
        self.tilesInstancesObj.SetInstanceData(self.tilesInstances)
        self.townsInstancesObj.SetInstanceData(self.townsInstances)
        self.townsInstancesClosedObj.SetInstanceData(self.townsInstancesClosed)
        self.spearmenInstancesObj.SetInstanceData(self.spearmenInstances)
        self.pineForestsInstancesObj.SetInstanceData(self.pineForestsInstances)
        self.peasantsInstancesObj.SetInstanceData(self.peasantsInstances)
        self.palmForestsInstancesObj.SetInstanceData(self.palmForestsInstances)
        self.knightsInstancesObj.SetInstanceData(self.knightsInstances)
        self.deadInstancesObj.SetInstanceData(self.deadInstances)
        self.castlesInstancesObj.SetInstanceData(self.castlesInstances)
        self.baronsInstancesObj.SetInstanceData(self.baronsInstances)
        self.SetEnemyActivitiesHighlightings(enemyActivitiesHighlighting)



    def ClearTable(self):
        if self.flashing:
            self.StopFlashing()
        self.storedTableData = None
        self.playersInfo = {}
        self.ownerColors = {}
        self.possibleMoveTiles = []
        self.possibleMovesTuples = []
        self.flashHighlightInstances = []
        self.highlightsInstance = []
        self.ResetCommonInstances()
        for obj in self.instanceIndex:
            self.instanceIndex[obj] = {}

        self.tilesInstancesObj.SetInstanceData([])
        self.tilesBorderInstancesObj.SetInstanceData([])
        self.townsInstancesObj.SetInstanceData([])
        self.townsInstancesClosedObj.SetInstanceData([])
        self.spearmenInstancesObj.SetInstanceData([])
        self.pineForestsInstancesObj.SetInstanceData([])
        self.peasantsInstancesObj.SetInstanceData([])
        self.palmForestsInstancesObj.SetInstanceData([])
        self.knightsInstancesObj.SetInstanceData([])
        self.deadInstancesObj.SetInstanceData([])
        self.castlesInstancesObj.SetInstanceData([])
        self.baronsInstancesObj.SetInstanceData([])
        self.flashHighlightObj.SetInstanceData([])
        self.enemyActivityHighlightInstancesObj.SetInstanceData([])



    def ResetCommonInstances(self):
        self.tilesInstances = []
        self.instanceIndex[self.tilesInstancesObj] = {}
        self.townsInstances = []
        self.instanceIndex[self.townsInstancesObj] = {}
        self.townsInstancesClosed = []
        self.instanceIndex[self.townsInstancesClosedObj] = {}
        self.tilesBorderInstances = []
        self.instanceIndex[self.tilesBorderInstancesObj] = {}
        self.spearmenInstances = []
        self.instanceIndex[self.spearmenInstancesObj] = {}
        self.pineForestsInstances = []
        self.instanceIndex[self.pineForestsInstancesObj] = {}
        self.peasantsInstances = []
        self.instanceIndex[self.peasantsInstancesObj] = {}
        self.palmForestsInstances = []
        self.instanceIndex[self.palmForestsInstancesObj] = {}
        self.knightsInstances = []
        self.instanceIndex[self.knightsInstancesObj] = {}
        self.deadInstances = []
        self.instanceIndex[self.deadInstancesObj] = {}
        self.castlesInstances = []
        self.instanceIndex[self.castlesInstancesObj] = {}
        self.baronsInstances = []
        self.instanceIndex[self.baronsInstancesObj] = {}




