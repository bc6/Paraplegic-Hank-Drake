import form
import uix
import listentry
import util
import xtriui
import uicls
import uiconst
import uiutil
import localization

class FittingMgmt(uicls.Window):
    __guid__ = 'form.FittingMgmt'
    __nonpersistvars__ = []
    default_windowID = 'FittingMgmt'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/WindowCaption'))
        self.SetWndIcon('ui_17_128_4')
        self.SetMinSize([525, 400])
        self.ownerID = session.charid
        self.fitting = None
        self.wordFilter = None
        self.exportButton = None
        self.fittingSvc = sm.GetService('fittingSvc')
        self.DrawLeftSide()
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftside, 'width', 'x', 256, 350)
        uicls.Line(parent=divider, align=uiconst.TORIGHT, top=const.defaultPadding)
        uicls.Line(parent=divider, align=uiconst.TOLEFT)
        self.DrawRightSide()
        self.HideRightPanel()



    def DrawLeftSide(self):
        self.sr.leftside = uicls.Container(name='leftside', parent=self.sr.main, align=uiconst.TOLEFT, width=256)
        uicls.Container(name='push', parent=self.sr.leftside, align=uiconst.TOTOP, height=6)
        self.sr.leftBottomPanel = uicls.Container(name='leftBottomPanel', parent=self.sr.leftside, align=uiconst.TOBOTTOM, height=26)
        self.sr.leftMainPanel = uicls.Container(name='leftMainPanel', parent=self.sr.leftside, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        dummyParent = uicls.Container(name='dummy', parent=self.sr.leftMainPanel, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        ownerParent = uicls.Container(name='ownerParent', parent=dummyParent, align=uiconst.TOTOP, height=20)
        uicls.Container(name='push', parent=ownerParent, align=uiconst.TORIGHT, width=1)
        options = [(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PersonalFittings'), session.charid), (localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/CorporationFittings'), session.corpid)]
        self.sr.ownerCombo = uicls.Combo(label=None, parent=ownerParent, options=options, name='savedFittingsCombo', select=None, callback=self.ChangeOwnerFilter, pos=(1, 1, 0, 0), align=uiconst.TOALL)
        searchContainer = uicls.Container(name='searchContainer', parent=dummyParent, align=uiconst.TOTOP, top=const.defaultPadding, height=20)
        self.sr.searchTextField = uicls.SinglelineEdit(name='searchTextField', parent=searchContainer, align=uiconst.TOLEFT, width=160, maxLength=40, left=1)
        self.sr.searchButton = uicls.Button(parent=searchContainer, label=localization.GetByLabel('UI/Common/Buttons/Search'), align=uiconst.CENTERRIGHT, func=self.Search)
        self.sr.scroll = uicls.Scroll(parent=dummyParent, align=uiconst.TOALL, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.scroll.multiSelect = 0
        buttonContainer = uicls.Container(name='', parent=self.sr.leftBottomPanel, pos=(0, 0, 0, 0))
        parent = self.sr.fitButtons = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Export'), self.ExportFittings, ()], [localization.GetByLabel('UI/Commands/Import'), self.ImportFittings, ()]], parent=buttonContainer, idx=0)
        self.exportButton = parent.GetBtnByLabel(localization.GetByLabel('UI/Commands/Export'))
        self.DrawFittings()



    def DrawRightSide(self):
        self.sr.rightside = uicls.Container(name='rightside', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        a = uicls.Container(name='push', parent=self.sr.rightside, align=uiconst.TOTOP, height=6)
        self.sr.rightBottomPanel = uicls.Container(name='rightBottomPanel', parent=self.sr.rightside, align=uiconst.TOBOTTOM, height=26)
        self.sr.rightMainPanel = uicls.Container(name='rightMainPanel', parent=self.sr.rightside, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        topParent = uicls.Container(parent=self.sr.rightMainPanel, align=uiconst.TOTOP, height=80)
        topLeftParent = uicls.Container(parent=topParent, align=uiconst.TOLEFT, width=70)
        topRightParent = uicls.Container(parent=topParent, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        bottomParent = uicls.Container(parent=self.sr.rightMainPanel, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOTOP, height=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TORIGHT, width=const.defaultPadding)
        uicls.Frame(parent=bottomParent)
        self.sr.shipIcon = uicls.Icon(parent=topParent, state=uiconst.UI_HIDDEN, size=64, left=const.defaultPadding, ignoreSize=True)
        self.sr.dragIcon = dragIcon = xtriui.FittingDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=topParent, height=64, width=64, top=const.defaultPadding, left=const.defaultPadding)
        dragIcon.Startup(self.fitting)
        dragIcon.hint = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingIconHint')
        dragIcon.OnClick = self.ClickDragIcon
        dragIcon.state = uiconst.UI_NORMAL
        fittingNameContainer = uicls.Container(parent=topRightParent, align=uiconst.TOTOP, height=20)
        self.sr.fittingName = uicls.SinglelineEdit(name='fittingName', parent=fittingNameContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         120,
         0), maxLength=40)
        shipInfoContainer = uicls.Container(parent=topRightParent, align=uiconst.TOTOP, height=20)
        self.sr.shipTypeName = uicls.EveHeaderMedium(text='', parent=shipInfoContainer, align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, left=const.defaultPadding)
        self.sr.infoicon = uicls.InfoIcon(parent=shipInfoContainer, size=16, left=1, top=0, idx=0, state=uiconst.UI_HIDDEN)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.radioButton = uicls.Container(name='', parent=topRightParent, align=uiconst.TOPLEFT, height=50, width=100, top=fittingNameContainer.height + shipInfoContainer.height)
        radioBtns = []
        for (cfgname, value, label, checked, group,) in [['fittingNone',
          session.charid,
          localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Personal'),
          self.ownerID == None,
          'ownership'], ['fittingOwnerCorporation',
          session.corpid,
          localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Corporation'),
          self.ownerID == session.corpid,
          'ownership']]:
            radioBtns.append(uicls.Checkbox(text=label, parent=self.sr.radioButton, configName=cfgname, retval=value, checked=checked, groupname=group, callback=None))

        self.sr.radioButtons = radioBtns
        self.sr.fittingDescription = uicls.EditPlainText(setvalue=None, parent=bottomParent, align=uiconst.TOALL, maxLength=400)
        self.sr.fittingInfo = uicls.Scroll(name='fittingInfoScroll', parent=bottomParent)
        tabs = [[localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Fittings'),
          self.sr.fittingInfo,
          self,
          None,
          self.sr.fittingInfo], [localization.GetByLabel('UI/Common/Description'),
          self.sr.fittingDescription,
          self,
          None,
          self.sr.fittingDescription]]
        self.fittingInfoTab = uicls.TabGroup(name='tabparent', parent=bottomParent, idx=0)
        self.fittingInfoTab.Startup(tabs, 'fittingInfoTab')
        self.sr.fittingInfo.Startup()
        self.sr.saveDeleteButtons = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Fit'), self.Fit, ()], [localization.GetByLabel('UI/Common/Buttons/Save'), self.Save, ()], [localization.GetByLabel('UI/Common/Buttons/Delete'), self.Delete, ()]], parent=self.sr.rightBottomPanel, idx=0)



    def EnableExportButton(self, enable):
        if enable:
            self.exportButton.SetLabel(localization.GetByLabel('UI/Commands/Export'))
            self.exportButton.state = uiconst.UI_NORMAL
        else:
            self.exportButton.SetLabel(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportDisabled'))
            self.exportButton.state = uiconst.UI_DISABLED



    def ClickDragIcon(self, *args):
        subsystems = {}
        techLevel = sm.GetService('godma').GetTypeAttribute(self.fitting.shipTypeID, const.attributeTechLevel)
        if techLevel == 3.0:
            for (typeID, flag, qty,) in self.fitting.fitData:
                if flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
                    subsystems[cfg.invtypes.Get(typeID).groupID] = typeID

            if len(subsystems) != 5:
                raise UserError('NotEnoughSubSystemsNotify', {})
        sm.GetService('preview').PreviewType(self.fitting.shipTypeID, subsystems)



    def Search(self, word, *args):
        self.wordFilter = self.sr.searchTextField.GetValue()
        if self.wordFilter == '':
            self.wordFilter = None
            eve.Message('LookupStringMinimum', {'minimum': 1})
        self.DrawFittings()



    def ShowInfo(self, *args):
        if self.fitting is not None:
            sm.GetService('info').ShowInfo(self.fitting.shipTypeID, None)



    def AddFitting(self, *args):
        form.SaveFittingSettings.Open().ShowModal()



    def ChangeOwnerFilter(self, combo, label, ownerID, *args):
        self.ownerID = ownerID
        self.DrawFittings()
        self.HideRightPanel()



    def DrawFittings(self, *args):
        scrolllist = []
        fittings = self.fittingSvc.GetFittings(self.ownerID).items()
        self.EnableExportButton(len(fittings) > 0)
        maxFittings = None
        if self.ownerID == session.charid:
            maxFittings = const.maxCharFittings
        elif self.ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        fittingsByGroupID = {}
        shipGroups = []
        if self.wordFilter is not None:
            for (fittingID, fitting,) in fittings[:]:
                if self.wordFilter.lower() not in fitting.name.lower():
                    fittings.remove((fittingID, fitting))

        hideRight = True
        for (fittingID, fitting,) in fittings:
            if self.fitting is not None and self.fitting.fittingID == fittingID:
                hideRight = False
            shipTypeID = fitting.shipTypeID
            shipType = cfg.invtypes.Get(shipTypeID)
            if shipType.groupID not in fittingsByGroupID:
                fittingsByGroupID[shipType.groupID] = []
            fittingsByGroupID[shipType.groupID].append(fitting)
            group = cfg.invgroups.Get(shipType.groupID)
            if (group.name, group.groupID) not in shipGroups:
                shipGroups.append((group.name, group.groupID))

        if len(fittings) == 0 and self.wordFilter is not None:
            data = {'label': localization.GetByLabel('UI/Common/NothingFound')}
            scrolllist.append(listentry.Get('Generic', data))
        if hideRight is None:
            self.HideRightPanel()
        shipGroups.sort()
        if maxFittings is not None:
            label = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingsListHeader', numFittings=len(fittings), maxFittings=maxFittings)
            scrolllist.append(listentry.Get('Header', {'label': label}))
        for (groupName, groupID,) in shipGroups:
            data = {'GetSubContent': self.GetShipGroupSubContent,
             'label': groupName,
             'fittings': fittingsByGroupID[groupID],
             'groupItems': fittingsByGroupID[groupID],
             'id': ('fittingMgmtScrollWndGroup', groupName),
             'showicon': 'hide',
             'state': 'locked',
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist, scrolltotop=0)



    def GetShipGroupSubContent(self, nodedata, *args):
        scrolllist = []
        fittingsByType = {}
        shipTypes = []
        for fitting in nodedata.fittings:
            shipTypeID = fitting.shipTypeID
            if shipTypeID not in fittingsByType:
                fittingsByType[shipTypeID] = []
            fittingsByType[shipTypeID].append(fitting)
            type = cfg.invtypes.Get(shipTypeID)
            if (type.name, shipTypeID) not in shipTypes:
                shipTypes.append((type.name, shipTypeID))

        shipTypes.sort()
        for (typeName, typeID,) in shipTypes:
            data = util.KeyVal()
            data.GetSubContent = self.GetFittingSubContent
            data.label = typeName
            data.groupItems = fittingsByType[typeID]
            data.fittings = fittingsByType[typeID]
            data.id = ('fittingMgmtScrollWndType', typeName)
            data.sublevel = 1
            data.showicon = 'hide'
            data.state = 'locked'
            scrolllist.append(listentry.Get('Group', data=data))

        return scrolllist



    def GetFittingSubContent(self, nodedata, *args):
        scrolllist = []
        fittings = []
        for fitting in nodedata.fittings:
            fittings.append((fitting.name, fitting))

        fittings.sort
        for (fittingName, fitting,) in fittings:
            data = util.KeyVal()
            data.label = fittingName
            data.fittingID = fitting.fittingID
            data.fitting = fitting
            data.ownerID = self.ownerID
            data.showinfo = 1
            data.GetMenu = self.GetFittingMenu
            data.showicon = 'hide'
            data.sublevel = 2
            data.OnClick = self.ClickEntry
            scrolllist.append(listentry.Get('FittingEntry', data=data))

        return scrolllist



    def GetFittingMenu(self, entry):
        m = []
        if not self or self.destroyed:
            return m
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        m = [(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/DeleteFitting'), self.DeleteFitting, [entry]), (localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/LoadFitting'), self.fittingSvc.LoadFitting, [ownerID, fittingID])]
        return m



    def DeleteFitting(self, entry):
        if eve.Message('DeleteFitting', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        entries = [entry.sr.node]
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        self.fittingSvc.DeleteFitting(ownerID, fittingID)
        if self.fitting is not None:
            if self.fitting.fittingID == fittingID:
                self.fitting = None
                self.HideRightPanel()



    def ClickEntry(self, entry, *args):
        if not self or self.destroyed:
            return 
        self.ShowRightPanel()
        if self.fitting is not None and self.fitting.fittingID == entry.sr.node.fitting.fittingID:
            return 
        self.fitting = fitting = entry.sr.node.fitting
        self.sr.fittingName.SetText(fitting.name)
        self.sr.fittingDescription.SetText(fitting.description)
        shipName = cfg.invtypes.Get(fitting.shipTypeID).typeName
        self.sr.shipTypeName.text = shipName
        width = uix.GetTextWidth(shipName, uppercase=1)
        self.sr.infoicon.left = width + 15
        self.sr.infoicon.state = uiconst.UI_NORMAL
        self.sr.shipIcon.LoadIconByTypeID(fitting.shipTypeID, ignoreSize=True)
        self.sr.shipIcon.SetSize(64, 64)
        self.sr.shipIcon.state = uiconst.UI_DISABLED
        self.sr.dragIcon.fitting = fitting
        for button in self.sr.radioButtons:
            button.SetValue(fitting.ownerID == button.data['value'])

        scrolllist = self.fittingSvc.GetFittingInfoScrollList(fitting)
        self.sr.fittingInfo.Load(contentList=scrolllist)



    def Save(self, *args):
        if self.fitting is None:
            return 
        newOwnerID = None
        for button in self.sr.radioButtons:
            if button.checked:
                newOwnerID = button.data['value']

        newFitting = None
        if newOwnerID != self.fitting.ownerID:
            newFitting = self.fittingSvc.ChangeOwner(self.fitting.ownerID, self.fitting.fittingID, newOwnerID)
        if newFitting is not None:
            fitting = newFitting
        else:
            fitting = self.fitting
        oldName = self.fitting.name
        newName = self.sr.fittingName.GetValue()
        newDescription = self.sr.fittingDescription.GetValue()
        fit = (self.fitting.shipTypeID, fitting.fitData)
        if fitting.fittingID is None:
            self.fittingSvc.DeleteLocalFitting(oldName)
            self.fittingSvc.PersistFitting(newOwnerID, newName, newDescription, fit=fit)
            self.HideRightPanel()
            return 
        self.fittingSvc.ChangeNameAndDescription(fitting.fittingID, fitting.ownerID, newName, newDescription)
        self.DrawFittings()



    def Fit(self, *args):
        if self.fitting is None:
            return 
        self.fittingSvc.LoadFitting(self.ownerID, self.fitting.fittingID)



    def Delete(self, *args):
        if self.fitting is None:
            return 
        if eve.Message('DeleteFitting', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        self.fittingSvc.DeleteFitting(self.fitting.ownerID, self.fitting.fittingID)
        self.fitting = None
        self.HideRightPanel()



    def HideRightPanel(self):
        self.sr.rightside.state = uiconst.UI_HIDDEN



    def ShowRightPanel(self):
        self.sr.rightside.state = uiconst.UI_NORMAL



    def ExportFittings(self, *args):
        isCorp = False
        if self.ownerID == session.corpid:
            isCorp = True
        form.ExportFittingsWindow.Open(isCorp=isCorp)



    def ImportFittings(self, *args):
        form.ImportFittingsWindow.Open()




class ViewFitting(uicls.Window):
    __guid__ = 'form.ViewFitting'
    __nonpersistvars__ = []
    default_width = 250
    default_height = 300

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.fitting = attributes.fitting
        self.truncated = attributes.truncated
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/WindowCaption'))
        self.SetWndIcon(None)
        self.SetMinSize([250, 300])
        self.fittingSvc = sm.GetService('fittingSvc')
        self.Draw()



    def ClickDragIcon(self, *args):
        subsystems = {}
        techLevel = sm.GetService('godma').GetTypeAttribute(self.fitting.shipTypeID, const.attributeTechLevel)
        if techLevel == 3.0:
            for (typeID, flag, qty,) in self.fitting.fitData:
                if flag >= const.flagSubSystemSlot0 and flag <= const.flagSubSystemSlot7:
                    subsystems[cfg.invtypes.Get(typeID).groupID] = typeID

            if len(subsystems) != 5:
                raise UserError('NotEnoughSubSystemsNotify', {})
        sm.GetService('preview').PreviewType(self.fitting.shipTypeID, subsystems)



    def Draw(self):
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=6)
        topParent = uicls.Container(parent=self.sr.main, align=uiconst.TOTOP, height=80)
        topLeftParent = uicls.Container(parent=topParent, align=uiconst.TOLEFT, width=70)
        topRightParent = uicls.Container(parent=topParent, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        bottomParent = uicls.Container(parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOTOP, height=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        uicls.Container(name='push', parent=bottomParent, align=uiconst.TORIGHT, width=const.defaultPadding)
        self.sr.shipIcon = uicls.Icon(parent=topParent, state=uiconst.UI_HIDDEN, size=64, left=const.defaultPadding, typeID=self.fitting.shipTypeID, ignoreSize=True)
        dragIcon = xtriui.FittingDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=topParent, height=64, width=64, top=const.defaultPadding, left=const.defaultPadding)
        dragIcon.Startup(self.fitting)
        dragIcon.hint = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingIconHint')
        dragIcon.OnClick = self.ClickDragIcon
        dragIcon.state = uiconst.UI_NORMAL
        self.sr.shipIcon.state = uiconst.UI_DISABLED
        fittingNameContainer = uicls.Container(parent=topRightParent, align=uiconst.TOTOP, height=20)
        self.sr.fittingName = uicls.SinglelineEdit(name='fittingName', parent=fittingNameContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         160,
         0), maxLength=40)
        self.sr.fittingName.SetText(self.fitting.name)
        if self.truncated:
            uicls.EveLabelMedium(text=localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Truncated'), parent=fittingNameContainer, left=self.sr.fittingName.width + 10, top=3, width=60, height=20, state=uiconst.UI_NORMAL)
        shipInfoContainer = uicls.Container(parent=topRightParent, align=uiconst.TOTOP, height=20)
        shipName = cfg.invtypes.Get(self.fitting.shipTypeID).typeName
        self.sr.shipName = uicls.EveHeaderMedium(text=shipName, parent=shipInfoContainer, align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, left=const.defaultPadding)
        self.sr.infoicon = uicls.InfoIcon(parent=shipInfoContainer, size=16, left=1, top=0, idx=0)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.infoicon.left = self.sr.shipName.textwidth + 6
        self.sr.radioButton = uicls.Container(name='', parent=topRightParent, align=uiconst.TOPLEFT, height=50, width=100, top=fittingNameContainer.height + shipInfoContainer.height)
        radioBtns = []
        for (cfgname, value, label, checked, group,) in [['fittingNone',
          session.charid,
          localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Personal'),
          True,
          'ownership'], ['fittingOwnerCorporation',
          session.corpid,
          localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Corporation'),
          False,
          'ownership']]:
            radioBtns.append(uicls.Checkbox(text=label, parent=self.sr.radioButton, configName=cfgname, retval=value, checked=checked, groupname=group, callback=None))

        self.sr.radioButtons = radioBtns
        self.sr.fittingDescription = uicls.EditPlainText(parent=bottomParent, align=uiconst.TOALL, maxLength=400)
        self.sr.fittingDescription.SetText(self.fitting.description)
        self.sr.fittingInfo = uicls.Scroll(name='fittingInfoScroll', parent=bottomParent)
        scrolllist = self.fittingSvc.GetFittingInfoScrollList(self.fitting)
        self.sr.fittingInfo.Load(contentList=scrolllist)
        tabs = [[localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/Fittings'),
          self.sr.fittingInfo,
          self,
          None,
          self.sr.fittingInfo], [localization.GetByLabel('UI/Common/Description'),
          self.sr.fittingDescription,
          self,
          None,
          self.sr.fittingDescription]]
        self.fittingInfoTab = uicls.TabGroup(name='tabparent', parent=bottomParent, idx=0)
        self.fittingInfoTab.Startup(tabs, 'fittingInfoTab')
        self.sr.saveDeleteButtons = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Save'), self.Save, ()], [localization.GetByLabel('UI/Common/Buttons/Cancel'), self.CloseByUser, ()]], parent=self.sr.main, idx=0)



    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.fitting.shipTypeID, None)



    def Save(self, *args):
        oldOwnerID = self.fitting.ownerID
        ownerID = None
        for button in self.sr.radioButtons:
            if button.checked:
                ownerID = button.data['value']
                break

        name = self.sr.fittingName.GetValue()
        description = self.sr.fittingDescription.GetValue()
        self.fittingSvc.PersistFitting(ownerID, name, description, fit=(self.fitting.shipTypeID, self.fitting.fitData))
        self.CloseByUser()




class FittingDraggableIcon(uicls.Container):
    __guid__ = 'xtriui.FittingDraggableIcon'

    def Startup(self, fitting):
        self.fitting = fitting



    def GetDragData(self, *args):
        entry = util.KeyVal()
        entry.fitting = self.fitting
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]




