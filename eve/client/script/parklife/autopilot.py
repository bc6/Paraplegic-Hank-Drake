import util
import destiny
import base
import service
import sys
import uthread
import blue

class AutoPilot(service.Service):
    __guid__ = 'svc.autoPilot'
    __exportedcalls__ = {'SetOn': [],
     'SetOff': [],
     'GetState': []}
    __notifyevents__ = ['OnBallparkCall', 'OnSessionChanged']
    __dependencies__ = ['michelle', 'starmap']

    def __init__(self):
        service.Service.__init__(self)
        self.updateTimer = None
        self.autopilot = 0
        self.ignoreTimerCycles = 0
        self.approachAndTryTarget = None
        self.warpAndTryTarget = None
        uthread.new(self.UpdateWaypointsThread).context = 'autoPilot::UpdateWaypointsThread'



    def UpdateWaypointsThread(self):
        blue.pyos.synchro.SleepWallclock(2000)
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        if len(waypoints):
            starmapSvc.SetWaypoints(waypoints)



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.StartTimer()



    def SetOn(self):
        if self.autopilot == 1:
            return 
        self.autopilot = 1
        sm.ScatterEvent('OnAutoPilotOn')
        eve.Message('AutoPilotEnabled')
        self.KillTimer()
        self.StartTimer()
        self.LogNotice('Autopilot Enabled')



    def OnSessionChanged(self, isremote, session, change):
        self.KillTimer()
        self.ignoreTimerCycles = 3
        self.StartTimer()
        sm.GetService('starmap').UpdateRoute(fakeUpdate=True)



    def SetOff(self, reason = ''):
        if self.autopilot == 0:
            self.KillTimer()
            return 
        sm.ScatterEvent('OnAutoPilotOff')
        self.autopilot = 0
        if reason == '  - waypoint reached':
            eve.Message('AutoPilotWaypointReached')
        elif reason == '  - no destination path set':
            eve.Message('AutoPilotDisabledNoPathSet')
        else:
            eve.Message('AutoPilotDisabled')
        self.LogNotice('Autopilot Disabled', reason)



    def OnBallparkCall(self, functionName, args):
        functions = ['GotoDirection', 'GotoPoint']
        approachAndTryFunctions = ['GotoDirection',
         'GotoPoint',
         'FollowBall',
         'Orbit',
         'WarpTo']
        warpAndTryFunctions = ['GotoDirection',
         'GotoPoint',
         'FollowBall',
         'Orbit']
        if args[0] != eve.session.shipid:
            return 
        if functionName in approachAndTryFunctions:
            if functionName != 'FollowBall' or self.approachAndTryTarget != args[1]:
                self.AbortApproachAndTryCommand()
        if functionName in warpAndTryFunctions:
            self.AbortWarpAndTryCommand()
        if functionName in functions:
            if functionName == 'GotoDirection' and self.gotoCount > 0:
                self.gotoCount = 0
                self.LogInfo('Autopilot gotocount set to 0')
                return 
            if self.gotoCount == 0:
                waypoints = sm.GetService('starmap').GetWaypoints()
                if waypoints and util.IsStation(waypoints[-1]):
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
            if not session.IsItSafe():
                self.LogInfo('returning as it is not safe')
                return 
            if not session.rwlock.IsCool():
                self.LogInfo("returning as the session rwlock isn't cool")
                return 
            starmapSvc = sm.GetService('starmap')
            destinationPath = starmapSvc.GetDestinationPath()
            if len(destinationPath) == 0:
                self.SetOff('  - no destination path set')
                return 
            if destinationPath[0] == None:
                self.SetOff('  - no destination path set')
                return 
            bp = sm.GetService('michelle').GetBallpark()
            if not bp:
                return 
            if sm.GetService('jumpQueue').IsJumpQueued():
                return 
            ship = bp.GetBall(session.shipid)
            if ship is None:
                return 
            if ship.mode == destiny.DSTBALL_WARP:
                return 
            destID = None
            destItem = None
            for ballID in bp.balls.iterkeys():
                slimItem = bp.GetInvItem(ballID)
                if slimItem == None:
                    continue
                if slimItem.groupID == const.groupStargate and destinationPath[0] in map(lambda x: x.locationID, slimItem.jumps):
                    destID = ballID
                    destItem = slimItem
                    break
                elif destinationPath[0] == slimItem.itemID:
                    destID = ballID
                    destItem = slimItem
                    break

            if destID is None:
                return 
            jumpingToCelestial = not util.IsSolarSystem(destinationPath[0])
            theJump = None
            if not jumpingToCelestial:
                for jump in destItem.jumps:
                    if destinationPath[0] == jump.locationID:
                        theJump = jump
                        break

            if theJump is None and not jumpingToCelestial:
                return 
            approachObject = bp.GetBall(destID)
            if approachObject is None:
                return 
            if jumpingToCelestial:
                jumpToLocationName = cfg.evelocations.Get(destinationPath[0]).name
            else:
                jumpToLocationName = cfg.evelocations.Get(theJump.locationID).name
            shipDestDistance = bp.GetSurfaceDist(ship.id, destID)
            if shipDestDistance < const.maxStargateJumpingDistance and not jumpingToCelestial:
                if ship.isCloaked:
                    return 
                if session.mutating:
                    self.LogInfo('session is mutating')
                    return 
                if session.changing:
                    self.LogInfo('session is changing')
                    return 
                if bp.solarsystemID != session.solarsystemid:
                    self.LogInfo('bp.solarsystemid is not solarsystemid')
                    return 
                if sm.GetService('michelle').GetRemotePark()._Moniker__bindParams != session.solarsystemid:
                    self.LogInfo('remote park moniker bindparams is not solarsystemid')
                    return 
                try:
                    self.LogNotice('Autopilot jumping from', destID, 'to', theJump.toCelestialID, '(', jumpToLocationName, ')')
                    sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.GetService('michelle').GetRemotePark().StargateJump, destID, theJump.toCelestialID, session.shipid)
                    eve.Message('AutoPilotJumping', {'what': jumpToLocationName})
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
                        park.FollowBall(destID, 0.0)
                        self.LogWarn("Autopilot: I thought I was close enough to jump, but I wasn't.")
                    sys.exc_clear()
                    self.LogError('Autopilot: jumping to ' + jumpToLocationName + ' failed. Will try again')
                    self.ignoreTimerCycles = 5
                except:
                    sys.exc_clear()
                    self.LogError('Autopilot: jumping to ' + jumpToLocationName + ' failed. Will try again')
                    self.ignoreTimerCycles = 5
                return 
            if jumpingToCelestial and util.IsStation(destID) and shipDestDistance < const.maxDockingDistance:
                if shipDestDistance > 2500:
                    sm.GetService('audio').SendUIEvent('wise:/msg_AutoPilotApproachingStation_play')
                sm.GetService('menu').Dock(destID)
                return 
            if shipDestDistance < const.minWarpDistance:
                if ship.mode == destiny.DSTBALL_FOLLOW and ship.followId == destID:
                    return 
                park = sm.GetService('michelle').GetRemotePark()
                park.SetSpeedFraction(1.0)
                shipui = uicore.layer.shipui
                if shipui.isopen:
                    shipui.SetSpeed(1.0)
                park.FollowBall(destID, 0.0)
                eve.Message('AutoPilotApproaching')
                if not (jumpingToCelestial and util.IsStation(destID)):
                    sm.GetService('audio').SendUIEvent('wise:/msg_AutoPilotApproaching_play')
                self.LogInfo('Autopilot: approaching')
                self.ignoreTimerCycles = 2
                return 
            try:
                sm.GetService('space').WarpDestination(destID, None, None)
                sm.GetService('michelle').GetRemotePark().WarpToStuffAutopilot(destID)
                eve.Message('AutoPilotWarpingTo', {'what': jumpToLocationName})
                if jumpingToCelestial:
                    if util.IsStation(destID):
                        sm.GetService('audio').SendUIEvent('wise:/msg_AutoPilotWarpingToStation_play')
                    self.LogInfo('Autopilot: warping to celestial object', destID)
                else:
                    sm.GetService('audio').SendUIEvent('wise:/msg_AutoPilotWarpingTo_play')
                    self.LogInfo('Autopilot: warping to gate')
                self.ignoreTimerCycles = 2
            except:
                sys.exc_clear()
                item = sm.GetService('godma').GetItem(session.shipid)
                if item.warpScrambleStatus > 0:
                    self.SetOff('Autopilot cannot warp while warp scrambled.')
            return 



    def WarpAndTryCommand(self, id, cmdMethod, args, interactionRange):
        bp = sm.StartService('michelle').GetRemotePark()
        if not bp:
            return 
        if sm.StartService('space').CanWarp() and self.warpAndTryTarget != id:
            self.approachAndTryTarget = None
            self.warpAndTryTarget = id
            try:
                michelle = sm.StartService('michelle')
                shipBall = michelle.GetBall(session.shipid)
                if shipBall is None:
                    return 
                if shipBall.mode != destiny.DSTBALL_WARP:
                    bp.WarpToStuff('item', id)
                    sm.StartService('space').WarpDestination(id, None, None)
                while self.warpAndTryTarget == id and shipBall.mode != destiny.DSTBALL_WARP:
                    blue.pyos.synchro.SleepWallclock(500)

                while shipBall.mode == destiny.DSTBALL_WARP:
                    blue.pyos.synchro.SleepWallclock(500)

                destBall = michelle.GetBall(id)
                if destBall and self.warpAndTryTarget == id:
                    destBall.GetVectorAt(blue.os.GetSimTime())
                    if destBall.surfaceDist < interactionRange:
                        cmdMethod(*args)

            finally:
                if self.warpAndTryTarget == id:
                    self.warpAndTryTarget = None




    def ApproachAndTryCommand(self, id, cmdMethod, args, interactionRange):
        bp = sm.StartService('michelle').GetRemotePark()
        if not bp:
            return 
        if self.approachAndTryTarget != id and not self.warpAndTryTarget:
            self.warpAndTryTarget = None
            self.approachAndTryTarget = id
            localbp = sm.StartService('michelle').GetBallpark()
            if not localbp:
                return 
            try:
                sm.GetService('menu').Approach(id)
                michelle = sm.StartService('michelle')
                while self.approachAndTryTarget == id:
                    ball = localbp.GetBall(id)
                    if not ball:
                        break
                    ball.GetVectorAt(blue.os.GetSimTime())
                    if ball.surfaceDist < interactionRange:
                        cmdMethod(*args)
                        break
                    blue.pyos.synchro.SleepWallclock(500)


            finally:
                if self.approachAndTryTarget == id:
                    self.approachAndTryTarget = False




    def AbortApproachAndTryCommand(self, nextID = None):
        if nextID != self.approachAndTryTarget:
            self.approachAndTryTarget = None



    def AbortWarpAndTryCommand(self, nextID = None):
        if nextID != self.warpAndTryTarget:
            self.warpAndTryTarget = None




