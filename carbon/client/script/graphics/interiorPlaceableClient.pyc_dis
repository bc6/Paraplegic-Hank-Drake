#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/interiorPlaceableClient.py
import cef
import collections
import geo2
import service
import trinity
import util
import metaMaterials
import uthread
import blue

class InteriorPlaceableClientComponent:
    __guid__ = 'component.InteriorPlaceableClientComponent'


class InteriorPlaceableClient(service.Service):
    __guid__ = 'svc.interiorPlaceableClient'
    __componentTypes__ = [cef.InteriorPlaceableComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.placeableEntities = set()

    def CreateComponent(self, name, state):
        component = InteriorPlaceableClientComponent()
        if 'graphicID' in state:
            component.graphicID = state['graphicID']
        else:
            self.LogError('interiorPlaceable Component requires graphicID in its state')
            component.graphicID = 0
        if 'overrideMetaMaterialPath' in state:
            component.overrideMetaMaterialPath = state['overrideMetaMaterialPath']
        else:
            component.overrideMetaMaterialPath = None
        if 'minSpecOverideMetaMaterialPath' in state:
            component.minSpecOverideMetaMaterialPath = state['minSpecOverideMetaMaterialPath']
        else:
            component.minSpecOverideMetaMaterialPath = None
        if 'probeOffsetX' in state and 'probeOffsetY' in state and 'probeOffsetZ' in state:
            component.probeOffset = (float(state['probeOffsetX']), float(state['probeOffsetY']), float(state['probeOffsetZ']))
        else:
            component.probeOffset = (0, 0, 0)
        component.depthOffset = float(state.get('depthOffset', 0))
        component.scale = util.UnpackStringToTuple(state['scale'])
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['graphicID'] = component.graphicID
        if component.renderObject is not None:
            report['Position'] = component.renderObject.GetPosition()
            report['Rotation'] = component.renderObject.GetRotationYawPitchRoll()
        report['minSpecOverideMetaMaterialPath'] = component.minSpecOverideMetaMaterialPath
        report['overrideMetaMaterialPath'] = component.overrideMetaMaterialPath
        return report

    def WaitForGeometry(self, renderObject):
        if renderObject is None or renderObject.placeableRes is None:
            return
        visualModel = renderObject.placeableRes.visualModel
        if visualModel is None:
            return
        for mesh in visualModel.meshes:
            geometry = mesh.geometry
            if geometry is None:
                continue
            while geometry.isLoading and not geometry.isPrepared:
                blue.synchro.Yield()

    def PrepareComponent(self, sceneID, entityID, component):
        modelFile = self.graphicClient.GetModelFilePath(component.graphicID)
        renderObject = trinity.Tr2InteriorPlaceable()
        if modelFile is not None:
            renderObject.placeableResPath = modelFile
        self.WaitForGeometry(renderObject)
        if renderObject.placeableRes is None:
            self.LogWarn('!!! WARNING !!! Asset (', modelFile, ') is missing !!! WARNING !!!')
            renderObject.placeableResPath = const.BAD_ASSET_PATH_AND_FILE
            self.WaitForGeometry(renderObject)
            if renderObject.placeableRes is None:
                self.LogError('!!! ERROR !!! The InteriorPlaceable bad asset is missing ', const.BAD_ASSET_PATH_AND_FILE, '!!! ERROR !!!')
        renderObject.isStatic = True
        renderObject.probeOffset = component.probeOffset
        renderObject.depthOffset = component.depthOffset
        graphicName = self.graphicClient.GetGraphicName(component.graphicID) or 'BadAsset'
        renderObject.name = str(graphicName) + ': ' + str(entityID)
        component.renderObject = renderObject
        self.ApplyMaterials(entityID, component)

    def ApplyMaterials(self, entity, component):
        if component.renderObject is None:
            return
        placeableRes = component.renderObject.placeableRes
        if placeableRes is None:
            return
        if placeableRes.visualModel is None:
            return
        isLoading = False
        for m in placeableRes.visualModel.meshes:
            if m.geometry is not None and not m.geometry.isGood:
                isLoading = True
                break

        if isLoading:
            trinity.WaitForResourceLoads()
        if component.minSpecOverideMetaMaterialPath is not None and component.minSpecOverideMetaMaterialPath != 'None' and sm.GetService('device').GetAppFeatureState('Interior.lowSpecMaterialsEnabled', False):
            materialRes = metaMaterials.LoadMaterialRes(component.minSpecOverideMetaMaterialPath)
            metaMaterials.ApplyMaterialRes(component.renderObject, materialRes)
        elif component.overrideMetaMaterialPath is not None and component.minSpecOverideMetaMaterialPath != 'None':
            materialRes = metaMaterials.LoadMaterialRes(component.overrideMetaMaterialPath)
            metaMaterials.ApplyMaterialRes(component.renderObject, materialRes)
        else:
            metaMaterials.LoadAndApplyMaterialRes(component.renderObject)

    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            scale = None
            if not entity.HasComponent('collisionMesh'):
                scale = component.scale
            component.renderObject.transform = util.ConvertTupleToTriMatrix(geo2.MatrixTransformation(None, None, scale, None, positionComponent.rotation, positionComponent.position))
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        scene.AddDynamic(component.renderObject)

    def RegisterComponent(self, entity, component):
        self.placeableEntities.add(entity)

    def UnRegisterComponent(self, entity, component):
        self.graphicClient.GetScene(entity.scene.sceneID).RemoveDynamic(component.renderObject)
        self.placeableEntities.remove(entity)

    def OnGraphicSettingsChanged(self, changes):
        for entity in self.placeableEntities:
            uthread.new(self.ApplyMaterials, entity, entity.GetComponent('interiorPlaceable'))