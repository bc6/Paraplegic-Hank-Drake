import blue
import uthread
import util
import uix
import form
import listentry
import lg
import uiconst
import uicls
import localization
LOGICAL_OPERATOR_OR = 1
LOGICAL_OPERATOR_AND = 2
OPERATOR_EQUAL = 1
OPERATOR_GREATER = 2
OPERATOR_GREATER_OR_EQUAL = 3
OPERATOR_LESS = 4
OPERATOR_LESS_OR_EQUAL = 5
OPERATOR_NOT_EQUAL = 6
OPERATOR_HAS_BIT = 7
OPERATOR_NOT_HAS_BIT = 8
OPERATOR_STR_CONTAINS = 9
OPERATOR_STR_LIKE = 10
OPERATOR_STR_STARTS_WITH = 11
OPERATOR_STR_ENDS_WITH = 12
OPERATOR_STR_IS = 13

class TwoButtons(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.TwoButtons'
    __params__ = ['label',
     'caption1',
     'caption2',
     'OnClick1',
     'OnClick2']
    ENTRYHEIGHT = 22

    def Startup(self, args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.button1 = uicls.Button(parent=self, label='', align=uiconst.CENTERRIGHT, left=2)
        self.sr.button2 = uicls.Button(parent=self, label='', align=uiconst.CENTERRIGHT)
        self.sr.label = uicls.EveLabelMedium(name='label', text='', parent=self, align=uiconst.CENTERLEFT, left=8, state=uiconst.UI_DISABLED)



    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        self.sr.button1.OnClick = lambda *args: self.sr.node.OnClick1(*(self.sr.node.Get('args1', (None,)), (self.sr.button1,)))
        self.sr.button1.SetLabel(self.sr.node.caption1)
        self.sr.button2.OnClick = lambda *args: self.sr.node.OnClick2(*(self.sr.node.Get('args2', (None,)), (self.sr.button2,)))
        self.sr.button2.SetLabel(self.sr.node.caption2)
        self.sr.button2.left = self.sr.button1.left + self.sr.button1.width + 2




class CorpQueryMembersForm():
    __guid__ = 'form.CorpQueryMembersForm'

    def __init__(self):
        self.memberIDs = []
        self.roles = sm.GetService('corp').GetRoles()
        self.titles = sm.GetService('corp').GetTitles()
        self.propertyControls = {}
        self.offices = sm.GetService('corp').GetMyCorporationsOffices()
        self.locationalRoles = sm.GetService('corp').GetLocationalRoles()
        self.offices.Fetch(0, len(self.offices))
        self.currentlyEditing = None
        self.lpfnQueryCompleted = None
        self.logicalOperators = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalOR'): LOGICAL_OPERATOR_OR,
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalAND'): LOGICAL_OPERATOR_AND}
        self.propertyList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/StartDate'), 'startDateTime'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Name'), 'characterID'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Title'), 'titleMask']]
        self.optionsRoles = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RolesInclude'), OPERATOR_HAS_BIT], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RolesNotInclude'), OPERATOR_NOT_HAS_BIT]]
        self.optionsLocation = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicEqualSign'), OPERATOR_EQUAL], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicNotEqualSign'), OPERATOR_NOT_EQUAL]]
        self.optionsDateTime = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicEqualSign'), OPERATOR_EQUAL],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicGreaterThanSign'), OPERATOR_GREATER],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicGreaterThanOrEqualSign'), OPERATOR_GREATER_OR_EQUAL],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicLessThanSign'), OPERATOR_LESS],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicLessThanOrEqualSign'), OPERATOR_LESS_OR_EQUAL],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicNotEqualSign'), OPERATOR_NOT_EQUAL]]
        self.optionsStr = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ContainsRelation'), OPERATOR_STR_CONTAINS],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LikeRelation'), OPERATOR_STR_LIKE],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/StartsWithRelation'), OPERATOR_STR_STARTS_WITH],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/EndsWithRelation'), OPERATOR_STR_ENDS_WITH],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/IsRelation'), OPERATOR_STR_IS]]
        self.optionsByProperty = {'roles': self.optionsRoles,
         'rolesAtHQ': self.optionsRoles,
         'rolesAtBase': self.optionsRoles,
         'rolesAtOther': self.optionsRoles,
         'grantableRoles': self.optionsRoles,
         'grantableRolesAtHQ': self.optionsRoles,
         'grantableRolesAtBase': self.optionsRoles,
         'grantableRolesAtOther': self.optionsRoles,
         'baseID': self.optionsLocation,
         'startDateTime': self.optionsDateTime,
         'characterID': self.optionsStr,
         'titleMask': self.optionsRoles}
        self.controlsByProperty = {'roles': 'role_picker',
         'rolesAtHQ': 'role_picker_locational',
         'rolesAtBase': 'role_picker_locational',
         'rolesAtOther': 'role_picker_locational',
         'grantableRoles': 'role_picker',
         'grantableRolesAtHQ': 'role_picker_locational',
         'grantableRolesAtBase': 'role_picker_locational',
         'grantableRolesAtOther': 'role_picker_locational',
         'baseID': 'location_picker',
         'startDateTime': 'date_picker',
         'characterID': 'edit_control',
         'titleMask': 'title_picker'}



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def Load(self, parentWindow, lpfnQueryCompleted = None):
        self.lpfnQueryCompleted = lpfnQueryCompleted
        parentWindow.left = parentWindow.width = parentWindow.height = const.defaultPadding
        wndForm = uicls.Container(name='form', parent=parentWindow, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.wndForm = wndForm
        self.scrollQuery = uicls.Scroll(name='queryinput', parent=wndForm, height=100, align=uiconst.TOTOP)
        uicls.Container(name='push', parent=wndForm, align=uiconst.TOTOP, height=const.defaultPadding)
        self.wndSearchBuilderToolbar = uicls.Container(name='searchtoolbar', parent=wndForm, align=uiconst.TOTOP, height=18)
        optionsList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalOR'), LOGICAL_OPERATOR_OR], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalAND'), LOGICAL_OPERATOR_AND]]
        combo = uicls.Combo(label='', parent=self.wndSearchBuilderToolbar, options=optionsList, name='join_operator', callback=self.OnComboChange, width=50, pos=(1, 0, 0, 0), align=uiconst.TOLEFT)
        self.comboJoinOperator = combo
        self.comboJoinOperator.state = uiconst.UI_HIDDEN
        combo = uicls.Combo(label='', parent=self.wndSearchBuilderToolbar, options=self.propertyList, name='property', callback=self.OnComboChange, width=128, pos=(const.defaultPadding,
         0,
         0,
         0), align=uiconst.TOLEFT)
        self.comboProperty = combo
        combo = uicls.Combo(label='', parent=self.wndSearchBuilderToolbar, options=self.optionsByProperty[self.comboProperty.GetValue()], name='operator', callback=self.OnComboChange, width=80, pos=(const.defaultPadding,
         0,
         0,
         0), align=uiconst.TOLEFT)
        combo.OnChange = self.OnComboChange
        self.comboOperator = combo
        wndInputControlArea = uicls.Container(name='inputArea', parent=self.wndSearchBuilderToolbar, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.wndInputFieldArea = wndInputControlArea
        self.ShowAppropriateInputField()
        wndOptionsBar = uicls.Container(name='options', parent=wndForm, align=uiconst.TOTOP, height=40)
        self.addEditButton = uicls.Button(parent=wndOptionsBar, label=localization.GetByLabel('UI/Commands/AddItem'), func=self.AddSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        self.saveEditButton = uicls.Button(parent=wndOptionsBar, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Save'), pos=(self.addEditButton.width + 6,
         0,
         0,
         0), func=self.SaveEditedSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        self.cancelEditButton = uicls.Button(parent=wndOptionsBar, label=localization.GetByLabel('UI/Commands/Cancel'), pos=(self.saveEditButton.left + self.saveEditButton.width + 6,
         0,
         0,
         0), func=self.CancelEditedSearchTerm, btn_default=0, align=uiconst.TOPRIGHT)
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN
        uicls.Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchTitles'), parent=wndOptionsBar, configName='FMBQsearchTitles', retval=None, checked=settings.user.ui.Get('FMBQsearchTitles', 0), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(0, 4, 400, 0))
        uicls.Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/IncludeImpliedRoles'), parent=wndOptionsBar, configName='FMBQincludeImplied', retval=None, checked=settings.user.ui.Get('FMBQincludeImplied', 0), groupname=None, callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(0, 20, 400, 0))
        wndButtonBar = uicls.Container(name='execute', parent=wndForm, align=uiconst.TOTOP, height=16)
        button = uicls.Button(parent=wndButtonBar, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ExecuteQuery'), func=self.ExecuteQuery, btn_default=0, align=uiconst.CENTER)
        wndButtonBar.height = button.height
        return wndForm



    def CheckBoxChange(self, checkbox):
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if checkbox.data.has_key('value'):
                if checkbox.data['value'] is None:
                    settings.user.ui.Set(config, checkbox.checked)
                else:
                    settings.user.ui.Set(config, checkbox.data['value'])



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
        elif requestedControlType == 'date_picker':
            nowSecs = blue.os.GetWallclockTime()
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(nowSecs)
            now = [year, month, day]
            requestedControl = uix.GetDatePicker(self.wndInputFieldArea, setval=now, left=6, top=-2, idx=None)
        elif requestedControlType == 'edit_control':
            control = uicls.SinglelineEdit(name=requestedControlType, parent=self.wndInputFieldArea, width=146, left=const.defaultPadding, align=uiconst.TOLEFT, maxLength=37)
            requestedControl = control
        else:
            raise RuntimeError('UnexpectedControlTypeRequested')
        if currentControlType is not None and self.propertyControls.has_key(currentControlType):
            currentControl = self.propertyControls[currentControlType]
            currentControl.state = uiconst.UI_HIDDEN
        if requestedControl is None:
            raise RuntimeError('FailedToCreateControlTypeRequested')
        requestedControl.state = uiconst.UI_NORMAL
        self.propertyControls[requestedControlType] = requestedControl
        self.propertyControls['current'] = requestedControlType



    def ExecuteQuery(self, *args):
        query = []
        for entry in self.scrollQuery.GetNodes():
            joinOperator = entry.joinOperator
            property = entry.property
            operator = entry.operator
            value = entry.value
            if joinOperator is None:
                query.append([property, operator, value])
            else:
                query.append([joinOperator,
                 property,
                 operator,
                 value])

        searchTitles = settings.user.ui.Get('FMBQsearchTitles', 0)
        includeImplied = settings.user.ui.Get('FMBQincludeImplied', 0)
        self.memberIDs = sm.GetService('corp').GetMemberIDsByQuery(query, includeImplied, searchTitles)
        if self.lpfnQueryCompleted is not None:
            self.lpfnQueryCompleted()



    def MakeLabel(self, joinOperator, property, operator, value):
        localizedJoinOperator = None
        localizedProperty = None
        localizedOperator = None
        localizedValue = None
        if joinOperator:
            for (k, v,) in self.logicalOperators.iteritems():
                if v == joinOperator:
                    localizedJoinOperator = k
                    break

        currentControlType = self.controlsByProperty[property]
        for (display_text, field_name,) in self.propertyList:
            if property == field_name:
                localizedProperty = display_text
                break

        if operator:
            for (k, v,) in self.optionsByProperty[property]:
                if v == operator:
                    localizedOperator = k
                    break

        if value:
            if currentControlType in ('role_picker', 'role_picker_locational'):
                for role in self.roles:
                    if role.roleID == value:
                        localizedValue = role.shortDescription
                        break

            elif currentControlType == 'title_picker':
                for title in self.titles:
                    if title.titleID == value:
                        localizedValue = title.titleName
                        break

            elif currentControlType == 'location_picker':
                localizedValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchQueryLocation', location=value)
            elif currentControlType == 'date_picker':
                localizedValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchQueryDate', date=value)
            elif currentControlType == 'edit_control':
                localizedValue = value
            else:
                raise RuntimeError('UnexpectedControlTypeRequested')
        if joinOperator and operator and value:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/FullSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, operator=localizedOperator, value=localizedValue)
        elif joinOperator and operator:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinOperatorSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, operator=localizedOperator)
        elif joinOperator and value:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinValueSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, value=localizedValue)
        elif operator and value:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/OperatorValueSearchLabel', property=localizedProperty, operator=localizedOperator, value=localizedValue)
        elif operator:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/OperatorSearchLabel', property=localizedProperty, operator=localizedOperator)
        elif value:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ValueSearchLabel', property=localizedProperty, value=localizedValue)
        elif joinOperator:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinSearchLabel', joinOperator=localizedJoinOperator)
        else:
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/DefaultSearchLabel', property=localizedProperty)
        return label



    def AddSearchTerm(self, *args):
        try:
            self.LogInfo('AddSearchTerm')
            sm.GetService('loading').Cycle('Loading')
            joinOperator = None
            if self.comboJoinOperator.state == uiconst.UI_NORMAL:
                joinOperator = self.comboJoinOperator.GetValue()
            property = self.comboProperty.GetValue()
            operator = self.comboOperator.GetValue()
            value = None
            if self.propertyControls.has_key('current'):
                currentControlType = self.propertyControls['current']
                currentControl = self.propertyControls[currentControlType]
                value = currentControl.GetValue()
            self.LogInfo('joinOperator: ', joinOperator)
            self.LogInfo('property: ', property)
            self.LogInfo('operator: ', operator)
            self.LogInfo('value: ', value)
            if not value:
                raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Shared/PleaseTypeSomething')})
            label = self.MakeLabel(joinOperator, property, operator, value)
            params = {'label': label,
             'caption1': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Edit'),
             'caption2': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Remove'),
             'OnClick1': self.OnClickEdit,
             'OnClick2': self.OnClickRemove,
             'args1': label,
             'args2': label,
             'joinOperator': joinOperator,
             'property': property,
             'operator': operator,
             'value': value}
            control = listentry.Get('TwoButtons', params)
            self.scrollQuery.AddEntries(-1, [control])
            self.comboJoinOperator.state = uiconst.UI_NORMAL

        finally:
            sm.GetService('loading').StopCycle()




    def SaveEditedSearchTerm(self, *args):
        if self.currentlyEditing is None:
            return 
        joinOperator = None
        if self.comboJoinOperator.state == uiconst.UI_NORMAL:
            joinOperator = self.comboJoinOperator.GetValue()
        property = self.comboProperty.GetValue()
        operator = self.comboOperator.GetValue()
        value = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            currentControl = self.propertyControls[currentControlType]
            value = currentControl.GetValue()
        entry = self.currentlyEditing
        label = self.MakeLabel(joinOperator, property, operator, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.joinOperator = joinOperator
        entry.property = property
        entry.operator = operator
        entry.value = value
        self.currentlyEditing = None
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def CancelEditedSearchTerm(self, *args):
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def OnClickEdit(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.currentlyEditing = entry
        joinOperator = entry.joinOperator
        property = entry.property
        operator = entry.operator
        value = entry.value
        if joinOperator is None:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
            self.comboJoinOperator.SelectItemByValue(joinOperator)
        self.comboProperty.SelectItemByValue(property)
        self.comboOperator.LoadOptions(self.optionsByProperty[property])
        self.comboOperator.SelectItemByValue(operator)
        self.ShowAppropriateInputField()
        currentControlType = self.propertyControls['current']
        currentControl = self.propertyControls[currentControlType]
        if getattr(currentControl, 'SelectItemByValue', None) is not None:
            currentControl.SelectItemByValue(value)
        elif getattr(currentControl, 'SetValue', None) is not None:
            currentControl.SetValue(value)
        self.addEditButton.state = uiconst.UI_HIDDEN
        self.saveEditButton.state = uiconst.UI_NORMAL
        self.cancelEditButton.state = uiconst.UI_NORMAL



    def OnClickRemove(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.scrollQuery.RemoveEntries([entry])
        self.RemoveJoinOperatorFromFirstEntry()
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN



    def RemoveJoinOperatorFromFirstEntry(self):
        self.LogInfo('RemoveJoinOperatorFromFirstEntry')
        if not len(self.scrollQuery.GetNodes()):
            self.LogInfo('no entries')
            return 
        entry = self.scrollQuery.GetNodes()[0]
        joinOperator = entry.joinOperator
        property = entry.property
        operator = entry.operator
        value = entry.value
        self.LogInfo('joinOperator: ', joinOperator, 'property: ', property, 'operator: ', operator, 'value: ', value)
        if joinOperator is None:
            self.LogInfo('no join operator')
            return 
        joinOperator = None
        label = self.MakeLabel(joinOperator, property, operator, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.joinOperator = joinOperator



    def GetEntryByLabel(self, label):
        for entry in self.scrollQuery.GetNodes():
            if entry.label == label:
                return entry




    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'property':
            self.comboOperator.LoadOptions(self.optionsByProperty[self.comboProperty.GetValue()])
            self.ShowAppropriateInputField()




class CorpFindMembersInRole(uicls.Container):
    __guid__ = 'form.CorpFindMembersInRole'
    __nonpersistvars__ = []

    def init(self):
        self.sr.wndQuery = form.CorpQueryMembersForm()
        self.sr.wndQueryForm = None
        self.sr.outputScrollContainer = None
        self.sr.showHideButton = None
        self.sr.wndButtonContainer = None
        self.sr.outputTypeCombo = None
        self.sr.outputWindow = None



    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)



    def Load(self, args):
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.wndButtonContainer = uicls.Container(name='results', parent=self, align=uiconst.TOTOP, height=16)
            showHide = uicls.Container(name='filters', parent=self.sr.wndButtonContainer, height=48, align=uiconst.TOTOP)
            uicls.Line(parent=showHide, align=uiconst.TOTOP, top=15, color=(0.0, 0.0, 0.0, 0.25))
            uicls.Line(parent=showHide, align=uiconst.TOTOP)
            self.sr.showHide = showHide
            uicls.EveHeaderSmall(text=localization.GetByLabel('UI/Corporations/BaseCorporationUI/Query'), parent=showHide, left=8, top=3, state=uiconst.UI_NORMAL)
            a = uicls.EveHeaderSmall(text='', parent=showHide, left=18, top=3, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
            a.OnClick = self.ShowHideQuery
            a.GetMenu = None
            self.sr.ml = a
            expander = uicls.Sprite(parent=showHide, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Shared/expanderDown.png', align=uiconst.TOPRIGHT)
            expander.OnClick = self.ShowHideQuery
            self.sr.showHideExp = expander
            self.sr.wndButtonContainer.state = uiconst.UI_HIDDEN
            wndQueryForm = self.sr.wndQuery.Load(self, self.PopulateView)
            wndQueryForm.align = uiconst.TOTOP
            wndQueryForm.height = 180
            self.sr.wndQueryForm = wndQueryForm
            wndForm = uicls.Container(name='form', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
            self.sr.wndForm = wndForm
            wndOutputTypeArea = uicls.Container(name='output_type', parent=wndForm, align=uiconst.TOTOP, height=24)
            uicls.Container(name='push', parent=wndOutputTypeArea, align=uiconst.TOTOP, height=6)
            label = uicls.Container(name='text', parent=wndOutputTypeArea, align=uiconst.TOLEFT, width=150)
            uicls.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ShowResultsUsingLabel'), parent=label, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            optlist = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleList'), form.CorpMembersViewSimple], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleManagementList'), form.CorpMembersViewRoleManagement], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskManagementList'), form.CorpMembersViewTaskManagement]]
            countcombo = uicls.Combo(label='', parent=wndOutputTypeArea, options=optlist, name='resultViewType', callback=self.OnComboChange, width=146, align=uiconst.TOLEFT)
            self.sr.outputTypeCombo = countcombo
            self.sr.outputWindowContainer = None
            viewClass = self.sr.outputTypeCombo.GetValue()
            self.SwitchToView(viewClass)
        sm.GetService('corpui').LoadTop('07_11', localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/FindMemberInRole'))



    def _OnClose(self, *args):
        if self.sr.outputWindow and hasattr(self.sr.outputWindow, '_OnClose'):
            self.sr.outputWindow._OnClose(args)



    def OnTabDeselect(self):
        if self.sr.outputWindow and hasattr(self.sr.outputWindow, 'OnTabDeselect'):
            self.sr.outputWindow.OnTabDeselect()



    def ShowHideQuery(self, *args):
        advanced = [True, False][(self.sr.wndQueryForm.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN))]
        if advanced:
            self.sr.showHideExp.texturePath = 'res:/UI/Texture/Shared/expanderUp.png'
        else:
            self.sr.showHideExp.texturePath = 'res:/UI/Texture/Shared/expanderDown.png'
        self.sr.ml.text = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ShowQuery'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/HideQuery')][advanced]
        self.sr.wndQueryForm.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][advanced]



    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'resultViewType':
            self.LogInfo('SWITCH TO: ', value)
            viewClass = self.sr.outputTypeCombo.GetValue()
            uthread.new(self.SwitchToView, viewClass)



    def SwitchToView(self, viewClass, populate = 1):
        try:
            sm.GetService('loading').Cycle('Loading')
            if self.sr.outputWindow is None or self.sr.outputWindow.__guid__ != viewClass.__guid__:
                if self.sr.outputWindowContainer is None:
                    self.sr.outputWindowContainer = uicls.Container(name='outputWindow', parent=self.sr.wndForm, align=uiconst.TOALL, pos=(0, 0, 0, 0))
                elif self.sr.outputWindow and hasattr(self.sr.outputWindow, 'OnTabDeselect'):
                    self.sr.outputWindow.OnTabDeselect()
                if self.sr.outputWindow and hasattr(self.sr.outputWindow, '_OnClose'):
                    self.sr.outputWindow._OnClose(self)
                self.sr.outputWindowContainer.Flush()
                self.sr.outputWindow = viewClass(parent=self.sr.outputWindowContainer)
                self.sr.outputWindow.CreateWindow()
            if populate:
                self.sr.outputWindow.PopulateView(self.sr.wndQuery.memberIDs)

        finally:
            sm.GetService('loading').StopCycle()




    def PopulateView(self):
        viewClass = self.sr.outputTypeCombo.GetValue()
        uthread.new(self.SwitchToView, viewClass)
        if len(self.sr.wndQuery.memberIDs):
            self.sr.wndButtonContainer.state = uiconst.UI_NORMAL
            self.ShowHideQuery()
        else:
            self.sr.wndButtonContainer.state = uiconst.UI_HIDDEN




