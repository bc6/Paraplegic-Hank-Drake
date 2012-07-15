#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/asteroidBelt.py
import spaceObject
import trinity

class AsteroidBelt(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.AsteroidBelt'

    def LoadModel(self):
        model = None
        model = trinity.EveRootTransform()
        spaceObject.SpaceObject.LoadModel(self, fileName='', loadedModel=model)

    def Assemble(self):
        self.SetupAmbientAudio(u'worldobject_asteroidbelt_wind_play')
        spaceObject.SpaceObject.Assemble(self)


exports = {'spaceObject.AsteroidBelt': AsteroidBelt}