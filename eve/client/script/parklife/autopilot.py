import uthread
import trinity
import destiny
import blue
import spaceObject
import base
import uix
import math
import service
import sys

class AutoPilot(service.Service):
    __guid__ = 'svc.autoPilot'
    __exportedcalls__ = {'SetOn': [],
     'SetOff': [],
     'GetState': []}
    __notifyevents__ = ['OnBallparkCall', 'ProcessSessionChange']
    __dependencies__ = ['michelle', 'starmap']

    def __init__(self):
        service.Service.__init__(self)
        self.updateTimer = None
        self.autopilot = 0
        self.ignoreTimerCycles = 0



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.StartTimer()
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        if len(waypoints):
            starmapSvc.SetWaypoints(waypoints)



    def SetOn(self):
        if self.autopilot == 1:
            return 
        self.autopilot = 1
        sm.ScatterEvent('OnAutoPilotOn')
        eve.Message('AutoPilotEnabled')
        self.KillTimer()
        self.StartTimer()
        self.LogNotice('Autopilot Enabled')



    def ProcessSessionChange(self, isremote, session, change):
        self.KillTimer()
        self.ignoreTimerCycles = 3
        self.StartTimer()



    def SetOff(self, reason = ''):
        if self.autopilot == 0:
            self.KillTimer()
            return 
        sm.ScatterEvent('OnAutoPilotOff')
        self.autopilot = 0
        if reason == '  - waypoint reached':
            eve.Message('AutoPilotWaypointReached')
        elif reason == '  - %s' % mls.UI_INFLIGHT_NODESTPATHSET:
            eve.Message('AutoPilotDisabledNoPathSet')
        else:
            eve.Message('AutoPilotDisabled')
        self.LogNotice('Autopilot Disabled', reason)



    def OnBallparkCall(self, functionName, args):
        functions = ['GotoDirection', 'GotoPoint']
        if args[0] != eve.session.shipid:
            return 
        if functionName in functions:
            if functionName == 'GotoDirection' and self.gotoCount > 0:
                self.gotoCount = 0
                self.LogInfo('Autopilot gotocount set to 0')
                return 
            self.SetOff(functionName + str(args))
            self.LogInfo('Autopilot stopped gotocount is ', self.gotoCount)



    def GetState(self):
        return self.autopilot



    def Stop(self, stream):
        self.KillTimer()
        service.Service.Stop(self)



    def KillTimer(self):
        self.updateTimer = None



    def StartTimer(self):
        self.gotoCount = 0
        self.updateTimer = base.AutoTimer(2000, self.Update)



    def Update(self):
        if self.autopilot == 0:
            self.KillTimer()
            return 
        else:
            if self.ignoreTimerCycles > 0:
                self.ignoreTimerCycles = self.ignoreTimerCycles - 1
                return 
            if not eve.session.IsItSafe():
                self.LogInfo('returning as it is not safe')
                return 
            if not eve.session.rwlock.IsCool():
                self.LogInfo("returning as the session rwlock isn't cool")
                return 
            starmapSvc = sm.GetService('starmap')
            waypoints = starmapSvc.GetWaypoints()
            destinationPath = starmapSvc.GetDestinationPath()
            if len(destinationPath) == 0:
                self.SetOff('  - %s' % mls.UI_INFLIGHT_NODESTPATHSET)
                return 
            if destinationPath[0] == None:
                self.SetOff('  - %s' % mls.UI_INFLIGHT_NODESTPATHSET)
                return 
            bp = sm.GetService('michelle').GetBallpark()
            if not bp:
                return 
            if sm.GetService('jumpQueue').IsJumpQueued():
                return 
            ship = bp.GetBall(eve.session.shipid)
            if ship is None:
                return 
            if ship.mode == destiny.DSTBALL_WARP:
                return 
            gateID = None
            gateItem = None
            for ballID in bp.balls.iterkeys():
                slimItem = bp.GetInvItem(ballID)
                if slimItem == None:
                    continue
                if slimItem.groupID == const.groupStargate and destinationPath[0] in map(lambda x: x.locationID, slimItem.jumps):
                    gateID = ballID
                    gateItem = slimItem
                    break

            if gateID is None:
                return 
            theJump = None
            for jump in gateItem.jumps:
                if destinationPath[0] == jump.locationID:
                    theJump = jump
                    break

            if theJump is None:
                return 
            gate = bp.GetBall(gateID)
            if gate is None:
                return 
            jumpToSystem = sm.GetService('map').GetItem(theJump.locationID)
            shipGateDistance = bp.GetSurfaceDist(ship.id, gateID)
            if shipGateDistance < const.maxStargateJumpingDistance:
                if ship.isCloaked:
                    return 
                if eve.session.mutating:
                    self.LogInfo('session is mutating')
                    return 
                if eve.session.changing:
                    self.LogInfo('session is changing')
                    return 
                if bp.solarsystemID != eve.session.solarsystemid:
                    self.LogInfo('bp.solarsystemid is not solarsystemid')
                    return 
                if sm.GetService('michelle').GetRemotePark()._Moniker__bindParams != eve.session.solarsystemid:
                    self.LogInfo('remote park moniker bindparams is not solarsystemid')
                    return 
                try:
                    self.LogNotice('Autopilot jumping from', gateID, 'to', theJump.toCelestialID, '(', jumpToSystem.itemName, ')')
                    sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.GetService('michelle').GetRemotePark().StargateJump, gateID, theJump.toCelestialID, eve.session.shipid)
                    eve.Message('AutoPilotJumping', {'what': jumpToSystem.itemName})
                    self.ignoreTimerCycles = 5
                except UserError as e:
                    if e.msg == 'SystemCheck_JumpFailed_Stuck':
                        self.SetOff()
                        raise 
                    elif e.msg.startswith('SystemCheck_JumpFailed_'):
                        eve.Message(e.msg, e.dict)
                    elif e.msg == 'NotCloseEnoughToJump':
                        park = sm.GetService('michelle').GetRemotePark()
                        park.SetSpeedFraction(1.0)
                        shipui = uicore.layer.shipui
                        if shipui.isopen:
                            shipui.SetSpeed(1.0)
                        park.FollowBall(gateID, 0.0)
                        self.LogWarn("Autopilot: I thought I was close enough to jump, but I wasn't.")
                    sys.exc_clear()
                    self.LogError('Autopilot: jumping to ' + jumpToSystem.itemName + ' failed. Will try again')
                    self.ignoreTimerCycles = 5
                except:
                    sys.exc_clear()
                    self.LogError('Autopilot: jumping to ' + jumpToSystem.itemName + ' failed. Will try again')
                    self.ignoreTimerCycles = 5
                return 
            if shipGateDistance < const.minWarpDistance:
                if ship.mode == destiny.DSTBALL_FOLLOW and ship.followId == gateID:
                    return 
                park = sm.GetService('michelle').GetRemotePark()
                park.SetSpeedFraction(1.0)
                shipui = uicore.layer.shipui
                if shipui.isopen:
                    shipui.SetSpeed(1.0)
                park.FollowBall(gateID, 0.0)
                eve.Message('AutoPilotApproaching')
                self.LogInfo('Autopilot: approaching')
                self.ignoreTimerCycles = 2
                return 
            try:
                sm.GetService('space').WarpDestination(gateID, None, None)
                sm.GetService('michelle').GetRemotePark().WarpToStuffAutopilot(gateID)
                eve.Message('AutoPilotWarpingTo', {'what': jumpToSystem.itemName})
                self.LogInfo('Autopilot: warping to gate')
                self.ignoreTimerCycles = 2
            except:
                sys.exc_clear()
                item = sm.GetService('godma').GetItem(session.shipid)
                if item.warpScrambleStatus > 0:
                    self.SetOff('Autopilot cannot warp while warp scrambled.')
            return 




