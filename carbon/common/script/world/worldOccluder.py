
class WorldOccluder(object):
    __guid__ = 'world.Occluder'

    def __init__(self, row):
        self.mainRow = row



    def GetName(self):
        return self.mainRow.occluderName



    def GetID(self):
        return self.mainRow.occluderID



    def GetOccluderID(self):
        return self.mainRow.occluderID



    def GetWorldSpaceTypeID(self):
        return self.mainRow.worldSpaceTypeID



    def GetPosition(self):
        return (self.mainRow.posX, self.mainRow.posY, self.mainRow.posZ)



    def GetRotation(self):
        return (self.mainRow.yaw, self.mainRow.pitch, self.mainRow.roll)



    def GetCellName(self):
        return self.mainRow.cellName



    def GetScale(self):
        return (self.mainRow.scaleX, self.mainRow.scaleY, self.mainRow.scaleZ)




