import blue
import uthread
import util
import xtriui
import uix
import form
import listentry
import lg
import uiconst
import uicls
import localization

class CorpMembersViewTaskManagement(uicls.Container):
    __guid__ = 'form.CorpMembersViewTaskManagement'
    __nonpersistvars__ = []

    def init(self):
        self.memberIDs = []
        self.wndTabs = None
        self.wndAction = None
        self.wndTargets = None
        self.targetIDs = []
        self.noneTargetIDs = []
        self.scrollTargets = None
        self.scrollNoneTargets = None
        self.roles = sm.GetService('corp').GetRoles()
        self.titles = sm.GetService('corp').GetTitles()
        self.propertyControls = {}
        self.offices = sm.GetService('corp').GetMyCorporationsOffices()
        self.locationalRoles = sm.GetService('corp').GetLocationalRoles()
        self.offices.Fetch(0, len(self.offices))
        self.currentlyEditing = None
        self.verbList = [[localization.GetByLabel('UI/Commands/AddItem'), const.CTV_ADD],
         [localization.GetByLabel('UI/Commands/Remove'), const.CTV_REMOVE],
         [localization.GetByLabel('UI/Common/CommandSet'), const.CTV_SET],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Give'), const.CTV_GIVE]]
        self.propertyList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Cash'), const.CTPG_CASH],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Shares'), const.CTPG_SHARES],
         [localization.GetByLabel('UI/Corporations/Common/Title'), 'titleMask']]
        self.bitmaskablesList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'],
         [localization.GetByLabel('UI/Corporations/Common/Title'), 'titleMask']]
        self.setList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID']]
        self.giveList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Cash'), const.CTPG_CASH], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Shares'), const.CTPG_SHARES]]
        self.optionsByVerb = {const.CTV_ADD: self.bitmaskablesList,
         const.CTV_REMOVE: self.bitmaskablesList,
         const.CTV_SET: self.setList,
         const.CTV_GIVE: self.giveList}
        self.controlsByProperty = {'roles': 'role_picker',
         'rolesAtHQ': 'role_picker_locational',
         'rolesAtBase': 'role_picker_locational',
         'rolesAtOther': 'role_picker_locational',
         'grantableRoles': 'role_picker',
         'grantableRolesAtHQ': 'role_picker_locational',
         'grantableRolesAtBase': 'role_picker_locational',
         'grantableRolesAtOther': 'role_picker_locational',
         'baseID': 'location_picker',
         const.CTPG_CASH: 'isk_amount_picker',
         const.CTPG_SHARES: 'share_amount_picker',
         'titleMask': 'title_picker'}



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def CreateWindow(self):
        self.LogInfo('CreateWindow')
        self.wndTabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
        self.wndTabs.Startup([[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Actions'),
          self,
          self,
          'actions'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Targets'),
          self,
          self,
          'targets']], 'taskManagement')
        self.Load('actions')



    def CreateActionWindow(self):
        self.wndAction = uicls.Container(name='wndAction', parent=self, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        wndOutputArea = uicls.Container(name='output', parent=self.wndAction, align=uiconst.TOTOP, height=48)
        captionparent = uicls.Container(name='captionparent', parent=wndOutputArea, align=uiconst.TOTOP, height=16)
        label = uicls.Container(name='text', parent=wndOutputArea, align=uiconst.TOTOP, height=16)
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/HintActionTargetRelation'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        wndQueryContainer = uicls.Container(name='queryinput', parent=self.wndAction, height=150, align=uiconst.TOTOP)
        self.wndQueryContainer = wndQueryContainer
        self.scrollQuery = uicls.Scroll(parent=wndQueryContainer)
        wndSearchBuilderToolbar = uicls.Container(name='searchtoolbar', parent=self.wndAction, align=uiconst.TOTOP, height=18, top=8)
        self.wndSearchBuilderToolbar = wndSearchBuilderToolbar
        combo = uicls.Combo(label='', parent=wndSearchBuilderToolbar, options=self.verbList, name='verb', callback=self.OnComboChange, width=66, pos=(const.defaultPadding,
         0,
         0,
         0), align=uiconst.TOLEFT)
        self.comboVerb = combo
        combo = uicls.Combo(label='', parent=wndSearchBuilderToolbar, options=self.bitmaskablesList, name='property', callback=self.OnComboChange, width=146, pos=(const.defaultPadding,
         0,
         0,
         0), align=uiconst.TOLEFT)
        self.comboProperty = combo
        wndInputControlArea = uicls.Container(name='inputArea', parent=wndSearchBuilderToolbar, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.wndInputFieldArea = wndInputControlArea
        self.ShowAppropriateInputField()
        wndAddButtonContainer = uicls.Container(name='sidepar', parent=wndSearchBuilderToolbar, align=uiconst.TORIGHT, width=104)
        self.addEditButton = uicls.Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Commands/AddItem'), func=self.AddSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        self.saveEditButton = uicls.Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Save'), pos=(self.addEditButton.width + 6,
         0,
         0,
         0), func=self.SaveEditedSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        self.cancelEditButton = uicls.Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Commands/Cancel'), pos=(self.saveEditButton.left + self.saveEditButton.width + 6,
         0,
         0,
         0), func=self.CancelEditedSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        wndAddButtonContainer.width = self.cancelEditButton.left + self.cancelEditButton.width
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN
        wndButtonBar = uicls.Container(name='execute', parent=self.wndAction, align=uiconst.TOTOP, height=28)
        button = uicls.Button(parent=wndButtonBar, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/CommitActionsOnTargets'), align=uiconst.CENTER, func=self.ExecuteActions, btn_default=0)
        self.UpdateActionsTabLabel()



    def ExecuteActions(self, *args):
        self.LogInfo('ExecuteActions args:', args)
        actions = []
        for entry in self.scrollQuery.GetNodes():
            verb = entry.verb
            property = entry.property
            value = entry.value
            actions.append([verb, property, value])

        sm.GetService('corp').ExecuteActions(self.targetIDs, actions)



    def MakeLabel(self, verb, property, value):
        label = None
        labelVerb = None
        labelProperty = None
        currentControlType = self.controlsByProperty[property]
        for (displayText, fieldName,) in self.verbList:
            if verb == fieldName:
                labelVerb = displayText
                break

        for (displayText, fieldName,) in self.propertyList:
            if property == fieldName:
                labelProperty = displayText
                break

        if currentControlType in ('role_picker', 'role_picker_locational'):
            for role in self.roles:
                if role.roleID == value:
                    label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/TextRecord', verb=labelVerb, property=labelProperty, value=role.shortDescription)
                    break

        elif currentControlType == 'title_picker':
            for title in self.titles:
                if title.titleID == value:
                    label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/TextRecord', verb=labelVerb, property=labelProperty, value=title.titleName)
                    break

        elif currentControlType == 'location_picker':
            if value is None:
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/LocationRecordWithNone', verb=labelVerb, property=labelProperty)
            else:
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/LocationRecord', verb=labelVerb, property=labelProperty, station=value)
        elif currentControlType == 'isk_amount_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/CashRecord', verb=labelVerb, property=labelProperty, cash=util.FmtISK(value))
        elif currentControlType == 'share_amount_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/SharesRecord', verb=labelVerb, property=labelProperty, shares=value)
        elif currentControlType == 'date_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/DateRecord', verb=labelVerb, property=labelProperty, dateValue=value)
        return label



    def AddSearchTerm(self, *args):
        try:
            self.LogInfo('AddSearchTerm')
            sm.GetService('loading').Cycle('Loading')
            verb = self.comboVerb.GetValue()
            property = self.comboProperty.GetValue()
            value = None
            if self.propertyControls.has_key('current'):
                currentControlType = self.propertyControls['current']
                if currentControlType is not None:
                    currentControl = self.propertyControls[currentControlType]
                    value = currentControl.GetValue()
            self.LogInfo('verb: ', verb)
            self.LogInfo('property: ', property)
            self.LogInfo('value: ', value)
            label = self.MakeLabel(verb, property, value)
            params = {'label': label,
             'caption1': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Edit'),
             'caption2': localization.GetByLabel('UI/Commands/Remove'),
             'OnClick1': self.OnClickEdit,
             'OnClick2': self.OnClickRemove,
             'args1': label,
             'args2': label,
             'verb': verb,
             'property': property,
             'value': value}
            control = listentry.Get('TwoButtons', params)
            self.scrollQuery.AddEntries(-1, [control])
            self.UpdateActionsTabLabel()

        finally:
            sm.GetService('loading').StopCycle()




    def SaveEditedSearchTerm(self, *args):
        if self.currentlyEditing is None:
            return 
        verb = self.comboVerb.GetValue()
        property = self.comboProperty.GetValue()
        value = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            if currentControlType is not None:
                currentControl = self.propertyControls[currentControlType]
                value = currentControl.GetValue()
        entry = self.currentlyEditing
        label = self.MakeLabel(verb, property, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.verb = verb
        entry.property = property
        entry.value = value
        self.currentlyEditing = None
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def CancelEditedSearchTerm(self, *args):
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def OnClickEdit(self, args):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.currentlyEditing = entry
        verb = entry.verb
        property = entry.property
        value = entry.value
        self.comboVerb.SelectItemByValue(verb)
        self.comboProperty.LoadOptions(self.optionsByVerb[verb])
        self.comboProperty.SelectItemByValue(property)
        self.ShowAppropriateInputField()
        currentControlType = self.propertyControls['current']
        if currentControlType is not None:
            currentControl = self.propertyControls[currentControlType]
            if getattr(currentControl, 'SelectItemByValue', None):
                currentControl.SelectItemByValue(value)
            elif getattr(currentControl, 'SetValue', None):
                currentControl.SetValue(value)
        self.addEditButton.state = uiconst.UI_HIDDEN
        self.saveEditButton.state = uiconst.UI_NORMAL
        self.cancelEditButton.state = uiconst.UI_NORMAL



    def OnClickRemove(self, args):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.scrollQuery.RemoveEntries([entry])
        self.UpdateActionsTabLabel()
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def GetEntryByLabel(self, label):
        for entry in self.scrollQuery.GetNodes():
            if entry.label == label:
                return entry




    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'verb':
            self.comboProperty.LoadOptions(self.optionsByVerb[self.comboVerb.GetValue()])
            self.ShowAppropriateInputField()
        elif entry.name == 'property':
            self.ShowAppropriateInputField()



    def ShowAppropriateInputField(self):
        currentProperty = self.comboProperty.GetValue()
        requestedControlType = self.controlsByProperty[currentProperty]
        currentControlType = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            if currentControlType == requestedControlType:
                return 
        requestedControl = None
        if self.propertyControls.has_key(requestedControlType):
            requestedControl = self.propertyControls[requestedControlType]
        elif requestedControlType == 'role_picker':
            optionsList = []
            for role in self.roles:
                if role.roleID in self.locationalRoles:
                    continue
                optionsList.append([role.shortDescription, role.roleID])

            requestedControl = uicls.Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'title_picker':
            optionsList = []
            for title in self.titles:
                optionsList.append([title.titleName, title.titleID])

            requestedControl = uicls.Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'role_picker_locational':
            optionsList = []
            for role in self.roles:
                if role.roleID not in self.locationalRoles:
                    continue
                optionsList.append([role.shortDescription, role.roleID])

            requestedControl = uicls.Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'location_picker':
            bases = [('-', None)]
            rows = self.offices
            if rows and len(rows):
                for row in rows:
                    bases.append((cfg.evelocations.Get(row.stationID).locationName, row.stationID))

            requestedControl = uicls.Combo(label='', parent=self.wndInputFieldArea, options=bases, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'isk_amount_picker':
            requestedControl = uicls.SinglelineEdit(name='edit', parent=self.wndInputFieldArea, ints=(1, None), width=146, left=8, top=8, align=uiconst.TOLEFT)
        elif requestedControlType == 'share_amount_picker':
            requestedControl = uicls.SinglelineEdit(name='edit', parent=self.wndInputFieldArea, ints=(1, None), width=146, left=8, top=8, align=uiconst.TOLEFT)
        elif requestedControlType == None:
            requestedControl = None
        else:
            raise RuntimeError('UnexpectedControlTypeRequested')
        if currentControlType is not None and self.propertyControls.has_key(currentControlType):
            currentControl = self.propertyControls[currentControlType]
            currentControl.state = uiconst.UI_HIDDEN
        if requestedControl is not None:
            requestedControl.state = uiconst.UI_NORMAL
        self.propertyControls[requestedControlType] = requestedControl
        self.propertyControls['current'] = requestedControlType



    def CreateTargetsWindow(self):
        self.wndTargets = uicls.Container(name='wndTargets', parent=self, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        wndOutputArea = uicls.Container(name='output', parent=self.wndTargets, align=uiconst.TOTOP, height=44)
        captionparent = uicls.Container(name='captionparent', parent=wndOutputArea, align=uiconst.TOTOP, height=16)
        label = uicls.Container(name='text', parent=wndOutputArea, align=uiconst.TOTOP, width=150, height=16)
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SelectMembersYouWantToTarget'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        label = uicls.Container(name='text', parent=wndOutputArea, align=uiconst.TOTOP, width=150, height=16)
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TargetTheseMembers'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        targetsScrollContainer = uicls.Container(name='targets', parent=self.wndTargets, height=150, align=uiconst.TOTOP)
        self.scrollTargets = uicls.Scroll(parent=targetsScrollContainer)
        uicls.Container(name='push', parent=self.wndTargets, align=uiconst.TOTOP, height=2)
        wndOutputArea = uicls.Container(name='output', parent=self.wndTargets, align=uiconst.TOTOP, height=18)
        label = uicls.Container(name='text', parent=wndOutputArea, align=uiconst.TOLEFT, width=150, height=16)
        uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/DoNotTargetTheseMembers'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        noneTargetsScrollContainer = uicls.Container(name='noneTargets', parent=self.wndTargets, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.scrollNoneTargets = uicls.Scroll(parent=noneTargetsScrollContainer)
        self.UpdateTargetsTabLabel()



    def Load(self, args):
        self.LogInfo('Load args:', args)
        if args == 'actions':
            if self.wndAction is None:
                self.CreateActionWindow()
            self.wndAction.state = uiconst.UI_NORMAL
            if self.wndTargets is not None:
                self.wndTargets.state = uiconst.UI_HIDDEN
            self.UpdateActionsTabLabel()
        elif args == 'targets':
            if self.wndTargets is None:
                self.CreateTargetsWindow()
                self.LoadTargets()
            self.wndTargets.state = uiconst.UI_NORMAL
            if self.wndAction is not None:
                self.wndAction.state = uiconst.UI_HIDDEN
            self.UpdateTargetsTabLabel()



    def PopulateView(self, memberIDs = None):
        if memberIDs is not None:
            self.memberIDs = memberIDs
            self.targetIDs = memberIDs
        if self.wndTargets is not None:
            self.LoadTargets()
        self.left = -const.defaultPadding
        self.width = -const.defaultPadding
        self.UpdateActionsTabLabel()
        self.UpdateTargetsTabLabel()



    def LoadTargets(self):
        self.targetIDs = []
        self.noneTargetIDs = []
        scrolllist = []
        for memberID in self.memberIDs:
            self.targetIDs.append(memberID)
            scrolllist.append(listentry.Get('Button', {'label': cfg.eveowners.Get(memberID).ownerName,
             'caption': localization.GetByLabel('UI/Commands/Remove'),
             'OnClick': self.OnRemove,
             'args': (memberID,)}))

        self.scrollTargets.Load(None, scrolllist)
        self.scrollNoneTargets.Load(None, [])
        self.UpdateTargetsTabLabel()



    def UpdateActionsTabLabel(self):
        if self.wndTabs is not None:
            actionsTabName = '%s_tab' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Actions')
            actionsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ActionsTabLabel', numberOfActions=len(self.scrollQuery.GetNodes()))
            self.wndTabs.sr.Get(actionsTabName, None).SetLabel(actionsLabel)



    def UpdateTargetsTabLabel(self):
        if self.wndTabs is not None:
            targetsTabName = '%s_tab' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Targets')
            targetsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TargetsTabLabel', targetCount=len(self.targetIDs), nonTargetCount=len(self.noneTargetIDs))
            self.wndTabs.sr.Get(targetsTabName, None).SetLabel(targetsLabel)



    def OnRemove(self, memberID, button):
        self.LogInfo('OnRemove memberID:', memberID)
        control = listentry.Get('Button', {'label': cfg.eveowners.Get(memberID).ownerName,
         'caption': localization.GetByLabel('UI/Commands/AddItem'),
         'OnClick': self.OnAdd,
         'args': (memberID,)})
        self.scrollNoneTargets.AddEntries(-1, [control])
        self.targetIDs.remove(memberID)
        self.noneTargetIDs.append(memberID)
        entry = self.GetEntryByArgs(self.scrollTargets, (memberID,))
        self.scrollTargets.RemoveEntries([entry])
        self.UpdateTargetsTabLabel()



    def OnAdd(self, memberID, button):
        self.LogInfo('OnAdd memberID:', memberID)
        control = listentry.Get('Button', {'label': cfg.eveowners.Get(memberID).ownerName,
         'caption': localization.GetByLabel('UI/Commands/AddItem'),
         'OnClick': self.OnRemove,
         'args': (memberID,)})
        self.scrollTargets.AddEntries(-1, [control])
        self.targetIDs.append(memberID)
        self.noneTargetIDs.remove(memberID)
        entry = self.GetEntryByArgs(self.scrollNoneTargets, (memberID,))
        self.scrollNoneTargets.RemoveEntries([entry])
        self.UpdateTargetsTabLabel()



    def GetEntryByArgs(self, scroll, args):
        for entry in scroll.GetNodes():
            if entry.args == args:
                return entry





