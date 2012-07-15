#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/view/transitions.py
from viewstate import Transition
import uicls
import uiconst
import util

class FadeToBlackTransition(Transition):
    __guid__ = 'viewstate.FadeToBlackTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        sm.GetService('loading').FadeToBlack(self.fadeInTimeMS)

    def EndTransition(self, fromView, toView):
        Transition.EndTransition(self, fromView, toView)
        sm.GetService('loading').FadeFromBlack(self.fadeOutTimeMS)


class FadeToBlackLiteTransition(Transition):
    __guid__ = 'viewstate.FadeToBlackLiteTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS
        self.fadeLayer = None

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        viewState = sm.GetService('viewState')
        self.fadeLayer = uicls.Container(name='transition_overlay', parent=viewState.overlayLayerParent, pickState=uiconst.TR2_SPS_OFF, bgColor=util.Color.BLACK, opacity=0.0)
        uicore.animations.FadeIn(self.fadeLayer, duration=self.fadeInTimeMS / 1000.0, sleep=True)

    def EndTransition(self, fromView, toView):
        sm.GetService('loading').FadeFromBlack(self.fadeOutTimeMS)
        uicore.animations.FadeOut(self.fadeLayer, duration=self.fadeOutTimeMS / 1000.0, sleep=True)
        self.fadeLayer.Close()
        del self.fadeLayer
        Transition.EndTransition(self, fromView, toView)