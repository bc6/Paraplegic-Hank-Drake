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
import localization
import localizationUtil

class ScannerFilterEditor(uicls.Window):
    __guid__ = 'form.ScannerFilterEditor'
    default_windowID = 'probeScannerFilterEditor'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.specialGroups = util.GetNPCGroups()
        self.scope = 'inflight'
        self.SetCaption(localization.GetByLabel('UI/Inflight/Scanner/ScannerFilterEditor'))
        self.SetMinSize([300, 250])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.main = uiutil.GetChild(self, 'main')
        topParent = uicls.Container(name='topParent', parent=self.sr.main, height=64, align=uiconst.TOTOP)
        topParent.padRight = 6
        topParent.padLeft = 6
        uicls.EveHeaderSmall(text=localization.GetByLabel('UI/Inflight/Scanner/FilterName'), parent=topParent, state=uiconst.UI_DISABLED, idx=0, top=2)
        nameEdit = uicls.SinglelineEdit(name='name', parent=topParent, setvalue=None, align=uiconst.TOTOP, maxLength=64)
        nameEdit.top = 16
        self.sr.nameEdit = nameEdit
        hint = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/SelectGroupsToFilter'), parent=topParent, align=uiconst.TOTOP)
        hint.top = 4
        self.sr.topParent = topParent
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.multiSelect = 0
        self.DefineButtons(uiconst.OKCANCEL, okLabel=localization.GetByLabel('UI/Common/Buttons/Save'), okFunc=self.SaveChanges, cancelFunc=self.Close)
        self.scanGroupsNames = {const.probeScanGroupAnomalies: localization.GetByLabel('UI/Inflight/Scanner/CosmicAnomaly'),
         const.probeScanGroupSignatures: localization.GetByLabel('UI/Inflight/Scanner/CosmicSignature'),
         const.probeScanGroupShips: localization.GetByLabel('UI/Inflight/Scanner/Ship'),
         const.probeScanGroupStructures: localization.GetByLabel('UI/Inflight/Scanner/Structure'),
         const.probeScanGroupDronesAndProbes: localization.GetByLabel('UI/Inflight/Scanner/DroneAndProbe')}
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
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/PleaseNameFilter')})
            self.sr.nameEdit.SetFocus()
            return 
        if name.lower() == localization.GetByLabel('UI/Common/Show all').lower():
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/CannotNameFilter')})
            return 
        groups = [ key for (key, value,) in self.tempState.iteritems() if bool(value) ]
        if not groups:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Inflight/Scanner/SelectGroupsForFilter')})
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
        self.Close()



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
        m = [None, (localization.GetByLabel('UI/Common/SelectAll'), self.SelectGroup, (node, True)), (localization.GetByLabel('UI/Common/DeselectAll'), self.SelectGroup, (node, False))]
        return m



    def SelectGroup(self, node, isSelect):
        for (groupID, label,) in node.groupItems:
            self.tempState[groupID] = isSelect

        self.LoadTypes()



    def GetCatSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        for (groupID, name,) in nodedata.groupItems:
            if groupID == const.groupCosmicSignature:
                for signatureType in [const.attributeScanGravimetricStrength,
                 const.attributeScanLadarStrength,
                 const.attributeScanMagnetometricStrength,
                 const.attributeScanRadarStrength,
                 const.attributeScanAllStrength]:
                    name = localization.GetByLabel(const.EXPLORATION_SITE_TYPES[signatureType])
                    checked = self.tempState.get((groupID, signatureType), 0)
                    data = util.KeyVal()
                    data.label = name
                    data.checked = checked
                    data.cfgname = 'probeScannerFilters'
                    data.retval = (groupID, signatureType)
                    data.OnChange = self.CheckBoxChange
                    data.sublevel = 0
                    scrolllist.append(listentry.Get('Checkbox', data=data))

            else:
                name = cfg.invgroups.Get(groupID).groupName
                checked = self.tempState.get(groupID, 0)
                data = util.KeyVal()
                data.label = name
                data.checked = checked
                data.cfgname = 'probeScannerFilters'
                data.retval = groupID
                data.OnChange = self.CheckBoxChange
                data.sublevel = 0
                scrolllist.append(listentry.Get('Checkbox', data=data))

        return localizationUtil.Sort(scrolllist, key=lambda x: x.label)



    def CheckBoxChange(self, checkbox, *args):
        self.tempState[checkbox.data['retval']] = checkbox.checked




