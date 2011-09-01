import service
import collections
import geo2
import blue

class SelectionClientComponent:
    __guid__ = 'entity.SelectionClientComponent'
    ALWAYS_ACCEPT_MODE = 1
    ALWAYS_REJECT_MODE = 2
    MAX_DISTANCE_MODE = 3

    def __init__(self):
        self.modeEnum = SelectionClientComponent.MAX_DISTANCE_MODE
        self.maxSelectionDistance = 10




class SelectionClient(service.Service):
    __guid__ = 'svc.selectionClient'
    __componentTypes__ = ['selectionComponent']
    __dependencies__ = ['graphicClient']

    def Run(self, *etc):
        self.mouseInputService = sm.GetService('mouseInput')
        self.defaultSelectionComponent = SelectionClientComponent()
        self.selectedEntityID = None
        self.InitModeToMethodDict()
        self.mouseInputService.RegisterCallback(const.INPUT_TYPE_MOUSEDOWN, self.OnMouseDown)
        self.renderableToEntity = {}



    def InitModeToMethodDict(self):
        self.modeToMethodDict = {SelectionClientComponent.ALWAYS_ACCEPT_MODE: self._TryAlwaysAcceptMode,
         SelectionClientComponent.ALWAYS_REJECT_MODE: self._TryAlwaysRejectMode,
         SelectionClientComponent.MAX_DISTANCE_MODE: self._TryMaxDistanceMode}



    def CreateComponent(self, name, state):
        component = SelectionClientComponent()
        if state:
            component.__dict__.update(state)
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict(sorted(component.__dict__.items()))
        return report



    def _TryAlwaysAcceptMode(self, selectionComponent, pickedEntity):
        return True



    def _TryAlwaysRejectMode(self, selectionComponent, pickedEntity):
        return False



    def _TryMaxDistanceMode(self, selectionComponent, pickedEntity):
        pickedPos = pickedEntity.GetComponent('position').position
        playerPos = self.entityService.GetPlayerEntity().GetComponent('position').position
        distSq = geo2.Vec3DistanceSq(pickedPos, playerPos)
        maxDist = selectionComponent.maxSelectionDistance
        maxSq = maxDist * maxDist
        return distSq <= maxSq



    def GetSelectedEntityID(self):
        return self.selectedEntityID



    def TrySelect(self, entityID):
        pickedEntity = self.entityService.FindEntityByID(entityID)
        if not pickedEntity:
            return 
        if pickedEntity.HasComponent('selectionComponent'):
            selectionComponent = pickedEntity.GetComponent('selectionComponent')
        else:
            return 
        methodToCall = self.modeToMethodDict[selectionComponent.modeEnum]
        selectionAccepted = methodToCall(selectionComponent, pickedEntity)
        entityID = entityID if selectionAccepted else None
        if entityID != self.selectedEntityID:
            self.selectedEntityID = entityID
            sm.ScatterEvent('OnEntitySelectionChanged', self.selectedEntityID)
        return selectionAccepted



    def OnMouseDown(self, button, posX, posY, entityID):
        if entityID:
            self.TrySelect(entityID)




