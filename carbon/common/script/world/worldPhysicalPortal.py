
class WorldPhysicalPortal(object):
    __guid__ = 'world.PhysicalPortal'

    def __init__(self, row):
        self.worldSpaceTypeID = row.worldSpaceTypeID
        self.portalID = row.portalID
        self.mainRow = row



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetID(self):
        return self.portalID



    def GetPortalID(self):
        return self.portalID



    def GetName(self):
        return self.mainRow.portalName



    def GetPosition(self):
        return (self.mainRow.posX, self.mainRow.posY, self.mainRow.posZ)



    def GetRotation(self):
        return (self.mainRow.rotY, self.mainRow.rotX, self.mainRow.rotZ)



    def GetScale(self):
        return (self.mainRow.scaleX, self.mainRow.scaleY, self.mainRow.scaleZ)



    def GetCellA(self):
        return self.mainRow.cellA



    def GetCellB(self):
        return self.mainRow.cellB




