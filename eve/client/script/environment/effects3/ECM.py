import effects
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_USEBALLTRANSLATION = 1
FX_SCALE_EFFECT_NONE = 0
FX_USEBALLROTATION = 2

class ECM(effects.ShipEffect):
    __guid__ = 'effects.ElectronicAttributeModifyActivate'
    __gfx__ = 'res:/Model/Effect3/ECM.red'
    __scaling__ = FX_SCALE_EFFECT_SYMMETRICAL
    __positioning__ = FX_USEBALLTRANSLATION | FX_USEBALLROTATION

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Prepare(self):
        effects.ShipEffect.Prepare(self)
        self.gfx.translation = (0, 0, 0)




