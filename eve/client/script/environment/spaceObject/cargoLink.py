import spaceObject
import nodemanager
import blue
import trinity
import uthread
import util
CARGOLINK_SPACEPORT = 4579
CARGOLINK_SPACEELEVATOR = 4580

class CargoLink(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.CargoLink'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.modelLists = {1: CARGOLINK_SPACEPORT,
         2: CARGOLINK_SPACEELEVATOR}



    def Assemble(self):
        self.SetStaticDirection()



    def LoadModel(self):
        self.LogInfo('CargoLink LoadModel ')
        self.level = self.ballpark.slimItems[self.id].level
        self.DoModelChange()



    def OnSlimItemUpdated(self, slimItem):
        self.level = self.ballpark.slimItems[self.id].level
        uthread.pool('CargoLink::DoModelChange', self.DoModelChange)



    def DoModelChange(self):
        oldModel = self.model
        if self.level is None or self.level not in self.modelLists:
            spaceObject.SpaceObject.LoadModel(self)
        else:
            modelName = util.GraphicFile(self.modelLists[self.level])
            spaceObject.SpaceObject.LoadModel(self, modelName)
            if self.model is None:
                spaceObject.SpaceObject.LoadModel(self)
        self.SetStaticDirection()
        if oldModel is not None:
            uthread.pool('CargoLink::DelayedRemove', self.DelayedRemove, oldModel, int(1000))
        if self.model is not None:
            self.model.display = True



    def DelayedRemove(self, model, delay):
        model.name = model.name + '_removing'
        model.display = False
        trinity.WaitForResourceLoads()
        blue.pyos.synchro.Sleep(delay)
        self.RemoveAndClearModel(model)




