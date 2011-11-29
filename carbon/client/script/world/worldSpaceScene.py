import world

class WorldSpaceScene(world.WorldSpace):
    __guid__ = 'world.CoreWorldSpaceScene'

    def __init__(self, worldSpaceID = None, instanceID = None):
        world.WorldSpace.__init__(self, worldSpaceID, instanceID)
        self.properties = {}



    def LoadProperties(self):
        pass




