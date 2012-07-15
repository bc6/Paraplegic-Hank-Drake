#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/interiorStaticClient.py
import cef
import collections
import service
import trinity
import blue

class InteriorStaticClientComponent:
    __guid__ = 'component.InteriorStaticClientComponent'


class InteriorStaticClient(service.Service):
    __guid__ = 'svc.interiorStaticClient'
    __componentTypes__ = [cef.InteriorStaticComponentView.GetComponentCodeName()]
    __dependencies__ = ['graphicClient']

    def CreateComponent(self, name, state):
        component = InteriorStaticClientComponent()
        if 'graphicID' in state:
            component.graphicID = state['graphicID']
        else:
            self.LogError('interiorStatic Component requires graphicID in its state')
            component.graphicID = 0
        component.cellName = state.get('cellName', 'DefaultCell')
        component.systemID = state.get('systemID', '0')
        component.objectID = state.get('objectID', 0)
        component.spawnID = state['_spawnID']
        component.enlightenOverrides = state.get('keyedData', {})
        component.depthOffset = float(state.get('depthOffset', 0))
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['graphicID'] = component.graphicID
        report['Position'] = component.renderObject.GetPosition()
        report['Rotation'] = component.renderObject.GetRotationYawPitchRoll()
        return report

    def WaitForGeometry(self, renderObject):
        geometry = renderObject.geometry
        if geometry is None:
            return
        while geometry.isLoading and not geometry.isPrepared:
            blue.synchro.Yield()

    def PrepareComponent(self, sceneID, entityID, component):
        modelFile = self.graphicClient.GetModelFilePath(component.graphicID)
        component.entityID = entityID
        if modelFile is not None:
            renderObject = trinity.Load(modelFile)
        else:
            renderObject = None
        if renderObject is None or renderObject.__bluetype__ != 'trinity.Tr2InteriorStatic':
            if renderObject is None:
                self.LogWarn('!!! WARNING !!! Asset (', modelFile, ') is missing !!! WARNING !!!')
            else:
                self.LogWarn('!!! WARNING !!! Asset (', modelFile, ') is not a trinity.Tr2InteriorStatic but instead a ', renderObject.__bluetype__, ' !!! WARNING !!!')
            renderObject = trinity.Load(const.BAD_ASSET_STATIC)
            if renderObject is None:
                self.LogError('!!! ERROR !!! The InteriorStatic bad asset is missing ', const.BAD_ASSET_STATIC, '!!! ERROR !!!')
                renderObject = trinity.Tr2InteriorStatic()
            self.WaitForGeometry(renderObject)
        else:
            for areaName, enlightenOverride in component.enlightenOverrides.iteritems():
                for area in renderObject.enlightenAreas:
                    if areaName == area.name:
                        area.isEmissive = bool(enlightenOverride['isEmissive'])
                        area.albedoColor = (enlightenOverride['albedoColorR'],
                         enlightenOverride['albedoColorG'],
                         enlightenOverride['albedoColorB'],
                         0)
                        area.emissiveColor = (enlightenOverride['emissiveColorR'],
                         enlightenOverride['emissiveColorG'],
                         enlightenOverride['emissiveColorB'],
                         0)
                else:
                    self.LogWarn('On interiorStatic graphicID', component.graphicID, 'missing area name', areaName, 'for override')

            renderObject.depthOffset = component.depthOffset
        renderObject.name = str(self.graphicClient.GetGraphicName(component.graphicID) + ': ' + str(entityID))
        component.renderObject = renderObject

    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.renderObject.worldPosition = positionComponent.position
            component.renderObject.rotation = positionComponent.rotation
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        scene.AddStatic(component.renderObject, component.cellName, component.systemID, id=component.spawnID)

    def UnRegisterComponent(self, entity, component):
        self.graphicClient.GetScene(entity.scene.sceneID).RemoveStatic(component.renderObject)