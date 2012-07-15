#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/world/gameWorldClient.py
import GameWorld
import trinity

class GameWorldClient(GameWorld.GameWorldService):
    __guid__ = 'svc.gameWorldClient'

    def Run(self, *etc):
        GameWorld.GameWorldService.Run(self)

    def GetGameWorldType(self):
        return GameWorld.GameWorldClient

    def OnLoadEntityScene(self, sceneID):
        GameWorld.GameWorldService.OnLoadEntityScene(self, sceneID)