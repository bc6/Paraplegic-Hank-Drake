import service
import util
import blue
import trinity
import geo2
import uix
import uiutil
import uiconst
import uthread
import base
import xtriui
import state
import listentry
import sys
import _weakref
import bracket
import form
import math
import uicls
import uiconst
from math import sqrt
BRACKETBORDER = 17

class TacticalSvc(service.Service):
    __guid__ = 'svc.tactical'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetPresetsMenu': [],
     'AssureSetup': [],
     'Get': [],
     'ChangeSettings': [],
     'GetAvailableGroups': [],
     'CheckIfGroupIDActive': [],
     'InvalidateFlags': [],
     'WantIt': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnTacticalPresetChange',
     'OnStateChange',
     'OnStateSetupChance',
     'ProcessSessionChange',
     'OnSessionChanged',
     'OnSpecialFX',
     'ProcessOnUIAllianceRelationshipChanged',
     'ProcessRookieStateChange',
     'OnSetCorpStanding',
     'OnSetAllianceStanding',
     'OnAggressionChanged',
     'OnFleetStateChange',
     'OnSlimItemChange',
     'OnPostCfgDataChanged',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnItemChange',
     'OnBallparkCall',
     'OnEwarStart',
     'OnEwarEnd',
     'OnEveGetsFocus',
     'OnContactChange']
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.logme = 0
        self.preset = None
        self.activePreset = None
        self.activeBracketPreset = None
        self.miniflag = settings.user.overview.Get('useSmallColorTags', 0)
        self.smartFilterOn = False
        self.jammers = {}
        self.overviewEntriesToRemove = {}
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.CleanUp()
        if not (eve.rookieState and eve.rookieState < 23):
            self.Setup()



    def Setup(self):
        self.CleanUp()
        self.AssureSetup()
        if eve.session.solarsystemid:
            if settings.user.overview.Get('viewTactical', 0):
                self.Init()
            self.Open()



    def Stop(self, *etc):
        service.Service.Stop(self, *etc)
        self.CleanUp()



    def OnBallparkCall(self, eventName, argTuple):
        if self.sr is None:
            return 
        if eventName == 'SetBallInteractive' and argTuple[1] == 1:
            bp = sm.GetService('michelle').GetBallpark()
            if not bp:
                return 
            slimItem = bp.GetInvItem(argTuple[0])
            if not slimItem:
                return 
            overview = self.GetPanelForUpdate('overview')
            if overview and self.sr is not None:
                self.InvalidateFlags()



    def OnItemChange(self, item, change):
        if const.ixFlag in change and item.flagID == const.flagDroneBay:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckDrones()
            else:
                self.CheckInitDrones()



    def ProcessSessionChange(self, isRemote, session, change):
        if self.logme:
            self.LogInfo('Tactical::ProcessSessionChange', isRemote, session, change)
        if 'solarsystemid' in change:
            self.TearDownOverlay()
        if 'shipid' in change:
            for itemID in self.attackers:
                sm.GetService('state').SetState(itemID, state.threatAttackingMe, 0)

            self.attackers = {}
            droneview = self.GetPanel('droneview')
            overview = self.GetPanelForUpdate('overview')
            if overview:
                overview.FlushEwarStates()
            if droneview:
                if getattr(self, '_initingDrones', False):
                    self.LogInfo('Tactical: ProcessSessionChange: busy initing drones, cannot close the window')
                else:
                    droneview.SelfDestruct()



    def OnSessionChanged(self, isRemote, session, change):
        if eve.session.solarsystemid:
            self.AssureSetup()
            self.Open()
            if settings.user.overview.Get('viewTactical', 0):
                self.Init()
            self.CheckInitDrones()
            overview = self.GetPanelForUpdate('overview')
            if 'shipid' in change and overview:
                overview.UpdateAll()
            self.InvalidateFlags()
        else:
            self.CleanUp()



    def OnSlimItemChange(self, oldSlim, newSlim):
        if not eve.session.solarsystemid:
            return 
        update = 0
        if getattr(newSlim, 'allianceID', None) and newSlim.allianceID != getattr(oldSlim, 'allianceID', None):
            update = 1
        elif newSlim.corpID and newSlim.corpID != oldSlim.corpID:
            update = 1
        elif newSlim.charID != oldSlim.charID:
            update = 1
        elif newSlim.ownerID != oldSlim.ownerID:
            update = 1
        elif getattr(newSlim, 'lootRights', None) != getattr(oldSlim, 'lootRights', None):
            update = 1
        elif getattr(newSlim, 'isEmpty', None) != getattr(oldSlim, 'isEmpty', None):
            update = 1
        if update:
            updateOverview = 0
            overview = self.GetPanelForUpdate('overview')
            if not overview:
                return 
            ball = sm.GetService('michelle').GetBall(newSlim.itemID)
            if not ball:
                return 
            overviewEntry = self.GetOverviewEntry(newSlim.itemID)
            filtered = self.GetFilteredStatesFunctionNames()
            wantIt = self.WantIt(newSlim, filtered)
            (columns, displayColumns,) = self.GetColumns()
            newData = self.GetEntryData(newSlim, ball)
            overview.UpdateSortData(newData, columns)
            if overviewEntry:
                if wantIt:
                    overviewEntry.update(newData)
                    if overviewEntry.panel:
                        overviewEntry.panel.Load(overviewEntry)
                else:
                    overview.sr.scroll.RemoveEntries([overviewEntry])
            elif wantIt:
                overview.sr.scroll.AddEntries(-1, [listentry.Get('TacticalItem', data=newData)])
                overview.sr.scroll.ShowHint()
            self.InvalidateFlags()
        else:
            overviewEntry = self.GetOverviewEntry(newSlim.itemID)
            if overviewEntry:
                overviewEntry.slimItem = _weakref.ref(newSlim)



    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            overviewEntry = self.GetOverviewEntry(data[0])
            if overviewEntry:
                slimItem = overviewEntry.slimItem()
                if not slimItem:
                    return 
                tickerName = ''
                if getattr(slimItem, 'corpID', None):
                    tickerName = '[' + cfg.corptickernames.Get(slimItem.corpID).tickerName + ']'
                name = uix.GetSlimItemName(slimItem)
                overviewEntry.Set('sort_' + mls.UI_GENERIC_NAME, name.lower())
                overviewEntry.Set(mls.UI_GENERIC_NAME, name)
                overviewEntry.NAME = name
                overviewEntry.name = name
                overviewEntry.hint = sm.GetService('bracket').GetBracketName(slimItem.itemID)
                if overviewEntry.panel:
                    overviewEntry.panel.Load(overviewEntry)



    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if not eve.session.solarsystemid:
            return 
        self.InvalidateFlags()



    def ProcessRookieStateChange(self, state):
        if eve.session.solarsystemid:
            if not not (eve.rookieState and eve.rookieState < 23):
                self.CleanUp()
            elif not self.GetPanel('overview'):
                self.Setup()



    def OnContactChange(self, contactIDs, contactType = None):
        if not eve.session.solarsystemid:
            return 
        self.InvalidateFlags()



    def OnSetCorpStanding(self, *args):
        if not eve.session.solarsystemid:
            return 
        self.InvalidateFlags()



    def OnSetAllianceStanding(self, *args):
        if not eve.session.solarsystemid:
            return 
        self.InvalidateFlags()



    def OnAggressionChanged(self, solarsystemID, aggressors):
        if not eve.session.solarsystemid:
            return 
        uthread.new(self.DelayedOnAggressionChanged)



    def DelayedOnAggressionChanged(self):
        if getattr(self, 'delayedOnAggressionChanged', False):
            return 
        setattr(self, 'delayedOnAggressionChanged', True)
        blue.pyos.synchro.Sleep(1000)
        self.InvalidateFlags()
        setattr(self, 'delayedOnAggressionChanged', False)



    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, area, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, graphicInfo = None):
        if targetID == eve.session.shipid and isOffensive:
            attackerID = shipID
            attackTime = startTime
            attackRepeat = repeat
            shipItem = sm.StartService('michelle').GetItem(shipID)
            if shipItem and shipItem.categoryID == const.categoryStructure:
                attackerID = moduleID
                attackTime = 0
                attackRepeat = 0
            data = self.attackers.get(attackerID, [])
            key = (moduleID,
             guid,
             attackTime,
             duration,
             attackRepeat)
            if active and shipID != session.shipid:
                if key not in data:
                    data.append(key)
                sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 1)
            else:
                toRemove = None
                for signature in data:
                    if signature[0] == key[0] and signature[1] == key[1] and signature[2] == key[2] and signature[3] == key[3]:
                        toRemove = signature
                        break

                if toRemove is not None:
                    data.remove(toRemove)
                if not data:
                    sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 0)
            self.attackers[attackerID] = data



    def LayoutButtons(self, parent, state = None, maxHeight = None):
        if parent is None:
            return 
        (l, t, w, h,) = parent.GetAbsolute()
        colwidth = 33
        if w <= colwidth:
            return 
        perRow = w / colwidth
        small = len(parent.children) / float(perRow) > 2.0
        size = [32, 24][small]
        if maxHeight and size > maxHeight:
            size = 24
        if len(parent.children) * (size + 1) + 1 > w:
            size = 24
        left = 1
        top = 0
        parent.height = size + 1
        for icon in parent.children:
            if l + left + size + 1 >= l + w:
                left = 1
                top += size + 1
                parent.height += size + 1
            icon.left = left
            icon.top = top
            icon.width = size
            icon.height = size
            if state is not None:
                icon.state = state
            left += size + 1




    def CheckInitDrones(self):
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if mySlim and mySlim.groupID != const.groupCapsule:
            dronesInBay = eve.GetInventoryFromId(eve.session.shipid).ListDroneBay()
            if dronesInBay:
                self.InitDrones()
            else:
                myDrones = sm.GetService('michelle').GetDrones()
                if myDrones:
                    self.InitDrones()



    def Open(self):
        self.InitSelectedItem()
        self.InitOverview()
        self.CheckInitDrones()



    def GetMain(self):
        if self and getattr(self.sr, 'mainParent', None):
            return self.sr.mainParent



    def OnStateChange(self, itemID, flag, true, *args):
        uthread.new(self._OnStateChange, itemID, flag, true, *args)



    def _OnStateChange(self, itemID, flag, true, *args):
        if not eve.session.solarsystemid:
            return 
        if not self or getattr(self, 'sr', None) is None:
            return 
        if self.logme:
            self.LogInfo('Tactical::OnStateChange', itemID, flag, true, *args)
        if getattr(self, 'inited', 0) and flag == state.selected and true:
            self.ShowDirectionTo(itemID)
        overviewEntry = self.GetOverviewEntry(itemID)
        if overviewEntry and overviewEntry.panel:
            overviewEntry.panel.OnStateChange(itemID, flag, true, *args)



    def OnFleetStateChange(self, fleetState):
        if fleetState:
            for (itemID, tag,) in fleetState.targetTags.iteritems():
                overviewEntry = self.GetOverviewEntry(itemID)
                if not overviewEntry:
                    continue
                overviewEntry.Set('sort_' + mls.UI_GENERIC_TAG, tag)
                overviewEntry.TAG = tag
                if overviewEntry.panel:
                    overviewEntry.panel.Load(overviewEntry)




    def OnTacticalPresetChange(self, label, set):
        t = uthread.new(self.OnTacticalPresetChange_thread, label, set)
        t.context = 'tactical::OnTacticalPresetChange'



    def OnTacticalPresetChange_thread(self, label, set):
        if self.logme:
            self.LogInfo('Tactical::OnTacticalPresetChange', label, set)
        if self.inited:
            self.InitConnectors()
        overview = self.GetPanelForUpdate('overview')
        if overview:
            overview.UpdateAll()
            if label == 'ccp_notsaved':
                label = mls.UI_GENERIC_NOTSAVED
            overviewName = self.overviewPresetSvc.GetDefaultOverviewName(label)
            if overviewName is not None:
                label = overviewName
            overview.sr.presetMenu.hint = label
            overview.SetCaption(mls.UI_GENERIC_OVERVIEW + ' (' + label + ')')



    def OnStateSetupChance(self, what):
        self.InvalidateFlags()
        if self.inited:
            self.InitConnectors()
        overview = self.GetPanelForUpdate('overview')
        if overview:
            overview.UpdateAll()



    def Toggle(self):
        pass



    def BlinkHeader(self, key):
        if not self or self.sr is None:
            return 
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            panel.Blink()



    def IsExpanded(self, key):
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            return panel.sr.main.state == uiconst.UI_PICKCHILDREN



    def AssureSetup(self):
        if self.logme:
            self.LogInfo('Tactical::AssureSetup')
        if getattr(self, 'setupAssured', None):
            return 
        if getattr(self, 'sr', None) is None:
            self.sr = uiutil.Bunch()
        self.setupAssured = 1



    def CleanUp(self):
        if self.logme:
            self.LogInfo('Tactical::CleanUp')
        self.sr = None
        self.numberShader = None
        self.planeShader = None
        self.circleShader = None
        self.lines = None
        self.targetingRanges = None
        self.updateDirectionTimer = None
        self.genericUpdateTimer = None
        self.toggling = 0
        self.setupAssured = 0
        self.lastFactor = None
        self.groupList = None
        self.groupIDs = []
        self.direction = None
        self.direction2 = None
        self.intersections = []
        self.threats = {}
        self.attackers = {}
        self.maxConnectorDist = 150000.0
        self.TearDownOverlay()
        uicore.layer.tactical.Flush()
        self.dronesInited = 0
        self.busy = 0



    def CheckFiltered(self, slimItem, filtered):
        stateSvc = sm.GetService('state')
        for functionName in filtered:
            f = getattr(stateSvc, 'Check' + functionName, None)
            if f is not None and f(slimItem):
                return True
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)

        return False



    def RefreshOverview(self):
        overview = self.GetPanelForUpdate('overview')
        if overview:
            overview.UpdateAll()



    def UpdateOverviewForOneCharacter(self, member):
        overview = self.GetPanelForUpdate('overview')
        if overview:
            overview.UpdateForOneCharacter(member.charID)



    def OnFleetJoin_Local(self, member, *args):
        self.UpdateOverviewForOneCharacter(member)



    def OnFleetLeave_Local(self, member, *args):
        self.UpdateOverviewForOneCharacter(member)



    def UpdateStates(self, slimItem, uiwindow):
        if uiwindow is None or uiwindow.destroyed:
            return 
        try:
            if uiwindow.sr.icon is None or not slimItem:
                return 
            bg = self.UpdateBackground(slimItem, uiwindow)
            if uiwindow.updateItem:
                icon = self.UpdateIcon(slimItem, uiwindow)
                if slimItem and (slimItem.ownerID and util.IsNPC(slimItem.ownerID) or slimItem.charID and util.IsNPC(slimItem.charID) and slimItem.groupID != const.groupAgentsinSpace):
                    flag = 0
                    if getattr(uiwindow.sr, 'flag', None) is not None:
                        flag = uiwindow.sr.flag
                        uiwindow.sr.flag = None
                        flag.Close()
                    bg = 0
                    if getattr(uiwindow.sr, 'bgColor', None) is not None:
                        bgColor = uiwindow.sr.bgColor
                        uiwindow.sr.bgColor = None
                        bgColor.Close()
                else:
                    flag = self.UpdateFlag(slimItem, uiwindow)
                if uiwindow.sr.node:
                    uiwindow.sr.node.Set('sort_' + mls.UI_GENERIC_ICON, (flag,
                     icon,
                     bg,
                     slimItem.typeID))
        except AttributeError:
            if uiwindow.destroyed:
                return 
            raise 



    def UpdateBackground(self, slimItem, uiwindow):
        stateSvc = sm.GetService('state')
        flag = stateSvc.CheckStates(slimItem, 'background')
        if flag and flag != -1:
            (r, g, b, a,) = stateSvc.GetStateColor(flag)
            a = a * 0.5
            blink = stateSvc.GetStateBlink('background', flag)
            if not uiwindow.sr.bgColor:
                uiwindow.sr.bgColor = uicls.Fill(name='flag%s_%s' % (flag, blink), state=uiconst.UI_DISABLED, color=(r,
                 g,
                 b,
                 a))
                uiwindow.background.append(uiwindow.sr.bgColor)
            else:
                uiwindow.sr.bgColor.SetRGBA(r, g, b, a)
            if blink:
                sm.GetService('ui').BlinkSpriteRGB(uiwindow.sr.bgColor, r, g, b, 750, None, passColor=0)
                sm.GetService('ui').BlinkSpriteA(uiwindow.sr.bgColor, a, 750, None, passColor=0)
            else:
                sm.GetService('ui').StopBlink(uiwindow.sr.bgColor)
        elif uiwindow.sr.bgColor:
            uiwindow.background.remove(uiwindow.sr.bgColor)
            u = uiwindow.sr.bgColor
            uiwindow.sr.bgColor = None
            u.Close()
        return flag



    def UpdateIcon(self, slimItem, uiwindow):
        if uiwindow is None or uiwindow.destroyed:
            return 
        if uiwindow.sr.icon is None or not slimItem:
            return 
        colorFlag = 0
        if slimItem.categoryID == const.categoryEntity and slimItem.typeID:
            tmp = [ each for each in sm.GetService('godma').GetType(slimItem.typeID).displayAttributes if each.attributeID == const.attributeEntityBracketColour ]
            for attr in tmp:
                if attr.value >= 1:
                    colorFlag = attr.value
                    break

        if bracket.IsForbiddenContainer(slimItem):
            colorFlag = -1
        if not colorFlag:
            if slimItem.groupID == const.groupStargate:
                destinationPath = sm.GetService('starmap').GetDestinationPath()
                if slimItem.jumps[0].locationID in destinationPath:
                    colorFlag = -1
        col = {-1: (1.0, 1.0, 0.0),
         1: (1.0, 0.1, 0.1)}.get(colorFlag, (1.0, 1.0, 1.0))
        uiwindow.SetColor(*col)
        if slimItem.groupID == const.groupWreck and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            uiwindow.Viewed(True)
        return colorFlag



    def UpdateFlag(self, slimItem, uiwindow):
        icon = None
        if uiwindow.sr.icon.state != uiconst.UI_HIDDEN:
            icon = uiwindow.sr.icon
        elif getattr(uiwindow.sr, 'tempIcon', None) is not None and uiwindow.sr.tempIcon.state != uiconst.UI_HIDDEN:
            icon = uiwindow.sr.tempIcon
        stateSvc = sm.GetService('state')
        if icon is None:
            flag = -1
        else:
            flag = stateSvc.CheckStates(slimItem, 'flag')
        if flag and flag != -1:
            if uiwindow is None or uiwindow.destroyed:
                return 
            if icon is None or not slimItem:
                return 
            props = stateSvc.GetStateProps(flag)
            filterName = props[0]
            if filterName:
                if uiwindow.sr.flag is None:
                    uiwindow.sr.flag = self.GetFlagUI(uiwindow)
                col = stateSvc.GetStateColor(flag)
                blink = stateSvc.GetStateBlink('flag', flag)
                uiwindow.sr.flag.children[1].color.SetRGB(*col)
                uiwindow.sr.flag.children[1].color.a *= 0.75
                if blink:
                    sm.GetService('ui').BlinkSpriteA(uiwindow.sr.flag.children[0], 1.0, 500, None, passColor=0)
                    sm.GetService('ui').BlinkSpriteA(uiwindow.sr.flag.children[1], uiwindow.sr.flag.children[0].color.a, 500, None, passColor=0)
                else:
                    sm.GetService('ui').StopBlink(uiwindow.sr.flag.children[0])
                    sm.GetService('ui').StopBlink(uiwindow.sr.flag.children[1])
                props = stateSvc.GetStateProps(flag)
                self.UpdateFlagPositions(uiwindow, icon)
                iconNum = 0 if self.miniflag else props[4] + 1
                uiwindow.sr.flag.children[0].rectLeft = iconNum * 10
                uiwindow.sr.flag.state = uiconst.UI_DISABLED
        elif getattr(uiwindow.sr, 'flag', None) is not None:
            flag = uiwindow.sr.flag
            uiwindow.sr.flag = None
            flag.Close()
        return flag



    def GetFlagUI(self, parent):
        flag = uicls.Container(parent=parent, name='flag', pos=(0, 0, 10, 10), align=uiconst.TOPLEFT, idx=0)
        icon = uicls.Sprite(parent=flag, name='icon', pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png')
        icon.rectWidth = 10
        icon.rectHeight = 10
        uicls.Fill(parent=flag)
        return flag



    def UpdateFlagPositions(self, uiwindow, icon = None):
        if icon is None:
            icon = util.GetAttrs(uiwindow, 'sr', 'icon')
        flag = util.GetAttrs(uiwindow, 'sr', 'flag')
        if icon and flag:
            if self.miniflag:
                uiwindow.sr.flag.width = uiwindow.sr.flag.height = 5
                uiwindow.sr.flag.left = uiwindow.sr.icon.left + 10
                uiwindow.sr.flag.top = uiwindow.sr.icon.top + 10
            else:
                uiwindow.sr.flag.width = uiwindow.sr.flag.height = 9
                uiwindow.sr.flag.left = uiwindow.sr.icon.left + 9
                uiwindow.sr.flag.top = uiwindow.sr.icon.top + 8



    def InvalidateFlags(self):
        if not eve.session.solarsystemid:
            return 
        self.miniflag = settings.user.overview.Get('useSmallColorTags', 0)
        sm.GetService('bracket').RenewFlags()
        overview = self.GetPanelForUpdate('overview')
        if overview:
            for entry in overview.sr.scroll.GetNodes():
                if entry.updateItem:
                    slimItem = entry.slimItem()
                    if slimItem and entry.panel:
                        xtriui.UpdateEntry.Load_update(entry.panel, slimItem)




    def InvalidateFlagsLimited(self):
        if not eve.session.solarsystemid:
            return 
        self.miniflag = settings.user.overview.Get('useSmallColorTags', 0)
        sm.GetService('bracket').RenewFlags()



    def InvalidateFlagsExtraLimited(self, charID):
        if not eve.session.solarsystemid:
            return 
        self.miniflag = settings.user.overview.Get('useSmallColorTags', 0)
        sm.GetService('bracket').RenewSingleFlag(charID)



    def ShowDirectionTo(self, itemID):
        if self.logme:
            self.LogInfo('Tactical::ShowDirectionTo', itemID)
        if self.direction is None:
            return 
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        self.direction.display = False
        if self.directionCurveSet is not None:
            self.usedCurveSets.remove(self.directionCurveSet)
            scene2.curveSets.remove(self.directionCurveSet)
            self.directionCurveSet = None
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        ball = ballpark.GetBall(itemID)
        if ball is None or ball.model is None or ball.IsCloaked():
            return 
        meball = ballpark.GetBall(eve.session.shipid)
        if not meball or not meball.model:
            return 
        distVec = geo2.Vector(ball.x - meball.x, ball.y - meball.y, ball.z - meball.z)
        if geo2.Vec3Length(distVec) >= 200000.0:
            return 
        set = trinity.TriCurveSet()
        vs = trinity.TriVectorSequencer()
        vc = trinity.TriVectorCurve()
        vc.value.SetXYZ(1.0, 1.0, 1.0)
        vs.functions.append(ball)
        vs.functions.append(vc)
        bind = trinity.TriValueBinding()
        bind.destinationObject = self.direction
        bind.destinationAttribute = 'scaling'
        bind.sourceObject = vs
        bind.sourceAttribute = 'value'
        set.curves.append(vs)
        set.curves.append(vc)
        set.bindings.append(bind)
        set.name = str(ball.id) + '_direction'
        set.Play()
        scene2.curveSets.append(set)
        self.usedCurveSets.append(set)
        self.directionCurveSet = set
        self.direction.display = True
        self.UpdateDirection()



    def UpdateDirection(self):
        if self.logme:
            self.LogInfo('Tactical::UpdateDirection')
        if self.direction is None or not self.direction.display:
            return 
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        ball = ballpark.GetBall(sm.GetService('state').GetExclState(state.selected))
        if ball is None:
            return 
        meball = ballpark.GetBall(eve.session.shipid)
        if not meball:
            return 
        distVec = geo2.Vector(ball.x - meball.x, ball.y - meball.y, ball.z - meball.z)
        if ball.IsCloaked() or geo2.Vec3Length(distVec) > 200000.0:
            self.updateDirectionTimer = None
            self.direction.display = False
            if self.directionCurveSet is not None:
                self.usedCurveSets.remove(self.directionCurveSet)
                scene2.curveSets.remove(self.directionCurveSet)
                self.directionCurveSet = None
                return 
        if self.updateDirectionTimer is None:
            self.updateDirectionTimer = base.AutoTimer(111, self.UpdateDirection)



    def GetAllColumns(self):
        allColumns = ['ICON',
         'DISTANCE',
         'NAME',
         'TYPE',
         'TAG',
         'CORPORATION',
         'ALLIANCE',
         'FACTION',
         'MILITIA',
         'SIZE',
         'VELOCITY',
         'RADIALVELOCITY',
         'TRANSVERSALVELOCITY',
         'ANGULARVELOCITY']
        return allColumns



    def GetColumns(self):
        default = self.GetDefaultVisibleColumns()
        userSet = settings.user.overview.Get('overviewColumns', None)
        if userSet is None:
            userSet = default
        userSetOrder = self.GetColumnOrder()
        return ([ label for label in userSetOrder if label in userSet ], [ getattr(mls, 'UI_GENERIC_' + label, label) for label in userSetOrder if label in userSet ])



    def GetColumnOrder(self):
        ret = settings.user.overview.Get('overviewColumnOrder', None)
        if ret is None:
            return self.GetAllColumns()
        return ret



    def GetDefaultVisibleColumns(self):
        default = ['ICON',
         'DISTANCE',
         'NAME',
         'TYPE']
        return default



    def GetNotSavedTranslations(self):
        ret = [u'Not saved', u'Nicht gespeichert', u'\u672a\u30bb\u30fc\u30d6']
        return ret



    def PrimePreset(self):
        if getattr(self, 'activePreset', None) is None:
            self.activePreset = settings.user.overview.Get('activeOverviewPreset', 'default')
        if getattr(self, 'preset', None) is None or self.preset[0] != self.activePreset:
            presets = settings.user.overview.Get('overviewPresets', {})
            for label in self.GetNotSavedTranslations():
                if label in presets.keys():
                    presets['ccp_notsaved'] = presets[label]
                    del presets[label]

            if self.activePreset in self.overviewPresetSvc.GetDefaultOverviewNameList():
                presets[self.activePreset] = {'groups': self.overviewPresetSvc.GetDefaultOverviewGroups(self.activePreset)}
            default = self.overviewPresetSvc.GetDefaultOverviewGroups('default')
            self.preset = (self.activePreset,
             presets.get(self.activePreset, {'groups': default}),
             self.activeBracketPreset,
             presets.get(self.activeBracketPreset, {'groups': default}))



    def GetGroups(self):
        self.PrimePreset()
        return self.preset[1]['groups']



    def SetNPCGroups(self):
        sendGroupIDs = []
        userSettings = self.GetGroups()
        for (cat, groupdict,) in util.GetNPCGroups().iteritems():
            for (groupname, groupids,) in groupdict.iteritems():
                for groupid in groupids:
                    if groupid in userSettings:
                        sendGroupIDs += groupids
                        break



        if sendGroupIDs:
            self.ChangeSettings('groups', sendGroupIDs, 1)



    def GetBracketGroups(self):
        self.PrimePreset()
        return self.preset[3]['groups']



    def GetValidGroups(self, isBracket = False):
        groups = set(self.GetBracketGroups()) if isBracket else set(self.GetGroups())
        return groups.intersection(self.GetAvailableGroups(getIds=True))



    def GetFilteredStates(self, isBracket = False):
        self.PrimePreset()
        if isBracket:
            return self.preset[3].get('filteredStates', [])
        else:
            return self.preset[1].get('filteredStates', [])



    def GetEwarFiltered(self):
        self.PrimePreset()
        return self.preset[1].get('smartFilters', [])



    def GetFilteredStatesFunctionNames(self, isBracket = False):
        return [ sm.GetService('state').GetStateProps(flag)[1] for flag in self.GetFilteredStates(isBracket=isBracket) ]



    def Get(self, what, default):
        if self.logme:
            self.LogInfo('Tactical::Get', what, default)
        return getattr(self, what, default)



    def GetPresetsMenu(self):
        if self.logme:
            self.LogInfo('Tactical::GetPresetsMenu')
        p = settings.user.overview.Get('overviewPresets', {}).keys()
        p.sort()
        defaultm = []
        for name in self.overviewPresetSvc.GetDefaultOverviewNameList():
            if name in p:
                p.remove(name)
            overviewName = self.overviewPresetSvc.GetDefaultOverviewName(name)
            if overviewName is not None:
                defaultm.append((overviewName, self.LoadPreset, (name,)))

        m = []
        dm = []
        for label in p:
            if label == 'ccp_notsaved':
                continue
            m.append((mls.UI_CMD_LOAD + ' ' + label, self.LoadPreset, (label,)))
            dm.append((label, self.DeletePreset, (label,)))

        m.append(None)
        m.append((mls.UI_CMD_LOADDEFAULT, defaultm))
        if dm:
            m.append(None)
            m.append((mls.UI_CMD_DELETE, dm))
        bracketMgr = sm.GetService('bracket')
        if not bracketMgr.ShowingAll():
            m.append((mls.UI_CMD_SHOWALLBRACKETS, bracketMgr.ShowAll))
        else:
            m.append((mls.UI_CMD_STOPSHOWALLBRACKETS, bracketMgr.StopShowingAll))
        if not bracketMgr.ShowingNone():
            m.append((mls.UI_CMD_SHOWNOBRACKETS, bracketMgr.ShowNone))
        else:
            m.append((mls.UI_CMD_STOPSHOWNOBRACKETS, bracketMgr.StopShowingNone))
        m += [None, (mls.UI_CMD_SAVECURRENTTYPESELECTION, self.SavePreset), (mls.UI_CMD_OPENOVERVIEWSETTINGS, self.OpenSettings)]
        m += [None, (mls.UI_CMD_EXPORTOVERVIEWSETTINGS, self.ExportOverviewSettings), (mls.UI_CMD_IMPORTOVERVIEWSETTINGS, self.ImportOverviewSettings)]
        return m



    def OpenSettings(self, *args):
        uicore.cmd.OpenOverviewSettings()



    def LoadPreset(self, label, updateTabSettings = True):
        if self.logme:
            self.LogInfo('Tactical::LoadPreset', label)
        presets = settings.user.overview.Get('overviewPresets', {})
        defaultPresetNames = self.overviewPresetSvc.GetDefaultOverviewNameList()
        if label is not 'ccp_notsaved' and label not in presets and label not in defaultPresetNames:
            return 
        if updateTabSettings:
            overview = self.GetPanelForUpdate('overview')
            if overview is not None and hasattr(overview, 'GetSelectedTabKey'):
                tabKey = overview.GetSelectedTabKey()
                tabSettings = settings.user.overview.Get('tabsettings', {})
                if tabKey in tabSettings.keys():
                    tabSettings[tabKey]['overview'] = label
                sm.ScatterEvent('OnOverviewTabChanged', tabSettings, None)
        settings.user.overview.Set('activeOverviewPreset', label)
        self.activePreset = label
        self.preset = None
        self.PrimePreset()
        sm.ScatterEvent('OnTacticalPresetChange', label, None)



    def LoadBracketPreset(self, label):
        if self.logme:
            self.LogInfo('Tactical::LoadBracketPreset', label)
        presets = settings.user.overview.Get('overviewPresets', {})
        defaultPresetNames = self.overviewPresetSvc.GetDefaultOverviewNameList()
        if label not in ('ccp_notsaved', None) and label not in presets and label not in defaultPresetNames:
            return 
        settings.user.overview.Set('activeBracketPreset', label)
        self.activeBracketPreset = label
        self.preset = None
        self.PrimePreset()
        sm.GetService('bracket').Reload()



    def SavePreset(self, *args):
        if self.logme:
            self.LogInfo('Tactical::SavePreset')
        ret = uix.NamePopup(mls.UI_INFLIGHT_TYPELABELFORPRESET, mls.UI_INFLIGHT_TYPELABEL, maxLength=20)
        if ret:
            presetName = ret['name'].lower()
            if presetName == 'default':
                presetName = 'default2'
            presets = settings.user.overview.Get('overviewPresets', {})
            if presetName in presets:
                if eve.Message('AlreadyHaveLabel', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
            else:
                presets[presetName] = {}
            presets[presetName]['groups'] = self.GetGroups()[:]
            presets[presetName]['filteredStates'] = self.GetFilteredStates()[:]
            presets[presetName]['ewarFilters'] = self.GetEwarFiltered()[:]
            settings.user.overview.Set('overviewPresets', presets)
            sm.ScatterEvent('OnOverviewPresetSaved')
            self.LoadPreset(presetName)



    def DeletePreset(self, dlabel):
        if self.logme:
            self.LogInfo('Tactical::DeletePreset', dlabel)
        presets = settings.user.overview.Get('overviewPresets', {})
        if dlabel in presets:
            del presets[dlabel]
        settings.user.overview.Set('overviewPresets', presets)
        if dlabel == self.activePreset:
            self.LoadPreset('default')
        sm.ScatterEvent('OnOverviewPresetSaved')



    def ChangeSettings(self, what, value, add):
        if self.logme:
            self.LogInfo('Tactical::ChangeSettings', what, value, add)
        current = None
        if what == 'filteredStates':
            current = self.GetFilteredStates()[:]
        elif what == 'groups':
            current = self.GetGroups()[:]
        elif what == 'smartFilters':
            current = self.GetEwarFiltered()[:]
        if current is None:
            return 
        if add:
            if type(value) == list:
                for each in value:
                    if each not in current:
                        current.append(each)

            elif value not in current:
                current.append(value)
        elif type(value) == list:
            for each in value:
                while each in current:
                    current.remove(each)


        else:
            while value in current:
                current.remove(value)

        presets = settings.user.overview.Get('overviewPresets', {})
        activePreset = self.preset[1].copy()
        activePreset[what] = current
        presets['ccp_notsaved'] = activePreset
        settings.user.overview.Set('overviewPresets', presets)
        self.LoadPreset('ccp_notsaved')



    def SetSettings(self, what, set):
        if what == 'groups':
            preset = self.preset[1].copy()
            preset['groups'] = set
            presets = settings.user.overview.Get('overviewPresets', {})
            presets['ccp_notsaved'] = preset
            settings.user.overview.Set('overviewPresets', presets)
            self.LoadPreset('ccp_notsaved')



    def ToggleOnOff(self):
        current = settings.user.overview.Get('viewTactical', 0)
        settings.user.overview.Set('viewTactical', not current)
        if not current:
            self.Init()
        elif self.inited:
            self.TearDownOverlay()
        sm.ScatterEvent('OnTacticalOverlayChange', not current)



    def CheckInit(self):
        if eve.session.solarsystemid and settings.user.overview.Get('viewTactical', 0):
            self.Init()



    def TearDownOverlay(self):
        connectors = getattr(self, 'connectors', None)
        if connectors:
            del connectors.children[:]
        self.connectors = None
        self.TargetingRange = None
        self.OptimalRange = None
        self.FalloffRange = None
        self.direction = None
        self.directionCurveSet = None
        self.updateDirectionTimer = None
        self.circles = None
        arena = getattr(self, 'arena', None)
        self.arena = None
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        if scene2 and arena and arena in scene2.objects:
            scene2.objects.remove(arena)
        usedCurves = getattr(self, 'usedCurveSets', None)
        if scene2 is not None and usedCurves is not None:
            for cs in self.usedCurveSets:
                scene2.curveSets.remove(cs)

        self.usedCurveSets = []
        self.inited = False



    def AddCircleToLineSet(self, set, radius, color):
        tessSteps = int(math.sqrt(radius))
        for t in range(0, tessSteps):
            alpha0 = 2.0 * math.pi * float(t) / tessSteps
            alpha1 = 2.0 * math.pi * float(t + 1) / tessSteps
            x0 = radius * math.cos(alpha0)
            y0 = radius * math.sin(alpha0)
            x1 = radius * math.cos(alpha1)
            y1 = radius * math.sin(alpha1)
            set.AddLine((x0, 0.0, y0), color, (x1, 0.0, y1), color)




    def InitDistanceCircles(self):
        if self.circles is None:
            return 
        self.circles.ClearLines()
        colorDark = (50.0 / 255.0,
         50.0 / 255.0,
         50.0 / 255.0,
         100.0 / 255.0)
        colorBright = (150.0 / 255.0,
         150.0 / 255.0,
         150.0 / 255.0,
         100.0 / 255.0)
        self.AddCircleToLineSet(self.circles, 5000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 10000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 20000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 30000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 40000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 50000.0, colorBright)
        self.AddCircleToLineSet(self.circles, 75000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 100000.0, colorBright)
        self.AddCircleToLineSet(self.circles, 150000.0, colorDark)
        self.AddCircleToLineSet(self.circles, 200000.0, colorDark)
        self.circles.SubmitChanges()



    def InitDirectionLines(self):
        if self.direction is None:
            return 
        self.direction.ClearLines()
        color = (0.2, 0.2, 0.2, 1.0)
        self.direction.AddLine((0.0, 0.0, 0.0), color, (1.0, 1.0, 1.0), color)
        self.direction.display = False
        self.direction.SubmitChanges()



    def Init(self):
        if self.logme:
            self.LogInfo('Tactical::Init')
        if not self.inited:
            rm = []
            scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
            if scene2 is None:
                return 
            for each in scene2.objects:
                if each.name == 'TacticalMap':
                    rm.append(each)

            for each in rm:
                scene2.objects.remove(each)

            self.arena = trinity.Load('res:/UI/Inflight/tactical/TacticalMap.red')
            self.arena.name = 'TacticalMap'
            self.usedCurveSets = []
            self.directionCurveSet = None
            self.updateDirectionTimer = None
            for child in self.arena.children:
                if child.name == 'connectors':
                    self.connectors = child
                elif child.name == 'TargetingRange':
                    self.TargetingRange = child
                elif child.name == 'OptimalRange':
                    self.OptimalRange = child
                elif child.name == 'FalloffRange':
                    self.FalloffRange = child
                elif child.name == 'circleLineSet':
                    self.circles = child
                elif child.name == 'directionLineSet':
                    self.direction = child

            self.InitDistanceCircles()
            self.InitDirectionLines()
            scene2.objects.append(self.arena)
            self.inited = True
            self.InitConnectors()
            self.UpdateTargetingRanges()



    def UpdateTargetingRanges(self, module = None):
        if not self or not self.inited:
            self.targetingRanges = None
            return 
        self.targetingRanges = None
        self.intersections = []
        if not eve.session.shipid:
            self.FalloffRange.display = False
            self.OptimalRange.display = False
            self.TargetingRange.display = False
            self.UpdateDirection()
            return 
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        maxTargetRange = ship.maxTargetRange * 2
        self.TargetingRange.display = True
        self.TargetingRange.scaling = (maxTargetRange, maxTargetRange, maxTargetRange)
        self.intersections = [ship.maxTargetRange]
        if module is None:
            self.FalloffRange.display = False
            self.OptimalRange.display = False
        elif module.maxRange:
            optimal = module.maxRange * 2
            falloff = (module.maxRange + module.falloff) * 2
            self.FalloffRange.scaling = (falloff, falloff, falloff)
            self.FalloffRange.display = True
        else:
            optimal = 0
            for attribute in module.displayAttributes:
                if attribute.attributeID in (const.attributeEmpFieldRange,
                 const.attributePowerTransferRange,
                 const.attributeWarpScrambleRange,
                 const.attributeMaxNeutralizationRange):
                    optimal = attribute.value * 2
                    break

            self.FalloffRange.display = False
            self.OptimalRange.display = False
        if optimal:
            self.OptimalRange.scaling = (optimal, optimal, optimal)
            self.OptimalRange.display = True
        self.intersections += [module.maxRange, module.maxRange + module.falloff]
        self.UpdateDirection()



    def ResetTargetingRanges(self):
        self.targetingRanges = base.AutoTimer(5000, self.UpdateTargetingRanges)



    def GetPanelForUpdate(self, what):
        panel = self.GetPanel(what)
        if panel and not panel.IsCollapsed() and not panel.IsMinimized():
            return panel



    def GetPanel(self, what):
        wnd = sm.GetService('window').GetWindow(what)
        if wnd and not wnd.destroyed:
            return wnd



    def InitDrones(self):
        if getattr(self, '_initingDrones', False):
            return 
        self._initingDrones = True
        try:
            sm.GetService('window').GetWindow('droneview', decoClass=form.DroneView, create=1, expandIfCollapsed=False, panelID='droneview', showActions=False, panelName=mls.UI_GENERIC_DRONES)

        finally:
            self._initingDrones = False




    def InitOverview(self):
        sm.GetService('window').GetWindow('overview', decoClass=form.OverView, create=1, expandIfCollapsed=False, panelID='overview', showActions=False, panelName=mls.UI_GENERIC_OVERVIEW)



    def InitSelectedItem(self):
        sm.GetService('window').GetWindow('selecteditemview', decoClass=form.ActiveItem, create=1, expandIfCollapsed=False, panelname=mls.UI_GENERIC_SELECTEDITEM)



    def InitConnectors(self):
        if self.logme:
            self.LogInfo('Tactical::InitConnectors')
        if not self.inited:
            return 
        if self.connectors:
            del self.connectors.children[:]
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return 
        selected = None
        filtered = self.GetFilteredStatesFunctionNames()
        for (itemID, ball,) in ballpark.balls.iteritems():
            if itemID < 0 or itemID == eve.session.shipid:
                continue
            if ballpark is None:
                break
            slimItem = ballpark.GetInvItem(itemID)
            if slimItem and self.WantIt(slimItem, filtered):
                self.AddConnector(ball, 0)
            (selected,) = sm.GetService('state').GetStates(itemID, [state.selected])
            if selected:
                selected = itemID

        if selected:
            self.ShowDirectionTo(selected)
        if self.genericUpdateTimer is None:
            self.genericUpdateTimer = base.AutoTimer(1000, self.GenericUpdate)



    def GenericUpdate(self):
        if not self or not self.connectors:
            self.genericUpdateTimer = None
            return 
        for connector in self.connectors.children:
            try:
                ballID = int(connector.name)
            except:
                sys.exc_clear()
                continue
            if connector.name == 'footprint':
                connector.display = geo2.Vec3Length(connector.translation) < 200000.0




    def WantIt(self, slimItem, filtered = None, isBracket = False):
        if not self.preset[2] and isBracket:
            return 1
        if self.logme:
            self.LogInfo('Tactical::WantIt', slimItem)
        if not slimItem:
            return 0
        if slimItem.itemID == eve.session.shipid:
            return isBracket
        filterGroups = self.GetValidGroups(isBracket=isBracket)
        if slimItem.groupID in filterGroups:
            if sm.GetService('state').CheckIfFilterItem(slimItem) and self.CheckFiltered(slimItem, filtered):
                return 0
            return 1
        return 0



    def GetAvailableGroups(self, getIds = 0):
        if getattr(self, 'logme', None):
            self.LogInfo('Tactical::GetAvailableGroups', getIds)
        if getattr(self, 'groupList', None) is None:
            filterGroups = [const.groupStationServices,
             const.groupSecondarySun,
             const.groupTemporaryCloud,
             const.groupSolarSystem,
             const.groupRing,
             const.groupConstellation,
             const.groupRegion,
             const.groupCloud,
             const.groupComet,
             const.groupCosmicAnomaly,
             const.groupCosmicSignature,
             const.groupGlobalWarpDisruptor,
             const.groupPlanetaryCloud,
             const.groupCommandPins,
             const.groupExtractorPins,
             const.groupPlanetaryLinks,
             const.groupProcessPins,
             const.groupSpaceportPins,
             const.groupStoragePins,
             11,
             const.groupExtractionControlUnitPins,
             const.groupDefenseBunkers,
             const.groupAncientCompressedIce,
             const.groupTerranArtifacts,
             const.groupShippingCrates,
             const.groupProximityDrone,
             const.groupRepairDrone,
             const.groupUnanchoringDrone,
             const.groupWarpScramblingDrone,
             const.groupZombieEntities,
             const.groupForceFieldArray,
             const.groupLogisticsArray,
             const.groupMobilePowerCore,
             const.groupMobileShieldGenerator,
             const.groupMobileStorage,
             const.groupStealthEmitterArray,
             const.groupStructureRepairArray,
             const.groupTargetPaintingBattery]
            groups = []
            validCategories = (const.categoryStation,
             const.categoryShip,
             const.categoryEntity,
             const.categoryCelestial,
             const.categoryAsteroid,
             const.categoryDrone,
             const.categoryDeployable,
             const.categoryStructure,
             const.categoryCharge,
             const.categorySovereigntyStructure,
             const.categoryPlanetaryInteraction,
             const.categoryOrbital)
            for each in cfg.invgroups:
                if each.categoryID == const.categoryCharge and each.groupID not in [const.groupBomb,
                 const.groupBombECM,
                 const.groupBombEnergy,
                 const.groupScannerProbe,
                 const.groupWarpDisruptionProbe,
                 const.groupSurveyProbe]:
                    continue
                if each.categoryID not in validCategories:
                    continue
                if each.groupID in filterGroups:
                    continue
                groups.append((each.groupName.lower(), (each.groupID, each.groupName)))

            self.groupList = uiutil.SortListOfTuples(groups)
            self.groupIDs = set((each[0] for each in self.groupList))
        if getIds:
            return self.groupIDs
        return self.groupList



    def CheckIfGroupIDActive(self, groupID):
        if getattr(self, 'logme', None):
            self.LogInfo('Tactical::CheckIfGroupIDActive', groupID)
        if groupID not in self.GetAvailableGroups(1):
            return -1
        return groupID in self.GetGroups()



    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::tactical')
        try:
            return self.DoBallsAdded_(*args, **kw)

        finally:
            t.PopTimer(timer)




    def DoBallsAdded_(self, lst):
        if not self or getattr(self, 'sr', None) is None:
            return 
        uthread.pool('Tactical::DoBallsAdded', self._DoBallsAdded, lst)



    def _DoBallsAdded(self, lst):
        if not self or self.sr is None:
            return 
        if self.logme:
            self.LogInfo('Tactical::DoBallsAdded', lst)
        self.LogInfo('Tactical - adding balls, num balls:', len(lst))
        updateOverview = 0
        overview = self.GetPanelForUpdate('overview')
        if overview:
            if not len(overview.sr.scroll.GetNodes()):
                updateOverview = 2
            elif getattr(overview, 'solarsystemHasChanged', False):
                self.LogWarn('Forcing full refresh of overview when switching systems')
                updateOverview = 2
            else:
                updateOverview = 1
        self.LogInfo('Tactical - when adding balls, updateOverview:', updateOverview)
        inCapsule = 0
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if mySlim and mySlim.groupID == const.groupCapsule:
            inCapsule = 1
        scrolllist = []
        checkDrones = 0
        filtered = self.GetFilteredStatesFunctionNames()
        (columns, displayColumns,) = self.GetColumns()
        for each in lst:
            if each[1].itemID == eve.session.shipid:
                checkDrones = 1
            if not checkDrones and not inCapsule and each[1].categoryID == const.categoryDrone:
                drone = sm.GetService('michelle').GetDroneState(each[1].itemID)
                if drone and (drone.ownerID == eve.session.charid or drone.controllerID == eve.session.shipid):
                    checkDrones = 1
            if not self.WantIt(each[1], filtered):
                continue
            if self.inited:
                self.AddConnector(each[0])
            if updateOverview == 1:
                data = self.GetEntryData(each[1], each[0])
                overview.UpdateSortData(data, columns)
                scrolllist.append(listentry.Get('TacticalItem', data=data))

        if scrolllist:
            freezeOverview = sm.StartService('ui').GetOverviewFreezeMode()
            if freezeOverview:
                overview.IncrementEntriesAdded(scrolllist)
            else:
                self.LogInfo('Tactical - about to add balls to overview scroll, num:', len(scrolllist))
                overview.sr.scroll.AddEntries(-1, scrolllist)
            overview.sr.scroll.ShowHint()
            uthread.new(overview.UpdateOverview)
        elif updateOverview == 2:
            overview.UpdateAll()
        if checkDrones:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckDrones()
            else:
                self.CheckInitDrones()



    def OnDroneStateChange2(self, droneID, oldState, newState):
        self.InitDrones()
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()



    def OnDroneControlLost(self, droneID):
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()



    def DoBallRemove(self, ball, slimItem, terminal):
        if not self or getattr(self, 'sr', None) is None:
            return 
        if ball is None:
            return 
        if not eve.session.solarsystemid:
            return 
        if self.logme:
            self.LogInfo('Tactical::DoBallRemove', ball.id)
        uthread.pool('tactical::DoBallRemoveThread', self.DoBallRemoveThread, ball, slimItem, terminal)



    def DoBallRemoveThread(self, ball, slimItem, terminal):
        if self.inited:
            self.ClearConnector(ball.id)
            if util.GetAttrs(self, 'direction', 'object', 'dest') and ball == self.direction.object.dest.translationCurve or util.GetAttrs(self, 'direction', 'object', 'source') and ball == self.direction.object.source.translationCurve:
                self.direction.object.dest.translationCurve = None
                self.direction.object.source.translationCurve = None
                self.direction.display = 0
                self.direction2.display = 0
        droneview = self.GetPanel('droneview')
        if droneview and slimItem.categoryID == const.categoryDrone and slimItem.ownerID == eve.session.charid:
            droneview.CheckDrones()
        overview = self.GetPanelForUpdate('overview')
        freezeOverview = sm.StartService('ui').GetOverviewFreezeMode()
        if overview and overview.sr.scroll:
            overviewEntry = self.GetOverviewEntry(ball.id)
            if overviewEntry:
                if freezeOverview:
                    overview.AddEntryToRemoveLater(overviewEntry)
                    if util.GetAttrs(overviewEntry, 'panel', 'SetLabelAlpha'):
                        overviewEntry.panel.SetLabelAlpha(0.25)
                else:
                    self.LogInfo('Tactical -  about to remove ball, id:', ball.id)
                    overview.sr.scroll.RemoveEntries([overviewEntry])
            if not overview.sr.scroll.GetNodes():
                overview.sr.scroll.ShowHint(mls.UI_GENERIC_NOTHINGFOUND)



    def ClearConnector(self, ballID):
        if self.logme:
            self.LogInfo('Tactical::ClearConnector', ballID)
        for connector in self.connectors.children[:]:
            if connector.name.startswith(str(ballID)):
                self.connectors.children.remove(connector)




    def GetOverviewEntry(self, itemID):
        overview = self.GetPanelForUpdate('overview')
        if not overview:
            return None
        if self.logme:
            self.LogInfo('Tactical::GetOverviewEntry', itemID)
        for entry in overview.sr.scroll.GetNodes():
            if entry.itemID == itemID:
                return entry




    def GetEntryData(self, slimItem, ball):
        itemID = slimItem.itemID
        (iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag,) = sm.GetService('bracket').GetBracketProps(slimItem, ball)
        name = hint = uix.GetSlimItemName(slimItem)
        if slimItem.groupID == const.groupStation:
            name = uix.EditStationName(name, usename=0)
        corporationTickerName = ''
        factionName = ''
        if slimItem.corpID:
            corporationTickerName = '[' + cfg.corptickernames.Get(slimItem.corpID).tickerName + ']'
        if slimItem.ownerID and util.IsNPC(slimItem.ownerID) or slimItem.charID and util.IsNPC(slimItem.charID):
            faction = sm.GetService('faction').GetFaction(slimItem.ownerID or slimItem.charID)
            if faction:
                factionName = cfg.eveowners.Get(faction).name
        militiaName = ''
        if slimItem.warFactionID:
            militiaName = cfg.eveowners.Get(slimItem.warFactionID).name
        allianceShortName = ''
        if slimItem.allianceID:
            allianceShortName = '[' + cfg.allianceshortnames.Get(slimItem.allianceID).shortName + ']'
        typeName = ''
        if slimItem.typeID:
            typeName = cfg.invtypes.Get(slimItem.typeID).typeName
        data = uiutil.Bunch()
        data.Set('sort_' + mls.UI_GENERIC_NAME, name.lower())
        data.Set('sort_' + mls.UI_GENERIC_CORPORATION, corporationTickerName.lower())
        data.Set('sort_' + mls.UI_GENERIC_ALLIANCE, allianceShortName.lower())
        data.Set('sort_' + mls.UI_GENERIC_FACTION, factionName.lower())
        data.Set('sort_' + mls.UI_GENERIC_MILITIA, militiaName.lower())
        data.Set('sort_' + mls.UI_GENERIC_VELOCITY, None)
        data.Set('sort_' + mls.UI_GENERIC_RADIALVELOCITY, None)
        data.Set('sort_' + mls.UI_GENERIC_TRANSVERSALVELOCITY, None)
        data.Set('sort_' + mls.UI_GENERIC_ANGULARVELOCITY, None)
        data.Set('sort_' + mls.UI_GENERIC_DISTANCE, ball.surfaceDist)
        data.Set('sort_' + mls.UI_GENERIC_SIZE, ball.radius * 2)
        data.Set('sort_' + mls.UI_GENERIC_ICON, (slimItem.categoryID, slimItem.groupID))
        data.Set('sort_' + mls.UI_GENERIC_TAG, sm.GetService('fleet').GetTargetTag(itemID) or '')
        data.Set('sort_' + mls.UI_GENERIC_TYPE, typeName)
        data.NAME = name
        data.TYPE = typeName
        data.CORPORATION = corporationTickerName
        data.ALLIANCE = allianceShortName
        data.FACTION = factionName
        data.MILITIA = militiaName
        data.SIZE = util.FmtDist(data.Get('sort_' + mls.UI_GENERIC_SIZE))
        data.TAG = data.Get('sort_' + mls.UI_GENERIC_TAG)
        data.ICON = ''
        data.Set('fmt_' + mls.UI_GENERIC_VELOCITY, None)
        data.Set('fmt_' + mls.UI_GENERIC_RADIALVELOCITY, None)
        data.Set('fmt_' + mls.UI_GENERIC_TRANSVERSALVELOCITY, None)
        data.Set('fmt_' + mls.UI_GENERIC_ANGULARVELOCITY, None)
        data.Set('fmt_' + mls.UI_GENERIC_DISTANCE, None)
        data.name = name
        data.label = ''
        data.icon = ''
        data.tag = data.Get('sort_' + mls.UI_GENERIC_TAG)
        data.hint = hint
        data.itemID = slimItem.itemID
        data.typeID = slimItem.typeID
        data.iconNo = iconNo
        data.updateItem = sm.GetService('state').CheckIfUpdateItem(slimItem)
        data.tabs = None
        data.ball = _weakref.ref(ball)
        data.slimItem = _weakref.ref(slimItem)
        data.DecoSortValue = lambda val: self.DecoDataSortValue(data, val)
        return data



    def DecoDataSortValue(self, data, val):
        if settings.user.overview.Get('overviewBroadcastsToTop', False) and sm.GetService('fleet').CurrentFleetBroadcastOnItem(data.itemID):
            return (1, val)
        else:
            return (2, val)



    def GetIntersection(self, dist, planeDist):
        if self.logme:
            self.LogInfo('Tactical::GetIntersection', dist, planeDist)
        return sqrt(abs(dist ** 2 - planeDist ** 2))



    def AddConnector(self, ball, update = 1):
        if self.logme:
            self.LogInfo('Tactical::AddConnector', ball, update)
        if self.connectors is None:
            return 
        connector = trinity.Load('res:/UI/Inflight/tactical/footprint.red')
        connector.name = str(ball.id)
        connector.display = True
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        verticalLine = None
        footprintPlane = None
        for child in connector.children:
            if child.name == 'verticalLine':
                verticalLine = child
            if child.name == 'footprint':
                footprintPlane = child

        if verticalLine is not None:
            verticalLine.ClearLines()
            verticalLine.AddLine((0.0, 0.0, 0.0), (0.2, 0.2, 0.2, 1.0), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2, 1.0))
            verticalLine.SubmitChanges()
            verticalLine.translationCurve = ball
            set = trinity.TriCurveSet()
            vs = trinity.TriVectorSequencer()
            vc = trinity.TriVectorCurve()
            vc.value.SetXYZ(0.0, -1.0, 0.0)
            vs.functions.append(ball)
            vs.functions.append(vc)
            bind = trinity.TriValueBinding()
            bind.destinationObject = verticalLine
            bind.destinationAttribute = 'scaling'
            bind.sourceObject = vs
            bind.sourceAttribute = 'value'
            set.curves.append(vs)
            set.curves.append(vc)
            set.bindings.append(bind)
            set.name = str(ball.id) + '_vline'
            set.Play()
            scene2.curveSets.append(set)
            self.usedCurveSets.append(set)
        if footprintPlane is not None:
            set = trinity.TriCurveSet()
            vs = trinity.TriVectorSequencer()
            vc = trinity.TriVectorCurve()
            vc.value.SetXYZ(1.0, 0.0, 1.0)
            vs.functions.append(ball)
            vs.functions.append(vc)
            bind = trinity.TriValueBinding()
            bind.destinationObject = footprintPlane
            bind.destinationAttribute = 'translation'
            bind.sourceObject = vs
            bind.sourceAttribute = 'value'
            set.curves.append(vs)
            set.curves.append(vc)
            set.bindings.append(bind)
            set.name = str(ball.id) + '_fprint'
            set.Play()
            scene2.curveSets.append(set)
            self.usedCurveSets.append(set)
            connector.display = geo2.Vec3Length(footprintPlane.translation) < 200000.0
        self.connectors.children.append(connector)
        if ball.id == sm.GetService('state').GetExclState(state.selected):
            self.ShowDirectionTo(ball.id)



    def IsEwarFiltered(self, ewarType):
        self.PrimePreset()
        ewarFilters = self.preset[1].get('smartFilters', [])
        return ewarType in ewarFilters



    def SmartFilter(self, itemID, overview = True):
        if overview:
            (activePreset, preset,) = (self.preset[0], self.preset[1])
        else:
            (activePreset, preset,) = (self.preset[2], self.preset[3])
        if not self.smartFilterOn == True:
            return False
        ewarFilters = preset.get('smartFilters', [])



    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarStart', sourceBallID, jammingType)
            return 
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        if targetBallID == session.shipid:
            if not self.jammers.has_key(sourceBallID):
                self.jammers[sourceBallID] = {}
            self.jammers[sourceBallID][jammingType] = sm.GetService('state').GetEwarFlag(jammingType)



    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarStart', sourceBallID, jammingType)
            return 
        if not hasattr(self, 'jammers'):
            return 
        if self.jammers.has_key(sourceBallID) and self.jammers[sourceBallID].has_key(jammingType):
            del self.jammers[sourceBallID][jammingType]



    def RemoveDelayedOverviewEntries(self):
        overview = self.GetPanelForUpdate('overview')
        if overview:
            overview.RemoveDelayedEntries()



    def GetOverviewEntriesToRemove(self):
        return self.overviewEntriesToRemove



    def ClearOverviewEntriesToRemove(self):
        self.overviewEntriesToRemove.clear()



    def ImportOverviewSettings(self):
        wnd = sm.GetService('window').GetWindow('ImportOverviewWindow', create=1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def ExportOverviewSettings(self):
        wnd = sm.GetService('window').GetWindow('ExportOverviewWindow', create=1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def OnEveGetsFocus(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if not ctrl:
            self.RemoveDelayedOverviewEntries()




