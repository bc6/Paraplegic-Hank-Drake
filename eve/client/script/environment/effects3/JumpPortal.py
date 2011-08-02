import effects
import trinity
import blue
FX_SCALE_EFFECT_NONE = 0

class JumpPortal(effects.ShipEffect):
    __guid__ = 'effects.JumpPortal'
    __gfx__ = 'res:/Model/Effect3/JumpPortal.red'
    __scaling__ = FX_SCALE_EFFECT_NONE

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')
        self.PlayOldAnimations(self.gfx)



    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')
        self.PlayOldAnimations(self.gfx)




class JumpPortalBO(JumpPortal):
    __guid__ = 'effects.JumpPortalBO'
    __gfx__ = 'res:/Model/Effect3/JumpPortal_BO.red'
    __scaling__ = FX_SCALE_EFFECT_NONE


