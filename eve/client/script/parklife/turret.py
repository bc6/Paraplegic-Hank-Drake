import service
import state
import turret

class TurretSvc(service.Service):
    __exportedcalls__ = {}
    __notifyevents__ = ['OnStateChange',
     'OnTarget',
     'OnTargets',
     'OnGodmaItemChange',
     'ProcessShipEffect']
    __dependencies__ = []
    __guid__ = 'svc.turret'
    __servicename__ = 'turret'
    __displayname__ = 'Turret Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting Turret Service')



    def Startup(self):
        pass



    def Stop(self, memStream = None):
        pass



    def OnStateChange(self, itemID, flag, true, *args):
        if flag == state.targeting:
            pass
        if flag != state.activeTarget:
            return 
        targets = sm.GetService('target').GetTargets()
        if len(targets) == 0:
            return 
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        for turretSet in ship.turrets:
            if not turretSet.IsShooting():
                turretSet.SetTarget(eve.session.shipid, itemID)
                turretSet.TakeAim(itemID)




    def OnGodmaItemChange(self, item, change):
        ball = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ball is None:
            return 
        if item.groupID in const.turretModuleGroups:
            turret.TurretSet.FitTurrets(eve.session.shipid, ball.model)



    def OnTargets(self, targets):
        for each in targets:
            self.OnTarget(*each[1:])




    def OnTarget(self, what, tid = None, reason = None):
        targets = sm.GetService('target').GetTargets()
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ship is None:
            return 
        if not hasattr(ship, 'turrets'):
            return 
        for turretSet in ship.turrets:
            turretSet.SetTargetsAvailable(len(targets) != 0)




    def ProcessShipEffect(self, godmaStm, effectState):
        if effectState.effectName == 'online':
            ship = sm.GetService('michelle').GetBall(eve.session.shipid)
            if ship is not None:
                turret = None
                for moduleID in ship.modules:
                    if moduleID == effectState.itemID:
                        turret = ship.modules[moduleID]

                if turret is not None:
                    if effectState.active:
                        turret.Online()
                    else:
                        turret.Offline()




