import xtriui
import base
import uix
import uiutil
import blue
import uthread
import util
import _weakref
import listentry
import state
import form
import dbg
import uicls
import uiconst
import localization
import localizationUtil

class DroneEntry(listentry.BaseTacticalEntry):
    __guid__ = 'listentry.DroneEntry'
    __notifyevents__ = ['OnStateChange', 'OnDroneStateChange2', 'OnDroneActivityChange']

    def Startup(self, *args):
        listentry.BaseTacticalEntry.Startup(self, *args)
        self.activityID = None
        self.activity = None
        text_gaugeContainer = uicls.Container(name='text_gaugeContainer', parent=self, idx=0, pos=(0, 0, 0, 0))
        self.sr.gaugesContainer = uicls.Container(name='gaugesContainer', parent=text_gaugeContainer, width=85, align=uiconst.TORIGHT, state=uiconst.UI_HIDDEN)
        tClip = uicls.Container(name='textClipper', parent=text_gaugeContainer, state=uiconst.UI_PICKCHILDREN, clipChildren=1)
        uiutil.Transplant(self.sr.label, tClip)



    def Load(self, node):
        listentry.BaseTacticalEntry.Load(self, node)
        if self.sr.node.droneState in ('inlocalspace', 'indistantspace'):
            self.UpdateState()
        if node.droneState == 'inbay':
            self.sr.gaugesContainer.state = uiconst.UI_HIDDEN
        else:
            self.sr.gaugesContainer.state = uiconst.UI_PICKCHILDREN



    def UpdateState(self, droneState = None):
        michelle = sm.GetService('michelle')
        droneRow = michelle.GetDroneState(self.sr.node.itemID)
        droneActivity = michelle.GetDroneActivity(self.sr.node.itemID)
        if droneActivity:
            (self.activity, self.activityID,) = droneActivity
        if droneState is None and droneRow is not None:
            droneState = droneRow.activityState
        droneStates = {const.entityIdle: 'UI/Inflight/Drone/Idle',
         const.entityCombat: 'UI/Inflight/Drone/Fighting',
         const.entityMining: 'UI/Inflight/Drone/Mining',
         const.entityApproaching: 'UI/Inflight/Drone/Approaching',
         const.entityDeparting: 'UI/Inflight/Drone/ReturningToShip',
         const.entityDeparting2: 'UI/Inflight/Drone/ReturningToShip',
         const.entityOperating: 'UI/Inflight/Drone/Operating',
         const.entityPursuit: 'UI/Inflight/Drone/Following',
         const.entityFleeing: 'UI/Inflight/Drone/Fleeing',
         const.entityEngage: 'UI/Inflight/Drone/Repairing',
         None: 'UI/Inflight/Drone/NoState'}
        droneStateLabel = droneStates.get(droneState, 'UI/Inflight/Drone/Incapacitated')
        stateText = localization.GetByLabel(droneStateLabel)
        label = localization.GetByLabel('UI/Inflight/Drone/Label', droneType=self.sr.node.label, state=stateText)
        target = ''
        if droneState in [const.entityCombat, const.entityEngage, const.entityMining]:
            targetID = droneRow.targetID
            targetTypeName = None
            pilotName = None
            if targetID:
                targetSlim = michelle.GetItem(targetID)
                if targetSlim:
                    if targetSlim.groupID == const.categoryShip:
                        pilotID = michelle.GetCharIDFromShipID(targetSlim.itemID)
                        if pilotID:
                            pilotName = cfg.eveowners.Get(pilotID).name
                    targetTypeName = uix.GetSlimItemName(targetSlim)
            if pilotName:
                target = pilotName
            elif targetTypeName:
                target = targetTypeName
            target = localization.GetByLabel('UI/Generic/Unknown')
        tooltipExtra = ''
        if self.sr.node.ownerID != eve.session.charid:
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/OwnershipText', owner=self.sr.node.ownerID)
        elif self.sr.node.controllerID != eve.session.shipid:
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/ControllerText', owner=self.sr.node.controllerOwnerID)
        elif self.activityID and self.activity:
            activity = ''
            if self.activity == 'guard':
                activity = localization.GetByLabel('UI/Inflight/Drone/Guarding')
            elif self.activity == 'assist':
                activity = localization.GetByLabel('UI/Inflight/Drone/Assisting')
            tooltipExtra = localization.GetByLabel('UI/Inflight/Drone/Activity', activity=activity, idInfo=cfg.eveowners.Get(self.activityID).name)
        tooltip = localization.GetByLabel('UI/Inflight/Drone/Tooltip', droneType=self.sr.node.label, state=stateText, target=target, tooltipExtra=tooltipExtra)
        self.sr.label.text = label
        self.hint = tooltip



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight('Xg', singleLine=1) + 4
        return node.height



    def OnDroneStateChange2(self, droneID, oldActivityState, newActivityState):
        if not self or getattr(self, 'sr', None) is None:
            return 
        if self.sr.node and self.sr.node.droneState in ('inlocalspace', 'indistantspace') and droneID == self.sr.node.itemID:
            droneRow = sm.GetService('michelle').GetDroneState(self.sr.node.itemID)
            if droneRow:
                self.sr.node.controllerID = droneRow.controllerID
                self.sr.node.controllerOwnerID = droneRow.controllerOwnerID
                self.UpdateState(newActivityState)



    def OnDroneActivityChange(self, droneID, activityID, activity):
        if not self or getattr(self, 'sr', None) is None:
            return 
        if self.sr.node and self.sr.node.droneState in ('inlocalspace', 'indistantspace') and droneID == self.sr.node.itemID:
            self.activity = activity
            self.activityID = activityID
            self.UpdateState()



    def OnClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if not uicore.uilib.Key(uiconst.VK_CONTROL):
                if not uicore.uilib.Key(uiconst.VK_SHIFT):
                    sm.GetService('state').SetState(self.sr.node.itemID, state.selected, 1)
            else:
                sm.GetService('target').TryLockTarget(self.sr.node.itemID)



    def GetSelected(self):
        ids = []
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in sel:
            if node.Get('typeID', None) is None:
                continue
            if cfg.invtypes.Get(node.typeID).groupID == cfg.invtypes.Get(self.sr.node.typeID).groupID:
                ids.append(node.itemID)

        return ids



    def GetSelectedItems(self):
        items = []
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in sel:
            items.append(node.invItem)

        return items



    def GetMenu(self):
        m = []
        if self.sr.node.customMenu:
            m += self.sr.node.customMenu(self.sr.node)
        if self.sr.node.droneState != 'inbay':
            args = []
            droneData = []
            selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
            for node in selected:
                if node.Get('typeID', None) is None:
                    continue
                args.append((self.sr.node.itemID,
                 None,
                 None,
                 0,
                 self.sr.node.typeID,
                 None,
                 None))
                droneData.append((node.itemID, cfg.invtypes.Get(node.typeID).groupID, eve.session.charid))

            if droneData:
                m += self.DroneMenu(droneData)
            m += sm.GetService('menu').CelestialMenu(args, ignoreDroneMenu=1)
        else:
            selected = self.GetSelectedItems()
            args = []
            for rec in selected:
                args.append((rec, 0, 0))

            filterFunc = [localization.GetByLabel('UI/Inventory/ItemActions/BuyThisType'),
             localization.GetByLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             localization.GetByLabel('UI/Inventory/ItemActions/FindInContracts')]
            m += sm.GetService('menu').InvItemMenu(args, filterFunc=filterFunc)
        return m



    def DroneMenu(self, droneData):
        menuSvc = sm.GetService('menu')
        specialDroneData = []
        for (droneID, groupID, ownerID,) in droneData:
            if cfg.invtypes.Get(self.sr.node.typeID).groupID == groupID:
                specialDroneData.append([droneID, groupID, ownerID])

        menu = menuSvc.GetGroupSpecificDroneMenu(specialDroneData)
        menu += menuSvc.GetCommonDroneMenu(droneData)
        return menu



    def SelectAll(self):
        self.sr.node.scroll.SelectAll()
        sel = self.GetSelected()
        if len(sel) > 1:
            sm.ScatterEvent('OnMultiSelect', sel)



    def InitGauges(self):
        if getattr(self, 'gaugesInited', False):
            self.sr.gaugeParent.state = uiconst.UI_DISABLED
            return 
        parent = self.sr.gaugesContainer
        uicls.Line(parent=parent, align=uiconst.TOLEFT)
        (barw, barh,) = (24, 6)
        borderw = 2
        barsw = (barw + borderw) * 3 + borderw
        par = uicls.Container(name='gauges', parent=parent, align=uiconst.TORIGHT, width=barsw + 2, height=0, left=0, top=0, idx=10)
        self.sr.gauges = []
        l = 2
        for each in ('SHIELD', 'ARMOR', 'STRUCT'):
            g = uicls.Container(parent=par, name='gauge_%s' % each.lower(), align=uiconst.CENTERLEFT, width=barw, height=barh, left=l)
            uicls.Frame(parent=g)
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            self.sr.gauges.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)
            l += barw + borderw

        self.sr.gaugeParent = par
        self.gaugesInited = True




class DroneView(form.ActionPanel):
    __guid__ = 'form.DroneView'
    __notifyevents__ = ['OnItemLaunch',
     'OnDroneControlLost',
     'ProcessSessionChange',
     'OnAttribute',
     'OnAttributes',
     'OnItemChange']
    default_windowID = 'droneview'
    default_pinned = True
    default_left = 0
    default_top = 0

    def ApplyAttributes(self, attributes):
        self.fafDefVal = cfg.dgmattribs.Get(const.attributeFighterAttackAndFollow).defaultValue
        self.droneAggressionDefVal = cfg.dgmattribs.Get(const.attributeDroneIsAggressive).defaultValue
        self.droneFFDefVal = cfg.dgmattribs.Get(const.attributeDroneFocusFire).defaultValue
        form.ActionPanel.ApplyAttributes(self, attributes)



    def OnItemLaunch(self, ids):
        reload = False
        for (oldID, newIDs,) in ids.iteritems():
            group = self.GetDroneGroup(oldID)
            if group is not None:
                for newID in newIDs:
                    if newID != oldID:
                        group['droneIDs'].add(newID)
                        reload = True


        if reload:
            self.UpdateGroupSettings()
            self.CheckDrones(True)



    def ProcessSessionChange(self, *etc):
        self.CheckDrones(True)


    ProcessSessionChange = util.Uthreaded(ProcessSessionChange)

    def OnDroneControlLost(self, droneID):
        self.CheckDrones(True)



    def OnAttributes(self, l):
        for (attributeName, item, newValue,) in l:
            self.OnAttribute(attributeName, item, newValue)




    def OnAttribute(self, attributeName, item, newValue):
        if not self or self.destroyed:
            return 
        if item.itemID == session.charid and attributeName == 'maxActiveDrones':
            t = self.sr.lastUpdate
            if t is None:
                self.CheckDrones()
            else:
                self.UpdateHeader(t[0], t[1] + t[2])



    def OnItemChange(self, item, change):
        if item.locationID == session.shipid:
            if item.flagID == const.flagDroneBay or change.get(const.ixFlag, None) == const.flagDroneBay:
                ignoreClose = session.solarsystemid == change.get(const.ixLocationID, None)
                self.CheckDrones(ignoreClose=ignoreClose)
        elif change.get(const.ixLocationID, None) == session.shipid and change.get(const.ixFlag, None) == const.flagDroneBay:
            self.CheckDrones()



    def PostStartup(self):
        if not self or self.destroyed:
            return 
        self.SetTopparentHeight(0)
        self.SetMinSize((240, 80))
        self.SetHeaderIcon()
        hicon = self.sr.headerIcon
        hicon.GetMenu = self.GetDroneMenu
        hicon.expandOnLeft = 1
        self.sr.droneMenu = hicon
        self.sr.scroll = uicls.Scroll(name='dronescroll', align=uiconst.TOALL, parent=self.sr.main)
        self.sr.scroll.multiSelect = 1
        self.sr.scroll.OnChar = self.OnDronesScrollChar
        self.sr.inSpace = None
        self.sr.lastUpdate = None
        self.settingsName = 'droneBlah2'
        self.reloading = 0
        self.pending = None
        uicore.registry.GetLockedGroup('dronegroups', 'inbay', localization.GetByLabel('UI/Inflight/Drone/DronesInBay'))
        uicore.registry.GetLockedGroup('dronegroups', 'inlocalspace', localization.GetByLabel('UI/Inflight/Drone/DronesInLocalSpace'))
        uicore.registry.GetLockedGroup('dronegroups', 'indistantspace', localization.GetByLabel('UI/Inflight/Drone/DronesInDistantSpace'))
        self.groups = self.SettifyGroups(settings.user.ui.Get(self.settingsName, {}))
        droneSettingChanges = {}
        droneSettingChanges[const.attributeDroneIsAggressive] = settings.char.ui.Get('droneAggression', self.droneAggressionDefVal)
        droneSettingChanges[const.attributeFighterAttackAndFollow] = settings.char.ui.Get('fighterAttackAndFollow', self.fafDefVal)
        droneSettingChanges[const.attributeDroneFocusFire] = settings.char.ui.Get('droneFocusFire', self.droneFFDefVal)
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettingChanges)
        if self and not self.destroyed:
            uthread.new(self.CheckDrones)



    def OnDronesScrollChar(self, *args):
        return False



    def GetDroneMenu(self):
        return [None, (localization.GetByLabel('UI/Inflight/Drone/Settings'), self.DroneSettings)]



    def DroneSettings(self):
        form.DroneSettings.Open()



    def GroupXfier(fn):

        def XfyGroup(group):
            ret = group.copy()
            ret['droneIDs'] = fn(group['droneIDs'])
            return ret


        return lambda self, groups: dict([ (name, XfyGroup(group)) for (name, group,) in groups.iteritems() ])


    ListifyGroups = GroupXfier(list)
    SettifyGroups = GroupXfier(set)
    del GroupXfier

    def GetSelected(self, fromNode):
        nodes = []
        sel = self.sr.scroll.GetSelectedNodes(fromNode)
        for node in sel:
            if node.Get('typeID', None) is None:
                continue
            if cfg.invtypes.Get(node.typeID).groupID == cfg.invtypes.Get(fromNode.typeID).groupID:
                if node.droneState == fromNode.droneState:
                    nodes.append(node)

        return nodes



    def UpdateHeader(self, inBay, inSpace):
        self.SetCaption(localization.GetByLabel('UI/Inflight/Drone/PanelHeader', panelName=self.panelname, inSpace=len(inSpace), maxTotal=sm.GetService('godma').GetItem(session.charid).maxActiveDrones or 0))



    def UpdateAll(self):
        if self.sr.main.state != uiconst.UI_PICKCHILDREN:
            self.sr.actionsTimer = None
            return 
        self.CheckDrones()



    def GetSubGroups(self, what):
        return []



    def CheckDrones(self, force = False, ignoreClose = False, *args):
        if session.stationid:
            return 
        if not self.pending:
            self.pending = ('updating',)
        elif 'updating' in self.pending:
            self.pending = ('pending', force, ignoreClose)
            return 
        if 'pending' in self.pending:
            return 
        if self.destroyed:
            return 
        inBay = self.GetDronesInBay()
        inBayIDs = [ drone.itemID for drone in inBay ]
        inBayIDs.sort()
        inLocalSpace = [ drone for drone in self.GetDronesInLocalSpace() if drone.droneID not in inBayIDs ]
        inLocalSpaceIDs = [ drone.droneID for drone in inLocalSpace ]
        inLocalSpaceIDs.sort()
        inDistantSpace = [ drone for drone in self.GetDronesInDistantSpace() if drone.droneID not in inBayIDs ]
        inDistantSpaceIDs = [ drone.droneID for drone in inDistantSpace ]
        inDistantSpaceIDs.sort()
        t = (inBayIDs, inLocalSpaceIDs, inDistantSpaceIDs)
        if self.sr.lastUpdate != t or force or inDistantSpace:
            self.sr.lastUpdate = t
            groupInfo = uicore.registry.GetListGroup(('dronegroups', 'inbay'))
            scrolllist = self.GetGroupListEntry(groupInfo, 'inbay', inBayIDs)
            groupInfo = uicore.registry.GetListGroup(('dronegroups', 'inlocalspace'))
            scrolllist += self.GetGroupListEntry(groupInfo, 'inlocalspace', inLocalSpaceIDs)
            if inDistantSpaceIDs:
                groupInfo = uicore.registry.GetListGroup(('dronegroups', 'indistantspace'))
                scrolllist += self.GetGroupListEntry(groupInfo, 'indistantspace', inDistantSpaceIDs)
            self.sr.scroll.Load(contentList=scrolllist)
        self.UpdateHeader(inBayIDs, inLocalSpaceIDs + inDistantSpaceIDs)
        self.CheckHint()
        blue.pyos.synchro.SleepWallclock(500)
        if not self or self.destroyed:
            return 
        if 'pending' in self.pending:
            (p, force, ignoreClose,) = self.pending
            self.pending = None
            self.CheckDrones(force, ignoreClose)
            return 
        self.pending = None
        if not ignoreClose and not self.destroyed:
            self.CheckClose()



    def CheckClose(self):
        if not (self.GetDronesInBay() or sm.GetService('michelle').GetDrones()) and hasattr(self, 'Close'):
            self.Close()



    def GetMainFolderMenu(self, node):
        m = [None]
        delMenu = [ (groupName, self.DeleteGroup, (groupName,)) for (groupName, groupInfo,) in self.groups.iteritems() ]
        if delMenu:
            m += [(localization.GetByLabel('UI/Commands/DeleteGroup'), delMenu), None]
        if node.droneState == 'inlocalspace':
            data = [ [drone.droneID, cfg.invtypes.Get(drone.typeID).groupID, drone.ownerID] for drone in self.GetDronesInLocalSpace() ]
            if data:
                m += sm.GetService('menu').GetDroneMenu(data)
        elif node.droneState == 'indistantspace':
            data = [ [drone.droneID, cfg.invtypes.Get(drone.typeID).groupID, drone.ownerID] for drone in self.GetDronesInDistantSpace() ]
            if data:
                m += sm.GetService('menu').GetDroneMenu(data)
        else:
            inBay = [ (drone, 0, None) for drone in self.GetDronesInBay() ]
            if inBay:
                filterFunc = [localization.GetByLabel('UI/Inventory/ItemActions/BuyThisType'),
                 localization.GetByLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
                 localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
                 localization.GetByLabel('UI/Inventory/ItemActions/FindInContracts')]
                m += sm.GetService('menu').InvItemMenu(inBay, filterFunc=filterFunc)
        return m



    def DeleteGroup(self, groupName):
        self.EmptyGroup(groupName)
        if groupName in self.groups:
            del self.groups[groupName]
        self.UpdateGroupSettings()
        self.UpdateAll()



    def GetSubFolderMenu(self, node):
        m = [None]
        itemIDs = self.GetSubGroup(node.groupName)['droneIDs']
        if itemIDs:
            if node.droneState == 'inlocalspace':
                data = [ (drone.droneID, cfg.invtypes.Get(drone.typeID).groupID, drone.ownerID) for drone in self.GetDronesInLocalSpace() if drone.droneID in itemIDs ]
                droneMenu = sm.GetService('menu').GetDroneMenu(data)
                m += droneMenu
            elif node.droneState == 'indistantspace':
                data = [ (drone.droneID, cfg.invtypes.Get(drone.typeID).groupID, drone.ownerID) for drone in self.GetDronesInDistantSpace() if drone.droneID in itemIDs ]
                droneMenu = sm.GetService('menu').GetDroneMenu(data)
                m += droneMenu
            else:
                inBay = [ (drone, 0, None) for drone in self.GetDronesInBay() if drone.itemID in itemIDs ]
                if len(inBay):
                    filterFunc = [localization.GetByLabel('UI/Inventory/ItemActions/BuyThisType'),
                     localization.GetByLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
                     localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
                     localization.GetByLabel('UI/Inventory/ItemActions/FindInContracts')]
                    m += sm.GetService('menu').InvItemMenu(inBay, filterFunc=filterFunc)
        return m



    def GroupMenu(self, droneNode):
        selected = self.GetSelected(droneNode)
        m = []
        move = [(localization.GetByLabel('UI/Commands/NewGroup'), self.CreateSubGroup, (droneNode.itemID, cfg.invtypes.Get(droneNode.typeID).groupID, selected))]
        inGroup = []
        for node in selected:
            group = self.GetDroneGroup(node.itemID)
            if group:
                inGroup.append(node)

        if inGroup:
            move += [(localization.GetByLabel('UI/Commands/OutOfThisGroup'), self.NoGroup, (inGroup,))]
        groupNames = self.groups.keys()[:]
        groupNames.sort()
        move += [ (groupName, self.MoveToGroup, (groupName,
          droneNode.itemID,
          cfg.invtypes.Get(droneNode.typeID).groupID,
          selected)) for groupName in groupNames ]
        m += [(localization.GetByLabel('UI/Commands/MoveDrone'), move)]
        return m



    def GetEmptyGroups(self):
        empty = []
        for (groupName, groupInfo,) in self.groups.iteritems():
            if not groupInfo['droneIDs']:
                empty.append(groupName)

        return empty



    def DeleteEmptyGroups(self, *args):
        for groupName in self.GetEmptyGroups():
            del self.groups[groupName]




    def GetDroneGroup(self, droneID, getall = 0):
        retall = []
        for (groupName, group,) in self.groups.iteritems():
            if droneID in group['droneIDs']:
                if getall:
                    retall.append(group)
                else:
                    return group

        if getall:
            return retall



    def NoGroup(self, nodes):
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)


        self.CheckDrones(1)
        self.UpdateGroupSettings()



    def EmptyGroup(self, groupName):
        droneGroup = self.GetSubGroup(groupName)
        for droneID in droneGroup.get('droneIDs', set()).copy():
            for group in self.GetDroneGroup(droneID, getall=1):
                group['droneIDs'].remove(droneID)


        self.CheckDrones(1)



    def MoveToGroup(self, groupName, droneID, droneGroupID, nodes):
        group = self.GetSubGroup(groupName)
        if group['droneIDs'] and group['droneGroupID'] != droneGroupID:
            eve.Message('CannotMixDrones')
            return 
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)


        group = self.GetSubGroup(groupName)
        if not group['droneIDs']:
            group['droneGroupID'] = droneGroupID
        if group:
            for node in nodes:
                group['droneIDs'].add(node.itemID)

        self.CheckDrones(1)
        self.UpdateGroupSettings()



    def GetSubGroup(self, groupName):
        if groupName in self.groups:
            return self.groups[groupName]



    def CreateSubGroup(self, droneID, droneGroupID, nodes = None):
        ret = uix.NamePopup(localization.GetByLabel('UI/Generic/TypeGroupName'), localization.GetByLabel('UI/Generic/TypeNameForGroup'))
        if not ret:
            return 
        droneIDs = set()
        for node in nodes:
            for group in self.GetDroneGroup(node.itemID, getall=1):
                group['droneIDs'].remove(node.itemID)

            droneIDs.add(node.itemID)

        origname = groupname = ret['name']
        i = 2
        while groupname in self.groups:
            groupname = '%s_%i' % (origname, i)
            i += 1

        group = {}
        group['label'] = groupname
        group['droneIDs'] = droneIDs
        group['id'] = (groupname, str(blue.os.GetWallclockTime()))
        group['droneGroupID'] = droneGroupID
        self.groups[groupname] = group
        self.CheckDrones(1)
        self.UpdateGroupSettings()



    def OnMainGroupClick(self, group, *args):
        if group.sr.node.droneState == 'inlocalspace':
            itemIDs = [ drone.droneID for drone in self.GetDronesInLocalSpace() ]
        elif group.sr.node.droneState == 'indistantspace':
            itemIDs = [ drone.droneID for drone in self.GetDronesInDistantSpace() ]
        else:
            itemIDs = [ drone.itemID for drone in self.GetDronesInBay() ]
        if itemIDs:
            sm.ScatterEvent('OnMultiSelect', itemIDs)



    def OnSubGroupClick(self, group, *args):
        itemIDs = self.GetSubGroup(group.sr.node.groupName)['droneIDs']
        if group.sr.node.droneState == 'inlocalspace':
            itemIDs = [ drone.droneID for drone in self.GetDronesInLocalSpace() if drone.droneID in itemIDs ]
        if group.sr.node.droneState == 'indistantspace':
            itemIDs = [ drone.droneID for drone in self.GetDronesInDistantSpace() if drone.droneID in itemIDs ]
        else:
            itemIDs = [ drone.itemID for drone in self.GetDronesInBay() if drone.itemID in itemIDs ]
        if len(itemIDs) > 1:
            sm.ScatterEvent('OnMultiSelect', itemIDs)



    def GetDronesInBay(self, *args):
        if eve.session.shipid:
            return sm.GetService('invCache').GetInventoryFromId(eve.session.shipid).ListDroneBay()
        return []



    def GetDronesInLocalSpace(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return []
        drones = sm.GetService('michelle').GetDrones()
        return [ drones[droneID] for droneID in drones if droneID in ballpark.slimItems if drones[droneID].ownerID == eve.session.charid or drones[droneID].controllerID == eve.session.shipid ]



    def GetDronesInDistantSpace(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return []
        drones = sm.GetService('michelle').GetDrones()
        return [ drones[droneID] for droneID in drones if droneID not in ballpark.slimItems if drones[droneID].ownerID == eve.session.charid or drones[droneID].controllerID == eve.session.shipid ]



    def GetSpaceDrone(self, droneID):
        return sm.GetService('michelle').GetDroneState(droneID)



    def GetGroupListEntry(self, group, state, items):
        if not group or 'id' not in group:
            return []
        t = 0
        if state == 'inbay':
            dronebay = {}
            for drone in self.GetDronesInBay():
                dronebay[drone.itemID] = drone

            for droneID in items:
                t += dronebay[droneID].stacksize

        else:
            t = len(items)
        states = {'INBAY': localization.GetByLabel('UI/Inflight/Drone/DronesInBay'),
         'INLOCALSPACE': localization.GetByLabel('UI/Inflight/Drone/DronesInLocalSpace'),
         'INDISTANTSPACE': localization.GetByLabel('UI/Inflight/Drone/DronesInDistantSpace')}
        data = {'GetSubContent': self.GetGroupContent,
         'MenuFunction': self.GetMainFolderMenu,
         'label': localization.GetByLabel('UI/Inflight/Drone/DroneGroupWithCount', groupLabel=states[state.upper()], count=t),
         'id': group['id'],
         'groupItems': items,
         'iconMargin': 18,
         'state': 'locked',
         'sublevel': 0,
         'droneState': state,
         'BlockOpenWindow': 1,
         'OnClick': self.OnMainGroupClick,
         'showlen': 0,
         'groupName': group['label'],
         'name': 'droneOverview%s' % group['label'].replace(' ', '').capitalize()}
        return [listentry.Get('Group', data)]



    def GetSubGroupListEntry(self, group, state, items):
        t = 0
        if state == 'inbay':
            dronebay = {}
            for drone in self.GetDronesInBay():
                dronebay[drone.itemID] = drone

            for droneID in items:
                t += dronebay[droneID].stacksize

        else:
            t = len(items)
        data = {'GetSubContent': self.GetGroupContent,
         'MenuFunction': self.GetSubFolderMenu,
         'label': localization.GetByLabel('UI/Inflight/Drone/DroneGroupWithCount', groupLabel=group['label'], count=t),
         'id': group['id'],
         'droneGroupID': group['droneGroupID'],
         'groupItems': None,
         'iconMargin': 18,
         'state': 'locked',
         'sublevel': 1,
         'droneState': state,
         'BlockOpenWindow': 1,
         'OnClick': self.OnSubGroupClick,
         'showlen': 0,
         'groupName': group['label']}
        return listentry.Get('Group', data)



    def GetGroupContent(self, nodedata, newitems = 0):
        scrollList = []
        if nodedata.sublevel == 0:
            if nodedata.droneState == 'inbay':
                dronebay = {}
                for drone in self.GetDronesInBay():
                    dronebay[drone.itemID] = drone

            subGroups = {}
            for droneID in nodedata.groupItems:
                group = self.GetDroneGroup(droneID)
                if group:
                    subGroups.setdefault(group['label'], []).append(droneID)
                    continue
                if nodedata.droneState == 'inbay':
                    if dronebay.has_key(droneID):
                        scrollList.append(self.GetBayDroneEntry(dronebay[droneID], nodedata.sublevel, nodedata.droneState))
                else:
                    scrollList.append(self.GetSpaceDroneEntry(self.GetSpaceDrone(droneID), nodedata.sublevel, nodedata.droneState))

            for (groupName, droneIDs,) in subGroups.iteritems():
                group = self.GetSubGroup(groupName)
                if group:
                    scrollList.append(self.GetSubGroupListEntry(group, nodedata.droneState, droneIDs))

        elif nodedata.sublevel == 1:
            subGroupInfo = self.GetSubGroup(nodedata.groupName)
            if nodedata.droneState == 'inbay':
                drones = self.GetDronesInBay()
                for drone in drones:
                    if drone.itemID in subGroupInfo['droneIDs']:
                        scrollList.append(self.GetBayDroneEntry(drone, 1, nodedata.droneState))

            elif nodedata.droneState == 'inlocalspace':
                drones = self.GetDronesInLocalSpace()
                for drone in drones:
                    if drone.droneID in subGroupInfo['droneIDs']:
                        scrollList.append(self.GetSpaceDroneEntry(drone, 1, nodedata.droneState))

            else:
                drones = self.GetDronesInDistantSpace()
                for drone in drones:
                    if drone.droneID in subGroupInfo['droneIDs']:
                        scrollList.append(self.GetSpaceDroneEntry(drone, 1, nodedata.droneState))

        return localizationUtil.Sort(scrollList, key=lambda x: x.label)



    def GetBayDroneEntry(self, drone, level, droneState):
        data = util.KeyVal()
        data.itemID = drone.itemID
        data.typeID = drone.typeID
        data.invItem = drone
        data.displayName = cfg.invtypes.Get(drone.typeID).name
        if drone.stacksize > 1:
            data.label = localization.GetByLabel('UI/Inflight/Drone/DroneBayEntryWithStacksize', drone=drone.typeID, stacksize=drone.stacksize)
        else:
            data.label = cfg.invtypes.Get(drone.typeID).name
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        return listentry.Get('DroneEntry', data=data)



    def GetSpaceDroneEntry(self, drone, level, droneState):
        data = util.KeyVal()
        data.itemID = drone.droneID
        data.typeID = drone.typeID
        data.ownerID = drone.ownerID
        data.controllerID = drone.controllerID
        data.controllerOwnerID = drone.controllerOwnerID
        data.displayName = data.label = cfg.invtypes.Get(drone.typeID).name
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        return listentry.Get('DroneEntry', data=data)



    def CheckHint(self):
        if not self.sr.scroll.GetNodes():
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Inflight/Drone/NoDrones'))
        else:
            self.sr.scroll.ShowHint()



    def UpdateGroupSettings(self):
        settings.user.ui.Set(self.settingsName, self.ListifyGroups(self.groups))
        sm.GetService('settings').SaveSettings()




