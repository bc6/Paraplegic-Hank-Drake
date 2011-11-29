import uix
import uiutil
import util
import form
import listentry
import sys
import uicls
import uiconst
import log
import localization
import localizationUtil

class StationManagementDialog(uicls.Window):
    __guid__ = 'form.StationManagementDialog'
    default_windowID = 'StationManagement'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.corpStationMgr = None
        self.services = None
        self.servicesByID = None
        self.station = None
        self.solarsystem = None
        self.serviceAccessRulesByServiceID = None
        self.modifiedServiceAccessRulesByServiceID = None
        self.serviceCostModifiers = None
        self.modifiedServiceCostModifiers = None
        self.rentableItems = None
        self.modifiedRentableItems = None
        self.ddxFunction = None
        self.ddxArguments = {}
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Station/StationManagment/StationDetails'), localization.GetByLabel('UI/Common/GettingData'), 1, 4)
        self.SetScope('station')
        self.SetCaption(localization.GetByLabel('UI/Station/StationManagment/StationManagment'))
        self.SetMinSize([400, 300])
        self.SetTopparentHeight(70)
        defaultPadding = (const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=defaultPadding)
        self.sr.scroll2 = uicls.Scroll(parent=self.sr.main, padding=defaultPadding)
        self.sr.scroll2.sr.id = 'station_management_scroll2'
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.sr.hint = None
        cap = uicls.CaptionLabel(text=cfg.evelocations.Get(eve.session.stationid).name, parent=self.sr.topParent, align=uiconst.CENTERLEFT, left=74, width=320)
        self.DisplayLogo()
        self.ShowLoad()
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Station/StationServices'), localization.GetByLabel('UI/Common/GettingData'), 2, 4)
        self.LoadServices()
        self.LoadData()
        self.HideLoad()
        if not self or not self or self.destroyed:
            return 

        def CreateTab(label, arg, useScroll2 = False):
            scroll = self.sr.scroll
            if useScroll2:
                scroll = self.sr.scroll2
            return [localization.GetByLabel(label),
             scroll,
             self,
             arg,
             scroll]


        maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=0, groupID='stationmanagementpanel')
        maintabs.Startup([CreateTab('UI/Station/StationManagment/StationDetails', 'station_details'), CreateTab('UI/Station/StationManagment/ServiceAccessControl', 'station_service_access_control')], groupID='stationmanagementpanel')
        tabs = [CreateTab('UI/Station/StationManagment/CostModifiers', 'cost_modifiers'), CreateTab('UI/Station/StationManagment/CloneContracts', 'clone_contracts')]
        serviceMask = self.GetStationServiceMask()
        if const.stationServiceOfficeRental == const.stationServiceOfficeRental & serviceMask:
            tabs.append(CreateTab('UI/Corporations/Common/Offices', 'offices', useScroll2=True))
        if self.ShouldDisplayImprovements():
            tabs.append(CreateTab('UI/Station/StationManagment/StationImprovements', 'improvements'))
        subtabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=1, groupID='stationmanagementpanel')
        subtabs.Startup(tabs, groupID='stationmanagementpanel', autoselecttab=0)
        self.sr.maintabs = maintabs
        self.sr.subtabs = subtabs
        self.sr.maintabs.AddRow(subtabs)
        self.sr.maintabs.AutoSelect()
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Commands/ProgressDone'), localization.GetByLabel('UI/Common/GettingData'), 4, 4)



    def LoadServices(self):
        self.corpStationMgr = sm.GetService('corp').GetCorpStationManager()



    def GetStationServiceMask(self):
        return eve.stationItem.serviceMask | const.stationServiceJumpCloneFacility



    def GetServiceName(self, service):
        return localization.GetByMessageID(service.serviceNameID)



    def IsServiceAvailable(self, serviceID):
        return serviceID == self.GetStationServiceMask() & serviceID



    def LoadData(self):
        self.services = self.corpStationMgr.GetStationServiceIdentifiers()
        self.servicesByID = {}
        self.serviceAccessRulesByServiceID = {}
        self.modifiedServiceAccessRulesByServiceID = {}
        self.modifiedServiceCostModifiers = []
        self.modifiedRentableItems = []
        serviceMask = self.GetStationServiceMask()
        for service in self.services:
            if not self.IsActiveService(service.serviceID):
                continue
            if service.serviceID == serviceMask & service.serviceID:
                self.servicesByID[service.serviceID] = service
                serviceAccessRule = self.corpStationMgr.GetStationServiceAccessRule(eve.session.stationid, service.serviceID)
                self.serviceAccessRulesByServiceID[service.serviceID] = serviceAccessRule
                log.LogInfo('serviceAccessRule:', serviceAccessRule)

        self.serviceCostModifiers = self.corpStationMgr.GetStationManagementServiceCostModifiers(eve.session.stationid)
        self.station = self.corpStationMgr.GetStationDetails(eve.session.stationid)
        orbitName = cfg.evelocations.Get(self.station.orbitID).name
        if self.station.stationName.startswith(orbitName):
            orbitNameStripped = uiutil.StripTags(orbitName)
            orbitNameStripped += ' - '
            self.station.stationName = uiutil.ReplaceStringWithTags(self.station.stationName, old=orbitNameStripped, new='')
        if self.station.description is None:
            self.station.description = ''
        log.LogInfo('GetStationDetails:', self.station)
        rentableItems = self.corpStationMgr.GetRentableItems()
        self.rentableItems = []
        for rentableItem in rentableItems:
            self.rentableItems.append(rentableItem)
            log.LogInfo('RentableItem:', rentableItem)

        self.rentableItems.sort(lambda x, y: -cmp(y.number, x.number))
        owners = []
        for each in self.rentableItems:
            if each.typeID != const.typeOfficeFolder:
                continue
            if each.rentedToID is not None and each.rentedToID not in owners:
                owners.append(each.rentedToID)

        if len(owners):
            cfg.eveowners.Prime(owners)



    def DisplayLogo(self):
        self.SetWndIcon()
        logo = uiutil.GetLogoIcon(itemID=session.corpid, name='logo', parent=self.sr.topParent, acceptNone=True, state=uiconst.UI_NORMAL, left=const.defaultPadding, align=uiconst.RELATIVE)
        logo.width = logo.height = 64



    def Load(self, args):
        self.InitializeList()
        if args == 'station_details':
            self.OnTabStationDetails()
        elif args == 'station_service_access_control':
            self.OnTabStationServiceAccessControl()
        elif args == 'cost_modifiers':
            self.OnTabCostModifiers()
        elif args == 'offices':
            self.OnTabOffices()
        elif args == 'clone_contracts':
            self.OnTabCloneContracts(-1)
        elif args == 'improvements':
            self.OnTabImprovements()



    def InitializeList(self):
        if self.ddxFunction is not None:
            try:
                log.LogInfo('Calling ddxFunction:', self.ddxFunction)
                self.ddxFunction()
                log.LogInfo('Called ddxFunction:', self.ddxFunction)

            finally:
                self.ddxFunction = None
                self.ddxArguments = {}




    def CheckBoxChange(self, checkbox):
        if checkbox.data['key'] == 'roles':
            roleID = checkbox.data['retval']
            if self.newRoles & roleID == roleID:
                self.newRoles = self.newRoles & ~roleID
            else:
                self.newRoles = self.newRoles | roleID
        elif checkbox.data['key'] == 'grantableroles':
            roleID = checkbox.data['retval']
            if self.newGrantableRoles & roleID == roleID:
                self.newGrantableRoles = self.newGrantableRoles & ~roleID
            else:
                self.newGrantableRoles = self.newGrantableRoles | roleID



    def OnTabStationDetails(self):
        scrolllist = []
        scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Station/StationManagment/StationDetails')}))
        orbitName = cfg.evelocations.Get(self.station.orbitID).name
        if self.station.stationName.startswith(orbitName):
            editName = self.station.stationName[(len(orbitName) + 3):]
        else:
            editName = self.station.stationName
        scrolllist.append(listentry.Get('Edit', {'label': localization.GetByLabel('UI/Station/StationManagment/Name'),
         'setValue': editName[:32],
         'name': 'details_name',
         'lines': 1,
         'maxLength': 32}))
        scrolllist.append(listentry.Get('TextEdit', {'label': localization.GetByLabel('UI/Common/Description'),
         'setValue': self.station.description,
         'name': 'details_description',
         'lines': 5,
         'maxLength': 5000,
         'killFocus': True}))
        scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
         'label': localization.GetByLabel('UI/Common/Security'),
         'text': self.station.security}))
        scrolllist.append(listentry.Get('Edit', {'label': localization.GetByLabel('UI/Station/StationManagment/DockingCostPerVolume'),
         'setValue': self.station.dockingCostPerVolume,
         'name': 'details_dockingCostPerVolume',
         'floatmode': (0.0, 1000.0)}))
        scrolllist.append(listentry.Get('Edit', {'label': localization.GetByLabel('UI/Station/StationManagment/OfficeRentalCost'),
         'setValue': self.station.officeRentalCost,
         'name': 'details_officeRentalCost',
         'intmode': (0, sys.maxint)}))
        exitTime = self.station.exitTime
        if exitTime is None:
            exitTime = 1200
        scrolllist.append(listentry.Get('Combo', {'options': self.GetHours(),
         'label': localization.GetByLabel('UI/Station/StationManagment/ReinforcedModeExitTime'),
         'cfgName': 'StationReinforcmentExitTimeCFG',
         'setValue': exitTime / 100,
         'OnChange': self.OnComboChange,
         'name': 'details_exitTime'}))
        maxshipvoldockable = localization.GetByLabel('UI/Station/StationManagment/MaxShipVolumeDockableAmount', maxshipvolume=util.FmtAmt(self.station.maxShipVolumeDockable), squaremeters=sm.GetService('info').FormatUnit(cfg.dgmattribs.Get(const.attributeVolume).unitID))
        scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
         'label': localization.GetByLabel('UI/Station/StationManagment/MaxShipVolumeDockable'),
         'text': maxshipvoldockable}))
        if self.IsServiceAvailable(const.stationServiceReprocessingPlant):
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/ReprocessingStationsTake'),
             'setValue': self.station.reprocessingStationsTake * 100,
             'name': 'details_reprocessingStationsTake',
             'floatmode': (0.0, 100.0)}))
            options = self.GetAvailableHangars()
            if len(options) == 0:
                scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Station/StationManagment/NoDivisionHangarsWarning')}))
            else:
                default = None
                if self.station.reprocessingHangarFlag is not None:
                    for (description, flag,) in options:
                        if self.station.reprocessingHangarFlag == flag:
                            default = flag
                            break

                data = {'options': options,
                 'label': localization.GetByLabel('UI/Station/StationManagment/ReprocessingOutput'),
                 'cfgName': 'reprocessingHangarFlag',
                 'setValue': default,
                 'OnChange': self.OnComboChange,
                 'name': 'reprocessingHangarFlag'}
                scrolllist.append(listentry.Get('Combo', data))
                if default is None:
                    self.station.reprocessingHangarFlag = options[0][1]
        if eve.session.allianceid:
            scrolllist.append(listentry.Get('Divider'))
            scrolllist.append(listentry.Get('Button', {'label': '',
             'caption': localization.GetByLabel('UI/Inflight/POS/TransferSovStructureOwnership'),
             'OnClick': self.TransferStation}))
        self.ddxFunction = self.DDXTabStationDetails
        self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)



    def GetHours(self):
        hours = []
        for i in xrange(24):
            text = ''
            if i < 10:
                text = '0%s:00' % i
            else:
                text = '%s:00' % i
            hours.append((text, i))

        return hours



    def TransferStation(self, *args):
        members = sm.GetService('alliance').GetMembers()
        owners = []
        for member in members.itervalues():
            if member.corporationID not in owners:
                owners.append(member.corporationID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        tmplist = []
        for member in members.itervalues():
            if self.station.ownerID != member.corporationID:
                tmplist.append((cfg.eveowners.Get(member.corporationID).ownerName, member.corporationID))

        ret = uix.ListWnd(tmplist, 'generic', localization.GetByLabel('UI/Corporations/Common/SelectCorporation'), None, 1)
        if ret is not None and len(ret):
            self.corpStationMgr.UpdateStationOwner(ret[1])
            self.CloseByUser()



    def DDXTabStationDetails(self):
        try:
            log.LogInfo('>>>DDXTabStationDetails')
            self.station.stationName = self.GetNodeValue('details_name')
            self.station.description = self.GetNodeValue('details_description')
            self.station.dockingCostPerVolume = self.GetNodeValue('details_dockingCostPerVolume')
            self.station.officeRentalCost = self.GetNodeValue('details_officeRentalCost')
            self.station.exitTime = self.GetNodeValue('details_exitTime') * 100
            if self.IsServiceAvailable(const.stationServiceReprocessingPlant):
                self.station.reprocessingStationsTake = self.GetNodeValue('details_reprocessingStationsTake') / 100

        finally:
            log.LogInfo('<<<DDXTabStationDetails')




    def GetAvailableHangars(self):
        options = []
        paramsByDivision = {1: (const.flagHangar, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
         2: (const.flagCorpSAG2, const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
         3: (const.flagCorpSAG3, const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
         4: (const.flagCorpSAG4, const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
         5: (const.flagCorpSAG5, const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
         6: (const.flagCorpSAG6, const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
         7: (const.flagCorpSAG7, const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
        divisions = sm.GetService('corp').GetDivisionNames()
        options = []
        i = 0
        while i < 7:
            i += 1
            param = paramsByDivision[i]
            hangarDescription = divisions[i]
            options.append((hangarDescription, param[0]))

        return options



    def OnComboChange(self, combo, header, value, *args):
        log.LogInfo('OnComboChange combo', combo)
        log.LogInfo('OnComboChange header', header)
        log.LogInfo('OnComboChange value', value)
        if combo.name == 'reprocessingHangarFlag':
            self.station.reprocessingHangarFlag = value



    def OnTabStationServiceAccessControl(self):
        scrolllist = []
        if session.allianceid is not None:
            data = util.KeyVal()
            data.label = localization.GetByLabel('UI/Station/StationManagment/UseAllianceStandings')
            data.cfgname = 'useAllianceStandings'
            data.checked = session.allianceid is not None and session.allianceid == self.station.standingOwnerID
            data.retval = None
            data.OnChange = self.StandingOwnerCheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))
        for (serviceID, service,) in self.servicesByID.iteritems():
            serviceAccess = localization.GetByLabel('UI/Station/StationManagment/AccessControlForService', servicename=self.GetServiceName(service))
            scrolllist.append(listentry.Get('Header', {'label': serviceAccess}))
            rule = self.serviceAccessRulesByServiceID[serviceID]
            log.LogInfo(service.serviceName, rule)
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/MinimumStanding'),
             'setValue': rule.minimumStanding,
             'name': '%smods_minimumStanding' % serviceID,
             'floatmode': (-10.0, 10.0)}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/MinimumCharacterSecurity'),
             'setValue': rule.minimumCharSecurity,
             'name': '%smods_minimumCharSecurity' % serviceID,
             'floatmode': (-10.0, 10.0)}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/MaximumCharacterSecurity'),
             'setValue': rule.maximumCharSecurity,
             'name': '%smods_maximumCharSecurity' % serviceID,
             'floatmode': (-10.0, 10.0)}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/MinimumCorporationSecurity'),
             'setValue': rule.minimumCorpSecurity,
             'name': '%smods_minimumCorpSecurity' % serviceID,
             'floatmode': (-10.0, 10.0)}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/MaximumCorporationSecurity'),
             'setValue': rule.maximumCorpSecurity,
             'name': '%smods_maximumCorpSecurity' % serviceID,
             'floatmode': (-10.0, 10.0)}))

        self.ddxArguments = {}
        self.ddxFunction = self.DDXTabStationServiceAccessControl
        self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)



    def StandingOwnerCheckBoxChange(self, checkbox):
        if checkbox.checked:
            self.station.standingOwnerID = session.allianceid
        else:
            self.station.standingOwnerID = session.corpid



    def GetEntryDataByName(self, name):
        entries = self.sr.scroll.GetNodes() + self.sr.scroll2.GetNodes()
        for entry in entries:
            if entry.name == name:
                return entry




    def FindNode(self, nodeName):
        entries = self.sr.scroll.GetNodes() + self.sr.scroll2.GetNodes()
        for entry in entries:
            if entry.name == nodeName:
                return entry




    def GetNodeValue(self, nodeName):
        node = self.FindNode(nodeName)
        if node is not None:
            return node.setValue
        raise RuntimeError('ChildNotFound', nodeName)



    def DDXTabStationServiceAccessControl(self):
        try:
            log.LogInfo('>>>DDXTabStationServiceAccessControl')
            for (serviceID, service,) in self.servicesByID.iteritems():
                if not self.IsActiveService(serviceID):
                    continue
                log.LogInfo('>>>--', service.serviceName, '--<<<')
                rule = self.serviceAccessRulesByServiceID[serviceID]
                minimumStanding = self.GetNodeValue('%smods_minimumStanding' % serviceID)
                minimumCharSecurity = self.GetNodeValue('%smods_minimumCharSecurity' % serviceID)
                maximumCharSecurity = self.GetNodeValue('%smods_maximumCharSecurity' % serviceID)
                minimumCorpSecurity = self.GetNodeValue('%smods_minimumCorpSecurity' % serviceID)
                maximumCorpSecurity = self.GetNodeValue('%smods_maximumCorpSecurity' % serviceID)
                if rule.minimumStanding == minimumStanding and rule.minimumCharSecurity == minimumCharSecurity and rule.maximumCharSecurity == maximumCharSecurity and rule.minimumCorpSecurity == minimumCorpSecurity and rule.maximumCorpSecurity == maximumCorpSecurity:
                    continue
                log.LogInfo('!!!--', service.serviceName, ' has modified data--!!!')
                rule.minimumStanding = minimumStanding
                rule.minimumCharSecurity = minimumCharSecurity
                rule.maximumCharSecurity = maximumCharSecurity
                rule.minimumCorpSecurity = minimumCorpSecurity
                rule.maximumCorpSecurity = maximumCorpSecurity
                self.modifiedServiceAccessRulesByServiceID[serviceID] = rule


        finally:
            log.LogInfo('<<<DDXTabStationServiceAccessControl')




    def OnTabCostModifiers(self):
        scrolllist = []
        scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Station/StationManagment/CostModifiers')}))
        scrolllist.append(listentry.Get('Text', {'text': localization.GetByLabel('UI/Station/StationManagment/CostModifiersHint')}))
        for row in self.serviceCostModifiers:
            if not self.IsServiceAvailable(row.serviceID):
                continue
            if not self.IsActiveService(row.serviceID):
                continue
            taskname = self.GetServiceName(self.servicesByID[row.serviceID])
            scrolllist.append(listentry.Get('Divider'))
            scrolllist.append(listentry.Get('Subheader', {'label': taskname}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/GoodStandingDiscount'),
             'setValue': row.discountPerGoodStandingPoint,
             'name': 'cost_%s_discountPerGoodStandingPoint' % taskname,
             'floatmode': (0.0, 10.0)}))
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': localization.GetByLabel('UI/Station/StationManagment/BadStandingSurcharge'),
             'setValue': row.surchargePerBadStandingPoint,
             'name': 'cost_%s_surchargePerBadStandingPoint' % taskname,
             'floatmode': (0.0, 10.0)}))

        self.ddxFunction = self.DDXTabCostModifiers
        self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)



    def DDXTabCostModifiers(self):
        try:
            log.LogInfo('>>>DDXTabCostModifiers')
            for row in self.serviceCostModifiers:
                if not self.IsServiceAvailable(row.serviceID):
                    continue
                if not self.IsActiveService(row.serviceID):
                    continue
                taskname = self.GetServiceName(self.servicesByID[row.serviceID])
                discountPerGoodStandingPoint = float(self.GetEntryDataByName('cost_%s_discountPerGoodStandingPoint' % taskname).setValue)
                surchargePerBadStandingPoint = float(self.GetEntryDataByName('cost_%s_surchargePerBadStandingPoint' % taskname).setValue)
                if discountPerGoodStandingPoint == row.discountPerGoodStandingPoint and surchargePerBadStandingPoint == row.surchargePerBadStandingPoint:
                    continue
                row.discountPerGoodStandingPoint = discountPerGoodStandingPoint
                row.surchargePerBadStandingPoint = surchargePerBadStandingPoint
                bFound = 0
                for each in self.modifiedServiceCostModifiers:
                    if each.serviceID == row.serviceID:
                        bFound = 1
                        each.discountPerGoodStandingPoint = discountPerGoodStandingPoint
                        each.surchargePerBadStandingPoint = surchargePerBadStandingPoint
                        break

                if not bFound:
                    self.modifiedServiceCostModifiers.append(row)


        finally:
            log.LogInfo('<<<DDXTabCostModifiers')




    def OnTabOffices(self):
        scrolllist = []
        scrollHeaders = [localization.GetByLabel('UI/Corporations/Common/Offices'),
         localization.GetByLabel('UI/Station/OfficeNumber'),
         localization.GetByLabel('UI/Station/StationManagment/OfficeRentedBy'),
         localization.GetByLabel('UI/Station/StationManagment/RentStartDate'),
         localization.GetByLabel('UI/Station/StationManagment/RentPeriod'),
         localization.GetByLabel('UI/Station/StationManagment/RentPeriodCost'),
         localization.GetByLabel('UI/Station/StationManagment/RentBalanceDue')]
        for each in self.rentableItems:
            if each.typeID == const.typeOfficeFolder:
                pass
            else:
                log.LogError('Unknown typeID on Corporation Folder %s (typeID) %s (CorpID)' % each.typeID, eve.session.corpid)
                continue
            rname = ''
            if each.rentedToID is not None:
                rname = localization.GetByLabel('UI/Station/StationManagment/OfficesTableRentedBy', rentername=cfg.eveowners.Get(each.rentedToID).name)
            dataLabel = '<t>'.join([localization.GetByLabel('UI/Station/StationManagment/OfficesTablePubliclyAvailable'),
             util.FmtAmt(each.number),
             rname,
             util.FmtDate(each.startDate, 'ln') if each.startDate else u'',
             util.FmtAmt(each.rentPeriodInDays) if each.rentPeriodInDays else u'',
             util.FmtISK(each.periodCost) if each.periodCost else u'',
             util.FmtDate(each.balanceDueDate, 'ln') if each.balanceDueDate else u''])
            data = {'label': dataLabel,
             'checked': each.publiclyAvailable,
             'cfgname': 'offices',
             'retval': 'type%s_number%s' % (each.typeID, each.number),
             'OnChange': self.CheckBoxChange,
             'name': 'offices_type%s_number%s' % (each.typeID, each.number)}
            scrolllist.append(listentry.Get('Checkbox', data))

        self.ddxFunction = self.DDXTabOffices
        self.sr.scroll2.Load(fixedEntryHeight=24, contentList=scrolllist, headers=scrollHeaders)



    def DDXTabOffices(self):
        try:
            log.LogInfo('>>>DDXTabOffices')
            for each in self.rentableItems:
                if each.typeID == const.typeOfficeFolder:
                    pass
                else:
                    log.LogError('Unknown typeID on Corporation Folder %s (typeID) %s (CorpID)' % each.typeID, eve.session.corpid)
                    continue
                publiclyAvailable = self.GetEntryDataByName('offices_type%s_number%s' % (each.typeID, each.number)).checked
                if each.publiclyAvailable == publiclyAvailable:
                    continue
                each.publiclyAvailable = publiclyAvailable
                bFound = 0
                for row in self.modifiedRentableItems:
                    if row.typeID == each.typeID and row.number == each.number:
                        bFound = 1
                        row.publiclyAvailable = publiclyAvailable
                        break

                if not bFound:
                    self.modifiedRentableItems.append(each)


        finally:
            log.LogInfo('<<<DDXTabOffices')




    def OnTabCloneContracts(self, corpID, *args):
        self.InitializeList()
        scrolllist = []
        cloneContracts = [ cloneContract for cloneContract in self.corpStationMgr.GetOwnerIDsOfClonesAtStation(corpID) ]
        if corpID == -1:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Station/StationManagment/CloneContractsByCorporation')}))
            cloneContracts.sort(lambda a, b: cmp(cfg.eveowners.Get(a.corporationID).ownerName, cfg.eveowners.Get(b.corporationID).ownerName))
            for cloneContract in cloneContracts:
                scrolllist.append(listentry.Get('Divider'))
                scrolllist.append(listentry.Get('Subheader', {'label': cfg.eveowners.Get(cloneContract.corporationID).ownerName}))
                scrolllist.append(listentry.Get('Button', {'label': localization.GetByLabel('UI/Station/StationManagment/RevokeCloneContractsHint'),
                 'caption': localization.GetByLabel('UI/Station/StationManagment/RevokeCloneContractsButton'),
                 'OnClick': self.RevokeCloneContractsAtStation,
                 'args': (corpID, cloneContract.corporationID, -1)}))
                scrolllist.append(listentry.Get('Button', {'label': localization.GetByLabel('UI/Station/StationManagment/ExpandCloneContractsHint'),
                 'caption': localization.GetByLabel('UI/Station/StationManagment/ExpandCloneContractsButton'),
                 'OnClick': self.OnTabCloneContracts,
                 'args': (cloneContract.corporationID,)}))

        else:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Station/StationManagment/CloneContractsForCorporation', corporationname=cfg.eveowners.Get(corpID).ownerName)}))
            scrolllist.append(listentry.Get('Button', {'label': localization.GetByLabel('UI/Station/StationManagment/ReturnToPreviousCloneContracts'),
             'caption': localization.GetByLabel('UI/Commands/Back'),
             'OnClick': self.OnTabCloneContracts,
             'args': (-1,)}))
            cloneContracts.sort(lambda a, b: cmp(cfg.eveowners.Get(a.characterID).ownerName, cfg.eveowners.Get(b.characterID).ownerName))
            for cloneContract in cloneContracts:
                scrolllist.append(listentry.Get('Divider'))
                scrolllist.append(listentry.Get('Subheader', {'label': cfg.eveowners.Get(cloneContract.characterID).ownerName}))
                scrolllist.append(listentry.Get('Button', {'label': localization.GetByLabel('UI/Station/StationManagment/RevokeCloneContractsHint'),
                 'caption': localization.GetByLabel('UI/Station/StationManagment/RevokeCloneContractsButton'),
                 'OnClick': self.RevokeCloneContractsAtStation,
                 'args': (corpID, corpID, cloneContract.characterID)}))

        if self and self and not self.destroyed:
            self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)



    def GetRemoteImprovementTiers(self):
        outpostData = self.GetOutpostData()
        isd = sm.RemoteSvc('corpStationMgr').GetImprovementStaticData()
        outpostRaceID = cfg.invtypes.Get(outpostData.typeID).raceID
        outpostAsmLines = set([ each.assemblyLineTypeID for each in sm.ProxySvc('ramProxy').AssemblyLinesGet(eve.session.stationid) ])

        def IndexBenefitRowset(rowset):
            ret = {}
            for row in rowset:
                ret.setdefault(row.improvementTypeID, []).append(row)

            return ret



        def MakeImprovement(imp):
            return uiutil.Bunch(typeID=imp.typeID, requiredImprovementTypeID=imp.requiredImprovementTypeID)


        available = [ MakeImprovement(imp) for imp in isd.improvementTypes if imp.raceID == outpostRaceID and imp.requiredAssemblyLineTypeID is None or imp.requiredAssemblyLineTypeID in outpostAsmLines ]
        byReq = {}
        for imp in available:
            byReq.setdefault(imp.requiredImprovementTypeID, []).append(imp)

        branches = []
        for imp in byReq.get(None, []):
            branch = []
            while True:
                branch.append(imp)
                if imp.typeID not in byReq:
                    break
                imp = byReq[imp.typeID][0]

            branches.append(branch)

        nTiers = max([ len(branch) for branch in branches ])
        tiers = []
        for i in xrange(nTiers):
            improvements = []
            for branch in branches:
                if len(branch) > i:
                    improvements.append(branch[i])
                else:
                    improvements.append(None)

            tiers.append(uiutil.Bunch(improvements=improvements))

        return tiers



    def GetRemoteInstalledImprovements(self):
        s = self.corpStationMgr.GetStationImprovements()
        improvLst = [s.improvementTier1aTypeID,
         s.improvementTier2aTypeID,
         s.improvementTier3aTypeID,
         s.improvementTier1bTypeID,
         s.improvementTier2bTypeID,
         s.improvementTier1cTypeID]
        return set(filter(None, improvLst))



    def GetOutpostData(self):
        return uiutil.Bunch(itemID=eve.session.stationid, typeID=eve.stationItem.stationTypeID, upgradeLevel=self.station.upgradeLevel)



    def ShouldDisplayImprovements(self):
        return eve.stationItem.stationTypeID not in (12242, 12294, 12295)



    def GetBenefitStrings(self, impr):
        ret = []
        for (benefitLst, GetStr,) in [(impr.typeBenefits, self.GetTypeBenefitStr),
         (impr.quantityBenefits, self.GetQuantityBenefitStr),
         (impr.typeQuantityBenefits, self.GetTypeQuantityBenefitStr),
         (impr.reprEffBenefits, self.GetReprEffBenefitStr),
         (impr.officeSlotBenefits, self.GetOfficeSlotsBenefitStr),
         (impr.serviceBenefits, self.GetServicesBenefitStr)]:
            ret.extend(map(GetStr, benefitLst))

        return ret



    def OnTabImprovements(self, *args):
        tiers = self.GetRemoteImprovementTiers()
        installed = self.GetRemoteInstalledImprovements()
        for tier in tiers:
            for improvement in filter(None, tier.improvements):
                improvement.installed = improvement.typeID in installed
                if improvement.installed:
                    statusHint = localization.GetByLabel('UI/Station/StationManagment/ImprovementInstalled')
                else:
                    statusHint = localization.GetByLabel('UI/Station/StationManagment/ImprovementNotInstalled')
                improvementType = util.ImprovementTypeResolver.GetImprovementTypeName(improvement.typeID)
                description = util.ImprovementTypeResolver.GetImprovementTypeDescription(improvement.typeID)
                improvement.hint = localization.GetByLabel('UI/Station/StationManagment/ImprovementHint', type=improvementType, statusHint=statusHint, description=description)


        outpostData = self.GetOutpostData()
        forkData = uiutil.Bunch()
        for data in (outpostData, forkData):
            data.nBranches = len(tiers[0].improvements)

        scrolllist = []
        scrolllist.append(listentry.Get('OutpostImprovementsHeader', data=outpostData))
        scrolllist.append(listentry.Get('OutpostImprovementsFork', data=forkData))
        for (i, tier,) in enumerate(tiers):
            tier.tier = i + 1
            scrolllist.append(listentry.Get('OutpostImprovementTierLines', data=tier))
            scrolllist.append(listentry.Get('OutpostImprovementTierIcons', data=tier.Copy()))

        scrolllist.append(listentry.Get('Empty', data=util.KeyVal(height=30)))
        self.sr.scroll.Load(contentList=scrolllist)



    def RevokeCloneContractsAtStation(self, viewCorpID, corpID, charID, *args):
        self.corpStationMgr.RevokeCloneContractsAtStation(corpID, charID)
        self.OnTabCloneContracts(viewCorpID)



    def OnOK(self, *args):
        if self.ddxFunction:
            self.ddxFunction()
        if self.station.stationName == '':
            eve.Message('StationNameEmpty')
        if self.station.officeRentalCost < 1:
            eve.Message('OfficeRentalCostMustBePositive')
        else:
            self.UpdateData()
            self.CloseByUser()



    def OnCancel(self, *args):
        self.CloseByUser()



    def UpdateData(self):
        self.corpStationMgr.UpdateStationManagementSettings(self.modifiedServiceAccessRulesByServiceID, self.modifiedServiceCostModifiers, self.modifiedRentableItems, self.station.stationName, self.station.description, self.station.dockingCostPerVolume, self.station.officeRentalCost, self.station.reprocessingStationsTake, self.station.reprocessingHangarFlag, self.station.exitTime, self.station.standingOwnerID)
        sm.GetService('objectCaching').InvalidateCachedMethodCall('stationSvc', 'GetStation', session.stationid)



    def IsActiveService(self, serviceID):
        isActive = True
        if const.stationServiceFactory == const.stationServiceFactory & serviceID:
            isActive = False
        if const.stationServiceLaboratory == const.stationServiceLaboratory & serviceID:
            isActive = False
        return isActive




class StationManagement():
    __guid__ = 'form.StationManagement'

    def Startup(self):
        wnd = form.StationManagementDialog.GetIfOpen()
        if wnd:
            wnd.Maximize()
            return 
        if not const.corpRoleStationManager & eve.session.corprole == const.corpRoleStationManager:
            eve.Message('StationMgtStartupInfo1')
            return 
        if not eve.session.stationid:
            eve.Message('StationMgtStartupInfo2')
            return 
        corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        if not sm.GetService('corp').DoesCharactersCorpOwnThisStation():
            eve.Message('StationMgtStartupInfo3')
            return 
        form.StationManagementDialog.Open()




class ImprovementsMetrics():
    __guid__ = 'util.ImprovementsMetrics'
    center = 220
    iconMargin = 15
    iconSize = 64
    lineThickness = 4
    trunkThickness = 10
    firstLineHeight = 12
    restLinesHeight = 80
    lineAlpha = 0.7
    iconToLine = (iconSize - lineThickness) // 2
    betweenLines = iconMargin + 2 * iconToLine
    for each in (iconSize, lineThickness, trunkThickness):
        pass


    def Width(cls, nBranches):
        return (cls.iconSize + cls.iconMargin) * nBranches - cls.iconMargin


    Width = classmethod(Width)

    def LeftMargin(cls, nBranches):
        return cls.center - cls.Width(nBranches) // 2


    LeftMargin = classmethod(LeftMargin)


class ImprovementsHeaderEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OutpostImprovementsHeader'

    def Startup(self, *etc):
        self.sr.infoIcon = uicls.Icon(hint=localization.GetByLabel('UI/Common/ShowInfo'), parent=self, name='infoIcon', icon='ui_38_16_208', size=16)
        self.sr.icon = uicls.Icon(parent=self, name='icon', size=96, top=40)
        self.sr.upgradeLevelHeader = uicls.EveHeaderLarge(parent=self, name='upgradeLevelHeader', state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Station/StationManagment/OutpostUpgradeLevel'), bold=True, left=20, top=10)
        self.sr.upgradeLevelLabel = uicls.Label(parent=self, name='upgradeLevelLabel', state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Station/StationManagment/OutpostUpgradeLevel'), bold=True, fontsize=60, top=25)
        self.sr.trunk = uicls.Fill(parent=self, align=uiconst.RELATIVE, name='trunk')
        self.sr.trunk.width = util.ImprovementsMetrics.trunkThickness
        self.sr.trunk.color.a = util.ImprovementsMetrics.lineAlpha



    def Load(self, data):
        im = util.ImprovementsMetrics
        header = self.sr.upgradeLevelHeader
        label = self.sr.upgradeLevelLabel
        icon = self.sr.icon
        info = self.sr.infoIcon
        trunk = self.sr.trunk
        label.text = localizationUtil.FormatNumeric(data.upgradeLevel, decimalPlaces=0)
        label.left = header.left + (header.width - label.width) // 2
        icon.left = im.center - icon.width // 2
        icon.LoadIconByTypeID(data.typeID, ignoreSize=True)
        icon.SetSize(96, 96)
        info.top = icon.top + 2
        info.left = icon.left + icon.width - info.width - 2
        info.OnClick = (uix.ShowInfo, data.typeID, data.itemID)
        trunk.left = im.center - im.trunkThickness // 2
        trunk.top = icon.top + icon.height // 2
        trunk.height = self.height - trunk.top



    def GetHeight(self, node, width):
        node.height = ImprovementsHeaderEntry.entryHeight
        return node.height


    entryHeight = 160


class ImprovementsForkEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OutpostImprovementsFork'

    def Startup(self, *etc):
        cont = uicls.Container(parent=self)
        self.sr.leftPush = uicls.Container(parent=cont, name='leftPush', align=uiconst.TOLEFT)
        self.sr.body = uicls.Fill(parent=cont, name='body', align=uiconst.TOLEFT)
        self.state = uiconst.UI_DISABLED
        self.sr.body.color.a = util.ImprovementsMetrics.lineAlpha



    def Load(self, data):
        im = util.ImprovementsMetrics
        self.sr.leftPush.width = im.LeftMargin(data.nBranches) + im.iconToLine
        self.sr.body.width = im.Width(data.nBranches) - 2 * im.iconToLine



    def GetHeight(self, node, width):
        node.height = util.ImprovementsMetrics.lineThickness
        return node.height




class ImprovementTierLinesEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OutpostImprovementTierLines'

    def Startup(self, *etc):
        self.state = uiconst.UI_DISABLED



    def AssureInited(self, data):
        if self.sr.Get('lines', False):
            return 
        self.sr.lines = []
        im = util.ImprovementsMetrics
        for blah in data.improvements:
            uicls.Container(parent=self, name='blank', align=uiconst.TOLEFT, width=im.betweenLines)
            line = uicls.Line(parent=self, name='line', align=uiconst.TOLEFT, weight=im.lineThickness)
            self.sr.lines.append(line)

        self.children[0].width = im.LeftMargin(len(self.sr.lines)) + im.iconToLine



    def Load(self, data):
        self.AssureInited(data)
        for (improvement, line,) in zip(data.improvements, self.sr.lines):
            if improvement is None:
                line.color.a = 0.0
            else:
                line.color.a = util.ImprovementsMetrics.lineAlpha - 0.25 * (data.tier - 1)




    def GetHeight(self, node, width):
        if node.tier == 1:
            node.height = util.ImprovementsMetrics.firstLineHeight
        else:
            node.height = util.ImprovementsMetrics.restLinesHeight
        return node.height




class ImprovementTierIconsEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OutpostImprovementTierIcons'
    tierIcons = {'filled': {1: 145,
                2: 146,
                3: 147},
     'empty': {1: 161,
               2: 162,
               3: 163}}

    def Startup(self, *etc):
        self.state = uiconst.UI_PICKCHILDREN



    def AssureInited(self, data):
        if self.sr.Get('icons', False):
            return 
        self.sr.icons = []
        im = util.ImprovementsMetrics
        for blah in data.improvements:
            uicls.Container(parent=self, align=uiconst.TOLEFT, width=im.iconMargin, name='blank', state=uiconst.UI_DISABLED)
            icon = uicls.Container(parent=self, name='iconParent', align=uiconst.TOLEFT, width=im.iconSize)
            icon.sr.tier = uicls.Icon(parent=icon, name='tier', icon='ui_38_16_161', size=16, align=uiconst.TOPRIGHT, left=2, top=-2)
            icon.sr.icon = uicls.Icon(parent=icon, name='icon', align=uiconst.TOALL, hint=localization.GetByLabel('UI/Common/ShowInfo'), state=uiconst.UI_NORMAL)
            self.sr.icons.append(icon)

        self.children[0].width = im.LeftMargin(len(self.sr.icons))



    def Load(self, data):
        self.AssureInited(data)
        for (improvement, iconPar,) in zip(data.improvements, self.sr.icons):
            icon = iconPar.sr.icon
            tier = iconPar.sr.tier
            if improvement is None:
                icon.state = tier.state = uiconst.UI_HIDDEN
            else:
                icon.state = uiconst.UI_NORMAL
                tier.state = uiconst.UI_DISABLED
                util.ImprovementTypeResolver.SetImprovementTypeIcon(icon, improvement.typeID)
                icon.SetHint(improvement.hint)
                if improvement.installed:
                    icon.color.a = 1.0
                    tierFill = 'filled'
                else:
                    icon.color.a = 0.4
                    tierFill = 'empty'
                tier.LoadIcon('ui_38_16_%i' % self.tierIcons[tierFill][data.tier])




    def GetHeight(self, node, width):
        node.height = util.ImprovementsMetrics.iconSize
        return node.height




class EmptyEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Empty'

    def Startup(self, *etc):
        self.state = uiconst.UI_DISABLED



    def Load(self, data):
        self.height = data.height




class ImprovementTypeResolver():
    __guid__ = 'util.ImprovementTypeResolver'

    def GetImprovementTypeID(typeID):
        godmaType = sm.GetService('godma').GetType(typeID)
        return getattr(godmaType, 'stationTypeID', typeID)


    GetImprovementTypeID = staticmethod(GetImprovementTypeID)

    def GetImprovementTypeName(typeID):
        return cfg.invtypes.Get(util.ImprovementTypeResolver.GetImprovementTypeID(typeID)).typeName


    GetImprovementTypeName = staticmethod(GetImprovementTypeName)

    def GetImprovementTypeDescription(typeID):
        return cfg.invtypes.Get(util.ImprovementTypeResolver.GetImprovementTypeID(typeID)).description


    GetImprovementTypeDescription = staticmethod(GetImprovementTypeDescription)

    def SetImprovementTypeIcon(icon, typeID):
        stationTypeID = util.ImprovementTypeResolver.GetImprovementTypeID(typeID)
        icon.LoadIconByTypeID(stationTypeID)


    SetImprovementTypeIcon = staticmethod(SetImprovementTypeIcon)


