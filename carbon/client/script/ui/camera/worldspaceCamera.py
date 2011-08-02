import GameWorld
import cameras

class WorldspaceCamera(cameras.PolarCamera):
    __guid__ = 'cameras.WorldspaceCamera'

    def __init__(self):
        cameras.PolarCamera.__init__(self)
        self.gameWorldClient = sm.GetService('gameWorldClient')



    def PerformPick(self, x, y, ignoreEntID = -1):
        (startPoint, endPoint,) = self.GetRay(x, y)
        if not session.worldspaceid:
            return None
        else:
            gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
            if gameWorld:
                collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
                p = gameWorld.LineTestEntId(startPoint, endPoint, ignoreEntID, collisionGroups)
                return p
            return None




