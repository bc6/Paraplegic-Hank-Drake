import blue
import uix
import uiutil
import trinity
import xtriui
import form
import util
import listentry
import uicls
import uiconst

class ScannerFilterEditor(uicls.Window):
    __guid__ = 'form.ScannerFilterEditor'
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.specialGroups = sm.GetService('state').GetNPCGroups()
        self.scope = 'inflight'
        self.SetCaption(mls.UI_GENERIC_SCANNER_FILTER_EDITOR)
        self.SetMinSize([300, 250])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.main = uiutil.GetChild(self, 'main')
        topParent = uicls.Container(name='topParent', parent=self.sr.main, height=64, align=uiconst.TOTOP)
        topParent.padRight = 6
        topParent.padLeft = 6
        uicls.Label(text=mls.UI_GENERIC_FILTER_NAME, parent=topParent, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1, idx=0, top=2)
        nameEdit = uicls.SinglelineEdit(name='name', parent=topParent, setvalue=None, align=uiconst.TOTOP, maxLength=64)
        nameEdit.top = 16
        self.sr.nameEdit = nameEdit
        hint = uicls.Label(text=mls.UI_GENERIC_SELECT_GROUPS_TO_FILTER, parent=topParent, align=uiconst.TOTOP, autowidth=0)
        hint.top = 4
        self.sr.topParent = topParent
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.multiSelect = 0
        self.DefineButtons(uiconst.OKCANCEL, okLabel=mls.UI_CMD_SAVE, okFunc=self.SaveChanges, cancelFunc=self.SelfDestruct)
        self.scanGroupsNames = {const.probeScanGroupAnomalies: mls.UI_INFLIGHT_SCANCOSMICANOMALY,
         const.probeScanGroupSignatures: mls.UI_INFLIGHT_SCANCOSMICSIGNATURE,
         const.probeScanGroupShips: mls.UI_GENERIC_SHIP,
         const.probeScanGroupStructures: mls.UI_GENERIC_STRUCTURE,
         const.probeScanGroupDronesAndProbes: mls.UI_INFLIGHT_SCANDRONEANDPROBE}
        self.Maximize()
        self.OnResizeUpdate()



    def LoadData(self, filterName):
        self.tempState = {}
        if filterName:
            self.sr.nameEdit.SetValue(filterName)
            userSettings = settings.user.ui.Get('probeScannerFilters', {}).get(filterName, [])
            for each in userSettings:
                self.tempState[each] = True

        self._originalName = filterName
        self.LoadTypes()



    def OnResizeUpdate(self, *args):
        self.sr.topParent.height = sum([ each.height + each.top + each.padTop + each.padBottom for each in self.sr.topParent.children if each.align == uiconst.TOTOP ])



    def SaveChanges(self, *args):
        name = self.sr.nameEdit.GetValue()
        if name is None or name == '':
            eve.Message('CustomNotify', {'notify': mls.UI_GENERIC_PLEASE_NAME_FILTER})
            self.sr.nameEdit.SetFocus()
            return 
        if name.lower() == mls.UI_STATION_SHOWALL.lower():
            eve.Message('CustomNotify', {'notify': mls.UI_GENERIC_CANNOTNAMEFILTER})
            return 
        groups = [ key for (key, value,) in self.tempState.iteritems() if bool(value) ]
        if not groups:
            eve.Message('CustomNotify', {'notify': mls.UI_GENERIC_SELECT_GROUPS_FOR_FILTER})
            self.sr.scroll.SetFocus()
            return 
        current = settings.user.ui.Get('probeScannerFilters', {})
        if name in current:
            if eve.Message('OverwriteFilter', {'filter': name}, uiconst.YESNO) != uiconst.ID_YES:
                return 
        if name != self._originalName and self._originalName in current:
            del current[self._originalName]
        current[name] = groups
        settings.user.ui.Set('probeScannerFilters', current)
        settings.user.ui.Set('activeProbeScannerFilter', name)
        sm.ScatterEvent('OnNewScannerFilterSet', name, current[name])
        self.SelfDestruct()



    def LoadTypes(self):
        categoryList = {}
        for (scanGroupID, groupSet,) in const.probeScanGroups.iteritems():
            if scanGroupID not in self.scanGroupsNames:
                continue
            catName = self.scanGroupsNames[scanGroupID]
            for groupID in groupSet:
                name = cfg.invgroups.Get(groupID).name
                if catName not in categoryList:
                    categoryList[catName] = [(groupID, name)]
                elif (groupID, name) not in categoryList[catName]:
                    categoryList[catName].append((groupID, name))


        sortCat = categoryList.keys()
        sortCat.sort()
        scrolllist = []
        for catName in sortCat:
            data = {'GetSubContent': self.GetCatSubContent,
             'MenuFunction': self.GetSubFolderMenu,
             'label': catName,
             'id': ('ProberScannerGroupSel', catName),
             'groupItems': categoryList[catName],
             'showlen': 1,
             'showicon': 'hide',
             'sublevel': 0,
             'state': 'locked',
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        self.sr.scroll.Load(contentList=scrolllist, scrolltotop=0, scrollTo=getattr(self, 'cachedScrollPos', 0.0))



    def GetSubFolderMenu(self, node):
        m = [None, (mls.UI_CMD_SELECTALL, self.SelectGroup, (node, True)), (mls.UI_CMD_DESELECTALL, self.SelectGroup, (node, False))]
        return m



    def SelectGroup(self, node, isSelect):
        for (groupID, label,) in node.groupItems:
            self.tempState[groupID] = isSelect

        self.LoadTypes()



    def GetCatSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        for (groupID, name,) in nodedata.groupItems:
            name = cfg.invgroups.Get(groupID).groupName
            checked = self.tempState.get(groupID, 0)
            data = util.KeyVal()
            data.label = name
            data.checked = checked
            data.cfgname = 'probeScannerFilters'
            data.retval = groupID
            data.OnChange = self.CheckBoxChange
            data.sublevel = 0
            scrolllist.append((name, listentry.Get('Checkbox', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        return scrolllist



    def CheckBoxChange(self, checkbox, *args):
        self.tempState[checkbox.data['retval']] = checkbox.checked




