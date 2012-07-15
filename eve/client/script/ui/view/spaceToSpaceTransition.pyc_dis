#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/view/spaceToSpaceTransition.py
import viewstate
import blue

class SpaceToSpaceTransition(viewstate.FadeToBlackLiteTransition):
    __guid__ = 'viewstate.SpaceToSpaceTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        self.scene = None
        viewstate.FadeToBlackLiteTransition.__init__(self, fadeTimeMS, fadeInTimeMS, fadeOutTimeMS, **kwargs)

    def StartTransition(self, fromView, toView):
        sceneManager = sm.GetService('sceneManager')
        sceneRes = sceneManager.GetScene()
        self.scene = blue.resMan.GetObject(sceneRes)
        blue.synchro.Yield()
        viewstate.FadeToBlackLiteTransition.StartTransition(self, fromView, toView)

    def EndTransition(self, fromView, toView):
        viewstate.FadeToBlackLiteTransition.EndTransition(self, fromView, toView)
        self.scene = None