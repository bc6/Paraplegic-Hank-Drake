import util
import xtriui
import uix
import form
import listentry
import blue
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

class CorpMembers(uicls.Container):
    __guid__ = 'form.CorpMembers'
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
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                try:
                    self.SaveChanges()
                except UserError as e:
                    eve.Message(e.msg, e.dict)
                    self.sr.ignoreDirtyFlag = True
            else:
                self.sr.ignoreDirtyFlag = True



    def DataChanged(self, primaryKey, change):
        if not (self and not self.destroyed):
            return 
        if self.destroyed or not hasattr(self, 'sr') or self.sr.scroll is None:
            return 
        dataChangedBy = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/UpdatedByUnknown')
        if self.sr.progressTotal == 0:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 1
        self.sr.progressCurrent += 1
        sm.GetService('loading').ProgressWnd(cfg.eveowners.Get(primaryKey).ownerName, dataChangedBy, self.sr.progressCurrent, self.sr.progressTotal)
        blue.pyos.synchro.Yield()
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



    def Load(self, populateView = 1, *args):
        sm.GetService('corpui').LoadTop('ui_7_64_11', localization.GetByLabel('UI/Corporations/Common/Members'))
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=54)
            self.sr.fwdBtn = uicls.Button(parent=toppar, icon='ui_77_32_41', iconSize=20, align=uiconst.BOTTOMRIGHT, left=6, func=self.Navigate, args=1, hint=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/ViewMoreCorpMembers'))
            self.sr.backBtn = uicls.Button(parent=toppar, icon='ui_77_32_42', iconSize=20, align=uiconst.BOTTOMRIGHT, left=32, func=self.Navigate, args=-1, hint=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/ViewPreviousCorpMembers'))
            uicls.Container(name='push', parent=toppar, align=uiconst.TOTOP, height=6)
            optlist = [[localizationUtil.FormatNumeric(10), 10],
             [localizationUtil.FormatNumeric(25), 25],
             [localizationUtil.FormatNumeric(50), 50],
             [localizationUtil.FormatNumeric(100), 100],
             [localizationUtil.FormatNumeric(500), 500]]
            countcombo = uicls.Combo(label=localization.GetByLabel('UI/Common/PerPage'), parent=toppar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=92, pos=(5, 36, 0, 0))
            self.sr.MembersPerPage = countcombo
            viewOptionsList1 = [[localization.GetByLabel('UI/Corporations/Common/Roles'), VIEW_ROLES], [localization.GetByLabel('UI/Corporations/Common/GrantableRoles'), VIEW_GRANTABLE_ROLES], [localization.GetByLabel('UI/Corporations/Common/Titles'), VIEW_TITLES]]
            viewOptionsList2 = []
            for roleGrouping in self.sr.roleGroupings.itervalues():
                viewOptionsList2.append([localization.GetByMessageID(roleGrouping.roleGroupNameID), roleGrouping.roleGroupID])

            i = 0
            for (optlist, label, config, defval, width,) in [(viewOptionsList1,
              localization.GetByLabel('UI/Common/View'),
              'viewtype',
              1000,
              146), (viewOptionsList2,
              localization.GetByLabel('UI/Common/Type'),
              'rolegroup',
              None,
              146)]:
                combo = uicls.Combo(label=label, parent=toppar, options=optlist, name=config, callback=self.OnComboChange, width=width, pos=(5 + countcombo.left + countcombo.width + i * (width + 4),
                 countcombo.top,
                 0,
                 0))
                combo.OnChange = self.OnComboChange
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
        if populateView:
            self.PopulateView()



    def Navigate(self, direction, *args):
        uthread.new(self.NavigateImpl, direction)



    def NavigateImpl(self, direction):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.ignoreDirtyFlag = True
        self.sr.viewFrom = self.sr.viewFrom + direction * self.sr.viewPerPage
        if self.sr.viewFrom < 0:
            self.sr.viewFrom = 0
        self.PopulateView()



    def PopulateView(self):
        log.LogInfo('PopulateView')
        try:
            serverPage = self.sr.viewFrom / self.sr.members.perPage + 1
            members = self.sr.members.PopulatePage(serverPage)
            viewPage = self.sr.viewFrom / self.sr.viewPerPage + 1
            viewPagesTotal = self.sr.members.totalCount / self.sr.viewPerPage + 1
            blue.pyos.synchro.Yield()
            if viewPage < viewPagesTotal:
                self.sr.fwdBtn.Enable()
            else:
                self.sr.fwdBtn.Disable()
            if viewPage == 1:
                self.sr.backBtn.Disable()
            else:
                self.sr.backBtn.Enable()
            scrolllist = []
            strings = []
            headers = self.GetHeaderValues()
            fixed = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'): 88}
            for each in headers:
                if each in (localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')):
                    continue
                fixed[each] = uix.GetTextWidth(each, 9, 2) + 24 + 4

            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            count = min(self.sr.viewPerPage, self.sr.members.totalCount - self.sr.viewFrom)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', 1, count)
            for number in range(count):
                index = (number + self.sr.viewFrom) % self.sr.members.perPage
                currentServerPage = (number + self.sr.viewFrom) / self.sr.members.perPage + 1
                if serverPage != currentServerPage:
                    members = self.sr.members.PopulatePage(currentServerPage)
                    serverPage = currentServerPage
                rec = members[index]
                text = cfg.eveowners.Get(rec.characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), cfg.eveowners.Get(rec.characterID).ownerName, number, count)
                blue.pyos.synchro.Yield()
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text += '<t>%s' % baseName
                nameColumnLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName')
                baseColumnLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')
                params = {'rec': None,
                 'srcRec': rec,
                 'viewtype': self.sr.viewType,
                 'rolegroup': self.sr.viewRoleGroupingID,
                 'parent': self,
                 'sort_%s' % nameColumnLabel: cfg.eveowners.Get(rec.characterID).ownerName,
                 'sort_%s' % baseColumnLabel: baseName}
                if self.sr.viewType == VIEW_TITLES:
                    titles = sm.GetService('corp').GetTitles()
                    titlesByID = util.IndexRowset(titles.header, titles.lines, 'titleID')
                    titleID = 1
                    for x in range(1, 1 + len(titles)):
                        title = titlesByID[titleID]
                        sortvalue = rec.titleMask & titleID == titleID
                        text += ['<t>',
                         '[',
                         sortvalue,
                         ']']
                        params['sort_%s' % title.titleName] = sortvalue
                        titleID = titleID << 1

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        (columnName, subColumns,) = column
                        newtext = '<t>'
                        sortmask = ''
                        for (subColumnName, role,) in subColumns:
                            isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                            if isChecked:
                                newtext += ' [X] %s' % subColumnName
                            else:
                                newtext += ' [ ] %s' % subColumnName
                            sortmask += [' ', 'X'][(not not isChecked)]

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
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', count, count)
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
                if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                    self.SaveChanges()
                else:
                    self.sr.ignoreDirtyFlag = True
            self.sr.viewFrom = 0
            self.sr.viewPerPage = value
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
                text = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                sortvalues[characterID] = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'): text}
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text += '<t>%s' % baseName
                sortvalues[characterID]['base'] = baseName
                if self.sr.viewType == VIEW_TITLES:
                    titles = sm.GetService('corp').GetTitles()
                    titlesByID = util.IndexRowset(titles.header, titles.lines, 'titleID')
                    titleID = 1
                    for ix in range(1, 1 + len(titles)):
                        title = titlesByID[titleID]
                        sortvalue = rec.titleMask & titleID == titleID
                        text += '<t>[%s]' % sortvalue
                        sortvalues[characterID][title.titleName.lower().replace(' ', '')] = str(sortvalue)
                        titleID = titleID << 1

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        (columnName, subColumns,) = column
                        newtext = '<t>'
                        sortvalue = []
                        for subColumn in subColumns:
                            for (subColumnName, role,) in subColumns:
                                isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                                if isChecked:
                                    newtext += ' [X] %s' % subColumnName
                                else:
                                    newtext += ' [ ] %s' % subColumnName
                                sortvalue.append(isChecked)


                        sortvalues[characterID][columnName.lower().replace(' ', '')] = str(sortvalue)
                        text += newtext

                strings.append((text,
                 9,
                 2,
                 0))

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            fixed = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'): 88}
            for header in headers:
                if header in (localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')):
                    continue
                fixed[header] = 100

            self.sr.scroll.adjustableColumns = 1
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                characterID = entry.rec.characterID
                text = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                for (columnName, sortvalue,) in sortvalues[characterID].iteritems():
                    entry.Set('sort_%s' % columnName, sortvalue)

                if entry.panel is None or entry.panel.destroyed:
                    continue
                entry.panel.sr.loadingCharacterID = [characterID]
                entry.panel.LoadColumns(characterID)
                entry.panel.UpdateLabelText()
                entry.panel.UpdateHint()

            self.sr.scroll.LoadHeaders(headers)

        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', nCount, nCount)
            blue.pyos.synchro.Yield()




    def GetHeaderValues(self):
        viewType = self.sr.viewType
        if viewType == VIEW_TITLES:
            header = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')]
            titles = sm.GetService('corp').GetTitles()
            titlesByID = {}
            for title in titles:
                titlesByID[title.titleID] = title

            titleID = 1
            for ix in range(1, 1 + len(titles)):
                title = titlesByID[titleID]
                header.append(title.titleName)
                titleID = titleID << 1

        else:
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            header = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase')]
            for column in roleGroup.columns:
                (columnName, subColumns,) = column
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
            return 
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
                sm.ScatterEvent('OnRoleEdit', rows)
            if myRow is not None:
                sm.GetService('sessionMgr').PerformSessionChange('corp.UpdateMembers', sm.GetService('corp').UpdateMembers, myRow)

        finally:
            if nCount:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount - 1, nCount)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount, nCount)
                blue.pyos.synchro.Yield()





