import service
import geo2
import mathCommon
import trinity
import blue
import uthread
import GameWorld
import yaml
import safeThread
import miscUtil
import uiconst
import uicls
import log
import time
import math

class AnimationDebugWindow(uicls.Window):
    __guid__ = 'uicls.AnimationDebugWindow'
    default_windowID = 'AnimationDebugWindow'
    default_width = 200
    default_height = 250
    default_topParentHeight = 0

    def ApplyAttributes(self, attributes):
        super(uicls.AnimationDebugWindow, self).ApplyAttributes(attributes)
        self.SetCaption('Animation Debug Draw')
        parent = self.GetMainArea()
        parent.SetAlign(uiconst.TOALL)
        parent.SetPadding(5, 5, 5, 5)
        self.entityClient = sm.GetService('entityClient')
        self.animationDebugClient = sm.GetService('animationDebugClient')
        uicls.Checkbox(parent=parent, text='Draw position trace', checked=self.animationDebugClient.IsPositionTrace(), callback=self.OnPositionTraceCheckbox, align=uiconst.TOTOP)
        uicls.Checkbox(parent=parent, text='Draw velocity trace', checked=self.animationDebugClient.IsVelocityTrace(), callback=self.OnVelocityTraceCheckbox)
        uicls.Checkbox(parent=parent, text='Draw rotational trace', checked=self.animationDebugClient.IsRotationalTrace(), callback=self.OnRotationalTraceCheckbox)
        uicls.Checkbox(parent=parent, text='Draw Char Controller', checked=self.animationDebugClient.IsPlayerAvatarDebugDraw(), callback=self.OnPlayerAvatarDebugDraw)
        uicls.Checkbox(parent=parent, text='Draw Morpheme Skeleton', checked=self.animationDebugClient.IsAnimationSkeletonEnabled(), callback=self.SetAnimationSkeletonDraw)
        uicls.Checkbox(parent=parent, text='Draw Mesh Skeleton', checked=self.animationDebugClient.IsMeshSkeletonEnabled(), callback=self.SetMeshSkeletonDraw)
        uicls.Checkbox(parent=parent, text='Draw Net Controller', checked=self.animationDebugClient.IsNetDebugDraw(), callback=self.OnNetDebugDraw)
        uicls.Checkbox(parent=parent, text='Draw Net History', checked=self.animationDebugClient.IsNetDebugDrawHistory(), callback=self.OnNetDebugDrawHistory)
        uicls.Button(parent=parent, align=uiconst.TOBOTTOM, padding=(0, 5, 0, 0), label='Reload Animation Network', func=self.OnReloadAnimationNetwork)
        button = uicls.Button(parent=parent, align=uiconst.TOBOTTOM, label='Reload Static States', func=self.OnReloadStaticStates)
        self.SetMinSize([button.width + 10, 250])



    def OnPositionTraceCheckbox(self, checkbox):
        self.animationDebugClient.SetPositionTrace(checkbox.GetValue())



    def OnVelocityTraceCheckbox(self, checkbox):
        self.animationDebugClient.SetVelocityTrace(checkbox.GetValue())



    def OnRotationalTraceCheckbox(self, checkbox):
        self.animationDebugClient.SetRotationalTrace(checkbox.GetValue())



    def OnPlayerAvatarDebugDraw(self, checkbox):
        self.animationDebugClient.SetPlayerAvatarDebugDraw(checkbox.GetValue())



    def OnNetDebugDraw(self, checkbox):
        self.animationDebugClient.SetNetDebugDraw(checkbox.GetValue())



    def OnNetDebugDrawHistory(self, checkbox):
        self.animationDebugClient.SetNetDebugDrawHistory(checkbox.GetValue())



    def SetAnimationSkeletonDraw(self, checkbox):
        self.animationDebugClient.SetAnimationSkeleton(checkbox.GetValue())



    def SetMeshSkeletonDraw(self, checkbox):
        self.animationDebugClient.SetMeshSkeleton(checkbox.GetValue())



    def OnReloadAnimationNetwork(self, button):
        self.animationDebugClient.ReloadAnimationNetwork()



    def OnReloadStaticStates(self, button):
        self.animationDebugClient.ReloadStaticStates()




class AnimationDebugClient(service.Service):
    __guid__ = 'svc.animationDebugClient'
    __dependencies__ = ['entityClient', 'debugSelectionClient', 'debugRenderClient']
    __notifyevents__ = ['OnSessionChanged', 'OnDebugSelectionChanged']

    def __init__(self, *args):
        service.Service.__init__(self, *args)
        self.registered = False
        self.lastPos = (0.0, 0.0, 0.0)
        self.lastVelPos = (0.0, 0.0, 0.0)
        self.lastRotPos = (0.0, 0.0, 0.0)
        self.lastRot = (1.0, 0.0, 0.0, 0.0)
        self.lastKey = 0
        self.debugRenderStep = None
        self.positionTraceOn = False
        self.velocityTraceOn = False
        self.rotationalTraceOn = False
        self.netDebugDrawOn = False
        self.netDebugDrawHistoryOn = False
        self.animationSkeletonOn = False
        self.meshSkeletonOn = False
        self.positionTrace = None
        self.velocityTrace = None
        self.rotationalTrace = None



    def Run(self, *args):
        service.Service.Run(self, *args)



    def OnDebugSelectionChanged(self, entityID):
        if self.IsPositionTrace():
            self.TurnOnPositionTrace()
        if self.IsVelocityTrace():
            self.TurnOnVelocityTrace()
        if self.IsRotationalTrace():
            self.TurnOnRotationalTrace()



    def OnSessionChanged(self, isRemote, sess, change):
        if 'worldspaceid' in change:
            oldworldspaceid = change['worldspaceid'][0]
            worldspaceid = change['worldspaceid'][1]
            if oldworldspaceid:
                if self.registered:
                    self.UnRegisterPositionTraceKeyEvents()
            if worldspaceid:
                if self.registered:
                    self.RegisterPositionTraceKeyEvents()



    def RegisterPositionTraceKeyEvents(self):
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyDownCallback)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)
        self.mouseDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDownCallback)
        self.mouseUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUpCallback)



    def UnRegisterPositionTraceKeyEvents(self):
        if self.keyDownCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
            self.keyDownCookie = None
        if self.keyUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
            self.keyUpCookie = None
        if self.mouseDownCookie:
            uicore.event.UnregisterForTriuiEvents(self.mouseDownCookie)
            self.mouseDownCookie = None
        if self.mouseUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.mouseUpCookie)
            self.mouseUpCookie = None



    def OnGlobalKeyDownCallback(self, wnd, eventID, (vkey, flag,)):
        playerEnt = self.entityClient.GetPlayerEntity()
        if playerEnt is not None:
            pos = playerEnt.position.position
        if self.lastKey != vkey:
            keyToPrint = chr(vkey)
            if keyToPrint == ' ':
                keyToPrint = 'SPACE'
            self.debugRenderClient.RenderText(pos, keyToPrint, 4294967295L)
            self.lastKey = vkey
        return True



    def OnGlobalKeyUpCallback(self, wnd, eventID, (vkey, flag,)):
        playerEnt = self.entityClient.GetPlayerEntity()
        if playerEnt is not None:
            pos = playerEnt.position.position
        self.debugRenderClient.RenderText(pos, chr(vkey), 4294901760L)
        self.lastKey = 0
        return True



    def OnGlobalMouseDownCallback(self, *args):
        playerEnt = self.entityClient.GetPlayerEntity()
        if playerEnt is not None:
            pos = playerEnt.position.position
        if uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            self.debugRenderClient.RenderText(pos, 'LMB', 4294967295L)
        elif uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
            self.debugRenderClient.RenderText(pos, 'RMB', 4294967295L)
        elif uicore.uilib.rightbtn and uicore.uilib.leftbtn:
            self.debugRenderClient.RenderText(pos, 'LMB+RMB', 4294967295L)
        return True



    def OnGlobalMouseUpCallback(self, wnd, eventID, (vkey, flag,)):
        playerEnt = self.entityClient.GetPlayerEntity()
        if playerEnt is not None:
            pos = playerEnt.position.position
        if vkey == uiconst.MOUSELEFT:
            self.debugRenderClient.RenderText(pos, 'LMB', 4294901760L)
        elif vkey == uiconst.MOUSERIGHT:
            self.debugRenderClient.RenderText(pos, 'RMB', 4294901760L)
        return True



    def SetPositionTrace(self, desireOn):
        if self.positionTraceOn != desireOn:
            self.positionTraceOn = desireOn
        if self.positionTraceOn:
            self.TurnOnPositionTrace()
        else:
            self.TurnOffPositionTrace()



    def TogglePositionTrace(self):
        if self.positionTraceOn:
            self.TurnOffPositionTrace()
        else:
            self.TurnOnPositionTrace()



    def TurnOnPositionTrace(self):
        self.CreateDebugRenderer()
        if self.positionTrace is not None:
            self.TurnOffPositionTrace()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        playerEnt = self.entityClient.GetPlayerEntity()
        if entity is playerEnt:
            self.registered = True
            self.RegisterPositionTraceKeyEvents()
        self.lastPos = entity.position.position
        self.positionTrace = uthread.worker('animationDebugClient.PositionTrace', self._DrawPositionTrace)



    def TurnOffPositionTrace(self):
        self.positionTrace.kill()
        self.positionTrace = None
        if self.registered:
            self.UnRegisterPositionTraceKeyEvents()
            self.registered = False



    def _DrawPositionTrace(self):
        while True:
            try:
                offset = (0, 0.25, 0)
                entity = self.debugSelectionClient.GetSelectedEntity()
                if entity is not None:
                    pos = entity.position.position
                    if self.lastPos != pos:
                        self.debugRenderClient.RenderRay(geo2.Vec3Add(self.lastPos, offset), geo2.Vec3Add(pos, offset), 4294901760L, 4294901760L, time=1000, pulse=True)
                    self.lastPos = pos
            except:
                log.LogException()
            blue.pyos.synchro.SleepWallclock(const.ONE_TICK / const.MSEC)




    def IsPositionTrace(self):
        return self.positionTraceOn



    def SetVelocityTrace(self, desireOn):
        if self.velocityTraceOn != desireOn:
            self.velocityTraceOn = not self.velocityTraceOn
        if self.velocityTraceOn:
            self.TurnOnVelocityTrace()
        else:
            self.TurnOffVelocityTrace()



    def ToggleVelocityTrace(self):
        if self.velocityTraceOn:
            self.TurnOffVelocityTrace()
        else:
            self.TurnOnVelocityTrace()



    def TurnOnVelocityTrace(self):
        self.CreateDebugRenderer()
        if self.velocityTrace is not None:
            self.TurnOffVelocityTrace()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        if not entity.HasComponent('movement'):
            return 
        pos = entity.position.position
        self.lastVelPos = pos
        self.lastVelRulePos = pos
        self.velocityTrace = uthread.worker('animationDebugClient.VelocityTrace', self._DrawVelocityTrace)



    def TurnOffVelocityTrace(self):
        self.velocityTrace.kill()
        self.velocityTrace = None



    def _DrawVelocityTrace(self):
        while True:
            try:
                entity = self.debugSelectionClient.GetSelectedEntity()
                if entity is not None:
                    if not entity.HasComponent('movement'):
                        return 
                    scaleFactor = 1.5 / 4.0
                    offset = 0.25
                    pos = entity.position.position
                    vel = entity.GetComponent('movement').physics.velocity
                    speed = geo2.Vec3Length(vel)
                    speedScaled = speed * scaleFactor
                    velPos = geo2.Vec3Add(pos, (0, offset + speedScaled, 0))
                    velRulePos = geo2.Vec3Add(pos, (0, offset + 1, 0))
                    if self.lastVelPos != velPos:
                        self.debugRenderClient.RenderRay(self.lastVelPos, velPos, 4278190335L, 4278190335L, time=1000, pulse=True)
                        self.debugRenderClient.RenderRay(self.lastVelRulePos, velRulePos, 4278255360L, 4278255360L, time=1000, pulse=False)
                        self.lastVelPos = velPos
                        self.lastVelRulePos = velRulePos
            except:
                log.LogException()
            blue.pyos.synchro.SleepWallclock(const.ONE_TICK / const.MSEC)




    def IsVelocityTrace(self):
        return self.velocityTraceOn



    def SetRotationalTrace(self, desireOn):
        if self.rotationalTraceOn != desireOn:
            self.rotationalTraceOn = not self.rotationalTraceOn
        if self.rotationalTraceOn:
            self.TurnOnRotationalTrace()
        else:
            self.TurnOffRotationalTrace()



    def ToggleRotationalTrace(self):
        if self.rotationalTraceOn:
            self.TurnOffRotationalTrace()
        else:
            self.TurnOnRotationalTrace()



    def TurnOnRotationalTrace(self):
        self.CreateDebugRenderer()
        if self.rotationalTrace is not None:
            self.TurnOffRotationalTrace()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        pos = entity.position.position
        rot = entity.position.rotation
        self.lastRotPos = pos
        self.lastRot = rot
        self.lastRotTime = time.time()
        self.lastRotVel = 0
        self.rotationalTrace = uthread.worker('animationDebugClient.RotationalTrace', self._DrawRotationalTrace)



    def TurnOffRotationalTrace(self):
        self.rotationalTrace.kill()
        self.rotationalTrace = None



    def _DrawRotationalTrace(self):
        while True:
            try:
                entity = self.debugSelectionClient.GetSelectedEntity()
                if entity is not None:
                    offset = 1.2
                    pos = entity.position.position
                    rot = entity.position.rotation
                    if self.lastRotPos != pos or self.lastRot != rot:
                        curTime = time.time()
                        (yaw, trash, trash,) = geo2.QuaternionRotationGetYawPitchRoll(rot)
                        (yawOld, trash, trash,) = geo2.QuaternionRotationGetYawPitchRoll(self.lastRot)
                        if yaw > 1.5 * math.pi and yawOld < 0.5 * math.pi:
                            yawOld = yawOld + 2 * math.pi
                        elif yaw < 0.5 * math.pi and yawOld > 1.5 * math.pi:
                            yawOld = yawOld - 2 * math.pi
                        deltaAngle = yaw - yawOld
                        deltaTime = curTime - self.lastRotTime
                        rotVel = deltaAngle / deltaTime
                        scale = 0.75 / math.pi
                        rulePos = geo2.Vec3Add(pos, (0, offset, 0))
                        lastRulePos = geo2.Vec3Add(self.lastRotPos, (0, offset, 0))
                        if self.lastRotPos != pos:
                            velOffset = rotVel * scale
                            lastVelOffset = self.lastRotVel * scale
                            velPos = geo2.Vec3Add(rulePos, (0, velOffset, 0))
                            lastVelPos = geo2.Vec3Add(lastRulePos, (0, lastVelOffset, 0))
                        else:
                            velPos = rulePos
                            lastVelPos = lastRulePos
                        self.debugRenderClient.RenderRay(lastVelPos, velPos, 4278190335L, 4278190335L, time=1000, pulse=True)
                        self.debugRenderClient.RenderRay(lastRulePos, rulePos, 4278255360L, 4278255360L, time=1000, pulse=False)
                        self.debugRenderClient.RenderRay(geo2.Vec3Add(lastRulePos, (0, math.pi * scale, 0)), geo2.Vec3Add(rulePos, (0, math.pi * scale, 0)), 4294967040L, 4294967040L, time=1000, pulse=False)
                        self.debugRenderClient.RenderRay(geo2.Vec3Add(lastRulePos, (0, -math.pi * scale, 0)), geo2.Vec3Add(rulePos, (0, -math.pi * scale, 0)), 4294967040L, 4294967040L, time=1000, pulse=False)
                        self.lastRotPos = pos
                        self.lastRotTime = curTime
                        self.lastRot = rot
                        self.lastRotVel = rotVel
            except:
                log.LogException()
            blue.pyos.synchro.SleepWallclock(const.ONE_TICK / const.MSEC)




    def IsRotationalTrace(self):
        return self.rotationalTraceOn



    def SetAnimationSkeleton(self, value):
        self.CreateDebugRenderer()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is not None and entity.HasComponent('animation'):
            entity.animation.controller.animationNetwork.displaySkeleton = value



    def IsAnimationSkeletonEnabled(self):
        return self.animationSkeletonOn



    def SetMeshSkeleton(self, value):
        self.CreateDebugRenderer()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity.HasComponent('paperdoll'):
            model = entity.paperdoll.doll.avatar
            model.debugRenderSkeletonTrail = bool(value)



    def IsMeshSkeletonEnabled(self):
        return self.meshSkeletonOn



    def IsPlayerAvatarDebugDraw(self):
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return False
        if not entity.HasComponent('movement'):
            return False
        return entity.GetComponent('movement').characterController.renderDebug



    def SetPlayerAvatarDebugDraw(self, value):
        self.CreateDebugRenderer()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        if not entity.HasComponent('movement'):
            return 
        entity.GetComponent('movement').characterController.renderDebug = bool(value)



    def SetNetDebugDraw(self, desireOn):
        if self.netDebugDrawOn != desireOn:
            self.netDebugDrawOn = not self.netDebugDrawOn
        if self.netDebugDrawOn:
            self.TurnOnNetDebugDraw()
        else:
            self.TurnOffNetDebugDraw()



    def TurnOnNetDebugDraw(self):
        self.CreateDebugRenderer()
        self.TurnOffNetDebugDraw()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        GameWorld.SetNetMoveDebugDraw(entity.entityID, True)



    def TurnOffNetDebugDraw(self):
        try:
            entity = self.debugSelectionClient.GetSelectedEntity()
            if entity is None:
                return 
            GameWorld.SetNetMoveDebugDraw(entity.entityID, False)
        except:
            pass



    def IsNetDebugDraw(self):
        return self.netDebugDrawOn



    def SetNetDebugDrawHistory(self, desireOn):
        if self.netDebugDrawHistoryOn != desireOn:
            self.netDebugDrawHistoryOn = not self.netDebugDrawHistoryOn
        if self.netDebugDrawHistoryOn:
            self.TurnOnNetDebugDrawHistory()
        else:
            self.TurnOffNetDebugDrawHistory()



    def TurnOnNetDebugDrawHistory(self):
        self.CreateDebugRenderer()
        self.TurnOffNetDebugDrawHistory()
        entity = self.debugSelectionClient.GetSelectedEntity()
        if entity is None:
            return 
        GameWorld.SetNetMoveDebugDrawHistory(entity.entityID, True)



    def TurnOffNetDebugDrawHistory(self):
        try:
            entity = self.debugSelectionClient.GetSelectedEntity()
            if entity is None:
                return 
            GameWorld.SetNetMoveDebugDrawHistory(entity.entityID, False)
        except:
            pass



    def IsNetDebugDrawHistory(self):
        return self.netDebugDrawHistoryOn



    def CreateDebugRenderer(self):
        job = getattr(self, 'DebugRenderJob', None)
        if not job:
            render_job = trinity.CreateRenderJob('DebugRender')
            self.debugRenderStep = trinity.TriStepRenderDebug()
            render_job.steps.append(self.debugRenderStep)
            render_job.ScheduleRecurring()
            GameWorld.SetDebugRenderer(self.debugRenderStep)
            render = sm.GetService('debugRenderClient')
            render.SetDebugRendering(True)
            setattr(self, 'DebugRenderJob', True)



    def ReloadAnimationNetwork(self):
        animService = sm.GetService('animationClient')
        entity = self.debugSelectionClient.GetSelectedEntity()
        animService.AnimManager.RemoveEntity(entity.entityID, entity.animation.updater)
        av = entity.paperdoll.doll.avatar
        bundle = entity.animation.updater.network.morphemeBundleRes
        path = entity.animation.updater.network.morphemeBundleRes.path
        bundle.Reload()
        av.animationUpdater = GameWorld.GWAnimation(path)
        entity.animation.updater = av.animationUpdater
        entity.animation.updater.positionComponent = entity.GetComponent('position')
        entity.animation.controller.animationNetwork = entity.animation.updater.network
        entity.animation.updater.SetUpdateCallback(component.controller.Update)
        animService.AnimManager.AddEntity(entity.entityID, entity.animation.updater)
        animService.RegisterAnimationController(entity.animation.controller)



    def ReloadStaticStates(self):
        movementService = sm.GetService('movementClient')
        movementService.movementStates.LoadStates()




