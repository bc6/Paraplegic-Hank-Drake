import util

class ProximityOpenTutorialComponent:
    __guid__ = 'tutorial.ProximityOpenTutorialComponent'

    def __init__(self):
        self.tutorialID = None
        self.radius = None



exports = util.AutoExports('tutorial', locals())

