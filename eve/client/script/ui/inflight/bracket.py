import weakref
import blue
import bluepy
import xtriui
import uix
import mathUtil
import uthread
import util
import state
import base
import menu
import trinity
import fleetbr
import uiutil
import uiconst
import pos
import uicls
import maputils
import log
import random
import entities
import localization
import fontConst
SHOWLABELS_NEVER = 0
SHOWLABELS_ONMOUSEENTER = 1
SHOWLABELS_ALWAYS = 2

class BracketLabel(uicls.EveLabelSmall):
    __guid__ = 'xtriui.BracketLabel'
    default_name = 'label'

    def Startup(self, bracket):
        self.bracket_wr = weakref.ref(bracket)
        cs = uicore.uilib.bracketCurveSet
        xBinding = trinity.CreateBinding(cs, bracket.GetRenderObject(), 'displayX', self.GetRenderObject(), 'displayX')
        yBinding = trinity.CreateBinding(cs, bracket.GetRenderObject(), 'displayY', self.GetRenderObject(), 'displayY')
        yOffset = getattr(self, 'yOffset', 3)
        yBinding.offset = (yOffset,
         0,
         0,
         0)
        self.bindings = (xBinding, yBinding)
        self.UpdateLabelAndOffset()
        self.updateTimer = base.AutoTimer(500, self.UpdateLabelAndOffset)



    def Close(self, *args, **kw):
        if getattr(self, 'bindings', None):
            cs = uicore.uilib.bracketCurveSet
            for each in self.bindings:
                if cs and each in cs.bindings:
                    cs.bindings.remove(each)

        self.updateTimer = None
        self.updatePosTimer = None
        uicls.Label.Close(self, *args, **kw)



    def UpdateLabelAndOffset(self):
        bracket = self.bracket_wr
        if bracket:
            bracket = bracket()
        else:
            self.Close()
            return 
        if getattr(self, 'attrName', None) is None:
            newStr = bracket.displayName
            if getattr(bracket, 'showDistance', 1):
                distance = bracket.GetDistance()
                if distance:
                    newStr += ' ' + util.FmtDist(distance)
        else:
            newStr = getattr(bracket, self.attrName, '')
        if newStr != self.text:
            self.text = newStr
        bracketRO = bracket.GetRenderObject()
        (x, y,) = bracketRO.translation
        (xb, yb,) = self.bindings
        bracketLayerWidth = uicore.layer.bracket.GetRenderObject().displayWidth
        if x + 22 + self.textwidth > bracketLayerWidth:
            xb.offset = (-self.textwidth - 6,
             0,
             0,
             0)
        else:
            xb.offset = (22, 0, 0, 0)




class UpdateEntry(object):
    __guid__ = 'xtriui.UpdateEntry'
    broadcastIconSize = ('smallIcon', 16)

    def Startup_update(self, *args):
        self.targetingPath = None
        self.stateItemID = None
        self.sr.targetItem = None
        self.sr.hitchhiker = None
        self.sr.fleetBroadcastIcon = None



    def Load_update(self, slimItem, *args):
        if slimItem is None:
            return 
        self.stateItemID = slimItem.itemID
        (selected, hilited, attacking, hostile, targeting, targeted,) = sm.GetService('state').GetStates(self.stateItemID, [state.selected,
         state.mouseOver,
         state.threatAttackingMe,
         state.threatTargetsMe,
         state.targeting,
         state.targeted])
        self.Select(selected)
        self.Hilite(hilited)
        self.Targeted(targeted)
        activeTargetID = sm.GetService('target').GetActiveTargetID()
        isActive = activeTargetID and activeTargetID == slimItem.itemID
        self.ActiveTarget(isActive)
        if not isActive:
            self.Targeting(targeting)
            if not targeting:
                (targeted,) = sm.GetService('state').GetStates(slimItem.itemID, [state.targeted])
                self.Targeted(targeted)
        if self.updateItem:
            uthread.pool('UpdateEntry::Load_update --> UpdateStates', self.UpdateStates, slimItem)
            self.Attacking(attacking)
            self.Hostile(not attacking and hostile, attacking)
        else:
            f = self.sr.Get('flag', None)
            self.sr.flag = None
            if f:
                f.Close()
            f = self.sr.Get('bgColor', None)
            self.sr.bgColor = None
            if f:
                f.Close()
            if self.sr.hostile_attacking:
                ha = self.sr.hostile_attacking
                self.sr.hostile_attacking = None
                ha.Close()
            if self.sr.icon:
                self.SetColor(*const.OVERVIEW_NORMAL_COLOR)
                if slimItem.groupID == const.groupStargate and slimItem.jumps:
                    destinationPath = sm.GetService('starmap').GetDestinationPath()
                    if slimItem.jumps[0].locationID in destinationPath:
                        self.SetColor(*const.OVERVIEW_AUTO_PILOT_DESTINATION_COLOR)
                    if getattr(self, 'IsBracket', 0):
                        uiutil.SetOrder(self, 0)
                if slimItem.groupID == const.groupStation:
                    waypoints = sm.GetService('starmap').GetWaypoints()
                    if waypoints and slimItem.itemID == waypoints[-1]:
                        self.SetColor(*const.OVERVIEW_AUTO_PILOT_DESTINATION_COLOR)
                if IsForbiddenContainer(slimItem):
                    self.SetColor(*const.OVERVIEW_FORBIDDEN_CONTAINER_COLOR)
                elif IsAbandonedContainer(slimItem):
                    self.SetColor(*const.OVERVIEW_ABANDONED_CONTAINER_COLOR)
        uthread.worker('bracket.UpdateViewed', self.UpdateViewed, slimItem)
        uthread.worker('bracket.UpdateWreckEmpty', self.UpdateWreckEmpty, slimItem)
        uthread.worker('bracket.UpdateFleetBroadcasts', self.UpdateFleetBroadcasts, slimItem)



    def UpdateViewed(self, slimItem):
        if self.destroyed:
            return 
        if slimItem.groupID == const.groupWreck and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            self.Viewed(True)



    def UpdateWreckEmpty(self, slimItem):
        if self.destroyed:
            return 
        if slimItem and slimItem.groupID == const.groupWreck:
            self.WreckEmpty(slimItem.isEmpty)



    def UpdateFleetBroadcasts(self, slimItem):
        (broadcastID, broadcastType, broadcastData,) = sm.GetService('fleet').GetCurrentFleetBroadcastOnItem(slimItem.itemID)
        if self.destroyed or broadcastID is None:
            return 
        for typeName in fleetbr.types:
            if broadcastType == getattr(state, 'gb%s' % typeName):
                handler = getattr(self, 'GB%s' % typeName, None)
                if handler is None:
                    self.FleetBroadcast(True, typeName, broadcastID, *broadcastData)
                else:
                    handler(True, broadcastID, *broadcastData)
                break




    def UpdateStates(self, slimItem):
        sm.GetService('tactical').UpdateStates(slimItem, self)



    def OnStateChange(self, itemID, flag, status, *args):
        if flag == state.lookingAt and hasattr(self, 'ShowTempIcon'):
            if self.stateItemID == eve.session.shipid == itemID:
                if not status:
                    self.ShowTempIcon()
                else:
                    self.HideTempIcon()
        if self.stateItemID != itemID:
            return 
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            self.Select(status)
        elif flag == state.threatTargetsMe:
            attacking = sm.StartService('state').GetStates(itemID, [state.threatAttackingMe])
            if attacking is not None and len(attacking) > 0:
                attacking = attacking[0]
            else:
                attacking = 0
            self.Hostile(status, attacking=attacking)
        elif flag == state.threatAttackingMe:
            self.Attacking(status)
        elif flag == state.targeted:
            self.Targeted(status)
        elif flag == state.targeting:
            self.Targeting(status)
        elif flag == state.activeTarget:
            self.ActiveTarget(status)
        elif flag == state.flagWreckAlreadyOpened:
            self.Viewed(status)
        elif flag == state.flagWreckEmpty:
            self.WreckEmpty(status)
        else:
            for name in fleetbr.types:
                if flag == getattr(state, 'gb%s' % name):
                    handler = getattr(self, 'GB%s' % name, None)
                    if handler is None:
                        self.FleetBroadcast(status, name, *args)
                    else:
                        handler(status, *args)
                    break




    def SetColor(self, r, g, b, _save = True):
        if _save:
            self._originalIconColor = (r, g, b)
        self.sr.icon.color.SetRGB(r, g, b)
        if util.GetAttrs(self, 'sr', 'tempIcon') is not None:
            self.sr.tempIcon.color.SetRGB(r, g, b)



    def Viewed(self, status):
        if not hasattr(self, '_originalIconColor'):
            color = self.sr.icon.color
            self._originalIconColor = (color.r, color.g, color.b)
        (r, g, b,) = self._originalIconColor
        if status:
            attenuation = 0.55
            self.SetColor(r * attenuation, g * attenuation, b * attenuation, _save=False)
        else:
            self.SetColor(r, g, b, _save=False)



    def WreckEmpty(self, isEmpty):
        if isEmpty:
            wreckIcon = 'ui_38_16_29'
        else:
            wreckIcon = 'ui_38_16_28'
        self.sr.icon.LoadIcon(wreckIcon)
        if self.sr.tempIcon:
            self.sr.tempIcon.LoadIcon(wreckIcon)
        self.iconNo = wreckIcon



    def GBTarget(self, active, fleetBroadcastID, charID, targetNo = None):
        self.FleetBroadcast(active, 'Target', fleetBroadcastID, charID)
        if self.sr.targetNo:
            self.sr.targetNo.Close()
            self.sr.targetNo = None
        if active:
            self.sr.targetNo = uicls.EveLabelLarge(text=targetNo, parent=self, idx=0, left=15, top=-6, state=uiconst.UI_DISABLED)



    def FleetBroadcast(self, active, broadcastType, fleetBroadcastID, charID):
        if active:
            self.fleetBroadcastSender = charID
            self.fleetBroadcastType = broadcastType
            self.fleetBroadcastID = fleetBroadcastID
            if self.sr.fleetBroadcastIcon:
                self.sr.fleetBroadcastIcon.Close()
                self.sr.fleetBroadcastIcon = None
            (sizeName, pixels,) = self.broadcastIconSize
            icon = fleetbr.types[broadcastType][sizeName]
            if not self.sr.icon:
                self.LoadIcon(self.iconNo)
            iconLeft = self.sr.icon.width / 2 + self.sr.icon.left - pixels / 2
            iconTop = self.sr.icon.height / 2 + self.sr.icon.top - pixels / 2
            self.sr.fleetBroadcastIcon = uicls.Icon(icon=icon, parent=self, align=uiconst.RELATIVE, pos=(iconLeft,
             iconTop,
             16,
             16), state=uiconst.UI_DISABLED)
            self.sr.fleetBroadcastIcon.name = 'fleetBroadcastIcon'
            self.sr.fleetBroadcastIcon.state = uiconst.UI_DISABLED
        elif fleetBroadcastID == getattr(self, 'fleetBroadcastID', None):
            if self.sr.Get('fleetBroadcastIcon') and self.sr.fleetBroadcastIcon is not None:
                self.sr.fleetBroadcastIcon.Close()
                self.sr.fleetBroadcastIcon = None
            self.fleetBroadcastSender = self.fleetBroadcastType = self.fleetBroadcastID = None



    def ActiveTarget(self, activestate):
        for each in self.children[:]:
            if each.name == 'activetarget':
                each.Close()

        if activestate:
            activeTarget = self.GetActiveTargetUI()
        else:
            (targeted,) = sm.GetService('state').GetStates(self.stateItemID, [state.targeted])
            self.Targeted(targeted, 0)



    def Targeted(self, state, tryActivate = 1):
        obs = sm.GetService('target').IsObserving()
        if obs:
            return 
        if state:
            if not self.sr.targetItem:
                targ = self.GetTargetedUI()
                lines = uiutil.FindChild(targ, 'lines')
                if not settings.user.ui.Get('targetCrosshair', 1):
                    lines.state = uiconst.UI_HIDDEN
                else:
                    lines.state = uiconst.UI_DISABLED
                    _FixLines(targ)
                self.sr.targetItem = targ
            sq = uiutil.FindChild(self.sr.targetItem, 'square')
            if sq is not None and not sq.destroyed:
                sq.state = uiconst.UI_DISABLED
        elif tryActivate:
            self.ActiveTarget(0)
        t = self.sr.targetItem
        self.sr.targetItem = None
        if t is not None:
            t.Close()



    def Targeting(self, state):
        if state:
            if self.sr.targetItem is None or self.sr.targetItem.destroyed:
                self.Targeted(1)
            if self.sr.targetItem:
                uthread.new(self.CountDown, self.sr.targetItem)
                targeting = uiutil.FindChild(self.sr.targetItem, 'targeting')
                targeting.state = uiconst.UI_DISABLED
                uthread.new(self.AnimateTargeting, targeting)
        elif self.sr.targetItem:
            uiutil.FindChild(self.sr.targetItem, 'targeting').state = uiconst.UI_HIDDEN



    def AnimateTargeting(self, item):
        while not item.destroyed and item.state != uiconst.UI_HIDDEN:
            (start, ndt,) = (blue.os.GetSimTime(), 0.0)
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start, blue.os.GetSimTime()) / 333.0, 1.0))
                item.left = item.top = item.width = item.height = int(mathUtil.Lerp(-12, 10, ndt))
                blue.pyos.synchro.Yield()





    def CountDown(self, *args):
        pass



    def Hilite(self, state):
        if self.sr.hilite:
            self.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]



    def Select(self, state):
        if self.sr.selection:
            if state:
                self.sr.node.scroll.DeselectAll(report=False)
                self.sr.node.selected = True
            else:
                self.sr.node.selected = False
            self.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][state]



    def Hostile(self, state, attacking = 0):
        isBracket = getattr(self, 'IsBracket', 0)
        if not isBracket and (self.sr.icon is None or self.sr.icon.state == uiconst.UI_HIDDEN):
            state = 0
        if state:
            if not self.sr.hostile_attacking:
                self.sr.hostile_attacking = self.GetHostileAttackingUI()
                sm.GetService('ui').BlinkSpriteA(self.sr.hostile_attacking, 0.75, 500, None, passColor=0)
            self.sr.hostile_attacking.SetRGB(1, 0.8, 0)
            self.sr.hostile_attacking.state = uiconst.UI_DISABLED
            if not isBracket:
                self.sr.hostile_attacking.left = self.sr.icon.left - 1
        elif not attacking and self.sr.hostile_attacking:
            h = self.sr.hostile_attacking
            self.sr.hostile_attacking = None
            h.Close()



    def Attacking(self, state):
        isBracket = getattr(self, 'IsBracket', 0)
        if not isBracket and (self.sr.icon is None or self.sr.icon.state == uiconst.UI_HIDDEN):
            state = 0
        if state:
            if not self.sr.hostile_attacking:
                self.sr.hostile_attacking = self.GetHostileAttackingUI()
                sm.GetService('ui').BlinkSpriteA(self.sr.hostile_attacking, 0.75, 500, None, passColor=0)
            self.sr.hostile_attacking.SetRGB(0.8, 0, 0)
            self.sr.hostile_attacking.state = uiconst.UI_DISABLED
            if not isBracket:
                self.sr.hostile_attacking.left = self.sr.icon.left - 1
        elif self.itemID in sm.GetService('target').GetTargetedBy():
            self.Hostile(1)
        elif self.sr.hostile_attacking:
            h = self.sr.hostile_attacking
            self.sr.hostile_attacking = None
            h.Close()



    def GetHostileAttackingUI(self):
        return uicls.Sprite(parent=self, name='hostile', pos=(0, 0, 18, 18), state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/classes/Bracket/hostileBracket.png')



    def GetTargetedUI(self):
        return uicls.Sprite(parent=self, name='targeted', pos=(1, 0, 18, 18), state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png')



    def GetActiveTargetUI(self):
        return uicls.Sprite(parent=self, name='activetarget', pos=(1, 0, 18, 18), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png', color=(1.0, 1.0, 1.0, 0.6))



    def UpdateStructureState(self, slimItem):
        if not util.IsStructure(slimItem.categoryID):
            return 
        self.lastPosEvent = blue.os.GetWallclockTime()
        (stateName, stateTimestamp, stateDelay,) = sm.GetService('pwn').GetStructureState(slimItem)
        if self.sr.posStatus is None:
            self.sr.posStatus = uicls.EveLabelSmall(text=entities.POS_STRUCTURE_STATE[stateName], parent=self, left=24, top=30, state=uiconst.UI_NORMAL)
        else:
            self.sr.posStatus.text = entities.POS_STRUCTURE_STATE[stateName]
        if stateName in ('anchoring', 'onlining', 'unanchoring', 'reinforced', 'operating', 'incapacitated'):
            uthread.new(self.StructureProgress, self.lastPosEvent, stateName, stateTimestamp, stateDelay)



    def UpdateOrbitalState(self, slimItem):
        if not util.IsOrbital(slimItem.categoryID):
            return 
        self.lastOrbitalEvent = blue.os.GetWallclockTime()
        if slimItem.orbitalState in (entities.STATE_ANCHORING, entities.STATE_ONLINING, entities.STATE_SHIELD_REINFORCE) or slimItem.groupID == const.groupOrbitalConstructionPlatforms:
            statusString = entities.GetEntityStateString(slimItem.orbitalState)
            if self.sr.orbitalStatus is None:
                self.sr.orbitalStatus = uicls.EveLabelSmall(text=statusString, parent=self, left=24, top=30, state=uiconst.UI_NORMAL)
            else:
                self.sr.orbitalStatus.text = statusString
        if slimItem.orbitalState in (entities.STATE_UNANCHORED, entities.STATE_IDLE, entities.STATE_ANCHORED) and slimItem.groupID != const.groupOrbitalConstructionPlatforms:
            if self.sr.orbitalStatus is not None:
                self.sr.orbitalStatus.Close()
                self.sr.orbitalStatus = None
        if slimItem.orbitalHackerID is not None:
            if self.sr.orbitalHack is None:
                self.sr.orbitalHack = uicls.HackingNumberGrid(parent=self, width=140, height=140, numCellRows=7, cellsPerRow=7, cellHeight=20, cellWidth=20, align=uiconst.CENTERTOP, top=-150)
                self.sr.orbitalHack.BeginColorCycling()
            progress = 0.0 if slimItem.orbitalHackerProgress is None else slimItem.orbitalHackerProgress
            self.sr.orbitalHack.SetProgress(progress)
        elif self.sr.orbitalHack is not None:
            self.sr.orbitalHack.StopColorCycling()
            self.children.remove(self.sr.orbitalHack)
            self.sr.orbitalHack = None
        if slimItem.orbitalState in (entities.STATE_ONLINING,
         entities.STATE_OFFLINING,
         entities.STATE_ANCHORING,
         entities.STATE_UNANCHORING,
         entities.STATE_SHIELD_REINFORCE):
            uthread.new(self.OrbitalProgress, self.lastOrbitalEvent, slimItem)



    def UpdateOutpostState(self, slimItem, oldSlimItem = None):
        if slimItem.groupID == const.groupStation and hasattr(slimItem, 'structureState') and slimItem.structureState in [pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE]:
            endTime = slimItem.startTimestamp + slimItem.delayTime * const.MSEC
            if getattr(self, 'reinforcedProgressThreadRunning', False) == False:
                uthread.new(self.ReinforcedProgress, slimItem.startTimestamp, endTime)
        elif slimItem.groupID == const.groupStation and hasattr(slimItem, 'structureState') and slimItem.structureState == pos.STRUCTURE_INVULNERABLE:
            if not hasattr(self, 'reinforcedTimeText'):
                self.reinforcedTimeText = uicls.EveLabelSmall(text=' ', parent=self, left=-10, top=32, lineSpacing=0.2, state=uiconst.UI_NORMAL)
            timeText = self.reinforcedTimeText
            timeText.text = localization.GetByLabel('UI/Inflight/Brackets/OutpostInvulnerable')
            timeText.left = -32
            self.ChangeReinforcedState(uiconst.UI_NORMAL)
        elif oldSlimItem is not None and getattr(oldSlimItem, 'structureState', None) in [pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE] and getattr(slimItem, 'structureState', None) not in [pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE]:
            self.reinforcedProgressThreadRunning = False
        self.ChangeReinforcedState(uiconst.UI_HIDDEN)
        self.ChangeReinforcedState(uiconst.UI_HIDDEN)



    def UpdatePlanetaryLaunchContainer(self, slimItem):
        uthread.new(self._UpdatePlanetaryLaunchContainer, slimItem)



    def _UpdatePlanetaryLaunchContainer(self, slimItem):
        if slimItem.typeID != const.typePlanetaryLaunchContainer:
            return 
        cnt = 0
        while slimItem.launchTime is None and cnt < 90:
            blue.pyos.synchro.SleepWallclock(1000)
            cnt += 1

        if getattr(self, 'planetaryLaunchContainerThreadRunning', False) == False and slimItem.launchTime is not None:
            uthread.new(self.PlanetaryLaunchContainerProgress, slimItem.launchTime, long(slimItem.launchTime + const.piLaunchOrbitDecayTime))



    def PlanetaryLaunchContainerProgress(self, startTime, endTime):
        self.planetaryLaunchContainerThreadRunning = True
        try:
            boxwidth = 82
            fillwidth = boxwidth - 2
            boxheight = 14
            fillheight = boxheight - 2
            boxtop = 30
            filltop = boxtop + 1
            boxleft = -(boxwidth / 2) + 5
            fillleft = boxleft + 1
            boxcolor = (1.0, 1.0, 1.0, 0.35)
            fillcolor = (1.0, 1.0, 1.0, 0.25)
            if not hasattr(self, 'reinforcedState'):
                self.burnupFill = uicls.Fill(parent=self, align=uiconst.RELATIVE, width=fillwidth, height=fillheight, left=fillleft, top=filltop, color=fillcolor)
            burnupFill = self.burnupFill
            if not hasattr(self, 'burnupTimeText'):
                self.burnupTimeText = uicls.EveLabelSmall(text=' ', parent=self, left=-10, top=32, lineSpacing=0.2, state=uiconst.UI_NORMAL)
            timeText = self.burnupTimeText
            if not hasattr(self, 'burnupFrame'):
                self.burnupFrame = uicls.Frame(parent=self, align=uiconst.RELATIVE, width=boxwidth, height=boxheight, left=boxleft, top=boxtop, color=boxcolor)
            frame = self.burnupFrame
            while not self.destroyed and self.planetaryLaunchContainerThreadRunning:
                currentTime = blue.os.GetWallclockTime()
                portion = float(currentTime - startTime) / (endTime - startTime)
                if portion > 1.0:
                    break
                width = min(int(portion * fillwidth), fillwidth)
                width = fillwidth - abs(width)
                if burnupFill.width != width:
                    burnupFill.width = width
                newTimeText = util.FmtDate(endTime - currentTime, 'ss')
                if timeText.text != newTimeText:
                    textWidth = uix.GetTextWidth(newTimeText, fontsize=fontConst.EVE_SMALL_FONTSIZE, hspace=1, uppercase=1)
                    timeText.text = newTimeText
                    timeText.left = -32
                blue.pyos.synchro.SleepWallclock(1000)


        finally:
            self.planetaryLaunchContainerThreadRunning = False




    def ChangeReinforcedState(self, state):
        if hasattr(self, 'reinforcedState'):
            self.reinforcedState.state = state
        if hasattr(self, 'reinforcedTimeText'):
            self.reinforcedTimeText.state = state
        if hasattr(self, 'reinforcedFrame'):
            self.reinforcedFrame.state = state



    def ReinforcedProgress(self, startTime, endTime):
        self.reinforcedProgressThreadRunning = True
        try:
            boxwidth = 82
            fillwidth = boxwidth - 2
            boxheight = 14
            fillheight = boxheight - 2
            boxtop = 30
            filltop = boxtop + 1
            boxleft = -(boxwidth / 2) + 5
            fillleft = boxleft + 1
            boxcolor = (1.0, 1.0, 1.0, 0.35)
            fillcolor = (1.0, 1.0, 1.0, 0.25)
            if not hasattr(self, 'reinforcedState'):
                self.reinforcedState = uicls.Fill(parent=self, align=uiconst.RELATIVE, width=fillwidth, height=fillheight, left=fillleft, top=filltop, color=fillcolor)
            p = self.reinforcedState
            if not hasattr(self, 'reinforcedTimeText'):
                self.reinforcedTimeText = uicls.EveLabelSmall(text=' ', parent=self, left=-10, top=32, lineSpacing=0.2, state=uiconst.UI_NORMAL)
            timeText = self.reinforcedTimeText
            if not hasattr(self, 'reinforcedFrame'):
                self.reinforcedFrame = uicls.Frame(parent=self, align=uiconst.RELATIVE, width=boxwidth, height=boxheight, left=boxleft, top=boxtop, color=boxcolor)
            frame = self.reinforcedFrame
            self.ChangeReinforcedState(uiconst.UI_NORMAL)
            while not self.destroyed and self.reinforcedProgressThreadRunning:
                currentTime = blue.os.GetWallclockTime()
                portion = float(currentTime - startTime) / (endTime - startTime)
                if portion > 1.0:
                    break
                width = min(int(portion * fillwidth), fillwidth)
                width = fillwidth - abs(width)
                if p.width != width:
                    p.width = width
                timeText.text = localization.GetByLabel('UI/Inflight/Brackets/RemainingReinforcedTime', timeRemaining=endTime - currentTime)
                timeText.left = -32
                blue.pyos.synchro.SleepWallclock(1000)


        finally:
            self.reinforcedProgressThreadRunning = False




    def UpdateCaptureProgress(self, captureData):
        slimItem = self.slimItem
        if slimItem.groupID != const.groupCapturePointTower:
            return 
        if captureData:
            self.captureData = captureData
        else:
            self.captureData = sm.GetService('bracket').GetCaptureData(self.itemID)
        if not self.captureData:
            return 
        if not getattr(self, 'captureTaskletRunning', False):
            uthread.new(self.CaptureProgress)



    def CaptureProgress(self):
        captureID = self.captureData.get('captureID', None)
        if captureID is None:
            return 
        self.captureTaskletRunning = True
        boxwidth = 82
        fillwidth = boxwidth - 2
        boxheight = 14
        fillheight = boxheight - 2
        boxtop = 30
        filltop = boxtop + 1
        boxleft = -(boxwidth / 2) + 5
        fillleft = boxleft + 1
        boxcolor = (1.0, 1.0, 1.0, 0.35)
        fillcolor = (1.0, 1.0, 1.0, 0.25)
        frame = uicls.Frame(parent=self, align=uiconst.RELATIVE, width=boxwidth, height=boxheight, left=boxleft, top=boxtop, color=boxcolor)
        if not hasattr(self, 'captureState'):
            self.captureState = uicls.Fill(parent=self, align=uiconst.RELATIVE, width=0, height=fillheight, left=fillleft, top=filltop, color=fillcolor)
        p = self.captureState
        texttop = boxtop + boxheight + 2
        if not hasattr(self, 'captureStateText'):
            self.captureStateText = uicls.EveLabelSmall(text=' ', parent=self, left=boxleft, top=texttop, state=uiconst.UI_NORMAL)
        t = self.captureStateText
        if not hasattr(self, 'captureStateTimeText'):
            self.captureStateTimeText = uicls.EveLabelSmall(text=' ', parent=self, left=-10, top=filltop + 1, state=uiconst.UI_NORMAL)
        timeText = self.captureStateTimeText
        portion = 0.0
        while not self.destroyed and portion < 1.0:
            if self.captureData['captureID'] != 'contested':
                totalTimeMs = self.captureData['captureTime'] * 60 * 1000
                timeDiff = blue.os.TimeDiffInMs(self.captureData['lastIncident'], blue.os.GetSimTime())
                portion = float(timeDiff) / totalTimeMs
                portion = portion + float(self.captureData['points']) / 100
                width = min(int(portion * fillwidth), fillwidth)
                width = abs(width)
                if p.width != width:
                    p.width = width
                capText = localization.GetByLabel('UI/Inflight/Brackets/FacWarCapturing', ownerName=cfg.eveowners.Get(self.captureData['captureID']).name)
                if t.text != capText:
                    t.text = capText
                newTimeText = self.GetCaptureTimeString(portion)
                if timeText.text != newTimeText:
                    textWidth = uix.GetTextWidth(newTimeText, fontsize=fontConst.EVE_SMALL_FONTSIZE, hspace=1, uppercase=1)
                    timeText.text = newTimeText
                    timeText.left = -8
                if portion < 0.0:
                    self.SetCaptureLogo(self.captureData['lastCapturing'])
                else:
                    self.SetCaptureLogo(self.captureData['captureID'])
            else:
                self.SetCaptureLogo(self.captureData['lastCapturing'])
                portion = float(self.captureData['points']) / 100
                width = min(int(portion * fillwidth), fillwidth)
                width = abs(width)
                if p.width != width:
                    p.width = width
                t.text = localization.GetByLabel('UI/Inflight/Brackets/SystemContested')
                break
            blue.pyos.synchro.SleepWallclock(500)

        if self and not self.destroyed:
            timeText.text = self.GetCaptureTimeString(portion)
        self.captureTaskletRunning = False



    def GetCaptureTimeString(self, portion):
        if self.captureData['captureID'] == 'contested':
            return ' '
        timeScalar = 1 - portion
        if timeScalar <= 0:
            return localization.GetByLabel('UI/Inflight/Brackets/FacWarCaptured')
        maxTime = self.captureData['captureTime']
        timeLeft = timeScalar * maxTime
        properTime = long(60000L * const.dgmTauConstant * timeLeft)
        return util.FmtDate(properTime, 'ns')



    def SetCaptureLogo(self, teamID):
        if teamID == 'contested' or teamID is None:
            return 
        if self.sr.Get('captureLogo'):
            if self.sr.captureLogo.name == cfg.eveowners.Get(teamID).name:
                return 
            self.sr.captureLogo.Close()
        raceIDByTeamID = {const.factionCaldariState: const.raceCaldari,
         const.factionMinmatarRepublic: const.raceMinmatar,
         const.factionAmarrEmpire: const.raceAmarr,
         const.factionGallenteFederation: const.raceGallente}
        logo = uicls.LogoIcon(itemID=raceIDByTeamID.get(teamID, teamID), parent=self, state=uiconst.UI_DISABLED, size=32, pos=(-70, 22, 32, 32), name=cfg.eveowners.Get(teamID).name, align=uiconst.RELATIVE, ignoreSize=True)
        self.sr.captureLogo = logo



    def StructureProgress(self, lastPosEvent, stateName, stateTimestamp, stateDelay):
        if self.destroyed:
            return 
        t = self.sr.posStatus
        uicls.Frame(parent=self, align=uiconst.RELATIVE, width=82, height=13, left=18, top=30, color=(1.0, 1.0, 1.0, 0.5))
        p = uicls.Fill(parent=self, align=uiconst.RELATIVE, width=80, height=11, left=19, top=31, color=(1.0, 1.0, 1.0, 0.25))
        startTime = blue.os.GetWallclockTime()
        if stateDelay:
            stateDelay = float(stateDelay * const.MSEC)
        doneStr = {'anchoring': localization.GetByLabel('Entities/States/Anchored'),
         'onlining': localization.GetByLabel('Entities/States/Online'),
         'unanchoring': localization.GetByLabel('Entities/States/Unanchored'),
         'reinforced': localization.GetByLabel('Entities/States/Online'),
         'operating': localization.GetByLabel('Entities/States/Operating'),
         'incapacitated': localization.GetByLabel('Entities/States/Incapacitated')}.get(stateName, localization.GetByLabel('Entities/States/Done'))
        endTime = 0
        if stateDelay:
            endTime = stateTimestamp + stateDelay
        while 1 and endTime:
            if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
                return 
            timeLeft = endTime - blue.os.GetWallclockTime()
            portion = timeLeft / stateDelay
            timeLeftSec = timeLeft / 1000.0
            if timeLeft <= 0:
                t.text = doneStr
                break
            t.text = localization.GetByLabel('UI/Inflight/Brackets/StructureProgress', stateName=entities.POS_STRUCTURE_STATE[stateName], timeRemaining=long(timeLeft))
            p.width = int(80 * portion)
            blue.pyos.synchro.SleepWallclock(900)

        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed:
            return 
        for each in self.children[-2:]:
            if each is not None and not getattr(each, 'destroyed', 0):
                each.Close()

        if lastPosEvent != self.lastPosEvent:
            return 
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return 
        t.text = doneStr
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return 
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return 
        t.text = doneStr



    def OrbitalProgress(self, lastOrbitalEvent, slimItem):
        if self.destroyed:
            return 
        t = self.sr.orbitalStatus
        uicls.Frame(parent=self, align=uiconst.TOPLEFT, width=82, height=13, left=18, top=30, color=(1.0, 1.0, 1.0, 0.5))
        p = uicls.Fill(parent=self, align=uiconst.TOPLEFT, width=80, height=11, left=19, top=31, color=(1.0, 1.0, 1.0, 0.25))
        stateName = entities.GetEntityStateString(slimItem.orbitalState)
        stateTimestamp = slimItem.orbitalTimestamp
        stateDelay = None
        doneText = localization.GetByLabel('Entities/States/Done')
        godmaSM = sm.GetService('godma').GetStateManager()
        if slimItem.orbitalState == entities.STATE_ANCHORING:
            stateDelay = godmaSM.GetType(slimItem.typeID).anchoringDelay
            doneText = entities.GetEntityStateString(entities.STATE_ANCHORED)
        elif slimItem.orbitalState == entities.STATE_ONLINING:
            stateName = localization.GetByLabel('Entities/States/Upgrading')
            stateDelay = godmaSM.GetType(slimItem.typeID).onliningDelay
            doneText = localization.GetByLabel('Entities/States/Online')
        elif slimItem.orbitalState == entities.STATE_UNANCHORING:
            stateDelay = godmaSM.GetType(slimItem.typeID).unanchoringDelay
            doneText = entities.GetEntityStateString(entities.STATE_UNANCHORED)
        elif slimItem.orbitalState == entities.STATE_SHIELD_REINFORCE:
            doneText = entities.GetEntityStateString(entities.STATE_ANCHORED)
        if stateDelay:
            stateDelay = float(stateDelay * const.MSEC)
        else:
            stateDelay = const.DAY
        timeLeft = stateTimestamp - blue.os.GetWallclockTime()
        try:
            while timeLeft > 0:
                blue.pyos.synchro.SleepWallclock(900)
                if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
                    return 
                timeLeft = stateTimestamp - blue.os.GetWallclockTime()
                portion = max(0.0, min(1.0, timeLeft / stateDelay))
                t.text = localization.GetByLabel('UI/Inflight/Brackets/StructureProgress', stateName=stateName, timeRemaining=long(timeLeft))
                p.width = int(80 * portion)

            t.text = doneText
            blue.pyos.synchro.SleepWallclock(250)
            if not self or self.destroyed:
                return 

        finally:
            if self and not self.destroyed:
                t.text = doneText
                for each in self.children[-2:]:
                    if each is not None and not getattr(each, 'destroyed', 0):
                        each.Close()


        if lastOrbitalEvent != self.lastOrbitalEvent:
            return 
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return 
        t.text = doneText
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return 
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return 
        t.text = doneText



    def SetBracketAnchoredState(self, slimItem):
        if not cfg.invgroups.Get(slimItem.groupID).anchorable:
            return 
        if not slimItem or slimItem.itemID == eve.session.shipid or slimItem.ownerID != eve.session.charid and slimItem.ownerID != eve.session.corpid:
            return 
        ball = self.ball
        if ball is None:
            bp = sm.GetService('michelle').GetBallpark()
            ball = bp.GetBall(slimItem.itemID)
            if not ball:
                return 
        (_iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag,) = sm.GetService('bracket').GetBracketProps(slimItem, ball)
        (iconNo, dockType, minDist, maxDist, iconOffset, logflag,) = self.data
        for each in self.children:
            if each.name == 'anchoredicon':
                if ball.isFree:
                    self.data = (iconNo,
                     dockType,
                     _minDist,
                     _maxDist,
                     iconOffset,
                     logflag)
                    each.Close()
                return 

        if not ball.isFree:
            self.data = (iconNo,
             dockType,
             0.0,
             1e+32,
             iconOffset,
             logflag)
            uicls.Icon(icon='ui_38_16_15', name='anchoredicon', parent=self, pos=(0, 16, 16, 16), align=uiconst.TOPLEFT)



    def UpdateHackProgress(self, hackProgress):
        if self.sr.orbitalHackLocal is None:
            return 
        self.sr.orbitalHackLocal.SetValue(hackProgress)



    def BeginHacking(self):
        if self.sr.orbitalHackLocal is None:
            self.sr.orbitalHackLocal = uicls.HackingProgressBar(parent=self, height=20, width=120, align=uiconst.CENTERBOTTOM, top=-50, color=(0.0, 0.8, 0.0, 1.0), backgroundColor=(0.25, 0.0, 0.0, 1.0))



    def _StopHacking(self):
        blue.pyos.synchro.SleepWallclock(5000)
        if self and self.sr.orbitalHackLocal:
            self.sr.orbitalHackLocal.state = uiconst.UI_HIDDEN
            self.sr.orbitalHackLocal.Close()
            self.sr.orbitalHackLocal = None



    def StopHacking(self, success = False):
        if self.sr.orbitalHackLocal is not None:
            self.sr.orbitalHackLocal.Finalize(complete=success)
            uthread.new(self._StopHacking)




class BaseBracket(uicls.Bracket):
    __guid__ = 'xtriui.BaseBracket'
    default_width = 16
    default_height = 16

    def ApplyAttributes(self, attributes):
        uicls.Bracket.ApplyAttributes(self, attributes)
        self.IsBracket = 1
        self.invisible = False
        self.inflight = False
        self.categoryID = None
        self.groupID = None
        self.itemID = None
        self.displayName = ''
        self.displaySubLabel = ''
        self.sr.icon = None
        self.sr.tempIcon = None
        self.sr.hitchhiker = None
        self.sr.flag = None
        self.sr.bgColor = None
        self.sr.hostile_attacking = None
        self.sr.hilite = None
        self.sr.selection = None
        self.sr.posStatus = None
        self.sr.orbitalHack = None
        self.sr.orbitalHackLocal = None
        self.slimItem = None
        self.ball = None
        self.stateItemID = None
        self.label = None
        self.subLabel = None
        self.fadeColor = True
        self.iconNo = None
        self.iconXOffset = 0
        self.lastPosEvent = None
        self.scanAttributeChangeFlag = False
        self.iconTop = 0



    def Close(self, *args, **kw):
        self.KillLabel(closing=True)
        uicls.Bracket.Close(self, *args, **kw)



    def OnStateChange(self, itemID, flag, status, *args):
        if flag == state.lookingAt and hasattr(self, 'ShowTempIcon'):
            if self.stateItemID == eve.session.shipid == itemID:
                if not status:
                    self.ShowTempIcon()
                else:
                    self.HideTempIcon()
        if self.stateItemID != itemID:
            return 
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            self.Select(status)



    def Startup(self, itemID, groupID, categoryID, iconNo):
        self.iconNo = iconNo
        self.LoadIcon(iconNo)
        self.itemID = itemID
        self.stateItemID = itemID
        self.groupID = groupID
        self.categoryID = categoryID



    def LoadIcon(self, iconNo):
        if getattr(self, 'noIcon', 0) == 1:
            return 
        if self.sr.icon is None:
            icon = uicls.Icon(parent=self, name='mainicon', state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), icon=iconNo, align=uiconst.RELATIVE)
            if self.fadeColor:
                self.color = icon.color
            else:
                icon.color.a = 0.75
            self.sr.icon = icon
        else:
            self.sr.icon.LoadIcon(iconNo)



    def ShowTempIcon(self):
        if getattr(self, 'noIcon', 0) == 1:
            return 
        if not self.sr.tempIcon:
            tempicon = uicls.Icon(parent=self, name='tempicon', state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), align=uiconst.RELATIVE, icon=self.iconNo, color=(1, 1, 1, 0.75), idx=0)
            if self.sr.icon:
                tempicon.top = self.sr.icon.top
                tempicon.left = self.sr.icon.left
                tempicon.SetAlign(self.sr.icon.GetAlign())
            else:
                tempicon.top = 0
                tempicon.left = 0
                tempicon.SetAlign(uiconst.CENTERTOP)
            self.sr.tempIcon = tempicon
        if self.sr.icon:
            self.sr.tempIcon.color.SetRGB(*self.sr.icon.GetRGBA())
            self.sr.icon.state = uiconst.UI_HIDDEN



    def HideTempIcon(self, closing = False):
        if not closing:
            lookingAt = sm.GetService('state').GetExclState(state.lookingAt)
            if self.stateItemID == eve.session.shipid and lookingAt != eve.session.shipid:
                return 
        if self.sr.tempIcon:
            self.sr.tempIcon.Close()
            self.sr.tempIcon = None
        if self.sr.icon:
            self.sr.icon.state = uiconst.UI_DISABLED



    def ShowLabel(self, *args):
        if not self.destroyed and (self.displayName == '' or not getattr(self, 'showLabel', True)):
            return 
        if self.itemID == eve.session.shipid:
            if not self.sr.tempIcon:
                return 
        if not self.label:
            self.label = BracketLabel(parent=self.parent, name='labelparent', idx=0, align=uiconst.RELATIVE, state=uiconst.UI_NORMAL)
            self.label.Startup(self)
            self.label.OnMouseUp = self.OnMouseUp
            self.label.OnMouseDown = self.OnMouseDown
            self.label.OnMouseEnter = self.OnMouseEnter
            self.label.OnMouseExit = self.OnMouseExit
            self.label.OnMouseHover = self.OnMouseHover
            self.label.OnClick = self.OnClick
            self.label.GetMenu = self.GetMenu
        if not self.subLabel:
            self.subLabel = BracketLabel(parent=self.parent, name='sublabelparent', align=uiconst.TOPLEFT, top=16, state=uiconst.UI_NORMAL)
            self.subLabel.attrName = 'displaySubLabel'
            self.subLabel.yOffset = 19
            self.subLabel.Startup(self)
            self.subLabel.OnMouseUp = self.OnMouseUp
            self.subLabel.OnMouseDown = self.OnMouseDown
            self.subLabel.OnMouseEnter = self.OnMouseEnter
            self.subLabel.OnMouseExit = self.OnMouseExit
            self.subLabel.OnMouseHover = self.OnMouseHover
            self.subLabel.OnClick = self.OnClick
            self.subLabel.GetMenu = self.GetMenu
        if getattr(self, 'showLabel', True) == SHOWLABELS_ONMOUSEENTER:
            self.ShowTempIcon()



    def KillLabel(self, closing = False):
        self.HideTempIcon(closing)
        if getattr(self, 'label', None):
            self.label.Close()
        if getattr(self, 'subLabel', None):
            self.subLabel.Close()
        self.label = None
        self.subLabel = None



    def GetMenu(self):
        return None



    def Select(self, status):
        if status:
            if not self.sr.selection:
                self.sr.selection = selection = uicls.Sprite(parent=self, pos=(0, 0, 16, 16), name='selection', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/selectionFrame.png', align=uiconst.CENTER)
            self.sr.selection.state = uiconst.UI_DISABLED
            self.ShowLabel()
        elif self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN
        if self.projectBracket and self.projectBracket.bracket:
            self.KillLabel()



    def Hilite(self, status):
        if status and self.state != uiconst.UI_HIDDEN:
            uthread.pool('Bracket::Hilite', self._ShowLabel)
        elif self.projectBracket and self.projectBracket.bracket and sm.GetService('state').GetExclState(state.selected) != self.itemID:
            self.KillLabel()



    def _ShowLabel(self):
        blue.pyos.synchro.SleepWallclock(50)
        if self.destroyed:
            return 
        over = uicore.uilib.mouseOver
        if getattr(over, 'stateItemID', None) == self.itemID:
            self.ShowLabel()



    def GetDistance(self):
        ball = self.ball
        if ball:
            return ball.surfaceDist
        slimItem = self.GetSlimItem()
        if slimItem:
            ballPark = sm.GetService('michelle').GetBallpark()
            if ballPark and slimItem.itemID in ballPark.balls:
                return ballPark.balls[slimItem.itemID].surfaceDist



    @apply
    def ball():
        doc = ''

        def fget(self):
            if self._ball:
                return self._ball()



        def fset(self, value):
            if value is None:
                self._ball = None
                return 
            self._ball = weakref.ref(value)


        return property(**locals())



    def GetSlimItem(self):
        return self.slimItem



    def HideBubble(self):
        if self.sr.bubble is not None:
            self.sr.bubble.Close()
            self.sr.bubble = None



    def ShowBubble(self, hint):
        if self.sr.bubble is not None:
            self.sr.bubble.Close()
            self.sr.bubble = None
        if hint:
            bubble = xtriui.BubbleHint(parent=self, name='bubblehint', align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_PICKCHILDREN)
            pointer = {const.groupStargate: 5,
             const.groupStation: 3}.get(self.groupID, 0)
            bubble.ShowHint(hint, pointer)
            self.sr.bubble = bubble
            self.sr.bubble.state = uiconst.UI_NORMAL




class Bracket(BaseBracket, UpdateEntry):
    __guid__ = 'xtriui.Bracket'
    broadcastIconSize = ('bigIcon', 32)

    def Startup(self, slimItem, ball = None, transform = None):
        (self.iconNo, dockType, minDist, maxDist, iconOffset, logflag,) = self.data
        self.slimItem = slimItem
        self.itemID = slimItem.itemID
        self.groupID = slimItem.groupID
        self.categoryID = slimItem.categoryID
        xtriui.UpdateEntry.Startup_update(self)
        if not self.invisible:
            self.LoadIcon(self.iconNo)
        self.UpdateStructureState(slimItem)
        self.UpdateCaptureProgress(None)
        self.UpdateOutpostState(slimItem)
        self.UpdatePlanetaryLaunchContainer(slimItem)
        self.SetBracketAnchoredState(slimItem)
        UpdateEntry.Load_update(self, slimItem)



    @apply
    def slimItem():

        def fget(self):
            if self._slimItem:
                return self._slimItem()
            else:
                return None



        def fset(self, value):
            if value is None:
                self._slimItem = None
            else:
                self._slimItem = weakref.ref(value)


        return property(**locals())



    def OnStateChange(self, *args):
        xtriui.UpdateEntry.OnStateChange(self, *args)



    def OnMouseDown(self, *args):
        if getattr(self, 'slimItem', None):
            if sm.GetService('menu').TryExpandActionMenu(self.itemID, uicore.uilib.x, uicore.uilib.y, self):
                return 
        sm.GetService('viewState').GetView('inflight').layer.looking = True



    def OnMouseEnter(self, *args):
        log.LogInfo('Bracket OnMouseEnter')
        if uicore.uilib.leftbtn:
            return 
        if not getattr(self, 'invisible', False) or self.sr.tempIcon:
            if self.itemID == sm.GetService('bracket').CheckingOverlaps():
                return 
            sm.GetService('state').SetState(self.itemID, state.mouseOver, 1)



    def OnMouseHover(self, *args):
        if uicore.uilib.leftbtn:
            return 
        if self.projectBracket and self.projectBracket.bracket:
            if self.itemID == sm.GetService('bracket').CheckingOverlaps():
                return 
            sm.GetService('bracket').CheckOverlaps(self, not getattr(self, 'inflight', 1))



    def OnMouseExit(self, *args):
        log.LogInfo('Bracket OnMouseExit')
        if uicore.uilib.leftbtn:
            return 
        if self.projectBracket and self.projectBracket.bracket:
            over = uicore.uilib.mouseOver
            if self.itemID == sm.GetService('bracket').CheckingOverlaps():
                return 
            sm.GetService('state').SetState(self.itemID, state.mouseOver, 0)



    def OnClick(self, *args):
        if self.sr.clicktime and blue.os.TimeDiffInMs(self.sr.clicktime, blue.os.GetWallclockTime()) < 1000.0:
            cameraSvc = sm.StartService('camera')
            if cameraSvc.IsFreeLook():
                cameraSvc.LookAt(self.itemID)
                return 
            sm.GetService('state').SetState(self.itemID, state.selected, 1)
            slimItem = getattr(self, 'slimItem', None)
            if slimItem:
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    return 
                sm.GetService('menu').Activate(slimItem)
            self.sr.clicktime = None
        else:
            sm.GetService('state').SetState(self.itemID, state.selected, 1)
            if sm.GetService('target').IsTarget(self.itemID):
                sm.GetService('state').SetState(self.itemID, state.activeTarget, 1)
            elif uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT):
                sm.GetService('fleet').SendBroadcast_Target(self.itemID)
            self.sr.clicktime = blue.os.GetWallclockTime()
        sm.GetService('menu').TacticalItemClicked(self.itemID)



    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.itemID, slimItem=self.slimItem)



    def OnAttribute(self, attributeName, item, newValue):
        self.scanAttributeChangeFlag = True



    def CountDown(self, target):
        if self.destroyed:
            return 
        self.scanAttributeChangeFlag = False
        slimItem = self.slimItem
        source = eve.session.shipid
        time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
        if target:
            par = uicls.Container(parent=target, width=82, height=13, left=36, top=37, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
            t = uicls.EveLabelSmall(text='', parent=par, width=200, left=6, state=uiconst.UI_NORMAL)
            p = uicls.Fill(parent=par, align=uiconst.RELATIVE, width=80, height=11, left=1, top=1, color=(1.0, 1.0, 1.0, 0.25))
            uicls.Frame(parent=par, color=(1.0, 1.0, 1.0, 0.5))
            startTime = blue.os.GetSimTime()
            lockedText = localization.GetByLabel('UI/Inflight/Brackets/TargetLocked')
            while 1:
                now = blue.os.GetSimTime()
                dt = blue.os.TimeDiffInMs(startTime, now)
                if self.scanAttributeChangeFlag:
                    waitRatio = dt / float(time)
                    self.scanAttributeChangeFlag = False
                    time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
                    startTime = now - long(time * waitRatio * 10000)
                    dt = blue.os.TimeDiffInMs(startTime, now)
                if t.destroyed:
                    return 
                t.text = localization.GetByLabel('UI/Inflight/Brackets/TargetingCountdownTimer', numSeconds=(time - dt) / 1000.0)
                if dt > time:
                    t.text = lockedText
                    break
                p.width = int(80 * ((time - dt) / time))
                blue.pyos.synchro.Yield()

            blue.pyos.synchro.SleepWallclock(250)
            if t.destroyed:
                return 
            t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
            if t.destroyed:
                return 
            t.text = lockedText
            blue.pyos.synchro.SleepWallclock(250)
            if t.destroyed:
                return 
            t.text = ''
            blue.pyos.synchro.SleepWallclock(250)
            if t.destroyed:
                return 
            t.text = lockedText
            blue.pyos.synchro.SleepWallclock(250)
            par.Close()



    def GBEnemySpotted(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'EnemySpotted')



    def GBNeedBackup(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'NeedBackup')



    def GBInPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'InPosition')



    def GBHoldPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'HoldPosition')



    def NearIDFleetBroadcast(self, active, fleetBroadcastID, charID, broadcastType):
        inBubble = bool(util.SlimItemFromCharID(charID))
        if inBubble:
            return self.FleetBroadcast(active, broadcastType, fleetBroadcastID, charID)
        if active:
            self.fleetBroadcastSender = charID
            self.fleetBroadcastType = broadcastType
            self.fleetBroadcastID = fleetBroadcastID
            if self.sr.Get('fleetBroadcastIcon') and self.sr.fleetBroadcastIcon is not None:
                self.sr.fleetBroadcastIcon.Close()
                self.sr.fleetBroadcastIcon = None
            icon = fleetbr.types[broadcastType]['bigIcon']
            (sizeName, pixels,) = self.broadcastIconSize
            icon = fleetbr.types[broadcastType][sizeName]
            iconLeft = self.sr.icon.width / 2 + self.sr.icon.left - pixels / 2
            iconTop = self.sr.icon.height / 2 + self.sr.icon.top - pixels / 2
            self.sr.fleetBroadcastIcon = uicls.Icon(icon='ui_44_16_53', parent=self, align=uiconst.RELATIVE, pos=(0, 0, 16, 16), state=uiconst.UI_DISABLED)
            self.sr.fleetBroadcastIcon.name = 'fleetBroadcastIcon'
            self.sr.fleetBroadcastIcon.state = uiconst.UI_NORMAL
        elif fleetBroadcastID == getattr(self, 'fleetBroadcastID', None):
            if self.sr.Get('fleetBroadcastIcon') and self.sr.fleetBroadcastIcon is not None:
                self.sr.fleetBroadcastIcon.Close()
                self.sr.fleetBroadcastIcon = None
            self.fleetBroadcastSender = self.fleetBroadcastType = self.fleetBroadcastID = None



    def GetHostileAttackingUI(self):
        threat = uicls.Sprite(parent=self, name='threat', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/threatBracket.png')
        return threat



    def GetActiveTargetUI(self):
        return ActiveTarget(parent=self)



    def GetTargetedUI(self):
        return xtriui.TargetLayout(parent=self)



    def CreateColorCurve(self, destObject, curveSet, length = 1.0, startValue = (1, 1, 1, 1), endValue = (1, 1, 1, 0), cycle = False):
        curve = trinity.Tr2ColorCurve()
        curve.length = length
        curve.cycle = cycle
        curve.startValue = startValue
        curve.endValue = endValue
        curve.interpolation = 1
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, 'currentValue', destObject, 'color', curveSet)
        return (curve, binding)



    def CreateScalarCurve(self, destObject, sourceAttr, destAttr, curveSet, length = 1.0, startValue = 0.0, endValue = 0.0, cycle = False, startTangent = 0.0, endTangent = 0.0):
        curve = trinity.Tr2ScalarCurve()
        curve.length = length
        curve.cycle = cycle
        curve.startValue = startValue
        curve.endValue = endValue
        curve.interpolation = 2
        curve.startTangent = startTangent
        curve.endTangent = endTangent
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)



    def CreatePerlinCurve(self, destObject, sourceAttr, destAttr, curveSet, scale = 1000.0, offset = 0.0, N = 2, speed = 1.0, alpha = 1000.0, beta = 5000.0):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.N = N
        curve.speed = speed
        curve.alpha = alpha
        curve.beta = beta
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)



    def CreateSineCurve(self, destObject, sourceAttr, destAttr, curveSet, scale = 1.0, offset = 0.0, speed = 1.0):
        curve = trinity.TriSineCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curveSet.curves.append(curve)
        binding = self.AddBinding(curve, sourceAttr, destObject, destAttr, curveSet)
        return (curve, binding)



    def AddBinding(self, sourceObject, sourceAttribute, destObject, destAttribute, curveSet):
        binding = trinity.TriValueBinding()
        binding.sourceObject = sourceObject
        binding.sourceAttribute = sourceAttribute
        binding.destinationObject = destObject.GetRenderObject()
        binding.destinationAttribute = destAttribute
        curveSet.bindings.append(binding)
        return binding




class ActiveTarget(uicls.Container):
    __guid__ = 'xtriui.ActiveTarget'
    default_name = 'activetarget'
    default_width = 64
    default_height = 64
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        CORNERLEN = 10
        NOTCHLEN = 3
        NOTCHOFFSET = 5
        WIDTH = 1
        for align in (uiconst.TOPLEFT,
         uiconst.TOPRIGHT,
         uiconst.BOTTOMLEFT,
         uiconst.BOTTOMRIGHT):
            uicls.Line(parent=self, align=align, pos=(0,
             0,
             CORNERLEN,
             WIDTH))
            uicls.Line(parent=self, align=align, pos=(0,
             0,
             WIDTH,
             CORNERLEN))

        for align in (uiconst.CENTERLEFT, uiconst.CENTERRIGHT):
            uicls.Line(parent=self, align=align, pos=(0,
             -NOTCHOFFSET,
             NOTCHLEN,
             WIDTH))
            uicls.Line(parent=self, align=align, pos=(0,
             NOTCHOFFSET,
             NOTCHLEN,
             WIDTH))

        for align in (uiconst.CENTERTOP, uiconst.CENTERBOTTOM):
            uicls.Line(parent=self, align=align, pos=(-NOTCHOFFSET,
             0,
             WIDTH,
             NOTCHLEN))
            uicls.Line(parent=self, align=align, pos=(NOTCHOFFSET,
             0,
             WIDTH,
             NOTCHLEN))

        rotate = uicls.Transform(parent=self, name='rotate', pos=(-22, -22, 108, 108), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        sm.GetService('ui').Rotate(rotate, 2.0, timeFunc=blue.os.GetSimTime)
        arrowLeft = uicls.Sprite(parent=rotate, name='arrowLeft', width=9, height=18, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/ActiveTarget/arrows.png')
        arrowLeft.rectLeft = 9
        arrowLeft.rectWidth = 9
        arrowLeft.rectHeight = 18
        arrowTop = uicls.Sprite(parent=rotate, name='arrowTop', width=18, height=9, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ActiveTarget/arrows.png')
        arrowTop.rectTop = 9
        arrowTop.rectWidth = 18
        arrowTop.rectHeight = 9
        arrowRight = uicls.Sprite(parent=rotate, name='arrowRight', width=9, height=18, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/ActiveTarget/arrows.png')
        arrowRight.rectLeft = 0
        arrowRight.rectWidth = 9
        arrowRight.rectHeight = 18
        arrowBottom = uicls.Sprite(parent=rotate, name='arrowBottom', width=18, height=9, align=uiconst.CENTERBOTTOM, texturePath='res:/UI/Texture/classes/ActiveTarget/arrows.png')
        arrowBottom.rectWidth = 18
        arrowBottom.rectHeight = 9
        sm.GetService('ui').BlinkSpriteA(arrowLeft, 1.0, 500.0, 0)
        sm.GetService('ui').BlinkSpriteA(arrowTop, 1.0, 500.0, 0)
        sm.GetService('ui').BlinkSpriteA(arrowRight, 1.0, 500.0, 0)
        sm.GetService('ui').BlinkSpriteA(arrowBottom, 1.0, 500.0, 0)




class TargetLine(uicls.Fill):
    default_state = uiconst.UI_DISABLED
    default_color = (1.0, 1.0, 1.0, 0.2)
    default_align = uiconst.RELATIVE


class Target(uicls.Container):
    __guid__ = 'xtriui.TargetLayout'
    default_name = 'target'
    default_width = 56
    default_height = 56
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        square = uicls.Container(parent=self, name='square', align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        uicls.Frame(parent=square, color=(1.0, 1.0, 1.0, 0.2))
        lines = uicls.Container(parent=self, name='lines', pos=(0, 0, 1, 1), align=uiconst.CENTER)
        linetop = TargetLine(parent=lines, name='linetop', pos=(0, -1208, 1, 1200))
        lineleft = TargetLine(parent=lines, name='lineleft', pos=(-1608, 0, 1600, 1))
        lineright = TargetLine(parent=lines, name='lineright', pos=(9, 0, 1600, 1))
        linebottom = TargetLine(parent=lines, name='linebottom', pos=(0, 9, 1, 1200))
        linehorizontal = TargetLine(parent=lines, name='linehorizontal', pos=(-3, 8, 7, 1))
        linehorizontal = TargetLine(parent=lines, name='linehorizontal', pos=(8, -3, 1, 7))
        linehorizontal = TargetLine(parent=lines, name='linehorizontal', pos=(-8, -3, 1, 7))
        linehorizontal = TargetLine(parent=lines, name='linehorizontal', pos=(-3, -8, 7, 1))
        targeting = uicls.Container(parent=self, name='targeting', pos=(10, 10, 10, 10), state=uiconst.UI_HIDDEN)
        for align in (uiconst.TOPLEFT,
         uiconst.TOPRIGHT,
         uiconst.BOTTOMLEFT,
         uiconst.BOTTOMRIGHT):
            TargetLine(parent=targeting, name='linehorizontal', pos=(7, 0, 3, 10), align=align)
            TargetLine(parent=targeting, name='linehorizontal', pos=(0, 7, 7, 3), align=align)





def _FixLines(target):

    def FindLine(name):
        return uiutil.FindChild(target, 'lines', name)


    (l, r, t, b,) = map(FindLine, ['lineleft',
     'lineright',
     'linetop',
     'linebottom'])
    l.left -= uicore.desktop.width - l.width
    l.width = r.width = uicore.desktop.width
    t.top -= uicore.desktop.height - t.height
    t.height = b.height = uicore.desktop.height



def IsAbandonedContainer(slimItem):
    bp = sm.StartService('michelle').GetBallpark()
    if bp is None:
        return False
    if bp.IsAbandoned(slimItem.itemID):
        return True
    return False



def IsForbiddenContainer(slimItem):
    if slimItem.groupID not in (const.groupWreck, const.groupCargoContainer, const.groupSecureCargoContainer):
        return False
    if not slimItem.ownerID:
        return False
    if slimItem.ownerID == eve.session.charid:
        return False
    if slimItem.corpID and slimItem.corpID == eve.session.corpid:
        return False
    if slimItem.allianceID and slimItem.allianceID == eve.session.allianceid:
        return False
    if sm.GetService('corp').GetMember(slimItem.ownerID):
        return False
    if sm.GetService('fleet').IsMember(slimItem.ownerID):
        return False
    bp = sm.StartService('michelle').GetBallpark()
    if bp is None:
        return False
    if bp.HaveLootRight(slimItem.itemID):
        return False
    return True


exports = util.AutoExports('bracket', locals())

