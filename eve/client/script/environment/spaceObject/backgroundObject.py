import spaceObject
import trinity

class BackgroundObject(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.BackgroundObject'

    def LoadModel(self):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        graphicURL = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
        object = trinity.Load(graphicURL)
        self.backgroundObject = object
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.backgroundObjects.append(object)



    def Release(self):
        if self.released:
            return 
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.backgroundObjects.fremove(self.backgroundObject)
        self.backgroundObject = None
        spaceObject.SpaceObject.Release(self, 'BackgroundObject')



exports = {'spaceObject.BackgroundObject': BackgroundObject}

