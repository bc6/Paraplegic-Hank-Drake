#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/AI/perceptionClient.py
import GameWorld
import service
import AI

class PerceptionClient(AI.perceptionCommon):
    __guid__ = 'svc.perceptionClient'
    __notifyevents__ = []
    __dependencies__ = ['gameWorldClient']

    def __init__(self):
        AI.perceptionCommon.__init__(self)

    def Run(self, *etc):
        self.gameWorldService = self.gameWorldClient
        service.Service.Run(self, etc)

    def MakePerceptionManager(self):
        return GameWorld.PerceptionManagerClient()

    def IsClientServerFlagValid(self, clientServerFlag):
        return clientServerFlag & const.aiming.AIMING_CLIENTSERVER_FLAG_CLIENT