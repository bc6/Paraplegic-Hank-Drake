import collections
import service
import trinity
import blue

class InteriorStaticClientComponent:
    __guid__ = 'component.InteriorStaticClientComponent'


class InteriorStaticClient(service.Service):
    __guid__ = 'svc.interiorStaticClient'
    __componentTypes__ = ['interiorStatic']
    __dependencies__ = ['graphicClient']

    def CreateComponent(self, name, state):
        component = InteriorStaticClientComponent()
        if 'graphicID' in state:
            component.graphicID = state['graphicID']
        else:
            cfgGraphic = cfg.invtypes.Get(state['_typeID']).Graphic()
            if cfgGraphic:
                component.graphicID = cfgGraphic.id
            else:
                self.LogError('interiorPlaceable Component requires typeID: ', state['_typeID'], ' to have a graphicID')
                component.graphicID = 0
        component.cellID = state['cellID']
        component.systemID = state['systemID']
        component.objectID = state['objectID']
        component.enlightenOverrides = state.get('keyedData', {})
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
        renderObject = trinity.Load(modelFile)
        self.WaitForGeometry(renderObject)
        if renderObject is None or renderObject.__bluetype__ != 'trinity.Tr2InteriorStatic':
            if renderObject is None:
                self.LogWarn('!!! WARNING !!! Asset (', modelFile, ') is missing !!! WARNING !!!')
            else:
                self.LogWarn('!!! WARNING !!! Asset (', modelFile, ') is not a trinity.Tr2InteriorStatic but instead a ', renderObject.__bluetype__, ' !!! WARNING !!!')
            renderObject = trinity.Load(const.BAD_ASSET_STATIC)
            self.WaitForGeometry(renderObject)
            if renderObject is None:
                self.LogError('!!! ERROR !!! The InteriorStatic bad asset is missing ', const.BAD_ASSET_STATIC, '!!! ERROR !!!')
                renderObject = trinity.Tr2InteriorStatic()
        else:
            for (areaName, enlightenOverride,) in component.enlightenOverrides:
                for area in renderObject.enlightenAreas:
                    if areaName == area.name:
                        area.isEmissive = enlightenOverride['isEmissive']
                        area.albedoColor = (enlightenOverride['albedoColorR'],
                         enlightenOverride['albedoColorG'],
                         enlightenOverride['albedoColorB'],
                         0)
                        area.emissiveColor = (enlightenOverride['emmissiveColorR'],
                         enlightenOverride['emmissiveColorG'],
                         enlightenOverride['emmissiveColorB'],
                         0)
                else:
                    self.LogWarn('On interiorStatic graphicID', component.graphicID, 'missing area name', areaName, 'for override')


        renderObject.name = str(entityID)
        component.renderObject = renderObject



    def SetupComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.renderObject.worldPosition = positionComponent.position
            component.renderObject.rotation = positionComponent.rotation
        scene = self.graphicClient.GetScene(entity.scene.sceneID)
        scene.AddStatic(component.renderObject, component.cellID, component.systemID, id=component.objectID)



    def UnRegisterComponent(self, entity, component):
        self.graphicClient.GetScene(entity.scene.sceneID).RemoveStatic(component.renderObject)




