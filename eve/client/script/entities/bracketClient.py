import service
import uicls

class BracketComponent:
    __guid__ = 'entities.BracketComponent'

    def __init__(self):
        self.bracketUI = None
        self.bracket = None
        self.maxWidth = 0.0
        self.maxHeight = 0.0




class BracketClient(service.Service):
    __update_on_reload__ = True
    __guid__ = 'svc.bracketClient'
    __componentTypes__ = ['bracket']
    __dependencies__ = ['graphicClient', 'proximityTrigger']

    def __init__(self):
        service.Service.__init__(self)
        self.components = {}



    def Run(self, *args):
        service.Service.Run(self, args)
        self.activeBrackets = set()



    def CreateComponent(self, name, state):
        component = BracketComponent()
        component.maxWidth = state.get('maxWidth', 0.0)
        component.maxHeight = state.get('maxHeight', 0.0)
        return component



    def RegisterComponent(self, entity, component):
        self.components[entity.entityID] = component
        self.proximityTrigger.RegisterEnterCallback(session.locationid, entity.entityID, self.SetActive)
        self.proximityTrigger.RegisterExitCallback(session.locationid, entity.entityID, self.SetInactive)
        self._CreateBracket(entity)



    def UnRegisterComponent(self, entity, component):
        self.activeBrackets.discard(entity.entityID)
        component = self.components.pop(entity.entityID, None)
        if component and component.bracketUI:
            component.bracketUI.Close()
            component.bracketUI = None



    def ReloadBrackets(self):
        for bracket in self.components.values():
            if bracket.bracketUI:
                bracket.bracketUI.Close()
                self._CreateBracket(bracket.bracketUI.entity)
            if bracket.bracketUI.entity.entityID in self.activeBrackets:
                bracket.bracketUI.SetActive()




    def SetActive(self, causingEntityID, entityID):
        self.activeBrackets.add(entityID)
        self.components[entityID].bracketUI.SetActive()



    def SetInactive(self, causingEntityID, entityID):
        self.activeBrackets.remove(entityID)
        self.components[entityID].bracketUI.SetInactive()



    def _CreateBracket(self, entity):
        interiorPlaceable = entity.GetComponent('interiorPlaceable')
        if interiorPlaceable is not None:
            renderObject = interiorPlaceable.renderObject
        else:
            interiorStatic = entity.GetComponent('interiorStatic')
            if interiorStatic is not None:
                renderObject = interiorStatic.renderObject
        bracket = entity.GetComponent('bracket')
        bracket.bracketUI = uicls.EntityBracket(parent=uicore.layer.charcontrol.bracketContainer, entity=entity, trackObject=renderObject, maxWidth=bracket.maxWidth, maxHeight=bracket.maxHeight)
        if uicore.layer.charcontrol.IsClosed():
            bracket.bracketUI.Close()




