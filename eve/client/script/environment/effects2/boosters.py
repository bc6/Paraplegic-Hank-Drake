import effects
import trinity
import blue

class BoosterShort(effects.GenericEffect):
    __guid__ = 'effects.BoosterShort'

    def Key(trigger):
        return (trigger.shipID,
         None,
         None,
         None)


    Key = staticmethod(Key)

    def _GetDuration():
        return 1000


    _GetDuration = staticmethod(_GetDuration)

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]



    def Stop(self):
        pass



    def Prepare(self):
        pass



    def Start(self, duration):
        pass



    def Repeat(self, duration):
        pass




class BoosterStop(BoosterShort):
    __guid__ = 'effects.BoosterStop'

    def _GetDuration():
        return 2000


    _GetDuration = staticmethod(_GetDuration)

    def Start(self, duration):
        pass




