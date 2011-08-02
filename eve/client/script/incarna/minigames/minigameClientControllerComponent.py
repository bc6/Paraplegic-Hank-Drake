import minigames
import collections
import minigameConst

class MinigameControllerClientComponent:
    __guid__ = 'minigames.MinigameControllerClientComponent'

    def __init__(self, state):
        if state['gameTypeID'] == minigameConst.GAME_SLAY:
            self.minigameController = minigames.SlayLogicClient()
        else:
            raise RuntimeError('Minigame controller needs to be of a specific known type, type %s, is not recognized.' % str(state['gameTypeID']))
        self.state = state



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        for key in self.state:
            report[key] = self.state[key]

        return report



    def JoinGame(self):
        self.minigameController.JoinGame()



    def OnMinigameServerMessage(self, entityID, *args):
        self.minigameController.OnMinigameServerMessage(entityID, *args)




