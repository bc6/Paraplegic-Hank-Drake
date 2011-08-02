import geo2
import entities

class CoreWorldSpaceObject(object):
    __guid__ = 'world.CoreWorldSpaceObject'

    def __init__(self, mainRow):
        self.worldSpaceTypeID = mainRow.worldSpaceTypeID
        self.objectID = mainRow.objectID
        self.mainRow = mainRow
        self.graphicIDOverride = None
        self.lightOverrides = {}
        self.enlightenAreas = {}
        role = boot.role
        self.graphicSvc = sm.GetService('graphic' + role[0].upper() + role[1:].lower())
        self.actionObjectServerSvc = None
        self.boundingBox = None
        self.gwObject = None



    def GetWorldSpaceTypeID(self):
        return self.worldSpaceTypeID



    def GetID(self):
        return self.objectID



    def GetObjectID(self):
        return self.objectID



    def GetModelResFilePath(self):
        return self.graphicSvc.GetModelFilePath(self.GetGraphicID())



    def GetCollisionResFilePath(self):
        return self.graphicSvc.GetCollisionFilePath(self.GetGraphicID())



    def GetGraphicType(self):
        return self.graphicSvc.GetGraphicType(self.GetGraphicID())



    def IsCollidable(self):
        return self.graphicSvc.IsCollidable(self.GetGraphicID())



    def GetTemplateID(self):
        return self.graphicSvc.GetTemplateID(self.GetGraphicID())



    def SetGraphicIDOverride(self, newGraphicID):
        self.graphicIDOverride = newGraphicID



    def SetGameWorldObject(self, gwObject):
        self.gwObject = gwObject



    def GetGameWorldObject(self):
        return self.gwObject



    def GetTransformationMatrix(self):
        scale = geo2.Vector(*self.GetScale())
        rot = geo2.QuaternionRotationSetYawPitchRoll(*self.GetRotation())
        trans = geo2.Vector(*self.GetPosition())
        return geo2.MatrixTransformation(None, None, scale, None, rot, trans)



    def SetBoundingBox(self, boundingBox):
        self.boundingBox = boundingBox



    def GetBoundingBox(self):
        return self.boundingBox



    def GetGroupID(self):
        return self.mainRow.groupID



    def GetPrefabObjectID(self):
        return self.mainRow.prefabObjectID



    def GetName(self):
        return self.mainRow.objectName



    def GetCellID(self):
        if self.mainRow.cellID is None:
            return 0
        else:
            return self.mainRow.cellID



    def GetSystemID(self):
        if self.mainRow.systemID is None:
            return 0
        else:
            return self.mainRow.systemID



    def GetCellName(self):
        return str(self.GetCellID())



    def GetSystemName(self):
        return str(self.GetSystemID())



    def GetPosition(self):
        return (self.mainRow.posX, self.mainRow.posY, self.mainRow.posZ)



    def GetRotation(self):
        return (self.mainRow.rotY, self.mainRow.rotX, self.mainRow.rotZ)



    def GetScale(self):
        return (self.mainRow.scaleX, self.mainRow.scaleY, self.mainRow.scaleZ)



    def GetGraphicID(self):
        if getattr(self, 'graphicIDOverride', None) is None:
            return self.mainRow.graphicID
        return self.graphicIDOverride



    def GetUsesTemplate(self):
        return self.mainRow.usesTemplate



    def IsActionObject(self):
        templateID = self.GetTemplateID()
        if templateID and self.GetUsesTemplate():
            return cfg.actionObjects.GetIfExists(templateID) is not None



    def IsEntity(self):
        return self.IsActionObject()




