import world

class WorldSpaceObject(world.CoreWorldSpaceObject):
    __guid__ = 'world.WorldSpaceObject'

    def IsTemplateObject(self):
        print 'WorldSpaceObject.IsTemplateObject'
        return False



    def IsEntity(self):
        return False




