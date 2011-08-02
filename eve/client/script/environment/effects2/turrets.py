import effects
import uthread
FX_SCALE_EFFECT_SYMMETRICAL = 1
FX_SCALE_EFFECT_NONE = 0

class StandardWeapon(effects.GenericEffect):
    __guid__ = 'effects.StandardWeapon'
    __gfx__ = None

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        self.moduleID = trigger.moduleID
        self.otherTypeID = trigger.otherTypeID



    def _Key(trigger):
        return (trigger.shipID,
         trigger.moduleID,
         None,
         None,
         trigger.guid)


    _Key = staticmethod(_Key)

    def Prepare(self):
        pass



    def Shoot(self, shipBall, targetBall):
        if getattr(self, 'turret', None) is not None:
            self.turret.SetTarget(shipBall, targetBall)
            self.turret.StartShooting()



    def Start(self, duration):
        if not prefs.GetValue('turretsEnabled', 1):
            return 
        shipID = self.ballIDs[0]
        shipBall = sm.StartService('michelle').GetBall(shipID)
        targetID = self.ballIDs[1]
        targetBall = sm.StartService('michelle').GetBall(targetID)
        if targetBall is None:
            return 
        if shipBall is None:
            return 
        if not hasattr(shipBall, 'fitted'):
            sm.StartService('FxSequencer').LogError(self.__guid__ + str(shipBall.id) + ' Turrets: Error! can not fit turrets. No fitted attribute ')
            return 
        if not shipBall.fitted:
            shipBall.FitHardpoints()
        if shipBall.modules is None:
            return 
        self.turret = shipBall.modules.get(self.moduleID)
        if getattr(self, 'turret', None) is None:
            sm.StartService('FxSequencer').LogError('Turret not fitted on shipID', shipID)
            return 
        if hasattr(self.turret, 'SetAmmoColor'):
            self.SetAmmoColor()
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)



    def SetAmmoColor(self):
        if self.otherTypeID is not None:
            self.turret.SetAmmoColorByTypeID(self.otherTypeID)



    def Stop(self):
        if getattr(self, 'turret', None) is None:
            return 
        self.turret.StopShooting()
        self.turret.shooting = 0
        self.turret = None



    def Repeat(self, duration):
        if getattr(self, 'turret', None) is None:
            return 
        shipID = self.ballIDs[0]
        shipBall = sm.StartService('michelle').GetBall(shipID)
        targetID = self.ballIDs[1]
        targetBall = sm.StartService('michelle').GetBall(targetID)
        if targetBall is None:
            self.turret.Rest()
            self.turret.shooting = 0
            return 
        if shipBall is None:
            self.turret.Rest()
            self.turret.shooting = 0
            return 
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)




class Laser(StandardWeapon):
    __guid__ = 'effects.Laser'


class Projectile(StandardWeapon):
    __guid__ = 'effects.ProjectileFired'


class HybridFired(StandardWeapon):
    __guid__ = 'effects.HybridFired'


class ProjectileFiredForEntities(StandardWeapon):
    __guid__ = 'effects.ProjectileFiredForEntities'


class TractorBeam(StandardWeapon):
    __guid__ = 'effects.TractorBeam'


class Salvage(StandardWeapon):
    __guid__ = 'effects.Salvaging'


