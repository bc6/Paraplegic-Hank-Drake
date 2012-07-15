#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveLoadingWheel.py
import uicls
import uiconst
import uiutil
import uthread
import blue

class LoadingWheel(uicls.Transform):
    __guid__ = 'uicls.LoadingWheel'
    default_name = 'loadingWheel'
    default_width = 64
    default_height = 64
    default_loopParams = (1, 1000.0)

    def ApplyAttributes(self, attributes):
        uicls.Transform.ApplyAttributes(self, attributes)
        sprite = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/loadingWheel.dds', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        loopParams = attributes.get('loopParams', self.default_loopParams)
        if loopParams:
            direction, time = loopParams
            uthread.new(self.StartRotationCycle, direction, time)