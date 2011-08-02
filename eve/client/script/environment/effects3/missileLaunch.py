import effects
import state
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_USEBALLTRANSLATION = 1
FX_SCALE_EFFECT_NONE = 0

class missileLaunch(effects.ShipEffect):
    __guid__ = 'effects.MissileDeployment'
    __gfx__ = 'res:/Model/Effect3/missileLaunch.red'
    __positioning__ = FX_USEBALLTRANSLATION
    __scaling__ = FX_SCALE_EFFECT_NONE

    def _Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def _GetDuration():
        return 12000


    _GetDuration = staticmethod(_GetDuration)

    def Prepare(self):
        if self.GetEffectShipID() != sm.StartService('state').GetExclState(state.lookingAt):
            return 
        effects.ShipEffect.Prepare(self)



    def Start(self, duration):
        if self.gfx is None:
            return 
        effects.ShipEffect.Start(self, duration)



    def Stop(self):
        if self.gfx is None:
            return 
        effects.ShipEffect.Stop(self)



    def Repeat(self, duration):
        if self.gfx is None:
            return 
        effects.ShipEffect.Repeat(self, duration)




