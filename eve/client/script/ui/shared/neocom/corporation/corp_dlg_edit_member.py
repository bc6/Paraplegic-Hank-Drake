import blue
import uthread
import util
import xtriui
import uix
import uiutil
import form
import listentry
import types
import lg
import log
import uicls
import uiconst
import localization
import localizationUtil
import corputil
from corputil import *
HAS_ROLE_OR_TITLE_ICON_ID = 'ui_38_16_193'
DOES_NOT_HAVE_ROLE_OR_TITLE_ICON_ID = 'ui_38_16_194'

class EditMemberDialog(uicls.Window):
    __guid__ = 'form.EditMemberDialog'
    __notifyevents__ = ['OnRoleEdit']
    default_windowID = 'EditMemberDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        charID = attributes.charID
        self.charID = None
        self.corp = None
        self.standing2 = None
        self.charMgr = None
        self.memberinfo = None
        self.corporation = None
        self.roleGroupings = None
        self.myGrantableRoles = None
        self.myGrantableRolesAtHQ = None
        self.myGrantableRolesAtBase = None
        self.myGrantableRolesAtOther = None
        self.isCEOorEq = None
        self.userIsCEO = None
        self.member = None
        self.playerIsCEO = 0
        self.playerIsDirector = 0
        self.roles = 0
        self.grantableRoles = 0
        self.rolesAtHQ = 0
        self.grantableRolesAtHQ = 0
        self.rolesAtBase = 0
        self.grantableRolesAtBase = 0
        self.rolesAtOther = 0
        self.grantableRolesAtOther = 0
        self.baseID = None
        self.title = ''
        self.titleMask = 0
        self.args = ''
        self.ddxFunction = None
        self.viewType = 0
        self.viewRoleGroupingID = 1
        self.bases = [('-', None)]
        self.LoadServices()
        self.LoadChar(charID)
        self.SetScope('all')
        if not self.member:
            self.Close()
            return 
        self.SetTopparentHeight(70)
        self.SetCaption(localization.GetByLabel('UI/Corporations/EditMemberDialog/EditMemberCaption'))
        self.SetMinSize([310, 300])
        self.sr.main = uiutil.GetChild(self, 'main')
        self.wndCombos = uicls.Container(name='options', parent=self.sr.main, align=uiconst.TOTOP, height=34)
        viewOptionsList1 = [[localization.GetByLabel('UI/Corporations/Common/Roles'), VIEW_ROLES], [localization.GetByLabel('UI/Corporations/Common/GrantableRoles'), VIEW_GRANTABLE_ROLES]]
        viewOptionsList2 = []
        for roleGrouping in self.roleGroupings.itervalues():
            viewOptionsList2.append([localization.GetByMessageID(roleGrouping.roleGroupNameID), roleGrouping.roleGroupID])

        i = 0
        for (optlist, label, config, defval,) in [(viewOptionsList1,
          localization.GetByLabel('UI/Common/View'),
          'viewtype',
          1000), (viewOptionsList2,
          localization.GetByLabel('UI/Corporations/Common/GroupType'),
          'rolegroup',
          None)]:
            combo = uicls.Combo(label=label, parent=self.wndCombos, options=optlist, name=config, callback=self.OnComboChange, width=146, pos=(const.defaultPadding + i * 152 + 1,
             const.defaultPadding + 12,
             0,
             0))
            i += 1

        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81], [localization.GetByLabel('UI/Corporations/EditMemberDialog/Apply'),
          self.OnApply,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        cap = uicls.CaptionLabel(text=cfg.eveowners.Get(self.charID).name, parent=self.sr.topParent, align=uiconst.RELATIVE, left=74, top=20)
        if self.member.title:
            uicls.EveHeaderLarge(text=self.member.title, parent=self.sr.topParent, align=uiconst.RELATIVE, left=cap.left, top=cap.top + cap.height, bold=True)
        buttons = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Corporations/EditMemberDialog/GiveShares'),
          self.OnGiveShares,
          (),
          81]])
        self.sr.main.children.insert(1, buttons)
        maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        maintabs.Startup([[localization.GetByLabel('UI/Generic/General'),
          self.sr.scroll,
          self,
          'general',
          buttons],
         [localization.GetByLabel('UI/Corporations/Common/Roles'),
          self.sr.scroll,
          self,
          'roles'],
         [localization.GetByLabel('UI/Corporations/Common/Titles'),
          self.sr.scroll,
          self,
          'titles'],
         [localization.GetByLabel('UI/Corporations/EditMemberDialog/RolesSummary'),
          self.sr.scroll,
          self,
          'roles_summary']], 'editmemberdialog')
        self.sr.maintabs = maintabs
        self.DisplayPhoto()



    def LoadServices(self):
        self.corp = sm.GetService('corp')
        self.standing2 = sm.RemoteSvc('standing2')
        self.charMgr = sm.RemoteSvc('charMgr')



    def LoadChar(self, charID):
        self.charID = charID
        self.security = self.standing2.GetSecurityRating(self.charID)
        self.memberinfo = self.charMgr.GetPrivateInfo(self.charID)
        self.corporation = self.corp.GetCorporation(eve.session.corpid)
        (grantableRoles, grantableRolesAtHQ, grantableRolesAtBase, grantableRolesAtOther,) = self.corp.GetMyGrantableRoles()
        self.myGrantableRoles = grantableRoles
        self.myGrantableRolesAtHQ = grantableRolesAtHQ
        self.myGrantableRolesAtBase = grantableRolesAtBase
        self.myGrantableRolesAtOther = grantableRolesAtOther
        self.isCEOorEq = const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector
        self.userIsCEO = self.corp.UserIsCEO()
        self.member = self.corp.GetMember(self.charID)
        if not self.member:
            return 
        self.divisionalRoles = self.corp.GetDivisionalRoles()
        self.divisions = self.corp.GetDivisionNames()
        self.locationalRoles = self.corp.GetLocationalRoles()
        self.playerIsCEO = self.corporation.ceoID == self.charID
        self.playerIsDirector = 0
        if const.corpRoleDirector & self.member.roles == const.corpRoleDirector:
            self.playerIsDirector = 1
        self.roles = self.member.roles
        self.grantableRoles = self.member.grantableRoles
        self.title = self.member.title
        self.rolesAtHQ = self.member.rolesAtHQ
        self.grantableRolesAtHQ = self.member.grantableRolesAtHQ
        self.rolesAtBase = self.member.rolesAtBase
        self.grantableRolesAtBase = self.member.grantableRolesAtBase
        self.rolesAtOther = self.member.rolesAtOther
        self.grantableRolesAtOther = self.member.grantableRolesAtOther
        self.baseID = self.member.baseID
        self.titleMask = self.member.titleMask
        self.offices = self.corp.GetMyCorporationsOffices()
        self.offices.Fetch(0, len(self.offices))
        self.bases = [(localization.GetByLabel('UI/Corporations/EditMemberDialog/NoBase'), None)]
        rows = self.offices
        if rows and len(rows):
            stations = []
            for row in rows:
                stationName = localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberBase', station=row.stationID)
                stations.append((stationName, (stationName, row.stationID)))

            stations = uiutil.SortListOfTuples(stations)
            self.bases += stations
        self.roleGroupings = sm.GetService('corp').GetRoleGroupings()



    def DisplayPhoto(self):
        self.picture = uiutil.GetChild(self, 'mainicon')
        self.picture.left = const.defaultPadding
        self.picture.top = const.defaultPadding
        self.picture.state = uiconst.UI_DISABLED
        uiutil.GetChild(self, 'clippedicon').Close()
        sm.GetService('photo').GetPortrait(self.charID, 128, self.picture)



    def Load(self, args):
        if self.ddxFunction is not None:
            try:
                self.ddxFunction()

            finally:
                self.ddxFunction = None

        self.args = args
        self.SetHint()
        self.sr.scroll.Clear()
        if args == 'general':
            self.wndCombos.state = uiconst.UI_HIDDEN
            self.OnTabGeneral()
        elif args == 'roles':
            self.wndCombos.state = uiconst.UI_NORMAL
            self.OnTabRoles()
        elif args == 'titles':
            self.wndCombos.state = uiconst.UI_HIDDEN
            self.OnTabTitles()
        elif args == 'roles_summary':
            self.wndCombos.state = uiconst.UI_HIDDEN
            self.OnTabRolesSummary()



    def FindNode(self, nodeName):
        for entry in self.sr.scroll.GetNodes():
            if entry.name == nodeName:
                return entry




    def GetNodeValue(self, nodeName):
        node = self.FindNode(nodeName)
        if node is not None:
            return node.setValue
        raise RuntimeError('ChildNotFound', nodeName)



    def OnTabGeneral(self):
        scrolllist = []
        canEditBase = corputil.CanEditBase(self.playerIsCEO, self.userIsCEO, eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector)
        if not self.title:
            self.title = ''
        if canEditBase:
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberTitleCaption'),
             'setValue': self.title,
             'name': 'general_title',
             'lines': 1,
             'maxLength': 100}))
            data = {'options': self.bases,
             'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberBaseCaption'),
             'cfgName': 'baseID',
             'setValue': self.baseID,
             'OnChange': self.OnComboChange,
             'name': 'baseID'}
            scrolllist.append(listentry.Get('Combo', data))
        else:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberTitleCaption'),
             'text': self.title}))
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberBaseCaption'),
             'text': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberBase', station=self.baseID)}))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberJoined'),
         'text': localizationUtil.FormatDateTime(self.member.startDateTime, dateFormat='short')}))
        scrolllist.append(listentry.Get('Divider'))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/Name'),
         'text': cfg.eveowners.Get(self.memberinfo.characterID).name}))
        if self.memberinfo.gender:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Common/Gender/Gender'),
             'text': localization.GetByLabel('UI/Common/Gender/Male')}))
        else:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Common/Gender/Gender'),
             'text': localization.GetByLabel('UI/Common/Gender/Female')}))
        race = sm.GetService('cc').GetRaceDataByID(self.memberinfo.raceID)
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Common/Race'),
         'text': localization.GetByMessageID(race.raceNameID)}))
        bloodline = sm.GetService('cc').GetData('bloodlines', ['bloodlineID', self.memberinfo.bloodlineID])
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Common/Bloodline'),
         'text': localization.GetByMessageID(bloodline.bloodlineNameID)}))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/DateOfBirth'),
         'text': localizationUtil.FormatDateTime(self.memberinfo.createDateTime, dateFormat='short')}))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/SecurityStatus'),
         'text': localizationUtil.FormatNumeric(float(self.security), decimalPlaces=2)}))
        self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
        if canEditBase:
            self.ddxFunction = self.DDXTabGeneral



    def OnComboChange(self, combo, header, value, *args):
        if combo.name == 'baseID':
            self.baseID = value
        if combo.name in ('viewtype', 'rolegroup'):
            uthread.new(self.OnComboChangeImpl, combo.name, value)



    def OnComboChangeImpl(self, entryName, value):
        if entryName == 'viewtype':
            self.viewType = value
        elif entryName == 'rolegroup':
            self.viewRoleGroupingID = value
        self.OnTabRoles()



    def DDXTabGeneral(self):
        try:
            log.LogInfo('>>>DDXTabGeneral')
            self.title = self.GetNodeValue('general_title')

        finally:
            log.LogInfo('<<<DDXTabGeneral')




    def AddCheckBox(self, role, on, roleVariablesName):
        log.LogInfo('AddCheckBox', role, on, roleVariablesName)
        label = localization.GetByLabel('UI/Corporations/EditMemberDialog/RoleNameDashRoleDescription', roleName=role.shortDescription, roleDesc=role.description)
        data = {'label': label,
         'checked': on,
         'cfgname': roleVariablesName,
         'retval': role.roleID,
         'OnChange': self.CheckBoxChange}
        return listentry.Get('Checkbox', data)



    def CheckBoxChange(self, checkbox):
        log.LogInfo('CheckBoxChange', checkbox)
        roleVariablesName = checkbox.data['key']
        if roleVariablesName not in ('roles', 'grantableRoles', 'rolesAtHQ', 'grantableRolesAtHQ', 'rolesAtBase', 'grantableRolesAtBase', 'rolesAtOther', 'grantableRolesAtOther'):
            return 
        roleID = checkbox.data['retval']
        if not checkbox.GetValue():
            setattr(self, roleVariablesName, getattr(self, roleVariablesName) & ~roleID)
        else:
            setattr(self, roleVariablesName, getattr(self, roleVariablesName) | roleID)
        if roleVariablesName == 'roles' and roleID == const.corpRoleDirector:
            self.playerIsDirector = [1, 0][self.playerIsDirector]
            self.roles = [0, const.corpRoleDirector][self.playerIsDirector]
            self.grantableRoles = 0
            self.rolesAtHQ = 0
            self.grantableRolesAtHQ = 0
            self.rolesAtBase = 0
            self.grantableRolesAtBase = 0
            self.rolesAtOther = 0
            self.grantableRolesAtOther = 0
            self.OnTabRoles()



    def OnTabRoles(self):
        playersRoles = None
        roleVariablesName = ''
        rolesToDisplay = None
        if self.viewType == VIEW_TITLES:
            raise RuntimeError('NotImplemented')
        if self.roleGroupings.has_key(self.viewRoleGroupingID):
            roleGrouping = self.roleGroupings[self.viewRoleGroupingID]
            if self.viewType == VIEW_ROLES:
                roleVariablesName = roleGrouping.appliesTo
            elif self.viewType == VIEW_GRANTABLE_ROLES:
                roleVariablesName = roleGrouping.appliesToGrantable
            playersRoles = getattr(self, roleVariablesName)
            rolesToDisplay = []
            for (columnName, subColumns,) in roleGrouping.columns:
                for subColumn in subColumns:
                    (name, role,) = subColumn
                    rolesToDisplay.append(role)


        if playersRoles is None:
            raise RuntimeError('WhatAreWeLookingAt')
        self.DisplayRoles(self.viewType == VIEW_GRANTABLE_ROLES, playersRoles, roleVariablesName, rolesToDisplay)



    def DisplayRoles(self, grantable, playersRoles, roleVariablesName, rolesToDisplay):
        myBaseID = self.corp.GetMember(eve.session.charid).baseID
        scrolllist = []
        for role in rolesToDisplay:
            canEditRole = corputil.CanEditRole(role.roleID, grantable, self.playerIsCEO, self.playerIsDirector, self.userIsCEO, self.viewRoleGroupingID, myBaseID, self.baseID, self.myGrantableRoles, self.myGrantableRolesAtHQ, self.myGrantableRolesAtBase, self.myGrantableRolesAtOther)
            hasRole = role.roleID & playersRoles == role.roleID
            if self.playerIsCEO:
                hasRole = 1
            if self.playerIsDirector and not (grantable and role.roleID == const.corpRoleDirector):
                hasRole = 1
            if canEditRole:
                scrolllist.append(self.AddCheckBox(role, hasRole, roleVariablesName))
            else:
                iconID = HAS_ROLE_OR_TITLE_ICON_ID
                if not hasRole:
                    iconID = DOES_NOT_HAVE_ROLE_OR_TITLE_ICON_ID
                scrolllist.append(listentry.Get('IconLabelText', {'label': role.shortDescription,
                 'text': role.description,
                 'icon': iconID,
                 'iconPositioning': listentry.IconLabelText.ICON_POS_IN_FRONT_OF_LABEL,
                 'textpos': 170,
                 'labelAdjust': 165}))

        self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def OnOK(self, *args):
        self.OnApply()
        self.Close()



    def OnCancel(self, *args):
        self.Close()



    def OnApply(self, *args):
        try:
            if self.ddxFunction is not None:
                self.ddxFunction()

        finally:
            self.ddxFunction = None

        self.UpdateMember()



    def GetChangeDict(self):
        change = {}
        if self.roles != self.member.roles:
            change['roles'] = [self.member.roles, self.roles]
        if self.grantableRoles != self.member.grantableRoles:
            change['grantableRoles'] = [self.member.grantableRoles, self.grantableRoles]
        if self.rolesAtHQ != self.member.rolesAtHQ:
            change['rolesAtHQ'] = [self.member.rolesAtHQ, self.rolesAtHQ]
        if self.grantableRolesAtHQ != self.member.grantableRolesAtHQ:
            change['grantableRolesAtHQ'] = [self.member.grantableRolesAtHQ, self.grantableRolesAtHQ]
        if self.rolesAtBase != self.member.rolesAtBase:
            change['rolesAtBase'] = [self.member.rolesAtBase, self.rolesAtBase]
        if self.grantableRolesAtBase != self.member.grantableRolesAtBase:
            change['grantableRolesAtBase'] = [self.member.grantableRolesAtBase, self.grantableRolesAtBase]
        if self.rolesAtOther != self.member.rolesAtOther:
            change['rolesAtOther'] = [self.member.rolesAtOther, self.rolesAtOther]
        if self.grantableRolesAtOther != self.member.grantableRolesAtOther:
            change['grantableRolesAtOther'] = [self.member.grantableRolesAtOther, self.grantableRolesAtOther]
        if self.baseID != self.member.baseID:
            change['baseID'] = [self.member.baseID, self.baseID]
        if self.title != self.member.title:
            change['title'] = [self.member.title, self.title]
        if self.titleMask != self.member.titleMask:
            change['titleMask'] = [self.member.titleMask, self.titleMask]
        return change



    def UpdateMember(self):
        if self.playerIsCEO and not self.userIsCEO:
            return 
        if self.member.roles & const.corpRoleDirector == const.corpRoleDirector:
            if self.roles & const.corpRoleDirector == const.corpRoleDirector:
                self.roles = self.member.roles
                self.grantableRoles = self.member.grantableRoles
                self.rolesAtHQ = self.member.rolesAtHQ
                self.grantableRolesAtHQ = self.member.grantableRolesAtHQ
                self.rolesAtBase = self.member.rolesAtBase
                self.grantableRolesAtBase = self.member.grantableRolesAtBase
                self.rolesAtOther = self.member.rolesAtOther
                self.grantableRolesAtOther = self.member.grantableRolesAtOther
                self.titleMask = self.member.titleMask
        newTitle = self.title
        divisionID = self.member.divisionID
        squadronID = self.member.squadronID
        if not self.isCEOorEq:
            newTitle = None
            divisionID = None
            squadronID = None
        change = self.GetChangeDict()
        if len(change) == 0:
            return 
        roles = self.roles
        grantableRoles = self.grantableRoles
        rolesAtHQ = self.rolesAtHQ
        grantableRolesAtHQ = self.grantableRolesAtHQ
        rolesAtBase = self.rolesAtBase
        grantableRolesAtBase = self.grantableRolesAtBase
        rolesAtOther = self.rolesAtOther
        grantableRolesAtOther = self.grantableRolesAtOther
        titleMask = self.titleMask
        if roles & const.corpRoleDirector == const.corpRoleDirector:
            grantableRoles = 0
            rolesAtHQ = 0
            grantableRolesAtHQ = 0
            rolesAtBase = 0
            grantableRolesAtBase = 0
            rolesAtOther = 0
            grantableRolesAtOther = 0
            titleMask = 0
        if self.titleMask == self.member.titleMask:
            titleMask = None
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Corporations/EditMemberDialog/SavingChanges'), '', 0, 2)
            if self.charID == eve.session.charid:
                sm.GetService('sessionMgr').PerformSessionChange('corp.UpdateMember', self.corp.UpdateMember, self.charID, newTitle, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, self.baseID, titleMask)
            else:
                self.corp.UpdateMember(self.charID, newTitle, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, self.baseID, titleMask)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Corporations/EditMemberDialog/RefreshingChanges'), '', 1, 2)
            self.LoadChar(self.charID)
            self.Load(self.args)

        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Corporations/EditMemberDialog/ProgressCompleted'), '', 2, 2)




    def OnGiveShares(self, *args):
        ret = uix.QtyPopup(2147483647, 1, '1', localization.GetByLabel('UI/Corporations/EditMemberDialog/HowManySharesToGive', player=self.charID), localization.GetByLabel('UI/Corporations/EditMemberDialog/GiveShares'))
        if ret is not None:
            amount = ret['qty']
            self.corp.MoveCompanyShares(eve.session.corpid, self.charID, amount)



    def OnTabTitles(self):
        scrolllist = []
        titles = sm.GetService('corp').GetTitles()
        titlesByID = util.IndexRowset(titles.header, titles.lines, 'titleID')
        titleID = 1
        for ix in range(1, 1 + len(titles)):
            title = titlesByID[titleID]
            hasTitle = self.titleMask & title.titleID == title.titleID
            if self.playerIsDirector or self.playerIsCEO:
                hasTitle = True
            if not self.isCEOorEq or self.playerIsDirector or self.playerIsCEO:
                iconID = DOES_NOT_HAVE_ROLE_OR_TITLE_ICON_ID
                if hasTitle:
                    iconID = HAS_ROLE_OR_TITLE_ICON_ID
                scrolllist.append(listentry.Get('IconLabelText', {'label': title.titleName,
                 'text': '',
                 'icon': iconID,
                 'iconPositioning': listentry.IconLabelText.ICON_POS_REPLACES_TEXT}))
            else:
                scrolllist.append(self.AddTitleCheckBox(title, hasTitle))
            titleID = titleID << 1

        self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)



    def AddTitleCheckBox(self, title, hasTitle):
        data = {'label': title.titleName,
         'checked': hasTitle,
         'cfgname': title.titleName,
         'retval': title.titleID,
         'OnChange': self.TitleCheckBoxChange}
        return listentry.Get('Checkbox', data)



    def TitleCheckBoxChange(self, checkbox):
        titleID = checkbox.data['retval']
        if not checkbox.GetValue():
            self.titleMask = self.titleMask & ~titleID
        else:
            self.titleMask = self.titleMask | titleID



    def OnTabRolesSummary(self):
        scrolllist = []
        titles = sm.GetService('corp').GetTitles()
        for roleGrouping in self.roleGroupings.itervalues():
            roleMask = getattr(self, roleGrouping.appliesTo)
            grantableRoleMask = getattr(self, roleGrouping.appliesToGrantable)
            roleMaskByTitles = long(0)
            for title in titles:
                if not self.member.titleMask & title.titleID == title.titleID:
                    continue
                titleRolesRelevant = getattr(title, roleGrouping.appliesTo)
                titleRolesFiltered = titleRolesRelevant & roleGrouping.roleMask
                if not titleRolesFiltered:
                    continue
                roleMaskByTitles |= titleRolesFiltered

            rolesToDisplay = []
            for (columnName, subColumns,) in roleGrouping.columns:
                for subColumn in subColumns:
                    (name, role,) = subColumn
                    hasRole = roleMask & role.roleID == role.roleID
                    hasGrantableRole = grantableRoleMask & role.roleID == role.roleID
                    hasRoleByTitle = roleMaskByTitles & role.roleID == role.roleID
                    if self.playerIsDirector:
                        hasRole = True
                        hasGrantableRole = role.roleID != const.corpRoleDirector
                    if self.playerIsCEO:
                        hasRole = True
                        hasGrantableRole = True
                    if not hasRole and not hasGrantableRole and not hasRoleByTitle:
                        continue
                    roleName = columnName
                    if len(name):
                        roleName = localization.GetByLabel('UI/Corporations/EditMemberDialog/RoleNameAndRole', role=roleName, name=name)
                    rolesToDisplay.append([roleName,
                     hasRole,
                     hasGrantableRole,
                     hasRoleByTitle])


            rolesToDisplay.sort(lambda a, b: -(a[0].upper() < b[0].upper()))
            data = {'GetSubContent': self.GetSubContentRoleSummary,
             'label': localization.GetByLabel('UI/Corporations/EditMemberDialog/RoleAndNumber', role=localization.GetByMessageID(roleGrouping.roleGroupNameID), numRoles=len(rolesToDisplay)),
             'groupItems': None,
             'id': ('RolesSummary', roleGrouping.roleGroupName),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'rolesToDisplay': rolesToDisplay}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(roleGrouping.roleGroupName, 0)

        self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)



    def GetSubContentRoleSummary(self, nodedata, *args):
        subcontent = []
        for roleToDisplay in nodedata.rolesToDisplay:
            (roleName, hasRole, hasGrantableRole, hasRoleByTitle,) = roleToDisplay
            desc = []
            if hasRole:
                desc.append(localization.GetByLabel('UI/Corporations/Common/Role'))
            if hasRoleByTitle:
                desc.append(localization.GetByLabel('UI/Corporations/EditMemberDialog/RoleByTitle'))
            if hasGrantableRole:
                desc.append(localization.GetByLabel('UI/Corporations/EditMemberDialog/GrantableRole'))
            subcontent.append(listentry.Get('LabelText', {'label': roleName,
             'text': localizationUtil.FormatGenericList(desc),
             'textpos': 170}))

        return subcontent



    def OnRoleEdit(self, rows):
        for row in rows:
            if row.characterID == self.charID:
                self.roles = row.roles
                self.grantableRoles = row.grantableRoles
                self.Load(self.args)
                break





