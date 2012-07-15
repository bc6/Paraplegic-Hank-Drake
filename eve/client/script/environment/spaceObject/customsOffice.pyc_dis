#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/customsOffice.py
import spaceObject
import nodemanager
import blue
import trinity
import uthread
import util
CUSTOMSOFFICE_SPACEPORT = 4579
CUSTOMSOFFICE_SPACEELEVATOR = 4580

class CustomsOffice(spaceObject.LargeCollidableStructure):
    __guid__ = 'spaceObject.CustomsOffice'

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.modelLists = {1: CUSTOMSOFFICE_SPACEPORT,
         2: CUSTOMSOFFICE_SPACEELEVATOR}

    def Assemble(self):
        self.SetStaticRotation()
        self.SetupAmbientAudio()

    def LoadModel(self):
        self.LogInfo('CustomsOffice LoadModel ')
        self.level = self.ballpark.slimItems[self.id].level
        self.DoModelChange()

    def OnSlimItemUpdated(self, slimItem):
        self.level = self.ballpark.slimItems[self.id].level
        uthread.pool('CustomsOffice::DoModelChange', self.DoModelChange)

    def DoModelChange(self):
        oldModel = self.model
        if self.level is None or self.level not in self.modelLists:
            spaceObject.SpaceObject.LoadModel(self)
        else:
            modelName = util.GraphicFile(self.modelLists[self.level])
            spaceObject.SpaceObject.LoadModel(self, modelName)
            if self.model is None:
                spaceObject.SpaceObject.LoadModel(self)
        self.SetStaticRotation()
        if oldModel is not None:
            uthread.pool('CustomsOffice::DelayedRemove', self.DelayedRemove, oldModel, int(1000))
        if self.model is not None:
            self.model.display = True

    def DelayedRemove(self, model, delay):
        model.name = model.name + '_removing'
        model.display = False
        trinity.WaitForResourceLoads()
        blue.pyos.synchro.SleepWallclock(delay)
        self.RemoveAndClearModel(model)