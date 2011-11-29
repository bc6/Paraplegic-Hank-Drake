import form
import listentry
import uix
import uiutil
import uthread
import util
import xtriui
import blue
import uiconst
import uicls
import log
import math
import contractutils
import localization
import fontConst
AREA_OF_OPERATIONS_GROUPID = 6
TIMEZONE_GROUPID = 8
PRIMARY_LANGUAGE_GROUPID = 10
LOOKING_FOR_GROUPID = 11
COMMITMENT_GROUPID = 12
AREA_NO_SPECIFIC_MASK = 68719476736L

class CorpRecruitment(uicls.Container):
    __guid__ = 'form.CorpRecruitment'
    __nonpersistvars__ = []
    DEFAULT_AREA_OF_OPERATIONS = {const.raceAmarr: 4096,
     const.raceCaldari: 8192,
     const.raceGallente: 16384,
     const.raceMinmatar: 32768}

    def init(self):
        self.corpSvc = sm.GetService('corp')



    def Load(self, args):
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.corpAdvertContainer = uicls.Container(parent=self, name='corpAdvertContainer', align=uiconst.TOALL, padding=const.defaultPadding * 2)
            self.corpAdvertContentContainer = uicls.Container(parent=self.corpAdvertContainer, align=uiconst.TOALL)
            self.applications = form.CorpApplications(name='applications', parent=self, align=uiconst.TOALL, padding=const.defaultPadding * 2)
            self.searchContainer = uicls.Container(parent=self, name='searchContainer', align=uiconst.TOALL, padding=const.defaultPadding * 2)
            tabs = []
            tabs.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdSearch'),
             self.searchContainer,
             self,
             'search'])
            if not util.IsNPC(session.corpid):
                tabs.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MyCorporationTab'),
                 self.corpAdvertContainer,
                 self,
                 'corp'])
            tabs.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorpApplicationsTab'),
             self.applications,
             self,
             'applications'])
            tabGroup = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            tabGroup.Startup(tabs, 'corporationrecruitment', UIIDPrefix='corporationRecruitmentTab')
            self.sr.tabs = tabGroup
        if args == 'corp':
            self.sr.viewingOwnerID = eve.session.corpid
            if not self.sr.Get('corpAdvertsInited', False):
                self.sr.corpAdvertsInited = True
                self.PopulateCorp()
        elif args == 'search':
            self.sr.viewingOwnerID = -1
            if not self.sr.Get('searchInited', False):
                self.sr.searchInited = True
                self.PopulateSearch()
        elif args == 'applications':
            self.sr.viewingOwnerID = -1
            if not self.sr.Get('applicationsInited', False):
                self.sr.applicationsInited = True
                self.PopulateApplications()
        sm.GetService('corpui').LoadTop('ui_7_64_8', localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentLabel'))



    def OnCorporationApplicationChanged(self, applicantID, corporationID, change):
        if hasattr(self, 'applications') and self.applications:
            self.applications.OnCorporationApplicationChanged(applicantID, corporationID, change)



    def GetRecruitmentAds(self, onlyMyCorpAds = False, typeMask = 0, isInAlliance = False, minMembers = 0, maxMembers = 0, *args):
        ads = []
        if eve.session.corpid and onlyMyCorpAds is True:
            ads = self.corpSvc.GetRecruitmentAdsForCorporation()
        else:
            ads = self.corpSvc.GetRecruitmentAdsByCriteria(typeMask, isInAlliance, minMembers, maxMembers)
            ads.sort(lambda i, j: cmp(self._GetCriteriaMatchPercentage(j.typeMask), self._GetCriteriaMatchPercentage(i.typeMask)))
            for ad1 in ads[-1]:
                for ad2 in ads[:]:
                    if ad1.corporationID != ad2.corporationID or ad1.adID == ad2.adID:
                        continue
                    if ad1 in ads:
                        ads.remove(ad1)


        ownersToPrime = []
        for ad in ads:
            if ad.corporationID:
                ownersToPrime.append(ad.corporationID)
            if ad.allianceID:
                ownersToPrime.append(ad.allianceID)

        if ownersToPrime:
            cfg.eveowners.Prime(ownersToPrime)
        return ads



    def _GetCriteriaMatchPercentage(self, adTypeMask):
        selectedTypesMask = settings.char.ui.Get('corporation_recruitment_types', 0)
        matchRating = 0
        optimalMatches = 0
        adMatches = 0
        if AREA_NO_SPECIFIC_MASK & selectedTypesMask:
            for adType in self.advertTypesByGroupID[AREA_OF_OPERATIONS_GROUPID]:
                if adTypeMask & adType.typeMask:
                    adTypeMask -= adType.typeMask
                if selectedTypesMask & adType.typeMask:
                    selectedTypesMask -= adType.typeMask

        for recruitmentType in self.advertTypes:
            if recruitmentType.typeMask & selectedTypesMask:
                optimalMatches += 2
            if recruitmentType.typeMask & adTypeMask != 0:
                adMatches += 1
            else:
                continue
            if recruitmentType.typeMask & adTypeMask & selectedTypesMask != 0:
                matchRating += 2
            else:
                matchRating -= 1

        ret = 0.0
        if optimalMatches != 0:
            ret = float(matchRating) / optimalMatches * 100
        elif adMatches > 0:
            ret = -(float(matchRating) / adMatches) * 100
        if ret < 0:
            ret = 0.0
        return round(ret, 2)



    def PopulateCorp(self, *args):
        if not hasattr(self, 'advertTypes'):
            self.advertTypes = self.corpSvc.GetRecruitmentAdTypes()
        if not hasattr(self, 'advertTypesByGroupID'):
            self.advertTypesByGroupID = self.advertTypes.Filter('groupID')
        if not hasattr(self, 'advertGroups'):
            self.advertGroups = self.corpSvc.GetRecruitmentAdGroups().Index('groupID')
        self.ShowCorpAdverts()



    def ShowCorpAdverts(self, *args):
        self.corpAdvertContentContainer.Show()
        self.PopulateCorpAdverts()
        adverts = self.GetRecruitmentAds(onlyMyCorpAds=True)
        scrolllist = self.GetAdvertScrollEntries(adverts, corpView=True)
        self.corpAdvertsScroll.Load(contentList=scrolllist)
        if len(adverts):
            self.corpAdvertsScroll.ShowHint(None)
        else:
            corpName = cfg.eveowners.Get(session.corpid).name
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorpHasNoRecruitmentAdvertisements', corpName=corpName)
            self.corpAdvertsScroll.ShowHint(hint)



    def PopulateApplications(self):
        self.applications.ShowCorporateApplications()
        self.applications.ShowMyApplications()
        if uiutil.IsVisible(self.applications.corpApplicationsContainer) and not self.applications.sr.personalScroll.GetNodes():
            self.applications.personalApplicationsContainer.Hide()
            self.applications.corpApplicationsContainer.SetAlign(uiconst.TOALL)
            self.applications.corpApplicationsContainer.height = 0
        if not uiutil.IsVisible(self.applications.corpApplicationsContainer):
            self.applications.personalApplicationsContainer.height = 0
            self.applications.personalApplicationsContainer.SetAlign(uiconst.TOALL)
        self.applications.Show()



    def PopulateSearch(self):
        searchTypes = settings.char.ui.Get('corporation_recruitment_types', None)
        if not hasattr(self, 'advertTypes'):
            self.advertTypes = self.corpSvc.GetRecruitmentAdTypes()
        if not hasattr(self, 'advertTypesByGroupID'):
            self.advertTypesByGroupID = self.advertTypes.Filter('groupID')
        if not hasattr(self, 'advertGroups'):
            self.advertGroups = self.corpSvc.GetRecruitmentAdGroups().Index('groupID')
        corpSearchOptionsContainer = uicls.Container(parent=self.searchContainer, name='corpSearchOptionsContainer', align=uiconst.TOLEFT, padRight=const.defaultPadding)
        corpSearchButton = uix.GetBigButton(where=corpSearchOptionsContainer, height=28)
        corpSearchButton.name = 'corpSearchButton'
        corpSearchButton.padTop = const.defaultPadding
        corpSearchButton.SetInCaption(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdSearch'))
        corpSearchButton.SetAlign(uiconst.TOBOTTOM)
        corpSearchButton.OnClick = self.SearchAdverts
        self.searchDetails = {}
        basicOptionsContainer = uicls.Container(parent=corpSearchOptionsContainer, name='basicOptionContainer', align=uiconst.TOPLEFT)
        searchLookingForLabel = self.CreateGroupLabel(basicOptionsContainer, LOOKING_FOR_GROUPID)
        searchLookingForButtonContainer = self.CreateGroupCheckboxContainer(basicOptionsContainer, LOOKING_FOR_GROUPID, searchTypes, callback=self.UpdateSearchDetails, top=searchLookingForLabel.top + searchLookingForLabel.height)
        searchCommitmentButtonContainer = self.CreateGroupCheckboxContainer(basicOptionsContainer, COMMITMENT_GROUPID, searchTypes, callback=self.UpdateSearchDetails, radioGroup=True, top=searchLookingForButtonContainer.top + searchLookingForButtonContainer.height + 2 * const.defaultPadding)
        searchTimeZoneLabel = self.CreateGroupLabel(basicOptionsContainer, TIMEZONE_GROUPID, top=searchCommitmentButtonContainer.top + searchCommitmentButtonContainer.height + const.defaultPadding * 2)
        selected = []
        tabs = []
        timezoneAds = self.advertTypesByGroupID[TIMEZONE_GROUPID]
        timezoneAds.sort(lambda i, j: cmp(i.typeMask, j.typeMask))
        for adType in timezoneAds:
            text = adType.typeName
            checked = False
            if searchTypes and searchTypes & adType.typeMask:
                checked = True
            tabs.append([text,
             None,
             self,
             adType.description,
             (TIMEZONE_GROUPID, adType.typeMask)])
            if checked:
                selected.append((TIMEZONE_GROUPID, adType.typeMask))

        timeZoneButtons = uicls.TimezonePicker(parent=basicOptionsContainer, align=uiconst.TOPLEFT, height=28, top=searchTimeZoneLabel.top + searchTimeZoneLabel.height + const.defaultPadding, multiSelect=True)
        timeZoneButtons.Startup(tabs, selectedArgs=selected)
        basicOptionsContainer.AutoFitToContent()
        corpSearchOptionsContainer.width = max(corpSearchOptionsContainer.width, basicOptionsContainer.width)
        maxComboWidth = 0
        self.advancedOptionsContainer = uicls.Container(parent=corpSearchOptionsContainer, name='advancedOptionsContainer', align=uiconst.TOPLEFT, top=basicOptionsContainer.top + basicOptionsContainer.height + const.defaultPadding)
        searchAreaLabel = self.CreateGroupLabel(self.advancedOptionsContainer, AREA_OF_OPERATIONS_GROUPID)
        self.searchAreaCombo = self.CreateGroupCombo(self.advancedOptionsContainer, AREA_OF_OPERATIONS_GROUPID, searchTypes, top=searchAreaLabel.top + searchAreaLabel.height, ignoreReplace=(AREA_NO_SPECIFIC_MASK, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AnyAreaOfOperations'), 0))
        maxComboWidth = max(self.searchAreaCombo.width, maxComboWidth)
        searchSizeLabel = uicls.EveLabelMedium(parent=self.advancedOptionsContainer, name='searchSizeLabel', text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorporationSize'), align=uiconst.TOPLEFT, top=self.searchAreaCombo.top + self.searchAreaCombo.height + 3 * const.defaultPadding, bold=True)
        searchSizeOptions = []
        selected = 0
        minMembers = settings.char.ui.Get('corporation_recruitment_minmembers', 0)
        maxMembers = settings.char.ui.Get('corporation_recruitment_maxmembers', 1000)
        for (description, data,) in [(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AnyCorporationSize'), (0, 6300)),
         ('0 - 10', (0, 10)),
         ('10 - 50', (10, 50)),
         ('50 - 100', (50, 100)),
         ('100 - 200', (100, 200)),
         ('200 - 500', (200, 500)),
         ('500 - 1000', (500, 1000)),
         ('1000+', (1000, 6300))]:
            searchSizeOptions.append((description, data))
            if data[0] == minMembers and data[1] == maxMembers:
                selected = data

        self.searchSizeCombo = uicls.Combo(parent=self.advancedOptionsContainer, options=searchSizeOptions, name='searchSizeCombo', adjustWidth=True, align=uiconst.TOPLEFT, top=searchSizeLabel.top + searchSizeLabel.height, select=selected)
        maxComboWidth = max(self.searchSizeCombo.width, maxComboWidth)
        searchLanguageLabel = self.CreateGroupLabel(self.advancedOptionsContainer, PRIMARY_LANGUAGE_GROUPID, top=self.searchSizeCombo.top + self.searchSizeCombo.height + 3 * const.defaultPadding)
        self.searchLanguageCombo = self.CreateGroupCombo(self.advancedOptionsContainer, PRIMARY_LANGUAGE_GROUPID, searchTypes, top=searchLanguageLabel.top + searchLanguageLabel.height)
        maxComboWidth = max(self.searchLanguageCombo.width, maxComboWidth)
        self.searchLanguageCombo.width = self.searchSizeCombo.width = self.searchAreaCombo.width = maxComboWidth
        self.inAllianceCheckbox = uicls.Checkbox(align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorpIsInAnAlliance'), parent=self.advancedOptionsContainer, checked=settings.char.ui.Get('corporation_recruitment_isinalliance', False), top=self.searchLanguageCombo.top + self.searchLanguageCombo.height + 2 * const.defaultPadding, wrapLabel=False)
        self.advancedOptionsContainer.AutoFitToContent()
        corpSearchOptionsContainer.width = max(corpSearchOptionsContainer.width, self.advancedOptionsContainer.width)
        corpSearchResultsContainer = uicls.Container(parent=self.searchContainer, name='corpSearchResultsContainer', align=uiconst.TOALL, padLeft=const.defaultPadding)
        self.corpSearchResultsScroll = uicls.Scroll(parent=corpSearchResultsContainer)
        self.corpSearchResultsScroll.ShowHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/SearchDefaultHint'))



    def PopulateCorpAdverts(self):
        self.corpAdvertContentContainer.Flush()
        corpAdvertButtonContainer = uicls.Container(parent=self.corpAdvertContentContainer, name='corpAdvertButtonContainer', align=uiconst.TOBOTTOM, padTop=const.defaultPadding)
        if self.HasAccess(session.corpid):
            buttons = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CreateRecruitmentAdButtonLabel'),
              self.PopulateCorpAdvertsClick,
              (None,),
              None]]
            buttons = uicls.ButtonGroup(btns=buttons, parent=corpAdvertButtonContainer, line=False)
            corpAdvertButtonContainer.height = buttons.height
            if len(self.GetRecruitmentAds(onlyMyCorpAds=True)) >= const.corporationMaxRecruitmentAds:
                btn = buttons.GetBtnByLabel(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CreateRecruitmentAdButtonLabel'))
                btn.Disable()
        self.corpAdvertsScroll = uicls.Scroll(parent=self.corpAdvertContentContainer)



    def PopulateCorpAdvertsClick(self, clickObj):
        self.PopulateCorpAdvertsEdit()



    def PopulateCorpAdvertsEdit(self, advertData = None):
        self.corpAdvertContentContainer.Flush()
        advertID = None
        typeData = None
        recruiters = []
        daysRemaining = 0
        if advertData:
            advertID = advertData.adID
            typeData = advertData.typeMask
            recruiters = self.corpSvc.GetRecruiters(advertData.corporationID, advertID)
            daysRemaining = int((advertData.expiryDateTime - advertData.createDateTime) / DAY)
        corpAdvertButtonContainer = uicls.Container(parent=self.corpAdvertContentContainer, name='corpAdvertButtonContainer', align=uiconst.TOBOTTOM)
        buttons = [[localization.GetByLabel('UI/Common/Buttons/Submit'),
          self.UpdateAdvert,
          (advertID,),
          None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.ShowCorpAdverts,
          (None,),
          None]]
        buttons = uicls.ButtonGroup(btns=buttons, parent=corpAdvertButtonContainer)
        corpAdvertButtonContainer.height = buttons.height
        corpAdvertEditContainer = uicls.Container(parent=self.corpAdvertContentContainer, name='corpAdvertEditContainer', align=uiconst.TOALL, padTop=const.defaultPadding)
        corpAdvertDetailsContainer = uicls.Container(parent=corpAdvertEditContainer, name='corpAdvertDetailsContainer', align=uiconst.TOBOTTOM, height=230, padBottom=const.defaultPadding * 2)
        self.advertDetails = {}
        advertDetailsCenter = uicls.Container(parent=corpAdvertDetailsContainer, name='advertDetailsCenter', align=uiconst.CENTERTOP, top=const.defaultPadding)
        advertAreaLabel = self.CreateGroupLabel(advertDetailsCenter, AREA_OF_OPERATIONS_GROUPID)
        self.advertAreaCombo = self.CreateGroupCombo(advertDetailsCenter, AREA_OF_OPERATIONS_GROUPID, typeData or self._GetDefaultAreaOfOperations(), top=advertAreaLabel.top + advertAreaLabel.height + const.defaultPadding)
        advertDetailsCenter.width = max(advertDetailsCenter.width, advertAreaLabel.width, self.advertAreaCombo.width)
        advertLanguageLabel = self.CreateGroupLabel(advertDetailsCenter, PRIMARY_LANGUAGE_GROUPID, top=self.advertAreaCombo.top + self.advertAreaCombo.height + 2 * const.defaultPadding)
        self.advertLanguageCombo = self.CreateGroupCombo(advertDetailsCenter, PRIMARY_LANGUAGE_GROUPID, typeData, top=advertLanguageLabel.top + advertLanguageLabel.height + const.defaultPadding)
        advertDetailsCenter.width = max(advertDetailsCenter.width, advertLanguageLabel.width, self.advertLanguageCombo.width)
        advertCommitmentLabel = self.CreateGroupLabel(advertDetailsCenter, COMMITMENT_GROUPID, top=self.advertLanguageCombo.top + self.advertLanguageCombo.height + 2 * const.defaultPadding)
        advertCommitmentButtonContainer = self.CreateGroupCheckboxContainer(advertDetailsCenter, COMMITMENT_GROUPID, typeData, callback=self.UpdateAdvertDetails, radioGroup=True, top=advertCommitmentLabel.top + advertCommitmentLabel.height)
        advertDetailsCenter.width = max(advertDetailsCenter.width, advertCommitmentLabel.width, advertCommitmentButtonContainer.width)
        advertDetailsCenter.height = advertCommitmentButtonContainer.top + advertCommitmentButtonContainer.height
        advertDetailsLeft = uicls.Container(parent=corpAdvertDetailsContainer, name='advertDetailsLeft', align=uiconst.CENTERTOP, top=const.defaultPadding)
        advertLookingForLabel = self.CreateGroupLabel(advertDetailsLeft, LOOKING_FOR_GROUPID)
        advertLookingForButtonContainer = self.CreateGroupCheckboxContainer(advertDetailsLeft, LOOKING_FOR_GROUPID, typeData, callback=self.UpdateAdvertDetails, top=advertLookingForLabel.top + advertLookingForLabel.height)
        advertDetailsLeft.width = max(advertDetailsLeft.width, advertLookingForLabel.width, advertLookingForButtonContainer.width)
        advertDetailsLeft.height = advertLookingForButtonContainer.top + advertLookingForButtonContainer.height
        advertDetailsRight = uicls.Container(parent=corpAdvertDetailsContainer, name='advertDetailsRight', align=uiconst.CENTERTOP, top=const.defaultPadding)
        advertTimeLabel = self.CreateGroupLabel(advertDetailsRight, TIMEZONE_GROUPID)
        selected = []
        tabs = []
        timezoneAds = self.advertTypesByGroupID[TIMEZONE_GROUPID]
        timezoneAds.sort(lambda i, j: cmp(i.typeMask, j.typeMask))
        for adType in timezoneAds:
            text = adType.typeName
            checked = False
            if typeData and typeData & adType.typeMask:
                checked = True
            tabs.append([text,
             None,
             self,
             adType.description,
             (TIMEZONE_GROUPID, adType.typeMask)])
            if checked:
                selected.append((TIMEZONE_GROUPID, adType.typeMask))

        timeZoneButtons = uicls.TimezonePicker(parent=advertDetailsRight, align=uiconst.TOPLEFT, height=28, top=advertTimeLabel.top + advertTimeLabel.height + const.defaultPadding, multiSelect=True)
        timeZoneButtons.Startup(tabs, selectedArgs=selected)
        advertDetailsRight.width = max(advertDetailsRight.width, advertTimeLabel.width, timeZoneButtons.width)
        if advertID:
            durationHeader = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDuration')
        else:
            durationHeader = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ExtendRecruitmentAdDuration')
        advertDurationLabel = uicls.EveHeaderMedium(parent=advertDetailsRight, name='advertDurationLabel', text=durationHeader, align=uiconst.TOPLEFT, top=timeZoneButtons.top + timeZoneButtons.height + 2 * const.defaultPadding)
        adLimitExceeded = len(self.GetRecruitmentAds(onlyMyCorpAds=True)) > const.corporationMaxRecruitmentAds
        adDurationExceeded = daysRemaining > const.corporationMaxRecruitmentAdDuration - const.corporationMinRecruitmentAdDuration
        if adLimitExceeded or adDurationExceeded:
            advertDurationLabel.height = 0
            advertDurationLabel.top -= 2 * const.defaultPadding
            advertDurationLabel.Hide()
        advertDurationButtonContainer = uicls.Container(parent=advertDetailsRight, name='advertDurationButtonContainer', align=uiconst.TOPLEFT, top=advertDurationLabel.height + advertDurationLabel.top)

        def AdvertPrice(days):
            amount = days * const.corporationAdvertisementDailyRate
            if not advertID:
                amount += const.corporationAdvertisementFlatFee
            return amount


        durationEntries = []
        if advertID:
            durationEntries = [[0, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdZeroDurationOption'), True]]
        durationEntries += [[const.corporationMinRecruitmentAdDuration, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDurationOptionWithPrice', adDuration=3 * DAY, adPrice=contractutils.FmtISKWithDescription(AdvertPrice(3), justDesc=True)), False],
         [7, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDurationOptionWithPrice', adDuration=7 * DAY, adPrice=contractutils.FmtISKWithDescription(AdvertPrice(7), justDesc=True)), False],
         [14, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDurationOptionWithPrice', adDuration=14 * DAY, adPrice=contractutils.FmtISKWithDescription(AdvertPrice(14), justDesc=True)), False if advertID else True],
         [const.corporationMaxRecruitmentAdDuration, localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentAdDurationOptionWithPrice', adDuration=28 * DAY, adPrice=contractutils.FmtISKWithDescription(AdvertPrice(28), justDesc=True)), False]]
        top = 0
        maxDurExtension = const.corporationMaxRecruitmentAdDuration - daysRemaining
        for (value, label, checked,) in durationEntries:
            if value and value > maxDurExtension:
                continue
            box = uicls.Checkbox(align=uiconst.TOPLEFT, text=label, top=top, parent=advertDurationButtonContainer, retval=value, checked=checked, groupname='Duration', callback=self.UpdateAdvertDetails, wrapLabel=False)
            top += box.height
            box.name = 'Duration'
            if checked:
                self.UpdateAdvertDetails(box)

        advertDurationButtonContainer.AutoFitToContent()
        advertDetailsRight.width = max(advertDetailsRight.width, advertDurationLabel.width, advertDurationButtonContainer.width)
        if adLimitExceeded or adDurationExceeded:
            advertDurationButtonContainer.height = 0
            advertDurationButtonContainer.Hide()
        advertDetailsRight.height = advertDurationButtonContainer.top + advertDurationButtonContainer.height
        width = max(advertDetailsLeft.width, advertDetailsRight.width, advertDetailsCenter.width)
        advertDetailsLeft.width = advertDetailsRight.width = advertDetailsCenter.width = width
        advertDetailsLeft.left = advertDetailsCenter.left - advertDetailsCenter.width - const.defaultPadding * 3
        advertDetailsRight.left = advertDetailsCenter.left + advertDetailsCenter.width + const.defaultPadding * 3
        parentWindow = uiutil.GetWindowAbove(self)
        parentWindow.SetMinSize((max(parentWindow.minsize[0], width * 3 + const.defaultPadding * 12), parentWindow.minsize[1]))
        self.corpMembers = self.corpSvc.GetMemberIDs()
        self.contactsList = []
        contactsContainer = uicls.Container(parent=corpAdvertEditContainer, name='contactsContainer', height=230, align=uiconst.TOBOTTOM, padBottom=const.defaultPadding * 2)
        channelOptions = [(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoneRecruitmentChannelSelection'), 0)]
        selected = None
        lsc = sm.GetService('LSC')
        for channel in lsc.GetChannels():
            if channel.channelID and type(channel.channelID) is int and (channel.channelID < 0 or channel.channelID > 2100000000) and lsc.IsOperator(channel.channelID, session.charid):
                channelOptions.append((channel.displayName, channel.channelID))

        advertChannelLabel = uicls.EveLabelMedium(parent=contactsContainer, name='advertChannelLabel', align=uiconst.BOTTOMLEFT, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentChannelHeader'))
        if advertData:
            selected = advertData.channelID
        self.advertChannelCombo = uicls.Combo(parent=contactsContainer, options=channelOptions, name='advertChannelCombo', select=selected, adjustWidth=True, align=uiconst.BOTTOMLEFT, left=advertChannelLabel.width + const.defaultPadding)
        advertContactSelectionContainer = uicls.Container(parent=contactsContainer, name='advertContactSelectionContainer', align=uiconst.TOLEFT, width=175, padTop=const.defaultPadding, padBottom=self.advertChannelCombo.height + const.defaultPadding * 2)
        self.contactsFilter = uicls.SinglelineEdit(parent=advertContactSelectionContainer, name='contactsFilter', align=uiconst.TOTOP, maxLength=10, OnInsert=self.FilterOnInsert, hinttext=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/FilterRecruiterCandidates'))
        advertAddContactButton = uicls.Button(parent=advertContactSelectionContainer, name='advertAddContactButton', align=uiconst.CENTERBOTTOM, func=self.AddContactClick, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AddRecruiterToAd'))
        scrollList = []
        cfg.eveowners.Prime(self.corpMembers)
        for member in self.corpMembers:
            data = util.KeyVal()
            data.charID = member
            data.OnDblClick = self.OnContactDoubleClick
            scrollList.append(listentry.Get('User', data=data))

        self.corpMemberPickerScroll = uicls.Scroll(parent=advertContactSelectionContainer, padTop=const.defaultPadding, padBottom=advertAddContactButton.height + const.defaultPadding)
        self.corpMemberPickerScroll.Load(contentList=scrollList)
        self.contactContainers = {}
        for i in xrange(0, 6):
            self.contactContainers[i] = uicls.ContactContainer(parent=contactsContainer, align=uiconst.TOPLEFT, pos=(advertContactSelectionContainer.width + 4 * const.defaultPadding,
             2 * const.defaultPadding,
             160,
             46), removeFunc=self.RemoveContact, addCallback=self.AddContactCallback, state=uiconst.UI_NORMAL, corpMembers=self.corpMembers)

        self.contactContainers[1].top = self.contactContainers[0].top + self.contactContainers[0].height + 4 * const.defaultPadding
        self.contactContainers[2].top = self.contactContainers[1].top + self.contactContainers[1].height + 4 * const.defaultPadding
        self.contactContainers[4].top = self.contactContainers[3].top + self.contactContainers[3].height + 4 * const.defaultPadding
        self.contactContainers[5].top = self.contactContainers[4].top + self.contactContainers[4].height + 4 * const.defaultPadding
        self.contactContainers[3].left = self.contactContainers[0].left + self.contactContainers[0].width + 4 * const.defaultPadding
        self.contactContainers[4].left = self.contactContainers[1].left + self.contactContainers[1].width + 4 * const.defaultPadding
        self.contactContainers[5].left = self.contactContainers[2].left + self.contactContainers[2].width + 4 * const.defaultPadding
        for contact in recruiters:
            self.AddContact(contact)

        corpAdvertDetailsContainer.height = max(corpAdvertDetailsContainer.height, contactsContainer.height)
        contactsContainer.height = corpAdvertDetailsContainer.height
        tabs = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditDetails'),
          corpAdvertDetailsContainer,
          self,
          'details'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRecruiters'),
          contactsContainer,
          self,
          'recruiters']]
        tabGroup = uicls.TabGroup(name='corpAdEditTabGroup', parent=corpAdvertEditContainer, align=uiconst.TOBOTTOM, padTop=const.defaultPadding)
        tabGroup.Startup(tabs)
        corpTitleLabel = uicls.EveLabelMedium(parent=corpAdvertEditContainer, align=uiconst.TOPLEFT, name='corpTitleLabel', text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditTitle'))
        self.corpTitleEdit = uicls.SinglelineEdit(parent=corpAdvertEditContainer, name='corpTitleEdit', align=uiconst.TOTOP, top=corpTitleLabel.top + corpTitleLabel.height, maxLength=40)
        if advertData:
            self.corpTitleEdit.SetValue(advertData.title)
        corpMessageLabel = uicls.EveLabelMedium(parent=corpAdvertEditContainer, align=uiconst.TOPLEFT, name='corpMessageLabel', top=self.corpTitleEdit.top + self.corpTitleEdit.height + const.defaultPadding, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEditMessage'))
        self.corpMessageEdit = uicls.EditPlainText(parent=corpAdvertEditContainer, align=uiconst.TOALL, name='corpMessageEdit', top=corpMessageLabel.height + const.defaultPadding, maxLength=1000)
        if advertData:
            self.corpMessageEdit.SetValue(advertData.description)



    def _GetDefaultAreaOfOperations(self):
        return self.DEFAULT_AREA_OF_OPERATIONS[session.raceID]



    def FilterOnInsert(self, *args):
        scrollList = []
        for member in self.corpMembers:
            if member not in self.contactsList and self.contactsFilter.GetValue().lower() in cfg.eveowners.Get(member).name.lower():
                data = util.KeyVal()
                data.charID = member
                data.OnDblClick = self.OnContactDoubleClick
                scrollList.append(listentry.Get('User', data=data))

        self.corpMemberPickerScroll.Load(contentList=scrollList)



    def AddContactClick(self, *args):
        selected = self.corpMemberPickerScroll.GetSelected()
        if len(selected) and len(self.contactsList) < 6:
            for item in selected:
                self.AddContact(item.itemID)




    def OnContactDoubleClick(self, entry, *args):
        self.AddContact(entry.sr.node.itemID)



    def AddContact(self, charID):
        for container in self.contactContainers.values():
            if not container.IsSet():
                container.Set(charID)
                break




    def AddContactCallback(self, callbackObj, charID):
        if charID in self.contactsList:
            callbackObj.Clear()
        else:
            self.contactsList.append(charID)
            self.FilterOnInsert()



    def RemoveContact(self, charID):
        for container in self.contactContainers.values():
            if container.IsSet() == charID:
                container.Clear()
                self.contactsList.remove(charID)
                self.FilterOnInsert()




    def CreateGroupLabel(self, parent, groupID, top = 0):
        label = uicls.EveLabelMedium(parent=parent, name='groupLabel_' + self.advertGroups[groupID].groupName, align=uiconst.TOPLEFT, text=self.advertGroups[groupID].groupName, top=top, hint=self.advertGroups[groupID].description, state=uiconst.UI_NORMAL, bold=True)
        return label



    def CreateGroupCheckboxContainer(self, parent, groupID, typeData, callback = None, top = 0, radioGroup = False):
        container = uicls.Container(parent=parent, name='groupCheckbox_' + self.advertGroups[groupID].groupName, align=uiconst.TOPLEFT, top=top)
        radioGroupName = None
        if radioGroup:
            radioGroupName = self.advertGroups[groupID].groupName
        top = 0
        selected = None
        firstEntry = None
        for adType in self.advertTypesByGroupID[groupID]:
            text = adType.typeName
            checked = False
            if typeData and typeData & adType.typeMask:
                checked = True
            box = uicls.Checkbox(align=uiconst.TOPLEFT, text=text, top=top, parent=container, retval=adType.typeMask, checked=checked, callback=callback, groupname=radioGroupName, wrapLabel=False, hint=adType.description)
            top += box.height
            box.name = self.advertGroups[groupID].groupName
            if checked:
                callback(box)
                selected = box
            if not firstEntry:
                firstEntry = box

        if radioGroupName and not selected:
            firstEntry.SetChecked(True)
        container.AutoFitToContent()
        return container



    def CreateGroupCombo(self, parent, groupID, typeData = None, top = 0, ignoreReplace = None):
        options = []
        selected = None
        for adType in self.advertTypesByGroupID[groupID]:
            if not ignoreReplace or ignoreReplace and ignoreReplace[0] != adType.typeMask:
                options.append((adType.typeName, adType.typeMask))
                if typeData and typeData & adType.typeMask:
                    selected = adType.typeMask

        if ignoreReplace:
            options.insert(ignoreReplace[2], (ignoreReplace[1], ignoreReplace[0]))
        combo = uicls.Combo(parent=parent, options=options, name='groupCombo_' + self.advertGroups[groupID].groupName, adjustWidth=True, align=uiconst.TOPLEFT, top=top, select=selected)
        return combo



    def UpdateAdvertDetails(self, checkbox):
        if checkbox.name not in self.advertDetails:
            self.advertDetails[checkbox.name] = 0
        checkboxVal = checkbox.data['value']
        if checkbox.GetValue():
            if checkbox.GetGroup():
                self.advertDetails[checkbox.name] = checkboxVal
            else:
                self.advertDetails[checkbox.name] += checkboxVal
        else:
            self.advertDetails[checkbox.name] -= checkboxVal



    def UpdateSearchDetails(self, checkbox):
        if checkbox.name not in self.searchDetails:
            self.searchDetails[checkbox.name] = 0
        checkboxVal = checkbox.data['value']
        if checkbox.GetValue():
            if checkbox.GetGroup():
                self.searchDetails[checkbox.name] = checkboxVal
            else:
                self.searchDetails[checkbox.name] += checkboxVal
        else:
            self.searchDetails[checkbox.name] -= checkboxVal



    def OnButtonSelected(self, args):
        groupName = self.advertGroups[args[0]].groupName
        typeMask = args[1]
        if self.sr.viewingOwnerID == -1:
            if groupName not in self.searchDetails:
                self.searchDetails[groupName] = 0
            self.searchDetails[groupName] += typeMask
        elif groupName not in self.advertDetails:
            self.advertDetails[groupName] = 0
        self.advertDetails[groupName] += typeMask



    def OnButtonDeselected(self, args):
        groupName = self.advertGroups[args[0]].groupName
        typeMask = args[1]
        if self.sr.viewingOwnerID == -1:
            if groupName in self.searchDetails:
                self.searchDetails[groupName] -= typeMask
        elif groupName in self.advertDetails:
            self.advertDetails[groupName] -= typeMask



    def UpdateAdvert(self, advertID = None):
        title = self.corpTitleEdit.GetValue()
        description = self.corpMessageEdit.GetValue()
        channel = self.advertChannelCombo.GetValue()
        recruiters = self.contactsList
        days = self.advertDetails.get('Duration', 0)
        typeMask = 0
        for (groupID, group,) in self.advertGroups.iteritems():
            typeMask += self.advertDetails.get(group.groupName, 0)

        typeMask += self.advertAreaCombo.GetValue()
        typeMask += self.advertLanguageCombo.GetValue()
        if advertID:
            self.corpSvc.UpdateRecruitmentAd(advertID, typeMask, description, channel, recruiters, title, days)
            sm.GetService('objectCaching').InvalidateCachedMethodCall(('corpRegistry', (session.corpid, 1)), 'GetRecruiters', session.corpid, advertID)
        else:
            self.corpSvc.CreateRecruitmentAd(days, typeMask, session.allianceid, description, channel, recruiters, title)
        self.ShowCorpAdverts()



    def SearchAdverts(self):
        typeMask = 0
        for (groupID, group,) in self.advertGroups.iteritems():
            typeMask += self.searchDetails.get(group.groupName, 0)

        originalAreaVal = self.searchAreaCombo.GetValue()
        if originalAreaVal & AREA_NO_SPECIFIC_MASK:
            areaVal = 0
            for adType in self.advertTypesByGroupID[AREA_OF_OPERATIONS_GROUPID]:
                areaVal += adType.typeMask

        else:
            areaVal = originalAreaVal
        typeMask += areaVal
        typeMask += self.searchLanguageCombo.GetValue()
        isInAlliance = self.inAllianceCheckbox.GetValue()
        (minMembers, maxMembers,) = self.searchSizeCombo.GetValue()
        settings.char.ui.Set('corporation_recruitment_types', typeMask - areaVal + originalAreaVal)
        settings.char.ui.Set('corporation_recruitment_isinalliance', isInAlliance)
        settings.char.ui.Set('corporation_recruitment_minmembers', minMembers)
        settings.char.ui.Set('corporation_recruitment_maxmembers', maxMembers)
        results = self.GetRecruitmentAds(typeMask=typeMask, minMembers=minMembers, maxMembers=maxMembers, isInAlliance=isInAlliance)
        scrolllist = self.GetAdvertScrollEntries(results)
        self.corpSearchResultsScroll.Load(contentList=scrolllist)
        if results:
            self.corpSearchResultsScroll.SetHint(None)
        else:
            self.corpSearchResultsScroll.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/SearchDefaultHint'))



    def GetAdvertScrollEntries(self, adverts, corpView = False, *args):
        scrolllist = []
        if adverts:
            corpIDs = []
            for advert in adverts:
                corpIDs.append(advert.corporationID)

            corpIDs = list(set(corpIDs))
            cfg.eveowners.Prime(corpIDs)
            cfg.corptickernames.Prime(corpIDs)
            for advert in adverts:
                data = util.KeyVal()
                data.id = advert.adID
                data.percentage = self._GetCriteriaMatchPercentage(advert.typeMask)
                data.advert = advert
                data.GetMenu = self.CorpViewRecruitmentMenu
                data.corporationID = advert.corporationID
                data.allianceID = advert.allianceID
                data.channelID = advert.channelID
                data.editFunc = self._CorpEditRecruitment
                data.corpView = corpView
                if corpView:
                    data.memberCount = len(self.corpSvc.GetMemberIDs())
                else:
                    data.memberCount = advert.memberCount
                scrolllist.append(listentry.Get('RecruitmentEntry', data=data))

        return scrolllist



    def CorpViewRecruitmentMenu(self, entry, *args):
        if self.destroyed:
            return 
        m = []
        if entry.sr.node.advert:
            if util.IsCorporation(entry.sr.node.corporationID):
                m += [(localization.GetByLabel('UI/Common/Corporation'), sm.GetService('menu').GetMenuFormItemIDTypeID(entry.sr.node.corporationID, const.typeCorporation))]
            if util.IsAlliance(entry.sr.node.allianceID):
                m += [(localization.GetByLabel('UI/Common/Alliance'), sm.GetService('menu').GetMenuFormItemIDTypeID(entry.sr.node.allianceID, const.typeAlliance))]
            if m:
                m += [None]
            if self.HasAccess(entry.sr.node.corporationID):
                if entry.sr.node.advert.expiryDateTime > blue.os.GetWallclockTime():
                    pass
            return m



    def OnCorporationRecruitmentAdChanged(self, corporationID, adID, change):
        log.LogInfo('OnCorporationRecruitmentAdChanged corporationID', corporationID, 'adID', adID, 'change', change)
        if self is None or self.destroyed:
            log.LogInfo('OnCorporationRecruitmentAdChanged self is None or self.destroyed')
            return 
        if self.corpAdvertContainer.IsHidden():
            self.sr.tabs.BlinkPanelByName(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MyCorporationTab'))
        self.ShowCorpAdverts()



    def HasAccess(self, corporationID):
        if corporationID != session.corpid:
            return False
        if const.corpRolePersonnelManager & session.corprole != const.corpRolePersonnelManager:
            return False
        return True



    def _CorpEditRecruitment(self, advertData, *args):
        self.PopulateCorpAdvertsEdit(advertData)




class RecruitmentEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.RecruitmentEntry'

    def Startup(self, *args):
        self.expanded = False
        self.expandedEntry = None
        self.corpSvc = sm.GetService('corp')
        self.advertTypes = self.corpSvc.GetRecruitmentAdTypes()
        self.advertTypesByGroupID = self.advertTypes.Filter('groupID')
        self.advertGroups = self.corpSvc.GetRecruitmentAdGroups().Index('groupID')
        self.expander = uicls.Sprite(parent=self, state=uiconst.UI_DISABLED, name='expander', align=uiconst.CENTERLEFT, pos=(2, 0, 10, 10), texturePath='res:/UI/Texture/Shared/triangleRight.png')
        self.corpInfoContainer = uicls.Container(parent=self, align=uiconst.TOPLEFT, height=32 + 2 * const.defaultPadding, left=self.expander.width + 2)
        self.percentageContainer = uicls.Container(parent=self, align=uiconst.CENTERRIGHT, padRight=const.defaultPadding * 2, height=32 + 2 * const.defaultPadding)
        self.underline = uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.2))



    def Load(self, node):
        self.sr.node = node
        data = node
        self.corporationID = data.corporationID
        self.corpInfoContainer.Flush()
        self.percentageContainer.Flush()
        corpLogo = uiutil.GetLogoIcon(itemID=self.corporationID, parent=self.corpInfoContainer, align=uiconst.CENTERLEFT, name='corpLogo', state=uiconst.UI_DISABLED, size=32, ignoreSize=True)
        corpNameLabel = uicls.EveLabelMedium(parent=self.corpInfoContainer, name='corpNameLabel', align=uiconst.TOPLEFT, top=const.defaultPadding, left=corpLogo.width + const.defaultPadding, text=cfg.eveowners.Get(self.corporationID).ownerName, bold=True)
        corpAllianceLabel = uicls.EveLabelMedium(parent=self.corpInfoContainer, name='corpAllianceLabel', align=uiconst.TOPLEFT, top=corpNameLabel.top + corpNameLabel.height, left=corpNameLabel.left, text=getattr(cfg.eveowners.GetIfExists(data.allianceID), 'name', ''))
        adTitleLabel = uicls.EveLabelMedium(parent=self.corpInfoContainer, align=uiconst.TOPLEFT, top=const.defaultPadding, state=uiconst.UI_HIDDEN, userEditable=True)
        if data.corpView:
            adTitleLabel.SetText(data.advert.title)
            adTitleLabel.left = corpNameLabel.left
            adTitleLabel.top = corpNameLabel.top + corpNameLabel.height
            adTitleLabel.Show()
            corpAllianceLabel.left = corpNameLabel.left + corpNameLabel.width
            corpAllianceLabel.top = corpNameLabel.top
            expireTime = data.advert.expiryDateTime - blue.os.GetWallclockTime()
            if expireTime > 0:
                expirationString = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdExpiresIn', adDuration=expireTime)
            else:
                expirationString = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdExpired')
            expiryLabel = uicls.EveLabelMedium(parent=self.percentageContainer, align=uiconst.CENTERRIGHT, left=const.defaultPadding * 2, text=expirationString)
            if expireTime < DAY:
                expiryLabel.color = util.Color.RED
            self.percentageContainer.width = expiryLabel.width
        else:
            percentageLabel = uicls.EveLabelMedium(parent=self.percentageContainer, align=uiconst.CENTERLEFT, text='%s%%' % data.percentage)
            percentageBarBack = uicls.Fill(parent=self.percentageContainer, align=uiconst.CENTERRIGHT, color=(0, 0, 0, 1), width=60, height=8)
            if data.percentage >= 75:
                color = util.Color.GREEN
            elif data.percentage >= 50:
                color = util.Color.YELLOW
            elif data.percentage >= 25:
                color = (1, 0.5, 0, 1)
            else:
                color = util.Color.RED
            width = int(data.percentage / 100.0 * percentageBarBack.width) or 1
            percentageBarFront = uicls.Fill(parent=self.percentageContainer, align=uiconst.CENTERRIGHT, left=percentageBarBack.width - width, color=color, width=width, height=percentageBarBack.height - 2, idx=0)
            self.percentageContainer.width = percentageLabel.width + percentageBarBack.width + const.defaultPadding * 4
        self.corpInfoContainer.AutoFitToContent()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32 + 2 * const.defaultPadding
        return node.height



    def GetMenu(self):
        self.OnClick()
        if self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if self.corporationID:
            return sm.GetService('menu').GetMenuFormItemIDTypeID(self.corporationID, const.typeCorporation)
        return []



    def OnClick(self, *args):
        if self.expanded:
            self.expanded = not self.expanded
            self.expander.texturePath = 'res:/UI/Texture/Shared/triangleRight.png'
            if self.expandedEntry:
                self.sr.node.scroll.RemoveNodes([self.expandedEntry])
                self.expandedEntry = None
            self.underline.Show()
        else:
            self.expanded = not self.expanded
            if not self.expandedEntry:
                data = util.KeyVal()
                data.advert = self.sr.node.advert
                data.corporationID = self.sr.node.corporationID
                data.channelID = self.sr.node.channelID
                data.editFunc = self.sr.node.editFunc
                data.corpView = self.sr.node.corpView
                data.text = self.GenerateExpandedText()
                data.showRecruiters = False
                data.recruiters = None
                self.expandedEntry = listentry.Get('RecruitmentEntryExpanded', data=data)
                self.sr.node.scroll.AddNode(self.sr.node.idx + 1, self.expandedEntry)
            self.expander.texturePath = 'res:/UI/Texture/Shared/triangleDown.png'
            self.underline.Hide()
        self.sr.node.scroll.UpdatePosition()



    def GenerateExpandedText(self):
        node = self.sr.node
        text = [node.advert.description]
        if len(text[0]):
            text.append('<br><br>')
        text.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorporationMemberCount', memberCount=node.memberCount))
        text.append('<br><br>')
        for groupID in [LOOKING_FOR_GROUPID, PRIMARY_LANGUAGE_GROUPID]:
            typeList = ''
            for adType in self.advertTypesByGroupID[groupID]:
                if node.advert.typeMask & adType.typeMask:
                    if len(typeList):
                        typeList += ', '
                    typeList += adType.typeName

            if len(typeList):
                text.append('<b>')
                text.append(self.advertGroups[groupID].groupName)
                text.append('</b><br>')
                text.append(typeList)
                text.append('<br><br>')

        if node.channelID and node.corpView:
            channel = sm.GetService('LSC').GetChannelInfo(node.channelID)
            if channel:
                channelName = channel.info.displayName
                text.append('<b>')
                text.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruitmentChannelHeader'))
                text.append('</b><br>')
                text.append(channelName)
                text.append('<br>')
        return text




class RecruitmentEntryExpanded(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.RecruitmentEntryExpanded'
    BUTTONGROUP_HEIGHT = 32

    def Startup(self, *args):
        self.corpSvc = sm.GetService('corp')
        self.lscSvc = sm.GetService('LSC')
        self.expandedTextLabel = uicls.EveLabelMedium(parent=self, name='expandedTextLabel', align=uiconst.TOTOP, width=self.width - const.defaultPadding, padLeft=16)
        self.recruitersContainer = uicls.Container(parent=self, name='recruitersContainer', align=uiconst.TOTOP, width=self.expandedTextLabel.width, padLeft=self.expandedTextLabel.padLeft)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.2))
        self.buttonContainer = uicls.Container(parent=self, name='buttonContainer', align=uiconst.TOBOTTOM)



    def Load(self, node):
        self.expandedTextLabel.SetText(node.text)
        self.recruitersContainer.Flush()
        self.recruitersContainer.height = 0
        recruitersLabel = uicls.EveLabelMedium(parent=self.recruitersContainer, name='recruitersLabel', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRecruiters'), bold=True)
        recruitersLabel.OnClick = self.ToggleRecruiters
        icon = 'res:/UI/Texture/Shared/triangleUp.png' if node.showRecruiters else 'res:/UI/Texture/Shared/triangleDown.png'
        recruitersToggleIcon = uicls.Sprite(parent=self.recruitersContainer, name='recruitersToggleIcon', state=uiconst.UI_NORMAL, texturePath=icon, align=uiconst.TOPLEFT, pos=(recruitersLabel.left + recruitersLabel.width + 1,
         3,
         10,
         10))
        recruitersToggleIcon.OnClick = self.ToggleRecruiters
        self.recruitersContainer.height += 16
        if node.showRecruiters:
            top = 16
            if node.recruiters:
                for recruiter in node.recruiters:
                    container = uicls.Container(parent=self.recruitersContainer, align=uiconst.TOPLEFT, height=40, state=uiconst.UI_NORMAL, top=top)
                    top += container.height
                    online = sm.GetService('onlineStatus').GetOnlineStatus(recruiter)
                    onlineStatus = xtriui.SquareDiode(parent=container, align=uiconst.CENTERLEFT, pos=(0, 0, 12, 12), state=uiconst.UI_NORMAL)
                    onlineStatus.SetRGB(float(not online) * 0.75, float(online) * 0.75, 0.0)
                    if online:
                        hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruiterIsOnline')
                    else:
                        hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/RecruiterIsOffline')
                    onlineStatus.hint = hint
                    logoContainer = uicls.Container(parent=container, name='logoContainer', align=uiconst.CENTERLEFT, pos=(onlineStatus.left + onlineStatus.width + const.defaultPadding,
                     0,
                     32,
                     32), state=uiconst.UI_DISABLED)
                    uiutil.GetOwnerLogo(logoContainer, recruiter, size=32, orderIfMissing=True)
                    charinfo = cfg.eveowners.Get(recruiter)
                    menuList = [(localization.GetByLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (charinfo.typeID, recruiter))]
                    menuList += sm.GetService('menu').GetMenuFormItemIDTypeID(recruiter, cfg.invtypes.Get(charinfo.typeID))
                    container.GetMenu = lambda : menuList
                    nameLabel = uicls.EveLabelMedium(parent=container, name='nameLabel', text=cfg.eveowners.Get(recruiter).name, align=uiconst.CENTERLEFT, left=logoContainer.left + logoContainer.width + const.defaultPadding, state=uiconst.UI_DISABLED)
                    container.width = nameLabel.left + nameLabel.width
                    self.recruitersContainer.height += container.height

            else:
                uicls.EveLabelMedium(parent=self.recruitersContainer, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, top=top, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoRecruiterAssigned'))
        self.buttonContainer.Flush()
        buttons = []
        if node.channelID:
            if not self.lscSvc.IsJoined(node.channelID):
                buttons.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/JoinCorporationRecruitmentChannel'),
                 self.JoinChannel,
                 (None,),
                 None])
        if session.corpid == node.corporationID:
            if node.corpView and const.corpRolePersonnelManager & session.corprole == const.corpRolePersonnelManager:
                buttons.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEdit'),
                 self.EditRecruitmentAd,
                 (None,),
                 None])
                buttons.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRemove'),
                 self.DeleteRecruitmentAd,
                 (None,),
                 None])
        else:
            buttons.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ApplyToJoinCorporation'),
             self.Apply,
             (None,),
             None])
        self.buttonGroup = uicls.ButtonGroup(btns=buttons, parent=self.buttonContainer, name='buttonGroup', line=False, padBottom=const.defaultPadding)
        self.buttonGroup.height = self.BUTTONGROUP_HEIGHT
        self.buttonContainer.height = self.buttonGroup.height



    def ToggleRecruiters(self):
        self.sr.node.showRecruiters = not self.sr.node.showRecruiters
        if self.sr.node.showRecruiters:
            if self.sr.node.recruiters is None:
                self.sr.node.recruiters = self.corpSvc.GetRecruiters(self.sr.node.corporationID, self.sr.node.advert.adID)
        self.sr.node.height = listentry.RecruitmentEntryExpanded.GetDynamicHeight(self.sr.node, self.width)
        self.sr.node.scroll.RefreshNodes()
        self.sr.node.scroll.UpdatePosition()
        self.sr.node.panel.Load(self.sr.node)



    def GetDynamicHeight(node, width):
        height = uicore.font.GetTextHeight(node.text, width=width, fontsize=fontConst.EVE_MEDIUM_FONTSIZE, linespace=fontConst.EVE_MEDIUM_FONTSIZE, letterspace=0)
        height += 16
        if node.showRecruiters:
            if node.recruiters:
                for recruiter in node.recruiters:
                    height += 40

            else:
                height += 16
            height += 10
        height += listentry.RecruitmentEntryExpanded.BUTTONGROUP_HEIGHT
        return height



    def Apply(self, *args):
        self.corpSvc.ApplyForMembership(self.sr.node.corporationID)



    def DeleteRecruitmentAd(self, *args):
        if eve.Message('CorpAdsAreYouSureYouWantToDelete', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.corpSvc.DeleteRecruitmentAd(self.sr.node.advert.adID)



    def EditRecruitmentAd(self, *args):
        self.sr.node.editFunc(self.sr.node.advert)



    def JoinChannel(self, *args):
        self.lscSvc.JoinOrLeaveChannel(self.sr.node.channelID)
        self.Load(self.sr.node)




class ContactContainer(uicls.Container):
    __guid__ = 'uicls.ContactContainer'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.charID = None
        self.removeFunc = attributes.Get('removeFunc', None)
        self.addCallback = attributes.Get('addCallback', None)
        self.corpMembers = attributes.Get('corpMembers', [])
        self.iconContainer = uicls.Container(parent=self, align=uiconst.CENTERLEFT, pos=(const.defaultPadding,
         0,
         40,
         40))
        self.iconContainer.Hide()
        self.contactNameLabel = uicls.EveLabelMedium(parent=self, align=uiconst.CENTERLEFT)
        self.removeContactButton = uicls.Button(parent=self, align=uiconst.CENTERRIGHT, left=const.defaultPadding, hint=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRemove'), func=self.RemoveClick, color=util.Color.RED, iconSize=16, icon='ui_73_16_45')
        uicls.Fill(parent=self, color=(0, 0, 0, 0.5))
        uicls.Frame(parent=self, color=(1, 1, 1, 0.15), idx=0)
        self.Clear()



    def Clear(self):
        self.iconContainer.Flush()
        self.charID = None
        self.contactNameLabel.left = const.defaultPadding
        self.contactNameLabel.SetText(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/NoRecruiterAssigned'))
        self.removeContactButton.Hide()
        self.iconContainer.Hide()



    def Set(self, charID = None):
        self.iconContainer.Flush()
        if charID:
            self.charID = charID
            uiutil.GetOwnerLogo(self.iconContainer, charID, size=self.iconContainer.width, orderIfMissing=True)
            self.iconContainer.Show()
            self.contactNameLabel.left += self.iconContainer.width + const.defaultPadding
            self.contactNameLabel.SetText(cfg.eveowners.Get(charID).name)
            self.removeContactButton.Show()
            self.addCallback(self, charID)



    def IsSet(self):
        return self.charID



    def RemoveClick(self, *args):
        if self.removeFunc and self.charID:
            self.removeFunc(self.charID)



    def OnDropData(self, dragObj, *args):
        if not self.IsSet() and dragObj.__class__ == listentry.User:
            if dragObj.sr.node.itemID in self.corpMembers:
                self.Set(dragObj.sr.node.itemID)




class TimezonePicker(uicls.FlatButtonGroup):
    __guid__ = 'uicls.TimezonePicker'
    default_unisize = True

    def ApplyAttributes(self, attributes):
        uicls.FlatButtonGroup.ApplyAttributes(self, attributes)
        self.dividerColor = (1.0, 1.0, 1.0, 0.5)
        self.selectedRGBA = (1, 1, 1, 0.7)
        self.hiliteRGBA = (1, 1, 1, 0.25)



    def Prepare_Appearance_(self, *args):
        self.dividerColor = (1.0, 1.0, 1.0, 0.5)
        uicls.Line(parent=self.sr.buttonParent, color=self.dividerColor, align=uiconst.TOTOP)
        uicls.Line(parent=self.sr.buttonParent, color=self.dividerColor, align=uiconst.TOBOTTOM)



    def Startup(self, data, selectedArgs = None):
        uicls.FlatButtonGroup.Startup(self, data, selectedArgs)
        self.sr.buttonParent.SetAlign(uiconst.CENTERTOP)
        self.sr.buttonParent.height = self.height - 4
        self.sr.buttonParent.width = self.width
        self.height += 20
        self.width = 0
        for button in self.buttons:
            button.width -= 8
            self.sr.buttonParent.width -= 8
            self.width += button.width
            button.sr.label.Hide()

        self.width += self.buttons[0].width
        for button in self.buttons:
            offset = button.GetAbsolutePosition()[0] - self.GetAbsolutePosition()[0] - 1
            line = uicls.Line(parent=self, color=self.dividerColor, align=uiconst.TOPLEFT, pos=(offset,
             self.sr.buttonParent.top + self.sr.buttonParent.height,
             1,
             5))
            label = uicls.EveLabelMedium(parent=self, text=button.localizedLabel, align=uiconst.TOPLEFT, left=line.left, top=line.top + line.height)
            label.left -= label.textwidth / 2

        baseOffset = self.sr.buttonParent.GetAbsolutePosition()[0] - self.GetAbsolutePosition()[0]
        offset = baseOffset + self.sr.buttonParent.width - 1
        line = uicls.Line(parent=self, color=self.dividerColor, align=uiconst.TOPLEFT, pos=(offset,
         self.sr.buttonParent.top + self.sr.buttonParent.height,
         1,
         5))
        label = uicls.EveLabelMedium(parent=self, text=self.buttons[0].localizedLabel, align=uiconst.TOPLEFT, left=line.left, top=line.top + line.height)
        label.left -= label.textwidth / 2




