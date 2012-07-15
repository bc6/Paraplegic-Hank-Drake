#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/corp_ui_member_view_role_mgt.py
import util
import xtriui
import uix
import form
import listentry
import blue
import types
import uthread
import lg
import log
import corputil
import uiconst
import uicls
import uiutil
import localization
import localizationUtil
from corputil import *

class CorpMembersViewRoleManagement(uicls.Container):
    __guid__ = 'form.CorpMembersViewRoleManagement'
    __nonpersistvars__ = []

    def init(self):
        self.sr.members = sm.GetService('corp').GetMembers()
        self.sr.viewType = 0
        self.sr.viewRoleGroupingID = 1
        self.sr.viewPerPage = 10
        self.sr.viewFrom = 0
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
        self.sr.progressCurrent = 0
        self.sr.progressTotal = 0
        self.sr.memberIDs = []
        self.sr.members.AddListener(self)
        self.sr.scroll = None
        self.sr.ignoreDirtyFlag = False

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def _OnClose(self, *args):
        self.OnTabDeselect()
        self.sr.members.RemoveListener(self)

    def OnTabDeselect(self):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.ignoreDirtyFlag = True

    def DataChanged(self, primaryKey, change):
        if not (self and not self.destroyed):
            return
        if self.sr.progressTotal == 0:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 1
        self.sr.progressCurrent += 1
        sm.GetService('loading').ProgressWnd(cfg.eveowners.Get(primaryKey).ownerName, '', self.sr.progressCurrent, self.sr.progressTotal)
        blue.pyos.synchro.Yield()
        if self.sr.scroll is None:
            return
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None or entry.rec is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.rec.characterID == primaryKey:
                if change.has_key('corporationID') and change['corporationID'][1] == None:
                    self.LogInfo('removing member list entry for charID:', primaryKey)
                    self.sr.scroll.RemoveEntries([entry])
                    self.LogInfo('member list entry removed for charID:', primaryKey)
                    break
                entry.panel.DataChanged(primaryKey, change)
                break

        if self.sr.progressCurrent >= self.sr.progressTotal:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 0

    def CreateWindow(self):
        toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=54)
        sidepar = uicls.Container(name='sidepar', parent=toppar, align=uiconst.TORIGHT, width=54)
        icon = uicls.Button(parent=toppar, icon='ui_77_32_41', iconSize=20, align=uiconst.BOTTOMRIGHT, left=6, func=self.Navigate, args=1)
        icon.hint = localization.GetByLabel('UI/Common/Next')
        self.sr.fwdBtn = icon
        icon = uicls.Button(parent=toppar, icon='ui_77_32_42', iconSize=20, align=uiconst.BOTTOMRIGHT, left=26, func=self.Navigate, args=-1)
        icon.hint = localization.GetByLabel('UI/Common/Previous')
        self.sr.backBtn = icon
        uicls.Container(name='push', parent=toppar, align=uiconst.TOTOP, height=6)
        optlist = [[localizationUtil.FormatNumeric(10), 10],
         [localizationUtil.FormatNumeric(25), 25],
         [localizationUtil.FormatNumeric(50), 50],
         [localizationUtil.FormatNumeric(100), 100],
         [localizationUtil.FormatNumeric(500), 500]]
        countcombo = uicls.Combo(label=localization.GetByLabel('UI/Common/PerPage'), parent=toppar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=92, pos=(2, 36, 0, 0))
        self.sr.MembersPerPage = countcombo
        viewOptionsList1 = [[localization.GetByLabel('UI/Corporations/Common/Roles'), VIEW_ROLES], [localization.GetByLabel('UI/Corporations/Common/GrantableRoles'), VIEW_GRANTABLE_ROLES], [localization.GetByLabel('UI/Corporations/Common/Titles'), VIEW_TITLES]]
        viewOptionsList2 = []
        for roleGrouping in self.sr.roleGroupings.itervalues():
            viewOptionsList2.append([localization.GetByMessageID(roleGrouping.roleGroupNameID), roleGrouping.roleGroupID])

        i = 0
        for optlist, label, config, defval in [(viewOptionsList1,
          localization.GetByLabel('UI/Common/ViewMode'),
          'viewtype',
          1000), (viewOptionsList2,
          localization.GetByLabel('UI/Common/Type'),
          'rolegroup',
          None)]:
            combo = uicls.Combo(label=label, parent=toppar, options=optlist, name=config, callback=self.OnComboChange, width=146, pos=(countcombo.left + countcombo.width + 6 + i * 152,
             countcombo.top,
             0,
             0))
            setattr(self.sr, config + 'Combo', combo)
            i += 1

        self.sr.scroll = uicls.Scroll(name='journal', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.OnColumnChanged = self.OnColumnChanged
        buttons = [[localization.GetByLabel('UI/Common/Buttons/SaveChanges'),
          self.SaveChanges,
          (),
          81]]
        btns = uicls.ButtonGroup(btns=buttons)
        self.children.insert(0, btns)

    def Navigate(self, direction, *args):
        uthread.new(self.NavigateImpl, direction)

    def NavigateImpl(self, direction):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.self.sr.ignoreDirtyFlag = True
        self.sr.viewFrom = self.sr.viewFrom + direction * self.sr.viewPerPage
        if self.sr.viewFrom < 0:
            self.sr.viewFrom = 0
        self.PopulateView()

    def PopulateView(self, memberIDs = None):
        nIndex = 0
        nCount = 0
        try:
            log.LogInfo('memberIDs: ', memberIDs)
            if memberIDs is not None:
                self.sr.memberIDs = memberIDs
            nFrom = self.sr.viewFrom
            nTo = nFrom + self.sr.viewPerPage
            if nTo >= len(self.sr.memberIDs) - 1:
                nTo = len(self.sr.memberIDs)
                self.sr.fwdBtn.Disable()
            else:
                self.sr.fwdBtn.Enable()
            if nFrom < 0:
                nFrom = 0
            if nFrom == 0:
                self.sr.backBtn.Disable()
            else:
                self.sr.backBtn.Enable()
            nCount = nTo - nFrom
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Generic/Loading'), '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            scrolllist = []
            strings = []
            headers = self.GetHeaderValues()
            fixed = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'): 88}
            for each in headers:
                if each.lower() in (localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')):
                    continue
                fixed[each] = uix.GetTextWidth(each, 9, 2) + 24 + 4

            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            log.LogWarn('About to FetchByKey: ', self.sr.memberIDs, ' from: ', nFrom, ' to: ', nTo)
            self.sr.members.FetchByKey(self.sr.memberIDs)
            for ix in range(nFrom, nTo):
                nIndex += 1
                rec = self.sr.members.GetByKey(self.sr.memberIDs[ix])
                ownerName = cfg.eveowners.Get(rec.characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Generic/Loading'), ownerName, nIndex, nCount)
                blue.pyos.synchro.Yield()
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text = '%s<t>%s' % (ownerName, baseName)
                params = {'rec': None,
                 'srcRec': rec,
                 'viewtype': self.sr.viewType,
                 'rolegroup': self.sr.viewRoleGroupingID,
                 'parent': self,
                 'sort_%s' % localization.GetByLabel('UI/Insurance/InsuranceWindow/Name'): cfg.eveowners.Get(rec.characterID).ownerName,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'): baseName}
                if self.sr.viewType == VIEW_TITLES:
                    for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                        sortvalue = rec.titleMask & title.titleID == title.titleID
                        text += '<t>[%s]' % sortvalue
                        params['sort_%s' % title.titleName] = sortvalue

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        columnName, subColumns = column
                        newtext = '<t>'
                        sortmask = ''
                        for subColumnName, role in subColumns:
                            isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                            if isChecked:
                                newtext += ' [X] %s' % subColumnName
                            else:
                                newtext += ' [ ] %s' % subColumnName
                            sortmask += [' ', 'X'][not not isChecked]

                        params['sort_%s' % columnName] = sortmask
                        text += newtext

                params['label'] = text
                scrolllist.append(listentry.Get('CorpMemberRoleEntry', params))
                strings.append((text,
                 9,
                 2,
                 0))

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'CorporationMembers'
            self.sr.scroll.Load(None, scrolllist, self.sr.scroll.GetSortBy(), reversesort=1, headers=headers)
            self.OnColumnChanged(self.sr.scroll.sr.tabs)
            self.sr.ignoreDirtyFlag = False
        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', nCount, nCount)
            blue.pyos.synchro.Yield()

    def OnColumnChanged(self, tabstops):
        self.LogInfo('ENTRIES [', len(self.sr.scroll.GetNodes()), ']:', self.sr.scroll.GetNodes())
        for node in self.sr.scroll.GetNodes():
            self.LogInfo('>>> ENTRY:', node)
            if node.panel is None or node.panel.destroyed or node is None:
                continue
            panel = node.panel
            try:
                panel.Lock()
                panel.sr.loadingCharacterID = [node.srcRec.characterID]
                panel.OnUpdateTabstops(tabstops)
            finally:
                panel.Unlock()

    def OnComboChange(self, entry, header, value, *args):
        uthread.new(self.OnComboChangeImpl, entry.name, value)

    def OnComboChangeImpl(self, entryName, value):
        if entryName == 'membersperpage':
            if not self.sr.ignoreDirtyFlag and self.IsDirty():
                if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    self.SaveChanges()
                else:
                    self.sr.self.sr.ignoreDirtyFlag = True
            self.sr.viewPerPage = value
            self.sr.viewFrom = 0
            return self.PopulateView()
        if entryName == 'viewtype':
            self.sr.viewType = value
            if value == VIEW_TITLES:
                self.sr.rolegroupCombo.state = uiconst.UI_HIDDEN
            else:
                self.sr.rolegroupCombo.state = uiconst.UI_NORMAL
        elif entryName == 'rolegroup':
            self.sr.viewRoleGroupingID = value
        nIndex = 0
        nCount = 0
        try:
            nCount = self.sr.viewPerPage
            for entry in self.sr.scroll.GetNodes():
                if entry is None or entry.rec is None:
                    continue
                if entry.panel is None or entry.panel.destroyed:
                    continue
                nCount += 1

            strings = []
            headers = self.GetHeaderValues()
            headertabs = []
            sortvalues = {}
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                rec = entry.rec
                characterID = rec.characterID
                ownerName = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), ownerName, nIndex, nCount)
                blue.pyos.synchro.Yield()
                sortvalues[characterID] = {localization.GetByLabel('UI/Common/Name'): ownerName}
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text = '%s<t>%s' % (ownerName, baseName)
                sortvalues[characterID][localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')] = baseName.upper()
                if self.sr.viewType == VIEW_TITLES:
                    for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                        sortvalue = rec.titleMask & title.titleID == title.titleID
                        text += '<t>[%s]' % sortvalue
                        sortvalues[characterID][title.titleName] = str(sortvalue)

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        columnName, subColumns = column
                        newtext = '<t>'
                        sortvalue = []
                        for subColumn in subColumns:
                            for subColumnName, role in subColumns:
                                isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                                if isChecked:
                                    newtext += ' [X] %s' % subColumnName
                                else:
                                    newtext += ' [ ] %s' % subColumnName
                                sortvalue.append(isChecked)

                        sortvalues[characterID][columnName] = str(sortvalue)
                        text += newtext

                strings.append((text,
                 9,
                 2,
                 0))

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                characterID = entry.rec.characterID
                text = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                for columnName, sortvalue in sortvalues[characterID].iteritems():
                    entry.Set('sort_%s' % columnName, sortvalue)

                if entry.panel is None or entry.panel.destroyed:
                    continue
                entry.panel.sr.loadingCharacterID = [characterID]
                entry.panel.LoadColumns(characterID)
                entry.panel.UpdateLabelText()

            self.sr.scroll.LoadHeaders(headers)
        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', nCount, nCount)
            blue.pyos.synchro.Yield()

    def GetHeaderValues(self):
        viewType = self.sr.viewType
        if viewType == VIEW_TITLES:
            header = [localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')]
            for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                header.append(title.titleName)

        else:
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            header = [localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')]
            for column in roleGroup.columns:
                columnName, subColumns = column
                colName = uiutil.ReplaceStringWithTags(columnName)
                header.append(colName)

        return header

    def MemberDetails(self, charid, *args):
        log.LogInfo('members.MemberDetails charid:', charid)
        form.EditMemberDialog.Open(charID=charid)

    def IsDirty(self):
        try:
            sm.GetService('loading').Cycle(localization.GetByLabel('UI/Common/PleaseWait'))
            if self and not self.destroyed and self.sr.scroll is not None:
                nodes = self.sr.scroll.GetNodes()
                for node in nodes:
                    if node is None or node is None or node.rec is None:
                        continue
                    changed = 0
                    if node.rec.roles != node.rec.oldRoles:
                        changed = 1
                    elif node.rec.grantableRoles != node.rec.oldGrantableRoles:
                        changed = 1
                    elif node.rec.rolesAtHQ != node.rec.oldRolesAtHQ:
                        changed = 1
                    elif node.rec.grantableRolesAtHQ != node.rec.oldGrantableRolesAtHQ:
                        changed = 1
                    elif node.rec.rolesAtBase != node.rec.oldRolesAtBase:
                        changed = 1
                    elif node.rec.grantableRolesAtBase != node.rec.oldGrantableRolesAtBase:
                        changed = 1
                    elif node.rec.rolesAtOther != node.rec.oldRolesAtOther:
                        changed = 1
                    elif node.rec.grantableRolesAtOther != node.rec.oldGrantableRolesAtOther:
                        changed = 1
                    elif node.rec.baseID != node.rec.oldBaseID:
                        changed = 1
                    elif node.rec.titleMask != node.rec.oldTitleMask:
                        changed = 1
                    if not changed:
                        continue
                    return 1

            return 0
        finally:
            sm.GetService('loading').StopCycle()

    def SaveChanges(self, *args):
        nodesToUpdate = []
        try:
            sm.GetService('loading').Cycle(localization.GetByLabel('UI/Common/PreparingToUpdate'))
            for node in self.sr.scroll.GetNodes():
                if not node or not node or not node.rec:
                    continue
                changed = 0
                if node.rec.roles != node.rec.oldRoles:
                    changed = 1
                elif node.rec.grantableRoles != node.rec.oldGrantableRoles:
                    changed = 1
                elif node.rec.rolesAtHQ != node.rec.oldRolesAtHQ:
                    changed = 1
                elif node.rec.grantableRolesAtHQ != node.rec.oldGrantableRolesAtHQ:
                    changed = 1
                elif node.rec.rolesAtBase != node.rec.oldRolesAtBase:
                    changed = 1
                elif node.rec.grantableRolesAtBase != node.rec.oldGrantableRolesAtBase:
                    changed = 1
                elif node.rec.rolesAtOther != node.rec.oldRolesAtOther:
                    changed = 1
                elif node.rec.grantableRolesAtOther != node.rec.oldGrantableRolesAtOther:
                    changed = 1
                elif node.rec.baseID != node.rec.oldBaseID:
                    changed = 1
                elif node.rec.titleMask != node.rec.oldTitleMask:
                    changed = 1
                if not changed:
                    continue
                nodesToUpdate.append(node)

        finally:
            sm.GetService('loading').StopCycle()

        nCount = len(nodesToUpdate)
        if nCount == 0:
            log.LogWarn('Nothing to save')
        self.sr.progressCurrent = 0
        self.sr.progressTotal = nCount
        nIndex = 0
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updating'), '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            rows = None
            myRow = None
            for node in nodesToUpdate:
                entry = node.rec
                src = node.srcRec
                characterID = entry.characterID
                title = src.title
                divisionID = src.divisionID
                squadronID = src.squadronID
                roles = entry.roles
                grantableRoles = entry.grantableRoles
                rolesAtHQ = entry.rolesAtHQ
                grantableRolesAtHQ = entry.grantableRolesAtHQ
                rolesAtBase = entry.rolesAtBase
                grantableRolesAtBase = entry.grantableRolesAtBase
                rolesAtOther = entry.rolesAtOther
                grantableRolesAtOther = entry.grantableRolesAtOther
                baseID = entry.baseID
                titleMask = entry.titleMask
                if entry.titleMask == src.titleMask:
                    titleMask = None
                if roles & const.corpRoleDirector == const.corpRoleDirector:
                    roles = const.corpRoleDirector
                    grantableRoles = 0
                    rolesAtHQ = 0
                    grantableRolesAtHQ = 0
                    rolesAtBase = 0
                    grantableRolesAtBase = 0
                    rolesAtOther = 0
                    grantableRolesAtOther = 0
                if characterID == eve.session.charid:
                    if myRow is None:
                        myRow = util.Rowset(['characterID',
                         'title',
                         'divisionID',
                         'squadronID',
                         'roles',
                         'grantableRoles',
                         'rolesAtHQ',
                         'grantableRolesAtHQ',
                         'rolesAtBase',
                         'grantableRolesAtBase',
                         'rolesAtOther',
                         'grantableRolesAtOther',
                         'baseID',
                         'titleMask'])
                    myRow.append([characterID,
                     None,
                     None,
                     None,
                     roles,
                     grantableRoles,
                     rolesAtHQ,
                     grantableRolesAtHQ,
                     rolesAtBase,
                     grantableRolesAtBase,
                     rolesAtOther,
                     grantableRolesAtOther,
                     baseID,
                     titleMask])
                else:
                    if rows is None:
                        rows = util.Rowset(['characterID',
                         'title',
                         'divisionID',
                         'squadronID',
                         'roles',
                         'grantableRoles',
                         'rolesAtHQ',
                         'grantableRolesAtHQ',
                         'rolesAtBase',
                         'grantableRolesAtBase',
                         'rolesAtOther',
                         'grantableRolesAtOther',
                         'baseID',
                         'titleMask'])
                    rows.append([characterID,
                     None,
                     None,
                     None,
                     roles,
                     grantableRoles,
                     rolesAtHQ,
                     grantableRolesAtHQ,
                     rolesAtBase,
                     grantableRolesAtBase,
                     rolesAtOther,
                     grantableRolesAtOther,
                     baseID,
                     titleMask])

            if rows is not None:
                sm.GetService('corp').UpdateMembers(rows)
            if myRow is not None:
                sm.GetService('sessionMgr').PerformSessionChange('corp.UpdateMembers', sm.GetService('corp').UpdateMembers, myRow)
        finally:
            if nCount:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount - 1, nCount)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount, nCount)
                blue.pyos.synchro.Yield()