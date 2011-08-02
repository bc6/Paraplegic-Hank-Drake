import spaceObject
import trinity
import timecurves
import log
ENVIRONMENTS = (19713, 19746, 19747, 19748, 19749, 19750, 19751, 19752, 19753, 19754, 19755, 19756)

class Cloud(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Cloud'

    def LoadModel(self, fileName = None, useInstance = False, loadedModel = None):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if fileName is None and loadedModel is None:
            if slimItem is None:
                return 
            invType = cfg.invtypes.Get(slimItem.typeID)
            if invType is not None:
                typeID = invType.id
                if typeID in ENVIRONMENTS:
                    log.LogInfo('Not loading dungeon environment (%s), since rework is pending.' % invType.GraphicFile())
                    return 
            if invType.graphicID is not None:
                if type(invType.graphicID) != type(0):
                    raise RuntimeError('NeedGraphicIDNotMoniker', slimItem.itemID)
                tryFileName = invType.GraphicFile()
                if tryFileName is not None:
                    tryFileName = tryFileName.split(' ')[0]
                model = trinity.Load(tryFileName)
                return spaceObject.SpaceObject.LoadModel(self, tryFileName, loadedModel=model)
        spaceObject.SpaceObject.LoadModel(self, fileName, useInstance, loadedModel)



    def Assemble(self):
        self.SetStaticRotation()
        self.SetRadius(self.radius)
        timecurves.ResetTimeCurves(self.model, self.id)
        timecurves.ScaleTime(self.model, 1.0 + 0.01 * (self.id % 20) / 20.0)
        self.SetDefaultLOD()
        if hasattr(self.model, 'boundingSphereRadius'):
            self.model.boundingSphereRadius = 0.5



    def SetRadius(self, r):
        if self.HasBlueInterface(self.model, 'IEveSpaceObject2'):
            self.SetRadiusScene2(self.radius)
        else:
            self.SetRadiusDX8(self.radius)



    def SetRadiusDX8(self, r):
        s = 2.0
        if self.model is not None:
            self.model.scaling.SetXYZ(s * r, s * r, s * r)



    def SetRadiusScene2(self, r):
        if len(self.model.children):
            self.model.children[0].scaling = (r, r, r)



exports = {'spaceObject.Cloud': Cloud}

