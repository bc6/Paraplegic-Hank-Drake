import cameras
import GameWorld

class RoomEditCamera(cameras.FreeCamera):
    __guid__ = 'cameras.RoomEditCamera'

    def PerformPick(self, x, y, ignoreEntID = -1):
        (startPoint, endPoint,) = self.GetRay(x, y)
        gameWorld = sm.GetService('gameWorldClient').GetGameWorld(session.worldspaceid)
        if gameWorld:
            collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
            p = gameWorld.LineTestEntId(startPoint, endPoint, ignoreEntID, collisionGroups)
            return p
        else:
            return None



    def PickAgainstRoomEditGrids(self, x, y, roomEditGridGW):
        (pickRayStart, pickRayEnd,) = self.GetRay(x, y)
        return roomEditGridGW.LineTest(pickRayStart, pickRayEnd)



    def IsCamFirstPerson(self):
        return True




