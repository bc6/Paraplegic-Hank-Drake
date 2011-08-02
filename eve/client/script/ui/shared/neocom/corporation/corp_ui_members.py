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



    def OnClose_(self, *args):
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



    def OnDataChanged(self, rowset, primaryKey, change, notificationParams):
        if not (self and not self.destroyed):
            return 
        dataChangedBy = 'Unknown'
        if notificationParams.has_key('charIDcallee'):
            if notificationParams['charIDcallee'] > 0:
                dataChangedBy = cfg.eveowners.Get(notificationParams['charIDcallee']).ownerName
        if self.sr.progressTotal == 0:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 1
        self.sr.progressCurrent += 1
        sm.GetService('loading').ProgressWnd(cfg.eveowners.Get(primaryKey).ownerName, '%s: %s' % (mls.UI_CORP_UPDATEDBY, dataChangedBy), self.sr.progressCurrent, self.sr.progressTotal)
        blue.pyos.synchro.Yield()
        if self.destroyed or not hasattr(self, 'sr') or self.sr.scroll is None:
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
                entry.panel.OnDataChanged(rowset, primaryKey, change, notificationParams)
                break

        if self.sr.progressCurrent >= self.sr.progressTotal:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 0



    def Load(self, populateView = 1, *args):
        sm.GetService('corpui').LoadTop('ui_7_64_11', mls.UI_CORP_MEMBERS)
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=54)
            icon = uicls.Button(parent=toppar, icon='ui_77_32_41', iconSize=20, align=uiconst.BOTTOMRIGHT, left=6, func=self.Navigate, args=1)
            icon.hint = mls.UI_GENERIC_VIEWMORE
            self.sr.fwdBtn = icon
            icon = uicls.Button(parent=toppar, icon='ui_77_32_42', iconSize=20, align=uiconst.BOTTOMRIGHT, left=26, func=self.Navigate, args=-1)
            icon.hint = mls.UI_GENERIC_PREVIOUS
            self.sr.backBtn = icon
            uicls.Container(name='push', parent=toppar, align=uiconst.TOTOP, height=6)
            optlist = [['10', 10],
             ['25', 25],
             ['50', 50],
             ['100', 100],
             ['500', 500]]
            countcombo = uicls.Combo(label=mls.UI_SHARED_PERPAGE, parent=toppar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=92, pos=(5, 36, 0, 0))
            self.sr.MembersPerPage = countcombo
            viewOptionsList1 = [[mls.UI_CORP_ROLES, VIEW_ROLES], [mls.UI_CORP_GRANTABLEROLES, VIEW_GRANTABLE_ROLES], [mls.UI_CORP_TITLES, VIEW_TITLES]]
            viewOptionsList2 = []
            for roleGrouping in self.sr.roleGroupings.itervalues():
                viewOptionsList2.append([Tr(roleGrouping.roleGroupName, 'dbo.crpRoleGroups.roleGroupName', roleGrouping.roleGroupID), roleGrouping.roleGroupID])

            i = 0
            for (optlist, label, config, defval, width,) in [(viewOptionsList1,
              mls.UI_GENERIC_VIEW,
              'viewtype',
              1000,
              146), (viewOptionsList2,
              mls.UI_GENERIC_TYPE,
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
            buttons = [[mls.UI_CMD_SAVECHANGES,
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
        nIndex = 0
        nCount = 0
        try:
            nFrom = self.sr.viewFrom
            nTo = nFrom + self.sr.viewPerPage
            if nTo >= len(self.sr.members) - 1:
                nTo = len(self.sr.members)
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
            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            scrolllist = []
            strings = []
            headers = self.GetHeaderValues()
            fixed = {mls.UI_GENERIC_BASE: 88}
            for each in headers:
                if each in (mls.UI_GENERIC_NAME, mls.UI_GENERIC_BASE):
                    continue
                fixed[each] = uix.GetTextWidth(each, 9, 2) + 24 + 4

            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            log.LogWarn('About to Fetch from:', nFrom, 'count:', nTo - nFrom)
            self.sr.members.Fetch(nFrom, nTo - nFrom)
            for ix in range(nFrom, nTo):
                nIndex += 1
                rec = self.sr.members[ix]
                text = cfg.eveowners.Get(rec.characterID).ownerName
                sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text += '<t>%s' % baseName
                params = {'rec': None,
                 'srcRec': rec,
                 'viewtype': self.sr.viewType,
                 'rolegroup': self.sr.viewRoleGroupingID,
                 'parent': self,
                 'sort_%s' % mls.UI_GENERIC_NAME: uiutil.UpperCase(cfg.eveowners.Get(rec.characterID).ownerName),
                 'sort_%s' % mls.UI_GENERIC_BASE: baseName}
                if self.sr.viewType == VIEW_TITLES:
                    titles = sm.GetService('corp').GetTitles()
                    titlesByID = util.IndexRowset(titles.header, titles.lines, 'titleID')
                    titleID = 1
                    for ix in range(1, 1 + len(titles)):
                        title = titlesByID[titleID]
                        sortvalue = rec.titleMask & titleID == titleID
                        text += '<t>[%s]' % sortvalue
                        params['sort_%s' % title.titleName] = '%s' % sortvalue
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
                            newtext += ' [%s] %s' % ([' ', 'X'][(not not isChecked)], subColumnName)
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
            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, '', nCount, nCount)
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
                sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                sortvalues[characterID] = {mls.UI_GENERIC_NAME: uiutil.UpperCase(text)}
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text += '<t>%s' % baseName
                sortvalues[characterID]['base'] = uiutil.UpperCase(baseName)
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
                                newtext += ' [%s] %s' % ([' ', 'X'][(not not isChecked)], subColumnName)
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
            fixed = {mls.UI_GENERIC_BASE: 88}
            for header in headers:
                if header in (mls.UI_GENERIC_NAME, mls.UI_GENERIC_BASE):
                    continue
                fixed[header] = 100

            self.sr.scroll.adjustableColumns = 1
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                characterID = entry.rec.characterID
                text = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, text, nIndex, nCount)
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
            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_LOADING, '', nCount, nCount)
            blue.pyos.synchro.Yield()




    def GetHeaderValues(self):
        viewType = self.sr.viewType
        if viewType == VIEW_TITLES:
            header = [mls.UI_GENERIC_NAME, mls.UI_GENERIC_BASE]
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
            header = [mls.UI_GENERIC_NAME, mls.UI_GENERIC_BASE]
            for column in roleGroup.columns:
                (columnName, subColumns,) = column
                header.append(columnName)

            header = [ header.replace(' ', '<br>').replace('PERSONNEL', 'PERS.') for header in header ]
        return header



    def MemberDetails(self, charid, *args):
        log.LogInfo('members.MemberDetails charid:', charid)
        sm.GetService('window').GetWindow('EditMemberDialog', 1, charID=charid)



    def IsDirty(self):
        try:
            sm.GetService('loading').Cycle(mls.UI_GENERIC_PLEASEWAIT)
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
            sm.GetService('loading').Cycle(mls.UI_GENERIC_PREPARINGTOUPDATE)
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
            sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_UPDATING, '', nIndex, nCount)
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
                sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_UPDATED, '', nCount - 1, nCount)
                blue.pyos.synchro.Sleep(500)
                sm.GetService('loading').ProgressWnd(mls.UI_GENERIC_UPDATED, '', nCount, nCount)
                blue.pyos.synchro.Yield()





