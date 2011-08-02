import effects
import trinity
import blue
import uthread
import audio2

class Cloaking(effects.GenericEffect):
    __guid__ = 'effects.Cloaking'


class Cloak(effects.ShipRenderEffect):
    __guid__ = 'effects.Cloak'
    __gfx__ = 'res:/Model/Effect3/Cloaking.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.guid,
         None,
         None)


    _Key = staticmethod(_Key)

    def _GetDuration():
        return 6000


    _GetDuration = staticmethod(_GetDuration)

    def Start(self, duration):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        shipBall.KillCloakedCopy()
        shipBall.cloakedCopy = self.gfxModel
        effects.ShipRenderEffect.Start(self, duration)
        if getattr(shipBall, 'model', None) is not None:
            model = shipBall.model
            bindings = self.gfxModel.Find('trinity.TriValueBinding')
            for binding in bindings:
                if binding.name == 'hide':
                    binding.destinationObject = model
                    binding.destinationAttribute = 'display'
                    binding.sourceAttribute = 'value'




    def Stop(self):
        pass




class CloakNoAnim(Cloak):
    __guid__ = 'effects.CloakNoAmim'

    def Start(self, duration):
        Cloak.Start(self, 6000)
        length = self.gfx.curveSets[0].GetMaxCurveDuration()
        self.gfx.curveSets[0].PlayFrom(length)
        shipBall = self.GetEffectShipBall()
        if getattr(shipBall, 'model', None) is not None:
            shipBall.model.display = False




class CloakRegardless(Cloak):
    __guid__ = 'effects.CloakRegardless'
    __gfx__ = 'res:/Model/Effect3/Cloaking.red'


class Uncloak(effects.ShipRenderEffect):
    __guid__ = 'effects.Uncloak'
    __gfx__ = 'res:/Model/Effect3/Cloaking.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.guid,
         None,
         None)


    _Key = staticmethod(_Key)

    def _GetDuration():
        return 7500


    _GetDuration = staticmethod(_GetDuration)

    def Prepare(self):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        if shipBall is None:
            raise RuntimeError('ShipEffect: no ball found')
        cloakedModel = getattr(shipBall, 'cloakedCopy', None)
        if cloakedModel is not None:
            self.gfxModel = cloakedModel
            self.gfx = cloakedModel.children[0]
        else:
            effects.ShipRenderEffect.Prepare(self)



    def Start(self, duration):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        if self.gfx is None:
            return 
        length = self.gfx.curveSets[0].GetMaxCurveDuration()
        if length > 0.0:
            scaleValue = -length / (duration / 1000.0)
            self.gfx.curveSets[0].scale = scaleValue
        self.gfx.curveSets[0].PlayFrom(length)
        shipModel = getattr(shipBall, 'model', None)
        shipBall.PlayGeneralAudioEvent('wise:/ship_uncloak_play')



    def Stop(self):
        shipID = self.GetEffectShipID()
        shipBall = self.GetEffectShipBall()
        shipModel = getattr(shipBall, 'model', None)
        if shipBall is not None and self.gfx is not None and self.gfxModel == shipBall.cloakedCopy:
            shipBall.cloakedCopy = None
            if shipModel is not None:
                shipModel.display = True
        effects.ShipEffect.Stop(self)




