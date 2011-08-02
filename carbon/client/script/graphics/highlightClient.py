import service
import trinity

class HighlightComponent:
    __guid__ = 'component.HighlightComponent'

    def __init__(self):
        self.highlightAreas = []
        self.curveResPath = ''
        self.highlighted = False
        self.curveSet = None
        self.curve = None




class HighlightClient(service.Service):
    __guid__ = 'svc.highlightClient'
    __displayname__ = 'Highlight Client Service'
    __componentTypes__ = ['highlight']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)



    def CreateComponent(self, name, state):
        component = HighlightComponent()
        if 'highlighted' in state:
            component.highlighted = state['highlighted']
        if 'curveResPath' in state:
            component.curveResPath = state['curveResPath']
        if 'highlightAreas' in state:
            component.highlightAreas = [ name.strip() for name in state['highlightAreas'].split(';') ]
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if component.curveResPath == '':
            return 
        component.curve = trinity.Load(component.curveResPath)



    def SetupComponent(self, entity, component):
        if component.highlighted:
            self.HighlightEntity(entity, component.highlightAreas, True)



    def UnRegisterComponent(self, entity, component):
        if component.highlighted:
            self.HighlightEntity(entity, False)
        component.curve = None



    def HighlightEntity(self, entity, highlight):
        highlightComponent = entity.GetComponent('highlight')
        if highlightComponent is None:
            return 
        if highlightComponent.highlighted == highlight:
            return 
        if highlightComponent.curve is None:
            return 
        placeableComponent = entity.GetComponent('interiorPlaceable')
        if placeableComponent is None:
            return 
        if placeableComponent.renderObject is None:
            return 
        highlightParameters = []
        curveSets = None
        object = placeableComponent.renderObject
        if hasattr(object, 'detailMeshes'):
            rebind = False
            for mesh in object.detailMeshes:
                rebind |= self._FindMeshHighlightParameters(mesh, highlightComponent.highlightAreas, highlightParameters, highlight)

            if rebind:
                object.BindLowLevelShaders()
            curveSets = object.curveSets
        elif hasattr(object, 'placeableRes') and object.placeableRes is not None and object.placeableRes.visualModel is not None:
            rebind = False
            for mesh in object.placeableRes.visualModel.meshes:
                rebind |= self._FindMeshHighlightParameters(mesh, highlightComponent.highlightAreas, highlightParameters, highlight)

            if rebind:
                object.BindLowLevelShaders()
            curveSets = object.placeableRes.curveSets
        if curveSets is not None and len(highlightParameters) > 0:
            if highlight:
                highlightComponent.curveSet = trinity.TriCurveSet()
                highlightComponent.curveSet.curves.append(highlightComponent.curve)
                for parameter in highlightParameters:
                    binding = trinity.TriValueBinding()
                    binding.sourceObject = highlightComponent.curve
                    binding.sourceAttribute = 'value'
                    binding.destinationObject = parameter
                    binding.destinationAttribute = 'value'
                    highlightComponent.curveSet.bindings.append(binding)

                curveSets.append(highlightComponent.curveSet)
                highlightComponent.curveSet.Play()
            elif highlightComponent.curveSet is not None and not highlight:
                curveSets.remove(highlightComponent.curveSet)
                highlightComponent.curveSet = None
                for parameter in highlightParameters:
                    parameter.value = (0.0, 0.0, 0.0, 0.0)

        highlightComponent.highlighted = highlight



    def _FindMeshHighlightParameters(self, mesh, highlightAreas, highlightParameters, highlight):
        rebind = False
        for area in mesh.opaquePrepassAreas:
            rebind |= self._FindAreaHighlightParameters(area, highlightAreas, highlightParameters, highlight)

        for area in mesh.transparentAreas:
            rebind |= self._FindAreaHighlightParameters(area, highlightAreas, highlightParameters, highlight)

        return rebind



    def _FindAreaHighlightParameters(self, area, highlightAreas, highlightParameters, highlight):
        if len(highlightAreas) > 0 and area.name not in highlightAreas:
            return False
        if area.effect is None or type(area.effect) != trinity.Tr2ShaderMaterial:
            return False
        if 'MaterialHighlight' not in area.effect.parameters:
            if highlight:
                parameter = trinity.Tr2Vector4Parameter()
                parameter.name = 'MaterialHighlight'
                parameter.value = (0, 0, 0, 0)
                area.effect.parameters['MaterialHighlight'] = parameter
                highlightParameters.append(parameter)
                return True
        else:
            highlightParameters.append(area.effect.parameters['MaterialHighlight'])
        return False




