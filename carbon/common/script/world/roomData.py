import util
import geo2
import world

class RoomData:
    __guid__ = 'world.RoomData'
    __name__ = 'RoomData'

    def __init__(self, instanceID):
        self.placeables = {}
        self.detailMeshVariants = {}
        self.instanceID = instanceID



    def GetPlaceable(self, itemID):
        if itemID in self.placeables:
            return self.placeables[itemID]



    def PrimePlaceable(self, itemID, typeID, positionVector, rotation):
        newPlaceable = util.KeyVal()
        newPlaceable.itemID = itemID
        newPlaceable.typeID = typeID
        newPlaceable.positionVector = geo2.Vector(*positionVector)
        newPlaceable.rotation = rotation
        self.placeables[itemID] = newPlaceable



    def TransformPlaceable(self, itemID, positionVector, rotation):
        if itemID not in self.placeables:
            raise RuntimeError('Cannot translate an Placeable that does not exist')
        obj = self.placeables[itemID]
        if positionVector is not None:
            obj.positionVector = geo2.Vector(*positionVector)
        if rotation is not None:
            obj.rotation = rotation



    def RemovePlaceable(self, itemID):
        if itemID in self.placeables:
            del self.placeables[itemID]



    def GetDetailMeshVariant(self, objectID):
        if objectID not in self.detailMeshVariants:
            return None
        return self.detailMeshVariants[objectID]



    def PrimeDetailMeshVariant(self, objectID, graphicID):
        self.detailMeshVariants[objectID] = graphicID



    def GetCopy(self):
        newRoomData = world.RoomData(self.instanceID)
        for obj in self.placeables.itervalues():
            newRoomData.PrimePlaceable(obj.itemID, obj.typeID, obj.positionVector, obj.rotation)

        for (objectID, graphicID,) in self.detailMeshVariants.iteritems():
            newRoomData.PrimeDetailMeshVariant(objectID, graphicID)

        return newRoomData



    def Diff(self, otherRoomData):
        diff = util.KeyVal()
        diff.added = []
        diff.moved = []
        diff.removed = []
        diff.variantsAdded = []
        diff.variantsMorphed = []
        diff.variantsRemoved = []
        for (itemID, obj,) in self.placeables.iteritems():
            if itemID not in otherRoomData.placeables:
                diff.added.append(obj)
            else:
                otherObj = otherRoomData.GetPlaceable(itemID)
                if obj.positionVector != otherObj.positionVector or obj.rotation != otherObj.rotation:
                    diff.moved.append(obj)

        for itemID in otherRoomData.placeables.iterkeys():
            if itemID not in self.placeables:
                diff.removed.append(itemID)

        for (objectID, graphicID,) in self.detailMeshVariants.iteritems():
            if objectID not in otherRoomData.detailMeshVariants:
                diff.variantsAdded.append((objectID, graphicID))
            elif graphicID != otherRoomData.detailMeshVariants[objectID]:
                diff.variantsMorphed.append((objectID, graphicID))

        for (objectID, graphicID,) in otherRoomData.detailMeshVariants.iteritems():
            if objectID not in self.detailMeshVariants:
                diff.variantsRemoved.append((objectID, graphicID))

        return diff



    def Serialize(self):
        serializedPlaceables = []
        for obj in self.placeables.itervalues():
            placeable = util.KeyVal(itemID=obj.itemID, typeID=obj.typeID, positionVector=(obj.positionVector.x, obj.positionVector.y, obj.positionVector.z), rotation=obj.rotation)
            serializedPlaceables.append(placeable)

        return (self.instanceID, serializedPlaceables, dict(self.detailMeshVariants))



    def Deserialize(self, data):
        (self.instanceID, placeables, self.detailMeshVariants,) = data
        for obj in placeables:
            self.PrimePlaceable(obj.itemID, obj.typeID, obj.positionVector, obj.rotation)




exports = util.AutoExports('world', locals())

