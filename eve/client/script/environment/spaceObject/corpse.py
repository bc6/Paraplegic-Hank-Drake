import spaceObject

class Corpse(spaceObject.SpaceObject):
    __guid__ = 'spaceObject.Corpse'

    def LoadModel(self, fileName = None, useInstance = False):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        gender = ['male', 'female'][(slimItem.typeID == const.typeCorpseFemale)]
        path = 'res:/Model/Face/fullbody_char/corpses/corpse_%s0%s.blue' % (gender, self.id % 3 + 1)
        spaceObject.SpaceObject.LoadModel(self, path, useInstance)



    def Explode(self):
        if self.model is None:
            return 
        explosionURL = 'res:/Model/Effect3/capsule_explosion.red'
        return spaceObject.SpaceObject.Explode(self, explosionURL)



exports = {'spaceObject.Corpse': Corpse}

