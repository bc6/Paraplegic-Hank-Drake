#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/environment/spaceObject/forceField.py
import spaceObject
from string import split

class ForceField(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.ForceField'

    def Assemble(self):
        self.model.boundingSphereRadius = 0.5
        self.model.scaling = (self.radius * 2, self.radius * 2, self.radius * 2)


exports = {'spaceObject.ForceField': ForceField}