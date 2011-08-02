import blue
import bluepy
import geo2
import trinity
import uthread
import prepassConversion
ENLIGHTEN_BUILD_WAIT_TIME = 200
INTERIOR_RES_PATH = 'res:/interiorCache/'
INTERIOR_REFMAP_PATH = 'res:/Graphics/Interior/StaticEnvmaps/'

class Tr2InteriorScene(bluepy.WrapBlueClass('trinity.Tr2InteriorScene')):
    __guid__ = 'graphicWrappers.Tr2InteriorScene'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorScene(triObject)
        triObject.objects = {}
        triObject.systemParentName = {}
        triObject.systemNames = {}
        triObject.id = ''
        triObject.cellData = {}
        return triObject



    def SetID(self, id):
        self.id = id



    def _SortCells(self):
        listToSort = list(self.cells)
        listToSort.sort(lambda x, y: x.name < y.name)
        self.cells.removeAt(-1)
        self.cells.extend(listToSort)



    def _SortSystems(self, cell):
        listToSort = list(cell.systems)
        listToSort.sort(lambda x, y: x.systemID < y.systemID)
        cell.systems.removeAt(-1)
        cell.systems.extend(listToSort)
        for (i, system,) in enumerate(cell.systems):
            system.SetSystemInCellIdx(i)




    def _GetCell(self, cellName):
        cellName = str(cellName)
        for cell in self.cells:
            if cell.name == cellName:
                return cell

        cell = trinity.Tr2InteriorCell()
        cell.name = cellName
        cell.shProbeResPath = INTERIOR_RES_PATH + str(self.id) + '_' + cellName + '.shp'
        cell.reflectionMapPath = INTERIOR_REFMAP_PATH + 'Cube_%s_%s.dds' % (self.id, cellName)
        self.cells.append(cell)
        self._SortCells()
        self._LoadUVData(cellName)
        return cell



    def _RemoveCellIfEmpty(self, cell):
        if cell in self.cells:
            if not cell.systems and not cell.probeVolumes:
                self.cells.remove(cell)



    def _RemoveSystemIfEmpty(self, system):
        cellName = self.systemParentName.get(system, None)
        if cellName:
            cell = self._GetCell(cellName)
            if not system.statics:
                cell.RemoveSystem(system)
                self._RemoveCellIfEmpty(cell)



    def _GetSystem(self, cell, systemName):
        systemNames = self.systemNames.get(cell.name, None)
        if systemNames is None:
            systemNames = []
            self.systemNames[cell.name] = systemNames
        if systemName not in systemNames:
            systemNames.append(systemName)
        systemNum = systemNames.index(systemName)
        while len(cell.systems) < systemNum + 1:
            newSystem = trinity.Tr2InteriorEnlightenSystem()
            newSystem.bounceScale = 1.0
            newSystem.systemID = int(systemName) + int(cell.name) * 100000
            newSystem.radSystemPath = INTERIOR_RES_PATH + str(self.id) + '_' + cell.name + '_' + str(systemName) + '.rad'
            cell.systems.append(newSystem)
            newSystem.SetSystemInCellIdx(cell.systems.index(newSystem))
            self._SortSystems(cell)
            self.systemParentName[newSystem] = cell.name

        return cell.systems[systemNum]



    def AddStatic(self, staticObj, cellName = '', systemName = 0, id = None):
        prepassConversion.AddPrepassAreasToStatic(staticObj)
        self.RemoveStatic(staticObj)
        cell = self._GetCell(cellName)
        system = self._GetSystem(cell, systemName)
        system.AddStatic(staticObj)
        self.objects[staticObj] = system
        if id is None:
            id = staticObj.objectID
        uvData = self.cellData[cellName].get(id, None)
        if uvData:
            staticObj.SetInstanceData(*uvData)



    def RemoveStatic(self, staticObj):
        system = self.objects.get(staticObj, None)
        if system:
            system.RemoveStatic(staticObj)
            self.objects[staticObj] = None
            self._RemoveSystemIfEmpty(system)



    def AddLight(self, lightObj):
        self.RemoveLight(lightObj)
        self.AddLightSource(lightObj)
        try:
            import wx
            triPanel = wx.FindWindowByName('TrinityPanel')
            if triPanel:
                triPanel.PopulateLights()
                triPanel.PopulateLights()
        except:
            pass



    def RemoveLight(self, lightObj):
        if lightObj in self.lights:
            self.RemoveLightSource(lightObj)
            try:
                import wx
                triPanel = wx.FindWindowByName('TrinityPanel')
                if triPanel:
                    triPanel.PopulateLights()
                    triPanel.PopulateLights()
            except:
                pass



    def AddPhysicalPortal(self, portalObj):
        if portalObj in self.portals:
            self.RemovePhysicalPortal(portalObj)
        self.portals.append(portalObj)



    def RemovePhysicalPortal(self, portalObj):
        self.portals.remove(portalObj)



    def AddOccluder(self, occluderObj, cellName = ''):
        cell = self._GetCell(cellName)
        if occluderObj in cell.occluders:
            self.RemoveOccluder(occluderObj)
        cell.occluders.append(occluderObj)



    def RemoveOccluder(self, occluderObj):
        cell = self._GetCell(occluderObj.cellName)
        if occluderObj in cell.occluders:
            cell.occluders.remove(occluderObj)



    def AddProbeVolume(self, probeObj, cellName = ''):
        cell = self._GetCell(cellName)
        if probeObj in cell.probeVolumes:
            self.RemoveProbeVolume(probeObj)
        cell.probeVolumes.append(probeObj)



    def RemoveProbeVolume(self, probeObj):
        cell = self._GetCell(probeObj.cellName)
        if probeObj in cell.probeVolumes:
            cell.probeVolumes.remove(probeObj)



    def AddAvatarToScene(self, avatar):
        self.AddDynamicToScene(avatar)



    def RemoveAvatarFromScene(self, avatar):
        self.RemoveDynamicFromScene(avatar)



    def AddDynamicToScene(self, obj):
        prepassConversion.AddPrepassAreasToDynamic(obj)
        if type(obj) is trinity.Tr2IntSkinnedObject:
            obj.visualModel.ResetAnimationBindings()
        self.AddDynamic(obj)
        return obj



    def RemoveDynamicFromScene(self, obj):
        if obj in self.dynamics:
            self.RemoveDynamic(obj)



    def AddCurveSetToScene(self, curveSet):
        self.curveSets.append(curveSet)



    def RemoveCurveSetFromScene(self, curveSet):
        self.curveSets.remove(curveSet)



    def Refresh(self):
        pass



    def BuildEnlightenScene(self):
        trinity.WaitForResourceLoads()
        import CCP_P4 as p4
        for cell in self.cells:
            p4.PrepareFileForSave(blue.rot.PathToFilename(cell.shProbeResPath))
            for system in cell.systems:
                p4.PrepareFileForSave(blue.rot.PathToFilename(system.radSystemPath))

            cell.RebuildInternalData()
            lightVolumeRes = [ int(v) + 1 for v in geo2.Vec3Subtract(cell.maxBounds, cell.minBounds) ]
            cell.BuildLightVolume(*lightVolumeRes)
            uvFileName = blue.rot.PathToFilename('res:/interiorCache/' + str(self.id) + '_' + str(cell.name) + '.uv')
            p4.PrepareFileForSave(blue.rot.PathToFilename(uvFileName))

        import app.Interior.EnlightenBuildProgressDialog as progress
        dlg = progress.EnlightenBuildDialog()
        if dlg.BuildEnlighten(self):
            self.SaveEnlighten()
        p4.AddFilesToP4()
        for cell in self.cells:
            self._SaveUVData(cell, cell.name)




    def _SaveUVData(self, cell, cellName):
        self.cellData[cellName] = {}
        cellData = self.cellData[cellName]
        for system in cell.systems:
            for static in system.statics:
                cellData[static.worldSpaceObject().GetID()] = (static.uvLinearTransform, static.uvTranslation, static.instanceInSystemIdx)


        marshalData = blue.marshal.Save(cellData)
        import CCP_P4 as p4
        import os
        fileName = blue.rot.PathToFilename(INTERIOR_RES_PATH + str(self.id) + '_' + str(cellName) + '.uv')
        p4.PrepareFileForSave(fileName)
        if not os.path.exists(blue.rot.PathToFilename(INTERIOR_RES_PATH)):
            os.makedirs(blue.rot.PathToFilename(INTERIOR_RES_PATH))
        file = open(fileName, 'wb')
        file.write(marshalData)
        file.close()
        p4.AddFilesToP4()



    def _LoadUVData(self, cellName):
        file = blue.ResFile()
        filePath = INTERIOR_RES_PATH + str(self.id) + '_' + str(cellName) + '.uv'
        if file.FileExists(filePath):
            file.open(filePath)
            marshalData = file.read()
            file.close()
            self.cellData[cellName] = blue.marshal.Load(marshalData)
        else:
            self.cellData[cellName] = {}



    def RemoveSkyboxTexture(self):
        self.backgroundEffect = None
        self.backgroundCubemapPath = ''



    def SetSkyboxTexture(self, texturePath):
        self.backgroundEffect = trinity.Tr2Effect()
        texture = trinity.TriTextureCubeParameter()
        texture.name = 'EnvMap1'
        texture.resourcePath = texturePath
        self.backgroundEffect.resources.append(texture)
        self.backgroundEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Static/EnvironmentCubemap.fx'
        self.backgroundCubemapPath = str(texturePath)



    def GetBoundingBox(self):
        minBB = (99999999.9, 99999999.9, 99999999.9)
        maxBB = (-99999999.9, -99999999.9, -99999999.9)
        for cell in self.cells:
            minBB = geo2.Vec3Minimize(minBB, cell.minBounds)
            maxBB = geo2.Vec3Maximize(maxBB, cell.maxBounds)

        return (minBB, maxBB)




