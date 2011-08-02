import minigames
import minigameConst

class MinigameConfigClientComponent:
    __guid__ = 'minigames.MinigameConfigClientComponent'

    def __init__(self, state):
        self.entityID = None
        self.state = state
        for entry in state:
            setattr(self, entry, state[entry])




    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        for key in self.state:
            report[key] = self.state[key]

        return report




