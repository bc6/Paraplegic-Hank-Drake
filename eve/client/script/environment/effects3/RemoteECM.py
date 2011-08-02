import effects

class RemoteECM(effects.StretchEffect):
    __guid__ = 'effects.RemoteECM'
    __gfx__ = 'res:/Model/Effect3/RemoteECM.red'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.targetID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)


