import uiutil
import uicls
import uiconst
import uthread
import form
import uix
import blue
import trinity
import util
import menu
import sys
import service
import FxSequencer
import moniker
import const
import appUtils
import svc
import destiny
contextFiS = 1
contextIncarna = 2

class EveCommandService(svc.cmd):
    __guid__ = 'svc.eveCmd'
    __displayname__ = 'Command service'
    __replaceservice__ = 'cmd'
    __notifyevents__ = ['OnSessionChanged']
    __categoryToContext__ = {mls.UI_GENERIC_GENERAL: (contextFiS, contextIncarna),
     mls.UI_GENERIC_WINDOW: (contextFiS, contextIncarna),
     mls.UI_GENERIC_COMBAT: (contextFiS,),
     mls.UI_GENERIC_DRONES: (contextFiS,),
     mls.UI_GENERIC_MODULES: (contextFiS,),
     mls.UI_GENERIC_NAVIGATION: (contextFiS,),
     mls.UI_GENERIC_MOVEMENT: (contextIncarna,)}

    def Run(self, memStream = None):
        svc.cmd.Run(self, memStream)
        self.combatFunctionLoaded = None
        self.combatCmdLoaded = None
        self.combatCmdCurrentHasExecuted = False
        self.contextToCommand = {}



    def Reload(self, forceGenericOnly = False):
        svc.cmd.Reload(self, forceGenericOnly)
        change = {}
        self.contextToCommand = {}
        self.LoadAllAccelerators()



    def OnSessionChanged(self, isRemote, sess, change):
        svc.cmd.OnSessionChanged(self, isRemote, sess, change)
        if 'locationid' in change:
            self.LoadAllAccelerators()



    def LoadAllAccelerators(self):
        self.commandMap.UnloadAllAccelerators()
        self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_GENERAL)
        self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_WINDOW)
        if getattr(session, 'locationid', None):
            if util.IsWorldSpace(session.locationid):
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_MOVEMENT)
            elif util.IsStation(session.locationid):
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_MOVEMENT)
            else:
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_COMBAT)
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_DRONES)
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_MODULES)
                self.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_NAVIGATION)



    def GetCategoryContext(self, category):
        return self.__categoryToContext__[category]



    def CheckContextIntersection(self, context1, context2):
        for context in context1:
            if context in context2:
                return True

        return False



    def CheckDuplicateShortcuts(self):
        for cmd in self.defaultShortcutMapping:
            for cmdCheck in self.defaultShortcutMapping:
                if cmdCheck.shortcut:
                    sameName = cmdCheck.name == cmd.name
                    sameShortcut = cmdCheck.shortcut == cmd.shortcut
                    cmdCheckContext = self.__categoryToContext__[cmdCheck.category]
                    cmdContext = self.__categoryToContext__[cmd.category]
                    sameContext = self.CheckContextIntersection(cmdCheckContext, cmdContext)
                    if sameShortcut and sameContext and not sameName:
                        self.LogError('Same default shortcut used for multiple commands:', cmd)





    def SetDefaultShortcutMappingGAME(self):
        ret = []
        c = util.CommandMapping
        CTRL = uiconst.VK_CONTROL
        ALT = uiconst.VK_MENU
        SHIFT = uiconst.VK_SHIFT
        m = [c(self.CmdOverloadLowPowerRack, (CTRL, uiconst.VK_1)),
         c(self.CmdOverloadMediumPowerRack, (CTRL, uiconst.VK_2)),
         c(self.CmdOverloadHighPowerRack, (CTRL, uiconst.VK_3)),
         c(self.CmdReloadAmmo, (CTRL, uiconst.VK_R))]
        for i in xrange(1, 9):
            key = getattr(uiconst, 'VK_F%s' % i)
            m.extend([c(getattr(self, 'CmdActivateHighPowerSlot%s' % i), key),
             c(getattr(self, 'CmdActivateMediumPowerSlot%s' % i), (ALT, key)),
             c(getattr(self, 'CmdActivateLowPowerSlot%s' % i), (CTRL, key)),
             c(getattr(self, 'CmdOverloadHighPowerSlot%s' % i), (SHIFT, key)),
             c(getattr(self, 'CmdOverloadMediumPowerSlot%s' % i), (ALT, SHIFT, key)),
             c(getattr(self, 'CmdOverloadLowPowerSlot%s' % i), (CTRL, SHIFT, key))])

        for cm in m:
            cm.category = mls.UI_GENERIC_MODULES
            ret.append(cm)

        brdcstStr = '%s: ' % mls.UI_FLEET_BROADCAST
        m = [c(self.CmdSelectPrevTarget, (ALT, uiconst.VK_LEFT)),
         c(self.CmdSelectNextTarget, (ALT, uiconst.VK_RIGHT)),
         c(self.CmdZoomIn, uiconst.VK_PRIOR, repeatable=True),
         c(self.CmdZoomOut, uiconst.VK_NEXT, repeatable=True),
         c(self.CmdToggleAutopilot, (CTRL, uiconst.VK_S)),
         c(self.CmdToggleTacticalOverlay, (CTRL, uiconst.VK_D)),
         c(self.CmdDecelerate, uiconst.VK_SUBTRACT, repeatable=True),
         c(self.CmdAccelerate, uiconst.VK_ADD, repeatable=True),
         c(self.CmdStopShip, (CTRL, uiconst.VK_SPACE)),
         c(self.CmdSetShipFullSpeed, (ALT, CTRL, uiconst.VK_SPACE)),
         c(self.CmdToggleShowAllBrackets, (ALT, uiconst.VK_Z)),
         c(self.CmdToggleShowNoBrackets, (ALT, SHIFT, uiconst.VK_Z)),
         c(self.CmdToggleShowSpecialBrackets, (ALT, SHIFT, uiconst.VK_X)),
         c(self.CmdFleetBroadcast_EnemySpotted, uiconst.VK_Z, description=brdcstStr + mls.UI_FLEET_BROADCAST_ENEMYSPOTTED),
         c(self.CmdFleetBroadcast_NeedBackup, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_NEEDBACKUP),
         c(self.CmdFleetBroadcast_HealArmor, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_HEALARMOR),
         c(self.CmdFleetBroadcast_HealShield, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_HEALSHIELD),
         c(self.CmdFleetBroadcast_HealCapacitor, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_HEALCAPACITOR),
         c(self.CmdFleetBroadcast_InPosition, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_INPOSITION),
         c(self.CmdFleetBroadcast_HoldPosition, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_HOLDPOSITION),
         c(self.CmdFleetBroadcast_JumpBeacon, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_JUMPBEACON),
         c(self.CmdFleetBroadcast_Location, None, description=brdcstStr + mls.UI_FLEET_BROADCAST_LOCATION),
         c(self.CmdSendBroadcast_Target, uiconst.VK_X),
         c(self.CmdCycleFleetBroadcastScope, None, description=mls.UI_CMD_CYCLEFLEETBROADCAST)]
        for cm in m:
            cm.category = mls.UI_GENERIC_NAVIGATION
            ret.append(cm)

        m = [c(self.CmdDronesEngage, uiconst.VK_F),
         c(self.CmdDronesReturnAndOrbit, (SHIFT, ALT, uiconst.VK_R)),
         c(self.CmdDronesReturnToBay, (SHIFT, uiconst.VK_R)),
         c(self.CmdToggleAggressivePassive, None),
         c(self.CmdToggleDroneFocusFire, None),
         c(self.CmdToggleFighterAttackAndFollow, None)]
        for cm in m:
            cm.category = mls.UI_GENERIC_DRONES
            ret.append(cm)

        isDungeonMaster = bool(session.role & service.ROLE_CONTENT)
        isElevatedPlayer = bool(session.role & service.ROLEMASK_ELEVATEDPLAYER)
        m = [c(self.CmdPrevStackedWindow, (CTRL, SHIFT, uiconst.VK_PRIOR)),
         c(self.CmdNextStackedWindow, (CTRL, SHIFT, uiconst.VK_NEXT)),
         c(self.CmdPrevTab, (CTRL, uiconst.VK_PRIOR)),
         c(self.CmdNextTab, (CTRL, uiconst.VK_NEXT)),
         c(self.CmdExitStation, None),
         c(self.CmdHideUI, (CTRL, uiconst.VK_F9)),
         c(self.CmdHideCursor, (ALT, uiconst.VK_F9)),
         c(self.OpenDungeonEditor, (CTRL, SHIFT, uiconst.VK_D), enabled=isDungeonMaster),
         c(self.CmdToggleEffects, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_E), description=mls.UI_CMD_DISABLEEFFECTS),
         c(self.CmdToggleEffectTurrets, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_T), description=mls.UI_CMD_DISABLETURRETEFFECTS),
         c(self.CmdToggleCombatView, (CTRL, ALT, uiconst.VK_T), description=mls.UI_CMD_DISABLECOMBATVIEW, enabled=isElevatedPlayer)]
        ret.extend(m)
        if bool(session.role & service.ROLE_CONTENT):
            ret.append(c(self.OpenDungeonEditor, (CTRL, SHIFT, uiconst.VK_D)))
        if bool(session.role & service.ROLEMASK_ELEVATEDPLAYER):
            ret.append(c(self.CmdToggleCombatView, (CTRL, ALT, uiconst.VK_T), description=mls.UI_CMD_DISABLECOMBATVIEW))
        m = [c(self.CmdToggleTargetItem, None),
         c(self.CmdLockTargetItem, CTRL),
         c(self.CmdUnlockTargetItem, (CTRL, SHIFT)),
         c(self.CmdToggleLookAtItem, ALT),
         c(self.CmdApproachItem, uiconst.VK_Q),
         c(self.CmdAlignToItem, uiconst.VK_A),
         c(self.CmdOrbitItem, uiconst.VK_W),
         c(self.CmdKeepItemAtRange, uiconst.VK_E),
         c(self.CmdShowItemInfo, uiconst.VK_T),
         c(self.CmdDockOrJumpOrActivateGate, uiconst.VK_D),
         c(self.CmdWarpToItem, uiconst.VK_S)]
        for cm in m:
            cm.category = mls.UI_GENERIC_COMBAT
            ret.append(cm)

        m = [c(self.CmdOpenNewMessage, None),
         c(self.CmdSetChatChannelFocus, uiconst.VK_SPACE),
         c(self.CmdSetOverviewFocus, (ALT, uiconst.VK_SPACE)),
         c(self.CmdToggleMap, uiconst.VK_F10),
         c(self.OpenAssets, (ALT, uiconst.VK_T)),
         c(self.OpenBrowser, (ALT, uiconst.VK_B)),
         c(self.OpenCalculator, None),
         c(self.OpenCalendar, None),
         c(self.OpenCapitalNavigation, None),
         c(self.OpenCargoHoldOfActiveShip, (ALT, uiconst.VK_C)),
         c(self.OpenCertificatePlanner, None),
         c(self.OpenChannels, None),
         c(self.OpenCharactersheet, (ALT, uiconst.VK_A)),
         c(self.OpenConfigMenu, None),
         c(self.OpenContracts, None),
         c(self.OpenCorpDeliveries, None),
         c(self.OpenCorporationPanel, None),
         c(self.OpenDroneBayOfActiveShip, None),
         c(self.OpenFactories, (ALT, uiconst.VK_S)),
         c(self.OpenFitting, (ALT, uiconst.VK_F)),
         c(self.OpenFleet, None),
         c(self.OpenFpsMonitor, (CTRL, uiconst.VK_F)),
         c(self.OpenHangarFloor, (ALT, uiconst.VK_G)),
         c(self.OpenHelp, uiconst.VK_F12),
         c(self.OpenInsurance, None),
         c(self.OpenJournal, (ALT, uiconst.VK_J)),
         c(self.OpenJukebox, None),
         c(self.OpenLog, None),
         c(self.OpenLpstore, None),
         c(self.OpenMail, (ALT, uiconst.VK_I)),
         c(self.OpenMapBrowser, uiconst.VK_F11),
         c(self.OpenMarket, (ALT, uiconst.VK_R)),
         c(self.OpenMedical, None),
         c(self.OpenMilitia, None),
         c(self.OpenMissions, None),
         c(self.OpenMoonMining, None),
         c(self.OpenNotepad, None),
         c(self.OpenOverviewSettings, None),
         c(self.OpenPeopleAndPlaces, (ALT, uiconst.VK_E)),
         c(self.OpenCharacterCustomization, None),
         c(self.OpenRepairshop, None),
         c(self.OpenReprocessingPlant, None),
         c(self.OpenScanner, (ALT, uiconst.VK_D)),
         c(self.OpenShipConfig, None),
         c(self.OpenShipHangar, (ALT, uiconst.VK_N)),
         c(self.OpenSkillQueueWindow, (ALT, uiconst.VK_X)),
         c(self.OpenSovDashboard, None),
         c(self.OpenStationManagement, None),
         c(self.OpenTutorials, None),
         c(self.OpenWallet, (ALT, uiconst.VK_W)),
         c(self.CmdForceFadeFromBlack, (SHIFT, uiconst.VK_BACK)),
         c(self.OpenAgentFinder, None),
         c(self.OpenStore, None)]
        if bool(session.role & service.ROLE_PROGRAMMER):
            m.append(c(self.OpenUIDebugger, None, description='Open UI Debugger'))
        for cm in m:
            cm.category = mls.UI_GENERIC_WINDOW
            ret.append(cm)

        m = [c(self.CmdMoveForward, uiconst.VK_W),
         c(self.CmdMoveBackward, uiconst.VK_S),
         c(self.CmdMoveLeft, uiconst.VK_A),
         c(self.CmdMoveRight, uiconst.VK_D)]
        for cm in m:
            cm.category = mls.UI_GENERIC_MOVEMENT
            ret.append(cm)

        return ret



    def CmdActivateHighPowerSlot1(self, *args):
        self._cmdshipui(0, 0)



    def CmdActivateHighPowerSlot2(self, *args):
        self._cmdshipui(1, 0)



    def CmdActivateHighPowerSlot3(self, *args):
        self._cmdshipui(2, 0)



    def CmdActivateHighPowerSlot4(self, *args):
        self._cmdshipui(3, 0)



    def CmdActivateHighPowerSlot5(self, *args):
        self._cmdshipui(4, 0)



    def CmdActivateHighPowerSlot6(self, *args):
        self._cmdshipui(5, 0)



    def CmdActivateHighPowerSlot7(self, *args):
        self._cmdshipui(6, 0)



    def CmdActivateHighPowerSlot8(self, *args):
        self._cmdshipui(7, 0)



    def CmdActivateMediumPowerSlot1(self, *args):
        self._cmdshipui(0, 1)



    def CmdActivateMediumPowerSlot2(self, *args):
        self._cmdshipui(1, 1)



    def CmdActivateMediumPowerSlot3(self, *args):
        self._cmdshipui(2, 1)



    def CmdActivateMediumPowerSlot4(self, *args):
        self._cmdshipui(3, 1)



    def CmdActivateMediumPowerSlot5(self, *args):
        self._cmdshipui(4, 1)



    def CmdActivateMediumPowerSlot6(self, *args):
        self._cmdshipui(5, 1)



    def CmdActivateMediumPowerSlot7(self, *args):
        self._cmdshipui(6, 1)



    def CmdActivateMediumPowerSlot8(self, *args):
        self._cmdshipui(7, 1)



    def CmdActivateLowPowerSlot1(self, *args):
        self._cmdshipui(0, 2)



    def CmdActivateLowPowerSlot2(self, *args):
        self._cmdshipui(1, 2)



    def CmdActivateLowPowerSlot3(self, *args):
        self._cmdshipui(2, 2)



    def CmdActivateLowPowerSlot4(self, *args):
        self._cmdshipui(3, 2)



    def CmdActivateLowPowerSlot5(self, *args):
        self._cmdshipui(4, 2)



    def CmdActivateLowPowerSlot6(self, *args):
        self._cmdshipui(5, 2)



    def CmdActivateLowPowerSlot7(self, *args):
        self._cmdshipui(6, 2)



    def CmdActivateLowPowerSlot8(self, *args):
        self._cmdshipui(7, 2)



    def CmdOverloadHighPowerSlot1(self, *args):
        self._cmdoverload(0, 0)



    def CmdOverloadHighPowerSlot2(self, *args):
        self._cmdoverload(1, 0)



    def CmdOverloadHighPowerSlot3(self, *args):
        self._cmdoverload(2, 0)



    def CmdOverloadHighPowerSlot4(self, *args):
        self._cmdoverload(3, 0)



    def CmdOverloadHighPowerSlot5(self, *args):
        self._cmdoverload(4, 0)



    def CmdOverloadHighPowerSlot6(self, *args):
        self._cmdoverload(5, 0)



    def CmdOverloadHighPowerSlot7(self, *args):
        self._cmdoverload(6, 0)



    def CmdOverloadHighPowerSlot8(self, *args):
        self._cmdoverload(7, 0)



    def CmdOverloadMediumPowerSlot1(self, *args):
        self._cmdoverload(0, 1)



    def CmdOverloadMediumPowerSlot2(self, *args):
        self._cmdoverload(1, 1)



    def CmdOverloadMediumPowerSlot3(self, *args):
        self._cmdoverload(2, 1)



    def CmdOverloadMediumPowerSlot4(self, *args):
        self._cmdoverload(3, 1)



    def CmdOverloadMediumPowerSlot5(self, *args):
        self._cmdoverload(4, 1)



    def CmdOverloadMediumPowerSlot6(self, *args):
        self._cmdoverload(5, 1)



    def CmdOverloadMediumPowerSlot7(self, *args):
        self._cmdoverload(6, 1)



    def CmdOverloadMediumPowerSlot8(self, *args):
        self._cmdoverload(7, 1)



    def CmdOverloadLowPowerSlot1(self, *args):
        self._cmdoverload(0, 2)



    def CmdOverloadLowPowerSlot2(self, *args):
        self._cmdoverload(1, 2)



    def CmdOverloadLowPowerSlot3(self, *args):
        self._cmdoverload(2, 2)



    def CmdOverloadLowPowerSlot4(self, *args):
        self._cmdoverload(3, 2)



    def CmdOverloadLowPowerSlot5(self, *args):
        self._cmdoverload(4, 2)



    def CmdOverloadLowPowerSlot6(self, *args):
        self._cmdoverload(5, 2)



    def CmdOverloadLowPowerSlot7(self, *args):
        self._cmdoverload(6, 2)



    def CmdOverloadLowPowerSlot8(self, *args):
        self._cmdoverload(7, 2)



    def CmdOverloadHighPowerRack(self, *args):
        self._cmdoverloadrack('Hi')



    def CmdOverloadMediumPowerRack(self, *args):
        self._cmdoverloadrack('Med')



    def CmdOverloadLowPowerRack(self, *args):
        self._cmdoverloadrack('Lo')



    def CmdSelectPrevTarget(self, *args):
        sm.GetService('target').SelectPrevTarget()
        self.CmdSetOverviewFocus()



    def CmdSelectNextTarget(self, *args):
        sm.GetService('target').SelectNextTarget()
        self.CmdSetOverviewFocus()



    def CmdZoomIn(self, *args):
        self._Zoom(direction=-1)



    def CmdZoomOut(self, *args):
        self._Zoom(direction=1)



    def _Zoom(self, direction):
        camera = sm.GetService('sceneManager').GetRegisteredCamera('default')
        if sm.GetService('planetUI').IsOpen():
            dz = -30 * direction
            sm.GetService('planetUI').planetNav.camera.ManualZoom(dz)
        elif camera is not None and camera.__typename__ == 'EveCamera':
            dz = 0.12 * direction
            camera.Dolly(dz * abs(camera.translationFromParent.z))
            if eve.session.stationid is not None:
                camera.translationFromParent.z = sm.GetService('station').CheckCameraTranslation(camera.translationFromParent.z)
            elif eve.session.solarsystemid is not None:
                camera.translationFromParent.z = sm.GetService('camera').CheckTranslationFromParent(camera.translationFromParent.z)



    def CmdToggleAutopilot(self, *args):
        if session.solarsystemid:
            if sm.GetService('autoPilot').GetState():
                sm.GetService('autoPilot').SetOff()
            else:
                sm.GetService('autoPilot').SetOn()



    def CmdToggleTacticalOverlay(self, *args):
        if session.solarsystemid is not None:
            sm.GetService('tactical').ToggleOnOff()



    def CmdDecelerate(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            rp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(eve.session.shipid)
            if rp is not None and ownBall is not None:
                rp.SetSpeedFraction(min(1.0, ownBall.speedFraction - 0.1))



    def CmdAccelerate(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            rp = sm.GetService('michelle').GetRemotePark()
            bp = sm.GetService('michelle').GetBallpark()
            ownBall = bp.GetBall(eve.session.shipid)
            if rp is not None and ownBall is not None:
                rp.SetSpeedFraction(min(1.0, ownBall.speedFraction + 0.1))



    def CmdStopShip(self, *args):
        if eve.session.shipid and eve.session.solarsystemid:
            sm.GetService('menu').AbortWarpDock()
            if session.IsItSafe():
                bp = sm.GetService('michelle').GetRemotePark()
                if bp and session.IsItSafe():
                    bp.Stop()
            sm.GetService('logger').AddText(mls.UI_INFLIGHT_SHIPSTOPPING, 'notify')
            sm.GetService('gameui').Say(mls.UI_INFLIGHT_SHIPSTOPPING)
            if sm.GetService('autoPilot').GetState():
                sm.GetService('autoPilot').SetOff()
            sm.GetService('menu').CancelWarpDock()



    def CmdSetShipFullSpeed(self, *args):
        bp = sm.GetService('michelle').GetBallpark()
        rbp = sm.GetService('michelle').GetRemotePark()
        if bp is None or rbp is None:
            return 
        ownBall = bp.GetBall(eve.session.shipid)
        if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
            if not sm.GetService('autoPilot').GetState():
                direction = trinity.TriVector(0.0, 0.0, 1.0)
                currentDirection = ownBall.GetQuaternionAt(blue.os.GetTime())
                direction.TransformQuaternion(currentDirection)
                rbp.GotoDirection(direction.x, direction.y, direction.z)
        if rbp is not None:
            rbp.SetSpeedFraction(1.0)
            sm.GetService('logger').AddText('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self._FormatSpeed(ownBall.maxVelocity)), 'notify')
            sm.GetService('gameui').Say('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self._FormatSpeed(ownBall.maxVelocity)))



    def _FormatSpeed(self, speed):
        if speed < 100:
            return '%.1f %s' % (speed, mls.UI_GENERIC_MPERS)
        return '%i %s' % (long(speed), mls.UI_GENERIC_MPERS)



    def CmdToggleShowAllBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            if bracketMgr.ShowingAll():
                bracketMgr.StopShowingAll()
            else:
                bracketMgr.ShowAll()



    def CmdToggleShowNoBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            if bracketMgr.ShowingNone():
                bracketMgr.StopShowingNone()
            else:
                bracketMgr.ShowNone()



    def CmdToggleShowSpecialBrackets(self, *args):
        if session.solarsystemid:
            bracketMgr = sm.GetService('bracket')
            bracketMgr.ToggleShowSpecials()



    def CmdReloadAmmo(self, *args):
        shipui = uicore.layer.shipui
        if shipui.isopen:
            shipui.OnReloadAmmo()



    def _cmdshipui(self, sidx, gidx):
        shipui = uicore.layer.shipui
        if shipui.isopen:
            shipui.OnF(sidx, gidx)



    def _cmdoverload(self, sidx, gidx):
        shipui = uicore.layer.shipui
        if shipui.isopen:
            shipui.OnFKeyOverload(sidx, gidx)



    def _cmdoverloadrack(self, what):
        shipui = uicore.layer.shipui
        if shipui.isopen:
            shipui.ToggleRackOverload(what)



    def CmdQuitGame(self, *args):
        modalWnd = uicore.registry.GetModalWindow()
        if modalWnd and modalWnd.__guid__ == 'form.MessageBox':
            return 
        if uicore.Message('AskQuitGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('tutorial').OnCloseApp()
            self.settings.SaveSettings()
            sm.GetService('clientStatsSvc').OnProcessExit()
            blue.pyos.Quit('User requesting close')



    def CmdLogOff(self, *args):
        modalWnd = uicore.registry.GetModalWindow()
        if modalWnd and modalWnd.__guid__ == 'form.MessageBox':
            return 
        if uicore.Message('AskLogoffGame', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.settings.SaveSettings()
            appUtils.Reboot('Generic Logoff')



    def CmdDronesEngage(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if drones is None:
            return 
        droneIDs = drones.keys()
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            sm.GetService('menu').EngageTarget(droneIDs)



    def CmdDronesReturnAndOrbit(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if not drones:
            return 
        droneIDs = drones.keys()
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnHome(droneIDs)
            sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs and targetID:
                eve.Message('Command', {'command': mls.UI_INFLIGHT_ALLDRONESRETURNINGANDORBITING})



    def CmdDronesReturnToBay(self, *args):
        drones = sm.GetService('michelle').GetDrones()
        if not drones:
            return 
        droneIDs = drones.keys()
        targetID = sm.GetService('target').GetActiveTargetID()
        entity = moniker.GetEntityAccess()
        if entity:
            ret = entity.CmdReturnBay(droneIDs)
            sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
            if droneIDs and targetID:
                eve.Message('Command', {'command': mls.UI_INFLIGHT_ALLDRONESRETURNINGTOBAY})



    def CmdToggleAggressivePassive(self, *args):
        isAggressive = settings.char.ui.Get('droneAggression', cfg.dgmattribs.Get(const.attributeDroneIsAggressive).defaultValue)
        newIsAggressive = (isAggressive + 1) % 2
        droneSettings = {const.attributeDroneIsAggressive: newIsAggressive}
        settings.char.ui.Set('droneAggression', newIsAggressive)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)
        sm.ScatterEvent('OnDroneSettingChanges')



    def CmdToggleDroneFocusFire(self, *args):
        isFocusFire = settings.char.ui.Get('droneFocusFire', cfg.dgmattribs.Get(const.attributeDroneFocusFire).defaultValue)
        newIsFocusFire = (isFocusFire + 1) % 2
        droneSettings = {const.attributeDroneFocusFire: newIsFocusFire}
        settings.char.ui.Set('droneFocusFire', newIsFocusFire)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)
        sm.ScatterEvent('OnDroneSettingChanges')



    def CmdToggleFighterAttackAndFollow(self, *args):
        isFaf = settings.char.ui.Get('fighterAttackAndFollow', cfg.dgmattribs.Get(const.attributeFighterAttackAndFollow).defaultValue)
        newIsFaf = (isFaf + 1) % 2
        droneSettings = {const.attributeFighterAttackAndFollow: newIsFaf}
        settings.char.ui.Set('fighterAttackAndFollow', newIsFaf)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettings)
        sm.ScatterEvent('OnDroneSettingChanges')



    def WinCmdToggleWindowed(self, *args):
        lastTimeToggled = settings.user.ui.Get('LastTimeToggleWindowed', 0)
        if blue.os.GetTime() - lastTimeToggled > 2 * SEC:
            settings.user.ui.Set('LastTimeToggleWindowed', blue.os.GetTime())
            sm.GetService('device').ToggleWindowed()



    def CmdResetMonitor(self, *args):
        sm.GetService('device').ResetMonitor()



    def CmdToggleMap(self, *args):
        if eve.session.charid is not None and not getattr(self, 'loadingCharacterCustomization', False):
            uthread.new(sm.GetService('map').Toggle).context = 'svc.map.Toggle'



    def CmdPrevStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or wnd.sr.stack is None:
            return 
        tabGroup = wnd.sr.stack.sr.tabs.children[0]
        tabGroup.SelectPrev()



    def CmdNextStackedWindow(self, *args):
        wnd = uicore.registry.GetActive()
        if wnd is None or wnd.sr.stack is None:
            return 
        tabGroup = wnd.sr.stack.sr.tabs.children[0]
        tabGroup.SelectNext()



    def CmdPrevTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectPrev()



    def CmdNextTab(self, *args):
        tabGroup = self._GetTabgroup()
        if tabGroup:
            tabGroup.SelectNext()



    def _GetTabgroup(self):
        wnd = uicore.registry.GetActive()
        if not wnd:
            return 
        MAXRECURS = 10
        tabGroup = self._FindTabGroup(wnd.sr.maincontainer, MAXRECURS)
        if not tabGroup and wnd.sr.stack and len(wnd.sr.stack.sr.content.children) > 1:
            tabGroup = self._FindTabGroup(wnd.sr.stack.sr.tabs, MAXRECURS)
        return tabGroup



    def _FindTabGroup(self, parent, maxLevel):
        if isinstance(parent, uicls.TabGroupCore) and not parent.destroyed:
            return parent
        if not hasattr(parent, 'children') or not parent.children or maxLevel == 0:
            return 
        blue.pyos.BeNice()
        for c in parent.children:
            tabGroup = self._FindTabGroup(c, maxLevel - 1)
            if tabGroup:
                return tabGroup




    def CmdExitStation(self, *args):
        if eve.session.stationid and not uicore.registry.GetModalWindow():
            ccLayer = uicore.layer.Get('charactercreation')
            if ccLayer is not None and ccLayer.isopen:
                return 
            sm.GetService('tutorial').ChangeTutorialWndState(visible=False)
            sm.GetService('station').Exit()



    def CmdSetChatChannelFocus(self, *args):
        sm.GetService('focus').SetChannelFocus()



    def CmdSetOverviewFocus(self, *args):
        wnd = sm.GetService('window').GetWindow('overview')
        if wnd:
            uicore.registry.SetFocus(wnd)



    def GetActiveWnd(self, *args):
        all = sm.GetService('window').GetWindows()
        active = uicore.registry.GetActive()
        if active:
            for each in all:
                if each == active:
                    return each
                if uiutil.IsUnder(active, each):
                    return each




    def GetWndMenu(self, *args):
        if uicore.registry.GetModalWindow() or not session.charid:
            return 
        if not getattr(eve, 'chooseWndMenu', None) or eve.chooseWndMenu.destroyed or eve.chooseWndMenu.state == uiconst.UI_HIDDEN:
            menu.KillAllMenus()
            if sm.GetService('window').GetWindow('CtrlTabWindow') is not None:
                sm.GetService('window').GetWindow('CtrlTabWindow').SelfDestruct()
            mv = sm.GetService('window').GetWindow('CtrlTabWindow', create=1, decoClass=form.CtrlTabWindow)
            mv.left = (uicore.desktop.width - mv.width) / 2
            mv.top = (uicore.desktop.height - mv.height) / 2
            eve.chooseWndMenu = mv
        if uix.GetInflightNav(0):
            uix.GetInflightNav(0).CloseZoomCursor()
        return eve.chooseWndMenu



    def CmdFleetBroadcast_EnemySpotted(self):
        sm.GetService('fleet').SendBroadcast_EnemySpotted()



    def CmdFleetBroadcast_NeedBackup(self):
        sm.GetService('fleet').SendBroadcast_NeedBackup()



    def CmdFleetBroadcast_HealArmor(self):
        sm.GetService('fleet').SendBroadcast_HealArmor()



    def CmdFleetBroadcast_HealShield(self):
        sm.GetService('fleet').SendBroadcast_HealShield()



    def CmdFleetBroadcast_HealCapacitor(self):
        sm.GetService('fleet').SendBroadcast_HealCapacitor()



    def CmdFleetBroadcast_InPosition(self):
        sm.GetService('fleet').SendBroadcast_InPosition()



    def CmdFleetBroadcast_HoldPosition(self):
        sm.GetService('fleet').SendBroadcast_HoldPosition()



    def CmdFleetBroadcast_JumpBeacon(self):
        sm.GetService('fleet').SendBroadcast_JumpBeacon()



    def CmdFleetBroadcast_Location(self):
        sm.GetService('fleet').SendBroadcast_Location()



    def OpenCapitalNavigation(self, *args):
        if eve.session.shipid:
            wnd = sm.GetService('window').GetWindow('capitalnav', decoClass=form.CapitalNav, create=1, maximize=1)



    def OpenMonitor(self, *args):
        sm.GetService('monitor').Show()



    def OpenFpsMonitor(self, *args):
        for each in uicore.layer.abovemain.children:
            if each.name == 'fpsmonitor':
                each.Close()
                break
        else:
            uicls.FpsMonitor(name='fpsmonitor', parent=uicore.layer.abovemain, align=uiconst.TOPLEFT, idx=0)




    def OpenConfigMenu(self, *args):
        sysMenu = uicore.layer.systemmenu
        if sysMenu.isopen:
            uthread.new(sysMenu.CloseMenu)
        else:
            sys.OpenView()



    def OpenMail(self, *args):
        if session.charid:
            wnd = sm.GetService('mailSvc').GetMailWindow()
            if wnd:
                wnd.Maximize()



    def OpenAgentFinder(self, *args):
        if session.charid:
            wnd = sm.GetService('window').GetWindow('AgentFinderWnd')
            if wnd:
                wnd.Maximize()
            else:
                sm.GetService('window').GetWindow('AgentFinderWnd', create=1, decoClass=form.AgentFinderWnd)



    def CmdOpenNewMessage(self, *args):
        if session.charid:
            sm.GetService('mailSvc').SendMsgDlg()



    def OpenWallet(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('wallet').Show()



    def OpenCorporationPanel(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('corpui').Show()



    def OpenCorporationPanel_RecruitmentPane(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('corpui').Show('recruitment')



    def OpenAssets(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('assets').Show()



    def OpenChannels(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('channels').Show()



    def OpenJournal(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('journal').Show()



    def OpenJukebox(self, *args):
        if not sm.GetService('audio').IsActivated():
            eve.Message('UnableToOpenJukebox')
            return 
        wnd = sm.GetService('window').GetWindow('jukebox', decoClass=form.jukebox, create=1, maximize=1)



    def OpenCertificatePlanner(self, *args):
        if session.charid:
            wnd = sm.GetService('certificates').OpenCertificateWindow()



    def OpenSkillQueueWindow(self, *args):
        if session.charid:
            wnd = sm.GetService('window').GetWindow('trainingqueue', create=1, decoClass=form.SkillQueue)
            wnd.Maximize()



    def OpenEveMenu(self, *args):
        sm.GetService('neocomNew').ToggleEveMenu()



    def OpenLog(self, *args):
        uthread.new(self._EveCommandService__OpenLog_thread).context = 'cmd.OpenLog'



    def __OpenLog_thread(self, *args):
        sm.GetService('logger').Show()



    def OpenDroneBayOfActiveShip(self, *args):
        if eve.session.shipid and eve.session.stationid:
            uthread.new(self._EveCommandService__OpenDroneBayOfActiveShip_thread).context = 'cmd.OpenDroneBayOfActiveShip'



    def __OpenDroneBayOfActiveShip_thread(self, *args):
        if eve.session.shipid and eve.session.stationid:
            name = cfg.evelocations.Get(eve.session.shipid).name
            sm.GetService('window').OpenDrones(eve.session.shipid, name, "%s's drone bay" % name)



    def OpenCargoHoldOfActiveShip(self, *args):
        if eve.session.shipid:
            uthread.new(self._EveCommandService__OpenCargoHoldOfActiveShip_thread).context = 'cmd.OpenCargoHoldOfActiveShip'



    def __OpenCargoHoldOfActiveShip_thread(self, *args):
        if eve.session.shipid:
            wnd = sm.GetService('window').GetWindow('shipCargo_%s' % eve.session.shipid)
            if wnd:
                wnd.Maximize()
            else:
                shipName = cfg.evelocations.Get(eve.session.shipid).name
                sm.GetService('window').OpenCargo(eve.session.shipid, shipName, '%s%s %s' % (shipName, mls.AGT_AGENTMGR_FORMATMESSAGE_APPEND_APOSTROPHE_AND_S, mls.UI_GENERIC_CARGO))



    def OpenCharactersheet(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('charactersheet').Show()



    def OpenFleet(self, *args):
        wnd = sm.GetService('window').GetWindow('fleetwindow', create=0, decoClass=form.FleetWindow, maximize=1)
        if not wnd:
            sm.GetService('window').GetWindow('fleetwindow', create=1, decoClass=form.FleetWindow, maximize=1)



    def OpenSovDashboard(self, solarSystemID = None):
        wnd = sm.GetService('window').GetWindow('sovOverview', decoClass=form.SovereigntyOverviewWnd, create=0)
        if not wnd:
            wnd = sm.GetService('window').GetWindow('sovOverview', decoClass=form.SovereigntyOverviewWnd, create=1)
        if wnd is not None and not wnd.destroyed:
            if solarSystemID:
                regionID = sm.GetService('map').GetRegionForSolarSystem(solarSystemID)
                constellationID = sm.GetService('map').GetConstellationForSolarSystem(solarSystemID)
                wnd.SetLocation(solarSystemID, constellationID, regionID)
            wnd.Maximize()



    def OpenPeopleAndPlaces(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('addressbook').Show()



    def OpenHelp(self, *args):
        if eve.session.charid:
            wnd = sm.GetService('window').GetWindow('help', decoClass=form.HelpWindow, maximize=1, create=1)
            if wnd:
                wnd.sr.mainTabs.ShowPanelByName('Support')



    def OpenStationManagement(self, *args):
        if eve.session.solarsystemid2:
            wnd = sm.GetService('window').GetWindow('StationManagement', maximize=1)
            if not wnd:
                form.StationManagement().Startup()



    def OpenScanner(self, *args):
        if eve.session.solarsystemid:
            uthread.new(self._EveCommandService__OpenScanner_thread).context = 'cmd.OpenScanner'



    def __OpenScanner_thread(self, *args):
        if eve.session.solarsystemid:
            wnd = sm.GetService('window').GetWindow('scanner', showIfInStack=False)
            if wnd is not None and not wnd.destroyed:
                if wnd.IsMinimized():
                    wnd.Maximize()
                elif wnd.IsCollapsed():
                    wnd.Expand()
                else:
                    wnd.CloseX()
            else:
                sm.GetService('window').GetWindow('scanner', create=1, decoClass=form.Scanner)



    def OpenMapBrowser(self, locationID = None):
        if eve.session.solarsystemid2:
            wnd = sm.GetService('window').GetWindow('mapbrowser')
            if wnd and not wnd.destroyed:
                if locationID is None:
                    if wnd.state == uiconst.UI_HIDDEN:
                        wnd.Show()
                    else:
                        wnd.Hide()
                elif wnd.state == uiconst.UI_HIDDEN:
                    wnd.Show()
                wnd.DoLoad(locationID)
                return 
            sm.GetService('window').GetWindow('mapbrowser', 1, decoClass=form.MapBrowserWnd, locationID=locationID)



    def OpenHangarFloor(self, *args):
        if eve.session.stationid is None:
            return 
        if eve.rookieState is None and settings.user.windows.Get('dockshipsanditems', 0):
            lobby = sm.GetService('station').GetLobby()
            if lobby:
                lobby.ShowItems()
            return 
        sm.GetService('window').GetWindow('hangarFloor', create=True, maximize=True, decoClass=form.ItemHangar)



    def OpenShipHangar(self, maximizeWindow = 1, *args):
        if eve.session.stationid is None:
            return 
        if eve.rookieState is None and settings.user.windows.Get('dockshipsanditems', 0):
            lobby = sm.GetService('station').GetLobby()
            if lobby:
                lobby.ShowShips()
            return 
        sm.GetService('window').GetWindow('shipHangar', create=True, maximize=maximizeWindow, decoClass=form.ShipHangar, showIfInStack=maximizeWindow)



    def OpenCalculator(self, *args):
        sm.GetService('window').GetWindow('calculator', decoClass=form.Calculator, maximize=1, create=1)



    def OpenOverviewSettings(self, *args):
        sm.GetService('window').GetWindow('overviewsettings', decoClass=form.OverviewSettings, maximize=1, create=1)



    def OpenCorpDeliveries(self, *args):
        deliveryRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        if eve.session.corprole & deliveryRoles == 0:
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED14})
        if eve.session.stationid:
            t = uthread.new(self._EveCommandService__OpenCorpDeliveries_thread)
            t.context = 'lobby::OpenCorpDeliveries'



    def __OpenCorpDeliveries_thread(self, *args):
        if eve.session.stationid:
            wnd = sm.GetService('window').GetWindow('corpMarketHangar', create=1, maximize=1, decoClass=form.CorpMarketHangar, prefsName='container')



    def OpenBrowser(self, url = None, windowName = 'virtualbrowser', args = {}, data = None, newTab = False):
        if not hasattr(eve.session, 'charid') or eve.session.charid is None:
            if url is not None and url != 'home' and (url.startswith('http://') or url.startswith('https://')):
                blue.os.ShellExecute(url)
                return 
        w = sm.GetService('window').GetWindow(windowName, decoClass=form.EveBrowserWindow, maximize=1, create=0)
        if w is None:
            w = sm.GetService('window').GetWindow(windowName, decoClass=form.EveBrowserWindow, maximize=1, create=1, initialUrl=url)
        elif url:
            if url == 'home':
                uthread.new(w.GoHome)
            elif newTab:
                uthread.new(w.AddTab, url)
            else:
                uthread.new(w.BrowseTo, url, args=args, data=data)
        return w



    def OpenNotepad(self, *args):
        sm.GetService('notepad').Show()



    def OpenMoonMining(self, id = None):
        bp = sm.GetService('michelle').GetBallpark()
        if not id:
            for itemID in bp.slimItems:
                if bp.slimItems[itemID].groupID == const.groupControlTower:
                    id = bp.slimItems[itemID]
                    break

        if not id:
            return 
        sm.GetService('window').GetWindow('moon', decoClass=form.MoonMining, slimItem=id, maximize=1, create=1)



    def OpenShipConfig(self, id = None):
        if session.shipid is not None and session.solarsystemid is not None:
            ship = sm.GetService('godma').GetItem(session.shipid)
            if bool(sm.GetService('godma').GetType(ship.typeID).hasShipMaintenanceBay):
                sm.GetService('window').GetWindow('shipconfig', decoClass=form.ShipConfig, maximize=1, create=1)



    def OpenTutorials(self, *args):
        if eve.session.charid:
            wnd = sm.GetService('window').GetWindow('help', decoClass=form.HelpWindow, maximize=1, create=1)
            if wnd:
                wnd.sr.mainTabs.ShowPanelByName('Tutorials')



    def OpenMarket(self, *args):
        wnd = sm.GetService('window').GetWindow('market', decoClass=form.RegionalMarket, maximize=1, create=1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def OpenContracts(self, *args):
        sm.GetService('contracts').Show()



    def OpenFactories(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('manufacturing').Show()



    def OpenCorporationPanel_Planets(self, *args):
        if eve.session.solarsystemid2:
            sm.GetService('manufacturing').Show(panelName=mls.UI_GENERIC_PLANETS)



    def OpenFitting(self, *args):
        if getattr(eve.session, 'shipid', None) is None:
            uicore.Message('CannotPerformActionWithoutShip')
        else:
            wnd = sm.GetService('window').GetWindow('fitting')
            if wnd:
                if wnd.IsMinimized():
                    wnd.Maximize()
                else:
                    wnd.SelfDestruct()
            else:
                sm.GetService('window').GetWindow('fitting', decoClass=form.FittingWindow, create=1, maximize=1)



    def OpenMedical(self, *args):
        if eve.session.stationid:
            if eve.stationItem.serviceMask & const.stationServiceCloning == const.stationServiceCloning or eve.stationItem.serviceMask & const.stationServiceSurgery == const.stationServiceSurgery or eve.stationItem.serviceMask & const.stationServiceDNATherapy == const.stationServiceDNATherapy:
                sm.GetService('window').GetWindow('medical', decoClass=form.MedicalWindow, create=1, maximize=1)



    def OpenRepairshop(self, *args):
        if eve.session.stationid:
            if eve.stationItem.serviceMask & const.stationServiceRepairFacilities == const.stationServiceRepairFacilities:
                sm.GetService('window').GetWindow('repairshop', decoClass=form.RepairShopWindow, create=1, maximize=1)



    def OpenInsurance(self, *args):
        if eve.session.stationid:
            if eve.stationItem.serviceMask & const.stationServiceInsurance == const.stationServiceInsurance:
                sm.GetService('window').GetWindow('insurance', decoClass=form.InsuranceWindow, create=1, maximize=1)



    def OpenMissions(self, charID = None):
        if eve.session.stationid:
            if eve.stationItem.serviceMask & const.stationServiceBountyMissions == const.stationServiceBountyMissions or eve.stationItem.serviceMask & const.stationServiceAssassinationMissions == const.stationServiceAssassinationMissions:
                wnd = sm.GetService('window').GetWindow('missions', decoClass=form.BountyWindow, create=1, maximize=1)
                if wnd and charID:
                    wnd.PlaceBountyExt(charID)



    def OpenMilitia(self, *args):
        if sm.StartService('facwar').CheckStationElegibleForMilitia():
            sm.GetService('window').GetWindow('militia', decoClass=form.MilitiaWindow, create=1, maximize=1)



    def OpenReprocessingPlant(self, items = None, outputOwner = None, outputFlag = None):
        if getattr(eve.session, 'shipid', None) is None:
            uicore.Message('CannotPerformActionWithoutShip')
        elif eve.session.stationid:
            if eve.stationItem.serviceMask & const.stationServiceReprocessingPlant == const.stationServiceReprocessingPlant:
                sm.GetService('window').GetWindow('reprocessing', create=1, maximize=1, decoClass=form.ReprocessingDialog, items=items, outputOwner=outputOwner, outputFlag=outputFlag)



    def OpenLpstore(self, *args):
        if eve.session.stationid:
            corpID = eve.stationItem.ownerID
            if util.IsNPC(corpID):
                sm.GetService('lpstore').OpenLPStore(corpID)



    def OpenCharacterCustomization(self, *args):
        if getattr(sm.GetService('map'), 'busy', False):
            return 
        if sm.GetService('cc').NoExistingCustomization():
            raise UserError('CantRecustomizeCharacterWithoutDoll')
        if session.stationid:
            try:
                self.loadingCharacterCustomization = True
                if sm.GetService('planetUI').IsOpen():
                    exitPI = sm.GetService('planetUI').Close()
                    if not exitPI:
                        return 
                if sm.GetService('map').IsOpen():
                    sm.GetService('map').Close()
                sm.GetService('gameui').GoCharacterCreationCurrentCharacter()

            finally:
                self.loadingCharacterCustomization = False




    def OpenStore(self, *args):
        sm.GetService('store').CheckStoreOpen()
        if session.stationid2:
            sm.GetService('window').GetWindow('virtualGoodsStore', decoClass=form.VirtualGoodsStore, create=1, maximize=1)



    def OpenCalendar(self, *args):
        sm.GetService('neocom').BlinkOff('clock')
        if session.charid:
            wnd = sm.GetService('window').GetWindow('calendar', create=1, decoClass=form.eveCalendarWnd)
            if wnd:
                wnd.Maximize()



    def OpenAuraInteraction(self, *args):
        agentService = sm.GetService('agents')
        auraID = agentService.GetAuraAgentID()
        agentService.InteractWith(auraID)



    def CmdHideUI(self, force = 0):
        sys = uicore.layer.systemmenu
        if sys.isopen and not force:
            return 
        if eve.hiddenUIState:
            self.ShowUI()
            return 
        sm.GetService('tutorial').ChangeTutorialWndState(visible=0)
        sm.GetService('neocom').UpdateWindowPush(None)
        layersToHide = ('main', 'tabs', 'login', 'intro', 'charsel', 'shipui', 'bracket', 'target', 'tactical', 'neocom')
        hiddenUIState = []
        for each in layersToHide:
            layer = uicore.layer.Get(each)
            if layer.state == uiconst.UI_HIDDEN:
                continue
            layer.state = uiconst.UI_HIDDEN
            hiddenUIState.append(each)

        sm.ScatterEvent('OnHideUI')
        eve.hiddenUIState = hiddenUIState



    def ShowUI(self, *args):
        if eve.hiddenUIState:
            for each in eve.hiddenUIState:
                layer = uicore.layer.Get(each)
                layer.state = uiconst.UI_PICKCHILDREN

        sm.GetService('tutorial').ChangeTutorialWndState(visible=1)
        eve.hiddenUIState = None
        sm.GetService('neocom').UpdateWindowPush(None)
        sm.ScatterEvent('OnShowUI')



    def IsUIHidden(self, *args):
        return bool(eve.hiddenUIState)



    def CmdHideCursor(self, *args):
        uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)



    def OpenDungeonEditor(self, *args):
        if session.solarsystemid and eve.session.role & service.ROLE_CONTENT:
            sm.GetService('window').GetWindow('dungeoneditor', create=1, decoClass=form.DungeonEditor)
            if '/jessica' in blue.pyos.GetArg():
                sm.StartService('window').GetWindow('dungeonObjectProperties', create=1, decoClass=form.DungeonObjectProperties)
                import panel
                panel.LoadDungeonListViewer()



    def OpenUIDebugger(self, *args):
        wnd = sm.GetService('window').GetWindow('UIDebugger')
        if wnd:
            wnd.CloseX()
        else:
            sm.GetService('window').GetWindow('UIDebugger', create=1)



    def CmdToggleEffects(self, *args):
        candidateEffects = []
        for guid in FxSequencer.fxGuids:
            if guid not in FxSequencer.fxTurretGuids and guid not in FxSequencer.fxProtectedGuids:
                candidateEffects.append(guid)

        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if len(candidateEffects) > 0:
            if candidateEffects[0] in disabledGuids:
                settings.user.ui.Set('effectsEnabled', 1)
                sm.GetService('FxSequencer').EnableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - On'})
            else:
                settings.user.ui.Set('effectsEnabled', 0)
                sm.GetService('FxSequencer').DisableGuids(candidateEffects)
                uicore.Message('CustomNotify', {'notify': 'All effects - Off'})



    def CmdToggleEffectTurrets(self, *args):
        disabledGuids = sm.GetService('FxSequencer').GetDisabledGuids()
        if FxSequencer.fxTurretGuids[0] in disabledGuids:
            settings.user.ui.Set('turretsEnabled', 1)
            sm.GetService('FxSequencer').EnableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - On'})
        else:
            settings.user.ui.Set('turretsEnabled', 0)
            sm.GetService('FxSequencer').DisableGuids(FxSequencer.fxTurretGuids)
            uicore.Message('CustomNotify', {'notify': 'All Turret effects - Off'})



    def CmdToggleCombatView(self, *args):
        if eve.session.solarsystemid and eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            sm.GetService('target').ToggleViewMode()



    def CmdCycleFleetBroadcastScope(self, *args):
        sm.GetService('fleet').CycleBroadcastScope()



    def CmdToggleTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleTargetItem')
        self.LoadCombatCommand(sm.GetService('target').ToggleLockTarget, cmd)



    def CmdLockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdLockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').TryLockTarget, cmd)



    def CmdUnlockTargetItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdUnlockTargetItem')
        self.LoadCombatCommand(sm.GetService('target').UnlockTarget, cmd)



    def CmdToggleLookAtItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleLookAtItem')
        self.LoadCombatCommand(sm.GetService('menu').ToggleLookAt, cmd)



    def CmdApproachItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdApproachItem')
        self.LoadCombatCommand(sm.GetService('menu').Approach, cmd)



    def CmdAlignToItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdAlignToItem')
        self.LoadCombatCommand(sm.GetService('menu').AlignTo, cmd)



    def CmdOrbitItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdOrbitItem')
        self.LoadCombatCommand(sm.GetService('menu').Orbit, cmd)



    def CmdKeepItemAtRange(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdKeepItemAtRange')
        self.LoadCombatCommand(sm.GetService('menu').KeepAtRange, cmd)



    def CmdShowItemInfo(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdShowItemInfo')
        self.LoadCombatCommand(sm.GetService('menu').ShowInfoForItem, cmd)



    def CmdDockOrJumpOrActivateGate(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdDockOrJumpOrActivateGate')
        self.LoadCombatCommand(sm.GetService('menu').DockOrJumpOrActivateGate, cmd)



    def CmdWarpToItem(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdWarpToItem')
        self.LoadCombatCommand(sm.GetService('menu').WarpToItem, cmd)



    def CmdSendBroadcast_Target(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdSendBroadcast_Target')
        self.LoadCombatCommand(sm.GetService('fleet').SendBroadcast_Target, cmd)



    def LoadCombatCommand(self, function, cmd):
        if not session.solarsystemid:
            return 
        sm.GetService('ui').SetFreezeOverview(freeze=True)
        self.combatFunctionLoaded = function
        self.combatCmdLoaded = cmd
        uicore.event.RegisterForTriuiEvents((uiconst.UI_KEYUP, uiconst.UI_KEYDOWN, uiconst.UI_ACTIVE), self.CombatKeyUnloadListener)
        delayMs = 300
        for key in cmd.shortcut:
            if key not in uiconst.MODKEYS:
                delayMs = 0
                break

        sm.GetService('space').Indicate(cmd.GetDescription(), '<center>%s' % mls.UI_CMD_CLICKTARGET, delayMs)



    def UnloadCombatCommand(self):
        uthread.new(self._UnloadCombatCommand)



    def _UnloadCombatCommand(self):
        sm.GetService('space').Indicate(None, None)
        sm.GetService('ui').SetFreezeOverview(freeze=False)
        self.combatFunctionLoaded = None
        self.combatCmdCurrentHasExecuted = False



    def CombatKeyUnloadListener(self, wnd, eventID, keyChange):
        if eventID == uiconst.UI_ACTIVE:
            self.UnloadCombatCommand()
            return 
        (vk, id,) = keyChange
        if vk not in self.combatCmdLoaded.shortcut:
            self.UnloadCombatCommand()
            return 
        for key in self.combatCmdLoaded.shortcut:
            if not uicore.uilib.Key(key):
                self.UnloadCombatCommand()
                return 

        return True



    def ExecuteCombatCommand(self, itemID, eventID):
        if itemID is None or self.combatFunctionLoaded is None:
            return 
        if eventID == uiconst.UI_KEYUP and self.combatCmdCurrentHasExecuted:
            self.UnloadCombatCommand()
            return 
        self.combatCmdCurrentHasExecuted = True
        uthread.new(self.combatFunctionLoaded, itemID)



    def CmdForceFadeFromBlack(self, *args):
        loadSvc = sm.GetService('loading')
        if loadSvc.IsLoading():
            loadSvc.FadeFromBlack(100)



    def CmdMoveForward(self, *args):
        return self._UpdateMovement(const.MOVDIR_FORWARD)



    def CmdMoveBackward(self, *args):
        return self._UpdateMovement(const.MOVDIR_BACKWARD)



    def CmdMoveLeft(self, *args):
        return self._UpdateMovement(const.MOVDIR_LEFT)



    def CmdMoveRight(self, *args):
        return self._UpdateMovement(const.MOVDIR_RIGHT)



    def _UpdateMovement(self, direction):
        if uicore.layer.charcontrol.isopen:
            sm.GetService('navigation').UpdateMovement(direction)
        return False



    def Reset(self, resetKey):
        if resetKey == 'windows':
            sm.GetService('window').ResetAll()
        elif resetKey == 'window color':
            sm.GetService('window').ResetWindowColors()
        elif resetKey == 'clear cache':
            sm.GetService('gameui').ClearCacheFiles()
        elif resetKey == 'clear iskspammers':
            try:
                delattr(sm.GetService('LSC'), 'spammerList')
            except:
                sys.exc_clear()
        elif resetKey == 'clear settings':
            sm.GetService('gameui').ClearSettings()
        elif resetKey == 'clear mail':
            sm.GetService('mailSvc').ClearMailCache()
        elif resetKey == 'jukebox playlist':
            sm.GetService('jukebox').ResetPlaylist()



    def OnEsc(self, *args):
        if len(uicore.layer.menu.children):
            uicore.layer.menu.Flush()
            return 1
        modalResult = uicore.registry.GetModalResult(uiconst.ID_CANCEL, 'btn_cancel')
        if modalResult is not None:
            uicore.registry.GetModalWindow().SetModalResult(modalResult)
            return 1
        if uicore.layer.loading.state == uiconst.UI_NORMAL:
            uthread.new(sm.GetService('loading').HideAllLoad)
            return 
        intro = uicore.layer.intro
        if intro.isopen:
            intro.OnEsc()
            return 
        login = uicore.layer.login
        if login.isopen:
            login.OnEsc()
            return 
        sys = uicore.layer.systemmenu
        if sys.isopen:
            sm.GetService('uipointerSvc').ShowPointer()
            uthread.new(sys.CloseMenu)
        else:
            sm.GetService('uipointerSvc').HidePointer()
            uthread.new(sys.OpenView)



    def OnTab(self):
        oldfoc = uicore.registry.GetFocus()
        if oldfoc is None or oldfoc in (uicore.desktop, uicore.layer.charcontrol):
            prestate = getattr(uicore, 'toggleState', None)
            if prestate:
                for windowID in prestate:
                    wnd = uicore.registry.GetWindow(windowID)
                    if wnd and (getattr(wnd, '_collapsed', 0) or getattr(wnd, 'collapsed', 0)):
                        wnd.Expand()

                uicore.toggleState = None
                return 
            state = []
            wnds = uicore.registry.GetValidWindows(floatingOnly=True)
            for wnd in wnds:
                if not getattr(wnd, 'windowID', None):
                    continue
                if not (getattr(wnd, '_collapsed', 0) or getattr(wnd, 'collapsed', 0)):
                    windowID = wnd.windowID
                    wnd.Collapse()
                    state.append(windowID)

            if not state:
                for wnd in wnds:
                    if getattr(wnd, '_collapsed', 0) or getattr(wnd, 'collapsed', 0):
                        wnd.Expand()

            uicore.toggleState = state
            if state:
                return 
        uicore.registry.FindFocus([1, -1][uicore.uilib.Key(uiconst.VK_SHIFT)])



    def MapCmd(self, cmdname, context):
        self.commandMap.UnloadAllAccelerators()
        wnd = sm.GetService('window').GetWindow('MapCmdWindow', create=1, cmdname=cmdname)
        modalResult = wnd.ShowModal()
        self.LoadAllAccelerators()
        if modalResult == 1:
            retval = wnd.result
            shortcut = retval['shortcut']
        else:
            return 
        errorMsg = self.MapCmdErrorCheck(cmdname, shortcut, context)
        if errorMsg:
            eve.Message('CustomInfo', {'info': errorMsg})
            return 
        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing is not None:
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            if alreadyUsingContext not in self.contextToCommand:
                self.contextToCommand[alreadyUsingContext] = {}
            self.contextToCommand[alreadyUsingContext][shortcut] = alreadyUsing
        self.commandMap.RemapCommand(cmdname, shortcut)
        if context not in self.contextToCommand:
            self.contextToCommand[context] = {}
        self.ClearContextToCommandMapping(context, cmdname)
        self.contextToCommand[context][shortcut] = self.commandMap.GetCommandByName(cmdname)
        sm.ScatterEvent('OnMapShortcut', cmdname, shortcut)



    def ClearContextToCommandMapping(self, context, cmdname):
        toDeleteShortcut = None
        for (shortcutKey, command,) in self.contextToCommand[context].iteritems():
            if command.name == cmdname:
                toDeleteShortcut = shortcutKey

        if toDeleteShortcut is not None:
            del self.contextToCommand[context][toDeleteShortcut]



    def MapCmdErrorCheck(self, cmdname, shortcut, context):
        if not shortcut:
            return mls.UI_GENERIC_MAPKEYERROR2
        for key in shortcut:
            keyName = self.GetKeyNameFromVK(key)
            if not getattr(uiconst, 'VK_%s' % keyName.upper(), None):
                eve.Message('UnknownKey', {'key': keyName})
                return 

        alreadyUsing = self.commandMap.GetCommandByShortcut(shortcut)
        if alreadyUsing:
            cmdEdit = self.commandMap.GetCommandByName(cmdname)
            alreadyUsingContext = self.__categoryToContext__[alreadyUsing.category]
            cmdEditContext = self.__categoryToContext__[cmdEdit.category]
            sameContext = self.CheckContextIntersection(alreadyUsingContext, cmdEditContext)
            if sameContext and alreadyUsing.name != cmdname:
                descString = '%s/%s' % (alreadyUsing.category, alreadyUsing.GetDescription())
                return mls.UI_GENERIC_MAPKEYERROR3 % {'cmd': alreadyUsing.GetShortcutAsString(),
                 'func': descString}
        if context in self.contextToCommand and shortcut in self.contextToCommand[context]:
            alreadyUsing = self.contextToCommand[context][shortcut]
            descString = '%s/%s' % (alreadyUsing.category, alreadyUsing.GetDescription())
            return mls.UI_GENERIC_MAPKEYERROR3 % {'cmd': alreadyUsing.GetShortcutAsString(),
             'func': descString}
        return ''



    def ClearMappedCmd(self, cmdname, showMsg = 1):
        command = self.commandMap.GetCommandByName(cmdname)
        context = self.__categoryToContext__[command.category]
        if context in self.contextToCommand:
            self.ClearContextToCommandMapping(context, cmdname)
        svc.cmd.ClearMappedCmd(self, cmdname, showMsg)




class MapCmdWindow(uicls.Window):
    __guid__ = 'form.MapCmdWindow'
    default_fixedWidth = 250
    default_fixedHeight = 135
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        cmdname = attributes.cmdname
        self.SetCaption(uicore.cmd.FuncToDesc(cmdname))
        self.SetTopparentHeight(0)
        self.SetMainIconSize(0)
        self.MakeUnResizeable()
        self.MakeUnpinable()
        self.mouseCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        self.keyCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUp)
        currShortcut = uicore.cmd.GetShortcutStringByFuncName(cmdname) or mls.UI_GENERIC_NONE
        uicls.Label(text=mls.UI_SYSTEMMENU_ENTERSHORTCUT % {'currShortcut': currShortcut}, parent=self.sr.main, state=uiconst.UI_DISABLED, width=self.default_width - 100, left=50, autowidth=False, top=10, singleline=False)
        btnGroup = uicls.ButtonGroup(btns=[(mls.UI_CMD_CANCEL, self.SelfDestruct, None)], parent=self.sr.main, line=True)



    def OnGlobalMouseUp(self, window, msgID, param):
        (btnNum, type,) = param
        btnMap = {uiconst.MOUSEMIDDLE: uiconst.VK_MBUTTON,
         uiconst.MOUSEXBUTTON1: uiconst.VK_XBUTTON1,
         uiconst.MOUSEXBUTTON2: uiconst.VK_XBUTTON2}
        if btnNum in btnMap:
            self.Apply(btnMap[btnNum])



    def OnGlobalKeyUp(self, window, msgID, param):
        (vkey, type,) = param
        self.Apply(vkey)



    def Confirm(self, *args):
        pass



    def Apply(self, vkey):
        shortcut = []
        for modKey in uiconst.MODKEYS:
            if uicore.uilib.Key(modKey) and modKey != vkey:
                shortcut.append(modKey)

        shortcut.append(vkey)
        self.result = {'shortcut': tuple(shortcut)}
        self.SetModalResult(1)



    def OnClose_(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.mouseCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyCookie)




