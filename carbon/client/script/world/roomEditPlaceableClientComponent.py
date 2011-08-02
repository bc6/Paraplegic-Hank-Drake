import uthread
import geo2

class RoomEditPlaceableClientComponent:
    __guid__ = 'entities.RoomEditPlaceableClientComponent'

    def __init__(self, state):
        self.itemID = self.entID = state['itemID']
        self.typeID = state['typeID']
        self.gridTypeAssociation = [const.world.ROOM_EDIT_GRID_TYPE_FLOOR, const.world.ROOM_EDIT_GRID_TYPE_SURFACE]
        self.worldspaceID = state['worldspaceID']
        if boot.appname == 'EVE':
            invType = cfg.invtypes.Get(self.typeID)
            if invType:
                self.graphicID = invType.graphicID
                self.typeName = invType.typeName
            else:
                self.graphicID = self.typeName = None
        else:
            invType = cfg.inventoryTypes.GetIfExists(self.typeID)
            if invType:
                self.graphicID = invType.worldModelGraphicID
                self.typeName = invType.typeName
            else:
                self.graphicID = self.typeName = None
        self.translation = state['pos']
        self.rotation = state['rot']
        self.localRotationY = state['rot'][0]
        rotQuat = geo2.QuaternionRotationSetYawPitchRoll(*state['rot'])
        self.normal = geo2.QuaternionTransformVector(rotQuat, (0.0, 1.0, 0.0))
        self.validPosition = False
        self.validGridType = False
        self.validCollision = False



    def GetValidationState(self):
        return self.validPosition and self.validGridType




